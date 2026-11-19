#!/usr/bin/env python3
"""test_frontier.py — the cheapest a kilo of cells could cost with every lever at its limit (frontier.py)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import frontier as F
import scenarios as S


def close(a, b, tol=1e-3):
    return abs(a - b) <= tol * max(1.0, abs(b))


def check() -> list:
    fails = []
    rows = F.ladder()
    base = S.run(S.SCENARIOS["central"].choice)["total"]
    if not close(rows[0]["cost"], base, 1e-12):
        fails.append("the first step is not the central scenario")
    # moving a lever to its limit never costs more
    for a, b in zip(rows, rows[1:]):
        if b["cost"] > a["cost"] + 1e-9:
            fails.append(f"'{b['name']}' raised the cost")
    # 2026-11-19: Central fell $3.0 (growth factors inside its medium price) and the frontier rose $0.30 (the nutrient floor),
    # so the frontier is now about 27% of Central, not under a quarter
    if not rows[-1]["cost"] < 0.30 * rows[0]["cost"]:
        fails.append("the frontier should be under 30% of the central cost")
    # the single levers, pinned (since PR #32 the studies' own notes are snapshots of the earlier model)
    alone = {n: c for n, c, _d in F.alone()}
    # 2026-11-19 repin: nutrient floor $2.00, growth factors inside complete media prices (central $29.42 -> $26.43);
    # the "$0.05 a litre" lever is now "Medium at the nutrient floor" (growth factors bought on top); a complete medium no
    # longer costs less than its nutrients plus its growth factors (gf_in_medium), so 6.4 L/kg pays them: 13.3873 -> 14.0865
    want = {"Medium at the least the physics allows: 6.4 L/kg, fed as a concentrate": 14.0865,
            "Dialyser-grade hollow fibres as the filter": 18.2770, "Medium at the nutrient floor": 25.7653,
            "Cells double in 16 hours": 22.1112, "Culture at 320 g/L in place of 258": 26.4296,
            "A food-grade plant with shared medium": 23.5685}
    for n, w in want.items():
        if not close(alone[n], w, 1e-4):
            fails.append(f"{n}: {alone[n]:.4f} != {w}")
    # the largest lever alone is the least medium
    if min(alone, key=alone.get) != "Medium at the least the physics allows: 6.4 L/kg, fed as a concentrate":
        fails.append("the least-medium lever should be the largest on its own")
    # the pinned frontier, and the one with GFI's amino-acid floor
    if not close(rows[-1]["cost"], 7.1572, 1e-4):   # 6.8551 before 2026-11-19: the nutrient floor rose $0.30
        fails.append(f"frontier {rows[-1]['cost']:.4f} != pinned 7.1572")
    # since 2026-11-19 the model's floor IS GFI's cheapest (feed grade, efficient need), so at the defaults they coincide
    if not close(F.with_gfi_amino_acids(rows[-1]["state"]), rows[-1]["cost"], 1e-9):
        fails.append("GFI's cheapest amino-acid floor should equal the model's frontier")
    return fails


def test_frontier():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the frontier holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
