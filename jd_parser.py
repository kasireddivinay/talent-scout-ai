import anthropic
import json
import re


def parse_job_description(jd_text: str) -> dict:
    """Parse a raw job description into structured fields using Claude."""
    client = anthropic.Anthropic()

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

If experience is not specified, use 0 for min and 99 for max.
Return ONLY valid JSON, no markdown fences, no explanation."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    # Strip markdown fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw.strip())
