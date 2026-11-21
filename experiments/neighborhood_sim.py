"""Group chat vs agora on synthetic neighborhoods (conditional commitments).
Writes runs/neighborhood_eager.csv (vary the share of eager members) and
runs/neighborhood_n.csv (vary the neighborhood size); also compares greedy vs exact."""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from agora.neighborhood import neighborhood, greedy_agora, exact_agora, board

K = 4
POPS = [0.30, 0.22, 0.16, 0.12, 0.09, 0.07, 0.05, 0.04, 0.03, 0.02]   # ten activities, popular to niche
os.makedirs('runs', exist_ok=True)


def run(n, eager, seeds=20, exact=True):
    out = dict(board=0, agora=0, exact=0, board_groups=0, agora_groups=0, interested=0)
    for sd in range(seeds):
        rng = np.random.default_rng(10_000 + sd)
        for A, th in neighborhood(n, POPS, eager=eager, seed=sd):
            out['interested'] += len(A) / seeds
            b, bg = board(A, th, K, rng)
            g, gg = greedy_agora(A, th, K)
            out['board'] += b / seeds; out['agora'] += g / seeds
            out['board_groups'] += len(bg) / seeds; out['agora_groups'] += len(gg) / seeds  # greedy groups
            if exact:
                out['exact'] += exact_agora(A, th, K) / seeds
    return out


rows = []
for eager in [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0]:
    r = run(100, eager); r['eager'] = eager; rows.append(r); print('eager', {a: round(v, 1) for a, v in r.items()}, flush=True)
with open('runs/neighborhood_eager.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

rows = []
for n in [25, 50, 100, 200, 400]:
    r = run(n, 0.1); r['n'] = n; rows.append(r); print('n', {a: round(v, 1) for a, v in r.items()}, flush=True)
with open('runs/neighborhood_n.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

r = run(100, 0.1, seeds=20)
print('greedy vs exact (n=100, 20 neighborhoods):', round(r['agora'], 1), round(r['exact'], 1))
