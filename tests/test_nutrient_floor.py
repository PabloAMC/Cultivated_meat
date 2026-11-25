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
    # 2026-11-21: 2.0035 -> 1.9999 (the floor's glucose is the mass balance's, 0.311 kg a kilo, not 0.32)
    if not close(fp.feedstock(fp.GOOD_CELLS), 1.9999, 2e-3) or not close(N.floor("feed", "eff"), fp.feedstock(fp.GOOD_CELLS), 1e-6):
        fails.append("the model's nutrient floor moved, or is no longer GFI's feed-grade, efficient floor")
    # 2026-11-19 audit batch: ammonia tolerance 4 mmol/L (best 11.16 -> 13.75 L/kg, central 28 -> 35) and lost runs pay for
    # their membranes: best 9.9613 -> 11.4569, central 26.4296 -> 32.8028
    # 2026-11-20 batch: best 11.6738 -> 18.7144, central 32.8028 -> 49.9616
    # 2026-11-20 final pass: the all-favourable example is now scenarios.all_favourable() (18.7144 -> 7.6209); the low-lactate
    # example 49.9616 -> 49.4977 (the fixes to bubble deaths and viscous oxygen transfer)
    # 2026-11-21 (Humbird back-test fixes, thinned tank designs, floor glucose): best 7.6209 -> 6.9686, central 49.4977 -> 48.6815
    for k, want in (("best", 6.9686), ("central", 48.6815)):
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
    # the all-favourable example, whose medium is set by the floor, rises with dearer amino acids; central, set by litres x price, does not
    if not N.scenario_cost("best", "feed", "mid")["total"] > S.run(S.SCENARIOS["best"].choice)["total"]:
        fails.append("the all-favourable example should cost more at GFI's middle amino-acid need")
    if not close(N.scenario_cost("central", "feed", "eff")["total"], S.run(S.SCENARIOS["central"].choice)["total"], 1e-9):
        fails.append("central should not move at the cheapest amino acids: litres x price binds")
    # 2026-11-19 audit batch: at 35 L/kg the low-lactate example's $0.20 medium costs $7.00, above its nutrients plus its growth factors until
    # the floor passes about $3.3 a kilo. So the low-lactate example no longer moves at feed-grade prices and 350 g, or at low food-grade
    # prices and 232 g (it rose at both at 28 L/kg); it does at low food-grade prices and 350 g.
    # 2026-11-20 batch: CHANGED. Growth factors are now dosed per litre from Humbird's fed-batch 8.65 L/kg (it was 11.2), so the
    # 30% of them inside the low-lactate example's complete medium cost more: its nutrients plus those growth factors come to within
    # 3 cents a kilo of its 35 litres at $0.20 ($7.00). So ANY dearer amino-acid floor now raises its cost, by nearly the
    # floor's rise over the share of the cells harvested; before the batch it did not move until the floor passed about $3.3.
    base_r = S.run(S.SCENARIOS["central"].choice)
    base_c = base_r["total"]
    for t, n in (("feed", "mid"), ("low", "eff"), ("low", "mid")):
        rise = N.scenario_cost("central", t, n)["total"] - base_c
        d = N.floor(t, n) - N.floor("feed", "eff")
        if not (0.9 * d < rise <= 1.02 * d / base_r["harvested_share"] / 0.8):
            fails.append(f"central should rise by about the floor's rise (${d:.2f}) at {t} prices and the {n} need, got ${rise:.2f}")
    # the all-favourable example moves dollar for dollar with the floor (over the share of output not lost with lost tanks)
    d_floor = N.floor("low", "mid") - N.floor("feed", "eff")
    d_best = N.scenario_cost("best", "low", "mid")["total"] - N.scenario_cost("best", "feed", "eff")["total"]
    d_best *= S.run(S.SCENARIOS["best"].choice)["harvested_share"]     # 2026-11-20: costs are per kilo harvested; the floor is per kilo grown
    # 2026-11-20 final pass: the all-favourable example now loses no runs (Humbird's design loses none, and the case takes the
    # more favourable source), so it moves EXACTLY dollar for dollar per kilo grown; before, lost tanks made it move a little
    # more. The lower bound allows 1e-9 for floating-point rounding only (the two differed by 4e-16 and the check failed on that).
    if not (d_floor - 1e-9 <= d_best <= 1.02 * d_floor):
        fails.append("the all-favourable example should move dollar for dollar with the floor")
    # pinned
    # 2026-11-19 audit batch: the same two changes move all three (9.9613, 12.5648, 39.7235 before)
    # 2026-11-20 batch: 11.6738, 14.2773, 45.4289 before
    # 2026-11-20 final pass: 18.7144, 21.6023, 65.7209 before (the all-favourable example redefined; viscous oxygen, bubble deaths)
    # 2026-11-21: 7.6209, 10.4139, 64.7523 before (the same causes)
    # 2026-11-25 (the gas cap and loop thinning): central high low 63.9312 -> 63.7218 (the engine thins the loop for this medium itself)
    for (k, t, n), want in {("best", "feed", "eff"): 6.9686, ("best", "low", "mid"): 9.8644, ("central", "high", "low"): 63.7218}.items():
        got = N.scenario_cost(k, t, n)["total"]
        if not close(got, want, 1e-3):
            fails.append(f"{k} {t} {n}: {got:.4f} != pinned {want}")
    # 2026-11-21: the floor's glucose is the mass balance's for Humbird's enhanced cell with no lactate (inputs glucose_intensity)
    import floor_physics as _fp
    from inputs import value as _v
    g0 = _fp.glucose_balance(_fp.GOOD_CELLS.o2_per_kg * 1000.0 / 32.0, _v("pf_nh3_efficient"), 0.0) * 0.18016
    if abs(g0 - _v("glucose_intensity")) > 0.0015:
        fails.append(f"the floor's glucose {_v('glucose_intensity')} kg a kilo should be the balance's {g0:.4f} (no lactate)")
    return fails


def test_nutrient_floor():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the nutrient floor holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
