#!/usr/bin/env python3
"""
Calgary Community Crime Dashboard
Visualizes crime statistics by community and category
"""

import requests
import json
from collections import defaultdict
from datetime import datetime

def fetch_crime_data(limit=20000):
    """Fetch community crime statistics from Calgary Open Data"""
    url = f"https://data.calgary.ca/resource/78gh-n26t.json?$limit={limit}"
    print(f"Fetching crime data...")
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.json()

def analyze_crime_by_community(data):
    """Analyze crime by community"""
    community_stats = defaultdict(lambda: {'total': 0, 'categories': defaultdict(int)})
    
    for record in data:
        # Crime dataset uses 'community' field (community code)
        community = record.get('community', 'Unknown')
        category = record.get('category', 'Unknown')
        crime_count = int(float(record.get('crime_count', 0)))
        
        community_stats[community]['total'] += crime_count
        community_stats[community]['categories'][category] += crime_count
    
    # Convert to sorted list
    results = []
    for community, stats in community_stats.items():
        if stats['total'] == 0:
            continue
        top_categories = sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True)[:3]
        results.append({
            'community': community,
            'total_crimes': stats['total'],
            'top_categories': top_categories
        })
    
    results.sort(key=lambda x: x['total_crimes'], reverse=True)
    return results

def analyze_crime_by_category(data):
    """Analyze crime by category across all communities"""
    category_totals = defaultdict(int)
    
    for record in data:
        category = record.get('category', 'Unknown')
        crime_count = int(float(record.get('crime_count', 0)))
        category_totals[category] += crime_count
    
    results = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    return results

def generate_html_report(community_stats, category_stats, total_crimes):
    """Generate an HTML visualization"""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Calgary Crime Dashboard</title>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 40px;
        }}
        h1 {{
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        .subtitle {{
            color: #718096;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-card h3 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: bold;
        }}
        .stat-card p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            color: #2d3748;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        thead {{
            background: #f7fafc;
        }}
        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #2d3748;
            border-bottom: 2px solid #e2e8f0;
        }}
        td {{
            padding: 15px;
            border-bottom: 1px solid #e2e8f0;
        }}
        tr:hover {{
            background: #f7fafc;
        }}
        .rank {{
            font-weight: bold;
            color: #667eea;
            font-size: 1.2em;
        }}
        .crime-count {{
            font-weight: bold;
            color: #e53e3e;
        }}
        .category-list {{
            color: #718096;
            font-size: 0.9em;
        }}
        .top-10 {{
            background: #fff5f5;
        }}
        .bar {{
            height: 20px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚨 Calgary Crime Dashboard</h1>
        <p class="subtitle">Community crime statistics from Calgary Open Data</p>
        <p class="subtitle"><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>{len(community_stats)}</h3>
                <p>Communities</p>
            </div>
            <div class="stat-card">
                <h3>{len(category_stats)}</h3>
                <p>Crime Categories</p>
            </div>
            <div class="stat-card">
                <h3>{total_crimes:,}</h3>
                <p>Total Crimes</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Top 20 Communities by Crime Volume</h2>
            <table>
                <thead>
                    <tr>
                        <th style="width: 60px">Rank</th>
                        <th>Community</th>
                        <th>Total Crimes</th>
                        <th>Top Crime Categories</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for idx, community in enumerate(community_stats[:20], 1):
        row_class = 'top-10' if idx <= 10 else ''
        top_cats = ', '.join([f"{cat} ({count})" for cat, count in community['top_categories'][:3]])
        html += f"""
                    <tr class="{row_class}">
                        <td class="rank">{idx}</td>
                        <td><strong>{community['community']}</strong></td>
                        <td class="crime-count">{community['total_crimes']:,}</td>
                        <td class="category-list">{top_cats}</td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>Crime Categories Across All Communities</h2>
            <table>
                <thead>
                    <tr>
                        <th style="width: 60px">Rank</th>
                        <th>Category</th>
                        <th>Total Count</th>
                        <th>Distribution</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    max_crimes = category_stats[0][1] if category_stats else 1
    for idx, (category, count) in enumerate(category_stats[:15], 1):
        bar_width = (count / max_crimes * 100) if max_crimes > 0 else 0
        html += f"""
                    <tr>
                        <td class="rank">{idx}</td>
                        <td><strong>{category}</strong></td>
                        <td class="crime-count">{count:,}</td>
                        <td>
                            <div class="bar" style="width: {bar_width}%"></div>
                        </td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="section" style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #e2e8f0; color: #718096; font-size: 0.9em;">
            <p><strong>Data Source:</strong> Calgary Open Data Portal - Crime Statistics (78gh-n26t)</p>
            <p><strong>Note:</strong> This dashboard shows aggregated crime statistics by community. Higher numbers may reflect larger populations or better reporting.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    print("=" * 60)
    print("CALGARY COMMUNITY CRIME DASHBOARD")
    print("=" * 60)
    
    # Fetch data
    print("\n[1/3] Fetching crime data...")
    data = fetch_crime_data(limit=10000)
    print(f"   ✓ Loaded {len(data)} records")
    
    # Analyze
    print("\n[2/3] Analyzing data...")
    community_stats = analyze_crime_by_community(data)
    category_stats = analyze_crime_by_category(data)
    total_crimes = sum(c['total_crimes'] for c in community_stats)
    print(f"   ✓ Analyzed {len(community_stats)} communities")
    print(f"   ✓ Found {len(category_stats)} crime categories")
    
    # Generate output
    print("\n[3/3] Generating output...")
    
    # JSON
    with open('crime_dashboard_data.json', 'w') as f:
        json.dump({
            'communities': community_stats[:50],
            'categories': category_stats,
            'total_crimes': total_crimes
        }, f, indent=2)
    print("   ✓ Saved crime_dashboard_data.json")
    
    # HTML
    html = generate_html_report(community_stats, category_stats, total_crimes)
    with open('crime_dashboard.html', 'w') as f:
        f.write(html)
    print("   ✓ Saved crime_dashboard.html")
    
    # Print summary
    print("\n" + "=" * 60)
    print("TOP 10 COMMUNITIES BY CRIME VOLUME")
    print("=" * 60)
    for idx, community in enumerate(community_stats[:10], 1):
        print(f"{idx:2d}. {community['community']:30s} {community['total_crimes']:6,} crimes")
    
    print("\n✅ Crime dashboard generated successfully!")

if __name__ == "__main__":
    main()
