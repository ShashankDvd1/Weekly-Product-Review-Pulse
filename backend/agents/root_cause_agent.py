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
4. PROBLEM STATEMENT DOMINANCE: Filter out and reject generic, unrelated complaints (such as standard delivery delays, generic app crashes, support refund disputes) unless they directly evidence the specific mechanism of friction for the active problem statement.
"""
        if problem_statement:
            system_prompt += f"""
FOCUS & PROBLEM STATEMENT DOMINANCE RULE:
Your entire root-cause analysis and validated root causes MUST be strictly aligned with this specific problem statement:
"{problem_statement}"
Every validated root cause MUST directly explain the underlying behavioral, psychological, UX, or cognitive friction preventing users from achieving the desired outcome of this problem statement.
Do NOT output generic logistics, delivery speed, or customer support issues if the problem statement is focused on feature workflows (such as Wishlist intent decay, sizing/fit uncertainty, discovery, decision paralysis, navigation friction).
"""

        system_prompt += """
Return strictly a JSON object with this schema:
{
  "validated_root_causes": [
    {
      "root_cause_id": "RC1",
      "cause_title": "Short descriptive title of root cause",
      "barrier_type": "ux_friction | decision_paralysis | fit_and_sizing | intent_decay | habit | trust | quality_concern | discovery | price_perception | selection | convenience | usability | logistics",
      "category": "Specific category or product workflow affected (e.g., 'Wishlist Management', 'Fit & Sizing', 'Checkout Intent')",
      "explanation": "Deep causal explanation tracing why this friction occurs",
      "supporting_evidence": ["Exact evidence quote or data point"],
      "alternative_explanations": ["Alternative explanation 1"],
      "business_impact": "Loss of conversion, cart abandonment, revenue leak, etc.",
      "customer_impact": "Decision fatigue, hesitation, loss of confidence, etc.",
      "impact_score": 8.5
    }
  ]
}
"""
        # Keep inputs compact to stay within payload limits
        disc_summary = {
            "patterns": discovery_data.get("observed_patterns", [])[:6],
            "hypotheses": discovery_data.get("hypotheses", [])[:4],
            "quotes": discovery_data.get("representative_quotes", [])[:4],
            "jtbd": discovery_data.get("jobs_to_be_done", [])[:3]
        }
        seg_summary = {
            "user_segments": segmentation_data.get("user_segments", [])[:4],
            "themes": segmentation_data.get("prioritized_themes", [])[:4]
        }

        user_prompt = f"""
Discovery Summary:
{json.dumps(disc_summary, indent=2)}

Segmentation Summary:
{json.dumps(seg_summary, indent=2)}
"""
        if problem_statement:
            user_prompt += f"\nTarget Strategic Problem: {problem_statement}\n"

        user_prompt += "\nPerform the root-cause analysis.\n"
        return self.generate_json(system_prompt, user_prompt)
