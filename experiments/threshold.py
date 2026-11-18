"""Planted group with threshold k: silos (independent / convention) vs central EC.
Writes runs/threshold.csv: b,k,setting,mean,se."""
import csv, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from agora.run import run
from agora.data.synthetic import planted

n, m, T = 60, 12, 1000
rows = []
for b in [2, 3]:
    for k in [1, 2, 3, 4, 6, 8, 12]:
        for s in ["silos", "silos-convention", "central-ec"]:
            w = [run(planted(n, m, k, seed=10_000 + t), s, b, seed=t)["welfare_ratio"] for t in range(T)]
            rows.append(dict(b=b, k=k, setting=s, mean=np.mean(w), se=np.std(w) / np.sqrt(T)))
            print(rows[-1], flush=True)
os.makedirs("runs", exist_ok=True)
with open("runs/threshold.csv", "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
