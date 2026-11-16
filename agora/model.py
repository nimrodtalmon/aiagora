"""The basic model, for the task of forming groups.

Follows the AI-Agora position paper (single-membership variant) and the
BSF proposal's basic model:

- members 0..n-1, one agent each;
- initiatives 0..m-1;
- member i accepts initiative j or not (accept[i, j]);
- an assignment puts each member in at most one initiative; an initiative
  forms only with at least `min_size` members, all of whom accept it;
- welfare = number of members served (assigned to some initiative).

Agent i holds an estimate of row i: for each initiative, YES / NO / UNKNOWN.
Estimates are never wrong (basic model): known entries match the truth.
"""
from dataclasses import dataclass
import numpy as np

UNKNOWN, NO, YES = -1, 0, 1


@dataclass
class Instance:
    accept: np.ndarray          # bool, shape (n, m): true acceptance sets
    min_size: int               # smallest group that may form
    initial: np.ndarray         # int8, shape (n, m): agents' initial estimates
    names: dict | None = None   # optional story labels (members, initiatives)

    @property
    def n(self):
        return self.accept.shape[0]

    @property
    def m(self):
        return self.accept.shape[1]

    def to_json(self):
        return {
            "accept": self.accept.astype(int).tolist(),
            "min_size": self.min_size,
            "initial": self.initial.astype(int).tolist(),
            "names": self.names,
        }
