def compute_final_scores(matched_candidates: list, outreach_results: dict) -> list:
    """
    Merge match scores with interest scores and produce a final ranked shortlist.

    Weights:
        Match Score  → 60%
        Interest Score → 40%

    Returns candidates sorted by composite_score descending.
    """
    final = []

    for candidate in matched_candidates:
        cid = candidate["id"]
        match_score = candidate.get("match_score", 0)
        outreach = outreach_results.get(cid, {})
        interest_score = outreach.get("interest_score", 0)

        # Weighted composite
        composite_score = round(0.6 * match_score + 0.4 * interest_score, 1)

        grade = _composite_grade(composite_score)

        final.append({
            "id": cid,
            "name": candidate.get("name", ""),
            "title": candidate.get("profile", {}).get("title", ""),
            "current_company": candidate.get("profile", {}).get("current_company", ""),
            "experience_years": candidate.get("profile", {}).get("experience_years", 0),
            "location": candidate.get("profile", {}).get("location", ""),
            "availability": candidate.get("profile", {}).get("availability", ""),
            "salary_expectation": candidate.get("profile", {}).get("salary_expectation", ""),
            # Scores
            "match_score": match_score,
            "match_grade": candidate.get("match_grade", ""),
            "interest_score": interest_score,
            "interest_level": outreach.get("interest_level", "N/A"),
            "composite_score": composite_score,
            "composite_grade": grade,
            # Explainability
            "match_reasoning": candidate.get("match_reasoning", ""),
            "matched_skills": candidate.get("matched_skills", []),
            "missing_critical_skills": candidate.get("missing_critical_skills", []),
            "red_flags": candidate.get("red_flags", []),
            "interest_reasoning": outreach.get("interest_reasoning", ""),
            "next_action": outreach.get("next_action", "Review profile"),
            "engagement_signals": outreach.get("engagement_signals", []),
            "risk_factors": outreach.get("risk_factors", []),
            # Raw profile
            "profile": candidate.get("profile", {}),
            # Conversation
            "conversation": outreach.get("conversation", []),
        })

    final.sort(key=lambda x: x["composite_score"], reverse=True)
    return final


def _composite_grade(score: float) -> str:
    if score >= 82:
        return "🏆 Top Pick"
    elif score >= 68:
        return "⭐ Strong"
    elif score >= 52:
        return "✅ Good Fit"
    elif score >= 38:
        return "⚠️ Borderline"
    else:
        return "❌ Weak"
