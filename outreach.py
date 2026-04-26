import google.generativeai as genai
import json
import re
import os

def simulate_outreach(candidate: dict, parsed_jd: dict) -> dict:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")

    profile = candidate.get("profile", {})
    role = parsed_jd.get("role_title", "Software Engineer")

    prompt = f"""Simulate a real recruitment outreach conversation on LinkedIn.

ROLE: {role} | Domain: {parsed_jd.get('domain','tech')} | Mode: {parsed_jd.get('work_mode','Hybrid')} | Skills: {', '.join(parsed_jd.get('required_skills', [])[:6])}

CANDIDATE: {json.dumps(profile, indent=2)}

Write a 4-turn conversation (Recruiter → Candidate → Recruiter → Candidate).
Candidate responds REALISTICALLY based on open_to_new_roles, salary, location.

Return ONLY valid JSON:
{{"conversation": [{{"sender": "Recruiter", "message": "..."}}, {{"sender": "{profile.get('name','Candidate')}", "message": "..."}}, {{"sender": "Recruiter", "message": "..."}}, {{"sender": "{profile.get('name','Candidate')}", "message": "..."}}], "interest_score": 75, "interest_level": "High", "interest_reasoning": "...", "next_action": "...", "engagement_signals": ["..."], "risk_factors": ["..."]}}

interest_level: Very High | High | Moderate | Low | Not Interested"""

    response = model.generate_content(prompt)
    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw.strip())
