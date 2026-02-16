#!/usr/bin/env node
/**
 * Calgary RE Deal Finder
 * Connects to OpenClaw Chrome via CDP, navigates Realtor.ca, intercepts API data.
 * Scores listings for walkout bungalow + rental yield profiles.
 * Outputs markdown summary with top deals.
 */

import { chromium } from 'playwright';
import { writeFileSync, readFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = join(__dirname, 'data');
if (!existsSync(DATA_DIR)) mkdirSync(DATA_DIR, { recursive: true });

const CDP_URL = 'http://127.0.0.1:18800';

const SEARCHES = [
  {
    key: 'walkout',
    name: 'Walkout Bungalows (SW+SE Calgary)',
    url: 'https://www.realtor.ca/map#ZoomLevel=11&Center=50.962500%2C-114.107500&LatitudeMax=51.04500&LongitudeMax=-113.90000&LatitudeMin=50.88000&LongitudeMin=-114.31500&Sort=6-D&GeoName=Calgary%2C%20AB&PropertyTypeGroupID=1&TransactionTypeId=2&PriceMin=500000&PriceMax=1200000&BuildingTypeId=1&BedRange=3-0&BathRange=2-0&StoreyRange=1-2&Currency=CAD',
  },
  {
    key: 'rental',
    name: 'Rental Yield (SW+SE Calgary)',
    // BuildingTypeId=1 = House (detached only)
    url: 'https://www.realtor.ca/map#ZoomLevel=11&Center=50.962500%2C-114.107500&LatitudeMax=51.04500&LongitudeMax=-113.90000&LatitudeMin=50.88000&LongitudeMin=-114.31500&Sort=6-D&GeoName=Calgary%2C%20AB&PropertyTypeGroupID=1&TransactionTypeId=2&PriceMin=150000&PriceMax=600000&BuildingTypeId=1&Currency=CAD',
  },
];

async function collectListings(context, search) {
  console.log(`\n🔍 ${search.name}`);
  const page = await context.newPage();
  let allListings = [];
  let totalRecords = 0;
  let captureResolve = null;

  // Intercept API responses
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

  // Helper: wait for next API capture
  function waitForCapture(timeoutMs = 10000) {
    return new Promise((resolve) => {
      captureResolve = resolve;
      setTimeout(resolve, timeoutMs);
    });
  }

  // Initial load
  await page.goto(search.url, { waitUntil: 'networkidle', timeout: 45000 });
  await page.waitForTimeout(5000);

  // Switch to List view for pagination
  try {
    await page.click('text=List', { timeout: 5000 });
    await page.waitForTimeout(3000);
  } catch (e) {
    console.log('  Could not switch to List view');
  }

  // Paginate
  const maxPages = 30;
  let pageNum = 1;
  
  while (allListings.length < totalRecords && pageNum < maxPages) {
    // Look for pagination controls
    try {
      // Try multiple selectors for the "next page" button
      const nextSelectors = [
        'a.lnkNextResultsPage',
        'a[title="Next"]',
        '.paginationLink:has-text("Next")',
        '.paginator li:last-child a',
        'button:has-text("Next")',
        '[class*="next"]',
        // Page number links — click the next page number
        `.paginator a:has-text("${pageNum + 1}")`,
        `a[title="Page ${pageNum + 1}"]`,
      ];
      
      let clicked = false;
      for (const sel of nextSelectors) {
        try {
          const el = page.locator(sel).first();
          if (await el.isVisible({ timeout: 1000 })) {
            const prevCount = allListings.length;
            await el.click();
            // Wait for new API data
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
        // Try scrolling to load more (some views use infinite scroll)
        const prevCount = allListings.length;
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await waitForCapture(5000);
        if (allListings.length <= prevCount) {
          console.log(`  Pagination stopped at page ${pageNum} (${allListings.length} listings)`);
          break;
        }
        pageNum++;
      }
    } catch (e) {
      console.log(`  Pagination error: ${e.message}`);
      break;
    }
  }

  await page.close();

  // Deduplicate by MLS
  const seen = new Set();
  allListings = allListings.filter(l => {
    if (seen.has(l.MlsNumber)) return false;
    seen.add(l.MlsNumber);
    return true;
  });
  console.log(`  ✅ ${allListings.length} unique listings collected`);
  return allListings;
}

function parseDaysOnMarket(timeStr) {
  if (!timeStr) return 0;
  const m = timeStr.match(/(\d+)/);
  if (!m) return 0;
  const num = parseInt(m[1]);
  if (/month/i.test(timeStr)) return num * 30;
  if (/year/i.test(timeStr)) return num * 365;
  if (/week/i.test(timeStr)) return num * 7;
  return num; // days
}

function scoreListing(l, profileKey) {
  const flags = [];
  let score = 0;
  const desc = (l.PublicRemarks || '').toLowerCase();
  const price = l.Property?.PriceUnformattedValue || 0;
  const beds = parseInt(l.Building?.Bedrooms) || 0;
  const baths = parseInt(l.Building?.BathroomTotal) || 0;
  const storeys = l.Building?.StoriesTotal || '';
  const lot = l.Land?.SizeTotal || '';
  const timeOnSite = l.TimeOnRealtor || '';
  const priceChange = l.Property?.PriceChangeTimeOnRealtor || '';
  const dom = parseDaysOnMarket(timeOnSite);

  // === UNIVERSAL SIGNALS ===
  if (/judicial|court.?order|foreclos|bank.?own|power.?of.?sale|lender/i.test(desc)) {
    score += 30; flags.push('🏛️ JUDICIAL');
  }
  if (/estate.?sale|probate|executor|deceased/i.test(desc)) {
    score += 20; flags.push('⚰️ ESTATE');
  }
  if (/must.?sell|motiv|relocat|divorce|urgent|as.?is|quick.?close/i.test(desc)) {
    score += 15; flags.push('🔥 MOTIVATED');
  }
  if (priceChange) {
    score += 12; flags.push(`📉 PRICE DROP (${priceChange} ago)`);
  } else if (/price.?reduc|new.?price|just.?reduced/i.test(desc)) {
    score += 10; flags.push('📉 PRICE DROP');
  }
  if (dom > 120) {
    score += 15; flags.push(`📅 ${timeOnSite}`);
  } else if (dom > 90) {
    score += 10; flags.push(`📅 ${timeOnSite}`);
  } else if (dom > 60) {
    score += 5; flags.push(`📅 ${timeOnSite}`);
  }

  // === WALKOUT PROFILE ===
  if (profileKey === 'walkout') {
    if (/walk.?out|walkout/i.test(desc)) {
      score += 25; flags.push('🚪 WALKOUT');
    }
    if (/ravin|creek|park|river|pond|lake|coulee|escarpment|bluff|ridge|green.?space|pathway/i.test(desc)) {
      score += 15; flags.push('🌲 NATURE');
    }
    if (/bungalow|one.?stor|single.?stor/i.test(desc) || storeys === '1') {
      score += 5; flags.push('🏡 BUNGALOW');
    }
    if (/suite|in.?law|legal.?suite|secondary/i.test(desc)) {
      score += 10; flags.push('🏠 SUITE');
    }
    const lotNum = parseFloat(lot);
    if (lotNum > 6000 || /([7-9]\d{3}|[1-9]\d{4,})\s*sq/i.test(lot)) {
      score += 10; flags.push(`📐 LOT:${lot}`);
    }
    if (price > 0 && price < 800000) {
      score += 5; flags.push('💰 <800K');
    }
    // Pie lot, corner lot, backing
    if (/pie.?lot|corner.?lot|backing/i.test(desc)) {
      score += 5; flags.push('📐 SPECIAL LOT');
    }
  }

  // === RENTAL PROFILE ===
  if (profileKey === 'rental') {
    if (/legal.?suite|basement.?suite|secondary.?suite|in.?law|rental.?income|revenue|tenant|rented|currently.?rented/i.test(desc)) {
      score += 25; flags.push('💰 RENTAL INCOME');
    }
    if (/duplex|triplex|fourplex|multi.?family|side.?by.?side|up.?and.?down/i.test(desc)) {
      score += 20; flags.push('🏘️ MULTI-UNIT');
    }
    if (price > 0 && beds > 0) {
      const ppb = price / beds;
      if (ppb < 120000) {
        score += 15; flags.push(`💎 $${Math.round(ppb/1000)}k/bed`);
      } else if (ppb < 150000) {
        score += 8; flags.push(`💎 $${Math.round(ppb/1000)}k/bed`);
      }
    }
    if (/c.?train|lrt|transit|university|sait|mru|u.?of.?c|downtown/i.test(desc)) {
      score += 10; flags.push('🚇 TRANSIT');
    }
    if (/condo|apartment/i.test(l.Building?.Type || '') && price < 300000) {
      score += 5; flags.push('🏢 CONDO<300K');
    }
  }

  return { score, flags };
}

function formatResults(listings, profileKey, profileName, previousMLS) {
  const scored = listings.map(l => {
    const { score, flags } = scoreListing(l, profileKey);
    const isNew = !previousMLS.has(l.MlsNumber);
    return { listing: l, score, flags, isNew };
  }).sort((a, b) => b.score - a.score);

  const flagged = scored.filter(s => s.score > 0);
  const newOnes = scored.filter(s => s.isNew);

  let md = `## ${profileName}\n`;
  md += `**Total:** ${listings.length} | **Flagged:** ${flagged.length} | **New since last scan:** ${newOnes.length}\n\n`;

  const toShow = flagged.slice(0, 25);
  if (toShow.length === 0) {
    md += `No high-signal listings. Showing latest 5:\n\n`;
    scored.slice(0, 5).forEach(s => {
      const l = s.listing;
      const p = l.Property || {};
      md += `- **${p.Price}** | ${l.Building?.Bedrooms || '?'}bd/${l.Building?.BathroomTotal || '?'}ba | ${p.Address?.AddressText || '?'} | MLS# ${l.MlsNumber}\n`;
    });
    md += '\n';
    return { md, scored };
  }

  toShow.forEach((s, i) => {
    const l = s.listing;
    const p = l.Property || {};
    const b = l.Building || {};
    const newTag = s.isNew ? ' 🆕' : '';

    md += `### ${i + 1}. ${p.Address?.AddressText || 'Unknown'}${newTag}\n`;
    md += `**${p.Price}** | ${b.Bedrooms || '?'}bd/${b.BathroomTotal || '?'}ba | ${b.SizeInterior || 'N/A'} | ${b.Type || p.Type || 'N/A'}\n`;
    md += `Score: **${s.score}** | ${s.flags.join(' ')}\n`;
    md += `${l.TimeOnRealtor || 'New'} | Lot: ${l.Land?.SizeTotal || 'N/A'} | [View](https://www.realtor.ca${l.RelativeURLEn || ''})\n`;
    if (l.PublicRemarks && s.score >= 20) {
      md += `> ${l.PublicRemarks.substring(0, 250)}...\n`;
    }
    md += '\n';
  });

  return { md, scored };
}

function generateAlerts(allScored, previousMLS) {
  // Find new listings with score >= 20
  const alerts = [];
  for (const [key, scored] of Object.entries(allScored)) {
    for (const s of scored) {
      if (s.score >= 50 && s.isNew) {
        const l = s.listing;
        const p = l.Property || {};
        const b = l.Building || {};
        alerts.push({
          profile: key,
          score: s.score,
          flags: s.flags.join(' '),
          price: p.Price,
          address: p.Address?.AddressText || 'Unknown',
          beds: b.Bedrooms || '?',
          baths: b.BathroomTotal || '?',
          sqft: b.SizeInterior || 'N/A',
          url: `https://www.realtor.ca${l.RelativeURLEn || ''}`,
          mls: l.MlsNumber,
        });
      }
    }
  }
  return alerts;
}

async function main() {
  console.log('Connecting to Chrome via CDP...');
  const browser = await chromium.connectOverCDP(CDP_URL);
  const contexts = browser.contexts();
  const context = contexts[0] || await browser.newContext();

  // Load previous MLS numbers
  const latestFile = join(DATA_DIR, 'latest.json');
  let previousMLS = new Set();
  if (existsSync(latestFile)) {
    try {
      const prev = JSON.parse(readFileSync(latestFile, 'utf8'));
      for (const listings of Object.values(prev)) {
        if (Array.isArray(listings)) listings.forEach(l => previousMLS.add(l.MlsNumber));
      }
    } catch {}
  }

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
  const allRaw = {};
  const allScored = {};
  let fullSummary = `# 🏠 Calgary RE Deal Scan\n**${new Date().toLocaleString('en-CA', { timeZone: 'America/Edmonton' })}**\n\n`;

  for (const search of SEARCHES) {
    const listings = await collectListings(context, search);
    allRaw[search.key] = listings;
    const { md, scored } = formatResults(listings, search.key, search.name, previousMLS);
    allScored[search.key] = scored;
    fullSummary += md;
    await new Promise(r => setTimeout(r, 3000));
  }

  // Save
  writeFileSync(join(DATA_DIR, `raw-${timestamp}.json`), JSON.stringify(allRaw, null, 2));
  writeFileSync(join(DATA_DIR, `summary-${timestamp}.md`), fullSummary);
  writeFileSync(latestFile, JSON.stringify(allRaw, null, 2));
  writeFileSync(join(DATA_DIR, 'latest-summary.md'), fullSummary);

  // Generate alerts for new high-score listings
  const alerts = generateAlerts(allScored, previousMLS);
  if (alerts.length > 0) {
    const alertFile = join(DATA_DIR, 'alerts.json');
    writeFileSync(alertFile, JSON.stringify(alerts, null, 2));
    console.log(`\n🚨 ${alerts.length} new high-score listings!`);
    alerts.forEach(a => console.log(`  [${a.profile}] ${a.score}pts | ${a.price} | ${a.address} | ${a.flags}`));
  }

  console.log(`\n💾 Saved scan ${timestamp}`);
  console.log(fullSummary);

  await browser.close();
}

main().catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});
