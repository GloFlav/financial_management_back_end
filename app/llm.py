"""Multi-provider LLM fallback router.
Priority order: OpenAI keys → Anthropic keys → Gemini
"""
import os
import json
from typing import Any
import httpx


# ── Key helpers ───────────────────────────────────────────────────────

def _openai_keys() -> list[str]:
    keys = []
    for k in ("OPENAI_API_KEY_1", "OPENAI_API_KEY_2", "OPENAI_API_KEY"):
        v = os.getenv(k, "").strip()
        if v and v not in keys:
            keys.append(v)
    return keys


def _anthropic_keys() -> list[str]:
    keys = []
    for k in ("ANTHROPIC_API_KEY_1", "ANTHROPIC_API_KEY_2"):
        v = os.getenv(k, "").strip()
        if v and v not in keys:
            keys.append(v)
    return keys


def _gemini_key() -> str:
    return os.getenv("GEMINI_API_KEY", "").strip()


# ── Provider callers ──────────────────────────────────────────────────

def _call_openai(key: str, messages: list, max_tokens: int, temperature: float) -> str:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    resp = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": model, "messages": messages,
            "temperature": temperature, "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},  # force JSON
        },
        timeout=20.0,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _call_anthropic(key: str, messages: list, max_tokens: int, temperature: float) -> str:
    model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    user_msgs = [m for m in messages if m["role"] != "system"]
    # Prefill assistant avec "{" pour forcer la réponse JSON
    prefill_msgs = user_msgs + [{"role": "assistant", "content": "{"}]
    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "system": system,
            "messages": prefill_msgs,
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
        timeout=20.0,
    )
    resp.raise_for_status()
    # Le prefill "{" est déjà inclus — on le rajoute devant la continuation
    return "{" + resp.json()["content"][0]["text"].strip()


def _call_gemini(key: str, messages: list, max_tokens: int, temperature: float) -> str:
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    contents: list[dict[str, Any]] = []
    system_parts: list[dict[str, Any]] = []
    for m in messages:
        if m["role"] == "system":
            system_parts.append({"text": m["content"]})
        elif m["role"] == "user":
            contents.append({"role": "user", "parts": [{"text": m["content"]}]})
        elif m["role"] == "assistant":
            contents.append({"role": "model", "parts": [{"text": m["content"]}]})

    payload: dict[str, Any] = {
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
            "responseMimeType": "application/json",  # force JSON
        },
    }
    if system_parts:
        payload["system_instruction"] = {"parts": system_parts}

    resp = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=20.0,
    )
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


# ── Clean JSON helpers ────────────────────────────────────────────────

def _clean_json(content: str) -> str:
    """Extract the first valid JSON object from LLM output."""
    content = content.strip()
    # Strip markdown fences
    if content.startswith("```"):
        lines = content.splitlines()
        lines = lines[1:]  # drop opening fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines).strip()
    # Find first { and last } to extract JSON even with surrounding text
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
        content = content[start:end + 1]
    return content


# ── Public API ────────────────────────────────────────────────────────

def call_llm(messages: list, max_tokens: int = 512, temperature: float = 0.2) -> str:
    """Call LLM with automatic fallback: OpenAI → Anthropic → Gemini.
    Returns raw text from the LLM.
    Raises RuntimeError if all providers fail.
    """
    errors: list[str] = []

    for key in _openai_keys():
        try:
            return _call_openai(key, messages, max_tokens, temperature)
        except Exception as e:
            errors.append(f"OpenAI: {e}")

    for key in _anthropic_keys():
        try:
            return _call_anthropic(key, messages, max_tokens, temperature)
        except Exception as e:
            errors.append(f"Anthropic: {e}")

    gkey = _gemini_key()
    if gkey:
        try:
            return _call_gemini(gkey, messages, max_tokens, temperature)
        except Exception as e:
            errors.append(f"Gemini: {e}")

    raise RuntimeError(f"Tous les fournisseurs LLM ont échoué — {'; '.join(errors)}")


def call_llm_json(messages: list, max_tokens: int = 512, temperature: float = 0.2) -> dict:
    """Call LLM and parse JSON response. Retries once with stricter prompt if parsing fails."""
    content = call_llm(messages, max_tokens, temperature)
    try:
        return json.loads(_clean_json(content))
    except json.JSONDecodeError:
        # Retry : injecter le texte brut et demander de le reformater en JSON
        retry_messages = messages + [
            {"role": "assistant", "content": content},
            {"role": "user", "content": (
                "ERREUR : ta réponse précédente n'était pas un JSON valide. "
                "Reformule-la MAINTENANT en JSON pur, en commençant directement par { et "
                "en respectant exactement le format demandé. Aucun texte hors du JSON."
            )},
        ]
        content2 = call_llm(retry_messages, max_tokens, temperature=0.0)
        return json.loads(_clean_json(content2))
