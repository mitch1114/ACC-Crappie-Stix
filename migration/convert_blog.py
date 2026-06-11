#!/usr/bin/env python3
"""Convert a WordPress export (WXR XML) into Matrixify import CSVs for
Shopify blog posts and pages.

Get the export file from WordPress admin: Tools -> Export -> All content
(or run it twice: once for Posts, once for Pages). Save the .xml file(s)
into migration/data/.

Reads:  migration/data/*.xml
Writes: migration/output/matrixify_blog_posts.csv
        migration/output/matrixify_pages.csv

Heads-up: images inside post bodies still point at acccrappiestix.com
wp-content URLs. Keep WordPress online (or its media folder hosted
somewhere) until you re-upload or re-point those images.
"""

import csv
import glob
import xml.etree.ElementTree as ET
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
OUT_DIR = Path(__file__).parent / "output"

NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "wp": "http://wordpress.org/export/1.2/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
}

BLOG_COLUMNS = [
    "Handle", "Command", "Title", "Author", "Body HTML", "Summary HTML",
    "Tags", "Published", "Published At", "Blog: Handle", "Blog: Title",
]
PAGE_COLUMNS = ["Handle", "Command", "Title", "Body HTML", "Published", "Published At"]

# Shopify's default blog handle; posts will live at /blogs/news/<handle>
BLOG_HANDLE = "news"
BLOG_TITLE = "News"

SKIP_PAGE_SLUGS = {
    # WooCommerce/WordPress utility pages that Shopify replaces outright
    "cart", "checkout", "my-account", "shop", "wp-login", "sample-page",
    "refund_returns",
}


def text(item, tag):
    el = item.find(tag, NS)
    return (el.text or "") if el is not None else ""


def main():
    xml_files = sorted(glob.glob(str(DATA_DIR / "*.xml")))
    if not xml_files:
        raise SystemExit(f"No .xml export files found in {DATA_DIR}. "
                         "Run Tools -> Export in WordPress admin first.")

    posts, pages = [], []
    for path in xml_files:
        root = ET.parse(path).getroot()
        for item in root.iter("item"):
            post_type = text(item, "wp:post_type")
            status = text(item, "wp:status")
            if status not in ("publish", "draft"):
                continue
            slug = text(item, "wp:post_name")
            published = "TRUE" if status == "publish" else "FALSE"
            published_at = text(item, "wp:post_date_gmt")
            if published_at:
                published_at = published_at.replace(" ", "T") + "Z"
            body = text(item, "content:encoded")

            if post_type == "post":
                tags = [c.text for c in item.findall("category")
                        if c.text and c.get("domain") in ("post_tag", "category")]
                posts.append({
                    "Handle": slug,
                    "Command": "NEW",
                    "Title": text(item, "title"),
                    "Author": text(item, "dc:creator"),
                    "Body HTML": body,
                    "Summary HTML": text(item, "excerpt:encoded"),
                    "Tags": ", ".join(dict.fromkeys(tags)),
                    "Published": published,
                    "Published At": published_at,
                    "Blog: Handle": BLOG_HANDLE,
                    "Blog: Title": BLOG_TITLE,
                })
            elif post_type == "page" and slug not in SKIP_PAGE_SLUGS:
                pages.append({
                    "Handle": slug,
                    "Command": "NEW",
                    "Title": text(item, "title"),
                    "Body HTML": body,
                    "Published": published,
                    "Published At": published_at,
                })

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, columns, rows in (
        ("matrixify_blog_posts.csv", BLOG_COLUMNS, posts),
        ("matrixify_pages.csv", PAGE_COLUMNS, pages),
    ):
        out = OUT_DIR / name
        with out.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {len(rows)} rows -> {out}")


if __name__ == "__main__":
    main()
