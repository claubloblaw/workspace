# Transit Development Radar

Tracks development permits near transit stations and LRT lines to predict property appreciation and development trends.

## What It Does

1. Pulls development permit data
2. Pulls transit station locations and LRT routes
3. Maps permits within 500m, 1km of transit
4. Tracks transit-oriented development (TOD) velocity
5. Identifies emerging TOD corridors

## Why It's Interesting

Properties near transit appreciate faster. High permit activity near new/upgraded transit = early signal of neighborhood transformation.

## Output

- `tod_hotspots.json` - Transit corridors ranked by development activity
- `transit_development_map.html` - Interactive map
- `tod_analysis.csv` - Permit counts and values by station

## Usage

```bash
python3 main.py
```

## Data Sources

- Development Permits: `6933-unw5`
- LRT Stations: `2axz-c3aj`
- CTrain Routes: `4tx8-r5pk`
