import asyncio
import json
from agents.matcher_agent import MatcherAgent
from agents.market_intelligence_agent import MarketIntelligenceAgent
from agents.candidate_advisor_agent import CandidateAdvisorAgent
from config import Config

async def test_backend_features():
    print("🧪 Starting Phase 1 & 2 Verification...")
    
    # 1. Test Configuration Loading
    print("\n[1/4] Testing Configuration...")
    try:
        agent = MatcherAgent(provider="ollama")
        assert agent.provider == "ollama"
        print("✅ Provider configuration works (Ollama default)")
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")

    # 2. Test Market Intelligence (Live Data)
    print("\n[2/4] Testing Market Intelligence Agent (DuckDuckGo + LLM)...")
    try:
        market_agent = MarketIntelligenceAgent(provider="ollama")
        # specific inputs to test search
        market_input = [{"content": {"role": "Python Developer", "skills": ["Django", "FastAPI"]}}]
        
        market_result = await market_agent.run(market_input)
        
        jobs = market_result.get("market_jobs", [])
        if len(jobs) > 0:
            print(f"✅ Market Intelligence generated {len(jobs)} live jobs.")
            print(f"   Sample: {jobs[0]['title']} at {jobs[0]['company']}")
        else:
            print("⚠️ Market Intelligence run returned 0 jobs (Might be search blocking or LLM failure).")
            print(f"   Raw Result: {market_result}")
    except Exception as e:
        print(f"❌ Market Intelligence test failed: {e}")

    # 3. Test Hybrid Matcher (DB + Live)
    print("\n[3/4] Testing Hybrid Matcher Agent...")
    try:
        matcher = MatcherAgent(provider="ollama")
        # inputs simulating previous analyzer step
        matcher_input = [{"content": json.dumps({
            "skills_analysis": {
                "technical_skills": ["Python", "SQL", "Streamlit"],
                "experience_level": "Mid-level"
            }
        })}]
        
        match_result = await matcher.run(matcher_input)
        matched_jobs = match_result.get("matched_jobs", [])
        
        sources = [job.get("source", "Unknown") for job in matched_jobs]
        print(f"✅ Matcher returned {len(matched_jobs)} jobs.")
        print(f"   Sources found: {set(sources)}")
        
        if "Live Market 🌐" in sources:
            print("✅ Live Market jobs successfully integrated!")
        else:
            print("⚠️ No Live Market jobs found in final match list (Check scoring?).")
            
    except Exception as e:
        print(f"❌ Matcher test failed: {e}")

    # 4. Test Candidate Advisor
    print("\n[4/4] Testing Candidate Advisor Agent...")
    try:
        advisor = CandidateAdvisorAgent(provider="ollama")
        advisor_input = [{"content": {
            "skills": ["Python", "SQL"],
            "experience": "2 years",
            "goal": "Senior Developer"
        }}]
        
        advice = await advisor.run(advisor_input)
        if "actionable_tips" in advice:
             print("✅ Advisor generated actionable tips.")
             print(f"   Tip: {advice['actionable_tips'][0]}")
        else:
             print("❌ Advisor output format incorrect.")
             
    except Exception as e:
        print(f"❌ Advisor test failed: {e}")

    print("\n🎉 Verification Complete!")

if __name__ == "__main__":
    asyncio.run(test_backend_features())
