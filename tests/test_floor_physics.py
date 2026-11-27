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
    # repinned 2026-11-19: nutrient floor $1.70 -> $2.00 (+$0.30 in every tier); the rough lower bound's cheap amino acids
    # ($1/kg) now multiply 0.232 kg of amino acids instead of 0.337 kg of hydrolysate (-$0.105)
    # repinned 2026-11-20 (the two perfusion tiers that are explore(): bubble deaths, the 2% harvest loss, twice the fed-batch
    # crew in perfusion, medium preparation capital and utilities in four parts; 15.14 -> 18.76 and 8.82 -> 11.75. Humbird's own
    # designs and the fill-and-draw tiers are plant_cost() and do not move)
    # 2026-11-20, third pass: what each tank brings with it is charged per tank (floor_physics.tank_items: a 20 m3 perfusion
    # tank against the 20 m3 fed-batch reference), and plant_floor follows: no clean rooms, perfusion 18.76 -> 18.63
    # 2026-11-21: the three fill-and-draw tiers are explore() itself (they were plant_cost(), which skipped the waste build-up, the
    # least medium flow, bubble deaths and the harvest loss): half density 35.91 -> 39.77, fill-and-draw 19.71 -> 22.54, without
    # clean rooms 18.19 -> 20.47; the building's power follows its floor and class: perfusion 18.63 -> 18.42, microbial-class
    # 11.75 -> 11.48
    want = {"Humbird fed-batch, as designed": 24.9, "Humbird perfusion, as designed": 45.78,
            "Same fed-batch plant, small slow cells": 48.7, "Pharma-style plant, half the density": 39.77,
            "Pharma-style plant, fill-and-draw": 22.54, "No clean rooms, fill-and-draw": 20.47,
            "No clean rooms, perfusion": 18.42, "Microbial-fermentation-class plant": 11.48, "Rough lower bound": 3.08}
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
    # the perfusion tiers ARE explore() (since 2026-11-15, late): the filter loop, the protectant and the oxygen
    near("explore() = the floor tier", fp.explore()["total"], by["No clean rooms, perfusion"]["total_mature"], 1e-9)
    near("explore(plant='microbial') = the frontier tier", fp.explore(plant="microbial")["total"],
         by["Microbial-fermentation-class plant"]["total_mature"], 1e-9)
    near("explore() defaults, with the TFF loop, protectant and antifoam", fp.explore()["total"], 15.774, 1e-3)   # 15.721 before the nitrogen and carbon balance (2026-11-27); 12.81 before the 2026-11-20 batch; 16.025 before tank_items (third pass); 15.929 before the building's power followed its floor and class (2026-11-21)
    for key, (_label, dh, mass, _med, pco2, rng, extra, _note) in fp.SPECIES_PRESETS.items():
        r = fp.explore(doubling_h=dh, mass_pg=mass, pco2_mbar=pco2, **(extra or {}))
        if not (rng[0] <= (value("pf_pco2_limit") if pco2 is None else pco2) <= rng[1]):
            fails.append(f"species preset {key}: CO2 tolerance outside its own range")
        if not (0 < r["density"] <= value("pf_x_visc") and r["total"] > 0):
            fails.append(f"species preset {key}: implausible case {r}")
    # uncertainty on the floor: the point floor is the favourable end, so the median sits above it
    mc = fp.floor_mc()["total"]
    near("floor Monte Carlo median, $/kg", float(np.median(mc)), 36.64, 0.03)   # 27.5 before the 2026-11-20 batch
    # premium-product analogues: the default over-predicts them; kappa = 9 fits far better
    from market_share import DemandParams, analogue_check
    e4, e9 = (analogue_check(DemandParams(cult_sub_mult=k))["rms_log_error"] for k in (4.0, 9.0))
    # 2026-11-21 (fourth batch): 1.87 -> 1.92 (pinned 1.84; plant-based meat's committed buyers re-solve the mainstream weights)
    near("analogue misfit at the default kappa", e4, 1.92, 0.03)
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
    # sparge gas: the floor is unchanged by the gas term; while CO2 binds the oxygen fed per kg of cells grown does not depend
    # on the gas velocity; less gas per litre is credited and more is charged
    base = fp.explore()
    near("oxygen fed, kg per m3 of liquid per hour", fp.oxygen_fed(), 8.59, 0.005)
    if abs(base["gas_extra"]) > 1e-12:
        fails.append("gas: the floor case must carry no gas adjustment")
    near("gas cost per kg at the floor", base["gas"], 0.58, 0.02)   # 0.52 per kilo grown / 0.90 harvested (2026-11-20)
    lo_gas, hi_gas = fp.explore(gas_velocity=0.002), fp.explore(gas_velocity=0.009)
    # 2026-11-20: bubble deaths rise with the gas passed and every cost is per kilo harvested, so the statement that holds is
    # per kilo GROWN (gas x harvested share); per kilo harvested the gas cost rises with the gas velocity
    # 2026-11-20, third pass: since a thick culture takes up oxygen more slowly (viscous_kla, tc_kla_exp), the default 0.006 m/s
    # sits at the switch: above it the oxygen supply binds (157 g/L at 0.009 against CO2's 180), so the gas passed buys fewer
    # kilos and gas per kilo grown rises. The statement holds where CO2 binds: below the default, and at 0.009 with medium's kLa
    grown = [r["gas"] * r["harvested_share"] for r in (lo_gas, base)]
    hi_thin = fp.explore(gas_velocity=0.009, viscous_kla=False)
    if (lo_gas["limit"] != "CO2 removal" or base["limit"] != "CO2 removal" or hi_thin["limit"] != "CO2 removal"
            or abs(grown[0] - grown[1]) > 1e-9 or abs(hi_thin["gas"] * hi_thin["harvested_share"] - grown[1]) > 1e-9):
        fails.append("gas: while CO2 binds, gas per kg of cells grown should not depend on the gas velocity")
    if not (hi_gas["limit"] == "oxygen supply" and hi_gas["gas"] * hi_gas["harvested_share"] > grown[1] + 1e-6):
        fails.append("gas: at 0.009 m/s the thick culture's oxygen supply should bind, so gas per kg grown should rise")
    if not (lo_gas["gas"] < base["gas"] < hi_gas["gas"] and lo_gas["death_share"] < base["death_share"] < hi_gas["death_share"]):
        fails.append("gas: more gas should kill more cells, so gas per kg harvested should rise with the gas velocity")
    if not (lo_gas["gas_extra"] < 0 < hi_gas["gas_extra"] and fp.explore(aspect=1.0)["gas_extra"] > 0
            and fp.explore(vessel_m3=200.0)["gas_extra"] < 0):
        fails.append("gas: wrong sign of the oxygen-plant adjustment")
    # settling: single cells settle at centimetres per hour; clumps of a few cells settle several times faster
    st = fp.settler_spec()
    if not (1.0 < st["single_cell_cm_h"] < 15.0 and st["clump_um_needed"] > st["cell_um"]):
        fails.append(f"settler: implausible settling figures ({st})")
    # tornado: every factor has a row; at the floor the widest is the waste the cells make (more medium, more permeate
    # through the membranes), and CO2 tolerance lowers the cost
    tor = {r[0]: r for r in fp.floor_tornado()}
    if len(tor) != len(fp.TORNADO) or fp.floor_tornado()[0][0] != "Waste the cells make":
        fails.append("tornado: wrong rows or order")
    if any(len(t[6]) < 80 or "Evidence" not in t[6] for t in fp.TORNADO):
        fails.append("tornado: every factor needs an explanation that says how solid the evidence is")
    if not tor["CO\u2082 the cells tolerate"][2] < fp.explore()["total"]:
        fails.append("tornado: more CO2 tolerance should lower the cost")
    # species CO2 tolerance: fish at 50 mbar cost more than at the default; the tornado takes a species' range
    if not fp.explore(doubling_h=24, mass_pg=2500, pco2_mbar=50)["total"] > 1.5 * fp.explore(doubling_h=24, mass_pg=2500)["total"]:
        fails.append("fish at 50 mbar should cost well above fish at 100 mbar")
    row = {r[0]: r for r in fp.floor_tornado(pco2_range=(10.0, 100.0), pco2_mbar=50.0)}["CO\u2082 the cells tolerate"]
    if not (row[1] > row[2] and row[3] == "10 mbar"):
        fails.append("tornado: the species CO2 range was not applied")
    # the working plant (Vow): the reconstruction lands on its implied density and inside its stated output range
    _l, dh, mass, _m, pco2, _r, extra, _n = fp.SPECIES_PRESETS["vow"]
    vow = fp.explore(doubling_h=dh, mass_pg=mass, pco2_mbar=pco2, **extra)
    near("Vow reconstruction, density g/L", vow["density"], 27.0, 0.05)
    if not (3.0 < vow["output"] < 6.5):
        fails.append(f"Vow reconstruction: output {vow['output']:.1f} t/m3/yr outside its stated range")
    # back-test: the model allows the densities reported and gives less medium than real runs used
    bt = {(r[0], r[1]): r for r in fp.backtest()}
    if len(bt) != 8:
        fails.append("back-test: expected eight rows")
    sm = bt[("Chicken, 10 L perfusion (SuperMeat 2024)", "medium, L per kg of cells")]
    if not (1.2 < sm[2] / sm[3] < 1.7):
        fails.append(f"back-test: SuperMeat medium ratio moved ({sm[2] / sm[3]:.2f})")
    # drained-and-refilled tanks: the waste they hold caps the density; growth factors scale with medium. 2026-11-21: the least
    # medium flow's cap is now times pf_batch_end_x, as the other wastes' are (92 -> 120 g/L), so ammonia and lactate set it at
    # 116 g/L (the check was "the medium-flow cap near 92 g/L")
    fd = fp.explore(mode="filldraw")
    if not (fd["limit"] == "waste build-up" and 110 < fd["density"] < 120
            and abs(fd["limits"]["other by-products"] - value("pf_batch_end_x") * 1000.0 * 0.693 / value("pf_min_perfusion")) < 1.0):
        fails.append(f"fill-and-draw: expected the waste cap near 116 g/L and the least-flow cap at 1.3 x 92, got {fd['density']:.0f} ({fd['limit']})")
    if not fp.explore(growth_factors=True, waste=0.1)["growth_factors"] > 2 * fp.explore(growth_factors=True)["growth_factors"]:
        fails.append("growth factors should scale with the litres of medium")
    # cost and demand together: the median share is well below the point floor share
    js = mm.floor_share_mc("global", 400)
    if not (0.01 < float(np.median(js["vol"])) < 3.0):   # lower bound 0.2 -> 0.05 (shop margin) -> 0.01 (premium markets sized), 2026-11-18
        fails.append(f"joint uncertainty: world median share {float(np.median(js['vol'])):.2f}% out of range")
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
