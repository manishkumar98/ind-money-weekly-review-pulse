# What is the "INDmoney Weekly App Review Pulse" Project?

Imagine the product team that builds the INDmoney app. Every day, hundreds of users leave reviews on the App Store or Google Play Store. Some complain about bugs, others request new features, and some leave glowing praise. 

Normally, a product manager or a support agent has to manually read through thousands of these reviews every week. They have to try and spot patterns, copy-paste important quotes into a document, and then write an email to the rest of the company saying, "Here's what our users are feeling this week."

**Our project is an AI assistant that does all this repetitive, manual work automatically in seconds, while still giving the human the final say.**

---

## How it works (Step-by-Step)

### 1. It collects the reviews (Data Gathering)
Instead of a human logging into the App Store, our system runs a scripted "scraper." A scraper is a tool that goes directly to the Google Play Store and Apple App Store and downloads the last 8 to 12 weeks' worth of reviews automatically.

### 2. It protects user privacy (Sanitization)
Before any AI reads these reviews, our system scans them and removes any private information (like phone numbers, email addresses, or real names). We only care about the feedback, not the specific identity of the person leaving it.

### 3. It "Reads" everything incredibly fast (AI Analysis)
We use a super-fast Artificial Intelligence called **Groq**. We feed thousands of cleaned-up reviews to Groq and ask it to play the role of a data analyst. It will:
*   Group thousands of unique reviews into the top 5 main topics (e.g., "Login Bugs", "New Feature Praise", "Customer Service Complaints").
*   Pick out the top 3 most urgent themes.
*   Pull out 3 real, direct quotes from real users as evidence.
*   Write a sharp, 250-word summary note for the team.
*   Suggest 3 action items the company should take based on this feedback.

*We also use the AI to generate a standard, easy-to-understand response to one common INDmoney-specific complaint (like "Why was I charged a fee for US stocks?").*

### 4. It prepares the paperwork (Connecting to Apps)
Once the summary is written, we hand the results over to a second AI named **Gemini**. Gemini knows how to talk to other software (via something called MCP). Gemini will:
*   Connect to the team's internal notes (like a Google Doc or Notion) and format the summary so it can be saved for the record.
*   Open an email drafting tool and write a professional email containing the summary, addressed to the whole product team.

### 5. It waits for Human Approval (The "Gate")
**This is the most important part:** The AI is not allowed to actually send the email or permanently edit the company notes on its own. 

The system will pause and show the human exactly what it wrote and what it intends to do. The human looks it over, makes sure it makes sense, and clicks "Approve." Only then does the AI actually click final "Save" or "Send."

---

## The Ultimate Goal
We are simulating exactly how modern Product and Support teams are using AI. By turning a massive, unstructured pile of comments into a clean weekly summary with action items, we save the team a huge amount of time—allowing humans to focus on actually *fixing* the problems, rather than just *finding* them.
