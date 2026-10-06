#!/usr/bin/env python3
"""
build_interactive.py — generate the self-contained interactive explorer.

Reads the constants, slider ranges and per-region market tables straight from
`inputs.py` + `meat_market.py` (the single source of truth) and injects them into
a dependency-free HTML/JS/SVG widget written to `interactive.html`. The JS model
logic MIRRORS market_share.share / meat_market.penetration / uncertainty.R_from_inputs;
the in-page "model self-check" panel reproduces the Python reference numbers so any
drift is visible. Re-run after any change to inputs.py.

    python build_interactive.py
"""
from __future__ import annotations

import json
import os

from inputs import (value, prior, AA_FLOOR, GLUCOSE_OTHER_FLOOR, PASITKA_CONFIGS, MC_COST_INPUTS, MC_DEMAND_INPUTS,
                    MC_TIER_INPUTS, MC_TIMING_INPUTS)
import meat_market as mm
from market_share import (DemandParams, LOSS_AVERSION_RATIO,
                          lusk_at_parity_elasticity as _lusk_at_parity)
from foothold import PRODUCTS as _FOOTHOLD, base_price as _fbase, PRICE_BASIS as _FBASIS


def _pasitka_oh(substr):
    """Overhead ($/kg) for a Pasitka reactor config, matched by a substring of its verbose
    PASITKA_CONFIGS key — keeps the cost-chart numbers tied to the datasheet (no magic dup)."""
    for k, v in PASITKA_CONFIGS.items():
        if substr.lower() in k.lower():
            return v
    raise KeyError(f"no PASITKA_CONFIGS key contains {substr!r}")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "interactive.html")


def _prior_lo_hi(name):
    kind, lo, hi, mode, _ = prior(name)
    return lo, hi


def _prior_lo_mode_hi(name):
    kind, lo, hi, mode, _ = prior(name)
    return lo, mode, hi


def _income_check(dp):
    """[income, R, Python share %] at a non-US income, for the in-page regional self-check.
    The income/alpha normalisation coincides for US (income_ref) regardless of which factor is
    used, so a US-only self-check cannot catch regional income-channel drift — this adds a China
    income point where the two diverge if the JS and Python ever fall out of sync again."""
    from market_share import share as _share
    from cost_model import CostParams, biomass_cost, ratio as cost_ratio
    cp = CostParams()
    R = cost_ratio(biomass_cost(cp, value("media_price"), 1.0), cp)   # Pasitka-base R (~2.42)
    inc = mm.REGION_INCOME["china"]
    return [inc, R, _share(R, dp, income=inc) * 100.0]


def build_model() -> dict:
    dp = DemandParams()        # runs the calibration solve once -> reference solved values for the self-check
    const = {
        "media_intensity": value("media_intensity"),
        "AA_FLOOR": AA_FLOOR,
        "FEEDSTOCK_FLOOR": AA_FLOOR + GLUCOSE_OTHER_FLOOR,
        "glucose_other_floor": GLUCOSE_OTHER_FLOOR,
        "plant_floor": value("plant_floor"),
        "cost_floor": AA_FLOOR + GLUCOSE_OTHER_FLOOR + value("plant_floor"),
        # --- demand: two-segment, four-product discrete-choice (logit) model ---
        # products: w=whole-food, c=conventional, p=plant-based, x=cultivated.
        # the JS mirrors market_share._utilities/share and re-runs the calibration solve.
        "p_conv_anchor": value("p_conv"),       # the $12 commodity anchor: conventional's price in the demand model
        "eps_own": value("eps_own"),
        "cult_sub_mult": value("cult_sub_mult"),  # closeness/substitutability lever
        # the demand price coefficient beta is DERIVED (mirror of market_share._derive_beta):
        # anchored at cultivated's OWN retail price = biomass(base) + markup, solved at its own
        # share via a fixed point. These BASE cost values set that anchor (NOT the live sliders).
        "anchor_media_price": value("media_price"),
        "anchor_overhead": value("overhead"),
        "anchor_markup": value("markup_add"),
        # income (BLP price term): richer => less price-sensitive
        "income_ref": value("income_ref"),
        "income_gradient": value("income_gradient"),
        # product positions (attributes)
        "price_pb_mult": value("price_pb_mult"),
        "price_wf_mult": value("price_wf_mult"),
        "taste_quality_p": value("taste_quality_p"),
        "taste_quality_w": value("taste_quality_w"),
        "w_taste": value("w_taste"),
        # segment weights & the reference-dependent loss aversion (uniform across products)
        "LOSS_AVERSION_RATIO": LOSS_AVERSION_RATIO,   # loss/gain asymmetry (Tversky-Kahneman 2.25)
        "w_eth": value("w_eth"),
        "theta_free_M": value("theta_free_M"),
        "accept_x": value("accept_x"),
        "w_realtissue_E": value("w_realtissue_E"),
        "w_slaughter_E": value("w_slaughter_E"),
        "loss_aversion": value("loss_aversion"),
        "real_tissue_x": value("real_tissue_x"),   # identifying asymmetry, now a dial
        "real_tissue_p": value("real_tissue_p"),
        # HEALTH PERCEPTION — a named ATTRIBUTE on every product, weighted by a segment-specific,
        # SOLVED health weight (w_health_M/E). Positions: whole-food health_w (+, the healthy choice),
        # conventional health_c (slightly -); plant-based / cultivated via their health_p / health_x
        # scenario dials (default 0). The whole-food health premium replaces the old free intercept.
        "health_x": value("health_x"),
        "health_p": value("health_p"),
        "health_w": value("health_w"),
        "health_c": value("health_c"),
        "neophobia_p": value("neophobia_p"),
        "neophobia_p0": value("neophobia_p0"),      # plant-based cold-start (timing)
        # calibration TARGETS the JS solve hits (so calibration-affecting sliders work live)
        "pb_share_target": value("pb_share_target"),
        "pb_mainstream_frac": value("pb_mainstream_frac"),
        "wf_mainstream_target": value("wf_mainstream_target"),
        # Python-SOLVED reference values (for the in-page self-check; JS re-solves and should match)
        "w_realtissue_M_ref": dp.w_realtissue_M,
        "w_health_M_ref": dp.w_health_M,
        "w_health_E_ref": dp.w_health_E,
        # implied at-parity COLD own-price elasticity of cultivated at the default kappa — the
        # quantity Van Loo/Caputo/Lusk 2020 measured; the kappa-validation moment (self-check [4b]).
        # Computed here from the live model (NOT hand-typed) so the prose figure can never go stale —
        # this is the number the {{KAPPA4_LUSK_ELAS}} token in the methods text substitutes.
        "lusk_elas_parity_cold_ref": _lusk_at_parity(dp),
        # REGIONAL income-channel reference: Python share at a Pasitka-base R for a non-US income.
        # Guards against the income/alpha mirror silently drifting again (the US case alone can't —
        # at income_ref both alpha forms coincide). [income, R, Python share %].
        "income_check": _income_check(dp),
        "cleanroom_cost": value("cleanroom_cost"),
        # per-region income (GDP/cap PPP) for the BLP price term
        "REGION_INCOME": mm.REGION_INCOME,
        # demand calibration constants (surfaced so the methods section can show them)
        "PREMIUM_RATIO": mm.PREMIUM_RATIO,
        # WHICH inputs the page's bands sample: the SAME lists the Python bands use (inputs.MC_*),
        # so the page's band and the numbers quoted in RESULTS.md cannot sample different sets.
        "mc_inputs": list(MC_COST_INPUTS + MC_DEMAND_INPUTS + MC_TIER_INPUTS),
        "mc_timing_inputs": list(MC_TIMING_INPUTS),
        # triangular Monte-Carlo priors [lo, mode, hi] for every sampled input
        "priors": {
            **{k: list(_prior_lo_mode_hi(k))
               for k in dict.fromkeys(MC_COST_INPUTS + MC_DEMAND_INPUTS + MC_TIER_INPUTS
                                      + MC_TIMING_INPUTS)},
            # plant-based's own health prior (its band, equal footing with cultivated's health_x)
            "health_p": list(_prior_lo_mode_hi("health_p")),
            # plant-based exploratory dials, also swept so PB gets a band on equal footing
            # with cultivated (its taste a_p, novelty ν_p, cold-start ν_p0). Centred at defaults.
            "a_p": [0.6, 0.8, 1.0],
            "neophobia_p": [-1.0, 0.0, 1.0],
            "neophobia_p0": [-2.0, -1.0, 0.5],
        },
        "years": int(value("years")),   # diffusion horizon for the timing rung
        # tier offsets (meat_market)
        "AUTH_BASIC": mm.AUTH_BASIC, "AUTH_CUT": mm.AUTH_CUT,
        "AUTH_PREMIUM": mm.AUTH_PREMIUM,
        "EPS_MULT_CUT": mm.EPS_MULT_CUT, "EPS_MULT_PREMIUM": mm.EPS_MULT_PREMIUM,
        # reactor configs for the cost chart: [short label, overhead $/kg]. The overhead
        # NUMBERS are read from inputs.PASITKA_CONFIGS (the source of truth) so they can't
        # drift from the datasheet; only the short display labels live here.
        "configs": [["perfusion 20 m³", _pasitka_oh("perfusion")],
                    ["TFF 5 m³", _pasitka_oh("TFF")],
                    ["ATF 0.5 m³", _pasitka_oh("ATF")]],
        # FOOTHOLD products (foothold.py, the strategic entry layer): the per-product ladder the
        # "reachability waterline" panel plots. p_conv & structure feed the SAME R machinery as the
        # cost chart (R = (biomass + scaffold? + markup)/p_conv); the rest are the sourced ordinals
        # for the drill-down. PROVISIONAL sources (see foothold.py) — structure, not the digits, is
        # what the panel demonstrates. no-referent (novel) products are dropped here (no price axis).
        "foothold_products": [
            {"label": p.label, "p_conv": p.p_conv, "structure": p.structure,
             # Option B: p_base = accessible-tier price cultivated actually competes at (rent stripped);
             # "has a prestige tier" is inferred in JS from p_base < p_conv; the prestige VOLUME share is a
             # single global slider (phi), so no per-product phi is injected.
             "p_base": _fbase(p), "source": _FBASIS.get(p.label, "indicative retail tier"),
             "volume_kt": p.volume_kt, "launched_by": p.launched_by, "note": p.note,
             "defect": max(p.defect_health, p.defect_env, p.defect_ethics),
             "defect_ethics": p.defect_ethics, "defect_env": p.defect_env,
             "defect_health": p.defect_health, "authenticity": p.authenticity,
             "tractability": p.tractability, "transferability": p.transferability,
             "regulatory": p.regulatory}
            for p in _FOOTHOLD if not p.no_referent],
        # Comparison products: the SAME demand machinery (reused meat-derived beta) applied to
        # other real-world analog categories, to validate it out-of-sample. Each gives the analog's
        # POSITIONS vs its conventional incumbent and its OBSERVED share. Fields:
        #   pb_mult (price x incumbent), taste (0=parity, <0 deficit), w_rt (real-X weight: how much
        #   "the real thing" matters in that category), wf_mult (outside-option price x: high=weak rival),
        #   K_wf (outside-option intercept; less negative = stronger pull away), obs (observed share %),
        #   note. The plant-based MEAT row uses the model's own calibrated position (its ~1.2% target).
        # health: optional per-product HEALTH-perception offset (utils, + healthier / - less healthy),
        # applied as the analog's health_p position. ILLUSTRATIVE, like the other comparison numbers.
        "comparison_products": {
            "plant-based milk (oat/soy)": {"pb_mult":1.0,"taste":0.0,"w_rt":2.1,"wf_mult":1.2,
                "K_wf":-2.0,"health":0.0,"obs":15.0,"note":"price+taste parity in use (coffee/cereal); no cheap rival",
                "why":{"price":"~parity in use: a splash in coffee/cereal costs about the same (GFI/SPINS)",
                       "taste":"functional parity in its key uses (barista oat/soy froths, tastes fine in cereal)",
                       "rival":"no cheap whole-food substitute for milk-in-coffee → weak outside option",
                       "rt":"a 'not real dairy' gap exists but bites less when price & taste are at parity",
                       "health":"neutral here — dairy (not red meat) is the reference, no health edge either way"}},
            "plant-based meat":           {"pb_mult":1.77,"taste":-0.2,"w_rt":None,"wf_mult":0.25,
                "K_wf":None,"health":0.0,"obs":1.2,"note":"the model's own calibrated meat world (price premium, taste deficit, cheap beans)"},
            "margarine (vs butter)":      {"pb_mult":0.6,"taste":-0.1,"w_rt":1.2,"wf_mult":1.3,
                "K_wf":-2.5,"health":-0.4,"obs":40.0,"note":"ILLUSTRATIVE positions (not calibrated): cheap, near-taste-parity, weak 'real dairy' pull; health PENALTY (butter seen as the more natural/healthier choice since the trans-fat reckoning) → still won big historically on price+habit",
                "why":{"price":"~0.6× butter: margarine is markedly CHEAPER (the historic draw)",
                       "taste":"close but slightly below butter for many uses (−0.1)",
                       "rival":"no cheap third option — you spread butter or margarine (weak outside)",
                       "rt":"a modest 'real dairy' attachment (1.2), weaker than meat's real-tissue pull",
                       "health":"a PENALTY (−0.4): post-trans-fat, butter reads as the more natural choice"}},
            "plant-based 'chicken' nuggets":{"pb_mult":1.3,"taste":-0.1,"w_rt":1.6,"wf_mult":0.5,
                "K_wf":-2.0,"health":0.3,"obs":8.0,"note":"ILLUSTRATIVE positions (not calibrated): processed form hides texture → smaller real-tissue gap than burgers; small health DRAW (plant nuggets read as slightly healthier than the fried-meat version)",
                "why":{"price":"~1.3× the conventional nugget — a premium, but milder than PB burgers",
                       "taste":"close (−0.1): breading/processing masks texture, the usual PB weak spot",
                       "rival":"some cheap alternatives but no dominant whole-food rival (moderate)",
                       "rt":"1.6 — a real-tissue gap, but smaller than a burger's (the nugget form hides it)",
                       "health":"a small DRAW (+0.3): plant nuggets read as slightly healthier than fried meat"}},
            # Cage-free / free-range eggs vs caged eggs — a DIFFERENT mechanism from the rows above, shown for
            # contrast and as a real-world probe of the WELFARE lever (θ_free) the model is humble about.
            # An egg is an egg: NO 'not the real thing' penalty (w_rt≈0), NO taste deficit (taste 0). The only
            # differences are a price premium and a welfare/ethical attribute. Two complementary anchors:
            #   * PRICE anchor (what we model here) = the US, because US shelves still show a real caged-vs-cage-free
            #     price gap a shopper actually faces: cage-free $1.92 vs caged $1.43/doz (+34%, USDA AMS 2024).
            #   * PREFERENCE signal (the cleaner evidence, in the note) = EUROPE's cross-country divergence under
            #     the SAME 2012 cage rules: the UK/Netherlands went heavily non-cage VOLUNTARILY (UK free-range
            #     ~44% pre-ban), while price-sensitive Poland/Spain stayed caged (Poland egg prices +63% in weeks
            #     when forced). Same regulation, opposite uptake -> welfare WTP is REAL but income-gated and
            #     price-fragile: rich/strong-norm markets pay, price-sensitive ones don't. That is exactly the
            #     model's two-segment + income story, and exactly why θ_free defaults to ~0 (a weak, heterogeneous
            #     driver, not a demand engine).
            # The welfare draw is PROXIED via the +offset field (this schema has no per-product θ_free), small +0.4.
            # KEY CAVEATS: (1) different lever than the meat rows (welfare, not authenticity); (2) BOTH US and EU
            # observed shares are heavily MANDATE-DRIVEN (Prop 12 / retailer pledges in the US; the 2012 EU cage
            # ban), NOT pure willingness-to-pay — so matching ~39% is NOT a clean validation, and the clean
            # revealed-preference signal (pre-mandate voluntary share, the attitude-behaviour gap) is that welfare
            # rarely survives a price premium at the register; (3) β is anchored to MEAT $/kg, so it responds to the
            # 1.34x RATIO, not the trivial ~$0.49/doz absolute gap — the price term is too weak here. Read the
            # DIRECTION (premium down, welfare up, both modest), never the number.
            "free-range vs caged eggs":   {"pb_mult":1.34,"taste":0.0,"w_rt":0.0,"wf_mult":5.0,
                "K_wf":-3.0,"health":0.4,"obs":39.0,"note":"DIFFERENT mechanism (a welfare probe, not a meat analog): an egg is an egg — NO 'not real' penalty, NO taste deficit. Anchors: US price gap +34% (cage-free $1.92 vs caged $1.43/doz, USDA AMS 2024) for the MODELLED premium; Europe's cross-country split for PREFERENCE (UK/NL went non-cage voluntarily, price-sensitive Poland/Spain didn't — welfare WTP is real but income-gated & price-fragile). CAVEATS: observed ~39% is MANDATE-driven (US Prop 12 / EU 2012 cage ban), NOT willingness-to-pay; β is meat-anchored so it sees the ratio not the trivial ~$0.49/doz gap. Read the DIRECTION, not the number — this is why the model keeps θ_free ≈ 0.",
                "why":{"price":"+34% measured US shelf premium (cage-free $1.92 vs caged $1.43/doz, USDA AMS 2024)",
                       "taste":"zero deficit — a free-range egg is sensorily identical to a caged one",
                       "rival":"no cheap third option: the caged egg IS the cheap reference (weak outside)",
                       "rt":"zero penalty — nobody thinks a free-range egg is a 'fake egg' (unlike PB meat)",
                       "health":"a small WELFARE draw (+0.4), proxied here (the schema has no per-product θ_free); kept small because revealed WTP for welfare is weak & price-fragile"}},
        },
        # every tweakable slider -> [symbol (HTML), where it enters the equations].
        # keyed by slider key; rendered as two extra columns of the parameter table (appendix A9).
        "param_symbols": {
            "media_price":   ["p<sub>med</sub>", "medium cost &iota;&eta;p<sub>med</sub> in Eq. (1)"],
            "efficiency":    ["&eta;", "medium cost &iota;&eta;p<sub>med</sub> in Eq. (1)"],
            "overhead":      ["h", "plant running cost in Eq. (1)"],
            "scaffold":      ["k", "Eq. (1), structured cuts only"],
            "markup_add":    ["m", "Eq. (1)"],
            "meat_tax":      ["t", "denominator of Eq. (1)"],
            "income":        ["y", "income term &alpha;&thinsp;ln(y<sub>eff</sub>&minus;p<sub>j</sub>) in Eq. (2); A2"],
            "income_gradient": ["&phi;", "y<sub>eff</sub> = y<sub>ref</sub>(y/y<sub>ref</sub>)<sup>&phi;</sup>; A2"],
            "eps_own":       ["&epsilon;", "sets the price weight &beta;; A1"],
            "cult_sub_mult": ["&kappa;", "sets the price weight &beta;; A1"],
            "loss_aversion": ["&lambda;", "reference-price term &minus;&lambda;(d<sub>j</sub>)<sup>+</sup>+(d<sub>j</sub>)<sup>&minus;</sup> in Eq. (2); A3"],
            "accept_x":      ["a<sub>x</sub>", "taste term w<sup>t</sup>(a<sub>x</sub>&minus;1) in Eq. (2)"],
            "neophobia_x":   ["&nu;<sub>x</sub>", "novelty term in Eq. (2); long-run end of Eq. (5)"],
            "neophobia_p":   ["&nu;<sub>p</sub>", "plant-based novelty term in Eq. (2)"],
            "a_p":           ["a<sub>p</sub>", "plant-based taste term in Eq. (2)"],
            "R_p":           ["R<sub>p</sub>", "plant-based price in Eq. (2)"],
            "theta_free_M":  ["&theta;", "mainstream no-slaughter weight w<sup>s</sup> in Eq. (2)"],
            "w_eth":         ["w<sub>eth</sub>", "segment mix, Eq. (3)"],
            "premium_resistance": ["&rho;", "scales the tier offsets &tau; and &psi;; A5"],
            "real_tissue_x": ["b<sub>x</sub>", "real-meat term w<sup>rt</sup>b<sub>x</sub> in Eq. (2)"],
            "real_tissue_p": ["b<sub>p</sub>", "plant-based real-meat term in Eq. (2)"],
            "health_x":      ["&zeta;<sub>x</sub>", "health term w<sup>h</sup>&zeta;<sub>x</sub> in Eq. (2)"],
            "health_p":      ["&zeta;<sub>p</sub>", "plant-based health term in Eq. (2)"],
            "auth_basic":    ["&tau;<sub>mince</sub>", "cultivated's authenticity term in Eq. (2); A5"],
            "auth_cut":      ["&tau;<sub>cut</sub>", "cultivated's authenticity term in Eq. (2); A5"],
            "auth_premium":  ["&tau;<sub>prem</sub>", "cultivated's authenticity term in Eq. (2); A5"],
            "w_taste":       ["w<sup>t</sup>", "taste weight in Eq. (2); A4"],
            "w_realtissue_M": ["w<sup>rt</sup><sub>M</sub>", "real-meat weight in Eq. (2), mainstream; A4"],
            "w_realtissue_E": ["w<sup>rt</sup><sub>E</sub>", "real-meat weight in Eq. (2), ethical; A4"],
            "w_health_M":    ["w<sup>h</sup><sub>M</sub>", "health weight in Eq. (2), mainstream; A4"],
            "w_health_E":    ["w<sup>h</sup><sub>E</sub>", "health weight in Eq. (2), ethical; A4"],
            "w_slaughter_E": ["w<sup>s</sup><sub>E</sub>", "no-slaughter weight in Eq. (2), ethical; A4"],
            "neophobia_x0":  ["&nu;<sub>x0</sub>", "starting novelty in Eq. (5)"],
            "neophobia_p0":  ["&nu;<sub>p0</sub>", "plant-based starting novelty in Eq. (5)"],
            "accept_rate":   ["r", "fade speed in Eq. (5)"],
            "p_innov":       ["p<sub>B</sub>", "Bass rollout F(t) in Eq. (5)"],
            "q_imit":        ["q<sub>B</sub>", "Bass rollout F(t) in Eq. (5)"],
            "phi":           ["&chi;", "reachable volume (1&minus;&chi;)Q; A6"],
        },
    }

    def slider(key, label, unit, lo, hi, step, default, src, tip, fmt="num"):
        return dict(key=key, label=label, unit=unit, min=lo, max=hi, step=step,
                    default=default, src=src, tip=tip, fmt=fmt)

    # Rail layout: the KEY assumptions first (always visible), then everything else inside one
    # collapsed "Advanced" section, grouped by the model step it belongs to (the same Step 1-4 the
    # methods and the four-step strip at the top use). (name, keys, advanced?)
    SLIDER_GROUPS = [
        ("Key assumptions",
         ["media_price", "overhead", "markup_add", "meat_tax",
          "real_tissue_x", "accept_x", "theta_free_M", "premium_resistance"], False),
        ("Step 1 · cost and price", ["efficiency", "scaffold"], True),
        ("Step 2 · how shoppers choose",
         ["eps_own", "cult_sub_mult", "loss_aversion", "income", "income_gradient", "w_eth",
          "health_x", "neophobia_x"], True),
        ("Step 2 · plant-based meat", ["R_p", "a_p", "real_tissue_p", "health_p", "neophobia_p"], True),
        ("Step 3 · authenticity by tier", ["auth_basic", "auth_cut", "auth_premium"], True),
        ("Step 4 · over time",
         ["neophobia_x0", "accept_rate", "p_innov", "q_imit", "neophobia_p0"], True),
        ("Entry points (chart 7)", ["phi"], True),
        ("Expert · attribute weights",
         ["w_taste", "w_realtissue_M", "w_health_M", "w_health_E", "w_slaughter_E",
          "w_realtissue_E"], True),
    ]

    # Tooltips follow one pattern: what it is -> what moving it does (with a model-computed number,
    # via {{TOKEN}}, where that helps) -> default and source. Kept short on purpose; the methods
    # section carries the detail.
    sliders = [
        # ---- key assumptions ------------------------------------------------------------
        slider("media_price", "Medium price (<i>p</i><sub>med</sub>)", "$/L", 0.10, 1.00, 0.01,
               value("media_price"), "Pasitka / GFI",
               tip="Price of the nutrient liquid the cells grow in, the biggest single cost. $0.63/L "
               "(default) is the only peer-reviewed measurement (Pasitka 2024). Companies report $0.20/L "
               "or less, unverified; $1.00/L is the case where a process doesn't match Pasitka's. Each "
               "$0.10/L adds about ${{MEDIA_PER_010}}/kg."),
        slider("overhead", "Plant running cost (<i>h</i>)", "$/kg", 6.0, 24.7, 0.1, 9.9, "Pasitka",
               tip="Everything except the medium, per kg: reactors and other capital, labour, energy, "
               "consumables. Set mainly by reactor scale, and the least demonstrated number in the model. "
               "Pasitka's three designs: $24.7 (many small vessels), $9.9 (default), $7.9 (large perfusion "
               "reactors). About $6 is the floor for a very large, efficient plant."),
        slider("markup_add", "Retail markup (<i>m</i>)", "$/kg", 2.0, 7.0, 0.1, value("markup_add"),
               "USDA spread",
               tip="Processing, packaging, cold chain and retail margin, added per kg. Default $5 is about "
               "conventional meat's farm-to-retail spread (USDA). Price parity needs production cost below "
               "the meat price minus this markup, so it matters a lot. Adding it per kg rather than as a "
               "percentage is an assumption."),
        slider("meat_tax", "Meat price multiplier (<i>t</i>)", "x", 0.8, 1.6, 0.05, 1.0, "policy",
               tip="Multiplies every conventional meat price, e.g. a meat or carbon tax. 1.0 = today's "
               "prices. A multiplier of 1.25 lowers cultivated's price ratio as much as cutting all its "
               "costs by 20%."),
        slider("real_tissue_x", "Seen as real meat (<i>b</i><sub>x</sub>)", "0→1", 0.0, 1.0, 0.05,
               value("real_tissue_x"), "premise",
               tip="The model's central premise: shoppers count cultivated as real animal meat, so it "
               "competes head-on with conventional meat. Share at equal price: 1 (default) → "
               "~{{BX_10}}%, 0.75 → ~{{BX_075}}%, 0.5 → ~{{BX_05}}%, 0.25 → ~{{BX_025}}%, 0 (treated "
               "like a veggie burger) → ~{{BX_00}}%. Not sampled in the Monte Carlo."),
        slider("accept_x", "Taste vs conventional (<i>a</i><sub>x</sub>)", "", 0.6, 1.2, 0.05, 1.0,
               "judgement",
               tip="How good cultivated tastes next to the conventional product (1 = just as good). Share "
               "at equal price: 1 → ~{{PARITY_NEUTRAL}}%, 0.8 → ~{{AX_08}}%, 0.6 → ~{{AX_06}}%, 1.1 "
               "(tastier) → ~{{AX_11}}%. A judgement call: nobody has tasted it at scale. Sampled in the "
               "Monte Carlo."),
        slider("theta_free_M", "Mainstream values “no slaughter” (&theta;)", "", 0.0, 1.5, 0.05, 0.0,
               "judgement",
               tip="How much mainstream shoppers (95% of people) care that no animal was killed. 0 "
               "(default) = not at all. Raising it lifts every slaughter-free option, cultivated most. "
               "Share at equal price: 0.5 → ~{{TH_05}}%, 1 → ~{{TH_10}}%. Sampled in the Monte Carlo "
               "(0 to 1)."),
        slider("premium_resistance", "Premium resistance (&rho;)", "x", 0.0, 2.0, 0.1,
               value("premium_resistance"), "judgement",
               tip="How strongly cuts and premium meat resist cultivated compared with mince. Scales both "
               "the authenticity penalties and the lower price sensitivity of pricier tiers: 1 = default, "
               "0 = no tier effect (wagyu as easy as mince), 2 = double. No direct data, so the Monte "
               "Carlo samples 0.5 to 1.5."),
        # ---- step 1: cost and price ----------------------------------------------------------
        slider("efficiency", "Cell efficiency (&eta;)", "x", 0.25, 1.0, 0.05, value("efficiency"),
               "Pasitka / CHO",
               tip="Medium used per kg, relative to Pasitka's measured cells (1 = default). 0.25 = four "
               "times leaner, like the CHO cells used in pharma, not yet shown for food cells. The Monte "
               "Carlo samples 0.25 to 1, so its median assumes some improvement."),
        slider("scaffold", "Scaffold cost for cuts (<i>k</i>)", "$/kg", 0.0, 12.0, 0.5, mm.SCAF,
               "assumed",
               tip="Extra cost to turn cells into a structured cut (steak, fillet); mince doesn't need it. "
               "No published study covers it (Humbird, CE Delft and Risner all stop at unstructured "
               "cells), so the $6 default is a guess."),
        # ---- step 2: how shoppers choose -----------------------------------------------------
        slider("eps_own", "Price sensitivity of meat (&epsilon;)", "", -1.4, -0.5, 0.05,
               value("eps_own"), "scanner data",
               tip="How much meat purchases fall when prices rise: −0.9 (default) means 1% dearer, 0.9% "
               "fewer purchases (Andreyeva 2010; meta-analyses span −0.7 to −1.0). A single cultivated "
               "product is &kappa; times more sensitive than this. Sampled in the Monte Carlo."),
        slider("cult_sub_mult", "Closeness to conventional (&kappa;)", "x", 3.0, 6.0, 0.5,
               value("cult_sub_mult"), "Lusk 2020",
               tip="How many times more price-sensitive a cultivated product is than meat as a whole: it "
               "has a near-identical substitute on the same shelf. Mostly matters above parity: at "
               "today's price, &kappa; = 3 → ~{{KAPPA_3}}%, 4 → ~{{KAPPA_4}}%, 5 → ~{{KAPPA_5}}%. "
               "Default 4 fits Lusk 2020's measured range (appendix A1)."),
        slider("loss_aversion", "Loss aversion (&lambda;)", "ratio", 1.0, 2.25, 0.05,
               value("loss_aversion"), "off by default",
               tip="Makes paying more than the conventional price hurt more than an equal discount helps. "
               "1 (default) = symmetric; up to Tversky and Kahneman's 2.25. Barely moves the result, "
               "because the price weight is re-fitted: at today's price, 1 → ~{{LAMBDA_1}}%, 2.25 → "
               "~{{LAMBDA_225}}%."),
        slider("income", "Income (<i>y</i>, GDP per person)", "$/yr", 5000, 5000000, 1000,
               value("income_ref"), "World Bank",
               tip="Average income (PPP), set by the region selector. Poorer shoppers feel the same "
               "premium more, so they buy less of a pricier product. You can drag it far beyond today's "
               "richest country."),
        slider("income_gradient", "Income damping (&phi;)", "exp", 0.0, 1.0, 0.05,
               value("income_gradient"), "Muhammad / ERS",
               tip="How strongly income changes price sensitivity. 1 = the raw economic form, too steep "
               "for food; 0.5 (default) matches the roughly 2× rich-to-poor gap in food price sensitivity "
               "(Muhammad et al. 2011); 0 = no income effect. US results don't depend on it."),
        slider("w_eth", "Ethical shoppers (<i>w</i><sub>eth</sub>)", "", 0.04, 0.10, 0.01,
               value("w_eth"), "Gallup",
               tip="Share of vegetarians and vegans, who strongly value “no slaughter” and mostly eat "
               "beans and other whole foods. Default 5% (Gallup 2023). Moving it re-fits the model so "
               "plant-based stays at its observed ~1.2%."),
        slider("health_x", "Cultivated health image (&zeta;<sub>x</sub>)", "utils", -1.0, 1.0, 0.05,
               0.0, "scenario",
               tip="How healthy cultivated meat is perceived to be: + for “clean, no antibiotics”, − for "
               "“lab-grown, ultra-processed”. Default 0 because surveys find both and they roughly "
               "cancel. Near equal price, +0.5 adds about 10 points. Sampled in the Monte Carlo (±0.5)."),
        slider("neophobia_x", "Cultivated long-run novelty (&nu;<sub>x</sub>)", "utils", -2.0, 1.0,
               0.1, value("neophobia_x"), "judgement",
               tip="Where wariness of a new food settles once cultivated is familiar: − = a lasting “is it "
               "natural?” doubt, + = a lasting draw, 0 = neutral (default). Share at equal price: −1 → "
               "~{{NX_NEG1}}%, 0 → ~{{PARITY_NEUTRAL}}%, +1 → ~{{NX_POS1}}%. Sampled in the Monte Carlo."),
        # ---- step 2: plant-based meat --------------------------------------------------------
        slider("R_p", "Plant-based price (<i>R</i><sub>p</sub>)", "x", 0.2, 3.0, 0.05,
               value("price_pb_mult"), "GFI / NIQ",
               tip="Plant-based meat's price relative to conventional. Default 1.77× (+77%, GFI/NIQ). "
               "Set it to 1 to ask what happens if plant-based reached price parity."),
        slider("a_p", "Plant-based taste (<i>a</i><sub>p</sub>)", "", 0.4, 1.1, 0.05,
               round(1 + value("taste_quality_p"), 2), "NECTAR",
               tip="Plant-based taste next to conventional (1 = as good). Default 0.8: only ~16% of "
               "products match conventional meat in blind tastings (NECTAR 2025)."),
        slider("real_tissue_p", "Plant-based seen as real meat (<i>b</i><sub>p</sub>)", "0→1", 0.0,
               1.0, 0.05, value("real_tissue_p"), "0 by definition",
               tip="The same premise for plant-based, which isn't animal tissue (0). This is the only "
               "built-in difference between the two alternatives. Set it to 1 and plant-based rises to "
               "~{{BP_1_PB}}% at its current price."),
        slider("health_p", "Plant-based health image (&zeta;<sub>p</sub>)", "utils", -1.0, 1.0, 0.05,
               0.0, "scenario",
               tip="How healthy plant-based meat is perceived to be: + for “good for you”, − for "
               "“ultra-processed”. Default 0. Sampled in its band (±0.5)."),
        slider("neophobia_p", "Plant-based long-run novelty (&nu;<sub>p</sub>)", "utils", -2.0, 1.0,
               0.1, value("neophobia_p"), "scenario",
               tip="Plant-based's lasting attitude as a new food (− wary, + drawn; default 0). Its real "
               "resistance is already in the calibration, so this is a what-if."),
        # ---- step 3: authenticity by tier ----------------------------------------------------
        slider("auth_basic", "Authenticity: mince (&tau;<sub>mince</sub>)", "utils", -1.0, 1.0, 0.05,
               mm.AUTH_BASIC, "judgement", fmt="signed",
               tip="Bonus or penalty for cultivated in everyday mince and processed meat. Default +0.2: "
               "nobody misses “the real thing” in a nugget, and “cleaner meat” helps. Scaled by premium "
               "resistance. No direct data."),
        slider("auth_cut", "Authenticity: cuts (&tau;<sub>cut</sub>)", "utils", -2.0, 1.0, 0.05,
               mm.AUTH_CUT, "judgement", fmt="signed",
               tip="The same for steaks and fillets. Default −0.4: some shoppers want the real cut. "
               "Scaled by premium resistance. No direct data."),
        slider("auth_premium", "Authenticity: premium (&tau;<sub>prem</sub>)", "utils", -3.0, 0.5,
               0.05, mm.AUTH_PREMIUM, "judgement", fmt="signed",
               tip="The same for luxury products (wagyu, sushi-grade fish). Default −1.5: the genuine "
               "article is the point. This caps premium shares even where cultivated is cheaper. Scaled "
               "by premium resistance. No direct data."),
        # ---- step 4: over time ---------------------------------------------------------------
        slider("neophobia_x0", "Cultivated novelty today (&nu;<sub>x0</sub>)", "utils", -3.5, 1.5, 0.1,
               value("neophobia_x0"), "Lusk / GFI",
               tip="How wary shoppers are of cultivated meat today: where the adoption curve starts. "
               "Default −2.8 matches a US experiment where only ~5% chose lab-grown at the same price as "
               "beef (Van Loo, Caputo &amp; Lusk 2020). Warmer survey framings reach ~60% (about "
               "+{{NX0_60}}). The slider runs from −3.5 (~{{NX0_MIN}}%) to +1.5 (~{{NX0_WARM}}%). Changes timing, "
               "not the long-run ceiling."),
        slider("accept_rate", "Familiarity speed (<i>r</i>)", "1/exp", 0.05, 0.50, 0.01,
               value("accept_rate"), "assumed",
               tip="How fast wariness fades as people keep seeing the product. Changes when adoption "
               "levels off, not where: 0.15 (default) → about year {{STAB_YEAR}}; 0.5 → about year "
               "{{STAB_R05}}; 0.05 → still climbing at year 30. No direct estimate; the default "
               "matches the decades-long uptake of other radically new foods. Sampled."),
        slider("p_innov", "Rollout: early adopters (<i>p</i><sub>B</sub>)", "1/yr", 0.005, 0.05, 0.005,
               value("p_innov"), "Bass lit.",
               tip="How fast independent early adopters take it up (Bass diffusion). With word of mouth, "
               "it sets the speed of the S-curve, not its height. Default 0.02, near the cross-study "
               "norm (0.01 to 0.03)."),
        slider("q_imit", "Rollout: word of mouth (<i>q</i><sub>B</sub>)", "1/yr", 0.20, 0.60, 0.05,
               value("q_imit"), "Bass lit.",
               tip="How fast existing buyers pull in new ones (Bass diffusion). Default 0.40, near the "
               "cross-study norm (0.3 to 0.5)."),
        slider("neophobia_p0", "Plant-based novelty at launch (&nu;<sub>p0</sub>)", "utils", -2.0, 0.5,
               0.1, value("neophobia_p0"), "scenario",
               tip="Plant-based's starting wariness (default −1), for the green line in chart 5. It fades "
               "like cultivated's, yet plant-based stalls anyway: its taste and price gaps don't fade."),
        # ---- entry points (chart 7) ----------------------------------------------------------
        slider("phi", "Prestige share (&chi;)", "", 0.0, 0.95, 0.05, 0.25, "salmon / ibérico",
               tip="Share of a luxury market held by buyers who want the genuine article at any price, "
               "and so are out of cultivated's reach (chart 7). Default 0.25, from the only two published "
               "splits: wild salmon (~25% of supply) and bellota ibérico (~20%). 0 = all reachable."),
        # ---- expert: attribute weights (the multipliers in Eq. 2) -----------------------------
        # Normally FIXED (w_taste, w_slaughter_E, w_realtissue_E) or SOLVED to data (w_realtissue_M,
        # w_health_M, w_health_E). The three SOLVED ones carry solved=True + warn=...: they stay AUTO
        # (solved live) until you tick "override", which pins them and breaks the fact in the warning.
        slider("w_taste", "Taste weight (<i>w</i><sup>t</sup>)", "utils", 1.0, 10.0, 0.5,
               value("w_taste"), "Malone &amp; Lusk 2017",
               tip="How much taste matters: the scale every other weight is read against (only "
               "differences between scores matter). Default 5, anchored to willingness-to-pay studies "
               "that rank taste first (taste ≈ 2× health, 3× safety). Changing it re-fits the others."),
        slider("w_realtissue_M", "Mainstream real-meat weight (<i>w</i><sup>rt</sup><sub>M</sub>)",
               "utils", 0.0, 6.0, 0.05, round(dp.w_realtissue_M, 2), "solved",
               tip="How much mainstream shoppers value real animal tissue: why cultivated takes buyers "
               "from conventional meat rather than from plant-based. Solved so ~89% of plant-based buyers "
               "are mainstream (GFI 2024). Override to set your own; the model then stops matching that "
               "fact."),
        slider("w_health_M", "Mainstream health weight (<i>w</i><sup>h</sup><sub>M</sub>)", "utils",
               0.0, 4.0, 0.05, round(dp.w_health_M, 2), "solved",
               tip="How much mainstream shoppers weigh health: the pull toward beans over a veggie burger. "
               "Solved so ~6% of mainstream meals skip meat by choice. It comes out at "
               "{{HEALTH_TASTE_RATIO}}× the taste weight, lighter than the ~0.5× in willingness-to-pay "
               "studies. Override to set your own."),
        slider("w_health_E", "Ethical health weight (<i>w</i><sup>h</sup><sub>E</sub>)", "utils", 0.0,
               6.0, 0.05, round(dp.w_health_E, 2), "solved",
               tip="The ethical shoppers' health weight. Solved (~{{HEALTH_E}}) so that a 5% ethical "
               "group adds only a little to plant-based meat: most of them choose beans. Override to set "
               "your own; plant-based then drifts from its ~1.2%."),
        slider("w_slaughter_E", "Ethical no-slaughter weight (<i>w</i><sup>s</sup><sub>E</sub>)",
               "utils", 1.0, 8.0, 0.5, value("w_slaughter_E"), "assumed",
               tip="How strongly the 5% ethical shoppers value “no animal killed” (default 4, assumed). "
               "Gives cultivated a small ethical niche even above parity. The calibration re-fits around "
               "it."),
        slider("w_realtissue_E", "Ethical real-meat weight (<i>w</i><sup>rt</sup><sub>E</sub>)",
               "utils", 0.0, 4.0, 0.05, value("w_realtissue_E"), "assumed ≈ 0",
               tip="How much ethical shoppers value real animal tissue. Assumed about 0: they choose on "
               "“no slaughter”, not “is it meat”. Raising it makes them favour both real meats, which "
               "helps cultivated a little (they are 5% of shoppers)."),
    ]

    # income uses a LOG scale (the $5k–$5M range spans three orders of magnitude)
    for _s in sliders:
        if _s["key"] == "income":
            _s["logscale"] = True

    # SOLVED weights: the UI renders an "override" checkbox plus a warning naming the data fact the
    # override breaks. w_taste / w_slaughter_E / w_realtissue_E are inputs (not solved), so changing
    # them just re-solves the others; they carry no warning.
    _SOLVED_WARN = {
        "w_realtissue_M": "Override on: this weight is pinned, so the model no longer reproduces the "
                          "~89% mainstream share of plant-based buyers it was fitted to (GFI).",
        "w_health_M": "Override on: this weight is pinned, so the ~6% mainstream meatless rate is no "
                      "longer matched.",
        "w_health_E": "Override on: this weight is pinned, so plant-based no longer stays at its "
                      "observed ~1.2%.",
    }
    for _s in sliders:
        if _s["key"] in _SOLVED_WARN:
            _s["solved"] = True
            _s["warn"] = _SOLVED_WARN[_s["key"]]

    # A logit identifies only DIFFERENCES in scores, and the taste weight sets the scale every other
    # weight is read against. So these sliders also show their value as a multiple of taste
    # (e.g. "0.85 → 0.17× taste"): that ratio is the factor's relative importance.
    # (Not on the key "no slaughter" slider: there the ratio is expert detail and clutters the readout.)
    _WNORM = {"w_taste", "w_slaughter_E", "w_realtissue_M", "w_realtissue_E",
              "w_health_M", "w_health_E", "auth_basic", "auth_cut", "auth_premium"}
    for _s in sliders:
        if _s["key"] in _WNORM:
            _s["wnorm"] = True

    # PRICE has a weight too, the coefficient β, but it is DERIVED from ε·κ (appendix A1). The two
    # sliders that set it show the live β and the resulting elasticity in their readout.
    for _s in sliders:
        if _s["key"] in ("eps_own", "cult_sub_mult"):
            _s["pricew"] = True

    # --- apply the rail layout: tag each slider with its group (+ advanced flag) and reorder ---
    _by_key = {s["key"]: s for s in sliders}
    _grouped = []
    for _gname, _keys, _adv in SLIDER_GROUPS:
        for _k in _keys:
            if _k in _by_key:
                _by_key[_k]["group"] = _gname
                _by_key[_k]["adv"] = _adv
                _grouped.append(_by_key.pop(_k))
    if _by_key:                                   # every slider must be placed in exactly one group
        raise RuntimeError(f"sliders missing from SLIDER_GROUPS: {sorted(_by_key)}")
    sliders = _grouped

    toggles = [
        dict(key="cleanroom", label="Add Humbird's clean-room cost (to <i>h</i>)",
             add=value("cleanroom_cost"),
             group="Step 1 · cost and price",   # it adds to the plant running cost h
             tip="Adds Humbird's cost for clean-room, pharma-style buildings (about +$" +
             ("%.0f" % value("cleanroom_cost")) + "/kg). Pasitka's numbers assume a cheaper "
             "food-grade facility."),
    ]

    markets = {
        region: [dict(name=mt.name, p_conv=mt.p_conv, w_vol=mt.w_vol,
                      structured=(mt.scaffold > 0), cost_mult=mt.cost_mult)
                 for mt in market]
        for region, market in mm.MARKETS.items()
    }
    regions = [["us", "US"], ["eu", "Europe"], ["china", "China"], ["global", "Global"],
               ["brazil", "Brazil"], ["india", "India"], ["nigeria", "Nigeria"]]
    return dict(const=const, sliders=sliders, toggles=toggles, markets=markets, regions=regions)


# ---------------------------------------------------------------------------
# Python cross-check: recompute the reference numbers with the SAME formulas we
# inject, to confirm the constants/markets are the ones the model uses.
# ---------------------------------------------------------------------------
def crosscheck(model: dict) -> None:
    from market_share import DemandParams, share
    from cost_model import CostParams, biomass_cost
    cp = CostParams()
    R = (biomass_cost(cp, 0.63, 1.0) + value("markup_add")) / value("p_conv")
    pr = DemandParams()
    pb = share(1.0, pr, cultivated_present=False, which="pb")
    s0 = share(1.0, pr)                       # neutral defaults (accept_x=1, theta_free_M=0)
    print(f"  cross-check (Python): basic R={R:.2f}  PB(no cult)={pb*100:.2f}%  "
          f"share@parity(neutral)={s0*100:.1f}%")


def weights_table_rows() -> str:
    """Model-GENERATED rows for the 'attribute weights, and how each is pinned' table — pulled
    live from the solved DemandParams so the values can never go stale (mirrors the file's
    single-source-of-truth / anti-drift discipline). Answers the reader's 'why can't I tweak the
    weights?': SOLVED = pinned by a calibration moment, FIXED = a normalisation/assumption,
    SLIDER = yours, DERIVED = built from the elasticity target."""
    from market_share import DemandParams, share
    dp = DemandParams()
    def row(name, sym, M, E, how):
        return (f'<tr><td>{name}</td><td style="white-space:nowrap">{sym}</td>'
                f'<td class="n">{M}</td><td class="n">{E}</td><td class="s">{how}</td></tr>')
    # --- live derivation of the price coefficients beta (logit slope) and alpha (BLP constant) ---
    kap, eps = dp.cult_sub_mult, dp.eps_own
    eps_x = kap * eps                                          # the own-price elasticity TARGET
    p_x, p_c, lam, y = dp.anchor_price, dp.p_conv, dp.loss_aversion, dp.income_ref
    s_x = share(p_x / p_c, dp, accept_x=1.0, theta_free_M=0.0, # cultivated's own neutral share at the anchor
                neophobia_x=0.0, neophobia_p=0.0)
    beta = dp.beta_ref
    alpha = -beta * (y - p_x)
    price_row = (
        '<tr><td>price</td><td style="white-space:nowrap">&alpha;, &beta;</td>'
        f'<td class="n" colspan="2">&beta; = {beta:.3f}<br>&alpha; = {alpha:,.0f}'
        '<br><span style="color:#888;font-size:.85em">(shared by both)</span></td>'
        '<td class="s"><b>DERIVED</b> from the price-sensitivity target '
        f'&epsilon;<sub>x</sub> = &kappa;&epsilon; = {kap:.0f}&times;({eps}) = <b>{eps_x:.1f}</b> (A1), at cultivated&rsquo;s '
        f'own price p<sub>x</sub> = ${p_x:.0f}/kg and share s<sub>x</sub> = {s_x*100:.0f}%: '
        f'&beta; = &epsilon;<sub>x</sub>/[p<sub>x</sub>(1&minus;s<sub>x</sub>)] + &lambda;/p<sub>c</sub> = '
        f'{eps_x:.1f}/[{p_x:.0f}&middot;{1-s_x:.2f}] + {lam:.0f}/{p_c:.0f} = <b>{beta:.3f}</b>; then '
        f'&alpha; = &minus;&beta;(y<sub>ref</sub>&minus;p<sub>x</sub>) = <b>{alpha:,.0f}</b> (large only because '
        'differences in log income are tiny). p<sub>x</sub> is computed from the default costs, not typed in; the '
        'page&rsquo;s cost sliders change cultivated&rsquo;s price but not this calibration point.</td></tr>'
    )
    rows = [
        price_row,
        row("taste", "w<sup>t</sup>", f"{dp.w_taste:.2f}", f"{dp.w_taste:.2f}",
            '<b>FIXED</b> scale: only differences between scores matter, so taste sets the scale for every other '
            'weight (anchored to willingness-to-pay studies). Expert slider.'),
        row("no slaughter", "w<sup>s</sup>", f"{dp.theta_free_M:.2f}", f"{dp.w_slaughter_E:.1f}",
            'mainstream = <b>SLIDER</b> (&theta;, default 0); ethical = <b>FIXED</b> assumption (large: it is what '
            'defines the ethical shopper)'),
        row("real meat", "w<sup>rt</sup>", f"{dp.w_realtissue_M:.2f}", f"{dp.w_realtissue_E:.2f}",
            'mainstream = <b>SOLVED</b> so ~89% of plant-based buyers are mainstream; ethical = <b>FIXED</b> '
            '&asymp;0 (they choose on &ldquo;no slaughter&rdquo;, not &ldquo;is it meat&rdquo;)'),
        row("health", "w<sup>h</sup>", f"{dp.w_health_M:.2f}", f"{dp.w_health_E:.2f}",
            'both <b>SOLVED</b>: the mainstream meatless rate (~6%) and the ethical shoppers&rsquo; plant-based '
            'share'),
        row("loss aversion", "&lambda;", f"{dp.loss_aversion:.2f}", f"{dp.loss_aversion:.2f}",
            '<b>SLIDER</b>, default 1 = symmetric (A3)'),
        row("segment mix", "w<sub>eth</sub>", "&mdash;", f"{dp.w_eth*100:.0f}%",
            '<b>SLIDER</b> (Gallup: 5% vegetarian or vegan); moving it re-solves the calibration'),
    ]
    return "\n        ".join(rows)


# ---------------------------------------------------------------------------
# Illustrative numbers, COMPUTED FROM THE MODEL at build time.
# The methodology prose and the slider tooltips quote example shares ("at parity
# 0.8 -> ~27%", "kappa=3 keeps ~14%", ...). Hand-typing those invites DRIFT: a
# recalibration (e.g. the health-attribute refactor that lifted every at-parity
# figure ~2-3pp) silently leaves the prose stale and self-contradictory. So we
# compute every illustrative figure here, from the SAME model the page runs, and
# substitute it into the prose via {{TOKEN}} placeholders. Change a coefficient and
# the prose updates itself; the placeholders can never go out of sync.
# ---------------------------------------------------------------------------
def illustrative_numbers() -> dict:
    """Return {TOKEN: "NN"} for every illustrative share quoted in the prose/tooltips.
    Each is rounded to a whole percent, matching how the prose reads ("~50%")."""
    from market_share import DemandParams, share
    from cost_model import CostParams, biomass_cost, ratio as cost_ratio

    cp = CostParams()
    R_today = cost_ratio(biomass_cost(cp, 0.63, 1.0), cp)     # today's basic R (~2.42)
    base = DemandParams()                                     # central calibration

    def pc(x):                                                # share% as a rounded whole number
        return f"{round(x * 100)}"

    def at_parity(**kw):                                      # cultivated share at R=1, central calib
        return share(1.0, base, **kw)

    def resolved(R, **dp_kwargs):                             # re-solve calibration, then share at R
        return share(R, DemandParams(**dp_kwargs), accept_x=1.0, theta_free_M=0.0)

    from cost_model import cost_floor
    from adoption_timing import TimingParams, simulate
    bio = biomass_cost(cp, 0.63, 1.0)
    pen = {r: mm.penetration(mm.MARKETS[r], bio, income=mm.REGION_INCOME[r])[1:]   # (vol, val) totals
           for r in ("global", "eu", "us")}
    pen_us_floor = mm.penetration(mm.MARKETS["us"], cost_floor(cp), income=mm.REGION_INCOME["us"])[1]
    traj = simulate(R_today, base, TimingParams(), acceptance_grows=True, which="x")["share"] * 100
    from dataclasses import replace as _replace
    from market_share import _segment
    pbp = _replace(base, price_pb_mult=1.0, taste_quality_p=0.0)   # keeps the solved weights (no re-solve)

    N = {
        # at-parity baseline (neutral dials) — the most-quoted figure
        "PARITY_NEUTRAL": pc(at_parity(accept_x=1.0, theta_free_M=0.0)),
        # taste-acceptance ladder (a_x), at parity
        "AX_06": pc(at_parity(accept_x=0.6, theta_free_M=0.0)),
        "AX_08": pc(at_parity(accept_x=0.8, theta_free_M=0.0)),
        "AX_11": pc(at_parity(accept_x=1.1, theta_free_M=0.0)),
        # slaughter-free upside ladder (theta_free_M), at parity
        "TH_05": pc(at_parity(accept_x=1.0, theta_free_M=0.5)),
        "TH_10": pc(at_parity(accept_x=1.0, theta_free_M=1.0)),
        # long-run novelty ladder (neophobia_x), at parity
        "NX_NEG1": pc(at_parity(accept_x=1.0, theta_free_M=0.0, neophobia_x=-1.0)),
        "NX_POS1": pc(at_parity(accept_x=1.0, theta_free_M=0.0, neophobia_x=1.0)),
        # real-meat-credit ladder (b_x), at parity (re-instantiates, but b_x is stable in the solve)
        "BX_10": pc(share(1.0, DemandParams(real_tissue_x=1.00), accept_x=1.0, theta_free_M=0.0)),
        "BX_075": pc(share(1.0, DemandParams(real_tissue_x=0.75), accept_x=1.0, theta_free_M=0.0)),
        "BX_05": pc(share(1.0, DemandParams(real_tissue_x=0.50), accept_x=1.0, theta_free_M=0.0)),
        "BX_025": pc(share(1.0, DemandParams(real_tissue_x=0.25), accept_x=1.0, theta_free_M=0.0)),
        "BX_00": pc(share(1.0, DemandParams(real_tissue_x=0.00), accept_x=1.0, theta_free_M=0.0)),
        # nu_x0 framing band (static-share proxy at that novelty level), at parity
        "NX0_NEUTRAL": pc(at_parity(accept_x=1.0, theta_free_M=0.0, neophobia_x=0.0)),
        "NX0_WARM": pc(at_parity(accept_x=1.0, theta_free_M=0.0, neophobia_x=1.5)),
        # plant-based with b_p=1 (credited as real meat) at ITS current price — the equal-footing what-if
        "BP_1_PB": pc(share(1.0, DemandParams(real_tissue_p=1.0), cultivated_present=False, which="pb")),
        # closeness (kappa) ladder, re-solved, at TODAY's R (the above-parity lever)
        "KAPPA_3": pc(resolved(R_today, cult_sub_mult=3.0)),
        "KAPPA_4": pc(resolved(R_today, cult_sub_mult=4.0)),
        "KAPPA_5": pc(resolved(R_today, cult_sub_mult=5.0)),
        # loss-aversion (lambda) ladder, re-solved, at TODAY's R (shows lambda barely moves the level
        # across its principled 1 -> TK-2.25 range; the slider is capped at 2.25, see its tooltip)
        "LAMBDA_1": pc(resolved(R_today, loss_aversion=1.0)),
        "LAMBDA_225": pc(resolved(R_today, loss_aversion=2.25)),
        # --- the headline findings (front door + methods), at the default settings -----------
        "SHARE_TODAY": pc(share(R_today, base)),                      # long run, today's price, US
        "COLD_PARITY": pc(at_parity(neophobia_x=value("neophobia_x0"))),   # first contact, equal price
        "CONV_PARITY": pc(share(1.0, base, which="c")),               # conventional's share at parity
        "NOHEALTH_PARITY": pc(share(1.0, DemandParams(health_c=0.0))),  # parity without the health edge
        "NX0_MIN": pc(at_parity(neophobia_x=-3.5)),                   # the novelty slider's cold end
        "INCOME_CAP": pc(share(R_today, base, income=5_000_000)),     # a very rich buyer, today's price
        "CHINA_TODAY": pc(share(R_today, base, income=mm.REGION_INCOME["china"])),
        "NIGERIA_TODAY": f"{share(R_today, base, income=mm.REGION_INCOME['nigeria']) * 100:.1f}",
        "PEN_GLOBAL_VOL": f"{pen['global'][0] * 100:.1f}", "PEN_GLOBAL_VAL": f"{pen['global'][1] * 100:.1f}",
        "PEN_EU_VOL": f"{pen['eu'][0] * 100:.1f}", "PEN_EU_VAL": f"{pen['eu'][1] * 100:.1f}",
        "PEN_US_VOL": f"{pen['us'][0] * 100:.1f}",
        "PEN_US_FLOOR_VOL": pc(pen_us_floor),                         # US total if cost hit the floor
        "Y10_SHARE": pc(traj[10] / 100), "Y30_SHARE": pc(traj[-1] / 100),   # the timing path (US)
        # plant-based at full price+taste parity, mainstream, calibration held (self-check [5])
        "PB_PARITY": pc(_segment(1.0, pbp, pbp.beta_price, "M", accept_x=1.0, theta_free_M=0.0,
                                 tier_offset=0.0, neophobia_x=0.0, neophobia_p=0.0, income=pbp.income_ref,
                                 cultivated_present=False)["p"]),
    }
    return {f"{{{{{k}}}}}": v for k, v in N.items()}


def derived_numbers() -> dict:
    """Return {TOKEN: text} for every NON-share model number the prose quotes (price ratios, $/kg,
    years, coefficients). Same discipline as illustrative_numbers() (which holds the %-shares):
    computed from the live model at build time, so the text cannot drift from the model."""
    import numpy as np
    import uncertainty as U
    from market_share import DemandParams, share
    from cost_model import CostParams, biomass_cost, cost_floor, media_cost
    from adoption_timing import TimingParams, simulate, _time_to_stabilize

    cp, dp = CostParams(), DemandParams()
    p_conv, markup = value("p_conv"), value("markup_add")
    media = float(media_cost(cp, value("media_price"), value("efficiency")))
    bio = float(biomass_cost(cp, value("media_price"), value("efficiency")))
    R_today = (bio + markup) / p_conv
    floor = float(cost_floor(cp))
    stall = media + _pasitka_oh("ATF")                        # Pasitka's small-vessel design
    Rq = np.percentile(U.monte_carlo(20000, "commodity", {})["R"], [10, 50, 90])   # = RESULTS.md's draw

    def stab(**kw):                                           # year the path reaches 90% of its yr-30 value
        sim = simulate(R_today, dp, TimingParams(**kw), acceptance_grows=True, which="x")
        return int(_time_to_stabilize(sim["share"] * 100))

    lo, hi = -3.0, 3.0                                        # novelty at which the parity share is 60%
    for _ in range(60):                                       # (the warmest survey framing, Perdue 2024)
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if share(1.0, dp, neophobia_x=mid) < 0.60 else (lo, mid)

    N = {
        "R_TODAY": f"{R_today:.1f}",
        "MEDIA_TODAY": f"{media:.0f}",
        "BIOMASS_TODAY": f"{bio:.0f}",
        "RETAIL_TODAY": f"{bio + markup:.0f}",
        "CUT_RETAIL_TODAY": f"{bio + mm.SCAF + markup:.0f}",
        "PCONV": f"{p_conv:.0f}",
        "MARKUP": f"{markup:.0f}",
        "PARITY_BIOMASS": f"{p_conv - markup:.0f}",
        "COST_FLOOR": f"{floor:.1f}",
        "FEEDSTOCK_FLOOR": f"{AA_FLOOR + GLUCOSE_OTHER_FLOOR:.1f}",
        "PLANT_FLOOR": f"{value('plant_floor'):.0f}",
        "HUMBIRD_PLANT": f"{value('humbird_plant_cost'):.1f}",
        "R_FLOOR": f"{(floor + markup) / p_conv:.2f}",
        "R_STALL": f"{(stall + markup) / p_conv:.2f}",
        "R_MC_P10": f"{Rq[0]:.1f}", "R_MC_P50": f"{Rq[1]:.1f}", "R_MC_P90": f"{Rq[2]:.1f}",
        "STAB_YEAR": str(stab()), "STAB_R05": str(stab(accept_rate=0.5)),
        "NX0_60": f"{(lo + hi) / 2:.1f}",
        "HEALTH_TASTE_RATIO": f"{dp.w_health_M / dp.w_taste:.2f}",
        "HEALTH_E": f"{dp.w_health_E:.1f}",
        "MEDIA_PER_010": f"{value('media_intensity') * 0.10:.1f}",
        # the kappa-validation elasticity (golden-guarded as lusk_elas_parity_cold)
        "KAPPA4_LUSK_ELAS": f"{_lusk_at_parity(dp):.1f}",
    }
    return {f"{{{{{k}}}}}": v for k, v in N.items()}


PAGE_HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cultivated meat — how much of the market can it win?</title>
<style>
:root{--ink:#1a1a1a;--muted:#666;--rule:#e3e3e3;--accent:#0072B2;--orange:#E69F00;
 --green:#117733;--red:#CC3311;--bg:#fff;}
*{box-sizing:border-box;}
body{margin:0;background:var(--bg);color:var(--ink);
 font-family:-apple-system,Helvetica,Arial,sans-serif;line-height:1.5;}
.wrap{max-width:1120px;margin:0 auto;padding:24px 20px 64px;}
h1{font-size:1.45rem;margin:0 0 .2em;font-family:Georgia,serif;}
.lede{color:var(--muted);font-size:.92rem;margin:0 0 14px;overflow-wrap:break-word;max-width:760px;}
.lede a{color:var(--accent);}
.grid{display:grid;grid-template-columns:300px 1fr;gap:26px;}
@media(max-width:780px){.grid{grid-template-columns:1fr;}}
.rail{border:1px solid var(--rule);border-radius:10px;padding:14px 16px;
 position:sticky;top:14px;background:#fcfcfc;
 max-height:calc(100vh - 28px);overflow-y:auto;overscroll-behavior:contain;}
@media(max-width:780px){.rail{position:static;max-height:none;overflow-y:visible;}}
.ctl{margin:0 0 13px;}
.methods a[href^="#ref"]{font-size:.78em;font-weight:600;color:#0173B2;text-decoration:none;
 vertical-align:super;padding:0 1px;}
.methods a[href^="#ref"]:hover{text-decoration:underline;}
.refs li{scroll-margin-top:60px;}
.grphdr{font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.04em;
 color:#0173B2;margin:16px 0 9px;padding-bottom:3px;border-bottom:1px solid var(--rule);}
.grphdr:first-of-type{margin-top:6px;}
.ctl label{display:flex;justify-content:space-between;font-size:.82rem;margin-bottom:3px;}
.ctl .nm{font-weight:600;}
.ctl .val{font-variant-numeric:tabular-nums;color:var(--accent);font-weight:600;}
.ctl .src{color:#999;font-size:.7rem;font-weight:400;}
input[type=range]{width:100%;accent-color:var(--accent);margin:0;}
input[type=range]:disabled{accent-color:#c4c4c4;opacity:.55;cursor:not-allowed;}
.ctl .ovr{display:flex;align-items:center;gap:5px;font-size:.72rem;color:#777;margin-top:3px;}
.ctl .ovr input{margin:0;}
.ctl .wovr{font-size:.72rem;color:#8a5a00;background:#fff6e5;border:1px solid #f0d089;
 border-radius:5px;padding:5px 7px;margin-top:4px;line-height:1.35;}
select{width:100%;padding:5px;border:1px solid var(--rule);border-radius:6px;font-size:.85rem;}
.btn{margin-top:6px;width:100%;padding:7px;border:1px solid var(--rule);background:#fff;
 border-radius:6px;cursor:pointer;font-size:.82rem;}
.btn:hover{background:#f2f2f2;}
.heads{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:18px;}
@media(max-width:560px){.heads{grid-template-columns:repeat(2,1fr);}}
.head{border:1px solid var(--rule);border-radius:10px;padding:11px 13px;text-align:center;}
.head .big{font-size:1.7rem;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.1;}
.head .lab{font-size:.72rem;color:var(--muted);margin-top:3px;}
.charts{display:grid;grid-template-columns:1fr 1fr;gap:16px;}
@media(max-width:780px){.charts{grid-template-columns:1fr;}}
.card{border:1px solid var(--rule);border-radius:10px;padding:10px 12px;}
.card.full{grid-column:1/-1;}
.card h3{margin:0 0 4px;font-size:.92rem;font-family:Georgia,serif;}
.card .sub{font-size:.72rem;color:var(--muted);margin:0 0 6px;}
svg{width:100%;height:auto;display:block;}
.note{font-size:.74rem;color:#999;margin-top:14px;}
.selftest{font-size:.74rem;margin-top:10px;font-variant-numeric:tabular-nums;border:1px solid var(--rule);
  border-radius:6px;padding:8px 10px;background:#fbfcfd;}
.selftest .sthead{font-weight:700;color:var(--ink);font-size:.76rem;margin-bottom:5px;}
.selftest table{border-collapse:collapse;width:100%;}
.selftest td{padding:2px 6px 2px 0;vertical-align:top;border-top:1px solid #eef1f3;}
.selftest tr:first-child td{border-top:none;}
.selftest .stchk{color:var(--green);font-weight:700;width:14px;}
.selftest .stwhat{color:var(--ink);}
.selftest .stval{text-align:right;font-weight:700;color:var(--accent);white-space:nowrap;}
.selftest .stobs{color:var(--muted);white-space:nowrap;}
.selftest .stnote{color:var(--muted);font-size:.7rem;margin-top:5px;}
.selftest .stbad{color:var(--red);}
.selftest .stsecrow td{border-top:none;padding-top:8px;}
.selftest .stsec{font-weight:600;color:var(--ink);font-size:.71rem;}
.selftest .sttag{display:inline-block;font-size:.62rem;font-weight:700;line-height:1;padding:2px 5px;
  border-radius:9px;white-space:nowrap;}
.selftest .tag-match{background:#e3f2e8;color:var(--green);}
.selftest .tag-pin{background:#eef1f4;color:var(--muted);}
.selftest .tag-proj{background:#eaf2f8;color:var(--accent);}
.selftest .stbuild{color:var(--muted);font-size:.7rem;margin-top:7px;padding-top:6px;border-top:1px solid #eef1f3;}
.selftest .stanchor{color:var(--muted);font-size:.71rem;margin:0 0 6px;padding:5px 7px;background:#eef1f4;
  border-radius:5px;}
.toggle button{font-size:.7rem;border:1px solid var(--rule);background:#fff;padding:2px 7px;cursor:pointer;}
.toggle button.on{background:var(--accent);color:#fff;border-color:var(--accent);}
.toggle button:first-child{border-radius:6px 0 0 6px;}
.toggle button:last-child{border-radius:0 6px 6px 0;border-left:0;}
#foottip{position:fixed;display:none;pointer-events:none;z-index:9999;background:#1a1a1a;color:#fff;
  font-size:.72rem;line-height:1.4;padding:6px 9px;border-radius:5px;max-width:320px;white-space:pre-line;
  box-shadow:0 2px 10px rgba(0,0,0,.28);}
.q{display:inline-block;width:14px;height:14px;line-height:14px;text-align:center;border-radius:50%;
 background:#dcdcdc;color:#333;font-size:.64rem;cursor:help;margin-left:3px;font-weight:700;}
.tog{margin:10px 0 2px;font-size:.82rem;display:flex;align-items:center;gap:7px;}
.tog input{accent-color:var(--accent);}
.methods{margin-top:16px;border-top:1px solid var(--rule);padding-top:10px;}
.methods summary{cursor:pointer;font-weight:600;font-size:.92rem;color:var(--accent);font-family:Georgia,serif;}
.methods p{font-size:.86rem;}
.methods a{color:var(--accent);}
.methods .refs a{white-space:nowrap;}
.methods h4{font-family:Georgia,serif;font-size:.95rem;margin:18px 0 4px;}
.methods pre{background:#f7f7f5;border:1px solid var(--rule);border-radius:6px;padding:8px 11px;
 font-size:.78rem;overflow-x:auto;font-family:'SF Mono',Menlo,monospace;line-height:1.45;}
.methods .refs{font-size:.8rem;padding-left:18px;} .methods .refs li{margin-bottom:4px;}
.methods code{background:#f0f0ee;padding:0 3px;border-radius:3px;font-size:.82em;}
table.pt{border-collapse:collapse;font-size:.78rem;width:100%;}
table.pt th,table.pt td{border-bottom:1px solid var(--rule);padding:3px 6px;text-align:left;}
table.pt td.n{font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap;}
table.pt td.s{color:#777;}
.scrollx{overflow-x:auto;-webkit-overflow-scrolling:touch;}
/* keep every meat-type / parameter name on a single line; the table scrolls sideways if needed */
table.pt td:first-child,table.pt th:first-child{white-space:nowrap;min-width:160px;}
.mcbar{display:flex;align-items:center;gap:12px;margin:0 0 14px;}
.mcbtn{padding:6px 14px;border:1px solid var(--accent);background:#fff;color:var(--accent);
 border-radius:6px;cursor:pointer;font-size:.82rem;font-weight:600;}
.mcbtn.on{background:var(--accent);color:#fff;}
.mcbar .mcnote{font-size:.74rem;color:#999;}
.tip{position:fixed;max-width:290px;background:#222;color:#fff;padding:9px 11px;border-radius:7px;
 font-size:.78rem;line-height:1.45;z-index:999;display:none;box-shadow:0 4px 14px rgba(0,0,0,.25);
 font-family:-apple-system,Helvetica,Arial,sans-serif;}
text{font-family:Georgia,serif;}
.methods .vardef{font-size:.84rem;border-collapse:collapse;margin:6px 0;}
.methods .vardef td{padding:2px 10px 2px 0;vertical-align:top;}
.methods .vardef td:first-child{white-space:nowrap;color:#111;}
.methods .vardef tr.sub td:first-child{padding-left:18px;border-left:2px solid #d6d6d6;font-weight:normal;}
.methods .attr th{padding:2px 10px;text-align:center;font-size:.8rem;vertical-align:bottom;color:#333;}
.methods .attr td{text-align:center;padding:3px 10px;border-bottom:1px solid #f0f0f0;}
.methods .attr td:first-child,.methods .attr th:first-child{text-align:left;white-space:nowrap;}
.methods mjx-container{overflow-x:auto;overflow-y:hidden;}
/* the plain-language on-ramp at the top of the methods (newcomer-first big picture) */
.methods .intro{background:#f4f8fb;border:1px solid #cfe0ec;border-left:3px solid var(--accent);
 border-radius:8px;padding:12px 16px;margin:6px 0 14px;}
.methods .intro p{font-size:.9rem;margin:0 0 8px;} .methods .intro p:last-child{margin-bottom:0;}
.methods .intro ol{font-size:.9rem;margin:6px 0 8px;padding-left:22px;} .methods .intro li{margin-bottom:5px;}
/* "for the skeptical reader" asides — the referee-objection rebuttals, set apart from the main read
   so the narrative flows and the defences are there when wanted */
.methods .aside{background:#fafaf8;border:1px solid var(--rule);border-left:3px solid #bbb;
 border-radius:6px;padding:8px 12px;margin:8px 0;font-size:.82rem;color:#444;}
.methods .aside .ah{font-weight:700;color:#555;font-family:Georgia,serif;
 text-transform:none;letter-spacing:.02em;font-size:.8rem;display:block;margin-bottom:3px;}
/* --- reader-first layout: findings box, four-step strip, rail sections --- */
.stamp{font-size:.5em;font-weight:400;color:#bbb;display:inline-block;white-space:nowrap;}
.findings{border:1px solid #cfe0ec;border-left:4px solid var(--accent);background:#f6fafd;border-radius:10px;
 padding:10px 18px 8px;margin:4px 0 14px;max-width:760px;}
.findings .fh{font-family:Georgia,serif;font-weight:700;font-size:1.02rem;margin:0 0 6px;}
.findings ol{margin:0;padding-left:20px;} .findings li{font-size:.93rem;margin:0 0 4px;line-height:1.45;}
.findings .fnote{font-size:.78rem;color:var(--muted);margin:6px 0 0;}
/* the model in one line: a chain of four numbers */
.chain{display:flex;align-items:stretch;gap:6px;max-width:760px;margin:0 0 6px;}
.chain .link{flex:1;border:1px solid var(--rule);border-radius:10px;padding:8px 10px;background:#fff;text-align:center;}
.chain .num{font-size:1.25rem;font-weight:700;font-variant-numeric:tabular-nums;color:var(--accent);line-height:1.2;}
.chain .lab{font-size:.74rem;color:var(--muted);line-height:1.3;margin-top:2px;}
.chain .arr{align-self:center;color:#aaa;font-size:1.1rem;}
@media(max-width:620px){.chain{flex-direction:column;} .chain .arr{transform:rotate(90deg);}}
.howto{font-size:.84rem;color:#444;margin:0 0 16px;max-width:760px;}
.rail details.adv{margin-top:14px;border-top:1px solid var(--rule);padding-top:6px;}
.rail details.adv>summary{cursor:pointer;font-size:.8rem;font-weight:700;color:var(--accent);padding:4px 0;}
.head .sub2{font-size:.72rem;color:var(--muted);margin-top:1px;}
.selftest .tag-cal{background:#fbf1e3;color:#8a5a00;}
.methods h5{font-family:Georgia,serif;font-size:.9rem;margin:16px 0 4px;}
/* readable measure: ~70 characters per line in the methods prose */
.methods p,.methods ul,.methods .mintro{max-width:72ch;}
.methods p,.methods li{font-size:.9rem;line-height:1.55;}
.methods details.step{border-top:1px solid var(--rule);padding:7px 0;}
.methods details.step>summary{cursor:pointer;font-size:.9rem;line-height:1.5;max-width:80ch;}
.methods details.step>summary b{font-family:Georgia,serif;}
.methods details.step[open]>summary{margin-bottom:6px;}
.methods .mintro{color:#555;font-size:.86rem;}
.card h3 .q{vertical-align:2px;}
.methods ul{font-size:.86rem;padding-left:20px;} .methods li{margin-bottom:4px;}
.methods .example{background:#f7f9f4;border:1px solid #dfe8d5;border-radius:6px;padding:7px 11px;font-size:.86rem;}
.methods .attr{font-size:.82rem;border-collapse:collapse;margin:4px 0 8px;}
</style>
<script>window.MathJax={chtml:{scale:0.96}};</script>
<script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head><body><div id="tip" class="tip"></div><div class="wrap">
<h1>Cultivated meat: how much of the meat market can it win — and how fast? <span class="stamp">build __BUILD_STAMP__</span></h1>
<p class="lede">Cultivated meat is real animal meat grown from cells, without slaughter. This model estimates how
much of the meat market it could win, and how fast. Every assumption is a slider.</p>

<div class="findings">
  <div class="fh">At the default settings</div>
  <ol>
    <li><b>Price:</b> ~{{R_TODAY}}&times; everyday meat with today's technology; ~{{R_FLOOR}}&times; even at the cost
    floor.</li>
    <li><b>At equal price:</b> ~{{PARITY_NEUTRAL}}% of the market once familiar, if seen as real meat; ~{{BX_00}}% if
    not.</li>
    <li><b>At today's cost:</b> ~{{PEN_GLOBAL_VOL}}% of world meat by weight (Europe ~{{PEN_EU_VOL}}%); less by
    animal count, since most are chickens.</li>
    <li><b>Where:</b> beef and seafood; chicken and pork stay dearer even at the cost floor.</li>
    <li><b>When:</b> these are long-run ceilings, reached in about {{STAB_YEAR}} years.</li>
  </ol>
</div>

<div class="chain" role="group" aria-label="The model in one line">
  <div class="link"><div class="num">${{BIOMASS_TODAY}}/kg</div><div class="lab">to grow</div></div>
  <div class="arr">&rarr;</div>
  <div class="link"><div class="num">${{RETAIL_TODAY}}</div><div class="lab">in the shop, {{R_TODAY}}&times; everyday meat</div></div>
  <div class="arr">&rarr;</div>
  <div class="link"><div class="num">~{{SHARE_TODAY}}%</div><div class="lab">long-run share, US</div></div>
  <div class="arr">&rarr;</div>
  <div class="link"><div class="num">~{{STAB_YEAR}} years</div><div class="lab">to get there</div></div>
</div>
<p class="howto">The model in one line: everyday meat in the US, point estimates. It repeats this for every kind of
meat and region (charts 1, 2, 7). The left panel starts with the key assumptions; hover or tap
<span class="q">?</span> for help.</p>

<div class="grid">
  <div class="rail" id="rail"></div>
  <div>
    <div class="heads" id="heads"></div>
    <div class="mcbar">
      <button class="mcbtn" id="mcbtn">Monte Carlo: off</button>
      <span class="mcnote">Redraws the charts as uncertainty bands.</span>
    </div>
    <div class="charts">
      <div class="card full" id="mccard" style="display:none"><h3 data-help="2,000 draws of the uncertain inputs from their plausible ranges: medium price, cell efficiency, plant cost, markup, taste, the value of &ldquo;no slaughter&rdquo;, price sensitivity, long-run novelty, health image and premium resistance (plus plant-based's own taste, novelty and health image). Other sliders stay where you set them. The long right tail is the world where scale-up succeeds and shoppers embrace it.">Uncertainty band (Monte Carlo)</h3>
        <p class="sub" id="mcsub"></p><svg id="mc" viewBox="0 0 720 250"></svg></div>

      <div class="card full"><h3 data-help="Each bar is cultivated meat's share within one kind of meat (solid), with plant-based stacked on top (pale). The colour marks mince, cuts or premium; R is the price ratio. Dashed lines are the totals across all meat, by weight and by value. With Monte Carlo on, bars are medians and whiskers the 10&ndash;90% range.">1 · Share by type of meat</h3>
        <p class="sub" id="barsub"></p><svg id="bars" viewBox="0 0 720 300"></svg></div>
      <div class="card full"><h3 data-help="Each wedge is one kind of meat, sized by weight eaten (or by money spent, with the toggle). The solid inner part is cultivated's share; the lighter band is plant-based's.">2 · Share of all meat
        <span class="toggle" id="pietog" style="font-weight:400;margin-left:8px;vertical-align:middle"></span></h3>
        <p class="sub" id="piesub"></p>
        <svg id="pie" viewBox="0 0 720 330"></svg></div>

      <div class="card full"><h3 data-help="The three lines are Pasitka's reactor designs: ATF (many small vessels), TFF (mid-sized) and perfusion (large). Below the red line, cultivated meat matches the price of everyday meat; the green line is the cost floor.">3 · What it costs to grow (Step 1)</h3>
        <p class="sub">Cost of a kilo of cells against the medium price, one line per reactor design; the dot is your
        setting.</p>
        <svg id="cost" viewBox="0 0 720 300"></svg></div>
      <!-- 4a + 4b sit side by side and share ONE meat-type selector (in 4a). -->
      <div class="card"><h3 data-help="Blue dot: cultivated at its current price. Green dot: plant-based's current price (1.77&times;); read the blue curve at the same point to compare the two at equal prices. The selector below also drives 4b.">4a · Share vs price (Step 2)</h3>
        <p class="sub">How the four options' shares move with cultivated's price, for the meat chosen below.</p>
        <div style="margin:0 0 5px"><select id="curveSel" style="width:auto;max-width:100%;font-size:.78rem;padding:3px 5px"></select></div>
        <svg id="curve" viewBox="0 0 420 300"></svg></div>
      <div class="card"><h3 data-help="In score points (utils): green helps cultivated, orange hurts it. The bars add up to the net gap that sets the mainstream share; the &ldquo;blend&rdquo; in brackets mixes in the ethical shoppers. Move a slider and watch its bar change.">4b · Why this share</h3>
        <p class="sub" id="bdsub">Each factor's pull for or against cultivated, compared with conventional meat.</p>
        <svg id="breakdown" viewBox="0 0 420 300"></svg></div>
      <div class="card full"><h3 data-help="Cultivated rises as it reaches shelves and stops feeling new. Plant-based runs on the same machinery but stalls, because its taste and price gaps don't fade. One everyday product at the ${{PCONV}} benchmark price and the selected region's income, with costs held at today's level: not the path of the headline totals.">5 · Adoption over time (Step 4)</h3>
        <p class="sub" id="timingsub">Cultivated (blue) climbs from near zero toward its ceiling (dashed); plant-based
        (green) stalls.</p>
        <svg id="timing" viewBox="0 0 720 300"></svg></div>
      <div class="card full"><h3 data-help="For plant-based milk (the default) the model was not fitted to milk and predicts about 15%, close to its market share. That is a weak test, since milk's facts are set by hand; margarine and plant-based nuggets fit less well. Plant-based meat is what the model was fitted to, so it is not a test; eggs test a different lever (animal welfare), and their share is largely set by laws.">6 · Does the same model explain other products?</h3>
        <p class="sub" id="cmpsub">The same shopper model, with only the product's facts changed.</p>
        <div style="margin:0 0 5px"><select id="cmpSel" style="width:auto;max-width:100%;font-size:.78rem;padding:3px 5px"></select></div>
        <svg id="milk" viewBox="0 0 720 320"></svg></div>
      <div class="card full"><h3 data-help="Each product is compared with the price of its everyday grade, not the luxury price paid for wild-caught, top-grade or protected-origin products, which cultivated can't copy. Colour: green = already cheaper, blue = about equal, orange = only at the cost floor, grey = not even then. Bubble size = the conventional production it would displace if sold at cost. The &ldquo;cost waterline&rdquo; view draws cultivated's cost as a line. Hover over a bubble for details.">7 · Which products could it enter first?</h3>
        <p class="sub">Luxury products are already beatable on price but tiny; commodity meat, where the volume is,
        stays out of reach.</p>
        <div class="toggle" style="margin:0 0 6px;display:inline-block"><button id="footWL">cost waterline</button><button id="footMV" class="on">share vs price</button></div>
        <div style="margin:0 0 5px"><select id="footSel" style="width:auto;max-width:100%;font-size:.78rem;padding:3px 5px"></select></div>
        <svg id="foothold" viewBox="0 0 720 380"></svg>
        <div id="footcap" class="sub" style="margin-top:6px"></div></div>
    </div>
    <div class="selftest" id="selftest"></div>
    <details class="methods"><summary>How the model works: method, equations and sources</summary>

      <p class="mintro">Each step below has a one-line summary; click it for the detail. Equations are in appendix A0.
      Numbers with a bracketed reference, like 22.4&nbsp;L/kg&nbsp;[1], come from that source; judgement calls are
      labelled; everything else is computed by the model at its default settings.</p>

      <details class="step" id="step1"><summary><b>Step 1 · Cost &rarr; price.</b> Medium, plant running cost and
      retail markup, divided by the price of the meat it replaces: {{R_TODAY}}&times; today, about {{R_FLOOR}}&times;
      at the cost floor.</summary>
      <p>The <b>price ratio</b> <i>R</i> is cultivated meat's retail price divided by the price of the conventional
      meat beside it: 1 means the same price, 2 means twice the price. The retail price has three parts:</p>
      <ul>
        <li><b>Medium,</b> the nutrient liquid the cells grow in. Pasitka and colleagues measured 22.4 litres per kilo
        of cells at $0.63 per litre [1]. Companies reported $0.20/L or less in 2025, and an amino-acid cost analysis by
        GFI and MG Consulting supports that level [3], but there is no peer-reviewed measurement at scale. Leaner cells
        would use less (the cell-efficiency slider: 1 = today's cells).</li>
        <li><b>Plant running cost:</b> capital, labour, energy and consumables. It is set mainly by reactor scale and
        is the least demonstrated number in the model: $24.7/kg with many small vessels, $9.9 (the default), $7.9
        with large perfusion reactors [1]. Scaling up animal cells is hard because of oxygen and CO₂ transfer and
        sterility [2].</li>
        <li><b>Getting it to the shelf:</b> a ${{MARKUP}}/kg markup for processing, cold chain and retail (about
        conventional meat's farm-to-retail spread), plus $6/kg of scaffold for structured cuts, a guess because no
        study has costed it [6].</li>
      </ul>
      <p>&ldquo;Today's cost&rdquo; means Pasitka's projection for a large plant built with today's technology, not
      what pilot production costs now. The headline ratio uses a ${{PCONV}}/kg benchmark for everyday meat (range
      $10–14); charts 1, 2 and 7 use each meat's local price.</p>
      <p class="example"><b>Worked example.</b> Medium: 22.4 × $0.63 ≈ ${{MEDIA_TODAY}}/kg. Plus the plant's $9.9:
      ${{BIOMASS_TODAY}}/kg of cells. Plus the ${{MARKUP}} markup: ${{RETAIL_TODAY}}/kg in the shop
      (${{CUT_RETAIL_TODAY}} for a cut). Against ${{PCONV}} everyday meat: <i>R</i> ≈ {{R_TODAY}}.</p>
      <p><b>The floor.</b> Cells must eat a fixed amount of amino acids, glucose and salts (about ${{FEEDSTOCK_FLOOR}}/kg [2]), and even an
      ideal plant costs about ${{PLANT_FLOOR}}/kg to run (from Pasitka's breakdown [1]; Humbird's independent estimate is about
      ${{HUMBIRD_PLANT}}/kg [2]): a floor of about ${{COST_FLOOR}}/kg. Parity
      with ${{PCONV}} meat and a ${{MARKUP}} markup needs ${{PARITY_BIOMASS}}/kg, so even at the floor
      <i>R</i> ≈ {{R_FLOOR}}.</p>
      <p><b>Uncertainty.</b> Across the plausible ranges of the four cost inputs, the median is <i>R</i> ≈
      {{R_MC_P50}} (80% range {{R_MC_P10}}–{{R_MC_P90}}); almost no draws reach parity. The median is below
      {{R_TODAY}} because cell efficiency can only improve on today's cells.</p>
      <p><b>What moves it most:</b> the medium price and reactor scale (chart 3), then the markup. A 25% meat tax
      lowers <i>R</i> as much as a 20% cut in every cost.</p>
      </details>

      <details class="step" id="step2"><summary><b>Step 2 · Price &rarr; choice.</b> Shoppers choose among four options
      by price, taste, health, &ldquo;is it real meat?&rdquo; and &ldquo;no slaughter&rdquo;; at equal price, cultivated
      gets ~{{PARITY_NEUTRAL}}% if seen as real meat.</summary>
      <p>A standard discrete-choice model [12]. For each meal a shopper picks conventional meat, plant-based meat,
      cultivated meat, or beans and other whole foods, so shares include the bean meals. Each option gets a score
      that adds up its price, taste, health, whether it is real meat and whether an animal was killed. Tastes vary,
      so the top score doesn't always win: each option's share rises smoothly with its score (one point more means
      about 2.7 times as often).</p>
      <p><b>Two kinds of shopper:</b> 95% mainstream, who choose mainly on price, taste and real meat; 5% vegetarian
      or vegan [7], who care about slaughter and mostly eat beans.</p>
      <div class="scrollx"><table class="attr">
        <tr><th>option</th><th>price</th><th>taste</th><th>real meat</th><th>no slaughter</th><th>health</th></tr>
        <tr><td><b>conventional</b> meat</td><td>1</td><td>1</td><td>yes</td><td>no</td><td>&minus;0.1</td></tr>
        <tr><td><b>plant-based</b> meat</td><td>1.77&times; [14]</td><td>0.8 [7]</td><td>no</td><td>yes</td><td>0</td></tr>
        <tr><td><b>cultivated</b> meat</td><td><i>R</i> (Step 1)</td><td>1 (slider)</td><td>yes (slider)</td><td>yes</td><td>0</td></tr>
        <tr><td><b>beans</b> / whole food</td><td>~0.25&times; [15]</td><td>0.3</td><td>no</td><td>yes</td><td>+2</td></tr>
      </table></div>
      <p style="font-size:.84rem;color:#555">Conventional meat's small health penalty stands for antibiotics and
      contamination; beans are &ldquo;the healthy choice&rdquo;.</p>
      <p><b>The central premise.</b> Cultivated meat <i>is</i> animal tissue, so, unlike a veggie burger, it keeps
      conventional meat's main advantage with mainstream shoppers and draws its buyers from conventional meat. The
      premise is a slider: full credit gives ~{{BX_10}}% at equal price, none ~{{BX_00}}%.</p>
      <p><b>Tied to data.</b> Price sensitivity follows grocery data for meat (1% dearer, 0.9% fewer purchases [4]),
      made steeper for cultivated because an almost identical product sits beside it (A1). Three weights are solved
      so the model reproduces plant-based meat's ~1.2% share and ~89% mainstream buyers [14], plus an assumed ~6%
      of mainstream meals that skip meat (A4). Taste sets the scale for the rest. As a check, the same model with
      only the product's facts changed to plant-based milk's predicts about 15%, close to milk's share (chart 6); a
      weak test, since milk's facts are set by hand.</p>
      <p><b>At equal price</b>, once familiar, mainstream shoppers see two near-identical real meats and split that
      market: cultivated ~{{PARITY_NEUTRAL}}%, conventional ~{{CONV_PARITY}}% (cultivated's small edge is its
      slaughter-free and cleaner profile; without the health edge, ~{{NOHEALTH_PARITY}}%). The judgement calls that
      move it most:</p>
      <div class="scrollx"><table class="attr">
        <tr><th>if cultivated meat…</th><th>share at equal price</th></tr>
        <tr><td>tastes as good and is seen as real meat (default)</td><td>~{{PARITY_NEUTRAL}}%</td></tr>
        <tr><td>tastes a little worse (0.8)</td><td>~{{AX_08}}%</td></tr>
        <tr><td>tastes noticeably worse (0.6)</td><td>~{{AX_06}}%</td></tr>
        <tr><td>is judged tastier (1.1)</td><td>~{{AX_11}}%</td></tr>
        <tr><td>tastes as good, and &ldquo;no slaughter&rdquo; matters a little (0.5)</td><td>~{{TH_05}}%</td></tr>
        <tr><td>tastes as good, and &ldquo;no slaughter&rdquo; matters a lot (1.0)</td><td>~{{TH_10}}%</td></tr>
        <tr><td>tastes as good but isn't seen as real meat</td><td>~{{BX_00}}%</td></tr>
      </table></div>
      <p>At first contact the model gives ~{{COLD_PARITY}}% (Step 4). <b>At today's price</b> (<i>R</i> ≈
      {{R_TODAY}}) it gives ~{{SHARE_TODAY}}% in the long run (US, everyday meat): price is the binding constraint.</p>
      </details>

      <details class="step" id="step3"><summary><b>Step 3 · Every meat, every region.</b> Repeat at each meat's local
      price and add up: ~{{PEN_GLOBAL_VOL}}% of world meat by weight ({{PEN_GLOBAL_VAL}}% by value), ~{{PEN_EU_VOL}}% in
      Europe.</summary>
      <p>Cultivated meat costs about the same whatever animal it copies, but conventional prices vary: in the US,
      chicken mince is about $5/kg, a beef steak $20, sushi-grade fish $40. So the model runs each meat at its local
      price and adds up <b>by weight</b> (closest to the climate footprint) and <b>by value</b> (the market). Neither
      counts animals: most land animals raised for meat are chickens, where cultivated does worst.</p>
      <p><b>Mince, cuts and premium.</b> Premium means a cut at least 2.5 times the species' cheapest form (wagyu,
      sushi-grade fish). Up the ladder, <b>authenticity</b> matters more (nobody misses &ldquo;the real thing&rdquo; in a
      nugget; for wagyu the breed <i>is</i> the product: +0.2 for mince, &minus;0.4 for cuts, &minus;1.5 for premium) and
      buyers react less to <b>price</b> [5] (0.8× for cuts, 0.3× for premium). The directions are documented; the
      values are judgement, scaled by one <b>premium resistance</b> slider that the Monte Carlo samples (0.5–1.5).</p>
      <p><b>What comes out</b> (chart 1, at today's cost):</p>
      <ul>
        <li><b>Beef and seafood</b> are where cultivated can compete; chicken and pork stay dearer even at the
        floor.</li>
        <li><b>Premium products</b> get the biggest share of their category (cultivated is already cheaper there), but
        authenticity holds it to about a quarter, and the markets are small.</li>
        <li><b>Beef and seafood cuts</b> displace the most meat. At the cost floor, cuts and ground beef overtake
        premium, and the US total rises from {{PEN_US_VOL}}% to ~{{PEN_US_FLOOR_VOL}}% by weight.</li>
      </ul>
      <p><b>Regions.</b> Europe is easiest ({{PEN_EU_VOL}}% by weight, {{PEN_EU_VAL}}% by value): dear meat, rich
      shoppers. China and the world average are pulled down by cheap chicken and pork; low-income regions are
      hardest, with cheap meat and price-sensitive shoppers (A2). Prices and mixes for low-income regions are rough
      (A7).</p>
      </details>

      <details class="step" id="step4"><summary><b>Step 4 · Over time.</b> Starts near zero and rises as the product
      spreads and stops feeling new, levelling off after about {{STAB_YEAR}} years.</summary>
      <ul>
        <li><b>Rollout:</b> availability spreads like other new products, with early adopters, then word of mouth
        (Bass diffusion [11], standard rates from durable goods).</li>
        <li><b>Familiarity:</b> in a US choice experiment only ~5% chose lab-grown meat at the same price as beef [8].
        The model starts about there (~{{COLD_PARITY}}% at equal price) and lets the wariness fade with exposure.</li>
      </ul>
      <p class="example"><b>Worked example</b> (US, everyday meat, today's price and cost held fixed): near 0% at
      launch, ~{{Y10_SHARE}}% after 10 years, ~{{Y30_SHARE}}% after 30, against a long-run ceiling of
      ~{{SHARE_TODAY}}%; the curve flattens around year {{STAB_YEAR}}.</p>
      <p><b>For timing, the biggest unknown</b> is how wary people are today: surveys range from ~5% (a cold choice
      experiment) to ~60% (&ldquo;cultivated chicken in a restaurant&rdquo;) [10]. The &ldquo;novelty today&rdquo; slider
      spans that range (~{{NX0_MIN}}% at &minus;3.5, ~{{NX0_NEUTRAL}}% at 0, ~60% near +{{NX0_60}}, ~{{NX0_WARM}}% at
      +1.5). It changes how fast, not how far. Plant-based runs on the same machinery but stalls: its taste and price
      gaps don't fade.</p>
      </details>

      <details class="step" id="entry"><summary><b>Which products first (chart 7).</b> Luxury products are already
      beatable on price but tiny; commodity meat is out of reach, even at the cost floor.</summary>
      <p>A luxury price is mostly not cost: A5 wagyu or caviar is dear because of breed, origin and scarcity
      (<i>economic rent</i>). Cultivated meat can copy the meat, not the pedigree, so the model compares its cost with
      the product's <b>everyday grade</b> (farmed salmon, crossbred wagyu). A <b>prestige core</b> of buyers never
      switches: 25% by default, a proxy from the only two published splits (wild salmon, bellota ibérico).</p>
      <p>Already cheaper: foie gras, bluefin tuna, sea urchin, wagyu, lobster, but each market is thousands to
      hundreds of thousands of tonnes a year. Commodity beef, pork and chicken (tens of millions of tonnes each;
      chart 7 uses whole-category volumes) stay out of reach at world prices. New technologies often start at the top
      and move down-market as costs fall [18], [19]. Foie gras stands out: unstructured, expensive, and increasingly
      banned on welfare grounds that don't apply to a cultivated version.</p>
      <p>Chart 7 gives luxury products higher shares than chart 1 because it removes the prestige core and treats the
      rest like ordinary cuts, where chart 1 applies one large penalty to the whole category; chart 1 is the
      conservative view. Chart 7 assumes sale at cost, so it shows reach and impact, not profit.</p>
      </details>

      <details class="step" id="cruxes"><summary><b>What would change the conclusions.</b> Large reactors or cheap
      medium at scale (up), scale-up stalling (down), and how shoppers take to it.</summary>
      <ul>
        <li><b>Up:</b> a peer-reviewed demonstration of animal-cell reactors of 20,000 litres or more at high density
        and sterility; independently confirmed medium below $0.30/L at scale; a meat tax.</li>
        <li><b>Down:</b> if reactors can't be scaled up, production stays in small vessels and <i>R</i> stays around
        {{R_STALL}}, with the floor out of reach at any medium price.</li>
        <li><b>Demand:</b> acceptance as real meat, taste and the value of &ldquo;no slaughter&rdquo; span
        {{BX_00}}%–{{TH_10}}% at equal price. Nobody can measure these before launch, so they stay sliders.</li>
      </ul>
      </details>

      <details class="step" id="limits"><summary><b>What the model leaves out.</b> Supply and competition, a full spread
      of tastes, niche entry routes, and eggs and dairy.</summary>
      <ul>
        <li><b>Calibrated, not estimated:</b> no purchase data exist yet, so demand is a set of scenarios, not a
        forecast.</li>
        <li><b>Prices are given:</b> no supply response, competition or capacity limits.</li>
        <li><b>Two kinds of shopper</b> and one price sensitivity per product; convenience enters only through the
        rollout.</li>
        <li><b>Timing is rougher than the ceilings:</b> a durable-goods Bass curve plus a familiarity fade that may
        overlap, with costs held fixed.</li>
        <li><b>A fixed mix of meats</b> in each region; a meat tax scales all prices equally.</li>
        <li><b>Today's price ladder:</b> niche routes (pet food, new species, &ldquo;no animal harmed&rdquo; products)
        score as small.</li>
        <li><b>Meat only:</b> cultivated egg and dairy proteins use precision fermentation and need their own
        model.</li>
      </ul>
      </details>

      <details class="step" id="appendix"><summary><b>Technical appendix.</b> Equations, price sensitivity, income,
      calibration, the entry-point maths, data, questions a sceptic might ask, parameters and references.</summary>

      <h5>A0. The equations</h5>
      <p><b>Step 1, the price ratio.</b></p>
      \[ R \;=\; \frac{\overbrace{\iota\,\eta\,p_{\rm med}}^{\text{medium}} \;+\; \overbrace{h}^{\text{plant}}
         \;+\; \overbrace{k}^{\text{scaffold (cuts)}} \;+\; \overbrace{m}^{\text{markup}}}{p_c\,t} \tag{1} \]
      <p>\(\iota\): litres of medium per kilo; \(\eta\): cell efficiency (1 = today's cells); \(p_{\rm med}\): medium
      price; \(h\): plant running cost; \(k\): scaffold (cuts only); \(m\): markup; \(p_c\): conventional price;
      \(t\): meat-tax multiplier. The medium cost never falls below the feedstock dissolved in it, and the cost of
      cells never below the floor, about ${{COST_FLOOR}}/kg.</p>
      <p><b>Step 2, the score and the shares.</b></p>
      \[ V_j \;=\; \underbrace{\alpha\ln(y_{\rm eff}-p_j) \;-\; \lambda\,(d_j)^{+} + (d_j)^{-}}_{\text{price}}
         \;+\; \underbrace{w^{t}(a_j-1)}_{\text{taste}} \;+\; \underbrace{w^{rt}\,b_j}_{\text{real meat}}
         \;+\; \underbrace{w^{s}\,g_j}_{\text{no slaughter}} \;+\; \underbrace{w^{h}\,\zeta_j}_{\text{health}}
         \;+\; \underbrace{\nu_j+\tau_j}_{\text{novelty, authenticity}} \tag{2} \]
      \[ P_j = \frac{e^{V_j}}{\sum_k e^{V_k}}, \qquad
         \text{share}_j = w_{\rm eth}\,P^{\rm ethical}_j + (1-w_{\rm eth})\,P^{\rm mainstream}_j \tag{3} \]
      <p>Price enters twice: through the dollars it takes from income (\(p_j = R_j\,p_c\); \(y_{\rm eff}\) is an income
      measure, A2), and through the premium over conventional meat, \(d_j = R_j-1\), split into its positive part
      \((d_j)^{+}\) and negative part \((d_j)^{-}\) (at the default \(\lambda=1\) the two terms are simply \(-d_j\); A3).
      \(a_j\): taste (1 = as good as conventional); \(b_j\), \(g_j\): 1 if real meat, 1 if slaughter-free; \(\zeta_j\):
      health image. The weights \(w\) (A4) differ between the two kinds of shopper for no slaughter, real meat and
      health. \(\nu_j\) (novelty) and \(\tau_j\) (authenticity by tier, A5) are zero unless set.</p>
      <p><b>Step 3, adding up.</b></p>
      \[ \text{share}_{\rm vol} = \sum_i \frac{\omega_i}{\sum_k \omega_k}\,s_i, \qquad
         \text{share}_{\rm val} = \sum_i \frac{p_i\,\omega_i}{\sum_k p_k\,\omega_k}\,s_i \tag{4} \]
      <p>\(s_i\): cultivated's share of meat type \(i\); \(\omega_i\): that type's share of meat eaten (the listed
      weights sum to slightly more than 1 in some regions, hence the normalisation); \(p_i\): its local price.</p>
      <p><b>Step 4, over time.</b></p>
      \[ \text{share}(t) = F(t)\times \text{ceiling}\big(\nu(t)\big), \qquad
         \nu(t) = \nu_x + (\nu_{x0}-\nu_x)\,e^{-r\,E(t)} \tag{5} \]
      <p>\(F(t)\): the fraction of the market reached, a Bass curve with rates \(p_{\rm B}\) (early adopters) and
      \(q_{\rm B}\) (word of mouth). Novelty \(\nu\) fades from today's \(\nu_{x0}\) toward its long-run \(\nu_x\) as
      cumulative exposure \(E(t)\) grows, at speed \(r\); the ceiling is the Step 2 share at that novelty.</p>


      <h5>A1. Price sensitivity: where the price weight comes from</h5>
      <p>Grocery data give the <b>price elasticity</b> of meat as a category, \(\varepsilon \approx -0.9\) [4]:
      1% dearer, 0.9% fewer purchases. Meat as a whole has no close substitute, so it is fairly insensitive. A single
      cultivated product does have one, conventional meat on the same shelf, so its own sensitivity is \(\kappa\)
      times larger: \(\varepsilon_x = \kappa\varepsilon \approx 4 \times (-0.9) = -3.6\) at today's price. The price
      weight \(\beta\) (the slope of the price score) is solved so the model delivers exactly that at cultivated's
      own price \(p_x\) and share \(s_x\), which depend on each other and are solved together:</p>
      \[ \beta=\frac{\kappa\,\varepsilon}{p_x\,(1-s_x)}+\frac{\lambda}{p_c},\qquad
         \alpha=-\beta\,(y_{\rm ref}-p_x) \tag{A1} \]
      <p>The \(\lambda/p_c\) term hands back the part of the price response already carried by the reference-price
      term in Eq. (2), so \(\kappa\) sets the level of sensitivity and \(\lambda\) only its shape around parity.
      The price \(p_x\) is cultivated's own price at the default costs (${{RETAIL_TODAY}}/kg), computed by the cost
      model rather than typed in: change the default costs and it moves. Moving the cost sliders on the page changes
      cultivated's price, but not this calibration point.</p>
      <p><b>Evidence for \(\kappa\).</b> Van Loo, Caputo and Lusk [8] priced lab-grown meat at six levels. Their two
      models put its elasticity at equal price between &minus;0.84 and &minus;3.4. The model's implied value in the
      same setting (equal price, first-contact wariness) at \(\kappa=4\) is {{KAPPA4_LUSK_ELAS}}, inside that range.
      No experiment has priced cultivated meat at 2.4 times conventional, so the &minus;3.6 there is an assumption
      (\(\kappa\varepsilon\)), checked only against the data at parity. Once shoppers are familiar with the
      product, the model's elasticity is about −0.8 at parity, −1.7 at \(R=1.5\) and −3.6 at today's \(R\): share
      falls slowly just above parity, then faster. \(\kappa\) is the most consequential demand number above parity: at today's price,
      \(\kappa=3\) gives about {{KAPPA_3}}%, 4 about {{KAPPA_4}}% and 5 about {{KAPPA_5}}%. It plays the role that a
      nested logit's similarity parameter would play for a &ldquo;real meat&rdquo; nest.</p>

      <h5>A2. Income</h5>
      <p>The income part of the price score, \(\alpha\ln(y_{\rm eff}-p_j)\), is the Berry–Levinsohn–Pakes form [12]:
      the same premium is a bigger bite of a smaller income, so poorer shoppers are more sensitive to price. Taken
      literally, this makes poor shoppers about six times as price-sensitive as rich ones, which is too steep for
      food. So income is damped, \(y_{\rm eff}=y_{\rm ref}\,(y/y_{\rm ref})^{\phi}\), with \(\phi=0.5\) matching the
      roughly twofold gap in the data [15] (\(\phi=0\) removes income; US results don't depend on \(\phi\)). For
      the same product at the same price as today, that gives about {{SHARE_TODAY}}% in the US, {{CHINA_TODAY}}% in
      China and {{NIGERIA_TODAY}}% in Nigeria. Wealth relaxes price sensitivity but doesn't erase the other differences: even a very rich shopper
      buys cultivated only about {{INCOME_CAP}}% of the time at today's price.</p>

      <h5>A3. Loss aversion (symmetric by default)</h5>
      <p>People judge a price against the familiar price of the conventional product, and a premium can feel like a
      loss [13]. The term \(-\lambda(d_j)^{+}+(d_j)^{-}\) rewards a discount at rate 1 and penalises a premium at rate
      \(\lambda\). The default \(\lambda=1\) is symmetric; the slider goes up to Tversky and Kahneman's 2.25. It is
      left symmetric by default for three reasons: it barely moves the result once \(\beta\) is re-fitted (at today's
      price, {{LAMBDA_1}}% at \(\lambda=1\) vs {{LAMBDA_225}}% at 2.25); cultivated data can't identify it; and
      measured loss aversion largely reflects differences in price sensitivity between shoppers (Bell and Lattin,
      2000), which \(\kappa\) already carries.</p>

      <h5>A4. Calibration, and the attribute weights</h5>
      <p><b>Fixed from data:</b> plant-based meat's price premium (+77% [14]) and taste (0.8 [7]), and the ethical
      share (5% [7]). <b>Solved:</b> the mainstream real-meat weight and the two health weights, so that the model
      reproduces (i) the ~89% of plant-based buyers who are mainstream [14], (ii) ~6% of mainstream meals skipping meat
      by choice, and (iii) the ethical shoppers' small plant-based share. Together these give plant-based meat its
      observed ~1.2%. Moving the ethical share, \(\lambda\), \(\kappa\) or income re-solves them live, so plant-based
      stays anchored.</p>
      <p>Only differences between scores matter in this kind of model, so one weight has to set the scale. Taste does
      (\(w^t = 5\)), anchored to willingness-to-pay studies that rank taste first (taste about twice health and three
      times safety; Malone and Lusk 2017). Each weight slider shows its size relative to taste. The solved mainstream
      health weight comes out at {{HEALTH_TASTE_RATIO}}&times; taste, lighter than the ~0.5&times; in those studies.
      Beans' appeal is carried by their health score (+2) times a solved weight, rather than by a free constant;
      only the product of the two is pinned down by the data. Without it, plant-based meat would roughly triple, with
      mostly vegetarian buyers, contradicting the data.</p>
      <div class="scrollx"><table class="pt"><tr><th>weight</th><th>symbol</th><th>mainstream</th><th>ethical</th><th>how it is set</th></tr>
        __WEIGHTS_TABLE__
      </table></div>

      <h5>A5. Three different &ldquo;is it real?&rdquo; questions, and the tier ladder</h5>
      <ul>
        <li><b>Real meat</b> (\(b\)): is it animal tissue? Permanent, the same for every product, and the reason
        cultivated takes buyers from conventional meat.</li>
        <li><b>Novelty</b> (\(\nu\)): is it new, strange, safe? The same for a nugget and a steak, and it fades with
        familiarity (Step 4).</li>
        <li><b>Authenticity</b> (\(\tau\)): for this occasion, do I want the genuine article? Tier-specific and
        permanent: irrelevant for a nugget, decisive for wagyu.</li>
      </ul>
      <p>They are separate because they behave differently: a cultivated nugget faces novelty but no authenticity
      demand; a cultivated wagyu faces both. A fourth attribute, <b>health image</b> (\(\zeta\)), is separate again: it
      is 0 by default because surveys find both a &ldquo;clean meat&rdquo; draw and an &ldquo;ultra-processed&rdquo;
      aversion, and it is sampled between &minus;0.5 and +0.5.</p>
      <p>The tier ladder in formulas, with premium resistance \(\rho\) scaling both the authenticity offset and the
      elasticity multiplier \(\psi\):</p>
      \[ \tau_{\rm tier}=\rho\,\tau^0_{\rm tier},\qquad \varepsilon_{\rm tier}=\big(1+\rho\,(\psi^0_{\rm tier}-1)\big)\,\varepsilon,\qquad
         (\tau^0,\psi^0)=\begin{cases}(+0.2,\ 1.0)&\text{mince}\\ (-0.4,\ 0.8)&\text{cut}\\ (-1.5,\ 0.3)&\text{premium}\end{cases} \tag{A5} \]
      <p>&ldquo;Premium&rdquo; is defined per species (at least 2.5 times the species' cheapest form), so every species
      can have one and a product doesn't change tier between regions. Wagyu and sushi-grade fish are well attested;
      organic chicken and heritage pork are real but smaller, so they carry little volume.</p>

      <h5>A6. Entry points: the equations behind chart 7</h5>
      <p>A product's headline price splits into the accessible price and the rent, and cultivated's price ratio is
      taken against the accessible price only (Rosen's hedonic pricing [16]):</p>
      \[ p^{\rm auth} = p^{\rm base} + \underbrace{(p^{\rm auth}-p^{\rm base})}_{\text{rent}},\qquad
         R = \frac{c_x}{p^{\rm base}},\qquad c_x = c_{\rm bio} + k\,[\text{cut}] + m \tag{A6a} \]
      <p>A prestige core, a share \(\chi\) of the category's volume \(Q\), pays the rent and never switches. Luxury
      sellers keep their price and give up volume rather than discount, the classic Veblen pattern [17]. Only the
      rest is reachable, and cultivated wins a share \(s\) of it from the same shopper model as Step 2, using the mince
      or cut authenticity setting (the premium tier is the prestige core, already removed):</p>
      \[ Q^{\rm reach} = (1-\chi)\,Q,\qquad s = S\big(R;\ \tau_{\rm mince\ or\ cut}\big),\qquad
         D = s\cdot Q^{\rm reach}\quad(\text{kt/yr displaced}) \tag{A6b} \]
      <p>Zones: <i>about equal</i> if the accessible price is within $3 of cultivated's cost; <i>cheaper now</i> if
      above it; <i>only at the floor</i> if above the floor cost; otherwise <i>never on price</i>. A single-grade
      product (no rent, \(\chi=0\)) reproduces chart 1's share exactly, so the two views agree. Authenticity is counted
      once: as removed volume for the prestige grade, and through the mince or cut setting for the accessible grade.
      Limits: no margin or profit is modelled, the shopper model is calibrated on meat (so it is indicative for luxury
      and seafood), and each product is treated in isolation. The accessible and headline prices are sourced per
      product (June 2026 retail and wholesale; hover a bubble for the basis); shark fin's price is an estimate.</p>

      <h5>A7. Prices, the markup, and what people eat</h5>
      <p>Conventional retail prices by region and tier, the \(p_c\) in Eq. (1):</p>
      <div class="scrollx" id="pricetable"></div>
      <p style="font-size:.76rem;color:#888;">Prices: GlobalProductPrices (retail, January 2026), cross-checked
      against USDA ERS and BLS for the US. Volumes: USDA ERS per-capita availability (US); OECD-FAO Agricultural
      Outlook 2024 and FAO food balance sheets (Europe, China, world). The mix of meats differs by region: China is
      two-thirds pork, the US about half poultry, Europe pork-led and shifting to poultry. Prices and mixes for India,
      Brazil and Nigeria are rough.</p>
      <p><b>The markup is added per kilo, not as a percentage.</b> Much of it (processing, cold chain, retail
      handling) is genuinely per kilo, and conventional meat's farm-to-retail spread (USDA ERS, about $3–6/kg for
      ground beef) sets its size. But this is a modelling choice rather than a measurement, and a percentage markup
      would change the parity arithmetic. That is why the markup has its own slider.</p>

      <h5>A8. Questions a sceptic might ask</h5>
      <p><b>Isn't ~{{PARITY_NEUTRAL}}% at equal price just assumed?</b> It follows from the model's symmetry: two
      options that mainstream shoppers see as equivalent split that market. The sliders show how it moves if they
      are not equivalent (Step 2 table).</p>
      <p><b>Why not a nested logit?</b> The shared real-meat attribute and the two kinds of shopper already make
      cultivated take its share almost entirely from conventional meat, which is what a nest would do, with fewer
      unobservable parameters.</p>
      <p><b>Is there really no fitted constant?</b> Almost none. Beans' appeal is a labelled attribute (health) times a
      solved weight, rather than a free constant, but its position (+2) is assumed; only the product is identified
      (A4).</p>
      <p><b>Isn't premium resistance just novelty again?</b> No. Novelty is the same for every product and fades;
      authenticity depends on the tier, is permanent, and comes with lower price sensitivity (A5).</p>
      <p><b>The experiment behind the ~5% also had plant-based at 23% at equal price. Why doesn't the model?</b>
      The model is fitted to what plant-based meat actually sells (~1.2%), and predicts about {{PB_PARITY}}% for it
      among mainstream shoppers at equal price and taste. Hypothetical choice experiments tend to overstate adoption of new products; the model uses that
      experiment only for cultivated meat's starting wariness and price sensitivity.</p>
      <p><b>Why no habit term?</b> Habit can't be separated from preference without panel data (Heckman [13]); in
      this model it lives in the slow rollout and fading novelty of Step 4.</p>
      <p><b>Why is loss aversion symmetric by default?</b> See A3.</p>

      <h5>A9. Parameters and sources</h5>
      <p>Every slider, its symbol, default and range, where it enters the equations, and its source. The full
      datasheet, with every number and its uncertainty range, is <a href="https://github.com/PabloAMC/Cultivated_meat/blob/main/inputs.py">inputs.py</a>.</p>
      <div class="scrollx" id="paramtable"></div>

      <h5>References</h5>
      <ul class="refs">
        <li id="ref1"><b>[1]</b> <b>Medium cost and use, plant costs, reactor designs:</b> Pasitka, L. <i>et al.</i>
        Empirical economic analysis shows cost-effective continuous manufacturing of cultivated chicken
        using animal-free medium. <i>Nature Food</i> <b>5</b>, 693&ndash;702 (2024).
        <a href="https://doi.org/10.1038/s43016-024-01022-w" target="_blank" rel="noopener">doi:10.1038/s43016-024-01022-w</a></li>
        <li id="ref2"><b>[2]</b> <b>Feedstock floor, scale-up limits, clean-room cost:</b> Humbird, D. Scale-up economics
        for cultured meat. <i>Biotechnology and Bioengineering</i> <b>118</b>, 3239&ndash;3250 (2021).
        <a href="https://doi.org/10.1002/bit.27848" target="_blank" rel="noopener">doi:10.1002/bit.27848</a></li>
        <li id="ref3"><b>[3]</b> <b>Company medium costs of $0.20/L or less, amino-acid cost analysis:</b> The Good Food Institute,
        <a href="https://gfi.org/resource/cultivated-meat-seafood-and-ingredients-state-of-the-industry/" target="_blank" rel="noopener">2026 State of the Industry report: cultivated meat, seafood and ingredients</a>
        &amp; Specht, L., <a href="https://gfi.org/resource/analyzing-cell-culture-medium-costs/" target="_blank" rel="noopener">Analyzing cell-culture medium costs</a> (GFI, 2021).</li>
        <li id="ref4"><b>[4]</b> <b>Meat price elasticity &minus;0.9 (beef &minus;0.75, pork &minus;0.72, poultry &minus;0.68):</b>
        Andreyeva, T., Long, M.&nbsp;W. &amp; Brownell, K.&nbsp;D. The impact of food prices on
        consumption. <i>Am. J. Public Health</i> <b>100</b>, 216&ndash;222 (2010).
        <a href="https://doi.org/10.2105/AJPH.2008.151415" target="_blank" rel="noopener">doi:10.2105/AJPH.2008.151415</a></li>
        <li id="ref5"><b>[5]</b> <b>Pricier meat is less price-sensitive:</b> Lusk, J.&nbsp;L. &amp; Tonsor, G.&nbsp;T. How
        meat-demand elasticities vary with price, income and product category.
        <i>Appl. Econ. Perspect. Policy</i> <b>38</b>, 673 (2016).
        <a href="https://doi.org/10.1093/aepp/ppv050" target="_blank" rel="noopener">doi:10.1093/aepp/ppv050</a>.
        Species elasticities across regions: Gallet, C.&nbsp;A., meta-analyses (2010, 2012).</li>
        <li id="ref6"><b>[6]</b> <b>Scaffold cost ($6/kg) is our assumption:</b> no cost study covers scaffolding
        or structuring; Humbird 2021, CE Delft 2021 and Risner <i>et al.</i> 2021 all stop at unstructured cells.</li>
        <li id="ref7"><b>[7]</b> <b>Plant-based taste (only ~16% reach blind-taste parity):</b>
        <a href="https://www.nectar.org/sensory-research/2025-taste-of-the-industry" target="_blank" rel="noopener">NECTAR, Taste of the Industry (2025)</a>.
        <b>5% vegetarian or vegan:</b>
        <a href="https://news.gallup.com/poll/510038/identify-vegetarian-vegan.aspx" target="_blank" rel="noopener">Gallup (Brenan, 2023)</a>: 4% vegetarian, 1% vegan.</li>
        <li id="ref8"><b>[8]</b> <b>~5% choose lab-grown at equal price; its price elasticity:</b>
        Van&nbsp;Loo, E.&nbsp;J., Caputo, V. &amp; Lusk, J.&nbsp;L. Consumer preferences for farm-raised meat,
        lab-grown meat, and plant-based meat alternatives. <i>Food Policy</i> <b>95</b>, 101931 (2020),
        <a href="https://doi.org/10.1016/j.foodpol.2020.101931" target="_blank" rel="noopener">doi:10.1016/j.foodpol.2020.101931</a>.
        US choice experiment: at equal price, lab-grown ~5%, plant-based 16% and 7%, beef 72%; even at 50% discounts
        beef keeps the majority. Its price coefficient implies an elasticity between &minus;0.84 and &minus;3.4.</li>
        <li id="ref9"><b>[9]</b> <b>Plant-based price response:</b>
        Jahn, Guhl &amp; Erhard. Substitution patterns and price response for plant-based meat alternatives.
        <i>PNAS</i> <b>121</b>, e2319016121 (2024),
        <a href="https://doi.org/10.1073/pnas.2319016121" target="_blank" rel="noopener">doi:10.1073/pnas.2319016121</a>.
        Meat-analogue burger elasticity &minus;1.39 [&minus;2.31, &minus;0.48]; analogue shares stay below ~20&ndash;25%
        even at parity. A cross-check on the plant-based side, not used in the calibration.</li>
        <li id="ref10"><b>[10]</b> <b>5&ndash;60% depending on framing; ~27% familiar:</b> The Good Food
        Institute, <a href="https://gfi.org/wp-content/uploads/2025/01/Consumer-snapshot-cultivated-meat-in-the-US.pdf" target="_blank" rel="noopener">Consumer outlook on cultivated meat, US (2024)</a>
        (Morning Consult, n=2,214) &amp; <a href="https://gfi.org/industry/consumer-insights/" target="_blank" rel="noopener">Consumer insights</a>.
        Willingness to try ranges from 28% (plain free sample) to 60% (&ldquo;cultivated chicken in a
        restaurant&rdquo;, Perdue 2024); acceptance rises with familiarity.</li>
        <li id="ref11"><b>[11]</b> <b>Bass diffusion and its typical rates:</b> Bass, F.&nbsp;M. A new product growth
        model for consumer durables. <i>Management Science</i> <b>15</b>, 215 (1969),
        <a href="https://doi.org/10.1287/mnsc.15.5.215" target="_blank" rel="noopener">doi:10.1287/mnsc.15.5.215</a>;
        typical ranges from Sultan, Farley &amp; Lehmann, <i>J. Marketing Research</i> <b>27</b>, 70 (1990),
        <a href="https://doi.org/10.1177/002224379002700107" target="_blank" rel="noopener">doi:10.1177/002224379002700107</a>.</li>
        <li id="ref12"><b>[12]</b> <b>Discrete-choice demand:</b> McFadden, D.
        <a href="https://eml.berkeley.edu/reprints/mcfadden/zarembka.pdf" target="_blank" rel="noopener">Conditional logit analysis of qualitative choice behavior</a> (1974);
        Train, K. <a href="https://eml.berkeley.edu/books/choice2.html" target="_blank" rel="noopener"><i>Discrete Choice Methods with Simulation</i></a> (2009).
        <b>Income in the price term:</b> Berry, Levinsohn &amp; Pakes, <i>Econometrica</i> <b>63</b>, 841 (1995),
        <a href="https://doi.org/10.2307/2171802" target="_blank" rel="noopener">doi:10.2307/2171802</a>.</li>
        <li id="ref13"><b>[13]</b> <b>Loss aversion around a reference price:</b> Tversky &amp; Kahneman, <i>Q. J. Econ.</i> <b>106</b>,
        1039 (1991), <a href="https://doi.org/10.2307/2937956" target="_blank" rel="noopener">doi:10.2307/2937956</a>
        and <i>J. Risk Uncertain.</i> <b>5</b>, 297 (1992),
        <a href="https://doi.org/10.1007/BF00122574" target="_blank" rel="noopener">doi:10.1007/BF00122574</a>
        (the median of ~2.25); Hardie, Johnson &amp; Fader, <i>Marketing Science</i> <b>12</b>, 378 (1993),
        <a href="https://doi.org/10.1287/mksc.12.4.378" target="_blank" rel="noopener">doi:10.1287/mksc.12.4.378</a>.
        <b>Habit vs preference:</b> Heckman, J.,
        <a href="https://www.nber.org/system/files/chapters/c8909/c8909.pdf" target="_blank" rel="noopener">Heterogeneity and state dependence</a>, NBER (1981).</li>
        <li id="ref14"><b>[14]</b> <b>Plant-based share ~1.2%, ~89% mainstream buyers, +77% price premium:</b>
        <a href="https://gfi.org/marketresearch/" target="_blank" rel="noopener">GFI market research</a>
        (GFI/SPINS, GFI&ndash;Morning Consult, GFI/NIQ, 2024).
        <b>Displacement at parity:</b> Peacock, J.,
        <a href="https://forum.effectivealtruism.org/posts/iukeBPYNhKcddfFki/price-taste-and-convenience-competitive-plant-based-meat" target="_blank" rel="noopener">Price, taste &amp; convenience</a> (2023).</li>
        <li id="ref15"><b>[15]</b> <b>Income by region and its effect on food price sensitivity:</b>
        <a href="https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.CD" target="_blank" rel="noopener">World Bank (2023&ndash;24)</a>;
        Muhammad <i>et al.</i>,
        <a href="https://www.ers.usda.gov/publications/pub-details?pubid=47581" target="_blank" rel="noopener">International evidence on food consumption patterns</a>,
        USDA ERS TB-1929 (2011). <b>Bean prices:</b>
        <a href="https://fred.stlouisfed.org/series/APU0000714233" target="_blank" rel="noopener">BLS/FRED retail series</a> (2025).</li>
        <li id="ref16"><b>[16]</b> <b>A price as the sum of its attributes' prices (the rent split):</b>
        Rosen, S. Hedonic prices and implicit markets. <i>J. Polit. Econ.</i> <b>82</b>, 34&ndash;55 (1974).
        <a href="https://doi.org/10.1086/260169" target="_blank" rel="noopener">doi:10.1086/260169</a></li>
        <li id="ref17"><b>[17]</b> <b>Why luxury sellers hold their price:</b>
        Bagwell, L.&nbsp;S. &amp; Bernheim, B.&nbsp;D. Veblen effects in a theory of conspicuous consumption.
        <i>Am. Econ. Rev.</i> <b>86</b>, 349&ndash;373 (1996).</li>
        <li id="ref18"><b>[18]</b> <b>Learning curves: unit cost falls with cumulative output:</b>
        Wright, T.&nbsp;P. Factors affecting the cost of airplanes. <i>J. Aeronaut. Sci.</i> <b>3</b>, 122&ndash;128 (1936);
        Arrow, K.&nbsp;J. The economic implications of learning by doing. <i>Rev. Econ. Stud.</i> <b>29</b>, 155&ndash;173 (1962).
        <a href="https://doi.org/10.2307/2295952" target="_blank" rel="noopener">doi:10.2307/2295952</a></li>
        <li id="ref19"><b>[19]</b> <b>Moving down a quality ladder as costs fall:</b>
        Spence, A.&nbsp;M. The learning curve and competition. <i>Bell J. Econ.</i> <b>12</b>, 49&ndash;70 (1981).
        <a href="https://doi.org/10.2307/3003508" target="_blank" rel="noopener">doi:10.2307/3003508</a></li>
      </ul>
      </details>
      <p>Full results: <a href="https://github.com/PabloAMC/Cultivated_meat/blob/main/RESULTS.md">RESULTS.md</a>.
      Code and tests: <a href="https://github.com/PabloAMC/Cultivated_meat">github.com/PabloAMC/Cultivated_meat</a>.</p>
    </details>
  </div>
</div>
<div id="foottip"></div>
"""  # ---- end PAGE_HTML (CSS + markup + methodology) ----

# ===========================================================================
# JS_ENGINE — the live model + SVG charts + UI wiring. This is a hand-port of the
# Python model (market_share / cost_model / meat_market / adoption_timing); the
# parity test (tests/run_parity.py) asserts it matches to ~1e-16. Kept as its own
# string (separate from PAGE_HTML above) so the ~1000-line script is editable and
# diffable on its own. Concatenated back together in `main()`.
# ===========================================================================
JS_ENGINE = r"""<script>
const MODEL = __MODEL_JSON__;
const C = MODEL.const, SV = "http://www.w3.org/2000/svg";
const state = {region: "global"};
MODEL.sliders.forEach(s => { state[s.key] = s.default;
  if (s.solved) state[s.key + "_ovr"] = false; });   // SOLVED weights start on AUTO (not overridden)
MODEL.toggles.forEach(t => state[t.key] = false);
state.mc = false;
state.curveType = null;                          // shared species selector — drives panels 4a AND 4b
state.pieBasis = "vol";                          // the pie/donut basis: by volume or by value
state.footView = "margin";                       // panel 7 default view: "margin" = share vs price-ratio (vs "waterline")
state.income = C.REGION_INCOME[state.region];   // income follows the selected region
let KP = null;   // the current effective+calibrated constants (set every recompute)

/* ---------- model (mirror of market_share / meat_market / cost_model) ---------- */
function mediaCost(mp,ef){return Math.max(C.FEEDSTOCK_FLOOR,C.media_intensity*ef*mp);}

/* TWO-SEGMENT, FOUR-PRODUCT discrete-choice (logit) demand — a line-for-line mirror of
   market_share._utilities / _segment / share. Products [w,c,p,x] = whole-food (the non-meat
   outside option), conventional, plant-based, cultivated. EVERY product uses the SAME linear
   utility (no product-specific term): a BLP income price term, a reference-dependent loss-
   aversion premium penalty, taste, slaughter-free, real-tissue, and a per-product offset xi
   (0 for conventional & plant-based). Total share = w_eth*P_ethical + (1-w_eth)*P_mainstream.
   K = the effective constants (sliders override C) WITH the solved values from solveCalibration(). */
/* the shared price coefficient beta is DERIVED (mirror of market_share._derive_beta), stored as
   K.beta_ref by deriveBeta(). beta splits into an elasticity part and the loss-aversion
   compensation (lam); an eps override scales ONLY the elasticity part (so a tier's TOTAL
   elasticity scales as intended), leaving the loss-aversion compensation fixed. */
function betaPrice(K,eps,income,pRef){
  // per-tier eps override scales the WHOLE price response (both channels), not just the elastic part:
  // beta = beta_ref*(eps/eps_own). (Scaling only the elastic part pushed the inelastic premium beta
  // positive -> the cap flattened premium share to a constant ~18% across R; this is the fix.)
  let beta=K.beta_ref*(eps/K.eps_own);
  // MONOTONICITY GUARD (BLP-correct, income-aware; mirror of market_share.share). On the discount
  // side the BLP log slope is -alpha*pRef/(y_eff - price), alpha=-beta*(income_ref-anchor_price);
  // the binding case price->pRef (R->1) gives  beta <= (y_eff - pRef)/((income_ref-anchor_price)*pRef).
  // Tightens at low income; inert at the default, bites only in the low-income/premium/high-lambda corner.
  const inc=(income===undefined?K.income_ref:income);
  const pr=(pRef===undefined?K.p_conv_anchor:pRef);
  const yEff=K.income_ref*Math.pow(inc/K.income_ref,K.income_gradient);
  const denom=(K.income_ref-K.anchor_price)*pr;
  if(denom>0) beta=Math.min(beta,(yEff-pr)/denom-1e-6);
  return beta;}
function utilities(R,K,seg,o){
  const pRef=(o.pRef===undefined?K.p_conv_anchor:o.pRef);          // per-comparison reference price (the cut's rival)
  const pc=pRef;
  // plant-based price (R_p) and taste (a_p) are exploratory overrides; default to the
  // calibrated/observed position when not supplied (e.g. inside the calibration solve).
  const pPb=(o.pricePb===undefined?K.price_pb_mult:o.pricePb);
  const tP=(o.tasteP===undefined?K.taste_quality_p:o.tasteP);
  const priceRatio=[K.price_wf_mult,1,pPb,R];                       // w, c, p, x
  const taste=[K.taste_quality_w,0,tP,o.ax-1];                      // deviation from real meat (0 = parity)
  // real_tissue: whole-food 0, conventional 1 (ref); plant-based & cultivated are DIALS
  // (default p=0, x=1 — the identifying asymmetry, adjustable for equal-footing what-ifs).
  const rtP=(o.rtp!==undefined?o.rtp:(K.real_tissue_p!==undefined?K.real_tissue_p:0));
  const rtX=(o.rtx!==undefined?o.rtx:(K.real_tissue_x!==undefined?K.real_tissue_x:1));
  const slaughter=[1,0,1,1], realtissue=[0,1,rtP,rtX];
  // HEALTH PERCEPTION — a named ATTRIBUTE on every product, weighted by a SEGMENT-SPECIFIC health
  // weight (K.w_health_M / K.w_health_E; solved in the calibration), like slaughter-free and real-
  // tissue. Positions: whole-food health_w (+, "beans are the healthy choice"), conventional health_c
  // (slightly -, the reference's standing), plant-based / cultivated via their health_p / health_x
  // dials (two-sided scenario, default 0). The whole-food health premium is what pulls ethical eaters
  // to whole foods over a processed veggie burger — so w_health REPLACES the old free whole-food
  // intercept xi_w: the model is now fully attribute-based, no free fitted constant on any product.
  const hW=(K.health_w!==undefined?K.health_w:0);
  const hC=(K.health_c!==undefined?K.health_c:0);
  const hP=(o.hp!==undefined?o.hp:(K.health_p!==undefined?K.health_p:0));
  const hX=(o.hx!==undefined?o.hx:(K.health_x!==undefined?K.health_x:0));
  const health=[hW,hC,hP,hX];                                       // [w, c, p, x]
  // FOOD NEOPHOBIA (utils; - = neophobia penalty, + = neophilia bonus) on the two NOVEL products;
  // whole-food carries NO intercept now (health carries it), conventional 0.
  const xi=[0,0,(o.nbp||0),(o.nbx||0)+o.toff];                      // xi_j per product [w,c,p,x]
  const wSl=(seg==="M")?o.tfM:K.w_slaughter_E;
  const wRt=(seg==="M")?K.w_realtissue_M:K.w_realtissue_E;
  const wH=(seg==="M")?K.w_health_M:K.w_health_E;                   // segment-specific health weight (solved)
  const beta=betaPrice(K,o.eps,o.income,pRef);
  // INCOME — genuine damped Berry-Levinsohn-Pakes (mirror of market_share._utilities):
  //   Vp_j = alpha*ln(y_eff - price_j),  y_eff = income_ref*(income/income_ref)^phi,
  //   alpha = -beta*(income_ref - anchor_price)  (a single constant).
  // Income enters ONLY inside the log -> the diminishing-marginal-utility curvature IS the
  // mechanism (poorer = a given price is a bigger, more painful bite). phi DAMPS the effective
  // income so the BLP gradient matches the empirical ~2-3x food gradient (raw phi=1 is ~6x, too
  // steep). US anchor & at-parity numbers are invariant to phi (y_eff=income_ref at the US ref).
  const yEff=K.income_ref*Math.pow(o.income/K.income_ref,K.income_gradient);   // damped effective income
  const alpha=-beta*(K.income_ref-K.anchor_price);                 // BLP coefficient (a constant)
  const V=[], CO={price:[],taste:[],slaughter_free:[],real_meat:[],health:[],asc:[]};
  for(let j=0;j<4;j++){
    const price=priceRatio[j]*pc;                                  // pc = the per-comparison reference price (pRef)
    const resid=Math.max(yEff-price,1.0);                          // income left after buying j (log-domain guard)
    const Vp=alpha*Math.log(resid);                                // BLP: utility of residual income
    const prem=priceRatio[j]-1;                                    // premium over the conventional reference
    const Vl=(-K.loss_aversion*Math.max(0,prem)                    // loss side: penalise a premium at -lambda
              +1.0*Math.max(0,-prem));                            // gain side: reward a discount (ratio-based, no income scaling)
    // per-FACTOR components (mirror of market_share._utilities components) — summed to V[j]
    CO.price[j]=Vp+Vl; CO.taste[j]=K.w_taste*taste[j]; CO.slaughter_free[j]=wSl*slaughter[j];
    CO.real_meat[j]=wRt*realtissue[j]; CO.health[j]=wH*health[j]; CO.asc[j]=xi[j];
    V[j]=CO.price[j]+CO.taste[j]+CO.slaughter_free[j]+CO.real_meat[j]+CO.health[j]+CO.asc[j];
  }
  return o.components?CO:V;
}
/* relative-importance decomposition (mirror of market_share.utility_breakdown): split a product's
   utility RELATIVE TO CONVENTIONAL into each factor's contribution (utils), so the weights are
   legible. Contributions sum to V_which - V_c. seg = "M" (mainstream, the dominant segment). */
function breakdownCalc(R,K,seg,o){
  const which=o.which||"x", J={w:0,c:1,p:2,x:3}[which], c=1;
  const CO=utilities(R,K,seg,Object.assign({},o,{components:true}));
  const out={
    price:          CO.price[J]-CO.price[c],
    taste:          CO.taste[J]-CO.taste[c],
    real_meat:      CO.real_meat[J]-CO.real_meat[c],
    health:         CO.health[J]-CO.health[c],
    slaughter_free: CO.slaughter_free[J]-CO.slaughter_free[c],
    novelty:        which==="x"?(o.nbx||0):(which==="p"?(o.nbp||0):0),
    authenticity:   which==="x"?(o.toff||0):0,
  };
  let net=0; for(const k in out) net+=out[k];
  out._net=net;
  out._share=segShares(R,K,seg,Object.assign({},o,{present:true}))[which];
  return out;
}
function softmax(V){const m=Math.max.apply(null,V),e=V.map(v=>Math.exp(v-m)),s=e.reduce((a,b)=>a+b,0);return e.map(x=>x/s);}
function segShares(R,K,seg,o){
  const V=utilities(R,K,seg,o);
  if(o.present){const P=softmax(V);return {w:P[0],c:P[1],p:P[2],x:P[3]};}
  const P=softmax(V.slice(0,3));return {w:P[0],c:P[1],p:P[2],x:0};
}
function shareCalc(R,K,{ax=1,tfM=0,toff=0,eps,income,pricePb,aP,nbx=0,nbp=0,present=true,which="x",rtx,rtp,hx,hp,pRef}){
  const o={ax,tfM,toff,present,nbx,nbp,eps:(eps===undefined?K.eps_own:eps),
           income:(income===undefined?K.income_ref:income),
           pricePb:pricePb, tasteP:(aP===undefined?undefined:aP-1), rtx:rtx, rtp:rtp, hx:hx, hp:hp, pRef:pRef};
  const M=segShares(R,K,"M",o), E=segShares(R,K,"E",o), key=(which==="pb")?"p":which;
  return K.w_eth*E[key]+(1-K.w_eth)*M[key];
}
/* re-solve the calibration (mirror of market_share.solve_calibration): three monotone
   bisections so the live sliders (w_eth, λ, κ, ε, prices…) keep plant-based at its observed
   ~1.2% share AND the 89% mainstream buyer split. */
// The calibration MUST run at the canonical real-tissue baseline (plant-based not credited as real
// tissue: rtp=0; cultivated fully credited: rtx=1). The real_tissue_p / real_tissue_x sliders are
// EXPLORATORY OVERRIDES that shift the OUTCOME (applied at display time via o.rtp / o.rtx), they must
// NOT re-pin the calibration — otherwise raising bp forces w_realtissue_M to a bisection bound and the
// plant-based share jumps non-monotonically. Forcing rtp:0,rtx:1 here keeps the solve stable in both
// dials (mirrors deriveBeta, which already forces rtx:1 for the same reason).
function _rate(K,seg,which){return segShares(1,K,seg,{ax:1,tfM:0,toff:0,eps:K.eps_own,income:K.income_ref,present:false,rtp:0,rtx:1,hp:0,hx:0})[which];}
/* re-solve the calibration (mirror of market_share.solve_calibration): solve the SEGMENT-SPECIFIC
   HEALTH WEIGHTS (w_health_M, w_health_E) — times the whole-food health premium, these REPLACE the
   old free whole-food intercept xi_w, so the model carries no free fitted constant. WF_M increases
   in w_health_M and ethical PB decreases in w_health_E (health_w > 0), so the bisections run on
   [0, 16]. */
function solveCalibration(K){
  const we=K.w_eth;
  const pbM=K.pb_mainstream_frac*K.pb_share_target/(1-we);
  const pbE=(1-K.pb_mainstream_frac)*K.pb_share_target/we, wfM=K.wf_mainstream_target;
  const pin=K._pin||[], pinned=k=>pin.indexOf(k)>=0;     // SOLVED weights the user pinned (skip solving)
  if(!pinned("w_realtissue_M"))K.w_realtissue_M=2;       // seed only the weights we will solve
  if(!pinned("w_health_M"))K.w_health_M=1;
  if(!pinned("w_health_E"))K.w_health_E=1;
  for(let r=0;r<12;r++){
    if(!pinned("w_realtissue_M")){
      let lo=0,hi=8;
      for(let i=0;i<60;i++){const m=0.5*(lo+hi);K.w_realtissue_M=m;if(_rate(K,"M","p")>pbM)lo=m;else hi=m;}
      K.w_realtissue_M=0.5*(lo+hi);
    }
    if(!pinned("w_health_M")){
      let lo=0,hi=16;                                                // WF_M increases in w_health_M
      for(let i=0;i<60;i++){const m=0.5*(lo+hi);K.w_health_M=m;if(_rate(K,"M","w")>wfM)hi=m;else lo=m;}
      K.w_health_M=0.5*(lo+hi);
    }
    if(pinned("w_realtissue_M")&&pinned("w_health_M"))break;         // nothing left to coordinate-descend
  }
  if(!pinned("w_health_E")){
    let lo=0,hi=16;                                                  // ethical PB decreases in w_health_E
    for(let i=0;i<60;i++){const m=0.5*(lo+hi);K.w_health_E=m;if(_rate(K,"E","p")>pbE)lo=m;else hi=m;}
    K.w_health_E=0.5*(lo+hi);
  }
  return K;
}
/* DERIVE the price coefficient beta with NO free anchor (mirror of market_share._derive_beta):
   the target is cultivated's own-price elasticity eps_x = eps*kappa. Price enters utility through
   TWO channels — the BLP income term (slope beta) and the loss-aversion term (slope -lam on the
   loss side, lam = loss_aversion/p_conv) — so beta is solved so their SUM reproduces eps_x AT
   cultivated's own retail price (= biomass at BASE cost + markup, which tracks the cost model)
   and its own modeled share. A short fixed point co-solved with the calibration; nothing here is
   a hand-set number. (Absorbing lam into beta is the double-counting fix: loss_aversion then only
   shapes the kink at parity, not the elasticity level.) */
function deriveBeta(K){
  const pAnchor=mediaCost(C.anchor_media_price,1)+C.anchor_overhead+C.anchor_markup;
  K.anchor_price=pAnchor;
  const Rtoday=pAnchor/K.p_conv_anchor, epsX=K.eps_own*K.cult_sub_mult;
  const lam=K.loss_aversion/K.p_conv_anchor;   // loss-side semi-elasticity the loss-aversion term adds
  // MONOTONICITY GUARD (mirror of market_share._derive_beta): cap beta below 1/p_conv so the
  // DISCOUNT side (where the loss term is off) always slopes downward — a cheaper product must
  // never lose share. Inert at the default; only bites in the high-loss_aversion tail.
  // WHY λ is capped at the TK 2.25 anchor (see the loss_aversion slider): once this cap binds
  // (λ≈2.6 at default p_conv) β can no longer fully absorb the loss-aversion slope, so the realised
  // elasticity would drift off the eps_own*κ target. Stopping at 2.25 keeps the "λ reshapes the kink,
  // not the level" property true across the whole admissible range.
  const betaCap=1.0/K.p_conv_anchor-1e-3;
  let s=0;
  for(let it=0;it<40;it++){
    K.beta_ref=Math.min(betaCap, epsX/(pAnchor*(1-s))+lam);  // set before solveCalibration uses betaPrice
    solveCalibration(K);
    // beta is calibrated to cultivated AS A REAL-MEAT product (rtx=1), so the fixed-point share
    // uses rtx=1 regardless of the user's real_tissue_x dial (matches Python _derive_beta, which
    // is stable in rtx). The dial then shifts the OUTCOME, not the price-coefficient calibration.
    const sNew=shareCalc(Rtoday,K,{ax:1,tfM:0,rtx:1});
    if(Math.abs(sNew-s)<1e-9){s=sNew;break;}
    s=sNew;
  }
  K.beta_ref=Math.min(betaCap, epsX/(pAnchor*(1-s))+lam);
  return solveCalibration(K);                  // final calibration at the converged beta
}
/* effective constants from the current sliders, then derive beta + run the calibration solve. */
function effConsts(s){
  const K=Object.assign({},C);
  ["cult_sub_mult","loss_aversion","w_eth","eps_own","real_tissue_x","real_tissue_p","health_x","health_p","income_gradient",
   "w_taste","w_slaughter_E","w_realtissue_E"].forEach(k=>{if(k in s)K[k]=s[k];});
  // EXPERT WEIGHT OVERRIDES (mirror of market_share.DemandParams.pinned_weights): the three
  // attribute weights that are normally SOLVED to data moments (w_realtissue_M -> GFI 89% buyer
  // split; w_health_M -> mainstream meatless rate; w_health_E -> ethical PB rate) can be PINNED to a
  // user value. When pinned, solveCalibration leaves them fixed (deliberately breaking that moment);
  // the un-pinned ones still re-solve. w_taste / w_slaughter_E above are NOT solved, so changing them
  // simply re-pins the solved weights around the new value (no moment is broken).
  const pin=[];
  ["w_realtissue_M","w_health_M","w_health_E"].forEach(k=>{ if(s[k+"_ovr"]){K[k]=s[k]; pin.push(k);} });
  K._pin=pin;
  return deriveBeta(K);
}
function biomass(s){return mediaCost(s.media_price,s.efficiency)
  +s.overhead+(s.cleanroom?C.cleanroom_cost:0);}
function basicR(s){return (biomass(s)+s.markup_add)/(C.p_conv_anchor*s.meat_tax);}
function speciesBases(market){const b={};market.forEach(mt=>{const a=animalOf(mt.name);
  b[a]=Math.min((a in b)?b[a]:Infinity,mt.p_conv);});return b;}
function tierOf(mt,base){return !mt.structured?"basic":(mt.p_conv>=C.PREMIUM_RATIO*base?"premium":"cut");}
// per-type price ratio + tier, shared by penetration / monteCarlo / perTypeMC so the
// R = (biomass*cost_mult + scaffold + markup) / (p_conv*meat_tax) formula lives in ONE place
// (mirror of meat_market._rollup's per-type R). `b` biomass $/kg, `mk` retail markup $/kg.
function typeR(mt,b,mk,s,bases){
  const scaf=mt.structured?s.scaffold:0, price=mt.p_conv*s.meat_tax;
  return {R:(b*mt.cost_mult+scaf+mk)/price, t:tierOf(mt,bases[animalOf(mt.name)])};
}
// per-tier authenticity offset and elasticity multiplier, scaled by the premium-resistance
// dial r (r=1 central; r=0 no tier effect; mirrors meat_market.tier_authenticity/tier_eps_mult).
// per-tier authenticity offset = premium-resistance r × the per-tier τ (basic/cut/premium). The τ
// values are user-settable (the authenticity sliders auth_basic/auth_cut/auth_premium); they fall
// back to the datasheet ladder C.AUTH_* when unset. Mirror of meat_market.tier_authenticity(...,auth).
function _auth(key,dflt){return (typeof state!=="undefined" && (key in state))?state[key]:dflt;}
function tAuth(t,r){r=(r===undefined?1:r);
  const A=t==="basic"?_auth("auth_basic",C.AUTH_BASIC):t==="cut"?_auth("auth_cut",C.AUTH_CUT):_auth("auth_premium",C.AUTH_PREMIUM);
  return r*A;}
function tMult(t,r){r=(r===undefined?1:r);const m=(t==="basic"?1.0:t==="cut"?C.EPS_MULT_CUT:C.EPS_MULT_PREMIUM);return 1.0+r*(m-1.0);}
function penetration(s){
  const K=KP||effConsts(s);                                         // current calibrated constants
  const market=MODEL.markets[s.region], b=biomass(s), bases=speciesBases(market);
  const r=(s.premium_resistance===undefined?1:s.premium_resistance);
  let Wval=0, Wvol=0; market.forEach(mt=>{Wval+=mt.p_conv*mt.w_vol; Wvol+=mt.w_vol;});   // Wvol: listed weights sum to 1.00-1.025
  const rows=market.map(mt=>{
    const {R,t}=typeR(mt,b,s.markup_add,s,bases);
    const eps=s.eps_own*tMult(t,r);                                 // premium tiers less price-sensitive
    const o={ax:s.accept_x,tfM:s.theta_free_M,toff:tAuth(t,r),eps,income:s.income,pricePb:s.R_p,aP:s.a_p,nbx:s.neophobia_x,nbp:s.neophobia_p,pRef:mt.p_conv};
    const sh=shareCalc(R,K,o);                                      // cultivated share of this type
    const shp=shareCalc(R,K,Object.assign({},o,{which:"p"}));       // plant-based share of this type
    return {mt,R,sh,shp,t};
  });
  let tv=0,tval=0,tvp=0,tvalp=0;                                     // cultivated AND plant-based roll-ups
  rows.forEach(r=>{tv+=r.mt.w_vol/Wvol*r.sh; tval+=(r.mt.p_conv*r.mt.w_vol/Wval)*r.sh;
                   tvp+=r.mt.w_vol/Wvol*r.shp; tvalp+=(r.mt.p_conv*r.mt.w_vol/Wval)*r.shp;});
  return {rows,tv,tval,tvp,tvalp};
}
/* ---- TIMING RUNG: Bass rollout x food-neophobia fading (mirror of adoption_timing._run) ----
   At a held price ratio R, realized share(t) = F(t) * ceiling(t), where F is Bass diffusion and
   the ceiling rises as the cold-start neophobia nb0 fades toward the long-run nbL with exposure E.
   Product-agnostic (equal footing): o.which="x" cultivated (default) or "pb" plant-based.
   o = {R, nb0, nbL, rate, p, q, ax, tfM, aP, income, which} ; returns per-year arrays.
   For the PB curve, o.aP carries the plant-based taste slider (a_p) so dragging it moves
   the green ceiling — same exploratory override as the static penetration bars. */
function bassTrajectory(o){
  const yrs=MODEL.years||30, K=KP, which=o.which||"x";
  let F=0.0, E=0.0; const share=[], ceiling=[], nb=[];
  for(let k=0;k<=yrs;k++){
    const nbk=o.nbL + (o.nb0-o.nbL)*Math.exp(-o.rate*E);             // cold-start fades onto long-run
    const ceil=(which==="pb")
      ? shareCalc(o.R,K,{toff:0,income:o.income,nbp:nbk,pricePb:o.R,aP:o.aP,hp:o.hp,present:false,which:"pb"})
      : shareCalc(o.R,K,{ax:o.ax,tfM:o.tfM,toff:0,income:o.income,nbx:nbk,hx:o.hx});
    share.push(F*ceil); ceiling.push(ceil); nb.push(nbk);
    if(k<yrs){ const dF=(o.p+o.q*F)*(1.0-F); F=Math.min(1.0,F+dF); E+=F; }
  }
  return {share,ceiling,nb};
}
// first year realized share reaches `frac` of its final (yr-N) value
function timeToStabilize(series,frac){frac=frac||0.9; const fin=series[series.length-1];
  if(fin<=1e-9) return series.length-1;
  for(let k=0;k<series.length;k++) if(series[k]>=frac*fin) return k; return series.length-1;}
/* trajectory Monte-Carlo: sweep ALL timing+acceptance priors -> band on share(t) + tstab dist.
   R held fixed. Mirrors adoption_timing.monte_carlo_trajectory. */
function trajectoryMC(s,N,which){
  // product-aware: which="x" (cultivated, default) or "pb" (plant-based). Each sweeps ITS OWN
  // priors over the shared Bass/rate diffusion priors, so BOTH novel meats get a band on EQUAL
  // FOOTING. Cultivated samples C.mc_timing_inputs (the Python timing band's list); plant-based
  // sweeps a_p, ν_p, ν_p0, health_p (its price R_p is held at the slider, like the cultivated R is held).
  which=which||"x";
  const yrs=MODEL.years||30, P=C.priors, pb=(which==="pb");
  _seedRng(pb?2:1);                 // reproducible band, distinct stream per product
  const all=[]; const tstab=[], finals=[];
  for(let d=0;d<N;d++){
    const o=pb
      ? {R:s.R_p, aP:triang.apply(null,P.a_p),
         nbL:triang.apply(null,P.neophobia_p), nb0:triang.apply(null,P.neophobia_p0),
         rate:triang.apply(null,P.accept_rate), p:triang.apply(null,P.p_innov), q:triang.apply(null,P.q_imit),
         hp:triang.apply(null,P.health_p), income:s.income, which:"pb"}
      : (dr=>({R:s._Rtiming, ax:dr.accept_x, tfM:dr.theta_free_M, nbL:dr.neophobia_x, nb0:dr.neophobia_x0,
               rate:dr.accept_rate, p:dr.p_innov, q:dr.q_imit, hx:dr.health_x, income:s.income,
               which:"x"}))(mcDraw(C.mc_timing_inputs));   // C.mc_timing_inputs = inputs.MC_TIMING_INPUTS
    const tr=bassTrajectory(o); const sh=tr.share.map(x=>x*100);
    all.push(sh); tstab.push(timeToStabilize(sh)); finals.push(sh[sh.length-1]);
  }
  // percentile band per year
  const p10=[],p50=[],p90=[];
  for(let k=0;k<=yrs;k++){const col=all.map(a=>a[k]).sort((x,y)=>x-y);
    p10.push(pctl(col,10)); p50.push(pctl(col,50)); p90.push(pctl(col,90));}
  return {p10,p50,p90,tstab:tstab.sort((a,b)=>a-b),finals:finals.sort((a,b)=>a-b)};
}
function animalOf(n){
  // SPECIES label — also the per-species 'premium' base (mirror of meat_market.animal_of); duck
  // gets its own base so duck cuts are judged vs duck, not chicken. Coarser poultry/fish FAMILY
  // grouping is familyOf() (display only).
  const map=[["chicken","Chicken"],["beef","Beef"],["pork","Pork"],["turkey","Turkey"],
    ["duck","Duck"],["seafood","Seafood"],["sheep","Sheep/goat"],["goat","Sheep/goat"],["rabbit","Rabbit"]];
  for(const[k,l]of map) if(n.startsWith(k)) return l;
  return n.split(" ")[0];
}
// FAMILY (display grouping only; mirror of meat_market.family_of): poultry + fish are grouped
// (member species share biology/price/framing); others stand alone.
function familyOf(n){const a=animalOf(n);
  if(a==="Chicken"||a==="Turkey"||a==="Duck") return "Poultry";
  if(a==="Seafood") return "Seafood / fish";
  return a.replace("\n"," ");}
// fixed colour per species, kept CONSTANT across regions (so a wedge is the same
// colour whichever region you select)
const COLSP={Chicken:"#4C78A8", Beef:"#E45756", Pork:"#F58518", Turkey:"#72B7B2",
  Duck:"#3E6B5A", Seafood:"#54A24B", "Sheep/goat":"#B279A2", Rabbit:"#A8836B", Buffalo:"#7F7F7F", Goat:"#B279A2"};
/* Tiny inline-SVG species ICONS (compact, recognisable face/silhouette glyphs centred at
   (cx,cy)). All face-forward heads where possible, each with EYES. No external files. */
function _eyes(g,cx,cy,dx,ey,er){   // a symmetric pair of eyes (white sclera + dark pupil)
  [-dx,dx].forEach(o=>{el("circle",{cx:cx+o,cy:ey,r:er,fill:"#fff"},g);
    el("circle",{cx:cx+o,cy:ey,r:er*0.55,fill:"#222"},g);});}
const SPECIES_ICONS={
  Chicken:(g,cx,cy,r,c)=>{ // hen SIDE PROFILE (lean): tail + body + neck/breast + head + comb + beak + wattle + legs + eye
    el("path",{d:`M${cx+r*0.40} ${cy} q ${r*0.50} ${-r*0.10} ${r*0.675} ${-r*0.45} q ${r*0.025} ${r*0.275} ${-r*0.175} ${r*0.45} q ${r*0.175} ${-r*0.025} ${r*0.25} ${-r*0.225} q ${r*0.025} ${r*0.325} ${-r*0.375} ${r*0.45} z`,fill:"#3C617F"},g); // tail
    el("ellipse",{cx:cx,cy:cy+r*0.15,rx:r*0.55,ry:r*0.3625,fill:c},g);                     // body
    el("path",{d:`M${cx-r*0.40} ${cy+r*0.15} q ${-r*0.25} ${-r*0.25} ${-r*0.10} ${-r*0.55} q ${r*0.10} ${-r*0.20} ${r*0.30} ${-r*0.15} q ${r*0.20} ${r*0.05} ${r*0.15} ${r*0.30} q ${-r*0.05} ${r*0.25} ${-r*0.20} ${r*0.35} z`,fill:c},g); // neck + breast
    el("circle",{cx:cx-r*0.40,cy:cy-r*0.475,r:r*0.2125,fill:c},g);                          // head
    el("path",{d:`M${cx-r*0.525} ${cy-r*0.675} q ${r*0.05} ${-r*0.125} ${r*0.1125} ${-r*0.0375} q ${r*0.05} ${-r*0.125} ${r*0.1125} ${-r*0.0375} q ${r*0.025} ${r*0.0875} ${-r*0.05} ${r*0.1375} z`,fill:"#E0463A"},g); // comb
    el("path",{d:`M${cx-r*0.5875} ${cy-r*0.4625} l ${-r*0.225} ${r*0.05} l ${r*0.225} ${r*0.0875} z`,fill:"#E8A33D"},g); // beak
    el("path",{d:`M${cx-r*0.475} ${cy-r*0.30} q ${-r*0.025} ${r*0.125} ${r*0.0625} ${r*0.15} q ${r*0.0625} ${-r*0.05} ${r*0.025} ${-r*0.15} z`,fill:"#E0463A"},g); // wattle
    el("path",{d:`M${cx-r*0.05} ${cy+r*0.475} l 0 ${r*0.275} m 0 ${-r*0.0} l ${-r*0.125} ${r*0.075} m ${r*0.125} ${-r*0.075} l ${r*0.125} ${r*0.075}`,stroke:"#E8A33D","stroke-width":r*0.045,fill:"none","stroke-linecap":"round"},g); // leg L
    el("path",{d:`M${cx+r*0.225} ${cy+r*0.475} l 0 ${r*0.275} m 0 ${-r*0.0} l ${-r*0.125} ${r*0.075} m ${r*0.125} ${-r*0.075} l ${r*0.125} ${r*0.075}`,stroke:"#E8A33D","stroke-width":r*0.045,fill:"none","stroke-linecap":"round"},g); // leg R
    el("circle",{cx:cx-r*0.425,cy:cy-r*0.50,r:r*0.05,fill:"#fff"},g);el("circle",{cx:cx-r*0.435,cy:cy-r*0.50,r:r*0.03,fill:"#222"},g);}, // eye
  Beef:(g,cx,cy,r,c)=>{ // cow FACE: head + ears + horns + muzzle + eyes
    el("path",{d:`M${cx-r*0.42} ${cy-r*0.28} q ${-r*0.5} ${-r*0.18} ${-r*0.34} ${-r*0.5} q ${r*0.28} ${r*0.06} ${r*0.42} ${r*0.4}z`,fill:"#E8E0D0"},g); // horn L
    el("path",{d:`M${cx+r*0.42} ${cy-r*0.28} q ${r*0.5} ${-r*0.18} ${r*0.34} ${-r*0.5} q ${-r*0.28} ${r*0.06} ${-r*0.42} ${r*0.4}z`,fill:"#E8E0D0"},g); // horn R
    el("ellipse",{cx:cx-r*0.52,cy:cy,rx:r*0.2,ry:r*0.13,fill:c},g);el("ellipse",{cx:cx+r*0.52,cy:cy,rx:r*0.2,ry:r*0.13,fill:c},g); // ears
    el("ellipse",{cx:cx,cy:cy+r*0.05,rx:r*0.46,ry:r*0.5,fill:c},g);                        // head
    el("ellipse",{cx:cx,cy:cy+r*0.42,rx:r*0.32,ry:r*0.22,fill:"#F2C0BC"},g);               // muzzle
    el("circle",{cx:cx-r*0.12,cy:cy+r*0.44,r:r*0.05,fill:"#9A6A66"},g);el("circle",{cx:cx+r*0.12,cy:cy+r*0.44,r:r*0.05,fill:"#9A6A66"},g);
    _eyes(g,cx,cy-r*0.1,r*0.2,cy-r*0.1,r*0.11);},
  Pork:(g,cx,cy,r,c)=>{ // pig FACE: round + ears + snout + eyes
    el("path",{d:`M${cx-r*0.48} ${cy-r*0.28} l ${r*0.06} ${-r*0.34} l ${r*0.3} ${r*0.22}z`,fill:c},g); // ear L
    el("path",{d:`M${cx+r*0.48} ${cy-r*0.28} l ${-r*0.06} ${-r*0.34} l ${-r*0.3} ${r*0.22}z`,fill:c},g); // ear R
    el("circle",{cx:cx,cy:cy+r*0.08,r:r*0.56,fill:c},g);                                   // head
    el("ellipse",{cx:cx,cy:cy+r*0.34,rx:r*0.28,ry:r*0.2,fill:"#F2C0BC"},g);                // snout
    el("ellipse",{cx:cx-r*0.1,cy:cy+r*0.34,rx:r*0.045,ry:r*0.07,fill:"#C98E8A"},g);el("ellipse",{cx:cx+r*0.1,cy:cy+r*0.34,rx:r*0.045,ry:r*0.07,fill:"#C98E8A"},g);
    _eyes(g,cx,cy-r*0.06,r*0.22,cy-r*0.06,r*0.1);},
  Turkey:(g,cx,cy,r,c)=>{ // turkey: fanned tail behind + body + head + eyes
    for(let k=-3;k<=3;k++){const a=k*0.3; el("path",{d:`M${cx} ${cy+r*0.2} L ${cx+Math.sin(a)*r*0.95} ${cy+r*0.2-Math.cos(a)*r*0.95}`,stroke:(k%2?c:"#B5703A"),"stroke-width":r*0.2,"stroke-linecap":"round"},g);}
    el("ellipse",{cx:cx,cy:cy+r*0.4,rx:r*0.36,ry:r*0.42,fill:c},g);                        // body
    el("circle",{cx:cx,cy:cy+r*0.12,r:r*0.2,fill:c},g);                                    // head
    el("path",{d:`M${cx} ${cy+r*0.16} l ${r*0.22} ${r*0.04} l ${-r*0.2} ${r*0.14}z`,fill:"#E8A33D"},g); // beak
    el("path",{d:`M${cx-r*0.04} ${cy+r*0.04} q ${-r*0.04} ${-r*0.16} ${r*0.04} ${-r*0.16}`,stroke:"#E0463A","stroke-width":r*0.07,fill:"none"},g); // snood
    _eyes(g,cx,cy+r*0.08,r*0.09,cy+r*0.08,r*0.06);},
  Duck:(g,cx,cy,r,c)=>{ // duck SIDE PROFILE (swimming, facing right): solid overlapping body+head (like the hen),
    // short neck wedge, flat BILL, upswept tail, folded wing. NO hollow ring — every part overlaps solidly.
    const d=c, dk="#2F5446", wg="#33594B";   // body, darker tail, folded wing
    el("ellipse",{cx:cx,cy:cy+r*0.18,rx:r*0.78,ry:r*0.50,fill:d},g);                         // body
    el("path",{d:`M${cx-r*0.55} ${cy} q ${-r*0.45} ${-r*0.12} ${-r*0.66} ${-r*0.30} q ${r*0.10} ${r*0.34} ${r*0.66} ${r*0.40} z`,fill:dk},g); // tail (upswept, off the back)
    el("path",{d:`M${cx+r*0.18} ${cy-r*0.10} q ${r*0.10} ${-r*0.38} ${r*0.45} ${-r*0.50} q ${r*0.20} ${r*0.05} ${r*0.18} ${r*0.30} q ${-r*0.20} ${r*0.18} ${-r*0.50} ${r*0.28} z`,fill:d},g); // short neck wedge
    el("circle",{cx:cx+r*0.50,cy:cy-r*0.42,r:r*0.30,fill:d},g);                              // head (overlaps body)
    el("path",{d:`M${cx+r*0.78} ${cy-r*0.46} q ${r*0.42} ${-r*0.02} ${r*0.44} ${r*0.08} q ${-r*0.02} ${r*0.10} ${-r*0.44} ${r*0.09} q ${-r*0.08} ${-r*0.085} 0 ${-r*0.17} z`,fill:"#E8A33D"},g); // flat BILL (forward)
    el("circle",{cx:cx+r*0.58,cy:cy-r*0.50,r:r*0.055,fill:"#fff"},g);el("circle",{cx:cx+r*0.595,cy:cy-r*0.50,r:r*0.032,fill:"#1c1c1c"},g); // eye
    el("path",{d:`M${cx-r*0.18} ${cy-r*0.04} q ${r*0.34} ${-r*0.24} ${r*0.64} ${-r*0.10} q ${-r*0.16} ${r*0.22} ${-r*0.50} ${r*0.18} q ${-r*0.14} ${-r*0.06} ${-r*0.14} ${-r*0.18} z`,fill:wg},g);}, // folded wing
  Seafood:(g,cx,cy,r,c)=>{ // fish: teardrop body + tail + dorsal & pelvic fins + gill + eye + mouth
    el("path",{d:`M${cx-r*0.75} ${cy} q ${r*0.40} ${-r*0.50} ${r*1.0} ${-r*0.30} q ${r*0.25} ${r*0.10} ${r*0.30} ${r*0.30} q ${-r*0.05} ${r*0.20} ${-r*0.30} ${r*0.30} q ${-r*0.60} ${r*0.20} ${-r*1.0} ${-r*0.30} z`,fill:c},g); // body
    el("path",{d:`M${cx+r*0.50} ${cy} l ${r*0.50} ${-r*0.325} q ${-r*0.15} ${r*0.325} 0 ${r*0.65} z`,fill:c},g);   // tail
    el("path",{d:`M${cx-r*0.15} ${cy-r*0.25} q ${r*0.25} ${-r*0.20} ${r*0.50} ${-r*0.075} q ${-r*0.20} ${r*0.05} ${-r*0.50} ${r*0.075} z`,fill:"#3F7C39"},g); // dorsal fin
    el("path",{d:`M${cx} ${cy+r*0.275} q ${r*0.15} ${r*0.15} ${r*0.35} ${r*0.125} q ${-r*0.15} ${-r*0.125} ${-r*0.35} ${-r*0.125} z`,fill:"#3F7C39"},g); // pelvic fin
    el("path",{d:`M${cx-r*0.35} ${cy-r*0.225} q ${-r*0.125} ${r*0.225} 0 ${r*0.45}`,stroke:"#3F7C39","stroke-width":r*0.05,fill:"none"},g); // gill
    el("circle",{cx:cx-r*0.475,cy:cy-r*0.05,r:r*0.11,fill:"#fff"},g);el("circle",{cx:cx-r*0.475,cy:cy-r*0.05,r:r*0.0575,fill:"#222"},g); // eye
    el("path",{d:`M${cx-r*0.75} ${cy} q ${r*0.075} ${r*0.075} ${r*0.025} ${r*0.175}`,stroke:"#3F7C39","stroke-width":r*0.05,fill:"none"},g);}, // mouth
  "Sheep/goat":(g,cx,cy,r,c)=>{ // sheep FACE: woolly cloud crown + face + ears + eyes
    [[-0.34,-0.28],[0,-0.4],[0.34,-0.28],[-0.5,-0.05],[0.5,-0.05]].forEach(([dx,dy])=>   // wool puffs round the top
      el("circle",{cx:cx+dx*r,cy:cy+dy*r,r:r*0.27,fill:c},g));
    el("ellipse",{cx:cx-r*0.5,cy:cy+r*0.18,rx:r*0.16,ry:r*0.1,fill:"#5C4A3E"},g);el("ellipse",{cx:cx+r*0.5,cy:cy+r*0.18,rx:r*0.16,ry:r*0.1,fill:"#5C4A3E"},g); // ears (drooping)
    el("ellipse",{cx:cx,cy:cy+r*0.18,rx:r*0.36,ry:r*0.4,fill:"#6B5648"},g);               // face (long muzzle)
    _eyes(g,cx,cy+r*0.02,r*0.16,cy+r*0.02,r*0.1);
    el("ellipse",{cx:cx,cy:cy+r*0.46,rx:r*0.1,ry:r*0.07,fill:"#3E322A"},g);},              // nose
  Goat:(g,cx,cy,r,c)=>{ // goat FACE: face + back-swept horns + beard + eyes
    el("path",{d:`M${cx-r*0.28} ${cy-r*0.36} q ${-r*0.2} ${-r*0.4} ${r*0.06} ${-r*0.5}`,stroke:"#C9BBA8","stroke-width":r*0.12,fill:"none","stroke-linecap":"round"},g); // horn L
    el("path",{d:`M${cx+r*0.28} ${cy-r*0.36} q ${r*0.2} ${-r*0.4} ${-r*0.06} ${-r*0.5}`,stroke:"#C9BBA8","stroke-width":r*0.12,fill:"none","stroke-linecap":"round"},g); // horn R
    el("ellipse",{cx:cx-r*0.46,cy:cy+r*0.05,rx:r*0.18,ry:r*0.1,fill:c},g);el("ellipse",{cx:cx+r*0.46,cy:cy+r*0.05,rx:r*0.18,ry:r*0.1,fill:c},g); // ears
    el("path",{d:`M${cx-r*0.38} ${cy-r*0.18} q ${r*0.38} ${r*0.2} ${r*0.76} 0 q ${-r*0.1} ${r*0.6} ${-r*0.38} ${r*0.7} q ${-r*0.28} ${-r*0.1} ${-r*0.38} ${-r*0.7}z`,fill:c},g); // face
    _eyes(g,cx,cy+r*0.04,r*0.18,cy+r*0.04,r*0.1);
    el("path",{d:`M${cx-r*0.08} ${cy+r*0.5} l ${r*0.16} 0 l ${-r*0.05} ${r*0.3} z`,fill:"#8A7A66"},g);}, // beard
  Rabbit:(g,cx,cy,r,c)=>{ // rabbit FACE: head + long ears + eyes + nose
    el("ellipse",{cx:cx-r*0.2,cy:cy-r*0.42,rx:r*0.13,ry:r*0.42,fill:c},g);                 // ear L
    el("ellipse",{cx:cx-r*0.2,cy:cy-r*0.42,rx:r*0.06,ry:r*0.3,fill:"#F2C0BC"},g);
    el("ellipse",{cx:cx+r*0.2,cy:cy-r*0.42,rx:r*0.13,ry:r*0.42,fill:c},g);                 // ear R
    el("ellipse",{cx:cx+r*0.2,cy:cy-r*0.42,rx:r*0.06,ry:r*0.3,fill:"#F2C0BC"},g);
    el("circle",{cx:cx,cy:cy+r*0.18,r:r*0.42,fill:c},g);                                   // head
    _eyes(g,cx,cy+r*0.12,r*0.18,cy+r*0.12,r*0.1);
    el("ellipse",{cx:cx,cy:cy+r*0.34,rx:r*0.07,ry:r*0.05,fill:"#E08F9A"},g);},              // nose
  Buffalo:(g,cx,cy,r,c)=>{ // buffalo FACE: big curved horns + head + muzzle + eyes
    el("path",{d:`M${cx-r*0.4} ${cy-r*0.18} q ${-r*0.55} ${-r*0.05} ${-r*0.5} ${-r*0.4} q ${-r*0.25} ${r*0.25} ${r*0.0} ${r*0.4} q ${r*0.2} ${-r*0.1} ${r*0.5} ${r*0.0}z`,fill:"#5B5B5B"},g); // horn L
    el("path",{d:`M${cx+r*0.4} ${cy-r*0.18} q ${r*0.55} ${-r*0.05} ${r*0.5} ${-r*0.4} q ${r*0.25} ${r*0.25} ${-r*0.0} ${r*0.4} q ${-r*0.2} ${-r*0.1} ${-r*0.5} ${r*0.0}z`,fill:"#5B5B5B"},g); // horn R
    el("ellipse",{cx:cx,cy:cy+r*0.12,rx:r*0.44,ry:r*0.46,fill:c},g);                       // head
    el("ellipse",{cx:cx,cy:cy+r*0.44,rx:r*0.3,ry:r*0.2,fill:"#C9BBB3"},g);                 // muzzle
    _eyes(g,cx,cy,r*0.2,cy,r*0.1);}
};
function drawSpeciesIcon(g,species,cx,cy,size){
  const fn=SPECIES_ICONS[species]; const c=COLSP[species]||"#888";
  if(fn) fn(g,cx,cy,size,c);
  else el("circle",{cx,cy,r:size*0.5,fill:c},g);   // fallback dot
}
function colOf(species){return COLSP[species]||"#BAB0AC";}

/* ---------- tiny SVG helpers ---------- */
function el(t,a,p){const e=document.createElementNS(SV,t);for(const k in a)e.setAttribute(k,a[k]);
  if(p)p.appendChild(e);return e;}
function tx(p,x,y,s,a){const t=el("text",Object.assign({x,y},a||{}),p);t.textContent=s;return t;}
// word-wrap a string into multiple <text> lines within maxW px; returns the y AFTER the last line.
// fontPx ~ font-size; lineH ~ line spacing. SVG <text> never auto-wraps, so we greedily pack words
// using a ~0.52*fontPx average glyph width (good enough for these short justifications).
function txWrap(p,x,y,s,maxW,a,lineH){const fpx=(a&&a["font-size"])?parseFloat(a["font-size"]):10;
  lineH=lineH||(fpx+3); const cw=fpx*0.52, max=Math.max(1,Math.floor(maxW/cw));
  const words=String(s).split(" "); let line="", yy=y;
  for(const w of words){const t=line?line+" "+w:w;
    if(t.length>max && line){tx(p,x,yy,line,a); yy+=lineH; line=w;} else line=t;}
  if(line){tx(p,x,yy,line,a); yy+=lineH;}
  return yy;}
// text with a "R" + subscript "x" + suffix, e.g. txRsub(svg, x, y, "Price ratio ", "x", " (…)", attrs)
function txRsub(p,x,y,pre,sub,suf,a){const t=el("text",Object.assign({x,y},a||{}),p);
  const mk=(txt,extra)=>{const s=el("tspan",extra||{},t);s.textContent=txt;};
  mk(pre); mk("R"); mk(sub,{"baseline-shift":"sub","font-size":"0.75em"}); mk(suf); return t;}
function clear(svg){while(svg.firstChild)svg.removeChild(svg.firstChild);}
const fmtPct=v=>(v*100).toFixed(0)+"%";
// Tooltip text is authored with light HTML markup (subscripts like R<sub>x</sub>, &times;, &rho;,
// &sect; …) and is ENTIRELY build-time / author-controlled (no user input ever reaches it), so it is
// rendered as HTML. Using innerHTML here is what makes R<sub>x</sub> show as a real subscript instead
// of leaking the literal tag. (If dynamic/user content ever needs to go in a tip, sanitise it first.)
function showTip(e,text){const t=document.getElementById("tip");t.innerHTML=text;t.style.display="block";
  const r=e.target.getBoundingClientRect();
  t.style.left=Math.max(8,Math.min(window.innerWidth-300,r.left-10))+"px";
  const th=t.offsetHeight, below=r.bottom+6, above=r.top-th-6;   // flip above if it would overflow the bottom
  t.style.top=Math.max(8, (below+th<=window.innerHeight-8) ? below : above)+"px";}
function hideTip(){document.getElementById("tip").style.display="none";}
function addQ(parent,text){const q=document.createElement("span");q.className="q";q.textContent="?";
  q.onmouseenter=e=>showTip(e,text);q.onmouseleave=hideTip;
  q.onclick=e=>{const t=document.getElementById("tip");
    if(t.style.display==="block")hideTip();else showTip(e,text);};
  parent.appendChild(q);return q;}

/* ---------- the four live views ---------- */
function drawHeads(s){
  const b=biomass(s), p=penetration(s), R=basicR(s);
  const retail=b+s.markup_add, conv=C.p_conv_anchor*s.meat_tax, cut=retail+s.scaffold;
  const reg=MODEL.regions.find(r=>r[0]===s.region)[1];
  // Each cell = [big number, label HTML, second line, colour, tooltip]. The tooltip uses the same addQ()
  // "?" badge as the sliders (a styled #tip popup), not a native title= attribute.
  const cultTip="Cultivated meat's long-run share of the meat market in this region at the current settings: once "+
    "it is on every shelf and no longer feels new. Not today's share: chart 5 shows the path up from near zero. The "+
    "big number weights each kind of meat by weight eaten; the second line by money spent. Counted in animals it "+
    "would be lower, since most land animals raised for meat are chickens, where cultivated does worst.";
  const pbTip="The same for plant-based meat, which the model is fitted to reproduce (~1.2% of US meat).";
  const rTip="Cultivated meat's retail price divided by the price of everyday conventional meat, using a round "+
    "benchmark of $"+conv.toFixed(0)+"/kg (each meat type in charts 1, 2 and 7 uses its own local price). "+
    "1&times; = price parity. The same for every region. Structured cuts also need a scaffold: $"+cut.toFixed(0)+"/kg.";
  const cells=[
    [(p.tv*100).toFixed(1)+"%","<b>cultivated</b>: long-run share of the meat market by weight ("+reg+")",
     (p.tval*100).toFixed(1)+"% by value","var(--accent)",cultTip],
    [(p.tvp*100).toFixed(1)+"%","<b>plant-based</b>: share of the meat market by weight ("+reg+")",
     (p.tvalp*100).toFixed(1)+"% by value","var(--green)",pbTip],
    [R.toFixed(1)+"&times;","<b>cultivated's price</b> vs everyday meat",
     "$"+retail.toFixed(0)+" vs $"+conv.toFixed(0)+" a kilo (benchmark)","var(--ink)",rTip]];
  const h=document.getElementById("heads"); h.innerHTML="";
  cells.forEach(([big,lab,sub,col,tip])=>{const d=document.createElement("div");d.className="head";
    d.innerHTML='<div class="big" style="color:'+col+'">'+big+'</div><div class="lab">'+lab+'</div>'+
      '<div class="sub2">'+sub+'</div>';
    if(tip) addQ(d.querySelector(".lab"),tip);     // the styled "?" tooltip badge, after the label
    h.appendChild(d);});
}
function drawBars(s,ptmc){
  const svg=document.getElementById("bars");clear(svg);
  const W=720,H=300,mL=40,mR=150,mT=34,mB=46;       // wide right margin = a dedicated gutter for the totals labels
  const {rows,tv,tval,tvp,tvalp}=penetration(s);
  const groups={};
  rows.forEach(r=>{const a=animalOf(r.mt.name);(groups[a]=groups[a]||[]).push(r);});
  const order=Object.keys(groups).sort((a,b)=>
    (groups[a].reduce((x,r)=>x+r.mt.p_conv,0)/groups[a].length)-
    (groups[b].reduce((x,r)=>x+r.mt.p_conv,0)/groups[b].length));
  // the bars STACK cultivated + plant-based, so the axis must reach the tallest STACK (or its band)
  const stackTop=r=>{const w=ptmc&&ptmc[r.mt.name];return (w?w.p50:r.sh)+(w?w.pp50:r.shp);};
  const whisk=ptmc?Math.max(...rows.map(r=>{const w=ptmc[r.mt.name]||{p90:0,pp50:0,pp90:0};
    return Math.max(w.p90+w.pp50, w.p50+w.pp90);})):0;
  const maxs=Math.max(0.2,whisk,...rows.map(stackTop)), yTop=maxs*1.18;
  const X=i=>mL+(W-mL-mR)*(i+0.5)/order.length, Y=v=>H-mB-(H-mT-mB)*v/yTop;
  el("line",{x1:mL,y1:H-mB,x2:W-mR,y2:H-mB,stroke:"#ccc"},svg);
  [0,.1,.2,.3,.4,.5,.6,.7,.8].filter(v=>v<=yTop).forEach(v=>{
    el("line",{x1:mL,y1:Y(v),x2:W-mR,y2:Y(v),stroke:"#eee"},svg);
    tx(svg,mL-5,Y(v)+3,(v*100).toFixed(0),{"font-size":9,"text-anchor":"end",fill:"#666"});});
  // rolled-up totals: cultivated by volume & value (dark dashes), plant-based by volume & value (green dashes).
  // Draw the dashed LINES across the chart, but place the LABELS in a right-side strip with a de-collision
  // pass (sort by y, nudge any that are <11px apart) so they never overlap each other, the bars, or the
  // species names. Labels are right-anchored at the chart's right edge, where the bars are shortest.
  // Two-channel encoding: COLOUR = product (cultivated dark grey/black, plant-based green);
  // DASH = metric (loose "5 3" = volume, tight "1 3" = value). So a reader learns the key once.
  const totals=[
    [tv,   "#444444","cultivated · volume "+(tv*100).toFixed(0)+"%",   "5 3"],
    [tval, "#444444","cultivated · value $ "+(tval*100).toFixed(0)+"%","1 3"],
    [tvp,  "#117733","plant-based · volume "+(tvp*100).toFixed(0)+"%", "5 3"],
    [tvalp,"#117733","plant-based · value $ "+(tvalp*100).toFixed(0)+"%","1 3"]];
  // dashed lines span only the PLOT area (mL..W-mR); the labels live in the right GUTTER (past W-mR),
  // each connected to its line by a short leader, so they never touch a bar. A de-collision pass keeps
  // the four labels from stacking when their values are close (e.g. the two plant-based totals).
  totals.forEach(([v,c,,dash])=>{
    el("line",{x1:mL,y1:Y(v),x2:W-mR,y2:Y(v),stroke:c,"stroke-dasharray":dash},svg);});
  const GAP=12, lblY=totals.map(([v])=>Y(v)).map((y,i)=>({y,yLine:y,i})).sort((a,b)=>a.y-b.y);
  for(let k=1;k<lblY.length;k++) if(lblY[k].y-lblY[k-1].y<GAP) lblY[k].y=lblY[k-1].y+GAP;
  const overflow=lblY[lblY.length-1].y-(H-mB-2);                   // keep inside the plot height
  if(overflow>0) lblY.forEach(o=>o.y-=overflow);
  lblY.forEach(({y,yLine,i})=>{const [,c,lab]=totals[i];
    el("line",{x1:W-mR,y1:yLine,x2:W-mR+5,y2:y-3,stroke:c,"stroke-width":0.6,opacity:0.6},svg); // leader from line to label
    tx(svg,W-mR+7,y-1,lab,{"font-size":8.5,fill:c});});            // label in the gutter, left-anchored
  const COL={basic:"#E69F00",cut:"#0072B2",premium:"#882255"}, TO={basic:0,cut:1,premium:2};
  // plant-based segment = the SAME tier colour, lightened (blended toward white) so a stack reads as
  // "this tier's cultivated (solid) + plant-based (pale)". lighten(hex, f) blends f of the way to white.
  const lighten=(hex,f)=>{const n=parseInt(hex.slice(1),16);
    const r=(n>>16)&255,g=(n>>8)&255,b2=n&255, m=x=>Math.round(x+(255-x)*f);
    return "rgb("+m(r)+","+m(g)+","+m(b2)+")";};
  const PB_F=0.45;                                     // how far toward white the PB segment sits — 0.45 keeps
  // every tier's PB segment clear of the gridlines/background (the old 0.62 washed the pale-orange basic tier
  // out) while staying distinct from the solid cultivated below it; the thin tier-colour outline reinforces it.
  const bw=Math.min(18,(W-mL-mR)/order.length/3.4);
  order.forEach((a,i)=>{
    const items=groups[a].sort((p,q)=>TO[p.t]-TO[q.t]), n=items.length;
    items.forEach((r,j)=>{
      const cx=X(i)+(j-(n-1)/2)*(bw*1.18);
      const w=ptmc&&ptmc[r.mt.name];                    // P10-P50-P90 Monte-Carlo summary (cult .p*, PB .pp*)
      // when MC is on the bars ARE the MC medians (so the whisker brackets them; the priors for
      // accept_x/theta_free are one-sided vs their slider defaults, so a point-estimate bar would
      // sit at the edge of — or outside — the band). MC off: the point estimates.
      const ch=w?w.p50:r.sh, ph=w?w.pp50:r.shp, top=ch+ph;     // cultivated, plant-based, stacked total
      const pbCol=lighten(COL[r.t],PB_F);              // plant-based = the tier colour, lightened
      // cultivated segment (bottom, solid tier colour); plant-based segment stacked on top (same hue, paler)
      el("rect",{x:cx-bw/2,y:Y(ch),width:bw,height:H-mB-Y(ch),fill:COL[r.t],opacity:0.92},svg);
      if(ph>0.002) el("rect",{x:cx-bw/2,y:Y(top),width:bw,height:Y(ch)-Y(top),fill:pbCol,
        stroke:COL[r.t],"stroke-width":0.5},svg);       // thin outline keeps the pale segment visible
      if(w){ // cultivated whisker (within its own segment), then PB whisker (around the stacked top)
        el("line",{x1:cx,y1:Y(w.p10),x2:cx,y2:Y(w.p90),stroke:"#333","stroke-width":1},svg);
        el("line",{x1:cx-3,y1:Y(w.p10),x2:cx+3,y2:Y(w.p10),stroke:"#333","stroke-width":1},svg);
        el("line",{x1:cx-3,y1:Y(w.p90),x2:cx+3,y2:Y(w.p90),stroke:"#333","stroke-width":1},svg);
        const pLo=ch+w.pp10, pHi=ch+w.pp90;             // PB band sits ON TOP of the cultivated median
        const pbWhisk=lighten(COL[r.t],0.25);           // a darker shade of the tier hue, for the PB whisker
        el("line",{x1:cx,y1:Y(pLo),x2:cx,y2:Y(pHi),stroke:pbWhisk,"stroke-width":1},svg);
        el("line",{x1:cx-3,y1:Y(pLo),x2:cx+3,y2:Y(pLo),stroke:pbWhisk,"stroke-width":1},svg);
        el("line",{x1:cx-3,y1:Y(pHi),x2:cx+3,y2:Y(pHi),stroke:pbWhisk,"stroke-width":1},svg);}
      // labels above the stack: cultivated %, then "+PB %" if PB is non-trivial, then R
      const labY=Y(w?Math.max(w.p90,top,ch+w.pp90):top);
      tx(svg,cx,labY-(ph>0.002?17:9),fmtPct(ch),{"font-size":8.5,"text-anchor":"middle","font-weight":700,fill:COL[r.t]});
      if(ph>0.002) tx(svg,cx,labY-9,"+"+fmtPct(ph),{"font-size":8,"text-anchor":"middle","font-weight":700,fill:lighten(COL[r.t],0.25)});
      tx(svg,cx,labY-1,"R="+r.R.toFixed(2),{"font-size":7,"text-anchor":"middle",fill:"#888"});
    });
    drawSpeciesIcon(svg,a,X(i),H-mB+15,11);                 // species ICON under the bar group
    tx(svg,X(i),H-mB+34,a,{"font-size":7.5,"text-anchor":"middle",fill:"#888"});  // small name caption
  });
  // legend in the top header strip, anchored to the plot's left edge (robust to the gutter width).
  // row 1: cultivated tiers; row 2: the plant-based stack segment
  let lx=mL;
  [["#E69F00","mince/processed"],["#0072B2","cut/fillet"],
   ["#882255","premium (≥"+C.PREMIUM_RATIO.toFixed(1)+"× base)"]].forEach(([c,l])=>{
    el("rect",{x:lx,y:mT-26,width:9,height:9,fill:c},svg);
    tx(svg,lx+12,mT-18,l,{"font-size":9,fill:"#333"});lx+=100;});
  // row 2: convey "solid = cultivated, pale = plant-based" with a paired swatch (blue tier as example)
  el("rect",{x:mL,y:mT-14,width:9,height:9,fill:COL.cut},svg);
  el("rect",{x:mL+9,y:mT-14,width:9,height:9,fill:lighten(COL.cut,PB_F),
    stroke:COL.cut,"stroke-width":0.5},svg);
  tx(svg,mL+22,mT-6,"solid = cultivated, pale = plant-based (same tier hue)"+
    (ptmc?";  whiskers = 10–90%":""),{"font-size":9,fill:"#555"});
  // live reading of the chart: the biggest share, and where most of the displaced VOLUME comes from
  const topS=rows.reduce((a,r)=>r.sh>a.sh?r:a), topV=rows.reduce((a,r)=>r.mt.w_vol*r.sh>a.mt.w_vol*a.sh?r:a);
  document.getElementById("barsub").innerHTML=
    "Share within each kind of meat; dashed lines are totals. <b>"+MODEL.regions.find(r=>r[0]===s.region)[1]+":</b> "+
    (topS===topV
      ? "biggest share and most volume in "+topS.mt.name+" ("+fmtPct(topS.sh)+")."
      : "biggest share in "+topS.mt.name+" ("+fmtPct(topS.sh)+"); most volume from "+topV.mt.name+
        " ("+fmtPct(topV.sh)+").");
}
function drawPie(s){
  const svg=document.getElementById("pie");clear(svg);
  const byVal=state.pieBasis==="val";                                   // wedge basis: volume or $ value
  const cx=185,cy=168,rO=138,rI=76;
  const {rows,tv,tval}=penetration(s);
  const groups={};
  rows.forEach(r=>{const a=animalOf(r.mt.name);
    const g=groups[a]=groups[a]||{vol:0,cult:0,pb:0,val:0,cultval:0,pbval:0,pmin:Infinity,pmax:0};
    g.vol+=r.mt.w_vol; g.cult+=r.mt.w_vol*r.sh; g.pb+=r.mt.w_vol*r.shp;                       // by volume (mass)
    g.val+=r.mt.p_conv*r.mt.w_vol; g.cultval+=r.mt.p_conv*r.mt.w_vol*r.sh; g.pbval+=r.mt.p_conv*r.mt.w_vol*r.shp; // by value ($)
    g.pmin=Math.min(g.pmin,r.mt.p_conv);g.pmax=Math.max(g.pmax,r.mt.p_conv);});
  const wt=g=>byVal?g.val:g.vol, cfOf=g=>{const d=wt(g);return d>0?(byVal?g.cultval:g.cult)/d:0;},
        pfOf=g=>{const d=wt(g);return d>0?(byVal?g.pbval:g.pb)/d:0;};
  const items=Object.entries(groups).sort((x,y)=>wt(y[1])-wt(x[1]));
  const tot=items.reduce((a,[,g])=>a+wt(g),0);
  const A=(r,a)=>[cx+r*Math.cos(a),cy+r*Math.sin(a)];
  function arc(r0,r1,a0,a1){const[x0,y0]=A(r1,a0),[x1,y1]=A(r1,a1),[xa,ya]=A(r0,a1),[xb,yb]=A(r0,a0),
    big=(a1-a0)>Math.PI?1:0;
    return "M"+x0+" "+y0+" A"+r1+" "+r1+" 0 "+big+" 1 "+x1+" "+y1+" L"+xa+" "+ya+
      " A"+r0+" "+r0+" 0 "+big+" 0 "+xb+" "+yb+" Z";}
  let ang=-Math.PI/2, pbTot=0;
  items.forEach(([name,g],k)=>{
    const a1=ang+(wt(g)/tot)*2*Math.PI, col=colOf(name);
    el("path",{d:arc(rI,rO,ang,a1),fill:col,opacity:0.20},svg);             // conventional / other (pale)
    const cf=cfOf(g), pf=pfOf(g), rC=rI+(rO-rI)*cf;
    el("path",{d:arc(rI,rC,ang,a1),fill:col,opacity:0.95},svg);             // cultivated (solid, innermost)
    el("path",{d:arc(rC,rC+(rO-rI)*pf,ang,a1),fill:col,opacity:0.50},svg);  // plant-based (lighter band)
    pbTot+=pf*wt(g); ang=a1;
  });
  tx(svg,cx,cy-2,((byVal?tval:tv)*100).toFixed(1)+"%",{"font-size":27,"text-anchor":"middle","font-weight":700,fill:"#117733"});
  tx(svg,cx,cy+17,"cultivated",{"font-size":11,"text-anchor":"middle",fill:"#666"});
  tx(svg,cx,cy+30,"of meat by "+(byVal?"value":"volume"),{"font-size":9,"text-anchor":"middle",fill:"#999"});
  tx(svg,cx,cy+45,"plant-based "+(pbTot/tot*100).toFixed(1)+"%",{"font-size":9.5,"text-anchor":"middle",fill:"#117733"});
  // legend table on the right (price + share of all meat + cultivated & plant-based portions)
  const lx=350; let ly=44;
  tx(svg,lx,ly-15,"meat type",{"font-size":9,fill:"#999"});
  tx(svg,lx+150,ly-15,"$/kg",{"font-size":9,fill:"#999","text-anchor":"end"});
  tx(svg,lx+212,ly-15,"of all meat",{"font-size":9,fill:"#999","text-anchor":"end"});
  tx(svg,lx+278,ly-15,"cultivated",{"font-size":9,fill:"#999","text-anchor":"end"});
  tx(svg,lx+366,ly-15,"plant-based",{"font-size":9,fill:"#999","text-anchor":"end"});
  items.forEach(([name,g],k)=>{
    const col=colOf(name), cf=cfOf(g), pf=pfOf(g);
    const pr=g.pmax-g.pmin<0.5?"$"+g.pmin.toFixed(0):"$"+g.pmin.toFixed(0)+"–"+g.pmax.toFixed(0);
    drawSpeciesIcon(svg,name.replace("\n"," "),lx+7,ly-4,9);   // species icon in place of the colour swatch
    tx(svg,lx+20,ly,name.replace("\n"," "),{"font-size":11,fill:"#333"});
    tx(svg,lx+150,ly,pr,{"font-size":11,fill:"#555","text-anchor":"end"});
    tx(svg,lx+212,ly,(wt(g)/tot*100).toFixed(0)+"%",{"font-size":11,fill:"#555","text-anchor":"end"});
    tx(svg,lx+278,ly,(cf*100).toFixed(0)+"%",{"font-size":11,fill:"#117733","text-anchor":"end","font-weight":600});
    tx(svg,lx+366,ly,(pf*100).toFixed(1)+"%",{"font-size":11,fill:"#117733","text-anchor":"end","opacity":0.7});
    ly+=23;
  });
  tx(svg,lx,ly+10,"bands inner→out: cultivated (solid) · plant-based (lighter) · pale = conventional/other",{"font-size":8.5,fill:"#999"});
  document.getElementById("piesub").textContent=byVal
    ? "each wedge is a meat type sized by its $ market value (price × volume); the shaded inner part is the cultivated fraction of that $"
    : "each wedge is a meat type sized by how much is eaten (mass → animal impact); the shaded inner part is the cultivated fraction";
}
function buildPieToggle(){
  const host=document.getElementById("pietog");host.innerHTML="";
  [["vol","by volume"],["val","by value"]].forEach(([v,l])=>{
    const b=document.createElement("button");b.textContent=l;
    if(state.pieBasis===v)b.className="on";
    b.onclick=()=>{state.pieBasis=v;buildPieToggle();drawPie(state);};
    host.appendChild(b);});
}
function drawCost(s){
  const svg=document.getElementById("cost");clear(svg);
  const W=720,H=300,mL=42,mR=14,mT=14,mB=40, x0=0.10,x1=1.0,y1=52;
  const X=v=>mL+(W-mL-mR)*(v-x0)/(x1-x0), Y=v=>H-mB-(H-mT-mB)*v/y1;
  el("line",{x1:mL,y1:H-mB,x2:W-mR,y2:H-mB,stroke:"#ccc"},svg);
  el("line",{x1:mL,y1:mT,x2:mL,y2:H-mB,stroke:"#ccc"},svg);
  [0,10,20,30,40,50].forEach(v=>{tx(svg,mL-5,Y(v)+3,v,{"font-size":9,"text-anchor":"end",fill:"#666"});
    el("line",{x1:mL,y1:Y(v),x2:W-mR,y2:Y(v),stroke:"#f0f0f0"},svg);});
  [0.2,0.4,0.63,0.8,1.0].forEach(v=>tx(svg,X(v),H-mB+13,v.toFixed(2).replace(/0$/,""),
    {"font-size":9,"text-anchor":"middle",fill:"#666"}));
  const cols=["#117733","#0072B2","#CC3311"];
  C.configs.forEach(([lab,oh],k)=>{
    let d="";for(let i=0;i<=40;i++){const mp=x0+(x1-x0)*i/40;
      const b=mediaCost(mp,s.efficiency)+oh;
      d+=(i?"L":"M")+X(mp).toFixed(1)+" "+Y(b).toFixed(1)+" ";}
    el("path",{d,fill:"none",stroke:cols[k],"stroke-width":2},svg);
    tx(svg,W-mR-2,Y(mediaCost(x1,s.efficiency)+oh)-2,lab,
      {"font-size":8,"text-anchor":"end",fill:cols[k]});});
  // floor + parity
  el("line",{x1:mL,y1:Y(C.cost_floor),x2:W-mR,y2:Y(C.cost_floor),stroke:"#117733","stroke-dasharray":"4 3"},svg);
  tx(svg,mL+3,Y(C.cost_floor)-3,"floor ~$"+C.cost_floor.toFixed(1)+"/kg",{"font-size":8,fill:"#117733"});
  const par=C.p_conv_anchor*s.meat_tax-s.markup_add;
  el("line",{x1:mL,y1:Y(par),x2:W-mR,y2:Y(par),stroke:"#CC3311","stroke-dasharray":"1 3"},svg);
  tx(svg,mL+3,Y(par)+11,"parity ≤ $"+par.toFixed(0)+"/kg",{"font-size":8,fill:"#CC3311"});
  // marker
  const b=biomass(s);
  el("circle",{cx:X(s.media_price),cy:Y(b),r:5,fill:"#000"},svg);
  tx(svg,X(s.media_price),Y(b)-8,"$"+b.toFixed(0)+"/kg",{"font-size":9,"text-anchor":"middle","font-weight":700});
  tx(svg,(mL+W-mR)/2,H-3,"Medium price ($/L)",{"font-size":9,"text-anchor":"middle",fill:"#444"});
}
function drawCurve(s){
  const svg=document.getElementById("curve");clear(svg);
  const W=420,H=300,mL=40,mR=14,mT=22,mB=40, x0=0.5,y1=90;
  // the chosen product: its tier sets the authenticity offset + elasticity multiplier
  const market=MODEL.markets[s.region];
  const mt=market.find(m=>m.name===state.curveType)||market[0];
  const rpr=(s.premium_resistance===undefined?1:s.premium_resistance);
  const {R:Rmark,t}=typeR(mt,biomass(s),s.markup_add,s,speciesBases(market));
  const eps=s.eps_own*tMult(t,rpr);
  const Rp=s.R_p;                                                   // plant-based's OWN price ratio (its marker x)
  // x-axis extends to cover BOTH markers (cultivated's Rmark and plant-based's R_p) so the dots land ON the curves
  const x1=Math.max(3, Math.ceil((Math.max(Rmark,Rp)+0.4)*2)/2);
  const X=v=>mL+(W-mL-mR)*(v-x0)/(x1-x0), Y=v=>H-mB-(H-mT-mB)*v/y1;
  const evW=(R,which)=>shareCalc(R,KP,{ax:s.accept_x,tfM:s.theta_free_M,toff:tAuth(t,rpr),eps,
                              income:s.income,pricePb:s.R_p,aP:s.a_p,nbx:s.neophobia_x,nbp:s.neophobia_p,which});
  el("line",{x1:mL,y1:H-mB,x2:W-mR,y2:H-mB,stroke:"#ccc"},svg);
  [0,20,40,60,80].forEach(v=>{tx(svg,mL-5,Y(v)+3,v,{"font-size":9,"text-anchor":"end",fill:"#666"});
    el("line",{x1:mL,y1:Y(v),x2:W-mR,y2:Y(v),stroke:"#f0f0f0"},svg);});
  // x ticks: evenly spaced across the (possibly extended) range
  {const step=x1<=3?0.5:1; for(let v=Math.ceil(x0/step)*step; v<=x1+1e-9; v+=step)
    tx(svg,X(v),H-mB+13,(v%1?v.toFixed(1):v.toFixed(0)),{"font-size":9,"text-anchor":"middle",fill:"#666"});}
  // parity line
  el("line",{x1:X(1),y1:mT,x2:X(1),y2:H-mB,stroke:"#999","stroke-dasharray":"4 3"},svg);
  tx(svg,X(1)+3,mT+9,"parity",{"font-size":8,fill:"#999"});
  tx(svg,mL,mT-8,mt.name+"  ("+t+" tier)",{"font-size":9,fill:"#333","font-weight":700});
  // all four product shares vs cultivated's price ratio R_x (cultivated is the bold line)
  const LINES=[["c","conventional","#E69F00",1.3],["p","plant-based","#117733",1.3],
               ["w","whole-food","#949494",1.3],["x","cultivated","#0072B2",2.4]];
  LINES.forEach(([which,lab,col,w])=>{
    let d="";for(let i=0;i<=80;i++){const R=x0+(x1-x0)*i/80;
      d+=(i?"L":"M")+X(R).toFixed(1)+" "+Y(evW(R,which)*100).toFixed(1)+" ";}
    el("path",{d,fill:"none",stroke:col,"stroke-width":w,opacity:which==="x"?1:0.85},svg);});
  // legend doubles as a LIVE READOUT: each product's share at the marked R (so the
  // plant-based & whole-food shares are shown as numbers, not just lines)
  const lg=LINES.slice().reverse(), lbw=170;
  el("rect",{x:W-mR-lbw,y:mT-2,width:lbw-2,height:lg.length*12+16,fill:"#fff",opacity:0.86},svg);
  tx(svg,W-mR-lbw+4,mT+8,"share @ R="+Rmark.toFixed(2)+":",{"font-size":8,fill:"#888"});
  let lgy=mT+20; lg.forEach(([which,lab,col])=>{
    el("line",{x1:W-mR-lbw+4,y1:lgy-3,x2:W-mR-lbw+18,y2:lgy-3,stroke:col,"stroke-width":which==="x"?2.4:1.3},svg);
    tx(svg,W-mR-lbw+22,lgy,lab,{"font-size":8.5,fill:"#444"});
    tx(svg,W-mR-5,lgy,fmtPct(evW(Rmark,which)),{"font-size":8.5,fill:col,"text-anchor":"end","font-weight":600});
    lgy+=12;});
  // CULTIVATED marker: its share at its own R_x, on the blue curve (axis covers R_x so the dot
  // lands on the curve). Anchor the label so it never overflows the edges.
  const sh=evW(Rmark,"x");
  const mx=X(Math.max(x0,Math.min(Rmark,x1))), my=Y(sh*100);
  el("circle",{cx:mx,cy:my,r:5,fill:"#0072B2"},svg);
  const lbl="cultivated "+fmtPct(sh)+" @ Rₓ="+Rmark.toFixed(2);
  const nearR=mx>W-mR-148, nearL=mx<mL+74;                          // would overflow an edge?
  tx(svg,nearR?mx-9:(nearL?mx+9:mx),my-9,lbl,
     {"font-size":9,"font-weight":700,fill:"#0072B2","text-anchor":nearR?"end":(nearL?"start":"middle")});
  // PLANT-BASED marker: its ACTUAL operating point — its share at its OWN price R_p, on the green
  // curve (the true analogue of the cultivated dot; cultivated's R_x doesn't set PB's price).
  const shp=evW(Rp,"p");
  const px=X(Math.max(x0,Math.min(Rp,x1))), py=Y(shp*100);
  el("circle",{cx:px,cy:py,r:4,fill:"#117733"},svg);
  const plbl="plant-based "+fmtPct(shp)+" @ Rₚ="+Rp.toFixed(2);
  const pNearR=px>W-mR-150, pNearL=px<mL+78;
  tx(svg,pNearR?px-8:(pNearL?px+8:px),py+(py<my+14?16:-8),plbl,   // dodge the cultivated label if close
     {"font-size":8.5,"font-weight":700,fill:"#117733","text-anchor":pNearR?"end":(pNearL?"start":"middle")});
  txRsub(svg,(mL+W-mR)/2,H-3,"Cultivated price ratio ","x"," (lower = cheaper; plant-based fixed at its own Rₚ)",{"font-size":9,"text-anchor":"middle",fill:"#444"});
  // JS-build fingerprint, drawn by the CURVE code itself: if this matches the header stamp, the
  // JavaScript is current (not a stale cached script). Tiny, bottom-right.
  tx(svg,W-mR,mT-6,"js __BUILD_STAMP__",{"font-size":6.5,"text-anchor":"end",fill:"#ccc"});
}
/* MILK vs MEAT: the cross-category validation, depicted. Plant-based MILK (~15%) vs plant-based
   MEAT (~1%) from the SAME meat-derived coefficients (beta_ref/anchor reused), swapping only the
   product positions. Two bars + the three drivers that differ. Mirrors market_share.pb_milk_check. */
/* COMPARISON PRODUCT: the same demand machinery (reused meat-derived beta_ref + anchor) applied
   to another real-world analog category, swapping ONLY that product's positions. Mirrors
   market_share.pb_milk_check, generalised over MODEL.const.comparison_products. */
function cmpShare(pd){
  // plant-based MEAT is the model's own calibrated world (no override) — its ~1.2% target.
  if(pd.w_rt===null||pd.K_wf===null) return shareCalc(1.0,KP,{present:false,which:"pb"});
  const K=Object.assign({},effConsts(state));                       // reuse current calibrated beta/anchor
  K.price_pb_mult=pd.pb_mult; K.taste_quality_p=pd.taste; K.w_realtissue_M=pd.w_rt;
  // outside-option strength: pd.K_wf is the analog's whole-food intercept -> in the health
  // parameterisation that's a whole-food health POSITION at unit weight (health_c=0: the analog's
  // incumbent, e.g. dairy/butter, is the reference, no health penalty).
  K.price_wf_mult=pd.wf_mult; K.health_w=pd.K_wf; K.health_c=0; K.w_health_M=1; K.w_health_E=1;
  // the comparison product is a PLANT-BASED-style analog -> its novelty is the plant-based
  // dial neophobia_p (not cultivated's), since milk/margarine are plant-based products.
  // It also carries its own HEALTH-perception position (pd.health, ILLUSTRATIVE): e.g. margarine a
  // penalty (butter read as healthier), plant nuggets a small draw. Applied as the analog's hp.
  const hpd=(pd.health!==undefined?pd.health:0);
  return shareCalc(1.0,K,{present:false,which:"pb",nbp:state.neophobia_p,hp:hpd});
}
/* PANEL 4b — relative-importance breakdown: each factor's utils contribution to cultivated vs
   conventional (mainstream). Half-width, side-by-side with 4a, and driven by the SAME species
   selector (state.curveType). PER MEAT TYPE × REGION: the selected meat type sets the price ratio R
   (its LOCAL conventional price), tier (authenticity τ + elasticity multiplier), and the per-
   comparison reference price p_ref; the region sets the income that scales price-sensitivity. So the
   balance of bars is product- and region-specific (price dominates cheap chicken; for sushi price is
   a POSITIVE bar and τ_premium does the work). Uses breakdownCalc, so the bars sum to the net utility
   gap that sets the share, and every weight slider moves its bar. */
function drawBreakdown(s){
  const svg=document.getElementById("breakdown"); if(!svg||!KP) return; clear(svg);
  const xL=104, xR=412, xz=(xL+xR)/2, padTop=34, rowH=25;
  const market=MODEL.markets[s.region], bases=speciesBases(market);
  const mt=market.find(m=>m.name===s.curveType)||market[0];     // SHARED selector with panel 4a
  const b=biomass(s), rpr=(s.premium_resistance===undefined?1:s.premium_resistance);
  const {R,t}=typeR(mt,b,s.markup_add,s,bases);                 // this type's price ratio + tier
  const o={ax:s.accept_x,tfM:s.theta_free_M,toff:tAuth(t,rpr),
           eps:s.eps_own*tMult(t,rpr),income:s.income,nbx:s.neophobia_x,nbp:s.neophobia_p,
           hx:s.health_x,hp:s.health_p,pricePb:s.R_p,tasteP:(s.a_p-1),
           rtx:s.real_tissue_x,rtp:s.real_tissue_p,pRef:mt.p_conv,which:"x"};
  const bd=breakdownCalc(R,KP,"M",o);
  const blended=shareCalc(R,KP,{ax:s.accept_x,tfM:s.theta_free_M,toff:tAuth(t,rpr),
           eps:s.eps_own*tMult(t,rpr),income:s.income,nbx:s.neophobia_x,nbp:s.neophobia_p,
           hx:s.health_x,hp:s.health_p,pricePb:s.R_p,aP:s.a_p,rtx:s.real_tissue_x,rtp:s.real_tissue_p,
           pRef:mt.p_conv,which:"x"});
  const FACT=[["price","price (β)"],["taste","taste (wᵗ)"],["real_meat","real-meat (wʳᵗ)"],
              ["health","health (wʰ)"],["slaughter_free","slaughter (wˢ)"],
              ["novelty","novelty (ν)"],["authenticity","authent. (τ)"]];
  let maxA=1e-6; FACT.forEach(([k])=>maxA=Math.max(maxA,Math.abs(bd[k])));
  maxA=Math.max(maxA,Math.abs(bd._net));
  const sc=(Math.min(xz-xL,xR-xz)-30)/maxA;                     // utils -> px (leave room for value labels)
  // species/tier/R tag + the worse/better axis hint
  tx(svg,xL-2,padTop-16,s.region.toUpperCase()+" · "+mt.name,{"font-size":8.5,fill:"#999","text-anchor":"start"});
  tx(svg,xR,padTop-16,t+" · R="+R.toFixed(2),{"font-size":8.5,fill:"#999","text-anchor":"end"});
  tx(svg,xz,padTop-5,"← worse  |  better →",{"font-size":8.5,fill:"#bbb","text-anchor":"middle"});
  el("line",{x1:xz,y1:padTop,x2:xz,y2:padTop+FACT.length*rowH+2,stroke:"#ccc","stroke-width":1},svg);
  FACT.forEach(([k,lab],i)=>{
    const y=padTop+i*rowH+rowH/2, v=bd[k], w=v*sc;
    const col=Math.abs(v)<1e-9?"#bbb":(v>0?"#029E73":"#D55E00");
    el("rect",{x:Math.min(xz,xz+w),y:y-7,width:Math.max(1.2,Math.abs(w)),height:14,fill:col,opacity:0.9,rx:2},svg);
    tx(svg,xL-6,y+3,lab,{"font-size":9.5,fill:"#333","text-anchor":"end"});
    tx(svg,xz+w+(w>=0?4:-4),y+3,(v>=0?"+":"")+v.toFixed(2),
       {"font-size":9,fill:"#555","text-anchor":w>=0?"start":"end"});
  });
  // net row + resulting share
  const yN=padTop+FACT.length*rowH+16, net=bd._net;
  el("line",{x1:xL-6,y1:yN-11,x2:xR,y2:yN-11,stroke:"#eee","stroke-width":1},svg);
  tx(svg,xL-6,yN+3,"NET",{"font-size":9.5,fill:"#111","text-anchor":"end","font-weight":700});
  tx(svg,xz,yN+3,(net>=0?"+":"")+net.toFixed(2)+" utils → share "+
     (bd._share*100).toFixed(0)+"% (blend "+(blended*100).toFixed(0)+"%)",
     {"font-size":9.5,fill:"#111","text-anchor":"middle","font-weight":700});
}
function drawMilk(s){   // (id kept "milk"; now the general comparison-product chart, full width)
  const svg=document.getElementById("milk"); if(!svg) return; clear(svg);
  const W=720,H=320,mT=26,mB=44;
  const PR=C.comparison_products, names=Object.keys(PR);
  const sel=s.cmpProduct||names[0], pd=PR[sel];
  const model=cmpShare(pd)*100, obs=pd.obs;
  // LEFT HALF: model-vs-observed bars; RIGHT HALF: the positions swapped in.
  const bL=44, bR=W*0.46;                                            // bar-panel bounds
  const ymax=Math.max(20, Math.ceil(Math.max(model,obs)/10)*10);
  const Y=v=>H-mB-(H-mT-mB)*v/ymax;
  el("line",{x1:bL,y1:H-mB,x2:bR,y2:H-mB,stroke:"#ccc"},svg);
  for(let v=0;v<=ymax;v+=ymax/5){tx(svg,bL-5,Y(v)+3,Math.round(v)+"%",{"font-size":8.5,"text-anchor":"end",fill:"#666"});
    el("line",{x1:bL,y1:Y(v),x2:bR,y2:Y(v),stroke:"#f3f3f3"},svg);}
  const bars=[["model",model,"#0173B2"],["observed",obs,"#5AAE61"]];
  const bw=104, gap=(bR-bL-2*bw)/3;
  bars.forEach(([lab,v,col],i)=>{
    const x=bL+gap+i*(bw+gap);
    el("rect",{x,y:Y(v),width:bw,height:(H-mB)-Y(v),fill:col,opacity:0.85},svg);
    tx(svg,x+bw/2,Y(v)-5,v.toFixed(0)+"%",{"font-size":15,"text-anchor":"middle","font-weight":700,fill:col});
    tx(svg,x+bw/2,H-mB+14,lab,{"font-size":10,"text-anchor":"middle",fill:"#333","font-weight":600});
  });
  const ok=Math.abs(model-obs)<=Math.max(2,0.25*obs);
  // HONEST title per product-kind (mirrors the self-check tags), not a blanket "✓ reproduces":
  //   PB-meat  = the calibration TARGET (circular — the model is tuned to it, not a validation)
  //   eggs     = a DIFFERENT mechanism (welfare, not the real-tissue machinery) — a contrast probe
  //   others   = genuine OUT-OF-SAMPLE (same coefficients, only positions swapped)
  const _isMeat=(pd.w_rt===null), _isEgg=(!_isMeat && pd.w_rt===0 && (pd.health||0)>0);
  let title, tcol;
  if(_isMeat){ title="“"+sel+"” is the calibration TARGET — the model is tuned to it (not a validation)"; tcol="#888"; }
  else if(_isEgg){ title=(ok?"✓ ":"")+"“"+sel+"”: a DIFFERENT lever (welfare, not authenticity) — read as a contrast"; tcol=ok?"#0173B2":"#666"; }
  else { title=(ok?"✓ out-of-sample: model reproduces “":"model gives “")+sel+"”"+(ok?" (NOT tuned to it)":""); tcol=ok?"#0173B2":"#666"; }
  tx(svg,W/2,mT-12,title,{"font-size":10,"text-anchor":"middle",fill:tcol,"font-weight":700});  // center over FULL width (not the left bar-panel) so the long title doesn't clip off the left edge
  // RIGHT HALF: positions swapped in (same β, income, q) + the note
  const pX=W*0.52, pVal=W-18;
  let ry=mT+10;
  tx(svg,pX,ry,"the product's facts (same weights and income; only these change):",{"font-size":9,fill:"#888"}); ry+=20;
  const isMeat=(pd.w_rt===null);
  const hh=(pd.health!==undefined?pd.health:0);
  // eggs are a DIFFERENT mechanism (welfare premium, no authenticity penalty): relabel the
  // bottom two rows so they read as 'not-real penalty: none' and 'welfare draw' rather than
  // 'real-meat credit' / 'health'. Detected by w_rt≈0 with a positive offset.
  const isEgg=(!isMeat && pd.w_rt===0 && hh>0);
  const W4=(pd.why||{});   // per-value short justifications (non-calibrated rows), keyed price/taste/rival/rt/health
  const lastTwo = isEgg
    ? [["‘not real’ penalty", "none (an egg is an egg)", W4.rt],
       ["welfare draw", "+"+hh.toFixed(1)+" (ethical pull)", W4.health]]
    : [["real-meat credit (w)", isMeat?"calibrated":(pd.w_rt).toFixed(1), W4.rt],
       ["health perception (ζ)", (isMeat?"0 (neutral)":(hh>0?"+"+hh.toFixed(1)+" (draw)":(hh<0?hh.toFixed(1)+" (penalty)":"0 (neutral)"))), W4.health]];
  const pos=[["price vs incumbent", (pd.pb_mult).toFixed(2)+"×", W4.price],
             ["taste vs the real thing", isMeat?"−0.2 (deficit)":(pd.taste===0?"~parity":pd.taste.toFixed(1)), W4.taste],
             ["cheap substitute rival", (isMeat?"strong (beans)":(pd.wf_mult>=1?"weak":"present")), W4.rival],
             lastTwo[0], lastTwo[1]];
  // each row: label + value on one line, then (if a why-comment exists) a small grey justification
  // WRAPPED to as many lines as it needs within the panel width (SVG text doesn't auto-wrap).
  const whyW=pVal-(pX+10);                                            // px available for the why-line
  pos.forEach(([d,v,why])=>{tx(svg,pX+4,ry,d,{"font-size":10,fill:"#555"});
    tx(svg,pVal,ry,v,{"font-size":10,fill:"#222","text-anchor":"end","font-weight":600}); ry+=13;
    if(why){ry=txWrap(svg,pX+10,ry,"— "+why,whyW,{"font-size":8,fill:"#999"},10); ry+=1;}
    el("line",{x1:pX+4,y1:ry-3,x2:pVal,y2:ry-3,stroke:"#f0f0f0"},svg); ry+=7;});
  ry+=4; ry=txWrap(svg,pX,ry,pd.note,pVal-pX,{"font-size":8.5,fill:"#999"},11);
  ry+=12; tx(svg,pX,ry,"→ same shopper model, different product: a test outside meat.",
     {"font-size":8.5,fill:"#0173B2","font-style":"italic"});
  // grow the viewBox to fit the (now variable-height, wrapped) right-hand column
  svg.setAttribute("viewBox","0 0 "+W+" "+Math.max(H, ry+14));
}
/* TIMING chart: adoption over time at the headline commodity R. Shows the median realized
   share, the 80% band (sweeping all timing+acceptance priors), the rising ceiling (cold-start
   neophobia fading to long-run), and the median year-to-stabilise. */
function drawTiming(s){
  const svg=document.getElementById("timing"); if(!svg) return; clear(svg);
  const W=720,H=300,mL=42,mR=148,mT=18,mB=38, yrs=MODEL.years||30;
  const Rx=basicR(s); s._Rtiming=Rx;                                  // cultivated's commodity price ratio
  // CULTIVATED trajectory: cold-start nu_x0 -> long-run nu_x
  const cx=bassTrajectory({R:Rx,nb0:s.neophobia_x0,nbL:s.neophobia_x,rate:s.accept_rate,
    p:s.p_innov,q:s.q_imit,ax:s.accept_x,tfM:s.theta_free_M,income:s.income,which:"x"});
  // PLANT-BASED trajectory: same machinery, its OWN price R_p and cold-start nu_p0 -> nu_p.
  // PB STALLS because its taste deficit (a_p<1) + price premium cap the ceiling even after novelty fades.
  const cp=bassTrajectory({R:s.R_p,nb0:s.neophobia_p0,nbL:s.neophobia_p,rate:s.accept_rate,   // the slider (was the constant)
    p:s.p_innov,q:s.q_imit,aP:s.a_p,income:s.income,which:"pb"});
  const xShare=cx.share.map(v=>v*100), xCeil=cx.ceiling.map(v=>v*100), pShare=cp.share.map(v=>v*100);
  const pCeil=cp.ceiling.map(v=>v*100);                  // plant-based ceiling (for y-scaling)
  const band=s.mc?trajectoryMC(s,500,"x"):null;          // cultivated band
  const bandP=s.mc?trajectoryMC(s,500,"pb"):null;        // plant-based band (EQUAL FOOTING)
  // y-axis must fit EVERY drawn series — cultivated AND plant-based, realized + ceiling + bands —
  // because plant-based can exceed the cultivated ceiling (e.g. a skeptic on cultivated + a
  // believer on plant-based: PB ~13% vs cultivated ceiling ~0%). Scaling to cultivated alone clips it.
  const ymax=Math.max(10, Math.ceil(Math.max(...xCeil, ...xShare, ...pShare, ...pCeil,
    band?Math.max(...band.p90):0, bandP?Math.max(...bandP.p90):0)/10)*10);
  const X=k=>mL+(W-mL-mR)*k/yrs, Y=v=>H-mB-(H-mT-mB)*v/ymax;
  el("line",{x1:mL,y1:H-mB,x2:W-mR,y2:H-mB,stroke:"#ccc"},svg);
  for(let v=0;v<=ymax;v+=ymax/5){tx(svg,mL-5,Y(v)+3,Math.round(v),{"font-size":9,"text-anchor":"end",fill:"#666"});
    el("line",{x1:mL,y1:Y(v),x2:W-mR,y2:Y(v),stroke:"#f3f3f3"},svg);}
  [0,5,10,15,20,25,30].filter(k=>k<=yrs).forEach(k=>tx(svg,X(k),H-mB+13,k,{"font-size":9,"text-anchor":"middle",fill:"#666"}));
  // plant-based 80% band (EQUAL FOOTING with cultivated) — green, drawn first/underneath
  if(bandP){let d="M";for(let k=0;k<=yrs;k++)d+=X(k).toFixed(1)+" "+Y(bandP.p90[k]).toFixed(1)+" L";
    for(let k=yrs;k>=0;k--)d+=X(k).toFixed(1)+" "+Y(bandP.p10[k]).toFixed(1)+" L";d=d.slice(0,-2)+"Z";
    el("path",{d,fill:"#117733",opacity:0.12},svg);}
  // cultivated 80% band
  if(band){let d="M";for(let k=0;k<=yrs;k++)d+=X(k).toFixed(1)+" "+Y(band.p90[k]).toFixed(1)+" L";
    for(let k=yrs;k>=0;k--)d+=X(k).toFixed(1)+" "+Y(band.p10[k]).toFixed(1)+" L";d=d.slice(0,-2)+"Z";
    el("path",{d,fill:"#0173B2",opacity:0.12},svg);}
  // cultivated ceiling (dashed)
  let dc="";for(let k=0;k<=yrs;k++)dc+=(k?"L":"M")+X(k).toFixed(1)+" "+Y(xCeil[k]).toFixed(1)+" ";
  el("path",{d:dc,fill:"none",stroke:"#7fb2d6","stroke-width":1.1,"stroke-dasharray":"5 3"},svg);
  // PLANT-BASED realized (the stalled contrast) — green, the PB colour used elsewhere
  let dp="";for(let k=0;k<=yrs;k++)dp+=(k?"L":"M")+X(k).toFixed(1)+" "+Y(pShare[k]).toFixed(1)+" ";
  el("path",{d:dp,fill:"none",stroke:"#117733","stroke-width":2.0},svg);
  // CULTIVATED realized (bold blue)
  let ds="";for(let k=0;k<=yrs;k++)ds+=(k?"L":"M")+X(k).toFixed(1)+" "+Y(xShare[k]).toFixed(1)+" ";
  el("path",{d:ds,fill:"none",stroke:"#0173B2","stroke-width":2.6},svg);
  // stabilisation marker (cultivated)
  const ts=band?pctl(band.tstab,50):timeToStabilize(xShare);
  el("line",{x1:X(ts),y1:mT,x2:X(ts),y2:H-mB,stroke:"#999","stroke-dasharray":"2 2","stroke-width":1},svg);
  tx(svg,X(ts)-4,mT+10,"cultivated stabilises ~yr "+Math.round(ts),{"font-size":8,fill:"#777","text-anchor":"end"});
  tx(svg,mL,mT-4,"cultivated "+xShare[0].toFixed(0)+"%→"+xShare[yrs].toFixed(0)+"%   ·   plant-based "+pShare[0].toFixed(0)+"%→"+pShare[yrs].toFixed(0)+"%",
     {"font-size":9,fill:"#333","font-weight":700});
  // right-side legend
  let ly=mT+8;
  [["#0173B2","cultivated",2.6],["#117733","plant-based",2.0],
   ["#7fb2d6","cultivated ceiling",1.1],["#0173B2","cultivated 80% band"+(band?"":" — MC off"),0],
   ["#117733","plant-based 80% band",0]].forEach(([c,lab,w])=>{
    if(w)el("line",{x1:W-mR+6,y1:ly-3,x2:W-mR+22,y2:ly-3,stroke:c,"stroke-width":w,"stroke-dasharray":w===1.1?"5 3":""},svg);
    else el("rect",{x:W-mR+6,y:ly-7,width:16,height:7,fill:c,opacity:0.12},svg);
    tx(svg,W-mR+26,ly,lab,{"font-size":8,fill:"#555"}); ly+=13;});
  ly+=4;
  tx(svg,W-mR+6,ly,"what caps PB:",{"font-size":8,fill:"#888"}); ly+=11;
  tx(svg,W-mR+6,ly,"taste a_p="+(s.a_p).toFixed(2)+", R_p="+(s.R_p).toFixed(2),{"font-size":8,fill:"#117733"}); ly+=11;
  tx(svg,W-mR+6,ly,"(novelty fades; taste",{"font-size":8,fill:"#999"}); ly+=10;
  tx(svg,W-mR+6,ly,"deficit is permanent)",{"font-size":8,fill:"#999"}); ly+=14;
  if(band){tx(svg,W-mR+6,ly,"cult yr-"+yrs+": P50 "+pctl(band.finals,50).toFixed(0)+"%",{"font-size":8.5,fill:"#0173B2"});
    ly+=11; tx(svg,W-mR+6,ly,"["+pctl(band.finals,10).toFixed(0)+"–"+pctl(band.finals,90).toFixed(0)+"]",{"font-size":8.5,fill:"#0173B2"});ly+=13;}
  if(bandP){tx(svg,W-mR+6,ly,"PB yr-"+yrs+": P50 "+pctl(bandP.finals,50).toFixed(0)+"%",{"font-size":8.5,fill:"#117733"});
    ly+=11; tx(svg,W-mR+6,ly,"["+pctl(bandP.finals,10).toFixed(0)+"–"+pctl(bandP.finals,90).toFixed(0)+"]",{"font-size":8.5,fill:"#117733"});}
  tx(svg,(mL+W-mR)/2,H-3,"Years since launch",{"font-size":9,"text-anchor":"middle",fill:"#444"});
}
function fillCurveSel(){
  const sel=document.getElementById("curveSel"), market=MODEL.markets[state.region];
  const bases=speciesBases(market);
  // every form, including the premium SKUs (each labelled with its tier)
  const forms=market;
  // default to a beef cut: an informative mid-range case (chicken mince, the first row, sits near 0% everywhere)
  if(!forms.find(m=>m.name===state.curveType))
    state.curveType=(forms.find(m=>m.name.startsWith("beef (steak"))||forms.find(m=>m.name.startsWith("beef"))||forms[0]).name;
  sel.innerHTML="";
  forms.forEach(mt=>{const o=document.createElement("option");o.value=mt.name;
    o.textContent=mt.name+" ("+tierOf(mt,bases[animalOf(mt.name)])+")";sel.appendChild(o);});
  sel.value=state.curveType;
  sel.onchange=()=>{state.curveType=sel.value;recompute();};
}
function fillCmpSel(){
  const sel=document.getElementById("cmpSel"); if(!sel) return;
  const names=Object.keys(C.comparison_products);
  if(!state.cmpProduct||names.indexOf(state.cmpProduct)<0) state.cmpProduct=names[0];
  sel.innerHTML="";
  names.forEach(n=>{const o=document.createElement("option");o.value=n;o.textContent=n;sel.appendChild(o);});
  sel.value=state.cmpProduct;
  sel.onchange=()=>{state.cmpProduct=sel.value;recompute();};
}

/* ---------- FOOTHOLD: the reachability waterline (foothold.py strategic layer) ----------
   Cultivated retail cost = a waterline set by the live cost sliders (medium/overhead/markup/scaffold),
   via the SAME stack as the cost chart. Products are islands at their conventional price; above the
   line = price-reachable (R<1). Two reference lines: the current sea and the irreducible-floor sea. */
function footRetail(s,structured){return biomass(s)+(structured?s.scaffold:0)+s.markup_add;}
function footFloor(s,structured){return C.cost_floor+(structured?s.scaffold:0)+s.markup_add;}
function footR(s,pd){return footRetail(s,pd.structure==="structured")/pd.p_base;}   // vs the ACCESSIBLE price (rent stripped)
function footHasRent(p){return p.p_base!=null && p.p_conv!=null && p.p_base<p.p_conv;}   // a distinct, cheaper accessible tier exists
function footPhi(p){return footHasRent(p) ? (state.phi===undefined?0.25:state.phi) : 0;}  // global prestige share φ where a rent tier exists
function footAddr(p){return (1-footPhi(p))*p.volume_kt;}                              // addressable base (prestige core removed)
function footDisplace(s,p){return footShare(s,p)*footAddr(p);}  // conventional volume DISPLACED (kt/yr) = break-even share × addressable. The rung's impact metric — NO margin/profit claim: cultivated is assumed to price at its own cost (0% margin), since cost, price and volume are too coupled to pin a credible $-figure.
function footReach(s,p){   // reachability zone at the accessible price, with a ±$3 "at parity" band so
  const structured=p.structure==="structured";   // knife-edge products (salmon vs unagi) don't look categorical
  const cost=footRetail(s,structured), fl=footFloor(s,structured), b=p.p_base;
  if(Math.abs(b-cost)<=3) return {zone:"par",  col:"#56B4E9"};   // borderline / essentially at parity
  if(b>=cost)             return {zone:"now",  col:"#117733"};
  if(b>=fl)               return {zone:"floor",col:"#E69F00"};
  return {zone:"never", col:"#BBBBBB"};
}
function fillFootholdSel(){
  const sel=document.getElementById("footSel"); if(!sel) return;
  const P=C.foothold_products;
  if(state.footSel===undefined||state.footSel<0||state.footSel>=P.length) state.footSel=0;
  sel.innerHTML="";
  P.forEach((p,i)=>{const o=document.createElement("option");o.value=i;o.textContent="drill into: "+p.label;sel.appendChild(o);});
  sel.value=state.footSel;
  sel.onchange=()=>{state.footSel=parseInt(sel.value);drawFoothold(state);};
}
function drawFoothold(s){
  const svg=document.getElementById("foothold"); if(!svg) return; clear(svg);
  const ft=document.getElementById("foottip"); if(ft) ft.style.display="none";   // hide stale tooltip on redraw
  if(state.footView==="margin") drawFootResponse(s,svg); else drawFootWaterline(s,svg);
  footCaption(s);
}
function drawFootWaterline(s,svg){
  const W=720,H=380,mL=52,mR=156,mT=22,mB=84;
  const P=C.foothold_products.slice().sort((a,b)=>b.p_base-a.p_base);   // by the ACCESSIBLE price cultivated competes at
  const selLabel=(C.foothold_products[state.footSel]||{}).label;        // highlight by identity (P is re-sorted)
  const n=P.length, yLo=6, yHi=2600;
  const Y=v=>H-mB-(H-mT-mB)*(Math.log(Math.max(v,yLo))-Math.log(yLo))/(Math.log(yHi)-Math.log(yLo));
  const X=i=>mL+(W-mL-mR)*(i+0.5)/n;
  [10,30,100,300,1000,2500].forEach(v=>{el("line",{x1:mL,y1:Y(v),x2:W-mR,y2:Y(v),stroke:"#f2f2f2"},svg);
    tx(svg,mL-6,Y(v)+3,"$"+v,{"font-size":8.5,"text-anchor":"end",fill:"#888"});});
  const seaU=footRetail(s,false), seaS=footRetail(s,true), floorU=footFloor(s,false), floorS=footFloor(s,true);
  // underwater shading (below the lower, unstructured cost) + the cost BAND (unstructured edge -> +scaffold
  // edge) so STRUCTURED products' stems land on a visible line, not in mid-air.
  el("rect",{x:mL,y:Y(seaU),width:W-mL-mR,height:(H-mB)-Y(seaU),fill:"#0072B2",opacity:0.05},svg);
  el("rect",{x:mL,y:Y(seaS),width:W-mL-mR,height:Y(seaU)-Y(seaS),fill:"#0072B2",opacity:0.12},svg);
  el("line",{x1:mL,y1:Y(seaU),x2:W-mR,y2:Y(seaU),stroke:"#0072B2","stroke-width":1.8},svg);
  el("line",{x1:mL,y1:Y(seaS),x2:W-mR,y2:Y(seaS),stroke:"#0072B2","stroke-width":1.1,"stroke-dasharray":"5 2"},svg);
  tx(svg,W-mR+4,Y(seaS)-1,"+scaffold $"+seaS.toFixed(0),{"font-size":8,fill:"#0072B2"});
  tx(svg,W-mR+4,Y(seaU)+9,"cult. cost $"+seaU.toFixed(0),{"font-size":8,fill:"#0072B2","font-weight":700});
  el("line",{x1:mL,y1:Y(floorU),x2:W-mR,y2:Y(floorU),stroke:"#0072B2","stroke-width":1,"stroke-dasharray":"2 3",opacity:0.6},svg);
  tx(svg,W-mR+4,Y(floorU)+3,"floor $"+floorU.toFixed(0),{"font-size":8,fill:"#0072B2",opacity:0.8});
  P.forEach((p,i)=>{
    const structured=p.structure==="structured";
    const cost=structured?seaS:seaU, fl=structured?floorS:floorU;
    const rc=footReach(s,p), reach=rc.zone, col=rc.col;
    const r=footRad(footDisplace(s,p)), x=X(i), y=Y(p.p_base);
    // prestige core (rent cultivated can't capture): faint marker at the headline price, dotted down to the base
    if(p.p_conv>p.p_base*1.05){const yp=Y(p.p_conv), rent=p.p_conv-p.p_base;
      el("line",{x1:x,y1:yp,x2:x,y2:y,stroke:"#CCC","stroke-width":1,"stroke-dasharray":"1 3"},svg);
      tip(el("circle",{cx:x,cy:yp,r:3,fill:"#CCC"},svg),
        p.label+"\nheadline (sticker) price $"+p.p_conv+"/kg — the premium/prestige tier"
        +"\ncultivated competes $"+rent+"/kg lower, at $"+p.p_base+"/kg (the accessible tier)"
        +"\nthe gap = brand/scarcity RENT cultivated can't capture (it isn't the authentic thing)");
      if(p.label===selLabel) tx(svg,x+5,(yp+y)/2+3,"rent $"+rent,{"font-size":8,fill:"#999","font-style":"italic"});}
    // the vertical bar is the cost→accessible-price gap (reachability headroom): solid up when reachable, dotted-grey deficit
    if(reach!=="never") el("line",{x1:x,y1:Y(cost),x2:x,y2:y,stroke:col,"stroke-width":2.2,opacity:0.6},svg);
    else el("line",{x1:x,y1:Y(cost),x2:x,y2:y,stroke:"#CCC","stroke-width":1,"stroke-dasharray":"2 2"},svg);
    tip(el("circle",{cx:x,cy:y,r,fill:col,opacity:0.9,stroke:"#fff","stroke-width":1},svg),footTip(s,p));
    if(p.launched_by) el("circle",{cx:x,cy:y,r:r+3,fill:"none",stroke:"#333","stroke-width":1,opacity:0.7},svg);
    if(p.label===selLabel){el("circle",{cx:x,cy:y,r:r+6,fill:"none",stroke:"#CC3311","stroke-width":1.6},svg);
      tx(svg,x+5,(Y(cost)+y)/2+3,"R="+footR(s,p).toFixed(2),{"font-size":9,fill:"#CC3311","font-weight":700});}
    const short=p.label.replace("cultivated ","").replace(/ \(.*\)/,"");
    tx(svg,x,H-mB+12,short,{"font-size":7.5,"text-anchor":"end",fill:"#444",transform:"rotate(-42 "+x+" "+(H-mB+12)+")"});
  });
  el("line",{x1:mL,y1:H-mB,x2:W-mR,y2:H-mB,stroke:"#ccc"},svg);
  tx(svg,(mL+W-mR)/2,H-3,"islands at the ACCESSIBLE price (grey tick = headline price = rent)   ·   bar = cost→price gap (reachability)   ·   dot = displaceable volume",
    {"font-size":8,"text-anchor":"middle",fill:"#666"});
  [["#117733","reachable now"],["#56B4E9","at parity (±$3)"],["#E69F00","needs the floor"],["#BBBBBB","never on price"]].forEach(([c,t],k)=>{
    el("circle",{cx:W-mR+8,cy:mT+8+k*14,r:4,fill:c},svg);tx(svg,W-mR+16,mT+11+k*14,t,{"font-size":8,fill:"#555"});});
  const _ky=mT+8+4*14;   // the grey tick above each island = the headline (rent) price cultivated can't capture
  el("circle",{cx:W-mR+8,cy:_ky-3,r:2.5,fill:"#CCC"},svg);
  el("line",{x1:W-mR+8,y1:_ky,x2:W-mR+8,y2:_ky+8,stroke:"#CCC","stroke-dasharray":"1 2"},svg);
  tx(svg,W-mR+16,_ky+1,"headline price (rent,",{"font-size":8,fill:"#555"});
  tx(svg,W-mR+16,_ky+10,"unaddressable)",{"font-size":8,fill:"#555"});
  footSizeKey(svg,W-mR+16,W-mR+38,mT+8+5*14+16);           // quantified volume legend
}
/* per-product PREDICTED SHARE via the demand model (shareCalc), live to the acceptance/price sliders.
   NO new foothold parameter: it is the IDENTICAL Step-2 logit panel 1 uses, with the SAME per-tier
   authenticity offset (tAuth) and elasticity multiplier (tMult). The accessible tier cultivated competes
   at is BASIC (unstructured/processed, +0.2 everyday pull) or CUT (structured, −0.4 "want the real cut");
   the PREMIUM tier is the prestige core, already removed as volume via φ — so authenticity is counted
   ONCE (premium grade → volume; accessible grade → its calibrated basic/cut taste), never double. This
   makes a commodity foothold product reproduce panel 1's basic-tier share exactly. See appendix A6. */
function footShare(s,pd){   // share of the ADDRESSABLE base = Step 2's calibrated logit at the accessible price.
  if(pd.p_base==null) return 0;
  const K=KP||effConsts(s), r=(s.premium_resistance===undefined?1:s.premium_resistance);
  const tier=(pd.structure==="structured")?"cut":"basic";   // premium = the φ-removed prestige core, not an offset here
  return shareCalc(footR(s,pd),K,{ax:s.accept_x,tfM:s.theta_free_M,toff:tAuth(tier,r),
    eps:s.eps_own*tMult(tier,r),income:s.income,pricePb:s.R_p,aP:s.a_p,nbx:s.neophobia_x,nbp:s.neophobia_p,pRef:pd.p_base});
}
function footRad(v){return 3+2.6*Math.log10(Math.max(v,0.2)+1);}   // bubble radius ~ log volume (impact)
function tip(elem,text){   // instant custom hover tooltip (native SVG <title> is slow/finicky)
  elem.style.cursor="pointer";
  elem.addEventListener("mouseenter",()=>{const t=document.getElementById("foottip");if(t){t.textContent=text;t.style.display="block";}});
  elem.addEventListener("mousemove",e=>{const t=document.getElementById("foottip");if(t){t.style.left=(e.clientX+14)+"px";t.style.top=(e.clientY+14)+"px";}});
  elem.addEventListener("mouseleave",()=>{const t=document.getElementById("foottip");if(t)t.style.display="none";});
  return elem;}
function footEdge(p){   // plain-language: the capturable advantage + how much of the market is unaddressable rent
  const lvl=v=>v>=2?"strong":(v>=1?"moderate":"no");
  const mx=Math.max(p.defect_ethics,p.defect_env,p.defect_health);
  const which=[["welfare",p.defect_ethics],["sustainability",p.defect_env],["health/safety",p.defect_health]]
    .filter(a=>a[1]===mx&&mx>0).map(a=>a[0]).join(" & ");
  const adv=mx>0?lvl(mx)+" "+which+" advantage":"no clear attribute advantage";
  const rent=footPhi(p)>0?Math.round(100*footPhi(p))+"% of the market is prestige rent (cultivated can't capture it)":
             "no prestige rent (cultivated competes at the full price)";
  return adv+"; "+rent;
}
function footTip(s,p){                  // hover card — short sentences + blank-line grouping (white-space:pre-line) for scannability
  const structured=p.structure==="structured", R=footR(s,p), cost=footRetail(s,structured);
  const disp=footDisplace(s,p), sh=(100*footShare(s,p)).toFixed(0);
  const dispTxt=disp>=1000?(disp/1000).toFixed(1)+" Mt/yr":disp.toFixed(0)+" kt/yr";
  const addrTxt=footAddr(p).toLocaleString(undefined,{maximumFractionDigits:0})+" kt/yr";
  const compete=(p.p_conv>p.p_base*1.05)
    ? "Competes at the $"+p.p_base+"/kg accessible grade — the $"+p.p_conv+" headline is prestige rent it can't capture."
    : "Competes at the $"+p.p_base+"/kg grade (single grade, no prestige rent).";
  // cultivated's price = its cost (the price the share is read at); R compares that to the accessible grade.
  const vsGrade=R<1
    ? "undercuts the $"+p.p_base+" grade (R = "+R.toFixed(2)+"), winning"
    : "sits "+(100*(R-1)).toFixed(0)+"% above the $"+p.p_base+" grade (R = "+R.toFixed(2)+"), yet still wins";
  const priceLine="At its cost (≈$"+cost.toFixed(0)+"/kg) it "+vsGrade+" ≈"+sh+"% of the addressable base.";
  const core=footPhi(p)>0?" ("+Math.round(100*footPhi(p))+"% prestige core removed)":"";
  const impact="That base is "+addrTxt+core+", so it displaces ≈"+dispTxt+" of conventional product.";
  const foot="edge: "+footEdge(p).split(";")[0]+(p.launched_by?"  ·  led by "+p.launched_by:"");
  return p.label+"  ·  "+(structured?"whole-cut":"processed")
    +"\n\n"+compete
    +"\n\n"+priceLine
    +"\n\n"+impact
    +"\n\n"+foot
    +"\nprice basis: "+p.source;
}
function footSizeKey(svg,cx,labx,yTop){                            // quantified bubble-size legend (reference volumes)
  tx(svg,cx-12,yTop,"bubble = displaceable volume (share × addressable, kt/yr, log):",{"font-size":7.5,fill:"#999"});
  [[1000,"1,000"],[100,"100"],[10,"10"]].forEach(([v,lab],k)=>{
    const cy=yTop+22+k*28;
    el("circle",{cx,cy,r:footRad(v),fill:"none",stroke:"#999"},svg);
    tx(svg,labx,cy+3,lab+" kt",{"font-size":7.5,fill:"#777"});});
}
function drawFootResponse(s,svg){   // demand RESPONSE: share (dependent → y) vs price ratio R (x); the SELECTED product's curve
  const W=720,H=380,mL=58,mR=150,mT=26,mB=54;
  const P=C.foothold_products, sel=C.foothold_products[state.footSel]||P[0], selLabel=sel?sel.label:"";
  const rLo=0.05, rHi=5, yLo=0, yHi=100;
  const X=v=>mL+(W-mL-mR)*(Math.log(Math.max(v,rLo))-Math.log(rLo))/(Math.log(rHi)-Math.log(rLo));
  const Y=v=>mT+(H-mT-mB)*(yHi-Math.max(yLo,Math.min(yHi,v)))/(yHi-yLo);
  [0,20,40,60,80,100].forEach(v=>{el("line",{x1:mL,y1:Y(v),x2:W-mR,y2:Y(v),stroke:"#f2f2f2"},svg);
    tx(svg,mL-6,Y(v)+3,v+"%",{"font-size":8,"text-anchor":"end",fill:"#aaa"});});
  [0.1,0.3,1,3].forEach(v=>{el("line",{x1:X(v),y1:mT,x2:X(v),y2:H-mB,stroke:v===1?"#bbb":"#f2f2f2","stroke-width":v===1?1.3:1},svg);
    tx(svg,X(v),H-mB+13,v===1?"R=1 (parity)":("R="+v),{"font-size":8,"text-anchor":"middle",fill:v===1?"#666":"#aaa"});});
  tx(svg,mL+4,Y(34),"share saturates < 100%: once cheap vs income, price stops mattering (BLP) — rivals' attributes hold the rest",
    {"font-size":7,fill:"#bbb"});
  P.forEach(p=>{
    if(p.p_base==null) return;
    const R=footR(s,p), sh=100*footShare(s,p), rc=footReach(s,p);
    const r=footRad(footDisplace(s,p)), x=X(R), y=Y(sh);
    tip(el("circle",{cx:x,cy:y,r,fill:rc.col,opacity:0.5,stroke:rc.col,"stroke-width":1.2},svg),footTip(s,p));
    if(p.launched_by) el("circle",{cx:x,cy:y,r:r+3,fill:"none",stroke:"#333","stroke-width":1,opacity:0.7},svg);
    if(p.label===selLabel){el("circle",{cx:x,cy:y,r:r+6,fill:"none",stroke:"#CC3311","stroke-width":1.8},svg);
      tx(svg,x,y-r-6,selLabel.replace("cultivated ",""),{"font-size":8.5,"text-anchor":"middle",fill:"#CC3311","font-weight":700});}
  });
  tx(svg,(mL+W-mR)/2,H-3,"price ratio R = cultivated price ÷ accessible conventional price  (log; R<1 = cheaper)  ·  hover any bubble for its name",
    {"font-size":8.5,"text-anchor":"middle",fill:"#666"});
  tx(svg,15,(mT+H-mB)/2,"predicted market share (%) — the dependent variable",{"font-size":8.5,"text-anchor":"middle",fill:"#666",transform:"rotate(-90 15 "+((mT+H-mB)/2)+")"});
  footSizeKey(svg,W-mR+18,W-mR+40,mT+22);   // quantified volume legend (top-right)
}
function footCaption(s){
  const pd=C.foothold_products[state.footSel]; if(!pd) return;
  const structured=pd.structure==="structured", R=footR(s,pd);
  const zone=R<1?"already cheaper":(pd.p_base>=footFloor(s,structured)?"cheaper only at the cost floor":"not even at the floor");
  const disp=footDisplace(s,pd), dispTxt=disp>=1000?(disp/1000).toFixed(1)+" Mt/yr":disp.toFixed(0)+" kt/yr";
  // one line of key numbers; the price basis and notes live in the bubble's hover card (footTip)
  document.getElementById("footcap").innerHTML=
    "<b>"+pd.label.replace("cultivated ","")+"</b>: R = "+R.toFixed(2)+" ("+zone+") · ~"+(100*footShare(s,pd)).toFixed(0)+
    "% of the reachable market · displaces ~"+dispTxt+(pd.launched_by?" · led by "+pd.launched_by:"")+
    ". <span style='color:#888'>Hover a bubble for the price basis.</span>";
}

/* ---------- Monte Carlo (mirror of meat_market.monte_carlo) ---------- */
// Seeded PRNG (mulberry32) so the uncertainty bands are REPRODUCIBLE run-to-run, mirroring the
// Python MCs (which use np.random.default_rng(0)) instead of jittering on every redraw. Each band
// entry point calls _seedRng() first, so the same sliders always yield the same band.
let _rngState = 0x9e3779b9;
function _seedRng(seed){_rngState = (seed>>>0) || 1;}
function _rand(){ _rngState |= 0; _rngState = (_rngState + 0x6D2B79F5) | 0;
  let t = Math.imul(_rngState ^ (_rngState >>> 15), 1 | _rngState);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }
function triang(lo,mode,hi){const u=_rand(),c=(mode-lo)/(hi-lo);
  return u<c?lo+Math.sqrt(u*(hi-lo)*(mode-lo)):hi-Math.sqrt((1-u)*(hi-lo)*(hi-mode));}
function pctl(sorted,q){const i=(sorted.length-1)*q/100,lo=Math.floor(i),hi=Math.ceil(i);
  return sorted[lo]+(sorted[hi]-sorted[lo])*(i-lo);}
// One Monte-Carlo draw: a triangular sample of every input in `keys`. The lists (C.mc_inputs,
// C.mc_timing_inputs) are injected from inputs.MC_* — the SAME sets the Python bands sample — so the
// page's bands and the numbers quoted in RESULTS.md cannot sweep different uncertainties.
function mcDraw(keys){const d={};for(const k of keys)d[k]=triang.apply(null,C.priors[k]);return d;}
// cultivated's shareCalc options for one draw of C.mc_inputs, for meat type mt (tier t). Same options
// as penetration()'s point estimate, including pRef = this cut's own price (the income log needs the
// dollar price of the rival it faces; before this helper the bands priced every cut at the $12 anchor).
function mcShareOpts(dr,mt,t,s){return {ax:dr.accept_x,tfM:dr.theta_free_M,toff:tAuth(t,dr.premium_resistance),
  eps:dr.eps_own*tMult(t,dr.premium_resistance),income:s.income,pricePb:s.R_p,aP:s.a_p,
  nbx:dr.neophobia_x,nbp:s.neophobia_p,hx:dr.health_x,pRef:mt.p_conv};}
function monteCarlo(s,N){
  // bands TOTAL penetration for BOTH novel meats on equal footing: cultivated (samples C.mc_inputs:
  // cost, acceptance, elasticity, long-run novelty, health, premium resistance) and plant-based (also
  // its own a_p, ν_p, health_p; PB has no cost stack, its price is the R_p slider). Returns vol/val
  // for cultivated and pvol/pval for plant-based.
  const P=C.priors, market=MODEL.markets[s.region], bases=speciesBases(market);
  let Wval=0, Wvol=0; market.forEach(mt=>{Wval+=mt.p_conv*mt.w_vol; Wvol+=mt.w_vol;});
  _seedRng(3);                      // reproducible penetration band (mirrors np seed=0)
  const vol=new Array(N), val=new Array(N), pvol=new Array(N), pval=new Array(N);
  for(let d=0;d<N;d++){
    const dr=mcDraw(C.mc_inputs);
    // plant-based draws (its own priors, equal footing)
    const aps=triang.apply(null,P.a_p), nbps=triang.apply(null,P.neophobia_p), hps=triang.apply(null,P.health_p);
    const b=mediaCost(dr.media_price,dr.efficiency)+dr.overhead+(s.cleanroom?C.cleanroom_cost:0);
    let tv=0,tval=0,tpv=0,tpval=0;
    for(const mt of market){
      const {R,t}=typeR(mt,b,dr.markup_add,s,bases);
      const o=mcShareOpts(dr,mt,t,s);
      const sh=shareCalc(R,KP,o);
      // plant-based share of this type, in the SAME sampled world (same cultivated draw), with PB's
      // own sampled positions.
      const shp=shareCalc(R,KP,Object.assign({},o,{aP:aps,nbp:nbps,hp:hps,which:"p"}));
      tv+=mt.w_vol/Wvol*sh; tval+=(mt.p_conv*mt.w_vol/Wval)*sh;
      tpv+=mt.w_vol/Wvol*shp; tpval+=(mt.p_conv*mt.w_vol/Wval)*shp;
    }
    vol[d]=tv*100; val[d]=tval*100; pvol[d]=tpv*100; pval[d]=tpval*100;
  }
  return {vol,val,pvol,pval};
}
/* per-TYPE Monte-Carlo: P10/P50/P90 share for each product, for the error bars on the per-type
   chart. Bands BOTH cultivated (.x) and plant-based (.p) on equal footing. Keyed by meat-type. */
function perTypeMC(s,N){
  const P=C.priors, market=MODEL.markets[s.region], bases=speciesBases(market);
  const acc={}, accP={}; market.forEach(mt=>{acc[mt.name]=new Array(N);accP[mt.name]=new Array(N);});
  _seedRng(4);                      // reproducible per-type error bars
  for(let d=0;d<N;d++){
    const dr=mcDraw(C.mc_inputs),
      aps=triang.apply(null,P.a_p), nbps=triang.apply(null,P.neophobia_p), hps=triang.apply(null,P.health_p);
    const b=mediaCost(dr.media_price,dr.efficiency)+dr.overhead+(s.cleanroom?C.cleanroom_cost:0);
    for(const mt of market){
      const {R,t}=typeR(mt,b,dr.markup_add,s,bases);
      const o=mcShareOpts(dr,mt,t,s);
      acc[mt.name][d]=shareCalc(R,KP,o);
      accP[mt.name][d]=shareCalc(R,KP,Object.assign({},o,{aP:aps,nbp:nbps,hp:hps,which:"p"}));
    }
  }
  const out={};
  for(const k in acc){const a=acc[k].sort((x,y)=>x-y), ap=accP[k].sort((x,y)=>x-y);
    out[k]={p10:pctl(a,10),p50:pctl(a,50),p90:pctl(a,90),
            pp10:pctl(ap,10),pp50:pctl(ap,50),pp90:pctl(ap,90)};}
  return out;
}
function drawMC(s){
  const card=document.getElementById("mccard");
  if(!state.mc){card.style.display="none";return;}
  card.style.display="";
  const mc=monteCarlo(s,2000);
  const svg=document.getElementById("mc");clear(svg);
  const W=720,H=250,mL=24,mR=14,mT=40,mB=34;
  // x-axis covers BOTH products' volume distributions + cultivated value (so PB's band fits too)
  const all=mc.vol.concat(mc.val).concat(mc.pvol).sort((a,b)=>a-b), xmax=Math.max(6,pctl(all,99));
  const nb=48, bw=xmax/nb;
  const hist=a=>{const h=new Array(nb).fill(0);a.forEach(v=>{const k=Math.floor(v/bw);if(k>=0&&k<nb)h[k]++;});return h;};
  const hv=hist(mc.vol), hl=hist(mc.val), hpv=hist(mc.pvol), hmax=Math.max(...hv,...hl,...hpv,1);
  const X=v=>mL+(W-mL-mR)*Math.min(v,xmax)/xmax, Y=h=>H-mB-(H-mT-mB)*h/hmax;
  el("line",{x1:mL,y1:H-mB,x2:W-mR,y2:H-mB,stroke:"#ccc"},svg);
  for(let v=0;v<=xmax+1e-6;v+=(xmax>20?5:(xmax>8?2:1)))
    tx(svg,X(v),H-mB+13,v.toFixed(0),{"font-size":9,"text-anchor":"middle",fill:"#666"});
  let ty=14;
  // cultivated by volume + by value, then plant-based by volume (EQUAL FOOTING, green)
  [[hv,mc.vol,"#E69F00","cultivated by volume (impact)"],
   [hl,mc.val,"#0072B2","cultivated by value ($ market)"],
   [hpv,mc.pvol,"#117733","plant-based by volume (impact)"]].forEach(([h,raw,c,lab])=>{
    let d="M"+mL+" "+(H-mB);
    for(let k=0;k<nb;k++){const y=Y(h[k]);d+=" L"+X(k*bw).toFixed(1)+" "+y.toFixed(1)+" L"+X((k+1)*bw).toFixed(1)+" "+y.toFixed(1);}
    d+=" L"+X(xmax)+" "+(H-mB)+" Z";
    el("path",{d,fill:c,opacity:0.30,stroke:c,"stroke-width":1.2},svg);
    const srt=raw.slice().sort((a,b)=>a-b), p10=pctl(srt,10),p50=pctl(srt,50),p90=pctl(srt,90);
    [[p10,0],[p50,1],[p90,0]].forEach(([q,solid])=>el("line",{x1:X(q),y1:mT,x2:X(q),y2:H-mB,
      stroke:c,"stroke-dasharray":solid?"":"3 3","stroke-width":solid?1.5:0.8,opacity:0.85},svg));
    tx(svg,mL,ty,lab+":  P50 "+p50.toFixed(1)+"%   ·   80% CI ["+p10.toFixed(1)+", "+p90.toFixed(1)+"]",
      {"font-size":10,fill:c,"font-weight":700});ty+=15;
  });
  tx(svg,(mL+W-mR)/2,H-2,"Total penetration of meat (%) — cultivated & plant-based, equal footing — solid = median, dashed = 80% CI",
    {"font-size":9,"text-anchor":"middle",fill:"#444"});
  document.getElementById("mcsub").textContent=
    MODEL.regions.find(r=>r[0]===s.region)[1]+": spread of the total share over 2,000 draws of the uncertain inputs.";
}

/* ---------- wiring ---------- */
function recompute(){
  KP=effConsts(state);                               // re-solve the calibration at the current sliders
  // AUTO (non-overridden) SOLVED-weight sliders display the live solved value, so the user sees what
  // the calibration chose (and an override starts from there). Then refresh every weight readout so
  // the "× taste" relative-importance suffix tracks wᵗ when it (or anything) moves. Pinned weights keep
  // the user's value.
  MODEL.sliders.forEach(s=>{
    if(s.solved && !state[s.key+"_ovr"] && (s.key in KP)){
      const v=+KP[s.key].toFixed(2); state[s.key]=v;
      const r=document.getElementById("r_"+s.key); if(r)r.value=v;
    }
    if(s.solved || s.wnorm || s.pricew) setReadout(s);
  });
  const ptmc=state.mc?perTypeMC(state,600):null;     // per-type P10-P90 whiskers when MC is on
  drawHeads(state); drawTiming(state); drawBars(state,ptmc); drawPie(state); drawCost(state); drawCurve(state);
  drawBreakdown(state); drawMilk(state); drawMC(state); drawFoothold(state);
}
function setIncome(v){                                // sync the income slider when the region changes
  state.income=v; const ri=document.getElementById("r_income"), vi=document.getElementById("v_income");
  const s=MODEL.sliders.find(x=>x.key==="income");
  if(ri)ri.value=(s&&s.logscale)?val2pos(s,v):v; if(vi&&s)vi.textContent=fmtVal(s,v);
}
function fillParamTable(){
  const SY=C.param_symbols||{};
  let h='<table class="pt"><tr><th>parameter</th><th>symbol</th><th>default</th><th>range</th>'+
        '<th>where it enters the equations</th><th>source</th></tr>';
  let curG=null;
  MODEL.sliders.forEach(s=>{const sy=SY[s.key]||["",""];
    if(s.group&&s.group!==curG){curG=s.group;
      h+='<tr><td colspan="6" style="background:#f2f6fa;font-weight:700;font-size:.74rem;'+
         'text-transform:uppercase;letter-spacing:.03em;color:#0173B2;padding:5px 4px">'+s.group+'</td></tr>';}
    h+='<tr><td>'+s.label.replace(/\s*\([^)]*\)\s*$/,"")+'</td><td style="white-space:nowrap">'+sy[0]+
    '</td><td class="n">'+fmtVal(s,s.default)+'</td><td class="n">'+fmtVal(s,s.min)+' … '+fmtVal(s,s.max)+
    '</td><td class="s">'+sy[1]+'</td><td class="s">'+s.src+'</td></tr>';});
  document.getElementById("paramtable").innerHTML=h+'</table>';
}
function fillPriceTable(){
  // Group by a CANONICAL (species, tier) key so region-specific variant names
  // (beef wagyu/prime/picanha, seafood sushi/premium, beef steak/cuts vs cuts)
  // collapse into ONE clean row rather than a thicket of near-duplicates.
  const regs=MODEL.regions, TIERW={basic:"mince/processed",cut:"cut/fillet",premium:"premium"},
        TORD={basic:0,cut:1,premium:2}, cap=t=>t.charAt(0).toUpperCase()+t.slice(1);
  const rowmap={}, keys=[];
  regs.forEach(([k])=>{const market=MODEL.markets[k], bases=speciesBases(market);
    market.forEach(mt=>{const sp=cap(animalOf(mt.name)), ti=tierOf(mt,bases[animalOf(mt.name)]),
      key=sp+"|"+ti;
      if(!(key in rowmap)){rowmap[key]={sp,ti,label:sp+" ("+TIERW[ti]+")",price:{},min:Infinity};keys.push(key);}
      rowmap[key].price[k]=mt.p_conv; rowmap[key].min=Math.min(rowmap[key].min,mt.p_conv);});});
  const spMin={}; keys.forEach(k=>{const r=rowmap[k];spMin[r.sp]=Math.min(spMin[r.sp]===undefined?Infinity:spMin[r.sp],r.min);});
  keys.sort((a,b)=>{const A=rowmap[a],B=rowmap[b];
    return (spMin[A.sp]-spMin[B.sp])||A.sp.localeCompare(B.sp)||(TORD[A.ti]-TORD[B.ti]);});
  let h='<table class="pt"><tr><th>meat type (tier)</th>';
  regs.forEach(([k,l])=>h+='<th style="text-align:right">'+l+'&nbsp;$/kg</th>');
  h+='</tr>';
  keys.forEach(key=>{const r=rowmap[key];h+='<tr><td>'+r.label+'</td>';
    regs.forEach(([k])=>{h+='<td class="n">'+(k in r.price?'$'+r.price[k].toFixed(0):'—')+'</td>';});
    h+='</tr>';});
  document.getElementById("pricetable").innerHTML=h+'</table>'+
    '<p style="font-size:.72rem;color:#aaa;margin:4px 0 0">One row per species × tier; region-specific '+
    'premium names (wagyu / prime / picanha / ibérico / sushi …) are grouped under “premium”.</p>';
}
// log-scale slider mapping: position 0..1000 <-> value in [min,max] (log-spaced)
// round to $100 (not $1k) so the region presets — e.g. Nigeria $6,440, China $27,105 —
// stay reproducible from the slider rather than snapping ~$500 away once you touch it.
function pos2val(s,pos){const lo=Math.log(s.min),hi=Math.log(s.max);
  const v=Math.exp(lo+(hi-lo)*pos/1000); return Math.round(v/100)*100;}   // round to $100
function val2pos(s,v){const lo=Math.log(s.min),hi=Math.log(s.max);
  return 1000*(Math.log(Math.max(s.min,Math.min(s.max,v)))-lo)/(hi-lo);}
function fmtVal(s,v){
  if(s.fmt==="signed")return (v>=0?"+":"")+v.toFixed(2);
  if(s.unit==="$/L")return "$"+v.toFixed(2);
  if(s.unit==="$/kg")return "$"+v.toFixed(s.step<1?1:0);
  if(s.unit==="$/yr")return "$"+(v/1000).toFixed(0)+"k";
  if(s.unit==="x")return v.toFixed(2)+"x";
  if(s.unit==="utils")return v.toFixed(1);
  return v.toFixed(2);
}
// utils-denominated weight sliders also show their size relative to the TASTE weight wᵗ (the scale
// anchor a logit reads every other weight against), so "how much each factor matters" is legible.
// Mirror of the wnorm tag in build_model. w_taste itself is the anchor.
function weightSuffix(s){
  if(!s.wnorm) return "";
  if(s.key==="w_taste") return " · the taste scale";
  const wt=(KP&&KP.w_taste)||(("w_taste" in state)?state.w_taste:C.w_taste);
  if(!wt) return "";
  return " · "+(state[s.key]/wt).toFixed(2)+"× taste";
}
// PRICE's weight is the DERIVED coefficient β (utils per $/kg at the calibration anchor) — the price
// analogue of the w-weights. Surface it (and the realised own-price elasticity εₓ = ε·κ) on the
// sliders that set it, so "price has a weight, here it is" is visible right at the price controls.
function priceSuffix(s){
  if(!s.pricew || !KP) return "";
  const b=KP.beta_ref, epsx=KP.eps_own*KP.cult_sub_mult;
  return " · price weight β="+b.toFixed(3)+"/$ (εₓ≈"+epsx.toFixed(1)+")";
}
// one place that builds a slider's value readout: the number, an "(auto)" tag for un-overridden
// solved weights, the "× taste" relative-importance suffix, and (for the price controls) β.
function setReadout(s){
  const vv=document.getElementById("v_"+s.key); if(!vv) return;
  const auto=s.solved && !state[s.key+"_ovr"];
  vv.textContent=fmtVal(s,state[s.key])+(auto?" (auto)":"")+weightSuffix(s)+priceSuffix(s);
}
function buildRail(){
  const rail=document.getElementById("rail");
  // region selector
  const rc=document.createElement("div");rc.className="ctl";
  rc.innerHTML='<label><span class="nm">Region</span></label>';
  const sel=document.createElement("select");
  MODEL.regions.forEach(([k,l])=>{const o=document.createElement("option");o.value=k;o.textContent=l;sel.appendChild(o);});
  sel.value=state.region;
  sel.onchange=()=>{state.region=sel.value;setIncome(C.REGION_INCOME[state.region]);fillCurveSel();recompute();};
  rc.appendChild(sel); rail.appendChild(rc);
  // render one on/off toggle (checkbox + label + help) into `parent`.
  const addToggle=(t,parent)=>{
    const d=document.createElement("div");d.className="tog";
    const cb=document.createElement("input");cb.type="checkbox";cb.id="t_"+t.key;cb.checked=state[t.key];
    cb.onchange=()=>{state[t.key]=cb.checked;recompute();};
    const sp=document.createElement("span");sp.innerHTML=t.label+" ";   // innerHTML so <i>h</i> renders
    addQ(sp, t.tip);
    d.appendChild(cb);d.appendChild(sp);parent.appendChild(d);
  };
  // The KEY assumptions render directly in the rail; every other slider goes inside one collapsed
  // "Advanced" section, still grouped by model step. A group's toggles (e.g. the clean-room cost, which
  // adds to the plant cost h) render right after that group's sliders.
  const adv=document.createElement("details"); adv.className="adv";
  adv.innerHTML="<summary>Advanced assumptions ("+MODEL.sliders.filter(x=>x.adv).length+")</summary>";
  let curGroup=null, host=rail;
  const emitGroupToggles=(g,parent)=>MODEL.toggles.filter(t=>t.group===g).forEach(t=>addToggle(t,parent));
  MODEL.sliders.forEach(s=>{
    if(s.group && s.group!==curGroup){
      if(curGroup!==null) emitGroupToggles(curGroup,host);   // flush the finished group's toggles
      curGroup=s.group; host=s.adv?adv:rail;
      if(s.adv && !adv.parentNode) rail.appendChild(adv);
      const gh=document.createElement("div");gh.className="grphdr";gh.textContent=s.group;
      host.appendChild(gh);}
    const d=document.createElement("div");d.className="ctl";
    d.innerHTML='<label><span class="nm">'+s.label+
      ' <span class="src">['+s.src+']</span> </span>'+
      '<span class="val" id="v_'+s.key+'"></span></label>';
    addQ(d.querySelector(".nm"), s.tip);
    const inp=document.createElement("input");inp.id="r_"+s.key;
    if(s.logscale){   // slider POSITION 0..1000 maps log-spaced onto [min,max]
      Object.assign(inp,{type:"range",min:0,max:1000,step:1,value:val2pos(s,state[s.key])});
      inp.oninput=()=>{state[s.key]=pos2val(s,parseFloat(inp.value));setReadout(s);recompute();};
    }else{
      Object.assign(inp,{type:"range",min:s.min,max:s.max,step:s.step,value:state[s.key]});
      inp.oninput=()=>{state[s.key]=parseFloat(inp.value);setReadout(s);recompute();};
    }
    d.appendChild(inp);
    // SOLVED weight: AUTO by default (slider disabled, value tracks the live calibration); an
    // "override" checkbox PINS it to the slider value and reveals the moment-break warning.
    if(s.solved){
      inp.disabled=!state[s.key+"_ovr"];
      const ov=document.createElement("div"); ov.className="ovr";
      const cb=document.createElement("input"); cb.type="checkbox"; cb.id="o_"+s.key; cb.checked=state[s.key+"_ovr"];
      const lb=document.createElement("label"); lb.htmlFor="o_"+s.key;
      lb.textContent=" override (pin — breaks calibration)";
      const warn=document.createElement("div"); warn.className="wovr"; warn.id="w_"+s.key;
      warn.textContent=s.warn; warn.style.display=state[s.key+"_ovr"]?"block":"none";
      cb.onchange=()=>{
        state[s.key+"_ovr"]=cb.checked; inp.disabled=!cb.checked;
        if(cb.checked && KP && (s.key in KP)){            // start the pin from the current solved value
          state[s.key]=+KP[s.key].toFixed(2); inp.value=state[s.key];
        }
        warn.style.display=cb.checked?"block":"none";
        recompute();
      };
      ov.appendChild(cb); ov.appendChild(lb); d.appendChild(ov); d.appendChild(warn);
    }
    host.appendChild(d);
    setReadout(s);
  });
  if(curGroup!==null) emitGroupToggles(curGroup,host);   // flush the LAST group's toggles
  // any toggles NOT tied to a group render at the end (none today, but keep it robust)
  MODEL.toggles.filter(t=>!t.group).forEach(t=>addToggle(t,rail));
  const b=document.createElement("button");b.className="btn";b.textContent="Reset all to defaults";
  b.onclick=()=>{
    MODEL.sliders.forEach(s=>{                               // by KEY, so it is robust to the rail's layout
      state[s.key]=s.default;
      const inp=document.getElementById("r_"+s.key);
      if(inp) inp.value=s.logscale?val2pos(s,s.default):s.default;
      setReadout(s);});
    MODEL.toggles.forEach(t=>{state[t.key]=false;            // reset by KEY (robust to render order)
      const cb=document.getElementById("t_"+t.key); if(cb)cb.checked=false;});
    MODEL.sliders.forEach(s=>{ if(s.solved){                 // clear any expert weight overrides
      state[s.key+"_ovr"]=false;
      const ob=document.getElementById("o_"+s.key); if(ob)ob.checked=false;
      const ri=document.getElementById("r_"+s.key); if(ri)ri.disabled=true;
      const wd=document.getElementById("w_"+s.key); if(wd)wd.style.display="none"; }});
    setIncome(C.REGION_INCOME[state.region]);            // income tracks the current region, not the US default
    recompute();};
  rail.appendChild(b);
}
/* cross-category VALIDATION (mirror of market_share.pb_milk_check): hold the shared
   taste/price coefficients FIXED but swap the product positions to plant-based MILK's
   (near price/taste parity in coffee/cereal; no cheap whole-food substitute for milk),
   and read its share. The same machinery that makes PB-MEAT fail makes PB-MILK succeed. */
function milkCheck(){
  // reuse the MEAT-derived price coefficient (beta_ref + anchor_price), like market_share.pb_milk_check;
  // then overwrite only the product POSITIONS to milk's (no re-solve).
  const K=Object.assign({},effConsts({}));
  K.price_pb_mult=1.0; K.taste_quality_p=0.0; K.w_realtissue_M=2.1;   // milk-appropriate positions
  // weak outside option (fixed, not solved): no healthy whole-food rival to milk-in-coffee, so the
  // whole-food slot carries a NEGATIVE health position (unit weights) -> the old -2.0 intercept;
  // health_c=0 because DAIRY (not red meat) is milk's reference.
  K.price_wf_mult=1.2; K.health_w=-2.0; K.health_c=0; K.w_health_M=1; K.w_health_E=1;
  return shareCalc(1.0,K,{present:false,which:"pb"});
}
function selfTest(){
  const def={}; MODEL.sliders.forEach(s=>def[s.key]=s.default); def.region="us"; def.income=C.income_ref;
  const Kd=effConsts(def), R=basicR(def);
  const pb=shareCalc(1.0,Kd,{present:false,which:"pb"});
  const s0=shareCalc(1.0,Kd,{ax:1,tfM:0});
  const cold=shareCalc(1.0,Kd,{ax:1,tfM:0,nbx:C.priors.neophobia_x0[1]});   // cold-start at parity
  // REGIONAL income-channel check: JS share at a non-US income vs the injected Python reference.
  // The income/alpha normalisation coincides at income_ref, so the US case alone can't catch
  // regional drift — this China point will mismatch if the JS and Python income terms fall apart.
  const ic=C.income_check, jsChina=shareCalc(ic[1],Kd,{ax:1,tfM:0,income:ic[0]})*100;
  const jsUS=shareCalc(ic[1],Kd,{ax:1,tfM:0,income:C.income_ref})*100;   // US at the same R, for the contrast
  const regOK=Math.abs(jsChina-ic[2])<0.1;
  const solveOK=Math.abs(Kd.w_realtissue_M-C.w_realtissue_M_ref)<0.05;
  const buildOK=regOK&&solveOK;
  const mlk=milkCheck()*100;
  // ONE status per row, three distinct meanings (no overloaded ✓):
  //   MATCHES    = a genuine out-of-sample hit (the model was NOT fitted to it)
  //   CALIBRATED = the model is SET to reproduce it (a consistency check, not a test)
  //   MODEL OUTPUT = a model projection with no real-world figure to check against
  const TAG={match:"<span class='sttag tag-match'>MATCHES</span>",
             cal:"<span class='sttag tag-cal'>CALIBRATED</span>",
             proj:"<span class='sttag tag-proj'>MODEL OUTPUT</span>"};
  // each row: [plain-language what, model value, the real-world anchor (or meaning), tag]
  const rows=[
    ["Plant-based <b>milk</b>, same model", (mlk).toFixed(0)+"%",
       "real share ~15% (milk's facts set by hand: a weak test)", "match"],
    ["<b>Cultivated</b> at equal price, first contact", (cold*100).toFixed(0)+"%",
       "Lusk 2020 found ~5%; starting wariness set to match", "cal"],
    ["<b>Cultivated</b> at equal price, once familiar", (s0*100).toFixed(0)+"%",
       "long-run projection", "proj"],
    ["China vs US, same product and price",
       jsChina.toFixed(0)+"% vs "+jsUS.toFixed(0)+"%",
       "poorer shoppers feel the premium more", "proj"],
  ];
  const rowHTML=([what,val,obs,tag])=>
    "<tr><td class='stwhat'>"+what+"<div class='stobs'>"+obs+"</div></td>"+
    "<td class='stval'>"+val+"</td>"+
    "<td style='text-align:right;white-space:nowrap'>"+TAG[tag]+"</td></tr>";
  document.getElementById("selftest").innerHTML=
    "<div class='sthead'>Reality checks (at the default settings)</div>"+
    "<div class='stanchor'>Fitted to: plant-based meat's ~1.2% US share (model: "+(pb*100).toFixed(1)+"%) and ~89% "+
    "mainstream buyers, plus an assumed ~6% meatless rate (A4). Not fitted:</div>"+
    "<table>"+rows.map(rowHTML).join("")+"</table>"+
    "<div class='stnote'><b>MATCHES</b>: a real number the model wasn't fitted to. <b>CALIBRATED</b>: set to "+
    "match, so a consistency check. <b>MODEL OUTPUT</b>: nothing real to compare yet.</div>"+
    "<div class='stbuild'>"+(buildOK?"✓":"&#9888;")+" Build check: the in-browser model reproduces the Python "+
    "source exactly (calibration &amp; the cross-region income term)"+(buildOK?".":" — MISMATCH, rebuild needed.")+"</div>";
}
console.log("interactive.html JS build __BUILD_STAMP__ — loss-aversion canonical form + betaCap monotonicity guard active");
buildRail(); selfTest(); fillParamTable(); fillPriceTable(); fillCurveSel(); fillCmpSel(); fillFootholdSel(); buildPieToggle();
// chart titles carry their longer "how to read" text in data-help, shown by the same "?" badge as the sliders
document.querySelectorAll("[data-help]").forEach(h=>addQ(h,h.getAttribute("data-help")));
function setFootView(v){state.footView=v;
  document.getElementById("footWL").classList.toggle("on",v!=="margin");
  document.getElementById("footMV").classList.toggle("on",v==="margin");
  drawFoothold(state);}
document.getElementById("footWL").onclick=()=>setFootView("waterline");
document.getElementById("footMV").onclick=()=>setFootView("margin");
document.getElementById("mcbtn").onclick=function(){state.mc=!state.mc;
  this.textContent="Monte Carlo: "+(state.mc?"on (2000 draws)":"off");
  this.classList.toggle("on",state.mc);recompute();};
recompute();
</script></body></html>"""


def main() -> None:
    model = build_model()
    crosscheck(model)
    import datetime as _dt
    html = PAGE_HTML + JS_ENGINE                         # page markup + the JS engine (two strings, one file)
    html = html.replace("__MODEL_JSON__", json.dumps(model))
    html = html.replace("__BUILD_STAMP__", _dt.datetime.now().strftime("%Y-%m-%d %H:%M"))
    # Substitute the illustrative numbers COMPUTED FROM THE MODEL (no hand-typed shares in the
    # prose/tooltips — they can never drift from the live calibration). See illustrative_numbers().
    illus = illustrative_numbers()
    for token, val in illus.items():
        html = html.replace(token, val)
    # Non-share model numbers (price ratios, $/kg, years, the kappa-validation elasticity), likewise
    # computed from the live model. See derived_numbers().
    derived = derived_numbers()
    for token, val in derived.items():
        html = html.replace(token, val)
    # The attribute-weights table, GENERATED from the live solved DemandParams (never hand-typed).
    html = html.replace("__WEIGHTS_TABLE__", weights_table_rows())
    if "__WEIGHTS_TABLE__" in html:
        raise RuntimeError("weights table token was not substituted")
    leftover = [t for t in list(illus) + list(derived) if t in html]
    if leftover:                                          # a typo'd placeholder would ship a literal {{TOKEN}}
        raise RuntimeError(f"unsubstituted illustrative tokens remain: {leftover}")
    import re as _re
    stray = _re.findall(r"\{\{[A-Z0-9_]+\}\}", html)
    if stray:
        raise RuntimeError(f"unknown {{{{...}}}} placeholders in the template (no value computed): {sorted(set(stray))}")
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"  wrote {os.path.relpath(OUT)}  ({os.path.getsize(OUT)/1024:.0f} KB, self-contained); "
          f"substituted {len(illus)} model-computed shares and {len(derived)} other model numbers")


if __name__ == "__main__":
    main()
