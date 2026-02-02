# Ralph Loops — Autonomous Build Loop Skill

Source: https://x.com/spacepixel/status/2017892748737818756
ClawdHub: https://clawhub.ai/skills/ralph-loops
Date captured: 2026-02-01

## What It Is

An autonomous iteration loop for complex coding projects. Each cycle: read state → do one task → save progress → repeat. Clean context every iteration, so the agent never drowns in its own history.

## Key Concepts

- 💡 **Ralph Loops skill** — `clawhub install ralph-loops`. Full autonomous builder with interview → plan → build → done phases
- 💡 **Interview → Plan → Build workflow** — Structured phases: gather requirements, write specs, create numbered plan, execute autonomously
- 💡 **One task per iteration** — Hard constraint to prevent cascading breakage from touching too many files at once
- 💡 **File-based state (progress.md)** — Ground truth lives in files, not context window. Agent rereads state each iteration
- 💡 **Live dashboard** — Real-time monitoring UI (port 3939) with iteration count, token usage, cost, transcripts, kill switch
- 💡 **Backpressure patterns** — Tests and linting run between iterations so mistakes don't compound
- 💡 **RALPH_DONE signal** — Explicit completion signaling instead of ambiguous stopping

## When to Use

- Multi-hour autonomous builds (dashboards, APIs, refactors)
- Anything that would take 20+ iterations and blow up context
- Overnight builds — kick off, sleep, wake up to working code

## Typical Economics

| Complexity | Iterations | Cost | Time |
|---|---|---|---|
| Simple | ~10 | ~$0.50 | ~15 min |
| Medium | ~30 | $2–5 | 1–2 hrs |
| Complex | 100+ | $15–30 | 4–8 hrs |

## Install When Ready

```bash
clawhub install ralph-loops
```
