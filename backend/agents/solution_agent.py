import json
from agents.base import BaseAgent

class SolutionGenerationAgent(BaseAgent):
    def __init__(self):
        super().__init__("Solution Generation Agent")

    def generate(self, root_cause_data: dict, discovery_data: dict, problem_statement: str = None) -> dict:
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
"""
        if problem_statement:
            system_prompt += f"\nFOCUS RULE: Your entire solution generation MUST be aligned with the following research problem statement/hypothesis:\n{problem_statement}\nPrioritize generating strategic product features, experiments, or operational changes that solve this specific goal.\n"

        system_prompt += """
IMPORTANT CAUTION: The schema below contains mock solutions like 'Contextual Smart Cart Drawer' and 'Counterfeit/Warranty trust gap in electronics/beauty' as EXAMPLES ONLY. 
Do NOT copy or repeat these mock examples in your output unless they are explicitly validated by your root causes. Generate unique solutions that directly address the actual root causes provided in the user prompt.

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
"""
        if problem_statement:
            user_prompt += f"\nTarget Strategic Problem: {problem_statement}\n"

        user_prompt += "\nGenerate the solution portfolio.\n"
        return self.generate_json(system_prompt, user_prompt)
