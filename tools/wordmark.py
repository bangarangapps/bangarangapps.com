#!/usr/bin/env python3
"""Generates the Bangarang wordmark assets from Archivo (OFL) outlines + the hand-drawn sail A.
Needs: python venv with fonttools; Archivo[wdth,wght].ttf at $ARCHIVO_TTF.
Outputs (next to this file's parent): assets/img/wordmark.svg, tools/wm-symbol.html, tools/sail-a.html, favicon.svg, tools/metrics.json
"""
import json, os, pathlib
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = pathlib.Path(__file__).resolve().parent.parent
TTF = os.environ.get('ARCHIVO_TTF', '/tmp/bg/fnt/Archivo.ttf')
TR = -14                      # tracking (font units)
CAP = 688

def inst(wd):
    return instantiateVariableFont(TTFont(TTF), {'wght': 900, 'wdth': wd})

# ---- sail A geometry (100x100 box, y down). Left = jib, right = main. Curves run apex -> foot.
LO = [(47,0),(24,22),(3,60),(0,100)];   LI = [(50,0),(40,30),(34,66),(30,100)]
RO = [(53,0),(80,22),(99,56),(100,100)]; RI = [(50,0),(60,30),(67,66),(70,100)]
LCUTS = [(0,.47),(.53,1)];  RCUTS = [(0,.30),(.37,.66),(.73,1)]
BOOM = (28,65,44,7)
def lerp(a,b,t): return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)
def curve(O,I,f): return [lerp(O[i],I[i],f) for i in range(4)]
def fmt(p): return f'{p[0]:.2f} {p[1]:.2f}'
def slice_d(O,I,f0,f1):
    c0, c1 = curve(O,I,f0), curve(O,I,f1)
    return f'M{fmt(c0[0])}C{fmt(c0[1])} {fmt(c0[2])} {fmt(c0[3])}L{fmt(c1[3])}C{fmt(c1[2])} {fmt(c1[1])} {fmt(c1[0])}Z'
def sail_ds(seams=True):
    l = LCUTS if seams else [(0,1)]; r = RCUTS if seams else [(0,1)]
    return [slice_d(LO,LI,a,b) for a,b in l] + [slice_d(RO,RI,a,b) for a,b in r]

def sail_group(x, y, w, h, seams=True):
    paths = ''.join(f'<path d="{d}"/>' for d in sail_ds(seams))
    bx,by,bw,bh = BOOM
    return (f'<g transform="translate({x},{y}) scale({w/100:.5f},{h/100:.5f})" style="fill:var(--sail,currentColor)">'
            f'{paths}<rect x="{bx}" y="{by}" width="{bw}" height="{bh}"/></g>')

# ---- metrics for the live hero (inline-svg width in em at each wdth)
metrics = {}
for wd in (62, 100, 125):
    f = inst(wd); gs = f.getGlyphSet(); cm = f.getBestCmap()
    g = cm[ord('A')]; bp = BoundsPen(gs); gs[g].draw(bp)
    metrics[wd] = {'ink': (bp.bounds[2]-bp.bounds[0])/1000, 'lsb': bp.bounds[0]/1000, 'adv': gs[g].width/1000}
(ROOT/'tools'/'metrics.json').write_text(json.dumps(metrics, indent=1))

# ---- static wordmark @ wdth 100
f = inst(100); gs = f.getGlyphSet(); cm = f.getBestCmap()
seq = ['B','A','N','G','S','R','A','N','G']
x = 0; parts = []
for ch in seq:
    if ch == 'S':
        a = gs[cm[ord('A')]]
        bp = BoundsPen(gs); a.draw(bp)
        w = bp.bounds[2]-bp.bounds[0]
        parts.append(sail_group(round(x+bp.bounds[0],1), 712-CAP-12+12-0, w, CAP))  # top at y=24? see below
        x += a.width + TR
    else:
        g = cm[ord(ch)]; pen = SVGPathPen(gs); gs[g].draw(pen)
        parts.append(f'<path transform="translate({round(x,1)},700) scale(1,-1)" d="{pen.getCommands()}" fill="currentColor"/>')
        x += gs[g].width + TR
total = round(x - TR + 6)
# baseline is y=700, cap top is y=700-688=12; place sail so its bottom sits on the baseline
parts = [p if 'translate(' not in p or 'scale(1,-1)' in p else p for p in parts]
sail_y = 700 - CAP
parts = [p.replace(f',{712-CAP-12+12-0})', f',{sail_y})') if 'var(--sail' in p else p for p in parts]
body = ''.join(parts)
VB = f'0 0 {total} 712'
(ROOT/'tools'/'wm-symbol.html').write_text(f'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><symbol id="wm" viewBox="{VB}">{body}</symbol></svg>')
(ROOT/'tools'/'wm-use.html').write_text(f'<svg viewBox="{VB}" role="img" aria-label="Bangarang"><use href="#wm"/></svg>')
(ROOT/'assets'/'img'/'wordmark.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VB}" style="color:#eee9da;--sail:#d6f24a">{body}</svg>')
# hero/inline sail A (with seams) paths for index.html
(ROOT/'tools'/'sail-a.html').write_text(''.join(f'<path d="{d}"/>' for d in sail_ds()) + f'<rect x="{BOOM[0]}" y="{BOOM[1]}" width="{BOOM[2]}" height="{BOOM[3]}"/>')
# favicon: sail A only, no seams (legible at 16px), glow on ink, square
sx, sw, sh = 3, 26, 26*688/760
ds = ''.join(f'<path d="{d}"/>' for d in sail_ds(False)); bx,by,bw,bh = BOOM
(ROOT/'favicon.svg').write_text(
  f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" fill="#0b100d"/>'
  f'<g transform="translate({sx+0.0},{(32-sh)/2:.2f}) scale({sw/100:.4f},{sh/100:.4f})" fill="#d6f24a">{ds}<rect x="{bx}" y="{by}" width="{bw}" height="{bh}"/></g></svg>')
print(json.dumps(metrics)); print('wordmark width units', total)
