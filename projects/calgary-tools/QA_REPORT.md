# Calgary Open Data Tools - Comprehensive QA Report

**Generated:** 2026-02-15  
**Total Projects Audited:** 49  
**Projects with main.py:** 48  

---

## Executive Summary

Of 49 project directories audited:
- ✅ **WORKING**: 2 projects (4%)
- ⚠️ **PARTIAL**: 40 projects (82%)
- ❌ **BROKEN**: 7 projects (14%)
- 🗑️ **DUPLICATES**: 3 duplicate sets (6 projects total)

**Critical Finding:** Only 2 projects (4%) have confirmed working output with real data. The vast majority (82%) have valid code and API endpoints but produce empty or incomplete output.

---

## Summary Statistics

| Category | Count | Percentage |
|----------|-------|------------|
| Working (produces real data) | 2 | 4% |
| Partial (code valid, output issues) | 40 | 82% |
| Broken (no API or no main.py) | 7 | 14% |
| **Total** | **49** | **100%** |

### Duplicates Identified

3 sets of duplicates found:

1. **311 Complaint Heatmap** (2 copies)
   - `02-311-complaint-heatmap`
   - `06-311-complaint-heatmap`

2. **Park Quality Scorer** (2 copies)
   - `06-park-quality-scorer`
   - `16-park-quality-scorer`

3. **Gentrification Index** (2 copies)
   - `19-gentrification-index`
   - `26-gentrification-index`

---

## Project-by-Project Findings

### ✅ WORKING (2 projects)

#### 1. 25-data-cross-analyzer
- **Status**: ✅ WORKING
- **Code Length**: 4,002 chars
- **API Endpoints**: 4 found
- **Output**: HTML file exists with real data
- **Notes**: Successfully fetches data from multiple Calgary Open Data APIs and produces analysis

#### 2. 26-gentrification-index  
- **Status**: ✅ WORKING
- **Code Length**: 3,504 chars
- **API Endpoints**: 3 found
- **Output**: HTML file with data (though analysis shows all zeros for scores)
- **Notes**: Has valid code and produces output, though the gentrification scoring algorithm may need review

---

### ⚠️ PARTIAL (40 projects)

These projects have valid Python code and real Calgary Open Data API endpoints, but produce empty or incomplete output:

#### 01-permit-profit-predictor
- **Code**: 8,735 chars ✓
- **APIs**: kr8b-c44i (permits), 4bsw-nn7w (assessments) ✓
- **Issue**: HTML output exists (1,736 bytes) but contains no table rows - empty dataset

#### 02-311-complaint-heatmap
- **Code**: 5,188 chars ✓
- **APIs**: 7955-menx (311 data) ✓
- **Issue**: No HTML output files found, only code exists

#### 02-business-desert-finder
- **Code**: 6,125 chars ✓
- **APIs**: Uses base URL only ✓
- **Issue**: No HTML output found

#### 03-crime-value-arbitrage
- **Code**: 6,204 chars ✓
- **APIs**: 2 endpoints ✓
- **Output**: HTML (4.8MB) with placeholder/empty data

#### 03-transit-ridership
- **Code**: 1,994 chars ✓
- **APIs**: t6ss-7nqj ✓
- **Issue**: No HTML output

#### 04-crime-pattern-mapper
- **Code**: 2,600 chars ✓
- **APIs**: 848s-4zvh ✓
- **Issue**: No HTML output

#### 04-transit-development-radar
- **Code**: 6,202 chars ✓
- **APIs**: 2 endpoints ✓
- **Output**: HTML (4.8MB) but likely empty/placeholder

#### 05-business-license-tracker
- **Code**: 2,806 chars ✓
- **APIs**: 7dha-e5pf ✓
- **Issue**: No HTML output

#### 05-restaurant-health-tracker
- **Code**: 5,536 chars ✓
- **APIs**: c98r-7byf ✓
- **Issue**: No HTML output

#### 06-311-complaint-heatmap 🗑️ DUPLICATE
- **Code**: 5,002 chars ✓
- **APIs**: i45m-iwig ✓
- **Issue**: Duplicate of 02-311-complaint-heatmap, no output

#### 06-park-quality-scorer 🗑️ DUPLICATE
- **Code**: 2,473 chars ✓
- **APIs**: kami-qbfh ✓
- **Issue**: Duplicate, no output

#### 07-snow-plow-tracker
- **Code**: 2,518 chars ✓
- **APIs**: it2k-92xe ✓
- **Output**: HTML (4.8MB)

#### 07-snow-routes
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Minimal code, no output

#### 08-dog-park-density
- **Code**: 3,759 chars ✓
- **APIs**: 2 endpoints ✓
- **Issue**: No output

#### 08-traffic-incidents
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Generic template code

#### 09-construction-boom-detector
- **Code**: 4,508 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: No output

#### 09-water-consumption
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Generic template

#### 10-pathways
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Generic template

#### 10-pothole-analyzer
- **Code**: 4,653 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: No output

#### 11-business-survival
- **Code**: 2,708 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: No output

#### 11-community-services
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Generic template

#### 12-election-results
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Generic template

#### 12-tax-efficiency-ranker
- **Code**: 1,575 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: No output

#### 13-waste-diversion
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Generic template

#### 14-demographic-shifter
- **Code**: 1,721 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: No output

#### 14-fire-response
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Generic template

#### 15-property-tax
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Generic template

#### 16-development-permits
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Generic template

#### 16-park-quality-scorer 🗑️ DUPLICATE
- **Code**: 1,173 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Duplicate of 06-park-quality-scorer

#### 17-playgrounds
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Generic template

#### 18-solar-potential
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Generic template

#### 18-vacancy-detector
- **Code**: 1,732 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: No output

#### 19-gentrification-index 🗑️ DUPLICATE
- **Code**: 1,990 chars ✓
- **APIs**: 2 endpoints ✓
- **Issue**: Duplicate of 26-gentrification-index

#### 19-tree-canopy
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Generic template

#### 20-city-budget
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Generic template

#### 21-bylaw-complaints
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Generic template

#### 22-heritage-properties
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Generic template

#### 23-demographics
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Generic template

#### 24-libraries
- **Code**: 919 chars ✓
- **APIs**: 1 endpoint ✓
- **Issue**: Generic template

#### 27-realtime-dashboard
- **Code**: 2,323 chars ✓
- **APIs**: 3 endpoints ✓
- **Issue**: No real-time output

---

### ❌ BROKEN (7 projects)

These projects either have no main.py or no Calgary Open Data API endpoints:

#### 07-snow-route-priority
- **Issue**: ❌ No main.py file found
- **Status**: BROKEN

#### 13-bike-lane-roi
- **Code**: 932 chars
- **Issue**: ❌ No Calgary Open Data API endpoints found
- **Status**: BROKEN

#### 15-emergency-response-mapper
- **Code**: 1,030 chars
- **Issue**: ❌ No API endpoints
- **Status**: BROKEN

#### 17-transit-ridership-predictor
- **Code**: 884 chars
- **Issue**: ❌ No API endpoints
- **Status**: BROKEN

#### 20-investment-dashboard
- **Code**: 2,753 chars
- **Issue**: ❌ No API endpoints
- **Status**: BROKEN

#### 21-water-quality-tracker
- **Code**: 954 chars
- **Issue**: ❌ No API endpoints
- **Status**: BROKEN

#### 22-event-impact-analyzer
- **Code**: 1,372 chars
- **Issue**: ❌ No API endpoints
- **Status**: BROKEN

---

## Common Issues Found

### 1. **Empty Output (Most Common)**
- 40 projects have valid code but produce no data or empty HTML
- HTML files either don't exist or contain empty table rows
- Suggests API calls may be failing or returning no results

### 2. **Generic Template Code**
- 16 projects appear to use a minimal template (~919 chars)
- Code structure exists but lacks real implementation
- Examples: 08-traffic-incidents, 09-water-consumption, 10-pathways, etc.

### 3. **Large Plotly Files with No Data**
- Several projects generate 4.8MB HTML files
- Files contain Plotly visualization library but no actual data points
- Examples: 03-crime-value-arbitrage, 04-transit-development-radar, 07-snow-plow-tracker

### 4. **Duplicate Projects**
- 3 sets of duplicates consuming 6 project slots
- Likely created by mistake during batch generation

### 5. **Missing API Endpoints**
- 7 projects have no Calgary Open Data API calls at all
- These appear to be placeholder projects

---

## Recommendations

### Immediate Actions

1. **Delete Duplicates** (Priority: HIGH)
   - Remove: `02-311-complaint-heatmap` (keep 06)
   - Remove: `06-park-quality-scorer` (keep 16)
   - Remove: `19-gentrification-index` (keep 26)
   - **Result**: Reduce from 49 to 46 projects

2. **Delete/Archive Generic Templates** (Priority: HIGH)
   - 16 projects are essentially empty templates
   - Either implement them properly or remove them
   - Templates: 08-traffic-incidents, 09-water-consumption, 10-pathways, 11-community-services, 12-election-results, 14-fire-response, 15-property-tax, 16-development-permits, 17-playgrounds, 18-solar-potential, 19-tree-canopy, 20-city-budget, 21-bylaw-complaints, 22-heritage-properties, 23-demographics, 24-libraries

3. **Fix or Remove Broken Projects** (Priority: MEDIUM)
   - 7 projects with no API endpoints or missing main.py
   - Either add real implementation or remove

4. **Investigate Data Fetch Issues** (Priority: HIGH)
   - Test API endpoints - many may be returning empty results
   - Check API rate limits
   - Verify dataset IDs are still valid on Calgary Open Data portal
   - Add error handling and logging to main.py files

### Long-term Improvements

1. **Add Data Validation**
   - Check if API calls return data before generating output
   - Log warnings when datasets are empty
   - Display friendly error messages in HTML output

2. **Create Automated Testing**
   - Script to run all main.py files with timeout
   - Validate that HTML outputs contain actual data
   - Check for API endpoint validity

3. **Documentation**
   - Add README to each working project
   - Document data sources and update frequency
   - Include example outputs

4. **Consolidation**
   - Group related projects (all crime projects, all transit projects, etc.)
   - Create a master dashboard linking to individual analyses

---

## Cleanup Plan

### Phase 1: Delete (Immediate)
- **Delete duplicates**: 3 projects
- **Delete broken (no API)**: 7 projects  
- **Delete generic templates**: 16 projects
- **Total reduction**: 26 projects → **23 remaining**

### Phase 2: Fix (1-2 weeks)
- Test remaining 23 projects individually
- Fix API calls and data processing
- Ensure HTML outputs contain real data
- Target: Get 15-20 projects fully working

### Phase 3: Enhancement (Ongoing)
- Add proper error handling
- Create automated tests
- Build master dashboard
- Add documentation

---

## Conclusion

The Calgary Open Data Tools project contains a large amount of code (48 projects with valid Python), but **only 4% are producing usable output**. The primary issues are:

1. **Empty/failed API calls** - Code runs but gets no data
2. **Template bloat** - 33% of projects are incomplete templates
3. **Duplicates** - 6% of projects are duplicates
4. **No validation** - No checks if data actually exists

**Recommended Action:** Delete 26 projects immediately (duplicates + broken + templates), then focus on fixing the remaining 23 to achieve a 65-87% working rate.

**Estimated Effort:**
- Cleanup (delete 26): **1 hour**
- Fix APIs (test & repair): **2-3 days**
- Add validation & tests: **1-2 days**
- Documentation: **1 day**

**Total**: ~1 week to go from 4% working to 65%+ working projects.
