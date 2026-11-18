#!/usr/bin/env python3
"""test_retail_spreads.py — the retail markup rule (retail_spreads.py, price_ratio.shelf_price).

Checks that the shelf-price rule and its inverse agree, that the page's engine carries the same rule, that the USDA test still
rejects a pure percentage markup on the time series, and that the note quotes the module's numbers and table. Runs as a
script or under pytest.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import retail_spreads as RS  # noqa: E402
from inputs import value  # noqa: E402
from price_ratio import shelf_price, cost_from_shelf  # noqa: E402


def check() -> list:
    fails = []
    for c in (0.0, 9.66, 29.42):
        if abs(cost_from_shelf(shelf_price(c)) - c) > 1e-9:
            fails.append("cost_from_shelf does not invert shelf_price")
    if abs(shelf_price(10.0, 5.0, 0.0) - 15.0) > 1e-12:
        fails.append("a zero margin should give the flat rule")
    if abs(shelf_price(10.0) - (10.0 + value("markup_add")) / (1 - value("retail_margin"))) > 1e-12:
        fails.append("shelf_price is not (cost + markup_add) / (1 - retail_margin)")
    page = open(os.path.join(ROOT, "build_interactive.py"), encoding="utf-8").read()
    if "function shelfPrice(x,s,mk,mg){" not in page or "return (x+mk)/(1-mg);}" not in page:
        fails.append("the page's engine no longer carries the shelf-price rule")

    for sp in RS.SERIES:
        ratio = RS.last_year(sp)["ratio"]
        pt = RS.pass_through(sp, 60)[0]
        if not pt < 0.8 * ratio:
            fails.append(f"{sp}: five-year pass-through {pt:.2f} is no longer well below the percentage rule's {ratio:.2f}")

    note = open(os.path.join(ROOT, "research_notes", "retail_markup_form.md"), encoding="utf-8").read()
    for line in RS.rules_table().splitlines():
        if line not in note:
            fails.append(f"the note does not carry: {line[:80]}")
    names = {"beef": "Choice beef", "pork": "Pork", "broiler": "Broilers"}
    for sp, name in names.items():
        ly = RS.last_year(sp)
        pts = " / ".join(f"{RS.pass_through(sp, h)[0]:.2f}" for h in (12, 36, 60))
        row = (f"| {name} | {ly['retail']:.2f} | {ly['wholesale']:.2f} | {ly['ratio']:.2f} | {pts} | "
               f"${RS.fit_a(sp, value('retail_margin')):.2f} |")
        if row not in note:
            fails.append(f"the note's USDA table is stale: {row}")
    c, slope, _trend = RS.levels_fit("beef")
    if f"retail = ${c:.2f} + {slope:.2f} × wholesale" not in note:
        fails.append("the note's beef levels fit is stale")
    return fails


def test_retail_spreads():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    if fails:
        sys.exit(1)
    print("retail spreads: all checks passed")
