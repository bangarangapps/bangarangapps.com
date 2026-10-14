# Accessibility

Target: **WCAG 2.2 AA**, plus our own bar of 44 px hit areas.

## How it is checked (repeatable)
1. **axe-core 4.10** on every page (`/`, `/contact/`, `/privacy/`, `/terms/`, `/refunds/`, 404) at 1280 and 390 px, in the *un-scrolled* state: inject `axe.min.js` from cdnjs and run `axe.run()`.
2. `tools/a11y/custom-audit.js`: contrast of every text element in every color world (alpha blended on the real background), focus-ring contrast, hit areas, landmarks/headings/alt/lang.
3. Reduced motion: page loaded with `matchMedia('(prefers-reduced-motion: reduce)')` forced true. No JS: scripts stripped.

## Result (2026-10-15)
- axe: 0 violations on all pages, both widths. "Needs review" = 13 outline-text words in the decorative marquee strip (`aria-hidden`, transparent fill + stroke); not content.
- Text contrast passes in all worlds (ink, oxblood, red, paper, night, bone). Brand red `#ff1f2d`: 5.2:1 on ink, 4.9:1 on oxblood; ink on red 5.2:1 (white on red would fail at 3.8:1, so buttons/finale use ink).
- Focus ring (2px, offset 3px, world accent): 3.4 to 6.2:1 against its ground. `scroll-padding-top` keeps focused items clear of the fixed header (WCAG 2.4.11).
- Landmarks: one `header`, labelled `nav` x2, `main`, `footer`; one `h1`; headings in order; every image has alt; `lang="en"`; skip link works.
- Reduced motion: no reveals hidden, no scroll-linked motion, hero is one normal screen. No JS: all content visible.

## Rules we hold
- The manifesto's un-lit words floor at opacity .45 (3.9:1). The accent word ("life") never dims, because red cannot reach 3:1 when faded.
- Links that open a new tab say so for assistive tech (`.sr` text).
- Decorative SVG is `aria-hidden`; the logo link has `aria-label`; the hero `h1` carries the name.
- Never convey meaning by color alone. Never animate the logo.

## Known limits
- 11-12 px mono labels meet contrast but are small. They are labels, not content.
- Inline links inside legal copy are under 44 px tall (allowed by the WCAG inline-link exception).
- Not tested with a screen reader or in forced-colors mode; run VoiceOver and a Windows High Contrast pass before any accessibility claim in marketing copy.
