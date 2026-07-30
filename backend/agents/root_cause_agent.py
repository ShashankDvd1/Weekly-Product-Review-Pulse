import json
from agents.base import BaseAgent

class RootCauseStrategyAgent(BaseAgent):
    def __init__(self):
        super().__init__("Root Cause & Strategy Agent")

    def analyze(self, segmentation_data: dict, discovery_data: dict, problem_statement: str = None) -> dict:
        """
        Validate hypotheses and trace patterns to underlying root causes.
        """
        system_prompt = """
You are a Principal Product Strategy and root-cause analysis expert. 
Your job is to take the user segments, prioritized themes, and discovery hypotheses and perform a root-cause investigation.

CRITICAL RULES:
1. Never infer causation without direct evidence in the data.
2. Consider alternative explanations for every observed behavior.
3. Quantify the business and customer impact based on evidence.
"""
        if problem_statement:
            system_prompt += f"\nFOCUS RULE: Your entire root-cause analysis and validated root causes MUST be aligned with the following research problem statement/hypothesis:\n{problem_statement}\nPrioritize root causes and causal paths that directly explain behaviors or friction relevant to this strategic problem.\n"

        system_prompt += """
Return strictly a JSON object with this schema:
{
  "validated_root_causes": [
    {
      "root_cause_id": "RC1",
      "cause_title": "Short title of root cause",
      "explanation": "Causal explanation",
      "supporting_evidence": ["Evidence 1"],
      "alternative_explanations": ["Alternative explanation 1"],
      "business_impact": "Loss of LTV, cart bounce rates, etc.",
      "customer_impact": "Increased frustration, trust deficit, etc.",
      "impact_score": 8.5
    }
  ]
}
"""
        user_prompt = f"""
Discovery Data:
{json.dumps(discovery_data, indent=2)}

Segmentation Data:
{json.dumps(segmentation_data, indent=2)}
"""
        if problem_statement:
            user_prompt += f"\nTarget Strategic Problem: {problem_statement}\n"

        user_prompt += "\nPerform the root-cause analysis.\n"
        return self.generate_json(system_prompt, user_prompt)
