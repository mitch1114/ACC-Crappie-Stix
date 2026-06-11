# Step 5 — Launch / cutover checklist

Do this only when products, theme, shipping, taxes, and payments are all
verified on the Shopify store. Best window: a low-traffic weekday morning.

## Before flipping DNS

- [ ] Place a **real test order** on the Shopify store (Shopify Payments test
      mode, or a real $1 product you refund) — confirm the confirmation
      email, tax, and shipping rate are right.
- [ ] **Klaviyo**: install the Klaviyo app on Shopify and connect it to your
      existing Klaviyo account. Your lists, flows, and templates stay; just
      re-point the flows' triggers from WooCommerce metrics to Shopify
      metrics (Placed Order, Started Checkout, etc.). Turn the WooCommerce
      integration off in Klaviyo after launch.
- [ ] **QuickBooks**: install a QuickBooks Online connector from the Shopify
      app store (e.g. "QuickBooks Online Global") so Shopify orders sync to
      QBO like the WooCommerce ones did.
- [ ] Recreate **active discount codes**.
- [ ] Re-point any **Google channels**: Google Search Console (add the
      domain property if not already), Google Merchant Center feed via the
      Shopify Google & YouTube app, GA4 via the same app.
- [ ] Freeze WooCommerce changes (no new products/prices), then re-run the
      export + order import for any **orders placed since the first import**
      (`export_from_woocommerce.py` again; Matrixify skips duplicates by
      order name).

## DNS flip

- [ ] Shopify admin → Settings → Domains → Connect existing domain →
      `acccrappiestix.com` (and `www`). Shopify shows the exact A record /
      CNAME values to set at your DNS host.
- [ ] At your DNS host (likely your current web host or registrar), set the
      A record for `acccrappiestix.com` to Shopify's IP and the `www` CNAME
      to `shops.myshopify.com`.
- [ ] Wait for Shopify to issue the SSL certificate (minutes to a few hours).
- [ ] Remove the storefront password (Online Store → Preferences).

## Immediately after

- [ ] Click through: homepage, each collection, a product of every rod line,
      add to cart, checkout, blog post, warranty page.
- [ ] Test old URLs redirect: `acccrappiestix.com/product/7-1pc-spinnin-stix/`,
      a category URL, a blog post URL.
- [ ] Watch the first few real orders end-to-end (payment → fulfillment
      → QuickBooks sync → Klaviyo event).
- [ ] Submit the new sitemap in Search Console
      (`acccrappiestix.com/sitemap.xml`).

## WordPress wind-down (after ~2-4 weeks of stable Shopify)

- [ ] Keep the WordPress hosting for now — blog/page images still load from
      it until they're re-uploaded (see step 3C).
- [ ] Put WooCommerce in a state where nobody can order (disable payment
      gateways or set the site to maintenance for `/checkout`).
- [ ] When images are migrated and rankings have settled: full WordPress
      backup, then cancel hosting. Revoke the migration API key.
- [ ] Cancel WooCommerce plugin subscriptions (payment gateway, etc.).
