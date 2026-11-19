#!/usr/bin/env python3
"""
Step 6 — Scaffolding: the structured product, and why premium seafood changes
the maths. (The most speculative rung — flagged loudly.)

Everything up to Rung 5 deliberately modelled the BASIC (minced, unstructured)
product, because no published TEA covers scaffolding. This rung relaxes that —
not because the data is now solid (it isn't), but because real companies
(Wildtype cultivated salmon, BlueNalu cultivated seafood) are building
*structured* products, and their strategy has a quantifiable logic worth seeing.

The cost of a structured product (rebuilt 2026-11-19, research_notes/structuring_cost.md)
--------------------------------
        structured_cost = (1 - scaffold_frac) * biomass_cost + scaffold_cost
        scaffold_cost   = scaffold_frac[kg/kg] * material_price[$/kg] + process[$/kg]
        p_cult          = (structured_cost + markup_add) / (1 - retail_margin)
        R               = p_cult / p_conv_TARGET

The matrix REPLACES cells: a kilo of cut holds (1 - scaffold_frac) kg of cells. Companies now assemble cuts from
suspension-grown cells after harvest (Wildtype since 2023, Aleph since 2025, Upside 2026), not by growing tissue on a
scaffold in a second bioreactor.
  * MATRIX price: textured or extruded plant protein with binders, about $2/kg (1-5).
  * ASSEMBLY (process) cost: binding, setting, slicing and yield loss beyond the forming every product pays in the shop
    add-on, about $2/kg (0.5-7), from plant-protein
    extrusion and surimi forming. No study costs it for cultivated meat. Growing tissue on a scaffold would add about
    $10/kg (3-35) instead.
  * The larger unknown is the cell share: cuts sold so far are 10-30% cells; 80% is assumed here.

The strategic point (why premium matters)
------------------------------------------
Scaffolding adds cost, but a structured product is not compared to $12/kg
commodity meat -- it competes with PREMIUM cuts: premium fish ~$25/kg, sushi-
grade salmon ~$40/kg. The denominator p_conv is far larger, so the SAME absolute
scaffold cost lands at a much lower price RATIO. That is precisely the Wildtype /
BlueNalu bet: target an expensive conventional product, and the structuring cost
is absorbed by the high benchmark.

Run it for the current figures (the preview that stood here used the old $6 scaffold on a full kilo of cells).
So a structured cultivated-seafood product can reach price parity MORE easily
than a basic commodity-meat product -- the opposite of the naive intuition --
because the target is a $40/kg product, not a $12/kg one.

Usage
-----
    python scaffolding.py --no-latex
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np
import matplotlib.pyplot as plt

from common import setup_style, _save
from inputs import value, prior
from price_ratio import shelf_price


# conventional TARGET products a structured cultivated product could compete with
COMPARATORS = [
    ("commodity meat",          value("p_conv"),              "#949494"),
    ("premium fish (BlueNalu)", value("p_conv_premium_fish"), "#0173B2"),
    ("sushi salmon (Wildtype)", value("p_conv_sushi_salmon"), "#DE8F05"),
]


@dataclass
class ScaffoldParams:
    # --- inherited cost (from Rung 2) --------------------------------------
    biomass_cost: float = value("biomass_cost_nearterm")  # $/kg near-term (media $0.2/L, current cells)
    markup_add: float = value("markup_add")   # $/kg per-kg costs to the shelf; the retail margin is inputs.py's

    # --- plant-protein matrix (structuring_cost.md) -------------------------
    scaffold_frac: float = value("scaffold_frac")    # kg plant-protein matrix and binder per kg cut (replaces cells)
    material_price: float = value("material_price")  # $/kg of matrix; band 1-5

    # --- assembly after harvest (analogues only, wide band) ----------------
    process_cost: float = value("process_cost")      # $/kg to assemble the cut beyond mince; band 0.5-7


def scaffold_cost(pr: ScaffoldParams, process=None, material=None) -> float:
    mat = pr.material_price if material is None else material
    proc = pr.process_cost if process is None else process
    return pr.scaffold_frac * mat + proc


def structured_R(pr: ScaffoldParams, p_conv: float, scaff: float | None = None) -> float:
    sc = scaffold_cost(pr) if scaff is None else scaff
    return shelf_price((1.0 - pr.scaffold_frac) * pr.biomass_cost + sc, pr.markup_add) / p_conv


# ----------------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------------
def summarise(pr: ScaffoldParams) -> None:
    sc = scaffold_cost(pr)
    print(f"  biomass ${pr.biomass_cost:.0f}/kg + scaffold ${sc:.0f}/kg "
          f"(material {pr.scaffold_frac*pr.material_price:.1f} + process {pr.process_cost:.0f}) "
          f"+ ${pr.markup_add:.1f}/kg to the shelf, over (1 - {value('retail_margin'):.0%}) = "
          f"p_cult ${shelf_price((1.0 - pr.scaffold_frac) * pr.biomass_cost + sc, pr.markup_add):.0f}/kg")
    print("  structured-product price ratio R vs different conventional targets:")
    for name, pc, _ in COMPARATORS:
        R = structured_R(pr, pc)
        verdict = "below parity" if R < 1 else ("~parity" if R < 1.15 else "uncompetitive")
        print(f"    vs {name:<26} (${pc:>4.0f}/kg)   R = {R:.2f}   ({verdict})")
    print("  -> targeting a PREMIUM product (high denominator) makes a structured "
          "product reach parity MORE easily than basic meat vs commodity, despite "
          "the added scaffold cost.")


# ----------------------------------------------------------------------------
# Figure: R vs scaffold cost, for each conventional target
# ----------------------------------------------------------------------------
def fig_scaffolding(pr: ScaffoldParams, outdir, fmts) -> None:
    scaff = np.linspace(0, 22, 200)
    fig, ax = plt.subplots(figsize=(6.6, 4.2))

    for name, pc, col in COMPARATORS:
        R = np.array([structured_R(pr, pc, s) for s in scaff])
        ax.plot(scaff, R, color=col, lw=2.0, label=f"vs {name} (\\${pc:.0f}/kg)")

    # parity line
    ax.axhline(1.0, ls="--", lw=0.9, color="0.35")
    ax.text(0.3, 1.03, "parity (R=1)", fontsize=7.5, color="0.35")

    # plausible scaffold-cost band — read the band ends from the process_cost / material_price
    # PRIORS (inputs.py) so the figure band always matches the sampled band, no drift.
    proc_lo, proc_hi = prior("process_cost")[1], prior("process_cost")[2]
    mat_lo, mat_hi = prior("material_price")[1], prior("material_price")[2]
    lo = scaffold_cost(pr, process=proc_lo, material=mat_lo)
    hi = scaffold_cost(pr, process=proc_hi, material=mat_hi)
    ax.axvspan(lo, hi, color="#029E73", alpha=0.10)
    ax.text((lo + hi) / 2, ax.get_ylim()[1] * 0.93,
            "plausible matrix + assembly cost\n(from plant-protein and surimi analogues)",
            fontsize=6.8, color="#029E73", ha="center", va="top")
    ax.axvline(scaffold_cost(pr), ls=":", lw=0.7, color="0.5")

    ax.set_xlabel(r"Matrix + assembly cost (\$/kg of cut), with the cells it replaces")
    ax.set_ylabel(r"Structured-product price ratio $R$")
    ax.set_title("Scaffolding vs a premium target: why Wildtype/BlueNalu chase seafood")
    ax.legend(fontsize=7.5, frameon=False)
    _save(fig, outdir, "scaffold_vs_premium", fmts)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outdir", default="figures")
    ap.add_argument("--biomass", type=float, default=None, help="biomass cost $/kg")
    ap.add_argument("--process", type=float, default=None, help="scaffold process cost $/kg")
    ap.add_argument("--no-latex", action="store_true")
    ap.add_argument("--formats", default="png,pdf")
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

    setup_style(use_latex=not args.no_latex)
    fmts = [f.strip() for f in args.formats.split(",") if f.strip()]
    pr = ScaffoldParams()
    if args.biomass is not None:
        pr.biomass_cost = args.biomass
    if args.process is not None:
        pr.process_cost = args.process

    print("Step 6 — scaffolding / structured products (MOST SPECULATIVE rung):")
    summarise(pr)
    fig_scaffolding(pr, args.outdir, fmts)
    print("Done.")
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
