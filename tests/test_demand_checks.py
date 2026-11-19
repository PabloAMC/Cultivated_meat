#!/usr/bin/env python3
"""test_demand_checks.py — the model's response to price against four measurements (demand_checks.py).

Checks that the model's plant-based elasticity, cultivated elasticity and premium slope are computed and stand where the note says
(too strong against three measurements, inside the fourth), that a weaker response raises Central's share, and that the note and
RESULTS.md carry the module's tables and the figures their prose quotes. Runs as a script or under pytest.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import demand_checks as D  # noqa: E402
import market_size_loop as L  # noqa: E402
import scenarios as S  # noqa: E402


def check() -> list:
    fails = []
    s = D.summary()
    if not s["pb"]["elasticity"] < 1.5 * D.PB_ELASTICITY_MEASURED:
        fails.append("plant-based meat's elasticity in the model is no longer well above the measured one; rewrite the note")
    if abs(s["pb"]["share"] - 1.2) > 0.01:
        fails.append("plant-based meat's share in the check is not the calibrated 1.2%")
    v = s["variants"]
    if not abs(v[0]["cold"] - D.VANLOO_AT_PARITY) < 0.3 or not v[1]["cold"] < 1.5 * D.VANLOO_AT_PARITY:
        fails.append("the model should match the experiment's first-contact elasticity and the model before should not; rewrite the note")
    i3 = D.R_GRID.index(3.0)
    if not (0.4 * s["premium_3x"] < v[0]["curve"][i3] < 2.0 * s["premium_3x"] and v[1]["curve"][i3] < 0.2 * s["premium_3x"]):
        fails.append("at 3 times the price the model should be near premium meats and the model before far below; rewrite the note")
    for k in D.SCEN:
        if abs(v[0]["world"][k] - s["model_world"][k]) > 1e-9:
            fails.append(f"{k}: the first variant is not the model's own share")
    if not v[1]["world"]["central"] < v[0]["world"]["central"] < v[2]["world"]["central"] < v[3]["world"]["central"]:
        fails.append("the order of Central's share across the price responses has changed; rewrite the note")
    u = [L.underused(S.SCENARIOS["central"].choice, x)["cost"] for x in L.UTILISATION]
    if u != sorted(u) or abs(u[0] - S.run(S.SCENARIOS["central"].choice)["total"]) > 1e-9:
        fails.append("the cost of an under-used plant should rise as less is sold, from the scenario's own cost")

    quoted = [f"{s['pb']['elasticity']:.2f}", f"{S.pct_num(v[0]['world']['central'])}%", f"{S.pct_num(v[0]['world']['best'])}%",
              f"{S.pct_num(v[1]['world']['central'])}% to {S.pct_num(v[3]['world']['central'])}%"]
    for name, tables in (("research_notes/demand_checks.md", [D.markdown_checks(), D.markdown_variants(), L.markdown_underused()]),
                         ("RESULTS.md", [D.markdown_checks()])):
        text = open(os.path.join(ROOT, name), encoding="utf-8").read()
        for line in "\n".join(tables).splitlines():
            if line.strip() and line not in text:
                fails.append(f"{name} does not carry: {line[:90]}")
        for q in quoted:
            if q not in text:
                fails.append(f"{name} does not quote {q}")
    return fails


def test_demand_checks():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    if fails:
        sys.exit(1)
    print("demand checks: all checks passed")
