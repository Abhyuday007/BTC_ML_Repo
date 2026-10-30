# Agent Reach integration boundary

Agent Reach is intentionally not bundled as an application runtime dependency. It is a user-level CLI that can provide read-only public search for Reddit and X, subject to each platform's availability and browser/session requirements.

The BTC research endpoint calls `agent-reach reddit search` and `agent-reach twitter search` sequentially, at most once per 15-minute refresh. It does not provide trading instructions to Agent Reach. Results are only used to render source-linked research and the local keyword sentiment estimate.

Install from the publisher's release, not PyPI:

```bash
uv tool install https://github.com/Panniantong/Agent-Reach/releases/latest/download/agent-reach.zip
agent-reach setup
```

Default channels are keyless. The external Reddit Data API may require approval for third-party apps, while X's official API is pay-per-use; this project uses neither official API. Agent Reach's public-web fallback can be incomplete or unavailable. If a platform requires a logged-in browser session, the user must connect it manually; the app will not open a login flow or collect credentials. Agent Reach is for read-only research context only; it never receives the BTC engine's wallet state or sends trading instructions.

Social results are cached in memory, not persisted. The adapter does not bypass CAPTCHAs, rate limits, login walls, or other access controls. Unavailable or empty results are shown as source status, not replaced with invented data.
