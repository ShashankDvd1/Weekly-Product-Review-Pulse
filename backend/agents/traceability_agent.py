import json
from agents.base import BaseAgent

class EvidenceTraceabilityAgent(BaseAgent):
    def __init__(self):
        super().__init__("Evidence Traceability Agent")

    def trace(self, solution_data: dict, root_cause_data: dict, discovery_data: dict) -> dict:
        """
        Build the evidence traceability map linking solutions to root causes, patterns, and raw reviews.
        """
        system_prompt = """
You are an Evidence Auditor. Your job is to create a complete traceability map linking:
Recommendations -> Root Cause -> Pattern -> Raw Evidence / Quotes.
Any recommendation or slide without a clear parent pattern must be flagged as "UNTRACEABLE".

Return strictly a JSON object with this schema:
{
  "traceability_map": [
    {
      "solution": "Name of solution",
      "root_cause": "Linked root cause ID",
      "supporting_patterns": ["Pattern title"],
      "raw_evidence_source": "Support ticket/survey/review source",
      "status": "Verified / Untraceable"
    }
  ],
  "untraceable_items": []
}
"""
        user_prompt = f"""
Discovery Data:
{json.dumps(discovery_data, indent=2)}

Root Cause Data:
{json.dumps(root_cause_data, indent=2)}

Solution Data:
{json.dumps(solution_data, indent=2)}

Generate the evidence traceability map.
"""
        return self.generate_json(system_prompt, user_prompt)
