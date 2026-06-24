# Intelligent Resume Screening & Hiring System

A full-stack AI application that evaluates multiple resumes against a job description and ranks candidates using RAG + LLM-based semantic scoring.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- No paid services required — fully local LLM via HuggingFace

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # Edit if using a different model
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open the URL shown in the terminal (default: http://localhost:5173)

---

## ⚙️ Configuration

### LLM Model
Set `LLM_MODEL` in `backend/.env` to swap the local model:

```
LLM_MODEL=Qwen/Qwen2.5-0.5B-Instruct
```

Default is `Qwen/Qwen2.5-0.5B-Instruct` — ~1GB download on first run, CPU-friendly.

Alternative options:
| Model | Size | Notes |
|---|---|---|
| `Qwen/Qwen2.5-0.5B-Instruct` | ~1GB | Default, fast |
| `microsoft/Phi-3-mini-4k-instruct` | ~2.3GB | Higher quality |
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | ~600MB | Very fast |

### Embedding Model
Embeddings use `all-MiniLM-L6-v2` (SentenceTransformers) — no configuration needed.

---

## 📁 Project Structure

```
intelligent-resume-screener/
├── backend/
│   ├── main.py           # FastAPI app — /upload, /match, /clear endpoints
│   ├── parsers.py        # PDF, DOCX, Excel resume parsers
│   ├── rag_pipeline.py   # ChromaDB vector store + embedding retrieval
│   ├── llm_scorer.py     # Local HuggingFace LLM scoring
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   ├── JobDescription.jsx
│   │   │   └── ResultsTable.jsx
│   │   └── main.jsx
│   └── package.json
└── docs/
    ├── architecture.md
    ├── prompt_design.md
    ├── responsible_ai.md
    └── limitations.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/upload` | Upload one or more resume files (PDF/DOCX/XLSX) |
| POST | `/match` | Submit JD text; returns ranked candidates |
| POST | `/clear` | Clear all resumes from the vector store |

---

## 📊 Supported Input Formats

| Format | How it's parsed |
|---|---|
| PDF | `pdfplumber` — extracts text layer |
| DOCX | `python-docx` — extracts paragraphs |
| Excel | `pandas` — reads `Name` + `Resume_Text` columns |

---

## 🧠 How It Works

1. **Upload** — Resumes are parsed, embedded with `all-MiniLM-L6-v2`, and stored in ChromaDB.
2. **Match** — Job description is embedded; top-10 semantically similar resumes are retrieved.
3. **Score** — Local LLM evaluates each resume against the JD and returns a structured JSON score.
4. **Rank** — Final score = 40% embedding similarity + 60% LLM match score.

See `docs/architecture.md` for diagrams and deeper detail.

---

## 📝 Documentation

| Doc | Contents |
|---|---|
| [Architecture](docs/architecture.md) | System design, data flow, scale-out |
| [Prompt Design](docs/prompt_design.md) | LLM prompt rationale, JSON enforcement, improvements |
| [Responsible AI](docs/responsible_ai.md) | Bias, explainability, governance |
| [Limitations](docs/limitations.md) | Known gaps, accuracy notes, future work |

---

## 🔒 Data & Privacy

- No external API calls. All inference runs locally.
- Resume data stored in local ChromaDB (`backend/chroma_db/`). Not persisted beyond your machine.
- Do not upload PHI or confidential data per assignment rules.
