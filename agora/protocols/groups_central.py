"""Central Agora: agents talk only to a coordinator, which directs the questions.

Round 0: each agent tells the coordinator what it already knows (one message
per known fact). Then the coordinator repeats the planning step of
groups_plan.py: it either outputs, or sends questions to members' agents,
which ask their members and report the answers back.
"""
import numpy as np
from ..model import UNKNOWN, NO, YES
from .groups_plan import plan


class CentralAgent:
    def __init__(self):
        self.started = False
        self.pending = []           # initiatives the coordinator asked about

    def act(self, v):
        out = []
        if not self.started:
            self.started = True
            out += [("send", "C", {"j": j, "v": int(e)})
                    for j, e in enumerate(v["estimate"]) if e != UNKNOWN]
        # answers to last round's questions are now in the estimate
        for j in self.pending:
            e = v["estimate"][j]
            out.append(("send", "C", {"j": j, "v": int(e) if e != UNKNOWN else -1}))
        self.pending = []
        for msg in v["inbox"]:
            if "ask" in msg:
                j = msg["ask"]
                if v["estimate"][j] == UNKNOWN:
                    out.append(("ask", j))
                self.pending.append(j)
        return out


class Coordinator:
    def __init__(self, seed, smart=False, batch=None):
        self.seed = seed
        self.cycle = 0
        self.smart = smart
        self.batch = batch
        self.K = None
        self.waiting = 0
        self.asked = None

    def act(self, v):
        n, m = v["n"], v["m"]
        if self.K is None:
            self.K = np.full((n, m), UNKNOWN, dtype=np.int8)
            self.asked = np.zeros(n, dtype=int)
            return []                               # round 0: listen
        for msg in v["inbox"]:
            if "v" in msg:
                self.K[msg["from"], msg["j"]] = msg["v"]
        if self.waiting:
            self.waiting -= 1
            return []
        # randomness per planning cycle, drawn exactly as the grassroots agents
        # draw it, so both settings make the same decisions
        rng = np.random.default_rng([self.seed, self.cycle])
        self.cycle += 1
        now, qs = plan(self.K, self.asked, v["budget"], v["min_size"],
                       rng, smart=self.smart, batch=self.batch)
        if qs is None:
            return [("output", now)]
        self.waiting = 2          # agent asks next round, its reply lands after
        return [("send", i, {"ask": j}) for i, j in qs]


def make(inst, rng, budget=None, smart=False, batch=None):
    return dict(agents=[CentralAgent() for _ in range(inst.n)],
                coordinator=Coordinator(int(rng.integers(1 << 30)),
                                        smart=smart, batch=batch))


class Smart:
    """Central Agora with the smarter planner: spread first questions evenly,
    then greedy; asks at most 10 members per cycle, so it learns in between
    (rounds are free in the basic model)."""
    @staticmethod
    def make(inst, rng, budget=None):
        return make(inst, rng, budget=budget, smart=True, batch=10)
