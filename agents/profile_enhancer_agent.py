from typing import Dict, Any
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class ProfileEnhancerAgent(BaseAgent):
    def __init__(self, provider: str = None, api_key: str = None):
        super().__init__(
            name="ProfileEnhancer",
            instructions="""You are a Professional Profile Optimizer.
            Your goal is to take extracted resume data and polish it into a coherent, professional summary.
            Fix grammatical errors, standardize job titles, and summarize key strengths.
            
            Return ONLY a JSON object with:
            {
                "enhanced_summary": "polished professional summary",
                "standardized_skills": ["Skill 1", "Skill 2"],
                "total_years_exp": 0
            }
            """,
            provider=provider,
            api_key=api_key
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Enhance and clean up the candidate profile"""
        print("✨ ProfileEnhancer: Polishing candidate profile")
        
        content = messages[-1].get("content", "{}")
        
        prompt = f"""
        Enhance and standardize this candidate data:
        {str(content)}
        
        Ensure output is valid JSON.
        """
        
        response = self._query_llm(prompt)
        return self._parse_json_safely(response)