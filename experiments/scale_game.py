"""Strategic version, simulation: groups that happen in the best equilibrium vs n.
Random communities: m = r*n activities, shares drawn from 0.5/j (j = 1..50);
k = 4, b = 3, c = 0.05, r = 0.5. Broadcast: members see every post; agora: each
irrelevant post is shown with probability q. Writes runs/scale_game.csv."""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from agora.scale_game import random_community, largest_equilibrium_fast, shown_share

K, B, C, R = 4, 3, 0.05, 0.5
SHARES = 0.5 / np.arange(1, 51)
ns = sorted(set(int(round(x)) for x in np.geomspace(20, 4000, 36)))
rows = []
for n in ns:
    res = {'n': n, 'activities': 0, 'viable': 0, 'broadcast': 0, 'agora_q0.1': 0, 'agora_q0.01': 0,
           'listen_broadcast': 0, 'listen_q0.1': 0}
    S = 40
    for seed in range(S):
        rng = np.random.default_rng(1000 * n + seed)
        I, init = random_community(n, R, SHARES, rng)
        res['activities'] += I.shape[1] / S
        res['viable'] += (I.sum(0) >= K).sum() / S
        Lb, hb = largest_equilibrium_fast(I, init, ~I, K, B, C)
        res['broadcast'] += hb.sum() / S; res['listen_broadcast'] += Lb.mean() / S
        for q, key in ((0.1, 'agora_q0.1'), (0.01, 'agora_q0.01')):
            L, h = largest_equilibrium_fast(I, init, shown_share(I, q, rng), K, B, C)
            res[key] += h.sum() / S
            if q == 0.1:
                res['listen_q0.1'] += L.mean() / S
    rows.append(res); print({a: round(v, 2) for a, v in res.items()}, flush=True)
os.makedirs('runs', exist_ok=True)
with open('runs/scale_game.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
