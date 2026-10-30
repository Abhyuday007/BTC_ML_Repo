#!/usr/bin/env python3
"""Public-data BTC/USDT SMA crossover paper session; never places exchange orders."""

from __future__ import annotations

import argparse
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://data-api.binance.vision/api/v3"
FEE = 0.0006
SLIPPAGE = 0.0002
ALLOCATION = 0.90


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def fetch(path: str):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "btc-paper-session/1.0"})
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.load(response)


def sma(values, window):
    return sum(values[-window:]) / window


class Session:
    def __init__(self, out: Path, initial: float):
        self.out = out
        self.out.mkdir(parents=True, exist_ok=True)
        self.state_path = out / "state.json"
        self.events_path = out / "events.jsonl"
        if self.state_path.exists():
            self.state = json.loads(self.state_path.read_text())
        else:
            now = time.time()
            self.state = {
                "mode": "PAPER_ONLY", "symbol": "BTCUSDT", "interval": "1h",
                "strategy": "SMA(8/24) long-only crossover", "started_at": utc_now(),
                "started_epoch": now, "ends_epoch": now + 86400, "initial_usd": initial,
                "cash_usd": initial, "btc": 0.0, "last_processed_close_ms": None,
                "peak_equity_usd": initial, "max_drawdown_pct": 0.0,
                "realized_pnl_usd": 0.0, "wins": 0, "closed_trades": 0,
                "errors": 0, "last_price": None, "last_updated": utc_now(),
            }
            self.save()
            self.event("session_started", {"initial_usd": initial, "duration_hours": 24})

    def event(self, kind, data):
        with self.events_path.open("a") as f:
            f.write(json.dumps({"at": utc_now(), "event": kind, **data}) + "\n")

    def save(self):
        self.state["last_updated"] = utc_now()
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, indent=2) + "\n")
        tmp.replace(self.state_path)

    def mark(self, price):
        s = self.state
        equity = s["cash_usd"] + s["btc"] * price
        s["last_price"] = price
        s["equity_usd"] = equity
        s["total_pnl_usd"] = equity - s["initial_usd"]
        s["total_return_pct"] = (equity / s["initial_usd"] - 1) * 100
        s["peak_equity_usd"] = max(s["peak_equity_usd"], equity)
        dd = (equity / s["peak_equity_usd"] - 1) * 100 if s["peak_equity_usd"] else 0
        s["max_drawdown_pct"] = min(s["max_drawdown_pct"], dd)

    def process(self, klines, price):
        closed = [k for k in klines if int(k[6]) < int(time.time() * 1000)]
        closes = [float(k[4]) for k in closed]
        if len(closes) < 25:
            raise RuntimeError("Not enough closed hourly candles for SMA(24) crossover")
        prev_close_ms = int(closed[-1][6])
        s = self.state
        if s["last_processed_close_ms"] != prev_close_ms:
            fast_now, slow_now = sma(closes, 8), sma(closes, 24)
            fast_prev, slow_prev = sma(closes[:-1], 8), sma(closes[:-1], 24)
            cross_up = fast_prev <= slow_prev and fast_now > slow_now
            cross_down = fast_prev >= slow_prev and fast_now < slow_now
            execution = price * (1 + SLIPPAGE if cross_up else 1 - SLIPPAGE)
            if cross_up and s["btc"] == 0:
                budget = s["cash_usd"] * ALLOCATION
                qty = budget / (execution * (1 + FEE))
                cost = qty * execution
                fee = cost * FEE
                s["cash_usd"] -= cost + fee
                s["btc"] = qty
                s["entry_price"] = execution
                s["entry_fee_usd"] = fee
                self.event("paper_buy", {"price": execution, "btc": qty, "fee_usd": fee,
                                          "signal_candle_close_ms": prev_close_ms})
            elif cross_down and s["btc"] > 0:
                qty = s["btc"]
                gross = qty * execution
                fee = gross * FEE
                proceeds = gross - fee
                pnl = proceeds - qty * s["entry_price"] - s.get("entry_fee_usd", 0)
                s["cash_usd"] += proceeds
                s["btc"] = 0.0
                s["realized_pnl_usd"] += pnl
                s["closed_trades"] += 1
                s["wins"] += int(pnl > 0)
                self.event("paper_sell", {"price": execution, "btc": qty, "fee_usd": fee,
                                           "trade_pnl_usd": pnl, "signal_candle_close_ms": prev_close_ms})
                s.pop("entry_price", None)
                s.pop("entry_fee_usd", None)
            s["last_processed_close_ms"] = prev_close_ms
            self.event("candle_processed", {"close_ms": prev_close_ms, "sma8": fast_now,
                                             "sma24": slow_now, "signal": "buy" if cross_up else "sell" if cross_down else "none"})
        self.mark(price)
        self.save()

    def finish(self):
        s = self.state
        s["finished_at"] = utc_now()
        s["status"] = "completed"
        s["win_rate_pct"] = s["wins"] / s["closed_trades"] * 100 if s["closed_trades"] else None
        self.event("session_finished", {k: s.get(k) for k in
                    ("equity_usd", "total_pnl_usd", "total_return_pct", "closed_trades", "max_drawdown_pct")})
        self.save()
        (self.out / "final-summary.json").write_text(json.dumps(s, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--initial-usd", type=float, default=1000)
    parser.add_argument("--poll-seconds", type=int, default=60)
    args = parser.parse_args()
    session = Session(args.out, args.initial_usd)
    while time.time() < session.state["ends_epoch"]:
        try:
            klines = fetch("/klines?symbol=BTCUSDT&interval=1h&limit=100")
            price = float(fetch("/ticker/price?symbol=BTCUSDT")["price"])
            session.process(klines, price)
            print(json.dumps({"at": utc_now(), "equity_usd": session.state.get("equity_usd"),
                              "price": price, "status": "running"}), flush=True)
        except Exception as exc:
            session.state["errors"] += 1
            session.state["last_error"] = f"{type(exc).__name__}: {exc}"
            session.event("data_error", {"error": session.state["last_error"]})
            session.save()
            print(f"{utc_now()} data error: {exc}", flush=True)
        time.sleep(args.poll_seconds)
    try:
        price = float(fetch("/ticker/price?symbol=BTCUSDT")["price"])
        session.mark(price)
    except Exception as exc:
        session.event("final_mark_error", {"error": str(exc)})
    session.finish()
    print(json.dumps(session.state, indent=2), flush=True)


if __name__ == "__main__":
    main()
