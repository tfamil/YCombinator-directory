# YC Startup Directory Scraper

A Python scraper that extracts data for approximately 500 startups from Y Combinator's startup directory.

**Approach:**
I discovered that YC's directory uses **Algolia Search API** to serve company data, which allowed for efficient bulk retrieval instead of complex HTML pagination. The scraper works in two phases: (1) fetch company listings via Algolia API, then (2) scrape individual company pages asynchronously to extract founder names and LinkedIn URLs from `ycdc-card` HTML elements.

**Roadblocks Faced:**
1. **Dynamic Content** - The YC directory loads companies via JavaScript/Algolia. Solved by directly querying the Algolia API endpoint.
2. **Founder Name Extraction** - Initial parsing returned "Unknown Founder" because YC uses custom CSS classes (`text-xl font-bold`) instead of standard heading tags. Fixed by targeting the correct selectors.
3. **False Positives** - Company LinkedIn pages (`/company/`) and company names were being captured as founders. Added filtering to only keep personal LinkedIn profiles (`/in/`).

---

## Data Extracted

| Column | Description |
|--------|-------------|
| Company Name | Official company name |
| Batch | YC batch (e.g., "W25", "S24") |
| Short Description | One-liner description |
| Founder Names | Comma-separated list of founders |
| Founder LinkedIn URLs | Comma-separated LinkedIn profile URLs |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Scrape 500 companies (default)
python yc_scraper.py --limit 1000 --output startups.csv
python yc_scraper.py --no-cache  # Fresh data

```

## Final Results

- **500 companies** scraped successfully
- **899 founders** extracted with real names
- **465 companies** (93%) have LinkedIn URLs
- **~45 seconds** total scrape time

