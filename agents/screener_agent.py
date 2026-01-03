from typing import Dict, Any
from .base_agent import BaseAgent
from datetime import datetime
import ast


class ScreenerAgent(BaseAgent):
    def __init__(self, provider: str = None, api_key: str = None):
        super().__init__(
            name="Screener",
            instructions="""Screen candidates based on:
            - Qualification alignment
            - Experience relevance
            - Skill match percentage
            - Cultural fit indicators
            - Red flags or concerns
            Provide comprehensive screening reports.""",
            provider=provider,
            api_key=api_key
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Screen the candidate"""
        print("👥 Screener: Conducting initial screening")

        content = messages[-1]["content"]
        try:
             workflow_context = ast.literal_eval(content) if isinstance(content, str) else content
        except (ValueError, SyntaxError):
             print(f"ScreenerAgent: Failed to parse input: {content}")
             workflow_context = {}
             
        prompt = f"""
        Conduct a comprehensive screening of this candidate.
        Context: {str(workflow_context)}
        
        Evaluate:
        1. Qualification alignment
        2. Experience relevance
        3. Potential red flags
        
        Return a JSON object with:
        {{
            "screening_report": "detailed textual report",
            "screening_score": number (0-100),
            "red_flags": ["flag1", "flag2"]
        }}
        """

        response = self._query_llm(prompt)
        parsed = self._parse_json_safely(response)

        return {
            "screening_report": parsed.get("screening_report", "No report generated"),
            "screening_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "screening_score": parsed.get("screening_score", 50),
            "red_flags": parsed.get("red_flags", [])
        }