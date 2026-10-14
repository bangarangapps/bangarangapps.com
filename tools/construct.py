#!/usr/bin/env python3
"""Constructs the Bangarang mark as clean vectors from the designer's original raster
(tools/source/mark-original.png) under the design rules the owner set:

  R1  the right-hand edges of the cap and the band lie on ONE straight line, which runs on to the
      swoosh's top-right corner S, where the swoosh's curve begins. (Line = apex A -> corner S.)
  R2  the two gaps (cap|band, band|swoosh) have EXACTLY the same width, constant along their length:
      the band's bottom edge is the swoosh's top edge offset by GAP; the cap's bottom edge is the
      band's top edge offset by GAP.
  R3  flow, proportions and curvature are taken from the original: the master curves are smooth fits
      of the original's arcs, not redrawn by eye.
  R4  smooth, as few points as possible: every piece is its corners + one or two cubics per edge.

Master curves (from the original): E1 swoosh top edge, E2 band top edge, E3 cap left edge,
R swoosh outer curve, Q swoosh inner edge.   Everything else is derived.

Writes tools/mark-path.json {d, w, h, bbox, anchors}.  Needs: pillow numpy scikit-image
"""
import json, math, pathlib, sys
import numpy as np
from PIL import Image
from skimage.measure import find_contours

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT/'source'/'mark-original.png'
GAP = 11.0          # source px: both gaps. (original: 10.9 and 11.3)
SIGMA = 6.0
SCALE = 8
SPAN, CORNER_DEG = 6, 35
VERBOSE = '-q' not in sys.argv

# ======================= geometry helpers =======================
def bez(P, t):
    t = np.atleast_1d(t)[:, None]; m = 1-t
    return m**3*P[0] + 3*m**2*t*P[1] + 3*m*t**2*P[2] + t**3*P[3]
def bez_d(P, t):
    t = np.atleast_1d(t)[:, None]; m = 1-t
    return 3*m**2*(P[1]-P[0]) + 6*m*t*(P[2]-P[1]) + 3*t**2*(P[3]-P[2])
def unit(v): n = np.linalg.norm(v); return v/n if n > 1e-12 else v
def split(P, t):
    a = P[0]+(P[1]-P[0])*t; b = P[1]+(P[2]-P[1])*t; c = P[2]+(P[3]-P[2])*t
    d = a+(b-a)*t; e = b+(c-b)*t; f = d+(e-d)*t
    return np.array([P[0], a, d, f]), np.array([f, e, c, P[3]])
def chain(segs, n=60):
    return np.vstack([bez(P, np.linspace(0, 1, n)) for P in segs])
def poly_len(p): return np.hypot(*np.diff(p, axis=0).T).sum()

# ======================= contours from the original =======================
im = Image.open(SRC).convert('RGBA')
a = np.asarray(im).astype(float)/255
cov = 1 - (a[..., :3]*a[..., 3:4] + (1-a[..., 3:4])).mean(axis=2)
H, W = cov.shape
raw = [np.fliplr(c) - 2 + 0.5 for c in find_contours(np.pad(cov, 2), 0.5)]
raw = [c for c in raw if len(c) > 12 and abs(0.5*np.sum(c[:-1, 0]*c[1:, 1] - c[1:, 0]*c[:-1, 1])) > 20]
def resample(c, step=0.5):
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(c, axis=0).T))]
    t = np.linspace(0, d[-1], max(int(d[-1]/step), 8), endpoint=False)
    return np.c_[np.interp(t, d, c[:, 0]), np.interp(t, d, c[:, 1])]
def circ_smooth(c, w=4):
    k = np.ones(2*w+1)/(2*w+1)
    return np.c_[[np.convolve(np.r_[c[-w:, i], c[:, i], c[:w, i]], k, mode='valid') for i in (0, 1)]].T
def arc_smooth(p, sigma):
    r = int(3*sigma/0.5)+1
    k = np.exp(-0.5*((np.arange(-r, r+1)*0.5)/sigma)**2); k /= k.sum()
    ext = np.vstack([2*p[0]-p[1:r+1][::-1], p, 2*p[-1]-p[-r-1:-1][::-1]])
    return np.c_[np.convolve(ext[:, 0], k, 'valid'), np.convolve(ext[:, 1], k, 'valid')]
cs = [circ_smooth(resample(c)) for c in raw]
cap, band, swoosh = sorted(cs, key=lambda c: c[:, 1].min())      # by top edge: cap, band, swoosh

def nearest(c, p): return int(np.argmin(np.hypot(*(c-p).T)))
def arc(c, p0, p1):                                              # arc of a closed contour from p0 to p1, in contour order
    i, j, n = nearest(c, p0), nearest(c, p1), len(c)
    return c[[(i+k) % n for k in range((j-i) % n+1)]]
def either_arc(c, p0, p1, want):                                  # choose the direction whose midpoint is nearer `want`
    A, B = arc(c, p0, p1), arc(c, p1, p0)[::-1]
    return A if np.hypot(*(A[len(A)//2]-want)) < np.hypot(*(B[len(B)//2]-want)) else B

# corner anchors read off the original (found by the corner detector; see tools/ notes)
A_  = np.array([138.8, 14.4])      # cap apex
S_  = np.array([216.9, 112.6])     # swoosh top-right corner: where its curve begins
T1_ = np.array([98.6, 77.3])       # cap left tip
T2_ = np.array([55.5, 161.0])      # band left tip
T3_ = np.array([25.5, 235.0])      # swoosh left tip
Tt_ = np.array([208.7, 262.2])     # swoosh tail tip

# ======================= R1: the right-hand line =======================
ell_d = unit(S_ - A_)
ell_n = np.array([-ell_d[1], ell_d[0]])
def line_pt(s): return A_ + ell_d*s
ang = math.degrees(math.atan2(ell_d[1], ell_d[0]))

# ======================= master curves: smooth fits of the original arcs =======================
def fit_cubic(p, t_start=None, t_end=None, tol=1.5, max_seg=3):
    """least-squares cubic(s) through an arc with pinned ends; optional fixed end directions."""
    import itertools
    def chord(q): d = np.r_[0, np.cumsum(np.hypot(*np.diff(q, axis=0).T))]; return d/d[-1]
    def gen(q, u, t1, t2):
        P0, P3 = q[0], q[-1]
        A1 = np.outer(3*(1-u)**2*u, t1); A2 = np.outer(3*(1-u)*u**2, t2)
        C = np.array([[np.sum(A1*A1), np.sum(A1*A2)], [np.sum(A1*A2), np.sum(A2*A2)]])
        tmp = q - (np.outer((1-u)**3 + 3*(1-u)**2*u, P0) + np.outer(3*(1-u)*u**2 + u**3, P3))
        X = np.array([np.sum(A1*tmp), np.sum(A2*tmp)]); seg = np.linalg.norm(P3-P0)
        al = np.linalg.solve(C, X) if abs(np.linalg.det(C)) > 1e-12 else (0, 0)
        if al[0] < 1e-6*seg or al[1] < 1e-6*seg: al = (seg/3, seg/3)
        return np.array([P0, P0+t1*al[0], P3+t2*al[1], P3])
    def one(q, t1, t2):
        u = chord(q); P = gen(q, u, t1, t2)
        for _ in range(20):
            d = bez(P, u)-q
            d1 = bez_d(P, u)
            m = 1-u[:, None]; d2 = 6*m*(P[2]-2*P[1]+P[0]) + 6*u[:, None]*(P[3]-2*P[2]+P[1])
            den = np.sum(d1*d1, 1) + np.sum(d*d2, 1)
            u = np.clip(np.where(np.abs(den) > 1e-12, u - np.sum(d*d1, 1)/den, u), 0, 1)
            u[0], u[-1] = 0, 1; u = np.maximum.accumulate(u)
            P = gen(q, u, t1, t2)
        return P, np.hypot(*(bez(P, u)-q).T)
    m = min(10, len(p)-1)
    t1 = unit(p[m]-p[0]) if t_start is None else t_start
    t2 = unit(p[-1-m]-p[-1]) if t_end is None else t_end
    def rec(q, t1, t2, depth):
        P, e = one(q, t1, t2)
        if e.max() < tol or depth >= 3 or len(q) < 8: return [P], e.max()
        k = min(max(int(np.argmax(e)), 3), len(q)-4); tc = unit(q[k-1]-q[k+1])
        l, el = rec(q[:k+1], t1, tc, depth+1); r, er = rec(q[k:], -tc, t2, depth+1)
        return l+r, max(el, er)
    return rec(p, t1, t2, 0)

def sm(c, p0, p1, want):
    return arc_smooth(either_arc(c, p0, p1, want), SIGMA)

# S must sit on the line by definition. P' = where the band's top edge meets the line.
band_top_raw = either_arc(band, T2_, np.array([180.9, 62.6]), np.array([100, 110]))
def cross_line(poly):                                   # first crossing of the poly with the line (signed dist sign change)
    s = (poly-A_)@ell_n
    for i in range(len(poly)-1):
        if s[i]*s[i+1] <= 0:
            f = s[i]/(s[i]-s[i+1]); return poly[i]+f*(poly[i+1]-poly[i])
    return poly[nearest(poly, line_pt(((poly[-1]-A_)@ell_d)))]
# extend slightly past the original corner so the crossing is found
ext = either_arc(band, T2_, np.array([196.0, 76.0]), np.array([100, 110]))
P_ = cross_line(ext)

E1, e1 = fit_cubic(sm(swoosh, T3_, S_, np.array([100, 160])))                      # swoosh top edge T3 -> S
E2, e2 = fit_cubic(arc_smooth(either_arc(band, T2_, P_, np.array([100, 110])), SIGMA))   # band top edge T2 -> P
E3, e3 = fit_cubic(sm(cap, T1_, A_, np.array([115, 45])))                           # cap left edge T1 -> A
Rr, er_ = fit_cubic(sm(swoosh, S_, Tt_, np.array([240, 190])), t_start=ell_d)       # swoosh outer: starts along the line
Qq, eq = fit_cubic(sm(swoosh, Tt_, T3_, np.array([150, 215])), tol=2.6)                      # swoosh inner edge tail -> left tip
# E2's end sits exactly on the line (pinned by construction of P_)

# ======================= R2: offset curves, equal width =======================
def extend(pts, a=0.0, b=0.0):
    """extend a polyline straight along its end tangents by a (start) and b (end)"""
    out = pts
    if a > 0:
        t = unit(pts[0]-pts[3]); out = np.vstack([pts[0]+t*np.linspace(a, 0.5, 40)[:, None], out])
    if b > 0:
        t = unit(pts[-1]-pts[-4]); out = np.vstack([out, pts[-1]+t*np.linspace(0.5, b, 40)[:, None]])
    return out
def offset_poly(segs, d, n=400, a=0.0, b=0.0):
    pts = extend(chain(segs, n), a, b)
    t = np.gradient(pts, axis=0); t = t/np.linalg.norm(t, axis=1)[:, None]
    nrm = np.c_[-t[:, 1], t[:, 0]]
    return pts + nrm*d, nrm

def side_toward(segs, piece):
    """sign of the normal that moves the curve toward the neighbouring piece (the contour it faces)"""
    pts = chain(segs, 60); idx = np.linspace(len(pts)*0.3, len(pts)*0.7, 12).astype(int)
    t = np.gradient(pts, axis=0); t = t/np.linalg.norm(t, axis=1)[:, None]; nrm = np.c_[-t[:, 1], t[:, 0]]
    def near(sign):
        q = pts[idx] + nrm[idx]*sign*GAP
        return np.min(np.hypot(q[:, None, 0]-piece[None, :, 0], q[:, None, 1]-piece[None, :, 1]), axis=1).mean()
    return 1.0 if near(1.0) < near(-1.0) else -1.0

sgn1 = side_toward(E1, band)                            # swoosh top edge -> offset toward the band
band_bottom_pts, _ = offset_poly(E1, sgn1*GAP, a=0, b=45)
sgn2 = side_toward(E2, cap)                             # band top edge -> offset toward the cap
cap_bottom_pts, _ = offset_poly(E2, sgn2*GAP, a=0, b=45)

def refit(poly, tol=0.30):
    """fit the (smooth) offset polyline with as few cubics as the tolerance allows."""
    segs, err = fit_cubic(poly, tol=tol, max_seg=8); return segs, err

# ======================= derived corners =======================
def poly_cross(poly_a, poly_b):                          # first intersection of two polylines
    best = None
    for i in range(len(poly_a)-1):
        p, r = poly_a[i], poly_a[i+1]-poly_a[i]
        d = poly_b[1:]-poly_b[:-1]; q = poly_b[:-1]
        den = r[0]*d[:, 1] - r[1]*d[:, 0]
        with np.errstate(all='ignore'):
            t = ((q[:, 0]-p[0])*d[:, 1] - (q[:, 1]-p[1])*d[:, 0])/den
            u = ((q[:, 0]-p[0])*r[1] - (q[:, 1]-p[1])*r[0])/den
        ok = np.where((t >= 0) & (t <= 1) & (u >= 0) & (u <= 1))[0]
        if len(ok): j = ok[0]; return p+t[j]*r, i, int(j)
    return None, None, None
def line_poly(): return np.array([line_pt(-5), line_pt(np.linalg.norm(S_-A_)+80)])

# B: band bottom (offset of E1) meets the line.  T2: band bottom meets E2.
B_pt, ib, _ = poly_cross(band_bottom_pts, line_poly())
E2pts = extend(chain(E2, 400), 40, 0)
T2_pt, i2, j2 = poly_cross(band_bottom_pts, E2pts)
# C: cap bottom (offset of E2) meets the line.  T1: cap bottom meets E3.
C_pt, ic, _ = poly_cross(cap_bottom_pts, line_poly())
E3pts = extend(chain(E3, 400), 40, 0)
T1_pt, i1, j1 = poly_cross(cap_bottom_pts, E3pts)
assert None not in (B_pt is None and None, ) or True
for nm, v in (('B', B_pt), ('T2', T2_pt), ('C', C_pt), ('T1', T1_pt)):
    assert v is not None, f'corner {nm} not found'

def sub(poly, p0, p1):                                   # polyline portion between two points on it
    i, j = nearest(poly, p0), nearest(poly, p1)
    q = poly[i:j+1] if i <= j else poly[j:i+1][::-1]
    return np.vstack([p0, q[1:-1], p1])

band_bottom_sub = sub(band_bottom_pts, B_pt, T2_pt)
cap_bottom_sub = sub(cap_bottom_pts, C_pt, T1_pt)
bb_segs, bb_err = refit(band_bottom_sub)
cb_segs, cb_err = refit(cap_bottom_sub)

# trim master curves to the derived corners (split at nearest parameter)
def trim(segs, p0, p1):
    pts = chain(segs, 400); tt = np.linspace(0, len(segs), len(pts))
    def par(p): return float(tt[nearest(pts, p)])
    a, b = sorted((par(p0), par(p1)))
    out = []
    for k, P in enumerate(segs):
        lo, hi = max(a-k, 0.0), min(b-k, 1.0)
        if hi <= lo: continue
        Q = P
        if hi < 1.0: Q, _ = split(Q, hi)
        if lo > 0.0: _, Q = split(P if hi >= 1.0 else split(P, hi)[0], lo/hi if hi < 1.0 else lo)
        out.append(Q)
    if par(p0) > par(p1): out = [q[::-1] for q in out[::-1]]
    return out

def snap(segs, p0, p1):
    segs = [s.copy() for s in segs]; segs[0][0] = p0; segs[-1][3] = p1; return segs
def line_seg(p0, p1): return [np.array([p0, p0+(p1-p0)/3, p0+2*(p1-p0)/3, p1])]
def rev(segs): return [s[::-1] for s in segs[::-1]]

# ======================= assemble pieces (closed, corner to corner) =======================
A = A_
# cap:   A --line--> C --cap bottom--> T1 --E3--> A
cap_segs = line_seg(A, C_pt) + snap(cb_segs, C_pt, T1_pt) + snap(trim(E3, T1_pt, A), T1_pt, A)
# band:  P --line--> B --band bottom--> T2 --E2--> P
band_segs = line_seg(P_, B_pt) + snap(bb_segs, B_pt, T2_pt) + snap(trim(E2, T2_pt, P_), T2_pt, P_)
# swoosh: S --R--> Tt --Q--> T3 --E1--> S
sw_segs = snap(Rr, S_, Tt_) + snap(Qq, Tt_, T3_) + snap(E1, T3_, S_)
shapes = [cap_segs, band_segs, sw_segs]

# ======================= output =======================
def dstr(shapes, s):
    out = ''
    for segs in shapes:
        out += f'M{segs[0][0][0]*s:.1f} {segs[0][0][1]*s:.1f}'
        for P in segs: out += f'C{P[1][0]*s:.1f} {P[1][1]*s:.1f} {P[2][0]*s:.1f} {P[2][1]*s:.1f} {P[3][0]*s:.1f} {P[3][1]*s:.1f}'
        out += 'Z'
    return out
d = dstr(shapes, SCALE)
allp = np.vstack([chain(s, 80) for s in shapes])*SCALE
bbox = [float(allp[:, 0].min()), float(allp[:, 1].min()), float(allp[:, 0].max()), float(allp[:, 1].max())]
n_seg = sum(len(s) for s in shapes)
(ROOT/'mark-path.json').write_text(json.dumps({'d': d, 'w': W*SCALE, 'h': H*SCALE, 'bbox': bbox, 'anchors': n_seg,
    'gap': GAP, 'line': [A_.tolist(), S_.tolist()]}))

if VERBOSE:
    def gap_check(p, q):
        dd = np.min(np.hypot(p[:, None, 0]-q[None, :, 0], p[:, None, 1]-q[None, :, 1]), axis=1); return dd
    g1 = gap_check(chain(cb_segs, 200), chain(E2, 400)); g2 = gap_check(chain(bb_segs, 200), chain(E1, 400))
    print(f'right-hand line: {ang:.2f} deg through apex A{tuple(A_.round(1))} and corner S{tuple(S_.round(1))}')
    print('corners (source px): C', C_pt.round(1), 'P', P_.round(1), 'B', B_pt.round(1), 'T1', T1_pt.round(1), 'T2', T2_pt.round(1))
    print(f'master fits: E1 {len(E1)} seg (err {e1:.2f}) | E2 {len(E2)} (err {e2:.2f}) | E3 {len(E3)} (err {e3:.2f}) | R {len(Rr)} (err {er_:.2f}) | Q {len(Qq)} (err {eq:.2f})')
    print(f'offset refits: cap bottom {len(cb_segs)} seg (err {cb_err:.2f}) | band bottom {len(bb_segs)} seg (err {bb_err:.2f})')
    print(f'gap widths (min dist) cap|band {g1.min():.2f}..{g1.max():.2f}   band|swoosh {g2.min():.2f}..{g2.max():.2f}   target {GAP}')
    print(f'pieces 3 | bezier segments {n_seg} (incl. {2} straight) | path {len(d)} chars | mark {(bbox[2]-bbox[0])/SCALE:.0f}x{(bbox[3]-bbox[1])/SCALE:.0f} px')
    # how far the constructed mark sits from the original artwork (it is constructed, so it is allowed to move a little)
    pcs = [chain(s, 120) for s in shapes]
    dev = []
    for c in (cap, band, swoosh):
        dd = np.min(np.hypot(c[:, None, 0]-np.vstack(pcs)[None, :, 0], c[:, None, 1]-np.vstack(pcs)[None, :, 1]), axis=1); dev.append(dd)
    dev = np.concatenate(dev); hgt = (bbox[3]-bbox[1])/SCALE
    print(f'vs original artwork: mean {dev.mean():.2f} px, 95% within {np.percentile(dev,95):.2f} px, max {dev.max():.2f} px of {hgt:.0f} px tall ({100*dev.max()/hgt:.1f}%)')
    # right-hand edge collinearity proof
    pts = {'A': A_, 'C': C_pt, 'P': P_, 'B': B_pt, 'S': S_}
    off = {k: float((v-A_)@ell_n) for k, v in pts.items()}
    print('distance of right-edge corners from the straight line (px):', {k: round(v, 3) for k, v in off.items()})
