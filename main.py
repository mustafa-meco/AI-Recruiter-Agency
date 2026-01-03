import os
import shutil
import logging
from typing import Optional, List
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
from agents.profile_enhancer_agent import ProfileEnhancerAgent
from agents.screener_agent import ScreenerAgent
from agents.recommender_agent import RecommenderAgent
from agents.orchestrator import OrchestratorAgent

# Config
from config import Config

# Database
from db.database import JobDatabase

# Setup
app = FastAPI(title="AI Recruiter Agency - Unified Platform")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Ensure uploads dir
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# --- CANDIDATE PORTAL ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def read_candidate_root(request: Request):
    """Serve the Candidate Portal Home"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/candidate/analyze")
async def analyze_candidate_resume(
    file: UploadFile = File(...),
    nebius_key: Optional[str] = Form(None)
):
    """
    Process resume for Candidate View (Focus on Advice & Matches).
    """
    temp_path = UPLOAD_DIR / f"candidate_{file.filename}"
    try:
        # Determine Provider
        provider = "nebius" if nebius_key else Config.DEFAULT_PROVIDER
        api_key = nebius_key
        
        logger.info(f"Processing candidate resume using {provider}...")

        # Save File
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Pipeline Execution (Candidate Flow)
        extractor = ExtractorAgent(provider=provider, api_key=api_key)
        extraction_res = await extractor.run([{"content": {"file_path": str(temp_path)}}])
        
        if extraction_res.get("extraction_status") == "failed":
            return {"error": "Failed to extract text from PDF."}

        # Profile Enhancement
        enhancer = ProfileEnhancerAgent(provider=provider, api_key=api_key)
        enhanced_data = await enhancer.run([{"content": str(extraction_res.get("structured_data", "")) }])
        
        # Analysis
        analyzer = AnalyzerAgent(provider=provider, api_key=api_key)
        analysis_input = {
            "raw_text": extraction_res.get("raw_text", ""),
            "enhanced_data": enhanced_data,
            "structured_data": extraction_res.get("structured_data", "")
        }
        analysis_res = await analyzer.run([{"content": str(analysis_input)}])
        structured_data = analysis_res.get("skills_analysis", {})

        # Matching
        matcher = MatcherAgent(provider=provider, api_key=api_key)
        matcher_res = await matcher.run([{"content": analysis_res}])
        
        # Advice
        advisor = CandidateAdvisorAgent(provider=provider, api_key=api_key)
        advice_res = await advisor.run([{"content": structured_data}])

        return {
            "status": "success",
            "provider_used": provider,
            "profile": structured_data,
            "jobs": matcher_res.get("matched_jobs", []),
            "advice": advice_res  
        }

    except Exception as e:
        logger.error(f"Candidate Analysis failed: {e}")
        return {"error": str(e), "status": "failed"}
    
    finally:
        if temp_path.exists():
            os.remove(temp_path)


# --- RECRUITER DASHBOARD ROUTES ---

@app.get("/recruiter", response_class=HTMLResponse)
async def read_recruiter_root(request: Request):
    """Serve the Recruiter Dashboard"""
    return templates.TemplateResponse("recruiter_dashboard.html", {"request": request})

@app.get("/api/recruiter/candidates")
async def get_candidates():
    """Retrieve all processed candidates from database"""
    try:
        db = JobDatabase()
        candidates = db.get_all_candidates()
        return {"status": "success", "results": candidates}
    except Exception as e:
        logger.error(f"Error retrieving candidates: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/recruiter/sync_resumes")
async def sync_local_resumes(nebius_key: Optional[str] = Form(None)):
    """
    Scans the 'resumes/' folder and processes any new PDF files found there.
    """
    RESUME_FOLDER = Path("resumes")
    RESUME_FOLDER.mkdir(exist_ok=True)
    
    files = list(RESUME_FOLDER.glob("*.pdf"))
    if not files:
        return {"status": "success", "message": "No resumes found in folder.", "results": []}

    results = []
    # Determine Provider
    provider = "nebius" if nebius_key else Config.DEFAULT_PROVIDER
    orchestrator = OrchestratorAgent(provider=provider, api_key=nebius_key)
    
    db = JobDatabase()
    for file_path in files:
        try:
            # 1. Check for duplicate based on Filename FIRST
            existing_candidates = db.get_all_candidates()
            is_file_duplicate = False
            uploaded_filename = file_path.name.lower().strip()
            
            logger.info(f"Checking for duplicates for: {uploaded_filename}")
            
            for cand in existing_candidates:
                db_filename = cand["filename"].lower().strip()
                # logger.info(f"Comparing against DB file: {db_filename}") # Verbose logging
                if db_filename == uploaded_filename:
                     is_file_duplicate = True
                     logger.info(f"FOUND DUPLICATE: {file_path.name} matches {cand['filename']}")
                     break
            
            if is_file_duplicate:
                logger.info(f"Skipping duplicate file: {file_path.name}")
                continue

            logger.info(f"Syncing local resume: {file_path.name}")
            
            # 2. Run Orchestrator
            resume_data = {
                "file_path": str(file_path),
                "filename": file_path.name
            }
            result = await orchestrator.process_application(resume_data)
            
            # 3. Robust Name Extraction
            extraction_results = result.get("extraction_results", {})
            structured_data = extraction_results.get("structured_data", {})
            personal = structured_data.get("Personal Info") or structured_data.get("personal_info") or {}
            
            if isinstance(personal, list) and len(personal) > 0: personal = personal[0]
            
            candidate_name = (
                personal.get("Name") or 
                personal.get("name") or 
                personal.get("Full Name") or 
                personal.get("full_name") or
                file_path.stem
            )
            
            # 4. Prepare and Save
            summary = {
                "filename": file_path.name,
                "name": str(candidate_name),
                "email": personal.get("Email") or personal.get("email"),
                "phone": personal.get("Phone") or personal.get("phone"),
                "score": result.get("screening_results", {}).get("screening_score", 0),
                "recommendation": result.get("final_recommendation", {}).get("recommendation", "N/A"),
                "full_report": result,
                "status": "Analyzed"
            }
            
            db.add_candidate(summary)
            results.append(summary)
            
            logger.info(f"Result for {file_path.name}: Name={candidate_name}, Score={summary['score']}")

        except Exception as e:
            logger.error(f"Sync failed for {file_path.name}: {e}")
            results.append({"filename": file_path.name, "status": "Failed", "error": str(e)})

    return {"status": "success", "results": results}

@app.post("/api/recruiter/upload")
async def batch_upload_resumes(
    files: List[UploadFile] = File(...),
    nebius_key: Optional[str] = Form(None)
):
    """
    Handle bulk upload for recruiter.
    """
    results = []
    # Determine Provider
    provider = "nebius" if nebius_key else Config.DEFAULT_PROVIDER
    orchestrator = OrchestratorAgent(provider=provider, api_key=nebius_key)
    
    db = JobDatabase()
    
    for file in files:
        try:
            logger.info(f"Processing batch upload: {file.filename}")
            # Save file
            temp_path = UPLOAD_DIR / file.filename
            with open(temp_path, "wb") as buffer:
                buffer.write(await file.read())
            
            # Run Orchestrator
            resume_data = {
                "file_path": str(temp_path),
                "filename": file.filename
            }
            result = await orchestrator.process_application(resume_data)
            
            # Robust Name Extraction
            extraction_results = result.get("extraction_results", {})
            structured_data = extraction_results.get("structured_data", {})
            personal = structured_data.get("Personal Info") or structured_data.get("personal_info") or {}
            if isinstance(personal, list) and len(personal) > 0: personal = personal[0]
            
            candidate_name = (
                personal.get("Name") or 
                personal.get("name") or 
                personal.get("Full Name") or 
                personal.get("full_name") or
                file.filename
            )
            
            summary = {
                "filename": file.filename,
                "name": str(candidate_name),
                "email": personal.get("Email") or personal.get("email"),
                "phone": personal.get("Phone") or personal.get("phone"),
                "score": result.get("screening_results", {}).get("screening_score", 0),
                "recommendation": result.get("final_recommendation", {}).get("recommendation", "N/A"),
                "full_report": result,
                "status": "Analyzed"
            }
            
            # Save to DB
            db.add_candidate(summary)
            results.append(summary)
            
            logger.info(f"Upload Result for {file.filename}: Name={candidate_name}, Score={summary['score']}")

        except Exception as e:
            logger.error(f"Batch upload failed for {file.filename}: {e}")
            results.append({"filename": file.filename, "status": "Failed", "error": str(e)})
        finally:
            if temp_path.exists():
                os.remove(temp_path)
                
    return {"results": results}



if __name__ == "__main__":
    import uvicorn
    # Clean up old port usage if needed
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



# Validated by QA - Final 2
