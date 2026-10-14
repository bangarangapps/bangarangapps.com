(() => {
  const parse = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p[3] === undefined ? 1 : p[3] }; };
  const lum = ({ r, g, b }) => { const f = (v) => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
  const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + .05) / (y + .05); };
  const blend = (fg, bg) => ({ r: fg.r * fg.a + bg.r * (1 - fg.a), g: fg.g * fg.a + bg.g * (1 - fg.a), b: fg.b * fg.a + bg.b * (1 - fg.a), a: 1 });
  const effBg = (el) => { let e = el; while (e) { const c = parse(getComputedStyle(e).backgroundColor); if (c && c.a > 0.99) return c; e = e.parentElement; } return { r: 12, g: 10, b: 10, a: 1 }; };
  const out = { text: [], focus: [], targets: [], misc: {} };
  const seen = new Set();
  document.querySelectorAll('body *').forEach((el) => {
    if (el.closest('svg') || el.closest('symbol')) return;
    const own = Array.from(el.childNodes).some((n) => n.nodeType === 3 && n.textContent.trim());
    if (!own) return;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') return;
    const fs = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight) >= 700;
    const large = fs >= 24 || (fs >= 18.66 && bold);
    const bg = effBg(el); let fg = parse(cs.color); fg = blend({ ...fg, a: fg.a * parseFloat(cs.opacity || 1) }, bg);
    const r = ratio(fg, bg), need = large ? 3 : 4.5;
    const key = el.className + '|' + cs.color + '|' + bg.r + bg.g + bg.b + '|' + fs;
    if (r < need && !seen.has(key)) { seen.add(key); out.text.push({ sel: (el.tagName.toLowerCase() + '.' + (el.className.baseVal ?? el.className)).slice(0, 40), text: el.textContent.trim().slice(0, 28), ratio: +r.toFixed(2), need, px: Math.round(fs), world: (el.closest('[data-world]') || {dataset:{}}).dataset.world }); }
  });
  // focus ring colour vs its world background
  const worlds = new Set(); document.querySelectorAll('[data-world]').forEach((e) => worlds.add(e.dataset.world));
  worlds.forEach((w) => { const e = document.querySelector('[data-world="' + w + '"]'); const cs = getComputedStyle(e); const acc = parse(cs.getPropertyValue('--accent').trim().startsWith('#') ? hex(cs.getPropertyValue('--accent').trim()) : cs.getPropertyValue('--accent')); const bg = parse(cs.backgroundColor); if (acc && bg) out.focus.push({ world: w, ring: +ratio(acc, bg).toFixed(2) }); });
  function hex(h) { h = h.replace('#', ''); if (h.length === 3) h = h.split('').map((c) => c + c).join(''); return `rgb(${parseInt(h.slice(0,2),16)},${parseInt(h.slice(2,4),16)},${parseInt(h.slice(4,6),16)})`; }
  document.querySelectorAll('a,button').forEach((el) => { const r = el.getBoundingClientRect(); if (r.width === 0) return; if (r.height < 44 || r.width < 44) out.targets.push({ t: (el.textContent.trim() || el.getAttribute('aria-label') || '').slice(0, 22), w: Math.round(r.width), h: Math.round(r.height) }); });
  out.misc = { lang: document.documentElement.lang, title: document.title, h1: document.querySelectorAll('h1').length, headings: Array.from(document.querySelectorAll('h1,h2,h3')).map((h) => h.tagName + ':' + (h.getAttribute('aria-label') || h.textContent.trim()).slice(0, 18)), landmarks: ['header', 'nav', 'main', 'footer'].map((t) => t + '=' + document.querySelectorAll(t).length).join(' '), skip: !!document.querySelector('.skip'), imgNoAlt: Array.from(document.images).filter((i) => !i.hasAttribute('alt')).length, newTab: Array.from(document.querySelectorAll('a[target=_blank]')).map((a) => a.textContent.trim().replace(/\s+/g, ' ').slice(0, 24)) };
  return JSON.stringify(out);
})()
