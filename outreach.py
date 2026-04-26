import json, re
from openai import OpenAI

def simulate_outreach(candidate, parsed_jd):
    client = OpenAI()
    profile = candidate.get("profile",{})
    prompt = f"""Simulate a 4-turn recruitment LinkedIn conversation. Return ONLY JSON.
ROLE: {parsed_jd.get('role_title')} | {parsed_jd.get('domain')} | Skills: {', '.join(parsed_jd.get('required_skills',[])[:5])}
CANDIDATE: {json.dumps(profile)}
Format: {{"conversation":[{{"sender":"Recruiter","message":"..."}},{{"sender":"{profile.get('name','Candidate')}","message":"..."}},{{"sender":"Recruiter","message":"..."}},{{"sender":"{profile.get('name','Candidate')}","message":"..."}}],"interest_score":75,"interest_level":"High","interest_reasoning":"...","next_action":"...","engagement_signals":["..."],"risk_factors":["..."]}}
interest_level: Very High|High|Moderate|Low|Not Interested. Return ONLY valid JSON, no markdown."""
    msg = client.chat.completions.create(model="gpt-3.5-turbo", max_tokens=1500, messages=[{"role":"user","content":prompt}])
    raw = msg.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*","",raw)
    return json.loads(re.sub(r"\s*```$","",raw).strip())
