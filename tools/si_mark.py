#!/usr/bin/env python3
"""Pulls SimpleInvite's current brandmark (the card) and app icon from the simpleinvite repo's origin/main and applies them here:
  - assets/brand/simpleinvite-card.svg      the mark, black (single colour; use currentColor in HTML)
  - assets/brand/simpleinvite-icon.svg      the cobalt app icon (their icon.svg, the 512 full-bleed app icon; NOT favicon.svg, which is a separate tab-icon file)
  - index.html                              the SimpleInvite panel's brand row
Source of truth is THEIR repo: packages/design/src/brand/card.ts and apps/app/public/icons/icon.svg.
Run after SimpleInvite changes its mark:  python3 tools/si_mark.py
"""
import pathlib, re, subprocess
R = pathlib.Path(__file__).resolve().parent.parent
SI = pathlib.Path.home() / 'Development/bangarang/simpleinvite'
def show(path): return subprocess.run(['git', '-C', str(SI), 'show', f'origin/main:{path}'], check=True, capture_output=True, text=True).stdout
subprocess.run(['git', '-C', str(SI), 'fetch', '-q', 'origin'], check=False)
card = show('packages/design/src/brand/card.ts')
vb = re.search(r'CARD_VIEWBOX = "([^"]+)"', card).group(1)
stroke = re.search(r'CARD_STROKE = ([\d.]+)', card).group(1)
path = re.search(r'CARD_PATH =\s*"([^"]+)"', card).group(1)
face = re.search(r'CARD_FACE =\s*"([^"]+)"', card).group(1)
w, h = (float(x) for x in vb.split()[2:])
inner = (f'<path d="{face}" fill="currentColor" stroke="none"/>'
         f'<path d="{path}"/>')
attrs = f'viewBox="{vb}" fill="none" stroke="currentColor" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" overflow="visible"'
(R / 'assets/brand/simpleinvite-card.svg').write_text(
    f'<svg xmlns="http://www.w3.org/2000/svg" {attrs} style="color:#111" role="img" aria-label="SimpleInvite">{inner}</svg>')
(R / 'assets/brand/simpleinvite-icon.svg').write_text(show('apps/app/public/icons/icon.svg'))
# the homepage brand row: the card at the lockup's proportions (1.177em tall, .306em gap, .04em seat), single colour
svg = f'<svg class="si-card" {attrs} aria-hidden="true" focusable="false">{inner}</svg>'
p = R / 'index.html'; s = p.read_text()
s, n = re.subn(r'(<section class="panel si"[^>]*>.*?<div class="brandrow rv">\s*)<svg.*?</svg>', lambda m: m.group(1) + svg, s, count=1, flags=re.S)
assert n == 1, 'brandrow not found'
p.write_text(s)
print('card', vb, 'stroke', stroke, '| wrote assets/brand/simpleinvite-card.svg, simpleinvite-icon.svg, patched index.html')
