import anthropic
import json
import re


def simulate_outreach(candidate: dict, parsed_jd: dict) -> dict:
    """
    Simulate a 4-turn recruiter ↔ candidate conversation using Claude.
    Claude plays BOTH the recruiter and the candidate (based on profile).
    Returns conversation + interest score + next action.
    """
    client = anthropic.Anthropic()

    profile = candidate.get("profile", {})
    role = parsed_jd.get("role_title", "Software Engineer")
    domain = parsed_jd.get("domain", "tech")
    work_mode = parsed_jd.get("work_mode", "Hybrid")
    location = parsed_jd.get("location", "Bangalore")

    prompt = f"""You are simulating a real recruitment outreach conversation on LinkedIn/WhatsApp.

ROLE BEING RECRUITED FOR:
- Title: {role}
- Domain: {domain}
- Work Mode: {work_mode}
- Location: {location}
- Seniority: {parsed_jd.get('seniority', 'Mid')}
- Key Requirements: {', '.join(parsed_jd.get('required_skills', [])[:6])}

CANDIDATE BEING CONTACTED:
{json.dumps(profile, indent=2)}

INSTRUCTIONS:
1. Write a 4-turn conversation (Recruiter → Candidate → Recruiter → Candidate)
2. The Recruiter message should be personalized — reference the candidate's current company and specific skills
3. The Candidate should respond REALISTICALLY based on their profile:
   - If open_to_new_roles=True and good skill match → positive but professional
   - If open_to_new_roles=False → politely decline or be cautious
   - Factor in salary expectations, location preference, notice period
4. Recruiter follow-up should address any candidate hesitations
5. Candidate's final reply reveals true interest level

After the conversation, assess the candidate's genuine interest.

Return ONLY valid JSON (no markdown):
{{
    "conversation": [
        {{"sender": "Recruiter", "message": "..."}},
        {{"sender": "{profile.get('name', 'Candidate')}", "message": "..."}},
        {{"sender": "Recruiter", "message": "..."}},
        {{"sender": "{profile.get('name', 'Candidate')}", "message": "..."}}
    ],
    "interest_score": 75,
    "interest_level": "High",
    "interest_reasoning": "Candidate expressed enthusiasm about the role but raised salary concerns. Responded quickly with thoughtful questions indicating genuine consideration.",
    "next_action": "Schedule a 30-min exploratory call",
    "engagement_signals": ["Responded promptly", "Asked about team structure", "Shared relevant project"],
    "risk_factors": ["3-month notice", "Salary bar may be a stretch"]
}}

interest_level must be one of: Very High | High | Moderate | Low | Not Interested
interest_score: 0-100 (Very High=85-100, High=70-84, Moderate=50-69, Low=25-49, Not Interested=0-24)"""

    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw.strip())
