"""Brute-force checks of the scale-paradox theorems (deterministic model).

1. Theorem 1 and Theorem 2 closed forms equal the robust announcement decision
   computed by enumerating every acceptance set, every pattern of wrong guesses and
   every invitation order, for all small communities.
2. Corollaries for growing communities (shares): windows, niche threshold, monotone agora.
"""
import itertools, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from agora.scale import (broadcast_forms, agora_forms, robust_announce_agora,
                         robust_announce_broadcast, broadcast_window, groups)

cases = mism = 0
for n in range(2, 8):
    for k in (2, 3, 4):
        for err in (0, 1, 2):
            for B in (0.5, 1, 2, 3, 5):
                c = 1
                for a in range(1, n + 1):
                    A = set(range(a))                 # by symmetry, any set of size a
                    ini = 0
                    rb = robust_announce_broadcast(n, A, k, B, c)
                    ra = robust_announce_agora(n, A, ini, k, B, c, err)
                    cases += 1
                    if rb != broadcast_forms(n, a, k, B, c) or ra != agora_forms(n, a, k, B, c, err):
                        mism += 1
                        print('MISMATCH', n, k, err, B, a, rb, ra)
print(f'Theorems 1-2 vs brute force: {cases} cases, {mism} mismatches')

# symmetry sanity check: a few non-initial sets give the same answer
for n, k, err, B, A, ini in [(6, 3, 1, 2, {1, 3, 4, 5}, 3), (7, 2, 2, 3, {0, 6}, 6), (6, 4, 0, 1, {0, 2, 3, 4, 5}, 2)]:
    assert robust_announce_agora(n, A, ini, k, B, 1, err) == agora_forms(n, len(A), k, B, 1, err)
print('symmetry spot checks passed')

# growing communities
k, R = 4, 100
viol = 0
for s in np.linspace(0.005, 0.99, 400):
    w = broadcast_window(s, k, R, 1, nmax=20000)
    niche = s < k / (k + R)
    if niche != (w is None):
        viol += 1; print('niche threshold fails', s, w)
    if w:
        lo, hi = w
        ns = [n for n in range(lo, hi + 1)]
        if not all(broadcast_forms(n, int(np.floor(s * n + 1e-9)), k, R, 1) for n in ns):
            viol += 1; print('not an interval', s)
        if hi > R / (1 - s) + 1e-9:
            viol += 1; print('window too long', s, hi)
print('broadcast corollary violations:', viol)

shares = 0.5 / np.arange(1, 301)
for err in (0, 10):
    g = [groups(n, shares, k, R, 1, err) for n in range(1, 4000)]
    assert all(x <= y for x, y in zip(g, g[1:])), 'agora not monotone'
    print(f'agora err={err}: nondecreasing; at n=3999 forms {g[-1]} of 300; all 300 from n = {next(n for n in range(1, 10**6) if groups(n, shares, k, R, 1, err) == 300)}')
gb = [groups(n, shares, k, R, 1) for n in range(1, 400)]
print('broadcast: max', max(gb), 'at n =', 1 + int(np.argmax(gb)), '; last n with a group:', max(n for n in range(1, 400) if gb[n - 1] > 0),
      '; types that ever form:', sum(broadcast_window(s, k, R, 1, 2000) is not None for s in shares))
