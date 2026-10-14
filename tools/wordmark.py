#!/usr/bin/env python3
"""Generates every Bangarang brand asset from two sources of truth:

  1. the designer's mark: tools/source/mark-original.png --(tools/construct.py)--> tools/mark-path.json
  2. the wordmark typeface's outlines (FONT / WGHT below; currently Gabarito Bold, SIL OFL, vendored in tools/source/fonts)

The mark replaces the middle A of BANGARANG and stands TALLER than the letters (MARK_K x cap height,
hanging MARK_DROP below the baseline). It is never redrawn or stretched: uniform scale only.
The wordmark is rigid everywhere, including the hero: no width axis, no morphing.

Needs a venv with fonttools. The font is read from tools/source/fonts (override with $WORDMARK_FONT).
Writes: assets/brand/*.svg, assets/img/wordmark.svg, favicon.svg,
        tools/wm-symbol.html, wm-use.html (header/footer), tools/hero-d.html, hero-m.html (hero), tools/metrics.json
"""
import json, os, pathlib
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = os.environ.get('WORDMARK_FONT', str(ROOT/'tools'/'source'/'fonts'/'Gabarito[wght].ttf'))
WGHT = int(os.environ.get('WORDMARK_WGHT', '700'))
CAP = 700.0         # cap height in the wordmark box; every font is scaled to this
BASE = 700          # baseline y in the wordmark box
OVERSHOOT = 14      # round-letter overshoot allowance below the baseline
# Two optical cuts. DISPLAY: hero, big uses. SMALL: header, footer, favicon (wider gaps in the mark so its three
# pieces survive at ~16-32 px; looser tracking; more air on the right where the straight stem of the R meets the curve).
CUTS = {
    'display': dict(mark='mark-path.json',       track=0.000, pad_l=0.075, pad_r=0.125),
    'small':   dict(mark='mark-path-small.json', track=0.030, pad_l=0.090, pad_r=0.155),
}
MARK_K = 1.30       # mark height / cap height
MARK_DROP = (MARK_K - 1) / 2   # fraction of cap height the mark hangs below the baseline: equal overhang above and below the letters

# ---------------- the mark (one geometry per cut) ----------------
class Cut:
    def __init__(self, name, c):
        M = json.loads((ROOT/'tools'/c['mark']).read_text())
        self.name = name; x0, y0, x1, y1 = M['bbox']
        self.BW, self.BH = x1 - x0, y1 - y0; self.ASPECT = self.BW / self.BH
        self.path = f'<path transform="translate({-x0:.3f},{-y0:.3f})" d="{M["d"]}"/>'
        self.MH = MARK_K * CAP; self.MW = self.ASPECT * self.MH
        self.tr = c['track'] * CAP; self.pad_l = c['pad_l'] * CAP; self.pad_r = c['pad_r'] * CAP
    def g(self, tx, ty, h, extra=''):
        return f'<g transform="translate({tx:.2f},{ty:.2f}) scale({h/self.BH:.5f})" {extra}>{self.path}</g>'
D = Cut('display', CUTS['display']); S = Cut('small', CUTS['small'])
DROP = MARK_DROP * CAP
MH = D.MH
# kept for older call sites
MARK_PATH, ASPECT, BW, BH, MW = D.path, D.ASPECT, D.BW, D.BH, D.MW
def mark_g(tx, ty, h, extra=''): return D.g(tx, ty, h, extra)

# ---------------- letters ----------------
_f = TTFont(FONT)
if 'fvar' in _f:
    _loc = {}
    for ax in _f['fvar'].axes:
        _loc[ax.axisTag] = max(ax.minValue, min(ax.maxValue, WGHT)) if ax.axisTag == 'wght' else (ax.maxValue if ax.axisTag == 'opsz' else ax.defaultValue)
    _f = instantiateVariableFont(_f, _loc)
gs = _f.getGlyphSet(); cm = _f.getBestCmap()
_bp = BoundsPen(gs); gs[cm[ord('H')]].draw(_bp)
FS = CAP / _bp.bounds[3]                     # font units -> wordmark units (cap height normalised)
def glyph(ch, x, base, hero):
    g = cm[ord(ch)]; pen = SVGPathPen(gs); gs[g].draw(pen)
    return f'<path transform="translate({round(x,1)},{base}) scale({FS:.5f},{-FS:.5f})" d="{pen.getCommands()}" fill="currentColor"/>', gs[g].width * FS

def line(seq, x=0.0, base=BASE, cut=D):
    parts = []
    for ch in seq:
        if ch == 'S':
            ty = base + DROP - cut.MH
            parts.append(cut.g(x + cut.pad_l, ty, cut.MH, 'style="fill:var(--sail,currentColor)"'))
            x += cut.MW + cut.pad_l + cut.pad_r + cut.tr
        else:
            p, w = glyph(ch, x, base, False); parts.append(p); x += w + cut.tr
    return ''.join(parts), x - cut.tr + 6

MARK_TOP = BASE + DROP - MH
MARK_BOT = BASE + DROP
LET_BOT = BASE + OVERSHOOT
VY0 = round(min(0, MARK_TOP) - 6); VY1 = round(max(LET_BOT, MARK_BOT) + 6); VH = VY1 - VY0

def vbox(total): return f'0 {VY0} {total} {VH}'
body_d, tot_d = line('BANGSRANG', cut=D); tot_d = round(tot_d)
body_s, tot_s = line('BANGSRANG', cut=S); tot_s = round(tot_s)
plain, tot_p = line('BANGARANG', cut=D); tot_p = round(tot_p)
VB_D, VB_S = vbox(tot_d), vbox(tot_s)

# header / footer: the SMALL cut, as a shared <symbol>
(ROOT/'tools'/'wm-symbol.html').write_text(f'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><symbol id="wm" viewBox="{VB_S}">{body_s}</symbol></svg>')
# a <use>d symbol sits at the outer viewport's origin, so the outer box starts at 0,0 (the symbol's own viewBox carries the offset)
(ROOT/'tools'/'wm-use.html').write_text(f'<svg viewBox="0 0 {tot_s} {VH}" role="img" aria-label="Bangarang"><use href="#wm"/></svg>')

# hero: the DISPLAY cut, rigid and never animated
(ROOT/'tools'/'hero-d.html').write_text(f'<svg class="hw-d" viewBox="{VB_D}" aria-hidden="true" focusable="false">{body_d}</svg>')
y2 = round(LET_BOT + 44 + MH - DROP)                  # phone line 2 baseline: the mark's head clears line 1 with air
L1, w1 = line('BANG', 0, BASE, D)
L2, w2 = line('SRANG', 0, y2, D)
Wm = round(max(w1, w2)); Hm = round(y2 + max(OVERSHOOT, DROP) + 6)
(ROOT/'tools'/'hero-m.html').write_text(f'<svg class="hw-m" viewBox="0 0 {Wm} {Hm}" aria-hidden="true" focusable="false">{L1}{L2}</svg>')
(ROOT/'tools'/'sail-a.html').write_text(D.path)
(ROOT/'tools'/'metrics.json').write_text(json.dumps({'aspect': D.ASPECT, 'bw': D.BW, 'bh': D.BH, 'vb_h': VH, 'vb_w': tot_s, 'vb_ref': LET_BOT}))

# ---------------- standalone brand files ----------------
B = ROOT/'assets'/'brand'; B.mkdir(parents=True, exist_ok=True)
NS = 'xmlns="http://www.w3.org/2000/svg"'
INK, BONE, GLOW = '#0b100d', '#eee9da', '#d6f24a'
PAD = 14
def mark_svg(c):
    return f'<svg {NS} viewBox="{-PAD} {-PAD} {c.BW+2*PAD:.2f} {c.BH+2*PAD:.2f}" fill="currentColor" role="img" aria-label="Bangarang">{c.path}</svg>'
(B/'mark.svg').write_text(mark_svg(D))
(B/'mark-small.svg').write_text(mark_svg(S))
(B/'wordmark.svg').write_text(f'<svg {NS} viewBox="{VB_D}" role="img" aria-label="Bangarang" style="color:{BONE};--sail:{GLOW}">{body_d}</svg>')
(B/'wordmark-small.svg').write_text(f'<svg {NS} viewBox="{VB_S}" role="img" aria-label="Bangarang" style="color:{BONE};--sail:{GLOW}">{body_s}</svg>')
(ROOT/'assets'/'img'/'wordmark.svg').write_text((B/'wordmark.svg').read_text())
(B/'wordmark-plain.svg').write_text(f'<svg {NS} viewBox="0 0 {tot_p} {LET_BOT}" role="img" aria-label="Bangarang" style="color:{BONE}">{plain}</svg>')
mh = 2000; mw = mh * D.ASPECT; gap = 380; W = tot_p; H = round(mh + gap + LET_BOT)
(B/'lockup-stacked.svg').write_text(
    f'<svg {NS} viewBox="0 0 {W} {H}" fill="currentColor" role="img" aria-label="Bangarang" style="color:{BONE}">'
    f'{D.g((W-mw)/2, 0, mh)}<g transform="translate(0,{round(mh+gap)})">{plain}</g></svg>')
# favicon: the SMALL mark, as large as the tile allows, on an ink square
h = 29; w = h * S.ASPECT
(ROOT/'favicon.svg').write_text(
    f'<svg {NS} viewBox="0 0 32 32"><rect width="32" height="32" fill="{INK}"/>' + S.g((32-w)/2, (32-h)/2, h, 'fill="%s"' % GLOW) + '</svg>')
# apple-touch / large icon: the DISPLAY mark
h = 24; w = h * D.ASPECT
(B/'icon-large.svg').write_text(
    f'<svg {NS} viewBox="0 0 32 32"><rect width="32" height="32" fill="{INK}"/>' + D.g((32-w)/2, 4, h, 'fill="%s"' % GLOW) + '</svg>')
print(f'mark display {D.BW:.0f}x{D.BH:.0f} | small {S.BW:.0f}x{S.BH:.0f} | wordmark vb display {VB_D} small {VB_S} | hero-m {Wm}x{Hm} | lockup {W}x{H}')
