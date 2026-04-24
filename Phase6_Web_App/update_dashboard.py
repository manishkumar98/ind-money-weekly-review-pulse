"""
Reads the latest pipeline outputs and injects them into dashboard.html
as baked-in JS constants. Run after the weekly pipeline completes.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = Path(__file__).resolve().parent / "frontend" / "dashboard.html"

draft_path = ROOT / "Phase3_MCP_Integration" / "email_draft.txt"
notes_path = ROOT / "Phase3_MCP_Integration" / "weekly_pulse_notes.md"
json_path  = ROOT / "Phase2_LLM_Processing"  / "weekly_pulse_output.json"
fee_path   = ROOT / "Phase2_LLM_Processing"  / "fee_explanation.json"

draft  = draft_path.read_text(encoding="utf-8").strip()
notes  = notes_path.read_text(encoding="utf-8").strip()
pulse  = json.loads(json_path.read_text(encoding="utf-8"))
fee    = json.loads(fee_path.read_text(encoding="utf-8")) if fee_path.exists() else None

# Escape backticks so they don't break JS template literals
def escape_js(text):
    return text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

html = DASHBOARD.read_text(encoding="utf-8")

# Replace EMAIL_DRAFT constant
draft_js = escape_js(draft)
html = re.sub(
    r"(const EMAIL_DRAFT = `)[\s\S]*?(`;)",
    lambda m: f"const EMAIL_DRAFT = `{draft_js}`;",
    html
)

# Replace NOTES_MD constant
notes_js = escape_js(notes)
html = re.sub(
    r"(const NOTES_MD = `)[\s\S]*?(`;)",
    lambda m: f"const NOTES_MD = `{notes_js}`;",
    html
)

# Replace PULSE_DATA constant
pulse_js = json.dumps(pulse, indent=12)
html = re.sub(
    r"(const PULSE_DATA = )\{[\s\S]*?\};",
    lambda m: f"const PULSE_DATA = {pulse_js};",
    html
)

# Replace FEE_DATA constant
if fee:
    fee_js = json.dumps(fee)
    html = re.sub(
        r"(const FEE_DATA = )\{[\s\S]*?\};",
        lambda m: f"const FEE_DATA = {fee_js};",
        html
    )

# Update week label in the draft tab
from datetime import date
week_str = f"Week of {date.today().strftime('%B %-d, %Y')}"
html = re.sub(
    r'(<div class="week-label">).*?(</div>)',
    f'\\1{week_str}\\2',
    html
)

DASHBOARD.write_text(html, encoding="utf-8")
print(f"✅ dashboard.html updated with latest pulse data ({week_str})")
