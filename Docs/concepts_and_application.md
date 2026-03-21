# Concepts & Application — INDmoney Weekly Pulse System

This document maps each assessed skill to exactly where and how it is applied in the codebase.

---

## 1. LLM Structuring

**What it means:**
Constraining the LLM to output a strict, machine-parseable JSON schema instead of free-form text. This makes LLM output reliable enough to use programmatically.

**How it is applied:**
- **File:** `Phase2_LLM_Processing/phase2_llm_processing.py` — `process_review_chunk_with_llm()`
- Groq API is called with `response_format={"type": "json_object"}` — forces JSON-only output.
- The prompt explicitly defines every field, its type, and constraints:
  ```
  Output a strict JSON object containing:
  - 'themes' (list of strings, max 5)
  - 'top_3_themes' (list of strings, exactly 3)
  - 'quotes' (list of strings, exactly 3)
  - 'weekly_note' (string, strict max 250 words)
  - 'action_ideas' (list of strings, exactly 3)
  ```
- `temperature=0.2` reduces randomness to enforce schema adherence.
- Output is immediately parsed with `json.loads()` and validated — any deviation triggers a retry.

---

## 2. Theme Clustering

**What it means:**
Grouping large volumes of unstructured user feedback into a small set of meaningful, labelled themes. Reduces noise and surfaces patterns across hundreds of reviews.

**How it is applied:**
- **File:** `Phase2_LLM_Processing/phase2_llm_processing.py` — `process_review_chunk_with_llm()` + `synthesize_chunks()`
- Groq/Llama 3 processes up to 3,000 sanitized reviews and extracts up to 5 themes per chunk.
- Reviews are split into 2 halves; each half produces its own theme list.
- `synthesize_chunks()` merges both lists into a deduplicated master set of exactly 5 themes and a ranked `top_3_themes`.
- Post-processing guard: if LLM returns > 5 themes, the list is trimmed to 5.
- **Output:** `Phase2_LLM_Processing/weekly_pulse_output.json` → `themes`, `top_3_themes`

---

## 3. Quote Extraction

**What it means:**
Pulling verbatim, high-signal user quotes directly from raw review text — not paraphrased summaries. Real quotes provide evidence and credibility.

**How it is applied:**
- **File:** `Phase2_LLM_Processing/phase2_llm_processing.py` — `process_review_chunk_with_llm()`
- Prompt explicitly instructs: `'quotes' (list of strings, exactly 3, real quotes from the text)` — emphasises authenticity.
- `validate_llm_json()` enforces `len(quotes) == 3` — retries if violated.
- Quotes flow through to:
  - `Phase3_MCP_Integration/weekly_pulse_notes.md` (Markdown report)
  - `Phase3_MCP_Integration/email_draft.txt` (plain-text email)
  - `Phase5_Email_UI/email_sender.py` → rendered as styled quote cards in the HTML email with avatar icons
  - `Phase6_Web_App/frontend/dashboard.html` → displayed in the Pulse Poster tab

---

## 4. Controlled Summarization

**What it means:**
Generating a concise, bounded narrative summary from a large corpus. "Controlled" means enforcing hard limits on length and tone to prevent rambling or hallucination.

**How it is applied:**
- **File:** `Phase2_LLM_Processing/phase2_llm_processing.py` — `process_review_chunk_with_llm()` + `validate_llm_json()`
- `weekly_note` is constrained to **strict max 250 words** in the prompt.
- `validate_llm_json()` calls `count_words(weekly_note)` and raises `LLMValidationException` if exceeded — triggering an automatic retry.
- `synthesize_chunks()` uses `temperature=0.1` (lower than the extraction pass) to keep the synthesized summary tight.
- The exit load explainer (`generate_exit_load_explainer()`) is a second controlled summarization: exactly ≤6 factual bullet points, neutral tone enforced in system prompt, no recommendations.

---

## 5. Workflow Sequencing

**What it means:**
Chaining multiple dependent steps in a fixed order where each step's output feeds the next. Ensures repeatability and correct data flow across phases.

**How it is applied:**
- **File:** `Phase4_Orchestration/main_orchestrator.py` — ties Phases 1 → 2 → 3 in sequence.
- **GitHub Actions:** `.github/workflows/weekly_pulse.yml` runs the full pipeline every Saturday 04:30 UTC:
  ```
  Phase 1 (scrape + sanitize)
    → Phase 2 (LLM extraction + fee explainer)
      → Phase 3 (MCP tool calls: notes + Google Doc + email draft)
        → Phase 5 (send HTML email via Brevo)
          → Phase 6 (update dashboard.html + git push → Vercel auto-deploy)
  ```
- Each phase reads from the previous phase's output files:
  - Phase 2 reads `sanitized_indmoney_reviews.csv`
  - Phase 3 reads `weekly_pulse_output.json` + `fee_explanation.json`
  - Phase 5 reads `email_draft.txt` + `weekly_pulse_output.json` + `fee_explanation.json`
  - Phase 6 reads all three and bakes them into `dashboard.html`

---

## 6. MCP Tool Calling

**What it means:**
Model Context Protocol (MCP) is Anthropic's open standard for connecting LLMs to external tools via a client/server architecture. The LLM decides *what* to call and *with what arguments*; the MCP layer handles *how* it executes.

**How it is applied:**
- **True MCP implementation** — not a direct API call.
- **MCP Server:** `Phase3_MCP_Integration/google_doc_mcp_server.py`
  - Built with `FastMCP` from the official `mcp` SDK (v1.26.0)
  - Exposes one tool: `append_to_google_doc`
  - Runs over **stdio transport** (JSON-RPC over stdin/stdout)
- **MCP Client:** `Phase3_MCP_Integration/mcp_tools.py` → `execute_google_doc_appender()`
  - Spawns `google_doc_mcp_server.py` as a **subprocess**
  - Connects via `ClientSession` + `stdio_client` from the MCP SDK
  - Calls the tool using `session.call_tool("append_to_google_doc", args)`
- **Groq as orchestrator:** `Phase3_MCP_Integration/phase3_mcp_orchestration.py`
  - Groq (`llama-3.3-70b-versatile`) receives tool schemas for all 3 tools and returns `function_call` proposals
  - `tool_choice="required"` forces Groq to always call tools (not generate free text)
  - The 3 tools: `Document_Appender` (local markdown), `Google_Doc_Appender` (MCP → Google Docs API), `Email_Drafter` (local txt)

---

## 7. Approval Gating

**What it means:**
Inserting a mandatory human checkpoint between the LLM proposing an action and that action being executed. Prevents autonomous, unreviewed side effects.

**How it is applied:**
- **File:** `Phase3_MCP_Integration/phase3_mcp_orchestration.py` — `human_approval_gate()`
- Before each of the 3 tool calls, the system:
  1. **Validates** the payload against the tool's JSON schema (`validate_tool_payload()`)
  2. **Pretty-prints** the full proposed payload to the terminal
  3. **Halts** and waits for explicit `Y` or `N` input:
     ```
     ⚠️  Approve execution of 'Document_Appender'? [Y/N]:
     ```
  4. Only executes if `Y` — `N` aborts that specific tool without affecting the others.
- **CI/automated mode:** `printf "Y\nY\nY\n" | python ...` pre-approves all three gates non-interactively in GitHub Actions.
- This pattern ensures a human always reviews LLM-proposed writes to external systems (Google Docs, local files, email drafts) before they happen.

---

## Summary Table

| Skill | File | Key Lines |
|---|---|---|
| LLM Structuring | `phase2_llm_processing.py` | `response_format={"type":"json_object"}`, `validate_llm_json()` |
| Theme Clustering | `phase2_llm_processing.py` | `synthesize_chunks()`, `top_3_themes` output |
| Quote Extraction | `phase2_llm_processing.py` | `quotes` field, `len(quotes) != 3` validation |
| Controlled Summarization | `phase2_llm_processing.py` | `weekly_note` 250-word cap, `generate_exit_load_explainer()` |
| Workflow Sequencing | `main_orchestrator.py`, `weekly_pulse.yml` | Phase 1→2→3→5→6 chain |
| MCP Tool Calling | `google_doc_mcp_server.py`, `mcp_tools.py`, `phase3_mcp_orchestration.py` | `FastMCP`, `stdio_client`, `ClientSession`, `tool_choice="required"` |
| Approval Gating | `phase3_mcp_orchestration.py` | `human_approval_gate()`, `validate_tool_payload()`, `printf "Y\nY\nY\n"` in CI |
