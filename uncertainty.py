#!/usr/bin/env python3
"""
Step 5 — Uncertainty: a distribution over the price ratio (and share), not a forecast.

This rung does NOT add a time axis. In a pre-commercial field, cost falls in
discrete, milestone-gated jumps with unknown (maybe never) timing — there is no
smooth, calibratable R(t) to put a confidence fan around. So we model the
ENDPOINT, not the path: given honest uncertainty about the *achievable* values of
the key inputs, what is the distribution of the achievable price ratio R, and the
share it implies? The output is a RANGE with confidence intervals (P5..P95).

TARGETS (basic vs structured/premium)
-------------------------------------
The same machinery runs for the BASIC product (vs commodity meat) and the
STRUCTURED product (Rung 6: scaffold cost added, compared to a PREMIUM benchmark
like premium fish or sushi salmon -- the Wildtype/BlueNalu case). Pick with
--target; the scaffold inputs are sampled only for the premium targets.

  commodity     basic minced product vs commodity meat (~$12/kg)   [no scaffold]
  premium-fish  structured product vs premium fish / BlueNalu (~$25/kg)
  sushi-salmon  structured product vs sushi salmon / Wildtype (~$40/kg)

The share reported is the LONG-RUN ceiling (after acceptance has grown and
rollout is complete -- the Rung 4 endpoint), so it reflects the cleaner-meat
upside, not the near-term static share. (For premium seafood the demand
calibration is meat-based, so treat the structured-target SHARE as softer than R.)

Tunable: edit the priors in inputs.py (the datasheet), or pin any active input, e.g.
    python uncertainty.py --target sushi-salmon --fix process_cost=5
    python uncertainty.py --fix media_price=0.2 --fix efficiency=0.25

Usage
-----
    python uncertainty.py --no-latex
    python uncertainty.py --target premium-fish --n 20000 --no-latex
"""

from __future__ import annotations

import argparse

import numpy as np
import matplotlib.pyplot as plt

from common import setup_style, _save
from inputs import prior
from cost_model import CostParams, media_cost
from market_share import DemandParams, share


# Priors are pulled straight from the inputs.py datasheet — one source of truth,
# so the MC band and the point estimates can never drift apart. Each prior() call
# returns (kind, lo, hi, mode, note). AA_FLOOR (the irreducible amino-acid cost)
# and the cost equation itself are also imported, not re-typed here.
# neophobia_x (long-run novelty attitude) is swept too, for CONSISTENCY with the other two
# reference MCs (meat_market.monte_carlo and adoption_timing.monte_carlo_trajectory both sweep
# it). It is a genuine long-run-share uncertainty — where novelty attitude LANDS once it has
# faded — on the same footing as the accept_x / theta_free_M acceptance dials, so omitting it
# here understated the share band. It does NOT enter R (novelty is a demand-side utility offset).
BASE_PRIORS = {name: prior(name) for name in
               ("media_price", "efficiency", "overhead", "markup_add", "eps_own",
                "theta_free_M", "accept_x", "neophobia_x")}

# scaffold inputs — sampled ONLY for structured (premium) targets (Rung 6)
SCAFFOLD_PRIORS = {name: prior(name) for name in
                   ("scaffold_frac", "material_price", "process_cost")}

# each target sets the conventional benchmark (from the datasheet) and whether
# scaffolding applies
TARGETS = {
    "commodity":    dict(scaffold=False, p_conv=prior("p_conv"),
                         label="basic product vs commodity meat (~$12/kg)"),
    "premium-fish": dict(scaffold=True,  p_conv=prior("p_conv_premium_fish"),
                         label="structured vs premium fish / BlueNalu (~$25/kg)"),
    "sushi-salmon": dict(scaffold=True,  p_conv=prior("p_conv_sushi_salmon"),
                         label="structured vs sushi salmon / Wildtype (~$40/kg)"),
}


def active_priors(target: str) -> dict:
    t = TARGETS[target]
    pri = dict(BASE_PRIORS)
    pri["p_conv"] = t["p_conv"]
    if t["scaffold"]:
        pri.update(SCAFFOLD_PRIORS)
    return pri


# ----------------------------------------------------------------------------
# Sampling
# ----------------------------------------------------------------------------
def _sample(name, pri, rng, n, fixed):
    if name in fixed:
        return np.full(n, fixed[name])
    kind, lo, hi, mode, _ = pri[name]
    if kind == "triangular":
        return rng.triangular(lo, mode, hi, n)
    if kind == "uniform":
        return rng.uniform(lo, hi, n)
    raise ValueError(kind)


def R_from_inputs(media_price, efficiency, overhead, markup_add, p_conv,
                  scaffold_frac=0.0, material_price=0.0, process_cost=0.0):
    """The ONE cost->R equation, shared by monte_carlo and sensitivity.py so the
    cost math exists in exactly one place. Scalar OR numpy-array inputs.

    media can never fall below the irreducible amino-acid floor (AA_FLOOR). overhead
    is the Pasitka scale-up knob (perfusion ~$7.9 -> ATF ~$24.7/kg), so the total
    cost floats from its own prior rather than cost_model's single point floor.
    Scaffold terms are 0 for the basic product, nonzero for structured targets."""
    cost = (media_cost(CostParams(), media_price, efficiency)
            + overhead + scaffold_frac * material_price + process_cost)
    return (cost + markup_add) / p_conv


def monte_carlo(n: int, target: str, fixed: dict, seed: int = 0) -> dict:
    # NOTE: this reference MC sweeps the cost stack + theta_free_M + accept_x. The interactive
    # explorer's JS penetration band (build_interactive.py `monteCarlo`) deliberately sweeps a
    # WIDER set (also health_x/health_p, premium_resistance, the plant-based dials) so both novel
    # meats get an equal-footing band — so the on-page band is intentionally wider. By design.
    pri = active_priors(target)
    rng = np.random.default_rng(seed)
    s = {k: _sample(k, pri, rng, n, fixed) for k in pri}

    scaf = TARGETS[target]["scaffold"]
    R = R_from_inputs(
        s["media_price"], s["efficiency"], s["overhead"], s["markup_add"], s["p_conv"],
        scaffold_frac=s["scaffold_frac"] if scaf else 0.0,
        material_price=s["material_price"] if scaf else 0.0,
        process_cost=s["process_cost"] if scaf else 0.0)
    cost = R * s["p_conv"] - s["markup_add"]

    base = DemandParams()      # WTP curve; the plant-based floor is a declared constant
    sh = np.array([share(R[i], base, theta_free_M=s["theta_free_M"][i],
                         accept_x=s["accept_x"][i], eps_own=s["eps_own"][i],
                         neophobia_x=s["neophobia_x"][i])
                   for i in range(n)])
    return dict(R=R, share=sh, cost=cost, samples=s, priors=pri)


# ----------------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------------
PCTS = [5, 10, 25, 50, 75, 90, 95]


def _ci(x):
    return {q: np.percentile(x, q) for q in PCTS}


def spread_contribution(mc: dict, target: str, fixed: dict) -> list:
    """How much each input drives the WIDTH of the R band: pin it to its mode, re-run
    the MC, and measure how far the P10-P90 width shrinks. Returns
    [(name, fraction_of_width), ...] sorted descending. Shared with sensitivity.py so
    the two modules report the SAME diagnostic.

    CAVEAT — this is NOT a variance decomposition: the fractions do NOT sum to 1, and
    an input whose prior MODE sits at an extreme of its range is under-credited
    (pinning to mode then only removes one tail, barely changing P10-P90, even though
    the input strongly moves the band's LOCATION). `efficiency` (mode 1.0 = the
    pessimistic edge of [0.25, 1.0]) is the canonical example: ~0% width-share despite
    a large one-at-a-time swing. Read it as 'realised dispersion ownership given where
    we centred the prior', not 'total influence'."""
    R = mc["R"]
    base_w = np.percentile(R, 90) - np.percentile(R, 10)
    rows = []
    for name in mc["priors"]:
        if name in fixed:
            continue
        mode = mc["priors"][name][3]
        mc2 = monte_carlo(len(R), target, {**fixed, name: mode}, seed=1)
        w = np.percentile(mc2["R"], 90) - np.percentile(mc2["R"], 10)
        frac = max(0.0, base_w - w) / base_w if base_w else 0.0
        rows.append((name, frac))
    return sorted(rows, key=lambda r: -r[1])


def summarise(mc: dict, target: str, fixed: dict) -> None:
    R, sh = mc["R"], mc["share"]
    cR, cS = _ci(R), _ci(sh * 100)
    print(f"  target: {TARGETS[target]['label']}")
    if fixed:
        print(f"  pinned: {', '.join(f'{k}={v}' for k, v in fixed.items())}")
    print("  price ratio R:")
    print(f"      P50 = {cR[50]:.2f}    80% CI [P10,P90] = [{cR[10]:.2f}, {cR[90]:.2f}]"
          f"    90% CI [{cR[5]:.2f}, {cR[95]:.2f}]")
    print("  long-run share (%):")
    print(f"      P50 = {cS[50]:.1f}    80% CI [P10,P90] = [{cS[10]:.1f}, {cS[90]:.1f}]")
    print(f"  ({100*np.mean(R <= 1.0):.0f}% of the R-distribution is at/below parity)")

    print("\n  spread contribution (how much the R P10-P90 width shrinks if pinned):")
    for name, frac in spread_contribution(mc, target, fixed):
        print(f"      {name:<14} {frac*100:4.0f}%")


# ----------------------------------------------------------------------------
# Figures
# ----------------------------------------------------------------------------
def fig_distributions(mc: dict, target: str, outdir, fmts) -> None:
    R, sh = mc["R"], mc["share"] * 100
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.6, 3.6))
    for ax, x, lbl, col, pline in [
        (ax1, R, r"price ratio $R$", "#0173B2", 1.0),
        (ax2, sh, r"long-run share (%)", "#029E73", None),
    ]:
        ax.hist(x, bins=50, color=col, alpha=0.75)
        for q, ls in [(10, ":"), (50, "-"), (90, ":")]:
            v = np.percentile(x, q)
            ax.axvline(v, ls=ls, lw=1.0, color="0.25")
            ax.text(v, ax.get_ylim()[1]*0.93,
                    f"P{q}={v:.2f}" if ax is ax1 else f"P{q}={v:.0f}",
                    rotation=90, fontsize=6.5, va="top", ha="right", color="0.25")
        if pline is not None:
            ax.axvline(pline, ls="--", lw=1.0, color="#DE8F05")
            ax.text(pline, ax.get_ylim()[1]*0.5, "parity", rotation=90,
                    fontsize=7, color="#DE8F05", va="center", ha="right")
        ax.set_xlabel(lbl)
        ax.set_ylabel("draws")
    fig.suptitle(f"Distribution — {TARGETS[target]['label']}", y=1.02, fontsize=10)
    _save(fig, outdir, "uncertainty_distributions", fmts)


def fig_target_compare(n, fixed, outdir, fmts) -> None:
    """Compare the R distribution across all targets — the scaffold/premium story."""
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    ys = list(range(len(TARGETS)))[::-1]
    for y, (target, t) in zip(ys, TARGETS.items()):
        mc = monte_carlo(n, target, fixed)
        c = _ci(mc["R"])
        ax.plot([c[10], c[90]], [y, y], color="#0173B2", lw=4, alpha=0.5,
                solid_capstyle="round")
        ax.plot([c[5], c[95]], [y, y], color="#0173B2", lw=1.5, alpha=0.6)
        ax.plot(c[50], y, "o", color="#0173B2", ms=6)
        ax.text(c[95] + 0.05, y, f"P50={c[50]:.2f}", fontsize=7.5, va="center")
    ax.axvline(1.0, ls="--", lw=1.0, color="#DE8F05")
    ax.text(1.0, len(TARGETS)-0.4, "parity", fontsize=8, color="#DE8F05", ha="center")
    ax.set_yticks(ys)
    ax.set_yticklabels([TARGETS[t]["label"].split(" (")[0] for t in TARGETS], fontsize=8)
    ax.set_xlabel(r"price ratio $R$  (P5–P95, P10–P90 bold, P50 dot)")
    ax.set_title("Premium targets absorb the scaffold cost (basic vs commodity does not)")
    _save(fig, outdir, "target_comparison", fmts)


def _parse_fixed(items, target):
    pri = active_priors(target)
    fixed = {}
    for it in items or []:
        k, v = it.split("=")
        if k not in pri:
            raise SystemExit(f"unknown input '{k}' for target '{target}'; "
                             f"options: {', '.join(pri)}")
        fixed[k] = float(v)
    return fixed


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", default="commodity", choices=list(TARGETS))
    ap.add_argument("--outdir", default="figures")
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--fix", action="append", default=[],
                    help="pin an active input, e.g. --fix process_cost=5 (repeatable)")
    ap.add_argument("--no-latex", action="store_true")
    ap.add_argument("--formats", default="png,pdf")
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

    setup_style(use_latex=not args.no_latex)
    fmts = [f.strip() for f in args.formats.split(",") if f.strip()]
    fixed = _parse_fixed(args.fix, args.target)

    print(f"Step 5 — Monte Carlo over input priors (N={args.n}, target={args.target}):")
    mc = monte_carlo(args.n, args.target, fixed)
    summarise(mc, args.target, fixed)
    fig_distributions(mc, args.target, args.outdir, fmts)
    fig_target_compare(args.n, fixed, args.outdir, fmts)
    print("Done.")
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
