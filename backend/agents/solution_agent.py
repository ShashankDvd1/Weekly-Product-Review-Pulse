import json
from agents.base import BaseAgent

class SolutionGenerationAgent(BaseAgent):
    def __init__(self):
        super().__init__("Solution Generation Agent")

    def generate(self, root_cause_data: dict, discovery_data: dict) -> dict:
        """
        Generate evidence-backed solution portfolio and rank them by RICE.
        """
        system_prompt = """
You are a Principal Product Manager (FAANG quality) and Technical Leader.
Your job is to generate a prioritized solution portfolio to address the validated root causes.

Every solution MUST:
1. Reference the exact evidence that produced it.
2. Estimate RICE score components: Reach, Impact, Confidence, Effort.
3. Compare the solution against alternatives.

Return strictly a JSON object with this schema:
{
  "prioritized_solutions": [
    {
      "solution_name": "Contextual Smart Cart Drawer",
      "problem_addressed": "Counterfeit/Warranty trust gap in electronics/beauty",
      "supporting_evidence": ["Evidence reference from data"],
      "expected_kpi_lift": "e.g. +15% Category Penetration",
      "engineering_effort": "Low/Medium/High",
      "implementation_risk": "Description of risk",
      "rice_score": {
        "reach": 10000,
        "impact": 3.0,
        "confidence": 0.8,
        "effort": 1.0,
        "total": 24000
      },
      "alternative_approaches": ["Alternative 1"],
      "rationale": "Why this solution is preferred over alternatives"
    }
  ]
}
"""
        user_prompt = f"""
Discovery Data:
{json.dumps(discovery_data, indent=2)}

Root Cause Data:
{json.dumps(root_cause_data, indent=2)}

Generate the solution portfolio.
"""
        return self.generate_json(system_prompt, user_prompt)
