#!/usr/bin/env python3
"""
answer_rests_on.py — which inputs the answer actually rests on, and how good the evidence for each is.

The model has about 500 inputs. Most serve side studies or a detail of the tank, and move the headline by cents. This module
finds the few that matter: it moves every input that has a range to the low and then the high end of that range, one at a
time, and records what happens to

  * the cost of a kilo of cells in the low-lactate example and in the all-favourable example (each scenario's tank design held as it is), and
  * the long-run share of world meat at the low-lactate example's cost and at the all-favourable example's cost.

It keeps the inputs that move either by more than a set amount, and says for each where its value comes from and whether the
scenarios' uncertainty bands (`scenarios.bands`) already draw it. An input that moves the answer a lot, rests on an assumption,
and is not in the band is where the model's stated uncertainty is too narrow, and where evidence is worth most.

    python answer_rests_on.py              # the tables, as text
    python answer_rests_on.py --markdown   # the tables RESULTS.md carries
"""
from __future__ import annotations

import dataclasses
import re
import sys
from dataclasses import replace

import floor_physics as fp
import inputs as I
import meat_market as mm
import scenarios as S
from inputs import value
from market_share import DemandParams, share

COST_MIN = 1.0           # $/kg in the low-lactate example or the all-favourable example
SHARE_MIN = (0.2, 2.0)   # percentage points of world meat, at the low-lactate example's cost and at the all-favourable example's cost

# plain names for the inputs that can appear in the tables (the test checks every row has one)
PLAIN = {
    "pf_nh3_limit": "Ammonia the cells tolerate in the tank (Humbird's design)",
    "sc_nh3_limit": "Ammonia the cells tolerate in the tank",
    "pf_lac_limit": "Lactate the cells tolerate in the tank (Humbird's design)",
    "sc_lac_limit": "Lactate the cells tolerate in the tank",
    "ge_kill_protected": "Culture whose cells bursting bubbles kill, per volume of gas passed",
    "pf_medium_prep_exp": "How the cost of medium preparation equipment rises with the medium passed (exponent)",
    "pf_harvest_recovery": "Share of the cells grown that the harvest gives back",
    "pf_labour_perfusion_x": "Staff a plant in perfusion needs, against a fed-batch plant",
    "pf_mature_h": "Hours the cells spend in the tank without growing before harvest (to mature muscle or fat)",
    "tc_kla_exp": "How fast oxygen uptake falls as the culture thickens (exponent on its viscosity)",
    "tc_thin": "How much thicker a dense culture is at the low shear of a large tank",
    # rows that crossed the $1 threshold when the costs rose on 2026-11-20
    "sc_lac_selected": "Lactate the cells of the low-lactate example make per mol of glucose",
    "sc_lac_engineered": "Lactate the low-waste cells make per mol of glucose",
    "pf_otr_cap": "Oxygen a stirred tank passes into the culture",
    "ge_col_pout": "CO₂ level at which the culture leaves the stripping column",
    "sc_do_setpoint": "Dissolved oxygen the tank is held at",
    "pi_vessel_food_k": "Price of a food-grade 20 m³ tank, installed",
    "sc_nh3_selected": "Ammonia the cells of the low-lactate example make per kilo grown",
    "sc_nh3_engineered": "Ammonia the low-waste cells make per kilo grown",
    "sc_mass_selected_pg": "Weight of one cell (every kind of cells since 2026-11-19)",
    "sc_p_top": "Pressure at the top of the tank, where the extra pressure is used",
    "rt_membrane_life": "Litres a m² of cell filter passes before it is replaced",
    "pf_protectant_price": "Price of the bubble protectant (poloxamer 188), bought by the tonne",
    "pf_min_perfusion": "Least medium flow the cells need for everything but ammonia and lactate",
    "plant_charge_mature": "Yearly charge on the plant's capital (financing and recovery)",
    "pf_antifoam_otr": "Oxygen transfer the sparger keeps with antifoam present",
    "pf_gas_velocity": "Gas flow the tank can take (superficial velocity)",
    "pf_protectant_dose": "Dose of bubble protectant in the medium",
    "rt_membrane_price": "Price of cell-filter membrane",
    "pf_maintenance_share": "Share of a cell's oxygen use that is upkeep, not growth",
    "pf_glc_kg": "Glucose Humbird's efficient cell uses per kg grown",
    "aa_intensity": "Amino acids a kilo of cells takes up (the nutrient floor)",
    "aa_bulk_price": "Price of amino acids (the nutrient floor)",
    "pf_capex_escalation": "Rise in plant construction costs since 2018",
    "pf_x_unperfused": "Density a tank reaches without perfusion",
    "pf_osm_limit": "Salt strength the cells tolerate (osmolality)",
    "neophobia_x": "How wary people are of a novel food, in the long run",
    "cult_sub_mult": "How much more price-sensitive cultivated meat is than meat in general",
    "equal_price_share": "Share of buyers who choose cultivated meat at equal price, once familiar",
    "wf_mainstream_target": "Share of mainstream meat meals where shoppers choose a whole-food plant protein instead of meat",
    "liking_sd": "How much shoppers differ in liking cultivated meat",
    "liking_tail": "How heavy the tails of that spread are (few shoppers who like it far more than most)",
    "price_insensitive_share": "Share of shoppers who respond much less to price than the others",
    "price_insensitive_response": "How strongly those price-insensitive shoppers respond to price, times other shoppers' response",
    "price_insensitive_liking": "How much more the price-insensitive shoppers like cultivated meat than other shoppers, utils",
    "markup_add": "Per-kg costs from cells to the shop shelf (forming, packing, cold chain), $ per kg",
    "retail_margin": "Retailer's gross margin, as a share of the shelf price",
    "eps_own": "Price elasticity of meat demand",
    "health_x": "Whether people see cultivated meat as healthier or less healthy",
    "income_gradient": "How price sensitivity falls with income",
    "loss_aversion": "Whether a price above meat's hurts more than a price below helps (off by default)",
    "p_conv": "Price of everyday meat",
    "premium_resistance": "How much less buyers of premium products (wagyu, sushi-grade fish) like a cultivated version, beyond what applies to any cut",
    "scaffold_frac": "Share of a cut that is plant protein, not cells",
    "process_cost": "Cost of assembling a cut, beyond what mince pays",
    "w_ratio": "Weight on the price compared with meat's",
    "theta_free_M": "Value mainstream buyers put on meat without slaughter",
    "accept_x": "How fully mainstream buyers credit cultivated meat's taste",
}

# where the value comes from, in a few words; the input's own source tag otherwise
EVIDENCE = {
    "sc_nh3_limit": "the evidence note's median, 3.5–4 mmol/L (80% interval 2–8): meat-relevant cells measured lose 10–55% of growth at 2.5–5, meat-cell processes hold 2–3, none measured at density",
    "sc_nh3_selected": "measured once, in bovine cells with glutamine replaced (Hubalek 2023): 'more than 5-fold' below the 0.70 with glutamine",
    "sc_nh3_engineered": "Humbird's enhanced cell; the best measured in meat cells is 0.14 (Hubalek 2023)",
    "sc_mass_selected_pg": "judgement between the 1.0–1.75 ng reported for chicken cells and Humbird's 3 ng",
    "sc_p_top": "vendor data sheets (vessels rated to 3–4 bar); no culture has been run at 1 bar",
    "pf_nh3_limit": "Humbird's choice within 2–10 mmol/L reported for mammalian cells; meat-relevant cells measured lose 10–55% of growth at 2.5–5 mM, none measured at density",
    "rt_membrane_life": "derived from pharma runs (fouled in 4.5 days to lasted 30); no meat-cell run; probably the generous end (median about 1,500), and read with the membrane price",
    "pf_protectant_price": "assumed: only catalogue prices ($230–260/kg) found",
    "pf_min_perfusion": "judgement within CHO measurements",
    "plant_charge_mature": "derived from Humbird's financing, at a mature industry's rates",
    "pf_antifoam_otr": "judgement: reported effects range from none to half",
    "pf_gas_velocity": "Humbird's limit; 2–9 mm/s reported",
    "pf_protectant_dose": "dense pharma cultures (`gas_flow_cap.md`)",
    "rt_membrane_price": "Humbird's ATF price; retail modules a quarter less",
    "pf_maintenance_share": "judgement from GFI and Miller 1987",
    "pf_glc_kg": "derived from Humbird's enhanced cells",
    "aa_intensity": "GFI's eight estimates, 200–650 g; the model takes the most efficient (`nutrient_floor.md`)",
    "aa_bulk_price": "GFI's feed-grade mean of 22, to low food-grade (`nutrient_floor.md`)",
    "pf_capex_escalation": "construction cost index, 2024 estimated",
    "pf_x_unperfused": "Humbird's fed-batch limit",
    "pf_osm_limit": "CHO measurements (`perfusion_rate_osmolality.md`)",
    "tc_kla_exp": "one correlation for stirred tanks (Yagi and Yoshida 1975); CHO perfusion data show almost no loss (`thick_culture.md`)",
    "tc_thin": "one CHO study at 1e8 cells/mL (Tregidgo 2023); up to 3 times at shear rates below 40 per second",
    "neophobia_x": "a judgement on long-run behaviour",
    "cult_sub_mult": "bracketed by data on close substitutes",
    "equal_price_share": "a judgement: an even split for meat buyers, the neutral start where no good data exist (since 2026-11-24; 13% of all choices before); the literature review puts the 10th, 50th and 90th percentiles at 2%, 10% and 35% (`what_drives_choice.md`)",
    "liking_sd": "fitted to the one random-parameter choice experiment, premium real meats and farmed salmon, jointly",
    "liking_tail": "fitted with the spread, jointly; the data bound it loosely (`liking_spread.profile`)",
    "price_insensitive_share": "latent-class studies: 15-35% in stated choices, probably 8-15% in purchases; fitted within that to the demand checks (`demand_checks.md` section 7)",
    "price_insensitive_response": "4-10 times between groups in purchases; fitted within that to the demand checks (`demand_checks.md` section 7)",
    "price_insensitive_liking": "two latent-class studies, read in utils: no more hostile than other shoppers (`demand_checks.md` section 7)",
    "markup_add": "fitted to USDA ERS meat spreads, plus forming",
    "retail_margin": "US meat-department margins (28–32%) and French supermarket data",
    "eps_own": "scanner-data meta-analysis",
    "health_x": "a scenario dial: no data",
    "income_gradient": "USDA demand estimates",
    "loss_aversion": "an alternative model of price, not a measured value; with it, part of the price response moves from dollars to the ratio to meat's price",
    "p_conv": "market prices",
    "premium_resistance": "assumed",
    "scaffold_frac": "assumed: the cuts sold or approved so far are 10–30% cells, and no mostly-cell cut has been shown with the texture of meat (`structuring_cost.md`)",
    "process_cost": "analogues, no study of cultivated meat: plant-protein extrusion, surimi forming, binder prices (`structuring_cost.md`)",
    "w_ratio": "judgement: how much of the price response is a ratio to meat's price rather than dollars",
    "theta_free_M": "a scenario dial: surveys disagree",
    "accept_x": "a scenario dial",
}

# what the scenarios' uncertainty bands draw (scenarios.scenario_mc and meat_market.monte_carlo)
IN_BAND = ({"plant_charge_mature", "rt_membrane_life", "pf_maintenance_share", "markup_add", "retail_margin"}
           | set(I.MC_DEMAND_INPUTS) | set(I.MC_TIER_INPUTS) | set(I.MC_CUT_INPUTS))
if value("sc_wide_bands") >= 0.5:                    # since 2026-11-16 the bands also draw the estimates the cost rests on most
    IN_BAND |= {name for _key, name in S.MC_ESTIMATES} | set(S.MC_ESTIMATE_INPUTS) | set(S.MC_SCENARIO_PRIORS.values()) | {"sc_nh3_selected", "sc_mass_selected_pg"}
PARTLY_IN_BAND = {"pf_capex_escalation": "the plant's cost is drawn, not this index"}
NOT_DRAWN = {"pf_glc_kg": "no: a trait of the cells, held by the kind-of-cells switch",
             "sc_nh3_engineered": "no: the all-favourable example assumes cells that reach it",
             "sc_p_top": "no: a design choice",
             "aa_intensity": "no: a trait of the cells, as glucose use is; the all-favourable example takes the efficient end",
             "pf_osm_limit": "no: moves the all-favourable example's median by about $0.1, at forty times the computing time",
             "loss_aversion": "no: each value re-solves the demand model's calibration",
             "liking_sd": "no: the share at equal price is set given it",
             "liking_tail": "no: the share at equal price is set given it",
             "price_insensitive_share": "no: the share at equal price is set given it",
             "price_insensitive_response": "no: the share at equal price is set given it",
             "price_insensitive_liking": "no: the share at equal price is set given it",
             "theta_free_M": "no: part of the share at equal price, which is drawn",
             "accept_x": "no: part of the share at equal price, which is drawn (left the bands on 2026-11-20)",
             "neophobia_x": "no: part of the share at equal price, which is drawn",
             "health_x": "no: part of the share at equal price, which is drawn",
             "w_ratio": "no: each value re-solves the demand model's calibration",
             "income_gradient": "no: each value re-solves the demand model's calibration",
             "p_conv": "no: an observed price"}
# inputs left out of the tables, and why
EXCLUDE = {"pf_gas_velocity": "The gas flow the tank takes is a scenario switch (2, 4 or 6 mm/s). The input of that name is "
                              "also the reference speed of Humbird's oxygen figure, so moving it alone rescales that figure "
                              "({gas_lo} to {gas_hi} in the low-lactate example) without changing any tank; it is left out.",
           "pf_mature_h": "Maturation, the hours the cells spend in the tank without growing before harvest, is a choice of "
                          "product, not an estimate. The products near market are bulk cell mass and take none; 4 to 28 days "
                          "to mature muscle or fat would take the low-lactate example from {mature_0} to {mature_4} (4 days) or "
                          "{mature_28} (28 days). It is a lever on the page; it is left out here.",
           **{k: None for k in ("sc_medium_mid", "sc_gf_part", "sc_hazard_cm", "sc_gas_mid", "sc_td_central", "sc_td_fast",
                                "sc_restart_base", "sc_hazard_mid", "sc_medium_high")}}
EXCLUDE_NOTE = ("Also left out: the settings of the scenario switches themselves (medium price, growth factors bought, runs lost, "
                "gas flow, doubling time, restart time). \"What to prioritise\" shows what each switch is worth.")

# demand inputs applied as overrides after the demand model is calibrated, as the uncertainty band applies them
_SHARE_OVERRIDES = {"neophobia_x", "health_x", "eps_own", "cult_sub_mult", "theta_free_M", "accept_x"}
_PENETRATION_ARGS = {"markup_add", "retail_margin", "premium_resistance"}
# a cut's make-up: they move the share (a cut's cost and how much shoppers like it), not the cost of a kilo of cells
_CUT_ARGS = set(I.MC_CUT_INPUTS)                     # scaffold_frac, process_cost


def share_at(cost: float, region: str = "global", **over) -> float:
    """Long-run share of meat by weight, %, at cells costing `cost`, with demand inputs set by `over` (input names). Inputs
    the band draws are applied the way `meat_market.monte_carlo` applies them; other demand inputs re-make the demand model."""
    fields = {f.name for f in dataclasses.fields(DemandParams)}
    rebuild = {k: v for k, v in over.items() if k in fields and k not in _SHARE_OVERRIDES}
    pr = DemandParams(**rebuild) if rebuild else S._demand()
    eps = over.get("eps_own", pr.eps_own)
    income = mm.REGION_INCOME[region]

    cell_share = 1.0 - over.get("scaffold_frac", value("scaffold_frac"))     # the cut's cost and its liking: one figure for both

    def share_of(mt, R, base, res):
        return share(R, pr, theta_free_M=over.get("theta_free_M", 0.0), accept_x=over.get("accept_x", 1.0),
                     tier_offset=mm.tier_offset(mt, base, res, pr, cell_share), eps_own=eps,
                     income=income, p_ref=mt.p_conv, neophobia_x=over.get("neophobia_x"), health_x=over.get("health_x"),
                     kappa=over.get("cult_sub_mult"), which="x_meat")
    markup = over.get("markup_add", value("markup_add"))
    res = over.get("premium_resistance", value("premium_resistance"))
    margin = over.get("retail_margin", value("retail_margin"))
    return mm._rollup(mm.MARKETS[region], cost, markup, res, share_of, margin, cell_share=cell_share,
                      assembly=over.get("process_cost"))[1] * 100.0


def _cost_at(key: str, inp: str, x: float) -> float:
    """A scenario's cost with one input set to x (inputs read when scenarios.py is imported are handled by a reload)."""
    import importlib, pathlib
    v = I.REGISTRY[inp]
    reload = re.search(r'value\("' + re.escape(inp) + r'"\)', pathlib.Path(S.__file__).read_text()) is not None
    I.REGISTRY[inp] = replace(v, value=x)
    try:
        if reload:
            importlib.reload(S)
        return _cost(key)
    finally:
        I.REGISTRY[inp] = v
        if reload:
            importlib.reload(S)


def excluded_reasons() -> list:
    """EXCLUDE's reasons with their figures computed now (since 2026-11-21; they were typed in and went stale)."""
    if "excl" in _CACHE:
        return _CACHE["excl"]
    g = I.REGISTRY["pf_gas_velocity"]
    m = lambda x: f"${x:.2f}"
    fig = {"gas_lo": m(_cost_at("central", "pf_gas_velocity", g.lo)), "gas_hi": m(_cost_at("central", "pf_gas_velocity", g.hi)),
           "mature_0": m(_cost("central")), "mature_4": m(_cost_at("central", "pf_mature_h", 4 * 24.0)),
           "mature_28": m(_cost_at("central", "pf_mature_h", 28 * 24.0))}
    _CACHE["excl"] = [why.format(**fig) for why in EXCLUDE.values() if why]
    return _CACHE["excl"]


def _cost(key: str) -> float:
    return fp.explore(**S.explore_kwargs(S.SCENARIOS[key].choice))["total"]


def _ranged() -> list:
    return [(k, v) for k, v in I.REGISTRY.items()
            if v.lo is not None and v.hi is not None and v.lo != v.hi and isinstance(v.value, (int, float)) and k not in EXCLUDE]


def _tag(k: str) -> str:
    m = re.match(r"\[([^\]]+)\]", (I.REGISTRY[k].source or "").strip())
    return m.group(1) if m else "no source tag"


def _band(k: str) -> str:
    if k in IN_BAND:
        return "yes"
    if k in PARTLY_IN_BAND:
        return "partly: " + PARTLY_IN_BAND[k]
    return NOT_DRAWN.get(k, "**no**")


_CACHE: dict = {}


def cost_drivers() -> list:
    """Inputs that move the low-lactate example's or the all-favourable example's cost by at least COST_MIN, largest swing in the low-lactate example first. Each row:
    {key, lo, hi, value, central: (at lo, at hi), best: (at lo, at hi), share: (the low-lactate example's share at lo, at hi)}."""
    if "cost" in _CACHE:
        return _CACHE["cost"]
    rows = []
    # The scenarios' settings read their inputs when scenarios.py is imported, so moving one in the registry changes nothing
    # until the module is read again (audit 2026-11-19: the scan showed no swing for any of them). Reload for those inputs.
    import importlib, pathlib
    at_import = set(re.findall(r'value\("([A-Za-z0-9_]+)"\)', pathlib.Path(S.__file__).read_text()))
    for k, v in _ranged():
        out = []
        for end in (v.lo, v.hi):
            I.REGISTRY[k] = replace(v, value=end)
            try:
                if k in at_import:
                    importlib.reload(S)
                out.append((_cost("central"), _cost("best")))
            finally:
                I.REGISTRY[k] = v
        if k in at_import:
            importlib.reload(S)
        c, b = (out[0][0], out[1][0]), (out[0][1], out[1][1])
        if max(abs(c[1] - c[0]), abs(b[1] - b[0])) >= COST_MIN:
            rows.append({"key": k, "lo": v.lo, "hi": v.hi, "value": v.value, "central": c, "best": b})
    rows.sort(key=lambda r: -abs(r["central"][1] - r["central"][0]))
    for r in rows:
        r["share"] = tuple(S.shares(c)["global"] for c in r["central"])
    _CACHE["cost"] = rows
    return rows


def demand_inputs() -> list:
    """The demand inputs that have a range: the demand model's own fields, the spread to the shelf, premium resistance,
    a cut's make-up (its plant-protein share and assembly cost), and the two scenario dials the headline holds at their
    neutral settings."""
    fields = {f.name for f in dataclasses.fields(DemandParams)}
    keys = [k for k, _v in _ranged() if k in fields or k in _PENETRATION_ARGS or k in _CUT_ARGS]
    return keys + [k for k in ("theta_free_M", "accept_x") if k not in keys and k in I.REGISTRY]


def demand_drivers() -> list:
    """Demand inputs that move the share by at least SHARE_MIN at the low-lactate example's or the all-favourable example's cost, largest at the
    all-favourable example first. Each row: {key, lo, hi, value, central: (share at lo, at hi), best: (share at lo, at hi)}."""
    if "demand" in _CACHE:
        return _CACHE["demand"]
    cc, cb = _cost("central"), _cost("best")
    rows = []
    for k in demand_inputs():
        v = I.REGISTRY[k]
        c = tuple(share_at(cc, **{k: e}) for e in (v.lo, v.hi))
        b = tuple(share_at(cb, **{k: e}) for e in (v.lo, v.hi))
        if abs(c[1] - c[0]) >= SHARE_MIN[0] or abs(b[1] - b[0]) >= SHARE_MIN[1]:
            rows.append({"key": k, "lo": v.lo, "hi": v.hi, "value": v.value, "central": c, "best": b})
    rows.sort(key=lambda r: -abs(r["best"][1] - r["best"][0]))
    _CACHE["demand"] = rows
    return rows


def summary() -> dict:
    cost, demand = cost_drivers(), demand_drivers()
    cc, cb = _cost("central"), _cost("best")
    n = len(_ranged())
    return {"inputs": len(I.REGISTRY), "ranged": n, "central": cc, "best": cb,
            "central_share": S.shares(cc)["global"], "best_share": S.shares(cb)["global"],
            "cost_rows": cost, "demand_rows": demand,
            "over_3": sum(abs(r["central"][1] - r["central"][0]) > 3 for r in cost),
            "not_in_band": [r["key"] for r in cost + demand if r["key"] not in IN_BAND],
            "not_in_band_open": [r["key"] for r in cost + demand if r["key"] not in IN_BAND and r["key"] not in NOT_DRAWN
                                 and r["key"] not in PARTLY_IN_BAND],
            "central_share_span": (min(min(r["central"]) for r in demand), max(max(r["central"]) for r in demand)),
            "best_share_span": (min(min(r["best"]) for r in demand), max(max(r["best"]) for r in demand))}


# ----------------------------------------------------------------------------
def _num(x: float) -> str:
    return f"{x:g}"


def markdown_cost() -> str:
    out = ["| input | its range (model's value) | Low-lactate example, $/kg | The low-lactate example's share of world meat | All-favourable example, $/kg | "
           "where the value comes from | in the uncertainty band? |", "|---|---|---|---|---|---|---|"]
    for r in cost_drivers():
        k, u = r["key"], I.REGISTRY[r["key"]].unit
        out.append(f"| {PLAIN[k]} | {_num(r['lo'])}–{_num(r['hi'])} {u} ({_num(r['value'])}) | "
                   f"${r['central'][0]:.1f} to ${r['central'][1]:.1f} | {S.pct_num(r['share'][0])}% to {S.pct_num(r['share'][1])}% | "
                   f"${r['best'][0]:.1f} to ${r['best'][1]:.1f} | {EVIDENCE.get(k, _tag(k))} | {_band(k)} |")
    out += ["", *(f"*Left out: {why}*" for why in excluded_reasons()), f"*{EXCLUDE_NOTE}*"]
    return "\n".join(out)


def markdown_demand() -> str:
    out = ["| input | its range (model's value) | share at the low-lactate example's cost | share at the all-favourable example's cost | "
           "where the value comes from | in the uncertainty band? |", "|---|---|---|---|---|---|"]
    for r in demand_drivers():
        k, u = r["key"], I.REGISTRY[r["key"]].unit
        out.append(f"| {PLAIN[k]} | {_num(r['lo'])} to {_num(r['hi'])} {u} ({_num(r['value'])}) | "
                   f"{S.pct_num(r['central'][0])}% to {S.pct_num(r['central'][1])}% | {r['best'][0]:.1f}% to {r['best'][1]:.1f}% | "
                   f"{EVIDENCE.get(k, _tag(k))} | {_band(k)} |")
    return "\n".join(out)


def main() -> None:
    if "--markdown" in sys.argv:
        print(markdown_cost() + "\n\n" + markdown_demand())
        return
    s = summary()
    print(f"{s['inputs']} inputs, {s['ranged']} with a range. The low-lactate example ${s['central']:.2f} ({s['central_share']:.2f}%), "
          f"best ${s['best']:.2f} ({s['best_share']:.2f}%).")
    print(f"{len(s['cost_rows'])} move a cost by ${COST_MIN:g} or more; {s['over_3']} move the low-lactate example by more than $3.")
    print(f"{len(s['demand_rows'])} demand inputs move the share by {SHARE_MIN[0]:g} / {SHARE_MIN[1]:g} points or more.")
    print(f"Share at the low-lactate example's cost, across them: {s['central_share_span'][0]:.2f}–{s['central_share_span'][1]:.2f}%; "
          f"at the all-favourable example's: {s['best_share_span'][0]:.1f}–{s['best_share_span'][1]:.1f}%.")
    print("Not in the uncertainty band:", ", ".join(s["not_in_band"]))
    print()
    print(markdown_cost())
    print()
    print(markdown_demand())


if __name__ == "__main__":
    main()
