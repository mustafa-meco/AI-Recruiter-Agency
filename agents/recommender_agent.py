from datetime import datetime
from typing import Dict, Any
from .base_agent import BaseAgent


class RecommenderAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Recommender",
            instructions="""Generate final recommendations considering:
            1. Extracted profile
            2. Skills analysis
            3. Job matches
            4. Screening results
            Provide clear next steps and specific recommendations.
            """,
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Generate final recommendations"""
        print("Recommender: Generating final recommendations")

        workflow_context = eval(messages[-1]['content'])
        recommendation = self._query_ollama(str(workflow_context))

        return {
            "final_recommendation": recommendation,
            "recommendation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "confidence_level": "high"
        }