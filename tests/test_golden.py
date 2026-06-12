#!/usr/bin/env python3
"""test_golden.py — golden-value regression tests for the model's headline outputs.

These pin the numbers the write-up and the interactive explorer quote, so any accidental
change to a model formula, default, or the calibration solve is caught immediately (and
visibly, with the old vs new value). They complement the Python↔JS parity test: parity
checks that the two implementations AGREE; this checks that the agreed-on number is the
RIGHT one and hasn't moved.

If a change is intentional, update the GOLDEN value here in the same commit — that makes the
output change explicit and reviewable in the diff, which is the whole point.

Run directly (no pytest needed):
    python tests/test_golden.py
Or under pytest, if installed:
    pytest tests/test_golden.py
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.dirname(HERE)
sys.path.insert(0, MODEL_DIR)

# Absolute tolerance on each pinned number. Tight enough to catch a real model change
# (sub-0.01 of a share point, or 1e-4 on a coefficient), loose enough to absorb the
# bisection/fixed-point's last-digit float noise.
TOL = 5e-3


def _golden_values() -> dict:
    """Compute the current headline numbers from the source-of-truth modules."""
    from market_share import (DemandParams, share, pb_milk_check,
                              lusk_at_parity_elasticity, LUSK_ELAS_BRACKET)
    from cost_model import CostParams, biomass_cost, cost_floor
    import meat_market as mm

    pr = DemandParams()
    cp = CostParams()
    b = float(biomass_cost(cp, 0.63, 1.0))               # Pasitka-base biomass cost $/kg
    rows, tv, tval = mm.penetration(mm.MARKETS["us"], b)

    return {
        # --- cost rung ---
        "cost_floor": float(cost_floor(cp)),
        "biomass_base": b,
        "basic_R": (b + cp.markup_add) / cp.p_conv,
        # --- calibration / derived coefficients ---
        "beta_ref": pr.beta_ref,
        "anchor_price": pr.anchor_price,
        "w_realtissue_M": pr.w_realtissue_M,
        "w_health_M": pr.w_health_M,
        "w_health_E": pr.w_health_E,
        # --- demand headline (percent) ---
        "pb_share_pct": share(1.0, pr, cultivated_present=False, which="pb") * 100,
        "parity_pct": share(1.0, pr, accept_x=1.0, theta_free_M=0.0) * 100,
        "milk_pct": pb_milk_check(pr) * 100,
        # --- kappa validation: implied at-parity cold elasticity, must stay in Lusk's bracket ---
        "lusk_elas_parity_cold": lusk_at_parity_elasticity(pr),
        # --- income gradient at the Pasitka-base R (the channel that once diverged) ---
        "income_us_pct": share(2.42, pr, income=85810) * 100,
        "income_china_pct": share(2.42, pr, income=27105) * 100,
        "income_nigeria_pct": share(2.42, pr, income=6440) * 100,
        # --- a scenario dial moves share as expected ---
        "health_x_half_pct": share(1.0, pr, health_x=0.5) * 100,
        # --- penetration roll-ups (US, base biomass) ---
        "us_pen_vol_pct": tv * 100,
        "us_pen_val_pct": tval * 100,
    }


# The pinned numbers. Captured from the current model; update deliberately (in the same
# commit) if a model change is intended, so the output move is explicit in the diff.
GOLDEN = {
    # The 2026-06-12 demand refactor moved several of these DELIBERATELY (old value in the comment):
    #  - loss_aversion default 2.25 -> 1.0 (symmetric price response, no kink): shifts beta_ref (now
    #    negative), parity 49.87 -> 48.76, the solved health weights, and the at-parity elasticities.
    #  - income channel re-architected (real income->price-sensitivity scaling, gamma 0.5 -> 0.25):
    #    the income_* rows now show a GENUINE rich-poor gradient (was a monotonicity-cap artifact).
    "cost_floor":          7.5200,
    "biomass_base":        24.0120,
    "basic_R":             2.41767,
    "beta_ref":           -0.052661,   # was 0.051044 (loss_aversion 2.25->1.0 flips beta sign)
    "anchor_price":        29.0120,
    "w_realtissue_M":      2.24227,    # was 2.2845
    "w_health_M":          0.847069,   # was 1.3116 (lambda=1 recalibration)
    "w_health_E":          1.81157,    # was 2.2762
    "pb_share_pct":        1.2000,
    "parity_pct":          48.7633,    # was 49.8696 (no loss-aversion kink lift)
    "milk_pct":            15.2568,
    "lusk_elas_parity_cold": -1.53837,  # was -0.9518; still in Lusk's [-3.4, -0.84] (self-check [4b])
    "income_us_pct":       8.72582,    # was 9.0336 (US anchor ~unchanged; tiny shift from lambda=1)
    "income_china_pct":    4.10816,    # was 8.4320 -> now a REAL income gradient (was cap artifact)
    "income_nigeria_pct":  1.02246,    # was 5.6870 -> real gradient: poorer = far more price-sensitive
    "health_x_half_pct":   59.577,     # was 65.9593 (lambda=1)
    "us_pen_vol_pct":      5.89337,    # was 5.9663
    "us_pen_val_pct":      9.97883,    # was 10.0657
}


def check_golden() -> list:
    """Return a list of human-readable failures (empty == all golden values hold)."""
    from market_share import LUSK_ELAS_BRACKET
    cur = _golden_values()
    fails = []
    for k, gold in GOLDEN.items():
        got = float(cur[k])
        if abs(got - gold) > TOL:
            fails.append(f"{k}: golden={gold:.6g} got={got:.6g} diff={abs(got - gold):.2e}")
    # SUBSTANTIVE guard (beyond pinning the number): the implied at-parity cold elasticity must
    # stay inside Lusk 2020's measured bracket — the data discipline on kappa. A recalibration
    # that pushed it out (e.g. a kappa change) should fail loudly, not just move the golden value.
    lo, hi = LUSK_ELAS_BRACKET
    le = float(cur["lusk_elas_parity_cold"])
    if not (lo <= le <= hi):
        fails.append(f"lusk_elas_parity_cold={le:.3f} fell OUTSIDE Lusk's measured [{lo}, {hi}] "
                     f"bracket — kappa is no longer data-consistent at parity")
    print(f"golden check: {len(GOLDEN)} pinned values (tol {TOL:.0e})")
    return fails


def check_illustrative_numbers_in_html() -> list:
    """Guard against PROSE DRIFT: the methodology + slider tooltips quote illustrative shares
    ("at parity 0.8 -> ~27%", "kappa=3 keeps ~14%"). build_interactive computes those from the
    live model and substitutes them via {{TOKEN}} placeholders, so they can never go stale —
    UNLESS someone hand-types a literal number again (the exact failure the health-attribute
    refactor once caused). This test enforces the invariant on THREE fronts:

      (1) every {{TOKEN}} the template uses has a value in illustrative_numbers() (no typos);
      (2) every value in illustrative_numbers() is actually USED by a {{TOKEN}} in the template
          (no dead/forgotten computed numbers);
      (3) the GENERATED interactive.html has no surviving {{...}} placeholder and every computed
          value is present.

    Checking the TEMPLATE (PAGE_HTML + JS_ENGINE), not just the output, is what makes this
    catch a re-introduced hand-typed number: a stale literal would not be a {{TOKEN}}, so the
    way to keep prose honest is to ensure illustrative shares are ONLY ever placeholders."""
    import json
    import re
    import build_interactive as bi
    fails = []
    nums = bi.illustrative_numbers()                     # {"{{TOKEN}}": "NN"}
    # The pre-substitution template is exactly what main() assembles: page markup + JS engine +
    # the MODEL_JSON blob (the slider TOOLTIPS — where several illustrative numbers live — are in
    # build_model()'s output, not in PAGE_HTML/JS_ENGINE). Reconstruct it the same way so the
    # token scan sees every placeholder, wherever it lives.
    template = (bi.PAGE_HTML + bi.JS_ENGINE).replace("__MODEL_JSON__", json.dumps(bi.build_model()))
    used = set(re.findall(r"\{\{[A-Z0-9_]+\}\}", template))
    have = set(nums.keys())
    # (1) tokens used in the template but not computed
    for t in sorted(used - have):
        fails.append(f"template uses {t} but illustrative_numbers() computes no value for it")
    # (2) computed numbers never used (dead — a sign a placeholder was hand-edited away)
    for t in sorted(have - used):
        fails.append(f"illustrative_numbers() computes {t} but no {{...}} in the template uses it "
                     f"(was it replaced by a hand-typed number?)")
    # (3) the generated page is clean and carries the values
    html_path = os.path.join(MODEL_DIR, "interactive.html")
    if not os.path.exists(html_path):
        fails.append(f"{html_path} missing — run `python build_interactive.py` first")
    else:
        html = open(html_path, encoding="utf-8").read()
        stray = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", html)))
        if stray:
            fails.append(f"unsubstituted placeholder(s) survived into interactive.html: {stray}")
        for token, val in nums.items():
            if f"{val}%" not in html:
                fails.append(f"{token}={val}% computed but not present in interactive.html")
    print(f"illustrative-number drift check: {len(nums)} model-computed values, "
          f"{len(used)} placeholders in template, "
          f"{'all consistent' if not fails else f'{len(fails)} problem(s)'}")
    return fails


def test_golden_values():
    """pytest entry point: the headline model outputs match their pinned golden values."""
    fails = check_golden()
    assert not fails, (
        "Golden-value regression FAILED (a model output changed):\n  " + "\n  ".join(fails)
        + "\n\nIf this change is intentional, update GOLDEN in tests/test_golden.py "
          "in the same commit so the output move is explicit.")


def test_illustrative_numbers_not_stale():
    """pytest entry point: the prose's illustrative numbers match the live model (no drift)."""
    fails = check_illustrative_numbers_in_html()
    assert not fails, (
        "Illustrative-number drift FAILED:\n  " + "\n  ".join(fails)
        + "\n\nRe-run `python build_interactive.py` to re-substitute the model-computed numbers.")


if __name__ == "__main__":
    failures = check_golden() + check_illustrative_numbers_in_html()
    if failures:
        print(f"\nFAIL — {len(failures)} check(s) failed:")
        for f in failures:
            print("  " + f)
        print("\nIf a model change is intentional, update GOLDEN (and re-run "
              "build_interactive.py) in the same commit.")
        sys.exit(1)
    print("PASS — all headline model outputs match golden values and the prose is in sync.")
    sys.exit(0)
