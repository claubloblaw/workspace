# Construction Boom Detector

Tracks construction permit velocity to identify neighborhoods experiencing rapid development.

## What It Does

1. Pulls building permit data with timestamps
2. Calculates permit issuance velocity (permits per month)
3. Tracks acceleration/deceleration in development
4. Identifies boom neighborhoods (rising permits)
5. Detects slowdowns (falling permits)

## Why It's Interesting

Permit velocity changes signal market shifts. Accelerating permits = growth. Slowing permits = market cooling.

## Output

- `construction_velocity.json` - Neighborhoods ranked by permit acceleration
- `boom_analysis.html` - Time-series charts
- `velocity_trends.csv` - Monthly permit trends by area

## Usage

```bash
python3 main.py
```

## Data Sources

- Building Permits: `kr8b-c44i`
