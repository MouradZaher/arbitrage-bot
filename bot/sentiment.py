"""
Sentinel-Poly | News Sentiment Engine
Queries the Tavily Search API for real-time news and converts
headlines to an implied probability score for comparison against
the Polymarket midpoint.
"""
from __future__ import annotations

import re
import aiohttp

from bot.config import TAVILY_API_KEY, DIVERGENCE_THRESHOLD
from bot.logger import get_logger

log = get_logger("sentiment")

TAVILY_URL = "https://api.tavily.com/search"

# Simple keyword scoring table
_BULLISH = [
    "wins", "victory", "passes", "approved", "elected", "confirmed",
    "breakthrough", "success", "agreement", "signed", "done",
]
_BEARISH = [
    "loses", "defeat", "rejected", "failed", "blocked", "withdrawn",
    "cancelled", "missed", "crisis", "arrested", "indicted",
]


def _score_headline(text: str) -> float:
    """
    Naive lexical scorer → [0.0, 1.0] implied YES probability.
    Returns 0.5 (neutral) if no signal found.
    """
    text_lower = text.lower()
    bull = sum(1 for w in _BULLISH if w in text_lower)
    bear = sum(1 for w in _BEARISH if w in text_lower)
    total = bull + bear
    if total == 0:
        return 0.5
    return bull / total


async def fetch_sentiment(
    query: str,
    session: aiohttp.ClientSession,
    max_results: int = 5,
) -> float:
    """
    Query Tavily for `query` and return an aggregated YES probability.

    Returns 0.5 if Tavily key is missing or request fails.
    """
    if not TAVILY_API_KEY:
        log.debug("Tavily key not set — skipping news for: %s", query)
        return 0.5

    payload = {
        "api_key":     TAVILY_API_KEY,
        "query":       query,
        "search_depth": "basic",
        "max_results":  max_results,
    }
    try:
        async with session.post(TAVILY_URL, json=payload, timeout=aiohttp.ClientTimeout(total=8)) as r:
            r.raise_for_status()
            data = await r.json()
    except Exception as exc:
        log.warning("Tavily request failed: %s", exc)
        return 0.5

    results = data.get("results", [])
    if not results:
        return 0.5

    scores = [_score_headline(r.get("title", "") + " " + r.get("content", "")) for r in results]
    agg = sum(scores) / len(scores)
    log.debug("Sentiment '%s' → %.3f (n=%d)", query, agg, len(scores))
    return round(agg, 4)


def check_divergence(
    market_mid: float,
    sentiment_prob: float,
    threshold: float = DIVERGENCE_THRESHOLD,
) -> tuple[bool, float]:
    """
    Returns (is_divergent, delta).
    Divergence = |market_mid − sentiment_prob| > threshold.
    """
    delta = abs(market_mid - sentiment_prob)
    return delta > threshold, round(delta, 4)
