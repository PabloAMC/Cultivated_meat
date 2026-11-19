#!/usr/bin/env python3
"""
audit.py — how uncertain is a scenario's cost, with every documented range drawn at once?

Why
---
`scenarios.scenario_mc` draws only the plant estimate, financing, the filter's capital, upkeep, medium price and loss rate, and
holds the scenario's switches. Each switch setting is itself an uncertain number (waste, doubling time, gas, growth factors,
restart), and since the filter loop became the default so are its flux, membrane price, hardware and membrane life. This module
draws all of them together from the triangular priors in inputs.py (low, mode, high) and reports the spread of the scenario's
cost, the chance it falls at or below stated prices, and which inputs move it.

Held fixed (no documented range): the tank design, the 20 m3 size, the plant class, the density limit. Draws are independent; good
cell traits tend to come together (floor_physics.CELL_QUALITY), which would fatten both tails.

STALE SINCE 2026-11-19 (found in the audit-batch repin; the draws were left as they were, so read the figures with this):
  * The low-lactate example's medium is now a complete medium with its growth factors inside the price (scenarios.explore_kwargs sets
    `gf_in_medium` and `growth_factors` = 0). The growth-factor draw here still goes to `growth_factors`, so it is bought on
    top: the growth factors are counted twice, about $5 at the low-lactate example's median.
  * The all-favourable example's medium is now at the nutrient floor (no price per litre). The medium-price draw here still gives it
    $0.15-0.50 a litre.
  * The ammonia the cells tolerate (sc_nh3_limit, 2-8 mmol/L, which every scenario now passes to explore and
    scenarios.scenario_mc draws) is not drawn here.
  With the three put right (a side calculation, 4,000 draws; the amino-acid price behind the floor drawn too): the low-lactate example
  $28 / $38 / $58 at the 10th, 50th and 90th percentile, against $34 / $46 / $65 as drawn here; the all-favourable example $11 / $14 / $22,
  against $14 / $19 / $28. Both are then close to the scenario bands ($27 / $37 / $57 and $11 / $14 / $20).

Run
---
    python audit.py
"""
from __future__ import annotations

import numpy as np

import floor_physics as fp
import retention
import scenarios as S
from inputs import REGISTRY, draw, prior, value
from price_ratio import shelf_price, cost_from_shelf

FLAT_MARKUP = 5.0   # $/kg, the model's flat markup before 2026-11-18

# explore() argument -> the input that gives its range, per scenario switch setting
CELL_INPUTS = {
    "central": {"nh3_kg": "sc_nh3_selected", "lac_yield": "sc_lac_selected", "mass_pg": "sc_mass_selected_pg",
                "doubling_h": "sc_td_central", "gas_velocity": "sc_gas_mid", "hazard": "sc_hazard_cm",
                "restart_fail_days": "sc_restart_base", "growth_factors": "sc_gf_part", "medium_price": "sc_medium_mid"},
    "best": {"nh3_kg": "sc_nh3_engineered", "lac_yield": "sc_lac_engineered",
             "hazard": "sc_hazard_mid", "restart_fail_days": "sc_restart_base", "medium_price": "sc_medium_mid"},
}
# inputs patched into the registry (the filter loop, plant and financing), with their priors
PATCH_INPUTS = ("rt_membrane_life", "rt_flux_lmh", "rt_membrane_price", "rt_tff_hw", "rt_install", "plant_charge_mature",
                "pf_maintenance_share")
PLANT_X = "capex_x"                                  # scenarios.MC_PRIORS: the plant estimate's accuracy


def _tri(rng, name: str, n: int) -> np.ndarray:
    return draw(name, rng, n)               # inputs.draw: THE one sampler (triangular unless the input says otherwise)


def draws(key: str, n: int = 1000, seed: int = 0) -> dict:
    """{input name: array of n draws} for a scenario ('central' or 'best')."""
    rng = np.random.default_rng(seed)
    d = {}
    for arg, name in CELL_INPUTS[key].items():
        d[arg] = _tri(rng, name, n)
    for name in PATCH_INPUTS:
        d[name] = _tri(rng, name, n)
    d[PLANT_X] = rng.triangular(*S.MC_PRIORS["capex_x"], n)
    return d


def run(key: str, n: int = 1000, seed: int = 0) -> dict:
    """Cost of the scenario for each draw: {'total': array, 'draws': {...}}."""
    d = draws(key, n, seed)
    base = S.explore_kwargs(S.SCENARIOS[key].choice)
    total = np.empty(n)
    for i in range(n):
        kw = dict(base)
        patch = {}
        for k, v in d.items():
            x = float(v[i])
            if k in CELL_INPUTS[key]:
                if k == "growth_factors" and "growth_factors" not in base:
                    continue
                kw[k] = x
            elif k == PLANT_X:
                kw["capex_x"] = x
            elif k == "plant_charge_mature":
                kw["charge"] = x
            elif k == "pf_maintenance_share":
                kw["maintenance_share"] = x
            else:
                patch[k] = x
        with retention._with(patch):
            total[i] = fp.explore(**kw)["total"]
    return {"total": total, "draws": d}


def summary(key: str, n: int = 1000, seed: int = 0, targets=(7.0, 12.0, 18.0, 26.64)) -> dict:
    r = run(key, n, seed)
    t = r["total"]
    point = S.run(S.SCENARIOS[key].choice)["total"]
    rank = lambda a: np.argsort(np.argsort(a))
    rho = {k: float(np.corrcoef(rank(v), rank(t))[0, 1]) for k, v in r["draws"].items()}
    return {"point": point, "p10": float(np.percentile(t, 10)), "p50": float(np.percentile(t, 50)), "p90": float(np.percentile(t, 90)),
            "mean": float(t.mean()), "point_percentile": float(np.mean(t <= point)),
            "at_or_below": {x: float(np.mean(t <= x)) for x in targets},
            "rank": dict(sorted(rho.items(), key=lambda kv: -abs(kv[1]))), "total": t}


def retail(cost: float, form: str = "model") -> float:
    """Shelf price of a kilo of product from a kilo of cells, $/kg. 'model' is the model's since 2026-11-18: per-kg costs
    plus the retailer's percentage margin, (cost + markup_add) / (1 - retail_margin). 'flat' is the model's rule before
    then, cost + $5. 'proportional' treats the whole wholesale-to-retail spread as a share of the retail price:
    (cost + processing) / (1 - share), with the share at 42-65% (research_notes/retail_markup_form.md)."""
    if form == "model":
        return shelf_price(cost)
    if form == "flat":
        return cost + FLAT_MARKUP
    return (cost + value("au_processing")) / (1.0 - value("au_retail_share"))


def parity_cost(form: str = "model", p_conv: float | None = None) -> float:
    """The cost of cells at which the shelf price equals conventional meat's."""
    p = value("p_conv") if p_conv is None else p_conv
    if form == "model":
        return cost_from_shelf(p)
    if form == "flat":
        return p - FLAT_MARKUP
    return p * (1.0 - value("au_retail_share")) - value("au_processing")


def main() -> None:
    for key in ("central", "best"):
        s = summary(key)
        print(f"  {key}: point ${s['point']:.2f}; P10 ${s['p10']:.2f}  P50 ${s['p50']:.2f}  P90 ${s['p90']:.2f}; the point estimate sits at the "
              f"{s['point_percentile'] * 100:.0f}th percentile")
        print("    P(cost <= $): " + ", ".join(f"{x:g}: {p:.0%}" for x, p in s["at_or_below"].items()))
        print("    what moves it (rank correlation): " + ", ".join(f"{k} {v:+.2f}" for k, v in list(s["rank"].items())[:8]))


if __name__ == "__main__":
    main()
