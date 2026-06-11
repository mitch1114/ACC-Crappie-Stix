# Step 4 — The theme

The `theme/` folder contains **Shopify Horizon v3.5.1** — Shopify's current
flagship free theme (fast, modern, fully editable in the admin theme editor)
— with an ACC brand color scheme added.

## What's customized

- **`scheme-acc-brand`** color scheme in `theme/config/settings_data.json`:
  near-black background (`#0d0d0d`), white text, ACC green (`#8cc63e`)
  buttons and accents. Apply it to any section in the theme editor via
  the section's "Color scheme" picker — it shows up as the last scheme.
  If the green doesn't match your logo exactly, tell me the hex code from
  your logo file and I'll dial it in.

## Push it to your store

With [Shopify CLI](https://shopify.dev/docs/api/shopify-cli) installed
(`npm i -g @shopify/cli`):

```bash
cd theme
shopify theme push --store acc-crappie-stix.myshopify.com --unpublished --theme "ACC Horizon"
```

Then in Shopify admin → Online Store → Themes, click **Customize** on
"ACC Horizon" to set it up visually, and **Publish** when ready.

For live development (edit code here, see changes instantly):

```bash
cd theme
shopify theme dev --store acc-crappie-stix.myshopify.com
```

## Suggested homepage build (in the theme editor)

1. **Hero** — full-width shot of a slab crappie coming over the gunwale, ACC
   brand color scheme, headline "Feel Every Bite", button → Shop All.
2. **Collection list** — the rod lines: Jiggin' Stix, Spinnin' Stix,
   Scopin' Stix, Green Series, Apparel.
3. **Featured collection** — best sellers row.
4. **Image with text** — the ACC story / 100% money-back guarantee.
5. **Testimonials/press** — quotes from tournament anglers.
6. **Blog posts** — latest from the blog.
7. **Email signup** — wired to Klaviyo once the integration is on.

Set up the main menu (Online Store → Navigation) to mirror the old site:
Shop (mega-menu by rod line), Apparel, Blog, Warranty, Contact, Dealer info.

## Logo and brand assets

Upload your logo in the theme editor (Theme settings → Logo). Horizon also
takes an inverse (white) logo for dark sections — worth exporting from your
logo source file.

Once the store exists and the theme is pushed, I can iterate on any of this
in code — custom sections, a rod-specs block for product pages (length,
pieces, action, guides), dealer locator page, whatever you need.
