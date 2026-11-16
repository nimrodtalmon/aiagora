"""The planning step shared by the central coordinator and the grassroots agents.

Given what is known (K: YES / NO / UNKNOWN for every member and initiative),
compare two numbers:
  - the welfare that can be guaranteed now (known YES pairs only), and
  - the welfare that could be reached if every still-askable unknown were YES.
If they are equal, no answer can help: stop and output the guaranteed groups.
Otherwise, ask each member who is not yet served (if none: every askable
member) about one unknown initiative, chosen by Thompson sampling on how
popular each initiative looks so far: it explores early and exploits once it
has learned which initiatives are popular.

With smart=True: first spread questions so every initiative is sampled at
least twice; then ask greedily about the initiative with the highest estimated
popularity times its chance of still reaching the minimum group size.
"""
import numpy as np
from scipy.stats import binom
from ..model import UNKNOWN, NO, YES
from ..tasks.groups import best_assignment, welfare


def plan(K, asked, budget, min_size, rng, smart=False, batch=None):
    """Return (groups_now, questions); questions is None when it is time to stop,
    otherwise a list of (member, initiative). Updates `asked` in place."""
    n = K.shape[0]
    can_ask = np.ones(n, dtype=bool) if budget is None else asked < budget
    sure = K == YES
    maybe = sure | ((K == UNKNOWN) & can_ask[:, None])
    now = best_assignment(sure, min_size)
    if welfare(best_assignment(maybe, min_size)) == welfare(now):
        return now, None
    yes, no = (K == YES).sum(0), (K == NO).sum(0)
    served = {i for g in now.values() for i in g}
    askable = [i for i in range(n) if can_ask[i] and (K[i] == UNKNOWN).any()]
    targets = [i for i in askable if i not in served] or askable
    if batch is not None and len(targets) > batch:
        targets = list(rng.choice(targets, size=batch, replace=False))
    if smart:
        pop = (yes + 1) / (yes + no + 2)
        open_unk = ((K == UNKNOWN) & can_ask[:, None]).sum(0)
        need = np.maximum(0, min_size - yes)
        forms = np.where(need == 0, 1.0, binom.sf(need - 1, open_unk, pop))
        samples = yes + no
    qs = []
    for i in targets:
        unk = np.flatnonzero(K[i] == UNKNOWN)
        if smart:
            # first make sure every initiative has been sampled a little
            # (spread evenly), then go greedy on estimated popularity times
            # the chance that the initiative still reaches the minimum size
            thin = unk[samples[unk] < 2]
            if len(thin):
                j = int(thin[np.argmin(samples[thin] + rng.random(len(thin)))])
            else:
                j = int(unk[np.argmax(pop[unk] * forms[unk])])
            samples[j] += 1
        else:
            j = int(unk[np.argmax(rng.beta(yes[unk] + 1, no[unk] + 1))])
        asked[i] += 1
        qs.append((i, j))
    return now, (qs or None)
