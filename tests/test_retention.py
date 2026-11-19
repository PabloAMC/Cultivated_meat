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
    fails = []
    for name, kw in R.cases().items():
        d = R.duty(kw)
        r = d["result"]
        # liquid balance: medium in = bleed + permeate
        if not close(d["medium_m3_h"], d["bleed_m3_h"] + d["permeate_m3_h"]):
            fails.append(f"{name}: medium in != bleed + permeate")
        # the bleed carries the harvest: bleed x density = kg/h
        if not close(d["bleed_m3_h"] * d["density"], d["kg_h"]):
            fails.append(f"{name}: bleed x density != harvest")
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
    if not close(R.scenario_cost("hoped", {})["total"], 12.4512, 1e-5):
        fails.append("the hoped-for device no longer gives the pinned reference cost ($12.45)")
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
    for dev, want in (("tff", 32.8028), ("discstack", 27.4945), ("atf", 37.4828)):
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
    for dev, want in (("reuse", 24.2304), ("dialyser", 20.2877), ("ceramic", 21.6535)):
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
    # only the Engineered cells, all favourable case (258 -> 193 g/L); no case loses growth for oxygen at the default sizes (the Engineered cells, all favourable case loses 2e-6);
    # no settler is impossible
    for name, kw in cs.items():
        a_, m_ = R.scenario_cost("aggregates", kw), R.scenario_cost("microcarriers", kw)
        if not (a_["beyond"] and m_["beyond"] and m_["note"]["capped"] and a_["note"]["capped"] == (name == "best")):
            fails.append(f"{name}: particle verdicts moved")
        if a_["note"]["penalty"] > 1e-5 or a_["impossible"] or m_["impossible"]:      # best: 300 um just above its 295 um
            fails.append(f"{name}: expected no growth lost and a possible settler")
        if not m_["total"] > R.scenario_cost("tff", kw)["total"]:
            fails.append(f"{name}: carriers should cost more than the filter loop")
    # ranking in Selected cells: aggregates beat every device shown at that density (TFF, ATF, disc stack) and the reused modules
    ag = R.scenario_cost("aggregates", cen)["total"]
    for dev in ("tff", "atf", "discstack", "reuse", "ceramic"):
        if not ag < R.scenario_cost(dev, cen)["total"]:
            fails.append(f"central: aggregates should cost less than {dev}")
    # every figure the note quotes (research_notes/retention_aggregates.md)
    pins = {("aggregates", "reference"): 12.12, ("aggregates", "central"): 20.39, ("aggregates", "best"): 8.34,
            ("microcarriers", "reference"): 37.43, ("microcarriers", "central"): 84.39, ("microcarriers", "best"): 28.53}
    for (dev, name), want in pins.items():
        got = R.scenario_cost(dev, cs[name])["total"]
        if abs(got - want) > 0.005:
            fails.append(f"{name} {dev}: ${got:.2f} != pinned ${want}")
    rng = {("aggregates", "central"): (19.95, 29.08), ("aggregates", "best"): (7.46, 12.12),
           ("microcarriers", "central"): (28.98, 451.86), ("microcarriers", "best"): (10.31, 213.19)}
    for (dev, name), want in rng.items():
        r = R.scenario_range(dev, cs[name])
        if max(abs(r["low"]["total"] - want[0]), abs(r["high"]["total"] - want[1])) > 0.005:
            fails.append(f"{name} {dev} range: ${r['low']['total']:.2f}-{r['high']['total']:.2f} != pinned {want}")
    ox = R.oxygen_sizes()
    for name, key, want in (("reference", "own", 543), ("central", "own", 307), ("best", "own", 295),
                            ("central", 0.21, 485), ("central", 0.28, 570)):
        got = ox[name][key][1] if key == "own" else ox[name][key]
        if round(got) != want:
            fails.append(f"{name}: oxygenated aggregate {got:.0f} um at {key} != pinned {want}")
    ca = R.scenario_cost("aggregates", cen)
    cm = R.scenario_cost("microcarriers", cen)
    for label, got, want, tol in (("aggregate cap g/L", ca["note"]["cap"], 193.5, 0.05), ("plate area m2", ca["area_m2"], 22.3, 0.05),
                                  ("aggregate cm/h alone", ca["particle_cm_h"], 57.0, 0.5), ("stay min", ca["stay_min"], 16.0, 0.5),
                                  ("carrier cap g/L", cm["note"]["cap"], 25.5, 0.05), ("carrier kg/kg", cm["particle"]["carrier_kg"], 0.62, 0.005),
                                  ("bead L/kg", cm["particle"]["bead_l_kg"], 8.8, 0.05), ("carrier share of product", cm["particle"]["carrier_wet_share"], 0.90, 0.005),
                                  ("carriers $/kg", cm["cons_kg"], 6.16, 0.005), ("bead cm/h alone", cm["particle_cm_h"], 239.0, 0.5)):
        if abs(got - want) > tol:
            fails.append(f"central {label}: {got:.3f} != pinned {want}")
    # at the carriers' density the harvest carries all the medium out: nothing is left for a device to clear
    if R.duty(R.particle_case("microcarriers", cen)[0])["permeate_m3_h"] > 1e-9:
        fails.append("central carriers: expected no permeate at the carriers' density")
    # larger aggregates lose growth; a higher setpoint keeps them oxygenated but lowers the tank's density
    scan = {(round(sp, 2), dm): (pen, x, tot) for sp, dm, pen, x, tot in R.aggregate_scan()}
    for key, want in (((0.1, 600.0), (0.065, 20.95)), ((0.28, 600.0), (0.0, 21.34))):
        pen, x, tot = scan[key]
        if abs(pen - want[0]) > 0.0005 or abs(tot - want[1]) > 0.005:
            fails.append(f"aggregate scan {key}: growth lost {pen:.4f}, ${tot:.2f} != pinned {want}")
    if round(scan[(0.28, 600.0)][1]) != 172:
        fails.append("aggregate scan: at 0.28 mmol/L the central tank should hold 172 g/L")
    for key, want in (((0.1, 300.0), (0.0, 20.39)), ((0.1, 400.0), (0.009, 20.45)), ((0.1, 500.0), (0.035, 20.62)),
                      ((0.28, 300.0), (0.0, 21.34))):
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
    for name, row in (("reference", (295, 466, 547)), ("central", (307, 485, 570)), ("best", (295, 466, 547))):
        got = tuple(round(ox[name][x]) for x in (0.10, 0.21, 0.28))
        if got != row:
            fails.append(f"{name}: oxygenated sizes {got} != pinned {row}")
    c = R._cells(cen)
    for label, st, kw, want in (("no film", {"rt_o2_sherwood": 1e12}, {}, 346), ("still liquid", {"rt_o2_sherwood": 2.0}, {}, 227),
                                ("proliferation level high", {}, {"c_min": 0.065}, 211), ("low", {}, {"c_min": 0.013}, 333)):
        with R._with(st):
            if round(R.critical_diameter(c, 0.10, **kw)) != want:
                fails.append(f"central oxygenated size, {label}: {R.critical_diameter(c, 0.10, **kw):.0f} != {want}")
    if not (abs(c.qo2 - 0.137) < 0.0005 and abs(R._cells(cs["best"]).qo2 - 0.149) < 0.0005 and abs(R.uptake_per_volume(c) - 0.030) < 0.0005):
        fails.append("uptake figures moved (0.137, 0.149 mmol/g/h; 0.030 mol/m3/s)")
    # one input at a time, at the ends of its range (section 4)
    one = {("aggregates", "rt_agg_cell_share", 0.60): 22.44, ("aggregates", "rt_part_phi_max", 0.20): 22.38,
           ("aggregates", "rt_part_loss", 0.01): 19.98, ("aggregates", "rt_part_loss", 0.08): 21.50,
           ("aggregates", "rt_agg_d_max_um", 450.0): 20.52, ("aggregates", "rt_o2_prolif", 0.065): 20.54,
           ("microcarriers", "rt_mc_cells_cm2", 1e5): 144.44, ("microcarriers", "rt_mc_cells_cm2", 3e5): 57.07,
           ("microcarriers", "rt_mc_d_um", 100.0): 52.26, ("microcarriers", "rt_mc_d_um", 250.0): 108.09,
           ("microcarriers", "rt_part_phi_max", 0.35): 64.33, ("microcarriers", "rt_mc_price", 3.0): 79.95,
           ("microcarriers", "rt_mc_price", 50.0): 109.78}
    for (dev, k, v), want in one.items():
        with R._with({k: v}):
            got = R.scenario_cost(dev, cen)["total"]
        if abs(got - want) > 0.005:
            fails.append(f"central {dev} with {k} = {v}: ${got:.2f} != pinned ${want}")
    with R._with({"rt_agg_cell_share": 0.60}):
        if round(R.scenario_cost("aggregates", cen)["density"]) != 155:
            fails.append("aggregates at a cell share of 0.60 should hold Selected cells to 155 g/L")
    rg = R.scenario_range("aggregates", cen)["high"]
    if round(rg["density"]) != 124 or round(R.scenario_range("microcarriers", cen)["low"]["density"]) != 94:
        fails.append("range ends: aggregates 124 g/L, carriers 94 g/L")
    # settling: Selected cells' 2 ng cell at 1.8 cm/h; a 100 um aggregate 31 times faster, a 300 um one about 280 times
    d_cell = (6.0 * 2000.0 * 1e-15 / (math.pi * value("pf_cell_density") * 1000.0)) ** (1.0 / 3.0) * 1e6
    v1 = fp._stokes(d_cell, (value("pf_cell_density") - value("pf_medium_density")) * 1000.0)
    a = R.scenario_cost("aggregates", cen)
    drho = R.particle("aggregates", cen)["drho"]
    if not (round(d_cell, 1) == 15.4 and round(v1, 1) == 1.8 and round(a["particle_cm_h"] / v1) == 31
            and 270 <= fp._stokes(300.0, drho) / v1 <= 290 and round(a["holdup_m3"], 2) == 0.38 and round(drho) == 22):
        fails.append("settling figures moved (15.4 um, 1.8 cm/h, 31x, about 280x, 0.38 m3, 22 kg/m3)")
    s1 = R.sizing("settler", cen)
    if round(s1["area_m2"]) != 488 or round(s1["holdup_m3"], 1) != 8.3:
        fails.append("single-cell settler: 488 m2 and 8.3 m3")
    # carriers for the 3 ng cells of the reference and best cases; Selected cells' layer 3.5 um; Cytodex at EUR 7.6/g about $5,000/kg
    pb, pc = R.particle("microcarriers", cs["best"]), R.particle("microcarriers", cen)
    if not (round(pb["carrier_kg"], 2) == 0.41 and round(pb["bead_l_kg"], 1) == 5.9 and round(pb["carrier_wet_share"], 2) == 0.86
            and round(pb["cap"]) == 36 and round(pc["layer_um"], 1) == 3.5 and 4500 < pc["carrier_kg"] * 7600 * 1.08 < 5500):
        fails.append("carrier figures moved (0.41 kg, 5.9 L, 86%, 36 g/L; 3.5 um; about $5,000)")
    if not 7.0 < R.duty(cen)["kg_year"] / R.duty(R.particle_case("microcarriers", cen)[0])["kg_year"] < 8.0:
        fails.append("carriers: the central tank should make about a seventh of the kilos")
    return fails


def test_retention():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the retention-device study holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
