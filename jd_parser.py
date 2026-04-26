import json, re
from openai import OpenAI

def parse_job_description(jd_text):
    client = OpenAI()
    prompt = f"""Parse this job description into JSON with exactly these fields: role_title, seniority, required_skills, nice_to_have_skills, experience_min, experience_max, location, work_mode, domain, key_responsibilities, salary_range, team_size.

JD: {jd_text}

Return ONLY valid JSON, no markdown."""
    msg = client.chat.completions.create(model="gpt-3.5-turbo", max_tokens=1000, messages=[{"role":"user","content":prompt}])
    raw = msg.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*","",raw)
    return json.loads(re.sub(r"\s*```$","",raw).strip())
