# Reddit JSON trick unlocks free structured data

Append `.json` to any Reddit URL to get full structured data:
- `reddit.com/r/SaaS/hot.json?limit=25` → subreddit listing
- `reddit.com/r/SaaS/top.json?t=week&limit=25` → top posts by timeframe
- `reddit.com/r/sub/comments/{id}.json` → full thread with all replies to n-th depth

No API key needed. No rate limit issues (reasonable use). Full metadata: scores, timestamps, authors, awards.

## Why this is valuable
- Feed to LLMs for analysis at scale
- Extract patterns from niche subreddits (what's working, revenue numbers, pain points)
- Monitor specific communities for opportunities
- Build tools/services around this (content curation, market research, lead gen)

## Money angles
- Niche subreddit monitoring as a service
- AI-powered market research from Reddit data
- Content curation tools for specific industries
- Pain point extraction → build solutions people are asking for

Links to: [[context windows are the bottleneck]] (structured data is token-efficient)
