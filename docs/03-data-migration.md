# Step 3 — Convert and import the data

Prerequisite: `migration/data/` is populated ([Step 2](02-wordpress-exports.md))
and the Shopify store exists ([Step 1](01-shopify-store-setup.md)).

## A. Run the converters

```bash
cd migration
python convert_products.py        # → output/shopify_products.csv
python convert_customers.py      # → output/shopify_customers.csv
python convert_orders.py         # → output/matrixify_orders.csv
python convert_blog.py           # → output/matrixify_blog_posts.csv + matrixify_pages.csv
python generate_redirects.py     # → output/shopify_redirects.csv
```

Each script prints what it wrote and lists anything it skipped. If
WooCommerce weights are in something other than pounds, pass
`--weight-unit kg` (or `g`/`oz`) to `convert_products.py`.

## B. Import — in this order

1. **Products** — Shopify admin → Products → Import →
   `shopify_products.csv`. Check "Publish new products". Shopify fetches all
   images from the old site during this step, so WordPress must stay online.
   Spot-check a few rods afterwards: variants (lengths/grips), prices,
   images, inventory.

2. **Collections** — create one collection per old product category
   (Jiggin' Stix, Spinnin' Stix, Scopin' Stix, Green Series, Apparel, ...).
   Use automated collections matching the category tag the import added, and
   set each collection's **handle** to match the old WooCommerce category
   slug (e.g. `jiggin-stix`) so the redirect file lines up.

3. **Customers** — Customers → Import → `shopify_customers.csv`.
   Don't check "send invite emails" — invite people later via Klaviyo at
   launch instead. Passwords can't migrate; customers just reset on first
   login.

4. **Orders** — install [Matrixify](https://apps.shopify.com/excel-export-import),
   then Import → upload `matrixify_orders.csv`. Imported orders are tagged
   `woocommerce-import`, numbered `#W…`, and send no emails. Do a dry run
   with the file's first ~20 rows first.

5. **Blog & pages** — Matrixify again: `matrixify_blog_posts.csv` and
   `matrixify_pages.csv`. Then review pages like Warranty/About — images in
   the body still point at WordPress URLs (see below).

6. **Redirects** — Shopify admin → Online Store (or Content) →
   URL Redirects → Import → `shopify_redirects.csv`.

## C. Known gaps to handle by hand

- **Images inside blog/page content** still load from
  `acccrappiestix.com/wp-content/...`. Once DNS moves to Shopify those break.
  Options: re-upload images on the important pages (Shopify admin →
  Content → Files), or keep the old site reachable at a subdomain like
  `old.acccrappiestix.com` and bulk-replace URLs. I can script the
  bulk-replace when we get there.
- **Product reviews**: if you use a WooCommerce review plugin and want the
  reviews, install a Shopify review app (Judge.me works well) — most have a
  WooCommerce CSV importer.
- **Coupons** don't migrate; recreate active discount codes in Shopify
  (Discounts → Create).
- Any product the converter reported as "skipped" (grouped/external types).
