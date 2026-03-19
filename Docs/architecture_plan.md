# Architecture Plan: INDmoney AI Review Workflow & Weekly Pulse

This document is the single source of truth for the technical architecture of the INDmoney Weekly Pulse system. It covers all phases as built and deployed, including everything added after the initial design.

---

## System Overview

A fully automated, 6-phase AI pipeline that:
1. Scrapes INDmoney app reviews from the Play Store and App Store
2. Cleans and sanitizes the data
3. Uses Groq (Llama 3) to extract themes, quotes, and action ideas
4. Uses Gemini (MCP tool-calling) to draft notes and emails
5. Sends a styled HTML email via Resend API
6. Updates a public Vercel dashboard and exposes a FastAPI backend on Render

The entire pipeline runs every Saturday at 10:00 AM IST via GitHub Actions — zero manual intervention required.

---

## End-to-End Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│              GitHub Actions Cron (Saturday 04:30 UTC)            │
└──────────────────────────────┬──────────────────────────────────┘
                               │
               ┌───────────────▼───────────────┐
               │       Phase 4: Orchestrator    │
               │      main_orchestrator.py      │
               │  (ties phases 1-3, auto Y/Y)   │
               └──┬────────────┬───────────────┘
                  │            │
    ┌─────────────▼──┐   ┌─────▼──────────────────┐
    │ Phase 1        │   │ Phase 2                  │
    │ Data Ingestion │   │ LLM Processing (Groq)    │
    │                │   │                          │
    │ Play Store ──► │   │ Input: sanitized CSV     │
    │ App Store  ──► │   │ Model: Llama 3 (Groq)    │
    │ Sanitizer      │   │ Output:                  │
    │ PII removal    │   │  weekly_pulse_output.json│
    │ Deduplication  │   │  fee_explanation.json    │
    └───────┬────────┘   └──────────┬───────────────┘
            │                       │
            └──────────┬────────────┘
                       │
            ┌──────────▼──────────────┐
            │ Phase 3                  │
            │ MCP Integration (Gemini) │
            │                          │
            │ Tool 1: Notes Appender   │
            │  → weekly_pulse_notes.md │
            │ Tool 2: Email Drafter    │
            │  → email_draft.txt       │
            │                          │
            │ Human gate (Y/N) in      │
            │ interactive mode;        │
            │ auto-approved in CI      │
            └──────────┬───────────────┘
                       │
            ┌──────────▼──────────────┐
            │ Phase 5: Email Sender    │
            │ email_sender.py          │
            │                          │
            │ Generates HTML poster    │
            │ Sends via Resend API     │
            │ (Gmail SMTP fallback)    │
            └──────────┬───────────────┘
                       │
            ┌──────────▼──────────────┐
            │ Phase 6: Dashboard Update│
            │ update_dashboard.py      │
            │                          │
            │ Reads output files       │
            │ Injects into             │
            │ dashboard.html as JS     │
            │ constants                │
            │ git commit + push        │
            └──────────┬───────────────┘
                       │
           ┌───────────▼────────────────────┐
           │         Vercel                  │
           │  Detects push → auto-deploys   │
           │                                 │
           │  index.html  (subscribe page)  │
           │  dashboard.html (3-tab viewer) │
           └─────────────────────────────────┘

                  On-demand (user action)
           ┌─────────────────────────────────┐
           │  Browser → POST /api/send-email  │
           │         ▼                        │
           │    Render (Docker)               │
           │    FastAPI app.py                │
           │    BackgroundTask: send email    │
           └─────────────────────────────────┘
```

---

## Phase-by-Phase Technical Specification

### Phase 1: Data Ingestion
**File:** `Phase1_Data_Ingestion/phase1_data_ingestion.py`
**Output:** `Phase1_Data_Ingestion/sanitized_indmoney_reviews.csv`

- Scrapes Google Play Store (`com.indwealth.rn`) and Apple App Store
- Fetches last 8–12 weeks of reviews; samples up to 3,000 with balanced star ratings
- Sanitization pipeline:
  - RegEx PII scan: masks emails, phone numbers, names
  - Emoji removal via `emoji` library
  - Minimum length filter: discard reviews under 5 words
  - Deduplication: exact-match on review text

---

### Phase 2: LLM Processing
**File:** `Phase2_LLM_Processing/phase2_llm_processing.py`
**Output:** `Phase2_LLM_Processing/weekly_pulse_output.json`, `Phase2_LLM_Processing/fee_explanation.json`

**Model:** Groq API — Llama 3
**Token constraint:** Input payload capped at ~12,000 tokens (~9,000 words); dataset dynamically sampled to fit

**Prompt strategy:**
- System: "You are an expert INDmoney Product Manager. Analyze user reviews. Do not hallucinate."
- User: "Output strict JSON with: `themes` (max 5), `top_3_themes`, `quotes` (exactly 3, real), `weekly_note` (max 250 words), `action_ideas` (exactly 3)."

**Output validation:**
- JSON parse success check
- `weekly_note` word count ≤ 250 (retry on violation)
- `quotes` array length == 3
- `action_ideas` array length == 3

**Secondary output:** `fee_explanation.json` — structured explanation of one common INDmoney fee scenario (e.g. US stocks withdrawal).

---

### Phase 3: MCP Integration
**File:** `Phase3_MCP_Integration/phase3_mcp_orchestration.py`, `Phase3_MCP_Integration/mcp_tools.py`
**Output:** `Phase3_MCP_Integration/weekly_pulse_notes.md`, `Phase3_MCP_Integration/email_draft.txt`

**Model:** Gemini API (tool-calling mode)

**MCP Tools defined:**
- `Document_Appender` — appends formatted weekly summary to `weekly_pulse_notes.md`
- `Email_Drafter` — generates a formatted plain-text email draft in `email_draft.txt`

**Approval gate:**
- In interactive (local) mode: pauses execution, shows exact tool arguments, waits for `Y/N` before executing
- In CI/automated mode: `printf "Y\nY\n"` pre-approves both gates
- Gate logic: intercepts Gemini's `function_call`, validates schema, conditionally executes

---

### Phase 4: Orchestration
**File:** `Phase4_Orchestration/main_orchestrator.py`

Ties Phases 1–3 into a single runnable script:
1. Call Phase 1 → produce sanitized CSV
2. Call Phase 2 → produce pulse JSON + fee JSON
3. Print outputs to console
4. Present approval gate → call Phase 3 Tool 1 (notes)
5. Present approval gate → call Phase 3 Tool 2 (email draft)

Used by both local `run_weekly.sh` and GitHub Actions CI.

---

### Phase 5: Email Sender
**File:** `Phase5_Email_UI/email_sender.py`
**Also:** `Phase5_Email_UI/generate_poster.py`

**Email delivery:**
- Primary (cloud/Render): Resend API — HTTP-based, not blocked by cloud hosting providers
- Fallback (local): Gmail SMTP via `smtplib` on port 587

**HTML email generation:**
- Reads `weekly_pulse_output.json`
- Generates a styled HTML email with:
  - Personalized greeting (recipient name)
  - User quotes with avatar icons (`ui-avatars.com`)
  - Weekly summary note
  - Top themes list
  - Action ideas list
  - Footer with branding
- Saves as `Phase5_Email_UI/poster.html` (standalone preview)

**Environment variables required:**
- `RESEND_API_KEY` — if set, uses Resend; otherwise falls back to SMTP
- `EMAIL_SENDER`, `EMAIL_PASSWORD` — for SMTP fallback

---

### Phase 6: Web Application
**Backend:** `Phase6_Web_App/backend/app.py` → deployed on **Render** (Docker)
**Frontend:** `Phase6_Web_App/frontend/` → deployed on **Vercel** (static)
**Dashboard updater:** `Phase6_Web_App/update_dashboard.py`

#### Backend (FastAPI on Render)

**Path detection (Docker vs local):**
```python
_this_dir = Path(__file__).resolve().parent
_local_root = _this_dir.parent.parent   # ind-money-weekly-pulse-view/
_docker_root = _this_dir                # Docker: /app
project_root = _local_root if (_local_root / "Phase5_Email_UI").exists() else _docker_root
```

**Endpoints:**
| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/subscribe` | Subscribe user, send email in background |
| POST | `/api/send-email` | Send pulse email to any address (dashboard) |

**Note:** `/api/pulse-data`, `/api/email-draft`, `/api/notes` endpoints exist in code but are no longer called by the frontend. Data is embedded directly in `dashboard.html`.

**CORS:**
- `allow_credentials=False` (required when `allow_origins=["*"]`)
- Origins configurable via `ALLOWED_ORIGINS` env var (comma-separated)

**Email sending:** Uses `BackgroundTasks` to avoid request timeout on Render's free tier (email sending can take 5–10s).

**Docker image:** Built from `Dockerfile` at repo root. Copies:
- `Phase6_Web_App/backend/app.py`
- `Phase5_Email_UI/` (email sender)
- `Phase2_LLM_Processing/weekly_pulse_output.json`
- `Phase3_MCP_Integration/email_draft.txt`
- `Phase3_MCP_Integration/weekly_pulse_notes.md`

#### Frontend (Vercel)

**`index.html`** — Subscribe page
- Glassmorphism UI, animated background blobs
- Name + email form → POST `/api/subscribe` → success feedback

**`dashboard.html`** — 3-tab weekly pulse viewer
- Tab 1: Email Draft (plain text)
- Tab 2: Markdown Report (rendered with `marked.js`)
- Tab 3: Pulse Poster (themes, quotes, actions, weekly note)
- Send Email form → POST `https://ind-money-weekly-review-pulse.onrender.com/api/send-email`

**Key design decision:** All tab content is **baked directly into `dashboard.html` as JavaScript constants**. No API calls are made to load data. This eliminates CORS issues, Render cold-start timeouts, and any dependency on the backend being awake. The only network call is the Send Email button.

**`vercel.json`** — Proxy rewrite:
```json
{ "rewrites": [{ "source": "/api/:path*", "destination": "https://ind-money-weekly-review-pulse.onrender.com/api/:path*" }] }
```

#### Dashboard Updater (`update_dashboard.py`)

Runs as part of the GitHub Actions pipeline after Phase 4. Reads the three output files and injects them into `dashboard.html` using regex replacement on the JS constant blocks:
- `EMAIL_DRAFT` ← `Phase3_MCP_Integration/email_draft.txt`
- `NOTES_MD` ← `Phase3_MCP_Integration/weekly_pulse_notes.md`
- `PULSE_DATA` ← `Phase2_LLM_Processing/weekly_pulse_output.json`

After updating, GitHub Actions commits and pushes → Vercel auto-deploys.

---

## GitHub Actions Workflow

**File:** `.github/workflows/weekly_pulse.yml`
**Trigger:** `cron: '30 4 * * 6'` (Saturday 04:30 UTC = 10:00 AM IST) + `workflow_dispatch` (manual)

**Steps:**
1. Checkout repo
2. Setup Python 3.11 with pip cache
3. `pip install -r requirements.txt`
4. Write `.env` from GitHub Secrets
5. Log run start → `logs/scheduler.log`
6. Run pipeline: `printf "Y\nY\n" | python Phase4_Orchestration/main_orchestrator.py`
7. Send email: `python Phase5_Email_UI/email_sender.py $EMAIL_SENDER`
8. Update dashboard: `python Phase6_Web_App/update_dashboard.py`
9. Git commit + push updated files (dashboard.html + output files)
10. Log result
11. Upload artifacts (output files + log, retained 30 days)

**GitHub Secrets required:**
- `GROQ_API_KEY`
- `GEMINI_API_KEY`
- `ANTHROPIC_API_KEY`
- `EMAIL_SENDER`
- `EMAIL_PASSWORD`

---

## Hosting & Infrastructure

| Component | Platform | Config |
|---|---|---|
| Frontend | Vercel | Root: `Phase6_Web_App/frontend/`, auto-deploy on push to `main` |
| Backend | Render (free tier) | Docker, `Dockerfile` at repo root, auto-deploy on push |
| Pipeline scheduler | GitHub Actions | Free tier, cron weekly |
| Email (cloud) | Resend API | Free tier, `onboarding@resend.dev` sender |
| Email (local) | Gmail SMTP | App password via env var |

**Render free tier caveats:**
- Spins down after 15 minutes of inactivity (cold start ~30–60s on first request)
- SMTP port 587 is blocked → must use Resend API

---

## Data Flow: File Outputs

```
Phase 1 → sanitized_indmoney_reviews.csv
Phase 2 → weekly_pulse_output.json
          fee_explanation.json
Phase 3 → weekly_pulse_notes.md  (appended each week)
          email_draft.txt
Phase 5 → poster.html  (local HTML preview of email)
Phase 6 → dashboard.html  (updated in-place by update_dashboard.py)
          logs/scheduler.log  (appended each run)
```

---

## Security Notes

- `.env` is gitignored; API keys only live in GitHub Secrets and Render env vars
- PII removed from review data before any LLM sees it
- Human approval gate in Phase 3 prevents autonomous tool execution in interactive mode
- `allow_credentials=False` on CORS middleware (required for `allow_origins=["*"]`)
