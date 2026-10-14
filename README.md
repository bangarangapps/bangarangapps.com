# bangarangapps.com

Static site for Bangarang Apps, Inc. Plain HTML/CSS/JS, no build step, no dependencies.

- `index.html` — the scroll story (hero, manifesto, apps, how we work, contact)
- `privacy/`, `terms/`, `refunds/`, `contact/`, `404.html` — shared shell, `bone`/`glow` worlds
- `assets/css/site.css` — all styles. Color is organised into `[data-world]` blocks.
- `assets/js/site.js` — one rAF loop for scroll motion; respects `prefers-reduced-motion`
- `docs/BRAND.md` — voice and visual rules. Read before editing copy or type.
- `assets/brand/` + `tools/wordmark.py` — the mark. All logo files are generated (`tools/construct.py`, `tools/wordmark.py`, `tools/inject.py`); don't hand-edit. `docs/brand-board.html` shows every format.

Deploy (Cloudflare Pages project `bangarangapps-com`):

    wrangler pages deploy . --project-name=bangarangapps-com --branch=main        # production
    wrangler pages deploy . --project-name=bangarangapps-com --branch=redesign   # preview

Bump the `?v=` on the CSS/JS links in every HTML file when either changes.

## Deploy
`tools/deploy.sh` (production) or `tools/deploy.sh <branch>` (preview URL). Bump `?v=` on CSS/JS links first. It purges the Cloudflare cache twice and verifies the new version is serving. Cloudflare Browser Integrity Check must stay OFF (it blocked Stripe's site check).
