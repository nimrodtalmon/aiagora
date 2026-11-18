#!/usr/bin/env python3
"""Builds web/brief/index.html: a briefing deck for Nimrod (what was done, in pictures).

A briefing is not a talk: one idea per slide, a picture first, a status badge
(proved / simulated / open), and a numbered "your call" slide he can answer
tersely. It reuses the explainer deck's drawing helpers and real runs.

    python3 web/brief/src/build.py
"""
import importlib.util, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(HERE, '..', '..', 'deck', 'src', 'build.py')
spec = importlib.util.spec_from_file_location('deckbuild', DECK)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)                      # also rebuilds the explainer deck (harmless)
svg, text, head, bot = d.svg, d.text, d.head, d.bot
OR, DK, GR, GL, CARD = d.OR, d.DK, d.GR, d.GL, d.CARD
N, M, ACTS, RUNS = d.N, d.M, d.ACTS, d.RUNS

OUT = os.path.join(HERE, '..', 'index.html')
DATE = 'November 18, 2026'


def badge(kind):
    label = {'proved': 'proved', 'sim': 'simulated', 'open': 'open'}[kind]
    return f'<span class="badge {kind}">{label}</span>'


def result(n, eyebrow, kind, title, why, vis):
    return f'''<section class="slide light">
  <p class="eyebrow">Result {n} · {eyebrow} {badge(kind)}</p>
  <h2>{title}</h2>
  <p class="sub">{why}</p>
  <div class="vis">{vis}</div>
</section>'''


# ---------- pictures ----------
def mini_grid(run, title, x0=0, cell=64):
    b = text(x0 + 4 * cell + 150, 40, title, 40, DK, weight=800)
    done = {(i, j): y for _, i, j, y in run['asks']}
    for k in range(N):
        b += head(x0 + 150 + k * cell + cell / 2, 92, 15, DK)
    for j, a in enumerate(ACTS):
        y = 140 + j * cell
        b += text(x0 + 135, y + cell / 2 + 10, a, 28, DK, 'end', 700)
        for k in range(N):
            x = x0 + 150 + k * cell
            v = done.get((k, j))
            fill = OR if v == 1 else ('#E6E5E0' if v == 0 else CARD)
            b += f'<rect x="{x+4}" y="{y+4}" width="{cell-8}" height="{cell-8}" rx="10" fill="{fill}" stroke="{GL if v is None else fill}" stroke-width="2"/>'
    return b


def grids_vis(which=('silos', 'central')):
    w = 870 * len(which) - 40
    b = ''
    for k, s in enumerate(which):
        lab = 'alone' if s == 'silos' else 'together'
        b += mini_grid(RUNS[s], f"{lab}: {RUNS[s]['welfare']} of {N} join", 870 * k)
    return svg(w, 560, b)


def model_vis():
    w, h, b = 1650, 520, ''
    cy, R = 250, 150
    for c, (cx, name, kind) in enumerate([(260, 'alone', 'silos'), (825, 'central', 'star'), (1390, 'grassroots', 'mesh')]):
        pts = [(cx + R * math.cos(2 * math.pi * k / N - math.pi / 2), cy + R * math.sin(2 * math.pi * k / N - math.pi / 2)) for k in range(N)]
        if kind == 'star':
            for x, y in pts:
                b += f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" stroke="{OR}" stroke-width="4"/>'
            b += bot(cx, cy + 8, 64, DK)
        if kind == 'mesh':
            for a in range(N):
                for e in range(a + 1, N):
                    b += f'<line x1="{pts[a][0]:.0f}" y1="{pts[a][1]:.0f}" x2="{pts[e][0]:.0f}" y2="{pts[e][1]:.0f}" stroke="{OR}" stroke-width="2.5" opacity=".7"/>'
        for x, y in pts:
            b += bot(x, y + 6, 46)
        b += text(cx, 480, name, 44, DK, weight=800)
    return svg(w, h, b)


def bars_vis():
    w, h = 1300, 520
    data = [(160, .43, .11), (640, .65, .107), (2560, .82, .10)]
    X0, Y0, H = 200, 430, 360
    b = f'<line x1="{X0-20}" y1="{Y0}" x2="1250" y2="{Y0}" stroke="{GL}" stroke-width="3"/>'
    for k, (n, t, a) in enumerate(data):
        x = X0 + k * 360
        for dx, v, col, lab in ((0, a, GR, 'alone'), (130, t, OR, 'together')):
            b += f'<rect x="{x+dx}" y="{Y0 - v*H:.0f}" width="110" height="{v*H:.0f}" rx="10" fill="{col}"/>'
            b += text(x + dx + 55, Y0 - v * H - 16, f'{int(round(v*100))}%', 36, col, weight=800)
        b += text(x + 120, Y0 + 50, f'{n} people', 36, GR, weight=700)
    b += f'<rect x="{X0+700}" y="20" width="34" height="34" rx="6" fill="{OR}"/>' + text(X0 + 750, 48, 'together', 34, DK, 'start', 700)
    b += f'<rect x="{X0+930}" y="20" width="34" height="34" rx="6" fill="{GR}"/>' + text(X0 + 980, 48, 'alone', 34, DK, 'start', 700)
    return svg(w, h, b)


def crown_vis():
    w, h, b = 1400, 520, ''
    cx, cy, R = 700, 250, 190
    pts = [(cx + R * math.cos(2 * math.pi * k / N - math.pi / 2), cy + R * math.sin(2 * math.pi * k / N - math.pi / 2)) for k in range(N)]
    lead = pts[0]
    for x, y in pts[1:]:
        b += f'<line x1="{lead[0]:.0f}" y1="{lead[1]:.0f}" x2="{x:.0f}" y2="{y:.0f}" stroke="{OR}" stroke-width="4"/>'
    for k, (x, y) in enumerate(pts):
        b += bot(x, y + 6, 70 if k == 0 else 54, DK if k == 0 else OR)
    x, y = lead
    b += f'<path d="M{x-30} {y-62} l10 -26 l20 18 l20 -18 l10 26 Z" fill="{OR}"/>'
    b += text(cx, 500, 'agent 1 plays the coordinator', 40, DK, weight=700)
    return svg(w, h, b)


def since_vis():
    tiles = [('6', 'results, all proved,<br>checked by simulation'),
             ('22+', 'papers read for<br>related work'),
             ('10', 'pages of paper<br>draft on Overleaf'),
             ('2', 'live pages: slides<br>and a playground')]
    return '<div class="tiles">' + ''.join(
        f'<div class="tile"><div class="big">{a}</div><div class="cap">{b}</div></div>' for a, b in tiles) + '</div>'


def related_vis():
    boxes = [('Asking voters little', 'Halpern et al. 2023 · Lu &amp; Boutilier 2011', 'outcome judged on everyone, not only who said yes'),
             ('Few bits per voter', 'Mandal et al. 2019, 2020 · Kempe', 'one-shot; same "options ÷ budget" shape as alone'),
             ('Bandits, adaptivity', 'Gupta–Nagarajan–Singla · Colton 1963', 'independent tastes: adaptivity gains only log'),
             ('Agents for people', 'Habermolt 2026 · CalBench 2026', 'no question budget, no comparison to the best')]
    return '<div class="rw">' + ''.join(
        f'<div class="box"><h3>{t}</h3><p class="who">{w}</p><p class="diff">{x}</p></div>' for t, w, x in boxes) + '</div>'


# ---------- slides ----------
TITLE = f'''<section class="slide dark center">
  <p class="eyebrow">Briefing · AI-Agora</p>
  <h1>What I did, in pictures</h1>
  <p class="muted">{DATE}</p>
</section>'''

slides = [TITLE]
S = slides.append

S(f'''<section class="slide light">
  <p class="eyebrow">Since last time</p>
  <h2>The simplest case, end to end</h2>
  <div class="vis">{since_vis()}</div>
</section>''')

S(f'''<section class="slide light">
  <p class="eyebrow">The model</p>
  <h2>Pick one activity, ask little, only yes counts</h2>
  <p class="sub">8 people, 6 activities, 2 yes/no questions per person. Three ways to organize:</p>
  <div class="vis">{model_vis()}</div>
</section>''')

S(result(1, 'alone', 'proved', 'Alone gets exactly questions ÷ options',
         'Everyone likes the garden, but an agent alone finds it only 2 times in 6.',
         grids_vis(('silos',))))

S(result(2, 'shared favorite', 'proved', 'Together: everyone joins with 2 questions',
         'Search together with question 1, join with question 2. A gain of 6 ÷ 2, the most possible.',
         grids_vis()))

S(result(3, 'no shared tastes', 'proved', 'Without shared tastes, no gain at all',
         'One person’s answer says nothing about another’s, so there is nothing to share.',
         d.tastes_vis()))

S(result(4, 'big communities', 'proved', 'One popular activity: close to the best',
         'Sample a few people per activity, then everyone asks about the leader. Simulated below.',
         d.scale_vis()))

S(result(5, 'one question each', 'proved', 'Even with one question each',
         'Only a small sample explores (they are used up); the rest join the leader. Slower.',
         bars_vis()))

S(result(6, 'no coordinator', 'proved', 'Grassroots is never weaker than central',
         'In our model, agents can simply agree that agent 1 coordinates. The difference is elsewhere: trust, load, privacy.',
         crown_vis()))

S(f'''<section class="slide light">
  <p class="eyebrow">Related work {badge('sim')}</p>
  <h2>New: only yes counts, three settings, two costs</h2>
  <p class="sub">The theorems are simple; the model and the shared-tastes story are new.</p>
  {related_vis()}
</section>'''.replace(badge('sim'), '<span class="badge sim">22+ papers read</span>'))

S('''<section class="slide dark">
  <p class="eyebrow">Your call</p>
  <h2>Answer by number</h2>
  <div class="rows ruled">
    <div class="row"><span class="n">1</span><p>Is “pick one, ask little, only yes counts” the right core model?</p></div>
    <div class="row"><span class="n">2</span><p>Next step: groups (many activities), or grassroots measures (trust, load)?</p></div>
    <div class="row"><span class="n">3</span><p>Does result 6 change how the BSF model defines grassroots?</p></div>
    <div class="row"><span class="n">4</span><p>Paper now, or more results first?</p></div>
  </div>
</section>''')

S('''<section class="slide light">
  <p class="eyebrow">Everything else</p>
  <h2>Links</h2>
  <div class="rows ruled">
    <div class="row"><span class="n">→</span><p><a class="interactive" href="../">Explainer slides</a> · talmonlab.bgu.ac.il/agora</p></div>
    <div class="row"><span class="n">→</span><p><a class="interactive" href="../play">Playground</a> · alone vs together, with sliders</p></div>
    <div class="row"><span class="n">→</span><p><a class="interactive" href="https://www.overleaf.com/project/6afb7a97a70946e905f9e3ab">Overleaf</a> · paper draft, related-work report</p></div>
    <div class="row"><span class="n">→</span><p><a class="interactive" href="https://github.com/nimrodtalmon/aiagora">Code</a> · github.com/nimrodtalmon/aiagora</p></div>
  </div>
</section>''')

slides.append(TITLE)

STYLE = '''<style>
.sub { font-size: 42px; color: var(--gray); margin-top: -20px; }
.vis { margin-block: auto; display: flex; justify-content: center; }
.badge { display: inline-block; margin-left: 18px; padding: 4px 18px; border-radius: 999px; font-size: 26px;
  font-weight: 700; vertical-align: 4px; }
.badge.proved { background: var(--orange); color: var(--dark); }
.badge.sim { border: 3px solid var(--orange); color: var(--dark); }
.badge.open { background: var(--gray-light); color: var(--dark); }
.tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 36px; width: 100%; }
.tile { background: var(--card); border: 3px solid var(--gray-light); border-radius: 28px; padding: 40px 36px; }
.tile .big { font-size: 140px; font-weight: 800; color: var(--orange); line-height: 1; }
.tile .cap { font-size: 38px; font-weight: 700; margin-top: 24px; line-height: 1.25; }
.rw { display: grid; grid-template-columns: 1fr 1fr; gap: 28px 36px; margin-top: 10px; }
.rw .box { background: var(--card); border: 3px solid var(--gray-light); border-radius: 24px; padding: 26px 32px; }
.rw h3 { font-size: 40px; margin: 0 0 8px; }
.rw .who { font-size: 30px; color: var(--gray); margin: 0 0 10px; }
.rw .diff { font-size: 32px; margin: 0; }
.rows a { color: inherit; }
</style>'''

html = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Briefing · AI-Agora</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@300..900&display=swap">
<link rel="stylesheet" href="../assets/deck.css">
''' + STYLE + '''
</head>
<body>
<div id="stage">
''' + '\n'.join(f'<!-- {k+1} -->{s}' for k, s in enumerate(slides)) + '''
</div>
<script src="../assets/deck.js"></script>
</body>
</html>
'''
open(OUT, 'w').write(html)
print(len(slides), 'slides')
