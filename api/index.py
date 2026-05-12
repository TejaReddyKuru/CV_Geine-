from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
import shutil
from dotenv import load_dotenv

# Import our custom logic
from app.utils.text_extractor import TextExtractor
from app.services.matching_engine import MatchingEngine
from app.services.resume_rewriter import ResumeRewriter
from app.services.pdf_generator import resumePDFGenerator
from app.services.report_generator import MatchReportGenerator
from app.routes.whatsapp_handler import router as whatsapp_router

load_dotenv()

app = FastAPI(title="Resume Matcher & Optimizer API")
app.include_router(whatsapp_router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOADS_DIR = "/tmp" if os.getenv("VERCEL") else os.getenv("UPLOADS_DIR", "./backend/uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "CV Genie API is running"}

@app.post("/analyze")
async def analyze_resume(
    request: Request,
    jd_text: str = Form(None),
    jd_file: UploadFile = File(None),
    resume_file: UploadFile = File(...)
):
    """
    Core endpoint to analyze JD similarity and generate improved resume.
    """
    job_description = ""
    # 1. Process JD (Text or File)
    if jd_text:
        job_description = jd_text
    elif jd_file:
        content = await jd_file.read()
        job_description = TextExtractor.extract(content, jd_file.filename)
    else:
        raise HTTPException(status_code=400, detail="Missing Job Description (JD)")

    # 2. Process Resume
    resume_content = await resume_file.read()
    resume_text = TextExtractor.extract(resume_content, resume_file.filename)

    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract text from Resume")

    try:
        # 3. Perform Analysis
        score = MatchingEngine.calculate_match(job_description, resume_text)
        analysis = MatchingEngine.analyze_gap_with_gpt(job_description, resume_text)
        
        # 4. Generate Improved Resume Content
        improved_json = ResumeRewriter.rewrite_content(job_description, resume_text)
        
        # 5. Generate PDFs
        unique_id = str(uuid.uuid4())
        
        # Improved Resume PDF
        resume_filename = f"improved_resume_{unique_id}.pdf"
        resume_path = resumePDFGenerator.generate(improved_json, resume_filename)
        
        # Analysis Report PDF
        report_filename = f"match_report_{unique_id}.pdf"
        report_path = MatchReportGenerator.generate(analysis, score, report_filename)
        
        # 6. Response
        base_url = str(request.base_url).rstrip("/")
        # On Vercel, base_url might be different depending on how it's called
        download_url = f"{base_url}/download/{resume_filename}"
        report_url = f"{base_url}/download/{report_filename}"

        return {
            "score": score,
            "missing_skills": analysis.get("missing_skills", []),
            "suggestions": analysis.get("suggestions", []),
            "formatting_tips": analysis.get("formatting_tips", []),
            "ats_score": analysis.get("ats_score", 0),
            "improved_resume_url": download_url,
            "match_report_url": report_url
        }

    except Exception as e:
        print(f"Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_resume(filename: str):
    """Serve the generated PDF file."""
    path = os.path.join(UPLOADS_DIR, filename)
    if os.path.exists(path):
        return FileResponse(path, media_type="application/pdf", filename="Improved_Resume.pdf")
    raise HTTPException(status_code=404, detail="File not found")

# Main entry point for uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
