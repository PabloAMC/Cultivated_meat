#!/usr/bin/env python3
"""test_growth_rate.py — checks for the doubling-time envelope (growth_rate.py).

Three kinds of check:
  * consistency: at the base doubling time the envelope returns the Rung 2 cost exactly;
  * the closed form: with no time-made by-product, no death and no second limit, the optimum
    is a corner, and slowing pays if and only if  M > K * time_share * (r* - 1);
  * pinned numbers: the scenario and Monte Carlo figures quoted in the write-up.

Run directly (no pytest needed):
    python tests/test_growth_rate.py
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

TOL = 5e-3


def check() -> list:
    from cost_model import CostParams, biomass_cost, media_cost
    from growth_rate import CASES, GrowthParams, cost, optimum, volume_rel, monte_carlo

    fails = []
    pr, gp = CostParams(), GrowthParams()

    def expect(name, got, want, tol=TOL):
        if abs(float(got) - want) > tol:
            fails.append(f"{name}: want {want:.6g} got {float(got):.6g}")

    # --- consistency with Rung 2 at the base doubling time, in every case -----------------
    for case in CASES:
        expect(f"base cost [{case}]", cost(gp.tau_ref, pr, gp, case=case), float(biomass_cost(pr)))
        expect(f"base volume [{case}]", volume_rel(gp.tau_ref, gp, case), 1.0)

    # --- closed form: linear cost up to tau*, so a corner optimum ---------------------------
    bare = GrowthParams(bp_time_share=0.0, death_rate=0.0, next_level=0.0, nut_time_share=0.0,
                        tau_star=48.0, time_share=1.0)
    M = float(media_cost(pr, 1.00, 1.0))                     # medium cost per kg at $1.00/L
    for oh in (6.0, 15.0, 60.0):
        pays = M > oh * bare.time_share * (bare.tau_star / bare.tau_ref - 1.0)
        tau_opt, _, saving = optimum(pr, bare, 1.00, oh)
        if pays:
            # medium falls to its feedstock floor slightly before tau*, so the corner sits just short of it
            if not (40.0 < tau_opt <= 48.0 + 1e-9) or saving <= 0:
                fails.append(f"closed form (overhead {oh}): expected the tau* corner, got {tau_opt:.1f} h")
        elif tau_opt != bare.tau_ref or saving != 0:
            fails.append(f"closed form (overhead {oh}): expected the base corner, got {tau_opt:.1f} h")

    # --- slowing never pays when nothing falls with growth rate ----------------------------
    for case in ("byproduct-proportional", "nutrient"):
        for p in (0.20, 0.50, 1.00):
            tau_opt, _, saving = optimum(pr, gp, p, 6.0, case)
            if tau_opt != gp.tau_ref or saving != 0:
                fails.append(f"{case} at ${p}/L: optimum moved off the base ({tau_opt:.1f} h)")

    # --- volume can only rise with doubling time once overflow is gone ---------------------
    tau = np.linspace(gp.tau_star, 4 * gp.tau_ref, 50)
    if np.any(np.diff(volume_rel(tau, gp)) < -1e-12):
        fails.append("volume falls beyond tau*, where no by-product is left to save")

    # --- pinned numbers (central growth parameters; quoted in the write-up) -----------------
    for (p, oh), (want_tau, want_saving) in {
        (0.50, 19.1): (24.0, 0.0),      # the default: never pays
        (1.00, 19.1): (36.3, 1.140),    # dear medium: pays
        (1.00, 12.4): (36.3, 3.880),    # dear medium at the plant floor
        (0.20, 12.4): (24.0, 0.0),
    }.items():
        tau_opt, _, saving = optimum(pr, gp, p, oh, "byproduct-threshold")
        expect(f"tau_opt at ${p}/L, overhead {oh}", tau_opt, want_tau, tol=0.2)
        expect(f"saving at ${p}/L, overhead {oh}", saving, want_saving)

    mc = monte_carlo(20000, 0)["byproduct-threshold"]["saving"]
    expect("MC P(saving > $1), prior medium price", np.mean(mc > 1), 0.062, tol=0.01)
    mc1 = monte_carlo(20000, 0, 1.00)["byproduct-threshold"]["saving"]
    expect("MC P(saving > $1), medium $1.00/L", np.mean(mc1 > 1), 0.218, tol=0.01)
    mc02 = monte_carlo(20000, 0, 0.20)["byproduct-threshold"]["saving"]
    expect("MC P(saving > $1), medium $0.20/L", np.mean(mc02 > 1), 0.0, tol=0.005)

    print("growth-rate envelope: consistency, closed form and pinned numbers checked")
    return fails


def test_growth_rate():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL", f)
    print("PASS — the doubling-time envelope holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
