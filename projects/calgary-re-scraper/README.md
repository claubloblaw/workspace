# Calgary RE Deal Finder

Automated scraper for Realtor.ca targeting Calgary SW/SE quadrants.

## Search Profiles
1. **Walkout Bungalows** — $500K-$1.2M, 3+bed/2+bath houses, SW+SE Calgary
2. **Rental Yield** — $150K-$600K, all types, SW+SE Calgary

## Scoring Signals
- 🏛️ Judicial/foreclosure (+30)
- ⚰️ Estate sale (+20)
- 🔥 Motivated seller (+15)
- 📉 Price drop (+10-12)
- 📅 High DOM: 60d+ (+5), 90d+ (+10), 120d+ (+15)
- 🚪 Walkout basement (+25)
- 🌲 Backs nature/park (+15)
- 🏠 Suite potential (+10)
- 💰 Rental income (+25)
- 🏘️ Multi-unit (+20)
- 💎 Low $/bed (+8-15)
- 🚇 Transit/uni nearby (+10)

## How It Works
Uses Playwright connected to OpenClaw Chrome browser via CDP.
Navigates Realtor.ca, intercepts API responses during pagination.
Scores all listings and generates markdown summaries.

## Files
- `scrape.mjs` — Main scraper
- `data/latest-summary.md` — Most recent scan results
- `data/latest.json` — Raw listing data (for diff detection)
- `data/alerts.json` — New high-score listings

## Running
```bash
node scrape.mjs
```
Requires OpenClaw browser running on CDP port 18800.
