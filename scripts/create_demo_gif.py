"""
Creates a terminal-style animated GIF demo showing the INDmoney Weekly Pulse pipeline.
Frames cycle through: pipeline phases → approval gates → dashboard tabs.
"""

from PIL import Image, ImageDraw, ImageFont
import imageio
import os

W, H = 900, 520
BG       = (15, 17, 26)
GREEN    = (74, 222, 128)
BLUE     = (96, 165, 250)
YELLOW   = (251, 191, 36)
RED      = (248, 113, 113)
PURPLE   = (167, 139, 250)
CYAN     = (34, 211, 238)
WHITE    = (255, 255, 255)
GREY     = (148, 163, 184)
DIM      = (71, 85, 105)
ORANGE   = (251, 146, 60)

FONT_PATH = "/System/Library/Fonts/Menlo.ttc"
try:
    MONO   = ImageFont.truetype(FONT_PATH, 14)
    MONO_S = ImageFont.truetype(FONT_PATH, 12)
    MONO_L = ImageFont.truetype(FONT_PATH, 16)
    MONO_XL= ImageFont.truetype(FONT_PATH, 20)
except:
    MONO = MONO_S = MONO_L = MONO_XL = ImageFont.load_default()

def base_frame(title="INDmoney Weekly Pulse — AI Pipeline"):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # title bar
    d.rectangle([0, 0, W, 34], fill=(30, 32, 44))
    for i, c in enumerate(["#FF5F57","#FFBD2E","#28C840"]):
        d.ellipse([12+i*20, 9, 26+i*20, 23], fill=c)
    d.text((W//2, 17), title, fill=GREY, font=MONO_S, anchor="mm")
    return img, d

def text_lines(d, lines, start_y=50, x=20):
    y = start_y
    for color, text in lines:
        d.text((x, y), text, fill=color, font=MONO)
        y += 22
    return y

# ── FRAMES ────────────────────────────────────────────────────────────────────

def frame_title():
    img, d = base_frame()
    cx = W // 2
    d.text((cx, 140), "INDmoney", fill=BLUE, font=MONO_XL, anchor="mm")
    d.text((cx, 168), "Weekly Product Pulse + Fee Explainer", fill=WHITE, font=MONO_L, anchor="mm")
    d.text((cx, 200), "Automated AI Pipeline  ·  6 Phases  ·  MCP Tool Calling", fill=GREY, font=MONO_S, anchor="mm")
    # phase badges
    phases = [("Phase 1","Ingest",GREEN),("Phase 2","LLM",BLUE),("Phase 3","MCP",PURPLE),
              ("Phase 5","Email",YELLOW),("Phase 6","Dashboard",ORANGE)]
    bx = 60
    for label, sub, col in phases:
        d.rounded_rectangle([bx, 240, bx+130, 290], radius=8, fill=(30,32,44), outline=col, width=1)
        d.text((bx+65, 258), label, fill=col, font=MONO_S, anchor="mm")
        d.text((bx+65, 276), sub, fill=GREY, font=MONO_S, anchor="mm")
        bx += 150
    d.text((cx, 340), "github.com/manishkumar98/ind-money-weekly-review-pulse", fill=DIM, font=MONO_S, anchor="mm")
    return img

def frame_phase1():
    img, d = base_frame("Phase 1 — Data Ingestion")
    text_lines(d, [
        (GREEN,  "$ python Phase1_Data_Ingestion/phase1_data_ingestion.py"),
        (GREY,   ""),
        (WHITE,  "--- Starting Phase 1: Data Ingestion ---"),
        (GREY,   "Scraping Google Play Store reviews for INDmoney..."),
        (GREEN,  "✓  Fetched 150 reviews (Play Store)"),
        (GREEN,  "✓  Fetched 76  reviews (App Store)"),
        (GREY,   "Running PII sanitizer..."),
        (GREEN,  "✓  Removed names, emails, phone numbers"),
        (GREEN,  "✓  Deduplicated: 226 unique reviews retained"),
        (GREY,   ""),
        (WHITE,  "Output: Phase1_Data_Ingestion/sanitized_indmoney_reviews.csv"),
        (GREEN,  "--- Phase 1 Complete ---"),
    ], start_y=55)
    # mini table
    d.rectangle([20, 330, 860, 500], fill=(22,25,37))
    cols = [("source",120),("date",180),("rating",80),("text",450)]
    x = 30
    for col, w in cols:
        d.text((x, 340), col.upper(), fill=PURPLE, font=MONO_S)
        x += w
    rows = [
        ("Google Play","2026-03-27","5","Flash mode is very easy and beneficial for trading..."),
        ("Google Play","2026-03-25","1","Poor performance since some days. Slow, price update issue..."),
        ("App Store",  "2026-03-20","4","Best app for options trading. Very intuitive design and UI."),
    ]
    y = 362
    for row in rows:
        x = 30
        for val, (_, w) in zip(row, cols):
            color = GREEN if val=="5" else (RED if val=="1" else YELLOW if val=="4" else WHITE)
            d.text((x, y), val[:int(w/8)], fill=color if col=="rating" else WHITE, font=MONO_S)
            x += w
        y += 22
    return img

def frame_phase2():
    img, d = base_frame("Phase 2 — LLM Processing (Groq / Llama 3)")
    text_lines(d, [
        (GREEN,  "$ python Phase2_LLM_Processing/phase2_llm_processing.py"),
        (GREY,   ""),
        (WHITE,  "--- Starting Phase 2: LLM Processing ---"),
        (GREY,   "Loaded 226 sanitized reviews."),
        (GREY,   "Sending reviews to Groq API in 2 halves..."),
        (GREEN,  "✓  Half 1 processed (113 reviews)"),
        (GREEN,  "✓  Half 2 processed (113 reviews)"),
        (GREEN,  "✓  Synthesised weekly pulse (Llama 3.1-8b-instant)"),
    ], start_y=55)
    # JSON preview
    d.rectangle([20, 240, 540, 500], fill=(22,25,37))
    d.text((30, 248), "weekly_pulse_output.json", fill=PURPLE, font=MONO_S)
    json_lines = [
        (DIM,    '{'),
        (BLUE,   '  "themes":'),
        (WHITE,  '    ["User Interface","Features","Performance",'),
        (WHITE,  '     "Customer Support","Security"],'),
        (BLUE,   '  "top_3_themes":'),
        (GREEN,  '    ["User Interface","Features","Performance"],'),
        (BLUE,   '  "quotes": ['),
        (YELLOW, '    "very easy to pick up for the commoner",'),
        (YELLOW, '    "Flash mode is very easy and beneficial",'),
        (YELLOW, '    "Poor performance since some days"],'),
        (BLUE,   '  "action_ideas": ["Improve performance...",'),
        (WHITE,  '    "Enhance customer support...","Add features..."]'),
        (DIM,    '}'),
    ]
    y = 268
    for col, txt in json_lines:
        d.text((30, y), txt, fill=col, font=MONO_S)
        y += 18

    d.rectangle([560, 240, 880, 500], fill=(22,25,37))
    d.text((570, 248), "analytics_data.json", fill=ORANGE, font=MONO_S)
    a_lines = [
        (WHITE,  '"review_count": 226,'),
        (BLUE,   '"keywords": ['),
        (WHITE,  '  {w:"trading", n:54},'),
        (WHITE,  '  {w:"best",    n:35},'),
        (WHITE,  '  {w:"option",  n:31}...'),
        (DIM,    '],'),
        (BLUE,   '"sentiment": {'),
        (GREEN,  '  "positive": 155,'),
        (YELLOW, '  "neutral":  7,'),
        (RED,    '  "negative": 64'),
        (DIM,    '},'),
        (BLUE,   '"rating_dist": {'),
        (GREEN,  '  "5": 121, "4": 34,'),
        (YELLOW, '  "3": 7,   "2": 11,'),
        (RED,    '  "1": 53'),
        (DIM,    '}'),
    ]
    y = 268
    for col, txt in a_lines:
        d.text((570, y), txt, fill=col, font=MONO_S)
        y += 15
    return img

def frame_phase3_propose():
    img, d = base_frame("Phase 3 — MCP Tool Calling (Approval Gate)")
    text_lines(d, [
        (GREEN,  "$ python Phase3_MCP_Integration/phase3_mcp_orchestration.py"),
        (GREY,   ""),
        (WHITE,  "--- Starting Phase 3: MCP Orchestration (Groq) ---"),
        (GREY,   "Model: llama-3.3-70b-versatile  |  Tool choice: required"),
        (GREY,   ""),
        (PURPLE, "🤖 GROQ PROPOSES TOOL CALL: Document_Appender"),
    ], start_y=55)
    d.rectangle([20, 195, 860, 340], fill=(22,25,37), outline=PURPLE, width=1)
    d.text((30, 205), "{", fill=DIM, font=MONO_S)
    payload = [
        ('  "filename": "weekly_pulse_notes.md",', WHITE),
        ('  "content": {', BLUE),
        ('    "date": "2026-03-27",', YELLOW),
        ('    "weekly_pulse": { themes, top_3_themes, quotes, weekly_note, action_ideas },', GREY),
        ('    "fee_scenario": "SBI Mutual Funds — Exit Load",', YELLOW),
        ('    "explanation_bullets": ["SBI Large Cap Fund: 1% exit load...", ...],', GREY),
        ('    "source_links": ["https://www.sbimf.com/..."]', GREY),
        ('  }', BLUE),
    ]
    y = 223
    for txt, col in payload:
        d.text((30, y), txt, fill=col, font=MONO_S)
        y += 14
    d.text((30, y), "}", fill=DIM, font=MONO_S)
    return img

def frame_phase3_gate():
    img, d = base_frame("Phase 3 — Human Approval Gate")
    text_lines(d, [
        (PURPLE, "🤖 GROQ PROPOSES TOOL CALL: Document_Appender"),
        (GREY,   ""),
        (WHITE,  "============================================================"),
        (YELLOW, "  ⚠️   Approve execution of 'Document_Appender'? [Y/N]:"),
        (WHITE,  "============================================================"),
        (GREY,   ""),
        (GREEN,  "  Y"),
        (GREY,   ""),
        (GREEN,  "✓  Executing Document_Appender..."),
        (GREEN,  "✓  weekly_pulse_notes.md updated"),
    ], start_y=55)
    # gate 2
    text_lines(d, [
        (GREY,   ""),
        (WHITE,  "============================================================"),
        (YELLOW, "  ⚠️   Approve execution of 'Google_Doc_Appender'? [Y/N]:"),
        (WHITE,  "============================================================"),
        (GREY,   ""),
        (GREEN,  "  Y"),
        (GREEN,  "✓  MCP server spawned (FastMCP stdio transport)"),
        (GREEN,  "✓  JSON appended to Google Doc"),
    ], start_y=285)
    return img

def frame_phase3_email():
    img, d = base_frame("Phase 3 — Email Draft Created (Approval-Gated)")
    text_lines(d, [
        (WHITE,  "============================================================"),
        (YELLOW, "  ⚠️   Approve execution of 'Email_Drafter'? [Y/N]:"),
        (WHITE,  "============================================================"),
        (GREEN,  "  Y"),
        (GREEN,  "✓  email_draft.txt written"),
        (GREY,   ""),
    ], start_y=55)
    d.rectangle([20, 190, 860, 490], fill=(22,25,37))
    draft = [
        (DIM,    "============================================================"),
        (WHITE,  "  EMAIL DRAFT — 2026-03-27"),
        (DIM,    "============================================================"),
        (GREY,   "To      : Product Team"),
        (BLUE,   "Subject : Weekly Pulse + Fee Explainer — 2026-03-27"),
        (DIM,    "------------------------------------------------------------"),
        (WHITE,  ""),
        (PURPLE, "Section 1 — WEEKLY PULSE:"),
        (WHITE,  "Top themes: User Interface, Features, Performance"),
        (YELLOW, '"very easy to pick up for the commoner to trade"'),
        (YELLOW, '"Flash mode is very easy and beneficial for trading"'),
        (WHITE,  "Action ideas: Improve performance, Enhance support..."),
        (WHITE,  ""),
        (PURPLE, "Section 2 — FEE EXPLAINER:"),
        (WHITE,  "SBI Large Cap Fund: 1% exit load if redeemed within 365 days"),
        (WHITE,  "SBI Flexicap Fund: Nil exit load"),
        (WHITE,  "SBI Small Cap Fund: 1% exit load if redeemed within 18 months"),
        (GREY,   "Source: sbimf.com  |  Last checked: March 27, 2026"),
        (DIM,    ""),
        (DIM,    "[DRAFT — Pending human review before sending]"),
    ]
    y = 200
    for col, txt in draft:
        d.text((30, y), txt, fill=col, font=MONO_S)
        y += 14
    return img

def frame_dashboard(tab_name, desc_lines, active=2):
    img, d = base_frame(f"Dashboard — {tab_name}")
    tabs = ["🔒 Gate","📧 Draft","📝 Report","🖼️ Poster","📊 Analytics","☁️ Words","🏷️ Cats","⚡ Ideas"]
    tw = W // len(tabs)
    for i, t in enumerate(tabs):
        col = BLUE if i == active else DIM
        bg  = (30,45,80) if i == active else (22,25,37)
        d.rectangle([i*tw, 36, (i+1)*tw-2, 62], fill=bg)
        d.text((i*tw + tw//2, 49), t, fill=col, font=MONO_S, anchor="mm")

    d.rectangle([0, 62, W, 64], fill=BLUE)

    y = 80
    for col, txt in desc_lines:
        d.text((30, y), txt, fill=col, font=MONO)
        y += 24
    return img

def frame_email_sent():
    img, d = base_frame("Phase 5 — Email Sent via Brevo API")
    text_lines(d, [
        (GREEN,  "$ Recipient: manish.kumar@nia.one"),
        (GREY,   ""),
        (WHITE,  "Sending via Brevo API (HTTP — works on Render free tier)..."),
        (GREEN,  "✓  200 OK — Email delivered"),
        (GREY,   ""),
        (WHITE,  "Subject: Weekly Pulse + Fee Explainer — 2026-03-27 (Mar 27, 2026)"),
        (GREY,   ""),
        (PURPLE, "Email content:"),
        (WHITE,  "  • Header: 'Read what our users have to say about INDmoney'"),
        (WHITE,  "  • 3 verified user quote cards"),
        (WHITE,  "  • Weekly Summary Note (≤250 words)"),
        (WHITE,  "  • Top Themes  |  Action Ideas"),
        (WHITE,  "  • Exit Load Explainer (SBI MF — 6 bullets + 2 source links)"),
        (GREEN,  ""),
        (GREEN,  "✓  poster.html saved for local preview"),
        (GREEN,  "--- Phase 5 Complete ---"),
    ], start_y=55)
    return img

FRAMES_SPEC = [
    (frame_title,        60),
    (frame_phase1,       80),
    (frame_phase2,       90),
    (frame_phase3_propose, 70),
    (frame_phase3_gate,  70),
    (frame_phase3_email, 80),
    (frame_email_sent,   80),
    (lambda: frame_dashboard("Approval Gate", [
        (WHITE,  "✓  Weekly pulse generated          2026-03-27"),
        (WHITE,  "✓  Notes appended to Google Doc    2026-03-27"),
        (WHITE,  "✓  Email draft created              2026-03-27"),
        (WHITE,  "✓  No PII in outputs verified       2026-03-27"),
        (GREY,   ""),
        (BLUE,   "Weekly Summary (editable):"),
        (GREY,   "The INDmoney app has received mixed reviews. Users praise"),
        (GREY,   "trading features and UI, but raise concerns about performance"),
        (GREY,   "and customer support."),
        (GREY,   ""),
        (GREEN,  "[ 📎 Send to Notes ]  [ 📧 Create Draft ]  [ ✅ Do Both & Finish ]"),
    ], active=0), 80),
    (lambda: frame_dashboard("Analytics", [
        (WHITE,  "Total Issues: 85      Active Tickets: 1      Categories: 4"),
        (GREY,   ""),
        (BLUE,   "Week-wise Issues by Category  [ Bar Chart | Trend Line ]"),
        (GREY,   ""),
        (WHITE,  "Performance  ████████████████░░░░  14"),
        (WHITE,  "Features     ████████░░░░░░░░░░░░   4"),
        (WHITE,  "UI/UX        ██████████░░░░░░░░░░   9"),
        (WHITE,  "General      ████████████░░░░░░░░  10"),
        (GREY,   ""),
        (PURPLE, "Category Tracker:  Performance Issues  HIGH  PB-6307"),
        (PURPLE, "                   Missing Features    MEDIUM  No tickets"),
    ], active=4), 80),
    (lambda: frame_dashboard("Word Cloud", [
        (BLUE,   "Reviews Analyzed: 226    Total Words: 3,694    Unique: 1,273"),
        (GREY,   ""),
        (GREEN,  "        trading   best  option  chart"),
        (CYAN,   "   platform    app    performance    support"),
        (YELLOW, "      easy   update   good   interface   excellent"),
        (PURPLE, "  investment  feature  order  market  slow"),
        (ORANGE, "      brokerage  seamless   data   trading"),
        (GREY,   ""),
        (WHITE,  "Top Keywords:  trading(54)  best(35)  option(31)  chart(24)"),
    ], active=5), 80),
    (lambda: frame_dashboard("Categories", [
        (WHITE,  "👍 General Praise: 120 reviews (12%)"),
        (WHITE,  "🖥️  UI/UX:          27 reviews (2.7%)"),
        (WHITE,  "⚡ Performance:    24 reviews (2.4%)"),
        (GREY,   ""),
        (BLUE,   "Sentiment Analysis:"),
        (GREEN,  "  Positive  ████████████████████  155"),
        (YELLOW, "  Neutral   ██░░░░░░░░░░░░░░░░░░    7"),
        (RED,    "  Negative  █████████░░░░░░░░░░░   64"),
        (GREY,   ""),
        (BLUE,   "Rating Distribution:"),
        (GREEN,  "  5★ ████████████████████  121   4★ ████  34"),
        (RED,    "  1★ ████████████░░░░░░░░   53   2★ ██   11"),
    ], active=6), 80),
    (lambda: frame_dashboard("Ideation", [
        (YELLOW, "💡 AI Idea Recommender"),
        (WHITE,  ""),
        (GREEN,  "  Fix Chart Lag in Flash Mode          [High Impact]"),
        (GREY,   "  Multiple users report lagging option charts during"),
        (GREY,   "  high-volatility sessions."),
        (WHITE,  ""),
        (GREEN,  "  Improve Customer Support SLA         [High Impact]"),
        (GREY,   "  Reviews cite tickets closed without resolution."),
        (WHITE,  ""),
        (YELLOW, "  Add Trailing Stop-Loss               [Medium Impact]"),
        (GREY,   "  Power traders explicitly request this standard feature."),
        (WHITE,  ""),
        (RED,    "🐛 Bug Reporter — Select reviews → Generate Report"),
    ], active=7), 80),
    (frame_title, 60),
]

def build_gif():
    frames = []
    for fn, duration_frames in FRAMES_SPEC:
        img = fn()
        for _ in range(duration_frames):
            frames.append(img)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "Docs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "demo.gif")

    imageio.mimsave(
        out_path,
        [f.convert("P", palette=Image.ADAPTIVE, colors=256) for f in frames],
        format="GIF",
        loop=0,
        duration=1000/30,
    )
    size_kb = os.path.getsize(out_path) // 1024
    print(f"✅ demo.gif saved → {out_path}  ({size_kb} KB, {len(frames)} frames)")

if __name__ == "__main__":
    build_gif()
