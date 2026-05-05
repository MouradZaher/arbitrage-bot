"""
Sentinel-Poly | Discovery Agent (Main Entrypoint)

Scans the top N high-volume Polymarket markets and logs every
"Opportunity Found" with projected edge. Does NOT place orders —
review the log table before enabling live execution.

Run:
    python -m bot.discovery_agent
"""
from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone

import aiohttp

from bot.clob_client import ClobClient, midpoint
from bot.config import TOP_MARKETS, CAPITAL_USDC
from bot.logger import get_logger
from bot.market_maker import MarketMaker, check_vegas_gap
from bot.risk_manager import RiskManager
from bot.sentiment import check_divergence, fetch_sentiment

log = get_logger("discovery")

POLL_INTERVAL_SECONDS = 30   # How often to re-scan
SIMULATION_HOURS      = 1    # Default sim duration

# ── ANSI table helpers ────────────────────────────────────────
HDR = (
    f"{'#':<4} {'Market Question':<50} {'Mid':>6} "
    f"{'Sent':>6} {'Δ%':>6} {'Signal':<20} {'Kelly $':>8}"
)
SEP = "─" * len(HDR)


def _fmt_row(
    idx: int,
    question: str,
    mid: float,
    sentiment: float,
    delta: float,
    signal: str,
    kelly: float,
) -> str:
    q = question[:48] + ".." if len(question) > 50 else question
    return (
        f"{idx:<4} {q:<50} {mid:>6.3f} "
        f"{sentiment:>6.3f} {delta*100:>5.1f}% {signal:<20} {kelly:>8.2f}"
    )


# ── Core scan loop ────────────────────────────────────────────

async def scan_once(
    clob: ClobClient,
    risk: RiskManager,
    session: aiohttp.ClientSession,
) -> list[dict]:
    """Single pass: fetch top markets → compute edge → log table."""

    if risk.kill_switch_triggered:
        log.critical("Kill switch active — scan paused.")
        return []

    markets = await clob.get_markets(limit=TOP_MARKETS)
    log.info("Scanning %d markets …", len(markets))

    opportunities: list[dict] = []

    log.info(SEP)
    log.info(HDR)
    log.info(SEP)

    for idx, mkt in enumerate(markets, 1):
        question   = mkt.get("question", mkt.get("description", "Unknown"))
        tokens     = mkt.get("tokens", [])
        if not tokens:
            continue
        yes_token  = tokens[0]
        token_id   = yes_token.get("token_id", "")

        # ── Fetch order book ──────────────────────────────────
        try:
            book = await clob.get_book(token_id)
        except Exception as exc:
            log.debug("Book fetch failed for %s: %s", token_id, exc)
            continue

        mid = midpoint(book)
        if mid is None:
            continue

        # ── News sentiment ────────────────────────────────────
        sentiment = await fetch_sentiment(question, session)

        # ── Divergence check ──────────────────────────────────
        is_divergent, delta = check_divergence(mid, sentiment)

        # ── Edge / Kelly sizing ───────────────────────────────
        # Simple edge: how far sentiment is from market mid
        # odds: approximate binary (mid maps to ~1/mid decimal odds)
        edge  = delta if is_divergent else 0.0
        odds  = (1 / mid - 1) if mid > 0 else 0.0
        kelly = risk.kelly_size(edge=edge, odds=odds) if is_divergent else 0.0

        signal = "🟢 OPPORTUNITY" if is_divergent else "   --"

        log.info(
            _fmt_row(idx, question, mid, sentiment, delta, signal, kelly)
        )

        # ── Vegas Gap check ───────────────────────────────────
        vegas = await check_vegas_gap(question, mid, session)
        if vegas:
            log.warning("🎰 VEGAS GAP: %s", vegas)

        # ── Market-maker spread check ─────────────────────────
        mm     = MarketMaker(clob=clob, risk=risk, session=session)
        quote  = await mm.quote(token_id, size_usdc=kelly or 10.0)

        if is_divergent or quote.get("status") == "circuit_breaker":
            opp = {
                "timestamp":    datetime.now(timezone.utc).isoformat(),
                "question":     question,
                "token_id":     token_id,
                "mid":          mid,
                "sentiment":    sentiment,
                "delta":        delta,
                "edge":         edge,
                "kelly_usdc":   kelly,
                "signal":       signal.strip(),
                "spread_pct":   quote.get("spread_pct"),
                "bid":          quote.get("bid"),
                "ask":          quote.get("ask"),
                "projected_roi": round(edge * kelly / max(CAPITAL_USDC, 1) * 100, 3),
            }
            opportunities.append(opp)
            log.info(
                "✅ Opportunity Found | %s | mid=%.3f | Δ=%.1f%% | kelly=$%.2f | ROI≈%.3f%%",
                question[:40], mid, delta * 100, kelly, opp["projected_roi"],
            )

        await asyncio.sleep(0.25)   # polite rate-limiting

    log.info(SEP)
    log.info(
        "Scan complete | %d opportunities | risk status: %s",
        len(opportunities), risk.status(),
    )
    return opportunities


# ── Simulation runner ─────────────────────────────────────────

async def run_simulation(hours: float = SIMULATION_HOURS):
    """
    Run the discovery loop for `hours` and print a final summary table.
    """
    end_time      = time.time() + hours * 3600
    all_opps: list[dict] = []
    scan_count    = 0

    connector = aiohttp.TCPConnector(limit=20)
    async with aiohttp.ClientSession(connector=connector) as session:
        clob = ClobClient(session)
        risk = RiskManager()

        log.info("=" * 70)
        log.info("  SENTINEL-POLY SIMULATION  |  %.1f-hour window", hours)
        log.info("  Capital: $%.2f  |  Max/trade: $%.2f  |  Kill: $%.2f",
                 CAPITAL_USDC, risk.kelly_size(0, 0) + 0,
                 CAPITAL_USDC * 0.05)
        log.info("=" * 70)

        while time.time() < end_time:
            scan_count += 1
            log.info("── Scan #%d ──", scan_count)
            try:
                opps = await scan_once(clob, risk, session)
                all_opps.extend(opps)
            except Exception as exc:
                log.error("Scan error: %s", exc)

            if risk.kill_switch_triggered:
                log.critical("Bot halted by kill switch.")
                break

            remaining = end_time - time.time()
            if remaining > POLL_INTERVAL_SECONDS:
                log.info("Next scan in %ds …", POLL_INTERVAL_SECONDS)
                await asyncio.sleep(POLL_INTERVAL_SECONDS)

    # ── Final Report ──────────────────────────────────────────
    log.info("\n%s", "=" * 70)
    log.info("  SIMULATION COMPLETE  |  Scans: %d  |  Opps: %d", scan_count, len(all_opps))
    log.info("=" * 70)

    if all_opps:
        log.info(
            f"\n{'Timestamp':<26} {'Question':<40} {'Δ%':>5} "
            f"{'Kelly$':>7} {'ROI%':>8}"
        )
        log.info("─" * 90)
        for o in sorted(all_opps, key=lambda x: x["projected_roi"], reverse=True):
            log.info(
                "%-26s %-40s %5.1f%% %7.2f %8.3f%%",
                o["timestamp"][:19],
                o["question"][:38],
                o["delta"] * 100,
                o["kelly_usdc"],
                o["projected_roi"],
            )
    else:
        log.info("No opportunities flagged this session.")

    # Dump raw JSON for dashboard ingestion
    with open("logs/opportunities.json", "w") as f:
        json.dump(all_opps, f, indent=2)
    log.info("Raw data saved to logs/opportunities.json")


# ── CLI ───────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Sentinel-Poly Discovery Agent")
    parser.add_argument("--hours", type=float, default=1.0, help="Simulation window in hours")
    args = parser.parse_args()
    asyncio.run(run_simulation(hours=args.hours))
