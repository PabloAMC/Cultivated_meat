#!/usr/bin/env python3
"""test_design_space.py — the tank design search and the price of each limit (design_space.py).

Checks that the search contains and reproduces the scenarios' own designs, that no design beats the ideal for its own feed, that
the frontier is ordered, that lifting a limit never costs more, and that RESULTS.md and the note carry the module's tables. Run directly or
under pytest.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import design_space as D  # noqa: E402
import floor_physics as fp  # noqa: E402
import scenarios as S  # noqa: E402
import vessels as V  # noqa: E402

TRICKS = {"none": ("none", "base"), "column": ("co2", "base"), "pressure": ("co2", "1"), "oxygen": ("o2", "1")}


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(b))


def ideal_fat_fed(key: str) -> dict:
    """design_space.ideal with fat taken from the feed: the ordinary tall tank, every gas and mixing limit lifted for free."""
    kw = V.explore_kwargs("stirred", "perfusion", {**D.base_kwargs(key), **D._option("fat", "fed")[2]})
    kw["vm"] = {**kw["vm"], **D._FREE_GAS}
    return fp.explore(**kw)


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
        # no design beats the ordinary tank with every gas limit lifted for free, on the same feed.
        # 2026-11-19 audit batch: was "no design costs less than the ideal". Glucose now comes from the cells' balance, so fat
        # taken from the feed cuts the glucose, the lactate and, where lactate sets the medium (today and process: 95 -> 66
        # L/kg), the litres. Those fat-fed designs cost less than the ideal, which keeps the scenario's feed. So each feed has its
        # own bound, and the fat-fed designs pass the scenario-feed ideal exactly where lactate sets the scenario's medium.
        ideal, ideal_fed = D.ideal(k), ideal_fat_fed(k)
        if ideal["limit"] != "thickness of the culture":
            fails.append(f"{k}: with every gas limit lifted the thickness should bind, got {ideal['limit']}")
        made = min(d["cost"] for d in all_ if d["design"]["fat"] == "made")
        fed = min(d["cost"] for d in all_ if d["design"]["fat"] == "fed")
        if made < ideal["cost"] - 1e-9:
            fails.append(f"{k}: a design on the scenario's feed costs less than the ideal")
        if fed < ideal_fed["total"] - 1e-9:
            fails.append(f"{k}: a fat-fed design costs less than the ideal with fat fed")
        lactate_sets = S.run(ch)["medium_set_by"] == "lactate"
        if lactate_sets != (fed < ideal["cost"] - 1e-9):
            fails.append(f"{k}: fat-fed designs should beat the scenario-feed ideal where lactate sets the medium, and only there "
                         f"(lactate sets it: {lactate_sets}; cheapest fat-fed {fed:.2f}, ideal {ideal['cost']:.2f}): rewrite section 4, "
                         "point 2 of research_notes/design_space.md")
        if lactate_sets and not ideal_fed["medium_l"] < ideal["medium_l"] - 1.0:
            fails.append(f"{k}: fat from the feed should cut the litres of medium where lactate sets them")
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
    # 2026-11-19 audit batch: ammonia tolerance 4 mmol/L and membranes for lost runs (Central +$6.46, best +$1.50); glucose from the
    # cells' balance (today's ideal +$56.03: the published cells' lactate sets 95 L/kg, and no gas exchange changes that).
    # New pins: today's cheapest designs and its ideal with fat fed, which now sit below its scenario-feed ideal
    for (k, what), want in {("central", "ideal"): 30.6623, ("central", "no_cage"): 31.3999, ("central", "cage"): 31.0906,
                            ("today", "ideal"): 84.8548, ("best", "ideal"): 11.1313,
                            ("today", "no_cage"): 64.9412, ("today", "cage"): 61.7755, ("today", "ideal_fed"): 61.2604}.items():
        if what == "ideal_fed":
            got = ideal_fat_fed(k)["total"]
        else:
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
