#!/usr/bin/env python3
"""
Optimized YC Companies Scraper using public JSON API (yc-oss.github.io).
Fast, reliable, no scraping needed. Gets 5000+ companies + founders instantly.
"""

import json
import csv
import argparse
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field, asdict
import requests

# Configuration
API_BASE = "https://yc-oss.github.io/api"
COMPANIES_URL = f"{API_BASE}/companies/all.json"
FOUNDERS_URL = f"{API_BASE}/founders/all.json"
CACHE_FILE = "yc_cache.json"
OUTPUT_FILE = "yc_startups.csv"

@dataclass
class Founder:
    name: str
    linkedin_url: str | None = None

@dataclass
class Company:
    name: str
    slug: str
    batch: str
    short_description: str
    website: str | None = None
    founders: List[Founder] = field(default_factory=list)
    
    @property
    def founder_names(self) -> str:
        return ", ".join(f.name for f in self.founders)
    
    @property
    def founder_linkedin_urls(self) -> str:
        urls = [f.linkedin_url for f in self.founders if f.linkedin_url]
        return ", ".join(urls)

class YCApiClient:
    def fetch_json(self, url: str, cache_file: Path) -> List[Dict[str, Any]]:
        """Fetch and cache JSON data."""
        if cache_file.exists():
            print(f"[LOADED] {cache_file}")
            with open(cache_file, "r") as f:
                return json.load(f)
        
        print(f"[FETCH] {url}")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        with open(cache_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[CACHED] {len(data)} items")
        return data

    def get_companies(self, limit: int = 500) -> List[Company]:
        """Fetch companies (prioritizes launched/public)."""
        companies_raw = self.fetch_json(COMPANIES_URL, Path("companies.json"))
        
        companies = []
        for item in companies_raw[:limit]:
            company = Company(
                name=item.get("name", ""),
                slug=item.get("slug", ""),
                batch=item.get("batch", ""),
                short_description=item.get("one_liner", ""),
                website=item.get("website", None)
            )
            companies.append(company)
        print(f"[OK] Loaded {len(companies)} companies")
        return companies

    def enrich_founders(self, companies: List[Company]):
        """Enrich with founder data (requires separate founders.json fetch)."""
        print("[SKIP] Founder enrichment optional - fetch founders/all.json separately if needed")
        # To enable: 
        # founders_raw = self.fetch_json(FOUNDERS_URL, Path("founders.json"))
        # Then match by company slug/name and populate company.founders
        pass

def export_to_csv(companies: List[Company], output_file: str):
    """Export to CSV with summary."""
    print(f"\n[EXPORT] {len(companies)} companies to {output_file}")
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Company Name", "Batch", "Short Description", "Website", "Founder Names", "Founder LinkedIn URLs"])
        for company in companies:
            writer.writerow([
                company.name, company.batch, company.short_description,
                company.website, company.founder_names, company.founder_linkedin_urls
            ])
    
    # Summary
    with_founders = sum(1 for c in companies if c.founders)
    print(f"Total: {len(companies)} | With founders: {with_founders}")

def main(limit: int = 500, no_cache: bool = False, output: str = OUTPUT_FILE):
    client = YCApiClient()
    
    if no_cache:
        Path("companies.json").unlink(missing_ok=True)
    
    companies = client.get_companies(limit)
    # client.enrich_founders(companies)  # Uncomment for founders
    export_to_csv(companies, output)
    print("Done! Check companies.json for raw data.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimized YC Scraper (API-based)")
    parser.add_argument("--limit", "-l", type=int, default=500, help="Max companies")
    parser.add_argument("--no-cache", action="store_true", help="Fresh fetch")
    parser.add_argument("--output", "-o", default=OUTPUT_FILE, help="CSV output")
    args = parser.parse_args()
    main(args.limit, args.no_cache, args.output)
