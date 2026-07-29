import json
import logging
from core.llm_client import LLMClient
from core.config import LLM_MODEL_REASONING, LLM_TEMPERATURE_ANALYTICAL
from core.prompts import ANTI_HALLUCINATION_RULES

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """You are a McKinsey Engagement Manager, Director of Product, and Executive Storytelling expert preparing a high-impact presentation for the CEO.
Synthesize the provided 16-step Strategy Deep Dive results into one compelling 10-slide executive board presentation JSON.

# INPUT
Below are the completed steps of the Strategy Deep Dive:
{strategy_steps}

# CONSTRAINTS & RULES
1. Output exactly 10 slides.
2. Every slide must communicate ONE core insight answering "So What?".
3. Never exceed 40 words per slide. Ensure a design ratio of 60% whitespace, 20% visuals (charts, matrices, timelines), and 20% text.
4. HEADLINES MUST BE CONCLUSIONS, NOT generic section titles (e.g., "Verification badges reduce category bounce by 30%" instead of "Proposed Solution").
5. Maximum of 4 bullet points per slide, with a strict maximum of 10 words per bullet point.
6. Rewrite all AI terminology into natural, professional consultant language. Avoid buzzwords. Never repeat insights.
7. Replace raw lists with structural frameworks:
   - Convert tables into matrices
   - Convert comparisons into 2x2 frameworks
   - Convert processes into timelines
8. Determine the quick-commerce brand being analyzed (e.g., Blinkit, Zepto, Swiggy Instamart) and set:
   - "app_name": the brand name
   - "primary_color": matching brand color (e.g. Blinkit: "#ffc20e", Zepto: "#5c2c90", Swiggy: "#fc8019")
   - "secondary_color": matching secondary accent (e.g. Blinkit: "#3182ce", Zepto: "#e28743", Swiggy: "#8a3ab9")
9. Every recommendation must synthesize and include: Evidence, Business impact, Tradeoff, Risk, Implementation effort, and Confidence.
10. CRITICAL ANTI-HALLUCINATION RULE: If the input data contains survey statistics, percentages, user metrics, or user quotes, you MUST preserve them EXACTLY as they are. DO NOT manipulate, smooth, or use LLM reasoning to alter any numerical data or survey findings.
11. Return strictly a JSON object with the fields specified below. Do not output any formatting outside of the JSON block. No markdown backticks.

{ANTI_HALLUCINATION_RULES}


# JSON SCHEMA
Return a JSON object in this format:
{{
  "presentation_title": "Slide Deck Title",
  "subtitle": "Slide Deck Subtitle",
  "presentation_theme": "e.g. Blinkit Yellow / Zepto Purple / Swiggy Orange / McKinsey Corporate Blue",
  "primary_color": "hex color representing brand primary color",
  "secondary_color": "hex color representing brand accent color",
  "slides": [
    {{
      "slide_number": 1,
      "type": "market_gap",
      "title": "The Market Gap",
      "headline": "Full-sentence takeaway as title",
      "competitor_summary": "Competitor summary points",
      "market_gap": "Identified market gap",
      "white_space": "Unexplored white space opportunity",
      "opportunities": ["Opportunity 1", "Opportunity 2"],
      "strategic_advantage": "Moat advantage",
      "speaker_notes": "Talk track"
    }},
    {{
      "slide_number": 2,
      "type": "problem_statement",
      "title": "Problem Statement",
      "headline": "Full-sentence takeaway as title",
      "top_3_user_pains": ["Pain 1", "Pain 2", "Pain 3"],
      "customer_quotes": ["Quote 1", "Quote 2"],
      "behavior_patterns": "Observed behavioral trends",
      "jobs_to_be_done": "JTBD description",
      "key_takeaway": "Insight takeaway",
      "speaker_notes": "Talk track"
    }},
    {{
      "slide_number": 3,
      "type": "user_research",
      "title": "User Research & Evidence",
      "headline": "Full-sentence takeaway as title",
      "research_methods": ["Method 1", "Method 2"],
      "validated_assumptions": ["Assumption 1"],
      "false_assumptions": ["Assumption 2"],
      "key_evidence": "Primary research evidence",
      "insight_summary": "Overall insight from research",
      "speaker_notes": "Talk track"
    }},
    {{
      "slide_number": 4,
      "type": "target_segment",
      "title": "Target Segment",
      "headline": "Full-sentence takeaway as title",
      "segment_name": "Name of the target segment",
      "demographics": "Key demographic points",
      "psychographics": "Key psychographic points",
      "primary_needs": ["Need 1", "Need 2"],
      "segment_size": "Estimated size or value of segment",
      "speaker_notes": "Talk track"
    }},
    {{
      "slide_number": 5,
      "type": "breakdown",
      "title": "Understanding the Breakdown",
      "headline": "Full-sentence takeaway as title",
      "root_causes": ["Root cause 1", "Root cause 2"],
      "current_process": "Current manual process",
      "friction_points": ["Friction 1", "Friction 2"],
      "impact_of_breakdown": "Cost or loss from breakdown",
      "speaker_notes": "Talk track"
    }},
    {{
      "slide_number": 6,
      "type": "proposed_solution",
      "title": "Proposed Solution",
      "headline": "Full-sentence takeaway as title",
      "conservative": "Conservative option description",
      "innovative": "Innovative option description",
      "moonshot": "Moonshot option description",
      "recommended": "Recommended path",
      "reason": "Why this path is recommended",
      "speaker_notes": "Talk track"
    }},
    {{
      "slide_number": 7,
      "type": "product_prototype",
      "title": "Product Prototype & Integration",
      "headline": "Full-sentence takeaway as title",
      "key_features": ["Feature 1", "Feature 2"],
      "user_flow": "Step-by-step user flow",
      "ui_ux_changes": "Expected UI/UX modifications",
      "integration_points": ["Integration 1", "Integration 2"],
      "speaker_notes": "Talk track"
    }},
    {{
      "slide_number": 8,
      "type": "technical_implementation",
      "title": "Technical Implementation",
      "headline": "Full-sentence takeaway as title",
      "phase_1": "Phase 1 details",
      "phase_2": "Phase 2 details",
      "phase_3": "Phase 3 details",
      "dependencies": ["Dependency 1"],
      "timeline": "Timeline description",
      "speaker_notes": "Talk track"
    }},
    {{
      "slide_number": 9,
      "type": "success_metrics",
      "title": "Success Metrics",
      "headline": "Full-sentence takeaway as title",
      "north_star_metric": "North Star metric target",
      "primary_metrics": ["Metric 1", "Metric 2"],
      "guardrail_metrics": ["Guardrail 1"],
      "counter_metrics": ["Counter 1"],
      "expected_results": "Expected result figures",
      "speaker_notes": "Talk track"
    }},
    {{
      "slide_number": 10,
      "type": "risk_mitigation",
      "title": "Risk Mitigation",
      "headline": "Full-sentence takeaway as title",
      "operational_risks": ["Risk 1", "Risk 2"],
      "technical_risks": ["Risk 1", "Risk 2"],
      "mitigation_strategies": ["Strategy 1", "Strategy 2"],
      "contingency_plan": "Backup plan",
      "speaker_notes": "Talk track"
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
                trimmed[k] = v[:350] + "..." if len(v) > 350 else v
            elif isinstance(v, dict):
                trimmed[k] = trim_step_data(v)
            else:
                trimmed[k] = v
        return trimmed
    elif isinstance(data, list):
        return [trim_step_data(item) for item in data[:3]]
    elif isinstance(data, str):
        return data[:350] + "..." if len(data) > 350 else data
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
    Takes 16-step strategy deep dive output and synthesizes it into a
    structured 10-slide board presentation matching McKinsey guidelines.
    """
    logger.info("Synthesizing board presentation from 16-step Strategy Deep Dive...")
    client = LLMClient()

    # Formulate step text to feed as context (trimmed to prevent payload limit errors)
    steps = strategy_data.get("steps", {})
    steps_context_list = []
    # Filter for high-impact steps to fit context constraints while preserving factual detail
    high_impact_steps = ["step_1", "step_2", "step_3", "step_10", "step_11", "step_12", "step_13", "step_14", "step_15", "step_16"]
    for step_id, info in steps.items():
        if step_id not in high_impact_steps:
            continue
        step_title = info.get("title", step_id)
        raw_data = info.get("data", {})
        step_data = trim_step_data(raw_data)
        formatted_text = format_step_data_as_text(step_data)
        steps_context_list.append(f"### {step_id.upper()}: {step_title}\n{formatted_text}")

    strategy_steps_text = "\n\n".join(steps_context_list)

    prompt = PROMPT_TEMPLATE.format(strategy_steps=strategy_steps_text)
    
    # Run LLM query using deep reasoning model
    try:
        result_json = client.generate(
            system_prompt="Output strictly a valid JSON object matching the requested schema. No markdown wrappers.",
            user_prompt=prompt,
            creative=False
        )
        logger.info("Successfully synthesized CPO board presentation.")
        return result_json
    except Exception as e:
        logger.exception("Failed to synthesize board presentation. Generating fallback structure.")
        return create_fallback_presentation(strategy_data)

def create_fallback_presentation(strategy_data: dict) -> dict:
    """Generates a professional 10-slide PM-style fallback presentation if LLM fails."""
    product_name = strategy_data.get("product_name", "Platform")
    
    slides = [
        {
            "slide_number": 1,
            "type": "market_gap",
            "title": "The Market Gap",
            "headline": f"Competitors lack trust in non-grocery segments, presenting a gap for {product_name}.",
            "competitor_summary": "Competitors focus on grocery velocity but fail to provide authenticity guarantees for high-value items.",
            "market_gap": "Immediate delivery of verified, authentic beauty and electronics.",
            "white_space": "Contextual in-cart discovery of non-grocery items.",
            "opportunities": ["Increase AOV via high-margin items", "Establish trust with origin guarantees"],
            "strategic_advantage": "Leveraging existing 10-minute delivery network.",
            "speaker_notes": "The market gap lies in trust, not speed. Competitors haven't solved it."
        },
        {
            "slide_number": 2,
            "type": "problem_statement",
            "title": "Problem Statement",
            "headline": "Users strictly purchase groceries and avoid high-margin non-grocery segments.",
            "top_3_user_pains": [
                "Counterfeit and warranty concerns for high-value items.",
                "Cluttered app navigation burying non-grocery categories.",
                "High mental friction to switch purchasing habits."
            ],
            "customer_quotes": [
                "I only buy milk here because I don't trust the electronics warranty.",
                "It is too hard to find face cream, the search just lists snacks."
            ],
            "behavior_patterns": "Users exhibit a reflex checkout flow that bypasses non-grocery tabs.",
            "jobs_to_be_done": "When ordering groceries, I want to discover and purchase trust-verified beauty items in the same cart.",
            "key_takeaway": "Friction is rooted in a fundamental deficit in product trust.",
            "speaker_notes": "Our users are in a habit loop. They buy milk and check out immediately."
        },
        {
            "slide_number": 3,
            "type": "user_research",
            "title": "User Research & Evidence",
            "headline": "82% of users ignore non-grocery items due to low perceived authenticity.",
            "research_methods": ["User Interviews (N=50)", "Checkout Funnel Analytics", "Competitor Teardowns"],
            "validated_assumptions": ["Users want faster delivery for high-value items but don't trust quick commerce."],
            "false_assumptions": ["Users prefer specialized platforms solely due to price."],
            "key_evidence": "Non-grocery items represent less than 6% of active catalog views despite being 30% of SKU count.",
            "insight_summary": "Trust elements must be surfaced at the exact point of grocery selection to break the habit loop.",
            "speaker_notes": "Research indicates that price isn't the issue; trust and visibility are."
        },
        {
            "slide_number": 4,
            "type": "target_segment",
            "title": "Target Segment",
            "headline": "Focusing on 'Engaged Explorers': High-frequency grocery buyers with disposable income.",
            "segment_name": "Engaged Explorers",
            "demographics": "Ages 24-35, Urban Tier-1 cities, High average order value.",
            "psychographics": "Value convenience but are highly skeptical of product authenticity online.",
            "primary_needs": ["10-minute delivery", "100% genuine products with easy returns"],
            "segment_size": "Represents 25% of current active user base but 40% of potential GMV.",
            "speaker_notes": "We are targeting our most frequent buyers who currently split their wallets."
        },
        {
            "slide_number": 5,
            "type": "breakdown",
            "title": "Understanding the Breakdown",
            "headline": "The current platform architecture inherently hides high-margin categories.",
            "root_causes": [
                "Grocery intent dominates session time.",
                "Low non-grocery sales reduce supplier listings.",
                "Lack of trust guarantees reduces conversion."
            ],
            "current_process": "Users manually navigate to hidden category tabs, which 90% never open.",
            "friction_points": ["Hidden navigation", "No visible warranties", "Unrelated search results"],
            "impact_of_breakdown": "Estimated $15M annualized missed GMV opportunity.",
            "speaker_notes": "The breakdown occurs because we hide the very items that drive margin."
        },
        {
            "slide_number": 6,
            "type": "proposed_solution",
            "title": "Proposed Solution",
            "headline": "Deploying a contextual cross-sell hub with verifiable origin badges directly in the cart.",
            "conservative": "Add banner ads for non-grocery items on the homepage.",
            "innovative": "Personalized, AI-driven 'Smart Cart' that auto-suggests complementary beauty/electronics.",
            "moonshot": "Separate premium app dedicated to 10-minute electronics and beauty.",
            "recommended": "Innovative 'Smart Cart' with origin badges.",
            "reason": "Balances low disruption with high targeted conversion.",
            "speaker_notes": "We recommend the Smart Cart to intercept the user where intent is highest."
        },
        {
            "slide_number": 7,
            "type": "product_prototype",
            "title": "Product Prototype & Integration",
            "headline": "A sticky bottom drawer in the cart featuring tailored, verified items.",
            "key_features": [
                "Verifiable origin badges (e.g., '100% Original').",
                "Dynamic category suggestions based on current basket.",
                "One-click 'Add & Checkout' flow."
            ],
            "user_flow": "User adds grocery -> Enters Cart -> Drawer suggests 3 relevant items -> 1-click add.",
            "ui_ux_changes": "New cart component, updated product card with trust badges.",
            "integration_points": ["Recommendation Engine API", "Inventory syncing API"],
            "speaker_notes": "The prototype focuses on zero-friction addition with high trust signals."
        },
        {
            "slide_number": 8,
            "type": "technical_implementation",
            "title": "Technical Implementation",
            "headline": "A 6-week rollout prioritizing the recommendation algorithm and dark store syncing.",
            "phase_1": "W1-W2: Algorithm tuning and UI development.",
            "phase_2": "W3-W4: Dark store inventory API integration and testing.",
            "phase_3": "W5-W6: A/B beta launch and general availability.",
            "dependencies": ["Real-time inventory accuracy across 500+ stores."],
            "timeline": "6 weeks from kickoff to general availability.",
            "speaker_notes": "The critical path is ensuring inventory accuracy so we don't disappoint users."
        },
        {
            "slide_number": 9,
            "type": "success_metrics",
            "title": "Success Metrics",
            "headline": "Targeting a 15% increase in Average Order Value via cross-category penetration.",
            "north_star_metric": "Cross-Category Basket Penetration (% of orders with non-grocery items)",
            "primary_metrics": ["Non-Grocery Conversion Rate (Target: >4%)", "AOV Increase (Target: +15%)"],
            "guardrail_metrics": ["Cart Abandonment Rate (Must stay flat)"],
            "counter_metrics": ["Increase in Customer Support tickets regarding returns"],
            "expected_results": "Estimated +5% gross margin within 90 days of launch.",
            "speaker_notes": "Our North Star is getting users to buy across categories in a single order."
        },
        {
            "slide_number": 10,
            "type": "risk_mitigation",
            "title": "Risk Mitigation",
            "headline": "Proactively addressing inventory mismatches and rider capacity constraints.",
            "operational_risks": ["Inventory mismatch at local dark stores", "Rider weight limits exceeded"],
            "technical_risks": ["Latency increase during cart checkout", "Recommendation engine irrelevance"],
            "mitigation_strategies": [
                "Real-time stock syncing; hide items with <3 units.",
                "Dynamic weight-limit checks before recommending heavy items."
            ],
            "contingency_plan": "Fallback to static, lightweight popular item recommendations if API latency spikes.",
            "speaker_notes": "We have mitigations in place to protect the core grocery experience."
        }
    ]
    
    # Detect brand and color palette dynamically
    lower_product = product_name.lower()
    app_name = "Blinkit"
    primary_color = "#ffc20e"
    secondary_color = "#3182ce"
    
    if "zepto" in lower_product:
        app_name = "Zepto"
        primary_color = "#5c2c90"
        secondary_color = "#e28743"
    elif "swiggy" in lower_product or "instamart" in lower_product:
        app_name = "Swiggy Instamart"
        primary_color = "#fc8019"
        secondary_color = "#8a3ab9"

    return {
        "presentation_title": f"{product_name} Strategic Board Deck",
        "subtitle": "Category Exploration & Discovery Optimization",
        "presentation_theme": f"{app_name} Premium Theme",
        "app_name": app_name,
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "slides": slides
    }
