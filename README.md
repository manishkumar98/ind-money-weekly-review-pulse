# INDmoney Weekly App Review Pulse

An end-to-end AI pipeline that automatically collects, analyzes, and distributes a weekly product pulse from INDmoney app reviews — completely hands-free, every Saturday.

**Live URLs**
- Subscribe page: https://ind-money-weekly-review-pulse.vercel.app
- Dashboard: https://ind-money-weekly-review-pulse.vercel.app/dashboard.html
- Backend API: https://ind-money-weekly-review-pulse.onrender.com

---

## What it does

Every week, the system:
1. Scrapes the latest INDmoney reviews from Google Play Store and Apple App Store
2. Strips all personal information (PII) from the reviews
3. Sends the cleaned data to Groq (Llama 3) which extracts themes, quotes, and action ideas
4. Uses Gemini to draft a markdown notes file and a formatted email
5. Saves outputs to disk and updates the public dashboard
6. Sends the weekly pulse email to the configured recipient
7. Publishes the updated dashboard to Vercel automatically via a git push

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   GitHub Actions (Cron)                  │
│              Every Saturday 10:00 AM IST                 │
└───────────────────────┬─────────────────────────────────┘
                        │
          ┌─────────────▼──────────────┐
          │   Phase 1: Data Ingestion   │
          │  Google Play + App Store    │
          │  Scraper → PII Sanitizer    │
          └─────────────┬──────────────┘
                        │ sanitized_indmoney_reviews.csv
          ┌─────────────▼──────────────┐
          │  Phase 2: LLM Processing    │
          │  Groq API (Llama 3)         │
          │  → themes, quotes,          │
          │    weekly_note, actions     │
          └─────────────┬──────────────┘
                        │ weekly_pulse_output.json
          ┌─────────────▼──────────────┐
          │  Phase 3: MCP Integration   │
          │  Gemini API (tool calling)  │
          │  → weekly_pulse_notes.md    │
          │  → email_draft.txt          │
          └─────────────┬──────────────┘
                        │
          ┌─────────────▼──────────────┐
          │  Phase 4: Orchestration     │
          │  main_orchestrator.py       │
          │  Ties phases 1-3 together   │
          │  with approval gates        │
          └─────────────┬──────────────┘
                        │
          ┌─────────────▼──────────────┐
          │  Phase 5: Email Sender      │
          │  email_sender.py            │
          │  Resend API (cloud)         │
          │  Gmail SMTP (local)         │
          │  → HTML poster email sent   │
          └─────────────┬──────────────┘
                        │
          ┌─────────────▼──────────────┐
          │  Phase 6: Web App           │
          │  update_dashboard.py        │
          │  Injects new data into      │
          │  dashboard.html → git push  │
          │  → Vercel auto-deploys      │
          └────────────────────────────┘

Frontend (Vercel)          Backend (Render + Docker)
─────────────────          ─────────────────────────
index.html                 FastAPI app.py
dashboard.html             POST /api/send-email
                           POST /api/subscribe
```

---

## Project Structure

```
ind-money-weekly-pulse-view/
│
├── Phase1_Data_Ingestion/
│   └── phase1_data_ingestion.py     # Scrapes + sanitizes reviews
│
├── Phase2_LLM_Processing/
│   ├── phase2_llm_processing.py     # Groq API analysis
│   └── weekly_pulse_output.json     # Output: themes, quotes, actions
│
├── Phase3_MCP_Integration/
│   ├── phase3_mcp_orchestration.py  # Gemini tool-calling
│   ├── mcp_tools.py                 # MCP tool definitions
│   ├── email_draft.txt              # Output: email draft
│   └── weekly_pulse_notes.md        # Output: markdown notes (appended weekly)
│
├── Phase4_Orchestration/
│   └── main_orchestrator.py         # End-to-end pipeline runner
│
├── Phase5_Email_UI/
│   ├── email_sender.py              # Sends HTML email via Resend/SMTP
│   ├── generate_poster.py           # Standalone HTML poster generator
│   └── poster.html                  # Generated email poster (local preview)
│
├── Phase6_Web_App/
│   ├── backend/
│   │   ├── app.py                   # FastAPI backend (Render)
│   │   └── requirements.txt
│   ├── frontend/
│   │   ├── index.html               # Subscribe page (Vercel)
│   │   ├── dashboard.html           # 3-tab pulse dashboard (Vercel)
│   │   └── vercel.json              # Vercel routing config
│   └── update_dashboard.py          # Injects weekly data into dashboard.html
│
├── Docs/
│   ├── architecture_plan.md         # Full technical architecture
│   └── layman_project_overview.md   # Plain-English overview
│
├── .github/workflows/
│   └── weekly_pulse.yml             # GitHub Actions scheduler
│
├── Dockerfile                       # Docker image for Render deployment
├── render.yaml                      # Render service config
├── requirements.txt                 # Python deps for pipeline + GitHub Actions
├── run_weekly.sh                    # Local manual run script
└── .env                             # API keys (never committed)
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Data scraping | `google-play-scraper`, `app-store-scraper` | Pull reviews from stores |
| Data processing | `pandas` | Clean, filter, deduplicate |
| LLM (fast inference) | Groq API — Llama 3 | Theme extraction, summarization |
| LLM (tool calling) | Gemini API | MCP orchestration, draft generation |
| Email delivery | Resend API (cloud), Gmail SMTP (local) | Send HTML pulse emails |
| Backend API | FastAPI + Uvicorn | Send-email endpoint |
| Frontend | Vanilla HTML/CSS/JS | Subscribe page + dashboard |
| Hosting (frontend) | Vercel | Static site, auto-deploys on push |
| Hosting (backend) | Render (Docker) | FastAPI container |
| Scheduler | GitHub Actions (cron) | Weekly pipeline trigger |
| Secrets | GitHub Secrets + `.env` | API key management |

---

## Setup & Running Locally

### Prerequisites
- Python 3.11+
- A `.env` file at the project root with:

```
GROQ_API_KEY=your_key
GEMINI_API_KEY=your_key
EMAIL_SENDER=your_gmail@gmail.com
EMAIL_PASSWORD=your_app_password
RESEND_API_KEY=your_key          # optional, for cloud email
```

### Install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run the full pipeline
```bash
# Interactive (prompts for approval at each gate)
python Phase4_Orchestration/main_orchestrator.py

# Non-interactive (auto-approves both gates — used by scheduler)
printf "Y\nY\n" | python Phase4_Orchestration/main_orchestrator.py
```

### Start the backend API locally
```bash
./venv/bin/uvicorn Phase6_Web_App.backend.app:app --reload --port 8000
```

### Update the dashboard with latest data
```bash
python3 Phase6_Web_App/update_dashboard.py
```

---

## Deployment

### Frontend → Vercel
- Connect the `Phase6_Web_App/frontend/` directory to Vercel
- Vercel auto-deploys on every push to `main`
- No environment variables needed on Vercel

### Backend → Render
- Render builds and runs the `Dockerfile` from the repo root
- Set these environment variables on Render:
  - `EMAIL_SENDER`
  - `EMAIL_PASSWORD`
  - `RESEND_API_KEY`
  - `ALLOWED_ORIGINS` (set to your Vercel URL, e.g. `https://ind-money-weekly-review-pulse.vercel.app`)

### GitHub Actions Scheduler
- Runs every Saturday at 10:00 AM IST (04:30 UTC)
- Set these GitHub Secrets: `GROQ_API_KEY`, `GEMINI_API_KEY`, `EMAIL_SENDER`, `EMAIL_PASSWORD`, `ANTHROPIC_API_KEY`
- Can also be triggered manually from the Actions tab

---

## Weekly Automation Flow

```
Saturday 10:00 AM IST
        │
        ▼
GitHub Actions triggers
        │
        ├─ Run pipeline (Phase 1 → 2 → 3 → 4)
        │       └─ Generates: weekly_pulse_output.json
        │                     email_draft.txt
        │                     weekly_pulse_notes.md
        │
        ├─ Send email via Resend API
        │
        ├─ Run update_dashboard.py
        │       └─ Injects new data into dashboard.html
        │
        └─ git commit + push
                └─ Vercel detects push → auto-deploys new dashboard
```

---

## Key Design Decisions

**Why embed data in HTML instead of fetching from API?**
The dashboard reads data that changes once a week. Embedding it as JS constants in the HTML means zero API calls for page load, no CORS issues, no dependency on the backend being awake (Render free tier sleeps after 15 min). The backend is only called when a user clicks Send Email.

**Why Resend instead of Gmail SMTP on Render?**
Render's free tier blocks outbound port 587 (SMTP). Resend provides an HTTP API for sending email that works on any host. Gmail SMTP is kept as a fallback for local development.

**Why GitHub Actions instead of a cron server?**
Free, reliable, zero infrastructure to maintain. The pipeline runs in a GitHub-managed Ubuntu environment with all secrets securely stored.
