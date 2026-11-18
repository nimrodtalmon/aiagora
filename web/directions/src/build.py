#!/usr/bin/env python3
"""Builds web/directions/index.html: research directions for AI-Agora, as a
research brief (conference-style slides). Content from the report
reports/Agora directions and apps.md. Reuses the brief deck's helpers.

    python3 web/directions/src/build.py
"""
import importlib.util, os

HERE = os.path.dirname(os.path.abspath(__file__))
BRIEF = os.path.join(HERE, '..', '..', 'brief', 'src', 'build.py')
spec = importlib.util.spec_from_file_location('briefbuild', BRIEF)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)                       # also rebuilds the brief (harmless)
svg, text, head, bot, thm, M = B.svg, B.text, B.head, B.bot, B.thm, B.M
OR, DK, GR, GL, CARD = B.OR, B.DK, B.GR, B.GL, B.CARD
OUT = os.path.join(HERE, '..', 'index.html')
DATE = 'November 18, 2026'


def tiles(items):
    return '<div class="tiles">' + ''.join(
        f'<div class="tile"><div class="big">{a}</div><div class="cap">{b}</div></div>' for a, b in items) + '</div>'


def rows(items, dark=False):
    return '<div class="rows ruled">' + ''.join(
        f'<div class="row"><span class="n">{k}</span><p>{t}</p></div>' for k, t in items) + '</div>'


def card_vis(title='Sunday 8am run', need=5, have=3, w=760):
    h = 520
    b = f'<rect x="20" y="20" width="{w-40}" height="{h-40}" rx="36" fill="{CARD}" stroke="{GL}" stroke-width="4"/>'
    b += text(w / 2, 110, title, 50, DK, weight=800)
    b += text(w / 2, 170, f'forms at {need} · no one is in before that', 30, GR)
    for k in range(need):
        x = w / 2 + (k - (need - 1) / 2) * 110
        b += head(x, 250, 30, DK if k < have else GL)
    b += f'<rect x="{w/2-200}" y="{h-150}" width="400" height="84" rx="42" fill="{OR}"/>'
    b += text(w / 2, h - 95, f'we need {need-have} more', 40, DK, weight=800)
    return svg(w, h, b)


def map_vis():
    w, h = 1300, 600
    X0, Y0, W, H = 300, 60, 960, 480
    b = ''
    cells = [(0, 0, 'shared assistant', 'pairs', 'schedulers (x.ai, Clara: shut down)', False),
             (1, 0, 'shared assistant', 'groups', 'ChatGPT, Meta AI, Instinct group chats', False),
             (0, 1, 'agent per person', 'pairs', 'Blockit, Boardy, Ditto, dating agents', False),
             (1, 1, 'agent per person', 'groups', 'empty: AI-Agora', True)]
    for cx, cy, _, _, label, hot in cells:
        x, y = X0 + cx * W / 2, Y0 + cy * H / 2
        b += f'<rect x="{x+8}" y="{y+8}" width="{W/2-16}" height="{H/2-16}" rx="22" fill="{OR if hot else CARD}" stroke="{OR if hot else GL}" stroke-width="3"/>'
        words = label.split(': ')
        if hot:
            b += text(x + W / 4, y + H / 4 + 16, label, 40, DK, weight=800)
        else:
            parts = label.split(', ')
            mid = (len(parts) + 1) // 2
            b += text(x + W / 4, y + H / 4 - 6, ', '.join(parts[:mid]) + (',' if parts[mid:] else ''), 30, DK)
            b += text(x + W / 4, y + H / 4 + 36, ', '.join(parts[mid:]), 30, DK)
    b += text(X0 + W / 4, Y0 - 16, 'pairs', 34, GR, weight=700) + text(X0 + 3 * W / 4, Y0 - 16, 'new groups', 34, GR, weight=700)
    b += text(X0 - 20, Y0 + H / 4 + 10, 'one shared AI', 32, GR, 'end', 700)
    b += text(X0 - 20, Y0 + 3 * H / 4 + 10, 'agent per person', 32, GR, 'end', 700)
    return svg(w, h, b)


def twin_vis():
    w, h = 820, 520
    b = head(130, 150, 56, DK) + text(130, 360, 'person', 34, GR, weight=700)
    b += f'<circle cx="410" cy="150" r="56" fill="none" stroke="{OR}" stroke-width="8" stroke-dasharray="14 10"/>'
    b += f'<path d="M{410-90} {150+146} a90 90 0 0 1 180 0" fill="none" stroke="{OR}" stroke-width="8" stroke-dasharray="14 10"/>'
    b += text(410, 360, 'twin: 80% yes', 34, GR, weight=700)
    b += bot(690, 180, 110) + text(690, 360, 'agent', 34, GR, weight=700)
    b += f'<path d="M690 400 L690 450 L130 450 L130 400" fill="none" stroke="{OR}" stroke-width="5"/>'
    b += text(410, 500, 'asks the person only when unsure', 30, DK, weight=700)
    return svg(w, h, b)


def loop_vis():
    w, h = 1500, 470
    steps = ['intention', 'agents pick likely people', 'one question each', 'forms at minimum', 'short? share the card']
    b = ''
    for k, s in enumerate(steps):
        x = 30 + k * 300
        hot = k == 4
        b += f'<rect x="{x}" y="120" width="250" height="190" rx="24" fill="{OR if hot else CARD}" stroke="{OR if hot else GL}" stroke-width="3"/>'
        words = s.split(' ')
        lines = [' '.join(words[:2]), ' '.join(words[2:])] if len(words) > 2 else [s]
        for li, ln in enumerate(lines):
            b += text(x + 125, 205 + li * 42 - (20 if len(lines) > 1 else 0), ln, 32, DK, weight=700)
        b += text(x + 125, 90, str(k + 1), 40, OR, weight=800)
        if k < 4:
            b += f'<path d="M{x+258} 215 l26 0" stroke="{GR}" stroke-width="5"/><path d="M{x+284} 215 l-12 -10 l0 20 z" fill="{GR}"/>'
    b += f'<path d="M{30+4*300+125} 320 C {30+4*300+125} 430, {30+125} 430, {30+125} 320" fill="none" stroke="{OR}" stroke-width="5" stroke-dasharray="12 10"/>'
    b += text(w / 2, 455, 'each short card recruits new people: the growth loop', 32, GR, weight=700)
    return svg(w, h, b)


def link_vis():
    w, h = 1300, 420
    b = ''
    for x, title, lines in ((60, 'Paper', ['threshold groups + twins', 'adaptivity gap, bounds', 'silos / central / grassroots']),
                            (760, 'App', ['the “need 2 more” card', 'one bounded community', 'event log of every question'])):
        b += f'<rect x="{x}" y="40" width="480" height="300" rx="28" fill="{CARD}" stroke="{OR}" stroke-width="5"/>'
        b += text(x + 240, 110, title, 48, DK, weight=800)
        for k, ln in enumerate(lines):
            b += text(x + 240, 175 + k * 50, ln, 32, DK)
    b += f'<path d="M560 150 L740 150" stroke="{OR}" stroke-width="6"/><path d="M740 150 l-18 -12 l0 24 z" fill="{OR}"/>'
    b += f'<path d="M740 240 L560 240" stroke="{GR}" stroke-width="6"/><path d="M560 240 l18 -12 l0 24 z" fill="{GR}"/>'
    b += text(650, 130, 'protocols', 28, DK) + text(650, 285, 'costs, data', 28, DK)
    b += text(650, 395, 'each logged instance solved exactly offline: compare to OPT', 30, GR, weight=700)
    return svg(w, h, b)


TITLE = f'''<section class="slide dark center">
  <p class="eyebrow">AI-Agora</p>
  <h1>Agents that form groups</h1>
  <p class="big">Evidence, open problems, and an app</p>
  <p class="muted">Nimrod Talmon · Ben-Gurion University · draft, {DATE}</p>
</section>'''

slides = [TITLE]
S = slides.append

S(f'''<section class="slide light">
  <p class="eyebrow">Evidence · Edge Esmeralda Agent Village, June 2026</p>
  <h2>Agents are fast; the human yes is the bottleneck</h2>
  <div class="vis">{tiles([('239', 'personal agents, one per attendee'),
                           ('147', 'accepted intros out of 9,688 possible'),
                           ('4.9 s', 'median agent negotiation'),
                           ('20 h', 'median wait for both humans’ yes')])}</div>
  <p class="why">Source: Cosmos Institute, July 2026. Also: popular people were swamped; a $10k fund was allocated before owners confirmed.</p>
</section>''')

S(f'''<section class="slide light">
  <p class="eyebrow">Evidence · failures across deployments</p>
  <h2>Each failure is a constraint of the model</h2>
  {rows([('1', 'Confirmation skipped when optional → <b>only a yes enrolls</b>'),
         ('2', 'Popular people swamped → <b>a question budget per person</b>'),
         ('3', 'Agents invent details about their person → <b>predictions never count as consent</b>'),
         ('4', 'Agents take the first offer (82–100%) → <b>compare protocols to OPT</b>')])}
  <p class="why">Sources: Cosmos Institute 2026; Habermolt (arXiv 2605.24413); Magentic Marketplace (arXiv 2510.25779).</p>
</section>''')

S(f'''<section class="slide light">
  <p class="eyebrow">Landscape</p>
  <h2>The open slot: an agent per person, new groups</h2>
  <div class="vis">{map_vis()}</div>
</section>''')

S(f'''<section class="slide light">
  <p class="eyebrow">What spreads</p>
  <h2>A link that is useless until others answer</h2>
  <div class="vis">{tiles([('98%', 'of Doodle users came by invite (2011, 10M monthly)'),
                           ('+400%', 'Partiful monthly app users in a year (2025)'),
                           ('0', 'accounts needed to answer When2meet'),
                           ('325→220', 'Timeleft cities, grown by paid ads')])}</div>
  <p class="why">Stranger matching has no invite loop: a member does not know whom to invite.</p>
</section>''')

S(thm('Problem 1 · most open', 'Threshold groups with consent',
      f"""<p>{M('n')} members, {M('m')} initiatives (acceptances unknown); initiative {M('j')} forms only with at least {M('k_j')} members.</p>
<p>An agent may ask its member at most {M('b')} questions: “join {M('j')} if it forms?”</p>
<p><b>Outcome:</b> disjoint groups of members who said yes. <b>Welfare:</b> members placed.</p>""",
      '<p><b>New:</b> groups with a minimum, not pairs; questions to failing groups are wasted.</p>',
      card_vis()))

S(thm('Problem 2 · safest', 'A twin predicts, the person decides',
      f"""<p>An agent holds a prediction of its member (a “twin”), error unknown, and asks at most {M('b')} questions.</p>
<p>The twin only picks whom to ask.</p>
<p><b>Goal:</b> good if the twin is right, safe if not.</p>""",
      '<p><b>Why now:</b> twins reach 83–86% of a person’s own consistency (Park et al. 2024).</p>',
      twin_vis()))

S(f'''<section class="slide light">
  <p class="eyebrow">Problems 3–5</p>
  <h2>Three more, from the same model</h2>
  {rows([('3', '<b>Grassroots vs central:</b> separate them by load per agent, privacy, dropouts'),
         ('4', '<b>Incentives of question order:</b> agents exaggerate flexibility to be asked first'),
         ('5', '<b>Value of pooling:</b> correlated tastes save questions, but leak information')])}
  <p class="why">3 extends our single-option observation; 4 is the hardest; 5 is the formal “value of the Agora”.</p>
</section>''')

S(f'''<section class="slide light">
  <p class="eyebrow">App concept</p>
  <h2>“We need 2 more”: a card that recruits</h2>
  <div class="vis">{loop_vis()}</div>
  <p class="why">Inside the app is Problem 1: whom to ask, in what order, under a cap of questions per person.</p>
</section>''')

S(f'''<section class="slide light">
  <p class="eyebrow">Direction</p>
  <h2>One paper, one testbed</h2>
  <div class="vis">{link_vis()}</div>
  <p class="why">Start in a bounded community (a conference, a campus): density, safety, and a few hundred people suffice.</p>
</section>''')

S(f'''<section class="slide dark">
  <p class="eyebrow">Summary</p>
  <h2>Price the human yes, not the message</h2>
  {rows([('1', 'Evidence: agents are fast; consent and attention are the bottleneck'),
         ('2', 'Open theory: threshold groups with consent, guided by twins'),
         ('3', 'App: the “need 2 more” card gives stranger matching an invite loop'),
         ('4', 'Check first: a targeted search on coalition formation with costly questions')])}
</section>''')

slides.append(TITLE)

STYLE = B.STYLE.replace('</style>', '''
.tile .big { font-size: 96px; }
.why { margin-top: 28px; }
</style>''')

html = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agents that form groups · AI-Agora</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@300..900&display=swap">
<link rel="stylesheet" href="../assets/deck.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/auto-render.min.js"></script>
''' + B.KATEX_INIT + STYLE + '''
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
