#!/usr/bin/env python3
"""Builds web/brief/index.html: research brief on the scale paradox (a broadcast
channel vs agent routing for forming groups). Uses the shared kit (web/kit.py)
and the real runs in runs/scale.csv (experiments/scale.py).

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


def chart_vis(which=('viable', 'agora_01', 'agora_03', 'broadcast'), YM=300, ticks=(0, 100, 200, 300), vline=None, hlines=(), w=1000):
    h = 640
    X0, X1, Y0, Y1 = 130, w - 140, 540, 50
    lx = lambda n: X0 + (math.log(n) - math.log(10)) / (math.log(2560) - math.log(10)) * (X1 - X0)
    Y = lambda v: Y0 - min(v, YM) / YM * (Y0 - Y1)
    b = ''
    for v in ticks:
        b += f'<line x1="{X0}" y1="{Y(v):.0f}" x2="{X1}" y2="{Y(v):.0f}" stroke="#E6E5E0" stroke-width="2"/>'
        b += text(X0 - 16, Y(v) + 10, str(v), 26, GR, 'end')
    for n in (10, 40, 160, 640, 2560):
        b += text(lx(n), Y0 + 40, str(n), 26, GR)
    b += text((X0 + X1) / 2, Y0 + 84, 'community size n (members)', 28, GR, weight=700)
    b += text(34, (Y0 + Y1) / 2, 'groups formed', 28, GR, weight=700, extra=f'transform="rotate(-90 34 {(Y0+Y1)/2})"')
    if vline:
        x = lx(vline[0])
        b += f'<line x1="{x:.0f}" y1="{Y1}" x2="{x:.0f}" y2="{Y0}" stroke="{OR}" stroke-width="3" stroke-dasharray="10 8"/>'
        b += text(x + 12, Y1 + 30, vline[1], 26, OR, 'start', 700)
    for v, lab in hlines:
        b += f'<line x1="{X0}" y1="{Y(v):.0f}" x2="{X1}" y2="{Y(v):.0f}" stroke="{OR}" stroke-width="3" stroke-dasharray="10 8"/>'
        b += text(X0 + 10, Y(v) - 12, lab, 26, OR, 'start', 700)
    series = {'viable': (GL, 'viable', True), 'agora_01': (OR, 'agora, 10% wrong', False),
              'agora_03': ('#E8B07A', 'agora, 30% wrong', False), 'broadcast': (DK, 'broadcast', False)}
    for key in which:
        col, lab, dash = series[key]
        pts = [(lx(int(r['n'])), Y(float(r[key]))) for r in RUNS]
        da = ' stroke-dasharray="10 8"' if dash else ''
        b += f'<polyline fill="none" stroke="{col}" stroke-width="5"{da} points="' + ' '.join(f'{x:.0f},{y:.0f}' for x, y in pts) + '"/>'
        if not dash:
            for x, y in pts:
                b += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="6" fill="{col}" stroke="#fff" stroke-width="2"/>'
        x, y = pts[-1]
        b += text(x + 14, y + 9, lab, 26, DK, 'start', 700)
    return svg(w + 120, h, b)


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
      f"""<p>{n} members, activity types {M('t')}. A member accepts {M('t')} with probability {M('p_t')} (<b>popularity</b>), independently.</p>
<p>Type {M('t')} has an <b>initiator</b> who accepts it. Its group forms if at least {k} reached members accept.</p>
<p>The initiator gains {B} if it forms, and pays {c} per reached member who does not accept (<b>bothered</b>). It announces iff</p>
<p class="eq">{M(r'B \cdot \Pr[\text{forms}] \ \ge\  c \cdot \mathbb{E}[\text{bothered}]')}</p>""",
      f'<b>Welfare:</b> groups formed. The cost {c} is social: fear of spamming.',
      kit.card_vis(), wide=True))

S(thm('Model', 'Two channels',
      f"""<p><b>Broadcast:</b> an announcement reaches all other {M('n-1')} members.</p>
<p><b>Agora:</b> each member's agent guesses whether its member accepts {M('t')}, wrong with probability {err}. The initiator's agent invites, in random order, only members guessed to accept, and stops at {M('k-1')} acceptances.</p>
<p><b>Benchmark:</b> types with at least {k} acceptors (viable).</p>""",
      'Orange: accepts. In the agora, agents guess wrong once each way.',
      channel_vis(), stack=True, pic_h=230))

S(thm('Theorem 1', 'Broadcast: groups appear, then vanish',
      f"""<p>In broadcast, type {M('t')} is announced only if {M(r'(1-p_t)(n-1) \le \tfrac{B}{c}')}.</p>
<p>So if all {M(r'p_t \le \bar p < 1')}, then no group forms once {M(r'n > 1 + \tfrac{B}{c(1-\bar p)}')}.</p>
<p>At {M('n=k')}, {M('t')} is announced iff {M(r'B\,p_t^{\,k-1} \ge c\,(k-1)(1-p_t)')}.</p>""",
      f"""<p>Expected bothered: {M(r'(1-p_t)(n-1)')}, while {M(r'\Pr[\text{forms}] \le 1')}. Niche types drop out first.</p>""",
      chart_vis(('broadcast',), YM=10, ticks=(0, 5, 10), vline=(201, 'n = 201'))))

S(thm('Theorem 2', f'Agora: groups keep forming as {n} grows',
      f"""<p>Let {M(r'\mathit{bother}_t = (k-1)\tfrac{1-r_t}{r_t}')}. For every {n}, at most {M(r'\mathit{bother}_t')} members are bothered in expectation.</p>
<p>So if {M(r'\mathit{bother}_t < \tfrac{B}{c}')}, then for all large {n}, {M('t')} is announced and forms with probability tending to 1.</p>""",
      f"""<p>{M('r_t')}: the chance an invited member accepts. Inviting stops at {M('k-1')} yeses, so the noes are at most negative binomial, for any {n}.</p>""",
      chart_vis(('agora_01', 'agora_03'), YM=160, ticks=(0, 50, 100, 150), hlines=((150, 'limit 150'), (39, 'limit 39')))))

S(thm('Simulation', 'Peak for broadcast, growth for the agora',
      f"""<p>300 types, {M(r'p_t = \tfrac{0.5}{t}')}, {M('k=4')}, {M(r'\tfrac{B}{c} = 100')}.</p>
<p>Broadcast peaks at 9.4 groups at 84 members; none above 201.</p>
<p>The agora tends to 150 and 39 groups, for {M(r'\mathit{err}')} of 0.1 and 0.3.</p>""",
      '<p>All expectations exact; they match direct sampling within 0.005.</p>',
      chart_vis()))

S(f'''<section class="slide light">
  <p class="eyebrow">Related work</p>
  <h2>Closest work, and the difference</h2>
  {related_vis()}
  <p class="why" style="margin-top:30px">New here: threshold groups found through one channel whose cost falls on all members; the number of groups as a function of community size.</p>
</section>''')

S('''<section class="slide light">
  <p class="eyebrow">Summary</p>
  <h2>Broadcast cost grows with \\(n\\); routing cost with \\(k\\)</h2>
  <div class="rows ruled">
    <div class="row"><span class="n">1</span><p>Broadcast: groups appear, then vanish as size grows; niche ones first</p></div>
    <div class="row"><span class="n">2</span><p>Agora: groups keep forming; agent accuracy sets how many</p></div>
    <div class="row"><span class="n">3</span><p>Open: a per-member budget of invitations; strategic initiators</p></div>
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
