export type BitcoinState = {
  mode: "paper";
  execution: string;
  market_data: string;
  price: number;
  history: number[];
  signal: { action: "BUY" | "SELL" | "HOLD"; confidence: number; up_probability: number; momentum_pct: number; risk: string };
  cash: number;
  btc: number;
  market_value: number;
  equity: number;
  pnl: number;
  orders: { id: string; side: "buy" | "sell"; amount_usd: number; btc_amount: number; price: number; filled_at: string }[];
};
