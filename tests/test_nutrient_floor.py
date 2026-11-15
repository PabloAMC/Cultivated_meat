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
    # the default is untouched: the model's own floor is $1.70 and the scenarios keep their costs
    if not close(fp.feedstock(fp.GOOD_CELLS), 1.70, 2e-3):
        fails.append("the model's nutrient floor moved")
    for k, want in (("best", 8.9488), ("central", 26.6381)):
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
    # every bottom-up floor is above the model's
    if not N.floor("feed", "eff") > fp.feedstock(fp.GOOD_CELLS):
        fails.append("the cheapest GFI floor should exceed the model's $1.70")
    # the best case, whose medium is set by the floor, rises; central, set by litres x price, does not (at cheap amino acids)
    if not N.scenario_cost("best", "feed", "eff")["total"] > S.run(S.SCENARIOS["best"].choice)["total"]:
        fails.append("best case should cost more with GFI's amino acid prices")
    if not close(N.scenario_cost("central", "feed", "eff")["total"], S.run(S.SCENARIOS["central"].choice)["total"], 1e-9):
        fails.append("central should not move at the cheapest amino acids: litres x price binds")
    # pinned
    for (k, t, n), want in {("best", "feed", "eff"): 9.7573, ("best", "low", "mid"): 12.3609, ("central", "high", "low"): 37.3903}.items():
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
