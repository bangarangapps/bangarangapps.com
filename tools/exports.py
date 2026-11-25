#!/usr/bin/env python3
"""Builds the standalone logo exports in assets/brand/export/ from the shipped files (so they can never drift from them).
Colours are baked in (no CSS variables), so the SVGs open correctly in Figma, Illustrator, Canva, Keynote.

  icon.svg            the profile picture / app icon: icon-large.svg (display-cut sail, red on an ink tile)
  wordmark-on-ink.svg   bone letters, red sail, ink background      (brand sheet: "Display cut · on ink")
  wordmark-on-bone.svg  ink letters, ink sail, bone background      (brand sheet: "On bone · sail goes ink")

Render the PNGs (icon 1024x1024, wordmarks 2400 wide) with the gstack browser:
    python3 tools/exports.py && tools/exports.sh
"""
import pathlib, re
R = pathlib.Path(__file__).resolve().parent.parent
B = R / 'assets/brand'
OUT = B / 'export'
OUT.mkdir(exist_ok=True)
INK, BONE, RED = '#0c0a0a', '#eee9da', '#ff1f2d'
NS = 'xmlns="http://www.w3.org/2000/svg"'

(OUT / 'icon.svg').write_text((B / 'icon-large.svg').read_text())

wm = (B / 'wordmark.svg').read_text()
x, y, w, h = map(float, re.search(r'viewBox="([^"]+)"', wm).group(1).split())
inner = wm[wm.index('>', wm.index('<svg')) + 1: wm.rindex('</svg>')]
PAD = 600  # units around the wordmark (cap height is 700)
vb = f'{x - PAD:g} {y - PAD:g} {w + 2 * PAD:g} {h + 2 * PAD:g}'
for name, bg, fg, sail in (('on-ink', INK, BONE, RED), ('on-bone', BONE, INK, INK)):
    body = inner.replace('var(--sail,currentColor)', sail).replace('currentColor', fg)
    (OUT / f'wordmark-{name}.svg').write_text(
        f'<svg {NS} viewBox="{vb}" role="img" aria-label="Bangarang">'
        f'<rect x="{x - PAD:g}" y="{y - PAD:g}" width="{w + 2 * PAD:g}" height="{h + 2 * PAD:g}" fill="{bg}"/>{body}</svg>')
print(f'wordmark export viewBox {vb} (aspect {(w + 2 * PAD) / (h + 2 * PAD):.4f})')
