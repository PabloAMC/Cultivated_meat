#!/usr/bin/env python3
"""
cost_model — the cost of cultivated biomass, with a derived floor. This is the
NUMERATOR of the price ratio.

HOW TO READ THE NUMBERS (2026-11-14). All costs are per kg of REAL wet cells (about
70% water, 20% protein: comparable with meat). The default is what a company reports
for its own process (SuperMeat 2024: 30.5 L of medium per kg at $0.50/L, plus $10.8/kg
of running costs), with a yearly charge on its plant at the rate used for every other
case ($8.3/kg): $34.3/kg. The company's own figure, with depreciation only, is $29.5.
The floor's plant term comes from physics (floor_physics.py). Pasitka et al. 2024 is
no longer an anchor: its kilogram is a wet pellet that is mostly liquid, and its cost
leaves out capital (METHODS.md, "Why Pasitka is not the anchor").

price_ratio.py defines how a biomass cost becomes R and where the parity
threshold sits; THIS module produces that biomass cost — a transparent,
component-based number you can poke. The two questions it answers:

  1. "What if the medium gets cheaper?"  -> vary `media_price` (0.50 -> 0.2 $/L).
  2. "Where is the floor?"               -> `cost_floor()` derives it from the
                                            irreducible amino-acid feedstock +
                                            the minimal cost of running a plant.

Why a component model (not one number)
--------------------------------------
Cost is a sum of a *reducible* part (recombinant proteins, single-use
consumables, small-scale capital — engineerable toward ~0) and an *irreducible*
part (bulk amino acids + glucose the cells must consume, and the minimal
capital/labour/energy of running a plant at scale). Splitting them is the only
honest way to say where the floor is.

        biomass_cost = media_cost + nonmedia_cost
        media_cost   = media_intensity[L/kg] * efficiency * media_price[$/L]
        p_cult       = biomass_cost + markup_add        (ADDITIVE, see below)

The markup is ADDITIVE, not multiplicative. Processing, packaging, cold-chain
distribution and retail margin are roughly FIXED dollars per kg; they do not
shrink in proportion when biomass gets cheaper. A multiplicative markup would
wrongly let the retail wedge vanish as cost falls and make parity look easier
than it is. ~$5/kg is comparable to conventional meat's farm-to-retail spread.

Anchors (all tagged; see inputs.py):
  * media_intensity = 30.5 L/kg   [SuperMeat: 92.77e6 L a year for 3,039 t].
  * media_price     = 0.50 $/L    [SuperMeat: "<$0.5 per liter"; tweak to 0.2].
  * nonmedia_cost   = 19.1 $/kg   [SuperMeat's running costs ($10.8) plus a 23.6%-a-
    year charge on its plant ($8.3, from its depreciation over an assumed 10 years)].
  * efficiency      = 1.0         [cells as reported; 0.25 = about 8 L/kg, the
    medium use of Humbird's efficient-cell designs].

What Humbird actually CONSTRAINS vs. what is our best guess
----------------------------------------------------------
The source check (Humbird 2021) sharpened which numbers are grounded and which
were draft guesses that turned out inaccurate. We keep them clearly separated:

  HUMBIRD'S GROUNDED CONSTRAINTS (use as anchors):
   * Bulk plant hydrolysate at $2/kg cuts $15-16/kg from his amino-acid bill
     (Table 3.4 -> 3.5: ~$19.2/kg AA mix collapses to ~$3.4/kg residual). VERBATIM.
   * His headline cost is $37/kg (fed-batch) / $51/kg (perfusion) -- BOTH above the
     ~$25/kg he treats as a parity threshold. He is PESSIMISTIC on parity.
   * His binding constraints are NOT just feedstock: bioreactor SCALE-UP (CO2
     accumulation caps production-vessel volume; O2 transfer; shear), STERILITY /
     clean-room cost limiting single-facility size, and growth-factor cost. He
     calls cheap media + metabolic efficiency "necessary but insufficient" and
     ranks capital reduction "secondary at best."
     -> Our floor below is a FEEDSTOCK + OVERHEAD floor that ASSUMES these scale/
        sterility ceilings are engineered away. That assumption, not the media
        price, is the model's biggest unrepresented risk. Flagged in cost_floor().

   * Glucose: his Table 2.3 gives 0.13 mol per mol of dry cell mass at full
     respiration (no lactate), i.e. 0.32 kg per kg wet: about $0.13/kg at $0.40/kg.
   * Buffers and mineral salts are left out of his medium cost as low-cost (fn. 26).

  OUR BEST GUESSES (labelled as ours, NOT attributed to Humbird):
   * aa_intensity: an earlier draft used 1.5 kg AA/kg biomass; Humbird's
     stoichiometry is ~0.26 kg/kg wet of pure amino acids (0.85 dry), and 0.337 kg/kg
     of soy hydrolysate to supply them (Table 3.5). The floor prices hydrolysate, so
     it uses 0.337. Humbird's $3.4 residual also buys free glutamine and tyrosine
     ($1.74 + $0.88); the floor leaves them out, assuming glutamine-synthetase cells
     (standard in CHO) and tyrosine from the hydrolysate. (Low impact either way next
     to the plant term.)
   * "~$0.75/kg AA at CHO-grade efficiency" and "4x" were draft extrapolations
     with NO basis in Humbird; they are model assumptions, not citations.

The floor (see cost_floor):
  * amino acids are irreducible feedstock: 0.337 kg/kg wet of hydrolysate x $2/kg =
    ~$0.67/kg.
  * glucose: anabolism (lipid, carbohydrate, nucleotides) plus the glucose respired
    to pay the cells' metabolic power while they grow. Humbird's full-respiration
    stoichiometry gives 0.32 kg/kg wet (half of it anabolic; faster growth lowers the
    rest), x $0.40/kg (GFI & Hawkwood 2025, US Midwest) = ~$0.13/kg. Salts, buffer,
    vitamins and trace elements: ~$0.9/kg, an assumption (the rest of an earlier $1
    glucose-and-other guess; Humbird treats them as low-cost). Together ~$1.7/kg.
    This is comparable to, not far below, conventional chicken's feed bill: US
    broilers eat ~4.6 kg of feed per kg of edible meat (parents included), ~$1.4/kg
    of edible meat in 2025 (~$1.9 in the EU, 2024), from NCC, Aviagen, USDA NASS and
    Wageningen data (pf-tea, data/evidence/feed.yaml). (The "9 cal in per 1 out" line
    is a CALORIE metric and overstates the headroom; by MASS the bird is efficient.)
    So cultivated meat has no order-of-magnitude feedstock advantage over the bird.
  * running a plant: capital/labour/maintenance/utilities do not go to zero.
    floor_physics.py derives this term from oxygen and CO2 physics and published
    plant costs in 2025 prices. THE FLOOR: a sterile plant without clean rooms
    ($810k per m3, Humbird's plant with a sanitary hall) plus a hoped-for device
    to hold cells back, 20 m3 tanks in perfusion at 120 g/L, efficient cells:
    ~$12.4/kg. THE FRONTIER: the same in a plant at the cost of built microbial
    fermentation plants ($190k per m3): ~$5.7/kg; not costed or built for animal
    cells. THE CAUTIOUS CASE: Humbird's pharma-style plant, tanks drained and
    refilled: ~$17.7/kg.

Result preview (defaults): as reported, with capital ~$34/kg; medium at $0.2/L
~$25/kg; + efficient cells ~$23/kg; floor ~$14/kg (band ~$7.4-19.4). With a $5/kg
additive markup against a $12/kg commodity price, parity (R=1) needs biomass
<= $7/kg. The floor with plants that have been costed for animal cells is about
twice that. The frontier case, a plant at the cost of today's microbial
fermentation plants, sits at the parity line (~$7.4/kg).

Usage
-----
    python cost_model.py --no-latex
    python cost_model.py --media-price 0.2 --efficiency 0.25
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np
import matplotlib.pyplot as plt

from common import setup_style, _save
from inputs import value, prior, AA_FLOOR, GLUCOSE_OTHER_FLOOR, PLANT_CONFIGS
from price_ratio import p_cult as _p_cult, ratio as _ratio, parity_cost as _parity_cost

# The medium's IRREDUCIBLE feedstock: amino acids + bulk glucose, which the cells
# must physically consume. Medium cost cannot fall below this however cheap the
# medium gets — but it is STOICHIOMETRIC, so it does NOT scale with media
# efficiency (using less medium does not let the cells eat fewer amino acids).
FEEDSTOCK_FLOOR = AA_FLOOR + GLUCOSE_OTHER_FLOOR   # ~0.67 + (0.13 + 0.9) = 1.70 $/kg


# ----------------------------------------------------------------------------
# Parameters  (defaults + sources live in inputs.py — the datasheet)
# ----------------------------------------------------------------------------
@dataclass
class CostParams:
    # --- operating cost: media ---------------------------------------------
    media_intensity: float = value("media_intensity")  # L medium per kg wet [SuperMeat]
    media_price: float = value("media_price")          # $/L medium          [SuperMeat] -> tweak to 0.2
    efficiency: float = value("efficiency")            # media-use multiplier; 0.25 = CHO-grade

    # --- operating cost: everything else -----------------------------------
    nonmedia_cost: float = value("overhead")           # $/kg everything but medium [SuperMeat, with depreciation]

    # --- floor inputs (irreducible) ----------------------------------------
    #   aa_intensity is stoichiometric (does NOT scale with media efficiency); an
    #   earlier draft used 1.5 here, ~6x too high — see module docstring.
    aa_intensity: float = value("aa_intensity")        # kg hydrolysate/kg wet  [Humbird Table 3.5]
    aa_bulk_price: float = value("aa_bulk_price")      # $/kg bulk plant hydrolysate [Humbird]
    glucose_other_floor: float = GLUCOSE_OTHER_FLOOR   # $/kg glucose [derived] + salts etc. [assumed]
    plant_floor: float = value("plant_floor")          # $/kg minimal plant cost at scale [floor_physics]
    eff_best: float = value("eff_best")                # CHO-grade media-VOLUME multiplier; SCENARIO only

    # --- conversion to the price ratio -------------------------------------
    markup_add: float = value("markup_add")            # $/kg additive biomass->retail [assumed]
    p_conv: float = value("p_conv")                    # conventional commodity price, $/kg [market]


# ----------------------------------------------------------------------------
# The cost model  (scalar OR numpy-array inputs — uncertainty.py reuses media_cost)
# ----------------------------------------------------------------------------
def media_cost(pr: CostParams, media_price=None, efficiency=None):
    """Media cost of 1 kg wet biomass, $/kg = litres of medium per kg x price per
    litre, floored at the irreducible feedstock.

        media_cost = max( FEEDSTOCK_FLOOR,  media_intensity * efficiency * media_price )

    The feedstock (amino acids + glucose the cells must physically eat) is
    stoichiometric and sets a hard floor (~$1.7/kg): medium can never cost less than
    its dissolved feedstock, i.e. media_price >= FEEDSTOCK_FLOOR/media_intensity
    (~$0.07/L). Above that floor it is simply litres x price. Accepts scalars or
    numpy arrays (Monte Carlo reuses it)."""
    mp = pr.media_price if media_price is None else media_price
    ef = pr.efficiency if efficiency is None else efficiency
    return np.maximum(FEEDSTOCK_FLOOR, pr.media_intensity * ef * mp)


def biomass_cost(pr: CostParams, media_price=None, efficiency=None):
    """Operating cost of 1 kg wet biomass, $/kg. Floored at the derived floor.
    np.maximum keeps this correct for scalar and array inputs alike."""
    raw = media_cost(pr, media_price, efficiency) + pr.nonmedia_cost
    return np.maximum(raw, cost_floor(pr))


def cost_floor(pr: CostParams) -> float:
    """The irreducible cost: stoichiometric amino-acid feedstock + bulk
    glucose/nutrients + the minimal cost of running a plant at scale. $/kg.

    The reducible parts (recombinant albumin/growth factors, single-use filters,
    small-scale capital) are assumed engineered toward zero; what remains is what
    the cells must physically eat plus the floor cost of operating a facility.

    The plant term is derived in floor_physics.py within Humbird's physical limits (oxygen and CO2
    transfer at 20 m3). It assumes efficient cells and a device to hold cells back that does not
    exist yet; see inputs.py `plant_floor` for what has and has not been shown.
    """
    aa = pr.aa_intensity * pr.aa_bulk_price   # 0.337*2 = 0.67 (stoichiometric, no eff knob)
    return aa + pr.glucose_other_floor + pr.plant_floor


def floor_band(pr: CostParams):
    """A band on the floor; the plant-overhead term is the least-constrained
    piece (it depends on the class of plant). (lo, central, hi)."""
    aa = pr.aa_intensity * pr.aa_bulk_price
    central = cost_floor(pr)
    # Plant term from floor_physics: the frontier (a plant at the cost of built microbial fermentation
    # plants; not shown for animal cells) up to the cautious case (Humbird's pharma-style plant, tanks
    # drained and refilled). Feedstock is held at its central value in both.
    lo = aa + pr.glucose_other_floor + value("plant_floor_lo")     # the frontier
    hi = aa + pr.glucose_other_floor + value("plant_floor_hi")     # the cautious case
    return lo, central, hi


# The price-ratio framing lives in price_ratio.py; these are thin CostParams
# adapters so cost_model can report R / parity off a CostParams without
# re-implementing (or duplicating) the markup + ratio arithmetic.
def p_cult(cost, pr: CostParams):
    return _p_cult(cost, pr.markup_add)


def ratio(cost, pr: CostParams):
    return _ratio(cost, pr.markup_add, pr.p_conv)


def parity_cost(pr: CostParams) -> float:
    """Biomass cost at which retail price equals the conventional price."""
    return _parity_cost(pr.markup_add, pr.p_conv)


# ----------------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------------
def summarise(pr: CostParams) -> None:
    scenarios = [
        ("as reported, with capital (SuperMeat 2024)", pr.media_price, 1.0),
        ("medium -> 0.2 $/L",                        0.20,           1.0),
        ("efficient cells (4x less medium)",         pr.media_price, pr.eff_best),
        ("both (0.2 $/L + efficient cells)",         0.20,           pr.eff_best),
    ]
    print("  MEDIUM / CELL lever (plant held at the default), cells $/kg and R:")
    print("  scenario                                    cells $/kg   R=p_cult/p_conv")
    for name, mp, ef in scenarios:
        c = biomass_cost(pr, mp, ef)
        print(f"    {name:<42} {c:7.1f}        {ratio(c, pr):.2f}")

    print(f"\n  PLANT lever — three plant cases (medium held at ${pr.media_price:.2f}/L):")
    m = media_cost(pr, pr.media_price, 1.0)
    for label, oh in PLANT_CONFIGS.items():
        tot = m + oh
        print(f"    {label:<58} {tot:6.1f}        {ratio(tot, pr):.2f}")

    lo, ce, hi = floor_band(pr)
    print(f"\n  derived FLOOR: {ce:.1f} $/kg  (band {lo:.1f}-{hi:.1f})  "
          f"-> R = {ratio(ce, pr):.2f} (band {ratio(lo,pr):.2f}-{ratio(hi,pr):.2f})")
    print(f"    components: amino acids {pr.aa_intensity*pr.aa_bulk_price:.2f} + "
          f"glucose/other {pr.glucose_other_floor:.1f} + running a plant {pr.plant_floor:.1f} $/kg")
    pc = parity_cost(pr)
    print(f"  parity (R=1) needs biomass <= {pc:.1f} $/kg (= p_conv - markup_add). "
          f"Floor central {ce:.1f} {'<=' if ce <= pc else '>'} {pc:.1f}: "
          f"parity is {'reachable' if ce <= pc else 'about reachable only at the frontier (microbial-class plant costs)' if lo <= pc * 1.1 else 'out of reach on these plant costs'}.")


# ----------------------------------------------------------------------------
# Figure: biomass cost vs media price, both efficiencies, with the floor band
# ----------------------------------------------------------------------------
def fig_cost_vs_media(pr: CostParams, outdir, fmts) -> None:
    mp = np.linspace(0.1, 0.7, 200)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))

    for ef, lbl, c in [(1.0, "cells as reported", "#0173B2"),
                       (pr.eff_best, "efficient cells (4x less medium)", "#DE8F05")]:
        cost = np.array([biomass_cost(pr, m, ef) for m in mp])
        ax.plot(mp, cost, color=c, lw=2.0, label=lbl)

    # floor band
    lo, ce, hi = floor_band(pr)
    ax.axhspan(lo, hi, color="#029E73", alpha=0.12)
    ax.axhline(ce, ls="--", lw=1.0, color="#029E73")
    ax.text(0.6, ce + 0.4, f"floor ~{ce:.0f} $/kg", fontsize=7.5, color="#029E73")

    # parity line (biomass cost that yields R=1, additive markup)
    pc = parity_cost(pr)
    ax.axhline(pc, ls=":", lw=1.0, color="0.4")
    ax.text(0.34, pc + 0.4, f"price parity (R=1) at {pc:.0f} $/kg biomass",
            fontsize=7.5, color="0.4")

    # anchor points
    ax.scatter([pr.media_price], [biomass_cost(pr, pr.media_price, 1.0)], color="#0173B2", zorder=5, s=28)
    ax.axvline(0.20, ls=":", lw=0.6, color="0.7")
    ax.text(0.205, ax.get_ylim()[1]*0.92, "0.2 $/L target", fontsize=7, color="0.5")

    ax.set_xlabel(r"Medium price (\$/L)")
    ax.set_ylabel(r"Biomass cost (\$/kg wet)")
    ax.set_title("Cost vs medium price, with the floor")
    ax.legend(fontsize=8, frameon=False)
    _save(fig, outdir, "cost_vs_media", fmts)


# ----------------------------------------------------------------------------
# Figure: the two big cost levers — medium price (x) x reactor scale (lines) —
# with their reasonable ranges and the irreducible floor. A "version of 2".
# ----------------------------------------------------------------------------
def fig_cost_vs_inputs(pr: CostParams, outdir, fmts) -> None:
    """Biomass cost as a function of the two dominant cost inputs: medium price
    (x-axis, its reasonable range shaded) and the PLANT (one line per plant
    case). The floor band and the parity threshold are drawn so the reader sees
    that no single input combination reaches parity on the basic product."""
    lo, hi = prior("media_price")[1:3]              # the medium range the model samples (0.20 .. 1.00)
    mp = np.linspace(0.15, hi + 0.05, 200)
    fig, ax = plt.subplots(figsize=(7.2, 4.7))

    # one line per plant case (cells held at the reported efficiency 1.0)
    oh_hi, oh_def, oh_floor = (PLANT_CONFIGS[k] for k in PLANT_CONFIGS)       # dict order: cautious, default, floor
    for lbl, oh, c in [("floor plant cost",                            oh_floor, "#029E73"),
                       ("as reported, with capital (default)",        oh_def,   "#0173B2"),
                       ("cautious plant cost",                         oh_hi,    "#CC3311")]:
        ax.plot(mp, pr.media_intensity * 1.0 * mp + oh, color=c, lw=2.2, label=lbl)

    # the MEDIUM range the model samples
    ax.axvspan(lo, hi, color="0.82", alpha=0.40, zorder=0)
    ax.text((lo + hi) / 2, 2.0, f"medium range in the model\n{lo:.2f} to {hi:.2f} per litre",
            ha="center", fontsize=7, color="0.4")
    ax.scatter([pr.media_price], [pr.media_intensity * 1.0 * pr.media_price + oh_def], color="#0173B2",
               zorder=6, s=34, edgecolor="white", label=rf"reported (\${pr.media_price:.2f}/L)")

    # two reference lines: the irreducible floor and the parity threshold (biomass terms)
    ce = cost_floor(pr)
    ax.axhline(ce, ls="--", lw=1.2, color="#117733")
    ax.text(0.17, ce + 0.6, rf"irreducible floor $\sim$\${ce:.1f}/kg", fontsize=8, color="#117733")
    pc = parity_cost(pr)
    ax.axhline(pc, ls=":", lw=1.2, color="#CC3311")
    ax.text(0.17, pc - 1.7, f"parity needs biomass $\\leq$ \\${pc:.0f}/kg", fontsize=8, color="#CC3311")

    ax.set_ylim(0, 50)
    ax.set_xlabel(r"Medium price (\$/L)")
    ax.set_ylabel(r"Biomass cost (\$/kg wet)")
    ax.set_title("The two big cost levers: medium price (x) and reactor scale (lines)")
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    _save(fig, outdir, "cost_vs_inputs", fmts)


# ----------------------------------------------------------------------------
# Figure: the cost WATERFALL — where the cost goes, and what is irreducible
# ----------------------------------------------------------------------------
def fig_cost_waterfall(pr: CostParams, outdir, fmts) -> None:
    """Walk the cost down from the cautious plant case to the floor, one lever per step, so a
    reader SEES which lever moves the most ($) and where the floor is. Pulls media_cost / cost_floor /
    parity_cost / PLANT_CONFIGS — no hard-coded numbers."""
    oh_hi, oh_def, oh_floor = (PLANT_CONFIGS[k] for k in PLANT_CONFIGS)
    m_def = media_cost(pr, pr.media_price, 1.0)
    top      = m_def + oh_hi                                   # cautious plant, reported medium
    reported = m_def + oh_def                                  # the default
    cheap    = media_cost(pr, 0.2, 1.0) + oh_def               # cheaper medium
    eff      = media_cost(pr, 0.2, pr.eff_best) + oh_def       # + efficient cells
    floor = cost_floor(pr)
    aa = pr.aa_intensity * pr.aa_bulk_price
    m_ref, oh_ref = m_def, oh_def                              # the default, for the reference line below

    # waterfall: (label, top, bottom, colour) — full bar at the ends, floating steps between
    steps = [
        ("cautious plant\n(pharma-style,\nhalf density)",   top,      0.0,      "#949494"),
        ("plant as\ncompanies\nreport",                     top,      reported, "#0173B2"),
        (f"cheaper medium\n{pr.media_price:.2f}->0.2/L",      reported, cheap,    "#56B4E9"),
        ("efficient\ncells",                                cheap,    eff,      "#56B4E9"),
        ("floor plant and\nfloor-price\nmedium",            eff,      floor,    "#56B4E9"),
    ]
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    xs = range(len(steps) + 1)
    for x, (lbl, top, bot, col) in zip(xs, steps):
        ax.bar(x, top - bot, bottom=bot, width=0.62, color=col, alpha=0.9)
        if x > 0:                                    # connector from previous top
            ax.plot([x - 1 + 0.31, x - 0.31], [bot, bot], color="0.5", lw=0.8, ls="-")
        if x > 0:                                    # label the $ removed by this lever
            ax.text(x, top + 0.6, f"-{top-bot:.1f}", ha="center", fontsize=7.5,
                    color="0.25", fontweight="bold")
    # irreducible floor block, split into its components (the last bar)
    xf = len(steps)
    bottoms = [0.0, aa, aa + pr.glucose_other_floor]
    heights = [aa, pr.glucose_other_floor, pr.plant_floor]
    fcols = ["#117733", "#44AA99", "#999933"]
    for b, h, c in zip(bottoms, heights, fcols):
        ax.bar(xf, h, bottom=b, width=0.62, color=c, alpha=0.9)
    # label the irreducible components inside the floor block
    for b, h, lab in zip(bottoms, heights,
                         [f"amino acids \\${aa:.1f}", f"glucose, salts \\${pr.glucose_other_floor:.1f}",
                          f"plant overhead \\${pr.plant_floor:.0f}"]):
        ax.text(xf + 0.34, b + h / 2, lab, fontsize=6.5, va="center", color="0.3")
    ax.text(xf, floor + 0.6, f"FLOOR\n\\${floor:.1f}", ha="center", fontsize=7.5,
            color="#117733", fontweight="bold")

    # parity threshold line
    pc = parity_cost(pr)
    ax.axhline(pc, ls=":", lw=1.1, color="#CC3311")
    ax.text(len(steps) + 0.05, pc - 1.5, rf"parity threshold (biomass $\leq$ \${pc:.0f}/kg)",
            fontsize=7.5, color="#CC3311", ha="right")
    # the default (label on the right, over the low descended bars = clear space)
    ax.axhline(m_ref + oh_ref, ls="--", lw=0.8, color="0.6")
    ax.text(len(steps) + 0.3, m_ref + oh_ref + 0.5, f"as reported\n\\${m_ref + oh_ref:.0f}/kg",
            fontsize=7, color="0.5", ha="right")

    labels = [s[0] for s in steps] + ["irreducible\nfloor"]
    ax.set_xticks(list(xs))
    ax.set_xticklabels(labels, fontsize=7.5)
    ax.set_ylabel(r"Biomass cost (\$/kg wet)")
    ax.set_title("From the cautious case to the floor")
    _save(fig, outdir, "cost_waterfall", fmts)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outdir", default="figures")
    ap.add_argument("--media-price", type=float, default=None)
    ap.add_argument("--efficiency", type=float, default=None)
    ap.add_argument("--no-latex", action="store_true")
    ap.add_argument("--formats", default="png,pdf")
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

    setup_style(use_latex=not args.no_latex)
    fmts = [f.strip() for f in args.formats.split(",") if f.strip()]
    pr = CostParams()
    if args.media_price is not None:
        pr.media_price = args.media_price
    if args.efficiency is not None:
        pr.efficiency = args.efficiency

    print("Step 2 — cost model (per kg of real cells):")
    summarise(pr)
    fig_cost_vs_inputs(pr, args.outdir, fmts)
    fig_cost_vs_media(pr, args.outdir, fmts)
    fig_cost_waterfall(pr, args.outdir, fmts)
    print("Done.")
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
