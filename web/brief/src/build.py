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
.ev.three { grid-template-columns: 1fr 1fr 1fr; margin-top: 40px; }
.ev.three .big { font-size: 96px; }
.ev.three .q { font-size: 40px; }
.ev.three .src { font-size: 28px; }
.try-row { display: grid; grid-template-columns: 1fr 1fr; gap: 50px; margin-top: 6px; }
.try-col svg { width: 100%; height: auto; }
.try-h { font-size: 40px; margin: 0 0 6px; }
.try-h b { color: var(--orange); font-size: 52px; }
.try-n { font-size: 34px; color: var(--gray); margin-top: 6px; }
.try-n span { color: var(--dark); font-weight: 800; }
.two-cap { display: grid; grid-template-columns: 1fr 1fr; text-align: center; font-size: 38px; margin-top: -10px; }
.two-cap p { margin: 0; } .two-cap b { color: var(--orange); }
.try-col svg { max-height: 430px; }
.chan svg { max-height: 500px; width: auto; }
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
def channel_vis(caps=None):
    """Broadcast reaches everyone; the agora reaches the likely yes."""
    w, h = 1500, 560 + (80 if caps else 0)
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
        if caps:
            b += f'<text x="{cx}" y="600" font-size="40" text-anchor="middle" fill="{DK}">{caps[c][0]} <tspan font-weight="800" fill="{OR}">{caps[c][1]}</tspan></text>'
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


def windows_vis(kind, rows=24, w=1000, nmax=1000, line_id=None):
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
                b += text(X0 + 10, y + 58, 'never happens', 24, OR, 'start', 700)
        else:
            x0 = lx(int(r['agora0_from']))
            b += f'<rect x="{x0:.0f}" y="{y+3}" width="{X1-x0:.0f}" height="{rh-6}" rx="4" fill="{OR}"/>'
    b += text(X0 - 14, top + 14, 'share 0.5', 22, GR, 'end')
    b += text(X0 - 14, top + (rows - 1) * rh + 14, f'0.5/{rows}', 22, GR, 'end')
    b += text(40, top + rows * rh / 2, 'activities', 26, GR, weight=700, extra=f'transform="rotate(-90 40 {top + rows*rh/2})"')
    b += _xaxis(X0, X1, Y0, nmax=nmax)
    if line_id:
        b += f'<line id="{line_id}" x1="{X0}" y1="{top - 10}" x2="{X0}" y2="{Y0}" stroke="{OR if kind == "broadcast" else DK}" stroke-width="5"/>'
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
    b += text(30, (Y0 + Y1) / 2, 'activities that happen', 26, GR, weight=700, extra=f'transform="rotate(-90 30 {(Y0+Y1)/2})"')
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
    tiles = [('62%', 'of a 4,147-member mailing list: “spamming a large audience” deters posting, the most troubling issue', 'Zhang, Ackerman, Karger, CHI 2015'),
             ('most', 'posts to groups and status updates are the most self-censored ways to share', '3.9M Facebook users · Das &amp; Kramer, ICWSM 2013'),
             ('mute', 'many respondents mute WhatsApp groups to cope with communication overload', '43 respondents · Mols &amp; Pridmore, Mobile Media &amp; Comm. 2020')]
    return '<div class="ev three">' + ''.join(
        f'<div class="tile"><div class="big">{a}</div><div class="q">{q}</div><div class="src">{s}</div></div>' for a, q, s in tiles) + '</div>'


def related_vis():
    boxes = [('Attention as a commons', 'Anderson &amp; de Palma 2009 (RAND)', 'senders over-use readers’ attention; no groups'),
             ('Niche crowding', 'Falkinger 2005 (IZA working paper)', 'larger reach raises the bar to be noticed; no groups'),
             ('Critical mass', 'Oliver &amp; Marwell 1988 (ASR)', 'big groups reach k, if the few “find one another”'),
             ('Group activity selection', 'Darmann et al. 2012 (WINE)', 'minimum group sizes; a planner knows all')]
    return '<div class="rw">' + ''.join(
        f'<div class="box"><h3>{t}</h3><p class="who">{w}</p><p class="diff">{x}</p></div>' for t, w, x in boxes) + '</div>'



TRY = f'''<section class="slide light tryit">
  <p class="eyebrow">Example</p>
  <h2>Grow the community: press 1 and 2</h2>
  <p class="sub">300 activities; activity \\(t\\) interests a share \\(\\tfrac{{0.5}}{{t}}\\) of members; \\(k=4\\), \\(\\mathit{{tol}}=150\\), \\(\\mathit{{err}}=0\\).</p>
  <p class="try-n"><span id="try-n">n = 40</span> members &nbsp;·&nbsp; 1 = smaller, 2 = larger &nbsp;·&nbsp; bars: the 24 most popular activities</p>
  <div class="interactive try-row">
    <div class="try-col"><p class="try-h">Broadcast: <b id="cnt-b">0</b> of 300 happen</p>{windows_vis('broadcast', line_id='ln-b')}</div>
    <div class="try-col"><p class="try-h">Agora: <b id="cnt-a">0</b> of 300 happen</p>{windows_vis('agora', line_id='ln-a')}</div>
  </div>
</section>'''

# ---------- slides ----------
TITLE = f'''<section class="slide dark center">
  <p class="eyebrow">AI-Agora</p>
  <h1>The Scale Paradox</h1>
  <p class="big">Bigger group chats form fewer groups, unless agents route</p>
  <p class="muted">Nimrod Talmon · Ben-Gurion University · draft, {DATE}</p>
</section>'''

slides = [TITLE]
S = slides.append
n, k, err, tol = I('n'), I('k'), I(r'\mathit{err}'), I(r'\mathit{tol}')

S(f"""<section class="slide light">
  <p class="eyebrow">Motivation</p>
  <h2>A neighborhood chat: too big to post in</h2>
  <p class="sub">Every post costs every reader attention; niche ideas are not posted.</p>
  {evidence()}
</section>""")

S(thm('Model', f'An activity needs {k} people',
      f"""<p>A community of {n} members. Each activity interests some of them, and happens only if at least {k} interested members hear of it.</p>
<p>Hearing of an activity you are not interested in <b>bothers</b> you.</p>
<p>The initiator knows how many are interested, not who. It posts only if, in the worst case, the activity happens and at most {tol} members are bothered.</p>""",
      f'<b>Welfare:</b> number of activities that happen. {tol}: the tolerance.',
      kit.card_vis(), wide=True))

S(f"""<section class="slide light">
  <p class="eyebrow">Model</p>
  <h2>Two ways to post</h2>
  <div class="box" style="margin-top:20px">
<p><b>Broadcast:</b> everyone hears.</p>
<p><b>Agora:</b> each agent guesses whether its member is interested; per activity, at most {err} guesses are wrong. Agents tell the members guessed interested, one by one, until {M('k-1')} say yes.</p>
<p><b>Growing community:</b> each activity interests a fixed share {M('s')} of the members.</p>
  </div>
</section>""")

S(f"""<section class="slide light">
  <p class="eyebrow">Example</p>
  <h2>One activity, two ways to post</h2>
  <p class="sub">17 members, 5 interested (orange; the initiator in the middle); {M('k=3')}, {M(r'\mathit{{tol}}=5')}.</p>
  <div class="vis chan">{channel_vis((('bothers 12 &gt; 5:', 'not posted'), ('bothers at most 2:', 'it happens')))}</div>
  <p class="why" style="text-align:center;margin-top:0">In the agora, two guesses are wrong: one interested member is missed, one other is invited.</p>
</section>""")

S(thm('Theorem 1', 'Broadcast: each activity has a window of sizes',
      f"""<p>In broadcast, an activity happens iff at least {k} members are interested and at most {tol} are not.</p>
<p>With share {M('s')}, it happens only for</p>
<p class="eq">{M(r'\tfrac{k}{s} \ \le\ n \ \le\ \tfrac{\mathit{tol}}{1-s}')}</p>
<p>and never if {M(r's < \tfrac{k}{k+\mathit{tol}}')}.</p>""",
      f"<p>All uninterested are bothered. E.g., share 10%, {M('k=4')}, {M(r'\mathit{tol}=50')}: {M('n')} from 40 to 55.</p>",
      windows_vis('broadcast')))

S(thm('Theorem 2', 'Agora: once an activity can happen, it always can',
      f"""<p>In the agora, if {M(r'\mathit{err} \le \mathit{tol}')}, an activity happens iff at least {M(r'k+\mathit{err}')} members are interested.</p>
<p>With share {M('s')}, it happens for every</p>
<p class="eq">{M(r'n \ \ge\ \tfrac{k+\mathit{err}}{s}')}</p>""",
      f"<p>Only wrongly guessed members are bothered: at most {err}, for every {n}. The same holds if agents filter what their members see.</p>",
      windows_vis('agora'), f"With {M(r'\mathit{err}=0')}: each bar starts where broadcast's does, and never ends."))

S(TRY)

S(thm('Example', 'Broadcast peaks and dies; the agora grows',
      f"""<p>300 activities; activity {M('t')} has share {M(r'\tfrac{0.5}{t}')}. Also {M('k=4')}, {M(r'\mathit{tol}=150')}.</p>
<p><b>Broadcast:</b> 19 activities ever happen, at most 19 at once (152–154 members), none above 300 members.</p>
<p><b>Agora:</b> all 300 from 2,400 members; with {M(r'\mathit{err}=10')}, from 8,400.</p>""",
      '<p>Exact counts. Both theorems checked by brute force: 1,215 small cases.</p>',
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
    <div class="row"><span class="n">1</span><p>Broadcast: each activity happens only in a window of sizes; niche ones never</p></div>
    <div class="row"><span class="n">2</span><p>Agora: once an activity can happen, it always can; wrong guesses only delay it</p></div>
    <div class="row"><span class="n">3</span><p>Open: initiators and members as players (post, mute); invitation budgets</p></div>
    <div class="row"><span class="n">4</span><p>Next: federation — try locally, escalate only when needed</p></div>
  </div>
</section>''')

slides.append(TITLE)

TRY_JS = '''<script>
(function () {
  const NS = [4, 6, 8, 10, 14, 20, 28, 40, 56, 70, 84, 100, 120, 140, 152, 170, 200, 250, 300, 400, 600, 1000];
  const K = 4, TOL = 150, ERR = 0, T = 300, X0 = 150, X1 = 970, NMIN = 4, NMAX = 1000;
  let idx = 7;
  const slide = document.querySelector('.slide.tryit');
  const lx = n => X0 + (Math.log(n) - Math.log(NMIN)) / (Math.log(NMAX) - Math.log(NMIN)) * (X1 - X0);
  function draw() {
    const n = NS[idx]; let b = 0, a = 0;
    for (let t = 1; t <= T; t++) {
      const m = Math.floor(0.5 * n / t + 1e-9);
      if (m >= K && n - m <= TOL) b++;
      if (m >= K + ERR && Math.min(ERR, n - m) <= TOL) a++;
    }
    document.getElementById('cnt-b').textContent = b;
    document.getElementById('cnt-a').textContent = a;
    document.getElementById('try-n').textContent = 'n = ' + n.toLocaleString('en-US');
    for (const id of ['ln-b', 'ln-a']) { const l = document.getElementById(id); l.setAttribute('x1', lx(n)); l.setAttribute('x2', lx(n)); }
  }
  document.addEventListener('keydown', e => {
    if (!slide.classList.contains('active') || e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === '1') { idx = Math.max(0, idx - 1); draw(); }
    if (e.key === '2') { idx = Math.min(NS.length - 1, idx + 1); draw(); }
  });
  draw();
})();
</script>'''

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
''' + TRY_JS + '''
</body>
</html>
'''
open(OUT, 'w').write(html)
print(len(slides), 'slides')
