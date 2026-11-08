# n8n Workflows — AI Recruiter Agency

## 📁 Workflow Files

| File | Description | Trigger |
|------|-------------|---------|
| `01_main_recruitment_pipeline.json` | **Full pipeline** — Extractor → Enhancer → Analyzer → Matcher → Screener → Recommender | POST `/webhook/process-application` |
| `02_candidate_advisor_agent.json` | **Self-service** — Candidates upload resume and get career advice + optional email | POST `/webhook/candidate-advisor` |
| `03_batch_processing.json` | **Batch** — Process multiple resumes on a schedule, aggregates results | Manual / Daily Cron |

---

## 🚀 Import Instructions

1. Open your n8n instance
2. Go to **Workflows → Import from file**
3. Import each `.json` file
4. Set your Nebius API key (see below)
5. Activate

---

## 🔑 Setting the Nebius API Key

Each HTTP Request node that calls the LLM has a header:
```
Authorization: Bearer YOUR_NEBIUS_API_KEY
```

Replace `YOUR_NEBIUS_API_KEY` in all API Call nodes with your own Nebius key. Never commit the key.

**Recommended:** Use n8n **Credentials** → create a "Header Auth" credential and reference it in all HTTP Request nodes instead of hardcoding.

---

## 🔒 Before you activate

- Every webhook requires a **Header Auth** credential named `Webhook Header Auth`. Create it in n8n with a long random value, and send that header from your callers. Batch processing (`03`) already sends it. Without it, anyone who finds the URL can run the pipeline on your LLM key.
- The two email nodes (`02`, `07`) are **disabled**. If you enable them, they send to the address in the request, so keep the webhook authenticated and only accept addresses you have verified. The email body is HTML-escaped.

## 🔧 Webhook Endpoints

After importing and activating:

| Workflow | URL |
|----------|-----|
| Main Pipeline | `http://localhost:5678/webhook/process-application` |
| Candidate Advisor | `http://localhost:5678/webhook/candidate-advisor` |

---

## 📤 Request Payloads

### Main Pipeline
```json
{
  "resume_text": "John Doe\nSoftware Engineer\n...",
  "file_path": "/optional/path/to/resume.pdf",
  "candidate_id": "optional-custom-id"
}
```

### Candidate Advisor
```json
{
  "resume_text": "Jane Smith\nData Scientist\n...",
  "candidate_email": "jane@example.com"
}
```

---

## 🤖 Agent Pipeline Architecture

```
Webhook
  └─► Validate Input
        └─► [1] Extractor Agent       (LLM: parse resume → structured JSON)
              └─► [2] Profile Enhancer  (LLM: standardize & polish)
                    └─► [3] Analyzer     (LLM: skills, experience level, achievements)
                          └─► [4] Market Intelligence  (LLM: generate live job listings)
                                └─► Score & Merge Jobs (Code: DB + live scoring)
                                      └─► [5] Screener     (LLM: qualify & score candidate)
                                            └─► [6] Recommender  (LLM: final hiring decision)
                                                  └─► Respond to Webhook
```

---

## 🗄️ SQLite Database (optional for Matcher)

The original Python `MatcherAgent` queries a local SQLite DB (`jobs.sqlite`).
In n8n, you can add an **SQLite node** to the main pipeline to query your jobs DB.
The `03_batch_processing.json` workflow calls the main pipeline webhook which handles this internally.

---

## 🛠️ LLM Model

Default: `google/gemma-2-9b-it-fast` via [Nebius AI Studio](https://studio.nebius.ai)  
The API is OpenAI-compatible — you can swap to any OpenAI-compatible endpoint by changing the URL in HTTP Request nodes.

| Node | Temperature |
|------|-------------|
| Extractor | 0.3 (precise) |
| Enhancer | 0.4 |
| Analyzer | 0.3 (precise) |
| Market Intelligence | 0.6 (creative) |
| Screener | 0.4 |
| Recommender | 0.5 |
