"""Optional Groq-compatible hosted inference. Missing keys safely use retrieval only."""
from __future__ import annotations
import os
import requests

MAX_QUESTION_CHARS = 500
MAX_CONTEXT_CHARS = 5000
MAX_CALLS_PER_SESSION = 5

def get_config(secrets=None):
    secrets = secrets or {}
    key = secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    model = secrets.get("GROQ_MODEL") or os.getenv("GROQ_MODEL") or "openai/gpt-oss-20b"
    return key, model

def generate(question: str, context: str, api_key: str, model: str, timeout: int = 18) -> str:
    if not api_key:
        raise RuntimeError("API key is missing")
    question = question[:MAX_QUESTION_CHARS]
    context = context[:MAX_CONTEXT_CHARS]
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "temperature": 0.1, "max_tokens": 450,
              "messages": [
                  {"role": "system", "content": "Answer only from the provided published source excerpts. If insufficient, say so. Do not give legal, insurance, occupational-safety, or compliance advice; refer to a specialist. Never infer seminar details or provider."},
                  {"role": "user", "content": f"SOURCE EXCERPTS:\n{context}\n\nQUESTION:\n{question}"}
              ]}, timeout=timeout)
    if response.status_code == 429:
        raise RuntimeError("Free-tier rate limit reached. Try again later; no other provider will be used.")
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()
