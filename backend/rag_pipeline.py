import os
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import uuid

class ResumeRAG:
    def __init__(self, persist_dir: str = "./chroma_db"):
        if persist_dir is None:
            persist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(name="resumes")

    def add_resumes(self, resumes: List[Dict]):
        ids, documents, metadatas = [], [], []
        for r in resumes:
            cid = r.get("id", str(uuid.uuid4()))
            ids.append(cid)
            documents.append(r["text"])
            metadatas.append({"name": r.get("name", cid), "source": r.get("id", cid)})
        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    def retrieve_top_k(self, job_description: str, k: int = 10) -> List[Dict]:
        jd_emb = self.embedder.encode([job_description]).tolist()
        results = self.collection.query(
            query_embeddings=jd_emb, n_results=k,
            include=["metadatas", "documents", "distances"]
        )
        candidates = []
        for i in range(len(results["ids"][0])):
            candidates.append({
                "id": results["ids"][0][i],
                "name": results["metadatas"][0][i]["name"],
                "text": results["documents"][0][i],
                "similarity_score": max(0.0, 1.0 - results["distances"][0][i])
            })
        return candidates