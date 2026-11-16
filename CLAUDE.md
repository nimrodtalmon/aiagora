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
- Web app: `web/server.py` (standard library), live at https://talmonlab.bgu.ac.il/agora/ on port 5401 (entry in the talmonlab repo's server/apps.json; the server pulls this repo every 5 minutes). Links in the page must stay relative.
- `runs/` holds outputs; only small headline results are committed.
