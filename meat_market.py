#!/usr/bin/env python3
"""
meat_market — cultivated meat's share across the SPECTRUM of conventional meats.

The single most important correction to Output 2. Earlier rungs used one
conventional price (~$12/kg, implicitly "beef"). But cultivated COST (the
numerator of R) is ~the same whatever animal it mimics — it is animal cells in a
bioreactor — while conventional PRICE (the denominator) ranges from cheap chicken
(~$4/kg) to premium seafood (~$35/kg). So the price ratio R, and cultivated's
share, differ enormously by meat type:

  * vs cheap chicken/pork: R stays well above 1 even at the cost floor -> ~0 share.
    The biggest categories are STRUCTURALLY unreachable on price.
  * vs beef / mid cuts: parity around the cost floor.
  * vs ultra-premium (sushi): R < 1 already, BUT demand resists (see below).

BUT price is only half the story — demand runs OPPOSITE to price.
Authenticity and price-sensitivity are tier-dependent (see AUTH_* / EPS_MULT_*):
  * BASIC everyday meat: cultivated is price-UNcompetitive but demand-FRIENDLY
    (cleaner-meat pull on staples; a nugget has no "authenticity"). Authenticity offset +.
  * PREMIUM/luxury meat: cultivated is price-COMPETITIVE but demand-HOSTILE
    (bought for the authentic experience; weak welfare pull on indulgence; buyers
    price-INsensitive). Authenticity offset -; low elasticity.
So there is NO easy entry point: cultivated is cheapest exactly where demand
resists (luxury) and demand-friendly exactly where it is dear (basics). The
sweet spot is the MID-CUTS (salmon fillet, beef steak). This subsumes the old
Rung 6 (premium = the high-price structured end, carrying scaffold cost), and
corrects its naive "premium first" reading.

Total cultivated penetration of meat = a weighted roll-up over the types. We
report BOTH weightings:
  * BY VOLUME (mass) -> "what fraction of meat is displaced" (animal/climate impact).
    Dragged DOWN by cheap-and-large chicken (~40% of volume, unreachable).
  * BY VALUE ($)     -> "what fraction of the meat market is captured" (commercial).
    Beef and premium count more.

Data: US per-capita consumption (USDA ERS, retail weight ~2023) and retail prices
(USDA/BLS ~2024). Global mix is FAO-style (poultry+pork dominate; prices held at
US levels as a first pass — regional price localisation is a refinement).

    python meat_market.py --no-latex
    python meat_market.py --region global --theta-free 0.5 --no-latex
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np
import matplotlib.pyplot as plt

from common import setup_style, _save
from inputs import value, prior
from cost_model import CostParams, cost_floor, media_cost
from market_share import DemandParams, share


@dataclass
class MeatType:
    name: str
    p_conv: float           # conventional retail price for THIS form, $/kg
    w_vol: float            # share of meat consumption BY VOLUME (mass)
    scaffold: float = 0.0   # extra $/kg for a STRUCTURED (cut) product; 0 = minced/unstructured
    cost_mult: float = 1.0  # cultivated biomass-cost multiplier (HOOK; default 1.0, no firm data)


# SCAF: scaffold cost $/kg for a STRUCTURED cut. ASSUMED — no published TEA covers
# scaffolding/structuring cost (Humbird 2021, CE Delft 2021 and Risner 2021 all stop at
# unstructured slurry); material side qualitatively guided by Gu et al. 2025 (no cost figure),
# process side ungrounded. Treat $6/kg as a judgement, not data. Defined in inputs.py (datasheet).

# --- The PRICE-TIER demand model (the key insight) --------------------------
# Authenticity and price-sensitivity are NOT uniform across the meat spectrum; they
# run OPPOSITE to the price ratio, which is why there is no easy entry point:
#
#   * BASIC everyday meat (mince/ground/processed, cheap): cultivated is price-
#     UNcompetitive but demand-FRIENDLY — the cleaner/no-slaughter pull is
#     exercised on routine staples, and a nugget has no "authenticity". Authenticity offset
#     +; price matters (elastic).
#   * PREMIUM meat (structured, dear: sushi, fine cuts): cultivated is price-
#     COMPETITIVE (R<1) but demand-HOSTILE — bought for the AUTHENTIC experience,
#     the welfare pull is weak on indulgence, and buyers are price-INsensitive.
#     Authenticity offset −; price barely matters (inelastic).
#   * CUTS in between.
#
# So the tier-dependent AUTHENTICITY OFFSET (added to cultivated's utility) and the
# elasticity MULTIPLIER are derived from (structured?, price). All DIALS.
# Calibrated for the WTP curve (market_share): premium must stay DEMAND-CAPPED even
# at a deep price discount (R<<1), so its authenticity offset is strongly negative AND it is
# very price-INelastic (a low EPS_MULT -> a flat WTP curve that the low R barely
# lifts). This reproduces the key insight that the sweet spot is the MID-CUTS, not
# ultra-premium: cultivated is cheapest exactly where authentic-experience demand
# resists most. (The old nested logit produced this cap structurally; here it is the
# two premium dials.)
# The tier ladder (AUTH_* authenticity offsets in utils, EPS_MULT_* elasticity multipliers)
# and PREMIUM_RATIO, SCAF live in inputs.py (the datasheet) — imported below so the numbers
# exist in exactly one place. AUTH_BASIC=+0.2, AUTH_CUT=-0.4, AUTH_PREMIUM=-1.5;
# EPS_MULT_CUT=0.8, EPS_MULT_PREMIUM=0.3. "Premium" is defined PER SPECIES by a within-species
# price ratio: a structured product priced >= PREMIUM_RATIO x its own species' everyday
# (cheapest) form is "premium", so every species can have one (wagyu beef, sushi seafood, ...).
from inputs import (SCAF, PREMIUM_RATIO, AUTH_BASIC, AUTH_CUT, AUTH_PREMIUM,
                    EPS_MULT_CUT, EPS_MULT_PREMIUM)


def species_bases(market) -> dict:
    """Cheapest (everyday) price per species in this market — the per-species
    reference against which 'premium' is judged."""
    b: dict[str, float] = {}
    for mt in market:
        a = animal_of(mt)
        b[a] = min(b.get(a, float("inf")), mt.p_conv)
    return b


def tier(mt: "MeatType", base: float) -> str:
    """basic = unstructured; premium = structured and priced >= PREMIUM_RATIO (=2.5x) its
    species' base everyday form; cut = structured but below that ratio. `base` = species_bases[...]"""
    if mt.scaffold == 0:
        return "basic"
    return "premium" if mt.p_conv >= PREMIUM_RATIO * base else "cut"


def tier_authenticity(mt: "MeatType", base: float, resistance: float = 1.0) -> float:
    """Per-tier authenticity offset (utils), scaled by the `premium_resistance` dial.
    resistance=1 -> the central ladder; 0 -> no tier effect; 2 -> doubly resistant."""
    return resistance * {"basic": AUTH_BASIC, "cut": AUTH_CUT, "premium": AUTH_PREMIUM}[tier(mt, base)]


def tier_eps_mult(mt: "MeatType", base: float, resistance: float = 1.0) -> float:
    """Per-tier own-price-elasticity multiplier, with its DEVIATION from 1 scaled by
    `premium_resistance` (so resistance=0 -> multiplier 1 = no tier effect; =1 -> central)."""
    mult = {"basic": 1.0, "cut": EPS_MULT_CUT, "premium": EPS_MULT_PREMIUM}[tier(mt, base)]
    return 1.0 + resistance * (mult - 1.0)

# Prices: GlobalProductPrices (Jan 2026) + USDA/BLS (US); mixes: USDA ERS (US),
# FAO/OECD (regional). Cultivated cost is ~global; the LOCAL price it competes
# against is what differs — by region AND by form.

# US — per-capita retail lbs (USDA ERS ~2023): chicken 100, beef 57, pork 50,
# turkey 14, seafood ~19; each split mince/cut.
# A premium variant per major species (priced >= PREMIUM_RATIO=2.5x the species' everyday form).
# Beef wagyu/prime and seafood sushi are well-attested premiums; organic chicken and
# heritage pork are real but smaller, lower-confidence categories — kept at small w_vol,
# carved out of the species' cut form so regional volume sums are unchanged.
US_MARKET = [
    MeatType("chicken (ground/proc.)", 5.0,  0.20),
    MeatType("chicken (cuts)",         9.0,  0.202, scaffold=SCAF),
    MeatType("chicken (organic)",     13.0,  0.010, scaffold=SCAF),   # premium [low-med conf]
    MeatType("beef (ground)",         11.0,  0.13),
    MeatType("beef (steak/cuts)",     20.0,  0.105, scaffold=SCAF),
    MeatType("beef (prime/wagyu)",    45.0,  0.005, scaffold=SCAF),   # premium [high conf]
    MeatType("pork (processed)",       8.0,  0.12),
    MeatType("pork (cuts)",           12.0,  0.085, scaffold=SCAF),
    MeatType("pork (heritage)",       20.0,  0.005, scaffold=SCAF),   # premium [med conf]
    MeatType("turkey (ground/proc.)",  5.0,  0.030),
    MeatType("turkey (breast/cuts)",   9.0,  0.028, scaffold=SCAF),
    MeatType("seafood (mince/canned)",10.0,  0.020),
    MeatType("seafood (fillet)",      24.0,  0.040, scaffold=SCAF),
    MeatType("seafood (sushi)",       40.0,  0.020, scaffold=SCAF),
    MeatType("rabbit (cuts)",         16.0,  0.004, scaffold=SCAF),
]

# Europe — higher prices (GPP Germany/France), pork+poultry heavy. Chicken is the
# cheapest staple (as globally); pork is the most-consumed but slightly dearer.
EU_MARKET = [
    MeatType("chicken (ground/proc.)", 6.0,  0.15),
    MeatType("chicken (cuts)",        10.0,  0.14, scaffold=SCAF),
    MeatType("chicken (organic)",     15.0,  0.010, scaffold=SCAF),   # premium [low-med conf]
    MeatType("pork (processed)",       7.0,  0.18),
    MeatType("pork (cuts)",           11.0,  0.165, scaffold=SCAF),
    MeatType("pork (iberico)",        20.0,  0.005, scaffold=SCAF),   # premium [med conf]
    MeatType("beef (ground)",         18.0,  0.10),
    MeatType("beef (steak/cuts)",     30.0,  0.095, scaffold=SCAF),
    MeatType("beef (wagyu/prime)",    55.0,  0.005, scaffold=SCAF),   # premium [high conf]
    MeatType("seafood (mince/canned)",13.0,  0.04),
    MeatType("seafood (fillet)",      28.0,  0.09, scaffold=SCAF),
    MeatType("seafood (sushi)",       45.0,  0.02, scaffold=SCAF),
    MeatType("rabbit (cuts)",         15.0,  0.02, scaffold=SCAF),
]

# China — pork-dominant; beef pricey (imported); large seafood.
CHINA_MARKET = [
    MeatType("chicken (ground/proc.)", 5.0,  0.10),
    MeatType("chicken (cuts)",         8.0,  0.115, scaffold=SCAF),
    MeatType("chicken (premium)",     13.0,  0.005, scaffold=SCAF),   # premium [low conf]
    MeatType("pork (processed)",       5.0,  0.25),
    MeatType("pork (cuts)",            7.0,  0.245, scaffold=SCAF),
    MeatType("pork (heritage)",       14.0,  0.005, scaffold=SCAF),   # premium [med conf]
    MeatType("beef (ground)",         18.0,  0.02),
    MeatType("beef (steak/cuts)",     25.0,  0.055, scaffold=SCAF),
    MeatType("beef (wagyu)",          50.0,  0.005, scaffold=SCAF),   # premium [high conf]
    MeatType("seafood (mince/canned)", 8.0,  0.06),
    MeatType("seafood (fillet)",      14.0,  0.10, scaffold=SCAF),
    MeatType("seafood (sushi)",       35.0,  0.04, scaffold=SCAF),
    MeatType("rabbit (cuts)",         12.0,  0.025, scaffold=SCAF),
]

# Global — world-average prices (GPP world avg) + FAO global mix.
GLOBAL_MARKET = [
    MeatType("chicken (ground/proc.)", 5.0,  0.15),
    MeatType("chicken (cuts)",         8.0,  0.195, scaffold=SCAF),
    MeatType("chicken (organic)",     13.0,  0.005, scaffold=SCAF),   # premium [low conf]
    MeatType("pork (processed)",       6.0,  0.16),
    MeatType("pork (cuts)",            9.0,  0.165, scaffold=SCAF),
    MeatType("pork (heritage)",       16.0,  0.005, scaffold=SCAF),   # premium [med conf]
    MeatType("beef (ground)",         14.0,  0.09),
    MeatType("beef (steak/cuts)",     24.0,  0.085, scaffold=SCAF),
    MeatType("beef (prime/wagyu)",    45.0,  0.005, scaffold=SCAF),   # premium [high conf]
    MeatType("sheep/goat",            14.0,  0.05, scaffold=SCAF),
    MeatType("seafood (mince/canned)", 8.0,  0.03),
    MeatType("seafood (fillet)",      16.0,  0.04, scaffold=SCAF),
    MeatType("seafood (sushi)",       35.0,  0.02, scaffold=SCAF),
    MeatType("rabbit (cuts)",         14.0,  0.012, scaffold=SCAF),
]

# Low-income markets — to exploit the income channel (price-sensitivity scales with
# income via the BLP term in market_share). Local retail meat prices + consumption
# mixes are ROUGH/illustrative (USDA FAS / Numbeo / FAO order-of-magnitude), flagged
# as such: cheap meat AND high price-sensitivity make cultivated hardest here.
# India: poultry/dairy-heavy, little beef (buffalo/carabeef instead), low per-capita.
INDIA_MARKET = [
    MeatType("chicken (ground/proc.)", 3.5,  0.30),
    MeatType("chicken (cuts)",         5.0,  0.28, scaffold=SCAF),
    MeatType("chicken (premium)",      9.0,  0.01, scaffold=SCAF),
    MeatType("buffalo (ground)",       4.0,  0.10),
    MeatType("buffalo (cuts)",         7.0,  0.05, scaffold=SCAF),
    MeatType("goat (cuts)",            9.0,  0.10, scaffold=SCAF),
    MeatType("goat (premium)",        23.0,  0.01, scaffold=SCAF),
    MeatType("seafood (mince/canned)", 4.0,  0.05),
    MeatType("seafood (fillet)",       8.0,  0.09, scaffold=SCAF),
    MeatType("seafood (premium)",     20.0,  0.01, scaffold=SCAF),
]
# Brazil: beef-heavy and CHEAP (major exporter); big poultry.
BRAZIL_MARKET = [
    MeatType("chicken (ground/proc.)", 3.5,  0.18),
    MeatType("chicken (cuts)",         5.0,  0.20, scaffold=SCAF),
    MeatType("beef (ground)",          7.0,  0.20),
    MeatType("beef (steak/cuts)",     12.0,  0.18, scaffold=SCAF),
    MeatType("beef (picanha/prime)",  22.0,  0.02, scaffold=SCAF),
    MeatType("pork (processed)",       5.0,  0.08),
    MeatType("pork (cuts)",            8.0,  0.07, scaffold=SCAF),
    MeatType("seafood (mince/canned)", 6.0,  0.03),
    MeatType("seafood (fillet)",      12.0,  0.04, scaffold=SCAF),
]
# Nigeria: poultry/goat/fish; low per-capita; locally pricey relative to income.
NIGERIA_MARKET = [
    MeatType("chicken (ground/proc.)", 4.5,  0.22),
    MeatType("chicken (cuts)",         6.5,  0.20, scaffold=SCAF),
    MeatType("goat (ground)",          5.5,  0.18),
    MeatType("goat (cuts)",            8.0,  0.15, scaffold=SCAF),
    MeatType("goat (premium)",        16.0,  0.01, scaffold=SCAF),
    MeatType("beef (cuts)",            8.0,  0.10, scaffold=SCAF),
    MeatType("seafood (mince/canned)", 5.0,  0.06),
    MeatType("seafood (fillet)",      10.0,  0.08, scaffold=SCAF),
]

MARKETS = {"us": US_MARKET, "eu": EU_MARKET, "china": CHINA_MARKET, "global": GLOBAL_MARKET,
           "india": INDIA_MARKET, "brazil": BRAZIL_MARKET, "nigeria": NIGERIA_MARKET}

# Region income (GDP per capita, PPP, World Bank 2023-24) — feeds the BLP price term
# in market_share.share(income=...): richer => less price-sensitive. The US is the
# reference (income_ref in inputs.py), so the US result is unchanged.
REGION_INCOME = {"us": 85810, "eu": 62266, "china": 27105, "global": 24248,
                 "india": 11159, "brazil": 22333, "nigeria": 6440}


def _rollup(market, biomass, markup, res, share_of):
    """The shared per-type roll-up used by BOTH the point estimate (penetration) and the
    Monte-Carlo band (monte_carlo): for each meat type compute its price ratio
    R = (biomass*cost_mult + scaffold + markup) / p_conv, get its cultivated share via the
    `share_of(mt, R, species_base, res)` callback (scalar for the point estimate, a per-draw
    NumPy array for the MC), then sum by VOLUME (mass) and by VALUE (price*volume, normalised).
    Keeping this in one place means the two paths can't drift. `biomass`, `markup`, `res` and the
    callback's return may each be a scalar or an array; the arithmetic is the same either way."""
    bases = species_bases(market)                                   # per-species reference price
    Wval = sum(mt.p_conv * mt.w_vol for mt in market)               # value-weight normaliser
    rows, tot_vol, tot_val = [], 0.0, 0.0
    for mt in market:
        base = bases[animal_of(mt)]
        R = (biomass * mt.cost_mult + mt.scaffold + markup) / mt.p_conv
        s = share_of(mt, R, base, res)
        rows.append((mt, R, s))
        tot_vol = tot_vol + mt.w_vol * s
        tot_val = tot_val + (mt.p_conv * mt.w_vol / Wval) * s
    return rows, tot_vol, tot_val


def penetration(market, biomass: float, theta_free_M: float = 0.0,
                accept_x: float = 1.0, markup=None, income=None, premium_resistance=None):
    """Per-type (R, cultivated share) and the volume- and value-weighted totals.

    biomass      = cultivated biomass cost $/kg (the shared numerator input).
    theta_free_M = mainstream value of the slaughter-free attribute (headline dial).
    accept_x     = how fully the mainstream credits cultivated's taste (the other dial).
    income       = region income ($/yr) for the BLP price term (None -> reference/US).
    premium_resistance = scales BOTH per-tier demand levers (authenticity offset and the
                   elasticity multiplier's deviation from 1); 1 = central, 0 = no tier effect.
    The per-tier demand resistance enters as share()'s tier_offset (in utils).
    """
    markup = value("markup_add") if markup is None else markup
    base_eps = value("eps_own")
    res = value("premium_resistance") if premium_resistance is None else premium_resistance
    pr = DemandParams()

    def share_of(mt, R, base, res):                                # per-type cultivated share
        return share(R, pr, theta_free_M=theta_free_M, accept_x=accept_x,
                     tier_offset=tier_authenticity(mt, base, res),
                     eps_own=base_eps * tier_eps_mult(mt, base, res), income=income,
                     p_ref=mt.p_conv)        # absolute price uses THIS cut's conventional price (chicken vs chicken, steak vs steak)

    rows, tot_vol, tot_val = _rollup(market, biomass, markup, res, share_of)
    return rows, tot_vol, tot_val


# ----------------------------------------------------------------------------
# Monte Carlo — propagate cost + demand uncertainty into a BAND on total
# penetration (volume and value), rolled up across meat types.
# ----------------------------------------------------------------------------
def _draw(name, rng, n):
    kind, lo, hi, mode, _ = prior(name)
    return rng.triangular(lo, mode, hi, n)


def monte_carlo(region: str, n: int = 10000, seed: int = 0) -> dict:
    """Distribution of TOTAL cultivated penetration (volume- and value-weighted),
    sampling the achievable cost inputs + the demand dials. Meat prices/mix are
    held fixed (observed market data); the band reflects the genuine unknowns:
    biomass cost, retail markup, the acceptance dials, and price elasticity."""
    rng = np.random.default_rng(seed)
    s = {k: _draw(k, rng, n) for k in
         ("media_price", "efficiency", "overhead", "markup_add", "eps_own",
          "theta_free_M", "accept_x", "premium_resistance", "neophobia_x")}
    cp = CostParams()
    biomass = media_cost(cp, s["media_price"], s["efficiency"]) + s["overhead"]

    base = DemandParams()                       # demand model (calibrated once)
    market = MARKETS[region]
    income = REGION_INCOME[region]              # region income for the BLP price term
    res = s["premium_resistance"]               # per-draw premium-resistance multiplier (array)

    def share_of(mt, R, b, res):                # per-draw cultivated share array for this type
        toff = np.array([tier_authenticity(mt, b, res[i]) for i in range(n)])   # per-draw (utils)
        eps = s["eps_own"] * np.array([tier_eps_mult(mt, b, res[i]) for i in range(n)])
        return np.array([share(R[i], base, theta_free_M=s["theta_free_M"][i],
                               accept_x=s["accept_x"][i], tier_offset=toff[i],
                               eps_own=eps[i], income=income, p_ref=mt.p_conv,
                               neophobia_x=s["neophobia_x"][i]) for i in range(n)])

    _rows, tot_vol, tot_val = _rollup(market, biomass, s["markup_add"], res, share_of)
    return dict(vol=tot_vol * 100, val=tot_val * 100)


def _ci(x):
    return {q: float(np.percentile(x, q)) for q in (5, 10, 50, 90, 95)}


def summarise_mc(region: str, n: int) -> None:
    mc = monte_carlo(region, n)
    cv, cl = _ci(mc["vol"]), _ci(mc["val"])
    print(f"\n  MONTE CARLO total penetration band ({region.upper()}, N={n}, "
          f"sampling cost + acceptance + elasticity):")
    print(f"    by VOLUME (impact):  P50 = {cv[50]:4.1f}%   80% CI [{cv[10]:.1f}, {cv[90]:.1f}]   "
          f"90% CI [{cv[5]:.1f}, {cv[95]:.1f}]")
    print(f"    by VALUE  (market):  P50 = {cl[50]:4.1f}%   80% CI [{cl[10]:.1f}, {cl[90]:.1f}]   "
          f"90% CI [{cl[5]:.1f}, {cl[95]:.1f}]")


def fig_mc(region: str, n: int, outdir, fmts) -> None:
    mc = monte_carlo(region, n)
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    for x, lbl, col in [(mc["vol"], "by VOLUME (impact)", "#DE8F05"),
                        (mc["val"], "by VALUE ($ market)", "#0173B2")]:
        ax.hist(x, bins=60, color=col, alpha=0.55, label=lbl)
        c = _ci(x)
        for q, ls in [(10, ":"), (50, "-"), (90, ":")]:
            ax.axvline(c[q], ls=ls, lw=1.0, color=col)
        ax.text(c[50], ax.get_ylim()[1] * (0.9 if col == "#DE8F05" else 0.78),
                f"P50={c[50]:.1f}% [{c[10]:.1f}-{c[90]:.1f}]", color=col, fontsize=7.5)
    ax.set_xlabel(r"Total cultivated penetration of meat (%)")
    ax.set_ylabel("draws")
    ax.set_title(f"Total penetration band — {region.upper()} (cost + acceptance + elasticity uncertainty)")
    ax.legend(fontsize=8, frameon=False)
    _save(fig, outdir, f"penetration_band_{region}", fmts)


# ----------------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------------
def summarise(region: str, theta_free: float) -> None:
    market = MARKETS[region]
    bases = species_bases(market)
    cp = CostParams()
    scenarios = [("near-term biomass $%g/kg" % value("biomass_cost_nearterm"),
                  value("biomass_cost_nearterm")),
                 ("cost FLOOR (central)", cost_floor(cp))]
    print(f"  region: {region.upper()}   theta_free_M (mainstream slaughter-free value) = {theta_free:+.1f}"
          f"   income = ${REGION_INCOME[region]:,}/yr (PPP)")
    for label, biomass in scenarios:
        rows, tv, tval = penetration(market, biomass, theta_free_M=theta_free,
                                     income=REGION_INCOME[region])
        print(f"\n  {label}  (p_cult = biomass + scaffold + ${value('markup_add'):.0f} markup):")
        print(f"    {'meat type':<20}{'$/kg':>6}{'vol%':>6}{'R':>7}{'cult share':>12}  tier")
        for mt, R, s in rows:
            print(f"    {mt.name:<20}{mt.p_conv:>6.0f}{mt.w_vol*100:>5.0f}%{R:>7.2f}{s*100:>10.1f}%  {tier(mt, bases[animal_of(mt)])}")
        print(f"    {'TOTAL — by VOLUME (impact)':<41}{tv*100:>10.1f}%")
        print(f"    {'TOTAL — by VALUE ($ market)':<41}{tval*100:>10.1f}%")


# ----------------------------------------------------------------------------
# Figure: cultivated share BY TYPE OF MEAT (chicken, pork, beef, ...), grouped by
# animal with mince-vs-cut sub-bars. Ordered cheap->expensive so the price/demand
# opposition reads left to right; both weighted totals marked.
# ----------------------------------------------------------------------------
def animal_of(mt: "MeatType") -> str:
    """Group label (the type of meat) for the per-type figure."""
    for key, lab in [("chicken", "Chicken"), ("beef", "Beef"), ("pork", "Pork"),
                     ("turkey", "Turkey"), ("seafood", "Seafood"),
                     ("sheep", "Sheep/\ngoat"), ("goat", "Sheep/\ngoat"), ("rabbit", "Rabbit")]:
        if mt.name.startswith(key):
            return lab
    return mt.name.split()[0].title()


def fig_penetration(region: str, theta_free: float, outdir, fmts) -> None:
    market = MARKETS[region]
    cp = CostParams()
    rows, tv, tval = penetration(market, cost_floor(cp), theta_free_M=theta_free,
                                 income=REGION_INCOME[region])

    # group rows by animal; colour each form by its TIER (basic / cut / premium)
    TIERCOL = {"basic": "#E69F00", "cut": "#0072B2", "premium": "#882255"}
    TORD = {"basic": 0, "cut": 1, "premium": 2}
    bases = species_bases(market)
    groups: dict[str, list] = {}
    for mt, R, s in rows:
        groups.setdefault(animal_of(mt), []).append((mt, R, s, tier(mt, bases[animal_of(mt)])))
    order = sorted(groups, key=lambda a: np.mean([mt.p_conv for mt, _, _, _ in groups[a]]))

    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    maxs = max(s for _, _, s in rows) * 100
    head = maxs * 0.16                                  # headroom for R labels
    bw = 0.26                                            # sub-bar width (up to 3 per group)
    xticks, xlabs = [], []
    for x, a in enumerate(order):
        items = sorted(groups[a], key=lambda it: TORD[it[3]])
        n = len(items)
        for j, (mt, R, s, t) in enumerate(items):
            off = (j - (n - 1) / 2) * (bw * 1.06)
            ax.bar(x + off, s * 100, width=bw, color=TIERCOL[t], alpha=0.92,
                   edgecolor="white", linewidth=0.5)
            ax.text(x + off, s * 100 + maxs * 0.015, rf"{s*100:.0f}\%", ha="center",
                    va="bottom", fontsize=7, fontweight="bold", color="0.2")
            ax.text(x + off, s * 100 + maxs * 0.075, f"R={R:.2f}", ha="center",
                    va="bottom", fontsize=6, color="0.5")
        xticks.append(x); xlabs.append(a)

    # weighted-total reference lines (neutral colours so they read as TOTALS,
    # not as another bar category), labelled in the clear left margin
    ax.axhline(tv * 100, ls="--", lw=1.2, color="0.35")
    ax.text(-0.85, tv * 100, rf"total by volume {tv*100:.0f}\%", fontsize=7.5,
            color="0.35", va="top", ha="left")
    ax.axhline(tval * 100, ls=":", lw=1.4, color="0.1")
    ax.text(-0.85, tval * 100, rf"total by value {tval*100:.0f}\%", fontsize=7.5,
            color="0.1", va="bottom", ha="left")

    ax.set_xlim(-0.9, len(order) - 0.4)
    ax.set_ylim(0, maxs + head)
    ax.set_xticks(xticks); ax.set_xticklabels(xlabs, fontsize=8.5)
    ax.set_ylabel(r"Cultivated share within the category (\%)")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=TIERCOL["basic"], label="mince / processed"),
                       Patch(color=TIERCOL["cut"], label="cut / fillet"),
                       Patch(color=TIERCOL["premium"],
                             label=r"premium ($\geq %g\times$ species base)" % PREMIUM_RATIO)],
              fontsize=8, frameon=False, loc="upper center", ncol=3)
    ax.set_title(f"Cultivated penetration by type of meat — {region.upper()} (at the cost floor)")
    _save(fig, outdir, f"penetration_by_type_{region}", fmts)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--region", default="us", choices=list(MARKETS))
    ap.add_argument("--theta-free", type=float, default=0.0, dest="theta_free",
                    help="mainstream slaughter-free value theta_free_M; 0=neutral (cultivated~conventional)")
    ap.add_argument("--n", type=int, default=10000, help="Monte Carlo draws")
    ap.add_argument("--outdir", default="figures")
    ap.add_argument("--no-latex", action="store_true")
    ap.add_argument("--formats", default="png,pdf")
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

    setup_style(use_latex=not args.no_latex)
    fmts = [f.strip() for f in args.formats.split(",") if f.strip()]
    print("meat_market — cultivated penetration across conventional meat types:")
    summarise(args.region, args.theta_free)
    summarise_mc(args.region, args.n)
    fig_penetration(args.region, args.theta_free, args.outdir, fmts)
    fig_mc(args.region, args.n, args.outdir, fmts)
    print("Done.")
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
