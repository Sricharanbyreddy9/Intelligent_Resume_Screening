# Responsible AI & Governance

## Explainability

Every ranked candidate includes human-readable justification:
- **key_strengths** — Skills explicitly matched between the resume and the job description.
- **skill_gaps** — Skills required by the JD but absent from the resume.
- **reasoning** — 2-3 sentence natural language explanation of the match score.
- **similarity_score** — Raw embedding cosine similarity, displayed alongside the LLM score for full transparency.

Recruiters can inspect both the automated score and its rationale before making any decision. The system is explicitly designed as a **decision-support tool**, not an autonomous hiring decision maker. No candidate is rejected or shortlisted without human review.

---

## Risk Discussion

### Risk 1: Incorrect Answers
The LLM may hallucinate skill names, misidentify gaps, or produce scores inconsistent with the resume content — especially for short or ambiguously worded resumes. The hybrid scoring formula (embedding + LLM) reduces but does not eliminate this risk. Fallback neutral scores (50) are assigned when output parsing fails, and the reasoning field flags this to the recruiter.

### Risk 2: Over-Reliance on AI
Recruiters may treat the ranked list as a final shortlist rather than a starting point. The UI should make clear that scores are AI-generated estimates. A candidate ranked 60 may outperform one ranked 85 in an interview. The system surfaces reasoning to encourage critical reading, not blind acceptance.

### Risk 3: UX Limitations
- LLM scoring takes 60-120 seconds for 10 candidates on CPU with no visible progress indicator. Users may think the application has frozen.
- Very long resumes are silently truncated to 2500 characters. Skills appearing late in a resume may be missed without any notification to the user.
- Scanned PDFs return empty text and receive near-zero scores without explaining why to the user.

---

## Bias Risks and Mitigations

### Identified Risks

| Risk | Description |
|---|---|
| Training data bias | LLM and embedding model trained on internet text may encode demographic, gender, or name-based associations. |
| Resume format bias | Keyword-dense resumes score higher on embeddings, disadvantaging concise or non-traditional formats. |
| Job description bias | Biased JD language propagates directly to scores. |
| Recency bias | Models may favor recent technologies over equivalent older skills with different naming. |

### Mitigations Applied
- **Score-only output**: The LLM is prompted for skill assessment only. Names and contact info are stored as metadata and are not injected into the scoring prompt.
- **Human-in-the-loop**: The UI presents ranked results for recruiter review. No automated rejection or shortlisting occurs.
- **Multi-signal scoring**: Combining embedding similarity and LLM score reduces dependence on any single model's biases.
- **Fallback handling**: Parsing failures produce a neutral score (50) rather than a zero that would unfairly eliminate candidates.

### Mitigations Recommended for Production
- Audit scores across demographic proxies (candidate name, school name) using a labeled test dataset.
- Anonymize names and contact fields before passing resume text to the LLM.
- Log all scoring decisions with timestamps for post-hoc audit trails.
- Establish a human review threshold: any candidate within 10 points of the cutoff should be flagged for manual review regardless of rank.

---

## Accuracy Controls

- **Hybrid scoring** reduces single-point failure risk across embedding and LLM signals.
- **Deterministic inference** (`temperature=0`) ensures reproducible scores for audit purposes.
- **Fallback values** are defined for all LLM parsing failures.
- **Top-10 retrieval** from ChromaDB ensures the LLM only scores genuinely relevant candidates, not the full corpus.

---

## Governance Checklist

- [x] No PHI or confidential data used
- [x] Public / synthetic dataset only (Kaggle Resume Dataset)
- [x] All inference local — no resume data sent to third parties
- [x] Scores accompanied by human-readable reasoning
- [x] Fallback values defined for parsing failures
- [x] Human review required before any hiring action
- [x] Deterministic scoring for reproducibility
- [ ] Demographic bias audit (recommended for production)
- [ ] Resume anonymization pipeline (recommended for production)
- [ ] Persistent audit log (recommended for production)