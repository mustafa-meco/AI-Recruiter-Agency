import asyncio
import json
from agents.orchestrator import OrchestratorAgent
from db.database import JobDatabase
from db.seed_jobs import seed_jobs

async def test_workflow():
    print("Starting Workflow Test...")
    
    # Ensure DB is seeded
    print("Checking database...")
    db = JobDatabase()
    if not db.get_all_jobs():
        print("Database empty. Seeding initial jobs...")
        seed_jobs()
    else:
        print(f"Database contains {len(db.get_all_jobs())} jobs.")

    orchestrator = OrchestratorAgent()
    
    # Mock resume data
    resume_data = {
        "text": """
        John Doe
        Python Developer
        Experience: 5 years of building web applications with Django and Flask.
        Skills: Python, SQL, Docker, AWS.
        Education: BS in Computer Science.
        """
    }
    
    try:
        print("Processing mock application...")
        result = await orchestrator.process_application(resume_data)
        
        print("\n--- Workflow Results ---")
        print(f"Status: {result.get('status')}")
        print(f"Current Stage: {result.get('current_stage')}")
        
        print("\nFinal Recommendation:")
        print(result.get("recommendations", {}).get("final_recommendation", "N/A"))
        
        print("\nTest Completed Successfully!")
        
    except Exception as e:
        print(f"\nTest Failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_workflow())
