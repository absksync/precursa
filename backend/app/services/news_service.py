import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List

import requests

from app.core.config import settings


logger = logging.getLogger(__name__)

KEYWORDS = ["maritime", "shipping", "port", "strait", "conflict", "naval"]
NEWS_LIMIT = 16


def _matches_keywords(*parts: object) -> bool:
    text = " ".join(str(part or "") for part in parts).lower()
    return any(keyword in text for keyword in KEYWORDS)


def _normalise_article(article: Dict[str, object], source: str) -> Dict[str, str]:
    published_at = str(article.get("publishedAt") or article.get("seendate") or article.get("timestamp") or datetime.now(timezone.utc).isoformat())
    title = str(article.get("title") or article.get("headline") or article.get("sourceTitle") or "").strip()
    description = str(article.get("description") or article.get("summary") or article.get("snippet") or article.get("sourceSummary") or "").strip()
    url = str(article.get("url") or article.get("sourceUrl") or article.get("documentIdentifier") or "").strip() or None

    source_name = source
    if source == "newsapi":
        source_name = str((article.get("source") or {}).get("name") or "NewsAPI")
    elif source == "gdelt":
        source_name = str(article.get("domain") or article.get("sourceCountry") or "GDELT")

    return {
        "headline": title,
        "summary": description,
        "published_at": published_at,
        "source": source_name,
        "url": url,
    }


def _fetch_newsapi(window: str) -> List[Dict[str, str]]:
    if not settings.NEWS_API_KEY.strip():
        return []

    days = {"24h": 1, "7d": 7, "30d": 30}.get(window, 1)
    params = {
        "q": "(maritime OR shipping OR port OR strait OR conflict OR naval)",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": NEWS_LIMIT * 2,
        "from": (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat(),
        "apiKey": settings.NEWS_API_KEY,
    }

    response = requests.get(f"{settings.NEWS_API_BASE_URL}/everything", params=params, timeout=15)
    response.raise_for_status()
    payload = response.json() or {}
    articles = payload.get("articles") or []

    results: List[Dict[str, str]] = []
    for article in articles:
        if not isinstance(article, dict):
            continue

        candidate = _normalise_article(article, "newsapi")
        if _matches_keywords(candidate["headline"], candidate["summary"]):
            results.append(candidate)

    return results[:NEWS_LIMIT]


def _fetch_gdelt(window: str) -> List[Dict[str, str]]:
    timespan = {"24h": "1d", "7d": "7d", "30d": "30d"}.get(window, "1d")
    params = {
        "query": "(maritime OR shipping OR port OR strait OR conflict OR naval)",
        "mode": "ArtList",
        "format": "json",
        "maxrecords": NEWS_LIMIT * 2,
        "timespan": timespan,
        "sort": "hybridrel",
    }

    response = requests.get(settings.GDELT_BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    payload = response.json() or {}
    articles = payload.get("articles") or []

    results: List[Dict[str, str]] = []
    for article in articles:
        if not isinstance(article, dict):
            continue

        candidate = _normalise_article(article, "gdelt")
        if _matches_keywords(candidate["headline"], candidate["summary"]):
            results.append(candidate)

    return results[:NEWS_LIMIT]


def fetch_recent_articles(window: str = "24h") -> Dict[str, object]:
    source = "gdelt"
    articles: List[Dict[str, str]] = []
    errors: List[str] = []

    try:
                articles = _fetch_newsapi(window)
                if articles:
                        source = "newsapi"
    except Exception as exc:
                logger.warning("NewsAPI fetch failed: %s", exc)
                errors.append("newsapi")

    if not articles:
        try:
            articles = _fetch_gdelt(window)
            source = "gdelt" if articles else source
        except Exception as exc:
            logger.warning("GDELT fetch failed: %s", exc)
            errors.append("gdelt")

    seen: set[str] = set()
    deduped: List[Dict[str, str]] = []
    for article in articles:
        headline = article.get("headline", "").strip()
        if not headline or headline.lower() in seen:
            continue
        seen.add(headline.lower())
        deduped.append(article)

    return {
        "source": source if deduped else "unavailable",
        "events": deduped[:NEWS_LIMIT],
        "errors": errors,
        "keywords": KEYWORDS,
    }