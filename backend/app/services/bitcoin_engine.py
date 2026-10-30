"""Keyless BTC market data plus a local paper-trading and signal-testing engine."""

from __future__ import annotations

import json
import math
import random
from datetime import UTC, datetime
from threading import Lock
from urllib.request import Request, urlopen
from uuid import uuid4


class BitcoinEngine:
    """Never routes an order externally. Live routing is deliberately not implemented here."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.cash = 10_000.0
        self.btc = 0.0
        self.average_cost = 0.0
        self.last_price = 68_000.0
        self.history = [67_520 + index * 18 + math.sin(index / 4) * 220 for index in range(48)]
        self.orders: list[dict] = []
        self.using_demo_feed = True

    def state(self) -> dict:
        with self._lock:
            self._refresh_price_locked()
            return self._state_locked()

    def order(self, side: str, amount_usd: float) -> dict:
        with self._lock:
            self._refresh_price_locked()
            if amount_usd < 10 or amount_usd > 10_000:
                raise ValueError("Order size must be between $10 and $10,000")
            btc_amount = amount_usd / self.last_price
            if side == "buy":
                if amount_usd > self.cash:
                    raise ValueError("Insufficient paper cash")
                total_cost = self.average_cost * self.btc + amount_usd
                self.btc += btc_amount
                self.average_cost = total_cost / self.btc
                self.cash -= amount_usd
            elif side == "sell":
                if btc_amount > self.btc:
                    raise ValueError("Insufficient paper BTC")
                self.btc -= btc_amount
                self.cash += amount_usd
                if self.btc < 0.00000001:
                    self.btc = 0.0
                    self.average_cost = 0.0
            else:
                raise ValueError("Order side must be buy or sell")
            self.orders.insert(0, {"id": uuid4().hex[:8], "side": side, "amount_usd": round(amount_usd, 2), "btc_amount": round(btc_amount, 8), "price": self.last_price, "filled_at": datetime.now(UTC).isoformat()})
            return self._state_locked()

    def reset(self) -> dict:
        with self._lock:
            self.cash, self.btc, self.average_cost, self.orders = 10_000.0, 0.0, 0.0, []
            return self._state_locked()

    def _refresh_price_locked(self) -> None:
        """CoinGecko's simple price endpoint is public and needs no API key."""
        try:
            request = Request("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", headers={"Accept": "application/json", "User-Agent": "BTC-ML-Demo/1.0"})
            with urlopen(request, timeout=3) as response:
                price = float(json.loads(response.read())["bitcoin"]["usd"])
            self.using_demo_feed = False
        except Exception:
            price = round(self.last_price * (1 + random.uniform(-0.0018, 0.0018)), 2)
            self.using_demo_feed = True
        self.last_price = price
        self.history = (self.history + [price])[-48:]

    def _signal_locked(self) -> dict:
        short = sum(self.history[-8:]) / 8
        long = sum(self.history[-24:]) / 24
        momentum = (short - long) / long
        volatility = max(0.001, sum(abs(self.history[index] / self.history[index - 1] - 1) for index in range(-12, 0)) / 12)
        probability = 1 / (1 + math.exp(-momentum / volatility * 0.35))
        if probability >= 0.56:
            action = "BUY"
        elif probability <= 0.44:
            action = "SELL"
        else:
            action = "HOLD"
        return {"action": action, "confidence": round(abs(probability - 0.5) * 200, 1), "up_probability": round(probability * 100, 1), "momentum_pct": round(momentum * 100, 3), "risk": "high" if volatility > 0.01 else "moderate"}

    def _state_locked(self) -> dict:
        market_value = self.btc * self.last_price
        equity = self.cash + market_value
        return {
            "mode": "paper", "execution": "local simulator", "market_data": "CoinGecko public feed" if not self.using_demo_feed else "demo fallback feed", "price": self.last_price,
            "history": [round(value, 2) for value in self.history], "signal": self._signal_locked(), "cash": round(self.cash, 2), "btc": round(self.btc, 8),
            "market_value": round(market_value, 2), "equity": round(equity, 2), "pnl": round(equity - 10_000, 2), "orders": self.orders[:8],
        }
