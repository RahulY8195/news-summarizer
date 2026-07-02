import os

import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")

REFUSAL_PHRASES = ["i can't", "i cannot", "i'm sorry", "i am sorry"]


def _generate(prompt: str) -> str:
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


def _generate_with_retry(prompt: str, fallback: str) -> str:
    result = _generate(prompt)
    if _is_refusal(result):
        result = _generate(prompt)
    if _is_refusal(result):
        return fallback
    return result


def summarize(text: str) -> str:
    prompt = (
        "You are summarizing a snippet from a real, already-published news "
        "article for a news aggregator app. The snippet below is public "
        "information, not a request to verify or fact-check anything. "
        "Just summarize what the snippet says in 2-3 plain, factual "
        "sentences. Do not refuse or add disclaimers.\n\n"
        f"Snippet:\n{text}\n\nSummary:"
    )
    return _generate_with_retry(prompt, fallback=text)


def summarize_story(texts: list[str], sources: list[str]) -> str:
    """Synthesize one summary from multiple sources covering the same story."""
    if len(texts) == 1:
        return summarize(texts[0])

    numbered = "\n\n".join(
        f"Source {i + 1} ({source}):\n{text}"
        for i, (text, source) in enumerate(zip(texts, sources))
    )
    prompt = (
        "The snippets below are public excerpts from different news outlets "
        "covering the same real, already-published story. This is not a "
        "request to verify or fact-check anything. Synthesize them into a "
        "single neutral 3-4 sentence summary that reflects points shared "
        "across sources, and briefly note any point where sources disagree. "
        "Do not refuse or add disclaimers.\n\n"
        f"{numbered}\n\nSynthesized summary:"
    )
    return _generate_with_retry(prompt, fallback=texts[0])
