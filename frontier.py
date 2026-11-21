#!/usr/bin/env python3
"""
frontier.py — the step-by-step path from Humbird's design to the all-favourable case, and what each lever is worth.

Why
---
The model has ONE most favourable case, `scenarios.all_favourable()`: for every lever of the engine, the most favourable value
among this model's own favourable end, Humbird's design and what any published study assumes without breaking a named limit
(study_assumptions.py). It is the all-favourable example (`scenarios.SCENARIOS["best"]`) and
the page's "best level known". Until 2026-11-20 this module kept a second one (a ladder from the low-lactate example to "every
lever at its limit", $7.86), and the all-favourable example ($18.7) cost more than Humbird's design ($16.0), which made no sense:
the example did not take the levers on which his design is the more favourable (a 3 ng cell, 5 mmol/L of ammonia and 50 of
lactate tolerated, no lost runs).

This module now only shows the path. It starts from Humbird's design as this model prices it (`scenarios.reference()`, with his
cell written as its four traits) and moves one lever at a time to its value in the all-favourable case, keeping each one moved.
The last row IS `scenarios.all_favourable()`: the same explore() arguments, so the same number.

The path starts from Humbird's design, not from the low-lactate example, because every step is then one lever made more
favourable. From the low-lactate example half the steps would be "take Humbird's value", and the first rows would mix two things.

The order matters (the tank design pays only once the filter is cheap), so the path runs: the cells, the plant, the device that
holds the cells back, the oxygen level, the tank design, then the levers that change nothing at this point and why.

Run
---
    python frontier.py
"""
from __future__ import annotations

import floor_physics as fp
import nutrient_floor
import retention
import scenarios as S
from inputs import value

HOURS = fp.HOURS

# explore() arguments at which the all-favourable case and Humbird's design agree: the start of the path sets them, with his cell
# written as its four traits (scenarios.HUMBIRD_TRAITS) so that the later steps change one thing each
_START = ("mode", "nh3_kg", "lac_yield", "glc_balance", "nh3_limit", "lac_limit", "gas_velocity", "hazard",
          "restart_fail_days", "growth_factors")


def _size() -> float:
    """The all-favourable case's tank size, m3 (its own vm_str_m3 unless it takes a published size)."""
    from inputs import value
    return float(S.all_favourable()["kw"].get("vessel_m3", value("vm_str_m3")))


def steps() -> list:
    """(name, the explore() arguments the step sets to their all-favourable value, evidence) for each lever, from Humbird's design."""
    return [
        ("Humbird's design: his enhanced cells in an ordinary perfusion tank", _START,
         "scenarios.reference(): a 3 ng cell that doubles in 24 hours and makes 0.054 mol of ammonia a kilo and 0.279 mol of lactate "
         "per mol of glucose; 5 mmol/L of ammonia and 50 of lactate tolerated; no lost runs; no growth factors bought; a "
         "food-grade plant; gas at up to 6 mm/s"),
        ("Cells double in 16 hours", ("doubling_h",),
         "physics allows about 8 h (median); a meat line in suspension at 50 g/L or more doubling in 16 h or less by 2035: 7% "
         "(gf_and_doubling_bounds.md)"),
        ("Cells of 3 ng, Humbird's, the heaviest allowed", ("mass_pg",),
         "no meat cell growing in suspension has been measured heavier (SuperMeat 2024: 1.75 ng weighed, about 2.3 ng from its "
         "diameter); the 5.3 ng assumed by Risner 2021 and CE Delft 2021 is rejected by the same rule as a doubling faster than "
         "any measured (2026-11-20, study_comparison.md). It changes nothing from Humbird's design"),
        ("A food-grade plant with shared medium", ("items",), "nobody has built one (cheap_plant_study.md)"),
        ("Dialyser-grade hollow fibres as the filter", ("flux", "membrane_life", "membrane_price", "membrane_hw"),
         "nothing run with animal cells; holds 25% cells for a month: 15% (retention_alternatives.md)"),
        ("Dissolved oxygen held at about half of air saturation", ("do_mmol",),
         "as pharma holds it; it changes nothing until the tank design makes oxygen the limit"),
        ("The cheapest tank design that passes the checks on the CO₂ loop", ("column", "col_pout", "p_top_barg", "aspect"),
         "nobody has run a stripping column or 1 bar of extra pressure with animal cells (gas_exchange_study.md)"),
        (f"Tanks of {_size():g} m³ in place of 20 m³", ("vessel_m3",),
         "the published tank size that costs least with every other lever at its favourable value; the tank design is chosen "
         "again and passes the same checks. Since 2026-11-20 a plant's cost follows what each tank brings with it (the tank, its "
         "makeup tanks and filter housings, buildings: floor_physics.tank_items), so larger tanks cost less per m³ than the old "
         "rule gave; the 211 m³ tanks of Negulescu 2023 still cost more here, because a deeper tank holds a thinner culture "
         "(study_comparison.md)"),
        ("The least medium flow at the lowest measured", ("min_perfusion",),
         "changes nothing here: ammonia, not the least flow, sets the litres of medium"),
        ("Culture up to 320 g/L in place of 258", ("x_visc",),
         "changes nothing here: oxygen holds the culture below both (thick_culture.md)"),
        ("Medium at the nutrient floor", ("medium_price",),
         "changes nothing here: Humbird's design already pays only for what the cells eat, $2.00 a kilo (nutrient_floor.md)"),
    ]


def target() -> dict:
    """The explore() arguments of the all-favourable case (scenarios.all_favourable()['kw'])."""
    return dict(S.all_favourable()["kw"])


def evaluate(kw: dict) -> dict:
    """The cost of a set of explore() arguments: explore's result."""
    return fp.explore(**kw)


def ladder() -> list:
    """The levers in order, each kept moved: [{'name', 'why', 'cost', 'kw', 'result'}]. The last row's `kw` is
    scenarios.all_favourable()['kw'], so its cost is that case's."""
    tgt = target()
    used = [k for _n, keys, _w in steps() for k in keys]
    assert sorted(used) == sorted(tgt), f"the path's steps and the all-favourable case differ: {sorted(set(used) ^ set(tgt))}"
    out, kw = [], {}
    for name, keys, why in steps():
        kw = {**kw, **{k: tgt[k] for k in keys}}
        r = evaluate(kw)
        out.append({"name": name, "why": why, "cost": r["total"], "kw": dict(kw), "result": r})
    assert out[-1]["kw"] == tgt
    return out


def alone() -> list:
    """Each lever on its own, from Humbird's design: [(name, cost, change from Humbird's design)]."""
    tgt = target()
    st = steps()
    base = {k: tgt[k] for k in st[0][1]}
    c0 = evaluate(base)["total"]
    out = []
    for name, keys, _why in st[1:]:
        c = evaluate({**base, **{k: tgt[k] for k in keys}})["total"]
        out.append((name, c, c - c0))
    return out


def with_gfi_amino_acids(kw: dict, tier: str = "feed", need: str = "eff") -> float:
    """A case's cost with the nutrient floor built from GFI's amino-acid prices (`nutrient_floor.aa_cost`). Since 2026-11-19
    the model's own floor is GFI's feed grade at the efficient need ($2.00 a kilo), so at the defaults this equals the case."""
    price = nutrient_floor.aa_cost(tier, need) / value("aa_intensity")
    with retention._with({"aa_bulk_price": price}):
        return evaluate(kw)["total"]


def lever_table() -> str:
    """The all-favourable case lever by lever, as Markdown: the value taken, the source it comes from, and each source's value."""
    a = S.all_favourable()
    names = dict(S.FAV_SOURCES)
    out = ["| lever | value taken | from | " + " | ".join(n for _s, n in S.FAV_SOURCES) + " | favourable is |",
           "|---|---|---|" + "---|" * len(S.FAV_SOURCES) + "---|"]
    show = lambda v: "none" if v is None else (", ".join(str(x) for x in v) if isinstance(v, tuple) else f"{v:g}" if isinstance(v, float) else str(v))
    for r in a["levers"]:
        better = {"lower": "lower", "higher": "higher", "cost": "whichever costs least"}[r["better"]]
        out.append(f"| {r['lever']} ({r['unit']}) | {show(r['value'])} | {names[r['source']]} | "
                   + " | ".join(f"{show(r['sources'][s][0])}: {r['sources'][s][1]}" for s, _n in S.FAV_SOURCES) + f" | {better} |")
    return "\n".join(out)


def summarise() -> None:
    rows = ladder()
    prev = None
    print("  the path: Humbird's design, one lever at a time, each kept moved ($/kg of cells)")
    for s in rows:
        d = "" if prev is None else f"  ({s['cost'] - prev:+6.2f})"
        print(f"    ${s['cost']:6.2f}{d:<10} {s['name']}")
        prev = s["cost"]
    print("  each lever alone, from Humbird's design:")
    for name, cost, d in alone():
        print(f"    ${cost:6.2f}  ({d:+6.2f})  {name}")
    last = rows[-1]
    print(f"  scenarios.reference(): ${S.reference()['total']:.2f}; the all-favourable case: ${S.all_favourable()['cost']:.2f}")
    print(f"  with GFI's cheapest amino-acid floor: ${with_gfi_amino_acids(last['kw']):.2f}")
    print(f"  price parity with US minced beef or pork cuts ($12 a kilo) needs about $6.1 a kilo of cells (the shelf rule: cost "
          f"plus $2.5, over 72%); the all-favourable case is ${last['cost']:.2f}")
    print()
    print(lever_table())


if __name__ == "__main__":
    summarise()
