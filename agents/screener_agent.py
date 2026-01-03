from typing import Dict, Any
from .base_agent import BaseAgent
from datetime import datetime
import ast
import json


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
            - Specific scoring (0-100)
            Provide comprehensive reports.""",
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
             
        # Prepare focused context
        focused_context = {
            "candidate_name": workflow_context.get("extraction_results", {}).get("structured_data", {}).get("Personal Info", {}).get("Name", "Candidate"),
            "skills_analysis": workflow_context.get("analysis_results", {}).get("skills_analysis", {}),
            "job_matches": workflow_context.get("job_matches", {}).get("matched_jobs", [])
        }
             
        prompt = f"""
        Conduct a comprehensive screening of this candidate based on the profile and job matches.
        
        Candidate Data: {json.dumps(focused_context, indent=2)}
        
        Evaluate:
        1. Qualification alignment with matched jobs
        2. Experience relevance
        3. Skill gaps or red flags
        
        Return a STRICT JSON object with no markdown formatting:
        {{
            "screening_report": "detailed textual report (3-4 sentences)",
            "screening_score": number (integer 0-100),
            "red_flags": ["flag1", "flag2"]
        }}
        """

        response = self._query_llm(prompt)
        parsed = self._parse_json_safely(response)

        return {
            "screening_report": parsed.get("screening_report", "No report generated"),
            "screening_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "screening_score": int(parsed.get("screening_score", 50)),
            "red_flags": parsed.get("red_flags", [])
        }