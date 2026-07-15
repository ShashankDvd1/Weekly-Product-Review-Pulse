"""
Pulse Intelligence — Report Generator

Generates executive summaries, category discovery reports,
and weekly reports from analysis results.
"""

import logging
from datetime import datetime

from core.llm_client import get_llm_client
from core.schemas import (
    Theme, CategoryBarrier, Persona, JTBD, GrowthOpportunity,
    Hypothesis, ExecutiveSummary, UnifiedSignal,
)
from output.evidence_builder import (
    compute_source_distribution,
    compute_sentiment_summary,
    compute_category_mention_counts,
    compute_behavioral_signal_counts,
)

logger = logging.getLogger(__name__)


REPORT_SYSTEM_PROMPT = """You are a Chief Product Officer writing an executive brief for the CEO of a Quick Commerce company.

Your writing is:
- Data-driven (every claim has a number behind it)
- Concise (executives don't read paragraphs)
- Actionable (end with clear next steps)
- Evidence-based (cite specific findings)

You structure reports like McKinsey consultants — pyramid principle, MECE, insight-first.
Always output valid JSON.
"""


def generate_executive_summary(
    signals: list[UnifiedSignal],
    themes: list[Theme],
    barriers: list[CategoryBarrier],
    personas: list[Persona],
    jobs: list[JTBD],
    opportunities: list[GrowthOpportunity],
) -> ExecutiveSummary:
    """
    Generate a comprehensive executive summary from all analysis outputs.
    """
    llm = get_llm_client()

    # Build data context
    source_dist = compute_source_distribution(signals)
    sentiment = compute_sentiment_summary(signals)
    category_counts = compute_category_mention_counts(signals)
    behavioral_counts = compute_behavioral_signal_counts(signals)

    context = f"""## DATA COVERAGE
- Total signals analyzed: {len(signals)}
- Sources: {source_dist}
- Sentiment: {sentiment}

## TOP THEMES ({len(themes)} detected)
{chr(10).join(f'- {t.title} ({t.sentiment.value}, confidence: {t.confidence:.1f}): {t.summary}' for t in themes[:5])}

## CATEGORY BARRIERS ({len(barriers)} detected)
{chr(10).join(f'- {b.category} → {b.barrier_type.value}: {b.description}' for b in barriers[:5])}

## PERSONAS ({len(personas)} generated)
{chr(10).join(f'- {p.name}: {p.description[:150]}' for p in personas)}

## TOP JOBS-TO-BE-DONE
{chr(10).join(f'- (score: {j.opportunity_score:.1f}) {j.job_statement}' for j in jobs[:4])}

## TOP OPPORTUNITIES
{chr(10).join(f'- [{o.impact} impact, {o.effort} effort] {o.title}: {o.description[:100]}' for o in opportunities[:5])}

## BEHAVIORAL SIGNALS
{behavioral_counts}

## CATEGORY MENTIONS
{category_counts}"""

    prompt = f"""Write an executive summary for a Quick Commerce Category Discovery Analysis.

{context}

Provide:
- "summary": 3-4 paragraph executive summary (include specific numbers)
- "key_findings": List of 5 most important findings (1 sentence each)
- "top_opportunities": List of 3 highest-impact opportunities
- "recommended_actions": List of 3 specific next steps for the product team

Return JSON with those 4 keys."""

    result = llm.generate(REPORT_SYSTEM_PROMPT, prompt, creative=False)

    summary_raw = result.get("summary", "Analysis complete. See detailed findings below.")
    if isinstance(summary_raw, list):
        summary_val = "\n\n".join(str(s) for s in summary_raw)
    else:
        summary_val = str(summary_raw)

    def normalize_list(lst):
        if not isinstance(lst, list):
            return [str(lst)] if lst else []
        return [str(x) for x in lst]

    key_findings_val = normalize_list(result.get("key_findings", []))
    top_opportunities_val = normalize_list(result.get("top_opportunities", []))
    recommended_actions_val = normalize_list(result.get("recommended_actions", []))

    return ExecutiveSummary(
        summary=summary_val,
        key_findings=key_findings_val,
        top_opportunities=top_opportunities_val,
        recommended_actions=recommended_actions_val,
        data_coverage={
            "total_signals": len(signals),
            "sources": source_dist,
            "sentiment": sentiment,
            "themes_detected": len(themes),
            "barriers_detected": len(barriers),
            "personas_generated": len(personas),
            "jobs_extracted": len(jobs),
            "opportunities_found": len(opportunities),
        },
        generated_at=datetime.utcnow(),
    )


def generate_category_discovery_report(
    signals: list[UnifiedSignal],
    barriers: list[CategoryBarrier],
    personas: list[Persona],
    opportunities: list[GrowthOpportunity],
    hypotheses: list[Hypothesis],
) -> dict:
    """
    Generate the Category Discovery Report — the primary assignment deliverable.

    This is the comprehensive analysis answering:
    "Why do users repeatedly purchase from the same categories
     instead of exploring new ones?"
    """
    source_dist = compute_source_distribution(signals)
    category_counts = compute_category_mention_counts(signals)
    behavioral_counts = compute_behavioral_signal_counts(signals)

    # Group barriers by type
    barriers_by_type = {}
    for b in barriers:
        bt = b.barrier_type.value
        if bt not in barriers_by_type:
            barriers_by_type[bt] = []
        barriers_by_type[bt].append(b.model_dump())

    # Group barriers by category
    barriers_by_category = {}
    for b in barriers:
        cat = b.category
        if cat not in barriers_by_category:
            barriers_by_category[cat] = []
        barriers_by_category[cat].append(b.model_dump())

    report = {
        "title": "Quick Commerce Category Discovery Analysis",
        "subtitle": "Why Users Don't Explore New Categories — AI-Powered Behavioral Intelligence",
        "generated_at": datetime.utcnow().isoformat(),
        "data_coverage": {
            "total_signals": len(signals),
            "source_distribution": source_dist,
            "apps_analyzed": list(set(s.app_name for s in signals if s.app_name != "unknown")),
        },
        "category_mentions": category_counts,
        "behavioral_signals": behavioral_counts,
        "barriers": {
            "total": len(barriers),
            "by_type": barriers_by_type,
            "by_category": barriers_by_category,
        },
        "personas": [p.model_dump() for p in personas],
        "opportunities": [o.model_dump() for o in opportunities],
        "hypotheses": [h.model_dump() for h in hypotheses],
    }

    return report
