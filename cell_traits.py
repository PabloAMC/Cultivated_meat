#!/usr/bin/env python3
"""
cell_traits.py — the four cell traits the cost rests on, and which routes have shown each level (2026-11-19).

The cost model uses four traits of the cells: the ammonia a kilo of cells makes as it grows (mol/kg wet), the lactate made per
glucose taken up (mol/mol), the doubling time (h) and the mass of a cell (pg wet). `scenarios.run` and `floor_physics.explore`
take them directly (`nh3_kg`, `lac_yield`, `doubling_h`, `mass_pg`). This module says, for any set of values, what has been shown:

ROUTES   the best level shown so far by each route, least intrusive first (inputs.py `cr_*`, sources there and in
         research_notes/cell_trait_routes.md): a feed change in meat cells; selection or adaptation in meat cells, without
         engineering; no engineering, in other cells only (CHO); genetic engineering, in any cells.
routes_needed(traits)   for each trait, the least intrusive route that has shown that level, and a plain verdict on the set.

It never says that engineering is necessary: it says what has and has not been shown. Each trait is judged alone, and
`combination` adds what has not been shown together.

    python cell_traits.py
"""
from __future__ import annotations

from inputs import value, REGISTRY

ROUTE_ORDER = ("feed", "select_meat", "select_other", "engineering")
ROUTE_TEXT = {"feed": "shown in meat cells with a feed change",
              "select_meat": "shown in meat cells without engineering (selection or adaptation)",
              "select_other": "shown without engineering, in other cells only",
              "engineering": "shown only with genetic engineering",
              None: "not shown by any route"}
# trait: (name, unit, explore() argument, direction: -1 lower is the better level, +1 higher is, plausible range for a slider)
TRAITS = {
    "nh3_kg": ("ammonia made per kilo of cells grown", "mol/kg wet", -1, (0.0, 0.95)),
    "lac_yield": ("lactate made per glucose taken up", "mol/mol", -1, (0.0, 1.5)),
    "doubling_h": ("doubling time", "h", -1, (12.0, 60.0)),
    "mass_pg": ("mass of a cell", "pg wet", +1, (1000.0, 3500.0)),
}
_PREFIX = {"nh3_kg": "nh3", "lac_yield": "lac", "doubling_h": "td", "mass_pg": "mass"}


def routes() -> dict:
    """{trait: [(route, level, source)]}: the levels shown, least intrusive route first, from inputs.py."""
    out = {}
    for t in TRAITS:
        rows = []
        for r in ROUTE_ORDER:
            name = f"cr_{_PREFIX[t]}_{r}"
            if name in REGISTRY:
                rows.append((r, value(name), REGISTRY[name].source))
        out[t] = rows
    return out


def _shown(trait: str, v: float, level: float) -> bool:
    d = TRAITS[trait][2]
    return v >= level - 1e-12 if d < 0 else v <= level + 1e-12


def trait_route(trait: str, v: float) -> str | None:
    """The least intrusive route that has shown a level at least as good as v (None: no route has)."""
    for r, level, _src in routes()[trait]:
        if _shown(trait, v, level):
            return r
    return None


def combination(traits: dict) -> list:
    """Combinations of traits not shown together, as sentences (each trait may still be shown alone)."""
    out = []
    nh3, td = traits.get("nh3_kg"), traits.get("doubling_h")
    low_feed = value("cr_nh3_feed")
    if nh3 is not None and td is not None and nh3 <= low_feed + 1e-12 and td < 42.9 - 1e-9:
        out.append(f"Low ammonia ({nh3:g} mol/kg or less) and a doubling under 42.9 hours have not been shown together in a meat cell: "
                   "the low-ammonia feed slowed the cells that showed it (Hubalek 2023).")
    return out


def routes_needed(traits: dict) -> dict:
    """For each trait in `traits` ({nh3_kg, lac_yield, doubling_h, mass_pg}), the least intrusive route that has shown that level,
    and a verdict for the set: 'No genetic engineering needed: ...' / 'These traits have so far been shown only with genetic
    engineering: ...' / 'Not yet shown by any route: ...'."""
    per = {}
    for t, v in traits.items():
        if t not in TRAITS:
            continue
        r = trait_route(t, float(v))
        per[t] = {"value": float(v), "route": r, "text": ROUTE_TEXT[r], "name": TRAITS[t][0], "unit": TRAITS[t][1]}
    none = [t for t, p in per.items() if p["route"] is None]
    eng = [t for t, p in per.items() if p["route"] == "engineering"]
    other = [t for t, p in per.items() if p["route"] == "select_other"]
    lst = lambda ts: "; ".join(f"{per[t]['name']} at {per[t]['value']:g} {per[t]['unit']}" for t in ts)
    if none:
        verdict, short = f"Not yet shown by any route: {lst(none)}.", "not shown by any route"
    elif eng:
        verdict, short = (f"These traits have so far been shown only with genetic engineering: {lst(eng)}.",
                          "some traits shown only with genetic engineering")
    elif other:
        verdict, short = (f"No genetic engineering needed: each trait has been shown without it, but {lst(other)} only in other "
                          "cells (CHO), not in meat cells.", "shown without engineering, some only in other cells")
    else:
        verdict, short = "No genetic engineering needed: each trait has been shown without it, in meat cells.", "shown in meat cells"
    together = combination(traits)
    if together:
        verdict += " Not shown together: " + " ".join(together)
        short += "; not yet together in one meat cell"
    return {"traits": per, "verdict": verdict, "short": short, "together": together,
            "rank": 3 if none else 2 if eng else 1 if other else 0}


# The best level of each trait MEASURED IN MEAT CELLS, with its source (2026-11-19, the author's direction: "I still think we are
# sometimes saying 'this is possible with engineering and this with selection' without having actual data for that. I would remove
# it."). The page, RESULTS.md, METHODS.md and README.md carry only these measurements, never a route. Only meat-cell measurements
# count: the CHO and HEK figures in ROUTES are left out, and so is the 2025 conference poster's zero ammonia (its cell type is not
# recorded in inputs.py). `short` is the source in the page's words.
MEAT_CELL_BEST = {
    "nh3_kg": ("cr_nh3_feed", "Hubalek 2023, bovine fat-precursor cells fed without glutamine"),
    "lac_yield": ("cr_lac_feed", "Pasitka 2024, chicken fibroblasts in perfusion"),
    "doubling_h": ("cr_td_engineering", "Stout 2023, immortalised bovine muscle cells, with serum"),
    "mass_pg": ("cr_mass_feed", "Pasitka 2024, chicken cells, from their density"),
}


def best_in_meat_cells() -> dict:
    """{trait: {"value", "source", "short", "unit", "dir"}}: the best level measured in meat cells (None where nothing is measured)."""
    out = {}
    for t, (name, short) in MEAT_CELL_BEST.items():
        inp = REGISTRY.get(name)
        out[t] = {"value": None if inp is None else value(name), "source": None if inp is None else inp.source, "short": short,
                  "unit": TRAITS[t][1], "dir": TRAITS[t][2]}
    return out


def beyond_measured(traits: dict) -> list:
    """The traits in `traits` set better than the best level measured in meat cells (a statement about data, not about routes)."""
    best = best_in_meat_cells()
    out = []
    for t, v in traits.items():
        b = best.get(t)
        if b is None or b["value"] is None:
            continue
        if (b["dir"] < 0 and float(v) < b["value"] - 1e-12) or (b["dir"] > 0 and float(v) > b["value"] + 1e-12):
            out.append(t)
    return out


def beyond_text(traits: dict) -> str:
    """The traits beyond what has been measured in meat cells, in words ('lactate 0.42 mol/mol, against 1.05 measured')."""
    best = best_in_meat_cells()
    parts = [f"{TRAITS[t][0].split(' made')[0].split(' time')[0]} {float(traits[t]):g} {TRAITS[t][1]}, against {best[t]['value']:g} measured"
             for t in TRAITS if t in beyond_measured(traits)]
    return "; ".join(parts) if parts else "none: each trait at or within the best measured in meat cells"


def js_model() -> dict:
    """What the page needs to say what a set of traits has been shown with (the page agent builds the UI)."""
    return {"routes": {t: [[r, lv, src] for r, lv, src in rows] for t, rows in routes().items()},
            "traits": {t: {"name": n, "unit": u, "dir": d, "range": list(rg)} for t, (n, u, d, rg) in TRAITS.items()},
            "route_text": {str(k): v for k, v in ROUTE_TEXT.items()}, "order": list(ROUTE_ORDER), "td_low_ammonia": 42.9}


def markdown() -> str:
    """The routes table (RESULTS.md, research_notes/cell_trait_routes.md)."""
    head = ("| trait | a feed change, in meat cells | selection or adaptation, in meat cells | no engineering, other cells only | "
            "genetic engineering, any cells | not shown by any route |")
    out = [head, "|---|---|---|---|---|---|"]
    rs = routes()
    for t, (name, unit, d, _rg) in TRAITS.items():
        lv = {r: v for r, v, _s in rs[t]}
        cell = lambda r: f"{lv[r]:g}" if r in lv else "nothing better"
        best = min(lv.values()) if d < 0 else max(lv.values())
        beyond = f"below {best:g}" if d < 0 else f"above {best:g}"
        if d < 0 and best <= 0.0:
            beyond = "nothing: zero has been shown"
        out.append(f"| {name} ({unit}) | {cell('feed')} | {cell('select_meat')} | {cell('select_other')} | {cell('engineering')} | {beyond} |")
    return "\n".join(out)


if __name__ == "__main__":
    print(markdown())
    import scenarios as S
    for k in S.LADDER:
        print(k, S.cell_traits(S.SCENARIOS[k].choice), routes_needed(S.cell_traits(S.SCENARIOS[k].choice))["verdict"])
