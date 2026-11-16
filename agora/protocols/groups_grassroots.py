"""Grassroots Agora, simplest protocol: a replicated coordinator.

No third party. Every agent broadcasts what it knows to all other agents, so
all agents hold the same knowledge. Each then runs the same planning step as
the central coordinator (groups_plan.py), with randomness shared through a
common seed, so all agents reach the same decisions: each asks its own member
when the plan says so, and broadcasts the answer. When the plan says stop,
every agent outputs the same groups, so agreement is guaranteed.

This is the baseline for what doing without a coordinator costs: the same
outcomes as the central Agora, paid for with broadcasts (n-1 messages per
fact instead of one).
"""
import numpy as np
from ..model import UNKNOWN
from .groups_plan import plan

# Simulation shortcut: all agents compute the same plan from the same
# knowledge, so one process computes it once and every agent reuses it.
_CACHE = {}


class ReplicatedAgent:
    def __init__(self, n, m, min_size, budget, seed):
        self.n, self.m, self.min_size, self.budget = n, m, min_size, budget
        self.seed = seed
        self.K = np.full((n, m), UNKNOWN, dtype=np.int8)
        self.asked = np.zeros(n, dtype=int)
        self.phase = "share"
        self.cycle = 0
        self.pending = None
        self.done = False

    def broadcast(self, me, payload):
        return [("send", k, payload) for k in range(self.n) if k != me]

    def act(self, v):
        if self.done:
            return []
        me = v["me"]
        for msg in v["inbox"]:
            self.K[msg["from"], msg["j"]] = msg["v"]
        if self.phase == "share":                    # round 0: tell everyone
            self.phase = "plan"
            out = []
            for j, e in enumerate(v["estimate"]):
                if e != UNKNOWN:
                    self.K[me, j] = e
                    out += self.broadcast(me, {"j": j, "v": int(e)})
            return out
        if self.phase == "answer":                   # my member answered
            self.phase = "plan"
            if self.pending is None:
                return []
            j, self.pending = self.pending, None
            e = int(v["estimate"][j])
            self.K[me, j] = e
            return self.broadcast(me, {"j": j, "v": e})
        # plan: every agent computes the same step from the same knowledge
        key = (self.K.tobytes(), self.asked.tobytes(), self.budget,
               self.min_size, self.seed, self.cycle)
        if key not in _CACHE:
            if len(_CACHE) > 20000:
                _CACHE.clear()
            rng = np.random.default_rng([self.seed, self.cycle])
            asked = self.asked.copy()
            now, qs = plan(self.K, asked, self.budget, self.min_size, rng)
            _CACHE[key] = (now, qs, asked)
        now, qs, asked = _CACHE[key]
        self.asked = asked.copy()
        self.cycle += 1
        if qs is None:
            self.done = True
            return [("output", now)]
        self.phase = "answer"
        mine = [j for i, j in qs if i == me]
        if mine:
            self.pending = mine[0]
            return [("ask", mine[0])]
        return []


def make(inst, rng, budget=None):
    seed = int(rng.integers(1 << 30))
    return dict(agents=[ReplicatedAgent(inst.n, inst.m, inst.min_size, budget, seed)
                        for _ in range(inst.n)])
