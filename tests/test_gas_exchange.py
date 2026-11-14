#!/usr/bin/env python3
"""test_gas_exchange.py — checks for the gas-exchange side study (gas_exchange.py).

  * the loop's balances close: passes x amount per pass = load; area x flux = load;
  * it agrees with the floor model: at the floor's own density and gas flow the loop has nothing to do,
    and the reference tank shape changes nothing;
  * the physics behaves: longer fibres exchange more, buffer raises what a pass carries, squat tanks
    cost more steel and floor, the per-litre gas rule makes the CO2 limit independent of shape;
  * pinned numbers: the ones quoted in research_notes/gas_exchange_study.md.

Run directly (no pytest needed):
    python tests/test_gas_exchange.py
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
    import gas_exchange as ge

    fails = []

    def near(name, got, want, rel):
        if abs(got - want) > rel * abs(want):
            fails.append(f"{name}: want {want:.4g} (+-{rel:.0%}) got {got:.4g}")

    us = value("pf_gas_velocity")

    # --- loads, and what a litre carries ---------------------------------------------------------
    co2, o2 = ge.gas_load(120.0)
    near("CO2 made at 120 g/L, mmol/L/h", co2, 21.5, 0.01)
    near("O2 used at 120 g/L, mmol/L/h", o2, 17.9, 0.01)
    amount, dph = ge.co2_per_pass(100.0, 50.0, buffer=0.0)
    near("CO2 per pass, 100 -> 50 mbar, no buffer", amount, value("pf_co2_henry") * 50.0, 1e-9)
    near("pH rise, 100 -> 50 mbar, no buffer", dph, np.log10(2.0), 1e-9)
    buffered, dph_b = ge.co2_per_pass(100.0, 50.0, buffer=5.0)
    if not (buffered > 2.0 * amount and dph_b < dph):
        fails.append("buffer should more than double the CO2 a pass carries here, and damp the pH rise")
    near("viscosity at the model's thickness limit, x medium", ge.viscosity(value("pf_x_visc")) / 0.75e-3, 2.4, 0.05)

    # --- one fibre --------------------------------------------------------------------------------
    d, v = 0.5e-3, 0.0625
    if not ge.exchanged_fraction(0.2, d, v, "co2") < ge.exchanged_fraction(0.4, d, v, "co2") < 1.0:
        fails.append("a longer fibre should exchange more, and never all")
    L = ge.fibre_length(0.5, d, v)
    near("fibre_length inverts exchanged_fraction", ge.exchanged_fraction(L, d, v, "co2"), 0.5, 1e-6)
    if not ge.fibre_length(0.5, d, v, wall_um=0.0) < L:
        fails.append("a wall with no resistance needs a shorter fibre")

    # --- the loop's balances ----------------------------------------------------------------------
    for kw in (dict(sparge_velocity=us), dict(sparge_velocity=0.0), dict(oxygen=True), dict(oxygen=True, o2_bar=2.0)):
        r = ge.loop_design(190.0, **kw)
        near(f"flux x area = CO2 taken by the loop {kw}", r["flux_co2"] * r["area_m2_m3"] / 1000.0, r["co2_by_loop"], 1e-9)
        if kw.get("oxygen"):
            near(f"loop supplies all the oxygen {kw}", r["o2_share"], 1.0, 1e-9)
            if not r["passes"] * r["per_pass"] >= r["co2_by_loop"] - 1e-9:
                fails.append("a loop sized for oxygen must still carry the CO2")
        else:
            near(f"passes x per pass = load {kw}", r["passes"] * r["per_pass"], r["co2_by_loop"], 1e-9)
    # at the floor's density and gas flow the sparger alone removes the CO2 (the model's 120 g/L)
    x_floor = fp.co2_limited_density(fp.GOOD_CELLS)
    near("loop has nothing to do at the floor", ge.loop_design(x_floor, sparge_velocity=us)["passes"] + 1.0, 1.0, 1e-6)
    a, b = ge.loop_design(150.0), ge.loop_design(250.0)
    near("with no sparger, area scales with density", b["area_m2_m3"] / a["area_m2_m3"], 250.0 / 150.0, 1e-9)

    # --- the floor with a loop ---------------------------------------------------------------------
    f = ge.floor_with_loop()
    near("floor_with_loop starts from the floor", f["base"], fp.explore()["total"], 1e-9)
    if not f["no_co2_limit"] < f["total"] < f["base"]:
        fails.append("at the default membrane price a CO2 loop should pay for itself at the floor, but not be free")
    if f["limit"] == "CO2 removal":
        fails.append("with the loop, CO2 removal should no longer bind")
    if not ge.floor_with_loop(cost_m2=value("ge_cost_m2") * 7.4)["total"] > f["base"]:
        fails.append("at pharma-filter prices the loop should cost more than it saves")

    # --- tank shape ----------------------------------------------------------------------------------
    ref = ge.shape_case(value("pf_aspect"))
    near("reference shape: no change in plant cost", ref["capex_x"], 1.0, 1e-9)
    near("reference shape reproduces the floor", ref["total"], fp.explore()["total"], 1e-9)
    squat = ge.shape_capex_factor(20.0, 0.8)
    if not (squat["shell"] > 1.0 and squat["floor"] > 1.0 and squat["plant"] < 1.2):
        fails.append("a squat tank should need more steel and floor, by under 20% of the plant")
    for a_ in (0.5, 1.0, 1.6):
        r = ge.shape_case(a_, gas_rule="volume", with_vessel_cost=False)
        near(f"per-litre gas rule: same gas per litre at depth/width {a_}", r["vvm"], us * 60.0 / fp.tank_shape(20.0)[1], 1e-9)
        if r["limit"] == "CO2 removal":
            near(f"per-litre gas rule: CO2 limit unchanged at {a_}", r["density"], x_floor, 1e-9)
    if not ge.best_shape()["aspect"] < 1.0 < ge.best_shape(gas_rule="volume")["aspect"]:
        fails.append("the cheapest shape should be squat under the velocity rule and not under the per-litre rule")

    # --- airlift --------------------------------------------------------------------------------------
    al = ge.airlift_check()
    for tag in ("paper", "model"):
        r = al[tag]
        near(f"airlift balance closes ({tag})", ge.co2_density_at(al["depth"], r["gas_velocity"], r["qo2"], 1.2), 100.0, 1e-9)
        if not r["gas_velocity"] > us:
            fails.append(f"airlift ({tag}): 100 g/L should need more than the model's gas limit")

    # --- numbers quoted in research_notes/gas_exchange_study.md ----------------------------------------
    r = ge.loop_design(190.0, sparge_velocity=us)
    for name, got, want in (
            ("note: passes/h, CO2 loop at 190 g/L", r["passes"], 11.3), ("note: m2 per m3 of culture", r["area_m2_m3"], 156.0),
            ("note: flux, mmol/m2/h", r["flux_co2"], 80.0), ("note: loop capital, $k/m3", r["capex_k_m3"], 78.0),
            ("note: floor with CO2 loop", f["total"], 9.2), ("note: floor, CO2 limit gone", f["no_co2_limit"], 8.5),
            ("note: floor, no sparging", ge.floor_with_loop(oxygen=True)["total"], 11.6),
            ("note: 2 mm/s cells, CO2 loop", ge.floor_with_loop(gas_velocity=0.002)["total"], 16.5),
            ("note: fish cells, CO2 loop", ge.floor_with_loop(pco2_mbar=50.0, mass_pg=2500.0)["total"], 12.0),
            ("note: cheapest shape, $/kg", ge.best_shape()["total"], 8.69), ("note: cheapest shape", ge.best_shape()["aspect"], 0.75),
            ("note: squat tank 0.8, $/kg", ge.shape_case(0.8)["total"], 8.8),
            ("note: 200 m3 in ten compartments", ge.shape_case(0.8, 200.0, cells_in_shell=10)["total"], 8.05),
            ("note: airlift gas, paper, mm/s", al["paper"]["gas_velocity"] * 1000.0, 9.7),
            ("note: airlift gas, model, mm/s", al["model"]["gas_velocity"] * 1000.0, 14.0),
            ("note: airlift density at 6 mm/s, paper", al["paper"]["density_at_limit"], 62.0),
            ("note: airlift density at 6 mm/s, model", al["model"]["density_at_limit"], 43.0)):
        near(name, got, want, 0.02)

    print("gas exchange: balances close, floor and shape tie to floor_physics, pinned note numbers checked")
    return fails


def test_gas_exchange():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL", f)
    print("PASS — the gas-exchange side study holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
