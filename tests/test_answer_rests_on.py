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
    if not s["cost_rows"] or s["cost_rows"][0]["key"] != "pf_nh3_limit":
        fails.append("the ammonia limit is no longer the largest driver of Central's cost; rewrite the summary")

    text = open(os.path.join(ROOT, "RESULTS.md"), encoding="utf-8").read()
    for line in (A.markdown_cost() + "\n" + A.markdown_demand()).splitlines():
        if line.strip() and line not in text:
            fails.append(f"RESULTS.md does not carry: {line[:90]}")
    cr = {r["key"]: r for r in s["cost_rows"]}
    cs, bs = s["central_share_span"], s["best_share_span"]
    quoted = [f"The model has {s['inputs']} inputs, {s['ranged']} of them with a range",
              f"only {len(s['cost_rows'])} move", f"and {s['over_3']} move Central by more than $3",
              
              f"{S.pct_num(cs[0])}–{S.pct_num(cs[1])}%", f"{bs[0]:.1f}–{bs[1]:.1f}%", f"above {S.pct_num(cs[1])}%"]
    for k in ("pf_nh3_limit", "rt_membrane_life", "pf_protectant_price", "pf_min_perfusion"):
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
