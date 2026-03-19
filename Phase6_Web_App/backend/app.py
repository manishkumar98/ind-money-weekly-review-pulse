from fastapi import FastAPI, HTTPException
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

@app.post("/api/subscribe")
async def subscribe_user(user: SubscriberInfo):
    """
    Subscribes a user to the weekly pulse and immediately triggers
    an email generation to their given email address with their personalized name.
    """
    print(f"Attempting to send personalized email to {user.name} at {user.email}")
    success, message = send_weekly_pulse_email(
        target_email=user.email,
        recipient_name=user.name
    )

    if success:
        return {"status": "success", "message": f"Successfully delivered INDmoney Pulse to {user.email}."}
    else:
        raise HTTPException(status_code=500, detail=message)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
