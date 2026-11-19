#!/usr/bin/env python3
"""test_nutrient_floor.py — the bottom-up nutrient floor (nutrient_floor.py)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import floor_physics as fp
import nutrient_floor as N
import scenarios as S


def close(a, b, tol=1e-3):
    return abs(a - b) <= tol * max(1.0, abs(b))


def check() -> list:
    fails = []
    # since 2026-11-19 the model's own floor is GFI's cheapest: feed-grade amino acids at the most efficient need, $2.00
    if not close(fp.feedstock(fp.GOOD_CELLS), 2.0035, 2e-3) or not close(N.floor("feed", "eff"), fp.feedstock(fp.GOOD_CELLS), 1e-6):
        fails.append("the model's nutrient floor moved, or is no longer GFI's feed-grade, efficient floor")
    # 2026-11-19 audit batch: ammonia tolerance 4 mmol/L (best 11.16 -> 13.75 L/kg, central 28 -> 35) and lost runs pay for
    # their membranes: best 9.9613 -> 11.4569, central 26.4296 -> 32.8028
    for k, want in (("best", 11.4569), ("central", 32.8028)):
        if not close(S.run(S.SCENARIOS[k].choice)["total"], want, 1e-4):
            fails.append(f"{k}: default cost moved")
    # GFI's headline: amino acids below about $5 a kilo at low food-grade prices and the better bioconversion estimates
    if not N.aa_cost("low", "mid") < 5.0 or not N.aa_cost("low", "eff") < N.aa_cost("low", "mid"):
        fails.append("low food-grade amino acids should cost under $5 a kilo at 350 g/kg")
    # prices and needs order the floor
    for need in N.NEEDS:
        if not N.floor("feed", need) < N.floor("low", need) < N.floor("high", need):
            fails.append(f"floor out of order across price tiers at need {need}")
    for tier in N.TIERS:
        if not N.floor(tier, "eff") < N.floor(tier, "mid") < N.floor(tier, "low"):
            fails.append(f"floor out of order across needs at tier {tier}")
    # every other GFI floor is above the model's
    if not all(N.floor(t, n) > fp.feedstock(fp.GOOD_CELLS) for t in N.TIERS for n in N.NEEDS if (t, n) != ("feed", "eff")):
        fails.append("every GFI floor but the cheapest should exceed the model's $2.00")
    # the Engineered cells, all favourable case, whose medium is set by the floor, rises with dearer amino acids; central, set by litres x price, does not
    if not N.scenario_cost("best", "feed", "mid")["total"] > S.run(S.SCENARIOS["best"].choice)["total"]:
        fails.append("Engineered cells, all favourable should cost more at GFI's middle amino-acid need")
    if not close(N.scenario_cost("central", "feed", "eff")["total"], S.run(S.SCENARIOS["central"].choice)["total"], 1e-9):
        fails.append("central should not move at the cheapest amino acids: litres x price binds")
    # 2026-11-19 audit batch: at 35 L/kg Selected cells' $0.20 medium costs $7.00, above its nutrients plus its growth factors until
    # the floor passes about $3.3 a kilo. So Selected cells no longer moves at feed-grade prices and 350 g, or at low food-grade
    # prices and 232 g (it rose at both at 28 L/kg); it does at low food-grade prices and 350 g.
    base_c = S.run(S.SCENARIOS["central"].choice)["total"]
    for t, n in (("feed", "mid"), ("low", "eff")):
        if not close(N.scenario_cost("central", t, n)["total"], base_c, 1e-9):
            fails.append(f"central should not move at {t} prices and the {n} need: litres x price still binds")
    if not N.scenario_cost("central", "low", "mid")["total"] > base_c + 1.0:
        fails.append("central should rise at low food-grade prices and 350 g/kg")
    # the Engineered cells, all favourable case moves dollar for dollar with the floor (over the share of output not lost with lost tanks)
    d_floor = N.floor("low", "mid") - N.floor("feed", "eff")
    d_best = N.scenario_cost("best", "low", "mid")["total"] - N.scenario_cost("best", "feed", "eff")["total"]
    if not (d_floor <= d_best <= 1.02 * d_floor):
        fails.append("the Engineered cells, all favourable case should move dollar for dollar with the floor")
    # pinned
    # 2026-11-19 audit batch: the same two changes move all three (9.9613, 12.5648, 39.7235 before)
    for (k, t, n), want in {("best", "feed", "eff"): 11.4569, ("best", "low", "mid"): 14.0604, ("central", "high", "low"): 45.4289}.items():
        got = N.scenario_cost(k, t, n)["total"]
        if not close(got, want, 1e-3):
            fails.append(f"{k} {t} {n}: {got:.4f} != pinned {want}")
    return fails


def test_nutrient_floor():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the nutrient floor holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
