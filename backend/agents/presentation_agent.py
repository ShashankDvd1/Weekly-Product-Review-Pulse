import json
from agents.base import BaseAgent

class ExecutivePresentationAgent(BaseAgent):
    def __init__(self):
        super().__init__("Executive Presentation Agent")

    def synthesize(self, solution_data: dict, root_cause_data: dict, discovery_data: dict, problem_statement: str = None) -> dict:
        """
        Synthesize analysis into a strict 10-slide executive board presentation JSON with rich, slide-specific layouts.
        """
        system_prompt = """
You are a McKinsey Engagement Manager and Executive Storytelling expert.
Synthesize the provided research data into exactly 10 presentation slides.

SLIDE OUTLINE (Must generate exactly these 10 slides in order, with these slide types):
1. type: "market_gap" (Market Gap & Problem)
2. type: "user_research" (User Research & Sentiment)
3. type: "personas_journey" (Segment Personas & User Journey)
4. type: "problem_framing" (Problem Framing Canvas)
5. type: "hypotheses_rice" (Hypotheses & RICE)
6. type: "solution_comparison" (Solution Comparison)
7. type: "mvp_spec" (MVP Prototype Spec)
8. type: "data_flow_edges" (System Data Flow & Edge Cases)
9. type: "metrics_indicators" (North Star & Leading Indicators)
10. type: "failure_mitigations" (Failure Modes & Mitigations)

CRITICAL WRITING RULES:
1. TAKE-AWAY TITLES: The 'title' field of each slide MUST be a takeaway message (e.g. "Dairy Quality Risks Prevent 34% of Basket Explorations", not generic titles like "User Research & Evidence" or "Proposed Solution").
2. HIGH-DENSITY SELF-EXPLANATORY BULLETS: Bullet points in the 'bullets' array MUST be written as detailed, multi-sentence statements. Avoid short phrases. Each bullet point must explicitly link:
   - A core customer behavioral finding or friction point.
   - Direct quantitative metrics or qualitative quote evidence (e.g., "34% of users drop out at checkout because of hidden shipping fees").
   - The direct strategic implication or product recommendation.
3. Every slide must contain:
   - "slide_number": int (1 to 10)
   - "type": "market_gap" | "user_research" | "personas_journey" | "problem_framing" | "hypotheses_rice" | "solution_comparison" | "mvp_spec" | "data_flow_edges" | "metrics_indicators" | "failure_mitigations"
   - "title": "Slide takeaway message"
   - "headline": "Key conclusion headline (must be an insight)"
   - "bullets": ["Detailed bullet 1", "Detailed bullet 2", "Detailed bullet 3"] (3 bullets max)
   - "speaker_notes": "McKinsey presentation speaker notes for the slide"

Determine the quick-commerce brand being analyzed (Blinkit / Zepto / Swiggy Instamart) from data and return brand details.
"""
        if problem_statement:
            system_prompt += f"\nFOCUS RULE: Your entire slide deck MUST target and solve this specific problem statement:\n{problem_statement}\n"

        system_prompt += """
Return strictly a JSON object with this exact schema:
{
  "presentation_title": "Platform Category Exploration Board Presentation",
  "subtitle": "Unlocking high-margin baskets",
  "presentation_theme": "Blinkit Yellow / Zepto Purple",
  "app_name": "Blinkit",
  "primary_color": "#ffc20e",
  "secondary_color": "#3182ce",
  "slides": [
    {
      "slide_number": 1,
      "type": "market_gap",
      "title": "...",
      "headline": "...",
      "bullets": [...],
      "speaker_notes": "...",
      "market_gap_table": [
        {"platform": "Blinkit", "offer": "...", "missing": "..."},
        {"platform": "Zepto", "offer": "...", "missing": "..."},
        {"platform": "Swiggy Instamart", "offer": "...", "missing": "..."},
        {"platform": "BigBasket", "offer": "...", "missing": "..."},
        {"platform": "Amazon Fresh", "offer": "...", "missing": "..."}
      ],
      "why_solve_first": ["Reason 1", "Reason 2", "Reason 3"],
      "stats": [
        {"label": "...", "value": "..."},
        {"label": "...", "value": "..."},
        {"label": "...", "value": "..."}
      ],
      "problem_statement": "...",
      "business_outcome": "...",
      "product_outcome": "..."
    },
    {
      "slide_number": 2,
      "type": "user_research",
      "title": "...",
      "headline": "...",
      "bullets": [...],
      "speaker_notes": "...",
      "findings": {
        "total_analyzed": 150,
        "llm_labeled": 150,
        "discovery_pain_pct": 20,
        "top_theme": "stale/repetitive",
        "wants_variety_pct": 40,
        "less_repetition_pct": 30,
        "real_shuffle_pct": 20,
        "better_music_pct": 10
      },
      "sentiment": {
        "negative": 60,
        "neutral": 30,
        "positive": 60
      },
      "cited_quotes": [
        {"quote": "...", "source": "Source 1"},
        {"quote": "...", "source": "Source 2"},
        {"quote": "...", "source": "Source 3"}
      ]
    },
    {
      "slide_number": 3,
      "type": "personas_journey",
      "title": "...",
      "headline": "...",
      "bullets": [...],
      "speaker_notes": "...",
      "why_segment": "...",
      "personas": [
        {"name": "...", "title": "The Grocery Loyalist", "meta": "...", "trust_pattern": "...", "unmet_need": "...", "behavioral_trap": "...", "quote": "..."},
        {"name": "...", "title": "The Care-Focused Buyer", "meta": "...", "trust_pattern": "...", "unmet_need": "...", "behavioral_trap": "...", "quote": "..."}
      ],
      "user_journey": [
        {"stage": "1. Open", "behavior": "Opens app to buy milk and eggs", "friction": "Habit loop; ignores home banners"},
        {"stage": "2. Served", "behavior": "Presented repeat list/history", "friction": "Algorithmic loops optimize for replay, not novelty"},
        {"stage": "3. Unfamiliar", "behavior": "Scrolls past beauty/personal care tabs", "friction": "No trust signals; worries about authenticity"},
        {"stage": "4. Checkout", "behavior": "Completes purchase in under 60 seconds", "friction": "High checkout speed makes category exploration zero"},
        {"stage": "5. Loop", "behavior": "Exits app immediately", "friction": "Zero cross-sell achieved"}
      ],
      "core_insight": "..."
    },
    {
      "slide_number": 4,
      "type": "problem_framing",
      "title": "...",
      "headline": "...",
      "bullets": [...],
      "speaker_notes": "...",
      "true_problem": "...",
      "target_cohort": "...",
      "evidences": ["...", "...", "..."],
      "value_generated": {
        "for_user": "...",
        "for_platform": "..."
      },
      "why_now": {
        "saturation": "...",
        "ai_unlock": "...",
        "first_mover": "..."
      }
    },
    {
      "slide_number": 5,
      "type": "hypotheses_rice",
      "title": "...",
      "headline": "...",
      "bullets": [...],
      "speaker_notes": "...",
      "hypotheses": [
        {"id": "H1", "name": "User hypothesis", "statement": "...", "validation": "..."},
        {"id": "H2", "name": "Business hypothesis", "statement": "...", "validation": "..."},
        {"id": "H3", "name": "Market hypothesis", "statement": "...", "validation": "..."}
      ],
      "rice_scores": [
        {"hypothesis_id": "H1", "reach": 10, "impact": 9, "confidence": 8, "effort": 7, "score": 116},
        {"hypothesis_id": "H2", "reach": 5, "impact": 6, "confidence": 6, "effort": 5, "score": 60},
        {"hypothesis_id": "H3", "reach": 6, "impact": 3, "confidence": 4, "effort": 6, "score": 7}
      ],
      "winning_rationale": "..."
    },
    {
      "slide_number": 6,
      "type": "solution_comparison",
      "title": "...",
      "headline": "...",
      "bullets": [...],
      "speaker_notes": "...",
      "solutions": [
        {"id": "S1", "name": "Full Homepage Redesign", "status": "REJECTED", "description": "...", "feedback": "..."},
        {"id": "S2", "name": "Push Notifications Only", "status": "REJECTED", "description": "...", "feedback": "..."},
        {"id": "S3", "name": "Category Badges without Guarantee", "status": "REJECTED", "description": "...", "feedback": "..."},
        {"id": "S4", "name": "Contextual In-Cart cross-sell with Brand Assured badging", "status": "CHOSEN", "description": "...", "components": ["...", "..."]}
      ],
      "vs_comparison": [
        {"against": "S1", "justification": "..."},
        {"against": "S2", "justification": "..."},
        {"against": "S3", "justification": "..."}
      ]
    },
    {
      "slide_number": 7,
      "type": "mvp_spec",
      "title": "...",
      "headline": "...",
      "bullets": [...],
      "speaker_notes": "...",
      "screens": [
        {"name": "Home Ingress", "spec": "Sticky banner alerting users of category explore incentives"},
        {"name": "In-Cart Recommendation Drawer", "spec": "Top 3 high-margin items tailored to cart contents (e.g. skin cream when ordering oats)"},
        {"name": "Checkout Trust Seal", "spec": "Doorstep return policy display with Brand Authenticity badge"}
      ],
      "trust_cues": ["...", "..."],
      "live_links": ["https://spotify-discovery-engine-bsjjhdrynge2awgw7ubgci.streamlit.app/"]
    },
    {
      "slide_number": 8,
      "type": "data_flow_edges",
      "title": "...",
      "headline": "...",
      "bullets": [...],
      "speaker_notes": "...",
      "data_flow": {
        "review_engine": "Crawls play store reviews -> Filters authentic complaints -> Groups category barriers",
        "product_engine": "Maps user cart -> Generates contextual category recommendations -> Renders assurance badges"
      },
      "nudges": ["...", "..."],
      "grounding_mapping": [
        {"component": "Grounded story", "reason": "..."},
        {"component": "Trust layer", "reason": "..."},
        {"component": "Novelty filter", "reason": "..."}
      ],
      "edge_cases": [
        {"id": "E1", "title": "Cold start for new accounts", "mitigation": "..."},
        {"id": "E2", "title": "Stock out at local dark store", "mitigation": "..."},
        {"id": "E3", "title": "Overburdened delivery riders", "mitigation": "..."},
        {"id": "E4", "title": "Authenticity disputes", "mitigation": "..."}
      ]
    },
    {
      "slide_number": 9,
      "type": "metrics_indicators",
      "title": "...",
      "headline": "...",
      "bullets": [...],
      "speaker_notes": "...",
      "north_star": {
        "name": "Cross-Category Basket Penetration Rate",
        "definition": "Percentage of monthly active customers who place at least one order containing items from a newly explored category",
        "target": "Increase from 12% to 25%",
        "why": "...",
        "stalls_action": "..."
      },
      "leading_indicators": [
        {"name": "Recommendation drawer click-through rate", "target": "> 18%", "proves": "High initial interest in recommendation drawer", "below_target_action": "Rewrite AI recommendation copy"},
        {"name": "Cross-category trial rate", "target": "> 8%", "proves": "Conversion of recommendations into purchases", "below_target_action": "Enforce stronger brand assurance badges"},
        {"name": "7-day repeat purchase in new category", "target": "> 15%", "proves": "Real habit shift, not a one-off purchase", "below_target_action": "Target with custom coupons"},
        {"name": "Monthly category breadth uplift", "target": "+30%", "proves": "Wide adoption of non-grocery categories", "below_target_action": "Widen recommendation catalog selection"}
      ]
    },
    {
      "slide_number": 10,
      "type": "failure_mitigations",
      "title": "...",
      "headline": "...",
      "bullets": [...],
      "speaker_notes": "...",
      "failures": [
        {"risk": "Authenticity fears trigger high return rates", "handling": "Ship with doorstep opening and 100% money back seals", "severity": "CRIT"},
        {"risk": "Riders refuse heavy packages", "handling": "Enforce weight filters on recommended basket items", "severity": "HIGH"},
        {"risk": "Users find drawer intrusive", "handling": "Dismissible drawer with frequency capping rules", "severity": "LOW"}
      ],
      "guardrails": [
        {"name": "Doorstep return rate", "threshold": "< 4%", "purpose": "Keep shipping and courier cost within margin tolerances"},
        {"name": "App load latency", "threshold": "< 200ms increase", "purpose": "Ensure recommendation computation does not slow checkout"},
        {"name": "Unsolicited support tickets", "threshold": "< 1% increase", "purpose": "Ensure recommendation copy is clear and non-confusing"}
      ],
      "closing_message": "..."
    }
  ]
}
"""
        user_prompt = f"""
Discovery Data:
{json.dumps(discovery_data, indent=2)}

Root Cause Data:
{json.dumps(root_cause_data, indent=2)}

Solution Data:
{json.dumps(solution_data, indent=2)}
"""
        if problem_statement:
            user_prompt += f"\nTarget Strategic Problem: {problem_statement}\n"

        user_prompt += "\nGenerate the rich 10-slide board presentation JSON following the slide types and structured keys specified.\n"
        return self.generate_json(system_prompt, user_prompt)
