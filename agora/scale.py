"""Scale paradox: broadcast channel vs. agent routing (simplest model). Exact.

Setting. n members; activity types t. Each member accepts type t independently
with probability p_t (popularity). Type t has one initiator, a member who accepts
it. The group of type t forms if at least k members accept and are reached (the
initiator counts). The initiator gains B if the group forms and pays c for each
reached member who does not accept it (bothered). It announces iff
    B * P(forms) >= c * E[bothered].
Welfare: expected number of groups formed = sum over announced types of P(forms).

Broadcast: an announcement reaches all n-1 others.
Agora: each member's agent guesses whether its member accepts t, wrongly with
probability eps, independently. The initiator's agent invites the members guessed
to accept, in uniformly random order, and stops once k-1 of them accepted.

Every expectation below is computed exactly (no sampling).
"""
import numpy as np
from scipy.stats import binom


def popularity(T=300, top=0.5, zipf=1.0):
    return top / np.arange(1, T + 1) ** zipf


# ---------- broadcast ----------
def broadcast_stats(n, p, k):
    """(P(forms), E[bothered]) for one type under broadcast."""
    return binom.sf(k - 2, n - 1, p), (1 - p) * (n - 1)


# ---------- agora ----------
def agora_stats(n, p, k, eps):
    """(P(forms), E[bothered]) for one type under agent routing.

    Each other member is a candidate (guessed to accept) w.p. q, independently;
    a candidate accepts w.p. r. In random order, candidates form a Bernoulli(r)
    sequence of length M ~ Bin(n-1, q). With T the position of the (k-1)-th yes,
    invited = min(M, T), yeses = min(S_M, k-1), bothered = invited - yeses.
    """
    q = p * (1 - eps) + (1 - p) * eps
    r = p * (1 - eps) / q
    m = np.arange(n)                                     # possible values of M
    pm = binom.pmf(m, n - 1, q)
    # E[min(m, T)] = sum_{j<m} P(T > j) = sum_{j<m} P(Bin(j, r) <= k-2)
    tail = binom.cdf(k - 2, m, r)                        # P(T > j) for j = m
    e_inv = np.concatenate([[0.0], np.cumsum(tail)[:-1]])
    # E[min(S_m, k-1)] = (k-1) - sum_{s<k-1} (k-1-s) P(S_m = s)
    s = np.arange(k - 1)
    e_yes = (k - 1) - ((k - 1 - s)[None, :] * binom.pmf(s[None, :], m[:, None], r)).sum(1)
    pform_m = binom.sf(k - 2, m, r)
    return float(pm @ pform_m), float(pm @ (e_inv - e_yes))


def agora_limit_bothered(p, k, eps):
    """lim_{n->inf} E[bothered] = (k-1)(1-r)/r (negative binomial mean)."""
    r = p * (1 - eps) / (p * (1 - eps) + (1 - p) * eps)
    return (k - 1) * (1 - r) / r


# ---------- welfare ----------
def groups(n, ps, k, B, c, eps=None):
    """Expected number of groups formed; eps=None means broadcast."""
    tot = 0.0
    for p in ps:
        pf, eb = broadcast_stats(n, p, k) if eps is None else agora_stats(n, p, k, eps)
        if B * pf >= c * eb:
            tot += pf
    return tot


def viable(n, ps, k):
    """Benchmark: expected number of types with at least k acceptors (initiator incl.)."""
    return float(sum(binom.sf(k - 2, n - 1, p) for p in ps))


def agora_limit(ps, k, B, c, eps):
    """Theorem 2: number of types with (k-1)(1-r_t)/r_t < B/c."""
    return int(sum(agora_limit_bothered(p, k, eps) < B / c for p in ps))
