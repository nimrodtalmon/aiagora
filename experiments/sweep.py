"""Sweep: welfare ratio of silos vs central, by attention budget and informedness.

    python experiments/sweep.py --seeds 20 --out runs/sweep1
"""
import argparse, csv, os, sys, time
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from agora.run import run
from agora.data.synthetic import neighborhood


def one(args):
    setting, b, informed, seed, n, m, k = args
    inst = neighborhood(n, m, k, informed=informed, seed=seed)
    r = run(inst, setting, budget=b, seed=seed)
    return dict(setting=setting, budget=b, informed=informed, seed=seed,
                welfare_ratio=r["welfare_ratio"], attention=r["attention"],
                messages=r["messages"], rounds=r["rounds"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--m", type=int, default=12)
    ap.add_argument("--min-size", type=int, default=3)
    ap.add_argument("--informed", default="0,0.3,0.6")
    ap.add_argument("--out", default="runs/sweep")
    a = ap.parse_args()
    infs = [float(x) for x in a.informed.split(",")]
    jobs = [(s, b, p, seed, a.n, a.m, a.min_size)
            for s in ("silos", "central") for b in range(1, a.m + 1)
            for p in infs for seed in range(a.seeds)]
    t = time.time()
    with ProcessPoolExecutor() as ex:
        rows = list(ex.map(one, jobs, chunksize=8))
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out + ".csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} runs in {time.time() - t:.0f}s -> {a.out}.csv")


if __name__ == "__main__":
    main()
