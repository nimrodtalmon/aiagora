#!/usr/bin/env python3
"""Builds web/brief/index.html: research brief on Problem 1 (groups with a size
threshold, formed only from members who said yes). Uses the explainer deck's
drawing helpers and the real runs in runs/threshold.csv (experiments/threshold.py).

    python3 web/brief/src/build.py
"""
import csv, importlib.util, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


kit = load('kit', os.path.join(HERE, '..', '..', 'kit.py'))
d = kit.d
svg, text, head, bot = d.svg, d.text, d.head, d.bot
OR, DK, GR, GL, CARD = d.OR, d.DK, d.GR, d.GL, d.CARD
I = M = kit.I
KATEX_INIT, model_vis = kit.KATEX_INIT, kit.model_vis
STYLE = kit.STYLE.replace('</style>', '.split.wide { grid-template-columns: 1.45fr 0.55fr; }\n.split.picwide { grid-template-columns: 0.85fr 1.15fr; gap: 44px; }\n</style>')


def thm(*a, wide=False, picwide=False, **kw):
    out = kit.thm(*a, **kw)
    if wide:
        out = out.replace('class="split"', 'class="split wide"')
    if picwide:
        out = out.replace('class="split"', 'class="split picwide"')
    return out


OUT = os.path.join(HERE, '..', 'index.html')
DATE = 'November 18, 2026'

RUNS = {}
for r in csv.DictReader(open(os.path.join(ROOT, 'runs', 'threshold.csv'))):
    RUNS[(int(r['b']), int(r['k']), r['setting'])] = float(r['mean'])


# ---------- pictures ----------
NM, MM, CELL = 8, 6, 62


def grid(x0, title, cells, group=(), hot=None):
    """cells: {(i, j): 0 asked-no / 1 asked-yes}; members are columns, initiatives rows."""
    b = text(x0 + 70 + NM * CELL / 2, 36, title, 36, DK, weight=800)
    for i in range(NM):
        b += head(x0 + 80 + i * CELL + CELL / 2, 80, 15, OR if i in group else GL)
    for j in range(MM):
        y = 110 + j * CELL
        b += text(x0 + 56, y + CELL / 2 + 10, f'{j+1}', 28, OR if j == hot else GR, 'end', 800)
        for i in range(NM):
            x = x0 + 80 + i * CELL
            v = cells.get((i, j))
            fill = OR if v == 1 else ('#E6E5E0' if v == 0 else CARD)
            b += f'<rect x="{x+4}" y="{y+4}" width="{CELL-8}" height="{CELL-8}" rx="10" fill="{fill}" stroke="{GL if v is None else fill}" stroke-width="2"/>'
    return b


GROUP, HOT, B = (1, 4, 6), 2, 2   # illustration: k = 3 members accept initiative 3


def answer(i, j):
    return 1 if (i in GROUP and j == HOT) else 0


def model_grid():
    return svg(590, 490, grid(0, 'acceptances: unknown', {}))


def silos_vis():
    rng = np.random.default_rng(3)
    ind = {(i, int(j)): answer(i, int(j)) for i in range(NM) for j in rng.choice(MM, B, replace=False)}
    conv_cols = [2, 5]
    conv = {(i, j): answer(i, j) for i in range(NM) for j in conv_cols}
    b = grid(0, 'independent', ind, GROUP, HOT) + grid(640, 'convention', conv, GROUP, HOT)
    return svg(1230, 490, b)


def central_vis():
    order = [3, 0, 6, 1, 7, 4, 2, 5]           # a random order of members
    exp = {}
    for p, i in enumerate(order):
        j = p % MM
        exp[(i, j)] = answer(i, j)
    com = dict(exp)
    for i in range(NM):
        if (i, HOT) not in com:
            com[(i, HOT)] = answer(i, HOT)
    b = grid(0, 'explore: 1 each', exp, GROUP, HOT) + grid(640, 'commit: all ask 3', com, GROUP, HOT)
    return svg(1230, 490, b)


def chart_vis(bq=3):
    ks = [1, 2, 3, 4, 6, 8, 12]
    w, h = 900, 620
    X0, X1, Y0, Y1 = 120, 760, 540, 60
    X = lambda k: X0 + (k - 1) / 11 * (X1 - X0)
    Y = lambda v: Y0 - v * (Y0 - Y1)
    b = ''
    for v in (0, .25, .5, .75, 1):
        b += f'<line x1="{X0}" y1="{Y(v):.0f}" x2="{X1}" y2="{Y(v):.0f}" stroke="#E6E5E0" stroke-width="2"/>'
        b += text(X0 - 16, Y(v) + 10, f'{v:g}', 26, GR, 'end')
    for k in ks:
        b += text(X(k), Y0 + 40, str(k), 26, GR)
    b += text((X0 + X1) / 2, Y0 + 82, 'threshold k (size of the group)', 28, GR, weight=700)
    b += text(36, (Y0 + Y1) / 2, 'welfare / OPT', 28, GR, weight=700, extra=f'transform="rotate(-90 36 {(Y0+Y1)/2})"')
    lb = [(k, 1 - (1 - (bq - 1) / 12) ** k) for k in ks]
    b += '<polyline fill="none" stroke="' + OR + '" stroke-width="3" stroke-dasharray="10 8" points="' + ' '.join(f'{X(k):.0f},{Y(v):.0f}' for k, v in lb) + '"/>'
    series = [('central-ec', OR, 'central'), ('silos-convention', DK, 'silos, convention'), ('silos', GL, 'silos, independent')]
    for s, col, lab in series:
        pts = [(k, RUNS[(bq, k, s)]) for k in ks]
        b += f'<polyline fill="none" stroke="{col}" stroke-width="5" points="' + ' '.join(f'{X(k):.0f},{Y(v):.0f}' for k, v in pts) + '"/>'
        for k, v in pts:
            b += f'<circle cx="{X(k):.0f}" cy="{Y(v):.0f}" r="8" fill="{col}" stroke="#fff" stroke-width="2"/>'
        k, v = pts[-1]
        dy = {'central-ec': -22, 'silos-convention': -20, 'silos': -18}[s]
        b += text(X1 - 4, Y(v) + dy, lab, 28, DK, 'end', 700)
    b += text(X(6), Y(lb[4][1]) + 48, 'proved lower bound', 26, OR, 'start', 700)
    return svg(w, h, b)


def related_vis():
    boxes = [('Group activity selection', 'Ganian, Ordyniak, Rahul 2023 (Algorithmica)', 'groups with size limits; full information'),
             ('Stable communities from samples', 'Igarashi, Sliwinski, Zick 2019 (AAAI)', 'learns from sampled coalitions; no questions, no threshold'),
             ('Elicitation for group decisions', 'Naamani-Dery, Golan, Kalech, Rokach 2014', 'few queries, but one winning item, no groups'),
             ('Adaptive group elicitation', 'Ding et al. 2026 (arXiv)', 'LLM picks whom to ask; predicts answers, forms nothing')]
    return '<div class="rw">' + ''.join(
        f'<div class="box"><h3>{t}</h3><p class="who">{w}</p><p class="diff">{x}</p></div>' for t, w, x in boxes) + '</div>'


# ---------- slides ----------
TITLE = f'''<section class="slide dark center">
  <p class="eyebrow">AI-Agora · Problem 1</p>
  <h1>Forming Groups with Consent</h1>
  <p class="big">Thresholds make sharing pay</p>
  <p class="muted">Nimrod Talmon · Ben-Gurion University · draft, {DATE}</p>
</section>'''

slides = [TITLE]
S = slides.append
n, m, b, k = I('n'), I('m'), I('b'), I('k')
BM, KBM = M(r'\tfrac{b}{m}'), M(r'\tfrac{kb}{m}')

S(f"""<section class="slide light">
  <p class="eyebrow">Motivation</p>
  <h2>A group exists only once enough say yes</h2>
  <p class="sub">A single yes is useless alone, but it points to where the others are.</p>
  <div class="vis">{kit.card_vis()}</div>
</section>""")

S(thm('Model', 'Groups with a threshold, only yes counts',
      f"""<p>{n} members, {m} initiatives. Member {M('i')} accepts a set {M('A_i')}, unknown to all, its agent included.</p>
<p>An agent may ask its member at most {b} questions: “join {M('j')} if it forms?”</p>
<p><b>Outcome:</b> disjoint groups {M('G_j')} of members who said yes to {M('j')}; each empty or of size at least {k}.</p>
<p><b>Welfare:</b> {M(r'\sum_j |G_j|')}. <b>OPT:</b> its maximum given all {M('A_i')}.</p>""",
      f'With {M('k=1')}: pick-one, with many options at once.',
      model_grid(), wide=True))

S(thm('Model', 'Settings and measure, as before',
      f"""<p><b>Silos:</b> agents ask alone, then report; a rule forms groups. <b>With a convention:</b> agents share a random seed fixed in advance.</p>
<p><b>Central:</b> a coordinator sees all answers and decides who is asked what.</p>
<p><b>Grassroots:</b> agents message each other; all output the same outcome.</p>
<p><b>Guarantee:</b> {M(r'\min_{\text{communities}}\ \mathbb{E}[\text{welfare}]\,/\,\mathrm{OPT}')}. <b>Gain:</b> best central / best silos.</p>""",
      f'First case, the <b>hidden group</b>: exactly {k} members accept one hidden initiative; no one accepts anything else.',
      model_vis(), stack=True, pic_h=250))

S(thm('Theorem 1', 'Hidden group: silos need a convention',
      f"""<p>For the hidden group, the best silos guarantee is</p><p>{BM} with a convention, {M(r'\big(\tfrac{b}{m}\big)^{k}')} without one.</p>""",
      f"""<p><b>≥</b> All ask the same {b} random initiatives; or each its own.</p>
<p><b>≤</b> A no tells nothing, so questions are fixed in advance; hide the group where few ask.</p>""",
      silos_vis(), f"{M('n=8,\\ m=6,\\ b=2,\\ k=3')}; the group accepts 3."))

S(thm('Theorem 2', f'Hidden group: a gain of order {M(r'\min(k,\,m/b)')}',
      f"""<p>If {M(r'b \ge 2')} and {m} divides {n}, then central guarantees {M(r'1-\big(1-\tfrac{b-1}{m}\big)^{k}')}. No protocol guarantees more than {M(r'\min\big(1,\tfrac{kb}{m}\big)')}.</p>
<p>So the gain is {M(r'\Theta\big(\min(k,\tfrac{m}{b})\big)')}; the constant is at least {M('0.3')}.</p>""",
      f"""<p><b>≥</b> Explore: in random order, {M('b-1')} questions each, cycling; commit: all ask about the yes. <b>≤</b> Before the first yes, all answers are no; {M('nb')} of {M('nm')} pairs are asked, {k} are hits.</p>""",
      central_vis(), stack=True, pic_h=215))

S(thm('Simulation', f'Central grows with {k}; silos do not',
      f"""<p>Hidden group: {M('n=60')}, {M('m=12')}, {M('b=3')}.</p><p>1,000 random instances per point.</p>""",
      '<p>Central runs the protocol of Theorem 2; the dashed line is its proved bound.</p>',
      chart_vis(3)))
S(f'''<section class="slide light">
  <p class="eyebrow">Related work</p>
  <h2>Closest work, and the difference</h2>
  {related_vis()}
  <p class="why" style="margin-top:30px">New here: a size threshold together with a question budget per member; only a yes enrolls.</p>
</section>''')

S('''<section class="slide light">
  <p class="eyebrow">Summary</p>
  <h2>Thresholds turn one yes into a pointer</h2>
  <div class="rows ruled">
    <div class="row"><span class="n">1</span><p>Hidden group: gain of order \\(\\min(k, m/b)\\); without thresholds it was 1</p></div>
    <div class="row"><span class="n">2</span><p>Silos need a convention: \\((b/m)^k\\) without one, \\(b/m\\) with one</p></div>
    <div class="row"><span class="n">3</span><p>Next: noise (a false lead), several groups, thresholds that differ</p></div>
    <div class="row"><span class="n">4</span><p>Next: members in several groups’ sets — whom to place where</p></div>
  </div>
</section>''')

slides.append(TITLE)

html = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Forming Groups with Consent · AI-Agora</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@300..900&display=swap">
<link rel="stylesheet" href="../assets/deck.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/auto-render.min.js"></script>
''' + KATEX_INIT + '\n' + STYLE + '''
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
