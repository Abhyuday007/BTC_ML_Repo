"""Read-only public BTC research feeds and transparent keyword sentiment."""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import subprocess
import threading
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from urllib.parse import urlparse

REFRESH_SECONDS = 15 * 60
MAX_ITEMS = 10
AGENT_REACH = shutil.which("agent-reach")

POSITIVE = {
    "adoption", "approval", "bullish", "breakout", "buy", "gain", "gains",
    "green", "higher", "inflow", "inflows", "moon", "positive", " rally",
    "rebound", "surge", "upside", "upgrade", "strong", "support", "record high",
}
NEGATIVE = {
    "bearish", "ban", "crash", "decline", "dump", "fear", "hack", "hacked",
    "lawsuit", "liquidation", "low", "negative", "outflow", "outflows", "panic",
    "risk", "scam", "sell", "selloff", "short", "weak", "downside", "drop",
}

RSS_FEEDS = [
    {
        "name": "CoinDesk",
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    },
]

KNOWLEDGE_LIBRARY = [
    {
        "title": "Bitcoin white paper",
        "source": "Bitcoin.org · primary technical source",
        "url": "https://bitcoin.org/en/bitcoin-paper",
        "takeaway": "The original design describes a peer-to-peer electronic cash system. It explains the protocol design, not a trading strategy or price forecast.",
        "topic": "Protocol fundamentals",
    },
    {
        "title": "Bitcoin Developer Guide",
        "source": "Bitcoin Developer Documentation",
        "url": "https://developer.bitcoin.org/devguide/",
        "takeaway": "Technical reference for transactions, blocks, wallets, the peer-to-peer network, and how nodes validate data.",
        "topic": "Technical reference",
    },
    {
        "title": "Crypto Asset-Related Investments",
        "source": "Investor.gov · SEC Office of Investor Education",
        "url": "https://www.investor.gov/introduction-investing/investing-basics/investment-products/crypto-asset-related-investments",
        "takeaway": "Explains crypto-asset investment types and investor risks. It is educational material, not a BTC price signal.",
        "topic": "Risk and investor education",
    },
    {
        "title": "Social media and investment fraud",
        "source": "Investor.gov · SEC Office of Investor Education",
        "url": "https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-alerts/social-media-and-investment-fraud-investor-alert",
        "takeaway": "Social posts can be misleading or impersonated; verify claims and never treat popularity as proof.",
        "topic": "Source verification",
    },
]


class _TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _plain_text(value: str) -> str:
    parser = _TextOnly()
    parser.feed(value or "")
    return re.sub(r"\s+", " ", html.unescape(" ".join(parser.parts))).strip()


def _sentiment(text: str) -> dict:
    words = re.findall(r"[a-z]+", text.lower())
    joined = " " + " ".join(words) + " "
    bullish = sum(1 for term in POSITIVE if f" {term.strip()} " in joined)
    bearish = sum(1 for term in NEGATIVE if f" {term} " in joined)
    total = bullish + bearish
    score = (bullish - bearish) / total if total else 0.0
    label = "bullish" if score >= 0.2 else "bearish" if score <= -0.2 else "neutral"
    return {"label": label, "score": round(score, 3)}


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _child_text(element: ET.Element, name: str) -> str:
    for child in element.iter():
        if _local_name(child.tag) == name.lower() and child.text:
            return child.text.strip()
    return ""


def _date(value: str) -> str | None:
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat(timespec="seconds")
    except (TypeError, ValueError, OverflowError):
        return None


def _normalise_item(raw: dict, channel: str, fallback_source: str = "") -> dict | None:
    title = _plain_text(str(raw.get("title") or ""))[:240]
    body = _plain_text(str(raw.get("text") or raw.get("description") or raw.get("summary") or ""))[:700]
    url = str(raw.get("url") or raw.get("link") or "")
    if not (title or body) or urlparse(url).scheme not in {"http", "https"}:
        return None
    combined = f"{title} {body}"
    scored = _sentiment(combined)
    identity = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
    return {
        "id": identity,
        "channel": channel,
        "source": str(raw.get("source") or raw.get("author") or fallback_source or channel)[:120],
        "title": title or body[:180],
        "text": body,
        "url": url,
        "published_at": raw.get("published_at") or raw.get("created_at") or None,
        "sentiment": scored["label"],
        "sentiment_score": scored["score"],
    }


def _fetch_rss(feed: dict) -> tuple[list[dict], dict]:
    status = {"source": feed["name"], "channel": "news", "status": "ok", "error": None}
    try:
        req = urllib.request.Request(
            feed["url"], headers={"User-Agent": "BTC-Research-Dashboard/1.0 (RSS reader)"}
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            root = ET.fromstring(response.read(2_000_000))
        entries = [node for node in root.iter() if _local_name(node.tag) in {"item", "entry"}]
        items = []
        for entry in entries:
            title = _child_text(entry, "title")
            description = _child_text(entry, "description") or _child_text(entry, "summary")
            link = _child_text(entry, "link")
            if not link:
                for node in entry.iter():
                    if _local_name(node.tag) == "link":
                        link = node.attrib.get("href", "")
                        if link:
                            break
            item = _normalise_item({
                "title": title, "text": description, "url": link,
                "published_at": _date(_child_text(entry, "pubdate") or _child_text(entry, "published")),
            }, "news", feed["name"])
            if item and re.search(r"\b(bitcoin|btc|crypto|cryptocurrency)\b", (item["title"] + " " + item["text"]).lower()):
                items.append(item)
            if len(items) >= MAX_ITEMS:
                break
        status["count"] = len(items)
        return items, status
    except Exception as exc:
        status.update({"status": "unavailable", "error": f"{type(exc).__name__}: {exc}"[:240], "count": 0})
        return [], status


def _agent_reach(channel: str, query: str) -> tuple[list[dict], dict]:
    status = {"source": "Agent Reach", "channel": channel, "status": "unavailable", "error": None, "count": 0}
    if not AGENT_REACH:
        status["error"] = "agent-reach CLI is not installed; see README setup instructions."
        return [], status
    try:
        result = subprocess.run(
            [AGENT_REACH, channel, "search", query, "--limit", str(MAX_ITEMS), "--timeout", "20"],
            capture_output=True, text=True, timeout=25, check=False,
        )
        payload = json.loads(result.stdout.strip()) if result.stdout.strip() else {}
        if result.returncode != 0 or not payload.get("ok"):
            error = payload.get("error") or {}
            if isinstance(error, dict):
                reason = error.get("hint") or error.get("message") or error.get("code")
            else:
                reason = str(error)
            status["error"] = str(reason or result.stderr.strip() or "The public source returned no usable response.")[:240]
            status["status"] = str(error.get("code", "unavailable")).lower() if isinstance(error, dict) else "unavailable"
            return [], status
        raw_items = payload.get("items") or []
        items = []
        for raw in raw_items:
            if not isinstance(raw, dict):
                continue
            item = _normalise_item(raw, channel)
            if item:
                items.append(item)
            if len(items) >= MAX_ITEMS:
                break
        status.update({
            "status": "ok" if items else "empty",
            "source": str(payload.get("meta", {}).get("backend") or "Agent Reach public read")[:100],
            "count": len(items),
        })
        return items, status
    except subprocess.TimeoutExpired:
        status["error"] = "Agent Reach search timed out."
    except (OSError, ValueError, TypeError) as exc:
        status["error"] = f"{type(exc).__name__}: {exc}"[:240]
    return [], status


def _build_snapshot() -> dict:
    all_items: list[dict] = []
    sources = []
    for feed in RSS_FEEDS:
        items, status = _fetch_rss(feed)
        all_items.extend(items)
        sources.append(status)

    # Agent Reach is intentionally called sequentially and only reads public posts.
    for channel in ("reddit", "twitter"):
        query = 'Bitcoin OR BTC'
        items, status = _agent_reach(channel, query)
        all_items.extend(items)
        sources.append(status)

    deduped = {}
    for item in all_items:
        deduped[item["id"]] = item
    items = list(deduped.values())
    counts = {name: sum(item["channel"] == name for item in items) for name in ("news", "reddit", "twitter")}
    scores = [item["sentiment_score"] for item in items]
    avg = sum(scores) / len(scores) if scores else 0.0
    buckets = {label: sum(item["sentiment"] == label for item in items) for label in ("bullish", "neutral", "bearish")}
    return {
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "refresh_seconds": REFRESH_SECONDS,
        "method": "Transparent keyword lexicon; not a trained financial model.",
        "disclaimer": "Public sentiment is noisy and manipulable. It is not a buy/sell signal and never places or triggers orders.",
        "summary": {
            "index": round(avg * 100, 1),
            "label": "bullish" if avg >= 0.2 else "bearish" if avg <= -0.2 else "mixed / neutral",
            "sample_size": len(items), "by_channel": counts, "distribution": buckets,
        },
        "sources": sources,
        "items": sorted(items, key=lambda item: item.get("published_at") or "", reverse=True)[:30],
        "knowledge": KNOWLEDGE_LIBRARY,
    }


_lock = threading.Lock()
_cache = {
    "updated_at": None,
    "refresh_seconds": REFRESH_SECONDS,
    "method": "Transparent keyword lexicon; not a trained financial model.",
    "disclaimer": "Public sentiment is noisy and manipulable. It is not a buy/sell signal and never places or triggers orders.",
    "summary": {"index": 0.0, "label": "warming up", "sample_size": 0,
                "by_channel": {"news": 0, "reddit": 0, "twitter": 0},
                "distribution": {"bullish": 0, "neutral": 0, "bearish": 0}},
    "sources": [], "items": [], "knowledge": KNOWLEDGE_LIBRARY,
}
_refreshing = False


def _refresh_in_background() -> None:
    global _cache, _refreshing
    try:
        snapshot = _build_snapshot()
        with _lock:
            _cache = snapshot
    finally:
        with _lock:
            _refreshing = False


def get_research_snapshot() -> dict:
    global _refreshing
    with _lock:
        updated = _cache.get("updated_at")
        stale = not updated or time.time() - datetime.fromisoformat(updated).timestamp() >= REFRESH_SECONDS
        if stale and not _refreshing:
            _refreshing = True
            threading.Thread(target=_refresh_in_background, name="btc-research-refresh", daemon=True).start()
        return json.loads(json.dumps(_cache))
