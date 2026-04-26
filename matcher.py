import json, re
from openai import OpenAI
from candidates import CANDIDATE_POOL

def discover_and_match_candidates(parsed_jd, top_n=8):
    client = OpenAI()
    compact = [{"id":c["id"],"name":c["name"],"title":c["title"],"experience_years":c["experience_years"],"skills":c["skills"],"location":c["location"],"work_mode_preference":c["work_mode_preference"],"current_company":c["current_company"],"availability":c["availability"],"salary_expectation":c["salary_expectation"],"open_to_new_roles":c["open_to_new_roles"],"bio":c["bio"]} for c in CANDIDATE_POOL]
    prompt = f"""Score ALL candidates against this job. Return JSON array sorted by match_score desc.
JOB: {json.dumps(parsed_jd)}
CANDIDATES: {json.dumps(compact)}
Format: [{{"id":"C001","name":"...","match_score":85,"match_grade":"Excellent","matched_skills":[],"missing_critical_skills":[],"match_reasoning":"2-3 sentences.","red_flags":[],"logistics_note":"..."}}]
match_grade: Excellent(85-100) Strong(70-84) Good(55-69) Fair(40-54) Weak(<40). Return ONLY valid JSON array, no markdown."""
    msg = client.chat.completions.create(model="gpt-3.5-turbo", max_tokens=4000, messages=[{"role":"user","content":prompt}])
    raw = msg.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*","",raw)
    results = json.loads(re.sub(r"\s*```$","",raw).strip())
    cmap = {c["id"]:c for c in CANDIDATE_POOL}
    for r in results: r["profile"] = cmap.get(r["id"],{})
    return results[:top_n]
