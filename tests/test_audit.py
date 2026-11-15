#!/usr/bin/env python3
"""test_audit.py — the global uncertainty run and the retail translation (audit.py)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import audit as A
import scenarios as S
from inputs import value


def close(a, b, tol=1e-3):
    return abs(a - b) <= tol * max(1.0, abs(b))


def check() -> list:
    fails = []
    cen = A.summary("central", 1000, 0)
    best = A.summary("best", 1000, 0)
    # the point estimates are the scenarios' own
    if not close(cen["point"], S.run(S.SCENARIOS["central"].choice)["total"], 1e-12):
        fails.append("the central point is not the scenario's cost")
    # the draws are ordered, and the point estimate is on the low side of its own uncertainty
    for name, s in (("central", cen), ("best", best)):
        if not s["p10"] < s["p50"] < s["p90"]:
            fails.append(f"{name}: percentiles out of order")
        if not s["point_percentile"] < 0.35:
            fails.append(f"{name}: the point estimate should sit below the 35th percentile of its own uncertainty")
    # no draw of the central case reaches the cost of the reference case or the parity cost
    if cen["at_or_below"][12.0] > 0.0 or cen["at_or_below"][7.0] > 0.0:
        fails.append("central draws should not reach $12")
    # the cells' ammonia is what moves the cost most, then the membranes' life (negatively)
    top = list(cen["rank"])[:2]
    if top[0] != "nh3_kg" or "rt_membrane_life" not in top or not cen["rank"]["rt_membrane_life"] < 0:
        fails.append(f"the main drivers should be ammonia and membrane life: {top}")
    # seeds agree
    other = A.summary("central", 1000, 1)
    if abs(other["p50"] - cen["p50"]) > 1.0:
        fails.append("the median should not move by $1 between seeds")
    # pinned (seed 0, 1,000 draws)
    for name, s, want in (("central P50", cen["p50"], 33.99), ("central P10", cen["p10"], 24.30), ("best P50", best["p50"], 14.42)):
        if not close(s, want, 5e-3):
            fails.append(f"{name}: {s:.2f} != pinned {want}")
    # the retail translation: the flat markup is the model's; a proportional chain gives a dearer shelf price and a lower parity cost
    if not close(A.retail(10.0), 10.0 + value("markup_add"), 1e-12):
        fails.append("the flat retail price is cost + markup")
    if not (A.retail(26.64, "proportional") > A.retail(26.64) and A.parity_cost("proportional") < A.parity_cost()):
        fails.append("a proportional chain should raise the price and lower the parity cost")
    return fails


def test_audit():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the audit holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
