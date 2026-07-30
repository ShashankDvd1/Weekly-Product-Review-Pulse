import json
from agents.base import BaseAgent
from core.schemas import UnifiedSignal

class ResearchDiscoveryAgent(BaseAgent):
    def __init__(self):
        super().__init__("Research Discovery Agent")

    def discover(self, signals: list[UnifiedSignal]) -> dict:
        """
        Extract patterns, anomalies, and customer quotes from the dataset without proposing solutions.
        """
        # Compress signals to fit context limits (prioritize high-signal/low-score or diverse ones)
        sample_signals = []
        for s in signals[:60]:
            sample_signals.append({
                "source": s.source.value,
                "app": s.app_name,
                "rating": s.rating,
                "content": s.content
            })
            
        system_prompt = """
You are an expert UX Researcher and Behavioral Analyst. 
Analyze the provided customer signals to discover patterns, anomalies, and contradictions.

CRITICAL RULES:
1. Ground every pattern, quote, or hypothesis strictly in the provided data.
2. DO NOT propose any product solutions, features, or roadmap items.
3. Identify contradictions where they exist (e.g. users state one preference but show a different behavior).

Return strictly a JSON object with this schema:
{
  "observed_patterns": ["Pattern 1", "Pattern 2"],
  "anomalies": ["Anomaly 1"],
  "representative_quotes": [
    {"quote": "Actual user quote from content", "source": "App Store/Reddit/Survey"}
  ],
  "contradictions": ["Contradicting behavior or signal"],
  "hypotheses": [
    {
      "hypothesis": "Causal hypothesis",
      "evidence": "Supporting text or signal reference",
      "confidence": "High/Medium/Low"
    }
  ]
}
"""
        user_prompt = f"""
Raw Dataset (Sample):
{json.dumps(sample_signals, indent=2)}

Perform the discovery.
"""
        return self.generate_json(system_prompt, user_prompt)
