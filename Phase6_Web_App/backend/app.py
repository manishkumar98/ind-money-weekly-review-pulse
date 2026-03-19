from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from pathlib import Path

# Add project root to python path to import email sender
sys.path.append(str(Path(__file__).parent.parent.parent))

from Phase5_Email_UI.email_sender import send_weekly_pulse_email

app = FastAPI(title="INDmoney Weekly Pulse Subscriber")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    print(f"🌟 Attempting to send personalized email to {user.name} at {user.email}")
    success, message = send_weekly_pulse_email(
        target_email=user.email,
        recipient_name=user.name
    )
    
    if success:
        return {"status": "success", "message": f"Successfully delivered INDmoney Pulse to {user.email}."}
    else:
        raise HTTPException(status_code=500, detail=message)

# Mount the frontend folder to serve the index.html
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
