#!/usr/bin/env python3
"""
filter_flux.py — can a hollow-fibre filter hold a flux of 5 L/m2/h at 25% cells by volume for a month?

Why
---
The default retention device is a TFF hollow-fibre loop (retention.py) at a permeate flux of 5 L/m2/h (`rt_flux_lmh`), with
membranes replaced after 3,960 litres a m2 (`rt_membrane_life`, one 33-day run at 5 L/m2/h). Two questions follow. Is 5 L/m2/h
above a physical limit? And is a life of 3,960 litres consistent with what has been measured?

The physical limit
------------------
Cells carried to the wall by the flow of liquid through the membrane are swept back by shear-induced diffusion. The limiting flux
(Belfort, Davis and Zydney 1994, as printed in Vyas 1999, Eq. 2.18) is

    J = 0.078 x gamma_w x (phi_w a^4 / (phi_b L))^(1/3) x ln(phi_w / phi_b)

with the wall shear rate gamma_w, cell radius a, fibre length L, the cell volume fraction in the bulk phi_b and at the wall phi_w.
Davis and Sherwood's form (Kromkamp 2005) has 0.072 and no logarithm, and is valid for phi_b below 0.1. Both are for rigid,
non-sticking spheres, and the 12-25% cells here are an extrapolation. Real yeast gave fluxes 2 to 4 times lower
(Redkar and Davis 1993). The ceiling says nothing about fouling by debris, DNA, protein and antifoam, which limits real filters.

What is measured
----------------
Sustained fluxes of 1 to 3 L/m2/h; membranes that foul after 450 to 1,200 litres a m2 (Pinto 2020; Veje 2024).

Run
---
    python filter_flux.py
"""
from __future__ import annotations

import math

import floor_physics as fp
import retention
import scenarios as S
from inputs import value

LMH = 3.6e6                                 # m/s to L/m2/h


def cell_radius_m(cells: fp.Cells | None = None) -> float:
    """Radius of a model cell as a sphere, metres (the same diameter thick_culture uses)."""
    cells = fp.GOOD_CELLS if cells is None else cells
    return (3.0 * cells.mass_pg * 1e-15 / (4.0 * math.pi * value("pf_cell_density") * 1000.0)) ** (1.0 / 3.0)


def backtransport_lmh(phi_b: float, shear: float | None = None, length: float | None = None, radius: float | None = None,
                      form: str = "belfort") -> float:
    """The limiting flux of shear-induced back-transport, L/m2/h. `form` is 'belfort' (with the logarithm) or 'davis'
    (Davis and Sherwood, valid for phi_b < 0.1)."""
    shear = value("ff_shear") if shear is None else shear
    length = value("ff_length") if length is None else length
    a = cell_radius_m() if radius is None else radius
    phi_w = value("ff_phi_w")
    core = (phi_w * a ** 4 / (phi_b * length)) ** (1.0 / 3.0)
    if form == "belfort":
        j = value("ff_coef_belfort") * shear * core * math.log(phi_w / phi_b)
    elif form == "davis":
        j = value("ff_coef_ds") * shear * core
    else:
        raise KeyError(form)
    return j * LMH


def shear_for_flux(flux_lmh: float, phi_b: float, length: float | None = None, form: str = "belfort") -> float:
    """The wall shear rate (1/s) at which the ceiling equals `flux_lmh`: the flux is proportional to the shear."""
    return flux_lmh / backtransport_lmh(phi_b, shear=1.0, length=length, form=form)


def margin(phi_b: float, flux_lmh: float | None = None, **kw) -> dict:
    """The ceiling against the flux the model assumes, and against the ceiling cut by the yeast shortfall."""
    flux = value("rt_flux_lmh") if flux_lmh is None else flux_lmh
    c = backtransport_lmh(phi_b, **kw)
    return {"ceiling": c, "ratio": c / flux, "cut_ceiling": c / value("ff_yeast_shortfall"),
            "cut_ratio": c / value("ff_yeast_shortfall") / flux}


def cost_at(key: str, flux_lmh: float, life_l_m2: float) -> float:
    """A scenario's cost with the filter at this flux and membrane life (the model's defaults are 5 and 3,960)."""
    with retention._with({"rt_flux_lmh": flux_lmh, "rt_membrane_life": life_l_m2}):
        return retention.scenario_cost("tff", S.explore_kwargs(S.SCENARIOS[key].choice))["total"]


def cost_at_life_price(key: str, life_l_m2: float, price_per_m2: float) -> float:
    """A scenario's cost with the cell filter at this membrane life and this membrane price (defaults: 3,960 L/m2 and $1,450/m2).
    What the membrane adds to a litre of permeate is price / life, so the two have to be read together."""
    with retention._with({"rt_membrane_life": life_l_m2, "rt_membrane_price": price_per_m2}):
        return retention.scenario_cost("tff", S.explore_kwargs(S.SCENARIOS[key].choice))["total"]


def break_even_price(life_l_m2: float) -> float:
    """The membrane price ($/m2) at which a membrane of this life adds the same cost per litre of permeate as the model's
    defaults (price / life = $0.366 a litre). A shorter life raises Central's cost only if membranes stay dearer than this."""
    return life_l_m2 * value("rt_membrane_price") / value("rt_membrane_life")


def time_limited_life(flux_lmh: float, days: float | None = None) -> float:
    """Litres a membrane filters if it is replaced once a run: flux x hours. The default life is this at 5 L/m2/h and 33 days."""
    return flux_lmh * 24.0 * (value("pf_run_days") if days is None else days)


def summarise() -> None:
    print("  back-transport ceiling, L/m2/h (cells a = %.1f um, wall layer %.2f):" % (cell_radius_m() * 1e6, value("ff_phi_w")))
    print("    L (m)  shear (1/s)  phi_b   Belfort   Davis   against 5 L/m2/h")
    for L in (0.3, 1.0):
        for g in (1000.0, 2000.0, 4000.0):
            for pb in (0.12, 0.25):
                b, d = backtransport_lmh(pb, g, L), backtransport_lmh(pb, g, L, form="davis")
                print(f"    {L:4.1f}  {g:9.0f}   {pb:5.2f}  {b:8.0f}  {d:6.0f}   {b / 5:5.0f}x")
    print(f"  shear at which 5 L/m2/h is the ceiling: {shear_for_flux(5.0, 0.12):.0f} to {shear_for_flux(5.0, 0.25, length=1.0):.0f} 1/s")
    print("  Central, $/kg, by membrane life (rows, L/m2) and membrane price (columns, $/m2); what counts is price / life:")
    prices = (1450.0, 550.0, 200.0, 50.0)
    print("    life      " + "".join(f"{pr:>9.0f}" for pr in prices) + "   break-even price")
    for life in (3960.0, 2000.0, 1500.0, 1000.0):
        print(f"    {life:6.0f}    " + "".join(f"{cost_at_life_price('central', life, pr):9.2f}" for pr in prices)
              + f"   ${break_even_price(life):.0f}")
    print("  cost per kg with the measured membrane throughput (flux, life):")
    for key in ("best", "central"):
        row = "; ".join(f"({f:g}, {l:g}) ${cost_at(key, f, l):.2f}" for f, l in
                        ((5.0, 3960.0), (5.0, 1200.0), (2.5, 1200.0), (2.5, 450.0), (1.5, 450.0)))
        print(f"    {key:<8} {row}")


if __name__ == "__main__":
    summarise()
