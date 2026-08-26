import json
from agents.base import BaseAgent

class PatternSegmentationAgent(BaseAgent):
    def __init__(self):
        super().__init__("Pattern & Segmentation Agent")

    def segment(self, discovery_data: dict, problem_statement: str = None) -> dict:
        """
        Cluster user behaviors and patterns into natural segments and prioritize themes.
        """
        system_prompt = """
You are a Lead Data Scientist and Consumer Insights expert. 
Your job is to cluster the observed patterns and user behaviors into distinct customer segments and prioritize the key themes.

CRITICAL RULES:
1. Do not use pre-defined PM templates (like generic persona names). Cluster users naturally based on the patterns.
2. PROBLEM STATEMENT DOMINANCE: Cluster behavioral cohorts around the specific problem statement workflows, motivations, and blockers. Ignore baseline operational noise.
"""
        if problem_statement:
            system_prompt += f"""
FOCUS & PROBLEM STATEMENT DOMINANCE RULE:
Your entire segmentation, theme prioritization, and growth opportunities extraction MUST be strictly aligned with this research problem statement:
"{problem_statement}"
Prioritize behavioral user segments, themes, and growth opportunities that are directly relevant to this specific problem (e.g. wishlist organization, sizing/fit confidence, intent decay, purchase activation).
"""

        system_prompt += """
Return strictly a JSON object with this schema:
{
  "user_segments": [
    {
      "segment_name": "Name of natural cluster",
      "defining_behaviors": ["Behavior 1", "Behavior 2"],
      "observed_needs": ["Need 1"],
      "estimated_size_pct": 30
    }
  ],
  "prioritized_themes": [
    {
      "theme_name": "Theme title",
      "evidence_strength": "High/Medium/Low",
      "supporting_facts": ["Fact 1"]
    }
  ],
  "growth_opportunities": [
    {
      "title": "Opportunity title",
      "description": "Opportunity description",
      "category": "Feature/UX/Content/Ops/Marketing",
      "impact": "high/medium/low",
      "effort": "high/medium/low",
      "confidence": 0.8,
      "recommended_experiment": "Experiment description"
    }
  ]
}
"""
        user_prompt = f"""
Discovery Data:
{json.dumps(discovery_data, indent=2)}
"""
        if problem_statement:
            user_prompt += f"\nTarget Strategic Problem: {problem_statement}\n"

        user_prompt += "\nGenerate the segmentation and prioritized themes.\n"
        return self.generate_json(system_prompt, user_prompt)
