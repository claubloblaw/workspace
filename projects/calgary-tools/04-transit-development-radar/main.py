#!/usr/bin/env python3
"""
Transit Development Radar
Maps building permits near major transit stations to identify TOD hotspots
"""

import requests
import pandas as pd
import json
from math import radians, cos, sin, asin, sqrt

BASE_URL = "https://data.calgary.ca/resource"

# Known Calgary CTrain (LRT) and major BRT stations
CALGARY_TRANSIT_STATIONS = [
    # Red Line (South)
    {"name": "Somerset-Bridlewood", "lat": 50.9088, "lon": -114.0715},
    {"name": "Fish Creek-Lacombe", "lat": 50.9253, "lon": -114.0702},
    {"name": "Shawnessy", "lat": 50.9393, "lon": -114.0668},
    {"name": "Anderson", "lat": 50.9656, "lon": -114.0811},
    {"name": "Chinook", "lat": 50.9978, "lon": -114.0707},
    {"name": "Heritage", "lat": 51.0113, "lon": -114.0705},
    {"name": "39 Avenue", "lat": 51.0250, "lon": -114.0836},
    {"name": "Erlton-Stampede", "lat": 51.0336, "lon": -114.0603},
    {"name": "Victoria Park-Stampede", "lat": 51.0433, "lon": -114.0542},
    {"name": "City Hall", "lat": 51.0486, "lon": -114.0625},
    
    # Red Line (North)
    {"name": "3 Street SE", "lat": 51.0497, "lon": -114.0580},
    {"name": "Bridgeland-Memorial", "lat": 51.0555, "lon": -114.0480},
    {"name": "Lions Park", "lat": 51.0652, "lon": -114.0503},
    {"name": "SAIT-ACAD-Jubilee", "lat": 51.0667, "lon": -114.0885},
    {"name": "Lions Park", "lat": 51.0652, "lon": -114.0503},
    {"name": "Sunnyside", "lat": 51.0544, "lon": -114.0789},
    {"name": "Crescent Heights", "lat": 51.0516, "lon": -114.0642},
    
    # Blue Line (West)
    {"name": "69 Street", "lat": 51.0396, "lon": -114.2062},
    {"name": "Westbrook", "lat": 51.0329, "lon": -114.1616},
    {"name": "Shaganappi Point", "lat": 51.0418, "lon": -114.1284},
    {"name": "Sunalta", "lat": 51.0445, "lon": -114.0995},
    
    # Blue Line (Northeast)
    {"name": "Whitehorn", "lat": 51.0852, "lon": -113.9667},
    {"name": "Marlborough", "lat": 51.0779, "lon": -113.9633},
    {"name": "Franklin", "lat": 51.0728, "lon": -113.9779},
    {"name": "Barlow-Max Bell", "lat": 51.0684, "lon": -113.9953},
    {"name": "Zoo", "lat": 51.0460, "lon": -114.0326},
    
    # Green Line (Future/Planning)
    {"name": "Brentwood", "lat": 51.0883, "lon": -114.1106},
    {"name": "Dalhousie", "lat": 51.1020, "lon": -114.1226},
]

def fetch_data(dataset_id, limit=50000):
    """Fetch data from Calgary Open Data API"""
    url = f"{BASE_URL}/{dataset_id}.json?$limit={limit}"
    print(f"Fetching {dataset_id}...")
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.json()

def haversine(lon1, lat1, lon2, lat2):
    """Calculate distance between two points in meters"""
    try:
        lon1, lat1, lon2, lat2 = map(float, [lon1, lat1, lon2, lat2])
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        m = 6371000 * c  # Radius of earth in meters
        return m
    except (ValueError, TypeError):
        return float('inf')

def main():
    print("🚇 Transit Development Radar")
    print("=" * 60)
    
    print(f"\n📍 Using {len(CALGARY_TRANSIT_STATIONS)} Calgary CTrain station locations")
    
    # Fetch building permits
    print("\n🏗️  Fetching building permits...")
    permits = fetch_data("c2es-76ed", limit=50000)
    print(f"   Found {len(permits)} permits")
    
    df_permits = pd.DataFrame(permits)
    
    # Analyze each station
    results_by_station = []
    
    for station in CALGARY_TRANSIT_STATIONS:
        permits_500m = []
        permits_1km = []
        total_value_500m = 0
        total_value_1km = 0
        
        for _, permit in df_permits.iterrows():
            # Get permit location
            lat = permit.get('latitude')
            lon = permit.get('longitude')
            
            if lat and lon:
                distance = haversine(station['lon'], station['lat'], lon, lat)
                
                if distance <= 500:
                    permits_500m.append(permit)
                    cost = permit.get('estprojectcost', 0)
                    if cost:
                        try:
                            total_value_500m += float(cost)
                        except:
                            pass
                elif distance <= 1000:
                    permits_1km.append(permit)
                    cost = permit.get('estprojectcost', 0)
                    if cost:
                        try:
                            total_value_1km += float(cost)
                        except:
                            pass
        
        # Calculate TOD score (weighted: 500m permits count double)
        tod_score = (len(permits_500m) * 2) + len(permits_1km)
        
        # Handle potential NaN values
        import math
        if math.isnan(total_value_500m):
            total_value_500m = 0
        if math.isnan(total_value_1km):
            total_value_1km = 0
        
        results_by_station.append({
            'station': station['name'],
            'lat': station['lat'],
            'lon': station['lon'],
            'permits_within_500m': len(permits_500m),
            'permits_within_1km': len(permits_1km),
            'total_permits': len(permits_500m) + len(permits_1km),
            'total_value_500m': int(total_value_500m),
            'total_value_1km': int(total_value_1km),
            'tod_score': tod_score
        })
    
    # Sort by TOD score
    results_sorted = sorted(results_by_station, key=lambda x: x['tod_score'], reverse=True)
    
    # Save results
    print("\n💾 Saving results...")
    
    with open('tod_hotspots.json', 'w') as f:
        json.dump(results_sorted, f, indent=2)
    print("   ✓ Saved tod_hotspots.json")
    
    df_results = pd.DataFrame(results_sorted)
    df_results.to_csv('tod_analysis.csv', index=False)
    print("   ✓ Saved tod_analysis.csv")
    
    # Generate HTML report
    html = generate_html_report(results_sorted)
    with open('transit_development_map.html', 'w') as f:
        f.write(html)
    print("   ✓ Saved transit_development_map.html")
    
    # Print top stations
    print("\n🚇 TOP TRANSIT-ORIENTED DEVELOPMENT HOTSPOTS")
    print("=" * 100)
    for i, r in enumerate(results_sorted[:15], 1):
        print(f"{i:2d}. {r['station']:<25} | "
              f"<500m: {r['permits_within_500m']:>3} | "
              f"<1km: {r['permits_within_1km']:>3} | "
              f"Total: {r['total_permits']:>3} | "
              f"Value 500m: ${r['total_value_500m']:>12,} | "
              f"TOD: {r['tod_score']:>5}")
    
    print("\n✅ Complete!")
    print(f"   📄 tod_hotspots.json - Station rankings")
    print(f"   📄 tod_analysis.csv - Full data")
    print(f"   📄 transit_development_map.html - Interactive map")

def generate_html_report(results):
    """Generate HTML report with map"""
    
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Calgary Transit Development Radar</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #0d1117; 
            color: #e6edf3;
        }
        .container { 
            max-width: 1600px; 
            margin: 0 auto; 
            background: #161b22; 
            padding: 30px; 
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.5);
        }
        h1 { 
            color: #58a6ff; 
            margin-bottom: 10px;
            font-size: 2.4em;
        }
        h2 {
            color: #79c0ff;
            border-bottom: 2px solid #30363d;
            padding-bottom: 10px;
            margin-top: 40px;
        }
        .meta { 
            color: #8b949e; 
            margin-bottom: 30px; 
        }
        #map { 
            height: 600px; 
            margin: 20px 0; 
            border-radius: 8px;
            border: 1px solid #30363d;
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0; 
            background: #0d1117;
        }
        th { 
            background: #1f6feb; 
            color: white; 
            padding: 14px; 
            text-align: left; 
            font-weight: 600;
        }
        td { 
            padding: 12px; 
            border-bottom: 1px solid #30363d; 
        }
        tr:hover { 
            background: #161b22; 
        }
        .high-tod { background: #1a3e1f; }
        .chart { 
            margin: 30px 0; 
            background: #0d1117; 
            padding: 20px; 
            border-radius: 8px;
        }
        .tod-score {
            font-weight: bold;
            color: #58a6ff;
            font-size: 1.1em;
        }
        .metric-card {
            display: inline-block;
            background: #0d1117;
            padding: 15px 25px;
            margin: 10px;
            border-radius: 8px;
            border: 1px solid #30363d;
        }
        .metric-value {
            font-size: 2em;
            color: #58a6ff;
            font-weight: bold;
        }
        .metric-label {
            color: #8b949e;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚇 Calgary Transit Development Radar</h1>
        <p class="meta">
            <strong>Analysis Date:</strong> """ + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + """<br>
            <strong>Methodology:</strong> Analyzes building permit density around Calgary CTrain stations<br>
            <strong>TOD Score:</strong> Transit-Oriented Development score (permits within 500m × 2 + permits within 1km)
        </p>
        
        <div class="metric-card">
            <div class="metric-value">""" + str(len(results)) + """</div>
            <div class="metric-label">Stations Analyzed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">""" + str(sum(r['total_permits'] for r in results)) + """</div>
            <div class="metric-label">Total Permits Near Transit</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">$""" + f"{sum(r['total_value_500m'] for r in results):,.0f}" + """</div>
            <div class="metric-label">Total Value (within 500m)</div>
        </div>
        
        <h2>Interactive Map</h2>
        <div id="map"></div>
        
        <h2>Top 20 TOD Hotspots</h2>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Station</th>
                    <th>Permits &lt;500m</th>
                    <th>Permits &lt;1km</th>
                    <th>Total</th>
                    <th>Value (500m)</th>
                    <th>TOD Score</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for idx, r in enumerate(results[:20], 1):
        row_class = 'high-tod' if idx <= 5 else ''
        html += f"""
                <tr class="{row_class}">
                    <td><strong>{idx}</strong></td>
                    <td><strong>{r['station']}</strong></td>
                    <td>{r['permits_within_500m']}</td>
                    <td>{r['permits_within_1km']}</td>
                    <td>{r['total_permits']}</td>
                    <td>${r['total_value_500m']:,}</td>
                    <td class="tod-score">{r['tod_score']}</td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
        
        <div class="chart" id="barChart"></div>
        
        <script>
            // Initialize map centered on Calgary
            var map = L.map('map').setView([51.0447, -114.0719], 11);
            
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
                subdomains: 'abcd',
                maxZoom: 20
            }).addTo(map);
            
            // Add station markers
            var stations = """ + json.dumps(results) + """;
            
            stations.forEach(function(station) {
                var radius = Math.sqrt(station.tod_score) * 50;
                var color = station.tod_score > 100 ? '#ff6b6b' : 
                           station.tod_score > 50 ? '#ffd93d' : '#6bcf7f';
                
                L.circle([station.lat, station.lon], {
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.5,
                    radius: radius
                }).bindPopup(`
                    <strong>${station.station}</strong><br>
                    TOD Score: ${station.tod_score}<br>
                    Permits (500m): ${station.permits_within_500m}<br>
                    Permits (1km): ${station.permits_within_1km}<br>
                    Value: $${station.total_value_500m.toLocaleString()}
                `).addTo(map);
                
                L.marker([station.lat, station.lon])
                    .bindPopup(`<strong>${station.station}</strong>`)
                    .addTo(map);
            });
            
            // Create bar chart
            var topStations = stations.slice(0, 15);
            
            var trace1 = {
                x: topStations.map(s => s.permits_within_500m),
                y: topStations.map(s => s.station),
                name: 'Within 500m',
                type: 'bar',
                orientation: 'h',
                marker: {color: '#58a6ff'}
            };
            
            var trace2 = {
                x: topStations.map(s => s.permits_within_1km),
                y: topStations.map(s => s.station),
                name: 'Within 1km',
                type: 'bar',
                orientation: 'h',
                marker: {color: '#79c0ff'}
            };
            
            var layout = {
                title: 'Development Permits by Transit Station',
                barmode: 'stack',
                paper_bgcolor: '#0d1117',
                plot_bgcolor: '#0d1117',
                font: {color: '#e6edf3'},
                xaxis: {
                    title: 'Number of Permits',
                    gridcolor: '#30363d',
                    color: '#e6edf3'
                },
                yaxis: {
                    gridcolor: '#30363d',
                    color: '#e6edf3',
                    autorange: 'reversed'
                },
                height: 600
            };
            
            Plotly.newPlot('barChart', [trace1, trace2], layout);
        </script>
        
        <p style="color: #8b949e; margin-top: 40px; font-size: 0.9em;">
            <strong>Interpretation:</strong><br>
            • <strong>TOD Score:</strong> Higher values indicate more active development around transit stations<br>
            • <strong>Circle Size:</strong> Larger circles on map represent higher TOD scores<br>
            • <strong>Colors:</strong> Red = high activity, Yellow = moderate, Green = low activity<br>
            • Data includes all building permits within 1km of each CTrain station
        </p>
    </div>
</body>
</html>
"""
    
    return html

if __name__ == "__main__":
    main()
