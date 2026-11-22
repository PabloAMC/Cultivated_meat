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
# repinned 2026-11-20 (model batch): bubble deaths and the 2% harvest loss in every sparged vessel, twice the fed-batch crew and the
# 2,415 L/m2 membrane life in perfusion, medium preparation capital, utilities in four parts
# repinned 2026-11-20 (final pass): stirred perfusion 16.0254 -> 15.9293 and chemostat 37.3715 -> 37.4347 (per-tank plant items,
# capex_at_size with tank_items; a vessel's recovery scales every cost). The airlift now follows the stirred tank's mixing rule at
# its own shape (aspect 3): a stirred tank of that shape is held at 45.1 g/L by mixing in the reference case, and so is the airlift
# (it was held at 78.9 g/L by CO2 removal). Output per m3 falls by 42%, so every per-kilo line rises: fed-batch capital 15.03 ->
# 25.70, labour 2.97 -> 5.08, medium 2.16 -> 3.50 (13.6 -> 23.3 L/kg), utilities 1.88 -> 3.15, consumables 1.14 -> 1.72
# (23.18 -> 39.14; 23.18 is what the old rule gives with today's other changes). Perfusion 18.12 -> 30.48 the same way
# (capital 10.05 -> 17.18, labour 3.90 -> 6.66, medium 2.16 -> 3.50, utilities 0.87 -> 1.42, consumables 1.14 -> 1.72)
GOLDEN_REF = {
    # 2026-11-21: batch 71.8825 -> 70.4820, fed-batch 21.0971 -> 17.3153 and fill-and-draw 19.9801 -> 16.5048 (the least medium
    # flow now caps an unwashed tank at pf_batch_end_x times its level, 120 g/L not 92, so CO2 and the waste hold them; and the
    # building's power by floor and class), chemostat 37.4347 -> 36.6689, perfusion 15.9293 -> 15.7207, airlift fed-batch
    # 39.1422 -> 38.3548, airlift perfusion 30.4806 -> 29.9640 (the building's power, labour per tank, the floor's glucose)
    ("stirred", "batch"): 70.4820, ("stirred", "fedbatch"): 17.3153, ("stirred", "filldraw"): 16.5048,
    ("stirred", "chemostat"): 36.6689, ("stirred", "perfusion"): 15.7207,
    ("airlift", "fedbatch"): 38.3548, ("airlift", "perfusion"): 29.9640,
    ("packed", "filldraw"): None, ("hollow", "chemostat"): None,
}
# 2026-11-19 audit batch: the reference grid does not move (Humbird's design keeps his 5 mmol/L and loses no runs). The low-lactate example:
# ammonia tolerance 4 mmol/L (35 L/kg in perfusion, was 28; fed-batch stops at 56 g/L, was 62) and lost runs pay for their membranes
# 2026-11-19 restructure: an unwashed tank is held by the waste mass balance (1.3 times the 4 mmol/L perfusion is held to), so
# the low-lactate example's fed-batch stops at 37 g/L, not 56 ($45.81 -> $67.42); the reference grid does not move (other by-products hold it at 92)
# 2026-11-20 batch: lactate held to 35 mmol/L in the scenarios. The airlift in perfusion (run thinner so its loop passes) is now CHEAPER
# than the stirred tank: bubble deaths follow the gas passed per litre of culture, 3.6% of the cells in the tall airlift against 11%
# repinned 2026-11-20 (final pass): stirred perfusion 49.9616 -> 49.4977 and fed-batch 73.4398 -> 71.7592 (per-tank plant items,
# recovery on every cost). The airlift in perfusion 47.6021 -> 53.1084: held at 87.4 g/L by the stirred tank's mixing rule at its
# shape (it ran at 138.7 g/L with the column thinned), so it is again dearer than the stirred tank (capital 11.71 -> 17.15, labour
# 3.78 -> 6.01; membranes and medium fall a little, consumables 23.69 -> 20.47)
# 2026-11-21: stirred perfusion 49.4977 -> 48.6815 (the thinned recycled-oxygen design), fed-batch 71.7592 -> 70.3150, airlift
# perfusion 53.1084 -> 52.7303 (the building's power by floor and class, the floor's glucose)
GOLDEN_CENTRAL = {("stirred", "perfusion"): 48.6815, ("stirred", "fedbatch"): 70.3150, ("airlift", "perfusion"): 52.7303}


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
    want *= r["harvested_share"]       # 2026-11-20: output is what is harvested (bubble deaths and the 2% harvest loss taken off)
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
    # 2026-11-20: and per kilo GROWN (output / harvested share): the two lose different shares to bursting bubbles, because the gas
    # a culture needs follows its density and the chemostat may stop thinner
    if not close(a["output"] / a["harvested_share"] / a["density"] * f / math.log(1.0 / (1.0 - f)),
                 b["output"] / b["harvested_share"] / b["density"] * slow, 1e-9) \
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
    # 2026-11-20 (final pass): the airlift follows the stirred tank's mixing rule at its own tall shape. Before, it was exempt from
    # mixing and held by CO2 removal (79 g/L against the stirred tank's 120). Now mixing holds it thinner still, at the density a
    # stirred tank of the same shape reaches, and it costs more than the stirred tank in perfusion in both settings
    stir_tall = fp.explore(aspect=V.VESSELS["airlift"]["aspect"], shape_cost=False)
    if not gr[("airlift", "perfusion")]["limit"] == "mixing" \
            or not close(gr[("airlift", "perfusion")]["density"], stir_tall["density"], 1e-9) \
            or not gr[("airlift", "perfusion")]["density"] < gr[("stirred", "perfusion")]["density"]:
        fails.append("the taller airlift should be held by mixing at the density of a stirred tank of its shape, below the stirred tank's")
    for name, g in (("reference", gr), ("central", gc)):
        if not g[("airlift", "perfusion")]["cost"] > g[("stirred", "perfusion")]["cost"]:
            fails.append(f"{name}: the airlift in perfusion should cost more than the stirred tank")
    if not V.what_if_bed(ref)["total"] > gr[("stirred", "perfusion")]["cost"]:
        fails.append("even the most favourable packed bed should cost more than a stirred tank in perfusion")
    # 2026-11-20 (final pass): before, the central airlift ran dense enough (139 g/L) that the column loop failed its check and fell
    # back to a lesser trick; held by mixing at 87 g/L, the column strips a thinner culture and passes with the case's own added equipment
    if gc[("airlift", "perfusion")]["tricks_fallback"] not in (None, "") or gc[("airlift", "perfusion")]["limit"] != "mixing":
        fails.append("central airlift perfusion: held by mixing, the loop should pass with the case's own added equipment")
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
