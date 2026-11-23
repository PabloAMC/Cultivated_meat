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

BUT price is only half the story. Shoppers like a cultivated CUT less than cultivated mince (tier_offset below):
  * mince and other unstructured products: no offset (a nugget has no "genuine article" to miss);
  * every cut: a cut is part plant protein, so it gets that much less of the real-meat credit;
  * premium cuts (wagyu, sushi-grade fish): a further penalty that grows with how far the product's price sits above its
    species' cheapest form, because part of what the buyer pays for is the genuine article.
Every product uses the model's own price sensitivity. So cultivated meat is cheapest, against the conventional product,
exactly where shoppers like it least (premium), and liked most where it is dearest (basics).

Total cultivated penetration of meat = a weighted roll-up over the types. We
report BOTH weightings:
  * BY VOLUME (mass) -> "what fraction of meat is displaced" (animal/climate impact).
    Dragged DOWN by cheap-and-large chicken (~40% of US volume, above parity even at the floor).
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
from inputs import value
from cost_model import CostParams, cost_floor, media_cost
from price_ratio import shelf_price, structured_cost
from market_share import DemandParams, share, share_x_meat_many


@dataclass
class MeatType:
    name: str
    p_conv: float           # conventional retail price for THIS form, $/kg
    w_vol: float            # share of meat consumption BY VOLUME (mass)
    scaffold: float = 0.0   # extra $/kg for a STRUCTURED (cut) product; 0 = minced/unstructured
    cost_mult: float = 1.0  # cultivated biomass-cost multiplier (HOOK; default 1.0, no firm data)


# SCAF: assembly cost $/kg for a STRUCTURED cut. A cut is CUT_CELL_SHARE cells plus a plant-protein matrix, assembled after
# harvest (price_ratio.structured_cost; research_notes/structuring_cost.md, 2026-11-19). No study costs it for cultivated
# meat; the figures come from plant-protein extrusion, surimi and binder prices. Defined in inputs.py (datasheet).

# --- How liking differs across the meat spectrum (the key insight) ---------
# Liking runs OPPOSITE to the price ratio, which is why there is no easy entry point:
#
#   * BASIC everyday meat (mince/ground/processed, cheap): cultivated is price-UNcompetitive but liked as much as the
#     model's reference product: a nugget has no "genuine article" to miss. No offset.
#   * CUTS: a cut is part plant protein, so shoppers give it that much less of the real-meat credit.
#   * PREMIUM meat (structured, dear: sushi, fine cuts): cultivated is price-COMPETITIVE (R<1) but part of what the buyer
#     pays for is the genuine article. A further penalty, growing with the product's price against its species' cheapest form.
#
# REBUILT 2026-11-19 (audit D3, D4; the constants and the reasons are in inputs.py). Until then a ladder by tier (mince +0.2,
# cut -0.4, premium -1.5 utils, with a cliff at PREMIUM_RATIO) came with LOWER price sensitivity for cuts and premium products,
# which raised cultivated meat's share wherever it was the dearer product. Now the offset is tier_offset() below and every
# product uses the model's own price sensitivity. "Premium" is judged PER SPECIES, by the product's price against its own
# species' cheapest form, so every species can have one (wagyu beef, sushi seafood, ...).
from inputs import (SCAF, CUT_CELL_SHARE, PREMIUM_RATIO, PREMIUM_START, PREMIUM_FULL, AUTH_PREMIUM_EXTRA,
                    MC_COST_INPUTS, MC_DEMAND_INPUTS, MC_TIER_INPUTS, MC_CUT_INPUTS, draw as _draw_input)


def species_bases(market) -> dict:
    """Cheapest (everyday) price per species in this market — the per-species
    reference against which 'premium' is judged."""
    b: dict[str, float] = {}
    for mt in market:
        a = animal_of(mt)
        b[a] = min(b.get(a, float("inf")), mt.p_conv)
    return b


def tier(mt: "MeatType", base: float) -> str:
    """A LABEL for charts and tables, nothing numeric depends on it: basic = unstructured; premium = structured and priced
    >= PREMIUM_RATIO (=2.5x) its species' cheapest form; cut = structured but below that ratio. `base` = species_bases[...]"""
    if mt.scaffold == 0:
        return "basic"
    return "premium" if mt.p_conv >= PREMIUM_RATIO * base else "cut"


def premium_ramp(mt: "MeatType", base: float) -> float:
    """How far a product sits in its species' premium range, 0 to 1: 0 at PREMIUM_START (2x) the species' cheapest form or
    below, 1 at PREMIUM_FULL (4x) or above, linear in the logarithm of price between. 0 for unstructured products."""
    if mt.scaffold == 0:
        return 0.0
    x = np.clip(np.log(mt.p_conv / base / PREMIUM_START) / np.log(PREMIUM_FULL / PREMIUM_START), 0.0, 1.0)
    return float(x) if np.ndim(x) == 0 else x


def tier_offset(mt: "MeatType", base: float, resistance, pr, cell_share=None, premium_extra=None):
    """Utils added to cultivated meat's utility for this product (market_share.share's tier_offset), against cultivated mince.
      mince and other unstructured products: 0.
      a structured product: BLEND + PREMIUM, with
        BLEND   = -(1 - cell_share) x pr.w_realtissue_M: the cut is part plant protein, so it gets that much less of the
                  mainstream real-meat credit of the calibrated demand model `pr` (at 80% cells about -0.45). Not scaled by
                  `resistance`.
        PREMIUM = resistance x premium_extra x premium_ramp(mt, base): what buyers of premium products hold against a
                  cultivated version, continuous in price.
    cell_share    = kg of cells in a kg of cut, THE SAME figure the cut's cost uses (None = 1 - inputs.py's scaffold_frac).
    premium_extra = None for inputs.AUTH_PREMIUM_EXTRA (the page's slider overrides it).
    `resistance` and `cell_share` may be scalars or per-draw arrays."""
    if mt.scaffold == 0:
        return 0.0
    cs = 1.0 - value("scaffold_frac") if cell_share is None else cell_share
    extra = AUTH_PREMIUM_EXTRA if premium_extra is None else premium_extra
    return -(1.0 - cs) * pr.w_realtissue_M + resistance * extra * premium_ramp(mt, base)

# Prices: GlobalProductPrices (Jan 2026) + USDA/BLS (US); mixes: USDA ERS (US),
# FAO/OECD (regional). Cultivated cost is ~global; the LOCAL price it competes
# against is what differs — by region AND by form.

# US — per-capita retail lbs (USDA ERS ~2023): chicken 100, beef 57, pork 50,
# turkey 14, seafood ~19; each split mince/cut.
# A premium variant per major species (labelled premium where priced >= PREMIUM_RATIO=2.5x the species' everyday form).
# Beef wagyu/prime and seafood sushi are well-attested premiums; organic chicken and
# heritage pork are real but smaller, lower-confidence categories — kept at small w_vol,
# carved out of the species' cut form so regional volume sums are unchanged.
# PREMIUM ROWS SIZED FROM DATA, 2026-11-18 (research_notes/premium_market_sizes.md). Until then every region carried sushi-grade
# seafood at 2% of volume and the other premium rows at 0.5-1%, unsourced. What was removed went to the species' cut row, so the
# regional totals are unchanged. US: organic chicken is 0.67% of chicken output (0.3% of all volume, was 1.0%); sushi-grade
# seafood about 0.3 Mt edible (sashimi tuna 90 kt, raw salmon and others; 0.7% of volume, was 2.0%, an inference from the world
# figures); prime beef stays at 0.5% (the rib and loin of the 10% of fed cattle that grade Prime, about 0.2 Mt).
US_MARKET = [
    MeatType("chicken (ground/proc.)", 5.0,  0.20),
    MeatType("chicken (cuts)",         9.0,  0.209, scaffold=SCAF),
    MeatType("chicken (organic)",     13.0,  0.003, scaffold=SCAF),   # premium: 0.67% of US chicken output (WATT, 2020)
    MeatType("beef (ground)",         11.0,  0.13),
    MeatType("beef (steak/cuts)",     20.0,  0.105, scaffold=SCAF),
    MeatType("beef (prime/wagyu)",    45.0,  0.005, scaffold=SCAF),   # premium [high conf]
    MeatType("pork (processed)",       8.0,  0.12),
    MeatType("pork (cuts)",           12.0,  0.085, scaffold=SCAF),
    MeatType("pork (heritage)",       20.0,  0.005, scaffold=SCAF),   # premium [med conf]
    MeatType("turkey (ground/proc.)",  5.0,  0.030),
    MeatType("turkey (breast/cuts)",   9.0,  0.028, scaffold=SCAF),
    MeatType("seafood (mince/canned)",10.0,  0.020),
    MeatType("seafood (fillet)",      24.0,  0.053, scaffold=SCAF),
    MeatType("seafood (sushi)",       40.0,  0.007, scaffold=SCAF),   # premium: about 0.3 Mt edible [inference]
    MeatType("rabbit (cuts)",         16.0,  0.004, scaffold=SCAF),
]

# Europe — higher prices (GPP Germany/France), pork+poultry heavy. Chicken is the
# cheapest staple (as globally); pork is the most-consumed but slightly dearer.
EU_MARKET = [
    MeatType("chicken (ground/proc.)", 6.0,  0.14),
    MeatType("chicken (cuts)",        10.0,  0.135, scaffold=SCAF),
    MeatType("chicken (organic)",     15.0,  0.010, scaffold=SCAF),   # premium [low-med conf]
    # Duck: a small but real European poultry product (France/Germany), pricier than chicken —
    # retail ~$13-21/kg (Selina Wamucii FR); whole-duck wholesale ~$6.4/kg. Carved from chicken.
    MeatType("duck (whole/cuts)",     14.0,  0.015, scaffold=SCAF),
    MeatType("pork (processed)",       7.0,  0.18),
    MeatType("pork (cuts)",           11.0,  0.165, scaffold=SCAF),
    MeatType("pork (iberico)",        20.0,  0.005, scaffold=SCAF),   # premium [med conf]
    MeatType("beef (ground)",         18.0,  0.10),
    MeatType("beef (steak/cuts)",     30.0,  0.095, scaffold=SCAF),
    MeatType("beef (wagyu/prime)",    55.0,  0.005, scaffold=SCAF),   # premium [high conf]
    MeatType("seafood (mince/canned)",13.0,  0.04),
    MeatType("seafood (fillet)",      21.0,  0.105, scaffold=SCAF),   # was $28; households' own spend gives $14-18 for all seafood (EUMOFA)
    MeatType("seafood (sushi)",       45.0,  0.005, scaffold=SCAF),  # premium: raw salmon and sashimi tuna, about 0.25 Mt [inference]
    MeatType("rabbit (cuts)",         15.0,  0.02, scaffold=SCAF),
]

# China — pork-dominant; beef pricey (imported); large seafood.
CHINA_MARKET = [
    MeatType("chicken (ground/proc.)", 5.0,  0.055),
    MeatType("chicken (cuts)",         8.0,  0.085, scaffold=SCAF),
    MeatType("chicken (premium)",     13.0,  0.005, scaffold=SCAF),   # premium [low conf]
    # Duck is a major poultry product in China (~88% of world duck/goose; ~8% of Chinese meat).
    # Prices: Selina Wamucii / Tridge retail ~$6-7.5/kg whole, cuts dearer. Carved from chicken so
    # the region volume total is unchanged.
    MeatType("duck (whole/proc.)",     6.0,  0.05),
    MeatType("duck (cuts)",            9.0,  0.025, scaffold=SCAF),
    MeatType("pork (processed)",       5.0,  0.25),
    MeatType("pork (cuts)",            7.0,  0.235, scaffold=SCAF),
    MeatType("pork (heritage)",       10.0,  0.015, scaffold=SCAF),   # black pigs: about 3-5% of head, 2-4x standard pork (AgroPortal 2026); was $14, 0.5%
    MeatType("beef (ground)",         18.0,  0.02),
    MeatType("beef (steak/cuts)",     25.0,  0.059, scaffold=SCAF),
    MeatType("beef (wagyu)",          40.0,  0.001, scaffold=SCAF),   # premium: Japanese wagyu barred, imported premium beef tens of kt; was $50, 0.5%
    MeatType("seafood (mince/canned)", 8.0,  0.06),
    MeatType("seafood (fillet)",       9.0,  0.132, scaffold=SCAF),   # was $14; carp $3-7, hairtail $6-9 a kilo edible (world_seafood_prices.md)
    MeatType("seafood (sushi)",       35.0,  0.008, scaffold=SCAF),   # premium: salmon 0.12 Mt, lobster, crab, grouper, abalone, about 0.7 Mt edible; was 4%
    MeatType("rabbit (cuts)",         12.0,  0.025, scaffold=SCAF),
]

# Global — world-average prices (GPP world avg) + FAO global mix.
GLOBAL_MARKET = [
    # 2026-11-18: seafood raised from 9% to 24% of the table's volume, its share of world meat plus seafood by edible weight
    # (FAO SOFIA: about 170 Mt live weight eaten, about half edible; meat about 380 Mt carcass, about two-thirds boneless;
    # research_notes/premium_market_sizes.md section 6). Meat rows scaled down in proportion; sushi-grade kept at 0.4%.
    MeatType("chicken (ground/proc.)", 5.0,  0.1126),
    MeatType("chicken (cuts)",         8.0,  0.1532, scaffold=SCAF),
    MeatType("chicken (organic)",     13.0,  0.0010, scaffold=SCAF),  # premium: about 0.35 Mt (France, US, EU organic and Label Rouge)
    # Duck + goose ~3.3% of world meat (~12 of 365 Mt; China ~88%). World-avg price ~$7 whole.
    # Carved from chicken so the global volume total is unchanged.
    MeatType("duck/goose (whole)",     7.0,  0.0208),
    MeatType("duck/goose (cuts)",     10.0,  0.0083, scaffold=SCAF),
    MeatType("pork (processed)",       6.0,  0.1334),
    MeatType("pork (cuts)",            9.0,  0.1405, scaffold=SCAF),
    MeatType("pork (heritage)",       16.0,  0.0013, scaffold=SCAF),  # premium: Iberico about 0.25 Mt, EU organic 0.05; Chinese black pig not counted
    # Beef (revised 2026-11-13): GPP's own "average price" (17.59 USD/kg, Jan 2026) is an UNWEIGHTED mean
    # over 76 countries, so Switzerland (64.64) counts as much as China or Brazil; the earlier $14/$24 sat
    # ABOVE the US $11/$20 for that reason. Weighting each country's GPP beef price by its 2025 beef
    # consumption (USDA FAS PSD 'Meat, Beef and Veal', Domestic Consumption; 90% of world use matched;
    # EU = mean of DE, FR, IT, ES, PL, NL) gives 19.15 USD/kg against GPP USA 18.80: world = 1.019 x US.
    # So both beef rows are the US rows x 1.019. Method and country table: METHODS.md, "World beef price".
    MeatType("beef (ground)",         11.2,  0.0750),
    MeatType("beef (steak/cuts)",     20.4,  0.0734, scaffold=SCAF),
    MeatType("beef (prime/wagyu)",    45.0,  0.0017, scaffold=SCAF),   # premium: about 0.5 Mt at $45 or more (0.25-0.9): US Prime rib and loin, wagyu, Hanwoo
    MeatType("sheep/goat",            14.0,  0.0417, scaffold=SCAF),
    # Seafood re-priced by who eats the fish, 2026-11-19 (research_notes/world_seafood_prices.md). Before: canned $8 (34% of
    # seafood), one "fillet" row at $16 (64%), from no weighted source. Weighted by consumption (China 36%, at $3-9 a kilo edible),
    # seafood averages about $10: a mass market near $7 (whole fish and ordinary fillets, per kg edible) and a premium tier near $20
    # (salmon, shrimp, cod, tuna loins; about 16% of edible weight). The seafood total (0.244) is unchanged.
    MeatType("seafood (mince/canned)", 7.0,  0.0659),
    MeatType("seafood (whole fish, ordinary fillet)", 7.0, 0.1341, scaffold=SCAF),
    MeatType("seafood (premium fillet, shrimp)", 20.0, 0.0400, scaffold=SCAF),
    MeatType("seafood (sushi)",       35.0,  0.0040, scaffold=SCAF),   # premium: about 1.2 Mt edible (0.6-2.5): raw salmon 0.5, sashimi tuna 0.25, others
    MeatType("rabbit (cuts)",         14.0,  0.0100, scaffold=SCAF),
]

# Low-income markets — to exploit the income channel (price-sensitivity scales with
# income via the BLP term in market_share). Local retail meat prices + consumption
# mixes are ROUGH/illustrative (USDA FAS / Numbeo / FAO order-of-magnitude), flagged
# as such: cheap meat AND high price-sensitivity make cultivated hardest here.
# India: poultry/dairy-heavy, little beef (buffalo/carabeef instead), low per-capita.
INDIA_MARKET = [
    MeatType("chicken (ground/proc.)", 3.5,  0.30),
    MeatType("chicken (cuts)",         5.0,  0.289, scaffold=SCAF),
    MeatType("chicken (premium)",      9.0,  0.001, scaffold=SCAF),   # branded chilled lines, 0.1% or less (unsourced estimate); was 1%
    MeatType("buffalo (ground)",       4.0,  0.10),
    MeatType("buffalo (cuts)",         7.0,  0.05, scaffold=SCAF),
    MeatType("goat (cuts)",            9.0,  0.10, scaffold=SCAF),
    MeatType("goat (premium)",        23.0,  0.01, scaffold=SCAF),
    MeatType("seafood (mince/canned)", 4.0,  0.05),
    MeatType("seafood (fillet)",       6.0,  0.09, scaffold=SCAF),    # was $8; bone-in rohu $4.5-6 a kilo edible
    MeatType("seafood (premium)",     20.0,  0.01, scaffold=SCAF),
]
# Brazil: beef-heavy and CHEAP (major exporter); big poultry.
BRAZIL_MARKET = [
    MeatType("chicken (ground/proc.)", 3.5,  0.18),
    MeatType("chicken (cuts)",         5.0,  0.20, scaffold=SCAF),
    MeatType("beef (ground)",          7.0,  0.20),
    MeatType("beef (steak/cuts)",     12.0,  0.195, scaffold=SCAF),
    MeatType("beef (picanha/prime)",  22.0,  0.005, scaffold=SCAF),   # certified Angus and branded lines, about 0.5% (Canal Rural 2026, snippet); was 2%
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
    MeatType("goat (cuts)",            8.0,  0.158, scaffold=SCAF),
    MeatType("goat (premium)",        16.0,  0.002, scaffold=SCAF),   # 0.2% or less (unsourced estimate; imports banned, trade informal); was 1%
    MeatType("beef (cuts)",            8.0,  0.10, scaffold=SCAF),
    MeatType("seafood (mince/canned)", 5.0,  0.06),
    MeatType("seafood (fillet)",      10.0,  0.08, scaffold=SCAF),
]

MARKETS = {"us": US_MARKET, "eu": EU_MARKET, "china": CHINA_MARKET, "global": GLOBAL_MARKET,
           "india": INDIA_MARKET, "brazil": BRAZIL_MARKET, "nigeria": NIGERIA_MARKET}

# Region income — feeds the BLP price term in market_share.share(income=...): richer => less price-sensitive. The US is the
# reference (income_ref in inputs.py), so the US result is unchanged. Since 2026-11-20: GDP per head in NOMINAL US dollars,
# World Bank 2024 (API, indicator NY.GDP.PCAP.CD), because the meat prices it is set against are nominal dollars, and ln(y - p)
# needs both in the same units. Until then GDP per head at purchasing-power parity (World Bank 2023-24): US 85,810, EU 62,266,
# China 27,105, world 24,248, India 11,159, Brazil 22,333, Nigeria 6,440. income_gradient was re-solved to keep the Nigeria/US
# own-price elasticity ratio at equal price at 2.2 (inputs.py).
REGION_INCOME = {"us": 86170, "eu": 43314, "china": 13293, "global": 13717,
                 "india": 2592, "brazil": 10311, "nigeria": 1084}


# ----------------------------------------------------------------------------
# Markets it cannot be sold into, and conventional meat's price as cultivated meat takes sales (2026-11-20)
# ----------------------------------------------------------------------------
US_POP_M, EU_POP_M = 341.78, 451.28         # US Census Vintage 2025; Eurostat 1 Jan 2025 (research_notes/closed_markets.md)
# Meat eaten a head, kg a year: FAO food balance sheets, 2023 (meat supply per person, via Our World in Data's
# "meat-supply-per-person" series, fetched 2026-11-20). The US and EU weights in the world are each region's people times its meat
# a head, over the world's (research_notes/closed_markets.md).
MEAT_KG_HEAD = {"us": 122.06, "eu": 78.55, "world": 45.12}
CLOSED_LEVELS = ("none", "permanent", "all", "religious_against", "religious_conditions")


def world_meat_weight(region: str) -> float:
    """The region's share of the world's meat eaten: its people times its meat a head, over the world's (MEAT_KG_HEAD)."""
    pop = {"us": US_POP_M, "eu": EU_POP_M}[region]
    return pop * MEAT_KG_HEAD[region] / (value("mk_world_pop_m") * MEAT_KG_HEAD["world"])


def closed_share(region: str, level=None) -> float:
    """Share of a region's meat market cultivated meat cannot be sold into (research_notes/closed_markets.md), each closed
    jurisdiction weighted by its share of the region's meat eaten: US states by their share of the US population (meat a head
    taken as equal between states, an assumption), Italy and Hungary by their share of the EU's meat, the US and the EU by their
    share of the world's meat (world_meat_weight). `level` (default the input mk_closed_level): 0 or "none"; 1 or "permanent": the
    five US states with permanent bans; 2 or "all": every law in force, the three US temporary bans and Italy's and Hungary's
    contested laws included; 3 or "religious_against": the same and, for the world only, Indonesia, where the one religious body
    that has ruled against it (Nahdlatul Ulama, 2021) sits (mk_closed_religious_against); 4 or "religious_conditions": the same and,
    for the world only, the populations whose religious authorities have set conditions (halal or kosher inputs and supervision),
    counted as closed as if those conditions were not met (mk_closed_religious_conditions). Other regions: none."""
    lv = int(round(value("mk_closed_level"))) if level is None else (CLOSED_LEVELS.index(level) if isinstance(level, str) else int(level))
    if lv <= 0:
        return 0.0
    us = value("mk_closed_us_permanent") + (value("mk_closed_us_temporary") if lv >= 2 else 0.0)
    eu = value("mk_closed_eu_contested") if lv >= 2 else 0.0
    if region == "us":
        return us
    if region == "eu":
        return eu
    if region == "global":
        laws = us * world_meat_weight("us") + eu * world_meat_weight("eu")
        return (laws + (value("mk_closed_religious_against") if lv >= 3 else 0.0)
                + (value("mk_closed_religious_conditions") if lv >= 4 else 0.0))
    return 0.0


def conv_exponent(supply_elast=None) -> float:
    """1 / (es - ed): conventional meat's price falls as p0 x (1 - s)^this when cultivated meat takes a share s of the market
    (mk_supply_elast, mk_demand_elast). None or inf supply elasticity: 0, a fixed price."""
    es = value("mk_supply_elast") if supply_elast is None else supply_elast
    if es is None or not np.isfinite(es):
        return 0.0
    return 1.0 / (es - value("mk_demand_elast"))


def _region_of(market) -> str | None:
    return next((k for k, m in MARKETS.items() if m is market), None)


def _rollup(market, biomass, markup, res, share_of, margin=None, cell_share=None, assembly=None, closed=None,
            supply_elast=None, displaced=None):
    """`_rollup_once` with two things a market does around it (2026-11-20):
      * conventional meat's price falls as cultivated meat takes sales: every price of the region's meat is p0 x f with
        f = (1 - s)^(1 / (es - ed)) (conv_exponent), s the region's volume share sold, solved with the share (the secant
        method from f = 1, to 1e-8; a lower price lowers the share, so it converges). Applied to the market as a whole (the same s and f for every kind of meat);
        `supply_elast` = inf holds the price fixed. The fall in conventional meat's sales is d x s, d the kilos of conventional
        meat not bought for each kilo sold (`displaced`, default the input meat_displaced_per_kg, 1; 2026-11-22, sixth batch):
        the price follows the meat farms stop selling, not cultivated meat's sales as such;
      * the share of the market it cannot be sold into (`closed`, default closed_share(region)): the volume and value shares
        are multiplied by (1 - closed). The price fall uses the share actually sold.
    rows carry the per-type shares of the whole region (the closed part included, at none); so do the totals."""
    region = _region_of(market)
    cl = closed_share(region) if (closed is None and region is not None) else (closed or 0.0)
    k = conv_exponent(supply_elast)
    dsp = value("meat_displaced_per_kg") if displaced is None else displaced
    rows, tv, tval = _rollup_once(market, biomass, markup, res, share_of, margin, cell_share, assembly, 1.0)
    if k != 0.0:
        # solve h(f) = f - (1 - dsp s(f) (1 - closed))^k = 0 by the secant method from f = 1 (to |h| < 1e-8; per draw for arrays)
        f0, h0 = 1.0, 1.0 - (1.0 - dsp * np.asarray(tv) * (1.0 - cl)) ** k
        f = f0 - h0
        for _ in range(30):
            rows, tv, tval = _rollup_once(market, biomass, markup, res, share_of, margin, cell_share, assembly, f)
            h = f - (1.0 - dsp * np.asarray(tv) * (1.0 - cl)) ** k
            if np.max(np.abs(h)) < 1e-8:
                break
            d = h - h0
            step = np.where(np.abs(d) > 1e-14, h * (f - f0) / np.where(np.abs(d) > 1e-14, d, 1.0), h)
            f0, h0, f = f, h, f - step
    rows = [(mt, R, sh * (1.0 - cl)) for mt, R, sh in rows]       # each kind of meat's share of the whole region's sales
    return rows, tv * (1.0 - cl), tval * (1.0 - cl)


def conv_price_factor(market, biomass, **kw) -> float:
    """The factor f on conventional meat's prices at the share cultivated meat takes (penetration's fixed point)."""
    tv = penetration(market, biomass, **kw)[1]
    d = value("meat_displaced_per_kg") if kw.get("displaced") is None else kw["displaced"]
    return float((1.0 - d * tv) ** conv_exponent(kw.get("supply_elast")))


def _rollup_once(market, biomass, markup, res, share_of, margin=None, cell_share=None, assembly=None, f=1.0):
    """The shared per-type roll-up used by BOTH the point estimate (penetration) and the
    Monte-Carlo band (monte_carlo): for each meat type compute its price ratio
    R = shelf_price(cut_cost, markup, margin) / p_conv, with cut_cost = biomass*cost_mult for mince and
    price_ratio.structured_cost(biomass*cost_mult) for a cut; get its cultivated share via the
    `share_of(mt, R, species_base, res)` callback (scalar for the point estimate, a per-draw
    NumPy array for the MC), then sum by VOLUME (mass) and by VALUE (price*volume, normalised).
    Keeping this in one place means the two paths can't drift. `biomass`, `markup`, `res`, `cell_share`, `assembly` and the
    callback's return may each be a scalar or an array; the arithmetic is the same either way. `margin` is the
    retailer's gross margin (None = inputs.py's retail_margin). `cell_share` is the kg of cells in a kg of cut (None = 1 -
    inputs.py's scaffold_frac) and `assembly` what assembling a cut costs, $/kg (None = each type's own mt.scaffold, which is
    inputs.py's process_cost). A callback that applies tier_offset must be given the SAME cell_share: the cut is one product
    in cost and in liking."""
    bases = species_bases(market)                                   # per-species reference price
    Wval = sum(mt.p_conv * mt.w_vol for mt in market)               # value-weight normaliser (at the prices before any fall)
    scaled = (lambda mt: mt) if np.ndim(f) == 0 and f == 1.0 else (lambda mt: _Scaled(mt, f))
    # volume-weight normaliser: the listed w_vol sum to 1.00-1.025 by region (premium variants were
    # added without trimming the rest exactly), so normalise to make the total a true share.
    Wvol = sum(mt.w_vol for mt in market)
    rows, tot_vol, tot_val = [], 0.0, 0.0
    for mt0 in market:
        base = bases[animal_of(mt0)] * f                            # the premium ramp is a ratio: unchanged by a uniform fall
        mt = scaled(mt0)
        cells = biomass * mt.cost_mult
        cut = (structured_cost(cells, cell_share=cell_share, assembly=mt.scaffold if assembly is None else assembly)
               if mt.scaffold > 0 else cells)
        R = shelf_price(cut, markup, margin) / mt.p_conv
        s = share_of(mt, R, base, res)
        rows.append((mt0, R, s))
        tot_vol = tot_vol + (mt.w_vol / Wvol) * s
        tot_val = tot_val + (mt0.p_conv * mt0.w_vol / Wval) * s
    return rows, tot_vol, tot_val


class _Scaled:
    """A meat type whose conventional price is `f` times its own (f may be a per-draw array)."""
    def __init__(self, mt, f):
        self._mt, self.p_conv = mt, mt.p_conv * f

    def __getattr__(self, name):
        return getattr(self._mt, name)


def penetration(market, biomass: float, theta_free_M: float = 0.0,
                accept_x: float = 1.0, markup=None, income=None, premium_resistance=None,
                premium_extra=None, pr=None, cell_share=None, assembly=None, closed=None, supply_elast=None,
                displaced=None):
    """Per-type (R, cultivated share) and the volume- and value-weighted totals.

    biomass      = cultivated biomass cost $/kg (the shared numerator input).
    theta_free_M = mainstream value of the slaughter-free attribute (headline dial).
    accept_x     = how fully the mainstream credits cultivated's taste (the other dial).
    income       = region income ($/yr) for the BLP price term (None -> reference/US).
    premium_resistance = how much less buyers of premium products like a cultivated version, beyond what applies to
                   any cut: scales the premium part of tier_offset only; 1 = as set, 0 = none.
    premium_extra = optional full premium penalty in utils (the interactive's slider); None = inputs.AUTH_PREMIUM_EXTRA.
                   premium_resistance still scales it.
    pr           = optional DemandParams (e.g. a w_ratio or loss_aversion variant); None = the defaults.
    cell_share   = kg of cells in a kg of cut (None = 1 - inputs.py's scaffold_frac): sets BOTH the cut's cost and how much
                   less shoppers like it than a product that is all cells.
    assembly     = what assembling a cut costs, $/kg (None = inputs.py's process_cost, carried by each type).
    displaced    = kg of conventional meat not bought for each kg sold (None = the input meat_displaced_per_kg): it sets only
                   conventional meat's price fall (_rollup), not the shares themselves.
    The per-product offset enters as share()'s tier_offset (in utils); every product uses pr's own price sensitivity.
    """
    markup = value("markup_add") if markup is None else markup
    pr = DemandParams() if pr is None else pr
    res = value("premium_resistance") if premium_resistance is None else premium_resistance
    cs = 1.0 - value("scaffold_frac") if cell_share is None else cell_share

    def share_of(mt, R, base, res):                                # per-type cultivated share
        return share(R, pr, theta_free_M=theta_free_M, accept_x=accept_x,
                     tier_offset=tier_offset(mt, base, res, pr, cs, premium_extra), income=income,
                     p_ref=mt.p_conv, which="x_meat")   # share of the meat sold (x / (x + c)), since 2026-11-19        # absolute price uses THIS cut's conventional price (chicken vs chicken, steak vs steak)

    rows, tot_vol, tot_val = _rollup(market, biomass, markup, res, share_of, cell_share=cs, assembly=assembly, closed=closed,
                                     supply_elast=supply_elast, displaced=displaced)
    return rows, tot_vol, tot_val


# ----------------------------------------------------------------------------
# Monte Carlo — propagate cost + demand uncertainty into a BAND on total
# penetration (volume and value), rolled up across meat types.
# ----------------------------------------------------------------------------
def _draw(name, rng, n):
    return _draw_input(name, rng, n)        # inputs.draw: THE one sampler (triangular, or lognormal where the input says so)


def monte_carlo(region: str, n: int = 10000, seed: int = 0, biomass=None, equal_share_input: str = "equal_price_share") -> dict:
    """Distribution of TOTAL cultivated penetration (volume- and value-weighted),
    sampling the achievable cost inputs + the demand dials. Meat prices/mix are
    held fixed (observed market data); the band reflects the genuine unknowns:
    biomass cost, retail markup, the acceptance dials, price elasticity, premium
    resistance, and a cut's make-up (its cell share, which moves both its cost and how much shoppers like it, and its
    assembly cost). The sampled set is inputs.MC_* — the same list the page's band uses."""
    rng = np.random.default_rng(seed)
    s = {k: _draw(k, rng, n) for k in MC_COST_INPUTS + MC_DEMAND_INPUTS + MC_TIER_INPUTS + MC_CUT_INPUTS}
    if equal_share_input != "equal_price_share":   # a scenario with its own demand setting (the all-favourable example): drawn on its own
        s["equal_price_share"] = _draw(equal_share_input, np.random.default_rng(seed + 7), n)   # stream, the others unchanged
    cp = CostParams()
    if biomass is None:
        biomass = media_cost(cp, s["media_price"], s["efficiency"]) + s["overhead"]
    else:                                       # a cost distribution supplied by the caller (floor_share_mc)
        biomass = np.asarray(biomass, dtype=float)
        assert biomass.shape == (n,), "biomass must have one value per draw"

    base = DemandParams()                       # demand model (calibrated once)
    market = MARKETS[region]
    income = REGION_INCOME[region]              # region income for the BLP price term
    res = s["premium_resistance"]               # per-draw premium-resistance multiplier (array)
    cell_share = 1.0 - s["scaffold_frac"]       # per-draw kg of cells in a kg of cut: the cut's cost AND its liking

    def share_of(mt, R, b, res):                # per-draw cultivated share array for this type
        toff = np.broadcast_to(tier_offset(mt, b, res, base, cell_share), (n,))   # per-draw (utils)
        # taste (accept_x) is not drawn since 2026-11-20: it is held at its point value (equal_price_share is the net of it)
        # share(R[i], base, tier_offset=toff[i], eps_own=..., kappa=..., income, p_ref=mt.p_conv, equal_share=..., which="x_meat")
        # for every draw at once (novelty, no-slaughter, health: in equal_price_share); tests/test_share_many.py checks it is that
        return share_x_meat_many(np.broadcast_to(np.asarray(R, dtype=float), (n,)), base, tier_offset=toff,
                                 eps_own=s["eps_own"], kappa=s["cult_sub_mult"], income=income,
                                 p_ref=np.broadcast_to(mt.p_conv, (n,)), equal_share=s["equal_price_share"])

    _rows, tot_vol, tot_val = _rollup(market, biomass, s["markup_add"], res, share_of, s["retail_margin"],
                                      cell_share=cell_share, assembly=s["process_cost"])
    return dict(vol=tot_vol * 100, val=tot_val * 100)


def floor_share_mc(region: str = "global", n: int = 2000, seed: int = 0, plant: str = "sanitary") -> dict:
    """Cost and demand uncertain together, at the floor case: each draw takes a cost from the floor's own
    uncertainty (floor_physics.floor_mc: plant estimate, density, cells, financing ...) and the demand
    dials from their priors (price sensitivity, acceptance, markup ...). Returns the total penetration
    draws (% by volume and by value) and the cost draws."""
    import floor_physics as fp
    cost = fp.floor_mc(n, seed=seed, plant=plant)["total"]
    mc = monte_carlo(region, n, seed=seed + 1, biomass=cost)
    return dict(vol=mc["vol"], val=mc["val"], cost=cost)


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
                        (mc["val"], r"by VALUE (\$ market)", "#0173B2")]:
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
          f"   income = ${REGION_INCOME[region]:,}/yr (nominal)")
    for label, biomass in scenarios:
        rows, tv, tval = penetration(market, biomass, theta_free_M=theta_free,
                                     income=REGION_INCOME[region])
        print(f"\n  {label}  (p_cult = (biomass, or for cuts {1 - value('scaffold_frac'):.0%} biomass + matrix + assembly, + ${value('markup_add'):.1f}) / (1 - {value('retail_margin'):.0%})):")
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
# Animals per tonne of edible meat, by species [approximate; from typical carcass and edible yields: a
# 2.6 kg broiler gives about 1.7 kg of meat, a 630 kg steer about 330 kg, a 125 kg pig about 90 kg, a
# 14 kg turkey about 9 kg, a 2.3 kg rabbit about 1.3 kg]. Seafood is left out: it runs from a few
# hundred animals per tonne (farmed salmon) to tens of thousands (shrimp, small fish), and the model's
# seafood rows do not say which.
ANIMALS_PER_TONNE = {"Chicken": 580.0, "Beef": 3.0, "Pork": 11.0, "Turkey": 110.0, "Rabbit": 770.0}


def animals_per_tonne_sold(market, biomass: float, **kw) -> dict:
    """Land animals spared per tonne of cultivated meat sold, given where the model says it sells.
    Returns the mix-weighted figure for cultivated sales, the same for the whole meat market (what a
    tonne spares if it displaced meat in proportion to consumption), and the seafood share of sales.
    Each tonne sold is counted as meat_displaced_per_kg tonnes of conventional meat not bought (1 by default; 2026-11-22,
    sixth batch); this has not been measured for cultivated meat."""
    rows, _vol, _val = penetration(market, biomass, **kw)
    d = value("meat_displaced_per_kg") if kw.get("displaced") is None else kw["displaced"]
    sold = {mt.name: mt.w_vol * sh for mt, _R, sh in rows}
    tot = sum(sold.values())
    a = lambda mt: ANIMALS_PER_TONNE.get(animal_of(mt).split("/")[0], 0.0)
    land = sum(v for mt, _R, _s in rows for v in [sold[mt.name]] if animal_of(mt) != "Seafood")
    return {"cultivated_mix": d * sum(sold[mt.name] * a(mt) for mt, _R, _s in rows) / tot,
            "market_mix": d * sum(mt.w_vol * a(mt) for mt, _R, _s in rows) / sum(mt.w_vol for mt, _R, _s in rows),
            "seafood_share_of_sales": 1.0 - land / tot}


# Species with published cell data (floor_physics.SPECIES_PRESETS) and the meat types they stand for.
SPECIES_OF = {"Chicken": "chicken", "Turkey": "chicken", "Duck": "chicken", "Beef": "cattle", "Seafood": "fish"}


def species_market(market, **explore_kw) -> list:
    """The market with each type's cost_mult set from its species' published cells, relative to the
    model cell, everything else as in the floor case (floor_physics.explore). Types with no cell
    data (pork, rabbit, sheep) keep 1.0. For the question: what does the floor's plant cost with the
    cells that have actually been published?"""
    import floor_physics as fp
    from dataclasses import replace as _rep
    base = fp.explore(**explore_kw)["total"]
    mult = {}
    for animal, key in SPECIES_OF.items():
        _label, dh, mass, _med, pco2, _rng, _extra, _note = fp.SPECIES_PRESETS[key]
        mult[animal] = fp.explore(**{**explore_kw, "doubling_h": dh, "mass_pg": mass, "pco2_mbar": pco2})["total"] / base   # the species' cells replace the case's
    return [_rep(mt, cost_mult=mult.get(animal_of(mt), 1.0)) for mt in market]


def animal_of(mt: "MeatType") -> str:
    """SPECIES label (the type of meat). Used BOTH for figure grouping AND for the per-species
    'premium' base price (a cut is premium if >= PREMIUM_RATIO x its OWN species' cheapest form),
    so each species — incl. duck — gets its own base. The coarser POULTRY/FISH grouping for display
    is family_of() below; species stays the unit of the tier math."""
    for key, lab in [("chicken", "Chicken"), ("beef", "Beef"), ("pork", "Pork"),
                     ("turkey", "Turkey"), ("duck", "Duck"), ("seafood", "Seafood"),
                     ("sheep", "Sheep/\ngoat"), ("goat", "Sheep/\ngoat"), ("rabbit", "Rabbit")]:
        if mt.name.startswith(key):
            return lab
    return mt.name.split()[0].title()


# Coarser FAMILY grouping — display/organising layer ONLY (does NOT enter the tier math, which
# stays per-species via animal_of). We group ONLY the two families where the member species share
# real structure: POULTRY (chicken/turkey/duck/goose — near-identical cell biology, ~37C culture,
# cheap price band, no-authenticity-on-a-nugget framing) and SEAFOOD/FISH (the one biologically
# distinct family — lower ~24-28C culture, different cells; wide price range). Red meat (beef),
# pork, sheep/goat, rabbit are NOT forced into a synthetic family — they stand alone, because
# lumping e.g. ruminant beef with monogastric pork would assert a commonality the data lacks.
def family_of(mt: "MeatType") -> str:
    """Family label for display grouping (poultry / fish grouped; others stand alone)."""
    a = animal_of(mt)
    if a in ("Chicken", "Turkey", "Duck"):
        return "Poultry"
    if a == "Seafood":
        return "Seafood / fish"
    return a.replace("\n", " ")


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
            ax.text(x + off, s * 100 + maxs * 0.015, rf"{s*100:.0f}%", ha="center",
                    va="bottom", fontsize=7, fontweight="bold", color="0.2")
            ax.text(x + off, s * 100 + maxs * 0.075, f"R={R:.2f}", ha="center",
                    va="bottom", fontsize=6, color="0.5")
        xticks.append(x); xlabs.append(a)

    # weighted-total reference lines (neutral colours so they read as TOTALS,
    # not as another bar category), labelled in the clear left margin
    ax.axhline(tv * 100, ls="--", lw=1.2, color="0.35")
    ax.text(-0.85, tv * 100, rf"total by volume {tv*100:.0f}%", fontsize=7.5,
            color="0.35", va="top", ha="left")
    ax.axhline(tval * 100, ls=":", lw=1.4, color="0.1")
    ax.text(-0.85, tval * 100, rf"total by value {tval*100:.0f}%", fontsize=7.5,
            color="0.1", va="bottom", ha="left")

    ax.set_xlim(-0.9, len(order) - 0.4)
    ax.set_ylim(0, maxs + head)
    ax.set_xticks(xticks); ax.set_xticklabels(xlabs, fontsize=8.5)
    ax.set_ylabel(r"Cultivated share within the category (%)")
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
