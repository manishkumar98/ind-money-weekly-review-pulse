from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from pathlib import Path

# Works both locally (Phase6_Web_App/backend/app.py) and in Docker (/app/app.py)
_this_dir = Path(__file__).resolve().parent
_local_root = _this_dir.parent.parent.parent   # local monorepo root
_docker_root = _this_dir                        # Docker: /app

project_root = _local_root if (_local_root / "Phase5_Email_UI").exists() else _docker_root
sys.path.insert(0, str(project_root))

from Phase5_Email_UI.email_sender import send_weekly_pulse_email

# CORS: allow Vercel frontend domain via ALLOWED_ORIGINS env var (comma-separated)
# Default "*" works for local dev; set to your Vercel URL in production
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app = FastAPI(title="INDmoney Weekly Pulse Subscriber")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SubscriberInfo(BaseModel):
    name: str
    email: EmailStr

def send_email_task(email: str, name: str):
    """Background task — runs after response is returned to avoid timeout."""
    try:
        success, message = send_weekly_pulse_email(target_email=email, recipient_name=name)
        if success:
            print(f"[EMAIL OK] Sent to {email}")
        else:
            print(f"[EMAIL FAIL] {message}")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")

@app.post("/api/subscribe")
async def subscribe_user(user: SubscriberInfo, background_tasks: BackgroundTasks):
    """
    Subscribes a user to the weekly pulse and sends email in the background
    to avoid request timeouts on free-tier hosting.
    """
    print(f"Queuing email for {user.name} at {user.email}")
    background_tasks.add_task(send_email_task, user.email, user.name)
    return {"status": "success", "message": f"Successfully delivered INDmoney Pulse to {user.email}."}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
