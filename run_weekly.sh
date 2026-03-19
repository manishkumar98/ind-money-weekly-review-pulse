#!/bin/bash
# Cron job script to run the INDmoney Weekly Pulse Orchestrator automatically

cd /Users/binaykumarsinha/Desktop/aibootcampproject/ind-money-weekly-pulse-view
source venv/bin/activate
printf "Y\nY\n" | python Phase4_Orchestration/main_orchestrator.py
python Phase5_Email_UI/email_sender.py "manish98ad@gmail.com"
