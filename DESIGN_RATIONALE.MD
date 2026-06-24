# Design Rationale, Assumptions & Future Work

## Why These Technology Choices

### Local LLM — Qwen2.5-0.5B-Instruct
- Assignment requires no paid services or special infrastructure.
- 0.5B parameters fits comfortably in CPU RAM (~2GB peak usage).
- Strong instruction-following for its size; reliably produces JSON output with the right prompt structure.
- Swappable via the `LLM_MODEL` environment variable without any code changes.

### ChromaDB for Vector Storage
- Runs as a local persistent file store — zero infrastructure, no Docker, no cloud account needed.
- `PersistentClient` writes to disk so uploaded resumes survive server restarts across development sessions.
- HNSW index supports fast approximate nearest-neighbor search at this dataset scale.
- Production alternative: Pinecone, Weaviate, or pgvector with managed hosting for multi-user scale.

### SentenceTransformers — all-MiniLM-L6-v2
- Fastest general-purpose encoder available (~80ms per batch on CPU).
- Produces L2-normalized embeddings suitable for cosine similarity without additional normalization.
- No API key required. No internet calls after the initial model download.
- 384-dimensional vectors keep ChromaDB storage compact even for large resume corpora.

### FastAPI Backend
- Native async I/O with Uvicorn handles concurrent file uploads cleanly.
- Auto-generated OpenAPI docs at `/docs` allow easy manual endpoint testing during development.
- `python-multipart` enables clean multi-file form uploads matching the assignment requirement.
- CORS middleware configured permissively for local development (should be restricted to known origins in production).

### React + Vite Frontend
- Vite's hot module replacement makes UI iteration fast during development.
- Component split (FileUpload, JobDescription, ResultsTable) keeps concerns cleanly separated.
- No Redux or global state management — local state in App.jsx is sufficient for this scope and keeps the codebase simple and defensible in an interview.

### Hybrid Scoring (40% Embedding + 60% LLM)
- Embedding similarity provides a fast, deterministic pre-filter based on semantic overlap.
- LLM score adds contextual depth: role-level fit, skill gap identification, and reasoning.
- 60/40 weighting favors LLM judgment while the embedding score anchors results when LLM output is unreliable.
- Both scores are surfaced to the recruiter for full transparency.

---

## Assumptions Log

| # | Assumption |
|---|---|
| 1 | All uploaded PDFs have a selectable text layer (not scanned images). |
| 2 | Excel datasets use `Name` and `Resume_Text` as column headers after renaming from source. |
| 3 | At least 4GB system RAM is available for LLM loading. |
| 4 | First run has internet access for the HuggingFace model download (~1GB). |
| 5 | All resume content is in English. |
| 6 | The recruiter is the final decision maker — scores are advisory only. |
| 7 | All uploaded resume data is public, synthetic, or clearly de-identified. |

---

## What I Would Improve With More Time

**Highest priority:**
1. **Streaming progress feedback** — LLM scoring takes 1-2 minutes silently on CPU. Server-Sent Events or WebSocket progress updates are essential for real usability.
2. **Resume anonymization** — Strip candidate names and contact info before LLM scoring to reduce demographic bias risk in the scoring prompt.
3. **OCR fallback** — Handle scanned PDFs with `pytesseract` so image-based resumes are not silently dropped with a near-zero score.

**Medium priority:**
4. Async LLM inference with background tasks and a polling endpoint.
5. Resume chunking by section to avoid 2500-character truncation losing important experience.
6. Structured JD skill extraction before scoring to improve gap detection accuracy.

**Lower priority:**
7. Upgrade to a 7B model with GPU for significantly better scoring quality.
8. Fine-tune the embedding model on resume/JD pairs for domain-specific retrieval.
9. A/B test the 40/60 hybrid weighting against human-labeled ground truth to find the optimal split.