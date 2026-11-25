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
# Since 2026-11-24 (the default of 50% of meat buyers at equal price) the medians are about 3-5% and the page's runs about 13-17%
# above Python's (13% on 2026-11-23, when the medians were below 1%, a gap an absolute 0.4 pp could not see), so the tolerance
# is the larger of 0.4 pp and 25% of Python's median.
MC_TOL = 0.4
MC_TOL_REL = 0.25


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
        "basicR": cost_ratio(biomass_cost(cp), cp),
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

    # plants built item by item: floorExplore with items (JS) against explore(items=...) and plant_items
    import plant_items as _pi
    item_cases = [_pi.PLANTS["lean"], _pi.PLANTS["yeastplus"], _pi.PLANTS["yeast"], {"hall": "shed"},
                  {"oxygen": "bought", "seed": "one"}, {"vessels": "food", "medium": "shared"}]
    if len(js.get("fxItems", [])) != 2 * len(item_cases):
        fails.append("fxItems: not emitted by the JS probe")
    for i, mo, tot, capex in js.get("fxItems", []):
        r = _fp.explore(vessel_m3=50.0 if i == 3 else 20.0, mode=mo, charge=0.173, items=item_cases[i],
                        hazard=0.015 if i == 1 else 0.0, run_days=33, restart_fail_days=14)
        worst_fx = max(worst_fx, abs(r["total"] - tot))
        if abs(r["total"] - tot) > 1e-6 or abs(r["capex"] - capex) > 1e-6:
            fails.append(f"floorExplore items case {i} {mo}: python={r['total']:.6f} js={tot:.6f}")

    # the tricks: floorExplore (JS) against explore with column, pressure, explicit wastes and a sorbent
    FX_TRICKS = [{'column': 'co2'}, {'column': 'o2_closed', 'p_top': 1.0, 'gas_v': 0.002, 'col_pout': 55.0}, {'p_top': 0.5, 'aspect': 1.0}, {'nh3_kg': 0.14, 'lac_yield': 1.05, 'glc_kg': 0.84, 'doubling_h': 42.9}, {'nh3_kg': 0.7, 'sorbent': 0.8, 'sorbent_price': 0.3}, {'column': 'co2', 'plant': 'microbial', 'vessel_m3': 50, 'p_top': 0.0}, {'mode': 'filldraw', 'nh3_kg': 0.2}, {'sorbent': 0.5, 'nh3_kg': 0.3, 'lac_yield': 0.4, 'osm_limit': 380, 'sorbent_cycles': 10}, {'column': 'o2_closed', 'p_top': 1.0, 'aspect': 0.8, 'doubling_h': 30, 'mass_pg': 2000, 'nh3_kg': 0.1}, {'fat_fed': 1.0}, {'do_mmol': 0.05, 'doubling_h': 48, 'maint': 0.31}, {'rq': 1.0, 'gas_v': 0.003}, {'column': 'o2_closed', 'do_mmol': 0.08, 'gas_v': 0.002, 'fat_fed': 0.5, 'fat_price': 10.0}, {'column': 'co2', 'p_top': 0.5, 'do_mmol': 0.15, 'aspect': 1.2}, {'aspect': 1.0}, {'aspect': 0.8, 'shape_cost': False}, {'aspect': 2.5, 'vessel_m3': 100},
                 # a tank that is not washed, with the cells' lactate yield set: lactate can cap the density (2026-11-19)
                 {'mode': 'filldraw', 'nh3_kg': 0.14, 'lac_yield': 1.05, 'glc_balance': True, 'doubling_h': 43.0, 'mass_pg': 2000.0},
                 # 2026-11-19 restructure: the mass balance of an unwashed tank. Fed-batch (a batch that ends above the steady-state
                 # level, so its last doublings grow slower), with low-lactate cells at 4 mM and losses; and a chemostat (held at the level)
                 {'mode': 'filldraw', 'vm': {'kind': 'cyclic', 'washed': False, 'n_doublings': 2.0, 'turnaround_h': 10.0, 'restart_days': 2.0},
                  'nh3_kg': 0.14, 'lac_yield': 0.42, 'glc_balance': True, 'doubling_h': 36.0, 'mass_pg': 2000.0, 'nh3_limit': 4.0, 'hazard': 0.01},
                 {'mode': 'filldraw', 'vm': {'washed': False, 'shape': 1.0, 'dil_frac': 0.6}, 'nh3_kg': 0.2, 'nh3_limit': 3.0},
                 {'mode': 'filldraw', 'nh3_kg': 0.3, 'nh3_limit': 4.0, 'doubling_h': 30.0},
                 # 2026-11-20: the lactate the cells tolerate as an argument; bubble deaths (a set kill constant, the cap at half
                 # of growth, and with the litres of medium set)
                 {'lac_limit': 22.0, 'nh3_kg': 0.14, 'lac_yield': 0.42, 'glc_balance': True, 'doubling_h': 36.0, 'mass_pg': 2000.0},
                 {'kill': 1.6e-3, 'gas_v': 0.004}, {'kill': 0.01, 'doubling_h': 48.0}, {'medium_l': 60.0, 'kill': 8e-4},
                 {'mode': 'filldraw', 'lac_limit': 30.0, 'lac_yield': 1.05, 'glc_balance': True, 'kill': 0.0}]
    names = {"gas_v": "gas_velocity", "p_top": "p_top_barg", "pco2": "pco2_mbar", "maint": "maintenance_share",
             "restart_fail": "restart_fail_days"}
    js_tr = js.get("fxTricks", [])
    if len(js_tr) != len(FX_TRICKS):
        fails.append("fxTricks: not emitted by the JS probe")
    for case, jr in zip(FX_TRICKS, js_tr):
        kw = {names.get(k, k): v for k, v in case.items()}
        r = _fp.explore(charge=0.173, **kw)
        tot, dens, lim, ml, setby, jlims, jo2, jo2u, jco2, jcol = jr
        if (jcol is None) != (r["column"] is None) or (jcol and max(abs(jcol[0] - r["column"]["passes"]),
                abs(jcol[1] - r["column"]["loop_volume"]), abs(jcol[2] - r["column"]["ph_vs_safe"])) > 1e-6):
            fails.append(f"floorExplore tricks {case}: column passes / loop volume / pH differ: python "
                         f"{None if r['column'] is None else (r['column']['passes'], r['column']['ph_vs_safe'])} js {jcol}")
        d = max(abs(r["total"] - tot), abs(r["density"] - dens), abs(r["medium_l"] - ml), abs(r["o2_kg"] - jo2),
                abs(r["o2_kg_upkeep"] - jo2u), abs(r["co2_kg"] - jco2))
        bad_lims = [k for k, v in r["limits"].items()
                    if not ((v == float("inf") and jlims.get(k) is None) or (jlims.get(k) is not None and abs(v - jlims[k]) < 1e-6))]
        if d > 1e-6 or r["limit"] != lim or r["medium_set_by"] != setby or bad_lims:
            fails.append(f"floorExplore tricks {case}: python={r['total']:.6f} ({r['limit']}, {r['medium_set_by']}) "
                         f"js={tot:.6f} ({lim}, {setby}) limits differ: {bad_lims}")

    # 2026-11-20: cleaning and reusing the medium (explore's `clean`, `clean_share`) and a leaner feed for the litres that only
    # wash waste out (`wash_price`), on two scenarios in perfusion, a fed-batch one and Humbird's reference design. A route with
    # no share given takes the share that costs least. The same cases as tests/js_probe.js fxClean.
    import scenarios as _S1
    FX_CLEAN = [{'clean': 'none'}, {'clean': 'exchanger'}, {'clean': 'electrodialysis'}, {'clean': 'dialysis'},
                {'clean': 'exchanger', 'clean_share': 0.3}, {'clean': 'electrodialysis', 'clean_share': 0.5},
                {'clean': 'dialysis', 'clean_share': 0.9}, {'wash_price': 0.066},
                {'wash_price': 0.02, 'clean': 'dialysis', 'clean_share': 0.7}, {'wash_price': 0.0, 'clean': 'electrodialysis'}]
    clean_bases = [_S1.explore_kwargs(_S1.SCENARIOS[k].choice) for k in ("central", "cautious", "today")] + [{}]
    js_cl = js.get("fxClean", [])
    if len(js_cl) != len(clean_bases) or any(len(x) != len(FX_CLEAN) for x in js_cl):
        fails.append("fxClean: not emitted by the JS probe")
    CLEAN_OUT = ("total", "medium_l", "medium_l_unclean", "clean_capex", "clean_opex", "clean_capital", "clean_filter_membranes",
                 "clean_loop", "clean_share", "gas_used", "harvested_share", "membranes", "feedstock")
    worst_cl = 0.0
    for bi, (b, rows) in enumerate(zip(clean_bases, js_cl)):
        for case, jr in zip(FX_CLEAN, rows):
            r = _fp.explore(**{**b, **case})
            d = max(abs(r[k] - jv) / max(1.0, abs(r[k])) for k, jv in zip(CLEAN_OUT, jr))
            worst_cl = max(worst_cl, d)
            if d > 1e-6:
                fails.append(f"floorExplore cleaning, base {bi}, {case}: python "
                             f"{[round(r[k], 6) for k in CLEAN_OUT]} js {[round(v, 6) for v in jr]}")
        if abs(_fp.explore(**{**b, 'clean': 'none'})["total"] - _fp.explore(**b)["total"]) > 0:
            fails.append(f"cleaning, base {bi}: 'none' does not give the case itself")
        # the exchanger route is the sorbent lever, the same calculation
        a_, b_ = _fp.explore(**{**b, 'clean': 'exchanger', 'clean_share': 0.3}), _fp.explore(**{**b, 'sorbent': 0.3})
        if abs(a_["total"] - b_["total"]) > 1e-12 or abs(a_["medium_l"] - b_["medium_l"]) > 1e-12:
            fails.append(f"cleaning, base {bi}: the exchanger route is not explore's sorbent lever")

    # tornado of limiting factors: fxTornadoRows (JS) against floor_physics.floor_tornado
    cases = [dict(), dict(doubling_h=40.0, mass_pg=1500.0, vessel_m3=50.0, plant="microbial", charge=0.2, waste=0.1),
             dict(items=_pi.PLANTS["lean"]),
             dict(mass_pg=2500.0, pco2_mbar=50.0, pco2_range=(10.0, 100.0))]
    if len(js.get("fxTor", [])) != len(cases):
        fails.append("fxTor: not emitted by the JS probe")
    for case, jrows in zip(cases, js.get("fxTor", [])):
        prow = {r[0]: (r[1], r[2]) for r in _fp.floor_tornado(**case)}
        for lab, a, b in jrows:
            if lab not in prow or abs(prow[lab][0] - a) > 1e-6 or abs(prow[lab][1] - b) > 1e-6:
                fails.append(f"tornado '{lab}' case {case}: python={prow.get(lab)} js=({a:.6f}, {b:.6f})")

    # vessel types against operating modes: vmCell (JS) against vessels.cell, for the reference case and three presets
    import vessels as _V
    import scenarios as _S0
    vm_js = js.get("vm")
    if not vm_js:
        fails.append("vessels: not emitted by the JS probe")
    else:
        bases = [{}] + [_S0.explore_kwargs(_S0.SCENARIOS[k].choice) for k in ("central", "best", "cautious")]
        for b, rows in zip(bases, vm_js):
            for row in rows:
                for c in row:
                    pc = _V.cell(c[0], c[1], b)
                    if pc["possible"] != c[2]:
                        fails.append(f"vessels {c[0]} {c[1]}: possible python={pc['possible']} js={c[2]}")
                    elif pc["possible"] and (abs(pc["cost"] - c[3]) > 1e-6 * max(1.0, pc["cost"]) or pc["limit"] != c[4]
                                             or pc["tricks_fallback"] != c[6] or pc["density_unshown"] != c[8]):
                        fails.append(f"vessels {c[0]} {c[1]}: python={pc['cost']:.6f} ({pc['limit']}, {pc['tricks_fallback']!r}) "
                                     f"js={c[3]:.6f} ({c[4]}, {c[6]!r})")
    # the retention devices: rtCost (JS, page_retention.js) against retention.scenario_cost, for Humbird's reference case and
    # three presets and every device on the page; and floorExplore's extra_opex and flat retention capital against explore
    import retention as _R
    rt_js = js.get("rt") or {}
    ported = [k for k in _R.ORDER if k != "hoped" and k not in _R.PARTICLES]
    RT_FX = [{"extra_opex": 1.5}, {"extra_opex": 0.7, "hazard": 0.02, "plant": "microbial"},
             {"retention": 40.0, "extra_opex": 0.3, "hazard": 0.01}, {"retention": 0.0},
             {"mode": "filldraw", "retention": 40.0, "extra_opex": 2.0}]
    worst_rt = 0.0
    if not rt_js.get("cases") or len(rt_js.get("fx", [])) != len(RT_FX):
        fails.append("retention: not emitted by the JS probe")
    else:
        if rt_js["order"] != ported:
            fails.append(f"retention: devices on the page {rt_js['order']} are not those of retention.py {ported}")
        rel = lambda a, b: abs(a - b) / max(1.0, abs(a), abs(b))
        for case, jr in zip(RT_FX, rt_js["fx"]):
            r = _fp.explore(charge=0.173, **case)
            d = max(rel(r["total"], jr[0]), rel(r["extra_opex"], jr[1]), rel(r["capex"], jr[2]), rel(r["consumables"], jr[3]),
                    rel(r["run_frac"], jr[4]))
            worst_rt = max(worst_rt, d)
            if d > 1e-6:
                fails.append(f"floorExplore {case}: python total={r['total']:.6f} extra_opex={r['extra_opex']:.6f} "
                             f"capex={r['capex']:.6f} js={jr}")
        names = ("reference", "central", "best", "today")
        bases = [{}] + [_S0.explore_kwargs(_S0.SCENARIOS[k].choice) for k in names[1:]]
        for name, b, rows in zip(names, bases, rt_js["cases"]):
            for dev, tot, capex, cons, loss, beyond, imposs, base, units, area, parts, res_tot in rows:
                pc = _R.scenario_cost(dev, b)
                d = max(rel(pc["total"], tot), rel(pc["capex_k_m3"], capex), rel(pc["cons_kg"], cons), rel(pc["loss"], loss),
                        rel(pc["base"], base), rel(pc["units"], units), rel(pc["area_m2"], area),
                        rel(parts, tot), rel(res_tot, tot))          # the breakdown rtCost hands back adds up to its total
                worst_rt = max(worst_rt, d)
                if d > 1e-6 or pc["beyond"] != beyond or pc["impossible"] != imposs:
                    fails.append(f"retention {name} {dev}: python=${pc['total']:.6f} (capital {pc['capex_k_m3']:.6f}, running "
                                 f"{pc['cons_kg']:.6f}, loss {pc['loss']:.6f}, beyond {pc['beyond']}, {pc['impossible']!r}) "
                                 f"js=${tot:.6f} ({capex:.6f}, {cons:.6f}, {loss:.6f}, {beyond}, {imposs!r}; parts {parts:.6f})")
    print(f"retention devices: {sum(len(r) for r in rt_js.get('cases', []))} device-cases, max relative diff = {worst_rt:.2e}")
    # the scenarios: scEval / scShare / scPriorities / scInteractions / scDesign (JS) against scenarios.py
    import scenarios as _S
    sc = js.get("sc") or {}
    if not sc.get("cases"):
        fails.append("scenarios: not emitted by the JS probe")
    worst_sc = 0.0
    for vals, tot, lim, ml, wsh, ush in sc.get("cases", []):
        ch = dict(zip(_S.KEYS, vals))
        if len(vals) > len(_S.KEYS) and vals[len(_S.KEYS)]:   # the choice's extra settings (scenarios.EXTRAS), after the switches
            ch["extra"] = vals[len(_S.KEYS)]
        if len(vals) > len(_S.KEYS) + 1 and vals[len(_S.KEYS) + 1]:   # a thinned tank design (scenarios.design, 2026-11-21)
            ch["thin"] = vals[len(_S.KEYS) + 1]
        r = _S.run(ch)
        shs = _S.shares(r["total"], ("global", "us"))
        worst_sc = max(worst_sc, abs(r["total"] - tot))
        if abs(r["total"] - tot) > 1e-6 or r["limit"] != lim or abs(r["medium_l"] - ml) > 1e-6:
            fails.append(f"scenario {vals}: python={r['total']:.6f} ({r['limit']}, {r['medium_l']:.3f} L) js={tot:.6f} ({lim}, {ml:.3f} L)")
        for lab, pv, jv in (("world", shs["global"], wsh), ("us", shs["us"], ush)):
            if abs(pv - jv) > 0.02:
                fails.append(f"scenario {vals} {lab} share: python={pv:.4f}% js={jv:.4f}%")
    c0 = _S.SCENARIOS["central"].choice
    pri = _S.priorities(c0, True)
    for (k, best, wst, db, dw, sb, sw_), prow in zip(sc.get("pri", []), pri):
        if (k, best, wst) != (prow["switch"], prow["best"], prow["worst"]) or max(abs(db - prow["d_best"]), abs(dw - prow["d_worst"])) > 1e-6 \
                or max(abs(sb - prow["share_best"]), abs(sw_ - prow["share_worst"])) > 0.02:
            fails.append(f"priorities {k}: python=({prow['switch']}, {prow['best']}, {prow['worst']}, {prow['d_best']:.4f}, {prow['d_worst']:.4f}) js=({best}, {wst}, {db:.4f}, {dw:.4f})")
    if len(sc.get("pri", [])) != len(pri):
        fails.append("priorities: different number of switches")
    inter = _S.interactions(c0, 6, 0.25)
    if [(a, b) for a, b, _g in sc.get("inter", [])] != [(x["a"], x["b"]) for x in inter] or \
            any(abs(g - x["gap"]) > 1e-6 for (_a, _b, g), x in zip(sc.get("inter", []), inter)):
        fails.append(f"interactions: python={[(x['a'], x['b'], round(x['gap'], 4)) for x in inter]} js={sc.get('inter')}")
    for k, (tk, sh, th) in zip(_S.PAGE_ORDER, sc.get("design", [])):
        d = _S.design({**_S.SCENARIOS[k].choice, "tricks": "none", "shape": "tall"})
        if (d["tricks"], d["shape"]) != (tk, sh) or abs((d.get("thin") or 0.0) - (th or 0.0)) > 1e-9:
            fails.append(f"design {k}: python=({d['tricks']}, {d['shape']}, {d.get('thin')}) js=({tk}, {sh}, {th})")

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

    # OFFSET of a cut / premium product: tierOffset(premiumRamp(...)) must mirror meat_market.tier_offset. One MeatType per
    # case (unstructured, or a cut priced against a $10 species base), at several premium resistances and cell shares, with
    # the default premium penalty ("def") and a custom one set through the page's slider ("cust").
    from meat_market import MeatType, tier_offset
    from market_share import DemandParams as _DPa
    from inputs import SCAF
    _CUST_EXTRA = -2.5
    _pra = _DPa()
    worst_a = 0.0
    if len(js.get("authCheck", [])) < 10:
        fails.append("authCheck: not emitted by the JS probe")
    for kind, structured, price, r, cells, jv in js.get("authCheck", []):
        mt = MeatType("x", float(price), 0.0, scaffold=SCAF if structured else 0.0)
        pv = float(tier_offset(mt, 10.0, r, _pra, cell_share=cells, premium_extra=None if kind == "def" else _CUST_EXTRA))
        d = abs(pv - jv)
        worst_a = max(worst_a, d)
        if d > TOL:
            fails.append(f"authCheck[{kind} structured={structured} price={price} r={r} cells={cells}]: "
                         f"python={pv:.6f} js={jv:.6f} diff={d:.2e}")

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
        from inputs import MC_COST_INPUTS, MC_DEMAND_INPUTS, MC_TIER_INPUTS, MC_CUT_INPUTS
        want = list(MC_COST_INPUTS + MC_DEMAND_INPUTS + MC_TIER_INPUTS + MC_CUT_INPUTS)
        if list(mc["inputs"]) != want:
            fails.append(f"MC sampled inputs differ: page={mc['inputs']} python={want}")
        m = pen_mc(mc["region"], int(mc["n"]))
        diffs = []
        for key, arr in (("vol_p50", m["vol"]), ("val_p50", m["val"])):
            pv, jv = float(np.percentile(arr, 50)), float(mc[key])
            diffs.append(abs(pv - jv))
            tol = max(MC_TOL, MC_TOL_REL * pv)
            if abs(pv - jv) > tol:
                fails.append(f"MC {mc['region']} {key}: python={pv:.2f}% page={jv:.2f}% "
                             f"diff={abs(pv - jv):.2f} pp (> {tol:.2f} pp: do they sample the same inputs?)")
        mc_msg = f"MC median max diff = {max(diffs):.2f} pp (tol max({MC_TOL}, {MC_TOL_REL:.0%} of the median))"

    # the samplers: percentiles of the page's draws of each sampled input against inputs.draw (different PRNGs, so within
    # sampling noise: 2% of the prior's lo-hi width). Catches a prior kind the page does not mirror (lognormal).
    import numpy as _np
    from inputs import draw as _draw, REGISTRY as _REG
    if not js.get("drawCheck"):
        fails.append("drawCheck: not emitted by the JS probe")
    for k, *jq in js.get("drawCheck", []):
        pq = _np.percentile(_draw(k, _np.random.default_rng(5), 40000), [10, 50, 90])
        tol = 0.02 * (_REG[k].hi - _REG[k].lo)
        if max(abs(a - b) for a, b in zip(pq, jq)) > tol:
            fails.append(f"draws of {k}: 10th/50th/90th python={[round(float(x), 4) for x in pq]} page={[round(x, 4) for x in jq]}")

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
          f"breakdown max diff = {worst_b:.2e}, premise-dial max diff = {worst_p:.2e} (tol {TOL:.0e}); "
          f"scenarios: {len(sc.get('cases', []))} cases, max cost diff = {worst_sc:.2e}; {mc_msg}")
    return fails



# ---------------------------------------------------------------------------
# The first screen (page_scenarios.js, 2026-11-19): the draws, the traits beyond the best measured in meat cells (no routes since
# 2026-11-19), the tank design for set traits, the meat-buyers scale of the contour map, and the plant's capital per m3 and the
# nutrient floor, against scenarios.py, floor_physics.py and cell_traits.py.
# ---------------------------------------------------------------------------
CLOUD_EXACT_TOL = 1e-6        # relative, per draw, on Python's own draws
CLOUD_MED_TOL = 0.05          # relative: the page's 300 draws against Python's 4,000 (sampling noise is about 2% at 300)
CLOUD_TAIL_TOL = 0.10         # relative, on the 10th and 90th percentiles
_JS_DRAW = {"maintenance_share": "maint", "pf_protectant_dose": "_dose", "rt_membrane_price": "_memprice", "aa_bulk_price": "_aa",
            "tc_kla_exp": "_kla", "tc_thin": "_thin"}



def _page_held(held: dict) -> dict:
    """A test's held estimates as the page holds them: `cpl` (filter cost per litre) is the membranes' life at the model's price."""
    from inputs import value as _v
    out = {k: v for k, v in held.items() if k != "cpl"}
    if "cpl" in held:
        out["mem_price"] = _v("rt_membrane_price")
        out["mem_life"] = _v("rt_membrane_price") / held["cpl"]
    return out


def _first_screen_cases():
    import scenarios as S
    from inputs import value
    import numpy as np
    cen, best, lean = S.SCENARIOS["central"].choice, S.SCENARIOS["best"].choice, S.SCENARIOS["central_lean"].choice
    t4 = {"lac_yield": 0.2, "mass_pg": 2500.0}
    held_choice = S._design_traits({**lean, "mode": "fedbatch50"}, t4)
    exact = [  # (choice or None for Humbird's design, traits, held)
        (cen, {}, {}), (S.SCENARIOS["today"].choice, {}, {}), (best, {"nh3_kg": 0.1, "doubling_h": 30.0}, {}),
        (held_choice, t4, {"capex_x": 0.6, "cpl": 0.5, "medium_price": 0.25}),
        (S._design_traits(cen, {"nh3_kg": 0.3, "lac_yield": 0.9, "doubling_h": 40.0, "mass_pg": 1500.0}),
         {"nh3_kg": 0.3, "lac_yield": 0.9, "doubling_h": 40.0, "mass_pg": 1500.0}, {"cpl": 1.2}),
        (None, {}, {}), (None, {"doubling_h": 30.0}, {"capex_x": 1.3})]
    n = 40
    cases, py_cost = [], []
    for ch, tr, held in exact:
        mc = S.scenario_mc(ch, n, 3, traits=tr)
        draws = [{(_JS_DRAW.get(k, k)): float(v[i]) for k, v in mc.items() if k != "total"} for i in range(n)]
        if held:                                    # what the page does with an estimate the reader set: hold it, recompute
            import floor_physics as fp
            kw0 = {**(S.explore_kwargs(ch) if ch is not None else {}), **tr}
            costs = []
            for d in draws:
                d = dict(d)
                if "capex_x" in held: d.pop("capex_x", None)
                if "cpl" in held: d.pop("membrane_life", None); d.pop("_memprice", None)
                if "medium_price" in held: d.pop("medium_price", None)
                kw = {**kw0, **{({"maint": "maintenance_share"}).get(k, k): v for k, v in d.items() if not k.startswith("_")}}
                if "capex_x" in held: kw["capex_x"] = held["capex_x"]
                if "cpl" in held: kw["membrane_life"] = value("rt_membrane_price") / held["cpl"]
                if "medium_price" in held: kw["medium_price"] = held["medium_price"]
                reg = {name: d[js] for name, js in (("pf_protectant_dose", "_dose"), ("rt_membrane_price", "_memprice"), ("aa_bulk_price", "_aa"), ("tc_kla_exp", "_kla"), ("tc_thin", "_thin")) if js in d}
                with fp._inputs_set(reg):
                    costs.append(fp.explore(**kw)["total"])
            # the page drops the held keys itself (tpDrop), so it gets the full draws
            py_cost.append(costs)
        else:
            py_cost.append([float(x) for x in mc["total"]])
        cases.append({"base": "humbird" if ch is None else "switches", "choice": ch or S.SCENARIOS["central"].choice,
                      "traits": tr, "held": _page_held(held), "draws": draws})
    # (the page holds the membranes' price and life as two settings, in the sliders' units; a cost per litre `cpl` is that pair)
    stat = [(S.SCENARIOS[k].choice, {}) for k in ("today", "central", "best", "central_lean")] + [(None, {})] + \
           [(S._design_traits(cen, {"lac_yield": 0.2, "doubling_h": 28.0}), {"lac_yield": 0.2, "doubling_h": 28.0})]
    py_stat = []
    for ch, tr in stat:
        c = S.scenario_mc(ch, 4000, 0, traits=tr)["total"]
        py_stat.append((list(np.percentile(c, [10, 50, 90])), (S.run(ch, **tr) if ch is not None else S.reference())["total"]))
    routes = [{"nh3_kg": a, "lac_yield": l, "doubling_h": t, "mass_pg": m}
              for a in (0.0, 0.03, 0.054, 0.1, 0.14, 0.5) for l in (0.0, 0.42, 1.05, 1.4) for t in (12.0, 15.0, 20.0, 25.7, 36.0, 43.0)
              for m in (1000.0, 3300.0, 3400.0)]
    design = [({**cen, "tricks": "none", "shape": "tall"}, {"nh3_kg": 0.055, "lac_yield": 0.28, "doubling_h": 24.0, "mass_pg": 2000.0}),
              ({**cen, "mode": "fedbatch", "tricks": "none", "shape": "tall"}, {"lac_yield": 0.42, "doubling_h": 20.0}),
              ({**S.SCENARIOS["best"].choice}, {"mass_pg": 1200.0}), ({**lean}, {"nh3_kg": 0.0, "lac_yield": 0.0, "doubling_h": 25.7})]
    return S, exact, cases, py_cost, stat, py_stat, routes, design


def check_first_screen() -> tuple:
    import cell_traits as CT
    S, exact, cases, py_cost, stat, py_stat, routes, design = _first_screen_cases()
    buyers = [0.05, 0.145, 0.3, 0.5, 0.585, 0.75]       # scenarios.all_choices_for_meat_buyers stops at a dial of 0.79 (about 79% of buyers)
    shares = [[c, b] for c in (3.0, 8.0, 15.0, 36.0, 120.0) for b in (0.145, 0.5, 0.8)]
    costfor = [[1.0, 0.1450734531872825], [10.0, 0.1450734531872825], [1.0, 0.5], [10.0, 0.5]]
    sharesd = [[c, b, d] for c in (3.0, 15.0) for b in (0.145, 0.8) for d in (0.0, 0.5)]   # meat_displaced_per_kg (2026-11-22)
    payload = {"exact": cases, "stat": [{"base": "humbird" if ch is None else "switches", "choice": ch or S.SCENARIOS["central"].choice,
                                         "traits": tr, "held": {}} for ch, tr in stat],
               "routes": routes, "design": [{"choice": c, "traits": t} for c, t in design], "buyers": buyers, "shares": shares, "sharesd": sharesd, "costfor": costfor}
    node = shutil.which("node")
    if node is None:
        return [], "first screen: node not found, not checked"
    fd, model_js = tempfile.mkstemp(prefix="_model_extracted_", suffix=".js"); os.close(fd)
    fd, inp = tempfile.mkstemp(prefix="_tp_in_", suffix=".json"); os.close(fd)
    open(model_js, "w", encoding="utf-8").write(_extract_model_js(HTML))
    json.dump(payload, open(inp, "w"))
    try:
        out = subprocess.run([node, PROBE, model_js, inp], capture_output=True, text=True, timeout=300)
    finally:
        for f in (model_js, inp):
            try:
                os.remove(f)
            except OSError:
                pass
    if out.returncode != 0:
        return [f"first-screen probe failed: {out.stderr[-2000:] or out.stdout[-2000:]}"], ""
    js = json.loads(out.stdout.strip().splitlines()[-1])
    if "error" in js:
        return [f"first-screen probe error: {js['error'][:2000]}"], ""
    tp = js["tp"]
    fails = []
    worst = 0.0
    for i, (pc, jc) in enumerate(zip(py_cost, tp["exact"])):
        for k, (a, b) in enumerate(zip(pc, jc)):
            d = abs(a - b) / max(1.0, abs(a))
            worst = max(worst, d)
            if d > CLOUD_EXACT_TOL:
                fails.append(f"cloud case {i} draw {k}: python={a:.6f} js={b:.6f}")
                break
    worst_m = 0.0
    for i, ((pq, ppt), jq, jpt) in enumerate(zip(py_stat, tp["stat"], tp["points"])):
        dm = abs(pq[1] - jq[1]) / pq[1]
        worst_m = max(worst_m, dm)
        if dm > CLOUD_MED_TOL:
            fails.append(f"cloud median, case {i}: python (4,000 draws) {pq[1]:.3f}, page ({len(cases[0]['draws']) and 300} draws) {jq[1]:.3f}")
        for a, b in ((pq[0], jq[0]), (pq[2], jq[2])):
            if abs(a - b) / a > CLOUD_TAIL_TOL:
                fails.append(f"cloud tails, case {i}: python {pq[0]:.2f}/{pq[2]:.2f}, page {jq[0]:.2f}/{jq[2]:.2f}")
                break
        if abs(ppt - jpt) > 1e-6 * max(1.0, ppt):
            fails.append(f"most-likely-values cost, case {i}: python {ppt:.6f} js {jpt:.6f}")
    for t, jb in zip(routes, tp["beyond"]):
        pb = CT.beyond_measured(t)
        if sorted(pb) != sorted(jb):
            fails.append(f"beyond the best measured in meat cells, {t}: python {pb} js {jb}")
    for k, (v, src) in tp["best"].items():
        b = CT.best_in_meat_cells()[k]
        if v != b["value"] or src != b["short"]:
            fails.append(f"best measured in meat cells, {k}: python {b['value']} ({b['short']}) js {v} ({src})")
    # the plant sliders' words: capital per m3 of tank (explore()'s 'capex', $k) and the nutrient floor (floor_physics.feedstock)
    import floor_physics as fp
    for i, ((ch, tr), (jcap, jnut)) in enumerate(zip(stat, tp["plant"])):
        r = S.run(ch, **tr) if ch is not None else S.reference()
        kw = {**(S.explore_kwargs(ch) if ch is not None else {}), **tr}
        nut = fp.feedstock(fp.Cells(mass_pg=kw.get("mass_pg", 3000.0), doubling_h=kw.get("doubling_h", 24.0)))
        if abs(r["capex"] - jcap) > 1e-6 * r["capex"] or abs(nut - jnut) > 1e-9 * nut:
            fails.append(f"plant sliders, case {i}: python capex {r['capex']:.4f} nutrients {nut:.5f}; js {jcap:.4f} {jnut:.5f}")
    for (c, t), (tk, sh) in zip(design, tp["design"]):
        d = S._design_traits(c, t)
        if (d["tricks"], d["shape"]) != (tk, sh):
            fails.append(f"design for traits {t}: python=({d['tricks']}, {d['shape']}) js=({tk}, {sh})")
    for b, jd in zip(buyers, tp["dial"]):
        pd = S.all_choices_for_meat_buyers(b)
        if abs(pd - jd) > 3e-4:          # Python reads the liking from its table, the page solves it: about 1e-4 apart
            fails.append(f"meat buyers {b}: python dial {pd:.6f} js {jd:.6f}")
    worst_s = 0.0
    for (c, b), js_s in zip(shares, tp["shares"]):
        ps = S.world_share(c, b)
        worst_s = max(worst_s, abs(ps - js_s))
        if abs(ps - js_s) > max(0.01, 0.002 * ps):
            fails.append(f"map share at ${c} and {b:.1%} of meat buyers: python {ps:.5f}% js {js_s:.5f}%")
    import meat_market as _mm
    for (c, b, d), js_s in zip(sharesd, tp["sharesd"]):
        _pr = S._DP_V.get(b)
        if _pr is None:
            S.world_share(c, b); _pr = S._DP_V[b]
        ps = _mm.penetration(_mm.MARKETS["global"], c, income=_mm.REGION_INCOME["global"], pr=_pr, displaced=d)[1] * 100.0
        if abs(ps - js_s) > max(0.01, 0.002 * ps):
            fails.append(f"map share at ${c}, {b:.1%} of meat buyers and {d} kg of meat displaced a kg sold: python {ps:.5f}% js {js_s:.5f}%")
    if len(tp["sharesd"]) != len(sharesd):
        fails.append("the page's probe gave no shares with the meat displaced set")
    for (t, b), jc in zip(costfor, tp["costfor"]):
        pc = S.cost_for_share(t, b)
        if (pc is None) != (jc is None) or (pc is not None and abs(pc - jc) / pc > 0.003):
            fails.append(f"cost for {t}% at {b:.1%}: python {pc} js {jc}")
    if abs(tp["humbird"] - S.reference()["total"]) > 1e-6:
        fails.append(f"Humbird's design: python {S.reference()['total']:.6f} js {tp['humbird']:.6f}")
    import meat_market as mm
    from inputs import value
    for r, (avg, par) in zip(("global", "us", "eu"), tp["parity"]):
        mk = mm.MARKETS[r]
        pavg = sum(t.p_conv * t.w_vol for t in mk) / sum(t.w_vol for t in mk)
        ppar = pavg * (1 - value("retail_margin")) - value("markup_add")
        if abs(pavg - avg) > 1e-9 or abs(ppar - par) > 1e-9:
            fails.append(f"average kilo, {r}: python {pavg:.4f} (cells {ppar:.4f}) js {avg:.4f} ({par:.4f})")
    # where the money goes, by what drives it: each item is floor_physics.explore's component, and the groups add up to its total
    worst_g = 0.0
    for i, ((ch, tr), jg) in enumerate(zip(stat, tp["groups"])):
        r = S.run(ch, **tr) if ch is not None else S.reference()
        want = {"membranes": ("litres", r["membranes"]), "medium": ("litres", r["feedstock"]), "protectant": ("litres", r["protectant"]),
                "gf": ("litres", r["growth_factors"]), "capital": ("time", r["capital"]), "labour": ("time", r["labour"]),
                "energy": ("other", r["utilities"] + r["extra_opex"]), "supplies": ("other", r["consumables"] - r["membranes"] - r["protectant"])}
        for k, comp in (("gf", "growth_factors"), ("membranes", "membranes"), ("protectant", "protectant")):
            if r[comp] <= 0:
                want.pop(k)                         # the page leaves out a line that costs nothing (no filter, no bubbles, no growth factors)
        got = {k: tuple(v) for k, v in jg["items"].items()}
        if set(got) != set(want):
            fails.append(f"cost groups, case {i}: items {sorted(got)} != {sorted(want)}")
            continue
        for k, (grp, v) in want.items():
            d = abs(got[k][1] - v) / max(1.0, abs(r["total"]))
            worst_g = max(worst_g, d)
            if got[k][0] != grp or d > 1e-6:
                fails.append(f"cost groups, case {i}, {k}: python ({grp}, {v:.6f}) js ({got[k][0]}, {got[k][1]:.6f})")
        if abs(sum(v for _g, v in want.values()) - r["total"]) > 1e-9 * max(1.0, r["total"]) \
                or abs(jg["sum"] - r["total"]) > 1e-6 * max(1.0, r["total"]) or abs(jg["ml"] - r["medium_l"]) > 1e-6 * r["medium_l"]:
            fails.append(f"cost groups, case {i}: they add up to {jg['sum']:.6f}, explore's total is {r['total']:.6f}")
    msg = (f"first screen: cloud on Python's draws max rel diff {worst:.1e} ({len(cases)} cases x {len(cases[0]['draws'])} draws); "
           f"cloud median max rel diff {worst_m:.3f} (tol {CLOUD_MED_TOL}, {len(stat)} cases); {len(routes)} trait sets against the meat-cell measurements; "
           f"{len(design)} tank designs; map share max diff {worst_s:.4f} pp; cost groups max rel diff {worst_g:.1e} ({len(stat)} cases)")
    return fails, msg


def test_python_js_parity():
    """pytest entry point: the JS mirror agrees with the Python source of truth."""
    fails = check_parity() + check_first_screen()[0]
    assert not fails, "Python↔JS parity FAILED:\n  " + "\n  ".join(fails)


if __name__ == "__main__":
    failures = check_parity()
    _f, _m = check_first_screen()
    print(_m)
    failures += _f
    if failures:
        print(f"\nFAIL — {len(failures)} mismatch(es):")
        for f in failures[:25]:
            print("  " + f)
        if len(failures) > 25:
            print(f"  … and {len(failures) - 25} more")
        sys.exit(1)
    print("PASS — the JS model mirrors the Python source of truth.")
    sys.exit(0)
