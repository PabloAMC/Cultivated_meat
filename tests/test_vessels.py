#!/usr/bin/env python3
"""test_vessels.py — vessel types against operating modes (vessels.py).

Checks that the grid is anchored to the rest of the model (the stirred tank in perfusion IS the reference case and the
scenario's own number; fill-and-draw IS the old 'drained and refilled'), that the new modes reduce to known formulas,
that impossible combinations are marked, and pins the grid so a change shows. Run directly or under pytest.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import floor_physics as fp
import scenarios as S
import vessels as V
from inputs import value

# the reference-case grid, $/kg (None = not possible). Update in the same commit as an intended change.
# repinned 2026-11-19: nutrient floor $2.00 (+$0.30 where it binds, less where medium at $0.15 a litre partly covers it; batch and
# chemostat buy more than the floor and do not move); central: growth factors inside the $0.20 complete medium, which cannot
# cost less than the nutrients plus those growth factors (fed-batch, at 16 L/kg, pays that floor)
GOLDEN_REF = {
    ("stirred", "batch"): 65.3527, ("stirred", "fedbatch"): 19.1562, ("stirred", "filldraw"): 18.7618,   # 2026-11-19: slowdown
    ("stirred", "chemostat"): 34.7532, ("stirred", "perfusion"): 12.8122,
    ("airlift", "fedbatch"): 20.8887, ("airlift", "perfusion"): 15.1712,
    ("packed", "filldraw"): None, ("hollow", "chemostat"): None,
}
# 2026-11-19 audit batch: the reference grid does not move (Humbird's design keeps his 5 mmol/L and loses no runs). Selected cells:
# ammonia tolerance 4 mmol/L (35 L/kg in perfusion, was 28; fed-batch stops at 56 g/L, was 62) and lost runs pay for their membranes
# 2026-11-19 restructure: an unwashed tank is held by the waste mass balance (1.3 times the 4 mmol/L perfusion is held to), so
# Selected cells' fed-batch stops at 37 g/L, not 56 ($45.81 -> $67.42); the reference grid does not move (other by-products hold it at 92)
GOLDEN_CENTRAL = {("stirred", "perfusion"): 32.8028, ("stirred", "fedbatch"): 67.4193, ("airlift", "perfusion"): 34.1429}


def close(a, b, tol=1e-3):
    return abs(a - b) <= tol * max(1.0, abs(b))


def check() -> list:
    fails = []
    ref, cen = V.settings()["reference"], V.settings()["central"]
    gr, gc = V.grid(ref), V.grid(cen)
    # 1. anchors
    if not close(gr[("stirred", "perfusion")]["cost"], fp.explore()["total"], 1e-12):
        fails.append("stirred perfusion is not the reference case")
    if not close(gr[("stirred", "filldraw")]["cost"], fp.explore(mode="filldraw")["total"], 1e-12):
        fails.append("stirred fill-and-draw is not explore(mode='filldraw')")
    if not close(gc[("stirred", "perfusion")]["cost"], S.run(S.SCENARIOS["central"].choice)["total"], 1e-12):
        fails.append("stirred perfusion is not the central scenario's cost")
    # 2. fed-batch with no losses reproduces Humbird's fed-batch output: working volume x density / (2 doublings + 10 h)
    r = fp.explore(**V.explore_kwargs("stirred", "fedbatch", {}))
    # 2026-11-19 restructure: the two doublings take longer when the batch ends above the steady-state waste level (here 1.03 times
    # it, lactate: other by-products hold the density at 92 g/L), as floor_physics.batch_slowdown charges
    slow = fp.batch_slowdown(r["density"] * max(r["nh3_kg"] / value("pf_nh3_limit"), r["lac_kg"] / value("pf_lac_limit")),
                             value("pf_fedbatch_doublings"))
    want = value("pf_working_volume") * r["density"] / (value("pf_fedbatch_doublings") * 24.0 * slow + value("pf_turnaround_h")) * 8760 / 1000
    if not close(r["output"], want, 1e-9):
        fails.append(f"fed-batch output {r['output']:.4f} != {want:.4f}")
    # 3. a chemostat at the full growth rate is fill-and-draw with the culture held at its cap (shape 1)
    kw = V.explore_kwargs("stirred", "chemostat", {})
    kw["vm"] = {**kw["vm"], "dil_frac": 1.0}
    a = fp.explore(**kw)
    b = fp.explore(mode="filldraw")
    f = value("pf_draw_fraction")
    # 2026-11-19 restructure: fill-and-draw's climb back to its cap is slowed where it ends above the steady-state waste level; a
    # chemostat sits at its level (no slowdown), so compare them with that slowdown taken out
    slow = fp.batch_slowdown(b["density"] * max(b["nh3_kg"] / value("pf_nh3_limit"), b["lac_kg"] / value("pf_lac_limit")),
                             math.log2(1.0 / (1.0 - f)))
    # and per gram of density: a chemostat is held to the steady-state level itself (end factor 1), so it may stop thinner
    if not close(a["output"] / a["density"] * f / math.log(1.0 / (1.0 - f)), b["output"] / b["density"] * slow, 1e-9) \
            or a["density"] > b["density"] + 1e-9:
        fails.append("chemostat at the full growth rate is not fill-and-draw at shape 1")
    # 4. not possible, and same as
    for k in V.NOT_POSSIBLE:
        if gr[k]["possible"]:
            fails.append(f"{k} should be not possible")
    for k, (other, _t) in V.SAME_AS.items():
        if not close(gr[k]["cost"], gr[(k[0], other)]["cost"], 1e-12):
            fails.append(f"{k} should equal {other}")
    # 5. what the physics should give
    if not gr[("stirred", "perfusion")]["cost"] < gr[("stirred", "filldraw")]["cost"] < gr[("stirred", "chemostat")]["cost"] \
            < gr[("stirred", "batch")]["cost"]:
        fails.append("stirred tank: expected perfusion < fill-and-draw < chemostat < batch")
    if not gr[("airlift", "perfusion")]["limit"] == "CO2 removal" or not gr[("airlift", "perfusion")]["density"] < gr[("stirred", "perfusion")]["density"]:
        fails.append("the taller airlift should clear less CO2 than the stirred tank")
    if not V.what_if_bed(ref)["total"] > gr[("stirred", "perfusion")]["cost"]:
        fails.append("even the best-case packed bed should cost more than a stirred tank in perfusion")
    if gc[("airlift", "perfusion")]["tricks_fallback"] in (None, ""):
        fails.append("central airlift perfusion: the loop should fail its check in the taller tank and fall back to a lesser trick")
    # 6. every combination has a maturity tag and evidence
    for k in [(v, m) for v in V.VESSEL_ORDER for m in V.MODE_ORDER]:
        if k not in V.TAGS:
            fails.append(f"no maturity tag for {k}")
        elif k not in V.NOT_POSSIBLE and not V.TAGS[k][1]:
            fails.append(f"no evidence for {k}")
    # 7. golden values
    for name, g, gold in (("reference", gr, GOLDEN_REF), ("central", gc, GOLDEN_CENTRAL)):
        for k, want in gold.items():
            c = g[k]
            if want is None:
                if c["possible"]:
                    fails.append(f"{name} {k}: should be not possible")
            elif not c["possible"] or not close(c["cost"], want, 1e-5):
                fails.append(f"{name} {k}: {c.get('cost')} != golden {want}")
    return fails


def test_vessels():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — vessel types against operating modes hold." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
