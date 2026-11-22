#!/usr/bin/env python3
"""
thick_culture.py — how thick can a stirred or airlift culture of 17 um animal cells be?

The model's density limit is 258 g/L (320 in the all-favourable example): a volume fraction of 0.25, Humbird's "practical
maximum" from the way viscosity climbs when cells collide (floor_physics `pf_x_visc`, the 'thickness of the culture' limit in
`explore`). Since 2026-11-20 no scenario's tank reaches it: the sparger's oxygen, lowered by viscosity, stops them first. It is a rule of
thumb about viscosity. It is not a calculated limit of any machine. This module asks what viscosity does to a 20 m3 tank,
limit by limit, with the model's own tank, and what each scenario costs if the density limit were another number.

What it adds (the cost scan sets the limit through `vm={"caps": ...}`; since 2026-11-20 `explore` applies this module's
oxygen-transfer correction itself, `viscous_kla`, and the viscosity laws live in floor_physics):
  * viscosity of the suspension at any volume fraction: Thomas (the model's law, `gas_exchange.viscosity`) and
    Krieger-Dougherty with a maximum packing, with a factor for the shear thinning a large tank sees;
  * the stirrer: Reynolds number at a fixed power per volume, the power that keeps the flow turbulent (so Humbird's mixing
    time, which has no viscosity in it, still holds), the yield-stress cavern, and the smallest eddies;
  * oxygen transfer: kLa falls with the apparent viscosity, so the oxygen a sparger can supply falls with density;
  * gas hold-up (bubbles rise slower in a thick liquid), settling of the cells, and the heat the cells give off;
  * `limits_at()`: the density at which each limit binds for a given tank, and which binds first;
  * `cost_by_cap()`: a scenario's cost with the density limit held at 180, 258, 320 or 400 g/L.

Evidence and the verdict: research_notes/thick_culture.md.

Run
---
    python thick_culture.py
"""
from __future__ import annotations

import numpy as np

import floor_physics as fp
import gas_exchange as ge
import scenarios as S
from inputs import value

G = 9.81
LAWS = ("thomas", "krieger")


def phi_of(x: float) -> float:
    """Volume fraction of cells in a culture at x g wet/L."""
    return ge.cell_volume_fraction(x)


def x_of(phi: float) -> float:
    """g wet/L at a volume fraction."""
    return phi * value("pf_cell_density") * 1000.0


def cell_diameter_um(cells: fp.Cells | None = None) -> float:
    """Diameter of the model cell, um (a sphere of its wet mass at the cell density): 17.7 um for 3,000 pg."""
    m = (fp.GOOD_CELLS if cells is None else cells).mass_pg * 1e-15            # kg
    return (6.0 * m / (np.pi * value("pf_cell_density") * 1000.0)) ** (1.0 / 3.0) * 1e6


# ----------------------------------------------------------------------------
# 1. Viscosity
# ----------------------------------------------------------------------------
def rel_viscosity(phi: float, law: str = "thomas", phi_max: float | None = None) -> float:
    """The engine's (floor_physics.rel_viscosity; one implementation since 2026-11-20)."""
    return fp.rel_viscosity(phi, law, phi_max)


def apparent_rel_viscosity(x: float, law: str = "thomas", thin: float | None = None) -> float:
    """The engine's (floor_physics.apparent_rel_viscosity)."""
    return fp.apparent_rel_viscosity(x, law, thin)


def apparent_viscosity(x: float, law: str = "thomas", thin: float | None = None) -> float:
    """Pa s."""
    return value("pf_medium_viscosity") * 1e-3 * apparent_rel_viscosity(x, law, thin)


def yield_stress(x: float) -> float:
    """Yield stress of the suspension, Pa: sigma* (phi/phi_max)^8.4 (Iordan et al. 2007's scaling, `tc_yield_*`). About 5e-4 Pa at
    a quarter cells, 0.15 Pa at half. Their plotted values were not extracted, so this is their scaling with their stress scale."""
    return value("tc_yield_sigma") * (phi_of(x) / value("tc_phi_max")) ** value("tc_yield_exp")


def viscosity_table(phis=(0.1, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5)) -> list:
    """[(phi, g/L, million cells/mL, Thomas, Krieger, apparent mPa s, yield stress Pa)] at the model cell's size."""
    d = cell_diameter_um() * 1e-6
    vc = np.pi * d ** 3 / 6.0 * 1e6                                       # mL per cell
    rows = []
    for p in phis:
        x = x_of(p)
        rows.append((p, x, p / vc / 1e6, rel_viscosity(p, "thomas"), rel_viscosity(p, "krieger"),
                     apparent_viscosity(x) * 1e3, yield_stress(x)))
    return rows


# ----------------------------------------------------------------------------
# 2. The stirrer
# ----------------------------------------------------------------------------
def eddy_um(x: float, power_w_m3: float, law: str = "thomas", thin: float | None = None) -> float:
    """Smallest eddies near the impeller, um: Kolmogorov's scale (nu^3 / eps)^(1/4) with the dissipation there `tc_peak_dissipation`
    (50) times the tank's mean, as in Humbird's Eq. 2.17, but with the viscosity of the culture. Thicker culture, larger eddies,
    gentler on the cells (if the cells feel the bulk viscosity, which cells smaller than the eddies may not)."""
    rho = ge.suspension_density(x)
    eps = power_w_m3 / rho * value("tc_peak_dissipation")
    return ((apparent_viscosity(x, law, thin) / rho) ** 3 / eps) ** 0.25 * 1e6


def stirrer(x: float, vessel_m3: float = 20.0, aspect: float | None = None, power_w_m3: float | None = None,
            law: str = "thomas", thin: float | None = None, np_: float | None = None) -> dict:
    """The stirrer of a tank at a fixed power per volume of liquid (default 43 W/m3, Humbird's: the power at which the smallest
    eddies are about a cell across), with an impeller a third of the tank wide (Humbird's Fig. 2.5) of power number `tc_np`.

    Returns speed (1/s), Reynolds number, whether the flow is fully turbulent (Humbird's mixing time, which has no viscosity in
    it, then holds), the power per volume that keeps it turbulent, the stress at the impeller over the yield stress and the
    tank-to-cavern ratio (the cavern fills the tank when the stress ratio exceeds (T/D)^3, to within a coefficient of order one),
    and the smallest eddies near the impeller in um (Humbird's Eq. 2.17, with the medium's viscosity replaced by the culture's)."""
    pv = value("ge_stir_power") if power_w_m3 is None else power_w_m3
    np_ = value("tc_np") if np_ is None else np_
    T, H = fp.tank_shape(vessel_m3, aspect)
    D = T / 3.0
    V = value("pf_working_volume") * vessel_m3
    rho = ge.suspension_density(x)
    mu = apparent_viscosity(x, law, thin)
    P = pv * V
    N = (P / (np_ * rho * D ** 5)) ** (1.0 / 3.0)
    Re = rho * N * D * D / mu
    p_turb = np_ * value("tc_re_turb") ** 3 * mu ** 3 / (rho ** 2 * D) / V      # W/m3 that gives Re = Re_turb
    tau_imp = np_ * rho * N * N * D * D
    tau_y = max(yield_stress(x), 1e-12)
    eddy = eddy_um(x, pv, law, thin)
    return {"T": T, "D": D, "N_rps": N, "rpm": N * 60.0, "tip_m_s": np.pi * N * D, "Re": Re,
            "turbulent": Re >= value("tc_re_turb"), "re_margin": Re / value("tc_re_turb"),
            "mu_mpas": mu * 1e3, "power_to_stay_turbulent": p_turb,
            "power_for_same_mixing": max(pv, p_turb), "stress_ratio": tau_imp / tau_y,
            "cavern_fills_tank": tau_imp / tau_y > (T / D) ** 3, "eddy_um": eddy}


def gas_power(x: float, gas_velocity: float | None = None) -> float:
    """W per m3 of liquid the rising gas gives the tank: density x g x superficial velocity. An airlift has only this; at the
    model's 6 mm/s it is 59 W/m3 (research_notes/gas_flow_cap.md, section 3), more than the stirrer's 43."""
    us = value("pf_gas_velocity") if gas_velocity is None else gas_velocity
    return ge.suspension_density(x) * G * us


# ----------------------------------------------------------------------------
# 3. Oxygen transfer, gas hold-up, settling, heat
# ----------------------------------------------------------------------------
def kla_factor(x: float, law: str = "thomas", thin: float | None = None, exponent: float | None = None) -> float:
    """The engine's (floor_physics.kla_factor): kLa of the thick culture over the kLa in medium."""
    return fp.kla_factor(x, law, thin, exponent)


def oxygen_limit(x_base: float, law: str = "thomas", thin: float | None = None, exponent: float | None = None) -> float:
    """The engine's (floor_physics.oxygen_limit): the density a sparger can feed once viscosity is counted, from the limit
    `x_base` with the kLa of medium. explore() applies it itself since 2026-11-20 (`viscous_kla`)."""
    return fp.oxygen_limit(x_base, law, thin, exponent)


def _rise_speed(d_m: float, mu: float, rho: float) -> float:
    """Terminal speed (m/s) of a bubble of diameter d_m in a liquid of viscosity mu and density rho, with the drag of a rigid
    sphere (Schiller and Naumann), which is what a bubble in a protein- and polymer-laden medium behaves like."""
    lo, hi = 1e-4, 5.0
    for _ in range(80):
        u = 0.5 * (lo + hi)
        re = rho * u * d_m / mu
        cd = 24.0 / re * (1.0 + 0.15 * re ** 0.687)
        # excess of weight over drag: positive while the bubble can still speed up
        if (4.0 * d_m * G * rho) / (3.0 * cd * rho) > u * u:
            lo = u
        else:
            hi = u
    return 0.5 * (lo + hi)


def holdup(x: float, gas_velocity: float | None = None, law: str = "thomas", thin: float | None = None) -> float:
    """Share of the tank that is gas: the measured 4% at 6 mm/s (`tc_holdup`), in proportion to the gas velocity and to the
    inverse of the bubbles' rise speed, which falls as the liquid thickens."""
    us = value("pf_gas_velocity") if gas_velocity is None else gas_velocity
    d = value("tc_bubble_mm") * 1e-3
    mu0 = value("pf_medium_viscosity") * 1e-3
    u0 = _rise_speed(d, mu0, value("pf_medium_density") * 1000.0)
    u1 = _rise_speed(d, apparent_viscosity(x, law, thin), ge.suspension_density(x))
    return min(0.5, value("tc_holdup") * us / value("pf_gas_velocity") * u0 / u1)


def settling(x: float, vessel_m3: float = 20.0, aspect: float | None = None) -> dict:
    """Settling of single cells in the culture: Stokes' speed in medium, slowed by crowding (Richardson-Zaki, (1 - phi)^4.65).
    Returns cm/h, days to fall the liquid's depth with nothing stirring, and the speed over the gas velocity."""
    d = cell_diameter_um() * 1e-6
    drho = (value("pf_cell_density") - value("pf_medium_density")) * 1000.0
    v0 = d * d * drho * G / (18.0 * value("pf_medium_viscosity") * 1e-3)                  # m/s
    v = v0 * (1.0 - phi_of(x)) ** 4.65
    _T, depth = fp.tank_shape(vessel_m3, aspect)
    return {"v_cm_h": v * 360000.0, "days_to_fall": depth / v / 86400.0, "over_gas_velocity": v / value("pf_gas_velocity")}


def heat_w_m3(x: float, cells: fp.Cells | None = None) -> float:
    """Heat the cells give off, W per m3 of liquid: oxygen used x the heat of respiration (`pf_heat_per_o2`)."""
    cells = fp.GOOD_CELLS if cells is None else cells
    # x g/L x mmol/g/h = mol/m3/h; x kJ/mol x 1000 J/kJ / 3600 s/h
    return x * cells.qo2 * value("pf_heat_per_o2") / 3.6


def cooling_w_m3(vessel_m3: float = 20.0, aspect: float | None = None) -> float:
    """What the jacket on the wall and floor takes off, W per m3 of liquid: U x area x temperature difference / liquid volume
    (`tc_jacket_u`, `tc_cool_dt`; both assumed). Internal coils would add to it."""
    T, H = fp.tank_shape(vessel_m3, aspect)
    area = np.pi * T * H + np.pi * T * T / 4.0
    return value("tc_jacket_u") * area * value("tc_cool_dt") / (value("pf_working_volume") * vessel_m3)


def heat_limit(vessel_m3: float = 20.0, aspect: float | None = None, cells: fp.Cells | None = None) -> float:
    """Density (g/L) at which the cells' heat equals what the jacket removes."""
    return cooling_w_m3(vessel_m3, aspect) / heat_w_m3(1.0, cells)


# ----------------------------------------------------------------------------
# 4. Which limit binds first
# ----------------------------------------------------------------------------
def turbulence_limit(vessel_m3: float = 20.0, aspect: float | None = None, power_w_m3: float | None = None,
                     law: str = "thomas", thin: float | None = None, np_: float | None = None) -> float:
    """Density (g/L) above which the flow at the given stirring power is no longer fully turbulent (Re below `tc_re_turb`)."""
    lo, hi = 1.0, x_of(0.64)
    if stirrer(hi, vessel_m3, aspect, power_w_m3, law, thin, np_)["turbulent"]:
        return float("inf")
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if stirrer(mid, vessel_m3, aspect, power_w_m3, law, thin, np_)["turbulent"]:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _loop_ok(kw: dict, cap: float) -> bool:
    # the case's own vessel settings, without a thinned design's cap on the loop (scenarios.design, 2026-11-21): this asks where
    # the loop itself stops passing
    vm = dict(kw.get("vm") or {})
    caps = {k: v for k, v in vm.get("caps", {}).items() if k != "what the column can strip safely"}
    vm["caps"] = {**caps, "thickness of the culture": float(cap)}
    r = fp.explore(**{**kw, "vm": vm})
    d = r["column"]
    return d is None or (d["ph_vs_safe"] <= 1.0 + 1e-9 and d["passes_tested"])


def loop_check_limit(kw: dict | None = None) -> float:
    """Density (g/L) above which the column loop of a tank design breaks the model's two screening rules (the culture's pH
    exposure stays at the design judged safe; no more passes an hour than dense cultures have taken, `ge_passes_tested`).
    These are rules, not walls: a bigger column passes more culture. Infinite for a tank with no column. The loop must pass
    the CO2 (and oxygen) that the sparger cannot, which grows faster than density."""
    kw = {} if kw is None else kw
    if kw.get("column", "none") == "none":
        return float("inf")
    lo, hi = 20.0, x_of(0.60)
    if _loop_ok(kw, hi):
        return float("inf")
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if _loop_ok(kw, mid):
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def cost_viscous_oxygen(key: str, law: str = "thomas", thin: float | None = None, exponent: float | None = None) -> dict:
    """A scenario's cost if oxygen from the sparger is limited by viscosity (kLa falls with the apparent viscosity): the
    scenario's own tank, with its 'oxygen supply' limit replaced by `oxygen_limit`. {'cost', 'density', 'limit', 'base_cost',
    'oxygen_base', 'oxygen_viscous'}."""
    kw = S.explore_kwargs(S.SCENARIOS[key].choice)
    r0 = fp.explore(**kw, viscous_kla=False)          # the engine counts viscosity itself since 2026-11-20: off for the base
    xo = oxygen_limit(r0["limits"]["oxygen supply"], law, thin, exponent)
    r = fp.explore(**kw, viscous_kla=False, vm={"caps": {"oxygen supply": float(xo)}}) if np.isfinite(xo) else r0
    return {"cost": float(r["total"]), "density": float(r["density"]), "limit": r["limit"], "base_cost": float(r0["total"]),
            "oxygen_base": float(r0["limits"]["oxygen supply"]), "oxygen_viscous": float(xo)}


def limits_at(kw: dict | None = None, law: str = "thomas", thin: float | None = None, exponent: float | None = None) -> dict:
    """The density (g/L) at which each limit stops a tank, for the tank of `explore(**kw)` (default: Humbird's 20 m3 stirred tank).
    Gas-side limits are explore's own, except oxygen, which is corrected for viscosity. Added: the stirrer's turbulence, the
    heat, and the retention devices' ceilings (`rt_atf_phi_max`, `rt_tff_phi_max`). The viscosity rule of the model (258) is
    listed as 'model: thickness of the culture'. Returns {'limits': {name: g/L}, 'first': name, 'x': g/L, 'result': explore's}."""
    kw = {} if kw is None else kw
    r = fp.explore(**{**kw, "viscous_kla": False})   # the uncorrected oxygen limit; viscosity is applied below
    lim = dict(r["limits"])
    lim["oxygen supply, with viscosity"] = oxygen_limit(lim["oxygen supply"], law, thin, exponent)
    vessel, aspect = kw.get("vessel_m3", 20.0), kw.get("aspect")
    lim["stirrer turbulence"] = turbulence_limit(vessel, aspect, None, law, thin)
    lim["cooling by the jacket"] = heat_limit(vessel, aspect)
    lim["column loop checks"] = loop_check_limit(kw)
    lim["ATF filter (Clincke)"] = x_of(value("rt_atf_phi_max"))
    lim["TFF filter (Clincke)"] = x_of(value("rt_tff_phi_max"))
    # the model's own rule (258) and its uncorrected oxygen limit are replaced; the filters are shown, not counted
    physical = {k: v for k, v in lim.items() if k not in ("oxygen supply", "thickness of the culture", "ATF filter (Clincke)",
                                                          "TFF filter (Clincke)")}
    first = min(physical, key=physical.get)
    return {"limits": lim, "first": first, "x": physical[first], "result": r}


# ----------------------------------------------------------------------------
# 5. What the cost does if the density limit is somewhere else
# ----------------------------------------------------------------------------
def _best_design(choice: dict, cap: float, redesign: bool, checked: bool):
    """Cheapest (explore result, choice) with the 'thickness of the culture' limit held at `cap`. With `redesign` the tank
    tricks and shape are chosen again among the scenario switches' settings; with `checked` a design whose column loop breaks
    the pH exposure or pass-rate checks (scenarios.design's rule) is refused."""
    tricks = S.SW["tricks"].settings if redesign else [S.setting("tricks", choice["tricks"])]
    shapes = S.SW["shape"].settings if redesign else [S.setting("shape", choice["shape"])]
    best = None

    def run(c):
        kw = S.explore_kwargs(c)
        vm = dict(kw.get("vm") or {})
        vm["caps"] = {**vm.get("caps", {}), "thickness of the culture": float(cap)}
        return fp.explore(**{**kw, "vm": vm})
    base = choice if not redesign else {k: v for k, v in choice.items() if k != "thin"}
    for tk in tricks:
        for sh in shapes:
            c = {**base, "tricks": tk.key, "shape": sh.key}
            r = run(c)
            if checked and not S.loop_ok(r):
                # as scenarios.design (2026-11-21): the same design with the culture held thinner, at the densest its loop passes
                lo, hi, ok = 0.0, float(r["density"]), None
                for _ in range(S.THIN_STEPS):
                    mid = 0.5 * (lo + hi)
                    rr = run({**c, "thin": mid})
                    if S.loop_ok(rr):
                        lo, ok = mid, (rr, {**c, "thin": mid})
                    else:
                        hi = mid
                if ok is None:
                    continue
                r, c = ok
            if best is None or r["total"] < best[0]["total"] - 1e-12:
                best = (r, c)
    return best


def cost_by_cap(key: str, caps=(180.0, 258.0, 320.0, 400.0)) -> dict:
    """A scenario's cost per kg of cells if its density limit ('thickness of the culture') were each of `caps`, g/L. Nothing else
    changes. Two readings per cap:
      'fixed'  the scenario's own tank design, the column loop not checked: what the physics the model has gives;
      'checked' the tank design chosen again, as `scenarios.design` does, with the loop checks (a pH-safe loop at a pass rate dense
                cultures have taken): the loop's own limits can stop the design from using a thicker culture.
    Each entry: {'cost', 'density', 'limit', 'design' (tricks/shape)}. Where another limit holds the culture below the cap, the
    density is that limit's and 'limit' names it."""
    choice = S.SCENARIOS[key].choice
    out = {}
    for cap in caps:
        row = {}
        for name, redesign, checked in (("fixed", False, False), ("checked", True, True)):
            b = _best_design(choice, cap, redesign, checked)
            r, c = b
            row[name] = {"cost": float(r["total"]), "density": float(r["density"]), "limit": r["limit"],
                         "design": f"{c['tricks']}/{c['shape']}"}
        out[float(cap)] = row
    return out


def humbird_basis() -> dict:
    """What 258 g/L stands for: the volume fraction, the cells per mL for the model cell, and the viscosity at that fraction."""
    x = value("pf_x_visc")
    p = phi_of(x)
    d = cell_diameter_um() * 1e-6
    n = x / (fp.GOOD_CELLS.mass_pg * 1e-12 * 1e3)                          # cells per mL at x g/L
    return {"x": x, "phi": p, "cells_ml": n, "diameter_um": d * 1e6, "thomas": rel_viscosity(p, "thomas"),
            "krieger": rel_viscosity(p, "krieger"), "mpas": apparent_viscosity(x, thin=1.0) * 1e3}


def summarise() -> None:
    hb = humbird_basis()
    print(f"258 g/L = volume fraction {hb['phi']:.3f}, {hb['cells_ml']/1e6:.0f} million {hb['diameter_um']:.1f} um cells/mL; "
          f"viscosity x{hb['thomas']:.2f} (Thomas), x{hb['krieger']:.2f} (Krieger, phi_max 0.65): {hb['mpas']:.2f} mPa s")
    print("  phi    g/L   Mcells/mL  Thomas  Krieger  apparent mPa s  yield Pa")
    for row in viscosity_table():
        print("  %.2f %6.0f %9.0f %8.2f %8.2f %12.2f %10.4f" % row)
    print("\nstirrer, 20 m3, 43 W/m3, power number 5 (Re, rpm, eddies near the impeller um, W/m3 to stay turbulent):")
    for p in (0.1, 0.25, 0.4, 0.5):
        s = stirrer(x_of(p))
        print(f"  phi {p:.2f}: Re {s['Re']:.0f} ({s['rpm']:.0f} rpm), eddy {s['eddy_um']:.0f} um, turbulent {s['turbulent']}, "
              f"stay turbulent at {s['power_to_stay_turbulent']:.0f} W/m3, stress ratio {s['stress_ratio']:.0f}")
    print("\nkLa factor, gas hold-up, settling, heat (20 m3, 6 mm/s):")
    for p in (0.1, 0.25, 0.4, 0.5):
        x = x_of(p)
        s = settling(x)
        print(f"  phi {p:.2f}: kLa x{kla_factor(x):.2f}, hold-up {holdup(x) * 100:.1f}%, settling {s['v_cm_h']:.2f} cm/h "
              f"({s['days_to_fall']:.0f} days to fall), heat {heat_w_m3(x) / 1000:.1f} kW/m3, gas power {gas_power(x):.0f} W/m3, "
              f"eddies at gas+stirrer power {eddy_um(x, 43.0 + gas_power(x)):.0f} um")
    print(f"  jacket takes {cooling_w_m3():.0f} W/m3 (tall) and {cooling_w_m3(aspect=0.5):.0f} W/m3 (flat)")
    print("\nlimits of three tanks (g/L):")
    for name, kw in (("Humbird's tank, no added equipment for oxygen and CO₂", {}),
                     ("the low-lactate example's design", S.explore_kwargs(S.SCENARIOS["central"].choice)),
                     ("the all-favourable example's design", S.explore_kwargs(S.SCENARIOS["best"].choice))):
        L = limits_at(kw)
        print(f"  {name}: first {L['first']} at {L['x']:.0f}; " +
              ", ".join(f"{k} {v:.0f}" for k, v in L["limits"].items() if np.isfinite(v)))
    print("\ncost at each density limit, $/kg (fixed design / design chosen again with the loop checks):")
    for k in S.ORDER:
        c = cost_by_cap(k)
        print(f"  {k:<13}" + "  ".join(f"{cap:.0f}: ${v['fixed']['cost']:.2f}/${v['checked']['cost']:.2f}" for cap, v in c.items()))
    print("\ncost if viscosity lowers the oxygen a sparger can feed (kLa x apparent viscosity^-0.4):")
    for k in S.ORDER:
        v = cost_viscous_oxygen(k)
        print(f"  {k:<13}${v['base_cost']:.2f} -> ${v['cost']:.2f}; oxygen limit {v['oxygen_base']:.0f} -> {v['oxygen_viscous']:.0f} g/L; "
              f"density {v['density']:.0f} ({v['limit']})")


if __name__ == "__main__":
    summarise()
