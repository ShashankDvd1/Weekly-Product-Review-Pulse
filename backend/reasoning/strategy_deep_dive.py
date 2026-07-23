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


def _build_context(signals, themes, barriers, personas, opportunities, problem_statement: str = None) -> str:
    """Build a compact context string from pipeline data and problem statement."""
    sig_summary = f"Total signals analyzed: {len(signals)}"
    theme_titles = ", ".join(t.title for t in themes[:5]) if themes else "None"
    barrier_types = ", ".join(b.barrier_type.value for b in barriers[:5]) if barriers else "None"
    persona_names = ", ".join(p.name for p in personas[:4]) if personas else "None"
    opp_titles = ", ".join(o.title for o in opportunities[:5]) if opportunities else "None"

    sample_reviews = []
    for s in signals[:30]:
        stars = f"{'★' * (s.rating or 0)}" if s.rating else ""
        sample_reviews.append(f"[{s.source.value}|{s.app_name}|{stars}] {s.content[:200]}")

    prob_stmt_block = f"## TARGET PROBLEM STATEMENT / STRATEGIC FOCUS\n{problem_statement}\n" if problem_statement else ""

    return f"""## PROJECT CONTEXT
{prob_stmt_block}{sig_summary}
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
        "prompt": """Restate the core problem using the MECE (Mutually Exclusive, Collectively Exhaustive) framework.
Then rewrite it from four distinct strategic perspectives:
1. User perspective (HEART Framework: Pain/Friction points)
2. Business perspective (Revenue/Growth/Retention risk)
3. Technology perspective (Architectural/Data/System constraints)
4. Market perspective (Competitive positioning & Differentiation gap)

Return JSON: {{"user_perspective": "...", "business_perspective": "...", "technology_perspective": "...", "market_perspective": "...", "core_problem_restatement": "..."}}"""
    },
    {
        "id": "step_2",
        "title": "Challenge Assumptions",
        "phase": 1,
        "prompt": """Apply First-Principles Thinking to identify and challenge every hidden assumption embedded in this problem space.
For each assumption, perform a validation check:
- What is the underlying belief?
- What direct user evidence/data backs this up?
- What contradicting signals/data points did we scrape?
- Verdict: Validated or Refuted?

Return JSON: {{"assumptions": [{{"assumption": "...", "why_believed": "...", "supporting_evidence": "...", "contradicting_evidence": "...", "verdict": "Validated/Refuted"}}]}}"""
    },
    {
        "id": "step_3",
        "title": "5 Whys Analysis",
        "phase": 1,
        "prompt": """Perform a rigorous 5 Whys cause-and-effect analysis using the Ishikawa (Fishbone) causal framework.
Deconstruct the core customer complaint down to its systemic, operational, or psychological root cause.

Return JSON: {{"problem": "...", "why_1": {{"question": "Why?", "answer": "..."}}, "why_2": {{"question": "Why?", "answer": "..."}}, "why_3": {{"question": "Why?", "answer": "..."}}, "why_4": {{"question": "Why?", "answer": "..."}}, "why_5": {{"question": "Why?", "answer": "..."}}, "root_cause": "..."}}"""
    },
    {
        "id": "step_4",
        "title": "Issue Tree",
        "phase": 1,
        "prompt": """Decompose the problem into a MECE Issue Tree spanning multiple critical branches:
User, Business, Psychology, Operations, and Economics.
Each branch must have 2-3 specific sub-issues grounded in the actual scraped signals.

Return JSON: {{"branches": [{{"category": "...", "sub_issues": [{{"issue": "...", "evidence": "..."}}]}}]}}"""
    },
    {
        "id": "step_5",
        "title": "Behavioral Analysis",
        "phase": 2,
        "prompt": """Evaluate user friction using the Fogg Behavior Model (B=MAP: Motivation, Ability, Prompt) and Prospect Theory (Loss Aversion, Status Quo Bias, Habit loops).
Identify exactly which behavioral blockers prevent users from exploring new categories or changing their purchasing habits.

Return JSON: {{"behavioral_factors": [{{"factor": "B=MAP component / Prospect Theory", "impact_level": "high/medium/low", "evidence_from_signals": "...", "intervention_idea": "..."}}]}}"""
    },
    {
        "id": "step_6",
        "title": "Jobs To Be Done",
        "phase": 2,
        "prompt": """Define the deep Jobs-To-Be-Done (Clayton Christensen's JTBD Framework / Outcome-Driven Innovation):
- Functional Job: Operational task user is trying to get done.
- Emotional Job: Personal feeling/security sought.
- Social Job: How they want to be perceived by peers.
- Hidden Job: Unspoken/unconscious friction need.
- Future Job: Job that will emerge as the platform evolves.

Return JSON: {{"functional_job": "...", "emotional_job": "...", "social_job": "...", "hidden_job": "...", "future_job": "..."}}"""
    },
    {
        "id": "step_7",
        "title": "User Journey Mapping",
        "phase": 2,
        "prompt": """Map the customer journey across Before, During, and After phases applying the Peak-End Rule and Moments of Friction.
Identify: Pain points, Emotions, Questions asked, Opportunities for intervention, and Failure points for each phase.

Return JSON: {{"before": {{"pain_points": [...], "emotions": [...], "questions": [...], "opportunities": [...], "failure_points": [...]}}, "during": {{"pain_points": [...], "emotions": [...], "questions": [...], "opportunities": [...], "failure_points": [...]}}, "after": {{"pain_points": [...], "emotions": [...], "questions": [...], "opportunities": [...], "failure_points": [...]}}}}"""
    },
    {
        "id": "step_8",
        "title": "Root Cause Matrix",
        "phase": 2,
        "prompt": """Structure a Root Cause Matrix applying Systems Thinking and Bottleneck Mapping.
Link specific observed problems to their supporting signals, root causes, system impact, and leverage points (interventions).
Provide exactly 5 rows.

Return JSON: {{"matrix": [{{"problem": "...", "evidence": "...", "root_cause": "...", "impact": "...", "intervention": "..."}}]}}"""
    },
    {
        "id": "step_9",
        "title": "Competitive & Market Research",
        "phase": 2,
        "prompt": """Analyze the competitive landscape using Porter's Five Forces and SWOT frameworks.
Assess direct quick commerce players, indirect marketplaces, and substitutes. Explain why they succeed/fail and find market gaps.

Return JSON: {{"competitors": [{{"name": "...", "type": "direct/indirect/substitute/emerging", "why_succeeds": "...", "why_fails": "...", "market_gap": "..."}}]}}"""
    },
    {
        "id": "step_10",
        "title": "White Space Opportunities",
        "phase": 3,
        "prompt": """Apply the Blue Ocean Strategy Canvas and Value Proposition Design Grid to uncover white space opportunities.
Analyze what competitors over-optimize for, what they neglect, and outline opportunities that break shared industry assumptions.

Return JSON: {{"everyone_optimizes": "...", "nobody_optimizes": "...", "blind_spot": "...", "shared_assumption": "...", "breaking_assumption": "...", "white_space_opportunities": [{{"title": "...", "rationale": "..."}}]}}"""
    },
    {
        "id": "step_11",
        "title": "Second-Order Thinking",
        "phase": 3,
        "prompt": """Apply Second-Order Thinking and Game Theory to your recommended solution using the Futures Wheel.
Outline immediately visible effects, 1-month consequences, and 1-year systemic shifts. Evaluate gaming risks, incentives, and metric manipulation.

Return JSON: {{"immediate_effects": [...], "one_month_effects": [...], "one_year_effects": [...], "unintended_consequences": [...], "who_loses": [...], "who_benefits": [...], "gaming_risks": [...], "metric_manipulation_risks": [...]}}"""
    },
    {
        "id": "step_12",
        "title": "Metrics Framework",
        "phase": 3,
        "prompt": """Design a comprehensive Product Metrics Dashboard using the Google HEART Framework and North Star Metric Framework:
- North Star Metric (name, definition, 90-day target)
- Input Metrics (3) & Output Metrics (3)
- Guardrail Metrics (2) & Counter Metrics (2)
- Leading & Lagging Indicators
- A/B Testing Experiment Plan with statistical success/failure criteria.

Return JSON: {{"north_star": {{"name": "...", "definition": "...", "target": "..."}}, "input_metrics": [{{"name": "...", "definition": "..."}}], "output_metrics": [{{"name": "...", "definition": "..."}}], "guardrail_metrics": [{{"name": "...", "definition": "...", "threshold": "..."}}], "counter_metrics": [{{"name": "...", "definition": "..."}}], "leading_indicators": [{{"name": "...", "signal": "..."}}], "lagging_indicators": [{{"name": "...", "signal": "..."}}], "experiment_plan": {{"hypothesis": "...", "success_criteria": "...", "failure_criteria": "...", "sample_size": "...", "duration": "..."}}}}"""
    },
    {
        "id": "step_13",
        "title": "AI Opportunity Discovery",
        "phase": 3,
        "prompt": """Build an AI Utility Matrix mapping Generative vs Predictive vs Agentic opportunities.
Analyze what user decisions require high cognitive effort, where AI can reduce user uncertainty, and where it can predict user intent.

Return JSON: {{"ai_opportunities": [{{"decision_area": "...", "current_human_effort": "...", "ai_intervention": "...", "impact": "...", "feasibility": "high/medium/low"}}]}}"""
    },
    {
        "id": "step_14",
        "title": "Solution Generation",
        "phase": 4,
        "prompt": """Generate four solution options (Conservative, Innovative, Moonshot, AI-First).
Apply the RICE Prioritization Framework to assign numeric scores to each solution:
- Reach (estimated users impacted/month)
- Impact (1-10 product utility impact)
- Confidence (1-10 data validation confidence)
- Effort (1-10 engineering effort)
- Calculated RICE Score = (Reach * Impact * Confidence) / Effort

Return JSON: {{"conservative": {{"title": "...", "description": "...", "why_works": "...", "trade_offs": "...", "reach": 0, "impact": 0, "confidence": 0, "effort": 0, "rice_score": 0.0}}, "innovative": {{"title": "...", "description": "...", "why_works": "...", "trade_offs": "...", "reach": 0, "impact": 0, "confidence": 0, "effort": 0, "rice_score": 0.0}}, "moonshot": {{"title": "...", "description": "...", "why_works": "...", "trade_offs": "...", "reach": 0, "impact": 0, "confidence": 0, "effort": 0, "rice_score": 0.0}}, "ai_first": {{"title": "...", "description": "...", "why_works": "...", "trade_offs": "...", "reach": 0, "impact": 0, "confidence": 0, "effort": 0, "rice_score": 0.0}}}}"""
    },
    {
        "id": "step_15",
        "title": "Competitive Advantage Assessment",
        "phase": 4,
        "prompt": """Evaluate the recommended solution using Hamilton Helmer's 7 Powers Moat Framework.
Assess how the solution builds: Scale Economies, Network Effects, Counter-Positioning, Switching Costs, Branding, Cornered Resource, or Process Power.

Return JSON: {{"powers": [{{"power": "Scale Economies/Network Effects/Counter-Positioning/Switching Costs/Branding/Cornered Resource/Process Power", "strength": "high/medium/low", "evidence": "..."}}], "overall_defensibility_score": 0, "verdict": "..."}}"""
    },
    {
        "id": "step_16",
        "title": "Executive Presentation",
        "phase": 4,
        "prompt": """Apply the Minto Pyramid Principle (SCQA structure: Situation, Complication, Question, Answer) to draft executive slides.
Provide a clear situation context, complicating signals, the strategic question, and your data-validated recommendation.

Return JSON: {{"situation": "...", "complication": "...", "question": "...", "answer": "...", "supporting_data": [...], "debate_points": [{{"role": "Principal PM / McKinsey Partner / Behavioral Scientist", "argument": "..."}}]}}"""
    },
]

from concurrent.futures import ThreadPoolExecutor
import threading

def _summarize_step_data(step_id: str, data: any) -> str:
    """Helper to convert step output JSON data to a highly compact summary to fit within LLM token limits."""
    if not data:
        return ""
    if isinstance(data, str):
        return data[:300]
    if not isinstance(data, dict):
        return str(data)[:300]
        
    summary_parts = []
    for k, v in data.items():
        if isinstance(v, list):
            summary_parts.append(f"{k}: {', '.join(str(x) for x in v[:3])}")
        elif isinstance(v, dict):
            sub_parts = [f"{sk}: {sv}" for sk, sv in list(v.items())[:2]]
            summary_parts.append(f"{k}: {{{', '.join(sub_parts)}}}")
        else:
            summary_parts.append(f"{k}: {str(v)[:150]}")
    return "\n".join(summary_parts)[:350]


def run_strategy_deep_dive(signals, themes, barriers, personas, opportunities, problem_statement: str = None, progress_callback = None, existing_steps = None, on_step_complete = None, target_phase = "all", survey_context = None) -> dict:
    """
    Execute the full 16-step strategy deep dive analysis in structured dependency batches
    to ensure logical reasoning flow while parallelizing independent tasks for maximum speed.
    Supports running only Phase 1 (Discovery) or Phase 2 (Solutioning).
    """
    llm = get_llm_client()
    results = {}
    lock = threading.Lock()

    # Pre-populate results with already completed steps from cache
    if existing_steps:
        for s_id, s_val in existing_steps.items():
            if s_val.get("status") == "complete":
                results[s_id] = s_val

    # Define sequential dependency batches
    batches_phase_1 = [
        ["step_1"],
        ["step_2", "step_3"],
        ["step_4"],
        ["step_5", "step_6", "step_7", "step_9", "step_10", "step_12", "step_13"],
        ["step_8", "step_11"]
    ]
    batches_phase_2 = [
        ["step_14"],
        ["step_15"],
        ["step_16"]
    ]

    if target_phase == 1:
        batches = batches_phase_1
    elif target_phase == 2:
        batches = batches_phase_2
    else:
        batches = batches_phase_1 + batches_phase_2

    target_step_ids = [step for batch in batches for step in batch]
    total = len(target_step_ids)
    completed = 0

    def process_step(step_cfg):
        nonlocal completed
        step_id = step_cfg["id"]
        
        # Check if we can reuse the cached result for this step
        if existing_steps and step_id in existing_steps:
            cached = existing_steps[step_id]
            if cached.get("status") == "complete":
                logger.info(f"[Strategy Deep Dive] Reusing cached result for step {step_id}: {step_cfg['title']}")
                with lock:
                    results[step_id] = cached
                if progress_callback:
                    try:
                        progress_callback(step_id, step_cfg["title"], "start")
                        progress_callback(step_id, step_cfg["title"], "complete")
                    except Exception:
                        pass
                with lock:
                    completed += 1
                    logger.info(f"[Strategy Deep Dive] Progress: {completed}/{total}")
                return

        logger.info(f"[Strategy Deep Dive] Running {step_id}: {step_cfg['title']}...")
        if progress_callback:
            try:
                progress_callback(step_id, step_cfg["title"], "start")
            except Exception:
                pass

        # Build context dynamically from base context + previously completed steps
        base_context = _build_context(signals, themes, barriers, personas, opportunities, problem_statement=problem_statement)
        completed_context_parts = []
        with lock:
            for s_id, s_info in results.items():
                completed_context_parts.append(f"### COMPLETED {s_id.upper()}: {s_info['title']}\n{_summarize_step_data(s_id, s_info['data'])}")
        
        full_context = base_context
        if completed_context_parts:
            full_context += "\n\n## COMPLETED STEPS HISTORY (Logical Causal Flow)\n" + "\n\n".join(completed_context_parts)
            
        if survey_context:
            full_context += f"\n\n## VALIDATED SURVEY CONTEXT (From User Interviews)\n{json.dumps(survey_context, indent=2)}\nUse this validated context to inform your solutions."


        full_prompt = f"""{full_context}

---

## ANALYSIS STEP: {step_cfg['title']}

{step_cfg['prompt']}"""

        try:
            response = llm.generate(STRATEGY_SYSTEM_PROMPT, full_prompt, creative=False)
            if isinstance(response, dict):
                parsed_data = response
            else:
                parsed_data = json.loads(response)
            
            step_res = {
                "title": step_cfg["title"],
                "phase": step_cfg["phase"],
                "data": parsed_data,
                "status": "complete",
            }
            with lock:
                results[step_id] = step_res
                
            if on_step_complete:
                try:
                    on_step_complete(step_id, step_res)
                except Exception as oce:
                    logger.error(f"Error in on_step_complete callback: {oce}")

            if progress_callback:
                try:
                    progress_callback(step_id, step_cfg["title"], "complete")
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"[Strategy Deep Dive] Step {step_id} failed: {e}")
            with lock:
                results[step_id] = {
                    "title": step_cfg["title"],
                    "phase": step_cfg["phase"],
                    "data": {"error": str(e)},
                    "status": "failed",
                }
            if progress_callback:
                try:
                    progress_callback(step_id, step_cfg["title"], "failed", detail=str(e))
                except Exception:
                    pass

        with lock:
            completed += 1
            logger.info(f"[Strategy Deep Dive] Progress: {completed}/{total}")

    # Process each batch sequentially, running steps within each batch concurrently
    with ThreadPoolExecutor(max_workers=8) as executor:
        for batch_step_ids in batches:
            batch_configs = [cfg for cfg in STEP_CONFIGS if cfg["id"] in batch_step_ids]
            list(executor.map(process_step, batch_configs))

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
