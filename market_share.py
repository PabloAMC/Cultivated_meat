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
(segment x weights), plus an alternative-specific constant (ASC) per product:

    V_sj = V_price(price_j, income)        # BLP income term (richer = less price-sensitive)
         - loss_aversion * max(0, price_ratio_j - 1)              # premium penalty (loss side)
         + (loss_aversion / 2.25) * max(0, 1 - price_ratio_j)     # discount reward (gain side)
         + q_taste * taste_j
         + w_slaughter[s] * slaughter_j  +  w_realtissue[s] * real_tissue_j
         + asc_j[s]
    P_sj = softmax_j(V_sj)

No product gets a special-case term: plant-based and cultivated are treated by the
SAME two-sided, reference-dependent rule (penalised for a premium, rewarded for a
discount, with the loss side ~2.25x steeper — Tversky-Kahneman loss aversion).
Conventional `c` is the reference (price_ratio 1, taste 0, ASC 0); see the attribute
table in `_utilities`.

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
OWN-PRICE ELASTICITY eps_x = eps_own * cult_sub_mult (meat's measured -0.9, steepened ~3x
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
are flexitarians, not the 5% ethical core); the SEGMENT-SPECIFIC whole-food ASCs
K_wholefood_M / K_wholefood_E so the mainstream meatless rate and the residual ethical PB
rate match (total PB ~1.2%). w_realtissue_M is a REDUCED-FORM standing (real-tissue
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
  * ASC             : alternative-specific constant — a product's baseline appeal beyond
    its attributes (conventional = 0, the reference).
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
from inputs import value, prior
from cost_model import (
    CostParams, biomass_cost, cost_floor, ratio as cost_ratio,
)


# product order used throughout: whole-food, conventional, plant-based, cultivated
PRODUCTS = ("w", "c", "p", "x")

# Loss-aversion asymmetry: how much more a premium (price ABOVE the conventional
# reference) hurts than an equal discount (price BELOW it) helps. The canonical
# Tversky-Kahneman (1992) median estimate is lambda ~ 2.25 (losses loom ~2.25x
# larger than gains). The reference-dependent term is two-sided (it rewards
# discounts AND penalises premiums), but STEEPER on the loss side by this ratio.
LOSS_AVERSION_RATIO = 2.25


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
    price_pb_mult: float = value("price_pb_mult")   # plant-based price premium (x p_conv)
    price_wf_mult: float = value("price_wf_mult")   # whole-food price (x p_conv) — cheap
    taste_quality_p: float = value("taste_quality_p")  # plant-based average taste deficit (norm, 0=parity)
    taste_quality_w: float = value("taste_quality_w")  # whole-food taste AS A MEAT SUBSTITUTE (norm, 0=parity)
    q_taste: float = value("q_taste")               # taste-utility weight (utils per unit taste gap)

    # --- segment weights & structure ---------------------------------------
    w_eth: float = value("w_eth")                   # ethical-segment weight (Gallup veg+vegan ~5%)
    accept_x: float = value("accept_x")             # cultivated taste credit (1=parity); -> taste_x = accept_x-1
    theta_free_M: float = value("theta_free_M")     # MAINSTREAM slaughter-free weight (the upside dial)
    w_realtissue_M: float = value("w_realtissue_M")  # MAINSTREAM real-tissue weight (the no-nest mechanism)
    w_realtissue_E: float = value("w_realtissue_E")  # ETHICAL real-tissue weight (~0)
    w_slaughter_E: float = value("w_slaughter_E")   # ETHICAL slaughter-free weight (large)

    # --- reference-dependent loss aversion (uniform across products) -------
    loss_aversion: float = value("loss_aversion")    # premium-over-conventional penalty, every product

    # --- calibration anchors & the SEGMENT-SPECIFIC solved outside options --
    pb_share_target: float = value("pb_share_target")          # plant-based total share anchor
    pb_mainstream_frac: float = value("pb_mainstream_frac")    # share of PB buyers who are mainstream (GFI ~89%)
    wf_mainstream_target: float = value("wf_mainstream_target")  # mainstream 'meatless-by-choice' share
    K_wholefood_M: float = value("K_wholefood_M")   # mainstream whole-food intercept; SOLVED
    K_wholefood_E: float = value("K_wholefood")     # ethical whole-food intercept; SOLVED
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
        #      w_realtissue_M (mainstream PB rate = the 89% buyer split), K_wholefood_M
        #      (mainstream whole-food rate), K_wholefood_E (ethical PB rate).
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
               tier_offset, neophobia, income):
    """Utility vector V over the four products in segment `seg` in {'M','E'}.

    EVERY product goes through the SAME linear-in-attributes rule and the same
    softmax — no product gets a special-case term. The model is a (products x
    attributes) TABLE dotted with (segment x weights), plus an alternative-specific
    constant (ASC) per product. Conventional `c` is the reference (price_ratio 1,
    taste 0, ASC 0); the others are positioned relative to it:

        product   price_ratio   taste            slaughter_free  real_tissue   ASC
        w  whole  price_wf_mult taste_quality_w  1               0             asc_w
        c  conv   1 (anchor)    0 (reference)    0               1             0
        p  plant  price_pb_mult taste_quality_p  1               0             0
        x  cult   R (from cost) accept_x - 1     1               1             asc_x

    Attribute WEIGHTS are shared (q_taste, the price/loss coefficients) except the
    two that carry the segment's identity: w_slaughter (ethical values it) and
    w_realtissue (mainstream values it). The ASC of whole-food is segment-specific
    (beans are the ethical default, a rare mainstream choice); cultivated's ASC is
    its launch food-neophobia (`neophobia`, a timing transient that fades to 0, so 0 in
    the long-run static model) plus the per-meat-type authenticity offset.

    Two price-related terms, BOTH applied to every product by its own price:
      * BLP (Berry-Levinsohn-Pakes 1995) income term  alpha*ln(y_eff - price) -- richer
        consumers are less price-sensitive; alpha is derived from `beta` so the
        reference income reproduces today's coefficient, and y_eff scales with income.
      * Reference-dependent LOSS AVERSION, two-sided around the conventional price: a
        premium (price_ratio>1) is penalised at -loss_aversion, a discount (price_ratio<1)
        rewarded at +loss_aversion/2.25 -- steeper on the loss side (Tversky-Kahneman).
        Applied to every product (plant-based at 1.77x and cultivated at R alike); no
        cultivated-only cliff.
    """
    # --- the product x attribute TABLE (rows = products w, c, p, x) ----------
    price_ratio    = np.array([pr.price_wf_mult, 1.0, pr.price_pb_mult, R])
    taste          = np.array([pr.taste_quality_w, 0.0, pr.taste_quality_p, accept_x - 1.0])  # 0 = parity
    slaughter_free = np.array([1.0, 0.0, 1.0, 1.0])
    real_tissue    = np.array([0.0, 1.0, 0.0, 1.0])
    asc_w = pr.K_wholefood_M if seg == "M" else pr.K_wholefood_E      # segment-specific whole-food ASC
    asc            = np.array([asc_w, 0.0, 0.0, neophobia + tier_offset])  # cultivated: launch neophobia (->0) + tier authenticity

    # --- segment-specific attribute weights ---------------------------------
    if seg == "M":
        w_slaughter, w_realtissue = theta_free_M, pr.w_realtissue_M
    else:
        w_slaughter, w_realtissue = pr.w_slaughter_E, pr.w_realtissue_E

    # --- the SAME utility for every product ---------------------------------
    price = price_ratio * pr.p_conv
    y_eff = pr.income_ref * (income / pr.income_ref) ** pr.income_gradient
    alpha = -beta * (pr.income_ref - pr.anchor_price)
    V_price = alpha * np.log1p(-price / y_eff)                        # BLP income term (~ beta*price near ref)
    # Reference-dependent value, TWO-SIDED (symmetric around the conventional price,
    # but steeper on losses): a premium (price_ratio > 1) is penalised at -loss_aversion,
    # a discount (price_ratio < 1) is REWARDED at +loss_aversion/LOSS_AVERSION_RATIO.
    # The kink at parity is loss aversion (Tversky-Kahneman); applied to EVERY product.
    premium = price_ratio - 1.0
    V_loss = (-pr.loss_aversion * np.maximum(0.0, premium)
              + (pr.loss_aversion / LOSS_AVERSION_RATIO) * np.maximum(0.0, -premium))

    return (V_price + V_loss + pr.q_taste * taste
            + w_slaughter * slaughter_free + w_realtissue * real_tissue + asc)


def _segment(R, pr: DemandParams, beta, seg, *, accept_x, theta_free_M,
             tier_offset, neophobia, income, cultivated_present=True) -> dict:
    """Flat-logit shares of {w, c, p, x} in one segment. cultivated_present=False
    drops x from the choice set."""
    V = _utilities(R, pr, beta, seg, accept_x=accept_x, theta_free_M=theta_free_M,
                   tier_offset=tier_offset, neophobia=neophobia, income=income)
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
          neophobia_M=None, neophobia_E=None) -> float:
    """Total market share of `which` in {w, c, p, x} (pb is an alias for p),
    mixing the two segments: share_j = w_eth*P_E(j) + (1-w_eth)*P_M(j).

    The override knobs map cleanly onto the four-product / two-segment model:
      accept_x      -> cultivated taste credit (taste_x = accept_x - 1)
      theta_free_M  -> the MAINSTREAM slaughter-free weight (lifts every no-slaughter
                       product, cultivated most because it ALSO has real-tissue)
      tier_offset   -> per-product-type authenticity addend to cultivated's utility (utils)
      neophobia_M / neophobia_E -> cultivated's LAUNCH food-neophobia in each segment
                       (utils; default 0 = the long-run, fully-faded state). A timing
                       transient set by adoption_timing as it decays toward 0 with exposure.
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
    nbM = 0.0 if neophobia_M is None else neophobia_M      # default = long-run (neophobia fully faded)
    nbE = 0.0 if neophobia_E is None else neophobia_E

    M = _segment(R, pr, beta, "M", accept_x=ax, theta_free_M=tfM, tier_offset=tier_offset,
                 neophobia=nbM, income=inc, cultivated_present=cultivated_present)
    E = _segment(R, pr, beta, "E", accept_x=ax, theta_free_M=tfM, tier_offset=tier_offset,
                 neophobia=nbE, income=inc, cultivated_present=cultivated_present)
    w = pr.w_eth
    key = "p" if which == "pb" else which
    return float(w * E[key] + (1.0 - w) * M[key])


def _rate(pr: DemandParams, seg: str, which: str) -> float:
    """One segment's share of `which` in {w,c,p,x} at neutral parity, cultivated
    absent and at reference income — the moment the calibration solves target."""
    s = _segment(1.0, pr, pr.beta_price, seg, accept_x=1.0, theta_free_M=0.0,
                 tier_offset=0.0, neophobia=0.0, income=pr.income_ref, cultivated_present=False)
    return s[which]


def solve_calibration(pr: DemandParams, iters: int = 70, rounds: int = 12):
    """Pin the demand model to the cross-sectional anchors with three monotone
    1-D bisections (one equation each):

      * w_realtissue_M  -> mainstream plant-based rate = pb_mainstream_frac of PB
        buyers (GFI ~89%) — i.e. the MAINSTREAM, not the 5% ethical core, carries PB.
      * K_wholefood_M   -> mainstream whole-food rate = wf_mainstream_target.
      * K_wholefood_E   -> ethical plant-based rate = the residual (~11%) of PB.

    The first two share the mainstream normalisation, so they run in a short
    coordinate descent; the ethical one is independent. Together they reproduce the
    total PB share and the mainstream/ethical split by construction. (No separate
    static habit term — see __post_init__.)
    """
    we = pr.w_eth
    pb_M_target = pr.pb_mainstream_frac * pr.pb_share_target / (1.0 - we)        # mainstream PB rate
    pb_E_target = (1.0 - pr.pb_mainstream_frac) * pr.pb_share_target / we        # ethical PB rate
    wf_M_target = pr.wf_mainstream_target

    # --- mainstream block: (w_realtissue_M, K_wholefood_M) for (PB_M, WF_M) ---
    for _ in range(rounds):
        lo, hi = 0.0, 8.0                                # PB_M decreases in w_realtissue_M
        for _ in range(iters):
            mid = 0.5 * (lo + hi); pr.w_realtissue_M = mid
            if _rate(pr, "M", "p") > pb_M_target: lo = mid
            else: hi = mid
        pr.w_realtissue_M = 0.5 * (lo + hi)
        lo, hi = -16.0, 16.0                             # WF_M increases in K_wholefood_M
        for _ in range(iters):
            mid = 0.5 * (lo + hi); pr.K_wholefood_M = mid
            if _rate(pr, "M", "w") > wf_M_target: hi = mid
            else: lo = mid
        pr.K_wholefood_M = 0.5 * (lo + hi)

    # --- ethical block: K_wholefood_E for the ethical PB rate (PB_E decreases in it) ---
    lo, hi = -16.0, 16.0
    for _ in range(iters):
        mid = 0.5 * (lo + hi); pr.K_wholefood_E = mid
        if _rate(pr, "E", "p") > pb_E_target: lo = mid
        else: hi = mid
    pr.K_wholefood_E = 0.5 * (lo + hi)
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
    s = 0.0
    for _ in range(iters):
        pr.beta_ref = eps_x / (pr.anchor_price * (1.0 - s)) + lam_slope
        solve_calibration(pr)                                         # recalibrate at this beta
        s_new = share(R_today, pr, accept_x=1.0, theta_free_M=0.0)    # cultivated's own neutral share
        if abs(s_new - s) < tol:
            s = s_new
            break
        s = s_new
    pr.beta_ref = eps_x / (pr.anchor_price * (1.0 - s)) + lam_slope
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
        K_wholefood_M=-2.0, K_wholefood_E=-2.0,  # fixed weak outside (not solved; not the meat market)
        calibrated=True,                   # do NOT run the meat calibration solve on the milk world
    )
    milk.beta_ref = pr.beta_ref            # reuse the SAME (meat-derived) price coefficient + its anchor
    milk.anchor_price = pr.anchor_price
    # plant share = "p" with the cultivated slot absent (milk has no cultivated product)
    return share(1.0, milk, cultivated_present=False, which="p")


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
    print(f"  solved: w_realtissue_M = {pr.w_realtissue_M:.2f}  K_wholefood_M = {pr.K_wholefood_M:.2f}  "
          f"K_wholefood_E = {pr.K_wholefood_E:.2f}")
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
                             tier_offset=0.0, neophobia=0.0, income=pr.income_ref)["x"] * 100
    print(f"  [3b] ethical-segment cultivated rate: {exr(1.0):.0f}% at parity, {exr(1.6):.0f}% at R=1.6 "
          f"-> competes with cheap whole-foods, so a MODEST (not dominant) early adopter")

    # cross-category validation: plant-based MILK with the SAME taste/price machinery
    milk = pb_milk_check(pr) * 100
    print(f"  [4] PB-MILK validation (same shared coefficients, milk-appropriate product positions): "
          f"{milk:.0f}%  (observed ~15%; vs PB-meat ~1%)")
    print("      -> the SAME logit/price/taste machinery reproduces milk's success AND meat's failure")

    # PLANT-BASED AT FULL PARITY (cultivated absent), holding the calibrated standing:
    # with price+taste equalised, the only thing left penalising plant-based in the
    # mainstream is the (calibrated) reduced-form standing w_realtissue_M. replace()
    # keeps the solved values (no re-solve), changing ONLY PB's price/taste to parity.
    pbp = replace(pr, price_pb_mult=1.0, taste_quality_p=0.0)
    pb_par = _segment(1.0, pbp, pbp.beta_price, "M", accept_x=1.0, theta_free_M=0.0,
                      tier_offset=0.0, neophobia=0.0, income=pbp.income_ref,
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
    print("Done.")
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
