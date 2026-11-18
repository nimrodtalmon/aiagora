"""Scale paradox: broadcast channel vs. agent routing (simplest model).

Setting. n members, activity types t = 1..T. Each member accepts type t
independently with probability p_t (its popularity). A group of type t forms if
at least k members, the initiator included, accept and are reached.
Each type has one initiator (a member who accepts it). The initiator decides
whether to announce. Reaching a member who does not accept t bothers that member;
the initiator bears a social cost c per bothered member and gains B if the group
forms (reputation / politeness, internalized).

Broadcast: an announcement reaches all n-1 others.
Agora: the initiator's agent invites, in random order, only members whose agents
estimate "accepts t" (each estimate is wrong with probability eps), and stops as
soon as k-1 others accepted.

The initiator announces iff B * P(form) >= c * E[bothered]. Output: expected
number of groups formed (types announced and formed).
"""
import numpy as np
from scipy.stats import binom


def popularity(T=300, top=0.5, zipf=1.0):
    return top / np.arange(1, T + 1) ** zipf


def broadcast_type(n, p, k, B, c):
    pf = binom.sf(k - 2, n - 1, p)                 # P(at least k-1 of n-1 others accept)
    bothered = (1 - p) * (n - 1)
    return pf if B * pf >= c * bothered else 0.0


def agora_type(n, p, k, B, c, eps, rng, runs=400):
    """Monte Carlo: expected bothered members and P(form) under routing."""
    q_true = p * (1 - eps)                          # other member: accepts and agent says yes
    q_false = (1 - p) * eps                         # does not accept, agent says yes
    forms, both = 0, 0
    for _ in range(runs):
        nt = rng.binomial(n - 1, q_true)
        nf = rng.binomial(n - 1 - nt, q_false / max(1e-12, 1 - q_true))
        if nt >= k - 1:
            # invite in random order until k-1 true: false invites before the (k-1)-th true
            order = rng.permutation(np.r_[np.ones(nt), np.zeros(nf)])
            pos = np.nonzero(order)[0][k - 2]
            both += pos + 1 - (k - 1); forms += 1
        else:
            both += nf
    pf, eb = forms / runs, both / runs
    return pf if B * pf >= c * eb else 0.0


def groups(n, ps, k, B, c, eps=None, seed=0):
    if eps is None:
        return sum(broadcast_type(n, p, k, B, c) for p in ps)
    rng = np.random.default_rng(seed)
    return sum(agora_type(n, p, k, B, c, eps, rng) for p in ps)


def viable(n, ps, k):
    """Benchmark: expected number of types with at least k acceptors (initiator incl.)."""
    return sum(binom.sf(k - 2, n - 1, p) for p in ps)
