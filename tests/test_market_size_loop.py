#!/usr/bin/env python3
"""test_market_size_loop.py — cost falling with market size, solved with the share (market_size_loop.py).

Checks that with no learning the module returns each scenario's own cost, that cost falls with volume and never below the cost at the
floors, that a resting point is one (its cost buys the share its volume is), that premium products alone just carry Central past the
membrane switch while ordinary cuts make most of its sales, that Central crosses even a slow-learning switch on its own (one resting
point), how the premium products respond to price against history, and that the note and RESULTS.md carry the module's tables and
the figures their prose quotes. Runs as a script or under pytest.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import market_size_loop as L  # noqa: E402
from market_size_loop import _case  # noqa: E402
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
        if abs(lo["volume_mt"] - hi["volume_mt"]) > 1e-3 * hi["volume_mt"] + 1e-6:
            fails.append(f"{k}: two resting points in the central case now; the note says there is one")
        if k != "today" and not lo["share"] > s["model_share"][k]:
            fails.append(f"{k}: learning no longer raises the share; rewrite the note")
        c = s["comp"][(k, "resting point")]
        if abs(c["total"] - lo["volume_mt"]) > 1e-3 * lo["volume_mt"] + 1e-6:
            fails.append(f"{k}: the volumes by tier do not add to the resting point's volume")
    # 2026-11-19: cuts cost 0.8 cells + matrix + assembly, so cuts are cheaper and Central sells more than four times as much.
    # Premium products alone now just reach the switch for Central (1.11 million m2 against 1.0), not for today's cells or the
    # best case; Central's and the best case's whole sales cross it by far.
    for k in L.SCEN:
        st = s["start"][(k, "central")]
        whole = s["base"][k]["area_per_kg"] * s["model_share"][k] / 100.0 * value("ms_world_meat") * 1e9
        if st["crosses"] != (k == "central") or (k != "today") != (whole > st["switch_m2"]):
            fails.append(f"{k}: premium products alone, or the whole sales, now stand differently against the membrane switch; rewrite the note")
        if k == "central" and not st["area_m2"] < 1.25 * st["switch_m2"]:
            fails.append("Central's premium products alone are now well past the switch, not just at it; rewrite the note")
    # 2026-11-19: cuts cost 0.8 cells + matrix + assembly; Central with slow learning crosses a 3 million m2 switch on its own sales,
    # so it has one resting point (well below its own cost), not two.
    lo, hi = s["solved"][("central", "slow learning", "below")], s["solved"][("central", "slow learning", "above")]
    if not (abs(hi["volume_mt"] - lo["volume_mt"]) < 1e-3 * hi["volume_mt"] and lo["area_m2"] > _case("slow learning")["ms_switch_area"]
            and lo["cost"] < 0.8 * s["base"]["central"]["cost"]):
        fails.append("Central with slow learning no longer crosses the switch on its own to one resting point; rewrite the note's section 3")
    # 2026-11-19: cuts cost 0.8 cells + matrix + assembly; premium products are now a small part of Central's sales (11%), ordinary
    # cuts most of it.
    c0 = s["comp"][("central", "no learning")]
    if not (0.05 < c0["premium_of_sales"] < 0.2 and c0["cut"] > 0.5 * c0["total"]):
        fails.append("premium products' part of Central's sales has left 5-20%, or cuts are no longer most of it; rewrite the note")
    # 2026-11-19: cuts cost 0.8 cells + matrix + assembly; where cultivated meat is still dearer than the premium product at both
    # costs it responds within history's range (along the curve to the totals); where it undercuts it once the membrane is cheap
    # (prime beef 0.52x, sushi 0.67x at $15.05) it responds less than history along the curve; none above the totals.
    for n, v in s["response"]["products"].items():
        dearer = v["R"][1] > 1.0
        if dearer and not L.HISTORY_ALONG_CURVE[0] <= v["response"] < L.HISTORY_TOTAL[1]:
            fails.append(f"{n}: the response to price where cultivated meat is dearer has left history's range; rewrite the note")
        if not dearer and not 0.5 * L.HISTORY_ALONG_CURVE[0] < v["response"] < L.HISTORY_ALONG_CURVE[0]:
            fails.append(f"{n}: the response to price where cultivated meat undercuts is no longer below history's; rewrite the note")

    for k in ("central", "best"):
        if not s["passes"][k]["later_rounds"] < 0.35:
            fails.append(f"{k}: later rounds now give 35% or more of the share gain; the note says it is mostly one step")
    if not s["anchored"]["best"]["share"] < 0.7 * s["passes"]["best"]["rest"][1]:
        fails.append("the best case's share with demand anchored on premium meats is no longer well below the main model's; rewrite the note")

    sv = s["solved"]
    quoted = []
    for k in L.SCEN:
        for case in L.CASES:
            r = sv[(k, case, "below")]
            quoted += [f"${r['cost']:.2f}", f"{r['share']:.2f}%"]
        quoted.append(f"${s['floor'][k]['cost']:.2f}")
    for name, tables in (("research_notes/market_size_loop.md", [L.markdown_ladder(), L.markdown_solved(), L.markdown_composition(), L.markdown_start(), L.markdown_passes(),
                          L.markdown_sensitivity(), L.markdown_response()]), ("RESULTS.md", [])):
        text = open(os.path.join(ROOT, name), encoding="utf-8").read()
        for line in "\n".join(tables).splitlines():
            if line.strip() and line not in text:
                fails.append(f"{name} does not carry: {line[:90]}")
        up = sv[("central", "central", "above")]
        for q in (quoted if name.startswith("research") else
                  [f"${sv[('central', 'central', 'below')]['cost']:.2f}", f"${up['cost']:.2f}", f"{up['share']:.2f}%",
                   f"${sv[('best', 'central', 'below')]['cost']:.2f}", f"{sv[('best', 'central', 'below')]['share']:.2f}%"]):
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
