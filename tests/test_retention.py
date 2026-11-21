#!/usr/bin/env python3
"""test_retention.py — the retention-device study (retention.py).

Checks the duty against explore() (mass and liquid balance), that the devices are sized on the right flow, that the
default model is untouched (the hoped-for device reproduces the scenario costs), and pins the headline. Run directly or
under pytest.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import floor_physics as fp
import retention as R
import scenarios as S
from inputs import value


def close(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(1.0, abs(b))


def run_share(kw: dict) -> float:
    """The share of a planned run an average start completes at the case's chance of losing a run per day (explore()'s rule
    for filter membranes since the 2026-11-19 audit: a lost run throws its membranes away early). 1 with no losses."""
    h, days = kw.get("hazard", 0.0), value("pf_run_days")
    return 1.0 if h <= 0 else (1.0 - math.exp(-h * days)) / (h * days)


def check() -> list:
    # CORRECTED 2026-11-20 (second pass). explore() reports output and litres per kilo HARVESTED (bubble deaths, harvest loss);
    # retention.duty took the bleed as harvested kilos / density, though the culture that leaves carries the cells GROWN, and
    # scenario_cost() passed a device's running cost per kilo harvested as explore's extra_opex, which explore divided by the
    # harvested share again. duty() now takes bleed = harvest / harvested_share / density, and scenario_cost passes the cost per
    # kilo grown (sizing's `cons_kg_grown`). The pins below were set again from the module's output after that, after the gas
    # the culture needs was corrected in explore (a column that strips nothing no longer lowers bubble deaths: the thin
    # carrier culture pays for more of them), and after the all-favourable example became scenarios.all_favourable() (3 ng
    # cells, 16 hours, dialyser-grade fibres, $7.56).
    fails = []
    for name, kw in R.cases().items():
        d = R.duty(kw)
        r = d["result"]
        # liquid balance: medium in = bleed + permeate
        if not close(d["medium_m3_h"], d["bleed_m3_h"] + d["permeate_m3_h"]):
            fails.append(f"{name}: medium in != bleed + permeate")
        # the bleed carries the cells grown: bleed x density = kg harvested an hour / the share of the cells grown that is harvested
        if not close(d["bleed_m3_h"] * d["density"], d["kg_h"] / r["harvested_share"]):
            fails.append(f"{name}: bleed x density != the cells grown")
        # the harvest over a year is the tank's output
        if not close(d["kg_h"] * 8760 * d["uptime"], r["output"] * d["vessel_m3"] * 1000.0):
            fails.append(f"{name}: harvest over the year != output")
    # the model's default is the TFF loop: retention.py's own sizing gives the same capital and membranes as explore().
    # 2026-11-19 audit batch: both now charge the membranes of lost runs (life x the share of a planned run an average start
    # completes, explore()'s `run_frac`), and that share is the one this test works out from the case's chance of losing a run
    for name, kw in R.cases().items():
        d0 = R.duty(kw)
        sz, r = R.sizing("tff", kw, d0), d0["result"]
        if not (close(sz["capex_k_m3"], r["retention_capex"], 1e-9) and close(sz["cons_kg"], r["membranes"], 1e-9)):
            fails.append(f"{name}: TFF sizing ({sz['capex_k_m3']:.3f}k, ${sz['cons_kg']:.3f}) != explore "
                         f"({r['retention_capex']:.3f}k, ${r['membranes']:.3f})")
        if not close(d0["run_frac"], run_share(kw), 1e-9):
            fails.append(f"{name}: run share {d0['run_frac']:.4f} != {run_share(kw):.4f} from the chance of losing a run")
    # the old hoped-for device: a flat $89k per m3 and no membranes gives the reference case's cost with that device
    # 2026-11-19 repin: nutrient floor $1.70 -> $2.00 ($12.15 -> $12.45); growth factors inside complete media prices
    # (central -$2.99, disc stack -$3.69 as it buys more medium)
    # 2026-11-20 batch: bubble deaths, harvest loss, twice the fed-batch crew, medium preparation capital, utilities ($12.45 -> $14.89)
    # 2026-11-20, third pass: plant items charged per tank (floor_physics.tank_items) and the plant floor ($14.89 -> $14.79)
    if not close(R.scenario_cost("hoped", {})["total"], 14.7944, 1e-5):
        fails.append("the hoped-for device no longer gives the pinned reference cost ($14.79)")
    cen = R.cases()["central"]
    d = R.duty(cen)
    # ATF: whole units that cover the permeate at the design flux
    a = R.sizing("atf", cen, d)
    if a["units"] != int(a["units"]) or a["units"] * value("rt_atf_area") * value("rt_flux_lmh") / 1000.0 < d["permeate_m3_h"]:
        fails.append("ATF units do not cover the permeate")
    # membranes: litres of permeate per kg x price per m2 / litres per m2 over a life, the life cut by the runs lost
    want = d["permeate_m3_h"] * 1000.0 / d["kg_h"] * value("rt_membrane_price") / (value("rt_membrane_life") * run_share(cen))
    if not close(R.sizing("tff", cen, d)["cons_kg"], want, 1e-12):
        fails.append("membrane cost per kg is not permeate x price / life")
    # a device's running cost reaches explore per kilo grown, so it is divided by the harvested share once: the cost with a device
    # is explore's with that device's capital and its running cost per kilo harvested, over the cells that survive it
    for dev in ("atf", "reuse", "dialyser", "ceramic", "discstack"):
        sz = R.sizing(dev, cen, d)
        r0 = fp.explore(**{**cen, "retention": sz["capex_k_m3"]})
        if not close(R.scenario_cost(dev, cen)["total"], (r0["total"] + sz["cons_kg"]) / (1.0 - sz["loss"]), 1e-9):
            fails.append(f"central {dev}: the device's running cost per kilo harvested is not added once")
    # a settler is not possible at the central duty (too much culture outside the tank), possible at the reference duty
    if not R.sizing("settler", cen, d)["impossible"] or R.sizing("settler", {}, None)["impossible"]:
        fails.append("settler feasibility: expected not possible in central, possible in the reference case")
    # a disc stack loses more cells the more of the culture it passes, and never all of them
    ds = R.sizing("discstack", cen, d)
    if not 0.0 < ds["loss"] < 1.0 or not ds["loss"] > R.sizing("discstack", {}, None)["loss"]:
        fails.append("disc-stack losses out of order")
    # ranges: favourable <= central <= unfavourable
    for dev in R.ORDER:
        rg = R.scenario_range(dev, cen)
        if not rg["low"]["total"] <= rg["mid"]["total"] + 1e-9 <= rg["high"]["total"] + 2e-9:
            fails.append(f"{dev}: range out of order")
    # pinned headline (central): TFF $32.80, disc stack $27.49, ATF $37.48
    # 2026-11-19 audit batch: ammonia tolerance 4 mmol/L (35 L/kg, was 28: permeate 1.71 m3/h, was 1.31, so more membrane, more
    # ATF units, a second running disc stack and more cells burst); the TFF loop and the ATF filter also pay for the membranes
    # of lost runs
    # 2026-11-20 batch: membranes replaced after 2,415 L/m2 (3,960 before) and every cost per kilo harvested (87% of the cells grown);
    # 40 litres a kilo harvested. TFF $32.80 -> $49.96, disc stack $27.49 -> $36.91, ATF $37.48 -> $59.45
    # 2026-11-20, second pass (the bleed carries the cells grown; a device's running cost divided by the harvested share once):
    # disc stack $36.91 -> $35.42, ATF $59.45 -> $55.32; the TFF loop is explore itself and did not move
    # 2026-11-20, third pass: the low-lactate example's design now holds 154 g/L (was 191; scenarios), plant items per tank, and
    # an ATF unit priced with Humbird's accounting for bought equipment, escalated to 2025 (retention.atf_factor, 6.25 x bare,
    # was rt_install 1.84): TFF $49.96 -> $49.50, disc stack $35.42 -> $34.34, ATF $55.32 -> $66.60
    for dev, want in (("tff", 49.4977), ("discstack", 34.3402), ("atf", 66.5955)):
        got = R.scenario_cost(dev, cen)["total"]
        if not close(got, want, 1e-4):
            fails.append(f"central {dev}: {got:.4f} != pinned {want}")
    # a thinner culture does not pay in the central case: the cheapest density is the one the tank allows
    scan = R.density_scan(R.cases()["central"])
    if min(scan, key=lambda r: r[1])[0] != 258.0 or not scan[-1][2] < scan[0][2]:
        fails.append("central: a thinner culture should save membranes but cost more in total")
    # the alternative membranes: each is cheaper per kg than the default TFF loop in the central case, and the dialyser's
    # lower flux needs more membrane area for the same duty
    tff_c = R.scenario_cost("tff", cen)
    for dev in ("reuse", "dialyser", "ceramic"):
        if not R.scenario_cost(dev, cen)["total"] < tff_c["total"]:
            fails.append(f"central {dev}: should cost less than the TFF loop")
    if not R.sizing("dialyser", cen, d)["area_m2"] > R.sizing("tff", cen, d)["area_m2"]:
        fails.append("dialyser: lower flux should need more membrane area than the TFF loop")
    if not R.sizing("reuse", cen, d)["cons_kg"] < R.sizing("tff", cen, d)["cons_kg"]:
        fails.append("reused modules: membranes per kg should fall")
    # 2026-11-19 audit batch: ammonia tolerance 4 mmol/L (more permeate, so more membrane area and membranes); reused modules and
    # dialysers pay for the membranes of lost runs, ceramic elements are cleaned and kept
    # 2026-11-20 batch: 24.23 -> 31.60, 20.29 -> 26.30, 21.65 -> 28.05
    # 2026-11-20, second pass (as above): 31.60 -> 30.76, 26.30 -> 26.24, 28.05 -> 27.81
    # 2026-11-20, third pass (154 g/L, plant items per tank): 30.76 -> 31.70, 26.24 -> 27.52, 27.81 -> 28.97
    for dev, want in (("reuse", 31.7044), ("dialyser", 27.5181), ("ceramic", 28.9683)):
        got = R.scenario_cost(dev, cen)["total"]
        if not close(got, want, 1e-3):
            fails.append(f"central {dev}: {got:.4f} != pinned {want}")
    # the order of the membrane devices: dialysers < ceramic < reused modules < TFF loop < ATF filter
    order = [R.scenario_cost(dev, cen)["total"] for dev in ("dialyser", "ceramic", "reuse", "tff", "atf")]
    if order != sorted(order):
        fails.append("central: expected dialyser < ceramic < reused modules < TFF loop < ATF")
    # a lost run does not shorten a ceramic element's life: its membranes per kg are permeate x price / life as it stands
    if not close(R.sizing("ceramic", cen, d)["cons_kg"], d["permeate_m3_h"] * 1000.0 / d["kg_h"] * value("rt_ceramic_price") / value("rt_ceramic_life"), 1e-12):
        fails.append("ceramic: a lost run should not shorten the element's life")
    # pinned duty (reference case): 0.62 m3/h of medium, 0.16 of permeate
    d = R.duty({})
    if not (close(d["medium_m3_h"], 0.6195, 1e-3) and close(d["permeate_m3_h"], 0.1573, 1e-2)):
        fails.append(f"reference duty moved: medium {d['medium_m3_h']:.4f}, permeate {d['permeate_m3_h']:.4f}")
    fails += check_particles()
    return fails


def check_particles() -> list:
    """Cells grown as aggregates or on edible carriers (2026-11-19; research_notes/retention_aggregates.md)."""
    fails = []
    cs = R.cases()
    cen, best = cs["central"], cs["best"]
    # Stokes: speed goes as diameter squared and as the density excess
    if not (close(fp._stokes(200.0, 20.0) / fp._stokes(100.0, 20.0), 4.0, 1e-12)
            and close(fp._stokes(100.0, 40.0) / fp._stokes(100.0, 20.0), 2.0, 1e-12)):
        fails.append("Stokes speed should scale with d^2 and the density excess")
    # the critical diameter without the film is 2 sqrt(6 D (C_s - C_min) / Q), Q = qO2 x cells' share x cell density
    c = R._cells(cen)
    q = c.qo2 * value("rt_agg_cell_share") * value("pf_cell_density") * 1000.0 / 3600.0      # mol/m3/s
    if not close(R.uptake_per_volume(c), q, 1e-12):
        fails.append("uptake per volume of an aggregate is not qO2 x cells' share x cell density")
    D, cmin = value("rt_o2_diff_tissue"), value("rt_o2_prolif")
    with R._with({"rt_o2_sherwood": 1e12}):                     # no film
        want = 2.0 * math.sqrt(6.0 * D * (0.10 - cmin) / q) * 1e6
        if not close(R.critical_diameter(c, 0.10), want, 1e-9):
            fails.append("critical diameter without the film is not 2 sqrt(6 D dC / Q)")
    # with the film: the drop to the middle is Q R^2 (1/(6D) + 2/(3 Sh D_water))
    F = 1.0 / (6.0 * D) + 2.0 / (3.0 * value("rt_o2_sherwood") * value("rt_o2_diff_water"))
    dc = R.critical_diameter(c, 0.10)
    if not close(q * (dc * 1e-6 / 2.0) ** 2 * F, 0.10 - cmin, 1e-9):
        fails.append("critical diameter with the film does not bring the middle to C_min")
    # the hypoxic share: none at or below the critical size, some above it, rising with size and below 1
    sh = [R.hypoxic_share(x, c, 0.10) for x in (dc * 0.999, dc * 1.05, 1.5 * dc, 3.0 * dc)]
    if not (sh[0] == 0.0 and 0.0 < sh[1] < sh[2] < sh[3] < 1.0):
        fails.append(f"hypoxic share out of order: {sh}")
    # at the core radius found, the drop across the shell and the film equals C_s - C_min
    Rr = 1.5 * dc * 1e-6 / 2.0
    a = sh[2] ** (1.0 / 3.0) * Rr
    drop = (q / (6 * D) * (Rr ** 2 - a ** 2) + q * a ** 3 / (3 * D) * (1 / Rr - 1 / a)
            + 2 * q * (Rr ** 3 - a ** 3) / (3 * Rr * value("rt_o2_sherwood") * value("rt_o2_diff_water")))
    if not close(drop, 0.10 - cmin, 1e-6):
        fails.append("hypoxic core: the drop across the shell and film is not C_s - C_min")
    # carriers: cells' share of a loaded bead is 6t / (6t + d), t = cells/cm2 x mass / cell density; dry carrier per kg of
    # cells is solids x d / (6 x cells/cm2 x mass); the cap is phi_max x share x cell density
    p = R.particle("microcarriers", cen)
    m, sig, db = cen["mass_pg"] * 1e-12, value("rt_mc_cells_cm2"), value("rt_mc_d_um") * 1e-4
    t = sig * m / value("pf_cell_density")
    if not (close(p["share"], 6 * t / (6 * t + db), 1e-12) and close(p["carrier_kg"], value("rt_mc_solids") * db / (6 * sig * m), 1e-12)
            and close(p["cap"], value("rt_part_phi_max") * p["share"] * value("pf_cell_density") * 1000.0, 1e-12)):
        fails.append("carrier geometry: share, carrier per kg or cap is off")
    # verdicts: both are beyond what is shown in every case; carriers hold every case far below its density; aggregates hold
    # only the all-favourable example (258 -> 193 g/L); no case loses growth for oxygen at the default sizes (the all-favourable example loses 2e-6);
    # no settler is impossible
    for name, kw in cs.items():
        a_, m_ = R.scenario_cost("aggregates", kw), R.scenario_cost("microcarriers", kw)
        # 2026-11-20: the all-favourable example's cheapest tank is now the tall one with the column alone, at 153 g/L (it was 258 g/L
        # with the pressure in a squarer tank: bubble deaths follow the gas passed per litre and a tall tank passes less), so
        # the aggregates' 193 g/L no longer holds it: no case is held by the aggregates' cap
        if not (a_["beyond"] and m_["beyond"] and m_["note"]["capped"] and not a_["note"]["capped"]):
            fails.append(f"{name}: particle verdicts moved")
        # 2026-11-19 restructure: the best case's cells weigh 2 ng (were 3), so their oxygenated size is 281 um and its 300 um
        # aggregates lose a little growth (0.04%); allowed up to 0.1% there
        # 2026-11-20, second pass: the all-favourable example's cells weigh 3 ng and double in 16 hours (scenarios.all_favourable),
        # so their oxygenated size is 264 um and its 300 um aggregates lose 0.19% of growth; allowed up to 0.3% there
        if a_["note"]["penalty"] > (3e-3 if name == "best" else 1e-5) or a_["impossible"] or m_["impossible"]:
            fails.append(f"{name}: expected no growth lost and a possible settler")
        if not m_["total"] > R.scenario_cost("tff", kw)["total"]:
            fails.append(f"{name}: carriers should cost more than the filter loop")
    # ranking in the low-lactate example: aggregates beat every device shown at that density (TFF, ATF, disc stack) and the reused modules
    ag = R.scenario_cost("aggregates", cen)["total"]
    for dev in ("tff", "atf", "discstack", "reuse", "ceramic"):
        if not ag < R.scenario_cost(dev, cen)["total"]:
            fails.append(f"central: aggregates should cost less than {dev}")
    # every figure the note quotes (research_notes/retention_aggregates.md)
    # repinned 2026-11-20 (model batch; see the note at the top of check())
    # 2026-11-20, second pass: best is the new all-favourable case (11.42 -> 7.70, 46.93 -> 25.77); central carriers 99.26 ->
    # 100.17 (their thin culture bubbles the gas its CO2 needs, which the column no longer hides)
    # 2026-11-20, third pass (the low-lactate example at 154 g/L, plant items per tank)
    pins = {("aggregates", "reference"): 14.46, ("aggregates", "central"): 27.80, ("aggregates", "best"): 7.79,
            ("microcarriers", "reference"): 44.16, ("microcarriers", "central"): 96.46, ("microcarriers", "best"): 24.26}
    for (dev, name), want in pins.items():
        got = R.scenario_cost(dev, cs[name])["total"]
        if abs(got - want) > 0.005:
            fails.append(f"{name} {dev}: ${got:.2f} != pinned ${want}")
    rng = {("aggregates", "central"): (27.22, 36.77), ("aggregates", "best"): (7.62, 10.39),
           ("microcarriers", "central"): (36.02, 491.52), ("microcarriers", "best"): (8.68, 206.02)}   # 2026-11-20 batch, third pass
    for (dev, name), want in rng.items():
        r = R.scenario_range(dev, cs[name])
        if max(abs(r["low"]["total"] - want[0]), abs(r["high"]["total"] - want[1])) > 0.005:
            fails.append(f"{name} {dev} range: ${r['low']['total']:.2f}-{r['high']['total']:.2f} != pinned {want}")
    ox = R.oxygen_sizes()
    for name, key, want in (("reference", "own", 543), ("central", "own", 307), ("best", "own", 264),
                            ("central", 0.21, 485), ("central", 0.28, 570)):
        got = ox[name][key][1] if key == "own" else ox[name][key]
        if round(got) != want:
            fails.append(f"{name}: oxygenated aggregate {got:.0f} um at {key} != pinned {want}")
    ca = R.scenario_cost("aggregates", cen)
    cm = R.scenario_cost("microcarriers", cen)
    for label, got, want, tol in (("aggregate cap g/L", ca["note"]["cap"], 193.5, 0.05), ("plate area m2", ca["area_m2"], 12.9, 0.05),
                                  ("aggregate cm/h alone", ca["particle_cm_h"], 57.0, 0.5), ("stay min", ca["stay_min"], 11.7, 0.5),
                                  ("carrier cap g/L", cm["note"]["cap"], 25.5, 0.05), ("carrier kg/kg", cm["particle"]["carrier_kg"], 0.62, 0.005),
                                  ("bead L/kg", cm["particle"]["bead_l_kg"], 8.8, 0.05), ("carrier share of product", cm["particle"]["carrier_wet_share"], 0.90, 0.005),
                                  # per kilo harvested since 2026-11-20 (6.16 per kilo grown, over the 95.7% harvested)
                                  ("carriers $/kg", cm["cons_kg"], 6.435, 0.005), ("carriers $/kg grown", cm["cons_kg_grown"], 6.16, 0.005),
                                  ("bead cm/h alone", cm["particle_cm_h"], 239.0, 0.5)):
        if abs(got - want) > tol:
            fails.append(f"central {label}: {got:.3f} != pinned {want}")
    # at the carriers' density the harvest carries all the medium out: nothing is left for a device to clear
    if R.duty(R.particle_case("microcarriers", cen)[0])["permeate_m3_h"] > 1e-9:
        fails.append("central carriers: expected no permeate at the carriers' density")
    # larger aggregates lose growth; a higher setpoint keeps them oxygenated but lowers the tank's density
    scan = {(round(sp, 2), dm): (pen, x, tot) for sp, dm, pen, x, tot in R.aggregate_scan()}
    # 2026-11-20, third pass (the low-lactate example at 154 g/L, plant items per tank)
    for key, want in (((0.1, 600.0), (0.0654, 28.68)), ((0.28, 600.0), (0.0001, 28.95))):
        pen, x, tot = scan[key]
        if abs(pen - want[0]) > 0.0005 or abs(tot - want[1]) > 0.005:
            fails.append(f"aggregate scan {key}: growth lost {pen:.4f}, ${tot:.2f} != pinned {want}")
    if round(scan[(0.28, 600.0)][1]) != 142:
        fails.append("aggregate scan: at 0.28 mmol/L the central tank should hold 142 g/L")
    for key, want in (((0.1, 300.0), (0.0, 27.80)), ((0.1, 400.0), (0.009, 27.92)), ((0.1, 500.0), (0.035, 28.25)),
                      ((0.28, 300.0), (0.0, 28.94))):
        pen, x, tot = scan[key]
        if abs(pen - want[0]) > 0.0005 or abs(tot - want[1]) > 0.005:
            fails.append(f"aggregate scan {key}: growth lost {pen:.4f}, ${tot:.2f} != pinned {want}")
    fails += check_note_figures()
    return fails


def check_note_figures() -> list:
    """The remaining figures research_notes/retention_aggregates.md quotes."""
    fails = []
    cs = R.cases()
    cen = cs["central"]
    ox = R.oxygen_sizes()
    for name, row in (("reference", (295, 466, 547)), ("central", (307, 485, 570)), ("best", (264, 416, 489))):   # 2026-11-19: best's cells 2 ng, as the low-lactate example's ... (respire more per gram)
        got = tuple(round(ox[name][x]) for x in (0.10, 0.21, 0.28))
        if got != row:
            fails.append(f"{name}: oxygenated sizes {got} != pinned {row}")
    c = R._cells(cen)
    for label, st, kw, want in (("no film", {"rt_o2_sherwood": 1e12}, {}, 346), ("still liquid", {"rt_o2_sherwood": 2.0}, {}, 227),
                                ("proliferation level high", {}, {"c_min": 0.065}, 211), ("low", {}, {"c_min": 0.013}, 333)):
        with R._with(st):
            if round(R.critical_diameter(c, 0.10, **kw)) != want:
                fails.append(f"central oxygenated size, {label}: {R.critical_diameter(c, 0.10, **kw):.0f} != {want}")
    if not (abs(c.qo2 - 0.137) < 0.0005 and abs(R._cells(cs["best"]).qo2 - 0.186) < 0.0005 and abs(R.uptake_per_volume(c) - 0.030) < 0.0005):
        fails.append("uptake figures moved (0.137, 0.186 mmol/g/h; 0.030 mol/m3/s)")   # best 0.165 -> 0.186 (3 ng cells doubling in 16 h, 2026-11-20)
    # one input at a time, at the ends of its range (section 4)
    # repinned 2026-11-20 (model batch); third pass the same day (the low-lactate example at 154 g/L, which neither the
    # aggregates' cap at a cell share of 0.60 (155 g/L) nor at phi_max 0.20 holds any longer)
    one = {("aggregates", "rt_agg_cell_share", 0.60): 27.82, ("aggregates", "rt_part_phi_max", 0.20): 27.80,
           ("aggregates", "rt_part_loss", 0.01): 27.24, ("aggregates", "rt_part_loss", 0.08): 29.31,
           ("aggregates", "rt_agg_d_max_um", 450.0): 28.07, ("aggregates", "rt_o2_prolif", 0.065): 28.10,
           ("microcarriers", "rt_mc_cells_cm2", 1e5): 164.54, ("microcarriers", "rt_mc_cells_cm2", 3e5): 66.12,
           ("microcarriers", "rt_mc_d_um", 100.0): 60.94, ("microcarriers", "rt_mc_d_um", 250.0): 123.33,
           ("microcarriers", "rt_part_phi_max", 0.35): 73.88, ("microcarriers", "rt_mc_price", 3.0): 91.82,
           ("microcarriers", "rt_mc_price", 50.0): 123.00}
    for (dev, k, v), want in one.items():
        with R._with({k: v}):
            got = R.scenario_cost(dev, cen)["total"]
        if abs(got - want) > 0.005:
            fails.append(f"central {dev} with {k} = {v}: ${got:.2f} != pinned ${want}")
    # 2026-11-20, third pass: at a cell share of 0.60 the aggregates' cap is 155 g/L, just above the low-lactate example's 154 g/L,
    # so it no longer holds the example (it held it from 191 g/L)
    with R._with({"rt_agg_cell_share": 0.60}):
        ag60 = R.scenario_cost("aggregates", cen)
        if round(ag60["note"]["cap"]) != 155 or ag60["note"]["capped"] or round(ag60["density"]) != 154:
            fails.append("aggregates at a cell share of 0.60: cap 155 g/L, not holding the low-lactate example's 154 g/L")
    rg = R.scenario_range("aggregates", cen)["high"]
    if round(rg["density"]) != 124 or round(R.scenario_range("microcarriers", cen)["low"]["density"]) != 94:
        fails.append("range ends: aggregates 124 g/L, carriers 94 g/L")
    # settling: the low-lactate example's 2 ng cell at 1.8 cm/h; a 100 um aggregate 31 times faster, a 300 um one about 280 times
    d_cell = (6.0 * 2000.0 * 1e-15 / (math.pi * value("pf_cell_density") * 1000.0)) ** (1.0 / 3.0) * 1e6
    v1 = fp._stokes(d_cell, (value("pf_cell_density") - value("pf_medium_density")) * 1000.0)
    a = R.scenario_cost("aggregates", cen)
    drho = R.particle("aggregates", cen)["drho"]
    if not (round(d_cell, 1) == 15.4 and round(v1, 1) == 1.8 and round(a["particle_cm_h"] / v1) == 31
            and 270 <= fp._stokes(300.0, drho) / v1 <= 290 and round(a["holdup_m3"], 2) == 0.22 and round(drho) == 22):
        fails.append("settling figures moved (15.4 um, 1.8 cm/h, 31x, about 280x, 0.22 m3, 22 kg/m3)")
    # 2026-11-20, third pass: the low-lactate example at 154 g/L sends 1.32 m3/h of permeate (less than at 191 g/L), so
    # the plates are smaller: 12.9 m2 for aggregates (was 22.3), 307 m2 and 5.2 m3 for single cells (were 488 and 8.3)
    s1 = R.sizing("settler", cen)
    if round(s1["area_m2"]) != 307 or round(s1["holdup_m3"], 1) != 5.2:
        fails.append("single-cell settler: 307 m2 and 5.2 m3")
    # carriers for the 3 ng cells of the reference and best cases; the low-lactate example's layer 3.5 um; Cytodex at EUR 7.6/g about $5,000/kg
    pb, pc = R.particle("microcarriers", cs["best"]), R.particle("microcarriers", cen)
    # 2026-11-20, second pass: the all-favourable example's cells weigh 3 ng again (Humbird's, the more favourable), so its carriers
    # are the reference case's (0.41 kg, 5.9 L, 86%, 36 g/L); the low-lactate example's 2 ng cells keep 0.62 kg and a 3.5 um layer
    if not (round(pb["carrier_kg"], 2) == 0.41 and round(pb["bead_l_kg"], 1) == 5.9 and round(pb["carrier_wet_share"], 2) == 0.86
            and round(pb["cap"]) == 36 and round(pc["carrier_kg"], 2) == 0.62 and round(pc["layer_um"], 1) == 3.5
            and 4500 < pc["carrier_kg"] * 7600 * 1.08 < 5500):
        fails.append("carrier figures moved (best 0.41 kg, 5.9 L, 86%, 36 g/L; central 0.62 kg, 3.5 um; about $5,000)")
    # 2026-11-20: 6.8 times, not 7.3: the kilos are those harvested, and the thin carrier culture needs little gas, so bubbles kill 1%
    # of its cells against 11% of the dense tank's
    # 2026-11-20, third pass: 5.7 times: the low-lactate example now holds 154 g/L (was 191), nearer the carriers' 26 g/L
    if not 5.2 < R.duty(cen)["kg_year"] / R.duty(R.particle_case("microcarriers", cen)[0])["kg_year"] < 6.2:
        fails.append("carriers: the central tank should make about a sixth of the kilos")
    return fails


def test_retention():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the retention-device study holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
