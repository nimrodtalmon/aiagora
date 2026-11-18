"""Shared kit for the research-brief decks (web/brief, web/directions):
drawing helpers from the explainer deck, the thm() result slide, CSS and KaTeX."""
import importlib.util, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('deckbuild', os.path.join(HERE, 'deck', 'src', 'build.py'))
d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(d)                      # also rebuilds the explainer deck (harmless)
svg, text, head, bot = d.svg, d.text, d.head, d.bot
OR, DK, GR, GL, CARD = d.OR, d.DK, d.GR, d.GL, d.CARD
N = d.N
I = lambda v: '\\(' + v + '\\)'
M = I


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

