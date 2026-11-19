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

from inputs import (value, prior, AA_FLOOR, GLUCOSE_OTHER_FLOOR, PLANT_CONFIGS, MC_COST_INPUTS, MC_DEMAND_INPUTS,
                    MC_TIER_INPUTS, MC_CUT_INPUTS, MC_TIMING_INPUTS, REGISTRY, LOGNORMAL_Z90)
import meat_market as mm
from price_ratio import shelf_price, cost_from_shelf, structured_cost
import floor_physics
import plant_items
import contamination
from market_share import (DemandParams, LOSS_AVERSION_RATIO,
                          lusk_at_parity_elasticity as _lusk_at_parity)
from foothold import PRODUCTS as _FOOTHOLD, base_price as _fbase, PRICE_BASIS as _FBASIS


def _plant_oh(substr):
    """Everything-but-medium cost ($/kg) for a plant case, matched by a substring of its PLANT_CONFIGS
    key — keeps the cost-chart numbers tied to the datasheet (no magic duplicate)."""
    for k, v in PLANT_CONFIGS.items():
        if substr.lower() in k.lower():
            return v
    raise KeyError(f"no PLANT_CONFIGS key contains {substr!r}")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "interactive.html")


def _prior_lo_hi(name):
    kind, lo, hi, mode, _ = prior(name)
    return lo, hi


def _lognormal_5_95(name):
    """5th and 95th percentile of a lognormal input's draws before clipping: median x (lo/hi)^0.5 and median x (hi/lo)^0.5
    (inputs.sample: lo and hi set the spread; they are the percentiles themselves only when the median is their geometric mean)."""
    inp = REGISTRY[name]
    return inp.prior_mode * (inp.lo / inp.hi) ** 0.5, inp.prior_mode * (inp.hi / inp.lo) ** 0.5


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
    R = cost_ratio(biomass_cost(cp, value("media_price"), 1.0), cp)   # R at the default cost
    inc = mm.REGION_INCOME["china"]
    return [inc, R, _share(R, dp, income=inc) * 100.0]


def build_model() -> dict:
    import market_share as _ms
    dp = DemandParams()        # runs the calibration solve once -> reference solved values for the self-check
    const = {
        "media_intensity": value("media_intensity"),
        "AA_FLOOR": AA_FLOOR,
        "FEEDSTOCK_FLOOR": AA_FLOOR + GLUCOSE_OTHER_FLOOR,
        "glucose_other_floor": GLUCOSE_OTHER_FLOOR,
        "plant_floor": value("plant_floor"),
        # cost cross-checks for the page's reality checks (inputs.py; not used in the cost)
        **{k: value(k) for k in ("humbird_plant_cost", "humbird_tci_fedbatch", "humbird_output_fedbatch",
                                 "humbird_plant_charge", "believer_capex", "believer_capacity")},
        # build-your-own-case controls: the JS floorExplore mirrors floor_physics.explore on these
        "fx": {
            "charge_mature": value("plant_charge_mature"), "charge_first": value("humbird_plant_charge"),
            "uptime_perfusion": value("pf_uptime"), "uptime_filldraw": value("pf_uptime_realistic"),
            "capex": {k: value(v[0]) * (value("pf_capex_escalation") if v[1] else 1.0)
                      for k, v in floor_physics.PLANT_CLASSES.items()},
            "sized": {k: v[2] for k, v in floor_physics.PLANT_CLASSES.items()},
            "retention": value("pf_capex_retention"), "bioreactor_share": value("pf_bioreactor_capex_share"),
            # the default retention device, a TFF hollow-fibre loop (floor_physics.explore, retention.py)
            "tff": {"on": value("rt_tff_default") >= 0.5, "flux": value("rt_flux_lmh"), "hw": value("rt_tff_hw"), "install": value("rt_install"),
                    "mem_price": value("rt_membrane_price"), "mem_life": value("rt_membrane_life")},
            "otr": value("pf_otr_cap"), "x_visc": value("pf_x_visc"), "x_co2_20": value("pf_x_co2_20m3"),
            "x_waste": value("pf_x_unperfused"),
            "pco2": value("pf_pco2_limit"), "gas_v": value("pf_gas_velocity"), "aspect": value("pf_aspect"),
            "rq": value("pf_rq"), "strip_eff": value("pf_co2_strip_eff"), "antifoam": value("pf_antifoam_otr"), "protect_dose": value("pf_protectant_dose"),
            "protect_price": value("pf_protectant_price"), "o2_microbial": value("pf_o2_microbial") >= 0.5,
            "draw": value("pf_draw_fraction"), "wv": value("pf_working_volume"),
            "labour_ref": value("pf_labour") * floor_physics.output_per_m3(floor_physics.GOOD_CELLS, "fedbatch")
                          * value("pf_opex_escalation"),
            "utilities": value("pf_utilities") * value("pf_opex_escalation"),
            "consumables": value("pf_consumables_low"),
            "power_coef": value("pf_power_coef"), "heat_per_o2": value("pf_heat_per_o2"),
            "aa": AA_FLOOR, "glucose": floor_physics.GLUCOSE_FLOOR, "other": value("other_nutrients_floor"),
            "ref_mass": floor_physics.GOOD_CELLS.mass_pg, "ref_doubling": floor_physics.GOOD_CELLS.doubling_h,
            "run_days": value("pf_run_days"), "medium_l": value("pf_medium_l_floor"),
            "gf": value("pf_growth_factors") * value("pf_opex_escalation"), "filler": value("pf_blend_filler_price"),
            "hazard_pharma": value("pf_hazard_pharma"),
            "nh3": [value("pf_nh3_efficient"), value("pf_nh3_wild")],
            "lac": [value("pf_lac_efficient"), value("pf_lac_wild")],
            "nh3_limit": value("pf_nh3_limit"), "lac_limit": value("pf_lac_limit"),
            "osm_base": value("pf_osm_base"), "osm_limit": value("pf_osm_limit"), "ph": value("pf_ph"),
            "pk1": value("pf_pk1"), "co2_henry": value("pf_co2_henry"), "hco3_base": value("pf_hco3_base"),
            "min_perfusion": value("pf_min_perfusion"),
            "gf_litres": floor_physics.washout_litres(floor_physics.GOOD_CELLS),
            # tornado factors: [label, JS argument, low, high, low text, high text] (floor_physics.TORNADO)
            "tornado": [[lab, {"pco2_mbar": "pco2", "gas_velocity": "gas_v", "maintenance_share": "maint", "p_top_barg": "p_top"}.get(arg, arg),
                         lo, hi, lo_t, hi_t, info] for lab, arg, lo, hi, lo_t, hi_t, info in floor_physics.TORNADO],
            "maint_share": value("pf_maintenance_share"), "mix_ratio": value("pf_mix_ratio_20m3"),
            "species": {k: list(v) for k, v in floor_physics.SPECIES_PRESETS.items()},
            # the tricks (gas_exchange.column_design / headspace_pressure; sorbent and explicit wastes)
            "glc_kg": value("pf_glc_kg"), "glc_anabolic": value("pf_glc_anabolic"), "sorbent_q": value("pf_sorbent_q"), "sorbent_price": value("pf_sorbent_price"),
            "sorbent_cycles": value("pf_sorbent_cycles"), "pco2_design": value("pf_pco2_limit"),
            "rq_lipid": value("pf_rq_lipid"), "fat_kg": value("pf_fat_kg"), "fat_price": value("pf_fat_price"),
            "do_implied": __import__("gas_exchange").headspace_pressure()["c_liquid_implied"],
            "uptime_col": value("pf_uptime"), "cell_density": value("pf_cell_density"),
            "medium_density": value("pf_medium_density"), "medium_viscosity": value("pf_medium_viscosity"),
            "ge": {k[3:]: value(k) for k in ("ge_pk_area", "ge_pk_angle", "ge_pk_side", "ge_pk_ce", "ge_pk_load",
                   "ge_surface_tension", "ge_d_co2", "ge_d_o2", "ge_o2_henry", "ge_do_setpoint", "ge_o2_sweep_purity",
                   "ge_col_gas_in", "ge_col_gas_out", "ge_col_head_extra", "ge_col_pout", "ge_pump_eff", "ge_pump_cost",
                   "ge_pump_flow", "ge_install_x", "ge_col_extra_height", "ge_col_wall", "ge_head_area", "ge_cepci_2014",
                   "ge_power_price", "ge_o2_price", "ge_lime_price", "ge_lime_use", "ge_p_top_base", "ge_sparge_o2",
                   "ge_kla_20m3", "ge_buffer", "ge_vessel_cost_exp", "ge_hall_share", "ge_clearance_m",
                   "ge_loop_transit", "ge_passes_tested", "ge_paul_dph", "ge_paul_share")},
            "species_missing": floor_physics.SPECIES_MISSING,
            # the plant item by item (plant_items): {item: {option: [capital $k per m3 in 2018 dollars, text]}},
            # the options each plant choice in the panel stands for, and the cost of bought oxygen per kg
            "items": {item: {o: [c, txt] for o, (c, txt) in opts.items()}
                      for item, opts in plant_items.options().items()},
            "item_labels": plant_items.ITEM_LABELS,
            "plant_items": {"pharma": plant_items.choices_for("humbird"), "sanitary": plant_items.choices_for("floor"),
                            "lean": plant_items.choices_for("lean"), "yeastplus": plant_items.choices_for("yeastplus"),
                            "microbial": plant_items.choices_for("yeast")},
            "o2_opex": value("pi_o2_feed") * value("pi_o2_price"), "escalation": value("pf_capex_escalation"),
            # loss rates per day at which a cheaper plant stops paying (contamination.breakeven_hazard), and the
            # rate cultivated-meat makers report
            "breakeven": {k: contamination.breakeven_hazard(k) for k in ("lean", "yeastplus")},
            "hazard_cm": value("ct_hazard_frontier"),
        },
        "cost_reference": AA_FLOOR + GLUCOSE_OTHER_FLOOR + value("plant_floor"),   # standard perfusion tank, no tricks
        # --- demand: two-segment, four-product discrete-choice (logit) model ---
        # products: w=whole-food, c=conventional, p=plant-based, x=cultivated.
        # the JS mirrors market_share._utilities/share and re-runs the calibration solve.
        "eqs_default": value("equal_price_share"),   # the central demand setting (scApply resets to it)
        "p_conv_anchor": value("p_conv"),       # the $12 commodity anchor: conventional's price in the demand model
        "eps_own": value("eps_own"),
        "cult_sub_mult": value("cult_sub_mult"),  # closeness/substitutability lever
        "kappa_base": value("kappa_base"),        # sets the shared beta; kappa/kappa_base acts on cultivated's price gap
        # shoppers differ in how much they like cultivated meat (market_share.share, _segment, _solve_liking)
        # The spread is a standardised distribution given as nodes z_i and weights w_i (market_share.spread_quadrature): a shopper
        # of kind i likes cultivated meat by liking_mean + liking_sd * z_i. The JS uses the two arrays as they come, so it mirrors
        # whichever shape is the default (a Student's t since 2026-11-19; inputs.LIKING_FAMILY, liking_tail) without knowing its formula.
        "liking_sd": value("liking_sd"), "equal_price_share": value("equal_price_share"),
        "liking_family": _ms.LIKING_FAMILY, "liking_tail": value("liking_tail"),
        "spread_nodes": [float(v) for v in _ms.SPREAD_NODES], "spread_weights": [float(v) for v in _ms.SPREAD_WEIGHTS],
        "liking_grid": [float(v) for v in _ms.LIKING_GRID],
        # the demand price coefficient beta is DERIVED (mirror of market_share._derive_beta):
        # anchored at a FIXED calibration price (inputs elasticity_anchor_price), solved at cultivated's
        # own share there via a fixed point. Neither the cost defaults nor the live sliders move it.
        "anchor_price": value("elasticity_anchor_price"),
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
        "w_ratio": value("w_ratio"),                # weight of the ratio-based (income-free) price term
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
        # REGIONAL income-channel reference: Python share at the default R for a non-US income.
        # Guards against the income/alpha mirror silently drifting again (the US case alone can't —
        # at income_ref both alpha forms coincide). [income, R, Python share %].
        "income_check": _income_check(dp),
        "cleanroom_cost": value("cleanroom_cost"),
        # per-region income (GDP/cap PPP) for the BLP price term
        "REGION_INCOME": mm.REGION_INCOME,
        # "premium" as a LABEL for charts (nothing numeric depends on it), and the premium penalty's price range (tierOffset)
        "PREMIUM_RATIO": mm.PREMIUM_RATIO,
        "PREMIUM_START": mm.PREMIUM_START, "PREMIUM_FULL": mm.PREMIUM_FULL,
        "AUTH_PREMIUM_EXTRA": mm.AUTH_PREMIUM_EXTRA,
        # a cut = cut_cells x cells + (1 - cut_cells) x matrix price + assembly (price_ratio.structured_cost; cutCost below)
        "matrix_price": value("material_price"),
        # WHICH inputs the page's bands sample: the SAME lists the Python bands use (inputs.MC_*),
        # so the page's band and the numbers quoted in RESULTS.md cannot sample different sets.
        "mc_inputs": list(MC_COST_INPUTS + MC_DEMAND_INPUTS + MC_TIER_INPUTS + MC_CUT_INPUTS),
        "mc_timing_inputs": list(MC_TIMING_INPUTS),
        # Monte-Carlo priors [lo, mode, hi] for every sampled input: triangular, unless prior_kinds names the input
        "priors": {
            **{k: list(_prior_lo_mode_hi(k))
               for k in dict.fromkeys(MC_COST_INPUTS + MC_DEMAND_INPUTS + MC_TIER_INPUTS + MC_CUT_INPUTS
                                      + MC_TIMING_INPUTS)},
            # plant-based's own health prior (its band, equal footing with cultivated's health_x)
            "health_p": list(_prior_lo_mode_hi("health_p")),
            # plant-based exploratory dials, also swept so PB gets a band on equal footing
            # with cultivated (its taste a_p, novelty ν_p, cold-start ν_p0). Centred at defaults.
            "a_p": [0.6, 0.8, 1.0],
            "neophobia_p": [-1.0, 0.0, 1.0],
            "neophobia_p0": [-2.0, -1.0, 0.5],
        },
        # inputs whose prior is not triangular (inputs.sample): {name: [kind, clip low, clip high]}. lognormal: the median is
        # priors[name][1] and priors[name][0], [2] are the 5th and 95th percentiles (mcDraw mirrors inputs.draw)
        "prior_kinds": {k: [REGISTRY[k].kind, *(REGISTRY[k].clip or (None, None))]
                        for k in dict.fromkeys(MC_COST_INPUTS + MC_DEMAND_INPUTS + MC_TIER_INPUTS + MC_CUT_INPUTS
                                               + MC_TIMING_INPUTS) if REGISTRY[k].kind != "triangular"},
        "lognormal_z90": LOGNORMAL_Z90,
        "years": int(value("years")),   # diffusion horizon for the timing rung
        # reactor configs for the cost chart: [short label, overhead $/kg]. The overhead
        # NUMBERS are read from inputs.PLANT_CONFIGS (the source of truth) so they can't
        # drift from the datasheet; only the short display labels live here.
        "configs": [["the plant of Humbird's optimistic design", _plant_oh("reference plant")],
                    ["the plant the company reports", _plant_oh("as reported")],
                    ["a pharma-style plant, cells at half the density", _plant_oh("cautious")]],
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
                "K_wf":-2.0,"health":0.0,"obs":15.0,"note":"Price and taste parity are in use (coffee and cereal). There is no cheap rival.",
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
            "cut_cells":     ["c", "Eq. (1), structured cuts only"],
            "markup_add":    ["a", "Eq. (1)"],
            "retail_margin": ["m", "Eq. (1)"],
            "meat_tax":      ["t", "denominator of Eq. (1)"],
            "income":        ["y", "income term &alpha;&thinsp;ln(y<sub>eff</sub>&minus;p<sub>j</sub>) in Eq. (2), see A2"],
            "income_gradient": ["&phi;", "y<sub>eff</sub> = y<sub>ref</sub>(y/y<sub>ref</sub>)<sup>&phi;</sup>, see A2"],
            "eps_own":       ["&epsilon;", "sets the price weight &beta;, see A1"],
            "cult_sub_mult": ["&kappa;", "sets the price weight &beta;, see A1"],
            "loss_aversion": ["&lambda;", "reference-price term w<sub>r</sub>[&minus;&lambda;(d<sub>j</sub>)<sup>+</sup>+(d<sub>j</sub>)<sup>&minus;</sup>] in Eq. (2), see A3"],
            "w_ratio":       ["w<sub>r</sub>", "weight of the reference-price term in Eq. (2), see A3"],
            "accept_x":      ["a<sub>x</sub>", "taste term w<sup>t</sup>(a<sub>x</sub>&minus;1) in Eq. (2)"],
            "neophobia_x":   ["&nu;<sub>x</sub>", "novelty term in Eq. (2); long-run end of Eq. (5)"],
            "neophobia_p":   ["&nu;<sub>p</sub>", "plant-based novelty term in Eq. (2)"],
            "a_p":           ["a<sub>p</sub>", "plant-based taste term in Eq. (2)"],
            "R_p":           ["R<sub>p</sub>", "plant-based price in Eq. (2)"],
            "theta_free_M":  ["&theta;", "mainstream no-slaughter weight w<sup>s</sup> in Eq. (2)"],
            "w_eth":         ["w<sub>eth</sub>", "segment mix, Eq. (3)"],
            "premium_resistance": ["&rho;", "scales the premium part of the offset &tau;, see A5"],
            "real_tissue_x": ["b<sub>x</sub>", "real-meat term w<sup>rt</sup>b<sub>x</sub> in Eq. (2)"],
            "real_tissue_p": ["b<sub>p</sub>", "plant-based real-meat term in Eq. (2)"],
            "health_x":      ["&zeta;<sub>x</sub>", "health term w<sup>h</sup>&zeta;<sub>x</sub> in Eq. (2)"],
            "health_p":      ["&zeta;<sub>p</sub>", "plant-based health term in Eq. (2)"],
            "auth_premium_extra": ["&tau;<sub>prem</sub>", "the full premium part of the offset &tau; in Eq. (2), see A5"],
            "w_taste":       ["w<sup>t</sup>", "taste weight in Eq. (2), see A4"],
            "w_realtissue_M": ["w<sup>rt</sup><sub>M</sub>", "real-meat weight in Eq. (2), mainstream, see A4"],
            "w_realtissue_E": ["w<sup>rt</sup><sub>E</sub>", "real-meat weight in Eq. (2), ethical, see A4"],
            "w_health_M":    ["w<sup>h</sup><sub>M</sub>", "health weight in Eq. (2), mainstream, see A4"],
            "w_health_E":    ["w<sup>h</sup><sub>E</sub>", "health weight in Eq. (2), ethical, see A4"],
            "w_slaughter_E": ["w<sup>s</sup><sub>E</sub>", "no-slaughter weight in Eq. (2), ethical, see A4"],
            "neophobia_x0":  ["&nu;<sub>x0</sub>", "starting novelty in Eq. (5)"],
            "neophobia_p0":  ["&nu;<sub>p0</sub>", "plant-based starting novelty in Eq. (5)"],
            "accept_rate":   ["r", "fade speed in Eq. (5)"],
            "p_innov":       ["p<sub>B</sub>", "Bass rollout F(t) in Eq. (5)"],
            "q_imit":        ["q<sub>B</sub>", "Bass rollout F(t) in Eq. (5)"],
            "phi":           ["&chi;", "reachable volume (1&minus;&chi;)Q, see A6"],
        },
    }

    HIDDEN_GROUP = "As a company reports (not shown on the page)"
    def slider(key, label, unit, lo, hi, step, default, src, tip, fmt="num"):
        return dict(key=key, label=label, unit=unit, min=lo, max=hi, step=step,
                    default=default, src=src, tip=tip, fmt=fmt)

    # Rail layout: the KEY assumptions first (always visible), then everything else inside one
    # collapsed "Advanced" section, grouped by the model step it belongs to (the same Step 1-4 the
    # methods and the four-step strip at the top use). (name, keys, advanced?)
    SLIDER_GROUPS = [
        ("Main settings",
         ["equal_price_share", "accept_x", "premium_resistance", "markup_add", "retail_margin", "meat_tax"], False),
        ("A cut (a steak or fillet)", ["cut_cells", "scaffold"], True),
        ("How shoppers choose",
         ["eps_own", "cult_sub_mult", "liking_sd", "theta_free_M", "loss_aversion", "w_ratio", "income", "income_gradient", "w_eth",
          "health_x", "neophobia_x", "real_tissue_x"], True),
        ("Plant-based meat", ["R_p", "a_p", "real_tissue_p", "health_p", "neophobia_p"], True),
        ("Premium products", ["auth_premium_extra"], True),
        ("Over time",
         ["neophobia_x0", "accept_rate", "p_innov", "q_imit", "neophobia_p0"], True),
        ("Entry points (which products first)", ["phi"], True),
        ("Expert: the weights shoppers give each attribute",
         ["w_taste", "w_realtissue_M", "w_health_M", "w_health_E", "w_slaughter_E",
          "w_realtissue_E"], True),
        (HIDDEN_GROUP, ["media_price", "overhead", "efficiency"], True),
    ]

    # Tooltips follow one pattern: what it is -> what moving it does (with a model-computed number,
    # via {{TOKEN}}, where that helps) -> default and source. Kept short on purpose; the methods
    # section carries the detail.
    sliders = [
        # ---- key assumptions ------------------------------------------------------------
        slider("media_price", "Medium price (<i>p</i><sub>med</sub>)", "$/L", 0.10, 1.00, 0.01,
               value("media_price"), "SuperMeat / GFI",
               tip="This is the price of the nutrient liquid the cells grow in, the biggest single cost. The default $0.50/L "
               "is what one company reports for its own medium. Others report $0.20/L or less. "
               "Nobody has verified any of these at production scale. $1.00/L stands for a process that has not reached production scale. Each "
               "$0.10/L adds about ${{MEDIA_PER_010}}/kg."),
        slider("overhead", "Plant running cost (<i>h</i>)", "$/kg", value("plant_floor_lo"), _plant_oh("cautious"), 0.1,
               value("overhead"), "SuperMeat / physics",
               tip="This covers everything except the medium, per kg. It includes reactors and other capital, labour, energy and "
               "consumables. The default ${{OH_DEF}} is one company's running costs for a 25,000-litre perfusion plant, "
               "plus a yearly charge on the plant. ${{OH_FLOOR}} is the plant term of the reference tank, which is a food-grade plant costed for "
               "animal cells with food-industry financing. ${{PLANT_FLOOR_LO}} is a plant that costs what "
               "microbial fermentation plants cost, and no scenario assumes it. ${{OH_HI}} is a cautious case with a pharma-style plant and cells at half "
               "the density."),
        slider("markup_add", "Costs to the shelf (<i>a</i>)", "$/kg", 0.0, 9.0, 0.1, value("markup_add"),
               "USDA spread fit",
               tip="Forming, packing, cold chain, transport and store handling, added per kg. They do not grow with the "
               "product's price: USDA's meat prices show shop prices moving about dollar for dollar with wholesale prices. "
               "Fitted to USDA's 2025 spreads with a 28% shop margin, they are $1.6/kg for chicken and $2.9 for beef; "
               "the default $2.5 adds about $1 to form cells into a product. Set this to $5 and the shop margin to 0 "
               "for the model's flat rule before November 2026."),
        slider("retail_margin", "Shop's margin (<i>m</i>)", "of price", 0.0, 0.45, 0.01, value("retail_margin"),
               "meat departments",
               tip="The shop's gross margin as a share of the shelf price, so a dearer product carries a larger margin "
               "in dollars. US supermarket meat departments run at about 28-32%; French supermarkets take 25% on a "
               "premium Label Rouge chicken and 36% on a chicken fillet. The shelf price is (cost + <i>a</i>) / (1 &minus; <i>m</i>).",
               fmt="pct"),
        slider("meat_tax", "Meat price multiplier (<i>t</i>)", "x", 0.8, 1.6, 0.05, 1.0, "policy",
               tip="This multiplies every conventional meat price, for example through a meat or carbon tax. A value of 1.0 leaves "
               "prices as they are. A multiplier of 1.25 lowers cultivated meat's price ratio as much as cutting all its "
               "costs by 20%."),
        slider("real_tissue_x", "Seen as real meat (<i>b</i><sub>x</sub>)", "0→1", 0.0, 1.0, 0.05,
               value("real_tissue_x"), "premise",
               tip="Whether shoppers count cultivated meat as real animal meat. Until November 2026 this set the share at "
               "equal price. That share is now a setting of its own, and it absorbs this one: moving this slider leaves "
               "cultivated meat's share almost unchanged. It is kept for the record. The matching slider for plant-based meat "
               "still matters."),
        slider("accept_x", "Taste vs conventional (<i>a</i><sub>x</sub>)", "", 0.6, 1.2, 0.05, 1.0,
               "judgement",
               tip="This is how good cultivated meat tastes next to the conventional product, where 1 means just as good. The share "
               "at equal price is ~{{PARITY_NEUTRAL}}% at 1, ~{{AX_08}}% at 0.8, ~{{AX_06}}% at 0.6 and ~{{AX_11}}% at 1.1 "
               "(tastier). This is a judgement call, because nobody has tasted it at scale. The "
               "Monte Carlo samples this slider."),
        slider("theta_free_M", "Mainstream values “no slaughter” (&theta;)", "", 0.0, 1.5, 0.05, 0.0,
               "judgement",
               tip="This is how much mainstream shoppers (95% of people) care that no animal was killed. The default 0 "
               "means not at all. Raising it lifts every slaughter-free option, and cultivated meat most. "
               "The share at equal price is ~{{TH_05}}% at 0.5 and ~{{TH_10}}% at 1. The Monte Carlo samples this slider "
               "from 0 to 1."),
        slider("premium_resistance", "How much less buyers of premium products like a cultivated version (&rho;)", "x", 0.0, 2.0, 0.1,
               value("premium_resistance"), "judgement",
               tip="This is how much less buyers of premium products (wagyu, sushi-grade fish) like a cultivated version, beyond what "
               "applies to any cut. A value of 1 is the model's setting, 0 means a premium product is liked as much as any other cut, and "
               "2 doubles the penalty. It does not change mince or ordinary cuts. There are no direct data, so the Monte "
               "Carlo samples 0.5 to 1.5."),
        # ---- step 1: cost and price ----------------------------------------------------------
        slider("efficiency", "Cell efficiency (&eta;)", "x", 0.25, 1.0, 0.05, value("efficiency"),
               "SuperMeat / Humbird",
               tip="This is the medium used per kg, relative to the reported process, where 1 is the default. A value of 0.25 means four "
               "times leaner, like the CHO cells used in pharma. Nobody has shown this for food cells. The Monte "
               "Carlo samples 0.25 to 1, so its median assumes some improvement."),
        slider("cut_cells", "Share of a cut that is cells (<i>c</i>)", "", 0.1, 1.0, 0.05, mm.CUT_CELL_SHARE,
               "assumed",
               fmt="pct",
               tip="A cut (steak or fillet) is made by binding harvested cells with plant protein. The rest of the cut is that "
               "plant protein, at $" + f"{value('material_price'):.0f}" + "/kg. Cuts sold or approved so far are 10 to 30% cells. "
               "Nobody has shown a cut that is mostly cells grown in suspension with the texture of meat. The model's setting keeps the cut "
               "mostly cells. A lower share makes a cut cheaper, and shoppers like it less: a cut that is part plant protein gets "
               "that much less of the credit shoppers give real meat. The Monte Carlo samples "
               + f"{(1 - REGISTRY['scaffold_frac'].hi) * 100:.0f} to {(1 - REGISTRY['scaffold_frac'].lo) * 100:.0f}" + "% cells."),
        slider("scaffold", "Cost of assembling a cut (<i>k</i>)", "$/kg", 0.0, 12.0, 0.5, mm.SCAF,
               "analogues",
               tip="This is the cost of binding, forming, setting and slicing a cut after the cells are harvested. Mince does not need it. "
               "No study has costed it for cultivated meat, so the figure comes from plant-protein extrusion ($0.4 to $1.6 a kilo), "
               "surimi forming (about $1) and binder prices: $1 to $8 all in, less the $1 of forming and packing that every product already pays "
               "in the costs of reaching the shelf. Growing the cells into tissue on a scaffold "
               "instead would add about $10 a kilo, which is why companies have dropped it. The Monte Carlo samples $"
               + f"{REGISTRY['process_cost'].lo:g} to ${REGISTRY['process_cost'].hi:g}" + "."),
        # ---- step 2: how shoppers choose -----------------------------------------------------
        slider("eps_own", "Price sensitivity of meat (&epsilon;)", "", -1.4, -0.5, 0.05,
               value("eps_own"), "scanner data",
               tip="This is how much meat purchases fall when prices rise. The default −0.9 means that meat 1% dearer sells 0.9% "
               "less (Andreyeva 2010). Meta-analyses span −0.7 to −1.0. A single cultivated "
               "product is several times more sensitive than this, because conventional meat sits beside it on the shelf (the next "
               "slider). The Monte Carlo samples this slider."),
        slider("equal_price_share", "Share at equal price, once familiar", "of buyers", 0.03, 0.80, 0.01,
               value("equal_price_share"), "judgement", fmt="pct",
               tip="If cultivated meat cost the same as the meat beside it, tasted the same and was no longer new, this is the "
               "share of that meat's buyers who would choose it. At first contact a US choice experiment found about 5%. The "
               "default 13% assumes a third of that first wariness fades: novelty fades by half, while the sense that it is "
               "unnatural stays. 49% would mean shoppers end up indifferent on average. The best case takes "
               f"{value('best_equal_price_share'):.0%}: shoppers slightly favour it. Nobody has measured it, and it moves "
               "the long-run share more than any cost does. The Monte Carlo draws it with a median of "
               f"{value('equal_price_share'):.0%}, and nine draws in ten fall between about "
               f"{_lognormal_5_95('equal_price_share')[0]:.0%} and {_lognormal_5_95('equal_price_share')[1]:.0%}."),
        slider("liking_sd", "Spread of liking between shoppers", "points of score", 0.0, 8.0, 0.1, value("liking_sd"),
               "Van Loo 2020",
               tip="How much shoppers differ in how much they like cultivated meat. With a wide spread, the shoppers still "
               "buying at a high price are the ones who like it most, so sales fall off slowly as the price rises. The spread is "
               f"a Student's t with {value('liking_tail'):g} degrees of freedom: most shoppers sit near the typical liking, and a few "
               f"are far from it in either direction. The model's {value('liking_sd'):g} is fitted to the one choice experiment that "
               "estimated shoppers one by one and to the share that premium real meats hold at two to four times the ordinary price, "
               "together. 0 makes every shopper alike, as the model was before November 2026 (and then the share-at-equal-price "
               "setting has no effect)."),
        slider("cult_sub_mult", "How many times more price-sensitive than meat in general (&kappa;)", "x", 3.0, 12.0, 0.5,
               value("cult_sub_mult"), "Lusk 2020",
               tip="This is how many times more price-sensitive a cultivated product is than meat as a whole, because it "
               "has a near-identical substitute on the same shelf. It matters mostly above equal price. At "
               "one and a half times the price of meat, the share is ~{{KAPPA_LO}}% at 4, ~{{KAPPA_MID}}% at 8.5 and ~{{KAPPA_HI}}% at 10. "
               "The default 8.5 is the best fit to the shares that premium animal products (organic milk, eggs and chicken) "
               "take at their prices, within the range that Lusk 2020 measured (appendix A1). It changes nothing "
               "at equal price."),
        slider("loss_aversion", "Loss aversion (&lambda;)", "ratio", 1.0, 2.25, 0.05,
               value("loss_aversion"), "off by default",
               tip="This makes paying more than the conventional price hurt more than an equal discount helps. "
               "The default 1 is symmetric, and the slider goes up to Tversky and Kahneman's 2.25. It barely changes the result, "
               "because the model re-fits the price weight. At one and a half times the price of meat, the share is ~{{LAMBDA_1}}% at 1 and "
               "~{{LAMBDA_225}}% at 2.25."),
        slider("w_ratio", "Weight of the price-ratio term (<i>w</i><sub>r</sub>)", "points of score", 0.5, 1.5, 0.05,
               value("w_ratio"), "judgement",
               tip="This is how much of the price response compares each product with the conventional price "
               "(the same for rich and poor shoppers), rather than with the shopper's income. The model re-fits the price "
               "weight, so the US result does not change. A higher value makes poorer shoppers "
               "relatively less put off by a premium. That raises the share in poorer regions and in the "
               "world. There is no direct estimate, and 1 is the model's original value."),
        slider("income", "Income (<i>y</i>, GDP per person)", "$/yr", 5000, 5000000, 1000,
               value("income_ref"), "World Bank",
               tip="This is average income (PPP), set by the region selector. Poorer shoppers feel the same "
               "premium more, so they buy less of a pricier product. You can drag it far beyond the income of "
               "the richest country."),
        slider("income_gradient", "Income damping (&phi;)", "exp", 0.0, 1.0, 0.05,
               value("income_gradient"), "Muhammad / ERS",
               tip="This is how strongly income changes price sensitivity. A value of 1 is the raw economic form, which is too steep "
               "for food. The default 0.5 matches the roughly 2× rich-to-poor gap in food price sensitivity "
               "(Muhammad et al. 2011). A value of 0 means no income effect. US results do not depend on it."),
        slider("w_eth", "Ethical shoppers (<i>w</i><sub>eth</sub>)", "", 0.04, 0.10, 0.01,
               value("w_eth"), "Gallup",
               tip="This is the share of vegetarians and vegans, who strongly value “no slaughter” and mostly eat "
               "beans and other whole foods. The default is 5% (Gallup 2023). Moving it makes the model re-fit, so "
               "plant-based meat stays at its observed ~1.2%."),
        slider("health_x", "Cultivated health image (&zeta;<sub>x</sub>)", "points of score", -1.0, 1.0, 0.05,
               0.0, "scenario",
               tip="This is how healthy shoppers think cultivated meat is. A plus means “clean, no antibiotics”, and a minus means "
               "“lab-grown, ultra-processed”. The default is 0, because surveys find both views and they roughly "
               "cancel. The share at equal price is ~{{PARITY_NEUTRAL}}% at 0 and ~{{HX_05}}% at +0.5. The Monte Carlo samples ±0.5."),
        slider("neophobia_x", "Cultivated long-run novelty (&nu;<sub>x</sub>)", "points of score", -2.0, 1.0,
               0.1, value("neophobia_x"), "judgement",
               tip="This is where wariness of a new food settles once cultivated meat is familiar. A minus means a lasting “is it "
               "natural?” doubt, a plus means a lasting appeal, and the default 0 is neutral. The share at equal price is "
               "~{{NX_NEG1}}% at −1, ~{{PARITY_NEUTRAL}}% at 0 and ~{{NX_POS1}}% at +1. The Monte Carlo samples this slider."),
        # ---- step 2: plant-based meat --------------------------------------------------------
        slider("R_p", "Plant-based price (<i>R</i><sub>p</sub>)", "x", 0.2, 3.0, 0.05,
               value("price_pb_mult"), "GFI / NIQ",
               tip="This is plant-based meat's price relative to conventional meat. The default is 1.77× (+77%, GFI/NIQ). "
               "Set it to 1 to ask what happens if plant-based meat reached price parity."),
        slider("a_p", "Plant-based taste (<i>a</i><sub>p</sub>)", "", 0.4, 1.1, 0.05,
               round(1 + value("taste_quality_p"), 2), "NECTAR",
               tip="This is plant-based taste next to conventional meat, where 1 means as good. The default is 0.8, because only ~16% of "
               "products match conventional meat in blind tastings (NECTAR 2025)."),
        slider("real_tissue_p", "Plant-based seen as real meat (<i>b</i><sub>p</sub>)", "0→1", 0.0,
               1.0, 0.05, value("real_tissue_p"), "0 by definition",
               tip="This is the same premise for plant-based meat, which is not animal tissue (0). It is the only "
               "built-in difference between the two alternatives. Set it to 1 and plant-based meat rises to "
               "~{{BP_1_PB}}% at its current price."),
        slider("health_p", "Plant-based health image (&zeta;<sub>p</sub>)", "points of score", -1.0, 1.0, 0.05,
               0.0, "scenario",
               tip="This is how healthy shoppers think plant-based meat is. A plus means “good for you”, and a minus means "
               "“ultra-processed”. The default is 0. The Monte Carlo samples ±0.5."),
        slider("neophobia_p", "Plant-based long-run novelty (&nu;<sub>p</sub>)", "points of score", -2.0, 1.0,
               0.1, value("neophobia_p"), "scenario",
               tip="This is the lasting attitude toward plant-based meat as a new food. A minus means wary, a plus means drawn to it, and the "
               "default is 0. Its real resistance is already in the calibration, so this slider is a what-if."),
        # ---- step 3: premium products ---------------------------------------------------------
        slider("auth_premium_extra", "Penalty on a cultivated version of a premium product (&tau;<sub>prem</sub>)", "points of score", -3.0, 0.5,
               0.05, mm.AUTH_PREMIUM_EXTRA, "judgement", fmt="signed",
               tip="This is how much less a buyer of a luxury product (wagyu, sushi-grade fish) likes a cultivated version, on top of "
               "what applies to any cut, because the genuine article is part of what they pay for. It applies in full to a product "
               "priced at " + f"{mm.PREMIUM_FULL:g}" + " times its species' cheapest form or more, not at all below "
               + f"{mm.PREMIUM_START:g}" + " times, and in part between. The slider above (&rho;) "
               "scales it. There are no direct data."),
        # ---- step 4: over time ---------------------------------------------------------------
        slider("neophobia_x0", "Starting wariness of cultivated meat (&nu;<sub>x0</sub>)", "points of score", -3.5, 1.5, 0.1,
               value("neophobia_x0"), "Lusk / GFI",
               tip="This is how wary shoppers are of cultivated meat at launch, which is where the adoption curve starts. "
               "The default −2.8 matches a US experiment in which only ~5% chose lab-grown meat at the same price as "
               "beef (Van Loo, Caputo &amp; Lusk 2020). Warmer survey framings reach ~60% (about "
               "+{{NX0_60}}). The slider runs from −3.5 (~{{NX0_MIN}}%) to +1.5 (~{{NX0_WARM}}%). It changes the timing, "
               "not the long-run ceiling."),
        slider("accept_rate", "Familiarity speed (<i>r</i>)", "1/exp", 0.05, 0.50, 0.01,
               value("accept_rate"), "assumed",
               tip="This is how fast wariness fades as people keep seeing the product. It changes when adoption "
               "levels off, not where. For one product at equal price, the default 0.15 gives about year {{STAB_YEAR}}, 0.5 gives about year "
               "{{STAB_R05}} and 0.05 gives about year {{STAB_R005}}. Each is the year when adoption reaches 90% of its "
               "long-run share. There is no direct estimate. The default "
               "matches the decades-long uptake of other radically new foods. The Monte Carlo samples this slider."),
        slider("p_innov", "Rollout: early adopters (<i>p</i><sub>B</sub>)", "1/yr", 0.005, 0.05, 0.005,
               value("p_innov"), "Bass lit.",
               tip="This is how fast independent early adopters take it up (Bass diffusion). Together with word of mouth, "
               "it sets the speed of the S-curve, not its height. The default 0.02 is near the cross-study "
               "norm (0.01 to 0.03)."),
        slider("q_imit", "Rollout: word of mouth (<i>q</i><sub>B</sub>)", "1/yr", 0.20, 0.60, 0.05,
               value("q_imit"), "Bass lit.",
               tip="This is how fast existing buyers persuade new ones to buy (Bass diffusion). The default 0.40 is near the "
               "cross-study norm (0.3 to 0.5)."),
        slider("neophobia_p0", "Plant-based novelty at launch (&nu;<sub>p0</sub>)", "points of score", -2.0, 0.5,
               0.1, value("neophobia_p0"), "scenario",
               tip="This is plant-based meat's starting wariness (default −1), for the plant-based line in the chart of the path over time. It fades "
               "like cultivated meat's, yet plant-based meat stalls anyway, because its taste and price gaps do not fade."),
        # ---- entry points (which products first) ----------------------------------------------------------
        slider("phi", "Prestige share (&chi;)", "", 0.0, 0.95, 0.05, 0.25, "salmon / ibérico",
               tip="This is the share of a luxury market held by buyers who want the genuine article at any price. "
               "Cultivated meat cannot reach them (see the chart of which products it could enter first). The default 0.25 comes from the only two published "
               "splits, wild salmon (~25% of supply) and bellota ibérico (~20%). A value of 0 means all buyers are reachable."),
        # ---- expert: attribute weights (the multipliers in Eq. 2) -----------------------------
        # Normally FIXED (w_taste, w_slaughter_E, w_realtissue_E) or SOLVED to data (w_realtissue_M,
        # w_health_M, w_health_E). The three SOLVED ones carry solved=True + warn=...: they stay AUTO
        # (solved live) until you tick "override", which pins them and breaks the fact in the warning.
        slider("w_taste", "Taste weight (<i>w</i><sup>t</sup>)", "points of score", 1.0, 10.0, 0.5,
               value("w_taste"), "Malone &amp; Lusk 2017",
               tip="This is how much taste matters. It is the scale that every other weight is read against, because only "
               "differences between scores matter. The default 5 is anchored to willingness-to-pay studies "
               "that rank taste first (taste ≈ 2× health, 3× safety). Changing it re-fits the other weights."),
        slider("w_realtissue_M", "Mainstream real-meat weight (<i>w</i><sup>rt</sup><sub>M</sub>)",
               "points of score", 0.0, 6.0, 0.05, round(dp.w_realtissue_M, 2), "solved",
               tip="This is how much mainstream shoppers value real animal tissue. It is why cultivated meat takes buyers "
               "from conventional meat rather than from plant-based meat. The model solves it so that ~89% of plant-based buyers "
               "are mainstream (GFI 2024). Override it to set your own value, and the model then stops matching that "
               "fact."),
        slider("w_health_M", "Mainstream health weight (<i>w</i><sup>h</sup><sub>M</sub>)", "points of score",
               0.0, 4.0, 0.05, round(dp.w_health_M, 2), "solved",
               tip="This is how much mainstream shoppers weigh health. It pushes them toward beans and away from a veggie burger. "
               "The model solves it so that ~6% of mainstream meals skip meat by choice. It comes out at "
               "{{HEALTH_TASTE_RATIO}}× the taste weight, which is lighter than the ~0.5× in willingness-to-pay "
               "studies. Override it to set your own value."),
        slider("w_health_E", "Ethical health weight (<i>w</i><sup>h</sup><sub>E</sub>)", "points of score", 0.0,
               6.0, 0.05, round(dp.w_health_E, 2), "solved",
               tip="This is the ethical shoppers' health weight. The model solves it (~{{HEALTH_E}}) so that a 5% ethical "
               "group adds only a little to plant-based meat, because most of them choose beans. Override it to set "
               "your own value, and plant-based meat then moves away from its ~1.2%."),
        slider("w_slaughter_E", "Ethical no-slaughter weight (<i>w</i><sup>s</sup><sub>E</sub>)",
               "points of score", 1.0, 8.0, 0.5, value("w_slaughter_E"), "assumed",
               tip="This is how strongly the 5% ethical shoppers value “no animal killed” (default 4, assumed). "
               "It gives cultivated meat a small ethical niche even above parity. The calibration re-fits around "
               "it."),
        slider("w_realtissue_E", "Ethical real-meat weight (<i>w</i><sup>rt</sup><sub>E</sub>)",
               "points of score", 0.0, 4.0, 0.05, value("w_realtissue_E"), "assumed ≈ 0",
               tip="This is how much ethical shoppers value real animal tissue. The model assumes about 0, because they choose on "
               "“no slaughter”, not on “is it meat”. Raising it makes them favour both real meats, which "
               "helps cultivated meat a little (they are 5% of shoppers)."),
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
              "w_health_M", "w_health_E", "auth_premium_extra"}
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
                if _gname == HIDDEN_GROUP:
                    _by_key[_k]["hidden"] = True
                _grouped.append(_by_key.pop(_k))
    if _by_key:                                   # every slider must be placed in exactly one group
        raise RuntimeError(f"sliders missing from SLIDER_GROUPS: {sorted(_by_key)}")
    sliders = _grouped

    toggles = [
        dict(key="cleanroom", label="Add Humbird's clean-room cost (to <i>h</i>)",
             add=value("cleanroom_cost"),
             group=HIDDEN_GROUP, hidden=True,   # it adds to the plant running cost h of the reported process
             tip="Adds Humbird's cost for clean-room, pharma-style buildings (about +$" +
             ("%.0f" % value("cleanroom_cost")) + "/kg). The default is a company's figure for a "
             "food-grade facility."),
    ]

    markets = {
        region: [dict(name=mt.name, p_conv=mt.p_conv, w_vol=mt.w_vol,
                      structured=(mt.scaffold > 0), cost_mult=mt.cost_mult)
                 for mt in market]
        for region, market in mm.MARKETS.items()
    }
    regions = [list(r) for r in REGION_NAMES]
    # The cost sliders (medium price, cell efficiency, plant running cost) describe the process one company
    # reports; the page's cost scenarios (scenarios.py) set the cost in every other case.
    for sl in sliders:
        sl["start"] = sl["default"]
    import scenarios
    import vessels
    return dict(const=const, sliders=sliders, toggles=toggles, markets=markets, regions=regions,
                sc=_plain_switch_words(scenarios.js_model()), vm=vessels.js_model(), page=page_data())


# ---------------------------------------------------------------------------
# Python cross-check: recompute the reference numbers with the SAME formulas we
# inject, to confirm the constants/markets are the ones the model uses.
# ---------------------------------------------------------------------------
def crosscheck(model: dict) -> None:
    from market_share import DemandParams, share
    from cost_model import CostParams, biomass_cost
    cp = CostParams()
    R = shelf_price(biomass_cost(cp, value("media_price"), 1.0)) / value("p_conv")
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
    # --- the price coefficients beta (logit slope) and alpha (BLP constant), as market_share._derive_beta sets them ---
    # beta = eps * kappa_base / (p_x (1 - s_x)) + w_ratio * lambda / p_c, with s_x the share at the calibration price in the
    # model without the spread of liking (the fixed point _derive_beta solves). s_x is read back from that identity here, so
    # the printed arithmetic reproduces beta by construction.
    eps, kb = dp.eps_own, value("kappa_base")
    eps_x = kb * eps                                           # the own-price elasticity TARGET at the calibration price
    p_x, p_c, lam, y = dp.anchor_price, dp.p_conv, dp.w_ratio * dp.loss_aversion, dp.income_ref
    beta = dp.beta_ref
    s_x = 1.0 - eps_x / (p_x * (beta - lam / p_c))
    alpha = -beta * (y - p_x)
    price_row = (
        '<tr><td>price</td><td style="white-space:nowrap">&alpha;, &beta;</td>'
        f'<td class="n" colspan="2">&beta; = {beta:.3f}<br>&alpha; = {alpha:,.0f}'
        '<br><span class="small">(shared by both)</span></td>'
        '<td class="s"><b>DERIVED</b> from the price-sensitivity target at the calibration price, '
        f'{kb:g}&times;({eps:g}) = <b>{eps_x:.1f}</b> (A1), at the calibration '
        f'price p<sub>x</sub> = ${p_x:.0f}/kg and the share s<sub>x</sub> = {s_x*100:.0f}% that the model gives there before the spread '
        f'of liking: &beta; = {eps_x:.1f}/[p<sub>x</sub>(1&minus;s<sub>x</sub>)] + &lambda;/p<sub>c</sub> = '
        f'{eps_x:.1f}/[{p_x:.0f}&middot;{1-s_x:.2f}] + {lam:g}/{p_c:.0f} = <b>{beta:.3f}</b>; then '
        f'&alpha; = &minus;&beta;(y<sub>ref</sub>&minus;p<sub>x</sub>) = <b>{alpha:,.0f}</b> (large only because '
        'differences in log income are tiny). p<sub>x</sub> is a fixed calibration price (A1). Cultivated meat&rsquo;s own price gap '
        f'then counts {dp.cult_sub_mult:g}/{kb:g} times as much again. The cases&rsquo; costs change cultivated meat&rsquo;s price but not this '
        'calibration point.</td></tr>'
    )
    rows = [
        price_row,
        row("taste", "w<sup>t</sup>", f"{dp.w_taste:.2f}", f"{dp.w_taste:.2f}",
            '<b>FIXED</b> scale. Only differences between scores matter, so taste sets the scale for every other '
            'weight (anchored to willingness-to-pay studies). It is among the expert settings.'),
        row("no slaughter", "w<sup>s</sup>", f"{dp.theta_free_M:.2f}", f"{dp.w_slaughter_E:.1f}",
            'Mainstream: <b>A SETTING</b> (&theta;, 0 in the model). Ethical: <b>FIXED</b> assumption. It is large, because it '
            'defines the ethical shopper.'),
        row("real meat", "w<sup>rt</sup>", f"{dp.w_realtissue_M:.2f}", f"{dp.w_realtissue_E:.2f}",
            'Mainstream: <b>SOLVED</b> so that ~89% of plant-based buyers are mainstream. Ethical: <b>FIXED</b> '
            'at about 0, because they choose on &ldquo;no slaughter&rdquo;, not &ldquo;is it meat&rdquo;.'),
        row("health", "w<sup>h</sup>", f"{dp.w_health_M:.2f}", f"{dp.w_health_E:.2f}",
            'Both <b>SOLVED</b>, from the mainstream meatless rate (~6%) and the ethical shoppers&rsquo; plant-based '
            'share.'),
        row("loss aversion", "&lambda;", f"{dp.loss_aversion:.2f}", f"{dp.loss_aversion:.2f}",
            '<b>A SETTING</b>, 1 = symmetric in the model (A3)'),
        row("segment mix", "w<sub>eth</sub>", "&mdash;", f"{dp.w_eth*100:.0f}%",
            '<b>A SETTING</b> (Gallup: 5% vegetarian or vegan). Moving it re-solves the calibration.'),
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
    """Return {TOKEN: "NN"} for every illustrative share quoted in the prose/tooltips. Shares of 1% or more are whole
    percents; smaller ones keep the decimals scenarios.pct_num gives, so no nonzero share prints as 0."""
    from market_share import DemandParams, share
    import scenarios as S

    base = DemandParams()                                     # central calibration
    R_ILLUS = 1.5                                             # "one and a half times the price of meat": the worked examples' price

    def pc(x):                                                # share as text: whole percent from 1%, pct_num's decimals below
        return f"{round(x * 100)}" if x >= 0.00995 else S.pct_num(x * 100)

    def at_parity(**kw):                                      # cultivated share at R=1, central calib
        return share(1.0, base, **kw)

    def resolved(R, **dp_kwargs):                             # re-solve calibration, then share at R
        return share(R, DemandParams(**dp_kwargs), accept_x=1.0, theta_free_M=0.0)

    from adoption_timing import TimingParams, simulate
    traj = simulate(1.0, base, TimingParams(), acceptance_grows=True, which="x")["share"]     # one product held at the price of meat
    from dataclasses import replace as _replace
    from market_share import _segment
    pbp = _replace(base, price_pb_mult=1.0, taste_quality_p=0.0)   # keeps the solved weights (no re-solve)
    pd = page_data()
    cband = pd["region_bands"]["central"]
    world = mm.MARKETS["global"]
    sea = sum(t.w_vol for t in world if t.name.startswith("seafood")) / sum(t.w_vol for t in world)
    bands_c = S.bands(S.SCENARIOS["central"].choice)
    R_central = shelf_price(bands_c["cost"][1]) / value("p_conv")
    lo5, hi95 = _lognormal_5_95("equal_price_share")

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
        # cultivated's health image, at parity
        "HX_05": pc(at_parity(health_x=0.5)),
        # long-run novelty ladder (neophobia_x), at parity
        "NX_NEG1": pc(at_parity(accept_x=1.0, theta_free_M=0.0, neophobia_x=-1.0)),
        "NX_POS1": pc(at_parity(accept_x=1.0, theta_free_M=0.0, neophobia_x=1.0)),
        # nu_x0 framing band (static-share proxy at that novelty level), at parity
        "NX0_NEUTRAL": pc(at_parity(accept_x=1.0, theta_free_M=0.0, neophobia_x=0.0)),
        "NX0_WARM": pc(at_parity(accept_x=1.0, theta_free_M=0.0, neophobia_x=1.5)),
        # plant-based with b_p=1 (credited as real meat) at ITS current price — the equal-footing what-if
        "BP_1_PB": pc(share(1.0, DemandParams(real_tissue_p=1.0), cultivated_present=False, which="pb")),
        # price-sensitivity (kappa) ladder, re-solved, at one and a half times the price of meat
        "KAPPA_LO": pc(resolved(R_ILLUS, cult_sub_mult=4.0)),
        "KAPPA_MID": pc(resolved(R_ILLUS, cult_sub_mult=8.5)),
        "KAPPA_HI": pc(resolved(R_ILLUS, cult_sub_mult=10.0)),
        # loss-aversion (lambda) ladder, re-solved, at the same price
        "LAMBDA_1": pc(resolved(R_ILLUS, loss_aversion=1.0)),
        "LAMBDA_225": pc(resolved(R_ILLUS, loss_aversion=2.25)),
        # below the price of meat: the spread of liking leaves most shoppers out at any price
        "HALF_PRICE": pc(share(0.5, base)), "FREE_PRICE": pc(share(0.0, base)), "NEVER_BUY": f"{100 - round(share(0.0, base) * 100)}",
        "COLD_PARITY": pc(at_parity(neophobia_x=value("neophobia_x0"))),   # first contact, equal price
        "CONV_PARITY": pc(share(1.0, base, which="c")),               # conventional's share at parity
        "NX0_MIN": pc(at_parity(neophobia_x=-3.5)),                   # the novelty slider's cold end
        # income: the same product at one and a half times the price of meat, by region's income
        "SHARE_15_US": pc(share(R_ILLUS, base)),
        "SHARE_15_CHINA": pc(share(R_ILLUS, base, income=mm.REGION_INCOME["china"])),
        "SHARE_15_NIGERIA": pc(share(R_ILLUS, base, income=mm.REGION_INCOME["nigeria"])),
        "INCOME_CAP": pc(share(R_ILLUS, base, income=5_000_000)),     # a very rich buyer, the same price
        # a US shopper at the Central case's shop price (the median cost), long run
        "SHARE_AT_R_CENTRAL": pc(share(R_central, base)),
        # the timing path of one product held at the price of meat (US)
        "Y10_SHARE": pc(traj[10]), "Y30_SHARE": pc(traj[-1]),
        # plant-based at full price+taste parity, mainstream, calibration held (self-check [5])
        "PB_PARITY": pc(_segment(1.0, pbp, pbp.beta_price, "M", accept_x=1.0, theta_free_M=0.0,
                                 tier_offset=0.0, neophobia_x=0.0, neophobia_p=0.0, income=pbp.income_ref,
                                 cultivated_present=False)["p"]),
        # the share at equal price: the best case's setting and the middle nine tenths of the central draws
        "BEST_EQS": pc(value("best_equal_price_share")), "EQS_P05": pc(lo5), "EQS_P95": pc(hi95),
        # the Central case's median share by region (the same draws as the world band)
        "CENTRAL_US_P50": S.pct_num(cband["us"][1]), "CENTRAL_EU_P50": S.pct_num(cband["eu"][1]),
        "CENTRAL_CHINA_P50": S.pct_num(cband["china"][1]),
        "SEAFOOD_PCT": f"{sea * 100:.0f}",
    }
    return {f"{{{{{k}}}}}": v for k, v in N.items()}


# Plain-language meaning of every cost case on the page: what it is, where it comes from, and whether
# anyone has done it. Keys are floor_physics tier names; the two non-tier rows are added in _cost_cases_table.
_CASE_TEXT = {
    "Humbird fed-batch, as designed": (
        "Humbird's fed-batch design",
        "This is a detailed engineering design [2] with twenty-four 20,000-litre stirred tanks in a food-grade plant. Each tank is "
        "filled, the cells grow for about two days, and then the tank is emptied (&ldquo;fed-batch&rdquo;). The cells are efficient, and "
        "growth factors are bought.",
        "Designed on paper. Nobody has built it."),
    "Humbird perfusion, as designed": (
        "Humbird's perfusion design",
        "This comes from the same study [2]. It has ninety-six 2,000-litre tanks. Filters hold the cells back while fresh "
        "medium flows through (&ldquo;perfusion&rdquo;). The cultures are denser, but the plant needs many small tanks and many filters.",
        "Pharma uses perfusion at this size. Nobody has built this plant."),
    "Same fed-batch plant, small slow cells": (
        "The fed-batch design with small, slow cells",
        "This is Humbird's fed-batch plant growing cells like those in the one peer-reviewed measured run [20]. They are six times "
        "smaller and double every 61 hours, not 24. The row shows how much the cells themselves matter.",
        "Such cells exist. This plant does not."),
    "Pharma-style plant, half the density": (
        "A pharma-style plant with clean rooms, cells at half the density",
        "This is the next row, but with 60 g of cells per litre, not 120. Reported harvests from a "
        "20,000-litre tank imply about 27 g per litre.",
        "Closer to what has been reported"),
    "Pharma-style plant, fill-and-draw": (
        "A pharma-style plant with clean rooms, tanks drained and refilled",
        "This is Humbird's pharma-style plant with clean rooms. The 20,000-litre tanks are never emptied. Each cycle, half the tank is drained and "
        "refilled (&ldquo;fill-and-draw&rdquo;), nothing holds the cells back, and the tank "
        "produces for 85% of the year. The cells are efficient, at 120 g per litre.",
        "Fill-and-draw has been filed as an option at 20,000 litres. Nobody has shown this density."),
    "No clean rooms, fill-and-draw": (
        "A food-grade plant, tanks drained and refilled",
        "This is the same culture, still free of contaminants, in a food-grade building. It is Humbird's plant with an ordinary "
        "hall in place of the clean room. That saves about a tenth of the plant's cost.",
        "Food-grade 20,000-litre tanks are in use. Nobody has shown this density."),
    "No clean rooms, perfusion": (
        "A food-grade plant, perfusion <b>(Humbird's optimistic design)</b>",
        "This combines everything that has been costed for animal cells. The plant is food-grade. Fresh "
        "medium flows through 20,000-litre tanks while a hollow-fibre filter holds the cells back (&ldquo;perfusion&rdquo;). "
        "The culture stays at 120 g per litre, the most such a tank can clear of CO&#8322;. The cells are efficient, "
        "the medium costs $0.15 a litre, and the tank produces for 91% of the year. The filter's membranes and a protectant "
        "against bubble damage are counted.",
        "Each piece has been shown or claimed somewhere, but never together. No device yet holds cells back at this size."),
    "Microbial-fermentation-class plant": (
        "A plant as cheap as microbial fermentation plants (no case assumes it)",
        "This is Humbird's optimistic design in a plant that costs what plants for yeast and other microbes cost. Such a plant costs "
        "about a quarter as much per litre of tank and has much larger vessels. It buys its oxygen. Bacteria double in 20 minutes and "
        "animal cells in a day or two, so animal cells are far easier to contaminate.",
        "Such plants exist for microbes. Nobody has built or costed one for animal cells."),
}


def _familiar_elasticity(dp, R: float, h: float = 1e-5) -> float:
    """Own-price elasticity of cultivated's share at price ratio R once shoppers are familiar with it."""
    from market_share import share as _share
    f = lambda r: _share(r, dp, accept_x=1.0, theta_free_M=0.0, neophobia_x=0.0)
    return (f(R * (1 + h)) - f(R * (1 - h))) / (2 * h * f(R))


def _floor_mc_tokens(parity: float) -> dict:
    """Percentiles of the floor case when its own inputs are uncertain (floor_physics.floor_mc)."""
    import numpy as np
    t = floor_physics.floor_mc()["total"]
    y = floor_physics.floor_mc(plant="microbial")["total"]
    q = lambda a, k: f"{np.percentile(a, k):.0f}"
    # cost and demand uncertain together at the reference case (meat_market.floor_share_mc), world, by volume
    sh = mm.floor_share_mc("global", 2000)["vol"]
    shy = mm.floor_share_mc("global", 2000, plant="microbial")["vol"]
    f1 = lambda a, k: f"{np.percentile(a, k):.1f}"
    return {"FLOOR_MC_P10": q(t, 10), "FLOOR_MC_P50": q(t, 50), "FLOOR_MC_P90": q(t, 90),
            "FLOOR_MC_YEAST_P50": q(y, 50), "FLOOR_MC_YEAST_PARITY": f"{np.mean(y <= parity) * 100:.0f}",
            "FLOOR_SHARE_MC_P10": f1(sh, 10), "FLOOR_SHARE_MC_P50": f1(sh, 50), "FLOOR_SHARE_MC_P90": f1(sh, 90),
            "FLOOR_SHARE_MC_YEAST_P50": f1(shy, 50)}


def _cost_cases_table(bio: float, markup: float, p_conv: float) -> str:
    """HTML rows for the 'what each cost case means' table: every case the page quotes, in plain words."""
    def row(name, what, shown, cost, mature, hl=False):
        cell = lambda c: f'<td class="n">${c:.0f} ({shelf_price(c, markup) / p_conv:.1f}&times;)</td>'
        return (f'<tr{" class=\"hl\"" if hl else ""}><td>{name}</td><td class="s">{what}</td><td class="s">{shown}</td>'
                f'{cell(cost)}{cell(mature)}</tr>')
    # the default's capital is $35 per kg of yearly output (inputs.py `overhead`): the two rates differ on that
    bio_mature = bio - 35.0 * (value("humbird_plant_charge") - value("plant_charge_mature"))
    rows = [
        row("As a company reports, with a yearly charge on its plant",
            "SuperMeat's 2024 report [1] describes chicken cells in perfusion at 10 litres for 45 days, scaled up on paper to "
            "25,000-litre tanks. It uses 30.5 litres of medium per kilo at $0.50 a litre. The cost adds the company's running costs and a "
            "yearly charge on the plant, at the same rate as every other row. The company's own figure, with "
            "depreciation only, is about $29.5.",
            "The company has done 10-litre runs, and nobody has peer reviewed them. Nobody has built the plant.", bio, bio_mature),
    ]
    for t in floor_physics.tiers():
        if t["name"] not in _CASE_TEXT:           # the "rough lower bound" is not a design, and the page no longer shows it
            continue
        name, what, shown = _CASE_TEXT[t["name"]]
        rows.append(row(name, what, shown, t["total"], t["total_mature"]))
    return "\n        ".join(rows)


def _scenario_tokens() -> dict:
    """Numbers for the prose about the cases (scenarios.py): costs, price ratios, shares and bands."""
    import scenarios as S
    import page_sections as ps
    out = {}
    for key, tag in (("today", "TODAY"), ("process", "PROCESS"), ("central", "CENTRAL"), ("best", "BEST")):
        choice = S.SCENARIOS[key].choice
        r = S.run(choice)
        if key != "process":
            b = ps.bands(key)
            out[f"COST_{tag}"] = f"{r['total']:.1f}"                      # every estimate at its most likely value
            out[f"MEDIUM_L_{tag}"] = f"{r['medium_l']:.0f}"
            for i, q in enumerate(("P10", "P50", "P90")):
                out[f"{tag}_COST_{q}"] = f"{b['cost'][i]:.0f}"
        if key in ("best", "central"):
            out[f"R_{tag}"] = f"{shelf_price(b['cost'][1]) / value('p_conv'):.1f}"     # the shop price at the median cost
            for i, q in enumerate(("P10", "P50", "P90")):
                out[f"{tag}_SHARE_{q}"] = S.pct_num(b['share'][i])
        if key == "central":
            import audit as AU                    # the shelf price under the three markup rules (research_notes/retail_markup_form.md)
            out["RETAIL_CENTRAL"] = f"{AU.retail(r['total']):.0f}"
            out["RETAIL_CENTRAL_FLAT"] = f"{AU.retail(r['total'], 'flat'):.0f}"
            out["RETAIL_CENTRAL_PROP"] = f"{AU.retail(r['total'], 'proportional'):.0f}"
        if key in ("process", "central", "best"):
            tr = S.tricks_report(choice)
            out[f"TRICKS_{tag}_NO"] = f"{tr['no_tricks']:.1f}"
            out[f"TRICKS_{tag}_ORD"] = f"{tr['ordinary_tank']:.1f}"
            out[f"TRICKS_{tag}_LIST"] = S.plain_list(tr["used"])
    sb = ps.bands("today")["share"]
    out["TODAY_SHARE_SENTENCE"] = (
        "With the published cells it is under 0.001% in at least 9 draws in 10." if sb[2] < 0.00095 else
        f"With the published cells the median is {S.pct_num(sb[1])}% (8 in 10 draws between {S.pct_num(sb[0])}% and {S.pct_num(sb[2])}%).")
    out["NH3_LIMIT"] = f"{value('sc_nh3_limit'):g}"
    return out


def derived_numbers() -> dict:
    """Return {TOKEN: text} for every NON-share model number the prose quotes (price ratios, $/kg,
    years, coefficients). Same discipline as illustrative_numbers() (which holds the %-shares):
    computed from the live model at build time, so the text cannot drift from the model."""
    import numpy as np
    import uncertainty as U
    from market_share import DemandParams, share
    from cost_model import CostParams, biomass_cost, cost_floor, media_cost
    from adoption_timing import TimingParams, years_to_stabilize
    from market_share import organic_premium_check

    cp, dp = CostParams(), DemandParams()
    p_conv, markup = value("p_conv"), value("markup_add")
    media = float(media_cost(cp, value("media_price"), value("efficiency")))
    bio = float(biomass_cost(cp, value("media_price"), value("efficiency")))
    R_today = shelf_price(bio) / p_conv
    floor = float(cost_floor(cp))

    _org = organic_premium_check(dp)                          # premium real-meat check (organic chicken)

    def stab(**kw):                                           # year one product held at the price of meat reaches 90% of its long-run share
        return int(years_to_stabilize(1.0, dp, TimingParams(**kw)))

    lo, hi = -3.0, 3.0                                        # novelty at which the parity share is 60%
    for _ in range(60):                                       # (the warmest survey framing, Perdue 2024)
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if share(1.0, dp, neophobia_x=mid) < 0.60 else (lo, mid)

    N = {
        "R_TODAY": f"{R_today:.1f}",
        "MEDIA_TODAY": f"{media:.0f}",
        "BIOMASS_TODAY": f"{bio:.0f}",
        "RETAIL_TODAY": f"{shelf_price(bio):.0f}",
        "CUT_RETAIL_TODAY": f"{shelf_price(structured_cost(bio)):.0f}",
        "PCONV": f"{p_conv:.0f}",
        "MARKUP": f"{markup:.1f}",
        "CUT_CELLS_PCT": f"{mm.CUT_CELL_SHARE * 100:.0f}",
        # how much less shoppers like a cut than mince (meat_market.tier_offset): the blend penalty at the default cell share, and
        # the premium penalty's size and price range
        "BLEND_OFFSET": f"\u2212{(1 - mm.CUT_CELL_SHARE) * dp.w_realtissue_M:.2f}",
        "PREMIUM_EXTRA": f"\u2212{abs(mm.AUTH_PREMIUM_EXTRA):g}",
        "PREMIUM_START": f"{mm.PREMIUM_START:g}", "PREMIUM_FULL": f"{mm.PREMIUM_FULL:g}", "PREMIUM_RATIO": f"{mm.PREMIUM_RATIO:g}",
        "SCAF": f"{mm.SCAF:.0f}",
        "MARGIN_PCT": f"{value('retail_margin') * 100:.0f}",
        "PARITY_BIOMASS": f"{cost_from_shelf(p_conv):.1f}",
        "COST_FLOOR": f"{floor:.1f}",
        "FEEDSTOCK_FLOOR": f"{AA_FLOOR + GLUCOSE_OTHER_FLOOR:.1f}",
        "PLANT_FLOOR": f"{value('plant_floor'):.1f}",
        "ANCHOR_PRICE": f"{value('elasticity_anchor_price'):.0f}",
        "COST_CASES_ROWS": _cost_cases_table(bio, markup, p_conv),
        "PLANT_FLOOR_LO": f"{value('plant_floor_lo'):.1f}",
        "MATURE_CHARGE_PCT": f"{value('plant_charge_mature') * 100:.1f}",
        "COST_FLOOR_FIRST": f"{[t for t in floor_physics.tiers() if t['name'] == 'No clean rooms, perfusion'][0]['total']:.0f}",
        "COST_FLOOR_LO": f"{AA_FLOOR + GLUCOSE_OTHER_FLOOR + value('plant_floor_lo'):.1f}",
        "COST_FLOOR_HI": f"{AA_FLOOR + GLUCOSE_OTHER_FLOOR + value('plant_floor_hi'):.0f}",
        "OH_DEF": f"{_plant_oh('as reported'):.1f}", "OH_FLOOR": f"{_plant_oh('reference plant'):.1f}",
        "OH_HI": f"{_plant_oh('cautious'):.0f}",
        "MEDIA_L": f"{value('media_intensity'):.1f}", "MEDIA_P": f"{value('media_price'):.2f}",
        "HUMBIRD_CHARGE_PCT": f"{value('humbird_plant_charge') * 100:.1f}",
        "HUMBIRD_PLANT": f"{value('humbird_plant_cost'):.1f}",
        "STAB_YEAR": str(stab()), "STAB_R05": str(stab(accept_rate=0.5)), "STAB_R005": str(stab(accept_rate=0.05)),
        "ORG_CUTS": f"{_org['vs_cuts']:.0f}", "ORG_MINCE": f"{_org['vs_mince']:.0f}",
        "NX0_60": f"{(lo + hi) / 2:.1f}",
        "HEALTH_TASTE_RATIO": f"{dp.w_health_M / dp.w_taste:.2f}",
        "HEALTH_E": f"{dp.w_health_E:.1f}",
        "MEDIA_PER_010": f"{value('media_intensity') * 0.10:.1f}",
        # the kappa-validation elasticity (golden-guarded as lusk_elas_parity_cold)
        "KAPPA4_LUSK_ELAS": f"{_lusk_at_parity(dp):.1f}",
        "LIKING_SD": f"{value('liking_sd'):g}", "LIKING_TAIL": f"{value('liking_tail'):g}",
        "DO_IMPLIED": f"{__import__('gas_exchange').headspace_pressure()['c_liquid_implied']:.3f}",
        **_scenario_tokens(),
        "TANK_NOTE": _tank_note(),
        "OTHER_ESTIMATES_HTML": _other_estimates_html(),
        "HOW_MET_HTML": _how_met_html(),
        "GRID_HTML": _cells_by_tank_html(),
        "VESSELS_HTML": _vessels_html(),
        "BACKTEST_HTML": __import__("page_sections").backtest_table(),
        "INDUSTRY_HTML": _industry_html(),
        "MEASURED_HTML": _measured_html(),
        **{f"ELAS_{tag}": f"{_familiar_elasticity(dp, R):.1f}".replace("-", "\u2212")
           for tag, R in (("10", 1.0), ("15", 1.5), ("24", 2.42))},
    }
    return {f"{{{{{k}}}}}": v for k, v in N.items()}


# ---------------------------------------------------------------------------
# The page's own data and generated sections (rebuild of 2026-11-19). One case selector drives the page: three named
# cases (CASE_KEYS) plus the reader's own settings. Everything here is computed from the model at build time; the only
# typed-in figures are the author's stated odds (ODDS), which are judgements quoted from RESULTS.md and inputs.py.
# ---------------------------------------------------------------------------
CASE_KEYS = ("today", "central", "best")
CASE_LABELS = {"today": "Published cells", "central": "Central case", "best": "Best case"}
OWN_LABEL = "Your own settings"
REGION_NAMES = [["global", "World"], ["us", "United States"], ["eu", "Europe"], ["china", "China"], ["brazil", "Brazil"],
                ["india", "India"], ["nigeria", "Nigeria"]]

# The author's odds, as the repo states them (RESULTS.md, "The forecast for 2035"; inputs.py notes on sc_td_central and
# vm_perf_max_m3). tests/test_easy_view.py checks that each figure is still in RESULTS.md or inputs.py.
ODDS = {
    "engineered": ("Engineered low-waste cell lines in production by 2035", "about 25%"),
    "h24": ("Low-waste cells that double every 24 hours", "about 10%"),
    "h36": ("Low-waste cells that double every 36 hours or faster", "about 45%"),
    "plant": ("A food-grade plant with shared medium at or below the cost assumed", "about 65%"),
    "gas6": ("Gas at 6 mm a second working in a 20 m³ tank", "about even"),
    "column": ("Cells working on a column that strips CO₂", "60%"),
    "pressure": ("Cultures at 2 bar absolute", "85%"),
    "gf": ("Announced medium prices already include growth factors", "about 85%"),
    "perf20": ("Anyone having yet run animal cells in perfusion at 20 m³ for a month", "2 to 3%"),
}


def _odds_html(keys) -> str:
    return ("<p><b>The author's odds.</b> These are judgements, not measurements, and are for 2035 unless they say otherwise. "
            + " ".join(f"{ODDS[k][0]}: {ODDS[k][1]}." for k in keys) + "</p>")


def _money(v: float, d: int = 1) -> str:
    return f"${v:.{d}f}"


_PAGE_DATA: dict = {}


def _region_band(job) -> tuple:
    """10th / 50th / 90th percentile of a case's long-run share in one region, cost and demand both drawn (a worker for page_data)."""
    import numpy as np
    key, region, cost, eqs, n = job
    mc = mm.monte_carlo(region, n, seed=1, biomass=cost, equal_share_input=eqs)
    return key, region, [float(x) for x in np.percentile(mc["vol"], [10, 50, 90])]


def _region_bands_side_by_side(jobs: list) -> list:
    """Run _region_band for every job in a few separate Python processes. Each worker is started with its own short
    program (it imports this module and nothing of the caller's), so it does not matter what script called the build."""
    import pickle
    import subprocess
    import sys
    code = ("import sys, pickle, json; sys.path.insert(0, %r); import build_interactive as B; "
            "jobs = pickle.load(sys.stdin.buffer); print(json.dumps([B._region_band(j) for j in jobs]))" % HERE)
    n = max(1, min(6, os.cpu_count() or 1))
    chunks = [c for c in (jobs[i::n] for i in range(n)) if c]
    procs = [subprocess.Popen([sys.executable, "-c", code], stdin=subprocess.PIPE, stdout=subprocess.PIPE, cwd=HERE) for _c in chunks]
    for p, c in zip(procs, chunks):
        p.stdin.write(pickle.dumps(c))
        p.stdin.close()
    out = []
    for p in procs:
        data = p.stdout.read().decode("utf-8")
        if p.wait() != 0:
            raise RuntimeError("a worker failed")
        out += [tuple(x) for x in json.loads(data.strip().splitlines()[-1])]
    return out


def page_data() -> dict:
    """What the first screen and Levels 1 to 3 need beyond the scenario engine: the three cases in plain words, the
    regional bands, the ladder, the estimates and shopper judgements Level 2 moves, and the ranges it moves them over."""
    if _PAGE_DATA:
        return _PAGE_DATA
    import numpy as np
    import scenarios as S
    import answer_rests_on as AR

    def kw(key):
        return S.explore_kwargs(S.SCENARIOS[key].choice)

    def hours(key):
        return f"{kw(key)['doubling_h']:.0f}"

    perf_max, tank = value("vm_perf_max_m3"), value("vm_str_m3")
    eqs_c, eqs_b = value("equal_price_share"), value("best_equal_price_share")
    r = {k: S.run(S.SCENARIOS[k].choice) for k in CASE_KEYS}
    tr = {k: S.tricks_report(S.SCENARIOS[k].choice) for k in CASE_KEYS}
    med = lambda k: S.MEDIUM_PLAIN.get(r[k]["medium_set_by"], r[k]["medium_set_by"])
    texts = {
        "today": (
            f"<p><b>What it assumes.</b> The best meat cells in the published record: cattle cells fed without glutamine, which "
            f"double every {hours('today')} hours and turn most of their glucose into lactate (Hubalek 2023). Companies may hold "
            f"better cells that they have not shown. The plant is food-grade. The tank is an ordinary stirred tank of {tank:.0f} "
            f"cubic metres, run in perfusion with no more gas than anyone has run. Medium costs "
            f"{_money(kw('today')['medium_price'], 2)} a litre, with growth factors in that price, as companies report today.</p>"
            f"<p><b>What has to go right.</b> Nothing new in the cells. But nobody has run animal cells in perfusion above about "
            f"{perf_max:.0f} cubic metres, and no device yet holds cells back at this size.</p>"
            f"<p><b>Why it is dear.</b> Each kilo of cells needs about {r['today']['medium_l']:.0f} litres of medium, set by "
            f"{med('today')}. The filter that holds the cells back is paid for by the litre, so its cost grows with the medium.</p>"
            + _odds_html(("perf20",))),
        "central": (
            f"<p><b>What it assumes.</b> The same low-ammonia feed, with cells selected on it until they double every "
            f"{hours('central')} hours and make less lactate. No genetic engineering. A food-grade plant. Medium at "
            f"{_money(kw('central')['medium_price'], 2)} a litre, the price companies announced, with growth factors in that price. "
            f"The tank uses {S.plain_list(tr['central']['used'])}. A run is lost on {kw('central')['hazard'] * 100:.0f}% of days, and "
            f"the tank is back after {kw('central')['restart_fail_days']:.0f} days. Each kilo of cells needs about "
            f"{r['central']['medium_l']:.0f} litres of medium, set by {med('central')}.</p>"
            f"<p><b>What has to go right.</b> Selection must win back speed without bringing the waste back. Each has been shown "
            f"alone, never both in one culture. The column and the pressure are calculated, not measured: without them a kilo costs "
            f"{_money(tr['central']['no_tricks'])} at its most likely values, {_money(tr['central']['d_no_tricks'])} more. The announced "
            f"medium price must hold at scale, and something must hold the cells back in a {tank:.0f} cubic metre tank.</p>"
            + _odds_html(("h36", "column", "pressure", "gf"))),
        "best": (
            f"<p><b>What it assumes.</b> Cells engineered to make almost no waste. They double every {hours('best')} hours and need no "
            f"bought growth factors. A food-grade plant with shared medium. Medium at the cost of the nutrients alone. Gas at up to "
            f"{kw('best')['gas_velocity'] * 1000:.0f} mm a second. The tank uses {S.plain_list(tr['best']['used'])}. A run is lost on "
            f"{kw('best')['hazard'] * 100:.1f}% of days. Shoppers are favourable too: once it is familiar, {eqs_b:.0%} choose it at "
            f"equal price. The other cases take {eqs_c:.0%}.</p>"
            f"<p><b>What has to go right.</b> Everything at once. The waste level has been seen only in engineered pharma cells, not "
            f"in meat cells. Nobody has built the plant. Many markets restrict genetically engineered food. And most of this case's "
            f"share comes from the {eqs_b:.0%}: with the other cases' {eqs_c:.0%}, the same cost gives "
            f"{S.pct_num(S.shares(r['best']['total'])['global'])}% of the world's meat and seafood, not "
            f"{S.pct_num(S.shares(r['best']['total'], eqs='best_equal_price_share')['global'])}% (both at the most-likely-values cost).</p>"
            + _odds_html(("engineered", "h24", "plant", "gas6"))
            + f"<p>The author gives no odds for the {eqs_b:.0%}. This case is the favourable end of what the model allows, not what to expect.</p>"),
    }
    one_line = {
        "today": "The best meat cells anyone has published, in an ordinary tank.",
        "central": "A changed feed and tank, cheaper inputs, and cells selected to grow faster. No genetic engineering.",
        "best": "Everything works, including engineered cells and shoppers who slightly favour it.",
    }
    cases = [{"key": k, "label": CASE_LABELS[k], "say": one_line[k], "text": texts[k], "eqs": value(S.SCENARIOS[k].equal_price_share)}
             for k in CASE_KEYS]

    # the regional bands: the same draws as scenarios.bands (cost from scenario_mc, demand from meat_market.monte_carlo), by region
    region_bands = {k: {"global": list(S.bands(S.SCENARIOS[k].choice, eqs=S.eqs_of(k))["share"])} for k in CASE_KEYS}
    jobs = []
    for k in CASE_KEYS:
        cost = S.scenario_mc(S.SCENARIOS[k].choice, S.BAND_N, 0)["total"]
        jobs += [(k, reg, cost, S.eqs_of(k), S.BAND_N) for reg, _name in REGION_NAMES if reg != "global"]
    try:                                         # eighteen independent draws: run them side by side where the machine allows
        done = _region_bands_side_by_side(jobs)
    except Exception:                            # no worker processes here: one after the other gives the same numbers
        done = [_region_band(j) for j in jobs]
    for k, reg, band in done:
        region_bands[k][reg] = band

    # the ladder: each step adds one kind of change to the one before (scenarios.LADDER)
    step_text = {
        "today": ("Published cells in an ordinary tank", "needs nothing new"),
        "process": ("Change the process and buy cheaper inputs", "needs a change of process and cheaper inputs"),
        "central": ("Select cells that grow faster on the low-waste feed. This is the Central case", "needs selected cells"),
        "central_lean": ("Build a cheaper plant: food-grade, with shared medium", "needs a cheaper plant"),
        "best": ("Engineer the cells, and put every other switch at its cheapest plausible setting. This is the Best case",
                 "needs genetic engineering"),
    }
    ladder = []
    for k in S.LADDER:
        b = S.bands(S.SCENARIOS[k].choice, eqs=S.eqs_of(k))
        ladder.append({"key": k, "name": step_text[k][0], "tag": step_text[k][1], "cost": list(b["cost"]),
                       "point": S.run(S.SCENARIOS[k].choice)["total"]})

    # Level 2: the estimates behind the cost that nobody has measured on meat cells (the ones the bands draw), each with
    # the floorExplore argument that carries it, its range and where the range comes from
    def est(arg, name, lo, hi, unit, why, cells=None, scale=1.0, digits=None, pre=""):
        return {"arg": arg, "name": name, "lo": lo, "hi": hi, "unit": unit, "why": why, "cells": cells, "scale": scale, "digits": digits, "pre": pre}

    def reg(arg, key, name=None, **k):
        v = REGISTRY[key]
        return est(arg, name or AR.PLAIN[key], v.lo, v.hi, k.pop("unit", v.unit), AR.EVIDENCE.get(key, ""), **k)

    cx = S.MC_PRIORS["capex_x"]
    estimates = [
        reg("nh3_limit", "sc_nh3_limit", unit="mmol a litre"),
        reg("membrane_life", "rt_membrane_life", unit="litres"),
        est("capex_x", "What the plant costs to build, against the model's estimate", cx[0], cx[2], "times the estimate",
            "Humbird calls his estimate good to within 50%; two published designs come in at about a third of it"),
        reg("min_perfusion", "pf_min_perfusion", unit="mL of medium for each gram of cells a day"),
        reg("nh3_kg", "sc_nh3_selected", unit="mol a kilo", cells=["selected", "measured"]),
        reg("charge", "plant_charge_mature", unit="% of the plant's cost a year", scale=100.0, digits=1),
        reg("protectant_price", "pf_protectant_price", unit="a kilo", pre="$"),
        reg("antifoam_otr", "pf_antifoam_otr", unit="% of the oxygen transfer without antifoam", scale=100.0, digits=0),
        reg("maint", "pf_maintenance_share", unit="% of the oxygen a cell uses", scale=100.0, digits=0),
    ]
    best_eqs = REGISTRY["best_equal_price_share"]
    lo_c, hi_c = _lognormal_5_95("equal_price_share")
    ksm, sf = REGISTRY["cult_sub_mult"], REGISTRY["scaffold_frac"]
    judgements = [
        {"key": "equal_price_share", "name": "Share of shoppers who would choose it at equal price, once familiar",
         "ranges": {"central": [lo_c, hi_c], "best": [best_eqs.lo, best_eqs.hi]}, "fmt": "pct",
         "why": "A judgement. Surveys run from about 5% (a cold choice between labelled packs) to 60% (willing to try it in a "
                "restaurant), and there are no sales to check against. The range is the middle nine tenths of the draws for this case."},
        {"key": "cult_sub_mult", "name": "How much more price-sensitive cultivated meat is than meat in general",
         "ranges": {"central": [ksm.lo, ksm.hi], "best": [ksm.lo, ksm.hi]}, "fmt": "times",
         "why": AR.EVIDENCE.get("cult_sub_mult", "") + ". A low value means shoppers keep buying it at a higher price."},
        {"key": "cut_cells", "name": "Share of a cut (a steak or fillet) that is cells, the rest plant protein",
         "ranges": {"central": [1 - sf.hi, 1 - sf.lo], "best": [1 - sf.hi, 1 - sf.lo]}, "fmt": "pct",
         "why": "Products on sale are 10 to 30% plant protein and binder. Fewer cells make a cut cheaper, and shoppers like it less."},
    ]
    _PAGE_DATA.update({"cases": cases, "own_label": OWN_LABEL, "regions": REGION_NAMES, "region_bands": region_bands,
                       "ladder": ladder, "estimates": estimates, "judgements": judgements, "p_conv": value("p_conv")})
    return _PAGE_DATA


def _plain_switch_words(sc: dict) -> dict:
    """A few of the switches' labels and notes lean on the line above them ("his price", "the same effect"). On the page
    each can be read alone (a dropdown, a row of Level 2), so say who and what. Words only: no setting's numbers change."""
    words = {("gf", "60"): {"label": "60% of Humbird's price", "note": "Most of Humbird's large-scale price."},
             ("gf", "all"): {"label": "All bought at Humbird's price"},
             ("shape", "square"): {"note": "A squarer tank passes more gas per litre than a tall one, though less than a squat one. "
                                           "The model counts the extra steel and floor."}}
    for sw in sc["switches"]:
        for st in sw["settings"]:
            st.update(words.get((sw["key"], st["key"]), {}))
    return sc


def _tank_note() -> str:
    """The tank all the cases assume, in plain sentences (Level 1 and the vessel section)."""
    return (f"<b>The tank in every case.</b> Every case uses a stirred tank of {value('vm_str_m3'):.0f} m³ run in perfusion. A filter "
            "holds the cells back while fresh medium washes the waste out. Cells leave the tank in a steady bleed, so the harvest is "
            f"continuous. Nobody has run animal cells in perfusion above about {value('vm_perf_max_m3'):.0f} m³.")


def _other_estimates_html() -> str:
    """Level 1's small table: the 2035 forecast, Humbird's optimistic design and a company's own report, on the cases' basis."""
    import scenarios as S
    rows = S.table_rows()[len(S.PAGE_ORDER) - 1:]                 # the forecast, Humbird's design, the reported process
    names = ("The author's forecast for 2035", "Humbird's optimistic design", "As a company reports")
    what = ("Each switch at the setting the author thinks as likely as not to be reached at production scale by 2035: Central's "
            "cells in a food-grade plant with shared medium and fewer lost runs. A first draft.",
            "Humbird's 2021 design: his engineered cells in an ordinary perfusion tank, a food-grade plant, no tank tricks and no lost "
            "runs. It assumes the hardest change and none of the easy ones.",
            "SuperMeat's 2024 report of its own process, scaled up on paper, with a yearly charge on its plant added. "
            "The company's figures have not been peer reviewed.")
    out = []
    for (name, cost, cb, ratio, world, sb, _need), nm, wh in zip(rows, names, what):
        if cb is not None:
            c1 = f"<b>about {_money(cb[1], 0)}</b><br><span class='alt'>Median. 8 in 10 draws between {_money(cb[0], 0)} and {_money(cb[2], 0)}.</span>"
            ratio = shelf_price(cb[1]) / value("p_conv")
            shop = shelf_price(cb[1])
        else:
            c1 = f"<b>{_money(cost, 0)}</b><br><span class='alt'>The report's own single figure. No draws.</span>"
            shop = shelf_price(cost)
        rng = ("8 in 10 draws under 0.001%." if sb[2] < 0.00095 else
               f"8 in 10 draws between {S.pct_num(sb[0])}% and {S.pct_num(sb[2])}%.")
        out.append(f"<tr><td><b>{nm}</b><br><span class='alt'>{wh}</span></td><td class='n'>{c1}</td>"
                   f"<td class='n'>{_money(cost)}</td><td class='n'>{_money(shop, 0)}<br><span class='alt'>{ratio:.1f} times everyday meat</span></td>"
                   f"<td class='n'><b>{S.pct_num(sb[1])}%</b><br><span class='alt'>Median. {rng}</span></td></tr>")
    head = ("<thead><tr><th>Estimate</th><th>Cost to grow a kilo of cells</th><th>If every estimate lands on its most likely value</th>"
            "<th>Price in the shop, a kilo</th><th>Long-run share of world meat and seafood</th></tr></thead>")
    labels = ("", "Cost to grow a kilo of cells", "If every estimate lands on its most likely value", "Price in the shop, a kilo",
              "Long-run share of world meat and seafood")
    out = ["<tr>" + "".join((f"<td data-label='{labels[i]}'" if labels[i] else "<td") + part
                            for i, part in enumerate(row.split("<td")[1:])) for row in out]
    return f"<div class='scrollx'><table class='sctab stack'>{head}<tbody>{''.join(out)}</tbody></table></div>"


def _how_met_html() -> str:
    """Level 2's list: what it would take to meet each thing the cost rests on, and how solid the evidence is. Written
    for the Central case; every figure is computed."""
    import scenarios as S
    c0 = S.SCENARIOS["central"].choice
    r0 = S.run(c0)
    be = 1.0 / contamination.breakeven_hazard("lean")
    cost = lambda ch: _money(S.run({**c0, **ch})["total"])
    used = S.plain_list(S.tricks_report(c0)["used"])
    rows = [
        ("Waste the cells make",
         f"The Central case assumes a low-waste feed and selected cells: {r0['medium_l']:.0f} litres of medium a kilo. With the best "
         f"meat cells in the published record, which make more lactate, the cost is {cost({'cells': 'measured'})}. With ordinary meat "
         f"cells it is {cost({'cells': 'ordinary'})}.",
         f"Replace glutamine in the feed. Select or adapt cells that make less waste. Engineer the cells ({cost({'cells': 'engineered'})}). "
         "Or take the ammonium out of the used medium.",
         "The feed change was measured once, in cattle cells. The engineered level has been seen only in pharma cells."),
        ("The filter that holds the cells back",
         f"Perfusion needs a device that holds cells back while used medium leaves. The model prices a hollow-fibre filter loop. Its "
         f"membranes are the largest single line of the Central case, {_money(r0['membranes'])} a kilo.",
         "A filter that lasts longer, a cheaper membrane, or a device with no membrane at all (a settler or an acoustic separator).",
         f"No such device exists at {value('vm_str_m3'):.0f} cubic metres. The membrane's life comes from pharma runs, not meat cells."),
        ("Clearing CO₂ from a dense tank",
         f"Cells give off CO₂, which leaves a tank only in the gas bubbled through it. The Central case uses {used}. With none of "
         f"these the cost is {cost({'tricks': 'none'})}. It is {cost({'gas': '2'})} if the cells tolerate only 2 mm of gas a second.",
         "A column beside the tank, extra pressure, a squatter tank, or recycled oxygen. The sizes come from calculation.",
         "Calculated, not measured. Nobody has run animal cells over such a column, or 4 mm a second at this size."),
        ("The cost of the plant",
         f"The Central case assumes a food-grade plant. Built like a pharma plant, the cost is {cost({'plant': 'pharma'})}.",
         f"Leave out what animal cells do not need: a clean-room hall, an owned oxygen plant and spare seed tanks. The cost is then "
         f"{cost({'plant': 'lean'})}. No case assumes a plant as cheap as a yeast plant, because nothing shows animal cells can grow in one.",
         f"Nobody has built a food-grade plant with shared medium for animal cells. It pays off only while a tank loses a run less often "
         f"than about once in {be:.0f} days."),
        ("Fast growth and low waste together",
         f"The Central case assumes cells that double every 36 hours while making little waste. At 43 hours, the pace of the best "
         f"low-waste culture measured, the cost is {cost({'growth': '43'})}. At 24 hours it is {cost({'growth': '24'})}.",
         "Select faster lines on the low-waste feed.", "Each has been shown alone, never both in one culture."),
        ("Runs lost to contamination",
         f"The Central case loses a run on {value('sc_hazard_cm') * 100:.0f}% of days, and a lost tank is out of use for "
         f"{value('sc_restart_base'):.0f} days. At 2% a day with a month to restart, the cost is {cost({'losses': '2', 'restart': '30'})}. "
         f"At pharma's 0.2% it is {cost({'losses': '0.2'})}.",
         "Sealed, steam-sterilised tanks, tested seed trains and strict hygiene.",
         "One survey of makers gives this rate, and it does not state run lengths."),
        ("Medium price and growth factors",
         f"The Central case pays $0.20 a litre, what several companies announced for 2025, and takes that price to include the growth "
         f"factors (the proteins that tell cells to grow). The growth-factor switch then sets a floor: medium cannot cost less than its "
         f"nutrients plus the growth factors bought. At the Central setting the floor is below $0.20, so the switch adds nothing. With "
         f"all growth factors bought at Humbird's price the cost is {cost({'gf': 'all'})}. At $0.50 a litre, what SuperMeat reports, it "
         f"is {cost({'medium': '0.50'})}. At the cost of the nutrients alone it is {cost({'medium': 'floor', 'gf': 'none'})}.",
         "Cheaper amino acids, recycled medium, cheaper growth factors or cells that make their own.",
         "Company announcements. Nobody has verified them at scale. Genetic engineering has made cattle cells that make their own growth factors."),
    ]
    h = ["<table><thead><tr><th>What the cost rests on</th><th>What the Central case assumes, and the cost if it fails</th>"
         "<th>How it could be met</th><th>How solid</th></tr></thead><tbody>"]
    for name, assumes, met, solid in rows:
        h.append(f"<tr><td><b>{name}</b></td><td>{assumes}</td><td>{met}</td><td>{solid}</td></tr>")
    h.append("</tbody></table>")
    return (f"<p class='small'>Written for the Central case, which costs {_money(r0['total'])} a kilo of cells when every estimate is at its "
            "most likely value. Each row moves one thing and leaves the rest alone. All costs are dollars a kilo of wet cells.</p>"
            "<div class='blk scrollx'>" + "".join(h).replace("<table>", "<table style='min-width:720px'>") + "</div>")


def _cells_by_tank_html() -> str:
    """Cost of a kilo of cells for every kind of cell in every tank, Central's other settings; each figure loads into the switches."""
    import html as _h
    import scenarios as S
    import page_sections as ps
    c0 = S.SCENARIOS["central"].choice
    head = ["<thead><tr><th>Cells ↓ &nbsp; Tank →</th>" + "".join(f"<th>{t}<br><span class='alt'>{d}</span></th>" for _k, t, d in ps._GRID_TANKS)
            + "</tr></thead><tbody>"]
    save = {}
    for ck, gk, clab in ps._GRID_CELLS:
        head.append(f"<tr><th>{clab}</th>")
        costs = []
        for tk, _t, _d in ps._GRID_TANKS:
            shape = "flat" if tk != "none" else "tall"
            cs = {**c0, "cells": ck, "growth": gk, "tricks": tk, "shape": shape}
            r, lean = S.run(cs), S.run({**cs, "plant": "lean"})
            costs.append(r["total"])
            lim = S.LIMIT_PLAIN.get(r["limit"], r["limit"])
            head.append(f"<td onclick=\"scApplyChoice({{cells:'{ck}',growth:'{gk}',tricks:'{tk}',shape:'{shape}'}})\" class='gcell'>"
                        f"<b>{_money(r['total'])}</b> <span class='alt'>({_money(lean['total'])} with shared medium)</span><br>"
                        f"<span class='alt'>{r['density']:.0f} g/L, limited by {_h.escape(lim)}</span></td>")
        head.append("</tr>")
        save[ck] = (costs[0] - costs[-1], (costs[0] - costs[-1]) / costs[0])
    head.append("</tbody>")
    lo, hi = min(v[0] for v in save.values()), max(v[0] for v in save.values())
    best = S.tricks_report(S.SCENARIOS["best"].choice)
    return ("<p class='small'>The cost of a kilo of cells for each kind of cell in each kind of tank, at its most likely values. The first "
            "figure is for a food-grade plant. The figure in brackets is for a food-grade plant with shared medium. Everything else is as "
            "in the Central case. Click a figure to load it into the switches.</p>"
            f"<div class='scrollx'><table class='sctab grid2'>{''.join(head)}</table></div>"
            f"<p class='small'>All three tank tricks together save between {_money(lo)} and {_money(hi)} a kilo in this table. As a share of "
            f"the cost they matter more when the cells are good: {save['engineered'][1]:.0%} with engineered cells, "
            f"{save['ordinary'][1]:.0%} with ordinary meat cells, where the medium that washes the waste out sets most of the cost and "
            f"no tank trick lowers that. In the Best case, where the plant is cheap, the tricks are worth {_money(best['d_no_tricks'])}.</p>")


def _vessels_html() -> str:
    """The vessel-by-mode section: the table (page_vessels.js redraws it for the selected case) and what it says, with the
    cheapest combination found from the table itself."""
    import html as _h
    import vessels as V
    import page_sections as ps
    f = ps.vessel_facts()
    R, C = f["ref"], f["cen"]
    m = ps._vm_money
    S_ = ("stirred", "perfusion")
    name = lambda k: f"{V.VESSELS[k[0]]['name'].lower()}, {V.MODES[k[1]]['name'].lower()}"
    cheapest = lambda g: min(((c["cost"], k) for k, c in g.items() if c["possible"]))
    cc, cr = cheapest(C), cheapest(R)
    if cc[1] == S_:
        lead = f"A stirred tank in perfusion is the cheapest combination in the Central case, at {m(C[S_]['cost'])} a kilo."
    else:
        lead = (f"The cheapest combination in the Central case is {name(cc[1])}, at {m(cc[0])} a kilo. A stirred tank in perfusion, "
                f"which every case on this page assumes, costs {m(C[S_]['cost'])}.")
    if cr[1] != S_:
        lead += (f" In Humbird's optimistic design the cheapest is {name(cr[1])}, at {m(cr[0])}, against {m(R[S_]['cost'])} for "
                 "the stirred tank in perfusion.")
    guide = (f"<p class='small'>{_tank_note()} This table asks what other vessels and other ways of running a tank "
             "would cost. Each cell gives the cost of a kilo of cells at its most likely values. Only the vessel (the row) and the way "
             "it is run (the column) change. The cells, plant, tank tricks and losses stay as in <b id='vm_case'>the Central case</b>.</p>"
             "<p class='small'><button class='btn small vmbtn on' data-vm='scenario' onclick=\"vmSet('scenario');return false\">"
             "The selected case</button> <button class='btn small vmbtn' data-vm='reference' onclick=\"vmSet('reference');"
             "return false\">Humbird's optimistic design</button></p>")
    lim_rows = "".join(f"<li><b>{_h.escape(V.VESSELS[v]['name'])}</b> ({ps._vm_size(V.VESSELS[v]['size'])}): {_h.escape(V.VESSELS[v]['limits'])}</li>"
                       for v in V.VESSEL_ORDER)
    fd = [g[("stirred", "filldraw")]["density"] for g in (R, C)]
    take = (
        f"<p class='small'><b>What the table says.</b> {lead} Nobody has run animal cells in perfusion above about "
        f"{value('vm_perf_max_m3'):.0f} m³. In Humbird's optimistic design CO₂ limits the stirred tank, at {R[S_]['density']:.0f} g a "
        f"litre. In the Central case oxygen does, at {C[S_]['density']:.0f} g a litre: the column takes the CO₂ out, and antifoam takes "
        f"a quarter of the oxygen the bubbles deliver. The ways of running a tank that have been used at {value('vm_str_m3'):.0f} m³ "
        f"cost more. In Humbird's design a fed-batch stirred tank costs {m(R[('stirred', 'fedbatch')]['cost'])} and fill-and-draw costs "
        f"{m(R[('stirred', 'filldraw')]['cost'])}. In the Central case they cost {m(C[('stirred', 'fedbatch')]['cost'])} and "
        f"{m(C[('stirred', 'filldraw')]['cost'])}. These costs assume {min(fd):.0f} to {max(fd):.0f} g of cells a litre. Nobody has "
        f"shown that density for meat cells in a tank this size: the one {value('vm_str_m3'):.0f} m³ plant for meat cells reports "
        f"harvests of about {value('vm_x_meat_shown'):.0f} g a litre.</p>"
        f"<p class='small'>A chemostat costs more than fill-and-draw ({m(R[('stirred', 'chemostat')]['cost'])} in Humbird's design) "
        f"because it must run below the cells' top growth rate. Batch costs the most of the stirred-tank modes "
        f"({m(R[('stirred', 'batch')]['cost'])}) because one fill of medium feeds only a thin culture. An airlift costs about what a "
        f"stirred tank costs when the culture is not washed out. In perfusion it costs more ({m(R[('airlift', 'perfusion')]['cost'])} in "
        f"Humbird's design) because its tall shape passes less gas per litre and clears less CO₂. A single-use bag needs a new bag "
        f"every run, so it is close to a stirred tank only in perfusion ({m(R[('bag', 'perfusion')]['cost'])}), where a run lasts a "
        f"month. Packed beds and hollow fibres exist only as small units, so they cost {m(R[('packed', 'perfusion')]['cost'])} and "
        f"{m(R[('hollow', 'perfusion')]['cost'])} a kilo in Humbird's design. Even a {value('vm_str_m3'):.0f} m³ bed priced like a "
        f"stirred tank, with carriers that cost nothing, would cost {m(f['bed'])}.</p>")
    legend = ("<p class='small'>Under each cost, the cell gives how dense the culture gets, what limits that density, and the largest "
              "item of cost. The tag says whether anyone has grown animal cells this way at this size, for any product: "
              f"{ps._vm_tag(V.TODAY)} {ps._vm_tag(V.PILOT)} {ps._vm_tag(V.PAPER)}. Only Vow's stirred tank grows cells for food at "
              f"{value('vm_str_m3'):.0f} m³. The tag describes the vessel, the way it is run and its size. It does not say that anyone "
              f"has reached the density in the cell. If the density is above the {value('vm_x_meat_shown'):.0f} g a litre reported for "
              "meat cells in a tank of 1 m³ or more, the cell says so.</p>")
    ev = "".join(f"<li><b>{_h.escape(V.VESSELS[v]['name'])}, {_h.escape(V.MODES[mo]['name'].lower())}:</b> {_h.escape(V.TAGS[(v, mo)][1])}</li>"
                 for v in V.VESSEL_ORDER for mo in V.MODE_ORDER if V.TAGS[(v, mo)][1] and (v, mo) not in V.SAME_AS)
    grid0 = (ps.vessel_grid_html(V.settings()['central']).replace("The scenario clears", "The case clears")
             .replace("the scenario’s own tricks", "the case’s own tricks"))          # the words page_vessels.js uses when it redraws
    return (guide + f"<div id='vm_grid'>{grid0}</div>" + legend + take +
            f"<details class='scdet'><summary>The evidence behind each tag</summary><ul>{ev}</ul></details>" +
            f"<details class='scdet'><summary>What limits each vessel</summary><ul>{lim_rows}</ul><p class='fxn'>Perfusion assumes "
            f"a hollow-fibre filter loop that holds the cells back. Its membranes cost about "
            f"${value('rt_membrane_price') / value('rt_membrane_life'):.2f} per litre they filter. Batch and fed-batch run "
            f"{value('pf_fedbatch_doublings'):.0f} doublings a cycle from a seed, plus {value('pf_turnaround_h'):.0f} hours to clean and refill "
            f"(Humbird's design). A lost cycle costs the cycle and {value('vm_restart_cycle_days'):.0f} more days. The model prices each vessel at "
            f"the largest unit built for animal cells, up to {value('vm_str_m3'):.0f} m³.</p></details>" + ps._vm_pointers())


def _industry_html() -> str:
    """The model against company cost claims (page_sections.industry_claims), with the rows named as the rest of the page names them."""
    import html as _h
    import industry_claims as IC
    import page_sections as ps
    names = {"today": "Published cells", "process": "Step 2: process changes and cheaper inputs", "central": "Central case",
             "central_lean": "Step 4: a cheaper plant, with shared medium", "best": "Best case",
             "forecast": "The author's forecast for 2035", "reference": "Humbird's optimistic design"}
    out = ps.industry_claims()
    for k, new in names.items():
        old = f"<tr><td>{_h.escape(IC.NAMES[k])}</td>"
        if old not in out:
            raise RuntimeError(f"industry claims: the row for {k} was not found")
        out = out.replace(old, f"<tr><td>{_h.escape(new)}</td>")
    return (out.replace("Every scenario here includes", "Every case here includes").replace("Central's cells", "The Central case's cells")
            .replace("the scenario's food-grade plant", "the Central case's food-grade plant")
            .replace("the scenario&#x27;s food-grade plant", "the Central case&#x27;s food-grade plant"))


def _measured_html() -> str:
    """Two lists: what has been measured and what has not. The run figures come from the back-test table's own rows."""
    import html as _h
    done = [
        "Dense perfusion at bench scale. CHO cells in a wave bag were held at 100 to 214 million cells a millilitre (Clincke 2013). "
        "Chicken cells in a 10-litre tank were held at 80 million a millilitre (SuperMeat 2024, a company report).",
        "Ammonia made by cattle meat cells with and without glutamine (Hubalek 2023). With glutamine, the cells made 0.70 mol a kilo and "
        "doubled in 26 hours. Without it, they made under 0.14 mol and doubled in 43 to 54 hours.",
        f"Vow reports growing animal cells in a {value('vm_str_m3') * 1000:,.0f}-litre food-grade stirred tank, drained and refilled, "
        f"with no clean room, at about {value('vm_x_meat_shown'):.0f} g of cells a litre.",
        "A survey of makers found contamination losses of 11.2% of batches, or 19.5% beyond flasks. It did not state run lengths (Powell 2025).",
        "Gas flows of 0.1 to 2 mm a second in tanks of 8 to 20 cubic metres with animal cells (Nienow 2006).",
    ]
    todo = [
        f"Perfusion with animal cells above about {value('vm_perf_max_m3'):.0f} cubic metres, and a way to hold cells back at "
        f"{value('vm_str_m3'):.0f}.",
        f"Meat cells denser than about {value('vm_x_meat_shown'):.0f} g a litre in a tank of a cubic metre or more.",
        "Meat cells that make this little waste and still double in 24 to 36 hours.",
        "The ammonia and CO₂ that muscle or fish cells tolerate when dense. How much gas and foam dense cultures stand at 20 cubic metres.",
        "A pumped column, extra pressure or recycled oxygen with meat cells.",
        "The real cost of a food-grade plant for animal cells, with or without shared medium.",
        "Medium at $0.20 a litre and growth factors at scale, on a stated mass basis.",
    ]
    li = lambda xs: "".join(f"<li>{_h.escape(x)}</li>" for x in xs)
    return (f"<div class='scpair'><div><h4>Has been measured</h4><ul>{li(done)}</ul></div><div><h4>Has not been measured</h4>"
            f"<ul>{li(todo)}</ul></div></div>")


PAGE_HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cultivated meat: cost and market share</title>
<style>
/* ---- tokens: one set for light, one for dark; every colour on the page comes from here ---- */
:root{color-scheme:light;
 --bg:#fcfcfb;--card:#ffffff;--sunk:#f4f3f0;--ink:#0b0b0b;--ink2:#52514e;--muted:#6b6a65;--rule:#e2e0da;--grid:#ecebe6;--axis:#b9b7b0;
 --accent:#1c5cab;--caseline:#c2410c;--pick:#dbe8fa;
 --b1:#cde2fb;--b2:#9ec5f4;--b3:#6da7ec;--b4:#3987e5;--b5:#256abf;--b6:#104281;
 --up:#0a7d5a;--down:#b3321c;--s1:#2a78d6;--s2:#1baf7a;--s3:#eda100;--s4:#9a9890;
 --orange:#E69F00;--green:#117733;--red:#CC3311;}
@media (prefers-color-scheme: dark){:root{color-scheme:dark;
 --bg:#1a1a19;--card:#222220;--sunk:#262624;--ink:#f0efec;--ink2:#c3c2b7;--muted:#a3a199;--rule:#3a3936;--grid:#2e2d2a;--axis:#66645e;
 --accent:#86b6ef;--caseline:#f08a55;--pick:#1f3657;
 --b1:#0d366b;--b2:#184f95;--b3:#256abf;--b4:#3987e5;--b5:#6da7ec;--b6:#9ec5f4;
 --up:#3fbf95;--down:#ee7a63;--s1:#3987e5;--s2:#199e70;--s3:#c98500;--s4:#8a8880;}}
*{box-sizing:border-box;}
html{scroll-behavior:smooth;scroll-padding-top:var(--barh,84px);}
body{margin:0;background:var(--bg);color:var(--ink);
 font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;line-height:1.5;font-size:16px;}
/* one link style for the whole page */
a{color:var(--accent);text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:.18em;
 text-decoration-color:color-mix(in srgb,currentColor 40%,transparent);}
a:hover{text-decoration-color:currentColor;} a:visited{color:var(--accent);}
a:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:2px;}
button:focus-visible,select:focus-visible,input:focus-visible,summary:focus-visible,[tabindex]:focus-visible{outline:2px solid var(--accent);outline-offset:2px;}
.wrap{max-width:964px;margin:0 auto;padding:0 20px 64px;}
/* a readable measure: about 70 characters a line for running text */
p,li,dd,.measure{max-width:70ch;} td p,td li,th p{max-width:none;}
h1{font-size:1.6rem;line-height:1.2;margin:22px 0 6px;}
h2{font-size:1.2rem;margin:0;} h3{font-size:1.02rem;margin:22px 0 4px;} h4{font-size:.95rem;margin:16px 0 4px;} h5{font-size:.95rem;margin:18px 0 4px;}
.deck{font-size:1.05rem;margin:0 0 10px;}
.small{font-size:.86rem;color:var(--ink2);} .note{font-size:.84rem;color:var(--muted);}
/* one callout style */
.callout,.fxcard,.scwarn,.example,.aside,.intro,.wovr,.selftest .stanchor{border-left:3px solid var(--axis);background:var(--sunk);padding:8px 12px;margin:10px 0;
 font-size:.9rem;border-radius:0 4px 4px 0;max-width:74ch;}
.callout p,.fxcard p,.aside p,.intro p{margin:0 0 6px;} .callout p:last-child,.fxcard p:last-child{margin-bottom:0;}
.aside .ah{font-weight:700;display:block;margin-bottom:3px;}
/* one tag style: a quiet outlined chip; the words carry the meaning */
.tag,.tagchip,.vtag,.selftest .sttag{display:inline-block;font-size:.72rem;font-weight:600;line-height:1.3;padding:1px 7px;border-radius:9px;
 border:1px solid var(--axis);color:var(--ink2);background:transparent;white-space:normal;}
/* ---- the sticky case bar ---- */
.casebar{position:sticky;top:0;z-index:30;background:var(--bg);border-bottom:1px solid var(--rule);margin:0 -20px;padding:8px 20px;}
.casebar .in{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;}
.seg{display:flex;flex-wrap:wrap;gap:0;border:1px solid var(--axis);border-radius:8px;overflow:hidden;}
.seg button{font:inherit;font-size:.9rem;padding:7px 13px;border:0;border-right:1px solid var(--axis);background:var(--card);color:var(--ink);cursor:pointer;line-height:1.25;}
.seg button:last-child{border-right:0;} .seg button:hover{background:var(--sunk);}
.seg button[aria-pressed="true"]{background:var(--ink);color:var(--bg);font-weight:600;}
.seg button[aria-disabled="true"]{color:var(--muted);cursor:default;}
.casebar label{font-size:.86rem;color:var(--ink2);display:flex;align-items:center;gap:6px;}
.casebar select{width:auto;}
.casehint{font-size:.8rem;color:var(--muted);flex-basis:100%;display:none;} .casehint.on{display:block;}
select{font:inherit;font-size:.88rem;padding:5px 6px;border:1px solid var(--axis);border-radius:6px;background:var(--card);color:var(--ink);max-width:100%;}
.btn{font:inherit;font-size:.86rem;padding:6px 12px;border:1px solid var(--axis);background:var(--card);color:var(--ink);border-radius:6px;cursor:pointer;}
.btn:hover{background:var(--sunk);} .btn.on{background:var(--ink);color:var(--bg);} .btn.small{padding:3px 9px;font-size:.8rem;}
/* ---- first screen ---- */
.tiles{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:12px 0;}
.tile{border:1px solid var(--rule);border-radius:8px;background:var(--card);padding:12px 14px;}
.tile .tl{font-size:.86rem;color:var(--ink2);} .tile .tb{font-size:1.9rem;font-weight:700;line-height:1.15;font-variant-numeric:tabular-nums;margin:2px 0 4px;}
.tile .td{font-size:.86rem;color:var(--ink2);line-height:1.4;margin:0;}
@media(max-width:700px){.tiles{grid-template-columns:1fr;gap:8px;} .tile .tb{font-size:1.6rem;}}
.chart{border:1px solid var(--rule);border-radius:8px;background:var(--card);padding:12px 14px;margin:12px 0;}
.chart h3{margin:0 0 2px;font-size:1rem;} .chart .sub{font-size:.86rem;color:var(--ink2);margin:0 0 8px;max-width:74ch;}
.legend{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:.8rem;color:var(--ink2);margin:6px 0 4px;align-items:center;}
.legend .lt{flex-basis:100%;} .legend .li{display:inline-flex;align-items:center;gap:5px;} .legend .li>span:first-child{flex:none;}
.legend .sw{display:inline-block;width:14px;height:10px;border-radius:2px;}
.legend .ln{display:inline-block;width:18px;height:0;border-top:2.5px solid var(--caseline);}
.legend .dt{display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--ink);}
.legend .dn{display:inline-block;width:18px;height:0;border-top:1.5px dotted var(--ink2);}
.plot{position:relative;} .plot svg{display:block;width:100%;height:auto;overflow:visible;touch-action:pan-y;}
.tipbox{position:absolute;pointer-events:none;display:none;z-index:5;background:var(--card);color:var(--ink);border:1px solid var(--axis);border-radius:6px;
 padding:7px 9px;font-size:.78rem;line-height:1.4;box-shadow:0 3px 12px rgba(0,0,0,.18);min-width:170px;max-width:240px;}
.tipbox b{font-weight:600;} .tipbox .tr{display:flex;justify-content:space-between;gap:12px;font-variant-numeric:tabular-nums;}
.tipbox .tr .sw{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:5px;}
.alt{font-size:.86rem;color:var(--ink2);margin:8px 0 0;max-width:74ch;}
details.tv{margin:6px 0 0;font-size:.84rem;} details.tv>summary{cursor:pointer;color:var(--accent);}
table.num{border-collapse:collapse;font-size:.82rem;font-variant-numeric:tabular-nums;margin:6px 0;}
table.num th,table.num td{border-bottom:1px solid var(--rule);padding:3px 9px 3px 0;text-align:right;white-space:nowrap;}
table.num th:first-child,table.num td:first-child{text-align:left;white-space:normal;}
table.num th{font-weight:600;color:var(--ink2);}
.ctlrow{margin:12px 0;} .ctlrow label{display:block;font-size:.95rem;margin-bottom:4px;} .ctlrow input[type=range]{width:100%;max-width:460px;display:block;}
.readouts{font-size:.9rem;color:var(--ink2);margin:6px 0 0;}
input[type=range]{width:100%;accent-color:var(--accent);margin:0;}
input[type=range]:disabled{opacity:.5;cursor:not-allowed;}
.levelnav{margin:22px 0 8px;padding:0;list-style:none;border-top:1px solid var(--rule);}
.levelnav li{max-width:none;border-bottom:1px solid var(--rule);padding:7px 0;font-size:.92rem;display:flex;gap:10px;flex-wrap:wrap;}
.levelnav .lv{color:var(--muted);font-size:.8rem;min-width:52px;padding-top:2px;} .levelnav .ld{color:var(--ink2);}
/* ---- levels: sections that open in place ---- */
details.level{border-bottom:1px solid var(--rule);} details.level:first-of-type{border-top:1px solid var(--rule);}
details.level>summary{cursor:pointer;padding:12px 0;list-style:none;display:grid;grid-template-columns:auto 1fr;gap:2px 12px;align-items:baseline;}
details.level>summary::-webkit-details-marker{display:none;}
details.level>summary .lv{font-size:.8rem;color:var(--muted);grid-row:1;white-space:nowrap;}
details.level>summary .lv::before{content:"\25B8\00a0";color:var(--ink2);} details.level[open]>summary .lv::before{content:"\25BE\00a0";}
details.level>summary h2{grid-column:2;} details.level>summary .ls{grid-column:2;font-size:.9rem;color:var(--ink2);max-width:70ch;}
details.level>.lb{padding:2px 0 22px;}
details.sub{border:1px solid var(--rule);border-radius:8px;padding:8px 12px;margin:14px 0;background:var(--card);}
details.sub>summary{cursor:pointer;font-weight:600;font-size:.95rem;} details.sub[open]>summary{margin-bottom:8px;}
.scdet{margin-top:6px;font-size:.84rem;} .scdet summary{cursor:pointer;color:var(--accent);} .scdet ul{margin:4px 0;padding-left:18px;}
/* ---- tables ---- */
.scrollx{overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;} .scrollx+.scrollx{margin-top:18px;}
table.sctab,table.pt,.blk table{border-collapse:collapse;width:100%;font-size:.84rem;}
.sctab th,.sctab td,table.pt th,table.pt td,.blk th,.blk td{border-top:1px solid var(--rule);padding:6px 10px 6px 0;vertical-align:top;text-align:left;line-height:1.4;}
.sctab th,table.pt th,.blk th{font-size:.8rem;color:var(--ink2);font-weight:600;}
.sctab thead th,.blk thead th{border-top:0;}
.sctab td.n,table.pt td.n{font-variant-numeric:tabular-nums;white-space:nowrap;} .sctab td.s,table.pt td.s{color:var(--ink2);}
.sctab .alt,.vmtab .alt{color:var(--ink2);font-size:.8rem;font-weight:400;white-space:normal;}
.sctab{min-width:640px;} .sctab.grid2{min-width:560px;} .sctab.grid2 th:first-child{min-width:170px;}
.sctab .gcell{cursor:pointer;} .sctab .gcell:hover{background:var(--sunk);}
.vmtab td{min-width:130px;} .vmtab td.vno,.vmtab td.vsame{color:var(--muted);background:var(--sunk);} .vunshown{font-style:italic;}
table.pt td:first-child,table.pt th:first-child{min-width:150px;}
table.scgrid{border-collapse:collapse;font-size:.84rem;} .scgrid th{font-weight:600;font-size:.8rem;padding:4px 8px;text-align:left;color:var(--ink2);}
.scgrid td{padding:6px 10px;text-align:center;cursor:pointer;border:2px solid var(--card);font-variant-numeric:tabular-nums;min-width:62px;color:#0b0b0b;}
.scpair{display:grid;grid-template-columns:1fr 1fr;gap:16px;} @media(max-width:700px){.scpair{grid-template-columns:1fr;}}
.scpair h4{margin:0 0 4px;} .scpair ul{margin:0;padding-left:18px;font-size:.88rem;} .scpair li{margin-bottom:4px;}
/* ---- controls ---- */
.ctl{margin:0 0 12px;min-width:0;} .ctl label{display:flex;flex-wrap:wrap;justify-content:space-between;gap:2px 8px;font-size:.86rem;margin-bottom:3px;}
.ctl .nm{font-weight:600;} .ctl .val{font-variant-numeric:tabular-nums;color:var(--ink);font-weight:600;margin-left:auto;}
.ctl .src{color:var(--muted);font-size:.74rem;font-weight:400;}
.ctl .ovr{display:flex;align-items:center;gap:5px;font-size:.78rem;color:var(--ink2);margin-top:3px;} .ctl .ovr input{margin:0;}
.ctl select{width:100%;}
.grphdr{font-size:.86rem;font-weight:700;margin:14px 0 8px;padding-bottom:3px;border-bottom:1px solid var(--rule);grid-column:1/-1;}
.railgrid,.fxg{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:4px 22px;}
.fxn{font-size:.82rem;color:var(--ink2);margin:.3em 0 0;} .scsw .fxn{min-height:2.4em;}
.fx select{width:100%;}
.q{display:inline-block;width:16px;height:16px;line-height:16px;text-align:center;border-radius:50%;border:1px solid var(--axis);
 color:var(--ink2);font-size:.68rem;cursor:help;margin-left:4px;font-weight:700;background:var(--card);}
.tip,#foottip{position:fixed;max-width:300px;background:var(--ink);color:var(--bg);padding:8px 10px;border-radius:6px;font-size:.8rem;line-height:1.45;z-index:999;
 display:none;box-shadow:0 4px 14px rgba(0,0,0,.25);} #foottip{pointer-events:none;white-space:pre-line;max-width:320px;}
.tog{margin:8px 0 2px;font-size:.86rem;display:flex;align-items:center;gap:7px;}
.toggle button{font:inherit;font-size:.8rem;border:1px solid var(--axis);background:var(--card);color:var(--ink);padding:3px 9px;cursor:pointer;}
.toggle button.on{background:var(--ink);color:var(--bg);} .toggle button:first-child{border-radius:6px 0 0 6px;} .toggle button:last-child{border-radius:0 6px 6px 0;border-left:0;}
/* ---- charts: one font, text in ink colours, recessive grid ---- */
svg text{font-family:inherit;fill:var(--ink2);} svg text.b{fill:var(--ink);font-weight:600;} svg text.m{fill:var(--muted);} svg text.on{fill:#fff;}
svg text[stroke="#fff"]{stroke:var(--card);} svg rect[fill="#fff"]{fill:var(--card);} svg circle[fill="#000"]{fill:var(--ink);}
svg [stroke="#ccc"],svg [stroke="#999"],svg [stroke="#444"],svg [stroke="#333"],svg [stroke="#bbb"],svg [stroke="#CCC"]{stroke:var(--axis);}
svg [stroke="#eee"],svg [stroke="#f0f0f0"],svg [stroke="#f3f3f3"],svg [stroke="#f2f2f2"]{stroke:var(--grid);}
/* bar charts drawn in HTML: labels are real text that wraps, bars sit on a shared scale, and the rows stack on a phone */
.hb{display:grid;grid-template-columns:minmax(200px,44%) 1fr;gap:4px 16px;align-items:center;padding:7px 4px;border-top:1px solid var(--grid);font-size:.86rem;}
.hbars .hb:first-child{border-top:0;} .hb .hl{line-height:1.35;} .hb .hv{color:var(--ink2);font-size:.82rem;}
.hb .ht{position:relative;height:26px;min-width:0;}
.hb .bar{position:absolute;top:6px;height:14px;border-radius:3px;background:var(--s1);min-width:2px;}
.hb .bar.save{background:var(--s1);opacity:.28;border-radius:0 3px 3px 0;} .hb .bar.dn{background:var(--up);} .hb .bar.up{background:var(--down);} .hb .bar.sh{background:var(--s1);}
.hb .bar.clip{border-right:3px dashed var(--card);}
.hb .wh{position:absolute;top:12px;height:2px;background:var(--ink);} .hb .dotm{position:absolute;top:7px;width:12px;height:12px;border-radius:50%;background:var(--ink);border:2px solid var(--card);margin-left:-6px;}
.hb .vline{position:absolute;top:-8px;bottom:-8px;width:0;border-left:1.5px dotted var(--ink2);} .hb .vbase{position:absolute;top:0;bottom:0;width:2px;margin-left:-1px;background:var(--ink);}
.hb.axis{border-top:1px solid var(--axis);align-items:start;} .hb.axis .ht{height:18px;} .hb .tk{position:absolute;top:2px;transform:translateX(-50%);font-size:.72rem;color:var(--ink2);white-space:nowrap;}
.hb.axis .tk:first-child{transform:none;} .hb.axis .tk:last-child{transform:translateX(-100%);}
.hb.click{cursor:pointer;} .hb.click:hover,.hb.sel{background:var(--sunk);}
.hbh{font-weight:600;font-size:.9rem;margin:14px 0 2px;padding-top:8px;border-top:1px solid var(--axis);} .hbars .hbh:first-child{border-top:0;margin-top:2px;padding-top:0;}
@media(max-width:640px){.hb{grid-template-columns:1fr;} .hb.axis .hl{order:2;}}
.fxrow{fill:transparent;cursor:pointer;} .fxrow:hover,.fxrow.sel{fill:var(--sunk);}
.rowhit{fill:transparent;cursor:pointer;} .rowhit:hover,.rowhit.sel{fill:var(--sunk);}
/* older charts keep their own drawing size; they are shown large enough for 11 px text and scroll sideways on a phone */
svg.w720{width:880px;max-width:none;height:auto;display:block;} svg.w420{width:512px;max-width:none;height:auto;display:block;}
.calc{border:1px solid var(--rule);border-radius:8px;padding:10px 14px;margin:8px 0 14px;font-size:.88rem;background:var(--card);}
.calc .ch{font-weight:700;margin-bottom:4px;} .calc ol{margin:0;padding-left:20px;} .calc li{margin:4px 0;max-width:none;}
.calc .eq{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.8rem;background:var(--sunk);border-radius:5px;padding:2px 6px;display:inline-block;max-width:100%;overflow-x:auto;white-space:nowrap;vertical-align:middle;}
.calc .note{color:var(--ink2);font-size:.8rem;margin-top:4px;}
@media(max-width:560px){.calc .eq{white-space:normal;}}
.selftest{font-size:.82rem;font-variant-numeric:tabular-nums;}
.selftest .sthead{font-weight:700;margin-bottom:5px;} .selftest table{border-collapse:collapse;width:100%;}
.selftest td{padding:3px 8px 3px 0;vertical-align:top;border-top:1px solid var(--rule);} .selftest tr:first-child td{border-top:none;}
.selftest .stchk{font-weight:700;width:14px;} .selftest .stval{text-align:right;font-weight:700;white-space:nowrap;}
.selftest .stobs,.selftest .stnote,.selftest .stbuild{color:var(--ink2);} .selftest .stbad{color:var(--down);}
.selftest .stsecrow td{border-top:none;padding-top:10px;} .selftest .stsec{font-weight:600;}
@media(max-width:560px){.selftest table,.selftest tbody,.selftest tr{display:block;} .selftest td{display:inline-block;border-top:none;} .selftest tr{border-top:1px solid var(--rule);padding:3px 0;} .selftest td.stwhat{display:block;}}
/* ---- method ---- */
.methods p,.methods li{font-size:.94rem;line-height:1.55;}
.methods details.step{border-top:1px solid var(--rule);padding:8px 0;}
.methods details.step>summary{cursor:pointer;font-size:.94rem;line-height:1.5;max-width:74ch;} .methods details.step[open]>summary{margin-bottom:6px;}
.methods pre{background:var(--sunk);border:1px solid var(--rule);border-radius:6px;padding:8px 11px;font-size:.8rem;overflow-x:auto;}
.methods code{background:var(--sunk);padding:0 3px;border-radius:3px;font-size:.86em;}
.methods a[href^="#ref"]{font-size:.8em;font-weight:600;vertical-align:super;padding:0 1px;text-decoration:none;}
.methods a[href^="#ref"]:hover{text-decoration:underline;}
.methods .refs{font-size:.86rem;padding-left:18px;} .methods .refs li{margin-bottom:5px;scroll-margin-top:90px;}
.methods .vardef td{padding:2px 10px 2px 0;vertical-align:top;}
.methods .attr{font-size:.86rem;border-collapse:collapse;margin:4px 0 8px;}
.methods .attr th{padding:3px 10px;text-align:center;font-size:.82rem;vertical-align:bottom;color:var(--ink2);}
.methods .attr td{text-align:center;padding:3px 10px;border-bottom:1px solid var(--rule);}
.methods .attr td:first-child,.methods .attr th:first-child{text-align:left;}
.methods mjx-container{overflow-x:auto;overflow-y:hidden;max-width:100%;} .methods mjx-container[display="true"]{min-width:0 !important;}
#about{margin:26px 0 8px;font-size:.88rem;color:var(--ink2);border-top:1px solid var(--rule);padding-top:10px;}
#about h3{margin:0 0 6px;}
section[id],h3[id],details[id]{scroll-margin-top:var(--barh,84px);}
@media(max-width:600px){
 .wrap{padding:0 16px 48px;} .casebar{margin:0 -16px;padding:6px 16px;} h1{font-size:1.3rem;margin-top:14px;}
 .seg{width:100%;display:grid;grid-template-columns:repeat(4,1fr);} .seg button{padding:6px 4px;font-size:.78rem;}
 .casebar label{font-size:.8rem;} .chart{padding:10px 10px;} details.level>summary{grid-template-columns:1fr;} details.level>summary h2,details.level>summary .ls{grid-column:1;}
}
@media(max-width:700px){table.stack{min-width:0;} .stack thead{display:none;} .stack tr,.stack td{display:block;} .stack td{border-top:0;padding:3px 0;white-space:normal !important;}
 .stack tr{border-top:1px solid var(--rule);padding:8px 0;} .stack td[data-label]:before{content:attr(data-label) ": ";font-weight:600;color:var(--ink2);font-size:.8rem;}}
@media print{.casebar{position:static;} details.level>.lb{display:block;}}
</style>
<script>window.MathJax={chtml:{scale:0.96}};</script>
<script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head><body><div id="tip" class="tip" role="tooltip"></div><div class="wrap">
<header>
<h1>Cultivated meat: cost and market share</h1>
<p class="deck" id="deck" aria-live="polite"></p>
<p class="small">Cultivated meat is animal meat grown from cells in tanks, without slaughter. This is an open model of what it could cost and
how much meat and seafood it could replace. Pick a case. Every figure on the page follows it.</p>
</header>

<div class="casebar" id="casebar"><div class="in">
  <div class="seg" role="group" aria-label="The case shown on this page" id="casebtns"></div>
  <label for="regionsel">Region <select id="regionsel"></select></label>
  <span class="casehint" id="casehint">Move any setting on this page and it becomes your own case. The three named cases stay as they are.</span>
</div></div>

<section id="first" aria-label="The answer for the selected case">
<div class="tiles" id="tiles" aria-live="polite"></div>
<div class="chart" id="l0card">
<h3 id="l0title">Long-run share against the cost of growing a kilo of cells</h3>
<p class="sub">Each shade is a range for one thing nobody can measure yet: the share of shoppers who would choose it at the same price as
meat, once it is no longer new. The line is the selected case's own setting. The dots are the cases.</p>
<div class="legend" id="l0legend"></div>
<div class="plot" id="l0plot"><svg id="l0chart" role="img" aria-labelledby="l0title" aria-describedby="l0alt"></svg><div class="tipbox" id="l0tip"></div></div>
<p class="alt" id="l0alt"></p>
<details class="tv"><summary>Show the chart's numbers as a table</summary><div class="scrollx" id="l0table"></div></details>
</div>

<div class="ctlrow">
<label for="eqs">If it cost the same as meat and was no longer new, the share of shoppers who would choose it: <b id="eqs_v"></b></label>
<input type="range" id="eqs" min="3" max="80" step="1">
<p class="readouts" id="eqs_read" aria-live="polite"></p>
</div>
<div class="callout" id="sharedef"><b>What &ldquo;share&rdquo; means on this page.</b> The share of all meat and seafood sold, by weight, in the long run:
once cultivated meat is on every shelf and no longer feels new. Seafood is {{SEAFOOD_PCT}}% of that total in the model's world market.
It is a ceiling the market moves towards, not a figure for any year.</div>
<p class="note">These are long-run ceilings, not a forecast of when. Nobody has run any of these processes at production scale, and no human
expert has reviewed the model yet. It is not investment or business advice. <a href="#method">Method, sources and limits</a>.</p>
</section>

<ul class="levelnav" aria-label="The rest of this page">
<li><span class="lv">Level 1</span><span><a href="#assumes">What each case assumes</a> <span class="ld">What has to go right, and the steps from the published cells to the best case.</span></span></li>
<li><span class="lv">Level 2</span><span><a href="#moves">What would move it most</a> <span class="ld">Choices, unmeasured estimates and judgements about shoppers, ranked.</span></span></li>
<li><span class="lv">Level 3</span><span><a href="#where">Where and when</a> <span class="ld">By type of meat, by region, and over time.</span></span></li>
<li><span class="lv">Level 4</span><span><a href="#engineering">Check the engineering</a> <span class="ld">The ten switches, the cost breakdown, tanks, vessels and reported runs.</span></span></li>
<li><span class="lv">Level 5</span><span><a href="#shoppers">Check the shopper model</a> <span class="ld">The shopper settings, share against price, and other products.</span></span></li>
<li><span class="lv">Level 6</span><span><a href="#method">Method, sources, limits</a> <span class="ld">Equations, inputs, references and the questions a sceptic would ask.</span></span></li>
</ul>

<details class="level" id="assumes">
<summary><span class="lv">Level 1</span><h2>What each case assumes</h2>
<span class="ls">Most of the fall in cost needs no genetic engineering. The largest step is selecting cells that make less lactate.</span></summary>
<div class="lb">
<div id="l1_case"></div>
<div class="chart">
<h3 id="l1title">From the published cells to the best case, one step at a time</h3>
<p class="sub">Each bar is the cost of a kilo of cells after one more step: the median of the draws, with a thin line for the range that
holds 8 in 10 draws. The tag says what the step needs.</p>
<div class="hbars" id="l1chart" role="group" aria-labelledby="l1title" aria-describedby="l1alt"></div>
<p class="alt" id="l1alt"></p>
<details class="tv"><summary>Show the steps as a table</summary><div class="scrollx" id="l1table"></div></details>
</div>
<p class="small">{{TANK_NOTE}}</p>
<p class="small"><b>What the cases assume about the tank.</b> Nobody has run any of these tank designs with animal cells. The Published cells
case has no tank tricks. From the second step on, the tank clears CO&#8322; without more bubbles. The second step uses {{TRICKS_PROCESS_LIST}}.
Without these it costs ${{TRICKS_PROCESS_NO}} a kilo in a tank of the same shape, and ${{TRICKS_PROCESS_ORD}} in the ordinary tall tank. The
Central case uses {{TRICKS_CENTRAL_LIST}}: ${{TRICKS_CENTRAL_NO}} without them, and ${{TRICKS_CENTRAL_ORD}} in the ordinary tall tank. The Best
case uses {{TRICKS_BEST_LIST}}: ${{TRICKS_BEST_NO}} without them, and ${{TRICKS_BEST_ORD}} in the ordinary tall tank. These are costs with
every estimate at its most likely value, calculated, not measured. The switches &ldquo;Tank tricks&rdquo; and &ldquo;Tank shape&rdquo; in
<a href="#engineering">Check the engineering</a> take the tricks away.</p>
<h3>Other estimates</h3>
<p class="small">Three figures from outside the three cases, on the same basis. They are for comparison and cannot be selected.</p>
{{OTHER_ESTIMATES_HTML}}
<details class="sub"><summary>Words used on this page</summary>
<p><b>Medium</b> is the nutrient liquid the cells grow in. <b>Waste</b> means the ammonia and lactate that cells give off as they grow. Waste
slows growth, so fresh medium must wash it out. <b>Perfusion</b> means that fresh medium flows through the tank all the time. A filter holds
the cells back, and they are harvested continuously. A <b>column</b> is a packed tower beside the tank. The culture runs down it in a thin
film, and CO&#8322; leaves without bubbles. <b>Gas the cells tolerate</b> is the speed of gas rising through the tank, in millimetres a
second. Bubbles and foam hurt cells, so the cells set how much gas can pass. A <b>run lost</b> is a batch ruined by contamination. It
empties the tank and takes days to restart. A <b>draw</b> is one run of the model with its uncertain estimates picked at random from their
ranges. The <b>median</b> is the middle draw: half give less and half give more. A <b>most-likely-values figure</b> puts every estimate at
its single most likely value instead.</p></details>
</div></details>

<details class="level" id="moves">
<summary><span class="lv">Level 2</span><h2>What would move it most</h2>
<span class="ls">The kind of cells moves the cost most. How much shoppers like it moves the share as much as cost does.</span></summary>
<div class="lb">
<p>Each row moves one thing and leaves the rest alone. The start is the selected case with every estimate at its most likely value.
Three kinds of thing can move: <span class="tag">a choice</span> is one of the ten switches, something a company decides or achieves;
<span class="tag">an estimate nobody has measured at scale</span> is a number the model had to take from other cells, from small cultures or from calculation;
<span class="tag">a judgement about shoppers</span> cannot be measured before the product is on sale.</p>
<div class="chart">
<h3 id="l2title">One change at a time, largest first</h3>
<p class="sub" id="l2sub"></p>
<div class="hbars" id="l2chart" role="group" aria-labelledby="l2title"></div>
<div class="callout" id="l2card" aria-live="polite"></div>
<details class="tv"><summary>Show the rows as a table</summary><div class="scrollx" id="l2table"></div></details>
</div>
<details class="sub"><summary>How each could be met, and how solid the evidence is</summary>
{{HOW_MET_HTML}}
</details>
</div></details>

<details class="level" id="where">
<summary><span class="lv">Level 3</span><h2>Where and when</h2>
<span class="ls">Steaks and fish fillets first. Chicken and pork stay dearer even in the Best case.</span></summary>
<div class="lb">
<p id="l3_intro"></p>
<div class="chart">
<h3 id="l3atitle">Share by type of meat</h3>
<p class="sub" id="l3asub"></p>
<div class="hbars" id="l3types" role="group" aria-labelledby="l3atitle" aria-describedby="l3aalt"></div>
<p class="alt" id="l3aalt"></p>
<details class="tv"><summary>Show the types as a table</summary><div class="scrollx" id="l3atable"></div></details>
</div>
<h3>By region</h3>
<p class="small" id="l3rsub"></p>
<div class="scrollx" id="l3regions"></div>
<div class="chart">
<h3 id="l3ttitle">How fast: the path to the long-run share</h3>
<p class="sub" id="l3tsub"></p>
<div class="plot" id="l3tplot"><svg id="l3time" role="img" aria-labelledby="l3ttitle" aria-describedby="l3talt"></svg><div class="tipbox" id="l3ttip"></div></div>
<p class="alt" id="l3talt"></p>
</div>
<p class="small">The path uses the way other new products have spread (first a few early adopters, then word of mouth) and lets wariness of a
new food fade as people meet it. The cost stays fixed along the path. The timing is rougher than the ceiling. The settings are under
<a href="#shoppers">Check the shopper model</a>.</p>
</div></details>

<details class="level" id="engineering">
<summary><span class="lv">Level 4</span><h2>Check the engineering</h2>
<span class="ls">Ten switches set the cost. Change any of them and see what limits the tank and where the money goes.</span></summary>
<div class="lb">
<p>The cost of a kilo of cells is the cost of the plant, the medium and the losses, divided by what a tank produces in a year. Ten switches
hold the decisions that move it. Each named case is a preset of these switches. Moving one makes this page your own case.</p>
<div class="fxcard" id="sc_result"></div>
<div class="railgrid scsw" id="sc_switches"></div>
<p><button class="btn" onclick="scDesignNow()">Pick the cheapest tank design for these settings</button>
<span class="fxn">This tries every tank trick and shape, and keeps the cheapest one that passes two checks on the column's loop: how often the
culture passes through it, and how long it stays alkaline there.</span></p>
<h3>Where the cost goes</h3>
<div id="sc_parts" class="scrollx"></div>
<p class="small" id="sc_parts_note"></p>
<h3>Two switches together</h3>
<p class="small">The cost for every pair of settings of two switches, with the others as set above. Click a figure to set both.
<label>First switch <select id="sc_ga" onchange="scGridSet()" style="width:auto"></select></label>
<label>second switch <select id="sc_gb" onchange="scGridSet()" style="width:auto"></select></label></p>
<div id="sc_grid" class="scrollx"></div>
<h3>Which switches interact</h3>
<p class="small">A pair appears here when moving one switch is worth a different amount once the other has moved.</p>
<div id="sc_notes"></div>
<div class="blk" id="cellsxtank"><h3>Cells against tank</h3>
{{GRID_HTML}}
</div>
<h3>Cost against the price of medium</h3>
<div class="chart"><p class="sub" data-help="The three solid lines are three plants running the process one company reports (SuperMeat, 2024): the plant of Humbird's optimistic design, the plant that company reports, and a pharma-style plant with cells at half the density. The dashed lines mark the costs of the page's cases at their most likely values, named at the right. Below the dotted line, cultivated meat costs the same in the shop as everyday meat or less.">The cost of a kilo of cells as the medium gets
cheaper, for three plants running the process one company reports. The dot is the case set by the switches above.</p>
<div class="scrollx"><svg id="cost" class="w720" viewBox="0 0 720 300" role="img" aria-label="Cost of a kilo of cells against the price of a litre of medium, for three plants, with the cases as dashed lines"></svg></div></div>
<h3 id="vessels">Vessel types and operating modes</h3>
{{VESSELS_HTML}}
<h3>The cost model against reported runs</h3>
<p class="small">Reported runs beside what the cost model gives for the same cells and vessel. Nobody tuned the model to these runs. (Humbird's
two designs, which the model was tuned to, are left out.) An observed-to-model ratio far from 1 shows where the model is not reliable.</p>
{{BACKTEST_HTML}}
<h3>Against what companies report</h3>
{{INDUSTRY_HTML}}
<h3>What has and has not been measured</h3>
{{MEASURED_HTML}}
<details class="sub" id="fxwrap"><summary>All the levers: build your own case from the physics</summary>
      <div class="fx" id="fx">
        <p>When you move a lever, the model applies the physics. The tank holds only as many cells as it can supply with oxygen, clear of
        CO&#8322;, mix and feed. The chart &ldquo;What limits this tank&rdquo; below shows which limit applies. The ten switches above are
        ten of these levers. The rest are here.</p>
        <div class="ctl"><label for="fx_sc"><span class="nm">Start from a case</span></label>
          <select id="fx_sc" onchange="fxFromScenario(this.value)"></select></div>
        <div class="ctl"><label for="fx_sp"><span class="nm">Start from a kind of cell</span></label>
          <select id="fx_sp" onchange="fxSpecies()"></select></div>
        <p class="fxn" id="fx_spn"></p>
        <div class="fxg">
          <div class="ctl"><label for="fx_dh"><span class="nm">Doubling time</span><span class="val" id="fx_dh_v"></span></label>
            <input type="range" id="fx_dh" min="16" max="72" step="1" value="24" oninput="fxRender()"></div>
          <div class="ctl"><label for="fx_m"><span class="nm">Cell mass</span><span class="val" id="fx_m_v"></span></label>
            <input type="range" id="fx_m" min="0.5" max="3" step="0.1" value="3" oninput="fxRender()"></div>
          <div class="ctl"><label for="fx_ch"><span class="nm">Yearly charge on the plant</span><span class="val" id="fx_ch_v"></span></label>
            <input type="range" id="fx_ch" min="12.3" max="23.6" step="0.1" value="{{MATURE_CHARGE_PCT}}" oninput="fxRender()"></div>
          <div class="ctl"><label for="fx_hz"><span class="nm">Chance of losing a run, per day</span><span class="val" id="fx_hz_v"></span></label>
            <input type="range" id="fx_hz" min="0" max="10" step="0.1" value="0" oninput="fxRender()"></div>
          <div class="ctl"><label for="fx_rd"><span class="nm">Planned length of a run</span><span class="val" id="fx_rd_v"></span></label>
            <input type="range" id="fx_rd" min="5" max="90" step="1" value="33" oninput="fxRender()"></div>
          <div class="ctl"><label for="fx_rf"><span class="nm">Restart after a contamination</span><span class="val" id="fx_rf_v"></span></label>
            <input type="range" id="fx_rf" min="3" max="30" step="1" value="3" oninput="fxRender()"></div>
          <div class="ctl"><label for="fx_ws"><span class="nm">Waste the cells make</span><span class="val" id="fx_ws_v"></span></label>
            <input type="range" id="fx_ws" min="0" max="100" step="0.5" value="0" oninput="fxRender()"></div>
          <div class="ctl"><label for="fx_mp"><span class="nm">Medium price</span><span class="val" id="fx_mp_v"></span></label>
            <input type="range" id="fx_mp" min="0" max="1" step="0.01" value="0.15" oninput="fxRender()"></div>
          <div class="ctl"><label for="fx_cs"><span class="nm">Share of the product that is cells</span><span class="val" id="fx_cs_v"></span></label>
            <input type="range" id="fx_cs" min="30" max="100" step="5" value="100" oninput="fxRender()"></div>
          <div class="ctl"><label for="fx_gf"><span class="nm">Growth factors bought</span><span class="val" id="fx_gf_v"></span></label>
            <input type="range" id="fx_gf" min="0" max="100" step="5" value="0" oninput="fxRender()">
            <p class="fxn">As a share of Humbird's large-scale price per litre of medium.</p></div>
          <div class="ctl"><label for="fx_ms"><span class="nm">Oxygen used for upkeep, not growth</span><span class="val" id="fx_ms_v"></span></label>
            <input type="range" id="fx_ms" min="31" max="100" step="1" value="50" oninput="fxRender()"></div>
          <div class="ctl"><label for="fx_pc"><span class="nm">CO&#8322; the cells tolerate</span><span class="val" id="fx_pc_v"></span></label>
            <input type="range" id="fx_pc" min="5" max="250" step="5" value="100" oninput="fxRender()"></div>
          <div class="ctl"><label for="fx_gv"><span class="nm">Gas flow the cells tolerate</span><span class="val" id="fx_gv_v"></span></label>
            <input type="range" id="fx_gv" min="0.6" max="12" step="0.2" value="6" oninput="fxRender()"></div>
          <div class="ctl"><label for="fx_ar"><span class="nm">Tank shape: liquid depth over width</span><span class="val" id="fx_ar_v"></span></label>
            <input type="range" id="fx_ar" min="0.5" max="2.5" step="0.05" value="1.6" oninput="fxRender()"></div>
          <div class="ctl"><label for="fx_os"><span class="nm">Salt strength the cells tolerate</span><span class="val" id="fx_os_v"></span></label>
            <input type="range" id="fx_os" min="330" max="480" step="5" value="415" oninput="fxRender()"></div>
          <div class="ctl"><label for="fx_ph"><span class="nm">pH held in the tank</span><span class="val" id="fx_ph_v"></span></label>
            <input type="range" id="fx_ph" min="6.8" max="7.5" step="0.05" value="7.2" oninput="fxRender()"></div>
          <div class="ctl"><label for="fx_mf"><span class="nm">Least medium flow the cells need</span><span class="val" id="fx_mf_v"></span></label>
            <input type="range" id="fx_mf" min="3.5" max="30" step="0.5" value="7.5" oninput="fxRender()"></div>
          <div class="ctl"><label for="fx_v"><span class="nm">Tank size</span></label>
            <select id="fx_v" onchange="fxRender()"><option value="2">2 m&sup3;</option><option value="5">5 m&sup3;</option>
            <option value="10">10 m&sup3;</option><option value="20" selected>20 m&sup3;</option><option value="50">50 m&sup3;</option>
            <option value="100">100 m&sup3;</option><option value="200">200 m&sup3;</option></select></div>
          <div class="ctl"><label for="fx_pl"><span class="nm">Class of plant</span></label>
            <select id="fx_pl" onchange="fxRender()"><option value="pharma">A pharma-style plant with clean rooms</option>
            <option value="sanitary" selected>A food-grade plant</option>
            <option value="lean">A food-grade plant with shared medium (one medium line and fewer seed tanks serve all the tanks)</option>
            <option value="yeastplus">A yeast plant plus what animal cells must have (not shown to work either)</option>
            <option value="microbial">A plant built like a yeast plant (not shown to work for animal cells)</option>
            <option value="custom">Your own choice of items (below)</option></select></div>
          <div class="ctl"><label for="fx_mo"><span class="nm">How the tank is run</span></label>
            <select id="fx_mo" onchange="fxMode()"><option value="perfusion" selected>Perfusion (fresh medium flows through, and the cells are held back and harvested all the time)</option>
            <option value="filldraw">Drained and refilled (half the tank is drained and refilled each cycle, and nothing holds the cells back)</option></select></div>
        </div>
        <details style="margin:0 0 .6em"><summary class="fxn" style="cursor:pointer"><b>The plant, item by item.</b>
          Humbird's design for animal cells costs five times his own yeast plant with the same tanks. Choose what
          each item is built to. The class of plant above sets them all at once.</summary>
          <div class="railgrid" id="fx_items" style="margin-top:.5em"></div>
          <p class="fxn" id="fx_items_sum"></p></details>
        <p style="margin:.9em 0 .2em"><b>Tricks.</b> These are ways to get past the limits below. The model sizes each one by calculation
        (see the research notes on gas exchange and on waste). Nobody has tried any of them with meat cells.</p>
        <div class="fxg">
          <div class="ctl"><label for="fx_fat"><span class="nm">Fat taken from the feed, not made from glucose</span><span class="val" id="fx_fat_v"></span></label>
            <input type="range" id="fx_fat" min="0" max="100" step="5" value="0" oninput="fxRender()">
            <p class="fxn"><i>Feed or process.</i> Cells that make fat from glucose give off CO&#8322; without using oxygen. This is most of why cells make 1.2 CO&#8322; per oxygen. Fat in the feed lowers the ratio to 0.97 and raises the CO&#8322; limit by a quarter (a carbon balance on Humbird's cell). Nobody has tested whether the cells stop making their own fat.</p></div>
          <div class="ctl"><label for="fx_do"><span class="nm">Dissolved oxygen held at</span><span class="val" id="fx_do_v"></span></label>
            <input type="range" id="fx_do" min="0.02" max="0.3" step="0.005" value="{{DO_IMPLIED}}" oninput="fxRender()">
            <p class="fxn"><i>Feed or process.</i> The standard tank's oxygen supply implies about 0.28 mmol/L, which is above air saturation. Pharma holds 30&ndash;50% of air saturation, and cells grow unimpaired at about 10&ndash;100%. A lower level leaves more room to push oxygen in.</p></div>
          <div class="ctl"><label for="fx_col"><span class="nm">Packed column on a pumped loop</span><span class="val" id="fx_col_v"></span></label>
            <select id="fx_col" onchange="fxRender()"><option value="none" selected>none</option>
            <option value="co2">for CO&#8322; (air blown through)</option>
            <option value="o2_closed">for CO&#8322; and oxygen (oxygen recycled, lime takes the CO&#8322;)</option></select>
            <p class="fxn"><i>Feed or process.</i> The culture runs as a thin film down half a metre of steel packing, with no bubbles. The model calculates the size, the flow and the cost. Dense cultures have been pumped through fibres at up to about 15&ndash;24 tank volumes an hour for weeks, in volumes of 1&ndash;4 litres. Nobody has tested more than that. Culture that has lost CO&#8322; stays alkaline until it is back in the tank, so the more passes an hour, the more of the culture is alkaline at any moment.</p></div>
          <div class="ctl"><label for="fx_cp"><span class="nm">CO&#8322; the culture leaves the column at</span><span class="val" id="fx_cp_v"></span></label>
            <input type="range" id="fx_cp" min="20" max="70" step="5" value="55" oninput="fxRender()">
            <p class="fxn">A lower value strips more CO&#8322; per pass but makes the returning culture more alkaline. A value of 55 keeps the pH rise to 0.26.</p></div>
          <div class="ctl"><label for="fx_pt"><span class="nm">Pressure at the top of the tank</span><span class="val" id="fx_pt_v"></span></label>
            <input type="range" id="fx_pt" min="0" max="1" step="0.01" value="0.33" oninput="fxRender()">
            <p class="fxn"><i>Feed or process.</i> More pressure dissolves more oxygen. It does nothing for CO&#8322;. Steam-rated tanks take the pressure. Nobody has tested it in cells.</p></div>
          <div class="ctl"><label for="fx_wm"><span class="nm">Ammonia and lactate set</span></label>
            <select id="fx_wm" onchange="fxRender()"><option value="dial" selected>by the waste lever above</option>
            <option value="sep">separately, below</option></select></div>
          <div class="ctl"><label for="fx_nh"><span class="nm">Ammonia the cells make</span><span class="val" id="fx_nh_v"></span></label>
            <input type="range" id="fx_nh" min="0.02" max="1" step="0.005" value="0.055" oninput="fxRender()">
            <p class="fxn">0.055 is the engineered cell, and only <i>genetically engineered</i> CHO cells have shown it. Bovine cells made 0.70, and 0.14 with glutamine replaced in the feed (<i>feed or process</i>, measured).</p></div>
          <div class="ctl"><label for="fx_ly"><span class="nm">Lactate made per glucose used</span><span class="val" id="fx_ly_v"></span></label>
            <input type="range" id="fx_ly" min="0" max="1.8" step="0.05" value="0.5" oninput="fxRender()">
            <p class="fxn">0.5 is the engineered cell's. Ordinary pharma cells make about 1.4, and cells adapted to it make 0.4 (<i>selection or adaptation</i>). Chicken cells make 1.05. A value near 0 needs knocked-out genes (<i>genetic engineering</i>).</p></div>
          <div class="ctl"><label for="fx_gk"><span class="nm">Glucose used per kilo of cells</span><span class="val" id="fx_gk_v"></span></label>
            <input type="range" id="fx_gk" min="0.6" max="3.6" step="0.02" value="1.12" oninput="fxRender()">
            <p class="fxn">The engineered cell uses 1.12 mol. Measured pharma cells use 0.67&ndash;1.0. Nobody has measured this for meat cells. The named cases do not use this lever: they work the glucose out from the cells' own balance of fat, oxygen, ammonia and lactate.</p></div>
          <div class="ctl"><label for="fx_sb"><span class="nm">Ammonium taken out by a sorbent</span><span class="val" id="fx_sb_v"></span></label>
            <input type="range" id="fx_sb" min="0" max="95" step="5" value="0" oninput="fxRender()">
            <p class="fxn"><i>Feed or process.</i> The cell-free medium passes through a zeolite or resin before it returns to the tank. It saves fresh medium but not the cell filter: the liquid it cleans has passed the filter too. The sodium the sorbent gives back counts as salt. The model derives the capacity in medium and nobody has measured it.</p></div>
          <div class="ctl"><label for="fx_spx"><span class="nm">Sorbent price</span></label>
            <select id="fx_spx" onchange="fxRender()"><option value="0.05">$0.05/kg (bulk zeolite)</option>
            <option value="0.3">$0.30/kg (bulk zeolite, top)</option><option value="5" selected>$5/kg (graded and sterile, assumed)</option>
            <option value="20">$20/kg (medical-grade resin, assumed)</option></select></div>
          <div class="ctl"><label for="fx_scy"><span class="nm">Uses before the sorbent is thrown away</span></label>
            <select id="fx_scy" onchange="fxRender()"><option value="1" selected>1 (single use)</option>
            <option value="10">10</option><option value="50">50 (hoped for, not measured)</option></select></div>
        </div>
        <p style="margin:.8em 0 .2em"><b>What limits this tank.</b> Each bar shows the density that one limit allows in this case.
        The shortest bar is the limit that applies. The faint bars behind are Humbird's optimistic design (a standard perfusion tank), so you can see what each
        lever or trick changes.</p>
        <div id="fx_limits" class="scrollx"></div>
        <p class="example" id="fx_out"></p>
        <p style="margin:.2em 0 .6em"><button class="btn" onclick="fxApply()">Use this case on the whole page</button>
        <span class="fxn" id="fx_apply_msg"></span></p>
        <p style="margin:.6em 0 .2em"><b>What limits this case.</b> This chart moves each factor alone across its plausible
        range, with the others as you set them. Bars to the left lower the cost and bars to the right raise it. The dotted line is the cost
        that matches everyday meat. Click a factor to see what it is and where its range comes from.</p>
        <div id="fx_tornado" class="scrollx"></div>
        <div id="fx_torinfo" class="fxcard"></div>
        <p class="fxn" id="fx_notes"></p>
      </div>
</details>
</div></details>

<details class="level" id="shoppers">
<summary><span class="lv">Level 5</span><h2>Check the shopper model</h2>
<span class="ls">How a price becomes a share: the settings, share against price, why the share is what it is, and other products.</span></summary>
<div class="lb">
<p>For each meal, a shopper picks conventional meat, plant-based meat, cultivated meat, or beans and other whole foods. Each option gets a
score that adds up its price, its taste, its health image, whether it is real meat and whether an animal was killed. Tastes vary, so each
option's share rises smoothly with its score. Of every hundred shoppers, 95 are mainstream and choose mainly on price, taste and real meat.
The other 5 are vegetarian or vegan and care about slaughter. Shoppers also differ in how much they like cultivated meat. Most sit near
the typical liking, and a few are far from it in either direction, so some never buy it at any price.</p>
<h3>The shopper settings</h3>
<p class="small">The cost comes from the selected case. These settings are about shoppers and shops. Moving one makes this page your own case.</p>
<div id="rail"></div>
<h3>From the cost of cells to the price in the shop</h3>
<div class="calc" id="calc" aria-live="polite"></div>
<h3>Share against price, and why</h3>
<p class="small"><label for="curveSel">Type of meat for the two charts below</label> <select id="curveSel" style="width:auto"></select></p>
<div class="chart"><p class="sub" data-help="The marked point on the cultivated line is cultivated meat at the selected case's price. The marked point on the plant-based line is plant-based meat at its own price, 1.77 times meat. To compare the two at equal prices, read the cultivated line at that price.">How the four options' shares change as cultivated meat's price changes. The price is given as a
multiple of the conventional product's price: 1 means the same price.</p>
<div class="scrollx"><svg id="curve" class="w420" viewBox="0 0 420 300" role="img" aria-label="Shares of conventional meat, plant-based meat, whole foods and cultivated meat against the price of cultivated meat as a multiple of the conventional price"></svg></div></div>
<div class="chart"><p class="sub" id="bdsub" data-help="The bars are in points of score. One more point means the option is chosen about 2.7 times as often. Bars to the right help cultivated meat and bars to the left hurt it. They add up to the net gap that sets the mainstream shoppers' share.">What helps and what hurts cultivated meat against conventional meat for the average
mainstream shopper, in points of score. The last line is the share that results once shoppers' different liking for cultivated meat and
the 5% of vegetarians and vegans are counted.</p>
<div class="scrollx"><svg id="breakdown" class="w420" viewBox="0 0 420 300" role="img" aria-label="What helps and hurts cultivated meat against conventional meat, factor by factor, in points of score"></svg></div>
<p class="small">The rows, in words: <b>price</b> is the price gap times the price weight (written &beta; in the equations); <b>taste</b>,
<b>real meat</b>, <b>health</b> and <b>no slaughter</b> are each a difference between the two products times the weight shoppers give it
(w with a superscript in the equations); <b>novelty</b> is wariness of a new food (&nu;); <b>cut, premium</b> is how much less shoppers
like a cultivated cut or premium product than cultivated mince (&tau;).</p></div>
<h3>The spread when the shopper settings are uncertain</h3>
<div class="chart"><p class="sub" id="mcsub"></p>
<div class="scrollx"><svg id="mc" class="w720" viewBox="0 0 720 250" role="img" aria-label="Histogram of the long-run share over 2,000 draws of the shopper settings, for cultivated meat by weight and by value and for plant-based meat"></svg></div></div>
<h3>Other products, and which could go first</h3>
<div class="chart"><h3>Does the same shopper model explain other products?</h3>
<p class="sub" id="cmpsub" data-help="The model was not fitted to plant-based milk. It predicts about 15%, close to milk's market share. That is a weak test, because the milk facts are set by hand. Margarine and plant-based nuggets fit less well. The model was fitted to plant-based meat, so plant-based meat is not a test. Eggs test a different lever (animal welfare), and laws largely set their share.">The same shopper model, with only the product's facts changed.</p>
<p class="small"><label for="cmpSel">Product</label> <select id="cmpSel" style="width:auto"></select></p>
<div class="scrollx"><svg id="milk" class="w720" viewBox="0 0 720 320" role="img" aria-label="The model's share for another product beside its observed share"></svg></div></div>
<div class="chart"><h3>Which products could it enter first?</h3>
<p class="sub" data-help="The chart compares each product with the price of its everyday grade. It does not use the luxury price paid for wild-caught, top-grade or protected-origin products, because cultivated meat cannot copy those. The words beside each product say whether cultivated meat is already cheaper, about equal, cheaper only in the best case, or not even then. Bubble size is the conventional production that cultivated meat would displace if sold at cost. The cost view draws cultivated meat's cost as a line. Hover over a bubble for details.">Cultivated meat can already beat luxury products on price, but those markets are tiny. Commodity meat, where the volume is,
stays out of reach.</p>
<div class="toggle" style="margin:0 0 6px;display:inline-block"><button id="footWL">cost against each product's price</button><button id="footMV" class="on">share against price</button></div>
<p class="small"><label for="footSel">Product</label> <select id="footSel" style="width:auto"></select></p>
<div class="scrollx"><svg id="foothold" class="w720" viewBox="0 0 720 380" role="img" aria-label="Products cultivated meat could enter first, by price and size of market"></svg></div>
<div id="footcap" class="small" style="margin-top:6px"></div></div>
</div></details>

<details class="level methods" id="method">
<summary><span class="lv">Level 6</span><h2>Method, sources, limits</h2>
<span class="ls">How the model works step by step, what it leaves out, the equations, every input and the references.</span></summary>
<div class="lb">
<p>Each step below has a one-line summary. Open it for the detail. The equations are in appendix A0. A number with a bracketed reference,
like {{MEDIA_L}}&nbsp;L/kg&nbsp;[1], comes from that source. Judgement calls are labelled. The model computes everything else.</p>
<h3>Reality checks</h3>
<p class="small">Numbers from the model at its central settings beside real ones. <b>Matches</b> means that the model was not fitted to that number.</p>
<div class="selftest" id="selftest"></div>

      <details class="step" id="step1"><summary><b>Step 1 · From cost to price.</b> The cost of a kilo of cells is medium, plant and
      losses. The shop price adds the costs of reaching the shelf and the shop's margin. At the median cost that is {{R_CENTRAL}} times
      the price of everyday meat in the Central case and {{R_BEST}} times in the Best case.</summary>
      <p>The <b>price ratio</b> <i>R</i> is cultivated meat's price in the shop divided by the price of the conventional
      meat beside it. A ratio of 1 means the same price, and 2 means twice the price. The shop price has three parts:</p>
      <ul>
        <li><b>Medium</b> is the nutrient liquid the cells grow in. Cells must eat a fixed amount of amino acids, glucose and salts,
        and that feed costs at least about ${{FEEDSTOCK_FLOOR}} a kilo of cells [2]. The salts, buffer and vitamins in that figure are an
        assumption. How many litres carry the feed depends on the waste the cells make. Fresh medium must wash ammonia out before it
        passes {{NH3_LIMIT}} mmol a litre, the level the cases' cells are taken to tolerate, and lactate likewise. The model works out
        the glucose a kilo of cells takes up from the cells' own balance: what they build, what they burn and what they turn into
        lactate. The published cells need about {{MEDIUM_L_TODAY}} litres of medium a kilo, set by lactate. The Central case's
        selected cells need {{MEDIUM_L_CENTRAL}}, set by ammonia, and the engineered cells {{MEDIUM_L_BEST}}. Companies reported medium at
        $0.20 a litre or less in 2025, and an amino-acid cost analysis by GFI and MG Consulting supports that level [3]. Nobody has
        verified it at production scale.</li>
        <li><b>The plant</b> covers capital, labour, energy and supplies. Its cost per kilo is its cost per cubic metre of tank divided by
        what a cubic metre makes in a year. The second part is physics: how much oxygen a cell needs, and how much oxygen and
        CO&#8322; a tank can exchange without bubbles killing the cells. The plant's cost per cubic metre comes from Humbird's design [2]
        in 2025 prices, item by item. His plant as drawn comes to ${{HUMBIRD_PLANT}}/kg in 2018 prices. In perfusion a filter holds
        the cells back. Its membranes are paid for by the litre filtered, and they are the largest single line of the Central case.
        Scaling up animal cells is hard because of oxygen and CO&#8322; transfer and sterility [2].</li>
        <li><b>Getting it to the shelf</b> adds ${{MARKUP}}/kg for forming, packing and cold chain, and then the shop's margin,
        {{MARGIN_PCT}}% of the shelf price. Fitted to conventional meat's wholesale-to-retail spreads, this form gives the
        shop more dollars on a dearer product, as shops' percentage margins do. A structured cut is {{CUT_CELLS_PCT}}% cells bound with
        plant protein, plus ${{SCAF}}/kg to assemble it. No study has costed this for cultivated meat. The figures come from plant-protein
        extrusion, surimi and binder prices [6].</li>
      </ul>
      <p><b>The cases.</b> How these parts come out depends on ten decisions, the switches in
      <a href="#engineering">Check the engineering</a>. A case is a preset of them. Every cost on this page is for one kilo of real
      cells, which are about 70% water and 20% protein, like meat, in 2025 prices. At the median of the draws a kilo costs
      ${{TODAY_COST_P50}} with the published cells (8 in 10 draws between ${{TODAY_COST_P10}} and ${{TODAY_COST_P90}}),
      ${{CENTRAL_COST_P50}} in the Central case (${{CENTRAL_COST_P10}} to ${{CENTRAL_COST_P90}}) and ${{BEST_COST_P50}} in the Best case
      (${{BEST_COST_P10}} to ${{BEST_COST_P90}}). With every estimate at its most likely value the figures are ${{COST_TODAY}},
      ${{COST_CENTRAL}} and ${{COST_BEST}}. The most-likely-values figure is below the median in every case, because most of the
      estimates have more room to come in worse than better. Matching ${{PCONV}} meat in the shop needs ${{PARITY_BIOMASS}} a kilo
      of cells.</p>
      <p><b>What the draws vary.</b> Each case's switches stay fixed, but the estimates behind it can be off. These are the plant
      estimate, the yearly charge on it, the life and price of the filter membranes, the share of a cell's oxygen that goes to upkeep,
      the medium price, the loss rate, the ammonia the cells tolerate and (for the published and the selected cells) make, the least
      medium flow, the bubble protectant and antifoam. Each draw picks all of them from their ranges. When the shopper settings vary
      as well (price sensitivity, the share at equal price, taste, the costs of reaching the shelf and a cut's make-up), the long-run
      share of world meat and seafood is {{CENTRAL_SHARE_P50}}% in the Central case at the median (8 in 10 draws between
      {{CENTRAL_SHARE_P10}}% and {{CENTRAL_SHARE_P90}}%) and {{BEST_SHARE_P50}}% in the Best case ({{BEST_SHARE_P10}}% to
      {{BEST_SHARE_P90}}%). {{TODAY_SHARE_SENTENCE}} The draws do not vary the switches themselves.
      <a href="#moves">What would move it most</a> shows what each is worth.</p>
      <p><b>Financing.</b> Humbird charges {{HUMBIRD_CHARGE_PCT}}% of a plant's cost a year. This covers money at 7.5% repaid in
      10 years, plus maintenance and insurance. That fits a first plant. His own report gives the food industry's
      cost of capital as 5.4% and uses a 20-year life for a yeast plant. Those figures make the yearly charge
      {{MATURE_CHARGE_PCT}}% [2]. The cases are long-run cases set against meat, a mature industry, so they use the
      lower rate, and the draws vary it. The table below gives every row at both rates.</p>
      <p><b>Other estimates.</b> <b>Humbird's optimistic design</b> is his perfusion tank with his engineered cells, no tank tricks
      and no lost runs. Earlier versions of this page called it the floor. The plant costs about ${{PLANT_FLOOR}}/kg and the cells
      ${{COST_FLOOR}}/kg at its most likely values. It assumes the hardest change, engineered cells, and none of the easy ones, so it is
      not a step between the cases. The page keeps it because the cross-checks against Humbird's own analysis use it. At the
      first-plant rate it would cost about ${{COST_FLOOR_FIRST}}/kg. <b>As a company reports.</b> SuperMeat reports {{MEDIA_L}} litres
      of medium per kilo of cells at under ${{MEDIA_P}} a litre [1], which is about ${{MEDIA_TODAY}} a kilo. Its running costs plus a
      yearly charge on its plant at the first-plant rate add ${{OH_DEF}}, so cells cost about ${{BIOMASS_TODAY}} a kilo, which is
      ${{RETAIL_TODAY}} in the shop (${{CUT_RETAIL_TODAY}} for a cut) and {{R_TODAY}} times everyday meat. The company itself counts
      depreciation only, which gives about $5 less. It is a company's claim from 10-litre runs, not a peer-reviewed result, and its stated
      tank sizes and densities account for only about half of its stated output. An earlier version of this page used a peer-reviewed
      study [20]. Its kilo turned out to be a wet pellet that holds several times more liquid than cells, so this page no longer uses it.
      <b>A plant as cheap as a yeast plant</b> is not used in any case. Plants for yeast and other microbes cost about a
      quarter as much per cubic metre as Humbird's design for animal cells. That would cut the plant term to about ${{PLANT_FLOOR_LO}}/kg
      (cells ${{COST_FLOOR_LO}}/kg with Humbird's optimistic design). But animal cells are far easier to contaminate, and nobody has shown
      that they can grow in such a plant. For comparison only, Humbird's optimistic design in a pharma-style plant with clean rooms, tanks
      simply drained and refilled, and first-plant financing costs about ${{COST_FLOOR_HI}}/kg.</p>
      <p><b>What each row of the table means.</b> These are older, simpler cost cases, kept for comparison with the published designs.
      Plant costs are in 2025 prices. A pharma-style plant has clean rooms and vessels sterilised with steam. The last two columns give
      the cost of a kilo of cells and, in brackets, the shop price against ${{PCONV}} everyday meat after ${{MARKUP}}/kg to the shelf and
      the shop's {{MARGIN_PCT}}% margin. The first of them finances the plant as a first plant ({{HUMBIRD_CHARGE_PCT}}% of its cost a
      year), and the second as a mature food industry ({{MATURE_CHARGE_PCT}}%).</p>
      <div class="scrollx"><table class="pt"><tr><th>case</th><th>what it means</th><th>has anyone done it?</th>
        <th>cells, $/kg (vs meat), first-plant financing</th><th>the same with food-industry financing</th></tr>
        {{COST_CASES_ROWS}}
      </table></div>
      <p><b>Reading the table.</b> The cells and the class of plant matter far more than how the tank is run. The rows
      from &ldquo;a pharma-style plant with clean rooms, cells at half the density&rdquo; down come from physics, not from anyone's plant.
      See <a href="https://github.com/PabloAMC/Cultivated_meat/blob/main/METHODS.md">METHODS.md</a>, &ldquo;A
      physics-based cost estimate&rdquo;. A 25% tax on conventional meat lowers <i>R</i> as much as a 20% cut in every cost of
      cultivated meat.</p>
      </details>

      <details class="step" id="step2"><summary><b>Step 2 · From price to choice.</b> Shoppers choose among four options.
      They weigh price, taste, health, &ldquo;is it real meat?&rdquo; and &ldquo;no slaughter&rdquo;. The share who choose cultivated
      meat at equal price, once it is familiar, is a setting: {{PARITY_NEUTRAL}}% in the Published cells and Central cases,
      {{BEST_EQS}}% in the Best case.</summary>
      <p>This is a standard discrete-choice model [12]. For each meal, a shopper picks conventional meat, plant-based meat,
      cultivated meat, or beans and other whole foods. The shares therefore include the bean meals. Each option gets a score
      that adds up its price, taste, health, whether it is real meat and whether an animal was killed. Tastes vary,
      so the top score does not always win. Each option's share rises smoothly with its score, and one more point means
      about 2.7 times as often.</p>
      <p><b>Two kinds of shopper.</b> 95% are mainstream, and they choose mainly on price, taste and real meat. 5% are vegetarian
      or vegan [7]. They care about slaughter and mostly eat beans. Within each kind, shoppers differ in how much they like
      cultivated meat: most sit near the typical liking, and a few are far from it in either direction (A1).</p>
      <div class="scrollx"><table class="attr">
        <tr><th>option</th><th>price</th><th>taste</th><th>real meat</th><th>no slaughter</th><th>health</th></tr>
        <tr><td><b>conventional</b> meat</td><td>1</td><td>1</td><td>yes</td><td>no</td><td>&minus;0.1</td></tr>
        <tr><td><b>plant-based</b> meat</td><td>1.77&times; [14]</td><td>0.8 [7]</td><td>no</td><td>yes</td><td>0</td></tr>
        <tr><td><b>cultivated</b> meat</td><td><i>R</i> (Step 1)</td><td>1 (a setting)</td><td>yes</td><td>yes</td><td>0</td></tr>
        <tr><td><b>beans</b> / whole food</td><td>~0.25&times; [15]</td><td>0.3</td><td>no</td><td>yes</td><td>+2</td></tr>
      </table></div>
      <p class="small">Conventional meat's small health penalty stands for antibiotics and contamination. Beans are &ldquo;the
      healthy choice&rdquo;.</p>
      <p><b>The premise.</b> Cultivated meat <i>is</i> animal tissue. Unlike a veggie burger, it keeps conventional meat's main
      advantage with mainstream shoppers, and it draws its buyers from conventional meat. How many it draws at equal price is the
      model's largest judgement, and it is the next paragraph.</p>
      <p><b>At equal price</b>, once the product is familiar, {{PARITY_NEUTRAL}}% of shoppers choose cultivated meat and
      {{CONV_PARITY}}% choose conventional meat. The {{PARITY_NEUTRAL}}% is a judgement, not a result. At first contact a US choice
      experiment found about 5% [8], and the setting assumes that a third of that first wariness fades. Because shoppers differ so much
      in how much they like it, a lower price wins fewer of them than one might expect. At half the price of meat {{HALF_PRICE}}% choose
      it, and if it were free {{FREE_PRICE}}% would, so {{NEVER_BUY}}% never take it. The first screen's slider sets this
      share, and the chart there shows what it does to the answer. Around the {{PARITY_NEUTRAL}}% setting, these other judgements move
      the share at equal price:</p>
      <div class="scrollx"><table class="attr">
        <tr><th>if cultivated meat…</th><th>share at equal price</th></tr>
        <tr><td>tastes as good (the setting)</td><td>{{PARITY_NEUTRAL}}%</td></tr>
        <tr><td>tastes a little worse (0.8)</td><td>{{AX_08}}%</td></tr>
        <tr><td>tastes noticeably worse (0.6)</td><td>{{AX_06}}%</td></tr>
        <tr><td>is judged tastier (1.1)</td><td>{{AX_11}}%</td></tr>
        <tr><td>tastes as good, and &ldquo;no slaughter&rdquo; matters a little to mainstream shoppers (0.5)</td><td>{{TH_05}}%</td></tr>
        <tr><td>tastes as good, and &ldquo;no slaughter&rdquo; matters a lot (1.0)</td><td>{{TH_10}}%</td></tr>
      </table></div>
      <p><b>Tied to data.</b> Price sensitivity follows grocery data for meat (1% dearer, 0.9% fewer purchases [4]).
      It is steeper for cultivated meat because an almost identical product is next to it (A1). Three weights are solved
      so that the model reproduces plant-based meat's ~1.2% share and ~89% mainstream buyers [14], plus an assumed ~6%
      of mainstream meals that skip meat (A4). Taste sets the scale for the rest. As a check, the same model with
      only the product's facts changed to plant-based milk's predicts about 15%, close to milk's share (see the chart of other
      products in <a href="#shoppers">Check the shopper model</a>). This is a weak test, because the milk facts are set by hand.
      <b>A harder test.</b> Six premium animal products (organic milk, cage-free, organic and omega-3 eggs, organic chicken and organic
      meat) take 2–7% of sales at 1.5 to 2.2 times the conventional price. Each is the ordinary product plus a virtue, which is what
      cultivated meat above equal price would be. With cultivated meat 8.5 times as price-sensitive as meat in general (the model's
      setting, written &kappa; in A1), the model reproduces them to within a factor of about 2.6. It over-predicted them sixfold at its
      earlier setting of 4. For example, it gives about {{ORG_CUTS}}% for a real-meat product at 1.44&times; the price of chicken cuts,
      and about {{ORG_MINCE}}% at 2.6&times; mince. It still over-predicts at small premiums and under-predicts at large ones.
      Real premium buyers look like a small group that pays whatever the premium, and one price-sensitivity number cannot
      capture that.</p>
      <p>At first contact the model gives {{COLD_PARITY}}% at equal price (Step 4). Price is the main limit on the share. At the
      Central case's shop price, {{R_CENTRAL}} times everyday meat, a US shopper chooses cultivated mince {{SHARE_AT_R_CENTRAL}}% of the
      time in the long run.</p>
      </details>

      <details class="step" id="step3"><summary><b>Step 3 · Every meat, every region.</b> The model repeats the choice at each meat's local
      price and adds up the results. In the Central case the median of the draws is {{CENTRAL_SHARE_P50}}% of the world's meat and seafood by
      weight, {{CENTRAL_US_P50}}% in the United States and {{CENTRAL_EU_P50}}% in Europe.</summary>
      <p>Cultivated meat costs about the same whatever animal it copies, but conventional prices vary. In the US,
      chicken mince costs about $5/kg, a beef steak $20 and sushi-grade fish $40. So the model runs each meat at its local
      price and adds up the results <b>by weight</b> (closest to the climate footprint) and <b>by value</b> (the market). Neither
      total counts animals. Most land animals raised for meat are chickens, and cultivated meat does worst there.</p>
      <p><b>Mince, cuts and premium products.</b> Shoppers like a cultivated cut less than cultivated mince, for two reasons. First, a cut
      is cells bound with plant protein, so it gets that much less of the credit shoppers give real meat: at {{CUT_CELLS_PCT}}% cells
      the penalty is {{BLEND_OFFSET}} points of score, and it grows as the share of cells falls. The same share of cells sets the cut's cost.
      Second, <b>wanting the genuine article</b>: nobody misses &ldquo;the real thing&rdquo; in a nugget, but for wagyu the breed <i>is</i> the
      product. A further penalty starts at {{PREMIUM_START}} times the species' cheapest form and reaches its full size,
      {{PREMIUM_EXTRA}} points, at {{PREMIUM_FULL}} times (wagyu, sushi-grade fish). Its size is a judgement, scaled by one setting
      that the draws take from 0.5 to 1.5. Every product has the same price sensitivity. The charts label a cut
      &ldquo;premium&rdquo; from {{PREMIUM_RATIO}} times its species' cheapest form. The label changes no number.</p>
      <p><b>What comes out</b> (the chart of share by type of meat in <a href="#where">Where and when</a>):</p>
      <ul>
        <li><b>Beef and seafood</b> are where cultivated meat can compete. Chicken and pork stay dearer even in the
        Best case.</li>
        <li><b>Premium products</b> get the biggest share of their own category, because cultivated meat is nearest their price.
        Wanting the genuine article limits that share, and the markets are small.</li>
        <li><b>Beef cuts and fish fillets</b> displace the most meat, in every case and region.</li>
      </ul>
      <p><b>Regions.</b> Europe is easiest, because meat is dear and shoppers are rich: the Central case's median there is
      {{CENTRAL_EU_P50}}%, against {{CENTRAL_US_P50}}% in the United States and {{CENTRAL_CHINA_P50}}% in China. Cheap chicken and pork
      lower the figures for China and for the world. Low-income regions are hardest, because meat is cheap and shoppers are
      price-sensitive (A2). The prices and mixes for low-income regions are rough (A7).</p>
      </details>

      <details class="step" id="step4"><summary><b>Step 4 · Over time.</b> The share starts near zero. It rises as the product
      spreads and stops feeling new. One product sold at the price of meat gets nine tenths of the way in about {{STAB_YEAR}} years.</summary>
      <ul>
        <li><b>Rollout.</b> Availability spreads like it does for other new products, first among early adopters and then by word of mouth
        (Bass diffusion [11], with standard rates from durable goods).</li>
        <li><b>Familiarity.</b> In a US choice experiment, only ~5% chose lab-grown meat at the same price as beef [8].
        The model starts about there ({{COLD_PARITY}}% at equal price) and lets the wariness fade with exposure.</li>
      </ul>
      <p class="example"><b>Worked example</b> (a US shopper, one everyday product held at the price of meat). The share starts
      from nothing at launch. It is {{Y10_SHARE}}% after 10 years and {{Y30_SHARE}}% after 30. The long-run ceiling is
      {{PARITY_NEUTRAL}}%. The path reaches nine tenths of it in year {{STAB_YEAR}}. The chart in
      <a href="#where">Where and when</a> draws the same path for the selected case's whole market, and prints its own year.</p>
      <p><b>For timing, the biggest unknown</b> is how wary people are at the start. Surveys range from ~5% (a cold choice
      experiment) to ~60% (&ldquo;cultivated chicken in a restaurant&rdquo;) [10]. The &ldquo;starting wariness&rdquo; setting
      runs from {{NX0_MIN}}% at &minus;3.5 to {{NX0_WARM}}% at +1.5, with {{NX0_NEUTRAL}}% at 0 (each at equal price). The warmest
      survey figure, ~60%, would need about +{{NX0_60}}, beyond the setting's range. It changes how fast the share grows, not how far. Plant-based meat follows the same rules but stalls,
      because its taste and price gaps do not fade.</p>
      </details>

      <details class="step" id="entry"><summary><b>Which products first.</b> Cultivated meat can already beat luxury products on price,
      but those markets are tiny. Commodity meat is out of reach, even in the Best case.</summary>
      <p>A luxury price is mostly not cost. A5 wagyu or caviar is dear because of breed, origin and scarcity
      (<i>economic rent</i>). Cultivated meat can copy the meat but not the pedigree. So the model compares its cost with
      the product's <b>everyday grade</b> (farmed salmon, crossbred wagyu). A <b>prestige core</b> of buyers never
      switches. The setting is 25%, a proxy taken from the only two published splits (wild salmon and bellota ibérico).</p>
      <p>Cultivated meat is already cheaper than foie gras, bluefin tuna, sea urchin and wagyu, and lobster is close. Each of these markets is only thousands to
      hundreds of thousands of tonnes a year. Commodity beef, pork and chicken are tens of millions of tonnes each, and
      the chart of which products it could enter first uses whole-category volumes. Cultivated meat stays out of reach for these at world prices. New technologies often start at the top
      and move down-market as costs fall [18], [19]. Foie gras stands out. It is unstructured, it is expensive, and more places are
      banning it on welfare grounds that do not apply to a cultivated version.</p>
      <p>That chart gives luxury products higher shares than the chart of share by type of meat does. It removes the prestige core and treats the
      rest like ordinary cuts. The chart of share by type of meat applies one penalty to the whole category, and that is the
      conservative view. The entry chart assumes sale at cost, so it shows reach and impact, not profit.</p>
      </details>

      <details class="step" id="cruxes"><summary><b>What would change the conclusions.</b> Cheaper classes of plant,
      better cells or cheap medium at scale would raise the share. Low density at scale or more lost runs would lower it. How shoppers
      react could change it either way.</summary>
      <ul>
        <li><b>Up:</b> animal cells grown in plants built like microbial fermentation plants, low-waste cells
        shown at pilot scale with a full mass balance, perfusion with a scalable way to hold cells back at 20,000
        litres, independently confirmed medium below $0.30/L at scale, or a meat tax.</li>
        <li><b>Down:</b> cells that reach only half the density in a pharma-style plant (the table in Step 1 gives that cost), or
        more runs lost to contamination than the cases assume. The &ldquo;Runs lost&rdquo; switch covers 0.2% to 2% of runs a day.</li>
        <li><b>Shoppers:</b> the share at equal price is a judgement. The draws take it from about {{EQS_P05}}% to {{EQS_P95}}% around
        the {{PARITY_NEUTRAL}}% setting, and the Best case sets it at {{BEST_EQS}}%. Taste and the value of &ldquo;no slaughter&rdquo;
        move it between {{AX_06}}% and {{TH_10}}% around that setting. Nobody can measure these before launch, so they stay settings.</li>
      </ul>
      </details>

      <details class="step" id="limits"><summary><b>What the model leaves out.</b> The model leaves out supply and competition, a full spread
      of tastes, niche entry routes, and eggs and dairy.</summary>
      <ul>
        <li><b>Calibrated, not estimated.</b> No purchase data exist yet, so the shopper side is a set of stated judgements, not a
        forecast.</li>
        <li><b>Prices are given.</b> The model has no supply response, competition or capacity limits.</li>
        <li><b>Two kinds of shopper</b>, with a spread of liking for cultivated meat among them, and one price sensitivity.
        Convenience enters only through the rollout.</li>
        <li><b>Timing is rougher than the ceilings.</b> It uses a durable-goods Bass curve plus a familiarity fade, and the two may
        overlap. Costs stay fixed.</li>
        <li><b>A fixed mix of meats</b> in each region. A meat tax scales all prices equally.</li>
        <li><b>The existing price ladder.</b> Niche routes (pet food, new species and &ldquo;no animal harmed&rdquo; products)
        score as small.</li>
        <li><b>Meat only.</b> Cultivated egg and dairy proteins use precision fermentation and need their own
        model.</li>
      </ul>
      </details>

      <details class="step" id="appendix"><summary><b>Technical appendix.</b> Equations, price sensitivity, income,
      calibration, the entry-point maths, data, questions a sceptic might ask, parameters and references.</summary>

      <h5>A0. The equations</h5>
      <p><b>Step 1, the price ratio.</b></p>
      \[ R \;=\; \frac{\Big(\overbrace{\iota\,\eta\,p_{\rm med}}^{\text{medium}} \;+\; \overbrace{h}^{\text{plant}}
         \;+\; \overbrace{k}^{\text{assembly (cuts)}} \;+\; \overbrace{a}^{\text{to the shelf}}\Big)\Big/\big(1-\overbrace{m}^{\text{shop's margin}}\big)}{p_c\,t} \tag{1} \]
      <p>This is the form for the process a company reports. The cases compute the cost of the cells from the tank physics instead
      (Step 1), and the rest of the equation is the same. \(\iota\): litres of medium per kilo; \(\eta\): cell efficiency (1 = as reported); \(p_{\rm med}\): medium
      price; \(h\): plant running cost; \(k\): assembling a cut (cuts only). For a cut the cell cost (medium plus plant) is
      multiplied by \(c\), the share of the cut that is cells, and the plant protein that makes up the rest is added at its price; \(a\): forming, packing and cold chain per kilo; \(m\): the shop's
      gross margin as a share of the shelf price; \(p_c\): conventional price;
      \(t\): meat-tax multiplier. The medium cost never falls below the feedstock dissolved in it.</p>
      <p><b>Step 2, the score and the shares.</b></p>
      \[ V_j \;=\; \underbrace{\alpha\ln(y_{\rm eff}-p_j) \;-\; \lambda\,(d_j)^{+} + (d_j)^{-}}_{\text{price}}
         \;+\; \underbrace{w^{t}(a_j-1)}_{\text{taste}} \;+\; \underbrace{w^{rt}\,b_j}_{\text{real meat}}
         \;+\; \underbrace{w^{s}\,g_j}_{\text{no slaughter}} \;+\; \underbrace{w^{h}\,\zeta_j}_{\text{health}}
         \;+\; \underbrace{\nu_j+\tau_j}_{\text{novelty; cut, premium}} \tag{2} \]
      \[ P_j = \frac{e^{V_j}}{\sum_k e^{V_k}}, \qquad
         \text{share}_j = w_{\rm eth}\,P^{\rm ethical}_j + (1-w_{\rm eth})\,P^{\rm mainstream}_j \tag{3} \]
      <p>Price enters twice: through the dollars it takes from income (\(p_j = R_j\,p_c\); \(y_{\rm eff}\) is an income
      measure, A2), and through the premium over conventional meat, \(d_j = R_j-1\), split into its positive part
      \((d_j)^{+}\) and negative part \((d_j)^{-}\) (at the default \(\lambda=1\) the two terms are simply \(-d_j\); A3).
      \(a_j\): taste (1 = as good as conventional); \(b_j\), \(g_j\): 1 if real meat, 1 if slaughter-free; \(\zeta_j\):
      health image. The weights \(w\) (A4) differ between the two kinds of shopper for no slaughter, real meat and
      health. \(\nu_j\) (novelty) is zero unless set. \(\tau_j\) is how much less shoppers like a cultivated cut or premium product than cultivated mince (A5).
      For cultivated meat the score also carries each shopper's own liking, which is spread around a mean set so that the share at equal
      price comes out at its setting (A1).</p>
      <p><b>Step 3, adding up.</b></p>
      \[ \text{share}_{\rm vol} = \sum_i \frac{\omega_i}{\sum_k \omega_k}\,s_i, \qquad
         \text{share}_{\rm val} = \sum_i \frac{p_i\,\omega_i}{\sum_k p_k\,\omega_k}\,s_i \tag{4} \]
      <p>\(s_i\): cultivated's share of meat type \(i\); \(\omega_i\): that type's share of meat eaten (the listed
      weights sum to slightly more than 1 in some regions, hence the normalisation); \(p_i\): its local price.</p>
      <p><b>Step 4, over time.</b></p>
      \[ \text{share}(t) = F(t)\times \text{ceiling}\big(\nu(t)\big), \qquad
         \nu(t) = \nu_x + (\nu_{x0}-\nu_x)\,e^{-r\,E(t)} \tag{5} \]
      <p>\(F(t)\): the fraction of the market reached, a Bass curve with rates \(p_{\rm B}\) (early adopters) and
      \(q_{\rm B}\) (word of mouth). Novelty \(\nu\) fades from its starting value \(\nu_{x0}\) toward its long-run value \(\nu_x\) as
      cumulative exposure \(E(t)\) grows, at speed \(r\). The ceiling is the Step 2 share at that novelty.</p>


      <h5>A1. Price sensitivity: where the price weight comes from</h5>
      <p>Grocery data give the <b>price elasticity</b> of meat as a category, \(\varepsilon \approx -0.9\) [4].
      This means that meat 1% dearer sells 0.9% less. Meat as a whole has no close substitute, so it is fairly insensitive to price. A single
      cultivated product does have a close substitute, which is conventional meat on the same shelf. So a single product is more sensitive than the category.
      At the calibration price the sensitivity is \(4 \times (-0.9) = -3.6\), the usual gap between a product and its category.
      That sets the price weight that every product shares. Cultivated meat's price
      <i>difference from the conventional meat beside it</i> then counts \(\kappa/4\) times as much again, because the two are
      near-identical (\(\kappa = 8.5\) by default). The model solves the price
      weight \(\beta\) (the slope of the price score) so that it delivers exactly that sensitivity at the calibration
      price \(p_x\) and at cultivated meat's share there, \(s_x\). These two depend on each other, so the model solves them together:</p>
      \[ \beta=\frac{\kappa\,\varepsilon}{p_x\,(1-s_x)}+\frac{\lambda}{p_c},\qquad
         \alpha=-\beta\,(y_{\rm ref}-p_x) \tag{A1} \]
      <p>The \(\lambda/p_c\) term adds back the part of the price response that the reference-price
      term in Eq. (2) already contains. So \(\kappa\) sets the level of sensitivity, and \(\lambda\) sets only its shape around parity.
      The price \(p_x\) is a fixed calibration price of ${{ANCHOR_PRICE}}/kg. The model holds it fixed, so that correcting a cost
      changes cultivated meat's price but not how shoppers respond to price. At a higher shop price the model is more price-sensitive.</p>
      <p><b>Evidence for \(\kappa\) and for the spread of liking.</b> There are two kinds. <b>First,</b> Van Loo, Caputo and Lusk [8]
      priced lab-grown meat at six levels. The paper reports no elasticity; simulating its fitted model gives about &minus;1.5 at equal
      price (&minus;1.1 to &minus;1.65 across its four groups). Its main finding is that shoppers differ widely in how much they like
      lab-grown meat: about half prefer it to buying nothing, half do not. With every shopper alike this model gave &minus;3.3 in that
      setting. With the spread of liking added in November 2026 it gives {{KAPPA4_LUSK_ELAS}}, and matches the experiment
      at all four prices tested. The spread is a Student's t with a standard deviation of {{LIKING_SD}} points of score and {{LIKING_TAIL}}
      degrees of freedom: most shoppers sit near the typical liking, and a few are far from it in either direction. It is fitted to
      this experiment and to the shares that premium real meats hold at two to four times the ordinary price, together. <b>Second,</b> premium animal products show what share a
      product takes when it is the conventional one plus a virtue, at a higher price. Organic milk, cage-free,
      organic and omega-3 eggs, organic chicken and organic meat take 2–7% of volume at 1.5 to 2.2 times the
      conventional price. At \(\kappa = 4\), this model's default until November 2026, the model over-predicts those six
      about sixfold. At 8.5 the typical miss is under threefold, and the best fit is at 10. So 8.5 is the best fit
      to the premium products within what the experiment allows. \(\kappa\) changes nothing at equal price. Once
      shoppers are familiar with the product, the model's elasticity is about {{ELAS_10}} at parity, {{ELAS_15}} at
      \(R=1.5\) and {{ELAS_24}} at \(R=2.4\). At one and a half times the price of meat, \(\kappa=4\) gives a share of about {{KAPPA_LO}}%,
      8.5 about {{KAPPA_MID}}% and 10 about {{KAPPA_HI}}%. \(\kappa\) plays the role that a nested logit's
      similarity parameter would play for a &ldquo;real meat&rdquo; nest, but it applies to price only.</p>

      <h5>A2. Income</h5>
      <p>The income part of the price score, \(\alpha\ln(y_{\rm eff}-p_j)\), has the Berry–Levinsohn–Pakes form [12].
      The same premium is a bigger bite of a smaller income, so poorer shoppers are more sensitive to price. Taken
      literally, this makes poor shoppers about six times as price-sensitive as rich ones, which is too steep for
      food. So the model damps income, \(y_{\rm eff}=y_{\rm ref}\,(y/y_{\rm ref})^{\phi}\), with \(\phi=0.5\) matching the
      roughly twofold gap in the data [15]. (\(\phi=0\) removes income. US results do not depend on \(\phi\).) For
      the same product at one and a half times the price of meat, this gives {{SHARE_15_US}}% in the US, {{SHARE_15_CHINA}}% in
      China and {{SHARE_15_NIGERIA}}% in Nigeria. Wealth relaxes price sensitivity but does not erase the other differences. Even a very rich shopper
      buys cultivated meat only {{INCOME_CAP}}% of the time at that price.</p>

      <h5>A3. Loss aversion (symmetric by default)</h5>
      <p>People judge a price against the familiar price of the conventional product, and a premium can feel like a
      loss [13]. The term \(-\lambda(d_j)^{+}+(d_j)^{-}\) rewards a discount at rate 1 and penalises a premium at rate
      \(\lambda\). The default \(\lambda=1\) is symmetric, and the slider goes up to Tversky and Kahneman's 2.25. The model leaves it
      symmetric by default for three reasons. First, it barely changes the result once \(\beta\) is re-fitted (at one and a half
      times the price of meat, {{LAMBDA_1}}% at \(\lambda=1\) against {{LAMBDA_225}}% at 2.25). Second, cultivated meat data cannot identify it. Third,
      measured loss aversion largely reflects differences in price sensitivity between shoppers (Bell and Lattin,
      2000), and \(\kappa\) already contains those.</p>

      <h5>A4. Calibration, and the attribute weights</h5>
      <p><b>Fixed from data:</b> plant-based meat's price premium (+77% [14]) and taste (0.8 [7]), and the ethical
      share (5% [7]). <b>Solved:</b> the mainstream real-meat weight and the two health weights, so that the model
      reproduces (i) the ~89% of plant-based buyers who are mainstream [14], (ii) ~6% of mainstream meals skipping meat
      by choice, and (iii) the ethical shoppers' small plant-based share. Together these give plant-based meat its
      observed ~1.2%. Moving the ethical share, \(\lambda\), \(\kappa\) or income re-solves them live, so plant-based
      stays anchored.</p>
      <p>Only differences between scores matter in this kind of model, so one weight has to set the scale. Taste sets it
      (\(w^t = 5\)). This is anchored to willingness-to-pay studies that rank taste first (taste about twice health and three
      times safety, Malone and Lusk 2017). Each weight slider shows its size relative to taste. The solved mainstream
      health weight comes out at {{HEALTH_TASTE_RATIO}}&times; taste, which is lighter than the ~0.5&times; in those studies.
      Beans' appeal comes from their health score (+2) times a solved weight, not from a free constant.
      The data pin down only the product of the two. Without this, plant-based meat would roughly triple, with
      mostly vegetarian buyers, which contradicts the data.</p>
      <div class="scrollx"><table class="pt"><tr><th>weight</th><th>symbol</th><th>mainstream</th><th>ethical</th><th>how it is set</th></tr>
        __WEIGHTS_TABLE__
      </table></div>

      <h5>A5. Three different &ldquo;is it real?&rdquo; questions, and how much less shoppers like cuts and premium products</h5>
      <ul>
        <li><b>Real meat</b> (\(b\)) asks whether it is animal tissue. The answer is permanent and the same for every product, and it is the reason
        cultivated meat takes buyers from conventional meat.</li>
        <li><b>Novelty</b> (\(\nu\)) asks whether it is new, strange or safe. It is the same for a nugget and a steak, and it fades with
        familiarity (Step 4).</li>
        <li><b>The genuine article</b> (\(\tau\)) asks whether, for this occasion, the shopper wants the original. It depends on the product and is
        permanent. It is irrelevant for a nugget and decisive for wagyu.</li>
      </ul>
      <p>They are separate because they behave differently. A cultivated nugget faces novelty but nobody wants
      the original nugget. A cultivated wagyu faces both. A fourth attribute, <b>health image</b> (\(\zeta\)), is separate again. It
      is 0 by default, because surveys find both a &ldquo;clean meat&rdquo; appeal and an &ldquo;ultra-processed&rdquo;
      aversion. The draws take it between &minus;0.5 and +0.5.</p>
      <p>In formulas. For mince and other unstructured products \(\tau=0\). For a cut made of a share \(c\) of cells,
      priced at \(q\) times its species' cheapest form:</p>
      \[ \tau=\underbrace{-(1-c)\,w^{rt}_M}_{\text{part plant protein}}\;+\;\rho\,\tau_{\rm prem}\,
         \min\!\Big(1,\max\!\Big(0,\frac{\ln(q/{{PREMIUM_START}})}{\ln({{PREMIUM_FULL}}/{{PREMIUM_START}})}\Big)\Big) \tag{A5} \]
      <p>The first term is derived: \(w^{rt}_M\) is the weight mainstream shoppers put on real meat (A4), and a cut that is one-fifth
      plant protein gets four-fifths of that credit. \(c\) is the same share of cells that sets the cut's cost in Eq. (1). The second
      term is a judgement: \(\tau_{\rm prem}={{PREMIUM_EXTRA}}\) is the full penalty on a cultivated version of a premium product, and
      \(\rho\) scales it. It rises smoothly with price, so no product changes sharply at a threshold, and because \(q\) is taken
      per species every species can have premium products. Wagyu and sushi-grade fish are well attested.
      Organic chicken and heritage pork are real but smaller, so they have little volume. Price sensitivity is the same for every
      product. Until 19 November 2026 the model also made buyers of cuts and premium products less sensitive to price [5]; that
      raised cultivated meat's share wherever it was the dearer product, and it was removed.</p>

      <h5>A6. Entry points: the equations behind the chart of which products it could enter first</h5>
      <p>A product's headline price splits into the accessible price and the rent. The model takes cultivated meat's price ratio
      against the accessible price only (Rosen's hedonic pricing [16]):</p>
      \[ p^{\rm auth} = p^{\rm base} + \underbrace{(p^{\rm auth}-p^{\rm base})}_{\text{rent}},\qquad
         R = \frac{c_x}{p^{\rm base}},\qquad c_x = c_{\rm bio} + k\,[\text{cut}] + m \tag{A6a} \]
      <p>A prestige core, a share \(\chi\) of the category's volume \(Q\), pays the rent and never switches. Luxury
      sellers keep their price and give up volume rather than discount, which is the classic Veblen pattern [17]. Only the
      rest is reachable. Cultivated meat wins a share \(s\) of it from the same shopper model as Step 2, using \(\tau\) for
      mince or for a cut (A5) without the premium part. (The premium part stands for the prestige core, which the model has already removed.)</p>
      \[ Q^{\rm reach} = (1-\chi)\,Q,\qquad s = S\big(R;\ \tau_{\rm mince\ or\ cut}\big),\qquad
         D = s\cdot Q^{\rm reach}\quad(\text{kt/yr displaced}) \tag{A6b} \]
      <p><b>Zones.</b> A product is <i>about equal</i> if the accessible price is within $3 of cultivated meat's cost. It is <i>cheaper now</i> if
      the accessible price is above that. It is <i>only in the best case</i> if the accessible price is above the best case's cost. Otherwise it is
      <i>never on price</i>. A single-grade
      product (no rent, \(\chi=0\)) reproduces the chart of share by type of meat exactly, so the two views agree. The model counts wanting the genuine
      article once, as removed volume for the prestige grade and through \(\tau\) for the accessible grade.
      The model has limits. It does not model margin or profit, its shopper model is calibrated on meat (so it is indicative for luxury
      and seafood), and it treats each product in isolation. The accessible and headline prices come from sources for each
      product (June 2026 retail and wholesale, with the basis shown when you hover over a bubble). Shark fin's price is an estimate.</p>

      <h5>A7. Prices, the markup, and what people eat</h5>
      <p>Conventional retail prices by region and kind of product, the \(p_c\) in Eq. (1):</p>
      <div class="scrollx" id="pricetable"></div>
      <p class="small">Prices: GlobalProductPrices (retail, January 2026), cross-checked
      against USDA ERS and BLS for the US. Volumes: USDA ERS per-capita availability (US); OECD-FAO Agricultural
      Outlook 2024 and FAO food balance sheets (Europe, China, world). The mix of meats differs by region. China is
      two-thirds pork, the US is about half poultry, and Europe is pork-led and shifting to poultry. Prices and mixes for India,
      Brazil and Nigeria are rough.</p>
      <p><b>The markup is part per kilo and part a percentage.</b> Forming, packing, cold chain and transport cost the same per
      kilo whatever the product's price: USDA's monthly meat prices for 1970&ndash;2025 show shop prices moving about dollar for
      dollar with wholesale prices over one to five years, not by the 1.7&ndash;2.5 times a pure percentage markup would give.
      The shop's own margin is a percentage: US meat departments run at about 28&ndash;32% of the shelf price, so a product
      that costs several times more carries more dollars of margin. Fitted to USDA's 2025 spreads with a 28% margin, the
      per-kilo part is $1.6 for chicken and $2.9 for beef. Until November 2026 the model added a flat $5. At the Central case's most-likely-values cost,
      the shelf price is ${{RETAIL_CENTRAL}} under this rule, ${{RETAIL_CENTRAL_FLAT}} under the old flat $5, and
      ${{RETAIL_CENTRAL_PROP}} if the whole spread were a percentage. Both parts have sliders.</p>

      <h5>A8. Questions a sceptic might ask</h5>
      <p><b>Isn't {{PARITY_NEUTRAL}}% at equal price just assumed?</b> Yes. It is a judgement, and the model says so. Until
      November 2026 two real meats at the same price split the market about evenly, which no survey supports. The share is now a
      setting with a wide range ({{EQS_P05}}% to {{EQS_P95}}% in the draws), the first screen's chart shows the answer across that range,
      and <a href="#moves">What would move it most</a> ranks it against the cost.</p>
      <p><b>Why not a nested logit?</b> The shared real-meat attribute and the two kinds of shopper already make
      cultivated take its share almost entirely from conventional meat, which is what a nest would do, with fewer
      unobservable parameters.</p>
      <p><b>Is there really no fitted constant?</b> Almost none. Beans' appeal is a labelled attribute (health) times a
      solved weight, not a free constant. The model assumes the attribute's position (+2), so only the product of the two is identified
      (A4).</p>
      <p><b>Isn't the premium penalty just novelty again?</b> No. Novelty is the same for every product and fades.
      Wanting the genuine article depends on how premium the product is, and is permanent (A5).</p>
      <p><b>The experiment behind the ~5% also had plant-based at 23% at equal price. Why doesn't the model?</b>
      The model is fitted to what plant-based meat actually sells (~1.2%). It predicts about {{PB_PARITY}}% for plant-based meat
      among mainstream shoppers at equal price and taste. Hypothetical choice experiments tend to overstate adoption of new products. The model uses that
      experiment only for cultivated meat's starting wariness and price sensitivity.</p>
      <p><b>Why no habit term?</b> Habit cannot be separated from preference without panel data (Heckman [13]). In
      this model, the slow rollout and fading novelty of Step 4 stand in for habit.</p>
      <p><b>Why is loss aversion symmetric by default?</b> See A3.</p>

      <h5>A9. Parameters and sources</h5>
      <p>This table lists every shopper setting with its symbol, the model's value, its range, its place in the equations and its source. The full
      datasheet, with every number and its uncertainty range, is <a href="https://github.com/PabloAMC/Cultivated_meat/blob/main/inputs.py">inputs.py</a>.</p>
      <div class="scrollx" id="paramtable"></div>

      <h5>References</h5>
      <ul class="refs">
        <li id="ref1"><b>[1]</b> <b>Medium use and price, plant cost, as reported by a company:</b> SuperMeat (2024).
        <i>Cultivating the future: a deep dive into cost-effective cultivated meat production</i> (company report,
        not peer reviewed).</li>
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
        <li id="ref6"><b>[6]</b> <b>The cost of a cut is built from analogues:</b> no cost study covers structuring cultivated
        meat; Humbird 2021, CE Delft 2021 and Risner <i>et al.</i> 2021 all stop at unstructured cells. Wildtype (FDA memo, 2025),
        Aleph Farms (2025) and Upside (2026) now bind cells with plant protein after harvest instead of growing tissue on a scaffold.
        The assembly cost comes from GFI's 2021 costing of plant-protein extrusion, surimi forming and binder prices; the cell share
        from products on sale (10 to 30% cells). Sources in the model's <code>research_notes/structuring_cost.md</code>.</li>
        <li id="ref7"><b>[7]</b> <b>Plant-based taste (only ~16% reach blind-taste parity):</b>
        <a href="https://www.nectar.org/sensory-research/2025-taste-of-the-industry" target="_blank" rel="noopener">NECTAR, Taste of the Industry (2025)</a>.
        <b>5% vegetarian or vegan:</b>
        <a href="https://news.gallup.com/poll/510038/identify-vegetarian-vegan.aspx" target="_blank" rel="noopener">Gallup (Brenan, 2023)</a>: 4% vegetarian, 1% vegan.</li>
        <li id="ref8"><b>[8]</b> <b>~5% choose lab-grown at equal price; its price elasticity:</b>
        Van&nbsp;Loo, E.&nbsp;J., Caputo, V. &amp; Lusk, J.&nbsp;L. Consumer preferences for farm-raised meat,
        lab-grown meat, and plant-based meat alternatives. <i>Food Policy</i> <b>95</b>, 101931 (2020),
        <a href="https://doi.org/10.1016/j.foodpol.2020.101931" target="_blank" rel="noopener">doi:10.1016/j.foodpol.2020.101931</a>.
        US choice experiment: at equal price, lab-grown ~5%, plant-based 16% and 7%, beef 72%; even at 50% discounts
        beef keeps the majority. Its fitted model implies an own-price elasticity of about &minus;1.5 at equal price, and a wide
        spread of liking for lab-grown meat across respondents.</li>
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
<li id="ref20"><b>[20]</b> <b>A measured 20-day run; no longer the cost anchor:</b> Pasitka, L. <i>et al.</i>
        Empirical economic analysis shows cost-effective continuous manufacturing of cultivated chicken
        using animal-free medium. <i>Nature Food</i> <b>5</b>, 693&ndash;702 (2024).
        <a href="https://doi.org/10.1038/s43016-024-01022-w" target="_blank" rel="noopener">doi:10.1038/s43016-024-01022-w</a></li>
      </ul>
      </details>
      <p>Full results: <a href="https://github.com/PabloAMC/Cultivated_meat/blob/main/RESULTS.md">RESULTS.md</a>.
      Code and tests: <a href="https://github.com/PabloAMC/Cultivated_meat">github.com/PabloAMC/Cultivated_meat</a>.</p>
</div></details>
  <section id="about">
    <h3>About this page</h3>
    <p><b>Views.</b> The views expressed on this page are purely those of the author, Pablo Antonio Moreno Casares.
    They may not in any circumstances be regarded as stating an official position of the European Commission.</p>
    <p><b>How it was made.</b> The model and this page were built with the help of an AI assistant (Claude,
    Anthropic). No human expert has reviewed the model yet. Every number is a model result computed from the inputs listed in the code, each with its source.</p>
    <p><b>Not advice.</b> This page is for research and discussion. It is not investment, business or policy advice.
    Market shares are long-run ceilings under stated assumptions, not forecasts.</p>
  </section>
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
MODEL.sliders.forEach(s => { state[s.key] = s.start;
  if (s.solved) state[s.key + "_ovr"] = false; });   // SOLVED weights start on AUTO (not overridden)
MODEL.toggles.forEach(t => state[t.key] = false);
state.mc = false;
state.curveType = null;                          // shared species selector — drives panels 4a AND 4b
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
  if(denom>0) beta=Math.min(beta,K.w_ratio*(eps/K.eps_own)*(yEff-pr)/denom-1e-6);   // discount slope incl. w_ratio*f
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
  // per-tier / per-draw override scales the ratio term too (mirror of market_share ratio_scale = eps/eps_own)
  const rScale=(o.eps===undefined?1:o.eps/K.eps_own);
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
    const Vl=K.w_ratio*rScale*(-K.loss_aversion*Math.max(0,prem)   // loss side: penalise a premium at -lambda
              +Math.max(0,-prem));                                 // gain side: reward a discount (ratio-based, no income scaling)
    // per-FACTOR components (mirror of market_share._utilities components) — summed to V[j]
    CO.price[j]=Vp+Vl; CO._vp=CO._vp||[]; CO._vl=CO._vl||[]; CO._vp[j]=Vp; CO._vl[j]=Vl;
    CO.taste[j]=K.w_taste*taste[j]; CO.slaughter_free[j]=wSl*slaughter[j];
    CO.real_meat[j]=wRt*realtissue[j]; CO.health[j]=wH*health[j]; CO.asc[j]=xi[j];
    V[j]=CO.price[j]+CO.taste[j]+CO.slaughter_free[j]+CO.real_meat[j]+CO.health[j]+CO.asc[j];
  }
  // CLOSENESS TO CONVENTIONAL (mirror of market_share._utilities): cultivated's price utility measured from
  // conventional's counts kappa/kappa_base times, on both channels; nothing else moves.
  const kr=(o.kap===undefined?K.cult_sub_mult:o.kap)/C.kappa_base;
  if(kr!==1){ const px=CO._vp[1]+kr*(CO._vp[3]-CO._vp[1])+kr*CO._vl[3]; V[3]+=px-CO.price[3]; CO.price[3]=px; }
  delete CO._vp; delete CO._vl;
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
  if(o.present && o.lsd>0){            // shoppers differ in liking for cultivated meat (mirror of market_share._segment)
    const nd=C.spread_nodes, wt=C.spread_weights, Vx=nd.map(z=>V[3]+o.lmean+o.lsd*z);
    const m=Math.max(V[0],V[1],V[2],Math.max.apply(null,Vx)), e=[0,1,2].map(j=>Math.exp(V[j]-m)), es=e[0]+e[1]+e[2];
    let iw=0,px=0; Vx.forEach((v,k)=>{const ex=Math.exp(v-m), inv=wt[k]/(es+ex); iw+=inv; px+=ex*inv;});
    return {w:e[0]*iw,c:e[1]*iw,p:e[2]*iw,x:px};
  }
  if(o.present){const P=softmax(V);return {w:P[0],c:P[1],p:P[2],x:P[3]};}
  const P=softmax(V.slice(0,3));return {w:P[0],c:P[1],p:P[2],x:0};
}
// lsd / lmean / eqs: the spread of liking for cultivated meat (mirror of market_share.share). lsd 0: every shopper alike, no shift
// (the calibration and the premium-meat checks). lmean sets the mean shift; eqs a long-run share at equal price (a draw), read off
// K.liking_table; neither: K.liking_mean.
function likingFor(K,eqs){const t=K.liking_table; if(!t) return 0; const g=C.liking_grid;
  if(eqs<=t[0]) return g[0]; for(let i=1;i<t.length;i++){ if(eqs<=t[i]) return g[i-1]+(g[i]-g[i-1])*(eqs-t[i-1])/(t[i]-t[i-1]); } return g[g.length-1];}
function shareCalc(R,K,{ax=1,tfM=0,toff=0,eps,income,pricePb,aP,nbx=0,nbp=0,present=true,which="x",rtx,rtp,hx,hp,pRef,kap,lsd,lmean,eqs}){
  const sd=(lsd===undefined?(K.liking_sd||0):lsd);
  const mean=(sd>0)?(lmean!==undefined?lmean:(eqs!==undefined?likingFor(K,eqs):(K.liking_mean||0))):0;
  const o={ax,tfM,toff,present,nbx,nbp,eps:(eps===undefined?K.eps_own:eps),
           income:(income===undefined?K.income_ref:income),
           pricePb:pricePb, tasteP:(aP===undefined?undefined:aP-1), rtx:rtx, rtp:rtp, hx:hx, hp:hp, pRef:pRef, kap:kap, lsd:sd, lmean:mean};
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
   the fixed calibration price C.anchor_price (inputs elasticity_anchor_price; frozen so cost
   corrections do not change price sensitivity) and cultivated's modeled share there. A short
   fixed point co-solved with the calibration. (Absorbing lam into beta is the double-counting fix: loss_aversion then only
   shapes the kink at parity, not the elasticity level.) */
function deriveBeta(K){
  const pAnchor=C.anchor_price;
  K.anchor_price=pAnchor;
  const Rtoday=pAnchor/K.p_conv_anchor, epsX=K.eps_own*C.kappa_base;   // kappa's extra acts on x only (utilities)
  const lam=K.w_ratio*K.loss_aversion/K.p_conv_anchor;   // loss-side semi-elasticity the reference term adds
  // MONOTONICITY GUARD (mirror of market_share._derive_beta): cap beta below 1/p_conv so the
  // DISCOUNT side (where the loss term is off) always slopes downward — a cheaper product must
  // never lose share. Inert at the default; only bites in the high-loss_aversion tail.
  // WHY λ is capped at the TK 2.25 anchor (see the loss_aversion slider): once this cap binds
  // (λ≈2.6 at default p_conv) β can no longer fully absorb the loss-aversion slope, so the realised
  // elasticity would drift off the eps_own*κ target. Stopping at 2.25 keeps the "λ reshapes the kink,
  // not the level" property true across the whole admissible range.
  // SIGN GUARD (mirror of market_share._derive_beta, 2026-11-16): beta, the dollar channel's slope, is never positive,
  // or shoppers would gain from paying more. Inert at the defaults; binds once loss_aversion*w_ratio exceeds about 1.6.
  const betaCap=Math.min(K.w_ratio/K.p_conv_anchor-1e-3, 0);
  let s=0;
  for(let it=0;it<40;it++){
    K.beta_ref=Math.min(betaCap, epsX/(pAnchor*(1-s))+lam);  // set before solveCalibration uses betaPrice
    solveCalibration(K);
    // beta is calibrated to cultivated AS A REAL-MEAT product (rtx=1), so the fixed-point share
    // uses rtx=1 regardless of the user's real_tissue_x dial (matches Python _derive_beta, which
    // is stable in rtx). The dial then shifts the OUTCOME, not the price-coefficient calibration.
    const sNew=shareCalc(Rtoday,K,{ax:1,tfM:0,rtx:1,kap:C.kappa_base,lsd:0});   // at kappa_base, every shopper alike: beta depends on neither kappa nor the spread
    if(Math.abs(sNew-s)<1e-9){s=sNew;break;}
    s=sNew;
  }
  K.beta_ref=Math.min(betaCap, epsX/(pAnchor*(1-s))+lam);
  return solveCalibration(K);                  // final calibration at the converged beta
}
/* effective constants from the current sliders, then derive beta + run the calibration solve. */
function effConsts(s){
  const K=Object.assign({},C);
  ["cult_sub_mult","loss_aversion","w_ratio","w_eth","eps_own","real_tissue_x","real_tissue_p","health_x","health_p","income_gradient",
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
  ["liking_sd","equal_price_share"].forEach(k=>{if(k in s)K[k]=s[k];});
  deriveBeta(K);
  return solveLiking(K);
}
// the mean liking shift that gives the long-run share at equal price (mirror of market_share._solve_liking)
function solveLiking(K){
  if(!(K.liking_sd>0)){K.liking_mean=0; K.liking_table=null; return K;}
  const par=m=>shareCalc(1,K,{ax:1,tfM:0,nbx:0,hx:0,lmean:m});
  const g=C.liking_grid; let lo=g[0], hi=g[g.length-1];
  for(let i=0;i<80;i++){const mid=0.5*(lo+hi); if(par(mid)<K.equal_price_share) lo=mid; else hi=mid;}
  K.liking_mean=0.5*(lo+hi); K.liking_table=g.map(par);
  return K;
}
function biomass(s){
  if(s.cost_override!=null) return s.cost_override;       // a cost scenario sets the cost (page_scenarios.js)
  return mediaCost(s.media_price,s.efficiency)+s.overhead+(s.cleanroom?C.cleanroom_cost:0);}
// Shelf price from the cost before the shelf: per-kg costs plus the shop's percentage margin. THE one place this
// rule lives in the page (mirror of price_ratio.shelf_price); `mk`/`mg` default to the settings `s`.
// a kilo of cut: cut_cells of cells, the rest plant-protein matrix, plus assembly (mirror of price_ratio.structured_cost)
function cutCost(cells,s){return s.cut_cells*cells+(1-s.cut_cells)*C.matrix_price+s.scaffold;}
function shelfPrice(x,s,mk,mg){mk=(mk===undefined?s.markup_add:mk); mg=(mg===undefined?s.retail_margin:mg); return (x+mk)/(1-mg);}
function parityCost(s){return C.p_conv_anchor*s.meat_tax*(1-s.retail_margin)-s.markup_add;}
function basicR(s){return shelfPrice(biomass(s),s)/(C.p_conv_anchor*s.meat_tax);}
function speciesBases(market){const b={};market.forEach(mt=>{const a=animalOf(mt.name);
  b[a]=Math.min((a in b)?b[a]:Infinity,mt.p_conv);});return b;}
// a LABEL for charts and tables (basic / cut / premium); nothing numeric depends on it (mirror of meat_market.tier)
function tierOf(mt,base){return !mt.structured?"basic":(mt.p_conv>=C.PREMIUM_RATIO*base?"premium":"cut");}
// how far a product sits in its species' premium range, 0 to 1: 0 at PREMIUM_START x the species' cheapest form or below,
// 1 at PREMIUM_FULL x or above, linear in the logarithm of price between (mirror of meat_market.premium_ramp)
function premiumRamp(mt,base){
  if(!mt.structured) return 0;
  const x=Math.log(mt.p_conv/base/C.PREMIUM_START)/Math.log(C.PREMIUM_FULL/C.PREMIUM_START);
  return Math.max(0,Math.min(1,x));}
// per-type price ratio, tier label and premium ramp, shared by penetration / monteCarlo / perTypeMC so the
// R = shelfPrice(cells, or cutCost(cells) for a cut) / (p_conv*meat_tax), cells = biomass*cost_mult, lives in ONE place
// (mirror of meat_market._rollup's per-type R). `b` biomass $/kg, `mk` per-kg costs to the shelf, `mg` the shop's margin.
function typeR(mt,b,mk,s,bases,mg){
  const cells=b*mt.cost_mult, price=mt.p_conv*s.meat_tax, base=bases[animalOf(mt.name)];
  return {R:shelfPrice(mt.structured?cutCost(cells,s):cells,s,mk,mg)/price, t:tierOf(mt,base), ramp:premiumRamp(mt,base)};
}
// Utils added to cultivated meat's utility for a product, against cultivated mince (mirror of meat_market.tier_offset).
//   mince and other unstructured products: 0
//   a structured product: BLEND + PREMIUM
//     BLEND   = -(1 - cells) x K.w_realtissue_M: a cut that is part plant protein gets that much less of the real-meat credit.
//               `cells` is the SAME cell share the cut's cost uses (s.cut_cells; cutCost above). Not scaled by r.
//     PREMIUM = r x (the full premium penalty) x ramp: r is the premium-resistance slider, ramp is premiumRamp. The full
//               penalty is the auth_premium_extra slider, C.AUTH_PREMIUM_EXTRA when unset.
// Every product uses the model's own price sensitivity (there is no per-tier multiplier since 2026-11-19).
function _auth(key,dflt){return (typeof state!=="undefined" && (key in state))?state[key]:dflt;}
function tierOffset(structured,ramp,r,cells,K){
  if(!structured) return 0;
  r=(r===undefined?1:r);
  return -(1-cells)*K.w_realtissue_M + r*_auth("auth_premium_extra",C.AUTH_PREMIUM_EXTRA)*ramp;}
function penetration(s){
  const K=KP||effConsts(s);                                         // current calibrated constants
  const market=MODEL.markets[s.region], b=biomass(s), bases=speciesBases(market);
  const r=(s.premium_resistance===undefined?1:s.premium_resistance);
  let Wval=0, Wvol=0; market.forEach(mt=>{Wval+=mt.p_conv*mt.w_vol; Wvol+=mt.w_vol;});   // Wvol: listed weights sum to 1.00-1.025
  const rows=market.map(mt=>{
    const {R,t,ramp}=typeR(mt,b,s.markup_add,s,bases);
    const o={ax:s.accept_x,tfM:s.theta_free_M,toff:tierOffset(mt.structured,ramp,r,s.cut_cells,K),eps:s.eps_own,income:s.income,pricePb:s.R_p,aP:s.a_p,nbx:s.neophobia_x,nbp:s.neophobia_p,pRef:mt.p_conv};
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
      : shareCalc(o.R,K,{ax:o.ax,tfM:o.tfM,toff:0,income:o.income,nbx:nbk,hx:o.hx,eqs:o.eqs});
    share.push(F*ceil); ceiling.push(ceil); nb.push(nbk);
    if(k<yrs){ const dF=(o.p+o.q*F)*(1.0-F); F=Math.min(1.0,F+dF); E+=F; }
  }
  return {share,ceiling,nb};
}
// first year the realized share reaches `frac` of its LONG-RUN share (rollout complete, novelty at
// its long-run value nbL), continuing past the plotted horizon (mirror of adoption_timing.years_to_stabilize;
// cap 200). Independent of where the chart stops.
function yearsToStabilize(o,frac){frac=frac||0.9; const K=KP, which=o.which||"x", MAX=200;
  const ceilAt=nbk=>(which==="pb")
      ? shareCalc(o.R,K,{toff:0,income:o.income,nbp:nbk,pricePb:o.R,aP:o.aP,hp:o.hp,present:false,which:"pb"})
      : shareCalc(o.R,K,{ax:o.ax,tfM:o.tfM,toff:0,income:o.income,nbx:nbk,hx:o.hx,eqs:o.eqs});
  const L=ceilAt(o.nbL); if(L<=1e-9) return MAX;
  let F=0.0, E=0.0;
  for(let k=0;k<=MAX;k++){
    const nbk=o.nbL+(o.nb0-o.nbL)*Math.exp(-o.rate*E);
    if(F*ceilAt(nbk)>=frac*L) return k;
    const dF=(o.p+o.q*F)*(1.0-F); F=Math.min(1.0,F+dF); E+=F;
  }
  return MAX;}
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
      : (dr=>({R:s._Rtiming, ax:dr.accept_x, tfM:s.theta_free_M, nbL:s.neophobia_x, nb0:dr.neophobia_x0,
               rate:dr.accept_rate, p:dr.p_innov, q:dr.q_imit, hx:s.health_x, income:s.income, eqs:dr.equal_price_share,
               which:"x"}))(mcDraw(C.mc_timing_inputs));   // C.mc_timing_inputs = inputs.MC_TIMING_INPUTS
    const tr=bassTrajectory(o); const sh=tr.share.map(x=>x*100);
    all.push(sh); tstab.push(yearsToStabilize(o)); finals.push(sh[sh.length-1]);
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
function el(t,a,p){const e=document.createElementNS(SV,t);for(const k in a)e.setAttribute(k,(k==="font-size"&&+a[k]<9)?9:a[k]);
  if(p)p.appendChild(e);return e;}
function tx(p,x,y,s,a){const t=el("text",Object.assign({x,y},a||{}),p);t.textContent=s;return t;}
// word-wrap a string into multiple <text> lines within maxW px; returns the y AFTER the last line.
// fontPx ~ font-size; lineH ~ line spacing. SVG <text> never auto-wraps, so we greedily pack words
// using a ~0.52*fontPx average glyph width (good enough for these short justifications).
function txWrap(p,x,y,s,maxW,a,lineH){const fpx=Math.max(9,(a&&a["font-size"])?parseFloat(a["font-size"]):10);
  lineH=Math.max(lineH||0,fpx+3); const cw=fpx*0.52, max=Math.max(1,Math.floor(maxW/cw));
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

function drawCost(s){
  const svg=document.getElementById("cost");clear(svg);
  // the scenarios' costs and the parity line are labelled in a column right of the plot, spaced so that no two overlap
  const par=parityCost(s);
  const marks=PG.cases.map(c=>({c:scEval(SC.presets[c.key].choice).total,lab:c.label,col:"#117733"}));
  marks.forEach(m=>{ m.lab+=", $"+m.c.toFixed(1); });
  marks.push({c:par,lab:"same shop price as meat, $"+par.toFixed(1),col:"#CC3311",par:true});
  const W=720,H=300,mL=42,mT=14,mB=40, x0=0.10,x1=1.0;
  const mR=Math.min(360,22+4.6*Math.max.apply(null,marks.map(m=>m.lab.length))), PR=W-mR;   // room for the longest name
  const own=(SCS.src==="custom")?SCS.customCost:scEval(SCS.choice).total;                    // the case set by the switches, at its most likely values
  const y1=Math.max(50,10*Math.ceil((Math.max.apply(null,marks.map(m=>m.c).concat([own]))+3)/10));
  const X=v=>mL+(PR-mL)*(v-x0)/(x1-x0), Y=v=>H-mB-(H-mT-mB)*v/y1;
  el("line",{x1:mL,y1:H-mB,x2:PR,y2:H-mB,stroke:"#ccc"},svg);
  el("line",{x1:mL,y1:mT,x2:mL,y2:H-mB,stroke:"#ccc"},svg);
  for(let v=0;v<=y1;v+=10){tx(svg,mL-5,Y(v)+3,v,{"font-size":9,"text-anchor":"end",fill:"#666"});
    el("line",{x1:mL,y1:Y(v),x2:PR,y2:Y(v),stroke:"#f0f0f0"},svg);}
  [0.2,0.4,0.6,0.8,1.0].forEach(v=>tx(svg,X(v),H-mB+13,v.toFixed(2).replace(/0$/,""),
    {"font-size":9,"text-anchor":"middle",fill:"#666"}));
  // one line per plant case, drawn up to the top of the plot and labelled where it ends
  const cols=["#117733","#0072B2","#CC3311"]; let lastLab=-99;
  C.configs.forEach(([lab,oh],k)=>{
    let d="", ex=x0, ey=0, on=false;
    for(let i=0;i<=80;i++){const mp=x0+(x1-x0)*i/80, b=mediaCost(mp,s.efficiency)+oh;
      if(b>y1){ on=false; continue; }
      d+=(on?"L":"M")+X(mp).toFixed(1)+" "+Y(b).toFixed(1)+" "; on=true; ex=mp; ey=b;}
    if(d==="") return;
    el("path",{d,fill:"none",stroke:cols[k],"stroke-width":2},svg);
    let ly=(k===0)?Y(ey)+12:Math.max(mT+8,Y(ey)-4); if(Math.abs(ly-lastLab)<10) ly=lastLab+10; lastLab=ly;   // the lowest line's name goes under it
    tx(svg,X(ex)-4,ly,lab,{"font-size":8,"text-anchor":"end",fill:cols[k],stroke:"#fff","stroke-width":2.5,"paint-order":"stroke"});});
  marks.forEach(m=>{ m.y=Y(m.c);
    el("line",{x1:mL,y1:m.y,x2:PR,y2:m.y,stroke:m.col,"stroke-dasharray":m.par?"1 3":"4 3",opacity:m.par?1:0.7},svg); });
  const gap=12, ord=marks.slice().sort((a,b)=>a.y-b.y);
  ord.forEach((m,i)=>{ m.ly=Math.max(m.y+3,i?ord[i-1].ly+gap:mT+6); });
  for(let i=ord.length-1;i>=0;i--){ const cap=(i===ord.length-1)?H-mB:ord[i+1].ly-gap; if(ord[i].ly>cap) ord[i].ly=cap; }
  ord.forEach(m=>{
    el("path",{d:"M"+PR+" "+m.y.toFixed(1)+" L"+(PR+8)+" "+(m.ly-3).toFixed(1)+" L"+(PR+11)+" "+(m.ly-3).toFixed(1),fill:"none",stroke:m.col,"stroke-width":0.7,opacity:0.8},svg);
    tx(svg,PR+13,m.ly,m.lab,{"font-size":8,fill:m.col}); });
  // marker
  const b=own, mpDot=scParams(SCS.choice).medium_price;
  if(SCS.src==="scenario"&&mpDot!==undefined&&b<=y1){
    const cx=X(Math.min(x1,Math.max(x0,mpDot)));
    el("circle",{cx:cx,cy:Y(b),r:5,fill:"#000"},svg);
    tx(svg,cx,Y(b)-8,"$"+b.toFixed(1),{"font-size":9,"text-anchor":"middle","font-weight":700,stroke:"#fff","stroke-width":3,"paint-order":"stroke"}); }
  tx(svg,(mL+PR)/2,H-3,"Price of a litre of medium, $",{"font-size":9,"text-anchor":"middle",fill:"#444"});
  tx(svg,mL+4,mT+6,"cost of a kilo of cells, $",{"font-size":9,fill:"#444"});
}
function drawCurve(s){
  const svg=document.getElementById("curve");clear(svg);
  const W=420,H=300,mL=40,mR=14,mT=22,mB=40, x0=0.5,y1=90;
  // the chosen product: whether it is a cut, and how premium, sets its offset (tierOffset)
  const market=MODEL.markets[s.region];
  const mt=market.find(m=>m.name===state.curveType)||market[0];
  const rpr=(s.premium_resistance===undefined?1:s.premium_resistance);
  const {R:Rmark,t,ramp}=typeR(mt,biomass(s),s.markup_add,s,speciesBases(market));   // t: a label for the title only
  const eps=s.eps_own, toff=tierOffset(mt.structured,ramp,rpr,s.cut_cells,KP);
  const Rp=s.R_p;                                                   // plant-based's OWN price ratio (its marker x)
  // x-axis extends to cover BOTH markers (cultivated's Rmark and plant-based's R_p) so the dots land ON the curves
  const x1=Math.max(3, Math.ceil((Math.max(Rmark,Rp)+0.4)*2)/2);
  const X=v=>mL+(W-mL-mR)*(v-x0)/(x1-x0), Y=v=>H-mB-(H-mT-mB)*v/y1;
  const evW=(R,which)=>shareCalc(R,KP,{ax:s.accept_x,tfM:s.theta_free_M,toff,eps,
                              income:s.income,pricePb:s.R_p,aP:s.a_p,nbx:s.neophobia_x,nbp:s.neophobia_p,pRef:mt.p_conv,which});
  el("line",{x1:mL,y1:H-mB,x2:W-mR,y2:H-mB,stroke:"#ccc"},svg);
  [0,20,40,60,80].forEach(v=>{tx(svg,mL-5,Y(v)+3,v,{"font-size":9,"text-anchor":"end",fill:"#666"});
    el("line",{x1:mL,y1:Y(v),x2:W-mR,y2:Y(v),stroke:"#f0f0f0"},svg);});
  // x ticks: evenly spaced across the (possibly extended) range
  {const step=x1<=3?0.5:1; for(let v=Math.ceil(x0/step)*step; v<=x1+1e-9; v+=step)
    tx(svg,X(v),H-mB+13,(v%1?v.toFixed(1):v.toFixed(0)),{"font-size":9,"text-anchor":"middle",fill:"#666"});}
  // parity line
  el("line",{x1:X(1),y1:mT,x2:X(1),y2:H-mB,stroke:"#999","stroke-dasharray":"4 3"},svg);
  tx(svg,X(1)+3,mT+9,"equal price",{"font-size":8,fill:"#999"});
  tx(svg,mL+34,mT-8,mt.name,{"font-size":9,fill:"#333","font-weight":700});
  // all four product shares vs cultivated's price ratio R_x (cultivated is the bold line)
  const LINES=[["c","conventional","#E69F00",1.3],["p","plant-based","#117733",1.3],
               ["w","whole-food","#949494",1.3],["x","cultivated","#0072B2",2.4]];
  LINES.forEach(([which,lab,col,w])=>{
    let d="";for(let i=0;i<=80;i++){const R=x0+(x1-x0)*i/80;
      d+=(i?"L":"M")+X(R).toFixed(1)+" "+Y(evW(R,which)*100).toFixed(1)+" ";}
    el("path",{d,fill:"none",stroke:col,"stroke-width":w,opacity:which==="x"?1:0.85},svg);});
  // legend doubles as a LIVE READOUT: each product's share at the marked R (so the
  // plant-based & whole-food shares are shown as numbers, not just lines)
  const lg=LINES.slice().reverse(), lbw=206;
  el("rect",{x:W-mR-lbw,y:mT-2,width:lbw-2,height:lg.length*12+16,fill:"#fff",opacity:0.86},svg);
  tx(svg,W-mR-lbw+4,mT+8,"shares at "+Rmark.toFixed(2)+" times the price:",{"font-size":8,fill:"#888"});
  let lgy=mT+20; lg.forEach(([which,lab,col])=>{
    el("line",{x1:W-mR-lbw+4,y1:lgy-3,x2:W-mR-lbw+18,y2:lgy-3,stroke:col,"stroke-width":which==="x"?2.4:1.3},svg);
    tx(svg,W-mR-lbw+22,lgy,lab+(which==="p"?" (at its own "+Rp.toFixed(2)+")":""),{"font-size":8.5,fill:"#444"});
    tx(svg,W-mR-5,lgy,pgPctS((which==="p"?evW(Rp,"p"):evW(Rmark,which))*100),{"font-size":8.5,fill:col,"text-anchor":"end","font-weight":600});
    lgy+=12;});
  // CULTIVATED marker: its share at its own R_x, on the blue curve (axis covers R_x so the dot
  // lands on the curve). Anchor the label so it never overflows the edges.
  const sh=evW(Rmark,"x");
  const mx=X(Math.max(x0,Math.min(Rmark,x1))), my=Y(sh*100);
  el("circle",{cx:mx,cy:my,r:5,fill:"#0072B2"},svg);
  // PLANT-BASED marker: its ACTUAL operating point — its share at its OWN price R_p, on the green
  // curve (the true analogue of the cultivated dot; cultivated's R_x doesn't set PB's price).
  const shp=evW(Rp,"p");
  const px=X(Math.max(x0,Math.min(Rp,x1))), py=Y(shp*100);
  el("circle",{cx:px,cy:py,r:4,fill:"#117733"},svg);
  tx(svg,(mL+W-mR)/2,H-3,"Cultivated meat's price, as a multiple of the conventional price",{"font-size":9,"text-anchor":"middle",fill:"#444"});
  tx(svg,mL-30,mT-8,"share, %",{"font-size":9,fill:"#444"});
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
   (its LOCAL conventional price), the offset τ of a cut or a premium product, and the per-
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
  const {R,t,ramp}=typeR(mt,b,s.markup_add,s,bases);            // this type's price ratio, tier label (for the tag) and premium ramp
  const toff=tierOffset(mt.structured,ramp,rpr,s.cut_cells,KP);
  const o={ax:s.accept_x,tfM:s.theta_free_M,toff,
           eps:s.eps_own,income:s.income,nbx:s.neophobia_x,nbp:s.neophobia_p,
           hx:s.health_x,hp:s.health_p,pricePb:s.R_p,tasteP:(s.a_p-1),
           rtx:s.real_tissue_x,rtp:s.real_tissue_p,pRef:mt.p_conv,which:"x"};
  const bd=breakdownCalc(R,KP,"M",o);
  const blended=shareCalc(R,KP,{ax:s.accept_x,tfM:s.theta_free_M,toff,
           eps:s.eps_own,income:s.income,nbx:s.neophobia_x,nbp:s.neophobia_p,
           hx:s.health_x,hp:s.health_p,pricePb:s.R_p,aP:s.a_p,rtx:s.real_tissue_x,rtp:s.real_tissue_p,
           pRef:mt.p_conv,which:"x"});
  const FACT=[["price","price"],["taste","taste"],["real_meat","real meat"],
              ["health","health"],["slaughter_free","no slaughter"],
              ["novelty","novelty"],["authenticity","cut, premium"]];
  let maxA=1e-6; FACT.forEach(([k])=>maxA=Math.max(maxA,Math.abs(bd[k])));
  maxA=Math.max(maxA,Math.abs(bd._net));
  const sc=(Math.min(xz-xL,xR-xz)-30)/maxA;                     // utils -> px (leave room for value labels)
  // species/tier/R tag + the worse/better axis hint
  tx(svg,4,padTop-18,pgRegionName()+", "+mt.name+", at "+R.toFixed(2)+" times the price",{"font-size":9,fill:"#999","text-anchor":"start"});
  tx(svg,xz,padTop-5,"← hurts  |  helps →",{"font-size":9,fill:"#bbb","text-anchor":"middle"});
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
  tx(svg,xL-6,yN+3,"net",{"font-size":9.5,fill:"#111","text-anchor":"end","font-weight":700});
  svg.setAttribute("viewBox","0 0 420 "+(yN+34));
  tx(svg,xz,yN+22,"Share of all shoppers, with the spread of liking: "+pgPctS(blended*100),{"font-size":9.5,fill:"#111","text-anchor":"middle"});
  tx(svg,xz,yN+3,(net>=0?"+":"")+net.toFixed(2)+" points for the average mainstream shopper",
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
  if(_isMeat){ title="The model is tuned to “"+sel+"”, so this is not a test"; tcol="#888"; }
  else if(_isEgg){ title=(ok?"✓ ":"")+"“"+sel+"”: this tests a different lever (welfare, not authenticity)"; tcol=ok?"#0173B2":"#666"; }
  else { title=(ok?"✓ Out of sample: the model reproduces “":"The model gives “")+sel+"”"+(ok?" (not tuned to it)":""); tcol=ok?"#0173B2":"#666"; }
  tx(svg,W/2,mT-12,title,{"font-size":10,"text-anchor":"middle",fill:tcol,"font-weight":700});  // center over FULL width (not the left bar-panel) so the long title doesn't clip off the left edge
  // RIGHT HALF: positions swapped in (same β, income, q) + the note
  const pX=W*0.52, pVal=W-18;
  let ry=mT+10;
  tx(svg,pX,ry,"The product's facts. Only these change:",{"font-size":9,fill:"#888"}); ry+=20;
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
    if(why){ry=txWrap(svg,pX+10,ry,String(why).replace(/\s*—\s*/g,": ").replace(/→/g,"so"),whyW,{"font-size":8,fill:"#999"},10); ry+=1;}
    el("line",{x1:pX+4,y1:ry-3,x2:pVal,y2:ry-3,stroke:"#f0f0f0"},svg); ry+=7;});
  ry+=4; ry=txWrap(svg,pX,ry,String(pd.note).replace(/\s*—\s*/g,": ").replace(/→/g,"so"),pVal-pX,{"font-size":8.5,fill:"#999"},11);
  ry+=12; tx(svg,pX,ry,"The same shopper model with a different product is a test outside meat.",
     {"font-size":8.5,fill:"#0173B2","font-style":"italic"});
  // grow the viewBox to fit the (now variable-height, wrapped) right-hand column
  svg.setAttribute("viewBox","0 0 "+W+" "+Math.max(H, ry+14));
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
    o.textContent=l3Name(mt.name);sel.appendChild(o);});
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
   Cultivated retail cost = a waterline set by the live cost sliders (medium/overhead/markup/cut cell share and assembly),
   via the SAME stack as the cost chart. Products are islands at their conventional price; above the
   line = price-reachable (R<1). Two reference lines: the current sea and the best-case sea. */
function footRetail(s,structured){const b=biomass(s);return shelfPrice(structured?cutCost(b,s):b,s);}
function footFloor(s,structured){return shelfPrice(structured?cutCost(SC.best_cost,s):SC.best_cost,s);}   // the best case's cost
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
  P.forEach((p,i)=>{const o=document.createElement("option");o.value=i;o.textContent=p.label;sel.appendChild(o);});
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
  // underwater shading (below the unstructured cost) + the BAND between the unstructured and the cut cost, so STRUCTURED
  // products' stems land on a visible line. Since 2026-11-19 a cut can cost LESS than mince (a fifth of it is plant protein),
  // so the band runs whichever way the two lie.
  el("rect",{x:mL,y:Y(seaU),width:W-mL-mR,height:(H-mB)-Y(seaU),fill:"#0072B2",opacity:0.05},svg);
  el("rect",{x:mL,y:Math.min(Y(seaS),Y(seaU)),width:W-mL-mR,height:Math.abs(Y(seaU)-Y(seaS)),fill:"#0072B2",opacity:0.12},svg);
  el("line",{x1:mL,y1:Y(seaU),x2:W-mR,y2:Y(seaU),stroke:"#0072B2","stroke-width":1.8},svg);
  el("line",{x1:mL,y1:Y(seaS),x2:W-mR,y2:Y(seaS),stroke:"#0072B2","stroke-width":1.1,"stroke-dasharray":"5 2"},svg);
  const cutAbove=seaS>=seaU;
  tx(svg,W-mR+4,Y(seaS)+(cutAbove?-3:11),"a cultivated cut $"+seaS.toFixed(0),{"font-size":8,fill:"#0072B2"});
  tx(svg,W-mR+4,Y(seaU)+(cutAbove?9:-1),"cultivated mince $"+seaU.toFixed(0),{"font-size":8,fill:"#0072B2","font-weight":700});
  el("line",{x1:mL,y1:Y(floorU),x2:W-mR,y2:Y(floorU),stroke:"#0072B2","stroke-width":1,"stroke-dasharray":"2 3",opacity:0.6},svg);
  tx(svg,W-mR+4,Y(floorU)+3,"best case $"+floorU.toFixed(0),{"font-size":8,fill:"#0072B2",opacity:0.8});
  P.forEach((p,i)=>{
    const structured=p.structure==="structured";
    const cost=structured?seaS:seaU, fl=structured?floorS:floorU;
    const rc=footReach(s,p), reach=rc.zone, col=rc.col;
    const r=footRad(footDisplace(s,p)), x=X(i), y=Y(p.p_base);
    // prestige core (rent cultivated can't capture): faint marker at the headline price, dotted down to the base
    if(p.p_conv>p.p_base*1.05){const yp=Y(p.p_conv), rent=p.p_conv-p.p_base;
      el("line",{x1:x,y1:yp,x2:x,y2:y,stroke:"#CCC","stroke-width":1,"stroke-dasharray":"1 3"},svg);
      tip(el("circle",{cx:x,cy:yp,r:3,fill:"#CCC"},svg),
        p.label+"\nThe headline price is $"+p.p_conv+" a kilo, the luxury grade."
        +"\nCultivated meat competes $"+rent+" a kilo lower, at $"+p.p_base+" (the everyday grade)."
        +"\nThe gap is paid for the brand and the scarcity. Cultivated meat cannot capture it, because it is not the original.");
      if(p.label===selLabel) tx(svg,x+5,(yp+y)/2+3,"rent $"+rent,{"font-size":8,fill:"#999","font-style":"italic"});}
    // the vertical bar is the cost→accessible-price gap (reachability headroom): solid up when reachable, dotted-grey deficit
    if(reach!=="never") el("line",{x1:x,y1:Y(cost),x2:x,y2:y,stroke:col,"stroke-width":2.2,opacity:0.6},svg);
    else el("line",{x1:x,y1:Y(cost),x2:x,y2:y,stroke:"#CCC","stroke-width":1,"stroke-dasharray":"2 2"},svg);
    tip(el("circle",{cx:x,cy:y,r,fill:col,opacity:0.9,stroke:"#fff","stroke-width":1},svg),footTip(s,p));
    if(p.launched_by) el("circle",{cx:x,cy:y,r:r+3,fill:"none",stroke:"#333","stroke-width":1,opacity:0.7},svg);
    if(p.label===selLabel){el("circle",{cx:x,cy:y,r:r+6,fill:"none",stroke:"#CC3311","stroke-width":1.6},svg);
      tx(svg,x+5,(Y(cost)+y)/2+3,footR(s,p).toFixed(2)+" times",{"font-size":9,fill:"#CC3311","font-weight":700});}
    const short=p.label.replace("cultivated ","").replace(/ \(.*\)/,"");
    tx(svg,x,H-mB+12,short,{"font-size":7.5,"text-anchor":"end",fill:"#444",transform:"rotate(-42 "+x+" "+(H-mB+12)+")"});
  });
  el("line",{x1:mL,y1:H-mB,x2:W-mR,y2:H-mB,stroke:"#ccc"},svg);
  tx(svg,(mL+W-mR)/2,H-3,"Dot: the product at its everyday price, $ a kilo (log scale). Bar: the gap to cultivated meat's cost. Grey tick: its luxury price.",
    {"font-size":8,"text-anchor":"middle",fill:"#666"});
  [["#117733","cheaper now"],["#56B4E9","about equal (within $3)"],["#E69F00","only in the Best case"],["#BBBBBB","not even then"]].forEach(([c,t],k)=>{
    el("circle",{cx:W-mR+8,cy:mT+8+k*14,r:4,fill:c},svg);tx(svg,W-mR+16,mT+11+k*14,t,{"font-size":8,fill:"#555"});});
  const _ky=mT+8+4*14;   // the grey tick above each island = the headline (rent) price cultivated can't capture
  el("circle",{cx:W-mR+8,cy:_ky-3,r:2.5,fill:"#CCC"},svg);
  el("line",{x1:W-mR+8,y1:_ky,x2:W-mR+8,y2:_ky+8,stroke:"#CCC","stroke-dasharray":"1 2"},svg);
  tx(svg,W-mR+16,_ky+1,"luxury price (out",{"font-size":8,fill:"#555"});
  tx(svg,W-mR+16,_ky+11,"of reach)",{"font-size":8,fill:"#555"});
  footSizeKey(svg,W-mR+16,W-mR+38,mT+8+5*14+16);           // quantified volume legend
}
/* per-product PREDICTED SHARE via the demand model (shareCalc), live to the acceptance/price sliders.
   NO new foothold parameter: it is the IDENTICAL Step-2 logit panel 1 uses, with the SAME per-product
   offset (tierOffset). The accessible tier cultivated competes at is BASIC (unstructured/processed, no offset)
   or CUT (structured: the blend penalty of a cut that is part plant protein);
   the PREMIUM tier is the prestige core, already removed as volume via φ — so the premium penalty is counted
   ONCE (premium grade → volume; accessible grade → the offset of mince or of a cut), never double. This
   makes a commodity foothold product reproduce panel 1's basic-tier share exactly. See appendix A6. */
function footShare(s,pd){   // share of the ADDRESSABLE base = Step 2's calibrated logit at the accessible price.
  if(pd.p_base==null) return 0;
  const K=KP||effConsts(s), r=(s.premium_resistance===undefined?1:s.premium_resistance);
  // a structured product carries the blend penalty of any cut; the premium penalty is not applied here (ramp 0): the
  // prestige core is already removed as volume via φ
  return shareCalc(footR(s,pd),K,{ax:s.accept_x,tfM:s.theta_free_M,toff:tierOffset(pd.structure==="structured",0,r,s.cut_cells,K),
    eps:s.eps_own,income:s.income,pricePb:s.R_p,aP:s.a_p,nbx:s.neophobia_x,nbp:s.neophobia_p,pRef:pd.p_base});
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
  const rent=footPhi(p)>0?Math.round(100*footPhi(p))+"% of the market is prestige rent that cultivated meat cannot capture.":
             "There is no prestige rent, so cultivated meat competes at the full price.";
  return adv.charAt(0).toUpperCase()+adv.slice(1)+". "+rent;
}
function footTip(s,p){                  // hover card — short sentences + blank-line grouping (white-space:pre-line) for scannability
  const structured=p.structure==="structured", R=footR(s,p), cost=footRetail(s,structured);
  const disp=footDisplace(s,p), sh=(100*footShare(s,p)).toFixed(0);
  const dispTxt=disp>=1000?(disp/1000).toFixed(1)+" Mt/yr":disp.toFixed(0)+" kt/yr";
  const addrTxt=footAddr(p).toLocaleString(undefined,{maximumFractionDigits:0})+" kt/yr";
  const compete=(p.p_conv>p.p_base*1.05)
    ? "Cultivated meat competes at the $"+p.p_base+"/kg accessible grade. The $"+p.p_conv+" headline price includes prestige rent that it cannot capture."
    : "Cultivated meat competes at the $"+p.p_base+"/kg grade. This product has a single grade and no prestige rent.";
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
  tx(svg,cx-12,yTop,"bubble: tonnes displaced a year",{"font-size":7.5,fill:"#999"});
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
    tx(svg,X(v),H-mB+13,v===1?"1 (equal price)":String(v),{"font-size":8,"text-anchor":"middle",fill:v===1?"#666":"#aaa"});});
  P.forEach(p=>{
    if(p.p_base==null) return;
    const R=footR(s,p), sh=100*footShare(s,p), rc=footReach(s,p);
    const r=footRad(footDisplace(s,p)), x=X(R), y=Y(sh);
    tip(el("circle",{cx:x,cy:y,r,fill:rc.col,opacity:0.8,stroke:rc.col,"stroke-width":1.2},svg),footTip(s,p));
    if(p.launched_by) el("circle",{cx:x,cy:y,r:r+3,fill:"none",stroke:"#333","stroke-width":1,opacity:0.7},svg);
    if(p.label===selLabel){el("circle",{cx:x,cy:y,r:r+6,fill:"none",stroke:"#CC3311","stroke-width":1.8},svg);
      tx(svg,x,y-r-6,selLabel.replace("cultivated ",""),{"font-size":8.5,"text-anchor":"middle",fill:"#CC3311","font-weight":700});}
  });
  tx(svg,(mL+W-mR)/2,H-3,"Cultivated meat's price as a multiple of the product's everyday grade (log scale). Hover over a bubble for its name.",
    {"font-size":8.5,"text-anchor":"middle",fill:"#666"});
  tx(svg,15,(mT+H-mB)/2,"share of the reachable market, %",{"font-size":8.5,"text-anchor":"middle",fill:"#666",transform:"rotate(-90 15 "+((mT+H-mB)/2)+")"});
  footSizeKey(svg,W-mR+18,W-mR+40,mT+22);   // quantified volume legend (top-right)
}
function footCaption(s){
  const pd=C.foothold_products[state.footSel]; if(!pd) return;
  const structured=pd.structure==="structured", R=footR(s,pd);
  const zone=R<1?"already cheaper":(pd.p_base>=footFloor(s,structured)?"cheaper only in the best case":"not even in the best case");
  const disp=footDisplace(s,pd), dispTxt=disp>=1000?(disp/1000).toFixed(1)+" Mt/yr":disp.toFixed(0)+" kt/yr";
  // one line of key numbers; the price basis and notes live in the bubble's hover card (footTip)
  document.getElementById("footcap").innerHTML=
    "<b>"+pd.label.replace("cultivated ","")+"</b>: cultivated meat costs "+R.toFixed(2)+" times its everyday grade ("+zone+"). It takes about "+pgPctS(100*footShare(s,pd))+
    " of the reachable market and displaces about "+dispTxt.replace("/yr"," a year")+(pd.launched_by?". Led by "+pd.launched_by:"")+
    ". Hover over a bubble for the price basis. The share stays below 100% even when cultivated meat is far cheaper: once the price is low next to income, taste and the other attributes decide the rest.";
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
// a standard normal draw (Box-Muller on the page's own seeded _rand)
function randNormal(){let u=_rand(); if(u<1e-12)u=1e-12; return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*_rand());}
// a lognormal draw: median `median`, lo and hi its 5th and 95th percentiles (sigma = ln(hi/lo)/(2 x 1.645)), clipped to
// [clipLo, clipHi] when given (mirror of inputs.sample)
function lognorm(lo,median,hi,clipLo,clipHi){
  let x=median*Math.exp(Math.log(hi/lo)/(2*C.lognormal_z90)*randNormal());
  if(clipLo!=null) x=Math.max(clipLo,x); if(clipHi!=null) x=Math.min(clipHi,x);
  return x;}
function pctl(sorted,q){const i=(sorted.length-1)*q/100,lo=Math.floor(i),hi=Math.ceil(i);
  return sorted[lo]+(sorted[hi]-sorted[lo])*(i-lo);}
// One draw of the input `k` from its prior C.priors[k] = [lo, mode, hi]: triangular, unless C.prior_kinds[k] says
// lognormal (then the mode is the median). Mirror of inputs.draw.
function priorDraw(k){const P=C.priors[k], kd=C.prior_kinds[k];
  return (kd&&kd[0]==="lognormal")?lognorm(P[0],P[1],P[2],kd[1],kd[2]):triang(P[0],P[1],P[2]);}
// One Monte-Carlo draw: a sample of every input in `keys`. The lists (C.mc_inputs,
// C.mc_timing_inputs) are injected from inputs.MC_* — the SAME sets the Python bands sample — so the
// page's bands and the numbers quoted in RESULTS.md cannot sweep different uncertainties.
function mcDraw(keys){const d={};for(const k of keys)d[k]=priorDraw(k);return d;}
// The settings with one draw's cut: its cell share (1 - the drawn plant-protein share) and assembly cost. cutCost and
// tierOffset both read the cell share from here, so a draw's cut is one product in cost and in liking.
function mcCutSettings(s,dr){return Object.assign({},s,{cut_cells:1-dr.scaffold_frac,scaffold:dr.process_cost});}
// cultivated's shareCalc options for one draw of C.mc_inputs, for meat type mt (premium ramp `ramp`); `s` carries the
// draw's cut (mcCutSettings). Same options as penetration()'s point estimate, including pRef = this cut's own price (the
// income log needs the dollar price of the rival it faces; before this helper the bands priced every cut at the $12 anchor).
function mcShareOpts(dr,mt,ramp,s){return {ax:dr.accept_x,tfM:s.theta_free_M,
  toff:tierOffset(mt.structured,ramp,dr.premium_resistance,s.cut_cells,KP),
  eps:dr.eps_own, kap:dr.cult_sub_mult,   // a kappa draw scales cultivated's price gap
  income:s.income,pricePb:s.R_p,aP:s.a_p,
  nbx:s.neophobia_x,nbp:s.neophobia_p,hx:s.health_x,pRef:mt.p_conv,eqs:dr.equal_price_share};}   // novelty, no-slaughter, health: the slider values (not drawn)
function monteCarlo(s,N){
  // bands TOTAL penetration for BOTH novel meats on equal footing: cultivated (samples C.mc_inputs:
  // cost, acceptance, elasticity, the share at equal price, premium resistance, a cut's make-up) and plant-based (also
  // its own a_p, ν_p, health_p; PB has no cost stack, its price is the R_p slider). Returns vol/val
  // for cultivated and pvol/pval for plant-based.
  const P=C.priors, market=MODEL.markets[s.region], bases=speciesBases(market);
  let Wval=0, Wvol=0; market.forEach(mt=>{Wval+=mt.p_conv*mt.w_vol; Wvol+=mt.w_vol;});
  _seedRng(3);                      // reproducible penetration band (mirrors np seed=0)
  const vol=new Array(N), val=new Array(N), pvol=new Array(N), pval=new Array(N);
  for(let d=0;d<N;d++){
    const dr=mcDraw(C.mc_inputs), sd=mcCutSettings(s,dr);
    // plant-based draws (its own priors, equal footing)
    const aps=triang.apply(null,P.a_p), nbps=triang.apply(null,P.neophobia_p), hps=triang.apply(null,P.health_p);
    const b=(s.cost_override!=null)?s.cost_override:mediaCost(dr.media_price,dr.efficiency)+dr.overhead+(s.cleanroom?C.cleanroom_cost:0);
    let tv=0,tval=0,tpv=0,tpval=0;
    for(const mt of market){
      const {R,ramp}=typeR(mt,b,dr.markup_add,sd,bases,dr.retail_margin);
      const o=mcShareOpts(dr,mt,ramp,sd);
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
    const dr=mcDraw(C.mc_inputs), sd=mcCutSettings(s,dr),
      aps=triang.apply(null,P.a_p), nbps=triang.apply(null,P.neophobia_p), hps=triang.apply(null,P.health_p);
    const b=(s.cost_override!=null)?s.cost_override:mediaCost(dr.media_price,dr.efficiency)+dr.overhead+(s.cleanroom?C.cleanroom_cost:0);
    for(const mt of market){
      const {R,ramp}=typeR(mt,b,dr.markup_add,sd,bases,dr.retail_margin);
      const o=mcShareOpts(dr,mt,ramp,sd);
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
  const mc=monteCarlo(s,2000);
  const svg=document.getElementById("mc");clear(svg);
  const W=720,H=270,mL=24,mR=14,mT=58,mB=34;
  svg.setAttribute("viewBox","0 0 "+W+" "+H);
  // x-axis covers BOTH products' volume distributions + cultivated value (so PB's band fits too)
  const all=mc.vol.concat(mc.val).concat(mc.pvol).sort((a,b)=>a-b), xmax=Math.max(6,pctl(all,99));
  const nb=48, bw=xmax/nb;
  const hist=a=>{const h=new Array(nb).fill(0);a.forEach(v=>{const k=Math.floor(v/bw);if(k>=0&&k<nb)h[k]++;});return h;};
  const hv=hist(mc.vol), hl=hist(mc.val), hpv=hist(mc.pvol), hmax=Math.max(...hv,...hl,...hpv,1);
  const X=v=>mL+(W-mL-mR)*Math.min(v,xmax)/xmax, Y=h=>H-mB-(H-mT-mB)*h/hmax;
  el("line",{x1:mL,y1:H-mB,x2:W-mR,y2:H-mB,stroke:"#ccc"},svg);
  for(let v=0;v<=xmax+1e-6;v+=(xmax>20?5:(xmax>8?2:1)))
    tx(svg,X(v),H-mB+13,v.toFixed(0),{"font-size":9,"text-anchor":"middle",fill:"#666"});
  let ty=12;
  // cultivated by volume + by value, then plant-based by volume (EQUAL FOOTING, green)
  [[hv,mc.vol,"#E69F00","cultivated, by weight"],
   [hl,mc.val,"#0072B2","cultivated, by value"],
   [hpv,mc.pvol,"#117733","plant-based, by weight"]].forEach(([h,raw,c,lab])=>{
    let d="M"+mL+" "+(H-mB);
    for(let k=0;k<nb;k++){const y=Y(h[k]);d+=" L"+X(k*bw).toFixed(1)+" "+y.toFixed(1)+" L"+X((k+1)*bw).toFixed(1)+" "+y.toFixed(1);}
    d+=" L"+X(xmax)+" "+(H-mB)+" Z";
    el("path",{d,fill:c,opacity:0.30,stroke:c,"stroke-width":1.2},svg);
    const srt=raw.slice().sort((a,b)=>a-b), p10=pctl(srt,10),p50=pctl(srt,50),p90=pctl(srt,90);
    [[p10,0],[p50,1],[p90,0]].forEach(([q,solid])=>el("line",{x1:X(q),y1:mT,x2:X(q),y2:H-mB,
      stroke:c,"stroke-dasharray":solid?"":"3 3","stroke-width":solid?1.5:0.8,opacity:0.85},svg));
    el("rect",{x:mL,y:ty-8,width:10,height:9,fill:c,opacity:0.6},svg);
    tx(svg,mL+15,ty,lab+": median "+pgPctS(p50)+", 8 in 10 draws between "+pgPct(p10)+"% and "+pgPct(p90)+"%",
      {"font-size":9.5});ty+=14;
  });
  tx(svg,(mL+W-mR)/2,H-2,"Long-run share of all meat and seafood, %. Solid line: the median. Dashed lines: the range for 8 in 10 draws.",
    {"font-size":9,"text-anchor":"middle",fill:"#444"});
  document.getElementById("mcsub").textContent=
    pgRegionName()+": the long-run share over 2,000 draws of the shopper settings (price sensitivity, the share at equal price, taste, the costs of "+
    "reaching the shelf, a cut's make-up, and plant-based meat's own taste and image). The cost of the cells is held at "+scMoney(biomass(s))+
    " a kilo, so this spread is narrower than the first screen's, where the cost is drawn too.";
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
  pgSetCost(); pgRenderFirst(); pgRenderLevels();
  pgWriteHash();
}
function pgWriteHash(){
  if(typeof history==='undefined' || !history.replaceState) return;
  let h=settingsHash();
  if(PGS.anchor) h=h?h+"&at="+PGS.anchor:PGS.anchor;
  history.replaceState(null,"",h?"#"+h:location.pathname+location.search);
}
function setIncome(v){                                // sync the income slider when the region changes
  state.income=v; const ri=document.getElementById("r_income"), vi=document.getElementById("v_income");
  const s=MODEL.sliders.find(x=>x.key==="income");
  if(ri)ri.value=(s&&s.logscale)?val2pos(s,v):v; if(vi&&s)vi.textContent=fmtVal(s,v);
}
function fillParamTable(){
  const SY=C.param_symbols||{};
  let h='<table class="pt"><tr><th>setting</th><th>symbol</th><th>model\'s value</th><th>range</th>'+
        '<th>where it enters the equations</th><th>source</th></tr>';
  let curG=null;
  const big=v=>"$"+Math.round(v).toLocaleString("en-US");
  MODEL.sliders.forEach(s=>{const sy=SY[s.key]||["",""];
    if(s.hidden) return;
    if(s.group&&s.group!==curG){curG=s.group;
      h+='<tr><th colspan="6">'+s.group+'</th></tr>';}
    if(s.key==="income"){ h+='<tr><td>'+s.label.replace(/\s*\([^)]*\)\s*$/,"")+'</td><td style="white-space:nowrap">'+sy[0]+'</td><td class="n">'+big(s.default)+
      '</td><td class="n">'+big(s.min)+' to '+big(s.max)+'</td><td class="s">'+sy[1]+'</td><td class="s">'+s.src+'</td></tr>'; return; }
    h+='<tr><td>'+s.label.replace(/\s*\([^)]*\)\s*$/,"")+'</td><td style="white-space:nowrap">'+sy[0]+
    '</td><td class="n">'+fmtVal(s,s.default)+'</td><td class="n">'+fmtVal(s,s.min)+' to '+fmtVal(s,s.max)+
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
  let h='<table class="pt"><tr><th>type of meat (kind of product)</th>';
  regs.forEach(([k,l])=>h+='<th style="text-align:right">'+l+'&nbsp;$/kg</th>');
  h+='</tr>';
  keys.forEach(key=>{const r=rowmap[key];h+='<tr><td>'+r.label+'</td>';
    regs.forEach(([k])=>{h+='<td class="n">'+(k in r.price?'$'+r.price[k].toFixed(0):'—')+'</td>';});
    h+='</tr>';});
  document.getElementById("pricetable").innerHTML=h+'</table>'+
    '<p class="note">One row for each species and kind of product. Region-specific '+
    'premium names (wagyu, prime, picanha, ibérico, sushi) are grouped under “premium”.</p>';
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
  if(s.fmt==="pct")return (v*100).toFixed(0)+"%";
  if(s.unit==="$/L")return "$"+v.toFixed(2);
  if(s.unit==="$/kg")return "$"+v.toFixed(s.step<1?1:0);
  if(s.unit==="$/yr")return "$"+Math.round(v).toLocaleString("en-US");
  if(s.key==="w_eth")return (v*100).toFixed(0)+"%";
  if(s.unit==="x")return v.toFixed(2)+"x";
  if(s.unit==="points of score")return v.toFixed(1);
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
  return s.key==="cult_sub_mult"?" (so "+epsx.toFixed(1)+" for cultivated meat)":"";
}
// The price ratio step by step, with the current settings in place (same formulas as biomass() and
// basicR(), which tests/run_parity.py checks against the Python model).
function drawCalc(s,b,retail,conv,R){
  const raw=C.media_intensity*s.efficiency*s.media_price, med=mediaCost(s.media_price,s.efficiency);
  const d2=x=>"$"+x.toFixed(2), d1=x=>"$"+x.toFixed(1);
  const medTxt=raw<C.FEEDSTOCK_FLOOR
    ? "medium at its floor "+d2(med)+" (the feedstock cannot cost less)"
    : C.media_intensity.toFixed(1)+" L/kg &times; efficiency "+s.efficiency.toFixed(2)+" &times; "+d2(s.media_price)+"/L = "+d2(med);
  const clean=s.cleanroom?" + clean room "+d1(C.cleanroom_cost):"";
  const tax=s.meat_tax!==1?" (benchmark $"+C.p_conv_anchor.toFixed(1)+" &times; price multiplier "+s.meat_tax.toFixed(2)+")":"";
  const f=pgFacts();
  const costStep='<li><b>Cost to grow a kilo of cells.</b> From the selected case ('+f.label+'): the cells, plant, tank, medium and losses together. '+
      '<span class="eq">'+d1(b)+' a kilo</span> '+(f.cb?'This is the median of the draws.':'This is a single estimate.')+'</li>';
  document.getElementById("calc").innerHTML='<ol>'+costStep+
    '<li><b>Price in the shop.</b> Add forming, packing and cold chain per kilo, then the shop\'s margin: '+
      '<span class="eq">('+d1(b)+' + '+d1(s.markup_add)+') &divide; (1 &minus; '+(s.retail_margin*100).toFixed(0)+'%) = '+d1(retail)+' a kilo</span></li>'+
    '<li><b>Against everyday meat.</b> Divide by the price of everyday meat'+tax+': '+
      '<span class="eq">'+d1(retail)+' &divide; '+d1(conv)+' = '+R.toFixed(2)+' times</span></li>'+
    '<li><b>Share.</b> Shoppers then choose by price, taste, whether it is real meat, health and welfare. '+
      'The two charts below show that step for one type of meat. <a href="#where">Where and when</a> repeats it for every type.</li></ol>'+
    '<div class="note">The page uses the same formulas as the Python model. A test checks that the two agree '+
    '(tests/run_parity.py).</div>';
}
// The settings in the address (#region=...&media_price=...): only what differs from the defaults.
function settingsHash(){
  const q=new URLSearchParams();
  if(state.region!=="global") q.set("region",state.region);
  MODEL.sliders.forEach(s=>{
    if(s.key==="income") return;
    if(s.solved){ if(state[s.key+"_ovr"]){ q.set(s.key,+(+state[s.key]).toPrecision(6)); q.set(s.key+"_ovr","1"); } return; }
    if(state[s.key]!==s.start) q.set(s.key,+(+state[s.key]).toPrecision(6));
  });
  if(Math.abs(state.income-C.REGION_INCOME[state.region])>1e-9) q.set("income",+(+state.income).toPrecision(6));
  MODEL.toggles.forEach(t=>{ if(state[t.key]) q.set(t.key,"1"); });
  if(scSettingsHash()!==SC.start) q.set("sc",scSettingsHash());
  return q.toString();
}
function readHash(){
  if(typeof location==='undefined') return;                // no address bar (the Node parity probe)
  const raw=location.hash.slice(1);
  if(raw&&raw.indexOf("=")<0){ PGS.anchor=raw; return; }   // a plain link to a level or a section (#moves)
  const q=new URLSearchParams(raw);
  if(q.get("at")) PGS.anchor=q.get("at");
  if(q.has("region") && MODEL.regions.some(r=>r[0]===q.get("region"))) state.region=q.get("region");
  state.income=C.REGION_INCOME[state.region];
  MODEL.sliders.forEach(s=>{
    if(!q.has(s.key)) return;
    const v=parseFloat(q.get(s.key)); if(!isFinite(v)) return;
    if(s.solved){ if(q.get(s.key+"_ovr")==="1"){ state[s.key]=v; state[s.key+"_ovr"]=true; } }
    else state[s.key]=Math.min(s.max,Math.max(s.min,v));
  });
  MODEL.toggles.forEach(t=>{ if(q.get(t.key)==="1") state[t.key]=true; });
  scReadHash(q.get("sc"));
  if(q.has("sc")||q.has("equal_price_share")) return;
  state.equal_price_share=SC.presets[SC.start].eqs;
}
// one place that builds a slider's value readout: the number, an "(auto)" tag for un-overridden
// solved weights, the "× taste" relative-importance suffix, and (for the price controls) β.
function setReadout(s){
  const vv=document.getElementById("v_"+s.key); if(!vv) return;
  const auto=s.solved && !state[s.key+"_ovr"];
  vv.textContent=fmtVal(s,state[s.key])+(auto?" (auto)":"")+weightSuffix(s)+priceSuffix(s);
}
// "Medium price (<i>p</i><sub>med</sub>)" -> name "Medium price", symbol "<i>p</i><sub>med</sub>";
// "Income (<i>y</i>, GDP per person)" -> name "Income (GDP per person)", symbol "<i>y</i>".
function splitLabel(label){
  const m=label.match(/^(.*?)\s*\(([^()]*)\)\s*$/);
  if(!m) return {name:label, sym:""};
  const inner=m[2], k=inner.indexOf(", ");
  return k>=0 ? {name:m[1]+" ("+inner.slice(k+2)+")", sym:inner.slice(0,k)} : {name:m[1], sym:inner};
}
function buildRail(){
  const rail=document.getElementById("rail"); if(!rail) return;
  rail.innerHTML="";
  // The main settings show at once; the rest sit in one folded section, grouped by what they are about. The three sliders of
  // the process one company reports are not shown (s.hidden): no case uses them.
  const main=document.createElement("div"); main.className="railgrid";
  const adv=document.createElement("details"); adv.className="sub";
  adv.innerHTML="<summary>All the other shopper settings ("+MODEL.sliders.filter(x=>x.adv&&!x.hidden).length+")</summary>";
  const advg=document.createElement("div"); advg.className="railgrid"; adv.appendChild(advg);
  rail.appendChild(main); rail.appendChild(adv);
  let curGroup=null;
  MODEL.sliders.forEach(s=>{
    if(s.hidden) return;
    const host=s.adv?advg:main;
    if(s.group && s.group!==curGroup){ curGroup=s.group;
      if(s.adv){ const gh=document.createElement("div");gh.className="grphdr";gh.textContent=s.group; host.appendChild(gh); } }
    const d=document.createElement("div");d.className="ctl";
    const L=splitLabel(s.label);
    d.innerHTML='<label for="r_'+s.key+'"><span class="nm">'+L.name+
      ' <span class="src">['+s.src+']</span> </span>'+
      '<span class="val" id="v_'+s.key+'"></span></label>';
    addQ(d.querySelector(".nm"), s.tip+(L.sym?" <br>Symbol in the equations: "+L.sym+".":""));
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
      lb.textContent=" set it by hand (this breaks the fit to data)";
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
  const row=document.createElement("p");
  const lk=document.createElement("button");lk.className="btn";lk.type="button";lk.textContent="Copy a link to these settings";
  lk.onclick=()=>{const url=location.href;
    (navigator.clipboard?navigator.clipboard.writeText(url):Promise.reject()).then(
      ()=>{lk.textContent="Link copied";setTimeout(()=>lk.textContent="Copy a link to these settings",1500);},
      ()=>prompt("Copy this link:",url));};
  const b=document.createElement("button");b.className="btn";b.type="button";b.textContent="Reset every setting to the Central case";
  b.onclick=()=>scApply(SC.start);
  row.appendChild(b); row.appendChild(document.createTextNode(" ")); row.appendChild(lk); rail.appendChild(row);
}
// after a case is picked: every control back in step with the settings
function pgSyncControls(){
  if(typeof document==="undefined") return;
  MODEL.sliders.forEach(s=>{ const inp=document.getElementById("r_"+s.key); if(!inp) return;
    inp.value=s.logscale?val2pos(s,state[s.key]):state[s.key];
    if(s.solved){ inp.disabled=true; const ob=document.getElementById("o_"+s.key); if(ob) ob.checked=false;
      const wd=document.getElementById("w_"+s.key); if(wd&&wd.style) wd.style.display="none"; }
    setReadout(s); });
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
  const us15=shareCalc(1.5,Kd,{ax:1,tfM:0,income:C.income_ref})*100, china15=shareCalc(1.5,Kd,{ax:1,tfM:0,income:C.REGION_INCOME.china})*100;   // the same product at one and a half times the price of meat
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
             proj:"<span class='sttag tag-proj'>MODEL OUTPUT</span>",
             judge:"<span class='sttag tag-proj'>A JUDGEMENT</span>",
             other:"<span class='sttag tag-pin'>OTHER MODEL</span>",
             claim:"<span class='sttag tag-cal'>COMPANY CLAIM</span>"};
  // cost cross-checks (inputs.py, read 2026-11-03): Humbird's non-medium cost and its plant share (24% of TCI a
  // year: capital charge 15% + maintenance 4% + insurance 5%), and Believer's announced plant cost and capacity
  const ovh=def.overhead, hb=C.humbird_plant_cost, hbPlant=C.humbird_plant_charge*C.humbird_tci_fedbatch/C.humbird_output_fedbatch;
  const hbPerT=C.humbird_tci_fedbatch/(C.humbird_output_fedbatch/1000), blPerT=C.believer_capex/(C.believer_capacity/1000);
  const blPlant=C.humbird_plant_charge*C.believer_capex/C.believer_capacity;
  const k$=x=>"$"+(x/1000).toFixed(0)+"k";
  const costRows=[
    ["Cost of everything but the medium: Humbird's independent design", "$"+ovh.toFixed(1)+" vs $"+hb.toFixed(1)+"/kg",
       "The first figure is the process a company reports: its running costs plus the same yearly charge on its plant. Humbird charges "+(C.humbird_plant_charge*100).toFixed(1)+"% of the plant's cost "+
       "a year, which is $"+hbPlant.toFixed(1)+" of his $"+hb.toFixed(1)+" in 2018 prices.", "other"],
    ["A real plant: Believer Meats, Wilson NC", k$(blPerT)+" per t/yr",
       "This is the investment per tonne of yearly capacity, as announced. Humbird's design needs "+k$(hbPerT)+". At his "+
       (C.humbird_plant_charge*100).toFixed(0)+"% a year, that plant costs $"+blPlant.toFixed(1)+"/kg, which is inside this model's $"+
       ovh.toFixed(1)+". The company built it in 2025 and closed before producing at scale.", "claim"],
  ];
  // each row: [plain-language what, model value, the real-world anchor (or meaning), tag]
  const rows=[
    ["Plant-based <b>milk</b>, same model", (mlk).toFixed(0)+"%",
       "The real share is ~15%. This is a weak test, because the milk facts are set by hand.", "match"],
    ["<b>Cultivated</b> at equal price, first contact", (cold*100).toFixed(0)+"%",
       "Lusk 2020 found ~5%. The starting wariness is set to match.", "cal"],
    ["<b>Cultivated</b> at equal price, once familiar", (s0*100).toFixed(0)+"%",
       "A setting, not a result: it assumes a third of the first wariness fades (Step 2).", "judge"],
    ["China against the US, the same product at one and a half times the price of meat",
       pgPctS(china15)+" against "+pgPctS(us15),
       "Poorer shoppers feel the premium more.", "proj"],
  ];
  const rowHTML=([what,val,obs,tag])=>
    "<tr><td class='stwhat'>"+what+"<div class='stobs'>"+obs+"</div></td>"+
    "<td class='stval'>"+val+"</td>"+
    "<td style='text-align:right;white-space:nowrap'>"+TAG[tag]+"</td></tr>";
  document.getElementById("selftest").innerHTML=
    "<div class='stanchor'>The model is fitted to plant-based meat's ~1.2% US share (model: "+(pb*100).toFixed(1)+"%) and ~89% "+
    "mainstream buyers, plus an assumed ~6% meatless rate (A4). It is not fitted to the rows below.</div>"+
    "<table><tr class='stsecrow'><td colspan='3' class='stsec'>Demand</td></tr>"+rows.map(rowHTML).join("")+
    "<tr class='stsecrow'><td colspan='3' class='stsec'>Cost</td></tr>"+costRows.map(rowHTML).join("")+"</table>"+
    "<div class='stnote'><b>MATCHES</b> means a real number that the model was not fitted to. <b>CALIBRATED</b> means the model was set to "+
    "match, so the row is a consistency check. <b>A JUDGEMENT</b> is a setting the author chose. <b>MODEL OUTPUT</b> means there is nothing real to compare yet. <b>OTHER MODEL</b> means another "+
    "study's estimate, and agreeing with it is not proof. <b>COMPANY CLAIM</b> means a company's own figure.</div>"+
    "<div class='stbuild'>"+(buildOK?"Check passed: ":"<b class='stbad'>Check failed: </b>")+"the model in this page reproduces the Python "+
    "source (the calibration and the income term across regions)"+(buildOK?".":". The page needs rebuilding.")+"</div>";
}
console.log("interactive.html JS build __BUILD_STAMP__ — loss-aversion canonical form + betaCap monotonicity guard active");
/*__SC_JS__*/
/*__VM_JS__*/
readHash();
pgSetCost();
// ---- build your own case: mirrors floor_physics.explore (checked by tests/run_parity.py) ----
function fxCell(massPg, doublingH, maint){
  const F=C.fx, mu=Math.LN2/doublingH, power=F.power_coef*Math.pow(massPg,0.75);        // pW per cell
  const q24=power*1e-12*3600/(F.heat_per_o2*1e3)/(massPg*1e-12)*1e3;                     // mmol O2 per g per h, at 24 h
  const qo2=q24*(maint+(1-maint)*mu/(Math.LN2/F.ref_doubling));                          // upkeep + the energy of growth
  return {mu:mu, qo2:qo2, o2kg:qo2/mu*32/1000, td:doublingH};
}
// The tricks (mirror of gas_exchange.packing_film / column_design / column_cost / headspace_pressure)
function fxShape(v,a){ const T=Math.pow(4*C.fx.wv*v/(Math.PI*a),1/3); return [T,a*T]; }
function fxHead(pt,v,a,dom){    // oxygen driving force (top of the tank at pt bar gauge, held at dom mmol/L) relative to Humbird's
  const F=C.fx, G=F.ge, depth=fxShape(v,a)[1], rgh=1007*9.81*depth/1e5/2;
  const cs=pp=>G.o2_henry*G.sparge_o2*(1.01325+pp+rgh)*1000, cl=cs(G.p_top_base)-F.otr/G.kla_20m3;
  const cset=dom===undefined?cl:dom, p0=pt===undefined?G.p_top_base:pt;
  return {f:(cs(p0)-cset)/(cs(G.p_top_base)-cl), cl:cset};
}
function fxShapeCost(v,a){      // mirror of gas_exchange.shape_capex_factor: steel ~ diameter x surface, plus floor
  const F=C.fx, G=F.ge, geo=aa=>{ const s=fxShape(v,aa), T=s[0], h=s[1]/F.wv, surf=Math.PI*T*h+2*G.head_area*T*T;
    return {steel:T*surf, fp:Math.pow(T+G.clearance_m,2)}; };
  const g=geo(a), g0=geo(F.aspect);
  return 1+F.bioreactor_share*(Math.pow(g.steel/g0.steel,G.vessel_cost_exp)-1)+G.hall_share*(g.fp/g0.fp-1);
}
function fxVisc(x){ const phi=x/(C.fx.cell_density*1000);
  return C.fx.medium_viscosity*1e-3*(1+2.5*phi+10.05*phi*phi+0.00273*Math.exp(16.6*phi)); }
function fxRho(x){ const phi=x/(C.fx.cell_density*1000); return 1000*((1-phi)*C.fx.medium_density+phi*C.fx.cell_density); }
function fxColumnCost(A,h){ const G=C.fx.ge, d=Math.sqrt(4*A/Math.PI), hh=h+G.col_extra_height;
  const steel=(Math.PI*d*hh+2*G.head_area*d*d)*G.col_wall*8000/0.4536;
  return (A*h*(7.31*G.pk_area+203.05)+575*Math.pow(steel,0.609)+15355*Math.pow(d,0.1764)*(1+5/6)+12019*Math.pow(d,0.1792))*G.cepci_2014; }
function fxColumn(x,us,pout,oxygen,pt,v,a,cell,rq,dom,se,af){
  const F=C.fx, G=F.ge, wv=F.wv, ptank=F.pco2_design, R=8.314, TK=310.15, g=9.81;
  const co2=rq*cell.qo2*x, o2=cell.qo2*x, depth=fxShape(v,a)[1];
  const SE=se===undefined?F.strip_eff:se, AF=af===undefined?F.antifoam:af;   // explore(strip_eff=, antifoam_otr=)
  const bySp=us/depth*3600*(ptank*100/(R*TK))*SE, co2loop=Math.max(0,co2-bySp);
  const fpp=(pt===undefined&&dom===undefined)?1:fxHead(pt,v,a,dom).f, o2short=oxygen?Math.max(0,o2-F.otr*Math.pow(us/F.gas_v,0.8)*fpp*AF):0;
  const doIn=fxHead(pt,v,a,dom).cl;                     // the culture enters at the tank's dissolved oxygen
  const uL=G.pk_load/3600, ap=G.pk_area, th=G.pk_angle*Math.PI/180, S=G.pk_side, rho=fxRho(x), mu=fxVisc(x);
  const ae=Math.min(1,1.34*Math.pow((rho/G.surface_tension)*Math.pow(g,1/3)*Math.pow(uL/ap,4/3),0.116));
  const q=uL/(ae*ap*Math.sin(th)), dl=Math.pow(3*mu*q/(rho*g*Math.sin(th)),1/3), u=q/dl;
  const kl=D=>2*Math.sqrt(D*G.pk_ce*u/(Math.PI*S)), htuC=uL/(kl(G.d_co2)*ae*ap), htuO=uL/(kl(G.d_o2)*ae*ap);
  const po=pout===undefined?G.col_pout:pout, d1=ptank-G.col_gas_out, d2=po-G.col_gas_in;
  const ntu=(ptank-po)/(Math.abs(d1-d2)>1e-9?(d1-d2)/Math.log(d1/d2):d1), h=ntu*htuC;
  const perPass=F.co2_henry*(ptank-po);          // dissolved CO2 only (no buffer: ge_buffer = 0)
  const yo2=oxygen?G.o2_sweep_purity:0.21, o2pass=(1-Math.exp(-h/htuO))*(G.o2_henry*yo2*1013-doIn);
  const passes=Math.max(co2loop/perPass,o2pass>0?o2short/o2pass:0), flow=passes*wv*v, A=flow/(uL*3600);
  const co2rem=passes*perPass*wv*v, o2given=passes*o2pass*wv*v, power=rho*g*(h+G.col_head_extra)*flow/3600/G.pump_eff;
  const capex=(fxColumnCost(A,h)+G.pump_cost*Math.pow(flow/G.pump_flow,0.6))*G.install_x;
  const outKg=wv*x*cell.mu*8760*F.uptime_col, hours=8760*F.uptime_col;
  const energy=power*hours/1000*G.power_price/v/outKg;
  const gas=oxygen?(o2given*0.032*G.o2_price+co2rem*0.074*G.lime_price/G.lime_use)*hours/v/outKg:0;
  const stay=dl*ae*ap*h/uL, loopVol=flow/3600*(stay+G.loop_transit), dph=Math.log10(ptank/po);
  const dose=dph*loopVol/(wv*v), safe=Math.log10(ptank/55)*0.5/(wv*20), paul=G.paul_dph*G.paul_share;
  return {passes:passes, flow:flow, area:A, diameter:Math.sqrt(4*A/Math.PI), height:h, capex_k_m3:capex/1000/v,
          loop_volume:loopVol, ph_rise:dph, ph_vs_safe:dose/safe, ph_vs_paul:dose/paul, passes_tested:passes<=G.passes_tested+1e-9,
          energy_kg:energy, gas_kg:gas, co2_loop:co2loop, o2_short:o2short};
}
function floorExplore(p,noSearch){
  const F=C.fx, ms=p.maint===undefined?F.maint_share:p.maint, vm=p.vm||{};   // vm: vessel and mode (vessels.py)
  const perf=vm.washed!==undefined?vm.washed:p.mode==="perfusion", cyclic=vm.kind==="cyclic", wv=vm.wv!==undefined?vm.wv:F.wv;
  const cell=fxCell(p.mass_pg,vm.dil_frac?p.doubling_h/vm.dil_frac:p.doubling_h,ms), ref=fxCell(F.ref_mass,F.ref_doubling,F.maint_share);
  const load=cell.qo2/ref.qo2, burn=cell.o2kg/ref.o2kg;
  // salt strength: how much lactate the culture may hold at this CO2 level and pH (mirror of floor_physics.explore)
  const pcTol=p.pco2===undefined?F.pco2:p.pco2, osmLim=p.osm_limit===undefined?F.osm_limit:p.osm_limit, ph=p.ph===undefined?F.ph:p.ph;
  const hco3=F.co2_henry*pcTol*Math.pow(10,ph-F.pk1), osmCo2=2*Math.max(0,hco3-F.hco3_base);
  const lacRoom=Math.min(F.lac_limit,Math.max(1,(osmLim-F.osm_base-osmCo2)/2));
  if(!noSearch&&perf&&p.medium_l===undefined&&lacRoom<F.lac_limit){
    // the salt limit binds: run the tank at the CO2 level, up to what the cells tolerate, that costs least
    let best=null;
    for(let i=0;i<60;i++){ const r=floorExplore(Object.assign({},p,{pco2:pcTol*(i+1)/60}),true); if(best===null||r.total<best.total) best=r; }
    return best;
  }
  let capex=F.capex[p.plant], sized=F.sized[p.plant], extra=0;
  if(p.items){ let k=0;                                          // a plant built item by item (plant_items.capital)
    Object.keys(F.items).forEach(it=>{ k+=F.items[it][p.items[it]||Object.keys(F.items[it])[0]][0]; });
    capex=k*F.escalation; sized=true; extra=p.items.oxygen==="bought"?F.o2_opex:0; }
  else if(p.plant==="microbial"&&vm.o2_gas!==false&&F.o2_microbial) extra=F.o2_opex;   // no oxygen unit in this class's price
  { const per=v=>(30.7*v+800)/v, sf=sized?per(p.vessel_m3)/per(20):1;             // another vessel: its unit price ratio
    if(vm.capex_ratio!==undefined) capex*=(1-F.bioreactor_share)+F.bioreactor_share*sf*vm.capex_ratio;
    else if(sized) capex*=(1-F.bioreactor_share)+F.bioreactor_share*sf; }
  capex*=(p.capex_x===undefined?1:p.capex_x);                    // uncertainty in the plant estimate (tornado)
  if(p.shape_cost!==false&&p.aspect!==undefined) capex*=fxShapeCost(p.vessel_m3,p.aspect);   // steel and floor of a squat tank
  const tff=perf&&!vm.own_retention&&p.retention===undefined&&F.tff.on;   // the default device, priced after the medium
  if(perf&&!vm.own_retention&&!tff) capex+=(p.retention===undefined?F.retention:p.retention);
  // a run ends at its planned length or when contaminated; then the tank is cleaned and regrown
  let uptime=p.uptime, lost=0, cycleH=null, runsYr=null, runFrac=1;
  if(cyclic){                       // cycles: n doublings, then empty, clean and refill; a loss costs the cycle and a restart
    const h=p.hazard||0, grow=vm.n_doublings*cell.td; cycleH=grow+vm.turnaround_h;
    const pFail=h<=0?0:1-Math.exp(-h*cycleH/24);
    cycleH+=24*pFail*vm.restart_days; lost=Math.min(0.9,pFail); uptime=grow/cycleH; runsYr=8760/cycleH;
  } else if(uptime===undefined){
    const clean=vm.clean_uptime!==undefined?vm.clean_uptime:(p.mode==="perfusion"?F.uptime_perfusion:F.uptime_filldraw), restart=F.run_days*(1/clean-1);
    const L=p.run_days===undefined?(vm.run_days!==undefined?vm.run_days:F.run_days):p.run_days, h=p.hazard||0;
    const T=h<=0?L:(1-Math.exp(-h*L))/h, pFail=h<=0?0:1-Math.exp(-h*L);
    const down=p.restart_fail===undefined?restart:(1-pFail)*restart+pFail*Math.max(restart,p.restart_fail);
    uptime=T/(T+down); runsYr=365/(T+down); lost=Math.min(0.9,pFail/(cell.mu*24*T));
    runFrac=T/L;                    // a lost run throws its membranes away early
  }
  // tank shape, then the CO2 balance: removal = (gas velocity / liquid depth) x pCO2/RT; production = RQ x qO2
  const ar=p.aspect===undefined?F.aspect:p.aspect, us=p.gas_v===undefined?F.gas_v:p.gas_v, pc=p.pco2===undefined?F.pco2:p.pco2;
  const tankT=(v,a)=>Math.pow(4*F.wv*v/(Math.PI*a),1/3), T=tankT(p.vessel_m3,ar), depth=ar*T;
  const SE=p.strip_eff===undefined?F.strip_eff:p.strip_eff, AF=p.antifoam_otr===undefined?F.antifoam:p.antifoam_otr;
  const xCo2=us/depth*3600*(pc*100/(8.314*310.15))*SE/((p.rq!==undefined?p.rq:F.rq-F.rq_lipid*(p.fat_fed||0))*cell.qo2);
  const tmRel=Math.pow(T/tankT(20,F.aspect),2/3)*Math.pow(ar/F.aspect,2.5);
  const col=p.column||"none", fP=(p.p_top===undefined&&p.do_mmol===undefined)?1:fxHead(p.p_top,p.vessel_m3,ar,p.do_mmol).f;   // the tricks
  const rq=p.rq!==undefined?p.rq:F.rq-F.rq_lipid*(p.fat_fed||0);   // fat from the feed releases no lipogenic CO2
  const limits=[["oxygen supply",col==="o2_closed"?Infinity:F.otr*Math.pow(us/F.gas_v,0.8)/cell.qo2*fP*AF],["thickness of the culture",F.x_visc],
                ["mixing",F.otr/cell.qo2*F.mix_ratio/tmRel*fP],
                ["CO2 removal",col!=="none"?Infinity:xCo2]];
  if(p.vm){ limits[0][1]*=(vm.otr_mult===undefined?1:vm.otr_mult);         // the vessel's own gas exchange
    if(vm.mixing===false) limits[2][1]=Infinity; if(vm.co2_gas===false) limits[3][1]=Infinity; if(vm.o2_gas===false) limits[0][1]=Infinity;
    limits[3][1]*=(vm.co2_mult===undefined?1:vm.co2_mult);
    Object.keys(vm.caps||{}).forEach(k=>limits.push([k,vm.caps[k]])); }
  const w=p.waste||0;
  const nh3=p.nh3_kg!==undefined?p.nh3_kg:(F.nh3[0]+w*(F.nh3[1]-F.nh3[0]))*burn;        // mol per kg wet cells
  // glucose from what the cells build, burn and ferment (mirror of floor_physics.glucose_balance), when the scenarios ask
  const glcBal=(F.glc_anabolic*(1-0.75*(p.fat_fed||0))+Math.max(0,cell.o2kg*1000/32-2.25*nh3)/6)/Math.max(0.05,1-(p.lac_yield||0)/2);
  const lac=p.lac_yield!==undefined?p.lac_yield*(p.glc_kg!==undefined?p.glc_kg:(p.glc_balance?glcBal:F.glc_kg)):(F.lac[0]+w*(F.lac[1]-F.lac[0]))*burn;
  const nh3Lim=p.nh3_limit===undefined?F.nh3_limit:p.nh3_limit;      // the scenarios carry their own (SC.always)
  // ammonia relative to enhanced cells, at the ammonia limit in force (mirror of floor_physics.explore: a tank that is not
  // washed builds waste up to the limit, so a lower limit caps the density sooner)
  const wf=nh3/(F.nh3[0]*burn)*(F.nh3_limit/nh3Lim);
  const flow=p.min_perfusion===undefined?F.min_perfusion:p.min_perfusion;
  // a tank that is not washed is capped by whichever waste builds up first: ammonia (wf) or, when the cells' lactate yield is
  // set explicitly, lactate relative to the enhanced cells at the same oxygen burn (lf). Mirror of floor_physics.explore.
  const lf=p.lac_yield!==undefined?lac/(F.lac[0]*burn):0;
  if(!perf){ limits.push(["waste build-up",F.x_waste/load/Math.max(wf,lf)]);
    limits.push(["other by-products",1000*cell.mu*24/flow]); }   // least medium flow caps the density of a drained-and-refilled tank
  let lim=limits[0]; limits.forEach(l=>{if(l[1]<lim[1]) lim=l;});
  const shape=vm.shape!==undefined?vm.shape:(perf?1:F.draw/Math.log(1/(1-F.draw))), rec=vm.recovery===undefined?1:vm.recovery;
  const out=cyclic?wv*lim[1]*rec*8760/cycleH/1000*(1-lost):wv*lim[1]*cell.mu*shape*8760*uptime/1000*(1-lost)*rec;
  let colR=null;
  if(col!=="none"){ colR=fxColumn(lim[1],us,p.col_pout,col==="o2_closed",p.p_top,p.vessel_m3,ar,cell,rq,p.do_mmol,p.strip_eff,p.antifoam_otr); capex+=colR.capex_k_m3; }
  let capital=p.charge*capex/out; const labour=F.labour_ref/out*(vm.labour_mult===undefined?1:vm.labour_mult);
  let utilities=F.utilities*(0.5+0.5*burn); if(colR) utilities+=colR.energy_kg+colR.gas_kg;
  const eat=F.aa+F.glucose*(0.5+0.5*burn)+F.other;
  // litres per kg: ammonia (less what a sorbent takes), lactate within the salt limit, the sorbent's sodium, and the
  // least flow a cell needs for everything else
  const sorb=perf?(p.sorbent||0):0; const terms={};
  let need=1000/lim[1];
  if(p.medium_l===undefined){
    if(perf){ terms["ammonia"]=nh3*(1-sorb)/(nh3Lim/1000); terms["lactate"]=lac/(lacRoom/1000); terms["least flow"]=flow/(cell.mu*24);
      if(sorb>0) terms["salt"]=1000*(2*lac+sorb*nh3)/Math.max(2,osmLim-F.osm_base-osmCo2);
      if(!vm.own_retention) terms["harvest"]=1000/lim[1];      // the culture that leaves with the harvested cells must be replaced
      need=Math.max.apply(null,Object.keys(terms).map(k=>terms[k])); }
    terms["nutrients"]=F.medium_l; }
  let setBy=""; Object.keys(terms).forEach(k=>{ if(setBy===""||terms[k]>terms[setBy]) setBy=k; });
  const ml=p.medium_l===undefined?Math.max(F.medium_l,need):((perf&&!vm.own_retention)?Math.max(p.medium_l,1000/lim[1]):p.medium_l), mp=p.medium_price===undefined?0.15:p.medium_price;
  let consumables=F.consumables, retCapex=0, membranes=0;
  if(tff){                                   // the TFF loop clears what the bleed of cells does not carry out
    let perm=Math.max(0,ml-1000/lim[1]); const kgH=out*1000/(8760*uptime);
    if(sorb>0) perm+=sorb*nh3/(nh3Lim/1000);     // the permeate sent through the exchanger and back passes the filter too
    const area=perm*kgH/(p.flux===undefined?F.tff.flux:p.flux);
    retCapex=area*F.tff.hw*F.tff.install; membranes=perm*F.tff.mem_price/((p.membrane_life===undefined?F.tff.mem_life:p.membrane_life)*runFrac);
    capex+=retCapex; capital+=p.charge*retCapex/out; consumables+=membranes; }
  if(vm.cons_run) consumables+=vm.cons_run*(runsYr!==null?runsYr:365/(p.run_days||F.run_days))/out;   // what the vessel throws away
  if(p.fat_fed) consumables+=p.fat_fed*F.fat_kg*(p.fat_price!==undefined?p.fat_price:F.fat_price);
  if(sorb>0) consumables+=sorb*nh3/(p.sorbent_q!==undefined?p.sorbent_q:F.sorbent_q)*(p.sorbent_price!==undefined?p.sorbent_price:F.sorbent_price)
                          /(p.sorbent_cycles!==undefined?p.sorbent_cycles:F.sorbent_cycles);
  let protectant=0;                                     // poloxamer leaves with every litre of a sparged tank's medium
  if((vm.o2_gas!==false||vm.co2_gas!==false)&&!vm.no_protectant){ protectant=ml*F.protect_dose/1000*(p.protectant_price===undefined?F.protect_price:p.protectant_price); consumables+=protectant; }
  const gfPer=F.gf*ml/F.gf_litres, gf=gfPer*(+p.growth_factors||0), cs=p.cell_share===undefined?1:p.cell_share;   // growth factors scale with litres
  const feed=Math.max(eat+gfPer*(+p.gf_in_medium||0),ml*mp)/(1-lost);   // a complete medium cannot cost less than nutrients + its growth factors
  const total=capital+labour+utilities+consumables+feed+gf+extra;
  const mu24=Math.LN2/F.ref_doubling, q24=cell.qo2/(ms+(1-ms)*cell.mu/mu24), o2up=q24*ms/cell.mu, o2gr=q24*(1-ms)/mu24;
  const lims={}; limits.forEach(l=>{lims[l[0]]=l[1];});
  return {density:lim[1], limit:lim[0], output:out, capex:capex, extra_opex:extra, retention_capex:retCapex, membranes:membranes, protectant:protectant, capital:capital, labour:labour,
          utilities:utilities, consumables:consumables, feedstock:feed, growth_factors:gf, uptime:uptime,
          medium_l:ml, total:total, product:cs*total+(1-cs)*F.filler, medium_floor:eat>=ml*mp,
          pco2_used:pcTol, osmolality:perf&&p.medium_l===undefined?F.osm_base+osmCo2+(2*lac+sorb*nh3)/ml*1000:NaN,
          limits:lims, medium_terms:terms, medium_set_by:setBy, nh3_kg:nh3, lac_kg:lac, column:colR,
          rq:rq, o2_kg:cell.qo2/cell.mu, o2_kg_upkeep:o2up, o2_kg_growth:o2gr, co2_kg:rq*cell.qo2/cell.mu};
}
// Tornado: each limiting factor moved alone across its range around the current case (mirror of
// floor_physics.floor_tornado; checked by tests/run_parity.py). Returns [label, cost at low, cost at high, low text, high text].
let fxPco2Range=null;   // the selected species' CO2-tolerance range [low, high] in mbar (null = the general one)
function fxTornadoRows(p,pco2Range){
  const q=Object.assign({},p); if(q.restart_fail===undefined||q.restart_fail<14) q.restart_fail=14;
  return C.fx.tornado.map((t,k)=>{
    let lo=t[2], hi=t[3], loT=t[4], hiT=t[5];
    if(t[1]==="pco2"&&pco2Range){ lo=pco2Range[0]; hi=pco2Range[1]; loT=lo.toFixed(0)+" mbar"; hiT=hi.toFixed(0)+" mbar"; }
    const drop=t[1]==="plant"?{items:undefined}:{};              // a class of plant replaces the chosen items
    const a=floorExplore(Object.assign({},q,drop,{[t[1]]:lo})).total, b=floorExplore(Object.assign({},q,drop,{[t[1]]:hi})).total;
    return [t[0],a,b,loT,hiT,k,lo,hi];
  }).sort((x,y)=>Math.abs(y[2]-y[1])-Math.abs(x[2]-x[1]));
}
let fxTorSel=null;     // index into C.fx.tornado of the factor whose card is open
function fxTornadoDraw(p,base,parity){
  const allRows=fxTornadoRows(p,fxPco2Range), rows=allRows.filter(r=>Math.abs(r[1]-base)>=0.05||Math.abs(r[2]-base)>=0.05);
  const W=640, L=218, R=14, rh=30, top=22, H=top+rows.length*rh+26;
  const all=rows.reduce((a,r)=>a.concat([r[1],r[2]]),[base,parity]);
  const mn=Math.min.apply(null,all), hi=Math.min(Math.max.apply(null,all)*1.05,base*4), lo=Math.max(0,mn-0.12*(hi-mn));   // room for the value labels
  const X=v=>L+(Math.min(v,hi)-lo)/(hi-lo)*(W-L-R), esc=t=>String(t).replace(/&/g,"&amp;").replace(/</g,"&lt;");
  let g='<svg viewBox="0 0 '+W+' '+H+'" style="width:'+Math.round(W*1.22)+'px;max-width:none;height:auto;display:block" role="img" aria-label="Tornado chart of limiting factors">';
  rows.forEach((r,i)=>{   // a wide, clickable band per factor (drawn first, under the bars)
    g+='<rect class="fxrow'+(r[5]===fxTorSel?" sel":"")+'" x="0" y="'+(top+i*rh-3)+'" width="'+W+'" height="'+rh+'" onclick="fxTorInfo('+r[5]+')"><title>Click for what this is and where its range comes from</title></rect>';
  });
  g+='<line x1="'+X(base)+'" x2="'+X(base)+'" y1="'+(top-6)+'" y2="'+(H-22)+'" stroke="#444" stroke-width="1" pointer-events="none"/>';
  g+='<text x="'+X(base)+'" y="12" font-size="10" text-anchor="middle" fill="#444">this case $'+base.toFixed(1)+'</text>';
  if(parity>lo&&parity<hi){ g+='<line x1="'+X(parity)+'" x2="'+X(parity)+'" y1="'+(top-6)+'" y2="'+(H-22)+'" stroke="#CC3311" stroke-width="1" stroke-dasharray="3 3" pointer-events="none"/>';
    g+='<text x="'+X(parity)+'" y="'+(H-10)+'" font-size="10" text-anchor="middle" fill="#CC3311">parity $'+parity.toFixed(0)+'</text>'; }
  rows.forEach((r,i)=>{
    const y=top+i*rh;
    g+='<g pointer-events="none"><text x="'+(L-8)+'" y="'+(y+13)+'" font-size="11" text-anchor="end" fill="#1a1a1a"'+(r[5]===fxTorSel?' font-weight="700"':'')+'>'+esc(r[0])+'</text>';
    [[r[1],r[3]],[r[2],r[4]]].forEach(e=>{
      const v=e[0]; if(Math.abs(v-base)<0.05) return;
      const x0=Math.min(X(v),X(base)), w=Math.abs(X(v)-X(base)), col=v<base?"#029E73":"#CC3311", clipped=v>hi;
      g+='<rect x="'+x0+'" y="'+(y+2)+'" width="'+Math.max(w,1)+'" height="14" fill="'+col+'" opacity="0.85"/>';
      g+='<text x="'+(v<base?x0-3:x0+w+3)+'" y="'+(y+13)+'" font-size="10" text-anchor="'+(v<base?"end":"start")+'" fill="'+col+'">$'+v.toFixed(1)+(clipped?"+":"")+'</text>';
      // range labels run away from the base line, so the two ends of a factor never collide
      g+='<text x="'+(v<base?X(base)-4:X(base)+4)+'" y="'+(y+26)+'" font-size="9" text-anchor="'+(v<base?"end":"start")+'" fill="#777">'+esc(e[1])+'</text>';
    });
    g+='</g>';
  });
  g+='</svg>';
  const none=allRows.filter(r=>rows.indexOf(r)<0);
  if(none.length) g+='<p class="fxn">No effect on this case: '+none.map(r=>'<a href="#" onclick="fxTorInfo('+r[5]+');return false">'+esc(r[0]).toLowerCase()+'</a>').join(", ")+'.</p>';
  return g;
}
// which panel control carries each factor, and the factor of its unit (null = a select; "check" = the checkbox)
const FX_TOR_CTL={osm_limit:["fx_os",1],ph:["fx_ph",1],min_perfusion:["fx_mf",1],doubling_h:["fx_dh",1],mass_pg:["fx_m",0.001],pco2:["fx_pc",1],gas_v:["fx_gv",1000],aspect:["fx_ar",1],
  waste:["fx_ws",100],charge:["fx_ch",100],hazard:["fx_hz",100],maint:["fx_ms",100],medium_price:["fx_mp",1],
  plant:["fx_pl",null],mode:["fx_mo",null],vessel_m3:["fx_v",null],growth_factors:["fx_gf",100],p_top:["fx_pt",1],nh3_kg:["fx_nh",1]};
function fxTorSet(k,end){          // put the panel's control at one end of factor k's range
  const t=C.fx.tornado[k], c=FX_TOR_CTL[t[1]]; if(!c) return;
  const v=(t[1]==="pco2"&&fxPco2Range)?fxPco2Range[end?1:0]:t[end?3:2];
  const el=document.getElementById(c[0]);
  if(c[1]==="check") el.checked=!!v; else el.value=(c[1]===null?v:v*c[1]);
  if(t[1]==="hazard"&&v>0) document.getElementById("fx_rf").value=14;
  if(t[1]==="nh3_kg") document.getElementById("fx_wm").value="sep";
  fxRender();
}
function fxTorInfo(k){
  fxTorSel=(fxTorSel===k?null:k); fxRender();
}
function fxTorCard(){
  const box=document.getElementById("fx_torinfo");
  if(fxTorSel===null){ box.innerHTML='<span class="fxn">Click a factor to see what it is, where its range comes from and how solid the evidence is.</span>'; return; }
  const t=C.fx.tornado[fxTorSel], c=FX_TOR_CTL[t[1]];
  const rng=(t[1]==="pco2"&&fxPco2Range)?[fxPco2Range[0].toFixed(0)+" mbar",fxPco2Range[1].toFixed(0)+" mbar"]:[t[4],t[5]];
  const btn=(end,txt)=>'<button class="btn" style="margin:4px 6px 0 0" onclick="fxTorSet('+fxTorSel+','+end+')">Set to '+txt+'</button>';
  box.innerHTML='<b>'+t[0]+'.</b> '+t[6]+'<br>'+(c?btn(0,rng[0])+btn(1,rng[1])
    :'<span class="fxn">This one has no control above. It is an uncertainty in the estimate, not a design choice.</span>')+
    '<button class="btn" style="margin:4px 0 0 0" onclick="fxTorInfo('+fxTorSel+')">Close</button>';
}
function fxSpecies(){
  const sel=document.getElementById("fx_sp"), sp=C.fx.species[sel.value]; if(!sp) return;
  document.getElementById("fx_dh").value=sp[1]; document.getElementById("fx_m").value=sp[2]/1000;
  // waste level that gives the reported litres per kg at this cell's doubling time (0 if none reported)
  let ws=0;
  if(sp[3]!==null){const F=C.fx, c=fxCell(sp[2],sp[1],F.maint_share), r=fxCell(F.ref_mass,F.ref_doubling,F.maint_share);
    const burn=c.o2kg/r.o2kg; ws=Math.max(0,Math.min(1,(sp[3]*F.nh3_limit/1000/burn-F.nh3[0])/(F.nh3[1]-F.nh3[0])));}
  document.getElementById("fx_ws").value=Math.round(ws*100); document.getElementById("fx_wm").value="dial";
  // CO2 tolerance: the species' own value where it differs, and its plausible range for the tornado
  document.getElementById("fx_pc").value=(sp[4]===null?C.fx.pco2:sp[4]); fxPco2Range=sp[5];
  // a preset of a whole operation also fixes how the tank is run, the plant and the financing
  const ex=sp[6]; if(ex){
    if(ex.mode) document.getElementById("fx_mo").value=ex.mode;
    if(ex.plant) document.getElementById("fx_pl").value=ex.plant;
    if(ex.charge) document.getElementById("fx_ch").value=ex.charge*100;
    if(ex.waste!==undefined) document.getElementById("fx_ws").value=ex.waste*100; }
  document.getElementById("fx_spn").innerHTML=sp[7]; fxRender();
}
let fxDefaults=null;
function fxInit(){
  const sel=document.getElementById("fx_sp");
  Object.keys(C.fx.species).forEach(k=>{const o=document.createElement("option");o.value=k;o.textContent=C.fx.species[k][0];sel.appendChild(o);});
  document.getElementById("fx_ms").value=Math.round(100*C.fx.maint_share);
  const box=document.getElementById("fx_items");
  Object.keys(C.fx.items).forEach(it=>{
    const d=document.createElement("div"); d.className="ctl";
    d.innerHTML='<label for="fx_it_'+it+'"><span class="nm">'+C.fx.item_labels[it]+'</span></label><select id="fx_it_'+it+'" onchange="fxItem()">'+
      Object.keys(C.fx.items[it]).map(o=>'<option value="'+o+'">'+C.fx.items[it][o][1]+'</option>').join("")+'</select>';
    box.appendChild(d); });
  sel.value="model"; fxSpecies();
  fxDefaults={}; document.getElementById("fx").querySelectorAll("input,select").forEach(e=>{ if(e.id) fxDefaults[e.id]=(e.type==="checkbox"?e.checked:e.value); });
  fxFromScenario(SC.start);
}
function fxMode(){fxRender();}
function fxItem(){ document.getElementById("fx_pl").value="custom"; fxRender(); }   // an item changed by hand
// Send the panel's case to the charts: every chart takes its cost from the case (the switches in "What decides it" step aside).
let fxLast=null;
function fxApply(){
  if(!fxLast) return;
  SCS.src="custom"; SCS.preset=null; SCS.customCost=fxLast.total; scCommit();
  document.getElementById("fx_apply_msg").innerHTML="Done: the page now runs at $"+fxLast.total.toFixed(1)+" a kilo of cells, as your own settings.";
}
// "What limits this tank": one bar per limit (density it allows), the binding one in the accent colour, the
// floor case faintly behind; below it, the litres of medium per kilo and what sets them.
function fxFloorCase(){ return {doubling_h:24, mass_pg:3000, vessel_m3:20, plant:"sanitary", mode:"perfusion", charge:C.fx.charge_mature}; }
function fxLimitsDraw(r,f){
  const esc=t=>String(t).replace(/&/g,"&amp;").replace(/</g,"&lt;");
  const name={"CO2 removal":"CO\u2082 removal","oxygen supply":"Oxygen supply","mixing":"Mixing","thickness of the culture":"Thickness of the culture",
              "waste build-up":"Waste build-up","other by-products":"Other by-products"};
  const keys=Object.keys(r.limits), W=640, L=170, R=60, rh=24, top=18;
  const fin=keys.map(k=>r.limits[k]).concat(Object.keys(f.limits).map(k=>f.limits[k])).filter(v=>isFinite(v));
  const mx=Math.max(300,Math.ceil(Math.max.apply(null,fin)/50)*50), X=v=>L+Math.min(v,mx)/mx*(W-L-R);
  const XI=v=>isFinite(v)?X(v):L+0.8*(W-L-R);       // a limit the tricks remove: a bar to 80% of the axis
  const bar=(y,v,style)=>'<rect x="'+L+'" y="'+y+'" width="'+Math.max(1,XI(v)-L)+'" height="14" style="'+style+'"/>';
  const H1=top+keys.length*rh+18;
  let g='<svg viewBox="0 0 '+W+' '+H1+'" style="width:'+Math.round(W*1.22)+'px;max-width:none;height:auto;display:block" role="img" aria-label="Density each limit allows">';
  g+='<text x="'+L+'" y="11" font-size="10" style="fill:var(--muted)">g of cells per litre the tank can hold</text>';
  keys.forEach((k,i)=>{
    const y=top+i*rh, v=r.limits[k], fv=f.limits[k], bind=(k===r.limit);
    g+='<text x="'+(L-8)+'" y="'+(y+11)+'" font-size="11" text-anchor="end" style="fill:var(--ink)"'+(bind?' font-weight="700"':'')+'>'+esc(name[k]||k)+'</text>';
    if(fv!==undefined) g+=bar(y-3,fv,"fill:var(--muted);opacity:0.18");
    g+=bar(y,v,bind?"fill:var(--accent)":"fill:var(--muted);opacity:0.55");
    g+='<text x="'+(XI(v)+4)+'" y="'+(y+11)+'" font-size="10" style="fill:'+(bind?'var(--accent)':'var(--muted)')+'">'+
       (isFinite(v)?v.toFixed(0)+" g/L":"none (column)")+(bind?" (binds)":"")+'</text>';
  });
  g+='<text x="'+L+'" y="'+(H1-4)+'" font-size="9" style="fill:var(--muted)">faint: Humbird\'s optimistic design (holds '+f.density.toFixed(0)+' g/L, limited by '+esc(f.limit)+')</text></svg>';
  // medium litres per kilo, by what sets them
  const mk=Object.keys(r.medium_terms);
  if(mk.length){
    const mname={"ammonia":"Washing out ammonia","lactate":"Washing out lactate","salt":"Salt from the sorbent","least flow":"Least flow the cells need","harvest":"Liquid that leaves with the cells","nutrients":"Nutrients the cells eat"};
    const mvals=mk.map(k=>r.medium_terms[k]).concat(Object.keys(f.medium_terms).map(k=>f.medium_terms[k]));
    const mm=Math.max(20,Math.ceil(Math.max.apply(null,mvals)/10)*10), XM=v=>L+Math.min(v,mm)/mm*(W-L-R), H2=top+mk.length*rh+6;
    g+='<svg viewBox="0 0 '+W+' '+H2+'" style="width:'+Math.round(W*1.22)+'px;max-width:none;height:auto;display:block;margin-top:6px" role="img" aria-label="Litres of medium per kilo and what sets them">';
    g+='<text x="'+L+'" y="11" font-size="10" style="fill:var(--muted)">litres of medium per kilo of cells that each need asks for. The largest sets the amount ('+r.medium_l.toFixed(1)+' L)</text>';
    mk.forEach((k,i)=>{
      const y=top+i*rh, v=r.medium_terms[k], fv=f.medium_terms[k], bind=(k===r.medium_set_by);
      g+='<text x="'+(L-8)+'" y="'+(y+11)+'" font-size="11" text-anchor="end" style="fill:var(--ink)"'+(bind?' font-weight="700"':'')+'>'+esc(mname[k]||k)+'</text>';
      if(fv!==undefined) g+='<rect x="'+L+'" y="'+(y-3)+'" width="'+Math.max(1,XM(fv)-L)+'" height="14" style="fill:var(--muted);opacity:0.18"/>';
      g+='<rect x="'+L+'" y="'+y+'" width="'+Math.max(1,XM(v)-L)+'" height="14" style="'+(bind?"fill:var(--orange)":"fill:var(--muted);opacity:0.55")+'"/>';
      g+='<text x="'+(XM(v)+4)+'" y="'+(y+11)+'" font-size="10" style="fill:'+(bind?'var(--ink)':'var(--muted)')+'">'+v.toFixed(1)+' L'+(v>mm?'+':'')+'</text>';
    });
    g+='</svg>';
  }
  return g;
}
function fxRender(){
  const g=id=>document.getElementById(id), num=id=>parseFloat(g(id).value);
  const pl=g("fx_pl").value, its={};
  // the class of plant sets every item; "custom" leaves them as chosen. Humbird's two classes and the as-built
  // yeast plant keep their own price; the others are the sum of their items
  if(pl!=="custom") Object.keys(C.fx.items).forEach(it=>{ g("fx_it_"+it).value=C.fx.plant_items[pl][it]; });
  Object.keys(C.fx.items).forEach(it=>{ its[it]=g("fx_it_"+it).value; });
  const byItems=(pl==="lean"||pl==="yeastplus"||pl==="custom");
  const p={doubling_h:num("fx_dh"), mass_pg:num("fx_m")*1000, vessel_m3:num("fx_v"), plant:byItems?"sanitary":pl,
           items:byItems?its:undefined, mode:g("fx_mo").value, charge:num("fx_ch")/100, maint:num("fx_ms")/100,
           hazard:num("fx_hz")/100, run_days:num("fx_rd"), restart_fail:num("fx_rf"),
           waste:num("fx_ws")/100, medium_price:num("fx_mp"),
           pco2:num("fx_pc"), gas_v:num("fx_gv")/1000, aspect:num("fx_ar"),
           osm_limit:num("fx_os"), ph:num("fx_ph"), min_perfusion:num("fx_mf"), growth_factors:num("fx_gf")/100, cell_share:num("fx_cs")/100,
           column:g("fx_col").value, col_pout:num("fx_cp"), p_top:num("fx_pt"),
           sorbent:num("fx_sb")/100, sorbent_price:num("fx_spx"), sorbent_cycles:num("fx_scy"), fat_fed:num("fx_fat")/100};
  if(Math.abs(num("fx_do")-C.fx.do_implied)>0.003) p.do_mmol=num("fx_do");     // the default slider position is the floor's
  const sep=g("fx_wm").value==="sep";
  if(sep){ p.nh3_kg=num("fx_nh"); p.lac_yield=num("fx_ly"); p.glc_kg=num("fx_gk"); }
  if(fxCarry){                     // loaded from a case: what the case carries and the panel has no lever for (page_scenarios.js)
    if(fxCarry.nh3_limit!==undefined) p.nh3_limit=fxCarry.nh3_limit;
    if(fxCarry.gf_in_medium&&p.growth_factors===0) p.gf_in_medium=fxCarry.gf_in_medium;
    if(fxCarry.glc_balance&&sep&&g("fx_gk").value===fxCarry.gk){ delete p.glc_kg; p.glc_balance=true; } }
  ["fx_nh","fx_ly","fx_gk"].forEach(id=>{ g(id).disabled=!sep; });
  g("fx_cp").disabled=(p.column==="none");
  { const air=C.fx.ge.o2_henry*0.2095*1013, dv=num("fx_do"), rqv=C.fx.rq-C.fx.rq_lipid*p.fat_fed;
    g("fx_do_v").textContent=dv.toFixed(3)+" mmol/L ("+(dv/air*100).toFixed(0)+"% of air)";
    g("fx_fat_v").textContent=(p.fat_fed*100).toFixed(0)+"%: cells give off "+rqv.toFixed(2)+" CO\u2082 per oxygen used"; }
  g("fx_cp_v").textContent=p.col_pout.toFixed(0)+" mbar, against "+p.pco2.toFixed(0)+" in the tank";
  { const rc=p.column!=="none"?floorExplore(p).column:null;
    g("fx_col_v").textContent=rc?rc.passes.toFixed(0)+" passes an hour, "+rc.flow.toFixed(0)+" m\u00b3/h":""; } g("fx_pt_v").textContent=p.p_top.toFixed(2)+" bar above the air outside";
  { const nh=num("fx_nh"), tag=Math.abs(nh-0.055)<0.003?" (the engineered cell)":Math.abs(nh-0.14)<0.005?" (glutamine replaced)":Math.abs(nh-0.70)<0.01?" (ordinary cells)":"";
    g("fx_nh_v").textContent=nh.toFixed(3)+" mol per kilo of cells"+tag; }
  g("fx_ly_v").textContent=num("fx_ly").toFixed(2)+" lactate per glucose";
  g("fx_gk_v").textContent=num("fx_gk").toFixed(2)+" mol per kilo of cells"; g("fx_sb_v").textContent=(p.sorbent*100).toFixed(0)+"%";
  if(!(p.doubling_h>0)) return;
  g("fx_dh_v").textContent=p.doubling_h.toFixed(0)+" h"; g("fx_m_v").textContent=(p.mass_pg/1000).toFixed(1)+" ng";
  g("fx_ch_v").textContent=(p.charge*100).toFixed(1)+"% of its cost"; g("fx_ms_v").textContent=(p.maint*100).toFixed(0)+"%";
  g("fx_hz_v").textContent=(p.hazard*100).toFixed(1)+"%"; g("fx_rd_v").textContent=p.run_days.toFixed(0)+" days";
  g("fx_rf_v").textContent=p.restart_fail.toFixed(0)+" days"; g("fx_pc_v").textContent=p.pco2.toFixed(0)+" mbar"; g("fx_gv_v").textContent=(p.gas_v*1000).toFixed(1)+" mm/s";
  g("fx_ar_v").textContent=p.aspect.toFixed(1); g("fx_os_v").textContent=p.osm_limit.toFixed(0)+" mOsm/kg";
  g("fx_ph_v").textContent=p.ph.toFixed(2); g("fx_mf_v").textContent=p.min_perfusion.toFixed(1)+" mL per g a day"; g("fx_ws_v").textContent=(p.waste*100).toFixed(0)+"% of the way to ordinary cells";
  g("fx_gf_v").textContent=(p.growth_factors*100).toFixed(0)+"%"; g("fx_mp_v").textContent=p.medium_price<0.005?"at the nutrient floor":"$"+p.medium_price.toFixed(2)+" a litre"; g("fx_cs_v").textContent=(p.cell_share*100).toFixed(0)+"%";
  const r=floorExplore(p), def=MODEL.sliders.reduce((d,s)=>{d[s.key]=s.default;return d;},{});
  fxLast=r; { const m=document.getElementById("fx_apply_msg"); if(m) m.innerHTML=""; }
  const R=shelfPrice(r.product,def)/C.p_conv_anchor, blend=p.cell_share<1;
  // long-run share against $12 meat (US): a blend is credited as real meat in proportion to its cells [assumed]
  def.region="us"; def.income=C.income_ref;
  const K=KP||effConsts(def), sh=shareCalc(R,K,{ax:1,tfM:0,rtx:p.cell_share*(K.real_tissue_x!==undefined?K.real_tissue_x:1)});
  g("fx_out").innerHTML="<b>$"+r.total.toFixed(1)+" per kilo of cells"+
    (blend?" ($"+r.product.toFixed(1)+" per kilo of the blended product)":"")+", "+R.toFixed(2)+"&times; everyday meat.</b> "+
    "The tank holds "+r.density.toFixed(0)+" g of cells per litre (limited by "+r.limit.replace("CO2","CO&#8322;")+"). It produces for "+
    (r.uptime*100).toFixed(0)+"% of the year and makes "+r.output.toFixed(1)+" tonnes per m&sup3; a year. The plant costs $"+
    (r.capex/1000).toFixed(2)+" million per m&sup3; of tank"+
    (r.column?", of which the column is $"+r.column.capex_k_m3.toFixed(0)+"k. The column is "+r.column.diameter.toFixed(1)+" m across and passes "+r.column.flow.toFixed(0)+" m&sup3; of culture an hour, "+
      r.column.passes.toFixed(0)+" times the tank's contents"+(r.column.passes_tested?", which is within the range dense cultures have taken":", <b>which is beyond the 15&ndash;24 an hour that dense cultures have taken</b>")+
      ". The alkaline culture in the loop is "+(r.column.ph_vs_safe<=1?"within":"<b>"+r.column.ph_vs_safe.toFixed(1)+" times</b>")+" the exposure judged safe, and "+r.column.ph_vs_paul.toFixed(2)+" of the exposure that slowed CHO cells":"")+
    ". Per kilo: plant capital $"+r.capital.toFixed(1)+", labour $"+
    r.labour.toFixed(1)+", energy and consumables $"+(r.utilities+r.consumables).toFixed(1)+", medium $"+r.feedstock.toFixed(1)+" for "+r.medium_l.toFixed(0)+" litres"+

    (r.medium_floor?" (the nutrients the cells must eat, so the medium cannot cost less)":"")+
    (p.growth_factors>0?", growth factors $"+r.growth_factors.toFixed(1):"")+". "+
    (isFinite(r.osmolality)?"Salt strength in the tank: "+r.osmolality.toFixed(0)+" mOsm/kg"+
      (r.pco2_used<p.pco2-0.5?". The tank runs at "+r.pco2_used.toFixed(0)+" mbar of CO&#8322;, below what the cells tolerate, because more bicarbonate would cost more in medium than it saves in plant":"")+". ":"")+
    "Each kilo of cells uses "+r.o2_kg.toFixed(1)+" mol of oxygen ("+r.o2_kg_upkeep.toFixed(1)+" for upkeep, which grows with the doubling time, and "+
    r.o2_kg_growth.toFixed(1)+" for growth) and gives off "+r.co2_kg.toFixed(1)+" mol of CO&#8322;. "+
    "<b>Long-run share against $"+C.p_conv_anchor.toFixed(0)+" meat (US): about "+(sh*100).toFixed(0)+"%</b>"+
    (blend?", counting the blend as real meat only in proportion to its cells":"")+".";
  g("fx_limits").innerHTML=fxLimitsDraw(r,floorExplore(fxFloorCase()));
  g("fx_tornado").innerHTML=fxTornadoDraw(p,r.total,C.p_conv_anchor*(1-def.retail_margin)-def.markup_add); fxTorCard();
  { let k=0; const parts=Object.keys(C.fx.items).map(it=>{ const c=C.fx.items[it][its[it]][0]*C.fx.escalation; k+=c;
      return C.fx.item_labels[it].toLowerCase()+" $"+c.toFixed(0)+"k"; });
    g("fx_items_sum").innerHTML="These items add up to $"+k.toFixed(0)+"k per m&sup3; of tank in 2025 prices, at 20 m&sup3; tanks: "+parts.join(", ")+"."+
      (its.oxygen==="bought"&&byItems?" Bought oxygen adds $"+C.fx.o2_opex.toFixed(2)+" per kilo of cells.":"")+
      (pl==="microbial"?" The class above is priced at what yeast plants cost when built ($"+C.fx.capex.microbial.toFixed(0)+"k), not at this sum.":""); }
  const n=[];
  if(byItems) n.push("Plant by items. The tanks must still be sealed and steam-sterilised. A cheaper plant pays off only while each tank loses a run less often than about once every "+(1/C.fx.breakeven.lean).toFixed(0)+" days (for the food-grade plant with shared medium) or once every "+(1/C.fx.breakeven.yeastplus).toFixed(0)+" days (for the yeast plant with additions). This compares each plant with a food-grade plant at pharma's loss rate. Cultivated-meat makers report losses that work out to about one every "+(1/C.fx.hazard_cm).toFixed(0)+" days. Nobody has built either plant for animal cells.");
  if(fxCarry) n.push("Loaded from a case. The panel also carries three things it has no lever for: the ammonia the case's cells tolerate ("+fxCarry.nh3_limit+" mmol a litre), glucose worked out from the cells' own balance (until you move the glucose lever), and growth factors inside the medium's price.");
  if(p.mode==="perfusion") n.push("Perfusion at more than 2 m&sup3; needs a device to hold the cells back, and that device does not exist. The model prices it at what one study hopes it will cost.");
  if(p.plant==="microbial") n.push("This is what yeast plants cost, what Humbird's own yeast plant costs with 20 m&sup3; tanks, and about what two published cultivated-meat designs assume. Humbird's design for animal cells costs four to five times more. The extra cost comes from sterile starter cultures, medium handling, oxygen supply and clean rooms. Nobody has run animal cells in the cheaper kind of plant.");
  if(p.doubling_h<20) n.push("Few animal cell lines double in under 20 hours.");
  if(p.vessel_m3>20) n.push("Nobody has grown animal cells at this tank size outside pharma fed-batch.");
  n.push("Losing runs. Large pharma plants lose about "+(C.fx.hazard_pharma*100).toFixed(1)+"% of runs a day to contamination. Cultivated-meat makers report losses that work out to roughly 1&ndash;2% a day. After a contamination, a plant may need two weeks or more to sterilise and regrow its starter cultures.");
  n.push("Oxygen for upkeep. Part of a cell's oxygen use goes on whether or not it grows, and the rest rises with growth. Measurements put the upkeep share between about 31% and 62% at a 24-hour doubling time. Humbird assumes 100% [2].");
  n.push("CO&#8322;. Humbird's limits are 100 mbar, 6 mm/s of gas and a depth 1.6 times the width [2]. With them, a simple balance gives the 120 g/L he reports at 20 m&sup3;. Pharma cells lose about a tenth of their growth at 200 mbar. But 6 mm/s is a rule of thumb, not a measured limit. Large pharma tanks run at 0.1 to 2 mm/s. Nobody has run cells this dense at this size, or any culture at 6 mm/s. A protectant holds off bubble damage, and foam is the likelier cap. The author puts the odds that 6 mm/s works here at about even. The oxygen fed with the gas, nearly all of it vented, adds about $0.5 to each kilo's cost.");
  n.push("What each lever needs. Tank tricks, the oxygen setpoint, fat and glutamine replaced in the feed, and the sorbent need <i>feed or process</i> changes. Cells that tolerate more CO&#8322; or make less lactate need <i>selection or adaptation</i>. The engineered cells (ammonia as low as 0.055 mol/kg) have been shown only with <i>genetic engineering</i>. Selection is easier to regulate than engineering.");
  n.push("Salt. Holding the pH against CO&#8322; takes bicarbonate, and lactate comes with its base. Both add salt, and cells stop growing when the total is too high. So more CO&#8322; leaves less room for lactate, which then needs more medium to wash out.");
  n.push("Waste. 0% is Humbird's efficient cells (about 11 litres of medium per kilo in perfusion), and 100% is ordinary cells (about 190 litres). The 30.5 litres a company reports for chicken is about 10% of the way.");
  if(blend) n.push("Blend. The rest of the product is plant ingredients at $"+C.fx.filler.toFixed(0)+" a kilo.");
  g("fx_notes").innerHTML=n.join(" ");
}
buildRail(); scBuild(); pgInit(); selfTest(); fxInit(); fillParamTable(); fillPriceTable(); fillCurveSel(); fillCmpSel(); fillFootholdSel();
// chart notes carry their longer "how to read" text in data-help, shown by the same "?" badge as the settings
document.querySelectorAll("[data-help]").forEach(h=>addQ(h,h.getAttribute("data-help")));
function setFootView(v){state.footView=v;
  document.getElementById("footWL").classList.toggle("on",v!=="margin");
  document.getElementById("footMV").classList.toggle("on",v==="margin");
  drawFoothold(state);}
document.getElementById("footWL").onclick=()=>setFootView("waterline");
document.getElementById("footMV").onclick=()=>setFootView("margin");
if(PGS.anchor) pgOpenFor(document.getElementById(PGS.anchor));
recompute();
if(PGS.anchor) pgGoto(PGS.anchor);
</script></body></html>"""


def main() -> None:
    model = build_model()
    crosscheck(model)
    import datetime as _dt
    html = PAGE_HTML + JS_ENGINE                         # page markup + the JS engine (two strings, one file)
    html = html.replace("__MODEL_JSON__", json.dumps(model))
    html = html.replace("/*__SC_JS__*/", open(os.path.join(HERE, "page_scenarios.js"), encoding="utf-8").read())
    html = html.replace("/*__VM_JS__*/", open(os.path.join(HERE, "page_vessels.js"), encoding="utf-8").read())
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
