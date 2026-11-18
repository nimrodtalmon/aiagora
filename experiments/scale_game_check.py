"""Brute-force checks for the strategic version (agora/scale_game.py).

1. Uniform communities: enumerate every listening profile, find all equilibria, and
   check Theorem 3: if the condition holds, all-listen is an equilibrium and every
   activity happens; otherwise no activity happens in any equilibrium (and the only
   equilibrium is all-mute when members see at least one irrelevant post).
2. Random communities: best-response iteration from all-listen returns an
   equilibrium that is above every equilibrium and that every member weakly prefers.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from agora.scale_game import (uniform, shown_irrelevant, all_equilibria, largest_equilibrium,
                              happening, payoffs, uniform_works)

rng = np.random.default_rng(0)
cases = bad = 0
for n in range(4, 10):
    for r in (1, 2, 3):
        for a in range(1, n + 1):
            if r * a > n * r:  # every member interested in r*a of the r*n activities
                continue
            I, init = uniform(n, r, a)
            if set(I.sum(0)) != {a}:
                continue
            irrelevant = r * n - r * a
            for Q in sorted({0, 1, irrelevant // 3, irrelevant}):
                if Q > irrelevant:
                    continue
                F = shown_irrelevant(I, Q, rng)
                for k in (2, 3, 4):
                    for b in (1, 2, 4):
                        for c in (0.1, 0.3, 1.0):
                            eqs = all_equilibria(I, init, F, k, b, c)
                            works = uniform_works(n, r, a, k, b, c, Q)
                            top = np.ones(n, dtype=bool)
                            top_is_eq = any(e.all() for e in eqs)
                            hap_top = happening(I, init, top, k)[0].all()
                            if works:
                                ok = top_is_eq and hap_top
                            else:
                                ok = all(not happening(I, init, e, k)[0].any() for e in eqs)
                                if Q >= 1 and a >= k:
                                    ok = ok and len(eqs) == 1 and not eqs[0].any()
                            cases += 1
                            if not ok:
                                bad += 1
                                if bad < 10:
                                    print('FAIL', n, r, a, Q, k, b, c, works, [e.astype(int) for e in eqs])
print(f'Theorem 3 vs brute force: {cases} cases, {bad} failures')

# 2. random communities: the largest equilibrium
cases = bad = 0
for trial in range(300):
    n = int(rng.integers(3, 9)); m = int(rng.integers(2, 10))
    I = rng.random((n, m)) < rng.uniform(0.2, 0.8)
    for t in range(m):
        if not I[:, t].any():
            I[rng.integers(n), t] = True
    init = np.array([rng.choice(np.nonzero(I[:, t])[0]) for t in range(m)])
    F = (~I) & (rng.random((n, m)) < rng.uniform(0, 1))
    k = int(rng.integers(2, 4)); b = int(rng.integers(1, 4)); c = float(rng.choice([0.1, 0.3, 0.7]))
    eqs = all_equilibria(I, init, F, k, b, c)
    L = largest_equilibrium(I, init, F, k, b, c)
    is_eq = any((e == L).all() for e in eqs)
    above = all((L >= e).all() for e in eqs)
    pL = payoffs(I, init, F, L, k, b, c)
    pref = all((pL >= payoffs(I, init, F, e, k, b, c) - 1e-9).all() for e in eqs)
    cases += 1
    if not (is_eq and above and pref):
        bad += 1; print('FAIL random', trial, is_eq, above, pref)
print(f'Largest equilibrium (random communities): {cases} cases, {bad} failures')
