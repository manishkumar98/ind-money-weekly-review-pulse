"""
Phase 5 - Email Sender Utility

Reads the generated email draft from Phase 3 and sends it via Brevo API (primary),
Resend API (secondary), or Gmail SMTP (local fallback).
Also generates a beautifully styled HTML "poster" layout based on user quotes.

Priority:
  1. Brevo API  — HTTP-based, works on Render, sends to any email, free tier 300/day
  2. Resend API — HTTP-based, works on Render, free tier limited to account email
  3. Gmail SMTP — local only (Render blocks port 587)
"""

import os
import json
import smtplib
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

def generate_html_poster(json_data, recipient_name=None, fee_data=None):
    """
    Generates a minimalist, beautifully styled HTML string based on a premium 
    client references design.
    """
    quotes = json_data.get("quotes", [])
    themes = json_data.get("top_3_themes", [])
    action_ideas = json_data.get("action_ideas", [])
    note = json_data.get("weekly_note", "")

    # Exit Load Fee Explainer section
    exit_load_html = ""
    if fee_data:
        bullets = fee_data.get("explanation_bullets", [])
        source_links = fee_data.get("source_links", [])
        last_checked = fee_data.get("last_checked", "")
        scenario_name = fee_data.get("scenario_name", "Exit Load")

        bullets_html = "".join(
            f"<li style='margin-bottom: 10px; font-size: 16px; color: #444;'>{b}</li>"
            for b in bullets
        )
        links_html = "".join(
            f"<a href='{lnk}' style='display:block; font-size:13px; color:#0066cc; margin-top:6px; word-break:break-all;'>{lnk}</a>"
            for lnk in source_links
        )
        checked_html = (
            f"<p style='font-size:12px; color:#999; margin-top:16px;'>Last checked: {last_checked}</p>"
            if last_checked else ""
        )

        exit_load_html = f"""
            <div style="border-top: 1px solid #eaeaea; padding: 60px 0;">
                <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 20px; color: #000;">{scenario_name}</h2>
                <ul style="padding-left: 20px; line-height: 1.6; margin: 0;">
                    {bullets_html}
                </ul>
                <div style="margin-top: 20px;">
                    <p style="font-size: 13px; font-weight: 600; color: #333; margin-bottom: 4px;">Official Sources:</p>
                    {links_html}
                </div>
                {checked_html}
            </div>
        """

    # Construct the quotes HTML
    quotes_html = ""
    avatars = ["111822", "607D8B", "F44336", "E91E63", "9C27B0"]
    for i, quote in enumerate(quotes):
        color = avatars[i % len(avatars)]
        img_url = f"https://ui-avatars.com/api/?name=App+User&background={color}&color=fff&rounded=true"
        
        quotes_html += f"""
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top: 40px; margin-bottom: 40px;">
            <tr>
                <td width="30%" valign="top" style="padding-right: 20px;">
                    <img src="{img_url}" width="50" style="border-radius: 50%; float: left; margin-right: 15px; display: block;" />
                    <div style="float: left; padding-top: 6px;">
                        <div style="font-family: inherit; font-weight: 700; font-size: 14px; color: #111;">App User</div>
                        <div style="font-family: inherit; font-size: 12px; color: #666; margin-top: 2px;">Verified Reviewer</div>
                    </div>
                </td>
                <td width="70%" valign="top" style="font-family: inherit; font-size: 22px; font-weight: 400; line-height: 1.5; color: #111; letter-spacing: -0.2px;">
                    "{quote}"
                </td>
            </tr>
        </table>
        """
        
        # Add horizontal separator unless it's the last quote
        if i < len(quotes) - 1:
            quotes_html += """<div style="border-top: 1px solid #eaeaea;"></div>"""

    # Construct the top themes and action ideas as well
    themes_html = ""
    for theme in themes:
         themes_html += f"<li style='margin-bottom: 15px; font-size: 18px;'><strong>{theme}</strong></li>"
         
    actions_html = ""
    for action in action_ideas:
         actions_html += f"<li style='margin-bottom: 15px; font-size: 18px; color: #444;'>{action}</li>"

    greeting_html = ""
    if recipient_name:
        greeting_html = f"""
            <div style="max-width: 900px; margin: 0 auto; padding: 20px 20px 0 20px; text-align: center;">
                <p style="font-size: 22px; font-weight: 500; color: #111; margin: 0;">Hi {recipient_name},</p>
                <p style="font-size: 16px; color: #666; margin-top: 5px;">Here is your INDmoney product review pulse for this week.</p>
            </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {{ margin: 0; padding: 0; background-color: #ffffff; -webkit-font-smoothing: antialiased; }}
    </style>
    </head>
    <body style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; background-color: #ffffff;">
        {greeting_html}
        <div style="max-width: 900px; margin: 0 auto; padding: 20px 20px 40px 20px;">
            
            <!-- Header Section -->
            <div style="text-align: center; padding: 40px 20px 80px 20px;">
                <p style="font-size: 13px; font-weight: 500; text-transform: uppercase; letter-spacing: 1.5px; color: #666; margin-bottom: 25px;">Weekly Pulse References</p>
                <h1 style="font-size: 46px; font-weight: 700; line-height: 1.15; margin: 0; color: #000; letter-spacing: -1px;">
                    Read what our users have to say about INDmoney.
                </h1>
            </div>

            <!-- Quotes Section -->
            <div style="border-top: 1px solid #eaeaea;">
                {quotes_html}
            </div>
            
            <!-- Summary Note -->
            <div style="border-top: 1px solid #eaeaea; padding: 60px 0;">
                <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 20px; color: #000;">Weekly Summary Note</h2>
                <p style="font-size: 18px; line-height: 1.6; color: #444; max-width: 800px;">
                    {note}
                </p>
            </div>

            <!-- Additional Sections -->
            <div style="border-top: 1px solid #eaeaea; padding: 60px 0;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                        <td width="50%" valign="top" style="padding-right: 40px;">
                            <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 30px; color: #000;">Top Themes</h2>
                            <ul style="padding-left: 20px; line-height: 1.5;">
                                {themes_html}
                            </ul>
                        </td>
                        <td width="50%" valign="top" style="padding-left: 40px; border-left: 1px solid #eaeaea;">
                            <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 30px; color: #000;">Action Ideas</h2>
                            <ul style="padding-left: 20px; line-height: 1.5;">
                                {actions_html}
                            </ul>
                        </td>
                    </tr>
                </table>
            </div>
            
            <!-- Exit Load Fee Explainer -->
            {exit_load_html}

            <!-- Footer -->
            <div style="border-top: 1px solid #eaeaea; padding: 40px 0; text-align: center;">
                <p style="font-size: 13px; color: #999;">Generated by AI Pulse System &copy; INDmoney Reviews</p>
            </div>

        </div>
    </body>
    </html>
    """
    return html_content


def send_weekly_pulse_email(target_email: str, recipient_name: str = None):
    """
    Reads the email_draft.txt (for plain text) and weekly_pulse_output.json (for html)
    and sends a beautifully formatted email to the target_email.
    Also saves a 'poster.html' in the current directory.
    """
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        raise ValueError("EMAIL_SENDER or EMAIL_PASSWORD not found in .env file. Please add them.")

    draft_path = Path(__file__).parent.parent / "Phase3_MCP_Integration" / "email_draft.txt"
    json_path = Path(__file__).parent.parent / "Phase2_LLM_Processing" / "weekly_pulse_output.json"
    fee_path = Path(__file__).parent.parent / "Phase2_LLM_Processing" / "fee_explanation.json"

    # Get the date the scheduler last ran (use JSON file mtime if available)
    if json_path.exists():
        run_date = datetime.fromtimestamp(json_path.stat().st_mtime).strftime("%b %d, %Y")
    else:
        run_date = datetime.today().strftime("%b %d, %Y")

    # Read Plain Text Draft
    if draft_path.exists():
        with open(draft_path, "r", encoding="utf-8") as f:
            draft_content = f.read()
        lines = draft_content.split('\n')
        subject = "Weekly INDmoney Product Pulse"
        body_lines = []
        in_body = False
        for line in lines:
            if line.startswith("Subject :"):
                subject = line.replace("Subject :", "").strip()
            elif line.startswith("---") and not in_body:
                in_body = True
            elif in_body and not line.startswith("===") and not line.startswith("---") and "[DRAFT" not in line:
                body_lines.append(line)
        clean_body = "\n".join(body_lines).strip()
    else:
        subject = "Weekly INDmoney Product Pulse"
        clean_body = "The weekly pulse output is attached below."

    subject = f"{subject} ({run_date})"

    # Read JSON and generate HTML poster
    html_content = ""
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            pulse_data = json.load(f)
        fee_data = None
        if fee_path.exists():
            with open(fee_path, "r", encoding="utf-8") as f:
                fee_data = json.load(f)
        html_content = generate_html_poster(pulse_data, recipient_name=recipient_name, fee_data=fee_data)
        
        # Save standalone poster
        poster_path = Path(__file__).parent / "poster.html"
        with open(poster_path, "w", encoding="utf-8") as pf:
            pf.write(html_content)
        print(f"📄 Poster HTML saved to {poster_path}")
    else:
        print(f"⚠️ warning: {json_path} not found. Cannot generate HTML poster.")

    # Construct the email
    msg = MIMEMultipart('alternative')
    msg['From'] = EMAIL_SENDER
    msg['To'] = target_email
    msg['Subject'] = subject

    # Attach Plain text
    part1 = MIMEText(clean_body, 'plain')
    msg.attach(part1)

    # Attach HTML if exists
    if html_content:
        part2 = MIMEText(html_content, 'html')
        msg.attach(part2)

    try:
        if BREVO_API_KEY:
            # Brevo HTTP API — works on Render, sends to any email, 300/day free
            response = requests.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "accept": "application/json",
                    "api-key": BREVO_API_KEY,
                    "content-type": "application/json",
                },
                json={
                    "sender": {"name": "INDmoney Pulse", "email": EMAIL_SENDER},
                    "to": [{"email": target_email, "name": recipient_name or "User"}],
                    "subject": subject,
                    "htmlContent": html_content if html_content else f"<p>{clean_body}</p>",
                    "textContent": clean_body,
                },
            )
            response.raise_for_status()
        elif RESEND_API_KEY:
            # Resend API — free tier only sends to account owner's email
            import resend
            resend.api_key = RESEND_API_KEY
            resend.Emails.send({
                "from": "INDmoney Pulse <onboarding@resend.dev>",
                "to": target_email,
                "subject": subject,
                "html": html_content if html_content else f"<p>{clean_body}</p>",
                "text": clean_body,
            })
        else:
            # Gmail SMTP fallback — local only (Render blocks port 587)
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, target_email, msg.as_string())
            server.quit()

        print(f"✅ Email sent to {target_email}")
        return True, "Email sent successfully."
    except Exception as e:
        error_msg = f"❌ Failed to send email: {str(e)}"
        print(error_msg)
        return False, error_msg

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Send the drafted email.")
    parser.add_argument("target", help="The delivery email address")
    parser.add_argument("--name", help="The recipient's name", default=None)
    args = parser.parse_args()
    send_weekly_pulse_email(args.target, recipient_name=args.name)
