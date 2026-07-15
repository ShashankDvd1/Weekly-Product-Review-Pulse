"""
Pulse Intelligence — Research Copilot

Generates research artifacts from analysis results:
- Hypotheses to validate
- Interview questions
- Survey questions
- Research plans

Directly supports Product Managers performing primary research.
"""

import logging
import uuid

from core.llm_client import get_llm_client
from core.schemas import (
    Theme, CategoryBarrier, Persona, JTBD, GrowthOpportunity,
    Hypothesis, InterviewQuestion,
)

logger = logging.getLogger(__name__)


RESEARCH_SYSTEM_PROMPT = """You are a Senior User Researcher at a Quick Commerce company.

You design rigorous research studies to validate product hypotheses. Your interview questions are:
- Open-ended (not leading)
- Behavioral (ask about past actions, not hypothetical futures)
- Specific (reference real scenarios users encounter)
- Progressive (start broad, narrow to specifics)

Your hypotheses are:
- Falsifiable (can be proven wrong)
- Specific (not vague)
- Tied to measurable outcomes

You follow best practices from "The Mom Test" and JTBD interview methodology.
Always output valid JSON.
"""


def generate_hypotheses(
    barriers: list[CategoryBarrier],
    opportunities: list[GrowthOpportunity],
    themes: list[Theme],
) -> list[Hypothesis]:
    """
    Generate testable product hypotheses from analysis results.

    Each hypothesis is:
    - Falsifiable
    - Evidence-backed
    - Tied to a specific barrier or opportunity
    - Includes a validation method
    """
    llm = get_llm_client()

    barriers_str = "\n".join([
        f"- [{b.barrier_type.value}] {b.category}: {b.description} (confidence: {b.confidence:.1f})"
        for b in barriers[:8]
    ])

    opportunities_str = "\n".join([
        f"- {o.title}: {o.description} (impact: {o.impact})"
        for o in opportunities[:6]
    ])

    themes_str = "\n".join([
        f"- {t.title}: {t.summary}"
        for t in themes[:8]
    ])

    prompt = f"""Based on the following analysis of quick commerce user behavior, generate 8-10 testable product hypotheses.

## CATEGORY BARRIERS
{barriers_str}

## GROWTH OPPORTUNITIES
{opportunities_str}

## KEY THEMES
{themes_str}

For each hypothesis, provide:
- "statement": The hypothesis in format "We believe that [intervention] will [outcome] because [reason]"
- "rationale": 2-3 sentences explaining the evidence behind this hypothesis
- "evidence_count": Number of supporting data points
- "confidence": Float 0.0-1.0
- "validation_method": Specific method to test this (A/B test, user interview, survey, prototype test)

CRITICAL: At least 4 hypotheses must be about category exploration barriers.

Return JSON: {{"hypotheses": [...]}}"""

    result = llm.generate(RESEARCH_SYSTEM_PROMPT, prompt, creative=False)

    hypotheses = []
    for h_data in result.get("hypotheses", []):
        hyp = Hypothesis(
            hypothesis_id=f"hyp_{uuid.uuid4().hex[:8]}",
            statement=h_data.get("statement", ""),
            rationale=h_data.get("rationale", ""),
            evidence_count=h_data.get("evidence_count", 0),
            confidence=max(0.0, min(1.0, h_data.get("confidence", 0.5))),
            validation_method=h_data.get("validation_method", ""),
        )
        hypotheses.append(hyp)

    logger.info(f"Generated {len(hypotheses)} research hypotheses")
    return hypotheses


def generate_interview_questions(
    personas: list[Persona],
    barriers: list[CategoryBarrier],
    hypotheses: list[Hypothesis],
    num_questions: int = 15,
) -> list[InterviewQuestion]:
    """
    Generate user interview questions for primary research.

    Uses "The Mom Test" methodology — questions about past behavior,
    not hypothetical futures.
    """
    llm = get_llm_client()

    personas_str = "\n".join([
        f"- {p.name}: {p.description[:200]}"
        for p in personas
    ])

    barriers_str = "\n".join([
        f"- {b.category} — {b.barrier_type.value}: {b.description[:150]}"
        for b in barriers[:6]
    ])

    hypotheses_str = "\n".join([
        f"- {h.statement}"
        for h in hypotheses[:5]
    ])

    prompt = f"""Design {num_questions} interview questions for user research on quick commerce category exploration.

## TARGET PERSONAS
{personas_str}

## BARRIERS TO VALIDATE
{barriers_str}

## HYPOTHESES TO TEST
{hypotheses_str}

For each question, provide:
- "question": The actual interview question
- "purpose": What insight this question aims to uncover (1 sentence)
- "target_persona": Which persona this is most relevant for (or "all")
- "question_type": One of [open, probing, behavioral, scaling]

RULES (from "The Mom Test"):
1. Ask about PAST behavior, not hypothetical futures ("Tell me about the last time..." NOT "Would you...")
2. Never ask leading questions
3. Ask about specific instances, not generalizations
4. Include 2-3 warm-up questions before deep questions
5. End with "What else should I know about...?"

Structure:
- Questions 1-3: Warm-up (general shopping habits)
- Questions 4-7: Category behavior (what they buy, what they don't)
- Questions 8-11: Barrier probing (why they avoid certain categories)
- Questions 12-14: Discovery & trust (how they found new categories)
- Question 15: Closing open question

Return JSON: {{"questions": [...]}}"""

    result = llm.generate(RESEARCH_SYSTEM_PROMPT, prompt, creative=True)

    questions = []
    for q_data in result.get("questions", []):
        question = InterviewQuestion(
            question=q_data.get("question", ""),
            purpose=q_data.get("purpose", ""),
            target_persona=q_data.get("target_persona"),
            related_hypothesis=q_data.get("related_hypothesis"),
            question_type=q_data.get("question_type", "open"),
        )
        questions.append(question)

    logger.info(f"Generated {len(questions)} interview questions")
    return questions
