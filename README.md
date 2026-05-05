# ⚡ Sentinel-Poly — Polymarket Arbitrage Bot

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/MouradZaher/arbitrage-bot)

A production-grade **Polymarket CLOB arbitrage and liquidity farming bot** with a real-time Next.js dashboard.

---

## Architecture

```
arbitrage-bot/
├── bot/                        # Python arbitrage engine
│   ├── config.py               # Env vars & strategy constants
│   ├── logger.py               # Coloured console + rotating file logger
│   ├── clob_client.py          # Async Polymarket CLOB REST client
│   ├── risk_manager.py         # Kelly Criterion + kill-switch
│   ├── sentiment.py            # Tavily news sentiment engine
│   ├── market_maker.py         # Passive MM + circuit breaker
│   └── discovery_agent.py      # Main scan loop (entrypoint)
├── app/                        # Next.js 14 dashboard (Vercel)
│   ├── layout.tsx
│   ├── page.tsx                # Live dashboard UI
│   └── globals.css
├── lib/
│   └── mockData.ts             # Realistic demo data generator
├── .agent/skills/              # Antigravity skill files
├── .env.example                # ← copy to .env and fill in
├── requirements.txt
└── vercel.json
```

---

## Quick Start

### 1. Clone & configure

```bash
git clone https://github.com/MouradZaher/arbitrage-bot
cd arbitrage-bot
cp .env.example .env
# → edit .env with your keys
```

### 2. Run the discovery bot (Python)

```bash
pip install -r requirements.txt
python -m bot.discovery_agent --hours 1
```

The bot **only logs** opportunities — it does NOT place orders until you explicitly enable live mode.

### 3. Run the dashboard (Next.js)

```bash
npm install
npm run dev
# → open http://localhost:3000
```

---

## Strategy Modules

| Module | Purpose |
|--------|---------|
| **Scanner** | Polls `/price` and `/book` for top 20 markets every 30s |
| **Edge Detector** | Compares CLOB midpoint to Tavily news sentiment; flags >10% divergence |
| **Liquidity Bot** | Posts limit orders one tick inside best bid/ask to farm rewards |
| **Vegas Gap** | (Stub) Compares sportsbook implied probs to Polymarket mid |
| **Risk Manager** | Half-Kelly sizing, 2% per-trade cap, 5% daily drawdown kill-switch |
| **Circuit Breaker** | Cancels all orders if spread widens beyond 2% |

---

## Risk Management (Sentinel Protocol)

- **Kelly Criterion**: `f* = edge / odds × 0.5` (half-Kelly)
- **Hard cap**: max `$57` per trade (2% of `$2,850`)
- **Kill switch**: auto-cancel all orders at `$142.50` daily loss (5%)
- **Circuit breaker**: spread > 2% → immediate cancel
- **Limit orders only**: no market orders, ever

---

## Environment Variables

| Key | Description |
|-----|-------------|
| `POLYGON_RPC` | Alchemy/Infura Polygon RPC URL |
| `PRIVATE_KEY` | Bot wallet private key (dedicated wallet only) |
| `POLY_API_KEY` | Polymarket CLOB API key |
| `POLY_API_SECRET` | Polymarket CLOB API secret |
| `POLY_API_PASSPHRASE` | Polymarket CLOB passphrase |
| `TAVILY_API_KEY` | Tavily search API key for news sentiment |
| `CAPITAL_USDC` | Total capital (default: 2850) |

---

## Security

> 🔐 **NEVER commit your `.env` file.** It's in `.gitignore`.
> Use a **dedicated bot wallet** with only the capital you intend to deploy.
> The first run requires an `approve()` transaction for the Polymarket CTF contract.

---

## Dashboard

The Next.js dashboard provides:
- Live stat cards (capital, P&L, drawdown, trade count)
- 48-hour cumulative P&L chart
- Per-scan bar chart
- Filterable opportunity table with Kelly sizing and projected ROI
- Signal distribution breakdown
- Kill-switch status panel

Deploy to Vercel in one click via the button above.

---

## Disclaimer

This software is for **educational purposes only**. Prediction markets carry significant risk. Past performance does not guarantee future results. Never risk capital you cannot afford to lose.
