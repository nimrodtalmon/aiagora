#!/usr/bin/env python3
"""Builds web/brief/index.html: research brief on the scale paradox (a broadcast
channel vs agent routing for forming groups; deterministic worst-case model).
Uses the shared kit (web/kit.py) and the exact counts in runs/scale.csv and
runs/scale_windows.csv (experiments/scale.py).

    python3 web/brief/src/build.py
"""
import csv, importlib.util, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
_spec = importlib.util.spec_from_file_location('kit', os.path.join(HERE, '..', '..', 'kit.py'))
kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kit)
svg, text, head = kit.svg, kit.text, kit.head
OR, DK, GR, GL, CARD = kit.OR, kit.DK, kit.GR, kit.GL, kit.CARD
I = M = kit.I
STYLE = kit.STYLE.replace('</style>', '''.split.wide { grid-template-columns: 1.3fr 0.7fr; }
.ev { display: grid; grid-template-columns: 1fr 1fr; gap: 28px 36px; margin-top: 10px; }
.ev .tile { background: var(--card); border: 3px solid var(--gray-light); border-radius: 24px; padding: 26px 32px; }
.ev .big { font-size: 64px; font-weight: 800; color: var(--orange); line-height: 1.05; }
.ev .q { font-size: 34px; font-weight: 700; line-height: 1.25; margin-top: 8px; }
.ev .src { font-size: 26px; color: var(--gray); margin-top: 10px; }
</style>''')
OUT = os.path.join(HERE, '..', 'index.html')
DATE = 'November 18, 2026'

RUNS = list(csv.DictReader(open(os.path.join(ROOT, 'runs', 'scale.csv'))))
WIN = list(csv.DictReader(open(os.path.join(ROOT, 'runs', 'scale_windows.csv'))))
K, R = 4, 150


def thm(*a, wide=False, **kw):
    out = kit.thm(*a, **kw)
    return out.replace('class="split"', 'class="split wide"') if wide else out


# ---------- pictures ----------
def channel_vis():
    """Broadcast reaches everyone; the agora reaches the likely yes."""
    w, h = 1500, 560
    rng_acc = [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0]
    est = [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]      # agents' guesses (one wrong each way)
    b = ''
    for c, (cx, name) in enumerate([(370, 'broadcast'), (1130, 'agora')]):
        cy, R = 250, 200
        pts = [(cx + R * math.cos(2 * math.pi * i / 16), cy + R * math.sin(2 * math.pi * i / 16)) for i in range(16)]
        for i, (x, y) in enumerate(pts):
            reach = c == 0 or est[i]
            if reach:
                b += f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" stroke="{OR if rng_acc[i] else GL}" stroke-width="{5 if rng_acc[i] else 3}"/>'
        for i, (x, y) in enumerate(pts):
            b += head(x, y, 17, OR if rng_acc[i] else GL)
        b += head(cx, cy, 24, DK)
        b += text(cx, 520, name, 44, DK, weight=800)
    return svg(w, h, b)


NMIN, NMAX = 4, 20000


def _lx(n, X0, X1, nmax=NMAX):
    return X0 + (math.log(min(n, nmax)) - math.log(NMIN)) / (math.log(nmax) - math.log(NMIN)) * (X1 - X0)


def _xaxis(X0, X1, Y0, label=True, nmax=NMAX):
    b = ''
    for n in (4, 10, 40, 100, 400, 1000, 4000, 20000):
        if n <= nmax:
            b += text(_lx(n, X0, X1, nmax), Y0 + 38, f'{n:,}', 24, GR)
    if label:
        b += text((X0 + X1) / 2, Y0 + 80, 'community size n (members)', 28, GR, weight=700)
    return b


def windows_vis(kind, rows=24, w=1000, nmax=1000):
    """One row per type (largest share on top): the sizes n at which it forms."""
    X0, X1, top, rh = 150, w - 30, 30, 20
    lx = lambda n: _lx(n, X0, X1, nmax)
    Y0 = top + rows * rh + 8
    b = f'<line x1="{X0}" y1="{Y0}" x2="{X1}" y2="{Y0}" stroke="{GL}" stroke-width="2"/>'
    thr_drawn = False
    for r in WIN[:rows]:
        t, s = int(r['t']), float(r['share'])
        y = top + (t - 1) * rh
        if kind == 'broadcast':
            if r['b_lo']:
                x0, x1 = lx(int(r['b_lo'])), lx(int(r['b_hi']))
                b += f'<rect x="{x0:.0f}" y="{y+3}" width="{max(6, x1-x0):.0f}" height="{rh-6}" rx="4" fill="{DK}"/>'
            elif not thr_drawn:
                thr_drawn = True
                b += f'<line x1="{X0}" y1="{y-1}" x2="{X1}" y2="{y-1}" stroke="{OR}" stroke-width="3" stroke-dasharray="10 8"/>'
                b += text(X0 + 10, y + 30, 'below the line:', 24, OR, 'start', 700)
                b += text(X0 + 10, y + 58, 'never forms', 24, OR, 'start', 700)
        else:
            x0 = lx(int(r['agora10_from']))
            b += f'<rect x="{x0:.0f}" y="{y+3}" width="{X1-x0:.0f}" height="{rh-6}" rx="4" fill="{OR}"/>'
    b += text(X0 - 14, top + 14, 'share 0.5', 22, GR, 'end')
    b += text(X0 - 14, top + (rows - 1) * rh + 14, f'0.5/{rows}', 22, GR, 'end')
    b += text(40, top + rows * rh / 2, 'types', 26, GR, weight=700, extra=f'transform="rotate(-90 40 {top + rows*rh/2})"')
    b += _xaxis(X0, X1, Y0, nmax=nmax)
    return svg(w, Y0 + 92, b)


def counts_vis(w=1000, h=640):
    X0, X1, Y0, Y1 = 120, w - 200, 540, 50
    YM = 300
    Y = lambda v: Y0 - v / YM * (Y0 - Y1)
    b = ''
    for v in (0, 100, 200, 300):
        b += f'<line x1="{X0}" y1="{Y(v):.0f}" x2="{X1}" y2="{Y(v):.0f}" stroke="#E6E5E0" stroke-width="2"/>'
        b += text(X0 - 14, Y(v) + 9, str(v), 24, GR, 'end')
    b += _xaxis(X0, X1, Y0)
    b += text(30, (Y0 + Y1) / 2, 'groups formed', 26, GR, weight=700, extra=f'transform="rotate(-90 30 {(Y0+Y1)/2})"')
    for key, col, lab in (('agora_err0', OR, 'agora, err = 0'), ('agora_err10', '#E8B07A', 'agora, err = 10'), ('broadcast', DK, 'broadcast')):
        pts = [(_lx(int(r['n']), X0, X1), Y(float(r[key]))) for r in RUNS]
        b += f'<polyline fill="none" stroke="{col}" stroke-width="5" stroke-linejoin="round" points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + '"/>'
        if key == 'broadcast':
            x, y = pts[-1]
            b += text(x + 14, y + 9, lab, 26, DK, 'start', 700)
        else:
            tgt = 150 if key == 'agora_err0' else 100
            r = next(r for r in RUNS if float(r[key]) >= tgt)
            x, y = _lx(int(r['n']), X0, X1), Y(float(r[key]))
            b += text(x - 14 if key == 'agora_err0' else x + 14, y, lab, 26, DK, 'end' if key == 'agora_err0' else 'start', 700)
    return svg(w, h, b)


def evidence():
    tiles = [('62%', 'named “spamming a large audience” as the top reason not to post', 'large mailing lists · Zhang, Ackerman, Karger, CHI 2015'),
             ('38%', 'of self-censored posts: group posts, the highest of any location', '3.9M Facebook users · Das &amp; Kramer, ICWSM 2013'),
             ('“too large”', 'neighborhoods got “too large to post the things they wanted to say”', 'Nextdoor interviews · Masden et al., CHI 2014'),
             ('mute', 'muting is the main way people cope with WhatsApp groups', 'Dutch WhatsApp users · Mols &amp; Pridmore, 2020')]
    return '<div class="ev">' + ''.join(
        f'<div class="tile"><div class="big">{a}</div><div class="q">{q}</div><div class="src">{s}</div></div>' for a, q, s in tiles) + '</div>'


def related_vis():
    boxes = [('Attention as a commons', 'Anderson &amp; de Palma 2009 (RAND)', 'senders over-use readers’ attention; no groups, no size result'),
             ('Niche crowding', 'Falkinger 2005 (IZA working paper)', 'larger reach raises the bar to be noticed; no groups'),
             ('Critical mass', 'Oliver &amp; Marwell 1988 (ASR)', 'larger groups reach k; the few must “find one another” — in words'),
             ('Group activity selection', 'Darmann et al. 2018 (IJGT)', 'groups with lower size bounds; finding members is free')]
    return '<div class="rw">' + ''.join(
        f'<div class="box"><h3>{t}</h3><p class="who">{w}</p><p class="diff">{x}</p></div>' for t, w, x in boxes) + '</div>'


# ---------- slides ----------
TITLE = f'''<section class="slide dark center">
  <p class="eyebrow">AI-Agora</p>
  <h1>The Scale Paradox</h1>
  <p class="big">Bigger group chats form fewer groups, unless agents route</p>
  <p class="muted">Nimrod Talmon · Ben-Gurion University · draft, {DATE}</p>
</section>'''

slides = [TITLE]
S = slides.append
n, k, B, c, err = I('n'), I('k'), I('B'), I('c'), I(r'\mathit{err}')

S(f"""<section class="slide light">
  <p class="eyebrow">Motivation</p>
  <h2>A neighborhood chat: too big to post in</h2>
  <p class="sub">Every post costs every reader attention; niche ideas are not posted.</p>
  {evidence()}
</section>""")

S(thm('Model', f'Initiatives that need {k} members',
      f"""<p>{n} members. For each type {M('t')}, {M('a_t')} members accept it (the set {M('A_t')}); one is its <b>initiator</b>.</p>
<p>The group forms if at least {k} members of {M('A_t')} are reached; a reached non-member of {M('A_t')} is <b>bothered</b>.</p>
<p>Gain {B} if it forms; cost {c} per bothered. Knowing {M('a_t')}, the initiator announces iff, in the worst case, it forms and {M(r'B \ge c \cdot \text{bothered}')}.</p>""",
      f'<b>Welfare:</b> groups formed. The cost {c} is social: fear of spamming.',
      kit.card_vis(), wide=True))

S(thm('Model', 'Two channels, and a growing community',
      f"""<p><b>Broadcast:</b> an announcement reaches all other {M('n-1')} members.</p>
<p><b>Agora:</b> agents guess whether their members accept {M('t')}; at most {err} guesses per type are wrong. The initiator's agent invites members guessed to accept, in any order, until {M('k-1')} accept.</p>
<p><b>Growing community:</b> type {M('t')} has a share {M('s_t')}; with {n} members, {M(r'a_t = \lfloor s_t n \rfloor')}.</p>""",
      'Orange: accepts. In the agora, two guesses are wrong.',
      channel_vis(), stack=True, pic_h=210))

S(thm('Theorem 1', 'Broadcast: each type forms only in a window',
      f"""<p>In broadcast, type {M('t')} forms iff {M(r'a_t \ge k')} and {M(r'n - a_t \le \tfrac{B}{c}')}.</p>
<p>So a type with share {M('s')} forms only for {n} in an interval inside {M(r'\big[\tfrac{k}{s}, \tfrac{B}{c(1-s)}\big]')}.</p>
<p>If {M(r's < \tfrac{k}{k+B/c}')}, it never forms.</p>""",
      f"<p>It bothers exactly {M(r'n - a_t')} members; both conditions are monotone.</p>",
      windows_vis('broadcast')))

S(thm('Theorem 2', f'Agora: once a type forms, it keeps forming',
      f"""<p>In the agora, type {M('t')} forms iff {M(r'a_t \ge k + \mathit{err}')} and {M(r'c \cdot \min(\mathit{err},\, n - a_t) \le B')}.</p>
<p>So if {M(r'\mathit{err} \le \tfrac{B}{c}')}, a type with share {M('s')} forms for every {M(r'n \ge \tfrac{k+\mathit{err}}{s}')}.</p>""",
      f"<p>Always {M('k-1')} acceptors invited, at most {err} members bothered; both bounds tight.</p>",
      windows_vis('agora')))

S(thm('Example', 'Broadcast peaks and dies; the agora grows',
      f"""<p>300 types with shares {M(r's_t = \tfrac{0.5}{t}')}, and {M('k=4')}, {M(r'\tfrac{B}{c} = 150')}.</p>
<p><b>Broadcast:</b> 19 types ever form; at most 19 groups (152–154 members); none above 300.</p>
<p><b>Agora:</b> all 300 from 2,400 members; with {M(r'\mathit{err} = 10')}, from 8,400.</p>""",
      '<p>Exact counts. Theorems checked by brute force: 1,215 small cases.</p>',
      counts_vis()))

S(f'''<section class="slide light">
  <p class="eyebrow">Related work</p>
  <h2>Closest work, and the difference</h2>
  {related_vis()}
  <p class="why" style="margin-top:30px">New here: threshold groups found through one channel whose cost falls on all members; the number of groups as a function of community size.</p>
</section>''')

S('''<section class="slide light">
  <p class="eyebrow">Summary</p>
  <h2>Broadcast cost grows with \\(n\\); agora cost does not</h2>
  <div class="rows ruled">
    <div class="row"><span class="n">1</span><p>Broadcast: each type forms only in a window of sizes; niche types never</p></div>
    <div class="row"><span class="n">2</span><p>Agora: once a type forms, it keeps forming; wrong guesses only delay it</p></div>
    <div class="row"><span class="n">3</span><p>Open: initiators and members as players (post, mute); invitation budgets</p></div>
    <div class="row"><span class="n">4</span><p>Next: federation — try locally, escalate only when needed</p></div>
  </div>
</section>''')

slides.append(TITLE)

html = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Scale Paradox · AI-Agora</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@300..900&display=swap">
<link rel="stylesheet" href="../assets/deck.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/auto-render.min.js"></script>
''' + kit.KATEX_INIT + '\n' + STYLE + '''
</head>
<body>
<div id="stage">
''' + '\n'.join(f'<!-- {i+1} -->{s}' for i, s in enumerate(slides)) + '''
</div>
<script src="../assets/deck.js"></script>
</body>
</html>
'''
open(OUT, 'w').write(html)
print(len(slides), 'slides')
