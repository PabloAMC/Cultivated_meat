#!/usr/bin/env python3
"""test_demand_recalibration.py — the shopper model's two kinds of shopper (market_share.share, 2026-11-18).

Checks that the premium buyers' three fitted inputs are the fit to the sixteen premium meats at the stated share, that with no
premium buyers the share is the one-kind model's, that the calibration does not depend on premium buyers, that the model's
first-contact elasticity stays inside the experiment's range, that the curve now matches premium meats at three times the price,
and that the note and RESULTS.md quote the figures. Runs as a script or under pytest.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import demand_checks as D  # noqa: E402
import market_share as M  # noqa: E402
import premium_buyers as B  # noqa: E402
import premium_curve as P  # noqa: E402
import scenarios as S  # noqa: E402
from inputs import value  # noqa: E402


def check() -> list:
    fails = []
    fit = B.fit_at(value("premium_buyers_share"))["params"]
    for name, got in (("premium_kappa", fit["kappa_l"]), ("premium_liking", fit["v_l"])):
        if abs(value(name) - got) > 0.01:
            fails.append(f"{name} = {value(name)} is no longer the fit to the sixteen premium meats ({got:.3f}); update inputs.py")
    d = -P.delta_cases()["long run, central"]
    if abs(value("image_price_shift") - d) > 1e-9:
        fails.append(f"image_price_shift = {value('image_price_shift')} is not the long-run central correction ({d:.2f})")
    two, one = M.DemandParams(), M.DemandParams(premium_buyers_share=0.0)
    for name in ("beta_ref", "w_realtissue_M", "w_health_M", "w_health_E"):
        if abs(getattr(two, name) - getattr(one, name)) > 1e-12:
            fails.append(f"the calibration ({name}) depends on premium buyers; it must not")
    for R in (0.8, 1.0, 2.0, 3.5):
        if abs(M.share(R, two, premium_share=0.0) - M.share(R, one)) > 1e-12:
            fails.append("with premium_share=0 the share is not the one-kind model's")
        pi = two.premium_buyers_share
        prem = M.share(R + two.image_price_shift, one, kappa=two.premium_kappa, tier_offset=two.premium_liking, slaughter_free_x=0.0)
        if abs(M.share(R, two) - ((1 - pi) * M.share(R, one) + pi * prem)) > 1e-12:
            fails.append(f"at R={R} the share is not the weighted sum of the two kinds of shopper")
    for which in ("p", "w", "c"):
        if abs(M.share(1.0, two, cultivated_present=False, which=which) - M.share(1.0, one, cultivated_present=False, which=which)) > 1e-12:
            fails.append("with no cultivated meat on the shelf premium buyers should change nothing")
    e = M.lusk_at_parity_elasticity(two)
    if not M.LUSK_ELAS_BRACKET[0] <= e <= M.LUSK_ELAS_BRACKET[1]:
        fails.append(f"the first-contact elasticity at equal price ({e:.2f}) is outside the experiment's range")
    s = D.summary()
    at3 = s["variants"][0]["curve"][D.R_GRID.index(3.0)]
    if not 0.5 * s["premium_3x"] < at3 < 2.0 * s["premium_3x"]:
        fails.append(f"at 3 times the price the model gives {at3:.2f}%, no longer within a factor of 2 of premium meats' {s['premium_3x']:.2f}%")
    if not M.share(1.0, two) > 0.4:
        fails.append("at equal price the model no longer gives cultivated meat about half of real-meat buyers; rewrite the note")

    costs = {k: S.run(S.SCENARIOS[k].choice)["total"] for k in ("central", "best")}
    new = {k: S.shares(c, regions=("global",))["global"] for k, c in costs.items()}
    old = {k: s["variants"][1]["world"][k] for k in costs}
    if not all(new[k] > old[k] for k in costs):
        fails.append("premium buyers no longer raise the share in both Central and the best case; rewrite the note")
    quoted = [f"{S.pct_num(old['central'])}% to {S.pct_num(new['central'])}%", f"{old['best']:.1f}% to {new['best']:.1f}%",
              f"{at3:.1f}%", f"{e:.2f}", f"{M.share(1.0, two) * 100:.0f}%"]
    for name in ("research_notes/demand_recalibration.md", "RESULTS.md"):
        text = open(os.path.join(ROOT, name), encoding="utf-8").read()
        for q in quoted:
            if q not in text:
                fails.append(f"{name} does not quote {q}")
    return fails


def test_demand_recalibration():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    if fails:
        sys.exit(1)
    print("demand recalibration: all checks passed")
