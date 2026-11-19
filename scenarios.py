#!/usr/bin/env python3
"""
scenarios.py — cost scenarios for cultivated meat: what has to go right, and what each assumption is worth.

Why
---
Earlier versions of this model quoted one number, "the floor", as if it were the lowest cost the physics allows.
It was neither an all-favourable nor a typical case: it was `floor_physics.explore()` at its defaults (a standard
20 m3 stirred tank in perfusion, 120 g/L, a food-grade plant, cells that make almost no ammonia or lactate, no tank tricks). That number is
kept as a labelled REFERENCE (`reference()`), and everything else is described as SCENARIOS: each is a preset of a
small set of SWITCHES, one per decision that moves the cost. Every figure is computed from the model.

The pieces
----------
SWITCHES   the decisions (kind of cells, growth speed, plant, gas the cells tolerate, tank tricks, tank shape, runs
           lost, restart time, growth factors, medium price). Each has settings; each setting is an
           `floor_physics.explore()` argument set, a plain-language label, and a tag for what it needs:
           genetic engineering / selection or adaptation / a change of feed or process / nothing new.
SCENARIOS  presets of the switches, each with a one-sentence story of what has to go right.
priorities()   for one scenario, what each switch is worth if it moved to its best or its worst setting.
grid()         two switches against each other.
interactions() which switches do not add up (a tank trick matters little if the cells waste a lot), as sentences.
cell_traits()  the four cell traits a choice gives (ammonia, lactate, doubling time, cell mass); run(choice, **traits) and
               scenario_mc(choice, traits=...) take them directly (2026-11-19); cell_traits.best_in_meat_cells gives the best level of each
               measured in meat cells. The named cases are reference points defined by their traits.
what_it_would_take()  the cost of cells a 1% or 10% share needs, and trait sets that reach it, deterministic (2026-11-19).
plant_axis()   perfusion against fed-batch as the plant gets cheaper (2026-11-19).
scenario_mc()  the uncertainty in the estimates behind a scenario (plant cost, financing, retention membranes, upkeep,
               medium price, loss rate, and since 2026-11-16 the ammonia the cells tolerate, the protectant, the least
               medium flow, antifoam), holding the scenario's switches.

The page (build_interactive.py) has a JavaScript mirror of this module; tests/run_parity.py checks the two agree.
Evidence for every setting: research_notes/cost_scenarios.md.

Run
---
    python scenarios.py
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np

import floor_physics as fp
import plant_items
from inputs import value, prior, draw
from price_ratio import shelf_price

# What a setting needs (2026-11-19, the author's direction): cells with traits other than the published ones are tagged CELLS,
# with no claim about the route (selection, adaptation or engineering) that would give them; the page and the docs say only what
# has been measured in meat cells (cell_traits.best_in_meat_cells).
FEED, CELLS, NOTHING = "feed or process", "cells", "nothing new"
TAG_ORDER = (NOTHING, FEED, CELLS)                  # the most demanding tag a scenario needs is the last one it uses
TAG_PLAIN = {CELLS: "needs cells with other traits than those published", FEED: "needs a change of feed, process or plant",
             NOTHING: "needs nothing new"}


@dataclass(frozen=True)
class Setting:
    key: str
    label: str            # plain-language name of this setting
    kw: dict              # floor_physics.explore() arguments (plant_items for the food-grade plant with shared medium)
    tag: str              # what it needs
    note: str             # one line: what it assumes, evidence
    short: str = ""       # a few words, for chart labels


@dataclass(frozen=True)
class Switch:
    key: str
    name: str             # plain name of the decision
    question: str         # what it decides, in a phrase
    settings: tuple


# Pressure at the top of the tank, the column's exit CO₂: the tricks' own settings (gas_exchange.cheapest_tricks).
_COL = {"column": "co2", "col_pout": value("ge_col_pout")}
_P1 = {"p_top_barg": value("sc_p_top")}
_O2 = {"column": "o2_closed", "col_pout": value("ge_col_pout")}

# Fed-batch: Humbird's cycle (two doublings from the seed, 10 hours to clean and refill), waste not washed out (vessels.MODES)
FEDBATCH_VM = {"kind": "cyclic", "n_doublings": value("pf_fedbatch_doublings"), "turnaround_h": value("pf_turnaround_h"),
               "restart_days": value("vm_restart_cycle_days"), "washed": False}
_FB = "Waste is not washed out, so it caps the density: a batch may end 1.3 times above the level perfusion is held to " \
      "(pf_batch_end_x), and its last doublings grow a little slower there. A lost batch costs its cells and 2 days; the next " \
      "seed is ready, so the restart switch does not apply. "

SWITCHES = (
    Switch("mode", "How the tank is run",
           "Whether the cells are grown in a batch and harvested at the end, or waste is washed out continuously while a filter "
           "holds the cells back", (
        Setting("perfusion", "Perfusion in a 20 m³ tank: waste washed out continuously through a cell filter",
                {"mode": "perfusion"}, FEED,
                "Fresh medium flows through while a filter loop holds the cells back, and cells are bled off as they grow. The "
                "waste never builds up, so oxygen and CO₂ set the density. Animal-cell perfusion has been run up to about 4 m³ "
                "(Genzyme), meat cells only in about 10 litres. A bigger tank barely helps it (tank_size.md)."),
        Setting("fedbatch100", "Fed-batch in a 100 m³ tank", {"mode": "filldraw", "vm": dict(FEDBATCH_VM), "vessel_m3": 100.0}, FEED,
                _FB + "A bigger tank costs less per m³. No animal cells have been grown above about 25 m³; plans for 100,000 litres "
                      "were paused or abandoned."),
        Setting("fedbatch50", "Fed-batch in a 50 m³ tank", {"mode": "filldraw", "vm": dict(FEDBATCH_VM), "vessel_m3": 50.0}, FEED,
                _FB + "Twice the largest tank animal cells have been grown in."),
        Setting("fedbatch", "Fed-batch in a 20 m³ tank: cells grown in a batch and harvested at the end",
                {"mode": "filldraw", "vm": dict(FEDBATCH_VM)}, NOTHING,
                _FB + "Shown at this size: pharma runs fed-batch in tanks of up to about 25 m³, and Upside Foods reports a "
                      "single-vessel process validated at 20,000 litres for 18 months, in several 20,000+ litre tanks (AgFunderNews, "
                      "17 Nov 2026; mode not disclosed, most likely fed-batch)."))),
    Switch("cells", "Kind of cells",
           "How much waste the cells make, and how big each cell is. Ammonia and lactate are the waste, and they slow growth", (
        Setting("engineered", "Almost no ammonia or lactate",
                {"nh3_kg": value("sc_nh3_engineered"), "lac_yield": value("sc_lac_engineered"), "mass_pg": value("sc_mass_selected_pg")},
                CELLS, "The metabolism of Humbird's efficient cell: ammonia 0.055 mol per kilo of cells, lactate 0.28 mol per mol of the "
                       "glucose taken up. Neither level has been measured in meat cells: the best measured there are 0.14 mol of "
                       "ammonia a kilo (Hubalek 2023) and 1.05 mol of lactate per mol of glucose (Pasitka 2024). The cell weighs 2 ng, "
                       "as every other setting's does (Humbird's 3 ng is an assumed cell; chicken cells are reported at 1.0 to 1.75 "
                       "ng). Changed 2026-11-19; it was 3 ng."),
        Setting("selected", "Less lactate, on a low-ammonia feed",
                {"nh3_kg": value("sc_nh3_selected"), "lac_yield": value("sc_lac_selected"), "mass_pg": value("sc_mass_selected_pg")},
                CELLS, "Glutamine is replaced in the feed, so ammonia is 0.14 (measured once, in bovine cells, Hubalek 2023). Lactate "
                       "is 0.42 per glucose, below the 1.05 measured in meat cells (Pasitka 2024). A cell weighs 2 ng. These differ "
                       "from the best meat cells in the published "
                        "record only in lactate, and that is worth a great deal: the published cells turn most of their glucose into "
                        "lactate, so they need about three times the glucose and far more medium to wash the lactate out."),
        Setting("measured", "The best meat cells measured",
                {"nh3_kg": value("sc_nh3_selected"), "lac_yield": value("sc_lac_measured"),
                 "mass_pg": value("sc_mass_selected_pg")},
                FEED, "Not one cell line: the best published figure for each trait, never measured together in one line. Ammonia "
                      "0.14 mol a kilo and a 43-hour doubling come from primary bovine fibro-adipogenic progenitor (fat-precursor) "
                      "cells fed alpha-ketoglutarate in place of glutamine (Hubalek et al. 2023, Mosa Meat and Maastricht University, "
                      "spinner flasks, five donors). Lactate, 1.05 mol per mol of glucose, comes from chicken fibroblasts in perfusion "
                      "(Pasitka et al. 2024, Believer Meats). A cell weighs 2 ng, a judgement between SuperMeat's chicken cells "
                      "(1.0 to 1.75 ng) and Humbird's 3 ng. Glucose comes from the cells' own balance: fermenting most of it, they need "
                      "about 4.5 mol a kilo, and the lactate from it sets the litres of medium. Companies may hold better cells they "
                      "have not published."),
        Setting("ordinary", "Ordinary meat cells",
                {"nh3_kg": value("sc_nh3_ordinary"), "lac_yield": value("sc_lac_measured"),
                 "mass_pg": value("sc_mass_selected_pg")},
                NOTHING, "Ammonia is 0.70 in bovine cells with glutamine. Lactate is 1.05 per glucose. A cell weighs 2 ng."))),
    Switch("growth", "Growth speed", "How long the cells take to double", (
        Setting("24", "Cells double every 24 hours", {"doubling_h": value("pf_doubling_h")}, CELLS,
                "Humbird's model cell doubles this fast. The fastest measured in meat cells is 15 hours (Stout 2023, with serum); "
                "bovine cells on the low-ammonia feed doubled in 42.9 hours (Hubalek 2023)."),
        Setting("30", "Every 30 hours", {"doubling_h": value("sc_td_fast")}, CELLS,
                "Between the model cell and the central value."),
        Setting("36", "Every 36 hours", {"doubling_h": value("sc_td_central")}, CELLS,
                "Between the 43 hours measured on the low-ammonia feed and the 25.7 hours measured with glutamine, in the same bovine cells (Hubalek 2023)."),
        Setting("43", "Every 43 hours", {"doubling_h": value("sc_td_measured")}, NOTHING,
                "The best low-waste meat-cell culture measured doubled in 42.9 hours (Hubalek 2023)."))),
    Switch("plant", "The plant", "How much the buildings and equipment around the tanks cost", (
        Setting("lean", "A food-grade plant with shared medium",
                {"items": dict(plant_items.PLANTS["lean"])}, FEED,
                "Humbird's plant without what animal cells plausibly do not need. It has a plain hall, bought oxygen in place of an "
                "oxygen plant, two small seed trains in place of eight seed tanks, food-grade tanks without pharma polish, and one "
                "sterilised medium line shared by all the tanks. It costs about half as much. Most of the saving is the hall, the "
                "oxygen and the seed trains, not the shared medium. Nobody has built one."),
        Setting("sterile", "A food-grade plant", {"plant": "sanitary"}, NOTHING,
                "Humbird's plant with an ordinary hall in place of the clean room. Food-grade tanks of this size are in use."),
        Setting("pharma", "A pharma-style plant with clean rooms", {"plant": "pharma"}, NOTHING,
                "Humbird's plant as he designed it."))),
    Switch("gas", "Gas the cells tolerate", "How fast gas can be bubbled into the tank before bubbles and foam hurt the cells", (
        Setting("6", "Gas bubbled in at up to 6 mm a second", {"gas_velocity": value("pf_gas_velocity")}, FEED,
                "Humbird's rule of thumb, with a protectant and foam control. Nobody has run dense cells at this gas speed at this size."),
        Setting("4", "Up to 4 mm a second", {"gas_velocity": value("sc_gas_mid")}, FEED,
                "Twice what has been run in tanks of 8 to 20 m³."),
        Setting("2", "Up to 2 mm a second", {"gas_velocity": value("sc_gas_low")}, NOTHING,
                "About the most that has been run with cells in tanks of 8 to 20 m³ (Nienow 2006)."))),
    Switch("tricks", "Tank tricks", "Ways to clear CO₂ and supply oxygen without more bubbles", (
        Setting("none", "None: gas bubbled in at the base", {}, NOTHING, "The standard stirred tank."),
        Setting("column", "A column beside the tank that strips CO₂ without bubbles", dict(_COL), FEED,
                "A pump sends culture down a packed column. The size is calculated. No animal cells have gone through one."),
        Setting("pressure", "The column, and 1 bar extra pressure in the tank", {**_COL, **_P1}, FEED,
                "Oxygen dissolves in proportion to pressure, and steam-rated tanks take it. Nobody has tested it with cells."),
        Setting("oxygen", "The column, the pressure and recycled pure oxygen", {**_O2, **_P1}, FEED,
                "The loop also supplies the oxygen. A lime scrubber recycles it."))),
    Switch("shape", "Tank shape", "How deep the liquid is compared with the tank's width", (
        Setting("flat", "Very squat: liquid half as deep as wide", {"aspect": value("sc_aspect_flat")}, FEED,
                "The squattest shape the search considers. The model counts the extra steel and floor."),
        Setting("squat", "Squat: liquid 0.75 times as deep as wide", {"aspect": value("sc_aspect_squat")}, FEED,
                "A squat tank passes more gas per litre. The model counts the extra steel and floor."),
        Setting("square", "Squarer: liquid as deep as wide", {"aspect": value("sc_aspect_mid")}, FEED, "The same effect, smaller."),
        Setting("tall", "Tall: 1.6 times as deep as wide", {"aspect": value("pf_aspect")}, NOTHING, "Humbird's tank."))),
    Switch("losses", "Runs lost", "How often a run is lost to contamination", (
        Setting("0.2", "0.2% of runs lost a day", {"hazard": value("pf_hazard_pharma")}, FEED,
                "Large pharma plants reach this with sealed, steam-sterilised tanks and strict hygiene."),
        Setting("0.6", "0.6% a day", {"hazard": value("sc_hazard_mid")}, FEED, "The low end of what makers report."),
        Setting("1", "1% a day", {"hazard": value("sc_hazard_cm")}, NOTHING,
                "About what the survey of makers implies, if runs last 10 to 20 days."),
        Setting("2", "2% a day", {"hazard": value("sc_hazard_high")}, NOTHING, "The upper end of what makers report."))),
    Switch("restart", "Restart after a loss", "How long a lost tank is out of use", (
        Setting("4", "4 days: reseeded from a neighbouring tank", {"restart_fail_days": value("sc_restart_neighbour")}, FEED,
                "Half the culture of a healthy neighbouring tank reseeds the lost one, so no new seed train is needed. The donor must "
                "test clean first. Nobody has reported doing this with animal cells at scale."),
        Setting("14", "14 days to clean and restart", {"restart_fail_days": value("sc_restart_base")}, NOTHING,
                "The seed train is ready; regrowing from a seed to working density is about 7 doublings."),
        Setting("21", "21 days", {"restart_fail_days": value("sc_restart_slow")}, NOTHING, "The seed trains must be regrown."),
        Setting("30", "30 days", {"restart_fail_days": value("sc_restart_long")}, NOTHING,
                "One failure reaches every tank."))),
    Switch("gf", "Growth factors", "How much must be paid for the proteins that tell cells to grow", (
        Setting("none", "None bought", {"growth_factors": 0.0}, CELLS, "The cells need none or make their own."),
        Setting("30", "30% of Humbird's price per litre", {"growth_factors": value("sc_gf_part")}, FEED,
                "Cheaper factors, or lines that need fewer."),
        Setting("60", "60% of his price", {"growth_factors": value("sc_gf_most")}, NOTHING, "Most of his price."),
        Setting("all", "All bought at his price", {"growth_factors": 1.0}, NOTHING,
                "Humbird's large-scale price. It assumes an industry far larger than the current one."))),
    # (with a complete-medium price, $0.20 and above, growth factors are in that price and this switch adds nothing: explore_kwargs)
    Switch("medium", "Price of the medium", "What a litre of the nutrient liquid costs", (
        Setting("floor", "At the nutrient floor: only what the cells eat", {"medium_price": 0.0}, FEED,
                "No one has reported it. The medium costs what the cells take up, at GFI's feed-grade amino-acid prices: $2.00 a "
                "kilo of cells (232 g of amino acids at $6.36, glucose, salts and vitamins), whatever the litres; growth factors "
                "are bought on top (the growth-factor switch). At the low-lactate example's 35 litres a kilo that is about $0.06 a litre."),
        Setting("0.20", "$0.20 a litre", {"medium_price": value("sc_medium_mid"), "medium_complete": True}, FEED,
                "What several companies announced for 2025. A complete medium: growth factors are in the price."),
        Setting("0.30", "$0.30 a litre", {"medium_price": value("sc_medium_high"), "medium_complete": True}, NOTHING,
                "Between the announced and the reported price. A complete medium: growth factors are in the price."),
        Setting("0.50", "$0.50 a litre", {"medium_price": value("media_price"), "medium_complete": True}, NOTHING,
                "What SuperMeat reports. A complete medium: growth factors are in the price."))),
)

_SHORT = {
    ("mode", "perfusion"): "perfusion", ("mode", "fedbatch100"): "fed-batch, 100 m³", ("mode", "fedbatch50"): "fed-batch, 50 m³",
    ("mode", "fedbatch"): "fed-batch, 20 m³",
    ("cells", "engineered"): "almost no waste", ("cells", "selected"): "less lactate, low-ammonia feed", ("cells", "measured"): "best measured",
    ("cells", "ordinary"): "ordinary", ("growth", "24"): "24 h", ("growth", "30"): "30 h", ("growth", "36"): "36 h", ("growth", "43"): "43 h",
    ("plant", "lean"): "food-grade, shared medium", ("plant", "sterile"): "food-grade plant", ("plant", "pharma"): "pharma-style plant",
    ("gas", "6"): "6 mm/s", ("gas", "4"): "4 mm/s", ("gas", "2"): "2 mm/s",
    ("tricks", "none"): "no tricks", ("tricks", "column"): "column", ("tricks", "pressure"): "column + pressure",
    ("tricks", "oxygen"): "column + pressure + oxygen",
    ("shape", "flat"): "0.5 deep/wide", ("shape", "squat"): "0.75", ("shape", "square"): "1.0", ("shape", "tall"): "1.6",
    ("losses", "0.2"): "0.2% a day", ("losses", "0.6"): "0.6% a day", ("losses", "1"): "1% a day", ("losses", "2"): "2% a day",
    ("restart", "4"): "4 days (neighbour)", ("restart", "14"): "14 days", ("restart", "21"): "21 days", ("restart", "30"): "30 days",
    ("gf", "none"): "none", ("gf", "30"): "30%", ("gf", "60"): "60%", ("gf", "all"): "all",
    ("medium", "floor"): "nutrient floor", ("medium", "0.20"): "$0.20/L", ("medium", "0.30"): "$0.30/L", ("medium", "0.50"): "$0.50/L",
}
SWITCHES = tuple(replace(sw, settings=tuple(replace(st, short=_SHORT[(sw.key, st.key)]) for st in sw.settings))
                 for sw in SWITCHES)
SW = {s.key: s for s in SWITCHES}
KEYS = tuple(s.key for s in SWITCHES)


def setting(switch: str, key: str) -> Setting:
    for st in SW[switch].settings:
        if st.key == key:
            return st
    raise KeyError(f"{switch}: no setting {key!r}")


def explore_kwargs(choice: dict) -> dict:
    """The floor_physics.explore() arguments for a choice {switch: setting key}.

    GROWTH FACTORS IN THE MEDIUM'S PRICE (2026-11-18, research_notes/growth_factors_in_medium_price.md): the announced and reported
    medium prices ($0.20, $0.30, $0.50 a litre) are complete media, with whatever growth factors the process uses in the price
    (about 0.85 likely; SuperMeat 2024, Pasitka 2024 Table S5, GFI 2020). With one of those, the growth-factor switch adds nothing:
    its cost is already paid. It still applies to the medium at the nutrient floor, which is the nutrients alone. Gated by the
    input sc_medium_complete (on since 2026-11-19)."""
    kw = {}
    for s in SWITCHES:
        kw.update(setting(s.key, choice.get(s.key, "perfusion") if s.key == "mode" else choice[s.key]).kw)
    if kw.get("vm", {}).get("kind") == "cyclic" and kw.get("items", {}).get("seed") == "two":
        # the shared-medium plant's two small seed trains serve runs of ten days or more (plant_items); a fed-batch plant restarts
        # each tank every 3 to 4 days, so it keeps Humbird's full seed train (2026-11-19 restructure)
        kw["items"] = {**kw["items"], "seed": "full"}
    if kw.pop("medium_complete", False) and value("sc_medium_complete") >= 0.5:
        kw["gf_in_medium"] = kw.get("growth_factors", 0.0)   # in the price, and a floor on it: nutrients + growth factors
        kw["growth_factors"] = 0.0
    kw.update(always())
    return kw


def always() -> dict:
    """explore() arguments every scenario carries whatever its switches: the dissolved-oxygen setpoint (sc_do_setpoint,
    about half of air saturation, as pharma holds it; Humbird's tank implies 130%) and the ammonia the cells tolerate
    (sc_nh3_limit, 4 mM since 2026-11-19; Humbird's design keeps his 5). Read at call time, so a test can set
    sc_do_scenarios to 0 to reproduce earlier figures."""
    kw = {"nh3_limit": value("sc_nh3_limit"), "glc_balance": True}      # glucose from the cells' own balance (2026-11-19)
    if value("sc_do_scenarios") >= 0.5:
        kw["do_mmol"] = value("sc_do_setpoint")
    return kw


TRAIT_KEYS = ("nh3_kg", "lac_yield", "doubling_h", "mass_pg")


def cell_traits(choice: dict, **extra) -> dict:
    """The four cell traits a choice gives (cell_traits.TRAITS): ammonia per kilo, lactate per glucose, doubling time, cell mass;
    `extra` overrides them, as run() does."""
    kw = {**explore_kwargs(choice), **extra}
    return {k: float(kw[k]) for k in TRAIT_KEYS}


def run(choice: dict, **extra) -> dict:
    """The model's answer for a choice of settings (floor_physics.explore's result)."""
    return fp.explore(**{**explore_kwargs(choice), **extra})


# ----------------------------------------------------------------------------
# Scenarios
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class Scenario:
    key: str
    name: str
    story: str            # one sentence: what has to go right
    rule: str             # how its settings were chosen
    choice: dict          # {switch: setting}, tank design filled in by `design()`
    alt: tuple = ()       # [(label, {switch: setting}), ...] the same scenario with one assumption changed
    equal_price_share: str = "equal_price_share"   # the input that sets the long-run share at equal price (demand)


_TRICK_LEVELS = ("none", "column", "pressure", "oxygen")     # each setting needs the ones before it to work


def design(choice: dict, tricks_max: str = "oxygen") -> dict:
    """Fill the two tank-design switches (tricks, shape) with the cheapest pair among the settings offered
    that a loop could actually run: a pH-safe loop at a pass rate dense cultures have taken. Everything else
    is as in `choice`. `tricks_max`: the most the tricks can do."""
    best = None
    allowed = _TRICK_LEVELS[:_TRICK_LEVELS.index(tricks_max) + 1]
    for tk in SW["tricks"].settings:
        if tk.key not in allowed:
            continue
        for sh in SW["shape"].settings:
            c = {**choice, "tricks": tk.key, "shape": sh.key}
            r = run(c)
            d = r["column"]
            if d is not None and (d["ph_vs_safe"] > 1.0 + 1e-9 or not d["passes_tested"]):
                continue
            if best is None or r["total"] < best[0] - 1e-12:
                best = (r["total"], c)
    return best[1]


_BASE = {"mode": "perfusion", "cells": "selected", "growth": "36", "plant": "sterile", "gas": "4", "losses": "1", "restart": "14",
         "gf": "30", "medium": "0.20"}
_PUBLISHED = {"cells": "measured", "growth": "43"}
SCENARIOS = {
    # --- the ladder (2026-11-19 restructure): from what has been shown, one kind of change per step, likeliest first -------
    "today": Scenario(
        "today", "1. Published cells: the best meat cells in the published record, grown in batches in a 20 m³ tank",
        "The cells are the best published figure for each trait, never measured together in one line: ammonia and a 43-hour "
        "doubling from bovine fat-precursor cells fed without glutamine (Hubalek 2023), lactate from chicken fibroblasts that turn "
        "most of their glucose into it (Pasitka 2024), and a 2 ng cell (a judgement). Companies may hold better cells they have not "
        "published. They are grown "
        "as a 20 m³ fed-batch: the mode and size that pharma runs and that Upside Foods reports for its process. Nothing washes "
        "their waste out, so the lactate they make stops the batch thin. The plant is food-grade. Medium and growth factors cost "
        "what companies report today.",
        "Each switch at what has been measured, reported or run at this size. Only the medium price and the growth factors are "
        "judgements, because nobody has measured them at scale.",
        {"mode": "fedbatch", **_PUBLISHED, "plant": "sterile", "gas": "2", "tricks": "none", "shape": "tall", "losses": "1",
         "restart": "21", "gf": "60", "medium": "0.30"}),
    "process": Scenario(
        "process", "2. Plus process changes and cheaper inputs",
        "The same cells, still grown in batches in a 20 m³ tank. Medium and growth factors fall to the prices companies announce, "
        "and the tank may take more gas and the tank tricks. A batch this thin needs no more gas, so in fed-batch this step is "
        "mostly the cheaper medium.",
        "Rung 1 with every switch that needs only a change of feed, process or supply moved to the middle of what is reported; "
        "tank design the cheapest the loop checks allow.",
        design({"mode": "fedbatch", **_PUBLISHED, "plant": "sterile", "gas": "4", "losses": "1", "restart": "14",
                "gf": "30", "medium": "0.20"})),
    "selected": Scenario(
        "selected", "3. Plus cells that make less lactate (0.42 mol per mol of glucose) and double every 36 hours, still in batches",
        "Cells on the low-ammonia feed that double every 36 hours (not 43) and make 0.42 mol of lactate per mol of glucose (the "
        "best measured in meat cells is 1.05). Grown in batches in a 20 m³ tank: the batch ends near 37 g/L, held by ammonia, not "
        "14 g/L held by lactate.",
        "the low-lactate example's cells and switches, run as Rung 2 runs (fed-batch in a 20 m³ tank). It needs no new equipment.",
        design({**_BASE, "mode": "fedbatch"})),
    "central": Scenario(
        "central", "4. Plus perfusion (the low-lactate example): waste washed out through a cell filter",
        "The low-lactate example, a reference point defined by its traits: 0.14 mol of ammonia a kilo, 0.42 mol of lactate per mol of glucose, "
        "a doubling every 36 hours and 2 ng a cell (the lactate is below the 1.05 measured in meat cells). The cells, doubling every 36 hours, run in perfusion: fresh medium flows through a 20 m³ tank while a filter loop holds the cells "
        "back, so the waste is washed out and oxygen sets the density (191 g/L, five times the batch's). Nobody has run "
        "animal-cell perfusion above about 4 m³. The plant is food-grade. The tank clears CO₂ without more bubbles.",
        "Every other switch is at the setting nearest the middle "
        "of what is reported. The tank design is the cheapest one that passes the checks on the CO₂ loop.",
        design(dict(_BASE)),
        alt=(("at 30 hours", {"growth": "30"}), ("at 24 hours", {"growth": "24"}), ("in a food-grade plant with shared medium", {"plant": "lean"}))),
    "central_lean": Scenario(
        "central_lean", "5. Plus a food-grade plant with shared medium",
        "This is the low-lactate example in a food-grade plant with a shared medium line, two seed trains and bought oxygen. Nobody "
        "has built one. Its two small seed trains serve only long runs, so it comes after perfusion.",
        "The same as the low-lactate example, but with a food-grade plant with shared medium.",
        design({**_BASE, "plant": "lean"}),
        alt=(("at 30 hours", {"growth": "30"}), ("at 24 hours", {"growth": "24"}))),
    "engineered": Scenario(
        "engineered", "6. Plus cells that make almost no ammonia or lactate (0.055 mol a kilo; 0.28 mol per mol of glucose)",
        "Cells that make almost no waste: 0.055 mol of ammonia a kilo and 0.28 mol of lactate per mol of glucose (Humbird's efficient "
        "cell's metabolism), 2 ng a cell. The best measured in meat cells are 0.14 mol of ammonia a kilo and 1.05 mol of lactate per "
        "mol of glucose. Everything else is as in Rung 5, "
        "so the cells still double every 36 hours and the medium costs $0.20 a litre.",
        "Rung 5 with the kind of cells at its cheapest setting; tank design chosen again.",
        design({**_BASE, "plant": "lean", "cells": "engineered"})),
    "best": Scenario(
        "best", "7. Plus everything else at its favourable end (the all-favourable example)",
        "The all-favourable example, a reference point defined by its traits: 0.055 mol of ammonia a kilo, 0.28 mol of lactate "
        "per mol of glucose, a doubling every 24 hours and 2 ng a cell. The cells need no bought growth factors, the medium costs only what the cells eat, "
        "the tank takes 6 mm/s of gas, and runs are lost less often. Everything works.",
        "Cells, growth speed, plant, gas, growth factors and the medium are at their cheapest setting: the medium costs only what the "
        "cells eat. Losses are at the low end of what makers report, because pharma's 0.2% a day is not assumed. The tank "
        "design is the cheapest one that passes the checks on the CO₂ loop.",
        design({"mode": "perfusion", "cells": "engineered", "growth": "24", "plant": "lean", "gas": "6", "losses": "0.6",
                "restart": "14", "gf": "none", "medium": "floor"}),
        equal_price_share="best_equal_price_share"),
    # --- off the ladder ------------------------------------------------------------------------------------------------
    "cautious": Scenario(
        "cautious", "Cautious: the best meat cells measured so far, in perfusion",
        "The cells are meat cells as they have been measured. They double every 43 hours, and glutamine is replaced in the feed. "
        "The plant is food-grade. The tank gets no more gas than anyone has run. Each lost run is followed by a slow restart.",
        "Each switch is at a setting that has been measured or reported. For growth factors and medium price, nobody has measured "
        "it, so the setting is a cautious judgement. The tank design is the cheapest one that passes the checks on the CO₂ loop.",
        design({"mode": "perfusion", "cells": "measured", "growth": "43", "plant": "sterile", "gas": "2", "losses": "1",
                "restart": "21", "gf": "60", "medium": "0.30"})),
}
# The scenarios the side studies (tank size, thick culture, frontier, audit, ...) were run on; their tests iterate these.
ORDER = ("best", "central", "central_lean", "cautious")
# The reference points from what has been shown to every setting at its favourable end: each row changes one kind of thing
# (RESULTS.md, "The ladder"). Rungs 4, 5 and 7 are exactly the low-lactate example, the low-lactate example with shared medium and the all-favourable example.
LADDER = ("today", "process", "selected", "central", "central_lean", "engineered", "best")
PAGE_ORDER = LADDER


def scenario_choice(key: str, **change) -> dict:
    return {**SCENARIOS[key].choice, **change}


def alt_cost(key: str, change: dict) -> float:
    """Cost of a scenario with one assumption changed and the tank design chosen again for the new case."""
    return run(design({**SCENARIOS[key].choice, **change}))["total"]


REFERENCE_NAME = "Humbird's optimistic design: his enhanced cells in an ordinary perfusion tank"
# Humbird's enhanced cell as traits (explore() at its defaults; lactate 0.5 per glucose burned or fermented = 0.279 on all glucose)
HUMBIRD_TRAITS = {"nh3_kg": 0.054, "lac_yield": 0.279, "doubling_h": 24.0, "mass_pg": 3000.0}


def reference() -> dict:
    """Humbird's optimistic design (the old 'floor'): floor_physics.explore() at its defaults. A standard 20 m3 stirred tank in
    perfusion at 120 g/L, a food-grade plant, cells that make almost no ammonia or lactate, no tank tricks, no losses, no growth factors. It assumes the
    hardest change (cells that make almost no ammonia or lactate) and none of the easy ones (tank tricks), so it is not a rung of the LADDER. Kept so the
    Humbird cross-checks and the golden tests still make sense."""
    return fp.explore()


def reported_cost() -> float:
    """The process one company reports (SuperMeat 2024): cells $/kg at the model's default medium price and plant."""
    from cost_model import CostParams, biomass_cost
    return float(biomass_cost(CostParams()))


# ----------------------------------------------------------------------------
# What a scenario needs
# ----------------------------------------------------------------------------
def needs(choice: dict) -> list:
    """[(switch name, setting label, tag)] for every switch whose setting needs something new, hardest first."""
    rows = [(SW[k].name, setting(k, choice[k]).label, setting(k, choice[k]).tag) for k in KEYS]
    rows.sort(key=lambda r: -TAG_ORDER.index(r[2]))
    return rows


def hardest_need(choice: dict) -> str:
    return max((setting(k, choice[k]).tag for k in KEYS), key=TAG_ORDER.index)


LIMIT_PLAIN = {"CO2 removal": "clearing CO₂ from the tank", "oxygen supply": "getting oxygen into the tank",
               "mixing": "mixing the tank", "thickness of the culture": "how thick the culture can be",
               "waste build-up": "waste building up", "other by-products": "other by-products"}
MEDIUM_PLAIN = {"ammonia": "washing out ammonia", "lactate": "washing out lactate", "least flow": "the least flow the cells need",
                "nutrients": "the nutrients the cells eat", "salt": "salt from the sorbent",
                "harvest": "the liquid that leaves with the harvested cells"}


# ----------------------------------------------------------------------------
# The tank tricks a scenario relies on, and what it costs without them
# ----------------------------------------------------------------------------
_TRICK_PARTS = {"column": ("a column beside the tank that strips CO\u2082 without bubbles",),
                "pressure": ("a column beside the tank that strips CO\u2082 without bubbles", "1 bar of extra pressure in the tank"),
                "oxygen": ("a column beside the tank that strips CO\u2082 without bubbles", "1 bar of extra pressure in the tank",
                           "pure oxygen recycled through the column")}
_ASPECT_PLAIN = {"flat": "a tank whose liquid is half as deep as it is wide", "squat": "a tank whose liquid is 0.75 times as deep as it is wide",
                 "square": "a tank whose liquid is as deep as it is wide"}


def tricks_report(choice: dict) -> dict:
    """What the tank design of a scenario relies on that nobody has run with animal cells, and the cost without it.
    `no_tricks`: the same tank shape with gas bubbled in at the base (tricks switch at 'none'). `ordinary_tank`:
    Humbird's tall tank as well. `used`: the tricks, in words (empty for an ordinary tank)."""
    used = list(_TRICK_PARTS.get(choice["tricks"], ())) + ([_ASPECT_PLAIN[choice["shape"]]] if choice["shape"] != "tall" else [])
    base = run(choice)["total"]
    no_tricks = run({**choice, "tricks": "none"})["total"]
    ordinary = run({**choice, "tricks": "none", "shape": "tall"})["total"]
    return {"used": used, "cost": base, "no_tricks": no_tricks, "ordinary_tank": ordinary,
            "d_no_tricks": no_tricks - base, "d_ordinary": ordinary - base}


def plain_list(items) -> str:
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + ", and " + items[-1]


def tricks_sentence(choice: dict) -> str:
    t = tricks_report(choice)
    if not t["used"]:
        return ""
    return (f"Nobody has run this tank design with animal cells. It uses {plain_list(t['used'])}. "
            f"Without these tricks, a kilo costs ${t['no_tricks']:.1f} in a tank of the same shape. That is ${t['d_no_tricks']:.1f} more. "
            f"In the ordinary tall tank, a kilo costs ${t['ordinary_tank']:.1f}.")


def growth_sentence(key: str) -> str:
    """The reasoning behind a scenario's doubling time, where it needs one (computed costs)."""
    if key not in ("central", "central_lean"):
        return ""
    c = SCENARIOS[key].choice
    base = run(design(c))["total"]
    fast = alt_cost(key, {"growth": "24"})
    mid = alt_cost(key, {"growth": "30"})
    return ("The 36-hour doubling time is the author's judgement. Meat-cell cultures that make little waste have doubled in 43 to 54 hours. "
            "Only cultures fed glutamine have doubled in about 26 hours, and glutamine is what makes the waste (Hubalek 2023). "
            "The author thinks 24 hours at this waste level has about a 10% chance. "
            f"A 24-hour doubling would save ${base - fast:.1f} a kilo. A 30-hour doubling would save ${base - mid:.1f}.")


def story_text(key: str) -> str:
    """A scenario's story with what it relies on spelled out (the page's sentence under each scenario's name)."""
    sc = SCENARIOS[key]
    return " ".join(x for x in (sc.story, tricks_sentence(sc.choice), growth_sentence(key)) if x)


# ----------------------------------------------------------------------------
# Shares
# ----------------------------------------------------------------------------
_DP = None


def _demand():
    global _DP
    if _DP is None:
        from market_share import DemandParams
        _DP = DemandParams()
    return _DP


_DPS: dict = {}


def demand_for(eqs_input: str = "equal_price_share"):
    """The demand model with the long-run share at equal price taken from this input (the all-favourable example has its own)."""
    if eqs_input == "equal_price_share":
        return _demand()
    if eqs_input not in _DPS:
        from market_share import DemandParams
        _DPS[eqs_input] = DemandParams(equal_price_share=value(eqs_input))
    return _DPS[eqs_input]


def eqs_of(key: str | None) -> str:
    """The demand input a scenario uses (None, or a key that is not a scenario: the central one)."""
    return SCENARIOS[key].equal_price_share if key in SCENARIOS else "equal_price_share"


def shares(cost: float, regions=("global", "us", "eu"), eqs: str = "equal_price_share") -> dict:
    """Long-run share of meat sold by weight, %, by region, if cells cost `cost` $/kg (everything else at the
    model's central demand settings, or with the share at equal price from the input `eqs`)."""
    import meat_market as mm
    dp = demand_for(eqs)
    return {r: mm.penetration(mm.MARKETS[r], cost, income=mm.REGION_INCOME[r], pr=dp)[1] * 100.0 for r in regions}


def summary(choice: dict | None = None, r: dict | None = None, cost: float | None = None, eqs: str = "equal_price_share") -> dict:
    """Everything the scenario table shows for one choice (or, with `r`/`cost`, for an explore result)."""
    from inputs import value as v
    if r is None:
        r = run(choice)
    cost = r["total"] if cost is None else cost
    retail, pconv = shelf_price(cost), v("p_conv")
    sh = shares(cost, eqs=eqs)
    return {"cost": cost, "retail": retail, "ratio": retail / pconv, "world": sh["global"], "us": sh["us"],
            "eu": sh["eu"], "density": r["density"], "limit": r["limit"], "limit_plain": LIMIT_PLAIN.get(r["limit"], r["limit"]),
            "medium_l": r["medium_l"], "medium_set_by": r["medium_set_by"], "uptime": r["uptime"], "output": r["output"]}


# ----------------------------------------------------------------------------
# What to prioritise
# ----------------------------------------------------------------------------
def priorities(choice: dict, with_share: bool = True) -> list:
    """For each switch, the cost if it moved to each of its settings (the rest as in `choice`). Rows, widest
    swing first: {switch, name, now, best, worst, costs, d_best, d_worst, share_best, share_worst}."""
    base = run(choice)["total"]
    base_sh = shares(base)["global"] if with_share else None
    rows = []
    for sw in SWITCHES:
        costs = {st.key: run({**choice, sw.key: st.key})["total"] for st in sw.settings}
        kb = min(costs, key=lambda k: costs[k])
        kw_ = max(costs, key=lambda k: costs[k])
        row = {"switch": sw.key, "name": sw.name, "now": choice[sw.key], "costs": costs, "best": kb, "worst": kw_,
               "d_best": costs[kb] - base, "d_worst": costs[kw_] - base}
        if with_share:
            row["share_best"] = shares(costs[kb])["global"] - base_sh
            row["share_worst"] = shares(costs[kw_])["global"] - base_sh
        rows.append(row)
    return sorted(rows, key=lambda r: -(r["d_worst"] - r["d_best"]))


def grid(choice: dict, a: str, b: str) -> dict:
    """Cost for every pair of settings of switches a and b, the rest as in `choice`."""
    ra = [st.key for st in SW[a].settings]
    rb = [st.key for st in SW[b].settings]
    return {"a": a, "b": b, "rows": ra, "cols": rb,
            "cost": [[run({**choice, a: i, b: j})["total"] for j in rb] for i in ra]}


def interactions(choice: dict, top: int = 4, min_gap: float = 0.25) -> list:
    """Pairs of switches whose effects do not add up, as sentences computed from the model. For each pair (A, B) the
    cost saved by moving A to its cheapest setting is found with B as it is, and with B at its own cheapest
    setting; if the two differ by more than `min_gap` $/kg the pair is reported, largest gap first."""
    base = run(choice)["total"]
    best = {}
    for sw in SWITCHES:
        c = {st.key: run({**choice, sw.key: st.key})["total"] for st in sw.settings}
        k = min(c, key=lambda x: c[x])
        best[sw.key] = (k, base - c[k])
    out = []
    for i, a in enumerate(KEYS):
        for b in KEYS[i + 1:]:
            ka, ga = best[a]
            kb, gb = best[b]
            if ka == choice[a] or kb == choice[b]:
                continue
            both = run({**choice, a: ka, b: kb})["total"]
            only_b = run({**choice, b: kb})["total"]
            only_a = run({**choice, a: ka})["total"]
            ga_with_b = only_b - both           # what A saves once B has been moved
            gb_with_a = only_a - both
            gap = ga_with_b - ga
            if abs(gap) < min_gap:
                continue
            sa, sb = SW[a], SW[b]
            la, lb = setting(a, ka).label, setting(b, kb).label
            how = "The two overlap, because one does part of the other's job." if gap < 0 else "The two reinforce each other."
            out.append({"a": a, "b": b, "gap": gap, "ga": ga, "ga_with_b": ga_with_b, "gb": gb, "gb_with_a": gb_with_a,
                        "text": f"Setting {sa.name.lower()} to \u201c{la}\u201d would save ${ga:.1f} a kilo as things stand. "
                                f"It would save ${ga_with_b:.1f} if {sb.name.lower()} were \u201c{lb}\u201d. {how}"})
    # ties (two pairs with the same gap to nine decimals) keep the switches' order, so the page's JavaScript sorts alike
    return sorted(out, key=lambda r: (-round(abs(r["gap"]), 9), KEYS.index(r["a"]), KEYS.index(r["b"])))[:top]


# ----------------------------------------------------------------------------
# The uncertainty in the estimates behind a scenario
# ----------------------------------------------------------------------------
# Triangular (low, mode, high) multipliers on the scenario's own estimates. The scenario's switches are held: the
# band is how far the number could be off if its assumptions hold. Cell traits and speed are switches, so they are
# not drawn here; the tornado (priorities) shows what they are worth.
MC_PRIORS = {
    "capex_x": (0.34, 1.0, 1.5),          # as FLOOR_PRIORS: Humbird's estimate 'within 50%'; two published designs at a third
    "medium_price": (0.6, 1.0, 1.5),      # announced $0.20/L to reported $0.50/L around the setting
    "hazard": (0.3, 1.0, 2.0),            # makers report 0.6-2.2% a day; large pharma plants 0.2%
}
# Since 2026-11-16 the bands also draw the estimates the cost rests on most (answer_rests_on.py), each from its own prior in
# inputs.py: the ammonia the cells tolerate, the protectant's price and dose, the least medium flow, antifoam's cost to
# oxygen transfer and the membrane's price. A scenario that sets one of them itself keeps its own value. Not drawn: the gas
# flow (a switch); the glucose a cell burns per kg (a trait of the cells, which the kind-of-cells switch holds, as it holds
# their ammonia and lactate; drawn, it would double the all-favourable example's median); and the salt the cells tolerate (drawn, it
# moves the all-favourable example's median by about $0.1 and makes each band forty times slower, because a lower limit sets off the
# CO2-level search in explore). The ammonia the cells tolerate is drawn because no switch sets it: every scenario takes
# sc_nh3_limit (4 mmol/L since 2026-11-19; Humbird's optimistic design keeps his 5).
# `sc_wide_bands` = 0 restores the narrower bands.
MC_ESTIMATES = (("nh3_limit", "pf_nh3_limit"), ("protectant_price", "pf_protectant_price"),
                ("min_perfusion", "pf_min_perfusion"), ("antifoam_otr", "pf_antifoam_otr"))
MC_SCENARIO_PRIORS = {"nh3_limit": "sc_nh3_limit"}      # set by always() for every scenario; Humbird's design draws pf_nh3_limit
MC_ESTIMATE_INPUTS = ("pf_protectant_dose", "rt_membrane_price", "aa_bulk_price")    # no explore() argument: set in the datasheet per draw


def scenario_mc(choice: dict | None, n: int = 1000, seed: int = 0, traits: dict | None = None) -> dict:
    """Cost ($/kg) with the estimates behind a scenario uncertain: plant cost, financing, life of the retention membranes, upkeep
    share of respiration, medium price and loss rate, and (MC_ESTIMATES) the estimates the cost rests on most, drawn from
    their priors; the scenario's switches held. `choice=None` is
    Humbird's optimistic design (`reference()`, explore() at its defaults), drawn the same way.
    `traits` ({nh3_kg, lac_yield, doubling_h, mass_pg}, any subset) sets cell traits directly (2026-11-19): a trait set by the reader
    is held, not drawn (the draws are still made, so the other draws do not move)."""
    rng = np.random.default_rng(seed)
    kw0 = explore_kwargs(choice) if choice is not None else {}
    traits = dict(traits or {})
    kw0.update(traits)
    pri = dict(MC_PRIORS)
    if choice is not None and choice["plant"] == "lean":                       # not below a plant with everything animal cells must have
        lean = plant_items.capital("lean")["total"]
        pri["capex_x"] = (min(1.0, plant_items.capital("yeastplus")["total"] / lean), 1.0, 1.5)
    tri = lambda lo, mode, hi: rng.triangular(lo, mode, hi, n)       # the ranges of MC_PRIORS (multipliers, not inputs)
    reg_draw = lambda name: draw(name, rng, n)                      # a registry input from its own prior (inputs.draw)
    d = {"capex_x": tri(*pri["capex_x"]), "medium_price": tri(*pri["medium_price"]) * kw0.get("medium_price", 0.15),
         "hazard": tri(*pri["hazard"]) * kw0.get("hazard", 0.0)}
    for key, name in (("charge", "plant_charge_mature"), ("membrane_life", "rt_membrane_life"),
                      ("maintenance_share", "pf_maintenance_share")):
        d[key] = reg_draw(name)
    reg = {}
    if value("sc_wide_bands") >= 0.5 and choice is not None and choice["cells"] in ("selected", "measured"):
        # the ammonia these cells make was measured once (audit 2026-11-19: the third-largest estimate under the low-lactate example). The
        # 0.055 mol/kg setting is not drawn: the all-favourable example assumes cells that reach Humbird's figure.
        d["nh3_kg"] = reg_draw("sc_nh3_selected")
    if value("sc_wide_bands") >= 0.5:                  # drawn after the others, so their draws are unchanged
        for key, name in MC_ESTIMATES:
            if key in MC_SCENARIO_PRIORS and choice is not None:      # the scenarios' own setting, with its own range
                d[key] = reg_draw(MC_SCENARIO_PRIORS[key])
            elif key not in kw0:
                d[key] = reg_draw(name)
        for name in MC_ESTIMATE_INPUTS:
            reg[name] = reg_draw(name)
        if choice is not None:                         # 2026-11-19: the weight of a cell, the same for every kind of cells, drawn
            d["mass_pg"] = reg_draw("sc_mass_selected_pg")   # last, so the other draws are unchanged

    for k in traits:                                   # held at the reader's value
        d.pop(k, None)

    def one(i: int) -> float:
        kw = {**kw0, **{k: float(v[i]) for k, v in d.items()}}
        if not reg:
            return fp.explore(**kw)["total"]
        with fp._inputs_set({k: float(v[i]) for k, v in reg.items()}):
            return fp.explore(**kw)["total"]
    cost = np.array([one(i) for i in range(n)])
    return {"total": cost, **d, **reg}


def scenario_share_mc(choice: dict | None, region: str = "global", n: int = 1000, seed: int = 0,
                      eqs: str = "equal_price_share", traits: dict | None = None) -> dict:
    """Cost and demand uncertain together: each draw takes a cost from scenario_mc and the demand dials from their priors."""
    import meat_market as mm
    cost = scenario_mc(choice, n, seed, traits=traits)["total"]
    mc = mm.monte_carlo(region, n, seed=seed + 1, biomass=cost, equal_share_input=eqs)
    return dict(vol=mc["vol"], val=mc["val"], cost=cost)


# draws behind every headline band: the share's median moves by about 0.3 points between seeds at 1,000 draws, much less at 4,000
BAND_N = 4000
_BANDS: dict = {}


def bands(choice: dict | None, n: int = BAND_N, eqs: str = "equal_price_share", traits: dict | None = None) -> dict:
    """10th / 50th / 90th percentile of cost and of the world's long-run share by weight (cost and demand both
    uncertain). The 50th percentile of the share is the page's headline share for a scenario; the share at the
    scenario's own point cost (`summary(...)['world']`) is a different number and is labelled a point estimate."""
    key = (tuple(sorted(choice.items())) if choice is not None else "reference", n, eqs, tuple(sorted((traits or {}).items())))
    if key not in _BANDS:
        mc = scenario_share_mc(choice, "global", n, eqs=eqs, traits=traits)
        q = lambda a: tuple(float(x) for x in np.percentile(a, [10, 50, 90]))
        _BANDS[key] = {"cost": q(mc["cost"]), "share": q(mc["vol"])}
    return _BANDS[key]


# ----------------------------------------------------------------------------
# What it would take (2026-11-19): the cost of cells a share needs, and trait sets that reach it, deterministic, no odds
# ----------------------------------------------------------------------------
WIT_TARGETS = (1.0, 10.0)                 # long-run share of world meat and seafood, %
WIT_BUYERS = (None, 0.50)                 # share of meat buyers who pick cultivated meat at equal price: the model's own, and 50%
_EQ_ALL: dict = {}
_DP_V: dict = {}


def all_choices_for_meat_buyers(f: float) -> float:
    """The share-at-equal-price dial (of all choices) that gives `f` of meat buyers, x / (x + c), at neutral settings."""
    if f not in _EQ_ALL:
        import market_share as M
        pr = _demand()
        g = lambda e: M.share(1.0, pr, accept_x=1.0, theta_free_M=0.0, neophobia_x=0.0, health_x=0.0, equal_share=e, which="x_meat")
        lo, hi = 0.001, 0.79
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if g(mid) < f else (lo, mid)
        _EQ_ALL[f] = 0.5 * (lo + hi)
    return _EQ_ALL[f]


def meat_buyers_at_equal_price(eq_all: float | None = None) -> float:
    """The share of meat buyers who pick cultivated meat at equal price, at the dial `eq_all` (None: the model's own)."""
    import market_share as M
    pr = _demand()
    e = value("equal_price_share") if eq_all is None else eq_all
    return M.share(1.0, pr, accept_x=1.0, theta_free_M=0.0, neophobia_x=0.0, health_x=0.0, equal_share=e, which="x_meat")


def world_share(cost: float, buyers: float | None = None) -> float:
    """Long-run share of world meat and seafood, %, at `cost` $/kg of cells, with `buyers` of meat buyers picking it at equal price
    (None: the model's own 14.5%)."""
    import meat_market as mm
    if buyers is None:
        return shares(cost)["global"]
    if buyers not in _DP_V:
        from market_share import DemandParams
        _DP_V[buyers] = DemandParams(equal_price_share=all_choices_for_meat_buyers(buyers))
    return mm.penetration(mm.MARKETS["global"], cost, income=mm.REGION_INCOME["global"], pr=_DP_V[buyers])[1] * 100.0


def cost_for_share(target: float, buyers: float | None = None) -> float | None:
    """The cost of cells, $/kg, at which the long-run world share is `target` % (None if not reached even at $0.5)."""
    lo, hi = 0.5, 400.0
    if world_share(lo, buyers) < target:
        return None
    for _ in range(50):
        mid = (lo * hi) ** 0.5
        lo, hi = (mid, hi) if world_share(mid, buyers) >= target else (lo, mid)
    return lo


# the trait sets tried (each with the low-lactate example's other switches, a plant and a mode, tank design chosen): the published
# value of each trait, the low-lactate example's, the all-favourable example's and one better still
WIT_GRID = {"nh3_kg": (0.14, 0.055, 0.0), "lac_yield": (1.05, 0.42, 0.279, 0.0), "doubling_h": (43.0, 36.0, 25.7, 20.0, 15.0)}
WIT_CHOICES = tuple((p, m) for p in ("sterile", "lean") for m in ("perfusion", "fedbatch"))
_WIT: list = []


def beyond_measured(tr: dict) -> dict:
    """How far a trait set goes beyond what has been measured in meat cells (cell_traits.best_in_meat_cells): the traits set better
    than the best measurement, how far as a fraction of it, and the words. Data only: no route."""
    import cell_traits as CT
    best = CT.best_in_meat_cells()
    ks = CT.beyond_measured(tr)
    gap = sum((best[t]["value"] - tr[t]) / best[t]["value"] if best[t]["dir"] < 0 else (tr[t] - best[t]["value"]) / best[t]["value"]
              for t in ks)
    return {"beyond": ks, "gap": gap, "text": CT.beyond_text(tr)}


def trait_grid() -> list:
    """[(cost, traits, plant, mode, beyond_measured)] for every set in WIT_GRID x WIT_CHOICES, at most likely values, cells of 2 ng."""
    if not _WIT:
        base = {k: v for k, v in SCENARIOS["central"].choice.items() if k not in ("tricks", "shape", "plant", "mode")}
        mass = value("sc_mass_selected_pg")
        for a in WIT_GRID["nh3_kg"]:
            for l in WIT_GRID["lac_yield"]:
                for t in WIT_GRID["doubling_h"]:
                    tr = {"nh3_kg": a, "lac_yield": l, "doubling_h": t, "mass_pg": mass}
                    rn = beyond_measured(tr)
                    for p, m in WIT_CHOICES:
                        c = _design_traits({**base, "plant": p, "mode": m}, tr)
                        _WIT.append((run(c, **tr)["total"], tr, p, m, rn, c))
    return _WIT


def _design_traits(choice: dict, traits: dict) -> dict:
    """design() for a choice with its cell traits set directly."""
    best = None
    for tk in SW["tricks"].settings:
        for sh in SW["shape"].settings:
            c = {**choice, "tricks": tk.key, "shape": sh.key}
            r = run(c, **traits)
            d = r["column"]
            if d is not None and (d["ph_vs_safe"] > 1.0 + 1e-9 or not d["passes_tested"]):
                continue
            if best is None or r["total"] < best[0] - 1e-12:
                best = (r["total"], c)
    return best[1]


def what_it_would_take() -> list:
    """For each target share and each level of liking: the cost of cells needed, and the trait set in the grid that reaches it
    with the fewest traits beyond the best measured in meat cells, then the shortest way beyond (the sum of each such trait's
    distance past its measurement, as a fraction of it), then the least ambitious (the dearest that still reaches it). Since
    2026-11-19 the rule rests on measurements only, not on which route might give a trait (the author's direction)."""
    rows = []
    grid = trait_grid()
    for b in WIT_BUYERS:
        for tgt in WIT_TARGETS:
            need = cost_for_share(tgt, b)
            ok = [g for g in grid if need is not None and g[0] <= need]
            pick = min(ok, key=lambda g: (len(g[4]["beyond"]), round(g[4]["gap"], 9), -g[0])) if ok else None
            rows.append({"target": tgt, "buyers": meat_buyers_at_equal_price() if b is None else b, "need": need, "pick": pick,
                         "within_measured": any(not g[4]["beyond"] for g in ok)})
    return rows


def _traits_text(tr: dict) -> str:
    return (f"ammonia {tr['nh3_kg']:g} mol/kg, lactate {tr['lac_yield']:g} mol/mol, a doubling every {tr['doubling_h']:g} h, "
            f"{tr['mass_pg'] / 1000:g} ng")


def what_it_would_take_markdown() -> str:
    """The table RESULTS.md leads with (section 1 and the Summary)."""
    plant = {"sterile": "a food-grade plant", "lean": "a food-grade plant with shared medium"}
    out = ["| long-run share of world meat and seafood | with this share of meat buyers picking it at equal price | cells must cost "
           "(most likely values) | the cells tried that reach it with the fewest traits beyond the best measured in meat cells | at | "
           "traits beyond the best measured in meat cells (each against its own best measurement) |",
           "|---|---|---|---|---|---|"]
    for r in what_it_would_take():
        need = "out of reach: not even at $0.5" if r["need"] is None else f"${r['need']:.1f} a kilo or less"
        if r["pick"] is None:
            pk, at, ver = "none of the sets tried", "", ""
        else:
            cost, tr, p, m, rn, _c = r["pick"]
            pk = _traits_text(tr)
            at = f"${cost:.1f}, {plant[p]}, {'perfusion' if m == 'perfusion' else 'fed-batch at 20 m³'}"
            ver = rn["text"]
        out.append(f"| {r['target']:g}% | {r['buyers']:.1%} | {need} | {pk} | {at} | {ver} |")
    return "\n".join(out)


# ----------------------------------------------------------------------------
# The plant-cost axis: perfusion against fed-batch as the plant gets cheaper (2026-11-19 restructure)
# ----------------------------------------------------------------------------
PLANT_MULTS = (1.0, 0.75, 0.5, 0.34)            # the bands' range for the plant estimate: as modelled down to a third
PLANT_AXIS_CASES = (("process", "Published cells (rung 2's switches)"), ("central", "Low-lactate example (the low-lactate example's switches, rungs 3–4)"),
                    ("central_lean", "Low-lactate example, plant with shared medium (rung 5)"),
                    ("engineered", "Cells that make almost no ammonia or lactate (rung 6)"), ("best", "The all-favourable example's switches (rung 7)"))
AXIS_MODES = ("perfusion", "fedbatch", "fedbatch100")


def plant_axis(key: str, mults=PLANT_MULTS) -> dict:
    """For a rung's switches: cost in perfusion and in fed-batch at 20 and 100 m³, each with its tank design chosen at the plant's
    modelled cost, at each multiplier on the plant's cost (capex_x: buildings and tanks; not the filter loop or the column), and
    the multiplier below which each fed-batch is cheaper than perfusion (None if not between 0.05 and 1.5)."""
    base = {k: v for k, v in SCENARIOS[key].choice.items() if k not in ("mode", "tricks", "shape")}
    ch = {m: design({**base, "mode": m}) for m in AXIS_MODES}
    cost = lambda m, x: run(ch[m], capex_x=x)["total"]
    out = {"choices": ch, "cost": {m: {x: cost(m, x) for x in mults} for m in AXIS_MODES}, "cross": {}}
    for m in ("fedbatch", "fedbatch100"):
        f = lambda x: cost("perfusion", x) - cost(m, x)
        lo, hi = 0.05, 1.5
        if f(lo) * f(hi) > 0:
            out["cross"][m] = None
            continue
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if f(mid) * f(lo) > 0 else (lo, mid)
        out["cross"][m] = 0.5 * (lo + hi)
    return out


def plant_axis_markdown() -> str:
    out = ["| switches as in | $/kg with the plant at its modelled cost: perfusion / fed-batch 20 m³ / fed-batch 100 m³ | "
           + " | ".join(f"plant at {x:g}×" for x in PLANT_MULTS[1:])
           + " | fed-batch at 20 m³ is cheaper with the plant below | fed-batch at 100 m³, below |",
           "|---|" + "---|" * (len(PLANT_MULTS) + 2)]
    for key, lab in PLANT_AXIS_CASES:
        a = plant_axis(key)
        cells = [" / ".join(f"{a['cost'][m][x]:.1f}" for m in AXIS_MODES) for x in PLANT_MULTS]
        cr = lambda m: "never (0.05–1.5×)" if a["cross"][m] is None else f"{a['cross'][m]:.2f}×"
        out.append(f"| {lab} | " + " | ".join(cells) + f" | {cr('fedbatch')} | {cr('fedbatch100')} |")
    return "\n".join(out)


# ----------------------------------------------------------------------------
# For the page
# ----------------------------------------------------------------------------
_JS_NAME = {"gas_velocity": "gas_v", "p_top_barg": "p_top", "restart_fail_days": "restart_fail"}


def _js_params(kw: dict) -> dict:
    out = {}
    for k, v in kw.items():
        if k == "items":
            out["plantKey"] = "lean"                  # the page looks the items up (C.fx.plant_items.lean)
        elif k == "plant":
            out["plantKey"] = {"sanitary": "sterile", "pharma": "pharma"}[v]
        else:
            out[_JS_NAME.get(k, k)] = v
    return out


def js_model() -> dict:
    """The switches, settings and presets the page's JavaScript runs (it mirrors run / priorities / interactions)."""
    sw = [{"key": s.key, "name": s.name, "q": s.question,
           "settings": [{"key": t.key, "label": t.label, "short": t.short, "tag": t.tag, "note": t.note,
                         "p": _js_params(t.kw)} for t in s.settings]} for s in SWITCHES]
    presets = {k: {"name": SCENARIOS[k].name, "story": story_text(k), "choice": SCENARIOS[k].choice,
                   "eqs": value(SCENARIOS[k].equal_price_share)}
               for k in SCENARIOS}
    band = {k: bands(SCENARIOS[k].choice, eqs=eqs_of(k)) for k in SCENARIOS}
    return {"switches": sw, "keys": list(KEYS), "presets": presets, "order": list(PAGE_ORDER), "start": "central",
            "medium_complete_on": value("sc_medium_complete") >= 0.5,
            "always": _js_params(always()),
            "tags": list(TAG_ORDER), "tag_plain": TAG_PLAIN, "limit_plain": LIMIT_PLAIN, "medium_plain": MEDIUM_PLAIN,
            "best_cost": run(SCENARIOS["best"].choice)["total"], "mc_priors": MC_PRIORS, "bands": band,
            # cells as traits (2026-11-19): each reference point's traits (the page shows only what has been measured in meat cells)
            "traits": {k: cell_traits(SCENARIOS[k].choice) for k in SCENARIOS}}


def reported_band(n: int = 30000) -> tuple:
    """10th / 50th / 90th percentile of the world's long-run share for the process a company reports, with its cost and demand
    uncertain (meat_market.monte_carlo at the default cost model; RESULTS.md section 4 uses the same draw)."""
    import meat_market as mm
    if "reported" not in _BANDS:
        v = mm.monte_carlo("global", n)["vol"]
        _BANDS["reported"] = tuple(float(x) for x in np.percentile(v, [10, 50, 90]))
    return _BANDS["reported"]


def table_rows() -> list:
    """Every row of the headline table: the ladder, Humbird's optimistic design, the reported process.
    Each row: name, cost point, cost band (or None), ratio, share at the point cost, share band (P10, P50, P90), and which of its
    cells' traits are set beyond the best measured in meat cells (cell_traits.best_in_meat_cells; data only, since 2026-11-19)."""
    import cell_traits as CT
    names = {"nh3_kg": "ammonia", "lac_yield": "lactate", "doubling_h": "doubling time", "mass_pg": "cell mass"}
    beyond = lambda tr: ", ".join(names[t] for t in CT.beyond_measured(tr)) or "none"
    rows = []
    for key in PAGE_ORDER:
        sc = SCENARIOS[key]
        sm, b = summary(sc.choice, eqs=sc.equal_price_share), bands(sc.choice, eqs=sc.equal_price_share)
        rows.append((sc.name, sm["cost"], b["cost"], sm["ratio"], sm["world"], b["share"], beyond(cell_traits(sc.choice))))
    rs, b = summary(r=reference()), bands(None)
    rows.append((REFERENCE_NAME, rs["cost"], b["cost"], rs["ratio"], rs["world"], b["share"], beyond(HUMBIRD_TRAITS)))
    rc = reported_cost()
    rows.append(("As a company reports (SuperMeat 2024)", rc, None, shelf_price(rc) / value("p_conv"),
                 shares(rc)["global"], reported_band(), "a company's own report"))
    return rows


def pct_num(x: float) -> str:
    """A share in percent as text: one decimal from 0.1 up, two below it, three below 0.01 (so 0.04 does not print as 0.0)."""
    if x < 0.00095:
        return "under 0.001"
    return f"{x:.3f}" if x < 0.0095 else f"{x:.2f}" if x < 0.095 else f"{x:.1f}"


def markdown_table() -> str:
    """The headline table as Markdown (RESULTS.md, METHODS.md and research_notes/cost_scenarios.md quote it). Every row gives both the
    share at its own point cost and the median of draws in which cost and demand are uncertain, so rows can be compared."""
    out = ["| scenario | cells, $/kg: median of draws (8 in 10 between) | $/kg if every estimate lands on its most likely value | "
           "shop price against $12 meat, at the median | share of world meat and seafood, long run: median of draws (8 in 10 between) | "
           "share at the most-likely-values cost | cell traits set beyond the best measured in meat cells |", "|---|---|---|---|---|---|---|"]
    for name, cost, cb, ratio, world, sb, need in table_rows():
        if cb is not None:                   # the headline is the median of the draws; the point is the most-likely-values figure
            head, ratio = f"**${cb[1]:.0f}** (${cb[0]:.0f}\u2013{cb[2]:.0f})", shelf_price(cb[1]) / value("p_conv")
        else:
            head = f"**${cost:.0f}** (its own point figure)"
        rng = "" if sb[2] < 0.00095 else f" ({pct_num(sb[0])}\u2013{pct_num(sb[2])}%)"      # nothing to show when it is all under 0.001%
        if sb[0] < 0.00095 and 0.00095 <= sb[2] < 0.0095:          # the range would read "under 0.001-0.001%": say where 9 in 10 fall
            e = 10.0 ** np.floor(np.log10(sb[2]))
            rng = f" (9 in 10 draws under {np.ceil(sb[2] / e) * e:.3f}%)"
        out.append(f"| {name} | {head} | ${cost:.1f} | {ratio:.1f}\u00d7 | **{pct_num(sb[1])}%**{rng} | {pct_num(world)}% | {need} |")
    return "\n".join(out)


# ----------------------------------------------------------------------------
def main() -> None:
    import sys
    if "--markdown" in sys.argv:
        print(markdown_table())
        return
    ref = reference()
    print(f"Reference (what earlier versions called the floor): standard perfusion tank, no tricks: ${ref['total']:.2f}/kg, "
          f"{ref['density']:.0f} g/L ({ref['limit']}), world share {shares(ref['total'])['global']:.1f}%")
    print(f"As a company reports: ${reported_cost():.2f}/kg, world share {shares(reported_cost())['global']:.1f}%\n")
    for key in ORDER:
        sc = SCENARIOS[key]
        s = summary(sc.choice, eqs=sc.equal_price_share)
        b = bands(sc.choice, eqs=sc.equal_price_share)
        print(f"{sc.name}\n  {story_text(key)}\n  rule: {sc.rule}")
        print(f"  ${s['cost']:.2f}/kg cells, ${s['retail']:.1f} in the shop, {s['ratio']:.2f}x US minced beef or pork cuts ($12 a kilo); world {b['share'][1]:.1f}% median ({b['share'][0]:.1f}\u2013{b['share'][2]:.1f}%), point estimate {s['world']:.1f}% "
              f"(US {s['us']:.1f}%, Europe {s['eu']:.1f}%); {s['density']:.0f} g/L, limited by {s['limit']}; {s['medium_l']:.0f} L/kg "
              f"set by {s['medium_set_by']}; hardest need: {hardest_need(sc.choice)}")
        print("  settings: " + "; ".join(f"{SW[k].name}: {setting(k, sc.choice[k]).label}" for k in KEYS))
        for lab, ch in sc.alt:
            print(f"    {lab}: ${alt_cost(key, ch):.2f}")
        print("  what moves it (cost if one switch went to its best / worst setting):")
        for p in priorities(sc.choice)[:6]:
            print(f"    {p['name']:<22} best {setting(p['switch'], p['best']).label[:34]:<34} {p['d_best']:+6.2f}"
                  f"   worst {setting(p['switch'], p['worst']).label[:34]:<34} {p['d_worst']:+6.2f}")
        for it in interactions(sc.choice):
            print("   *", it["text"])
        b = bands(sc.choice, eqs=sc.equal_price_share)
        print(f"  band (P10-P50-P90): cost ${b['cost'][0]:.1f} / {b['cost'][1]:.1f} / {b['cost'][2]:.1f}; "
              f"world share {b['share'][0]:.1f} / {b['share'][1]:.1f} / {b['share'][2]:.1f}%\n")


if __name__ == "__main__":
    main()
