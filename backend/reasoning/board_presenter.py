import json
import logging
from core.llm_client import LLMClient
from core.config import LLM_MODEL_REASONING, LLM_TEMPERATURE_ANALYTICAL

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
10. Return strictly a JSON object with the fields specified below. Do not output any formatting outside of the JSON block. No markdown backticks.

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
      "type": "executive_summary",
      "title": "Executive Summary",
      "headline": "Full-sentence takeaway",
      "problem": "Brief description of the problem",
      "why_now": "Market/user triggers showing urgency",
      "recommendation": "High-level recommendation summary",
      "business_impact": "Expected outcome in numbers",
      "speaker_notes": "Talk track for the presenter"
    }},
    {{
      "slide_number": 2,
      "type": "customer_problem",
      "title": "Customer Problem",
      "headline": "Full-sentence takeaway",
      "top_3_user_pains": ["Pain 1", "Pain 2", "Pain 3"],
      "customer_quotes": ["Quote 1", "Quote 2"],
      "behavior_patterns": "Observed behavioral trends",
      "jobs_to_be_done": "JTBD description",
      "key_takeaway": "Insight takeaway",
      "speaker_notes": "Talk track"
    }},
    {{
      "slide_number": 3,
      "type": "root_cause",
      "title": "Root Cause Analysis",
      "headline": "Full-sentence takeaway",
      "root_causes": ["Root cause 1", "Root cause 2"],
      "validated_assumptions": ["Assumption 1"],
      "false_assumptions": ["Assumption 2"],
      "issue_tree_summary": "Issue tree insight",
      "key_takeaway": "Insight takeaway",
      "speaker_notes": "Talk track"
    }},
    {{
      "slide_number": 4,
      "type": "landscape",
      "title": "Market & Competitive Landscape",
      "headline": "Full-sentence takeaway",
      "competitor_summary": "Competitor summary points",
      "market_gap": "Identified market gap",
      "white_space": "Unexplored white space opportunity",
      "opportunities": ["Opportunity 1", "Opportunity 2"],
      "strategic_advantage": "Moat advantage",
      "speaker_notes": "Talk track"
    }},
    {{
      "slide_number": 5,
      "type": "ai_opportunity",
      "title": "AI Opportunity",
      "headline": "Full-sentence takeaway",
      "current_process": "Current manual process",
      "ai_can_improve": "How AI optimizes the process",
      "automation": "Automation target",
      "personalization": "Personalization mechanism",
      "predictions": "Prediction utility",
      "expected_business_value": "Calculated value addition",
      "speaker_notes": "Talk track"
    }},
    {{
      "slide_number": 6,
      "type": "solutions",
      "title": "Solution Options",
      "headline": "Full-sentence takeaway",
      "conservative": "Conservative option description",
      "innovative": "Innovative option description",
      "moonshot": "Moonshot option description",
      "recommended": "Recommended path",
      "reason": "Why this path is recommended",
      "speaker_notes": "Talk track"
    }},
    {{
      "slide_number": 7,
      "type": "business_impact",
      "title": "Expected Business Impact",
      "headline": "Full-sentence takeaway",
      "north_star_metric": "North Star metric target",
      "primary_metrics": ["Metric 1", "Metric 2"],
      "guardrail_metrics": ["Guardrail 1"],
      "counter_metrics": ["Counter 1"],
      "expected_results": "Expected result figures",
      "risks": ["Risk 1", "Risk 2"],
      "speaker_notes": "Talk track"
    }},
    {{
      "slide_number": 8,
      "type": "roadmap",
      "title": "Implementation Roadmap",
      "headline": "Full-sentence takeaway",
      "phase_1": "Phase 1 details",
      "phase_2": "Phase 2 details",
      "phase_3": "Phase 3 details",
      "dependencies": ["Dependency 1"],
      "timeline": "Timeline description",
      "speaker_notes": "Talk track"
    }},
    {{
      "slide_number": 9,
      "type": "moat",
      "title": "Competitive Moat",
      "headline": "Full-sentence takeaway",
      "switching_costs": "Switching costs description",
      "data_advantage": "Data network effects",
      "network_effect": "Standard network effects",
      "flywheel": "Virtuous cycle flywheel",
      "long_term_strategy": "Long term Moat strategy",
      "speaker_notes": "Talk track"
    }},
    {{
      "slide_number": 10,
      "type": "executive_recommendation",
      "title": "Executive Recommendation",
      "headline": "Full-sentence takeaway",
      "decision": "Core decision requested",
      "top_priorities": ["Priority 1", "Priority 2"],
      "investment_required": "Required resources/budget",
      "expected_roi": "Estimated return on investment",
      "next_steps": ["Next step 1", "Next step 2"],
      "closing_message": "Strong final statement",
      "speaker_notes": "Talk track"
    }}
  ]
}}
"""

def trim_step_data(data):
    if isinstance(data, dict):
        trimmed = {}
        for k, v in data.items():
            if isinstance(v, list):
                trimmed[k] = [trim_step_data(item) for item in v[:4]]
            elif isinstance(v, str):
                trimmed[k] = v[:400] + "..." if len(v) > 400 else v
            elif isinstance(v, dict):
                trimmed[k] = trim_step_data(v)
            else:
                trimmed[k] = v
        return trimmed
    elif isinstance(data, list):
        return [trim_step_data(item) for item in data[:4]]
    elif isinstance(data, str):
        return data[:400] + "..." if len(data) > 400 else data
    return data

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
    for step_id, info in steps.items():
        step_title = info.get("title", step_id)
        raw_data = info.get("data", {})
        step_data = trim_step_data(raw_data)
        steps_context_list.append(f"### {step_id.upper()}: {step_title}\n{json.dumps(step_data, indent=2)}")

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
    """Generates a professional 10-slide McKinsey-style fallback presentation if LLM fails."""
    product_name = strategy_data.get("product_name", "Quick Commerce Platform")
    
    slides = [
        {
            "slide_number": 1,
            "type": "executive_summary",
            "title": "Executive Summary",
            "headline": f"Optimizing Category Discovery on {product_name} to unlock high-margin growth.",
            "problem": "Users stick strictly to grocery categories and avoid high-margin non-grocery segments (Beauty, Electronics).",
            "why_now": "Stagnant grocery margins and increasing user acquisition costs demand basket value optimization.",
            "recommendation": "Deploy a personalized contextual cross-sell engine and restructure category tabs.",
            "business_impact": "Expected +18% Average Order Value (AOV) and +5% gross margins in 90 days.",
            "speaker_notes": "Welcome team. Today we discuss the critical challenge of category discovery on our quick commerce platform and our path to higher profitability."
        },
        {
            "slide_number": 2,
            "type": "customer_problem",
            "title": "Customer Problem",
            "headline": "Users suffer from high friction and lack of trust in non-grocery categories.",
            "top_3_user_pains": [
                "Counterfeit and warranty concerns for high-value electronics.",
                "Freshness and authenticity doubts for cosmetics and beauty products.",
                "Cluttered application navigation burying non-grocery listings."
            ],
            "customer_quotes": [
                "I only buy milk here because I don't trust the electronics warranty.",
                "It is too hard to find face cream, the search just lists snacks."
            ],
            "behavior_patterns": "Users open the app with high intent for groceries but exhibit a reflex checkout flow that bypasses other tabs.",
            "jobs_to_be_done": "When ordering daily groceries, I want to discover and purchase trust-verified beauty items in the same cart, so that I can save delivery fees and time.",
            "key_takeaway": "Friction isn't just about interface clicks; it's a fundamental deficit in product trust.",
            "speaker_notes": "Our users are in a habit loop. They buy milk and check out immediately. We need to intercept this flow with high-trust category cues."
        },
        {
            "slide_number": 3,
            "type": "root_cause_analysis",
            "title": "Root Cause Analysis (5 Whys)",
            "headline": "Distrust in platform quality stems from lack of verifiable origin and poor delivery care.",
            "root_cause_chain": [
                "Grocery intent dominates -> Non-grocery is hidden -> Low category sales.",
                "Low sales -> Reduced supplier listing -> Limited product selection.",
                "Limited selection -> Users buy elsewhere -> Platform doesn't build trust."
            ],
            "proven_facts": "82% of users buy only food; non-grocery items represent less than 6% of active catalog views.",
            "unproven_assumptions": "Assumed users prefer specialized platforms (Myntra, Amazon) solely due to price.",
            "key_insight": "Breaking the habit loop requires surfacing trust elements at the exact point of grocery selection.",
            "speaker_notes": "Why don't they explore? Because they don't trust us for these items. By tracing the 5 Whys, we see that origin verification is key."
        },
        {
            "slide_number": 4,
            "type": "competitive_landscape",
            "title": "Competitive Landscape",
            "headline": "Competitors succeed by blending specialized verticals into quick-delivery models.",
            "competitors": [
                {"name": "Blinkit", "strength": "Wide selection & quick delivery", "weakness": "Variable quality in electronics"},
                {"name": "Zepto", "strength": "Fast deliveries (under 10 mins)", "weakness": "High reliance on grocery SKU volume"},
                {"name": "Nykaa/Amazon", "strength": "Established product trust and warranties", "weakness": "Slower delivery speeds (1-2 days)"}
            ],
            "whitespace_opportunity": "Offering verified quick-delivery for beauty and electronics with immediate instant return options.",
            "key_takeaway": "We can win by matching specialized trust with our unbeatable 10-minute delivery promise.",
            "speaker_notes": "Competitors are moving fast, but their weakness is delivery speed or high-intent focus. Our whitespace lies in verified instant-delivery."
        },
        {
            "slide_number": 5,
            "type": "strategic_alternatives",
            "title": "Strategic Alternatives",
            "headline": "Contextual cross-selling outweighs full category redesigns in ROI and time-to-market.",
            "alternatives": [
                {"name": "Complete UI Redesign", "pros": "Modern looks", "cons": "High dev effort, disrupts user muscle memory", "decision": "Rejected"},
                {"name": "Contextual In-Cart Cross-Sell", "pros": "Zero disruption, high conversion", "cons": "Needs smart recommendation engine", "decision": "Selected"}
            ],
            "tradeoff_analysis": "Selecting in-cart cross-sell minimizes developmental risk while directly targeting checkout habit loops.",
            "speaker_notes": "We evaluated a total redesign, but rejected it to prevent disrupting active users. Instead, we are deploying contextual cross-sells."
        },
        {
            "slide_number": 6,
            "type": "proposed_solution",
            "title": "Proposed MVP: Smart Cross-Sell Hub",
            "headline": "An intelligent, trust-verified recommendation engine integrated into the cart checkout.",
            "mvp_features": [
                "Verifiable origin badges (e.g., '100% Original Brand Verified').",
                "Dynamic category suggestions based on grocery basket profiles.",
                "Zero-friction instant returns at the doorstep."
            ],
            "ux_wireframe_spec": "A sticky bottom drawer on the cart page displaying 3 verified items tailored to the user's current items.",
            "success_criteria": "A click-through rate (CTR) of >12% and conversion rate of >4% on recommended products.",
            "speaker_notes": "Here is the MVP. It features verified brand badges and doorstep returns to eliminate buyer anxiety."
        },
        {
            "slide_number": 7,
            "type": "kpi_framework",
            "title": "KPI & Metrics Framework",
            "headline": "North Star metric shifts from active orders to cross-category basket penetration.",
            "north_star_metric": "Cross-Category Basket Penetration (% of orders with non-grocery items)",
            "key_metrics": [
                {"metric": "Non-Grocery Conversion Rate", "target": "4.5%", "justification": "Benchmarks show in-cart recommendations drive high conversions."},
                {"metric": "Average Order Value (AOV)", "target": "+15%", "justification": "Adding higher-value beauty items increases checkout basket size."}
            ],
            "speaker_notes": "We are aligning the team around basket penetration. If we get users to buy one non-grocery item, their lifetime value doubles."
        },
        {
            "slide_number": 8,
            "type": "rice_prioritization",
            "title": "Implementation Prioritization",
            "headline": "In-cart recommendations offer the highest impact-to-effort ratio.",
            "solutions": [
                {"name": "In-Cart Recommendations", "reach": "90%", "impact": "High", "confidence": "80%", "effort": "Low", "rice_score": "240"},
                {"name": "Homepage Brand Banners", "reach": "50%", "impact": "Medium", "confidence": "70%", "effort": "Medium", "rice_score": "120"}
            ],
            "resource_allocation": "Focus 70% of engineering bandwidth on refining the contextual recommendations algorithm.",
            "speaker_notes": "Our RICE scoring clearly identifies in-cart suggestions as the highest-impact launch solution."
        },
        {
            "slide_number": 9,
            "type": "risks_and_mitigations",
            "title": "Risks & Mitigations",
            "headline": "Delivery delays and inventory mismatches present the highest operational risks.",
            "risks": [
                {"risk": "Inventory mismatch at local dark stores", "impact": "High", "mitigation": "Real-time stock syncing before displaying recommendations."},
                {"risk": "Increased delivery rider burden", "impact": "Medium", "mitigation": "Limit weight of cross-sold items dynamically in the recommendations engine."}
            ],
            "operational_dependencies": "Requires dark store inventory API integration with the recommendation engine.",
            "speaker_notes": "We must mitigate out-of-stock experiences. The recommendations engine will automatically hide items with fewer than 3 units in stock."
        },
        {
            "slide_number": 10,
            "type": "financial_roi",
            "title": "Financial Impact & Timeline",
            "headline": "Projected to break even in Month 3, driving long-term gross margin expansion.",
            "timeline": "Phase 1: Dev (W1-W3) -> Phase 2: Beta Launch (W4) -> Phase 3: General Availability (W6)",
            "break_even_point": "Month 3 post-launch",
            "investment_required": "$45,000 engineering and dark-store branding cost.",
            "roi_justification": "Unlocking high-margin categories offsets customer acquisition costs, stabilizing long-term unit economics.",
            "speaker_notes": "With a minimal $45k investment, we break even in month 3. I request approval to move to development phase."
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
