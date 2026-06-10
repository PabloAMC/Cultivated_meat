#!/usr/bin/env python3
"""
inputs.py — the ONE place every concrete number in the model lives, with its
source and (where it is uncertain) its Monte-Carlo range.

Why this file exists
--------------------
The model's whole credibility rests on every number being honest and sourced.
Before this file, a number like the medium price lived as a point default in
cost_model (`media_price = 0.63`) AND as an independent prior in uncertainty.py
(`("triangular", 0.20, 0.63, 0.40, ...)`) — two unconnected facts that could
silently drift apart. Here each input is a SINGLE record carrying both facets:

    Input(value=0.63, unit="$/L", source="Pasitka empirical ACF medium",
          lo=0.20, hi=0.63, mode=0.40, note="albumin removal cut $3.26->0.63")

  * `value`            -> the point/base-case default the dataclasses use.
  * `lo, mode, hi`     -> the triangular Monte-Carlo prior uncertainty.py samples.
  * `unit, source, note` -> provenance, so the datasheet is self-documenting.

So the point estimate and the uncertainty band can never diverge: change the
number here and every rung follows.

Reference it
------------
    python inputs.py            # prints the full datasheet (every number + source)

    from inputs import value, prior, REGISTRY
    value("media_price")        # -> 0.63
    prior("media_price")        # -> ("triangular", 0.20, 0.63, 0.40, "<note>")

Every number here is real and sourced. The model has no placeholder mechanism
that a later rung substitutes, so there are no "fake" values to keep out — the
price_ratio module takes a cost as input rather than inventing a cost curve.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Input:
    """One concrete model input: its base value, optional MC prior, and source."""
    value: float                  # point / base-case default
    unit: str
    source: str                   # short provenance tag
    lo: float | None = None       # MC prior low  (None -> not sampled / fixed)
    hi: float | None = None       # MC prior high
    mode: float | None = None     # MC prior mode (defaults to `value` if omitted)
    kind: str = "triangular"      # MC prior distribution
    note: str = ""                # one-line justification / caveat

    @property
    def has_prior(self) -> bool:
        return self.lo is not None and self.hi is not None

    @property
    def prior_mode(self) -> float:
        return self.value if self.mode is None else self.mode


# ----------------------------------------------------------------------------
# THE REGISTRY  (grouped by where in the ladder the number is used)
# Tags: [Pasitka] empirical TEA (Nature Food 5, 693-702, 2024) · [Humbird] TEA
#       (Biotechnol. Bioeng. 118, 3239-3250, 2021) · [GFI] GFI 2025 State-of-the-
#       Industry / medium-cost analysis (company self-reports) · [Gu25-qual] Gu et al.
#       2025 scaffolds review (Compr. Rev. Food Sci. Food Saf. 24, e70221) — materials
#       only, NO cost figure · [market] observed retail price · [scanner] meat/plant-
#       based own-price elasticity (Andreyeva 2010; Gallet 2010/2012) · [assumed] our
#       judgement · [calibration] fixes a model coefficient
#
# Sourcing discipline: the cost stack is anchored to Pasitka throughout. The
# scale-up risk is expressed INSIDE Pasitka's own three reactor configurations
# (see `overhead` below), not via Humbird's $37/$51 — Humbird supplies only the
# physical amino-acid feedstock floor and the *rationale* for why scale-up is
# hard (CO2/O2 transfer, sterility), never a load-bearing cost ceiling.
# ----------------------------------------------------------------------------
REGISTRY: dict[str, Input] = {

    # --- shared across rungs ------------------------------------------------
    "markup_add": Input(5.0, "$/kg", "[assumed] additive biomass->retail spread, roughly "
        "fixed $/kg (does NOT shrink as biomass falls). Anchored to conventional meat's "
        "farm-to-retail margin: USDA price-spread data put ground-beef processing+retail at "
        "very roughly $3-6/kg.",
        lo=2.0, hi=7.0, mode=5.0,
        note="PIVOTAL: with p_conv this sets the parity threshold (p_conv - markup_add). The lower "
             "bound is $2 (not the conventional ~$4) because cultivated SKIPS slaughter / evisceration "
             "/ carcass breakdown — a real chunk of conventional's farm-to-retail wedge — so its retail "
             "markup can sit slightly BELOW conventional's; mode stays $5 (typical), $7 = markup-heavy. "
             "The most leverage of any single number; at the $2 floor parity becomes reachable in the "
             "optimistic cost corner."),
    "p_conv": Input(12.0, "$/kg", "[market] conventional commodity meat price (~$10-15/kg)",
        lo=10.0, hi=14.0, mode=12.0,
        note="PIVOTAL: co-sets the parity threshold with markup_add (a meat tax enters here)."),
    "years": Input(30, "years", "[assumed] analysis horizon"),

    # --- Rung 2: cost model (Pasitka-anchored) ------------------------------
    "media_intensity": Input(22.4, "L/kg wet", "[Pasitka] 50,000 L facility: 24e6 L ACF "
        "-> 1.07e6 kg/yr wet biomass = 24e6/1.07e6", note="fixed; not a major uncertainty"),
    "media_price": Input(0.63, "$/L", "[Pasitka] empirical animal-free (ACF) medium, $0.63/L "
        "(peer-reviewed; albumin removal cut it from $3.31->$0.63/L)",
        lo=0.20, hi=0.63, mode=0.63,
        note="CENTERED ON THE MEASURED VALUE (mode=0.63): the prior is one-sided improvement, so "
             "cheaper medium is UPSIDE, never assumed. lo=0.20 is a COMPANY SELF-REPORT, not "
             "measured: [GFI26] reports 'several companies announced media costs at $0.20/L or below "
             "in 2025' (p.8), with the amino-acid input portion independently validated by GFI/MG "
             "Consulting (p.30) but the full media cost unverified; Pasitka itself calls <$0.50/L "
             "'theoretically possible' but needing 'major efforts to empirically demonstrate'. So "
             "0.63 is the demonstrated centre and 0.20 the optimistic tail."),
    "efficiency": Input(1.0, "x media-use", "[Pasitka] cells (1.0); ~4x more media than CHO",
        lo=0.25, hi=1.00, mode=1.00,
        note="media-VOLUME multiplier; CENTERED ON THE MEASURED Pasitka cells (mode=1.0). "
             "0.25 = CHO-grade is the OPTIMISTIC tail (a different cell line, not demonstrated for "
             "these cells), so better efficiency is upside, never assumed."),
    "overhead": Input(9.9, "$/kg", "[Pasitka] non-media cost (capital+consumables+labour+"
        "utilities) at the 50,000 L facility, TFF config",
        lo=6.0, hi=15.0, mode=9.9,
        note="THE SCALE-UP knob, expressed inside Pasitka's OWN reactor configs (Fig. 4, total "
             "COGS $/kg = media ~$14 + this overhead). The central band is CENTERED on the "
             "demonstrated, scalable case so the median is neutral, not pessimistic: "
             "mode=9.9 = TFF 5 m^3 (10x5,000 L; total $24/kg) = Pasitka's demonstrated-scalable "
             "base; lo=6.0 = large-scale perfusion 20 m^3 / irreducible plant floor (total ~$22/kg; "
             "scale-up WINS, the optimistic tail); hi=15.0 = scale-up proves HARDER than the clean "
             "projection (a partial shortfall). The FULL scale-up-STALL case — ATF 0.5 m^3 small "
             "vessels, overhead ~$24.7/kg, total ~$38.8/kg (see PASITKA_CONFIGS) — is shown as an "
             "explicit DOWNSIDE SCENARIO (cost_model scenario table + the waterfall), NOT folded "
             "into the central band, since a commercial plant would only fall back to many small "
             "vessels if larger reactors fail (Humbird's CO2/sterility caps). PIVOTAL: the top R "
             "lever AND the largest downside, but the central estimate stays Pasitka-faithful."),

    # --- Rung 2: the irreducible FLOOR --------------------------------------
    "aa_intensity": Input(0.26, "kg AA/kg wet", "[Humbird] Table 3.4 stoichiometry (~0.85 "
        "kg/kg dry)", note="stoichiometric -> does NOT scale with media efficiency"),
    "aa_bulk_price": Input(2.0, "$/kg", "[Humbird] bulk plant hydrolysate (cuts $15-16/kg)"),
    "glucose_other_floor": Input(1.0, "$/kg", "[assumed] irreducible non-AA bulk nutrients"),
    "plant_floor": Input(6.0, "$/kg", "[Pasitka] large-scale perfusion config: nutrients "
        "~66-70% of COGS, so non-nutrient remainder ~30-34% ~= $6/kg",
        note="least-constrained floor term; dominates the floor's width"),
    "eff_best": Input(0.25, "x media-use", "[assumed] CHO-grade media-volume multiplier "
        "(~4x less media than Pasitka's cells)", note="drives the CHO-grade SCENARIO, not the floor"),
    "cleanroom_cost": Input(3.0, "$/kg", "[Humbird] clean-room / aseptic buildings cost burden "
        "(Table 4.7 $3.08/kg fed-batch, Table 4.14 $4.11/kg perfusion; ~8% of his COGS)",
        note="OPTIONAL adder, OFF by default: Pasitka's overhead already reflects a food-grade "
             "facility. Toggle adds Humbird's pharma-leaning clean-room burden. p.53: halving it "
             "(sanitary) or removing it (outdoor) still leaves his COP above target."),

    # --- Rung 3: demand / WILLINGNESS-TO-PAY reservation-price curve ----------
    # Cultivated's share at price ratio R is the SURVIVAL fraction of a logistic
    # distribution of consumers' log reservation ratio w = ln(WTP/p_conv):
    #   share_x(R) = (1 - pb_floor_share) / (1 + exp((ln R - mu)/sigma + parity(R)))
    # sigma = (1-s_calib)/|eps_own| is the dispersion (<- elasticity); mu is the
    # location (<- the standing dials); parity(R) is the curve's SHAPE near R=1.
    # A binary log-price logit is exactly this logistic-in-ln(R) — the reframe just
    # makes the WTP curve explicit (no nest, no second segment). See market_share.py.
    "eps_own": Input(-0.9, "elasticity", "[scanner] own-price elasticity of meat demand. "
        "Andreyeva, Long & Brownell 2010 (AJPH 100:216) meta-analysis: beef -0.75, pork -0.72, "
        "poultry -0.68; Gallet 2010/2012 meta-analysis: -0.7..-1.0 by species/region; plant-based "
        "scanner data sits in the same -0.5..-1.4 envelope. -0.9 is the mid-range central.",
        lo=-1.4, hi=-0.5, mode=-0.9,
        note="Sets the DISPERSION of the WTP curve, sigma=(1-s_calib)/|eps_own| (more elastic = "
             "tighter reservation-price spread = sharper response). Premium tiers are made LESS "
             "elastic in meat_market (cuts x0.8, luxury x0.5): premium buyers are less price-sensitive "
             "(Lusk & Tonsor 2016: demand more inelastic at high price)."),
    "s_calib": Input(0.05, "share", "[calibration] share at which the own-price elasticity is "
        "anchored. With the LOG-PRICE (WTP) curve the elasticity is beta*(1-s), independent of the "
        "price level, so NO price anchor is needed; it sets the dispersion "
        "sigma = (1-s_calib)/(|eps_own|*cult_sub_mult)."),
    "cult_sub_mult": Input(3.0, "x", "[assumed] SUBSTITUTABILITY / closeness parameter: how much MORE "
        "own-price-elastic cultivated is than meat-as-a-category, because conventional is a near-perfect "
        "substitute for it (same tissue). The measured -0.9 is the elasticity of MEAT (no close "
        "substitute, hence inelastic); cultivated's own price bites harder because buyers switch to "
        "conventional.",
        lo=2.0, hi=4.0, mode=3.0,
        note="THE model's least data-disciplined lever (no cultivated cross-price data exists; PB "
             "cross-price elasticities are ~0/contested, but cultivated is closer). It is the FLAT-MNL "
             "counterpart of the retired nest's lambda (lam_meat=0.5 => ~2x) and a reduced-form stand-in "
             "for a random coefficient on real_tissue (correlated taste for conventional & cultivated). "
             "Held fixed at 3 centrally; its leverage is shown explicitly in market_share self-check [6] "
             "(setting it to 1 -- 'as inelastic as meat overall' -- lifts central penetration ~6x)."),
    "loss_aversion": Input(1.0, "utils", "[behavioural] REFERENCE-DEPENDENT loss aversion "
        "(Tversky-Kahneman; Hardie, Johnson & Fader 1993): consumers anchor on the conventional price. "
        "The term is TWO-SIDED around that reference — a product priced ABOVE it is penalised, one priced "
        "BELOW it is rewarded — but STEEPER on the loss side by the canonical 2.25x ratio (losses loom "
        "~2.25x larger than gains): V_loss_j = -loss_aversion*max(0, price_ratio_j - 1) "
        "+ (loss_aversion/2.25)*max(0, 1 - price_ratio_j). Applied UNIFORMLY to every product (plant-based "
        "at 1.77x and cultivated at R), not a cultivated-only cliff.",
        lo=0.0, hi=2.5, mode=1.0,
        note="replaces the old cultivated-only parity_penalty, putting all options on the same "
             "functional form. 0 = pure smooth logit; higher = stronger reference dependence. The 2.25 "
             "loss/gain asymmetry is the Tversky-Kahneman (1992) median, not a free parameter. Judgement."),
    "parity_penalty": Input(1.0, "utils", "[assumed] LEGACY cultivated-only parity cliff — used ONLY by "
        "the interactive JS (build_interactive.py / build_html.py). The Python model uses the symmetric "
        "loss_aversion term instead.",
        note="superseded by loss_aversion; kept so the (stale) interactive HTML still imports."),
    "parity_width": Input(0.13, "R-units", "[market] conventional PRICE SPREAD (coefficient of "
        "variation) — sets how gradually the parity-shape term turns on. 'Conventional meat' is not "
        "one price but a range (~+/-13% across brands/cuts/stores), so for a fixed cultivated cost the "
        "share of conventional it undercuts is GRADED, not a step. That dispersion IS the softness.",
        lo=0.02, hi=0.25, mode=0.13,
        note="parity(R) = parity_penalty * (1 - exp(-(max(0,R-1)/spread)^2)); 0 at parity, ~full by "
             "R~1+2*spread. Tied to a measured price CV, not an arbitrary constant."),

    # --- the WTP LOCATION dials (cultivated's standing vs conventional) -------
    #     The standing of cultivated is TWO interpretable dials that shift the WTP
    #     location mu (NO baked-in stance; the reader sets them). taste-acceptance
    #     accept_x is the FRICTION half; slaughter-free value theta_free_M is the
    #     UPSIDE half. mu = sigma*(wtp_taste_scale*(accept_x-1) + theta_free_M + tier).
    "wtp_taste_scale": Input(5.0, "utils", "[calibration] scale converting the taste-acceptance "
        "deficit (1-accept_x) into a shift of the WTP-ratio location mu. Large -> the flavour-first "
        "majority is very reluctant to buy what it does not credit as real meat (this absorbs the old "
        "plant-based 'not-real-meat' stigma magnitude)."),
    "theta_free_M": Input(0.0, "utils", "[NEUTRAL DIAL] MAINSTREAM utility weight on the slaughter-free "
        "attribute — THE headline UPSIDE dial. In the rebuilt MNL it is w_slaughter[M], applied to "
        "EVERY slaughter-free product (cultivated, plant-based, whole-food). 0 = mainstream indifferent "
        "to no-slaughter (cultivated ties conventional at parity); positive = mainstream values cleaner "
        "/ no-slaughter, so cultivated (and, more weakly, plant-based) gain.",
        lo=0.0, hi=1.0, mode=0.0,
        note="The ethical UPSIDE half of cultivated's standing. ~89% of real PB-meat buyers are "
             "non-veg/vegan (GFI 2024) — that flexitarian pull lives HERE (mainstream), not in the 5% "
             "ethical core (w_eth). MC prior 0..1: neutral to 'values no-slaughter'."),
    "accept_x": Input(1.0, "fraction", "[DIAL] how fully the mainstream credits cultivated's taste / "
        "real-meat attribute. In the rebuilt MNL it sets cultivated's taste_quality = (accept_x - 1), "
        "weighted by q_taste utils. 1 = tastes as real as conventional (neutral); <1 = a taste deficit.",
        lo=0.6, hi=1.0, mode=1.0,
        note="The taste-FRICTION half of cultivated's standing. In the MNL the utility offset is "
             "q_taste*(accept_x-1) utils (replaces the old wtp_taste_scale*(accept_x-1) WTP-shift)."),
    "pb_floor_share": Input(0.015, "share", "[GFI] mature plant-based meat share (~1.3% US, declining "
        "since its ~2020-21 peak)",
        lo=0.010, hi=0.025, mode=0.015,
        note="LEGACY: used only by the binary WTP curve in build_interactive.py / build_html.py. The "
             "rebuilt MNL replaces this static floor with pb_share_target (a calibration CHECK that "
             "K_wholefood is solved to hit), so plant-based is now a competing product, not a constant."),

    # === Rung 3, REBUILT: two-segment, FOUR-product latent-class MNL ==========
    # Demand is an explicit discrete choice over FOUR products by TWO segments:
    #   products  c = conventional meat, p = plant-based meat, x = cultivated,
    #             w = whole-food / non-meat outside option (beans/tofu/lentils)
    #   segments  M = mainstream (taste/price-driven), E = ethical (slaughter-free)
    # Each product carries {price, taste_quality, slaughter_free, real_tissue};
    # each segment weights those attributes differently. Total share_j =
    # w_eth*P_E(j) + (1-w_eth)*P_M(j). NO nested logit: cultivated cannibalises
    # CONVENTIONAL (not the veggie burger) because the shared real_tissue attribute
    # makes conventional dominate the large mainstream segment. See market_share.py.
    "price_calib": Input(18.0, "$/kg", "[calibration] price at which the own-price elasticity is "
        "anchored; sets beta_price = eps_own*cult_sub_mult/(price_calib*(1-s_calib))"),
    "price_pb_mult": Input(1.77, "x p_conv", "[GFI] plant-based meat retail PRICE premium vs "
        "conventional: GFI/NIQ 2024 put PB meat at +77% per lb (up from +65% in 2022); the gap WIDENED, "
        "and 2025 narrowing is an artifact of beef inflation, not PB cost-down",
        lo=1.5, hi=2.2, mode=1.77,
        note="PB meat is a genuine, persistent price PREMIUM — a load-bearing reason its share is small."),
    "price_wf_mult": Input(0.25, "x p_conv", "[BLS] whole-food plant protein staple (dried beans/lentils) "
        "$/kg vs commodity meat: US dried beans $3.40/kg (BLS Aug 2025), representative $2-3.5/kg, vs "
        "~$12/kg meat -> ~0.25x. Beans are also ~3-5x cheaper per kg of PROTEIN than beef (VRG 2024).",
        note="the outside option is CHEAP; with taste_quality_w and K_wholefood it absorbs most ethical "
             "demand -> PB stays ~1%."),
    "taste_quality_w": Input(-0.7, "norm", "[assumed] whole-food (beans/tofu/lentils) taste/utility AS A "
        "MEAT SUBSTITUTE: nutritious and cheap, but quite far from a meat-eating experience. Normalised "
        "like (accept_x-1): 0 = as satisfying as real meat, negative = a worse stand-in for meat (-0.7 ≈ "
        "a_w 0.3 on the 1=real-meat scale)",
        lo=-1.0, hi=-0.3, mode=-0.7,
        note="NOT load-bearing: the whole-food ASC K_wholefood is SOLVED to hit the meatless / PB-share "
             "targets, so it absorbs whatever this taste does not — lowering taste_quality_w just raises "
             "the solved ASC, leaving cultivated and plant-based shares unchanged. Set to a plausible "
             "'beans aren't a burger' value; the split between taste and the solved ASC is not identified."),

    # --- Rung 3: income-dependent price sensitivity (BLP log form) -----------
    # Price enters utility as alpha*ln(income_eff - price) (Berry-Levinsohn-Pakes 1995):
    # richer consumers are LESS price-sensitive. alpha is derived in market_share from
    # beta_price so the US-reference behaviour is unchanged; income_eff = income_ref *
    # (income/income_ref)**income_gradient damps the cross-region gradient. See market_share.py.
    "income_ref": Input(85810, "$/yr", "[World Bank] US GDP per capita PPP 2023 ($85,810) — the "
        "REFERENCE income at which the price coefficient is anchored (so the US/commodity case is "
        "unchanged). Only income RATIOS across regions matter, so the absolute level is absorbed by alpha."),
    "income_gradient": Input(0.5, "exponent", "[Muhammad/ERS] phi: how strongly price-sensitivity scales "
        "with income. Effective income = income_ref*(income/income_ref)**phi, so the own-price elasticity "
        "ratio across regions = (income_ref/income)**phi.",
        lo=0.0, hi=1.0, mode=0.5,
        note="phi=1 = literal BLP / pure 1-over-income (cultivated ~13x more price-elastic in Nigeria than "
             "the US — too steep). phi=0.5 (DEFAULT) gives China ~1.8x, India ~2.8x, Nigeria ~3.6x, "
             "matching the empirical food-price-elasticity gradient (poor countries ~2-3x more responsive "
             "for meat; Muhammad et al. 2011 USDA ERS, food income-elasticity 0.78 low- vs 0.50 high-income). "
             "phi=0 = no income effect. A documented judgement dial."),
    "taste_quality_p": Input(-0.2, "norm", "[Nectar] plant-based meat AVERAGE blind-taste deficit vs "
        "real meat. Nectar 'Taste of the Industry' 2025: only ~16% (20/122) of PB SKUs reach blind "
        "sensory parity, so the category average is BELOW parity. Normalised like (accept_x-1): "
        "0 = parity, negative = deficit",
        lo=-0.4, hi=0.0, mode=-0.2,
        note="taste is the binding constraint on PB meat (Nectar); the best ~16% reach parity, the "
             "average lags -> a modest negative, weighted by q_taste in utils."),
    "q_taste": Input(5.0, "utils", "[calibration] taste-utility weight: converts a normalised taste "
        "gap (0=parity, -1=very poor) into utils. Large => the flavour-first mainstream punishes a "
        "taste deficit heavily. Absorbs the old wtp_taste_scale."),
    "w_eth": Input(0.05, "fraction", "[Gallup] ethics-driven CORE = vegetarian (4%) + vegan (1%), "
        "Gallup 2023",
        lo=0.04, hi=0.10, mode=0.05,
        note="5% is the ethics core and is KEPT. Plant-based lands at ~1% (not ~5%) because the cheap "
             "whole-food outside option (K_wholefood) absorbs most ethical eaters — NOT because the "
             "segment is smaller. The flexitarian PB buyer base (~89% of buyers, GFI 2024) lives in the "
             "MAINSTREAM via theta_free_M, not here."),
    "w_realtissue_M": Input(2.0, "utils", "[calibration, SOLVED] MAINSTREAM utility weight on REAL TISSUE "
        "(=1 conventional & cultivated, =0 plant-based & whole-food). SOLVED at runtime so the mainstream "
        "carries pb_mainstream_frac (~89%) of plant-based buyers (GFI/Morning Consult 2024). The stored "
        "value is a seed.",
        note="A REDUCED-FORM bundle: the mainstream non-price standing of non-real-meat products (genuine "
             "'I want real meat' preference + processed/habit residual). Cross-sectionally it is NOT "
             "separately identifiable from habit (we only observe plant-based, which lacks both), so we do "
             "not split it (Heckman state-dependence-vs-heterogeneity). HABIT proper lives in the diffusion "
             "rung (adoption_timing) + the long-run standing dial xi_x_floor_M. real_tissue is the "
             "IDENTIFYING ASSUMPTION that cultivated, being real tissue, ESCAPES this penalty (inherits "
             "conventional's standing) — the load-bearing premise, giving conventional > cultivated > "
             "plant-based at parity as a structural PREDICTION, not a fitted result."),
    "pb_mainstream_frac": Input(0.89, "fraction", "[GFI] share of plant-based-meat BUYERS who are NOT "
        "vegetarian/vegan (mainstream flexitarians/omnivores): GFI/Morning Consult 2024 (~89%: 57% "
        "omnivore + 15% flexitarian + ~17% other; only ~11% veg/vegan)",
        lo=0.82, hi=0.93, mode=0.89,
        note="pins w_realtissue_M: PB's ~1.2% must be carried mostly by the MAINSTREAM (flexitarians), not "
             "the 5% ethical core. Solved jointly with the segment-specific whole-food intercepts."),
    "wf_mainstream_target": Input(0.06, "share", "[assumed, SOFT] mainstream 'meatless-by-choice' share: "
        "the fraction of mainstream meat-occasions where a whole-food plant protein is chosen over meat",
        lo=0.04, hi=0.14, mode=0.06,
        note="pins K_wholefood_M (the mainstream whole-food intercept) so the cheap outside option does not "
             "spill unrealistically into the mainstream. SOFT (no clean source); mostly moves the whole-food "
             "line, NOT the cultivated headline (self-check [6]: <=0.2pp). Lowered 0.10->0.06 so total "
             "whole-food (~ethical core 5pp + this) sits ~10%, not ~14%; the irreducible part is the ethical "
             "segment eating beans (w_eth * ~96% ~= 5pp), which IS the model's premise, not a free knob."),
    "K_wholefood_M": Input(-3.0, "utils", "[calibration, SOLVED] mainstream whole-food (beans/tofu) "
        "outside-option intercept — SOLVED so mainstream whole-food == wf_mainstream_target. Seed only.",
        note="SEGMENT-SPECIFIC (vs K_wholefood for the ethical segment): mainstream meat-eaters rarely "
             "substitute beans for a meat occasion, so this intercept is much weaker than the ethical one. "
             "Splitting the outside option by segment is what lets w_realtissue_M be pinned to the buyer "
             "split without the cheap bean option leaking into the mainstream."),
    "w_realtissue_E": Input(0.0, "utils", "[assumed] ethical-segment weight on real tissue ~ 0: ethical "
        "eaters choose on slaughter-free, not on 'real meat'"),
    "w_slaughter_E": Input(4.0, "utils", "[assumed] ETHICAL-segment utility weight on the SLAUGHTER-FREE "
        "attribute (=1 for p, x, w; =0 for conventional). Large => segment E strongly avoids conventional "
        "and is drawn to no-slaughter options; this is what lets cultivated win an early beachhead at R>1"),
    "pb_share_target": Input(0.012, "share", "[GFI] plant-based meat's mature share of TOTAL meat "
        "(~0.8% of all meat by $, ~1.7% of packaged, <1% by volume; ~13% household penetration; declining "
        "since the ~2020-21 peak), SPINS/Circana via GFI 2024",
        lo=0.008, hi=0.017, mode=0.012,
        note="the calibration ANCHOR: K_wholefood is solved at runtime so the model reproduces this with "
             "cultivated absent (market_share.solve_wholefood). Replaces the old static pb_floor_share."),
    "K_wholefood": Input(0.0, "utils", "[calibration, SOLVED] ETHICAL-segment whole-food outside-option "
        "intercept (utils) — SOLVED so the ethical-segment plant-based rate hits its target (the residual "
        "~11% of PB buyers / the non-mainstream part of pb_share_target). The stored value is a seed.",
        note="this, not a smaller w_eth, is why a 5% ethical core yields only ~0.1pp of PB: the cheap "
             "whole-food outside option (beans/tofu) absorbs most ethical eaters. Diffusion ruled out (PB "
             "is mature/declining). Mainstream uses the separate, weaker K_wholefood_M."),
    "xi_x_E": Input(-1.0, "utils", "[assumed] cultivated standing at LAUNCH in the ethical segment (less "
        "wary than mainstream — no-slaughter is a positive here); fades toward xi_x_floor_E"),
    "xi_x_floor_E": Input(0.0, "utils", "[assumed] cultivated's long-run ethical-segment standing (fades "
        "from xi_x_E toward ~0)"),

    # cultivated STANDING at LAUNCH. Conventional is the REFERENCE (mu measures
    # cultivated's standing vs it; no permanent "incumbency" term). The launch
    # wariness fades over time toward the long-run dial xi_x_floor_M (Rung 4).
    "xi_x_M": Input(-2.0, "utils", "[assumed] cultivated standing vs conventional at LAUNCH in the "
        "mainstream (wary/novel); a mu-offset (utils) that fades over time toward xi_x_floor_M"),

    # --- Rung 4: timing -----------------------------------------------------
    "p_innov": Input(0.02, "1/yr", "[literature] Bass innovation coeff.; near the cross-study "
        "norm (~0.03 avg in Bass-model meta-analyses) — independent adopters"),
    "q_imit": Input(0.40, "1/yr", "[literature] Bass imitation coeff.; near the cross-study "
        "norm (~0.38 avg) — word-of-mouth/contagion"),
    "xi_x_floor_M": Input(0.0, "utils", "[NEUTRAL DIAL] cultivated's LONG-RUN standing vs conventional "
        "at price+taste parity — THE headline scenario axis; a mu-offset (utils)",
        lo=-2.0, hi=1.0, mode=0.0,
        note="The single number that decides the ~1%-to-tens-of-percent question at parity. NEUTRAL "
             "default = 0 (cultivated treated as EQUIVALENT to conventional -> ~49% at parity, "
             "splitting the contestable meat pool by habit/brand only). Dial NEGATIVE for friction: "
             "-0.5 modest, -1.5 strong (~the Peacock/PTC-skeptic view: even at parity a real-world "
             "plant-based product displaced only ~3-4pp of beef). Dial POSITIVE if cultivated is "
             "actively preferred (cleaner/no-slaughter/safety). We take NO baked-in stance."),
    "accept_rate": Input(0.15, "1/exposure", "[assumed] how fast the launch novelty penalty fades per "
        "unit cumulative AVAILABILITY (rollout F, not the small consumed share)",
        note="UNGROUNDED: sets WHEN, not the long-run ceiling. ~0.15 gives ~90% acceptance over the "
             "30-yr horizon. (Driving it by consumed share would never ignite once shares are ~1%.)"),
    "milestone_year_breakthrough": Input(10, "year", "[assumed] year a scale-up / cheaper-media "
        "breakthrough lands, stepping R down (Rung 4 cost-path coupling)",
        lo=5, hi=20, mode=10,
        note="The WHEN of the cost step (the declared unknown), not the whether. The R endpoints of "
             "each cost path are DERIVED from the cost model (adoption_timing.COST_PATHS), not "
             "hand-typed here, so they cannot drift from Rung 2."),

    # --- Rung 6: scaffold / structured product (most speculative) -----------
    "biomass_cost_nearterm": Input(14.0, "$/kg", "[Pasitka-derived] near-term achievable biomass "
        "(media $0.2/L + current cells)"),
    "scaffold_frac": Input(0.2, "kg/kg", "[Gu25-qual/assumed] scaffold material per kg product "
        "(minority mass); Gu et al. 2025 gives the materials picture but no mass fraction",
        lo=0.1, hi=0.3, mode=0.2),
    "material_price": Input(8.0, "$/kg", "[Gu25-qual/assumed] synthetic PLA/PCL <$10/kg, plant "
        "cheaper, gels higher (Gu et al. 2025 ranking, no $/kg); Gelatex vendor claim ~<$1/kg of meat",
        lo=2.0, hi=20.0, mode=8.0),
    "process_cost": Input(5.0, "$/kg", "[UNGROUNDED] seed+maturation+removal bioprocess; no TEA",
        lo=1.0, hi=15.0, mode=5.0,
        note="widest, most speculative input; dominates the structured-product spread"),

    # --- premium comparators (Rung 5 targets / Rung 6) ----------------------
    "p_conv_premium_fish": Input(25.0, "$/kg", "[market] premium fish / BlueNalu target",
        lo=20.0, hi=30.0, mode=25.0),
    "p_conv_sushi_salmon": Input(40.0, "$/kg", "[market] sushi-grade salmon / Wildtype target",
        lo=32.0, hi=48.0, mode=40.0),
}


# ----------------------------------------------------------------------------
# Derived constants (computed from the registry — never hand-typed twice)
# ----------------------------------------------------------------------------
# Irreducible amino-acid feedstock cost: media cost can never fall below this.
AA_FLOOR: float = REGISTRY["aa_intensity"].value * REGISTRY["aa_bulk_price"].value  # 0.26*2 = 0.52

# Contestable real-meat pool: cultivated's max share as R->0 with neutral standing.
# = 1 - pb_floor_share, so the model reproduces ~49% at parity-neutral and the
# plant-based floor is the only structurally-lost share (this single ceiling
# replaces the old nest + ethical segment + whole-food outside option).
ADDRESSABLE_CEILING: float = 1.0 - REGISTRY["pb_floor_share"].value  # 1 - 0.015 = 0.985

# Pasitka's three MODELED reactor configurations (Nature Food 2024, Fig. 4), as
# (label -> non-media overhead $/kg). Media cost (~$14/kg at $0.63/L) is ~constant
# across them; total wet-biomass COGS = media + overhead, reproducing Pasitka's
# $38.8 / $24 / $22 per kg. These are the endpoints of the SCALE-UP axis that the
# `overhead` prior samples — the model's single most important cost bottleneck.
PASITKA_CONFIGS: dict[str, float] = {
    "ATF 0.5 m^3 (small vessels; scale-up STALLS)": 24.7,   # total ~$38.8/kg
    "TFF 5 m^3 (10x5,000 L; current base)":          9.9,   # total ~$24/kg
    "perfusion 20 m^3 (2x25,000 L; scale-up WINS)":  7.9,   # total ~$22/kg
}


# ----------------------------------------------------------------------------
# Accessors
# ----------------------------------------------------------------------------
def value(name: str) -> float:
    """The point / base-case value of an input (used as dataclass defaults)."""
    return REGISTRY[name].value


def prior(name: str) -> tuple:
    """The Monte-Carlo prior as (kind, lo, hi, mode, note). Raises if the input
    has no prior (i.e. it is treated as fixed)."""
    inp = REGISTRY[name]
    if not inp.has_prior:
        raise KeyError(f"input '{name}' has no MC prior (it is fixed at {inp.value})")
    return (inp.kind, inp.lo, inp.hi, inp.prior_mode, inp.source if not inp.note else inp.note)


# ----------------------------------------------------------------------------
# Datasheet  (python inputs.py)
# ----------------------------------------------------------------------------
def datasheet() -> str:
    lines = ["Cultivated-meat model — input datasheet", "=" * 78]
    hdr = f"{'input':<22}{'value':>8}  {'unit':<13}{'MC range (lo..hi)':<18}source"
    lines += [hdr, "-" * 78]
    for name, inp in REGISTRY.items():
        rng = f"{inp.lo:g}..{inp.hi:g}" if inp.has_prior else "(fixed)"
        src = inp.source if not inp.note else f"{inp.source}  [{inp.note}]"
        lines.append(f"{name:<22}{inp.value:>8g}  {inp.unit:<13}{rng:<18}{src}")
    lines += ["-" * 78,
              f"derived  AA_FLOOR = aa_intensity x aa_bulk_price = {AA_FLOOR:g} $/kg",
              f"derived  ADDRESSABLE_CEILING = 1 - pb_floor_share = {ADDRESSABLE_CEILING:g} share"]
    return "\n".join(lines)


if __name__ == "__main__":
    print(datasheet())
