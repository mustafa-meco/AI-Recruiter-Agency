from typing import Dict, Any
from .base_agent import BaseAgent


class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Analyzer",
            instructions="""Analyze candidate profiles in depth.
            - Evaluate technical skills and proficiency levels.
            - Assess years of experience and career progression.
            - Identify key strengths and potential gaps.
            - Provide a professional summary of the candidate's suitability.
            Return results in a structured format."""
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Analyze the candidate profile"""
        print("Analyzer: Analyzing candidate profile")

        workflow_context = eval(messages[-1]['content'])
        extracted_data = workflow_context.get("extracted_data", {})
        
        # In a real scenario, we would pass specific parts to the LLM
        # For now, we'll pass the whole structured data for analysis
        analysis_prompt = f"Analyze this candidate profile: {extracted_data.get('structured_data', '')}"
        
        analysis_content = self._query_ollama(analysis_prompt)

        return {
            "skills_analysis": analysis_content,
            "suitability_score": 80,  # Example score
            "key_strengths": ["Technical Expertise", "Experience"],
            "analysis_status": "completed"
        }
