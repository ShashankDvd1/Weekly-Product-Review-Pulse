import logging
import json
from core.llm_client import get_llm_client

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Base class for all research agents.
    Provides standard logging and JSON parsing helpers.
    """
    def __init__(self, name: str):
        self.name = name
        self.llm = get_llm_client()
        self.logger = logging.getLogger(f"agents.{name.lower().replace(' ', '_')}")

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        """Helper to query the LLM and return parsed JSON."""
        try:
            self.logger.info(f"[{self.name}] Querying LLM...")
            result = self.llm.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                creative=False
            )
            # If the llm returns raw text inside generator wrappers, parse it
            if isinstance(result, str):
                return json.loads(result)
            return result
        except Exception as e:
            self.logger.error(f"[{self.name}] LLM Generation failed: {e}")
            return {"error": str(e)}
