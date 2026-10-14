/* Bangarang Apps — scroll motion. No dependencies. One rAF loop.
   Everything degrades: no JS = static page; reduced motion = static page. */
(() => {
  'use strict';
  const d = document;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const ease = (t) => t * t * (3 - 2 * t);
  const $$ = (s, c = d) => Array.from(c.querySelectorAll(s));

  const header = d.querySelector('.hdr');
  const worlds = $$('main [data-world], footer[data-world]');
  const hero = d.querySelector('[data-hero]');
  const mf = d.querySelector('[data-mf]');
  const strips = $$('[data-strip]');
  const parallax = $$('[data-parallax]');
  const viewFits = $$('[data-wdth-view]');

  /* Fit a heavy line of type to its container's width at a given Archivo width axis. */
  function fit(el, wd) {
    const wrap = el.querySelector('.fit-wrap');
    if (!wrap) return;
    el.style.setProperty('--wd', wd.toFixed(2));
    el.style.setProperty('--aw', (wd <= 100 ? lerp(0.53, 0.759, (wd - 62) / 38) : lerp(0.759, 0.938, (wd - 100) / 25)).toFixed(4));
    el.style.fontSize = '100px';
    const w = wrap.getBoundingClientRect().width;
    if (w > 0) el.style.fontSize = (100 * el.clientWidth / w).toFixed(2) + 'px';
  }

  /* Split manifesto copy into words (keeps <em> wrappers). */
  function split(node) {
    Array.from(node.childNodes).forEach((c) => {
      if (c.nodeType === 3) {
        const frag = d.createDocumentFragment();
        c.textContent.split(/(\s+)/).forEach((part) => {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(d.createTextNode(part)); return; }
          const s = d.createElement('span');
          s.className = 'w';
          s.textContent = part;
          frag.appendChild(s);
        });
        node.replaceChild(frag, c);
      } else if (c.nodeType === 1) split(c);
    });
  }
  const mfText = mf && mf.querySelector('[data-words]');
  let words = [];
  if (mfText && !reduce) { split(mfText); words = $$('.w', mfText); }

  /* The sail A: sails fill and ease as you scroll. Geometry mirrors tools/wordmark.py. */
  const SL = { O: [[47,0],[24,22],[3,60],[0,100]], I: [[50,0],[40,30],[34,66],[30,100]], cuts: [[0,.47],[.53,1]] };
  const SR = { O: [[53,0],[80,22],[99,56],[100,100]], I: [[50,0],[60,30],[67,66],[70,100]], cuts: [[0,.30],[.37,.66],[.73,1]] };
  const mix = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
  const billow = (c, b) => c.map((p, i) => {
    if (i === 0 || i === 3) return p;
    const s = mix(c[0], c[3], i / 3);
    return [s[0] + (p[0] - s[0]) * b, s[1] + (p[1] - s[1]) * b];
  });
  const pt = (p) => p[0].toFixed(2) + ' ' + p[1].toFixed(2);
  function sailD(leg, b) {
    const O = billow(leg.O, b), I = billow(leg.I, b);
    return leg.cuts.map(([f0, f1]) => {
      const c0 = O.map((p, i) => mix(p, I[i], f0)), c1 = O.map((p, i) => mix(p, I[i], f1));
      return `M${pt(c0[0])}C${pt(c0[1])} ${pt(c0[2])} ${pt(c0[3])}L${pt(c1[3])}C${pt(c1[2])} ${pt(c1[1])} ${pt(c1[0])}Z`;
    });
  }
  const sailPaths = hero ? $$('.sa path', hero) : [];
  function setSail(b) {
    if (!sailPaths.length) return;
    const ds = sailD(SL, b).concat(sailD(SR, b));
    sailPaths.forEach((p, i) => { if (ds[i]) p.setAttribute('d', ds[i]); });
  }

  /* ---------- the loop ---------- */
  let queued = false;
  const request = () => { if (!queued) { queued = true; requestAnimationFrame(tick); } };

  function tick() {
    queued = false;
    const vh = innerHeight;

    /* header takes the color world of whatever is under it */
    if (header) {
      const y = header.offsetHeight * 0.5;
      for (const s of worlds) {
        const r = s.getBoundingClientRect();
        if (r.top <= y && r.bottom > y) {
          if (header.dataset.world !== s.dataset.world) header.dataset.world = s.dataset.world;
          break;
        }
      }
    }
    if (reduce) return;

    /* hero: the word breathes from tall-and-tight to wide as you scroll */
    if (hero) {
      const r = hero.getBoundingClientRect();
      if (r.bottom > 0) {
        const p = clamp(-r.top / Math.max(1, r.height - vh));
        fit(hero.querySelector('[data-fit]'), lerp(62, 125, ease(p)));
        setSail(1 + 0.3 * Math.sin(p * Math.PI * 3));
      }
    }

    /* manifesto: words light up in reading order */
    if (mf && words.length) {
      const r = mf.getBoundingClientRect();
      if (r.bottom > 0 && r.top < vh) {
        const p = clamp(-r.top / Math.max(1, r.height - vh));
        const lit = p * (words.length + 4);
        for (let i = 0; i < words.length; i++) {
          words[i].style.opacity = (0.14 + 0.86 * clamp(lit - i)).toFixed(3);
        }
      }
    }

    /* strips: rows drift sideways, opposite ways, tied to scroll */
    strips.forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;
      const v = clamp((vh - r.top) / (vh + r.height));
      $$('[data-dir]', el).forEach((row) => {
        const dir = Number(row.dataset.dir);
        const travel = Math.max(0, row.scrollWidth - innerWidth);
        const x = dir < 0 ? -travel * v : -travel * (1 - v);
        row.style.transform = `translate3d(${x.toFixed(1)}px,0,0)`;
      });
    });

    /* product shots drift a little against the scroll */
    parallax.forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;
      const v = clamp((vh - r.top) / (vh + r.height));
      const amt = Number(el.dataset.parallax) || 48;
      el.style.transform = `translate3d(0,${((0.5 - v) * amt).toFixed(1)}px,0)`;
    });

    /* big headings that widen as they arrive */
    viewFits.forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;
      const [a, b] = el.dataset.wdthView.split(',').map(Number);
      const v = clamp((vh - r.top) / (vh * 0.6));
      fit(el, lerp(a, b, ease(v)));
    });
  }

  /* reveal on enter */
  if (!reduce && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
    $$('.rv').forEach((el) => io.observe(el));
  }

  function refit() {
    if (reduce) $$('[data-fit]').forEach((el) => fit(el, 100));
    viewFits.forEach((el) => fit(el, reduce ? 100 : Number(el.dataset.wdthView.split(',')[0])));
    request();
  }
  addEventListener('scroll', request, { passive: true });
  addEventListener('resize', refit);
  (d.fonts && d.fonts.ready ? d.fonts.ready : Promise.resolve()).then(refit);
  refit();
})();
