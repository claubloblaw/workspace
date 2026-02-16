# Calgary Public Data Arsenal

**Mission:** Aggregate every publicly available dataset on Calgary to develop creative alpha through unique cross-dataset insights.

---

## Source Inventory

### 1. City of Calgary Open Data Portal — `data.calgary.ca`
- **990 datasets** (Socrata platform, SODA API)
- **API:** `https://data.calgary.ca/resource/{dataset-id}.json` (no auth for reads)
- **Full catalog saved:** `city_open_data_catalog.json`
- **Categories:**
  - Transportation/Transit: 179
  - Environment: 141
  - Government: 137
  - Demographics: 112
  - Help and Information: 79
  - Services and Amenities: 64
  - Health and Safety: 61
  - Business and Economic Activity: 58
  - Recreation and Culture: 58
  - Base Maps: 47
  - Other: 54

### 2. Alberta Open Government — `open.alberta.ca`
- Provincial data filtered to Calgary
- Income support caseloads, health metrics, education, housing
- Datasets: https://open.alberta.ca/dataset?q=%22Calgary%22

### 3. Calgary Metropolitan Region — `calgarymetroregion-cmrb.opendata.arcgis.com`
- Regional planning, land use, growth management
- ArcGIS Hub format

### 4. Statistics Canada — `statcan.gc.ca`
- Census profiles (Calgary CMA DGUID: 2021S0503825)
- Focus on Geography: https://www12.statcan.gc.ca/census-recensement/2021/as-sa/fogs-spg/page.cfm?lang=E&topic=1&dguid=2021S0503825
- Economic indicators, labour force surveys, CPI
- Table API: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action

### 5. Calgary Economic Development — `calgaryeconomicdevelopment.com`
- Monthly economic dashboard (compared to Van, Edm, TO, Ottawa, Montreal)
- Labour market, demographics, industry reports
- Report library: https://www.calgaryeconomicdevelopment.com/insights/reports/

### 6. CMHC (Canada Mortgage and Housing Corp)
- Housing starts, completions, supply reports
- Rental market surveys
- https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research

### 7. City of Calgary Housing Data — `calgary.ca`
- Housing Needs Assessment
- Quarterly housing market analysis
- https://www.calgary.ca/communities/housing-in-calgary/housing-research/housing-data.html

### 8. City of Calgary Population/Census — `calgary.ca`
- Civic census data, community profiles
- https://www.calgary.ca/research/population-profile.html

### 9. CREB (Calgary Real Estate Board)
- Monthly housing stats (benchmark prices, inventory, sales)
- Public summaries available (full data requires membership)

### 10. Open Data Calgary (Community) — `opendatacalgary.ca`
- Curated dashboards: Business Licences (21K+), Property Assessments (584K+), Building Permits (467K+)
- Federal corps (30K+), Alberta corps (363K+)

---

## High-Alpha Dataset Categories

These are the datasets most likely to yield unique insights when cross-referenced:

### 🏗️ Development & Real Estate
- Building permits (467K records)
- Property assessments (584K records)
- Land use redesignation applications
- Development permits
- Housing starts/completions (CMHC)

### 💼 Business & Economy
- Business licences (21K active)
- Alberta corporations (363K in Calgary)
- Federal corporations (30K in Calgary)
- Commercial property assessments

### 🚌 Transportation & Infrastructure
- Transit ridership
- Traffic volumes
- Bike lane usage
- Road conditions
- Parking data

### 👥 Demographics & Population
- 112 datasets on demographics
- Civic census (neighbourhood level)
- Immigration patterns
- Income distributions

### 🏥 Health & Safety
- Crime statistics
- Fire/EMS response
- Community safety data
- 311 service requests

### 🌿 Environment
- Air quality monitoring
- Water quality
- Parks and green spaces
- Flood risk areas

---

## Cross-Dataset Alpha Opportunities

1. **Permit-to-Assessment lag** — Track building permits → property assessment changes to predict neighbourhood appreciation
2. **Business licence clustering** — Map new licence issuance against transit/demo data to find underserved areas
3. **Crime × Property values** — Overlay crime stats with assessment data to find mispriced neighbourhoods
4. **Transit development corridor** — New transit routes × development permits × land use changes
5. **Corporation density mapping** — 393K corps mapped by postal code against commercial vacancy
6. **Population growth × Infrastructure** — Civic census trends vs. service capacity (schools, transit, rec)

---

## Files

- `city_open_data_catalog.json` — Full metadata for all 990 City of Calgary datasets
- `catalog_by_category.json` — Datasets grouped by category
- `README.md` — This file

## Next Steps

- [ ] Pull dataset samples from top priority categories
- [ ] Index Alberta Open Government Calgary-specific datasets
- [ ] Scrape CREB monthly stats archive
- [ ] Download StatCan Calgary CMA tables
- [ ] Build cross-reference index for spatial joins (by community/neighbourhood)
