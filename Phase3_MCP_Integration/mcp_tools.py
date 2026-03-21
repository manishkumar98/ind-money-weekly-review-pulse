"""
mcp_tools.py
Phase 3 - MCP Tool Definitions

Defines three tools. Two run locally; one uses a real MCP server:
  1. Document_Appender    - Appends the weekly pulse to a local Markdown file.
  2. Google_Doc_Appender  - Connects to google_doc_mcp_server.py via MCP stdio
                            transport and calls the 'append_to_google_doc' tool.
                            This is true MCP: JSON-RPC over stdio, server/client split.
  3. Email_Drafter        - Writes a formatted team email draft to a local .txt file.

Tools 1 and 3 execute locally after human approval.
Tool 2 spawns the MCP server as a subprocess and communicates via the MCP protocol.
"""

import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path


# ──────────────────────────────────────────────
# Tool Schemas (used by Gemini for function-calling)
# ──────────────────────────────────────────────

TOOL_SCHEMAS = [
    {
        "name": "Document_Appender",
        "description": (
            "Appends the weekly INDmoney product pulse (themes, quotes, weekly note, "
            "and action ideas) to a Markdown documentation file."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "weekly_note": {
                    "type": "string",
                    "description": "The PM-style weekly summary paragraph (max 250 words)."
                },
                "themes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of up to 5 key themes extracted from reviews."
                },
                "top_3_themes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The 3 most prominent themes."
                },
                "quotes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Exactly 3 real user quotes from the reviews."
                },
                "action_ideas": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Exactly 3 actionable product improvements."
                }
            },
            "required": ["weekly_note", "themes", "top_3_themes", "quotes", "action_ideas"]
        }
    },
    {
        "name": "Google_Doc_Appender",
        "description": (
            "Appends the combined weekly pulse and exit load fee explainer as a "
            "structured JSON block to a Google Doc. Called after both Document_Appender "
            "and Email_Drafter have executed."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "ISO date string for this pulse run (YYYY-MM-DD)."
                },
                "weekly_pulse": {
                    "type": "object",
                    "description": "The full weekly_pulse_output JSON object."
                },
                "fee_scenario": {
                    "type": "string",
                    "description": "Name of the fee scenario (e.g. 'SBI Mutual Funds — Exit Load')."
                },
                "explanation_bullets": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of ≤6 factual exit load bullet strings."
                },
                "source_links": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Exactly 2 official source URLs."
                }
            },
            "required": ["date", "weekly_pulse", "fee_scenario", "explanation_bullets", "source_links"]
        }
    },
    {
        "name": "Email_Drafter",
        "description": (
            "Drafts a team-wide distribution email summarizing the weekly INDmoney "
            "product pulse AND the fee explainer. Subject must follow the format: "
            "'Weekly Pulse + Fee Explainer — YYYY-MM-DD'. Body must include both "
            "the weekly pulse summary and the fee explanation bullets. No auto-send."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "Email subject. Format: 'Weekly Pulse + Fee Explainer — YYYY-MM-DD'."
                },
                "recipient": {
                    "type": "string",
                    "description": "Target recipient or team name (e.g. 'Product Team')."
                },
                "body": {
                    "type": "string",
                    "description": (
                        "Full email body in plain text. Must contain two sections: "
                        "1) Weekly Pulse — themes, quotes, weekly note, action ideas. "
                        "2) Fee Explainer — fee scenario name, explanation bullets, source links, last checked date."
                    )
                }
            },
            "required": ["subject", "recipient", "body"]
        }
    }
]


# ──────────────────────────────────────────────
# Tool 1: Document_Appender
# ──────────────────────────────────────────────

def execute_document_appender(args: dict, output_dir: str) -> str:
    """
    Appends the weekly pulse to a Markdown file.
    Returns the filepath of the written file.
    """
    weekly_note   = args.get("weekly_note", "")
    themes        = args.get("themes", [])
    top_3_themes  = args.get("top_3_themes", [])
    quotes        = args.get("quotes", [])
    action_ideas  = args.get("action_ideas", [])

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    week_label = datetime.now().strftime("Week of %B %d, %Y")

    newline = "\n"
    themes_lines      = newline.join(f"- {t}" for t in themes)
    top3_lines        = newline.join(f"{i+1}. {t}" for i, t in enumerate(top_3_themes))
    quotes_lines      = newline.join(f'> "{q}"' for q in quotes)
    action_lines      = newline.join(f"- [ ] {a}" for a in action_ideas)

    md_content = f"""
---

## 📅 {week_label}
*Appended at {timestamp}*

### Weekly Note
{weekly_note}

### Themes Identified
{themes_lines}

### Top 3 Themes
{top3_lines}

### User Quotes
{quotes_lines}

### Action Ideas
{action_lines}

"""

    output_path = os.path.join(output_dir, "weekly_pulse_notes.md")
    # Append to existing file (or create if first run)
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(md_content)

    return output_path


# ──────────────────────────────────────────────
# Tool 2: Google_Doc_Appender
# ──────────────────────────────────────────────

def execute_google_doc_appender(args: dict, _output_dir: str) -> str:
    """
    Uses a real MCP client to call the Google Docs append tool.

    Flow:
      1. Spawns google_doc_mcp_server.py as a subprocess (stdio transport).
      2. Connects via the MCP protocol (JSON-RPC over stdin/stdout).
      3. Calls the 'append_to_google_doc' MCP tool with the approved payload.
      4. Returns the text result from the server.

    This is true MCP — server/client split, stdio transport, JSON-RPC protocol.
    """
    server_script = str(Path(__file__).parent / "google_doc_mcp_server.py")
    python_exec = sys.executable

    async def _run_mcp_client():
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
        except ImportError:
            return "❌ mcp package not installed. Run: pip install mcp"

        server_params = StdioServerParameters(
            command=python_exec,
            args=[server_script]
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("append_to_google_doc", args)
                if result.content:
                    return result.content[0].text
                return "✅ MCP tool executed (no content returned)"

    try:
        return asyncio.run(_run_mcp_client())
    except Exception as e:
        return f"❌ MCP client error: {e}"


# ──────────────────────────────────────────────
# Tool 3: Email_Drafter
# ──────────────────────────────────────────────

def execute_email_drafter(args: dict, output_dir: str) -> str:
    """
    Writes a formatted email draft to a .txt file.
    Returns the filepath of the written file.
    """
    subject   = args.get("subject", "Weekly Product Pulse")
    recipient = args.get("recipient", "Product Team")
    body      = args.get("body", "")

    timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M")
    draft_text = f"""
============================================================
  EMAIL DRAFT — {timestamp}
============================================================
To      : {recipient}
Subject : {subject}
------------------------------------------------------------

{body}

------------------------------------------------------------
[DRAFT — Pending human review before sending]
============================================================
"""

    output_path = os.path.join(output_dir, "email_draft.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(draft_text)

    return output_path


# ──────────────────────────────────────────────
# Dispatcher
# ──────────────────────────────────────────────

def execute_tool(tool_name: str, args: dict, output_dir: str) -> dict:
    """
    Routes an approved tool call to the correct executor.
    Returns a result dict with 'success', 'tool', 'output_path', and 'message'.
    """
    if tool_name == "Document_Appender":
        path = execute_document_appender(args, output_dir)
        return {
            "success": True,
            "tool": tool_name,
            "output_path": path,
            "message": f"✅ Weekly pulse appended to: {path}"
        }
    elif tool_name == "Google_Doc_Appender":
        message = execute_google_doc_appender(args, output_dir)
        success = message.startswith("✅")
        return {
            "success": success,
            "tool": tool_name,
            "output_path": None,
            "message": message
        }
    elif tool_name == "Email_Drafter":
        path = execute_email_drafter(args, output_dir)
        return {
            "success": True,
            "tool": tool_name,
            "output_path": path,
            "message": f"✅ Email draft saved to: {path}"
        }
    else:
        return {
            "success": False,
            "tool": tool_name,
            "output_path": None,
            "message": f"❌ Unknown tool: {tool_name}"
        }
