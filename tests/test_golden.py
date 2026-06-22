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
    #  - income channel re-architected to GENUINE damped-BLP: V_price = alpha*ln(y_eff - price_j),
    #    y_eff = income_ref*(income/income_ref)**phi, single constant alpha. phi default 0.25->0.5 to
    #    hit the empirical ~2x Nigeria/US elasticity gradient. The income_* rows show the BLP gradient.
    #  - per-cut p_ref: each meat type's absolute price uses its own conventional price (us_pen_val moved).
    "cost_floor":          7.5200,
    "biomass_base":        24.0120,
    "basic_R":             2.41767,
    "beta_ref":           -0.052663,   # the BLP slope at the anchor (alpha = -beta*(y_ref - anchor))
    "anchor_price":        29.0120,
    "w_realtissue_M":      2.24236,
    "w_health_M":          0.847148,
    "w_health_E":          1.81164,
    "pb_share_pct":        1.2000,
    "parity_pct":          48.7634,    # calibration-anchored, invariant to the income re-architecture
    "milk_pct":            15.2568,
    "lusk_elas_parity_cold": -1.53827,  # in Lusk's [-3.4, -0.84] (self-check [4b])
    "income_us_pct":       8.72704,    # US = the anchor, invariant to phi (y_eff = income_ref there)
    "income_china_pct":    4.42554,    # damped-BLP gradient at phi=0.5
    "income_nigeria_pct":  0.76364,    # damped-BLP: poorer = more price-sensitive (curvature in the log)
    "health_x_half_pct":   59.578,
    "us_pen_vol_pct":      5.06441,    # cut/premium tier rescale fix (beta = beta_ref*eps_mult)
    "us_pen_val_pct":      8.40933,    # premium no longer flat-clamped; responds to R correctly
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
    # {{KAPPA4_LUSK_ELAS}} is the one model-computed token that is NOT a %-share, so it lives
    # outside illustrative_numbers() (which is %-share-only) and is substituted directly in main()
    # from market_share.lusk_at_parity_elasticity. It is still drift-proof (computed from the live
    # model, golden-guarded as lusk_elas_parity_cold), so exempt it from the share-token bookkeeping.
    used.discard("{{KAPPA4_LUSK_ELAS}}")
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


def check_derived_prose_numbers() -> list:
    """TRIPWIRE for the Layer-2 drift hole: a model-DERIVED number quoted in the methodology
    prose that is NOT a %-share (so it lives outside illustrative_numbers / the {{TOKEN}} system)
    must still match the live model. This is exactly the gap the stale '-0.95' elasticity slipped
    through: it was a hand-typed literal that no test re-derived. Each entry below pins a derived
    quantity to its live value AND asserts the rounded figure is present in the generated page —
    so a recalibration that moves it fails loudly here unless the prose is updated in the same commit.

    DISCIPLINE: when you quote a NEW model-derived number in the prose, add it here (or, if it is a
    %-share, route it through illustrative_numbers as a {{TOKEN}}). Numbers that are EXTERNAL DATA
    (the Lusk [-3.4, -0.84] bracket, the +0.2/-0.4/-1.5 tier offsets, DOIs) are NOT model outputs and
    deliberately do NOT belong here — they are sourced constants, guarded by review, not by the model."""
    import os
    from market_share import DemandParams, share
    from inputs import value

    pr = DemandParams()

    def elas(R):  # realised own-price elasticity at ratio R (neutral standing)
        h = 1e-5
        f = lambda r: share(r, pr, accept_x=1.0, theta_free_M=0.0, neophobia_x=0.0)
        s0 = f(R)
        return (f(R * (1 + h)) - f(R * (1 - h))) / (2 * h * s0)

    cost_floor = (value("aa_intensity") * value("aa_bulk_price")
                  + value("glucose_other_floor") + value("plant_floor"))

    # (label, live value, the exact string the prose uses for it). The string is what must appear
    # verbatim in interactive.html; if the live value drifts so the rounded string changes, update both.
    derived = [
        ("eps_x = eps_own*kappa",        value("eps_own") * value("cult_sub_mult"), "−3.6"),
        ("elasticity at R=1.0",          elas(1.0),  "−0.8"),
        ("elasticity at R=1.5",          elas(1.5),  "−1.7"),
        ("elasticity at R=2.42 (op.)",   elas(2.42), "−3.6"),
        ("biomass cost floor $/kg",      cost_floor, "7.5"),
    ]
    # what each label ROUNDS to, so the test also catches a silent value move that the prose missed
    rounds = {"eps_x = eps_own*kappa": "−3.6", "elasticity at R=1.0": "−0.8",
              "elasticity at R=1.5": "−1.7", "elasticity at R=2.42 (op.)": "−3.6",
              "biomass cost floor $/kg": "7.5"}

    fails = []
    html_path = os.path.join(MODEL_DIR, "interactive.html")
    html = open(html_path, encoding="utf-8").read() if os.path.exists(html_path) else ""
    if not html:
        return [f"{html_path} missing — run `python build_interactive.py` first"]
    for label, val, prose_str in derived:
        # 1) the live value still rounds to the string the prose uses
        neg = "−" if val < 0 else ""
        rounded = f"{neg}{abs(val):.1f}"
        if rounded != rounds[label]:
            fails.append(f"DERIVED '{label}': live value {val:.4f} now rounds to '{rounded}', "
                         f"but the prose quotes '{rounds[label]}' — update the prose AND this test")
        # 2) and that string is actually present in the generated page (catches a deleted/edited literal)
        if prose_str not in html:
            fails.append(f"DERIVED '{label}': expected figure '{prose_str}' not found in interactive.html "
                         f"(was the methodology prose edited away from the model?)")
    print(f"derived-prose-number tripwire: {len(derived)} non-share derived figures checked, "
          f"{'all present & current' if not fails else f'{len(fails)} problem(s)'}")
    return fails


def test_derived_prose_numbers():
    """pytest entry point: model-derived figures quoted in the methodology prose match the live model."""
    fails = check_derived_prose_numbers()
    assert not fails, ("Derived-prose-number drift FAILED:\n  " + "\n  ".join(fails)
        + "\n\nA model-derived number in the methodology prose no longer matches the model. "
          "Update the prose (and this test's expected string) in the same commit, then re-run "
          "build_interactive.py.")


def check_blp_linearisation() -> list:
    """RIGOR GUARD on the damped-BLP income term. The price utility is genuine BLP,
    V_price = alpha*ln(y_eff - price), alpha = -beta*(income_ref - anchor_price),
    y_eff = income_ref*(income/income_ref)**phi. At meat prices (price << income) BLP is
    well-approximated by its first-order linearisation,
        ln(y_eff - price) ~ ln(y_eff) - price/y_eff,
    so alpha*ln(y_eff-price) ~ const + beta*(income_ref-anchor)*price/y_eff. This independently
    re-derives the income term; if the BLP implementation has an algebra error, the two diverge.
    We assert they agree to <0.5pp over a region x R grid (verified ~0.01pp). This is a mutual
    cross-validation of the income microfoundation, not just a pinned number."""
    import numpy as np
    from market_share import DemandParams, _softmax
    pr = DemandParams()
    yref, anchor, beta = pr.income_ref, pr.anchor_price, pr.beta_ref

    def share_with(price_term, R, income, p_ref=12.0):
        def util(seg):
            ratio = np.array([pr.price_wf_mult, 1.0, pr.price_pb_mult, R]); price = ratio * p_ref
            taste = np.array([pr.taste_quality_w, 0.0, pr.taste_quality_p, 0.0])
            sl = np.array([1.0, 0, 1, 1]); rt = np.array([0, 1, pr.real_tissue_p, pr.real_tissue_x])
            h = np.array([pr.health_w, pr.health_c, 0, 0]); asc = np.array([0, 0, pr.neophobia_p, pr.neophobia_x])
            if seg == "M": ws, wr, wh = 0.0, pr.w_realtissue_M, pr.w_health_M
            else: ws, wr, wh = pr.w_slaughter_E, pr.w_realtissue_E, pr.w_health_E
            y_eff = yref * (income / yref) ** pr.income_gradient
            Vp = price_term(price, y_eff)
            prem = ratio - 1.0
            Vl = -pr.loss_aversion * np.maximum(0, prem) + np.maximum(0, -prem)
            return Vp + Vl + pr.w_taste * taste + ws * sl + wr * rt + wh * h + asc
        M = _softmax(util("M")); E = _softmax(util("E"))
        return float(pr.w_eth * E[3] + (1 - pr.w_eth) * M[3])

    blp = lambda price, y_eff: -beta * (yref - anchor) * np.log(np.maximum(y_eff - price, 1.0))
    lin = lambda price, y_eff: beta * (yref - anchor) * (price / y_eff)   # 1st-order term
    worst = 0.0
    for R in (1.0, 1.75, 2.42, 3.0):
        for income in (85810, 27105, 11159, 6440):
            a = share_with(blp, R, income) * 100
            b = share_with(lin, R, income) * 100
            worst = max(worst, abs(a - b))
    print(f"BLP-linearisation cross-check: max |BLP - linear| = {worst:.3f} pp (tol 0.5)")
    return [] if worst < 0.5 else [f"BLP income term diverges from its linearisation by {worst:.2f}pp "
                                   f"(>0.5) — possible algebra error in the damped-BLP price utility"]


def test_blp_linearisation():
    """pytest entry point: the damped-BLP income term matches its linearisation at meat prices."""
    fails = check_blp_linearisation()
    assert not fails, "BLP rigor check FAILED:\n  " + "\n  ".join(fails)


def _mc_prose_values() -> dict:
    """Recompute the Monte-Carlo headline numbers the PROSE essays (RESULTS/POST/METHODS) quote,
    at the SAME (deterministic) seed and N the docs state — so they are reproducible to the last
    digit. Slow (~75s: the regional roll-up runs a per-draw loop over 7 regions at N=30,000), so it
    is in the full suite, not the quick path."""
    import numpy as np
    import uncertainty as U
    from meat_market import monte_carlo as pen_mc
    mc = U.monte_carlo(20000, "commodity", {})            # commodity §2 block (N=20,000, seed 0)
    R, sh = mc["R"], mc["share"] * 100
    out = {
        "commodity_R_p50": float(np.percentile(R, 50)),
        "commodity_R_ci": (float(np.percentile(R, 10)), float(np.percentile(R, 90))),
        "commodity_share_p50": float(np.percentile(sh, 50)),
        "commodity_share_ci": (float(np.percentile(sh, 10)), float(np.percentile(sh, 90))),
        "regional": {},
    }
    for region in ("eu", "us", "global", "china", "brazil", "india", "nigeria"):
        m = pen_mc(region, 30000)                          # regional §5 table (N=30,000, seed 0)
        out["regional"][region] = {
            "vol": float(np.percentile(m["vol"], 50)),
            "val": float(np.percentile(m["val"], 50)),
        }
    return out


# which regions each prose doc actually tabulates (POST shows only four; RESULTS shows all seven)
_REGION_LABEL = {"eu": "Europe", "us": "US", "global": "global", "china": "China",
                 "brazil": "Brazil", "india": "India", "nigeria": "Nigeria"}
_DOC_REGIONS = {"RESULTS.md": list(_REGION_LABEL), "POST.md": ["eu", "us", "global", "china"]}


def check_markdown_prose_numbers() -> list:
    """ROOT-CAUSE GUARD for the prose-drift class that this audit found: the three MARKDOWN essays
    (RESULTS.md, POST.md, METHODS.md) hand-type headline Monte-Carlo numbers that NO test re-derived,
    so a prior change (the two-sided media_price) silently invalidated every one of them — and even
    inverted a conclusion. interactive.html is already drift-proof (tokens + the checks above); this
    extends the same discipline to the markdown.

    It recomputes the headline MC values from the live model (at the docs' stated seed/N) and asserts
    each rounded figure is PRESENT in the doc(s) that quote it — the commodity R/share §2 block and the
    per-region §5 table. If the model moves and a doc is not re-synced in the same commit, this fails
    with the stale-vs-live values shown. (Matches on the doc's own rounding; a coincidental match can
    only cause a false PASS, never a false FAIL, so it is a safe tripwire.)"""
    vals = _mc_prose_values()
    docs = {}
    for name in ("RESULTS.md", "POST.md", "METHODS.md"):
        p = os.path.join(MODEL_DIR, name)
        docs[name] = open(p, encoding="utf-8").read() if os.path.exists(p) else None

    fails = []
    rP = f"{vals['commodity_R_p50']:.2f}"                  # e.g. "2.09"
    sP = f"{vals['commodity_share_p50']:.1f}%"             # e.g. "7.3%"
    # commodity R P50 is quoted in all three; share P50 in RESULTS + METHODS (POST's block shows R only)
    for name in ("RESULTS.md", "POST.md", "METHODS.md"):
        if docs[name] is None:
            fails.append(f"{name} missing")
        elif rP not in docs[name]:
            fails.append(f"{name}: commodity R P50 = {rP} not found (prose stale vs live model?)")
    for name in ("RESULTS.md", "METHODS.md"):
        if docs[name] is not None and sP not in docs[name]:
            fails.append(f"{name}: commodity share P50 = {sP} not found (prose stale vs live model?)")

    # regional table: for each region the doc tabulates, find its row (stripped line starting with the
    # region label and carrying a CI bracket) and assert the vol & val P50 strings appear on it.
    for name, regions in _DOC_REGIONS.items():
        if docs[name] is None:
            continue
        lines = docs[name].splitlines()
        for region in regions:
            label = _REGION_LABEL[region]
            row = next((ln for ln in lines if ln.strip().startswith(label) and "[" in ln), None)
            volP = f"{vals['regional'][region]['vol']:.1f}%"
            valP = f"{vals['regional'][region]['val']:.1f}%"
            if row is None:
                fails.append(f"{name}: no regional table row for {label}")
                continue
            if volP not in row:
                fails.append(f"{name}: {label} VOLUME P50 should be {volP} but its row is stale: '{row.strip()}'")
            if valP not in row:
                fails.append(f"{name}: {label} VALUE P50 should be {valP} but its row is stale: '{row.strip()}'")

    print(f"markdown-prose drift check: commodity R/share + {sum(len(r) for r in _DOC_REGIONS.values())} "
          f"region-rows across RESULTS/POST/METHODS, "
          f"{'all in sync' if not fails else f'{len(fails)} stale'}")
    return fails


def test_markdown_prose_numbers():
    """pytest entry point: the markdown essays' headline MC numbers match the live model."""
    fails = check_markdown_prose_numbers()
    assert not fails, (
        "Markdown-prose drift FAILED (an essay's headline number no longer matches the model):\n  "
        + "\n  ".join(fails)
        + "\n\nRe-run the model and update RESULTS.md / POST.md / METHODS.md in the same commit.")


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
    failures = (check_golden() + check_illustrative_numbers_in_html()
                + check_derived_prose_numbers() + check_blp_linearisation()
                + check_markdown_prose_numbers())
    if failures:
        print(f"\nFAIL — {len(failures)} check(s) failed:")
        for f in failures:
            print("  " + f)
        print("\nIf a model change is intentional, update GOLDEN (and re-run "
              "build_interactive.py) in the same commit.")
        sys.exit(1)
    print("PASS — all headline model outputs match golden values and the prose is in sync.")
    sys.exit(0)
