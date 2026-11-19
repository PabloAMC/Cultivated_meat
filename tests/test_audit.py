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
    # 2026-11-19 audit batch: still true of these draws, which do not draw the ammonia the cells tolerate (sc_nh3_limit, new).
    # With it drawn the tolerance ranks first and the ammonia second (audit.py's docstring; a side calculation, not pinned)
    top = list(cen["rank"])[:2]
    if top[0] != "nh3_kg" or "rt_membrane_life" not in top or not cen["rank"]["rt_membrane_life"] < 0:
        fails.append(f"the main drivers should be ammonia and membrane life: {top}")
    # seeds agree
    other = A.summary("central", 1000, 1)
    if abs(other["p50"] - cen["p50"]) > 1.0:
        fails.append("the median should not move by $1 between seeds")
    # pinned (seed 0, 1,000 draws)
    # 2026-11-19 audit batch: ammonia tolerance 5 -> 4 mmol/L (Selected cells 28 -> 35 L/kg, best 11.2 -> 13.75) and lost runs pay
    # for their membranes: central P50 37.44 -> 47.57, P10 27.03 -> 34.38, best P50 15.48 -> 19.35. These pin the module as
    # it draws today. Its docstring lists three ways the draws lag the scenarios (growth factors bought on top of Selected cells'
    # complete medium, a price per litre for the Engineered cells, all favourable case's floor medium, the ammonia tolerance not drawn); put right,
    # Selected cells' median is about $38 and the Engineered cells, all favourable case's about $14, close to the scenario bands.
    # 2026-11-19 restructure: the selected cells' ammonia range widened (low end 0.07 -> 0.04 mol/kg) and every cell weighs 2 ng:
    # central P50 47.57 -> 45.77, P10 34.38 -> 32.38, best P50 19.35 -> 19.57
    for name, s, want in (("central P50", cen["p50"], 45.77), ("central P10", cen["p10"], 32.38), ("best P50", best["p50"], 19.57)):
        if not close(s, want, 5e-3):
            fails.append(f"{name}: {s:.2f} != pinned {want}")
    # the retail translation: the model's rule is per-kg costs plus a percentage margin; it sits between the old flat $5
    # and a chain that takes the whole spread as a percentage, at Selected cells' cost
    want = (10.0 + value("markup_add")) / (1.0 - value("retail_margin"))
    if not close(A.retail(10.0), want, 1e-12):
        fails.append("the model's retail price is (cost + markup_add) / (1 - retail_margin)")
    # 2026-11-19 audit batch: at Selected cells' own cost ($32.80; the check used $26.64, Selected cells' cost on 15 November)
    c_cost = S.run(S.SCENARIOS["central"].choice)["total"]
    if not (A.retail(c_cost, "flat") < A.retail(c_cost) < A.retail(c_cost, "proportional")):
        fails.append("at Selected cells' cost the model's shelf price should sit between the flat and the proportional rule")
    # since the audit batch Selected cells' point sits below the 10th percentile of these draws (it was the 19th percentile on
    # 16 November), and the Engineered cells, all favourable case's below the 1st
    # 2026-11-19 restructure: with the wider ammonia range Selected cells' point sits at about the 10th percentile (it was below it)
    if not (cen["point_percentile"] < 0.12 and best["point_percentile"] < 0.01):
        fails.append("Selected cells' point should sit near the 10th percentile of its draws, and the Engineered cells, all favourable case's below the 1st")
    if not close(A.retail(A.parity_cost()), value("p_conv"), 1e-9):
        fails.append("the parity cost should give a shelf price equal to meat's")
    return fails


def test_audit():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the audit holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
