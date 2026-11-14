#!/usr/bin/env python3
"""
growth_rate.py — side-study to Rung 2: does growing the cells SLOWER ever lower the
cost per kg?  (the "doubling-time envelope")

The question
------------
Fast-growing animal cells waste part of their glucose as lactate and part of their
glutamine as ammonia ("overflow"). Both are toxic, so the process must supply enough
litres of medium to keep them dilute. Slower growth may waste less and so need fewer
litres per kg; but a plant that grows cells more slowly makes fewer kg per year, so its
capital and labour cost more per kg. This module puts both effects into the Rung 2 cost
model and asks where the cheapest doubling time sits.

It is an ENVELOPE, not a metabolic model: every growth-rate parameter is a judgement
(tagged [assumed] in inputs.py, prefix `gr_`). Its job is to say whether the effect could
matter, and under which conditions, before anyone builds something heavier.

The model
---------
Write r = tau / tau_ref for the doubling time relative to the base process (r >= 1 means
slower). Cost per kg wet biomass:

    cost(r) = media_intensity * efficiency * V(r) * media_price          (medium)
            + overhead * [ (1 - time_share) + time_share * r ]           (everything else)

V(r) is the medium volume per kg relative to the base process. Volume is set by whichever
limit demands the most litres, so it is a MAX over limits, not a sum:

    V(r) = max( level_bp * byproduct(r),  level_nut * nutrient(r) )

    byproduct(r) = (1 - g) * overflow(r) * G(r)  +  g * r
    nutrient(r)  = (1 - m) * G(r)               +  m * r

  * overflow(r): by-product made per kg of GROWTH, relative to the base.
      "proportional": 1  (production rate proportional to growth rate -> flat per kg)
      "threshold":    (1 - r/r*) / (1 - 1/r*), zero for r >= r*  (production rate
                      a*(mu - mu*) -> falls per kg as growth slows, gone at tau*)
  * g (gr_bp_time_share): the part of the by-product made per unit TIME (glutamine
    breaking down in warm medium, maintenance metabolism) -> grows with r.
  * m (gr_nut_time_share): the part of the nutrient need that is per unit time
    (maintenance energy, growth-factor decay) -> grows with r.
  * G(r) = (1 + kd*tau/ln2) / (1 + kd*tau_ref/ln2): extra gross growth needed per NET kg
    because cells die at rate kd.
  * level_*: each limit's demand at the base, as a share of the volume actually used.
    The binding limit has level 1; the other has gr_next_level <= 1.

Three structural cases cover what is not known:
    "byproduct-threshold"     a by-product binds and overflow has a threshold
                              (the ONLY case in which slower growth can pay)
    "byproduct-proportional"  a by-product binds but is proportional to growth
    "nutrient"                nutrient or growth-factor supply binds

A closed-form check (tests/test_growth_rate.py): with g = 0, kd = 0 and no second limit,
cost is linear in r up to r*, so the optimum is a CORNER — either the base rate or tau* —
and slowing pays if and only if   M > K * time_share * (r* - 1),
with M the medium cost and K the overhead at the base.

Run
---
    python growth_rate.py                 # scenario table + conditional Monte Carlo + figure
    python growth_rate.py --no-latex --formats png
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np
import matplotlib.pyplot as plt

from common import setup_style, _save
from inputs import value, prior
from cost_model import CostParams, media_cost

CASES = ("byproduct-threshold", "byproduct-proportional", "nutrient")
LN2 = float(np.log(2.0))


@dataclass
class GrowthParams:
    tau_ref: float = value("gr_tau_ref")                # h, doubling time of the base process
    time_share: float = value("gr_time_share")          # share of overhead that scales with time
    tau_star: float = value("gr_tau_star")              # h, overflow stops here (threshold case)
    bp_time_share: float = value("gr_bp_time_share")    # g: by-product made per unit time
    next_level: float = value("gr_next_level")          # the non-binding limit's level at the base
    nut_time_share: float = value("gr_nut_time_share")  # m: nutrient need per unit time
    death_rate: float = value("gr_death_rate")          # kd, 1/h
    case: str = "byproduct-threshold"


# ----------------------------------------------------------------------------
# The envelope  (all functions accept scalars or broadcastable numpy arrays)
# ----------------------------------------------------------------------------
def gross_factor(tau, gp: GrowthParams):
    """Gross growth needed per net kg, relative to the base (cells that die are regrown)."""
    return (1.0 + gp.death_rate * tau / LN2) / (1.0 + gp.death_rate * gp.tau_ref / LN2)


def overflow(tau, gp: GrowthParams, case: str | None = None):
    """Growth-coupled by-product per kg of growth, relative to the base."""
    case = gp.case if case is None else case
    r = np.asarray(tau, dtype=float) / gp.tau_ref
    if case == "byproduct-proportional":
        return np.ones_like(r + 0.0 * np.asarray(gp.tau_star))
    rs = np.asarray(gp.tau_star, dtype=float) / gp.tau_ref
    return np.clip((1.0 - r / rs) / (1.0 - 1.0 / rs), 0.0, None)


def volume_rel(tau, gp: GrowthParams, case: str | None = None):
    """Medium volume per kg relative to the base process: the largest demand across limits."""
    case = gp.case if case is None else case
    if case not in CASES:
        raise ValueError(f"case must be one of {CASES}, got {case!r}")
    r = np.asarray(tau, dtype=float) / gp.tau_ref
    G = gross_factor(tau, gp)
    bp = (1.0 - gp.bp_time_share) * overflow(tau, gp, case) * G + gp.bp_time_share * r
    nut = (1.0 - gp.nut_time_share) * G + gp.nut_time_share * r
    lvl_bp, lvl_nut = (gp.next_level, 1.0) if case == "nutrient" else (1.0, gp.next_level)
    return np.maximum(lvl_bp * bp, lvl_nut * nut)


def overhead_cost(tau, pr: CostParams, gp: GrowthParams, overhead=None):
    """Non-medium cost per kg at doubling time tau: the time-scaled share grows with tau."""
    oh = pr.nonmedia_cost if overhead is None else overhead
    r = np.asarray(tau, dtype=float) / gp.tau_ref
    return oh * ((1.0 - gp.time_share) + gp.time_share * r)


def cost(tau, pr: CostParams, gp: GrowthParams, media_price=None, overhead=None, case=None):
    """Biomass cost ($/kg wet) at doubling time tau (h). At tau = tau_ref this is exactly
    cost_model's media_cost + nonmedia_cost."""
    v = volume_rel(tau, gp, case)
    return media_cost(pr, media_price, pr.efficiency * v) + overhead_cost(tau, pr, gp, overhead)


def optimum(pr: CostParams, gp: GrowthParams, media_price=None, overhead=None, case=None,
            max_ratio: float = 4.0, n: int = 721):
    """Cheapest doubling time on [tau_ref, max_ratio*tau_ref] (the base is taken as the
    fastest the cells go). Returns (tau_opt, cost_opt, saving vs the base); array inputs
    of shape (N, 1) give arrays of shape (N,)."""
    tau = np.linspace(1.0, max_ratio, n) * gp.tau_ref
    c = cost(tau, pr, gp, media_price, overhead, case)
    i = np.argmin(c, axis=-1)
    c_opt = np.take_along_axis(c, np.expand_dims(i, -1), axis=-1)[..., 0] if c.ndim > 1 else c[i]
    base = c[..., 0]
    return tau[i], c_opt, base - c_opt


# ----------------------------------------------------------------------------
# Conditional Monte Carlo: within each structural case, how often does slowing pay?
# ----------------------------------------------------------------------------
_SAMPLED = ("media_price", "overhead", "gr_time_share", "gr_tau_star", "gr_bp_time_share",
            "gr_next_level", "gr_nut_time_share", "gr_death_rate")


def monte_carlo(n: int = 20000, seed: int = 0, media_price=None) -> dict:
    """Sample the cost and growth priors (triangular, from inputs.py) and find the optimum
    in each structural case. `media_price` fixes the medium price instead of sampling it.
    Returns {case: {"tau_opt", "saving"}} plus the draws. The cases are NOT weighted
    against each other: which one holds for meat cells is the open question."""
    rng = np.random.default_rng(seed)
    d = {}
    for name in _SAMPLED:
        _, lo, hi, mode, _ = prior(name)
        d[name] = rng.triangular(lo, mode, hi, n)[:, None]
    if media_price is not None:
        d["media_price"] = np.full((n, 1), float(media_price))
    pr = CostParams()
    gp = GrowthParams(time_share=d["gr_time_share"], tau_star=d["gr_tau_star"],
                      bp_time_share=d["gr_bp_time_share"], next_level=d["gr_next_level"],
                      nut_time_share=d["gr_nut_time_share"], death_rate=d["gr_death_rate"])
    out = {"draws": d}
    for case in CASES:
        tau_opt, _, saving = optimum(pr, gp, d["media_price"], d["overhead"], case)
        out[case] = {"tau_opt": tau_opt, "saving": saving}
    return out


# ----------------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------------
def summarise(pr: CostParams, gp: GrowthParams, n_mc: int = 20000) -> None:
    base = float(cost(gp.tau_ref, pr, gp))
    print(f"  base process (doubling time {gp.tau_ref:.0f} h): {base:.1f} $/kg")

    print("\n  POINT SCENARIOS — cheapest doubling time and saving vs the base, by medium price")
    print("  (growth parameters at their central values; overhead as labelled)")
    print(f"    {'case':<24}{'overhead':>9}" + "".join(f"{f'${p:.2f}/L':>16}" for p in (0.20, 0.40, 0.50, 1.00)))
    for case in CASES:
        for oh in (9.8, 19.1, 34.0):
            cells = []
            for p in (0.20, 0.40, 0.50, 1.00):
                t, _, s = optimum(pr, gp, p, oh, case)
                cells.append(f"{t:5.0f} h {s:5.2f} $".rjust(16))
            print(f"    {case:<24}{oh:>9.1f}" + "".join(cells))

    print(f"\n  CONDITIONAL MONTE CARLO (N={n_mc}, seed 0) — within each case, over the priors")
    print(f"    {'medium':<14}{'case':<24}{'P(saving>$1)':>14}{'P(saving>$3)':>14}"
          f"{'median saving':>15}{'90th pct':>10}")
    for label, mp in (("prior", None), ("$0.20/L", 0.20), ("$0.50/L", 0.50), ("$1.00/L", 1.00)):
        mc = monte_carlo(n_mc, 0, mp)
        for case in CASES:
            s = mc[case]["saving"]
            print(f"    {label:<14}{case:<24}{np.mean(s > 1):>14.2f}{np.mean(s > 3):>14.2f}"
                  f"{np.median(s):>15.2f}{np.percentile(s, 90):>10.2f}")
    print("    -> slower growth can only pay if a by-product binds AND overflow has a threshold;")
    print("       the cases are not weighted against each other (which holds is unknown).")


def fig_cost_vs_doubling_time(pr: CostParams, gp: GrowthParams, outdir, fmts) -> None:
    tau = np.linspace(gp.tau_ref, 3.0 * gp.tau_ref, 400)
    fig, ax = plt.subplots(figsize=(6.6, 4.3))
    for p, c in [(1.00, "#D55E00"), (0.50, "#0173B2"), (0.20, "#029E73")]:
        y_thr = cost(tau, pr, gp, p, None, "byproduct-threshold")
        y_pro = cost(tau, pr, gp, p, None, "byproduct-proportional")
        ax.plot(tau, y_thr, color=c, lw=2.0, label=rf"medium \${p:.2f}/L")
        ax.plot(tau, y_pro, color=c, lw=1.2, ls="--")
        i = int(np.argmin(y_thr))
        ax.scatter([tau[i]], [y_thr[i]], color=c, s=30, zorder=5)
    ax.plot([], [], color="0.3", lw=2.0, label="overflow stops below a threshold rate")
    ax.plot([], [], color="0.3", lw=1.2, ls="--", label="overflow proportional to growth")
    ax.scatter([], [], color="0.3", s=30, label="cheapest doubling time (threshold case)")
    ax.set_xlabel("Doubling time (h)")
    ax.set_ylabel(r"Biomass cost (\$/kg wet)")
    ax.set_title("Does slower growth pay? Not at these plant costs")
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    _save(fig, outdir, "cost_vs_doubling_time", fmts)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outdir", default="figures")
    ap.add_argument("--n", type=int, default=20000, help="Monte Carlo draws")
    ap.add_argument("--no-latex", action="store_true")
    ap.add_argument("--formats", default="png,pdf")
    args = ap.parse_args()

    setup_style(use_latex=not args.no_latex)
    fmts = [f.strip() for f in args.formats.split(",") if f.strip()]
    pr, gp = CostParams(), GrowthParams()
    print("Rung 2 side-study — doubling-time envelope:")
    summarise(pr, gp, args.n)
    fig_cost_vs_doubling_time(pr, gp, args.outdir, fmts)
    print("Done.")


if __name__ == "__main__":
    main()
