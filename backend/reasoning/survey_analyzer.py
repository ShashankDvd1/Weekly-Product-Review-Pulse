import json
import logging
from typing import List, Dict, Any
from core.llm_client import get_llm_client

logger = logging.getLogger(__name__)

def analyze_survey_data(survey_data: List[Dict[str, Any]], phase_1_insights: dict) -> dict:
    """
    Takes the parsed CSV survey data and the Phase 1 strategy outputs.
    Uses LLM to synthesize a Validation Matrix identifying confirmed hypotheses,
    contradicted assumptions, and new insights.
    """
    llm = get_llm_client()
    
    # We want to compress phase_1_insights so it doesn't blow up context limit.
    # We just need the hypotheses, problem, and root causes.
    compressed_phase_1 = {}
    if "step_1" in phase_1_insights:
        compressed_phase_1["problem"] = phase_1_insights["step_1"].get("data", {})
    if "step_2" in phase_1_insights:
        compressed_phase_1["assumptions"] = phase_1_insights["step_2"].get("data", {})
    if "step_4" in phase_1_insights:
        compressed_phase_1["issue_tree"] = phase_1_insights["step_4"].get("data", {})
    if "step_8" in phase_1_insights:
        compressed_phase_1["root_causes"] = phase_1_insights["step_8"].get("data", {})
        
    compressed_phase1_str = json.dumps(compressed_phase_1, indent=2)
    survey_data_str = json.dumps(survey_data, indent=2)[:8000] # Cap it just in case
    
    prompt = f"""
You are a Principal PM and User Researcher. You have just completed a Phase 1 product discovery phase based on App Store Reviews.
You have now conducted a User Survey to validate your hypotheses. 

Phase 1 Strategy & Hypotheses:
{compressed_phase1_str}

User Survey Data (CSV Rows):
{survey_data_str}

Analyze the survey data against the Phase 1 insights. 
Generate a JSON output containing a Validation Matrix that maps each original hypothesis/assumption to its survey validation outcome.

Return ONLY a valid JSON object matching this schema:
{{
  "validation_matrix": [
    {{
      "original_insight": "The hypothesis or root cause from Phase 1",
      "survey_evidence": "What the survey actually says",
      "status": "Confirmed" | "Contradicted" | "New Insight",
      "implication": "How this changes our MVP strategy"
    }}
  ],
  "updated_problem_statement": "A refined problem statement incorporating survey reality",
  "survey_demographics": "Brief summary of the survey respondents",
  "key_takeaways": ["Takeaway 1", "Takeaway 2"]
}}
"""

    logger.info("Running Survey Validation against Phase 1 insights...")
    try:
        result = llm.generate_json(prompt)
        logger.info("Survey Validation completed successfully.")
        return result
    except Exception as e:
        logger.error(f"Failed to analyze survey data: {e}")
        return {
            "error": str(e),
            "validation_matrix": [],
            "updated_problem_statement": "Failed to generate.",
            "survey_demographics": "Unknown",
            "key_takeaways": []
        }
