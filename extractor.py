import json
import logging
import time
import urllib.error
import urllib.request

import pdfplumber

# pdfminer logs FontBBox issues on WARNING for some PDFs; extraction still works.
for _name in (
    "pdfminer",
    "pdfminer.pdffont",
    "pdfminer.pdfinterp",
    "pdfminer.pdfpage",
    "pdfminer.pdfdocument",
    "pdfplumber",
):
    logging.getLogger(_name).setLevel(logging.ERROR)

from config import (
    OLLAMA_BASE_URL,
    OLLAMA_MAX_INPUT_CHARS,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
)
from prompts import PROMPT


def extract_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def _prepare_llm_text(text: str) -> str:
    if len(text) <= OLLAMA_MAX_INPUT_CHARS:
        return text
    return (
        text[:OLLAMA_MAX_INPUT_CHARS]
        + "\n\n[Document truncated: only the first "
        f"{OLLAMA_MAX_INPUT_CHARS:,} characters were sent.]\n"
    )


def _parse_json_from_llm(raw: str):
    raw = raw.strip()
    if "```" in raw:
        start = raw.find("```")
        rest = raw[start + 3 :]
        if rest.lstrip().startswith("json"):
            rest = rest.lstrip()[4:].lstrip()
        end = rest.rfind("```")
        if end != -1:
            raw = rest[:end]
        else:
            raw = rest
        raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        lo, hi = raw.find("{"), raw.rfind("}")
        if lo != -1 and hi != -1 and hi > lo:
            return json.loads(raw[lo : hi + 1])
        lo, hi = raw.find("["), raw.rfind("]")
        if lo != -1 and hi != -1 and hi > lo:
            return json.loads(raw[lo : hi + 1])
        raise


def _ollama_chat(messages):
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/chat"
    payload = json.dumps(
        {"model": OLLAMA_MODEL, "messages": messages, "stream": False}
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    preflight_url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/tags"
    try:
        with urllib.request.urlopen(preflight_url, timeout=5):
            pass
    except Exception as e:
        raise RuntimeError(
            f"Ollama preflight failed at {preflight_url}. "
            "Check if `ollama serve` is running and reachable."
        ) from e

    started = time.monotonic()
    print(
        f"[extractor] Requesting Ollama model={OLLAMA_MODEL!r}, "
        f"chars={len(messages[-1].get('content', '')):,}, timeout={OLLAMA_TIMEOUT}s"
    )
    try:
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except TimeoutError as e:
        elapsed = time.monotonic() - started
        raise RuntimeError(
            f"Ollama request timed out after {elapsed:.1f}s (configured timeout: {OLLAMA_TIMEOUT}s). "
            "Try: increase OLLAMA_TIMEOUT, decrease OLLAMA_MAX_INPUT_CHARS, "
            "use a smaller model (e.g. llama3.2:1b), or ensure GPU acceleration."
        ) from e
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        raise RuntimeError(
            f"Ollama HTTP {e.code} for model {OLLAMA_MODEL!r}: {err_body or e.reason}"
        ) from e
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"Could not reach Ollama at {OLLAMA_BASE_URL}. "
            f"Start the daemon and ensure the model is pulled. ({e})"
        ) from e
    content = (body.get("message") or {}).get("content")
    if not content:
        raise RuntimeError(f"Unexpected Ollama response: {body}")
    print(f"[extractor] Ollama response received in {time.monotonic() - started:.1f}s")
    return content


def extract_flows(text):
    raw = _ollama_chat(
        [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": _prepare_llm_text(text)},
        ]
    )
    data = _parse_json_from_llm(raw)
    if isinstance(data, dict) and "name" in data and "steps" in data:
        return [data]
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of flow objects")
    return data
