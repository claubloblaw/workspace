#!/usr/bin/env python3
"""
Crime-Value Arbitrage Finder
Identifies mispriced neighborhoods based on crime vs property values
"""

import requests
import pandas as pd
import json
from collections import defaultdict

BASE_URL = "https://data.calgary.ca/resource"

def fetch_data(dataset_id, limit=50000):
    """Fetch data from Calgary Open Data API"""
    url = f"{BASE_URL}/{dataset_id}.json?$limit={limit}"
    print(f"Fetching {dataset_id}...")
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.json()

def create_community_mapping(demographics_data):
    """Create mapping from community code to community name"""
    mapping = {}
    for record in demographics_data:
        code = record.get('comm_code', '')
        name = record.get('name', '')
        if code and name:
            mapping[code] = name
    return mapping

def main():
    print("🚨 Crime-Value Arbitrage Finder")
    print("=" * 60)
    
    # Fetch demographics first to get community code mapping
    print("\n📊 Fetching demographics...")
    demographics = fetch_data("rkfr-buzb", limit=1000)
    print(f"   Found {len(demographics)} demographic records")
    
    # Create community code to name mapping
    comm_mapping = create_community_mapping(demographics)
    print(f"   Mapped {len(comm_mapping)} community codes")
    
    # Fetch crime statistics
    print("\n🚔 Fetching crime statistics...")
    crime = fetch_data("78gh-n26t", limit=20000)
    print(f"   Found {len(crime)} crime records")
    
    # Fetch property assessments
    print("\n🏘️  Fetching property assessments...")
    properties = fetch_data("4bsw-nn7w", limit=50000)
    print(f"   Found {len(properties)} property records")
    
    # Process crime data by community code, then map to names
    df_crime = pd.DataFrame(crime)
    crime_by_code = defaultdict(float)
    
    if 'community' in df_crime.columns and 'crime_count' in df_crime.columns:
        df_crime['crime_count'] = pd.to_numeric(df_crime['crime_count'], errors='coerce').fillna(0)
        
        # Filter for recent years (2020+)
        if 'year' in df_crime.columns:
            df_crime['year'] = pd.to_numeric(df_crime['year'], errors='coerce')
            recent_crime = df_crime[df_crime['year'] >= 2020]
        else:
            recent_crime = df_crime
        
        # Sum crimes by community code
        crime_by_code = recent_crime.groupby('community')['crime_count'].sum().to_dict()
    
    # Map crime counts from codes to community names
    crime_by_community = {}
    for code, count in crime_by_code.items():
        name = comm_mapping.get(code, code)  # Use code itself if no mapping found
        crime_by_community[name] = crime_by_community.get(name, 0) + count
    
    print(f"   Processed crime data for {len(crime_by_community)} communities")
    
    # Process property data
    df_prop = pd.DataFrame(properties)
    df_prop['assessed_value'] = pd.to_numeric(df_prop.get('assessed_value', 0), errors='coerce')
    
    # Calculate median assessed value and count by community
    median_values = df_prop.groupby('comm_name')['assessed_value'].median().to_dict()
    prop_counts = df_prop.groupby('comm_name').size().to_dict()
    
    print(f"   Processed property data for {len(median_values)} communities")
    
    # Combine data
    results = []
    all_communities = set(list(crime_by_community.keys()) + list(median_values.keys()))
    
    for community in all_communities:
        crime_count = crime_by_community.get(community, 0)
        median_value = median_values.get(community, 0)
        prop_count = prop_counts.get(community, 0)
        
        if median_value == 0 or prop_count < 10:
            continue
        
        # Calculate crime rate per 100 properties
        crime_rate = (crime_count / prop_count * 100) if prop_count > 0 else 0
        
        # Arbitrage score: combines value and crime rate
        # Negative score = good buy (low crime, low/reasonable price)
        # Positive score = overvalued (high crime or high price)
        value_norm = median_value / 500000  # Normalize around 500k
        crime_norm = crime_rate / 5  # Normalize around 5 per 100
        
        arbitrage_score = crime_norm - value_norm  # Negative = undervalued safety
        
        # Signal logic:
        # BUY: Low crime + reasonable/low price (arbitrage < -0.5)
        # SELL: High crime + high price (arbitrage > 0.5)
        # HOLD: Everything else
        if arbitrage_score < -0.5:
            signal = 'BUY'
        elif arbitrage_score > 0.5:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        results.append({
            'community': community,
            'median_property_value': int(median_value),
            'crime_count': int(crime_count),
            'property_count': prop_count,
            'crime_rate_per_100': round(crime_rate, 2),
            'arbitrage_score': round(arbitrage_score, 3),
            'signal': signal
        })
    
    # Sort by arbitrage score (most negative = best opportunity)
    results_sorted = sorted(results, key=lambda x: x['arbitrage_score'])
    
    # Save results
    print("\n💾 Saving results...")
    
    with open('crime_value_analysis.json', 'w') as f:
        json.dump(results_sorted, f, indent=2)
    print("   ✓ Saved crime_value_analysis.json")
    
    df_results = pd.DataFrame(results_sorted)
    df_results.to_csv('investment_signals.csv', index=False)
    print("   ✓ Saved investment_signals.csv")
    
    # Generate HTML report
    html = generate_html_report(results_sorted)
    with open('arbitrage_map.html', 'w') as f:
        f.write(html)
    print("   ✓ Saved arbitrage_map.html")
    
    # Print top opportunities
    print("\n💎 TOP 10 UNDERVALUED (Low Crime, Reasonable Price - BUY SIGNALS)")
    print("=" * 95)
    buys = [r for r in results_sorted if r['signal'] == 'BUY'][:10]
    if buys:
        for i, r in enumerate(buys, 1):
            print(f"{i:2d}. {r['community']:<35} | Value: ${r['median_property_value']:>10,} | "
                  f"Crime/100: {r['crime_rate_per_100']:>5.2f} | Score: {r['arbitrage_score']:>6.3f}")
    else:
        print("   No strong BUY signals found (try adjusting threshold)")
    
    print("\n⚠️  TOP 10 OVERVALUED (High Crime or High Price - SELL/HOLD)")
    print("=" * 95)
    sells = [r for r in reversed(results_sorted) if r['arbitrage_score'] > 0][:10]
    if sells:
        for i, r in enumerate(sells, 1):
            print(f"{i:2d}. {r['community']:<35} | Value: ${r['median_property_value']:>10,} | "
                  f"Crime/100: {r['crime_rate_per_100']:>5.2f} | Score: {r['arbitrage_score']:>6.3f}")
    else:
        print("   No major SELL signals found")
    
    print("\n✅ Complete!")
    print(f"   📄 crime_value_analysis.json - Full analysis")
    print(f"   📄 investment_signals.csv - Buy/sell signals")
    print(f"   📄 arbitrage_map.html - Interactive visualization")

def generate_html_report(results):
    """Generate an HTML visualization"""
    
    # Separate by signal
    buys = [r for r in results if r['signal'] == 'BUY'][:20]
    sells = [r for r in results if r['signal'] == 'SELL'][:20]
    holds = [r for r in results if r['signal'] == 'HOLD'][:20]
    
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Calgary Crime-Value Arbitrage Finder</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #0a0a0a; 
            color: #e0e0e0;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: #1a1a1a; 
            padding: 30px; 
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.5);
        }
        h1 { 
            color: #ff5252; 
            margin-bottom: 10px;
            font-size: 2.2em;
        }
        h2 {
            color: #4fc3f7;
            border-bottom: 2px solid #4fc3f7;
            padding-bottom: 10px;
            margin-top: 40px;
        }
        .meta { 
            color: #999; 
            margin-bottom: 30px; 
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0; 
            background: #252525;
        }
        th { 
            background: #2c5aa0; 
            color: white; 
            padding: 14px; 
            text-align: left; 
            font-weight: 600;
        }
        td { 
            padding: 12px; 
            border-bottom: 1px solid #333; 
        }
        tr:hover { 
            background: #2a2a2a; 
        }
        .score { 
            font-weight: bold; 
            font-size: 1.1em; 
        }
        .buy { background: #1b5e20; }
        .sell { background: #b71c1c; }
        .buy-score { color: #4caf50; }
        .sell-score { color: #f44336; }
        .chart { 
            margin: 30px 0; 
            background: #252525; 
            padding: 20px; 
            border-radius: 8px;
        }
        .metric-card {
            display: inline-block;
            background: #2a2a2a;
            padding: 15px 25px;
            margin: 10px;
            border-radius: 8px;
            border-left: 4px solid #ff5252;
        }
        .metric-value {
            font-size: 2em;
            color: #ff5252;
            font-weight: bold;
        }
        .metric-label {
            color: #999;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚨 Calgary Crime-Value Arbitrage Finder</h1>
        <p class="meta">
            <strong>Analysis Date:</strong> """ + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + """<br>
            <strong>Methodology:</strong> Identifies neighborhoods where property values don't align with crime rates<br>
            <strong>BUY Signal:</strong> Low crime + reasonable/low price (undervalued safety)<br>
            <strong>SELL Signal:</strong> High crime + high price (overvalued risk)
        </p>
        
        <div class="metric-card">
            <div class="metric-value">""" + str(len(results)) + """</div>
            <div class="metric-label">Communities Analyzed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">""" + str(len(buys)) + """</div>
            <div class="metric-label">BUY Signals</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">""" + str(len(sells)) + """</div>
            <div class="metric-label">SELL Signals</div>
        </div>
        
        <h2>💎 Top BUY Opportunities (Undervalued Safety)</h2>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Community</th>
                    <th>Median Property Value</th>
                    <th>Crime Count</th>
                    <th>Crime Rate (per 100)</th>
                    <th>Arbitrage Score</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for idx, r in enumerate(buys, 1):
        html += f"""
                <tr class="buy">
                    <td><strong>{idx}</strong></td>
                    <td><strong>{r['community']}</strong></td>
                    <td>${r['median_property_value']:,}</td>
                    <td>{r['crime_count']}</td>
                    <td>{r['crime_rate_per_100']:.2f}</td>
                    <td class="score buy-score">{r['arbitrage_score']:.3f}</td>
                </tr>
"""
    
    if not buys:
        html += """
                <tr>
                    <td colspan="6" style="text-align: center; color: #999;">No strong BUY signals in current dataset</td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
        
        <h2>⚠️ Top SELL Warnings (Overvalued or High Risk)</h2>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Community</th>
                    <th>Median Property Value</th>
                    <th>Crime Count</th>
                    <th>Crime Rate (per 100)</th>
                    <th>Arbitrage Score</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for idx, r in enumerate(sells, 1):
        html += f"""
                <tr class="sell">
                    <td><strong>{idx}</strong></td>
                    <td><strong>{r['community']}</strong></td>
                    <td>${r['median_property_value']:,}</td>
                    <td>{r['crime_count']}</td>
                    <td>{r['crime_rate_per_100']:.2f}</td>
                    <td class="score sell-score">{r['arbitrage_score']:.3f}</td>
                </tr>
"""
    
    if not sells:
        html += """
                <tr>
                    <td colspan="6" style="text-align: center; color: #999;">No major SELL signals in current dataset</td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
        
        <div class="chart" id="scatterChart"></div>
        
        <h2>📊 All Communities</h2>
        <table>
            <thead>
                <tr>
                    <th>Community</th>
                    <th>Property Value</th>
                    <th>Crime Count</th>
                    <th>Properties</th>
                    <th>Crime/100</th>
                    <th>Score</th>
                    <th>Signal</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for r in results[:50]:
        row_class = 'buy' if r['signal'] == 'BUY' else ('sell' if r['signal'] == 'SELL' else '')
        score_class = 'buy-score' if r['signal'] == 'BUY' else ('sell-score' if r['signal'] == 'SELL' else '')
        html += f"""
                <tr class="{row_class}">
                    <td>{r['community']}</td>
                    <td>${r['median_property_value']:,}</td>
                    <td>{r['crime_count']}</td>
                    <td>{r['property_count']}</td>
                    <td>{r['crime_rate_per_100']:.2f}</td>
                    <td class="score {score_class}">{r['arbitrage_score']:.3f}</td>
                    <td><strong>{r['signal']}</strong></td>
                </tr>
"""
    
    # Prepare data for scatter plot
    communities = [r['community'] for r in results[:40]]
    values = [r['median_property_value'] for r in results[:40]]
    crime_rates = [r['crime_rate_per_100'] for r in results[:40]]
    scores = [r['arbitrage_score'] for r in results[:40]]
    signals = [r['signal'] for r in results[:40]]
    
    html += f"""
            </tbody>
        </table>
        
        <script>
            var trace = {{
                x: {values},
                y: {crime_rates},
                mode: 'markers+text',
                type: 'scatter',
                text: {communities},
                textposition: 'top center',
                textfont: {{ size: 8, color: '#999' }},
                marker: {{
                    size: 12,
                    color: {scores},
                    colorscale: [
                        [0, '#4caf50'],
                        [0.5, '#ffeb3b'],
                        [1, '#f44336']
                    ],
                    showscale: true,
                    cmin: -2,
                    cmax: 2,
                    colorbar: {{
                        title: 'Arbitrage Score',
                        titleside: 'right'
                    }}
                }},
                hovertemplate: '<b>%{{text}}</b><br>' +
                               'Value: $%{{x:,}}<br>' +
                               'Crime Rate: %{{y:.2f}}<br>' +
                               '<extra></extra>'
            }};
            
            var layout = {{
                title: 'Property Value vs Crime Rate<br><sub>Green = BUY | Yellow = HOLD | Red = SELL</sub>',
                xaxis: {{
                    title: 'Median Property Value ($)',
                    gridcolor: '#333',
                    color: '#e0e0e0',
                    type: 'log'
                }},
                yaxis: {{
                    title: 'Crime Rate (per 100 properties)',
                    gridcolor: '#333',
                    color: '#e0e0e0'
                }},
                paper_bgcolor: '#252525',
                plot_bgcolor: '#252525',
                font: {{
                    color: '#e0e0e0'
                }},
                hovermode: 'closest',
                height: 600
            }};
            
            Plotly.newPlot('scatterChart', [trace], layout);
        </script>
        
        <p style="color: #999; margin-top: 40px; font-size: 0.9em;">
            <strong>How to Read This:</strong><br>
            • <strong>Arbitrage Score:</strong> Negative = undervalued (good buy), Positive = overvalued (avoid/sell)<br>
            • <strong>BUY Signal:</strong> Low crime + reasonable price = potential investment opportunity<br>
            • <strong>SELL Signal:</strong> High crime or very high price relative to safety<br>
            • <strong>Crime Rate:</strong> Number of reported crimes per 100 properties (2020+ data)<br>
            • Chart uses log scale for property values to show full range
        </p>
    </div>
</body>
</html>
"""
    
    return html

if __name__ == "__main__":
    main()
