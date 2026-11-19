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
    # so the frontier was about 27% of Central, not under a quarter
    # 2026-11-19 audit batch: Central rose to $32.80 (ammonia tolerance 4 mmol/L, lost runs pay for their membranes) and the
    # frontier did not move (no ammonia and no permeate at its litres), so the frontier is 22% of Central: under a quarter again
    if not rows[-1]["cost"] < 0.25 * rows[0]["cost"]:
        fails.append("the frontier should be under a quarter of the central cost")
    # the frontier's last state filters nothing: the bleed carries out all the liquid, so a lost run has no membrane to throw away
    import min_litres as _M
    import retention as _R
    _st = rows[-1]["state"]
    _kw = {**S.explore_kwargs(_st["choice"]), **_st.get("kw", {})}
    with _R._with(_st.get("patch", {})):
        _kw["medium_l"] = _M.bounds(_kw.get("doubling_h", 24.0), _kw.get("mass_pg", 3000.0))[_st["waste_floor"]]
        _d = _R.duty(_kw)
    if _d["permeate_m3_h"] > 1e-9:
        fails.append("the frontier should have no permeate (the bleed carries out all the liquid)")
    # the single levers, pinned (since PR #32 the studies' own notes are snapshots of the earlier model)
    alone = {n: c for n, c, _d in F.alone()}
    # 2026-11-19 repin: nutrient floor $2.00, growth factors inside complete media prices (central $29.42 -> $26.43);
    # the "$0.05 a litre" lever is now "Medium at the nutrient floor" (growth factors bought on top); a complete medium no
    # longer costs less than its nutrients plus its growth factors (gf_in_medium), so 6.4 L/kg pays them: 13.3873 -> 14.0865
    # 2026-11-19 audit batch: Central $26.43 -> $32.80 (ammonia tolerance 5 -> 4 mmol/L, so 28 -> 35 L/kg; lost runs pay for
    # their membranes). Every single lever starts from the higher Central; 6.4 L/kg moved only by the membranes of lost runs
    # (14.0865 -> 14.1614). Runs lost 0.2% a day is pinned too: it now saves $2.53, not $0.97, and ranks above the gas.
    # The dialyser-grade fibres: 18.2770 -> 20.2877, with retention.sizing also charging a lost run's membranes (run_frac).
    want = {"Medium at the least the physics allows: 6.4 L/kg, fed as a concentrate": 14.1614,
            "Dialyser-grade hollow fibres as the filter": 20.2877, "Medium at the nutrient floor": 31.4542,
            "Cells double in 16 hours": 28.3001, "Culture at 320 g/L in place of 258": 32.8028,
            "A food-grade plant with shared medium": 29.9417,
            "Runs lost 0.2% a day, as in pharma": 30.2700, "Gas at up to 6 mm/s": 31.1313}
    for n, w in want.items():
        if not close(alone[n], w, 1e-4):
            fails.append(f"{n}: {alone[n]:.4f} != {w}")
    # the largest lever alone is the least medium
    if min(alone, key=alone.get) != "Medium at the least the physics allows: 6.4 L/kg, fed as a concentrate":
        fails.append("the least-medium lever should be the largest on its own")
    # the pinned frontier, and the one with GFI's amino-acid floor
    # 6.8551 before 2026-11-19: the nutrient floor rose $0.30. 2026-11-19 audit batch: unchanged at 7.1572
    if not close(rows[-1]["cost"], 7.1572, 1e-4):
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
