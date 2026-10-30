import type { BitcoinState } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function fetchBitcoinState(): Promise<BitcoinState> { return request("/api/btc/state"); }
export function placeBitcoinOrder(side: "buy" | "sell", amount_usd: number): Promise<BitcoinState> {
  return request("/api/btc/orders", { method: "POST", body: JSON.stringify({ side, amount_usd }) });
}
export function resetBitcoinAccount(): Promise<BitcoinState> { return request("/api/btc/reset", { method: "POST" }); }
