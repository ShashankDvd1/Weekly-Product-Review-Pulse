import json
import logging
from typing import Optional
from core.llm_client import get_llm_client
from core.schemas import BoardEvaluation, VivaQuestion, VivaAnswerEvaluation

logger = logging.getLogger(__name__)

BOARD_SYSTEM_PROMPT = """You are an elite AI Product Review Board evaluating a product development project.
You consist of three virtual reviewers:
1. Professor: Evaluates Academic Quality, Research, Storytelling, and Feasibility.
2. Senior PM: Evaluates Product Thinking, Customer Focus, Roadmap, KPIs, and Execution.
3. Startup Founder / Investor: Evaluates Market Size, Moats, Scale, Pricing, and Investor Interest.

You must critically evaluate the generated product ideas, score them out of 10 for all requested categories, identify weaknesses, and draft improvements.
Your response MUST be a single, valid JSON object matching the requested schema. Do not output markdown around the JSON, only the JSON itself."""


def generate_board_evaluation(
    signals: list,
    themes: list,
    barriers: list,
    personas: list,
    jobs: list,
    opportunities: list,
    hypotheses: list,
) -> dict:
    """
    Generate scorecards, improvement guides, and visual assets (Mermaid format) using LLM reasoning.
    """
    llm = get_llm_client()

    # Create simplified context string for prompt
    context = f"""
## PROJECT DATA CONTEXT
- Total Signals: {len(signals)}
- Top Themes: {', '.join(t.title for t in themes[:3])}
- Exploration Barriers: {', '.join(b.barrier_type.value for b in barriers[:3])}
- Archetypes: {', '.join(p.name for p in personas[:2])}
- Growth Opportunities: {', '.join(o.title for o in opportunities[:3])}
- Hypotheses: {', '.join(h.statement for h in hypotheses[:3])}
"""

    prompt = f"""Generate a comprehensive Review Board Evaluation based on this project context:
{context}

You must return a single JSON object containing:
1. "professor_scorecard":
   - "reviewer_name": "Dr. Sarah Sterling (Academic Chair)"
   - "focus": "Research quality, logic flow, evidence consistency, and validation methodology."
   - "scores": List of scorecard items for the following categories:
     - "Problem Identification"
     - "Research Quality"
     - "Evidence"
     - "Presentation"
     - "Storytelling"
     - "Data Interpretation"
     - "Visualization"
     - "Creativity"
     - "Overall Professionalism"
2. "pm_scorecard":
   - "reviewer_name": "Alex Chen (VP of Product, QuickCommerce)"
   - "focus": "Product execution, prioritizations, customer understanding, North Star metrics, and experiment design."
   - "scores": List of scorecard items for the following categories:
     - "Product Thinking"
     - "Customer Understanding"
     - "Prioritization"
     - "Problem Validation"
     - "MVP Scope"
     - "Roadmap"
     - "Tradeoffs"
     - "KPIs"
     - "Experiment Design"
3. "founder_scorecard":
   - "reviewer_name": "Marcus Vance (Managing Partner, Founder Capital)"
   - "focus": "Market viability, scalabilities, GTM moats, pricing structures, and competitive differentiation."
   - "scores": List of scorecard items for the following categories:
     - "Market Size"
     - "Business Potential"
     - "Differentiation"
     - "Competitive Advantage"
     - "AI Moat"
     - "Scalability"
     - "Go-To-Market"
     - "Investment Potential"
4. "improvement_report": List of exactly 10 high-priority actionable improvements.
5. "visual_assets": Dictionary of Mermaid.js diagrams for:
   - "wireframe": A mock Mermaid gantt or flowchart representing a web/app layout layout
   - "decision_tree": A Mermaid flowchart showing the user conversion decision tree
   - "journey_map": A Mermaid user journey matrix or flowchart
   - "roadmap": A Mermaid timeline or Gantt chart representing Now/Next/Later execution

For each ScorecardItem in "scores", you must supply:
- "category": name of category
- "score": score float (between 1.0 and 10.0, do not make all scores identical)
- "reason": detailed critique
- "strengths": list of strings
- "weaknesses": list of strings
- "suggestions": list of strings

Make the reviewer opinions distinct. The PM is metrics-focused, the Founder is moat/revenue-focused, and the Professor is academic-focused. They should not always agree on all aspects.

Ensure the final JSON is valid and correctly formatted.
"""
    try:
        response_text = llm.generate(BOARD_SYSTEM_PROMPT, prompt, creative=True)
        # Parse output to ensure it matches
        data = json.loads(response_text)
        return data
    except Exception as e:
        logger.exception("Failed to generate board evaluation via LLM, compiling mock report")
        return get_fallback_evaluation()


def generate_viva_questions(opportunities: list) -> list[dict]:
    """
    Generate 15 Viva questions (5 easy, 5 medium, 5 hard) based on the opportunities.
    """
    llm = get_llm_client()
    opp_titles = [o.title for o in opportunities[:3]]

    prompt = f"""Based on the top opportunities: {', '.join(opp_titles)}, generate exactly 15 Viva Defense questions.
Generate:
- 5 Easy questions (focus on basic rationale, "Why this problem?", "Why this MVP?")
- 5 Medium questions (focus on metrics, KPIs, assumptions, "Why not build Feature X?", "How will you validate this?")
- 5 Hard questions (focus on risks, moats, competitive threat, and edge-cases, "What if users don't adopt?", "What is your competitive advantage?")

Your output must be a single, valid JSON array containing exactly 15 objects.
Each object must have the following fields:
- "question_id": unique string (e.g. "q1", "q2"...)
- "question": the interview question string
- "purpose": why the board is asking this question
- "expected_direction": what a good answer should mention
- "difficulty": "easy", "medium", or "hard"

Do not write markdown, return only the JSON array."""

    try:
        response_text = llm.generate(BOARD_SYSTEM_PROMPT, prompt, creative=False)
        questions = json.loads(response_text)
        if isinstance(questions, list) and len(questions) > 0:
            return questions
        return get_fallback_viva_questions()
    except Exception as e:
        logger.error(f"Failed to generate viva questions: {e}")
        return get_fallback_viva_questions()


def evaluate_viva_answer(question: str, expected_direction: str, user_answer: str) -> dict:
    """
    Evaluate the user's viva answer across metrics.
    """
    llm = get_llm_client()

    prompt = f"""Evaluate this candidate's response in a Product Review board defense:
Question: {question}
Expected direction: {expected_direction}
Candidate's Answer: {user_answer}

Return a single JSON object with:
- "score": Float score (1.0 to 10.0)
- "confidence": Text describing their confidence level (e.g. "High", "Coached", "Hesitant")
- "communication_score": Float (1.0 to 10.0)
- "logic_score": Float (1.0 to 10.0)
- "product_thinking_score": Float (1.0 to 10.0)
- "business_thinking_score": Float (1.0 to 10.0)
- "clarity": Brief summary of the answer's quality
- "suggestions": List of 2-3 specific improvements on what the candidate should have said or how to structure the response better.

Do not write markdown, return only the JSON object."""

    try:
        response_text = llm.generate(BOARD_SYSTEM_PROMPT, prompt, creative=False)
        return json.loads(response_text)
    except Exception as e:
        logger.error(f"Failed to evaluate answer: {e}")
        return {
            "score": 7.0,
            "confidence": "Moderate",
            "communication_score": 7.5,
            "logic_score": 7.0,
            "product_thinking_score": 7.0,
            "business_thinking_score": 6.5,
            "clarity": "The answer provides a basic explanation but lacks quantitative evidence or structure.",
            "suggestions": [
                "Structure your answer using a standard PM framework (e.g., Situation-Task-Action-Result).",
                "Refer back to the original reviews/data to back up your assumptions."
            ]
        }


def get_fallback_evaluation() -> dict:
    """Standard backup evaluation if LLM fails or is rate-limited."""
    return {
        "professor_scorecard": {
            "reviewer_name": "Dr. Sarah Sterling (Academic Chair)",
            "focus": "Research quality, logic flow, evidence consistency, and validation methodology.",
            "scores": [
                {"category": "Problem Identification", "score": 8.5, "reason": "Clear identification of core quick commerce friction points.", "strengths": ["Clear definitions", "Accurate scope"], "weaknesses": ["Lacks broad segment sizing"], "suggestions": ["Include market reports"]},
                {"category": "Research Quality", "score": 8.0, "reason": "Good normalization of reviews.", "strengths": ["PII scrubbed"], "weaknesses": ["Small Reddit sample"], "suggestions": ["Increase scraping window"]}
            ],
            "overall_reviewer_feedback": "A structurally sound thesis. Needs more quantitative segment sizes."
        },
        "pm_scorecard": {
            "reviewer_name": "Alex Chen (VP of Product)",
            "focus": "Product execution, prioritizations, customer understanding, North Star metrics, and experiment design.",
            "scores": [
                {"category": "Product Thinking", "score": 9.0, "reason": "Excellent user persona matching.", "strengths": ["Clear user segments"], "weaknesses": ["Feature scope creep"], "suggestions": ["Cut secondary wireframe details"]},
                {"category": "KPIs", "score": 8.5, "reason": "Clear North Star metrics identified.", "strengths": ["Focus on retention"], "weaknesses": ["Missing short-term proxy metrics"], "suggestions": ["Track weekly search sessions"]}
            ],
            "overall_reviewer_feedback": "Highly actionable MVP recommendation. The roadmap is realistic."
        },
        "founder_scorecard": {
            "reviewer_name": "Marcus Vance (Managing Partner)",
            "focus": "Market viability, scalabilities, GTM moats, pricing structures, and competitive differentiation.",
            "scores": [
                {"category": "Differentiation", "score": 7.5, "reason": "Good proposed feature set but low entry barrier.", "strengths": ["Personalized search"], "weaknesses": ["Easy to copy by competitors"], "suggestions": ["Detail the ML recommendation moat"]},
                {"category": "Investment Potential", "score": 8.0, "reason": "Solves an active leak in quick-commerce user funnel.", "strengths": ["High growth sector"], "weaknesses": ["High customer acquisition cost"], "suggestions": ["Validate customer LTV assumptions"]}
            ],
            "overall_reviewer_feedback": "Solid GTM concept. Make sure the technical moat is defensible."
        },
        "improvement_report": [
            "Add market sizing data for the non-grocery segments to show revenue upside.",
            "Incorporate proxy metrics to measure search conversion before final retention metrics.",
            "Incorporate a localized recommendation algorithm description to strengthen the AI moat.",
            "Focus GTM specifically on Routine Buyers first rather than all personas simultaneously.",
            "Add a search discovery performance KPI to track navigation bottlenecks.",
            "Define specific fallback strategies for out-of-stock items in recommended recipes.",
            "Expand validation metrics to track A/B testing checkout conversion rates.",
            "Clarify checkout integration dependencies inside the MVP roadmap.",
            "Strengthen the UX flow between category tabs and personalized recommendation feeds.",
            "Incorporate customer acquisition cost (CAC) payback calculations for investors."
        ],
        "visual_assets": {
            "wireframe": "graph TD\n    A[Home Feed] --> B[Category Hub]\n    B --> C[Personalized Carousel]\n    C --> D[Quick Add Button]\n    D --> E[Cart / Checkout]",
            "decision_tree": "graph TD\n    A[User Needs Item] --> B{{Aware of Category?}}\n    B -- Yes --> C{{Trusts Quality?}}\n    B -- No --> D[Stays in Habit Loop]\n    C -- Yes --> E[Purchases Item]\n    C -- No --> F[Fails to Convert]",
            "journey_map": "graph LR\n    A[Need] --> B[Search] --> C[Hesitation] --> D[Review Verification] --> E[Purchase]",
            "roadmap": "gantt\n    title MVP Development Timeline\n    dateFormat  YYYY-MM-DD\n    section Core MVP\n    Feed Integration   :2026-08-01, 30d\n    A/B Testing        :2026-09-01, 15d\n    section Moat Addition\n    ML Algorithm       :2026-09-15, 30d"
        }
    }


def get_fallback_viva_questions() -> list[dict]:
    """Standard pre-generated questions in case of API limits."""
    return [
        {"question_id": "q1", "question": "Why did you choose this specific user problem to focus on first?", "purpose": "Test problem identification rationale", "expected_direction": "User should reference review counts or highest friction barrier from EDA.", "difficulty": "easy"},
        {"question_id": "q2", "question": "What is the primary value proposition of your proposed MVP?", "purpose": "Validate product positioning", "expected_direction": "Focus on lowering trust/awareness barriers to drive adoption.", "difficulty": "easy"},
        {"question_id": "q3", "question": "Which features did you exclude from the MVP scope, and why?", "purpose": "Assess scope management", "expected_direction": "Explain trade-offs, focus on core UX, and delay secondary configurations.", "difficulty": "medium"},
        {"question_id": "q4", "question": "How did you determine the RICE prioritization scores?", "purpose": "Validate prioritization framework", "expected_direction": "Explain the reach, impact, confidence, and effort scoring based on data.", "difficulty": "medium"},
        {"question_id": "q5", "question": "What is your North Star Metric, and what proxy metric will you track first?", "purpose": "Evaluate metrics logic", "expected_direction": "Long term retention/categories count, short term search click-through rate.", "difficulty": "medium"},
        {"question_id": "q6", "question": "What is your Go-To-Market strategy, and how does it drive virality?", "purpose": "Evaluate distribution assumptions", "expected_direction": "Referral loops, category cross-selling promos, or contextual feeds.", "difficulty": "hard"},
        {"question_id": "q7", "question": "If a major competitor copies your feature within a month, what is your defensibility?", "purpose": "Challenge product moat", "expected_direction": "Emphasize proprietary ML model recommendations, local delivery speed integration, or brand trust.", "difficulty": "hard"}
    ]
