# Prompt Design

## Core Scoring Prompt

```
You are an expert technical recruiter. Evaluate the candidate resume against the job description.
Output ONLY a valid JSON object with this exact structure:
{
  "match_score": <0-100 integer>,
  "key_strengths": ["skill1", "skill2"],
  "skill_gaps": ["missing1", "missing2"],
  "reasoning": "<2-3 sentence explanation>"
}

Job Description:
{jd}

Candidate Resume:
{resume}
```

---

## Design Rationale

### Persona Priming
Opening with "You are an expert technical recruiter" grounds the model in a specific role. This reduces generic output and aligns the model's evaluation lens with professional hiring criteria.

### Strict JSON Enforcement
Requiring JSON-only output with a rigid schema serves two purposes:
1. **Reliable parsing** — `re.search(r'\{.*\}', raw, re.DOTALL)` extracts the JSON block even if the model adds preamble text. `json.loads()` is then applied deterministically.
2. **Structured UX** — The frontend renders strengths, gaps, and reasoning as distinct UI elements rather than unstructured text.

Fallback values are returned if parsing fails:
```python
{
  "match_score": 50,
  "key_strengths": [],
  "skill_gaps": [],
  "reasoning": "LLM output parsing failed."
}
```

### Resume Truncation to 2500 Characters
Resumes are capped at 2500 characters before injection into the prompt:
```python
prompt = SCORING_PROMPT.format(jd=jd, resume=c["text"][:2500])
```
This keeps each inference call within the model's 4096-token context window and controls latency on CPU. Tradeoff: very long resumes lose tail content. Future fix: chunk and summarize first.

### Temperature = 0 (Greedy Decoding)
`do_sample=False` ensures deterministic output. For a scoring tool, consistency matters more than diversity — the same resume against the same JD should produce the same score on every run, which also supports audit requirements.

### Hybrid Scoring Formula
```
final_score = (embedding_similarity × 40) + (llm_match_score × 0.6)
```
- Embedding similarity catches broad keyword and topic overlap quickly.
- LLM match score adds semantic depth: role-level fit, missing skills, and contextual understanding.
- 60/40 weighting favors LLM judgment while embedding acts as a fast pre-filter.

---

## AI Interaction Improvements Implemented

### 1. Chat Template Application
The model's built-in chat template is applied before generation:
```python
if hasattr(tokenizer, "apply_chat_template"):
    formatted = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
```
This ensures the model receives input in the exact format it was fine-tuned on, significantly improving instruction-following and JSON output reliability compared to raw prompt injection.

### 2. Prompt Echo Stripping
Raw output may echo the input prompt. Stripping it prevents double-counting and parsing errors:
```python
if generated.startswith(formatted):
    generated = generated[len(formatted):]
```

### 3. Regex-First JSON Extraction
Rather than assuming pure JSON output, a regex first locates the JSON block in the raw string. This handles models that prepend explanatory text before the JSON object.

### 4. Hybrid Scoring (Embedding + LLM)
Combining two independent signals reduces single-model failure risk. If the LLM produces a bad score due to truncation or hallucination, the embedding score anchors the result to something meaningful.

---

## Future Prompt Improvements

- **Chain-of-thought before scoring**: Ask the model to reason step by step, then output JSON. Improves accuracy on nuanced role-level fit assessments.
- **Skill taxonomy injection**: Pre-extract required skills from the JD and pass them as a structured list, reducing ambiguity in gap detection.
- **Resume chunking + summarization**: For long resumes, chunk by section, summarize each chunk, then score the combined summary. Avoids truncation data loss.
- **Few-shot examples**: Add 1-2 in-context scored examples to improve JSON format compliance with weaker or smaller models.