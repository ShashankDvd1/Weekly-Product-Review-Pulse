"""
Pulse Intelligence - Blinkit Cross Sell Case Study Engine

Dedicated reasoning engine for the Blinkit Growth PM Case Study.
Focuses specifically on why users don't explore new categories and 
synthesizing scraped data with primary survey data.
"""

import logging
from typing import Any
from core.llm_client import get_llm_client
from core.schemas import UnifiedSignal
from reasoning.behavior_analyzer import _prepare_signals_for_llm

logger = logging.getLogger(__name__)

BLINKIT_CASE_STUDY_PROMPT = """You are a Growth Product Manager at Blinkit. 
Your goal is to increase the percentage of MAUs who purchase products from at least one new category every month.

Analyze these filtered consumer signals specifically looking for:
1. Why do users repeatedly buy from the same categories?
2. What prevents them from exploring new categories (e.g., Electronics, Beauty, Toys)?
3. What role do habits play?
4. What information do users need before trying a new category on Blinkit?

Return a JSON object with:
- "root_causes": [{"cause": "string", "description": "string", "evidence_quotes": ["quote1"]}]
- "existing_workarounds": ["workaround1", "workaround2"]
- "user_value": "Why solving this helps the user"
- "business_value": "Why solving this helps Blinkit (AOV, Retention)"
- "recommended_mvp": {"title": "string", "description": "string"}

Always output valid JSON.
"""

def analyze_blinkit_cross_sell(signals: list[UnifiedSignal], problem_statement: str = None) -> dict:
    """Analyze filtered signals for the Blinkit case study using the custom problem statement."""
    if not signals:
        return {"error": "No signals provided"}

    llm = get_llm_client()
    chunks = _prepare_signals_for_llm(signals, max_tokens=3000)
    
    if not chunks:
        return {"error": "No chunks generated"}
        
    prob_context = f"\nTARGET PROBLEM STATEMENT / STRATEGIC FOCUS:\n{problem_statement}\n" if problem_statement else ""

    prompt = f"""{BLINKIT_CASE_STUDY_PROMPT}
{prob_context}
SIGNALS:
{chunks[0]}
"""
    result = llm.analyze("You are a Growth PM. Output valid JSON.", prompt, use_reasoning=True)
    return result

def synthesize_primary_research(scraped_insights: dict, survey_data: list[dict]) -> dict:
    """
    Compare and synthesize the AI insights from Play Store/Reddit (scraped_insights) 
    with the actual user survey data (Google Form CSV).
    """
    llm = get_llm_client()
    
    survey_text = "\n".join([str(row) for row in survey_data[:50]]) # Limit to 50 rows to save tokens
    
    prompt = f"""You are a Growth PM at Blinkit.
We have two data sources regarding why users don't explore new categories.

SOURCE 1: SCRAPED PUBLIC DATA (App Store / Reddit)
{scraped_insights}

SOURCE 2: PRIMARY USER SURVEY (Google Form)
{survey_text}

Task:
1. Validate or challenge the public data using the primary survey data.
2. Identify the final "Root Cause" of the problem based on both sources.
3. Write the final content for the "Problem Statement" slide deck.

Return JSON:
- "validation_summary": "How the survey validates or challenges the scraped data"
- "final_root_cause": "The definitive root cause"
- "problem_statement_markdown": "Markdown text for the final problem statement doc"
"""
    result = llm.analyze("You are a Growth PM. Output valid JSON.", prompt, use_reasoning=True)
    return result
