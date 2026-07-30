import json
from agents.base import BaseAgent

class ExecutivePresentationAgent(BaseAgent):
    def __init__(self):
        super().__init__("Executive Presentation Agent")

    def synthesize(self, solution_data: dict, root_cause_data: dict, discovery_data: dict) -> dict:
        """
        Synthesize analysis into a strict 10-slide executive board presentation JSON.
        """
        system_prompt = """
You are a McKinsey Engagement Manager and Executive Storytelling expert.
Synthesize the provided research data into exactly 10 presentation slides.

SLIDE OUTLINE:
1. Executive Summary
2. Problem Landscape
3. Evidence & Insights
4. Behavioral Analysis (only if supported)
5. Root Cause Prioritization
6. Competitive / White Space (only if justified)
7. Metrics Framework (only if measurable)
8. Prioritized Solutions
9. Strategic Recommendation
10. Executive Conclusion

CRITICAL RULES:
- Every slide must contain:
  1. "slide_number": int (1 to 10)
  2. "title": "Slide Title"
  3. "headline": "Key conclusion headline (must be an insight, not generic e.g. 'Dairy freshness issues drive 40% cart abandonment' instead of 'Problem Landscape')"
  4. "bullets": ["Bullet 1", "Bullet 2", "Bullet 3", "Bullet 4"] (3 to 5 bullets max)
  5. "recommendation": "One clear action"
  6. "key_metric": "One key metric" (where applicable)
- Determine the quick-commerce brand being analyzed (Blinkit / Zepto / Swiggy Instamart) from data and return brand details.

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
      "title": "Executive Summary",
      "headline": "...",
      "bullets": [],
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

Generate the 10-slide board presentation.
"""
        return self.generate_json(system_prompt, user_prompt)
