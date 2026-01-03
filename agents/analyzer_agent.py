from typing import Dict, Any
from .base_agent import BaseAgent
import ast
from datetime import datetime


class AnalyzerAgent(BaseAgent):
    def __init__(self, provider: str = None, api_key: str = None):
        super().__init__(
            name="Analyzer",
            instructions="""Analyze candidate profiles and extract:
            1. Technical skills (as a list)
            2. Years of experience (numeric)
            3. Education level
            4. Experience level (Junior/Mid-level/Senior)
            5. Key achievements
            6. Domain expertise
            
            Format the output as structured data.""",
            provider=provider,
            api_key=api_key
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Analyze the extracted resume data"""
        print("🔍 Analyzer: Analyzing candidate profile")

        content = messages[-1]["content"]
        try:
             extracted_data = ast.literal_eval(content) if isinstance(content, str) else content
        except (ValueError, SyntaxError):
             extracted_data = {}

        # Get structured analysis from Ollama
        analysis_prompt = f"""
        Strictly analyze and categorize the following resume data.
        
        Data Sources:
        1. Raw Text: {extracted_data.get("raw_text", "")[:2000]}
        2. Structured Bits: {extracted_data.get("structured_data", "")}
        3. Enhanced Signal: {extracted_data.get("enhanced_data", "")}

        Task: Return a JSON object representing the candidate's professional profile.
        
        Validation Rules:
        - technical_skills: List specific hard skills found.
        - years_of_experience: Total years across all roles (integer).
        - education: Must contain level (e.g. Masters) and field.
        - experience_level: Determine correctly (Junior < 3y, Mid 3-7y, Senior > 7y).
        - key_achievements: Concrete results from jobs.

        Structure:
        {{
            "technical_skills": ["skill1", "skill2"],
            "years_of_experience": number,
            "education": {{
                "level": "Bachelors/Masters/PhD",
                "field": "field of study"
            }},
            "experience_level": "Junior/Mid-level/Senior",
            "key_achievements": ["achievement1", "achievement2"],
            "domain_expertise": ["domain1", "domain2"]
        }}

        Return ONLY the JSON object, no other text.
        """

        analysis_results = self._query_ollama(analysis_prompt)
        parsed_results = self._parse_json_safely(analysis_results)

        # Ensure we have valid data even if parsing fails
        if "error" in parsed_results:
            parsed_results = {
                "technical_skills": [],
                "years_of_experience": 0,
                "education": {"level": "Unknown", "field": "Unknown"},
                "experience_level": "Junior",
                "key_achievements": [],
                "domain_expertise": [],
            }

        return {
            "skills_analysis": parsed_results,
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d"),
            "confidence_score": 0.85 if "error" not in parsed_results else 0.5,
        }


# from typing import Dict, Any
# from .base_agent import BaseAgent


# class AnalyzerAgent(BaseAgent):
#     def __init__(self):
#         super().__init__(
#             name="Analyzer",
#             instructions="""Analyze candidate profiles for:
#             1. Key skills and expertise level
#             2. Years of experience
#             3. Educational qualifications
#             4. Career progression
#             5. Potential red flags
#             Provide detailed analysis with specific observations.""",
#         )

#     async def run(self, messages: list) -> Dict[str, Any]:
#         """Analyze the extracted resume data"""
#         print("🔍 Analyzer: Analyzing candidate profile")

#         extracted_data = eval(messages[-1]["content"])
#         analysis_results = self._query_ollama(str(extracted_data["structured_data"]))

#         return {
#             "skills_analysis": analysis_results,
#             "analysis_timestamp": "2024-03-14",
#             "confidence_score": 0.85,
#         }