import json
from agents.base import BaseAgent
from core.schemas import UnifiedSignal

class DataProcessingAgent(BaseAgent):
    def __init__(self):
        super().__init__("Data Processing Agent")

    def process(self, signals: list[UnifiedSignal], problem_statement: str = None) -> dict:
        """
        Processes and normalizes dataset statistics, identifying missing fields or metadata.
        """
        missing_content_count = sum(1 for s in signals if not s.content)
        missing_rating_count = sum(1 for s in signals if s.rating is None)
        
        sources = {}
        apps = {}
        ratings = []
        for s in signals:
            sources[s.source.value] = sources.get(s.source.value, 0) + 1
            apps[s.app_name] = apps.get(s.app_name, 0) + 1
            if s.rating is not None:
                ratings.append(s.rating)
                
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        quality_report = {
            "total_signals": len(signals),
            "missing_content": missing_content_count,
            "missing_ratings": missing_rating_count,
            "source_distribution": sources,
            "app_distribution": apps,
            "average_rating": round(avg_rating, 2)
        }
        
        system_prompt = """
You are a Lead Data Analyst. Review the data quality metrics and generate a structured data processing output.
Highlight any anomalies or gaps in data attributes (e.g. missing metadata, skewed score distributions).
"""
        if problem_statement:
            system_prompt += f"\nFOCUS RULE: Evaluate dataset cleanliness, anomalies, and bias specifically through the lens of investigating the problem statement:\n{problem_statement}\n"

        system_prompt += """
Return strictly a JSON object with this schema:
{
  "sanitized_stats": {
    "total_records": 100,
    "avg_quality_score": 4.2
  },
  "data_quality_report": "Summary of cleanliness, missing attributes, and integrity",
  "anomalies_detected": ["List of anomalies, e.g. empty reviews, rating mismatches"]
}
"""
        
        user_prompt = f"""
Data Quality Metrics:
{json.dumps(quality_report, indent=2)}
"""
        if problem_statement:
            user_prompt += f"\nTarget Strategic Problem: {problem_statement}\n"

        user_prompt += "\nGenerate the Data Processing & Quality Report.\n"
        return self.generate_json(system_prompt, user_prompt)
