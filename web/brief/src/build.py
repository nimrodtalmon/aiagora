#!/usr/bin/env python3
"""Builds web/brief/index.html: research brief on conditional commitments
(group chat vs agents that hold everyone's conditions). Uses the shared kit
(web/kit.py), the exhaustive checks in experiments/commit_check.py and the runs in
runs/neighborhood_*.csv (experiments/neighborhood_sim.py).

    python3 web/brief/src/build.py
"""
import base64, csv, importlib.util, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
_spec = importlib.util.spec_from_file_location('kit', os.path.join(HERE, '..', '..', 'kit.py'))
kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kit)
svg, text, head = kit.svg, kit.text, kit.head
OR, DK, GR, GL, CARD = kit.OR, kit.DK, kit.GR, kit.GL, kit.CARD
I = M = kit.I
OUT = os.path.join(HERE, '..', 'index.html')
DATE = 'November 21, 2026'
EAGER = list(csv.DictReader(open(os.path.join(ROOT, 'runs', 'neighborhood_eager.csv'))))
SIZE = list(csv.DictReader(open(os.path.join(ROOT, 'runs', 'neighborhood_n.csv'))))
APP = base64.b64encode(open(os.path.join(HERE, 'app.jpg'), 'rb').read()).decode()
TH = [0, 2, 2, 3, 4, 4, 4, 5, 5, 6, 6, 9]          # the Theorem 4 example (12 members)

STYLE = kit.STYLE.replace('</style>', '''.split.wide { grid-template-columns: 1.3fr 0.7fr; }
.shot { display: block; margin: 14px auto 0; height: 540px; border: 3px solid var(--gray-light); border-radius: 18px; }
</style>''')


def thm(*a, wide=False, **kw):
    out = kit.thm(*a, **kw)
    return out.replace('class="split"', 'class="split wide"') if wide else out


# ---------- pictures ----------
def ten_vis():
    """Ten people, each 'if 3 others come': the chat stays empty, the agora forms all ten."""
    w, h = 1500, 420
    b = ''
    for c, (x0, name, cap) in enumerate([(60, 'group chat', 'nobody goes first: 0'), (800, 'agora', 'all ten, together')]):
        for i in range(10):
            x = x0 + 30 + (i % 5) * 120; y = 70 + (i // 5) * 160
            b += head(x + 30, y + 20, 22, OR if c else GL)
            b += text(x + 30, y + 120, 'if 3', 28, GR)
        if c:
            b += f'<rect x="{x0 + 10}" y="20" width="620" height="335" rx="30" fill="none" stroke="{OR}" stroke-width="5"/>'
        b += text(x0 + 330, 390, f'{name}: {cap}', 36, DK, weight=800)
    return svg(w, h, b)


def granovetter_vis():
    """H(c) = members ready once c others are in, against the diagonal."""
    n = len(TH)
    w, h = 900, 640
    X0, X1, Y0, Y1 = 110, 840, 540, 50
    X = lambda c: X0 + c / n * (X1 - X0)
    Y = lambda v: Y0 - v / n * (Y0 - Y1)
    b = ''
    for v in range(0, n + 1, 3):
        b += f'<line x1="{X0}" y1="{Y(v):.0f}" x2="{X1}" y2="{Y(v):.0f}" stroke="#E6E5E0" stroke-width="2"/>'
        b += text(X0 - 14, Y(v) + 9, str(v), 24, GR, 'end')
        b += text(X(v), Y0 + 36, str(v), 24, GR)
    b += text((X0 + X1) / 2, Y0 + 80, 'members already in', 28, GR, weight=700)
    b += text(36, (Y0 + Y1) / 2, 'members ready to join', 28, GR, weight=700, extra=f'transform="rotate(-90 36 {(Y0+Y1)/2})"')
    b += f'<line x1="{X(0)}" y1="{Y(0)}" x2="{X(n)}" y2="{Y(n)}" stroke="{GL}" stroke-width="3" stroke-dasharray="10 8"/>'
    pts = []
    for c in range(n + 1):
        v = sum(t <= c for t in TH)
        pts += [(X(c), Y(v)), (X(c + 1) if c < n else X(c), Y(v))]
    b += '<polyline fill="none" stroke="' + DK + '" stroke-width="5" points="' + ' '.join(f'{x:.0f},{y:.0f}' for x, y in pts) + '"/>'
    b += f'<circle cx="{X(1):.0f}" cy="{Y(1):.0f}" r="14" fill="{DK}"/>'
    b += text(X(1) + 26, Y(1) - 18, 'chat stops: 1', 28, DK, 'start', 800)
    b += f'<circle cx="{X(12):.0f}" cy="{Y(12):.0f}" r="14" fill="{OR}"/>'
    b += text(X(12) - 24, Y(12) + 44, 'agora: 12', 28, OR, 'end', 800)
    return svg(w, h, b)


def lines_vis(rows, xkey, xlab, xs_label, w=1000, h=620, logx=False):
    X0, X1, Y0, Y1 = 120, w - 170, 520, 50
    xs = [float(r[xkey]) for r in rows]
    if logx:
        lo, hi = math.log(xs[0]), math.log(xs[-1]); X = lambda x: X0 + (math.log(x) - lo) / (hi - lo) * (X1 - X0)
    else:
        lo, hi = xs[0], xs[-1]; X = lambda x: X0 + (x - lo) / (hi - lo) * (X1 - X0)
    Y = lambda v: Y0 - v * (Y0 - Y1)
    b = ''
    for v in (0, .25, .5, .75, 1):
        b += f'<line x1="{X0}" y1="{Y(v):.0f}" x2="{X1}" y2="{Y(v):.0f}" stroke="#E6E5E0" stroke-width="2"/>'
        b += text(X0 - 14, Y(v) + 9, f'{int(v*100)}%', 24, GR, 'end')
    for x, lab in xs_label:
        b += text(X(x), Y0 + 36, lab, 24, GR)
    b += text((X0 + X1) / 2, Y0 + 80, xlab, 28, GR, weight=700)
    b += text(30, (Y0 + Y1) / 2, 'interested members placed', 26, GR, weight=700, extra=f'transform="rotate(-90 30 {(Y0+Y1)/2})"')
    for key, col, lab in (('exact', OR, 'agora'), ('board', DK, 'group chat')):
        pts = [(X(float(r[xkey])), Y(float(r[key]) / float(r['interested']))) for r in rows]
        b += f'<polyline fill="none" stroke="{col}" stroke-width="5" points="' + ' '.join(f'{x:.0f},{y:.0f}' for x, y in pts) + '"/>'
        for x, y in pts:
            b += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="7" fill="{col}" stroke="#fff" stroke-width="2"/>'
        x, y = pts[-1]
        b += text(x + 14, y + 9, lab, 26, DK, 'start', 700)
    return svg(w, h, b)


def related_vis():
    boxes = [('Threshold models', 'Granovetter 1978 (AJS)', 'each joins once enough others did; the cascade stops early'),
             ('Assurance contracts', 'Tabarrok 1998 (Public Choice)', 'one common threshold, run by an entrepreneur'),
             ('Critical mass', 'Oliver &amp; Marwell 1988 (ASR)', 'the few interested must “find one another”'),
             ('Group activity selection', 'Darmann et al. 2012 (WINE)', 'a planner knows all; our problem is a special case')]
    return '<div class="rw">' + ''.join(
        f'<div class="box"><h3>{t}</h3><p class="who">{w}</p><p class="diff">{x}</p></div>' for t, w, x in boxes) + '</div>'


# ---------- slides ----------
TITLE = f'''<section class="slide dark center">
  <p class="eyebrow">AI-Agora</p>
  <h1>Who Goes First?</h1>
  <p class="big">Conditional commitments in a group chat and in an agora</p>
  <p class="muted">Nimrod Talmon · Ben-Gurion University · draft, {DATE}</p>
</section>'''

slides = [TITLE]
S = slides.append
k, n = I('k'), I('n')

S(f"""<section class="slide light">
  <p class="eyebrow">Motivation</p>
  <h2>“I'll come if enough others come”</h2>
  <p class="sub">In a group chat someone must say “I'm in” first. If everyone waits, nothing happens.</p>
  <div class="vis">{ten_vis()}</div>
</section>""")

S(f"""<section class="slide light">
  <p class="eyebrow">Model</p>
  <h2>Conditions, groups, welfare</h2>
  <div class="box" style="margin-top:20px">
<p>{n} members, one activity, several days. Member {M('i')} has a private <b>condition</b>: the days it accepts, and a threshold {M(r'\mathit{th}_i')}: “I come if at least {M(r'\mathit{th}_i')} others come.”</p>
<p>A <b>group</b> is a day and a set of members who all accept that day, has at least {k} members, and satisfies every member's threshold. At most one group per day; each member in at most one group.</p>
<p><b>Welfare:</b> the number of members placed in groups.</p>
  </div>
</section>""")

S(f"""<section class="slide light">
  <p class="eyebrow">Model</p>
  <h2>Two ways to form groups</h2>
  <div class="box" style="margin-top:20px">
<p><b>Group chat:</b> members read the chat one at a time, in any order, as often as they like. A member writes “I'm in” for an accepted day once at least {M(r'\mathit{th}_i')} others are in for that day, and does not take it back. A day with at least {k} sign-ups forms a group.</p>
<p><b>Agora:</b> agents hold their members' conditions and choose the groups with most members placed.</p>
  </div>
</section>""")

S(thm('Theorem 4', 'One day: the chat stops early, the agora does not',
      f"""<p>With one day, for every order, the chat ends with the smallest {M('c')} such that exactly {M('c')} members have threshold at most {M('c')}.</p>
<p>The agora places the largest {M(r'm \ge k')} such that at least {M('m')} members have threshold at most {M('m-1')}.</p>""",
      f"<p>The chat is Granovetter's cascade. Ten members “if 3”: chat 0, agora 10.</p>",
      granovetter_vis(), f'Thresholds 0, 2, 2, 3, 4, 4, 4, 5, 5, 6, 6, 9; {M("k=4")}.'))

S(f"""<section class="slide light">
  <p class="eyebrow">Proposition 5</p>
  <h2>Several days: the best groups are hard to find</h2>
  <div class="box" style="margin-top:20px">
<p>Deciding whether all members can be placed is NP-hard, even if every threshold is 2.</p>
  </div>
  <div class="why"><p>From exact cover by 3-sets: days are the sets and members the elements, each accepting the days of its sets; a group of at least three on a day is then exactly that set.</p>
<p>In practice, an integer program finds the best groups for neighborhoods of 400 members in under a second.</p></div>
</section>""")

S(thm('Simulation', 'Few eager members: the chat forms little',
      f"""<p>100 members, 10 activities from popular to niche, 7 days, {M('k=4')}; thresholds 2 to 6, except eager members (threshold 0).</p>
<p>With 10% eager: the chat places 13% of the interested; the agora, 69%.</p>""",
      '<p>Chat: random reading order. Agora: the best groups (integer program). 20 neighborhoods per point.</p>',
      lines_vis(EAGER, 'eager', 'share of eager members', [(0, '0%'), (0.25, '25%'), (0.5, '50%'), (0.75, '75%'), (1, '100%')])))

S(thm('Simulation', 'The gap stays as the neighborhood grows',
      f"""<p>10% eager members; neighborhoods from 25 to 400 members.</p>
<p>At 400 members: the chat places 53%, the agora 96%.</p>""",
      '<p>Same setting and methods as the previous slide.</p>',
      lines_vis(SIZE, 'n', 'neighborhood size n', [(25, '25'), (50, '50'), (100, '100'), (200, '200'), (400, '400')], logx=True)))

S(f'''<section class="slide light">
  <p class="eyebrow">Prototype</p>
  <h2>Try it: <a href="../app" style="color:var(--orange)">talmonlab.bgu.ac.il/agora/app</a></h2>
  <p class="sub">You and 80 simulated neighbors: set what you would join, compare chat and agora.</p>
  <img class="shot" src="data:image/jpeg;base64,{APP}" alt="prototype">
</section>''')

S(f'''<section class="slide light">
  <p class="eyebrow">Related work</p>
  <h2>Closest work, and the difference</h2>
  {related_vis()}
  <p class="why" style="margin-top:30px">New here: personal thresholds and days, and the gap between a public cascade and agents that choose the groups.</p>
</section>''')

S('''<section class="slide light">
  <p class="eyebrow">Summary</p>
  <h2>Agents let a group start together</h2>
  <div class="rows ruled">
    <div class="row"><span class="n">1</span><p>A chat stops where no one else is ready; the agora finds the largest group</p></div>
    <div class="row"><span class="n">2</span><p>With few eager members, the chat forms almost nothing; agents place most</p></div>
    <div class="row"><span class="n">3</span><p>A platform with conditional pledges could do this too; agents spare the forms</p></div>
    <div class="row"><span class="n">4</span><p>Next: questions needed per member; who-with-whom conditions</p></div>
  </div>
</section>''')

slides.append(TITLE)

html = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Who Goes First? · AI-Agora</title>
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
