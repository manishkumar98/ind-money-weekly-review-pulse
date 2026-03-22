# INDmoney Weekly Product Pulse & Fee Explainer

An end-to-end AI pipeline that automatically collects, analyzes, and distributes a weekly product pulse from INDmoney app reviews — completely hands-free, every Saturday.

**Live URLs**
- Subscribe page: https://ind-money-weekly-review-pulse.vercel.app
- Dashboard: https://ind-money-weekly-review-pulse.vercel.app/dashboard.html
- Backend API: https://ind-money-weekly-review-pulse.onrender.com

---

## What It Builds (Assignment Checklist)

### Part A — Weekly Review Pulse ✅

| Requirement | How it's met |
|---|---|
| Input: public reviews CSV (last 8–12 weeks) | `Phase1_Data_Ingestion/phase1_data_ingestion.py` scrapes Google Play + App Store, saves `sanitized_indmoney_reviews.csv` |
| Group reviews into max 5 themes | `Phase2_LLM_Processing/phase2_llm_processing.py` → `themes` list capped at 5 |
| Identify top 3 themes | Same file → `top_3_themes` list, exactly 3 items, validated |
| Extract 3 real user quotes | Same file → `quotes` list, exactly 3 verbatim quotes, validated |
| Generate ≤250-word weekly note | Same file → `weekly_note` string, word count checked programmatically |
| Add 3 action ideas | Same file → `action_ideas` list, exactly 3 items |
| No PII in outputs | PII sanitizer strips names, emails, phone numbers before any LLM call |

### Part B — Fee Explainer (Exit Load) ✅

**Fee scenario chosen:** SBI Mutual Fund Exit Loads (funds available on INDmoney)

Funds covered: SBI Large Cap, SBI Flexicap, SBI ELSS Tax Saver, SBI Small Cap, SBI Midcap, SBI Focused Equity

| Requirement | How it's met |
|---|---|
| ≤6 bullet structured explanation | `generate_exit_load_explainer()` in `phase2_llm_processing.py` — enforces `[:6]` trim post-LLM |
| 2 official source links | Hardcoded from `SBI_MF_SOURCE_URLS` after LLM call (ensures accuracy) |
| "Last checked: [date]" | Added programmatically with `datetime.now()` |
| Neutral, facts-only tone | System prompt: `"Maintain a facts-only tone. Do not make recommendations or comparisons."` |
| No recommendations or comparisons | Enforced by both system prompt and user prompt instructions |

Official source links used:
1. https://www.sbimf.com/en-us/investor-corner
2. https://www.sbimf.com/sbimf-scheme-details/sbi-large-cap-fund-(formerly-known-as-sbi-bluechip-fund)-43

### Required MCP Actions — Approval-Gated ✅

**Where MCP approval happens:** `Phase3_MCP_Integration/phase3_mcp_orchestration.py` → `human_approval_gate()`

Before each tool call, the system:
1. Validates the LLM-proposed payload against the tool schema
2. Pretty-prints the full payload to the terminal
3. Halts and waits for explicit `Y` / `N` input
4. Only executes on `Y` — `N` aborts that action only

Three approval gates, one per tool:

**Gate 1 — Document_Appender**
```
⚠️  Approve execution of 'Document_Appender'? [Y/N]:
```
Appends the combined JSON to `Phase3_MCP_Integration/weekly_pulse_notes.md`:
```json
{
  "date": "2026-03-21",
  "weekly_pulse": { themes, top_3_themes, quotes, weekly_note, action_ideas },
  "fee_scenario": "SBI Mutual Funds — Exit Load",
  "explanation_bullets": ["..."],
  "source_links": ["..."]
}
```

**Gate 2 — Google_Doc_Appender (MCP)**
```
⚠️  Approve execution of 'Google_Doc_Appender'? [Y/N]:
```
Uses a real MCP server (`google_doc_mcp_server.py` via `FastMCP` + stdio transport) to append the same combined JSON to a Google Doc via Google Docs API.

**Gate 3 — Email_Drafter**
```
⚠️  Approve execution of 'Email_Drafter'? [Y/N]:
```
Writes `email_draft.txt` with:
- Subject: `Weekly Pulse + Fee Explainer — YYYY-MM-DD`
- Section 1 — WEEKLY PULSE: themes, 3 quotes, weekly note, action ideas
- Section 2 — FEE EXPLAINER: scenario name, bullets, source links, last checked date
- No auto-send (draft only)

---

## Deliverables

| Deliverable | Location |
|---|---|
| Working prototype | https://ind-money-weekly-review-pulse.vercel.app/dashboard.html |
| Weekly note (MD) | `Phase3_MCP_Integration/weekly_pulse_notes.md` |
| Notes/Doc snippet | `Phase3_MCP_Integration/weekly_pulse_notes.md` (appended weekly) + [Google Doc](https://docs.google.com/document/d/1erfYuwVB6nNieTNwjxO6cTX9Be2FIXg6rQiEfSov0so/edit?tab=t.0) |
| Email draft | `Phase3_MCP_Integration/email_draft.txt` |
| Reviews CSV sample | `Phase1_Data_Ingestion/sanitized_indmoney_reviews.csv` |
| Source list | See sources below |
| README | This file |

### Source List

1. https://www.sbimf.com/en-us/investor-corner — SBI MF official investor corner
2. https://www.sbimf.com/sbimf-scheme-details/sbi-large-cap-fund-(formerly-known-as-sbi-bluechip-fund)-43 — SBI Large Cap Fund scheme details
3. https://github.com/manishkumar98/IND-MONEY-RAG-CHATBOT/blob/main/docs/sources.md#source-urls-sbi-mutual-funds — Fund source URL reference
4. https://play.google.com/store/apps/details?id=com.indwealth.indmoney — INDmoney Google Play page (reviews source)
5. https://apps.apple.com/in/app/indmoney/id1481026906 — INDmoney App Store page (reviews source)
6. https://console.groq.com — Groq API (Llama 3 inference)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              GitHub Actions (Cron — Every Saturday)      │
│                    10:00 AM IST / 04:30 UTC              │
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
          │  → fee_explanation.json     │
          └─────────────┬──────────────┘
                        │ weekly_pulse_output.json
                        │ fee_explanation.json
          ┌─────────────▼──────────────┐
          │  Phase 3: MCP Integration   │
          │  Groq (llama-3.3-70b)       │
          │  3 Approval-Gated Tools:    │
          │  → Document_Appender        │
          │  → Google_Doc_Appender(MCP) │
          │  → Email_Drafter            │
          └─────────────┬──────────────┘
                        │ email_draft.txt
                        │ weekly_pulse_notes.md
          ┌─────────────▼──────────────┐
          │  Phase 5: Email Sender      │
          │  Brevo API (HTTP)           │
          │  → HTML poster email sent   │
          │  → poster.html saved        │
          └─────────────┬──────────────┘
                        │
          ┌─────────────▼──────────────┐
          │  Phase 6: Web App           │
          │  update_dashboard.py        │
          │  Injects new data into      │
          │  dashboard.html → git push  │
          │  → Vercel auto-deploys      │
          └────────────────────────────┘
```

---

## How to Re-Run

### Prerequisites

Python 3.11+. Create a `.env` file at project root:

```
GROQ_API_KEY=your_key
EMAIL_SENDER=your_gmail@gmail.com
EMAIL_PASSWORD=your_app_password
BREVO_API_KEY=your_brevo_key
GOOGLE_DOC_ID=your_google_doc_id
GOOGLE_SERVICE_ACCOUNT_JSON=base64_encoded_service_account_json
```

### Install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run individual phases

```bash
# Phase 1 — Scrape and sanitize reviews
python Phase1_Data_Ingestion/phase1_data_ingestion.py

# Phase 2 — LLM analysis + fee explainer
python Phase2_LLM_Processing/phase2_llm_processing.py

# Phase 3 — MCP tool calling with approval gates (interactive)
python Phase3_MCP_Integration/phase3_mcp_orchestration.py

# Phase 3 — Non-interactive (auto-approve all 3 gates, used by CI)
printf "Y\nY\nY\n" | python Phase3_MCP_Integration/phase3_mcp_orchestration.py

# Phase 5 — Send email
python Phase5_Email_UI/email_sender.py recipient@email.com --name "Recipient Name"

# Phase 6 — Update dashboard
python Phase6_Web_App/update_dashboard.py
```

### Run the full pipeline
```bash
# Interactive — stops at each approval gate
python Phase4_Orchestration/main_orchestrator.py

# Non-interactive — auto-approves all gates (CI mode)
printf "Y\nY\nY\n" | python Phase4_Orchestration/main_orchestrator.py
```

### Start the backend API locally
```bash
./venv/bin/uvicorn Phase6_Web_App.backend.app:app --reload --port 8000
```

---

## Where MCP Approval Happens

**File:** `Phase3_MCP_Integration/phase3_mcp_orchestration.py`
**Function:** `human_approval_gate()` at line ~70

The flow for each tool call:
```
Groq proposes tool call
        ↓
validate_tool_payload()  ← checks required fields exist
        ↓
pretty_print_tool_call() ← shows full payload to human
        ↓
input("Approve? [Y/N]")  ← HALTS HERE — waits for human
        ↓
      Y → execute_tool()
      N → skip, continue to next tool
```

In CI (GitHub Actions), this is bypassed with:
```bash
printf "Y\nY\nY\n" | python Phase3_MCP_Integration/phase3_mcp_orchestration.py
```

**MCP Architecture for Google Doc appending:**
- `google_doc_mcp_server.py` — real MCP server (`FastMCP`, stdio transport), exposes `append_to_google_doc` tool
- `mcp_tools.py` — MCP client that spawns the server as subprocess, connects via `ClientSession` + `stdio_client`
- Google Docs API is called from inside the MCP server using a service account

---

## Fee Scenario Covered

**Scenario:** Exit Load for SBI Mutual Funds on INDmoney

Exit load is the fee charged when an investor redeems (withdraws from) a mutual fund before a specified holding period.

**Funds covered:**
- SBI Large Cap Fund — 1% exit load if redeemed within 365 days
- SBI Flexicap Fund — Nil exit load
- SBI ELSS Tax Saver Fund — Nil exit load
- SBI Small Cap Fund — 1% exit load if redeemed within 18 months
- SBI Midcap Fund — Nil exit load
- SBI Focused Equity Fund — Nil exit load

Output saved to: `Phase2_LLM_Processing/fee_explanation.json`

---

## Skills Demonstrated

| Skill | Implementation |
|---|---|
| **LLM Structuring** | `response_format={"type":"json_object"}` + schema-enforced prompts + `validate_llm_json()` with retry |
| **Theme Clustering** | 2-pass processing (split → synthesize), max 5 themes, ranked `top_3_themes` |
| **Quote Extraction** | Verbatim quotes enforced in prompt (`"real quotes from the text"`), `len==3` validated |
| **Controlled Summarization** | `weekly_note` ≤250 words (programmatic check), fee explainer ≤6 bullets (post-LLM trim), `temperature=0.1` |
| **Workflow Sequencing** | Phase 1→2→3→5→6 dependency chain, each phase reads previous phase output files |
| **MCP Tool Calling** | `FastMCP` server + `stdio_client` MCP client + Groq function calling with `tool_choice="required"` |
| **Approval Gating** | `human_approval_gate()` before each of 3 tools, payload shown before any execution, individual Y/N per tool |

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Data scraping | `google-play-scraper`, `app-store-scraper` | Pull reviews from stores |
| Data processing | `pandas` | Clean, filter, deduplicate |
| LLM (extraction) | Groq API — `llama-3.1-8b-instant` | Theme extraction, summarization, fee explainer |
| LLM (orchestration) | Groq API — `llama-3.3-70b-versatile` | MCP tool calling, draft generation |
| MCP | `mcp` SDK v1.26.0 — `FastMCP`, `stdio_client` | Google Doc appender tool |
| Email delivery | Brevo API (HTTP) | Send HTML pulse emails to any address |
| Backend API | FastAPI + Uvicorn (Docker) | Send-email endpoint |
| Frontend | Vanilla HTML/CSS/JS | Subscribe page + 3-tab dashboard |
| Hosting (frontend) | Vercel | Static site, auto-deploys on push |
| Hosting (backend) | Render (Docker) | FastAPI container |
| Scheduler | GitHub Actions (cron) | Weekly pipeline trigger |

---

## Project Structure

```
ind-money-weekly-pulse-view/
│
├── Phase1_Data_Ingestion/
│   ├── phase1_data_ingestion.py      # Scrapes + sanitizes reviews
│   └── sanitized_indmoney_reviews.csv
│
├── Phase2_LLM_Processing/
│   ├── phase2_llm_processing.py      # Groq API analysis + fee explainer
│   ├── weekly_pulse_output.json      # themes, quotes, actions
│   └── fee_explanation.json          # exit load bullets, sources, last_checked
│
├── Phase3_MCP_Integration/
│   ├── phase3_mcp_orchestration.py   # Groq tool-calling + approval gates
│   ├── mcp_tools.py                  # Tool schemas + executor
│   ├── google_doc_mcp_server.py      # FastMCP server (Google Docs)
│   ├── email_draft.txt               # Output: approval-gated email draft
│   └── weekly_pulse_notes.md         # Output: appended weekly notes
│
├── Phase4_Orchestration/
│   └── main_orchestrator.py          # End-to-end pipeline runner
│
├── Phase5_Email_UI/
│   ├── email_sender.py               # Sends HTML email via Brevo API
│   └── poster.html                   # Generated email poster (local preview)
│
├── Phase6_Web_App/
│   ├── backend/app.py                # FastAPI backend (Render)
│   ├── frontend/dashboard.html       # 3-tab pulse dashboard (Vercel)
│   ├── frontend/index.html           # Subscribe page (Vercel)
│   └── update_dashboard.py           # Injects weekly data into dashboard.html
│
├── Docs/
│   ├── architecture_plan.md          # Full technical architecture
│   ├── concepts_and_application.md   # 7 assessed skills mapped to code
│   └── layman_project_overview.md    # Plain-English overview
│
├── Dockerfile                        # Docker image for Render
├── requirements.txt                  # Python dependencies
└── .github/workflows/weekly_pulse.yml  # Saturday cron scheduler
```
