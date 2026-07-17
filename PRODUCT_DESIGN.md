# Product Design: Weekly Product Pulse and Fee Explainer (M2)

## Project: INDMoney Weekly Review Pulse
**Product:** INDMoney  
**Milestone:** M2 (Milestone 2)  
**Due Date:** Mar 25, 11:59:00 PM (Asia/Calcutta)  
**Repository:** [manishkumar98/ind-money-weekly-review-pulse](https://github.com/manishkumar98/ind-money-weekly-review-pulse)

---

## 1. PRODUCT VISION

**INDMoney Weekly Review Pulse** is an AI-powered workflow that transforms customer reviews into structured, actionable product insights. The system analyzes app reviews, clusters feedback into themes, extracts real user quotes, and generates a concise weekly pulse alongside standardized fee explanations. All outputs are created with human-in-the-loop MCP approval gates to ensure compliance and accuracy.

**Who it helps:**
- 🎯 **Product teams** — Weekly insights into customer sentiment and pain points
- 🎯 **Support teams** — Standardized fee explanations for repetitive customer questions
- 🎯 **Finance advisors** — Context-rich briefings about customer concerns before consultations
- 🎯 **Leadership** — Data-driven weekly product health snapshots

---

## 2. PRIMARY USERS

| User | Goal | Pain Point | Solution |
|------|------|-----------|----------|
| **Product Manager** | Understand customer sentiment trends | Manual review analysis is slow | AI clusters themes + extracts quotes in 2 mins |
| **Support Lead** | Answer fee questions consistently | Repetitive questions take time | Pre-generated fee explainer ready to use |
| **Finance Advisor** | Prepare for investor consultations | No context about product issues | Weekly pulse includes top 3 themes + quotes |
| **Compliance Officer** | Ensure structured, audit-able outputs | Risk of inconsistent explanations | MCP-gated approval ensures compliance |

---

## 3. KEY PAIN POINTS

**For Product Teams:**
- ❌ Manual analysis of 50-100+ reviews per week is time-consuming
- ❌ Themes are subjective; different analysts find different patterns
- ❌ No standardized way to present insights to leadership
- ❌ Missing connection between customer sentiment and advisor briefings

**For Support Teams:**
- ❌ Answering the same fee questions repeatedly (exit load, withdrawal charges, etc.)
- ❌ No standardized explanations; inconsistent responses to customers
- ❌ Hard to cite official sources for fee explanations
- ❌ Time spent on explanations could go to higher-value support

**For Financial Advisors:**
- ❌ No visibility into top customer pain points before calls
- ❌ Unprepared for common objections or concerns
- ❌ Wasting consultation time explaining known issues
- ❌ Missing context from weekly product feedback trends

**For Compliance/Security:**
- ❌ Risk of PII in review quotes (customer names, emails)
- ❌ No standardized format for internal documentation
- ❌ Fee explanations might accidentally recommend products
- ❌ No audit trail of when/who approved outputs

---

## 4. CUSTOMER JOURNEY

### **Current State (Manual & Inefficient):**
```
Product Manager 
  → Reads 50-100 reviews manually 
  → Takes notes on themes 
  → Writes summary (1-2 hours)
  → Shares in email/Slack
  → Leadership unsure if insights are comprehensive

Support Team
  → Customer asks about exit load
  → Manually search for fee info
  → Craft explanation from memory
  → Inconsistent responses to similar questions

Advisor
  → Gets calendar invite for investor call
  → Has no context about their pain points
  → Unprepared, wasting consultation time
```

### **Desired State (AI-Powered & Structured):**
```
Product Manager
  → Upload reviews CSV (last 8-12 weeks)
  → AI clusters into themes, extracts quotes
  → 5-min review of AI output → Approve/Edit
  → Weekly pulse generated + MCP append to Notes/Doc
  → Email draft sent to team (approval-gated)

Support Team
  → Weekly pulse shows exit load is Theme #2
  → Pre-generated fee explainer ready
  → Copy-paste standard response with sources
  → Consistent, compliant answers

Advisor
  → Receives email: "Top themes this week: Login Issues, Exit Load, Nominee Updates"
  → Reviews quotes + action items
  → Prepared for investor concerns
  → More productive consultation
```

### **Two-Part Workflow:**

| Part | Component | Input | Output |
|------|-----------|-------|--------|
| **Part A** | Weekly Review Pulse | Reviews CSV (8-12 weeks) | 5 themes → Top 3 + 3 quotes + ≤250-word pulse + 3 actions |
| **Part B** | Fee Explainer | Fee scenario selected | ≤6 bullets + 2 official sources + last checked date |
| **MCP Layer** | Approval-Gated Actions | Pulse + Explainer | Append to Notes/Doc + Draft email (no auto-send) |

---

## 5. WHAT WE'RE SOLVING

### **Challenge A: Sentiment Analysis at Scale**
- **Problem:** Manual review analysis doesn't scale; bias and inconsistency creep in
- **Solution:** AI clusters reviews into max 5 themes; identifies top 3 with supporting quotes
- **Success Metric:** Themes match manual analysis 90%+ of the time; extraction takes <2 mins

### **Challenge B: Standardized Fee Explanations**
- **Problem:** Support team gives inconsistent explanations; no compliance trail
- **Solution:** AI generates structured, sourced fee explainer; ready to copy-paste
- **Success Metric:** 100% of explanations include 2+ official sources; 0% PII leakage

### **Challenge C: Actionable Insights for Leadership**
- **Problem:** Raw themes aren't actionable; hard to connect to product decisions
- **Solution:** AI generates 3 action ideas per week (e.g., "Fix login bug", "Improve tax doc guide")
- **Success Metric:** Leadership acts on ≥2 of 3 action ideas per week

### **Challenge D: Advisor Context & Preparedness**
- **Problem:** Advisors unprepared for calls; don't know customer sentiment
- **Solution:** Weekly pulse email brief includes themes + quotes; advisor prepares in advance
- **Success Metric:** Advisor preparation time reduced by 50%; call satisfaction +20%

### **Challenge E: Compliance & Audit Trail**
- **Problem:** No structured approval process; risk of inaccurate/sensitive outputs
- **Solution:** All MCP actions approval-gated; audit trail logs who approved what & when
- **Success Metric:** 100% of outputs approved before going live; zero compliance incidents

---

## 6. CORE FEATURES & TECHNICAL SPECS

### **Feature 1: Review Clustering & Theme Extraction (Part A)**

**Input:** Public reviews CSV (last 8-12 weeks)
- Columns: `date`, `rating`, `review_text`, `user_name`, etc.
- 50-500 reviews per week

**Process:**
```
1. Clean reviews (remove PII like names, emails)
2. Embed reviews using LLM/semantic search
3. Cluster into max 5 themes (K-means or hierarchical clustering)
4. Rank themes by frequency + sentiment impact
5. Extract top 3 themes
6. Pull 3 representative quotes per top theme
7. Generate labels (e.g., "Login Issues", "Exit Load Confusion", "Tax Doc Access")
```

**Output:**
```json
{
  "analysis_date": "2024-03-24",
  "total_reviews_analyzed": 87,
  "themes": [
    {
      "rank": 1,
      "theme_name": "Login Issues",
      "frequency": 18,
      "sentiment_score": -0.85,
      "quote_1": "Can't log in for 3 days, very frustrated",
      "quote_2": "Login fails after password reset",
      "quote_3": "OTP not working, tried 5 times"
    },
    {
      "rank": 2,
      "theme_name": "Exit Load Confusion",
      "frequency": 12,
      "sentiment_score": -0.72,
      "quote_1": "Why was I charged exit load? No one explained",
      "quote_2": "Exit load calculation is not clear",
      "quote_3": "Didn't know about exit load when buying"
    },
    {
      "rank": 3,
      "theme_name": "Nominee Updates",
      "frequency": 9,
      "sentiment_score": -0.60,
      "quote_1": "Can't update nominee information online",
      "quote_2": "Nominee change process is too complicated",
      "quote_3": "Form says nominee can't be changed, very old"
    }
  ]
}
```

### **Feature 2: Weekly Pulse Generation (Part A)**

**Requirements:**
- ≤250 words
- Natural, conversational tone
- Structured: Opening + Top 3 themes summary + Key quotes + 3 action ideas
- No PII (use `[REDACTED]` for user references)
- Last updated timestamp

**Sample Output:**
```markdown
## Weekly Product Pulse — Week of Mar 24, 2024

### Summary
This week we analyzed 87 reviews (Mar 18-24). Customer sentiment shows 3 emerging themes:
login failures, exit load confusion, and nominee update friction.

### Top Themes & Key Insights
**1. Login Issues (18 reports, -0.85 sentiment)**
Customers reporting multi-day login failures, especially post-password-reset. OTP delivery is inconsistent.
- "Can't log in for 3 days, very frustrated"
- "OTP not working, tried 5 times"

**2. Exit Load Confusion (12 reports, -0.72 sentiment)**
Customers charged exit load without clear disclosure or education. Many first-time ELSS investors.
- "Why was I charged exit load? No one explained"
- "Didn't know about exit load when buying"

**3. Nominee Updates (9 reports, -0.60 sentiment)**
Legacy form system prevents nominee changes; customers perceive this as old/broken feature.
- "Can't update nominee information online"
- "Nominee change process is too complicated"

### Action Ideas
1. **Urgent:** Debug login + OTP delivery system; add fallback SMS if email fails
2. **Medium:** Create exit load explainer + add to fund purchase flow (before checkout)
3. **Low:** Migrate nominee update form to modern UI; reduce required steps from 5 to 2

---
Last updated: 2024-03-24 | Next pulse: 2024-03-31
```

### **Feature 3: Fee Explainer Generation (Part B)**

**Pick 1 Fee Scenario:** (e.g., Exit Load, Withdrawal Charge, Brokerage Fee, Maintenance Charge, STT, etc.)

**Requirements:**
- ≤6 structured bullets
- Include 2 official source links (AMC, SEBI, AMFI, fund factsheet)
- Last checked date
- Neutral, facts-only tone
- No product recommendations
- No comparisons (e.g., "this is cheaper than X")

**Sample Output:**
```markdown
## Exit Load Explanation

**What is Exit Load?**
An exit load is a fee charged by a mutual fund when you sell/redeem your units within a 
specified period from purchase. For ELSS funds (like SBI Bluechip), the standard exit load 
is 1% if units are sold within 3 years of purchase.

**Key Points:**
- **Timing:** Exit load applies only if you redeem BEFORE the lock-in/holding period ends
- **Amount:** Typically 1% of redemption value for ELSS; 0% after 3 years
- **Who pays:** The redeeming investor (deducted from redemption proceeds)
- **Purpose:** Discourages short-term speculation; keeps long-term investors stable
- **Tax impact:** Exit load reduces net redemption amount; affects capital gains calculation
- **Waiver:** No exit load if you hold ELSS for full 3-year lock-in period

**Official Sources:**
- SBI Bluechip ELSS — Scheme Information Document (SID): [link to AMC SID]
- SEBI — Mutual Fund Basics: Exit Load: [link to SEBI page]

Last checked: 2024-03-24
```

### **Feature 4: MCP Actions (Approval-Gated)**

**Action 1: Append to Notes/Doc**
```json
{
  "date": "2024-03-24",
  "week_ending": "2024-03-24",
  "total_reviews": 87,
  "top_3_themes": [
    "Login Issues",
    "Exit Load Confusion",
    "Nominee Updates"
  ],
  "weekly_pulse": "[full pulse text]",
  "fee_scenario": "Exit Load",
  "fee_explanation_bullets": [
    "Exit load is a fee charged when you sell units within lock-in period",
    "Applies to ELSS: 1% if redeemed before 3 years",
    "No exit load after 3-year lock-in",
    "Deducted from redemption proceeds",
    "Impacts capital gains calculation",
    "Check SID for your specific fund"
  ],
  "source_links": [
    "https://www.sbimf.com/en/investor/documents/elss-sid",
    "https://www.sebi.gov.in/investor-education/mutual-funds/exit-load"
  ],
  "status": "pending_approval",
  "created_at": "2024-03-24T14:32:00Z"
}
```

**Action 2: Create Email Draft (Approval-Gated)**
```
To: team@indmoney.com, advisors@indmoney.com
Subject: Weekly Pulse + Fee Explainer — Week of Mar 24, 2024

Body:
---

Hi Team,

**Weekly Product Pulse — Mar 18-24, 2024**

We analyzed 87 reviews this week. Here are the top 3 themes:

**1. Login Issues (18 reports, -0.85 sentiment)**
Customers report 3-day login failures, especially after password reset. OTP delivery inconsistent.

Key quotes:
- "Can't log in for 3 days, very frustrated"
- "OTP not working, tried 5 times"

**2. Exit Load Confusion (12 reports, -0.72 sentiment)**
Customers charged exit load without clear disclosure. Many first-time ELSS investors.

Key quotes:
- "Why was I charged exit load? No one explained"
- "Didn't know about exit load when buying"

**3. Nominee Updates (9 reports, -0.60 sentiment)**
Legacy form prevents nominee changes. Customers perceive feature as old/broken.

Key quotes:
- "Can't update nominee information online"
- "Nominee change process is too complicated"

---

**Action Items for This Week:**
1. 🔴 URGENT: Debug login + OTP delivery; add SMS fallback
2. 🟡 MEDIUM: Create exit load explainer + add to purchase flow
3. 🔵 LOW: Modernize nominee update form; reduce steps from 5 to 2

---

**Fee Explainer This Week: Exit Load**

Exit load is a 1% fee charged when you redeem ELSS units before 3-year lock-in.

Key points:
- Applies only before lock-in period ends
- Amount: 1% of redemption value (ELSS)
- Deducted from redemption proceeds
- No exit load after 3 years
- Check fund SID for your specific fund

Sources:
- SBI Bluechip ELSS SID: [link]
- SEBI Mutual Fund Basics: [link]

Last checked: 2024-03-24

---

[APPROVE] [EDIT] [REJECT]

This email is pending approval. Do not send until approved above.
```

### **Feature 5: Refusal & Safety Flows**

**PII Detection & Redaction:**
```
Input: "My account number is 987654321. I'm [REDACTED] from Mumbai."
Process: Detect PAN, Aadhaar, account #, email, phone
Output: "Customer from [REDACTED] city reported issue with [REDACTED] account."
```

**No Recommendations:**
```
Input: "Which ELSS fund should I buy?"
Output: NOT ALLOWED. The fee explainer only explains exit load.
        For fund recommendations, contact your advisor: [link]
```

---

## 7. SOLUTION PRIORITIZATION

| Priority | Feature | Effort | Impact | Reasoning |
|----------|---------|--------|--------|-----------|
| **P0** | **Review clustering + theme extraction** | High | High | Core product; foundation of all insights |
| **P0** | **Weekly pulse generation (≤250 words)** | High | High | Main deliverable; must be high quality |
| **P0** | **Fee explainer generation (≤6 bullets)** | Medium | High | Solves support team pain point |
| **P0** | **MCP append to Notes/Doc (HITL)** | Medium | High | Ensures compliance; creates audit trail |
| **P1** | **Email draft generation (approval-gated)** | Medium | Medium | Saves team time; ensures consistency |
| **P1** | **PII detection & redaction** | Medium | Medium | Safety critical; prevents data leakage |
| **P2** | **Historical trend analysis** | Medium | Low | Nice-to-have; shows week-over-week changes |
| **P3** | **Dashboard visualization** | Low | Low | Polish later; not critical for MVP |

---

## 8. KEY CONSTRAINTS & COMPLIANCE REQUIREMENTS

### **Data Privacy Constraints:**
- ✅ **No PII in outputs** — Use `[REDACTED]` for names, emails, account numbers, PAN, Aadhaar
- ✅ **Quote anonymization** — Extract verbatim quotes but mask personally identifying info
- ✅ **Source citations** — All fee explanations cite only official sources (AMC, SEBI, AMFI)
- ✅ **Audit trail** — Log all MCP approvals with timestamp + approver name

### **Compliance Constraints:**
- ✅ **Facts-only tone** — No opinions, recommendations, or speculation
- ✅ **HITL approval gates** — All outputs must be human-approved before appending/sending
- ✅ **Last checked date** — Fee explanations must include "Last checked: {date}"
- ✅ **No comparisons** — Fee explainers don't compare to competitors
- ✅ **Max word limits** — Pulse ≤250 words; explainer ≤6 bullets

### **UX Constraints:**
- ✅ **Structured format** — Themes, quotes, actions clearly labeled
- ✅ **Actionable insights** — 3 action ideas per week (not just observations)
- ✅ **Email-friendly** — Outputs readable in email; no complex formatting
- ✅ **Quick to review** — Approval UI must show output in <30 seconds

---

## 9. SUCCESS METRICS

| Metric | Target | Test Type | Owner |
|--------|--------|-----------|-------|
| **Theme Clustering Accuracy** | 90%+ match with manual analysis | Validation Test | PM |
| **PII Leakage Rate** | 0% (zero PII in outputs) | Adversarial Test | Compliance |
| **Pulse Quality** | 100% ≤250 words + 3 actions | Content Validation | PM |
| **Fee Explanation Quality** | 100% ≤6 bullets + 2 sources | Content Validation | Support |
| **MCP Approval Turnaround** | <5 mins average | Workflow Test | Ops |
| **Quote Relevance** | 90%+ of quotes match theme | Manual Review | PM |
| **Source Validity** | 100% of URLs are live + valid | Link Checker | Compliance |
| **Tone Consistency** | 100% neutral, facts-only | Content Review | Editor |
| **Process Time** | <5 mins from CSV upload to ready-for-approval | E2E Test | Eng |

---

## 10. TECHNICAL IMPLEMENTATION ROADMAP

### **Phase 1: Data Pipeline & Theme Clustering (Week 1)**
- Set up review CSV ingestion
- Implement PII detection + redaction
- Build embedding + clustering pipeline (LLM + K-means)
- Extract top 3 themes + frequencies
- Test on sample data (100+ reviews)

### **Phase 2: Pulse & Explainer Generation (Week 1-2)**
- Build prompt for pulse generation (≤250 words, 3 actions)
- Build prompt for fee explanation (≤6 bullets, 2 sources)
- Implement quote extraction + deduplication
- Add last-checked-date tagging
- Test quality with manual review

### **Phase 3: MCP Integration (Week 2)**
- Connect to Notes/Doc API (append entry)
- Connect to Email API (draft, no auto-send)
- Implement approval UI (Streamlit/Gradio)
- Add audit logging (who approved, when, what changed)
- Test HITL workflow end-to-end

### **Phase 4: Safety & Validation (Week 2-3)**
- Implement PII detection for outputs
- Build adversarial test suite (try to leak PII, get recommendations, etc.)
- Validate all fee explanation sources
- Add tone/style validation checks
- Test error handling (malformed CSV, empty results, etc.)

### **Phase 5: Testing & Deployment (Week 3-4)**
- Golden dataset (5 real review CSVs)
- Adversarial tests (3 safety scenarios)
- E2E testing (CSV → pulse → explainer → MCP → email)
- Deployment + demo video
- Documentation & README

---

## 11. DELIVERABLES CHECKLIST

- [ ] **GitHub Repository Link** — https://github.com/manishkumar98/ind-money-weekly-review-pulse
- [ ] **README.md** — Setup, how to re-run, MCP approval workflow, fee scenario covered
- [ ] **Working Prototype** — Live notebook or deployed app link
- [ ] **Demo Video** — ≤3 mins, showing full workflow (CSV upload → pulse → approval → email)
- [ ] **Sample Weekly Pulse** — MD/PDF showing generated output
- [ ] **Sample Fee Explainer** — Text with bullets + sources
- [ ] **Notes/Doc Append Screenshot** — Shows appended JSON entry
- [ ] **Email Draft Screenshot** — Shows generated email with [APPROVE/EDIT/REJECT]
- [ ] **Sample Reviews CSV** — 10+ rows with headers (date, rating, review_text)
- [ ] **Source List (4-6 URLs)** — Fee sources (AMC SID, SEBI pages, AMFI resources)
- [ ] **Test Report** — Golden dataset results + Adversarial tests + scores
- [ ] **Script/Prompts File** — The exact prompts used for theme extraction, pulse generation, fee explainer

---

## 12. SUCCESS DEFINITION

**This workflow is successful when:**

1. ✅ Reviews CSV (50-500 reviews) is processed and clustered into max 5 themes in <2 mins
2. ✅ Top 3 themes are identified with >90% accuracy vs manual analysis
3. ✅ 3 representative quotes extracted per theme (no PII)
4. ✅ Weekly pulse generated: ≤250 words, natural tone, 3 action ideas
5. ✅ Fee explainer generated: ≤6 bullets, 2+ official sources, last-checked date included
6. ✅ Both outputs appended to Notes/Doc via MCP (approval-gated)
7. ✅ Email draft created with pulse + explainer (no auto-send)
8. ✅ 0% PII leakage in all outputs
9. ✅ 100% of fee sources are valid + live
10. ✅ Approval UI shows output in <30 seconds; turnaround <5 mins
11. ✅ Full audit trail (who approved, when, what changed)
12. ✅ Workflow runs end-to-end without manual intervention (except approval)

---

## 13. INTEGRATION WITH OTHER MILESTONES

### **M1 Integration (RAG FAQ):**
- **Future Enhancement:** If pulse identifies "Exit Load Confusion" as theme, link to M1 FAQ: "What is exit load?"
- **Example:** Email includes "See also: M1 Exit Load FAQ link"
- **Priority:** P2 (future phase)

### **M3 Integration (Voice Agent):**
- **Future Enhancement:** If pulse identifies top themes, voice agent becomes "theme-aware"
- **Example:** Voice agent greeting mentions: "I see many customers ask about {Theme1} — let me help"
- **Priority:** P2 (future phase)

### **Unified Suite (M1 + M2 + M3):**
- **Final Architecture:** Weekly pulse themes feed into voice agent context + advisor email briefings
- **Impact:** Advisor receives pulse → mentions themes in voice greeting → investor feels heard

---

## 14. ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│     WEEKLY PRODUCT PULSE & FEE EXPLAINER (M2)               │
│              (AI-Powered Workflow)                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Data Ingestion Layer                                │  │
│  │  • Upload reviews CSV (8-12 weeks, 50-500 reviews)   │  │
│  │  • Validate format + structure                       │  │
│  │  • PII detection + redaction                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Theme Clustering Layer (LLM + Embeddings)           │  │
│  │  • Embed reviews using semantic search               │  │
│  │  • Cluster into max 5 themes                         │  │
│  │  • Rank by frequency + sentiment                     │  │
│  │  • Extract top 3 themes with supporting quotes       │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Generation Layer (LLM)                              │  │
│  │                                                      │  │
│  │  Part A: Weekly Pulse Generator                      │  │
│  │  • Input: Top 3 themes + quotes                      │  │
│  │  • Output: ≤250-word pulse + 3 action ideas          │  │
│  │  • Constraints: Facts-only, no PII, structured       │  │
│  │                                                      │  │
│  │  Part B: Fee Explainer Generator                     │  │
│  │  • Input: Selected fee scenario                      │  │
│  │  • Output: ≤6 bullets + 2 official sources           │  │
│  │  • Constraints: Facts-only, sourced, last-checked    │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Quality Validation Layer                            │  │
│  │  • Check pulse ≤250 words ✓                          │  │
│  │  • Check explainer ≤6 bullets ✓                      │  │
│  │  • Verify source links are live ✓                    │  │
│  │  • Scan for PII + recommendations ✓                  │  │
│  │  • Validate tone is neutral ✓                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Approval UI Layer (HITL)                            │  │
│  │  • Show pulse + explainer for review                 │  │
│  │  • Allow edit/reject/approve                         │  │
│  │  • Capture approver name + timestamp                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MCP Action Layer (Human-in-Loop)                    │  │
│  │  • Append to Notes/Doc (JSON entry)                  │  │
│  │  • Draft email to team/advisors                      │  │
│  │  • No auto-send; awaiting further approval           │  │
│  │  • Log all actions + timestamps                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Safety Layer (Always Active):
  • PII detection + redaction (all outputs)
  • Tone validation (no recommendations, no speculation)
  • Source validation (all links verified)
  • Audit logging (all approvals + changes)
  • Rate limiting (max 1 pulse per week to prevent abuse)
```

---

## 15. RESOURCE REQUIREMENTS

| Resource | Type | Provider | Notes |
|----------|------|----------|-------|
| **LLM** | Core AI | OpenAI/Claude/Gemini | For clustering, pulse generation, fee explainer |
| **Embeddings** | Semantic Search | OpenAI/Cohere/Hugging Face | For review clustering |
| **Notes/Doc API** | MCP Tool | Google Docs/Notion/Confluence | Append structured entry |
| **Email API** | MCP Tool | Gmail/SendGrid/AWS SES | Draft emails (no auto-send) |
| **PII Detector** | Utility | Custom/Presidio/spaCy | Detect + redact PII |
| **Link Validator** | Utility | Custom/requests library | Check source URLs are live |
| **CSV Parser** | Utility | pandas/polars | Read reviews CSV |
| **UI Framework** | Frontend | Streamlit/Gradio | Approval interface |
| **Logging** | Infrastructure | Python logging/ELK | Audit trail |

---

## 16. SAMPLE DELIVERABLES STRUCTURE

### **README.md Contents:**
```
# INDMoney Weekly Review Pulse

## Quick Start
1. Upload reviews CSV (columns: date, rating, review_text)
2. Select fee scenario (exit load, withdrawal charge, etc.)
3. Run: `python app.py`
4. Review pulse + explainer in UI
5. Approve (or edit) to append to Notes/Doc
6. Email draft auto-generated

## Files
- `app.py` — Main Streamlit app
- `processors/clustering.py` — Theme extraction
- `processors/pulse_generator.py` — Weekly pulse prompt
- `processors/fee_explainer.py` — Fee explainer prompt
- `config/prompts.yaml` — LLM prompts
- `config/sources.json` — Official fee sources (verified URLs)

## How to Re-Run
```bash
pip install -r requirements.txt
streamlit run app.py
# Upload CSV → Select fee scenario → Approve → Done
```

## MCP Approval Workflow
1. Pulse + Explainer generated
2. HITL UI shows output + [APPROVE] [EDIT] [REJECT] buttons
3. On APPROVE: Append to Notes/Doc + generate email draft
4. Email is NOT sent automatically (awaits further approval)

## Fee Scenarios Covered
- Exit Load (ELSS)
- Withdrawal Charges
- Brokerage Fees
- Expense Ratio
- Maintenance Charges

## Sources
All fee explanations sourced from:
- SBI Mutual Fund SIDs: https://www.sbimf.com/...
- SEBI Mutual Fund Guide: https://www.sebi.gov.in/...
- AMFI Standards: https://www.amfiindia.com/...

## Sample Review CSV
See `data/sample_reviews.csv` (10 rows with headers)
```

---

## 17. SUCCESS CRITERIA SUMMARY

| Criterion | Status | Evidence |
|-----------|--------|----------|
| ✅ Clustering works on 50-500 reviews | TODO | Demo video + live results |
| ✅ Top 3 themes identified | TODO | Sample pulse output |
| ✅ 3 quotes extracted per theme | TODO | Sample pulse output |
| ✅ Pulse ≤250 words | TODO | Content measurement |
| ✅ 3 action ideas generated | TODO | Sample pulse output |
| ✅ Fee explainer ≤6 bullets | TODO | Content measurement |
| ✅ 2 official sources cited | TODO | Source validation |
| ✅ No PII in outputs | TODO | Adversarial test results |
| ✅ Append to Notes/Doc works | TODO | Screenshot + audit log |
| ✅ Email draft generation works | TODO | Screenshot + audit log |
| ✅ Approval UI functional | TODO | Demo video |
| ✅ E2E workflow <5 mins | TODO | Process timing test |

---

## CONCLUSION

The **Weekly Product Pulse and Fee Explainer (M2)** transforms customer feedback into structured, actionable insights. By combining AI-powered clustering, prompt engineering, and human-in-the-loop approvals, it reduces analysis time from hours to minutes while maintaining 100% compliance and data privacy.

**Impact:**
- Product teams get weekly sentiment snapshots in 5 minutes (vs 2 hours manual)
- Support teams answer fee questions consistently with sourced explanations
- Financial advisors prepare for calls with real customer context
- Leadership makes data-driven product decisions

**This is the intelligence layer that powers the entire operations suite.**

