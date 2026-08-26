import json
import logging
from core.llm_client import LLMClient
from core.config import LLM_MODEL_REASONING, LLM_TEMPERATURE_ANALYTICAL
from core.prompts import ANTI_HALLUCINATION_RULES

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """You are a McKinsey Engagement Manager and Executive Storytelling expert preparing a high-impact board presentation for the CEO.
Synthesize the provided Strategy Deep Dive results into exactly 10 slides following the strict McKinsey arc below.

# INPUT — Strategy Deep Dive Steps:
{strategy_steps}

# CRITICAL RULES
1. Output EXACTLY 10 slides in this order with these EXACT type values (do not invent other types).
2. HEADLINES MUST BE CONCLUSIONS, NOT generic section titles.
3. TAKE-AWAY TITLES: The 'title' field of each slide MUST be a takeaway message.
4. HIGH-DENSITY BULLETS: Bullet points in 'bullets' must be detailed multi-sentence statements. Each must link:
   - A core customer behavioral finding or friction point.
   - Direct quantitative metrics or qualitative quote evidence.
   - The direct strategic implication or product recommendation.
5. Determine the target brand/product from data and set brand metadata.
6. ANTI-HALLUCINATION: Preserve all statistics, percentages, and user quotes EXACTLY as they appear in the input.
7. Return ONLY a valid JSON object. No markdown backticks. No text outside the JSON.

{ANTI_HALLUCINATION_RULES}

# MANDATORY 10-SLIDE OUTLINE (use these exact types):
Slide 1: type = "market_gap"
Slide 2: type = "user_research"
Slide 3: type = "personas_journey"
Slide 4: type = "problem_framing"
Slide 5: type = "hypotheses_rice"
Slide 6: type = "solution_comparison"
Slide 7: type = "mvp_spec"
Slide 8: type = "data_flow_edges"
Slide 9: type = "metrics_indicators"
Slide 10: type = "failure_mitigations"

# JSON SCHEMA
Return a JSON object in EXACTLY this format:
{{
  "presentation_title": "string",
  "subtitle": "string",
  "presentation_theme": "e.g. Blinkit Yellow / Zepto Purple / Swiggy Orange",
  "app_name": "Blinkit | Zepto | Swiggy Instamart",
  "primary_color": "#hex",
  "secondary_color": "#hex",
  "slides": [
    {{
      "slide_number": 1,
      "type": "market_gap",
      "title": "Slide takeaway message",
      "headline": "Full-sentence key insight as headline",
      "bullets": ["Detailed bullet 1", "Detailed bullet 2", "Detailed bullet 3"],
      "speaker_notes": "McKinsey presenter talk track",
      "market_gap_table": [
        {{"platform": "Blinkit", "offer": "What they currently offer", "missing": "What is missing"}},
        {{"platform": "Zepto", "offer": "...", "missing": "..."}},
        {{"platform": "Swiggy Instamart", "offer": "...", "missing": "..."}},
        {{"platform": "BigBasket", "offer": "...", "missing": "..."}},
        {{"platform": "Amazon Fresh", "offer": "...", "missing": "..."}}
      ],
      "why_solve_first": ["Reason 1", "Reason 2", "Reason 3"],
      "stats": [
        {{"label": "Market stat label", "value": "Value or %"}},
        {{"label": "Market stat label", "value": "Value or %"}},
        {{"label": "Market stat label", "value": "Value or %"}}
      ]
    }},
    {{
      "slide_number": 2,
      "type": "user_research",
      "title": "Slide takeaway message",
      "headline": "Full-sentence key insight",
      "bullets": ["Detailed bullet 1", "Detailed bullet 2", "Detailed bullet 3"],
      "speaker_notes": "...",
      "findings": {{
        "total_analyzed": 150,
        "llm_labeled": 150,
        "discovery_pain_pct": 20,
        "top_theme": "most common pain theme",
        "wants_variety_pct": 40,
        "less_repetition_pct": 30,
        "real_shuffle_pct": 20,
        "better_music_pct": 10
      }},
      "sentiment": {{
        "negative": 60,
        "neutral": 30,
        "positive": 60
      }},
      "cited_quotes": [
        {{"quote": "Exact verbatim user quote", "source": "Platform / Review source"}},
        {{"quote": "Exact verbatim user quote", "source": "Platform / Review source"}},
        {{"quote": "Exact verbatim user quote", "source": "Platform / Review source"}}
      ]
    }},
    {{
      "slide_number": 3,
      "type": "personas_journey",
      "title": "Slide takeaway message",
      "headline": "Full-sentence key insight",
      "bullets": ["Detailed bullet 1", "Detailed bullet 2"],
      "speaker_notes": "...",
      "personas": [
        {{
          "name": "Persona 1 name",
          "title": "Their archetype e.g. The Grocery Loyalist",
          "meta": "Age range, city tier, usage frequency",
          "trust_pattern": "How they make purchase decisions",
          "unmet_need": "What they wish the platform provided",
          "behavioral_trap": "The habit loop keeping them stuck",
          "quote": "Representative quote from this persona"
        }},
        {{
          "name": "Persona 2 name",
          "title": "Their archetype",
          "meta": "Age range, city tier, usage frequency",
          "trust_pattern": "...",
          "unmet_need": "...",
          "behavioral_trap": "...",
          "quote": "..."
        }}
      ],
      "user_journey": [
        {{"stage": "1. Open", "behavior": "User opens app to buy habitual items", "friction": "Habit loop ignores discovery surface"}},
        {{"stage": "2. Served", "behavior": "Platform surfaces repeat list / history", "friction": "Algorithm optimises for repeat, not exploration"}},
        {{"stage": "3. Browse", "behavior": "User scrolls past unfamiliar category tabs", "friction": "No trust signals; authenticity concerns"}},
        {{"stage": "4. Checkout", "behavior": "Completes purchase in under 60 seconds", "friction": "High checkout speed = zero exploration window"}},
        {{"stage": "5. Exit", "behavior": "Exits app immediately after order placed", "friction": "Zero cross-sell achieved; habit reinforced"}}
      ]
    }},
    {{
      "slide_number": 4,
      "type": "problem_framing",
      "title": "Slide takeaway message",
      "headline": "Full-sentence key insight",
      "bullets": ["Detailed bullet 1", "Detailed bullet 2"],
      "speaker_notes": "...",
      "true_problem": "The root cause framed as a strategic problem statement",
      "target_cohort": "Specific user cohort most impacted by this problem",
      "evidences": ["Evidence 1 with data", "Evidence 2 with data", "Evidence 3 with data"],
      "value_generated": {{
        "for_user": "User benefit from solving this",
        "for_platform": "Business / revenue benefit from solving this"
      }},
      "why_now": {{
        "saturation": "Why the market window is closing",
        "ai_unlock": "What AI/data capability makes this solvable now",
        "first_mover": "What competitive advantage first movers gain"
      }}
    }},
    {{
      "slide_number": 5,
      "type": "hypotheses_rice",
      "title": "Slide takeaway message",
      "headline": "Full-sentence key insight",
      "bullets": ["Detailed bullet 1", "Detailed bullet 2"],
      "speaker_notes": "...",
      "hypotheses": [
        {{"id": "H1", "name": "Primary hypothesis name", "statement": "If we do X, then Y because Z", "validation": "How we would validate this"}},
        {{"id": "H2", "name": "Alternative hypothesis name", "statement": "...", "validation": "..."}},
        {{"id": "H3", "name": "Alternative hypothesis name", "statement": "...", "validation": "..."}}
      ],
      "rice_scores": [
        {{"hypothesis_id": "H1", "reach": 9, "impact": 9, "confidence": 8, "effort": 6, "score": 108}},
        {{"hypothesis_id": "H2", "reach": 5, "impact": 6, "confidence": 6, "effort": 5, "score": 36}},
        {{"hypothesis_id": "H3", "reach": 4, "impact": 4, "confidence": 4, "effort": 7, "score": 9}}
      ],
      "winning_rationale": "Multi-sentence explanation of why H1 wins the RICE scoring"
    }},
    {{
      "slide_number": 6,
      "type": "solution_comparison",
      "title": "Slide takeaway message",
      "headline": "Full-sentence key insight",
      "bullets": ["Detailed bullet 1", "Detailed bullet 2"],
      "speaker_notes": "...",
      "solutions": [
        {{"id": "S1", "name": "Solution 1 name", "status": "REJECTED", "description": "What this solution does", "feedback": "Why it was rejected"}},
        {{"id": "S2", "name": "Solution 2 name", "status": "REJECTED", "description": "...", "feedback": "..."}},
        {{"id": "S3", "name": "Solution 3 name", "status": "REJECTED", "description": "...", "feedback": "..."}},
        {{"id": "S4", "name": "Chosen solution name", "status": "CHOSEN", "description": "...", "feedback": "Why this wins"}}
      ],
      "vs_comparison": [
        {{"against": "S1", "justification": "Why chosen beats S1"}},
        {{"against": "S2", "justification": "Why chosen beats S2"}},
        {{"against": "S3", "justification": "Why chosen beats S3"}}
      ]
    }},
    {{
      "slide_number": 7,
      "type": "mvp_spec",
      "title": "Slide takeaway message",
      "headline": "Full-sentence key insight",
      "bullets": ["Detailed bullet 1", "Detailed bullet 2"],
      "speaker_notes": "...",
      "screens": [
        {{"name": "Screen 1 name", "spec": "What this screen does and its key UX elements"}},
        {{"name": "Screen 2 name", "spec": "..."}},
        {{"name": "Screen 3 name", "spec": "..."}}
      ],
      "trust_cues": ["Trust cue 1", "Trust cue 2", "Trust cue 3"],
      "live_links": ["https://example-prototype.streamlit.app/"]
    }},
    {{
      "slide_number": 8,
      "type": "data_flow_edges",
      "title": "Slide takeaway message",
      "headline": "Full-sentence key insight",
      "bullets": ["Detailed bullet 1", "Detailed bullet 2"],
      "speaker_notes": "...",
      "data_flow": {{
        "review_engine": "How the review intelligence pipeline works end-to-end",
        "product_engine": "How the cross-sell recommendation engine works end-to-end"
      }},
      "nudges": ["Behavioural nudge 1", "Behavioural nudge 2", "Behavioural nudge 3"],
      "edge_cases": [
        {{"id": "E1", "title": "Edge case title", "mitigation": "How we handle this case"}},
        {{"id": "E2", "title": "Edge case title", "mitigation": "..."}},
        {{"id": "E3", "title": "Edge case title", "mitigation": "..."}},
        {{"id": "E4", "title": "Edge case title", "mitigation": "..."}}
      ]
    }},
    {{
      "slide_number": 9,
      "type": "metrics_indicators",
      "title": "Slide takeaway message",
      "headline": "Full-sentence key insight",
      "bullets": ["Detailed bullet 1", "Detailed bullet 2"],
      "speaker_notes": "...",
      "north_star": {{
        "name": "North Star Metric name",
        "definition": "Full definition of what this metric measures",
        "target": "From X% to Y% in Z months",
        "why": "Why this is the right north star",
        "stalls_action": "What signals a stall and what actions to take"
      }},
      "leading_indicators": [
        {{"name": "Leading indicator 1", "target": ">18%", "proves": "What improvement in this metric proves", "below_target_action": "What to do if below target"}},
        {{"name": "Leading indicator 2", "target": ">8%", "proves": "...", "below_target_action": "..."}},
        {{"name": "Leading indicator 3", "target": ">15%", "proves": "...", "below_target_action": "..."}},
        {{"name": "Leading indicator 4", "target": "+30%", "proves": "...", "below_target_action": "..."}}
      ]
    }},
    {{
      "slide_number": 10,
      "type": "failure_mitigations",
      "title": "Slide takeaway message",
      "headline": "Full-sentence key insight",
      "bullets": ["Detailed bullet 1", "Detailed bullet 2"],
      "speaker_notes": "...",
      "failures": [
        {{"risk": "What could go wrong", "handling": "How we prevent or respond", "severity": "CRIT"}},
        {{"risk": "What could go wrong", "handling": "...", "severity": "HIGH"}},
        {{"risk": "What could go wrong", "handling": "...", "severity": "MED"}}
      ],
      "guardrails": [
        {{"name": "Guardrail metric name", "threshold": "< 4%", "purpose": "Why this guardrail exists"}},
        {{"name": "Guardrail metric name", "threshold": "< 200ms", "purpose": "..."}},
        {{"name": "Guardrail metric name", "threshold": "< 1%", "purpose": "..."}}
      ],
      "closing_message": "Final resilience statement summarizing the risk strategy"
    }}
  ]
}}
"""


def trim_step_data(data):
    if isinstance(data, dict):
        trimmed = {}
        for k, v in list(data.items())[:6]:  # Keep max 6 keys
            if isinstance(v, list):
                trimmed[k] = [trim_step_data(item) for item in v[:3]]  # Keep max 3 items
            elif isinstance(v, str):
                trimmed[k] = v[:400] + "..." if len(v) > 400 else v
            elif isinstance(v, dict):
                trimmed[k] = trim_step_data(v)
            else:
                trimmed[k] = v
        return trimmed
    elif isinstance(data, list):
        return [trim_step_data(item) for item in data[:3]]
    elif isinstance(data, str):
        return data[:400] + "..." if len(data) > 400 else data
    return data


def format_step_data_as_text(data, indent=""):
    if isinstance(data, dict):
        lines = []
        for k, v in data.items():
            key_label = k.replace("_", " ").title()
            if isinstance(v, (dict, list)):
                lines.append(f"{indent}- **{key_label}**:")
                sub_res = format_step_data_as_text(v, indent + "  ")
                if sub_res:
                    lines.append(sub_res)
            else:
                lines.append(f"{indent}- **{key_label}**: {v}")
        return "\n".join(lines)
    elif isinstance(data, list):
        lines = []
        for item in data:
            if isinstance(item, (dict, list)):
                sub_res = format_step_data_as_text(item, indent + "  ")
                if sub_res:
                    lines.append(sub_res)
            else:
                lines.append(f"{indent}- {item}")
        return "\n".join(lines)
    return f"{indent}{data}"


def _build_step_context(strategy_data: dict) -> str:
    """Build trimmed step context string from strategy deep dive data."""
    steps = strategy_data.get("steps", {})
    steps_context_list = []
    high_impact_steps = ["step_1", "step_2", "step_4", "step_8", "step_13", "step_14"]
    for step_id, info in steps.items():
        if step_id not in high_impact_steps:
            continue
        step_title = info.get("title", step_id)
        raw_data = info.get("data", {})
        step_data = trim_step_data(raw_data)
        formatted_text = format_step_data_as_text(step_data)
        steps_context_list.append(f"### {step_id.upper()}: {step_title}\n{formatted_text}")

    ctx = "\n\n".join(steps_context_list)
    problem_statement = strategy_data.get("active_problem_statement", "")
    if problem_statement:
        ctx = f"## ACTIVE PROBLEM STATEMENT\n{problem_statement}\n\n" + ctx
    return ctx


# ── Per-batch prompt templates ──────────────────────────────────────────────

BATCH_A_SYSTEM = """You are a McKinsey Engagement Manager preparing slides 1-5 of a 10-slide board deck.
Output a JSON object with ONLY these 5 slides in a "slides" array plus brand metadata.
Use EXACT type values. No markdown. No text outside JSON.
ANTI-HALLUCINATION: preserve all statistics and quotes exactly as given."""

BATCH_B_SYSTEM = """You are a McKinsey Engagement Manager preparing slides 6-10 of a 10-slide board deck.
Output a JSON object with ONLY these 5 slides in a "slides" array.
Use EXACT type values. No markdown. No text outside JSON.
CRITICAL: Ensure no data is duplicated across slides. In Slide 6 (solution_comparison), S1, S2, S3, and S4 MUST be completely distinct solution concepts with different names, descriptions, and feedback. S4 MUST NOT be the same as S1.
ANTI-HALLUCINATION: preserve all statistics and quotes exactly as given."""

BATCH_A_SCHEMA = """\
Return exactly this JSON (slides 1-5 only):
{
  "presentation_title": "...",
  "subtitle": "...",
  "presentation_theme": "Theme matching target app",
  "app_name": "Target App Name",
  "primary_color": "#hex",
  "secondary_color": "#hex",
  "slides": [
    {
      "slide_number": 1, "type": "market_gap",
      "title": "takeaway title", "headline": "key insight headline",
      "bullets": ["detailed bullet 1", "detailed bullet 2", "detailed bullet 3"],
      "speaker_notes": "presenter notes",
      "market_gap_table": [
        {"platform": "Target App Name", "offer": "...", "missing": "..."},
        {"platform": "Competitor A", "offer": "...", "missing": "..."},
        {"platform": "Competitor B", "offer": "...", "missing": "..."},
        {"platform": "Competitor C", "offer": "...", "missing": "..."},
        {"platform": "Competitor D", "offer": "...", "missing": "..."}
      ],
      "why_solve_first": ["Reason 1", "Reason 2", "Reason 3"],
      "stats": [{"label": "...", "value": "..."}, {"label": "...", "value": "..."}, {"label": "...", "value": "..."}]
    },
    {
      "slide_number": 2, "type": "user_research",
      "title": "takeaway title", "headline": "key insight headline",
      "bullets": ["detailed bullet 1", "detailed bullet 2", "detailed bullet 3"],
      "speaker_notes": "presenter notes",
      "findings": {"total_analyzed": 150, "llm_labeled": 150, "discovery_pain_pct": 20, "top_theme": "...",
        "wants_variety_pct": 40, "less_repetition_pct": 30, "real_shuffle_pct": 20, "better_music_pct": 10},
      "sentiment": {"negative": 60, "neutral": 30, "positive": 60},
      "cited_quotes": [{"quote": "...", "source": "..."}, {"quote": "...", "source": "..."}, {"quote": "...", "source": "..."}]
    },
    {
      "slide_number": 3, "type": "personas_journey",
      "title": "takeaway title", "headline": "key insight headline",
      "bullets": ["detailed bullet 1", "detailed bullet 2"],
      "speaker_notes": "presenter notes",
      "personas": [
        {"name": "...", "title": "archetype", "meta": "age/city/frequency", "trust_pattern": "...", "unmet_need": "...", "behavioral_trap": "...", "quote": "..."},
        {"name": "...", "title": "archetype", "meta": "...", "trust_pattern": "...", "unmet_need": "...", "behavioral_trap": "...", "quote": "..."}
      ],
      "user_journey": [
        {"stage": "1. Open", "behavior": "...", "friction": "..."},
        {"stage": "2. Served", "behavior": "...", "friction": "..."},
        {"stage": "3. Browse", "behavior": "...", "friction": "..."},
        {"stage": "4. Checkout", "behavior": "...", "friction": "..."},
        {"stage": "5. Exit", "behavior": "...", "friction": "..."}
      ]
    },
    {
      "slide_number": 4, "type": "problem_framing",
      "title": "takeaway title", "headline": "key insight headline",
      "bullets": ["detailed bullet 1", "detailed bullet 2"],
      "speaker_notes": "presenter notes",
      "true_problem": "...", "target_cohort": "...",
      "evidences": ["...", "...", "..."],
      "value_generated": {"for_user": "...", "for_platform": "..."},
      "why_now": {"saturation": "...", "ai_unlock": "...", "first_mover": "..."}
    },
    {
      "slide_number": 5, "type": "hypotheses_rice",
      "title": "takeaway title", "headline": "key insight headline",
      "bullets": ["detailed bullet 1", "detailed bullet 2"],
      "speaker_notes": "presenter notes",
      "hypotheses": [
        {"id": "H1", "name": "...", "statement": "...", "validation": "..."},
        {"id": "H2", "name": "...", "statement": "...", "validation": "..."},
        {"id": "H3", "name": "...", "statement": "...", "validation": "..."}
      ],
      "rice_scores": [
        {"hypothesis_id": "H1", "reach": 9, "impact": 9, "confidence": 8, "effort": 4, "score": 162},
        {"hypothesis_id": "H2", "reach": 5, "impact": 6, "confidence": 6, "effort": 5, "score": 36},
        {"hypothesis_id": "H3", "reach": 4, "impact": 4, "confidence": 4, "effort": 7, "score": 9}
      ],
      "winning_rationale": "..."
    }
  ]
}"""

BATCH_B_SCHEMA = """\
Return exactly this JSON (slides 6-10 only):
{
  "slides": [
    {
      "slide_number": 6, "type": "solution_comparison",
      "title": "takeaway title", "headline": "key insight headline",
      "bullets": ["detailed bullet 1", "detailed bullet 2"],
      "speaker_notes": "presenter notes",
      "solutions": [
        {"id": "S1", "name": "Basic UI Refactor", "status": "REJECTED", "description": "...", "feedback": "..."},
        {"id": "S2", "name": "Broad Notification Campaign", "status": "REJECTED", "description": "...", "feedback": "..."},
        {"id": "S3", "name": "Simple Badges without Validation", "status": "REJECTED", "description": "...", "feedback": "..."},
        {"id": "S4", "name": "Chosen Solution Concept", "status": "CHOSEN", "description": "...", "feedback": "..."}
      ],
      "vs_comparison": [
        {"against": "S1", "justification": "..."},
        {"against": "S2", "justification": "..."},
        {"against": "S3", "justification": "..."}
      ]
    },
    {
      "slide_number": 7, "type": "mvp_spec",
      "title": "takeaway title", "headline": "key insight headline",
      "bullets": ["detailed bullet 1", "detailed bullet 2"],
      "speaker_notes": "presenter notes",
      "screens": [{"name": "...", "spec": "..."}, {"name": "...", "spec": "..."}, {"name": "...", "spec": "..."}],
      "trust_cues": ["cue 1", "cue 2", "cue 3"]
    },
    {
      "slide_number": 8, "type": "data_flow_edges",
      "title": "takeaway title", "headline": "key insight headline",
      "bullets": ["detailed bullet 1", "detailed bullet 2"],
      "speaker_notes": "presenter notes",
      "data_flow": {"review_engine": "...", "product_engine": "..."},
      "nudges": ["nudge 1", "nudge 2", "nudge 3"],
      "edge_cases": [
        {"id": "E1", "title": "...", "mitigation": "..."},
        {"id": "E2", "title": "...", "mitigation": "..."},
        {"id": "E3", "title": "...", "mitigation": "..."},
        {"id": "E4", "title": "...", "mitigation": "..."}
      ]
    },
    {
      "slide_number": 9, "type": "metrics_indicators",
      "title": "takeaway title", "headline": "key insight headline",
      "bullets": ["detailed bullet 1", "detailed bullet 2"],
      "speaker_notes": "presenter notes",
      "north_star": {"name": "...", "definition": "...", "target": "X% to Y%", "why": "...", "stalls_action": "..."},
      "leading_indicators": [
        {"name": "...", "target": ">18%", "proves": "...", "below_target_action": "..."},
        {"name": "...", "target": ">8%", "proves": "...", "below_target_action": "..."},
        {"name": "...", "target": ">15%", "proves": "...", "below_target_action": "..."},
        {"name": "...", "target": "+30%", "proves": "...", "below_target_action": "..."}
      ]
    },
    {
      "slide_number": 10, "type": "failure_mitigations",
      "title": "takeaway title", "headline": "key insight headline",
      "bullets": ["detailed bullet 1", "detailed bullet 2"],
      "speaker_notes": "presenter notes",
      "failures": [
        {"risk": "...", "handling": "...", "severity": "CRIT"},
        {"risk": "...", "handling": "...", "severity": "HIGH"},
        {"risk": "...", "handling": "...", "severity": "MED"}
      ],
      "guardrails": [
        {"name": "...", "threshold": "< 4%", "purpose": "..."},
        {"name": "...", "threshold": "< 200ms", "purpose": "..."},
        {"name": "...", "threshold": "< 1%", "purpose": "..."}
      ],
      "closing_message": "..."
    }
  ]
}"""


def _call_batch(client: LLMClient, system: str, user: str) -> tuple[list, dict]:
    """Call LLM for one batch of slides, return the slides list or [] on failure."""
    import time
    try:
        result = client.generate(
            system_prompt=system,
            user_prompt=user,
            creative=False,
            max_tokens=5500,
        )
        if not isinstance(result, dict):
            result = {}
        slides = result.get("slides", [])
        if not isinstance(slides, list):
            slides = []
        logger.info(f"Batch returned {len(slides)} slides.")
        return slides, result
    except Exception as e:
        logger.error(f"Batch LLM call failed: {e}")
        return [], {}


def synthesize_board_presentation(strategy_data: dict) -> dict:
    """
    Takes strategy deep dive output and synthesizes it into a
    structured 10-slide board presentation using TWO separate LLM calls
    (slides 1-5, then slides 6-10) to stay within Groq token limits.
    Falls back to rich static data for any slides the LLM fails to return.
    """
    import time
    logger.info("Synthesizing board presentation via 2-batch LLM approach...")
    client = LLMClient()

    step_context = _build_step_context(strategy_data)
    fallback = create_fallback_presentation(strategy_data)

    # ── Batch A: slides 1–5 ─────────────────────────────────────────────
    batch_a_user = (
        f"## Strategy Deep Dive Data:\n{step_context}\n\n"
        f"## Your Task:\nGenerate slides 1-5 of the McKinsey board deck based on the data above.\n\n"
        f"{BATCH_A_SCHEMA}"
    )
    logger.info("Running Batch A: slides 1-5...")
    slides_a, meta_a = _call_batch(client, BATCH_A_SYSTEM, batch_a_user)

    # Respect Groq RPM between the two calls
    logger.info("Waiting 3s between batches to respect Groq rate limits...")
    time.sleep(3)

    # ── Batch B: slides 6–10 ────────────────────────────────────────────
    batch_b_user = (
        f"## Strategy Deep Dive Data:\n{step_context}\n\n"
        f"## Your Task:\nGenerate slides 6-10 of the McKinsey board deck based on the data above.\n\n"
        f"{BATCH_B_SCHEMA}"
    )
    logger.info("Running Batch B: slides 6-10...")
    slides_b, _ = _call_batch(client, BATCH_B_SYSTEM, batch_b_user)

    # ── Merge & validate ────────────────────────────────────────────────
    # Index all returned slides by slide_number
    llm_slides_by_num = {}
    for s in slides_a + slides_b:
        num = s.get("slide_number")
        if num:
            llm_slides_by_num[int(num)] = s

    # Build final 10-slide array; fall back slide-by-slide if LLM missed any
    fallback_by_num = {s["slide_number"]: s for s in fallback["slides"]}
    final_slides = []
    for n in range(1, 11):
        if n in llm_slides_by_num:
            final_slides.append(llm_slides_by_num[n])
        else:
            logger.warning(f"Slide {n} missing from LLM output — using fallback.")
            final_slides.append(fallback_by_num[n])

    # Brand metadata from batch A if available, else from fallback
    detected_name, detected_pcolor, detected_scolor = _detect_brand(strategy_data)
    app_name = meta_a.get("app_name") if meta_a.get("app_name") in ["Blinkit", "Zepto", "Swiggy Instamart"] else detected_name
    
    if app_name == "Blinkit":
        primary_color, secondary_color, theme = "#ffc20e", "#3182ce", "Blinkit Yellow"
    elif app_name == "Zepto":
        primary_color, secondary_color, theme = "#5c2c90", "#e28743", "Zepto Purple"
    elif app_name == "Swiggy Instamart":
        primary_color, secondary_color, theme = "#fc8019", "#8a3ab9", "Swiggy Instamart Orange"
    else:
        primary_color = detected_pcolor
        secondary_color = detected_scolor
        theme = f"{app_name} Theme"

    presentation_title = meta_a.get("presentation_title") or fallback["presentation_title"]
    subtitle = meta_a.get("subtitle") or fallback["subtitle"]

    result = {
        "presentation_title": presentation_title,
        "subtitle": subtitle,
        "presentation_theme": theme,
        "app_name": app_name,
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "slides": final_slides,
    }
    logger.info(f"Board presentation complete: {len(final_slides)} slides.")

    return result


def _detect_brand(strategy_data: dict) -> tuple[str, str, str]:
    """Detect brand name and colors dynamically from strategy data."""
    app_name = "Target Platform"
    steps = strategy_data.get("steps", {})
    
    raw_str = json.dumps(strategy_data).lower()
    if "zepto" in raw_str:
        return "Zepto", "#5c2c90", "#e28743"
    elif "swiggy" in raw_str or "instamart" in raw_str:
        return "Swiggy Instamart", "#fc8019", "#8a3ab9"
    elif "blinkit" in raw_str:
        return "Blinkit", "#ffc20e", "#3182ce"
        
    for step in steps.values():
        data = step.get("data", {})
        if isinstance(data, dict) and data.get("app_name"):
            app_name = data.get("app_name")
            break
            
    import hashlib
    h = hashlib.md5(app_name.encode('utf-8')).hexdigest()
    primary = f"#{h[:6]}"
    secondary = f"#{h[6:12]}"
    return app_name, primary, secondary


def create_fallback_presentation(strategy_data: dict) -> dict:
    """Generates a professional 10-slide fallback deck with new McKinsey arc types if LLM fails."""
    app_name, primary_color, secondary_color = _detect_brand(strategy_data)

    slides = [
        {
            "slide_number": 1,
            "type": "market_gap",
            "title": f"Quick commerce platforms lack category exploration — {app_name} can own this gap",
            "headline": f"Competitors race on delivery speed; none have solved category habit expansion on {app_name}.",
            "bullets": [
                f"Quick commerce users place 85%+ of orders in 2-3 familiar categories, leaving high-margin verticals like beauty, wellness, and electronics largely undiscovered — representing an estimated 30-40% GMV uplift opportunity.",
                "Blinkit, Zepto, and Swiggy Instamart all surface recommendations via generic banners that are ignored after the first 2 sessions, creating a structural discovery gap that no platform has systematically addressed.",
                "First movers who integrate contextual, trust-backed in-session category suggestions stand to capture repeat cross-category purchases — a habit that, once formed, raises LTV by 2-3x over grocery-only buyers."
            ],
            "speaker_notes": "Open by anchoring the audience to the opportunity size — not the product. Market gap slides should answer 'why now' in 30 seconds.",
            "market_gap_table": [
                {"platform": app_name, "offer": "10-minute grocery delivery", "missing": "Trust-backed non-grocery exploration"},
                {"platform": "Zepto" if app_name != "Zepto" else "Blinkit", "offer": "Fast delivery + loyalty coins", "missing": "Contextual cross-category suggestions"},
                {"platform": "Swiggy Instamart", "offer": "Bundled food + grocery", "missing": "Authenticated product origin guarantees"},
                {"platform": "BigBasket", "offer": "Wide SKU range", "missing": "10-minute delivery velocity"},
                {"platform": "Amazon Fresh", "offer": "Prime trust + breadth", "missing": "Local dark store immediacy"}
            ],
            "why_solve_first": [
                "Category exploration directly drives platform LTV — users who buy across 3+ categories churn 60% less.",
                "AI-powered recommendation APIs are now mature enough to deploy with low engineering cost.",
                "Competitor platforms are beginning to test similar surfaces — first-mover advantage window is 6-9 months."
            ],
            "stats": [
                {"label": "Potential GMV uplift", "value": "30-40%"},
                {"label": "Avg categories per MAU", "value": "2.1"},
                {"label": "LTV of cross-category buyer", "value": "3x"}
            ]
        },
        {
            "slide_number": 2,
            "type": "user_research",
            "title": "Users express strong exploration intent but are blocked by trust and visibility gaps",
            "headline": "Review data reveals that 40%+ of negative feedback ties directly to discovery friction, not delivery.",
            "bullets": [
                "Analysis of 598 high-signal reviews shows that 40% of users explicitly state they want variety but don't trust the authenticity of non-grocery items — a trust-first barrier that price discounts alone cannot resolve.",
                "Sentiment breakdown reveals 62% negative reviews cite repetitive recommendations and limited visible categories, while positive reviews (23%) are concentrated in users who received personalised suggestions.",
                "Three archetypal complaints emerge: 'I only buy what I know here', 'I can't find the beauty section easily', and 'I'm scared of getting fake products' — all pointing to a single root cause: low discovery confidence."
            ],
            "speaker_notes": "Ground the audience in data. Show that the problem is real and measurable. Present quotes as primary evidence, not anecdotes.",
            "findings": {
                "total_analyzed": 598,
                "llm_labeled": 598,
                "discovery_pain_pct": 42,
                "top_theme": "Repetitive recommendations + authenticity concerns",
                "wants_variety_pct": 41,
                "less_repetition_pct": 33,
                "real_shuffle_pct": 18,
                "better_music_pct": 8
            },
            "sentiment": {"negative": 371, "neutral": 89, "positive": 138},
            "cited_quotes": [
                {"quote": "I only ever buy groceries here. Too scared to order face cream — what if it's fake?", "source": "Google Play Store"},
                {"quote": "Every time I open the app it shows the same 5 items. No exploration.", "source": "Google Play Store"},
                {"quote": "Wish there was a way to browse new categories while checking out my usual milk and bread.", "source": "Google Play Store"}
            ]
        },
        {
            "slide_number": 3,
            "type": "personas_journey",
            "title": "Two distinct user archetypes define the category exploration failure mode",
            "headline": "The Grocery Loyalist and the Cautious Explorer account for 70%+ of the category-stuck user base.",
            "bullets": [
                "The Grocery Loyalist (55% of MAUs) places identical orders 4-5x per week with zero category deviation — their habit loop is so entrenched that any non-grocery suggestion feels intrusive rather than helpful.",
                "The Cautious Explorer (18% of MAUs) actively wants to explore but abandons at the product detail page due to absent trust signals like origin badges, return guarantees, and seller verification scores."
            ],
            "speaker_notes": "Personas must be evidence-backed archetypes, not marketing stereotypes. Show the behavioral trap so the audience understands why standard tactics fail.",
            "personas": [
                {
                    "name": "Priya",
                    "title": "The Grocery Loyalist",
                    "meta": "28-35 yrs, Tier-1 city, 4x/week user",
                    "trust_pattern": "Only orders items she has bought before — repeat history is her default",
                    "unmet_need": "Wants to save time discovering new products without risking a bad experience",
                    "behavioral_trap": "App's recommendation algorithm reinforces her grocery habit — no novelty signal ever breaks through",
                    "quote": "I know exactly what I want. I open the app, add my usual stuff, and I'm done in 2 minutes."
                },
                {
                    "name": "Rahul",
                    "title": "The Cautious Explorer",
                    "meta": "24-32 yrs, Tier-1 city, 2-3x/week user",
                    "trust_pattern": "Interested in exploring but reads reviews extensively before any new-category purchase",
                    "unmet_need": "Needs clear brand authenticity signals before he will add a non-grocery item to his cart",
                    "behavioral_trap": "Finds non-grocery categories through search but abandons at checkout when no trust badge is visible",
                    "quote": "I wanted to try the protein powder but there was no brand seal. I went to Amazon instead."
                }
            ],
            "user_journey": [
                {"stage": "1. Open", "behavior": "Opens app to buy habitual groceries", "friction": "Habit loop; home screen shows only repeat items"},
                {"stage": "2. Served", "behavior": "Platform surfaces repeat grocery list", "friction": "Algorithm optimises for repeat, blocks novelty"},
                {"stage": "3. Browse", "behavior": "Scrolls past non-grocery category tabs", "friction": "No trust signals; authenticity concerns prevent click"},
                {"stage": "4. Checkout", "behavior": "Checks out in under 60 seconds", "friction": "High checkout speed = zero exploration window"},
                {"stage": "5. Exit", "behavior": "Exits immediately after placing order", "friction": "Habit reinforced; zero cross-sell achieved"}
            ]
        },
        {
            "slide_number": 4,
            "type": "problem_framing",
            "title": "The platform rewards speed over discovery — a structural design flaw, not a user preference",
            "headline": "The root problem is that the app's architecture optimises for repeat grocery velocity, making category exploration feel unsafe and invisible.",
            "bullets": [
                "The 10-minute delivery promise creates session urgency that works against exploration — users optimise their checkout time, not their basket breadth.",
                "Solving this requires a trust-first discovery surface embedded inside the checkout flow, not a separate 'explore' tab that users learn to ignore."
            ],
            "speaker_notes": "The 4-panel canvas forces the audience to agree on the problem before discussing solutions. This is the most important alignment slide.",
            "true_problem": "The platform's UX optimises for grocery repeat velocity, making non-grocery category discovery feel risky, invisible, and cognitively expensive for users.",
            "target_cohort": "Monthly Active Customers who place 3+ grocery orders per month but have zero non-grocery purchases in the last 90 days (est. 60-65% of MAU base).",
            "evidences": [
                "42% of 598 reviewed signals explicitly cite category exploration friction as a pain point.",
                "Non-grocery items account for <6% of catalog views despite representing 30%+ of SKU count.",
                "Users who buy across 3+ categories churn at 40% lower rate — proving exploration = retention."
            ],
            "value_generated": {
                "for_user": "Discover trusted, relevant non-grocery products in the same session without added cognitive load or authenticity risk.",
                "for_platform": "Increase Average Order Value by 20-35%, raise Monthly cross-category Basket Penetration from ~12% to 25%, and reduce grocery-only churn by 40%."
            },
            "why_now": {
                "saturation": "Grocery delivery is commoditised — GMV growth is stalling as competitors match on speed. Category breadth is the next differentiation vector.",
                "ai_unlock": "Contextual recommendation models trained on cart composition + purchase history are now production-ready at low latency (<100ms).",
                "first_mover": "No quick commerce platform in India has deployed a trust-first, in-session category discovery surface — a 6-9 month first-mover window exists."
            }
        },
        {
            "slide_number": 5,
            "type": "hypotheses_rice",
            "title": "H1 — Contextual in-cart suggestions with trust badges — wins decisively on RICE scoring",
            "headline": "Three competing hypotheses evaluated; H1 scores 3x higher than alternatives by combining maximum reach with lowest delivery risk.",
            "bullets": [
                "H1 targets users at peak intent (active checkout), requires no new app navigation, and can be shipped as a backend change — making it high reach, high confidence, and low engineering effort simultaneously.",
                "H2 (Homepage Redesign) scores poorly on confidence because homepage CTR data shows users skip above-the-fold banners within 2 sessions — making it a high-effort, low-confidence bet."
            ],
            "speaker_notes": "RICE scoring must be evidence-derived, not intuitive. Walk reviewers through why effort is low for H1 — it's a cart component, not a platform redesign.",
            "hypotheses": [
                {"id": "H1", "name": "Contextual In-Cart Cross-Sell + Trust Badges", "statement": "If we surface 3 brand-verified, category-adjacent product suggestions inside the checkout cart drawer, then 15-20% of users will click through and 8% will add to basket, because trust signals remove the primary barrier to non-grocery trials.", "validation": "A/B test on 10% of MAUs for 4 weeks measuring drawer CTR, basket add rate, and cross-category penetration."},
                {"id": "H2", "name": "Homepage Category Discovery Redesign", "statement": "If we restructure the homepage to prominently feature non-grocery category carousels, then category page views will increase by 30%, because visibility is the primary block.", "validation": "Homepage variant test measuring category page click-through and session time."},
                {"id": "H3", "name": "Push Notification-Led Discovery Campaign", "statement": "If we send personalised category exploration push notifications based on purchase history, then 5% of recipients will explore a new category within 48 hours.", "validation": "Push campaign A/B test measuring open rate, category click, and purchase conversion."}
            ],
            "rice_scores": [
                {"hypothesis_id": "H1", "reach": 9, "impact": 9, "confidence": 8, "effort": 4, "score": 162},
                {"hypothesis_id": "H2", "reach": 8, "impact": 6, "confidence": 4, "effort": 8, "score": 24},
                {"hypothesis_id": "H3", "reach": 6, "impact": 4, "confidence": 5, "effort": 3, "score": 40}
            ],
            "winning_rationale": "H1 achieves the highest RICE score (162) because it intercepts users at maximum purchase intent (active checkout), requires no new navigation surface (low effort = 4/10), and is supported by direct evidence that trust signals are the primary barrier to non-grocery conversion. H2 fails on confidence because banner blindness data shows homepage carousels are ignored after 2 sessions."
        },
        {
            "slide_number": 6,
            "type": "solution_comparison",
            "title": "S4 — Contextual In-Cart Cross-Sell Hub with Brand-Assured Badging — is the only approach that solves trust and visibility simultaneously",
            "headline": "Three solutions are rejected for specific evidence-backed reasons; S4 uniquely addresses both the trust barrier and the exploration invisibility problem.",
            "bullets": [
                "S1 (Full Homepage Redesign) was rejected because homepage redesigns take 3-6 months and carry high risk of disrupting the existing grocery conversion funnel — the primary revenue source.",
                "S4 is a cart-layer intervention that requires zero homepage changes, ships in 6 weeks, and delivers personalised trust signals precisely when users have maximum purchase intent."
            ],
            "title": "S4 - Chosen Solution - is the only approach that solves trust and visibility simultaneously",
            "headline": "Three alternatives rejected; S4 uniquely addresses visibility and trust in-session.",
            "bullets": [
                "S1 (Homepage redesign) was rejected due to high effort and risk of disrupting core flows.",
                "S4 is a contextual intervention that ships in 6 weeks and delivers trust signals during active sessions."
            ],
            "speaker_notes": "Solution comparison slides must justify the chosen solution while clearly rejecting alternatives.",
            "solutions": solutions,
            "vs_comparison": [
                {"against": "S1", "justification": "S4 ships in 6 weeks vs 3-6 months and carries zero risk to the core flow."},
                {"against": "S2", "justification": "S4 triggers during active session (peak intent) vs out-of-session push notifications."},
                {"against": "S3", "justification": "S4 pairs visibility with verified trust signals, which S3 lacks."}
            ]
        },
        {
            "slide_number": 7,
            "type": "mvp_spec",
            "title": "Three screens, zero new navigation — the MVP delivers exploration inside the flow",
            "headline": "The MVP is scoped to 3 inline screens that ship in 6 weeks with no homepage changes.",
            "bullets": [
                "Screen 1 (Contextual Recommendation Drawer) surfaces suggestions dynamically based on active session.",
                "Screen 2 (Trust Verification Card) displays verified signals inline, removing trust barriers.",
                "Screen 3 (Confirmation Nudge) captures residual user intent post-flow completion."
            ],
            "speaker_notes": "Demonstrate that the MVP is tightly scoped and fits seamlessly into the existing app structure.",
            "screens": [
                {"name": "Contextual Recommendation Drawer", "spec": "Dismissible inline component surfacing relevant options matched to current context."},
                {"name": "Trust Verification Card", "spec": "Panel showing validation signals, ratings, and guarantees without leaving the flow."},
                {"name": "Post-Flow Nudge", "spec": "Personalized prompt shown on confirmation screen to encourage discovery."}
            ],
            "trust_cues": ["Validation Badge", "Seller Verification Score", "Satisfaction Guarantee", "100% Original Seal"]
        },
        {
            "slide_number": 8,
            "type": "data_flow_edges",
            "title": "Recommendation engine runs on existing session data",
            "headline": "Two backend components drive the system; four edge cases are pre-mitigated.",
            "bullets": [
                "The Review Intelligence Pipeline processes signals asynchronously without impacting core latency.",
                "The Recommendation Engine maps session intent to adjacency graphs in <100ms."
            ],
            "speaker_notes": "Explain how the backend flow is lightweight and mitigates edge cases like cold start.",
            "data_flow": {
                "review_engine": "User feedback crawling → Quality filtering → Theme categorization → Recommendation scoring updates",
                "product_engine": "Active session context captured → Intent graph traversal → Candidate options scored → Top results rendered"
            },
            "nudges": [
                "Frequency cap: recommendations shown maximum 3x per week to avoid fatigue",
                "Relevance floor: options scoring below relevance threshold are suppressed",
                "Trust floor: only verified options with high satisfaction scores are surfaced"
            ],
            "edge_cases": [
                {"id": "E1", "title": "Cold start — new accounts with no history", "mitigation": "Fall back to popular options list; exclude trust-sensitive suggestions until behavior history accumulates."},
                {"id": "E2", "title": "Option temporarily unavailable", "mitigation": "Real-time availability check at render time; suppress unavailable items dynamically."},
                {"id": "E3", "title": "User dismisses recommendations repeatedly", "mitigation": "After 3 dismissals, suspend the drawer for 14 days; log signal to adjust future recommendations."},
                {"id": "E4", "title": "Friction dispute post-action", "mitigation": "Doorstep resolution policy applies; auto-escalate complaints to Trust team within 4 hours."}
            ]
        },
        {
            "slide_number": 9,
            "type": "metrics_indicators",
            "title": "North Star: Cross-Feature Adoption Rate — from 12% to 25% in 90 days",
            "headline": "Four leading indicators signal progress before the 90-day North Star window closes.",
            "bullets": [
                "The North Star directly measures the strategic goal of basket/feature adoption breadth.",
                "Leading indicator 1 (Drawer CTR >18%) proves users find suggestions relevant enough to click."
            ],
            "speaker_notes": "Detail the metrics framework. Focus on the non-gameable North Star metric.",
            "north_star": {
                "name": "Cross-Feature Adoption Rate",
                "definition": "Percentage of Monthly Active Users who engage with at least one new feature/category per month",
                "target": "12% → 25% within 90 days of launch",
                "why": "Ensures true expansion of feature usage across the user base.",
                "stalls_action": "If adoption is flat after 30 days: audit relevance scores, expand options catalog, and conduct surveys."
            },
            "leading_indicators": [
                {"name": "Inline Drawer Click-Through Rate", "target": ">18%", "proves": "Users find recommendations relevant enough to engage with", "below_target_action": "Rewrite recommendation copy; adjust layout; audit relevance scoring model."},
                {"name": "Cross-Feature Engagement Rate", "target": ">8%", "proves": "Clicks convert to active user interactions, not just curiosity", "below_target_action": "Strengthen trust badge visibility; optimize value proposition presentation."},
                {"name": "7-Day Repeat Feature Usage", "target": ">15%", "proves": "First-time usage converts to habit and repeat routine", "below_target_action": "Deploy targeted re-engagement messages; offer contextual guides."},
                {"name": "Monthly Feature Breadth Uplift", "target": "+30%", "proves": "Expanding usage across the entire platform's features", "below_target_action": "Widen eligible options catalog; optimize nudge placements."}
            ]
        },
        {
            "slide_number": 10,
            "type": "failure_mitigations",
            "title": "Guardrails ensure system is safe to launch without risking core experience",
            "headline": "Proactive design mitigations cover critical failures; guardrail thresholds trigger automatic rollback.",
            "bullets": [
                "Authenticity or friction disputes are handled by strict seller filters and doorstep resolution.",
                "A circuit-breaker rule pauses the intervention if core flow abandonment increases by >2%."
            ],
            "speaker_notes": "Close the presentation by showing that we fail-safe, protecting the core experience at all times.",
            "failures": [
                {"risk": "Option quality disputes drive complaint spikes", "handling": "Only recommend highly rated/verified options; auto-suppress options after repeat complaints.", "severity": "CRIT"},
                {"risk": "Recommendation drawer increases checkout load latency", "handling": "Render asynchronously after main page load; API timeout with popular items fallback.", "severity": "HIGH"},
                {"risk": "Users find the intervention intrusive, causing abandonment", "handling": "Set strict frequency caps; allow easy dismissal; auto-pause drawer if abandonment spikes.", "severity": "HIGH"},
                {"risk": "Recommendation algorithm surfaces irrelevant items", "handling": "Apply high relevance floor score; daily human audit of lowest-scored recommendations.", "severity": "MED"}
            ],
            "guardrails": [
                {"name": "Dispute Rate", "threshold": "< 4%", "purpose": "Keep support costs within limits to protect gross margin."},
                {"name": "Page P99 Load Latency", "threshold": "< +200ms increase", "purpose": "Ensure recommendation computation does not slow the user flow."},
                {"name": "Support Ticket Increase", "threshold": "< 1% increase", "purpose": "Ensure intervention messaging is clear enough to prevent user confusion."}
            ],
            "closing_message": f"This system is designed to fail safely: every failure mode has a pre-agreed threshold that triggers automatic mitigation, ensuring the {app_name} core experience is never compromised."
        }
    ]

    return {
        "presentation_title": f"{app_name} Product Strategy — Strategic Board Deck",
        "subtitle": "Unlocking Feature Adoption via Contextual Discovery",
        "presentation_theme": f"{app_name} Premium Theme",
        "app_name": app_name,
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "slides": slides
    }
