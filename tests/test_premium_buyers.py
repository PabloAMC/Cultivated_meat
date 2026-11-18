#!/usr/bin/env python3
"""test_premium_buyers.py — cultivated meat competing with welfare labels for premium buyers (premium_buyers.py).

Checks that the five-product model reduces to the main model with no premium buyers and no label, that with no cultivated meat the
label's share is the fitted premium curve, that a label on the shelf takes share from cultivated meat and a higher value of no killing
adds to it, and that the note and RESULTS.md carry the module's tables and the figures their prose quotes. Runs as a script or under
pytest.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import market_share as M  # noqa: E402
import premium_buyers as B  # noqa: E402
import premium_curve as P  # noqa: E402


def check() -> list:
    fails = []
    pr = P.demand()
    p0 = {"kappa": pr.cult_sub_mult, "v": 0.0, "pi": 0.0, "v_l": 0.0, "kappa_l": 1.0}
    for R in (1.0, 2.0, 3.7):
        if abs(B.shares(R, p0, R_L=None, tier_offset=0.3, p_ref=9.0)["x"] - M.share(R, pr, tier_offset=0.3, p_ref=9.0, premium_share=0.0)) > 1e-12:
            fails.append(f"with no premium buyers and no label the share at R={R} is not the main model's")
    f = B.fit_at(B.PI_CENTRAL)["params"]
    for R in (1.5, 2.0, 3.0):
        if abs(B.shares(1.0, f, R_L=R, cultivated=False)["L"] - P.curve(R, f)) > 1e-12:
            fails.append(f"with no cultivated meat the label's share at R={R} is not the fitted premium curve")
    tot = sum(v for k, v in B.shares(5.85, f, d=B.d_for(0.05), p_ref=9.0).items() if k != "x_premium")
    if abs(tot - 1.0) > 1e-9:
        fails.append("the five shares do not add to 1")

    s = B.summary()
    for k in B.SCEN:
        if not s["grid"][(k, 0.05)]["share"] < s["no_label"][k]:
            fails.append(f"{k}: a label on the shelf should take share from cultivated meat")
        shares = [s["grid"][(k, nk)]["share"] for nk in B.NO_KILLING_CASES]
        if shares != sorted(shares):
            fails.append(f"{k}: the share should rise with the value of no killing")
        # since 2026-11-18 the model itself has premium buyers: it is this study's case with no label on the shelf
        if abs(s["no_label"][k] - s["model"][k]) > 0.02 * s["model"][k]:
            fails.append(f"{k}: the study with no label on the shelf is no longer the model's own share; rewrite the note")
    rms = [f["rms_log_error"] for f in s["fits"].values()]
    if max(rms) - min(rms) > 0.02:
        fails.append("the fits now tell the premium-buyer shares apart; the note says they do not")

    g = s["grid"]
    quoted = [f"{s['model']['central']:.2f}%", f"{g[('central', 0.05)]['share']:.2f}%", f"{g[('central', 1.0)]['share']:.2f}%",
              f"{s['model']['best']:.2f}%", f"{g[('best', 0.05)]['share']:.2f}%", f"{g[('best', 1.0)]['share']:.2f}%",
              f"{g[('central', 0.05)]['from_label']:.0%}", f"{g[('central', 1.0)]['from_label']:.0%}"]
    for name, tables in (("research_notes/premium_buyers.md", [B.markdown_fits(), B.markdown_shares(), B.markdown_pi()]),
                         ("RESULTS.md", [])):
        text = open(os.path.join(ROOT, name), encoding="utf-8").read()
        for line in "\n".join(tables).splitlines():
            if line.strip() and line not in text:
                fails.append(f"{name} does not carry: {line[:90]}")
        for q in quoted:
            if q not in text:
                fails.append(f"{name} does not quote {q}")
    return fails


def test_premium_buyers():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    if fails:
        sys.exit(1)
    print("premium buyers: all checks passed")
