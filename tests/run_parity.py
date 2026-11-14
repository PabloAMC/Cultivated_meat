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
income (the channel that previously diverged), the calibration solve, the milk cross-check, the
foothold rung's per-product price ratio (where a scaffold-cost mismatch once slipped through), and
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
import tempfile

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
# Monte-Carlo medians (percentage points): JS and Python draw with different PRNGs, so they can only
# agree within sampling noise (~0.1 pp at N=3000). 0.4 pp still catches a changed sampled set.
MC_TOL = 0.4


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

    # Write to the system temp dir, NOT the (possibly read-only / mounted) test dir — on some
    # mounted filesystems os.remove of a file under tests/ raises PermissionError, making the
    # test appear to fail when the model is fine. tempfile + try/except OSError is robust.
    fd, model_js = tempfile.mkstemp(prefix="_model_extracted_", suffix=".js")
    os.close(fd)
    open(model_js, "w", encoding="utf-8").write(_extract_model_js(HTML))
    try:
        out = subprocess.run([node, PROBE, model_js], capture_output=True, text=True, timeout=120)
    finally:
        try:
            os.remove(model_js)
        except OSError:
            pass
    if out.returncode != 0:
        raise RuntimeError(f"node probe failed (exit {out.returncode}):\n{out.stderr or out.stdout}")
    data = json.loads(out.stdout.strip().splitlines()[-1])
    if "error" in data:
        raise RuntimeError(f"JS probe error: {data['error']}")
    return data


# ---------------------------------------------------------------------------
# Python side: the SAME quantities from the source-of-truth modules.
# ---------------------------------------------------------------------------
def _python_reference(grid_keys, health_keys, timing_R, weight_cases=()) -> dict:
    from market_share import DemandParams, share, pb_milk_check
    from cost_model import CostParams, biomass_cost, ratio as cost_ratio
    from adoption_timing import TimingParams, simulate
    from foothold import PRODUCTS as FOOTHOLD_PRODUCTS, product_R

    pr = DemandParams()
    cp = CostParams()

    headline = {
        "basicR": (biomass_cost(cp) + cp.markup_add) / cp.p_conv,
        "beta_ref": pr.beta_ref,
        "anchor_price": pr.anchor_price,
        "w_realtissue_M": pr.w_realtissue_M,
        "w_health_M": pr.w_health_M,
        "w_health_E": pr.w_health_E,
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
    # foothold rung: per-product price ratio R = product_R (cost->R at the central inputs, divided
    # by base_price). Mirrors the JS footR at the slider defaults. Keyed by label; only the injected
    # (non-no_referent) products have a price axis, matching what build_interactive injects.
    foothold = {p.label: float(product_R(p))
                for p in FOOTHOLD_PRODUCTS if not p.no_referent}
    # EXPERT weight overrides: rebuild the calibration with the same values pinned the JS did, and
    # read the solved weights + shares (mirror of DemandParams.pinned_weights). Keyed by case index.
    weights = []
    for c in weight_cases:
        vals = {k: float(v) for k, v in c["vals"].items()}
        dpw = DemandParams(pinned_weights=frozenset(c["pin"]), **vals)
        weights.append({
            "w_realtissue_M": dpw.w_realtissue_M, "w_health_M": dpw.w_health_M,
            "w_health_E": dpw.w_health_E,
            "parity": share(1.0, dpw, accept_x=1.0, theta_free_M=0.0),
            "pb": share(1.0, dpw, cultivated_present=False, which="pb")})

    # timing rung at the JS-reported R (use simulate -> same _run core)
    tp = TimingParams()
    timing = simulate(timing_R, pr, tp, acceptance_grows=True, which="x")["share"]
    from adoption_timing import years_to_stabilize
    tstabs = [years_to_stabilize(timing_R, pr, TimingParams(accept_rate=r)) for r in (0.05, 0.15, 0.5)]
    return {"headline": headline, "grid": grid, "health": health,
            "foothold": foothold, "weights": weights, "timing": list(map(float, timing)),
            "tstabs": [int(x) for x in tstabs]}


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
    weight_cases = js.get("weightCases", [])
    py = _python_reference(grid_keys, health_keys, js["timing"]["R"], weight_cases)
    fails = []

    # EXPERT weight overrides: the pinned-weight calibration must mirror Python (the new override path)
    worst_w = 0.0
    for i, (jc, pc) in enumerate(zip(weight_cases, py["weights"])):
        for k, pv in pc.items():
            jv = jc["out"][k]
            d = abs(pv - jv)
            worst_w = max(worst_w, d)
            if d > TOL:
                fails.append(f"weightCase[{i}] {jc['pin'] or list(jc['vals'])} [{k}]: "
                             f"python={pv:.6f} js={jv:.6f} diff={d:.2e}")

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

    # build-your-own-case controls: floorExplore (JS) against floor_physics.explore
    import floor_physics as _fp
    worst_fx = 0.0
    if not js.get("fxGrid"):
        fails.append("fxGrid: not emitted by the JS probe")
    for dh, m, v, pl, mo, tot, dens, out, lim in js.get("fxGrid", []):
        r = _fp.explore(dh, m, v, pl, mo, charge=0.173, maintenance_share=0.31 if dh == 48 else None,
                        hazard=0.02 if v == 5 else 0.0, run_days=25, restart_fail_days=14,
                        waste=0.3 if v == 200 else 0.0, pco2_mbar=160 if dh == 24 else None,
                        gas_velocity=0.009 if m == 3000 else None, aspect=1.0 if v == 5 else None,
                        osm_limit=380.0 if pl == "sanitary" else None, ph=7.0 if mo == "filldraw" else None,
                        min_perfusion=12.0 if v == 20 else None, medium_l=30.5 if m == 550 else None, medium_price=0.5, growth_factors=(dh == 16),
                        cell_share=0.5 if pl == "pharma" else 1.0)
        d = max(abs(r["product"] - tot), abs(r["density"] - dens), abs(r["output"] - out))
        worst_fx = max(worst_fx, d)
        if d > 1e-6 or r["limit"] != lim:
            fails.append(f"floorExplore dh={dh} m={m} v={v} {pl} {mo}: python={r['product']:.6f} ({r['limit']}) "
                         f"js={tot:.6f} ({lim})")

    # the tricks: floorExplore (JS) against explore with column, pressure, explicit wastes and a sorbent
    FX_TRICKS = [{'column': 'co2'}, {'column': 'o2_closed', 'p_top': 1.0, 'gas_v': 0.002, 'col_pout': 55.0}, {'p_top': 0.5, 'aspect': 1.0}, {'nh3_kg': 0.14, 'lac_yield': 1.05, 'glc_kg': 0.84, 'doubling_h': 42.9}, {'nh3_kg': 0.7, 'sorbent': 0.8, 'sorbent_price': 0.3}, {'column': 'co2', 'plant': 'microbial', 'vessel_m3': 50, 'p_top': 0.0}, {'mode': 'filldraw', 'nh3_kg': 0.2}, {'sorbent': 0.5, 'nh3_kg': 0.3, 'lac_yield': 0.4, 'osm_limit': 380, 'sorbent_cycles': 10}, {'column': 'o2_closed', 'p_top': 1.0, 'aspect': 0.8, 'doubling_h': 30, 'mass_pg': 2000, 'nh3_kg': 0.1}]
    names = {"gas_v": "gas_velocity", "p_top": "p_top_barg", "pco2": "pco2_mbar", "maint": "maintenance_share",
             "restart_fail": "restart_fail_days"}
    js_tr = js.get("fxTricks", [])
    if len(js_tr) != len(FX_TRICKS):
        fails.append("fxTricks: not emitted by the JS probe")
    for case, jr in zip(FX_TRICKS, js_tr):
        kw = {names.get(k, k): v for k, v in case.items()}
        r = _fp.explore(charge=0.173, **kw)
        tot, dens, lim, ml, setby, jlims = jr
        d = max(abs(r["total"] - tot), abs(r["density"] - dens), abs(r["medium_l"] - ml))
        bad_lims = [k for k, v in r["limits"].items()
                    if not ((v == float("inf") and jlims.get(k) is None) or (jlims.get(k) is not None and abs(v - jlims[k]) < 1e-6))]
        if d > 1e-6 or r["limit"] != lim or r["medium_set_by"] != setby or bad_lims:
            fails.append(f"floorExplore tricks {case}: python={r['total']:.6f} ({r['limit']}, {r['medium_set_by']}) "
                         f"js={tot:.6f} ({lim}, {setby}) limits differ: {bad_lims}")

    # tornado of limiting factors: fxTornadoRows (JS) against floor_physics.floor_tornado
    cases = [dict(), dict(doubling_h=40.0, mass_pg=1500.0, vessel_m3=50.0, plant="microbial", charge=0.2, waste=0.1),
             dict(mass_pg=2500.0, pco2_mbar=50.0, pco2_range=(10.0, 100.0))]
    if len(js.get("fxTor", [])) != len(cases):
        fails.append("fxTor: not emitted by the JS probe")
    for case, jrows in zip(cases, js.get("fxTor", [])):
        prow = {r[0]: (r[1], r[2]) for r in _fp.floor_tornado(**case)}
        for lab, a, b in jrows:
            if lab not in prow or abs(prow[lab][0] - a) > 1e-6 or abs(prow[lab][1] - b) > 1e-6:
                fails.append(f"tornado '{lab}' case {case}: python={prow.get(lab)} js=({a:.6f}, {b:.6f})")

    # foothold rung: per-product price ratio R (the cost->R machinery shared with foothold.product_R;
    # the corner the scaffold-cost mismatch slipped through). JS emits [label, R] per product.
    worst_f = 0.0
    js_foothold = dict(js.get("foothold", []))
    for label, pv in py["foothold"].items():
        if label not in js_foothold:
            fails.append(f"foothold[{label}]: in Python reference but not emitted by JS")
            continue
        jv = js_foothold[label]
        d = abs(pv - jv)
        worst_f = max(worst_f, d)
        if d > TOL:
            fails.append(f"foothold[{label}]: python={pv:.6f} js={jv:.6f} diff={d:.2e}")

    # AUTHENTICITY ladder: tAuth(tier, r, τ) must mirror meat_market.tier_authenticity. Build one
    # MeatType per tier (basic = unstructured; cut/premium by price vs a $10 base) and compare.
    from meat_market import MeatType, tier_authenticity
    from inputs import SCAF
    _mt = {"basic": MeatType("x", 10.0, 0.0), "cut": MeatType("x", 10.0, 0.0, scaffold=SCAF),
           "premium": MeatType("x", 30.0, 0.0, scaffold=SCAF)}
    _CUST = {"basic": 0.5, "cut": -1.0, "premium": -2.5}
    worst_a = 0.0
    for kind, t, r, jv in js.get("authCheck", []):
        auth = None if kind == "def" else _CUST
        pv = tier_authenticity(_mt[t], 10.0, r, auth)
        d = abs(pv - jv)
        worst_a = max(worst_a, d)
        if d > TOL:
            fails.append(f"authCheck[{kind} {t} r={r}]: python={pv:.6f} js={jv:.6f} diff={d:.2e}")

    # IMPORTANCE BREAKDOWN: the per-factor utils decomposition must mirror utility_breakdown.
    from market_share import utility_breakdown, DemandParams as _DP
    pr = _DP()
    worst_b = 0.0
    for i, c in enumerate(js.get("bdCases", [])):
        o = c["o"]
        pv = utility_breakdown(
            c["R"], pr, seg="M", which=o.get("which", "x"),
            accept_x=o.get("ax"), theta_free_M=o.get("tfM"), eps_own=o.get("eps"),
            income=o.get("income"), neophobia_x=o.get("nbx"), tier_offset=o.get("toff", 0.0),
            health_x=o.get("hx"), p_ref=o.get("pRef"))
        for k, pvv in pv.items():
            jvv = c["out"][k]
            d = abs(pvv - jvv)
            worst_b = max(worst_b, d)
            if d > TOL:
                fails.append(f"bdCase[{i}] R={c['R']} [{k}]: python={pvv:.6f} js={jvv:.6f} diff={d:.2e}")

    # PREMISE DIALS (b_x, b_p): what-ifs applied after a calibration run in the observed world.
    from market_share import DemandParams as _DPp, share as _share
    worst_p = 0.0
    for kind, v, jsh, jbeta, jwrt in js.get("premise", []):
        dpp = _DPp(real_tissue_x=v) if kind == "x" else _DPp(real_tissue_p=v)
        psh = (_share(1.0, dpp, accept_x=1.0, theta_free_M=0.0) if kind == "x"
               else _share(1.0, dpp, cultivated_present=False, which="pb"))
        for lab, pv, jv in (("share", psh, jsh), ("beta", dpp.beta_ref, jbeta),
                            ("w_realtissue_M", dpp.w_realtissue_M, jwrt)):
            d = abs(pv - jv)
            worst_p = max(worst_p, d)
            if d > TOL:
                fails.append(f"premise b_{kind}={v} [{lab}]: python={pv:.6f} js={jv:.6f} diff={d:.2e}")

    # MONTE CARLO (statistical): the page's penetration band samples the same inputs as the Python
    # roll-up quoted in RESULTS.md. Different PRNGs, so medians must agree within sampling noise
    # (MC_TOL percentage points; the bug this guards against was a ~1.4 pp gap at the US median).
    mc = js.get("mcCheck")
    mc_msg = "no MC check"
    if mc:
        import numpy as np
        from meat_market import monte_carlo as pen_mc
        from inputs import MC_COST_INPUTS, MC_DEMAND_INPUTS, MC_TIER_INPUTS
        want = list(MC_COST_INPUTS + MC_DEMAND_INPUTS + MC_TIER_INPUTS)
        if list(mc["inputs"]) != want:
            fails.append(f"MC sampled inputs differ: page={mc['inputs']} python={want}")
        m = pen_mc(mc["region"], int(mc["n"]))
        diffs = []
        for key, arr in (("vol_p50", m["vol"]), ("val_p50", m["val"])):
            pv, jv = float(np.percentile(arr, 50)), float(mc[key])
            diffs.append(abs(pv - jv))
            if abs(pv - jv) > MC_TOL:
                fails.append(f"MC {mc['region']} {key}: python={pv:.2f}% page={jv:.2f}% "
                             f"diff={abs(pv - jv):.2f} pp (> {MC_TOL} pp: do they sample the same inputs?)")
        mc_msg = f"MC median max diff = {max(diffs):.2f} pp (tol {MC_TOL})"

    # years to 90% of the long-run share (accept_rate 0.05, 0.15, 0.5): must be identical integers
    if [int(x) for x in js["timing"].get("tstabs", [])] != py["tstabs"]:
        fails.append(f"years-to-stabilize: python={py['tstabs']} js={js['timing'].get('tstabs')}")
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
          f"{len(py['foothold'])} foothold products, {len(weight_cases)} weight-override cases, "
          f"{len(py['headline'])} headline values, {n} timing years; grid max diff = {worst:.2e}, "
          f"health max diff = {worst_h:.2e}, foothold max diff = {worst_f:.2e}, "
          f"weight-override max diff = {worst_w:.2e}, authenticity max diff = {worst_a:.2e}, "
          f"breakdown max diff = {worst_b:.2e}, premise-dial max diff = {worst_p:.2e} (tol {TOL:.0e}); {mc_msg}")
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
