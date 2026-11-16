"""Large communities with a popular option: share of the optimum vs community size.

    python experiments/pick_one_scale.py   -> paper/pick_one_scale.pdf, runs/pick_one_scale.png/.csv
"""
import csv, math, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from agora.pick_one import popular, run

M, B, SEEDS = 10, 2, 40
NS = [10, 20, 40, 80, 160, 320, 640]
ALPHAS = [0.2, 0.5]
rows = []
for a in ALPHAS:
    for n in NS:
        for s in ("silos", "central"):
            for seed in range(SEEDS):
                r = run(popular(n, M, a, seed=seed), s, B, seed=seed)
                rows.append(dict(alpha=a, n=n, setting=s, seed=seed, ratio=r["welfare_ratio"]))
with open("runs/pick_one_scale.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)


def bound(n, a):
    s = (B - 1) * (n // M)
    if s < 1:
        return 0
    return max(0.0, (1 - 1 / n) * (1 - (2 / a) * math.sqrt(math.log(2 * M * n) / (2 * s))))


fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
for ax, a in zip(axes, ALPHAS):
    for s, col, lab in (("silos", "#eb6834", "silos"), ("central", "#2a78d6", "Agora (central)")):
        ys = [np.mean([r["ratio"] for r in rows if r["alpha"] == a and r["n"] == n and r["setting"] == s]) for n in NS]
        ax.plot(NS, ys, color=col, lw=2, marker="o", ms=3.5, label=lab)
    ax.axhline(B / M, color="#999", lw=1, ls="--")
    ax.set_xscale("log"); ax.set_xticks(NS); ax.set_xticklabels([str(n) for n in NS])
    ax.set_title(f"popular option approved by {int(a*100)}%", fontsize=10)
    ax.set_xlabel("members")
    ax.grid(alpha=.25, lw=.6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
axes[0].set_ylabel("share of the optimum")
axes[0].set_ylim(0, 1.05)
axes[1].legend(frameon=False, loc="lower right", fontsize=8.5)
fig.tight_layout()
fig.savefig("paper/pick_one_scale.pdf"); fig.savefig("runs/pick_one_scale.png", dpi=150)
print("ok")
