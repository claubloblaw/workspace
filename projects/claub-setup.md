# Claub (Clawdbot/OpenClaw) Setup & Improvement
**Status:** Active (ongoing)
**Started:** 2026-01-25
**Goal:** Fully operational AI assistant — reliable, proactive, well-integrated with tools.

## Context
Personal AI assistant running OpenClaw on Mac VM. Telegram as primary channel. Building out tools, memory, and workflows.

## Current State
- OpenClaw 2026.1.30 (updated from clawdbot)
- Telegram: working
- GitHub: authed as claubloblaw, repo at clawd-workspace (clean)
- X/Twitter: bird CLI works via env var wrapper (bird-auth), config file parsing broken
- Memory search: local embeddings (embeddinggemma-300M), indexing
- TTS: ElevenLabs configured
- Whisper: local speech-to-text
- Nightly crons: X digest (3 AM), git push (11 PM)

## Next Steps
- [ ] Configure Brave Search API key (web_search tool broken without it)
- [ ] Find X post about context serialization strategies
- [ ] Verify memory search index is fully built and returning results
- [ ] Set up email checking (Outlook via himalaya or browser)
- [ ] Set up calendar integration
- [ ] Explore experimental session memory search

## Log
- 2026-01-25: Initial setup, Opus model switch
- 2026-02-01: RULES.md, MEM, GitHub repo (clean), OpenClaw update, bird fix, local embeddings, projects/ folder
