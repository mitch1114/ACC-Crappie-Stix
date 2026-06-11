# WooCommerce → Shopify migration toolkit

Scripts that move the ACC Crappie Stix catalog, customers, orders, blog, and
SEO redirects from WooCommerce to Shopify. Run them on your own computer with
Python 3.9+ (`python3 --version` to check).

## Pipeline

```
1. export_from_woocommerce.py   pulls products/customers/orders from the live
                                site via the WooCommerce REST API → data/*.json
   (WordPress Tools → Export)   gives you the blog/pages XML    → data/*.xml

2. convert_products.py          → output/shopify_products.csv    (Shopify native import)
   convert_customers.py         → output/shopify_customers.csv   (Shopify native import)
   convert_orders.py            → output/matrixify_orders.csv    (import via Matrixify app)
   convert_blog.py              → output/matrixify_blog_posts.csv + matrixify_pages.csv
   generate_redirects.py        → output/shopify_redirects.csv   (Shopify native import)
```

Step-by-step instructions live in [`docs/02-wordpress-exports.md`](../docs/02-wordpress-exports.md)
and [`docs/03-data-migration.md`](../docs/03-data-migration.md).

## Important

- `data/` and `output/` contain customer names, addresses, and order history.
  They are gitignored — **never commit them**.
- Product handles reuse the WooCommerce slugs, so old product URLs map 1:1 to
  new ones and the redirect file works without manual mapping.
- Shopify downloads product images from the URLs in the CSV. Keep the
  WordPress site online until the product import finishes.
- Orders require the [Matrixify](https://matrixify.app) Shopify app (free
  plan covers small imports; paid month covers everything, then cancel).
