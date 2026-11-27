#!/usr/bin/env python3
"""test_plant_items.py — checks for the plant built item by item (plant_items.py) and the contamination
model (contamination.py).

  * both of Humbird's totals are reproduced from the same item list: his animal-cell plant ($327.9M,
    $683k per m3) exactly, and his yeast plant with 20 m3 tanks ($70M, $130k per m3) with one solved
    exponent that must come out ordinary;
  * his sub-totals, seed train and standard yeast plant are reproduced, so the rules are applied as he
    applies them;
  * the options behave: the named plants are ordered, explore() takes items, and the floor's plant by
    items is the floor;
  * the contamination model behaves and its thresholds solve what they claim to;
  * pinned numbers: the figures quoted in research_notes/cheap_plant_study.md and METHODS.md.

Run directly (no pytest needed):
    python tests/test_plant_items.py
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)


def check() -> list:
    """Three parts.

    HISTORY (`_check`, run with floor_physics.BEFORE_FILTER_LOOP). The body of research_notes/cheap_plant_study.md is a dated
    snapshot: its figures were computed at the settings the note was written with on 2026-11-14 (the old hoped-for retention
    device, rt_tff_default = 0; no bubble protectant; no antifoam effect; no oxygen bought by the yeast-style plant), on the
    engine as it stood when the note was last recomputed (2026-11-20: bubble deaths, harvest loss, perfusion crew, utilities and
    medium preparation capital apply in it). These pins check that the snapshot still reproduces on those settings; they are not
    the model's figures.

    CURRENT (`_check_current`, the model's own settings): the note's box of current figures, recomputed 2026-11-21.

    METHODS (`_check_methods`): what METHODS.md quotes, also at the model's own settings."""
    import retention
    import floor_physics
    with retention._with(floor_physics.BEFORE_FILTER_LOOP):
        fails = _check()
    return fails + _check_current() + _check_methods()


def _check_current() -> list:
    """The box of current figures at the top of cheap_plant_study.md, at the model's own settings (2026-11-21, after the second
    batch of engine fixes: the building's power by floor and class, part of the crew per tank, the floor's glucose)."""
    import floor_physics as fp
    import plant_items as pi
    import contamination as ct
    fails = []
    got = {"sterile plant": pi.cost_per_kg("floor")["total"], "sterile plant at 0.2% a day": ct.cost("floor", 0.002),
           "yeast-style class": fp.explore(plant="microbial")["total"], "yeast plant with additions": pi.cost_per_kg("yeastplus")["total"],
           "lean plant": pi.cost_per_kg("lean")["total"], "lean, 0.6% a day": ct.cost("lean", 0.006),
           "lean, 1.5% a day": ct.cost("lean", 0.015), "lean, 5% a day": ct.cost("lean", 0.05),
           "lean, 1.5% a day, 30-day restart": ct.cost("lean", 0.015, restart_fail_days=30.0),
           "lean, drained and refilled": pi.cost_per_kg("lean", mode="filldraw")["total"],
           "yeast plant with additions, drained and refilled": pi.cost_per_kg("yeastplus", mode="filldraw")["total"],
           "sterile plant, drained and refilled": pi.cost_per_kg("floor", mode="filldraw")["total"]}
    # 2026-11-27 (nutrient balance): every figure +$0.05 or +$0.06 (sterile plant 15.72 -> 15.78, lean 12.83 -> 12.88,
    # yeast plant with additions drained and refilled 9.05 -> 9.11); the break-even loss rates are unchanged
    want = {"sterile plant": 15.78, "sterile plant at 0.2% a day": 16.09, "yeast-style class": 10.77,
            "yeast plant with additions": 10.97, "lean plant": 12.88, "lean, 0.6% a day": 13.59, "lean, 1.5% a day": 14.71,
            "lean, 5% a day": 19.57, "lean, 1.5% a day, 30-day restart": 16.14, "lean, drained and refilled": 12.05,
            "yeast plant with additions, drained and refilled": 9.11, "sterile plant, drained and refilled": 16.56}
    for k, w in want.items():
        if abs(got[k] - w) > 0.006:
            fails.append(f"current figures, {k}: want ${w:.2f} got ${got[k]:.2f}")
    for p, w in (("lean", 2.56), ("yeastplus", 4.81), ("yeast", 5.97)):
        g = ct.breakeven_hazard(p) * 100.0
        if abs(g - w) > 0.006:
            fails.append(f"current break-even loss rate, {p}: want {w:.2f}% got {g:.2f}%")
    note = open(os.path.join(ROOT, "research_notes", "cheap_plant_study.md")).read()
    box = note.split("> **Current figures**")[1].split("> Third pass")[0]
    for q in [f"${w:.2f}" for w in want.values()] + ["2.56%", "4.81%", "5.97%"]:
        if q not in box:
            fails.append(f"cheap_plant_study.md's box of current figures does not quote {q!r}")
    return fails


def _check() -> list:
    from inputs import value
    import floor_physics as fp
    import plant_items as pi
    import contamination as ct

    fails = []

    def near(name, got, want, rel):
        if abs(got - want) > rel * abs(want):
            fails.append(f"{name}: want {want:.5g} (+-{rel:.1%}) got {got:.5g}")

    v = value
    # --- Humbird's animal-cell plant: Tables 4.1-4.3 ------------------------------------------------
    h = pi.humbird()
    vol = v("pi_n_tanks") * v("pi_tank_m3")
    near("Humbird TCI, $k", sum(h.values()) * vol, 327907.0, 2e-4)
    near("Humbird per m3", sum(h.values()), v("pf_capex_aseptic_fedbatch"), 5e-4)
    to_direct = vol / pi.indirect()
    near("ISBL direct cost", (h["vessels"] + h["seed"] + h["medium"] + h["harvest"]) * to_direct, 93949.0, 2e-4)
    near("OSBL direct cost", (h["oxygen"] + h["cleaning"]) * to_direct, 35779.0, 2e-4)
    near("buildings", (h["hall"] + h["labs"] + h["support"]) * to_direct, 48482.0, 1e-6)
    near("one 20 m3 bioreactor by Eq. 3.1", pi.eq31(20.0) * v("pi_n_tanks"), v("pi_prod_installed"), 1e-3)
    near("seed train by Eq. 3.1", pi.seed_installed_k(v("pi_seed_trains"), 2 * v("pi_seed_trains")),
         v("pi_seed_installed"), 5e-3)
    sizes = [20.0] * 24 + [v("pi_seed_f4_m3")] * 8 + [v(f"pi_seed_f{i}_m3") for i in range(4)] * 4
    near("bare cost of all bioreactors (note 127)", sum(pi.bare(s) for s in sizes), v("pi_bioreactor_bare"), 5e-3)
    near("Table 3.3 parts add to $1.5M", sum(v(k) for k in ("pi_t33_vessel", "pi_t33_piping", "pi_t33_instr",
         "pi_t33_other", "pi_t33_internals", "pi_t33_surface")), 1500.0, 0.02)
    near("Humbird's seed train keeps up with 57-hour cycles", pi.final_seeds_needed(2.0, 9.0 / 24.0), 8.0, 0.03)

    # --- Humbird's yeast plants: Tables A.1 and A.5 -------------------------------------------------
    near("standard yeast plant TCI, $k", pi.yeast_standard_total_k(), 68742.0, 2e-4)
    y = pi.yeast20()
    near("yeast plant with 20 m3 tanks, $k", sum(y.values()) * v("pi_yeast20_tanks") * v("pi_tank_m3"),
         v("pi_yeast20_capex"), 1e-6)
    near("yeast plant with 20 m3 tanks, per m3", sum(y.values()), 129.6, 1e-3)
    n = pi.yeast20_vessel_exp()
    if not 0.4 <= n <= 0.7:
        fails.append(f"the solved vessel exponent should be an ordinary one (0.4-0.7): {n:.3f}")
    near("the same plant with the six-tenths rule throughout", pi.yeast20_total_k(0.6), v("pi_yeast20_capex"), 0.25)
    near("the fivefold gap", sum(h.values()) / sum(y.values()), 5.27, 0.01)

    # --- options and named plants -------------------------------------------------------------------
    opts = pi.options()
    if set(opts) != set(pi.ITEMS):
        fails.append("options() must cover every item")
    for item in pi.ITEMS:
        first = next(iter(opts[item].values()))[0]
        near(f"first option of {item} is Humbird's", first, h[item], 1e-12)
    tot = {p: pi.capital(p)["total"] for p in pi.PLANTS}
    if not tot["humbird"] > tot["floor"] > tot["lean"] > tot["yeastplus"] > tot["yeast"]:
        fails.append(f"named plants out of order: {tot}")
    near("floor plant by items = the sanitary class", tot["floor"], v("pf_capex_no_cleanroom"), 1e-3)
    near("yeast plant by items", tot["yeast"], sum(y.values()), 1e-9)
    near("explore(items=floor) = the floor", fp.explore(items=pi.PLANTS["floor"])["total"], fp.explore()["total"], 1e-3)
    near("explore(items={}) = the pharma class", fp.explore(items={})["total"], fp.explore(plant="pharma")["total"], 1e-3)
    lean = fp.explore(items=pi.PLANTS["lean"])
    # 2026-11-20: every cost is per kilo harvested, so the oxygen bought per kilo grown is divided by the harvested share; and a
    # plant built from items scales its OWN medium preparation item with the medium passed, where a plant given as a total
    # (capex_2018=) scales Humbird's. So the two cases differ in capital by that item's scaling and in nothing else but the oxygen.
    whole = fp.explore(capex_2018=tot["lean"])
    near("bought oxygen is charged, per kilo harvested", lean["extra_opex"],
         pi.capital("lean")["extra_opex"] / lean["harvested_share"], 1e-9)
    # 2026-11-21: the building's power follows the plant's own halls (floor_physics.building_power): the lean plant's plain shed
    # draws a tenth of the power of the sanitary hall a plant given as a total is taken to have, so the utilities differ too
    near("bought oxygen is the only running cost the items add, beside the building's power",
         lean["total"] - lean["extra_opex"] - lean["capital"] - lean["utilities"],
         whole["total"] - whole["capital"] - whole["utilities"], 1e-9)
    if not lean["utilities"] < whole["utilities"]:
        fails.append("the lean plant's plain building should draw less power than a sanitary hall")
    # 2026-11-20, third pass: and by what each tank brings with it in perfusion against fed-batch (floor_physics.tank_items): a
    # plant given as a total has Humbird's dedicated makeup tanks and filter housings, fewer in perfusion (-$8.3k per m3 in 2018
    # dollars), where the lean plant shares its medium line and has none per tank, so nothing changes for it
    def _mode_shift(choices):
        a, b = fp.tank_items(20.0, True, choices), fp.tank_items(20.0, False, choices)
        return (a["total"] - b["total"]) * v("pf_capex_escalation")
    near("items and a total differ in capital by the medium preparation item's scaling and the tanks' items",
         whole["capex"] - lean["capex"], whole["medium_prep_capex"] - lean["medium_prep_capex"]
         + _mode_shift(None) - _mode_shift(dict(pi.PLANTS["lean"])), 1e-9)
    if not lean["medium_prep_capex"] < whole["medium_prep_capex"]:
        fails.append("the lean plant's shared medium lines should scale a smaller medium item than Humbird's")
    if pi.capital("lean", oxygen="owned")["extra_opex"] != 0.0:
        fails.append("no oxygen purchase when the plant owns its oxygen plant")
    try:
        pi.capital(hall="marble")
        fails.append("an unknown option should raise")
    except ValueError:
        pass
    for item, opt, verdict, _why in pi.STATUS:
        if opt not in opts[item] or verdict not in ("not needed", "probably not needed", "needed", "unknown"):
            fails.append(f"STATUS row {item}/{opt}/{verdict} does not match the options")
    if not pi.final_seeds_needed(10.0, 3.3) < 2.0 < pi.final_seeds_needed(5.0, 3.3):
        fails.append("two final seed tanks should cover runs of ten days and not of five")
    near("queue when 24 tanks restart on two seed tanks, days", pi.restart_queue_days(24.0, 2.0), 4.55, 0.01)

    # --- explore(): the new loss terms --------------------------------------------------------------
    base = fp.explore(hazard=0.015, restart_fail_days=14)
    near("no start failures and no salvage = the old treatment", base["total"],
         fp.explore(hazard=0.015, restart_fail_days=14, start_fail=0.0, salvage=0.0)["total"], 1e-12)
    if not fp.explore(hazard=0.015, restart_fail_days=14, start_fail=0.1)["total"] > base["total"]:
        fails.append("failed starts should raise the cost")
    if not fp.explore(hazard=0.015, restart_fail_days=14, salvage=1.0)["total"] < base["total"]:
        fails.append("salvaging the cells of a lost run should lower the cost")
    near("start failures alone: uptime", fp.explore(start_fail=0.2)["uptime"],
         0.8 * 33.0 / (0.8 * 33.0 + 33.0 * (1 / 0.91 - 1) + 0.2 * v("ct_start_detect_days")), 1e-9)

    # --- contamination: growth and detection --------------------------------------------------------
    t20, t60 = ct.time_to_detect_h(20.0), ct.time_to_detect_h(60.0)
    if not (12.0 < t20 < 24.0 and abs(t60 / t20 - 3.0) < 1e-9):
        fails.append(f"a 20-minute contaminant should show in 12-24 h and a 60-minute one in three times that: {t20:.1f}, {t60:.1f}")
    near("doublings to detection at 120 g/L", ct.doublings_to(ct.detect_threshold(120.0)), 51.0, 0.03)
    if not ct.detect_threshold(120.0) > ct.detect_threshold(27.0):
        fails.append("a denser culture should hide more contaminant")
    if not ct.contaminant_share_at_detection() < 0.005:
        fails.append("at detection the contaminant should be a small share of the biomass")
    if not ct.blind_hours(20.0, limit_cfu_g=1e2) > ct.blind_hours(20.0, limit_cfu_g=1e4) > 3.0:
        fails.append("the food limit should be crossed hours before detection")
    if not 0.0 < ct.escape_probability(20.0) < ct.escape_probability(60.0) <= 1.0:
        fails.append("slower contaminants should escape a seed stage more often")
    near("hazard from batch loss round-trips", ct.batch_loss(ct.hazard_from_batch_loss(0.112, 15.0), 15.0), 0.112, 1e-9)
    ref = ct.reference_hazards()
    if not (ref["pharma"][0] < v("pf_hazard_pharma") < ref["pharma"][1] + 1e-3):
        fails.append(f"pf_hazard_pharma should sit in the range the survey implies: {ref['pharma']}")
    lo, hi = ref["cultivated meat, all"][0], ref["cultivated meat, beyond flasks"][1]
    if not lo <= v("ct_hazard_frontier") <= hi:
        fails.append("ct_hazard_frontier should sit in the range the cultivated-meat survey implies")

    # --- contamination: thresholds ------------------------------------------------------------------
    be = {p: ct.breakeven_hazard(p) for p in ("lean", "yeastplus", "yeast")}
    if not v("pf_hazard_pharma") < be["lean"] < be["yeastplus"] < be["yeast"] < 1.0:
        fails.append(f"break-even loss rates out of order: {be}")
    for p, hz in be.items():
        near(f"break-even solves equal cost ({p})", ct.cost(p, hz), ct.cost("floor", v("pf_hazard_pharma")), 1e-6)
    if not ct.breakeven_hazard("lean", run_days=5.0) > be["lean"] > ct.breakeven_hazard("lean", run_days=60.0):
        fails.append("the tolerable chance per day should fall as runs get longer")
    if not ct.breakeven_hazard("lean", restart_fail_days=30.0) < be["lean"] < ct.breakeven_hazard("lean", salvage=1.0):
        fails.append("a longer restart should tighten the threshold and salvage loosen it")
    if not be["lean"] > hi:
        fails.append("the lean plant's threshold should lie above today's cultivated-meat loss rates")
    if not 0.0 < ct.breakeven_start_fail("lean") < ct.breakeven_start_fail("yeast") < 0.95:
        fails.append("break-even share of failed starts out of order")

    # --- pinned: the figures the note and METHODS.md quote -------------------------------------------
    cost = {p: pi.cost_per_kg(p)["total"] for p in pi.PLANTS}
    fd = {p: pi.cost_per_kg(p, mode="filldraw")["total"] for p in pi.PLANTS}
    lp = pi.capital("lean")["items"]
    quoted = [f"{sum(h.values()):.0f}", f"{tot['floor']:.0f}", f"{tot['lean']:.0f}", f"{tot['yeastplus']:.0f}",
              f"{tot['yeast']:.0f}"]
    quoted += [f"{h[i]:.0f} | {lp[i]:.0f} |" for i in pi.ITEMS]
    quoted += [f"${cost[p]:.1f}" for p in pi.PLANTS] + [f"${fd[p]:.1f}" for p in pi.PLANTS]
    quoted += [f"{be[p] * 100:.1f}%" for p in be] + [f"{n:.2f}", f"{t20:.0f} hours", f"{t60:.0f} hours"]
    quoted += [f"${ct.cost(p, v('ct_hazard_frontier')):.1f}" for p in ("lean", "yeastplus", "yeast")]
    note = open(os.path.join(ROOT, "research_notes", "cheap_plant_study.md")).read()
    for q in quoted:
        if q not in note:
            fails.append(f"research_notes/cheap_plant_study.md does not quote {q!r}")
    return fails


def _check_methods() -> list:
    """METHODS.md quotes the plant costs and break-even loss rates of the model as it now stands (not the note's snapshot)."""
    import plant_items as pi
    import contamination as ct
    methods = open(os.path.join(ROOT, "METHODS.md")).read()
    tot = {p: pi.capital(p)["total"] for p in ("lean", "yeastplus")}
    cost = {p: pi.cost_per_kg(p)["total"] for p in ("lean", "yeastplus")}
    be = {p: ct.breakeven_hazard(p) for p in ("lean", "yeastplus")}
    return [f"METHODS.md does not quote {q!r}" for q in
            ([f"${tot[p]:.0f}k" for p in tot] + [f"${cost[p]:.1f}" for p in cost] + [f"{be[p] * 100:.1f}%" for p in be])
            if q not in methods]


def main() -> None:
    fails = check()
    if fails:
        print("FAIL: plant items / contamination")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("PASS: plant items and contamination (both of Humbird's totals reproduced)")


if __name__ == "__main__":
    main()
