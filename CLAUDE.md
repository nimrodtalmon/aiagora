# CLAUDE.md — working on AI-Agora

## What this is
A simulation framework (later also a live web app) for AI-Agora. Not related to GLP or to SimGov.

## Spec sources
- BSF proposal (Overleaf 6acaf487a50a568cf03a2b52), section "Modeling the Setting": members, agents, estimates, questions (attention), messages (eps), settings silos / central / grassroots, value of the Agora.
- Position paper (Overleaf 69a8e9a80b768bda5423671e), section "Model": initiatives, acceptance sets, minimum group size, single membership, welfare = members served; agent layer; ratification.

## Design rules
1. Model objects are code objects; keep names aligned with the papers.
2. The engine enforces locality: a policy sees only its own view. Never let a policy read the instance.
3. The event log is the source of truth; costs and metrics are computed from it.
4. Two cost tiers stay separate: attention (questions to members) and messages.
5. Every new protocol is checked against the exact optimum and for feasibility.
6. Simulated, LLM and human members must be interchangeable behind the same interface.

## Conventions
- Python 3, numpy/scipy/matplotlib only for now; no build step for any future web UI (the talmonlab server has no Node).
- Web app: `web/server.py` (standard library, static pages only: the deck at / and `web/play.html` at /play), live at https://talmonlab.bgu.ac.il/agora/ on port 5401 (entry in the talmonlab repo's server/apps.json; the server pulls this repo every 5 minutes). Links in the page must stay relative.
- The explainer at /agora/ is a deck built by `web/deck/src/build.py` (never hand-edit `web/deck/index.html`); it uses the zutot deck engine copied to `web/deck/assets/` (arrows change slides, 1/2 drive demos, Esc goes home, no notes key). Its demos replay real runs of `agora/pick_one.py`.
- Research briefs: `web/brief/` (current results, at /brief/) and `web/directions/` (at /directions/), both built from `src/build.py` with the shared kit `web/kit.py`.
- `paper/` holds LaTeX: `paper/main.tex` (pick-one seed; figure from `experiments/pick_one_plot.py`) and `paper/scale/main.tex` (the scale paradox: model, theorems, proofs).
- The scale paradox model is analytic and outside the engine: `agora/scale.py` (deterministic worst-case model, closed forms plus the processes themselves), `experiments/scale.py` (exact counts for the brief), `experiments/scale_check.py` (brute-force check of every theorem). The earlier random version is kept in `agora/scale_random.py`. The strategic version (members listen or mute; best equilibrium) is `agora/scale_game.py`, checked by `experiments/scale_game_check.py`, simulated by `experiments/scale_game.py`; `experiments/scale_plot.py` makes the paper figures.
- `runs/` holds outputs; only small headline results are committed.
