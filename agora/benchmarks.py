"""Benchmarks: reference points, not protocols. They may look at the instance.

popularity_oracle: each member is asked about its unknown initiatives in the
order of their true popularity (how many members accept them), up to the
budget, and the best groups are formed from what is then known. A protocol
that has to learn popularity can be compared against it.
"""
import numpy as np
from .model import UNKNOWN, YES
from .tasks.groups import best_assignment, welfare


def popularity_oracle(inst, budget):
    order = np.argsort(-inst.accept.sum(0), kind="stable")
    known = inst.initial == YES
    att = 0
    for i in range(inst.n):
        unk = [j for j in order if inst.initial[i, j] == UNKNOWN][:budget]
        for j in unk:
            known[i, j] = inst.accept[i, j]
        att += len(unk)
    return {"welfare": welfare(best_assignment(known, inst.min_size)), "attention": att}
