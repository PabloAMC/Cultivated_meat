#!/usr/bin/env python3
"""test_frontier.py — the path from Humbird's design to the all-favourable case (frontier.py).

Rewritten 2026-11-20: frontier.py no longer holds a second "every lever at its limit" case. Its ladder is the step-by-step path
from Humbird's design (scenarios.reference()) to scenarios.all_favourable(), and its last row IS that case. The earlier ladder
started from the low-lactate example ($49.96) and ended at $7.86; its pins are in the file's history. tests/test_ordering.py holds
the checks on the case itself (one number, the order of the reference points, lever by lever)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import floor_physics as fp
import frontier as F
import retention as R
import scenarios as S


def close(a, b, tol=1e-3):
    return abs(a - b) <= tol * max(1.0, abs(b))


def check() -> list:
    fails = []
    rows = F.ladder()
    a = S.all_favourable()
    # the last row is the all-favourable case: the same explore() arguments, so the same number
    if rows[-1]["kw"] != a["kw"] or rows[-1]["cost"] != a["cost"] or rows[-1]["cost"] != S.run(S.SCENARIOS["best"].choice)["total"]:
        fails.append("the last row is not scenarios.all_favourable() / the `best` scenario")
    # the first row is Humbird's design with his cell written as its four traits: scenarios.reference() to within 0.2%
    # (the traits are his to three decimals: 0.054 mol of ammonia a kilo, 0.279 mol of lactate per mol of glucose)
    ref = S.reference()["total"]
    if not close(rows[0]["cost"], ref, 2e-3):
        fails.append(f"the first row (${rows[0]['cost']:.4f}) is not scenarios.reference() (${ref:.4f})")
    # moving a lever to its favourable value never costs more, in the path's order
    for x, y in zip(rows, rows[1:]):
        if y["cost"] > x["cost"] + 1e-9:
            fails.append(f"'{y['name']}' raised the cost")
    # every explore() argument of the case is set by exactly one step
    used = [k for _n, keys, _w in F.steps() for k in keys]
    if sorted(used) != sorted(a["kw"]):
        fails.append("the steps do not cover the all-favourable case's arguments exactly once")
    # the path, pinned (the model's own output, 2026-11-20)
    # repinned 2026-11-20 (published studies as sources: a 5.3 ng cell from Risner 2021 and CE Delft 2021, 25 m³ tanks from SuperMeat 2024)
    # repinned 2026-11-20 (additions: viscosity lowers oxygen transfer, per-tank plant items; the cell's weight held at 3 ng, the
    # heaviest measured rule; 42 m³ tanks now cost least)
    # repinned 2026-11-21 (building power by floor and class, labour per tank, floor glucose 0.311, the tank design held thinner so
    # its oxygen-feeding loop passes, the column on the filter loop): was [15.945, 12.2424, 12.2424, 9.9371, 9.6923, 9.6923, 8.0977,
    # 7.6209, 7.6209, 7.6209, 7.6209]
    want = [15.7364, 12.0731, 12.0731, 9.7471, 9.5023, 9.5023, 7.4981, 6.9686, 6.9686, 6.9686, 6.9686]
    got = [r["cost"] for r in rows]
    if len(got) != len(want) or any(not close(g, w, 1e-4) for g, w in zip(got, want)):
        fails.append(f"the path moved: {[round(g, 4) for g in got]} != pinned {want}")
    # each lever alone, from Humbird's design, pinned
    alone = {n: c for n, c, _d in F.alone()}
    # repinned 2026-11-21 (as above). The tank design alone now costs more than Humbird's design (16.34 against 15.74; it saved
    # $0.35 before): the all-favourable case's design is a flat tank held at 219 g/L by its loop's checks, which pays only with
    # its fast cells and cheap filter
    want = {"Cells double in 16 hours": 12.0731, "Cells of 3 ng, Humbird's, the heaviest allowed": 15.7364,
            "Tanks of 42 m³ in place of 20 m³": 15.0079,
            "A food-grade plant with shared medium": 12.8447,
            "Dialyser-grade hollow fibres as the filter": 13.8666,
            "Dissolved oxygen held at about half of air saturation": 15.7364,
            "The cheapest tank design that passes the checks on the CO₂ loop": 16.3359,
            "The least medium flow at the lowest measured": 15.7364, "Culture up to 320 g/L in place of 258": 15.7364,
            "Medium at the nutrient floor": 15.7364}
    for n, w in want.items():
        if n not in alone or not close(alone[n], w, 1e-4):
            fails.append(f"{n} alone: {alone.get(n, float('nan')):.4f} != {w}")
    # the largest lever alone is the doubling time
    if min(alone, key=alone.get) != "Cells double in 16 hours":
        fails.append("the doubling time should be the largest lever on its own")
    # the all-favourable case is under half of Humbird's design and under a quarter of the low-lactate example
    central = S.run(S.SCENARIOS["central"].choice)["total"]
    if not (rows[-1]["cost"] < 0.5 * ref and rows[-1]["cost"] < 0.25 * central):
        fails.append("the all-favourable case should be under half of Humbird's design and under a quarter of the low-lactate example")
    # retention.duty and explore agree on the bleed (corrected 2026-11-20): with only the litres that leave with the cells, the
    # bleed carries out all the liquid, so there is no permeate and explore charges no membrane
    kw = {**a["kw"], "medium_l": 1.0}                         # explore raises it to 1000 / density
    d = R.duty(kw)
    if d["permeate_m3_h"] != 0.0 or d["result"]["membranes"] != 0.0 or R.sizing("tff", kw, d)["cons_kg"] != 0.0:
        fails.append(f"a case fed only the litres that leave with its cells should have no permeate and no membranes "
                     f"(permeate {d['permeate_m3_h']:.3g} m3/h, membranes ${d['result']['membranes']:.3g})")
    # with its own litres the case's filter sizing is explore's own (the dialyser's numbers, as explore's arguments)
    d = R.duty(a["kw"])
    sz = R.sizing("tff", a["kw"], d)
    if not (close(sz["cons_kg"], d["result"]["membranes"], 1e-9) and close(sz["capex_k_m3"], d["result"]["retention_capex"], 1e-9)):
        fails.append("retention.sizing('tff') does not give explore's membranes and filter capital for the all-favourable case")
    # since 2026-11-19 the model's floor IS GFI's cheapest (feed grade, efficient need), so at the defaults they coincide
    if not close(F.with_gfi_amino_acids(rows[-1]["kw"]), rows[-1]["cost"], 1e-9):
        fails.append("GFI's cheapest amino-acid floor should equal the model's all-favourable case")
    return fails


def test_frontier():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the path to the all-favourable case holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
