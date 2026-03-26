import os
import openai
import json
from dotenv import load_dotenv

load_dotenv()

# Configure Groq (Compatible with OpenAI SDK)
groq_client = openai.OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Groq Model
MODEL = "llama-3.3-70b-versatile"

class ResumeRewriter:
    @staticmethod
    def rewrite_content(jd_text: str, resume_text: str) -> dict:
        """Use Groq Llama3 to rewrite current resume to better match JD."""
        
        prompt = f"""
        Rewrite current Resume following specific Job Description (JD). 
        
        System Rules:
        1. Maintain user identity (Keep name, contact, Education details 100% same).
        2. Improve wording to use high-impact action verbs.
        3. Quantify achievements.
        4. Integrate missing JD keywords naturally.
        5. Structure as clear Resume sections: Summary, Skills, Experience, Projects.
        
        Job Description:
        {jd_text[:3000]}
        
        Resume Content:
        {resume_text[:3000]}
        
        Return re-written resume as structured JSON:
        {{
            "summary": "Full summary text...",
            "skills": ["Skill 1", "Skill 2"],
            "experience": [
                {{
                    "role": "Title",
                    "company": "Company",
                    "bullets": ["Bullet 1", "Bullet 2"]
                }}
            ],
            "projects": [
                {{
                    "name": "Project name",
                    "description": "Short description",
                    "bullets": ["Bullet 1", "Bullet 2"]
                }}
            ]
        }}
        """
        try:
            response = groq_client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional resume writer specializing in ATS optimization. Only respond in JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Groq Rewrite Error: {e}")
            return {
                "summary": "Error during rewrite", 
                "skills": [], "experience": [], "projects": []
            }
