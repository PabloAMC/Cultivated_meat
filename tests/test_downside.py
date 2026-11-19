#!/usr/bin/env python3
"""test_downside.py — what each scenario costs if perfusion cannot be run at 20 m3 (downside.py)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import downside as D
import scenarios as S
import vessels as V
from inputs import value

# $/kg, fed-batch and fill-and-draw, at the model's own density cap and at the density shown for meat cells
# repinned 2026-11-19: best's medium is now the nutrient floor ($2.00 a kilo whatever the litres, against $0.15 a litre before);
# the other scenarios' growth factors are inside their complete-medium price, which cannot cost less than the nutrients plus those
# growth factors (it binds at the model cap's 16 L/kg, not at 27 g/L's 37 L/kg)
GOLDEN = {
    "best": {("fedbatch", "model"): 14.1793, ("fedbatch", "shown"): 39.1678, ("filldraw", "model"): 14.2754},
    "central": {("fedbatch", "model"): 40.1594, ("fedbatch", "shown"): 88.2078, ("filldraw", "model"): 43.3466},
    "central_lean": {("fedbatch", "model"): 27.9892, ("filldraw", "model"): 29.9716},
    "cautious": {("fedbatch", "model"): 57.3257, ("filldraw", "shown"): 121.6584},
}


def close(a, b, tol=1e-3):
    return abs(a - b) <= tol * max(1.0, abs(b))


def check() -> list:
    fails = []
    for k in S.ORDER:
        c = D.costs(k)
        base = S.explore_kwargs(S.SCENARIOS[k].choice)
        if not close(c["perfusion"], S.run(S.SCENARIOS[k].choice)["total"], 1e-12):
            fails.append(f"{k}: the perfusion cost is not the scenario's own")
        for m in D.MODES:
            # the design chosen again is never dearer than the one chosen for perfusion (vessels.cell holds it fixed)
            if c[(m, "model")]["cost"] > V.cell("stirred", m, base)["cost"] + 1e-9:
                fails.append(f"{k} {m}: re-chosen design dearer than the perfusion design")
            # a thinner culture is dearer, and its density is the one shown for meat cells
            if not c[(m, "shown")]["cost"] > c[(m, "model")]["cost"]:
                fails.append(f"{k} {m}: the 27 g/L cost should exceed the model-cap cost")
            if not close(c[(m, "shown")]["density"], value("vm_x_meat_shown"), 1e-9):
                fails.append(f"{k} {m}: density at the cap should be {value('vm_x_meat_shown')}")
            # no perfusion is dearer than perfusion in every scenario
            if not c[(m, "model")]["cost"] > c["perfusion"]:
                fails.append(f"{k} {m}: the fallback should cost more than perfusion")
            if not c[(m, "shown")]["share"] <= c[(m, "model")]["share"] <= c["perfusion_share"] + 1e-9:
                fails.append(f"{k} {m}: shares out of order")
        for key, want in GOLDEN.get(k, {}).items():
            if not close(c[key]["cost"], want, 1e-4):
                fails.append(f"{k} {key}: {c[key]['cost']:.4f} != pinned {want}")
    return fails


def test_downside():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the no-perfusion downside holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
