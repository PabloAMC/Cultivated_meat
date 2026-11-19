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
        fails.append("share_at does not reproduce the headline share at Central's cost")
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
    # longer moves them), and the scan now sees the scenarios' own settings. The largest driver of Central's cost is no
    # longer the ammonia limit: it is the life of the cell filter (a lost run now throws its membranes away, and Central
    # filters 30 litres a kilo, not 23), then the ammonia the cells tolerate, then the ammonia the selected cells make.
    order = [r["key"] for r in s["cost_rows"]]
    if order[:3] != ["rt_membrane_life", "sc_nh3_limit", "sc_nh3_selected"]:
        fails.append(f"the three largest drivers of Central's cost have changed ({order[:3]}); rewrite the summary")
    if "pf_nh3_limit" in order:
        fails.append("pf_nh3_limit should no longer move a scenario's cost (the scenarios pass sc_nh3_limit)")
    cr = {r["key"]: r for r in s["cost_rows"]}
    swing = lambda k: abs(cr[k]["central"][1] - cr[k]["central"][0])
    # the first three dwarf the rest: each moves Central by over $25, and the fourth (the protectant's price) by under $10
    if not (min(swing(k) for k in order[:3]) > 25.0 and swing(order[3]) < 10.0 and order[3] == "pf_protectant_price"):
        fails.append("the first three drivers should each move Central by over $25 and the fourth by under $10")
    # the new rows are there, with the band status the bands' code gives them
    for k, band in (("sc_nh3_limit", "yes"), ("sc_nh3_selected", "yes"), ("sc_nh3_engineered", A.NOT_DRAWN["sc_nh3_engineered"]),
                    ("sc_mass_selected_pg", A.NOT_DRAWN["sc_mass_selected_pg"]), ("sc_p_top", A.NOT_DRAWN["sc_p_top"])):
        if k not in cr:
            fails.append(f"{k} should move Central's or the best case's cost by $1 or more")
        elif A._band(k) != band:
            fails.append(f"{k}: band status {A._band(k)!r}, expected {band!r}")
    if "sc_nh3_limit" not in S.MC_SCENARIO_PRIORS.values() or 'reg_draw("sc_nh3_selected")' not in src:
        fails.append("scenario_mc no longer draws the scenarios' ammonia tolerance or the ammonia the selected cells make")
    # the selected cells' traits do not move the best case (engineered cells), and the engineered cells' do not move Central
    for k in ("sc_nh3_selected", "sc_mass_selected_pg"):
        if k in cr and abs(cr[k]["best"][1] - cr[k]["best"][0]) > 1e-9:
            fails.append(f"{k} should not move the best case")
    if "sc_nh3_engineered" in cr and swing("sc_nh3_engineered") > 1e-9:
        fails.append("sc_nh3_engineered should not move Central")
    dr = {r["key"]: r for r in s["demand_rows"]}
    for k in ("scaffold_frac", "process_cost"):
        if k not in dr or A._band(k) != "yes":
            fails.append(f"{k} should be a demand row that the bands draw")
    if s["demand_rows"][0]["key"] != "equal_price_share":
        fails.append("the share at equal price is no longer the largest demand driver at the best case's cost")
    # the spread of liking (second round): both of its inputs are scanned, named, sourced and marked as not drawn; across
    # their fitted ranges neither moves the share enough to be a row (0.2 points at Central's cost, 2 at the best case's)
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
    if abs(I.REGISTRY["liking_sd"].value - 3.9) > 1e-9 or abs(I.REGISTRY["liking_tail"].value - 4.0) > 1e-9:
        fails.append("the liking spread is no longer sd 3.9 with 4 degrees of freedom; repin the shares")
    # the share at each scenario's own cost, % of world meat and seafood (0.0786 and 2.8149 with the normal spread)
    for name, got, want in (("Central's share", s["central_share"], 0.1638), ("the best case's share, Central's demand", s["best_share"], 2.7352)):
        if abs(got - want) > 2e-3:
            fails.append(f"{name}: {got:.4f} != pinned {want}")
    # which demand input sets each end of Central's span: the price elasticity of meat (low) and the price sensitivity of
    # cultivated meat (high); before the t spread the share at equal price set both ends
    lo_k = min(s["demand_rows"], key=lambda r: min(r["central"]))["key"]
    hi_k = max(s["demand_rows"], key=lambda r: max(r["central"]))["key"]
    if (lo_k, hi_k) != ("eps_own", "cult_sub_mult"):
        fails.append(f"the ends of Central's share span are now set by {lo_k} and {hi_k}; rewrite the summary")
    # pinned (2026-11-19 audit batch; before it 15 inputs moved a cost by $1 or more and 7 moved Central by more than $3)
    pins = [("inputs", s["inputs"], 528), ("with a range", s["ranged"], 241),      # liking_tail added in the second round
            ("rows", len(s["cost_rows"]), 18), ("over $3", s["over_3"], 11),
            ("move Central by $1 or more", sum(swing(k) >= 1.0 for k in order), 16),
            ("demand rows", len(s["demand_rows"]), 9)]
    for name, got, want in pins:
        if got != want:
            fails.append(f"{name}: {got} != pinned {want}")
    # Central's cost at each end of the range, $/kg (ammonia tolerance was $53.3 to $19.4 as pf_nh3_limit, filter life $54.8
    # to $24.1, protectant price $25.3 to $31.5, at Central $26.43)
    for k, want in (("rt_membrane_life", (76.30, 29.22)), ("sc_nh3_limit", (57.42, 23.33)), ("sc_nh3_selected", (23.50, 52.14)),
                    ("pf_protectant_price", (31.40, 39.10)), ("pf_osm_limit", (38.42, 32.80))):
        if max(abs(a - b) for a, b in zip(cr[k]["central"], want)) > 0.02:
            fails.append(f"{k}: Central {cr[k]['central'][0]:.2f} to {cr[k]['central'][1]:.2f} != pinned {want}")
    # the share's span across the demand rows, % of world meat and seafood
    # 2026-11-19, second round: shoppers' liking is a Student's t spread (liking_sd 3.9, liking_tail 4), so every share moved
    # and no cost did. Central's span was 0.0090 to 1.0137 and the best case's 0.5178 to 16.8051 with the normal spread: the
    # heavier tail lifts the low end far above parity, and the narrower middle lowers the best case's top by a third.
    for name, got, want in (("Central's share span", s["central_share_span"], (0.0504, 0.8093)),
                            ("the best case's share span", s["best_share_span"], (0.7398, 11.6982))):
        if max(abs(a - b) for a, b in zip(got, want)) > 2e-3:
            fails.append(f"{name}: {got[0]:.4f} to {got[1]:.4f} != pinned {want}")

    text = open(os.path.join(ROOT, "RESULTS.md"), encoding="utf-8").read()
    for line in (A.markdown_cost() + "\n" + A.markdown_demand()).splitlines():
        if line.strip() and line not in text:
            fails.append(f"RESULTS.md does not carry: {line[:90]}")
    cs, bs = s["central_share_span"], s["best_share_span"]
    quoted = [f"The model has {s['inputs']} inputs, {s['ranged']} of them with a range",
              f"only {len(s['cost_rows'])} move", f"and {s['over_3']} move Central by more than $3",
              
              f"{S.pct_num(cs[0])}–{S.pct_num(cs[1])}%", f"{bs[0]:.1f}–{bs[1]:.1f}%", f"above {S.pct_num(cs[1])}%"]
    # 2026-11-19 audit batch: the four the prose names are the four largest in Central now: filter life, the ammonia the
    # cells tolerate, the ammonia they make, the protectant's price. The least medium flow fell to ninth ($3.5 in Central).
    for k in ("rt_membrane_life", "sc_nh3_limit", "sc_nh3_selected", "pf_protectant_price"):
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
