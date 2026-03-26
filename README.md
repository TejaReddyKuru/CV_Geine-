# Resume-JD Matcher & Optimizer Tool 🚀

A multi-platform system (Telegram, Discord, WhatsApp) powered by AI (OpenAI GPT-4o & Embeddings) to analyze resumes against job descriptions, provide detailed insights, and generate an ATS-optimized resume.

## 🛠️ Tech Stack
- **Backend:** FastAPI, OpenAI API, ReportLab (PDF), pdfplumber.
- **Telegram Bot:** `python-telegram-bot`
- **Discord Bot:** `discord.py`
- **WhatsApp:** Twilio API (FastAPI Webhooks)

---

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.9+
- OpenAI API Key
- Telegram Token (via @BotFather)
- Discord Token (via Discord Developer Portal)
- Twilio Account (for WhatsApp)

### 2. Environment Setup
Clone this repository and create a `.env` file based on `.env.example`:
```env
OPENAI_API_KEY=your_key
TELEGRAM_BOT_TOKEN=your_token
DISCORD_BOT_TOKEN=your_token
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
BASE_URL=http://your-server-ip:8000
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Backend
```bash
cd backend
python main.py
```
*Note: Make sure your `BASE_URL` is accessible if testing bots remotely (e.g., use `ngrok` for local development).*

### 5. Run the Bots
In separate terminals:
```bash
# Telegram
python bots/telegram/bot.py

# Discord
python bots/discord/bot.py
```

---

## 📂 Project Structure
```
/backend
  /app
    /core           - Configuration
    /services       - Matching Engine, AI Analyzer, PDF Generator
    /utils          - File parsers (PDF/DOCX)
    /routes         - WhatsApp Webhook
  main.py           - FastAPI app
/bots
  /telegram         - Telegram Bot logic
  /discord          - Discord Bot logic
.env                - API Keys
requirements.txt    - Python packages
```

---

## 🤖 Bot Usage
- **Telegram:** Send `/start` and follow the flow (Send JD -> Upload Resume).
- **Discord:** Use `!analyze` command. Either attach two files (JD and Resume) OR paste the JD text in the message and attach the Resume.
- **WhatsApp:** Send "Hi" to your Twilio number. Follow the text prompts to provide JD and Resume.

---

## 🔐 Security & Scaling
- Ensure `UPLOADS_DIR` has appropriate write permissions.
- In production, use **PostgreSQL/Redis** for WhatsApp session state instead of the current in-memory `user_state` dictionary.
- Use **Celery/Redis** for background processing if handling numerous concurrent file analyses.

Developed with ❤️ using AI.
