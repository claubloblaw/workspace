#!/usr/bin/env python3
"""
Business Desert Finder
Finds residential communities with high population but few commercial permits
(indicating potential underserved areas for business development)
"""

import requests
import pandas as pd
import json
from collections import defaultdict

# Calgary Open Data API endpoints
PERMITS_ENDPOINT = "https://data.calgary.ca/resource/c2es-76ed.json"
DEMOGRAPHICS_ENDPOINT = "https://data.calgary.ca/resource/rkfr-buzb.json"

def fetch_data(endpoint, limit=50000):
    """Fetch data from Calgary Open Data API"""
    print(f"Fetching data from {endpoint}...")
    response = requests.get(f"{endpoint}?$limit={limit}")
    response.raise_for_status()
    return response.json()

def analyze_commercial_permits(permits_data):
    """Count commercial/retail permits by community"""
    commercial_by_community = defaultdict(lambda: {
        'commercial_permits': 0,
        'total_permits': 0,
        'commercial_value': 0
    })
    
    # Commercial permit classes to look for
    commercial_keywords = ['commercial', 'retail', 'business', 'office', 'store', 'restaurant']
    
    for permit in permits_data:
        community = permit.get('communityname', 'Unknown')
        if community == 'Unknown':
            continue
        
        permit_class = str(permit.get('permitclassmapped', '')).lower()
        permit_type = str(permit.get('workclassmapped', '')).lower()
        
        # Check if it's a commercial permit
        is_commercial = any(kw in permit_class or kw in permit_type for kw in commercial_keywords)
        
        commercial_by_community[community]['total_permits'] += 1
        
        if is_commercial:
            commercial_by_community[community]['commercial_permits'] += 1
            value = float(permit.get('estprojectcost', 0))
            commercial_by_community[community]['commercial_value'] += value
    
    return dict(commercial_by_community)

def analyze_demographics(demographics_data):
    """Get population data by community"""
    community_pop = {}
    
    # Get most recent data for each community
    for record in demographics_data:
        community = record.get('name', 'Unknown')
        if community == 'Unknown':
            continue
        
        # Try to get resident count
        residents = record.get('res_cnt', record.get('resident_count', 0))
        try:
            residents = int(float(residents))
        except (ValueError, TypeError):
            residents = 0
        
        # Keep the highest population value for each community
        if community not in community_pop or residents > community_pop[community]:
            community_pop[community] = residents
    
    return community_pop

def find_business_deserts(permit_stats, population_stats):
    """Identify communities with high population but few commercial permits"""
    results = []
    
    for community in population_stats:
        population = population_stats[community]
        
        # Skip small communities
        if population < 500:
            continue
        
        # Get permit stats
        permits = permit_stats.get(community, {
            'commercial_permits': 0,
            'total_permits': 0,
            'commercial_value': 0
        })
        
        commercial_permits = permits['commercial_permits']
        total_permits = permits['total_permits']
        commercial_value = permits['commercial_value']
        
        # Calculate metrics
        commercial_permits_per_1k = (commercial_permits / population * 1000) if population > 0 else 0
        commercial_ratio = (commercial_permits / total_permits * 100) if total_permits > 0 else 0
        
        # Opportunity score: high population, low commercial activity
        # Higher score = bigger opportunity
        opportunity_score = (population / 1000) / (commercial_permits + 1)
        
        results.append({
            'community': community,
            'population': population,
            'commercial_permits': commercial_permits,
            'total_permits': total_permits,
            'commercial_value': round(commercial_value, 2),
            'commercial_permits_per_1k': round(commercial_permits_per_1k, 2),
            'commercial_ratio': round(commercial_ratio, 2),
            'opportunity_score': round(opportunity_score, 2)
        })
    
    # Sort by opportunity score (descending)
    results.sort(key=lambda x: x['opportunity_score'], reverse=True)
    
    return results

def generate_html_report(results):
    """Generate an HTML visualization"""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Calgary Business Desert Finder</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #1a1a1a; 
            color: #e0e0e0;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: #2a2a2a; 
            padding: 30px; 
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        h1 { 
            color: #4fc3f7; 
            margin-bottom: 10px;
        }
        h2 {
            color: #81c784;
            border-bottom: 2px solid #81c784;
            padding-bottom: 10px;
        }
        .meta { 
            color: #999; 
            margin-bottom: 30px; 
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0; 
            background: #333;
        }
        th { 
            background: #1565c0; 
            color: white; 
            padding: 14px; 
            text-align: left; 
            font-weight: 600;
        }
        td { 
            padding: 12px; 
            border-bottom: 1px solid #444; 
        }
        tr:hover { 
            background: #3a3a3a; 
        }
        .opportunity { 
            font-weight: bold; 
            color: #ff9800; 
            font-size: 1.1em; 
        }
        .high-opportunity { 
            background: #1b5e20; 
        }
        .chart { 
            margin: 30px 0; 
            background: #333; 
            padding: 20px; 
            border-radius: 8px;
        }
        .metric-card {
            display: inline-block;
            background: #424242;
            padding: 15px 25px;
            margin: 10px;
            border-radius: 8px;
            border-left: 4px solid #4fc3f7;
        }
        .metric-value {
            font-size: 2em;
            color: #4fc3f7;
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
        <h1>🏪 Calgary Business Desert Finder</h1>
        <p class="meta">
            <strong>Analysis Date:</strong> """ + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + """<br>
            <strong>Methodology:</strong> Identifies residential communities with high population but low commercial permit activity
        </p>
        
        <div class="metric-card">
            <div class="metric-value">""" + str(len(results)) + """</div>
            <div class="metric-label">Communities Analyzed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">""" + f"{sum(r['population'] for r in results):,}" + """</div>
            <div class="metric-label">Total Population</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">""" + str(sum(r['commercial_permits'] for r in results)) + """</div>
            <div class="metric-label">Commercial Permits</div>
        </div>
        
        <h2>Top 20 Business Opportunity Areas</h2>
        <p style="color: #999;">Communities with high population density but limited commercial development</p>
        
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Community</th>
                    <th>Population</th>
                    <th>Commercial Permits</th>
                    <th>Per 1,000 Residents</th>
                    <th>Commercial %</th>
                    <th>Opportunity Score</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for idx, result in enumerate(results[:20], 1):
        row_class = 'high-opportunity' if idx <= 5 else ''
        html += f"""
                <tr class="{row_class}">
                    <td><strong>{idx}</strong></td>
                    <td><strong>{result['community']}</strong></td>
                    <td>{result['population']:,}</td>
                    <td>{result['commercial_permits']}</td>
                    <td>{result['commercial_permits_per_1k']:.2f}</td>
                    <td>{result['commercial_ratio']:.1f}%</td>
                    <td class="opportunity">{result['opportunity_score']:.2f}</td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
        
        <div class="chart" id="scatterChart"></div>
        
        <h2>All Communities Analysis</h2>
        <table>
            <thead>
                <tr>
                    <th>Community</th>
                    <th>Population</th>
                    <th>Commercial Permits</th>
                    <th>Total Permits</th>
                    <th>Commercial Value ($)</th>
                    <th>Commercial Ratio</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for result in results[:50]:
        html += f"""
                <tr>
                    <td>{result['community']}</td>
                    <td>{result['population']:,}</td>
                    <td>{result['commercial_permits']}</td>
                    <td>{result['total_permits']}</td>
                    <td>${result['commercial_value']:,.0f}</td>
                    <td>{result['commercial_ratio']:.1f}%</td>
                </tr>
"""
    
    # Prepare data for scatter plot
    communities = [r['community'] for r in results[:30]]
    populations = [r['population'] for r in results[:30]]
    commercial_permits = [r['commercial_permits'] for r in results[:30]]
    opportunity_scores = [r['opportunity_score'] for r in results[:30]]
    
    html += f"""
            </tbody>
        </table>
        
        <script>
            var trace = {{
                x: {populations},
                y: {commercial_permits},
                mode: 'markers',
                type: 'scatter',
                text: {communities},
                marker: {{
                    size: {opportunity_scores},
                    color: {opportunity_scores},
                    colorscale: 'Viridis',
                    showscale: true,
                    sizemode: 'diameter',
                    sizeref: 0.5,
                    colorbar: {{
                        title: 'Opportunity Score'
                    }}
                }},
                hovertemplate: '<b>%{{text}}</b><br>' +
                               'Population: %{{x:,}}<br>' +
                               'Commercial Permits: %{{y}}<br>' +
                               '<extra></extra>'
            }};
            
            var layout = {{
                title: 'Population vs Commercial Development',
                xaxis: {{
                    title: 'Population',
                    gridcolor: '#444',
                    color: '#e0e0e0'
                }},
                yaxis: {{
                    title: 'Commercial Permits',
                    gridcolor: '#444',
                    color: '#e0e0e0'
                }},
                paper_bgcolor: '#333',
                plot_bgcolor: '#333',
                font: {{
                    color: '#e0e0e0'
                }},
                hovermode: 'closest'
            }};
            
            Plotly.newPlot('scatterChart', [trace], layout);
        </script>
        
        <p style="color: #999; margin-top: 40px; font-size: 0.9em;">
            <strong>Interpretation:</strong><br>
            • <strong>Opportunity Score:</strong> Higher values indicate communities with large populations but few commercial permits (potential underserved markets)<br>
            • <strong>Commercial Permits per 1,000:</strong> Number of commercial building permits per 1,000 residents<br>
            • <strong>Commercial Ratio:</strong> Percentage of all permits that are commercial/business-related<br>
            • Bubble size in chart represents opportunity score (larger = greater opportunity)
        </p>
    </div>
</body>
</html>
"""
    
    return html

def main():
    print("=" * 60)
    print("BUSINESS DESERT FINDER")
    print("=" * 60)
    
    # Fetch data
    print("\n[1/4] Fetching building permits...")
    permits = fetch_data(PERMITS_ENDPOINT, limit=50000)
    print(f"   ✓ Loaded {len(permits)} permits")
    
    print("\n[2/4] Fetching demographics...")
    demographics = fetch_data(DEMOGRAPHICS_ENDPOINT, limit=5000)
    print(f"   ✓ Loaded {len(demographics)} demographic records")
    
    # Analyze
    print("\n[3/4] Analyzing data...")
    permit_stats = analyze_commercial_permits(permits)
    population_stats = analyze_demographics(demographics)
    results = find_business_deserts(permit_stats, population_stats)
    print(f"   ✓ Analyzed {len(results)} communities")
    
    # Save outputs
    print("\n[4/4] Generating outputs...")
    
    # JSON
    with open('business_deserts.json', 'w') as f:
        json.dump(results[:30], f, indent=2)
    print("   ✓ Saved business_deserts.json")
    
    # CSV
    df = pd.DataFrame(results)
    df.to_csv('opportunities.csv', index=False)
    print("   ✓ Saved opportunities.csv")
    
    # HTML
    html = generate_html_report(results)
    with open('desert_analysis.html', 'w') as f:
        f.write(html)
    print("   ✓ Saved desert_analysis.html")
    
    # Print summary
    print("\n" + "=" * 60)
    print("TOP 10 BUSINESS DESERT CANDIDATES")
    print("=" * 60)
    for idx, result in enumerate(results[:10], 1):
        print(f"{idx:2d}. {result['community']:30s} | "
              f"Pop: {result['population']:>6,} | "
              f"Commercial: {result['commercial_permits']:>3} | "
              f"Score: {result['opportunity_score']:>6.2f}")
    
    print("\n✅ Analysis complete! Check the output files.")

if __name__ == "__main__":
    main()
