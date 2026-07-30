import json
from agents.base import BaseAgent
from core.schemas import UnifiedSignal

class ResearchPlanningAgent(BaseAgent):
    def __init__(self):
        super().__init__("Research Planning Agent")

    def plan(self, signals: list[UnifiedSignal]) -> dict:
        """
        Analyze the dataset properties and select frameworks to generate a research plan.
        """
        sample_size = min(len(signals), 10)
        samples = [
            f"[{s.source.value}|{s.app_name}] {s.content[:150]}" 
            for s in signals[:sample_size]
        ]
        
        system_prompt = """
You are a Principal PM and Strategy consultant. You specialize in evidence-driven data planning.
Your job is to inspect the dataset properties (total size, sources, sample content) and plan the research.

Framework Selection Rule:
Only select/use a framework if it uncovers new, evidence-backed insights based on the available data. 
Do not automatically generate frameworks (e.g. Personas, JTBD, SWOT, SWOT, etc.). If the evidence doesn't support them, skip them.
If multiple frameworks produce overlapping conclusions, keep only the one that provides the greatest analytical value.

Return strictly a JSON object with this schema:
{
  "dataset_types": ["e.g. App Store Reviews", "Reddit Posts", "User Surveys"],
  "quality_assessment": "Details of data quality, completeness, and potential bias",
  "selected_frameworks": ["List of frameworks from: Personas, JTBD, User Journey, 5 Whys, SWOT, Issue Tree, Metrics, Competitor Analysis, Behavioral Models"],
  "confidence_assessment": "High/Medium/Low based on volume and consistency of evidence"
}
"""
        
        user_prompt = f"""
Dataset Properties:
- Total Signal Count: {len(signals)}
- Sample Signals:
{json.dumps(samples, indent=2)}

Generate the Research Plan.
"""
        return self.generate_json(system_prompt, user_prompt)
