from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from groq import Groq
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set")
MODEL = os.getenv("GROQ_MODEL_EMAIL", "llama3-70b-8192")

client = Groq(api_key=GROQ_API_KEY)
app = FastAPI(title="Email Composer", version="1.0")

class PreviousEmail(BaseModel):
    subject: str
    body: str

class EmailRequest(BaseModel):
    recipient_first_name: str
    recipient_last_name: str
    recipient_email: str
    template_type: str
    recipient_id: str
    recipient_phone: str
    recipient_company: str
    recipient_industry: str
    recipient_title: str
    recipient_address: str
    sender_id: str
    sender_email: str
    sender_first_name: str
    sender_last_name: str
    sender_phone: str
    sender_company: str
    sender_industry: str
    sender_title: str
    sender_address: str
    previous_emails: Optional[List[PreviousEmail]] = Field(default_factory=list)

class EmailResponse(BaseModel):
    subject: str
    body: str

TEMPLATES: Dict[str, str] = {
    "introduce": "Introduce the company and its offerings.",
    "nudge": "Follow up on the previous email and offer more details.",
    "checkin": "Check if the client is still interested and address challenges.",
    "reignite": "Thank the recipient and reignite the conversation.",
    "invite": "Invite the recipient to a meeting for opportunities or collaboration.",
    "prompt": "Write the email exactly per the user's purpose described above."
}

def create_email_prompt(data: EmailRequest) -> str:
    prev = "\n\n".join(
        [f"Previous Email {i+1}:\nSubject: {e.subject}\nBody: {e.body}" for i, e in enumerate(data.previous_emails)]
    )
    description = TEMPLATES.get(data.template_type, "General professional email.")
    return f"""
You are a professional email assistant. Generate a professional email.

Template Type: {data.template_type}
Description: {description}

Recipient:
First Name: {data.recipient_first_name}
Last Name: {data.recipient_last_name}
Email: {data.recipient_email}
Company: {data.recipient_company}
Industry: {data.recipient_industry}
Title: {data.recipient_title}
Address: {data.recipient_address}
Phone: {data.recipient_phone}

Sender:
First Name: {data.sender_first_name}
Last Name: {data.sender_last_name}
Email: {data.sender_email}
Company: {data.sender_company}
Industry: {data.sender_industry}
Title: {data.sender_title}
Address: {data.sender_address}
Phone: {data.sender_phone}

Previous Emails Context:
{prev if prev else "None"}

Output format:
Subject: <one line subject>
Body:
<email body with paragraphs>
"""

@app.get("/healthz")
def healthz():
    return {"ok": True, "model": MODEL}

@app.post("/generate-email", response_model=EmailResponse)
def generate_email(request: EmailRequest):
    try:
        prompt = create_email_prompt(request)
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL
        )
        text = resp.choices[0].message.content or ""
        subject_marker = "Subject:"
        body_marker = "Body:"
        if subject_marker not in text or body_marker not in text:
            raise ValueError("Model did not follow the required Subject/Body format")

        subject = text.split(subject_marker, 1)[1].split("\n", 1)[0].strip()
        body = text.split(body_marker, 1)[1].strip()
        return EmailResponse(subject=subject, body=body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
