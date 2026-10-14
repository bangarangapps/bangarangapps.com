#!/usr/bin/env python3
"""Builds docs/brand-sheet.html: the one-page Bangarang brand sheet (mark, wordmark, color, type, voice, rules).

Pulls the real logo geometry from assets/brand/*.svg (so it can never drift from the shipped files) and computes
every contrast ratio from the hex values below. Replaces the old tools/board.py. Re-run after any brand change:
    python3 tools/sheet.py
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
B = ROOT / 'assets' / 'brand'

# ---------- colors (mirror assets/css/site.css) ----------
INK, OXB, BONE, RED = '#0c0a0a', '#210d10', '#eee9da', '#ff1f2d'
PAPER, PAPER_INK, BLUE = '#efeae0', '#211d16', '#0f3fa8'
NIGHT, AMBER = '#0a0a0b', '#d97706'

def lum(h):
    h = h.lstrip('#'); r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)
def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True); return (la + .05) / (lb + .05)
def blend(fg, bg, a):
    f = [int(fg.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]; g = [int(bg.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
    return '#%02x%02x%02x' % tuple(round(a * x + (1 - a) * y) for x, y in zip(f, g))
def grade(r, large=False):
    if r >= 7: return 'AAA'
    if r >= 4.5: return 'AA'
    if r >= 3: return 'AA large' if large else 'Large text + graphics only'
    return 'Fails'

# ---------- logo geometry from the shipped files ----------
def inner(name):
    s = (B / name).read_text()
    vb = re.search(r'viewBox="([^"]+)"', s).group(1)
    body = s[s.index('>', s.index('<svg')) + 1: s.rindex('</svg>')]
    return vb, body
VB_MK, MK = inner('mark.svg'); VB_MKS, MKS = inner('mark-small.svg')
VB_WD, WD = inner('wordmark.svg'); VB_WS, WS = inner('wordmark-small.svg')
VB_WP, WP = inner('wordmark-plain.svg'); VB_LK, LK = inner('lockup-stacked.svg')
mk_w, mk_h = (float(x) for x in VB_MK.split()[2:])
ASPECT = mk_w / mk_h

symbols = (
    f'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">'
    f'<symbol id="mk" viewBox="{VB_MK}">{MK}</symbol><symbol id="mks" viewBox="{VB_MKS}">{MKS}</symbol>'
    f'<symbol id="wd" viewBox="{VB_WD}">{WD}</symbol><symbol id="ws" viewBox="{VB_WS}">{WS}</symbol>'
    f'<symbol id="wp" viewBox="{VB_WP}">{WP}</symbol><symbol id="lk" viewBox="{VB_LK}">{LK}</symbol></svg>')

def use(sym, vb, cls='', style='', label='Bangarang'):
    w, h = (float(x) for x in vb.split()[2:])
    return f'<svg class="{cls}" style="aspect-ratio:{w:.0f}/{h:.0f};{style}" role="img" aria-label="{label}"><use href="#{sym}"/></svg>'

# ---------- worlds ----------
worlds = [
    ('Ink', INK, BONE, 'The base. Hero, header, footer, anything that should feel like the studio.', INK),
    ('Oxblood', OXB, BONE, 'The second dark. Manifesto and "how we work": the same ink, warmed, so long stretches have rhythm.', OXB),
    ('Bone', BONE, '#17100f', 'Document pages (privacy, terms, refunds, contact) and any print use. Never pure white.', BONE),
    ('Highlighter red', RED, INK, 'The mark, the accent, the finale. One bold moment per screen; never body copy on red but ink.', RED),
]
ALPHA = {'Ink': .68, 'Oxblood': .70, 'Bone': .74, 'Highlighter red': .84}   # the --dim alpha each world uses in site.css
swatch_rows = []
for name, bg, fg, role, _ in worlds:
    dim = blend(fg, bg, ALPHA[name])
    swatch_rows.append((name, bg, fg, role, ratio(bg, fg), ratio(bg, dim)))

pairs = [
    ('Bone on ink', BONE, INK, 'Body and headings on the base world'),
    ('Ink on highlighter red', INK, RED, 'Hero finale ("Say hello"), buttons on red. White fails here.'),
    ('Red sail on ink', RED, INK, 'The mark in the header and hero. Graphic use, 3:1 is enough'),
    ('Bone on oxblood', BONE, OXB, 'Manifesto copy'),
    ('Dimmed bone (68%) on ink', blend(BONE, INK, .68), INK, 'Secondary text. Never go lower than this'),
    ('Dimmed bone (68%) on oxblood', blend(BONE, OXB, .70), OXB, 'Secondary text on oxblood'),
    ('Dimmed ink (84%) on red', blend(INK, RED, .84), RED, 'Sub-copy on the red finale'),
    ('Red on oxblood (large only)', RED, OXB, 'The "life" accent word in the manifesto. 22px+ only'),
    ('SimpleInvite blue on paper', BLUE, PAPER, 'Header sail and CTA on the SimpleInvite panel'),
    ('White on SimpleInvite blue', '#ffffff', BLUE, 'CTA label'),
    ('Amber on night', AMBER, NIGHT, 'Header sail and CTA on the fdbck panel'),
    ('Night on amber', NIGHT, AMBER, 'fdbck CTA label'),
]
pair_rows = ''.join(
    f'<tr><td><span class="chip" style="background:{bg};color:{fg}">Aa</span></td><th scope="row">{n}</th>'
    f'<td class="num">{ratio(fg, bg):.2f} : 1</td><td>{grade(ratio(fg, bg))}</td><td class="dim">{note}</td></tr>'
    for n, fg, bg, note in pairs)

swatches = ''.join(
    f'<article class="sw" style="background:{bg};color:{fg}"><div><h3>{n}</h3><p class="hex">{bg.upper()}</p></div>'
    f'<p>{role}</p><p class="cr">Text {r1:.1f}:1 &middot; secondary {r2:.1f}:1</p></article>'
    for n, bg, fg, role, r1, r2 in swatch_rows)

def mark_tile(sym, vb, bg, fg, label, size):
    return (f'<figure class="tile" style="background:{bg};color:{fg}">'
            f'{use(sym, vb, "m", f"height:{size}px;width:auto;", label)}<figcaption>{label}</figcaption></figure>')

sizes = ''.join(
    f'<div class="sz"><div class="szrow" style="color:{BONE}">'
    f'{use("mks" if s <= 36 else "mk", VB_MKS if s <= 36 else VB_MK, "m", f"height:{s}px;width:auto;--sail:{RED};fill:{RED}", f"{s}px")}'
    f'</div><p>{s} px<br><span class="dim">{"small cut" if s <= 36 else "display cut"}</span></p></div>'
    for s in (16, 24, 32, 48, 96))

page = f'''<title>Bangarang Brand Sheet</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=Gabarito:wght@700&family=JetBrains+Mono:wght@400;500&family=Young+Serif&family=Hanken+Grotesk:wght@400..600&family=Outfit:wght@600;700&family=DM+Sans:wght@400;500&display=swap">
<style>
/* A brand sheet for a dark brand: it commits to the ink world on purpose, so it is single-theme. */
:root{{--ink:{INK};--oxb:{OXB};--bone:{BONE};--red:{RED};--dim:rgba(238,233,218,.68);--line:rgba(238,233,218,.18);color-scheme:dark}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ink);color:var(--bone);font-family:"Archivo",system-ui,sans-serif;font-size:17px;line-height:1.55;-webkit-font-smoothing:antialiased;padding-inline:max(16px,4vw);padding-block:0}}
.wrap{{max-width:1180px;margin-inline:auto}}
section{{padding-block:clamp(48px,8vw,104px);border-top:1px solid var(--line)}}
section:first-of-type{{border-top:0}}
h1,h2,h3{{margin:0;text-wrap:balance}}
h2{{font-size:clamp(34px,6vw,76px);font-weight:900;text-transform:uppercase;line-height:.9;letter-spacing:-.02em;font-variation-settings:"wdth" 80}}
h3{{font-size:20px;font-weight:700;letter-spacing:-.01em}}
p{{margin:0;max-width:62ch}}
.lab{{font-family:"JetBrains Mono",monospace;font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);display:block;margin-bottom:16px}}
.dim{{color:var(--dim)}}
.lead{{margin-top:20px;font-size:clamp(18px,2vw,22px);color:var(--dim)}}
.grid{{display:grid;gap:16px;margin-top:40px}}
.g2{{grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr))}}
.g4{{grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr))}}
.hero{{padding-top:clamp(32px,5vw,64px)}}
.hero .wm{{display:block;width:100%;height:auto;color:var(--bone);--sail:var(--red);margin-block:clamp(36px,7vw,96px) 24px}}
.hero .row{{display:flex;flex-wrap:wrap;gap:12px 32px;justify-content:space-between;font-family:"JetBrains Mono",monospace;font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim)}}
.tile{{margin:0;min-height:230px;display:grid;place-items:center;gap:16px;padding:28px 16px 16px;border:1px solid var(--line)}}
.tile figcaption{{font-family:"JetBrains Mono",monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;opacity:.8;align-self:end}}
.m,.wmbox svg{{fill:currentColor}}
.m{{display:block}}
.tile .m{{--sail:currentColor}}
.sizes{{display:flex;flex-wrap:wrap;gap:28px 40px;align-items:flex-end;margin-top:40px;padding:32px;border:1px solid var(--line)}}
.sz p{{margin-top:12px;font-family:"JetBrains Mono",monospace;font-size:11px;letter-spacing:.06em;text-transform:uppercase}}
.wmbox{{display:grid;place-items:center;padding:clamp(24px,4vw,56px) clamp(16px,3vw,40px);border:1px solid var(--line);margin:0}}
.wmbox svg{{width:100%;height:auto;display:block}}
.wmbox figcaption{{margin-top:20px;font-family:"JetBrains Mono",monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:inherit;opacity:.8;justify-self:start}}
.lk{{max-width:380px}}
.sw{{min-height:250px;padding:22px;display:flex;flex-direction:column;gap:14px;justify-content:space-between;border:1px solid var(--line)}}
.sw div{{display:flex;justify-content:space-between;gap:12px;align-items:baseline;flex-wrap:wrap}}
.sw p{{font-size:15px;max-width:34ch}}
.hex,.cr{{font-family:"JetBrains Mono",monospace;font-size:12px;letter-spacing:.06em}}
.prod{{padding:28px;border:1px solid var(--line);display:grid;gap:20px;align-content:start}}
.prod .head{{display:flex;align-items:center;gap:14px;flex-wrap:wrap}}
.prod .bar{{display:flex;gap:10px;flex-wrap:wrap}}
.dot{{display:inline-flex;align-items:center;gap:8px;font-family:"JetBrains Mono",monospace;font-size:12px;letter-spacing:.06em}}
.dot i{{width:20px;height:20px;border:1px solid var(--line);display:inline-block}}
.tbl{{overflow-x:auto;margin-top:40px}}
table{{border-collapse:collapse;width:100%;min-width:720px;font-size:15px}}
th,td{{text-align:left;padding:12px 14px;border-bottom:1px solid var(--line);vertical-align:middle}}
thead th{{font-family:"JetBrains Mono",monospace;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);font-weight:500}}
tbody th{{font-weight:600}}
.num{{font-family:"JetBrains Mono",monospace;white-space:nowrap}}
.chip{{display:inline-grid;place-items:center;width:44px;height:30px;font-weight:800;border:1px solid var(--line)}}
.spec{{padding:28px;border:1px solid var(--line);display:grid;gap:14px;align-content:start}}
.spec .big{{font-size:clamp(40px,6vw,76px);line-height:.95}}
.spec .meta{{font-family:"JetBrains Mono",monospace;font-size:12px;letter-spacing:.06em;color:var(--dim)}}
.cols{{display:grid;gap:16px 40px;grid-template-columns:repeat(auto-fit,minmax(min(100%,360px),1fr));margin-top:40px}}
.cols>div{{min-width:0}}
ul.rules{{list-style:none;margin:16px 0 0;padding:0;display:grid;gap:0}}
ul.rules li{{padding:12px 0;border-bottom:1px solid var(--line);max-width:62ch}}
ul.rules b{{font-weight:700}}
.yes,.no{{font-family:"JetBrains Mono",monospace;font-size:11px;letter-spacing:.1em;text-transform:uppercase;margin-right:10px}}
.yes{{color:var(--bone)}} .no{{color:var(--red)}}
.say{{font-size:clamp(22px,2.6vw,32px);font-weight:700;line-height:1.1;letter-spacing:-.015em}}
.files{{font-family:"JetBrains Mono",monospace;font-size:13px;line-height:1.9}}
footer{{padding-block:48px 72px;border-top:1px solid var(--line);color:var(--dim);font-size:14px}}
a{{color:inherit}}
@media (max-width:560px){{.sizes{{padding:20px}}}}
</style>
{symbols}
<div class="wrap">

<section class="hero">
  <span class="lab">Brand sheet &middot; Bangarang Apps, Inc. &middot; October 2026</span>
  {use("wd", VB_WD, "wm", "", "Bangarang")}
  <div class="row"><span>Apps with a little more life in them.</span><span>bangarangapps.com</span></div>
</section>

<section>
  <span class="lab">01 &middot; The mark</span>
  <h2>A sail that<br>is also an A</h2>
  <p class="lead">Three panels in one continuous flow, standing in for the middle A of the name. It is the designer's own artwork rebuilt as clean vectors, not a trace. Uniform scale only: never redraw, stretch, skew, split, recolor pieces, or animate it.</p>
  <div class="grid g4">
    {mark_tile("mk", VB_MK, INK, RED, "Red on ink (primary)", 150)}
    {mark_tile("mk", VB_MK, BONE, INK, "Ink on bone", 150)}
    {mark_tile("mk", VB_MK, RED, INK, "Ink on red", 150)}
    {mark_tile("mk", VB_MK, INK, BONE, "Bone on ink (one color)", 150)}
  </div>
  <div class="sizes" aria-label="Mark at 16 to 96 pixels">{sizes}</div>
  <div class="cols">
    <div><h3>Two optical cuts, one geometry</h3>
      <ul class="rules">
        <li><b>Display cut</b>: gaps as drawn. Hero, print, large uses, 48 px and up.</li>
        <li><b>Small cut</b>: wider gaps (2x), looser tracking, more air after the mark so the R never crowds it. Header, footer, favicon, anything under about 40 px.</li>
        <li>The mark stands 1.3x the cap height and hangs equally above and below the letters.</li>
      </ul></div>
    <div><h3>Construction rules (set by the owner)</h3>
      <ul class="rules">
        <li>The right-hand edges of the cap and the band sit on <b>one straight line</b>; the swoosh's curve starts at the band's sharp top-right corner.</li>
        <li>The two gaps are exactly the same width and parallel for their whole length.</li>
        <li>Proportions and curvature come from the original artwork. 11 Bezier segments, smooth except at true corners.</li>
      </ul></div>
  </div>
</section>

<section>
  <span class="lab">02 &middot; Wordmark and lockups</span>
  <h2>The name with<br>a sail in it</h2>
  <p class="lead">Gabarito Bold outlines, cap height normalized, the mark replacing the middle A. Always set from the supplied files; never retype it in a font.</p>
  <div class="grid g2">
    <figure class="wmbox" style="background:{INK};color:{BONE};--sail:{RED}">{use("wd", VB_WD, "", "", "Bangarang, display cut")}<figcaption>Display cut &middot; on ink</figcaption></figure>
    <figure class="wmbox" style="background:{BONE};color:{INK};--sail:{INK}">{use("wd", VB_WD, "", "", "Bangarang on bone")}<figcaption>On bone &middot; sail goes ink</figcaption></figure>
    <figure class="wmbox" style="background:{RED};color:{INK};--sail:{INK}">{use("wd", VB_WD, "", "", "Bangarang on red")}<figcaption>On red &middot; all ink</figcaption></figure>
    <figure class="wmbox" style="background:{INK};color:{BONE};--sail:{RED}">{use("ws", VB_WS, "", "max-width:420px", "Bangarang, small cut")}<figcaption>Small cut &middot; header, footer, under 40 px tall</figcaption></figure>
    <figure class="wmbox" style="background:{INK};color:{BONE}">{use("wp", VB_WP, "", "", "Bangarang plain, standard A")}<figcaption>Plain (standard A, no mark) &middot; text-only contexts</figcaption></figure>
    <figure class="wmbox" style="background:{INK};color:{BONE}">{use("lk", VB_LK, "lk", "--sail:" + RED, "Bangarang stacked lockup")}<figcaption>Stacked &middot; square formats, social, merch</figcaption></figure>
  </div>
  <div class="cols">
    <div><h3>Clear space and minimums</h3>
      <ul class="rules">
        <li>Keep clear space of one mark-width on every side.</li>
        <li>Wordmark: never under 90 px wide on screen. The mark alone: never under 16 px, and use the small cut below 40 px.</li>
        <li>No exclamation mark, ever. The name is plain BANGARANG.</li>
      </ul></div>
    <div><h3>The header sail follows the product</h3>
      <ul class="rules">
        <li>Brand red everywhere by default.</li>
        <li><span class="dot"><i style="background:{BLUE}"></i>{BLUE}</span> while a SimpleInvite section is under the header.</li>
        <li><span class="dot"><i style="background:{AMBER}"></i>{AMBER}</span> while an fdbck section is under the header.</li>
        <li>The sail changes color between sections as you scroll. The logo itself never animates.</li>
      </ul></div>
  </div>
</section>

<section>
  <span class="lab">03 &middot; Color</span>
  <h2>Highlighter red<br>on warm black</h2>
  <p class="lead">Studio color lives in worlds: a section and the header both read from the same set. Red is the one loud thing. Everything else is warm black and bone. No gradients, no pure white or pure black.</p>
  <div class="grid g4">{swatches}</div>
  <div class="tbl"><table><thead><tr><th scope="col">Sample</th><th scope="col">Pair</th><th scope="col">Contrast</th><th scope="col">Passes</th><th scope="col">Use</th></tr></thead><tbody>{pair_rows}</tbody></table></div>
  <p class="lead dim" style="font-size:15px">Targets: WCAG 2.2 AA (4.5:1 text, 3:1 large text and graphics). Buttons on red use ink text because white fails. Ratios computed from the hex values above.</p>
</section>

<section>
  <span class="lab">04 &middot; Type</span>
  <h2>One workhorse,<br>one label face</h2>
  <p class="lead">The wordmark is Gabarito Bold. The site and everything else the studio publishes is set in Archivo (headings and body) and JetBrains Mono (labels, captions, data). Never Fraunces.</p>
  <div class="grid g2">
    <div class="spec"><span class="lab" style="margin:0">Wordmark &middot; Gabarito Bold</span><div class="big" style="font-family:'Gabarito',sans-serif;font-weight:700">Bangarang</div><p class="meta">Outlines only (SIL OFL). Used for the logo, never for running text.</p></div>
    <div class="spec"><span class="lab" style="margin:0">Headings &middot; Archivo Black, condensed</span><div class="big" style="font-weight:900;text-transform:uppercase;font-variation-settings:'wdth' 80;letter-spacing:-.02em">Say hello.</div><p class="meta">Weight 800-900, width 80-88, uppercase for display, tight tracking (-.02em).</p></div>
    <div class="spec"><span class="lab" style="margin:0">Body &middot; Archivo Regular</span><p style="font-size:20px;font-weight:400">Some app categories got comfortable. We think they deserve a little life: lighter, quicker, genuinely nice to use.</p><p class="meta">17-22 px, line-height 1.5-1.65, 62-66 characters per line.</p></div>
    <div class="spec"><span class="lab" style="margin:0">Labels &middot; JetBrains Mono</span><p style="font-family:'JetBrains Mono',monospace;font-size:13px;letter-spacing:.1em;text-transform:uppercase">The apps &middot; How we work &middot; Say hello</p><p class="meta">11-13 px, uppercase, +.06 to +.1em tracking, always at least 4.5:1.</p></div>
  </div>
</section>

<section>
  <span class="lab">05 &middot; The apps</span>
  <h2>Products keep<br>their own identity</h2>
  <p class="lead">Bangarang is the studio; each app is its own brand and wears its own colors and type on its panel. Identity never crosses between products.</p>
  <div class="grid g2">
    <article class="prod" style="background:{PAPER};color:{PAPER_INK}">
      <div class="head"><svg width="48" height="35" viewBox="0 0 109.948043 79.373756" fill="#111" aria-hidden="true"><use href="#si-mark"/></svg><span style="font-family:'Young Serif',Georgia,serif;font-size:30px">SimpleInvite</span></div>
      <p style="font-family:'Hanken Grotesk',sans-serif">Paper <b>{PAPER}</b> &middot; ink <b>{PAPER_INK}</b> &middot; Young Serif display, Hanken Grotesk body.</p>
      <div class="bar"><span class="dot"><i style="background:#111"></i>Mark: always black #111</span><span class="dot"><i style="background:{BLUE}"></i>CTA blue {BLUE}</span></div>
      <p style="font-family:'Hanken Grotesk',sans-serif;font-size:15px">The mark is SimpleInvite's current envelope, taken from simpleinvite.app, and is never tinted with an accent. The blue is the header sail and CTA while this section is on screen.</p>
    </article>
    <article class="prod" style="background:{NIGHT};color:#fafafa">
      <div class="head"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" aria-hidden="true"><g stroke="#fafafa" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M16.247 7.761a6 6 0 0 1 0 8.478"/><path d="M19.075 4.933a10 10 0 0 1 0 14.134"/><path d="M4.925 19.067a10 10 0 0 1 0-14.134"/><path d="M7.753 16.239a6 6 0 0 1 0-8.478"/></g><circle cx="12" cy="12" r="2" fill="{AMBER}"/></svg><span style="font-family:'Outfit',sans-serif;font-weight:700;font-size:30px;letter-spacing:-.03em">fdbck<span style="color:{AMBER}">.</span></span></div>
      <p style="font-family:'DM Sans',sans-serif">Night <b>{NIGHT}</b> &middot; amber <b>{AMBER}</b> &middot; Outfit display, DM Sans body.</p>
      <div class="bar"><span class="dot"><i style="background:{AMBER}"></i>Accent amber {AMBER}</span></div>
      <p style="font-family:'DM Sans',sans-serif;font-size:15px">Amber is the header sail and CTA while this section is on screen. fdbck's copy never names how it works under the hood on the Bangarang site.</p>
    </article>
  </div>
</section>

<section>
  <span class="lab">06 &middot; Voice</span>
  <h2>Light, quick,<br>a little mischievous</h2>
  <p class="lead">Never smug. We hint that we want to do it better and put some life back into the market, and we never say a word against anyone. Short sentences. No filler sublines.</p>
  <div class="cols">
    <div><h3>How it sounds</h3>
      <p class="say" style="margin-top:20px">Apps with a little more life in them.</p>
      <p class="say" style="margin-top:14px">Some app categories got comfortable.</p>
      <p class="say" style="margin-top:14px">Out now.</p>
      <p class="say" style="margin-top:14px">We read everything.</p></div>
    <div><h3>Rules</h3>
      <ul class="rules">
        <li><span class="yes">Do</span>Say <b>apps</b>. Nobody says software anymore.</li>
        <li><span class="yes">Do</span>Hint at modern tools: "the newest tools we can get our hands on".</li>
        <li><span class="yes">Do</span>Say "Out now" for what is live.</li>
        <li><span class="no">Never</span>State a headcount: no "two of us", no "founders".</li>
        <li><span class="no">Never</span>Frame the lineup as small or unfinished: no "two so far".</li>
        <li><span class="no">Never</span>Mention agents, AI or vibe coding on the Bangarang site.</li>
        <li><span class="no">Never</span>Name or criticize an incumbent.</li>
        <li><span class="no">Never</span>Reference the film or use pirate or nautical language. The name is the only nod.</li>
        <li><span class="no">Never</span>Use an exclamation mark in the brand.</li>
      </ul></div>
  </div>
</section>

<section>
  <span class="lab">07 &middot; Motion and layout</span>
  <h2>It moves as<br>you scroll</h2>
  <div class="cols">
    <div><h3>Motion</h3>
      <ul class="rules">
        <li><span class="yes">Do</span>Scroll-linked: words light up in the manifesto, strips drift sideways, product shots parallax, sections reveal.</li>
        <li><span class="yes">Do</span>Horizontal and vertical movement only. Reduced motion means a static, fully readable page.</li>
        <li><span class="no">Never</span>Animate the logo: no squish, stretch, morph or color sweep.</li>
      </ul></div>
    <div><h3>Layout and imagery</h3>
      <ul class="rules">
        <li><span class="no">Never</span>Tilt, skew, stack or overlap elements. No fake materials: no tape, torn edges, perforations.</li>
        <li><span class="no">Never</span>Gradients, Fraunces, stock imagery or placeholder shots.</li>
        <li><span class="yes">Do</span>Real captures of the live products at 2x; re-capture when their UI changes.</li>
        <li><span class="yes">Do</span>Anchor links land flush so the header takes the section's color immediately.</li>
      </ul></div>
  </div>
</section>

<section>
  <span class="lab">08 &middot; Files and facts</span>
  <h2>Where everything is</h2>
  <div class="cols">
    <div><h3>Logo files</h3>
      <p class="files">assets/brand/mark.svg &middot; mark-small.svg<br>assets/brand/wordmark.svg &middot; wordmark-small.svg<br>assets/brand/wordmark-plain.svg<br>assets/brand/lockup-stacked.svg<br>assets/brand/icon-large.svg<br>favicon.svg &middot; apple-touch-icon.png &middot; og.png</p>
      <p class="dim" style="margin-top:14px;font-size:15px">All generated by <span class="num">tools/construct.py</span> and <span class="num">tools/wordmark.py</span>. Never hand-edit them; change the constants and regenerate.</p></div>
    <div><h3>The company</h3>
      <ul class="rules">
        <li><b>Bangarang Apps, Inc.</b>, a Delaware corporation.</li>
        <li>General: contact@bangarangapps.com</li>
        <li>Billing and refunds: help@bangarangapps.com</li>
        <li>Something broken: support@bangarangapps.com</li>
        <li>Site: bangarangapps.com &middot; products: simpleinvite.app, fdbck.app</li>
      </ul></div>
  </div>
</section>

<footer>Generated from the shipped brand files by <span class="num">tools/sheet.py</span>. Source of truth: <span class="num">docs/BRAND.md</span>.</footer>
</div>
'''
# the SimpleInvite mark is shared by <use>; define it once (current path from index.html)
si = re.search(r'<svg width="44" height="32" viewBox="0 0 109\.948043 79\.373756"[^>]*><path d="([^"]+)"', (ROOT / 'index.html').read_text()).group(1)
page = page.replace('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><symbol id="mk"',
                    f'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><symbol id="si-mark" viewBox="0 0 109.948043 79.373756"><path fill-rule="evenodd" d="{si}"/></symbol><symbol id="mk"', 1)
(ROOT / 'docs' / 'brand-sheet.html').write_text(page)
print('wrote docs/brand-sheet.html', len(page))
