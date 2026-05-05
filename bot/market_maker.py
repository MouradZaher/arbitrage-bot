"""
Sentinel-Poly | Market Maker (Liquidity Reward Farmer)

Places resting limit orders at the best bid/ask to earn Polymarket
USDC.e Liquidity Rewards, with a circuit breaker that cancels all
orders when the spread widens beyond the configured threshold.
"""
from __future__ import annotations

import asyncio

import aiohttp

from bot.clob_client import ClobClient, midpoint
from bot.config import SPREAD_CIRCUIT_PCT
from bot.logger import get_logger
from bot.risk_manager import RiskManager

log = get_logger("market_maker")


class MarketMaker:
    """
    Passive liquidity provider for a single YES token.

    Strategy:
      1. Fetch the current order book.
      2. Check the bid/ask spread.
      3. If spread > circuit-breaker threshold → cancel all & halt.
      4. Otherwise post limit orders one tick inside best bid/ask.
    """

    TICK = 0.001  # Minimum price increment on Polymarket CLOB

    def __init__(
        self,
        clob: ClobClient,
        risk: RiskManager,
        session: aiohttp.ClientSession,
    ):
        self._clob   = clob
        self._risk   = risk
        self._session = session

    # ── Circuit Breaker ───────────────────────────────────────

    @staticmethod
    def spread_pct(book: dict) -> float | None:
        bids = book.get("bids", [])
        asks = book.get("asks", [])
        if not bids or not asks:
            return None
        best_bid = max(float(b["price"]) for b in bids)
        best_ask = min(float(a["price"]) for a in asks)
        mid      = (best_bid + best_ask) / 2
        if mid == 0:
            return None
        return (best_ask - best_bid) / mid

    async def _trigger_circuit_breaker(self, token_id: str, spread: float):
        log.warning(
            "⚡ Circuit breaker | token=%s spread=%.2f%% (limit=%.2f%%)",
            token_id, spread * 100, SPREAD_CIRCUIT_PCT * 100,
        )
        try:
            result = await self._clob.cancel_all_orders()
            log.info("All orders cancelled: %s", result)
        except Exception as exc:
            log.error("Failed to cancel orders: %s", exc)

    # ── Quote ─────────────────────────────────────────────────

    async def quote(self, token_id: str, size_usdc: float) -> dict:
        """
        Compute and (in live mode) place resting bid and ask quotes.
        Returns a summary dict — never executes in discovery-only mode.
        """
        book  = await self._clob.get_book(token_id)
        bids  = book.get("bids", [])
        asks  = book.get("asks", [])

        if not bids or not asks:
            return {"status": "no_book", "token_id": token_id}

        best_bid = max(float(b["price"]) for b in bids)
        best_ask = min(float(a["price"]) for a in asks)
        spread   = self.spread_pct(book)

        # Circuit breaker
        if spread is not None and spread > SPREAD_CIRCUIT_PCT:
            await self._trigger_circuit_breaker(token_id, spread)
            return {
                "status":    "circuit_breaker",
                "token_id":  token_id,
                "spread_pct": round(spread * 100, 2),
            }

        our_bid = round(best_bid + self.TICK, 4)   # one tick above best bid
        our_ask = round(best_ask - self.TICK, 4)   # one tick below best ask

        result = {
            "status":    "quoted",
            "token_id":  token_id,
            "bid":       our_bid,
            "ask":       our_ask,
            "spread_pct": round((spread or 0) * 100, 2),
            "size_usdc": size_usdc,
        }

        log.info(
            "📊 Quote | token=%s bid=%.4f ask=%.4f spread=%.2f%%",
            token_id, our_bid, our_ask, (spread or 0) * 100,
        )
        return result


# ── Vegas Gap (Sportsbook Arbitrage) ─────────────────────────

async def check_vegas_gap(
    market_question: str,
    poly_mid: float,
    session: aiohttp.ClientSession,
    threshold: float = 0.05,
) -> dict | None:
    """
    Placeholder for sportsbook scraping.
    In production: scrape The Odds API / pinnacle for the same event
    and compare implied probability to poly_mid.
    Returns an alert dict if gap > threshold.
    """
    # TODO: integrate TheOddsAPI (https://the-odds-api.com/)
    # odds_prob = await _fetch_sportsbook_prob(market_question, session)
    odds_prob = None  # Not yet wired

    if odds_prob is None:
        return None

    gap = abs(poly_mid - odds_prob)
    if gap > threshold:
        return {
            "alert":       "VEGAS_GAP",
            "question":    market_question,
            "poly_mid":    poly_mid,
            "odds_prob":   odds_prob,
            "gap_pct":     round(gap * 100, 2),
        }
    return None
