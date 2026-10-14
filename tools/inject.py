#!/usr/bin/env python3
"""Pushes the generated logo into the hand-written HTML/CSS (header/footer symbol, hero lockups, wordmark sizing).
Run after tools/construct.py and tools/wordmark.py."""
import re, json, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
sym = (R/'tools/wm-symbol.html').read_text(); use = (R/'tools/wm-use.html').read_text()
hd = (R/'tools/hero-d.html').read_text(); hm = (R/'tools/hero-m.html').read_text()
met = json.loads((R/'tools/metrics.json').read_text())
for name in ['index.html', 'privacy/index.html', 'terms/index.html', 'contact/index.html', '404.html']:
    p = R/name; s = p.read_text()
    s, n1 = re.subn(r'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><symbol id="wm".*?</symbol></svg>', lambda m: sym, s, flags=re.S)
    s, n2 = re.subn(r'<svg viewBox="[^"]*" role="img" aria-label="Bangarang"><use href="#wm"/></svg>', lambda m: use, s)
    assert n1 == 1 and n2 >= 1, (name, n1, n2)
    if name == 'index.html':
        s, n3 = re.subn(r'<h1 class="hero-word"[^>]*>.*?</h1>', lambda m: '<h1 class="hero-word" aria-label="Bangarang">' + hd + hm + '</h1>', s, flags=re.S)
        assert n3 == 1, 'hero h1'
    p.write_text(s)
# header/footer wordmark height: keep the LETTERS the same size as before the taller viewBox
c = R/'assets/css/site.css'; t = c.read_text()
k = met['vb_h'] / 712
t = re.sub(r'(\.mk svg \{[^}]*?height: )[^;]+(;)', lambda m: f'{m.group(1)}{20*k:.1f}px{m.group(2)}', t, count=1)
t = re.sub(r'(\.foot \.mk svg \{ height: )[^;]+(;)', lambda m: f'{m.group(1)}{28*k:.1f}px{m.group(2)}', t, count=1)
c.write_text(t); print('injected; vb_h', met['vb_h'], 'k', round(k, 3))
