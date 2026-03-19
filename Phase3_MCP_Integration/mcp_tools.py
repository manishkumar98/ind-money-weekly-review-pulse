"""
mcp_tools.py
Phase 3 - MCP Tool Definitions

Defines the two MCP tools:
  1. Document_Appender  - Appends the weekly pulse to a local Markdown file.
  2. Email_Drafter      - Writes a formatted team email draft to a local .txt file.

These are the actual executors that run ONLY after the human approves them at the gate.
"""

import os
import json
from datetime import datetime


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
        "name": "Email_Drafter",
        "description": (
            "Drafts a team-wide distribution email summarizing the weekly INDmoney "
            "product pulse, ready to be reviewed and sent."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "Email subject line."
                },
                "recipient": {
                    "type": "string",
                    "description": "Target recipient or team name (e.g. 'Product Team')."
                },
                "body": {
                    "type": "string",
                    "description": "Full email body in plain text."
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
# Tool 2: Email_Drafter
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
