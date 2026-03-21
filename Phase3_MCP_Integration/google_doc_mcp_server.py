#!/usr/bin/env python3
"""
google_doc_mcp_server.py
MCP Server — Google Docs Appender

A proper MCP server (Anthropic Model Context Protocol) built with FastMCP.
Exposes one tool: append_to_google_doc

Protocol: JSON-RPC over stdio (MCP standard)
Transport: stdio — runs as a subprocess, communicates via stdin/stdout

Started automatically by the MCP client in mcp_tools.py.
"""

import base64
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(Path(__file__).parent.parent / ".env")

mcp = FastMCP("google-docs-appender")


@mcp.tool()
def append_to_google_doc(
    date: str,
    weekly_pulse: dict,
    fee_scenario: str,
    explanation_bullets: list,
    source_links: list
) -> str:
    """
    Appends a structured weekly pulse + fee explainer entry to a Google Doc.

    Args:
        date: ISO date string (YYYY-MM-DD) for this pulse run.
        weekly_pulse: Full weekly_pulse_output JSON object.
        fee_scenario: Fee scenario name (e.g. 'SBI Mutual Funds — Exit Load').
        explanation_bullets: List of ≤6 factual exit load bullet strings.
        source_links: Exactly 2 official source URLs.

    Returns:
        Status message string.
    """
    try:
        from googleapiclient.discovery import build
        from google.oauth2 import service_account
    except ImportError:
        return "❌ google-api-python-client not installed. Run: pip install google-api-python-client google-auth"

    doc_id = os.getenv("GOOGLE_DOC_ID")
    sa_raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    if not doc_id or not sa_raw or "your-google-doc-id" in doc_id:
        return "❌ GOOGLE_DOC_ID or GOOGLE_SERVICE_ACCOUNT_JSON not configured. Update .env with real values."

    # Accept both base64-encoded and raw JSON string
    try:
        sa_info = json.loads(base64.b64decode(sa_raw).decode("utf-8"))
    except Exception:
        try:
            sa_info = json.loads(sa_raw)
        except Exception as e:
            return f"❌ Failed to parse service account JSON: {e}"

    try:
        creds = service_account.Credentials.from_service_account_info(
            sa_info,
            scopes=["https://www.googleapis.com/auth/documents"]
        )
        service = build("docs", "v1", credentials=creds, cache_discovery=False)

        top_themes = ", ".join(weekly_pulse.get("top_3_themes", []))
        weekly_note = weekly_pulse.get("weekly_note", "")
        bullets_text = "\n".join(f"  • {b}" for b in explanation_bullets)
        links_text = "\n".join(f"  - {lnk}" for lnk in source_links)

        text_block = (
            f"\n{'─' * 60}\n"
            f"Date: {date}\n"
            f"Top Themes: {top_themes}\n"
            f"Weekly Note: {weekly_note}\n\n"
            f"Fee Scenario: {fee_scenario}\n"
            f"Exit Load Bullets:\n{bullets_text}\n\n"
            f"Source Links:\n{links_text}\n"
            f"{'─' * 60}\n"
        )

        doc = service.documents().get(documentId=doc_id).execute()
        end_index = doc["body"]["content"][-1]["endIndex"] - 1

        service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": [{"insertText": {"location": {"index": end_index}, "text": text_block}}]}
        ).execute()

        return f"✅ Appended to Google Doc: {doc_id}"

    except Exception as e:
        return f"❌ Google Docs API error: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
