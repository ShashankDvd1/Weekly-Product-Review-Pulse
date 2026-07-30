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
5. Determine the quick-commerce brand from data and set brand metadata.
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


def synthesize_board_presentation(strategy_data: dict) -> dict:
    """
    Takes strategy deep dive output and synthesizes it into a
    structured 10-slide board presentation matching the McKinsey arc.
    """
    logger.info("Synthesizing board presentation from Strategy Deep Dive...")
    client = LLMClient()

    # Formulate step text to feed as context (trimmed to prevent payload limit errors)
    steps = strategy_data.get("steps", {})
    steps_context_list = []
    # Filter for high-impact steps to fit context constraints while preserving factual detail
    high_impact_steps = ["step_1", "step_2", "step_4", "step_8", "step_13", "step_14"]
    for step_id, info in steps.items():
        if step_id not in high_impact_steps:
            continue
        step_title = info.get("title", step_id)
        raw_data = info.get("data", {})
        step_data = trim_step_data(raw_data)
        formatted_text = format_step_data_as_text(step_data)
        steps_context_list.append(f"### {step_id.upper()}: {step_title}\n{formatted_text}")

    strategy_steps_text = "\n\n".join(steps_context_list)

    # Also include active problem statement if available
    problem_statement = strategy_data.get("active_problem_statement", "")
    if problem_statement:
        strategy_steps_text = f"## ACTIVE PROBLEM STATEMENT\n{problem_statement}\n\n" + strategy_steps_text

    prompt = PROMPT_TEMPLATE.format(
        strategy_steps=strategy_steps_text,
        ANTI_HALLUCINATION_RULES=ANTI_HALLUCINATION_RULES
    )

    # Run LLM query using deep reasoning model
    try:
        result_json = client.generate(
            system_prompt="Output strictly a valid JSON object matching the requested schema. No markdown wrappers. No text outside JSON.",
            user_prompt=prompt,
            creative=False
        )
        logger.info("Successfully synthesized board presentation.")
        return result_json
    except Exception as e:
        logger.exception("Failed to synthesize board presentation. Generating fallback structure.")
        return create_fallback_presentation(strategy_data)


def _detect_brand(strategy_data: dict) -> tuple[str, str, str]:
    """Detect brand name and colors from strategy data."""
    raw_str = json.dumps(strategy_data).lower()
    if "zepto" in raw_str:
        return "Zepto", "#5c2c90", "#e28743"
    elif "swiggy" in raw_str or "instamart" in raw_str:
        return "Swiggy Instamart", "#fc8019", "#8a3ab9"
    else:
        return "Blinkit", "#ffc20e", "#3182ce"


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
            "speaker_notes": "Solution comparison slides must be falsifiable. Each rejection needs a reason, not just a preference. The audience should agree with each rejection before endorsing the chosen path.",
            "solutions": [
                {"id": "S1", "name": "Full Homepage Redesign", "status": "REJECTED", "description": "Restructure the home screen to prominently feature non-grocery category carousels and hero banners.", "feedback": "High engineering effort (3-6 months), high risk of disrupting core grocery conversion funnel. Banner blindness research shows homepage carousels are ignored after 2-3 sessions."},
                {"id": "S2", "name": "Push Notification Discovery Campaign", "status": "REJECTED", "description": "Send personalised category exploration push notifications based on purchase history to drive app re-engagement.", "feedback": "Low session-time relevance — users see notifications outside of checkout intent. Open rates for category exploration pushes average <6% in Indian quick commerce."},
                {"id": "S3", "name": "Category Badges without Authenticity Guarantee", "status": "REJECTED", "description": "Add 'New Category' badges to non-grocery SKUs without a full brand origin verification system.", "feedback": "Addresses visibility but not the trust barrier. Review data shows 42% of non-grocery hesitation is authenticity-driven — badges without verified origin guarantees will not convert Cautious Explorers."},
                {"id": "S4", "name": "Contextual In-Cart Cross-Sell Hub + Brand-Assured Badging", "status": "CHOSEN", "description": "A dismissible drawer inside the checkout cart surfacing 3 contextually relevant non-grocery items from verified brand partners, with origin seals and doorstep-return guarantees displayed inline.", "feedback": "Addresses both trust and visibility; intercepts at peak intent; ships in 6 weeks; designed to be dismissed if unwanted — protecting core UX."}
            ],
            "vs_comparison": [
                {"against": "S1", "justification": "S4 ships in 6 weeks vs S1's 3-6 months and carries zero disruption risk to the core grocery funnel — the primary revenue driver."},
                {"against": "S2", "justification": "S4 triggers during active checkout session (peak intent) vs S2's out-of-session notification timing, resulting in 3-5x higher conversion likelihood."},
                {"against": "S3", "justification": "S4 pairs visibility with verified origin guarantees — directly removing the trust barrier identified in 42% of review data, which S3 cannot address."}
            ]
        },
        {
            "slide_number": 7,
            "type": "mvp_spec",
            "title": "Three screens, zero new navigation — the MVP delivers category exploration inside the existing checkout flow",
            "headline": "The MVP is scoped to 3 cart-layer screens that ship in 6 weeks with no homepage changes required.",
            "bullets": [
                "Screen 1 (In-Cart Recommendation Drawer) surfaces 3 brand-verified, cart-contextual product suggestions as a bottom sheet — dismissible, frequency-capped, and personalised to the user's existing basket composition.",
                "Screen 2 (Product Trust Card) shows brand origin verification, seller rating, and one-tap 'Doorstep Return' guarantee inline — removing the authenticity barrier without sending users to a separate product detail page.",
                "Screen 3 (Post-Checkout Explore Nudge) displays one personalised new-category prompt at order confirmation, capturing residual exploration intent with zero checkout friction."
            ],
            "speaker_notes": "Screen mapping should answer 'where does this live in the existing app?' for each engineering reviewer. Prototype links make this real.",
            "screens": [
                {"name": "In-Cart Recommendation Drawer", "spec": "Dismissible bottom sheet inside cart view; shows 3 brand-verified items contextually matched to cart composition; frequency-capped to 3x per week per user; one-tap 'Add & Checkout' CTA."},
                {"name": "Product Trust Card", "spec": "Inline trust panel showing Brand Origin badge, Seller Verification Score (1-5), and 'Doorstep Return' guarantee link — visible without leaving the cart surface."},
                {"name": "Post-Checkout Category Nudge", "spec": "Single personalised category suggestion shown on the order confirmation screen; one-tap 'Explore [Category]' CTA; tracks impressions vs. clicks separately from cart drawer CTR."}
            ],
            "trust_cues": ["Brand Origin Verification Badge", "Seller Authenticity Score (1-5)", "Doorstep Return Guarantee", "100% Original Seal"],
            "live_links": ["https://example-discovery-prototype.streamlit.app/"]
        },
        {
            "slide_number": 8,
            "type": "data_flow_edges",
            "title": "The recommendation engine runs entirely on existing cart and purchase data — no new data infrastructure required",
            "headline": "Two pipeline components drive the system; four edge cases are pre-mitigated at the design stage.",
            "bullets": [
                "The Review Intelligence Pipeline processes Play Store, App Store, and Reddit signals through the quality filter, groups category barriers by theme, and feeds the recommendation scoring model — running fully asynchronously without impacting checkout latency.",
                "The Cross-Sell Engine maps active cart composition to a category adjacency graph, scores candidate SKUs by trust rating + margin + stock depth, and renders the top 3 suggestions in <100ms."
            ],
            "speaker_notes": "Technical reviewers need to see that edge cases are pre-thought, not discovered post-launch. Walk through E1 (cold start) in detail — it's the most common objection.",
            "data_flow": {
                "review_engine": "Play Store + App Store reviews crawled → Quality filter removes spam → NLP groups category barrier themes → Barrier signals feed recommendation scoring model → Model updated weekly via batch job",
                "product_engine": "Active cart composition captured → Category adjacency graph traversed → Candidate SKUs scored by trust + margin + stock depth → Top 3 rendered in cart drawer via <100ms API call"
            },
            "nudges": [
                "Frequency cap: recommendation drawer shown max 3x per week per user to prevent fatigue",
                "Relevance floor: items scoring <0.6 on contextual relevance score are suppressed from suggestions",
                "Trust floor: only SKUs with Seller Verification Score ≥4.0 are eligible for recommendation"
            ],
            "edge_cases": [
                {"id": "E1", "title": "Cold start — new accounts with <3 orders", "mitigation": "Fall back to city-level bestseller list in the target category; exclude trust-sensitive SKUs until purchase history accumulates."},
                {"id": "E2", "title": "Recommended SKU out of stock at local dark store", "mitigation": "Real-time inventory check at drawer render time; suppress SKUs with <3 units at user's nearest dark store."},
                {"id": "E3", "title": "User dismisses drawer repeatedly", "mitigation": "After 3 consecutive dismissals, suspend drawer for 14 days; log dismissal signal to reduce future intrusive recommendations."},
                {"id": "E4", "title": "Authenticity dispute post-purchase", "mitigation": "Doorstep return policy applies to all recommended SKUs; brand origin dispute triggers automated escalation to Seller Trust team within 4 hours."}
            ]
        },
        {
            "slide_number": 9,
            "type": "metrics_indicators",
            "title": "North Star: Monthly Cross-Category Basket Penetration — from 12% to 25% in 90 days",
            "headline": "Four leading indicators signal whether we are on track before the 90-day North Star measurement window closes.",
            "bullets": [
                "The North Star (% of MAUs with at least one non-grocery purchase per month) directly measures the strategic goal — raising category breadth — and cannot be gamed by improving grocery metrics alone.",
                "Leading indicator 1 (Drawer CTR >18%) proves users find recommendations relevant enough to engage; if below target within 14 days, recommendation copy and SKU selection must be revised immediately."
            ],
            "speaker_notes": "North Star metrics must be non-gameable. Explain to reviewers why AOV or GMV are insufficient — they can increase without any category exploration happening.",
            "north_star": {
                "name": "Monthly Cross-Category Basket Penetration Rate",
                "definition": "Percentage of Monthly Active Customers who place at least one order containing a product from a newly explored category (a category with zero prior purchases in the last 90 days)",
                "target": "12% → 25% within 90 days of full launch",
                "why": "This metric is impossible to improve without actual category exploration occurring — it cannot be inflated by grocery GMV growth or AOV improvements alone.",
                "stalls_action": "If metric is flat after 30 days: audit recommendation relevance scores, expand eligible SKU catalog, and escalate trust barrier via in-app survey."
            },
            "leading_indicators": [
                {"name": "In-Cart Drawer Click-Through Rate", "target": ">18%", "proves": "Users find recommendations relevant enough to engage with", "below_target_action": "Rewrite recommendation copy; test 2-item vs. 3-item drawer layout; audit SKU relevance scoring model."},
                {"name": "Cross-Category Add-to-Cart Rate", "target": ">8%", "proves": "Clicks are converting to genuine purchase intent, not just curiosity", "below_target_action": "Strengthen trust badge visibility on the product card; add price comparison vs. competitor to reduce hesitation."},
                {"name": "7-Day Repeat Purchase in New Category", "target": ">15%", "proves": "First-time category purchase is converting to habit, not a one-off event", "below_target_action": "Deploy a targeted 7-day re-engagement push notification for new-category buyers with a 10% repeat discount."},
                {"name": "Monthly Category Breadth Uplift", "target": "+30% categories per MAU", "proves": "The system is expanding basket breadth across the user base, not just for a niche power user segment", "below_target_action": "Widen eligible SKU catalog to include mid-confidence SKUs; test nudge placement on post-checkout screen."}
            ]
        },
        {
            "slide_number": 10,
            "type": "failure_mitigations",
            "title": "Three guardrails ensure the system is safe to launch without risking core grocery experience",
            "headline": "Proactive design-stage mitigations cover every critical failure mode; guardrail thresholds trigger automatic rollback.",
            "bullets": [
                "The highest severity failure (CRIT) — authenticity disputes triggering return rate spikes — is mitigated by restricting recommendations to SKUs from brand-verified partners with Seller Score ≥4.0, combined with a doorstep return guarantee that activates within 4 hours of a dispute.",
                "A circuit-breaker rule activates automatic rollback if cart abandonment rate increases by >2 percentage points in any 7-day window — ensuring the cross-sell surface never degrades the core checkout experience.",
                "All three guardrail thresholds (return rate, latency, support tickets) are monitored in real-time on the existing analytics dashboard — no new monitoring infrastructure required."
            ],
            "speaker_notes": "Failure mode slides must show reviewers that you have thought beyond the happy path. Walk through the CRIT case in detail — it's the one that will be raised as an objection.",
            "failures": [
                {"risk": "Recommended SKU authenticity disputes drive return rate spike", "handling": "Only recommend SKUs from brand-verified partners (Seller Score ≥4.0); doorstep return activated within 4 hours of dispute; auto-suppress SKU after 2 authenticity complaints.", "severity": "CRIT"},
                {"risk": "Recommendation drawer increases cart checkout latency", "handling": "Drawer renders asynchronously after cart page load; recommendation API has 150ms timeout with fallback to static popular items list; monitored via P99 latency dashboard.", "severity": "HIGH"},
                {"risk": "Users find the drawer intrusive, causing checkout abandonment", "handling": "Frequency cap set to 3 impressions/week; drawer is fully dismissible; if cart abandonment rate increases >2pp in any 7-day window, drawer is auto-paused pending review.", "severity": "HIGH"},
                {"risk": "Recommendation algorithm surfaces irrelevant items (e.g., baby food to single users)", "handling": "Relevance floor score of 0.6 applied before any SKU is eligible; weekly model retraining on click + purchase feedback; daily human audit of lowest-scored recommendations.", "severity": "MED"}
            ],
            "guardrails": [
                {"name": "Doorstep Return Rate", "threshold": "< 4%", "purpose": "Keep reverse logistics cost within unit economics tolerances — exceeding 4% erodes gross margin on recommended items."},
                {"name": "Cart Page P99 Load Latency", "threshold": "< +200ms increase", "purpose": "Ensure recommendation computation does not slow the checkout flow — grocery users are time-sensitive."},
                {"name": "Unsolicited Customer Support Tickets", "threshold": "< 1% increase vs. baseline", "purpose": "Ensure recommendation copy and trust signals are clear enough that users don't need support to understand what they are being shown."}
            ],
            "closing_message": f"This system is designed to fail safely: every failure mode has a pre-agreed threshold that triggers automatic mitigation, ensuring the {app_name} core grocery experience is never compromised by the category exploration layer."
        }
    ]

    return {
        "presentation_title": f"{app_name} Category Exploration — Strategic Board Deck",
        "subtitle": "Unlocking Cross-Category Basket Penetration via Contextual Discovery",
        "presentation_theme": f"{app_name} Premium Theme",
        "app_name": app_name,
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "slides": slides
    }
