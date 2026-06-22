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
        lo=0.20, hi=1.00, mode=0.63,
        note="CENTERED ON THE MEASURED VALUE (mode=0.63), now TWO-SIDED: $0.63 is the demonstrated "
             "central case, with both a cheaper tail and a dearer tail. lo=0.20 is the optimistic "
             "tail, a COMPANY SELF-REPORT, not measured: [GFI26] reports 'several companies announced "
             "media costs at $0.20/L or below in 2025' (p.8), amino-acid portion independently "
             "validated by GFI/MG Consulting (p.30) but full media cost unverified; Pasitka itself "
             "calls <$0.50/L 'theoretically possible' but needing 'major efforts to empirically "
             "demonstrate'. hi=1.00 is the PESSIMISTIC tail (ADDED 2026-06): media DEARER than "
             "Pasitka's demonstrated value — plausible for cell lines/processes that haven't achieved "
             "the albumin removal or the volume discounts Pasitka did (Pasitka itself was at $3.31/L "
             "before that optimisation). Making the prior two-sided removes the old asymmetry where "
             "only cheaper media could enter the band; it widens (and slightly lowers) the headline "
             "penetration band on the downside."),
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

    # --- Rung 3: demand / price-sensitivity inputs ----------------------------
    # Rung 3 is a two-segment, four-product latent-class logit (market_share.py), NOT a
    # willingness-to-pay reservation curve. Price enters via the BLP income term
    # alpha*ln(income-price); the shared price coefficient beta is DERIVED, not set here:
    # the behavioural primitive is cultivated's own-price elasticity
    # eps_x = eps_own*cult_sub_mult, and beta is solved so the logit reproduces it at
    # cultivated's OWN modeled retail price (= biomass_cost + markup_add) and share, with
    # no hand-chosen anchor (see market_share._derive_beta). The two inputs below are the
    # factors of that target; beta tracks them and the cost model automatically.
    "eps_own": Input(-0.9, "elasticity", "[scanner] own-price elasticity of meat demand. "
        "Andreyeva, Long & Brownell 2010 (AJPH 100:216) meta-analysis: beef -0.75, pork -0.72, "
        "poultry -0.68; Gallet 2010/2012 meta-analysis: -0.7..-1.0 by species/region; plant-based "
        "scanner data sits in the same -0.5..-1.4 envelope. -0.9 is the mid-range central.",
        lo=-1.4, hi=-0.5, mode=-0.9,
        note="ONE factor of cultivated's own-price-elasticity TARGET eps_x = eps_own*cult_sub_mult; "
             "the shared logit coefficient beta is DERIVED to hit that target at cultivated's own modeled "
             "price & share (market_share._derive_beta), so beta moves automatically when this moves. "
             "Premium tiers are made LESS elastic in meat_market (cuts x0.8, luxury x0.3): premium buyers "
             "are less price-sensitive (Lusk & Tonsor 2016: demand more inelastic at high price)."),
    "cult_sub_mult": Input(4.0, "x", "[data-bracketed] kappa: HOW MANY TIMES more own-price-elastic CULTIVATED "
        "meat is than meat as a CATEGORY. Plain meaning: a 1% rise in cultivated's price loses kappa x 0.9% of its "
        "buyers, versus 0.9% for meat-in-general. WHY > 1: the measured -0.9 is the elasticity of the meat "
        "CATEGORY, which is inelastic precisely because the category has no close substitute; but a single "
        "cultivated product DOES have a near-perfect substitute right next to it (conventional meat, the SAME "
        "tissue), so its OWN price matters far more -- a price cut wins buyers fast, a price rise loses them to "
        "conventional. kappa therefore sets HOW STEEPLY cultivated's share falls as it gets pricier than "
        "conventional (above parity); it does NOT change the at-parity share (where prices are equal).",
        lo=3.0, hi=6.0, mode=4.0,
        note="DATA ANCHOR (the one direct measurement): Van Loo, Caputo & Lusk 2020 (Food Policy 95:101931) "
             "priced lab-grown across SIX levels ($2.99-$10.49/lb) in a US choice experiment, identifying its "
             "OWN-PRICE ELASTICITY AT PARITY. Their two models bracket it: the conditional logit (price coeff "
             "-0.178/$) implies eps_lab ~ -0.84 at $5/lb; the random-parameter logit (mean -0.72/$, with a lab "
             "random-coeff SD ~3-4.6 LARGER than its mean -> ~half the population positive, half negative) implies "
             "eps_lab ~ -3.4. So the data bracket is eps_lab(at parity, cold) in [-3.4, -0.84]. kappa is the "
             "flat-logit STAND-IN for exactly that real_tissue heterogeneity (= a nested-logit dissimilarity "
             "parameter), so this is the moment that grounds it: at the central kappa=4 the model's implied "
             "at-parity cold elasticity is -1.5, INSIDE the bracket (self-check [4b]; golden-guarded at -1.53827). "
             "CORROBORATION: a single "
             "product's own-price elasticity is typically ~3-5x its category's (the standard brand-vs-category "
             "gap), and cultivated is a closer substitute (same tissue) -> the upper half is apt. RANGE 3-6 spans "
             "the bracket's interior (note kappa=3 dips just under the MNL -0.84 end; the floor could tighten to "
             "~3.5, kept at 3 as a mild dovish margin). RESIDUAL CAVEAT (functional form, not fixable by kappa): "
             "Lusk measures the elasticity AT PARITY, but the realized headline target eps_x = eps_own*kappa = "
             "-0.9*4 = -3.6 is at cultivated's OPERATING POINT R~2.4, where the BLP+kink elasticity is steeper -- "
             "matching the at-parity bracket grounds the SHAPE near parity, but the -3.6 at R~2.4 is an "
             "EXTRAPOLATION (no DCE has priced cultivated at ~2.4x conventional). The OTHER factor of eps_x, so it "
             "moves the DERIVED beta directly; swept lo-hi in self-check [6]."),
    "loss_aversion": Input(1.0, "ratio", "REFERENCE-DEPENDENT price asymmetry lambda (OFF by default). Consumers "
        "may compare each product to the conventional price and feel a premium as a 'loss': a DISCOUNT (below "
        "conventional) rewarded at the UNIT rate (+1), a PREMIUM penalised at -lambda, so "
        "V_loss_j = -lambda*max(0, price_ratio_j - 1) + 1*max(0, 1 - price_ratio_j). lambda=1 (the DEFAULT) is "
        "SYMMETRIC -- the term collapses to a smooth linear (1 - price_ratio) with NO kink, i.e. no loss "
        "aversion; lambda>1 adds an asymmetric premium penalty (Tversky-Kahneman 1992 put the loss/gain ratio "
        "~2.25). Applied uniformly to every product (plant-based at 1.77x and cultivated at R), never a "
        "cultivated-only cliff.",
        lo=1.0, hi=2.25, mode=1.0,
        note="WHY DEFAULT 1.0 (symmetric, no kink) rather than the TK 2.25: (1) it is NEAR-INERT on the headline "
             "anyway -- the beta-derivation absorbs lambda's price slope, so lambda only reshapes the parity KINK, "
             "not the elasticity level (lambda 1->2.25 moves the at-parity share <2pp and leaves the regional "
             "penetration roll-up UNCHANGED). RANGE CAPPED AT 2.25 (the TK median) for a principled reason: the "
             "beta-derivation absorbs lambda's price slope only up to lambda~2.6, where beta saturates at its "
             "monotonicity cap (beta_cap = 1/p_conv - 1e-3); beyond that the realised own-price elasticity would "
             "drift off the eps_own*kappa target (e.g. ~-7 at lambda=4) -- a broken microfoundation, not a "
             "meaningful scenario -- so the slider/prior stops at the literature anchor, where the 'only reshapes "
             "the kink, not the level' property still holds. (A subtler point: the BLP sub-term's coefficient flips "
             "sign around lambda~1.65; above that the price response is carried by the kink rather than the income "
             "log, though the HEADLINE elasticity stays on target throughout the capped range.) (2) Bell & Lattin "
             "2000 (Marketing Sci 19:185) show estimated loss "
             "aversion in aggregate choice data is largely CONFOUNDED by unmodeled price-response heterogeneity -- "
             "and this model already carries that heterogeneity in kappa (cult_sub_mult, the real_tissue "
             "random-coefficient stand-in), so a separate asymmetric kink risks DOUBLE-COUNTING it; (3) the model's "
             "reference is CONTEXTUAL (the competitor's current price), a cross-sectional comparison that does NOT "
             "fade -- distinct from a TEMPORAL reference anchored to a product's own price history, which adapts "
             "and is transient (the genuinely time-varying novelty effect lives in the neophobia fade, not here). "
             "BONUS: at lambda=1 the model's at-parity own-price elasticity is -0.82, CLOSER to Lusk 2020's "
             "measured MNL -0.84 than the kinked lambda=2.25 (-0.50) was. So lambda is now an OFF-by-default "
             "exploratory dial (range 1-4) for anyone who wants to test reference-dependent asymmetry, not a "
             "baked-in behavioral assumption. Its slope still feeds the beta calibration when moved."),

    # --- cultivated's STANDING dials (NO baked-in stance; the reader sets them) -
    #     Cultivated's standing vs conventional is TWO interpretable scenario dials,
    #     both with a NEUTRAL default (not fitted — reported as a band): taste-
    #     acceptance accept_x is the FRICTION half (enters utility as w_taste*(accept_x
    #     -1)); slaughter-free value theta_free_M is the UPSIDE half (the mainstream
    #     weight on the slaughter-free attribute). See market_share.py.
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
        "weighted by w_taste utils. 1 = tastes as real as conventional (neutral); <1 = a taste deficit.",
        lo=0.6, hi=1.0, mode=1.0,
        note="The taste-FRICTION half of cultivated's standing. In the MNL the utility offset is "
             "w_taste*(accept_x-1) utils, weighted by the shared taste coefficient w_taste."),
    "premium_resistance": Input(1.0, "x", "[assumed] JUDGEMENT DIAL scaling how much premium/cut meat "
        "resists cultivated, relative to everyday mince. It multiplies BOTH per-tier demand levers in "
        "meat_market together (they encode one belief): the authenticity offset tau_type "
        "(basic +0.2, cut -0.4, premium -1.5 utils) AND the deviation of the elasticity multiplier from 1 "
        "(cut 0.8, premium 0.3). At 1.0 = the central ladder; 0 = no tier effect (cultivated penetrates "
        "premium as easily as mince); 2 = doubly resistant premium.",
        lo=0.5, hi=1.5, mode=1.0,
        note="The model's most JUDGEMENT-TO-TARGET demand assumption: the tier offsets have NO external "
             "data source — they were chosen so premium stays demand-capped even at a deep price discount "
             "(the 'sweet spot is mid-cuts' result). Exposed and SWEPT (prior 0.5-1.5) so that judgement's "
             "leverage is visible rather than hidden. Scales (tau_type) and (eps_mult - 1) about their "
             "neutral points, so resistance=0 removes the tier effect entirely."),
    "real_tissue_x": Input(1.0, "0/1", "[IDENTIFYING PREMISE, now a DIAL] whether CULTIVATED meat counts as "
        "'real animal tissue' (1) or not (0). =1 is the model's load-bearing premise: cultivated, being "
        "actual cells, INHERITS conventional meat's real-tissue standing and so escapes the plant-based "
        "'not real meat' penalty — the structural reason it can succeed where plant-based stalled. Exposed "
        "as a 0/1 dial (default 1) so a SKEPTIC can set it to 0 ('consumers won't credit lab-grown as real "
        "meat') and watch cultivated collapse toward the plant-based outcome. Weighted by w_realtissue_M "
        "(mainstream) in V_x.",
        note="The single most important ASSUMPTION in the model, deliberately made adjustable rather than "
             "hardwired. At 1 cultivated > plant-based at parity (the headline ordering); at 0 cultivated "
             "becomes a second plant-based product. NOT swept in the MC (it is a scenario axis, like the "
             "acceptance dials), but a primary what-if."),
    "real_tissue_p": Input(0.0, "0/1", "[product position] whether PLANT-BASED meat counts as 'real animal "
        "tissue' (1) or not (0). =0 by definition (plant-based is not animal tissue) — this is the penalty "
        "that, with its price premium and taste deficit, keeps plant-based meat at ~1.2%. Exposed for "
        "SYMMETRY with real_tissue_x (equal footing): set it to 1 to ask the counterfactual 'what if "
        "consumers treated plant-based as equivalent to real meat?' (it would rise sharply). Default 0.",
        note="Plant-based gets the SAME machinery as cultivated; the only a-priori difference between the "
             "two novel meats is this attribute (and price/taste, which are observed). Equal footing means "
             "the asymmetry is a visible DIAL, not a hidden constant."),
    # --- HEALTH-PERCEPTION ATTRIBUTE (positions per product; the WEIGHT is segment-specific & SOLVED) ---
    # Health is a named attribute b_health on every product, weighted by a calibrated, segment-specific
    # health weight (w_health_M / w_health_E). The whole-food health premium is the principled
    # replacement for the old free whole-food intercept xi_w: it is WHY ethical/health-minded eaters
    # default to beans over a processed veggie burger. Positions below; weights are solved.
    "health_x": Input(0.0, "norm", "[SCENARIO, unidentified] HEALTH-PERCEPTION POSITION of CULTIVATED meat "
        "(on the same scale as the other products' health positions, weighted by the segment health weight). "
        "POSITIVE = perceived HEALTHIER (a draw: 'clean, no antibiotics, no faecal contamination, controlled "
        "fat'); NEGATIVE = perceived LESS healthy ('lab-grown, unnatural, ultra-processed'); 0 = at the "
        "conventional reference. Default 0 because the evidence is genuinely TWO-SIDED with no point estimate. "
        "A scenario dial like novelty/authenticity: inert at 0 relative to conventional, never re-pins.",
        lo=-0.5, hi=0.5, mode=0.0,
        note="Distinct from taste (a_x, sensory) and slaughter-free (theta, ethics). Equal footing with the "
             "plant-based health dial. Swept +-0.5 in the MC band."),
    "health_p": Input(0.0, "norm", "[SCENARIO, unidentified] HEALTH-PERCEPTION POSITION of PLANT-BASED meat — "
        "the SAME dial as health_x, for equal footing. POSITIVE = the 'plant-based = good for you' health-halo; "
        "NEGATIVE = the 'ultra-processed fake meat' backlash. 0 = at the conventional reference. Default 0 and "
        "UNIDENTIFIED, like health_x: an exploratory deviation from plant-based's calibrated ~1.2%, not a re-pin.",
        lo=-0.5, hi=0.5, mode=0.0,
        note="The term for 'how much of plant-based's plateau is a health-perception problem?'. Swept in MC."),
    "health_w": Input(2.0, "norm", "[position] HEALTH-PERCEPTION POSITION of the WHOLE-FOOD outside option "
        "(beans/tofu/lentils): POSITIVE — whole plant foods are widely seen as 'the healthy choice' (dietary "
        "guidance ranks legumes above red meat; ~17% name healthfulness the top protein driver, and 'good "
        "source of protein' is the #1 healthy-food definer). This positive position, times the SOLVED segment "
        "health weight, is what replaces the old free whole-food intercept. Default +2 (a judgement scale set "
        "with the weight; only the product depends on data, not the split)."),
    "health_c": Input(-0.1, "norm", "[position] HEALTH-PERCEPTION POSITION of CONVENTIONAL meat: slightly "
        "NEGATIVE — red/processed meat carries a mild 'less healthy' standing (saturated fat, processed-meat "
        "guidance) relative to whole plant foods, though it remains a high-quality protein. Small by design; it "
        "sets conventional's health standing that the other positions are measured against. Default -0.1, so "
        "cultivated (health_x=0, i.e. no antibiotics/contamination, controlled fat) carries a mild +0.1 health "
        "edge over conventional — a small, defensible lift to the at-parity share (~47% -> ~50%)."),
    "neophobia_p0": Input(-1.0, "utils", "[behavioural] plant-based meat's INITIAL (cold-start) novelty "
        "attitude — the analogue of neophobia_x0 for cultivated. Plant-based is already MATURE (~1.2%), so "
        "its observed position is the calibration target and this cold-start is mostly HISTORICAL / "
        "exploratory: it sets where plant-based's own diffusion curve STARTED. Crucially, plant-based's "
        "novelty never fully faded into success because it never reached sensory parity (the taste deficit "
        "a_p<1 is permanent) — so in the timing chart plant-based is the STALLED counterfactual to "
        "cultivated. Default -1.0; fades toward the long-run neophobia_p (default 0) at accept_rate.",
        lo=-2.0, hi=0.5, mode=-1.0,
        note="Mirrors neophobia_x0 so plant-based has the SAME timing apparatus. PB's stall in the chart is "
             "driven by its permanent taste deficit (a_p) + price premium (R_p), not by novelty — novelty "
             "fades for both; taste does not. Exploratory (PB is calibrated to its mature share)."),

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
    "price_pb_mult": Input(1.77, "x p_conv", "[GFI] plant-based meat retail PRICE premium vs "
        "conventional: GFI/NIQ 2024 put PB meat at +77% per lb (up from +65% in 2022); the gap WIDENED, "
        "and 2025 narrowing is an artifact of beef inflation, not PB cost-down",
        lo=1.5, hi=2.2, mode=1.77,
        note="PB meat is a genuine, persistent price PREMIUM — a load-bearing reason its share is small."),
    "price_wf_mult": Input(0.25, "x p_conv", "[BLS] whole-food plant protein staple (dried beans/lentils) "
        "$/kg vs commodity meat: US dried beans $3.40/kg (BLS Aug 2025), representative $2-3.5/kg, vs "
        "~$12/kg meat -> ~0.25x. Beans are also ~3-5x cheaper per kg of PROTEIN than beef (VRG 2024).",
        note="the outside option is CHEAP; with taste_quality_w and the whole-food HEALTH premium "
             "(health_w x the solved segment health weight) it absorbs most ethical demand -> PB stays ~1%."),
    "taste_quality_w": Input(-0.7, "norm", "[assumed] whole-food (beans/tofu/lentils) taste/utility AS A "
        "MEAT SUBSTITUTE: nutritious and cheap, but quite far from a meat-eating experience. Normalised "
        "like (accept_x-1): 0 = as satisfying as real meat, negative = a worse stand-in for meat (-0.7 ≈ "
        "a_w 0.3 on the 1=real-meat scale)",
        lo=-1.0, hi=-0.3, mode=-0.7,
        note="NOT load-bearing: the whole-food HEALTH weight (w_health) is SOLVED to hit the meatless / "
             "PB-share targets, so it absorbs whatever this taste does not — lowering taste_quality_w just "
             "raises the solved health weight, leaving cultivated and plant-based shares unchanged. Set to a plausible "
             "'beans aren't a burger' value; the split between taste and the solved ASC is not identified."),

    # --- Rung 3: income-dependent price sensitivity (BLP log form) -----------
    # Price enters utility as alpha*ln(income_eff - price) (Berry-Levinsohn-Pakes 1995):
    # richer consumers are LESS price-sensitive. alpha is derived in market_share from
    # beta_price so the US-reference behaviour is unchanged; income_eff = income_ref *
    # (income/income_ref)**income_gradient damps the cross-region gradient. See market_share.py.
    "income_ref": Input(85810, "$/yr", "[World Bank] US GDP per capita PPP 2023 ($85,810) — the "
        "REFERENCE income at which the price coefficient is anchored (so the US/commodity case is "
        "unchanged). Only income RATIOS across regions matter, so the absolute level is absorbed by alpha."),
    "income_gradient": Input(0.5, "exponent", "[Muhammad/ERS] phi: the DAMPING exponent on the BLP income "
        "term. Income enters the price utility as genuine Berry-Levinsohn-Pakes V_price = alpha*ln(y_eff - "
        "price_j), with the EFFECTIVE income y_eff = income_ref*(income/income_ref)**phi. phi controls how "
        "strongly the BLP curvature is expressed across regions: phi=1 = raw BLP (y_eff = actual income); "
        "phi=0 = no income effect (y_eff = income_ref everywhere); 0<phi<1 damps it.",
        lo=0.0, hi=1.0, mode=0.5,
        note="phi=0.5 (DEFAULT) gives a Nigeria/US own-price-elasticity ratio ~2.2x (India ~1.8x), matching "
             "the empirical food-price-elasticity gradient (poor countries ~2-3x more responsive for meat; "
             "Muhammad et al. 2011 USDA ERS, food income-elasticity 0.78 low- vs 0.50 high-income). WHY DAMP: "
             "RAW BLP (phi=1) is TOO STEEP for food — it implies a ~6.4x rich->poor elasticity ratio, far "
             "above the data; phi damps the EFFECTIVE income inside the log so the BLP curvature matches the "
             "empirical gradient. This is GENUINE BLP (income inside the log, a single constant alpha = "
             "-beta*(income_ref - anchor_price); the diminishing-marginal-utility-of-income curvature is the "
             "mechanism), NOT the earlier f-multiplier form (which froze income in the log and re-added it "
             "outside — that was not BLP). The US anchor and every at-parity number are invariant to phi "
             "(y_eff = income_ref at the US reference). Cultivated (a premium at R>1) penetrates LESS where "
             "income is lower; the effect saturates above ~US incomes (a $30 product is negligible to a high "
             "earner). phi=0 removes it; phi=1 is raw, over-steep BLP."),
    "taste_quality_p": Input(-0.2, "norm", "[Nectar] plant-based meat AVERAGE blind-taste deficit vs "
        "real meat. Nectar 'Taste of the Industry' 2025: only ~16% (20/122) of PB SKUs reach blind "
        "sensory parity, so the category average is BELOW parity. Normalised like (accept_x-1): "
        "0 = parity, negative = deficit",
        lo=-0.4, hi=0.0, mode=-0.2,
        note="taste is the binding constraint on PB meat (Nectar); the best ~16% reach parity, the "
             "average lags -> a modest negative, weighted by w_taste in utils."),
    "w_taste": Input(5.0, "utils", "[calibration] taste-utility weight: converts a normalised taste "
        "gap (0=parity, -1=very poor) into utils. Large => the flavour-first mainstream punishes a "
        "taste deficit heavily; it is the single shared taste coefficient for all products. It also sets "
        "the SCALE the other perception weights are read against: taste is the #1 food-choice driver "
        "(IFIC 2025; Malone & Lusk 2017 find taste WTP ~2x health and ~3x safety), so w_taste is the "
        "largest non-price weight and health (w_health_M ~0.26x w_taste) sits well below it."),
    "w_eth": Input(0.05, "fraction", "[Gallup] ethics-driven CORE = vegetarian (4%) + vegan (1%), "
        "Gallup 2023",
        lo=0.04, hi=0.10, mode=0.05,
        note="5% is the ethics core and is KEPT. Plant-based lands at ~1% (not ~5%) because the cheap, "
             "HEALTHY whole-food outside option (the health premium w_health_E x health_w) absorbs most "
             "ethical eaters — NOT because the segment is smaller. The flexitarian PB buyer base (~89% of "
             "buyers, GFI 2024) lives in the MAINSTREAM via theta_free_M, not here."),
    "w_realtissue_M": Input(2.0, "utils", "[calibration, SOLVED] MAINSTREAM utility weight on REAL TISSUE "
        "(=1 conventional & cultivated, =0 plant-based & whole-food). SOLVED at runtime so the mainstream "
        "carries pb_mainstream_frac (~89%) of plant-based buyers (GFI/Morning Consult 2024). The stored "
        "value is a seed.",
        note="A REDUCED-FORM bundle: the mainstream non-price standing of non-real-meat products (genuine "
             "'I want real meat' preference + processed/habit residual). Cross-sectionally it is NOT "
             "separately identifiable from habit (we only observe plant-based, which lacks both), so we do "
             "not split it (Heckman state-dependence-vs-heterogeneity). HABIT proper lives in the diffusion "
             "rung (adoption_timing) + the long-run acceptance dials accept_x/theta_free_M. real_tissue is the "
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
        note="pins w_health_M (the mainstream health weight) so the cheap, healthy outside option does not "
             "spill unrealistically into the mainstream. SOFT (no clean source); mostly moves the whole-food "
             "line, NOT the cultivated headline (self-check [6]: <=0.2pp). Lowered 0.10->0.06 so total "
             "whole-food (~ethical core 5pp + this) sits ~10%, not ~14%; the irreducible part is the ethical "
             "segment eating beans (w_eth * ~96% ~= 5pp), which IS the model's premise, not a free knob."),
    "w_health_M": Input(1.2, "utils", "[calibration, SOLVED] MAINSTREAM weight on the HEALTH attribute — "
        "SOLVED so mainstream whole-food == wf_mainstream_target. Seed only. Times the whole-food health "
        "position (health_w), this is the mainstream's pull toward beans; it REPLACES the old free whole-food "
        "intercept K_wholefood_M.",
        note="SEGMENT-SPECIFIC (vs w_health_E for the ethical segment): mainstream meat-eaters weight health "
             "less / substitute beans for a meat occasion rarely, so this weight is much smaller than the "
             "ethical one. Splitting the health weight by segment is what lets w_realtissue_M be pinned to the "
             "buyer split without the cheap bean option leaking into the mainstream. LITERATURE CHECK: Malone "
             "& Lusk (2017, J. Agric. Appl. Econ. 49:139), a US discrete-choice experiment with taste, health "
             "and safety perceptions on a common -5..+5 scale, find WTP of $0.60/$0.31/$0.21 per unit -> "
             "mainstream HEALTH is ~0.52x TASTE (and the IFIC 2025 'very important' ratio ~0.78x brackets the "
             "soft end). The solved w_health_M lands at ~0.26x w_taste — i.e. health is weighted BELOW taste "
             "and price for the mainstream, consistent with (and slightly below) the discrete-choice anchor."),
    "w_realtissue_E": Input(0.0, "utils", "[assumed] ethical-segment weight on real tissue ~ 0: ethical "
        "eaters choose on slaughter-free, not on 'real meat'"),
    "w_slaughter_E": Input(4.0, "utils", "[assumed] ETHICAL-segment utility weight on the SLAUGHTER-FREE "
        "attribute (=1 for p, x, w; =0 for conventional). Large => segment E strongly avoids conventional "
        "and is drawn to no-slaughter options; this is what lets cultivated win an early beachhead at R>1"),
    "pb_share_target": Input(0.012, "share", "[GFI] plant-based meat's mature share of TOTAL meat "
        "(~0.8% of all meat by $, ~1.7% of packaged, <1% by volume; ~13% household penetration; declining "
        "since the ~2020-21 peak), SPINS/Circana via GFI 2024",
        lo=0.008, hi=0.017, mode=0.012,
        note="the calibration ANCHOR: the whole-food health weight w_health is solved at runtime so the model reproduces this with "
             "cultivated absent (market_share.solve_calibration) — a solved calibration target, not a static floor."),
    "w_health_E": Input(2.3, "utils", "[calibration, SOLVED] ETHICAL-segment weight on the HEALTH attribute — "
        "SOLVED so the ethical-segment plant-based rate hits its target (the residual ~11% of PB buyers / the "
        "non-mainstream part of pb_share_target). Times the whole-food health position (health_w), this is the "
        "ethical segment's strong pull toward whole foods; it REPLACES the old free intercept K_wholefood. Seed.",
        note="this (a large health weight on the healthy whole-food option), not a smaller w_eth, is why a 5% "
             "ethical core yields only ~0.1pp of PB: the healthy whole-food option (beans/tofu) absorbs most "
             "ethical eaters. Diffusion ruled out (PB is mature/declining). Mainstream uses the smaller "
             "w_health_M. The health-minded and the ethical overlap, so the ethical segment weights health "
             "heavily — the principled reason it defaults to whole foods over a processed veggie burger."),
    # === FOOD NEOPHOBIA — an adjustable +/- attitude to a NOVEL food, on BOTH non-
    #     conventional meats. SIGN CONVENTION: the value is a UTILITY OFFSET in utils,
    #     NEGATIVE = neophobia (the novel product is shunned, a penalty), POSITIVE =
    #     neophilia (novelty is a draw, a bonus), 0 = neutral. Named & theory-grounded
    #     (Pliner & Hobden 1992, the Food Neophobia Scale) — NOT a generic cultivated-only
    #     "standing" catch-all: it applies SYMMETRICALLY to plant-based AND cultivated, the
    #     two novel meats (conventional & whole-food beans are familiar -> 0). Default 0 =
    #     neutral, so it does not move the central headline; it is an exploration dial.
    "neophobia_x": Input(0.0, "utils", "[behavioural] CULTIVATED's long-run NOVELTY attitude (utility offset): "
        "NEGATIVE = food neophobia (wary of a novel/unfamiliar food — a penalty), POSITIVE = neophilia (drawn "
        "to the new — a bonus), 0 = neutral (treated like conventional on novelty). Adjustable +/-. This is the "
        "PERMANENT (long-run) part — where novelty attitude LANDS after the product is familiar; the INITIAL "
        "cold-start value neophobia_x0 fades toward THIS with exposure.",
        lo=-2.0, hi=1.0, mode=0.0,
        note="Default 0 is neutral and non-load-bearing. Dial NEGATIVE if a residual 'lab-grown is unnatural' "
             "aversion persists even after the product is familiar (distinct from a TASTE deficit, which is "
             "accept_x); POSITIVE if novelty / cleaner-tech is itself a draw. An exploration dial alongside "
             "accept_x and theta_free_M (Gate 2); held at 0 centrally."),
    "neophobia_p": Input(0.0, "utils", "[behavioural] PLANT-BASED's NOVELTY attitude (utility offset; same sign "
        "convention as neophobia_x: - = neophobia, + = neophilia). An EXPLORATORY override applied after "
        "calibration (like a_p, R_p): default 0 keeps PB at its calibrated ~1.2%; move it to ask 'what if PB "
        "faced more/less novelty resistance?'. PB's residual processed-food / 'fake meat' resistance is already "
        "baked into the calibrated w_realtissue_M, so this term is a DEVIATION from that, not a double-count.",
        lo=-2.0, hi=1.0, mode=0.0,
        note="Lets plant-based be explored as a first-class product (with a_p, R_p). Default 0 = the observed, "
             "calibrated position; it is not in the headline band."),
    "neophobia_x0": Input(-2.8, "utils", "[DATA-ANCHORED] cultivated's INITIAL (cold-start, today) novelty "
        "attitude — the value of neophobia_x at the launch of diffusion (t=0), before any familiarity builds. "
        "It FADES with cumulative exposure (mere-exposure effect) at rate accept_rate, relaxing toward the "
        "long-run neophobia_x. DEFAULT -2.8 is anchored to data: at price+taste parity (R=1, accept_x=1) it "
        "reproduces cultivated's observed COLD at-parity share of ~5% (Van Loo, Caputo & Lusk 2020, US "
        "choice experiment: lab-grown 5% at price parity with beef). The RANGE [-3.5, +1.5] spans the full "
        "survey FRAMING band: -3.5 -> ~3% (coldest), -2.8 -> ~5% (Lusk choice exp), 0 -> ~47% (neutral), "
        "+1.5 -> ~78% (Perdue 2024 'cultivated chicken in a restaurant' warm framing ~60%). The legacy "
        "'launch wariness' is now DERIVED = neophobia_x0 - neophobia_x (the transient part that fades).",
        lo=-3.5, hi=1.5, mode=-2.8,
        note="Replaces the old neophobia_launch (which was the delta x0 - x_long); setting the two ENDPOINTS "
             "(initial x0, final neophobia_x) directly is more intuitive than setting the delta. Cold-start "
             "default -2.8 = 'today's unfamiliar consumer'; it sets the START of the diffusion S-curve, not "
             "the equilibrium (which is neophobia_x). With accept_x it captures the plant-based lesson: "
             "exposure cures the NOVELTY penalty (this fades), but a TASTE deficit (accept_x<1) is permanent. "
             "SWEPT in the Monte Carlo so the 5-60% framing uncertainty enters the band."),

    # --- Rung 4: timing -----------------------------------------------------
    "p_innov": Input(0.02, "1/yr", "[literature] Bass innovation coeff.; near the cross-study "
        "norm (~0.03 avg in Bass-model meta-analyses) — independent adopters",
        lo=0.005, hi=0.05, mode=0.02,
        note="Bass meta-analyses (Sultan/Farley/Lehmann 1990; Van den Bulte 2002) center p~0.01-0.03; "
             "range spans slow (0.005) to fast (0.05) early uptake."),
    "q_imit": Input(0.40, "1/yr", "[literature] Bass imitation coeff.; near the cross-study "
        "norm (~0.38 avg) — word-of-mouth/contagion",
        lo=0.20, hi=0.60, mode=0.40,
        note="Bass meta-analytic norm q~0.3-0.5; range 0.20-0.60 spans weak to strong contagion."),
    # NOTE: there is deliberately NO long-run cultivated "standing" input. Neophobia
    # (neophobia_M/E) fades to ZERO with exposure, and the PERMANENT at-parity standing
    # is the interpretable pair accept_x (sensory parity) + theta_free_M (cleaner-meat
    # upside) — the headline at-parity scenario axis (see RESULTS Gate 2). Removing the
    # old xi_x_floor_M dial is the "no symmetry-breaking garbage collector" fix.
    "accept_rate": Input(0.15, "1/exposure", "[assumed] how fast the INITIAL neophobia (neophobia_x0) decays "
        "toward the long-run neophobia_x, per unit cumulative AVAILABILITY (rollout F, not the small consumed "
        "share)",
        lo=0.05, hi=0.50, mode=0.15,
        note="UNGROUNDED (sets WHEN novelty fades, not the long-run ceiling — that is neophobia_x / accept_x / "
             "theta_free_M). ~0.15 -> ~90% faded by yr~23; range 0.05 (novelty barely resolves within 30yr) to "
             "0.50 (fast, ~90% by yr~13). Driving it by consumed share would never ignite once shares are "
             "realistically ~1%, hence availability (F). SWEPT in the MC (time-to-stabilize uncertainty)."),
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
    "material_price": Input(5.0, "$/kg", "[assumed/round] synthetic PLA/PCL <$10/kg, plant "
        "cheaper, gels higher (Gu et al. 2025 ranks materials but gives no $/kg); Gelatex vendor claim "
        "~<$1/kg of meat. Centred so the structured-scaffold mode 0.2*5 + process 5 = $6/kg == SCAF (the "
        "round datasheet scaffold cost) — the decomposition is illustrative, pinned to that one number.",
        lo=2.0, hi=20.0, mode=5.0),
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
# Demand-model tier ladder & scaffold (model constants, not sliders).
# These are scaled live by the `premium_resistance` slider in meat_market; they are
# defined HERE so the datasheet is the single source of truth (meat_market and
# market_share read them rather than redefining), and so the methods text can quote
# the same numbers it documents. NOT swept individually (premium_resistance sweeps
# the whole ladder); judgement-to-target, no external per-tier data exists.
# ----------------------------------------------------------------------------
SCAF: float = 6.0            # scaffold cost $/kg for a STRUCTURED cut (ASSUMED; no published TEA)
# The cost rung (cuts, §1, the JS) uses the round scalar SCAF; the foothold/uncertainty rungs build
# the SAME scaffold cost from a 3-input decomposition so they can sample a band. The two MUST agree on
# the central (mode) value or the foothold R silently drifts from the rest of the model — guard it here.
_SCAF_DECOMP = (REGISTRY["scaffold_frac"].value * REGISTRY["material_price"].value
                + REGISTRY["process_cost"].value)
assert abs(SCAF - _SCAF_DECOMP) < 1e-9, (
    f"scaffold cost out of sync: SCAF={SCAF} but the decomposition mode "
    f"(scaffold_frac*material_price + process_cost) = {_SCAF_DECOMP}. Re-centre one so they match.")
PREMIUM_RATIO: float = 2.5   # a structured product priced >= this x its species' base form is "premium"
AUTH_BASIC: float = +0.2     # per-tier authenticity offset (utils): everyday staple — cleaner-meat pull, no hang-up
AUTH_CUT: float = -0.4       #   cut (steak/fillet): some "want the real cut" attachment
AUTH_PREMIUM: float = -1.5   #   luxury (wagyu/sushi): strong authenticity, weak welfare pull
EPS_MULT_CUT: float = 0.8    # per-tier elasticity multiplier: cuts a bit less price-sensitive
EPS_MULT_PREMIUM: float = 0.3  #   premium buyers barely price-sensitive -> caps premium share

# Loss-aversion asymmetry constant (Tversky-Kahneman 1992 median ~2.25). The LIVE loss-aversion
# coefficient is the `loss_aversion` slider (canonical form, lambda IS the coefficient); this
# constant is the literature anchor surfaced for the methods text / interactive `const`.
LOSS_AVERSION_RATIO: float = 2.25


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
              f"derived  AA_FLOOR = aa_intensity x aa_bulk_price = {AA_FLOOR:g} $/kg"]
    return "\n".join(lines)


if __name__ == "__main__":
    print(datasheet())
