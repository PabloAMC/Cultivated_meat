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
GOLDEN = {
    "reference": (16.5241, 12.3669, 11.8349, 11.8411, 12.5528, 14.5885, 17.2992),
    "reference_redesigned": (14.2759, 11.2823, 10.3334, 9.8486, 9.6869, 10.2618, 10.1993),
    "best": (11.5503, 9.7566, 9.2665, 8.9488, 8.8308, 9.0653, 9.0256),
    "central": (34.7805, 29.1814, 27.3486, 26.6381, 28.3480, 28.3356, 28.8015),
    "central_lean": (29.1715, 25.8866, 24.7893, 24.3374, 25.1053, 25.0743, 25.3163),
    "cautious": (58.4279, 45.1962, 40.6883, 38.9681, 38.8011, 38.3342, 41.2425),
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
        if c in S.ORDER:     # the medium bought covers the liquid the bleed of cells carries out (the note says so)
            check(r["medium_l"] >= 1000.0 / r["density"] - 1e-9, f"{c} at {r['size']:g} m3: the bleed removes more liquid than the medium bought")
# ... and in the reference as defined it does not, at 100 and 200 m3 (the note says the reference is low there)
check(scan["reference"][5]["medium_l"] < 1000.0 / scan["reference"][5]["density"], "reference at 100 m3: the bleed should remove more than the medium bought")

# 3. the retention loop is sized per m3 of tank, so its cost per kg does not depend on size: the same density and medium give
#    the same loop capital and membranes at 50, 100 and 200 m3 (central: the same 153 g/L column design at all three)
cen = scan["central"]
check(cen[4]["density"] == cen[5]["density"] == cen[6]["density"], "central: the 50, 100 and 200 m3 designs should hold one density")
for a, b in ((4, 5), (5, 6)):
    check(close(cen[a]["parts"]["loop"], cen[b]["parts"]["loop"], 1e-9) and close(cen[a]["parts"]["membranes"], cen[b]["parts"]["membranes"], 1e-9),
          f"central: loop cost per kg differs between {sizes[a]:g} and {sizes[b]:g} m3")
    check(close(cen[a]["loop_area_m2_m3"], cen[b]["loop_area_m2_m3"], 1e-9), "central: membrane area per m3 of tank differs with size")
check(close(cen[6]["loop_area_m2"] / cen[3]["loop_area_m2"], cen[6]["loop_area_m2_m3"] * 200.0 / (cen[3]["loop_area_m2_m3"] * 20.0), 1e-9),
      "membrane area is not area per m3 times tank size")

# 4. where the 20 m3 design stops passing: it passes just below the limit and fails just above, and the limit is above 20 m3
for k in S.ORDER:
    lim = T.design_limit(k)
    ch = S.SCENARIOS[k].choice
    check(20.0 < lim < 30.0, f"{k}: the 20 m3 design should stop passing between 20 and 30 m3, not at {lim}")
    check(T.evaluate(k, ch["tricks"], ch["shape"], lim * 0.999)["ok"], f"{k}: the design fails just below its limit {lim:.2f}")
    check(not T.evaluate(k, ch["tricks"], ch["shape"], lim * 1.001)["ok"], f"{k}: the design passes just above its limit {lim:.2f}")
    check(T.design_limit(k, {"ph_max": "ph_relaxed"}) > lim, f"{k}: a looser pH check should raise the limit")

# 5. the answer: 20 m3 is near the flat bottom of the curve for every scenario, and no scenario gains more than 3% from another size
opt = {k: T.optimum(k) for k in S.ORDER}
for k in S.ORDER:
    o = opt[k]
    check(o["saving"] >= -1e-12, f"{k}: the optimum is dearer than 20 m3")
    check(o["saving_pct"] < 3.0, f"{k}: another size saves {o['saving_pct']:.1f}%, more than the 3% the note says")
    check(not o["at_edge"], f"{k}: the optimum sits at the end of the search range")
    check(o["within_3pct"][0] <= 20.0 <= o["within_3pct"][1], f"{k}: 20 m3 is not within 3% of the minimum")
ob, oc = opt["best"], opt["central"]
check(40.0 < ob["size"] < 70.0 and 1.0 < ob["saving_pct"] < 2.0, f"best: optimum {ob['size']:.1f} m3, {ob['saving_pct']:.2f}%")
check(20.0 <= oc["size"] < 26.0 and oc["saving_pct"] < 1.0, f"central: optimum {oc['size']:.1f} m3, {oc['saving_pct']:.2f}%")
# without the loop checks the best case keeps falling to the end of the range (the checks, not the density limits, stop it)
ub = T.optimum("best", {"checks": False})
check(ub["at_edge"] and ub["size"] >= 199.0, f"best without checks: optimum {ub['size']:.0f} m3 should be the 200 m3 end of the range")
check(ub["saving_pct"] > ob["saving_pct"], "best: removing the checks should save more")

# 5b. a flatter tank than the scenarios offer: the 0.5 row is the scenario's own flat design, and for the central case at 50 m3
#     a shape at 0.3 passes the checks with the oxygen trick at about the 20 m3 cost
fl = dict(T.flatter("central", 50.0))
check(close(fl[0.5]["total"], T.evaluate("central", fl[0.5]["tricks"], "flat", 50.0)["total"], 1e-12), "flatter(): the 0.5 row is not the flat design")
check(fl[0.3]["ok"] and abs(fl[0.3]["total"] - scan["central"][i20]["total"]) < 0.2, "central at 50 m3 and aspect 0.3 should cost about the 20 m3 price")

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
check(crew["size"] > ob["size"], "crew rule should favour a larger tank for the best case")
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


def test_tank_size():
    assert not fails, fails


if __name__ == "__main__":
    for f in fails:
        print("FAIL:", f)
    print("PASS — the tank-size scan holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
