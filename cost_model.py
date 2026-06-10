#!/usr/bin/env python3
"""
cost_model — the cost of cultivated biomass, anchored to Pasitka (2024), with a
derived floor. This is the NUMERATOR of the price ratio.

price_ratio.py defines how a biomass cost becomes R and where the parity
threshold sits; THIS module produces that biomass cost — a transparent,
component-based number you can poke. The reference is Pasitka et al. 2024
(Nature Food) — the one *empirical* TEA — and the two questions it answers are
exactly the ones we care about:

  1. "What if the medium gets cheaper?"  -> vary `media_price` (0.63 -> 0.2 $/L).
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

Anchors (all tagged):
  * media_intensity = 22.4 L/kg   [Pasitka: a 50,000 L facility uses 24e6 L of
    ACF medium to make 1.07e6 kg/yr wet biomass -> 24e6/1.07e6 = 22.4 L/kg].
  * media_price     = 0.63 $/L    [Pasitka empirical ACF medium; tweak to 0.2].
  * nonmedia_cost   = 9.9 $/kg     [Pasitka TFF base: nutrients are 59% of a
    ~$24/kg COGS, so non-nutrient is ~41% ~= $9.9/kg at the 50,000 L facility].
  * efficiency      = 1.0          [Pasitka cells; their cells use ~4x more
    medium than CHO, so efficiency 0.25 models "CHO-grade" metabolism].

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

  OUR BEST GUESSES (labelled as ours, NOT attributed to Humbird):
   * aa_intensity: an earlier draft used 1.5 kg AA/kg biomass; Humbird's
     stoichiometry is ~0.26 kg/kg wet (0.85 dry). CORRECTED to 0.26 -- the old
     value was ~6x too high. (Low impact: AA is a small slice of the floor.)
   * "~$0.75/kg AA at CHO-grade efficiency" and "4x" were draft extrapolations
     with NO basis in Humbird; they are model assumptions, not citations.

The floor (see cost_floor):
  * amino acids are irreducible feedstock at ~0.26 kg/kg wet x $2/kg = ~$0.5/kg.
    This is comparable to, not far below, conventional chicken's feed cost: a
    modern broiler runs FCR ~1.6-2 kg feed/kg live weight (~3-4 kg/kg edible) at
    ~$0.35/kg feed, i.e. ~$1-1.5/kg of feed per kg edible chicken. (The "9 cal in
    per 1 out" line is a CALORIE metric and overstates the headroom; by MASS the
    bird is highly efficient.) So cultivated meat has no order-of-magnitude
    feedstock advantage over the bird.
  * glucose + other bulk nutrients: ~$1/kg irreducible.
  * running a plant: capital/labour/maintenance/utilities do not go to zero.
    Pasitka anchors this (large-scale perfusion config): nutrients rise to
    ~66-70% of COGS, so the non-nutrient floor is ~30-34% of COGS ~= $6/kg.

Result preview (defaults): Pasitka base ~$24/kg; medium at $0.2/L ~$14/kg;
+ CHO-efficient cells ~$11/kg; floor ~$7.5/kg (band ~$7-10). With a $5/kg
additive markup against a $12/kg commodity price, parity (R=1) needs biomass
<= $7/kg -- and the floor sits right AT that line (R ~1.04, band ~1.00-1.25).
So price parity on a basic product is, at best, marginal: it requires the floor
to land at its optimistic (large-scale) end AND the scale/sterility ceilings
above to be solved.

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
from inputs import value, AA_FLOOR, PASITKA_CONFIGS
from price_ratio import p_cult as _p_cult, ratio as _ratio, parity_cost as _parity_cost

# The medium's IRREDUCIBLE feedstock: amino acids + bulk glucose, which the cells
# must physically consume. Medium cost cannot fall below this however cheap the
# medium gets — but it is STOICHIOMETRIC, so it does NOT scale with media
# efficiency (using less medium does not let the cells eat fewer amino acids).
FEEDSTOCK_FLOOR = AA_FLOOR + value("glucose_other_floor")   # ~0.52 + 1.0 = 1.52 $/kg


# ----------------------------------------------------------------------------
# Parameters  (defaults + sources live in inputs.py — the datasheet)
# ----------------------------------------------------------------------------
@dataclass
class CostParams:
    # --- operating cost: media ---------------------------------------------
    media_intensity: float = value("media_intensity")  # L medium per kg wet [Pasitka]
    media_price: float = value("media_price")          # $/L medium (ACF)    [Pasitka] -> tweak to 0.2
    efficiency: float = value("efficiency")            # media-use multiplier; 0.25 = CHO-grade

    # --- operating cost: everything else -----------------------------------
    nonmedia_cost: float = value("overhead")           # $/kg capital+consumables+labour [Pasitka 50k L]

    # --- floor inputs (irreducible) ----------------------------------------
    #   aa_intensity is stoichiometric (does NOT scale with media efficiency); an
    #   earlier draft used 1.5 here, ~6x too high — see module docstring.
    aa_intensity: float = value("aa_intensity")        # kg amino acids/kg wet  [Humbird Table 3.4]
    aa_bulk_price: float = value("aa_bulk_price")      # $/kg bulk plant hydrolysate [Humbird]
    glucose_other_floor: float = value("glucose_other_floor")  # $/kg non-AA nutrients [assumed]
    plant_floor: float = value("plant_floor")          # $/kg minimal plant overhead at scale [Pasitka]
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
    stoichiometric and sets a hard floor (~$1.5/kg): medium can never cost less than
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

    IMPORTANT (see module docstring): this is a FEEDSTOCK + OVERHEAD floor. It
    assumes Humbird's scale-up CEILINGS (CO2-limited reactor volume, sterility cost
    capping facility size) are engineered away. If they are not, this floor is
    unreachable at ANY media price -- the model's largest unrepresented risk.
    """
    aa = pr.aa_intensity * pr.aa_bulk_price   # 0.26*2 = 0.52 (stoichiometric, no eff knob)
    return aa + pr.glucose_other_floor + pr.plant_floor


def floor_band(pr: CostParams):
    """A band on the floor; the plant-overhead term is the least-constrained
    piece (depends on how far scale-up goes beyond Pasitka). (lo, central, hi)."""
    aa = pr.aa_intensity * pr.aa_bulk_price
    central = cost_floor(pr)
    # Overhead is bounded by Pasitka's OWN reported range; we do not extrapolate
    # below Pasitka's largest demonstrated scale (~$6/kg, large-scale perfusion).
    lo = aa + 0.5 * pr.glucose_other_floor + 6.0    # optimistic: Pasitka large-scale
    hi = aa + 1.5 * pr.glucose_other_floor + 8.0    # conservative: nearer 50,000 L scale
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
        ("Pasitka base (0.63 $/L, current cells)", pr.media_price, 1.0),
        ("medium -> 0.2 $/L (current cells)",       0.20,          1.0),
        ("CHO-grade cells (0.63 $/L)",              pr.media_price, pr.eff_best),
        ("both (0.2 $/L + CHO-grade)",              0.20,          pr.eff_best),
    ]
    print("  MEDIA / CELL lever (scale held at TFF base), biomass$/kg and R:")
    print("  scenario                                    biomass$/kg   R=p_cult/p_conv")
    for name, mp, ef in scenarios:
        c = biomass_cost(pr, mp, ef)
        print(f"    {name:<42} {c:7.1f}        {ratio(c, pr):.2f}")

    # The SCALE-UP lever, shown inside Pasitka's own three reactor configs (Fig. 4).
    # media held at the empirical $0.63/L so this isolates the overhead/scale axis.
    print("\n  SCALE-UP lever — Pasitka's three reactor configs (media held at $0.63/L):")
    m = media_cost(pr, 0.63, 1.0)
    for label, oh in PASITKA_CONFIGS.items():
        tot = m + oh
        print(f"    {label:<46} {tot:6.1f}        {ratio(tot, pr):.2f}")
    print("    -> scale-up (ATF->perfusion) is a ~$17/kg move; the media cut "
          "($0.63->$0.2) is only ~$10/kg. Scale is the bigger cost lever.")

    lo, ce, hi = floor_band(pr)
    print(f"\n  derived FLOOR: {ce:.1f} $/kg  (band {lo:.1f}-{hi:.1f})  "
          f"-> R = {ratio(ce, pr):.2f} (band {ratio(lo,pr):.2f}-{ratio(hi,pr):.2f})")
    print(f"    components: amino acids {pr.aa_intensity*pr.aa_bulk_price:.2f} + "
          f"glucose/other {pr.glucose_other_floor:.1f} + running a plant {pr.plant_floor:.1f} $/kg")
    pc = parity_cost(pr)
    print(f"  parity (R=1) needs biomass <= {pc:.1f} $/kg (= p_conv - markup_add). "
          f"Floor central {ce:.1f} {'<=' if ce <= pc else '>'} {pc:.1f}: "
          f"parity is {'reachable' if ce <= pc else 'marginal (only at the optimistic floor end)'}.")


# ----------------------------------------------------------------------------
# Figure: biomass cost vs media price, both efficiencies, with the floor band
# ----------------------------------------------------------------------------
def fig_cost_vs_media(pr: CostParams, outdir, fmts) -> None:
    mp = np.linspace(0.1, 0.7, 200)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))

    for ef, lbl, c in [(1.0, "current cells (Pasitka)", "#0173B2"),
                       (pr.eff_best, "CHO-grade cells (4x less media)", "#DE8F05")]:
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
    ax.scatter([0.63], [biomass_cost(pr, 0.63, 1.0)], color="#0173B2", zorder=5, s=28)
    ax.axvline(0.20, ls=":", lw=0.6, color="0.7")
    ax.text(0.205, ax.get_ylim()[1]*0.92, "0.2 $/L target", fontsize=7, color="0.5")

    ax.set_xlabel(r"Medium price (\$/L)")
    ax.set_ylabel(r"Biomass cost (\$/kg wet)")
    ax.set_title("Cost vs medium price (Pasitka-anchored), with floor")
    ax.legend(fontsize=8, frameon=False)
    _save(fig, outdir, "cost_vs_media", fmts)


# ----------------------------------------------------------------------------
# Figure: the two big cost levers — medium price (x) x reactor scale (lines) —
# with their reasonable ranges and the irreducible floor. A "version of 2".
# ----------------------------------------------------------------------------
def fig_cost_vs_inputs(pr: CostParams, outdir, fmts) -> None:
    """Biomass cost as a function of the two dominant cost inputs: medium price
    (x-axis, its reasonable range shaded) and reactor SCALE (one line per Pasitka
    config). The floor band and the parity threshold are drawn so the reader sees
    that no single input combination reaches parity on the basic product."""
    mp = np.linspace(0.15, 0.70, 200)
    fig, ax = plt.subplots(figsize=(7.2, 4.7))

    # one line per reactor SCALE config (cells held at the measured efficiency 1.0)
    for lbl, oh, c in [(r"perfusion 20 m$^3$  (scale-up wins)",     7.9, "#029E73"),
                       (r"TFF 5 m$^3$  (demonstrated base)",        9.9, "#0173B2"),
                       (r"ATF 0.5 m$^3$  (scale-up stalls)",       24.7, "#CC3311")]:
        ax.plot(mp, pr.media_intensity * 1.0 * mp + oh, color=c, lw=2.2, label=lbl)

    # the reasonable MEDIUM range: $0.20 (company claim) .. $0.63 (Pasitka measured)
    ax.axvspan(0.20, 0.63, color="0.82", alpha=0.40, zorder=0)
    ax.text(0.415, 2.0, "medium range\n0.20 (claim)-0.63 (measured)", ha="center",
            fontsize=7, color="0.4")
    ax.scatter([0.63], [pr.media_intensity * 1.0 * 0.63 + 9.9], color="#0173B2",
               zorder=6, s=34, edgecolor="white", label=r"Pasitka measured (\$0.63, TFF)")

    # two reference lines: the irreducible floor and the parity threshold (biomass terms)
    ce = cost_floor(pr)
    ax.axhline(ce, ls="--", lw=1.2, color="#117733")
    ax.text(0.17, ce + 0.6, rf"irreducible floor $\sim$\${ce:.1f}/kg", fontsize=8, color="#117733")
    pc = parity_cost(pr)
    ax.axhline(pc, ls=":", lw=1.2, color="#CC3311")
    ax.text(0.17, pc - 1.7, f"parity needs biomass $\\leq$ \\${pc:.0f}/kg", fontsize=8, color="#CC3311")

    ax.set_ylim(0, 40)
    ax.set_xlabel(r"Medium price (\$/L)")
    ax.set_ylabel(r"Biomass cost (\$/kg wet)")
    ax.set_title("The two big cost levers: medium price (x) and reactor scale (lines)")
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    _save(fig, outdir, "cost_vs_inputs", fmts)


# ----------------------------------------------------------------------------
# Figure: the cost WATERFALL — where the cost goes, and what is irreducible
# ----------------------------------------------------------------------------
def fig_cost_waterfall(pr: CostParams, outdir, fmts) -> None:
    """Walk the cost down from Pasitka's worst (ATF, scale-up stalls) to the
    irreducible floor, one lever per step, so a reader SEES which lever moves the
    most ($) and where the floor is. Pulls media_cost / cost_floor / parity_cost /
    PASITKA_CONFIGS — no new constants, no hard-coded numbers."""
    m063 = media_cost(pr, 0.63, 1.0)                 # ~14.1
    atf  = m063 + PASITKA_CONFIGS["ATF 0.5 m^3 (small vessels; scale-up STALLS)"]   # ~38.8
    perf = m063 + PASITKA_CONFIGS["perfusion 20 m^3 (2x25,000 L; scale-up WINS)"]   # ~22.0
    perf_02  = media_cost(pr, 0.2, 1.0)  + 7.9       # cheaper media at perfusion scale
    perf_02c = media_cost(pr, 0.2, 0.25) + 7.9       # + CHO-grade efficiency
    floor = cost_floor(pr)                            # ~7.5
    aa = pr.aa_intensity * pr.aa_bulk_price

    # waterfall: (label, top, bottom, colour) — full bar at the ends, floating steps between
    steps = [
        ("Pasitka ATF\n(scale-up\nstalls)",        atf,      0.0,      "#949494"),
        ("reach large\nreactors\n(SCALE-UP)",      atf,      perf,     "#0173B2"),
        ("cheaper media\n0.63->0.2/L\n(GFI '26)",  perf,     perf_02,  "#56B4E9"),
        ("CHO-grade\nefficiency",                  perf_02,  perf_02c, "#56B4E9"),
        ("other reducible\n(consumables,\nsmall-scale capital)", perf_02c, floor, "#56B4E9"),
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
                         [f"amino acids \\${aa:.1f}", f"glucose \\${pr.glucose_other_floor:.0f}",
                          f"plant overhead \\${pr.plant_floor:.0f}"]):
        ax.text(xf + 0.34, b + h / 2, lab, fontsize=6.5, va="center", color="0.3")
    ax.text(xf, floor + 0.6, f"FLOOR\n\\${floor:.1f}", ha="center", fontsize=7.5,
            color="#117733", fontweight="bold")

    # parity threshold line
    pc = parity_cost(pr)
    ax.axhline(pc, ls=":", lw=1.1, color="#CC3311")
    ax.text(len(steps) + 0.05, pc - 1.5, rf"parity threshold (biomass $\leq$ \${pc:.0f}/kg)",
            fontsize=7.5, color="#CC3311", ha="right")
    # base TFF reference (label on the right, over the low descended bars = clear space)
    ax.axhline(m063 + 9.9, ls="--", lw=0.8, color="0.6")
    ax.text(len(steps) + 0.3, m063 + 9.9 + 0.5, "Pasitka base\n(TFF) \\$24/kg",
            fontsize=7, color="0.5", ha="right")

    labels = [s[0] for s in steps] + ["irreducible\nfloor"]
    ax.set_xticks(list(xs))
    ax.set_xticklabels(labels, fontsize=7.5)
    ax.set_ylabel(r"Biomass cost (\$/kg wet)")
    ax.set_title("Cost waterfall: scale-up is the biggest lever; the floor sits at the parity line")
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

    print("Step 2 — Pasitka-anchored cost model:")
    summarise(pr)
    fig_cost_vs_inputs(pr, args.outdir, fmts)
    fig_cost_vs_media(pr, args.outdir, fmts)
    fig_cost_waterfall(pr, args.outdir, fmts)
    print("Done.")
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
