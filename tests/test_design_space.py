#!/usr/bin/env python3
"""test_design_space.py — the tank design search and the price of each limit (design_space.py).

Checks that the search contains and reproduces the scenarios' own designs, that no design beats the ideal, that the frontier
is ordered, that lifting a limit never costs more, and that RESULTS.md and the note carry the module's tables. Run directly or
under pytest.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import design_space as D  # noqa: E402
import scenarios as S  # noqa: E402

TRICKS = {"none": ("none", "base"), "column": ("co2", "base"), "pressure": ("co2", "1"), "oxygen": ("o2", "1")}


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(b))


def check() -> list:
    fails = []
    for k in S.PAGE_ORDER:
        ch = S.SCENARIOS[k].choice
        own = S.run(ch)["total"]
        col, prs = TRICKS[ch["tricks"]]
        same = D.run(k, {"column": col, "pressure": prs, "shape": ch["shape"], "fat": "made", "vessel": "stirred"})
        if not close(same["cost"], own):
            fails.append(f"{k}: the scenario's own design costs {same['cost']:.4f} here, {own:.4f} in scenarios.py")
        all_ = D.designs(k)
        if len(all_) != 144:
            fails.append(f"{k}: expected 144 designs, got {len(all_)}")
        # the scenarios' tank designs are the cheapest of their own subset (scenarios.design), for every scenario that used it
        if k != "today":
            sub = [d for d in all_ if d["ok"] and d["design"]["vessel"] == "stirred"
                   and d["design"]["fat"] == "made" and (d["design"]["column"], d["design"]["pressure"]) in TRICKS.values()]
            if not close(sub[0]["cost"], own):
                fails.append(f"{k}: the cheapest of the scenarios' subset is {sub[0]['cost']:.4f}, the scenario {own:.4f}")
        # no design beats the ordinary tank with every gas limit lifted for free
        ideal = D.ideal(k)
        if ideal["limit"] != "thickness of the culture":
            fails.append(f"{k}: with every gas limit lifted the thickness should bind, got {ideal['limit']}")
        if min(d["cost"] for d in all_) < ideal["cost"] - 1e-9:
            fails.append(f"{k}: a design costs less than the ideal")
        # the frontier: more unproven elements only where they buy a lower cost
        for cage in (True, False):
            fr = D.frontier(k, cage)
            if any(not (a["unproven"] < b["unproven"] and a["cost"] > b["cost"]) for a, b in zip(fr, fr[1:])):
                fails.append(f"{k}: frontier not ordered (cage={cage})")
            if not all(d["ok"] for d in fr):
                fails.append(f"{k}: a frontier design fails its loop checks")
            if not cage and any(d["design"]["vessel"] == "caged" for d in fr):
                fails.append(f"{k}: the no-cage frontier holds a cage")
        if D.frontier(k)[-1]["cost"] > D.frontier(k, False)[-1]["cost"] + 1e-9:
            fails.append(f"{k}: allowing the cage should not cost more")
        # lifting a limit for free never costs more, and lifting all three gas limits is at least as good as any one
        rows = {lab: cost for lab, cost, _d, _x, _l in D.limit_prices(k)}
        base = rows["the scenario as it is"]
        if not close(base, own):
            fails.append(f"{k}: limit_prices' base is not the scenario")
        for lab, cost in rows.items():
            if lab != "a yeast plant with what animal cells need" and cost > base + 1e-9:
                fails.append(f"{k}: '{lab}' raised the cost")
        gas = rows["every gas limit lifted (CO₂, oxygen, mixing)"]
        if any(gas > rows[l] + 1e-9 for l in ("CO₂ removal lifted", "oxygen supply lifted", "mixing lifted")):
            fails.append(f"{k}: lifting every gas limit should be at least as good as lifting one")
    # pinned (2026-11-16; repinned 2026-11-19: growth factors inside the complete medium's price, -$2.99 Central and -$5.97 today;
    # best's medium at the $2.00 nutrient floor, +$0.30)
    for (k, what), want in {("central", "ideal"): 24.2023, ("central", "no_cage"): 24.9399, ("central", "cage"): 24.6306,
                            ("today", "ideal"): 28.8246, ("best", "ideal"): 9.6357}.items():
        got = D.ideal(k)["cost"] if what == "ideal" else D.frontier(k, what == "cage")[-1]["cost"]
        if not close(got, want, 2e-4):
            fails.append(f"{k} {what}: {got:.4f} != pinned {want}")
    # the docs carry the module's tables
    md = D.markdown().splitlines()
    for fname, lines in (("RESULTS.md", md[:8]), (os.path.join("research_notes", "design_space.md"), md)):
        text = open(os.path.join(ROOT, fname), encoding="utf-8").read()
        for line in lines:
            if line.strip() and line not in text:
                fails.append(f"{fname} does not carry: {line[:90]}")
    return fails


def test_design_space():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the design search holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
