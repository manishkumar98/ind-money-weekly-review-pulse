import json
from pathlib import Path
from email_sender import generate_html_poster

json_path = Path(__file__).parent.parent / "Phase2_LLM_Processing" / "weekly_pulse_output.json"
poster_path = Path(__file__).parent / "poster.html"

if json_path.exists():
    with open(json_path, "r", encoding="utf-8") as f:
        pulse_data = json.load(f)
    html_content = generate_html_poster(pulse_data)
    with open(poster_path, "w", encoding="utf-8") as pf:
        pf.write(html_content)
    print(f"📄 Poster HTML saved to {poster_path}")
else:
    print(f"⚠️ warning: {json_path} not found. Cannot generate HTML poster.")
