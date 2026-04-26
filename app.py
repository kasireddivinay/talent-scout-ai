"""
TalentScout AI — AI-Powered Talent Scouting & Engagement Agent
Catalyst Hackathon | Deccan AI
"""

import streamlit as st
import time
import json
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TalentScout AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f4c75 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    color: white;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50px; right: -50px;
    width: 200px; height: 200px;
    background: rgba(99,179,237,0.1);
    border-radius: 50%;
}
.hero-title { font-size: 2rem; font-weight: 700; margin: 0; letter-spacing: -0.5px; }
.hero-sub { font-size: 1rem; color: #93c5fd; margin-top: 0.3rem; }
.hero-badge {
    display: inline-block;
    background: rgba(99,179,237,0.2);
    border: 1px solid rgba(99,179,237,0.4);
    color: #93c5fd;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* Step indicators */
.step-bar {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
    padding: 0.75rem 1rem;
    background: #f8fafc;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
}
.step-item {
    flex: 1;
    text-align: center;
    padding: 0.5rem;
    border-radius: 8px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #94a3b8;
}
.step-active { background: #1e40af; color: white; }
.step-done { background: #dcfce7; color: #15803d; }

/* Score badges */
.score-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
}
.score-excellent { background: #dcfce7; color: #15803d; }
.score-strong    { background: #dbeafe; color: #1d4ed8; }
.score-good      { background: #fef9c3; color: #854d0e; }
.score-fair      { background: #fee2e2; color: #b91c1c; }

/* Candidate card */
.candidate-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    transition: box-shadow 0.2s;
}
.candidate-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.candidate-name { font-size: 1rem; font-weight: 700; color: #0f172a; }
.candidate-meta { font-size: 0.8rem; color: #64748b; margin-top: 0.2rem; }

/* Chat bubble */
.chat-row { display: flex; margin-bottom: 0.75rem; gap: 0.5rem; }
.chat-row.recruiter { justify-content: flex-start; }
.chat-row.candidate { justify-content: flex-end; }
.bubble {
    max-width: 75%;
    padding: 0.65rem 1rem;
    border-radius: 12px;
    font-size: 0.85rem;
    line-height: 1.5;
}
.bubble-recruiter {
    background: #1e40af;
    color: white;
    border-bottom-left-radius: 4px;
}
.bubble-candidate {
    background: #f1f5f9;
    color: #0f172a;
    border-bottom-right-radius: 4px;
}
.chat-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #94a3b8;
    margin-bottom: 0.2rem;
}

/* Skill pill */
.skill-pill {
    display: inline-block;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    padding: 0.15rem 0.5rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    margin: 0.1rem;
}
.skill-pill-miss {
    background: #fff7ed;
    color: #9a3412;
    border: 1px solid #fed7aa;
}

/* Metric box */
.metric-box {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}
.metric-val { font-size: 2rem; font-weight: 800; color: #1e40af; }
.metric-label { font-size: 0.75rem; color: #64748b; margin-top: 0.25rem; }

/* Final table */
.rank-card {
    background: white;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    position: relative;
}
.rank-card.top { border-color: #fbbf24; background: #fffbeb; }
.rank-number {
    position: absolute;
    top: -12px; left: 1rem;
    background: #1e40af;
    color: white;
    width: 26px; height: 26px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 800;
}
.rank-number.gold { background: #f59e0b; }

/* Info callout */
.info-box {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    padding: 0.75rem 1rem;
    border-radius: 0 8px 8px 0;
    font-size: 0.85rem;
    color: #1e40af;
    margin-bottom: 1rem;
}

/* Divider */
.divider { border: none; border-top: 1px solid #e2e8f0; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)


# ── Helper functions ──────────────────────────────────────────────────────────

def score_color(score: float) -> str:
    if score >= 80: return "#15803d"
    if score >= 65: return "#1d4ed8"
    if score >= 50: return "#854d0e"
    return "#b91c1c"

def score_bg(score: float) -> str:
    if score >= 80: return "#dcfce7"
    if score >= 65: return "#dbeafe"
    if score >= 50: return "#fef9c3"
    return "#fee2e2"

def render_score_bar(score: float, label: str, color: str):
    pct = int(score)
    st.markdown(f"""
    <div style="margin-bottom:0.5rem;">
        <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
            <span style="font-size:0.75rem;font-weight:600;color:#475569;">{label}</span>
            <span style="font-size:0.75rem;font-weight:800;color:{color};">{pct}</span>
        </div>
        <div style="background:#e2e8f0;border-radius:4px;height:8px;overflow:hidden;">
            <div style="width:{pct}%;background:{color};height:100%;border-radius:4px;transition:width 0.5s;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_chat(conversation: list):
    for turn in conversation:
        sender = turn.get("sender", "")
        msg = turn.get("message", "")
        is_recruiter = sender.lower() == "recruiter"
        row_class = "recruiter" if is_recruiter else "candidate"
        bubble_class = "bubble-recruiter" if is_recruiter else "bubble-candidate"
        label = "🧑‍💼 Recruiter" if is_recruiter else f"👤 {sender}"
        st.markdown(f"""
        <div class="chat-row {row_class}">
            <div>
                <div class="chat-label" style="text-align:{'left' if is_recruiter else 'right'};">{label}</div>
                <div class="bubble {bubble_class}">{msg}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_skills(skills: list, pill_class: str = "skill-pill"):
    pills = " ".join(f'<span class="{pill_class}">{s}</span>' for s in skills)
    st.markdown(f'<div style="margin:0.3rem 0;">{pills}</div>', unsafe_allow_html=True)

def check_api_key():
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        st.error("⚠️ **ANTHROPIC_API_KEY not set.** Add it to your environment or `.env` file.")
        st.stop()


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    top_n = st.slider("Candidates to discover", min_value=3, max_value=10, value=6)
    outreach_n = st.slider("Candidates to engage (outreach)", min_value=1, max_value=6, value=4)
    match_weight = st.slider("Match Score weight %", 40, 80, 60, step=5)
    interest_weight = 100 - match_weight
    st.caption(f"Composite = {match_weight}% Match + {interest_weight}% Interest")
    st.divider()
    st.markdown("### 📋 Sample JDs")
    sample_jds = {
        "Senior Backend Engineer": """We are hiring a Senior Backend Engineer at FinFlow (FinTech startup, Series B).

Role: Senior Backend Engineer
Location: Bangalore (Hybrid)
Experience: 5-8 years

Requirements:
- Strong proficiency in Python (FastAPI or Django)
- Experience with PostgreSQL, Redis, and message queues (Kafka/RabbitMQ)
- Kubernetes and Docker in production
- Microservices architecture design
- AWS (EC2, RDS, Lambda, S3)

Nice to have:
- Experience in FinTech / payments domain
- Familiarity with regulatory compliance (PCI-DSS)

Responsibilities:
- Design and build scalable payment processing APIs
- Lead technical design reviews
- Mentor junior engineers
- Collaborate with product and ML teams

Compensation: ₹35–50 LPA
Team size: 8 engineers reporting to CTO""",

        "ML Engineer (LLMs)": """Stealth AI startup building enterprise LLM applications seeks an ML Engineer.

Location: Remote
Experience: 3-6 years

Must have:
- PyTorch, Transformers (Hugging Face)
- LLM fine-tuning (LoRA, QLoRA, RLHF)
- RAG pipeline development
- Vector databases (Pinecone, Weaviate, Qdrant)
- LangChain / LlamaIndex
- Strong Python skills

Nice to have:
- Published research or open source contributions
- Production ML deployment experience (MLflow, BentoML)
- GCP or AWS experience

Role involves building next-gen AI assistants for Fortune 500 enterprise clients.
Compensation: ₹30–50 LPA + meaningful equity""",

        "Product Manager – Growth": """PhaseOne (Series A SaaS company) hiring a Product Manager for Growth.

Location: Delhi / Remote
Experience: 3-5 years

Skills required:
- Product management experience at a B2C or SaaS company
- Strong analytical skills (SQL is a must)
- Experience running A/B tests and growth experiments
- User research and customer interview skills
- Stakeholder management

Nice to have:
- MBA from Tier 1 institution
- Experience in seller/marketplace growth
- Familiarity with Figma for wireframing

Responsibilities:
- Own the growth roadmap across acquisition and retention
- Run experiments and measure impact
- Work with engineering, design, and marketing

Compensation: ₹20–32 LPA""",
    }
    selected_sample = st.selectbox("Load sample JD:", ["— select —"] + list(sample_jds.keys()))
    if selected_sample != "— select —":
        st.session_state["sample_jd"] = sample_jds[selected_sample]

    st.divider()
    st.markdown("**Built for Catalyst Hackathon**  \nDeccan AI · April 2025")


# ── Session state init ─────────────────────────────────────────────────────────

for key in ["step", "parsed_jd", "matched_candidates", "outreach_results", "final_shortlist"]:
    if key not in st.session_state:
        st.session_state[key] = None
if "step" not in st.session_state or st.session_state["step"] is None:
    st.session_state["step"] = 0


# ── Hero ───────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-banner">
    <div class="hero-badge">🏆 Catalyst Hackathon · Deccan AI</div>
    <div class="hero-title">🎯 TalentScout AI</div>
    <div class="hero-sub">AI-powered talent scouting, matching & engagement — from JD to ranked shortlist in minutes.</div>
</div>
""", unsafe_allow_html=True)


# ── Step bar ───────────────────────────────────────────────────────────────────

step = st.session_state["step"]
steps = ["1 · JD Input", "2 · JD Parsed", "3 · Candidates Found", "4 · Outreach Done", "5 · Shortlist Ready"]

def step_class(i):
    if i < step: return "step-done"
    if i == step: return "step-active"
    return ""

bar_html = '<div class="step-bar">' + "".join(
    f'<div class="step-item {step_class(i)}">{s}</div>' for i, s in enumerate(steps)
) + "</div>"
st.markdown(bar_html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 0 — JD INPUT
# ══════════════════════════════════════════════════════════════════════════════

if step == 0:
    st.markdown("### 📄 Paste Job Description")
    st.markdown('<div class="info-box">Paste any job description below — we\'ll extract requirements, discover matching candidates, simulate outreach conversations, and return a ranked shortlist scored on <strong>Match</strong> + <strong>Interest</strong>.</div>', unsafe_allow_html=True)

    default_jd = st.session_state.get("sample_jd", "")
    jd_text = st.text_area(
        "Job Description",
        value=default_jd,
        height=320,
        placeholder="Paste your full job description here (role, skills, experience, location, responsibilities)...",
        label_visibility="collapsed"
    )

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        go = st.button("🚀 Analyze & Scout Candidates", type="primary", use_container_width=True)
    with col3:
        if st.button("🔄 Reset", use_container_width=True):
            for k in ["step", "parsed_jd", "matched_candidates", "outreach_results", "final_shortlist", "sample_jd"]:
                st.session_state[k] = None
            st.session_state["step"] = 0
            st.rerun()

    if go:
        if not jd_text.strip() or len(jd_text.strip()) < 50:
            st.warning("Please paste a full job description (at least 50 characters).")
        else:
            check_api_key()
            st.session_state["jd_text"] = jd_text
            # ── Parse JD ──────────────────────────────────────────────────────
            with st.spinner("🧠 Parsing job description..."):
                from agents.jd_parser import parse_job_description
                parsed = parse_job_description(jd_text)
                st.session_state["parsed_jd"] = parsed

            # ── Match Candidates ───────────────────────────────────────────────
            with st.spinner(f"🔍 Discovering and scoring candidates from pool of 15..."):
                from agents.matcher import discover_and_match_candidates
                matched = discover_and_match_candidates(parsed, top_n=top_n)
                st.session_state["matched_candidates"] = matched

            # ── Outreach Simulation ───────────────────────────────────────────
            outreach_results = {}
            engage_candidates = matched[:outreach_n]
            progress = st.progress(0, text="💬 Simulating outreach conversations...")
            from agents.outreach import simulate_outreach
            for i, cand in enumerate(engage_candidates):
                progress.progress((i + 1) / outreach_n, text=f"💬 Engaging {cand['name']}...")
                result = simulate_outreach(cand, parsed)
                outreach_results[cand["id"]] = result
            progress.empty()
            st.session_state["outreach_results"] = outreach_results

            # ── Final Scoring ─────────────────────────────────────────────────
            from agents.scorer import compute_final_scores
            # Override weights with sidebar settings
            import agents.scorer as scorer_module
            def weighted_score(candidates, outreach):
                final = []
                for candidate in candidates:
                    cid = candidate["id"]
                    ms = candidate.get("match_score", 0)
                    out = outreach.get(cid, {})
                    ins = out.get("interest_score", 0)
                    composite = round((match_weight / 100) * ms + (interest_weight / 100) * ins, 1)
                    grade = scorer_module._composite_grade(composite)
                    final.append({**candidate,
                        "match_score": ms, "interest_score": ins,
                        "interest_level": out.get("interest_level", "N/A"),
                        "composite_score": composite, "composite_grade": grade,
                        "match_reasoning": candidate.get("match_reasoning", ""),
                        "matched_skills": candidate.get("matched_skills", []),
                        "missing_critical_skills": candidate.get("missing_critical_skills", []),
                        "red_flags": candidate.get("red_flags", []),
                        "interest_reasoning": out.get("interest_reasoning", ""),
                        "next_action": out.get("next_action", "Review profile"),
                        "engagement_signals": out.get("engagement_signals", []),
                        "risk_factors": out.get("risk_factors", []),
                        "profile": candidate.get("profile", {}),
                        "conversation": out.get("conversation", []),
                        "name": candidate.get("name", ""),
                        "title": candidate.get("profile", {}).get("title", ""),
                        "current_company": candidate.get("profile", {}).get("current_company", ""),
                        "experience_years": candidate.get("profile", {}).get("experience_years", 0),
                        "location": candidate.get("profile", {}).get("location", ""),
                        "availability": candidate.get("profile", {}).get("availability", ""),
                        "salary_expectation": candidate.get("profile", {}).get("salary_expectation", ""),
                    })
                final.sort(key=lambda x: x["composite_score"], reverse=True)
                return final

            shortlist = weighted_score(matched, outreach_results)
            st.session_state["final_shortlist"] = shortlist
            st.session_state["step"] = 5
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — RESULTS (all tabs)
# ══════════════════════════════════════════════════════════════════════════════

if step == 5:
    parsed_jd = st.session_state["parsed_jd"]
    matched = st.session_state["matched_candidates"]
    outreach = st.session_state["outreach_results"]
    shortlist = st.session_state["final_shortlist"]

    # ── Reset button ──────────────────────────────────────────────────────────
    if st.button("🔄 Scout Another Role", type="secondary"):
        for k in ["step", "parsed_jd", "matched_candidates", "outreach_results", "final_shortlist", "sample_jd", "jd_text"]:
            st.session_state[k] = None
        st.session_state["step"] = 0
        st.rerun()

    # ── Summary metrics ───────────────────────────────────────────────────────
    top = shortlist[0] if shortlist else {}
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{len(matched)}</div><div class="metric-label">Candidates Scored</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{len(outreach)}</div><div class="metric-label">Outreach Simulated</div></div>', unsafe_allow_html=True)
    with c3:
        avg_match = round(sum(c.get("match_score", 0) for c in shortlist) / max(len(shortlist), 1), 1)
        st.markdown(f'<div class="metric-box"><div class="metric-val">{avg_match}</div><div class="metric-label">Avg Match Score</div></div>', unsafe_allow_html=True)
    with c4:
        top_score = top.get("composite_score", 0)
        st.markdown(f'<div class="metric-box"><div class="metric-val">{top_score}</div><div class="metric-label">Top Composite Score</div></div>', unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Ranked Shortlist", "🔍 Match Details", "💬 Outreach Conversations", "📋 Parsed JD"])

    # ═══════════════════════════════════════════════
    # TAB 1 — RANKED SHORTLIST
    # ═══════════════════════════════════════════════
    with tab1:
        st.markdown("### 🏆 Final Ranked Shortlist")
        st.caption(f"Composite = {match_weight}% Match Score + {interest_weight}% Interest Score · Top {len(shortlist)} candidates")

        for rank, cand in enumerate(shortlist, 1):
            is_top = rank == 1
            card_class = "rank-card top" if is_top else "rank-card"
            num_class = "rank-number gold" if is_top else "rank-number"
            cs = cand["composite_score"]
            ms = cand["match_score"]
            ins = cand["interest_score"]

            st.markdown(f'<div class="{card_class}"><div class="{num_class}">#{rank}</div>', unsafe_allow_html=True)

            col_info, col_scores = st.columns([3, 2])
            with col_info:
                st.markdown(f"**{cand['name']}** — {cand['title']} @ {cand['current_company']}")
                st.caption(f"📍 {cand['location']} · 🕐 {cand['experience_years']} yrs · 📅 {cand['availability']}")
                st.caption(f"💰 {cand['salary_expectation']}")
                st.markdown(f"**Grade:** {cand['composite_grade']}&nbsp;&nbsp;&nbsp;**Interest:** {cand.get('interest_level', 'N/A')}")
                st.caption(f"🎯 Next action: *{cand['next_action']}*")

            with col_scores:
                render_score_bar(cs, "Composite Score", score_color(cs))
                render_score_bar(ms, "Match Score", score_color(ms))
                render_score_bar(ins, "Interest Score", score_color(ins))

            with st.expander("🔎 See reasoning & skills"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    st.markdown("**✅ Matched Skills**")
                    render_skills(cand.get("matched_skills", []))
                    if cand.get("missing_critical_skills"):
                        st.markdown("**⚠️ Missing Skills**")
                        render_skills(cand.get("missing_critical_skills", []), "skill-pill skill-pill-miss")
                with ec2:
                    st.markdown("**Match Reasoning**")
                    st.write(cand.get("match_reasoning", ""))
                    if cand.get("interest_reasoning"):
                        st.markdown("**Interest Reasoning**")
                        st.write(cand.get("interest_reasoning", ""))
                if cand.get("red_flags"):
                    st.warning("⚠️ " + " · ".join(cand["red_flags"]))
                if cand.get("risk_factors"):
                    st.info("ℹ️ Risk factors: " + " · ".join(cand["risk_factors"]))

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("")

        # JSON export
        st.divider()
        st.markdown("#### 📥 Export Shortlist")
        export_data = [{
            "rank": i + 1,
            "name": c["name"],
            "title": c["title"],
            "company": c["current_company"],
            "match_score": c["match_score"],
            "interest_score": c["interest_score"],
            "composite_score": c["composite_score"],
            "grade": c["composite_grade"],
            "next_action": c["next_action"],
            "availability": c["availability"],
            "salary": c["salary_expectation"],
        } for i, c in enumerate(shortlist)]
        st.download_button(
            "⬇️ Download as JSON",
            data=json.dumps(export_data, indent=2),
            file_name="talentscout_shortlist.json",
            mime="application/json",
        )

    # ═══════════════════════════════════════════════
    # TAB 2 — MATCH DETAILS
    # ═══════════════════════════════════════════════
    with tab2:
        st.markdown("### 🔍 Candidate Match Analysis")
        for cand in matched:
            ms = cand.get("match_score", 0)
            mg = cand.get("match_grade", "")
            profile = cand.get("profile", {})

            with st.expander(f"**{cand['name']}** — Match: {ms}/100 ({mg}) · {profile.get('title', '')}"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown(f"**Bio:** {profile.get('bio', '')}")
                    st.markdown("**✅ Matched Skills:**")
                    render_skills(cand.get("matched_skills", []))
                    if cand.get("missing_critical_skills"):
                        st.markdown("**⚠️ Missing Critical Skills:**")
                        render_skills(cand.get("missing_critical_skills", []), "skill-pill skill-pill-miss")
                    st.markdown(f"**Reasoning:** {cand.get('match_reasoning', '')}")
                    if cand.get("logistics_note"):
                        st.info(f"📍 {cand['logistics_note']}")
                    if cand.get("red_flags"):
                        st.warning("⚠️ " + " · ".join(cand["red_flags"]))
                with c2:
                    render_score_bar(ms, "Match Score", score_color(ms))
                    st.markdown(f"**Company:** {profile.get('current_company', '')}")
                    st.markdown(f"**Experience:** {profile.get('experience_years', '')} yrs")
                    st.markdown(f"**Location:** {profile.get('location', '')}")
                    st.markdown(f"**Work Mode:** {profile.get('work_mode_preference', '')}")
                    st.markdown(f"**Availability:** {profile.get('availability', '')}")
                    st.markdown(f"**Salary Exp:** {profile.get('salary_expectation', '')}")
                    open_badge = "🟢 Open" if profile.get("open_to_new_roles") else "🔴 Not actively looking"
                    st.markdown(f"**Status:** {open_badge}")

    # ═══════════════════════════════════════════════
    # TAB 3 — OUTREACH CONVERSATIONS
    # ═══════════════════════════════════════════════
    with tab3:
        st.markdown("### 💬 Simulated Outreach Conversations")
        st.caption("AI-simulated LinkedIn/WhatsApp conversations. Candidate responses are generated based on their profile, openness to roles, and fit.")

        if not outreach:
            st.info("No outreach simulations available.")
        else:
            for cid, result in outreach.items():
                # Find candidate name
                cname = next((c["name"] for c in matched if c["id"] == cid), cid)
                ins = result.get("interest_score", 0)
                il = result.get("interest_level", "")

                with st.expander(f"**{cname}** — Interest: {ins}/100 · {il}"):
                    st.markdown("**Conversation:**")
                    render_chat(result.get("conversation", []))
                    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
                    col_a, col_b = st.columns(2)
                    with col_a:
                        render_score_bar(ins, "Interest Score", score_color(ins))
                        st.markdown(f"**Interest Level:** {il}")
                        st.markdown(f"**Next Action:** {result.get('next_action', '')}")
                    with col_b:
                        if result.get("engagement_signals"):
                            st.markdown("**🟢 Engagement Signals:**")
                            for sig in result["engagement_signals"]:
                                st.markdown(f"- {sig}")
                        if result.get("risk_factors"):
                            st.markdown("**🟡 Risk Factors:**")
                            for rf in result["risk_factors"]:
                                st.markdown(f"- {rf}")
                    if result.get("interest_reasoning"):
                        st.markdown(f"**Reasoning:** {result['interest_reasoning']}")

    # ═══════════════════════════════════════════════
    # TAB 4 — PARSED JD
    # ═══════════════════════════════════════════════
    with tab4:
        st.markdown("### 📋 Parsed Job Description")
        st.caption("Structured data extracted from your JD by the AI parser agent.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Role:** {parsed_jd.get('role_title', '')}")
            st.markdown(f"**Seniority:** {parsed_jd.get('seniority', '')}")
            st.markdown(f"**Domain:** {parsed_jd.get('domain', '')}")
            st.markdown(f"**Location:** {parsed_jd.get('location', '')}")
            st.markdown(f"**Work Mode:** {parsed_jd.get('work_mode', '')}")
            exp_min = parsed_jd.get('experience_min', 0)
            exp_max = parsed_jd.get('experience_max', 99)
            exp_str = f"{exp_min}–{exp_max} yrs" if exp_max < 99 else f"{exp_min}+ yrs"
            st.markdown(f"**Experience:** {exp_str}")
            if parsed_jd.get("salary_range"):
                st.markdown(f"**Salary:** {parsed_jd['salary_range']}")
        with col2:
            st.markdown("**Required Skills:**")
            render_skills(parsed_jd.get("required_skills", []))
            if parsed_jd.get("nice_to_have_skills"):
                st.markdown("**Nice-to-Have Skills:**")
                render_skills(parsed_jd.get("nice_to_have_skills", []))

        if parsed_jd.get("key_responsibilities"):
            st.markdown("**Key Responsibilities:**")
            for r in parsed_jd["key_responsibilities"]:
                st.markdown(f"• {r}")

        st.divider()
        st.markdown("**Raw parsed JSON:**")
        st.json(parsed_jd)
