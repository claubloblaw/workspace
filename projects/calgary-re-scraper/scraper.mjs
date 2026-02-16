#!/usr/bin/env node
/**
 * Calgary Real Estate Scraper — Realtor.ca API
 * 
 * Two search profiles:
 * 1. "walkout" — Big walkout bungalows in SW/SE Calgary
 * 2. "rental"  — Rental yield potential (condos, multi-family, affordable homes)
 * 
 * Flags: judicial sales, estate sales, price drops, high DOM
 */

import { writeFileSync, readFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = join(__dirname, 'data');
if (!existsSync(DATA_DIR)) mkdirSync(DATA_DIR, { recursive: true });

const API_URL = 'https://api37.realtor.ca/Listing.svc/PropertySearch_Post';
const DETAIL_URL = 'https://api37.realtor.ca/Listing.svc/PropertyDetails';

// Calgary quadrant boundaries
// Centre St ≈ -114.0625, Bow River ≈ 51.045
const BOUNDS = {
  SW: { LatitudeMin: 50.88, LatitudeMax: 51.045, LongitudeMin: -114.315, LongitudeMax: -114.0625 },
  SE: { LatitudeMin: 50.88, LatitudeMax: 51.045, LongitudeMin: -114.0625, LongitudeMax: -113.90 },
};

// Search profiles
const PROFILES = {
  walkout: {
    name: 'Walkout Bungalows (SW+SE)',
    description: 'Big bungalows with walkout potential',
    params: {
      PropertySearchTypeId: 1, // Residential
      TransactionTypeId: 2,    // For sale
      PriceMin: 500000,
      PriceMax: 1200000,
      BuildingTypeId: 1,       // House
      StoreyRange: '1-1',      // Bungalow (single storey)
      BedRange: '3-0',         // 3+
      BathRange: '2-0',        // 2+
      // Keywords to look for in post-processing: walkout, walk-out, backing, ravine, park, river
    },
  },
  rental: {
    name: 'Rental Yield (SW+SE)',
    description: 'Properties with rental income potential',
    params: {
      PropertySearchTypeId: 0, // No preference (houses + condos + multi)
      TransactionTypeId: 2,    // For sale
      PriceMin: 150000,
      PriceMax: 600000,
      BedRange: '1-0',         // 1+
    },
  },
};

const HEADERS = {
  'Content-Type': 'application/x-www-form-urlencoded',
  'Origin': 'https://www.realtor.ca',
  'Referer': 'https://www.realtor.ca/',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
};

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function searchPage(params, page = 1) {
  const body = new URLSearchParams({
    CultureId: '1',
    ApplicationId: '37',
    HashCode: '0',
    RecordsPerPage: '50',
    CurrentPage: String(page),
    SortBy: '6',       // Date posted
    SortOrder: 'D',    // Newest first
    ...params,
  });

  // Convert bounds to params
  for (const [k, v] of Object.entries(params)) {
    body.set(k, String(v));
  }

  const res = await fetch(API_URL, { method: 'POST', headers: HEADERS, body: body.toString() });
  if (!res.ok) {
    console.error(`API error: ${res.status} ${res.statusText}`);
    return null;
  }
  return res.json();
}

async function fetchAllListings(profileKey, quadrant) {
  const profile = PROFILES[profileKey];
  const bounds = BOUNDS[quadrant];
  const params = { ...profile.params, ...bounds };
  
  let allResults = [];
  let page = 1;
  let totalPages = 1;

  while (page <= totalPages) {
    console.log(`  [${quadrant}] Page ${page}/${totalPages}...`);
    const data = await searchPage(params, page);
    if (!data || !data.Results) break;
    
    totalPages = Math.ceil(data.Paging.TotalRecords / data.Paging.RecordsPerPage);
    allResults.push(...data.Results);
    
    page++;
    if (page <= totalPages) await sleep(2000); // Rate limit respect
  }
  
  return allResults;
}

function scoreListing(listing, profileKey) {
  const score = { total: 0, flags: [] };
  const desc = (listing.PublicRemarks || '').toLowerCase();
  const building = listing.Building || {};
  const property = listing.Property || {};
  const land = listing.Land || {};
  const addr = property.Address || {};
  
  // === Universal flags ===
  
  // Judicial / court-ordered sale
  if (desc.match(/judicial|court.?order|foreclos|bank.?own|power.?of.?sale|lender.?sale/i)) {
    score.total += 30;
    score.flags.push('🏛️ JUDICIAL/FORECLOSURE');
  }
  
  // Estate sale
  if (desc.match(/estate.?sale|probate|executor|deceased|passed away/i)) {
    score.total += 20;
    score.flags.push('⚰️ ESTATE SALE');
  }
  
  // Motivated seller signals
  if (desc.match(/must.?sell|motiv|relocat|divorce|price.?reduc|below.?assess|quick.?sale|urgent|as.?is/i)) {
    score.total += 15;
    score.flags.push('🔥 MOTIVATED');
  }
  
  // Days on market
  const dom = listing.DaysOnMarket || listing.InsertedDateUTC;
  if (dom && typeof dom === 'number' && dom > 90) {
    score.total += 10;
    score.flags.push(`📅 ${dom} DOM`);
  }
  
  // Price drop (checking price history would need detail API)
  if (desc.match(/price.?reduc|new.?price|just.?reduced/i)) {
    score.total += 10;
    score.flags.push('📉 PRICE REDUCED');
  }

  // === Walkout-specific ===
  if (profileKey === 'walkout') {
    if (desc.match(/walk.?out|walkout/i)) {
      score.total += 25;
      score.flags.push('🚪 WALKOUT');
    }
    if (desc.match(/ravin|creek|park|river|pond|lake|coulee|escarpment|bluff/i)) {
      score.total += 15;
      score.flags.push('🌲 BACKING NATURE');
    }
    if (desc.match(/develop|suite|in.?law|legal.?suite|basement.?suite/i)) {
      score.total += 10;
      score.flags.push('🏠 SUITE POTENTIAL');
    }
    // Lot size bonus
    const sqft = land.SizeTotal ? parseFloat(land.SizeTotal) : 0;
    if (sqft > 6000) {
      score.total += 10;
      score.flags.push(`📐 BIG LOT ${land.SizeTotal}`);
    }
  }

  // === Rental-specific ===
  if (profileKey === 'rental') {
    if (desc.match(/legal.?suite|basement.?suite|secondary.?suite|in.?law|rental.?income|revenue|tenant|rented/i)) {
      score.total += 25;
      score.flags.push('💰 RENTAL INCOME');
    }
    if (desc.match(/duplex|triplex|fourplex|multi.?family|side.?by.?side/i)) {
      score.total += 20;
      score.flags.push('🏘️ MULTI-UNIT');
    }
    // Price per bed ratio (lower = better yield)
    const price = parseFloat((listing.Property?.Price || '0').replace(/[^0-9.]/g, ''));
    const beds = parseInt(building.Bedrooms) || 1;
    if (price > 0 && price / beds < 150000) {
      score.total += 15;
      score.flags.push(`💎 $${Math.round(price/beds/1000)}k/bed`);
    }
    // Near transit / university keywords
    if (desc.match(/c.?train|lrt|transit|university|sait|mru|u.?of.?c/i)) {
      score.total += 10;
      score.flags.push('🚇 TRANSIT/UNI');
    }
  }

  return score;
}

function formatListing(listing, score) {
  const prop = listing.Property || {};
  const bldg = listing.Building || {};
  const addr = prop.Address || {};
  const price = prop.Price || 'N/A';
  const beds = bldg.Bedrooms || '?';
  const baths = bldg.BathroomTotal || '?';
  const sqft = bldg.SizeInterior || 'N/A';
  const type = bldg.Type || prop.Type || 'N/A';
  const mlsNum = listing.MlsNumber || 'N/A';
  const address = `${addr.AddressText || 'Unknown'}`;
  const url = `https://www.realtor.ca${listing.RelativeURLEn || ''}`;
  const flags = score.flags.length ? score.flags.join(' ') : '';
  const dom = listing.DaysOnMarket ? `${listing.DaysOnMarket}d` : '';

  return {
    score: score.total,
    flags,
    mlsNum,
    price,
    address,
    beds,
    baths,
    sqft,
    type,
    dom,
    url,
    remarks: (listing.PublicRemarks || '').substring(0, 200),
  };
}

async function runProfile(profileKey) {
  const profile = PROFILES[profileKey];
  console.log(`\n🔍 Running: ${profile.name}`);
  
  let allListings = [];
  for (const quad of ['SW', 'SE']) {
    console.log(`  Searching ${quad}...`);
    const results = await fetchAllListings(profileKey, quad);
    console.log(`  Found ${results.length} in ${quad}`);
    allListings.push(...results);
    await sleep(3000);
  }

  // Deduplicate by MLS number
  const seen = new Set();
  allListings = allListings.filter(l => {
    if (seen.has(l.MlsNumber)) return false;
    seen.add(l.MlsNumber);
    return true;
  });
  console.log(`  ${allListings.length} unique listings after dedup`);

  // Score and format
  const scored = allListings.map(l => {
    const score = scoreListing(l, profileKey);
    return formatListing(l, score);
  });

  // Sort by score descending
  scored.sort((a, b) => b.score - a.score);

  return scored;
}

async function main() {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
  const results = {};
  
  for (const profileKey of Object.keys(PROFILES)) {
    results[profileKey] = await runProfile(profileKey);
    await sleep(5000); // Between profiles
  }

  // Save full results
  const outFile = join(DATA_DIR, `scan-${timestamp}.json`);
  writeFileSync(outFile, JSON.stringify(results, null, 2));
  console.log(`\n💾 Full results saved to ${outFile}`);

  // Load previous results for diff
  const latestFile = join(DATA_DIR, 'latest.json');
  let previousMLS = new Set();
  if (existsSync(latestFile)) {
    try {
      const prev = JSON.parse(readFileSync(latestFile, 'utf8'));
      for (const key of Object.keys(prev)) {
        for (const l of prev[key]) previousMLS.add(l.mlsNum);
      }
    } catch {}
  }

  // Generate summary
  let summary = `# Calgary RE Scan — ${new Date().toLocaleString('en-CA', { timeZone: 'America/Edmonton' })}\n\n`;
  
  for (const [profileKey, listings] of Object.entries(results)) {
    const profile = PROFILES[profileKey];
    const topListings = listings.filter(l => l.score > 0).slice(0, 15);
    const newListings = listings.filter(l => !previousMLS.has(l.mlsNum));
    
    summary += `## ${profile.name}\n`;
    summary += `Total: ${listings.length} | Flagged: ${topListings.length} | New: ${newListings.length}\n\n`;
    
    if (topListings.length === 0) {
      summary += `No high-signal listings found.\n\n`;
      continue;
    }

    for (const l of topListings) {
      const isNew = !previousMLS.has(l.mlsNum) ? '🆕 ' : '';
      summary += `### ${isNew}${l.address}\n`;
      summary += `**${l.price}** | ${l.beds}bd/${l.baths}ba | ${l.sqft} | ${l.type} | MLS# ${l.mlsNum} ${l.dom}\n`;
      summary += `Score: ${l.score} | ${l.flags}\n`;
      summary += `${l.url}\n`;
      if (l.remarks) summary += `> ${l.remarks}...\n`;
      summary += `\n`;
    }
  }

  // Save summary and update latest
  const summaryFile = join(DATA_DIR, `summary-${timestamp}.md`);
  writeFileSync(summaryFile, summary);
  writeFileSync(latestFile, JSON.stringify(results, null, 2));
  writeFileSync(join(DATA_DIR, 'latest-summary.md'), summary);
  
  console.log(`📊 Summary saved to ${summaryFile}`);
  console.log(summary);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
