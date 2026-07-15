"""
Pulse Intelligence — Evidence Builder

Constructs evidence chains that link every insight back to its source data.
This is the "trust layer" — it ensures no AI-generated insight is presented
without traceable supporting evidence.
"""

import logging
from typing import Optional

from core.schemas import (
    UnifiedSignal, Theme, CategoryBarrier, Persona, JTBD,
    GrowthOpportunity, Hypothesis, EvidenceItem, DataSource,
    ConfidenceLevel,
)

logger = logging.getLogger(__name__)


def build_evidence_chain(
    insight_text: str,
    signals: list[UnifiedSignal],
    top_k: int = 5,
) -> list[EvidenceItem]:
    """
    Find the signals that best support a given insight.

    Uses simple keyword overlap scoring (fast, no embedding needed).
    For deeper semantic matching, use vector_store.semantic_search().
    """
    if not signals:
        return []

    insight_words = set(insight_text.lower().split())

    scored_signals = []
    for signal in signals:
        content_words = set(signal.content.lower().split())
        overlap = len(insight_words & content_words)
        if overlap > 2:
            scored_signals.append((overlap, signal))

    scored_signals.sort(key=lambda x: x[0], reverse=True)

    evidence = []
    for _, signal in scored_signals[:top_k]:
        evidence.append(EvidenceItem(
            source=signal.source,
            text=signal.content[:300],
            date=signal.date,
            rating=signal.rating,
            url=signal.url,
            app_name=signal.app_name,
        ))

    return evidence


def compute_confidence(
    mention_count: int,
    source_count: int,
    contradicting_count: int = 0,
) -> tuple[float, ConfidenceLevel]:
    """
    Compute a confidence score based on evidence volume and diversity.

    Formula: base_score = min(mentions/50, 1.0) * source_weight - contradiction_penalty
    """
    if mention_count == 0:
        return 0.1, ConfidenceLevel.VERY_LOW

    # Base score from mention count (caps at 50 mentions = 1.0)
    base = min(mention_count / 50.0, 1.0)

    # Source diversity multiplier
    source_weight = {1: 0.7, 2: 0.9, 3: 1.0}.get(min(source_count, 3), 1.0)

    # Contradiction penalty
    contradiction_ratio = contradicting_count / max(mention_count, 1)
    penalty = min(contradiction_ratio * 0.3, 0.3)

    score = max(0.05, min(1.0, base * source_weight - penalty))

    # Map to level
    if score >= 0.9:
        level = ConfidenceLevel.VERY_HIGH
    elif score >= 0.7:
        level = ConfidenceLevel.HIGH
    elif score >= 0.5:
        level = ConfidenceLevel.MEDIUM
    elif score >= 0.3:
        level = ConfidenceLevel.LOW
    else:
        level = ConfidenceLevel.VERY_LOW

    return round(score, 2), level


def compute_source_distribution(signals: list[UnifiedSignal]) -> dict:
    """Count how many signals come from each source."""
    dist = {}
    for s in signals:
        source_name = s.source.value
        dist[source_name] = dist.get(source_name, 0) + 1
    return dist


def compute_app_distribution(signals: list[UnifiedSignal]) -> dict:
    """Count how many signals mention each app."""
    dist = {}
    for s in signals:
        app = s.app_name
        if app and app != "unknown":
            dist[app] = dist.get(app, 0) + 1
    return dist


def compute_sentiment_summary(signals: list[UnifiedSignal]) -> dict:
    """Compute aggregate sentiment statistics."""
    scores = [s.sentiment_score for s in signals if s.sentiment_score is not None]
    if not scores:
        return {"avg": 0.0, "positive_pct": 0, "negative_pct": 0, "neutral_pct": 0, "count": 0}

    avg = sum(scores) / len(scores)
    positive = sum(1 for s in scores if s > 0.3)
    negative = sum(1 for s in scores if s < -0.3)
    neutral = len(scores) - positive - negative

    return {
        "avg": round(avg, 2),
        "positive_pct": round(positive / len(scores) * 100, 1),
        "negative_pct": round(negative / len(scores) * 100, 1),
        "neutral_pct": round(neutral / len(scores) * 100, 1),
        "count": len(scores),
    }


def compute_behavioral_signal_counts(signals: list[UnifiedSignal]) -> dict:
    """Count occurrences of each behavioral signal type."""
    counts = {}
    for s in signals:
        for signal_type in s.behavioral_signals:
            counts[signal_type] = counts.get(signal_type, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def compute_category_mention_counts(signals: list[UnifiedSignal]) -> dict:
    """Count how often each product category is mentioned."""
    counts = {}
    for s in signals:
        for cat in s.categories_mentioned:
            counts[cat] = counts.get(cat, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))
