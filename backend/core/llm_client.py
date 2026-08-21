"""
Pulse Intelligence — LLM Client

Unified Groq client with rate limiting, model selection, retry logic,
and structured JSON output enforcement.
"""

import os
import time
import json
import logging
from groq import Groq
import tiktoken

from core.config import (
    GROQ_API_KEY,
    LLM_MODEL_FAST,
    LLM_MODEL_REASONING,
    LLM_TEMPERATURE_ANALYTICAL,
    LLM_TEMPERATURE_CREATIVE,
    GROQ_MAX_TPM,
    GROQ_MAX_RPM,
    GROQ_RPM_DELAY,
)

logger = logging.getLogger(__name__)

# Tokenizer for rough token counting
_encoding = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Count approximate tokens in a text string."""
    return len(_encoding.encode(text))


class LLMClient:
    """
    Wrapper around the Groq API that handles:
    - Model selection (fast 8B vs reasoning 70B)
    - Rate limit compliance (RPM delay)
    - JSON-mode responses
    - Retry with exponential backoff
    """

    def __init__(self):
        api_key = GROQ_API_KEY
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in environment variables")
        self._client = Groq(api_key=api_key)
        self._last_call_time = 0.0
        self._force_fast_model = False
        self._token_window_start = time.time()
        self._tokens_used_in_window = 0

    # ── internal ────────────────────────────────
    def _enforce_token_limit(self, estimated_tokens: int):
        """Wait if needed to respect Groq's TPM limits."""
        now = time.time()
        # Reset window if > 60s has passed
        if now - self._token_window_start > 60:
            self._token_window_start = now
            self._tokens_used_in_window = 0
            
        if self._tokens_used_in_window + estimated_tokens > GROQ_MAX_TPM - 500:
            sleep_time = 60.0 - (now - self._token_window_start)
            if sleep_time > 0:
                logger.warning(f"Token limit approaching ({self._tokens_used_in_window}/{GROQ_MAX_TPM}). Pausing pipeline for {sleep_time:.1f}s...")
                time.sleep(sleep_time)
            
            # Reset window after sleep
            self._token_window_start = time.time()
            self._tokens_used_in_window = 0

    def _enforce_rate_limit(self):
        """Wait if needed to respect Groq's RPM limits."""
        elapsed = time.time() - self._last_call_time
        if elapsed < GROQ_RPM_DELAY:
            sleep_time = GROQ_RPM_DELAY - elapsed
            logger.debug(f"Rate-limit sleep: {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self._last_call_time = time.time()

    def _call(self, messages: list[dict], model: str, temperature: float, retries: int = 5, max_tokens: int = None, is_json: bool = False) -> str:
        """Make a single LLM call with retries."""
        # Estimate input tokens + expected output
        estimated_input = sum(count_tokens(m.get("content", "")) for m in messages)
        estimated_total = estimated_input + (max_tokens or 2000)

        for attempt in range(retries):
            self._enforce_rate_limit()
            self._enforce_token_limit(estimated_tokens=estimated_total)
            try:
                call_kwargs = dict(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                )
                if is_json:
                    call_kwargs["response_format"] = {"type": "json_object"}
                if max_tokens:
                    call_kwargs["max_tokens"] = max_tokens
                response = self._client.chat.completions.create(**call_kwargs)
                
                # Accurately track tokens used
                if hasattr(response, 'usage') and response.usage:
                    self._tokens_used_in_window += response.usage.total_tokens
                else:
                    self._tokens_used_in_window += estimated_total

                return response.choices[0].message.content
            except Exception as e:
                err_str = str(e)
                if "429" in err_str:
                    # Check for daily limits immediately to trigger instant fallback
                    err_lower = err_str.lower()
                    if "tokens per day" in err_lower or "requests per day" in err_lower or "tpd" in err_lower or "rpd" in err_lower:
                        logger.error(f"Groq Daily Limit Exceeded (TPD/RPD): {err_str}")
                        if model == LLM_MODEL_REASONING:
                            self._force_fast_model = True
                        raise RuntimeError(f"Groq Daily Limit Exceeded: {err_str}")

                    import re
                    # Parse try again duration from Groq rate limit message
                    match = re.search(r"try again in (?:(\d+)m)?([\d.]+)s", err_lower)
                    wait_time = 0
                    if match:
                        minutes = int(match.group(1)) if match.group(1) else 0
                        seconds = float(match.group(2))
                        wait_time = int(minutes * 60 + seconds) + 3  # Add 3s buffer
                    else:
                        wait_time = (attempt + 1) * 30  # Default backoff
                        
                    if wait_time > 300:
                        logger.error(f"Groq rate limit wait time too long ({wait_time}s): {err_str}")
                        if model == LLM_MODEL_REASONING:
                            self._force_fast_model = True
                        raise RuntimeError(f"Groq Daily Token Limit Exceeded (Wait time > 5m: {wait_time}s): {err_str}")
                        
                    logger.warning(f"Groq Rate Limit (429) hit. Waiting {wait_time}s before retry (attempt {attempt + 1}/{retries})...")
                    time.sleep(wait_time)
                elif "connection" in err_str.lower() or "getaddrinfo" in err_str.lower() or "connecterror" in err_str.lower():
                    if attempt == retries - 1:
                        logger.error(f"Connection error on final attempt {attempt + 1}: {err_str}")
                        raise
                    wait_time = (attempt + 1) * 5  # 5s, 10s, 15s, 20s
                    logger.warning(f"Connection/DNS error (attempt {attempt + 1}/{retries}), waiting {wait_time}s before retrying...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"LLM call failed: {err_str}")
                    if attempt == retries - 1:
                        raise
        raise RuntimeError("LLM call failed after all retries")

    def _parse_json(self, raw: str) -> dict:
        """Helper to robustly parse JSON from LLM outputs into a dict."""
        if not raw or not isinstance(raw, str):
            return {}
        cleaned = raw.strip()
        
        # Strip thinking blocks from reasoning models (e.g. <think>...</think>)
        import re
        cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL).strip()
        if "<think>" in cleaned:
            cleaned = cleaned.split("<think>")[0].strip()
        
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, str):
                try:
                    parsed = json.loads(parsed)
                except Exception:
                    pass
            if isinstance(parsed, dict):
                return parsed
            elif isinstance(parsed, list):
                return {"items": parsed}
            else:
                return {"text": str(parsed)}
        except Exception as e:
            logger.error(f"Failed to parse LLM JSON output: {cleaned[:200]}... Error: {e}")
            return {"error": "Failed to parse LLM response", "raw": raw}

    # ── public API ──────────────────────────────
    def analyze(self, system_prompt: str, user_prompt: str, use_reasoning: bool = False, max_tokens: int = None) -> dict:
        """
        Run an analytical LLM call and return parsed JSON.

        Args:
            system_prompt: System context for the LLM
            user_prompt: The actual analysis request
            use_reasoning: If True, uses the 70B model for deeper reasoning

        Returns:
            Parsed JSON dict from the LLM response
        """
        if self._force_fast_model or os.getenv("FORCE_FAST_MODEL") == "true":
            model = LLM_MODEL_FAST
        else:
            model = LLM_MODEL_REASONING if use_reasoning else LLM_MODEL_FAST
            
        temperature = LLM_TEMPERATURE_ANALYTICAL

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            raw = self._call(messages, model, temperature, max_tokens=max_tokens)
        except Exception as e:
            if model == LLM_MODEL_REASONING:
                print(f"REASONING MODEL FAILURE DETECTED: {e}")
                logger.warning(f"Reasoning model {LLM_MODEL_REASONING} failed: {e}. Falling back to fast model {LLM_MODEL_FAST}...")
                model = LLM_MODEL_FAST
                raw = self._call(messages, model, temperature, max_tokens=max_tokens)
            else:
                raise

        return self._parse_json(raw)

    def generate(self, system_prompt: str, user_prompt: str, creative: bool = False, max_tokens: int = None) -> dict:
        """
        Run a generative LLM call (personas, JTBD, reports).

        Args:
            system_prompt: System context
            user_prompt: Generation request
            creative: If True, uses higher temperature

        Returns:
            Parsed JSON dict
        """
        if self._force_fast_model or os.getenv("FORCE_FAST_MODEL") == "true":
            model = LLM_MODEL_FAST
        else:
            model = LLM_MODEL_REASONING
            
        temperature = LLM_TEMPERATURE_CREATIVE if creative else LLM_TEMPERATURE_ANALYTICAL

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            raw = self._call(messages, model, temperature, max_tokens=max_tokens)
        except Exception as e:
            if model == LLM_MODEL_REASONING:
                print(f"REASONING MODEL FAILURE DETECTED IN GENERATE: {e}")
                logger.warning(f"Reasoning model {LLM_MODEL_REASONING} failed: {e}. Falling back to fast model {LLM_MODEL_FAST}...")
                model = LLM_MODEL_FAST
                raw = self._call(messages, model, temperature, max_tokens=max_tokens)
            else:
                raise

        return self._parse_json(raw)

    def batch_analyze(self, system_prompt: str, text_chunks: list[str], use_reasoning: bool = False) -> list[dict]:
        """
        Process multiple text chunks through the LLM, respecting rate limits.

        Returns:
            List of parsed JSON results, one per chunk
        """
        results = []
        for i, chunk in enumerate(text_chunks):
            logger.info(f"Processing chunk {i + 1}/{len(text_chunks)}...")
            result = self.analyze(system_prompt, chunk, use_reasoning=use_reasoning)
            results.append(result)
        return results


# Module-level singleton
_client_instance = None


def get_llm_client() -> LLMClient:
    """Get or create a singleton LLM client."""
    global _client_instance
    if _client_instance is None:
        _client_instance = LLMClient()
    return _client_instance
