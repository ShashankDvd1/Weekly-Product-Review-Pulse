import json
import logging
from core.llm_client import get_llm_client

logger = logging.getLogger(__name__)

def generate_mvp_workspace(strategy_deep_dive_results: dict) -> dict:
    """
    Synthesizes the complete 16-step Strategy Deep Dive (plus survey validation)
    into a structured Product Requirements Document / MVP Workspace.
    """
    llm = get_llm_client()
    
    # Compress the deep dive results to fit in context window
    compressed_results = {}
    for step_id, step_val in strategy_deep_dive_results.get("steps", {}).items():
        compressed_results[step_id] = step_val.get("data", {})
        
    if "survey_validation" in strategy_deep_dive_results:
        compressed_results["survey_validation"] = strategy_deep_dive_results["survey_validation"]

    context_str = json.dumps(compressed_results, indent=2)[:15000] # Cap to prevent overflow

    prompt = f"""
You are an elite Principal Product Manager and Technical Lead.
Based on the highly detailed Strategy Deep Dive and User Validation data provided,
synthesize a comprehensive, executive-ready "MVP Workspace / Product Requirements Document (PRD)".

STRATEGY DEEP DIVE DATA:
{context_str}

Analyze this data and produce a structured JSON object exactly matching the schema below.
Make sure the content is highly actionable, logically sound, and directly tied to the evidence from the data.

Return ONLY a valid JSON object matching this exact schema:
{{
  "problem_definition": {{
    "core_problem": "...",
    "root_causes": ["...", "..."],
    "target_user_segment": "..."
  }},
  "why_this_mvp": "Brief executive summary of why this specific solution was chosen (from Step 14/15/Survey).",
  "moscow_prioritization": {{
    "must_have": ["...", "..."],
    "should_have": ["...", "..."],
    "could_have": ["...", "..."],
    "wont_have": ["...", "..."]
  }},
  "feature_breakdown": [
    {{
      "feature_name": "...",
      "description": "...",
      "user_value": "..."
    }}
  ],
  "user_journey_mapping": [
    {{
      "step": "...",
      "user_action": "...",
      "system_response": "..."
    }}
  ],
  "wireframe_suggestions": [
    {{
      "screen_name": "...",
      "key_elements": ["...", "..."],
      "layout_guidance": "..."
    }}
  ],
  "experiment_design": {{
    "hypothesis": "...",
    "success_criteria": "...",
    "test_duration": "..."
  }},
  "kpi_dashboard": [
    {{
      "metric_name": "...",
      "type": "North Star | Input | Output | Guardrail",
      "target": "..."
    }}
  ],
  "risk_assessment": [
    {{
      "risk": "...",
      "mitigation_strategy": "..."
    }}
  ],
  "launch_roadmap": [
    {{
      "phase": "...",
      "milestone": "..."
    }}
  ],
  "final_recommendation": "Go / No-Go decision with brief rationale."
}}
"""

    logger.info("Generating MVP Workspace PRD...")
    try:
        result = llm.generate("You are an elite Principal Product Manager and Technical Lead.", prompt)
        logger.info("MVP Workspace generated successfully.")
        return result
    except Exception as e:
        logger.error(f"Failed to generate MVP Workspace: {e}")
        return {"error": str(e)}
