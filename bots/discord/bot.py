import discord
from discord.ext import commands
import os
import aiohttp
import io
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")

@bot.command()
async def analyze(ctx):
    """
    Command: !analyze
    Expected: Send command and attach TWO files (JD and Resume)
    Alternative: Paste JD text in message and attach Resume.
    """
    attachments = ctx.message.attachments
    if len(attachments) < 1:
        await ctx.send("Please attach at least your Resume (PDF/DOCX).")
        return

    # Handle Attachments logic
    jd_file = None
    resume_file = None
    jd_text = None

    if len(attachments) >= 2:
        jd_file = attachments[0]
        resume_file = attachments[1]
    else:
        # Use message content as JD if no 2nd attachment
        resume_file = attachments[0]
        # Clean text by removing command
        cleaned_msg = ctx.message.content.replace("!analyze", "").strip()
        if cleaned_msg:
            jd_text = cleaned_msg
        else:
            await ctx.send("Please provide JD as text or attach two files (JD and Resume).")
            return

    await ctx.send("Analyzing... please wait. 🚀")

    async with aiohttp.ClientSession() as session:
        form = aiohttp.FormData()
        
        # Add Resume
        resume_bytes = await resume_file.read()
        form.add_field('resume_file', resume_bytes, filename=resume_file.filename)

        # Add JD (Text or File)
        if jd_text:
            form.add_field('jd_text', jd_text)
        elif jd_file:
            jd_bytes = await jd_file.read()
            form.add_field('jd_file', jd_bytes, filename=jd_file.filename)

        try:
            async with session.post(f"{API_BASE_URL}/analyze", data=form) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    embed = discord.Embed(title="Resume Analysis Results", color=discord.Color.green())
                    embed.add_field(name="Match Score", value=f"{data['score']}/100", inline=True)
                    embed.add_field(name="ATS Score", value=f"{data['ats_score']}/100", inline=True)
                    embed.add_field(name="Missing Skills", value="\n• " + "\n• ".join(data['missing_skills'][:5]), inline=False)
                    embed.add_field(name="Suggestions", value="\n• " + "\n• ".join(data['suggestions'][:3]), inline=False)
                    
                    await ctx.send(embed=embed)

                    # Send the improved resume file
                    async with session.get(data['improved_resume_url']) as pdf_res:
                        if pdf_res.status == 200:
                            pdf_bytes = await pdf_res.read()
                            pdf_file = discord.File(io.BytesIO(pdf_bytes), filename="Improved_Resume.pdf")
                            await ctx.send("Here is your optimized resume!", file=pdf_file)
                else:
                    await ctx.send(f"Server Error: {await response.text()}")
        except Exception as e:
            await ctx.send(f"Error connecting to backend: {str(e)}")

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Missing DISCORD_BOT_TOKEN in .env")
