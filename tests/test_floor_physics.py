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
    import numpy as np
    from inputs import value
    import floor_physics as fp

    fails = []

    def near(name, got, want, rel):
        if abs(got - want) > rel * abs(want):
            fails.append(f"{name}: want {want:.4g} (+-{rel:.0%}) got {got:.4g}")

    good, small = fp.GOOD_CELLS, fp.PASITKA_CELLS

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
    pf = fp.plant_cost(good, "perfusion", value("pf_capex_aseptic_perfusion"), value("pf_consumables_perfusion"),
                       uptime=value("pf_uptime"), labour=value("pf_labour_perfusion"))
    near("perfusion output, t/m3/yr", pf["output"], 6900.0 / 192.0, 0.05)
    near("perfusion capital charge, $/kg", pf["capital"], 13.97 + 3.84 + 4.79, 0.05)
    near("perfusion plant cost, $/kg", pf["plant"], 5.77 + 5.56 + 4.11 + 7.17 + 1.99 + 0.98 + 4.56, 0.05)

    # --- physics: small slow cells burn more oxygen per kg, and cost more in the same plant ------
    if not small.qo2 > good.qo2:
        fails.append("a smaller cell should take up more oxygen per gram")
    if not small.o2_per_kg > 2.5 * good.o2_per_kg:
        fails.append("small slow cells (0.55 ng, 61 h) should burn over 2.5x the oxygen per kg")
    for mode in ("fedbatch", "filldraw", "perfusion"):
        if not fp.output_per_m3(small, mode) < fp.output_per_m3(good, mode):
            fails.append(f"{mode}: small slow cells should yield less per m3")
    for cells in (good, small):
        for otr in (13.0, 29.0, 50.0, 200.0):
            if fp.density(cells, otr, True) > value("pf_x_visc") + 1e-9:
                fails.append("density above the viscosity limit")
            if fp.density(cells, otr, False) > value("pf_x_unperfused") + 1e-9:
                fails.append("unperfused density above the waste limit")
    if not fp.capex_at_size(683.0, 50.0) < 683.0 < fp.capex_at_size(683.0, 5.0):
        fails.append("capital per m3 should fall with vessel size")

    # --- pinned tier totals ($/kg of real wet cells, 2025 prices), quoted in METHODS.md ----------
    want = {"Humbird fed-batch, as designed": 24.6, "Humbird perfusion, as designed": 45.5,
            "Same fed-batch plant, small slow cells": 48.4, "Pharma-style plant, half the density": 35.6,
            "Pharma-style plant, fill-and-draw": 19.4, "No clean rooms, fill-and-draw": 17.9,
            "No clean rooms, perfusion": 14.1, "Microbial-fermentation-class plant": 7.4, "Rough lower bound": 3.2}
    got = {r["name"]: r["total"] for r in fp.tiers()}
    for name, w in want.items():
        if abs(got[name] - w) > 0.06:
            fails.append(f"tier '{name}': want {w} got {got[name]:.2f}")

    # --- the model's floor inputs ARE these tiers (inputs.py holds the numbers; this ties them) -----
    by = {r["name"]: r for r in fp.tiers()}
    near("plant_floor = the floor tier", value("plant_floor"), by["No clean rooms, perfusion"]["plant_mature"], 0.01)
    near("plant_floor_lo = the frontier tier", value("plant_floor_lo"), by["Microbial-fermentation-class plant"]["plant_mature"], 0.01)
    # the mature-industry charge: capital recovery at 5.4% over 20 years, plus 4% maintenance and 5% insurance
    near("mature plant charge", value("plant_charge_mature"), 0.054 / (1 - 1.054 ** -20) + 0.09, 0.005)
    near("plant_floor_hi = the cautious tier", value("plant_floor_hi"), by["Pharma-style plant, fill-and-draw"]["plant"], 0.01)
    near("overhead range starts at the plant floor", __import__("inputs").prior("overhead")[1], value("plant_floor"), 1e-9)
    near("overhead range ends at the half-density tier", __import__("inputs").prior("overhead")[2],
         by["Pharma-style plant, half the density"]["plant"], 0.02)
    # the no-clean-room capital is Humbird's Table 4.2 hall (5,268 m2 on 2 levels) at the Sanitary rate of
    # his Table 3.2 ($1,980 per m2-level) in place of Class 8 ($3,760)
    near("no-clean-room capital, $k/m3 (2018)", value("pf_capex_no_cleanroom"),
         683.0 * (178.21 - 39.607 + 5268 * 2 * 1.980 / 1000.0) / 178.21, 0.005)
    # caps fall for cells that respire more per gram
    if not fp.waste_cap(small) < fp.waste_cap(good) == value("pf_x_unperfused"):
        fails.append("the waste-limited density should fall for cells that respire more per gram")
    # the page's lever controls: the defaults are the floor, and every species preset runs
    near("explore() defaults = the floor", fp.explore()["total"], by["No clean rooms, perfusion"]["total_mature"], 1e-3)
    for key, (_label, dh, mass, _med, _note) in fp.SPECIES_PRESETS.items():
        r = fp.explore(doubling_h=dh, mass_pg=mass)
        if not (0 < r["density"] <= value("pf_x_visc") and r["total"] > 0):
            fails.append(f"species preset {key}: implausible case {r}")
    # uncertainty on the floor: the point floor is the favourable end, so the median sits above it
    mc = fp.floor_mc()["total"]
    near("floor Monte Carlo median, $/kg", float(np.median(mc)), 18.6, 0.03)
    # premium-product analogues: the default over-predicts them; kappa = 9 fits far better
    from market_share import DemandParams, analogue_check
    e4, e9 = (analogue_check(DemandParams(cult_sub_mult=k))["rms_log_error"] for k in (4.0, 9.0))
    near("analogue misfit at the default kappa", e4, 1.84, 0.03)
    if not e9 < 0.6 * e4:
        fails.append("kappa = 9 should fit the premium-product analogues much better than kappa = 4")
    # medium use follows from waste: Humbird's enhanced cells need about 11 L/kg in perfusion, ordinary ones 190
    near("wash-out litres, enhanced cells", fp.washout_litres(good, 0.0), 11.2, 0.02)
    near("wash-out litres, ordinary cells", fp.washout_litres(good, 1.0), 190.0, 0.02)
    if not fp.explore(mode="filldraw", waste=0.25)["density"] < fp.explore(mode="filldraw")["density"]:
        fails.append("wasteful cells should be kept thinner in a drained-and-refilled tank")
    if not (np.percentile(mc, 15) > fp.explore()["total"]):
        fails.append("floor Monte Carlo: the point floor should sit near the bottom of the distribution")
    # contamination: more losses cost more; none reproduces the stated uptime
    near("uptime with no losses", fp.explore()["uptime"], value("pf_uptime"), 1e-9)
    if not (fp.explore(hazard=0.02, restart_fail_days=14)["total"] > fp.explore(hazard=0.002, restart_fail_days=14)["total"] > fp.explore()["total"]):
        fails.append("contamination should raise the cost")
    # medium can never cost less than what the cells must eat; a blend is cheaper per kg of product
    if fp.explore(medium_l=1.0, medium_price=0.1)["feedstock"] < fp.feedstock(good) - 1e-9:
        fails.append("medium cost fell below the feedstock floor")
    if not fp.explore(cell_share=0.5)["product"] < fp.explore()["product"]:
        fails.append("a blend should cost less per kg of product")
    # species costs and animals per tonne in the market model
    import meat_market as mm
    from cost_model import CostParams, cost_floor
    fl = cost_floor(CostParams())
    sm = mm.species_market(mm.MARKETS["us"])
    if not mm.penetration(sm, fl)[1] < mm.penetration(mm.MARKETS["us"], fl)[1]:
        fails.append("published cells should lower the share at the floor's plant")
    an = mm.animals_per_tonne_sold(mm.MARKETS["us"], fl)
    if not (0 < an["cultivated_mix"] < an["market_mix"]):
        fails.append("cultivated sales should spare fewer land animals per tonne than the market mix")
    # CO2 balance: reproduces the 120 g/L at 20 m3 and Humbird's fall with size (about 70 g/L at 200 m3)
    near("CO2-limited density at 20 m3", fp.co2_limited_density(good, 20.0), value("pf_x_co2_20m3"), 0.002)
    near("CO2-limited density at 200 m3", fp.co2_limited_density(good, 200.0), 70.0, 0.25)
    if not fp.co2_limited_density(good, 20.0, aspect=1.0) > fp.co2_limited_density(good, 20.0):
        fails.append("a squatter tank should hold a denser culture")
    # settling: single cells settle at centimetres per hour; clumps of a few cells settle several times faster
    st = fp.settler_spec()
    if not (1.0 < st["single_cell_cm_h"] < 15.0 and st["clump_um_needed"] > st["cell_um"]):
        fails.append(f"settler: implausible settling figures ({st})")
    # tornado: every factor has a row; at the floor the widest is the gas flow, and CO2 tolerance lowers the cost
    tor = {r[0]: r for r in fp.floor_tornado()}
    if len(tor) != len(fp.TORNADO) or fp.floor_tornado()[0][0] != "Gas flow the cells tolerate":
        fails.append("tornado: wrong rows or order")
    if any(len(t[6]) < 80 or "Evidence" not in t[6] for t in fp.TORNADO):
        fails.append("tornado: every factor needs an explanation that says how solid the evidence is")
    if not tor["CO\u2082 the cells tolerate"][2] < fp.explore()["total"]:
        fails.append("tornado: more CO2 tolerance should lower the cost")
    # culture temperature: the cells' own heat exceeds what warming the medium by 10 C needs
    tc = fp.temperature_check()
    if not (tc["metabolic_heat_kwh"] > tc["heating_10c_kwh"] and tc["heating_10c_usd_reported"] < 0.05):
        fails.append(f"temperature check: heating should be small against metabolic heat ({tc})")
    if not (value("plant_floor_lo") < value("plant_floor") < value("plant_floor_hi")):
        fails.append("floor inputs out of order: frontier < floor < cautious expected")

    # --- fill-and-draw delivers f/ln(1/(1-f)) of (cap x maximum growth rate): 0.72 at half draws ----
    import numpy as np
    f = value("pf_draw_fraction")
    ideal = value("pf_working_volume") * value("pf_x_unperfused") * good.mu * 8760 / 1000.0
    near("fill-and-draw output factor", fp.output_per_m3(good, "filldraw", uptime=1.0) / ideal, f / np.log(1 / (1 - f)), 1e-6)
    if not fp.output_per_m3(good, "filldraw", uptime=1.0) < ideal:
        fails.append("fill-and-draw cannot beat the density cap times the maximum growth rate")

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
