"""Small standalone API for the BTC-only paper-trading dashboard."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.services.bitcoin_engine import BitcoinEngine

app = FastAPI(title="BTC Signal & Paper Trading Engine", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
engine = BitcoinEngine()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/btc/state")
def get_btc_state() -> dict:
    return engine.state()


@app.post("/api/btc/orders")
def place_btc_paper_order(payload: dict) -> dict:
    try:
        return engine.order(str(payload.get("side", "")).lower(), float(payload.get("amount_usd", 0)))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/btc/reset")
def reset_btc_paper_account() -> dict:
    return engine.reset()
