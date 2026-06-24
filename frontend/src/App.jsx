import { useState } from "react";
const API_URL = "http://localhost:8000";

export default function App() {
  const [files, setFiles] = useState([]);
  const [jd, setJd] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [msg, setMsg] = useState("");
  const [uploaded, setUploaded] = useState(false); // ✅ Moved inside component

      const handleUpload = async () => {
    if (!files.length) return setMsg("⚠️ Select files first.");
    const formData = new FormData();
    files.forEach(f => formData.append("files", f));
    
    setLoading(true);
    setMsg("⏳ Uploading & parsing resumes...");
    try {
      const res = await fetch(`${API_URL}/upload`, { method: "POST", body: formData });
      
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Server returned ${res.status}`);
      }
      
      const data = await res.json();
      setMsg(`✅ Successfully uploaded ${data.count} resumes.`);
      setUploaded(true); // ✅ Only unlocks button on real success
    } catch (e) {
      console.error("Upload failed:", e);
      setMsg(`❌ Upload failed: ${e.message}`);
      setUploaded(false);
    } finally {
      setLoading(false);
    }
  };
    const handleClear = async () => {
    try {
      await fetch(`${API_URL}/clear`, { method: "POST" });
      setUploaded(false);
      setResults([]);
      setMsg("🗑️ Previous resumes cleared. Upload a new batch.");
    } catch (e) {
      setMsg("❌ Failed to clear database.");
    }
  };

  const handleMatch = async () => {
    if (!uploaded) return setMsg("⚠️ Please upload resumes first.");
    if (!jd.trim()) return setMsg("Enter a job description.");
    setLoading(true);
    const formData = new FormData();
    formData.append("job_description", jd);
    try {
      const res = await fetch(`${API_URL}/match`, { method: "POST", body: formData });
      const data = await res.json();
      setResults(data.candidates || []);
      setMsg(data.message || "Matching complete.");
    } catch (e) {
      setMsg("Matching failed.");
    } finally { setLoading(false); }
  };

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 20, fontFamily: "system-ui" }}>
      <h1>🤖 Intelligent Resume Screener</h1>
            <div style={{ marginBottom: 16, display: "flex", gap: 10, alignItems: "center" }}>
        <input type="file" multiple accept=".pdf,.docx,.xlsx,.xls" onChange={e => setFiles(Array.from(e.target.files))} />
        <button onClick={handleUpload} disabled={loading}>Upload Resumes</button>
        <button onClick={handleClear} disabled={loading} style={{ background: "#fee2e2", color: "#b91c1c" }}>
          🗑️ Clear Previous
        </button>
      </div>
      <textarea
        rows={6} style={{ width: "100%", padding: 8, marginBottom: 16 }}
        placeholder="Paste Job Description here..."
        value={jd} onChange={e => setJd(e.target.value)}
      />
            <button onClick={handleMatch} disabled={loading || !uploaded}>
        {loading ? "⏳ Scoring Candidates..." : "Find Best Matches"}
      </button>
      <p style={{ marginTop: 10, color: "#555" }}>{msg}</p>

      {results.length > 0 && (
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 20 }}>
          <thead>
            <tr style={{ background: "#f4f4f4" }}>
              <th style={{ border: "1px solid #ccc", padding: 8 }}>Rank</th>
              <th style={{ border: "1px solid #ccc", padding: 8 }}>Candidate</th>
              <th style={{ border: "1px solid #ccc", padding: 8 }}>Score</th>
              <th style={{ border: "1px solid #ccc", padding: 8 }}>Strengths</th>
              <th style={{ border: "1px solid #ccc", padding: 8 }}>Gaps</th>
              <th style={{ border: "1px solid #ccc", padding: 8 }}>Reasoning</th>
            </tr>
          </thead>
          <tbody>
            {results.map((c, i) => (
              <tr key={c.id}>
                <td style={{ border: "1px solid #ccc", padding: 8 }}>{i + 1}</td>
                <td style={{ border: "1px solid #ccc", padding: 8 }}>{c.name}</td>
                <td style={{ border: "1px solid #ccc", padding: 8, fontWeight: "bold" }}>{c.final_score}</td>
                <td style={{ border: "1px solid #ccc", padding: 8 }}>{c.strengths.join(", ")}</td>
                <td style={{ border: "1px solid #ccc", padding: 8 }}>{c.gaps.join(", ")}</td>
                <td style={{ border: "1px solid #ccc", padding: 8 }}>{c.reasoning}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}