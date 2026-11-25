#!/usr/bin/env python3
"""Builds the standalone logo exports in assets/brand/export/ from the shipped files (so they can never drift from them).
Colours are baked in (no CSS variables), so the SVGs open correctly in Figma, Illustrator, Canva, Keynote.

  icon.svg                    profile picture / app icon: icon-large.svg (display-cut sail, red on an ink tile)
  wordmark-for-light-bg.svg   TRANSPARENT background, ink letters, red sail   (light mode, white or bone surfaces)
  wordmark-for-dark-bg.svg    TRANSPARENT background, bone letters, red sail  (dark mode, ink or black surfaces)

The sail is brand red in both (owner, 2026-11-24). Render the PNGs (icon 1024x1024 on its tile, wordmarks 2400 wide with
an alpha channel) with the gstack browser:
    python3 tools/exports.py && tools/exports.sh
"""
import pathlib, re
R = pathlib.Path(__file__).resolve().parent.parent
B = R / 'assets/brand'
OUT = B / 'export'
OUT.mkdir(exist_ok=True)
INK, BONE, RED = '#0c0a0a', '#eee9da', '#ff1f2d'
NS = 'xmlns="http://www.w3.org/2000/svg"'

for old in ('wordmark-on-ink', 'wordmark-on-bone'):
    for ext in ('svg', 'png'):
        (OUT / f'{old}.{ext}').unlink(missing_ok=True)

(OUT / 'icon.svg').write_text((B / 'icon-large.svg').read_text())

wm = (B / 'wordmark.svg').read_text()
x, y, w, h = map(float, re.search(r'viewBox="([^"]+)"', wm).group(1).split())
inner = wm[wm.index('>', wm.index('<svg')) + 1: wm.rindex('</svg>')]
PAD = 40  # a hair of air so antialiased edges are never clipped; placement margins are the user's call
vb = f'{x - PAD:g} {y - PAD:g} {w + 2 * PAD:g} {h + 2 * PAD:g}'
for name, fg in (('for-light-bg', INK), ('for-dark-bg', BONE)):
    body = inner.replace('var(--sail,currentColor)', RED).replace('currentColor', fg)
    (OUT / f'wordmark-{name}.svg').write_text(f'<svg {NS} viewBox="{vb}" role="img" aria-label="Bangarang">{body}</svg>')
print(f'wordmark export viewBox {vb} (aspect {(w + 2 * PAD) / (h + 2 * PAD):.4f})')
