# Calgary Open Data Tools 🏙️

A collection of data analysis tools that transform Calgary's Open Data into actionable real estate and investment insights.

## 🎯 Overview

This project provides 8 comprehensive analysis tools that help investors, developers, and residents make data-driven decisions about Calgary neighborhoods. All tools use real-time data from the [Calgary Open Data Portal](https://data.calgary.ca).

## 📊 Available Tools

### 1. Permit Profit Predictor 🏗️
**Location:** `01-permit-profit-predictor/`

Identifies investment hotspots by analyzing building permit density and property values.

- **Datasets Used:** Building Permits, Property Assessments
- **Key Metrics:** Permit density, investment ratio, opportunity score
- **Output:** `permit_analysis.html`

### 2. Business Desert Finder 🏪
**Location:** `02-business-desert-finder/`

Finds residential areas lacking commercial development, indicating business opportunities.

- **Datasets Used:** Building Permits, Demographics
- **Key Metrics:** Commercial permit density, population vs. businesses
- **Output:** `desert_analysis.html`

### 3. Crime-Value Arbitrage 🚨
**Location:** `03-crime-value-arbitrage/`

Discovers mispriced neighborhoods where safety doesn't match property values.

- **Datasets Used:** Crime Statistics, Property Assessments
- **Key Metrics:** Crime rate, median property value, arbitrage score
- **Output:** `arbitrage_map.html`

### 4. Transit Development Radar 🚇
**Location:** `04-transit-development-radar/`

Maps building activity near CTrain stations to identify TOD opportunities.

- **Datasets Used:** Building Permits, CTrain Station Locations
- **Key Metrics:** Permits within 500m/1km of stations, TOD score
- **Output:** `transit_development_map.html`

### 5. Construction Boom Detector 📈
**Location:** `09-construction-boom-detector/`

Tracks permit velocity to find neighborhoods with accelerating development.

- **Datasets Used:** Building Permits (time-series)
- **Key Metrics:** 6-month velocity change, percent change
- **Output:** `boom_analysis.html`

### 6. Data Cross-Analyzer 🔀
**Location:** `25-data-cross-analyzer/`

Combines multiple datasets to create composite investment scores.

- **Datasets Used:** Permits, Crime, Assessments, Demographics
- **Key Metrics:** Weighted composite score
- **Output:** `insights.html`, `recommendations.txt`

### 7. Gentrification Index 🏘️
**Location:** `26-gentrification-index/`

Identifies early signs of neighborhood gentrification.

- **Datasets Used:** Property Assessments, Building Permits
- **Key Metrics:** Permit rate, average property value, gentrification score
- **Output:** `gentrification_map.html`

### 8. Crime Dashboard 📊
**Location:** `30-crime-dashboard/`

Interactive dashboard of crime statistics by community and category.

- **Datasets Used:** Crime Statistics
- **Key Metrics:** Total crimes, crime by category
- **Output:** `crime_dashboard.html`

## 🚀 Quick Start

### Prerequisites

```bash
pip install requests pandas plotly
```

### Run All Tools

```bash
./run_all.sh
```

### Run Individual Tool

```bash
cd 01-permit-profit-predictor
python3 main.py
```

Each tool will:
1. Fetch live data from Calgary Open Data Portal
2. Process and analyze the data
3. Generate HTML visualizations
4. Create JSON/CSV exports

## 📁 Data Sources

All tools use verified Calgary Open Data API endpoints:

- **Building Permits** (`c2es-76ed`) - 50k+ records
- **Property Assessments** (`4bsw-nn7w`) - 50k+ records
- **Crime Statistics** (`78gh-n26t`) - 20k+ records
- **Demographics** (`rkfr-buzb`) - 312 communities
- **Traffic Volumes** (`vdjc-pybd`) - 22k records
- **Community Boundaries** (`j9ps-fyst`) - 312 boundaries

## 🎨 Features

- ✅ **Real-time data** from Calgary Open Data Portal
- ✅ **Interactive visualizations** using Plotly and Leaflet
- ✅ **Professional dark-themed dashboards**
- ✅ **Self-contained HTML outputs** (no dependencies required to view)
- ✅ **JSON/CSV exports** for further analysis
- ✅ **Responsive design** for mobile/desktop viewing

## 📋 Output Files

Each tool generates:
- **HTML report** - Interactive visualization (main output)
- **JSON file** - Raw data for programmatic access
- **CSV file** - Spreadsheet-compatible data (most tools)

## 🔧 Technical Stack

- **Language:** Python 3
- **Data Processing:** Pandas
- **Visualization:** Plotly, Leaflet
- **Data Source:** Calgary Open Data API (Socrata SODA)

## 📊 Use Cases

### For Investors
- Identify undervalued neighborhoods
- Find high-growth areas before prices surge
- Assess risk vs. reward across communities

### For Developers
- Locate areas with development momentum
- Find gaps in commercial services
- Plan projects near transit hubs

### For Residents
- Understand neighborhood safety trends
- Track development in your area
- Make informed moving decisions

## 🗺️ Viewing the Dashboard

Open `index.html` in any web browser to access:
- Overview of all tools
- Quick links to each analysis
- Summary statistics

## 📝 Notes

- Data is fetched fresh on each run (no caching)
- API limits to 50,000 records per dataset
- Some datasets (Crime) use community codes that are mapped to names
- Transit station coordinates are hardcoded (based on CTrain system)

## 🤝 Contributing

To add a new tool:
1. Create folder: `XX-tool-name/`
2. Add `main.py` with data fetching and analysis
3. Generate self-contained HTML output
4. Update this README and `index.html`

## 📜 License

This project uses public data from the Calgary Open Data Portal. Check individual dataset licenses on [data.calgary.ca](https://data.calgary.ca).

## 🔗 Links

- [Calgary Open Data Portal](https://data.calgary.ca)
- [Live Dashboard](./index.html)
- [Project Documentation](./FINAL_STATUS.md)

---

**Built with ❤️ for Calgary real estate intelligence**
