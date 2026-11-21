"""Brute-force checks for conditional commitments (agora/commit.py)."""
import itertools, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from agora.commit import (least_fixed_point, greatest_group, board_one_slot, best_group_brute,
                          board_slots, placed, agora_slots_brute, agora_slots_milp)

# 1. one slot: the sheet ends at the least fixed point for EVERY order; the best group is the greatest
cases = bad = 0
for n in range(1, 7):
    for th in itertools.product(range(n + 1), repeat=n):
        lfp, gg = least_fixed_point(th), greatest_group(th)
        if gg != best_group_brute(th):
            bad += 1
        for order in itertools.permutations(range(n)):
            cases += 1
            if board_one_slot(th, order) != lfp:
                bad += 1
print(f'one slot: {cases} (thresholds, order) pairs, {bad} failures')

# 2. several slots: integer program equals brute force; the sheet never beats the agora
rng = np.random.default_rng(0)
cases = bad = 0; worst = []
for trial in range(400):
    n = int(rng.integers(2, 8)); S = list(range(int(rng.integers(1, 4))))
    A = [set(s for s in S if rng.random() < 0.6) or {int(rng.integers(len(S)))} for _ in range(n)]
    th = [int(x) for x in rng.integers(0, 4, n)]
    opt = agora_slots_brute(A, th, S)
    if agora_slots_milp(A, th, S) != opt:
        bad += 1; print('milp mismatch', A, th)
    for _ in range(5):
        b = placed(board_slots(A, th, list(rng.permutation(n))))
        if b > opt:
            bad += 1; print('board beats agora', A, th)
    cases += 1
print(f'several slots: {cases} instances, {bad} failures')
