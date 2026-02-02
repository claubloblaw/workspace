# RULES.md - Mistakes & Lessons Learned

*Don't repeat mistakes. When something goes wrong, document it here so future-you learns from it.*

## Process Rules

### 1. Be Proactive About Context Window
- **Don't let compaction sneak up on you.** Monitor context usage and serialize important state to files BEFORE hitting limits.
- When a session gets long, periodically flush key context to `daily/` or `memory/` files.
- Summarize ongoing work state to a scratch file so compaction doesn't wipe critical context.
- **Every 10-15 exchanges in a long session**: write a state checkpoint to `memory/YYYY-MM-DD.md` with:
  - What we're working on
  - Key decisions made
  - Current state / next steps
  - Any important details that would be painful to lose
- Clawdbot has a built-in pre-compaction memory flush, but it only fires once near the limit — don't rely on it alone.
- Use `/compact` proactively with good instructions rather than letting auto-compaction summarize blindly.

### 2. Write It Down Immediately
- If Marcel says "remember this" or makes a decision → write to file THAT TURN, not later.
- Don't rely on conversation history persisting. It won't.

### 3. Don't Ask What You Can Figure Out
- Check files, search, read context before asking Marcel to repeat himself.
- Post-compaction: check memory files and recent daily notes before asking "what were we doing?"

### 3. Minimize Gateway Restarts
- **Batch config changes** into a single `config.patch` instead of multiple patches.
- **Never restart mid-conversation** without warning Marcel first.
- **Don't restart to "fix" things** — diagnose first. The issue is usually something else (indexing, cache, etc).
- **Schedule updates for off-hours** — npm installs + restarts belong in cron jobs, not active sessions.
- Each restart = brief outage + potential "missing tool result" transcript corruption.

### 4. Prefer Local File Operations Over API Calls
- **Cache API results locally** when data doesn't change frequently (e.g., save search results, fetched pages, or API responses to files).
- **Read from local files first** before hitting external APIs — check if the data already exists in the workspace.
- **Batch operations** — don't make 10 separate API calls when 1 call or a local scan will do.
- **Store reusable data** in workspace files (e.g., `memory/`, `cache/`, project dirs) to avoid re-fetching.
- This saves tokens, reduces latency, and avoids rate limits.

### 5. Bug Fixing: Test First, Then Fix
- **Don't jump to fixing.** When you find a bug, first write a test that reproduces it.
- Spawn a sub-agent to attempt the fix, with the failing test as the success criterion.
- The bug isn't fixed until the test passes. No "I think this should work" — prove it.

## Technical Lessons

### WordPress / WP-CLI
- `WP_DEBUG_DISPLAY` should be `false` on production/staging — log errors, don't show them to visitors.
- Always flush transients after removing plugins (stale references cause frontend errors).
- WPMU DEV hosting includes backups — UpdraftPlus is redundant there.

## Social / Communication
- Don't say the same thing twice when Marcel repeats info (he may have forgotten he told you, just acknowledge briefly).
- In group chats: quality > quantity. React don't reply when that's sufficient.
- **Don't ask for info you've been told before.** If compaction wiped it, check MEM/memory files first. Marcel noticed when I forgot his GitHub username.

---

*Add to this file whenever something goes wrong or a lesson is learned.*
