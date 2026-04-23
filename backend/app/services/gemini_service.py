import json
import logging
import re
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
    context = payload.get("context") if isinstance(payload, dict) else None
    if isinstance(context, dict) and context:
        weather = context.get("weather") if isinstance(context.get("weather"), dict) else {}
        breakdown = context.get("breakdown") if isinstance(context.get("breakdown"), dict) else {}
        nearby_vessels = context.get("nearby_vessels") if isinstance(context.get("nearby_vessels"), list) else []
        route_zones = context.get("route_zones") if isinstance(context.get("route_zones"), list) else []
        route = context.get("route", "Unknown route")

        prompt_lines = [
            "You are a maritime logistics risk analyst.",
            "Analyze the following shipment:",
            f"- Route: {route}",
            f"- Origin: {context.get('origin', 'N/A')}",
            f"- Destination: {context.get('destination', 'N/A')}",
            f"- DRI Score: {context.get('dri', 'N/A')}",
            f"- Risk Level: {context.get('level', 'N/A')}",
            "",
            "Weather Conditions:",
            f"- Temperature: {weather.get('temperature', 'N/A')}°C",
            f"- Wind Speed: {weather.get('wind_speed', 'N/A')} km/h",
            f"- Rain: {weather.get('rain', 'N/A')} mm",
            f"- Visibility: {weather.get('visibility', 'N/A')} km",
            f"- Weather Severity: {weather.get('weather_severity', 'N/A')}/100",
            "",
            f"Port Congestion: {breakdown.get('congestion', context.get('congestion', 'N/A'))}/100",
            f"Nearby Vessels: {len(nearby_vessels)}",
            f"Route Zones: {', '.join(route_zones) if route_zones else 'None detected'}",
            "",
            "Give a specific explanation:",
            "- WHY this shipment has this risk level",
            "- Which factor contributes the most (weather vs congestion)",
            "- Mention real-world maritime reasoning",
            "- Keep it concise (2–3 lines)",
            "",
            "DO NOT give generic answers.",
            "Each explanation must be unique to the data.",
            "",
            "Return plain text only.",
        ]
        return "\n".join(prompt_lines)

    return (
        "You are a maritime logistics analyst.\n"
        "Write a concise 2-sentence operational explanation grounded only in the supplied data.\n"
        "Mention the main risk drivers and the likely impact on shipments.\n"
        "Do not mention that you are an AI. Do not use bullet points. Return plain text only.\n\n"
        f"Data:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def _extract_json_block(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
      cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
      cleaned = re.sub(r"\s*```$", "", cleaned)

    start = cleaned.find("{")
    array_start = cleaned.find("[")
    if start == -1 or (array_start != -1 and array_start < start):
        start = array_start

    end = max(cleaned.rfind("}"), cleaned.rfind("]"))
    if start == -1 or end == -1 or end <= start:
        return cleaned

    return cleaned[start:end + 1]


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


def generate_structured_json(instructions: str, payload: Dict[str, Any]) -> Any | None:
    client = _get_client()
    if client is None:
        return None

    prompt = (
        f"{instructions.strip()}\n\n"
        "Return valid JSON only. No markdown fences, no commentary.\n\n"
        f"Data:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )
        text = (getattr(response, "text", "") or "").strip()
        if not text:
            return None

        parsed = json.loads(_extract_json_block(text))
        return parsed
    except Exception as exc:
        logger.warning("Gemini structured response failed: %s", exc)
        return None