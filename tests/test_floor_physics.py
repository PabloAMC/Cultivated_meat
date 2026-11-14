#!/usr/bin/env python3
"""test_floor_physics.py — checks for the physics-based floor (floor_physics.py).

  * it reproduces Humbird's two published designs (the model's only calibration targets);
  * the physics behaves: smaller, slower cells need more oxygen per kg and cost more; density
    never exceeds the oxygen, viscosity or waste limits;
  * pinned numbers: the tier totals quoted in METHODS.md.

Run directly (no pytest needed):
    python tests/test_floor_physics.py
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))


def check() -> list:
    from inputs import value
    import floor_physics as fp

    fails = []

    def near(name, got, want, rel):
        if abs(got - want) > rel * abs(want):
            fails.append(f"{name}: want {want:.4g} (+-{rel:.0%}) got {got:.4g}")

    good, today = fp.GOOD_CELLS, fp.TODAY_CELLS

    # --- the model cell matches Humbird's: 60 pW, ~0.4 pmol O2 per cell per hour ---------------
    near("power of the 3 ng cell, pW", good.power_pw, 60.0, 0.01)
    near("O2 uptake per cell, pmol/h", good.qo2 * good.mass_pg * 1e-12 * 1e9, 0.447, 0.02)
    near("oxygen-limited density, g/L", fp.density(good, value("pf_otr_cap"), True), 195.0, 0.02)

    # --- Humbird's fed-batch design: 6.8 kt/yr from 480 m3; $11.32/kg of capital, maintenance and
    #     insurance; $14.5/kg of non-nutrient cost (Tables 4.6 and 4.7) -----------------------------
    fb = fp.plant_cost(good, "fedbatch", value("pf_capex_aseptic_fedbatch"), value("pf_consumables_fedbatch"))
    near("fed-batch output, t/m3/yr", fb["output"], 6800.0 / 480.0, 0.05)
    near("fed-batch capital charge, $/kg", fb["capital"], 7.00 + 1.92 + 2.40, 0.03)
    near("fed-batch plant cost, $/kg", fb["plant"], value("humbird_plant_cost"), 0.03)

    # --- Humbird's perfusion design: 6.9 kt/yr from 192 m3; $22.6/kg of capital, maintenance and
    #     insurance; $30.1/kg of non-nutrient cost (Tables 4.13 and 4.14) ---------------------------
    pf = fp.plant_cost(good, "perfusion", value("pf_capex_aseptic_perfusion"), value("pf_consumables_perfusion"))
    near("perfusion output, t/m3/yr", pf["output"], 6900.0 / 192.0, 0.05)
    near("perfusion capital charge, $/kg", pf["capital"], 13.97 + 3.84 + 4.79, 0.05)
    near("perfusion plant cost, $/kg", pf["plant"], 5.77 + 5.56 + 4.11 + 7.17 + 1.99 + 0.98 + 4.56, 0.05)

    # --- physics: small slow cells burn more oxygen per kg, and cost more in the same plant ------
    if not today.qo2 > good.qo2:
        fails.append("a smaller cell should take up more oxygen per gram")
    if not today.o2_per_kg > 3 * good.o2_per_kg:
        fails.append("today's cells (0.55 ng, 61 h) should burn over 3x the oxygen per kg")
    for mode in ("fedbatch", "continuous", "perfusion"):
        if not fp.output_per_m3(today, mode) < fp.output_per_m3(good, mode):
            fails.append(f"{mode}: today's cells should yield less per m3")
    for cells in (good, today):
        for otr in (13.0, 29.0, 50.0, 200.0):
            if fp.density(cells, otr, True) > value("pf_x_visc") + 1e-9:
                fails.append("density above the viscosity limit")
            if fp.density(cells, otr, False) > value("pf_x_unperfused") + 1e-9:
                fails.append("unperfused density above the waste limit")
    if not fp.capex_at_size(683.0, 50.0) < 683.0 < fp.capex_at_size(683.0, 5.0):
        fails.append("capital per m3 should fall with vessel size")

    # --- pinned tier totals ($/kg of real wet cells), quoted in METHODS.md -----------------------
    want = {"Humbird fed-batch, as designed": 19.3, "Humbird perfusion, as designed": 34.0,
            "Same fed-batch plant, today's cells": 35.8, "Aseptic, continuous harvest": 11.3,
            "Aseptic, continuous, 50 m3 tanks": 10.5, "Large perfusion, cheap retention": 9.0,
            "Food-fermentation-class plant": 4.7, "Physics limit": 2.7}
    got = {r["name"]: r["total"] for r in fp.tiers()}
    for name, w in want.items():
        if abs(got[name] - w) > 0.06:
            fails.append(f"tier '{name}': want {w} got {got[name]:.2f}")

    # --- the model's floor inputs ARE these tiers (inputs.py holds the numbers; this ties them) -----
    by = {r["name"]: r for r in fp.tiers()}
    near("plant_floor = aseptic continuous tier", value("plant_floor"), by["Aseptic, continuous harvest"]["plant"], 0.01)
    near("plant_floor_lo = food-fermentation tier", value("plant_floor_lo"), by["Food-fermentation-class plant"]["plant"], 0.03)
    near("plant_floor_hi = Humbird as designed", value("plant_floor_hi"), by["Humbird fed-batch, as designed"]["plant"], 0.01)

    print("physics floor: Humbird's two designs reproduced, physics checks and pinned tiers checked")
    return fails


def test_floor_physics():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL", f)
    print("PASS — the physics-based floor holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
