# Architecture Overview

## System Diagram

```
┌─────────────────────────────────────────────────────┐
│                 Frontend (React + Vite)             │
│   FileUpload  │  JobDescription  │  ResultsTable    │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP (localhost:8000)
┌──────────────────────▼──────────────────────────────┐
│                  Backend (FastAPI)                  │
│                                                     │
│  POST /upload        POST /match      POST /clear   │
│       │                   │                         │
│  parsers.py         rag_pipeline.py                 │
│  (PDF/DOCX/XLS)     retrieve_top_k()                │
│       │                   │                         │
│       └─────► ChromaDB ◄──┘                         │
│             (local vector store)                    │
│                   │                                 │
│             llm_scorer.py                           │
│        (HuggingFace local model)                    │
│             score_candidates()                      │
└─────────────────────────────────────────────────────┘
```

---

## Component Responsibilities

### `parsers.py`
Handles multi-format resume ingestion:
- **PDF**: `pdfplumber` extracts text from text-based PDFs. Scanned/image PDFs return empty text.
- **DOCX**: `python-docx` extracts paragraph text.
- **Excel (.xlsx/.xls)**: `pandas` reads rows with `Name` and `Resume_Text` columns, enabling bulk candidate datasets from sources like Kaggle.

Returns a list of `{id, name, text}` dicts passed to the RAG pipeline.

---

### `rag_pipeline.py` — ResumeRAG
- Embeds resume text using `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional vectors).
- Persists embeddings in ChromaDB (`./chroma_db/`) using HNSW indexing.
- `retrieve_top_k(jd, k=10)` embeds the job description and returns the cosine-closest candidates with similarity scores.

---

### `llm_scorer.py`
- Loads `Qwen/Qwen2.5-0.5B-Instruct` locally via HuggingFace Transformers.
- Constructs a structured prompt for each candidate and enforces JSON output.
- Returns `{match_score, key_strengths, skill_gaps, reasoning}` per candidate.
- **Hybrid scoring formula**:
  ```
  final_score = (embedding_similarity × 40) + (llm_match_score × 0.6)
  ```

---

### `main.py`
FastAPI application with 3 endpoints:
- `/upload` — accepts `multipart/form-data`, calls parsers, upserts to ChromaDB.
- `/match` — accepts JD as form field, triggers RAG retrieval + LLM scoring, returns ranked list.
- `/clear` — deletes all ChromaDB records (session reset).

---

### Frontend (React + Vite)
- `FileUpload.jsx` — drag-and-drop multi-file upload posted to `/upload`.
- `JobDescription.jsx` — textarea that posts to `/match`.
- `ResultsTable.jsx` — renders ranked candidates with score, strengths, gaps, and reasoning.

---

## Data Flow

```
User uploads PDFs / Excel file
        ↓
parsers.py → [{id, name, text}, ...]
        ↓
SentenceTransformer embeds each resume text
        ↓
ChromaDB.upsert(ids, documents, embeddings)

User submits Job Description
        ↓
SentenceTransformer embeds JD
        ↓
ChromaDB.query(jd_embedding, k=10) → top 10 candidates
        ↓
For each candidate:
    LLM prompt → JSON {match_score, strengths, gaps, reasoning}
    final_score = similarity×40 + llm_score×0.6
        ↓
Sort by final_score DESC → return to frontend → render in table
```

---

## Scale-Out Considerations

| Bottleneck | Current State | Production Approach |
|---|---|---|
| Vector store | Local ChromaDB file | Hosted ChromaDB, Pinecone, Weaviate, or pgvector |
| LLM inference | Single-process CPU | vLLM or TGI behind a load balancer; or swap to OpenAI/Azure API |
| Concurrent requests | Single FastAPI worker | Gunicorn + multiple Uvicorn workers; async LLM calls |
| Resume parsing | Synchronous in-request | Background task queue (Celery + Redis) |
| Large datasets (10K+ resumes) | Sequential scan | Batch embed on upload; pagination on retrieval |

For enterprise deployment: containerize with Docker, deploy backend on Cloud Run or ECS, store vectors in a managed vector database, and replace the local LLM with a hosted inference endpoint.