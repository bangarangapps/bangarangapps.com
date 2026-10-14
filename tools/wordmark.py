#!/usr/bin/env python3
"""Generates every Bangarang brand asset from one source of truth.

  Archivo (OFL) outlines at wght 900 / wdth 100  +  the hand-drawn sail pair (below).
  The sails replace the middle A of BANGARANG: a sagging-luff jib and a billowed main,
  a mast gap that widens downward like an A's counter, flat feet on the baseline.

Needs a venv with fonttools and Archivo[wdth,wght].ttf at $ARCHIVO_TTF.
Run from anywhere:  ARCHIVO_TTF=... python tools/wordmark.py
Writes: assets/brand/*.svg, assets/img/wordmark.svg, favicon.svg, tools/wm-*.html, tools/sail-a.html, tools/metrics.json
"""
import json, os, pathlib
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = pathlib.Path(__file__).resolve().parent.parent
TTF = os.environ.get('ARCHIVO_TTF', '/tmp/bg/fnt/Archivo.ttf')
TR = -14   # tracking, font units
CAP = 688  # Archivo cap height, font units

# ---------------- the sails: 100 x 100 box, y down ----------------
JIB  = 'M45 6C32 42 16 74 0 100L37 100Z'
MAIN = 'M52 0L52 100L100 100C101 66 86 30 52 0Z'
WAKE = [(6, 110, 88, 5), (22, 121, 64, 5), (42, 132, 36, 5)]   # x, y, w, h (merch lockup only)
SAILS = f'<path d="{JIB}"/><path d="{MAIN}"/>'
WAKE_SVG = ''.join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>' for x, y, w, h in WAKE)

def inst(wd):
    return instantiateVariableFont(TTFont(TTF), {'wght': 900, 'wdth': wd})

# ---------------- hero metrics (inline sail width in em per wdth) ----------------
metrics = {}
for wd in (62, 100, 125):
    f = inst(wd); gs = f.getGlyphSet(); cm = f.getBestCmap()
    g = cm[ord('A')]; bp = BoundsPen(gs); gs[g].draw(bp)
    metrics[wd] = {'ink': (bp.bounds[2]-bp.bounds[0])/1000, 'lsb': bp.bounds[0]/1000, 'adv': gs[g].width/1000}
(ROOT/'tools'/'metrics.json').write_text(json.dumps(metrics, indent=1))

# ---------------- wordmarks @ wdth 100 ----------------
f = inst(100); gs = f.getGlyphSet(); cm = f.getBestCmap()
def glyph_path(ch, x):
    g = cm[ord(ch)]; pen = SVGPathPen(gs); gs[g].draw(pen)
    return f'<path transform="translate({round(x,1)},700) scale(1,-1)" d="{pen.getCommands()}" fill="currentColor"/>', gs[g].width
abp = BoundsPen(gs); gs[cm[ord('A')]].draw(abp)
A_LSB, A_W = abp.bounds[0], abp.bounds[2]-abp.bounds[0]

def build(seq):
    x = 0; parts = []
    for ch in seq:
        if ch == 'S':
            sx, sy = round(x + A_LSB, 1), 700 - CAP
            parts.append(f'<g transform="translate({sx},{sy}) scale({A_W/100:.5f},{CAP/100:.5f})" style="fill:var(--sail,currentColor)">{SAILS}</g>')
            x += gs[cm[ord('A')]].width + TR
        else:
            p, w = glyph_path(ch, x); parts.append(p); x += w + TR
    return ''.join(parts), round(x - TR + 6)

body, total = build('BANGSRANG'.replace('S', 'S'))            # sail A in the middle
plain, total_p = build('BANGARANG')                            # ordinary A (used under the brandmark)
VB = f'0 0 {total} 712'

(ROOT/'tools'/'wm-symbol.html').write_text(f'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><symbol id="wm" viewBox="{VB}">{body}</symbol></svg>')
(ROOT/'tools'/'wm-use.html').write_text(f'<svg viewBox="{VB}" role="img" aria-label="Bangarang"><use href="#wm"/></svg>')
(ROOT/'tools'/'sail-a.html').write_text(SAILS)

# ---------------- standalone brand files ----------------
B = ROOT/'assets'/'brand'; B.mkdir(parents=True, exist_ok=True)
NS = 'xmlns="http://www.w3.org/2000/svg"'
INK, BONE, GLOW = '#0b100d', '#eee9da', '#d6f24a'

# sail mark (sails only): favicon, avatars, embroidery
(B/'sail-mark.svg').write_text(f'<svg {NS} viewBox="-4 -4 108 108" fill="currentColor" role="img" aria-label="Bangarang">{SAILS}</svg>')
# brandmark (sails + wake): tees, stickers, signage
(B/'brandmark.svg').write_text(f'<svg {NS} viewBox="-4 -4 108 149" fill="currentColor" role="img" aria-label="Bangarang">{SAILS}{WAKE_SVG}</svg>')
# wordmark with the sail A
(B/'wordmark.svg').write_text(f'<svg {NS} viewBox="{VB}" role="img" aria-label="Bangarang" style="color:{BONE};--sail:{GLOW}">{body}</svg>')
(ROOT/'assets'/'img'/'wordmark.svg').write_text((B/'wordmark.svg').read_text())
# wordmark with an ordinary A (for use beside the brandmark so the sails aren't repeated)
(B/'wordmark-plain.svg').write_text(f'<svg {NS} viewBox="0 0 {total_p} 712" role="img" aria-label="Bangarang" style="color:{BONE}">{plain}</svg>')
# stacked lockup: brandmark over plain wordmark, one colour
mw = 1500; mh = mw * 149 / 108                       # brandmark box scaled to 1500 units wide
gap = 340; W = total_p; H = round(mh + gap + 712)
mx = (W - mw) / 2
(B/'lockup-stacked.svg').write_text(
    f'<svg {NS} viewBox="0 0 {W} {H}" fill="currentColor" role="img" aria-label="Bangarang" style="color:{BONE}">'
    f'<g transform="translate({mx:.1f},0) scale({mw/108:.5f})"><g transform="translate(4,4)">{SAILS}{WAKE_SVG}</g></g>'
    f'<g transform="translate(0,{round(mh+gap)})">{plain}</g></svg>')

# favicon: sails on an ink square, optically centred
s = 24 / 100
fav = (f'<svg {NS} viewBox="0 0 32 32"><rect width="32" height="32" fill="{INK}"/>'
       f'<g transform="translate(4,4) scale({s})" fill="{GLOW}">{SAILS}</g></svg>')
(ROOT/'favicon.svg').write_text(fav)
print('wordmark units', total, '| lockup', W, H)
