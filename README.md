# BTC Signal & Paper Trading Engine

An Apple-inspired dashboard for testing a BTC/USD momentum signal without connecting an exchange account.

## What runs without keys

- BTC/USD data from CoinGecko's public simple-price endpoint. It needs no API key.
- A compact momentum classifier that reports buy, sell, or hold with confidence and risk.
- An in-memory $10,000 paper wallet. Orders are local, instant, resettable, and never leave this app.
- A simulated-price fallback when the public provider is unavailable.
- CoinDesk headlines through its public RSS feed, with a transparent keyword-only sentiment score.
- Optional Reddit and X public-post search through the read-only Agent Reach CLI. The app never signs in for you; a platform may limit results or require you to connect a browser session.
- A small reference library linking to primary Bitcoin documentation and investor-education sources. It is curated, not exhaustive and not an investment-advice engine.

The official X API is not used: it currently charges per returned post. Reddit external Data API access can require approval. Social results come from Agent Reach public/read-only routes and the dashboard shows an unavailable status when those routes cannot provide content. This repository does not require API keys.

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
- `GET /api/btc/research` — cached headlines/posts, source status, heuristic sentiment, and linked learning references. The first request starts a background refresh; the refresh interval is 15 minutes.
- `POST /api/btc/orders` — local paper fill: `{ "side": "buy", "amount_usd": 250 }`.
- `POST /api/btc/reset` — restore the $10,000 test wallet.

The sentiment score is a small, explainable word-list heuristic—not a trained finance model. It is informational only and is never connected to order placement. Social posts can be spam, manipulated, or wrong. The app keeps the source-linked snapshot in memory only; it does not write collected post text to disk or forward it to other services.

## Live trading boundary

The current engine has **no live-trading code** and accepts no exchange credentials. That is intentional: it makes the demo safe to run and test. Exchange API keys themselves are normally free to create, but using them can create real-money orders and exchange fees. A future adapter must be separately enabled with explicit credentials, a testnet first, and hard risk limits.

## Requested tools

Agent Reach is a separate, user-level CLI rather than a project dependency. To enable social reads locally, install it and add its optional Reddit/X channels:

```bash
uv tool install https://github.com/Panniantong/Agent-Reach/releases/latest/download/agent-reach.zip
agent-reach setup
agent-reach add reddit
agent-reach add twitter
```

If a source asks for login, connect it yourself with `agent-reach login reddit` or `agent-reach login twitter`. The app never asks for passwords or logs in on your behalf. See [docs/agent-reach.md](docs/agent-reach.md) for details. Caveman's concise-response guidance is recorded in [`.codex/caveman.md`](.codex/caveman.md).
