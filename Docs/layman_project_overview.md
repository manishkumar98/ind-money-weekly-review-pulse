# INDmoney Weekly Pulse — Plain English Overview

## The Problem

The INDmoney app has thousands of users. Every single day, those users leave reviews on the Google Play Store and Apple App Store. Some say the app is great. Some complain about bugs. Some ask for new features. Some report being charged unexpected fees.

**The problem:** A product manager or support team member has to manually read through hundreds of these reviews every week. They need to spot patterns ("are more people complaining about login issues this week?"), pull out the most important quotes, write a summary document, and email it to the whole product team. This takes hours of repetitive, tedious work — every single week.

**What if an AI could do all of that in under 3 minutes, automatically, every Saturday morning?**

That is exactly what this project does.

---

## What This Project Does — In Plain English

Think of it like hiring an extremely fast, tireless assistant who:

1. Reads every app review published in the last 8–12 weeks
2. Protects users' privacy by removing personal details before anyone (or any AI) reads them
3. Identifies the top themes users are talking about
4. Picks out the most powerful direct quotes from real users
5. Writes a clear weekly summary note
6. Suggests 3 concrete action items the product team should act on
7. Drafts a professional email and sends it
8. Updates a live dashboard on the internet — all without a human lifting a finger

And every Saturday morning at 10:00 AM, it does all of this again automatically with the fresh week's reviews.

---

## The 6 Steps (How It Actually Works)

### Step 1 — Collect Reviews (Data Ingestion)
A script acts like a robot browser. It visits the Google Play Store and Apple App Store and downloads all recent INDmoney reviews — up to several thousand at a time. It stores them in a spreadsheet-like file.

**Tool used:** `google-play-scraper`, `app-store-scraper`, `pandas`

---

### Step 2 — Protect Privacy (Sanitization)
Before any AI reads the reviews, the system scans every review and removes anything that could identify a real person — phone numbers, email addresses, names. Only the feedback text itself goes forward.

Reviews shorter than 5 words are also discarded (e.g. "Good app" tells us nothing useful). Duplicate reviews are removed.

---

### Step 3 — AI Reads Everything (LLM Analysis with Groq)
We send the cleaned reviews to **Groq** — a lightning-fast AI that uses Meta's Llama 3 model. We give it clear instructions:

> "You are an expert INDmoney Product Manager. Read these reviews and give me:
> - The top 5 themes users are talking about
> - The top 3 most important themes
> - 3 direct quotes from real users
> - A 250-word weekly summary
> - 3 action items the team should take"

Groq returns a structured response in seconds. We also ask it to explain one common INDmoney fee scenario in plain language (e.g., "Why was I charged for withdrawing US stocks?").

**Tool used:** Groq API (Llama 3 model)

---

### Step 4 — Prepare Documents & Draft Email (MCP Integration with Gemini)
We hand the Groq output to **Gemini** (Google's AI). Gemini is better at "tool use" — meaning it can be told to prepare formatted documents and emails.

Gemini uses something called **MCP (Model Context Protocol)** — a standard way for AI models to interact with external apps and tools. It:
- Formats and saves a weekly notes file (like a running Google Doc entry)
- Drafts a professional email ready to send to the product team

**A human approval gate sits here:** in automated runs, the system auto-approves. When run manually, it pauses and shows you exactly what it will write and asks "Y/N" before doing anything.

**Tool used:** Gemini API, MCP tools

---

### Step 5 — Send the Email (Automated Delivery)
The system sends a beautifully styled HTML email to the configured recipient. The email contains:
- A personal greeting
- All user quotes with avatar icons
- The weekly summary note
- Top themes and action ideas

On cloud servers, it uses the **Resend API** (because Gmail is blocked on most cloud providers). Locally, it uses Gmail's SMTP.

**Tool used:** Resend API, Gmail SMTP fallback

---

### Step 6 — Update the Public Dashboard & Publish (Web App)
The system updates a live website dashboard that shows:
- **Email Draft tab** — the exact email that was (or will be) sent
- **Markdown Report tab** — the full running weekly notes history
- **Pulse Poster tab** — a visual card with themes, quotes, and action ideas

Anyone can also enter their name and email on the subscribe page to get the pulse email sent directly to them.

The website is hosted free on **Vercel** (frontend) and **Render** (backend API for send-email). Every Saturday after the pipeline runs, the dashboard automatically updates with the new week's data.

**Tool used:** HTML/CSS/JS (Vercel), FastAPI (Render), GitHub Actions

---

## The Big Picture: One Diagram

```
Every Saturday 10:00 AM IST
         │
         ▼
  GitHub Actions wakes up
         │
         ├──► Scrape reviews from Play Store + App Store
         │
         ├──► Strip private info (PII removal)
         │
         ├──► Send to Groq AI → get themes, quotes, summary, actions
         │
         ├──► Send to Gemini AI → draft notes file + email
         │
         ├──► Send email to recipient via Resend API
         │
         ├──► Inject new data into dashboard.html
         │
         └──► Push to GitHub → Vercel auto-deploys new dashboard
                                        │
                                        ▼
                              Live dashboard updated ✅
```

---

## Who Can Use This

| User | What They Get |
|---|---|
| Product Manager | Weekly email every Saturday with themes, quotes, action items |
| Anyone who subscribes | Same pulse email delivered on demand via the subscribe page |
| Developer / Technical user | Full pipeline they can run locally, modify, or extend |

---

## Why This Matters

Without this system, a product manager might spend 3–4 hours every week just reading reviews and writing summaries. This system reduces that to zero manual effort, while still keeping the human in the loop — they get the finished summary, review it, and decide what to act on.

It is a practical demonstration of how modern AI tools (Groq, Gemini, MCP) can be combined into a real automated workflow that solves a real business problem.
