"""
Pulse Intelligence — Data Normalizer

Normalizes data from all sources (Play Store, App Store, Reddit) into
a unified schema for cross-source analysis.
"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional

import pandas as pd

from core.schemas import DataSource, UnifiedSignal

logger = logging.getLogger(__name__)


def _generate_unified_id(source: str, source_id: str, content: str) -> str:
    """Generate a deterministic unique ID from source + content."""
    raw = f"{source}:{source_id}:{content[:100]}"
    return hashlib.md5(raw.encode()).hexdigest()


def _detect_app_from_content(content: str) -> str:
    """Detect which app is mentioned in text content."""
    text_lower = content.lower()

    app_keywords = {
        "zepto": ["zepto"],
        "blinkit": ["blinkit", "grofers"],
        "swiggy_instamart": ["swiggy instamart", "instamart", "swiggy"],
    }

    for app_key, keywords in app_keywords.items():
        for kw in keywords:
            if kw in text_lower:
                return app_key

    return "unknown"


def _detect_categories_mentioned(content: str) -> list[str]:
    """Detect quick commerce product categories mentioned in text."""
    text_lower = content.lower()

    category_keywords = {
        "grocery": ["grocery", "groceries", "atta", "dal", "rice", "sugar", "oil", "flour"],
        "fruits_vegetables": ["fruits", "vegetables", "veggies", "fresh produce", "sabzi", "fruit"],
        "dairy_bread": ["dairy", "milk", "bread", "curd", "paneer", "butter", "cheese", "eggs"],
        "snacks": ["snacks", "chips", "biscuits", "namkeen", "munchies", "cookies", "chocolate"],
        "beauty": ["beauty", "cosmetics", "skincare", "makeup", "shampoo", "face wash", "moisturizer", "personal care"],
        "home_kitchen": ["home", "kitchen", "utensils", "containers", "home decor", "appliances"],
        "electronics": ["electronics", "charger", "cable", "headphone", "earbuds", "power bank", "accessories"],
        "baby_care": ["baby", "diapers", "baby food", "baby care", "infant"],
        "pet_care": ["pet", "dog food", "cat food", "pet care", "pet supplies"],
        "cleaning": ["cleaning", "detergent", "floor cleaner", "dish wash", "toilet cleaner", "mop"],
        "health": ["health", "wellness", "medicine", "vitamins", "supplements", "first aid", "sanitizer"],
        "stationery": ["stationery", "pen", "notebook", "pencil", "school supplies"],
    }

    found = []
    for category, keywords in category_keywords.items():
        for kw in keywords:
            if kw in text_lower:
                found.append(category)
                break

    return found


def _detect_behavioral_signals(content: str) -> list[str]:
    """Detect behavioral patterns and signals in text."""
    text_lower = content.lower()
    signals = []

    # Habit signals
    habit_phrases = [
        "always order", "every week", "every day", "daily", "routine",
        "regularly", "habitual", "my go-to", "usual order", "same thing",
        "always buy", "keep ordering", "repeat order", "reorder",
    ]
    if any(p in text_lower for p in habit_phrases):
        signals.append("habit_loop")

    # Trust signals
    trust_phrases = [
        "don't trust", "can't trust", "not reliable", "risky", "scared",
        "worried about quality", "fake", "expired", "not genuine",
        "poor quality", "bad quality",
    ]
    if any(p in text_lower for p in trust_phrases):
        signals.append("trust_issue")

    # Discovery/awareness gaps
    discovery_phrases = [
        "didn't know", "don't know", "never knew", "just discovered",
        "found out", "surprised", "didn't realize", "hidden",
        "hard to find", "can't find", "where is", "not visible",
    ]
    if any(p in text_lower for p in discovery_phrases):
        signals.append("discovery_gap")

    # Price sensitivity
    price_phrases = [
        "expensive", "overpriced", "too costly", "not worth",
        "cheaper on", "better price", "discount", "offer", "deal",
        "price", "costly", "affordable",
    ]
    if any(p in text_lower for p in price_phrases):
        signals.append("price_sensitivity")

    # Convenience signals
    convenience_phrases = [
        "convenient", "easy", "quick", "fast delivery", "10 minutes",
        "instant", "saves time", "hassle free", "doorstep",
    ]
    if any(p in text_lower for p in convenience_phrases):
        signals.append("convenience_driver")

    # Comparison behavior
    comparison_phrases = [
        "better than", "worse than", "compared to", "switched from",
        "moved to", "prefer", "vs", "versus", "alternative",
    ]
    if any(p in text_lower for p in comparison_phrases):
        signals.append("comparison_behavior")

    # Emergency/urgency signals
    emergency_phrases = [
        "urgent", "emergency", "ran out", "running out",
        "last minute", "needed immediately", "suddenly needed",
    ]
    if any(p in text_lower for p in emergency_phrases):
        signals.append("emergency_trigger")

    return signals


def normalize_play_store_reviews(
    df: pd.DataFrame,
    app_name: str,
    package_name: str,
) -> list[UnifiedSignal]:
    """
    Normalize Play Store reviews into UnifiedSignal format.
    """
    if df.empty:
        return []

    signals = []
    for _, row in df.iterrows():
        content = str(row.get("content", ""))
        if not content.strip():
            continue

        source_id = str(row.get("reviewId", hashlib.md5(content.encode()).hexdigest()[:12]))
        date_val = pd.to_datetime(row.get("at", datetime.now(timezone.utc)))

        signal = UnifiedSignal(
            unified_id=_generate_unified_id("play_store", source_id, content),
            source=DataSource.PLAY_STORE,
            source_id=source_id,
            app_name=app_name,
            content=content,
            rating=int(row.get("score", 0)) if pd.notna(row.get("score")) else None,
            date=date_val,
            author_anon=str(row.get("userName", "Anonymous"))[:3] + "***",
            categories_mentioned=_detect_categories_mentioned(content),
            behavioral_signals=_detect_behavioral_signals(content),
            word_count=len(content.split()),
            metadata={"package_name": package_name},
        )
        signals.append(signal)

    logger.info(f"Normalized {len(signals)} Play Store reviews for {app_name}")
    return signals


def normalize_app_store_reviews(
    df: pd.DataFrame,
    app_name: str,
    app_store_id: str,
) -> list[UnifiedSignal]:
    """
    Normalize App Store reviews into UnifiedSignal format.
    """
    if df.empty:
        return []

    signals = []
    for _, row in df.iterrows():
        content = str(row.get("content", ""))
        if not content.strip():
            continue

        source_id = hashlib.md5(content.encode()).hexdigest()[:12]
        date_val = pd.to_datetime(row.get("at", datetime.now(timezone.utc)))

        signal = UnifiedSignal(
            unified_id=_generate_unified_id("app_store", source_id, content),
            source=DataSource.APP_STORE,
            source_id=source_id,
            app_name=app_name,
            content=content,
            rating=int(row.get("score", 0)) if pd.notna(row.get("score")) else None,
            date=date_val,
            author_anon=str(row.get("userName", "Anonymous"))[:3] + "***",
            categories_mentioned=_detect_categories_mentioned(content),
            behavioral_signals=_detect_behavioral_signals(content),
            word_count=len(content.split()),
            metadata={"app_store_id": app_store_id},
        )
        signals.append(signal)

    logger.info(f"Normalized {len(signals)} App Store reviews for {app_name}")
    return signals


def normalize_reddit_data(
    reddit_signals: list[dict],
) -> list[UnifiedSignal]:
    """
    Normalize Reddit posts/comments into UnifiedSignal format.
    """
    if not reddit_signals:
        return []

    signals = []
    for item in reddit_signals:
        content = str(item.get("content", ""))
        if not content.strip():
            continue

        source_id = item.get("post_id", "")
        date_val = item.get("date", datetime.now(timezone.utc))
        app_name = _detect_app_from_content(content)

        signal = UnifiedSignal(
            unified_id=_generate_unified_id("reddit", source_id, content),
            source=DataSource.REDDIT,
            source_id=source_id,
            app_name=app_name,
            content=content,
            title=item.get("title"),
            date=date_val,
            author_anon=str(item.get("author", "Anonymous"))[:3] + "***",
            categories_mentioned=_detect_categories_mentioned(content),
            behavioral_signals=_detect_behavioral_signals(content),
            word_count=len(content.split()),
            url=item.get("url"),
            metadata={
                "subreddit": item.get("subreddit", ""),
                "post_type": item.get("post_type", ""),
                "score": item.get("score", 0),
            },
        )
        signals.append(signal)

    logger.info(f"Normalized {len(signals)} Reddit signals")
    return signals


def merge_and_deduplicate(
    signals: list[UnifiedSignal],
    similarity_threshold: float = 0.95,
) -> list[UnifiedSignal]:
    """
    Merge signals from all sources and remove near-duplicates.

    Uses unified_id for exact dedup. Semantic dedup (via embeddings)
    is handled separately in processing/deduplication.py.
    """
    seen_ids = set()
    unique_signals = []

    for signal in signals:
        if signal.unified_id not in seen_ids:
            seen_ids.add(signal.unified_id)
            unique_signals.append(signal)

    deduped_count = len(signals) - len(unique_signals)
    if deduped_count > 0:
        logger.info(f"Removed {deduped_count} exact duplicates")

    return unique_signals
