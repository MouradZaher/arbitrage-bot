# Sentinel-Poly - Polymarket Arbitrage Bot

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/MouradZaher/arbitrage-bot)

A production-grade **Polymarket CLOB arbitrage and liquidity farming bot** with a real-time Next.js dashboard.

## Quick Start

```bash
git clone https://github.com/MouradZaher/arbitrage-bot
cd arbitrage-bot
cp .env.example .env
python -m bot.discovery_agent --hours 1
npm install && npm run dev
```

## Architecture

- bot/ - Python arbitrage engine (CLOB scanner, Kelly sizing, kill-switch)
- app/ - Next.js 14 real-time dashboard (Vercel-ready)
- lib/ - Shared utilities

## Disclaimer

Educational purposes only. Not financial advice.
