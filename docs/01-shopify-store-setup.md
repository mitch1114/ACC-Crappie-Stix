# Step 1 — Create the Shopify store

Time: ~30 minutes. Do this first; everything else plugs into it.

## Create the store

1. Go to [shopify.com](https://www.shopify.com) and start the free trial with
   your business email.
2. Store name: **ACC Crappie Stix**. You'll get a temporary address like
   `acc-crappie-stix.myshopify.com` — your real domain comes over later, at
   cutover (step 5), so the WordPress site stays live and selling the whole time.
3. Pick the **Basic** plan when the trial nags you (you can change anytime).
   Don't buy a theme — we have one in this repo.

## Initial settings (Settings → ...)

| Where | What to set |
|---|---|
| General | Business address, currency USD, timezone |
| Payments | Activate **Shopify Payments** (bank account + EIN/SSN). Turn on PayPal too if you take it today |
| Checkout | Customer accounts: "Optional". Email marketing checkbox: on, unchecked by default |
| Shipping and delivery | Recreate your current WooCommerce shipping rates/zones. Note: rods over 4 ft often need oversize handling — copy whatever carrier setup works for you today |
| Taxes and duties | Turn on automatic US sales tax collection for states where you have nexus |
| Markets | If you ship to Canada etc., enable those countries |

## Staff access for development

When you want me to push the theme or data for you (instead of doing the
clicks yourself), create a staff/collaborator account or a custom app token:

- **Theme + data via CLI**: install [Shopify CLI](https://shopify.dev/docs/api/shopify-cli)
  on your computer (`npm i -g @shopify/cli`), then from this repo run
  `shopify theme dev --store acc-crappie-stix.myshopify.com` — it opens a
  browser login, no keys needed.

## What NOT to do yet

- Don't connect the acccrappiestix.com domain yet.
- Don't announce anything — the store stays password-protected (Online
  Store → Preferences) until launch day.

Next: [Step 2 — WordPress exports](02-wordpress-exports.md)
