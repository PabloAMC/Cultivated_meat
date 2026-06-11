#!/usr/bin/env python3
"""run_parity.py — assert the interactive page's JS model MIRRORS the Python source of truth.

build_interactive.py hand-ports ~20 model functions (utilities / shareCalc / solveCalibration
/ deriveBeta / penetration / bassTrajectory …) from the Python modules into JavaScript so the
explorer runs offline. That duplication is the model's biggest maintenance risk: a change to one
side can silently diverge from the other (it already did once — a regional income-term mismatch
that this very test now guards against).

This test extracts the embedded JS from `interactive.html`, runs it headless under Node
(tests/js_probe.js), recomputes the same quantities with the Python model, and asserts they
agree to a tight tolerance over a grid that exercises price, both acceptance dials, elasticity,
income (the channel that previously diverged), the calibration solve, the milk cross-check, and
the timing rung.

Run directly (no pytest needed):
    python tests/run_parity.py
Or under pytest, if installed:
    pytest tests/run_parity.py

Exits 0 on parity, 1 on mismatch, and SKIPS (exit 0 with a notice) if Node is unavailable.
Re-run `python build_interactive.py` first if you've changed any Python model code, so
interactive.html reflects the current source.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.dirname(HERE)
sys.path.insert(0, MODEL_DIR)

HTML = os.path.join(MODEL_DIR, "interactive.html")
PROBE = os.path.join(HERE, "js_probe.js")

# Tolerance: the demand model matches to ~1e-5 because the JS and Python calibration use
# independent bisection loops (same iteration counts, but floating-point paths differ a hair).
# 1e-4 absolute on a share (i.e. <0.01 percentage point) is comfortably tight: the income bug
# this guards against was a 5-8 PERCENTAGE-POINT divergence, ~1000x this bound.
TOL = 1e-4


# ---------------------------------------------------------------------------
# JS side: extract the model <script> from interactive.html, run the probe.
# ---------------------------------------------------------------------------
def _extract_model_js(html_path: str) -> str:
    html = open(html_path, encoding="utf-8").read()
    bodies = [b for _a, b in re.findall(r"<script([^>]*)>(.*?)</script>", html, flags=re.S)
              if "function utilities" in b]
    if not bodies:
        raise RuntimeError("could not find the model <script> in interactive.html "
                           "(did the page structure change?)")
    return bodies[0]


def _run_js() -> dict:
    node = shutil.which("node")
    if node is None:
        return {"_skip": "node not found on PATH — JS parity not checked"}
    if not os.path.exists(HTML):
        raise RuntimeError(f"{HTML} missing — run `python build_interactive.py` first")

    model_js = os.path.join(HERE, "_model_extracted.js")
    open(model_js, "w", encoding="utf-8").write(_extract_model_js(HTML))
    try:
        out = subprocess.run([node, PROBE, model_js], capture_output=True, text=True, timeout=120)
    finally:
        if os.path.exists(model_js):
            os.remove(model_js)
    if out.returncode != 0:
        raise RuntimeError(f"node probe failed (exit {out.returncode}):\n{out.stderr or out.stdout}")
    data = json.loads(out.stdout.strip().splitlines()[-1])
    if "error" in data:
        raise RuntimeError(f"JS probe error: {data['error']}")
    return data


# ---------------------------------------------------------------------------
# Python side: the SAME quantities from the source-of-truth modules.
# ---------------------------------------------------------------------------
def _python_reference(grid_keys, health_keys, timing_R) -> dict:
    from market_share import DemandParams, share, pb_milk_check
    from cost_model import CostParams, biomass_cost, ratio as cost_ratio
    from adoption_timing import TimingParams, simulate

    pr = DemandParams()
    cp = CostParams()

    headline = {
        "basicR": (biomass_cost(cp, 0.63, 1.0) + cp.markup_add) / cp.p_conv,
        "beta_ref": pr.beta_ref,
        "anchor_price": pr.anchor_price,
        "w_realtissue_M": pr.w_realtissue_M,
        "K_wholefood_M": pr.K_wholefood_M,
        "K_wholefood_E": pr.K_wholefood_E,
        "pb": share(1.0, pr, cultivated_present=False, which="pb"),
        "parity": share(1.0, pr, accept_x=1.0, theta_free_M=0.0),
        "milk": pb_milk_check(pr),
    }
    # share over the SAME grid the JS emitted (keyed by the input tuple)
    grid = {}
    for (R, ax, tfM, eps, income) in grid_keys:
        grid[(R, ax, tfM, eps, income)] = share(
            R, pr, accept_x=ax, theta_free_M=tfM, eps_own=eps, income=income)
    # health grid: sweep cultivated (hx) and plant-based (hp) health dials, both shares
    health = {}
    for (R, hx, hp, which) in health_keys:
        health[(R, hx, hp, which)] = share(R, pr, health_x=hx, health_p=hp, which=which)
    # timing rung at the JS-reported R (use simulate -> same _run core)
    tp = TimingParams()
    timing = simulate(timing_R, pr, tp, acceptance_grows=True, which="x")["share"]
    return {"headline": headline, "grid": grid, "health": health,
            "timing": list(map(float, timing))}


# ---------------------------------------------------------------------------
# Compare
# ---------------------------------------------------------------------------
def check_parity() -> list:
    """Return a list of human-readable failures (empty == parity holds)."""
    js = _run_js()
    if "_skip" in js:
        print(f"SKIP: {js['_skip']}")
        return []

    grid_keys = [tuple(row[:5]) for row in js["grid"]]
    health_keys = [tuple(row[:4]) for row in js.get("healthGrid", [])]
    py = _python_reference(grid_keys, health_keys, js["timing"]["R"])
    fails = []

    # headline
    for k, pv in py["headline"].items():
        jv = js["headline"][k]
        if abs(pv - jv) > max(TOL, abs(pv) * 1e-4):
            fails.append(f"headline[{k}]: python={pv:.8g} js={jv:.8g} diff={abs(pv - jv):.2e}")

    # grid
    js_grid = {tuple(row[:5]): row[5] for row in js["grid"]}
    worst = 0.0
    for key, pv in py["grid"].items():
        jv = js_grid[key]
        d = abs(pv - jv)
        worst = max(worst, d)
        if d > TOL:
            R, ax, tfM, eps, income = key
            fails.append(f"grid R={R} ax={ax} tfM={tfM} eps={eps} income={income}: "
                         f"python={pv:.6f} js={jv:.6f} diff={d:.2e}")

    # health grid (the cultivated/plant-based health-perception dials)
    js_health = {tuple(row[:4]): row[4] for row in js.get("healthGrid", [])}
    worst_h = 0.0
    for key, pv in py["health"].items():
        jv = js_health[key]
        d = abs(pv - jv)
        worst_h = max(worst_h, d)
        if d > TOL:
            R, hx, hp, which = key
            fails.append(f"health R={R} hx={hx} hp={hp} which={which}: "
                         f"python={pv:.6f} js={jv:.6f} diff={d:.2e}")

    # timing trajectory
    jt = js["timing"]["share"]
    pt = py["timing"]
    n = min(len(jt), len(pt))
    if len(jt) != len(pt):
        fails.append(f"timing length mismatch: python={len(pt)} js={len(jt)}")
    for k in range(n):
        if abs(pt[k] - jt[k]) > TOL:
            fails.append(f"timing[year {k}]: python={pt[k]:.6f} js={jt[k]:.6f} "
                         f"diff={abs(pt[k] - jt[k]):.2e}")

    print(f"parity check: {len(py['grid'])} grid points, {len(py['health'])} health points, "
          f"{len(py['headline'])} headline values, {n} timing years; "
          f"grid max diff = {worst:.2e}, health max diff = {worst_h:.2e} (tol {TOL:.0e})")
    return fails


def test_python_js_parity():
    """pytest entry point: the JS mirror agrees with the Python source of truth."""
    fails = check_parity()
    assert not fails, "Python↔JS parity FAILED:\n  " + "\n  ".join(fails)


if __name__ == "__main__":
    failures = check_parity()
    if failures:
        print(f"\nFAIL — {len(failures)} mismatch(es):")
        for f in failures[:25]:
            print("  " + f)
        if len(failures) > 25:
            print(f"  … and {len(failures) - 25} more")
        sys.exit(1)
    print("PASS — the JS model mirrors the Python source of truth.")
    sys.exit(0)
