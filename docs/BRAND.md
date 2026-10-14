# Bangarang Apps — brand

**Who:** Bangarang Apps, Inc. Two founders, a crew of agents, building small sharp apps in categories that got comfortable. Current products: SimpleInvite, fdbck.

**Voice:** light, quick, a little mischievous, never smug. Hints that we want to do it better and put some life back into a market, never a word against anyone. Short sentences. No filler sublines. Confident, not cheeky.
- The name is the nod: "Bangarang!" with the glow exclamation mark. Never reference the film, never use pirate/nautical language ("ship" as in ship software is fine; "crew" sparingly).
- Never name or criticise an incumbent. "Some corners of software got comfortable" is as pointed as it gets.
- Agentic tooling is part of the story ("a crew of agents"), stated plainly.

**Visual:** one stylesheet, color in "worlds". Studio worlds: ink `#0b100d`, forest `#132119`, bone `#eee9da`, glow `#d6f24a`. Product sections wear the product's own identity: SimpleInvite = paper `#efeae0` + persimmon `#d8512f` + Young Serif/Hanken; fdbck = night `#0a0a0b` + amber `#d97706` + Outfit/DM Sans. Studio type: Archivo (variable width axis 62-125), JetBrains Mono for labels.
- Motion is scroll-linked and horizontal/vertical only. No tilt, no skew, no stacked or overlapping objects, no fake materials (house rule). Reduced motion = static page.
- Real imagery only: product shots are 2x captures of the live products (`assets/img`). Re-capture when a product's UI changes.
- Never Fraunces. No gradients.

**Gotchas learned:**
- `.wrap` is margin-based. Never put a `padding` shorthand on an element that also carries `.wrap` (v1 bug: it zeroed the mobile gutter).
- Cloudflare Browser Integrity Check was blocking Stripe's site-verification crawler; it is OFF on this zone. Leave it off.
