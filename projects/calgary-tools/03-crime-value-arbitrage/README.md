# Crime-Value Arbitrage

Cross-references crime statistics with property values to identify potentially mispriced neighborhoods.

## What It Does

1. Pulls crime and disorder statistics by community
2. Pulls property assessment data
3. Analyzes crime rates vs median property values
4. Identifies neighborhoods with:
   - Low crime + low property values (undervalued)
   - High crime + high property values (overvalued)
   - Crime trend improvements (turnaround stories)

## Why It's Interesting

Market pricing doesn't always reflect current crime trends. Neighborhoods improving on crime but still priced low = opportunity. High-priced areas with rising crime = risk.

## Output

- `crime_value_analysis.json` - Communities ranked by value/crime arbitrage
- `arbitrage_map.html` - Interactive visualization
- `investment_signals.csv` - Buy/sell signals by neighborhood

## Usage

```bash
python3 main.py
```

## Data Sources

- Community Crime Statistics: `78gh-n26t`
- Property Assessments: `4bsw-nn7w`
- Community District Boundaries: `surr-xmvs`
