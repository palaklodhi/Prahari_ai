"""Thin Google Gemini (Google AI Studio) client — augmentation layer only.

The platform's *verdicts* (risk scores, indicators, authenticity checks) always
come from the deterministic, auditable ML/rule engines. Gemini is an optional
layer that turns those structured verdicts into natural-language reasoning and
warm, multilingual conversational replies for the Citizen Fraud Shield.

Design goals:
  - No third-party SDK — uses the REST API over stdlib urllib, so it adds zero
    dependencies and works anywhere Python runs.
  - Graceful degradation — if no API key is configured or a call fails, callers
    fall back to the built-in responses. The product never breaks without a key.
  - Short timeouts so a slow LLM never blocks a fraud verdict.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional

from app.core.config import GEMINI_API_BASE, GEMINI_API_KEY, GEMINI_MODEL

_TIMEOUT = 12  # seconds — a fraud verdict must never hang on the LLM


def is_enabled() -> bool:
    """True when a Gemini API key has been supplied."""
    return bool(GEMINI_API_KEY)


def status() -> dict:
    return {
        "enabled": is_enabled(),
        "model": GEMINI_MODEL if is_enabled() else None,
        "provider": "Google Gemini (AI Studio)",
    }


def generate(
    prompt: str,
    system: Optional[str] = None,
    temperature: float = 0.4,
    max_tokens: int = 512,
    as_json: bool = False,
) -> Optional[str]:
    """Call Gemini generateContent. Returns the text, or None on any failure."""
    if not is_enabled():
        return None

    url = f"{GEMINI_API_BASE}/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    body: dict = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    if as_json:
        body["generationConfig"]["responseMimeType"] = "application/json"

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        candidates = payload.get("candidates") or []
        if not candidates:
            return None
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts).strip()
        return text or None
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, KeyError):
        return None
    except Exception:
        return None


def generate_json(prompt: str, system: Optional[str] = None) -> Optional[dict]:
    """Convenience wrapper that expects a JSON object back."""
    raw = generate(prompt, system=system, as_json=True, temperature=0.2)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return None
