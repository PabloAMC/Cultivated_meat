#!/usr/bin/env python3
"""test_market_size_loop.py — cost falling with market size, solved with the share (market_size_loop.py).

Checks that with no learning the module returns each scenario's own cost, that cost falls with volume and never below the cost at the
floors, that a resting point is one (its cost buys the share its volume is), that premium products carry Central past the membrane
switch in the central case and not with slow learning (two resting points), and that the note and RESULTS.md carry the module's tables
and the figures their prose quotes. Runs as a script or under pytest.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import market_size_loop as L  # noqa: E402
import scenarios as S  # noqa: E402
from inputs import value  # noqa: E402


def check() -> list:
    fails = []
    s = L.summary()
    none = {"ms_switch_area": L.NEVER, "ms_lr_plant": 0.0}       # no food-grade supplier and no plant learning
    for k in L.SCEN:
        choice = S.SCENARIOS[k].choice
        own = S.run(choice)["total"]
        if abs(L.cost_at(choice, 5.0, none)["cost"] - own) > 1e-9 or abs(L.cost_at(choice, 0.0)["cost"] - own) > 1e-9:
            fails.append(f"{k}: with no learning, or no volume, the cost is not the scenario's own")
        costs = [r["cost"] for r in s["ladder"][k]]
        if costs != sorted(costs, reverse=True):
            fails.append(f"{k}: the cost should fall as the volume rises")
        if not s["floor"][k]["cost"] <= costs[-1] + 1e-9:
            fails.append(f"{k}: a cost on the ladder is below the cost at the floors")
        for case in L.CASES:
            for start in ("below", "above"):
                r = s["solved"][(k, case, start)]
                if abs(r["share"] - 100.0 * r["volume_mt"] / value("ms_world_meat")) > 1e-3:
                    fails.append(f"{k}, {case}, from {start}: the resting point's cost does not buy the share its volume is")
        lo, hi = s["solved"][(k, "central", "below")], s["solved"][(k, "central", "above")]
        if abs(lo["volume_mt"] - hi["volume_mt"]) > 1e-3 * hi["volume_mt"]:
            fails.append(f"{k}: two resting points in the central case now; the note says there is one")
        if k != "today" and not lo["share"] > s["model_share"][k]:
            fails.append(f"{k}: learning no longer raises the share; rewrite the note")
        c = s["comp"][(k, "resting point")]
        if abs(c["total"] - lo["volume_mt"]) > 1e-3 * lo["volume_mt"] + 1e-6:
            fails.append(f"{k}: the volumes by tier do not add to the resting point's volume")
    # the trap: with slow learning Central rests at two points, because premium products alone do not reach the membrane switch
    lo, hi = s["solved"][("central", "slow learning", "below")], s["solved"][("central", "slow learning", "above")]
    if not (hi["volume_mt"] > 1.5 * lo["volume_mt"] and not s["start"][("central", "slow learning")]["crosses"]):
        fails.append("Central with slow learning no longer has two resting points; rewrite the note's section on the trap")
    if not (s["start"][("central", "central")]["crosses"] and not s["start"][("today", "central")]["crosses"]):
        fails.append("which scenarios' premium products cross the membrane switch has changed; rewrite the note")
    if not s["comp"][("central", "no learning")]["premium_of_sales"] > 0.9:
        fails.append("premium products are no longer nearly all of Central's sales; rewrite the note")

    for k in ("central", "best"):
        if not s["passes"][k]["later_rounds"] < 0.3:
            fails.append(f"{k}: later rounds now give 30% or more of the share gain; the note says it is mostly one step")
    if not s["anchored"]["best"]["share"] < 0.5 * s["passes"]["best"]["rest"][1]:
        fails.append("the best case's share with demand anchored on premium meats is no longer well below the main model's; rewrite the note")

    sv = s["solved"]
    quoted = []
    for k in L.SCEN:
        for case in L.CASES:
            r = sv[(k, case, "below")]
            quoted += [f"${r['cost']:.2f}", f"{r['share']:.2f}%"]
        quoted.append(f"${s['floor'][k]['cost']:.2f}")
    for name, tables in (("research_notes/market_size_loop.md", [L.markdown_ladder(), L.markdown_solved(), L.markdown_composition(), L.markdown_start(), L.markdown_passes(),
                          L.markdown_sensitivity()]), ("RESULTS.md", [])):
        text = open(os.path.join(ROOT, name), encoding="utf-8").read()
        for line in "\n".join(tables).splitlines():
            if line.strip() and line not in text:
                fails.append(f"{name} does not carry: {line[:90]}")
        for q in (quoted if name.startswith("research") else
                  [f"${sv[(k, 'central', 'below')]['cost']:.2f}" for k in ("central", "best")] + [f"{sv[(k, 'central', 'below')]['share']:.2f}%" for k in ("central", "best")]):
            if q not in text:
                fails.append(f"{name} does not quote {q}")
    return fails


def test_market_size_loop():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    if fails:
        sys.exit(1)
    print("market size loop: all checks passed")
