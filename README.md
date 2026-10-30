# BTC Signal & Paper Trading Engine

An Apple-inspired dashboard for testing a BTC/USD momentum signal without connecting an exchange account.

## What runs without keys

- BTC/USD data from CoinGecko's public simple-price endpoint. It needs no API key.
- A compact momentum classifier that reports buy, sell, or hold with confidence and risk.
- An in-memory $10,000 paper wallet. Orders are local, instant, resettable, and never leave this app.
- A simulated-price fallback when the public provider is unavailable.

This is a research/demo tool, not financial advice or a profitability claim.

## Run it

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-btc.txt
uvicorn btc_main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## API

- `GET /api/btc/state` — current price, model signal, history, wallet state.
- `POST /api/btc/orders` — local paper fill: `{ "side": "buy", "amount_usd": 250 }`.
- `POST /api/btc/reset` — restore the $10,000 test wallet.

## Live trading boundary

The current engine has **no live-trading code** and accepts no exchange credentials. That is intentional: it makes the demo safe to run and test. Exchange API keys themselves are normally free to create, but using them can create real-money orders and exchange fees. A future adapter must be separately enabled with explicit credentials, a testnet first, and hard risk limits.

## Requested tools

Agent Reach is a separate, user-level CLI rather than a project dependency. Its default web/GitHub channels are free and keyless; optional account-backed channels remain off. Caveman's concise-response guidance is recorded in [`.codex/caveman.md`](.codex/caveman.md).
