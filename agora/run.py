"""Run one protocol on one instance and evaluate it.

    python -m agora.run --setting central --n 30 --budget 4 --informed 0.3 --out runs/x.json
"""
import argparse, json
import numpy as np
from .engine import Engine
from .tasks.groups import optimum, welfare, is_feasible
from .data.synthetic import neighborhood
from .protocols import groups_silos, groups_central

SETTINGS = {"silos": groups_silos, "central": groups_central}


def run(inst, setting, budget=None, eps=0.01, seed=0):
    rng = np.random.default_rng(seed)
    parts = SETTINGS[setting].make(inst, rng)
    res = Engine(inst, attention_budget=budget, eps=eps, **parts).run()
    out = res["outcome"] or {}
    assert is_feasible(out, inst.accept, inst.min_size)
    opt = optimum(inst.accept, inst.min_size)
    res["welfare"] = welfare(out)
    res["opt"] = opt
    res["welfare_ratio"] = 1.0 if opt == 0 else welfare(out) / opt
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--setting", choices=SETTINGS, default="central")
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--m", type=int, default=12)
    ap.add_argument("--min-size", type=int, default=3)
    ap.add_argument("--informed", type=float, default=0.0)
    ap.add_argument("--budget", type=int, default=None)
    ap.add_argument("--eps", type=float, default=0.01)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    inst = neighborhood(a.n, a.m, a.min_size, informed=a.informed, seed=a.seed)
    res = run(inst, a.setting, a.budget, a.eps, a.seed)
    summary = {k: v for k, v in res.items() if k not in ("events", "outcome")}
    print(json.dumps(summary, indent=1))
    if a.out:
        with open(a.out, "w") as f:
            json.dump({"instance": inst.to_json(), "setting": a.setting,
                       "params": vars(a), **res}, f, default=int)


if __name__ == "__main__":
    main()
