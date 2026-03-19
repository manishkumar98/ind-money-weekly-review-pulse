"""
Streamlit UI to preview and manually trigger the final email
"""
import streamlit as st
import os
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from email_sender import send_weekly_pulse_email, generate_html_poster
import json
import streamlit.components.v1 as components

# Load credentials from Streamlit Cloud secrets if available, else fall back to .env
if hasattr(st, "secrets") and "EMAIL_SENDER" in st.secrets:
    os.environ["EMAIL_SENDER"] = st.secrets["EMAIL_SENDER"]
    os.environ["EMAIL_PASSWORD"] = st.secrets["EMAIL_PASSWORD"]

st.set_page_config(page_title="INDmoney Weekly Pulse", page_icon="📈", layout="wide")

st.title("🎯 INDmoney Weekly Pulse Orchestrator")
st.markdown("This dashboard allows you to view the final generated pulse and manually trigger the email to a specific stakeholder.")

# Paths
base_dir = Path(__file__).parent.parent
md_file_path = base_dir / "Phase3_MCP_Integration" / "weekly_pulse_notes.md"
email_draft_path = base_dir / "Phase3_MCP_Integration" / "email_draft.txt"
json_path = base_dir / "Phase2_LLM_Processing" / "weekly_pulse_output.json"

tab1, tab2, tab3 = st.tabs(["📧 Email Draft Preview", "📝 Markdown Report Preview", "🖼️ HD Poster Preview"])

with tab1:
    st.subheader("Final Email Output")
    if email_draft_path.exists():
        with open(email_draft_path, "r", encoding="utf-8") as file:
            draft_content = file.read()
        st.code(draft_content, language="text")
    else:
        st.warning("No email draft found yet! Did you complete Phase 3 or Phase 4?")

with tab2:
    st.subheader("Final Markdown Notes")
    if md_file_path.exists():
        with open(md_file_path, "r", encoding="utf-8") as file:
            md_content = file.read()
            st.markdown(md_content)
    else:
        st.warning("No Markdown notes found yet! Did you complete Phase 3 or Phase 4?")

with tab3:
    st.subheader("Modern HTML Poster Layout")
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            pulse_data = json.load(f)
        html_poster = generate_html_poster(pulse_data)
        components.html(html_poster, height=800, scrolling=True)
    else:
        st.warning("No JSON data found (weekly_pulse_output.json)! Run Phase 2/4 first.")

# Email Trigger Zone 
st.divider()
st.subheader("✉️ Send Final Pulse Email")

with st.form("email_form", clear_on_submit=False):
    target_email = st.text_input("Send Pulse to Email:", value="stakeholder@example.com")
    submitted = st.form_submit_button("Send Email 🚀", type="primary")

    if submitted:
        st.info("Attempting to send via SMTP...")
        success, message = send_weekly_pulse_email(target_email)
        if success:
            st.success("✅ Email successfully delivered via Gmail!")
        else:
            st.error(message)
            st.markdown("**Did you forget to add your EMAIL_SENDER and EMAIL_PASSWORD to `.env`?**")
