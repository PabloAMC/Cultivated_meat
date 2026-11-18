#!/usr/bin/env python3
"""test_premium_curve.py — cultivated meat anchored on premium real meats (premium_curve.py).

Checks that the switch added to the demand code leaves the default unchanged, that the fits respect the measured at-parity elasticity
and beat the main model's curve on the premium products, and that the note and RESULTS.md carry the module's tables and the figures
their prose quotes. Runs as a script or under pytest.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import market_share as M  # noqa: E402
import premium_curve as P  # noqa: E402


def check() -> list:
    fails = []
    pr = P.demand()
    for R in (1.0, 1.9, 3.0):
        if M.share(R, pr) != M.share(R, pr, slaughter_free_x=1.0):
            fails.append("slaughter_free_x=1 is not the default behaviour")
    s = P.summary()
    for name, fits in s["fits"].items():
        for k, f in fits.items():
            if not f["respects_lusk"]:
                fails.append(f"{name}, {k}: at-parity elasticity {f['elasticity']:.2f} outside the measured range")
        if not fits["one"]["rms_log_error"] < s["model_rms"][name]:
            fails.append(f"{name}: the fit does no better than the main model's curve")
    lr = "long run, central"
    if not 0.5 * s["model_share"]["central"] < s["shares"]["central"][lr] < 2.0 * s["model_share"]["central"]:   # since premium buyers
        fails.append("Central's anchored share is no longer within a factor of 2 of the model's; rewrite the note's conclusion")
    if not s["shares"]["best"][lr] < s["model_share"]["best"]:
        fails.append("the best case's anchored share is no longer below the model's; rewrite the note's conclusion")

    sh, unf, fav = s["shares"], "long run, unfavourable (novelty stays)", "long run, favourable (novelty gone)"
    quoted = [f"{sh['central'][lr]:.2f}%", f"{sh['central'][unf]:.2f}–{sh['central'][fav]:.2f}%", f"{s['model_share']['central']:.2f}%",
              f"{sh['best'][lr]:.1f}%", f"{sh['best'][unf]:.1f}–{sh['best'][fav]:.1f}%", f"{s['model_share']['best']:.1f}%"]
    for name, tables in (("research_notes/premium_curve.md", [P.markdown_curve(), P.markdown_fits(), P.markdown_shares()]),
                         ("RESULTS.md", [])):
        text = open(os.path.join(ROOT, name), encoding="utf-8").read()
        for line in "\n".join(tables).splitlines():
            if line.strip() and line not in text:
                fails.append(f"{name} does not carry: {line[:90]}")
        for q in quoted:
            if q not in text:
                fails.append(f"{name} does not quote {q}")
    return fails


def test_premium_curve():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the premium-meat anchoring holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
