#!/usr/bin/env python3
"""Export products, customers, and orders from a WooCommerce store.

Run this on your own computer (it needs to reach acccrappiestix.com).
It downloads everything into JSON files under migration/data/ which the
convert_*.py scripts then turn into Shopify import files.

Setup (one time):
    pip install requests

Create read-only API keys in WordPress admin:
    WooCommerce -> Settings -> Advanced -> REST API -> Add key
    Description: "Shopify migration", Permissions: Read

Usage:
    python export_from_woocommerce.py \
        --url https://acccrappiestix.com \
        --key ck_xxxxxxxxxxxxxxxx \
        --secret cs_xxxxxxxxxxxxxxxx
"""

import argparse
import json
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("The 'requests' package is required. Install it with: pip install requests")

DATA_DIR = Path(__file__).parent / "data"
PER_PAGE = 100


def fetch_all(session, base_url, endpoint, params=None):
    """Fetch every page of a WooCommerce REST collection."""
    items = []
    page = 1
    params = dict(params or {})
    while True:
        params.update({"per_page": PER_PAGE, "page": page})
        url = f"{base_url}/wp-json/wc/v3/{endpoint}"
        resp = session.get(url, params=params, timeout=60)
        if resp.status_code == 401:
            sys.exit("Authentication failed (401). Double-check your consumer key/secret.")
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        items.extend(batch)
        total_pages = int(resp.headers.get("X-WP-TotalPages", page))
        print(f"  {endpoint}: page {page}/{total_pages} ({len(items)} so far)")
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.3)  # be gentle with the live store
    return items


def save(name, data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / name
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"Saved {len(data)} records -> {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Store URL, e.g. https://acccrappiestix.com")
    parser.add_argument("--key", required=True, help="WooCommerce consumer key (ck_...)")
    parser.add_argument("--secret", required=True, help="WooCommerce consumer secret (cs_...)")
    parser.add_argument("--skip-orders", action="store_true", help="Skip order export")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    session = requests.Session()
    session.auth = (args.key, args.secret)
    session.headers["User-Agent"] = "acc-shopify-migration/1.0"

    print("Exporting product categories...")
    save("categories.json", fetch_all(session, base_url, "products/categories"))

    print("Exporting products...")
    products = fetch_all(session, base_url, "products", {"status": "any"})
    save("products.json", products)

    print("Exporting product variations...")
    variations = {}
    for product in products:
        if product.get("type") == "variable":
            variations[str(product["id"])] = fetch_all(
                session, base_url, f"products/{product['id']}/variations"
            )
    save_path = DATA_DIR / "variations.json"
    save_path.write_text(json.dumps(variations, indent=2, ensure_ascii=False))
    print(f"Saved variations for {len(variations)} variable products -> {save_path}")

    print("Exporting customers (registered accounts)...")
    save("customers.json", fetch_all(session, base_url, "customers"))

    if not args.skip_orders:
        print("Exporting orders (this can take a while)...")
        save("orders.json", fetch_all(session, base_url, "orders", {"status": "any"}))

    print("\nDone. Next: run the convert_*.py scripts. See migration/README.md.")


if __name__ == "__main__":
    main()
