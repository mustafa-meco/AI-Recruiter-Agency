from datetime import datetime
from typing import Dict, Any
from .base_agent import BaseAgent

class MatcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Matcher",
            instructions="""Match candidate profiles with job positions.
            Consider: skills match, experience level, location preferences.
            Provide detailed resoning and compatibility scores.
            Return matches in JSON format with title, match_score, and location fields. 
            """
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Match the candidate profile with job positions"""
        print("Matcher: Identifying job matches")

        analysis_results = eval(messages[-1]['content'])

        sample_jobs = [
            {
                "title": "Senior Software Engineer",
                "requirements": "Python, Cloude, 5+ years experience",
                "location": "Remote",
            },
            {
                "title": "Data Engineer",
                "requirements": "Python, Cloude, 5+ years experience",
                "location": "Remote",
            },
            {
                "title": "Data Scientist",
                "requirements": "Python, ML, Statistics, 6+ years experience",
                "location": "Cairo",
            },

        ]
        
        matching_response = self._query_ollama(
            f"""Analyze the following profile and provide job matches in valide JSON format:
            Profile: {analysis_results['skills_analysis']}
            Available Jobs: {sample_jobs}
            
            Return ONLY a JSON object with this exact structure:
            {{
                "matched_jobs": [
                    {{
                        "title": "job title",
                        "match_score": "85%",
                        "location": "job location"
                    }}
                ],
                "match_timestamp": {datetime.now().strftime("%Y-%m-%d")},
                "number_of_matches": 2
            }}
            """
        )

        # Parse the response
        parsed_response = self._parse_json_safely(matching_response)

        # Fallback to sample data if parsing fails
        if not parsed_response or "error" in parsed_response:
            parsed_response = {
                "matched_jobs": [
                    {
                        "title": "Senior Software Engineer",
                        "match_score": "85%",
                        "location": "Remote"
                    },
                    {
                        "title": "Data Scientist",
                        "match_score": "85%",
                        "location": "Cairo"
                    },
                ],
                "match_timestamp": datetime.now().strftime("%Y-%m-%d"),
                "number_of_matches": 2
            }
        
        return parsed_response