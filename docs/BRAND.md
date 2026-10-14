# Bangarang Apps — brand

**Who:** Bangarang Apps, Inc. An app studio building sharp, modern apps in categories that got comfortable. Current products: SimpleInvite, fdbck.

**Voice:** light, quick, a little mischievous, never smug. Hints that we want to do it better and put some life back into a market, never a word against anyone. Short sentences. No filler sublines. Confident, not cheeky.
- The name is the nod. Never reference the film, never use pirate/nautical language ("ship" as in ship apps is fine).
- **Never state a headcount** (no "two of us", no "two founders") and **never frame the product line as small or finished** (no "two so far", "just two"). Say "Out now", not "two so far".
- **Never mention agents, AI, vibe coding or similar anywhere on the site**, including product copy (fdbck's panel is written without it). Hint at modern tooling only: "modern tools", "the newest tools we can get our hands on".
- **No exclamation mark in the brand.** The wordmark is plain BANGARANG.
- **Say "apps", never "software".**
- Never name or criticise an incumbent. "Some app categories got comfortable" is as pointed as it gets.

**Mark:** the designer's own artwork (a three-panel sail), rebuilt as clean vectors by `tools/construct.py` from `tools/source/mark-original.png` under three rules the owner set: (1) the right-hand edges of the cap and the band lie on ONE straight line (apex to the swoosh's top-right corner), the band's top-right is a sharp corner on that line, and the swoosh's curve starts at that corner; (2) the two gaps are exactly the same width (11 px at source scale) and parallel along their whole length, so the three pieces read as one continuous flow; (3) proportions and curvature come from the original. 11 Bezier segments in total, smooth (tangent-continuous) except at true corners. Not a raw trace: a pixel trace of the 278 px original kept its wobble and was rejected as bumpy. It replaces the middle A of the name. **Never redraw, stretch, skew, split or recolour pieces of it; uniform scale only.** **Two optical cuts:** display (gaps as drawn, 11 px at source scale) for hero/large/print; small (22 px gaps, tracking +3%, extra air right of the mark) for header, footer and favicon, so the three pieces survive at 16-36 px and the R doesn't crowd the mark. Same geometry otherwise. Build the small mark with `python tools/construct.py --gap 22 --out mark-path-small.json -q`. Generated formats in `assets/brand/`: `mark.svg`, `wordmark.svg`, `wordmark-plain.svg`, `lockup-stacked.svg`; plus `/favicon.svg`, `/apple-touch-icon.png`, `/og.png`. Regenerate: `tools/construct.py` then `tools/wordmark.py`, `tools/inject.py`, `tools/board.py`. To change the design, change the constants/anchors at the top of `construct.py` (GAP, corner anchors), not the SVGs.

**Visual:** one stylesheet, color in "worlds". Studio worlds: ink `#0c0a0a`, oxblood `#210d10`, bone `#eee9da`, **highlighter red `#ff1f2d`** (the mark, the accent, the finale; a nod to Rufio's hair, never named). Buttons on red use ink text (white fails contrast). Product panels wear the product's own colors, and the header sail and CTA follow them (see "Per-product header accent" below). Product sections wear the product's own identity: SimpleInvite = paper `#efeae0` + persimmon `#d8512f` + Young Serif/Hanken; fdbck = night `#0a0a0b` + amber `#d97706` + Outfit/DM Sans. Wordmark: **Gabarito Bold** (SIL OFL; vendored in `tools/source/fonts`; chosen from `docs/wordmark-options.html`). Site type: Archivo for headings/body, JetBrains Mono for labels.
- Motion is scroll-linked. **The logo is never animated: no squish, stretch, morph or colour sweep.** Hero interaction is depth only: the eyebrow and statement drift up slightly faster than the pinned logo.
- Motion rules otherwise: horizontal/vertical only. No tilt, no skew, no stacked or overlapping objects, no fake materials (house rule). Reduced motion = static page.
- Real imagery only: product shots are 2x captures of the live products (`assets/img`). Re-capture when a product's UI changes.
- Never Fraunces. No gradients.

**Gotchas learned:**
- `.wrap` is margin-based. Never put a `padding` shorthand on an element that also carries `.wrap` (v1 bug: it zeroed the mobile gutter).
- Cloudflare Browser Integrity Check was blocking Stripe's site-verification crawler; it is OFF on this zone. Leave it off.

## Per-product header accent
While a product panel is under the header, the sail and "Say hello" button take that product's own accent: SimpleInvite `#0f3fa8` (its CTA blue), fdbck `#d97706` (amber). Everywhere else: brand red. The SimpleInvite panel mark is the product's current envelope mark (copied from simpleinvite.app `svg.logo-card`), always black `#111`, never an accent color.

## Policies and payments (Stripe site verification)
Stripe's business-website check wants: business name, what is sold, customer-service contact, refund/dispute/cancellation policy, no password, no region blocks, not under construction. This site satisfies it with `/refunds/` (cancellation, refunds, disputes, tax, restrictions for both products), a "Products and payments" section in `/terms/`, and three contact addresses. Keep `/refunds/` in step with SimpleInvite's and fdbck's own terms (SimpleInvite: $5/event, $39/year, no auto-renew; fdbck: Pro subscription, cancel anytime, keep until period end). Anchor links (`#apps`, `#hello`...) land flush at the top (`scroll-margin-top`) so the header takes the target's color world.
