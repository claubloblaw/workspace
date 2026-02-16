#!/usr/bin/env python3
"""Neighborhood Gentrification Index"""
import requests, json
from datetime import datetime

def fetch_data(dataset_id):
    try:
        resp = requests.get(f"https://data.calgary.ca/resource/{dataset_id}.json?$limit=20000")
        return resp.json() if resp.status_code == 200 else []
    except:
        return []

def main():
    print("=" * 60)
    print("NEIGHBORHOOD GENTRIFICATION INDEX")
    print("=" * 60)
    
    print("\nFetching property assessments...")
    properties = fetch_data('4bsw-nn7w')
    print(f"  ✓ {len(properties)} properties")
    
    print("\nFetching building permits...")
    permits = fetch_data('c2es-76ed')
    print(f"  ✓ {len(permits)} permits")
    
    print("\nFetching demographics...")
    demographics = fetch_data('rkfr-buzb')
    print(f"  ✓ {len(demographics)} records")
    
    from collections import defaultdict
    community_stats = defaultdict(lambda: {'value_sum': 0, 'permits': 0, 'properties': 0})
    
    for prop in properties:
        comm = prop.get('comm_name', 'Unknown')
        if comm != 'Unknown':
            community_stats[comm]['properties'] += 1
            community_stats[comm]['value_sum'] += float(prop.get('assessed_value', 0))
    
    for permit in permits:
        comm = permit.get('communityname', 'Unknown')
        if comm != 'Unknown':
            community_stats[comm]['permits'] += 1
    
    scores = []
    for comm, stats in community_stats.items():
        if stats['properties'] < 10:
            continue
        
        avg_value = stats['value_sum'] / stats['properties']
        permit_rate = stats['permits'] / stats['properties'] * 100
        
        # High permit rate + moderate values = potential gentrification
        score = permit_rate * (avg_value / 1000000)
        
        scores.append({
            'community': comm,
            'score': round(score, 2),
            'avg_property_value': round(avg_value, 0),
            'permit_rate': round(permit_rate, 2),
            'permits': stats['permits']
        })
    
    scores.sort(key=lambda x: x['score'], reverse=True)
    
    with open('gentrification_scores.json', 'w') as f:
        json.dump(scores[:50], f, indent=2)
    
    html = f"""<html><head><title>Gentrification Index</title><style>
    body {{font-family: Arial; margin: 20px;}} table {{border-collapse: collapse; width: 100%;}}
    th {{background: #9c27b0; color: white; padding: 10px;}}
    td {{padding: 8px; border-bottom: 1px solid #ddd;}} .watch {{background: #f3e5f5;}}
    </style></head><body><h1>🏘️ Gentrification Watch List</h1>
    <table><tr><th>Rank</th><th>Community</th><th>Score</th><th>Avg Value</th><th>Permit Rate</th></tr>"""
    
    for idx, item in enumerate(scores[:40], 1):
        row_class = 'watch' if idx <= 15 else ''
        html += f"""<tr class="{row_class}"><td>{idx}</td><td><b>{item['community']}</b></td>
        <td>{item['score']}</td><td>${item['avg_property_value']:,.0f}</td><td>{item['permit_rate']}%</td></tr>"""
    
    html += "</table></body></html>"
    
    with open('gentrification_map.html', 'w') as f:
        f.write(html)
    
    print("\n✅ Analysis complete!")
    print(f"\nTop 5 Gentrifying Neighborhoods:")
    for idx, item in enumerate(scores[:5], 1):
        print(f"  {idx}. {item['community']}: Score {item['score']}, Avg ${item['avg_property_value']:,.0f}")
    print("\n📁 Outputs: gentrification_scores.json, gentrification_map.html")

if __name__ == "__main__":
    main()
