import { BitcoinTradingDesk } from "../components/BitcoinTradingDesk";
import { ResearchSentimentDesk } from "../components/ResearchSentimentDesk";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-7xl flex-col gap-8 px-4 py-8 md:px-8">
      <section className="apple-card hero-card overflow-hidden">
        <div className="grid gap-8 p-8 lg:grid-cols-[1.1fr_0.9fr] lg:p-10">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-blue-600">Bitcoin research lab</p>
            <h1 className="mt-4 max-w-3xl text-5xl font-semibold tracking-tight text-slate-950 md:text-6xl">
              Test the thesis. Not your capital.
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-7 text-slate-500">
              A clean BTC research workspace for a transparent signal model, public data, and safe paper execution.
            </p>
          </div>

          <div className="rounded-[2rem] border border-slate-200 bg-white/75 p-6 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">Flow</p>
            <div className="mt-5 space-y-3 text-sm text-slate-600">
              <div className="flow-step">1. Read BTC/USD from a public feed.</div>
              <div className="flow-step">2. Score momentum and risk.</div>
              <div className="flow-step">3. Validate with paper execution.</div>
            </div>
          </div>
        </div>
      </section>

      <BitcoinTradingDesk />
      <ResearchSentimentDesk />
    </main>
  );
}
