from typing import Dict, Any
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class CandidateAdvisorAgent(BaseAgent):
    def __init__(self, provider: str = None, api_key: str = None):
        super().__init__(
            name="CandidateAdvisor",
            instructions="""You are a Career Advisor Expert.
            Your goal is to provide actionable, constructive feedback to candidates.
            
            Input: Candidate's structured profile (skills, experience, etc.) and potentially job matches.
            
            Task:
            1. Identify gaps between the candidate's profile and typical market requirements for their role.
            2. Suggest specific improvements (e.g., "Learn Docker", "Quantify achievements").
            3. Provide a motivating summary.
            
            Output JSON format:
            {
                "strengths": ["Strong python skills", ...],
                "improvement_areas": ["Lack of cloud experience", ...],
                "actionable_tips": ["Build a project using AWS", ...],
                "career_advice": "Focus on backend scalable systems..."
            }
            """,
            provider=provider,
            api_key=api_key
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """
        Generate career advice.
        Expected input: {"profile": {...}, "role": "..."}
        """
        print("🧑‍🏫 Advisor: Generating career advice...")
        
        content = messages[-1].get("content", {})
        
        # Prepare context for LLM
        prompt = f"""
        As a Career Advisor, analyze this candidate profile:
        {str(content)}
        
        Provide a strategic career advice report in JSON format.
        
        Required JSON Structure:
        {{
            "strengths": ["list of assets"],
            "improvement_areas": ["list of gaps"],
            "actionable_tips": ["specific steps to take"],
            "career_advice": "long-term strategic summary"
        }}
        
        Return ONLY valid JSON.
        """
        
        response = self._query_llm(prompt)
        parsed = self._parse_json_safely(response)
        
        if "error" in parsed:
            logger.warning(f"Advisor LLM failed: {parsed.get('error')}")
            return {
                "strengths": [],
                "improvement_areas": [],
                "actionable_tips": ["Update your resume with more keywords."],
                "career_advice": "Keep applying!"
            }
            
        return parsed
