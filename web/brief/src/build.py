#!/usr/bin/env python3
"""Builds web/brief/index.html: the current state of the work as conference-style
slides (motivation, model, results, related work, summary), for Nimrod to grasp
quickly. Questions for him go in the chat, not on slides. It reuses the
explainer deck's drawing helpers and real runs.

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
             ('Few bits per voter', 'Mandal et al. 2019, 2020 · Kempe', 'one-shot; same "options ÷ budget" shape as silos'),
             ('Bandits, adaptivity', 'Gupta–Nagarajan–Singla · Colton 1963', 'independent tastes: adaptivity gains only log'),
             ('Agents for people', 'Habermolt 2026 · CalBench 2026', 'no question budget, no comparison to the best')]
    return '<div class="rw">' + ''.join(
        f'<div class="box"><h3>{t}</h3><p class="who">{w}</p><p class="diff">{x}</p></div>' for t, w, x in boxes) + '</div>'


# ---------- slides ----------
TITLE = f'''<section class="slide dark center">
  <p class="eyebrow">AI-Agora</p>
  <h1>The Value of an Agora</h1>
  <p class="big">When personal agents should share</p>
  <p class="muted">Nimrod Talmon · Ben-Gurion University · draft, {DATE}</p>
</section>'''

slides = [TITLE]
S = slides.append


def thm(label, title, box, why, vis, caption='', stack=False, pic_h=None):
    """Conference-style result slide: a formal statement in a box, the reason in
    one or two dry lines, and a picture on the right (or below, if stack)."""
    cap = f'<p class="cap">{caption}</p>' if caption else ''
    # one name per concept: the brief says silos / central, not alone / together
    vis = vis.replace('>alone<', '>silos<').replace('>together<', '>central<').replace('alone: ', 'silos: ').replace('together: ', 'central: ')
    return f'''<section class="slide light">
  <p class="eyebrow">{label}</p>
  <h2>{title}</h2>
  <div class="{'stack' if stack else 'split'}">
    <div><div class="box">{box}</div><div class="why">{why}</div></div>
    <div class="pic"{f' style="--ph:{pic_h}px"' if pic_h else ''}>{vis}{cap}</div>
  </div>
</section>'''


I = lambda v: '\\(' + v + '\\)'
M = I
n, m, b, p = I('n'), I('m'), I('b'), I('p')
bm, mb = M(r'b/m'), M(r'm/b')                    # in titles
BM, MB = M(r'\tfrac{b}{m}'), M(r'\tfrac{m}{b}')  # in boxes

S(f"""<section class="slide light">
  <p class="eyebrow">Motivation</p>
  <h2>Soon, everyone has an AI agent</h2>
  <p class="sub">Each question costs attention; no one is committed without a yes.</p>
  <div class="vis">{d.ask_vis()}</div>
</section>""")

S(thm('Model', 'Pick one option, ask little, only yes counts',
      f"""<p>{n} people, {m} options. Each person approves some options, unknown to everyone, its agent included.</p>
<p>A person’s agent may ask it at most {b} questions: “do you approve option {M('o')}?”</p>
<p><b>Outcome:</b> one option, with the people who said yes to it.<br><b>Welfare:</b> their number. <b>OPT:</b> the most approvers of any option.</p>""",
      'Running example: 8 people, 6 options, 2 questions each.',
      svg(830, 560, mini_grid({'asks': []}, 'who approves what: unknown', 0))))

S(thm('Model', 'Three settings, one measure',
      f"""<p><b>Silos:</b> agents ask alone, then report; a rule picks.</p>
<p><b>Central:</b> a coordinator sees all answers and decides who is asked what.</p>
<p><b>Grassroots:</b> agents message each other; all output the same outcome.</p>
<p><b>Guarantee:</b> {M(r'\min_{\text{communities}}\ \mathbb{E}[\text{welfare}]\,/\,\mathrm{OPT}')}. <b>Gain:</b> best central / best silos.</p>""",
      'Questions (attention) and messages are counted separately.',
      model_vis(), stack=True, pic_h=250))

S(thm('Theorem 1', f'Silos guarantee exactly {bm}',
      f'<p>In silos, the best guarantee is {BM}.</p>',
      f"""<p><b>≥</b> Each agent asks {b} random options; the rule picks the most-yes option. Every approver of the best option is found with probability {BM}.</p>
<p><b>≤</b> Let everyone approve one hidden option. An agent alone asks about it with probability at most {BM}.</p>""",
      grids_vis(('silos',)), f"{M('n=8,\\ m=6,\\ b=2')}: 3 join (expected 2.7)."))

S(thm('Theorem 2', f'Central gets everyone: a gain of {mb}',
      f"<p>If {M(r'n \ge m')}, {M(r'b \ge 2')}, and all approve one option, then central enrolls everyone. Hence the gain is {MB}, the most possible.</p>",
      '<p><b>Explore:</b> one question per person, spread over all options; only the favorite gets a yes. <b>Commit:</b> everyone asks about it.</p>',
      grids_vis(), stack=True, pic_h=350))

S(thm('Theorem 3', 'No shared tastes, no gain',
      f'<p>If only one person approves only one option, then no protocol in any setting guarantees more than {BM}.</p><p>So over all communities, the gain is 1.</p>',
      f"<p>Until that exact pair is asked, all answers are no. Only {M(r'n b')} of the {M(r'n m')} pairs can be asked.</p>",
      d.tastes_vis()))

S(thm('Theorem 4', 'A popular option: central nears OPT',
      f"""<p>If {M(r'b \ge 2')} and some option is approved by a fraction {p} of the people, then central’s expected welfare is at least</p>
<p class="eq">{M(r'\Big(1 - O\Big(\tfrac{1}{p}\sqrt{\tfrac{m \log (mn)}{n(b-1)}}\Big)\Big)\cdot \mathrm{OPT}')}</p>
<p>For fixed {m}, {b}, {p}: it tends to OPT as {n} grows; silos stay at {BM}.</p>""",
      f"<p><b>Explore:</b> about {M(r'\tfrac{n(b-1)}{m}')} random people per option estimate its popularity. <b>Commit:</b> all ask about the leader.</p>",
      d.scale_vis(), f"Simulation: popular option {M(r'\tfrac12')}, others {M(r'\tfrac14')}; {M(r'm=10,\ b=2')}."))

S(thm('Theorem 5', 'One question each: still nears OPT',
      f"<p>If {M('b=1')}, then sampling {M(r'(n/m)^{2/3}')} people per option, and asking everyone else about the leader, gives welfare that tends to OPT as {n} grows.</p>",
      f"<p>Explorers of losing options cannot join: about {M(r'm\,(n/m)^{2/3}')} people, a vanishing fraction.</p>",
      bars_vis(), f"Simulation: popular option {M(r'\tfrac12')}, {M('m=10')}."))

S(thm('Observation', 'In this model, grassroots ≥ central',
      '<p>For every budget, best grassroots ≥ best central: agents agree in advance that agent 1 coordinates. Same questions, same messages.</p>',
      '<p>What really separates them must be added to the model: trust in one agent, load per agent, privacy, incomplete networks.</p>',
      crown_vis()))

S(f'''<section class="slide light">
  <p class="eyebrow">Related work</p>
  <h2>Closest work, and the difference</h2>
  {related_vis()}
  <p class="why" style="margin-top:30px">New here: only a yes counts; three settings compared to OPT; questions and messages kept apart. The theorems are simple.</p>
</section>''')

S('''<section class="slide dark">
  <p class="eyebrow">Summary</p>
  <h2>Sharing pays exactly when tastes are shared</h2>
  <div class="rows ruled">
    <div class="row"><span class="n">1</span><p>Silos: \\(b/m\\). Central: up to OPT, never more than \\(m/b\\) times silos.</p></div>
    <div class="row"><span class="n">2</span><p>Open: sharper protocols, especially for one question each</p></div>
    <div class="row"><span class="n">3</span><p>Next: many options at once, each person in at most one (groups)</p></div>
    <div class="row"><span class="n">4</span><p>Next: model what separates grassroots from central</p></div>
  </div>
</section>''')

slides.append(TITLE)

KATEX_INIT = r"""<script>
document.addEventListener("DOMContentLoaded", function () {
  renderMathInElement(document.body, {delimiters: [{left: "\\(", right: "\\)", display: false}]});
});
</script>"""

STYLE = '''<style>
.sub { font-size: 42px; color: var(--gray); margin-top: -20px; }
.split { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 56px; align-items: center; margin-block: auto; }
.stack { display: flex; flex-direction: column; gap: 10px; margin-top: -10px; }
.stack .pic svg { max-height: var(--ph, 400px); }
.box { background: var(--card); border-left: 10px solid var(--orange); border-radius: 0 18px 18px 0;
  padding: 24px 32px; font-size: 36px; line-height: 1.33; }
.box p { margin: 0 0 16px; } .box p:last-child { margin: 0; }
.box .eq { text-align: center; font-size: 36px; }
.why { font-size: 31px; color: var(--gray); line-height: 1.33; margin-top: 22px; }
.why p { margin: 0 0 12px; }
.pic svg { width: 100%; height: auto; max-height: var(--ph, 560px); }
.pic .cap { font-size: 28px; color: var(--gray); text-align: center; margin-top: 10px; }
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
<title>The Value of an Agora · AI-Agora</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@300..900&display=swap">
<link rel="stylesheet" href="../assets/deck.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/auto-render.min.js"></script>
''' + KATEX_INIT + '''
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
