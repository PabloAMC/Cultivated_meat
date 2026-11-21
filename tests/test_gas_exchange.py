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
    """The study's note quotes figures computed with the model as it was on 2026-11-14: the old hoped-for retention device
    (rt_tff_default = 0), no bubble protectant, no antifoam effect, no oxygen bought by the yeast-style plant. The checks
    run with those settings (floor_physics.BEFORE_FILTER_LOOP). Repinned 2026-11-19 for the $2.00 nutrient floor: +$0.30 where the
    floor binds, less where $0.15 a litre of medium already covered part of it (2 mm/s cells, fish cells).

    Repinned 2026-11-20 (model batch). Those settings no longer reproduce the 2026-11-14 model, because floor_physics.explore now
    charges, whatever the settings: the cells bursting bubbles kill (8% of the cells grown at the floor's 6 mm/s, at the
    protected kill rate even though these settings buy no protectant), a 2% harvest loss, twice the fed-batch crew in a washed
    continuous tank, utilities in four parts, growth factors by the litre and medium preparation capital with the medium
    passed. Every cost and every litre is per kilo harvested. The floor on these settings is $14.15, not $11.78, and its
    medium 12.38 L per kilo harvested (11.16 per kilo grown, as before). Every pin below that is a cost moved, by 5% to 54%.
    Three things changed in kind, not only in size (each is a consequence of charging bubble deaths, none a defect):
      * with the column and pressure, how much gas the cells tolerate no longer matters: the cheapest tricks cost $8.56, $8.53
        and $8.56 at 1, 2 and 6 mm/s (they cost $7.96, $7.83 and $7.50), because the gas the cells are spared also spares them;
      * more gas is worth less: 12.5 mm/s takes the floor from $14.15 to $10.87 (23%; it was 26%) with 13% of the cells killed;
      * a squat tank passes more gas per litre and kills more cells (11% at depth = width, 8% in the tall tank), so shape is
        worth less: depth = width saves 15% of the floor (it saved 17%).
    FINAL MODEL (2026-11-20, later the same day). One more change in kind: a thick culture now takes up oxygen more slowly
    (floor_physics.explore's viscous_kla, on by default; exponent tc_kla_exp). The oxygen a sparger passes falls as the
    culture thickens, so the oxygen cap at the floor's setpoint is 153 g/L, not 226. That one change explains every repin
    below that is not a few cents: (1) the column alone, or with 1 bar, now stops at 153 g/L held by oxygen (it reached the
    mixing limit at 189 g/L, or the thickness limit with 1 bar), so it makes 5.3 passes an hour, not 11.1, and the culture
    sees under half of the safe alkaline dose; (2) the cheapest tank shape is 1.1 times as deep as wide, not 0.75: once the
    shape lifts the CO2 limit above 153 g/L oxygen binds whatever the shape, and a squatter tank only adds steel and bubble
    deaths; (3) with every trick allowed the gas the cells tolerate matters again ($8.49 at 2 mm/s, $8.72 at 6 mm/s): the
    thickness binds in each, and the faster gas kills 8% of the cells grown against 2.7%. The other engine fixes of the day
    lowered the floor from $14.15 to $14.05.
    Two side calculations in gas_exchange.py were put back on their own basis the same day: lactate_relief takes the litres per
    kilo grown (its ATP is per kilo grown), and floor_with_loop's no-sparger case sets the bubble kill to zero (it lifts the
    oxygen limit with a 1 m/s gas velocity, which explore would otherwise charge as bubbles)."""
    import retention
    import floor_physics
    with retention._with(floor_physics.BEFORE_FILTER_LOOP):
        return _check()


def _check() -> list:
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
    # 2026-11-20 final model: was "squat (under 1.0) under the velocity rule". With viscous_kla the oxygen cap (153 g/L)
    # binds once the shape lifts the CO2 limit, so the cheapest shape is the tallest that does that (1.1), still less tall
    # than the reference 1.6 under the velocity rule, and taller than it under the per-litre rule.
    bs = ge.best_shape()
    if not (bs["aspect"] < value("pf_aspect") < ge.best_shape(gas_rule="volume")["aspect"] and bs["limit"] == "oxygen supply"):
        fails.append("the cheapest shape should be less tall than the reference, held by oxygen, under the velocity rule, and "
                     "taller under the per-litre rule")

    # --- stress test: buffer in the cells, and the acid-side option -----------------------------------
    b = ge.suspension_buffer(190.0)
    near("note: suspension buffer at 190 g/L, mmol/L per pH", b, 2.4, 0.03)
    rb = ge.loop_design(190.0, sparge_velocity=us, buffer=b)
    near("note: CO2 per pass with the cells' buffer", rb["per_pass"], 1.71, 0.02)
    near("note: passes with the cells' buffer", rb["passes"], 7.4, 0.02)
    near("note: floor with loop and cells' buffer", ge.floor_with_loop(buffer=ge.suspension_buffer(189.0))["total"], 12.12, 0.02)   # 10.80 before the final model
    one_run = value("pf_run_days") / value("pf_uptime") / 365.0
    near("note: silicone at $704, replaced each run", ge.floor_with_loop(cost_m2=704.0, life_y=one_run)["total"], 27.47, 0.02)   # 36.73
    near("note: silicone at $704, 2 years", ge.floor_with_loop(cost_m2=704.0)["total"], 13.41, 0.02)   # 12.98
    near("note: contactor at $160, 2 years", ge.floor_with_loop(cost_m2=160.0)["total"], 12.19, 0.02)   # 10.92
    near("note: more gas, 12.5 mm/s (0.2 vvm)", fp.explore(gas_velocity=0.0125)["total"], 10.87, 0.02)
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
    col = ge.column_design(189.0, p_out=20.0)        # section 7's first design (the default is now 55)
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
    # 2026-11-20: 8.90 / 7.48 / 16.06 / 9.29 / 7.80 / 5.30 before the batch; final model: the first three 10.44 -> 11.96
    # (mixing -> oxygen supply), 8.54 -> 9.63 (thickness -> oxygen supply), 18.53 -> 20.25 (viscous_kla)
    cases = (("note: floor, column at 6 mm/s", dict(), 11.96, "oxygen supply"),
             ("note: floor, column + 1 bar gauge", dict(p_top_barg=1.0), 9.63, "oxygen supply"),
             ("note: 2 mm/s, column for CO2 only", dict(sparge_velocity=0.002), 20.25, "oxygen supply"),
             ("note: 2 mm/s, column with oxygen sweep", dict(sparge_velocity=0.002, oxygen=True, sweep="o2_closed"), 10.30, "mixing"),
             ("note: 2 mm/s, column + oxygen + 1 bar", dict(sparge_velocity=0.002, oxygen=True, sweep="o2_closed", p_top_barg=1.0), 8.51,
              "thickness of the culture"),
             ("note: yeast-style plant, column + 1 bar", dict(oxygen=True, sweep="o2_closed", p_top_barg=1.0, plant="microbial"), 6.23,
              "thickness of the culture"))
    for name, kw, want, lim in cases:
        r = ge.floor_with_column(p_out=20.0, **kw)
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
    near("note: floor, gentle column", ge.floor_with_column(p_out=55.0)["total"], 11.98, 0.02)   # 10.47
    near("note: floor, gentle column + oxygen + 1 bar", ge.floor_with_column(p_out=55.0, oxygen=True, sweep="o2_closed",
         p_top_barg=1.0)["total"], 8.77, 0.02)
    near("note: same at 2 mm/s", ge.floor_with_column(p_out=55.0, sparge_velocity=0.002, oxygen=True, sweep="o2_closed",
         p_top_barg=1.0)["total"], 8.53, 0.02)

    # --- explore(): every cap, the liquid levers, the tricks as levers (the page mirrors these) -------------
    r0 = fp.explore()
    near("explore: default floor", r0["total"], 14.052, 0.001)            # 11.78 before 2026-11-20; 14.148 before the final model
    # the litres per kilo grown are what they were (11.16); explore reports them per kilo harvested (12.38)
    near("explore: default medium, per kilo grown, unchanged", r0["medium_l"] * r0["harvested_share"], 11.16, 1e-6)
    near("explore: default medium, per kilo harvested", r0["medium_l"], 12.379, 1e-4)
    near("explore: at the floor's 6 mm/s the bubbles kill 8% of the cells grown", r0["death_share"], 0.0801, 2e-3)
    near("harvested share = (1 - bubble deaths) x harvest recovery", r0["harvested_share"],
         (1.0 - r0["death_share"]) * value("pf_harvest_recovery"), 1e-9)
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
    near("sorbent cost: share x ammonia / capacity x price / uses, per kilo harvested",
         s8["consumables"] - s0["consumables"],
         0.8 * 0.70 / value("pf_sorbent_q") * value("pf_sorbent_price") / s8["harvested_share"], 1e-9)
    if not ("salt" in s8["medium_terms"] and s8["osmolality"] > s0["osmolality"] - 50):
        fails.append("sorbent: the sodium it gives back must count as salt")
    near("note: ordinary bovine ammonia, L per kilo grown", s0["medium_l"] * s0["harvested_share"], 140.0, 1e-6)
    near("ordinary bovine ammonia, L per kilo harvested", s0["medium_l"], 155.29, 1e-4)
    # (plant, loss per day, genetic engineering allowed, cell row, tank column, $/kg); 4 tank columns per cell row
    # 2026-11-19 audit batch, second round: the three cell cases that are not the floor's take glucose from the cells' own
    # balance (CELL_CASES, glc_balance=True) in place of 0.84 / 1.116 mol a kilo. "Best shown in meat cells" (cell row 1)
    # then takes up 4.3 mol and lactate sets its medium at 89.8 L/kg, not ammonia at 28: on these 2026-11-14 settings
    # 17.47 -> 26.74 (sparger), 13.13 -> 22.39 (every trick), yeast-style 9.08 -> 18.34 and 10.32 -> 20.14. The fed-fat
    # column is pinned too (20.13): it is now the cheapest tank case for these cells. Ordinary cells (row 2) and the
    # floor's cell without engineering did not move: ammonia still sets their medium.
    # 2026-11-20 model batch, in the order below, before -> after: 11.78 -> 14.148, 10.21 -> 12.153, 8.92 -> 10.468, 7.59 -> 8.768,
    # 26.74 -> 39.49, 22.39 -> 32.87, 20.13 -> 29.01, 31.09 -> 44.06, 26.89 -> 37.50, 12.00 -> 14.42, 7.70 -> 8.906, 6.91 -> 8.742,
    # 5.325 -> 6.254, 18.34 -> 28.05, 5.475 -> 6.476, 7.97 -> 10.278, 5.895 -> 7.090, 20.14 -> 30.93, 13.98 -> 17.98, 9.79 -> 12.363,
    # 9.90 -> 12.515, 7.52 -> 9.849, 8.16 -> 10.837. The slow, wasteful cells rose most (the best shown in meat cells by 44-54%):
    # they double in 43 hours, so the same bubbles kill 14% of them, and every litre of their 90 is passed for cells that die.
    # Final model (2026-11-20, later): the column case of the floor's cell 10.468 -> 11.982 (oxygen now binds at 153 g/L,
    # viscous_kla); the rest moved by under 1% with the day's engine fixes.
    pins = [("sanitary", 0.0, True, 0, 0, 14.052), ("sanitary", 0.0, True, 0, 1, 12.076), ("sanitary", 0.0, True, 0, 2, 11.982),
            ("sanitary", 0.0, True, 0, 3, 8.723), ("sanitary", 0.0, True, 1, 0, 39.35), ("sanitary", 0.0, True, 1, 3, 32.79),
            ("sanitary", 0.0, True, 1, 1, 28.90),
            ("sanitary", 0.0, True, 2, 0, 43.96), ("sanitary", 0.0, True, 2, 3, 37.50), ("sanitary", 0.002, True, 0, 0, 14.32),
            ("sanitary", 0.002, True, 0, 3, 8.860), ("microbial", 0.0, True, 0, 0, 8.742), ("microbial", 0.0, True, 0, 3, 6.254),
            ("microbial", 0.0, True, 1, 3, 28.05), ("microbial", 0.006, True, 0, 3, 6.476), ("microbial", 0.022, True, 0, 0, 10.278),
            ("microbial", 0.022, True, 0, 3, 7.090), ("microbial", 0.022, True, 1, 3, 30.93),
            ("sanitary", 0.0, False, 0, 0, 17.89), ("sanitary", 0.0, False, 0, 3, 12.318), ("sanitary", 0.002, False, 0, 3, 12.469),
            ("microbial", 0.0, False, 0, 3, 9.849), ("microbial", 0.022, False, 0, 3, 10.837)]
    tabs = {}
    for plant, hz, genetic, ci, tj, want in pins:
        tabs.setdefault((plant, hz, genetic), ge.cases_table(plant, hz, genetic=genetic))
        near(f"note: cases table {plant} loss {hz} genetic {genetic} cell {ci} tank {tj}",
             tabs[(plant, hz, genetic)][ci * 4 + tj][2], want, 0.002)
    # what sets the medium of each kind of cell, and what that does to the worth of the tricks (second round, 2026-11-19)
    t0 = tabs[("sanitary", 0.0, True)]
    meat, ordinary = t0[4:8], t0[8:12]
    # 2026-11-20: what sets the medium is unchanged, and so are the litres per kilo grown (89.8, 140 and 28). The table's litres
    # are per kilo harvested: 106.9, 156.3 and 31.1 where the sparger runs at its cap (the tank cases 0, 1 and 3), a little
    # less with the column alone (case 2: 106.4, 155.8, 31.0), which thickens the culture to the mixing limit, where the cap is
    # not all used and fewer cells are killed.
    if not all(r[6] == "lactate" for r in meat) or not all(abs(meat[j][5] - 106.9) < 0.1 for j in (0, 3)) \
            or not 106.0 < meat[2][5] < 106.9:
        fails.append("best shown in meat cells: lactate should set the medium, at 106.9 L per kilo harvested unless fat is fed")
    if not all(r[6] == "ammonia" for r in ordinary) or not all(abs(ordinary[j][5] - 156.26) < 0.01 for j in (0, 1, 3)) \
            or not 155.5 < ordinary[2][5] < 156.26:
        fails.append("ordinary meat cells: ammonia should set the medium at 156.3 L per kilo harvested")
    if not meat[1][5] < 0.7 * meat[0][5]:
        fails.append("fed fat should cut the best-shown meat cells' medium by over 30% (less glucose taken up, less lactate)")
    if min(range(4), key=lambda j: meat[j][2]) != 1:
        fails.append("fed fat should be the cheapest tank case for the best-shown meat cells")
    if not meat[0][2] > 2.0 * t0[0][2]:
        fails.append("best shown in meat cells should cost over twice the floor's cell in the same tank")
    noge = ge.cases_table("sanitary", 0.0, genetic=False)[:4]
    # final model: the column case (2) now stops at the oxygen limit with the sparger at its cap, so its litres are the
    # same 31.058 as the other three (it reached the mixing limit and used less gas before viscous_kla)
    if not all(r[6] == "ammonia" for r in noge) or not all(abs(noge[j][5] - 31.058) < 0.01 for j in range(4)):
        fails.append("the floor's cell by selection and feed: ammonia should still set the medium, at 31.1 L per kilo harvested")
    if any(c[2] == ge.GE for k, c in ge.CELL_CASES.items() if k != "floor"):
        fails.append("only the floor's assumed cell should need genetic engineering")
    lr = ge.lactate_relief()
    near("note: lactate could supply this share of the energy", lr["share_of_energy"], 0.021, 0.03)

    # final model: 11.99 -> 12.51 and 11.704 -> 12.207 (at depth = width oxygen now binds at 153 g/L)
    near("note: page shape lever at depth = width includes steel", fp.explore(aspect=1.0)["total"], 12.51, 0.002)
    near("shape cost off reproduces the shape-free figure", fp.explore(aspect=1.0, shape_cost=False)["total"], 12.207, 0.002)

    # --- circulation and the pH rule (review of PR 10) -------------------------------------------------------
    near("default column strips to 55 mbar", fp.explore(column="co2")["total"], 11.982, 0.002)   # 10.468 before the final model
    # final model: the column alone stops at 153 g/L (oxygen), so 11.1 -> 5.34 passes an hour and 0.92 -> 0.44 of the safe dose
    for kw, passes, safe in ((dict(column="co2"), 5.34, 0.44), (dict(column="o2_closed", p_top_barg=1.0), 22.4, 1.89),
                             (dict(column="o2_closed", p_top_barg=1.0, gas_velocity=0.002), 61.0, 5.16)):
        d = fp.explore(**kw)["column"]
        near(f"note: passes an hour {kw}", d["passes"], passes, 0.01)
        near(f"note: alkaline exposure vs the safe design {kw}", d["ph_vs_safe"], safe, 0.02)
    # 2026-11-20: 17.57 / 12.00 / 8.79 / 7.75 / 7.08 / 5.21 before the batch
    # final model: 20.150 / 13.695 / 10.639 / 9.280 / 8.479 / 6.419 -> the figures below (viscous_kla)
    for cap, plant, want in ((0.001, "sanitary", 21.972), (0.002, "sanitary", 14.622), (0.004, "sanitary", 11.481),
                             (0.006, "sanitary", 9.478), (0.002, "microbial", 9.093), (0.006, "microbial", 6.605)):
        b = ge.cheapest_tricks(cap, plant, ph_safe=True, tested=True)
        near(f"note: cheapest within pH and tested passes, {cap * 1000:.0f} mm/s {plant}", b["total"], want, 0.002)
        if b["column"] is not None and (b["column"]["ph_vs_safe"] > 1 + 1e-9 or not b["column"]["passes_tested"]):
            fails.append("constrained cheapest broke its own constraint")

    # --- cell side: fat in the feed, the oxygen setpoint, gas per kg ------------------------------------------
    near("fat fed: RQ 1.204 -> 0.966", fp.explore(fat_fed=1.0)["rq"], 0.9659, 1e-3)
    near("note: fat fed, CO2 cap", fp.explore(fat_fed=1.0)["limits"]["CO2 removal"], 149.6, 0.005)
    near("lipid CO2 per O2 matches Humbird's Reactions 2.2 and 2.11", value("pf_rq_lipid"), 0.090 / 0.378, 1e-3)
    # final model: 234.7 -> 177.1 and 225.8 -> 171.9; without viscous_kla they are what they were
    near("note: oxygen cap at 0.05 mmol/L", fp.explore(do_mmol=0.05)["limits"]["oxygen supply"], 177.1, 0.005)
    near("note: oxygen cap at 0.10 mmol/L", fp.explore(do_mmol=0.10)["limits"]["oxygen supply"], 171.9, 0.005)
    near("oxygen cap at 0.05 mmol/L without viscous_kla", fp.explore(do_mmol=0.05, viscous_kla=False)["limits"]["oxygen supply"], 234.7, 0.005)
    near("oxygen setpoint at the implied level changes nothing", fp.explore(
        do_mmol=ge.headspace_pressure()["c_liquid_implied"])["limits"]["oxygen supply"], r0["limits"]["oxygen supply"], 1e-9)
    near("note: oxygen per kg at 24 h, mol", r0["o2_kg"], 5.16, 0.005)
    near("upkeep + growth = oxygen per kg", r0["o2_kg_upkeep"] + r0["o2_kg_growth"], r0["o2_kg"], 1e-9)
    near("note: oxygen per kg at 48 h", fp.explore(doubling_h=48)["o2_kg"], 7.74, 0.005)
    near("CO2 per kg = RQ x oxygen", r0["co2_kg"], 1.204 * r0["o2_kg"], 1e-3)
    # 2026-11-20: 7.96 / 7.83 / 7.50 / 5.56 / 5.21 before the batch. The order by gas is gone (see the docstring): with every
    # trick allowed the three sanitary figures are within $0.03 of each other, and 2 mm/s is the cheapest.
    # final model: 8.560 / 8.533 / 8.562 / 6.156 / 6.079 -> 8.518 / 8.491 / 8.723 / 6.156 / 6.254. The check "the gas
    # tolerated moves the cost by under $0.05" no longer holds and is replaced: the thickness binds at every gas flow, so the
    # only thing the gas changes is the cells the bubbles kill (1.3%, 2.7% and 8.0% of the cells grown), and 2 mm/s, where
    # the oxygen column has the least to do beyond the sparger, is the cheapest; 6 mm/s costs $0.23 more.
    for cap, plant, want in ((0.001, "sanitary", 8.518), (0.002, "sanitary", 8.491), (0.006, "sanitary", 8.723),
                             (0.002, "microbial", 6.156), (0.006, "microbial", 6.254)):
        near(f"note: cheapest tricks at {cap * 1000:.0f} mm/s, {plant}", ge.cheapest_tricks(cap, plant)["total"], want, 0.002)
    trio = [ge.cheapest_tricks(cap, "sanitary") for cap in (0.001, 0.002, 0.006)]
    if not (all(t["limit"] == "thickness of the culture" for t in trio) and trio[0]["death_share"] < trio[1]["death_share"]
            < trio[2]["death_share"] and min(range(3), key=lambda i: trio[i]["total"]) == 1
            and trio[2]["total"] - trio[1]["total"] < 0.30):
        fails.append("with every trick allowed the thickness should bind at every gas flow, the bubbles kill more the more gas, "
                     "2 mm/s is cheapest and 6 mm/s costs under $0.30 more")

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
            # final model: 11.07 / 10.30 / 19.30 / 14.05 / 11.18 / 0.75 / 11.22 / 10.39 -> the figures here (viscous_kla)
            ("note: floor with CO2 loop", f["total"], 12.28), ("note: floor, CO2 limit gone", f["no_co2_limit"], 11.82),
            ("note: floor, no sparging", ge.floor_with_loop(oxygen=True)["total"], 12.62),
            ("note: 2 mm/s cells, CO2 loop", ge.floor_with_loop(gas_velocity=0.002)["total"], 20.90),
            ("note: fish cells, CO2 loop", ge.floor_with_loop(pco2_mbar=50.0, mass_pg=2500.0)["total"], 15.22),
            ("note: cheapest shape, $/kg", ge.best_shape()["total"], 12.35), ("note: cheapest shape", ge.best_shape()["aspect"], 1.1),
            ("note: squat tank 0.8, $/kg", ge.shape_case(0.8)["total"], 12.95),
            ("note: 200 m3 in ten compartments", ge.shape_case(0.8, 200.0, cells_in_shell=10)["total"], 11.21),
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
