"""Plot a sweep: welfare ratio vs attention budget, one panel per informedness.

    python experiments/plot_sweep.py runs/sweep1.csv
"""
import sys, csv
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

COLORS = {"central": "#2a78d6", "silos": "#eb6834"}
LABELS = {"central": "central Agora", "silos": "silos"}


def main(path):
    rows = list(csv.DictReader(open(path)))
    acc = defaultdict(list)
    for r in rows:
        acc[(r["setting"], float(r["informed"]), int(r["budget"]))].append(
            float(r["welfare_ratio"]))
    infs = sorted({k[1] for k in acc})
    budgets = sorted({k[2] for k in acc})
    fig, axes = plt.subplots(1, len(infs), figsize=(3.6 * len(infs), 3.2),
                             sharey=True)
    for ax, p in zip(axes, infs):
        for s in ("silos", "central"):
            ys = [sum(acc[(s, p, b)]) / len(acc[(s, p, b)]) for b in budgets]
            ax.plot(budgets, ys, color=COLORS[s], lw=2, marker="o", ms=4,
                    label=LABELS[s])
        ax.set_title(f"agents start knowing {int(p * 100)}%", fontsize=10)
        ax.set_xlabel("questions per member (budget)")
        ax.grid(alpha=0.25, lw=0.6)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    axes[0].set_ylabel("welfare / optimum")
    axes[0].set_ylim(0, 1.05)
    axes[-1].legend(frameon=False, loc="lower right")
    fig.tight_layout()
    out = path.replace(".csv", ".png")
    fig.savefig(out, dpi=150)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1])
