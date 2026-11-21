"""Conditional commitments.

Setting. n members and a set of slots (e.g., days for one activity). Member i has a
private condition: a set A_i of acceptable slots and a threshold th_i >= 0 ("I come
if at least th_i others come"). A group is a slot s and a set G of members with
s in A_i and |G| - 1 >= th_i for every i in G. Each member joins at most one group,
and each slot hosts at most one group. Welfare: the number of members placed.

Board (today): a public sign-up sheet. Members look at it one at a time, in some
order, as often as they like; a member signs up, unconditionally and for good, for
an acceptable slot that already has at least th_i sign-ups (if several, the one with
most sign-ups, lowest index on ties). The process ends when no member can sign up.

Agora: agents hold the conditions and form a welfare-maximizing set of groups.
"""
import itertools
import numpy as np


# ---------- one slot ----------
def least_fixed_point(th):
    """Board outcome for one slot: iterate c -> #{i : th_i <= c} from c = 0."""
    th = np.asarray(th); c = 0
    while True:
        nc = int((th <= c).sum())
        if nc == c:
            return c
        c = nc


def greatest_group(th):
    """Agora outcome for one slot: the largest m with #{i : th_i <= m - 1} >= m."""
    th = np.asarray(th); n = len(th)
    for m in range(n, 0, -1):
        if (th <= m - 1).sum() >= m:
            return m
    return 0


def board_one_slot(th, order):
    """Simulate the sheet: repeatedly pass over members in `order` until no change."""
    signed = set()
    changed = True
    while changed:
        changed = False
        for i in order:
            if i not in signed and th[i] <= len(signed):
                signed.add(i); changed = True
    return len(signed)


def best_group_brute(th):
    n = len(th); best = 0
    for r in range(1, n + 1):
        for G in itertools.combinations(range(n), r):
            if all(th[i] <= r - 1 for i in G):
                best = max(best, r)
    return best


# ---------- several slots ----------
def board_slots(A, th, order):
    """A[i]: set of acceptable slots; returns dict slot -> signed members."""
    sheet = {}
    where = {}
    changed = True
    while changed:
        changed = False
        for i in order:
            if i in where:
                continue
            ok = [s for s in sorted(A[i]) if len(sheet.get(s, ())) >= th[i]]
            if ok:
                s = max(ok, key=lambda x: (len(sheet.get(x, ())), -x))
                sheet.setdefault(s, set()).add(i); where[i] = s; changed = True
    return sheet


def placed(sheet):
    return sum(len(g) for g in sheet.values())


def agora_slots_brute(A, th, slots):
    """Optimal welfare by brute force over assignments (small instances)."""
    n = len(th); best = 0
    choices = [[None] + sorted(A[i]) for i in range(n)]
    for assign in itertools.product(*choices):
        groups = {}
        for i, s in enumerate(assign):
            if s is not None:
                groups.setdefault(s, []).append(i)
        if all(th[i] <= len(g) - 1 for g in groups.values() for i in g):
            best = max(best, sum(len(g) for g in groups.values()))
    return best


def agora_slots_milp(A, th, slots):
    """Optimal welfare via an integer program: x[i,s] (i in slot s), y[s,m] (slot s has a
    group of size class m: all its members have th_i <= m - 1 and it has >= m members)."""
    from scipy.optimize import milp, LinearConstraint, Bounds
    n = len(th); S = list(slots); ms = list(range(1, n + 1))
    xi = {(i, s): j for j, (i, s) in enumerate((i, s) for i in range(n) for s in S if s in A[i])}
    yi = {(s, m): len(xi) + j for j, (s, m) in enumerate((s, m) for s in S for m in ms)}
    N = len(xi) + len(yi)
    c = np.zeros(N); 
    for v in xi.values():
        c[v] = -1
    rows, lo, hi = [], [], []
    def row():
        return np.zeros(N)
    for i in range(n):                         # each member at most one slot
        r = row()
        for (ii, s), v in xi.items():
            if ii == i: r[v] = 1
        rows.append(r); lo.append(0); hi.append(1)
    for s in S:
        r = row()                              # at most one size class per slot
        for m in ms: r[yi[(s, m)]] = 1
        rows.append(r); lo.append(0); hi.append(1)
        for (i, ss), v in xi.items():          # member i in slot s needs a class m with th_i <= m-1
            if ss != s: continue
            r = row(); r[v] = 1
            for m in ms:
                if th[i] <= m - 1: r[yi[(s, m)]] -= 1
            rows.append(r); lo.append(-np.inf); hi.append(0)
        r = row()                              # slot with class m has at least m members
        for (i, ss), v in xi.items():
            if ss == s: r[v] = 1
        for m in ms: r[yi[(s, m)]] = -m
        rows.append(r); lo.append(0); hi.append(np.inf)
    res = milp(c, constraints=LinearConstraint(np.array(rows), lo, hi), integrality=np.ones(N), bounds=Bounds(0, 1))
    return int(round(-res.fun))
