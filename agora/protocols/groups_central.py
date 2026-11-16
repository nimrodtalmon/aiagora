"""Central Agora: agents talk only to a coordinator, which directs the questions.

Round 0: each agent tells the coordinator what it already knows (one message
per known fact). Then, repeatedly, the coordinator compares two numbers:
  - the welfare it can guarantee now (known YES pairs only), and
  - the welfare it could reach if every still-askable unknown were a YES.
If they are equal, no answer can help, so it outputs. Otherwise it asks
each member who is not yet served about one unknown initiative, chosen by
how popular it looks so far (Thompson sampling), through the member's agent.
"""
import numpy as np
from ..model import UNKNOWN, NO, YES
from ..tasks.groups import best_assignment, welfare


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
    def __init__(self, rng):
        self.rng = rng
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
        budget = v["budget"]
        can_ask = np.ones(n, dtype=bool) if budget is None else self.asked < budget
        sure = self.K == YES
        maybe = sure | ((self.K == UNKNOWN) & can_ask[:, None])
        now = best_assignment(sure, v["min_size"])
        hope = best_assignment(maybe, v["min_size"])
        if welfare(hope) == welfare(now):
            return [("output", now)]
        # each member not yet served (if none: every member) is asked about one
        # unknown initiative, chosen by Thompson sampling on how popular each
        # initiative looks so far: explores early, exploits once it learns
        yes = (self.K == YES).sum(0)
        no = (self.K == NO).sum(0)
        served = {i for g in now.values() for i in g}
        askable = [i for i in range(n)
                   if can_ask[i] and (self.K[i] == UNKNOWN).any()]
        targets = [i for i in askable if i not in served] or askable
        out = []
        for i in targets:
            unk = np.flatnonzero(self.K[i] == UNKNOWN)
            score = self.rng.beta(yes[unk] + 1, no[unk] + 1)
            j = int(unk[np.argmax(score)])
            self.asked[i] += 1
            out.append(("send", i, {"ask": j}))
        if not out:
            return [("output", now)]
        self.waiting = 2          # agent asks next round, its reply lands after
        return out


def make(inst, rng):
    return dict(agents=[CentralAgent() for _ in range(inst.n)],
                coordinator=Coordinator(rng))
