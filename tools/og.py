#!/usr/bin/env python3
"""Builds tools/og-card.html, the 1200x630 social card, from the shipped logo files (so it can never drift from them).
Render it to og.png with the gstack browser at 1200x630:
    python3 tools/og.py && B=~/.claude/skills/gstack/browse/dist/browse && $B viewport 1200x630 && \
      $B goto file://$PWD/tools/og-card.html && sleep 2 && $B screenshot --viewport og.png
"""
import pathlib, re
R = pathlib.Path(__file__).resolve().parent.parent
wm = (R / 'assets/brand/wordmark.svg').read_text()
vb = re.search(r'viewBox="([^"]+)"', wm).group(1)
inner = wm[wm.index('>', wm.index('<svg')) + 1: wm.rindex('</svg>')]
mk = (R / 'assets/brand/mark.svg').read_text()
mpath = re.search(r'<path[^>]*/>', mk).group(0)
M = __import__('json').loads((R / 'tools/metrics.json').read_text())
html = f'''<!doctype html><meta charset="utf-8"><title>og</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=JetBrains+Mono:wght@400&display=swap">
<style>
html,body{{margin:0;width:1200px;height:630px;background:#0c0a0a;overflow:hidden}}
body{{position:relative;color:#eee9da;font-family:"Archivo",sans-serif}}
.sail{{position:absolute;height:590px;width:{590 * 0.8704:.0f}px;top:20px;right:{-0.30 * 590 * 0.8704:.0f}px;fill:#ff1f2d;opacity:.11}}
.eyebrow{{position:absolute;left:60px;top:116px;font:400 13px "JetBrains Mono",monospace;letter-spacing:.14em;text-transform:uppercase;color:rgba(238,233,218,.68)}}
.line{{position:absolute;left:60px;top:168px;margin:0;font-size:56px;font-weight:700;line-height:1.02;letter-spacing:-.025em;font-variation-settings:"wdth" 88}}
.rw{{background:#ff1f2d;color:#0c0a0a;padding:0 .1em;margin-inline:.02em}}
.wm{{position:absolute;left:60px;right:60px;top:318px;width:1080px;color:#eee9da;--sail:#ff1f2d}}
</style>
<svg class="sail" viewBox="0 0 {M['bw']:.2f} {M['bh']:.2f}">{mpath}</svg>
<div class="eyebrow">Bangarang Apps, Inc.</div>
<p class="line">Apps with a little<br>more <span class="rw">life</span> in them.</p>
<svg class="wm" viewBox="{vb}">{inner}</svg>
'''
(R / 'tools/og-card.html').write_text(html)
print('wrote tools/og-card.html')
