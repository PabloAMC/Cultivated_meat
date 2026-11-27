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
    # 2026-11-27 (the nitrogen and carbon balance): best 6.9686 -> 7.0205; central unchanged (litres x price binds)
    for k, want in (("best", 7.0205), ("central", 48.6815)):
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
    # 2026-11-27 (the nitrogen and carbon balance, and scenario_cost sets the need directly): best feed eff 6.9686 -> 7.0205,
    # best low mid 9.8644 -> 9.9421, central high low 63.7218 -> 64.0478
    for (k, t, n), want in {("best", "feed", "eff"): 7.0205, ("best", "low", "mid"): 9.9421, ("central", "high", "low"): 64.0478}.items():
        got = N.scenario_cost(k, t, n)["total"]
        if not close(got, want, 1e-3):
            fails.append(f"{k} {t} {n}: {got:.4f} != pinned {want}")
    # 2026-11-21: the floor's glucose is the mass balance's for Humbird's enhanced cell with no lactate (inputs glucose_intensity)
    # 2026-11-27: and no ammonia, as the floor's amino acids are (nutrient_balance): 0.311 -> 0.3142
    import floor_physics as _fp
    from inputs import value as _v
    g0 = _fp.glucose_balance(_fp.GOOD_CELLS.o2_per_kg * 1000.0 / 32.0, 0.0, 0.0) * 0.18016
    if abs(g0 - _v("glucose_intensity")) > 0.0015:
        fails.append(f"the floor's glucose {_v('glucose_intensity')} kg a kilo should be the balance's {g0:.4f} (no lactate)")
    # 2026-11-27, the nitrogen and carbon balance (floor_physics.nutrient_balance):
    # (1) at the floor the medium's amino acids carry the cells' nitrogen and no more: 0.232 kg x 12.30 mol/kg = 2.86 mol
    n_cells = _v("ml_n_per_dry") * _v("ml_dry_mol_kg")
    if abs(_v("aa_intensity") * _v("nb_aa_n_kg") / n_cells - 1.0) > 0.01:
        fails.append(f"the floor's amino acids carry {_v('aa_intensity') * _v('nb_aa_n_kg'):.3f} mol N, not the cells' {n_cells:.3f}")
    # (2) each mol of ammonia takes 1 / nb_aa_n_kg kg more amino acids, and the floor keeps all the nitrogen
    nb0, nb1 = _fp.nutrient_balance(_fp.GOOD_CELLS), _fp.nutrient_balance(_fp.GOOD_CELLS, nh3=1.0)
    if not close(nb1["aa_kg"] - nb0["aa_kg"], 1.0 / _v("nb_aa_n_kg"), 1e-9) or not close(nb0["n_kept"], 1.0, 0.01):
        fails.append(f"amino acids per mol of ammonia {nb1['aa_kg'] - nb0['aa_kg']:.4f} kg, nitrogen kept at the floor {nb0['n_kept']:.3f}")
    # (3) the carbon balance is glucose_balance with the lactate in mol: G = A + B + lactate / 2
    for nh3, y in ((0.054, 0.28), (0.14, 1.05), (0.0, 0.0)):
        o2 = _fp.GOOD_CELLS.o2_per_kg * 1000.0 / 32.0
        g = _fp.glucose_balance(o2, nh3, y)
        nb = _fp.nutrient_balance(_fp.GOOD_CELLS, nh3=nh3, lac=y * g)
        if not close(nb["glc_mol"], g, 1e-9):
            fails.append(f"carbon balance at NH3 {nh3}, Y {y}: {nb['glc_mol']:.4f} mol against glucose_balance's {g:.4f}")
    # (4) cells that make waste eat more than the floor, and explore() charges what they eat
    r = _fp.explore(nh3_kg=0.14, lac_yield=1.05, glc_balance=True, medium_price=0.0)
    if not r["nutrients"] > _fp.feedstock(_fp.GOOD_CELLS) + 0.2 or not close(r["feedstock"] * r["harvested_share"], r["nutrients"], 0.05):
        fails.append(f"cells making 0.14 mol ammonia and 1.05 lactate eat ${r['nutrients']:.2f}, charged ${r['feedstock']:.2f}")
    # 2026-11-27, the cells' fat (lipid_share) and the measures other models report:
    # (5) Humbird's 15% reproduces the model as it was, exactly
    if _fp.explore(lipid_share=_v("gb_f_lipid"))["total"] != _fp.explore()["total"]:
        fails.append("lipid_share at Humbird's 15% should change nothing")
    if not close(_fp.anabolic_glucose(), _v("pf_glc_anabolic"), 1e-12) or not close(_fp.cell_rq(), _v("pf_rq"), 1e-12) \
            or not close(_fp.cell_rq(fat_fed=1.0), _v("pf_rq") - _v("pf_rq_lipid"), 1e-12):
        fails.append("anabolic glucose or RQ at Humbird's cell moved")
    # (6) fat made from glucose: more glucose, more CO2 per oxygen; fat from the feed: neither; amino acids follow the lean mass
    lo, hi = _fp.nutrient_balance(_fp.GOOD_CELLS, lipid_share=0.05), _fp.nutrient_balance(_fp.GOOD_CELLS, lipid_share=0.45)
    if not (hi["glc_kg"] > lo["glc_kg"] and hi["aa_kg"] < lo["aa_kg"] and _fp.cell_rq(lipid_share=0.45) > _fp.cell_rq()
            and close(_fp.cell_rq(fat_fed=1.0, lipid_share=0.45), _fp.cell_rq(fat_fed=1.0), 1e-12)
            and close(hi["aa_kg"] / lo["aa_kg"], 0.55 / 0.95, 1e-9) and close(hi["n_kept"], 1.0, 0.01)):
        fails.append("the fat trait: glucose, amino acids, RQ or nitrogen do not move as they should")
    r45, r45f = _fp.explore(lipid_share=0.45), _fp.explore(lipid_share=0.45, fat_fed=1.0)
    if not (r45["limits"]["CO2 removal"] < _fp.explore()["limits"]["CO2 removal"] and r45f["limits"]["CO2 removal"] > r45["limits"]["CO2 removal"]):
        fails.append("fattier cells that make their fat should be held thinner by CO2, and fed fat should lift that")
    # (7) the measures: a kilo of Humbird's cells is 210 g of protein, 45 g of fat, 1,425 kcal; costs per kg of dry matter and protein
    m = _fp.explore()["metrics"]; t = _fp.explore()["total"]
    if not (close(m["protein_kg"], 0.21, 1e-9) and close(m["lipid_kg"], 0.045, 1e-9) and close(m["kcal_kg"], 1425.0, 1e-9)
            and close(m["cost_dry"], t / 0.3, 1e-9) and close(m["cost_protein"], t / 0.21, 1e-9) and m["fcr_dry"] > 1.0 and m["fcr_energy"] > 1.0):
        fails.append(f"the measures other models report are off: {m}")
    return fails


def test_nutrient_floor():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the nutrient floor holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
