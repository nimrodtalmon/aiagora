"""Scale paradox curves: expected groups formed vs community size n.
Writes runs/scale.csv: n, viable, broadcast, agora_eps0.1, agora_eps0.3."""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agora.scale import popularity, groups, viable

ps, k, B, c = popularity(T=300, top=0.5, zipf=1.0), 4, 100, 1
rows = []
for j in range(17):
    n = int(round(10 * 2 ** (j / 2)))
    r = dict(n=n, viable=viable(n, ps, k), broadcast=groups(n, ps, k, B, c),
             agora_01=groups(n, ps, k, B, c, eps=0.1, seed=j), agora_03=groups(n, ps, k, B, c, eps=0.3, seed=j))
    rows.append(r); print({a: round(v, 1) for a, v in r.items()}, flush=True)
os.makedirs('runs', exist_ok=True)
with open('runs/scale.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
