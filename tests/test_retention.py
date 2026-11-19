#!/usr/bin/env python3
"""test_retention.py — the retention-device study (retention.py).

Checks the duty against explore() (mass and liquid balance), that the devices are sized on the right flow, that the
default model is untouched (the hoped-for device reproduces the scenario costs), and pins the headline. Run directly or
under pytest.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import floor_physics as fp
import retention as R
import scenarios as S
from inputs import value


def close(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(1.0, abs(b))


def run_share(kw: dict) -> float:
    """The share of a planned run an average start completes at the case's chance of losing a run per day (explore()'s rule
    for filter membranes since the 2026-11-19 audit: a lost run throws its membranes away early). 1 with no losses."""
    h, days = kw.get("hazard", 0.0), value("pf_run_days")
    return 1.0 if h <= 0 else (1.0 - math.exp(-h * days)) / (h * days)


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
    # the model's default is the TFF loop: retention.py's own sizing gives the same capital and membranes as explore().
    # 2026-11-19 audit batch: both now charge the membranes of lost runs (life x the share of a planned run an average start
    # completes, explore()'s `run_frac`), and that share is the one this test works out from the case's chance of losing a run
    for name, kw in R.cases().items():
        d0 = R.duty(kw)
        sz, r = R.sizing("tff", kw, d0), d0["result"]
        if not (close(sz["capex_k_m3"], r["retention_capex"], 1e-9) and close(sz["cons_kg"], r["membranes"], 1e-9)):
            fails.append(f"{name}: TFF sizing ({sz['capex_k_m3']:.3f}k, ${sz['cons_kg']:.3f}) != explore "
                         f"({r['retention_capex']:.3f}k, ${r['membranes']:.3f})")
        if not close(d0["run_frac"], run_share(kw), 1e-9):
            fails.append(f"{name}: run share {d0['run_frac']:.4f} != {run_share(kw):.4f} from the chance of losing a run")
    # the old hoped-for device: a flat $89k per m3 and no membranes gives the reference case's cost with that device
    # 2026-11-19 repin: nutrient floor $1.70 -> $2.00 ($12.15 -> $12.45); growth factors inside complete media prices
    # (central -$2.99, disc stack -$3.69 as it buys more medium)
    if not close(R.scenario_cost("hoped", {})["total"], 12.4512, 1e-5):
        fails.append("the hoped-for device no longer gives the pinned reference cost ($12.45)")
    cen = R.cases()["central"]
    d = R.duty(cen)
    # ATF: whole units that cover the permeate at the design flux
    a = R.sizing("atf", cen, d)
    if a["units"] != int(a["units"]) or a["units"] * value("rt_atf_area") * value("rt_flux_lmh") / 1000.0 < d["permeate_m3_h"]:
        fails.append("ATF units do not cover the permeate")
    # membranes: litres of permeate per kg x price per m2 / litres per m2 over a life, the life cut by the runs lost
    want = d["permeate_m3_h"] * 1000.0 / d["kg_h"] * value("rt_membrane_price") / (value("rt_membrane_life") * run_share(cen))
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
    # pinned headline (central): TFF $32.80, disc stack $27.49, ATF $37.48
    # 2026-11-19 audit batch: ammonia tolerance 4 mmol/L (35 L/kg, was 28: permeate 1.71 m3/h, was 1.31, so more membrane, more
    # ATF units, a second running disc stack and more cells burst); the TFF loop and the ATF filter also pay for the membranes
    # of lost runs
    for dev, want in (("tff", 32.8028), ("discstack", 27.4945), ("atf", 37.4828)):
        got = R.scenario_cost(dev, cen)["total"]
        if not close(got, want, 1e-4):
            fails.append(f"central {dev}: {got:.4f} != pinned {want}")
    # a thinner culture does not pay in the central case: the cheapest density is the one the tank allows
    scan = R.density_scan(R.cases()["central"])
    if min(scan, key=lambda r: r[1])[0] != 258.0 or not scan[-1][2] < scan[0][2]:
        fails.append("central: a thinner culture should save membranes but cost more in total")
    # the alternative membranes: each is cheaper per kg than the default TFF loop in the central case, and the dialyser's
    # lower flux needs more membrane area for the same duty
    tff_c = R.scenario_cost("tff", cen)
    for dev in ("reuse", "dialyser", "ceramic"):
        if not R.scenario_cost(dev, cen)["total"] < tff_c["total"]:
            fails.append(f"central {dev}: should cost less than the TFF loop")
    if not R.sizing("dialyser", cen, d)["area_m2"] > R.sizing("tff", cen, d)["area_m2"]:
        fails.append("dialyser: lower flux should need more membrane area than the TFF loop")
    if not R.sizing("reuse", cen, d)["cons_kg"] < R.sizing("tff", cen, d)["cons_kg"]:
        fails.append("reused modules: membranes per kg should fall")
    # 2026-11-19 audit batch: ammonia tolerance 4 mmol/L (more permeate, so more membrane area and membranes); reused modules and
    # dialysers pay for the membranes of lost runs, ceramic elements are cleaned and kept
    for dev, want in (("reuse", 24.2304), ("dialyser", 20.2877), ("ceramic", 21.6535)):
        got = R.scenario_cost(dev, cen)["total"]
        if not close(got, want, 1e-3):
            fails.append(f"central {dev}: {got:.4f} != pinned {want}")
    # the order of the membrane devices: dialysers < ceramic < reused modules < TFF loop < ATF filter
    order = [R.scenario_cost(dev, cen)["total"] for dev in ("dialyser", "ceramic", "reuse", "tff", "atf")]
    if order != sorted(order):
        fails.append("central: expected dialyser < ceramic < reused modules < TFF loop < ATF")
    # a lost run does not shorten a ceramic element's life: its membranes per kg are permeate x price / life as it stands
    if not close(R.sizing("ceramic", cen, d)["cons_kg"], d["permeate_m3_h"] * 1000.0 / d["kg_h"] * value("rt_ceramic_price") / value("rt_ceramic_life"), 1e-12):
        fails.append("ceramic: a lost run should not shorten the element's life")
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
