#!/usr/bin/env python3
"""test_retention.py — the retention-device study (retention.py).

Checks the duty against explore() (mass and liquid balance), that the devices are sized on the right flow, that the
default model is untouched (the hoped-for device reproduces the scenario costs), and pins the headline. Run directly or
under pytest.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import floor_physics as fp
import retention as R
import scenarios as S
from inputs import value


def close(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(1.0, abs(b))


def check() -> list:
    fails = []
    for name, kw in R.cases().items():
        d = R.duty(kw)
        r = d["result"]
        # liquid balance: medium in = bleed + permeate
        if not close(d["medium_m3_h"], d["bleed_m3_h"] + d["permeate_m3_h"]):
            fails.append(f"{name}: medium in != bleed + permeate")
        # the bleed carries the harvest: bleed x density = kg/h
        if not close(d["bleed_m3_h"] * d["density"], d["kg_h"]):
            fails.append(f"{name}: bleed x density != harvest")
        # the harvest over a year is the tank's output
        if not close(d["kg_h"] * 8760 * d["uptime"], r["output"] * d["vessel_m3"] * 1000.0):
            fails.append(f"{name}: harvest over the year != output")
    # the model's default is the TFF loop: retention.py's own sizing gives the same capital and membranes as explore()
    for name, kw in R.cases().items():
        d0 = R.duty(kw)
        sz, r = R.sizing("tff", kw, d0), d0["result"]
        if not (close(sz["capex_k_m3"], r["retention_capex"], 1e-9) and close(sz["cons_kg"], r["membranes"], 1e-9)):
            fails.append(f"{name}: TFF sizing ({sz['capex_k_m3']:.3f}k, ${sz['cons_kg']:.3f}) != explore "
                         f"({r['retention_capex']:.3f}k, ${r['membranes']:.3f})")
    # the old hoped-for device: a flat $89k per m3 and no membranes gives the old reference cost
    if not close(R.scenario_cost("hoped", {})["total"], 11.4801, 1e-5):
        fails.append("the hoped-for device no longer reproduces the old reference cost ($11.48)")
    cen = R.cases()["central"]
    d = R.duty(cen)
    # ATF: whole units that cover the permeate at the design flux
    a = R.sizing("atf", cen, d)
    if a["units"] != int(a["units"]) or a["units"] * value("rt_atf_area") * value("rt_flux_lmh") / 1000.0 < d["permeate_m3_h"]:
        fails.append("ATF units do not cover the permeate")
    # membranes: litres of permeate per kg x price per m2 / litres per m2 over a life
    want = d["permeate_m3_h"] * 1000.0 / d["kg_h"] * value("rt_membrane_price") / value("rt_membrane_life")
    if not close(R.sizing("tff", cen, d)["cons_kg"], want, 1e-12):
        fails.append("membrane cost per kg is not permeate x price / life")
    # a settler is not possible at the central duty (too much culture outside the tank), possible at the reference duty
    if not R.sizing("settler", cen, d)["impossible"] or R.sizing("settler", {}, None)["impossible"]:
        fails.append("settler feasibility: expected not possible in central, possible in the reference case")
    # a disc stack loses more cells the more of the culture it passes, and never all of them
    ds = R.sizing("discstack", cen, d)
    if not 0.0 < ds["loss"] < 1.0 or not ds["loss"] > R.sizing("discstack", {}, None)["loss"]:
        fails.append("disc-stack losses out of order")
    # ranges: favourable <= central <= unfavourable
    for dev in R.ORDER:
        rg = R.scenario_range(dev, cen)
        if not rg["low"]["total"] <= rg["mid"]["total"] + 1e-9 <= rg["high"]["total"] + 2e-9:
            fails.append(f"{dev}: range out of order")
    # pinned headline (central): TFF $26.64, disc stack $25.69, ATF $30.43
    for dev, want in (("tff", 26.6381), ("discstack", 25.6895), ("atf", 30.4258)):
        got = R.scenario_cost(dev, cen)["total"]
        if not close(got, want, 1e-4):
            fails.append(f"central {dev}: {got:.4f} != pinned {want}")
    # a thinner culture does not pay in the central case: the cheapest density is the one the tank allows
    scan = R.density_scan(R.cases()["central"])
    if min(scan, key=lambda r: r[1])[0] != 258.0 or not scan[-1][2] < scan[0][2]:
        fails.append("central: a thinner culture should save membranes but cost more in total")
    # pinned duty (reference case): 0.62 m3/h of medium, 0.16 of permeate
    d = R.duty({})
    if not (close(d["medium_m3_h"], 0.6195, 1e-3) and close(d["permeate_m3_h"], 0.1573, 1e-2)):
        fails.append(f"reference duty moved: medium {d['medium_m3_h']:.4f}, permeate {d['permeate_m3_h']:.4f}")
    return fails


def test_retention():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the retention-device study holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
