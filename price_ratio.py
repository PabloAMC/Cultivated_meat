#!/usr/bin/env python3
"""
price_ratio.py — the price ratio R and the parity threshold (the model's framing).

This is the OUTPUT layer, not a cost model. It defines how a cultivated BIOMASS
cost becomes a retail price and a price ratio against conventional meat, and the
single threshold that decides whether parity is even reachable. It deliberately
contains NO cost mechanism and NO time axis: it takes a biomass cost as an INPUT.
`cost_model.py` produces that cost and feeds it here — so nothing introduced in
this module is ever substituted later (the model has no throwaway rungs).

        p_cult = (biomass_cost + markup_add) / (1 - retail_margin)     (MIXED, see below)
        R      = p_cult / p_conv
        parity (R = 1)  requires  biomass_cost <= p_conv * (1 - retail_margin) - markup_add

Why the shelf price is per-kg costs plus a percentage margin
------------------------------------------------------------
Until 2026-11-18 the model added a flat $5/kg. The evidence (research_notes/retail_markup_form.md) says the
wholesale-to-retail spread has two parts:
  * per-kg costs (forming, packing, cold chain, distribution, store handling) that do not grow with the product's
    price: retail meat prices move about dollar for dollar with wholesale prices over 1-5 years (USDA ERS, 1970-2025),
    not by the 1.7-2.5 times a pure percentage markup would give;
  * the retailer's gross margin, set as a percentage of the shelf price (US meat departments about 28-32%), so a
    product that costs several times more carries a larger margin in dollars.
A pure percentage on the whole spread (the old audit's (cost + 1)/(1 - 0.45)) double-counts the per-kg part; a flat
$/kg leaves out the margin's growth with price. Parity still has a hard cost THRESHOLD,
p_conv * (1 - retail_margin) - markup_add, set by three numbers in inputs.py.

Usage
-----
    python price_ratio.py --no-latex
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np
import matplotlib.pyplot as plt

from common import setup_style, _save
from inputs import value


# ----------------------------------------------------------------------------
# Parameters  (defaults + sources live in inputs.py — the datasheet)
# ----------------------------------------------------------------------------
@dataclass
class RatioParams:
    markup_add: float = value("markup_add")   # $/kg per-kg costs from cells to the shelf [inputs.py]
    retail_margin: float = value("retail_margin")   # retailer's gross margin, share of the shelf price [inputs.py]
    p_conv: float = value("p_conv")           # conventional commodity price, $/kg [inputs.py]


# ----------------------------------------------------------------------------
# The framing: cost -> price -> ratio, and the parity threshold
# (all functions take scalars OR numpy arrays)
# ----------------------------------------------------------------------------
def shelf_price(cost, markup_add=None, retail_margin=None):
    """Shelf price of a kilo of product from its cost before the shelf, $/kg: per-kg costs plus the retailer's
    percentage margin. THE one place this rule lives in Python (the page mirrors it as shelfPrice in its engine).
    Scalars or numpy arrays; None takes the inputs.py value."""
    a = value("markup_add") if markup_add is None else markup_add
    m = value("retail_margin") if retail_margin is None else retail_margin
    return (cost + a) / (1.0 - m)


def cost_from_shelf(price, markup_add=None, retail_margin=None):
    """Inverse of shelf_price: the cost before the shelf that gives this shelf price."""
    a = value("markup_add") if markup_add is None else markup_add
    m = value("retail_margin") if retail_margin is None else retail_margin
    return price * (1.0 - m) - a


def p_cult(cost, markup_add, retail_margin=None):
    """Retail price of the cultivated product, $/kg, from its biomass cost."""
    return shelf_price(cost, markup_add, retail_margin)


def ratio(cost, markup_add, p_conv, retail_margin=None):
    """Price ratio R = p_cult / p_conv."""
    return p_cult(cost, markup_add, retail_margin) / p_conv


def parity_cost(markup_add, p_conv, retail_margin=None):
    """The biomass cost at which R = 1 — the parity THRESHOLD. Below it parity is
    reachable; above it, impossible at any biomass cost."""
    return cost_from_shelf(p_conv, markup_add, retail_margin)


# ----------------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------------
def summarise(rp: RatioParams) -> None:
    thr = parity_cost(rp.markup_add, rp.p_conv, rp.retail_margin)
    print(f"  retail price = (biomass_cost + ${rp.markup_add:.1f}/kg) / (1 - {rp.retail_margin:.0%} margin);  "
          f"R = retail / p_conv(${rp.p_conv:.0f}/kg)")
    print(f"  PARITY THRESHOLD: biomass_cost must be <= ${thr:.1f}/kg for R <= 1")
    costs = (5, 10, 15, 20, 25)
    print("  biomass cost $/kg :  " + "  ".join(f"{c:>4.0f}" for c in costs))
    print("  price ratio  R    :  " +
          "  ".join(f"{ratio(c, rp.markup_add, rp.p_conv, rp.retail_margin):>4.2f}" for c in costs))


# ----------------------------------------------------------------------------
# Figure: R as a function of biomass cost, with the parity threshold
# ----------------------------------------------------------------------------
def fig_ratio_vs_cost(rp: RatioParams, outdir: str, fmts) -> None:
    cost = np.linspace(3.0, 28.0, 200)
    R = ratio(cost, rp.markup_add, rp.p_conv, rp.retail_margin)
    fig, ax = plt.subplots(figsize=(6.0, 3.8))

    ax.plot(cost, R, color="#0173B2", lw=2.0,
            label=r"$R=\frac{(\mathrm{cost}+a)/(1-m)}{p_{\rm conv}}$")

    ax.axhline(1.0, ls="--", lw=0.9, color="0.35")
    ax.text(3.4, 1.03, "parity (R=1)", fontsize=7.5, color="0.35")

    thr = parity_cost(rp.markup_add, rp.p_conv, rp.retail_margin)
    ax.axvline(thr, ls=":", lw=1.0, color="#029E73")
    ax.text(thr + 0.3, ax.get_ylim()[1] * 0.9,
            f"parity threshold\nbiomass $\\leq$ \\${thr:.0f}/kg",
            fontsize=7.5, color="#029E73", va="top")

    ax.set_xlabel(r"Biomass cost (\$/kg wet)")
    ax.set_ylabel(r"Price ratio  $R = p_{\rm cult}/p_{\rm conv}$")
    ax.set_title("From biomass cost to the price ratio (and the parity threshold)")
    ax.legend(fontsize=8, frameon=False)
    _save(fig, outdir, "ratio_vs_cost", fmts)


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
    rp = RatioParams()

    print("price_ratio — R and the parity threshold (no cost mechanism):")
    summarise(rp)
    fig_ratio_vs_cost(rp, args.outdir, fmts)
    print("Done.")
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
