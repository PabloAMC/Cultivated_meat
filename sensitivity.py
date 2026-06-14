#!/usr/bin/env python3
"""
sensitivity — which knobs move the answer most (the levers & bottlenecks).

This is the headline output for a TECHNICAL reader (GFI): a systematic ranking of
how much each model input drives the two outputs — the price ratio R and the
long-run cultivated share. It turns the model's narrative "cruxes" into a
quantified, sorted list, so the question "where should effort / dollars go?" has a
data answer rather than a story.

Two complementary views (deliberately separated, never contradictory):

  1. ONE-AT-A-TIME (OAT) tornado — the lead. Sweep each input from its low to its
     high plausible value (everything else held at its mode) and measure how far
     the output moves. Ranked longest-first, the bars form a "tornado": the top
     bars are the LEVERS/BOTTLENECKS, the bottom bars are settled. Interpretable
     with no distributional assumptions — each bar is literally "if this one
     number moves across its honest range, R moves THIS much."

  2. VARIANCE SHARE — the cross-check, REUSED VERBATIM from uncertainty.py's
     spread_contribution() (pin each input to its mode, measure how much the Monte
     Carlo P10-P90 width shrinks). Shown as a column in the table. Because the cost
     inputs enter R nearly linearly, the OAT ranking and the variance ranking
     agree — and the table proves it (same numbers, one source).

The reuse is strict: R is computed by uncertainty.R_from_inputs (the ONE cost->R
equation), and the variance column is uncertainty.spread_contribution — so this
module can never disagree with the Monte-Carlo rung.

    python sensitivity.py --no-latex
    python sensitivity.py --target sushi-salmon --no-latex
"""

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt

from common import setup_style, _save
from market_share import DemandParams, share
from uncertainty import (
    active_priors, TARGETS, R_from_inputs, monte_carlo, spread_contribution,
)

# demand-side inputs affect SHARE (through nothing on the cost side) — they do not
# move R. Everything else in the active prior set is a cost input that moves R.
DEMAND_INPUTS = ("eps_own", "theta_free_M", "accept_x")

# human-readable axis labels (the raw keys are code names; readers see these)
LABELS = {
    "overhead":      "reactor scale / overhead",
    "p_conv":        "conventional meat price",
    "efficiency":    "cell media-efficiency",
    "media_price":   "medium price",
    "markup_add":    "retail markup",
    "theta_free_M":  "mainstream slaughter-free value",
    "accept_x":      "cultivated taste-acceptance",
    "eps_own":       "price elasticity",
    "process_cost":  "scaffold process cost",
    "material_price": "scaffold material price",
    "scaffold_frac": "scaffold fraction",
}


def _modes(target: str) -> dict:
    """Every active input at its prior MODE — the tornado's all-at-mode baseline."""
    return {name: pri[3] for name, pri in active_priors(target).items()}


def _R_at(target: str, overrides: dict) -> float:
    """R with all inputs at mode except `overrides`. Reuses R_from_inputs."""
    m = _modes(target); m.update(overrides)
    scaf = TARGETS[target]["scaffold"]
    return float(R_from_inputs(
        m["media_price"], m["efficiency"], m["overhead"], m["markup_add"], m["p_conv"],
        scaffold_frac=m["scaffold_frac"] if scaf else 0.0,
        material_price=m["material_price"] if scaf else 0.0,
        process_cost=m["process_cost"] if scaf else 0.0))


def _share_at(target: str, overrides: dict) -> float:
    """Long-run cultivated share at the R implied by `overrides`. Cost inputs move
    share THROUGH R; demand inputs (eps_own, theta_free_M, accept_x) move it directly."""
    m = _modes(target); m.update(overrides)
    R = _R_at(target, overrides)
    return float(share(R, DemandParams(), theta_free_M=m["theta_free_M"],
                       accept_x=m["accept_x"], eps_own=m["eps_own"]))


# ----------------------------------------------------------------------------
# One-at-a-time tornado
# ----------------------------------------------------------------------------
def oat(target: str, which: str = "R"):
    """Returns (baseline, rows) where each row is
    (name, out_lo, out_hi, swing, optimistic_end_label). Sorted by swing desc.
    which='R' skips the demand inputs (they don't move R)."""
    fn = _R_at if which == "R" else _share_at
    base = fn(target, {})
    rows = []
    for name, (kind, lo, hi, mode, _note) in active_priors(target).items():
        if which == "R" and name in DEMAND_INPUTS:
            continue
        o_lo, o_hi = fn(target, {name: lo}), fn(target, {name: hi})
        swing = abs(o_hi - o_lo)
        # "optimistic" = the end that helps: lower R, or higher share
        better_lo = (o_lo < o_hi) if which == "R" else (o_lo > o_hi)
        opt = f"{name}={lo:g}" if better_lo else f"{name}={hi:g}"
        rows.append((name, o_lo, o_hi, swing, opt))
    return base, sorted(rows, key=lambda r: -r[3])


# ----------------------------------------------------------------------------
# Figures
# ----------------------------------------------------------------------------
def _tornado_fig(target, which, base, rows, title, fname, outdir, fmts):
    sc = 1.0 if which == "R" else 100.0                # share is plotted in PERCENT
    off = 0.015 if which == "R" else 0.5               # label x-offset (axis units)
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    rows = rows[::-1]                                   # largest swing at the TOP
    for i, (name, o_lo, o_hi, swing, _opt) in enumerate(rows):
        left, right = sorted([o_lo * sc, o_hi * sc])
        col = "#029E73" if name in DEMAND_INPUTS else "#0173B2"  # demand vs cost
        ax.barh(i, right - left, left=left, height=0.62, color=col, alpha=0.85)
        lbl = f"{swing:.2f}" if which == "R" else f"{swing*100:.0f}pp"
        ax.text(right + off, i, lbl, va="center", fontsize=7, color="0.3")
    ax.set_ylim(-0.95, len(rows) - 0.35)
    ax.axvline(base * sc, ls="--", lw=1.0, color="0.35")
    ax.text(base * sc, -0.85, "baseline\n(all at mode)", fontsize=6.5, color="0.35",
            ha="center", va="bottom")
    if which == "R":
        ax.axvline(1.0, ls=":", lw=1.2, color="#DE8F05")
        ax.text(1.0, -0.85, "parity", fontsize=7, color="#DE8F05", ha="center", va="bottom")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([LABELS.get(r[0], r[0]) for r in rows], fontsize=8.5)
    ax.set_xlabel(r"price ratio $R$" if which == "R"
                  else r"long-run cultivated share (%)")
    ax.set_title(title, fontsize=9.5)
    if which == "share":
        from matplotlib.patches import Patch
        ax.legend(handles=[Patch(color="#0173B2", alpha=0.85, label="cost lever (via R)"),
                           Patch(color="#029E73", alpha=0.85, label="demand lever")],
                  fontsize=7.5, frameon=False, loc="lower right")
    _save(fig, outdir, fname, fmts)


def fig_tornado_R(target, outdir, fmts):
    base, rows = oat(target, "R")
    _tornado_fig(target, "R", base, rows,
                 "What drives the price ratio R (low->high, one at a time)",
                 "sensitivity_tornado_R", outdir, fmts)


def fig_tornado_share(target, outdir, fmts):
    base, rows = oat(target, "share")
    _tornado_fig(target, "share", base, rows,
                 "What drives long-run cultivated share (cost levers via R + demand levers)",
                 "sensitivity_tornado_share", outdir, fmts)


# ----------------------------------------------------------------------------
# Key-knobs table  (the "levers & bottlenecks" list for the results doc)
# ----------------------------------------------------------------------------
def key_knobs(target: str, n: int = 20000) -> None:
    base_R, rowsR = oat(target, "R")
    var = dict(spread_contribution(monte_carlo(n, target, {}), target, {}))
    print(f"  KEY KNOBS — drivers of the price ratio R   (baseline all-at-mode R = {base_R:.2f})")
    print(f"    {'input':<15}{'R(lo)':>7}{'R(hi)':>7}{'swing':>7}{'var%*':>7}   optimistic end")
    for name, o_lo, o_hi, swing, opt in rowsR:
        print(f"    {name:<15}{o_lo:>7.2f}{o_hi:>7.2f}{swing:>7.2f}"
              f"{var.get(name, 0.0)*100:>6.0f}%   {opt}")
    print("    *var% = share of the Monte-Carlo R P10-P90 width (uncertainty.spread_contribution)")

    base_s, rowsS = oat(target, "share")
    print(f"\n  KEY KNOBS — drivers of long-run SHARE   (baseline all-at-mode share = {base_s*100:.1f}%)")
    print(f"    {'input':<15}{'share(lo)':>11}{'share(hi)':>11}{'swing(pp)':>11}   lever")
    for name, o_lo, o_hi, swing, opt in rowsS:
        kind = "demand" if name in DEMAND_INPUTS else "cost->R"
        print(f"    {name:<15}{o_lo*100:>10.1f}%{o_hi*100:>10.1f}%{swing*100:>10.1f} {kind:>8}")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", default="commodity", choices=list(TARGETS))
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--outdir", default="figures")
    ap.add_argument("--no-latex", action="store_true")
    ap.add_argument("--formats", default="png,pdf")
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

    setup_style(use_latex=not args.no_latex)
    fmts = [f.strip() for f in args.formats.split(",") if f.strip()]

    print(f"sensitivity — levers & bottlenecks (target={args.target}):")
    key_knobs(args.target, args.n)
    fig_tornado_R(args.target, args.outdir, fmts)
    fig_tornado_share(args.target, args.outdir, fmts)
    print("Done.")
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
