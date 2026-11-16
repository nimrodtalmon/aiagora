"""Figure for the paper seed: share of the optimum, by questions per member.

    python experiments/pick_one_plot.py      -> paper/pick_one.pdf, runs/pick_one.csv
"""
import csv, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from agora.pick_one import hidden_favorite, random_popularity, run

N, M, SEEDS = 40, 10, 50
COLORS = {"silos": "#eb6834", "central": "#2a78d6", "grassroots": "#1baf7a"}
FAMILIES = {"hidden favorite": hidden_favorite, "random popularity": random_popularity}

rows = []
for fam, gen in FAMILIES.items():
    for b in range(1, M + 1):
        for s in ("silos", "central", "grassroots"):
            for seed in range(SEEDS):
                r = run(gen(N, M, seed=seed), s, b, seed=seed)
                rows.append(dict(family=fam, budget=b, setting=s, seed=seed,
                                 ratio=r["welfare_ratio"], attention=r["attention"],
                                 messages=r["messages"]))
os.makedirs("runs", exist_ok=True)
with open("runs/pick_one.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
for ax, fam in zip(axes, FAMILIES):
    bs = list(range(1, M + 1))
    ax.plot(bs, [b / M for b in bs], color="#999", lw=1, ls="--")
    for s in ("silos", "central"):           # grassroots coincides with central
        ys = [np.mean([r["ratio"] for r in rows if r["family"] == fam and
                       r["setting"] == s and r["budget"] == b]) for b in bs]
        ax.plot(bs, ys, color=COLORS[s], lw=2, marker="o", ms=3.5,
                label={"silos": "silos", "central": "Agora (central or grassroots)"}[s])
    ax.set_title(fam, fontsize=10)
    ax.set_xlabel("questions per member")
    ax.grid(alpha=.25, lw=.6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
axes[0].text(7.2, 0.62, "questions / options", color="#777", fontsize=8, rotation=31)
axes[0].set_ylabel("share of the optimum")
axes[0].set_ylim(0, 1.05)
axes[1].legend(frameon=False, loc="lower right", fontsize=8.5)
fig.tight_layout()
fig.savefig("paper/pick_one.pdf"); fig.savefig("runs/pick_one.png", dpi=150)
print("ok")
