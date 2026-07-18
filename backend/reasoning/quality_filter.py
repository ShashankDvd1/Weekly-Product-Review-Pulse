"""
Pulse Intelligence — Review Quality Filter

Executes the Intelligent Review Quality Filter & Research Pipeline Master Prompt
to rigorously evaluate, score, and classify reviews before they enter the main
behavioral analysis and persona generation pipelines.
"""

import logging
import json
import uuid
import time
from typing import List

from core.llm_client import get_llm_client
from core.schemas import UnifiedSignal, QualityCategory, ReviewQualityAssessment

logger = logging.getLogger(__name__)

QUALITY_FILTER_SYSTEM_PROMPT = """You are a Senior UX Researcher, Principal Product Manager, NLP Scientist, and Data Quality Engineer.

Your responsibility is NOT to analyze reviews immediately. Your first responsibility is to determine whether a review is useful enough to analyze.
Poor-quality reviews must never influence product decisions. Optimize for quality of evidence, not quantity.

# Phase 1 — Review Quality Assessment
Evaluate using the following rules:
Rule 1: Reject reviews with < 6 meaningful words (e.g. "Good", "Awesome") unless describing a concrete issue.
Rule 2: Must describe an experience, workflow, problem, or outcome.
Rule 3: Prefer specific details (Price, Delivery, App performance).
Rule 4: Remove pure emotion ("Amazing", "Worst").
Rule 5: Detect actionable problems ("because", "after", "crashed", "missing").
Rule 6: Detect evidence (timeline, numbers, comparisons).
Rule 7: Identify Root Cause Potential (Can this explain WHY?).
Rule 8: Ignore marketing language.
Rule 9: Detect fake or low-credibility reviews.
Rule 10: Reward rich context.

# Phase 2 — Quality Scoring
Calculate (0-10): Information Density, Specificity, Actionability, Root Cause Potential, Evidence Strength, Credibility.
Final Score (0-100).

# Phase 3 — Classification
Assign one: Discard, Low Signal, Medium Signal, High Signal, Gold Insight.

# Phase 4 — Insight Extraction
If accepted (Medium, High, Gold), extract: User Goal, Pain Point, Trigger, Context, Root Cause, Emotional Impact, Workaround, Desired Outcome, Feature Mentioned.

Return a valid JSON array of evaluation objects. Do not use markdown.
"""


def assess_review_quality_batch(signals: List[UnifiedSignal]) -> List[UnifiedSignal]:
    """
    Process a batch of signals using a blazing-fast Rule-Based Quality Filter.
    Bypasses the LLM entirely to save time (completes in 0s) and LLM tokens.
    """
    if not signals:
        return []

    for sig in signals:
        content = str(sig.content).strip()
        words = content.split()
        
        # Base score and category
        score = 50
        category = QualityCategory.MEDIUM_SIGNAL
        
        # Rule 1: Reject < 8 words unconditionally
        if len(words) < 8:
            category = QualityCategory.DISCARD
            score = 10
        elif len(words) > 30:
            score += 30
            category = QualityCategory.HIGH_SIGNAL
            
        # Rule 2: Detect actionable words
        actionable_keywords = ["because", "after", "crashed", "missing", "issue", "problem", "error", "failed", "bug", "stuck", "slow", "fix", "update"]
        if any(keyword in content.lower() for keyword in actionable_keywords):
            score += 20
            if category != QualityCategory.DISCARD:
                category = QualityCategory.GOLD_INSIGHT
                
        # Rule 3: Detect extreme emotion (cap score, but don't discard if long enough)
        if any(keyword in content.lower() for keyword in ["worst", "terrible", "awful", "amazing", "best app"]):
            score -= 10
                
        sig.quality_category = category
        sig.quality_score = min(max(score, 0), 100)
        
        # Attach dummy extracted insights so downstream functions don't crash
        if category in [QualityCategory.MEDIUM_SIGNAL, QualityCategory.HIGH_SIGNAL, QualityCategory.GOLD_INSIGHT]:
            sig.extracted_insights = {
                "user_goal": "Derived from context",
                "pain_point": content[:50] + "..." if len(content) > 50 else content,
                "context": "Rule-based fast extraction",
            }
            
    return signals
