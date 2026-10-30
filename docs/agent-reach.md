# Agent Reach integration boundary

Agent Reach is intentionally not bundled as an application runtime dependency. It is a user-level CLI that adds free web, GitHub, V2EX, and selected social/video reading tools to an AI agent.

Agent Reach 1.6.0 and its generated user skill are installed in the local agent environment. The project-specific skill copy is at [`.agents/skills/agent-reach/SKILL.md`](../.agents/skills/agent-reach/SKILL.md). Its default channels are installed; optional account-backed channels remain unconfigured.

Install from the publisher's release, not PyPI:

```bash
uv tool install https://github.com/Panniantong/Agent-Reach/releases/latest/download/agent-reach.zip
agent-reach setup
```

Default channels are keyless. Do not enable login-backed channels or submit credentials for this project. Agent Reach is for research context only; it never receives the BTC engine's state or sends trading instructions.
