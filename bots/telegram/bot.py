import os
import logging
import aiohttp
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv

load_dotenv()

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_JD, WAITING_FOR_RESUME = range(2)

API_BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask for JD."""
    await update.message.reply_text(
        "Hi! I am your AI Resume Matching Bot. 🚀\n\n"
        "Please send me the **Job Description (JD)** as text or upload a PDF/DOCX file.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return WAITING_FOR_JD

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message."""
    await update.message.reply_text("Help: /start to begin analysis. I accept PDF/DOCX files.")

async def handle_jd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store JD and ask for Resume."""
    if update.message.text:
        context.user_data["jd_text"] = update.message.text
        context.user_data["jd_file"] = None
    elif update.message.document:
        doc = update.message.document
        file = await context.bot.get_file(doc.file_id)
        context.user_data["jd_file_content"] = await file.download_as_bytearray()
        context.user_data["jd_filename"] = doc.file_name
        context.user_data["jd_text"] = None
    
    await update.message.reply_text("Great! Now, please **upload your current Resume (PDF/DOCX)**.")
    return WAITING_FOR_RESUME

async def handle_resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send both files to API and return analysis."""
    if not update.message.document:
        await update.message.reply_text("Please upload your resume as a file (PDF or DOCX).")
        return WAITING_FOR_RESUME

    await update.message.reply_text("Analyzing your profile... please wait. ⏳")

    resume_doc = update.message.document
    resume_file = await context.bot.get_file(resume_doc.file_id)
    resume_content = await resume_file.download_as_bytearray()

    # Prepare Multipart Form Data
    form = aiohttp.FormData()
    if context.user_data.get("jd_text"):
        form.add_field('jd_text', context.user_data["jd_text"])
    elif context.user_data.get("jd_file_content"):
         form.add_field('jd_file', context.user_data["jd_file_content"], filename=context.user_data["jd_filename"])
    
    form.add_field('resume_file', resume_content, filename=resume_doc.file_name)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{API_BASE_URL}/analyze", data=form) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Format output using HTML for better stability
                    msg = (
                        f"✅ <b>Analysis Complete!</b>\n\n"
                        f"📊 <b>Match Score:</b> {data['score']}/100\n"
                        f"🎯 <b>ATS Score:</b> {data['ats_score']}/100\n\n"
                        f"❌ <b>Missing Skills:</b>\n" + "\n".join([f"• {s}" for s in data['missing_skills'][:5]]) + "\n\n"
                        f"💡 <b>Key Suggestions:</b>\n" + "\n".join([f"• {s}" for s in data['suggestions'][:3]]) + "\n\n"
                        f"🔽 <b>Download Improved Resume Below</b>"
                    )
                    await update.message.reply_text(msg, parse_mode='HTML')
                    
                    # Send PDF Resume
                    async with session.get(data['improved_resume_url']) as pdf_res:
                        if pdf_res.status == 200:
                            pdf_data = await pdf_res.read()
                            await update.message.reply_document(
                                document=pdf_data, 
                                filename="Improved_Resume.pdf",
                                caption="Here is your optimized resume! 📄"
                            )
                    
                    # Send Match Report PDF
                    if 'match_report_url' in data:
                        async with session.get(data['match_report_url']) as report_res:
                            if report_res.status == 200:
                                report_data = await report_res.read()
                                await update.message.reply_document(
                                    document=report_data,
                                    filename="ATS_Match_Report.pdf",
                                    caption="And here is your detailed ATS Match Report! 📊"
                                )
                else:
                    err = await response.text()
                    await update.message.reply_text(f"❌ Error during analysis: {err}")
        except Exception as e:
            await update.message.reply_text(f"❌ Server Connection Error: {str(e)}")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel and end conversation."""
    await update.message.reply_text("Operation cancelled. Bye!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

import openai

# Initialize Groq for general chat
groq_client = openai.OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

async def general_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle normal chat using Groq."""
    user_msg = update.message.text
    if not user_msg:
        return

    # Typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful AI Career Assistant. You can chat normally but also guide users to use /start for resume analysis."},
                {"role": "user", "content": user_msg}
            ]
        )
        ai_reply = response.choices[0].message.content
        await update.message.reply_text(ai_reply)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        await update.message.reply_text("Sorry, I'm having trouble thinking right now. 🤖")

def main() -> None:
    """Run bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment.")
        return

    application = Application.builder().token(token).build()

    # Analysis Conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("analyze", start), CommandHandler("start", start)],
        states={
            WAITING_FOR_JD: [MessageHandler(filters.TEXT | filters.Document.ALL, handle_jd)],
            WAITING_FOR_RESUME: [MessageHandler(filters.Document.ALL, handle_resume)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    
    # Generic AI Chat (for anything that isn't a command or part of analysis)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, general_chat))

    application.run_polling()

if __name__ == "__main__":
    main()
