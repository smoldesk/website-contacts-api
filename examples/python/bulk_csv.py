"""Enrich a CSV of websites with emails, phones and socials.

Usage:
    pip install requests
    export RAPIDAPI_KEY=your_key
    python bulk_csv.py leads.csv enriched.csv --column website --country US --workers 2

The input needs a column with a domain or URL (default name: "website").
Every input row is kept; contact columns are added to the right.
Lookups that find nothing don't use your Lookups quota, but they do count as requests.
"""
import argparse
import csv
import os
import time
from concurrent.futures import ThreadPoolExecutor

import requests

HOST = "website-contacts-company-info.p.rapidapi.com"
SOCIALS = ["facebook", "instagram", "linkedin", "twitter", "tiktok", "youtube", "whatsapp"]
OUT_COLS = ["status", "emails", "generic_emails", "phones", "contact_form", "company_name"] + SOCIALS


def lookup(session: requests.Session, domain: str, country: str | None) -> dict:
    params = {"domain": domain}
    if country:
        params["country"] = country
    for attempt in range(5):
        try:
            r = session.get(f"https://{HOST}/v1/contacts", params=params, timeout=60)
        except requests.RequestException as e:
            if attempt == 4:
                return {"status": f"error: {type(e).__name__}"}
            time.sleep(2 ** attempt)
            continue
        if r.status_code == 429:  # plan rate limit: wait and retry
            time.sleep(2 ** attempt)
            continue
        if r.status_code == 400:
            return {"status": "invalid_input"}
        if r.status_code != 200:
            return {"status": f"error: HTTP {r.status_code}"}
        return r.json()
    return {"status": "error: rate limited"}


def to_row(data: dict) -> dict:
    emails = data.get("emails") or []
    socials = data.get("socials") or {}
    row = {
        "status": data.get("status", ""),
        "emails": "; ".join(e["email"] for e in emails),
        "generic_emails": "; ".join(e["email"] for e in emails if e["type"] == "generic"),
        "phones": "; ".join(p["international"] for p in data.get("phones") or []),
        "contact_form": data.get("contactFormUrl") or "",
        "company_name": (data.get("company") or {}).get("name") or "",
    }
    for s in SOCIALS:
        row[s] = (socials.get(s) or [""])[0]
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--column", default="website")
    ap.add_argument("--country", default=None, help="2-letter code, e.g. US. Recommended for .com sites.")
    ap.add_argument("--workers", type=int, default=2, help="parallel requests; keep within your plan's rate limit")
    args = ap.parse_args()

    with open(args.input, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = reader.fieldnames or []
    if args.column not in fields:
        raise SystemExit(f'column "{args.column}" not found; columns are: {", ".join(fields)}')

    session = requests.Session()
    session.headers.update({"x-rapidapi-host": HOST, "x-rapidapi-key": os.environ["RAPIDAPI_KEY"]})

    def work(row: dict) -> dict:
        site = (row.get(args.column) or "").strip()
        return to_row(lookup(session, site, args.country)) if site else {"status": "empty"}

    with ThreadPoolExecutor(args.workers) as ex:
        results = list(ex.map(work, rows))

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields + [c for c in OUT_COLS if c not in fields])
        w.writeheader()
        for row, res in zip(rows, results):
            w.writerow({**row, **res})

    found = sum(r.get("status") == "contacts_found" for r in results)
    print(f"done: {found}/{len(rows)} websites with contacts -> {args.output}")


if __name__ == "__main__":
    main()
