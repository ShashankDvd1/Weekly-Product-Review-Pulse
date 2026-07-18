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
    Hypothesis, OptimizedInterviewQuestion, InterviewScriptOutput
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

Always output valid JSON.
"""

MOM_TEST_SYSTEM_PROMPT = """You are an expert UX Researcher, Principal Product Manager, and Customer Discovery Coach who specializes in designing high-quality user interview scripts based on **The Mom Test** methodology.

Your task is NOT to generate more questions.
Your task is to **critically evaluate and optimize** the existing interview questionnaire.

## Objective
Every interview question must directly validate one or more product hypotheses.
Questions that do not contribute to validating the hypotheses must be removed or rewritten.
The final interview should be concise, focused, and free of unnecessary questions.

## Optimization Rules
Rule 1 — Every question must map to a hypothesis. Delete if it doesn't.
Rule 2 — Stay strictly within scope.
Rule 3 — Follow The Mom Test (ask about real behavior, recent experiences, actual decisions. Never ask about opinions or future intentions).
Rule 4 — One objective per question.
Rule 5 — Remove leading questions.
Rule 6 — Remove solution bias (never mention proposed features).
Rule 7 — Short and direct (Ideal length 10-15 words).
Rule 8 — Ask only what changes product decisions.
Rule 9 — Follow a logical interview flow.
Rule 10 — Identify redundancy and merge.

Your goal is to create a high-signal, low-noise interview guide where every question contributes directly to validating the product problem and informing product decisions.
You must output a "Hypothesis Coverage Matrix" (in the JSON) to prove every hypothesis has a valid question.
Respond in a single valid JSON object matching the requested schema. Do not output markdown around the JSON.
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


def _generate_draft_questions(
    personas: list[Persona],
    barriers: list[CategoryBarrier],
    hypotheses: list[Hypothesis],
    num_questions: int = 15,
) -> list[dict]:
    """Pass 1: Generate the rough draft of interview questions."""
    llm = get_llm_client()

    personas_str = "\n".join([f"- {p.name}: {p.description[:200]}" for p in personas])
    barriers_str = "\n".join([f"- {b.category} — {b.barrier_type.value}: {b.description[:150]}" for b in barriers[:6]])
    hypotheses_str = "\n".join([f"- {h.statement}" for h in hypotheses[:5]])

    prompt = f"""Design a draft of {num_questions} interview questions.

## TARGET PERSONAS
{personas_str}

## BARRIERS
{barriers_str}

## HYPOTHESES TO TEST
{hypotheses_str}

Return JSON: {{"questions": [{{"question": "...", "purpose": "...", "target_persona": "...", "question_type": "open"}}]}}"""

    result = llm.generate(RESEARCH_SYSTEM_PROMPT, prompt, creative=True)
    return result.get("questions", [])


def generate_interview_questions(
    personas: list[Persona],
    barriers: list[CategoryBarrier],
    hypotheses: list[Hypothesis],
    num_questions: int = 15,
) -> InterviewScriptOutput:
    """
    Pass 2: The Mom Test Strict Optimization.
    Takes the draft questions and rigorously critiques and optimizes them.
    """
    # Pass 1
    draft_questions = _generate_draft_questions(personas, barriers, hypotheses, num_questions)
    
    if not draft_questions:
        return InterviewScriptOutput()

    # Pass 2
    llm = get_llm_client()
    
    draft_str = "\n".join([
        f"Q{i+1}. {q.get('question')} (Purpose: {q.get('purpose')})" 
        for i, q in enumerate(draft_questions)
    ])
    
    hypotheses_str = "\n".join([f"- {h.statement}" for h in hypotheses[:5]])

    prompt = f"""Critically evaluate and optimize the following DRAFT interview questionnaire based on The Mom Test rules.

## THE DRAFT QUESTIONS
{draft_str}

## THE HYPOTHESES TO VALIDATE
{hypotheses_str}

Return JSON: 
{{
  "optimized_script": [
    {{
      "original_question": "...",
      "issues": ["Too broad", "Leading"],
      "optimized_question": "...",
      "validated_hypothesis": "...",
      "decision_supported": "..."
    }}
  ],
  "removed_questions": [
    {{"question": "...", "reason": "..."}}
  ],
  "missing_questions": ["..."],
  "estimated_duration": "15-20 minutes",
  "quality_score": 85,
  "recommendations": ["..."]
}}
"""

    result = llm.generate(MOM_TEST_SYSTEM_PROMPT, prompt, creative=False)
    
    try:
        if isinstance(result, dict):
            return InterviewScriptOutput(**result)
        else:
            import json
            return InterviewScriptOutput(**json.loads(result))
    except Exception as e:
        logger.error(f"Error parsing optimized script: {e}")
        return InterviewScriptOutput()
