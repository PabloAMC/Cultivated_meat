#!/usr/bin/env python3
"""test_liking_spread.py — a spread of liking for cultivated meat across shoppers (liking_spread.py).

Checks that with no spread and no shift the share is the model's, that a spread fits the choice experiment's price response much
better than none, that the same fade of first-contact wariness gives far less than half the market once liking is spread, and that
the notes and RESULTS.md carry the module's tables and the figures their prose quotes. Since 2026-11-19 also the shape of the spread
(market_share.spread_quadrature): that every shape's nodes are a standardised distribution, that the normal shape with a spread of
5 is still the model of 2026-11-18 to the last digit, and that the model's integration rule is within 1% of a 20,001-point
reference; and what the note says of the shapes: their order by joint misfit, that the model's two parameters are within 20% of the
least misfit, that farmed salmon's response still fails, and that the Engineered cells, all favourable case falls by about a third. Runs as a script or under
pytest.
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
    fam = LS.families()
    if not (lev[0]["parity"] < lev[1]["parity"] < 25.0 and lev[2]["parity"] > 40.0):
        fails.append("the three long-run readings no longer give about 5%, well under 25%, and about half at equal price; rewrite the note")
    for k in ("central", "best"):
        w = [r["world"][k] for r in lev]
        if w != sorted(w):
            fails.append(f"{k}: the world share should rise across the three readings")
        # 2026-11-19 second round (Student's t spread): fading the model's first-contact wariness from the measured 5% now gives 15%
        # at equal price, not 13%. The setting stays at 13% (a judgement), so the middle reading's world share is a little ABOVE
        # the default's: 0.18% against 0.16% for Selected cells, 3.2% against 2.7% for the Engineered cells, all favourable case's cells. (Was: within 10% of it.)
        if not 1.0 < lev[1]["world"][k] / s["default"]["world"][k] < 1.25:
            fails.append(f"{k}: the middle reading is no longer a little above the model's default; rewrite the note")
    if not 0.5 < lev[1]["curve"][3] / s["premium"][3] < 2.0:
        fails.append("the middle reading no longer lands near premium meats at twice the price; rewrite the note")
    if not (14.5 < lev[1]["parity"] < 15.5 and 4.0 < fam["Student's t (the model)"]["first"] < 4.6):
        fails.append("the middle reading is no longer 15% at equal price, or the model's 13% no longer reads back as about 4.3% at "
                     "first contact; rewrite the note")
    # 2026-11-19 second round: what the note says of the shapes (liking_spread.families). The t fits better than the normal and the
    # logistic; the mixture fits better still and was not chosen (two extra parameters, a price-insensitive block); the normal
    # integrated properly fails the requirements; farmed salmon's response still fails; the Engineered cells, all favourable case falls by about a third.
    J = {n: m["J"] for n, m in fam.items()}
    t_, mix, nrm = "Student's t (the model)", "mixture of two normals", "normal, as it was (15 integration points)"
    if not (J[mix] < J[t_] < J["logistic"] < J[nrm] and fam[t_]["meets"] and not fam["normal, integrated properly"]["meets"]):
        fails.append("the shapes no longer rank mixture, Student's t, logistic, normal by joint misfit, or the normal integrated "
                     "properly now meets the requirements; rewrite the note's section 2")
    if not min(fam[t_]["response"].values()) > 2.0 * LS._salmon_range()[1]:
        fails.append("the model's response to a falling price is no longer more than twice farmed salmon's; rewrite the note's section 6")
    if not 0.6 < fam[t_]["world"]["best, own demand"] / fam[nrm]["world"]["best, own demand"] < 0.75:
        fails.append("the Engineered cells, all favourable case with its own demand no longer falls by about a third against the normal spread; rewrite the note")
    # the note: a tail of 3 with a spread of 3.7 has the least joint misfit; the model's 4 and 3.9 are within 20% of it
    least = LS.evaluate(liking_family="student", liking_sd=3.7, liking_tail=3.0)
    if not (least["meets"] and least["J"] < J[t_] < 1.2 * least["J"]):
        fails.append("the model's spread and tail are no longer within 20% of the least joint misfit (tail 3, spread 3.7); rewrite the note")

    quoted = [f"{lev[1]['parity']:.0f}%", f"{S.pct_num(lev[0]['world']['central'])}% to {S.pct_num(lev[2]['world']['central'])}%",
              f"{S.pct_num(lev[0]['world']['best'])}% to {S.pct_num(lev[2]['world']['best'])}%"]
    tw = fam[t_]["world"]
    note_only = [f"{tw['best, own demand']:.1f}%", f"{fam[nrm]['world']['best, own demand']:.1f}%", f"{fam[t_]['first']:.1f}%",
                 f"{min(fam[t_]['response'].values()):.1f}–{max(fam[t_]['response'].values()):.1f}"]
    for name, tables in (("research_notes/liking_spread.md", [LS.markdown_fit(), LS.markdown_levels(), LS.markdown_families()]),
                         ("RESULTS.md", [LS.markdown_levels()])):
        text = open(os.path.join(ROOT, name), encoding="utf-8").read()
        for line in "\n".join(tables).splitlines():
            if line.strip() and line not in text:
                fails.append(f"{name} does not carry: {line[:90]}")
        for q in quoted + (note_only if name.startswith("research") else []):
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
