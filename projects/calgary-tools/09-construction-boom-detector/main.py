#!/usr/bin/env python3
"""
Construction Boom Detector
Identifies neighborhoods with accelerating development
"""

import requests
import pandas as pd
import json
import plotly.express as px
from datetime import datetime

BASE_URL = "https://data.calgary.ca/resource"

def fetch_data(dataset_id, limit=50000):
    url = f"{BASE_URL}/{dataset_id}.json?$limit={limit}"
    print(f"Fetching {dataset_id}...")
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.json()

def main():
    print("🏗️  Construction Boom Detector")
    print("=" * 60)
    
    print("\n📊 Fetching building permits...")
    permits = fetch_data("c2es-76ed", limit=50000)
    print(f"   Found {len(permits)} permits")
    
    df = pd.DataFrame(permits)
    
    # Find date column
    date_col = None
    for col in ['applieddate', 'issueddate', 'applied_date', 'issued_date', 'date']:
        if col in df.columns:
            date_col = col
            break
    
    community_col = None
    for col in ['communityname', 'community_name', 'community']:
        if col in df.columns:
            community_col = col
            break
    
    if not date_col or not community_col:
        print(f"⚠️  Columns: {df.columns.tolist()}")
        print("   Missing required columns")
        return
    
    # Parse dates
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df[df[date_col].notna()]
    
    # Add month column
    df['year_month'] = df[date_col].dt.to_period('M')
    
    # Count permits by community and month
    monthly_permits = df.groupby([community_col, 'year_month']).size().reset_index(name='permit_count')
    monthly_permits['year_month'] = monthly_permits['year_month'].astype(str)
    
    # Calculate velocity (change in permits month-over-month)
    results = []
    for community in monthly_permits[community_col].unique():
        comm_data = monthly_permits[monthly_permits[community_col] == community].sort_values('year_month')
        
        if len(comm_data) < 6:
            continue
        
        # Get recent 6 months vs previous 6 months
        recent_6 = comm_data.tail(6)['permit_count'].sum()
        previous_6 = comm_data.tail(12).head(6)['permit_count'].sum() if len(comm_data) >= 12 else 0
        
        velocity_change = recent_6 - previous_6
        pct_change = ((recent_6 - previous_6) / (previous_6 + 1) * 100)
        
        results.append({
            'community': community,
            'recent_6mo_permits': int(recent_6),
            'previous_6mo_permits': int(previous_6),
            'velocity_change': int(velocity_change),
            'percent_change': round(pct_change, 1),
            'status': 'BOOM' if pct_change > 50 else 'COOLING' if pct_change < -30 else 'STABLE'
        })
    
    # Sort by velocity change
    results_sorted = sorted(results, key=lambda x: x['velocity_change'], reverse=True)
    
    # Save results
    print("\n💾 Saving results...")
    with open('construction_velocity.json', 'w') as f:
        json.dump(results_sorted[:40], f, indent=2)
    
    df_results = pd.DataFrame(results_sorted)
    df_results.to_csv('velocity_trends.csv', index=False)
    
    # Viz
    print("📈 Creating visualizations...")
    top_boom = df_results.head(20)
    fig = px.bar(top_boom, x='velocity_change', y='community',
                 orientation='h',
                 title='Top 20 Construction Boom Neighborhoods',
                 labels={'velocity_change': 'Permit Velocity Change (Recent 6mo vs Previous 6mo)'},
                 color='percent_change',
                 color_continuous_scale='RdYlGn')
    fig.update_layout(height=600)
    fig.write_html('boom_analysis.html')
    
    print("\n📈 TOP 10 BOOM NEIGHBORHOODS (Accelerating Permits)")
    print("=" * 90)
    for i, r in enumerate(results_sorted[:10], 1):
        print(f"{i:2d}. {r['community']:<30} | Recent: {r['recent_6mo_permits']:>4} | "
              f"Previous: {r['previous_6mo_permits']:>4} | Change: {r['velocity_change']:>+5} ({r['percent_change']:>+6.1f}%)")
    
    print("\n📉 TOP 10 COOLING NEIGHBORHOODS (Slowing Permits)")
    print("=" * 90)
    for i, r in enumerate(reversed(results_sorted[-10:]), 1):
        print(f"{i:2d}. {r['community']:<30} | Recent: {r['recent_6mo_permits']:>4} | "
              f"Previous: {r['previous_6mo_permits']:>4} | Change: {r['velocity_change']:>+5} ({r['percent_change']:>+6.1f}%)")
    
    print("\n✅ Complete!")

if __name__ == "__main__":
    main()
