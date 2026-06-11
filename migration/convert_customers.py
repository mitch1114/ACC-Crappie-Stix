#!/usr/bin/env python3
"""Convert WooCommerce customers (and guest buyers found in orders) into a
Shopify customer import CSV.

Reads:  migration/data/customers.json, migration/data/orders.json (optional)
Writes: migration/output/shopify_customers.csv

Import in Shopify admin: Customers -> Import. Passwords cannot be migrated;
customers set a new one the first time they log in.

Note on marketing consent: WooCommerce does not record email-marketing opt-in,
so "Accepts Email Marketing" is left FALSE for everyone. Your real consent
list lives in Klaviyo - connect the Klaviyo Shopify integration and your
subscriber statuses sync from there.
"""

import csv
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
OUT_DIR = Path(__file__).parent / "output"

COLUMNS = [
    "First Name", "Last Name", "Email", "Accepts Email Marketing",
    "Default Address Company", "Default Address Address1",
    "Default Address Address2", "Default Address City",
    "Default Address Province Code", "Default Address Country Code",
    "Default Address Zip", "Phone", "Accepts SMS Marketing", "Tags", "Note",
    "Tax Exempt",
]


def row_from(first, last, email, billing, tags):
    return {
        "First Name": first or billing.get("first_name", ""),
        "Last Name": last or billing.get("last_name", ""),
        "Email": email,
        "Accepts Email Marketing": "FALSE",
        "Default Address Company": billing.get("company", ""),
        "Default Address Address1": billing.get("address_1", ""),
        "Default Address Address2": billing.get("address_2", ""),
        "Default Address City": billing.get("city", ""),
        "Default Address Province Code": billing.get("state", ""),
        "Default Address Country Code": billing.get("country", ""),
        "Default Address Zip": billing.get("postcode", ""),
        "Phone": billing.get("phone", ""),
        "Accepts SMS Marketing": "FALSE",
        "Tags": tags,
        "Note": "Imported from WooCommerce",
        "Tax Exempt": "FALSE",
    }


def main():
    customers = json.loads((DATA_DIR / "customers.json").read_text())
    orders_file = DATA_DIR / "orders.json"
    orders = json.loads(orders_file.read_text()) if orders_file.exists() else []

    seen = {}
    for c in customers:
        email = (c.get("email") or "").strip().lower()
        if not email:
            continue
        seen[email] = row_from(
            c.get("first_name"), c.get("last_name"), email,
            c.get("billing", {}), "woocommerce-import",
        )

    guests = 0
    # Newest orders first so a guest's most recent address wins
    for order in sorted(orders, key=lambda o: o.get("date_created", ""), reverse=True):
        billing = order.get("billing", {})
        email = (billing.get("email") or "").strip().lower()
        if not email or email in seen:
            continue
        seen[email] = row_from(
            billing.get("first_name"), billing.get("last_name"), email,
            billing, "woocommerce-import, guest-checkout",
        )
        guests += 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "shopify_customers.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(seen.values())

    print(f"Wrote {len(seen)} customers ({guests} from guest checkouts) -> {out_path}")


if __name__ == "__main__":
    main()
