# Next session — bangarangapps.com

**State (2026-10-14):** live at https://bangarangapps.com. Home, /privacy, /terms, /refunds, /contact, real 404. Stripe business-URL check passed; temp Cloudflare skip rule deleted; Security Level back to Medium; Browser Integrity Check OFF (keep it off).

**Read first:** `docs/BRAND.md` (voice rules, palette, per-product header accents, policies), `docs/ACCESSIBILITY.md`, `README.md` (deploy via `tools/deploy.sh`).

**Open items (none blocking):**
- `www.bangarangapps.com` serves the page directly (no redirect to apex). Add a Cloudflare redirect rule (needs a token with rulesets edit, or Adam adds it).
- OG card now built by `tools/og.py` (matches the hero). Social platforms cache old images; re-scrape with their debuggers if a stale card shows.
- Product screenshots (`assets/img/*.webp`) go stale when SimpleInvite/fdbck UI changes; re-capture.
- 16/32 px favicon and shirt/merch mockups of the mark are untested.
- fdbck's refund wording was written by us (no prior policy): Adam to confirm it is the policy he wants.

**Shipped 2026-10-14:** refined display-cut lockup (mark 18u, pads .0297/.0907). Review + measurements: `docs/lockup-proportions.html`; pre-change files: `docs/lockup-before/`. Small cut pads unchanged.

**SimpleInvite mark (2026-10-16):** the homepage panel and brand sheet use SimpleInvite's new card mark and cobalt app icon. Source: their repo origin/main (`packages/design/src/brand/card.ts`, `icons/icon.svg`); re-sync with `python3 tools/si_mark.py` then `tools/deploy.sh`. Their favicon is changing separately; we do not use it.
