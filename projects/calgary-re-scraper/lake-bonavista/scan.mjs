#!/usr/bin/env node
/**
 * Lake Bonavista Intelligence System
 * 
 * 1. Pulls ALL Lake Bonavista assessed values from Calgary Open Data (free API)
 * 2. Pulls ALL Lake Bonavista Realtor.ca listings via browser CDP
 * 3. Cross-references: assessed value vs listing price = discount/premium %
 * 4. Flags: judicial sales, estate sales, motivated sellers, price drops, high DOM
 * 5. Monitors new/removed listings between scans
 */

import { chromium } from 'playwright';
import { writeFileSync, readFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = join(__dirname, 'data');
if (!existsSync(DATA_DIR)) mkdirSync(DATA_DIR, { recursive: true });

const CDP_URL = 'http://127.0.0.1:18800';
const SOCRATA_BASE = 'https://data.calgary.ca/resource/4bsw-nn7w.json';

// ===== STEP 1: Fetch all Lake Bonavista assessments =====
async function fetchAssessments() {
  console.log('📊 Fetching Lake Bonavista assessments from Calgary Open Data...');
  const allRecords = [];
  let offset = 0;
  const limit = 1000;
  
  while (true) {
    const url = `${SOCRATA_BASE}?$where=COMM_NAME='LAKE BONAVISTA' AND assessment_class='RE' AND assessed_value>0&$limit=${limit}&$offset=${offset}&$order=address`;
    const res = await fetch(url);
    const data = await res.json();
    if (data.length === 0) break;
    allRecords.push(...data);
    offset += limit;
    if (data.length < limit) break;
  }
  
  console.log(`  ✅ ${allRecords.length} residential properties`);
  
  // Build address -> assessment lookup
  const assessmentMap = {};
  for (const r of allRecords) {
    // Normalize address for matching
    const addr = normalizeAddress(r.address);
    assessmentMap[addr] = {
      assessed: parseFloat(r.assessed_value),
      rollNumber: r.roll_number,
      yearBuilt: r.year_of_construction ? parseInt(r.year_of_construction) : null,
      zoning: r.land_use_designation,
      lotSqft: parseFloat(r.land_size_sf) || 0,
      lotSqm: parseFloat(r.land_size_sm) || 0,
      propertyType: r.property_type,
      address: r.address,
    };
  }
  
  return { records: allRecords, map: assessmentMap };
}

function normalizeAddress(addr) {
  if (!addr) return '';
  return addr
    .toUpperCase()
    .replace(/\s+/g, ' ')
    .replace(/\bSTREET\b/g, 'ST')
    .replace(/\bAVENUE\b/g, 'AV')
    .replace(/\bDRIVE\b/g, 'DR')
    .replace(/\bCRESCENT\b/g, 'CR')
    .replace(/\bBOULEVARD\b/g, 'BV')
    .replace(/\bROAD\b/g, 'RD')
    .replace(/\bPLACE\b/g, 'PL')
    .replace(/\bCOURT\b/g, 'CO')
    .replace(/\bCLOSE\b/g, 'CL')
    .replace(/\bBAY\b/g, 'BA')
    .replace(/\bWAY\b/g, 'WY')
    .replace(/\bTERRACE\b/g, 'TC')
    .replace(/\bGREEN\b/g, 'GR')
    .replace(/\bGATE\b/g, 'GA')
    .replace(/\bPARK\b/g, 'PA')
    .replace(/\bGARDENS?\b/g, 'GD')
    .replace(/\bLANE\b/g, 'LA')
    .replace(/\bMANOR\b/g, 'MR')
    .replace(/\bMEWS\b/g, 'ME')
    .replace(/\bPOINT\b/g, 'PT')
    .replace(/\bRISE\b/g, 'RI')
    .replace(/\bVIEW\b/g, 'VW')
    .replace(/\bSOUTHEAST\b/g, 'SE')
    .replace(/\bSOUTHWEST\b/g, 'SW')
    .replace(/\bNORTHEAST\b/g, 'NE')
    .replace(/\bNORTHWEST\b/g, 'NW')
    .replace(/,.*$/, '') // Strip city/province
    .trim();
}

// ===== STEP 2: Fetch Realtor.ca Lake Bonavista listings =====
async function fetchListings(context) {
  console.log('\n🔍 Fetching Lake Bonavista listings from Realtor.ca...');
  
  // Lake Bonavista bounds (tight)
  // Roughly: 50.925-50.945 lat, -114.085 to -114.050 lon
  const searchUrl = 'https://www.realtor.ca/map#ZoomLevel=14&Center=50.935000%2C-114.067500&LatitudeMax=50.945&LongitudeMax=-114.050&LatitudeMin=50.925&LongitudeMin=-114.085&Sort=6-D&GeoName=Lake%20Bonavista%2C%20Calgary%2C%20AB&PropertyTypeGroupID=1&TransactionTypeId=2&BuildingTypeId=1&Currency=CAD';
  
  const page = await context.newPage();
  let allListings = [];
  let totalRecords = 0;
  let captureResolve = null;

  page.on('response', async (response) => {
    const url = response.url();
    if (url.includes('PropertySearch_Post') || url.includes('PropertySearch')) {
      try {
        const json = await response.json();
        if (json.Results) {
          allListings.push(...json.Results);
          totalRecords = json.Paging?.TotalRecords || totalRecords;
          console.log(`  API: +${json.Results.length} (total: ${allListings.length}/${totalRecords})`);
          if (captureResolve) captureResolve();
        }
      } catch {}
    }
  });

  function waitForCapture(timeoutMs = 10000) {
    return new Promise((resolve) => {
      captureResolve = resolve;
      setTimeout(resolve, timeoutMs);
    });
  }

  await page.goto(searchUrl, { waitUntil: 'networkidle', timeout: 45000 });
  await page.waitForTimeout(5000);

  // Paginate
  const maxPages = 20;
  let pageNum = 1;
  while (allListings.length < totalRecords && pageNum < maxPages) {
    try {
      const selectors = [
        'a.lnkNextResultsPage',
        'a[title="Next"]',
        `.paginator a:has-text("${pageNum + 1}")`,
        `a[title="Page ${pageNum + 1}"]`,
        '[class*="next"]',
      ];
      let clicked = false;
      for (const sel of selectors) {
        try {
          const el = page.locator(sel).first();
          if (await el.isVisible({ timeout: 1000 })) {
            const prevCount = allListings.length;
            await el.click();
            await waitForCapture(8000);
            await page.waitForTimeout(1500);
            if (allListings.length > prevCount) {
              clicked = true;
              pageNum++;
              break;
            }
          }
        } catch {}
      }
      if (!clicked) {
        const prevCount = allListings.length;
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await waitForCapture(5000);
        if (allListings.length <= prevCount) break;
        pageNum++;
      }
    } catch { break; }
  }

  await page.close();

  // Deduplicate
  const seen = new Set();
  allListings = allListings.filter(l => {
    if (seen.has(l.MlsNumber)) return false;
    seen.add(l.MlsNumber);
    return true;
  });
  console.log(`  ✅ ${allListings.length} unique listings`);
  return allListings;
}

// ===== STEP 3: Cross-reference and score =====
function analyzeListing(listing, assessmentMap) {
  const flags = [];
  let score = 0;
  const desc = (listing.PublicRemarks || '').toLowerCase();
  const price = listing.Property?.PriceUnformattedValue || 0;
  const timeOnSite = listing.TimeOnRealtor || '';
  const priceChange = listing.Property?.PriceChangeTimeOnRealtor || '';
  const addr = listing.Property?.Address?.AddressText || '';

  // Try to match assessment
  const normalAddr = normalizeAddress(addr.split('|')[0]);
  let assessment = assessmentMap[normalAddr];
  
  // Fuzzy match if exact fails — try stripping unit numbers, etc.
  if (!assessment) {
    // Try without leading unit number
    const stripped = normalAddr.replace(/^\d+\s*,?\s*/, '');
    assessment = assessmentMap[stripped];
  }

  let assessedValue = assessment?.assessed || 0;
  let discountPct = 0;
  
  if (assessedValue > 0 && price > 0) {
    discountPct = ((assessedValue - price) / assessedValue * 100);
    if (discountPct > 15) {
      score += 25; flags.push(`🏷️ ${discountPct.toFixed(0)}% BELOW ASSESSED ($${(assessedValue/1000).toFixed(0)}k)`);
    } else if (discountPct > 10) {
      score += 18; flags.push(`🏷️ ${discountPct.toFixed(0)}% BELOW ASSESSED ($${(assessedValue/1000).toFixed(0)}k)`);
    } else if (discountPct > 5) {
      score += 10; flags.push(`🏷️ ${discountPct.toFixed(0)}% BELOW ASSESSED ($${(assessedValue/1000).toFixed(0)}k)`);
    } else if (discountPct < -20) {
      flags.push(`📈 ${Math.abs(discountPct).toFixed(0)}% ABOVE ASSESSED ($${(assessedValue/1000).toFixed(0)}k)`);
    }
  }

  // Judicial / foreclosure
  if (/judicial|court.?order|foreclos|bank.?own|power.?of.?sale|lender/i.test(desc)) {
    score += 35; flags.push('🏛️ JUDICIAL/FORECLOSURE');
  }
  // Estate sale
  if (/estate.?sale|probate|executor|deceased/i.test(desc)) {
    score += 25; flags.push('⚰️ ESTATE SALE');
  }
  // Motivated seller
  if (/must.?sell|motiv|relocat|divorce|urgent|as.?is|quick.?close/i.test(desc)) {
    score += 15; flags.push('🔥 MOTIVATED');
  }
  // Price reduced
  if (priceChange) {
    score += 12; flags.push(`📉 PRICE DROP (${priceChange} ago)`);
  } else if (/price.?reduc|new.?price|just.?reduced/i.test(desc)) {
    score += 10; flags.push('📉 PRICE DROP');
  }
  // Days on market
  const dom = parseDom(timeOnSite);
  if (dom > 120) { score += 15; flags.push(`📅 ${timeOnSite}`); }
  else if (dom > 90) { score += 10; flags.push(`📅 ${timeOnSite}`); }
  else if (dom > 60) { score += 5; flags.push(`📅 ${timeOnSite}`); }

  // Walkout
  if (/walk.?out|walkout/i.test(desc)) { score += 15; flags.push('🚪 WALKOUT'); }
  // Backing nature/lake
  if (/lake|water|ravin|creek|park|pathway|backing/i.test(desc)) { score += 10; flags.push('🌊 LAKE/NATURE'); }
  // Suite
  if (/suite|in.?law|legal.?suite|secondary/i.test(desc)) { score += 10; flags.push('🏠 SUITE'); }
  // Fixer-upper signals
  if (/renovat|updat|fixer|handyman|tlc|potential|opportunity|original|dated/i.test(desc)) {
    score += 8; flags.push('🔨 FIXER');
  }

  return {
    score,
    flags,
    discountPct,
    assessedValue,
    assessment,
  };
}

function parseDom(timeStr) {
  if (!timeStr) return 0;
  const m = timeStr.match(/(\d+)/);
  if (!m) return 0;
  const num = parseInt(m[1]);
  if (/month/i.test(timeStr)) return num * 30;
  if (/year/i.test(timeStr)) return num * 365;
  if (/week/i.test(timeStr)) return num * 7;
  return num;
}

// ===== STEP 4: Generate report =====
function generateReport(listings, assessmentMap, previousMLS) {
  const analyzed = listings.map(l => {
    const analysis = analyzeListing(l, assessmentMap);
    const isNew = !previousMLS.has(l.MlsNumber);
    return { listing: l, ...analysis, isNew };
  }).sort((a, b) => b.score - a.score);

  const flagged = analyzed.filter(a => a.score > 0);
  const newOnes = analyzed.filter(a => a.isNew);
  const withDiscount = analyzed.filter(a => a.discountPct > 5);

  let md = `# 🏠 Lake Bonavista Intelligence Report\n`;
  md += `**${new Date().toLocaleString('en-CA', { timeZone: 'America/Edmonton' })}**\n\n`;
  md += `**Active listings:** ${listings.length} | **Flagged:** ${flagged.length} | **New:** ${newOnes.length} | **Below assessed:** ${withDiscount.length}\n\n`;

  // === BIGGEST ASSESSMENT GAPS ===
  const discounted = analyzed.filter(a => a.discountPct > 0).sort((a, b) => b.discountPct - a.discountPct);
  if (discounted.length > 0) {
    md += `## 📊 Assessment vs Listing Price (Biggest Gaps)\n\n`;
    md += `| Address | Listed | Assessed | Gap | Score | Flags |\n`;
    md += `|---------|--------|----------|-----|-------|-------|\n`;
    for (const a of discounted.slice(0, 20)) {
      const l = a.listing;
      const p = l.Property || {};
      const addr = (p.Address?.AddressText || '').split('|')[0].trim();
      const listed = p.Price || 'N/A';
      const assessed = a.assessedValue > 0 ? `$${(a.assessedValue/1000).toFixed(0)}k` : 'N/A';
      const gap = a.discountPct > 0 ? `**-${a.discountPct.toFixed(1)}%**` : `+${Math.abs(a.discountPct).toFixed(1)}%`;
      const flagStr = a.flags.filter(f => !f.includes('ASSESSED')).join(' ');
      md += `| ${addr} | ${listed} | ${assessed} | ${gap} | ${a.score} | ${flagStr} |\n`;
    }
    md += '\n';
  }

  // === TOP SCORED LISTINGS ===
  if (flagged.length > 0) {
    md += `## 🎯 Top Scored Listings\n\n`;
    flagged.slice(0, 20).forEach((a, i) => {
      const l = a.listing;
      const p = l.Property || {};
      const b = l.Building || {};
      const newTag = a.isNew ? ' 🆕' : '';
      
      md += `### ${i + 1}. ${p.Address?.AddressText || 'Unknown'}${newTag}\n`;
      md += `**${p.Price}** | ${b.Bedrooms || '?'}bd/${b.BathroomTotal || '?'}ba | ${b.SizeInterior || 'N/A'} | ${b.Type || p.Type || 'N/A'}\n`;
      if (a.assessedValue > 0) {
        md += `Assessed: **$${(a.assessedValue/1000).toFixed(0)}k** (${a.discountPct > 0 ? a.discountPct.toFixed(1) + '% below' : Math.abs(a.discountPct).toFixed(1) + '% above'})\n`;
      }
      md += `Score: **${a.score}** | ${a.flags.join(' ')}\n`;
      md += `${l.TimeOnRealtor || 'New'} | [View](https://www.realtor.ca${l.RelativeURLEn || ''})\n`;
      if (l.PublicRemarks && a.score >= 20) {
        md += `> ${l.PublicRemarks.substring(0, 250)}...\n`;
      }
      md += '\n';
    });
  }

  // === NEW LISTINGS ===
  if (newOnes.length > 0 && previousMLS.size > 0) {
    md += `## 🆕 New Since Last Scan\n\n`;
    newOnes.forEach(a => {
      const l = a.listing;
      const p = l.Property || {};
      md += `- **${p.Price}** | ${p.Address?.AddressText || '?'} | Score: ${a.score} | [View](https://www.realtor.ca${l.RelativeURLEn || ''})\n`;
    });
    md += '\n';
  }

  // === DELISTED (were in previous, not in current) ===
  // We'll handle this outside

  // Alerts (score >= 50)
  const alerts = analyzed.filter(a => a.score >= 50 && a.isNew).map(a => ({
    score: a.score,
    flags: a.flags.join(' '),
    price: a.listing.Property?.Price,
    address: a.listing.Property?.Address?.AddressText || 'Unknown',
    assessed: a.assessedValue,
    discount: a.discountPct,
    url: `https://www.realtor.ca${a.listing.RelativeURLEn || ''}`,
    mls: a.listing.MlsNumber,
  }));

  return { md, analyzed, alerts };
}

async function main() {
  // Step 1: Assessments
  const { records: assessmentRecords, map: assessmentMap } = await fetchAssessments();

  // Step 2: Listings
  console.log('Connecting to Chrome via CDP...');
  const browser = await chromium.connectOverCDP(CDP_URL);
  const contexts = browser.contexts();
  const context = contexts[0] || await browser.newContext();
  
  const listings = await fetchListings(context);
  await browser.close();

  // Load previous scan
  const latestFile = join(DATA_DIR, 'latest.json');
  let previousMLS = new Set();
  if (existsSync(latestFile)) {
    try {
      const prev = JSON.parse(readFileSync(latestFile, 'utf8'));
      if (prev.listings) prev.listings.forEach(l => previousMLS.add(l.MlsNumber));
    } catch {}
  }

  // Step 3 & 4: Analyze and report
  const { md, analyzed, alerts } = generateReport(listings, assessmentMap, previousMLS);

  // Check for delisted
  if (previousMLS.size > 0) {
    const currentMLS = new Set(listings.map(l => l.MlsNumber));
    const delisted = [...previousMLS].filter(m => !currentMLS.has(m));
    if (delisted.length > 0) {
      // Append to report
      // (We'd need previous listing data to show details, just flag the MLS numbers for now)
    }
  }

  // Save
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
  writeFileSync(join(DATA_DIR, `report-${timestamp}.md`), md);
  writeFileSync(join(DATA_DIR, 'latest-report.md'), md);
  writeFileSync(latestFile, JSON.stringify({ listings, assessments: assessmentRecords.length, timestamp }, null, 2));
  if (alerts.length > 0) {
    writeFileSync(join(DATA_DIR, 'alerts.json'), JSON.stringify(alerts, null, 2));
  }

  console.log(`\n💾 Report saved`);
  console.log(md);
}

main().catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});
