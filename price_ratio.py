#!/usr/bin/env python3
"""
price_ratio.py — the price ratio R and the parity threshold (the model's framing).

This is the OUTPUT layer, not a cost model. It defines how a cultivated BIOMASS
cost becomes a retail price and a price ratio against conventional meat, and the
single threshold that decides whether parity is even reachable. It deliberately
contains NO cost mechanism and NO time axis: it takes a biomass cost as an INPUT.
`cost_model.py` produces that cost and feeds it here — so nothing introduced in
this module is ever substituted later (the model has no throwaway rungs).

        p_cult = biomass_cost + markup_add          (ADDITIVE markup, see below)
        R      = p_cult / p_conv
        parity (R = 1)  requires  biomass_cost <= p_conv - markup_add   <- THRESHOLD

Why the markup is ADDITIVE (and why that creates a hard threshold)
------------------------------------------------------------------
Processing, packaging, cold-chain distribution and retail margin are roughly
FIXED dollars per kg; they do not shrink in proportion as biomass gets cheaper.
A multiplicative markup would wrongly let the retail wedge vanish at low cost and
make parity look easy. Because the markup is a fixed addend, parity has a hard
cost THRESHOLD: biomass_cost <= p_conv - markup_add. Below it, parity is
reachable; above it, parity is impossible at ANY biomass cost.

That threshold — and therefore the entire "is parity reachable?" question — is
set by just two numbers, `markup_add` and `p_conv`. Both live in inputs.py, and
the verdict is sensitive to them (see MODEL.md): this is why they matter more
than the headline cost figure.

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
    markup_add: float = value("markup_add")   # $/kg additive biomass->retail [inputs.py]
    p_conv: float = value("p_conv")           # conventional commodity price, $/kg [inputs.py]


# ----------------------------------------------------------------------------
# The framing: cost -> price -> ratio, and the parity threshold
# (all functions take scalars OR numpy arrays)
# ----------------------------------------------------------------------------
def p_cult(cost, markup_add):
    """Retail price of the cultivated product, $/kg, from its biomass cost."""
    return cost + markup_add


def ratio(cost, markup_add, p_conv):
    """Price ratio R = p_cult / p_conv."""
    return p_cult(cost, markup_add) / p_conv


def parity_cost(markup_add, p_conv):
    """The biomass cost at which R = 1 — the parity THRESHOLD. Below it parity is
    reachable; above it, impossible at any biomass cost (additive markup)."""
    return p_conv - markup_add


# ----------------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------------
def summarise(rp: RatioParams) -> None:
    thr = parity_cost(rp.markup_add, rp.p_conv)
    print(f"  retail price = biomass_cost + markup_add(${rp.markup_add:.0f}/kg);  "
          f"R = retail / p_conv(${rp.p_conv:.0f}/kg)")
    print(f"  PARITY THRESHOLD: biomass_cost must be <= ${thr:.1f}/kg for R <= 1")
    costs = (5, 10, 15, 20, 25)
    print("  biomass cost $/kg :  " + "  ".join(f"{c:>4.0f}" for c in costs))
    print("  price ratio  R    :  " +
          "  ".join(f"{ratio(c, rp.markup_add, rp.p_conv):>4.2f}" for c in costs))


# ----------------------------------------------------------------------------
# Figure: R as a function of biomass cost, with the parity threshold
# ----------------------------------------------------------------------------
def fig_ratio_vs_cost(rp: RatioParams, outdir: str, fmts) -> None:
    cost = np.linspace(3.0, 28.0, 200)
    R = ratio(cost, rp.markup_add, rp.p_conv)
    fig, ax = plt.subplots(figsize=(6.0, 3.8))

    ax.plot(cost, R, color="#0173B2", lw=2.0,
            label=r"$R=(\mathrm{cost}+\mathrm{markup})/p_{\rm conv}$")

    ax.axhline(1.0, ls="--", lw=0.9, color="0.35")
    ax.text(3.4, 1.03, "parity (R=1)", fontsize=7.5, color="0.35")

    thr = parity_cost(rp.markup_add, rp.p_conv)
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
