"""Scale paradox, strategic version: members choose to listen or to mute.

Setting. n members, m activities; I[i][t] = member i is interested in activity t.
Each activity has an initiator (interested in it) who posts it: posting is free,
so every activity is posted. Each member i is shown every posted activity it is
interested in plus a set F_i of activities it is not interested in (broadcast:
F_i = all of them; agora: the activities its agent wrongly guesses relevant).
Each member chooses to listen (1) or mute (0). Activity t happens if at least k
interested members take part: its initiator, and every interested listener.
Payoff of i: (its own initiatives that happen)
             + min(b, others' activities that happen and i takes part in)
             - c * listen_i * |F_i|.
i takes part in another member's activity t if i is interested in t and listens
(a muted member still runs its own initiatives).

The game is supermodular (a member's gain from listening is nondecreasing in the
others' listening; the cost does not depend on them), so the set of equilibria
has a largest element, found by iterating best responses from "all listen";
every member weakly prefers it to every other equilibrium.
"""
import itertools
import numpy as np


def happening(I, init, listen, k):
    """Activities that happen given the listening profile."""
    n, m = I.shape
    part = I & (listen[:, None] | (np.arange(n)[:, None] == init[None, :]))
    return part.sum(0) >= k, part


def payoffs(I, init, F, listen, k, b, c):
    n = I.shape[0]
    hap, part = happening(I, init, listen, k)
    own = (np.arange(n)[:, None] == init[None, :])
    own_hap = (own & hap[None, :]).sum(1)
    joined_others = (part & ~own & hap[None, :]).sum(1)
    return own_hap + np.minimum(joined_others, b) - c * listen * F.sum(1)


def best_response_gain(I, init, F, listen, k, b, c, i):
    """Payoff of i when listening minus payoff when muting, others fixed."""
    l1, l0 = listen.copy(), listen.copy()
    l1[i], l0[i] = 1, 0
    return payoffs(I, init, F, l1, k, b, c)[i] - payoffs(I, init, F, l0, k, b, c)[i]


def largest_equilibrium(I, init, F, k, b, c):
    """Iterate simultaneous best responses from all-listen (ties: listen)."""
    n = I.shape[0]
    listen = np.ones(n, dtype=bool)
    while True:
        new = np.array([best_response_gain(I, init, F, listen, k, b, c, i) >= 0 for i in range(n)])
        if (new == listen).all():
            return listen
        listen = new


def all_equilibria(I, init, F, k, b, c):
    n = I.shape[0]
    eqs = []
    for bits in itertools.product([0, 1], repeat=n):
        listen = np.array(bits, dtype=bool)
        ok = True
        for i in range(n):
            g = best_response_gain(I, init, F, listen, k, b, c, i)
            if (listen[i] and g < 0) or (not listen[i] and g > 0):
                ok = False; break
        if ok:
            eqs.append(listen)
    return eqs


# ---------- uniform communities ----------
def uniform(n, r, a):
    """n members, m = r*n activities; activity (j, t) for block j < r and t < n
    interests members t, t+1, ..., t+a-1 (mod n) shifted by j; every activity
    interests a members, every member is interested in r*a activities.
    The initiator of an activity is its first interested member."""
    m = r * n
    I = np.zeros((n, m), dtype=bool)
    init = np.zeros(m, dtype=int)
    for j in range(r):
        for t in range(n):
            col = j * n + t
            for d in range(a):
                I[(t + d * (j + 1)) % n, col] = True
            init[col] = t
    return I, init


def shown_irrelevant(I, q_count, rng=None):
    """F_i: q_count activities member i is not interested in (first ones, or random)."""
    n, m = I.shape
    F = np.zeros_like(I)
    for i in range(n):
        cand = np.nonzero(~I[i])[0]
        if rng is not None:
            cand = rng.permutation(cand)
        F[i, cand[:q_count]] = True
    return F


def uniform_works(n, r, a, k, b, c, shown):
    """Theorem 3: every activity interests a members, every member is interested in
    d other members' activities (here d = r*(a-1)) and sees `shown` posts it is not
    interested in. Everyone listens and all activities happen iff a >= k and
    min(b, d) >= c * shown; otherwise no activity happens in any equilibrium."""
    d = r * (a - 1)
    return a >= k and min(b, d) >= c * shown


# ---------- large communities (fast best responses) ----------
def largest_equilibrium_fast(I, init, F, k, b, c):
    n, m = I.shape
    own = np.zeros((n, m), dtype=bool); own[init, np.arange(m)] = True
    cost = c * F.sum(1)
    L = np.ones(n, dtype=bool)
    while True:
        part = I & (L[:, None] | own)
        P = part.sum(0)
        base = P[None, :] - (L[:, None] & I & ~own)
        joined = (I & ~own & (base + 1 >= k)).sum(1)
        new = np.minimum(joined, b) - cost >= 0
        if (new == L).all():
            hap = (I & (L[:, None] | own)).sum(0) >= k
            return L, hap
        L = new


def random_community(n, r, shares, rng):
    """m = round(r*n) activities; activity t picks a share from `shares` and
    floor(share*n) (at least 1) random interested members; the first is the initiator."""
    m = max(1, int(round(r * n)))
    I = np.zeros((n, m), dtype=bool); init = np.zeros(m, dtype=int)
    for t in range(m):
        s = shares[rng.integers(len(shares))]
        a = max(1, int(np.floor(s * n)))
        mem = rng.choice(n, size=a, replace=False)
        I[mem, t] = True; init[t] = mem[0]
    return I, init


def shown_share(I, q, rng):
    """Each member sees each activity it is not interested in with probability q."""
    return (~I) & (rng.random(I.shape) < q)

