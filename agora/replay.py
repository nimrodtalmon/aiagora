"""Turn runs into replay frames and build the self-contained replay viewer.

    python -m agora.replay --budget 6 --informed 0 --seed 0 --out runs/replay.html

One frame per round: what the agents know so far, the best groups that this
knowledge allows, the questions asked and messages sent in that round, and
running totals. The last frame also carries the run's actual outcome.
"""
import argparse, json, os
import numpy as np
from .model import YES
from .tasks.groups import best_assignment, welfare, optimum
from .data.synthetic import neighborhood

VIEWER = os.path.join(os.path.dirname(__file__), "..", "web", "viewer.html")


def frames(inst, res):
    known = inst.initial.copy()
    by_round = {}
    for e in res["events"]:
        by_round.setdefault(e["t"], []).append(e)
    rounds = max(by_round) + 1 if by_round else 1
    out, att, msgs = [], 0, 0
    for t in range(rounds):
        asked, sent = [], 0
        for e in by_round.get(t, []):
            if e["type"] == "ask":
                known[e["agent"], e["j"]] = YES if e["answer"] else 0
                asked.append([e["agent"], e["j"]])
                att += 1
            elif e["type"] == "msg":
                sent += 1
        msgs += sent
        groups = best_assignment(known == YES, inst.min_size)
        out.append({"known": known.astype(int).tolist(), "asked": asked,
                    "groups": {str(j): g for j, g in groups.items()},
                    "attention": att, "messages": msgs, "sent": sent,
                    "served": welfare(groups)})
    out[-1]["groups"] = {str(j): g for j, g in (res["outcome"] or {}).items()}
    out[-1]["served"] = welfare(res["outcome"] or {})
    return out


def bundle(inst, results, params):
    return {"params": params, "n": inst.n, "m": inst.m,
            "min_size": inst.min_size, "names": inst.names,
            "accept": inst.accept.astype(int).tolist(),
            "initial": inst.initial.astype(int).tolist(),
            "optimum": optimum(inst.accept, inst.min_size),
            "runs": {s: {"frames": frames(inst, r), "welfare": r["welfare"],
                         "attention": r["attention"], "messages": r["messages"]}
                     for s, r in results.items()}}


def write_html(data, out):
    html = open(VIEWER).read().replace("/*AGORA_DATA*/null",
                                       json.dumps(data, separators=(",", ":")))
    with open(out, "w") as f:
        f.write(html)


def main():
    from .run import run, SETTINGS
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--m", type=int, default=12)
    ap.add_argument("--min-size", type=int, default=3)
    ap.add_argument("--informed", type=float, default=0.0)
    ap.add_argument("--budget", type=int, default=6)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="runs/replay.html")
    a = ap.parse_args()
    inst = neighborhood(a.n, a.m, a.min_size, informed=a.informed, seed=a.seed)
    results = {s: run(inst, s, budget=a.budget, seed=a.seed) for s in SETTINGS}
    write_html(bundle(inst, results, vars(a)), a.out)
    print(a.out)


if __name__ == "__main__":
    main()
