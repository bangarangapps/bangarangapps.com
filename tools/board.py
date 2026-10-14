#!/usr/bin/env python3
"""Builds docs/brand-board.html (content-only HTML, also published as an Artifact) from assets/brand/*."""
import re, json, base64, pathlib
R = pathlib.Path(__file__).resolve().parent.parent; b = R/'assets'/'brand'
def svg(name, cls=''):
    s = re.sub(r' style="[^"]*"', '', (b/name).read_text(), count=1)
    return s.replace('<svg ', f'<svg class="{cls}" ', 1)
M, WM, WP, LS = svg('mark.svg', 'm'), svg('wordmark.svg', 'wm'), svg('wordmark-plain.svg', 'wm'), svg('lockup-stacked.svg', 'ls')
src = base64.b64encode((R/'tools/source/mark-original.png').read_bytes()).decode()
met = json.loads((R/'tools/metrics.json').read_text())
tile = lambda cls, inner, label='': f'<figure class="tile {cls}">{inner}<figcaption>{label}</figcaption></figure>'
fav = (R/'favicon.svg').read_text()
favs = ''.join(f'<div class="sq" style="width:{px}px;height:{px}px">{fav.replace("<svg ", f"<svg width=\"{px}\" height=\"{px}\" ", 1)}</div>' for px in (16, 32, 48, 64, 96, 180))
html = f'''<title>Bangarang Mark</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
:root{{--ink:#0b100d;--forest:#132119;--bone:#eee9da;--glow:#d6f24a;--persimmon:#d8512f;--dim:rgba(238,233,218,.68);--line:rgba(238,233,218,.18);color-scheme:dark}}
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
<p style="margin-top:20px">Traced 1:1 from the original artwork (<span class="mono">tools/source/mark-original.png</span>). It is never redrawn, stretched or re-coloured per piece. It stands in for the middle A of the name. Everything below is generated, so every format matches.</p></div>

<section><div class="wrap"><h2>Primary wordmark</h2>
<div class="grid" style="grid-template-columns:1fr">{tile("t-ink hero-tile", WM, "on ink")}</div>
<div class="grid" style="margin-top:14px">{tile("t-bone", WM, "one colour, on bone")}{tile("t-glow", WM, "on glow")}{tile("t-forest", WM, "on forest")}</div></div></section>

<section><div class="wrap"><h2>The mark</h2>
<div class="grid">{tile("t-ink", M, "on ink")}{tile("t-glow", M, "on glow")}{tile("t-bone", M, "on bone")}{tile("t-pers", M, "reversed, on persimmon")}</div></div></section>

<section><div class="wrap"><h2>Stacked lockup (plain A beside the mark, so it isn't repeated)</h2>
<div class="grid">{tile("t-ink", LS, "on ink")}{tile("t-bone", LS, "on bone")}{tile("t-glow", LS, "on glow")}</div></div></section>

<section><div class="wrap"><h2>Small sizes: favicon, app icon, avatar</h2><div class="sizes">{favs}</div>
<p class="mono" style="margin-top:14px">16 / 32 / 48 / 64 / 96 / 180 px. The gaps between the three pieces close up below about 24 px; the silhouette still reads.</p></div></section>

<section><div class="wrap"><h2>One colour: any garment, any ground</h2>
<div class="grid">{tile("t-bone", M, "ink on bone")}{tile("t-glow", M, "ink on glow")}{tile("t-ink", M, "glow on ink")}{tile("t-pers", M, "white on persimmon")}{tile("t-white", M, "ink on white")}{tile("t-forest", M, "glow on forest")}</div></div></section>

<section><div class="wrap"><h2>Fidelity: source vs vector</h2>
<div class="two"><div class="grid">{tile("t-bone", f'<img class="src" alt="Original raster" src="data:image/png;base64,{src}">', "original, 278 x 280 px")}{tile("t-bone", M, "traced vector")}</div>
<div><ul><li><b>Method:</b> sub-pixel contour from the original's coverage, corners detected, least-squares cubic Bezier fit at 0.3 px tolerance.</li><li><b>Result:</b> 3 pieces, 114 curves, 99.1% area overlap with the original, 11 of 77,840 pixels differ by more than half a pixel.</li><li><b>Honest limit:</b> the original is 278 px tall, so its small edge wobbles are in the trace. They are invisible at web sizes and will show on a large print. A larger export from the Photoshop file traces cleaner (<span class="mono">python tools/trace.py</span>).</li></ul></div></div></div></section>

<section><div class="wrap"><div class="two"><div><h2>Colour</h2><ul><li><b>Ink</b> #0b100d</li><li><b>Forest</b> #132119</li><li><b>Bone</b> #eee9da</li><li><b>Glow</b> #d6f24a. The mark's colour on dark grounds.</li></ul><p style="margin-top:14px">Type is Archivo 900. The mark is the only coloured letter.</p></div>
<div><h2>Rules</h2><ul><li>Clear space: a quarter of the mark's height on every side.</li><li>Minimum: mark 16 px / 6 mm; wordmark 90 px / 25 mm wide.</li><li>One colour, or the mark in accent with letters in ink/bone. No gradients, outlines, shadows, rotation or skew.</li><li>Never redraw or re-typeset. Re-run the generator.</li></ul></div></div></div></section>

<section><div class="wrap"><h2>Files (repo: assets/brand)</h2><ul class="mono"><li>mark.svg</li><li>wordmark.svg · wordmark-plain.svg</li><li>lockup-stacked.svg</li><li>/favicon.svg · /apple-touch-icon.png · /og.png</li></ul></div></section>'''
(R/'docs'/'brand-board.html').write_text(html)
print(len(html))
