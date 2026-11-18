"""Scale paradox, deterministic worst-case model.

Setting. A community N of n members; activity types t, each with an acceptance
set A_t (a_t = |A_t| members accept t) and an initiator in A_t. The group of t
forms if at least k members of A_t are reached (the initiator counts). A reached
member outside A_t is bothered. The initiator gains B if the group forms and pays
c per bothered member. It knows a_t (not who accepts) and announces t iff, in the
worst case over what it does not know, the group forms and B >= c * bothered.

Broadcast: an announcement reaches all n-1 others.
Agora: each member's agent guesses whether its member accepts t; for each t, at
most `err` guesses are wrong. The initiator's agent invites the members guessed
to accept, one at a time in some order (worst case: any order), and stops once
k-1 invited members accepted.

Welfare: the number of groups formed.
"""
import itertools
import numpy as np


# ---------- closed forms (Theorems 1 and 2) ----------
def broadcast_forms(n, a, k, B, c):
    return a >= k and c * (n - a) <= B


def agora_forms(n, a, k, B, c, err):
    return a >= k + err and c * min(err, n - a) <= B


def groups(n, shares, k, B, c, err=None):
    """Groups formed in a community of n members where type t has floor(s_t n) acceptors."""
    tot = 0
    for s in shares:
        a = int(np.floor(s * n + 1e-9))
        ok = broadcast_forms(n, a, k, B, c) if err is None else agora_forms(n, a, k, B, c, err)
        tot += ok
    return tot


def broadcast_window(s, k, B, c, nmax=10**6):
    """Sizes n at which a type of share s forms under broadcast: an interval (or empty)."""
    ns = [n for n in range(1, nmax) if broadcast_forms(n, int(np.floor(s * n + 1e-9)), k, B, c)]
    return (ns[0], ns[-1]) if ns else None


# ---------- the processes themselves (for brute-force checks) ----------
def run_broadcast(n, A):
    """(reached acceptors incl. initiator, bothered)."""
    return len(A), n - len(A)


def run_agora(A, guess, order, k, initiator):
    """Invite guessed members (initiator excluded) in `order` until k-1 accept."""
    yes, bothered = 0, 0
    for i in order:
        if i == initiator or i not in guess:
            continue
        if yes == k - 1:
            break
        if i in A:
            yes += 1
        else:
            bothered += 1
    return 1 + yes, bothered


def robust_announce_agora(n, A, initiator, k, B, c, err):
    """Announce iff for every guess pattern with <= err wrong guesses (initiator's own
    agent is never wrong about it) and every invitation order: forms and B >= c*bothered."""
    others = [i for i in range(n) if i != initiator]
    for e in range(err + 1):
        for wrong in itertools.combinations(others, e):
            guess = {i for i in others if (i in A) != (i in wrong)}
            for order in itertools.permutations(sorted(guess)):
                reached, both = run_agora(A, guess, order, k, initiator)
                if reached < k or B < c * both:
                    return False
    return True


def robust_announce_broadcast(n, A, k, B, c):
    reached, both = run_broadcast(n, A)
    return reached >= k and B >= c * both
