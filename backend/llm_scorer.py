import os, re, json, torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from typing import List, Dict

# Lightweight, CPU-friendly instruct model (~1GB, excellent JSON following)
MODEL_NAME = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")

print(f"🔄 Loading local LLM: {MODEL_NAME}... (first run downloads ~1GB, takes 1-2 mins)")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32,
    # device_map="auto",  # <-- Remove or comment out this line
    trust_remote_code=True
)
llm_pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=400,
    pad_token_id=tokenizer.eos_token_id
)

SCORING_PROMPT = """You are an expert technical recruiter. Evaluate the candidate resume against the job description.
Output ONLY a valid JSON object with this exact structure:
{{
  "match_score": <0-100 integer>,
  "key_strengths": ["skill1", "skill2"],
  "skill_gaps": ["missing1", "missing2"],
  "reasoning": "<2-3 sentence explanation>"
}}

Job Description:
{jd}

Candidate Resume:
{resume}
"""

def call_llm(prompt: str) -> str:
    messages = [{"role": "user", "content": prompt}]
    # Apply model-specific chat template automatically
    if hasattr(tokenizer, "apply_chat_template"):
        formatted = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    else:
        formatted = prompt

    output = llm_pipe(formatted, do_sample=False, temperature=0.1)
    generated = output[0]["generated_text"]
    
    # Strip echoed prompt if present
    if generated.startswith(formatted):
        generated = generated[len(formatted):]
    return generated.strip()

def parse_llm_json(raw: str) -> Dict:
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        return {"match_score": 50, "key_strengths": [], "skill_gaps": [], "reasoning": "LLM output parsing failed."}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"match_score": 50, "key_strengths": [], "skill_gaps": [], "reasoning": "Invalid JSON from LLM."}

def score_candidates(jd: str, candidates: List[Dict]) -> List[Dict]:
    scored = []
    for c in candidates:
        prompt = SCORING_PROMPT.format(jd=jd, resume=c["text"][:2500])
        raw = call_llm(prompt)
        llm_result = parse_llm_json(raw)
        
        # Hybrid scoring: 40% embedding similarity + 60% LLM semantic match
        final_score = round((c["similarity_score"] * 40) + (llm_result["match_score"] * 0.6))
        scored.append({
            **c,
            "llm_score": llm_result["match_score"],
            "final_score": min(final_score, 100),
            "strengths": llm_result["key_strengths"],
            "gaps": llm_result["skill_gaps"],
            "reasoning": llm_result["reasoning"]
        })
    return sorted(scored, key=lambda x: x["final_score"], reverse=True)