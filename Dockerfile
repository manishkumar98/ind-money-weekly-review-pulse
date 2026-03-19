FROM python:3.11-slim

WORKDIR /app

# Install backend dependencies
COPY Phase6_Web_App/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI backend
COPY Phase6_Web_App/backend/app.py .

# Copy Phase5 email sender (imported by backend)
COPY Phase5_Email_UI/ ./Phase5_Email_UI/

# Copy pre-generated pulse data used by the email sender
COPY Phase2_LLM_Processing/weekly_pulse_output.json ./Phase2_LLM_Processing/
COPY Phase3_MCP_Integration/email_draft.txt ./Phase3_MCP_Integration/
COPY Phase3_MCP_Integration/weekly_pulse_notes.md ./Phase3_MCP_Integration/

EXPOSE 8000

# Railway injects $PORT automatically
CMD sh -c "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"
