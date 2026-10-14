# Bangarang Apps — brand

**Who:** Bangarang Apps, Inc. A software studio building sharp, modern apps in categories that got comfortable. Current products: SimpleInvite, fdbck.

**Voice:** light, quick, a little mischievous, never smug. Hints that we want to do it better and put some life back into a market, never a word against anyone. Short sentences. No filler sublines. Confident, not cheeky.
- The name is the nod. Never reference the film, never use pirate/nautical language ("ship" as in ship software is fine).
- **Never state a headcount** (no "two of us", no "two founders") and **never frame the product line as small or finished** (no "two so far", "just two"). Say "Out now", not "two so far".
- **Never mention agents, AI, vibe coding or similar anywhere on the site**, including product copy (fdbck's panel is written without it). Hint at modern tooling only: "modern tools", "the newest tools we can get our hands on".
- **No exclamation mark in the brand.** The wordmark is plain BANGARANG.
- Never name or criticise an incumbent. "Some corners of software got comfortable" is as pointed as it gets.
- Agentic tooling is part of the story ("a crew of agents"), stated plainly.

**Mark:** the middle A of the name is a pair of sails (a jib and a main) from one source file, `tools/wordmark.py`. Anatomy matters: straight mast edges, flat feet on the baseline, one billowed edge, a sagging jib luff, a gap that widens toward the base like an A's counter. It reads as sails first and an A by context and silhouette (peak + wide base). Not a pirate sail: no square rig, no flag, no hull. Rejected: crescent/blade legs ("banana"), seam or window-pane cuts. Formats in `assets/brand/`: `sail-mark.svg` (favicon, avatar), `brandmark.svg` (sails + 3-bar wake: tees, stickers), `wordmark.svg` / `wordmark-plain.svg`, `lockup-stacked.svg`. One colour or sails-in-accent only. Never redraw; regenerate. On the site the main fills and the jib works as the hero scrolls (`setSail` in site.js mirrors the Python geometry). Board with every format: `docs/brand-board.html`.

**Visual:** one stylesheet, color in "worlds". Studio worlds: ink `#0b100d`, forest `#132119`, bone `#eee9da`, glow `#d6f24a`. Product sections wear the product's own identity: SimpleInvite = paper `#efeae0` + persimmon `#d8512f` + Young Serif/Hanken; fdbck = night `#0a0a0b` + amber `#d97706` + Outfit/DM Sans. Studio type: Archivo (variable width axis 62-125), JetBrains Mono for labels.
- Motion is scroll-linked and horizontal/vertical only. No tilt, no skew, no stacked or overlapping objects, no fake materials (house rule). Reduced motion = static page.
- Real imagery only: product shots are 2x captures of the live products (`assets/img`). Re-capture when a product's UI changes.
- Never Fraunces. No gradients.

**Gotchas learned:**
- `.wrap` is margin-based. Never put a `padding` shorthand on an element that also carries `.wrap` (v1 bug: it zeroed the mobile gutter).
- Cloudflare Browser Integrity Check was blocking Stripe's site-verification crawler; it is OFF on this zone. Leave it off.
