# Step 2 — Export your data from WordPress

Time: ~20 minutes of clicking, then the export script runs on its own.
Nothing here changes your live site — it's all read-only.

## A. Create WooCommerce API keys (for products/customers/orders)

1. Log in to WordPress admin (`acccrappiestix.com/wp-admin`).
2. Go to **WooCommerce → Settings → Advanced → REST API → Add key**.
3. Description: `Shopify migration`. User: you. Permissions: **Read**.
4. Click **Generate API key** and copy both the **Consumer key** (`ck_...`)
   and **Consumer secret** (`cs_...`) somewhere safe — the secret is shown
   only once.

## B. Run the export script (on your computer)

You need Python 3 installed (macOS has it; on Windows get it from
[python.org](https://www.python.org/downloads/) and check "Add to PATH").

```bash
# from the repo root, one-time setup:
pip install requests

# the export (paste your real keys):
python migration/export_from_woocommerce.py \
    --url https://acccrappiestix.com \
    --key ck_xxxxxxxxxxxxxxxxxxxx \
    --secret cs_xxxxxxxxxxxxxxxxxxxx
```

It saves JSON files into `migration/data/`. If you have years of orders this
can take 10–30 minutes — let it run.

> **Cloudflare/firewall note:** if the script gets blocked (403 errors), your
> security plugin or Cloudflare is challenging it. Allowlist your own IP, or
> temporarily set Cloudflare's security level to "Essentially Off" while the
> export runs.

## C. Export blog posts & pages (WXR)

1. In WordPress admin go to **Tools → Export**.
2. Choose **All content** → **Download Export File**.
3. Save the `.xml` file into `migration/data/`.

## D. Sanity-check

`migration/data/` should now contain:

```
products.json     categories.json    variations.json
customers.json    orders.json        acccrappiestix.WordPress.xml
```

When it does, either run the converters yourself
([Step 3](03-data-migration.md)) or start a Claude session in this repo and
say "the WooCommerce exports are in migration/data — convert and check them"
and I'll take it from there, including eyeballing the output for problems.

## E. Clean up

After the migration is fully done, delete the API key
(WooCommerce → Settings → Advanced → REST API → Revoke).
