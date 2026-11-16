#!/usr/bin/env python3
"""
scenarios.py — cost scenarios for cultivated meat: what has to go right, and what each assumption is worth.

Why
---
Earlier versions of this model quoted one number, "the floor", as if it were the lowest cost the physics allows.
It was neither a best case nor a typical case: it was `floor_physics.explore()` at its defaults (a standard
20 m3 stirred tank in perfusion, 120 g/L, a food-grade plant, engineered cells, no tank tricks). That number is
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
scenario_mc()  the uncertainty in the estimates behind a scenario (plant cost, financing, retention membranes, upkeep,
               medium price, loss rate), holding the scenario's switches.

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
from inputs import value, prior

FEED, SELECT, GE, NOTHING = "feed or process", "selection or adaptation", "genetic engineering", "nothing new"
TAG_ORDER = (NOTHING, FEED, SELECT, GE)            # the most demanding tag a scenario needs is the last one it uses
TAG_PLAIN = {GE: "needs genetic engineering", SELECT: "needs selection or adaptation of cells",
             FEED: "needs a change of feed, process or plant", NOTHING: "needs nothing new"}


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

SWITCHES = (
    Switch("cells", "Kind of cells",
           "How much waste the cells make, and how big each cell is. Ammonia and lactate are the waste, and they slow growth", (
        Setting("engineered", "Engineered to make almost no waste",
                {"nh3_kg": value("sc_nh3_engineered"), "lac_yield": value("sc_lac_engineered"), "mass_pg": fp.GOOD_CELLS.mass_pg},
                GE, "Ammonia is 0.055 mol per kilo of cells, lactate is 0.5 per glucose, and a cell weighs 3 ng. This is Humbird's "
                    "efficient cell. Only genetically engineered pharma cells have shown it."),
        Setting("selected", "Selected on a low-waste feed",
                {"nh3_kg": value("sc_nh3_selected"), "lac_yield": value("sc_lac_selected"), "mass_pg": value("sc_mass_selected_pg")},
                SELECT, "Glutamine is replaced in the feed, so ammonia is 0.14 (measured once, in bovine cells). Lactate is 0.42 per "
                        "glucose, as in adapted CHO cells. A cell weighs 2 ng. These differ from the best meat cells measured only "
                        "in lactate. While ammonia sets the litres of medium, as it does in every scenario here, the two cost the "
                        "same. Less lactate pays once the ammonia is removed or the cells tolerate more of it."),
        Setting("measured", "The best meat cells measured",
                {"nh3_kg": value("sc_nh3_selected"), "lac_yield": value("sc_lac_measured"), "glc_kg": value("sc_glc_measured"),
                 "mass_pg": value("sc_mass_selected_pg")},
                FEED, "Ammonia is 0.14 with glutamine replaced (Hubalek 2023). Lactate is 1.05 per glucose in meat cells. A cell weighs 2 ng. "
                      "The ammonia is the same as for the selected cells, and ammonia sets the litres of medium, so the extra lactate "
                      "costs nothing in these scenarios."),
        Setting("ordinary", "Ordinary meat cells",
                {"nh3_kg": value("sc_nh3_ordinary"), "lac_yield": value("sc_lac_measured"), "glc_kg": value("sc_glc_measured"),
                 "mass_pg": value("sc_mass_selected_pg")},
                NOTHING, "Ammonia is 0.70 in bovine cells with glutamine. Lactate is 1.05 per glucose. A cell weighs 2 ng."))),
    Switch("growth", "Growth speed", "How long the cells take to double", (
        Setting("24", "Cells double every 24 hours", {"doubling_h": value("pf_doubling_h")}, SELECT,
                "Humbird's model cell doubles this fast. No meat-cell culture with low waste has."),
        Setting("30", "Every 30 hours", {"doubling_h": value("sc_td_fast")}, SELECT,
                "Between the model cell and the central value."),
        Setting("36", "Every 36 hours", {"doubling_h": value("sc_td_central")}, SELECT,
                "Selection wins back part of the slowdown that the low-waste feed caused. Cells doubled in 43 hours on that feed and in 25.7 hours with glutamine."),
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
        Setting("none", "None bought", {"growth_factors": 0.0}, GE, "The cells need none or make their own. "
                                                                     "Genetic engineering has done this in cattle cells."),
        Setting("30", "30% of Humbird's price per litre", {"growth_factors": value("sc_gf_part")}, FEED,
                "Cheaper factors, or lines that need fewer."),
        Setting("60", "60% of his price", {"growth_factors": value("sc_gf_most")}, NOTHING, "Most of his price."),
        Setting("all", "All bought at his price", {"growth_factors": 1.0}, NOTHING,
                "Humbird's large-scale price. It assumes an industry far larger than the current one."))),
    Switch("medium", "Price of the medium", "What a litre of the nutrient liquid costs", (
        Setting("0.05", "$0.05 a litre (an aspiration)", {"medium_price": value("sc_medium_aspire")}, FEED,
                "no one has reported it: the lowest company report is $0.07 and GFI's amino acids alone cost $0.02-0.17; "
                "the medium then costs what the cells must eat"),
        Setting("0.15", "$0.15 a litre", {"medium_price": 0.15}, FEED,
                "The cost of the nutrients the cells eat. The medium cannot cost less."),
        Setting("0.20", "$0.20 a litre", {"medium_price": value("sc_medium_mid")}, FEED,
                "What several companies announced for 2025."),
        Setting("0.30", "$0.30 a litre", {"medium_price": value("sc_medium_high")}, NOTHING, "Between the announced and the reported price."),
        Setting("0.50", "$0.50 a litre", {"medium_price": value("media_price")}, NOTHING, "What SuperMeat reports."))),
)

_SHORT = {
    ("cells", "engineered"): "engineered", ("cells", "selected"): "selected on low-waste feed", ("cells", "measured"): "best measured",
    ("cells", "ordinary"): "ordinary", ("growth", "24"): "24 h", ("growth", "30"): "30 h", ("growth", "36"): "36 h", ("growth", "43"): "43 h",
    ("plant", "lean"): "food-grade, shared medium", ("plant", "sterile"): "food-grade plant", ("plant", "pharma"): "pharma-style plant",
    ("gas", "6"): "6 mm/s", ("gas", "4"): "4 mm/s", ("gas", "2"): "2 mm/s",
    ("tricks", "none"): "no tricks", ("tricks", "column"): "column", ("tricks", "pressure"): "column + pressure",
    ("tricks", "oxygen"): "column + pressure + oxygen",
    ("shape", "flat"): "0.5 deep/wide", ("shape", "squat"): "0.75", ("shape", "square"): "1.0", ("shape", "tall"): "1.6",
    ("losses", "0.2"): "0.2% a day", ("losses", "0.6"): "0.6% a day", ("losses", "1"): "1% a day", ("losses", "2"): "2% a day",
    ("restart", "4"): "4 days (neighbour)", ("restart", "14"): "14 days", ("restart", "21"): "21 days", ("restart", "30"): "30 days",
    ("gf", "none"): "none", ("gf", "30"): "30%", ("gf", "60"): "60%", ("gf", "all"): "all",
    ("medium", "0.05"): "$0.05/L", ("medium", "0.15"): "$0.15/L", ("medium", "0.20"): "$0.20/L", ("medium", "0.30"): "$0.30/L", ("medium", "0.50"): "$0.50/L",
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
    """The floor_physics.explore() arguments for a choice {switch: setting key}."""
    kw = {}
    for s in SWITCHES:
        kw.update(setting(s.key, choice[s.key]).kw)
    kw.update(always())
    return kw


def always() -> dict:
    """explore() arguments every scenario carries whatever its switches: the dissolved-oxygen setpoint (sc_do_setpoint,
    about half of air saturation, as pharma holds it; Humbird's tank implies 130%). Read at call time, so a test can set
    sc_do_scenarios to 0 to reproduce earlier figures."""
    return {"do_mmol": value("sc_do_setpoint")} if value("sc_do_scenarios") >= 0.5 else {}


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


def design(choice: dict) -> dict:
    """Fill the two tank-design switches (tricks, shape) with the cheapest pair among the settings offered
    that a loop could actually run: a pH-safe loop at a pass rate dense cultures have taken. Everything else
    is as in `choice`."""
    best = None
    for tk in SW["tricks"].settings:
        for sh in SW["shape"].settings:
            c = {**choice, "tricks": tk.key, "shape": sh.key}
            r = run(c)
            d = r["column"]
            if d is not None and (d["ph_vs_safe"] > 1.0 + 1e-9 or not d["passes_tested"]):
                continue
            if best is None or r["total"] < best[0] - 1e-12:
                best = (r["total"], c)
    return best[1]


_BASE = {"cells": "selected", "growth": "36", "plant": "sterile", "gas": "4", "losses": "1", "restart": "14",
         "gf": "30", "medium": "0.20"}
SCENARIOS = {
    "best": Scenario(
        "best", "5. Plus engineered cells: the best case, everything works",
        "The cells are engineered to make almost no waste, and they double every day. The plant is a food-grade plant with shared medium. "
        "The tank clears CO₂ without more bubbles. The cells need no bought growth factors.",
        "Cells, growth speed, plant, gas and growth factors are at their cheapest setting. The medium costs $0.15 a litre, because the $0.05 "
        "aspiration is not assumed. Losses are at the low end of what makers report, because pharma's 0.2% a day is not assumed. The tank "
        "design is the cheapest one that passes the checks on the CO₂ loop.",
        design({"cells": "engineered", "growth": "24", "plant": "lean", "gas": "6", "losses": "0.6", "restart": "14",
                "gf": "none", "medium": "0.15"})),
    "central": Scenario(
        "central", "3. Plus cells selected for low waste (Central)",
        "A changed feed and selection of the best lines make the cells produce little waste. This needs no engineering. The cells double "
        "every 36 hours. The plant is food-grade. The tank clears CO₂ without more bubbles.",
        "The cells have been measured, or selection can reach them. Every other switch is at the setting nearest the middle "
        "of what is reported. The tank design is the cheapest one that passes the checks on the CO₂ loop.",
        design(dict(_BASE)),
        alt=(("at 30 hours", {"growth": "30"}), ("at 24 hours", {"growth": "24"}), ("in a food-grade plant with shared medium", {"plant": "lean"}))),
    "central_lean": Scenario(
        "central_lean", "4. Plus a food-grade plant with shared medium",
        "This is the central case in a food-grade plant with a shared medium line, two seed trains and bought oxygen. Nobody "
        "has built one.",
        "The same as Central, but with a food-grade plant with shared medium.",
        design({**_BASE, "plant": "lean"}),
        alt=(("at 30 hours", {"growth": "30"}), ("at 24 hours", {"growth": "24"}))),
    "cautious": Scenario(
        "cautious", "Cautious: the best meat cells measured so far",
        "The cells are meat cells as they have been measured. They double every 43 hours, and glutamine is replaced in the feed. "
        "The plant is food-grade. The tank gets no more gas than anyone has run. Each lost run is followed by a slow restart.",
        "Each switch is at a setting that has been measured or reported. For growth factors and medium price, nobody has measured "
        "it, so the setting is a cautious judgement. The tank design is the cheapest one that passes the checks on the CO₂ loop.",
        design({"cells": "measured", "growth": "43", "plant": "sterile", "gas": "2", "losses": "1", "restart": "21",
                "gf": "60", "medium": "0.30"})),
    # --- the ladder (2026-11-16): each rung adds one kind of change, easiest first ----------------------------
    "today": Scenario(
        "today", "1. Today: the best meat cells measured, in an ordinary 20 m³ perfusion tank",
        "The cells are meat cells as they have been measured: glutamine replaced in the feed, doubling every 43 hours. The plant is "
        "food-grade. The tank is the ordinary tall stirred tank with no tricks, run with no more gas than anyone has run. Medium and "
        "growth factors cost what they cost today. Perfusion itself has not been run at this size.",
        "Each switch at what has been measured or reported, and nothing new in the tank. Only the medium price and the growth "
        "factors are judgements, because nobody has measured them at scale.",
        {"cells": "measured", "growth": "43", "plant": "sterile", "gas": "2", "tricks": "none", "shape": "tall", "losses": "1",
         "restart": "21", "gf": "60", "medium": "0.30"}),
    "process": Scenario(
        "process", "2. Plus process changes and cheaper inputs",
        "The same cells. The tank clears CO₂ without more bubbles (a column beside it) and takes more gas with a protectant, runs "
        "restart faster, and medium and growth factors fall to the prices companies announce. None of this changes the cells.",
        "Rung 1 with every switch that needs only a change of feed, process or supply moved to the middle of what is reported; "
        "tank design the cheapest the loop checks allow.",
        design({"cells": "measured", "growth": "43", "plant": "sterile", "gas": "4", "losses": "1", "restart": "14",
                "gf": "30", "medium": "0.20"})),
    "forecast": Scenario(
        "forecast", "Forecast for 2035: a first draft of the author's medians",
        "Each switch at the setting the author thinks as likely as not to be reached at production scale by 2035: selected cells "
        "doubling every 36 hours, a food-grade plant with shared medium, 4 mm/s of gas with the column and pressure, 0.6% of runs "
        "lost a day, medium at $0.15 and growth factors at 30% of Humbird's price.",
        "The median of a forecast for each switch, from the odds in the research notes (RESULTS.md, \"The forecast\"). A judgement, "
        "not a measurement; the draws behind its band do not include the forecast's own uncertainty about the switches.",
        design({"cells": "selected", "growth": "36", "plant": "lean", "gas": "4", "losses": "0.6", "restart": "14",
                "gf": "30", "medium": "0.15"})),
}
# The four scenarios the side studies (tank size, thick culture, frontier, audit, ...) were run on; their tests iterate these.
ORDER = ("best", "central", "central_lean", "cautious")
# The ladder the page and RESULTS lead with: each rung adds one kind of change to the one before, easiest first. Rungs 3-5 are
# exactly Central, Central with shared medium and the best case. The forecast is a separate row.
LADDER = ("today", "process", "central", "central_lean", "best")
PAGE_ORDER = LADDER + ("forecast",)


def scenario_choice(key: str, **change) -> dict:
    return {**SCENARIOS[key].choice, **change}


def alt_cost(key: str, change: dict) -> float:
    """Cost of a scenario with one assumption changed and the tank design chosen again for the new case."""
    return run(design({**SCENARIOS[key].choice, **change}))["total"]


REFERENCE_NAME = "Humbird's optimistic design: engineered cells in an ordinary perfusion tank"


def reference() -> dict:
    """Humbird's optimistic design (the old 'floor'): floor_physics.explore() at its defaults. A standard 20 m3 stirred tank in
    perfusion at 120 g/L, a food-grade plant, engineered cells, no tank tricks, no losses, no growth factors. It assumes the
    hardest change (engineered cells) and none of the easy ones (tank tricks), so it is not a rung of the LADDER. Kept so the
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


def shares(cost: float, regions=("global", "us", "eu")) -> dict:
    """Long-run share of meat sold by weight, %, by region, if cells cost `cost` $/kg (everything else at the
    model's central demand settings)."""
    import meat_market as mm
    dp = _demand()
    return {r: mm.penetration(mm.MARKETS[r], cost, income=mm.REGION_INCOME[r], pr=dp)[1] * 100.0 for r in regions}


def summary(choice: dict | None = None, r: dict | None = None, cost: float | None = None) -> dict:
    """Everything the scenario table shows for one choice (or, with `r`/`cost`, for an explore result)."""
    from inputs import value as v
    if r is None:
        r = run(choice)
    cost = r["total"] if cost is None else cost
    markup, pconv = v("markup_add"), v("p_conv")
    sh = shares(cost)
    return {"cost": cost, "retail": cost + markup, "ratio": (cost + markup) / pconv, "world": sh["global"], "us": sh["us"],
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


def scenario_mc(choice: dict | None, n: int = 1000, seed: int = 0) -> dict:
    """Cost ($/kg) with the estimates behind a scenario uncertain: plant cost, financing, life of the retention membranes, upkeep
    share of respiration, medium price and loss rate, drawn from their priors; the scenario's switches held. `choice=None` is
    Humbird's optimistic design (`reference()`, explore() at its defaults), drawn the same way."""
    rng = np.random.default_rng(seed)
    kw0 = explore_kwargs(choice) if choice is not None else {}
    pri = dict(MC_PRIORS)
    if choice is not None and choice["plant"] == "lean":                       # not below a plant with everything animal cells must have
        lean = plant_items.capital("lean")["total"]
        pri["capex_x"] = (min(1.0, plant_items.capital("yeastplus")["total"] / lean), 1.0, 1.5)
    tri = lambda lo, mode, hi: rng.triangular(lo, mode, hi, n)
    d = {"capex_x": tri(*pri["capex_x"]), "medium_price": tri(*pri["medium_price"]) * kw0.get("medium_price", 0.15),
         "hazard": tri(*pri["hazard"]) * kw0.get("hazard", 0.0)}
    for key, name in (("charge", "plant_charge_mature"), ("membrane_life", "rt_membrane_life"),
                      ("maintenance_share", "pf_maintenance_share")):
        _kind, lo, hi, mode, _note = prior(name)
        d[key] = tri(lo, mode, hi)
    cost = np.array([fp.explore(**{**kw0, **{k: float(v[i]) for k, v in d.items()}})["total"] for i in range(n)])
    return {"total": cost, **d}


def scenario_share_mc(choice: dict | None, region: str = "global", n: int = 1000, seed: int = 0) -> dict:
    """Cost and demand uncertain together: each draw takes a cost from scenario_mc and the demand dials from their priors."""
    import meat_market as mm
    cost = scenario_mc(choice, n, seed)["total"]
    mc = mm.monte_carlo(region, n, seed=seed + 1, biomass=cost)
    return dict(vol=mc["vol"], val=mc["val"], cost=cost)


# draws behind every headline band: the share's median moves by about 0.3 points between seeds at 1,000 draws, much less at 4,000
BAND_N = 4000
_BANDS: dict = {}


def bands(choice: dict | None, n: int = BAND_N) -> dict:
    """10th / 50th / 90th percentile of cost and of the world's long-run share by weight (cost and demand both
    uncertain). The 50th percentile of the share is the page's headline share for a scenario; the share at the
    scenario's own point cost (`summary(...)['world']`) is a different number and is labelled a point estimate."""
    key = (tuple(sorted(choice.items())) if choice is not None else "reference", n)
    if key not in _BANDS:
        mc = scenario_share_mc(choice, "global", n)
        q = lambda a: tuple(float(x) for x in np.percentile(a, [10, 50, 90]))
        _BANDS[key] = {"cost": q(mc["cost"]), "share": q(mc["vol"])}
    return _BANDS[key]


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
    presets = {k: {"name": SCENARIOS[k].name, "story": story_text(k), "choice": SCENARIOS[k].choice}
               for k in SCENARIOS}
    band = {k: bands(SCENARIOS[k].choice) for k in SCENARIOS}
    return {"switches": sw, "keys": list(KEYS), "presets": presets, "order": list(PAGE_ORDER), "start": "central",
            "always": _js_params(always()),
            "tags": list(TAG_ORDER), "tag_plain": TAG_PLAIN, "limit_plain": LIMIT_PLAIN, "medium_plain": MEDIUM_PLAIN,
            "best_cost": run(SCENARIOS["best"].choice)["total"], "mc_priors": MC_PRIORS, "bands": band}


def reported_band(n: int = 30000) -> tuple:
    """10th / 50th / 90th percentile of the world's long-run share for the process a company reports, with its cost and demand
    uncertain (meat_market.monte_carlo at the default cost model; RESULTS.md section 4 uses the same draw)."""
    import meat_market as mm
    if "reported" not in _BANDS:
        v = mm.monte_carlo("global", n)["vol"]
        _BANDS["reported"] = tuple(float(x) for x in np.percentile(v, [10, 50, 90]))
    return _BANDS["reported"]


def table_rows() -> list:
    """Every row of the headline table: the ladder, the forecast, Humbird's optimistic design, the reported process.
    Each row: name, cost point, cost band (or None), ratio, share at the point cost, share band (P10, P50, P90), hardest need."""
    rows = []
    for key in PAGE_ORDER:
        sc = SCENARIOS[key]
        sm, b = summary(sc.choice), bands(sc.choice)
        rows.append((sc.name, sm["cost"], b["cost"], sm["ratio"], sm["world"], b["share"], TAG_PLAIN[hardest_need(sc.choice)]))
    rs, b = summary(r=reference()), bands(None)
    rows.append((REFERENCE_NAME, rs["cost"], b["cost"], rs["ratio"], rs["world"], b["share"], TAG_PLAIN[GE]))
    rc = reported_cost()
    rows.append(("As a company reports (SuperMeat 2024)", rc, None, (rc + value("markup_add")) / value("p_conv"),
                 shares(rc)["global"], reported_band(), "a company's own report"))
    return rows


def markdown_table() -> str:
    """The headline table as Markdown (RESULTS.md, METHODS.md and research_notes/cost_scenarios.md quote it). Every row gives both the
    share at its own point cost and the median of draws in which cost and demand are uncertain, so rows can be compared."""
    out = ["| scenario | cells, $/kg (10th\u201390th percentile) | R vs $12 meat | share of world meat, long run: at the point cost | "
           "median of draws (10th\u201390th) | hardest thing it needs |", "|---|---|---|---|---|---|"]
    for name, cost, cb, ratio, world, sb, need in table_rows():
        band = f" (${cb[0]:.0f}\u2013{cb[2]:.0f})" if cb is not None else ""
        out.append(f"| {name} | **${cost:.1f}**{band} | {ratio:.2f} | {world:.1f}% | **{sb[1]:.1f}%** ({sb[0]:.1f}\u2013{sb[2]:.1f}%) | {need} |")
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
        s = summary(sc.choice)
        b = bands(sc.choice)
        print(f"{sc.name}\n  {story_text(key)}\n  rule: {sc.rule}")
        print(f"  ${s['cost']:.2f}/kg cells, ${s['retail']:.1f} in the shop, {s['ratio']:.2f}x everyday meat; world {b['share'][1]:.1f}% median ({b['share'][0]:.1f}\u2013{b['share'][2]:.1f}%), point estimate {s['world']:.1f}% "
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
        b = bands(sc.choice)
        print(f"  band (P10-P50-P90): cost ${b['cost'][0]:.1f} / {b['cost'][1]:.1f} / {b['cost'][2]:.1f}; "
              f"world share {b['share'][0]:.1f} / {b['share'][1]:.1f} / {b['share'][2]:.1f}%\n")


if __name__ == "__main__":
    main()
