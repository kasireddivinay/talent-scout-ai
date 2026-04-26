import google.generativeai as genai
import json
import re
import os

def parse_job_description(jd_text: str) -> dict:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""You are an expert HR analyst. Parse the following job description and extract structured information.

Job Description:
{jd_text}

Return a JSON object with EXACTLY these fields:
{{
    "role_title": "string",
    "seniority": "Junior | Mid | Senior | Lead | Principal | Manager",
    "required_skills": ["skill1", "skill2"],
    "nice_to_have_skills": ["skill1", "skill2"],
    "experience_min": 0,
    "experience_max": 0,
    "location": "City, Country or Remote",
    "work_mode": "Remote | Hybrid | Onsite",
    "domain": "e.g. FinTech, HealthTech, E-commerce, SaaS, AI/ML",
    "key_responsibilities": ["responsibility1", "responsibility2"],
    "company_description": "brief summary if available, else null",
    "salary_range": "string or null",
    "team_size": "string or null"
}}

Return ONLY valid JSON, no markdown fences, no explanation."""

    response = model.generate_content(prompt)
    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw.strip())
