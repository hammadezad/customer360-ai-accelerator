# Royal Cyber – Salesforce Einstein GPT Suite

**AI-powered Salesforce add-on with containerized services for email generation, call summaries, and opportunities/cases insights.**  

This project demonstrates how Royal Cyber integrates **Salesforce Einstein GPT** with **open-source LLMs (Llama3, Mistral, Mixtral)** to reduce operational costs, enhance data privacy, and enable full customization for enterprise needs.  

---

## 🚀 Features

### 1. Email Composer  
- Automated, personalized **sales email generation**.  
- Prompt types: **Introduce, Nudge, Check-in, Reignite, Invite**.  
- Uses Llama3/Mistral models for tailored communication.  

### 2. Call Summaries  
- AI-generated **summaries and action items** from call transcripts.  
- Supports structured and unstructured transcript inputs.  
- Ensures critical call insights are never lost.  

### 3. Opportunities & Cases Insights  
- AI-driven **sentiment analysis**, **objection handling**, and **next best action** for Salesforce records.  
- Helps sales teams prioritize, respond faster, and close more deals.  

---

## 📂 Project Structure

```
contact-center-suite/
│
├── email-composer/       # Service 1: Email generation
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── call-summaries/       # Service 2: Call summaries
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── sales-insights/       # Service 3: Opportunities & cases
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── .env                  # Environment variables (not committed to git)
└── docker-compose.yml    # Multi-service orchestration
```

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/your-username/rc-einstein-gpt-suite.git
cd rc-einstein-gpt-suite
```

### 2. Create a `.env` file
```ini
GROQ_API_KEY=put_your_key_here
GROQ_MODEL_EMAIL=llama3-70b-8192
GROQ_MODEL_CALLS=llama3-70b-8192
GROQ_MODEL_SALES=llama3-8b-8192
```

> ⚠️ Do **not** commit `.env` to GitHub. Add it to `.gitignore`.

### 3. Run with Docker Compose
```bash
docker compose up --build
```

### 4. Access services
- Email Composer → [http://localhost:8001/docs](http://localhost:8001/docs)  
- Call Summaries → [http://localhost:8002/docs](http://localhost:8002/docs)  
- Sales Insights → [http://localhost:8003/docs](http://localhost:8003/docs)  

---

## 🧪 Example Requests

### Email Composer
```bash
curl -X POST http://localhost:8001/generate-email \
-H "Content-Type: application/json" \
-d '{
  "recipient_first_name":"Sara",
  "recipient_last_name":"Becker",
  "recipient_email":"sara@example.com",
  "template_type":"introduce",
  "recipient_id":"r-1",
  "recipient_phone":"+49 111",
  "recipient_company":"Acme GmbH",
  "recipient_industry":"Retail",
  "recipient_title":"Head of Ops",
  "recipient_address":"Berlin",
  "sender_id":"s-1",
  "sender_email":"me@example.com",
  "sender_first_name":"Hammad",
  "sender_last_name":"Ezad",
  "sender_phone":"+92 333",
  "sender_company":"Royal Cyber",
  "sender_industry":"Tech",
  "sender_title":"Senior Data Scientist",
  "sender_address":"Sahiwal"
}'
```

### Call Summaries
```bash
curl -X POST http://localhost:8002/generate-call-summary \
-H "Content-Type: application/json" \
-d '{
  "call_id":"c-101",
  "call_type":"demo",
  "call_status":"completed",
  "call_duration":"31:12",
  "call_start_time":"2025-08-18T10:00:00Z",
  "call_end_time":"2025-08-18T10:31:12Z",
  "caller_name":"Hammad",
  "caller_title":"Senior DS",
  "caller_company":"Royal Cyber",
  "recipient_name":"Client A",
  "is_call_recorded":true,
  "transcript":[
    {"timestamp":"00:10","speaker":"Hammad","text":"Welcome and agenda."},
    "00:45 - Client: We need OCR accuracy > 99%."
  ],
  "mentions":{
    "challenges":"OCR layout variance",
    "next_steps":"POC on 10 invoices"
  }
}'
```

---

## 📊 Why This Matters
- **Lower Costs**: Leverages open-source LLMs vs expensive SaaS models.  
- **Data Privacy**: Keep customer data internal, aligned with compliance.  
- **Customization**: Fine-tune prompts and workflows to match business needs.  
- **Productivity**: Save hours of manual drafting, summarization, and analysis.  

---

## 📜 License
© 2025 Royal Cyber Inc. All rights reserved.  
