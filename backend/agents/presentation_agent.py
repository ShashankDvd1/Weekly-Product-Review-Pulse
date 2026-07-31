import json
from agents.base import BaseAgent

class ExecutivePresentationAgent(BaseAgent):
    def __init__(self):
        super().__init__("Executive Presentation Agent")

    def synthesize(self, solution_data: dict, root_cause_data: dict, discovery_data: dict, problem_statement: str = None) -> dict:
        """
        Synthesize analysis into a strict 10-slide executive board presentation JSON using the 2-batch synthesize_board_presentation.
        """
        from reasoning.board_presenter import synthesize_board_presentation
        
        strategy_data = {
            "active_problem_statement": problem_statement,
            "steps": {
                "step_1": {"title": "Discovery Data", "data": discovery_data},
                "step_2": {"title": "Root Cause Analysis", "data": root_cause_data},
                "step_14": {"title": "Solution Generation", "data": solution_data}
            }
        }
        
        return synthesize_board_presentation(strategy_data)

