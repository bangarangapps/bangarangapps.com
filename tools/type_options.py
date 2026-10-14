#!/usr/bin/env python3
"""Builds docs/wordmark-options.html: the BANGARANG wordmark in many typefaces, with the real mark in the middle A.

Each option is true outline geometry (fonttools), not live text, so it is exactly what the logo would be.
Cap height is normalised to CAP so the mark (MARK_K x cap, equal overhang above/below) sits identically.
Fonts: Google Fonts (all SIL OFL). Files are fetched from google/fonts into $FONT_DIR.

Adopting an option: point tools/wordmark.py at the font file + weight (TTF, WGHT) and re-run the pipeline.
"""
import json, os, pathlib, math
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT_DIR = pathlib.Path(os.environ.get('FONT_DIR', '/tmp/bg/fnt/f'))
CAP = 700.0
MARK_K = 1.30
PAD = 0.075 * CAP
OVER = (MARK_K - 1) / 2 * CAP
BASE = CAP + OVER + 14
M = json.loads((ROOT/'tools'/'mark-path.json').read_text())
x0, y0, x1, y1 = M['bbox']; BW, BH = x1-x0, y1-y0; ASPECT = BW/BH
MH = MARK_K*CAP; MW = ASPECT*MH
MARK = f'<path transform="translate({-x0:.3f},{-y0:.3f})" d="{M["d"]}"/>'

# (slug, file, weight, label, group, note, tracking in cap-units)
OPTIONS = [
 ('archivo900', 'archivo.ttf', 900, 'Archivo Black (current)', 'Reference', 'What the site uses now. Heavy, sturdy, generic.', -0.02),
 ('archivo700', 'archivo.ttf', 700, 'Archivo Bold', 'Reference', 'Same face, lighter. The safe step down.', -0.01),
 ('syne', 'syne.ttf', 700, 'Syne Bold', 'Wide / editorial', 'Wide, theatrical, a little odd. Reads as a studio, not a template.', 0.0),
 ('unbounded', 'unbounded.ttf', 600, 'Unbounded SemiBold', 'Wide / rounded', 'Soft, wide, friendly corners. Playful without cartoon.', 0.0),
 ('bigshoulders', 'bigshouldersdisplay.ttf', 700, 'Big Shoulders Display', 'Condensed', 'Chicago signage. Tall and tough; very recognisable.', 0.03),
 ('leaguespartan', 'leaguespartan.ttf', 700, 'League Spartan Bold', 'Geometric', 'Futura-style circles and points. Pairs naturally with sails.', 0.01),
 ('jost', 'jost.ttf', 600, 'Jost SemiBold', 'Geometric', 'Cleaner, lighter Futura. Elegant, a little retro.', 0.02),
 ('josefin', 'josefinsans.ttf', 600, 'Josefin Sans SemiBold', 'Geometric', 'Vintage geometric with low, wide A and E. Distinct.', 0.02),
 ('sora', 'sora.ttf', 600, 'Sora SemiBold', 'Geometric', 'Wide, techy, very clean. Reads modern product.', 0.0),
 ('epilogue', 'epilogue.ttf', 700, 'Epilogue Bold', 'Grotesque', 'Sharp, tense grotesque. Confident and editorial.', 0.0),
 ('familjen', 'familjengrotesk.ttf', 700, 'Familjen Grotesk Bold', 'Grotesque', 'Quirky details, warm. Friendly but not soft.', 0.0),
 ('bricolage', 'bricolagegrotesque.ttf', 700, 'Bricolage Grotesque Bold', 'Grotesque', 'Inky, characterful. Still looks like most grotesques at a glance.', 0.0),
 ('gabarito', 'gabarito.ttf', 700, 'Gabarito Bold', 'Rounded geometric', 'Round, bold, upbeat. Games-and-apps energy.', 0.0),
 ('funnel', 'funneldisplay.ttf', 700, 'Funnel Display Bold', 'Display grotesque', 'Fresh 2024 display sans with crisp cuts. Not yet overused.', 0.0),
 ('lexend', 'lexend.ttf', 600, 'Lexend SemiBold', 'Wide / neutral', 'Wide, even, highly legible. Calm and modern.', 0.0),
 ('gloock', 'gloock.ttf', 400, 'Gloock', 'Serif', 'High-contrast display serif. Warm and editorial; a big departure.', 0.01),
 ('bodoni', 'bodonimoda.ttf', 700, 'Bodoni Moda Bold', 'Serif', 'Fashion-magazine contrast. Ownable, but hairlines vanish at header size.', 0.01),
 ('anybody', 'anybody.ttf', 700, 'Anybody Bold', 'Wide / extended', 'Extended and slightly retro-futurist. Loud.', 0.0),
 ('monasans', 'monasans.ttf', 700, 'Mona Sans Bold', 'Grotesque', 'GitHub-grade neutral grotesque. Polished, understated.', 0.0),
]

def build(file, wght):
    f = TTFont(FONT_DIR/file)
    if 'fvar' in f:
        loc = {}
        for ax in f['fvar'].axes:
            if ax.axisTag == 'wght': loc['wght'] = max(ax.minValue, min(ax.maxValue, wght))
            elif ax.axisTag == 'opsz': loc['opsz'] = ax.maxValue
            else: loc[ax.axisTag] = ax.defaultValue
        f = instantiateVariableFont(f, loc)
    gs = f.getGlyphSet(); cm = f.getBestCmap()
    bp = BoundsPen(gs); gs[cm[ord('H')]].draw(bp); cap = bp.bounds[3]
    s = CAP/cap
    return gs, cm, s

def wordmark(gs, cm, s, track, seq='BANGSRANG'):
    x = 0.0; parts = []
    tr = track*CAP
    for ch in seq:
        if ch == 'S':
            ty = BASE + OVER - MH
            parts.append(f'<g transform="translate({x+PAD:.1f},{ty:.1f}) scale({MH/BH:.5f})" style="fill:var(--sail)">{MARK}</g>')
            x += MW + 2*PAD + tr
        else:
            g = cm[ord(ch)]; pen = SVGPathPen(gs); gs[g].draw(pen)
            parts.append(f'<path transform="translate({x:.1f},{BASE}) scale({s:.5f},{-s:.5f})" d="{pen.getCommands()}" fill="currentColor"/>')
            x += gs[g].width*s + tr
    total = x - tr + 8
    return ''.join(parts), total

SHORTLIST = {'syne', 'josefin', 'bigshoulders', 'gloock'}
cards = []
outdir = ROOT/'docs'/'wordmark-options'; outdir.mkdir(exist_ok=True)
for i, (slug, file, wght, label, group, note, track) in enumerate(OPTIONS):
    gs, cm, s = build(file, wght)
    body, total = wordmark(gs, cm, s, track)
    vb = f'-4 0 {total:.0f} {BASE+OVER+14:.0f}'
    svg = f'<svg viewBox="{vb}" role="img" aria-label="Bangarang in {label}">{body}</svg>'
    (outdir/f'{slug}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" style="color:#eee9da;--sail:#ff1f2d">{body}</svg>')
    cards.append((i, slug, label, group, wght, note, svg))
    print(f'{i:2} {label:28} wght {wght}  width {total:.0f}')

def card(c):
    i, slug, label, group, wght, note, svg = c
    cur = ' cur' if i == 0 else (' pick' if slug in SHORTLIST else '')
    tag = '<span class="pk">Shortlist</span>' if slug in SHORTLIST else ''
    return f'''<article class="opt{cur}"><header><span class="n">{i:02d}</span><b>{label}</b>{tag}<span class="g">{group}</span></header>
<div class="ink">{svg}</div><div class="row"><div class="bone">{svg}</div><div class="lime">{svg}</div><div class="hdr">{svg}</div></div><p>{note}</p></article>'''

html = f'''<title>Wordmark Options</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;800&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
:root{{--ink:#0c0a0a;--bone:#eee9da;--glow:#ff1f2d;--dim:rgba(238,233,218,.68);--line:rgba(238,233,218,.18);color-scheme:dark}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--ink);color:var(--bone);font-family:"Archivo",system-ui,sans-serif;font-size:16px;line-height:1.5}}
.wrap{{width:min(100% - 32px,1280px);margin-inline:auto;padding-block:clamp(28px,5vw,64px)}}
h1{{margin:0 0 10px;font-size:clamp(34px,6vw,72px);font-weight:800;letter-spacing:-.02em;line-height:1}} .lead{{max-width:62ch;color:var(--dim);margin:0 0 28px}}
.grid{{display:grid;gap:18px;grid-template-columns:repeat(auto-fill,minmax(min(100%,560px),1fr))}}
.opt{{border:1px solid var(--line);padding:14px 14px 12px;display:grid;gap:10px;align-content:start}} .opt.cur{{border-color:var(--glow)}} .opt.pick{{border-color:rgba(214,242,74,.55);background:rgba(214,242,74,.04)}} .pk{{font-family:"JetBrains Mono",monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;background:var(--glow);color:var(--ink);padding:1px 6px}}
.opt header{{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}} .n{{font-family:"JetBrains Mono",monospace;font-size:12px;color:var(--glow)}}
.opt b{{font-weight:700}} .g{{margin-left:auto;font-family:"JetBrains Mono",monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--dim)}}
.opt p{{margin:0;color:var(--dim);font-size:14px}}
.ink,.bone,.lime,.hdr{{display:grid;align-items:center}} .ink{{background:var(--ink);color:var(--bone);--sail:var(--glow);padding:clamp(18px,3vw,30px) clamp(10px,2vw,22px);outline:1px solid var(--line);outline-offset:-1px}}
.row{{display:grid;grid-template-columns:1.2fr 1.2fr .8fr;gap:8px}}
.bone{{background:var(--bone);color:var(--ink);--sail:var(--ink);padding:14px 12px}} .lime{{background:var(--glow);color:var(--ink);--sail:var(--ink);padding:14px 12px}}
.hdr{{background:var(--ink);color:var(--bone);--sail:var(--glow);padding:10px 8px;outline:1px solid var(--line);outline-offset:-1px}}
svg{{display:block;width:100%;height:auto}} .hdr svg{{width:100%}}
</style>
<div class="wrap"><h1>Wordmark options</h1>
<p class="lead">Eighteen typefaces plus the current one, each rebuilt as real outlines with your mark as the middle A at the same size and equal overhang. All Google Fonts (SIL OFL, free for logo use). Weights are stepped back from 900 to semibold or bold, or regular for the serif. Each card shows ink, bone, red and header size. Most of the grotesques look alike at this weight; the four marked Shortlist are the ones that are actually different and would be hard to mistake for anyone else.</p>
<div class="grid">{''.join(card(c) for c in cards)}</div></div>'''
(ROOT/'docs'/'wordmark-options.html').write_text(html)
print('wrote docs/wordmark-options.html', len(html))
