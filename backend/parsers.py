import pdfplumber, docx, pandas as pd, io, os
from typing import List, Dict

def parse_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()

def parse_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([p.text for p in doc.paragraphs]).strip()

def parse_excel(file_bytes: bytes) -> List[Dict]:
    df = pd.read_excel(io.BytesIO(file_bytes))
    candidates = []
    for idx, row in df.iterrows():
        name = str(row.get("Name", f"Candidate_{idx}"))
        text = str(row.get("Resume_Text", row.get("Experience", "")))
        candidates.append({"id": f"exc_{idx}", "name": name, "text": text})
    return candidates

def parse_resume_file(filename: str, file_bytes: bytes) -> List[Dict]:
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return [{"id": filename, "name": filename, "text": parse_pdf(file_bytes)}]
    elif ext == ".docx":
        return [{"id": filename, "name": filename, "text": parse_docx(file_bytes)}]
    elif ext in [".xlsx", ".xls"]:
        return parse_excel(file_bytes)
    raise ValueError(f"Unsupported file type: {ext}")