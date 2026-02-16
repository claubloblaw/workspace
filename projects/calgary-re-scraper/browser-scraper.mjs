#!/usr/bin/env node
/**
 * Calgary RE Scraper — Uses Playwright connecting to existing OpenClaw Chrome via CDP
 * Navigates realtor.ca, intercepts API responses, extracts listing data
 */

import { chromium } from 'playwright';
import { writeFileSync, readFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = join(__dirname, 'data');
if (!existsSync(DATA_DIR)) mkdirSync(DATA_DIR, { recursive: true });

const CDP_URL = 'http://127.0.0.1:18800';

// Search configs
const SEARCHES = [
  {
    key: 'walkout',
    name: 'Walkout Bungalows (SW+SE Calgary)',
    url: 'https://www.realtor.ca/map#ZoomLevel=11&Center=50.962500%2C-114.107500&LatitudeMax=51.04500&LongitudeMax=-113.90000&LatitudeMin=50.88000&LongitudeMin=-114.31500&Sort=6-D&GeoName=Calgary%2C%20AB&PropertyTypeGroupID=1&TransactionTypeId=2&PriceMin=500000&PriceMax=1200000&BuildingTypeId=1&BedRange=3-0&BathRange=2-0&Currency=CAD',
  },
  {
    key: 'rental',
    name: 'Rental Yield (SW+SE Calgary)',
    url: 'https://www.realtor.ca/map#ZoomLevel=11&Center=50.962500%2C-114.107500&LatitudeMax=51.04500&LongitudeMax=-113.90000&LatitudeMin=50.88000&LongitudeMin=-114.31500&Sort=6-D&GeoName=Calgary%2C%20AB&PropertyTypeGroupID=1&TransactionTypeId=2&PriceMin=150000&PriceMax=600000&Currency=CAD',
  },
];

async function interceptAndCollect(page, searchConfig) {
  console.log(`\n🔍 ${searchConfig.name}`);
  
  const apiResponses = [];
  
  // Intercept API responses
  page.on('response', async (response) => {
    const url = response.url();
    if (url.includes('PropertySearch_Post') || url.includes('PropertySearch')) {
      try {
        const json = await response.json();
        if (json.Results) {
          apiResponses.push(...json.Results);
          console.log(`  Captured ${json.Results.length} listings (total: ${apiResponses.length})`);
        }
      } catch {}
    }
  });

  // Navigate to search
  await page.goto(searchConfig.url, { waitUntil: 'networkidle', timeout: 30000 });
  
  // Wait for listings to load
  await page.waitForTimeout(5000);

  // If no API data captured, try to scrape from DOM
  if (apiResponses.length === 0) {
    console.log('  No API intercept — trying DOM scrape...');
    
    // Click "List" view
    try {
      await page.click('a[href="#"]:has-text("List")', { timeout: 5000 });
      await page.waitForTimeout(3000);
    } catch {}

    // Try to extract from the page
    const listings = await page.evaluate(() => {
      const cards = document.querySelectorAll('.listingCard, .cardCon, [class*="listing"], [class*="property"]');
      return Array.from(cards).map(card => ({
        text: card.innerText,
        html: card.innerHTML.substring(0, 500),
      }));
    });
    
    if (listings.length > 0) {
      console.log(`  Found ${listings.length} DOM listings`);
      return { source: 'dom', listings };
    }
    
    // Last resort: get full page text
    const pageText = await page.evaluate(() => document.body.innerText);
    console.log(`  Page text length: ${pageText.length}`);
    console.log(`  First 500 chars: ${pageText.substring(0, 500)}`);
    return { source: 'text', text: pageText };
  }

  return { source: 'api', listings: apiResponses };
}

async function main() {
  console.log('Connecting to Chrome via CDP...');
  const browser = await chromium.connectOverCDP(CDP_URL);
  const contexts = browser.contexts();
  const context = contexts[0] || await browser.newContext();
  
  const results = {};
  
  for (const search of SEARCHES) {
    const page = await context.newPage();
    try {
      results[search.key] = await interceptAndCollect(page, search);
    } catch (err) {
      console.error(`  Error on ${search.key}:`, err.message);
      results[search.key] = { source: 'error', error: err.message };
    }
    await page.close();
    await new Promise(r => setTimeout(r, 3000));
  }

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
  const outFile = join(DATA_DIR, `scan-${timestamp}.json`);
  writeFileSync(outFile, JSON.stringify(results, null, 2));
  console.log(`\n💾 Saved to ${outFile}`);
  
  // Print summary
  for (const [key, data] of Object.entries(results)) {
    console.log(`\n--- ${key} ---`);
    if (data.source === 'api') {
      console.log(`${data.listings.length} listings from API`);
      data.listings.slice(0, 3).forEach(l => {
        const p = l.Property || {};
        console.log(`  ${p.Price} | ${p.Address?.AddressText} | MLS# ${l.MlsNumber}`);
      });
    } else if (data.source === 'dom') {
      console.log(`${data.listings.length} listings from DOM`);
      data.listings.slice(0, 3).forEach(l => console.log(`  ${l.text.substring(0, 100)}`));
    } else {
      console.log(`Source: ${data.source}`);
    }
  }

  await browser.close();
}

main().catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});
