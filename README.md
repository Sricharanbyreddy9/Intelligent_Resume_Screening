# Intelligent Resume Screening & Hiring System

## 🚀 Quick Start
### Prerequisites
- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com) installed & running (`ollama pull llama3.2:3b`)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit if using remote LLM
uvicorn main:app --reload --port 8000