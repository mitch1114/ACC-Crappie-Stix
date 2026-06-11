# ACC Crappie Stix — WooCommerce → Shopify migration

Everything needed to move [acccrappiestix.com](https://acccrappiestix.com)
from WordPress/WooCommerce to a modern Shopify store: the theme, the data
migration tooling, and the runbook.

## Repo map

```
theme/       Shopify Horizon v3.5.1 theme + ACC brand color scheme
migration/   Scripts: WooCommerce export → Shopify-ready import files
docs/        The step-by-step runbook (start at 01)
```

## The plan

| Step | What | Who | Doc |
|---|---|---|---|
| 1 | Create the Shopify store, payments, shipping, taxes | You (~30 min) | [docs/01](docs/01-shopify-store-setup.md) |
| 2 | Export data from WordPress (API keys + one script) | You (~20 min) | [docs/02](docs/02-wordpress-exports.md) |
| 3 | Convert + import products, customers, orders, blog, redirects | Scripts / Claude | [docs/03](docs/03-data-migration.md) |
| 4 | Push & customize the theme | Shopify CLI / theme editor | [docs/04](docs/04-theme-setup.md) |
| 5 | Launch: Klaviyo, QuickBooks, DNS, post-launch checks | You + checklist | [docs/05](docs/05-cutover-checklist.md) |

The WordPress site keeps running and selling until step 5 — there's no
downtime in this plan.

## Design decisions

- **Horizon theme, lightly customized** rather than built from scratch:
  you can edit everything yourself in the Shopify theme editor, every app
  works with it, and Shopify keeps improving it upstream.
- **Product handles = old WooCommerce slugs**, so every product URL gets a
  clean 301 redirect and SEO carries over.
- **Orders import via Matrixify** (Shopify has no native order import);
  old orders keep their numbers with a `W` prefix (`#W12345`).
- **Customer data never touches this repo** — exports and generated CSVs
  are gitignored.
