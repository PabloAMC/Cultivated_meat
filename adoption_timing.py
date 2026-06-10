#!/usr/bin/env python3
"""
adoption_timing — Timing: how fast does the share climb, and does the ceiling itself rise?

Rung 3 gave a STATIC map R -> share: the ceiling at a given price. This rung adds
TIME. Two DIFFERENT processes unfold, with different drivers, and a naive model
conflates them into one:

  PROCESS 1 — THE PRODUCT SPREADS THROUGH THE MARKET (rollout / diffusion).
    Even if nobody ever changes their mind, it takes years before cultivated meat
    is on every shelf and people have tried it. Adoption climbs toward whatever
    share today's preferences already support. Standard new-product diffusion
    S-curve (Bass: p = independent adopters, q = word-of-mouth/contagion). The
    ceiling here is FIXED; rollout only governs how fast you reach it.

  PROCESS 2 — PEOPLE BECOME MORE WILLING TO EAT IT (food neophobia fades).
    Separately, the launch novelty penalty is FOOD NEOPHOBIA -- the reluctance to eat
    an unfamiliar food (Pliner & Hobden 1992) -- and it is not permanent. As people are
    exposed to cultivated meat -- see it normalised, see others eat it -- it fades (the
    mere-exposure effect). This RAISES THE CEILING ITSELF (more people buy at a given
    price). We model the launch neophobia `neophobia_0` decaying toward ZERO as
    cumulative exposure grows -- there is NO free long-run "standing" floor; the
    permanent ceiling is set by the interpretable attributes accept_x + theta_free_M.

They are COUPLED: neophobia fades *because of* exposure, exposure happens *because of*
rollout. The gate: if SENSORY PARITY fails, neophobia does NOT fade (familiarity cures
"weird", not "worse") -- and even once it fades, a TASTE deficit (accept_x<1) persists.

And the THIRD axis this rung adds — COST OVER TIME (the cost->time coupling)
-------------------------------------------------------------------------
Rung 5 deliberately gives an ENDPOINT distribution of R, not a smooth R(t), because
in a pre-commercial field cost falls in milestone-gated jumps with unknown timing.
We honour that here: rather than a smooth learning curve, we drive the simulation
with a small set of named, discrete COST PATHS -- step functions where R drops when
a milestone (scale-up / cheaper medium) lands. The R endpoints are DERIVED from the
cost model (Pasitka base / medium-banked / both-levers / floor), so they cannot
drift from Rung 2; only the milestone YEAR is the declared unknown
(milestone_year_breakthrough). At each year R(t) comes from the active path, the
WTP curve (Rung 3) gives the current ceiling, and Bass rollout x growing acceptance
give the realised share. We show several paths (a scenario band), never one curve.

The long-run ACCEPTANCE (accept_x, theta_free_M) is QUALITY-DEPENDENT
--------------------------------------------------------------------
Once neophobia has faded, the permanent ceiling is set by two interpretable attributes,
and they are NOT one value:
  * PREMIUM / high-quality cut: authenticity matters, "I want the real thing" sticks --
    a lasting sensory/authenticity discount (accept_x < 1).
  * COMMODITY / processed (OUR scope -- minced, basic): provenance matters far less, so
    accept_x ~ 1 (sensory parity, physically attainable since it is real tissue) ...
  * ... and cultivated's cleaner/safer/no-slaughter profile is the upside theta_free_M > 0.
Because we model the basic commodity product, the central case is accept_x=1, theta_free=0,
and the upside is live. fig_acceptance_spectrum sweeps the whole range.

Usage
-----
    python adoption_timing.py --no-latex
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace

import numpy as np
import matplotlib.pyplot as plt

from common import setup_style, _save
from inputs import value
from cost_model import CostParams, biomass_cost, cost_floor, ratio as cost_ratio
from market_share import DemandParams, share


# cultivated's LONG-RUN acceptance, by scenario — the headline Gate-2 axis (no baked-in
# stance). By the long run food-neophobia has fully faded, so the permanent at-parity
# standing is the interpretable pair (accept_x = sensory acceptance, theta_free_M =
# cleaner-meat upside). Each scenario is (accept_x, theta_free_M, label), spanning the
# same friction -> preferred range the old xi_x_floor dial did, but in named attributes.
ACCEPT_SCENARIOS = [
    (0.6, 0.0, "strong taste friction (~Peacock/PTC-skeptic)"),
    (0.8, 0.0, "modest friction"),
    (1.0, 0.0, "sensory parity (neutral)"),
    (1.0, 0.5, "actively preferred (cleaner)"),
    (1.1, 1.0, "strongly preferred (better + cleaner)"),
]

# fixed price ratios for the static-R diagnostics (far above parity -> at parity)
R_GRID = [2.0, 1.5, 1.05, 1.0]


# ----------------------------------------------------------------------------
# COST PATHS — R over time as discrete, milestone-gated steps (the cost coupling)
# R endpoints are DERIVED from the cost model so they cannot drift from Rung 2.
# ----------------------------------------------------------------------------
_CP = CostParams()
R_TODAY  = cost_ratio(biomass_cost(_CP, value("media_price"), 1.0), _CP)   # Pasitka base (~2.4)
R_MEDIUM = cost_ratio(biomass_cost(_CP, 0.20, 1.0), _CP)                   # cheap medium banked (~1.6)
R_BREAK  = cost_ratio(biomass_cost(_CP, 0.20, _CP.eff_best), _CP)          # medium + efficient cells (~1.4)
R_FLOOR  = cost_ratio(cost_floor(_CP), _CP)                                # irreducible floor (~1.0)
YR_BREAK = int(value("milestone_year_breakthrough"))                       # when the step lands (~10)

# each path: a list of (year_the_step_takes_effect, R). Step function, NOT
# interpolated -- cost falls in discrete milestone jumps (see uncertainty.py).
COST_PATHS = {
    "stall (no cost progress)":         [(0, R_TODAY)],
    "cheap medium only (scale stalls)": [(0, R_MEDIUM)],
    f"breakthrough by yr{YR_BREAK}":    [(0, R_TODAY), (YR_BREAK, R_BREAK)],
    f"reach the floor by yr{YR_BREAK + 5}": [(0, R_TODAY), (YR_BREAK, R_BREAK),
                                             (YR_BREAK + 5, R_FLOOR)],
}


def R_at(path, year: int) -> float:
    """R active at `year`: the last step whose effective-year is <= year."""
    r = path[0][1]
    for yr, rv in path:
        if year >= yr:
            r = rv
    return r


# ----------------------------------------------------------------------------
# Timing parameters
# ----------------------------------------------------------------------------
@dataclass
class TimingParams:
    # --- Process 1: market rollout (Bass diffusion) ------------------------
    p_innov: float = value("p_innov")   # independent adopters (innovation coefficient)
    q_imit: float = value("q_imit")     # word-of-mouth / contagion (imitation coefficient)

    # --- Process 2: growing acceptance = launch FOOD-NEOPHOBIA fading toward ZERO ----
    neophobia_0: float = value("neophobia_M")    # launch food-neophobia, mainstream (decays -> 0)
    #   The LONG-RUN standing is NOT a free floor — it is the interpretable pair below,
    #   which neophobia decays toward (accept_x carries friction, theta_free_M the upside):
    accept_x: float = value("accept_x")          # long-run sensory acceptance (Gate-2 friction dial)
    theta_free_M: float = value("theta_free_M")  # long-run cleaner-meat upside (Gate-2 upside dial)
    accept_rate: float = value("accept_rate")  # how fast neophobia decays per unit cumulative exposure
    sensory_parity: bool = True         # gate: if False, neophobia does NOT fade (the PB-meat case)

    years: int = int(value("years"))


# ----------------------------------------------------------------------------
# The coupled simulation
# ----------------------------------------------------------------------------
def _run(R_of_year, dp: DemandParams, tp: TimingParams, acceptance_grows: bool):
    """Core loop shared by the fixed-R and cost-path simulations. `R_of_year(k)`
    returns the price ratio in year k. Returns time series dict."""
    t = np.arange(tp.years + 1)
    F = 0.0          # rollout: fraction-of-ceiling reached (Bass)
    E = 0.0          # cumulative exposure (drives neophobia decay)
    shares, ceilings, nbs, Rs = [], [], [], []

    accept_on = acceptance_grows and tp.sensory_parity
    for k in range(tp.years + 1):
        Rk = R_of_year(k)
        if accept_on:
            nb = tp.neophobia_0 * np.exp(-tp.accept_rate * E)  # launch neophobia decays toward 0
        else:
            nb = tp.neophobia_0                                # neophobia never fades (the PB-meat case)
        # Rung-3 ceiling at the current neophobia, holding the LONG-RUN acceptance attributes
        # (accept_x sensory, theta_free_M cleaner-meat). As nb -> 0 the ceiling rises to its
        # permanent level set by those two attributes.
        ceiling = share(Rk, dp, accept_x=tp.accept_x, theta_free_M=tp.theta_free_M, neophobia_M=nb)
        s = F * ceiling
        shares.append(s); ceilings.append(ceiling); nbs.append(nb); Rs.append(Rk)
        if k < tp.years:
            dF = (tp.p_innov + tp.q_imit * F) * (1.0 - F)     # rollout advances
            F = min(1.0, F + dF)
            E += F          # exposure ~ AVAILABILITY (familiarity grows as it fills shelves),
            #   not the small consumed share -- else neophobia never fades once shares
            #   are realistically ~1%. People grow familiar with a product they keep seeing
            #   even if price keeps them from buying.
    return dict(t=t, share=np.array(shares), ceiling=np.array(ceilings),
                neophobia=np.array(nbs), R=np.array(Rs))


def simulate(R: float, dp: DemandParams, tp: TimingParams,
             acceptance_grows: bool = True):
    """Fixed-price (fixed-R) timing: the two processes at a single price ratio.
    acceptance_grows=False -> rollout only (fixed ceiling)."""
    return _run(lambda k: R, dp, tp, acceptance_grows)


def simulate_path(path, dp: DemandParams, tp: TimingParams,
                  acceptance_grows: bool = True):
    """Cost-coupled timing: R steps over time along a milestone COST PATH, so the
    ceiling rises both because cost falls (R drops) AND because acceptance grows."""
    return _run(lambda k: R_at(path, k), dp, tp, acceptance_grows)


def y30(R, dp, tp, **kw):
    return simulate(R, dp, tp, **kw)["share"][-1] * 100


# ----------------------------------------------------------------------------
# Report — year-30 share by COST PATH x long-run acceptance (accept_x, theta_free_M)
# ----------------------------------------------------------------------------
def summarise(dp: DemandParams, tp: TimingParams) -> None:
    print("  cost paths (R endpoints derived from the cost model):")
    for name, steps in COST_PATHS.items():
        seq = " -> ".join(f"R={rv:.2f}@yr{yr}" for yr, rv in steps)
        print(f"    {name:<28} {seq}")
    # long-run acceptance columns = (accept_x, theta_free_M); neophobia has faded to 0
    cols = [(0.8, 0.0, "friction"), (1.0, 0.0, "neutral"), (1.1, 1.0, "preferred")]
    hdr = "".join(f"{lbl:>11}" for _, _, lbl in cols)
    print(f"\n  year-30 realised share %, by cost path x long-run acceptance (accept_x, theta_free):")
    print(f"    {'cost path':<28}{hdr}   final R")
    for name, steps in COST_PATHS.items():
        row = "".join(
            f"{simulate_path(steps, dp, replace(tp, accept_x=a, theta_free_M=tf))['share'][-1]*100:>11.1f}"
            for a, tf, _ in cols)
        print(f"    {name:<28}{row}   {steps[-1][1]:>6.2f}")
    print("  -> the cost PATH sets the achievable ceiling (final R); long-run acceptance (columns) sets")
    print("     how much of it converts. Trajectory = Bass rollout x neophobia fading to 0, 30 yr.")


# ----------------------------------------------------------------------------
# Figures
# ----------------------------------------------------------------------------
def _grid(figsize=(8.6, 6.4)):
    fig, axes = plt.subplots(2, 2, figsize=figsize, sharex=True, sharey=True)
    return fig, axes


def fig_cost_paths(dp: DemandParams, tp: TimingParams, outdir, fmts) -> None:
    """THE cost->penetration->time figure: realised share trajectory per cost path
    (neutral long-run acceptance), with the milestone year marked and a scenario band."""
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    cols = ["#949494", "#DE8F05", "#0173B2", "#029E73"]
    sims = {}
    for (name, steps), col in zip(COST_PATHS.items(), cols):
        sim = simulate_path(steps, dp, tp)            # neutral acceptance (tp default accept_x=1, theta_free=0)
        sims[name] = sim
        ax.plot(sim["t"], sim["share"] * 100, lw=2.0, color=col, label=name)

    # scenario band across the paths
    allshare = np.vstack([s["share"] for s in sims.values()]) * 100
    ax.fill_between(np.arange(tp.years + 1), allshare.min(0), allshare.max(0),
                    color="0.5", alpha=0.08)

    ax.axvline(YR_BREAK, ls=":", lw=1.0, color="0.45")
    ax.text(YR_BREAK + 0.3, ax.get_ylim()[1] * 0.04, f"milestone\n~yr{YR_BREAK}",
            fontsize=7, color="0.45")
    ax.set_xlabel("Years from launch")
    ax.set_ylabel(r"Realised cultivated share (\%)")
    ax.set_title("Penetration over time, by cost-milestone path (neutral long-run acceptance)")
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    _save(fig, outdir, "cost_paths_timing", fmts)


def fig_timing(dp: DemandParams, tp: TimingParams, outdir, fmts) -> None:
    """Two processes (rollout vs rollout+acceptance) at four FIXED price ratios."""
    fig, axes = _grid()
    for ax, R in zip(axes.flat, R_GRID):
        fixed = simulate(R, dp, tp, acceptance_grows=False)
        grow = simulate(R, dp, tp, acceptance_grows=True)
        ax.plot(fixed["t"], fixed["share"] * 100, ls="--", color="#DE8F05",
                label="rollout only")
        ax.plot(grow["t"], grow["share"] * 100, color="#0173B2",
                label="rollout + growing acceptance")
        ax.set_title(f"R = {R:.2f}", fontsize=9)
    for ax in axes[-1]:
        ax.set_xlabel("Years (price fixed)")
    for ax in axes[:, 0]:
        ax.set_ylabel(r"Realised share (%)")
    axes[0, 0].legend(fontsize=7, frameon=False, loc="upper left")
    fig.suptitle(r"Two processes over time, by price ratio "
                 r"(neophobia $\to 0$, long-run acceptance neutral)",
                 y=1.01, fontsize=10)
    _save(fig, outdir, "timing_two_processes", fmts)


def fig_acceptance_spectrum(dp: DemandParams, tp: TimingParams, outdir, fmts) -> None:
    """Sweep the LONG-RUN acceptance (accept_x sensory, theta_free_M cleaner-meat upside)
    from friction -> parity -> actively preferred, at four fixed price ratios. Neophobia
    fades to 0 in every case; what differs is the permanent ceiling these two set."""
    fig, axes = _grid()
    for ax, R in zip(axes.flat, R_GRID):
        for a, tf, lbl in ACCEPT_SCENARIOS:
            sim = simulate(R, dp, replace(tp, accept_x=a, theta_free_M=tf), acceptance_grows=True)
            ax.plot(sim["t"], sim["share"] * 100, lw=1.6, label=lbl)
        ax.set_title(f"R = {R:.2f}", fontsize=9)
    for ax in axes[-1]:
        ax.set_xlabel("Years (price fixed)")
    for ax in axes[:, 0]:
        ax.set_ylabel(r"Realised share (%)")
    axes[0, 0].legend(fontsize=6.5, frameon=False, loc="upper left", title="long-run acceptance")
    fig.suptitle("Cleaner-meat upside: long-run acceptance, by price ratio",
                 y=1.01, fontsize=10)
    _save(fig, outdir, "acceptance_spectrum", fmts)


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
    dp = DemandParams()
    tp = TimingParams()

    print("Step 4 — timing (cost paths over time + the two demand processes):")
    summarise(dp, tp)
    fig_cost_paths(dp, tp, args.outdir, fmts)
    fig_timing(dp, tp, args.outdir, fmts)
    fig_acceptance_spectrum(dp, tp, args.outdir, fmts)
    print("Done.")
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
