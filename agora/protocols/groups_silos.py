"""Silos: each agent asks its member alone, then sends one free report.

Without knowing anything about the others, an agent can only ask about its
unknown initiatives in some order (here: random), up to its budget.
The mechanism then forms the best groups from the reported acceptances.
"""
import numpy as np
from ..model import UNKNOWN, YES
from ..tasks.groups import best_assignment


class SilosAgent:
    def __init__(self, rng):
        self.rng = rng
        self.asked = False
        self.done = False

    def act(self, v):
        if self.done:
            return []
        if not self.asked:
            self.asked = True
            unknown = [j for j, e in enumerate(v["estimate"]) if e == UNKNOWN]
            self.rng.shuffle(unknown)
            k = len(unknown) if v["budget_left"] is None else v["budget_left"]
            qs = [("ask", j) for j in unknown[:k]]
            if qs:
                return qs
        self.done = True
        yes = [j for j, e in enumerate(v["estimate"]) if e == YES]
        return [("report", {"yes": yes})]


def mechanism(reports, inst):
    allowed = np.zeros((inst.n, inst.m), dtype=bool)
    for i, r in reports.items():
        allowed[i, r["yes"]] = True
    return best_assignment(allowed, inst.min_size)


def make(inst, rng, budget=None):
    return dict(agents=[SilosAgent(np.random.default_rng(rng.integers(1 << 30)))
                        for _ in range(inst.n)],
                mechanism=mechanism)


class Convention:
    """Silos with a convention: all agents ask in the same random order of
    initiatives, drawn from a shared seed fixed in advance (no communication)."""
    @staticmethod
    def make(inst, rng, budget=None):
        seed = int(rng.integers(1 << 30))
        return dict(agents=[SilosAgent(np.random.default_rng(seed)) for _ in range(inst.n)],
                    mechanism=mechanism)
