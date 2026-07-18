"""
Pulse Intelligence — Strategy Deep Dive Engine

Executes a 16-step Principal PM / Strategy Consultant analysis framework
that applies first-principles thinking, systems analysis, behavioral science,
and competitive strategy to the collected product review signals.

Each step is an independent LLM call with a specialized prompt grounded
in the actual scraped data context.
"""

import json
import logging
from core.llm_client import get_llm_client

logger = logging.getLogger(__name__)

STRATEGY_SYSTEM_PROMPT = """You are a cross-functional Product Strategy Council composed of:
- Principal Product Manager (Google)
- Director of Product (Amazon)
- Staff Product Manager (Airbnb)
- Product Strategy Partner (McKinsey)
- Behavioral Economist
- Cognitive Psychologist
- UX Research Lead
- Data Scientist
- Growth Product Manager
- AI Research Scientist
- Systems Thinking Expert

Your responsibility is NOT to generate obvious solutions. Your responsibility is to discover the REAL problem.
Your success metric is measured by the quality of thinking, not the speed of answering.
Never jump to solutions. Think like someone whose recommendation could cost or save a billion-dollar company.

Every recommendation must answer:
- Why is this important? Why now?
- Why hasn't someone already solved it?
- Why will users care?
- What evidence supports this?

You must respond in a single valid JSON object matching the requested schema. Do not output markdown around the JSON."""


def _build_context(signals, themes, barriers, personas, opportunities) -> str:
    """Build a compact context string from pipeline data."""
    sig_summary = f"Total signals analyzed: {len(signals)}"
    theme_titles = ", ".join(t.title for t in themes[:5]) if themes else "None"
    barrier_types = ", ".join(b.barrier_type.value for b in barriers[:5]) if barriers else "None"
    persona_names = ", ".join(p.name for p in personas[:4]) if personas else "None"
    opp_titles = ", ".join(o.title for o in opportunities[:5]) if opportunities else "None"

    sample_reviews = []
    for s in signals[:30]:
        stars = f"{'★' * (s.rating or 0)}" if s.rating else ""
        sample_reviews.append(f"[{s.source.value}|{s.app_name}|{stars}] {s.content[:200]}")

    return f"""## PROJECT CONTEXT
{sig_summary}
Themes: {theme_titles}
Barriers: {barrier_types}
Personas: {persona_names}
Opportunities: {opp_titles}

## SAMPLE CONSUMER SIGNALS
{chr(10).join(sample_reviews)}"""


STEP_CONFIGS = [
    {
        "id": "step_1",
        "title": "Problem Restatement",
        "phase": 1,
        "prompt": """Restate the core problem discovered from the consumer signals.
Then rewrite it from four perspectives:
1. User perspective: What pain does the user feel?
2. Business perspective: What revenue/growth risk does this create?
3. Technology perspective: What technical constraint causes or amplifies it?
4. Market perspective: How does this problem position the company vs competitors?

Return JSON: {{"user_perspective": "...", "business_perspective": "...", "technology_perspective": "...", "market_perspective": "...", "core_problem_restatement": "..."}}"""
    },
    {
        "id": "step_2",
        "title": "Challenge Assumptions",
        "phase": 1,
        "prompt": """List every hidden assumption embedded in the problem space and signals.
For each assumption, answer:
- Why do we believe this?
- What evidence supports it?
- What evidence contradicts it?

Return JSON: {{"assumptions": [{{"assumption": "...", "why_believed": "...", "supporting_evidence": "...", "contradicting_evidence": "..."}}]}}"""
    },
    {
        "id": "step_3",
        "title": "5 Whys Analysis",
        "phase": 1,
        "prompt": """Perform a rigorous 5 Whys analysis on the top problem discovered from the signals.
Continue until no deeper explanation exists.

Return JSON: {{"problem": "...", "why_1": {{"question": "Why?", "answer": "..."}}, "why_2": {{"question": "Why?", "answer": "..."}}, "why_3": {{"question": "Why?", "answer": "..."}}, "why_4": {{"question": "Why?", "answer": "..."}}, "why_5": {{"question": "Why?", "answer": "..."}}, "root_cause": "..."}}"""
    },
    {
        "id": "step_4",
        "title": "Issue Tree",
        "phase": 1,
        "prompt": """Build an issue tree that decomposes the problem into branches:
User, Business, Technology, Psychology, Market, Operations, Data, Economics, Trust, Social, Behavior.
Each branch must have 2-3 specific sub-issues grounded in the signal data.

Return JSON: {{"branches": [{{"category": "...", "sub_issues": [{{"issue": "...", "evidence": "..."}}]}}]}}"""
    },
    {
        "id": "step_5",
        "title": "Behavioral Analysis",
        "phase": 2,
        "prompt": """Analyze which behavioral and psychological factors stop users from exploring new categories or changing habits.
Evaluate each: Fear, Risk, Regret, Choice Overload, Trust, Status, Habit, Loss Aversion, Social Proof, Mental Models, Cognitive Load, Motivation, Decision Fatigue.

Return JSON: {{"behavioral_factors": [{{"factor": "...", "impact_level": "high/medium/low", "evidence_from_signals": "...", "intervention_idea": "..."}}]}}"""
    },
    {
        "id": "step_6",
        "title": "Jobs To Be Done",
        "phase": 2,
        "prompt": """Identify deep Jobs-To-Be-Done from the signals:
- Functional Job: What task are users trying to accomplish?
- Emotional Job: What feeling are they seeking?
- Social Job: How do they want to be perceived?
- Hidden Job: What unspoken need exists?
- Future Job: What job will emerge as the market evolves?

Return JSON: {{"functional_job": "...", "emotional_job": "...", "social_job": "...", "hidden_job": "...", "future_job": "..."}}"""
    },
    {
        "id": "step_7",
        "title": "User Journey Mapping",
        "phase": 2,
        "prompt": """Map the complete user journey across Before, During, and After phases.
For each phase identify: Pain points, Emotions, Questions users ask, Opportunities for intervention, and Failure points.

Return JSON: {{"before": {{"pain_points": [...], "emotions": [...], "questions": [...], "opportunities": [...], "failure_points": [...]}}, "during": {{"pain_points": [...], "emotions": [...], "questions": [...], "opportunities": [...], "failure_points": [...]}}, "after": {{"pain_points": [...], "emotions": [...], "questions": [...], "opportunities": [...], "failure_points": [...]}}}}"""
    },
    {
        "id": "step_8",
        "title": "Root Cause Matrix",
        "phase": 2,
        "prompt": """Create a root cause matrix linking problems to evidence, root causes, impact, and possible interventions.
Provide exactly 5 rows.

Return JSON: {{"matrix": [{{"problem": "...", "evidence": "...", "root_cause": "...", "impact": "...", "intervention": "..."}}]}}"""
    },
    {
        "id": "step_9",
        "title": "Competitive & Market Research",
        "phase": 2,
        "prompt": """Analyze the competitive landscape for quick commerce category exploration:
- Direct competitors (Zepto, Blinkit, Swiggy Instamart, etc.)
- Indirect competitors (Amazon, Flipkart, BigBasket)
- Substitutes (offline retail, specialty stores)
- Emerging startups

For each explain: WHY they succeed, WHY they fail, and identify market gaps.

Return JSON: {{"competitors": [{{"name": "...", "type": "direct/indirect/substitute/emerging", "why_succeeds": "...", "why_fails": "...", "market_gap": "..."}}]}}"""
    },
    {
        "id": "step_10",
        "title": "White Space Opportunities",
        "phase": 3,
        "prompt": """Identify white space opportunities by answering:
- What is everyone optimizing for?
- What is nobody optimizing for?
- Where is the blind spot?
- What assumption does every competitor share?
- Can that assumption be broken?

Return JSON: {{"everyone_optimizes": "...", "nobody_optimizes": "...", "blind_spot": "...", "shared_assumption": "...", "breaking_assumption": "...", "white_space_opportunities": [{{"title": "...", "rationale": "..."}}]}}"""
    },
    {
        "id": "step_11",
        "title": "Second-Order Thinking",
        "phase": 3,
        "prompt": """Apply second-order thinking to the top recommended solution.
Answer: What happens immediately? After one month? After one year?
What unintended consequences? Who loses? Who benefits? Could users game this? Could the metric be manipulated?

Return JSON: {{"immediate_effects": [...], "one_month_effects": [...], "one_year_effects": [...], "unintended_consequences": [...], "who_loses": [...], "who_benefits": [...], "gaming_risks": [...], "metric_manipulation_risks": [...]}}"""
    },
    {
        "id": "step_12",
        "title": "Metrics Framework",
        "phase": 3,
        "prompt": """Define a complete metrics framework:
- North Star Metric
- Input Metrics (3)
- Output Metrics (3)
- Guardrail Metrics (2)
- Counter Metrics (2)
- Leading Indicators (2)
- Lagging Indicators (2)
- Experiment Plan with success and failure criteria

Return JSON: {{"north_star": {{"name": "...", "definition": "...", "target": "..."}}, "input_metrics": [{{"name": "...", "definition": "..."}}], "output_metrics": [{{"name": "...", "definition": "..."}}], "guardrail_metrics": [{{"name": "...", "definition": "...", "threshold": "..."}}], "counter_metrics": [{{"name": "...", "definition": "..."}}], "leading_indicators": [{{"name": "...", "signal": "..."}}], "lagging_indicators": [{{"name": "...", "signal": "..."}}], "experiment_plan": {{"hypothesis": "...", "success_criteria": "...", "failure_criteria": "...", "sample_size": "...", "duration": "..."}}}}"""
    },
    {
        "id": "step_13",
        "title": "AI Opportunity Discovery",
        "phase": 3,
        "prompt": """Instead of asking "Can AI be added?", analyze:
- What decisions currently require human effort that AI could assist?
- Can AI reduce uncertainty for users?
- Can AI summarize complexity?
- Can AI predict user intent?
- Can AI personalize outcomes?
- Can AI become a trusted advisor?

Return JSON: {{"ai_opportunities": [{{"decision_area": "...", "current_human_effort": "...", "ai_intervention": "...", "impact": "...", "feasibility": "high/medium/low"}}]}}"""
    },
    {
        "id": "step_14",
        "title": "Solution Generation",
        "phase": 4,
        "prompt": """Generate solutions across 4 categories. For each provide: why it works, trade-offs, implementation difficulty (1-10), business impact (1-10), defensibility assessment.

Return JSON: {{"conservative": {{"title": "...", "description": "...", "why_works": "...", "trade_offs": "...", "difficulty": 0, "impact": 0, "defensibility": "..."}}, "innovative": {{"title": "...", "description": "...", "why_works": "...", "trade_offs": "...", "difficulty": 0, "impact": 0, "defensibility": "..."}}, "moonshot": {{"title": "...", "description": "...", "why_works": "...", "trade_offs": "...", "difficulty": 0, "impact": 0, "defensibility": "..."}}, "ai_first": {{"title": "...", "description": "...", "why_works": "...", "trade_offs": "...", "difficulty": 0, "impact": 0, "defensibility": "..."}}}}"""
    },
    {
        "id": "step_15",
        "title": "Competitive Advantage Assessment",
        "phase": 4,
        "prompt": """Evaluate the recommended solution using competitive moat criteria:
- Can competitors copy this? How long?
- Does it improve with data?
- Does it become stronger with more users?
- Does it create switching costs?
- Does it create network effects?
- Does it create proprietary intelligence?
- Does it become an AI moat?

Return JSON: {{"copyability": {{"can_copy": true, "time_to_copy": "..."}}, "data_advantage": "...", "user_network_effect": "...", "switching_costs": "...", "network_effects": "...", "proprietary_intelligence": "...", "ai_moat": "...", "overall_defensibility_score": 0, "verdict": "..."}}"""
    },
    {
        "id": "step_16",
        "title": "Executive Presentation",
        "phase": 4,
        "prompt": """Create executive-ready takeaways assuming leadership has only 5 minutes.
Provide:
- One-line insight
- 3 key supporting data points
- The single recommended action
- Decision rationale (why this, why now)
- What would a Principal PM, McKinsey Partner, and Behavioral Scientist debate before approving?

Return JSON: {{"one_line_insight": "...", "supporting_data": [...], "recommended_action": "...", "why_this": "...", "why_now": "...", "debate_points": [{{"role": "Principal PM / McKinsey Partner / Behavioral Scientist", "argument": "..."}}]}}"""
    },
]


def run_strategy_deep_dive(signals, themes, barriers, personas, opportunities) -> dict:
    """
    Execute the full 16-step strategy deep dive analysis.
    Returns a dict with step results and progress metadata.
    """
    llm = get_llm_client()
    context = _build_context(signals, themes, barriers, personas, opportunities)

    results = {}
    completed = 0
    total = len(STEP_CONFIGS)

    for step_cfg in STEP_CONFIGS:
        step_id = step_cfg["id"]
        logger.info(f"[Strategy Deep Dive] Running {step_id}: {step_cfg['title']}...")

        full_prompt = f"""{context}

---

## ANALYSIS STEP: {step_cfg['title']}

{step_cfg['prompt']}"""

        try:
            response = llm.generate(STRATEGY_SYSTEM_PROMPT, full_prompt, creative=False)
            if isinstance(response, dict):
                results[step_id] = {
                    "title": step_cfg["title"],
                    "phase": step_cfg["phase"],
                    "data": response,
                    "status": "complete",
                }
            else:
                parsed = json.loads(response)
                results[step_id] = {
                    "title": step_cfg["title"],
                    "phase": step_cfg["phase"],
                    "data": parsed,
                    "status": "complete",
                }
        except Exception as e:
            logger.error(f"[Strategy Deep Dive] Step {step_id} failed: {e}")
            results[step_id] = {
                "title": step_cfg["title"],
                "phase": step_cfg["phase"],
                "data": {"error": str(e)},
                "status": "failed",
            }

        completed += 1
        logger.info(f"[Strategy Deep Dive] Progress: {completed}/{total}")

    return {
        "steps": results,
        "total_steps": total,
        "completed_steps": completed,
        "phases": {
            1: "Problem Discovery",
            2: "Behavioral & Market Analysis",
            3: "Strategic Opportunity",
            4: "Solutions & Presentation",
        },
    }
