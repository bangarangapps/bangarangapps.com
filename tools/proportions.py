#!/usr/bin/env python3
"""Measures the BANGARANG lockup: rasterises every element of assets/brand/wordmark.svg (or a candidate geometry) and reports
cap/stem metrics, mark size relative to the letters, optical (area-based) spacing around the mark, and ink color/weight.

Needs a venv with: fonttools numpy pillow svg.path.   Usage: python tools/proportions.py [--json out.json]
"""
import json, math, pathlib, re, sys
import numpy as np
from PIL import Image, ImageDraw
from svg.path import parse_path

ROOT = pathlib.Path(__file__).resolve().parent.parent
S = 2.0            # raster scale: pixels per wordmark unit

def poly_from_d(d, tf):
    """Flatten an SVG path to contours (lists of (x,y)) in wordmark units. tf = (a,b,c,d,e,f) 2D affine."""
    a, b, c, dd, e, f = tf
    contours, cur = [], []
    for seg in parse_path(d):
        n = 1 if seg.__class__.__name__ in ('Line', 'Close') else 24
        if not cur or abs(seg.start - cur[-1]) > 1e-6 and seg.__class__.__name__ == 'Move':
            pass
        if seg.__class__.__name__ == 'Move':
            if cur: contours.append(cur)
            cur = [seg.end]; continue
        if not cur: cur = [seg.start]
        for i in range(1, n + 1): cur.append(seg.point(i / n))
        if seg.__class__.__name__ == 'Close':
            contours.append(cur); cur = []
    if cur: contours.append(cur)
    out = []
    for ct in contours:
        out.append([(a * p.real + c * p.imag + e, b * p.real + dd * p.imag + f) for p in ct])
    return out

def parse_transform(t):
    m = np.eye(3)
    for name, args in re.findall(r'(translate|scale)\(([^)]*)\)', t or ''):
        v = [float(x) for x in args.replace(',', ' ').split()]
        if name == 'translate': M = np.array([[1, 0, v[0]], [0, 1, v[1] if len(v) > 1 else 0], [0, 0, 1]])
        else: M = np.array([[v[0], 0, 0], [0, v[1] if len(v) > 1 else v[0], 0], [0, 0, 1]])
        m = m @ M
    return m

def tf6(m): return (m[0, 0], m[1, 0], m[0, 1], m[1, 1], m[0, 2], m[1, 2])

def load(svg_path):
    s = pathlib.Path(svg_path).read_text()
    vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
    els = []
    for m in re.finditer(r'<g transform="([^"]+)"[^>]*>\s*<path transform="([^"]+)" d="([^"]+)"/>\s*</g>|<path transform="([^"]+)" d="([^"]+)"', s):
        if m.group(1):
            M = parse_transform(m.group(1)) @ parse_transform(m.group(2)); els.append(('mark', M, m.group(3)))
        else:
            els.append(('glyph', parse_transform(m.group(4)), m.group(5)))
    return vb, els

def raster(contours, vb):
    W, H = int(vb[2] * S) + 2, int(vb[3] * S) + 2
    acc = np.zeros((H, W), dtype=bool)
    for ct in contours:
        im = Image.new('1', (W, H), 0)
        ImageDraw.Draw(im).polygon([((x - vb[0]) * S, (y - vb[1]) * S) for x, y in ct], fill=1)
        acc ^= np.array(im, dtype=bool)          # even-odd, so counters stay open
    return acc

def analyse(svg='assets/brand/wordmark.svg', label='current'):
    vb, els = load(ROOT / svg)
    names = ['B', 'A', 'N', 'G', 'R', 'A2', 'N2', 'G2']   # BANG [mark] RANG, in drawing order
    res = {'label': label, 'viewBox': vb, 'elements': []}
    masks = []
    gi = 0
    for kind, M, d in els:
        cts = poly_from_d(d, tf6(M))
        mask = raster(cts, vb)
        ys, xs = np.nonzero(mask)
        x0, x1 = xs.min() / S + vb[0], (xs.max() + 1) / S + vb[0]
        y0, y1 = ys.min() / S + vb[1], (ys.max() + 1) / S + vb[1]
        name = 'mark' if kind == 'mark' else names[gi]
        if kind == 'glyph': gi += 1
        masks.append((name, mask))
        res['elements'].append(dict(name=name, x0=x0, x1=x1, y0=y0, y1=y1, w=x1 - x0, h=y1 - y0,
                                    area=float(mask.sum()) / S / S, cx=float(xs.mean()) / S + vb[0], cy=float(ys.mean()) / S + vb[1]))
    E = res['elements']
    res['_masks'] = masks
    return res, vb

def stem_of(masks, vb, letter='N', y_lo=300, y_hi=400):
    m = dict(masks)[letter]; runs = []
    for y in np.arange(y_lo, y_hi, 3):
        row = m[int((y - vb[1]) * S)]; d = np.diff(np.concatenate(([0], row.view(np.int8), [0])))
        st, en = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
        runs += list((en - st) / S)
    return float(np.median([r for r in runs if r > 40]))

def profile(mask, vb, y_lo, y_hi, side):
    """Per-row outermost ink x (in units) over cap band rows; NaN where the row is empty."""
    out = []
    for y in np.arange(y_lo, y_hi, 2):
        row = mask[int((y - vb[1]) * S)]; xs = np.nonzero(row)[0]
        out.append(np.nan if xs.size == 0 else ((xs.max() + 1) if side == 'R' else xs.min()) / S + vb[0])
    return np.array(out)

def optical_gap(left, right, vb, band=(0, 700), depth=None):
    """Mean row-wise white between two shapes inside the band, with each shape's profile clamped to `depth` units from its
    own extreme edge (so a deep counter or open A-foot counts only partly). Rows with no ink count as the clamp."""
    ml, mr = left[1], right[1]
    ysl = np.nonzero(ml.any(axis=1))[0]; xl = np.nonzero(ml.any(axis=0))[0]; xr = np.nonzero(mr.any(axis=0))[0]
    L_edge = (xl.max() + 1) / S + vb[0]; R_edge = xr.min() / S + vb[0]
    pl = profile(ml, vb, band[0], band[1], 'R'); pr = profile(mr, vb, band[0], band[1], 'L')
    pl = np.where(np.isnan(pl), L_edge - depth, pl); pr = np.where(np.isnan(pr), R_edge + depth, pr)
    pl = np.maximum(pl, L_edge - depth); pr = np.minimum(pr, R_edge + depth)
    return float(np.mean(pr - pl))

if __name__ == '__main__':
    res, vb = analyse()
    masks = res.pop('_masks')
    stem = stem_of(masks, vb)
    print('stem', round(stem, 1))
    for e in res['elements']:
        print({k: (round(v, 1) if isinstance(v, float) else v) for k, v in e.items()})
    order = [n for n, _ in masks]
    for depth in (120, 175, 250):
        print('depth', depth, [(f'{order[i]}{order[i+1]}', round(optical_gap(masks[i], masks[i+1], vb, depth=depth), 1)) for i in range(len(masks) - 1)])


# ---------------------------------------------------------------- candidates
CAP, BASE = 700.0, 700.0

def candidate_svg(src='assets/brand/wordmark.svg', K=1.30, pad_l=52.5, pad_r=87.5):
    """Re-lay the lockup with a different mark scale / pads, from the shipped geometry. Letters never change."""
    s = (ROOT / src).read_text()
    vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
    m = re.search(r'<g transform="translate\(([\d.\-]+),([\d.\-]+)\) scale\(([\d.]+)\)"([^>]*)>(<path[^>]*/>)</g>', s)
    tx, ty, k0, extra, mpath = m.group(1), m.group(2), float(m.group(3)), m.group(4), m.group(5)
    tx, ty = float(tx), float(ty)
    M0 = json.loads((ROOT / 'tools/mark-path.json').read_text()); bx0, by0, bx1, by1 = M0['bbox']
    BH, BW = by1 - by0, bx1 - bx0
    MH0 = BH * k0; MW0 = BW * k0
    MH = K * CAP; k = MH / BH; MW = BW * k
    drop = (K - 1) / 2 * CAP
    ty_new = BASE + drop - MH
    shift = (MW - MW0) + (pad_l - 52.5) + (pad_r - 87.5)   # glyphs after the mark move by this
    tx_new = tx + (pad_l - 52.5)
    new_g = f'<g transform="translate({tx_new:.2f},{ty_new:.2f}) scale({k:.5f})"{extra}>{mpath}</g>'
    out = s.replace(m.group(0), '@@MARK@@')
    head, tail = out.split('@@MARK@@')
    def shift_after(t):
        return re.sub(r'translate\(([\d.]+),(700)\)', lambda mm: f'translate({float(mm.group(1)) + shift:.1f},700)', t)
    tail = shift_after(tail)
    VY0 = round(min(0, -drop) - 6); VY1 = round(max(714, BASE + drop) + 6)
    W = round(vb[2] + shift)
    res = head + new_g + tail
    res = re.sub(r'viewBox="[^"]+"', f'viewBox="0 {VY0} {W} {VY1 - VY0}"', res, count=1)
    return res

def measure_candidate(svg_text, tmp='/tmp/_cand.svg'):
    pathlib.Path(tmp).write_text(svg_text)
    vb, els = load(tmp)
    names = ['B', 'A', 'N', 'G', 'mark', 'R', 'A2', 'N2', 'G2']
    masks = [(n, raster(poly_from_d(d, tf6(M)), vb)) for (k_, M, d), n in zip(els, names)]
    idx = {n: i for i, (n, _) in enumerate(masks)}
    out = {}
    for depth in (120, 175, 250):
        out[depth] = (optical_gap(masks[idx['G']], masks[idx['mark']], vb, depth=depth),
                      optical_gap(masks[idx['mark']], masks[idx['R']], vb, depth=depth))
    # closest approach (nearest ink-to-ink, any row in the cap band)
    def near(a, b):
        pa = profile(masks[idx[a]][1], vb, 0, 700, 'R'); pb = profile(masks[idx[b]][1], vb, 0, 700, 'L')
        return float(np.nanmin(pb - pa))
    out['near'] = (near('G', 'mark'), near('mark', 'R'))
    return out
