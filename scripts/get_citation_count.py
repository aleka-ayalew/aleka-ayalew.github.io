#!/usr/bin/env python3
"""
Fetch Google Scholar profile page (public) and extract total citations and publications count.
Writes data/citations.json with {"citations": int, "publications": int, "fetched_at": "ISO8601", "source": url}.
Usage: set env var SCHOLAR_URL or pass profile URL as first arg.
"""
import os
import sys
import json
import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

default_url = "https://scholar.google.com/citations?hl=en&user=Yda5OkEAAAAJ"
url = os.environ.get("SCHOLAR_URL") or (sys.argv[1] if len(sys.argv) > 1 else default_url)
if not url:
    raise SystemExit("Set SCHOLAR_URL env or pass profile URL as first arg")

headers = {"User-Agent": "Mozilla/5.0 (compatible; CitationBot/1.0)"}
headers["Accept-Language"] = "en-US,en;q=0.9"

out_path = os.path.join("data", "citations.json")
existing_payload = None
if os.path.exists(out_path):
    try:
        with open(out_path, "r", encoding="utf-8") as f:
            existing_payload = json.load(f)
    except Exception:
        existing_payload = None

# Fetch the profile page for metrics (citations table)
resp = None
last_error = None
for _ in range(3):
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        break
    except requests.RequestException as e:
        last_error = e

if resp is None:
    if existing_payload and isinstance(existing_payload.get("citations"), int):
        print(f"Warning: could not fetch Google Scholar ({last_error}); keeping existing data in {out_path}")
        sys.exit(0)
    raise SystemExit(f"Could not fetch Google Scholar data and no existing citation cache is available: {last_error}")

soup = BeautifulSoup(resp.text, "html.parser")

# Parse citations from the summary table
table = soup.find("table", class_="gsc_rsb_st")
if not table:
    if existing_payload and isinstance(existing_payload.get("citations"), int):
        print(f"Warning: couldn't parse citations table from Google Scholar page; keeping existing data in {out_path}")
        sys.exit(0)
    raise SystemExit("Couldn't find citations table on the page. Is the profile public?")

rows = table.find_all("tr")
if not rows or len(rows) < 1:
    if existing_payload and isinstance(existing_payload.get("citations"), int):
        print(f"Warning: unexpected page format while reading citations; keeping existing data in {out_path}")
        sys.exit(0)
    raise SystemExit("Unexpected page format: no citation rows found")

try:
    citations_text = rows[0].find_all("td")[1].get_text(strip=True)
    citations = int(citations_text.replace(",", ""))
except Exception as e:
    if existing_payload and isinstance(existing_payload.get("citations"), int):
        print(f"Warning: couldn't parse citation count ({e}); keeping existing data in {out_path}")
        sys.exit(0)
    raise SystemExit(f"Couldn't parse citation count: {e}")

# Attempt to fetch publications list with a large pagesize to count all publications
# Many Google Scholar profile pages accept cstart and pagesize parameters for the works table
publications = None
try:
    parsed = list(urlparse(url))
    qs = parse_qs(parsed[4])
    # set pagesize large to try to get all works on one page
    qs['cstart'] = ['0']
    qs['pagesize'] = ['1000']
    parsed[4] = urlencode(qs, doseq=True)
    big_url = urlunparse(parsed)
    resp2 = requests.get(big_url, headers=headers, timeout=15)
    resp2.raise_for_status()
    soup2 = BeautifulSoup(resp2.text, "html.parser")
    rows2 = soup2.find_all("tr", class_="gsc_a_tr")
    if rows2:
        publications = len(rows2)
except Exception:
    publications = None

# Fallback: try to find a text like "of N" (e.g., "1–20 of 52") on the page
if publications is None:
    try:
        import re
        m = re.search(r"of\s+([\d,]+)", resp.text)
        if m:
            publications = int(m.group(1).replace(",", ""))
    except Exception:
        publications = None

if publications is None:
    # As a last resort, set to 0 to avoid breaking consumers; caller may interpret null differently.
    publications = 0

payload = {
    "citations": citations,
    "publications": publications,
    "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
    "source": url
}

os.makedirs("data", exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)
print("Wrote", out_path, payload)
