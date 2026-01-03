import os
import shutil
import logging
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Agents
from agents.extractor_agent import ExtractorAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.matcher_agent import MatcherAgent
from agents.candidate_advisor_agent import CandidateAdvisorAgent

# Config
from config import Config

# Setup
app = FastAPI(title="AI Recruiter - Candidate View")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Ensure uploads dir
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the Candidate Portal Home"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    nebius_key: Optional[str] = Form(None)
):
    """
    Process resume with optional Nebius API Key.
    Returns: Analysis, Advice, and Matches.
    """
    temp_path = UPLOAD_DIR / file.filename
    try:
        # 1. Determine Provider
        provider = "nebius" if nebius_key else "ollama"
        api_key = nebius_key if nebius_key else "ollama"
        
        logger.info(f"Processing candidate resume using {provider}...")

        # 2. Save File Temporarily
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 3. Pipeline Execution
        
        # Step A: Extraction
        extractor = ExtractorAgent(provider=provider, api_key=api_key)
        extraction_res = await extractor.run([{"content": {"file_path": str(temp_path)}}])
        
        if extraction_res.get("extraction_status") == "failed":
            return {"error": "Failed to extract text from PDF."}

        # Step B: Profile Enhancement (New!)
        enhancer = ProfileEnhancerAgent(provider=provider, api_key=api_key)
        enhanced_data = await enhancer.run([{"content": str(extraction_res.get("structured_data", "")) }])
        
        # Step C: Analysis
        analyzer = AnalyzerAgent(provider=provider, api_key=api_key)
        # Pass both raw text and enhanced data for better context
        analysis_input = {
            "raw_text": extraction_res.get("raw_text", ""),
            "enhanced_data": enhanced_data,
            "structured_data": extraction_res.get("structured_data", "")
        }
        analysis_res = await analyzer.run([{"content": str(analysis_input)}])
        structured_data = analysis_res.get("skills_analysis", {})

        # Step D: Matching (Hybrid: DB + Live)
        matcher = MatcherAgent(provider=provider, api_key=api_key)
        matcher_res = await matcher.run([{"content": analysis_res}])
        
        # Step E: Advice
        advisor = CandidateAdvisorAgent(provider=provider, api_key=api_key)
        advice_res = await advisor.run([{"content": structured_data}])

        # 4. Construct Response
        return {
            "status": "success",
            "provider_used": provider,
            "profile": structured_data,
            "jobs": matcher_res.get("matched_jobs", []),
            "advice": advice_res  
        }

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return {"error": str(e), "status": "failed"}
    
    finally:
        # Cleanup
        if temp_path.exists():
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("candidate_app:app", host="0.0.0.0", port=8000, reload=True)
