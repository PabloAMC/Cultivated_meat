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
GOLDEN_REF = {
    ("stirred", "batch"): 65.3527, ("stirred", "fedbatch"): 18.8538, ("stirred", "filldraw"): 18.4583,
    ("stirred", "chemostat"): 34.7532, ("stirred", "perfusion"): 12.5107,
    ("airlift", "fedbatch"): 20.7859, ("airlift", "perfusion"): 14.7790,
    ("packed", "filldraw"): None, ("hollow", "chemostat"): None,
}
GOLDEN_CENTRAL = {("stirred", "perfusion"): 29.4162, ("stirred", "fedbatch"): 42.8732, ("airlift", "perfusion"): 30.8821}


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
    want = value("pf_working_volume") * r["density"] / (value("pf_fedbatch_doublings") * 24.0 + value("pf_turnaround_h")) * 8760 / 1000
    if not close(r["output"], want, 1e-9):
        fails.append(f"fed-batch output {r['output']:.4f} != {want:.4f}")
    # 3. a chemostat at the full growth rate is fill-and-draw with the culture held at its cap (shape 1)
    kw = V.explore_kwargs("stirred", "chemostat", {})
    kw["vm"] = {**kw["vm"], "dil_frac": 1.0}
    a = fp.explore(**kw)
    b = fp.explore(mode="filldraw")
    f = value("pf_draw_fraction")
    if not close(a["output"] * f / math.log(1.0 / (1.0 - f)), b["output"], 1e-9):
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
