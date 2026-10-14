#!/usr/bin/env python3
"""Pushes the generated mark into the hand-written HTML/CSS (header/footer wordmark symbol, hero mark, CSS aspect).
Run after tools/trace.py and tools/wordmark.py."""
import re, json, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
sym = (R/'tools/wm-symbol.html').read_text(); use = (R/'tools/wm-use.html').read_text(); mark = (R/'tools/sail-a.html').read_text()
met = json.loads((R/'tools/metrics.json').read_text())
for name in ['index.html', 'privacy/index.html', 'terms/index.html', 'contact/index.html', '404.html']:
    p = R/name; s = p.read_text()
    s, n1 = re.subn(r'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><symbol id="wm".*?</symbol></svg>', lambda m: sym, s, flags=re.S)
    s, n2 = re.subn(r'<svg viewBox="0 0 \d+ 712" role="img" aria-label="Bangarang"><use href="#wm"/></svg>', lambda m: use, s)
    assert n1 == 1 and n2 >= 1, (name, n1, n2)
    if name == 'index.html':
        s, n3 = re.subn(r'<svg class="sa" viewBox="[^"]*" focusable="false">.*?</svg>', lambda m: f'<svg class="sa" viewBox="0 0 {met["bw"]:.1f} {met["bh"]:.1f}" focusable="false">{mark}</svg>', s, flags=re.S)
        assert n3 == 1
    p.write_text(s)
c = R/'assets/css/site.css'; t = c.read_text()
t = re.sub(r'(\.sa \{[^}]*?width: calc\(\.688em \* )[0-9.]+(\))', lambda m: f'{m.group(1)}{met["aspect"]:.4f}{m.group(2)}', t)
c.write_text(t); print('injected; aspect', round(met['aspect'], 4))
