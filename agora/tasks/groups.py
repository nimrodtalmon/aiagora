"""Forming groups: feasibility, welfare, and an exact optimum (ILP)."""
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds


def welfare(assignment):
    """Number of members served. assignment: dict initiative -> list of members."""
    return sum(len(g) for g in assignment.values())


def is_feasible(assignment, accept, min_size):
    seen = set()
    for j, group in assignment.items():
        if not group:
            continue
        if len(group) < min_size:
            return False
        for i in group:
            if i in seen or not accept[i, j]:
                return False
            seen.add(i)
    return True


def best_assignment(allowed, min_size):
    """Max-welfare assignment using only pairs with allowed[i, j] True.

    Single membership, groups of at least min_size. Solved as an ILP:
    x_ij = member i joins initiative j, y_j = initiative j forms.
    """
    n, m = allowed.shape
    pairs = [(i, j) for i in range(n) for j in range(m) if allowed[i, j]]
    if not pairs:
        return {}
    P = len(pairs)
    nv = P + m                                   # x's then y's
    c = np.zeros(nv)
    c[:P] = -1.0                                 # maximize members served
    rows, lo, hi = [], [], []
    # each member in at most one initiative
    for i in range(n):
        r = np.zeros(nv)
        for k, (a, _) in enumerate(pairs):
            if a == i:
                r[k] = 1
        if r.any():
            rows.append(r); lo.append(-np.inf); hi.append(1)
    # x_ij <= y_j
    for k, (_, j) in enumerate(pairs):
        r = np.zeros(nv); r[k] = 1; r[P + j] = -1
        rows.append(r); lo.append(-np.inf); hi.append(0)
    # min_size * y_j <= sum_i x_ij
    for j in range(m):
        r = np.zeros(nv); r[P + j] = min_size
        for k, (_, b) in enumerate(pairs):
            if b == j:
                r[k] = -1
        rows.append(r); lo.append(-np.inf); hi.append(0)
    res = milp(c, constraints=LinearConstraint(np.array(rows), lo, hi),
               integrality=np.ones(nv), bounds=Bounds(0, 1))
    x = np.round(res.x[:P]).astype(int)
    out = {}
    for k, (i, j) in enumerate(pairs):
        if x[k]:
            out.setdefault(j, []).append(i)
    return out


def optimum(accept, min_size):
    return welfare(best_assignment(accept, min_size))
