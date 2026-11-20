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
# 2026-11-19: growth factors inside complete media prices (the low-lactate example -$3.0), nutrient floor $2.00 (best +$0.30)
# 2026-11-19 audit batch: ammonia tolerance 4 mM, not 5 (the low-lactate example +$4.9, best +$1.2), a lost run pays for its membranes (the low-lactate example
# +$1.5), and glucose from the cells' own balance, which makes the cautious case's measured cells lactate-bound ($36.4 -> $92.2)
for k, (lo, hi) in {"best": (11.2, 11.7), "central": (32.4, 33.2), "central_lean": (29.5, 30.3), "cautious": (91.0, 93.5)}.items():
    check(lo <= cost[k] <= hi, f"{k}: ${cost[k]:.2f} outside the pinned range [{lo}, {hi}]")

# 3. what each scenario needs (since 2026-11-19 no tag names a route: cells with other traits than the published ones are tagged
# CELLS, never "selection" or "genetic engineering", the author's direction)
need = {k: S.hardest_need(S.SCENARIOS[k].choice) for k in S.ORDER}
check(need["best"] == S.CELLS and need["central"] == S.CELLS and need["central_lean"] == S.CELLS,
      f"the low-lactate example and the all-favourable example need cells with other traits than those published: {need}")
check(need["cautious"] in (S.FEED, S.NOTHING), f"cautious needs {need['cautious']}")
for k in ("today", "process"):
    check(S.CELLS not in [t for _n, _l, t in S.needs(S.SCENARIOS[k].choice)], f"{k} uses cells with other traits than those published")
_ROUTE = __import__("re").compile(r"genetic|engineer|selection|adapt|routes?\b|other cells|shown together|least intrusive|\bCHO\b", __import__("re").I)
for t in list(S.TAG_PLAIN.values()) + [st.label + " " + st.note for sw in S.SWITCHES if sw.key in ("cells", "growth", "gf") for st in sw.settings]:
    check(not _ROUTE.search(t.replace("Humbird's efficient", "")), f"a setting's words name a route: {t[:120]}")

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
# method text states the low-lactate example and Best cases' median shares, and the forecast sits in "Other estimates" on its median.
import json as _json
_model = _json.JSONDecoder().raw_decode(page[page.index("const MODEL = ") + len("const MODEL = "):])[0]
for k in S.PAGE_ORDER:
    bk = S.bands(S.SCENARIOS[k].choice, eqs=S.eqs_of(k))
    check(max(abs(a - b) for a, b in zip(_model["sc"]["bands"][k]["share"], bk["share"])) < 1e-9
          and max(abs(a - b) for a, b in zip(_model["sc"]["bands"][k]["cost"], bk["cost"])) < 1e-9,
          f"the page does not carry {k}'s band")
    check(bk["share"][0] < bk["share"][1] < bk["share"][2], f"{k}: band not ordered")
# 2026-11-19: the page was rebuilt with the new names (the low-lactate example; the all-favourable example)
for k, words in (("central", "in the low-lactate example at the median"), ("best", "in the all-favourable example")):
    bk = S.bands(S.SCENARIOS[k].choice, eqs=S.eqs_of(k))
    check(f"{S.pct_num(bk['share'][1])}% {words}" in page, f"the page's method text does not state {k}'s median share {S.pct_num(bk['share'][1])}%")
check("Today's cells" not in page and "Today’s cells" not in page, "the first case is 'Published cells', never 'Today's cells'")
# the median sits below the point estimate for the all-favourable example (the cost draws fall short more often than they improve)
check(S.bands(S.SCENARIOS["best"].choice, eqs=S.eqs_of("best"))["share"][1] < S.summary(S.SCENARIOS["best"].choice, eqs=S.eqs_of("best"))["world"],
      "the all-favourable example: median share should be below the point estimate")

# 12b. the ladder (2026-11-16; rebuilt 2026-11-19 restructure): it starts from what has been shown (fed-batch at 20 m3), adds one
# kind of change per rung, and the cost falls rung by rung. Rungs 4, 5 and 7 are the low-lactate example, the low-lactate example with shared medium, the all-favourable example
lad = [S.run(S.SCENARIOS[k].choice)["total"] for k in S.LADDER]
check(all(a > b for a, b in zip(lad, lad[1:])), f"the ladder's cost should fall rung by rung: {[round(x, 2) for x in lad]}")
check(S.LADDER == ("today", "process", "selected", "central", "central_lean", "engineered", "best"), f"ladder: {S.LADDER}")
for a, b in zip(S.LADDER, S.LADDER[1:]):
    ca, cb = S.SCENARIOS[a].choice, S.SCENARIOS[b].choice
    check(S.TAG_ORDER.index(S.hardest_need(cb)) >= S.TAG_ORDER.index(S.hardest_need(ca)), f"rung {b} needs less than rung {a}")
STEP = {("today", "process"): {"gas", "restart", "gf", "medium"}, ("process", "selected"): {"cells", "growth"},
        ("selected", "central"): {"mode"}, ("central", "central_lean"): {"plant"}, ("central_lean", "engineered"): {"cells"},
        ("engineered", "best"): {"growth", "gas", "losses", "gf", "medium"}}
for (a, b), want in STEP.items():
    ca, cb = S.SCENARIOS[a].choice, S.SCENARIOS[b].choice
    got = {k for k in S.KEYS if ca[k] != cb[k]} - {"tricks", "shape"}         # the tank design is chosen again at each rung
    check(got == want, f"rung {a} -> {b} changes {sorted(got)}, expected {sorted(want)}")
check(S.SCENARIOS["today"].choice["tricks"] == "none" and S.SCENARIOS["today"].choice["shape"] == "tall", "rung 1 has no tank tricks")
for k in ("today", "process", "selected"):
    check(S.SCENARIOS[k].choice["mode"] == "fedbatch", f"{k} should be fed-batch at 20 m3, what has been shown")
for k in ("central", "central_lean", "engineered", "best", "cautious"):
    check(S.SCENARIOS[k].choice["mode"] == "perfusion", f"{k} should be in perfusion")

# 12c. the mass balance (2026-11-19): a batch ends at no more than pf_batch_end_x times the waste level perfusion is held to
from inputs import value as _v
for k in ("today", "process", "selected"):
    c = S.SCENARIOS[k].choice
    if c["mode"] == "perfusion":
        continue
    r = S.run(c)
    nh3_end = r["density"] * r["nh3_kg"]                         # mmol/L at the end of the batch
    lac_end = r["density"] * r["lac_kg"]
    check(nh3_end <= _v("pf_batch_end_x") * _v("sc_nh3_limit") + 1e-6 and lac_end <= _v("pf_batch_end_x") * _v("pf_lac_limit") + 1e-6,
          f"{k}: the batch ends at {nh3_end:.2f} mM ammonia and {lac_end:.1f} mM lactate, above the allowed level")
    check(abs(r["medium_l"] - 1000.0 / r["density"]) < 1e-6 or r["medium_l"] == _v("pf_medium_l_floor"), f"{k}: a batch's medium is 1000/density")
# the published cells stop below the densities companies report at 20 m3 (Vow 27 g/L; Upside's capacity needs 33 g/L or more in
# fed-batch), and the low-lactate cells reach the bottom of Upside's range: so the companies' cells make less lactate than the published
check(S.run(S.SCENARIOS["today"].choice)["density"] < _v("vm_x_meat_shown"), "the published cells should stop below 27 g/L in a batch")
check(S.run(S.SCENARIOS["selected"].choice)["density"] >= 33.0, "the low-lactate cells should reach Upside's 33 g/L in a batch")
# a fed-batch plant keeps Humbird's full seed train when the plant is the shared-medium one
check(S.explore_kwargs({**S.SCENARIOS["central_lean"].choice, "mode": "fedbatch"})["items"]["seed"] == "full", "fed-batch lean plant: full seed train")
check(S.explore_kwargs(S.SCENARIOS["central_lean"].choice)["items"]["seed"] == "two", "perfusion lean plant: two seed trains")

# 12d. cells as traits (2026-11-19, the author's direction: no forecast, no framing that makes engineering look necessary).
# routes_needed says what each trait level has been shown with, never that engineering is needed
import cell_traits as CT
for k in S.LADDER:
    tr = S.cell_traits(S.SCENARIOS[k].choice)
    check(set(tr) == set(CT.TRAITS), f"{k}: four traits expected")
    v = CT.routes_needed(tr)["verdict"]
    check(not any(w in v.lower() for w in ("necessary", "is needed", "requires", "must be engineered")), f"{k}: verdict says engineering is needed")
check(CT.routes_needed(S.cell_traits(S.SCENARIOS["today"].choice))["rank"] == 0, "the published cells' traits are shown in meat cells")
check(CT.routes_needed({"nh3_kg": 0.0, "lac_yield": 1.05, "doubling_h": 43.0, "mass_pg": 2000.0})["rank"] == 2, "zero ammonia: engineering only")
check(CT.routes_needed({"nh3_kg": 0.14, "lac_yield": 1.05, "doubling_h": 10.0, "mass_pg": 2000.0})["rank"] == 3, "10 h: not shown")
check(CT.trait_route("lac_yield", 0.42) == "select_other" and CT.trait_route("doubling_h", 20.0) == "select_meat", "trait routes")
check(CT.routes_needed({"nh3_kg": 0.14, "doubling_h": 36.0})["together"], "low ammonia with fast growth: not shown together")
# the clouds take traits directly: a trait set by the reader is held, and the other draws do not move
a = S.scenario_mc(S.SCENARIOS["central"].choice, 200, traits={"nh3_kg": 0.14})
b = S.scenario_mc(S.SCENARIOS["central"].choice, 200)
check("nh3_kg" not in a and abs(a["capex_x"] - b["capex_x"]).max() == 0.0, "scenario_mc(traits=...) should hold the trait and keep the other draws")
# what it would take: the cost of cells a share needs falls as the share rises, and rises with the liking
w = S.what_it_would_take()
need = {(round(r["buyers"], 3), r["target"]): r["need"] for r in w}
lo_b = min(b_ for b_, _t in need)
check(need[(lo_b, 1.0)] > (need[(lo_b, 10.0)] or 0.0) and need[(0.5, 1.0)] > need[(lo_b, 1.0)], f"what it would take: {need}")
check(abs(S.meat_buyers_at_equal_price() - 0.145) < 0.002, "the model's 13% of all choices is 14.5% of meat buyers")
check(abs(S.world_share(S.run(S.SCENARIOS["central"].choice)["total"], None) - S.shares(S.run(S.SCENARIOS["central"].choice)["total"])["global"]) < 1e-12,
      "world_share at the model's own liking is shares()")
for r in w:
    if r["pick"] is not None:
        check(r["pick"][0] <= r["need"] + 1e-9, "a picked trait set must reach the cost")

# 13. what the tank design relies on is stated, with the cost without it (rung 2 is fed-batch since 2026-11-19 and uses no tricks)
check(S.tricks_report(S.SCENARIOS["process"].choice)["used"] == [], "rung 2 (fed-batch) should use no tank tricks")
for k in ("best", "central"):
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

# 12e. what has been measured in meat cells, with its source (data only; since 2026-11-19 the page and the docs carry no routes)
best = CT.best_in_meat_cells()
check(set(best) == set(CT.TRAITS), "a best meat-cell measurement (or none) for each trait")
check(best["nh3_kg"]["value"] == 0.14 and best["lac_yield"]["value"] == 1.05 and best["doubling_h"]["value"] == 15.0
      and best["mass_pg"]["value"] == 3300.0, f"best measured in meat cells: {[(k, b['value']) for k, b in best.items()]}")
check(CT.beyond_measured({"nh3_kg": 0.14, "lac_yield": 1.05, "doubling_h": 43.0, "mass_pg": 2000.0}) == [], "Published cells: nothing beyond")
check(CT.beyond_measured(S.cell_traits(S.SCENARIOS["central"].choice)) == ["lac_yield"], "the low-lactate example: only the lactate is beyond")
check(set(CT.beyond_measured({"nh3_kg": 0.0, "doubling_h": 13.0, "mass_pg": 3400.0})) == {"nh3_kg", "doubling_h", "mass_pg"}, "beyond_measured")
for r in w:
    if r["pick"] is not None:
        others = [g for g in S.trait_grid() if g[0] <= r["need"]]
        check(len(r["pick"][4]["beyond"]) == min(len(g[4]["beyond"]) for g in others),
              "what it would take picks the set with the fewest traits beyond the best measured in meat cells")
# the docs carry no route claims and no routes table (the author, 2026-11-19: "I would remove it")
for fname in ("README.md", "RESULTS.md", "METHODS.md"):
    text = open(os.path.join(MODEL_DIR, fname), encoding="utf-8").read()
    check(CT.markdown().splitlines()[0] not in text, f"{fname} still carries the routes table")
    for bad in ("No genetic engineering needed", "shown only with genetic engineering", "shown without engineering", "only in other cells",
                "not yet together in one meat cell", "least intrusive", "routes_needed", "selection or adaptation", "[genetic engineering]"):
        check(bad not in text, f"{fname} still makes a route claim: '{bad}'")

# 14. RESULTS carries what it would take and the plant-cost axis (generated, by line)
for lab, md, docs in (("what it would take", S.what_it_would_take_markdown(), ("RESULTS.md",)),
                      ("plant axis", S.plant_axis_markdown(), ("RESULTS.md",))):
    for fname in docs:
        text = open(os.path.join(MODEL_DIR, fname), encoding="utf-8").read()
        for ln in md.splitlines():
            if ln.strip():
                check(ln in text, f"{fname} does not carry the {lab} table line: {ln[:80]}")
check("forecast for 2035" not in open(os.path.join(MODEL_DIR, "RESULTS.md"), encoding="utf-8").read().split("## 1.")[0].lower(),
      "the Summary should not lead with a forecast (the author's direction, 2026-11-19)")

if fails:
    print("FAIL — scenarios:")
    for f in fails:
        print("  " + f)
    sys.exit(1)
print(f"scenarios: all checks pass (best ${cost['best']:.2f}, central ${cost['central']:.2f}, lean ${cost['central_lean']:.2f}, "
      f"cautious ${cost['cautious']:.2f}, reference ${ref['total']:.2f})")
