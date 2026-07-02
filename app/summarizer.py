import os

import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")

REFUSAL_PHRASES = ["i can't", "i cannot", "i'm sorry", "i am sorry"]


def _call_model(text: str) -> str:
    prompt = (
        "You are summarizing a snippet from a real, already-published news "
        "article for a news aggregator app. The snippet below is public "
        "information, not a request to verify or fact-check anything. "
        "Just summarize what the snippet says in 2-3 plain, factual "
        "sentences. Do not refuse or add disclaimers.\n\n"
        f"Snippet:\n{text}\n\nSummary:"
    )
    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["response"].strip()


def _is_refusal(response: str) -> bool:
    lowered = response.lower()
    return any(phrase in lowered for phrase in REFUSAL_PHRASES)


def summarize(text: str) -> str:
    result = _call_model(text)
    if _is_refusal(result):
        result = _call_model(text)
    if _is_refusal(result):
        return text
    return result
