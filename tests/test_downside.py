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
# 2026-11-19 audit batch: ammonia tolerance 4 mmol/L lowers the selected cells' unwashed cap from 62 to 56 g/L (central and
# central_lean, model cap); best (capped by the least medium flow) and its 27 g/L figures do not move. Cautious: glucose from the
# cells' balance gives the published cells 4.8 mol of lactate a kilo, and an unwashed tank is now capped by whichever waste is
# further above the enhanced cells' (lactate here), so its cap falls from 52 to 25 g/L, below the 27 g/L shown for meat cells
# 2026-11-19 restructure: an unwashed tank is capped by the waste mass balance (pf_batch_end_x times the level perfusion is held
# to), not by Humbird's 120 g/L scaled. Selected cells' selected cells stop at 37 g/L (was 56), the published cells (cautious) at 13.6 g/L
# (was 25); the Engineered cells, all favourable case is still held at 92 g/L by other by-products. A fed-batch plant with shared medium keeps Humbird's full
# seed train (best and central_lean, fed-batch), so there fill-and-draw, which needs a seed only to restart, is the cheaper fallback.
GOLDEN = {
    "best": {("fedbatch", "model"): 15.6371, ("fedbatch", "shown"): 44.0019, ("filldraw", "model"): 14.3709},
    "central": {("fedbatch", "model"): 64.8950, ("fedbatch", "shown"): 88.2078, ("filldraw", "model"): 70.6191},
    "central_lean": {("fedbatch", "model"): 49.5107, ("filldraw", "model"): 47.9440},
    "cautious": {("fedbatch", "model"): 209.0520, ("filldraw", "model"): 242.0239, ("filldraw", "shown"): 242.0239},
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
            b = S.explore_kwargs({**S.SCENARIOS[k].choice, "mode": "fedbatch"}) if m == "fedbatch" else base   # 2026-11-19: seed train
            if c[(m, "model")]["cost"] > V.cell("stirred", m, b)["cost"] + 1e-9:
                fails.append(f"{k} {m}: re-chosen design dearer than the perfusion design")
            # a thinner culture is dearer, and its density is the one shown for meat cells.
            # 2026-11-19 audit batch: unless the model's own cap is already below it (cautious: lactate stops the published
            # cells' unwashed tank at 25 g/L, under the 27 g/L shown); then the two columns are the same tank
            model_x = c[(m, "model")]["density"]
            if model_x > value("vm_x_meat_shown") + 1e-9:
                if not c[(m, "shown")]["cost"] > c[(m, "model")]["cost"]:
                    fails.append(f"{k} {m}: the 27 g/L cost should exceed the model-cap cost")
                if not close(c[(m, "shown")]["density"], value("vm_x_meat_shown"), 1e-9):
                    fails.append(f"{k} {m}: density at the cap should be {value('vm_x_meat_shown')}")
            elif not (close(c[(m, "shown")]["density"], model_x, 1e-9) and close(c[(m, "shown")]["cost"], c[(m, "model")]["cost"], 1e-9)):
                fails.append(f"{k} {m}: the model's cap ({model_x:.1f} g/L) is under the density shown, so both columns should be that tank")
            # no perfusion is dearer than perfusion in every scenario
            if not c[(m, "model")]["cost"] > c["perfusion"]:
                fails.append(f"{k} {m}: the fallback should cost more than perfusion")
            if not c[(m, "shown")]["share"] <= c[(m, "model")]["share"] <= c["perfusion_share"] + 1e-9:
                fails.append(f"{k} {m}: shares out of order")
        # only the cautious case's own cap is under the density shown for meat cells
        if (c[("fedbatch", "model")]["density"] < value("vm_x_meat_shown")) != (k == "cautious"):
            fails.append(f"{k}: fed-batch cap {c[('fedbatch', 'model')]['density']:.1f} g/L against {value('vm_x_meat_shown')} shown: "
                         "rewrite section 2 of research_notes/no_perfusion_downside.md")
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
