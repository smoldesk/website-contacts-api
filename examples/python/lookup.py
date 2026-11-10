"""One lookup. Usage: RAPIDAPI_KEY=your_key python lookup.py cafemaltaaustin.com [US]"""
import os
import sys

import requests

HOST = "website-contacts-company-info.p.rapidapi.com"


def lookup(domain: str, country: str | None = None, emails: str = "all") -> dict:
    params = {"domain": domain, "emails": emails}
    if country:
        params["country"] = country
    r = requests.get(
        f"https://{HOST}/v1/contacts",
        params=params,
        headers={"x-rapidapi-host": HOST, "x-rapidapi-key": os.environ["RAPIDAPI_KEY"]},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python lookup.py <domain> [country]")
    data = lookup(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print("status: ", data["status"], f"({data['source']})")
    print("company:", data["company"]["name"])
    for e in data["emails"]:
        print("email:  ", e["email"], f"[{e['type']}]")
    for p in data["phones"]:
        print("phone:  ", p["international"])
    for network, urls in data["socials"].items():
        print(f"{network}:".ljust(9), ", ".join(urls))
    if data["contactFormUrl"]:
        print("form:   ", data["contactFormUrl"])
