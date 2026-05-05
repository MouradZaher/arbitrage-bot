"""
Sentinel-Poly | Polymarket CLOB Client
Thin async wrapper around the Polymarket CLOB REST API.
Docs: https://docs.polymarket.com/#clob-client
"""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import time
from typing import Any

import aiohttp

from bot.config import CLOB_BASE, POLY_API_KEY, POLY_API_SECRET, POLY_API_PASS
from bot.logger import get_logger

log = get_logger("clob_client")


def _sign_request(method: str, path: str, body: str = "") -> dict[str, str]:
    """Generate HMAC-SHA256 auth headers for the CLOB API."""
    ts = str(int(time.time()))
    msg = ts + method.upper() + path + body
    sig = hmac.new(
        POLY_API_SECRET.encode(),
        msg.encode(),
        hashlib.sha256,
    ).hexdigest()
    return {
        "POLY-API-KEY":        POLY_API_KEY,
        "POLY-SIGNATURE":      sig,
        "POLY-TIMESTAMP":      ts,
        "POLY-PASSPHRASE":     POLY_API_PASS,
        "Content-Type":        "application/json",
    }


class ClobClient:
    """Async Polymarket CLOB API client."""

    def __init__(self, session: aiohttp.ClientSession):
        self._s = session

    # ── Public endpoints (no auth required) ──────────────────

    async def get_markets(self, limit: int = 20, offset: int = 0) -> list[dict]:
        """Fetch markets sorted by volume (descending)."""
        url = f"{CLOB_BASE}/markets"
        params = {
            "limit":  limit,
            "offset": offset,
            "order":  "volume",
            "ascending": "false",
            "active": "true",
        }
        async with self._s.get(url, params=params) as r:
            r.raise_for_status()
            data = await r.json()
            return data.get("data", data) if isinstance(data, dict) else data

    async def get_book(self, token_id: str) -> dict:
        """Fetch the order book for a specific outcome token."""
        url = f"{CLOB_BASE}/book"
        params = {"token_id": token_id}
        async with self._s.get(url, params=params) as r:
            r.raise_for_status()
            return await r.json()

    async def get_price(self, token_id: str, side: str = "buy") -> float | None:
        """Return the best price for a token on the given side."""
        url = f"{CLOB_BASE}/price"
        params = {"token_id": token_id, "side": side}
        try:
            async with self._s.get(url, params=params) as r:
                r.raise_for_status()
                data = await r.json()
                return float(data.get("price", 0))
        except Exception as exc:
            log.warning("get_price failed for %s: %s", token_id, exc)
            return None

    # ── Authenticated endpoints ───────────────────────────────

    async def place_limit_order(self, order: dict) -> dict:
        """Place a limit order. order must be a signed CLOB order dict."""
        path = "/order"
        url  = CLOB_BASE + path
        import json
        body = json.dumps(order)
        headers = _sign_request("POST", path, body)
        async with self._s.post(url, headers=headers, data=body) as r:
            r.raise_for_status()
            return await r.json()

    async def cancel_all_orders(self) -> dict:
        """Emergency: cancel all open orders."""
        path = "/orders"
        url  = CLOB_BASE + path
        headers = _sign_request("DELETE", path)
        async with self._s.delete(url, headers=headers) as r:
            r.raise_for_status()
            return await r.json()

    async def get_open_orders(self) -> list[dict]:
        """Fetch all open orders for the authenticated wallet."""
        path = "/orders"
        url  = CLOB_BASE + path
        headers = _sign_request("GET", path)
        async with self._s.get(url, headers=headers) as r:
            r.raise_for_status()
            data = await r.json()
            return data.get("data", [])


# ── Midpoint helper ───────────────────────────────────────────

def midpoint(book: dict) -> float | None:
    """
    Compute the midpoint price from a CLOB order book.
    Returns None if the book is empty on either side.
    """
    bids = book.get("bids", [])
    asks = book.get("asks", [])
    if not bids or not asks:
        return None
    best_bid = max(float(b["price"]) for b in bids)
    best_ask = min(float(a["price"]) for a in asks)
    return (best_bid + best_ask) / 2
