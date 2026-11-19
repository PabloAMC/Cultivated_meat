#!/usr/bin/env python3
"""
min_litres.py — the least medium, in litres per kg of cells, that physics and chemistry allow.

`floor_physics.explore` sets the litres per kg from four terms: ammonia, lactate, the least flow a cell needs, and a
nutrient floor of 8 L/kg. This module asks how low each term could go, with the arithmetic in the open, and what the
all-favourable and low-lactate examples would cost at those litres. It changes no default and adds no logic to `explore`: costs
come from `explore(medium_l=...)`.

The bounds (per kg of wet cells)
--------------------------------
nitrogen     Ammonia is nitrogen the cells take in and do not build into protein or nucleic acid. If amino acids come in
             the proportion the cell builds protein, no nitrogen need leave as ammonia, so stoichiometry sets the floor
             at zero. `leak` is the share of the cell's 2.86 mol N that leaves as ammonia anyway; litres = leak x 2.86 /
             the ammonia limit. STALE SINCE 2026-11-19: the limit used here is Humbird's 5 mmol/L (`pf_nh3_limit`); the
             scenarios now hold 4 (`sc_nh3_limit`, through `scenarios.always()`), so at a scenario's own leak this term is
             4/5 of explore's ammonia term. The default leak is zero, so no cost in this module depends on it.
lactate      Glucose can be burned whole (6 O2 and 6 CO2 each), so the floor yield is zero. Litres = yield x glucose /
             the lactate limit.
bath         The medium is what the cells sit in, and its salts may not pass `pf_osm_limit`. The salts of a
             conventional medium (`ml_salts_osm`) leave the rest of the budget for nutrients. Litres = nutrient moles /
             that budget. This is how pharma perfusion media are made (Mayrhofer 2020: a 400 mOsm/kg target).
feed         The feed is a concentrate mixed into the tank and diluted there, so the tank, not the feed, meets the salt
             limit. The feed is then limited by what dissolves: litres = nutrient solids / `ml_feed_g_l`.
flow         The least medium flow per gram of cells per day, measured (`pf_min_perfusion`'s low end), over the growth
             rate in 1/day.

Run
---
    python min_litres.py
"""
from __future__ import annotations

import floor_physics as fp
import scenarios as S
from inputs import REGISTRY, value

SCENARIOS = ("best", "central")


def nitrogen_in() -> float:
    """Nitrogen in a kg of wet cells, mol/kg (Humbird's cell formula)."""
    return value("ml_n_per_dry") * value("ml_dry_mol_kg")


def nutrients(doubling_h: float = 24.0, mass_pg: float = 3000.0) -> dict:
    """What a kg of cells must eat, as amino acids and glucose (`floor_physics.feedstock` counts the same two): moles,
    which set the salt a medium carries, and kilograms, which set the strength of a feed. Glucose scales with the oxygen
    burned per kg, as in `feedstock` (half of it is upkeep)."""
    cells = fp.Cells(mass_pg=mass_pg, doubling_h=doubling_h)
    burn = cells.o2_per_kg / fp.GOOD_CELLS.o2_per_kg
    aa_kg = value("ml_aa_pure_kg")
    glc_kg = value("glucose_intensity") * (0.5 + 0.5 * burn)
    n_aa = aa_kg * 1000.0 / value("ml_aa_mw")
    n_glc = glc_kg * 1000.0 / value("ml_glc_mw")
    return {"n_aa": n_aa, "n_glc": n_glc, "n_osm": n_aa + n_glc, "solids_kg": aa_kg + glc_kg, "mu_day": cells.mu * 24.0}


def bounds(doubling_h: float = 24.0, mass_pg: float = 3000.0, leak: float = 0.0, lac_yield: float = 0.0,
           salts: float | None = None, feed_g_l: float | None = None, flow: float | None = None) -> dict:
    """The least litres per kg from each physical limit, L/kg wet. Defaults are the floor: no ammonia leak, no lactate,
    salts as in a conventional medium, a feed of `ml_feed_g_l`, and the lowest measured medium flow.

    `terms` holds each limit. `stoichiometric` is the larger of the nitrogen and lactate terms; `concentrated` adds the
    feed's solubility; `bath` replaces that with the salt budget of a medium the cells sit in; `measured_flow` is the flow
    term alone. `physical` is the `concentrated` figure: the least the physics allows if a concentrate can be dosed.
    `practical` also respects the lowest medium flow measured per cell, which was reached in 400 mOsm/kg media."""
    nut = nutrients(doubling_h, mass_pg)
    salts = value("ml_salts_osm") if salts is None else salts
    feed_g_l = value("ml_feed_g_l") if feed_g_l is None else feed_g_l
    flow = REGISTRY["pf_min_perfusion"].lo if flow is None else flow
    terms = {
        "nitrogen": leak * nitrogen_in() / (value("pf_nh3_limit") / 1000.0),
        "lactate": lac_yield * nut["n_glc"] / (value("pf_lac_limit") / 1000.0),
        "bath": nut["n_osm"] / ((value("pf_osm_limit") - salts) / 1000.0),
        "bath_low_salt": nut["n_osm"] / ((value("pf_osm_limit") - REGISTRY["ml_salts_osm"].lo) / 1000.0),
        "feed": nut["solids_kg"] * 1000.0 / feed_g_l,
        "flow": flow / nut["mu_day"],
    }
    stoich = max(terms["nitrogen"], terms["lactate"])
    return {"terms": terms, "nutrients": nut, "stoichiometric": stoich,
            "concentrated": max(stoich, terms["feed"]), "bath": max(stoich, terms["bath"]),
            "measured_flow": terms["flow"], "physical": max(stoich, terms["feed"]),
            "practical": max(stoich, terms["feed"], terms["flow"])}


def waste_allowed(litres: float, doubling_h: float = 24.0, mass_pg: float = 3000.0) -> dict:
    """The most waste a kg of cells may make if `litres` of permeate are to carry it away at the model's limits:
    ammonia in mol/kg, and the lactate yield that fits, in mol per mol of the glucose a cell making no lactate takes up
    (`nutrients`). STALE SINCE 2026-11-19 on two counts: the ammonia limit is Humbird's 5 mmol/L (`pf_nh3_limit`), where the
    scenarios hold 4 (`sc_nh3_limit`), so the scenarios allow 4/5 of `nh3_kg`; and the scenarios state the lactate yield per
    mol of all the glucose taken up (`floor_physics.glucose_balance`), on which basis the same lactate is a yield of
    lac / (n_glc + lac / 2)."""
    n_glc = nutrients(doubling_h, mass_pg)["n_glc"]
    nh3 = litres * value("pf_nh3_limit") / 1000.0
    lac = litres * value("pf_lac_limit") / 1000.0
    return {"nh3_kg": nh3, "lac_kg": lac, "lac_yield": lac / n_glc, "nh3_share": nh3 / nitrogen_in()}


def energy_check(doubling_h: float = 24.0, mass_pg: float = 3000.0) -> dict:
    """ATP per kg of cells: what the model's oxygen implies, against Kilburn's measured mouse fibroblast (biosynthesis plus
    upkeep over one generation of 27.6 h), both at `mass_pg` per cell. A cross-check on the energy side of the glucose figure."""
    cells = fp.Cells(mass_pg=mass_pg, doubling_h=doubling_h)
    per_kg = 1e15 / mass_pg                                               # cells per kg of wet cells
    model = cells.qo2 / cells.mu * value("ge_atp_per_o2")                 # mol ATP per kg
    kil = (value("ml_atp_bio") + value("ml_atp_maint") * doubling_h / value("ml_kilburn_td_h")) * per_kg
    return {"model_atp_kg": model, "kilburn_atp_kg": kil, "ratio": model / kil,
            "glucose_min_mol": kil / 32.0}                                # glucose that would pay Kilburn's ATP if burned whole


def costs_at(key: str) -> dict:
    """$/kg of a scenario at the bound litres, by `explore(medium_l=...)`, plus the scenario as it stands. Keys:
    `scenario` (the model's litres), `bath`, `measured_flow`, `physical`, `practical`; and two runs with waste set to zero and
    the model's own rules left in place: `no_waste` (default flow) and `no_waste_low_flow` (the lowest measured flow)."""
    kw = S.explore_kwargs(S.SCENARIOS[key].choice)
    b = bounds(kw.get("doubling_h", 24.0), kw.get("mass_pg", 3000.0))
    base = fp.explore(**kw)
    out = {"scenario": {"litres": base["medium_l"], "cost": base["total"], "set_by": base["medium_set_by"]}}
    for name in ("bath", "measured_flow", "physical", "practical"):
        r = fp.explore(**{**kw, "medium_l": b[name]})
        out[name] = {"litres": b[name], "cost": r["total"], "feedstock": r["feedstock"], "membranes": r["membranes"],
                     "retention_capex": r["retention_capex"]}
    clean = {k: v for k, v in kw.items() if k not in ("nh3_kg", "lac_yield", "glc_kg")}
    for name, extra in (("no_waste", {}), ("no_waste_low_flow", {"min_perfusion": REGISTRY["pf_min_perfusion"].lo})):
        r = fp.explore(**{**clean, "nh3_kg": 0.0, "lac_yield": 0.0, **extra})
        out[name] = {"litres": r["medium_l"], "cost": r["total"], "set_by": r["medium_set_by"]}
    return out


def main() -> None:
    n = nitrogen_in()
    print(f"nitrogen in a kg of cells: {n:.2f} mol; litres per unit leak at {value('pf_nh3_limit'):g} mM (Humbird's limit; "
          f"the scenarios hold {S.always()['nh3_limit']:g}): {n / (value('pf_nh3_limit') / 1000.0):.0f}")
    for key in SCENARIOS:
        kw = S.explore_kwargs(S.SCENARIOS[key].choice)
        d, m = kw.get("doubling_h", 24.0), kw.get("mass_pg", 3000.0)
        b = bounds(d, m)
        print(f"\n{key}: doubling {d:g} h, {m:g} pg; nutrients {b['nutrients']['n_osm']:.2f} mol, "
              f"{b['nutrients']['solids_kg']:.3f} kg per kg of cells")
        for k, v in b["terms"].items():
            print(f"  {k:<10}{v:7.1f} L/kg")
        print("  energy:", {k: round(v, 2) for k, v in energy_check(d, m).items()})
        for name, v in costs_at(key).items():
            print(f"  {name:<18}{v['litres']:6.1f} L/kg  ${v['cost']:.2f}/kg")
        print("  waste allowed at the physical bound:", {k: round(v, 3) for k, v in waste_allowed(b["physical"], d, m).items()})


if __name__ == "__main__":
    main()
