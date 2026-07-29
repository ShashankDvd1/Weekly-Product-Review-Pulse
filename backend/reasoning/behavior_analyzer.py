"""
Pulse Intelligence — Behavioral Pattern Analyzer

The core AI engine that detects behavioral patterns in consumer signals.
This is the primary differentiator — it answers WHY users behave the way they do,
not just WHAT they're saying.

Uses Groq (Llama 3.3 70B) for deep reasoning about:
- Shopping habits & routines
- Purchase motivations
- Category exploration barriers
- Emotional triggers
- Habit loops
"""

import logging
from datetime import datetime
from typing import Optional
import uuid

from core.llm_client import get_llm_client, count_tokens
from core.schemas import UnifiedSignal, Theme, CategoryBarrier, ConfidenceLevel, SentimentLabel, BarrierType, EvidenceItem
from core.config import GROQ_MAX_TPM, CATEGORY_BARRIER_TYPES
from core.prompts import ANTI_HALLUCINATION_RULES

logger = logging.getLogger(__name__)


def ensure_list(val) -> list[str]:
    if not val:
        return []
    if isinstance(val, list):
        return [str(x) for x in val if x]
    if isinstance(val, str):
        stripped = val.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            try:
                import json
                parsed = json.loads(stripped)
                if isinstance(parsed, list):
                    return [str(x) for x in parsed if x]
            except Exception:
                pass
        return [x.strip() for x in val.split(",") if x.strip()]
    return [str(val)]


def validate_quotes(quotes: list[str], signals: list[UnifiedSignal]) -> list[str]:
    """
    Filter the list of quotes to keep only those that exist as a substring
    (case-insensitive, ignoring spacing/punctuation) of at least one scraped signal's content.
    """
    valid_quotes = []

    def normalize(text: str) -> str:
        return "".join(c.lower() for c in text if c.isalnum())

    normalized_signals = [normalize(s.content) for s in signals]

    for quote in quotes:
        norm_quote = normalize(quote)
        if not norm_quote:
            continue

        matched = False
        for norm_signal in normalized_signals:
            if norm_quote in norm_signal:
                matched = True
                break

        if matched:
            valid_quotes.append(quote)
        else:
            logger.warning(f"Hallucinated quote rejected by guardrails: '{quote}'")

    return valid_quotes



BEHAVIOR_SYSTEM_PROMPT = f"""You are a Senior Product Manager at a Quick Commerce company (like Zepto, Blinkit, or Swiggy Instamart).

Your expertise is in understanding consumer behavior — specifically WHY users behave the way they do when using quick commerce apps.

You analyze customer signals (app reviews, Reddit discussions) to detect:
1. Shopping habits and routines (why do users always buy the same things?)
2. Category exploration barriers (why don't users explore new categories?)
3. Purchase motivations (what triggers a purchase?)
4. Emotional patterns (trust, frustration, delight, anxiety)
5. Habit loops (trigger → action → reward patterns)

You think like a behavioral scientist, not a dashboard analyst.

CRITICAL RULES:
- Every insight MUST be grounded in specific evidence from the provided signals
- Assign a confidence score (0.0 to 1.0) based on evidence volume and consistency
- Identify contradicting evidence when it exists
- Be specific, not generic. "Users want better UX" is useless. "Users only open the app when they run out of milk because the homepage doesn't surface new categories" is actionable.
- Always output valid JSON

{ANTI_HALLUCINATION_RULES}
"""


def _prepare_signals_for_llm(signals: list[UnifiedSignal], max_tokens: int = 3000) -> list[str]:
    """
    Chunk signals into batches. If there are too many signals, downsample them 
    using stratified sampling to avoid hitting LLM token rate limits.
    """
    MAX_SIGNALS = 100
    if len(signals) > MAX_SIGNALS:
        logger.info(f"Downsampling signals count from {len(signals)} to {MAX_SIGNALS} for LLM analysis.")
        # Stratified sampling by app and rating
        groups = {}
        for s in signals:
            key = (s.app_name, s.rating or 3)
            groups.setdefault(key, []).append(s)
            
        import random
        sampled_signals = []
        total_groups = len(groups)
        if total_groups > 0:
            per_group_limit = max(1, MAX_SIGNALS // total_groups)
            for key, group_list in groups.items():
                sampled_signals.extend(random.sample(group_list, min(len(group_list), per_group_limit)))
                
        if len(sampled_signals) < MAX_SIGNALS:
            remaining_quota = MAX_SIGNALS - len(sampled_signals)
            all_remaining = [s for s in signals if s not in sampled_signals]
            sampled_signals.extend(random.sample(all_remaining, min(len(all_remaining), remaining_quota)))
            
        signals = sampled_signals

    chunks = []
    current_chunk = []
    current_tokens = 0

    for signal in signals:
        entry = f"[{signal.source.value}|{signal.app_name}|{'★' * (signal.rating or 0)}] {signal.content}"
        tokens = count_tokens(entry)

        if current_tokens + tokens > max_tokens and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [entry]
            current_tokens = tokens
        else:
            current_chunk.append(entry)
            current_tokens += tokens

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def detect_themes(
    signals: list[UnifiedSignal],
    context: str = "quick commerce category exploration behavior",
) -> list[Theme]:
    """
    Detect themes from consumer signals using LLM analysis.

    Returns a list of Theme objects with evidence chains and confidence scores.
    """
    if not signals:
        return []

    llm = get_llm_client()
    chunks = _prepare_signals_for_llm(signals)
    all_themes = []

    from concurrent.futures import ThreadPoolExecutor

    def analyze_chunk(chunk):
        prompt = f"""Analyze these {len(signals)} consumer signals about {context}.

Extract the TOP THEMES — patterns that appear repeatedly across multiple signals.

For each theme, provide:
- "title": Short, specific title (not generic)
- "summary": 2-3 sentence description of the pattern
- "category": One of [Delivery, UX, Pricing, Quality, Selection, Trust, Habit, Discovery, Support, Feature]
- "sentiment": One of [positive, negative, neutral, mixed]
- "mention_count": Estimated number of signals supporting this theme
- "confidence": Float 0.0-1.0 based on evidence strength
- "supporting_quotes": ["quote1", "quote2", "quote3"] (a JSON list of exactly 3 verbatim string quotes from the signals, EXACT substrings)
- "apps_affected": Which apps are affected
- "contradicting_quotes": ["quote1"] (a JSON list of quotes that contradict this theme, or an empty list if none)

Return JSON: {{"themes": [...]}}

SIGNALS:
{chunk}"""
        try:
            return llm.analyze(BEHAVIOR_SYSTEM_PROMPT, prompt, use_reasoning=False)
        except Exception as e:
            logger.error(f"Failed to analyze theme chunk: {e}")
            return {"themes": []}

    with ThreadPoolExecutor(max_workers=3) as executor:
        chunk_results = list(executor.map(analyze_chunk, chunks))

    for result in chunk_results:
        for theme_data in result.get("themes", []):
            # Map confidence to level
            conf = theme_data.get("confidence", 0.5)
            if conf >= 0.9:
                conf_level = ConfidenceLevel.VERY_HIGH
            elif conf >= 0.7:
                conf_level = ConfidenceLevel.HIGH
            elif conf >= 0.5:
                conf_level = ConfidenceLevel.MEDIUM
            elif conf >= 0.3:
                conf_level = ConfidenceLevel.LOW
            else:
                conf_level = ConfidenceLevel.VERY_LOW

            # Map sentiment string
            sentiment_str = theme_data.get("sentiment", "neutral").lower()
            sentiment_map = {
                "positive": SentimentLabel.POSITIVE,
                "negative": SentimentLabel.NEGATIVE,
                "neutral": SentimentLabel.NEUTRAL,
                "mixed": SentimentLabel.MIXED,
            }
            sentiment = sentiment_map.get(sentiment_str, SentimentLabel.NEUTRAL)

            theme = Theme(
                theme_id=f"theme_{uuid.uuid4().hex[:8]}",
                title=theme_data.get("title", "Unknown Theme"),
                summary=theme_data.get("summary", ""),
                category=theme_data.get("category", "General"),
                sentiment=sentiment,
                mention_count=theme_data.get("mention_count", 0),
                confidence=conf,
                confidence_level=conf_level,
                supporting_quotes=validate_quotes(ensure_list(theme_data.get("supporting_quotes", [])), signals),
                apps_affected=ensure_list(theme_data.get("apps_affected", [])),
                first_seen=datetime.utcnow(),
            )
            all_themes.append(theme)

    logger.info(f"Detected {len(all_themes)} themes from {len(signals)} signals")
    return all_themes


def detect_category_barriers(
    signals: list[UnifiedSignal],
    target_categories: Optional[list[str]] = None,
    problem_statement: Optional[str] = None,
) -> list[CategoryBarrier]:
    """
    Detect barriers that prevent users from exploring new product categories.

    This is the CORE ANALYSIS for the graduation assignment.

    Barrier types:
    - awareness: User doesn't know the category exists on the platform
    - trust: User doesn't trust the platform for this category
    - habit: User has a fixed routine / trigger
    - price_perception: User assumes it's overpriced
    - quality_concern: User fears poor quality
    - selection: User thinks selection is limited
    - convenience: Easier to buy elsewhere
    - discovery: Hard to find/browse the category in the app
    """
    if not signals:
        return []

    llm = get_llm_client()
    chunks = _prepare_signals_for_llm(signals)
    all_barriers = []

    categories_str = ", ".join(target_categories) if target_categories else (
        "Beauty, Electronics, Home & Kitchen, Baby Care, Pet Care, Stationery, Toys"
    )

    from concurrent.futures import ThreadPoolExecutor

    def analyze_barrier_chunk(chunk):
        problem_context = f"The specific problem to focus on is: {problem_statement}" if problem_statement else f"The question: Why do users keep buying from familiar categories (Grocery, Snacks, Dairy) but avoid exploring: {categories_str}?"
        
        prompt = f"""Analyze these consumer signals to identify CATEGORY EXPLORATION BARRIERS in quick commerce apps.

{problem_context}

For each barrier you find, provide:
- "category": The product category users avoid (e.g., "Beauty", "Electronics")
- "barrier_type": One of {CATEGORY_BARRIER_TYPES}
- "description": Specific explanation of WHY this barrier exists (2-3 sentences)
- "signal_count": Number of signals supporting this barrier
- "confidence": Float 0.0-1.0
- "supporting_quotes": ["quote1", "quote2"] (a JSON list of 2-3 exact verbatim string quotes from the signals)
- "recommended_intervention": A specific product change to address this barrier
- "apps_affected": Which apps are affected

Return JSON: {{"barriers": [...]}}

CRITICAL STYLE RULES:
- Do NOT reuse the same sentence structures, phrasing, or templates (like "Users are concerned about...") across different barriers.
- Each barrier's description must be completely distinct, context-rich, and directly address the specific characteristics of that category (e.g., fears of counterfeit beauty products, fears of receiving malfunctioning or unboxable electronics, worries of delivery delays for dinner ingredients).
- Provide unique recommended interventions tailored to the specific barrier.

CONSUMER SIGNALS:
{chunk}"""
        try:
            return llm.analyze(BEHAVIOR_SYSTEM_PROMPT, prompt, use_reasoning=False)
        except Exception as e:
            logger.error(f"Failed to analyze barrier chunk: {e}")
            return {"barriers": []}

    with ThreadPoolExecutor(max_workers=3) as executor:
        chunk_results = list(executor.map(analyze_barrier_chunk, chunks))

    for result in chunk_results:
        for barrier_data in result.get("barriers", []):
            conf = barrier_data.get("confidence", 0.5)
            barrier_type_str = barrier_data.get("barrier_type", "awareness")
            try:
                barrier_type = BarrierType(barrier_type_str)
            except ValueError:
                barrier_type = BarrierType.AWARENESS

            # Build evidence items from quotes
            valid_quotes = validate_quotes(ensure_list(barrier_data.get("supporting_quotes", [])), signals)
            evidence = []
            for quote in valid_quotes:
                evidence.append(EvidenceItem(
                    source=DataSource.PLAY_STORE,  # Will be refined with actual source
                    text=quote,
                ))

            barrier = CategoryBarrier(
                barrier_id=f"barrier_{uuid.uuid4().hex[:8]}",
                category=barrier_data.get("category", "Unknown"),
                barrier_type=barrier_type,
                description=barrier_data.get("description", ""),
                signal_count=int(float(barrier_data.get("signal_count", 0))) if barrier_data.get("signal_count") is not None else 0,
                confidence=conf,
                confidence_level=(
                    ConfidenceLevel.HIGH if conf >= 0.7
                    else ConfidenceLevel.MEDIUM if conf >= 0.5
                    else ConfidenceLevel.LOW
                ),
                supporting_evidence=evidence,
                recommended_intervention=barrier_data.get("recommended_intervention", ""),
                apps_affected=ensure_list(barrier_data.get("apps_affected", [])),
            )
            all_barriers.append(barrier)

    logger.info(f"Detected {len(all_barriers)} category barriers")
    return all_barriers


def analyze_sentiment_batch(
    signals: list[UnifiedSignal],
) -> list[UnifiedSignal]:
    """
    Run sentiment analysis on signals.
    To avoid hitting LLM rate limits, we use the rating (1-5 stars) as a direct proxy
    for App Store and Play Store reviews, and only call the LLM for Reddit signals 
    or signals without ratings.
    """
    if not signals:
        return signals

    llm = get_llm_client()
    llm_signals = []
    
    for s in signals:
        if s.rating is not None:
            # Map 1-5 stars to -1.0 to 1.0
            # 1 -> -0.8, 2 -> -0.4, 3 -> 0.0, 4 -> 0.4, 5 -> 0.8
            s.sentiment_score = (s.rating - 3) * 0.4
        else:
            llm_signals.append(s)

    if not llm_signals:
        return signals

    # Process remaining signals (Reddit, etc.) in batches
    batch_size = 40
    for i in range(0, len(llm_signals), batch_size):
        batch = llm_signals[i:i + batch_size]
        texts = [f"{idx}: {s.content[:200]}" for idx, s in enumerate(batch)]

        prompt = f"""Classify the sentiment of each numbered text as a float from -1.0 (very negative) to 1.0 (very positive).

Return JSON: {{"sentiments": [{{"index": 0, "score": 0.5}}, ...]}}

TEXTS:
{chr(10).join(texts)}"""

        try:
            result = llm.analyze(
                "You are a sentiment analysis engine. Output only valid JSON.",
                prompt,
                use_reasoning=False,
            )

            for item in result.get("sentiments", []):
                idx = item.get("index", -1)
                if 0 <= idx < len(batch):
                    batch[idx].sentiment_score = max(-1.0, min(1.0, item.get("score", 0.0)))
        except Exception as e:
            logger.error(f"Sentiment LLM batch failed: {e}")
            for s in batch:
                s.sentiment_score = 0.0

    return signals


# Import DataSource for evidence items
from core.schemas import DataSource
