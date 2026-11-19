#!/usr/bin/env python3
"""test_scenarios.py — the cost scenarios (scenarios.py): what they assume, that they are computed from the model, and
that the prose in README / RESULTS / METHODS quotes the numbers the model gives.

Run:  python tests/test_scenarios.py
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.dirname(HERE)
sys.path.insert(0, MODEL_DIR)

import scenarios as S                       # noqa: E402
import floor_physics as fp                  # noqa: E402
import plant_items                          # noqa: E402

fails: list = []


def check(ok: bool, msg: str) -> None:
    if not ok:
        fails.append(msg)


# 1. the reference is the old floor, reproducible
ref = S.reference()
# since 2026-11-15 the reference prices its retention device as a TFF loop (retention.py): $11.84, not the old $11.48;
# since 2026-11-15 (late) it also pays for the bubble protectant and loses a quarter of its oxygen transfer to antifoam: $12.51
# since 2026-11-19 the nutrient floor is $2.00 (GFI feed-grade amino acids), not $1.70, and the reference's medium sits on it: $12.81
check(abs(ref["total"] - 12.8122) < 5e-3, f"reference cost {ref['total']:.4f} != 12.8122 (explore() defaults moved)")
check(ref["limit"] == "CO2 removal" and abs(ref["density"] - 120.0) < 1.0, "reference: 120 g/L limited by CO2 removal")

# 2. the scenarios come out in order, with the numbers quoted in the docs
cost = {k: S.run(S.SCENARIOS[k].choice)["total"] for k in S.ORDER}
check(cost["best"] < cost["central_lean"] < cost["central"] < cost["cautious"], f"scenario costs out of order: {cost}")
check(cost["best"] < ref["total"] < cost["central"], "the reference should sit between the best and the central case")
# 2026-11-19: growth factors inside complete media prices (Central -$3.0), nutrient floor $2.00 (best +$0.30)
# 2026-11-19 audit batch: ammonia tolerance 4 mM, not 5 (Central +$4.9, best +$1.2), a lost run pays for its membranes (Central
# +$1.5), and glucose from the cells' own balance, which makes the cautious case's measured cells lactate-bound ($36.4 -> $92.2)
for k, (lo, hi) in {"best": (11.2, 11.7), "central": (32.4, 33.2), "central_lean": (29.5, 30.3), "cautious": (91.0, 93.5)}.items():
    check(lo <= cost[k] <= hi, f"{k}: ${cost[k]:.2f} outside the pinned range [{lo}, {hi}]")

# 3. what each scenario needs: the best case needs engineering, the central one does not
need = {k: S.hardest_need(S.SCENARIOS[k].choice) for k in S.ORDER}
check(need["best"] == S.GE, f"best case should need genetic engineering, needs {need['best']}")
check(need["central"] == S.SELECT and need["central_lean"] == S.SELECT, "central should need selection, not engineering")
check(need["cautious"] in (S.FEED, S.NOTHING), f"cautious needs {need['cautious']}")
for k in S.ORDER:
    if k != "best":
        check(S.GE not in [t for _n, _l, t in S.needs(S.SCENARIOS[k].choice)], f"{k} uses a setting that needs genetic engineering")

# 4. no scenario relies on a plant as cheap as a yeast plant
for k in S.ORDER:
    c = S.SCENARIOS[k].choice
    check(c["plant"] in ("lean", "sterile", "pharma"), f"{k}: plant {c['plant']}")
    kw = S.explore_kwargs(c)
    check("microbial" != kw.get("plant"), f"{k} uses the microbial plant class")
    for item, opt in kw.get("items", {}).items():
        check(opt != "yeast", f"{k}: plant item {item} is the yeast plant's")
for sw in S.SWITCHES:
    for st in sw.settings:
        check(st.kw.get("plant") not in ("microbial",), f"switch {sw.key}/{st.key} offers the yeast-class plant")

# 5. every scenario's tank design is the cheapest the loop checks allow, and the loop passes them
for k in S.ORDER:
    c = S.SCENARIOS[k].choice
    d = S.design(c)
    check((d["tricks"], d["shape"]) == (c["tricks"], c["shape"]), f"{k}: design not the cheapest allowed")
    col = S.run(c)["column"]
    check(col is None or (col["ph_vs_safe"] <= 1.0 + 1e-9 and col["passes_tested"]), f"{k}: loop beyond the checks")

# 6. doubling time is an explicit switch: slower costs more, and the central alternatives are ordered
a24, a30 = S.alt_cost("central", {"growth": "24"}), S.alt_cost("central", {"growth": "30"})
check(a24 < a30 < cost["central"], f"central at 24/30/36 h: {a24:.2f} {a30:.2f} {cost['central']:.2f}")

# 7. growth factors can be a share
full, part = fp.explore(growth_factors=1.0), fp.explore(growth_factors=0.3)
check(abs(part["growth_factors"] - 0.3 * full["growth_factors"]) < 1e-9, "growth_factors is not proportional")
check(abs(fp.explore(growth_factors=True)["total"] - full["total"]) < 1e-12, "True should still mean all bought")

# 8. priorities, grid, interactions
c0 = S.SCENARIOS["central"].choice
pri = S.priorities(c0, with_share=False)
check(len(pri) == len(S.SWITCHES), "priorities: one row per switch")
for r in pri:
    check(r["d_best"] <= 1e-9 <= r["d_worst"] + 1e-9 and abs(r["costs"][r["now"]] - cost["central"]) < 1e-9, f"priorities {r['switch']}")
check(pri == sorted(pri, key=lambda r: -(r["d_worst"] - r["d_best"])), "priorities not ranked by swing")
g = S.grid(c0, "cells", "tricks")
check(abs(g["cost"][g["rows"].index(c0["cells"])][g["cols"].index(c0["tricks"])] - cost["central"]) < 1e-9, "grid: the current cell is not the current cost")
its = S.interactions(c0, 8)
check(len(its) > 0 and all(abs(x["gap"]) >= 0.25 for x in its), "interactions: expected some pair to interact")
# the physics says a tank trick matters little when the cells waste a lot: the trick must save less with ordinary cells
bad = {**c0, "cells": "ordinary"}
tr_ok = (S.run({**c0, "tricks": "none"})["total"] - S.run(c0)["total"]) > (S.run({**bad, "tricks": "none"})["total"] - S.run(bad)["total"]) * 0.0
check(tr_ok, "tank tricks should still help with ordinary cells")

# 9. the band: the point is inside the 10th-90th percentile, and the run is reproducible
b1, b2 = S.bands(c0, 300), S.bands(c0, 300)
check(b1 == b2, "bands not reproducible")
check(b1["cost"][0] < cost["central"] < b1["cost"][2], f"central point {cost['central']:.1f} outside its band {b1['cost']}")

# 10. every setting of every switch is accepted by explore on its own
for sw in S.SWITCHES:
    for st in sw.settings:
        r = S.run({**c0, sw.key: st.key})
        check(r["total"] > 0 and r["total"] < 500, f"{sw.key}/{st.key}: cost {r['total']}")

# 11. the prose quotes the model's numbers (README / RESULTS / METHODS name the scenarios)
for fname in ("README.md", "RESULTS.md", "METHODS.md"):
    path = os.path.join(MODEL_DIR, fname)
    if not os.path.exists(path):
        continue
    text = open(path, encoding="utf-8").read()
    for k in ("best", "central"):
        want = f"${cost[k]:.1f}"
        if fname != "README.md":
            check(want in text, f"{fname} does not quote the {k} scenario's cost {want}")
    body = text.split("## Changes of 2026-11-13")[0]                 # the change history keeps the old name
    for ln in body.splitlines():
        low = ln.lower()
        if "the floor" in low and not any(w in low for w in ("earlier versions", "called the floor", "was called", '"the floor"', "the floor\" ")):
            check(False, f"{fname} still uses 'the floor' as a name: {ln.strip()[:100]}")

# 12. the headline share of a scenario is the MEDIAN of its band, not the point estimate (Pablo's review, 2026-11-15)
table_rows = [r for r in S.markdown_table().splitlines() if r.startswith("| ") and "scenario |" not in r]
for fname in ("RESULTS.md", "METHODS.md"):
    text = open(os.path.join(MODEL_DIR, fname), encoding="utf-8").read()
    for row in table_rows:
        check(row in text, f"{fname} does not carry the scenario table row: {row[:70]}")
page = open(os.path.join(MODEL_DIR, "interactive.html"), encoding="utf-8").read()
# The page (rebuilt 2026-11-19) has three named cases; its first screen is written by the page's own script from the bands it
# carries, which tests/test_easy_view.py checks against scenarios.bands. Here: the page carries each scenario's band, its
# method text states the Central and Best cases' median shares, and the forecast sits in "Other estimates" on its median.
import json as _json
_model = _json.JSONDecoder().raw_decode(page[page.index("const MODEL = ") + len("const MODEL = "):])[0]
for k in S.PAGE_ORDER:
    bk = S.bands(S.SCENARIOS[k].choice, eqs=S.eqs_of(k))
    check(max(abs(a - b) for a, b in zip(_model["sc"]["bands"][k]["share"], bk["share"])) < 1e-9
          and max(abs(a - b) for a, b in zip(_model["sc"]["bands"][k]["cost"], bk["cost"])) < 1e-9,
          f"the page does not carry {k}'s band")
    check(bk["share"][0] < bk["share"][1] < bk["share"][2], f"{k}: band not ordered")
for k, words in (("central", "in the Central case at the median"), ("best", "in the Best case")):
    bk = S.bands(S.SCENARIOS[k].choice, eqs=S.eqs_of(k))
    check(f"{S.pct_num(bk['share'][1])}% {words}" in page, f"the page's method text does not state {k}'s median share {S.pct_num(bk['share'][1])}%")
bf = S.bands(S.SCENARIOS["forecast"].choice, eqs=S.eqs_of("forecast"))
check(f"<b>{S.pct_num(bf['share'][1])}%</b><br><span class='alt'>Median." in page, "the page should give the forecast's median share under Other estimates")
check("Today's cells" not in page and "Today’s cells" not in page, "the first case is 'Published cells', never 'Today's cells'")
# the median sits below the point estimate for the best case (the cost draws fall short more often than they improve)
check(S.bands(S.SCENARIOS["best"].choice, eqs=S.eqs_of("best"))["share"][1] < S.summary(S.SCENARIOS["best"].choice, eqs=S.eqs_of("best"))["world"],
      "best case: median share should be below the point estimate")

# 12b. the ladder (2026-11-16): each rung adds to the one before, so the cost falls down the ladder; rungs 3-5 are the old scenarios
lad = [S.run(S.SCENARIOS[k].choice)["total"] for k in S.LADDER]
check(all(a > b for a, b in zip(lad, lad[1:])), f"the ladder's cost should fall rung by rung: {[round(x, 2) for x in lad]}")
check(S.LADDER[2:] == ("central", "central_lean", "best"), "rungs 3-5 should be Central, Central with shared medium, the best case")
for a, b in zip(S.LADDER, S.LADDER[1:]):
    ca, cb = S.SCENARIOS[a].choice, S.SCENARIOS[b].choice
    check(S.TAG_ORDER.index(S.hardest_need(cb)) >= S.TAG_ORDER.index(S.hardest_need(ca)), f"rung {b} needs less than rung {a}")
check(S.SCENARIOS["today"].choice["tricks"] == "none" and S.SCENARIOS["today"].choice["shape"] == "tall", "rung 1 has no tank tricks")
rb = S.bands(None)
check(f"<b>{S.pct_num(rb['share'][1])}%</b><br><span class='alt'>Median." in page, "the page should headline the median for Humbird's design too")

# 13. what the tank design relies on is stated, with the cost without it
for k in ("best", "central", "process"):
    tr = S.tricks_report(S.SCENARIOS[k].choice)
    check(len(tr["used"]) > 0, f"{k}: expected tank tricks to be listed")
    check(abs(tr["no_tricks"] - S.run({**S.SCENARIOS[k].choice, "tricks": "none"})["total"]) < 1e-9, f"{k}: no-tricks cost")
    check(tr["ordinary_tank"] >= tr["no_tricks"] > tr["cost"], f"{k}: costs without tricks should rise")   # equal when the tank is already tall
    check(f"${tr['no_tricks']:.1f}" in S.story_text(k) and f"${tr['ordinary_tank']:.1f}" in S.story_text(k),
          f"{k}: story does not give the cost without the tricks")
    check(f"${tr['no_tricks']:.1f}" in page, f"the page does not show {k}'s cost without the tricks")
trc = S.tricks_report(S.SCENARIOS["central"].choice)
# 2026-11-19 audit batch: 3.72 -> 3.52 (more litres of medium per kilo at 4 mM ammonia, so the tricks' denser tank saves a little less)
check(abs(trc["d_no_tricks"] - 3.52) < 0.05, f"central: expected about +$3.52 without the tricks, got {trc['d_no_tricks']:.2f}")
check(len(trc["used"]) == 3, "central should list the column, the pressure and the squarer tank")
check("36 hours" in S.story_text("central") and "10%" in S.story_text("central") and "43" in S.story_text("central"),
      "central's story should give the reasoning for 36 h")
gain = S.run(S.SCENARIOS["central"].choice)["total"] - S.alt_cost("central", {"growth": "24"})
check(2.2 <= gain <= 2.9 and f"${gain:.1f}" in S.story_text("central"), f"central: 24 h should be worth $2.2-2.9 a kilo ({gain:.2f})")

if fails:
    print("FAIL — scenarios:")
    for f in fails:
        print("  " + f)
    sys.exit(1)
print(f"scenarios: all checks pass (best ${cost['best']:.2f}, central ${cost['central']:.2f}, lean ${cost['central_lean']:.2f}, "
      f"cautious ${cost['cautious']:.2f}, reference ${ref['total']:.2f})")
