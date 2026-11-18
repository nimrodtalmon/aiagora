"""Central explore-then-commit for forming groups with a minimum size.

Explore: members are put in a uniformly random order; the member in position p
is asked about b-1 initiatives p, p+1, ... (mod m). Commit: the leader is the
initiative with the largest share of yes answers; every member not yet asked
about it is asked (each has one question left); the leader's group forms if at
least min_size members said yes. This is the protocol of the planted-group
theorem: one yes points to the whole group.
"""
import numpy as np
from ..model import YES
from .groups_central import CentralAgent


class ECCoordinator:
    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)
        self.phase, self.wait, self.ans = "explore", 0, {}

    def act(self, v):
        n, m, b, k = v["n"], v["m"], v["budget"], v["min_size"]
        for msg in v["inbox"]:
            if "v" in msg and msg["v"] in (0, 1):
                self.ans[(msg["from"], msg["j"])] = msg["v"]
        if self.wait:
            self.wait -= 1
            return []
        if self.phase == "explore":
            self.phase, self.wait = "commit", 2
            e = max(1, min(m, b if b is not None else m) - 1)
            order = self.rng.permutation(n)
            return [("send", int(i), {"ask": (p + t) % m}) for p, i in enumerate(order) for t in range(e)]
        if self.phase == "commit":
            yes, cnt = np.zeros(m), np.zeros(m)
            for (i, j), a in self.ans.items():
                cnt[j] += 1; yes[j] += a == YES
            self.leader = int(np.argmax(np.where(cnt > 0, yes / np.maximum(cnt, 1), -1)))
            self.phase, self.wait = "done", 2
            ask = [i for i in range(n) if (i, self.leader) not in self.ans]
            if ask:
                return [("send", i, {"ask": self.leader}) for i in ask]
        g = sorted(i for (i, j), a in self.ans.items() if j == self.leader and a == YES)
        return [("output", {self.leader: g} if len(g) >= k else {})]


def make(inst, rng, budget=None):
    return dict(agents=[CentralAgent() for _ in range(inst.n)],
                coordinator=ECCoordinator(int(rng.integers(1 << 30))))
