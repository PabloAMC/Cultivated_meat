#!/usr/bin/env python3
"""
contamination.py — what a contamination does to a tank of animal cells, and how much of it a cheaper
plant can afford.  (Side-study; NOT used in the headline cost. Write-up:
research_notes/cheap_plant_study.md.)

The chain of reasoning
----------------------
1. A contaminant doubles in 20 to 60 minutes; the cells double in a day. Nothing the cells do can hold
   it back, so one cell that gets in ends the run. Starting from one cell in the tank it needs about
   50 doublings to become visible:

       time to detection = doubling time x log2(threshold x tank volume / cells that got in)

2. Ordinary sensors (dissolved oxygen, off-gas, pH) see a contaminant when it changes the tank's
   oxygen uptake by a few per cent. The cells themselves burn a lot of oxygen, so a dense culture
   hides more:

       threshold [cells per mL] = shift x (cell density x oxygen uptake per gram)
                                  / (oxygen uptake per bacterium)

   At the floor's 120 g/L this is about 2e8 bacteria per mL; at 27 g/L about 4e7.

3. Food limits for the harvested cells (1e2 to 1e4 per gram in the filings) are crossed about 15 to 20
   doublings BEFORE that, so the sensors that every tank has do not protect the product; they only stop
   the run. Product harvested in the hours between the two must be held back and discarded.

4. At detection the contaminant is still under 0.2% of the biomass: the cells are all there. Whether
   they may be sold after a kill step is a question of regulation and toxins, not of mass (`salvage`).

5. Economics: a tank is lost at a constant chance per day while it runs (`hazard`: seals, gas, feeds,
   sampling) and at a chance per start (`start_fail`: the seed, the start-up). Each loss costs the
   tankful, the restart, and the time before it showed. floor_physics.explore prices that. This module
   solves for the loss rate at which a cheaper plant stops being cheaper than a sterile one that loses
   runs at pharma's rate: a threshold, not a prediction.

6. Shared equipment (a seed train, a medium line) does not raise the expected number of tanks lost, if
   the chance of a failure is per vessel or per line. It makes losses come together: every tank on the
   line stops at once and they queue for the seed train to restart.

Run
---
    python contamination.py
"""

from __future__ import annotations

import math

from inputs import value
import floor_physics as fp
import plant_items as pi


# ----------------------------------------------------------------------------
# Growth and detection
# ----------------------------------------------------------------------------
def detect_threshold(x_g_l: float, cells: fp.Cells | None = None, shift: float | None = None) -> float:
    """Contaminant density, cells per mL, at which it changes the tank's oxygen uptake by `shift`."""
    cells = fp.GOOD_CELLS if cells is None else cells
    shift = value("ct_detect_shift") if shift is None else shift
    per_bacterium = value("ct_bact_qo2") * value("ct_bact_dry_pg") * 1e-12          # mmol O2 per cell per hour
    return shift * x_g_l * cells.qo2 / per_bacterium / 1000.0                       # per mL


def doublings_to(level_per_ml: float, vessel_m3: float = 20.0, inoculum: float | None = None) -> float:
    """Doublings from the cells that got in to a density of `level_per_ml` in the working volume."""
    n0 = value("ct_inoculum_cfu") if inoculum is None else inoculum
    ml = vessel_m3 * value("pf_working_volume") * 1e6
    return max(0.0, math.log2(level_per_ml * ml / n0))


def time_to_detect_h(doubling_min: float, x_g_l: float = 120.0, vessel_m3: float = 20.0,
                     inoculum: float | None = None, shift: float | None = None) -> float:
    """Hours from entry to detection by oxygen or off-gas readings."""
    return doubling_min / 60.0 * doublings_to(detect_threshold(x_g_l, shift=shift), vessel_m3, inoculum)


def food_limit_per_ml(x_g_l: float, limit_cfu_g: float | None = None) -> float:
    """Contaminant density in the tank, cells per mL, at which the harvested cells reach the food limit,
    if every bacterium ends up in the cell paste (the cautious case)."""
    limit = value("ct_food_limit_cfu") if limit_cfu_g is None else limit_cfu_g
    return limit * x_g_l / 1000.0


def blind_hours(doubling_min: float, x_g_l: float = 120.0, limit_cfu_g: float | None = None,
                shift: float | None = None) -> float:
    """Hours before detection during which the harvest is already over the food limit."""
    d = math.log2(detect_threshold(x_g_l, shift=shift) / food_limit_per_ml(x_g_l, limit_cfu_g))
    return max(0.0, d) * doubling_min / 60.0


def contaminant_share_at_detection(x_g_l: float = 120.0) -> float:
    """Contaminant dry mass over the cells' dry mass (30% of wet) at detection."""
    grams = detect_threshold(x_g_l) * 1000.0 * value("ct_bact_dry_pg") * 1e-12      # g dry per litre
    return grams / (0.3 * x_g_l)


def escape_probability(doubling_min: float, stage_h: float | None = None, x_g_l: float = 120.0,
                       vessel_m3: float = 15.6) -> float:
    """Chance that a contaminant entering a seed stage at a random time is still invisible when the
    stage is transferred: the stage ends before the time to detection has passed."""
    stage = value("pi_stage_h") if stage_h is None else stage_h
    return min(1.0, time_to_detect_h(doubling_min, x_g_l, vessel_m3) / stage)


# ----------------------------------------------------------------------------
# Loss rates
# ----------------------------------------------------------------------------
def hazard_from_batch_loss(share_lost: float, batch_days: float) -> float:
    """The constant chance per day that loses `share_lost` of batches lasting `batch_days`."""
    return -math.log(1.0 - share_lost) / batch_days


def batch_loss(hazard: float, run_days: float, start_fail: float = 0.0) -> float:
    """Share of runs lost: at the start, or at `hazard` per day over the run."""
    return start_fail + (1.0 - start_fail) * (1.0 - math.exp(-hazard * run_days))


def reference_hazards() -> dict:
    """Per-day loss rates implied by the two survey figures. Pharma batches last about 10-14 days; the
    cultivated-meat survey gives no run length, so 10 and 20 days bracket it [assumed]."""
    ph, cm, cms = value("ct_batch_loss_pharma"), value("ct_batch_loss_cm"), value("ct_batch_loss_cm_scaled")
    return {"pharma": (hazard_from_batch_loss(ph, 14.0), hazard_from_batch_loss(ph, 10.0)),
            "cultivated meat, all": (hazard_from_batch_loss(cm, 20.0), hazard_from_batch_loss(cm, 10.0)),
            "cultivated meat, beyond flasks": (hazard_from_batch_loss(cms, 20.0), hazard_from_batch_loss(cms, 10.0))}


# ----------------------------------------------------------------------------
# Thresholds
# ----------------------------------------------------------------------------
def cost(plant: str, hazard: float = 0.0, run_days: float | None = None, restart_fail_days: float = 14.0,
         start_fail: float = 0.0, salvage: float = 0.0, **kw) -> float:
    """Cost of cells, $/kg, in a named plant (plant_items.PLANTS) with a given loss pattern."""
    return pi.cost_per_kg(plant, hazard=hazard, run_days=run_days, restart_fail_days=restart_fail_days,
                          start_fail=start_fail, salvage=salvage, **kw)["total"]


def _solve(f, hi: float) -> float:
    """Smallest x in (0, hi) with f(x) >= 0, for increasing f; hi if never, 0 if already."""
    if f(0.0) >= 0:
        return 0.0
    if f(hi) < 0:
        return hi
    lo = 0.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if f(mid) >= 0 else (mid, hi)
    return 0.5 * (lo + hi)


def breakeven_hazard(plant: str, reference: str = "floor", run_days: float | None = None,
                     restart_fail_days: float = 14.0, ref_hazard: float | None = None,
                     ref_restart_fail_days: float | None = None, salvage: float = 0.0, **kw) -> float:
    """Chance per day of losing a run at which `plant` costs as much per kg as the `reference` plant
    losing runs at pharma's rate. Above it the cheaper plant is no longer cheaper. Capped at 1.0."""
    h0 = value("pf_hazard_pharma") if ref_hazard is None else ref_hazard
    rr = restart_fail_days if ref_restart_fail_days is None else ref_restart_fail_days
    target = cost(reference, h0, run_days, rr, **kw)
    return _solve(lambda h: cost(plant, h, run_days, restart_fail_days, salvage=salvage, **kw) - target, 1.0)


def breakeven_start_fail(plant: str, reference: str = "floor", run_days: float | None = None,
                         restart_fail_days: float = 14.0, hazard: float | None = None, **kw) -> float:
    """Share of starts that may fail (seed-borne or start-up contamination) before `plant` costs as much
    as the reference, with both losing running tanks at pharma's rate."""
    h0 = value("pf_hazard_pharma") if hazard is None else hazard
    target = cost(reference, h0, run_days, restart_fail_days, **kw)
    return _solve(lambda p: cost(plant, h0, run_days, restart_fail_days, start_fail=p, **kw) - target, 0.95)


def best_run_days(plant: str, hazard: float, start_fail: float = 0.0, restart_fail_days: float = 14.0,
                  lengths=(2, 3, 5, 7, 10, 14, 20, 33, 45, 60, 90), **kw) -> tuple:
    """(run length in days, $/kg) that costs least for a given loss pattern."""
    return min(((L, cost(plant, hazard, L, restart_fail_days, start_fail, **kw)) for L in lengths),
               key=lambda r: r[1])


def common_mode_restart_days(tanks_lost: float, f4: float, restart_fail_days: float = 14.0) -> float:
    """Restart time per tank when `tanks_lost` tanks go down together and must queue for a seed train
    with `f4` final seed tanks."""
    return restart_fail_days + pi.restart_queue_days(tanks_lost, f4)


def threshold_table(lengths=(5.0, 10.0, 20.0, 33.0, 60.0), restart_fail_days: float = 14.0, **kw) -> list:
    """Rows (plant, run length, break-even chance per day, days between losses of one tank, share of
    runs lost at break-even) against the floor's plant at pharma's loss rate."""
    rows = []
    for plant in ("lean", "yeastplus", "yeast"):
        for L in lengths:
            h = breakeven_hazard(plant, run_days=L, restart_fail_days=restart_fail_days, **kw)
            rows.append((plant, L, h, 1.0 / h if h > 0 else float("inf"), batch_loss(h, L)))
    return rows


def main() -> None:
    print("Detection by oxygen or off-gas readings (one cell gets into a 20 m3 tank)\n")
    print(f"  {'cells in the tank':<22}{'sensors see it at':>20}{'20 min':>10}{'60 min':>10}{'6 h':>10}   doubling time")
    for x in (27.0, 60.0, 120.0):
        t = [time_to_detect_h(m, x) for m in (value("ct_doubling_fast_min"), value("ct_doubling_slow_min"),
                                              value("ct_doubling_cryptic_h") * 60.0)]
        print(f"  {x:5.0f} g/L {'':<12}{detect_threshold(x):14.1e} /mL{t[0]:9.0f}h{t[1]:9.0f}h{t[2] / 24:8.1f}d")
    print(f"\n  doublings from one cell to detection at 120 g/L: {doublings_to(detect_threshold(120.0)):.0f}"
          f"  (in a 20 L vessel: {doublings_to(detect_threshold(120.0), 0.02):.0f})")
    print(f"  contaminant mass at detection: {contaminant_share_at_detection() * 100:.3f}% of the cells' dry mass")
    for lim in (1e2, 1e4, 1e6):
        print(f"  harvest over a food limit of {lim:.0e}/g for the last {blind_hours(20.0, limit_cfu_g=lim):.1f} h "
              f"(20 min doubling) to {blind_hours(60.0, limit_cfu_g=lim):.1f} h (60 min) before detection")
    print(f"  a contaminated seed stage is passed on unseen with chance {escape_probability(20.0):.0%} (20 min), "
          f"{escape_probability(60.0):.0%} (60 min)")

    print("\nReference loss rates, per day (low - high):")
    for k, (a, b) in reference_hazards().items():
        print(f"  {k:<32} {a * 100:.2f}% - {b * 100:.2f}%")

    for mode in ("perfusion", "filldraw"):
        print(f"\nBreak-even against the floor's plant losing 0.2% of runs a day ({mode}, 14-day restart after a loss):")
        print(f"  {'plant':<8}{'run, days':>10}{'chance/day':>12}{'one loss every':>16}{'runs lost':>11}")
        for plant, L, h, every, share in threshold_table(mode=mode):
            print(f"  {plant:<10}{L:8.0f}{h * 100:11.1f}%{every:11.0f} days{share * 100:10.0f}%")
    print("\nSensitivity of the 33-day perfusion threshold:")
    for plant in ("lean", "yeastplus", "yeast"):
        base = breakeven_hazard(plant)
        r30 = breakeven_hazard(plant, restart_fail_days=30.0)
        q = breakeven_hazard(plant, restart_fail_days=common_mode_restart_days(24.0, 2.0))
        sv = breakeven_hazard(plant, salvage=1.0)
        sf = breakeven_start_fail(plant)
        print(f"  {plant:<10} base {base * 100:.1f}%/day; 30-day restart {r30 * 100:.1f}%; all 24 tanks down together, two "
              f"seed tanks {q * 100:.1f}%; cells salvaged {sv * 100:.1f}%; or {sf * 100:.0f}% of starts failing")
    print("\nAt the cultivated-meat survey's rate (1.5% a day, 14-day restart):")
    for plant in pi.PLANTS:
        h = value("pf_hazard_pharma") if plant in ("humbird", "floor") else value("ct_hazard_frontier")
        L, c = best_run_days(plant, h)
        print(f"  {pi.PLANT_LABELS[plant]:<46} at {h * 100:.1f}%/day: ${cost(plant, h):5.2f}/kg at 33 days; "
              f"best run {L} days ${c:5.2f}")


if __name__ == "__main__":
    main()
