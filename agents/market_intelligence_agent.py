from typing import Dict, Any, List
from .base_agent import BaseAgent
from duckduckgo_search import DDGS
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MarketIntelligenceAgent(BaseAgent):
    def __init__(self, provider: str = None, api_key: str = None):
        super().__init__(
            name="MarketIntelligence",
            instructions="""You are a Market Intelligence Expert. 
            Your goal is to analyze real-time job market trends and generate REALISTIC, up-to-date job listings.
            
            Input: A candidate's role and top skills.
            Context: Real-world search snippets about current hiring trends for this role.
            
            Task:
            1. Analyze the search snippets to understand what skills/roles are in high demand RIGHT NOW.
            2. Generate 3-5 "Live" Job Listings that match these trends.
            3. The output MUST be a JSON object with a key "market_jobs" containing a list of jobs.
            
            Job Format:
            {
                "title": "Job Title",
                "company": "Company Name (Real or Realistic Tech Co)",
                "location": "Location (Remote/Tech Hub)",
                "salary_range": "$X - $Y",
                "requirements": ["Skill1", "Skill2", ...],
                "description": "Brief exciting description reflecting current trends."
            }
            """,
            provider=provider,
            api_key=api_key
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """
        Analyze markets and generate live jobs.
        Expected message format: {"role": "Python Developer", "skills": ["Django", "AWS"]}
        """
        print("🌐 MarketIntelligence: Scanning live job market...")
        
        # Parse input
        content = messages[-1].get("content", {})
        if isinstance(content, str):
            try:
                data = json.loads(content)
            except:
                data = {"role": "General", "skills": []}
        else:
            data = content
            
        role = data.get("role", "Software Engineer")
        skills = data.get("skills", [])
        
        # 1. Fetch real-world market signals
        market_signals = self._fetch_search_results(f"{role} hiring trends skills {datetime.now().year} {datetime.now().year+1}")
        
        # 2. Synthesize into fake-but-realistic jobs
        context_str = json.dumps(market_signals[:3])
        
        if market_signals and market_signals[0]["title"] == "General Market":
             # Fallback Prompt for Offline Mode
             print("⚠️ Search failed/offline. Generating simulated market data based on general knowledge.")
             prompt = f"""
             You are a Market Intelligence Expert. The live search is unavailable.
             Generate 3 REALISTIC, 'Live' job listings for a '{role}' role based on your general knowledge of the current tech market.
             
             Skills to include: {', '.join(skills)}
             
             Return ONLY a JSON object with this key: "market_jobs": [job1, job2, job3]
             """
        else:
             # Standard Prompt with Search Context
             prompt = f"""
             Role: {role}
             Top Skills: {', '.join(skills)}
             
             Real-world Market Signals (Search Results):
             {context_str} 
             
             Based on these signals, generate 3 highly relevant 'Live' job listings that a candidate with these skills might see today.
             Make them look distinct from generic simulated data. Use specific, modern terminology found in the signals.
             
             Return ONLY a JSON object with this key: "market_jobs": [job1, job2, job3]
             """
        
        response = self._query_llm(prompt)
        parsed = self._parse_json_safely(response)
        
        # Fallback if parsing fails or returns empty
        if "error" in parsed or "market_jobs" not in parsed:
            logger.warning(f"Market Intelligence LLM failed, using fallback: {parsed.get('error')}")
            return {"market_jobs": []}
            
        return parsed

    def _fetch_search_results(self, query: str) -> List[Dict[str, str]]:
        """Fetch snippets from DuckDuckGo"""
        try:
            results = []
            # Suppress/handle the specific warning if needed, but let's try direct usage
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                # Use simplified search
                search_results = ddgs.text(query, max_results=5)
                for r in search_results:
                    results.append({"title": r.get('title', ''), "snippet": r.get('body', '')})
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return [{"title": "General Market", "snippet": "High demand for AI and Cloud skills in 2024."}]
