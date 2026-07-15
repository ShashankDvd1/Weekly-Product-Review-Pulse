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

    # ── internal ────────────────────────────────
    def _enforce_rate_limit(self):
        """Wait if needed to respect Groq's RPM limits."""
        elapsed = time.time() - self._last_call_time
        if elapsed < GROQ_RPM_DELAY:
            sleep_time = GROQ_RPM_DELAY - elapsed
            logger.debug(f"Rate-limit sleep: {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self._last_call_time = time.time()

    def _call(self, messages: list[dict], model: str, temperature: float, retries: int = 5) -> str:
        """Make a single LLM call with retries."""
        for attempt in range(retries):
            self._enforce_rate_limit()
            try:
                response = self._client.chat.completions.create(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    response_format={"type": "json_object"},
                )
                return response.choices[0].message.content
            except Exception as e:
                err_str = str(e)
                if "429" in err_str:
                    if attempt == retries - 1:
                        logger.error(f"Rate limited on final attempt {attempt + 1}: {err_str}")
                        raise
                    wait_time = (attempt + 1) * 15  # 15s, 30s, 45s, 60s
                    logger.warning(f"Rate limited (attempt {attempt + 1}/{retries}), waiting {wait_time}s...")
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

    # ── public API ──────────────────────────────
    def analyze(self, system_prompt: str, user_prompt: str, use_reasoning: bool = False) -> dict:
        """
        Run an analytical LLM call and return parsed JSON.

        Args:
            system_prompt: System context for the LLM
            user_prompt: The actual analysis request
            use_reasoning: If True, uses the 70B model for deeper reasoning

        Returns:
            Parsed JSON dict from the LLM response
        """
        if self._force_fast_model:
            model = LLM_MODEL_FAST
        else:
            model = LLM_MODEL_REASONING if use_reasoning else LLM_MODEL_FAST

        temperature = LLM_TEMPERATURE_ANALYTICAL

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            raw = self._call(messages, model, temperature)
        except Exception as e:
            if model == LLM_MODEL_REASONING:
                logger.warning(f"Reasoning model {LLM_MODEL_REASONING} failed: {e}. Permanently falling back to fast model {LLM_MODEL_FAST}...")
                self._force_fast_model = True
                model = LLM_MODEL_FAST
                raw = self._call(messages, model, temperature)
            else:
                raise

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM JSON output: {raw[:200]}...")
            return {"error": "Failed to parse LLM response", "raw": raw}

    def generate(self, system_prompt: str, user_prompt: str, creative: bool = False) -> dict:
        """
        Run a generative LLM call (personas, JTBD, reports).

        Args:
            system_prompt: System context
            user_prompt: Generation request
            creative: If True, uses higher temperature

        Returns:
            Parsed JSON dict
        """
        if self._force_fast_model:
            model = LLM_MODEL_FAST
        else:
            model = LLM_MODEL_REASONING
            
        temperature = LLM_TEMPERATURE_CREATIVE if creative else LLM_TEMPERATURE_ANALYTICAL

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            raw = self._call(messages, model, temperature)
        except Exception as e:
            if model == LLM_MODEL_REASONING:
                logger.warning(f"Reasoning model {LLM_MODEL_REASONING} failed: {e}. Permanently falling back to fast model {LLM_MODEL_FAST}...")
                self._force_fast_model = True
                model = LLM_MODEL_FAST
                raw = self._call(messages, model, temperature)
            else:
                raise

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM JSON output: {raw[:200]}...")
            return {"error": "Failed to parse LLM response", "raw": raw}

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
