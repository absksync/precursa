import json
import logging
from functools import lru_cache
from typing import Any, Dict

from google import genai

from app.core.config import settings


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_client() -> genai.Client | None:
    api_key = settings.GEMINI_API_KEY.strip()
    if not api_key:
        return None

    return genai.Client(api_key=api_key)


def _build_prompt(payload: Dict[str, Any]) -> str:
    return (
        "You are a maritime logistics analyst.\n"
        "Write a concise 2-sentence operational explanation grounded only in the supplied data.\n"
        "Mention the main risk drivers and the likely impact on shipments.\n"
        "Do not mention that you are an AI. Do not use bullet points. Return plain text only.\n\n"
        f"Data:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def generate_risk_insight(payload: Dict[str, Any]) -> str | None:
    client = _get_client()
    if client is None:
        return None

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=_build_prompt(payload),
        )
        text = (getattr(response, "text", "") or "").strip()
        return text or None
    except Exception as exc:
        logger.warning("Gemini insight generation failed: %s", exc)
        return None