#!/usr/bin/env python3
"""Generates every Bangarang brand asset from two sources of truth:

  1. the designer's mark   tools/source/mark-original.png  --(tools/trace.py)-->  tools/mark-path.json
  2. Archivo (OFL) outlines at wght 900 / wdth 100 for the letters

The mark replaces the middle A of BANGARANG. It is NEVER redrawn or stretched: uniform scale only.

Needs a venv with fonttools and Archivo[wdth,wght].ttf at $ARCHIVO_TTF.
Writes: assets/brand/*.svg, assets/img/wordmark.svg, favicon.svg, tools/wm-*.html, tools/sail-a.html
"""
import json, os, pathlib
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = pathlib.Path(__file__).resolve().parent.parent
TTF = os.environ.get('ARCHIVO_TTF', '/tmp/bg/fnt/Archivo.ttf')
TR = -14            # tracking, font units
CAP = 688           # Archivo cap height, font units
SLOT_PAD = 44       # air either side of the mark inside the word, font units

# ---------------- the mark (traced from the original) ----------------
M = json.loads((ROOT/'tools'/'mark-path.json').read_text())
x0, y0, x1, y1 = M['bbox']
BW, BH = x1 - x0, y1 - y0               # mark box in source pixels
ASPECT = BW / BH
MARK_PATH = f'<path transform="translate({-x0:.3f},{-y0:.3f})" d="{M["d"]}"/>'   # normalised: sits in 0..BW x 0..BH

def mark_g(tx, ty, h, extra=''):
    s = h / BH
    return f'<g transform="translate({tx:.2f},{ty:.2f}) scale({s:.5f})" {extra}>{MARK_PATH}</g>'

# ---------------- letters ----------------
f = instantiateVariableFont(TTFont(TTF), {'wght': 900, 'wdth': 100})
gs = f.getGlyphSet(); cm = f.getBestCmap()
def glyph(ch, x):
    g = cm[ord(ch)]; pen = SVGPathPen(gs); gs[g].draw(pen)
    return f'<path transform="translate({round(x,1)},700) scale(1,-1)" d="{pen.getCommands()}" fill="currentColor"/>', gs[g].width

def build(seq):
    x = 0; parts = []
    for ch in seq:
        if ch == 'S':
            w = ASPECT * CAP
            parts.append(mark_g(x + SLOT_PAD, 700 - CAP, CAP, 'style="fill:var(--sail,currentColor)"'))
            x += w + 2*SLOT_PAD + TR
        else:
            p, w = glyph(ch, x); parts.append(p); x += w + TR
    return ''.join(parts), round(x - TR + 6)

body, total = build('BANGSRANG')         # mark in the middle
plain, total_p = build('BANGARANG')      # ordinary A (beside the standalone mark)
VB = f'0 0 {total} 712'

(ROOT/'tools'/'wm-symbol.html').write_text(f'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><symbol id="wm" viewBox="{VB}">{body}</symbol></svg>')
(ROOT/'tools'/'wm-use.html').write_text(f'<svg viewBox="{VB}" role="img" aria-label="Bangarang"><use href="#wm"/></svg>')
# inline hero mark (uniform scale, so it is never stretched by the width morph)
(ROOT/'tools'/'sail-a.html').write_text(MARK_PATH)
(ROOT/'tools'/'metrics.json').write_text(json.dumps({'aspect': ASPECT, 'bw': BW, 'bh': BH}))

# ---------------- standalone brand files ----------------
B = ROOT/'assets'/'brand'; B.mkdir(parents=True, exist_ok=True)
for old in ('brandmark.svg',):
    (B/old).unlink(missing_ok=True)
NS = 'xmlns="http://www.w3.org/2000/svg"'
INK, BONE, GLOW = '#0b100d', '#eee9da', '#d6f24a'
PAD = 14
# the mark alone: favicon, avatar, tees, stickers
(B/'mark.svg').write_text(f'<svg {NS} viewBox="{-PAD} {-PAD} {BW+2*PAD:.2f} {BH+2*PAD:.2f}" fill="currentColor" role="img" aria-label="Bangarang">{MARK_PATH}</svg>')
(B/'sail-mark.svg').unlink(missing_ok=True)
# wordmarks
(B/'wordmark.svg').write_text(f'<svg {NS} viewBox="{VB}" role="img" aria-label="Bangarang" style="color:{BONE};--sail:{GLOW}">{body}</svg>')
(ROOT/'assets'/'img'/'wordmark.svg').write_text((B/'wordmark.svg').read_text())
(B/'wordmark-plain.svg').write_text(f'<svg {NS} viewBox="0 0 {total_p} 712" role="img" aria-label="Bangarang" style="color:{BONE}">{plain}</svg>')
# stacked lockup: mark over the plain wordmark, one colour
mh = 2000; mw = mh * ASPECT; gap = 380; W = total_p; H = round(mh + gap + 712)
(B/'lockup-stacked.svg').write_text(
    f'<svg {NS} viewBox="0 0 {W} {H}" fill="currentColor" role="img" aria-label="Bangarang" style="color:{BONE}">'
    f'{mark_g((W-mw)/2, 0, mh)}<g transform="translate(0,{round(mh+gap)})">{plain}</g></svg>')
# favicon: mark on an ink square, optically centred
h = 24; w = h*ASPECT
glow_fill = 'fill="%s"' % GLOW
(ROOT/'favicon.svg').write_text(
    f'<svg {NS} viewBox="0 0 32 32"><rect width="32" height="32" fill="{INK}"/>'
    + mark_g((32-w)/2, 4, h, glow_fill) + '</svg>')
print(f'mark box {BW:.1f}x{BH:.1f} aspect {ASPECT:.4f} | wordmark {total} | lockup {W}x{H}')
