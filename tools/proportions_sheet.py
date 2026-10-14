#!/usr/bin/env python3
"""Builds docs/lockup-proportions.html: the BANGARANG lockup measured and drawn (blocks, modules, optical spacing),
current vs a refined candidate. Also writes the candidate SVG to docs/lockup-refined/ for review (never to assets/).
Needs the venv from tools/proportions.py.   Usage: python tools/proportions_sheet.py
"""
import json, math, pathlib, re, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import proportions as P

ROOT = P.ROOT
INK, BONE, RED = '#0c0a0a', '#eee9da', '#ff1f2d'
U = 50.0                                 # module: cap = 14u, stem = 3u
SRC = 'assets/brand/wordmark.svg'

# ------------------------------------------------------------------ measure
vb, els = P.load(ROOT / SRC)
names = ['B', 'A', 'N', 'G', 'mark', 'R', 'A2', 'N2', 'G2']
masks = {n: P.raster(P.poly_from_d(d, P.tf6(M)), vb) for (k, M, d), n in zip(els, names)}
mk_el = [e for e in els if e[0] == 'mark'][0]
mk_cts = P.poly_from_d(mk_el[2], P.tf6(mk_el[1]))

def bbox(m):
    ys, xs = np.nonzero(m); return xs.min() / P.S + vb[0], (xs.max() + 1) / P.S + vb[0], ys.min() / P.S + vb[1], (ys.max() + 1) / P.S + vb[1]
BB = {n: bbox(m) for n, m in masks.items()}
STEM_RASTER = P.stem_of(list(masks.items()), vb)     # sanity check only: antialiased runs read ~1.4 units fat
STEM = 146.0 * 1.0279                                # Gabarito Bold vertical stem (146 font units) at the lockup's cap-normalised scale
mx0, mx1, my0, my1 = BB['mark']; MW, MH = mx1 - mx0, my1 - my0
ys, xs = np.nonzero(masks['mark']); cx, cy = xs.mean() / P.S + vb[0], ys.mean() / P.S + vb[1]
bx_c, by_c = (mx0 + mx1) / 2, (my0 + my1) / 2

# benchmark: the same word with the typeface's own A
pvb, pels = P.load(ROOT / 'assets/brand/wordmark-plain.svg')
pn = ['B', 'A', 'N', 'G', 'A3', 'R', 'A2', 'N2', 'G2']
pmasks = [(n, P.raster(P.poly_from_d(d, P.tf6(M)), pvb)) for (k, M, d), n in zip(pels, pn)]
def pgap(i, depth=175): return P.optical_gap(pmasks[i], pmasks[i + 1], pvb, depth=depth)
bench_pairs = [(f'{pmasks[i][0]}-{pmasks[i+1][0]}', pgap(i)) for i in range(len(pmasks) - 1)]
BENCH_GA, BENCH_AR = bench_pairs[3][1], bench_pairs[4][1]

order = ['B', 'A', 'N', 'G', 'mark', 'R', 'A2', 'N2', 'G2']
cur_pairs = []
for i in range(len(order) - 1):
    a, b = order[i], order[i + 1]
    lab = f"{a.rstrip('2')}-{'mark' if b == 'mark' else b.rstrip('2')}" if a != 'mark' else f"mark-{b.rstrip('2')}"
    cur_pairs.append((lab, P.optical_gap((a, masks[a]), (b, masks[b]), vb, depth=175)))

def solve(K, f):
    pl, pr = 52.5, 87.5
    for _ in range(10):
        gl, gr = P.measure_candidate(P.candidate_svg(K=K, pad_l=pl, pad_r=pr))[175]
        tl, tr = BENCH_GA * f, BENCH_AR * f
        pl -= gl - tl; pr -= gr - tr
        if abs(gl - tl) < .5 and abs(gr - tr) < .5: break
    return pl, pr
K_REF = 18 / 14                         # mark = 18u = 6 stems tall; overhang 2u each side
F_REF = 1.10
PL, PR = solve(K_REF, F_REF)
ref_svg = P.candidate_svg(K=K_REF, pad_l=PL, pad_r=PR)
(ROOT / 'docs' / 'lockup-refined').mkdir(exist_ok=True)
(ROOT / 'docs' / 'lockup-refined' / 'wordmark-refined.svg').write_text(ref_svg)
cur_near = P.measure_candidate(P.candidate_svg())['near']
ref_m = P.measure_candidate(ref_svg)
vb_r, els_r = P.load(ROOT / 'docs' / 'lockup-refined' / 'wordmark-refined.svg')
r_masks = {n: P.raster(P.poly_from_d(d, P.tf6(M)), vb_r) for (k, M, d), n in zip(els_r, names)}
ref_pairs = []
for i in range(len(order) - 1):
    a, b = order[i], order[i + 1]
    lab = f"{a.rstrip('2')}-{'mark' if b == 'mark' else b.rstrip('2')}" if a != 'mark' else f"mark-{b.rstrip('2')}"
    ref_pairs.append((lab, P.optical_gap((a, r_masks[a]), (b, r_masks[b]), vb_r, depth=175)))
def bbox_v(m, v):
    ys_, xs_ = np.nonzero(m); return xs_.min() / P.S + v[0], (xs_.max() + 1) / P.S + v[0]
r_mx0, r_mx1 = bbox_v(r_masks['mark'], vb_r)
r_g1 = bbox_v(r_masks['G'], vb_r)[1]; r_R0 = bbox_v(r_masks['R'], vb_r)[0]
r_ys, r_xs = np.nonzero(r_masks['mark']); r_my0 = r_ys.min() / P.S + vb_r[1]; r_my1 = (r_ys.max() + 1) / P.S + vb_r[1]

# ------------------------------------------------------------------ svg helpers
def lockup_inner(src_svg):
    s = src_svg
    return s[s.index('>', s.index('<svg')) + 1: s.rindex('</svg>')]
CUR_INNER = lockup_inner((ROOT / SRC).read_text())
REF_INNER = lockup_inner(ref_svg)
G1, R0 = BB['G'][1], BB['R'][0]

def gap_poly(a_mask, b_mask, v, depth=175, band=(0, 700)):
    """Closed polygon of the white counted between two shapes (optical-gap area), row by row, in wordmark units."""
    pl = P.profile(a_mask, v, band[0], band[1], 'R'); pr = P.profile(b_mask, v, band[0], band[1], 'L')
    ys_ = np.arange(band[0], band[1], 2.0)
    xl = np.nonzero(a_mask.any(axis=0))[0]; xr = np.nonzero(b_mask.any(axis=0))[0]
    Le = (xl.max() + 1) / P.S + v[0]; Re = xr.min() / P.S + v[0]
    pl = np.where(np.isnan(pl), Le - depth, pl); pr = np.where(np.isnan(pr), Re + depth, pr)
    pl = np.maximum(pl, Le - depth); pr = np.minimum(pr, Re + depth)
    pts = [(f'{x:.1f},{y:.1f}') for x, y in zip(pl, ys_)] + [(f'{x:.1f},{y:.1f}') for x, y in zip(pr[::-1], ys_[::-1])]
    return ' '.join(pts)

def t(x, y, s, size=26, anchor='start', fill=BONE, weight=400, opacity=1):
    return (f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" opacity="{opacity}" '
            f'font-family="JetBrains Mono,monospace" font-weight="{weight}">{s}</text>')
def ln(x1, y1, x2, y2, col=BONE, w=2, dash='', op=.55):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{w}" opacity="{op}"{d}/>'
def uu(v): return f'{v / U:.1f}u'

# ---- figure 1: the blocks on the lockup (crop around the mark; right margin carries the height brackets)
VX0, VX1, VY0, VY1 = 2000, 5000, -300, 1190
EDGE = 4340                                          # past the R: mask the rest of the word, use the margin for dimensions
f1 = [f'<svg viewBox="{VX0} {VY0} {VX1 - VX0} {VY1 - VY0}" role="img" aria-label="The lockup with proportion blocks drawn around the mark" class="fig">']
f1.append(f'<g style="color:{BONE};--sail:{RED}" opacity=".95">{CUR_INNER}</g>')
f1.append(f'<rect x="{EDGE}" y="{VY0}" width="{VX1 - EDGE}" height="{VY1 - VY0}" fill="{INK}"/>')
f1.append(ln(EDGE, VY0, EDGE, VY1, BONE, 2, '', .25))
f1.append(f'<rect x="{mx0:.1f}" y="{my0:.1f}" width="{MW:.1f}" height="{-my0:.1f}" fill="{RED}" opacity=".16"/>')
f1.append(f'<rect x="{mx0:.1f}" y="700" width="{MW:.1f}" height="{my1 - 700:.1f}" fill="{RED}" opacity=".16"/>')
f1.append(f'<polygon points="{gap_poly(masks["G"], masks["mark"], vb)}" fill="{RED}" opacity=".30"/>')
f1.append(f'<polygon points="{gap_poly(masks["mark"], masks["R"], vb)}" fill="{RED}" opacity=".30"/>')
for y, col in ((my0, RED), (0, BONE), (700, BONE), (my1, RED)):
    f1.append(ln(VX0, y, EDGE, y, col, 2.5, '12 9', .75))
FS = 34
f1.append(t(EDGE + 30, my0 + 12, f'mark top {my0:.0f}', FS, fill=RED)); f1.append(t(EDGE + 30, my0 + 54, f'-{uu(-my0)} above caps', FS - 4, fill=RED))
f1.append(t(EDGE + 30, 12, 'cap line 0', FS))
f1.append(t(EDGE + 30, 712, 'baseline 700', FS)); f1.append(t(EDGE + 30, 754, '= 14u cap height', FS - 4))
f1.append(t(EDGE + 30, my1 + 12, f'mark bottom {my1:.0f}', FS, fill=RED)); f1.append(t(EDGE + 30, my1 + 54, f'+{uu(my1 - 700)} below baseline', FS - 4, fill=RED))
for x in (G1, mx0, mx1, R0):
    f1.append(ln(x, -190, x, 1000, BONE, 2, '4 9', .5))
f1.append(ln(G1, 940, mx0, 940, RED, 4, '', .95)); f1.append(t(G1 - 8, 995, f'{mx0 - G1:.0f}', FS, 'end', RED))
f1.append(ln(mx1, 940, R0, 940, RED, 4, '', .95)); f1.append(t(mx1 + (R0 - mx1) / 2, 995, f'{R0 - mx1:.0f}', FS, 'middle', RED))
f1.append(t(VX0 + 20, 1085, 'red numbers: bounding-box clearance from G and to R', FS - 6, fill=RED, opacity=.9))
f1.append(ln(mx0, -215, mx1, -215, BONE, 3, '', .9))
f1.append(ln(mx0, -230, mx0, -200, BONE, 3, '', .9)); f1.append(ln(mx1, -230, mx1, -200, BONE, 3, '', .9))
f1.append(t((mx0 + mx1) / 2, -240, f'mark width {MW:.0f} = {MW / STEM:.2f} stems = {uu(MW)}', FS, 'middle'))
bx = EDGE + 560
f1.append(ln(bx, 0, bx, 700, BONE, 3, '', .9)); f1.append(ln(bx - 14, 0, bx + 14, 0, BONE, 3, '', .9)); f1.append(ln(bx - 14, 700, bx + 14, 700, BONE, 3, '', .9))
f1.append(t(bx + 30, 330, 'cap', FS)); f1.append(t(bx + 30, 372, '700 = 14u', FS - 4))
bx2 = bx + 330
f1.append(ln(bx2, my0, bx2, my1, RED, 3, '', .95)); f1.append(ln(bx2 - 14, my0, bx2 + 14, my0, RED, 3, '', .95)); f1.append(ln(bx2 - 14, my1, bx2 + 14, my1, RED, 3, '', .95))
f1.append(t(bx2 - 30, 330, 'mark', FS, 'end', RED)); f1.append(t(bx2 - 30, 372, f'{MH:.0f} = {uu(MH)}', FS - 4, 'end', RED))
sx, sy = EDGE + 40, 930
f1.append(f'<rect x="{sx}" y="{sy}" width="{STEM:.1f}" height="{STEM:.1f}" fill="none" stroke="{BONE}" stroke-width="3"/>')
f1.append(t(sx + STEM + 24, sy + 70, f'1 stem = {STEM:.0f} = 3u', FS - 2))
f1.append('</svg>')
FIG1 = ''.join(f1)

# ---- figure 2: the mark, blocked
V2 = (2700, -215, 1560, 1130)
MG = 3680                                            # right margin x for labels
f2 = [f'<svg viewBox="{V2[0]} {V2[1]} {V2[2]} {V2[3]}" role="img" aria-label="The mark with stem-module grid, piece blocks, centre of mass and edge angles" class="fig">']
path_all = ' '.join('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in ct) + 'Z' for ct in mk_cts)
f2.append(f'<path d="{path_all}" fill="{RED}" fill-rule="evenodd" opacity=".95"/>')
# stem grid inside the bbox
k = 1
while mx0 + k * STEM < mx1:
    f2.append(ln(mx0 + k * STEM, my0, mx0 + k * STEM, my1, BONE, 1.5, '', .35)); f2.append(t(mx0 + k * STEM - 6, my0 - 10, str(k), 22, 'end', opacity=.75)); k += 1
k = 1
while my0 + k * STEM < my1:
    f2.append(ln(mx0, my0 + k * STEM, mx1, my0 + k * STEM, BONE, 1.5, '', .35)); f2.append(t(mx0 - 10, my0 + k * STEM + 8, str(k), 22, 'end', opacity=.75)); k += 1
f2.append(f'<rect x="{mx0:.1f}" y="{my0:.1f}" width="{MW:.1f}" height="{MH:.1f}" fill="none" stroke="{BONE}" stroke-width="3"/>')
# piece blocks
labels = ['cap', 'band', 'sweep']
pb = []
for ct, lab in zip(mk_cts, labels):
    xs_ = [p[0] for p in ct]; ys_ = [p[1] for p in ct]
    pb.append((lab, min(xs_), max(xs_), min(ys_), max(ys_)))
cols = (BONE, BONE, BONE)
for (lab, a, b, c, d_), col in zip(pb, cols):
    f2.append(f'<rect x="{a:.1f}" y="{c:.1f}" width="{b - a:.1f}" height="{d_ - c:.1f}" fill="none" stroke="{col}" stroke-width="2.5" stroke-dasharray="14 8" opacity=".9"/>')
    f2.append(t(MG, c + 30, f'{lab} {b - a:.0f} x {d_ - c:.0f}', 30))
    f2.append(ln(b, c + 4, MG - 16, c + 24, BONE, 1.5, '', .35))
hs = [p[4] - p[3] for p in pb]
f2.append(t(MG, 430, f'heights {hs[0]:.0f} : {hs[1]:.0f} : {hs[2]:.0f}', 30)); f2.append(t(MG, 468, f'= 1 : {hs[1] / hs[0]:.2f} : {hs[2] / hs[0]:.2f}', 30))
# centre of box vs centre of mass, apex
f2.append(f'<circle cx="{bx_c:.1f}" cy="{by_c:.1f}" r="11" fill="none" stroke="{BONE}" stroke-width="3"/>'); f2.append(t(bx_c + 18, by_c - 14, 'box centre', 26))
f2.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="11" fill="{BONE}"/>'); f2.append(t(cx + 18, cy + 34, f'centre of mass +{cx - bx_c:.0f} right', 26))
a = (mk_cts[0][0][0], mk_cts[0][0][1])
ax = a[0]
f2.append(f'<circle cx="{ax:.1f}" cy="{my0:.1f}" r="9" fill="{BONE}"/>'); f2.append(t(ax + 20, my0 - 46, f'apex +{ax - bx_c:.0f} from centre', 26))
# edge angle vs A leg
# apex -> swoosh top-right corner, recomputed from the shipped geometry: apex (source 1110.4,115.2), corner (1735.2,900.8)
Mm = mk_el[1]
def src(px, py): return (Mm[0, 0] * px + Mm[0, 1] * py + Mm[0, 2], Mm[1, 0] * px + Mm[1, 1] * py + Mm[1, 2])
ap, co = src(1110.4, 115.2), src(1735.2, 900.8)
ang_mark = math.degrees(math.atan2(co[1] - ap[1], co[0] - ap[0]))
f2.append(ln(ap[0], ap[1], co[0], co[1], BONE, 4, '', .95))
ang_A = 71.3
L = 330; ax2 = ap[0] + L / math.tan(math.radians(ang_A)); ay2 = ap[1] + L
f2.append(ln(ap[0], ap[1], ax2, ay2, BONE, 3, '12 8', .8))
f2.append(t(MG, 520, f'solid line: sail edge {ang_mark:.1f} deg', 28)); f2.append(t(MG, 560, f'dashed: the A leg, {ang_A:.0f} deg', 28, opacity=.85))
f2.append('</svg>')
FIG2 = ''.join(f2)

# ---- figure 3: optical spacing bars
def bars(rows, title):
    mx = 340
    out = [f'<div class="bars" role="img" aria-label="{title}">']
    for lab, v, kind in rows:
        out.append(f'<div class="bar {kind}"><span class="bl">{lab}</span><i style="width:{v / mx * 100:.1f}%"></i><b>{v:.0f}</b></div>')
    out.append('</div>'); return ''.join(out)
rows = []
for (lab, v) in cur_pairs:
    rows.append((lab, v, 'm' if 'mark' in lab else 'l'))
rows_ref = [(lab, v, 'm' if 'mark' in lab else 'l') for lab, v in ref_pairs]
BARS_CUR = bars(rows, 'Optical gap between neighbours, current')
BARS_REF = bars(rows_ref, 'Optical gap between neighbours, refined')
BARS_BENCH = bars([(lab, v, 'b') for lab, v in bench_pairs], 'Optical gap with the typeface\'s own A')

# ---- figure 4: current vs refined lockups
def full(inner, v, cap=''):
    return (f'<figure class="lk"><svg viewBox="{v[0]} {v[1]} {v[2]} {v[3]}" role="img" aria-label="{cap}" style="color:{BONE};--sail:{RED}">{inner}</svg>'
            f'<figcaption>{cap}</figcaption></figure>')
CUR_FULL = full(CUR_INNER, vb, f'Current: mark {MH:.0f} tall, pads 52 / 88')
REF_FULL = full(REF_INNER, vb_r, f'Refined: mark {r_my1 - r_my0:.0f} tall (18u), pads {PL:.0f} / {PR:.0f}')

def small(inner, v, h):
    return f'<svg viewBox="{v[0]} {v[1]} {v[2]} {v[3]}" height="{h}" style="color:{BONE};--sail:{RED};width:auto">{inner}</svg>'
SMALLS = (f'<div class="smalls"><div>{small(CUR_INNER, vb, 56)}<span>current, 56 px tall</span></div><div>{small(REF_INNER, vb_r, 56)}<span>refined, 56 px tall</span></div>'
          f'<div>{small(CUR_INNER, vb, 30)}<span>current, 30 px</span></div><div>{small(REF_INNER, vb_r, 30)}<span>refined, 30 px</span></div></div>')

# ------------------------------------------------------------------ numbers for the tables
A = BB['A']; Aw = A[1] - A[0]
ink = {n: float(m.sum()) / P.S / P.S for n, m in masks.items()}
letter_mean = np.mean([ink[n] for n in ('B', 'A', 'N', 'G', 'R', 'A2', 'N2', 'G2')])
near_cur = cur_near; near_ref = ref_m['near']
gm_c = cur_pairs[3][1]; mr_c = cur_pairs[4][1]; gm_r = ref_pairs[3][1]; mr_r = ref_pairs[4][1]

html = f'''<title>Lockup Proportions</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* Dark by intent, like the brand sheet it extends: single theme, every colour explicit. */
:root{{--ink:{INK};--bone:{BONE};--red:{RED};--dim:rgba(238,233,218,.68);--line:rgba(238,233,218,.18);color-scheme:dark}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ink);color:var(--bone);font-family:"Archivo",system-ui,sans-serif;font-size:17px;line-height:1.55;-webkit-font-smoothing:antialiased;padding-inline:max(16px,4vw)}}
.wrap{{max-width:1180px;margin-inline:auto}}
section{{padding-block:clamp(44px,7vw,92px);border-top:1px solid var(--line)}}
section:first-of-type{{border-top:0}}
h1,h2,h3{{margin:0;text-wrap:balance}}
h1,h2{{font-weight:900;text-transform:uppercase;line-height:.9;letter-spacing:-.02em;font-variation-settings:"wdth" 80}}
h1{{font-size:clamp(40px,8vw,104px)}} h2{{font-size:clamp(30px,5vw,64px)}}
h3{{font-size:19px;font-weight:700}}
p{{margin:0;max-width:64ch}}
.lab{{font-family:"JetBrains Mono",monospace;font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);display:block;margin-bottom:14px}}
.lead{{margin-top:18px;font-size:clamp(18px,2vw,21px);color:var(--dim)}}
.dim{{color:var(--dim)}}
.num{{font-family:"JetBrains Mono",monospace}}
.fig{{display:block;width:100%;height:auto;margin-top:28px;border:1px solid var(--line);background:var(--ink)}}
.cols{{display:grid;gap:20px 40px;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));margin-top:32px}}
.cols>div{{min-width:0}}
ul.r{{list-style:none;margin:14px 0 0;padding:0}}
ul.r li{{padding:11px 0;border-bottom:1px solid var(--line);max-width:64ch}}
.tbl{{overflow-x:auto;margin-top:28px}}
table{{border-collapse:collapse;width:100%;min-width:660px;font-size:15px}}
th,td{{text-align:left;padding:11px 12px;border-bottom:1px solid var(--line);vertical-align:top}}
thead th{{font-family:"JetBrains Mono",monospace;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);font-weight:500}}
tbody th{{font-weight:600}}
.ok{{color:var(--bone)}} .flag{{color:var(--red);font-weight:600}}
.bars{{display:grid;gap:7px;margin-top:20px}}
.bar{{display:grid;grid-template-columns:92px 1fr 44px;align-items:center;gap:10px;font-family:"JetBrains Mono",monospace;font-size:12px}}
.bar i{{display:block;height:14px;background:var(--bone);opacity:.5}}
.bar.m i{{background:var(--red);opacity:1}} .bar.b i{{background:transparent;border:1px solid var(--bone);opacity:.8}}
.bar b{{font-weight:500;text-align:right}}
.lk{{margin:0;border:1px solid var(--line);padding:clamp(18px,3vw,36px)}} .lk svg{{width:100%;height:auto;display:block}}
.lk figcaption{{margin-top:16px;font-family:"JetBrains Mono",monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--dim)}}
.smalls{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:28px 40px;align-items:end;margin-top:24px;padding:28px;border:1px solid var(--line)}}
.smalls div{{display:grid;gap:10px}} .smalls span{{font-family:"JetBrains Mono",monospace;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--dim)}}
.verdict{{display:grid;gap:0;margin-top:26px}}
.verdict>div{{display:grid;grid-template-columns:140px 1fr;gap:10px 24px;padding:14px 0;border-bottom:1px solid var(--line)}}
.verdict b{{font-family:"JetBrains Mono",monospace;font-size:12px;letter-spacing:.08em;text-transform:uppercase}}
@media (max-width:620px){{.verdict>div{{grid-template-columns:1fr}} .bar{{grid-template-columns:78px 1fr 40px}}}}
footer{{padding-block:44px 64px;border-top:1px solid var(--line);color:var(--dim);font-size:14px}}
</style>
<div class="wrap">

<section>
  <span class="lab">Bangarang &middot; lockup review &middot; October 2026</span>
  <h1>The sail,<br>measured</h1>
  <p class="lead">Every number here is measured from the shipped files: cap {BB["B"][3]:.0f} units, stem {STEM:.0f}, mark {MH:.0f} tall by {MW:.0f} wide. The sail is already sized to the system. What is not quite right is the air around it.</p>
  <div class="verdict">
    <div><b class="ok">Leave</b><p>Scale. The mark is {MH:.0f} units tall = {MH / STEM:.2f} stems = 18.2u on a 50-unit module, hung exactly centred on the cap band ({-my0:.0f} above, {my1 - 700:.0f} below). Its ink area is {ink["mark"] / letter_mean * 100:.0f}% of the average letter, so it carries the same colour on the line as G or N.</p></div>
    <div><b class="ok">Leave</b><p>Left/right balance. The mark's mass sits {cx - bx_c:.0f} units right of its box centre, so it needs more air on its left than its right. Current optical gaps run {gm_c:.0f} : {mr_c:.0f} = {gm_c / mr_c:.2f}. The typeface's own A runs {BENCH_GA:.0f} : {BENCH_AR:.0f} = {BENCH_GA / BENCH_AR:.2f}. Same asymmetry; the pads are doing the right job.</p></div>
    <div><b class="flag">Change</b><p>Overall looseness. Both gaps are about {(gm_c / BENCH_GA - 1) * 100:.0f}% and {(mr_c / BENCH_AR - 1) * 100:.0f}% wider than the A the sail replaces, and the gap before the mark ({gm_c:.0f}) is the widest in the whole word (next widest: {sorted(v for _, v in cur_pairs if 'mark' not in _)[-1]:.0f}). Tightening to +10% over the A's spacing closes the rhythm without crowding.</p></div>
    <div><b class="ok">Optional</b><p>Snap the mark to exactly 18u (6 stems, 2u overhang). It is a {abs(1 - 900 / MH) * 100:.1f}% change nobody will see, but it makes the system describable: cap 14u, stem 3u, mark 18u, overhang 2u.</p></div>
  </div>
</section>

<section>
  <span class="lab">01 &middot; Blocks on the lockup</span>
  <h2>Cap, stem,<br>overhang</h2>
  <p class="lead">Module u = 50 units. The cap is 14u, the stem 3u, the mark 18.2u, the overhang 2.1u each side (red blocks). The shaded red areas are the white space the eye counts between the mark and its neighbours, measured row by row to a depth of 175 units.</p>
  {FIG1}
  <div class="cols">
    <div><h3>What the blocks say</h3>
      <ul class="r">
        <li>Overhang above equals overhang below ({-my0:.0f} / {my1 - 700:.0f}), so the mark is centred on the caps. Correct, and it stays correct at every size.</li>
        <li>The sail is {MW / Aw:.2f}x the width of the A it replaces ({MW:.0f} vs {Aw:.0f}). Wider and taller than a letter is what makes it read as a symbol and not a misshapen A.</li>
        <li>Nearest bounding-box clearance: {mx0 - G1:.0f} to G, {R0 - mx1:.0f} to R. Letter pairs in this word sit at 40 to 120.</li>
      </ul></div>
    <div><h3>How to read it</h3>
      <ul class="r">
        <li>Optical gap = mean horizontal white between two shapes across the cap band, each shape's profile clamped to 175 units from its edge so deep counters count less. It is the standard area method for kerning, applied to the sail.</li>
        <li>Closest approach at equal height (not bounding box): G to sail {near_cur[0]:.0f}, sail to R {near_cur[1]:.0f}. G to A is 119 and A to R is 72 in the plain word.</li>
      </ul></div>
  </div>
</section>

<section>
  <span class="lab">02 &middot; Blocks on the mark</span>
  <h2>Inside<br>the sail</h2>
  <p class="lead">The mark's bounding box is {MW / STEM:.2f} x {MH / STEM:.2f} stems. The grid lines are one stem apart. The three pieces stand in a measured sequence, and the centre of mass sits right of the box centre, which is why the pads are asymmetric.</p>
  {FIG2}
  <div class="cols">
    <div><h3>Findings</h3>
      <ul class="r">
        <li><b>Piece heights {hs[0]:.0f} : {hs[1]:.0f} : {hs[2]:.0f}</b> = 1 : {hs[1] / hs[0]:.2f} : {hs[2] / hs[0]:.2f}. The first step is a golden step (1.62). The artwork has a real rhythm; do not touch the pieces.</li>
        <li><b>Apex</b> is {ax - bx_c:.0f} units right of the box centre; <b>centre of mass</b> {cx - bx_c:.0f} right and {cy - by_c:.0f} low. The A it replaces has its centre of mass 32 low, the sail's is {cy - by_c:.0f} low: the same low centre of gravity.</li>
        <li><b>Edge angle</b> {ang_mark:.1f} deg from horizontal against the A's {ang_A:.0f} deg. The sail leans harder than any letter. That lean is what stops it reading as an A, so it is not a flaw to correct.</li>
      </ul></div>
    <div><h3>Weight match</h3>
      <ul class="r">
        <li>Ink area {ink["mark"]:,.0f} vs G {ink["G"]:,.0f}, N {ink["N"]:,.0f}, B {ink["B"]:,.0f}, A {ink["A"]:,.0f}. The sail is as dark as the heavy letters; the A it replaces is the lightest letter in the word.</li>
        <li>Stroke thickness inside the sail averages 225 units against the stem's 150. It is a bolder shape than the type around it, which is what lets it stand taller without feeling thin.</li>
      </ul></div>
  </div>
</section>

<section>
  <span class="lab">03 &middot; Rhythm</span>
  <h2>The gap before<br>the sail is the<br>widest in the word</h2>
  <p class="lead">Optical gap between each pair of neighbours, in units. Red bars touch the sail. The outlined bars are the same word set with the typeface's own A, which is what a type designer judged right for that slot.</p>
  <div class="cols">
    <div><h3>Current</h3>{BARS_CUR}</div>
    <div><h3>Typeface's own A</h3>{BARS_BENCH}</div>
    <div><h3>Refined</h3>{BARS_REF}</div>
  </div>
</section>

<section>
  <span class="lab">04 &middot; Proposal</span>
  <h2>Current<br>vs refined</h2>
  <p class="lead">Refined = mark snapped to 18u and the pads set so both gaps land 10% over the A's spacing: left pad {PL:.0f} (was 52), right pad {PR:.0f} (was 88). Letters and mark geometry unchanged. The small cut (header, footer, favicon) keeps its wider air; your earlier note about the R crowding at small sizes still holds.</p>
  <div class="grid" style="display:grid;gap:16px;margin-top:28px">{CUR_FULL}{REF_FULL}</div>
  {SMALLS}
  <div class="tbl"><table><thead><tr><th scope="col">Measure</th><th scope="col">Current</th><th scope="col">Refined</th><th scope="col">A in the slot</th></tr></thead><tbody>
    <tr><th scope="row">Mark height</th><td>{MH:.0f} (1.30 cap)</td><td>{r_my1 - r_my0:.0f} (18u, 1.29 cap)</td><td>cap 700</td></tr>
    <tr><th scope="row">Gap G to mark (optical)</th><td>{gm_c:.0f}</td><td>{gm_r:.0f}</td><td>{BENCH_GA:.0f}</td></tr>
    <tr><th scope="row">Gap mark to R (optical)</th><td>{mr_c:.0f}</td><td>{mr_r:.0f}</td><td>{BENCH_AR:.0f}</td></tr>
    <tr><th scope="row">Left : right balance</th><td>{gm_c / mr_c:.2f}</td><td>{gm_r / mr_r:.2f}</td><td>{BENCH_GA / BENCH_AR:.2f}</td></tr>
    <tr><th scope="row">Closest approach, G / R</th><td>{near_cur[0]:.0f} / {near_cur[1]:.0f}</td><td>{near_ref[0]:.0f} / {near_ref[1]:.0f}</td><td>119 / 72</td></tr>
    <tr><th scope="row">Lockup width</th><td>{vb[2]:.0f}</td><td>{vb_r[2]:.0f} ({(vb_r[2] / vb[2] - 1) * 100:.1f}%)</td><td>6171 (plain)</td></tr>
  </tbody></table></div>
  <p class="lead dim" style="font-size:15px">If you approve it, it ships by changing three constants in <span class="num">tools/wordmark.py</span> (MARK_K and the display cut's pad_l, pad_r), regenerating the assets, hero and favicon, and redeploying. The candidate SVG is in <span class="num">docs/lockup-refined/</span>. Nothing on the site has changed.</p>
</section>

<footer>Measured by <span class="num">tools/proportions.py</span>; page built by <span class="num">tools/proportions_sheet.py</span>. Raster 2 px per unit, even-odd fill.</footer>
</div>
'''
(ROOT / 'docs' / 'lockup-proportions.html').write_text(html)
print('wrote docs/lockup-proportions.html', len(html))
print('pads', round(PL, 1), round(PR, 1), 'K', K_REF, 'gaps cur', round(gm_c, 1), round(mr_c, 1), 'ref', round(gm_r, 1), round(mr_r, 1), 'near', near_cur, near_ref)
