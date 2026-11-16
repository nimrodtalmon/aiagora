"""Plot a sweep: welfare ratio vs attention budget, one panel per informedness.

    python experiments/plot_sweep.py runs/sweep1.csv
"""
import sys, csv
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

COLORS = {"central": "#2a78d6", "silos": "#eb6834", "grassroots": "#1baf7a"}
LABELS = {"central": "central Agora", "silos": "silos",
          "grassroots": "grassroots Agora"}
ORDER = ("silos", "central", "grassroots")


def main(path):
    rows = list(csv.DictReader(open(path)))
    acc, msg = defaultdict(list), defaultdict(list)
    for r in rows:
        key = (r["setting"], float(r["informed"]), int(r["budget"]))
        acc[key].append(float(r["welfare_ratio"]))
        msg[key].append(int(r["messages"]))
    settings = [s for s in ORDER if any(k[0] == s for k in acc)]
    infs = sorted({k[1] for k in acc})
    budgets = sorted({k[2] for k in acc})
    fig, grid = plt.subplots(2, len(infs), figsize=(3.6 * len(infs), 5.8),
                             sharey="row", sharex=True)
    axes, maxes = grid[0], grid[1]
    for ax, mx, p in zip(axes, maxes, infs):
        for s in settings:
            ys = [sum(msg[(s, p, b)]) / len(msg[(s, p, b)]) for b in budgets]
            if max(ys) > 0:                 # silos send no messages at all
                mx.plot(budgets, ys, color=COLORS[s], lw=2, marker="o", ms=4)
        mx.set_yscale("log")
        mx.set_xlabel("questions per member (budget)")
        mx.grid(alpha=0.25, lw=0.6)
        for side in ("top", "right"):
            mx.spines[side].set_visible(False)
        for s in settings:
            ys = [sum(acc[(s, p, b)]) / len(acc[(s, p, b)]) for b in budgets]
            ax.plot(budgets, ys, color=COLORS[s], lw=2, marker="o", ms=4,
                    label=LABELS[s])
        ax.set_title(f"agents start knowing {int(p * 100)}%", fontsize=10)
        ax.grid(alpha=0.25, lw=0.6)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    axes[0].set_ylabel("welfare / optimum")
    axes[0].set_ylim(0, 1.05)
    maxes[0].set_ylabel("messages (log scale; silos: none)")
    axes[-1].legend(frameon=False, loc="lower right")
    fig.tight_layout()
    out = path.replace(".csv", ".png")
    fig.savefig(out, dpi=150)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1])
