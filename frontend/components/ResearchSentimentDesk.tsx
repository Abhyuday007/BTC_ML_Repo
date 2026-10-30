"use client";

import { useEffect, useState } from "react";
import { fetchBitcoinResearch } from "./api";
import type { ResearchItem, ResearchSnapshot } from "./types";

const channels = [
  { key: "news", label: "News" },
  { key: "reddit", label: "Reddit" },
  { key: "twitter", label: "X / Twitter" },
] as const;

export function ResearchSentimentDesk() {
  const [data, setData] = useState<ResearchSnapshot | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    const load = () => fetchBitcoinResearch().then((value) => {
      if (alive) { setData(value); setError(""); }
    }).catch(() => { if (alive) setError("Research service unavailable."); });
    load();
    const timer = window.setInterval(load, 30_000);
    return () => { alive = false; window.clearInterval(timer); };
  }, []);

  const score = data?.summary.index ?? 0;
  const moodColor = score > 15 ? "text-emerald-600" : score < -15 ? "text-rose-600" : "text-slate-600";
  return <section className="apple-card">
    <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-600">Read-only research</p>
        <h2 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">News & public sentiment</h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">Headline and public-post tone, kept separate from the trading engine. It never creates a buy/sell signal.</p>
      </div>
      <div className="rounded-2xl bg-slate-50 px-5 py-4 text-right ring-1 ring-slate-200">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">Sentiment index</p>
        <strong className={`mt-1 block text-3xl font-semibold ${moodColor}`}>{score > 0 ? "+" : ""}{score.toFixed(1)}</strong>
        <span className="text-sm capitalize text-slate-500">{data?.summary.label ?? "warming up"}</span>
      </div>
    </div>

    {error && <p className="mt-4 rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}

    <div className="mt-5 flex flex-wrap gap-2">
      {channels.map(({ key, label }) => {
        const status = data?.sources.find((source) => source.channel === key);
        return <span key={key} className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600">
          {label}: {status?.status ?? "starting"} · {data?.summary.by_channel[key] ?? 0} items
        </span>;
      })}
      <span className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-500">
        {data?.summary.sample_size ?? 0} posts/headlines scored
      </span>
    </div>
    <p className="mt-2 text-xs text-slate-400">
      {data?.updated_at ? `Last refreshed ${new Date(data.updated_at).toLocaleString()}` : "Collecting the first source snapshot…"}
    </p>

    {data?.sources.some((source) => source.status !== "ok" && source.status !== "empty") &&
      <p className="mt-3 text-xs leading-5 text-amber-700">
        {data.sources.filter((source) => source.status !== "ok" && source.status !== "empty").map((source) => `${source.channel}: ${source.error ?? source.status}`).join(" · ")}
      </p>}

    <div className="mt-6 grid gap-4 lg:grid-cols-3">
      {channels.map(({ key, label }) => <div key={key} className="rounded-3xl border border-slate-200 bg-white p-4">
        <h3 className="text-sm font-semibold text-slate-900">{label}</h3>
        <div className="mt-3 space-y-3">
          {(data?.items.filter((item) => item.channel === key).slice(0, 4) ?? []).map((item) => <ResearchCard key={item.id} item={item} />)}
          {!data?.items.some((item) => item.channel === key) && <p className="text-sm leading-6 text-slate-500">No public items are available yet. Check the source status above.</p>}
        </div>
      </div>)}
    </div>

    <div className="mt-5 rounded-3xl border border-blue-100 bg-blue-50/60 p-5">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="text-lg font-semibold text-slate-900">Trusted knowledge library</h3>
        <span className="text-xs text-slate-500">Primary technical and investor-education sources—not influencer predictions</span>
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {(data?.knowledge ?? []).map((source) => <a key={source.url} href={source.url} target="_blank" rel="noreferrer" className="rounded-2xl border border-white bg-white/90 p-4 transition hover:border-blue-200">
          <p className="text-xs font-medium uppercase tracking-wide text-blue-600">{source.topic}</p>
          <strong className="mt-1 block text-sm text-slate-900">{source.title}</strong>
          <span className="mt-1 block text-xs text-slate-500">{source.source}</span>
          <span className="mt-2 block text-sm leading-5 text-slate-600">{source.takeaway}</span>
        </a>)}
      </div>
    </div>

    <p className="mt-4 text-xs leading-5 text-slate-500">
      {data?.method} {data?.disclaimer} Source coverage is partial; social posts may be spam, coordinated, or wrong. Verify claims at the linked source.
    </p>
  </section>;
}

function ResearchCard({ item }: { item: ResearchItem }) {
  const sentimentColor = item.sentiment === "bullish" ? "text-emerald-600" : item.sentiment === "bearish" ? "text-rose-600" : "text-slate-500";
  return <article className="border-t border-slate-100 pt-3 first:border-0 first:pt-0">
    <div className="flex items-center justify-between gap-2 text-[11px] text-slate-400">
      <span className="truncate">{item.source}</span>
      <span className={`shrink-0 font-semibold uppercase ${sentimentColor}`}>{item.sentiment}</span>
    </div>
    <a href={item.url} target="_blank" rel="noreferrer" className="mt-1 block text-sm font-medium leading-5 text-slate-800 hover:text-blue-700">{item.title}</a>
    {item.text && <p className="mt-1 line-clamp-3 text-xs leading-5 text-slate-500">{item.text}</p>}
    {item.published_at && <time className="mt-1 block text-[11px] text-slate-400">{item.published_at}</time>}
  </article>;
}
