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
GOLDEN = {
    "reference": (20.5430, 14.8609, 12.9669, 12.8122, 13.5329, 15.8790, 19.3675),
    "reference_redesigned": (16.2225, 12.8053, 11.6782, 11.0259, 10.9678, 11.5972, 11.4955),
    "best": (14.3341, 12.3876, 11.7533, 11.4569, 11.3433, 11.4594, 11.6028),
    "central": (43.7184, 36.5912, 34.2748, 32.8028, 32.7546, 33.7123, 33.8613),
    "central_lean": (35.8885, 31.9539, 30.7940, 29.9417, 29.8530, 30.2197, 30.2894),
    "cautious": (117.7848, 101.0026, 95.2051, 92.1653, 91.1604, 90.3250, 91.8886),
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
for k in S.ORDER:
    r, ch = scan[k][i20], S.SCENARIOS[k].choice
    check((r["tricks"], r["shape"]) == (ch["tricks"], ch["shape"]), f"{k}: the design chosen at 20 m3 is not scenarios.design's")
    check(close(r["total"], S.run(ch)["total"], 1e-12), f"{k}: the 20 m3 cost is not the scenario's own")
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
for c, a, b in (("best", 3, 4), ("cautious", 4, 6)):
    sc = scan[c]
    check(sc[a]["density"] == sc[b]["density"], f"{c}: the {sizes[a]:g} and {sizes[b]:g} m3 designs should hold one density")
    check(close(sc[a]["parts"]["loop"], sc[b]["parts"]["loop"], 1e-9) and close(sc[a]["parts"]["membranes"], sc[b]["parts"]["membranes"], 1e-9),
          f"{c}: loop cost per kg differs between {sizes[a]:g} and {sizes[b]:g} m3")
    check(close(sc[a]["loop_area_m2_m3"], sc[b]["loop_area_m2_m3"], 1e-9), f"{c}: membrane area per m3 of tank differs with size")
cen = scan["central"]
check(close(cen[6]["loop_area_m2"] / cen[3]["loop_area_m2"], cen[6]["loop_area_m2_m3"] * 200.0 / (cen[3]["loop_area_m2_m3"] * 20.0), 1e-9),
      "membrane area is not area per m3 times tank size")

# 4. where the 20 m3 design stops passing: it passes just below the limit and fails just above, and the limit is above 20 m3
#    (between 20 and 30 m3 for the best and central designs; the cautious design, column + 1 bar in a tall tank, passes to 44 m3
#    since 2026-11-16, when it was 26 m3)
LIMIT_RANGE = {"cautious": (40.0, 50.0)}
for k in S.ORDER:
    lim = T.design_limit(k)
    ch = S.SCENARIOS[k].choice
    lo, hi = LIMIT_RANGE.get(k, (20.0, 30.0))
    check(lo < lim < hi, f"{k}: the 20 m3 design should stop passing between {lo:g} and {hi:g} m3, not at {lim}")
    check(T.evaluate(k, ch["tricks"], ch["shape"], lim * 0.999)["ok"], f"{k}: the design fails just below its limit {lim:.2f}")
    check(not T.evaluate(k, ch["tricks"], ch["shape"], lim * 1.001)["ok"], f"{k}: the design passes just above its limit {lim:.2f}")
    check(T.design_limit(k, {"ph_max": "ph_relaxed"}) > lim, f"{k}: a looser pH check should raise the limit")

# 5. the answer: 20 m3 is near the flat bottom of the curve, and no scenario gains more than 3% from another size.
#    2026-11-19 audit batch: the cautious case was the exception (5.4% at 111 m3, pinned between 4% and 5.5%). Its saving is
#    still $1.94 a kilo at 111 m3 (its oxygen-limited 120 g/L culture holds at every size), but glucose from the cells' balance
#    raised its cost from $36.42 to $92.17 through medium and membranes, which do not depend on size, so the saving is now 2.1%
#    and 20 m3 is within 3% of its minimum like the others. The exception is gone; the note says so.
opt = {k: T.optimum(k) for k in S.ORDER}
for k in S.ORDER:
    o = opt[k]
    check(o["saving"] >= -1e-12, f"{k}: the optimum is dearer than 20 m3")
    check(not o["at_edge"], f"{k}: the optimum sits at the end of the search range")
    check(o["saving_pct"] < 3.0, f"{k}: another size saves {o['saving_pct']:.1f}%, more than the 3% the note says")
    check(o["within_3pct"][0] <= 20.0 <= o["within_3pct"][1], f"{k}: 20 m3 is not within 3% of the minimum")
ob, oc, oq = opt["best"], opt["central"], opt["cautious"]
check(90.0 < oq["size"] < 130.0 and 1.8 < oq["saving_pct"] < 2.4 and 1.8 < oq["saving"] < 2.1,
      f"cautious: optimum {oq['size']:.1f} m3, {oq['saving_pct']:.2f}%, ${oq['saving']:.2f}")
check(60.0 < ob["size"] < 85.0 and 1.0 < ob["saving_pct"] < 2.0, f"best: optimum {ob['size']:.1f} m3, {ob['saving_pct']:.2f}%")
check(35.0 < oc["size"] < 55.0 and 1.0 < oc["saving_pct"] < 2.5, f"central: optimum {oc['size']:.1f} m3, {oc['saving_pct']:.2f}%")
# without the loop checks the Engineered cells, all favourable case keeps falling to the end of the range (the checks, not the density limits, stop it)
ub = T.optimum("best", {"checks": False})
check(ub["at_edge"] and ub["size"] >= 199.0, f"best without checks: optimum {ub['size']:.0f} m3 should be the 200 m3 end of the range")
check(ub["saving_pct"] > ob["saving_pct"], "best: removing the checks should save more")

# 5b. a flatter tank than the scenarios offer: the 0.5 row is the scenario's own flat design, and for the central case at 100 m3
#     a shape at 0.4 passes the checks with column + 1 bar at about the 20 m3 cost (until 2026-11-16: 50 m3, 0.3, oxygen trick;
#     on the current model the flat 0.5 tank is already the cheapest shape at 50 m3)
fl = dict(T.flatter("central", 100.0))
check(close(fl[0.5]["total"], T.evaluate("central", fl[0.5]["tricks"], "flat", 100.0)["total"], 1e-12), "flatter(): the 0.5 row is not the flat design")
check(fl[0.4]["ok"] and abs(fl[0.4]["total"] - scan["central"][i20]["total"]) < 0.2, "central at 100 m3 and aspect 0.4 should cost about the 20 m3 price")

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
check(crew["size"] > ob["size"], "crew rule should favour a larger tank for the Engineered cells, all favourable case")
check(haz["size"] < ob["size"], "a hazard that grows with size should favour a smaller tank")
check(relax["saving_pct"] > ob["saving_pct"], "a looser pH check should save more")

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
FB_GOLDEN = {"central": (64.8950, 58.0934), "best": (15.6371, 14.5032)}     # $/kg at 20 and 100 m3
for k, (a, b) in FB_GOLDEN.items():
    c20, c100 = T.fedbatch_at(k, 20.0)["total"], T.fedbatch_at(k, 100.0)["total"]
    check(abs(c20 - a) < 1e-3 * a and abs(c100 - b) < 1e-3 * b, f"{k} fed-batch: {c20:.4f}, {c100:.4f} != pinned {a}, {b}")
    check(c100 < c20 and T.fedbatch_at(k, 200.0)["total"] > S.run(S.SCENARIOS[k].choice)["total"], f"{k}: fed-batch against size")
check(abs(T.fedbatch_at("central", 20.0)["total"] - S.run(S.SCENARIOS["selected"].choice)["total"]) < 1e-9,
      "Selected cells' switches in fed-batch at 20 m3 should be rung 3")
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
