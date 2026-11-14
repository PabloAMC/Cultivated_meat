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

    # --- stress test: buffer in the cells, and the acid-side option -----------------------------------
    b = ge.suspension_buffer(190.0)
    near("note: suspension buffer at 190 g/L, mmol/L per pH", b, 2.4, 0.03)
    rb = ge.loop_design(190.0, sparge_velocity=us, buffer=b)
    near("note: CO2 per pass with the cells' buffer", rb["per_pass"], 1.71, 0.02)
    near("note: passes with the cells' buffer", rb["passes"], 7.4, 0.02)
    near("note: floor with loop and cells' buffer", ge.floor_with_loop(buffer=ge.suspension_buffer(189.0))["total"], 8.95, 0.02)
    one_run = value("pf_run_days") / value("pf_uptime") / 365.0
    near("note: silicone at $704, replaced each run", ge.floor_with_loop(cost_m2=704.0, life_y=one_run)["total"], 34.8, 0.02)
    near("note: silicone at $704, 2 years", ge.floor_with_loop(cost_m2=704.0)["total"], 11.0, 0.02)
    near("note: contactor at $160, 2 years", ge.floor_with_loop(cost_m2=160.0)["total"], 9.06, 0.02)
    near("note: more gas, 12.5 mm/s (0.2 vvm)", fp.explore(gas_velocity=0.0125)["total"], 8.47, 0.02)
    ac = ge.acid_side(190.0, 10.0)
    near("acid side: passes x per pass = load", ac["passes"] * ac["per_pass"], rb["co2_by_loop"], 1e-9)
    near("note: acid side, medium L/kg at 10 mmol/L", ac["medium_l"], 84.0, 0.02)
    near("note: acid side, extra medium $/kg", ac["extra_medium_cost"], 11.0, 0.02)
    near("note: electrodialysis filter area, m2", ac["ed_filter_m2"], 8660.0, 0.02)
    if not ge.acid_side(190.0, 2.0)["extra_medium_cost"] > 5.0:
        fails.append("even a little bought acid should cost more medium than the loop saves")

    # --- packed-column loop, headspace pressure, mixing (section 7 of the note) ------------------------
    film = ge.packing_film(189.0)
    near("note: film thickness at 189 g/L, mm", film["film_mm"], 0.336, 0.02)
    near("note: wall shear rate in the film, 1/s", film["shear_rate"], 1700.0, 0.03)
    near("note: HTU for CO2, m", film["htu_co2"], 0.265, 0.03)
    # Billet and Schultes' penetration form, kL = (2/sqrt(pi)) sqrt(D uL / (hL dh)), dh = 4 eps / ap, as a check
    dh = 4.0 * 0.98 / value("ge_pk_area")
    kl_bs = 2.0 / np.sqrt(np.pi) * np.sqrt(value("ge_d_co2") * film["uL"] / (film["holdup"] * dh))
    near("film kL agrees with Billet and Schultes' form within 15%", film["kl_co2"], kl_bs, 0.15)
    col = ge.column_design(189.0)
    near("column: passes x per pass = load", col["passes"] * col["per_pass"], col["co2_by_loop"], 1e-9)
    near("note: column CO2 per pass at 20 mbar out", col["per_pass"], 1.97, 0.02)
    near("note: column passes", col["passes"], 6.3, 0.02)
    near("note: column packing height, m", col["height_m"], 0.49, 0.03)
    near("note: column diameter, m", col["diameter_m"], 1.79, 0.03)
    near("note: column capital, $k/m3", col["capex_k_m3"], 26.2, 0.03)
    if not (col["gas_velocity"] < 0.1 and col["stay_s"] < 10.0):
        fails.append("column: sweep gas should be far below flooding and the film stay a few seconds")
    hp0, hp1 = ge.headspace_pressure(), ge.headspace_pressure(1.0)
    near("headspace at Humbird's pressure reproduces the model's oxygen limit", hp0["otr"], value("pf_otr_cap"), 1e-9)
    near("note: oxygen factor at 1 bar gauge", hp1["otr_factor"], 1.55, 0.02)
    near("note: pressure alone leaves the floor", fp.explore(p_top_barg=1.0)["total"],
         fp.explore()["total"], 1e-9)
    mx = ge.loop_mixing(189.0, col["passes"])
    near("note: the loop's jet barely helps mixing", mx["mix_x"], 1.06, 0.02)
    cases = (("note: floor, column at 6 mm/s", dict(), 8.60, "mixing"),
             ("note: floor, column + 1 bar gauge", dict(p_top_barg=1.0), 7.18, "thickness of the culture"),
             ("note: 2 mm/s, column for CO2 only", dict(sparge_velocity=0.002), 15.76, "oxygen supply"),
             ("note: 2 mm/s, column with oxygen sweep", dict(sparge_velocity=0.002, oxygen=True, sweep="o2_closed"), 8.99, "mixing"),
             ("note: 2 mm/s, column + oxygen + 1 bar", dict(sparge_velocity=0.002, oxygen=True, sweep="o2_closed", p_top_barg=1.0), 7.50,
              "thickness of the culture"),
             ("note: yeast-style plant, column + 1 bar", dict(oxygen=True, sweep="o2_closed", p_top_barg=1.0, plant="microbial"), 5.00,
              "thickness of the culture"))
    for name, kw, want, lim in cases:
        r = ge.floor_with_column(**kw)
        near(name, r["total"], want, 0.02)
        if r["limit"] != lim:
            fails.append(f"{name}: limit {r['limit']}, want {lim}")

    # --- section 8: stresses on the column, pH exposure, pressure -----------------------------------------
    st = ge.column_stresses(189.0)
    near("note: film dissipation at the wall, W/m3", st["film_dissipation_max"], 4000.0, 0.03)
    near("note: drop from 5 cm, W/m3", st["drop_dissipation"], 2.46e5, 0.03)
    near("note: fall height for 1e6 W/m3, m", ge.drop_height_for(1e6), 0.128, 0.03)
    near("note: bottom pressure today, bar abs", st["p_bottom_today"], 1.71, 0.01)
    near("note: bottom pressure at 1 bar gauge", st["p_bottom_new"], 2.38, 0.01)
    if not st["wall_shear_pa"] < 3400.0 * value("pf_medium_viscosity") * 1e-3:
        fails.append("the film's wall stress should be below what CHO took in Clincke's fibres (3,400/s)")
    hard, soft = ge.loop_ph_exposure(20.0, 1.0), ge.loop_ph_exposure(55.0, 0.5)
    near("note: hard design vs Paul's pH dose", hard["vs_paul"], 1.57, 0.02)
    near("note: gentle design vs Paul's pH dose", soft["vs_paul"], 0.29, 0.03)
    near("note: floor, gentle column", ge.floor_with_column(p_out=55.0)["total"], 8.62, 0.02)
    near("note: floor, gentle column + oxygen + 1 bar", ge.floor_with_column(p_out=55.0, oxygen=True, sweep="o2_closed",
         p_top_barg=1.0)["total"], 7.29, 0.02)
    near("note: same at 2 mm/s", ge.floor_with_column(p_out=55.0, sparge_velocity=0.002, oxygen=True, sweep="o2_closed",
         p_top_barg=1.0)["total"], 7.52, 0.02)

    # --- explore(): every cap, the liquid levers, the tricks as levers (the page mirrors these) -------------
    r0 = fp.explore()
    near("explore: default floor unchanged", r0["total"], 11.48, 0.001)
    near("explore: default medium unchanged", r0["medium_l"], 11.16, 1e-6)
    if set(r0["limits"]) != {"oxygen supply", "thickness of the culture", "mixing", "CO2 removal"} or r0["medium_set_by"] != "lactate":
        fails.append("explore: limits or medium terms missing at the floor")
    if abs(r0["limits"][r0["limit"]] - r0["density"]) > 1e-9 or min(r0["limits"].values()) != r0["density"]:
        fails.append("explore: the binding limit must be the smallest cap")
    ex = fp.explore(nh3_kg=value("pf_nh3_efficient"), lac_yield=0.5, glc_kg=value("pf_glc_kg"))
    near("explicit wastes at the enhanced cell reproduce the floor", ex["total"], r0["total"], 1e-9)
    near("pf_glc_kg times 0.5 is the enhanced lactate", 0.5 * value("pf_glc_kg"), value("pf_lac_efficient"), 1e-3)
    s0 = fp.explore(nh3_kg=0.70, sorbent=0.0)
    s8 = fp.explore(nh3_kg=0.70, sorbent=0.8)
    near("sorbent takes 80% of the ammonia term", s8["medium_terms"]["ammonia"], 0.2 * s0["medium_terms"]["ammonia"], 1e-9)
    near("sorbent cost: share x ammonia / capacity x price / uses",
         s8["consumables"] - s0["consumables"], 0.8 * 0.70 / value("pf_sorbent_q") * value("pf_sorbent_price"), 1e-9)
    if not ("salt" in s8["medium_terms"] and s8["osmolality"] > s0["osmolality"] - 50):
        fails.append("sorbent: the sodium it gives back must count as salt")
    near("note: ordinary bovine ammonia, L/kg", s0["medium_l"], 140.0, 1e-6)
    # (plant, loss per day, genetic engineering allowed, cell row, tank column, $/kg); 4 tank columns per cell row
    pins = [("sanitary", 0.0, True, 0, 0, 11.48), ("sanitary", 0.0, True, 0, 1, 9.91), ("sanitary", 0.0, True, 0, 2, 8.62),
            ("sanitary", 0.0, True, 0, 3, 7.29), ("sanitary", 0.0, True, 1, 0, 17.47), ("sanitary", 0.0, True, 1, 3, 13.13),
            ("sanitary", 0.0, True, 2, 0, 31.09), ("sanitary", 0.0, True, 2, 3, 26.89), ("sanitary", 0.002, True, 0, 0, 11.70),
            ("sanitary", 0.002, True, 0, 3, 7.40), ("microbial", 0.0, True, 0, 0, 6.61), ("microbial", 0.0, True, 0, 3, 5.02),
            ("microbial", 0.0, True, 1, 3, 9.08), ("microbial", 0.006, True, 0, 3, 5.17), ("microbial", 0.022, True, 0, 0, 7.66),
            ("microbial", 0.022, True, 0, 3, 5.58), ("microbial", 0.022, True, 1, 3, 10.32),
            ("sanitary", 0.0, False, 0, 0, 13.98), ("sanitary", 0.0, False, 0, 3, 9.79), ("sanitary", 0.002, False, 0, 3, 9.90),
            ("microbial", 0.0, False, 0, 3, 7.52), ("microbial", 0.022, False, 0, 3, 8.16)]
    tabs = {}
    for plant, hz, genetic, ci, tj, want in pins:
        tabs.setdefault((plant, hz, genetic), ge.cases_table(plant, hz, genetic=genetic))
        near(f"note: cases table {plant} loss {hz} genetic {genetic} cell {ci} tank {tj}",
             tabs[(plant, hz, genetic)][ci * 4 + tj][2], want, 0.002)
    if any(c[2] == ge.GE for k, c in ge.CELL_CASES.items() if k != "floor"):
        fails.append("only the floor's assumed cell should need genetic engineering")
    lr = ge.lactate_relief()
    near("note: lactate could supply this share of the energy", lr["share_of_energy"], 0.021, 0.03)

    # --- cell side: fat in the feed, the oxygen setpoint, gas per kg ------------------------------------------
    near("fat fed: RQ 1.204 -> 0.966", fp.explore(fat_fed=1.0)["rq"], 0.9659, 1e-3)
    near("note: fat fed, CO2 cap", fp.explore(fat_fed=1.0)["limits"]["CO2 removal"], 149.6, 0.005)
    near("lipid CO2 per O2 matches Humbird's Reactions 2.2 and 2.11", value("pf_rq_lipid"), 0.090 / 0.378, 1e-3)
    near("note: oxygen cap at 0.05 mmol/L", fp.explore(do_mmol=0.05)["limits"]["oxygen supply"], 234.7, 0.005)
    near("note: oxygen cap at 0.10 mmol/L", fp.explore(do_mmol=0.10)["limits"]["oxygen supply"], 225.8, 0.005)
    near("oxygen setpoint at the implied level changes nothing", fp.explore(
        do_mmol=ge.headspace_pressure()["c_liquid_implied"])["limits"]["oxygen supply"], r0["limits"]["oxygen supply"], 1e-9)
    near("note: oxygen per kg at 24 h, mol", r0["o2_kg"], 5.16, 0.005)
    near("upkeep + growth = oxygen per kg", r0["o2_kg_upkeep"] + r0["o2_kg_growth"], r0["o2_kg"], 1e-9)
    near("note: oxygen per kg at 48 h", fp.explore(doubling_h=48)["o2_kg"], 7.74, 0.005)
    near("CO2 per kg = RQ x oxygen", r0["co2_kg"], 1.204 * r0["o2_kg"], 1e-3)
    for cap, plant, want in ((0.001, "sanitary", 7.66), (0.002, "sanitary", 7.52), (0.006, "sanitary", 7.20),
                             (0.002, "microbial", 5.26), (0.006, "microbial", 4.91)):
        near(f"note: cheapest tricks at {cap * 1000:.0f} mm/s, {plant}", ge.cheapest_tricks(cap, plant)["total"], want, 0.002)

    # --- bubble damage goes with gas per litre: same velocity, shallower tank, more deaths -------------
    d0, d1 = ge.sparge_death(), ge.sparge_death(depth=fp.tank_shape(20.0, 0.8)[1])
    near("note: gas per litre at the floor, vvm", d0["vvm"], 0.096, 0.02)
    near("note: bubble deaths at the floor, share of growth", d0["share_of_growth"], 0.08, 0.03)
    near("note: bubble deaths in the squat tank", d1["share_of_growth"], 0.127, 0.03)
    near("deaths scale with 1/depth at a fixed velocity", d1["death_per_h"] / d0["death_per_h"],
         fp.tank_shape(20.0)[1] / fp.tank_shape(20.0, 0.8)[1], 1e-9)
    if not ge.sparge_death(protected=False)["share_of_growth"] > 1.0:
        fails.append("without protectant the model's gas flow should kill cells faster than they grow")

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
