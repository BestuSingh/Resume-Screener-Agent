# Resume Screener Agent

Production-ready Python starter for screening multiple resumes against a job description with Gemini:

- FastAPI API layer
- LangGraph workflow
- Gemini chat generation
- Gemini embeddings
- Chroma vector database by default
- Optional Pinecone backend
- PDF and text resume ingestion
- Structured JSON scoring and explanations

## Project layout

```text
resume_screener/
|-- app/
|   |-- main.py
|   |-- agent.py
|   |-- retriever.py
|   |-- evaluator.py
|   |-- embeddings.py
|   |-- parser.py
|   |-- schemas.py
|-- db/
|-- samples/
|-- scripts/
|-- requirements.txt
|-- .env
|-- README.md
```

## Setup

From the workspace root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r resume_screener\requirements.txt
```

Edit `resume_screener\.env` and set:

```env
GEMINI_API_KEY=your-gemini-api-key-here
```

The default Gemini models are:

```env
GEMINI_CHAT_MODEL=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_EMBEDDING_DIMENSIONALITY=768
```

## Run the API

```powershell
uvicorn resume_screener.app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## Screen resumes

JSON endpoint:

```powershell
$body = @{
  job_description = Get-Content resume_screener\samples\job_description.txt -Raw
  resumes = @(
    "resume_screener\samples\resume_alex_morgan.txt",
    "resume_screener\samples\resume_jamie_lee.txt"
  )
  top_k = 4
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/screen `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

Multipart upload endpoint:

```powershell
curl.exe -X POST http://127.0.0.1:8000/screen/upload `
  -F "job_description=<resume_screener/samples/job_description.txt" `
  -F "files=@resume_screener/samples/resume_alex_morgan.txt" `
  -F "files=@resume_screener/samples/resume_jamie_lee.txt"
```

Direct agent smoke test:

```powershell
python resume_screener\scripts\test_agent.py
```

API smoke test after the server is running:

```powershell
python resume_screener\scripts\test_api.py
```

## Response shape

The API returns:

```json
{
  "collection_name": "screening_...",
  "requirements": {
    "skills": [],
    "experience_years": 5,
    "keywords": [],
    "responsibilities": [],
    "seniority": "Senior"
  },
  "evaluations": [
    {
      "candidate_name": "Alex Morgan",
      "scores": {
        "skill_match": 9,
        "experience_match": 9,
        "keyword_match": 85,
        "overall_score": 88.5
      },
      "strengths": [],
      "weaknesses": [],
      "recommendation": "Accept",
      "source": "...",
      "candidate_id": "cand_..."
    }
  ],
  "errors": []
}
```

## How it works

1. `parser.py` parses PDF, TXT, or inline text resumes, cleans text, extracts basic metadata, and chunks text at about 500 tokens.
2. `embeddings.py` creates Gemini embeddings using `GEMINI_API_KEY`.
3. `retriever.py` stores chunks in Chroma and retrieves top-k relevant chunks per candidate using cosine distance.
4. `agent.py` runs a LangGraph workflow:
   - Input Node
   - Resume Retriever Node
   - Evaluation Node
   - Scoring Node
   - Output Formatter Node
5. `evaluator.py` extracts job requirements and asks Gemini for structured candidate evaluation.

## Switching from Chroma to Pinecone

Chroma is the default and persists locally under `resume_screener/db/chroma`.

To use Pinecone:

1. Create a Pinecone index whose dimension matches `GEMINI_EMBEDDING_DIMENSIONALITY`.
2. Set these in `resume_screener\.env`:

```env
VECTOR_DB_PROVIDER=pinecone
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=your-index-name
PINECONE_NAMESPACE_PREFIX=resume-screener
```

No code changes are required.

## Optional Streamlit UI

```powershell
streamlit run resume_screener\app\streamlit_app.py
```

## Gemini notes

This project uses the official `google-genai` SDK. Google docs assume `GEMINI_API_KEY` is set in the environment; this app loads it from `resume_screener\.env` via `pydantic-settings`.

Useful references:

- Gemini API quickstart: https://ai.google.dev/gemini-api/docs/quickstart
- Gemini API libraries: https://ai.google.dev/gemini-api/docs/libraries
- Gemini embeddings: https://ai.google.dev/gemini-api/docs/embeddings

## Notes for production

- Keep `.env` out of source control and use a secret manager in deployed environments.
- Restrict CORS origins in `app/main.py` before internet exposure.
- Add authentication for API access.
- Use a durable shared vector DB for horizontally scaled deployments.
- Add human review for hiring decisions. The model output should support, not replace, recruiter judgment.
