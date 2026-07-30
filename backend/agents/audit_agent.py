import json
from agents.base import BaseAgent

class ResearchAuditAgent(BaseAgent):
    def __init__(self):
        super().__init__("Research Audit Agent")

    def audit(
        self, 
        planning_data: dict,
        processing_data: dict,
        discovery_data: dict,
        segmentation_data: dict,
        root_cause_data: dict,
        solution_data: dict,
        presentation_data: dict,
        traceability_data: dict,
        problem_statement: str = None
    ) -> dict:
        """
        Audit the entire pipeline output, checking for logic consistency, unsupported claims, and slide guidelines.
        """
        system_prompt = """
You are an independent Research Audit Director. 
Your job is to verify all claims, ensure logical traceability, check correlation vs causation errors, and evaluate slide quality.

VERDICT GUIDELINES:
- "PASS": Everything is highly traceable, consistent, and strictly aligned with the target problem statement.
- "PASS WITH WARNINGS": Minor suggestions or weak evidence clusters exist but logic holds.
- "REQUIRES REVISION": Logical inconsistencies, slide outline mismatches (not exactly 10 slides following the McKinsey standard arc), unsupported claims, or misalignment with the target problem statement.
- "FAIL": Serious hallucinations, missing core deliverables, or no data traceability.
"""
        if problem_statement:
            system_prompt += f"\nFOCUS RULE: Verify that all slides, solutions, segments, and root causes target the research goals in the problem statement:\n{problem_statement}\nIf the presentation deviates to generic complaints (like support/refunds) instead of addressing the target problem, return verdict='REQUIRES REVISION'.\n"

        system_prompt += """
Return strictly a JSON object with this schema:
{
  "verdict": "PASS / PASS WITH WARNINGS / REQUIRES REVISION / FAIL",
  "audit_labels": {
    "slides_outline": "Verified / Unsupported",
    "data_traceability": "Verified / Partially Verified / Weak Evidence / Unsupported",
    "correlation_causation_check": "Verified / Weak Evidence",
    "logical_consistency": "Verified / REQUIRES REVISION"
  },
  "warnings": ["Warning 1"],
  "required_revisions": [
    {
      "component": "e.g. Solution Generation Agent",
      "issue": "Detailed explanation of what needs to be corrected"
    }
  ]
}
"""
        user_prompt = f"""
Compilation of Pipeline Data:
- Planning: {json.dumps(planning_data, indent=2)[:1000]}
- Processing: {json.dumps(processing_data, indent=2)[:1000]}
- Discovery: {json.dumps(discovery_data, indent=2)[:1000]}
- Segmentation: {json.dumps(segmentation_data, indent=2)[:1000]}
- Root Cause: {json.dumps(root_cause_data, indent=2)[:1000]}
- Solutions: {json.dumps(solution_data, indent=2)[:1000]}
- Presentation: {json.dumps(presentation_data, indent=2)[:2000]}
- Traceability: {json.dumps(traceability_data, indent=2)[:1000]}
"""
        if problem_statement:
            user_prompt += f"\nTarget Strategic Problem: {problem_statement}\n"

        user_prompt += "\nPerform the audit.\n"
        return self.generate_json(system_prompt, user_prompt)
