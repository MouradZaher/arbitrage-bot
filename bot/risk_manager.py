"""
Sentinel-Poly | Risk Manager
Kelly Criterion sizing, daily P&L tracking, kill-switch logic.
"""
from __future__ import annotations

from bot.config import (
    CAPITAL_USDC,
    MAX_POSITION_USDC,
    KILL_SWITCH_LOSS,
    DRAWDOWN_KILL_PCT,
)
from bot.logger import get_logger

log = get_logger("risk")


class RiskManager:
    """
    Tracks intraday P&L and enforces hard limits.

    Usage:
        rm = RiskManager()
        size = rm.kelly_size(edge=0.12, odds=1.8)
        rm.record_trade(pnl=-30)
        if rm.kill_switch_triggered:
            await clob.cancel_all_orders()
    """

    def __init__(self):
        self._daily_pnl: float = 0.0
        self._trade_count: int = 0
        self.kill_switch_triggered: bool = False
        log.info(
            "RiskManager online | capital=%.2f | max/trade=%.2f | kill=%.2f",
            CAPITAL_USDC,
            MAX_POSITION_USDC,
            KILL_SWITCH_LOSS,
        )

    # ── Kelly Criterion ───────────────────────────────────────

    @staticmethod
    def kelly_fraction(edge: float, odds: float) -> float:
        """
        Full Kelly: f* = edge / odds
        edge  = expected win prob − lose prob  (e.g. 0.12)
        odds  = decimal odds − 1              (e.g. 0.8 for 1.8x)
        Returns a fraction of capital [0, 1].
        """
        if odds <= 0:
            return 0.0
        raw = edge / odds
        # Apply half-Kelly for conservatism
        return max(0.0, min(raw * 0.5, 1.0))

    def kelly_size(self, edge: float, odds: float) -> float:
        """
        Returns the recommended position size in USDC.
        Hard-capped at MAX_POSITION_USDC (2% of capital).
        """
        frac = self.kelly_fraction(edge, odds)
        size = CAPITAL_USDC * frac
        capped = min(size, MAX_POSITION_USDC)
        log.debug(
            "Kelly: edge=%.3f odds=%.3f → frac=%.4f size=%.2f capped=%.2f",
            edge, odds, frac, size, capped,
        )
        return round(capped, 2)

    # ── P&L Tracking ──────────────────────────────────────────

    def record_trade(self, pnl: float) -> None:
        """Update intraday P&L and check the kill switch."""
        self._daily_pnl    += pnl
        self._trade_count  += 1
        log.info(
            "Trade #%d recorded | pnl=%.2f | daily_pnl=%.2f",
            self._trade_count, pnl, self._daily_pnl,
        )
        self._check_kill_switch()

    def _check_kill_switch(self) -> None:
        if self._daily_pnl <= -KILL_SWITCH_LOSS and not self.kill_switch_triggered:
            self.kill_switch_triggered = True
            log.critical(
                "🚨 KILL SWITCH TRIGGERED | daily_pnl=%.2f (limit=%.2f) | "
                "All orders will be cancelled.",
                self._daily_pnl, -KILL_SWITCH_LOSS,
            )

    # ── Properties ────────────────────────────────────────────

    @property
    def daily_pnl(self) -> float:
        return self._daily_pnl

    @property
    def drawdown_pct(self) -> float:
        return abs(min(0.0, self._daily_pnl)) / CAPITAL_USDC

    def status(self) -> dict:
        return {
            "capital":       CAPITAL_USDC,
            "daily_pnl":     round(self._daily_pnl, 2),
            "drawdown_pct":  round(self.drawdown_pct * 100, 2),
            "kill_limit":    DRAWDOWN_KILL_PCT * 100,
            "kill_active":   self.kill_switch_triggered,
            "trades_today":  self._trade_count,
        }

    def reset_daily(self) -> None:
        """Call at midnight UTC to reset the daily counter."""
        log.info("Daily P&L reset | previous_pnl=%.2f", self._daily_pnl)
        self._daily_pnl   = 0.0
        self._trade_count = 0
        self.kill_switch_triggered = False
