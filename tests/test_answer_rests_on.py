#!/usr/bin/env python3
"""test_answer_rests_on.py — the inputs the answer rests on (answer_rests_on.py).

Checks that the share helper reproduces the headline share, that every row the tables can show has a plain name, that the list
of inputs the bands draw matches the code that draws them, and that RESULTS.md carries both tables and the figures its prose
quotes, so a model change cannot leave the summary stale. Run directly or under pytest.
"""
from __future__ import annotations

import inspect
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import answer_rests_on as A  # noqa: E402
import inputs as I  # noqa: E402
import scenarios as S  # noqa: E402


def check() -> list:
    fails = []
    s = A.summary()
    if abs(A.share_at(s["central"]) - S.shares(s["central"])["global"]) > 1e-9:
        fails.append("share_at does not reproduce the headline share at the low-lactate example's cost")
    for r in s["cost_rows"] + s["demand_rows"]:
        if r["key"] not in A.PLAIN:
            fails.append(f"{r['key']}: no plain name")
    src = inspect.getsource(S.scenario_mc)
    for k in ("plant_charge_mature", "rt_membrane_life", "pf_maintenance_share"):
        if f'"{k}"' not in src:
            fails.append(f"{k} is listed as in the band but scenario_mc does not draw it")
    if "MC_ESTIMATES" not in src or "MC_ESTIMATE_INPUTS" not in src:
        fails.append("scenario_mc no longer draws MC_ESTIMATES; the table's band column is wrong")
    for k in ("markup_add", "retail_margin"):
        if k not in I.MC_COST_INPUTS:
            fails.append(f"{k} is listed as in the band but the demand draws do not include it")
    # 2026-11-19 audit batch: the scenarios' ammonia tolerance is the input sc_nh3_limit (pf_nh3_limit, Humbird's 5 mmol/L, no
    # longer moves them), and the scan now sees the scenarios' own settings. The largest driver of the low-lactate example's cost is no
    # longer the ammonia limit: it is the life of the cell filter (a lost run now throws its membranes away, and the low-lactate example
    # filters 30 litres a kilo, not 23), then the ammonia the cells tolerate, then the ammonia the low-lactate cells make.
    order = [r["key"] for r in s["cost_rows"]]
    if order[:3] != ["rt_membrane_life", "sc_nh3_limit", "sc_nh3_selected"]:
        fails.append(f"the three largest drivers of the low-lactate example's cost have changed ({order[:3]}); rewrite the summary")
    if "pf_nh3_limit" in order:
        fails.append("pf_nh3_limit should no longer move a scenario's cost (the scenarios pass sc_nh3_limit)")
    cr = {r["key"]: r for r in s["cost_rows"]}
    swing = lambda k: abs(cr[k]["central"][1] - cr[k]["central"][0])
    # Until 2026-11-20 the first three dwarfed the rest: each moved the low-lactate example by over $25 and the fourth (the
    # protectant's price) by under $10.
    # 2026-11-20 model batch: the first three are the same and larger ($54, $46 and $37), but three inputs now stand between them
    # and the protectant's price: the lactate the cells tolerate (new, 20-50 mmol/L: $22), the culture bursting bubbles kill
    # (new, now charged: $21) and the lactate the low-lactate cells make ($17: it did not reach $1 while lactate was tolerated
    # to 50 mmol/L; at 35, lactate sets the medium once the yield passes about 0.48 mol per mol of glucose). The protectant's
    # price is eighth, still under $10.
    # 2026-11-20 final model (the low-lactate example $49.50): the first three $50.0, $45.3 and $36.0; then the lactate
    # tolerated ($21.7), the lactate made ($16.8) and the bubble kill ($13.5): the last two swapped places, and the bubble
    # kill is now under $15 (the cage's gas no longer counts, and the other fixes of the day). The protectant's price is
    # still eighth, under $10.
    if not (min(swing(k) for k in order[:3]) > 35.0 and order[3:6] == ["sc_lac_limit", "sc_lac_selected", "ge_kill_protected"]
            and min(swing(k) for k in order[3:6]) > 12.0 and swing("pf_protectant_price") < 10.0
            and order.index("pf_protectant_price") == 7):
        fails.append("the first three drivers should each move the low-lactate example by over $35, then the lactate tolerated, the "
                     f"lactate made and the bubble kill by over $12 each, and the protectant's price (eighth) by under $10: {order[:8]}")
    # the new rows are there, with the band status the bands' code gives them
    # 2026-11-20: sc_p_top (the pressure of the extra pressure, 0.33-2 bar) is no longer a row. At 0.33 bar the trick adds
    # nothing, and at 2 bar the only pH-safe design is a squat tank, where the bubbles (now charged) kill more cells, so the
    # design drops the trick: both ends cost $50.91 against $49.96 at 1 bar, under the $1 threshold. Before, the squat tank at
    # 2 bar was the cheapest design ($31.7 against $32.8).
    # 2026-11-20 final model: sc_p_top is a row again. The extra pressure's design is chosen again at each end: at 0.33 bar
    # the low-lactate example costs $52.47 and at 2 bar $51.00, against $49.50 at 1 bar, both over the $1 threshold.
    # 2026-11-21: sc_p_top is no longer a row again. The design search now holds a culture thinner when its loop fails
    # (scenarios.design), so the low-lactate example's tank design is the column with recycled oxygen, held at 168 g/L, which
    # does not use the extra pressure: the pressure's range moves it by under $1. It keeps its reason for not being drawn
    if "sc_p_top" in cr or A._band("sc_p_top") != A.NOT_DRAWN["sc_p_top"]:
        fails.append("sc_p_top should not be a row (the thinned oxygen-column design does not use pressure), and stays marked as a design choice not drawn")
    # maturation (pf_mature_h, 0 to 28 days) is a choice of product, left out of the tables with a stated reason
    if "pf_mature_h" in cr or "pf_mature_h" not in A.EXCLUDE:
        fails.append("pf_mature_h should be left out of the tables, with its reason in EXCLUDE")
    # 2026-11-20 final model: sc_nh3_engineered (0.055, range 0.054-0.14) is no longer a row. The all-favourable example takes
    # the lower of it and Humbird's 0.054 (scenarios.all_favourable), so no value in its range moves that case, and the scan's
    # cases do not include rung 6 (whose lactate sets its litres anyway). A correct consequence of the case's definition.
    if "sc_nh3_engineered" in cr:
        fails.append("sc_nh3_engineered should not move a scanned case: the all-favourable example takes Humbird's 0.054")
    for k, band in (("sc_nh3_limit", "yes"), ("sc_nh3_selected", "yes"),
                    ("sc_mass_selected_pg", "yes"),   # drawn in the bands since 2026-11-19
                    ("sc_lac_limit", "yes"), ("ge_kill_protected", "yes")):   # new inputs, drawn in the bands since 2026-11-20
        if k not in cr:
            fails.append(f"{k} should move the low-lactate example's or the all-favourable example's cost by $1 or more")
        elif A._band(k) != band:
            fails.append(f"{k}: band status {A._band(k)!r}, expected {band!r}")
    if "sc_nh3_limit" not in S.MC_SCENARIO_PRIORS.values() or 'reg_draw("sc_nh3_selected")' not in src:
        fails.append("scenario_mc no longer draws the scenarios' ammonia tolerance or the ammonia the low-lactate cells make")
    # the low-lactate cells' traits do not move the all-favourable example (almost no ammonia or lactate), and the low-waste cells' do not move the low-lactate example
    # 2026-11-19 restructure: the weight of a cell is shared by every kind of cell, so it moves both cases now
    for k in ("sc_nh3_selected",):
        if k in cr and abs(cr[k]["best"][1] - cr[k]["best"][0]) > 1e-9:
            fails.append(f"{k} should not move the all-favourable example")
    if "sc_nh3_engineered" in cr and swing("sc_nh3_engineered") > 1e-9:
        fails.append("sc_nh3_engineered should not move the low-lactate example")
    dr = {r["key"]: r for r in s["demand_rows"]}
    # 2026-11-20 model batch: the shares fell to a quarter (the low-lactate example 0.21% -> 0.05%, the all-favourable example
    # 3.2% -> 1.1%), and the thresholds for a demand row are in percentage points (0.2 at the low-lactate example's cost, 2 at the
    # all-favourable example's). Six of the eight demand rows fell under them, the cut's make-up (scaffold_frac, process_cost)
    # among them: scaffold_frac moves the low-lactate example's share by 0.14 points and the all-favourable example's by 1.0.
    # They are still scanned and still drawn in the bands; the check no longer asks for them as rows.
    for k in ("scaffold_frac", "process_cost"):
        if k not in A.demand_inputs() or A._band(k) != "yes":
            fails.append(f"{k} should be a demand input the scan moves and the bands draw")
    # 2026-11-20 final model: the all-favourable example is now $7.62 (was $18.71) and its share 5.4% (was 1.1%), so ten
    # demand inputs move its share by 2 points or more again: 2 -> 10 rows.
    if [r["key"] for r in s["demand_rows"]][:2] != ["equal_price_share", "neophobia_x"] or len(s["demand_rows"]) != 14:   # 14 since 2026-11-22
        fails.append(f"the demand rows have changed: {[r['key'] for r in s['demand_rows']]}")
    # taste (accept_x) left the bands on 2026-11-20: it was drawn on top of the share at equal price, which already nets it
    if "accept_x" in I.MC_DEMAND_INPUTS or A._band("accept_x") == "yes" or "accept_x" not in A.demand_inputs():
        fails.append("accept_x should still be scanned but no longer be marked as drawn in the bands")
    if s["demand_rows"][0]["key"] != "equal_price_share":
        fails.append("the share at equal price is no longer the largest demand driver at the all-favourable example's cost")
    # the spread of liking (second round): both of its inputs are scanned, named, sourced and marked as not drawn; across
    # their fitted ranges neither moves the share enough to be a row (0.2 points at the low-lactate example's cost, 2 at the all-favourable example's)
    for k in ("liking_sd", "liking_tail"):
        if k not in A.demand_inputs():
            fails.append(f"{k} is not among the demand inputs the scan moves")
        if k not in A.PLAIN or k not in A.EVIDENCE or not A._band(k).startswith("no: "):
            fails.append(f"{k}: needs a plain name, a source and a reason it is not drawn")
        v = I.REGISTRY[k]
        c = [A.share_at(s["central"], **{k: e}) for e in (v.lo, v.hi)]
        b = [A.share_at(s["best"], **{k: e}) for e in (v.lo, v.hi)]
        if abs(c[1] - c[0]) >= A.SHARE_MIN[0] or abs(b[1] - b[0]) >= A.SHARE_MIN[1]:
            fails.append(f"{k} now moves the share enough to be a row; the summary should say so")
        if k in dr:
            fails.append(f"{k} is a demand row; check its line reads correctly")
    # 2026-11-22 (fifth batch): refitted with the price-insensitive shoppers, 3.9 and 4 -> 3.55 and 7
    if abs(I.REGISTRY["liking_sd"].value - 3.55) > 1e-9 or abs(I.REGISTRY["liking_tail"].value - 7.0) > 1e-9:
        fails.append("the liking spread is no longer sd 3.55 with 7 degrees of freedom; repin the shares")
    # the share at each scenario's own cost, % of world meat and seafood (0.0786 and 2.8149 with the normal spread)
    # 2026-11-20 final model: 0.0456 -> 0.0466 ($49.50) and 1.1345 -> 5.4388 ($7.62, the all-favourable case redefined)
    # 2026-11-21: 0.0466 -> 0.0496 ($49.50 -> $48.68) and 5.4388 -> 6.0674 ($7.62 -> $6.97: the thinned tank design, the building's
    # power by floor and class, the crew per tank)
    # 2026-11-21 (fourth batch): 0.0496 -> 0.0455 and 6.0674 -> 5.5816 (plant-based meat's committed buyers raise the ordinary
    # shoppers' real-meat weight, and with it the blend penalty on cuts; research_notes/demand_checks.md section 5)
    # 2026-11-22 (fifth batch, the price-insensitive shoppers): 0.0455 -> 0.2588 and 5.5816 -> 5.4798
    for name, got, want in (("the low-lactate example's share", s["central_share"], 0.2588), ("the all-favourable example's share, the low-lactate example's demand", s["best_share"], 5.4798)):
        # 2026-11-19 restructure: the share of the meat sold (was 0.1638 and 2.7352 as a share of all four choices; best also 2 ng)
        # 2026-11-20 model batch: 0.2102 -> 0.0456 and 3.1617 -> 1.1345 (the costs rose from $32.80 to $49.96 and $11.67 to $18.71)
        if abs(got - want) > 2e-3:
            fails.append(f"{name}: {got:.4f} != pinned {want}")
    # which demand input sets each end of the low-lactate example's span: the price elasticity of meat (low) and the price sensitivity of
    # cultivated meat (high); before the t spread the share at equal price set both ends
    lo_k = min(s["demand_rows"], key=lambda r: min(r["central"]))["key"]
    hi_k = max(s["demand_rows"], key=lambda r: max(r["central"]))["key"]
    # 2026-11-19 restructure: with the share of the meat sold the low end is now set by the share at equal price
    # 2026-11-20 model batch: with two demand rows left, the price sensitivity of cultivated meat sets both ends (0.33% at 4 times
    # meat's, 0.021% at 11 times); the share at equal price at its low end gives 0.024%, just above. The price elasticity of
    # meat would set a lower end still (0.020%), but its swing, 0.19 points, is just under the 0.2 a row needs.
    # 2026-11-20 final model: ten demand rows; the ends are 0.022% and 0.33%.
    # With ten rows the retailer's margin at its high end gives 0.0220%, just under the price sensitivity's 0.0222%, so it sets
    # the low end; the price sensitivity still sets the high end.
    # 2026-11-22 (fifth batch): the share at equal price sets both ends (0.056% and 1.56%)
    if (lo_k, hi_k) != ("equal_price_share", "equal_price_share"):
        fails.append(f"the ends of the low-lactate example's share span are now set by {lo_k} and {hi_k}; rewrite the summary")
    # pinned (2026-11-19 audit batch; before it 15 inputs moved a cost by $1 or more and 7 moved the low-lactate example by more than $3)
    # 2026-11-19: the retention study's aggregate and microcarrier inputs (16, 14 with a range) take 528 / 241 to 544 / 255
    # 2026-11-19 restructure: + pf_batch_end_x, pf_batch_half_x (ranged) and ten cr_* route levels (no range): 556 / 257
    # 2026-11-20 model batch: 566 / 263 (the batch's new inputs); 18 -> 25 cost rows, 11 -> 14 over $3, 16 -> 22 at $1 or more in
    # the low-lactate example (the costs rose by half, so more ranges cross the $1 line, and six rows are new inputs); demand
    # rows 8 -> 2 (the shares fell to a quarter and the thresholds are in percentage points)
    # 2026-11-20 final model: 591 inputs, 273 with a range (pf_mature_h, ranged, is left out); 25 cost rows, 14 over $3, all
    # 25 move the low-lactate example by $1 or more (new rows: tc_kla_exp, tc_thin, sc_p_top, pf_harvest_recovery, ...;
    # gone: rows under $1 since the fixes); 10 demand rows
    # 2026-11-21: 605 inputs, 276 with a range (new: the building's power by class, the crew per tank, two spargers, the column on
    # the filter loop, the Class 6 rate); 25 -> 19 cost rows, 14 -> 13 over $3, all 19 move the low-lactate example by $1 or more.
    # The six that fell under $1: antifoam's cost to oxygen transfer, tc_kla_exp, tc_thin, the upkeep share of a cell's oxygen and
    # sc_p_top (the cases' tank designs now feed recycled oxygen from the column, held thinner so its loop passes, and oxygen no
    # longer sets their density), and the harvest recovery (its 0.97-0.99 now moves the low-lactate example by just under $1)
    # 2026-11-21 (fourth batch): 611 inputs, 281 with a range (plant-based meat's committed buyers: pb_committed_share,
    # pb_committed_volume, pb_committed_price_x ranged, pb_committed_liking solved; repeat_rate and lapse_rate, ranged)
    # 2026-11-22 (fifth batch): 614 inputs, 284 with a range (the price-insensitive shoppers' three inputs); demand rows 10 -> 14 (the
    # three new inputs, and others that the higher share at the low-lactate example lifts over the thresholds)
    # 2026-11-22 (sixth batch): 615 inputs, 285 with a range (meat_displaced_per_kg; it moves no cost and is not a demand field,
    # so no row)
    pins = [("inputs", s["inputs"], 615), ("with a range", s["ranged"], 285),      # liking_tail added in the second round
            ("rows", len(s["cost_rows"]), 19), ("over $3", s["over_3"], 13),
            ("move the low-lactate example by $1 or more", sum(swing(k) >= 1.0 for k in order), 19),
            ("demand rows", len(s["demand_rows"]), 14)]   # 2026-11-19: 9 -> 8 with the share of the meat sold
    for name, got, want in pins:
        if got != want:
            fails.append(f"{name}: {got} != pinned {want}")
    # the low-lactate example's cost at each end of the range, $/kg (ammonia tolerance was $53.3 to $19.4 as pf_nh3_limit, filter life $54.8
    # to $24.1, protectant price $25.3 to $31.5, at the low-lactate example $26.43)
    # 2026-11-20 model batch, at the low-lactate example $49.96: filter life 76.30-29.22 -> 90.43-36.48, ammonia tolerated
    # 57.42-23.33 -> 91.41-44.97 (above 5 mmol/L lactate sets the medium, so the high end stops at $44.97), ammonia made
    # 23.59-52.14 -> 45.61-82.70, protectant price 31.40-39.10 -> 48.36-57.18, osmolality 38.42-32.80 -> 59.50-49.96; and the two
    # new inputs
    # 2026-11-20 final model, at the low-lactate example $49.50
    # 2026-11-21, at $48.68: filter life (87.00, 37.00) -> (86.91, 35.94), ammonia tolerated (89.91, 44.65) -> (89.05, 43.84),
    # ammonia made (45.27, 81.28) -> (44.46, 80.42), lactate tolerated (71.18, 49.50) -> (70.33, 48.68), bubble kill
    # (46.46, 59.93) -> (45.70, 58.94), protectant price (47.94, 56.49) -> (47.13, 55.67), osmolality (58.76, 49.50) -> (57.93, 48.68)
    # 2026-11-21, the protectant's price band $10-120 -> $5-100 (evidence_poloxamer_price.md): (47.13, 55.67) -> (46.74, 54.12)
    for k, want in (("rt_membrane_life", (86.91, 35.94)), ("sc_nh3_limit", (89.05, 43.84)), ("sc_nh3_selected", (44.46, 80.42)),   # low end 0.07 -> 0.04 (2026-11-19)
                    ("sc_lac_limit", (70.33, 48.68)), ("ge_kill_protected", (45.70, 58.94)),
                    ("pf_protectant_price", (46.74, 54.12)), ("pf_osm_limit", (57.93, 48.68))):
        if max(abs(a - b) for a, b in zip(cr[k]["central"], want)) > 0.02:
            fails.append(f"{k}: the low-lactate example {cr[k]['central'][0]:.2f} to {cr[k]['central'][1]:.2f} != pinned {want}")
    # the share's span across the demand rows, % of world meat and seafood
    # 2026-11-19, second round: shoppers' liking is a Student's t spread (liking_sd 3.9, liking_tail 4), so every share moved
    # and no cost did. The low-lactate example's span was 0.0090 to 1.0137 and the all-favourable example's 0.5178 to 16.8051 with the normal spread: the
    # heavier tail lifts the low end far above parity, and the narrower middle lowers the all-favourable example's top by a third.
    # 2026-11-19 restructure (the share of the meat sold; best's cells 2 ng): 0.0504-0.8093 -> 0.0847-0.9709, 0.7398-11.6982 -> 0.8788-12.8533
    # 2026-11-20 model batch: 0.0847-0.9709 -> 0.0214-0.3316, 0.8788-12.8533 -> 0.3534-4.7193 (across the two demand rows left)
    # 2026-11-20 final model: 0.0214-0.3316 -> 0.0220-0.3278; 0.3534-4.7193 -> 1.4718-19.7075 (ten demand rows)
    # 2026-11-21: 0.0220-0.3278 -> 0.0234-0.3429; 1.4718-19.7075 -> 1.6331-21.6175 (the costs above)
    # 2026-11-21 (fourth batch): 0.0234-0.3429 -> 0.0216-0.3103; 1.6331-21.6175 -> 1.5030-20.4019 (the blend penalty above)
    # 2026-11-22 (fifth batch, the price-insensitive shoppers): 0.0216-0.3103 -> 0.0559-1.5650; 1.5030-20.4019 -> 1.3387-21.8664
    for name, got, want in (("the low-lactate example's share span", s["central_share_span"], (0.0559, 1.5650)),
                            ("the all-favourable example's share span", s["best_share_span"], (1.3387, 21.8664))):
        if max(abs(a - b) for a, b in zip(got, want)) > 2e-3:
            fails.append(f"{name}: {got[0]:.4f} to {got[1]:.4f} != pinned {want}")

    text = open(os.path.join(ROOT, "RESULTS.md"), encoding="utf-8").read()
    for line in (A.markdown_cost() + "\n" + A.markdown_demand()).splitlines():
        if line.strip() and line not in text:
            fails.append(f"RESULTS.md does not carry: {line[:90]}")
    cs, bs = s["central_share_span"], s["best_share_span"]
    quoted = [f"The model has {s['inputs']} inputs, {s['ranged']} of them with a range",
              f"only {len(s['cost_rows'])} move", f"and {s['over_3']} move the low-lactate example by more than $3",
              
              f"{S.pct_num(cs[0])}–{S.pct_num(cs[1])}%", f"{bs[0]:.1f}–{bs[1]:.1f}%", f"above {S.pct_num(cs[1])}%"]
    # 2026-11-19 audit batch: the four the prose names are the four largest in the low-lactate example now: filter life, the ammonia the
    # cells tolerate, the ammonia they make, the protectant's price. The least medium flow fell to ninth ($3.5 in the low-lactate example).
    # 2026-11-20 model batch: the five largest are filter life, the ammonia tolerated, the ammonia made, the lactate tolerated and
    # the bubble kill; RESULTS.md's prose should name those five (the protectant's price is eighth).
    # 2026-11-20 final model: the fifth is now the lactate the low-lactate cells make, ahead of the bubble kill
    for k in ("rt_membrane_life", "sc_nh3_limit", "sc_nh3_selected", "sc_lac_limit", "sc_lac_selected"):
        quoted.append(f"(${cr[k]['central'][0]:.1f} to ${cr[k]['central'][1]:.1f})")
    for q in quoted:
        if q not in text:
            fails.append(f"RESULTS.md does not quote: {q}")
    return fails


def main() -> None:
    fails = check()
    if fails:
        print("FAIL — what the answer rests on:")
        for f in fails:
            print("  " + f)
        sys.exit(1)
    print("PASS — what the answer rests on holds.")


if __name__ == "__main__":
    main()
