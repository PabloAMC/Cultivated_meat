#!/usr/bin/env python3
"""
frontier.py — the cheapest a kilo of cells could cost if every lever went to its limit, and what each lever is worth.

Why
---
The scenarios say what the model assumes. This module asks what is possible. It starts from the central scenario and moves
one lever at a time to the limit the research notes support, keeping each one moved, so the running cost shows what each lever
adds to the ones before it. Each step carries the calibrated odds from the note that studied it. The order matters (a cheaper
medium helps less once the cells need fewer litres), so the ladder runs from the lever that sets the others to the ones they
set: the cells, the retention device, the medium and growth factors, then the density, the plant and the losses.

Every step uses an existing model: `min_litres` (the least medium per kg), `retention` (the dialyser-grade fibre loop and its
membranes), `gf_doubling_bounds` (growth factors returned by the filter), `thick_culture` (the density limit),
`nutrient_floor` (GFI's amino-acid prices). Nothing here changes a default.

Held fixed: the scenario's tank design (tricks and shape, chosen for the central case), the 20 m3 tank (`tank_size`
finds Selected cells' cheapest size, 43 m3, 1.6% below it), and the stirred tank in perfusion. If perfusion fails, see `downside.py`.

Run
---
    python frontier.py
"""
from __future__ import annotations

import floor_physics as fp
import min_litres
import nutrient_floor
import retention
import scenarios as S
from inputs import value

HOURS = fp.HOURS


def _gf_share_with_reuse(kw: dict) -> float:
    """The scenario's share of Humbird's growth-factor price when a protein-retaining filter returns them: only the bleed carries
    them out, so the litres charged fall from the medium's to bleed + first fill (gf_doubling_bounds.reuse)."""
    d = retention.duty(kw)
    r = d["result"]
    bleed_l = d["bleed_m3_h"] * 1000.0 / d["kg_h"]
    fill_l = d["liquid_m3"] * 1000.0 / (d["kg_h"] * 24.0 * value("pf_run_days"))
    # capped at 1: when the bleed and the first fill already carry out as much liquid as the medium brings in (a thin culture
    # fed a concentrate), returning the proteins saves nothing, and cannot cost more
    return kw.get("growth_factors", 0.0) * min(1.0, (bleed_l + fill_l) / r["medium_l"])


def evaluate(state: dict) -> dict:
    """The cost of a state: {'choice': scenario switches, 'kw': explore overrides, 'patch': input overrides,
    'device': retention device, 'gf_reuse': bool}."""
    kw = {**S.explore_kwargs(state["choice"]), **state.get("kw", {})}
    with retention._with(state.get("patch", {})):
        if "waste_floor" in state:                                  # the least medium the physics allows at these cells
            b = min_litres.bounds(kw.get("doubling_h", 24.0), kw.get("mass_pg", 3000.0))
            kw["medium_l"] = b[state["waste_floor"]]
        if state.get("gf_reuse"):
            kw["growth_factors"] = _gf_share_with_reuse(kw)
        c = retention.scenario_cost(state["device"], kw)
    return {"total": c["total"], "medium_l": c["result"]["medium_l"] if "result" in c else None, "limit": None}


# The ladder: (name, what changes, evidence and odds). Each entry changes the state before it.
def steps() -> list:
    """(name, change, evidence and odds) for each lever, from the central scenario."""
    return [
        ("Selected cells scenario", {}, "the model as it stands: cells that make little waste, 36 h, TFF filter loop, $0.20 a litre"),
        ("Medium at the least the physics allows: 6.4 L/kg, fed as a concentrate",
         {"waste_floor": "physical"},
         "physically possible 60% (6 L/kg or less); a meat-cell process reporting 11 L/kg or less by 2030: 10% (min_litres_per_kg.md)"),
        ("Cells double in 16 hours", {"kw": {"doubling_h": 16.0}},
         "physics allows about 8 h (median); a meat line in suspension at 50 g/L or more doubling in 16 h or less by 2035: 7% (gf_and_doubling_bounds.md)"),
        ("Dialyser-grade hollow fibres as the filter", {"device": "dialyser"},
         "nothing run with animal cells; holds 25% cells for a month: 15% (retention_alternatives.md)"),
        ("Medium at the nutrient floor", {"choice": {"medium": "floor"}},
         "only what the cells eat, at GFI's feed-grade amino-acid prices; lowest company report $0.07 a litre (nutrient_floor.md)"),
        ("Growth factors returned by the filter, and bought at 30% of Humbird's price", {"gf_reuse": True},
         "a filter that holds back insulin and transferrin halves the cost: 20% (gf_and_doubling_bounds.md)"),
        ("Culture at 320 g/L in place of 258", {"patch": {"pf_x_visc": 320.0}},
         "held for a month at 20 m3, everything else solved: 6% (thick_culture.md); the column loop's checks may bind first"),
        ("A food-grade plant with shared medium", {"choice": {"plant": "lean"}},
         "nobody has built one (cheap_plant_study.md)"),
        ("Runs lost 0.2% a day, as in pharma", {"choice": {"losses": "0.2"}},
         "makers report 0.6-2% a day; pharma 0.2% (contamination notes)"),
        ("Gas at up to 6 mm/s", {"choice": {"gas": "6"}},
         "about even odds that 6 mm/s works at this size (gas_flow_cap.md)"),
    ]


def _apply(state: dict, change: dict) -> dict:
    state = {k: (dict(v) if isinstance(v, dict) else v) for k, v in state.items()}
    for k, v in change.items():
        if k in ("choice", "kw", "patch"):
            state[k] = {**state[k], **v}
        else:
            state[k] = v
    return state


def base_state() -> dict:
    return {"choice": dict(S.SCENARIOS["central"].choice), "device": "tff", "kw": {}, "patch": {}}


def ladder() -> list:
    """The levers in order, each kept moved: [{'name', 'why', 'cost', 'state'}]."""
    out, state = [], base_state()
    for name, change, why in steps():
        state = _apply(state, change)
        r = evaluate(state)
        out.append({"name": name, "why": why, "cost": r["total"], "state": _apply(state, {})})
    return out


def alone() -> list:
    """Each lever on its own, from the central scenario: [(name, cost, change from central)]."""
    b = base_state()
    c0 = evaluate(b)["total"]
    return [(name, evaluate(_apply(b, change))["total"], evaluate(_apply(b, change))["total"] - c0)
            for name, change, _why in steps()[1:]]


def with_gfi_amino_acids(state: dict, tier: str = "feed", need: str = "eff") -> float:
    """The frontier's cost with the nutrient floor built from GFI's amino-acid prices (`nutrient_floor.aa_cost`). Since 2026-11-19
    the model's own floor is GFI's feed grade at the efficient need ($2.00 a kilo), so at the defaults this equals the frontier."""
    price = nutrient_floor.aa_cost(tier, need) / value("aa_intensity")
    return evaluate({**state, "patch": {**state.get("patch", {}), "aa_bulk_price": price}})["total"]


def summarise() -> None:
    rows = ladder()
    prev = None
    print("  the ladder: central scenario, one lever at a time, each kept moved ($/kg of cells)")
    for s in rows:
        d = "" if prev is None else f"  ({s['cost'] - prev:+6.2f})"
        print(f"    ${s['cost']:6.2f}{d:<10} {s['name']}")
        prev = s["cost"]
    print("  each lever alone, from the central scenario:")
    for name, cost, d in alone():
        print(f"    ${cost:6.2f}  ({d:+6.2f})  {name}")
    last = rows[-1]
    print(f"  with GFI's cheapest amino-acid floor: ${with_gfi_amino_acids(last['state']):.2f}")
    print(f"  price parity with $12 meat needs about $6.1 a kilo of cells (the shelf rule: cost plus $2.5, over 72%); "
          f"the frontier is ${last['cost']:.2f}")


if __name__ == "__main__":
    summarise()
