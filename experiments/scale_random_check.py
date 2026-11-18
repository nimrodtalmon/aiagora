"""Checks for the scale-paradox theorems: exact formulas vs. sampling, and the
statements of Theorems 1 and 2 on a grid of parameters."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from agora.scale_random import broadcast_stats, agora_stats, agora_limit_bothered, groups, popularity, agora_limit

rng = np.random.default_rng(1)


def sample_agora(n, p, k, eps, runs=20000):
    forms = both = 0
    for _ in range(runs):
        acc = rng.random(n - 1) < p
        guess = acc ^ (rng.random(n - 1) < eps)
        cand = rng.permutation(np.nonzero(guess)[0])
        yes = 0
        for i in cand:
            if acc[i]:
                yes += 1
                if yes == k - 1:
                    break
            else:
                both += 1
        forms += yes >= k - 1
    return forms / runs, both / runs


# 1. exact agora formulas vs. direct sampling
worst = 0
for n, p, k, eps in [(10, .3, 3, .1), (30, .1, 4, .2), (60, .05, 4, .1), (25, .5, 6, .3), (40, .02, 2, .05)]:
    ex, sa = agora_stats(n, p, k, eps), sample_agora(n, p, k, eps)
    worst = max(worst, abs(ex[0] - sa[0]), abs(ex[1] - sa[1]) / max(1, ex[1]))
    print('agora exact vs sampled', (n, p, k, eps), np.round(ex, 3), np.round(sa, 3))
print('max discrepancy', round(worst, 3))

# 2. Theorem 1: no broadcast announcement once (1-p)(n-1) > B/c, for every type
viol = 0
for B in [5, 30, 100, 400]:
    for k in [2, 3, 4, 6]:
        for p in np.linspace(.01, .9, 30):
            for n in range(2, 2000, 7):
                pf, eb = broadcast_stats(n, p, k)
                if B * pf >= eb and (1 - p) * (n - 1) > B:
                    viol += 1
print('Theorem 1 violations:', viol)

# 3. Theorem 2: E[bothered] -> (k-1)(1-r)/r, P(forms) -> 1, and E[bothered] <= limit for all n
viol = 0
for k in [2, 3, 4, 6]:
    for eps in [.05, .1, .3]:
        for p in [.01, .05, .2, .5]:
            lim = agora_limit_bothered(p, k, eps)
            for n in [k, 2 * k, 50, 200, 1000, 4000]:
                pf, eb = agora_stats(n, p, k, eps)
                viol += eb > lim + 1e-9
            pf, eb = agora_stats(20000, p, k, eps)
            if abs(eb - lim) > 1e-3 * max(1, lim) or pf < 1 - 1e-6:
                print('slow convergence', k, eps, p, pf, eb, lim)
print('E[bothered] above its limit:', viol)

# 4. simulation parameters: welfare at large n equals the Theorem 2 count
ps = popularity(300)
for eps in [.1, .3]:
    print('eps', eps, 'groups at n=20000:', round(groups(20000, ps, 4, 100, 1, eps), 1), ' Theorem 2 limit:', agora_limit(ps, 4, 100, 1, eps))
