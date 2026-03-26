from fastapi import APIRouter, Request, Form, BackgroundTasks
from twilio.twiml.messaging_response import MessagingResponse
import requests
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

# Simple memory storage for JD (In production, use Redis/Postgres)
# {whatsapp_number: {"jd_text": "...", "step": "WAITING_FOR_RESUME"}}
user_state = {}

API_BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(None),
    From: str = Form(...),
    NumMedia: int = Form(0)
):
    """
    Handle Incoming WhatsApp messages from Twilio.
    """
    resp = MessagingResponse()
    msg = resp.message()
    
    sender = From # Format: whatsapp:+phoneNumber
    
    state = user_state.get(sender, {"step": "START"})

    if state["step"] == "START":
        msg.body("Hi! Send me the Job Description (JD) text to start matching your resume. 🚀")
        user_state[sender] = {"step": "WAITING_FOR_JD"}
        return str(resp)

    if state["step"] == "WAITING_FOR_JD":
        if not Body:
            msg.body("Please send the Job Description as text first.")
            return str(resp)
        
        user_state[sender]["jd_text"] = Body
        user_state[sender]["step"] = "WAITING_FOR_RESUME"
        msg.body("Great! Now, please **upload your Resume (PDF/DOCX)**. 📄")
        return str(resp)

    if state["step"] == "WAITING_FOR_RESUME":
        # Handle Media
        form_data = await request.form()
        media_url = form_data.get("MediaUrl0")
        media_content_type = form_data.get("MediaContentType0")

        if not media_url:
            msg.body("Please upload a file (PDF/DOCX) for your resume.")
            return str(resp)

        msg.body("Analyzing... please wait. ⏳")
        
        # Download resume from Twilio Media URL
        # Note: Twilio media URLs are protected; a simple requests call might work depending on account settings
        resume_response = requests.get(media_url)
        if resume_response.status_code != 200:
             msg.body("Failed to download your resume file from WhatsApp. ❌")
             return str(resp)

        # Prepare payload for our /analyze endpoint
        async with aiohttp.ClientSession() as session:
             form = aiohttp.FormData()
             form.add_field("jd_text", user_state[sender].get("jd_text", ""))
             form.add_field("resume_file", resume_response.content, filename="resume.pdf") # default extension

             try:
                 async with session.post(f"{API_BASE_URL}/analyze", data=form) as api_res:
                     if api_res.status == 200:
                         data = await api_res.json()
                         
                         analysis_summary = (
                             f"✅ *Analysis Complete!*\n\n"
                             f"📊 *Match Score:* {data['score']}/100\n"
                             f"🎯 *ATS Score:* {data['ats_score']}/100\n\n"
                             f"❌ *Missing Skills:*\n• " + "\n• ".join(data['missing_skills'][:3]) + "\n\n"
                             f"💡 *Download Improved Resume:* {data['improved_resume_url']}"
                         )
                         
                         msg.body(analysis_summary)
                         # Set next step to start over
                         user_state[sender] = {"step": "START"}
                     else:
                         msg.body(f"Error from analysis engine: {await api_res.text()}")
             except Exception as e:
                 msg.body(f"Connection Error: {str(e)}")

    return str(resp)
