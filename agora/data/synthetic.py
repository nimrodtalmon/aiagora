"""Synthetic instances: a neighborhood with initiatives of varying popularity."""
import numpy as np
from ..model import Instance, UNKNOWN

INITIATIVES = ["garden", "carpool north", "carpool south", "running club",
               "book club", "solar panels", "playgroup", "tool library",
               "street cleanup", "choir", "chess", "shared nanny",
               "bulk groceries", "dog walking", "repair cafe", "languages"]


def neighborhood(n=30, m=12, min_size=3, pop=(0.03, 0.25), informed=0.0, seed=0):
    """n residents, m initiatives; resident i accepts initiative j with
    probability pop_j; each agent initially knows each entry of its member's
    row with probability `informed`."""
    rng = np.random.default_rng(seed)
    popularity = rng.uniform(*pop, size=m)
    accept = rng.random((n, m)) < popularity
    initial = np.where(rng.random((n, m)) < informed,
                       accept.astype(np.int8), np.int8(UNKNOWN)).astype(np.int8)
    names = {"members": [f"resident {i}" for i in range(n)],
             "initiatives": [INITIATIVES[j % len(INITIATIVES)] for j in range(m)]}
    return Instance(accept=accept, min_size=min_size, initial=initial, names=names)


def planted(n, m, k, groups=1, noise=0.0, seed=0):
    """Planted groups: `groups` disjoint sets of k members, each accepting its own
    random initiative (distinct initiatives); every member also accepts each
    other initiative with probability `noise`. Minimum group size k."""
    rng = np.random.default_rng(seed)
    accept = rng.random((n, m)) < noise
    members = rng.permutation(n)
    inits = rng.permutation(m)
    for g in range(groups):
        accept[members[g * k:(g + 1) * k], inits[g]] = True
    initial = np.full((n, m), UNKNOWN, dtype=np.int8)
    return Instance(accept=accept, min_size=k, initial=initial,
                    names={"members": [f"member {i}" for i in range(n)],
                           "initiatives": [f"initiative {j}" for j in range(m)]})
