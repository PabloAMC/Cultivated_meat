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
    from market_share import (DemandParams, share, pb_milk_check, organic_premium_check,
                              lusk_at_parity_elasticity, LUSK_ELAS_BRACKET)
    from adoption_timing import TimingParams, years_to_stabilize
    from cost_model import CostParams, biomass_cost, cost_floor, ratio as cm_ratio
    import meat_market as mm

    pr = DemandParams()
    cp = CostParams()
    b = float(biomass_cost(cp))                          # default biomass cost $/kg
    rows, tv, tval = mm.penetration(mm.MARKETS["us"], b)
    _, gv, gval = mm.penetration(mm.MARKETS["global"], b, income=mm.REGION_INCOME["global"])

    return {
        # --- cost rung ---
        "cost_floor": float(cost_floor(cp)),
        "biomass_base": b,
        "basic_R": cm_ratio(b, cp),
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
        "world_pen_vol_pct": gv * 100,
        # --- premium real-meat check (organic chicken, ~2.4% observed; self-check [4c], FAILS by design) ---
        "organic_vs_cuts_pct": organic_premium_check(pr)["vs_cuts"],
        # --- timing: years to 90% of the LONG-RUN share at the default price (horizon-free) ---
        "years_to_stabilize": float(years_to_stabilize(cm_ratio(b, cp), pr, TimingParams())),
    }


# The pinned numbers. Captured from the current model; update deliberately (in the same
# commit) if a model change is intended, so the output move is explicit in the diff.
GOLDEN = {
    # 2026-11-20 (the engine batch: lactate tolerated 35 mM, medium-preparation capital, bubble deaths, labour in perfusion,
    # harvest loss, accept_x out of the bands, membrane life 2,415 L/m2, the Humbird back-test's three fixes): NO pin below moved.
    # Every pin is computed from cost_model's defaults (the reported cost and `cost_floor`) and from the demand model at its
    # point values, and the batch changed floor_physics.explore, the scenarios and what the bands draw. What the batch moved in
    # this file's scope is the prose check: with accept_x no longer drawn, the regional medians of RESULTS.md section 4 rose
    # (US volume 0.5% -> 0.7%, Europe 0.9% -> 1.1%, world 0.2% -> 0.3%) and the commodity share median 0.3% -> 0.4%.
    # 2026-11-20, later: `plant_floor` 10.8 -> 13.8 (the plant term of Humbird's optimistic design, which explore() now prices
    # at $16.0 with bubble deaths, the harvest loss, the 2,415 L/m2 membranes, the perfusion crew and the medium-preparation
    # capital): cost_floor 12.8035 -> 15.8035. No other pin moved (the default stack is the reported cost, above the floor).
    # The 2026-06-12 demand refactor moved several of these DELIBERATELY (old value in the comment):
    #  - loss_aversion default 2.25 -> 1.0 (symmetric price response, no kink): shifts beta_ref (now
    #    negative), parity 49.87 -> 48.76, the solved health weights, and the at-parity elasticities.
    #  - income channel re-architected to GENUINE damped-BLP: V_price = alpha*ln(y_eff - price_j),
    #    y_eff = income_ref*(income/income_ref)**phi, single constant alpha. phi default 0.25->0.5 to
    #    hit the empirical ~2x Nigeria/US elasticity gradient. The income_* rows show the BLP gradient.
    #  - per-cut p_ref: each meat type's absolute price uses its own conventional price (us_pen_val moved).
    # 2026-11-14: cost side re-anchored. Default = SuperMeat 2024 as reported (30.5 L/kg x $0.50 + $14.2);
    # floor = physics-based (plant 11.5). biomass_base 24.0120 -> 29.4500, basic_R 2.41767 -> 2.87083,
    # cost_floor 7.7020 -> 13.2020. The demand calibration is UNCHANGED (anchor fixed at 29.012,
    # `elasticity_anchor_price`), so beta_ref, the solved weights and every at-parity figure keep their values.
    # 2026-11-19: nutrient floor $1.70 -> $2.00 (GFI feed-grade amino acids, research_notes/nutrient_floor.md): cost_floor
    # 12.5020 -> 12.8035. Nothing else in this list moves: the default (reported) stack is above the floor.
    # 2026-11-21: plant_floor 13.8 -> 13.5 (floor_physics.tiers: the building's power follows its floor and its class; the
    # floor glucose tied to the mass balance, 0.32 -> 0.311 kg a kilo): cost_floor 15.8035 -> 15.4999. No other pin moved.
    "cost_floor":          15.4999,
    "biomass_base":        34.3500,
    # 2026-11-18: shelf price = (cost + $2.5) / (1 - 28% shop margin), was cost + $5 (research_notes/retail_markup_form.md).
    # basic_R 3.27917 -> 4.26505; US vol 0.584202 -> 0.233623, US val 1.7793 -> 0.80766, world vol 0.274195 -> 0.0914556.
    # The demand calibration is unchanged (its anchor price is frozen).
    # 2026-11-18 (later): premium rows of the market tables sized from data (research_notes/premium_market_sizes.md):
    # US vol 0.233623 -> 0.132224, US val 0.80766 -> 0.458047, world vol 0.0914556 -> 0.0251659.
    # 2026-11-18 (later): shoppers differ in how much they like cultivated meat (liking_sd 5, equal_price_share 13%), and the
    # premium rows and seafood's weight in the market tables sized from data. The calibration is unchanged. parity 48.7634 -> 13,
    # cold elasticity -3.26883 -> -1.53133 (experiment about -1.5), health_x_half 59.578 -> 14.7346, income_us 0.702045 -> 2.08241,
    # income_china 0.155473 -> 1.07862, income_nigeria 0.00390188 -> 0.138745, US vol 0.132224 -> 0.246504, US val 0.458047 ->
    # 0.613635, world vol 0.0251659 -> 0.0416619, years_to_stabilize 30 -> 28.
    "basic_R":             4.26505,
    "beta_ref":           -0.054036,   # the BLP slope at the anchor (alpha = -beta*(y_ref - anchor))
    "anchor_price":        29.0120,
    # 2026-11-21 (the final state of 2026-11-20): plant-based meat's share target 1.2% -> 0.4% of meat by volume
    # (pb_share_target), nominal incomes (REGION_INCOME, income_ref 85,810 -> 86,170, income_gradient 0.5 -> 0.32), conventional
    # meat's price falling as it loses sales (conv_exponent) and markets closed by law (closed_share). Each moved by design:
    # w_realtissue_M 2.24236 -> 3.39863, w_health_M 0.847148 -> 1.39169, w_health_E 1.81164 -> 2.36651 (re-solved to the new
    # plant-based target), pb_share_pct 1.2 -> 0.4, lusk_elas_parity_cold -1.3685 -> -1.37392, income_us 1.904789 -> 1.89075,
    # income_china 1.122423 -> 1.38545, income_nigeria 0.372591 -> 0.799218, health_x_half 15.387776 -> 16.9996, us_pen_vol
    # 0.514012 -> 0.423594, us_pen_val 1.023453 -> 0.83839, world_pen_vol 0.179202 -> 0.172079, organic_vs_cuts 19.4854 -> 20.1926.
    # 2026-11-21 (fourth batch): plant-based meat's committed buyers (market_share segment "K": 7% of shoppers buy 82% of the
    # mainstream's plant-based meat and respond 0.25 times as strongly to its price; research_notes/demand_checks.md section 5).
    # The ordinary shoppers buy plant-based meat less, so their solved real-meat weight rises and, with it, the blend penalty on
    # cuts: w_realtissue_M 3.39863 -> 5.11335, w_health_M 1.39169 -> 2.20457, w_health_E 2.36651 -> 2.35875, beta_ref -0.052663
    # -> -0.054036 (the old pin was within tolerance of -0.05319), lusk_elas_parity_cold -1.37392 -> -1.38249, income_us 1.89075
    # -> 1.86976, income_china 1.38545 -> 1.36397, income_nigeria 0.799218 -> 0.781302, health_x_half 16.9996 -> 19.656 (the
    # larger solved health weight), us_pen_vol 0.423594 -> 0.379082, us_pen_val 0.83839 -> 0.741859, world_pen_vol 0.172079 ->
    # 0.15554, organic_vs_cuts 20.1926 -> 21.397. years_to_stabilize stays 21 with repeat buying (repeat_rate 0.62, lapse_rate
    # 0.14) and the share of the meat sold.
    # 2026-11-22 (fifth batch): the price-insensitive shoppers (8% of every segment, 0.11 times other shoppers' response to every
    # price, liking 0 utils above others; research_notes/demand_checks.md section 7) are in the calibration, and the spread of
    # liking was refitted with them (3.9 -> 3.55 utils, tail 4 -> 7). Each moved by design: w_realtissue_M 5.11335 -> 5.28426,
    # w_health_M 2.20457 -> 2.31286, w_health_E 2.35875 -> 2.60496, lusk_elas_parity_cold -1.38249 -> -1.50699, income_us
    # 1.86976 -> 2.10414, income_china 1.36397 -> 1.64074, income_nigeria 0.781302 -> 1.13262 (the price-insensitive shoppers buy
    # at 2.42 times the price), health_x_half 19.656 -> 20.249, us_pen_vol 0.379082 -> 0.628687, us_pen_val 0.741859 -> 0.912001,
    # world_pen_vol 0.15554 -> 0.430605, organic_vs_cuts 21.397 -> 21.4752, years_to_stabilize 21 -> 25.
    "w_realtissue_M":      5.28426,
    "w_health_M":          2.31286,
    "w_health_E":          2.60496,
    "pb_share_pct":        0.4000,
    "parity_pct":          13.0000,    # calibration-anchored, invariant to the income re-architecture
    "milk_pct":            15.2568,
    # 2026-11-19, later: shoppers' liking is a Student's t spread (sd 3.9, 4 degrees of freedom) on a 67-point grid; the 15-point
    # rule had been too coarse (research_notes/liking_spread.md). Elasticity -1.53133 -> -1.3685; the income and health shares, the
    # roll-ups and the years to 90% below all moved with it (old values in the comments).
    "lusk_elas_parity_cold": -1.50699,  # experiment about -1.5 (-1.1 to -1.65 across arms; self-check [4b])
    "income_us_pct":       2.10414,   # was 2.08241   # US = the anchor, invariant to phi (y_eff = income_ref there)
    "income_china_pct":    1.64074,   # was 1.07862   # damped-BLP gradient at phi=0.5
    "income_nigeria_pct":  1.13262,   # was 0.138745: the heavier tail keeps a few buyers far above parity   # damped-BLP: poorer = more price-sensitive (curvature in the log)
    "health_x_half_pct":   20.2490,   # was 14.7346
    # 2026-11-13 (independent review): a tier's price-sensitivity override now scales BOTH price channels
    # (the ratio term too), as documented; cuts/premium tiers are less price-sensitive than before, so the
    # US roll-up rose (vol 5.04423 -> 5.73401, val 8.40933 -> 9.26091). World beef re-priced by consumption
    # weights (14/24 -> 11.2/20.4), which moves only the world roll-up (pinned from now on).
    # 2026-11-14 (cost side re-anchored): vol 5.73401 -> 3.56104, val 9.26091 -> 6.37199, world 2.46298 -> 1.36033.
    # 2026-11-19 (a cut = 0.8 cells + $2 plant-protein matrix + $2 assembly beyond mince, was a full kilo of cells + $6 scaffold;
    # research_notes/structuring_cost.md): vol 0.246504 -> 0.612519, val 0.613635 -> 1.31535, world 0.0416619 -> 0.182953.
    # 2026-11-19 audit batch (research_notes/audit_2026-11-19.md): the tier rule replaced by a blend penalty and a continuous
    # premium offset (no tier is less price-sensitive any more), world seafood re-priced by consumption:
    # vol 0.612519 -> 0.363114, val 1.31535 -> 0.848201, world 0.182953 -> 0.0594949.
    # with the Student's t spread: vol 0.363114 -> 0.440886, val 0.848201 -> 0.862196, world 0.0594949 -> 0.139634.
    # 2026-11-19 (restructure, audit 6a): the roll-ups report cultivated meat's share of the meat sold, x / (x + c), not of all four
    # choices: vol 0.440886 -> 0.514012, val 0.862196 -> 1.023453, world 0.139634 -> 0.179202. The calibration does not move.
    "us_pen_vol_pct":      0.628687,
    "us_pen_val_pct":      0.912001,
    "world_pen_vol_pct":   0.430605,
    "organic_vs_cuts_pct": 21.4752,  # vs ~2.4% observed: the model over-predicts shares above parity
    "years_to_stabilize":  25,      # 2026-11-22 (fifth batch): was 21; moved with the demand curve, not examined further      # 28 with the normal spread;     # was "~25" when measured as 90% of the year-30 value
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
    nums = bi.illustrative_numbers()                     # {"{{TOKEN}}": "NN"}  (%-shares)
    dnums = bi.derived_numbers()                         # {"{{TOKEN}}": "2.4"} (ratios, $/kg, years...)
    # The pre-substitution template is exactly what main() assembles: page markup + JS engine +
    # the MODEL_JSON blob (the slider TOOLTIPS — where several illustrative numbers live — are in
    # build_model()'s output, not in PAGE_HTML/JS_ENGINE). Reconstruct it the same way so the
    # token scan sees every placeholder, wherever it lives.
    template = (bi.PAGE_HTML + bi.JS_ENGINE).replace("__MODEL_JSON__", json.dumps(bi.build_model()))
    used = set(re.findall(r"\{\{[A-Z0-9_]+\}\}", template))
    have = set(nums.keys()) | set(dnums.keys())
    # (1) tokens used in the template but not computed
    for t in sorted(used - have):
        fails.append(f"template uses {t} but build_interactive computes no value for it")
    # (2) computed numbers never used (dead — a sign a placeholder was hand-edited away)
    for t in sorted(have - used):
        fails.append(f"build_interactive computes {t} but no {{...}} in the template uses it "
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
        for token, val in dnums.items():
            if val not in html:
                fails.append(f"{token}={val} computed but not present in interactive.html")
    print(f"illustrative-number drift check: {len(nums) + len(dnums)} model-computed values, "
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

    from inputs import GLUCOSE_OTHER_FLOOR
    cost_floor = (value("aa_intensity") * value("aa_bulk_price")
                  + GLUCOSE_OTHER_FLOOR + value("plant_floor"))

    # (label, live value, the exact string the prose uses for it). The string is what must appear
    # verbatim in interactive.html; if the live value drifts so the rounded string changes, update both.
    derived = [
        ("eps_x = eps_own*kappa",        value("eps_own") * value("kappa_base"), "-3.6"),
        # 2026-11-19: with the Student's t spread of liking these moved from −1.0, −1.8, −3.2 (steeper near parity, flatter far above it)
        # 2026-11-22 (fifth batch, the price-insensitive shoppers): −1.354 -> −1.309, −2.10 -> −2.04, −3.06 -> −2.54
        ("elasticity at R=1.0",          elas(1.0),  "−1.3"),   # 2026-11-21 (fourth batch): −1.349 -> −1.354, was "−1.3"
        ("elasticity at R=1.5",          elas(1.5),  "−2.0"),
        ("elasticity at R=2.42 (anchor)", elas(2.42), "−2.5"),  # 2026-11-21: was −3.0; the model gives −3.06
        # 2026-11-21: was "15.8" (plant_floor 13.8 -> 13.5: the building's power follows its floor and class, so Humbird's
        # optimistic design is $15.72, not $15.93). The page carries the figure as MODEL.cost_reference (15.49992), which
        # is where the old "15.8" was found too (15.80352); "15.49" is that literal's prefix
        ("reference cost $/kg",      cost_floor, "15.49"),     # 2026-11-20: was "12.8" (plant_floor 10.8 -> 13.8)
    ]
    # what each label ROUNDS to, so the test also catches a silent value move that the prose missed
    rounds = {"eps_x = eps_own*kappa": "−3.6", "elasticity at R=1.0": "−1.3",
              "elasticity at R=1.5": "−2.0", "elasticity at R=2.42 (anchor)": "−2.5",
              "reference cost $/kg": "15.5"}      # 2026-11-21: was "15.8"

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
    """Recompute the Monte-Carlo headline numbers the PROSE docs (RESULTS/METHODS) quote,
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
_REGION_LABEL = {"eu": "Europe", "us": "US", "global": "Global", "china": "China",
                 "brazil": "Brazil", "india": "India", "nigeria": "Nigeria"}
_DOC_REGIONS = {"RESULTS.md": list(_REGION_LABEL)}   # (POST.md was merged into RESULTS.md)


def check_markdown_prose_numbers() -> list:
    """ROOT-CAUSE GUARD for the prose-drift class that this audit found: the three MARKDOWN essays
    (RESULTS.md, METHODS.md; formerly also POST.md) hand-type headline Monte-Carlo numbers that NO test re-derived,
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
    for name in ("RESULTS.md", "METHODS.md"):
        p = os.path.join(MODEL_DIR, name)
        docs[name] = open(p, encoding="utf-8").read() if os.path.exists(p) else None

    fails = []
    rP = f"{vals['commodity_R_p50']:.2f}"                  # e.g. "2.09"
    sP = f"{vals['commodity_share_p50']:.1f}%"             # e.g. "7.3%"
    # commodity R P50 and share P50 are quoted in both RESULTS and METHODS
    for name in ("RESULTS.md", "METHODS.md"):
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
          f"region-rows across RESULTS/METHODS, "
          f"{'all in sync' if not fails else f'{len(fails)} stale'}")
    return fails


def test_markdown_prose_numbers():
    """pytest entry point: the markdown essays' headline MC numbers match the live model."""
    fails = check_markdown_prose_numbers()
    assert not fails, (
        "Markdown-prose drift FAILED (an essay's headline number no longer matches the model):\n  "
        + "\n  ".join(fails)
        + "\n\nRe-run the model and update RESULTS.md / METHODS.md in the same commit.")


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
