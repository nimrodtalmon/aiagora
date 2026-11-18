"""Scale paradox curves (deterministic model): groups formed vs community size n.
Type t has share s_t = 0.5/t (t = 1..300); a_t = floor(s_t n); k = 4; B/c = 150.
Writes runs/scale.csv (n, broadcast, agora_err0, agora_err10, viable) and
runs/scale_windows.csv (t, share, broadcast window, agora start for err 0 and 10)."""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from agora.scale import groups, broadcast_window

K, R, T = 4, 150, 300
shares = 0.5 / np.arange(1, T + 1)
ns = sorted(set(int(round(x)) for x in np.geomspace(4, 20000, 120)))
os.makedirs('runs', exist_ok=True)
with open('runs/scale.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['n', 'broadcast', 'agora_err0', 'agora_err10', 'viable'])
    for n in ns:
        viable = sum(int(np.floor(s * n + 1e-9)) >= K for s in shares)
        w.writerow([n, groups(n, shares, K, R, 1), groups(n, shares, K, R, 1, 0), groups(n, shares, K, R, 1, 10), viable])
with open('runs/scale_windows.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['t', 'share', 'b_lo', 'b_hi', 'agora0_from', 'agora10_from'])
    for t, s in enumerate(shares[:40], 1):
        win = broadcast_window(s, K, R, 1, nmax=2000)
        a0 = next(n for n in range(1, 10**6) if np.floor(s * n + 1e-9) >= K)
        a10 = next(n for n in range(1, 10**6) if np.floor(s * n + 1e-9) >= K + 10)
        w.writerow([t, s, win[0] if win else '', win[1] if win else '', a0, a10])
print('threshold share', K / (K + R), '-> types that ever form by broadcast:', sum(s >= K / (K + R) for s in shares))
