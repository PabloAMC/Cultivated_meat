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
    sh, unf, fav = s["shares"], "long run, unfavourable (novelty stays)", "long run, favourable (novelty gone)"
    # 2026-11-19 second round (Student's t spread of liking): the heavier tail doubled the model's share at Central's cost (0.08% to
    # 0.16%); the anchored share does not depend on the spread (0.10%). So the anchored share is now two-fifths BELOW the model's,
    # and the model's is still inside the range the corrections span (0.03-0.19%), near its favourable end. (After the audit batch,
    # with the normal spread: anchored a third above the model's. Before it: a tenth below.)
    m = s["model_share"]["central"]
    if not (0.5 * m < sh["central"][lr] < 0.8 * m and sh["central"][unf] < m < sh["central"][fav]):
        fails.append("Central's anchored share is no longer two-fifths below the model's, with the model's inside the corrections' range; "
                     "rewrite the note's conclusion")
    # 2026-11-19 audit batch, unchanged by the second round: the best case's cells with the model's ordinary demand: 2.7% in the model against 1.4% anchored
    # (0.6-2.5%). The model is about twice the curve's central figure and above its favourable end. (Was: anchored below the model's.)
    if not (sh["best"][lr] < 0.6 * s["model_share"]["best"] and sh["best"][fav] < s["model_share"]["best"]):
        fails.append("the best case's model share is no longer about twice the anchored one and above the curve's favourable end; "
                     "rewrite the note's conclusion")

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
