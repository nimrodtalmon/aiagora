"""The simplest Agora: pick one option.

n members, m options; member i approves some options (unknown to everyone,
its own agent included). Each agent may ask its member at most `budget`
yes/no questions ("do you approve option o?"). The community picks one
option; the members enrolled in it are those known to approve it (an agent
commits its member to nothing the member did not say yes to). Welfare is
the number of enrolled members; the optimum is the largest number of
approvers of any option.

Three settings, all run through the engine (locality, ledger, event log):
- silos: each agent asks `budget` random options, then reports once;
  the mechanism picks the option with the most reported yes answers;
- central: explore-then-commit through a coordinator: first every member is
  asked about all but one of its questions' worth of options (spread evenly),
  then every member not yet asked is asked about the leading option;
- grassroots: the same explore-then-commit without a coordinator: the first
  question of each agent is fixed by its id, agents broadcast only yes
  answers, and every agent computes the same leader.
"""
import numpy as np
from .model import Instance, UNKNOWN, YES, NO
from .engine import Engine


# ---------- instances ----------

def hidden_favorite(n, m, seed=0):
    """Every member approves one option, the same for all; no one approves
    any other. The favorite is chosen at random."""
    rng = np.random.default_rng(seed)
    accept = np.zeros((n, m), dtype=bool)
    accept[:, rng.integers(m)] = True
    return Instance(accept, 1, np.full((n, m), UNKNOWN, dtype=np.int8))


def random_popularity(n, m, top=0.6, seed=0):
    """Option o is approved by each member independently with probability
    pop_o, drawn uniformly between 0 and `top`."""
    rng = np.random.default_rng(seed)
    pop = rng.uniform(0, top, size=m)
    accept = rng.random((n, m)) < pop
    return Instance(accept, 1, np.full((n, m), UNKNOWN, dtype=np.int8))


def popular(n, m, alpha, rest=None, seed=0):
    """One popular option, approved by each member with probability alpha;
    every other option with probability rest (default alpha / 2)."""
    rng = np.random.default_rng(seed)
    rest = alpha / 2 if rest is None else rest
    p = np.full(m, rest)
    p[rng.integers(m)] = alpha
    accept = rng.random((n, m)) < p
    return Instance(accept, 1, np.full((n, m), UNKNOWN, dtype=np.int8))


def needle(n, m, seed=0):
    """One member approves one option; no one approves anything else."""
    rng = np.random.default_rng(seed)
    accept = np.zeros((n, m), dtype=bool)
    accept[rng.integers(n), rng.integers(m)] = True
    return Instance(accept, 1, np.full((n, m), UNKNOWN, dtype=np.int8))


def optimum(inst):
    return int(inst.accept.sum(0).max())


def one_question_sample(n, m):
    """With one question per member, only a few members explore each option:
    about (n/m)^(2/3) of them, so that exploration costs few members while
    the estimates still become accurate as n grows."""
    s = max(1, int(np.ceil((n / m) ** (2 / 3))))
    return min(s, n // m) if n >= m else 1


def explore_options(i, m, budget, n=None):
    """With one question per member (budget 1, n given), only the first
    m * one_question_sample(n, m) positions explore, one option each."""
    if budget == 1 and n is not None:
        return [i % m] if i < m * one_question_sample(n, m) else []
    return explore_options_k(i, m, budget)


def explore_options_k(i, m, budget):
    """Options member i is asked about while exploring: all but one of its
    questions (at least one), spread so that every option gets asked about
    about equally often. Fixed by the member's id, so no one has to assign it."""
    k = max(1, min(m, budget if budget is not None else m) - 1)
    return [(i + t) % m for t in range(k)]


# ---------- silos ----------

class SilosAgent:
    def __init__(self, rng):
        self.rng, self.state = rng, 0

    def act(self, v):
        if self.state == 0:
            self.state = 1
            m = len(v["estimate"])
            qs = self.rng.permutation(m)[:v["budget_left"]]
            return [("ask", int(o)) for o in qs]
        if self.state == 1:
            self.state = 2
            return [("report", {"yes": [int(o) for o in np.flatnonzero(v["estimate"] == YES)]})]
        return []


def silos_mechanism(reports, inst):
    count = np.zeros(inst.m, dtype=int)
    for r in reports.values():
        for o in r["yes"]:
            count[o] += 1
    o = int(np.argmax(count))
    return {o: sorted(i for i, r in reports.items() if o in r["yes"])} if count[o] else {}


# ---------- central: explore, then commit ----------

class Follower:
    """An agent in the central Agora: asks what it is told, reports answers."""
    def __init__(self):
        self.pending = []

    def act(self, v):
        out = [("send", "C", {"o": o, "v": int(v["estimate"][o])}) for o in self.pending]
        self.pending = []
        for msg in v["inbox"]:
            out.append(("ask", msg["ask"]))
            self.pending.append(msg["ask"])
        return out


class ExploreCommitCoordinator:
    """Members are put in a random order first, so that the members who explore
    each option form a uniformly random sample (used in the proof of the
    large-community theorem)."""
    def __init__(self, seed=0):
        self.rng = np.random.default_rng(seed)
        self.phase, self.wait = "explore", 0
        self.yes = self.asked = None
        self.answers = {}

    def act(self, v):
        n, m = v["n"], v["m"]
        if self.yes is None:
            self.yes, self.asked = np.zeros(m, int), np.zeros(m, int)
        for msg in v["inbox"]:
            self.answers[(msg["from"], msg["o"])] = msg["v"]
            self.asked[msg["o"]] += 1
            self.yes[msg["o"]] += msg["v"] == YES
        if self.wait:
            self.wait -= 1
            return []
        if self.phase == "explore":
            self.phase, self.wait = "commit", 2
            order = self.rng.permutation(n)
            return [("send", int(i), {"ask": o}) for pos, i in enumerate(order)
                    for o in explore_options(pos, m, v["budget"], n)]
        if self.phase == "commit":
            rate = np.where(self.asked > 0, self.yes / np.maximum(self.asked, 1), -1.0)
            self.leader = int(np.argmax(rate))
            self.phase, self.wait = "done", 2
            asked = {i for (i, _) in self.answers}
            if v["budget"] == 1:                     # only members who did not explore
                ask = [i for i in range(n) if i not in asked]
            else:
                ask = [i for i in range(n) if (i, self.leader) not in self.answers]
            if ask:
                return [("send", i, {"ask": self.leader}) for i in ask]
            self.wait = 0
        enrolled = sorted(i for (i, o), a in self.answers.items()
                          if o == self.leader and a == YES)
        return [("output", {self.leader: enrolled} if enrolled else {})]


# ---------- grassroots: explore, then commit, broadcasting yes answers ----------

class GrassrootsAgent:
    def __init__(self, n, m, budget):
        self.n, self.m, self.budget = n, m, budget
        self.yes = {}                     # (member, option) -> True, from broadcasts
        self.phase, self.mine, self.asked2 = "explore", None, False

    def tell(self, me, o):
        return [("send", k, {"o": o}) for k in range(self.n) if k != me]

    def act(self, v):
        me, n, m = v["me"], self.n, self.m
        for msg in v["inbox"]:
            self.yes[(msg["from"], msg["o"])] = True
        if self.phase == "explore":                  # round 0
            self.phase = "share1"
            self.first = explore_options(me, m, self.budget, n)
            return [("ask", o) for o in self.first]
        if self.phase in ("share1", "share2"):       # rounds 1 and 3
            done = self.phase == "share2"
            self.phase = "wait" if done else "commit"
            if done and not self.asked2:
                return []
            out = []
            for o in ([self.mine] if done else self.first):
                if v["estimate"][o] == YES:
                    self.yes[(me, o)] = True
                    out += self.tell(me, o)
            return out
        if self.phase == "commit":                   # round 2: all see round-0 yes answers
            assigned = np.bincount([o for i in range(n)
                                    for o in explore_options(i, m, self.budget, n)],
                                   minlength=m)
            count = np.zeros(m)
            for (i, o) in self.yes:
                count[o] += 1
            self.leader = int(np.argmax(np.where(assigned > 0, count / np.maximum(assigned, 1), -1.0)))
            self.phase = "share2"
            if self.leader not in self.first and (self.budget is None
                                                  or self.budget > len(self.first)):
                self.mine, self.asked2 = self.leader, True
                return [("ask", self.leader)]
            return []
        if self.phase == "wait":                     # round 4: output
            self.phase = "out"
            enrolled = sorted(i for (i, o) in self.yes if o == self.leader)
            return [("output", {self.leader: enrolled} if enrolled else {})]
        return []


# ---------- running ----------

def run(inst, setting, budget, seed=0, eps=0.01):
    rng = np.random.default_rng(seed)
    if setting == "silos":
        parts = dict(agents=[SilosAgent(np.random.default_rng(rng.integers(1 << 30)))
                             for _ in range(inst.n)], mechanism=silos_mechanism)
    elif setting == "central":
        parts = dict(agents=[Follower() for _ in range(inst.n)],
                     coordinator=ExploreCommitCoordinator(int(rng.integers(1 << 30))))
    elif setting == "grassroots":
        parts = dict(agents=[GrassrootsAgent(inst.n, inst.m, budget) for _ in range(inst.n)])
    else:
        raise ValueError(setting)
    res = Engine(inst, attention_budget=budget, eps=eps, **parts).run()
    out = res["outcome"] or {}
    assert len(out) <= 1
    for o, g in out.items():                         # safety: only real yes answers
        assert all(inst.accept[i, o] for i in g)
    res["welfare"] = sum(len(g) for g in out.values())
    res["opt"] = optimum(inst)
    res["welfare_ratio"] = res["welfare"] / res["opt"] if res["opt"] else 1.0
    return res
