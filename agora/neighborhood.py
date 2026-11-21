"""Synthetic neighborhoods for conditional commitments, and the two channels.

A neighborhood: n members, activities, 7 days. Member i likes activity t with
probability pop_t; for each liked activity it accepts each day with probability
p_day (at least one day), and has a threshold: 0 with probability `eager`
("I go anyway"), otherwise uniform in [lo, hi] ("I come if at least th others come").
A group needs at least k members.

Group chat (board): members read the chat in a random order, again and again; a
member writes "I'm in" for a liked activity and an accepted day once at least th
others are in for that activity and day (one day per activity, the one with most
sign-ups). An activity-day happens if at least k signed up.
Agora: agents know the conditions; per activity, they form groups on days so as to
place as many members as possible (each member in at most one group per activity).
"""
import numpy as np
from .commit import board_slots, placed, agora_slots_milp

DAYS = list(range(7))


def neighborhood(n, pops, p_day=0.4, eager=0.1, lo=2, hi=6, seed=0):
    rng = np.random.default_rng(seed)
    likes = []
    for t, pop in enumerate(pops):
        A, th = {}, {}
        for i in range(n):
            if rng.random() < pop:
                days = {d for d in DAYS if rng.random() < p_day} or {int(rng.integers(7))}
                A[i] = days
                th[i] = 0 if rng.random() < eager else int(rng.integers(lo, hi + 1))
        likes.append((A, th))
    return likes


def greedy_agora(A, th, k):
    """Repeatedly take the day with the largest feasible group among unplaced members."""
    free = set(A); total = 0; groups = []
    while True:
        best = (0, None, None)
        for d in DAYS:
            cand = [i for i in free if d in A[i]]
            ths = sorted(max(th[i], k - 1) for i in cand)
            m = 0
            for size in range(len(ths), 0, -1):
                if sum(1 for x in ths if x <= size - 1) >= size:
                    m = size; break
            if m > best[0]:
                members = [i for i in cand if max(th[i], k - 1) <= m - 1]
                best = (len(members), d, members)
        if best[0] < k:
            return total, groups
        total += best[0]; groups.append((best[1], best[2])); free -= set(best[2])


def exact_agora(A, th, k):
    if not A:
        return 0
    ids = sorted(A)
    AA = [A[i] for i in ids]; tt = [max(th[i], k - 1) for i in ids]
    return agora_slots_milp(AA, tt, DAYS)


def board(A, th, k, rng):
    if not A:
        return 0, {}
    ids = sorted(A)
    sheet = board_slots([A[i] for i in ids], [th[i] for i in ids], list(rng.permutation(len(ids))))
    happened = {d: g for d, g in sheet.items() if len(g) >= k}
    return sum(len(g) for g in happened.values()), happened


def greatest_on_day(free, A, th, k, d):
    cand = [i for i in free if d in A[i]]
    ths = sorted(max(th[i], k - 1) for i in cand)
    for size in range(len(ths), k - 1, -1):
        if sum(1 for x in ths if x <= size - 1) >= size:
            return [i for i in cand if max(th[i], k - 1) <= size - 1]
    return []


def order_agora(A, th, k, orders=None):
    """Best over orders of the days: in each order, give each day in turn the largest
    group among members not yet placed (the method used in the web prototype)."""
    import itertools
    best = (0, [])
    for order in (orders or itertools.permutations(DAYS)):
        free = set(A); groups = []
        for d in order:
            g = greatest_on_day(free, A, th, k, d)
            if g:
                groups.append((d, g)); free -= set(g)
        tot = sum(len(g) for _, g in groups)
        if tot > best[0]:
            best = (tot, groups)
    return best
