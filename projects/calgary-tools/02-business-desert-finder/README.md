# Business Desert Finder

Cross-references business licenses with population density to identify underserved neighborhoods with high population but low business presence.

## What It Does

1. Pulls active business license data from Calgary Open Data
2. Pulls population/demographic data by community
3. Calculates businesses per capita by neighborhood
4. Identifies "business deserts" - high population, low business density
5. Breaks down by business type (food, retail, services, etc.)

## Why It's Interesting

Helps entrepreneurs identify underserved markets and neighborhoods with unmet demand. High population + low business density = opportunity.

## Output

- `business_deserts.json` - Communities ranked by business-to-population ratio
- `desert_analysis.html` - Interactive map and charts
- `opportunities.csv` - Specific business type gaps by community

## Usage

```bash
python3 main.py
```

## Data Sources

- Business Licenses: `mhyc-r385`
- Community District Boundaries: `surr-xmvs`
- Civic Census by Community: `rkfr-buzb`
