"""
Pulse Intelligence — Persona Generator

Generates AI-powered user personas from behavioral signals.
Each persona represents a distinct user archetype with specific
shopping habits, motivations, and barriers.
"""

import logging
import uuid
from typing import Optional, List
from typing import Optional

from core.llm_client import get_llm_client, count_tokens
from core.schemas import UnifiedSignal, Persona
from core.prompts import ANTI_HALLUCINATION_RULES

logger = logging.getLogger(__name__)


def ensure_list(val) -> list[str]:
    if not val:
        return []
    if isinstance(val, list):
        return [str(x) for x in val if x]
    if isinstance(val, str):
        stripped = val.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            try:
                import json
                parsed = json.loads(stripped)
                if isinstance(parsed, list):
                    return [str(x) for x in parsed if x]
            except Exception:
                pass
        return [x.strip() for x in val.split(",") if x.strip()]
    return [str(val)]


PERSONA_SYSTEM_PROMPT = """You are a Senior UX Researcher specializing in Quick Commerce consumer behavior.

You create rich, evidence-based user personas from customer signals (app reviews, Reddit discussions).

Your personas are NOT generic marketing stereotypes. They are behavioral archetypes grounded in REAL user data.

Each persona should capture:
1. A vivid, specific behavioral profile (not demographics)
2. Concrete shopping habits and routines
3. Specific motivations (why they use quick commerce)
4. Specific barriers (what stops them from exploring new categories)
5. Category preferences and avoidances

Think like an ethnographer who spent 6 months observing these users, not a marketer filling in a template.

CRITICAL: Every claim in the persona must be traceable to actual user signals. Include representative quotes.
Always output valid JSON.

{ANTI_HALLUCINATION_RULES}
"""


def generate_personas(
    signals: list[UnifiedSignal],
    num_personas: int = 4,
    problem_statement: Optional[str] = None,
) -> list[Persona]:
    """
    Generate user personas from consumer signals.

    Analyzes behavioral patterns across all signals to identify
    distinct user archetypes with specific habits and barriers.

    Args:
        signals: Normalized consumer signals from all sources
        num_personas: Number of personas to generate (3-6 recommended)

    Returns:
        List of Persona objects with behavioral profiles
    """
    if not signals:
        return []

    llm = get_llm_client()

    # Prepare signal summary for the LLM (sample to respect token limits)
    sample_size = min(len(signals), 80)
    sample = signals[:sample_size]

    signal_texts = []
    for s in sample:
        prefix = f"[{s.source.value}|{s.app_name}"
        if s.rating:
            prefix += f"|{'★' * s.rating}"
        prefix += "]"
        if s.behavioral_signals:
            prefix += f" [signals: {', '.join(s.behavioral_signals)}]"
        signal_texts.append(f"{prefix} {s.content[:300]}")

    chunk = "\n\n".join(signal_texts)

    prob_stmt_block = f"\nTARGET PROBLEM STATEMENT / STRATEGIC FOCUS:\n{problem_statement}\n" if problem_statement else ""

    prompt = f"""Based on these {len(sample)} consumer signals from quick commerce users, generate exactly {num_personas} distinct user personas.
{prob_stmt_block}
These personas should represent DIFFERENT behavioral archetypes — users who use quick commerce apps differently.

For each persona, provide:
- "name": A memorable archetype name (e.g., "The Pantry Stocker", "The Impulse Snacker", "The Curious Explorer")
- "description": 3-4 sentence behavioral profile
- "shopping_habits": How and when they use quick commerce (specific routines, frequencies)
- "motivations": List of 3-5 specific reasons they use these apps
- "barriers": List of 3-5 specific things that prevent them from exploring new categories
- "preferred_categories": Categories they regularly buy from
- "avoided_categories": Categories they never/rarely buy from
- "apps_used": Which apps they primarily use
- "representative_quotes": 2-3 exact verbatim quotes from the signals that best represent this persona
- "signal_count": Estimated number of signals that match this persona
- "confidence": Float 0.0-1.0

IMPORTANT: Make each persona DISTINCT and BEHAVIORAL (not demographic). 
- Do NOT generate generic clichés like "The Convenience Seeker" or "The Price Sensitive Shopper".
- Instead, create hyper-specific behavioral archetypes relevant to quick-commerce category exploration (e.g. "The Non-Grocery Skeptic" who fears buying beauty/electronics because of counterfeit risk, "The Fresh-Food Loyalist" who only uses the app for daily vegetables and milk, "The Emergency-Only Purchaser", or "The Tech/Beauty Experimenter").
- At least one persona should be someone who DOES explore categories (to understand what drives exploration).

Return JSON: {{"personas": [...]}}

CONSUMER SIGNALS:
{chunk}"""

    result = llm.generate(PERSONA_SYSTEM_PROMPT, prompt, creative=True)

    personas = []
    for p_data in result.get("personas", []):
        desc_raw = p_data.get("description", "")
        if isinstance(desc_raw, list):
            description = " ".join(str(d) for d in desc_raw)
        elif isinstance(desc_raw, dict):
            description = ", ".join(f"{k}: {v}" for k, v in desc_raw.items())
        else:
            description = str(desc_raw)

        habits_raw = p_data.get("shopping_habits", "")
        if isinstance(habits_raw, dict):
            shopping_habits = ", ".join(f"{k}: {v}" for k, v in habits_raw.items())
        elif isinstance(habits_raw, list):
            shopping_habits = "; ".join(str(x) for x in habits_raw)
        else:
            shopping_habits = str(habits_raw)

        persona = Persona(
            persona_id=f"persona_{uuid.uuid4().hex[:8]}",
            name=p_data.get("name", "Unknown Persona"),
            description=description,
            shopping_habits=shopping_habits,
            motivations=ensure_list(p_data.get("motivations", [])),
            barriers=ensure_list(p_data.get("barriers", [])),
            preferred_categories=ensure_list(p_data.get("preferred_categories", [])),
            avoided_categories=ensure_list(p_data.get("avoided_categories", []),),
            apps_used=ensure_list(p_data.get("apps_used", [])),
            signal_count=p_data.get("signal_count", 0),
            representative_quotes=ensure_list(p_data.get("representative_quotes", [])),
            confidence=max(0.0, min(1.0, p_data.get("confidence", 0.5))),
        )
        personas.append(persona)

    logger.info(f"Generated {len(personas)} personas from {len(signals)} signals")
    return personas
