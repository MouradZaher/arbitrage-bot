"""
Sentinel-Poly | Config & Constants
Loads environment variables and validates critical settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Blockchain ──────────────────────────────────────────────
POLYGON_RPC      = os.getenv("POLYGON_RPC", "")
PRIVATE_KEY      = os.getenv("PRIVATE_KEY", "")

# ── Polymarket CLOB API ──────────────────────────────────────
CLOB_BASE        = "https://clob.polymarket.com"
POLY_API_KEY     = os.getenv("POLY_API_KEY", "")
POLY_API_SECRET  = os.getenv("POLY_API_SECRET", "")
POLY_API_PASS    = os.getenv("POLY_API_PASSPHRASE", "")

# ── Tavily ───────────────────────────────────────────────────
TAVILY_API_KEY   = os.getenv("TAVILY_API_KEY", "")

# ── Strategy ─────────────────────────────────────────────────
CAPITAL_USDC          = float(os.getenv("CAPITAL_USDC", "2850"))
MAX_RISK_PCT          = float(os.getenv("MAX_RISK_PCT", "0.02"))
DRAWDOWN_KILL_PCT     = float(os.getenv("DRAWDOWN_KILL", "0.05"))
SPREAD_CIRCUIT_PCT    = float(os.getenv("SPREAD_CIRCUIT_PCT", "0.02"))
DIVERGENCE_THRESHOLD  = float(os.getenv("DIVERGENCE_THRESHOLD", "0.10"))
TOP_MARKETS           = int(os.getenv("TOP_MARKETS", "20"))

# ── Computed limits ──────────────────────────────────────────
MAX_POSITION_USDC  = CAPITAL_USDC * MAX_RISK_PCT   # $57 per trade
KILL_SWITCH_LOSS   = CAPITAL_USDC * DRAWDOWN_KILL_PCT  # $142.50 daily

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
