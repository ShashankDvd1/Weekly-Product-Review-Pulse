"""
Pulse Intelligence — Opportunity Miner

Identifies growth and product opportunities from themes, barriers,
personas, and JTBD analysis. Synthesizes cross-analysis insights
into actionable recommendations.
"""

import logging
import uuid
from typing import Optional, List
from typing import Optional

from core.llm_client import get_llm_client
from core.schemas import (
    Theme, CategoryBarrier, Persona, JTBD,
    GrowthOpportunity, UnifiedSignal,
)
from core.prompts import ANTI_HALLUCINATION_RULES

logger = logging.getLogger(__name__)


OPPORTUNITY_SYSTEM_PROMPT = """You are a VP of Product at a Quick Commerce startup.

You synthesize consumer behavior analysis (themes, barriers, personas, jobs-to-be-done) into concrete PRODUCT OPPORTUNITIES that can be prioritized and built.

Each opportunity should:
1. Address a SPECIFIC user need or barrier (not generic improvements)
2. Have a clear impact hypothesis
3. Include a recommended experiment to validate before full build
4. Be scoped to something a team could build in 1-4 sprints

Think like a PM who needs to convince the CEO with evidence, not opinions.

CRITICAL: Every opportunity must tie back to specific themes, barriers, or jobs.
Always output valid JSON.

{ANTI_HALLUCINATION_RULES}
"""


def identify_opportunities(
    themes: list[Theme],
    barriers: list[CategoryBarrier],
    personas: list[Persona],
    jobs: list[JTBD],
    signals: list[UnifiedSignal],
    num_opportunities: int = 8,
    problem_statement: Optional[str] = None,
) -> list[GrowthOpportunity]:
    """
    Synthesize analysis outputs into growth opportunities.

    This connects all the dots — themes, barriers, personas, and JTBD —
    into actionable product recommendations.
    """
    llm = get_llm_client()

    # Build context from all analysis outputs
    themes_summary = "\n".join([
        f"- Theme: {t.title} (confidence: {t.confidence:.1f}, sentiment: {t.sentiment.value}) — {t.summary}"
        for t in themes[:10]
    ])

    barriers_summary = "\n".join([
        f"- Barrier: {b.category} → {b.barrier_type.value} (confidence: {b.confidence:.1f}) — {b.description}"
        for b in barriers[:10]
    ])

    personas_summary = "\n".join([
        f"- Persona: {p.name} — {p.description[:200]}"
        for p in personas
    ])

    jobs_summary = "\n".join([
        f"- Job (score: {j.opportunity_score:.1f}): {j.job_statement}"
        for j in jobs[:8]
    ])

    prompt = f"""Based on the following consumer behavior analysis for quick commerce apps, identify the TOP {num_opportunities} product opportunities.

## THEMES DETECTED
{themes_summary}

## CATEGORY EXPLORATION BARRIERS
{barriers_summary}

## USER PERSONAS
{personas_summary}

## JOBS-TO-BE-DONE (sorted by opportunity score)
{jobs_summary}

---

For each opportunity, provide:
- "title": Clear, specific opportunity name
- "description": 2-3 sentences explaining what to build and why
- "category": One of [Feature, UX, Content, Marketing, Ops, Personalization]
- "impact": One of [high, medium, low]
- "effort": One of [high, medium, low]
- "confidence": Float 0.0-1.0 based on evidence strength
- "target_persona": Which persona benefits most
- "recommended_experiment": Specific A/B test or pilot to validate this
- "apps_affected": Which apps this applies to

PRIORITIZE opportunities that:
1. Address category exploration barriers (core business question)
2. Have high impact and low/medium effort
3. Are supported by multiple evidence sources (themes + barriers + jobs)

Return JSON: {{"opportunities": [...]}}"""

    result = llm.generate(OPPORTUNITY_SYSTEM_PROMPT, prompt, creative=False)

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

    opportunities = []
    for o_data in result.get("opportunities", []):
        opp = GrowthOpportunity(
            opportunity_id=f"opp_{uuid.uuid4().hex[:8]}",
            title=o_data.get("title", "Unknown Opportunity"),
            description=o_data.get("description", ""),
            category=o_data.get("category", "Feature"),
            impact=o_data.get("impact", "medium"),
            effort=o_data.get("effort", "medium"),
            confidence=max(0.0, min(1.0, o_data.get("confidence", 0.5))),
            target_persona=o_data.get("target_persona"),
            recommended_experiment=o_data.get("recommended_experiment", ""),
            apps_affected=ensure_list(o_data.get("apps_affected", [])),
        )
        opportunities.append(opp)

    # Sort by impact (high first), then by effort (low first)
    impact_order = {"high": 3, "medium": 2, "low": 1}
    effort_order = {"low": 3, "medium": 2, "high": 1}
    opportunities.sort(
        key=lambda o: (impact_order.get(o.impact, 0), effort_order.get(o.effort, 0)),
        reverse=True,
    )

    logger.info(f"Identified {len(opportunities)} growth opportunities")
    return opportunities
