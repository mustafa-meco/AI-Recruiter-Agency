from typing import Dict, Any
from .base_agent import BaseAgent
from datetime import datetime
import ast


class RecommenderAgent(BaseAgent):
    def __init__(self, provider: str = None, api_key: str = None):
        super().__init__(
            name="Recommender",
            instructions="""Generate final recommendations considering:
            1. Extracted profile
            2. Skills analysis
            3. Job matches
            4. Screening results
            Provide clear next steps and specific recommendations.""",
            provider=provider,
            api_key=api_key
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Generate final recommendations"""
        print("💡 Recommender: Generating final recommendations")

        content = messages[-1]["content"]
        try:
             workflow_context = ast.literal_eval(content) if isinstance(content, str) else content
        except (ValueError, SyntaxError):
             print(f"RecommenderAgent: Failed to parse input: {content}")
             workflow_context = {}

        prompt = f"""
        Provide a final hiring recommendation based on the full workflow data.
        Data: {str(workflow_context)}
        
        Return a JSON object with:
        {{
            "recommendation": "detailed textual recommendation",
            "next_steps": ["step1", "step2"],
            "confidence_level": "Low/Medium/High"
        }}
        """

        response = self._query_llm(prompt)
        parsed = self._parse_json_safely(response)

        return {
            "final_recommendation": parsed.get("recommendation", "No recommendation generated"),
            "next_steps": parsed.get("next_steps", []),
            "recommendation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "confidence_level": parsed.get("confidence_level", "Medium"),
        }