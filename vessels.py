#!/usr/bin/env python3
"""
vessels.py — vessel type against operating mode: what a kilo of cells costs when ONLY the vessel and the way it is
run change.

Why
---
People compare "stirred tank" with "perfusion" as if they were alternatives. They are two different choices: the
VESSEL (a stirred tank, an airlift, a bed of carriers, a cartridge of hollow fibres, a single-use bag) and the
OPERATING MODE (batch, fed-batch, fill-and-draw, chemostat, perfusion). Before this module the model priced only
a stirred tank, and only two modes differed (perfusion, and drained and refilled). The cost ladder in
floor_physics.tiers() changes plant, mode, cells and density from one row to the next, so a reader cannot see
what caused each step.

This module holds the cells, the plant class, the added equipment for oxygen and CO₂ and the losses fixed (one of two settings: the
reference case, floor_physics.explore() at its defaults, or a scenario from scenarios.py), and changes only the
vessel and the mode. Every cell of the grid is a call to floor_physics.explore() with a `vm` dict (the numbers
that make the vessel and the mode, all from inputs.py `vm_*`), so the stirred tank in perfusion IS the
scenario's own number.

The vessels
-----------
stirred   Humbird's stirred tank (as everywhere else in the model).
airlift   an airlift (draft-tube bubble column): no stirrer, gas lifts and mixes the culture. The same sparged-gas
          rules for oxygen and CO2 as the stirred tank, at the airlift's taller shape; no stirrer to pay for.
bag       a single-use stirred bag at its largest common size: the stirred tank's physics at that size, a cheaper
          frame, a bag thrown away each run, no pressure (so no extra pressure).
packed    a packed or fixed bed: cells grow on carriers in a bed that medium is pumped through. The bed's capacity per
          litre of vessel caps the density. Cells must be detached to harvest, so the bed is grown and emptied in
          cycles even when medium flows through it; some cells stay behind.
hollow    hollow fibres: cells grow outside a bundle of porous fibres that carry the medium. Like the packed bed, the
          space caps the density and the unit is harvested in cycles.

The modes
---------
batch      fill with medium, grow two doublings from the seed, empty. All nutrients are in the first fill, so the
           medium caps the density (`vm_batch_x`), and every litre leaves with the cells.
fedbatch   as batch, with concentrated feed added: waste build-up and other by-products cap the density
           (Humbird's design; the cycle is his: two doublings plus 10 hours to clean and refill).
filldraw   never emptied: a share of the tank is drained and refilled each cycle, no cell retention (the existing
           'drained and refilled' mode).
chemostat  fresh medium in and whole culture out, continuously, at a dilution rate below the growth rate (no
           retention). Waste caps the density as in fill-and-draw, but the culture sits at the cap.
perfusion  fresh medium flows through while a device holds the cells back (the model's default, a TFF hollow-fibre
           loop: retention.py), so waste is washed out; cells are bled off at the growth rate.

Each cell carries: the cost per kg, what limits the density, the largest cost item, and a maturity tag
(`TAGS`: runs at this scale today / pilot / paper only), or "not possible" with the reason.

The page's JavaScript mirrors `vm_for` and `cell` (build_interactive.py, page_scenarios.js); tests/run_parity.py
checks the two agree. Evidence: research_notes/vessels_and_modes.md.

Run
---
    python vessels.py
"""
from __future__ import annotations

import math

import floor_physics as fp
from inputs import value

# the keys explore() reads from a vm dict (floor_physics.explore)
VM_KEYS = ("washed", "kind", "wv", "dil_frac", "n_doublings", "turnaround_h", "restart_days", "run_days",
           "clean_uptime", "shape", "recovery", "otr_mult", "mixing", "co2_gas", "o2_gas", "caps", "capex_ratio",
           "own_retention", "cons_run", "labour_mult", "co2_mult", "no_protectant", "gas_away")

TODAY, PILOT, PAPER = "done at this size", "only done smaller", "never done with animal cells"
TAG_ORDER = (TODAY, PILOT, PAPER)

# the explore() arguments of the added equipment for oxygen and CO₂ (scenarios.py "tricks" switch) and of the tank shape
_TRICK_ARGS = ("column", "col_pout", "p_top_barg")
_SHAPE_ARGS = ("aspect",)

VESSELS = {
    "stirred": dict(
        name="Stirred tank", size=value("vm_str_m3"),
        what="A steel tank with a stirrer. Gas bubbles in at the base.",
        limits="Oxygen and CO₂ move only through bubbles. Bubbles and foam hurt cells, so the gas flow is capped. "
               "A deeper tank passes less gas per litre and clears less CO₂. The stirrer must mix faster than the cells "
               "use oxygen.",
        vm={}, tricks=True, shape=True),
    "airlift": dict(
        name="Airlift (bubble column)", size=value("vm_str_m3"),
        what="A tall tank with a tube inside. Gas rises in the tube and moves the culture round. It has no stirrer.",
        limits="The same bubble rules apply as in a stirred tank. The tank is taller, so the same gas flow passes less "
               "gas per litre and clears less CO₂. The gas mixes the culture, not a stirrer. Its rising gas gives about the "
               "power per litre a stirrer gives, so the model holds it to the stirred tank's mixing rule at its own tall shape; "
               "no mixing time has been measured in an animal-cell airlift above 2 m³.",
        # 2026-11-20 (airlift trace): until then "mixing": False exempted the airlift from any mixing limit, which with its taller
        # shape (fewer bubble deaths per litre) made it cheaper than the stirred tank in perfusion although a stirred tank of the
        # same shape is held at about 85 g/L by mixing. Its gas power at 4-6 mm/s (39-59 W/m3, thick_culture.gas_power) is about
        # the stirrer's 43 W/m3, so the same rule at its own shape applies.
        vm={"capex_ratio": value("vm_alr_capex_ratio"), "otr_mult": value("vm_alr_otr_mult")},
        aspect=value("vm_alr_aspect"), tricks=True, shape=False),
    "caged": dict(
        name="Stirred tank with a bubble cage", size=value("vm_str_m3"),
        what="A stirred tank with an inner cylinder of fine mesh. The cells live in the ring around it, stirred gently and "
             "bubbled as softly as in the plain tank. A strong sparger bubbles inside the cylinder, where there are no cells. "
             "Only medium crosses the mesh.",
        limits="The ring's soft bubbling works as in a stirred tank. The cylinder adds gas exchange without bubbles touching "
               "the cells, up to what foam allows, but its oxygen and CO₂ reach the cells only with the medium that crosses the "
               "mesh, and a mesh fine enough to keep single cells out clogs.",
        vm={"capex_ratio": value("vm_cage_capex_ratio")},
        gas_add=value("vm_cage_exchange") * value("vm_cage_gas"), tricks=True, shape=True),
    "bag": dict(
        name="Single-use bag", size=value("vm_bag_m3"),
        what="A plastic bag in a steel frame, with a stirrer. Each run uses a new bag.",
        limits="The physics is the same as in a stirred tank, at the bag's largest common size. The bag takes no pressure, so the "
               "extra pressure does not apply. The frame is cheap, but each run uses a new bag.",
        vm={"capex_ratio": value("vm_bag_capex_ratio"), "cons_run": value("vm_bag_cost_run")},
        tricks=False, shape=False),
    "packed": dict(
        name="Packed bed", size=value("vm_bed_m3"),
        what="Cells grow on carriers packed in a bed. A pump sends medium through the bed, and the medium is oxygenated outside it.",
        limits="The carriers' surface per litre caps the density. Oxygen falls along the bed, which caps its height. "
               "The cells must be detached to harvest, so the bed is grown and emptied in cycles, and some cells stay behind.",
        vm={"co2_gas": False, "o2_gas": False, "mixing": False, "own_retention": True,
            "caps": {"room on the carriers": value("vm_bed_x")}, "recovery": value("vm_bed_recovery"),
            "capex_ratio": value("vm_bed_capex_ratio"), "cons_run": value("vm_bed_cost_run"), "wv": 1.0},
        cycle={"n_doublings": value("vm_bed_doublings"), "turnaround_h": value("vm_bed_turnaround_h")},
        tricks=False, shape=False, fixed=True),
    "hollow": dict(
        name="Hollow fibres", size=value("vm_hf_m3"),
        what="Cells grow around a bundle of porous fibres inside a cartridge. The fibres carry the medium.",
        limits="The space between the fibres caps the density. Oxygen and food must cross the fibre wall. "
               "Cartridges are small, so a plant needs thousands. Cells are flushed out to harvest.",
        vm={"co2_gas": False, "o2_gas": False, "mixing": False, "own_retention": True,
            "caps": {"room between the fibres": value("vm_hf_x")}, "recovery": value("vm_hf_recovery"),
            "capex_ratio": value("vm_hf_capex_ratio"), "cons_run": value("vm_hf_cost_run"), "wv": 1.0},
        cycle={"n_doublings": value("vm_hf_doublings"), "turnaround_h": value("vm_hf_turnaround_h")},
        tricks=False, shape=False, fixed=True),
}
VESSEL_ORDER = ("stirred", "caged", "airlift", "bag", "packed", "hollow")

_CYCLE = {"kind": "cyclic", "n_doublings": value("pf_fedbatch_doublings"), "turnaround_h": value("pf_turnaround_h"),
          "restart_days": value("vm_restart_cycle_days")}
MODES = {
    "batch": dict(name="Batch", what="Fill the tank with all its medium at once, let the cells grow, then empty it. Growth stops when the food in that one fill runs out.",
                  vm={**_CYCLE, "washed": False, "caps": {"food in one fill": value("vm_batch_x")}}),
    "fedbatch": dict(name="Fed-batch", what="As batch, but start with less medium and pump in concentrated food as the cells grow, then empty. More cells per run, until their own waste stops them, because nothing washes it out.",
                     vm={**_CYCLE, "washed": False}),
    "filldraw": dict(name="Fill-and-draw", what="Drain half, refill, and let it regrow. The tank is never emptied.",
                     vm={"washed": False}, mode="filldraw"),
    "chemostat": dict(name="Chemostat", what="Medium in and culture out all the time, at a steady density.",
                      vm={"washed": False, "shape": 1.0, "dil_frac": value("vm_chemostat_dil")}, mode="filldraw"),
    "perfusion": dict(name="Perfusion", what="Medium flows through while a device holds the cells back. Cells "
                                             "are bled off as they grow.",
                      vm={"washed": True}, mode="perfusion"),
}
MODE_ORDER = ("batch", "fedbatch", "filldraw", "chemostat", "perfusion")

# A vessel whose cells sit on a support holds no free culture, so fill-and-draw and a chemostat cannot be run in it.
# Its medium is pumped round from a separate tank: "batch" is that tank filled once (the medium holds food for
# vm_batch_x grams of cells a litre; the bed, not the medium, caps the density), and topping the tank up is the same
# run, so fed-batch is not a separate mode. In perfusion fresh medium flows through, but the bed is still grown and
# emptied in cycles: cells cannot be bled off a support.
NOT_POSSIBLE = {
    ("packed", "filldraw"): "The cells sit on the carriers, so part of the culture cannot be drained off.",
    ("packed", "chemostat"): "The cells sit on the carriers, so there is no free culture to draw off.",
    ("hollow", "filldraw"): "The cells sit between the fibres, so part of the culture cannot be drained off.",
    ("hollow", "chemostat"): "The cells sit between the fibres, so there is no free culture to draw off.",
}
SAME_AS = {("packed", "fedbatch"): ("batch", "A pump sends the medium round from a separate tank. Topping that tank up is "
                                             "the batch run, not a different mode."),
           ("hollow", "fedbatch"): ("batch", "A pump sends the medium round from a separate tank. Topping that tank up is "
                                             "the batch run, not a different mode.")}

# Maturity of each combination at the vessel's size: (tag, evidence). TODAY = animal cells have been grown this way
# at this size; PILOT = only in smaller vessels; PAPER = never with animal cells. research_notes/vessels_and_modes.md.
TAGS = {
    ("stirred", "batch"): (TODAY, "Pharma runs animal cells in stirred tanks of up to about 25 m³. Vow harvests whole 20 m³ tanks of quail cells."),
    ("stirred", "fedbatch"): (TODAY, "The standard way pharma grows animal cells, in tanks of up to about 25 m³."),
    ("stirred", "filldraw"): (TODAY, "Vow's food-safety filing names draw-and-fill at 20 m³. It does not say how often Vow uses it."),
    ("stirred", "chemostat"): (PILOT, "Animal-cell chemostats have been run only at about 1 litre."),
    ("stirred", "perfusion"): (PILOT, "The largest animal-cell perfusion found is 4 m³ (Genzyme). No way to hold cells back at 20 m³ exists."),
    ("airlift", "batch"): (PILOT, "Lonza (then Celltech) grew antibody-making cells in airlifts of up to 2 m³, at low density. A size of 10 m³ is claimed."),
    ("airlift", "fedbatch"): (PILOT, "The same as batch. Airlifts of up to 2 m³ have been used with animal cells, at low density."),
    ("airlift", "filldraw"): (PAPER, "Not found with animal cells. Quorn runs fungus continuously in 155 m³ airlifts."),
    ("airlift", "chemostat"): (PAPER, "Not found with animal cells. Quorn runs fungus continuously in 155 m³ airlifts."),
    ("airlift", "perfusion"): (PAPER, "Not found with animal cells at any size."),
    ("caged", "batch"): (PILOT, "Caged aeration (a sparger inside a mesh cage) has been used with cells on microcarriers in bench and pilot tanks, with mesh of about 85 µm. Single cells need a mesh finer than the cells; not found at any size."),
    ("caged", "fedbatch"): (PILOT, "As batch: microcarrier cultures only, in small tanks."),
    ("caged", "filldraw"): (PAPER, "Not found with animal cells."),
    ("caged", "chemostat"): (PAPER, "Not found with animal cells."),
    ("caged", "perfusion"): (PAPER, "Not found with animal cells. Perfusion would need a second device to hold the cells back, besides the cage."),
    ("bag", "batch"): (TODAY, "Single-use bags of 2,000 L are common in pharma, and 5,000 L bags are installed."),
    ("bag", "fedbatch"): (TODAY, "Pharma runs fed-batch in single-use bags of 2,000 to 5,000 L."),
    ("bag", "filldraw"): (PILOT, "Repeated harvests have been shown in bench vessels. No 5,000 L bag run has been found."),
    ("bag", "chemostat"): (PILOT, "Animal-cell chemostats have been run only at about 1 litre."),
    ("bag", "perfusion"): (PILOT, "Perfusion runs in single-use bags of up to about 2,000 L. The densest cultures were in rocking bags of a few litres."),
    ("packed", "batch"): (TODAY, "iCELLis 500 beds grow vaccine cells this way, at this size. They have never grown food cells."),
    ("packed", "fedbatch"): (TODAY, "As batch."),
    ("packed", "filldraw"): (TODAY, ""),
    ("packed", "chemostat"): (TODAY, ""),
    ("packed", "perfusion"): (TODAY, "iCELLis 500 beds can be perfused at this size, for vaccines. They have never been used for food cells."),
    ("hollow", "batch"): (TODAY, "The Quantum grows cells for cell therapy at this size, about 6 g a run."),
    ("hollow", "fedbatch"): (TODAY, "As batch."),
    ("hollow", "filldraw"): (TODAY, ""),
    ("hollow", "chemostat"): (TODAY, ""),
    ("hollow", "perfusion"): (TODAY, "The Quantum is perfused at this size, for cell therapy. No unit for kilograms of cells exists."),
}


def vm_for(vessel: str, mode: str) -> dict | None:
    """The vm dict for floor_physics.explore (None if the combination is not possible)."""
    if (vessel, mode) in NOT_POSSIBLE:
        return None
    if (vessel, mode) in SAME_AS:
        return vm_for(vessel, SAME_AS[(vessel, mode)][0])
    v, m = VESSELS[vessel], MODES[mode]
    out = {**v["vm"], **m["vm"]}
    caps = {**v["vm"].get("caps", {}), **m["vm"].get("caps", {})}
    if caps:
        out["caps"] = caps
    if v.get("fixed"):                                 # cells on a support: grown and emptied in cycles, seeded thin
        out.update(kind="cyclic", restart_days=value("vm_restart_cycle_days"), **v["cycle"])
        if mode == "batch":                            # the medium tank, not the bed, holds the food; waste is diluted in it
            out["washed"] = True
            out["caps"] = dict(v["vm"]["caps"])
    if v["size"] < value("vm_str_m3"):                 # many small units need more staff per m3 (Humbird's two plants)
        out["labour_mult"] = (value("vm_str_m3") / v["size"]) ** value("vm_labour_exp")
    return out


def explore_kwargs(vessel: str, mode: str, base: dict | None = None) -> dict | None:
    """explore() arguments for a vessel and a mode, on top of a case `base` (explore arguments, e.g. a scenario's).
    The vessel replaces the tank's size and, where it has its own, shape; a vessel that cannot take the added equipment for oxygen and CO₂
    drops them."""
    vm = vm_for(vessel, mode)
    if vm is None:
        return None
    v, m = VESSELS[vessel], MODES[mode]
    kw = dict(base or {})
    if not v["tricks"]:
        for k in _TRICK_ARGS:
            kw.pop(k, None)
    if not v["shape"]:
        for k in _SHAPE_ARGS:
            kw.pop(k, None)
    if "aspect" in v:
        kw["aspect"], kw["shape_cost"] = v["aspect"], False
    if "gas_add" in v:      # the cage's gas, discounted by the medium that crosses its mesh, adds to the ring's own bubbling
        kw["gas_velocity"] = kw.get("gas_velocity", value("pf_gas_velocity")) + v["gas_add"]
        vm = {**vm, "gas_away": v["gas_add"]}          # it exchanges oxygen and CO2 but meets no cells: no bubble deaths on it
    kw["vessel_m3"] = v["size"]
    kw["mode"] = m.get("mode", "filldraw")
    kw["vm"] = vm
    if v.get("fixed") and mode in ("batch", "fedbatch"):   # a tank of medium that holds food for vm_batch_x g/L
        kw["medium_l"] = 1000.0 / value("vm_batch_x")
    return kw


LIMIT_PLAIN = {"CO2 removal": "clearing CO₂", "oxygen supply": "getting oxygen in", "mixing": "mixing",
               "thickness of the culture": "how thick the culture can be", "waste build-up": "waste building up",
               "other by-products": "other waste and spent food", "food in one fill": "the food in one fill",
               "room on the carriers": "room on the carriers", "room between the fibres": "room between the fibres",
               "what the column can strip safely": "what the column can strip safely"}

UNSHOWN_NOTE = "This density is not shown for meat cells."

BIGGEST = {"capital": "the plant", "feedstock": "the medium", "consumables": "what is thrown away",
           "labour": "labour", "growth_factors": "growth factors", "utilities": "utilities"}


THIN_NOTE = ", with the culture run thinner"
LOOP_LIMIT = "what the column can strip safely"


def _thinned(kw: dict, x_hi: float, steps: int = 24):
    """The densest culture (g/L) at which the column loop of `kw` passes its checks, by bisection between 0 and `x_hi`; the
    explore() result there, or None if no density passes. page_vessels.js (vmThinned) does the same steps."""
    lo, hi, ok = 0.0, float(x_hi), None
    for _ in range(steps):
        mid = 0.5 * (lo + hi)
        r = fp.explore(**{**kw, "vm": {**kw["vm"], "caps": {**kw["vm"].get("caps", {}), LOOP_LIMIT: mid}}})
        if _loop_ok(r):
            lo, ok = mid, r
        else:
            hi = mid
    return ok


def cell(vessel: str, mode: str, base: dict | None = None) -> dict:
    """One cell of the grid: {'possible', 'cost', 'limit', 'density', 'biggest', 'tag', 'evidence', ...}."""
    tag, ev = TAGS[(vessel, mode)]
    kw = explore_kwargs(vessel, mode, base)
    if kw is None:
        return {"possible": False, "reason": NOT_POSSIBLE[(vessel, mode)], "tag": tag, "evidence": ev}
    r = fp.explore(**kw)
    fallback, unchecked = "", None
    if not _loop_ok(r):
        unchecked = r["total"]
        # the case's added equipment for oxygen and CO₂ need a loop this vessel cannot run within the checks (pH, pass rate dense cultures
        # have taken): use the cheapest setting of the tricks switch that passes, as scenarios.design() does
        import scenarios as S
        best = None
        for st in S.SW["tricks"].settings:
            b = {k: v for k, v in (base or {}).items() if k not in _TRICK_ARGS}
            kw2 = explore_kwargs(vessel, mode, {**b, **st.kw})
            rr, thin = fp.explore(**kw2), False
            if not _loop_ok(rr):                # the same tricks with the culture run thinner, so the loop passes its checks
                rr, thin = _thinned(kw2, rr["density"]), True
            if rr is not None and (best is None or rr["total"] < best[1]["total"] - 1e-12):
                best = (st, rr, thin)
        r, fallback = best[1], best[0].label + (THIN_NOTE if best[2] else "")
    parts = {k: r[k] for k in BIGGEST}
    big = max(parts, key=parts.get)
    return {"possible": True, "cost": r["total"], "limit": r["limit"], "density": r["density"], "output": r["output"],
            "medium_l": r["medium_l"], "uptime": r["uptime"], "biggest": BIGGEST[big], "biggest_share": parts[big] / r["total"],
            "density_unshown": tag == TODAY and r["density"] > value("vm_x_meat_shown") + 1e-9,
            "tricks_fallback": fallback, "unchecked_cost": unchecked, "same_as": SAME_AS.get((vessel, mode), (None,))[0],
            "tag": tag, "evidence": ev, "result": r}


def _loop_ok(r: dict) -> bool:
    col = r.get("column")
    return col is None or (col["ph_vs_safe"] <= 1.0 + 1e-9 and bool(col["passes_tested"]))


def grid(base: dict | None = None) -> dict:
    """{(vessel, mode): cell} for a case `base` (explore arguments; None = the reference case)."""
    return {(v, m): cell(v, m, base) for v in VESSEL_ORDER for m in MODE_ORDER}


def what_if_bed(base: dict | None = None) -> dict:
    """The packed bed with every handicap of today's units removed: 20 m3, priced like a stirred tank, carriers that
    cost nothing (edible, sold with the cells), every cell recovered, a stirred tank's crew. What is left is the cycle:
    the bed is seeded thin and emptied each run. Returns explore()'s result."""
    kw = explore_kwargs("packed", "perfusion", base)
    vm = {k: v for k, v in kw["vm"].items() if k != "labour_mult"}
    vm.update(capex_ratio=1.0, cons_run=0.0, recovery=1.0)
    return fp.explore(**{**kw, "vessel_m3": value("vm_str_m3"), "vm": vm})


def js_model() -> dict:
    """What the page's JavaScript needs to rebuild the grid (page_vessels.js mirrors vm_for, explore_kwargs, cell)."""
    jsn = {"p_top_barg": "p_top"}
    return {"vessels": {k: {"name": v["name"], "size": v["size"], "what": v["what"], "limits": v["limits"], "vm": v["vm"],
                            "aspect": v.get("aspect"), "tricks": v["tricks"], "shape": v["shape"], "fixed": bool(v.get("fixed")),
                            "cycle": v.get("cycle"), "gas_add": v.get("gas_add")} for k, v in VESSELS.items()},
            "modes": {k: {"name": m["name"], "what": m["what"], "vm": m["vm"], "mode": m.get("mode", "filldraw")}
                      for k, m in MODES.items()},
            "vorder": list(VESSEL_ORDER), "morder": list(MODE_ORDER),
            "not_possible": {f"{v}|{m}": t for (v, m), t in NOT_POSSIBLE.items()},
            "same_as": {f"{v}|{m}": list(t) for (v, m), t in SAME_AS.items()},
            "tags": {f"{v}|{m}": list(t) for (v, m), t in TAGS.items()}, "tag_order": list(TAG_ORDER),
            "trick_args": [jsn.get(k, k) for k in _TRICK_ARGS], "biggest": BIGGEST,
            "str_m3": value("vm_str_m3"), "labour_exp": value("vm_labour_exp"), "restart": value("vm_restart_cycle_days"),
            "batch_x": value("vm_batch_x"), "limit_plain": LIMIT_PLAIN, "x_meat_shown": value("vm_x_meat_shown"),
            "unshown_note": UNSHOWN_NOTE, "thin_note": THIN_NOTE, "loop_limit": LOOP_LIMIT}


def settings() -> dict:
    """The two settings the page shows: the reference case and the central scenario (explore arguments)."""
    import scenarios as S
    return {"reference": {}, "central": S.explore_kwargs(S.SCENARIOS["central"].choice)}


def markdown_table(base: dict | None = None) -> str:
    """The grid as Markdown (RESULTS.md, research_notes/vessels_and_modes.md quote it)."""
    g = grid(base)
    rows = ["| vessel (unit size) | " + " | ".join(MODES[m]["name"] for m in MODE_ORDER) + " |",
            "|---|" + "---|" * len(MODE_ORDER)]
    for v in VESSEL_ORDER:
        cells = []
        for m in MODE_ORDER:
            c = g[(v, m)]
            if not c["possible"]:
                cells.append("not possible")
            elif c["same_as"]:
                cells.append("as batch")
            else:
                cost = f"${c['cost']:,.0f}" if c["cost"] >= 1000 else f"${c['cost']:.2f}"
                fb = f", with {c['tricks_fallback']} (${c['unchecked_cost']:.2f} if the loop passed)" if c["tricks_fallback"] else ""
                un = f"; {UNSHOWN_NOTE[:-1].lower()}" if c["density_unshown"] else ""
                cells.append(f"**{cost}** ({c['density']:.0f} g/L, {LIMIT_PLAIN.get(c['limit'], c['limit'])}; {c['tag']}{un}{fb})")
        size = VESSELS[v]["size"]
        rows.append(f"| {VESSELS[v]['name']} ({size:g} m3) | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def summarise() -> None:
    for name, base in settings().items():
        g = grid(base)
        print(f"\n  {name}: cost per kg of cells, $ (limit; maturity)")
        print("  " + " " * 26 + "".join(f"{MODES[m]['name']:>16}" for m in MODE_ORDER))
        for v in VESSEL_ORDER:
            row = []
            for m in MODE_ORDER:
                c = g[(v, m)]
                row.append(f"{'not possible':>16}" if not c["possible"] else f"{c['cost']:>8.2f} {c['density']:>5.0f}g/L")
            print(f"  {VESSELS[v]['name']:<26}" + "".join(row))
        for v in VESSEL_ORDER:
            for m in MODE_ORDER:
                c = g[(v, m)]
                if c["possible"]:
                    print(f"    {v:<8} {m:<10} ${c['cost']:6.2f}  {c['limit']:<26} biggest: {c['biggest']:<20} "
                          f"{c['medium_l']:5.1f} L/kg  uptime {c['uptime']:.2f}  {c['tricks_fallback']}  [{c['tag']}]")


if __name__ == "__main__":
    summarise()
