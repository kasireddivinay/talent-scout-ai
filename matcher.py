import google.generativeai as genai
import json
import re
import os
from candidates import CANDIDATE_POOL

def discover_and_match_candidates(parsed_jd: dict, top_n: int = 8) -> list:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")

    compact_candidates = []
    for c in CANDIDATE_POOL:
        compact_candidates.append({
            "id": c["id"], "name": c["name"], "title": c["title"],
            "experience_years": c["experience_years"], "skills": c["skills"],
            "location": c["location"], "work_mode_preference": c["work_mode_preference"],
            "current_company": c["current_company"], "education": c["education"],
            "availability": c["availability"], "salary_expectation": c["salary_expectation"],
            "open_to_new_roles": c["open_to_new_roles"], "bio": c["bio"],
        })

    prompt = f"""You are an expert technical recruiter. Score every candidate against the job requirements.

JOB REQUIREMENTS:
{json.dumps(parsed_jd, indent=2)}

CANDIDATE POOL:
{json.dumps(compact_candidates, indent=2)}

Scoring weights: Skills overlap 40%, Experience fit 25%, Domain fit 20%, Logistics 15%.

Return a JSON ARRAY of ALL {len(compact_candidates)} candidates sorted by match_score descending:
[{{"id": "C001", "name": "...", "match_score": 85, "match_grade": "Excellent", "matched_skills": ["Python"], "missing_critical_skills": [], "match_reasoning": "2-3 sentence explanation.", "red_flags": [], "logistics_note": "..."}}]

match_grade: Excellent(85-100) Strong(70-84) Good(55-69) Fair(40-54) Weak(<40)
Return ONLY valid JSON array, no markdown."""

    response = model.generate_content(prompt)
    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    results = json.loads(raw.strip())

    candidate_map = {c["id"]: c for c in CANDIDATE_POOL}
    for r in results:
        r["profile"] = candidate_map.get(r["id"], {})
    return results[:top_n]
