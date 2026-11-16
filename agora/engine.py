"""The engine: synchronous rounds, locality, and a ledger of every event.

Each round, every policy gets only its own view and returns a list of actions:

  ("ask", j)            agent asks its member about initiative j  (1 attention)
  ("send", to, payload) message to an agent id or to "C"           (eps each)
  ("report", payload)   silos only: one free report to the mechanism
  ("output", outcome)   the run's outcome (coordinator or mechanism)

Answers to questions and messages become visible in the next round.
The event log is the source of truth; costs and metrics are computed from it.
"""
import copy
from .model import UNKNOWN, NO, YES


class SimMember:
    """A simulated member: answers questions from its true acceptance row."""

    def __init__(self, row):
        self.row = row

    def answer(self, j):
        return bool(self.row[j])


class Engine:
    def __init__(self, inst, agents, coordinator=None, mechanism=None,
                 attention_budget=None, eps=0.01, max_rounds=200):
        self.inst = inst
        self.agents = agents
        self.coord = coordinator
        self.mechanism = mechanism
        self.budget = attention_budget
        self.eps = eps
        self.max_rounds = max_rounds
        self.members = [SimMember(inst.accept[i]) for i in range(inst.n)]
        self.est = inst.initial.copy()               # agents' estimates
        self.att = [0] * inst.n
        self.msgs = 0
        self.events = []
        self.inbox = {i: [] for i in range(inst.n)}
        self.inbox["C"] = []
        self.reports = {}
        self.outcome = None

    def log(self, t, kind, **kw):
        self.events.append({"t": t, "type": kind, **kw})

    def agent_view(self, t, i):
        return {"round": t, "me": i, "estimate": self.est[i].copy(),
                "inbox": self.inbox[i], "budget_left": self._left(i)}

    def coord_view(self, t):
        inst = self.inst
        return {"round": t, "inbox": self.inbox["C"], "n": inst.n, "m": inst.m,
                "min_size": inst.min_size, "budget": self.budget}

    def _left(self, i):
        return None if self.budget is None else self.budget - self.att[i]

    def run(self):
        for t in range(self.max_rounds):
            actions = []
            for i, pol in enumerate(self.agents):
                actions += [(i, a) for a in pol.act(self.agent_view(t, i))]
            if self.coord is not None:
                actions += [("C", a) for a in self.coord.act(self.coord_view(t))]
            self.inbox = {k: [] for k in self.inbox}
            for who, a in actions:
                self._apply(t, who, a)
            if self.outcome is not None:
                break
            if self.mechanism is not None and len(self.reports) == self.inst.n:
                self.outcome = self.mechanism(self.reports, self.inst)
                self.log(t, "output", by="M", outcome=self.outcome)
                break
        return self.result()

    def _apply(self, t, who, a):
        kind = a[0]
        if kind == "ask":
            j = a[1]
            if self.budget is not None and self.att[who] >= self.budget:
                self.log(t, "refused", agent=who, j=j)
                return
            ans = self.members[who].answer(j)
            self.att[who] += 1
            self.est[who][j] = YES if ans else NO
            self.log(t, "ask", agent=who, j=j, answer=int(ans))
        elif kind == "send":
            to, payload = a[1], a[2]
            self.msgs += 1
            self.inbox[to].append({"from": who, **payload})
            self.log(t, "msg", frm=who, to=to, payload=payload)
        elif kind == "report":
            self.reports[who] = a[1]
            self.log(t, "report", agent=who, payload=a[1])
        elif kind == "output":
            self.outcome = a[1]
            self.log(t, "output", by=who, outcome=a[1])

    def result(self):
        return {
            "outcome": self.outcome,
            "attention": sum(self.att),
            "attention_max": max(self.att) if self.att else 0,
            "messages": self.msgs,
            "cost": sum(self.att) + self.eps * self.msgs,
            "rounds": self.events[-1]["t"] + 1 if self.events else 0,
            "events": self.events,
        }
