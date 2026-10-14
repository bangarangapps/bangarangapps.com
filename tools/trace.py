#!/usr/bin/env python3
"""Vectorise the brand mark from the designer's original raster (tools/source/mark-original.png).

Method (no redrawing, no eyeballing):
  1. ink coverage (alpha composited on white), 0..1
  2. marching squares at coverage 0.5 -> sub-pixel contours straight from the original pixels
  3. corner detection (apexes / clews stay sharp)
  4. Schneider least-squares cubic Bezier fit between corners, tolerance TOL px
  5. verification: rasterise the result at the original size and report error vs the source

Writes tools/mark-path.json {d, w, h}  (path in original pixel units, y down) and prints the error report.
Needs: pillow numpy scikit-image
"""
import json, pathlib, math
import numpy as np
from PIL import Image, ImageDraw
from skimage.measure import find_contours

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT/'source'/'mark-original.png'
TOL = 0.30            # max fit error vs the sub-pixel contour, in source pixels
CORNER_DEG = 48       # turning angle that counts as a real corner
CORNER_SPAN = 4       # points either side used to measure the turn

im = Image.open(SRC).convert('RGBA')
a = np.asarray(im).astype(float)/255
cov = 1 - (a[..., :3]*a[..., 3:4] + (1-a[..., 3:4])).mean(axis=2)
H, W = cov.shape
pad = np.pad(cov, 2)                                   # keep contours closed at the frame edge

# ---------- 1/2: contours ----------
raw = [np.fliplr(c) - 2 + 0.5 for c in find_contours(pad, 0.5)]   # (x,y), pixel-centre -> pixel-edge coords
raw = [c for c in raw if len(c) > 12 and abs(poly_area := 0.5*np.sum(c[:-1,0]*c[1:,1]-c[1:,0]*c[:-1,1])) > 20]

def resample(c, step=0.5):
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(c, axis=0).T))]
    n = max(int(d[-1]/step), 8)
    t = np.linspace(0, d[-1], n, endpoint=False)
    return np.c_[np.interp(t, d, c[:, 0]), np.interp(t, d, c[:, 1])]

def smooth(c, w=3):                                    # tiny circular moving average: removes alpha-quantisation jitter only
    k = np.ones(2*w+1)/(2*w+1)
    return np.c_[[np.convolve(np.r_[c[-w:, i], c[:, i], c[:w, i]], k, mode='valid') for i in (0, 1)]].T

# ---------- 3: corners ----------
def corners(c):
    n = len(c); idx = []
    turn = np.zeros(n)
    for i in range(n):
        p0, p1, p2 = c[(i-CORNER_SPAN) % n], c[i], c[(i+CORNER_SPAN) % n]
        v1, v2 = p1-p0, p2-p1
        turn[i] = abs(math.degrees(math.atan2(v1[0]*v2[1]-v1[1]*v2[0], v1@v2)))
    for i in range(n):                                 # local maxima over the threshold
        win = [turn[(i+j) % n] for j in range(-CORNER_SPAN, CORNER_SPAN+1)]
        if turn[i] >= CORNER_DEG and turn[i] == max(win): idx.append(i)
    return idx

# ---------- 4: Schneider fit ----------
def bez(P, t):
    t = np.asarray(t)[:, None]; mt = 1-t
    return mt**3*P[0] + 3*mt**2*t*P[1] + 3*mt*t**2*P[2] + t**3*P[3]
def bez1(P, t): mt = 1-t; return 3*mt**2*(P[1]-P[0]) + 6*mt*t*(P[2]-P[1]) + 3*t**2*(P[3]-P[2])
def bez2(P, t): mt = 1-t; return 6*mt*(P[2]-2*P[1]+P[0]) + 6*t*(P[3]-2*P[2]+P[1])
def unit(v): n = np.linalg.norm(v); return v/n if n > 1e-12 else v
def chord(pts):
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(pts, axis=0).T))]; return d/d[-1]
def gen(pts, u, t1, t2):
    P0, P3 = pts[0], pts[-1]
    A1 = np.outer(3*(1-u)**2*u, t1); A2 = np.outer(3*(1-u)*u**2, t2)
    C = np.array([[np.sum(A1*A1), np.sum(A1*A2)], [np.sum(A1*A2), np.sum(A2*A2)]])
    tmp = pts - (np.outer((1-u)**3 + 3*(1-u)**2*u, P0) + np.outer(3*(1-u)*u**2 + u**3, P3))
    X = np.array([np.sum(A1*tmp), np.sum(A2*tmp)])
    det = np.linalg.det(C); seg = np.linalg.norm(P3-P0)
    a1 = a2 = None
    if abs(det) > 1e-12:
        a1, a2 = np.linalg.solve(C, X)
    if a1 is None or a1 < 1e-6*seg or a2 < 1e-6*seg:
        a1 = a2 = seg/3
    return np.array([P0, P0+t1*a1, P3+t2*a2, P3])
def reparam(P, pts, u):
    d = bez(P, u) - pts; d1 = np.array([bez1(P, x) for x in u]); d2 = np.array([bez2(P, x) for x in u])
    num = np.sum(d*d1, axis=1); den = np.sum(d1*d1, axis=1) + np.sum(d*d2, axis=1)
    return np.clip(np.where(np.abs(den) > 1e-12, u - num/den, u), 0, 1)
def fit(pts, t1, t2, tol):
    if len(pts) == 2:
        s = np.linalg.norm(pts[1]-pts[0])/3; return [np.array([pts[0], pts[0]+t1*s, pts[1]+t2*s, pts[1]])]
    u = chord(pts); P = gen(pts, u, t1, t2)
    for _ in range(12):
        err = np.hypot(*(bez(P, u)-pts).T); k = int(np.argmax(err))
        if err[k] < tol: return [P]
        if err[k] > tol*6 and _ > 3: break
        u = reparam(P, pts, u); P = gen(pts, u, t1, t2)
    err = np.hypot(*(bez(P, u)-pts).T); k = int(np.argmax(err))
    if err[k] < tol: return [P]
    k = min(max(k, 1), len(pts)-2)
    tc = unit(pts[k-1]-pts[k+1])
    return fit(pts[:k+1], t1, tc, tol) + fit(pts[k:], -tc, t2, tol)

def fit_closed(c):
    c = smooth(resample(c))
    idx = corners(c); n = len(c)
    if not idx:                                        # fully smooth loop: split at the extremes
        idx = [int(np.argmin(c[:, 0])), int(np.argmax(c[:, 0]))]
    idx = sorted(idx); segs = []
    for a_, b_ in zip(idx, idx[1:]+[idx[0]+n]):
        pts = np.array([c[i % n] for i in range(a_, b_+1)])
        m = min(CORNER_SPAN+1, len(pts)-1)
        t1 = unit(pts[m]-pts[0]); t2 = unit(pts[-1-m]-pts[-1])
        segs += fit(pts, t1, t2, TOL)
    return segs

paths, allsegs = [], []
for c in raw:
    segs = fit_closed(c); allsegs.append(segs)
    d = f'M{segs[0][0][0]:.3f} {segs[0][0][1]:.3f}'
    for P in segs: d += f'C{P[1][0]:.3f} {P[1][1]:.3f} {P[2][0]:.3f} {P[2][1]:.3f} {P[3][0]:.3f} {P[3][1]:.3f}'
    paths.append(d+'Z')
d = ''.join(paths)
allpts = np.vstack([np.vstack([bez(P, np.linspace(0, 1, 60)) for P in segs]) for segs in allsegs])
bbox = [float(allpts[:, 0].min()), float(allpts[:, 1].min()), float(allpts[:, 0].max()), float(allpts[:, 1].max())]
(ROOT/'mark-path.json').write_text(json.dumps({'d': d, 'w': W, 'h': H, 'bbox': bbox}))

# ---------- 5: verification ----------
S = 8
img = Image.new('L', (W*S, H*S), 0); dr = ImageDraw.Draw(img)
for segs in allsegs:
    pts = np.vstack([bez(P, np.linspace(0, 1, 40)) for P in segs])
    dr.polygon([(x*S, y*S) for x, y in pts], fill=255)
r = np.asarray(img.resize((W, H), Image.BOX)).astype(float)/255
diff = np.abs(r-cov); m, g = r > .5, cov > .5
print(f'subpaths {len(raw)} | bezier segments {sum(len(s) for s in allsegs)} | path chars {len(d)}')
print(f'coverage MAE {diff.mean():.4f}  IoU {(m&g).sum()/(m|g).sum():.4f}  pixels differing >0.5: {(diff>.5).sum()}  max diff {diff.max():.2f}')
