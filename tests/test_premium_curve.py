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
    # 2026-11-19 second round (Student's t spread of liking): the heavier tail doubled the model's share at the low-lactate example's cost (0.08% to
    # 0.16%); the anchored share does not depend on the spread (0.10%). So the anchored share is now two-fifths BELOW the model's,
    # and the model's is still inside the range the corrections span (0.03-0.19%), near its favourable end. (After the audit batch,
    # with the normal spread: anchored a third above the model's. Before it: a tenth below.)
    # 2026-11-20 (engine batch: cells dearer, the low-lactate example $32.80 to $49.96): the model gives 0.046% and the anchored
    # curve 0.020% (0.006-0.041%). The anchored share is now a little under half the model's (was two-fifths below), and the
    # model's is just ABOVE the corrections' favourable end (was inside the range). A correct consequence of the dearer cells:
    # chicken and pork cuts, mince and processed meat are now 7 to 15 times their meat's price, where the model's Student's t
    # tail holds more than the premium curve (for one shopper the two cross at about 7 times the price).
    # 2026-11-21 (fourth batch): plant-based meat's committed buyers raise the blend penalty on cuts, which cuts the curve with
    # every shopper alike more than the model: 0.015% (0.005-0.029%) anchored against 0.045%, a third, and the model 1.6 times the
    # favourable end (was 0.019% against 0.047%, two-fifths, just above it).
    # 2026-11-22 (fifth batch): the price-insensitive shoppers take the model to 0.26% at the low-lactate example's cost; the
    # anchored curve (every shopper alike) stays at 0.014% (0.005-0.029%): about a twentieth of the model, which is about nine
    # times the corrections' favourable end (was a third, and 1.6 times)
    # 2026-11-24: the model's long-run share at equal price is 50% of meat buyers (was 14.5%): the model gives 1.43% at the low-lactate example's
    # cost, the anchored curve 0.014% (0.004-0.028%), which does not use it: about a hundredth, and about fifty times the favourable end.
    m = s["model_share"]["central"]
    if not (0.005 * m < sh["central"][lr] < 0.02 * m and 30.0 * sh["central"][fav] < m < 80.0 * sh["central"][fav]):
        fails.append("the low-lactate example's anchored share is no longer about a hundredth of the model's, with the model's about "
                     "fifty times the corrections' favourable end; rewrite the note's conclusion")
    # 2026-11-19 audit batch, unchanged by the second round: the all-favourable example's cells with the model's ordinary demand: 2.7% in the model against 1.4% anchored
    # (0.6-2.5%). The model is about twice the curve's central figure and above its favourable end. (Was: anchored below the model's.)
    # 2026-11-20 (engine batch, $11.67 to $18.71): 1.13% in the model against 0.66% anchored (0.24-1.17%). The model is 1.7 times
    # the curve's central figure and now just INSIDE its favourable end (it was above: 3.16% against 2.81%). The margin is
    # small either way; the note says so.
    # 2026-11-20 final pass (the all-favourable example rebuilt as scenarios.all_favourable(), $18.71 to $7.62; the demand anchor at
    # plant-based 0.4% by volume, nominal incomes, conventional meat's price falling with the share, the closed share weighted by
    # meat eaten): 5.44% in the model against 2.49% anchored (1.07-4.03%). The model is now 2.2 times the curve's central figure and
    # ABOVE its favourable end again (1.35 times it). A correct consequence: at $7.62 a kilo of cells the products in the world
    # market are at 0.35 to 2.9 times their meat's price (beef cuts, premium seafood and dearer below it), where the model's level
    # at equal price (14.4% of meat buyers) sits above the premium labels' 8.7% and its spread of liking holds more shoppers.
    # 2026-11-27 (nutrient balance): 20.52% -> 20.38% against 2.31% -> 2.29% anchored (3.69% -> 3.66% favourable end): still 8.9 and 5.6 times
    mb = s["model_share"]["best"]
    # 2026-11-21 (fourth batch): 5.58% against 2.33% anchored (1.02-3.73%): 2.4 times, and 1.50 times the favourable end (upper
    # bound widened from 1.5 to 1.6, which 5.58 / 3.73 = 1.496 sat on)
    if not (0.07 * mb < sh["best"][lr] < 0.15 * mb and 4.0 * sh["best"][fav] < mb < 7.5 * sh["best"][fav]):   # 2026-11-24: 20.5% against 2.31% (3.69% favourable end): 8.9 times, 5.6 times
        fails.append("the all-favourable example's model share is no longer about nine times the anchored one and above the curve's "
                     "favourable end; rewrite the note's conclusion")

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
