#!/usr/bin/env python3
"""test_humbird_check.py — the engine at Humbird's own conditions gives Humbird's own numbers (humbird_check.py).

Pins, for the four columns of his Table 4.7 and his perfusion design (Table 4.13):
  * each total within 3% of his, and each cost line within 5% or $0.30 a kilo;
  * the lines that could not be closed from his report carry their residual as the tolerance (humbird_check.RESIDUALS, each
    with its reason), and the perfusion total carries 5%;
  * the density, the output per m3 of tank and the plant cost per m3 within 5%, the plant now the engine's own for all five
    designs (floor_physics.tank_items, 2026-11-20; his plant cost is no longer entered): the wild-type plants and the perfusion
    plant carry their residuals in humbird_check.RESIDUALS;
  * the page's start is his best estimate like for like in today's dollars (page_start), and the five additions that are levers
    of the page each add cost (or nothing, where they do not bind), alone and together (page_additions, page_with_additions); tests/test_easy_view.py checks that the
    page's own JavaScript gives the same figures;
  * the model's own version of his design (start: its own plant figure and supplies, every addition on), and the steps to it;
  * his figures as transcribed add up to his own totals, and the four parts of the utilities add up to his $0.94.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import floor_physics as fp
import humbird_check as HC
from inputs import value


def check() -> list:
    fails = []
    # --- his figures as transcribed: the lines add up to his totals (to his rounding)
    for case, h in HC.HIS.items():
        s = sum(h["lines"].values())
        if abs(s - h["total"]) > 0.03:
            fails.append(f"{case}: his lines add up to {s:.2f}, his total is {h['total']:.2f}")
    if abs(HC.HIS[HC.BEST]["total"] - 21.00) > 1e-9:
        fails.append("his best estimate is $21.00 a kilo (Table 4.7, enhanced cells on hydrolysate)")
    # --- the engine at his conditions, 2018 dollars
    for case in HC.ORDER:
        h = HC.HIS[case]
        for line, his, eng, gap, _today in HC.compare(case):
            tol = HC.tolerance(case, line)
            if line in HC.LINES and abs(eng - his) <= HC.LINE_ABS:
                continue
            if abs(gap) > tol:
                fails.append(f"{h['label']}, {line}: engine {eng:.2f} against his {his:.2f} ({gap:+.1%}, tolerance {tol:.0%})")
        # a residual that has closed should leave the list
        r = HC.reproduce(case, "2018")
        for (c, line), (tol, _why) in HC.RESIDUALS.items():
            if c == case and abs(r[line] / h["lines"].get(line, h.get(line)) - 1.0) <= HC.LINE_TOL:
                fails.append(f"{h['label']}, {line}: now within 5% of his; take it out of humbird_check.RESIDUALS")
    # --- today's dollars: the same case with both escalations on
    a, b = HC.reproduce(HC.BEST, "2018"), HC.reproduce(HC.BEST, "today")
    cx, ox = value("pf_capex_escalation"), value("pf_opex_escalation")
    if abs(b["capital"] / a["capital"] - cx) > 1e-6 or abs((b["total"] - b["capital"]) / (a["total"] - a["capital"]) - ox) > 1e-6:
        fails.append("today's dollars should be the 2018 lines times the two escalations")
    # --- the engine's own plant reproduces both his plants per m3 within about 5% (research_notes/humbird_backtest.md, item 7)
    for case, lo, hi in (("fb_hydro", -0.02, 0.01), ("pf_aa", -0.07, -0.05)):
        gap = HC.reproduce(case, "2018")["capex"] / HC.HIS[case]["capex"] - 1.0
        if not lo < gap < hi:
            fails.append(f"the engine's own plant for {case} is {gap:+.1%} against his: update the note and this pin")
    # --- how he counts the end of a batch
    if abs(HC.his_batch_end() - 1.0 / (1.0 - 482.0 / 1849.0)) > 1e-12 or not 1.3 <= HC.his_batch_end() <= 1.36:
        fails.append("his batch end, by the engine's count, should be 1 / (1 - 482/1,849) = 1.35")
    # --- utilities in four parts: at his fed-batch plant they are his $0.94
    out = fp.humbird_fedbatch_output()
    parts = (value("pf_util_time") + value("pf_util_run") * HC.BATCHES_YR / 24.0) / out \
        + value("pf_util_water") * HC.BATCH_L / HC.BATCH_KG + value("pf_util_kg")
    if abs(parts - value("pf_utilities")) > 0.01:
        fails.append(f"the four parts of the utilities give {parts:.3f} at his fed-batch plant, his table says {value('pf_utilities')}")
    if abs(out - 14.17) > 0.01:
        fails.append(f"his fed-batch plant makes 6.8 kTA from 480 m3 = 14.17 t per m3 a year, got {out:.2f}")
    if abs(value("pf_labour") * out * 480.0 / 1000.0 - 9.9) > 0.1:
        fails.append("the crew per m3 of tank should give his $9.9M a year for 480 m3 (Table 4.5)")
    # --- growth factors per litre: his fed-batch's own
    if abs(value("pf_growth_factors") / value("pf_medium_prep_l_kg") - 5800.0 / 16000.0) > 0.01:
        fails.append("growth factors per litre should be his $5,800 for a batch of 16,000 litres")
    # --- the page's start (2026-11-20): his best estimate like for like in today's dollars; the four additions are levers
    p0, p4, padd = HC.page_start(), HC.page_with_additions(), HC.page_additions()
    if abs(p0["total"] - b["total"]) > 1e-12 * b["total"]:
        fails.append(f"the page's start {p0['total']:.6f} should be the like-for-like figure in today's dollars {b['total']:.6f}")
    # the viscosity lever adds nothing at his fed-batch, whose 120 g/L is held by CO2, not oxygen. 2026-11-21: nor does the least
    # medium flow: in a tank that is not washed out its cap is 1.35 x 92 = 124 g/L at the end of a batch as he counts it (it added
    # $6.7 when it capped his batch at 92 g/L; research_notes/humbird_backtest.md, item 11)
    if [k for k, _n, _d in padd] != ["kla_exp", "min_perfusion", "killx", "harvest_loss", "protect_dose"] \
            or not all(d > 0.1 for k, _n, d in padd if k not in ("kla_exp", "min_perfusion")) \
            or not all(-1e-9 <= d < 0.05 for k, _n, d in padd if k in ("kla_exp", "min_perfusion")):
        fails.append(f"each of the page's additions should add cost when switched on alone (viscosity and least flow: none at 120 g/L): {padd}")
    if not p0["total"] + max(d for _k, _n, d in padd) < p4["total"] < p0["total"] + 1.2 * sum(d for _k, _n, d in padd):
        fails.append(f"the four additions together ({p4['total']:.2f}) should add about the sum of each alone ({[round(d, 2) for _k, _n, d in padd]})")
    if abs(p0["feedstock"] * p0["harvested_share"] - HC.page_nutrients_kg()) > 1e-9 or abs(p4["feedstock"] * p4["harvested_share"] - HC.page_nutrients_kg()) > 1e-9:
        fails.append("the page's start and its additions keep his nutrient cost for a kilo of cells grown")
    fin = HC.page_finance()
    if abs(fin["rate"] / 100.0 / (1.0 - (1.0 + fin["rate"] / 100.0) ** -fin["life"]) + fin["upkeep"] / 100.0 - value("humbird_plant_charge")) > 1e-12:
        fails.append("the page's three finance levers should give his yearly charge of 23.6%")
    # 2026-11-21: with the least-flow cap no longer holding both at 92 g/L they differ by how the end of a batch is counted: the
    # page keeps his count (1.35 x the level, no slowdown), with_additions the model's (1.3, the last doublings slower), so the
    # page's batch ends at 120 g/L and with_additions' at 116 ($30.49 against $31.28; within a cent before)
    wa = HC.with_additions(HC.BEST)["total"]
    if not 0.0 < wa - p4["total"] < 1.5:
        fails.append(f"the page with its additions ({p4['total']:.2f}) should be a little below with_additions ({wa:.2f}), which counts the end of a batch the model's way")
    # --- the model's own version of his best estimate: its own plant figure and supplies, every addition on
    kw, s = HC.start_kwargs(), HC.start()
    if kw["plant"] != "pharma" or kw["vm"].get("kind") != "cyclic" or kw["vessel_m3"] != 20.0 or kw["growth_factors"] != 1.0:
        fails.append(f"the start should be a fed-batch in 20 m3 tanks in the plant with clean rooms, growth factors bought: {kw}")
    if abs(kw["charge"] - 0.2357) > 1e-4:
        fails.append(f"the start's yearly charge should be 7.5% over 10 years plus 9% = 23.57%, got {kw['charge']:.4f}")
    grown = s["feedstock"] * s["harvested_share"]
    if abs(grown - HC.HIS[HC.BEST]["lines"]["nutrients"] * ox) > 0.02:
        fails.append(f"the start's medium should cost his ${HC.HIS[HC.BEST]['lines']['nutrients'] * ox:.2f} a kilo of cells grown, got {grown:.2f}")
    if grown <= fp.feedstock(fp.GOOD_CELLS):
        fails.append("his medium should cost more than the model's ingredients (else the start should use the ingredients)")
    add = HC.additions()
    like = HC.reproduce(HC.BEST, "today")["total"]
    if abs(add[0][1] - like) > 1e-9 or abs(add[-1][1] - s["total"]) > 1e-9 or abs(sum(d for _l, _t, d in add) - (s["total"] - like)) > 1e-9:
        fails.append("the steps from his design to the model's own version should begin at the like-for-like figure, end at it and add up")
    if not (s["total"] > like and all(d >= -1e-9 for _l, _t, d in add[2:])):
        fails.append("each of the model's additions should add cost to his design")
    # pinned: the like-for-like figure and the start (2026-11-20)
    for name, got, want in (("his best estimate like for like, 2018 dollars", a["total"], 20.65), ("the same in today's dollars", like, 26.99),
                            ("the page's start", p0["total"], 26.99), ("the page with its five additions on", p4["total"], 30.49),
                            ("the model's own version of his design", s["total"], 30.45)):
        # 2026-11-21: 37.38 -> 30.49 and 36.21 -> 30.45 (the least-flow cap times pf_batch_end_x in a tank not washed out)
        if abs(got - want) > 0.005 * want:
            fails.append(f"{name}: {got:.2f} != pinned {want}")
    # 2026-11-21: his perfusion plant's building power and crew, from the rules that closed the residuals
    bp = fp.building_power(2.0)
    his_bp = 2521.0 / 192.0 / (543.0 * 150.0 / 20.0 / 1000.0)          # Table 4.11 facility power per m3 over Table 4.4's
    if not (abs(fp.building_power(20.0) - 1.0) < 1e-12 and abs(bp / his_bp - 1.0) < 0.06):
        fails.append(f"building power at 2 m3 should be his perfusion plant's {his_bp:.2f} times his fed-batch's within 6%, got {bp:.2f}")
    if abs(fp.building_power(20.0, {"hall": "sanitary"}) - 0.218) > 0.01:
        fails.append("a sanitary hall should draw about 22% of a clean-room plant's building power (Table 3.2: 50 against 410 W/m2)")
    if abs(fp.crew_multiplier(20.0, False) - 1.0) > 1e-12 or abs(fp.crew_multiplier(20.0, True) - value("pf_labour_perfusion_x")) > 1e-12:
        fails.append("at 20 m3 the crew should be his fed-batch crew, and pf_labour_perfusion_x times it in perfusion")
    pr = HC.reproduce("pf_aa", "2018")
    if abs(pr["labour"] / HC.HIS["pf_aa"]["lines"]["labour"] - 1.0) > 0.02 or abs(pr["growth_factors"] / HC.HIS["pf_aa"]["lines"]["growth_factors"] - 1.0) > 0.05:
        fails.append(f"his perfusion design's labour and growth factors should close (got {pr['labour']:.2f}, {pr['growth_factors']:.2f})")
    md = HC.markdown()
    if "| Total | 21.00 |" not in md or "page's start" not in md:
        fails.append("the Markdown table should carry his total and the page's start")
    return fails


def test_humbird_check():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the engine reproduces Humbird's Table 4.7 and Table 4.13 at his conditions." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
