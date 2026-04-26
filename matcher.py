import anthropic
import json
import re
from data.candidates import CANDIDATE_POOL


def discover_and_match_candidates(parsed_jd: dict, top_n: int = 8) -> list:
    """Score all candidates against the parsed JD and return top N with explanations."""
    client = anthropic.Anthropic()

    # Build a lightweight candidate representation to keep prompt manageable
    compact_candidates = []
    for c in CANDIDATE_POOL:
        compact_candidates.append({
            "id": c["id"],
            "name": c["name"],
            "title": c["title"],
            "experience_years": c["experience_years"],
            "skills": c["skills"],
            "location": c["location"],
            "work_mode_preference": c["work_mode_preference"],
            "current_company": c["current_company"],
            "education": c["education"],
            "availability": c["availability"],
            "salary_expectation": c["salary_expectation"],
            "open_to_new_roles": c["open_to_new_roles"],
            "bio": c["bio"],
        })

    prompt = f"""You are an expert technical recruiter. Score every candidate in the pool against the job requirements below.

JOB REQUIREMENTS:
{json.dumps(parsed_jd, indent=2)}

CANDIDATE POOL:
{json.dumps(compact_candidates, indent=2)}

Scoring weights:
- Skills overlap (40%): Required skills match >> nice-to-have match
- Experience fit (25%): Years of experience vs required range; relevance of past roles
- Domain/industry fit (20%): Has the candidate worked in a relevant domain?
- Logistics (15%): Location / work mode compatibility, availability, open to new roles

Return a JSON ARRAY containing ALL {len(compact_candidates)} candidates, sorted by match_score descending:
[
  {{
    "id": "C001",
    "name": "...",
    "match_score": 85,
    "match_grade": "Excellent",
    "matched_skills": ["Python", "FastAPI"],
    "missing_critical_skills": ["Kubernetes"],
    "match_reasoning": "2-3 sentence explanation highlighting strengths and gaps.",
    "red_flags": ["3-month notice period may delay start"],
    "logistics_note": "Location/remote fit note"
  }}
]

match_grade must be one of: Excellent (85-100) | Strong (70-84) | Good (55-69) | Fair (40-54) | Weak (<40)
Return ONLY valid JSON array, no markdown, no extra text."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    results = json.loads(raw.strip())

    # Merge full profile data back in
    candidate_map = {c["id"]: c for c in CANDIDATE_POOL}
    for r in results:
        r["profile"] = candidate_map.get(r["id"], {})

    return results[:top_n]
