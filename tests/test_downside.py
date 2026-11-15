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
GOLDEN = {
    "best": {("fedbatch", "model"): 13.2241, ("fedbatch", "shown"): 40.5495, ("filldraw", "model"): 13.3220},
    "central": {("fedbatch", "model"): 40.3857, ("fedbatch", "shown"): 89.9362, ("filldraw", "model"): 43.5795},
    "central_lean": {("fedbatch", "model"): 28.2155, ("filldraw", "model"): 30.2045},
    "cautious": {("fedbatch", "model"): 59.9254, ("filldraw", "shown"): 127.3374},
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
