#!/usr/bin/env python3
"""test_tank_size.py — cost against tank size (tank_size.py): the 20 m3 row is the scenario's own, the numbers are pinned,
the design is chosen again under the loop checks, the what-if adjustments vanish at 20 m3, and the note quotes the model.

Run:  python tests/test_tank_size.py
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.dirname(HERE)
sys.path.insert(0, MODEL_DIR)

import floor_physics as fp                  # noqa: E402
import scenarios as S                       # noqa: E402
import tank_size as T                       # noqa: E402

# $/kg at 2, 5, 10, 20, 50, 100, 200 m3, tank design chosen again at each size
# repinned 2026-11-19: nutrient floor $2.00 (+$0.30 where it binds), growth factors inside complete media prices
# 2026-11-19 audit batch: the two reference rows do not move (Humbird's design keeps his 5 mmol/L and loses no runs). The
# scenarios: ammonia tolerance 4 mmol/L (more medium and membranes a kilo), membranes for lost runs, and glucose from the
# cells' balance (cautious: the published cells' lactate sets 95 L/kg, +$55.7 at every size)
# 2026-11-20 batch (lactate tolerance 35 mmol/L in the scenarios, bubble deaths, harvest loss, twice the fed-batch crew in perfusion,
# membrane life 2,415 L/m2, medium preparation capital, utilities in four parts): every row moves, and the designs chosen change
# (the all-favourable example: the column alone in a tall tank at 20 m3, no tricks from 50 m3)
# 2026-11-20 final pass: per-tank plant items (floor_physics.tank_items: the tank, its makeup tanks and filter housings and the
# buildings are charged per tank, so capital per m3 falls with size over much more than the 32% bioreactor share), thick
# cultures take up oxygen more slowly (viscous_kla: lower densities), and the all-favourable example redefined ($7.62 at its own
# 42 m3; membranes at $8 a m2, no lost runs). Every row moves; small tanks cost much more than before.
GOLDEN = {
    "reference": (36.1915, 22.6045, 18.1576, 15.9293, 15.5706, 18.2298, 22.2473),
    "reference_redesigned": (29.3934, 19.6309, 16.6125, 14.8918, 14.2780, 13.9989, 13.8121),
    "best": (13.2993, 9.5937, 8.5210, 8.0977, 7.5390, 7.7710, 7.5592),
    "central": (80.8891, 60.7612, 53.4965, 49.4977, 48.3364, 47.2675, 47.7524),
    "central_lean": (63.6921, 52.1810, 47.6678, 45.0374, 44.1287, 43.0371, 43.3629),
    "cautious": (242.6364, 207.0385, 193.3322, 185.5915, 179.8443, 177.1860, 178.0085),
}
NOTE = os.path.join(MODEL_DIR, "research_notes", "tank_size.md")

fails: list = []


def check(ok: bool, msg: str) -> None:
    if not ok:
        fails.append(msg)


def close(a, b, tol=1e-3):
    return abs(a - b) <= tol * max(1.0, abs(b))


scan = T.size_scan()
sizes = list(T.SIZES)

# 1. pinned costs, and the 20 m3 row is the scenario's own (design and cost)
for c, want in GOLDEN.items():
    for r, w in zip(scan[c], want):
        check(close(r["total"], w, 2e-5), f"{c} at {r['size']:g} m3: ${r['total']:.4f} != pinned ${w}")
i20 = sizes.index(20.0)
# 2026-11-20 final pass: the all-favourable example now chooses its own tank size among the published ones (42 m3,
# scenarios.all_favourable), so its 20 m3 row is its switches at 20 m3, and its own cost is the same design at its own size
for k in S.ORDER:
    r, ch = scan[k][i20], S.SCENARIOS[k].choice
    own = S.explore_kwargs(ch).get("vessel_m3", 20.0)
    check((r["tricks"], r["shape"]) == (ch["tricks"], ch["shape"]), f"{k}: the design chosen at 20 m3 is not scenarios.design's")
    check(close(r["total"], S.run(ch, vessel_m3=20.0)["total"], 1e-12), f"{k}: the 20 m3 cost is not the scenario's switches at 20 m3")
    check(close(T.evaluate(k, ch["tricks"], ch["shape"], own)["total"], S.run(ch)["total"], 1e-12), f"{k}: the cost at its own {own:g} m3 is not the scenario's own")
check(S.explore_kwargs(S.SCENARIOS["best"].choice).get("vessel_m3") == 42.0, "the all-favourable example's own tank is no longer 42 m3: rewrite the note")
check(close(scan["reference"][i20]["total"], S.reference()["total"], 1e-12), "the reference at 20 m3 is not explore()'s default")
for r in scan["reference"]:
    check(close(r["total"], fp.explore(vessel_m3=r["size"])["total"], 1e-9), f"reference at {r['size']:g} m3 is not explore(vessel_m3=)")

# 2. the cost split adds up; every chosen design passes the loop checks; the unchecked cost is never above the checked one
for c in T.CASES:
    for r in scan[c]:
        check(abs(sum(r["parts"].values()) - r["total"]) < 1e-9, f"{c} at {r['size']:g} m3: parts do not add to the total")
        check(all(x > -1e-9 for x in r["parts"].values()), f"{c} at {r['size']:g} m3: a negative part {r['parts']}")
        check(r["ok"], f"{c} at {r['size']:g} m3: the chosen design fails a loop check ({r['why']})")
        check(r["unchecked"] <= r["total"] + 1e-9, f"{c} at {r['size']:g} m3: the unchecked design is dearer")
        check(r["check_cost"] >= -1e-9, f"{c} at {r['size']:g} m3: negative cost of the checks")
        # the medium bought covers the liquid the bleed of cells carries out: in every case since 2026-11-16, when explore
        # gained that floor (before, the reference at 100 and 200 m3 bought less, and the note said it was low there)
        check(r["medium_l"] >= 1000.0 / r["density"] - 1e-9, f"{c} at {r['size']:g} m3: the bleed removes more liquid than the medium bought")

# 3. the retention loop is sized per m3 of tank, so its cost per kg does not depend on size: the same density and medium give
#    the same loop capital and membranes at different sizes (best: the same 258 g/L design with recycled oxygen at 20 and 50 m3;
#    cautious: the same 120 g/L design at 50 and 200 m3). Until 2026-11-16 the central case's 153 g/L column design at 50, 100
#    and 200 m3 was the example; on the current model its density differs between those sizes (189, 137, 138 g/L).
# 2026-11-19 restructure: the best case's 2 ng cells are oxygen-limited, and its density now moves a little with size (218 g/L at
# 20 m3, 218.0 at 50), so only the cautious case serves as the example
# 2026-11-20: costs are per kilo HARVESTED, and the share harvested rises with tank depth (bubble deaths follow the gas passed per
# litre of culture), so the loop's cost per kilo is no longer the same at two sizes of one density; the cautious case's density
# also differs now between 50 and 200 m3. What still holds, shown on the reference tank at 2 and 10 m3 (146 g/L at both): the
# membrane area per m3 of tank is the same, the loop's capital and its membranes move in one proportion (both are per kilo grown,
# divided by the same harvested share), and the deeper tank's loop costs a little less per kilo harvested.
for c, a, b in (("reference", 0, 2),):
    sc = scan[c]
    check(sc[a]["density"] == sc[b]["density"], f"{c}: the {sizes[a]:g} and {sizes[b]:g} m3 designs should hold one density")
    check(close(sc[a]["loop_area_m2_m3"], sc[b]["loop_area_m2_m3"], 1e-9), f"{c}: membrane area per m3 of tank differs with size")
    check(close(sc[a]["parts"]["loop"] / sc[a]["parts"]["membranes"], sc[b]["parts"]["loop"] / sc[b]["parts"]["membranes"], 1e-9),
          f"{c}: loop capital and membranes per kg should move in one proportion between {sizes[a]:g} and {sizes[b]:g} m3")
    check(sc[b]["parts"]["membranes"] < sc[a]["parts"]["membranes"], f"{c}: the deeper tank should lose fewer cells, so its membranes cost less per kg harvested")
cen = scan["central"]
check(close(cen[6]["loop_area_m2"] / cen[3]["loop_area_m2"], cen[6]["loop_area_m2_m3"] * 200.0 / (cen[3]["loop_area_m2_m3"] * 20.0), 1e-9),
      "membrane area is not area per m3 times tank size")

# 4. where the 20 m3 design stops passing: it passes just below the limit and fails just above, and the limit is above 20 m3
#    (between 20 and 30 m3 for the best and central designs; the cautious design, column + 1 bar in a tall tank, passes to 44 m3
#    since 2026-11-16, when it was 26 m3)
# 2026-11-20: best's design is now the column alone in the tall tank (passes to 35.6 m3); central_lean's is the same design at
# 133 g/L and passes to 62.9 m3 (it was the low-lactate example's column + 1 bar, 24.3 m3)
# 2026-11-20 final pass: every scenario's 20 m3 design is now column + 1 bar (best square, the others tall), and thick cultures
# take up oxygen more slowly (viscous_kla), so the cultures are thinner (low-lactate 154 g/L, was 191; cautious 103, was 120)
# and the column's alkaline dose at 20 m3 lower (0.82 and 0.64 of the safe dose). The limits rise: all-favourable 51.1 m3,
# both low-lactate examples 32.1 m3, cautious 168.8 m3.
LIMIT_RANGE = {"cautious": (160.0, 180.0), "best": (48.0, 54.0), "central": (30.0, 34.0), "central_lean": (30.0, 34.0)}
for k in S.ORDER:
    lim = T.design_limit(k)
    ch = S.SCENARIOS[k].choice
    lo, hi = LIMIT_RANGE[k]
    check(lo < lim < hi, f"{k}: the 20 m3 design should stop passing between {lo:g} and {hi:g} m3, not at {lim}")
    check(T.evaluate(k, ch["tricks"], ch["shape"], lim * 0.999)["ok"], f"{k}: the design fails just below its limit {lim:.2f}")
    check(not T.evaluate(k, ch["tricks"], ch["shape"], lim * 1.001)["ok"], f"{k}: the design passes just above its limit {lim:.2f}")
    check(T.design_limit(k, {"ph_max": "ph_relaxed"}) > lim, f"{k}: a looser pH check should raise the limit")

# 5. the answer: 20 m3 is near the flat bottom of the curve, and no scenario gains more than 3% from another size.
#    2026-11-19 audit batch: the cautious case was the exception (5.4% at 111 m3, pinned between 4% and 5.5%). Its saving is
#    still $1.94 a kilo at 111 m3 (its oxygen-limited 120 g/L culture holds at every size), but glucose from the cells' balance
#    raised its cost from $36.42 to $92.17 through medium and membranes, which do not depend on size, so the saving is now 2.1%
#    and 20 m3 is within 3% of its minimum like the others. The exception is gone; the note says so.
# 2026-11-20 batch: THE ANSWER CHANGED. Three scenarios now gain more than 3% from a larger tank (best 5.1% at 121 m3, the
# low-lactate example 4.6% at 61 m3, with shared medium 5.0% at 61 m3), and for them 20 m3 is just outside the sizes within 3% of
# the minimum (29 to 34 m3 and up). The batch rewards a thinner culture in a deeper tank: bubble deaths follow the gas passed per
# litre, membranes are replaced after 2,415 L/m2, and the perfusion crew is doubled per m3. No scenario gains more than 5.5%, and
# the cautious case (2.3%) is still inside 3%. The note's section 1 says so.
# 2026-11-20 final pass: THE ANSWER CHANGED AGAIN. Every scenario now gains more than 3% from a larger tank (all-favourable 7.4%
# at 90 m3, low-lactate 6.2% and with shared medium 5.8% at 168 m3, cautious 5.3% at 168 m3), and 20 m3 is outside the sizes
# within 3% of the minimum for all four (they run from 32 to 63 m3 up to 200 m3). The cause is floor_physics.tank_items: the
# makeup tanks, filter housings and buildings are now charged per tank as well as per m3, so capital per m3 falls with size
# over much more of the plant than the bioreactor share (the cautious capital is $23.37 a kilo at 20 m3, $17.49 at 168 m3).
# A correct consequence of pricing the plant by its items (Humbird's own accounting), not a defect.
opt = {k: T.optimum(k) for k in S.ORDER}
for k in S.ORDER:
    o = opt[k]
    check(o["saving"] >= -1e-12, f"{k}: the optimum is dearer than 20 m3")
    check(not o["at_edge"], f"{k}: the optimum sits at the end of the search range")
    check(5.0 < o["saving_pct"] < 8.0, f"{k}: another size saves {o['saving_pct']:.1f}%, outside the 5% to 8% the note says")
    check(not (o["within_3pct"][0] <= 20.0 <= o["within_3pct"][1]), f"{k}: 20 m3 is within 3% of the minimum: rewrite section 1 of the note")
    check(30.0 < o["within_3pct"][0] < 65.0 and o["within_3pct"][1] >= 199.0, f"{k}: the sizes within 3% of the minimum should run from 30 to 65 m3 up to 200 m3")
ob, oc, oq = opt["best"], opt["central"], opt["cautious"]
check(160.0 < oq["size"] < 175.0 and 5.0 < oq["saving_pct"] < 5.6 and 9.5 < oq["saving"] < 10.2,
      f"cautious: optimum {oq['size']:.1f} m3, {oq['saving_pct']:.2f}%, ${oq['saving']:.2f}")
check(85.0 < ob["size"] < 95.0 and 7.0 < ob["saving_pct"] < 7.8, f"best: optimum {ob['size']:.1f} m3, {ob['saving_pct']:.2f}%")
check(160.0 < oc["size"] < 175.0 and 5.9 < oc["saving_pct"] < 6.6, f"central: optimum {oc['size']:.1f} m3, {oc['saving_pct']:.2f}%")
# Until 2026-11-20 the all-favourable example's optimum was a thin culture with no tricks (59 g/L at 121 m3) whose harvest carried
# out its own spent medium, saving membranes at $1,450 a m2. The example now uses membranes at $8 a m2 ($0.04 a kilo at every
# size), so a thin culture saves nothing and the optimum keeps the 20 m3 design's column + 1 bar and its density (156 g/L).
check(ob["tricks"] == "pressure" and 145.0 < ob["density"] < 165.0, f"best: the optimum should keep column + 1 bar and about 156 g/L ({ob['tricks']}, {ob['density']:.0f} g/L)")
# without the loop checks the all-favourable example keeps falling to the end of the range (the checks, not the density limits, stop it)
ub = T.optimum("best", {"checks": False})
check(ub["at_edge"] and ub["size"] >= 199.0, f"best without checks: optimum {ub['size']:.0f} m3 should be the 200 m3 end of the range")
check(ub["saving_pct"] > ob["saving_pct"], "best: removing the checks should save more")

# 5b. a flatter tank than the scenarios offer: the 0.5 row is the scenario's own flat design, and for the central case at 100 m3
#     a shape at 0.4 passes the checks with column + 1 bar at about the 20 m3 cost (until 2026-11-16: 50 m3, 0.3, oxygen trick;
#     on the current model the flat 0.5 tank is already the cheapest shape at 50 m3)
fl = dict(T.flatter("central", 100.0))
check(close(fl[0.5]["total"], T.evaluate("central", fl[0.5]["tricks"], "flat", 100.0)["total"], 1e-12), "flatter(): the 0.5 row is not the flat design")
# 2026-11-20: within 1.5% of the 20 m3 price ($50.43 against $49.96), and no longer the way to make 100 m3 pay: the scan's own
# 100 m3 design (the column alone, a thinner culture) is cheaper than every flatter shape and than 20 m3
# 2026-11-20 final pass: a shallow tank passes more gas per litre of culture at the same surface speed, so it loses more cells to
# bursting bubbles (at 20 m3 the flat 0.5 tank of the low-lactate example kills 17% of its cells against 8% in the tall tank) and
# every flatter shape now costs more than the 20 m3 price: at 100 m3 aspect 0.4 costs $51.39 against $49.50 (3.8% more)
check(fl[0.4]["ok"] and all(x["total"] > scan["central"][i20]["total"] for x in fl.values()),
      "central at 100 m3: every flatter shape should pass and cost more than the 20 m3 price")
check(scan["central"][sizes.index(100.0)]["total"] < min(x["total"] for x in fl.values()) and scan["central"][sizes.index(100.0)]["total"] < scan["central"][i20]["total"],
      "central at 100 m3: the scan's own design should now be cheaper than every flatter shape and than 20 m3")

# 6. every what-if adjustment is the identity at 20 m3, so the sizes differ only through the size effect
base20 = T.evaluate("central", "oxygen", "flat", 20.0)["total"]
for label, ch in T.WHAT_IFS:
    if ch.get("checks") is False:
        continue
    check(close(T.evaluate("central", "oxygen", "flat", 20.0, ch)["total"], base20, 1e-12), f"what-if '{label}' changes the 20 m3 cost")

# 7. the directions of the what-ifs
WI = dict(T.WHAT_IFS)
crew = T.optimum("best", WI["labour follows Humbird's crew rule"])
haz = T.optimum("best", WI["chance of losing a run grows with tank size"])
relax = T.optimum("best", WI["pH check relaxed to twice the safe dose"])
# 2026-11-20: the all-favourable example's optimum sits at the size where its filter duty reaches zero (121 m3, no tricks), a kink in
# the cost curve, so the crew rule does not move the size; it lowers the cost there and raises the saving against 20 m3 (5% -> 23%)
# 2026-11-20 final pass: the crew rule moves the all-favourable optimum to the 200 m3 end of the range (18.2%). The low-lactate
# example's optimum (168 m3) is the largest size at which its column-alone tall design passes the pH check; above it the design
# changes to a square tank at 118 g/L and the cost steps up by $1.59, so the crew rule cannot move the size and only deepens the
# saving (6.2% -> 12.0%). The all-favourable example loses no runs (hazard 0), so a hazard that grows with size changes nothing
# for it; the check uses the low-lactate example (168 m3 -> 32 m3).
check(crew["size"] > ob["size"] and crew["total"] < ob["total"] and crew["saving_pct"] > ob["saving_pct"],
      "crew rule should favour a larger tank for the all-favourable example")
crew_c = T.optimum("central", WI["labour follows Humbird's crew rule"])
check(crew_c["size"] >= oc["size"] and crew_c["saving_pct"] > oc["saving_pct"], "crew rule should not move the low-lactate example to a smaller tank, and should save more")
check(close(haz["total"], ob["total"], 1e-12), "the all-favourable example loses no runs, so the hazard what-if should change nothing")
check(T.optimum("central", WI["chance of losing a run grows with tank size"])["size"] < oc["size"], "a hazard that grows with size should favour a smaller tank")
# 2026-11-19 restructure: with the 2 ng cells the looser check also lowers the 20 m3 cost, so compare the costs, not the % saved
# 2026-11-20: the all-favourable example's optimum uses no column, so the pH check does not bind there and relaxing it changes nothing;
# the low-lactate example's optimum does use one, and a looser check reaches a lower cost
# 2026-11-20 final pass: both optima now use the column; the looser check lowers the 20 m3 cost too, so the % saved can fall
# (all-favourable 7.4% -> 5.5%) while the cost reached is lower; the checks below still compare costs
check(relax["total"] <= ob["total"] + 1e-12, "a looser pH check should not raise the all-favourable example's cost")
check(T.optimum("central", WI["pH check relaxed to twice the safe dose"])["total"] < oc["total"], "a looser pH check should reach a lower cost for the low-lactate example")

# 8. the note quotes the model: the 20 m3 and the cheapest costs, the sizes, the limits
if not os.path.exists(NOTE):
    check(False, "research_notes/tank_size.md is missing")
else:
    text = open(NOTE, encoding="utf-8").read()
    for k in S.ORDER:
        o = opt[k]
        for want in (f"${scan[k][i20]['total']:.2f}", f"${o['total']:.2f}", f"{T.design_limit(k):.1f} m\u00b3"):
            check(want in text, f"the note does not quote {want} ({k})")

# 9. fed-batch against size (2026-11-19 restructure): a bigger batch is cheaper, never cheaper than perfusion at 20 m3, and the
# note carries the table
# 2026-11-20 batch: with the all-favourable example's switches a fed-batch of 50 m3 or more is now CHEAPER than perfusion at 20 m3
# ($17.75 at 100 m3 against $18.71): perfusion pays twice the crew and membranes replaced after 2,415 L/m2. With the low-lactate
# example's switches no size closes the gap, as before.
# 2026-11-20 final pass: the all-favourable example now uses membranes at $8 a m2, so perfusion no longer pays for membranes and
# fed-batch at every size costs more than perfusion again ($10.22 at 200 m3 against $7.62): the reversal of the batch is undone.
FB_GOLDEN = {"central": (71.7592, 60.7101), "best": (11.2827, 10.4370)}     # $/kg at 20 and 100 m3
for k, (a, b) in FB_GOLDEN.items():
    c20, c100 = T.fedbatch_at(k, 20.0)["total"], T.fedbatch_at(k, 100.0)["total"]
    check(abs(c20 - a) < 1e-3 * a and abs(c100 - b) < 1e-3 * b, f"{k} fed-batch: {c20:.4f}, {c100:.4f} != pinned {a}, {b}")
    check(c100 < c20 and T.fedbatch_at(k, 200.0)["total"] > S.run(S.SCENARIOS[k].choice)["total"], f"{k}: fed-batch against size")
    check(c20 > S.run(S.SCENARIOS[k].choice)["total"], f"{k}: fed-batch at 20 m3 should cost more than perfusion at 20 m3")
check(abs(T.fedbatch_at("central", 20.0)["total"] - S.run(S.SCENARIOS["selected"].choice)["total"]) < 1e-9,
      "the low-lactate example's switches in fed-batch at 20 m3 should be rung 3")
if os.path.exists(NOTE):
    text = open(NOTE, encoding="utf-8").read()
    for ln in T.fedbatch_markdown().splitlines():
        check(ln in text, f"the note does not carry the fed-batch size table line: {ln[:70]}")


def test_tank_size():
    assert not fails, fails


if __name__ == "__main__":
    for f in fails:
        print("FAIL:", f)
    print("PASS — the tank-size scan holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
