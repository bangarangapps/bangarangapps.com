# Next session — bangarangapps.com

**State (2026-10-14):** live at https://bangarangapps.com. Home, /privacy, /terms, /refunds, /contact, real 404. Stripe business-URL check passed; temp Cloudflare skip rule deleted; Security Level back to Medium; Browser Integrity Check OFF (keep it off).

**Read first:** `docs/BRAND.md` (voice rules, palette, per-product header accents, policies), `docs/ACCESSIBILITY.md`, `README.md` (deploy via `tools/deploy.sh`).

**Open items (none blocking):**
- `www.bangarangapps.com` serves the page directly (no redirect to apex). Add a Cloudflare redirect rule (needs a token with rulesets edit, or Adam adds it).
- OG image is brand red only; decide whether product accents belong in it.
- Product screenshots (`assets/img/*.webp`) go stale when SimpleInvite/fdbck UI changes; re-capture.
- 16/32 px favicon and shirt/merch mockups of the mark are untested.
- fdbck's refund wording was written by us (no prior policy): Adam to confirm it is the policy he wants.

**Pending decision:** `docs/lockup-proportions.html` (built by `tools/proportions_sheet.py`) proposes a refined display-cut lockup: mark snapped to 18u, pads 21/63 instead of 52/88 (gaps +10% over the typeface's own A instead of +25%). Candidate SVG in `docs/lockup-refined/`. Not shipped. To ship: set MARK_K=18/14 and the display cut's pad_l/pad_r in `tools/wordmark.py`, run wordmark.py + inject.py, bump `?v=`, `tools/deploy.sh`. Small cut unchanged.
