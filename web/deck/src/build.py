#!/usr/bin/env python3
"""Builds web/deck/index.html: the AI-Agora explainer (zutot deck engine).

The two demo slides replay real runs of agora/pick_one.py on a hidden-favorite
neighborhood (8 people, 6 activities, everyone would join the garden), so the
slides, the code and the paper seed show the same numbers.

    python3 web/deck/src/build.py
"""
import csv, json, math, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
sys.path.insert(0, ROOT)
import numpy as np
from agora.model import Instance, UNKNOWN
from agora.pick_one import run

OUT = os.path.join(HERE, '..', 'index.html')
OR, DK, GR, GL, CARD, PALE, LT = '#F7941D', '#26282C', '#5F6368', '#B9BCC1', '#FDFDFB', '#FCE8D2', '#F3F3F1'
GREEN, BLUE = '#3E9B4F', '#3A7BC8'
FONT = 'font-family="Heebo, Arial, sans-serif"'

# ---------- the demo neighborhood ----------
N, M, FAV, BUDGET = 8, 6, 2, 2
ACTS = ['carpool', 'running', 'garden', 'book club', 'chess', 'choir']
acc = np.zeros((N, M), bool)
acc[:, FAV] = True
inst = Instance(acc, 1, np.full((N, M), UNKNOWN, np.int8))
SILOS_SEED = 5                      # a typical run: 3 of 8 join (expected 8 x 2/6 = 2.7)


def asks(res):
    """[[round, person, activity, yes], ...] in round order."""
    return [[e['t'], e['agent'], e['j'], e['answer']] for e in res['events'] if e['type'] == 'ask']


RUNS = {}
for name, setting, seed in [('silos', 'silos', SILOS_SEED), ('central', 'central', 0),
                            ('grassroots', 'grassroots', 0)]:
    r = run(inst, setting, BUDGET, seed=seed)
    RUNS[name] = {'asks': asks(r), 'welfare': r['welfare'], 'questions': r['attention'],
                  'messages': r['messages']}
assert RUNS['central']['welfare'] == N and RUNS['grassroots']['welfare'] == N

# ---------- simulation summary for the "in general" slide ----------
curve = defaultdict(list)
with open(os.path.join(ROOT, 'runs', 'pick_one.csv')) as f:
    for row in csv.DictReader(f):
        if row['family'] == 'random popularity':
            curve[(row['setting'], int(row['budget']))].append(float(row['ratio']))
CURVE = {s: [sum(curve[(s, b)]) / len(curve[(s, b)]) for b in range(1, 11)]
         for s in ('silos', 'central')}


# ---------- svg helpers ----------
def svg(w, h, body, extra=''):
    return f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" {FONT} {extra}>{body}</svg>'


def text(x, y, s, size=30, fill=DK, anchor='middle', weight=400, extra=''):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" {extra}>{s}</text>')


def head(cx, cy, r, fill):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'
            f'<path d="M{cx-1.6*r} {cy+2.6*r} a{1.6*r} {1.6*r} 0 0 1 {3.2*r} 0 Z" fill="{fill}"/>')


def bot(cx, cy, s, fill=OR):
    return (f'<rect x="{cx-s/2}" y="{cy-s/2}" width="{s}" height="{s*.8}" rx="{s/5}" fill="{fill}"/>'
            f'<circle cx="{cx-s/5}" cy="{cy-s/12}" r="{s/11}" fill="{DK}"/>'
            f'<circle cx="{cx+s/5}" cy="{cy-s/12}" r="{s/11}" fill="{DK}"/>'
            f'<line x1="{cx}" y1="{cy-s/2}" x2="{cx}" y2="{cy-s*.72}" stroke="{fill}" stroke-width="5"/>'
            f'<circle cx="{cx}" cy="{cy-s*.76}" r="{s/12}" fill="{fill}"/>')


def people_vis():
    w, h, b = 1500, 470, ''
    for k in range(N):
        x = 110 + k * 183
        b += head(x, 120, 42, DK)
        b += f'<line x1="{x}" y1="250" x2="{x}" y2="300" stroke="{GL}" stroke-width="4" stroke-dasharray="8 8"/>'
        b += bot(x, 360, 84)
    b += text(-10, 160, 'people', 34, GR, 'end', 700) + text(-10, 370, 'agents', 34, GR, 'end', 700)
    return svg(w, h, b, 'style="overflow:visible;margin-left:200px"')


def acts_vis():
    w, h, b = 1600, 300, ''
    for k, a in enumerate(ACTS):
        x = k * 270
        b += f'<rect x="{x}" y="20" width="240" height="240" rx="28" fill="{CARD}" stroke="{GL}" stroke-width="3"/>'
        b += text(x + 120, 125, '?', 110, GL, weight=800)
        b += text(x + 120, 225, a, 38, DK, weight=700)
    return svg(w, h, b)


def ask_vis():
    w, h, b = 1500, 470, ''
    b += head(200, 170, 70, DK)
    b += bot(1260, 220, 150)
    b += (f'<rect x="420" y="60" width="680" height="130" rx="30" fill="{CARD}" stroke="{GL}" stroke-width="3"/>'
          + text(760, 142, 'Would you join the garden?', 46, DK, weight=700))
    b += (f'<rect x="420" y="250" width="300" height="120" rx="30" fill="{OR}"/>'
          + text(570, 328, 'Yes!', 52, DK, weight=800))
    return svg(w, h, b)


GRID_W, GRID_H = 1290, 600
CX0, CY0, CW, CH = 300, 120, 124, 76


def grid_vis(gid):
    b = ''
    for k in range(N):
        b += head(CX0 + k * CW + CW / 2, 36, 22, DK)
    for j, a in enumerate(ACTS):
        y = CY0 + j * CH
        b += text(CX0 - 24, y + CH / 2 + 13, a, 36, DK, 'end', 700, f'class="rl" data-j="{j}"')
        for k in range(N):
            x = CX0 + k * CW
            b += (f'<g class="cell" data-i="{k}" data-j="{j}"><rect x="{x+6}" y="{y+6}" width="{CW-12}" '
                  f'height="{CH-12}" rx="14" fill="{CARD}" stroke="{GL}" stroke-width="2"/>'
                  f'<text x="{x+CW/2}" y="{y+CH/2+14}" font-size="40" font-weight="800" text-anchor="middle" fill="{GL}">?</text></g>')
    b += (f'<rect class="hlrow" x="{CX0-260}" y="{CY0+FAV*CH}" width="{N*CW+268}" height="{CH}" rx="16" '
          f'fill="none" stroke="{OR}" stroke-width="6" opacity="0"/>')
    return svg(GRID_W, GRID_H, b, f'id="{gid}"')


def demo(gid, title_eyebrow, title, sub):
    return f'''<section class="slide light demo" data-run="{gid}">
  <p class="eyebrow">{title_eyebrow}</p>
  <h2>{title}</h2>
  <p class="sub">{sub}</p>
  <div class="interactive demo-row">
    {grid_vis(gid)}
    <div class="res">
      <div class="keys"><button class="kb" data-act="run"><i>1</i> run</button><button class="kb" data-act="reset"><i>2</i> reset</button></div>
      <div class="joined"><span class="jn">–</span><span class="jd"> of {N}</span></div>
      <div class="jl">join the garden</div>
      <div class="stat">questions <b class="sq">0</b></div>
      <div class="stat">messages <b class="sm">0</b></div>
    </div>
  </div>
</section>'''


def nets_vis():
    w, h, b = 1600, 520, ''
    cx1, cx2, cy, R = 380, 1220, 250, 190
    pts = lambda cx: [(cx + R * math.cos(2 * math.pi * k / N - math.pi / 2),
                       cy + R * math.sin(2 * math.pi * k / N - math.pi / 2)) for k in range(N)]
    p1, p2 = pts(cx1), pts(cx2)
    for x, y in p1:
        b += f'<line x1="{cx1}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{OR}" stroke-width="5"/>'
    for a in range(N):
        for c in range(a + 1, N):
            b += (f'<line x1="{p2[a][0]:.1f}" y1="{p2[a][1]:.1f}" x2="{p2[c][0]:.1f}" y2="{p2[c][1]:.1f}" '
                  f'stroke="{OR}" stroke-width="3" opacity=".75"/>')
    b += bot(cx1, cy + 10, 80, DK)
    for x, y in p1 + p2:
        b += bot(x, y + 8, 56)
    c, g = RUNS['central']['messages'], RUNS['grassroots']['messages']
    b += text(cx1, 500, f'through a coordinator: {c} messages', 40, DK, weight=700)
    b += text(cx2, 500, f'everyone to everyone: {g} messages', 40, DK, weight=700)
    return svg(w, h, b)


def curve_vis():
    w, h = 1300, 600
    X0, X1, Y0, Y1 = 150, 1200, 500, 40
    xs = lambda b: X0 + (b - 1) / 9 * (X1 - X0)
    ys = lambda v: Y0 - v * (Y0 - Y1)
    b = ''
    for v in (0, .5, 1):
        b += f'<line x1="{X0}" y1="{ys(v):.0f}" x2="{X1}" y2="{ys(v):.0f}" stroke="{GL}" stroke-width="2"/>'
        b += text(X0 - 20, ys(v) + 12, f'{int(v*100)}%', 32, GR, 'end')
    for bb in (1, 2, 4, 6, 8, 10):
        b += text(xs(bb), Y0 + 50, str(bb), 32, GR)
    b += text((X0 + X1) / 2, Y0 + 98, 'questions per person', 34, GR, weight=700)
    b += text(X0 - 120, (Y0 + Y1) / 2, 'of the best', 34, GR, weight=700,
              extra=f'transform="rotate(-90 {X0-120} {(Y0+Y1)/2})"')
    for s, col, lab in (('silos', GR, 'alone'), ('central', OR, 'together')):
        pts = ' '.join(f'{xs(k+1):.0f},{ys(v):.0f}' for k, v in enumerate(CURVE[s]))
        b += f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="10" stroke-linejoin="round"/>'
        b += text(xs(3) + 16, ys(CURVE[s][2]) + (70 if s == 'silos' else -30), lab, 44, col, 'start', 800)
    return svg(w, h, b)


# ---------- slides ----------
TITLE = '''<section class="slide dark center">
  <p class="eyebrow">AI-Agora</p>
  <h1>What can our AI agents<br>do together?</h1>
  <p class="muted">Nimrod Talmon · Digital Cooperation Lab · Ben-Gurion University</p>
  <p class="muted small"><a class="interactive" href="play">Play with it yourself →</a></p>
</section>'''

slides = [TITLE]
S = slides.append

S(f'''<section class="slide light">
  <p class="eyebrow">The setting</p>
  <h2>Everyone has an AI agent</h2>
  <div class="vis">{people_vis()}</div>
</section>''')

S(f'''<section class="slide light">
  <p class="eyebrow">The task</p>
  <h2>The neighborhood picks one activity</h2>
  <p class="sub">Who would join what? Only each person knows.</p>
  <div class="vis">{acts_vis()}</div>
</section>''')

S(f'''<section class="slide light">
  <p class="eyebrow">The catch</p>
  <h2>Questions cost attention</h2>
  <p class="sub">Each agent may ask its person only <span class="hl">2 questions</span>.</p>
  <div class="vis">{ask_vis()}</div>
</section>''')

S(demo('silos', 'Alone', 'Each agent asks 2 random questions',
       'Everyone would join the garden, but no agent knows it.'))

S(demo('central', 'Together', 'Agents share what they hear',
       'Search together with the first question, join with the second.'))

S(f'''<section class="slide dark center">
  <p class="eyebrow">The gain</p>
  <h1 class="huge" style="color:var(--orange)">× 3</h1>
  <p class="big">6 activities ÷ 2 questions</p>
  <p>Alone, agents can never guarantee more than 2 of every 6.<br>Together, everyone joins. No sharing scheme can gain more.</p>
  <p class="muted small">Paper (draft): The Value of an Agora: A Simple Start</p>
</section>''')

S(f'''<section class="slide light">
  <p class="eyebrow">The price</p>
  <h2>Sharing costs messages</h2>
  <p class="sub">Same questions, same outcome. Messages are cheap, but not free.</p>
  <div class="vis">{nets_vis()}</div>
</section>''')

S(f'''<section class="slide light">
  <p class="eyebrow">Beyond the example</p>
  <h2>Random neighborhoods: 40 people, 10 activities</h2>
  <div class="vis">{curve_vis()}</div>
</section>''')

S('''<section class="slide dark">
  <p class="eyebrow">Next</p>
  <h2>From one choice to a community</h2>
  <div class="rows ruled">
    <div class="row"><span class="n">1</span><p>Many activities at once: forming groups</p></div>
    <div class="row"><span class="n">2</span><p>Agents that already know their person</p></div>
    <div class="row"><span class="n">3</span><p>Agents with interests of their own</p></div>
  </div>
</section>''')

slides.append(TITLE)

STYLE = '''<style>
.sub { font-size: 44px; color: var(--gray); margin-top: -20px; }
.vis { margin-block: auto; display: flex; justify-content: center; }
.demo-row { display: flex; gap: 40px; align-items: flex-start; margin-top: -8px; }
.res { display: flex; flex-direction: column; gap: 10px; width: 330px; padding-top: 30px; }
.keys { display: flex; gap: 14px; margin-bottom: 20px; }
.kb { font: 700 28px Heebo, Arial, sans-serif; color: var(--dark); background: var(--card);
  border: 3px solid var(--gray-light); border-radius: 999px; padding: 8px 22px 8px 10px;
  display: inline-flex; align-items: center; gap: 10px; cursor: pointer; }
.kb i { font-style: normal; width: 40px; height: 40px; border-radius: 50%; background: var(--orange);
  display: inline-flex; align-items: center; justify-content: center; font-size: 24px; }
.joined { font-size: 150px; font-weight: 800; line-height: 1; }
.jn { color: var(--orange); }
.jd { font-size: 64px; color: var(--gray); }
.jl { font-size: 40px; font-weight: 700; margin-bottom: 26px; }
.stat { font-size: 36px; color: var(--gray); }
.stat b { color: var(--dark); }
.cell rect, .cell text { transition: fill .35s, stroke .35s; }
.hlrow { transition: opacity .4s; }
</style>'''

SCRIPT = '''<script>
(function () {
  const RUNS = ''' + json.dumps(RUNS) + ''';
  const OR = '#F7941D', GREEN = '#3E9B4F', PALE = '#FCE8D2', CARD = '#FDFDFB', GL = '#B9BCC1', DK = '#26282C';
  const timers = {};
  function reset(slide) {
    const id = slide.dataset.run;
    (timers[id] || []).forEach(clearTimeout); timers[id] = [];
    slide.querySelectorAll('.cell').forEach(c => {
      c.querySelector('rect').setAttribute('fill', CARD); c.querySelector('rect').setAttribute('stroke', GL);
      const t = c.querySelector('text'); t.textContent = '?'; t.setAttribute('fill', GL);
    });
    slide.querySelector('.hlrow').setAttribute('opacity', 0);
    slide.querySelector('.jn').textContent = '–';
    slide.querySelector('.sq').textContent = 0; slide.querySelector('.sm').textContent = 0;
  }
  function play(slide) {
    reset(slide);
    const id = slide.dataset.run, run = RUNS[id], T = timers[id];
    const rounds = [...new Set(run.asks.map(a => a[0]))];
    let t = 400, q = 0;
    rounds.forEach((r, ri) => {
      run.asks.filter(a => a[0] === r).forEach(([_, i, j, yes]) => {
        T.push(setTimeout(() => {
          const c = slide.querySelector(`.cell[data-i="${i}"][data-j="${j}"]`);
          c.querySelector('rect').setAttribute('fill', yes ? OR : '#E6E5E0');
          c.querySelector('rect').setAttribute('stroke', yes ? OR : '#E6E5E0');
          const tx = c.querySelector('text'); tx.textContent = yes ? '✓' : '✗'; tx.setAttribute('fill', yes ? DK : '#9A9C9F');
          slide.querySelector('.sq').textContent = ++q;
        }, t));
        t += 160;
      });
      if (id !== 'silos' && ri === 0) {
        T.push(setTimeout(() => slide.querySelector('.hlrow').setAttribute('opacity', 1), t + 300));
        t += 1300;
      }
    });
    T.push(setTimeout(() => {
      slide.querySelector('.jn').textContent = run.welfare;
      slide.querySelector('.sm').textContent = run.messages;
    }, t + 300));
  }
  const demos = [...document.querySelectorAll('.slide.demo')];
  demos.forEach(s => {
    s.querySelector('[data-act=run]').addEventListener('click', () => play(s));
    s.querySelector('[data-act=reset]').addEventListener('click', () => reset(s));
    // play when the slide is shown
    new MutationObserver(() => { if (s.classList.contains('active')) play(s); else reset(s); })
      .observe(s, { attributes: true, attributeFilter: ['class'] });
    if (s.classList.contains('active')) play(s);
  });
  // keys 1 (run) and 2 (reset) on a demo slide; arrows stay for slides
  document.addEventListener('keydown', (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const s = demos.find(d => d.classList.contains('active'));
    if (!s) return;
    if (e.key === '1') play(s); else if (e.key === '2') reset(s);
  });
})();
</script>'''

html = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI-Agora · What can our AI agents do together?</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@300..900&display=swap">
<link rel="stylesheet" href="assets/deck.css">
''' + STYLE + '''
</head>
<body>
<div id="stage">
''' + '\n'.join(f'<!-- {k+1} -->{s}' for k, s in enumerate(slides)) + '''
</div>
<script src="assets/deck.js"></script>
''' + SCRIPT + '''
</body>
</html>
'''
open(OUT, 'w').write(html)
print(len(slides), 'slides')
