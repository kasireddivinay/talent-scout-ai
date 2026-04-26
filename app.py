import streamlit as st
import json
import os
import re

st.set_page_config(page_title="TalentScout AI", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.hero-banner{background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 50%,#0f4c75 100%);border-radius:16px;padding:2rem 2.5rem;margin-bottom:1.5rem;color:white}
.hero-title{font-size:2rem;font-weight:700;margin:0}
.hero-sub{font-size:1rem;color:#93c5fd;margin-top:0.3rem}
.hero-badge{display:inline-block;background:rgba(99,179,237,0.2);border:1px solid rgba(99,179,237,0.4);color:#93c5fd;padding:0.25rem 0.75rem;border-radius:20px;font-size:0.75rem;font-weight:600;margin-bottom:0.75rem;text-transform:uppercase}
.metric-box{background:white;border:1px solid #e2e8f0;border-radius:10px;padding:1rem;text-align:center}
.metric-val{font-size:2rem;font-weight:800;color:#1e40af}
.metric-label{font-size:0.75rem;color:#64748b;margin-top:0.25rem}
.rank-card{background:white;border:1.5px solid #e2e8f0;border-radius:14px;padding:1.25rem 1.5rem;margin-bottom:1rem}
.skill-pill{display:inline-block;background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;padding:0.15rem 0.5rem;border-radius:20px;font-size:0.7rem;font-weight:600;margin:0.1rem}
.skill-miss{background:#fff7ed;color:#9a3412;border:1px solid #fed7aa}
.bubble{max-width:75%;padding:0.65rem 1rem;border-radius:12px;font-size:0.85rem;line-height:1.5}
.brec{background:#1e40af;color:white}
.bcan{background:#f1f5f9;color:#0f172a}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for k in ["step","parsed_jd","matched","outreach","shortlist","jd_text","sample_jd"]:
    if k not in st.session_state:
        st.session_state[k] = None
if not st.session_state["step"]:
    st.session_state["step"] = 0

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Settings")
    top_n = st.slider("Candidates to discover", 3, 10, 6)
    outreach_n = st.slider("Candidates to engage", 1, 6, 4)
    mw = st.slider("Match Score weight %", 40, 80, 60, step=5)
    iw = 100 - mw
    st.caption(f"Composite = {mw}% Match + {iw}% Interest")
    st.divider()
    st.markdown("### Sample JDs")
    samples = {
        "Senior Backend Engineer": (
            "Hiring a Senior Backend Engineer at FinFlow (FinTech, Series B).\n"
            "Location: Bangalore (Hybrid). Experience: 5-8 years.\n"
            "Required: Python, FastAPI, PostgreSQL, Redis, Kafka, Kubernetes, Docker, AWS, Microservices.\n"
            "Nice to have: FinTech domain, PCI-DSS compliance.\n"
            "Responsibilities: Build payment APIs, lead design reviews, mentor engineers.\n"
            "Compensation: Rs 35-50 LPA. Team: 8 engineers."
        ),
        "ML Engineer (LLMs)": (
            "AI startup seeks ML Engineer. Location: Remote. Experience: 3-6 years.\n"
            "Required: PyTorch, Transformers, LLM fine-tuning, RAG pipelines, LangChain, Vector DBs.\n"
            "Nice to have: Published research, MLflow, GCP.\n"
            "Compensation: Rs 30-50 LPA + equity."
        ),
        "Product Manager": (
            "Series A SaaS company hiring PM for Growth. Location: Delhi/Remote. Experience: 3-5 years.\n"
            "Required: Product management, SQL, A/B testing, User research, Stakeholder management.\n"
            "Nice to have: MBA Tier 1, Figma, marketplace experience.\n"
            "Compensation: Rs 20-32 LPA."
        ),
    }
    sel = st.selectbox("Load sample JD:", ["— select —"] + list(samples.keys()))
    if sel != "— select —":
        st.session_state["sample_jd"] = samples[sel]
    st.divider()
    st.markdown("**Built for Catalyst Hackathon**")
    st.markdown("Deccan AI · April 2025")

# ── Helpers ────────────────────────────────────────────────────────────────────
def sc(s):
    if s >= 80: return "#15803d"
    if s >= 65: return "#1d4ed8"
    if s >= 50: return "#854d0e"
    return "#b91c1c"

def bar(score, label, color):
    st.markdown(
        f'<div style="margin-bottom:0.5rem">'
        f'<div style="display:flex;justify-content:space-between">'
        f'<span style="font-size:0.75rem;font-weight:600;color:#475569">{label}</span>'
        f'<span style="font-size:0.75rem;font-weight:800;color:{color}">{int(score)}</span>'
        f'</div>'
        f'<div style="background:#e2e8f0;border-radius:4px;height:8px">'
        f'<div style="width:{int(score)}%;background:{color};height:100%;border-radius:4px"></div>'
        f'</div></div>',
        unsafe_allow_html=True
    )

def chat(conversation):
    for t in conversation:
        sender = t.get("sender", "")
        msg = t.get("message", "")
        is_r = sender.lower() == "recruiter"
        align = "flex-start" if is_r else "flex-end"
        cls = "brec" if is_r else "bcan"
        label = "Recruiter" if is_r else sender
        st.markdown(
            f'<div style="display:flex;margin-bottom:0.75rem;justify-content:{align}">'
            f'<div><div style="font-size:0.7rem;font-weight:600;color:#94a3b8;margin-bottom:0.2rem">{label}</div>'
            f'<div class="bubble {cls}">{msg}</div></div></div>',
            unsafe_allow_html=True
        )

def pills(skills, extra=""):
    cls = "skill-pill " + extra
    st.markdown(" ".join(f'<span class="{cls.strip()}">{s}</span>' for s in skills), unsafe_allow_html=True)

def grade(s):
    if s >= 82: return "🏆 Top Pick"
    if s >= 68: return "⭐ Strong"
    if s >= 52: return "✅ Good Fit"
    if s >= 38: return "⚠️ Borderline"
    return "❌ Weak"

def call_gemini(prompt):
    from openai import OpenAI
    client = OpenAI()
    msg = client.chat.completions.create(model="gpt-3.5-turbo", max_tokens=2000, messages=[{"role":"user","content":prompt}])
    raw = msg.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero-banner">'
    '<div class="hero-badge">🏆 Catalyst Hackathon · Deccan AI</div>'
    '<div class="hero-title">🎯 TalentScout AI</div>'
    '<div class="hero-sub">AI-powered talent scouting, matching and engagement — from JD to ranked shortlist in minutes.</div>'
    '</div>',
    unsafe_allow_html=True
)

# ── Step bar ───────────────────────────────────────────────────────────────────
step = st.session_state["step"]
steps = ["1 · JD Input", "2 · JD Parsed", "3 · Candidates Found", "4 · Outreach Done", "5 · Shortlist Ready"]
bar_html = '<div style="display:flex;gap:0.5rem;margin-bottom:1.5rem;padding:0.75rem;background:#f8fafc;border-radius:10px;border:1px solid #e2e8f0">'
for i, s in enumerate(steps):
    if i < step:
        bg, col = "#dcfce7", "#15803d"
    elif i == step:
        bg, col = "#1e40af", "white"
    else:
        bg, col = "transparent", "#94a3b8"
    bar_html += f'<div style="flex:1;text-align:center;padding:0.5rem;border-radius:8px;background:{bg};color:{col};font-size:0.75rem;font-weight:600">{s}</div>'
bar_html += "</div>"
st.markdown(bar_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 0 — INPUT
# ══════════════════════════════════════════════════════════════════════════════
if step == 0:
    st.markdown("### Paste Job Description")
    default = st.session_state.get("sample_jd") or ""
    jd_text = st.text_area("JD", value=default, height=300,
                            placeholder="Paste your full job description here...",
                            label_visibility="collapsed")
    c1, _, c3 = st.columns([2, 1, 1])
    with c1:
        go = st.button("🚀 Analyze & Scout Candidates", type="primary", use_container_width=True)
    with c3:
        if st.button("🔄 Reset", use_container_width=True):
            for k in ["step","parsed_jd","matched","outreach","shortlist","sample_jd","jd_text"]:
                st.session_state[k] = None
            st.session_state["step"] = 0
            st.rerun()

    if go:
        if len(jd_text.strip()) < 50:
            st.warning("Please paste a full job description.")
        else:
            st.session_state["jd_text"] = jd_text

            # ── Parse JD ──────────────────────────────────────────────────────
            with st.spinner("🧠 Parsing job description..."):
                jd_prompt = f"""Parse this job description and return ONLY a JSON object with these fields:
{{"role_title":"","seniority":"Junior|Mid|Senior|Lead|Manager","required_skills":[],"nice_to_have_skills":[],"experience_min":0,"experience_max":10,"location":"","work_mode":"Remote|Hybrid|Onsite","domain":"","key_responsibilities":[],"salary_range":null,"team_size":null}}

Job Description:
{jd_text}

Return ONLY valid JSON, no markdown."""
                parsed = json.loads(call_gemini(jd_prompt))
                st.session_state["parsed_jd"] = parsed

            # ── Match Candidates ───────────────────────────────────────────────
            with st.spinner("🔍 Discovering and scoring candidates..."):
                from candidates import CANDIDATE_POOL
                compact = [{"id":c["id"],"name":c["name"],"title":c["title"],"experience_years":c["experience_years"],"skills":c["skills"],"location":c["location"],"work_mode_preference":c["work_mode_preference"],"current_company":c["current_company"],"availability":c["availability"],"salary_expectation":c["salary_expectation"],"open_to_new_roles":c["open_to_new_roles"],"bio":c["bio"]} for c in CANDIDATE_POOL]
                match_prompt = f"""You are an expert recruiter. Score ALL candidates against this job.

JOB: {json.dumps(parsed)}
CANDIDATES: {json.dumps(compact)}

Scoring: Skills 40%, Experience 25%, Domain 20%, Logistics 15%.

Return a JSON ARRAY of all {len(compact)} candidates sorted by match_score desc:
[{{"id":"C001","name":"...","match_score":85,"match_grade":"Excellent","matched_skills":[],"missing_critical_skills":[],"match_reasoning":"2-3 sentences.","red_flags":[],"logistics_note":"..."}}]

match_grade: Excellent(85-100) Strong(70-84) Good(55-69) Fair(40-54) Weak(<40)
Return ONLY valid JSON array."""
                raw_match = json.loads(call_gemini(match_prompt))
                cmap = {c["id"]: c for c in CANDIDATE_POOL}
                for r in raw_match:
                    r["profile"] = cmap.get(r["id"], {})
                matched = raw_match[:top_n]
                st.session_state["matched"] = matched

            # ── Outreach ───────────────────────────────────────────────────────
            outreach = {}
            prog = st.progress(0, text="💬 Simulating outreach conversations...")
            for i, cand in enumerate(matched[:outreach_n]):
                prog.progress((i + 1) / outreach_n, text=f"💬 Engaging {cand['name']}...")
                profile = cand.get("profile", {})
                out_prompt = f"""Simulate a recruitment outreach conversation.

ROLE: {parsed.get('role_title')} | {parsed.get('domain')} | {parsed.get('work_mode')}
REQUIRED SKILLS: {', '.join(parsed.get('required_skills', [])[:6])}
CANDIDATE: {json.dumps(profile)}

Write a 4-turn conversation. Candidate responds based on open_to_new_roles={profile.get('open_to_new_roles')}, salary={profile.get('salary_expectation')}, location={profile.get('location')}.

Return ONLY valid JSON:
{{"conversation":[{{"sender":"Recruiter","message":"..."}},{{"sender":"{profile.get('name','Candidate')}","message":"..."}},{{"sender":"Recruiter","message":"..."}},{{"sender":"{profile.get('name','Candidate')}","message":"..."}}],"interest_score":75,"interest_level":"High","interest_reasoning":"...","next_action":"...","engagement_signals":["..."],"risk_factors":["..."]}}

interest_level must be one of: Very High, High, Moderate, Low, Not Interested"""
                outreach[cand["id"]] = json.loads(call_gemini(out_prompt))
            prog.empty()
            st.session_state["outreach"] = outreach

            # ── Score ──────────────────────────────────────────────────────────
            shortlist = []
            for cand in matched:
                cid = cand["id"]
                ms = cand.get("match_score", 0)
                out = outreach.get(cid, {})
                ins = out.get("interest_score", 0)
                cs = round((mw / 100) * ms + (iw / 100) * ins, 1)
                p = cand.get("profile", {})
                shortlist.append({
                    "id": cid, "name": cand.get("name",""), "title": p.get("title",""),
                    "current_company": p.get("current_company",""), "experience_years": p.get("experience_years",0),
                    "location": p.get("location",""), "availability": p.get("availability",""),
                    "salary_expectation": p.get("salary_expectation",""),
                    "match_score": ms, "interest_score": ins, "composite_score": cs,
                    "composite_grade": grade(cs), "interest_level": out.get("interest_level","N/A"),
                    "match_grade": cand.get("match_grade",""), "matched_skills": cand.get("matched_skills",[]),
                    "missing_critical_skills": cand.get("missing_critical_skills",[]),
                    "match_reasoning": cand.get("match_reasoning",""), "red_flags": cand.get("red_flags",[]),
                    "interest_reasoning": out.get("interest_reasoning",""),
                    "next_action": out.get("next_action","Review profile"),
                    "engagement_signals": out.get("engagement_signals",[]),
                    "risk_factors": out.get("risk_factors",[]),
                    "conversation": out.get("conversation",[]), "profile": p,
                })
            shortlist.sort(key=lambda x: x["composite_score"], reverse=True)
            st.session_state["shortlist"] = shortlist
            st.session_state["step"] = 5
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — RESULTS
# ══════════════════════════════════════════════════════════════════════════════
if step == 5:
    parsed_jd = st.session_state["parsed_jd"]
    matched    = st.session_state["matched"]
    outreach   = st.session_state["outreach"]
    shortlist  = st.session_state["shortlist"]

    if st.button("🔄 Scout Another Role"):
        for k in ["step","parsed_jd","matched","outreach","shortlist","sample_jd","jd_text"]:
            st.session_state[k] = None
        st.session_state["step"] = 0
        st.rerun()

    top = shortlist[0] if shortlist else {}
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-box"><div class="metric-val">{len(matched)}</div><div class="metric-label">Candidates Scored</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-box"><div class="metric-val">{len(outreach)}</div><div class="metric-label">Outreach Simulated</div></div>', unsafe_allow_html=True)
    with c3:
        avg = round(sum(c.get("match_score", 0) for c in shortlist) / max(len(shortlist), 1), 1)
        st.markdown(f'<div class="metric-box"><div class="metric-val">{avg}</div><div class="metric-label">Avg Match Score</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-box"><div class="metric-val">{top.get("composite_score",0)}</div><div class="metric-label">Top Composite Score</div></div>', unsafe_allow_html=True)
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Ranked Shortlist", "🔍 Match Details", "💬 Outreach Conversations", "📋 Parsed JD"])

    with tab1:
        st.markdown("### 🏆 Final Ranked Shortlist")
        for rank, cand in enumerate(shortlist, 1):
            cs, ms, ins = cand["composite_score"], cand["match_score"], cand["interest_score"]
            with st.container():
                st.markdown(f'<div class="rank-card">', unsafe_allow_html=True)
                ci, cs_ = st.columns([3, 2])
                with ci:
                    st.markdown(f"**#{rank} {cand['name']}** — {cand['title']} @ {cand['current_company']}")
                    st.caption(f"📍 {cand['location']} · {cand['experience_years']} yrs · {cand['availability']}")
                    st.caption(f"💰 {cand['salary_expectation']}")
                    st.markdown(f"**{cand['composite_grade']}**  |  Interest: **{cand.get('interest_level','N/A')}**")
                    st.caption(f"🎯 {cand['next_action']}")
                with cs_:
                    bar(cs, "Composite Score", sc(cs))
                    bar(ms, "Match Score", sc(ms))
                    bar(ins, "Interest Score", sc(ins))
                with st.expander("🔎 Details"):
                    ea, eb = st.columns(2)
                    with ea:
                        if cand.get("matched_skills"):
                            st.markdown("**Matched Skills**")
                            pills(cand["matched_skills"])
                        if cand.get("missing_critical_skills"):
                            st.markdown("**Missing Skills**")
                            pills(cand["missing_critical_skills"], "skill-miss")
                    with eb:
                        st.markdown("**Match Reasoning**")
                        st.write(cand.get("match_reasoning", ""))
                        if cand.get("interest_reasoning"):
                            st.markdown("**Interest Reasoning**")
                            st.write(cand["interest_reasoning"])
                    if cand.get("red_flags"):
                        st.warning("⚠️ " + " · ".join(cand["red_flags"]))
                st.markdown("</div>", unsafe_allow_html=True)
        st.divider()
        export = [{"rank": i+1, "name": c["name"], "title": c["title"], "company": c["current_company"],
                   "match_score": c["match_score"], "interest_score": c["interest_score"],
                   "composite_score": c["composite_score"], "grade": c["composite_grade"],
                   "next_action": c["next_action"]} for i, c in enumerate(shortlist)]
        st.download_button("⬇️ Download Shortlist JSON", data=json.dumps(export, indent=2),
                           file_name="shortlist.json", mime="application/json")

    with tab2:
        st.markdown("### 🔍 Match Analysis")
        for cand in matched:
            ms = cand.get("match_score", 0)
            p = cand.get("profile", {})
            with st.expander(f"**{cand['name']}** — {ms}/100 · {p.get('title','')}"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.write(p.get("bio", ""))
                    if cand.get("matched_skills"):
                        st.markdown("**Matched Skills**")
                        pills(cand["matched_skills"])
                    if cand.get("missing_critical_skills"):
                        st.markdown("**Missing**")
                        pills(cand["missing_critical_skills"], "skill-miss")
                    st.write(cand.get("match_reasoning", ""))
                with c2:
                    bar(ms, "Match Score", sc(ms))
                    st.write(f"**Company:** {p.get('current_company','')}")
                    st.write(f"**Experience:** {p.get('experience_years','')} yrs")
                    st.write(f"**Location:** {p.get('location','')}")
                    status = "🟢 Open" if p.get("open_to_new_roles") else "🔴 Not looking"
                    st.write(f"**Status:** {status}")

    with tab3:
        st.markdown("### 💬 Outreach Conversations")
        if not outreach:
            st.info("No outreach simulations available.")
        for cid, result in outreach.items():
            cname = next((c["name"] for c in matched if c["id"] == cid), cid)
            ins = result.get("interest_score", 0)
            il = result.get("interest_level", "")
            with st.expander(f"**{cname}** — Interest: {ins}/100 · {il}"):
                chat(result.get("conversation", []))
                st.divider()
                ca, cb = st.columns(2)
                with ca:
                    bar(ins, "Interest Score", sc(ins))
                    st.write(f"**Next Action:** {result.get('next_action','')}")
                with cb:
                    if result.get("engagement_signals"):
                        st.markdown("**Engagement Signals**")
                        for sig in result["engagement_signals"]:
                            st.markdown(f"- {sig}")
                    if result.get("risk_factors"):
                        st.markdown("**Risk Factors**")
                        for rf in result["risk_factors"]:
                            st.markdown(f"- {rf}")
                st.write(result.get("interest_reasoning", ""))

    with tab4:
        st.markdown("### 📋 Parsed JD")
        c1, c2 = st.columns(2)
        with c1:
            for k, label in [("role_title","Role"),("seniority","Seniority"),("domain","Domain"),
                              ("location","Location"),("work_mode","Work Mode"),("salary_range","Salary")]:
                if parsed_jd.get(k):
                    st.markdown(f"**{label}:** {parsed_jd[k]}")
        with c2:
            if parsed_jd.get("required_skills"):
                st.markdown("**Required Skills**")
                pills(parsed_jd["required_skills"])
            if parsed_jd.get("nice_to_have_skills"):
                st.markdown("**Nice to Have**")
                pills(parsed_jd["nice_to_have_skills"])
        st.divider()
        st.json(parsed_jd)
