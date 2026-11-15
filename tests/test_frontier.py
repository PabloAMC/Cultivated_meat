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
    # moving a lever to its limit never costs more (the $0.05 step is already at the nutrient floor, so it adds nothing)
    for a, b in zip(rows, rows[1:]):
        if b["cost"] > a["cost"] + 1e-9:
            fails.append(f"'{b['name']}' raised the cost")
    if not rows[-1]["cost"] < 0.25 * rows[0]["cost"]:
        fails.append("the frontier should be well under a quarter of the central cost")
    # the single levers reproduce the numbers of the studies they come from
    alone = {n: c for n, c, _d in F.alone()}
    want = {"Medium at the least the physics allows: 6.4 L/kg, fed as a concentrate": 12.2803,
            "Dialyser-grade hollow fibres as the filter": 17.9978, "Medium at $0.05 a litre": 22.6790,
            "Cells double in 16 hours": 22.4851, "Culture at 320 g/L in place of 258": 25.7148,
            "A food-grade plant with shared medium": 24.3374}
    for n, w in want.items():
        if not close(alone[n], w, 1e-4):
            fails.append(f"{n}: {alone[n]:.4f} != {w}")
    # the largest lever alone is the least medium
    if min(alone, key=alone.get) != "Medium at the least the physics allows: 6.4 L/kg, fed as a concentrate":
        fails.append("the least-medium lever should be the largest on its own")
    # the pinned frontier, and the one with GFI's amino-acid floor
    if not close(rows[-1]["cost"], 5.4907, 1e-4):
        fails.append(f"frontier {rows[-1]['cost']:.4f} != pinned 5.4907")
    if not (close(F.with_gfi_amino_acids(rows[-1]["state"]), 6.2938, 1e-4) and
            F.with_gfi_amino_acids(rows[-1]["state"]) > rows[-1]["cost"]):
        fails.append("GFI's amino-acid floor should raise the frontier to about $6.29")
    return fails


def test_frontier():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the frontier holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
