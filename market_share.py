#!/usr/bin/env python3
"""
market_share — from the price ratio to a best-guess market share (a discrete-choice
demand model over FOUR products by TWO consumer segments).

Rung 2 gave us R = p_cult/p_conv. This rung answers Output 2: *what share does a
given R plausibly buy?* It is the SOFTER half of the model, so the cultivated
headline is always a BAND over the acceptance dials (accept_x, theta_free_M), never a forecast.

The demand model: a two-segment, four-product latent-class logit
----------------------------------------------------------------
Consumers choose among FOUR products, each carrying four attributes:

    product                price-ratio   taste   slaughter-free   real-tissue
    c  conventional meat   1 (anchor)    0 (ref) 0                1
    p  plant-based meat    ~1.77         -0.2    1                0
    x  cultivated meat     R (cost)      accept  1                1
    w  whole-food / veg    ~0.4 (cheap)  0       1                0   (the OUTSIDE option)

`w` (beans/tofu/lentils — "eat plants, not fake meat") is the reason plant-based
*meat* sits at ~1% despite a 5% ethically-motivated population: most ethical eaters
satisfy no-slaughter with whole foods, not a veggie burger. Without it the model
cannot reproduce PB-meat's observed floor.

Two consumer segments (a latent-class mixture, NOT a nest):

  * MAINSTREAM M (weight 1 - w_eth ~ 0.95) — taste/price-driven. Weights REAL TISSUE
    heavily (w_realtissue_M): conventional and cultivated are "real meat", plant-based
    and whole-food are not. This is what makes conventional DOMINATE the mainstream.
  * ETHICAL E (weight w_eth ~ 0.05, Gallup veg+vegan) — weights SLAUGHTER-FREE heavily
    (w_slaughter_E); barely cares about real-tissue. Its no-slaughter demand is mostly
    soaked up by the whole-food outside option.

    total share_j = w_eth * P_E(j) + (1 - w_eth) * P_M(j)

Each segment is a FLAT multinomial logit (softmax) over the products present. EVERY
product goes through the SAME rule — a (products x attributes) table dotted with
(segment x weights). The ONLY non-attribute constant is the outside option's intercept
(xi_w); the meats carry no free constant (their deviations are all named attributes):

    V_sj = V_price(price_j, income)        # BLP income term (richer = less price-sensitive)
         - loss_aversion * max(0, price_ratio_j - 1)              # premium penalty (loss side, slope lambda)
         + 1.0          * max(0, 1 - price_ratio_j)              # discount reward (gain side, unit slope)
         + q_taste * taste_j
         + w_slaughter[s] * slaughter_j  +  w_realtissue[s] * real_tissue_j
         + neophobia_j  +  xi_j           # novelty attitude (p, x); outside-option intercept (w only)
    P_sj = softmax_j(V_sj)

No product gets a special-case term: plant-based and cultivated are treated by the
SAME two-sided, reference-dependent rule (penalised for a premium, rewarded for a
discount, with the loss side ~2.25x steeper — Tversky-Kahneman loss aversion).
Conventional `c` is the reference (price_ratio 1, taste 0, intercept 0); see the
attribute table in `_utilities`.

Why this captures "cultivated cannibalises CONVENTIONAL, not the veggie burger"
without a NEST (the red-bus/blue-bus / IIA fix)
------------------------------------------------------------------------------
A single logit obeys IIA (a new option steals proportionally). We do NOT add a nest
(the user's constraint, and what the rebuild dropped). Instead the conventional-
cannibalisation emerges from PREFERENCE HETEROGENEITY plus the shared REAL_TISSUE
attribute: real_tissue makes conventional own almost the entire (large) mainstream
segment, so a proportional reduction there comes overwhelmingly out of conventional
in absolute terms; plant-based and whole-food, which barely register in the
mainstream, are hardly touched. The ethical segment (only ~5%) is where cultivated
also draws from plant-based / whole-food. Net: introducing cultivated at parity
takes tens of points from conventional and <1 pt from plant-based. The real_tissue
attribute is the MINIMAL extra structure (one shared characteristic) that does the
job the retired real-meat nest used to do — and it is what cultivated SHARES with
conventional, which is precisely the structural reason cultivated can succeed where
plant-based stalled. (See the [3] cannibalisation self-check below.)

Price and income (the BLP form)
-------------------------------
Price enters as V_price = alpha * ln(income_eff - price) (Berry-Levinsohn-Pakes 1995):
richer consumers are LESS price-sensitive (the marginal utility of income falls). The
shared coefficient beta is DERIVED, not an input: the behavioural primitive is cultivated's
OWN-PRICE ELASTICITY eps_x = eps_own * cult_sub_mult (meat's measured -0.9, steepened ~4x
because conventional is a near-perfect substitute), and beta is solved so the logit's TOTAL
price response reproduces eps_x AT cultivated's own modeled retail price & share -- a short fixed point
with NO hand-chosen anchor (see `_derive_beta`). The anchor price is cultivated's own retail
price (biomass_cost + markup_add), so beta tracks the cost model. alpha is then pinned so the
local price coefficient equals beta at the reference income (income_ref, US GDP/cap PPP).
Across regions income_eff = income_ref*(income/income_ref)**income_gradient damps the gradient
to the empirical ~2-3x rich->poor.

Calibration (demographic-conditional, reduced form)
---------------------------------------------------
Three monotone 1-D solves (`solve_calibration`) pin the model to cross-sectional data:
w_realtissue_M so the MAINSTREAM carries ~89% of plant-based buyers (GFI: most PB buyers
are flexitarians, not the 5% ethical core); the SEGMENT-SPECIFIC HEALTH WEIGHTS
w_health_M / w_health_E (times the whole-food health premium) so the mainstream meatless rate
and the residual ethical PB rate match (total PB ~1.2%). The health weight REPLACES the old
free whole-food intercept xi_w — the model now carries no free fitted constant, every product's
standing is a named attribute times a weight. w_realtissue_M is a REDUCED-FORM standing (real-tissue
preference + processed/habit residual) — we do not split it into a separate habit term
(not identified from heterogeneity without panel data; habit lives in the Rung-4 diffusion
+ the long-run acceptance dials accept_x/theta_free_M). real_tissue is the IDENTIFYING ASSUMPTION that cultivated,
being real tissue, escapes the plant-based penalty.

Glossary (for the non-economist)
--------------------------------
  * logit / softmax : turns each option's "attractiveness" (utility) into shares that
    sum to 100%.
  * utility V_j     : one number for how attractive option j is.
  * beta_price      : how much price matters (more negative = flee price faster).
  * real_tissue     : a 0/1 attribute = "is this actual animal tissue" (c, x = yes).
  * intercept (xi)  : an outside-option baseline beyond the attributes; ONLY the whole-food
    outside option has one (calibrated to data). The meats carry no free constant.
  * loss aversion   : a reference-dependent term measuring each product's price against
    the conventional price — penalising a premium and rewarding a discount, with the
    penalty ~2.25x steeper than the reward (Tversky-Kahneman); applies to every product.

Usage
-----
    python market_share.py --no-latex
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field, replace

import numpy as np
import matplotlib.pyplot as plt

from common import setup_style, _save
from inputs import value, prior, LOSS_AVERSION_RATIO
from cost_model import (
    CostParams, biomass_cost, cost_floor, ratio as cost_ratio,
)


# product order used throughout: whole-food, conventional, plant-based, cultivated
PRODUCTS = ("w", "c", "p", "x")

# LOSS_AVERSION_RATIO (Tversky-Kahneman 1992 median ~2.25) lives in inputs.py (the datasheet);
# imported above and re-exported here so build_interactive can read it from market_share as
# before. The LIVE loss-aversion coefficient is the `loss_aversion` slider (canonical form,
# lambda IS the coefficient); this constant is just the literature anchor for the methods text.


# ----------------------------------------------------------------------------
# Demand parameters  (defaults + sources live in inputs.py — the datasheet)
# ----------------------------------------------------------------------------
@dataclass
class DemandParams:
    p_conv: float = value("p_conv")               # conventional commodity price $/kg (the R anchor)

    # --- price sensitivity -> the shared logit price coefficient ------------
    #   The two factors of cultivated's OWN-PRICE ELASTICITY TARGET. The coefficient
    #   beta is DERIVED from them (not an input): it is solved so the logit reproduces
    #   eps_own*cult_sub_mult at cultivated's own modeled retail price & share, with no
    #   hand-chosen price/share anchor. See `_derive_beta`.
    eps_own: float = value("eps_own")             # own-price elasticity of MEAT (scanner: -0.5..-1.4)
    cult_sub_mult: float = value("cult_sub_mult")  # x: cultivated more elastic (conventional ~ perfect substitute)
    income_ref: float = value("income_ref")       # reference income ($/yr) for the BLP price term
    income_gradient: float = value("income_gradient")  # phi: how strongly price-sensitivity scales with income

    # --- product positions (attributes) ------------------------------------
    # NOTE on R_p / a_p semantics vs the interactive (build_interactive.py): setting price_pb_mult
    # or taste_quality_p HERE (via the constructor) RE-PINS the calibration in __post_init__, since
    # the solve runs against these positions — used by calibration_robustness/figures. The interactive
    # JS, by deliberate design (see the R_p / a_p slider tooltips), treats them as EXPLORATORY OVERRIDES
    # applied AFTER calibration: they move plant-based's share without re-pinning it to ~1.2%. Both are
    # intentional; do NOT "reconcile" them by forcing one to behave like the other.
    price_pb_mult: float = value("price_pb_mult")   # plant-based price premium (x p_conv); constructor re-pins (see note)
    price_wf_mult: float = value("price_wf_mult")   # whole-food price (x p_conv) — cheap
    taste_quality_p: float = value("taste_quality_p")  # plant-based taste deficit (0=parity); constructor re-pins (see note)
    taste_quality_w: float = value("taste_quality_w")  # whole-food taste AS A MEAT SUBSTITUTE (norm, 0=parity)
    q_taste: float = value("q_taste")               # taste-utility weight (utils per unit taste gap)

    # --- segment weights & structure ---------------------------------------
    w_eth: float = value("w_eth")                   # ethical-segment weight (Gallup veg+vegan ~5%)
    accept_x: float = value("accept_x")             # cultivated taste credit (1=parity); -> taste_x = accept_x-1
    theta_free_M: float = value("theta_free_M")     # MAINSTREAM slaughter-free weight (the upside dial)
    neophobia_x: float = value("neophobia_x")       # CULTIVATED novelty attitude (utils; -=neophobia, +=neophilia)
    neophobia_p: float = value("neophobia_p")       # PLANT-BASED novelty attitude (utils; exploratory override)
    real_tissue_x: float = value("real_tissue_x")   # CULTIVATED real-tissue flag (1=premise, the asymmetry; a DIAL)
    real_tissue_p: float = value("real_tissue_p")   # PLANT-BASED real-tissue flag (0 by definition; dial for symmetry)
    health_x: float = value("health_x")             # CULTIVATED health-perception offset (utils; +healthier/-less; default 0, scenario)
    health_p: float = value("health_p")             # PLANT-BASED health-perception offset (utils; default 0, scenario)
    health_w: float = value("health_w")             # WHOLE-FOOD health POSITION (utils; +, "beans are the healthy choice")
    health_c: float = value("health_c")             # CONVENTIONAL health POSITION (utils; slightly -, the reference's health standing)
    w_realtissue_M: float = value("w_realtissue_M")  # MAINSTREAM real-tissue weight (the no-nest mechanism)
    w_realtissue_E: float = value("w_realtissue_E")  # ETHICAL real-tissue weight (~0)
    w_slaughter_E: float = value("w_slaughter_E")   # ETHICAL slaughter-free weight (large)
    w_health_M: float = value("w_health_M")         # MAINSTREAM health weight; SOLVED (replaces the whole-food intercept)
    w_health_E: float = value("w_health_E")         # ETHICAL health weight; SOLVED (the whole-food health premium pulls ethical eaters to beans)

    # --- reference-dependent loss aversion (uniform across products) -------
    loss_aversion: float = value("loss_aversion")    # premium-over-conventional penalty, every product

    # --- calibration anchors & the SEGMENT-SPECIFIC solved outside options --
    pb_share_target: float = value("pb_share_target")          # plant-based total share anchor
    pb_mainstream_frac: float = value("pb_mainstream_frac")    # share of PB buyers who are mainstream (GFI ~89%)
    wf_mainstream_target: float = value("wf_mainstream_target")  # mainstream 'meatless-by-choice' share
    calibrated: bool = False                        # True once solve_calibration has run (or pinned by hand)

    # --- DERIVED (set in __post_init__ by _derive_beta; never user inputs) ----
    beta_ref: float = field(default=0.0, repr=False)      # the shared logit price coefficient ($/kg^-1)
    anchor_price: float = field(default=0.0, repr=False)  # cultivated's own retail price = the beta anchor ($/kg)

    def __post_init__(self):
        # Two coupled solves pin the model with NO free anchor numbers:
        #  (1) the price coefficient beta is DERIVED so cultivated's own-price
        #      elasticity equals its target eps_own*cult_sub_mult AT cultivated's own
        #      modeled retail price & share (a short fixed point — see _derive_beta);
        #  (2) three cross-sectional moments are matched (solve_calibration):
        #      w_realtissue_M (mainstream PB rate = the 89% buyer split), w_health_M
        #      (mainstream whole-food rate), w_health_E (ethical PB rate).
        # No separate static habit term: habit is not identified from heterogeneity
        # here (Heckman), so it lives in the diffusion rung (adoption_timing) + the
        # long-run standing is carried by accept_x + theta_free_M (no xi_x dial).
        if not self.calibrated:
            _derive_beta(self)            # sets beta_ref + anchor_price; calibrates at the converged beta
            self.calibrated = True

    @property
    def beta_price(self) -> float:
        """Shared logit price coefficient ($/kg^-1) — DERIVED, not an input.
        Set by `_derive_beta` so cultivated's own-price elasticity equals its target
        eps_own*cult_sub_mult at cultivated's own modeled price/share. (0 only on a
        hand-built calibrated=True object until beta_ref is assigned.)"""
        return self.beta_ref


# ----------------------------------------------------------------------------
# Per-segment choice probabilities (flat multinomial logit — NO nest)
# ----------------------------------------------------------------------------
def _softmax(V):
    V = np.asarray(V, dtype=float)
    e = np.exp(V - V.max())
    return e / e.sum()


def _utilities(R, pr: DemandParams, beta, seg, *, accept_x, theta_free_M,
               tier_offset, neophobia_x, neophobia_p, income, health_x=None, health_p=None):
    """Utility vector V over the four products in segment `seg` in {'M','E'}.

    EVERY product goes through the SAME linear-in-attributes rule and the same
    softmax — no product gets a special-case term. The model is a (products x
    attributes) TABLE dotted with (segment x weights). The ONLY non-attribute constant
    is the whole-food outside option's intercept; the meats carry none. Conventional `c`
    is the reference (price_ratio 1, taste 0, intercept 0); the others relative to it:

        product   price_ratio   taste            slaughter_free  real_tissue   intercept
        w  whole  price_wf_mult taste_quality_w  1               0             xi_w (calib)
        c  conv   1 (anchor)    0 (reference)    0               1             0
        p  plant  price_pb_mult taste_quality_p  1               0             0
        x  cult   R (from cost) accept_x - 1     1               1             asc_x

    Attribute WEIGHTS are shared (q_taste, the price/loss coefficients) except the
    two that carry the segment's identity: w_slaughter (ethical values it) and
    w_realtissue (mainstream values it). The INTERCEPT of whole-food is segment-specific
    (beans are the ethical default, a rare mainstream choice). FOOD NEOPHOBIA enters
    the utility of the two NOVEL products by its own sign convention (utils; - = neophobia
    penalty, + = neophilia bonus): `neophobia_x` for cultivated (+ its per-meat-type
    authenticity offset), `neophobia_p` for plant-based. Conventional and whole-food
    (familiar) carry none.

    Two price-related terms, BOTH applied to every product by its own price:
      * BLP (Berry-Levinsohn-Pakes 1995) income term  alpha*ln(y_eff - price) -- richer
        consumers are less price-sensitive; alpha = -beta*(y_eff - p_conv) is the local
        marginal-utility-of-income normalisation AT THE REGION'S OWN y_eff (so the income
        term's price-slope equals beta there), and y_eff scales with income.
      * Reference-dependent LOSS AVERSION (canonical Tversky-Kahneman form): a discount
        (price_ratio<1) is rewarded at the UNIT rate (+1), a premium (price_ratio>1) is
        penalised at -loss_aversion, where loss_aversion = lambda IS the loss-aversion
        coefficient (lambda>=1; ~2.25 in the data, so losses loom ~2.25x larger than gains).
        Applied to every product (plant-based at 1.77x and cultivated at R alike); no
        cultivated-only cliff.
    """
    # --- the product x attribute TABLE (rows = products w, c, p, x) ----------
    price_ratio    = np.array([pr.price_wf_mult, 1.0, pr.price_pb_mult, R])
    taste          = np.array([pr.taste_quality_w, 0.0, pr.taste_quality_p, accept_x - 1.0])  # 0 = parity
    slaughter_free = np.array([1.0, 0.0, 1.0, 1.0])
    # real_tissue: whole-food 0, conventional 1 (reference), plant-based & cultivated are DIALS
    # (default p=0, x=1 — the identifying asymmetry, now adjustable for equal-footing what-ifs).
    real_tissue    = np.array([0.0, 1.0, pr.real_tissue_p, pr.real_tissue_x])
    # HEALTH PERCEPTION (utils; + = perceived healthier, - = less healthy). A named ATTRIBUTE on
    # every product, weighted by a SEGMENT-SPECIFIC health weight w_health (like slaughter-free and
    # real-tissue). Positions: whole-food health_w (+, beans are "the healthy choice"), conventional
    # health_c (slightly -, the reference's health standing), plant-based / cultivated via their
    # health_p / health_x dials (two-sided scenario, default 0). The whole-food health premium is
    # what pulls ethical eaters to whole foods over a processed veggie burger — so w_health (solved
    # in calibration) REPLACES the old free whole-food intercept xi_w: the model is now fully
    # attribute-based, with no free fitted constant on any product.
    hX = pr.health_x if health_x is None else health_x
    hP = pr.health_p if health_p is None else health_p
    health         = np.array([pr.health_w, pr.health_c, hP, hX])     # [w, c, p, x]
    # intercept per product [w, c, p, x]: NONE now on whole-food (health carries it); conventional 0;
    # plant-based neophobia; cultivated neophobia + per-tier authenticity offset.
    asc            = np.array([0.0, 0.0, neophobia_p, neophobia_x + tier_offset])

    # --- segment-specific attribute weights ---------------------------------
    if seg == "M":
        w_slaughter, w_realtissue, w_health = theta_free_M, pr.w_realtissue_M, pr.w_health_M
    else:
        w_slaughter, w_realtissue, w_health = pr.w_slaughter_E, pr.w_realtissue_E, pr.w_health_E

    # --- the SAME utility for every product ---------------------------------
    price = price_ratio * pr.p_conv
    y_eff = pr.income_ref * (income / pr.income_ref) ** pr.income_gradient
    # BLP marginal-utility-of-income normalisation: alpha is set so the income term's LOCAL
    # price-slope equals beta AT THE REGION'S OWN income, so the factor must use the SAME y_eff
    # that appears inside log1p(-price/y_eff). Using the US-anchored (income_ref - anchor_price)
    # instead made the slope = beta*(income_ref-anchor)/(y_eff-price), which blows up at low income
    # and cancelled the unit discount reward, leaving the share-vs-R curve dead flat for R<1 (and
    # the premium share plateauing/rising) in non-US regions. Normalising with y_eff (and p_conv,
    # the conventional reference price the premium is measured against) fixes the regional gradient
    # while leaving the US anchor — and every at-parity headline number — unchanged. The interactive
    # JS (build_interactive.utilities) uses this exact form; this is the source-of-truth match.
    alpha = -beta * (y_eff - pr.p_conv)
    V_price = alpha * np.log1p(-price / y_eff)                        # BLP income term (~ beta*price near ref)
    # Reference-dependent value (Tversky-Kahneman), in the CANONICAL form: a discount
    # (price_ratio < 1) is rewarded at the natural UNIT rate (+1), and a premium
    # (price_ratio > 1) is penalised at -loss_aversion, where loss_aversion = lambda IS the
    # loss-aversion coefficient (lambda >= 1; the literature value is ~2.25, so losses loom
    # ~2.25x larger than equal-sized gains). Applied to EVERY product by its own premium.
    premium = price_ratio - 1.0
    V_loss = (-pr.loss_aversion * np.maximum(0.0, premium)
              + 1.0 * np.maximum(0.0, -premium))

    return (V_price + V_loss + pr.q_taste * taste
            + w_slaughter * slaughter_free + w_realtissue * real_tissue
            + w_health * health + asc)


def _segment(R, pr: DemandParams, beta, seg, *, accept_x, theta_free_M,
             tier_offset, neophobia_x, neophobia_p, income, health_x=None, health_p=None,
             cultivated_present=True) -> dict:
    """Flat-logit shares of {w, c, p, x} in one segment. cultivated_present=False
    drops x from the choice set."""
    V = _utilities(R, pr, beta, seg, accept_x=accept_x, theta_free_M=theta_free_M,
                   tier_offset=tier_offset, neophobia_x=neophobia_x,
                   neophobia_p=neophobia_p, income=income, health_x=health_x, health_p=health_p)
    if cultivated_present:
        P = _softmax(V)
        return {"w": P[0], "c": P[1], "p": P[2], "x": P[3]}
    P = _softmax(V[:3])
    return {"w": P[0], "c": P[1], "p": P[2], "x": 0.0}


# ----------------------------------------------------------------------------
# The headline: market share of a product given the price ratio R
# ----------------------------------------------------------------------------
def share(R, pr: DemandParams, *, accept_x=None, theta_free_M=None, tier_offset=0.0,
          eps_own=None, income=None, cultivated_present=True, which="x",
          neophobia_x=None, neophobia_p=None, health_x=None, health_p=None) -> float:
    """Total market share of `which` in {w, c, p, x} (pb is an alias for p),
    mixing the two segments: share_j = w_eth*P_E(j) + (1-w_eth)*P_M(j).

    The override knobs map cleanly onto the four-product / two-segment model:
      accept_x      -> cultivated taste credit (taste_x = accept_x - 1)
      theta_free_M  -> the MAINSTREAM slaughter-free weight (lifts every no-slaughter
                       product, cultivated most because it ALSO has real-tissue)
      tier_offset   -> per-product-type authenticity addend to cultivated's utility (utils)
      neophobia_x   -> CULTIVATED novelty attitude (utils; - = neophobia, + = neophilia;
                       default pr.neophobia_x). The timing rung passes the time-varying
                       value (launch wariness decaying onto the long-run neophobia_x).
      neophobia_p   -> PLANT-BASED novelty attitude (utils; default pr.neophobia_p) — an
                       exploratory deviation from PB's calibrated position.
      health_x      -> CULTIVATED health-perception offset (utils; default pr.health_x=0).
      health_p      -> PLANT-BASED health-perception offset (utils; default pr.health_p=0).
                       Both are two-sided SCENARIO dials (like neophobia): inert at 0,
                       never re-pin the calibration.
      eps_own       -> sweeps the price coefficient beta.
      income        -> region income ($/yr) for the BLP price term (default income_ref
                       => unchanged from the US-anchored calibration). Richer = less
                       price-sensitive. Used by meat_market for the regional roll-up.
      cultivated_present=False removes cultivated (PB calibration + cannibalisation checks).
    """
    ax = pr.accept_x if accept_x is None else accept_x
    tfM = pr.theta_free_M if theta_free_M is None else theta_free_M
    eps = pr.eps_own if eps_own is None else eps_own
    # beta is the DERIVED coefficient (pr.beta_ref). It splits into an elasticity part
    # (eps_x/(p*(1-s)), proportional to the elasticity target) and the loss-aversion
    # compensation (loss_aversion/p_conv). An eps_own override (e.g. the per-tier
    # multipliers) scales ONLY the elasticity part, leaving the loss-aversion
    # compensation fixed, so a tier's TOTAL elasticity scales as intended.
    lam_slope = pr.loss_aversion / pr.p_conv
    beta = (pr.beta_ref - lam_slope) * (eps / pr.eps_own) + lam_slope
    inc = pr.income_ref if income is None else income      # default = reference income (unchanged)
    # MONOTONICITY GUARD (income-aware). On the discount side (R<1) the loss term is off, so the
    # price response is the BLP income term (local slope ~ alpha/(y_eff-price)) plus the unit gain
    # reward. A cheaper product must never lose share, i.e. dV/d(price_ratio) <= 0, which requires
    #   beta <= (y_eff - p_conv) / ((income_ref - anchor_price) * p_conv).
    # This bound TIGHTENS at low income (the BLP slope is steeper there), so a fixed 1/p_conv cap
    # leaks for poor regions (e.g. global income 24k: cut tier rose toward parity). Cap per-call.
    y_eff_g = pr.income_ref * (inc / pr.income_ref) ** pr.income_gradient
    denom = (pr.income_ref - pr.anchor_price) * pr.p_conv
    if denom > 0:
        beta_cap = (y_eff_g - pr.p_conv) / denom - 1e-4
        beta = min(beta, beta_cap)
    nbx = pr.neophobia_x if neophobia_x is None else neophobia_x   # cultivated novelty attitude
    nbp = pr.neophobia_p if neophobia_p is None else neophobia_p   # plant-based novelty attitude

    M = _segment(R, pr, beta, "M", accept_x=ax, theta_free_M=tfM, tier_offset=tier_offset,
                 neophobia_x=nbx, neophobia_p=nbp, income=inc, health_x=health_x, health_p=health_p,
                 cultivated_present=cultivated_present)
    E = _segment(R, pr, beta, "E", accept_x=ax, theta_free_M=tfM, tier_offset=tier_offset,
                 neophobia_x=nbx, neophobia_p=nbp, income=inc, health_x=health_x, health_p=health_p,
                 cultivated_present=cultivated_present)
    w = pr.w_eth
    key = "p" if which == "pb" else which
    return float(w * E[key] + (1.0 - w) * M[key])


def _rate(pr: DemandParams, seg: str, which: str) -> float:
    """One segment's share of `which` in {w,c,p,x} at neutral parity, cultivated
    absent and at reference income — the moment the calibration solves target."""
    s = _segment(1.0, pr, pr.beta_price, seg, accept_x=1.0, theta_free_M=0.0,
                 tier_offset=0.0, neophobia_x=0.0, neophobia_p=0.0, income=pr.income_ref,
                 health_x=0.0, health_p=0.0, cultivated_present=False)
    return s[which]


def solve_calibration(pr: DemandParams, iters: int = 70, rounds: int = 12):
    """Pin the demand model to the cross-sectional anchors with three monotone
    1-D bisections (one equation each):

      * w_realtissue_M  -> mainstream plant-based rate = pb_mainstream_frac of PB
        buyers (GFI ~89%) — i.e. the MAINSTREAM, not the 5% ethical core, carries PB.
      * w_health_M      -> mainstream whole-food rate = wf_mainstream_target.
      * w_health_E      -> ethical plant-based rate = the residual (~11%) of PB.

    The HEALTH weight (segment-specific) is what makes whole foods the default for the
    health- and ethically-minded; it REPLACES the old free whole-food intercept xi_w, so
    the model now carries no free fitted constant — every product's standing is a named
    attribute (price, taste, slaughter-free, real-tissue, health) times a weight. With the
    whole-food health POSITION (health_w > 0) fixed, solving the segment health WEIGHT is
    equivalent to (and identified exactly as) solving the old intercept.

    The first two share the mainstream normalisation, so they run in a short coordinate
    descent; the ethical one is independent. Together they reproduce the total PB share and
    the mainstream/ethical split by construction. (No separate static habit term — see
    __post_init__.)
    """
    we = pr.w_eth
    pb_M_target = pr.pb_mainstream_frac * pr.pb_share_target / (1.0 - we)        # mainstream PB rate
    pb_E_target = (1.0 - pr.pb_mainstream_frac) * pr.pb_share_target / we        # ethical PB rate
    wf_M_target = pr.wf_mainstream_target

    # --- mainstream block: (w_realtissue_M, w_health_M) for (PB_M, WF_M) ---
    for _ in range(rounds):
        lo, hi = 0.0, 8.0                                # PB_M decreases in w_realtissue_M
        for _ in range(iters):
            mid = 0.5 * (lo + hi); pr.w_realtissue_M = mid
            if _rate(pr, "M", "p") > pb_M_target: lo = mid
            else: hi = mid
        pr.w_realtissue_M = 0.5 * (lo + hi)
        lo, hi = 0.0, 16.0                               # WF_M increases in w_health_M (health_w > 0)
        for _ in range(iters):
            mid = 0.5 * (lo + hi); pr.w_health_M = mid
            if _rate(pr, "M", "w") > wf_M_target: hi = mid
            else: lo = mid
        pr.w_health_M = 0.5 * (lo + hi)

    # --- ethical block: w_health_E for the ethical PB rate (PB_E decreases in w_health_E) ---
    lo, hi = 0.0, 16.0
    for _ in range(iters):
        mid = 0.5 * (lo + hi); pr.w_health_E = mid
        if _rate(pr, "E", "p") > pb_E_target: lo = mid
        else: hi = mid
    pr.w_health_E = 0.5 * (lo + hi)
    return pr


def _derive_beta(pr: DemandParams, iters: int = 40, tol: float = 1e-9) -> None:
    """Set pr.beta_ref (the shared price coefficient) and pr.anchor_price with NO
    hand-chosen price or share anchor — beta tracks the model's own parameters.

    The behavioural primitive is cultivated's OWN-PRICE ELASTICITY,
        eps_x = eps_own * cult_sub_mult,
    i.e. meat's measured own-price elasticity, steepened because conventional is a
    near-perfect substitute. The own-price elasticity is a property of the WHOLE
    price response, and in this model price enters utility through TWO channels:
      * the BLP income term, whose local slope dV/dprice is `beta`; and
      * the reference-dependent loss-aversion term -loss_aversion*(price_ratio-1),
        whose slope dV/dprice is -loss_aversion/p_conv on the loss side (price above
        the conventional reference — which is where the anchor R_today>1 sits).
    So the TOTAL semi-elasticity at the anchor is (beta - loss_aversion/p_conv), and
    the logit own-price elasticity identity reads
        eps_x = (beta - loss_aversion/p_conv) * price_x * (1 - s_x).
    We solve `beta` so that this TOTAL response reproduces eps_x at cultivated's OWN
    operating point (earlier versions omitted the loss-aversion channel, so the
    realised elasticity came out ~2x the target — the double-counting fix):
      * price  = cultivated's own retail price  p_anchor = biomass_cost + markup_add,
        DERIVED from the cost model (so it tracks media_price, overhead, markup, p_conv);
      * share  = cultivated's own neutral modeled share at that price (s_anchor), which
        itself depends on beta -> a short FIXED POINT (converges in ~3 steps).
    Nothing here is a free constant: move any cost input and p_anchor moves; move
    eps_own or cult_sub_mult and the target moves; beta follows. loss_aversion now
    only shapes the KINK/asymmetry at parity (its intended job), not the elasticity
    LEVEL — that is set by eps_own*cult_sub_mult, as documented.

        beta = eps_x / (p_anchor * (1 - s_anchor))  +  loss_aversion / p_conv
    """
    cp = CostParams(p_conv=pr.p_conv)
    pr.anchor_price = float(biomass_cost(cp, value("media_price"), 1.0) + cp.markup_add)
    R_today = pr.anchor_price / pr.p_conv
    eps_x = pr.eps_own * pr.cult_sub_mult
    # The loss-aversion term adds a second price-sensitivity channel; at the anchor
    # (R_today > 1, the loss side) its semi-elasticity is loss_aversion/p_conv, which
    # `beta` must absorb so the TOTAL realised elasticity equals the target eps_x.
    lam_slope = pr.loss_aversion / pr.p_conv
    # MONOTONICITY GUARD: on the DISCOUNT side (R<1) the loss-aversion term is off, so the
    # curve's slope there is governed by the BLP coefficient `beta` plus the unit gain reward
    # (slope -1/p_conv). A cheaper product must never lose share, i.e. the discount-side slope
    # must stay negative, which requires beta < 1/p_conv. At large loss_aversion the add-back
    # would push beta past that and make the share RISE toward parity (economically wrong), so
    # we cap beta just below 1/p_conv. This is inert at the default (beta<<cap) and only bites
    # in the high-loss_aversion tail, where it lets the loss side keep steepening while the
    # discount side stays monotone.
    beta_cap = 1.0 / pr.p_conv - 1e-3
    s = 0.0
    for _ in range(iters):
        pr.beta_ref = min(beta_cap, eps_x / (pr.anchor_price * (1.0 - s)) + lam_slope)
        solve_calibration(pr)                                         # recalibrate at this beta
        s_new = share(R_today, pr, accept_x=1.0, theta_free_M=0.0,    # cultivated's own neutral share
                      neophobia_x=0.0, neophobia_p=0.0)               # anchor beta at neutral; neophobia is a post-hoc override
        if abs(s_new - s) < tol:
            s = s_new
            break
        s = s_new
    pr.beta_ref = min(beta_cap, eps_x / (pr.anchor_price * (1.0 - s)) + lam_slope)
    solve_calibration(pr)                                             # final calibration at converged beta


def share_band(R: float, pr: DemandParams):
    """(lo, central, hi) LONG-RUN cultivated share across the acceptance dials
    (taste-acceptance accept_x: friction->full, slaughter-free value theta_free_M:
    indifferent->valued) and elasticity. Central = neutral (accept_x=1,
    theta_free_M=0 = cultivated treated as equivalent to conventional)."""
    central = share(R, pr, accept_x=1.0, theta_free_M=0.0)
    grid = [share(R, pr, accept_x=a, theta_free_M=f, eps_own=e)
            for a in (0.6, 0.8, 1.0, 1.1) for f in (0.0, 0.5, 1.0, 1.5)
            for e in (-1.4, -0.9, -0.5)]
    return min(grid), central, max(grid)


# ----------------------------------------------------------------------------
# Cross-category VALIDATION: plant-based MILK (the contrast case)
# ----------------------------------------------------------------------------
def pb_milk_check(pr: DemandParams) -> float:
    """Out-of-sample sanity check on the SHARED taste/price machinery. Holding
    q_taste, beta (the derived price coefficient) and w_eth FIXED at their meat-
    calibrated values, swap ONLY the product POSITIONS to plant-based milk's empirical
    ones and read its share. The same parameters that make PB-MEAT fail (premium price,
    taste deficit, big real-tissue gap, cheap strong outside option) make PB-MILK
    succeed when those positions improve — milk reached functional/taste parity in key
    uses (coffee/cereal) at ~price parity, the "not-real" gap is small, and there is no
    cheap whole-food substitute for milk-in-coffee. Returns the predicted plant-milk
    share (observed ~15%, GFI/SPINS 2024)."""
    milk = DemandParams(
        price_pb_mult=1.0,                 # near price-parity in use (small splash in coffee)
        taste_quality_p=0.0,               # taste/functional parity in key uses (barista oat/soy)
        w_realtissue_M=2.1,                # milk's own 'not real dairy' gap (smaller relative effect: price/taste parity)
        price_wf_mult=1.2,                 # NO cheap whole-food substitute for milk-in-coffee -> weak outside
        # WEAK outside option (fixed, not solved): no healthy whole-food rival to milk-in-coffee, so the
        # whole-food slot carries a NEGATIVE health position (unit weights) -> reproduces the old fixed
        # K_wholefood=-2.0 outside-option intercept. health_c=0 because DAIRY (not red meat) is milk's
        # reference, so the conventional product carries no health penalty in this contrast.
        health_w=-2.0, health_c=0.0, w_health_M=1.0, w_health_E=1.0,
        calibrated=True,                   # do NOT run the meat calibration solve on the milk world
    )
    milk.beta_ref = pr.beta_ref            # reuse the SAME (meat-derived) price coefficient + its anchor
    milk.anchor_price = pr.anchor_price
    # plant share = "p" with the cultivated slot absent (milk has no cultivated product)
    return share(1.0, milk, cultivated_present=False, which="p")


# ----------------------------------------------------------------------------
# DEMAND VALIDATION: the implied at-parity elasticity vs the one measured for cultivated
# ----------------------------------------------------------------------------
# The only direct price-variation data on cultivated meat is Van Loo, Caputo & Lusk 2020
# (Food Policy 95:101931): a US choice experiment that priced lab-grown across SIX levels
# ($2.99-$10.49/lb), so it identifies lab-grown's OWN-PRICE ELASTICITY AT PARITY. Their two
# models bracket it: the (homogeneous) conditional logit price coeff -0.178/$ implies
# eps_lab ~ -0.84 at the $5/lb parity point; the random-parameter logit mean -0.72/$ implies
# eps_lab ~ -3.4 (heterogeneity-driven: lab's random-coeff SD ~3-4.6 is LARGER than its mean,
# i.e. ~half the population is positive on lab-grown, half negative). So the data bracket is
#   eps_lab(at parity, cold survey) in [-3.4, -0.84].
# kappa (cult_sub_mult) is the model's flat-logit stand-in for exactly that real_tissue
# heterogeneity, so this is the moment that DISCIPLINES it: the model's implied at-parity cold
# elasticity should land inside the bracket. It does at the default kappa=4 (-0.95). The check
# is reported (like the PB-milk check) rather than re-solved, because the bracket is wide and
# kappa stays a SWEPT judgement dial — Lusk grounds its RANGE, it does not point-pin it.
#
# CAVEAT (the residual, by design): Lusk measures the elasticity AT PARITY; the model's headline
# elasticity target eps_x = eps_own*kappa is at cultivated's OPERATING POINT (R~2.4), where the
# model's (BLP+kink) elasticity is steeper. Matching the at-parity bracket therefore grounds the
# SHAPE near parity but the -3.6 at R~2.4 remains a functional-form EXTRAPOLATION — no choice
# experiment has priced cultivated at ~2.4x conventional. See METHODS / the limitations.
LUSK_ELAS_BRACKET = (-3.4, -0.84)   # at-parity, cold-survey own-price elasticity of lab-grown


def lusk_at_parity_elasticity(pr: DemandParams, R: float = 1.0, h: float = 1e-4) -> float:
    """The model's implied COLD-START at-parity own-price elasticity of cultivated — the
    quantity Van Loo/Caputo/Lusk 2020 measured. Central-difference d ln(share)/d ln(price) at
    parity, evaluated at the cold-start novelty (neophobia_x0, the survey condition: cultivated
    is unfamiliar), with neutral standing (accept_x=1, theta_free_M=0)."""
    nx0 = value("neophobia_x0")
    f = lambda r: share(r, pr, accept_x=1.0, theta_free_M=0.0, neophobia_x=nx0)
    s0 = f(R)
    return float((f(R * (1.0 + h)) - f(R * (1.0 - h))) / (2.0 * h * s0))


def lusk_elasticity_check(pr: DemandParams) -> dict:
    """Validate kappa against the Lusk bracket: return the model's implied at-parity cold
    elasticity, the data bracket, and whether it sits inside. Reported, not re-solved."""
    e = lusk_at_parity_elasticity(pr)
    lo, hi = LUSK_ELAS_BRACKET
    return {"implied": e, "bracket": LUSK_ELAS_BRACKET, "inside": lo <= e <= hi}


def _milk_params(pr: DemandParams) -> DemandParams:
    """The plant-based MILK world (same object pb_milk_check builds) — exposed so the
    figure can read its positions."""
    milk = DemandParams(price_pb_mult=1.0, taste_quality_p=0.0, w_realtissue_M=2.1,
                        price_wf_mult=1.2, health_w=-2.0, health_c=0.0, w_health_M=1.0, w_health_E=1.0,
                        calibrated=True)
    milk.beta_ref = pr.beta_ref
    milk.anchor_price = pr.anchor_price
    return milk


def fig_pb_milk_vs_meat(pr: DemandParams, outdir, fmts) -> None:
    """DEPICT the cross-category validation: plant-based MILK vs plant-based MEAT.
    The SAME shared machinery (price coefficient beta, taste weight q_taste, the 5%
    ethical segment) runs both — only the four PRODUCT POSITIONS differ. Milk wins
    (~15%) where meat fails (~1%) because it reaches price & taste parity in its key
    uses AND has no cheap whole-food substitute, even though its 'not-real' gap is the
    same size. Left: the positions, side by side. Right: the share each yields."""
    milk = _milk_params(pr)
    pb_meat = share(1.0, pr, cultivated_present=False, which="p") * 100
    pb_milk = pb_milk_check(pr) * 100

    # the four positions that DIFFER (conventional/dairy = the reference each competes with)
    labels = ["price\n(× reference)", "taste\n(1 = real)", "“not-real”\npenalty (utils)",
              "cheap rival\n(outside-option ×)"]
    meat_pos = [pr.price_pb_mult, 1 + pr.taste_quality_p, pr.w_realtissue_M, pr.price_wf_mult]
    milk_pos = [milk.price_pb_mult, 1 + milk.taste_quality_p, milk.w_realtissue_M, milk.price_wf_mult]

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.8, 4.2), gridspec_kw={"width_ratios": [1.7, 1]})
    y = np.arange(len(labels))[::-1]
    bw = 0.38
    axL.barh(y + bw/2, meat_pos, bw, color="#029E73", label=f"PB-MEAT  → {pb_meat:.1f}%")
    axL.barh(y - bw/2, milk_pos, bw, color="#0173B2", label=f"PB-MILK  → {pb_milk:.0f}%")
    for yi, mv, kv in zip(y, meat_pos, milk_pos):
        axL.text(mv + 0.04, yi + bw/2, f"{mv:.2f}", va="center", fontsize=7.5, color="#016b4e")
        axL.text(kv + 0.04, yi - bw/2, f"{kv:.2f}", va="center", fontsize=7.5, color="#015080")
    axL.axvline(1.0, ls=":", lw=1.0, color="0.5")
    axL.text(1.02, -0.62, "parity /\nreference", fontsize=6.5, color="0.5", va="bottom")
    axL.set_yticks(y); axL.set_yticklabels(labels, fontsize=8.5)
    axL.set_xlabel("position (× the reference price, or utils)")
    axL.set_title("Same machinery, different positions", fontsize=10)
    axL.legend(fontsize=8, frameon=False, loc="lower right")

    # right: the resulting shares (with the observed anchors)
    axR.bar([0, 1], [pb_meat, pb_milk], color=["#029E73", "#0173B2"], width=0.6, alpha=0.9)
    for x, v, obs in [(0, pb_meat, "obs ~1%"), (1, pb_milk, "obs ~15%")]:
        axR.text(x, v + 0.4, f"{v:.1f}%", ha="center", fontsize=10, fontweight="bold")
        axR.text(x, v + 1.6, obs, ha="center", fontsize=7.5, color="0.45")
    axR.set_xticks([0, 1]); axR.set_xticklabels(["PB-meat", "PB-milk"], fontsize=9)
    axR.set_ylim(0, max(pb_milk, 15) * 1.25)
    axR.set_ylabel(r"category share (\%)")
    axR.set_title("…reproduces both outcomes", fontsize=10)
    fig.suptitle("Why plant-based MILK succeeds where plant-based MEAT stalls (same model, swapped positions)",
                 y=1.01, fontsize=10.5)
    _save(fig, outdir, "pb_milk_vs_meat", fmts)


# ----------------------------------------------------------------------------
# Demand-calibration robustness: how much do the JUDGEMENT anchors move the answer?
# ----------------------------------------------------------------------------
# The honest response to "these demand parameters are calibrated/assumed, not estimated"
# is to SHOW their leverage (sensitivity), not to add unidentified structure. For each
# judgement anchor a referee would question, re-solve the calibration at its prior lo/hi
# and report the central (neutral-standing) cultivated share, others held at mode.
CALIBRATION_ANCHORS = ("cult_sub_mult", "loss_aversion", "pb_mainstream_frac",
                       "w_eth", "wf_mainstream_target")


def calibration_robustness(pr: DemandParams, R: float):
    rows = []
    for name in CALIBRATION_ANCHORS:
        _, lo, hi, _mode, _ = prior(name)
        s_lo = share(R, DemandParams(**{name: lo}), accept_x=1.0, theta_free_M=0.0) * 100
        s_hi = share(R, DemandParams(**{name: hi}), accept_x=1.0, theta_free_M=0.0) * 100
        rows.append((name, lo, hi, min(s_lo, s_hi), max(s_lo, s_hi)))
    return sorted(rows, key=lambda r: -(r[4] - r[3]))            # widest-swing first


# ----------------------------------------------------------------------------
# Report — cost scenarios -> share, plus the calibration self-checks
# ----------------------------------------------------------------------------
def summarise(pr: DemandParams) -> None:
    cp = CostParams(p_conv=pr.p_conv)
    print(f"  4-product / 2-segment logit:  beta_price = {pr.beta_price:.3f} $/kg^-1 "
          f"(eps_own={pr.eps_own:+.2f} x cult_sub_mult={pr.cult_sub_mult:g});  w_eth = {pr.w_eth*100:.0f}%")
    print(f"  solved: w_realtissue_M = {pr.w_realtissue_M:.2f}  w_health_M = {pr.w_health_M:.2f}  "
          f"w_health_E = {pr.w_health_E:.2f}  (health positions: wf={pr.health_w:+.1f} conv={pr.health_c:+.1f})")
    scenarios = [
        ("Pasitka base (0.63 $/L)",      cost_ratio(biomass_cost(cp, 0.63, 1.0), cp)),
        ("medium -> 0.2 $/L",            cost_ratio(biomass_cost(cp, 0.20, 1.0), cp)),
        ("both (0.2 $/L + CHO cells)",   cost_ratio(biomass_cost(cp, 0.20, cp.eff_best), cp)),
        ("cost floor (central)",         cost_ratio(cost_floor(cp), cp)),
        ("price parity",                 1.0),
    ]
    print("  scenario                          R       cultivated share (band)")
    for name, R in scenarios:
        lo, ce, hi = share_band(R, pr)
        print(f"    {name:<30} {R:4.2f}     {ce*100:4.1f}%   ({lo*100:4.1f}-{hi*100:4.1f}%)")

    print("\n  --- calibration self-checks ---")
    pb = share(1.0, pr, cultivated_present=False, which="p") * 100
    wf = share(1.0, pr, cultivated_present=False, which="w") * 100
    print(f"  [1] plant-based share (cultivated absent) = {pb:.2f}%  (target "
          f"{pr.pb_share_target*100:.1f}%);  whole-food outside option = {wf:.1f}%  "
          f"(>> PB: the outside option dominates non-meat eating)")
    # [1b] PB buyer composition: the MAINSTREAM (flexitarians) should carry ~89% of PB (GFI), not the
    # 5% ethical core. This is what pins w_realtissue_M (the reduced-form mainstream not-real-meat standing).
    pbM = (1 - pr.w_eth) * _rate(pr, "M", "p"); pbE = pr.w_eth * _rate(pr, "E", "p")
    print(f"  [1b] PB buyer split: mainstream {pbM/(pbM+pbE)*100:.0f}% / ethical {pbE/(pbM+pbE)*100:.0f}%  "
          f"(target mainstream {pr.pb_mainstream_frac*100:.0f}%, GFI);  mainstream whole-food = "
          f"{_rate(pr,'M','w')*100:.0f}% (target {pr.wf_mainstream_target*100:.0f}%)")

    print("  [2] cultivated share at parity by the acceptance dials (NO baked-in stance):")
    print("      (a) taste-acceptance accept_x (theta_free_M=0):")
    for a, lbl in [(0.6, "strong taste friction"), (0.8, "modest friction"),
                   (1.0, "EQUIVALENT real meat"), (1.1, "seen as better")]:
        print(f"          accept_x={a:.1f}: {share(1.0, pr, accept_x=a, theta_free_M=0.0)*100:5.1f}%   {lbl}")
    print("      (b) slaughter-free value theta_free_M (accept_x=1):")
    for f, lbl in [(0.0, "indifferent"), (0.5, "mild clean-meat pull"),
                   (1.0, "values no-slaughter"), (1.5, "strong clean-meat pull")]:
        print(f"          theta_free_M={f:.1f}: {share(1.0, pr, accept_x=1.0, theta_free_M=f)*100:5.1f}%   {lbl}")

    # cannibalisation: introducing cultivated at parity draws from CONVENTIONAL (the
    # no-nest IIA proof) — plant-based and whole-food barely move.
    def s(which, present):
        return share(1.0, pr, accept_x=1.0, theta_free_M=0.0,
                     cultivated_present=present, which=which) * 100
    c0, c1 = s("c", False), s("c", True)
    p0, p1 = s("p", False), s("p", True)
    w0, w1 = s("w", False), s("w", True)
    x1 = s("x", True)
    print(f"  [3] cannibalisation at parity (neutral): cultivated takes {x1:.1f}% from --")
    print(f"          conventional {c0:.1f}->{c1:.1f}%  ({c1-c0:+.1f} pp)   <- almost all of it")
    print(f"          plant-based  {p0:.2f}->{p1:.2f}%  ({p1-p0:+.2f} pp)")
    print(f"          whole-food   {w0:.1f}->{w1:.1f}%  ({w1-w0:+.1f} pp)")
    print("        -> draws from CONVENTIONAL (real-meat heterogeneity, NO nest)")

    # The ethical segment as an early adopter — a data-driven FINDING, not an assumption.
    # It values slaughter-free, but its demand is largely met by CHEAP whole foods, so it is
    # only a MODEST cultivated adopter: the same buyer data that pins ethical plant-based low
    # (11% of PB buyers) implies ethical consumers won't pay a big cultivated PREMIUM either —
    # beans out-compete expensive cultivated even for the ethically motivated.
    exr = lambda R: _segment(R, pr, pr.beta_price, "E", accept_x=1.0, theta_free_M=0.0,
                             tier_offset=0.0, neophobia_x=0.0, neophobia_p=0.0, income=pr.income_ref)["x"] * 100
    print(f"  [3b] ethical-segment cultivated rate: {exr(1.0):.0f}% at parity, {exr(1.6):.0f}% at R=1.6 "
          f"-> competes with cheap whole-foods, so a MODEST (not dominant) early adopter")

    # cross-category validation: plant-based MILK with the SAME taste/price machinery
    milk = pb_milk_check(pr) * 100
    print(f"  [4] PB-MILK validation (same shared coefficients, milk-appropriate product positions): "
          f"{milk:.0f}%  (observed ~15%; vs PB-meat ~1%)")
    print("      -> the SAME logit/price/taste machinery reproduces milk's success AND meat's failure")

    # kappa validation: the model's implied at-parity cold elasticity vs the only direct
    # price-variation data on cultivated meat (Van Loo/Caputo/Lusk 2020). Grounds kappa's RANGE.
    le = lusk_elasticity_check(pr)
    lo, hi = le["bracket"]
    print(f"  [4b] kappa validation (cult_sub_mult={pr.cult_sub_mult:g}): implied at-parity cold own-price "
          f"elasticity = {le['implied']:.2f}  vs Lusk 2020 measured [{lo:g}, {hi:g}]: "
          f"{'INSIDE' if le['inside'] else 'OUTSIDE'}")
    print("      -> the one DCE that priced cultivated across 6 levels brackets the at-parity elasticity;")
    print("         kappa stays swept (the bracket is wide), but the data grounds its range, not a heuristic.")

    # PLANT-BASED AT FULL PARITY (cultivated absent), holding the calibrated standing:
    # with price+taste equalised, the only thing left penalising plant-based in the
    # mainstream is the (calibrated) reduced-form standing w_realtissue_M. replace()
    # keeps the solved values (no re-solve), changing ONLY PB's price/taste to parity.
    pbp = replace(pr, price_pb_mult=1.0, taste_quality_p=0.0)
    pb_par = _segment(1.0, pbp, pbp.beta_price, "M", accept_x=1.0, theta_free_M=0.0,
                      tier_offset=0.0, neophobia_x=0.0, neophobia_p=0.0, income=pbp.income_ref,
                      cultivated_present=False)["p"] * 100
    print(f"  [5] plant-based at FULL price+taste parity (gen-pop mainstream) = {pb_par:.0f}%  "
          f"(structural prediction, NOT fitted)")
    print("      ordering at parity: conventional > cultivated (escapes the penalty, real tissue) > "
          "plant-based.")
    print("      (UCLA saw ~26% PB at parity, but that sample likely over-weights ethical/PB-friendly")
    print("       diners + captive dining; we pin to the GFI buyer split, not to UCLA.)")

    # income channel: richer consumers are less price-sensitive (BLP log term)
    rx = cost_ratio(biomass_cost(cp, 0.63, 1.0), cp)            # Pasitka-base R (~2.4)
    print(f"  [income] cultivated share at R={rx:.2f} by region income (phi={pr.income_gradient:g}):")
    for inc, lbl in [(85810, "US $86k"), (27105, "China $27k"), (6440, "Nigeria $6.4k")]:
        si = share(rx, pr, income=inc) * 100
        print(f"          income={lbl:<12} {si:4.1f}%   (lower income -> more price-sensitive)")

    # [6] demand-calibration ROBUSTNESS at the LIKELY operating point (R~2.4, today's
    # cost), where the premium is large and cult_sub_mult has the most leverage.
    base = share(rx, pr, accept_x=1.0, theta_free_M=0.0) * 100
    print(f"  [6] demand-calibration robustness — central share at R={rx:.2f} "
          f"(base {base:.1f}%), each anchor swept lo<->hi & RE-SOLVED (widest first):")
    for name, lo, hi, s_lo, s_hi in calibration_robustness(pr, rx):
        print(f"        {name:<20} [{lo:g}..{hi:g}]: {s_lo:4.1f}% -> {s_hi:4.1f}%  (swing {s_hi-s_lo:4.1f} pp)")
    print("      -> these are calibrated/judged, not estimated; the model is a CALIBRATED scenario")
    print("         (partial-equilibrium) demand model, so Output 2 is a band, not a forecast.")


# ----------------------------------------------------------------------------
# Figure: shares vs R — cultivated band + the other three products
# ----------------------------------------------------------------------------
def fig_share_vs_ratio(pr: DemandParams, outdir, fmts) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    ax.set_ylim(0, 95)

    R_lo = np.linspace(0.6, 1.0, 120)
    R_hi = np.linspace(1.0001, 3.0, 220)
    # neutral-standing central shares of the four products + the cultivated band
    colours = {"c": "#DE8F05", "p": "#029E73", "w": "#949494", "x": "#0173B2"}
    labels = {"c": "conventional", "p": "plant-based", "w": "whole-food (outside)",
              "x": "cultivated (central)"}
    for i, R in enumerate((R_lo, R_hi)):
        lo = np.array([share_band(r, pr)[0] * 100 for r in R])
        hi = np.array([share_band(r, pr)[2] * 100 for r in R])
        ax.fill_between(R, lo, hi, color=colours["x"], alpha=0.15,
                        label="cultivated range: friction $\\to$ preferred" if i == 0 else None)
        for which in ("c", "p", "w", "x"):
            y = np.array([share(r, pr, accept_x=1.0, theta_free_M=0.0, which=which) * 100 for r in R])
            ax.plot(R, y, color=colours[which], lw=2.2 if which == "x" else 1.4,
                    ls="-" if which == "x" else "--",
                    label=labels[which] if i == 0 else None)

    ax.axvline(1.0, ls="--", lw=1.0, color="0.35")
    ax.annotate("parity\n(R=1)", xy=(1.0, 60), xytext=(1.28, 74),
                fontsize=7.5, color="0.35", ha="center",
                arrowprops=dict(arrowstyle="->", color="0.5", lw=0.8))

    cp = CostParams(p_conv=pr.p_conv)
    for lbl, R in [("today\n(Pasitka)", cost_ratio(biomass_cost(cp, 0.63, 1.0), cp)),
                   ("optimistic\ncost", cost_ratio(biomass_cost(cp, 0.20, cp.eff_best), cp)),
                   ("cost\nfloor", cost_ratio(cost_floor(cp), cp))]:
        ax.axvline(R, ls=":", lw=0.7, color="0.7")
        ax.text(R, 93, lbl, fontsize=6.5, color="0.5", ha="center", va="top")

    ax.set_xlabel(r"Price ratio  $R = p_{\rm cult}/p_{\rm conv}$  (lower = cheaper vs conventional)")
    ax.set_ylabel(r"Share within the meat category (\%)")
    ax.set_title("Market shares vs the price ratio (two-segment, four-product choice model)")
    ax.legend(fontsize=7.5, frameon=False, loc="center right")
    _save(fig, outdir, "share_vs_ratio", fmts)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outdir", default="figures")
    ap.add_argument("--no-latex", action="store_true")
    ap.add_argument("--formats", default="png,pdf")
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

    setup_style(use_latex=not args.no_latex)
    fmts = [f.strip() for f in args.formats.split(",") if f.strip()]
    pr = DemandParams()

    print("market_share — two-segment, four-product choice model:")
    summarise(pr)
    fig_share_vs_ratio(pr, args.outdir, fmts)
    fig_pb_milk_vs_meat(pr, args.outdir, fmts)
    print("Done.")
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
