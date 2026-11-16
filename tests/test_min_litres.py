#!/usr/bin/env python3
"""test_min_litres.py — the least medium per kg of cells that physics allows (min_litres.py)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _snapshot  # noqa: E402,F401  the note was computed before the protectant, antifoam and oxygen (tests/_snapshot.py)

import floor_physics as fp
import min_litres as M
import scenarios as S
from inputs import REGISTRY, value

# L/kg and $/kg at the bounds, per scenario (the scenarios' own costs are pinned in test_scenarios and test_golden)
GOLDEN = {
    "best": {"bath": (23.0745, 15.19), "physical": (5.7992, 6.94), "practical": (5.7992, 6.94), "measured_flow": (5.3395, 6.77),
             "no_waste": (10.8202, 8.82), "no_waste_low_flow": (8.0, 7.76)},
    "central": {"bath": (25.1232, 24.67), "physical": (6.4098, 12.28), "practical": (8.0, 13.05), "measured_flow": (8.0, 13.05),
                "no_waste": (16.2303, 18.56), "no_waste_low_flow": (8.0, 13.05)},
}


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
    # the model's own ammonia settings: Best 0.055 mol/kg is 11 L/kg and Central 0.14 is 28 L/kg at 5 mM
    for nh3, want in ((value("sc_nh3_engineered"), 11.0), (value("sc_nh3_selected"), 28.0)):
        leak = nh3 / M.nitrogen_in()
        if not close(M.bounds(leak=leak)["terms"]["nitrogen"], want, 1e-6):
            fails.append(f"ammonia {nh3} should need {want} L/kg")
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
        if not close(t["terms"]["flow"], r["medium_terms"]["least flow"], 1e-9):
            fails.append(f"{key}: flow term differs from explore's least flow")
        # the model's litres sit above the physical floor, and the waste that fits at the floor is small
        base = fp.explore(**kw)
        if not base["medium_l"] > t["physical"]:
            fails.append(f"{key}: the scenario's litres should exceed the physical floor")
        w = M.waste_allowed(t["physical"], d, m)
        if not (0 < w["nh3_share"] < 0.05 and 0 < w["lac_yield"] < 0.5):
            fails.append(f"{key}: waste allowed at the floor out of range: {w}")
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
