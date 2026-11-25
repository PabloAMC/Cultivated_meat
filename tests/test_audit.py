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
    # 2026-11-20 model batch: the two swapped places. The membrane life's most likely value moved from 3,960 to 2,415 L/m2
    # (Humbird's replacement schedule), so a litre filtered costs $0.60 of membrane, not $0.37, and the same 900-5,500 range
    # moves the cost further: membrane life -0.51, ammonia +0.48 (seed 0; the order is the same on seeds 1 and 2). The check
    # is that these two lead, in either order, with the signs they must have.
    # 2026-11-21: the draws now include the lactate and ammonia the cells tolerate, the bubble kill and the harvest recovery
    # (audit.LIMIT_INPUTS): membrane life -0.43 leads, then the lactate tolerated -0.35 and the ammonia tolerated -0.31, ahead of
    # the lactate and the ammonia the cells make (+0.28, +0.27)
    top = list(cen["rank"])[:3]
    if top[0] != "rt_membrane_life" or set(top[1:]) != {"lac_limit", "nh3_limit"} or not all(cen["rank"][k] < 0 for k in top):
        fails.append(f"the main drivers should be membrane life, then the lactate and ammonia the cells tolerate: {top}")
    # seeds agree
    # 2026-11-20: the allowance was $1 when the median was $46 and the 10th-to-90th spread $32. The median is now $65 and the
    # spread $38, so the sampling error of a 1,000-draw median grew with them (seeds 0, 1, 2 give 65.2, 67.0, 65.9). The
    # allowance is now 4% of the median, about $2.6.
    other = A.summary("central", 1000, 1)
    if abs(other["p50"] - cen["p50"]) > 0.04 * cen["p50"]:
        fails.append("the median should not move by 4% between seeds")
    # pinned (seed 0, 1,000 draws)
    # 2026-11-19 audit batch: ammonia tolerance 5 -> 4 mmol/L (the low-lactate example 28 -> 35 L/kg, best 11.2 -> 13.75) and lost runs pay
    # for their membranes: central P50 37.44 -> 47.57, P10 27.03 -> 34.38, best P50 15.48 -> 19.35. These pin the module as
    # it draws today. Its docstring lists three ways the draws lag the scenarios (growth factors bought on top of the low-lactate example'
    # complete medium, a price per litre for the all-favourable example's floor medium, the ammonia tolerance not drawn); put right,
    # the low-lactate example's median is about $38 and the all-favourable example's about $14, close to the scenario bands.
    # 2026-11-19 restructure: the low-lactate cells' ammonia range widened (low end 0.07 -> 0.04 mol/kg) and every cell weighs 2 ng:
    # central P50 47.57 -> 45.77, P10 34.38 -> 32.38, best P50 19.35 -> 19.57
    # 2026-11-20 model batch (lactate tolerated 35 mmol/L, medium preparation with the medium passed, bubble deaths charged,
    # twice the crew, harvest loss, membrane life 2,415 L/m2): central P50 45.77 -> 65.24, P10 32.38 -> 50.60, best P50
    # 19.57 -> 24.57. The draws do not draw the lactate tolerated, the bubble kill or the harvest recovery (all new).
    # 2026-11-20 final model: central P50 65.24 -> 64.62, P10 50.60 -> 50.31; best P50 24.57 -> 11.37 (the all-favourable case
    # is now scenarios.all_favourable, $7.62: Humbird's cell traits, dialyser-grade membranes, 42 m3, no runs lost)
    # 2026-11-21: the draws put right (growth factors inside a complete medium, no price per litre on a floor medium, the
    # tolerated waste, kill and harvest drawn) and the model of 2026-11-21: central P50 64.62 -> 57.68, P10 50.31 -> 42.62,
    # best P50 11.37 -> 8.22
    # 2026-11-25 (the gas cap and loop thinning): the engine now tries every gas flow up to the cells' cap and holds a design
    # whose column loop is overloaded thinner, so draws that priced an overloaded loop as if it coped now cost what a loop that
    # passes costs (cheaper where a lower gas flow pays): central P50 57.68 -> 57.22, P10 42.62 -> 42.36, best P50 8.22 -> 8.11.
    # The point percentiles (0.26, 0.11) and the ranking (membrane life -0.40, lactate tolerated -0.37, ammonia -0.32) hold
    for name, s, want in (("central P50", cen["p50"], 57.22), ("central P10", cen["p10"], 42.36), ("best P50", best["p50"], 8.11)):
        if not close(s, want, 5e-3):
            fails.append(f"{name}: {s:.2f} != pinned {want}")
    # the retail translation: the model's rule is per-kg costs plus a percentage margin; it sits between the old flat $5
    # and a chain that takes the whole spread as a percentage, at the low-lactate example's cost
    want = (10.0 + value("markup_add")) / (1.0 - value("retail_margin"))
    if not close(A.retail(10.0), want, 1e-12):
        fails.append("the model's retail price is (cost + markup_add) / (1 - retail_margin)")
    # 2026-11-19 audit batch: at the low-lactate example's own cost ($32.80 then, $49.96 since 2026-11-20; the check used $26.64, the low-lactate example's cost on 15 November)
    c_cost = S.run(S.SCENARIOS["central"].choice)["total"]
    if not (A.retail(c_cost, "flat") < A.retail(c_cost) < A.retail(c_cost, "proportional")):
        fails.append("at the low-lactate example's cost the model's shelf price should sit between the flat and the proportional rule")
    # since the audit batch the low-lactate example's point sits below the 10th percentile of these draws (it was the 19th percentile on
    # 16 November), and the all-favourable example's below the 1st
    # 2026-11-19 restructure: with the wider ammonia range the low-lactate example's point sits at about the 10th percentile (it was below it)
    # 2026-11-20 model batch: the all-favourable example's point is no longer below the 1st percentile of its draws. It sits at
    # about the 13th (0.13 to 0.16 over seeds 0 to 2; 0.15 with 4,000 draws). Cause: the membrane life's most likely value
    # moved from 3,960 to 2,415 L/m2 inside the same 900-5,500 range. Two thirds of the draws now give a membrane that lasts
    # longer than the point's (before, a third did), so a share of the draws cost less than the point. The
    # low-lactate example stays at about the 9th to 10th percentile: its other drawn inputs still lean to the costly side.
    # 2026-11-20 final model: the all-favourable example's point is again below the 1st percentile (0.007 to 0.008 over seeds 0
    # to 2 and with 4,000 draws). A correct consequence of the case's definition, not a defect: scenarios.all_favourable takes
    # the favourable end of every lever (no runs lost, the medium at the nutrient floor, Humbird's 0.054 mol of ammonia a kilo),
    # and these draws put runs lost, a price per litre on the medium and the ammonia of sc_nh3_engineered's range on top, so
    # almost every draw costs more. Its membrane life is passed to explore directly, so that draw no longer reaches it.
    # 2026-11-21: with the draws put right the all-favourable example's point sits at about the 9th percentile (no price per litre
    # on its floor medium, its ammonia and lactate tolerated drawn around Humbird's 5 and 50) and the low-lactate example's at the 26th
    # (the growth factors are no longer bought twice)
    if not (0.15 < cen["point_percentile"] < 0.35 and 0.03 < best["point_percentile"] < 0.15):
        fails.append(f"the low-lactate example's point should sit near the 26th percentile of its draws ({cen['point_percentile']:.2f}), "
                     f"and the all-favourable example's near the 9th ({best['point_percentile']:.2f})")
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
