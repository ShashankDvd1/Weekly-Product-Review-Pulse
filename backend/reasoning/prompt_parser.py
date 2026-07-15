"""
Pulse Intelligence — Ingestion Command Prompt Parser

Translates natural language configuration prompts into structured API payloads.
Uses Groq Llama 3.1 8B with relative date calculations based on current date.
"""

import logging
from datetime import datetime
import json

from core.llm_client import get_llm_client

logger = logging.getLogger(__name__)

PARSER_SYSTEM_PROMPT = """You are a configuration parser for the Pulse Intelligence platform.
Your job is to translate a user's natural language command describing what data to fetch into a structured JSON configuration.

Current Date: {current_date}

Registered App Keys:
- "zepto" (Zepto)
- "blinkit" (Blinkit)
- "swiggy_instamart" (Swiggy Instamart)

Rules for parsing:
1. "apps": List of app keys mentioned. If the user mentions an app like "Zepto" or "Swiggy", map it to "zepto" or "swiggy_instamart". If they don't mention any app, default to ["zepto", "blinkit", "swiggy_instamart"], EXCEPT if they provide custom App/Play Store links, in which case "apps" should be an empty list [].
2. App Store / Play Store Links:
   - If they provide a Google Play link (e.g. details?id=com.grofers.customerapp), extract the package name (e.g., "com.grofers.customerapp") into "play_store_package".
   - If they provide an Apple App Store link (e.g. id741750240), extract the numeric ID (e.g., "741750240") into "app_store_id".
3. Dates:
   - If they mention "last 3 months", "past year", "since Jan 2024", etc., calculate the exact "YYYY-MM-DD" start and end dates relative to the Current Date ({current_date}).
   - Default from_date: "2024-01-01"
   - Default to_date: "{current_date}"
4. Reddit parameters:
   - "include_reddit": Boolean. Default is true if they mention Reddit, subreddits, or generic quick commerce queries. If they only ask for specific custom App Store / Play Store links, default to false.
   - "reddit_subreddits": Extract any subreddits mentioned (e.g., "r/india" -> "india").
   - "reddit_search_terms": Extract search queries/keywords.

You MUST output ONLY a valid JSON object matching the following structure:
{{
  "apps": ["zepto", "blinkit"],
  "play_store_package": "com.kiranacheckout.customer" or null,
  "app_store_id": "1575323757" or null,
  "from_date": "YYYY-MM-DD",
  "to_date": "YYYY-MM-DD",
  "include_reddit": true,
  "reddit_subreddits": ["india"],
  "reddit_search_terms": ["zepto delivery"]
}}
"""

def parse_ingestion_prompt(prompt: str) -> dict:
    """
    Parse natural language commands into a structured config dict.
    """
    llm = get_llm_client()
    current_date = datetime.now().strftime("%Y-%m-%d")

    system_prompt = PARSER_SYSTEM_PROMPT.format(current_date=current_date)
    user_prompt = f"Parse this command:\n\"{prompt}\""

    try:
        # Use fast 8B model for quick structured parsing
        result = llm.analyze(system_prompt, user_prompt, use_reasoning=False)
        logger.info(f"Successfully parsed command: '{prompt}' -> {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to parse command prompt: {e}")
        # Return fallback configuration
        return {
            "apps": ["zepto", "blinkit", "swiggy_instamart"],
            "play_store_package": None,
            "app_store_id": None,
            "from_date": "2024-01-01",
            "to_date": current_date,
            "include_reddit": True,
            "reddit_subreddits": [],
            "reddit_search_terms": [],
            "error": str(e)
        }
