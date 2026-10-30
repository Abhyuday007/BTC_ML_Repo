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

export type ResearchItem = {
  id: string;
  channel: "news" | "reddit" | "twitter";
  source: string;
  title: string;
  text: string;
  url: string;
  published_at: string | null;
  sentiment: "bullish" | "neutral" | "bearish";
  sentiment_score: number;
};

export type ResearchSnapshot = {
  updated_at: string | null;
  refresh_seconds: number;
  method: string;
  disclaimer: string;
  summary: {
    index: number;
    label: string;
    sample_size: number;
    by_channel: Record<string, number>;
    distribution: Record<string, number>;
  };
  sources: { source: string; channel: string; status: string; error: string | null; count: number }[];
  items: ResearchItem[];
  knowledge: { title: string; source: string; url: string; takeaway: string; topic: string }[];
};
