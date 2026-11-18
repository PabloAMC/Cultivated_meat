#!/usr/bin/env python3
"""
answer_rests_on.py — which inputs the answer actually rests on, and how good the evidence for each is.

The model has about 500 inputs. Most serve side studies or a detail of the tank, and move the headline by cents. This module
finds the few that matter: it moves every input that has a range to the low and then the high end of that range, one at a
time, and records what happens to

  * the cost of a kilo of cells in Central and in the best case (each scenario's tank design held as it is), and
  * the long-run share of world meat at Central's cost and at the best case's cost.

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

COST_MIN = 1.0           # $/kg in Central or the best case
SHARE_MIN = (0.2, 2.0)   # percentage points of world meat, at Central's cost and at the best case's cost

# plain names for the inputs that can appear in the tables (the test checks every row has one)
PLAIN = {
    "pf_nh3_limit": "Ammonia the cells tolerate in the tank",
    "rt_membrane_life": "Litres a m² of cell filter passes before it is replaced",
    "pf_protectant_price": "Price of the bubble protectant (poloxamer 188), bought by the tonne",
    "pf_min_perfusion": "Least medium flow the cells need for everything but ammonia and lactate",
    "plant_charge_mature": "Yearly charge on the plant's capital (financing and recovery)",
    "pf_antifoam_otr": "Oxygen transfer the sparger keeps with antifoam present",
    "pf_gas_velocity": "Gas flow the tank can take (superficial velocity)",
    "pf_protectant_dose": "Dose of bubble protectant in the medium",
    "rt_membrane_price": "Price of cell-filter membrane",
    "pf_maintenance_share": "Share of a cell's oxygen use that is upkeep, not growth",
    "pf_glc_kg": "Glucose the engineered cells use per kg grown",
    "pf_capex_escalation": "Rise in plant construction costs since 2018",
    "pf_x_unperfused": "Density a tank reaches without perfusion",
    "pf_osm_limit": "Salt strength the cells tolerate (osmolality)",
    "neophobia_x": "How wary people are of a novel food, in the long run",
    "cult_sub_mult": "How much more price-sensitive cultivated meat is than meat in general",
    "markup_add": "Per-kg costs from cells to the shop shelf (forming, packing, cold chain), $ per kg",
    "retail_margin": "Retailer's gross margin, as a share of the shelf price",
    "eps_own": "Price elasticity of meat demand",
    "health_x": "Whether people see cultivated meat as healthier or less healthy",
    "income_gradient": "How price sensitivity falls with income",
    "loss_aversion": "Whether a price above meat's hurts more than a price below helps (off by default)",
    "p_conv": "Price of everyday meat",
    "premium_resistance": "How much steaks and premium cuts resist cultivated meat, against mince",
    "w_ratio": "Weight on the price compared with meat's",
    "theta_free_M": "Value mainstream buyers put on meat without slaughter",
    "accept_x": "How fully mainstream buyers credit cultivated meat's taste",
}

# where the value comes from, in a few words; the input's own source tag otherwise
EVIDENCE = {
    "pf_nh3_limit": "Humbird's choice within 2–10 mmol/L reported for mammalian cells; unadapted meat-relevant cells lose 10–55% of growth at 2.5–5 mM, none measured at density",
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
    "pf_capex_escalation": "construction cost index, 2024 estimated",
    "pf_x_unperfused": "Humbird's fed-batch limit",
    "pf_osm_limit": "CHO measurements (`perfusion_rate_osmolality.md`)",
    "neophobia_x": "a judgement on long-run behaviour",
    "cult_sub_mult": "bracketed by data on close substitutes",
    "markup_add": "fitted to USDA ERS meat spreads, plus forming",
    "retail_margin": "US meat-department margins (28–32%) and French supermarket data",
    "eps_own": "scanner-data meta-analysis",
    "health_x": "a scenario dial: no data",
    "income_gradient": "USDA demand estimates",
    "loss_aversion": "an alternative model of price, not a measured value; with it, part of the price response moves from dollars to the ratio to meat's price",
    "p_conv": "market prices",
    "premium_resistance": "assumed",
    "w_ratio": "judgement: how much of the price response is a ratio to meat's price rather than dollars",
    "theta_free_M": "a scenario dial: surveys disagree",
    "accept_x": "a scenario dial",
}

# what the scenarios' uncertainty bands draw (scenarios.scenario_mc and meat_market.monte_carlo)
IN_BAND = ({"plant_charge_mature", "rt_membrane_life", "pf_maintenance_share", "markup_add", "retail_margin"}
           | set(I.MC_DEMAND_INPUTS) | set(I.MC_TIER_INPUTS))
if value("sc_wide_bands") >= 0.5:                    # since 2026-11-16 the bands also draw the estimates the cost rests on most
    IN_BAND |= {name for _key, name in S.MC_ESTIMATES} | set(S.MC_ESTIMATE_INPUTS)
PARTLY_IN_BAND = {"pf_capex_escalation": "the plant's cost is drawn, not this index"}
NOT_DRAWN = {"pf_glc_kg": "no: a trait of the cells, held by the kind-of-cells switch",
             "pf_osm_limit": "no: moves the best case's median by about $0.1, at forty times the computing time",
             "loss_aversion": "no: each value re-solves the demand model's calibration",
             "w_ratio": "no: each value re-solves the demand model's calibration",
             "income_gradient": "no: each value re-solves the demand model's calibration",
             "p_conv": "no: an observed price"}
# inputs left out of the tables, and why
EXCLUDE = {"pf_gas_velocity": "The gas flow the tank takes is a scenario switch (2, 4 or 6 mm/s). The input of that name is "
                              "also the reference speed of Humbird's oxygen figure, so moving it alone rescales that figure "
                              "($27.7 to $31.9 in Central) without changing any tank; it is left out."}

# demand inputs applied as overrides after the demand model is calibrated, as the uncertainty band applies them
_SHARE_OVERRIDES = {"neophobia_x", "health_x", "eps_own", "cult_sub_mult", "theta_free_M", "accept_x"}
_PENETRATION_ARGS = {"markup_add", "retail_margin", "premium_resistance"}


def share_at(cost: float, region: str = "global", **over) -> float:
    """Long-run share of meat by weight, %, at cells costing `cost`, with demand inputs set by `over` (input names). Inputs
    the band draws are applied the way `meat_market.monte_carlo` applies them; other demand inputs re-make the demand model."""
    fields = {f.name for f in dataclasses.fields(DemandParams)}
    rebuild = {k: v for k, v in over.items() if k in fields and k not in _SHARE_OVERRIDES}
    pr = DemandParams(**rebuild) if rebuild else S._demand()
    eps = over.get("eps_own", pr.eps_own)
    income = mm.REGION_INCOME[region]

    def share_of(mt, R, base, res):
        return share(R, pr, theta_free_M=over.get("theta_free_M", 0.0), accept_x=over.get("accept_x", 1.0),
                     tier_offset=mm.tier_authenticity(mt, base, res, None), eps_own=eps * mm.tier_eps_mult(mt, base, res),
                     income=income, p_ref=mt.p_conv, neophobia_x=over.get("neophobia_x"), health_x=over.get("health_x"),
                     kappa=over.get("cult_sub_mult"))
    markup = over.get("markup_add", value("markup_add"))
    res = over.get("premium_resistance", value("premium_resistance"))
    margin = over.get("retail_margin", value("retail_margin"))
    return mm._rollup(mm.MARKETS[region], cost, markup, res, share_of, margin)[1] * 100.0


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
    """Inputs that move Central's or the best case's cost by at least COST_MIN, largest swing in Central first. Each row:
    {key, lo, hi, value, central: (at lo, at hi), best: (at lo, at hi), share: (Central's share at lo, at hi)}."""
    if "cost" in _CACHE:
        return _CACHE["cost"]
    rows = []
    for k, v in _ranged():
        out = []
        for end in (v.lo, v.hi):
            I.REGISTRY[k] = replace(v, value=end)
            try:
                out.append((_cost("central"), _cost("best")))
            finally:
                I.REGISTRY[k] = v
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
    and the two scenario dials the headline holds at their neutral settings."""
    fields = {f.name for f in dataclasses.fields(DemandParams)}
    keys = [k for k, _v in _ranged() if k in fields or k in _PENETRATION_ARGS]
    return keys + [k for k in ("theta_free_M", "accept_x") if k not in keys and k in I.REGISTRY]


def demand_drivers() -> list:
    """Demand inputs that move the share by at least SHARE_MIN at Central's or the best case's cost, largest at the best
    case first. Each row: {key, lo, hi, value, central: (share at lo, at hi), best: (share at lo, at hi)}."""
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
    out = ["| input | its range (model's value) | Central, $/kg | Central's share of world meat | best case, $/kg | "
           "where the value comes from | in the uncertainty band? |", "|---|---|---|---|---|---|---|"]
    for r in cost_drivers():
        k, u = r["key"], I.REGISTRY[r["key"]].unit
        out.append(f"| {PLAIN[k]} | {_num(r['lo'])}–{_num(r['hi'])} {u} ({_num(r['value'])}) | "
                   f"${r['central'][0]:.1f} to ${r['central'][1]:.1f} | {r['share'][0]:.1f}% to {r['share'][1]:.1f}% | "
                   f"${r['best'][0]:.1f} to ${r['best'][1]:.1f} | {EVIDENCE.get(k, _tag(k))} | {_band(k)} |")
    out += ["", *(f"*Left out: {why}*" for why in EXCLUDE.values())]
    return "\n".join(out)


def markdown_demand() -> str:
    out = ["| input | its range (model's value) | share at Central's cost | share at the best case's cost | "
           "where the value comes from | in the uncertainty band? |", "|---|---|---|---|---|---|"]
    for r in demand_drivers():
        k, u = r["key"], I.REGISTRY[r["key"]].unit
        out.append(f"| {PLAIN[k]} | {_num(r['lo'])} to {_num(r['hi'])} {u} ({_num(r['value'])}) | "
                   f"{r['central'][0]:.1f}% to {r['central'][1]:.1f}% | {r['best'][0]:.1f}% to {r['best'][1]:.1f}% | "
                   f"{EVIDENCE.get(k, _tag(k))} | {_band(k)} |")
    return "\n".join(out)


def main() -> None:
    if "--markdown" in sys.argv:
        print(markdown_cost() + "\n\n" + markdown_demand())
        return
    s = summary()
    print(f"{s['inputs']} inputs, {s['ranged']} with a range. Central ${s['central']:.2f} ({s['central_share']:.2f}%), "
          f"best ${s['best']:.2f} ({s['best_share']:.2f}%).")
    print(f"{len(s['cost_rows'])} move a cost by ${COST_MIN:g} or more; {s['over_3']} move Central by more than $3.")
    print(f"{len(s['demand_rows'])} demand inputs move the share by {SHARE_MIN[0]:g} / {SHARE_MIN[1]:g} points or more.")
    print(f"Share at Central's cost, across them: {s['central_share_span'][0]:.2f}–{s['central_share_span'][1]:.2f}%; "
          f"at the best case's: {s['best_share_span'][0]:.1f}–{s['best_share_span'][1]:.1f}%.")
    print("Not in the uncertainty band:", ", ".join(s["not_in_band"]))
    print()
    print(markdown_cost())
    print()
    print(markdown_demand())


if __name__ == "__main__":
    main()
