# MEMORY-GUIDE.md — Knowledge Graph System

## Architecture
- `MEM` — Slim pointer file, read this first
- `memory/mocs/` — Maps of Content (topic indexes)
- `memory/notes/` — Atomic knowledge notes (permanent, wiki-linked)
- `memory/daily/` — Chronological session logs
- `memory/ops/observations/` — Things I learned (self-improvement)
- `memory/ops/tensions/` — Contradictions or outdated beliefs
- `memory/inbox/` — Unprocessed items

## Creating Notes

### Atomic Notes (memory/notes/)
- One idea per file
- Prose-titled filenames: `marcel-prefers-high-risk-investments.md` not `risk.md`
- YAML frontmatter required:
  ```yaml
  ---
  type: note
  description: "~150 char summary for scanning without opening"
  topics: ["[[moc-relevant-topic]]"]
  created: YYYY-MM-DD
  ---
  ```
- Use [[wiki-links]] to connect to other notes and MOCs
- Ask: "How will future-me find this?" before writing

### Daily Logs (memory/daily/)
- Named: `YYYY-MM-DD-topic.md` or `YYYY-MM-DD.md`
- Raw session activity, decisions, events
- Temporary — significant insights get extracted to notes/

### MOCs (memory/mocs/)
- Index files that link to related notes
- Update when adding notes to a topic area
- Hub MOC links to all other MOCs

### Observations (memory/ops/observations/)
- After significant actions, capture what you learned
- Format: `YYYY-MM-DD-short-description.md`
- Frontmatter: type, description, category (methodology|process|friction|surprise|quality), status (pending|promoted|implemented|archived)

### Tensions (memory/ops/tensions/)
- When new info contradicts existing notes
- Same format as observations
- Frontmatter: type, description, involves (links to conflicting notes), status (pending|resolved|dissolved)

## The Reduce/Reflect Cycle (Heartbeat Task)

### Reduce (daily → notes)
1. Scan recent daily/ files not yet processed
2. Extract significant insights, decisions, lessons
3. Create atomic notes in notes/
4. Link them to relevant MOCs

### Reflect (notes → connections)
1. Review recent notes
2. Find connections to existing notes (add wiki-links)
3. Update MOCs with new entries
4. Look for patterns or clusters that need a new MOC

### When to Reduce
- During heartbeats, every few days
- When daily/ has 5+ unprocessed files
- After significant project milestones

## Naming Conventions
- Notes: `topic-specific-description.md` (kebab-case, descriptive)
- Daily: `YYYY-MM-DD-topic.md`
- MOCs: `moc-topic-name.md`
- Observations: `YYYY-MM-DD-what-happened.md`
- Wiki links: `[[filename-without-extension]]`

## Rules
- Never delete notes — archive or update them
- One idea per note (atomic)
- Every note must be in at least one MOC
- Description field must differ from title
- Update MOCs when adding notes
