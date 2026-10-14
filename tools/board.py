#!/usr/bin/env python3
"""Builds docs/brand-board.html (content-only HTML, also published as an Artifact) from assets/brand/*."""
import re, json, base64, pathlib
R = pathlib.Path(__file__).resolve().parent.parent; b = R/'assets'/'brand'
def svg(name, cls=''):
    s = re.sub(r' style="[^"]*"', '', (b/name).read_text(), count=1)
    return s.replace('<svg ', f'<svg class="{cls}" ', 1)
M, WM, WP, LS = svg('mark.svg', 'm'), svg('wordmark.svg', 'wm'), svg('wordmark-plain.svg', 'wm'), svg('lockup-stacked.svg', 'ls')
MS, WS = svg('mark-small.svg', 'm'), svg('wordmark-small.svg', 'wm')
src = base64.b64encode((R/'tools/source/mark-original.png').read_bytes()).decode()
met = json.loads((R/'tools/metrics.json').read_text())
tile = lambda cls, inner, label='': f'<figure class="tile {cls}">{inner}<figcaption>{label}</figcaption></figure>'
fav = (R/'favicon.svg').read_text()
favs = ''.join(f'<div class="sq" style="width:{px}px;height:{px}px">{fav.replace("<svg ", f"<svg width=\"{px}\" height=\"{px}\" ", 1)}</div>' for px in (16, 32, 48, 64, 96, 180))
html = f'''<title>Bangarang Mark</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
:root{{--ink:#0c0a0a;--forest:#210d10;--bone:#eee9da;--glow:#ff1f2d;--persimmon:#d8512f;--dim:rgba(238,233,218,.68);--line:rgba(238,233,218,.18);color-scheme:dark}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--ink);color:var(--bone);font-family:"Archivo",system-ui,sans-serif;font-size:17px;line-height:1.55;-webkit-font-smoothing:antialiased}}
.wrap{{width:min(100% - 40px,1180px);margin-inline:auto}} section{{padding-block:clamp(48px,7vw,96px);border-top:1px solid var(--line)}}
h1{{margin:0;font-size:clamp(44px,9vw,120px);font-weight:900;text-transform:uppercase;line-height:.88;letter-spacing:-.02em;font-variation-settings:"wdth" 80}}
h2{{margin:0 0 24px;font-family:"JetBrains Mono",monospace;font-size:12px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;color:var(--dim)}}
p{{margin:0 0 14px;max-width:62ch;color:var(--dim)}} .mono{{font-family:"JetBrains Mono",monospace;font-size:12px;letter-spacing:.06em}}
.grid{{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr))}}
.tile{{margin:0;display:grid;place-items:center;align-content:center;padding:clamp(24px,4vw,44px);min-height:260px;position:relative}}
.tile figcaption{{position:absolute;left:14px;bottom:10px;font-family:"JetBrains Mono",monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;opacity:.7}}
.t-ink{{background:var(--ink);color:var(--bone);--sail:var(--glow);outline:1px solid var(--line);outline-offset:-1px}} .t-forest{{background:var(--forest);color:var(--bone);--sail:var(--glow)}}
.t-bone{{background:var(--bone);color:var(--ink);--sail:var(--ink)}} .t-glow{{background:var(--glow);color:var(--ink);--sail:var(--ink)}} .t-pers{{background:var(--persimmon);color:#fff;--sail:#fff}} .t-white{{background:#fff;color:var(--ink);--sail:var(--ink)}}
.wm{{width:min(100%,640px);height:auto}} .m{{height:clamp(130px,17vw,210px);width:auto;color:var(--sail,currentColor)}} .ls{{width:min(100%,340px);height:auto}}
.hero-tile{{min-height:clamp(280px,40vw,460px)}} .hero-tile .wm{{width:min(100%,1000px)}}
.sizes{{display:flex;gap:28px;align-items:flex-end;flex-wrap:wrap}} .sq{{outline:1px solid var(--line)}} .sq svg{{display:block}}
.two{{display:grid;gap:clamp(24px,5vw,72px);grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));align-items:center}}
ul{{margin:0;padding-left:20px}} li{{margin-bottom:8px;color:var(--dim)}} li b{{color:var(--bone)}} .src{{width:100%;max-width:300px;height:auto;image-rendering:auto}}
</style>
<div class="wrap" style="padding-top:clamp(32px,5vw,72px)"><p class="mono" style="color:var(--glow)">Bangarang Apps, Inc. / mark v4</p><h1>The mark</h1>
<p style="margin-top:20px">Built from the original artwork (<span class="mono">tools/source/mark-original.png</span>) as clean vectors. It is never redrawn, stretched or re-coloured per piece. It stands in for the middle A of the name. Everything below is generated, so every format matches.</p></div>

<section><div class="wrap"><h2>Primary wordmark</h2>
<div class="grid" style="grid-template-columns:1fr">{tile("t-ink hero-tile", WM, "on ink")}</div>
<div class="grid" style="margin-top:14px">{tile("t-bone", WM, "one colour, on bone")}{tile("t-glow", WM, "on red")}{tile("t-forest", WM, "on oxblood")}</div></div></section>

<section><div class="wrap"><h2>The mark</h2>
<div class="grid">{tile("t-ink", M, "on ink")}{tile("t-glow", M, "on red")}{tile("t-bone", M, "on bone")}{tile("t-pers", M, "reversed, on persimmon")}</div></div></section>

<section><div class="wrap"><h2>Stacked lockup (plain A beside the mark, so it isn't repeated)</h2>
<div class="grid">{tile("t-ink", LS, "on ink")}{tile("t-bone", LS, "on bone")}{tile("t-glow", LS, "on red")}</div></div></section>

<section><div class="wrap"><h2>Two optical cuts: display and small</h2>
<div class="two"><div class="grid">{tile("t-ink", M, "display mark: 11 px gaps")}{tile("t-ink", MS, "small mark: 22 px gaps")}</div>
<div><ul><li><b>Display</b> is the artwork as drawn. Use it above about 40 px: hero, print, merch.</li><li><b>Small</b> doubles the gaps between the three pieces so they survive at 16 to 36 px, with looser letter-spacing and more air to the right of the mark so the R no longer crowds it. Used for the header, footer and favicon.</li><li>Same drawing, same flow and right-hand line; only the gap width and spacing change.</li></ul></div></div>
<div class="grid" style="margin-top:14px;grid-template-columns:1fr 1fr">{tile("t-ink", WM, "wordmark, display")}{tile("t-ink", WS, "wordmark, small")}</div></div></section>

<section><div class="wrap"><h2>Small sizes: favicon, app icon, avatar</h2><div class="sizes">{favs}</div>
<p class="mono" style="margin-top:14px">16 / 32 / 48 / 64 / 96 / 180 px, small cut. At 32 px all three pieces separate; at 16 px it reads as a sail silhouette with stripes.</p></div></section>

<section><div class="wrap"><h2>One colour: any garment, any ground</h2>
<div class="grid">{tile("t-bone", M, "ink on bone")}{tile("t-glow", M, "ink on red")}{tile("t-ink", M, "red on ink")}{tile("t-pers", M, "white on persimmon")}{tile("t-white", M, "ink on white")}{tile("t-forest", M, "red on oxblood")}</div></div></section>

<section><div class="wrap"><h2>Construction: source vs vector</h2>
<div class="two"><div class="grid">{tile("t-bone", f'<img class="src" alt="Original raster" src="data:image/png;base64,{src}">', "original, 278 x 280 px")}{tile("t-bone", M, "constructed vector")}</div>
<div><ul><li><b>Right edge:</b> cap and band edges sit on one straight line (51.5 degrees, apex to the swoosh's top-right corner). The band's top-right is a sharp corner on that line; the swoosh curve starts there.</li><li><b>Gaps:</b> identical, 11 px at source scale, constant along their length (measured 10.8 to 11.1 px). Each gap is an exact offset of the edge above it, so the pieces flow.</li><li><b>Points:</b> 11 Bezier segments for the whole mark, smooth except at true corners. A raw pixel trace needed 114 and was bumpy.</li><li><b>Fidelity:</b> mean 0.85 px from your original, max 3.1 px of 248 (1.3%). The 278 px original has wobble; this keeps its design, not its wobble.</li></</ul></div></div></div></section>

<section><div class="wrap"><div class="two"><div><h2>Colour</h2><ul><li><b>Ink</b> #0c0a0a</li><li><b>Oxblood</b> #210d10</li><li><b>Bone</b> #eee9da</li><li><b>Red</b> #ff1f2d. Highlighter red: the mark's colour on dark grounds, and the full-bleed finale.</li></ul><p style="margin-top:14px">Wordmark type is Gabarito Bold (SIL OFL), cap height normalised, tracking 0. The mark is the only coloured letter.</p></div>
<div><h2>Rules</h2><ul><li>Clear space: a quarter of the mark's height on every side.</li><li>Minimum: mark 16 px / 6 mm; wordmark 90 px / 25 mm wide.</li><li>One colour, or the mark in accent with letters in ink/bone. No gradients, outlines, shadows, rotation or skew.</li><li>Never redraw or re-typeset. Re-run the generator.</li></ul></div></div></div></section>

<section><div class="wrap"><h2>Files (repo: assets/brand)</h2><ul class="mono"><li>mark.svg · mark-small.svg</li><li>wordmark.svg · wordmark-small.svg · wordmark-plain.svg</li><li>lockup-stacked.svg</li><li>/favicon.svg · /apple-touch-icon.png · /og.png</li></ul></div></section>'''
(R/'docs'/'brand-board.html').write_text(html)
print(len(html))
