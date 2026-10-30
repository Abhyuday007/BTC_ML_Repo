---
name: agent-reach
description: Use Agent Reach as a read-only fallback for public web, GitHub, YouTube, Reddit, V2EX and other supported research channels when native search or reading is unavailable or incomplete.
metadata:
  homepage: https://github.com/Panniantong/Agent-Reach
  version: "1.6.0"
---

# Agent Reach

Use `agent-reach` for read-only research. Prefer built-in search and reading tools first. Reach is a fallback when those tools are unavailable, fail, or miss the requested content.

```bash
agent-reach channels
agent-reach <channel> <action> [args]
agent-reach read <url>
agent-reach doctor --text
```

Keep this project on free, keyless defaults. Do not enable login-backed channels, add credentials, or connect Reach to trading actions. Never post, comment, like, message, log in for the user, or request passwords/cookies.

When output has `ok: true`, use returned `items`. When `ok: false`, follow its `error.code` and `error.hint`; stop rather than retrying on login, rate-limit, site-block, or browser-busy errors.

Agent Reach's upstream skill is installed in the user environment. This repository copy records the project-specific scope and guardrails.
