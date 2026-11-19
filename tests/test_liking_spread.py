#!/usr/bin/env python3
"""test_liking_spread.py — a spread of liking for cultivated meat across shoppers (liking_spread.py).

Checks that with no spread and no shift the share is the model's, that a spread fits the choice experiment's price response much
better than none, that the same fade of first-contact wariness gives far less than half the market once liking is spread, and that
the notes and RESULTS.md carry the module's tables and the figures their prose quotes. Runs as a script or under pytest.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import liking_spread as LS  # noqa: E402
import market_share as M  # noqa: E402
import scenarios as S  # noqa: E402


def check() -> list:
    fails = []
    pr = LS.demand()
    for R in (1.0, 2.0, 3.5):
        if abs(LS.share(R, 0.0, 0.0) - M.share(R, pr)) > 1e-12:
            fails.append("with no spread and no shift the share is not the model's")
    s = LS.summary()
    f = s["fit"]
    if not f["own"]["miss"] < 0.3 * f["none"]["miss"]:
        fails.append("a spread of liking no longer fits the experiment much better than none; rewrite the note")
    if not 3.0 <= s["sd"] <= 6.0:
        fails.append(f"the fitted spread ({s['sd']}) has left the range the experiment's own estimate implies; rewrite the note")
    if abs(LS.share(1.0, f["own"]["mu"], s["sd"], s["kappa"]) - LS.VANLOO_SHARE) > 1e-6:
        fails.append("the fitted mean does not give the experiment's 5% at equal price")
    lev = list(s["levels"].values())
    if not (lev[0]["parity"] < lev[1]["parity"] < 25.0 and lev[2]["parity"] > 40.0):
        fails.append("the three long-run readings no longer give about 5%, well under 25%, and about half at equal price; rewrite the note")
    for k in ("central", "best"):
        w = [r["world"][k] for r in lev]
        if w != sorted(w):
            fails.append(f"{k}: the world share should rise across the three readings")
        if not lev[1]["world"][k] < 4.0 * s["model"]["world"][k]:
            fails.append(f"{k}: the middle reading is no longer near the model's share; rewrite the note")
    if not 0.5 < lev[1]["curve"][3] / s["premium"][3] < 2.0:
        fails.append("the middle reading no longer lands near premium meats at twice the price; rewrite the note")

    quoted = [f"{lev[1]['parity']:.0f}%", f"{S.pct_num(lev[0]['world']['central'])}% to {S.pct_num(lev[2]['world']['central'])}%",
              f"{S.pct_num(lev[0]['world']['best'])}% to {S.pct_num(lev[2]['world']['best'])}%"]
    for name, tables in (("research_notes/liking_spread.md", [LS.markdown_fit(), LS.markdown_levels()]), ("RESULTS.md", [LS.markdown_levels()])):
        text = open(os.path.join(ROOT, name), encoding="utf-8").read()
        for line in "\n".join(tables).splitlines():
            if line.strip() and line not in text:
                fails.append(f"{name} does not carry: {line[:90]}")
        for q in quoted:
            if q not in text:
                fails.append(f"{name} does not quote {q}")
    return fails


def test_liking_spread():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    if fails:
        sys.exit(1)
    print("liking spread: all checks passed")
