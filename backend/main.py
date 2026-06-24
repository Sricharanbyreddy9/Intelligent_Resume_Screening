from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from parsers import parse_resume_file
from rag_pipeline import ResumeRAG
from llm_scorer import score_candidates
import os

app = FastAPI(title="Intelligent Resume Screener")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

rag = ResumeRAG()

@app.post("/upload")
async def upload_resumes(files: list[UploadFile] = File(...)):
    print(f"📥 Received {len(files)} file(s) for upload")
    if not files:
        raise HTTPException(400, "No files provided")
    
    all_resumes = []
    for f in files:
        content = await f.read()
        try:
            parsed = parse_resume_file(f.filename, content)
            all_resumes.extend(parsed)
        except Exception as e:
            print(f"⚠️ Parse failed for {f.filename}: {e}")
            continue
            
    if not all_resumes:
        raise HTTPException(400, "No valid resumes extracted. Ensure PDFs are text-based or Excel has 'Name' & 'Resume_Text' columns.")
        
    rag.add_resumes(all_resumes)
    print(f"✅ Successfully added {len(all_resumes)} resumes to ChromaDB")
    return {"status": "success", "count": len(all_resumes)}

@app.post("/clear")
async def clear_database():
    existing = rag.collection.get()
    if existing["ids"]:
        rag.collection.delete(ids=existing["ids"])
    return {"status": "success", "message": "All previous resumes cleared."}

@app.post("/match")
async def match_candidates(job_description: str = Form(...)):
    if not job_description.strip():
        raise HTTPException(400, "Job description cannot be empty")
    top_candidates = rag.retrieve_top_k(job_description, k=10)
    if not top_candidates:
        return {"candidates": [], "message": "No resumes uploaded yet."}
    ranked = score_candidates(job_description, top_candidates)
    return {"candidates": ranked}