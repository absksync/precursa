import logging
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List

from app.services.gemini_service import generate_structured_json
from app.services.news_service import fetch_recent_articles


logger = logging.getLogger(__name__)

RISK_LEVELS = ["low", "medium", "high"]
REGION_HINTS = [
    "red sea",
    "suez",
    "gulf of aden",
    "strait of hormuz",
    "malacca",
    "singapore",
    "south china sea",
    "taiwan",
    "black sea",
    "baltic",
    "panama",
    "mediterranean",
    "indian ocean",
    "eastern mediterranean",
]


def _risk_from_text(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ["attack", "conflict", "war", "missile", "blockade", "naval", "sanction", "strike"]):
        return "high"
    if any(token in lowered for token in ["delay", "port", "strait", "inspection", "warning", "tension", "disruption"]):
        return "medium"
    return "low"


def _infer_region(text: str) -> str:
    lowered = text.lower()
    for hint in REGION_HINTS:
        if hint in lowered:
            return hint.title().replace("Of", "of")

    if "china" in lowered or "taiwan" in lowered:
        return "East Asia"
    if "europe" in lowered or "russia" in lowered or "ukraine" in lowered or "black sea" in lowered:
        return "Europe / Black Sea"
    if "middle east" in lowered or "iran" in lowered or "israel" in lowered or "gaza" in lowered:
        return "Middle East"
    if "africa" in lowered or "red sea" in lowered or "suez" in lowered:
        return "Africa / Red Sea"
    return "Global Logistics"


def _fallback_article(article: Dict[str, str]) -> Dict[str, str]:
    headline = article.get("headline", "").strip()
    summary = article.get("summary", "").strip()
    combined = f"{headline} {summary}"
    risk_level = _risk_from_text(combined)
    region = _infer_region(combined)

    if risk_level == "high":
        reasoning = "The headline indicates acute geopolitical or maritime disruption risk that can escalate routing and insurance pressure."
        impact_summary = f"Likely to trigger rerouting, slower transit windows, and higher carrier caution around {region}."
    elif risk_level == "medium":
        reasoning = "The headline suggests active shipping stress or regional instability with probable operational spillover."
        impact_summary = f"May increase inspection times, congestion, and schedule variability across {region}."
    else:
        reasoning = "The article indicates watchlist-level developments that should be monitored but are not yet disrupting flows."
        impact_summary = f"Minimal immediate impact, though {region} should remain on monitoring status."

    return {
        "headline": headline,
        "region": region,
        "risk_level": risk_level,
        "reasoning": reasoning,
        "impact_summary": impact_summary,
        "published_at": article.get("published_at", datetime.now(timezone.utc).isoformat()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": article.get("source", "unknown"),
        "url": article.get("url"),
    }


def _normalize_model_item(item: Dict[str, object], article: Dict[str, str]) -> Dict[str, str]:
    headline = str(item.get("headline") or article.get("headline") or "").strip()
    region = str(item.get("region") or _infer_region(f"{headline} {article.get('summary', '')}")).strip()
    risk_level = str(item.get("risk_level") or "low").strip().lower()
    if risk_level not in RISK_LEVELS:
        risk_level = _risk_from_text(f"{headline} {article.get('summary', '')}")

    reasoning = str(item.get("reasoning") or article.get("summary") or "").strip()
    impact_summary = str(item.get("impact_summary") or "").strip()
    if not impact_summary:
        impact_summary = f"Operational exposure likely increases across {region}."

    return {
        "headline": headline,
        "region": region,
        "risk_level": risk_level,
        "reasoning": reasoning,
        "impact_summary": impact_summary,
        "published_at": article.get("published_at", datetime.now(timezone.utc).isoformat()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": article.get("source", "unknown"),
        "url": article.get("url"),
    }


def _batch_prompt(articles: List[Dict[str, str]]) -> str:
    return (
        "You are a geopolitical logistics risk analyst.\n"
        "Review the articles and return a JSON array of objects.\n"
        "Each object must include: headline, region, risk_level, reasoning, impact_summary.\n"
        "Risk level must be one of low, medium, high.\n"
        "Use only the supplied article data, and keep the reasoning concise but specific.\n"
        "Prefer the affected shipping region, strait, port, sea lane, or country block if mentioned.\n"
        "Return JSON only.\n\n"
        f"Articles:\n{articles}"
    )


def build_global_risk_intelligence(window: str = "24h", limit: int = 8) -> Dict[str, object]:
    news = fetch_recent_articles(window=window)
    articles = news.get("events") or []
    source = news.get("source", "unavailable")
    search_terms = news.get("keywords", [])
    errors = news.get("errors", [])

    if not articles:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "window": window,
            "source": source,
            "status": "degraded",
            "search_terms": search_terms,
            "summary": {
                "total_articles": 0,
                "high_risk_articles": 0,
                "medium_risk_articles": 0,
                "low_risk_articles": 0,
                "dominant_region": "Unavailable",
                "top_signal": "No articles returned from the news provider.",
                "source": source,
            },
            "events": [],
            "errors": errors,
        }

    selected = articles[:limit]
    model_payload = [
        {
            "headline": article.get("headline", ""),
            "summary": article.get("summary", ""),
            "source": article.get("source", ""),
            "published_at": article.get("published_at", ""),
        }
        for article in selected
    ]

    model_items = generate_structured_json(_batch_prompt(model_payload), {"articles": model_payload})

    structured_events: List[Dict[str, str]] = []
    if isinstance(model_items, list):
        for index, article in enumerate(selected):
            item = model_items[index] if index < len(model_items) and isinstance(model_items[index], dict) else {}
            structured_events.append(_normalize_model_item(item, article))
    else:
        structured_events = [_fallback_article(article) for article in selected]

    if not structured_events:
        structured_events = [_fallback_article(article) for article in selected]

    counts = Counter(item["risk_level"] for item in structured_events)
    region_counts = Counter(item["region"] for item in structured_events)
    dominant_region = region_counts.most_common(1)[0][0] if region_counts else "Global Logistics"
    top_signal = structured_events[0]["reasoning"] if structured_events else "No signal available."

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window": window,
        "source": source,
        "status": "ok" if source != "unavailable" else "degraded",
        "search_terms": search_terms,
        "summary": {
            "total_articles": len(structured_events),
            "high_risk_articles": counts.get("high", 0),
            "medium_risk_articles": counts.get("medium", 0),
            "low_risk_articles": counts.get("low", 0),
            "dominant_region": dominant_region,
            "top_signal": top_signal,
            "source": source,
        },
        "events": structured_events,
        "errors": errors,
    }