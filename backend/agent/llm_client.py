import json
from json import JSONDecodeError
from groq import Groq
from backend.config import get_settings

settings = get_settings()
_groq = Groq(api_key=settings.groq_api_key)


def call_llm(prompt: str, system: str = "", json_mode: bool = False) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    kwargs = {
        "model": settings.groq_model,
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.3,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = _groq.chat.completions.create(**kwargs, timeout=3.5)
        return response.choices[0].message.content
    except Exception as e:
        print(f"[NEXUS LLM] Error calling Groq: {e}")
        return "{}" if json_mode else f"NEXUS Fallback generated due to LLM error: {e}"


def call_llm_json(prompt: str, system: str = "") -> dict:
    raw = call_llm(prompt, system, json_mode=True)
    try:
        return json.loads(raw)
    except JSONDecodeError:
        cleaned = (
            raw.strip()
            .removeprefix("```json")
            .removeprefix("```")
            .removesuffix("```")
            .strip()
        )
        return json.loads(cleaned)
