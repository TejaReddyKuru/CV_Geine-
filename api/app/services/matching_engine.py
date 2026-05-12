import os
import openai
import numpy as np
import json
from typing import List
from dotenv import load_dotenv

load_dotenv()

# Configure xAI (Grok) - Compatible with OpenAI SDK
def get_xai_client():
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        return None
    return openai.OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1"
    )

xai_client = get_xai_client()

# xAI Model
MODEL = "grok-beta"

class MatchingEngine:
    @staticmethod
    def calculate_match(jd_text: str, resume_text: str) -> float:
        """
        Calculates similarity using Groq-managed Llama3 model.
        """
        prompt = f"""
        Analyze the Job Description (JD) and Resume below.
        Return ONLY a numerical match percentage (0-100) based on skills and experience matching.
        
        JD: {jd_text[:1500]}
        Resume: {resume_text[:1500]}
        
        Return Example: 85.5
        """
        try:
            if not xai_client:
                raise ValueError("XAI_API_KEY is not set")
            response = xai_client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            score_text = response.choices[0].message.content.strip()
            # Clean non-numeric
            return float("".join(c for c in score_text if c.isdigit() or c == "."))
        except Exception as e:
            print(f"xAI Match Error: {e}")
            return 50.0

    @classmethod
    def analyze_gap_with_gpt(cls, jd_text: str, resume_text: str) -> dict:
        """Use Groq Llama3 to perform deep analysis of missing skills and suggestions."""
        prompt = f"""
        Analyze current resume against this Job Description (JD).
        
        Job Description: {jd_text[:2000]}
        Resume Content: {resume_text[:2000]}
        
        RETURN A STRICT JSON OBJECT ONLY:
        {{
            "missing_skills": ["skill1", "skill2"],
            "suggestions": ["improvement1", "improvement2"],
            "formatting_tips": ["tip1", "tip2"],
            "ats_score": 0-100
        }}
        """
        try:
            if not xai_client:
                raise ValueError("XAI_API_KEY is not set")
            response = xai_client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are an ATS Match analyzer. Only respond in JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
             print(f"xAI Analysis Error: {e}")
             return {
                 "missing_skills": [f"Error: {str(e)}"],
                 "suggestions": ["Check your xAI API status"], 
                 "formatting_tips": [], "ats_score": 0
             }
