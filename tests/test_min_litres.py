#!/usr/bin/env python3
"""test_min_litres.py — the least medium per kg of cells that physics allows (min_litres.py)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import floor_physics as fp
import min_litres as M
import scenarios as S
from inputs import REGISTRY, value

# L/kg and $/kg at the bounds, per scenario (the scenarios' own costs are pinned in test_scenarios and test_golden)
# 2026-11-19 repin: nutrient floor $1.70 -> $2.00 (+$0.30 wherever the floor binds); growth factors inside complete media
# prices (the low-lactate example's bounds fall, but a complete medium never costs less than its nutrients plus its growth factors,
# gf_in_medium); Best's medium is now the nutrient floor, not $0.15 a litre (its bath bound falls $1.47)
# 2026-11-19 audit batch: the litres at the bounds did not move (none depends on the ammonia tolerance); every cost rose
# because a lost run now throws its filter membranes away early (floor_physics run_frac), by $0.05-0.72 for Best and
# $0.07-1.27 for the low-lactate example, more where more litres are filtered
# 2026-11-20 batch: every cost rose (bubble deaths, harvest loss, perfusion crew, membrane life 2,415 L/m2, medium preparation
# capital, utilities). The litres SET at a bound (bath, physical, practical, measured_flow) are per kilo of cells grown and did not
# move; the two zero-waste rows are explore()'s own litres, which are per kilo harvested since the batch (10.82 -> 12.00, 8.0 ->
# 8.87 for the all-favourable example; 16.23 -> 18.60, 8.007 -> 9.18 for the low-lactate example). The all-favourable example's tank is
# now 153 g/L, so the culture that leaves with its cells (6.5 L per kilo grown) is more than its three lowest bounds and they cost the same.
# 2026-11-20 final pass: costs_at now gives every row's litres per kilo HARVESTED, as explore reports them and as the costs are
# (the bound rows gave litres per kilo grown before), and explore raises a bound below the culture that leaves with the cells to
# that. The all-favourable example is now scenarios.all_favourable() (16 h doubling, 3 ng cells, Humbird's 5 mmol/L of ammonia and
# 50 of lactate, 155 g/L, $7.62): the culture that leaves with its cells (6.96 L per kilo harvested) is above its feed, flow and
# physical bounds, so those three rows are the same run. The low-lactate example's bounds per kilo grown did not move.
# 2026-11-21: both examples now run the recycled-oxygen column held thinner so its loop passes (all-favourable 219 g/L, low-lactate
# 168 g/L), so less culture leaves with the cells (all-favourable 4.6 L a kilo, against 6.5 at 155 g/L) and its bounds separate
# again; the building's power by floor and class and the floor's glucose lower every cost. Before: best bath (23.9996, 9.139),
# physical/practical/measured_flow (6.9638, 7.010), no_waste (8.6569, 7.232); central bath (27.8846, 38.552), physical (7.2215,
# 17.934), practical/measured_flow/no_waste_low_flow (8.8815, 19.545), no_waste (18.0031, 28.731).
# 2026-11-27 (the nitrogen and carbon balance): `nutrients` takes the floor's 0.232 kg of amino acids and the balance's glucose
# (Humbird's 0.26 kg before), so the salt-limited bath and the physical bounds need fewer litres; the cases' cells eat what their
# ammonia and lactate imply, so where the nutrients bind the cost rises. Before: best bath (24.5721, 8.471), physical/practical
# (6.1157, 6.209), measured_flow (5.1236, 6.078), no_waste (8.9758, 6.576); central bath (27.4844, 37.353), physical (6.9949,
# 16.903), practical/measured_flow (8.8815, 18.781), no_waste (18.0031, 27.945), no_waste_low_flow (8.8815, 18.781).
GOLDEN = {
    "best": {"bath": (23.2097, 8.361), "physical": (5.8387, 6.224), "practical": (5.8387, 6.224), "measured_flow": (5.1236, 6.130),
             "no_waste": (8.9758, 6.577), "no_waste_low_flow": (8.9758, 6.577)},
    "central": {"bath": (26.1265, 36.133), "physical": (6.7178, 16.765), "practical": (8.8815, 18.904),
                "measured_flow": (8.8815, 18.904), "no_waste": (18.0031, 27.946), "no_waste_low_flow": (8.8815, 18.782)},
}
# What sets each scenario's litres. 2026-11-20 (first batch): lactate for the all-favourable example, at 35 mmol/L. 2026-11-20 (final
# pass): ammonia again. The case now tolerates Humbird's 50 mmol/L of lactate and 5 of ammonia: its 0.054 mol of ammonia a kilo needs
# 10.80 L per kilo grown, its lactate 10.25. The low-lactate example is still set by ammonia (35). A correct consequence of the new case.
SET_BY = {"best": "ammonia", "central": "ammonia"}

def close(a, b, tol=2e-3):
    return abs(a - b) <= tol * max(1.0, abs(b))


def check() -> list:
    fails = []
    # nitrogen: 0.21 mol N per mol of dry mass x 13.6 mol per kg
    if not close(M.nitrogen_in(), 2.856, 1e-9):
        fails.append(f"nitrogen in a kg of cells {M.nitrogen_in():.4f}, expected 2.856")
    # no leak and no lactate: stoichiometry binds nothing; a leak sets litres in proportion
    b = M.bounds()
    if b["stoichiometric"] != 0.0:
        fails.append("the stoichiometric floor should be zero")
    if not close(M.bounds(leak=0.01)["terms"]["nitrogen"], 2 * M.bounds(leak=0.005)["terms"]["nitrogen"], 1e-9):
        fails.append("nitrogen litres should be proportional to the leak")
    # the model's own ammonia settings: Best 0.055 mol/kg is 13.75 L/kg and the low-lactate example 0.14 is 35 L/kg at the scenarios' 4 mM
    # 2026-11-19 audit batch: these were 11 and 28 L/kg at 5 mM. The scenarios' tolerance is now the input sc_nh3_limit (4).
    # The module's nitrogen term still divides by Humbird's 5 (pf_nh3_limit), which no scenario uses any more, so the check
    # rescales it to the scenarios' limit. (The module should read sc_nh3_limit; that is a change to its logic, left to the
    # author. No cost here depends on it: the default leak is zero.)
    to_scenarios = value("pf_nh3_limit") / value("sc_nh3_limit")
    if not close(value("sc_nh3_limit"), 4.0, 1e-12) or not close(S.always()["nh3_limit"], value("sc_nh3_limit"), 1e-12):
        fails.append("the scenarios' ammonia limit should be sc_nh3_limit, 4 mmol/L")
    for nh3, want in ((value("sc_nh3_engineered"), 13.75), (value("sc_nh3_selected"), 35.0)):
        leak = nh3 / M.nitrogen_in()
        if not close(M.bounds(leak=leak)["terms"]["nitrogen"] * to_scenarios, want, 1e-6):
            fails.append(f"ammonia {nh3} should need {want} L/kg at the scenarios' limit")
    # and that figure is explore's own ammonia term, which sets both scenarios' litres. 2026-11-20 final pass: each scenario at its
    # OWN ammonia limit (the all-favourable example takes Humbird's 5 mmol/L, the low-lactate example sc_nh3_limit's 4); the check
    # assumed 4 for both, which is why it failed for the all-favourable example (a stale check, not an inconsistency of min_litres)
    for key in M.SCENARIOS:
        kw = S.explore_kwargs(S.SCENARIOS[key].choice)
        r = fp.explore(**kw)
        to_own = value("pf_nh3_limit") / kw.get("nh3_limit", value("pf_nh3_limit"))
        # 2026-11-20: explore's terms are per kilo harvested; times the harvested share they are per kilo grown, as this module's
        if not close(M.bounds(leak=kw["nh3_kg"] / M.nitrogen_in())["terms"]["nitrogen"] * to_own,
                     r["medium_terms"]["ammonia"] * r["harvested_share"], 1e-9):
            fails.append(f"{key}: the nitrogen term at the scenario's ammonia and limit is not explore's ammonia term")
        if r["medium_set_by"] != SET_BY[key]:
            fails.append(f"{key}: {SET_BY[key]} should set the scenario's litres, not {r['medium_set_by']}")
    # 2026-11-19 audit batch: the glucose a cell making no lactate takes up, by the cells' own balance, is within 3% of the
    # feedstock count this module uses (1.74 against 1.78 mol for Best, 2.07 against 2.12 for the low-lactate example)
    for key in M.SCENARIOS:
        kw = S.explore_kwargs(S.SCENARIOS[key].choice)
        d, m = kw.get("doubling_h", 24.0), kw.get("mass_pg", 3000.0)
        g0 = fp.glucose_balance(fp.Cells(mass_pg=m, doubling_h=d).o2_per_kg * 1000.0 / 32.0, 0.0, 0.0, kw.get("fat_fed", 0.0))
        if not close(g0, M.nutrients(d, m)["n_glc"], 0.03):
            fails.append(f"{key}: glucose with no lactate {g0:.3f} mol is not within 3% of the feedstock count")
    for key in M.SCENARIOS:
        kw = S.explore_kwargs(S.SCENARIOS[key].choice)
        d, m = kw.get("doubling_h", 24.0), kw.get("mass_pg", 3000.0)
        t = M.bounds(d, m)
        # a concentrated feed beats a bath of the medium, and low salts beat typical salts
        if not t["terms"]["feed"] < t["terms"]["bath_low_salt"] < t["terms"]["bath"]:
            fails.append(f"{key}: feed < bath at low salts < bath at typical salts should hold")
        if not t["physical"] <= t["practical"] <= t["bath"]:
            fails.append(f"{key}: physical <= practical <= bath should hold")
        # the flow term is explore's own 'least flow' term at the measured low end
        r = fp.explore(**{**kw, "min_perfusion": REGISTRY["pf_min_perfusion"].lo})
        if not close(t["terms"]["flow"], r["medium_terms"]["least flow"] * r["harvested_share"], 1e-9):   # per kilo grown (2026-11-20)
            fails.append(f"{key}: flow term differs from explore's least flow")
        # the model's litres sit above the physical floor, and the waste that fits at the floor is small
        base = fp.explore(**kw)
        if not base["medium_l"] > t["physical"]:
            fails.append(f"{key}: the scenario's litres should exceed the physical floor")
        w = M.waste_allowed(t["physical"], d, m)
        if not (0 < w["nh3_share"] < 0.05 and 0 < w["lac_yield"] < 0.5):
            fails.append(f"{key}: waste allowed at the floor out of range: {w}")
        # the waste that fits at the floor is below what the scenario's cells make, on the scenarios' own basis for lactate
        # (mol per mol of all the glucose taken up)
        y_total = w["lac_kg"] / (M.nutrients(d, m)["n_glc"] + w["lac_kg"] / 2.0)
        own_nh3 = kw.get("nh3_limit", value("pf_nh3_limit")) / value("pf_nh3_limit")   # waste_allowed holds Humbird's 5 mmol/L
        if not (w["nh3_kg"] * own_nh3 < kw["nh3_kg"] and y_total < kw["lac_yield"]):
            fails.append(f"{key}: the floor litres should need less waste than the scenario's cells make")
        # the scenario's cost is not moved by this module, and fewer litres cost less
        c = M.costs_at(key)
        if not close(c["scenario"]["cost"], S.run(S.SCENARIOS[key].choice)["total"], 1e-12):
            fails.append(f"{key}: the scenario's own cost moved")
        if not c["physical"]["cost"] < c["scenario"]["cost"]:
            fails.append(f"{key}: the cost at the physical floor should be below the scenario's")
        for name, (litres, cost) in GOLDEN[key].items():
            if not close(c[name]["litres"], litres) or not close(c[name]["cost"], cost, 1e-3):
                fails.append(f"{key} {name}: {c[name]['litres']:.4f} L/kg ${c[name]['cost']:.3f} != pinned {litres} ${cost}")
    # a stronger feed needs fewer litres, in proportion
    if not close(M.bounds(feed_g_l=200.0)["terms"]["feed"] * 2.0, M.bounds(feed_g_l=100.0)["terms"]["feed"], 1e-9):
        fails.append("feed litres should halve when the feed doubles")
    # the energy cross-check: the model burns more ATP than a measured fibroblast, by less than a factor of 3
    e = M.energy_check()
    if not 1.0 < e["ratio"] < 3.0:
        fails.append(f"model ATP over Kilburn's should be 1-3, got {e['ratio']:.2f}")
    return fails


def test_min_litres():
    assert not check()


if __name__ == "__main__":
    fails = check()
    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("PASS — the least medium per kg: bounds, ordering and costs at the bounds match.")
