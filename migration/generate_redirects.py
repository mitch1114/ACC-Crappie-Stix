#!/usr/bin/env python3
"""Generate a Shopify URL-redirect import CSV so old WooCommerce URLs keep
working (and keep their Google rankings) after the switch.

Reads:  migration/data/products.json, migration/data/categories.json,
        migration/data/*.xml (WordPress export, for posts/pages - optional)
Writes: migration/output/shopify_redirects.csv

Import in Shopify admin: Content -> Menus (or Online Store -> Navigation)
-> View URL Redirects -> Import.

Mappings:
  /product/<slug>/            -> /products/<slug>
  /product-category/<slug>/   -> /collections/<slug>   (create matching collections!)
  /shop/                      -> /collections/all
  /YYYY/MM/DD/<post-slug>/    -> /blogs/news/<post-slug>
  /<page-slug>/               -> /pages/<page-slug>
  /my-account/                -> /account/login
"""

import csv
import glob
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

DATA_DIR = Path(__file__).parent / "data"
OUT_DIR = Path(__file__).parent / "output"

NS = {"wp": "http://wordpress.org/export/1.2/"}

STATIC_REDIRECTS = [
    ("/shop", "/collections/all"),
    ("/shop/", "/collections/all"),
    ("/my-account", "/account/login"),
    ("/my-account/", "/account/login"),
    ("/product-tag", "/collections/all"),
]


def old_path(record):
    """Extract the path of the old URL from a Woo permalink."""
    permalink = record.get("permalink") or record.get("link") or ""
    return urlparse(permalink).path if permalink else ""


def main():
    redirects = list(STATIC_REDIRECTS)

    products = json.loads((DATA_DIR / "products.json").read_text())
    for p in products:
        path = old_path(p) or f"/product/{p.get('slug', '')}/"
        if p.get("slug"):
            redirects.append((path, f"/products/{p['slug']}"))

    categories_file = DATA_DIR / "categories.json"
    if categories_file.exists():
        for c in json.loads(categories_file.read_text()):
            if c.get("slug"):
                redirects.append((f"/product-category/{c['slug']}/",
                                  f"/collections/{c['slug']}"))

    for path in sorted(glob.glob(str(DATA_DIR / "*.xml"))):
        root = ET.parse(path).getroot()
        for item in root.iter("item"):
            post_type = item.findtext("wp:post_type", default="", namespaces=NS)
            status = item.findtext("wp:status", default="", namespaces=NS)
            slug = item.findtext("wp:post_name", default="", namespaces=NS)
            link = item.findtext("link", default="")
            if status != "publish" or not slug or not link:
                continue
            old = urlparse(link).path
            if post_type == "post":
                redirects.append((old, f"/blogs/news/{slug}"))
            elif post_type == "page":
                redirects.append((old, f"/pages/{slug}"))

    # Dedupe and drop self-redirects / root
    seen = set()
    rows = []
    for src, dst in redirects:
        src = src.rstrip("/") or "/"
        if src in ("/", "") or src in seen or src == dst.rstrip("/"):
            continue
        seen.add(src)
        rows.append((src, dst))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "shopify_redirects.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Redirect from", "Redirect to"])
        writer.writerows(rows)
    print(f"Wrote {len(rows)} redirects -> {out}")


if __name__ == "__main__":
    main()
