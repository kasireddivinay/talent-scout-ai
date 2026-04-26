# 🎯 TalentScout AI

> AI-Powered Talent Scouting & Engagement Agent  
> **Catalyst Hackathon · Deccan AI · April 2025**

---

## 🚀 Live Demo

| | |
|---|---|
| **Deployed App** | _[Add your Streamlit Cloud / Hugging Face URL here]_ |
| **Demo Video** | _[Add your Loom / YouTube link here]_ |
| **GitHub Repo** | _[Add your repo URL here]_ |

---

## 📌 Problem Statement

Recruiters spend hours:
- Reading through dozens of profiles manually
- Sending cold outreach with no sense of candidate interest
- Manually ranking candidates without a consistent framework

**TalentScout AI** solves all three — automatically.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TalentScout AI Pipeline                         │
└─────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐
  │  Recruiter   │  Pastes raw Job Description (JD) into the Streamlit UI
  └──────┬───────┘
         │ raw JD text
         ▼
┌────────────────────┐
│   JD Parser Agent  │  Claude parses JD → structured JSON
│  (Claude Sonnet)   │  Extracts: role, seniority, required skills,
└────────┬───────────┘  nice-to-have, experience range, location, domain
         │ parsed_jd: dict
         ▼
┌──────────────────────────┐
│  Candidate Matcher Agent │  Claude scores ALL 15 candidates against JD
│    (Claude Sonnet)       │  in a single batched API call
│                          │  Returns: match_score, grade, reasoning,
└──────────┬───────────────┘  matched/missing skills, red flags
           │ top_n candidates ranked by match_score
           ▼
┌──────────────────────────┐
│  Outreach Simulation     │  Claude simulates a 4-turn conversation
│     Agent                │  for each of the top N candidates.
│  (Claude Sonnet)         │  Plays BOTH recruiter and candidate roles.
│                          │  Candidate responses are profile-driven.
└──────────┬───────────────┘  Returns: conversation, interest_score,
           │ outreach results  interest_level, next_action
           ▼
┌──────────────────────────┐
│   Composite Scorer       │  Merges match + interest scores
│                          │  Composite = 60% Match + 40% Interest
└──────────┬───────────────┘  (configurable via sidebar)
           │ ranked shortlist
           ▼
  ┌──────────────┐
  │  Streamlit   │  Recruiter sees:
  │  Dashboard   │  • Ranked shortlist with composite scores
  │              │  • Match analysis with skill explanations
  │              │  • Full conversation transcripts
  │              │  • Next action recommendations
  │              │  • JSON export
  └──────────────┘
```

---

## 🧠 Scoring Logic

### 1. Match Score (0–100)

Computed by Claude with these weighted dimensions:

| Dimension | Weight | What it measures |
|---|---|---|
| Skills overlap | 40% | Required skills matched > nice-to-have |
| Experience fit | 25% | Years of experience vs. required range + relevance |
| Domain/industry fit | 20% | Has the candidate worked in a relevant domain? |
| Logistics | 15% | Location, work mode, open to new roles, availability |

**Grade mapping:**
- `Excellent` → 85–100
- `Strong` → 70–84
- `Good` → 55–69
- `Fair` → 40–54
- `Weak` → below 40

### 2. Interest Score (0–100)

Generated from a simulated 4-turn LinkedIn/WhatsApp conversation where Claude:
- Plays the **Recruiter** (personalized, references candidate's background)
- Plays the **Candidate** (responses driven by their profile: open_to_new_roles, salary expectations, location fit)

Interest is assessed based on:
- Response tone and enthusiasm
- Questions asked (signals genuine curiosity)
- Hesitations or concerns raised
- Candidate's history of openness

**Level mapping:**
- `Very High` → 85–100
- `High` → 70–84
- `Moderate` → 50–69
- `Low` → 25–49
- `Not Interested` → 0–24

### 3. Composite Score (0–100)

```
Composite = (Match Weight%) × Match Score + (Interest Weight%) × Interest Score

Default: Composite = 0.60 × Match + 0.40 × Interest
```

The weights are **configurable** via the sidebar slider (40–80% for Match, remainder for Interest).

**Final Grade:**
- `🏆 Top Pick` → 82+
- `⭐ Strong` → 68–81
- `✅ Good Fit` → 52–67
- `⚠️ Borderline` → 38–51
- `❌ Weak` → below 38

---

## 🗂️ Project Structure

```
talent_scout_ai/
├── app.py                    # Main Streamlit application (UI + orchestration)
├── requirements.txt          # Python dependencies
├── .env.example              # API key template
├── README.md                 # This file
│
├── agents/
│   ├── jd_parser.py          # JD → structured JSON via Claude
│   ├── matcher.py            # Batch candidate scoring via Claude
│   ├── outreach.py           # Conversation simulation via Claude
│   └── scorer.py             # Composite score + grade calculation
│
└── data/
    └── candidates.py         # Mock candidate pool (15 realistic profiles)
```

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.10+
- An Anthropic API key ([get one here](https://console.anthropic.com/))

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/talent-scout-ai.git
cd talent-scout-ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 5. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Environment Variables

```
ANTHROPIC_API_KEY=sk-ant-...
```

---

## 🎮 How to Use

1. **Paste a Job Description** into the text area (or load a sample from the sidebar)
2. Click **"Analyze & Scout Candidates"**
3. Watch as the agent:
   - Parses the JD into structured fields
   - Scores all 15 candidates from the pool
   - Simulates outreach conversations with the top N candidates
4. Explore results across 4 tabs:
   - **🏆 Ranked Shortlist** — final ranked list with composite scores
   - **🔍 Match Details** — per-candidate skill breakdown and reasoning
   - **💬 Outreach Conversations** — simulated chat transcripts
   - **📋 Parsed JD** — structured JD data with raw JSON
5. **Download** the shortlist as JSON

---

## 📊 Sample Input / Output

### Sample Input (Job Description)

```
We are hiring a Senior Backend Engineer at FinFlow (FinTech startup, Series B).

Role: Senior Backend Engineer
Location: Bangalore (Hybrid)
Experience: 5-8 years

Requirements:
- Strong proficiency in Python (FastAPI or Django)
- Experience with PostgreSQL, Redis, and Kafka
- Kubernetes and Docker in production
- Microservices architecture design
- AWS (EC2, RDS, Lambda, S3)

Nice to have:
- FinTech / payments domain experience
- Compliance experience (PCI-DSS)

Compensation: ₹35–50 LPA
```

### Sample Output (Ranked Shortlist)

```json
[
  {
    "rank": 1,
    "name": "Arjun Sharma",
    "title": "Senior Backend Engineer",
    "company": "Flipkart",
    "match_score": 91,
    "interest_score": 82,
    "composite_score": 87.4,
    "grade": "🏆 Top Pick",
    "next_action": "Schedule 30-min intro call",
    "availability": "2 months notice",
    "salary": "₹35–45 LPA"
  },
  {
    "rank": 2,
    "name": "Vikram Singh",
    "title": "DevOps / Cloud Engineer",
    "company": "ThoughtWorks",
    "match_score": 74,
    "interest_score": 88,
    "composite_score": 79.6,
    "grade": "⭐ Strong",
    "next_action": "Send detailed JD + await response",
    "availability": "Immediately available",
    "salary": "₹28–38 LPA"
  },
  ...
]
```

### Sample Outreach Conversation

```
🧑‍💼 Recruiter:
Hi Arjun! I came across your profile and was impressed by your work at Flipkart —
specifically the microservices migration you led serving 10M+ users. We have a Senior
Backend Engineering role at a Series B FinTech that's almost tailor-made for your stack
(Python, FastAPI, Kafka, K8s). Would love to share more details — open to a quick chat?

👤 Arjun Sharma:
Hi! Thanks for reaching out. The role sounds interesting, especially the FinTech angle.
I'm currently at Flipkart but I'm open to hearing more — what's the company and what
does the product do exactly? Also, is this a leadership role or mostly IC?

🧑‍💼 Recruiter:
The company is FinFlow — they process ₹500Cr+ in monthly transactions for SMBs.
It's a senior IC role with a clear path to tech lead. The team is 8 engineers reporting
to the CTO. Compensation is ₹35–50 LPA with meaningful ESOPs.

👤 Arjun Sharma:
That sounds genuinely interesting! The scale and domain match what I'm looking for next.
₹35–50 LPA works for me. I'm on a 2-month notice but could potentially negotiate to
6 weeks. Could you share the full JD? Happy to get on a call this week.

→ Interest Score: 82/100 (High)
→ Next Action: Schedule exploratory call
```

---

## 🔧 Agent Details

### JD Parser Agent
- **Input:** Raw job description text
- **Output:** Structured JSON (role, skills, experience, location, domain, responsibilities)
- **Model:** `claude-sonnet-4-20250514`
- **Prompt strategy:** Strict JSON schema enforcement with few-shot field specification

### Candidate Matcher Agent
- **Input:** Parsed JD + full candidate pool
- **Output:** All candidates scored with match score, grade, skill analysis, reasoning
- **Model:** `claude-sonnet-4-20250514`
- **Efficiency:** Single batched API call for all candidates (avoids N×API calls)
- **Explainability:** Per-candidate reasoning + matched/missing skills highlighted

### Outreach Simulation Agent
- **Input:** Candidate profile + parsed JD
- **Output:** 4-turn conversation + interest score + next action
- **Model:** `claude-sonnet-4-20250514`
- **Design:** Claude plays both recruiter and candidate. Candidate persona is driven by: `open_to_new_roles`, salary expectations, work mode preference, location compatibility

### Composite Scorer
- **Input:** Match scores + interest scores + configurable weights
- **Output:** Final ranked shortlist sorted by composite score
- **Formula:** `Composite = W_match × Match + W_interest × Interest`
- **Configurable:** Weights adjustable 40–80% via sidebar

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **UI** | Streamlit |
| **AI Engine** | Anthropic Claude Sonnet (`claude-sonnet-4-20250514`) |
| **Language** | Python 3.10+ |
| **Candidate Data** | Curated mock pool (15 realistic Indian tech profiles) |
| **Deployment** | Streamlit Community Cloud (or local) |

---

## 🗺️ Future Roadmap

- [ ] **Real candidate sourcing** via LinkedIn API / Indeed MCP integration
- [ ] **ATS integration** — push shortlist to Lever, Greenhouse, Zoho Recruit
- [ ] **Custom candidate upload** — paste CSV of profiles
- [ ] **Multi-round conversation** — deeper engagement with top candidates
- [ ] **Bias detection** — flag potentially biased JD language
- [ ] **Team fit scoring** — match candidate personality to team culture
- [ ] **Email/WhatsApp outreach** — trigger real messages from shortlist

---

## 👥 Team

Built for Catalyst Hackathon by Deccan AI · April 2025

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
