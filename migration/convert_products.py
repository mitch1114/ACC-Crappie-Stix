#!/usr/bin/env python3
"""Convert WooCommerce product JSON (from export_from_woocommerce.py) into a
Shopify product import CSV.

Reads:  migration/data/products.json, migration/data/variations.json
Writes: migration/output/shopify_products.csv

Import in Shopify admin: Products -> Import. Shopify downloads images from the
URLs in the CSV, so keep the WordPress site online until the import finishes.

Usage:
    python convert_products.py [--weight-unit lbs|kg|g|oz]
"""

import argparse
import csv
import json
import re
import sys
from html import unescape
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
OUT_DIR = Path(__file__).parent / "output"

VENDOR = "ACC Crappie Stix"

WEIGHT_TO_GRAMS = {"lbs": 453.592, "kg": 1000.0, "g": 1.0, "oz": 28.3495}

COLUMNS = [
    "Handle", "Title", "Body (HTML)", "Vendor", "Type", "Tags", "Published",
    "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value",
    "Option3 Name", "Option3 Value",
    "Variant SKU", "Variant Grams", "Variant Inventory Tracker",
    "Variant Inventory Qty", "Variant Inventory Policy",
    "Variant Fulfillment Service", "Variant Price", "Variant Compare At Price",
    "Variant Requires Shipping", "Variant Taxable", "Variant Barcode",
    "Image Src", "Image Position", "Image Alt Text", "Gift Card",
    "SEO Title", "SEO Description", "Variant Image", "Variant Weight Unit",
    "Status",
]


def handle_from(product):
    """Use the WooCommerce slug as the Shopify handle so URLs carry over."""
    slug = product.get("slug") or ""
    if not slug:
        slug = re.sub(r"[^a-z0-9]+", "-", product.get("name", "").lower()).strip("-")
    return slug


def grams(weight_str, unit):
    if not weight_str:
        return ""
    try:
        return str(int(round(float(weight_str) * WEIGHT_TO_GRAMS[unit])))
    except (ValueError, KeyError):
        return ""


def price_fields(record):
    """Return (price, compare_at_price) honoring active sales."""
    regular = record.get("regular_price") or ""
    sale = record.get("sale_price") or ""
    current = record.get("price") or regular
    if sale and current == sale and regular and regular != sale:
        return sale, regular
    return current, ""


def inventory_fields(record):
    if record.get("manage_stock"):
        qty = record.get("stock_quantity")
        qty = 0 if qty is None else int(qty)
        policy = "continue" if record.get("backorders") in ("yes", "notify") else "deny"
        return "shopify", str(max(qty, 0)), policy
    # Not tracking stock: leave untracked so it always shows available
    if record.get("stock_status") == "outofstock":
        return "shopify", "0", "deny"
    return "", "", "deny"


def tags_for(product):
    tags = [c["name"] for c in product.get("categories", [])]
    tags += [t["name"] for t in product.get("tags", [])]
    return ", ".join(dict.fromkeys(tags))  # dedupe, keep order


def clean_html(text):
    return unescape(text or "").strip()


def strip_tags(text):
    return re.sub(r"<[^>]+>", " ", text or "").strip()


def variant_options(parent_attrs, attrs):
    """Map a variation's attributes onto the parent's option order."""
    values = {a["name"].lower(): a.get("option", "") for a in attrs}
    return [values.get(name.lower(), "") for name in parent_attrs]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weight-unit", default="lbs", choices=WEIGHT_TO_GRAMS,
                        help="Weight unit configured in WooCommerce (default: lbs)")
    args = parser.parse_args()

    products = json.loads((DATA_DIR / "products.json").read_text())
    variations_file = DATA_DIR / "variations.json"
    variations = json.loads(variations_file.read_text()) if variations_file.exists() else {}

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "shopify_products.csv"
    rows_written = 0
    skipped = []

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()

        for product in products:
            ptype = product.get("type")
            if ptype not in ("simple", "variable"):
                skipped.append((product.get("name"), f"unsupported type '{ptype}'"))
                continue

            handle = handle_from(product)
            status = "active" if product.get("status") == "publish" else "draft"
            published = "TRUE" if status == "active" else "FALSE"
            images = product.get("images", [])
            seo_title = product.get("name", "")
            body = clean_html(product.get("description", ""))
            type_name = product["categories"][0]["name"] if product.get("categories") else ""

            base = {
                "Handle": handle,
                "Title": product.get("name", ""),
                "Body (HTML)": body,
                "Vendor": VENDOR,
                "Type": type_name,
                "Tags": tags_for(product),
                "Published": published,
                "Gift Card": "FALSE",
                "SEO Title": seo_title,
                "SEO Description": strip_tags(unescape(product.get("short_description", "")))[:320],
                "Variant Weight Unit": args.weight_unit if args.weight_unit != "lbs" else "lb",
                "Status": status,
            }

            if ptype == "simple":
                price, compare = price_fields(product)
                tracker, qty, policy = inventory_fields(product)
                row = dict(base)
                row.update({
                    "Option1 Name": "Title", "Option1 Value": "Default Title",
                    "Variant SKU": product.get("sku", ""),
                    "Variant Grams": grams(product.get("weight"), args.weight_unit),
                    "Variant Inventory Tracker": tracker,
                    "Variant Inventory Qty": qty,
                    "Variant Inventory Policy": policy,
                    "Variant Fulfillment Service": "manual",
                    "Variant Price": price,
                    "Variant Compare At Price": compare,
                    "Variant Requires Shipping": "FALSE" if product.get("virtual") else "TRUE",
                    "Variant Taxable": "TRUE" if product.get("tax_status", "taxable") == "taxable" else "FALSE",
                })
                if images:
                    row["Image Src"] = images[0]["src"]
                    row["Image Position"] = "1"
                    row["Image Alt Text"] = images[0].get("alt", "")
                writer.writerow(row)
                rows_written += 1
            else:
                parent_attrs = [a["name"] for a in product.get("attributes", []) if a.get("variation")]
                if len(parent_attrs) > 3:
                    skipped.append((product.get("name"), f"{len(parent_attrs)} options (Shopify max is 3)"))
                    continue
                product_variations = variations.get(str(product["id"]), [])
                if not product_variations:
                    skipped.append((product.get("name"), "variable product with no variations exported"))
                    continue

                for i, variation in enumerate(product_variations):
                    price, compare = price_fields(variation)
                    tracker, qty, policy = inventory_fields(variation)
                    opts = variant_options(parent_attrs, variation.get("attributes", []))
                    row = dict(base) if i == 0 else {"Handle": handle}
                    for n, value in enumerate(opts[:3]):
                        if i == 0:
                            row[f"Option{n + 1} Name"] = parent_attrs[n]
                        row[f"Option{n + 1} Value"] = value
                    var_image = variation.get("image") or {}
                    row.update({
                        "Variant SKU": variation.get("sku", ""),
                        "Variant Grams": grams(variation.get("weight"), args.weight_unit),
                        "Variant Inventory Tracker": tracker,
                        "Variant Inventory Qty": qty,
                        "Variant Inventory Policy": policy,
                        "Variant Fulfillment Service": "manual",
                        "Variant Price": price,
                        "Variant Compare At Price": compare,
                        "Variant Requires Shipping": "TRUE",
                        "Variant Taxable": "TRUE" if variation.get("tax_status", "taxable") in ("taxable", "parent") else "FALSE",
                        "Variant Image": var_image.get("src", ""),
                    })
                    if i == 0 and images:
                        row["Image Src"] = images[0]["src"]
                        row["Image Position"] = "1"
                        row["Image Alt Text"] = images[0].get("alt", "")
                    writer.writerow(row)
                    rows_written += 1

            # Additional product images get their own image-only rows
            for pos, image in enumerate(images[1:], start=2):
                writer.writerow({
                    "Handle": handle,
                    "Image Src": image["src"],
                    "Image Position": str(pos),
                    "Image Alt Text": image.get("alt", ""),
                })
                rows_written += 1

    print(f"Wrote {rows_written} rows -> {out_path}")
    if skipped:
        print("\nSkipped (handle these manually):")
        for name, reason in skipped:
            print(f"  - {name}: {reason}")


if __name__ == "__main__":
    main()
