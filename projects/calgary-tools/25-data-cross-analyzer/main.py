#!/usr/bin/env python3
"""
Calgary Data Cross-Analyzer
Finds correlations across multiple datasets
"""
import requests, json
from collections import defaultdict

DATASETS = {
    'permits': 'c2es-76ed',      # Building Permits
    'crime': '78gh-n26t',        # Crime Statistics  
    'assessments': '4bsw-nn7w',  # Property Assessments
    'demographics': 'rkfr-buzb'  # Community Demographics
}

def fetch_dataset(name, dataset_id):
    try:
        resp = requests.get(f"https://data.calgary.ca/resource/{dataset_id}.json?$limit=10000")
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return []

def main():
    print("=" * 60)
    print("CALGARY DATA CROSS-ANALYZER")
    print("=" * 60)
    
    datasets = {}
    for name, dataset_id in DATASETS.items():
        print(f"\nFetching {name}...")
        data = fetch_dataset(name, dataset_id)
        datasets[name] = data
        print(f"  ✓ {len(data)} records")
    
    # Build community index
    communities = defaultdict(lambda: {k: 0 for k in DATASETS.keys()})
    
    # Count records per community per dataset
    for name, data in datasets.items():
        for record in data:
            community = (record.get('communityname') or 
                        record.get('comm_name') or
                        record.get('community_name') or
                        record.get('name') or
                        record.get('community') or 'Unknown')
            if community != 'Unknown':
                communities[community][name] += 1
    
    # Score communities
    scored = []
    for community, counts in communities.items():
        if sum(counts.values()) < 10:
            continue
        
        score = (
            counts.get('permits', 0) * 2 +
            counts.get('assessments', 0) * 0.01 -
            counts.get('crime', 0) * 0.5 +
            counts.get('demographics', 0) * 0.1
        )
        
        scored.append({
            'community': community,
            'score': round(score, 2),
            **counts
        })
    
    scored.sort(key=lambda x: x['score'], reverse=True)
    
    # Save outputs
    with open('correlations.json', 'w') as f:
        json.dump(scored[:50], f, indent=2)
    
    html = f"""<html><head><title>Cross-Dataset Insights</title><style>
    body {{font-family: Arial; margin: 20px;}}
    table {{border-collapse: collapse; width: 100%;}}
    th {{background: #1976d2; color: white; padding: 10px;}}
    td {{padding: 8px; border-bottom: 1px solid #ddd;}}
    .hot {{background: #e3f2fd;}}
    </style></head><body>
    <h1>📊 Calgary Cross-Dataset Insights</h1>
    <p>Communities ranked by composite investment/livability score</p>
    <table><tr><th>Rank</th><th>Community</th><th>Score</th><th>Permits</th><th>Properties</th><th>Crime</th></tr>"""
    
    for idx, item in enumerate(scored[:30], 1):
        row_class = 'hot' if idx <= 10 else ''
        html += f"""<tr class="{row_class}"><td>{idx}</td><td><b>{item['community']}</b></td>
        <td>{item['score']}</td><td>{item['permits']}</td><td>{item['assessments']}</td><td>{item['crime']}</td></tr>"""
    
    html += "</table></body></html>"
    
    with open('insights.html', 'w') as f:
        f.write(html)
    
    # Recommendations
    with open('recommendations.txt', 'w') as f:
        f.write("CALGARY INVESTMENT RECOMMENDATIONS\n")
        f.write("=" * 60 + "\n\n")
        f.write("Top 10 Communities by Composite Score:\n\n")
        for idx, item in enumerate(scored[:10], 1):
            f.write(f"{idx}. {item['community']} (score: {item['score']})\n")
            f.write(f"   Permits: {item['permits']}, Properties: {item['assessments']}, Crime: {item['crime']}\n\n")
    
    print("\n✅ Cross-analysis complete!")
    print(f"   Analyzed {len(communities)} communities")
    print("\nTop 5 by Composite Score:")
    for idx, item in enumerate(scored[:5], 1):
        print(f"  {idx}. {item['community']}: {item['score']}")
    
    print("\n📁 Outputs: correlations.json, insights.html, recommendations.txt")

if __name__ == "__main__":
    main()
