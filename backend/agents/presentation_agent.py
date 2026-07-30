import json
from agents.base import BaseAgent

class ExecutivePresentationAgent(BaseAgent):
    def __init__(self):
        super().__init__("Executive Presentation Agent")

    def synthesize(self, solution_data: dict, root_cause_data: dict, discovery_data: dict, problem_statement: str = None) -> dict:
        """
        Synthesize analysis into a strict 10-slide executive board presentation JSON.
        """
        system_prompt = """
You are a McKinsey Engagement Manager and Executive Storytelling expert.
Synthesize the provided research data into exactly 10 presentation slides.

SLIDE OUTLINE (Must generate exactly these 10 slides in order):
1. The Market Gap
2. Problem Statement
3. User Research & Evidence
4. Target Segment
5. Understanding the Breakdown
6. Proposed Solution
7. Product Prototype & Integration
8. Technical Implementation
9. Success Metrics
10. Risk Mitigation

CRITICAL SLIDE WRITING RULES:
1. TAKE-AWAY TITLES: The 'title' field of each slide MUST be a takeaway message (e.g. "Dairy Quality Risks Prevent 34% of Basket Explorations", not generic titles like "User Research & Evidence" or "Proposed Solution").
2. HIGH-DENSITY SELF-EXPLANATORY BULLETS: Bullet points in the 'bullets' array MUST be written as detailed, multi-sentence statements. Avoid short phrases. Each bullet point must explicitly link:
   - A core customer behavioral finding or friction point.
   - Direct quantitative metrics or qualitative quote evidence (e.g., "34% of users drop out at checkout because of hidden shipping fees").
   - The direct strategic implication or product recommendation.
3. Every slide must contain:
   - "slide_number": int (1 to 10)
   - "title": "Slide takeaway message"
   - "headline": "Key conclusion headline (must be an insight)"
   - "bullets": ["Detailed bullet 1", "Detailed bullet 2", "Detailed bullet 3"] (3 to 5 bullets max)
   - "recommendation": "One clear action"
   - "key_metric": "One key metric"
4. Determine the quick-commerce brand being analyzed (Blinkit / Zepto / Swiggy Instamart) from data and return brand details.
"""
        if problem_statement:
            system_prompt += f"\nFOCUS RULE: Your entire slide deck MUST target and solve this specific problem statement:\n{problem_statement}\n"

        system_prompt += """
Return strictly a JSON object with this schema:
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
      "title": "The Market Gap takeaway title",
      "headline": "...",
      "bullets": ["Multi-sentence finding with evidence and implication.", "Another dense bullet statement."],
      "recommendation": "...",
      "key_metric": "..."
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

        user_prompt += "\nGenerate the 10-slide board presentation.\n"
        return self.generate_json(system_prompt, user_prompt)
