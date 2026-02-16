#!/usr/bin/env python3
"""
Permit Profit Predictor
Analyzes building permits vs property values to find investment opportunities
"""

import requests
import pandas as pd
import json
from collections import defaultdict
from datetime import datetime, timedelta

# Calgary Open Data API endpoints
PERMITS_ENDPOINT = "https://data.calgary.ca/resource/c2es-76ed.json"
ASSESSMENTS_ENDPOINT = "https://data.calgary.ca/resource/4bsw-nn7w.json"

def fetch_data(endpoint, limit=50000):
    """Fetch data from Calgary Open Data API"""
    print(f"Fetching data from {endpoint}...")
    response = requests.get(f"{endpoint}?$limit={limit}")
    response.raise_for_status()
    return response.json()

def analyze_permits_by_community(permits_data):
    """Analyze building permit activity by community"""
    community_stats = defaultdict(lambda: {
        'permit_count': 0,
        'total_value': 0,
        'permits': []
    })
    
    for permit in permits_data:
        community = permit.get('communityname', 'Unknown')
        if community == 'Unknown':
            continue
            
        # Get permit value (estimate if not available)
        value = float(permit.get('estprojectcost', 0))
        
        community_stats[community]['permit_count'] += 1
        community_stats[community]['total_value'] += value
        community_stats[community]['permits'].append({
            'type': permit.get('workclassgroup', 'Unknown'),
            'value': value,
            'date': permit.get('applieddate', '')
        })
    
    return dict(community_stats)

def analyze_assessments_by_community(assessments_data):
    """Analyze property values by community"""
    community_values = defaultdict(lambda: {
        'property_count': 0,
        'total_assessed_value': 0,
        'avg_value': 0
    })
    
    for assessment in assessments_data:
        community = assessment.get('comm_name', 'Unknown')
        if community == 'Unknown':
            continue
        
        # Get total assessed value
        assessed_value = float(assessment.get('assessed_value', 0))
        
        community_values[community]['property_count'] += 1
        community_values[community]['total_assessed_value'] += assessed_value
    
    # Calculate averages
    for community in community_values:
        if community_values[community]['property_count'] > 0:
            community_values[community]['avg_value'] = (
                community_values[community]['total_assessed_value'] / 
                community_values[community]['property_count']
            )
    
    return dict(community_values)

def score_communities(permit_stats, assessment_stats):
    """Score communities based on development activity and property values"""
    scored_communities = []
    
    for community in permit_stats:
        if community not in assessment_stats:
            continue
        
        permits = permit_stats[community]
        values = assessment_stats[community]
        
        # Skip communities with no meaningful data
        if permits['permit_count'] < 3 or values['property_count'] < 10:
            continue
        
        # Calculate metrics
        permit_density = permits['permit_count'] / values['property_count'] if values['property_count'] > 0 else 0
        investment_ratio = permits['total_value'] / values['total_assessed_value'] if values['total_assessed_value'] > 0 else 0
        avg_permit_value = permits['total_value'] / permits['permit_count'] if permits['permit_count'] > 0 else 0
        
        # Score (higher = more interesting)
        # Weight permit density highly, investment ratio moderately
        score = (permit_density * 100) + (investment_ratio * 50)
        
        scored_communities.append({
            'community': community,
            'score': round(score, 2),
            'permit_count': permits['permit_count'],
            'total_permit_value': round(permits['total_value'], 2),
            'avg_permit_value': round(avg_permit_value, 2),
            'property_count': values['property_count'],
            'avg_property_value': round(values['avg_value'], 2),
            'permit_density': round(permit_density * 100, 2),  # permits per 100 properties
            'investment_ratio': round(investment_ratio * 100, 2)  # permit value as % of total value
        })
    
    # Sort by score descending
    scored_communities.sort(key=lambda x: x['score'], reverse=True)
    
    return scored_communities

def generate_html_report(scored_communities):
    """Generate an HTML visualization"""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Calgary Permit Profit Predictor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        h1 { color: #d32f2f; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th { background: #d32f2f; color: white; padding: 12px; text-align: left; }
        td { padding: 10px; border-bottom: 1px solid #ddd; }
        tr:hover { background: #f9f9f9; }
        .score { font-weight: bold; color: #d32f2f; font-size: 1.2em; }
        .metric { color: #666; font-size: 0.9em; }
        .top-pick { background: #fff3e0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏗️ Calgary Permit Profit Predictor</h1>
        <p><strong>Generated:</strong> """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        <p>Communities ranked by development activity and investment potential.</p>
        
        <h2>Top Investment Targets</h2>
        <table>
            <tr>
                <th>Rank</th>
                <th>Community</th>
                <th>Score</th>
                <th>Permits</th>
                <th>Avg Permit Value</th>
                <th>Properties</th>
                <th>Permit Density</th>
                <th>Investment Ratio</th>
            </tr>
"""
    
    for idx, community in enumerate(scored_communities[:30], 1):
        row_class = 'top-pick' if idx <= 10 else ''
        html += f"""
            <tr class="{row_class}">
                <td><strong>{idx}</strong></td>
                <td><strong>{community['community']}</strong></td>
                <td class="score">{community['score']}</td>
                <td>{community['permit_count']}</td>
                <td>${community['avg_permit_value']:,.0f}</td>
                <td>{community['property_count']}</td>
                <td class="metric">{community['permit_density']} per 100</td>
                <td class="metric">{community['investment_ratio']}%</td>
            </tr>
"""
    
    html += """
        </table>
        <p style="color: #666; font-size: 0.9em;">
            <strong>Score:</strong> Higher = more development activity<br>
            <strong>Permit Density:</strong> Number of permits per 100 properties<br>
            <strong>Investment Ratio:</strong> Total permit value as % of total assessed value
        </p>
    </div>
</body>
</html>
"""
    
    return html

def main():
    print("=" * 60)
    print("PERMIT PROFIT PREDICTOR")
    print("=" * 60)
    
    # Fetch data
    print("\n[1/4] Fetching building permits...")
    permits = fetch_data(PERMITS_ENDPOINT, limit=50000)
    print(f"   ✓ Loaded {len(permits)} permits")
    
    print("\n[2/4] Fetching property assessments...")
    assessments = fetch_data(ASSESSMENTS_ENDPOINT, limit=50000)
    print(f"   ✓ Loaded {len(assessments)} assessments")
    
    # Analyze
    print("\n[3/4] Analyzing data...")
    permit_stats = analyze_permits_by_community(permits)
    assessment_stats = analyze_assessments_by_community(assessments)
    scored = score_communities(permit_stats, assessment_stats)
    print(f"   ✓ Analyzed {len(scored)} communities")
    
    # Save outputs
    print("\n[4/4] Generating outputs...")
    
    # JSON
    with open('permit_hotspots.json', 'w') as f:
        json.dump(scored[:50], f, indent=2)
    print("   ✓ Saved permit_hotspots.json")
    
    # CSV
    df = pd.DataFrame(scored[:50])
    df.to_csv('investment_targets.csv', index=False)
    print("   ✓ Saved investment_targets.csv")
    
    # HTML
    html = generate_html_report(scored)
    with open('permit_analysis.html', 'w') as f:
        f.write(html)
    print("   ✓ Saved permit_analysis.html")
    
    # Print summary
    print("\n" + "=" * 60)
    print("TOP 10 INVESTMENT TARGETS")
    print("=" * 60)
    for idx, community in enumerate(scored[:10], 1):
        print(f"{idx:2d}. {community['community']:30s} Score: {community['score']:7.2f} | "
              f"{community['permit_count']:3d} permits | "
              f"Density: {community['permit_density']:.1f}/100")
    
    print("\n✅ Analysis complete! Check the output files.")

if __name__ == "__main__":
    main()
