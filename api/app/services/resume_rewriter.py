import os
import openai
import json
from dotenv import load_dotenv

load_dotenv()

# Configure xAI (Grok) - Compatible with OpenAI SDK
xai_client = openai.OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

# xAI Model
MODEL = "grok-beta"

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
            response = xai_client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional resume writer specializing in ATS optimization. Only respond in JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"xAI Rewrite Error: {e}")
            return {
                "summary": "Error during rewrite", 
                "skills": [], "experience": [], "projects": []
            }
