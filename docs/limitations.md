# Accuracy & Limitations

## Known Accuracy Limitations

### Embedding Model
- `all-MiniLM-L6-v2` is a 384-dimensional general-purpose encoder. It was not fine-tuned on resume/JD pairs.
- Semantic similarity scores are approximate. Two resumes mentioning the same skills in different contexts may score identically.
- Very short resumes (< 100 words) produce low-signal embeddings and may rank poorly even if qualified.

### LLM Scorer
- `Qwen2.5-0.5B-Instruct` is a small model. Larger models would produce more nuanced and accurate assessments.
- The model may hallucinate skill names or misidentify gaps if the resume is ambiguously worded.
- Truncation to 2500 characters means the model only sees roughly the first 400-600 words of longer resumes. Late-appearing skills or experience are invisible.
- JSON parsing relies on regex extraction. Malformed outputs fall back to a neutral score (50), introducing noise.

### Resume Parsing
- **PDF**: Only text-layer PDFs are supported. Scanned PDFs (image-based) return empty text and receive near-zero scores.
- **DOCX**: Tables, text boxes, and headers embedded in shapes may be missed by `python-docx`.
- **Excel**: Requires exact column names `Name` and `Resume_Text`. Variants like `resume_text` or `Candidate Name` will fail silently.

---

## System Limitations

### Scale
- ChromaDB runs as a local file store. Concurrent writes from multiple users are not safe without locking.
- LLM inference is synchronous and single-threaded. Scoring 10 candidates takes ~60-120 seconds on CPU.
- No caching: the same JD submitted twice will re-score all candidates.

### Session Management
- ChromaDB persists across server restarts. Uploaded resumes from a previous session remain until `/clear` is called.
- No authentication or user isolation — all users share the same resume pool.

### Frontend
- No progress indicator during LLM scoring (which can take 1-2 minutes). Users may think the app is frozen.
- No pagination for large result sets.

---

## What I Would Improve With More Time

| Priority | Improvement |
|---|---|
| High | Resume anonymization before LLM scoring (remove names, contact info) |
| High | Progress streaming via SSE or WebSocket during LLM scoring |
| High | OCR fallback for scanned PDFs (pytesseract) |
| Medium | Async LLM inference (background tasks, result polling) |
| Medium | Resume chunking: split by section, embed per chunk, re-rank by chunk similarity |
| Medium | JD parsing: pre-extract required/preferred skills from JD as a structured list |
| Medium | Persistent user sessions with resume pool isolation |
| Low | Upgrade to a 7B model with GPU for significantly better scoring accuracy |
| Low | Fine-tune embedding model on resume/JD pairs for domain-specific retrieval |
| Low | A/B test hybrid scoring weights (currently 40/60) against human-labeled ground truth |

---

## Assumptions

1. Uploaded PDFs contain extractable text (not scanned images).
2. Excel files follow the `Name` / `Resume_Text` column schema.
3. The local machine has at least 4GB RAM to load the default model.
4. First run requires internet access to download the HuggingFace model (~1GB).
5. All resumes are in English. Non-English text will score unpredictably.