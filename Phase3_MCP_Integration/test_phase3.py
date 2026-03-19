"""
test_phase3.py
Unit tests for Phase 3 MCP tool logic — no live API calls needed.
"""

import os
import json
import pytest
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mcp_tools import execute_document_appender, execute_email_drafter, execute_tool, TOOL_SCHEMAS
from phase3_mcp_orchestration import validate_tool_payload


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def sample_pulse():
    return {
        "weekly_note": "Users have mixed feedback on the app.",
        "themes": ["UI", "Trading", "Issues", "Fees", "Support"],
        "top_3_themes": ["UI", "Trading", "Issues"],
        "quotes": ["Great app!", "Needs improvement.", "Love the features."],
        "action_ideas": ["Fix bugs", "Improve UI", "Add features"]
    }


@pytest.fixture
def sample_email_args():
    return {
        "subject": "Weekly INDmoney Product Pulse",
        "recipient": "Product Team",
        "body": "Please find this week's product pulse below."
    }


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


# ──────────────────────────────────────────────
# Tool Schema Tests
# ──────────────────────────────────────────────

def test_tool_schemas_exist():
    assert len(TOOL_SCHEMAS) == 2
    names = [s["name"] for s in TOOL_SCHEMAS]
    assert "Document_Appender" in names
    assert "Email_Drafter" in names


def test_tool_schemas_have_required_fields():
    for schema in TOOL_SCHEMAS:
        assert "name" in schema
        assert "description" in schema
        assert "parameters" in schema
        assert "required" in schema["parameters"]


# ──────────────────────────────────────────────
# Document_Appender Tests
# ──────────────────────────────────────────────

def test_document_appender_creates_file(sample_pulse, tmp_dir):
    path = execute_document_appender(sample_pulse, tmp_dir)
    assert os.path.exists(path)
    assert path.endswith("weekly_pulse_notes.md")


def test_document_appender_content(sample_pulse, tmp_dir):
    path = execute_document_appender(sample_pulse, tmp_dir)
    content = open(path).read()
    assert "Users have mixed feedback" in content
    assert "UI" in content
    assert "Great app!" in content
    assert "Fix bugs" in content


def test_document_appender_appends_on_multiple_calls(sample_pulse, tmp_dir):
    execute_document_appender(sample_pulse, tmp_dir)
    execute_document_appender(sample_pulse, tmp_dir)
    path = os.path.join(tmp_dir, "weekly_pulse_notes.md")
    content = open(path).read()
    # The weekly note should appear twice (appended twice)
    assert content.count("Users have mixed feedback") == 2


# ──────────────────────────────────────────────
# Email_Drafter Tests
# ──────────────────────────────────────────────

def test_email_drafter_creates_file(sample_email_args, tmp_dir):
    path = execute_email_drafter(sample_email_args, tmp_dir)
    assert os.path.exists(path)
    assert path.endswith("email_draft.txt")


def test_email_drafter_content(sample_email_args, tmp_dir):
    path = execute_email_drafter(sample_email_args, tmp_dir)
    content = open(path).read()
    assert "Weekly INDmoney Product Pulse" in content
    assert "Product Team" in content
    assert "Please find this week's" in content
    assert "DRAFT" in content


# ──────────────────────────────────────────────
# execute_tool Dispatcher Tests
# ──────────────────────────────────────────────

def test_execute_tool_document_appender(sample_pulse, tmp_dir):
    result = execute_tool("Document_Appender", sample_pulse, tmp_dir)
    assert result["success"] is True
    assert result["tool"] == "Document_Appender"
    assert result["output_path"] is not None


def test_execute_tool_email_drafter(sample_email_args, tmp_dir):
    result = execute_tool("Email_Drafter", sample_email_args, tmp_dir)
    assert result["success"] is True
    assert result["tool"] == "Email_Drafter"
    assert result["output_path"] is not None


def test_execute_tool_unknown():
    result = execute_tool("Unknown_Tool", {}, "/tmp")
    assert result["success"] is False
    assert "Unknown tool" in result["message"]


# ──────────────────────────────────────────────
# Payload Validation Tests
# ──────────────────────────────────────────────

def test_validate_tool_payload_document_appender_valid(sample_pulse):
    assert validate_tool_payload("Document_Appender", sample_pulse) is True


def test_validate_tool_payload_document_appender_missing_field():
    incomplete = {"weekly_note": "Some note"}  # missing themes, quotes, etc.
    assert validate_tool_payload("Document_Appender", incomplete) is False


def test_validate_tool_payload_email_drafter_valid(sample_email_args):
    assert validate_tool_payload("Email_Drafter", sample_email_args) is True


def test_validate_tool_payload_email_drafter_missing_body():
    incomplete = {"subject": "Test", "recipient": "Team"}  # missing body
    assert validate_tool_payload("Email_Drafter", incomplete) is False


def test_validate_tool_payload_unknown_tool():
    assert validate_tool_payload("Ghost_Tool", {}) is False
