from typing import Dict, Any
from .base_agent import BaseAgent
from datetime import datetime
import ast
import json


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

        # Prepare focused context to avoid token limits and noise
        focused_context = {
            "candidate_name": workflow_context.get("extraction_results", {}).get("structured_data", {}).get("Personal Info", {}).get("Name", "Candidate"),
            "skills": workflow_context.get("analysis_results", {}).get("skills_analysis", {}).get("technical_skills", []),
            "experience": workflow_context.get("analysis_results", {}).get("skills_analysis", {}).get("years_of_experience", "Unknown"),
            "matches": workflow_context.get("job_matches", {}).get("matched_jobs", []),
            "screening_score": workflow_context.get("screening_results", {}).get("screening_score", 0),
            "red_flags": workflow_context.get("screening_results", {}).get("red_flags", [])
        }

        prompt = f"""
        ACT AS A SENIOR HR DIRECTOR.
        Provide a final hiring recommendation based on the candidate summary below.
        
        Candidate Data: {json.dumps(focused_context, indent=2)}
        
        REQUIRED OUTPUT FORMAT (STRICT JSON):
        {{
            "hiring_status": "Recommended" | "Not Recommended" | "Pending Review",
            "recommendation": "Professional 2-3 sentence justification. Focus on why they fit or don't fit based on skills and screening score.",
            "next_steps": ["Specific actionable next step 1", "Specific actionable next step 2"],
            "confidence_level": "Low" | "Medium" | "High"
        }}
        
        DO NOT include any explanation outside the JSON block.
        """

        response = self._query_llm(prompt)
        parsed = self._parse_json_safely(response)
        
        if not parsed or "recommendation" not in parsed:
            print(f"RecommenderAgent Error: Invalid JSON response: {response}")

        return {
             "hiring_status": parsed.get("hiring_status", "Pending Review"),
             "recommendation": parsed.get("recommendation", "Use manual review. Agent failed to generate recommendation."),
             "next_steps": parsed.get("next_steps", []),
             "recommendation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "confidence_level": parsed.get("confidence_level", "Medium"),
        }