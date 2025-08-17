from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any
from groq import Groq
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set")
MODEL = os.getenv("GROQ_MODEL_CALLS", "llama3-70b-8192")

client = Groq(api_key=GROQ_API_KEY)
app = FastAPI(title="Call Summaries", version="1.0")

class TranscriptEntry(BaseModel):
    timestamp: str
    speaker: str
    text: str

class CallMentions(BaseModel):
    longest_monologue: Optional[str] = None
    longest_customer_story: Optional[str] = None
    challenges: Optional[str] = None
    next_steps: Optional[str] = None

class CallSummaryRequest(BaseModel):
    call_id: str
    call_type: str
    call_status: str
    call_duration: str
    call_start_time: str
    call_end_time: str
    caller_number: Optional[str] = None
    caller_name: Optional[str] = None
    caller_title: Optional[str] = None
    caller_company: Optional[str] = None
    recipient_number: Optional[str] = None
    recipient_name: Optional[str] = None
    is_call_recorded: Optional[bool] = None
    transcript: List[Union[TranscriptEntry, str]]
    mentions: Optional[CallMentions] = None

class CallSummaryResponse(BaseModel):
    summary: str
    action_items: List[str]

def normalize_transcript(items: List[Union[TranscriptEntry, str]]) -> str:
    rows = []
    for it in items:
        if isinstance(it, str):
            rows.append(it)
        else:
            rows.append(f"{it.timestamp} - {it.speaker}: {it.text}")
    return "\n".join(rows)

@app.get("/healthz")
def healthz():
    return {"ok": True, "model": MODEL}

@app.post("/generate-call-summary", response_model=CallSummaryResponse)
def generate_call_summary(request: CallSummaryRequest):
    try:
        transcript_text = normalize_transcript(request.transcript)
        mentions_parts = []
        if request.mentions:
            if request.mentions.longest_monologue: mentions_parts.append(f"Longest Monologue: {request.mentions.longest_monologue}")
            if request.mentions.longest_customer_story: mentions_parts.append(f"Longest Customer Story: {request.mentions.longest_customer_story}")
            if request.mentions.challenges: mentions_parts.append(f"Challenges: {request.mentions.challenges}")
            if request.mentions.next_steps: mentions_parts.append(f"Next Steps: {request.mentions.next_steps}")
        mentions_text = "\n".join(mentions_parts)

        prompt = f"""
You are an expert in summarizing business calls. Use the format shown below.

Call:
Call ID: {request.call_id}
Call Type: {request.call_type}
Call Status: {request.call_status}
Call Duration: {request.call_duration}
Call Start Time: {request.call_start_time}
Call End Time: {request.call_end_time}
Caller Name: {request.caller_name}
Caller Title: {request.caller_title}
Caller Company: {request.caller_company}
Recipient Name: {request.recipient_name}
Is Call Recorded: {request.is_call_recorded}

Mentions:
{mentions_text if mentions_text else "None"}

Transcript:
{transcript_text}

Output format (follow exactly):
Summary:
<one concise paragraph>

Action Items:
- <first action>
- <second action>
"""
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL
        )
        text = resp.choices[0].message.content or ""
        sm = "Summary:"
        am = "Action Items:"
        if sm not in text or am not in text:
            raise ValueError("Model did not return required Summary/Action Items sections")

        summary = text.split(sm, 1)[1].split(am, 1)[0].strip()
        actions_raw = text.split(am, 1)[1].strip().splitlines()
        action_items = [a.lstrip("- ").strip() for a in actions_raw if a.strip()]
        return CallSummaryResponse(summary=summary, action_items=action_items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
