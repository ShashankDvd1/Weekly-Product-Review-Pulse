"""
Pulse Intelligence — JTBD Analyzer

Extracts Jobs-To-Be-Done from consumer signals.
Maps user needs into the JTBD framework:
"When [situation], I want to [motivation], so I can [outcome]"
"""

import logging
import uuid

from core.llm_client import get_llm_client
from core.schemas import UnifiedSignal, JTBD, JTBDCategory

from reasoning.behavior_analyzer import validate_quotes
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


JTBD_SYSTEM_PROMPT = """You are an expert in the Jobs-To-Be-Done (JTBD) framework, specifically applied to Quick Commerce (10-minute delivery apps like Zepto, Blinkit, Swiggy Instamart).

You analyze consumer signals to extract the real JOBS users are trying to get done — not features they want, but outcomes they desire.

JTBD Framework:
- Functional Jobs: Practical tasks (e.g., "stock up on essentials without leaving home")
- Emotional Jobs: Feelings desired (e.g., "feel like a responsible parent who always has supplies")
- Social Jobs: Social outcomes (e.g., "impress guests with snacks without advance planning")

Each job should follow the format:
"When [SITUATION/TRIGGER], I want to [MOTIVATION/ACTION], so I can [DESIRED OUTCOME]"

Also identify:
- Current solutions users employ (including workarounds)
- Gaps in how current products address the job
- Opportunity score = Importance × (1 - Satisfaction) on a 0-10 scale

CRITICAL: Ground every job in real user evidence. No hypothetical jobs.
Always output valid JSON.
"""


def analyze_jtbd(
    signals: list[UnifiedSignal],
    num_jobs: int = 8,
) -> list[JTBD]:
    """
    Extract Jobs-To-Be-Done from consumer signals.

    Returns JTBD objects with opportunity scoring.
    """
    if not signals:
        return []

    llm = get_llm_client()

    # Sample and prepare signals
    sample_size = min(len(signals), 80)
    sample = signals[:sample_size]

    signal_texts = []
    for s in sample:
        prefix = f"[{s.source.value}|{s.app_name}]"
        if s.behavioral_signals:
            prefix += f" [behavioral: {', '.join(s.behavioral_signals)}]"
        signal_texts.append(f"{prefix} {s.content[:300]}")

    chunk = "\n\n".join(signal_texts)

    prompt = f"""Analyze these consumer signals from quick commerce users and extract {num_jobs} Jobs-To-Be-Done.

For each job, provide:
- "job_statement": In the format "When [situation], I want to [motivation], so I can [outcome]"
- "category": One of ["functional", "emotional", "social"]
- "current_solution": How users currently get this job done
- "gaps": List of 2-3 ways current solutions fail to fully satisfy this job
- "opportunity_score": Float 0.0-10.0 (Importance × (1 - Satisfaction))
- "signal_count": Number of signals that relate to this job
- "supporting_quotes": 2 exact verbatim quotes from the signals

IMPORTANT:
- Include at least 2 jobs related to CATEGORY EXPLORATION (why users don't explore new categories)
- Include a mix of functional, emotional, and social jobs
- Higher opportunity_score means bigger product opportunity

Return JSON: {{"jobs": [...]}}

CONSUMER SIGNALS:
{chunk}"""

    result = llm.generate(JTBD_SYSTEM_PROMPT, prompt, creative=False)

    jobs = []
    for j_data in result.get("jobs", []):
        cat_str = j_data.get("category", "functional").lower()
        cat_map = {
            "functional": JTBDCategory.FUNCTIONAL,
            "emotional": JTBDCategory.EMOTIONAL,
            "social": JTBDCategory.SOCIAL,
        }
        category = cat_map.get(cat_str, JTBDCategory.FUNCTIONAL)

        job = JTBD(
            jtbd_id=f"jtbd_{uuid.uuid4().hex[:8]}",
            job_statement=j_data.get("job_statement", ""),
            category=category,
            current_solution=j_data.get("current_solution", ""),
            gaps=ensure_list(j_data.get("gaps", [])),
            opportunity_score=max(0.0, min(10.0, j_data.get("opportunity_score", 0.0))),
            signal_count=j_data.get("signal_count", 0),
            supporting_quotes=validate_quotes(ensure_list(j_data.get("supporting_quotes", [])), signals),
        )
        jobs.append(job)

    # Sort by opportunity score (highest first)
    jobs.sort(key=lambda j: j.opportunity_score, reverse=True)

    logger.info(f"Extracted {len(jobs)} Jobs-To-Be-Done")
    return jobs
