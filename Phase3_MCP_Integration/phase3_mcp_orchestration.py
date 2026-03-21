"""
phase3_mcp_orchestration.py
Phase 3 - MCP Tool Integration & Human Approval Gates

Flow:
  1. Load weekly_pulse_output.json from Phase 2.
  2. Send it to Groq (llama-3.3-70b-versatile) with Document_Appender,
     Google_Doc_Appender, and Email_Drafter declared as callable tools.
  3. Groq returns function_call requests with ready-made payloads.
  4. For EACH proposed tool call:
       a. Pretty-print the exact payload to the terminal.
       b. Prompt the human for Y/N approval.
       c. If Y  → execute the MCP tool.
          If N  → abort that specific action.
  5. Report results.
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Ensure we can import mcp_tools from the same package
sys.path.insert(0, str(Path(__file__).parent))
from mcp_tools import TOOL_SCHEMAS, execute_tool

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OUTPUT_DIR = str(Path(__file__).parent)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def load_json_file(json_path: str) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_groq_tools() -> list[dict]:
    """Convert our TOOL_SCHEMAS list into Groq Tool objects."""
    tools = []
    for schema in TOOL_SCHEMAS:
        tools.append({
            "type": "function",
            "function": {
                "name": schema["name"],
                "description": schema["description"],
                "parameters": schema["parameters"]
            }
        })
    return tools


def pretty_print_tool_call(tool_name: str, args: dict):
    """Print the proposed tool call in a readable format for human review."""
    separator = "=" * 60
    print(f"\n{separator}")
    print(f"  🤖 GROQ PROPOSES TOOL CALL: {tool_name}")
    print(separator)
    print(json.dumps(args, indent=2))
    print(separator)


def human_approval_gate(tool_name: str, args: dict) -> bool:
    """
    Halts execution. Presents the tool payload to the human.
    Returns True if approved, False if denied.
    """
    pretty_print_tool_call(tool_name, args)

    while True:
        response = input(f"\n  ⚠️  Approve execution of '{tool_name}'? [Y/N]: ").strip().upper()
        if response == "Y":
            print(f"  ✅ Approved. Executing '{tool_name}'...")
            return True
        elif response == "N":
            print(f"  ❌ Denied. Aborting '{tool_name}'.")
            return False
        else:
            print("  Please enter Y or N.")


# ──────────────────────────────────────────────
# Validation
# ──────────────────────────────────────────────

def validate_tool_payload(tool_name: str, args: dict) -> bool:
    """Validate that the Groq payload matches the expected MCP schema."""
    schema = next((s for s in TOOL_SCHEMAS if s["name"] == tool_name), None)
    if schema is None:
        print(f"  ⚠️  Validation failed: Unknown tool '{tool_name}'.")
        return False

    required_fields = schema["parameters"].get("required", [])
    for field in required_fields:
        if field not in args:
            print(f"  ⚠️  Validation failed: Missing required field '{field}' in {tool_name} payload.")
            return False
    return True


# ──────────────────────────────────────────────
# Core orchestration
# ──────────────────────────────────────────────

def run_groq_orchestration(pulse_data: dict, fee_data: dict) -> list[dict]:
    """
    Sends pulse + fee explainer data to Groq and collects its tool-call proposals.
    Returns a list of dicts: [{tool_name, args}, ...]
    Expects Groq to call all three tools: Document_Appender, Email_Drafter, Google_Doc_Appender.
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found. Please set it in your .env file.")

    client = Groq(api_key=GROQ_API_KEY)

    today = datetime.now().strftime("%Y-%m-%d")

    system_instruction = (
        "You are an orchestration AI for the INDmoney product team. "
        "You have access to three tools: 'Document_Appender', 'Google_Doc_Appender', and 'Email_Drafter'. "
        "Use the provided Weekly Pulse JSON and Exit Load Fee Explainer JSON to call ALL THREE tools.\n\n"
        "STRICT RULES:\n"
        "1. Document_Appender: use weekly pulse fields only.\n"
        "2. Google_Doc_Appender: combine both datasets — include date, full weekly_pulse object, "
        "fee_scenario name, explanation_bullets list, and source_links list.\n"
        "3. Email_Drafter:\n"
        f"   - subject MUST be exactly: 'Weekly Pulse + Fee Explainer — {today}'\n"
        "   - body MUST have two clearly labelled sections:\n"
        "     Section 1 — WEEKLY PULSE: top themes, 3 user quotes, weekly note, action ideas.\n"
        "     Section 2 — FEE EXPLAINER: fee scenario name, all explanation bullets, "
        "source links, and last checked date.\n"
        "   - No auto-send. This is a draft only."
    )

    user_message = (
        f"Today's date: {today}\n\n"
        f"Weekly Pulse JSON:\n{json.dumps(pulse_data, indent=2)}\n\n"
        f"Exit Load Fee Explainer JSON:\n{json.dumps(fee_data, indent=2)}\n\n"
        f"Call Document_Appender, Google_Doc_Appender, and Email_Drafter now."
    )

    tools = build_groq_tools()

    print("\n📡 Sending Weekly Pulse to Groq for tool-call orchestration...")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_message}
        ],
        tools=tools,
        tool_choice="required",  # Force Groq to always call a tool
        temperature=0.1
    )

    # Extract all function calls from the response
    tool_calls = []
    message = response.choices[0].message
    if message.tool_calls:
        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            tool_calls.append({"tool_name": tool_call.function.name, "args": args})

    return tool_calls


# ──────────────────────────────────────────────
# Main Phase 3 runner
# ──────────────────────────────────────────────

def run_phase3(
    pulse_json_path: str = "../Phase2_LLM_Processing/weekly_pulse_output.json",
):
    print("=" * 60)
    print("  Phase 3: MCP Tool Integration & Human Approval Gates")
    print("=" * 60)

    # Resolve path relative to this file if needed
    if not os.path.exists(pulse_json_path):
        pulse_json_path = str(
            Path(__file__).parent.parent
            / "Phase2_LLM_Processing"
            / "weekly_pulse_output.json"
        )

    if not os.path.exists(pulse_json_path):
        print(f"❌ Error: weekly_pulse_output.json not found at {pulse_json_path}")
        print("   Please run Phase 2 first.")
        return

    # 1. Load Phase 2 outputs
    pulse_data = load_json_file(pulse_json_path)
    print(f"\n✅ Loaded weekly pulse data from:\n   {pulse_json_path}")
    print(f"\n   Themes   : {pulse_data.get('themes', [])}")
    print(f"   Top 3    : {pulse_data.get('top_3_themes', [])}")

    fee_json_path = str(
        Path(__file__).parent.parent / "Phase2_LLM_Processing" / "fee_explanation.json"
    )
    fee_data = {}
    if os.path.exists(fee_json_path):
        fee_data = load_json_file(fee_json_path)
        print(f"✅ Loaded fee explainer data from:\n   {fee_json_path}")
    else:
        print(f"⚠️  fee_explanation.json not found — Google_Doc_Appender will have empty fee data.")

    # 2. Send to Groq → get tool-call proposals
    try:
        tool_calls = run_groq_orchestration(pulse_data, fee_data)
    except Exception as e:
        print(f"\n❌ Groq orchestration failed: {e}")
        return

    if not tool_calls:
        print("\n⚠️  Groq returned no tool calls. Exiting.")
        return

    print(f"\n🔍 Groq proposed {len(tool_calls)} tool call(s).")

    # 3. Human Approval Gate + Execution for each tool call
    results = []
    for tc in tool_calls:
        tool_name = tc["tool_name"]
        args = tc["args"]

        # Validate payload schema before presenting to human
        if not validate_tool_payload(tool_name, args):
            results.append({
                "tool": tool_name,
                "status": "skipped",
                "reason": "Schema validation failed"
            })
            continue

        # Gate: show payload and ask human
        approved = human_approval_gate(tool_name, args)

        if approved:
            result = execute_tool(tool_name, args, OUTPUT_DIR)
            print(f"\n  {result['message']}")
            results.append({
                "tool": tool_name,
                "status": "executed",
                "output_path": result.get("output_path"),
                "success": result.get("success")
            })
        else:
            results.append({
                "tool": tool_name,
                "status": "denied_by_user"
            })

    # 4. Final summary
    print("\n" + "=" * 60)
    print("  Phase 3 Complete — Execution Summary")
    print("=" * 60)
    for r in results:
        status_icon = "✅" if r.get("status") == "executed" else "❌"
        print(f"  {status_icon} {r['tool']:25s} → {r.get('status', 'unknown')}")
        if r.get("output_path"):
            print(f"      Output: {r['output_path']}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    run_phase3()
