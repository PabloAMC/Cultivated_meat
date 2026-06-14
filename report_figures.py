#!/usr/bin/env python3
"""
report_figures — builds the curated figure set for the report (one command).

The per-rung modules each emit diagnostic figures; this assembles the small,
well-formatted set the report actually uses, in story order:

  Output 1 — cost
    1. cost_vs_inputs          the two big cost levers (medium price x reactor scale) + floor
    2. cost_waterfall          where the cost goes; scale-up is the biggest single step
  Levers
    3. sensitivity_tornado_share  which knobs move the final share most
  Output 2 — demand & share
    4. share_vs_ratio          the share a given price ratio buys (the willingness-to-pay curve)
    5. cost_paths_timing       penetration over 30 yr by cost-milestone path (the cost->time coupling)
    6-9. penetration_by_type_{us,eu,china,global}  share BY TYPE OF MEAT (price vs demand oppose)
    10. report_regional_band   total penetration band by region (volume & value)

    python report_figures.py --no-latex

Diagnostics (all other figures) are written to figures/diagnostics/ by
`make_diagnostics.py` / running the rung modules with --outdir figures/diagnostics.
"""

from __future__ import annotations

import argparse
import numpy as np
import matplotlib.pyplot as plt

from common import setup_style, _save
from cost_model import CostParams, fig_cost_vs_inputs, fig_cost_waterfall
from market_share import DemandParams, fig_share_vs_ratio, fig_pb_milk_vs_meat
from adoption_timing import TimingParams, fig_cost_paths, fig_neophobia_time
from sensitivity import fig_tornado_share
from meat_market import fig_penetration, monte_carlo as pen_mc


# ----------------------------------------------------------------------------
# Output 2 headline — the total-penetration BAND by region (volume & value)
# ----------------------------------------------------------------------------
REGIONS = [("nigeria", "Nigeria"), ("india", "India"), ("global", "Global"),
           ("china", "China"), ("brazil", "Brazil"), ("us", "US"), ("eu", "Europe")]


def fig_regional_band(n, outdir, fmts) -> None:
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ys = np.arange(len(REGIONS))
    for (region, name), y in zip(REGIONS, ys):
        mc = pen_mc(region, n)
        for x, off, col in [(mc["vol"], 0.16, "#DE8F05"), (mc["val"], -0.16, "#0173B2")]:
            p10, p50, p90 = np.percentile(x, [10, 50, 90])
            ax.plot([p10, p90], [y + off, y + off], color=col, lw=4, alpha=0.5,
                    solid_capstyle="round")
            ax.plot(p50, y + off, "o", color=col, ms=6)
            ax.text(p90 + 0.4, y + off, rf"{p50:.0f}% [{p10:.0f}-{p90:.0f}]", va="center",
                    fontsize=7.5, color=col)
    ax.plot([], [], color="#DE8F05", lw=4, alpha=0.5, label="by volume (impact)")
    ax.plot([], [], color="#0173B2", lw=4, alpha=0.5, label=r"by value (\$ market)")
    ax.set_yticks(ys); ax.set_yticklabels([name for _, name in REGIONS])
    ax.set_xlabel(r"Total cultivated penetration of meat (%):  bars span P10 to P90, dot = P50")
    ax.set_title("Total penetration band by region (cost, standing and elasticity sampled)")
    ax.legend(fontsize=8, frameon=False, loc="upper right")
    _save(fig, outdir, "report_regional_band", fmts)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outdir", default="figures")
    ap.add_argument("--n", type=int, default=10000)
    ap.add_argument("--no-latex", action="store_true")
    ap.add_argument("--formats", default="png,pdf")
    args = ap.parse_args()
    setup_style(use_latex=not args.no_latex)
    fmts = [f.strip() for f in args.formats.split(",") if f.strip()]

    print("report_figures — building the curated report set:")
    fig_cost_vs_inputs(CostParams(), args.outdir, fmts)       # 1 cost levers + floor
    fig_cost_waterfall(CostParams(), args.outdir, fmts)       # 2 the cost waterfall
    fig_tornado_share("commodity", args.outdir, fmts)         # 3 levers on the final share
    fig_share_vs_ratio(DemandParams(), args.outdir, fmts)     # 4 the willingness-to-pay demand curve
    fig_pb_milk_vs_meat(DemandParams(), args.outdir, fmts)    # 4b PB-milk vs PB-meat (same machinery)
    fig_cost_paths(DemandParams(), TimingParams(), args.outdir, fmts)  # 5 cost->penetration over time
    fig_neophobia_time(args.outdir, fmts)                              # 5b timing: where it lands & how long
    for region, _ in REGIONS:                                 # 6-9 by type of meat
        fig_penetration(region, 0.0, args.outdir, fmts)
    fig_regional_band(args.n, args.outdir, fmts)              # 10 regional totals band
    print("Done — curated set (10): cost_vs_inputs, cost_waterfall, sensitivity_tornado_share,")
    print("       share_vs_ratio, cost_paths_timing, penetration_by_type_{us,eu,china,global},")
    print("       report_regional_band")


if __name__ == "__main__":
    main()
