#!/usr/bin/env python3
"""
design_space.py — explore the tank's design options efficiently: price each limit first, then search the designs.

The aim (Pablo, 2026-11-16) is a tank in which CO2, oxygen and mixing no longer bind, so that only the thickness of the
culture does. Two passes, cheapest first:

1. `limit_prices(key)`: for a scenario, the cost if each limit were lifted at no cost (CO2, oxygen, mixing, all three; then the
   thickness limit raised), and if each large cost line were removed (the litres of medium, the filter membranes, the
   protectant, growth factors, lost runs, the plant). This is the most any design that attacks that limit could be worth,
   so it says which limits deserve design work before any design is drawn.
2. `designs(key)`: every combination of the tank options the model already has (OPTIONS: the column, headspace pressure,
   tank shape, fat in the feed, a bubble cage), run through `floor_physics.explore`, kept only
   if a column loop passes its pH and pass-rate checks. Each design is scored by cost and by how many of its elements nobody
   has run with animal cells. `frontier(key)` is the cheapest design for each number of unproven elements.

`ideal(key)` is the scenario in the ordinary tall tank with every gas and mixing limit lifted for free: a lower bound on what
any of these designs can reach on the scenario's own feed. The gap between a design and the ideal is what is left to gain from
the tank's gas exchange. Since 2026-11-19 (glucose from the cells' balance) fat taken from the feed also cuts the glucose and
the lactate, so where lactate sets the medium (the published cells, rungs 1 and 2) a fat-fed design costs less than the ideal.

Nothing here changes a default. The scenarios' own tank designs (scenarios.design) are a subset of this search. Every design
carries what every scenario carries (scenarios.always): dissolved oxygen held at about half of air saturation. The first version of
this search had that setpoint as an option and found it free and unused, so the scenarios adopted it (2026-11-16).

    python design_space.py              # the tables, as text
    python design_space.py --markdown   # the tables RESULTS.md and the note quote
"""
from __future__ import annotations

import itertools
import sys

import floor_physics as fp
import min_litres
import plant_items
import scenarios as S
import vessels as V
from inputs import value

# ----------------------------------------------------------------------------
# The options. Each: (key, plain name, explore() arguments, unproven elements it adds, why).
# "Unproven" counts elements nobody has run with animal cells at any scale that matters; standard practice counts 0.
# ----------------------------------------------------------------------------
OPTIONS = {
    "column": (
        ("none", "no column", {}, 0, ""),
        ("co2", "a column that strips CO₂", dict(S._COL), 1, "no animal cells have gone through a packed column"),
        ("o2", "a column that strips CO₂ and feeds recycled oxygen", dict(S._O2), 2,
         "the column, and oxygen recycled through a lime scrubber"),
    ),
    "pressure": (
        ("base", "Humbird's 0.33 bar", {}, 0, ""),
        ("1", "1 bar of extra pressure", {"p_top_barg": value("sc_p_top")}, 1, "no culture has been run at 1 bar gauge"),
        ("2", "2 bar of extra pressure", {"p_top_barg": 2.0}, 2,
         "the top of the input's range; steel vessels are rated to 3-4 bar; cells at 3 bar absolute were not examined"),
    ),
    "shape": (
        ("tall", "the ordinary tall tank", {}, 0, ""),
        ("square", "liquid as deep as wide", {"aspect": value("sc_aspect_mid")}, 0, "tanks in use run from about 1 to 3"),
        ("squat", "liquid 0.75 times as deep as wide", {"aspect": value("sc_aspect_squat")}, 1, "squatter than tanks in use"),
        ("flat", "liquid half as deep as wide", {"aspect": value("sc_aspect_flat")}, 1, "squatter than tanks in use"),
    ),
    "fat": (
        ("made", "the cells make their fat from glucose", {}, 0, ""),
        ("fed", "fat taken from the feed", {"fat_fed": 1.0}, 1, "how much fed fat displaces is not measured; needs a carrier"),
    ),
    "vessel": (
        ("stirred", "a stirred tank", None, 0, ""),
        ("caged", "a stirred tank with a bubble cage", None, 1, "caged aeration exists only with microcarriers in small tanks"),
    ),
}
KEYS = tuple(OPTIONS)
_FREE_GAS = {"otr_mult": 1e3, "co2_mult": 1e3, "mixing": False}      # every gas and mixing limit lifted, at no cost
_CACHE: dict = {}


def _option(dim: str, key: str) -> tuple:
    return next(o for o in OPTIONS[dim] if o[0] == key)


def base_kwargs(key: str) -> dict:
    """The scenario's explore() arguments without its tank design: the ordinary tall tank, no tricks."""
    return S.explore_kwargs({**S.SCENARIOS[key].choice, "tricks": "none", "shape": "tall"})


def design_kwargs(key: str, design: dict) -> dict:
    """explore() arguments for a scenario with a design {dimension: option key}."""
    kw = base_kwargs(key)
    for dim in KEYS:
        if dim != "vessel":
            kw.update(_option(dim, design[dim])[2])
    return V.explore_kwargs(design["vessel"], "perfusion", kw)


def run(key: str, design: dict) -> dict:
    """One design: explore()'s result plus `ok` (a column loop passes its checks) and `unproven` (elements never run)."""
    k = (key, tuple(design[d] for d in KEYS))
    if k not in _CACHE:
        r = fp.explore(**design_kwargs(key, design))
        _CACHE[k] = {"design": dict(design), "cost": r["total"], "density": r["density"], "limit": r["limit"],
                     "ok": V._loop_ok(r), "unproven": sum(_option(d, design[d])[3] for d in KEYS),
                     "medium_l": r["medium_l"]}
    return _CACHE[k]


def designs(key: str) -> list:
    """Every combination of the options for a scenario, cheapest first."""
    out = [run(key, dict(zip(KEYS, combo))) for combo in itertools.product(*[[o[0] for o in OPTIONS[d]] for d in KEYS])]
    return sorted(out, key=lambda d: d["cost"])


def frontier(key: str, cage: bool = True) -> list:
    """The cheapest design that passes the loop checks for each number of unproven elements (only where it beats fewer).
    `cage=False` leaves out the bubble cage, whose three numbers are judgements (inputs vm_cage_*)."""
    best, out = float("inf"), []
    ok = [d for d in designs(key) if d["ok"] and (cage or d["design"]["vessel"] != "caged")]
    for n in range(0, max(d["unproven"] for d in ok) + 1):
        tier = [d for d in ok if d["unproven"] == n]
        if tier and tier[0]["cost"] < best - 1e-9:
            best = tier[0]["cost"]
            out.append(tier[0])
    return out


def ideal(key: str) -> dict:
    """The scenario in the ordinary tall tank with every gas and mixing limit lifted for free: the thickness of the culture
    binds. No design of OPTIONS that keeps the scenario's feed can cost less; one that takes fat from the feed can, where lactate
    sets the litres of medium (tests/test_design_space.py checks both)."""
    kw = V.explore_kwargs("stirred", "perfusion", base_kwargs(key))
    kw["vm"] = {**kw["vm"], **_FREE_GAS}
    r = fp.explore(**kw)
    return {"cost": r["total"], "density": r["density"], "limit": r["limit"], "medium_l": r["medium_l"]}


def plain(key: str) -> dict:
    return run(key, {d: OPTIONS[d][0][0] for d in KEYS})


def describe(design: dict) -> str:
    """A design in words: only the options that differ from the ordinary tank."""
    parts = [_option(d, design[d])[1] for d in KEYS if design[d] != OPTIONS[d][0][0]]
    return S.plain_list(parts) if parts else "the ordinary tall tank, no tricks"


# ----------------------------------------------------------------------------
# What each limit is worth
# ----------------------------------------------------------------------------
def limit_prices(key: str) -> list:
    """Rows (what is lifted, cost, change from the scenario, density, what then binds), for the scenario's own design.
    Each row lifts or removes one thing for free; 'every gas limit' lifts CO2, oxygen and mixing together."""
    choice = S.SCENARIOS[key].choice
    kw0 = S.explore_kwargs(choice)
    base = fp.explore(**kw0)

    def with_vm(extra: dict, **more) -> dict:
        kw = V.explore_kwargs("stirred", "perfusion", {**kw0, **more})
        kw["vm"] = {**kw["vm"], **extra}
        return fp.explore(**kw)

    rows = [("the scenario as it is", base)]
    rows.append(("CO₂ removal lifted", with_vm({"co2_mult": 1e3})))
    rows.append(("oxygen supply lifted", with_vm({"otr_mult": 1e3})))
    rows.append(("mixing lifted", with_vm({"mixing": False})))
    rows.append(("every gas limit lifted (CO₂, oxygen, mixing)", with_vm(_FREE_GAS)))
    with fp._inputs_set({"pf_x_visc": 320.0}):
        rows.append(("every gas limit lifted, and the culture as thick as 320 g/L", with_vm(_FREE_GAS)))
    least = min_litres.bounds(kw0.get("doubling_h", 24.0), kw0.get("mass_pg", 3000.0))["physical"]
    r_least = fp.explore(**{**kw0, "medium_l": least})   # explore raises it to the culture that leaves with the cells, if thin
    held = "" if r_least["medium_l"] <= least + 1e-9 else f"; this thin culture needs {r_least['medium_l']:.1f}, what leaves with the cells"
    rows.append((f"medium at the least the physics allows ({least:.1f} L/kg{held})", r_least))
    rows.append(("filter membranes that never wear out", fp.explore(**{**kw0, "membrane_life": 1e9})))
    rows.append(("no bubble protectant to buy", fp.explore(**{**kw0, "protectant_price": 0.0})))
    rows.append(("no growth factors to buy", fp.explore(**{**kw0, "growth_factors": 0.0})))
    rows.append(("no runs lost", fp.explore(**{**kw0, "hazard": 0.0})))
    cheap = {k: v for k, v in kw0.items() if k not in ("plant", "items")}
    rows.append(("a yeast plant with what animal cells need", fp.explore(**{**cheap, "items": plant_items.PLANTS["yeastplus"]})))
    b = base["total"]
    return [(lab, r["total"], r["total"] - b, r["density"], r["limit"]) for lab, r in rows]


def summary(key: str) -> dict:
    fr, nc = frontier(key), frontier(key, cage=False)
    return {"plain": plain(key), "scenario": S.run(S.SCENARIOS[key].choice)["total"], "frontier": fr, "best": fr[-1],
            "frontier_no_cage": nc, "best_no_cage": nc[-1],
            "ideal": ideal(key), "n": len(designs(key)), "n_ok": sum(d["ok"] for d in designs(key))}


# ----------------------------------------------------------------------------
LIM = {"CO2 removal": "CO₂", "oxygen supply": "oxygen", "mixing": "mixing", "thickness of the culture": "thickness"}
# The cases searched: the scenarios run in perfusion. A batch (fed-batch) is held by its waste, not by gas exchange, so the tank's
# gas design does not move it (2026-11-19 restructure: rungs 1-3 and the forecast's preset are fed-batch; the published cells in
# perfusion are the cautious scenario, whose switches are the old rung 1's, so its search gives the old rung 1's figures).
CASES = ("cautious", "central", "central_lean", "engineered", "best")
SHORT = {"cautious": "Published cells, in perfusion", "today": "1. Published cells", "process": "2. Plus process changes", "selected": "3. Selected cells", "central": "4. Selected cells",
         "central_lean": "5. Shared-medium plant", "engineered": "6. Engineered cells", "best": "7. Engineered cells, all favourable",
         "forecast": "Forecast for 2035 (medians)"}


def markdown() -> str:
    cell = lambda d: f"${d['cost']:.2f} ({d['density']:.0f} g/L, {LIM[d['limit']]}; {d['unproven']} unproven)"
    out = ["| case | ordinary tank | the scenario's design | cheapest design, no cage | cheapest design, with a bubble cage | "
           "perfect gas exchange |", "|---|---|---|---|---|---|"]
    for k in CASES:
        s = summary(k)
        p, i = s["plain"], s["ideal"]
        out.append(f"| {SHORT[k]} | ${p['cost']:.2f} ({p['density']:.0f} g/L, {LIM[p['limit']]}) | ${s['scenario']:.2f} | "
                   f"{cell(s['best_no_cage'])} | {cell(s['best'])} | **${i['cost']:.2f}** ({i['density']:.0f} g/L) |")
    for k in ("cautious", "central"):
        for cage, lab in ((False, "no cage"), (True, "with a bubble cage")):
            out += ["", f"| {SHORT[k]}, {lab}: unproven elements | cheapest design that passes the checks | cost | density, limit |",
                    "|---|---|---|---|"]
            for d in frontier(k, cage):
                out.append(f"| {d['unproven']} | {describe(d['design'])} | ${d['cost']:.2f} | {d['density']:.0f} g/L, {LIM[d['limit']]} |")
    for k in ("cautious", "central", "best"):
        out += ["", f"| {SHORT[k]}: if this were free | cost | change | density, what then binds |", "|---|---|---|---|"]
        for lab, cost, d, x, lim in limit_prices(k):
            ch = "" if abs(d) < 0.005 else f"−${-d:.2f}" if d < 0 else f"+${d:.2f}"
            out.append(f"| {lab} | ${cost:.2f} | {ch} | {x:.0f} g/L, {LIM.get(lim, lim)} |")
    return "\n".join(out)


def main() -> None:
    if "--markdown" in sys.argv:
        print(markdown())
        return
    for k in CASES:
        s = summary(k)
        print(f"\n{SHORT[k]}: {s['n']} designs, {s['n_ok']} pass the loop checks. Ordinary tank ${s['plain']['cost']:.2f}, the scenario's "
              f"design ${s['scenario']:.2f}, perfect gas exchange ${s['ideal']['cost']:.2f}")
        for lab, fr in (("no cage", s["frontier_no_cage"]), ("with a cage", s["frontier"])):
            for d in fr:
                print(f"   {lab:<11} {d['unproven']} unproven: ${d['cost']:6.2f}  {d['density']:.0f} g/L ({d['limit']})  {describe(d['design'])}")
        for lab, cost, d, x, lim in limit_prices(k):
            print(f"      {lab:<62} ${cost:6.2f} ({d:+.2f})  {x:.0f} g/L, {lim}")


if __name__ == "__main__":
    main()
