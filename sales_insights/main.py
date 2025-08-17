import re
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set")
MODEL = os.getenv("GROQ_MODEL_SALES", "llama3-8b-8192")

client = Groq(api_key=GROQ_API_KEY)
app = FastAPI(title="Sales Insights", version="1.0")

class TextBody(BaseModel):
    textbody: str

class Description(BaseModel):
    description: str

class Opportunity(BaseModel):
    opportunity_id: str
    opportunity_name: str
    account_name: str
    amount: float
    close_date: datetime
    description: str
    forecast_category: Optional[str] = None
    lead_source: Optional[str] = None
    next_step: Optional[str] = None
    reason_lost: Optional[str] = None
    stage: Optional[str] = None
    annual_revenue: Optional[float] = None
    email_text_body: List[TextBody] = []
    task_description: List[Description] = []
    event_description: List[Description] = []

class Case(BaseModel):
    case_id: str
    account_name: str
    case_origin: Optional[str] = None
    case_reason: str
    case_source: Optional[str] = None
    closed_date: Optional[datetime] = None
    close_summary: Optional[str] = None
    contact_reason: Optional[str] = None
    customer_type: Optional[str] = None
    date_closed: Optional[datetime] = None
    date_opened: datetime
    description: str
    duration: Optional[float] = None
    escalated: Optional[bool] = None
    priority: Optional[str] = None
    quality_score: Optional[float] = None
    status: str
    subject: str
    time_open: Optional[float] = None
    type: Optional[str] = None
    email_text_body: List[TextBody] = []
    task_description: List[Description] = []
    event_description: List[Description] = []

@app.get("/healthz")
def healthz():
    return {"ok": True, "model": MODEL}

def generate_response(prompt: str) -> str:
    resp = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL
    )
    return resp.choices[0].message.content or ""

@app.post("/generate-opportunity-responses")
def generate_opportunity_responses(opportunities: List[Opportunity]):
    results = []
    for opp in opportunities:
        prompt = f"""
You are a professional sales agent. Respond with three single-line items:

1. Summary: a concise one-line summary of the opportunity.
2. Objection: a likely customer objection, or write "No objection".
3. Next Best Action: the one best next step.

Context:
Opportunity ID: {opp.opportunity_id}
Name: {opp.opportunity_name}
Account: {opp.account_name}
Amount: {opp.amount}
Close Date: {opp.close_date}
Description: {opp.description}
Emails: {" ".join([e.textbody for e in opp.email_text_body])}
Tasks: {" ".join([t.description for t in opp.task_description])}
Events: {" ".join([e.description for e in opp.event_description])}

Output format:
1. Summary: <text>
2. Objection: <text>
3. Next Best Action: <text>
"""
        raw = generate_response(prompt)
        s = re.search(r"1\. *Summary:\s*(.*?)\s*2\.", raw, re.DOTALL)
        o = re.search(r"2\. *Objection:\s*(.*?)\s*3\.", raw, re.DOTALL)
        nba = re.search(r"3\. *Next Best Action:\s*(.*)", raw, re.DOTALL)
        results.append({
            "opportunity_id": opp.opportunity_id,
            "opportunity_name": opp.opportunity_name,
            "summary": s.group(1).strip() if s else "Summary not provided",
            "objection": o.group(1).strip() if o else "Objection not provided",
            "next_best_action": nba.group(1).strip() if nba else "Next Best Action not provided",
            "amount": opp.amount,
            "close_date": opp.close_date
        })
    return {"opportunities": results}

@app.post("/generate-case-responses")
def generate_case_responses(cases: List[Case]):
    results = []
    for case in cases:
        prompt = f"""
You are a professional case manager. Respond with four items:

1. Summary: one concise line summarizing the case.
2. Intent: one concise line describing customer intent.
3. Sentiment: one word: positive, negative, or neutral.
4. Days Open: numeric value only, no words.

Context:
Case ID: {case.case_id}
Account: {case.account_name}
Reason: {case.case_reason}
Status: {case.status}
Subject: {case.subject}
Description: {case.description}
Date Opened: {case.date_opened}
Date Closed: {case.date_closed}

Output format:
1. Summary: <text>
2. Intent: <text>
3. Sentiment: <positive|negative|neutral>
4. Days Open: <number>
"""
        raw = generate_response(prompt)
        s = re.search(r"1\. *Summary:\s*(.*?)\s*2\.", raw, re.DOTALL)
        i = re.search(r"2\. *Intent:\s*(.*?)\s*3\.", raw, re.DOTALL)
        sent = re.search(r"3\. *Sentiment:\s*(.*?)\s*4\.", raw, re.DOTALL)
        days = re.search(r"4\. *Days Open:\s*(\d+)", raw, re.DOTALL)

        summary = s.group(1).strip() if s else "Summary not provided"
        intent = i.group(1).strip() if i else "Intent not provided"
        sentiment = sent.group(1).strip().lower() if sent else "neutral"
        if days:
            days_open = days.group(1).strip()
        else:
            # fallback compute if LLM fails
            opened = case.date_opened.replace(tzinfo=timezone.utc)
            closed = (case.date_closed or datetime.now(timezone.utc))
            days_open = str((closed - opened).days)

        results.append({
            "case_id": case.case_id,
            "case": case.subject,
            "summary": summary,
            "intent": intent,
            "sentiment": sentiment,
            "days_open": days_open
        })
    return {"cases_reponses": results}
