#!/usr/bin/env python3
"""Generates every Bangarang brand asset from two sources of truth:

  1. the designer's mark: tools/source/mark-original.png --(tools/construct.py)--> tools/mark-path.json
  2. Archivo (OFL) outlines at wght 900 / wdth 100 for the letters

The mark replaces the middle A of BANGARANG and stands TALLER than the letters (MARK_K x cap height,
hanging MARK_DROP below the baseline). It is never redrawn or stretched: uniform scale only.
The wordmark is rigid everywhere, including the hero: no width axis, no morphing.

Needs a venv with fonttools and Archivo[wdth,wght].ttf at $ARCHIVO_TTF.
Writes: assets/brand/*.svg, assets/img/wordmark.svg, favicon.svg,
        tools/wm-symbol.html, wm-use.html (header/footer), tools/hero-d.html, hero-m.html (hero), tools/metrics.json
"""
import json, os, pathlib
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = pathlib.Path(__file__).resolve().parent.parent
TTF = os.environ.get('ARCHIVO_TTF', '/tmp/bg/fnt/Archivo.ttf')
TR = -14            # tracking, font units
CAP = 688           # Archivo cap height, font units
BASE = 700          # baseline y in the wordmark box
SLOT_PAD = 52       # air either side of the mark inside the word
MARK_K = 1.30       # mark height / cap height
MARK_DROP = 0.08    # fraction of cap height the mark hangs below the baseline

# ---------------- the mark ----------------
M = json.loads((ROOT/'tools'/'mark-path.json').read_text())
x0, y0, x1, y1 = M['bbox']
BW, BH = x1 - x0, y1 - y0
ASPECT = BW / BH
MARK_PATH = f'<path transform="translate({-x0:.3f},{-y0:.3f})" d="{M["d"]}"/>'
MH = MARK_K * CAP                      # mark height inside the wordmark
MW = ASPECT * MH
DROP = MARK_DROP * CAP

def mark_g(tx, ty, h, extra=''):
    return f'<g transform="translate({tx:.2f},{ty:.2f}) scale({h/BH:.5f})" {extra}>{MARK_PATH}</g>'

# ---------------- letters ----------------
f = instantiateVariableFont(TTFont(TTF), {'wght': 900, 'wdth': 100})
gs = f.getGlyphSet(); cm = f.getBestCmap()
def glyph(ch, x, base, hero):
    g = cm[ord(ch)]; pen = SVGPathPen(gs); gs[g].draw(pen); bp = BoundsPen(gs); gs[g].draw(bp)
    cx = x + (bp.bounds[0]+bp.bounds[2])/2
    attr = f' class="lt" data-cx="{cx:.0f}" data-cy="{base-CAP/2:.0f}"' if hero else ''
    return f'<path{attr} transform="translate({round(x,1)},{base}) scale(1,-1)" d="{pen.getCommands()}" fill="currentColor"/>', gs[g].width

def line(seq, x=0.0, base=BASE, hero=False):
    parts = []
    for ch in seq:
        if ch == 'S':
            ty = base + DROP - MH
            attr = f'class="mg" data-cx="{x+SLOT_PAD+MW/2:.0f}" data-cy="{ty+MH/2:.0f}" ' if hero else ''
            parts.append(mark_g(x + SLOT_PAD, ty, MH, attr + 'style="fill:var(--sail,currentColor)"'))
            x += MW + 2*SLOT_PAD + TR
        else:
            p, w = glyph(ch, x, base, hero); parts.append(p); x += w + TR
    return ''.join(parts), x - TR + 6

MARK_TOP = BASE + DROP - MH
MARK_BOT = BASE + DROP
VY0 = round(min(0, MARK_TOP) - 6); VY1 = round(max(712, MARK_BOT) + 6); VH = VY1 - VY0

body, total = line('BANGSRANG'); total = round(total)
plain, total_p = line('BANGARANG'); total_p = round(total_p)
VB = f'0 {VY0} {total} {VH}'
(ROOT/'tools'/'wm-symbol.html').write_text(f'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><symbol id="wm" viewBox="{VB}">{body}</symbol></svg>')
# a <use>d symbol is placed at the outer viewport's origin, so the outer box starts at 0,0 (the symbol's own viewBox carries the offset)
(ROOT/'tools'/'wm-use.html').write_text(f'<svg viewBox="0 0 {total} {VH}" role="img" aria-label="Bangarang"><use href="#wm"/></svg>')

# hero lockups: the same rigid logo; letters carry data-cx/cy so the page can colour them outward from the mark
hd, _ = line('BANGSRANG', hero=True)
(ROOT/'tools'/'hero-d.html').write_text(f'<svg class="hw-d" viewBox="{VB}" aria-hidden="true" focusable="false">{hd}</svg>')
y2 = round(712 + 44 + MH - DROP)                     # line-2 baseline: the mark's head clears line 1 with air
L1, w1 = line('BANG', 0, BASE, True)
L2, w2 = line('SRANG', 0, y2, True)
Wm = round(max(w1, w2)); Hm = round(y2 + max(12, DROP) + 6)
(ROOT/'tools'/'hero-m.html').write_text(f'<svg class="hw-m" viewBox="0 0 {Wm} {Hm}" aria-hidden="true" focusable="false">{L1}{L2}</svg>')
(ROOT/'tools'/'metrics.json').write_text(json.dumps({'aspect': ASPECT, 'bw': BW, 'bh': BH, 'vb_h': VH, 'vb_w': total}))

# ---------------- standalone brand files ----------------
B = ROOT/'assets'/'brand'; B.mkdir(parents=True, exist_ok=True)
NS = 'xmlns="http://www.w3.org/2000/svg"'
INK, BONE, GLOW = '#0b100d', '#eee9da', '#d6f24a'
PAD = 14
(B/'mark.svg').write_text(f'<svg {NS} viewBox="{-PAD} {-PAD} {BW+2*PAD:.2f} {BH+2*PAD:.2f}" fill="currentColor" role="img" aria-label="Bangarang">{MARK_PATH}</svg>')
(B/'wordmark.svg').write_text(f'<svg {NS} viewBox="{VB}" role="img" aria-label="Bangarang" style="color:{BONE};--sail:{GLOW}">{body}</svg>')
(ROOT/'assets'/'img'/'wordmark.svg').write_text((B/'wordmark.svg').read_text())
(B/'wordmark-plain.svg').write_text(f'<svg {NS} viewBox="0 0 {total_p} 712" role="img" aria-label="Bangarang" style="color:{BONE}">{plain}</svg>')
mh = 2000; mw = mh * ASPECT; gap = 380; W = total_p; H = round(mh + gap + 712)
(B/'lockup-stacked.svg').write_text(
    f'<svg {NS} viewBox="0 0 {W} {H}" fill="currentColor" role="img" aria-label="Bangarang" style="color:{BONE}">'
    f'{mark_g((W-mw)/2, 0, mh)}<g transform="translate(0,{round(mh+gap)})">{plain}</g></svg>')
h = 24; w = h*ASPECT
glow_fill = 'fill="%s"' % GLOW
(ROOT/'favicon.svg').write_text(
    f'<svg {NS} viewBox="0 0 32 32"><rect width="32" height="32" fill="{INK}"/>' + mark_g((32-w)/2, 4, h, glow_fill) + '</svg>')
print(f'mark {BW:.0f}x{BH:.0f} aspect {ASPECT:.4f} | in-word mark {MW:.0f}x{MH:.0f} (cap {CAP}; top {MARK_TOP:.0f}, bottom {MARK_BOT:.0f}) | wordmark vb {VB} | hero-m {Wm}x{Hm} | lockup {W}x{H}')
