import json
from agents.base import BaseAgent
from core.schemas import UnifiedSignal

class ResearchDiscoveryAgent(BaseAgent):
    def __init__(self):
        super().__init__("Research Discovery Agent")

    def discover(self, signals: list[UnifiedSignal], problem_statement: str = None) -> dict:
        """
        Extract patterns, anomalies, and customer quotes from the dataset without proposing solutions.
        """
        # Select up to 60 high-relevance signals with concise content
        sample_signals = []
        for s in signals[:60]:
            clean_content = (s.content or "").strip()
            if len(clean_content) > 200:
                clean_content = clean_content[:200] + "..."
            sample_signals.append({
                "source": s.source.value,
                "app": s.app_name,
                "rating": s.rating,
                "content": clean_content
            })
            
        system_prompt = """
You are an expert UX Researcher and Behavioral Analyst. 
Analyze the provided customer signals to discover patterns, anomalies, and contradictions.

CRITICAL RULES:
1. Ground every pattern, quote, or hypothesis strictly in the provided data.
2. DO NOT propose any product solutions, features, or roadmap items.
3. Identify contradictions where they exist (e.g. users state one preference but show a different behavior).
4. Generate a minimum of 4 distinct and detailed causal hypotheses.
5. PROBLEM STATEMENT DOMINANCE: Discard generic platform complaints (e.g. baseline delivery delays, generic app crashes, support refund disputes) that do not directly illuminate the target problem statement.
"""
        if problem_statement:
            system_prompt += f"""
FOCUS & PROBLEM STATEMENT DOMINANCE RULE:
Your entire analysis and extraction MUST be strictly aligned with this research problem statement:
"{problem_statement}"
Prioritize finding observed patterns, anomalies, representative quotes, contradictions, causal hypotheses, and Jobs-To-Be-Done that directly shed light on user behaviors, friction points, and psychological/UX barriers related to this specific problem statement.
Ignore generic complaints that are unrelated to this problem statement.
"""

        system_prompt += """
Return strictly a JSON object with this schema:
{
  "observed_patterns": ["Pattern 1", "Pattern 2"],
  "anomalies": ["Anomaly 1"],
  "representative_quotes": [
    {"quote": "Actual user quote from content", "source": "App Store/Reddit/Survey"}
  ],
  "contradictions": ["Contradicting behavior or signal"],
  "hypotheses": [
    // Generate a minimum of 4 distinct and detailed hypotheses here
    {
      "hypothesis": "Causal hypothesis",
      "evidence": "Supporting text or signal reference",
      "confidence": "High/Medium/Low"
    }
  ],
  "jobs_to_be_done": [
    {
      "job_statement": "When [situation], I want to [motivation], so I can [outcome]",
      "category": "functional/emotional/social",
      "current_solution": "How users do it today",
      "gaps": ["Gap 1", "Gap 2"],
      "opportunity_score": 8.0,
      "supporting_quotes": ["Quote 1"]
    }
  ]
}
"""
        user_prompt = f"""
Raw Dataset (Sample):
{json.dumps(sample_signals, indent=2)}
"""
        if problem_statement:
            user_prompt += f"\nTarget Strategic Problem: {problem_statement}\n"

        user_prompt += "\nPerform the discovery.\n"
        return self.generate_json(system_prompt, user_prompt)
