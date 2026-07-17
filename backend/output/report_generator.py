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


def generate_executive_deck(
    signals: list[UnifiedSignal],
    themes: list[Theme],
    barriers: list[CategoryBarrier],
    personas: list[Persona],
    jobs: list[JTBD],
    opportunities: list[GrowthOpportunity],
) -> dict:
    """
    Automatically generate a concise executive presentation (3-4 slides)
    that tells a compelling story and helps stakeholders understand the findings.
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
{chr(10).join(f'- {t.title} ({t.sentiment.value}, confidence: {t.confidence:.2f}): {t.summary}' for t in themes[:5])}

## CATEGORY BARRIERS ({len(barriers)} detected)
{chr(10).join(f'- {b.category} → {b.barrier_type.value}: {b.description}' for b in barriers[:5])}

## PERSONAS ({len(personas)} generated)
{chr(10).join(f'- {p.name}: {p.description[:150]}' for p in personas)}

## TOP JOBS-TO-BE-DONE
{chr(10).join(f'- (score: {j.opportunity_score:.1f}) {j.job_statement}' for j in jobs[:4])}

## TOP OPPORTUNITIES
{chr(10).join(f'- [{o.impact} impact, {o.effort} effort] {o.title}: {o.description[:100]}' for o in opportunities[:5])}
"""

    prompt = f"""You are a McKinsey-style Product Consultant. Generate a concise, consulting-style executive presentation slide deck of exactly 4 slides based on the following consumer behavioral analysis.

{context}

Format your response as a single, valid JSON object with a single root key "slides" containing a list of exactly 4 slide objects matching the following slide structure:

### Slide 1: Executive Summary & Problem Discovery
- `slide_number`: 1
- `title`: "Executive Summary & Problem Discovery"
- `headline`: Strong headline summarizing the key findings and the core problem (e.g. "Category discovery is bottlenecked by trust and search discovery barriers rather than delivery speed")
- `key_metrics`: 2-3 key metrics (e.g. total signals, top themes count, etc.)
- `content`: Clean, high-impact bullet points detailing dataset overview, top insights, and a generated Problem Statement explaining what the problem is, who is affected, why it exists, and its severity.
- `visualization`: {{"type": "distribution", "data": {source_dist}}}
- `speaker_notes`: {{"what_to_say": "...", "why_it_matters": "...", "audience_question": "...", "suggested_answer": "..."}}

### Slide 2: Evidence & Supporting Analysis
- `slide_number`: 2
- `title`: "Evidence & Supporting Analysis"
- `headline`: An insight-driven headline summarizing what the data shows (e.g. "Beauty and Electronics suffer from quality and trust concerns while Grocery remains the habit anchor")
- `key_metrics`: 2-3 category metrics from category mentions (e.g. percentage of grocery mentions vs beauty)
- `content`: McKinsey-style analysis answering "So what?", detailing highest and poorest performing categories, and why users stick to familiar categories (awareness, trust, habit barriers).
- `visualization`: {{"type": "barriers_chart", "data": {category_counts}}}
- `speaker_notes`: {{"what_to_say": "...", "why_it_matters": "...", "audience_question": "...", "suggested_answer": "..."}}

### Slide 3: Product Opportunity & MVP Recommendation
- `slide_number`: 3
- `title`: "Product Opportunity & MVP Recommendation"
- `headline`: Headline describing the primary proposed solution
- `key_metrics`: RICE / ICE prioritization scores
- `mvp_details`: {{"target_users": "...", "pain_points": "...", "root_cause": "...", "proposed_solution": "...", "core_features": ["feature 1", "feature 2"], "success_metrics": ["metric 1"], "roadmap": {{"now": ["item 1"], "next": ["item 2"], "later": ["item 3"]}}}}
- `visualization`: {{"type": "rice_matrix", "data": [{{"opportunity": o.title, "impact": o.impact, "effort": o.effort, "confidence": o.confidence}} for o in opportunities[:4]]}}
- `speaker_notes`: {{"what_to_say": "...", "why_it_matters": "...", "audience_question": "...", "suggested_answer": "..."}}

### Slide 4: Final Recommendation & Next Steps
- `slide_number`: 4
- `title`: "Final Recommendation & Next Steps"
- `headline`: One-sentence executive recommendation
- `key_metrics`: Expected KPI improvements
- `content`: Summary of what should be built, why now, expected value, future enhancements, and next experiments to validate the MVP.
- `visualization`: {{"type": "roadmap", "data": ["Build MVP Feed", "Pilot and A/B Test", "Expand Category Catalog"]}}
- `speaker_notes`: {{"what_to_say": "...", "why_it_matters": "...", "audience_question": "...", "suggested_answer": "..."}}

Ensure all fields are fully populated and relevant. Keep text concise, using consulting bullet style."""

    result = llm.generate(REPORT_SYSTEM_PROMPT, prompt, creative=False)
    return result
