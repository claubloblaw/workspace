# Permit Profit Predictor

Cross-references building permits with property assessments to identify neighborhoods with high development activity that may see property value appreciation.

## What It Does

1. Pulls building permit data from Calgary Open Data
2. Pulls current property assessment data
3. Analyzes permit density and total value by community
4. Identifies communities with:
   - High permit velocity (lots of new construction)
   - Rising assessment values
   - Good ROI potential (permits vs current values)

## Why It's Interesting

This tool helps identify "hot" neighborhoods before they fully appreciate by tracking where developers are actively investing. High permit activity often precedes property value increases.

## Output

- `permit_hotspots.json` - Top communities ranked by development activity
- `permit_analysis.html` - Interactive visualization of permit density vs property values
- `investment_targets.csv` - Scored communities with investment potential

## Usage

```bash
python main.py
```

## Data Sources

- Building Permits: `n4jq-68h8`
- Property Assessments: `4bsw-nn7w`
