# Architecture Plan: INDmoney AI Review Workflow & Weekly Pulse

This document is the single source of truth for the technical architecture of the INDmoney Weekly Pulse system. It covers all phases as built and deployed, including everything added after the initial design.

---

## System Overview

A fully automated, 6-phase AI pipeline that:
1. Scrapes INDmoney app reviews from the Play Store and App Store
2. Cleans and sanitizes the data (PII removal, deduplication)
3. Uses Groq (Llama 3) to extract themes, quotes, action ideas, an exit load explainer for SBI Mutual Funds, **and derives word frequencies, sentiment split, and rating distribution for the analytics dashboard**
4. Uses Groq (MCP tool-calling) to draft notes, emails, and append a combined JSON to Google Docs — all approval-gated
5. Sends a styled HTML email via Brevo API — includes Exit Load fee explainer section
6. Updates a public 8-tab Vercel dashboard with all pipeline outputs and exposes a FastAPI send-email endpoint on Render

The entire pipeline runs every Friday at 8:40 PM IST (15:10 UTC) via GitHub Actions — zero manual intervention required.

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
            │ MCP Integration (Groq)   │
            │                          │
            │ Tool 1: Notes Appender   │
            │  → weekly_pulse_notes.md │
            │ Tool 2: Google Doc       │
            │  → appends JSON to GDoc  │
            │ Tool 3: Email Drafter    │
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

**Secondary output:** `fee_explanation.json` — structured exit load explainer for SBI Mutual Funds available on INDmoney.

**Exit Load Explainer (`generate_exit_load_explainer`):**
- Funds covered: SBI Large Cap, Flexicap, ELSS Tax Saver, Small Cap, Midcap, Focused Equity
- Output schema:
  ```json
  {
    "scenario_name": "SBI Mutual Funds — Exit Load",
    "explanation_bullets": ["≤6 factual bullet strings"],
    "source_links": ["2 official sbimf.com URLs"],
    "last_checked": "Month DD, YYYY"
  }
  ```
- Tone: neutral, facts-only, no recommendations or comparisons
- Source links are hardcoded post-generation (LLM output overridden) to guarantee accuracy

---

### Phase 3: MCP Integration
**File:** `Phase3_MCP_Integration/phase3_mcp_orchestration.py`, `Phase3_MCP_Integration/mcp_tools.py`
**Output:** `Phase3_MCP_Integration/weekly_pulse_notes.md`, `Phase3_MCP_Integration/email_draft.txt`, appended entry in Google Doc

**Model:** Groq API — Llama 3 (tool-calling mode)

**Inputs loaded:** `weekly_pulse_output.json` + `fee_explanation.json` (both passed to Groq)

**MCP Tools defined:**

**Tool 1 — `Document_Appender`**
- Appends formatted weekly pulse summary to local `weekly_pulse_notes.md`
- Fields: `weekly_note`, `themes`, `top_3_themes`, `quotes`, `action_ideas`

**Tool 2 — `Google_Doc_Appender`** *(true MCP — server/client split)*
- Uses the **Model Context Protocol (MCP)** via stdio transport — not a direct API call
- Architecture:
  - **MCP Server** (`google_doc_mcp_server.py`) — exposes `append_to_google_doc` tool via JSON-RPC over stdio
  - **MCP Client** (`execute_google_doc_appender` in `mcp_tools.py`) — spawns the server as a subprocess, connects via `ClientSession`, calls the tool
- Payload schema (matches assignment spec exactly):
  ```json
  {
    "date": "YYYY-MM-DD",
    "weekly_pulse": { "...full pulse JSON..." },
    "fee_scenario": "SBI Mutual Funds — Exit Load",
    "explanation_bullets": ["≤6 factual bullets"],
    "source_links": ["2 official sbimf.com URLs"]
  }
  ```
- Auth: `GOOGLE_DOC_ID` + `GOOGLE_SERVICE_ACCOUNT_JSON` env vars (raw JSON or base64)
- MCP SDK: `mcp` v1.26.0 (Anthropic)

**Tool 3 — `Email_Drafter`**
- Writes a plain-text email draft to `email_draft.txt`. No auto-send.
- Subject format (enforced in system prompt): `Weekly Pulse + Fee Explainer — YYYY-MM-DD`
- Body has two mandatory sections:
  - **Section 1 — WEEKLY PULSE**: top themes, 3 user quotes, weekly note, action ideas
  - **Section 2 — FEE EXPLAINER**: fee scenario name, all explanation bullets, source links, last checked date

**Orchestration prompt rules (enforced):**
- Tool 1: weekly pulse fields only
- Tool 2: combined pulse + fee data, exact schema
- Tool 3: subject must match `Weekly Pulse + Fee Explainer — {date}` exactly; body must contain both sections

**Approval gate:**
- In interactive (local) mode: pauses execution, shows exact tool arguments, waits for `Y/N` before executing
- In CI/automated mode: `printf "Y\nY\nY\n"` pre-approves all three gates
- Gate logic: intercepts Groq's `function_call`, validates schema, conditionally executes

---

### Phase 4: Orchestration
**File:** `Phase4_Orchestration/main_orchestrator.py`

Ties Phases 1–3 into a single runnable script:
1. Call Phase 1 → produce sanitized CSV
2. Call Phase 2 → produce pulse JSON + exit load fee JSON
3. Print outputs to console
4. Present approval gate → call Phase 3 Tool 1 (notes)
5. Present approval gate → call Phase 3 Tool 2 (Google Doc append)
6. Present approval gate → call Phase 3 Tool 3 (email draft)

Used by both local `run_weekly.sh` and GitHub Actions CI.

---

### Phase 5: Email Sender
**File:** `Phase5_Email_UI/email_sender.py`
**Also:** `Phase5_Email_UI/generate_poster.py`

**Email delivery (priority order):**
- Primary: Brevo API — HTTP-based, works on Render, sends to any email address, 300 emails/day free tier, sender email verified in Brevo dashboard
- Secondary: Resend API — HTTP-based, but free tier (`onboarding@resend.dev`) limited to sending only to the Resend account owner's email
- Fallback (local only): Gmail SMTP via `smtplib` on port 587 — blocked on Render free tier

**Subject line:** Read from `email_draft.txt` (written by Email_Drafter tool). Format: `Weekly Pulse + Fee Explainer — YYYY-MM-DD`. A run-date suffix `(Mon DD, YYYY)` is appended by `email_sender.py` using `weekly_pulse_output.json` mtime as a fallback guard.

**HTML email generation:**
- Reads `weekly_pulse_output.json` and `fee_explanation.json`
- Generates a styled HTML email with:
  - Personalized greeting (recipient name)
  - User quotes with avatar icons (`ui-avatars.com`)
  - Weekly summary note
  - Top themes list
  - Action ideas list
  - **Exit Load Fee Explainer section** (new):
    - ≤6 factual bullet points on SBI MF exit loads
    - 2 clickable official source links
    - "Last checked: Month DD, YYYY"
  - Footer with branding
- Saves as `Phase5_Email_UI/poster.html` (standalone preview)
- Exit load section is omitted gracefully if `fee_explanation.json` is absent

**Environment variables required:**
- `BREVO_API_KEY` — if set, uses Brevo (primary, recommended for Render)
- `RESEND_API_KEY` — used if Brevo key absent; free tier limited to account email only
- `EMAIL_SENDER`, `EMAIL_PASSWORD` — sender address (used by all methods) + Gmail app password for SMTP fallback

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

**`dashboard.html`** — 8-tab weekly pulse dashboard (Chart.js + vanilla JS)

| Tab | Content | Data source | Pipeline-fed? |
|---|---|---|---|
| 🔒 Approval Gate | Checklist, editable summary, collapsible themes, action buttons, fee explainer toggle | `PULSE_DATA`, `FEE_DATA` | ✅ Yes |
| 📧 Email Draft | Plain text email draft with Section 1 + Section 2 | `EMAIL_DRAFT` | ✅ Yes |
| 📝 Markdown Report | Full appended history rendered with `marked.js` | `NOTES_MD` | ✅ Yes |
| 🖼️ Pulse Poster | Themes, quotes, weekly note, action ideas, fee explainer | `PULSE_DATA`, `FEE_DATA` | ✅ Yes |
| 📊 Analytics | Stat cards, bar/trend toggle chart (Chart.js), category tracker table with ticket management | `PULSE_DATA` | ✅ Yes |
| ☁️ Word Cloud | Frequency word cloud, top 20 keywords with bars, upvoted review cards | `KEYWORDS`, `ANALYTICS_META` | ✅ Yes |
| 🏷️ Categories | Category cards, horizontal distribution chart, sentiment chart, rating distribution chart | `CATEGORIES_DATA`, `ANALYTICS_META` | ✅ Yes |
| ⚡ Ideation | AI Idea Recommender cards, Bug Reporter (search/select/generate report) | `AI_IDEAS` (from `PULSE_DATA`), `NEGATIVE_REVIEWS` | ✅ Yes |

**Key design decision:** All tab content is **baked directly into `dashboard.html` as JavaScript constants**. No API calls are made to load data. This eliminates CORS issues, Render cold-start timeouts, and any dependency on the backend being awake. The only network call is the Send Email button.

**`vercel.json`** — Proxy rewrite:
```json
{ "rewrites": [{ "source": "/api/:path*", "destination": "https://ind-money-weekly-review-pulse.onrender.com/api/:path*" }] }
```

#### Dashboard Updater (`update_dashboard.py`)

Runs as part of the GitHub Actions pipeline after Phase 4. Reads all output files and injects them into `dashboard.html` using regex replacement on JS constant blocks:

| Constant | Source file |
|---|---|
| `EMAIL_DRAFT` | `Phase3_MCP_Integration/email_draft.txt` |
| `NOTES_MD` | `Phase3_MCP_Integration/weekly_pulse_notes.md` |
| `PULSE_DATA` | `Phase2_LLM_Processing/weekly_pulse_output.json` |
| `FEE_DATA` | `Phase2_LLM_Processing/fee_explanation.json` |
| `KEYWORDS` | `Phase2_LLM_Processing/analytics_data.json` → `keywords` |
| `CATEGORIES_DATA` | `Phase2_LLM_Processing/analytics_data.json` → `categories` |
| `NEGATIVE_REVIEWS` | `Phase2_LLM_Processing/analytics_data.json` → `negative_reviews` |
| `ANALYTICS_META` | `Phase2_LLM_Processing/analytics_data.json` → `review_count`, `sentiment`, `rating_dist` |

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
6. Run pipeline: `printf "Y\nY\nY\n" | python Phase4_Orchestration/main_orchestrator.py`
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
- `GOOGLE_DOC_ID` — target Google Doc for weekly appends
- `GOOGLE_SERVICE_ACCOUNT_JSON` — service account credentials with Docs write access

---

## Hosting & Infrastructure

| Component | Platform | Config |
|---|---|---|
| Frontend | Vercel | Root: `Phase6_Web_App/frontend/`, auto-deploy on push to `main` |
| Backend | Render (free tier) | Docker, `Dockerfile` at repo root, auto-deploy on push |
| Pipeline scheduler | GitHub Actions | Free tier, cron weekly |
| Email (cloud) | Brevo API | Free tier, 300/day, any recipient, sender verified in Brevo dashboard |
| Email (fallback) | Resend API | Free tier, limited to Resend account email only |
| Email (local) | Gmail SMTP | App password via env var, blocked on Render |

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
