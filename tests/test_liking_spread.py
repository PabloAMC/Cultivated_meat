#!/usr/bin/env python3
"""test_liking_spread.py — a spread of liking for cultivated meat across shoppers (liking_spread.py).

Checks that with no spread and no shift the share is the model's, that a spread fits the choice experiment's price response much
better than none, that the same fade of first-contact wariness gives far less than half the market once liking is spread, and that
the notes and RESULTS.md carry the module's tables and the figures their prose quotes. Since 2026-11-19 also the shape of the spread
(market_share.spread_quadrature): that every shape's nodes are a standardised distribution, that the normal shape with a spread of
5 is still the model of 2026-11-18 to the last digit, and that the model's integration rule is within 1% of a 20,001-point
reference. Runs as a script or under pytest.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np  # noqa: E402

import liking_spread as LS  # noqa: E402
import market_share as M  # noqa: E402
import scenarios as S  # noqa: E402


# the model of 2026-11-18 (a normal spread of 5 utils on fifteen Gauss-Hermite nodes): its share at 1, 2 and 4 times meat's price
NORMAL_2026_11_18 = {1.0: 0.13000000000010429, 2.0: 0.037927474907962924, 4.0: 0.0011968020247303283}


def check_shape() -> list:
    """The shape of the spread: nodes and weights, the normal shape's exact reproduction, and the integration rule's accuracy."""
    fails = []
    x, w = np.polynomial.hermite_e.hermegauss(15)
    z, wz = M.spread_quadrature("normal")
    if not (np.array_equal(z, x) and np.array_equal(wz, w / w.sum())):
        fails.append("the normal shape no longer uses the fifteen Gauss-Hermite nodes of the 2026-11-18 model")
    for fam, tail in (("normal", 0.0), ("student", 4.0), ("student", 3.0), ("logistic", 0.0), ("mixture", 3.0)):
        z, wz = M.spread_quadrature(fam, tail, 0.05)
        var = float((wz * z * z).sum())
        if abs(wz.sum() - 1.0) > 1e-12 or abs(float((wz * z).sum())) > 1e-9 or not 0.95 < var < 1.0 + 1e-9:   # a heavy tail keeps a little variance beyond the last node
            fails.append(f"{fam}: the nodes are not a standardised distribution (weights {wz.sum()}, variance {var})")
    old = LS.variant(liking_family="normal", liking_sd=5.0)
    for R, v in NORMAL_2026_11_18.items():
        if abs(M.share(R, old) - v) > 1e-12:
            fails.append(f"the normal shape with a spread of 5 no longer reproduces the 2026-11-18 model at {R:g} times the price")
    pr = LS.demand()
    if pr.liking_family != "normal":
        err = LS.quadrature_error(pr.spread, liking_family=pr.liking_family, liking_sd=pr.liking_sd, liking_tail=pr.liking_tail)
        if err > 0.01:
            fails.append(f"the model's integration rule is {err:.1%} from the 20,001-point reference at 1 to 5 times the price")
    for R in (1.0, 2.5):
        if abs(M.share(R, pr, liking_sd=0.0) - M.share(R, LS.variant(liking_family="normal"), liking_sd=0.0)) > 1e-15:
            fails.append("with no spread the share depends on the shape of the spread")
    return fails


def check() -> list:
    fails = check_shape()
    pr = LS.demand()
    for R in (1.0, 2.0, 3.5):
        if abs(LS.share(R, 0.0, 0.0) - M.share(R, pr, liking_sd=0.0)) > 1e-12:
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
        if abs(lev[1]["world"][k] / s["default"]["world"][k] - 1.0) > 0.1:
            fails.append(f"{k}: the middle reading is no longer the model's default; rewrite the note")
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
