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

PUT RIGHT ON 2026-11-21: the draws below lagged the scenarios; now the growth-factor draw goes inside a complete medium's price,
a medium at the nutrient floor gets no price per litre, and the ammonia and lactate the cells tolerate (the scenarios' ranges for
the low-lactate example, Humbird's for the all-favourable example, which takes his values), the cells bubbles kill and the harvest
recovery are drawn (after the others, so their draws are unchanged). The all-favourable example's membrane life is still passed
to explore directly (dialyser-grade fibres), so the membrane-life draw does not reach it. The history:

STALE SINCE 2026-11-19 (found in the audit-batch repin; the draws were left as they were, so read the figures with this):
  * The low-lactate example's medium is now a complete medium with its growth factors inside the price (scenarios.explore_kwargs sets
    `gf_in_medium` and `growth_factors` = 0). The growth-factor draw here still goes to `growth_factors`, so it is bought on
    top: the growth factors are counted twice, about $5 at the low-lactate example's median.
  * The all-favourable example's medium is now at the nutrient floor (no price per litre). The medium-price draw here still gives it
    $0.15-0.50 a litre.
  * The ammonia the cells tolerate (sc_nh3_limit, 2-8 mmol/L, which every scenario now passes to explore and
    scenarios.scenario_mc draws) is not drawn here.
  With the three put right (a side calculation on the model of 2026-11-19, 4,000 draws; the amino-acid price behind the floor
  drawn too): the low-lactate example $28 / $38 / $58 at the 10th, 50th and 90th percentile, against $34 / $46 / $65 as drawn
  here then; the all-favourable example $11 / $14 / $22, against $14 / $19 / $28. Both were then close to the scenario bands of
  that day ($27 / $37 / $57 and $11 / $14 / $20).
  2026-11-20 (final model): as drawn here the low-lactate example is $50 / $64 / $86 at the 10th, 50th and 90th percentile
  (4,000 draws; its point, $49.50, sits at about the 10th) and the all-favourable example $9 / $11 / $15 (its point, $7.62, sits
  below the 1st). The all-favourable example takes the favourable end of every lever (scenarios.all_favourable): Humbird's
  0.054 mol of ammonia a kilo, no runs lost, the medium at the nutrient floor, dialyser-grade membranes. The draws here put a
  price per litre on its medium ($0.15-0.50), draw runs lost and draw its ammonia from sc_nh3_engineered's range, so almost
  every draw costs more than the point; its membrane life is passed to explore directly, so the membrane-life draw does not
  reach it. The side calculation above was not redone. Not drawn here either: the lactate the cells tolerate (sc_lac_limit),
  the culture bubbles kill (ge_kill_protected) and the harvest recovery (pf_harvest_recovery). Membrane life (most likely
  2,415 L/m2) ranks first for the low-lactate example, ahead of the ammonia the cells make.

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
# 2026-11-21: what the draws lagged (the docstring's list), now drawn. The waste the cells tolerate and the cells bubbles kill, as
# explore() arguments: the scenarios' own ranges for the low-lactate example, Humbird's for the all-favourable example (it takes
# his 5 and 50 mmol/L)
LIMIT_INPUTS = {
    "central": {"nh3_limit": "sc_nh3_limit", "lac_limit": "sc_lac_limit", "kill": "ge_kill_protected"},
    "best": {"nh3_limit": "pf_nh3_limit", "lac_limit": "pf_lac_limit", "kill": "ge_kill_protected"},
}
# inputs patched into the registry (the filter loop, plant and financing), with their priors; the harvest recovery since 2026-11-21
PATCH_INPUTS = ("rt_membrane_life", "rt_flux_lmh", "rt_membrane_price", "rt_tff_hw", "rt_install", "plant_charge_mature",
                "pf_maintenance_share", "pf_harvest_recovery")
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
    for arg, name in LIMIT_INPUTS[key].items():         # drawn last (2026-11-21), so the draws above are unchanged
        d[arg] = _tri(rng, name, n)
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
            if k in CELL_INPUTS[key] or k in LIMIT_INPUTS[key]:
                if k == "growth_factors":
                    # a complete medium carries its growth factors inside its price (scenarios.explore_kwargs): the draw goes
                    # there, not on top (2026-11-21; it was bought twice)
                    if base.get("gf_in_medium", 0.0) > 0.0:
                        kw["gf_in_medium"] = x
                    elif "growth_factors" in base and base["growth_factors"] > 0.0:
                        kw["growth_factors"] = x
                    continue
                if k == "medium_price" and base.get("medium_price", 0.15) == 0.0:
                    continue                             # a medium at the nutrient floor has no price per litre to draw
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
