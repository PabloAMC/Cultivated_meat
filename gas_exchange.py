#!/usr/bin/env python3
"""
gas_exchange.py — side-study to floor_physics.py: how else could a 20 m3 tank of animal cells get rid
of its CO2 and take in its oxygen?  (NOT used in the headline cost or on the page.)

Three questions, each answered by functions here and written up in research_notes/gas_exchange_study.md:

1. A membrane loop ("a lung for the tank"): pump the culture through hollow fibres with a sweep gas
   on the other side. How much liquid flow, membrane area and money per m3 of tank, as a function of
   cell density?  (`loop_design`, `loop_table`, `floor_with_loop`)
2. Tank shape: what do squat, tall, horizontal and many-celled tanks do to the density and the cost
   per kg, once the vessel's own cost is made to depend on shape?  (`shape_case`, `shape_table`)
3. A published cheap design: can Negulescu et al.'s 262 m3 airlift hold its 100 g/L against the CO2
   balance?  (`airlift_check`)

The chain of reasoning for the loop
-----------------------------------
* What the cells make and use, per litre of culture per hour:  CO2 = RQ x qO2 x X,  O2 = qO2 x X.
* What a litre of culture gives up in one pass. Dissolved CO2 is only 0.0246 mmol/L per mbar, so a
  litre at 100 mbar carries 2.5 mmol and gives up half of it if stripped to 50 mbar. The 31 mmol/L of
  bicarbonate is NOT available: turning bicarbonate into CO2 uses up an acid, and culture medium has
  almost none to spare (blood has haemoglobin, which is why medical devices do better per litre). So

      CO2 per pass = s x (p_in - p_out) + buffer x (pH rise),      pH rise ~ log10(p_in / p_out)

  Oxygen is worse: liquid in contact with pure O2 at 1 bar holds 1 mmol/L, and there is no carrier.
* So the liquid must go round often:   passes per hour = load / (amount per pass).
* Inside a fibre the flow is laminar and the CO2 has to diffuse to the wall. Leveque's solution gives
  the wall coefficient, k = 1.62 (D/d) Gz^(1/3) with Gz = v d^2 / (D L); the membrane wall adds its own
  resistance in series. The fraction exchanged in a pass is 1 - exp(-4 K L / (v d)).
* Area, pressure drop (Hagen-Poiseuille), shear at the wall (8 v / d), pump power and cost follow.

Run
---
    python gas_exchange.py            # prints the tables used in the note
"""

from __future__ import annotations

import numpy as np

from inputs import value
import floor_physics as fp

R_GAS = 8.314
T_K = 310.15
BARRER = 3.35e-16          # mol m / (m2 s Pa)


# ----------------------------------------------------------------------------
# 1. Loads and what a litre of culture carries
# ----------------------------------------------------------------------------
def gas_load(x: float, cells: fp.Cells | None = None) -> tuple:
    """(CO2 made, O2 used) in mmol per litre of culture per hour at density x (g wet/L)."""
    cells = fp.GOOD_CELLS if cells is None else cells
    return value("pf_rq") * cells.qo2 * x, cells.qo2 * x


def cell_volume_fraction(x: float) -> float:
    """Share of the culture's volume that is cells."""
    return x / (value("pf_cell_density") * 1000.0)


def viscosity(x: float) -> float:
    """Viscosity of the culture, Pa s, from Thomas's equation for suspensions (the one Clincke et al.
    2013 use for CHO at 1-2 x 10^8 cells/mL): mu/mu0 = 1 + 2.5 phi + 10.05 phi^2 + 0.00273 exp(16.6 phi)."""
    phi = cell_volume_fraction(x)
    rel = 1.0 + 2.5 * phi + 10.05 * phi ** 2 + 0.00273 * np.exp(16.6 * phi)
    return value("pf_medium_viscosity") * 1e-3 * rel


def co2_per_pass(p_in: float, p_out: float, buffer: float | None = None) -> tuple:
    """(mmol of CO2 a litre gives up when its CO2 pressure falls from p_in to p_out mbar, pH rise).
    The dissolved gas, plus what the non-bicarbonate buffer lets bicarbonate release. Alkalinity is
    conserved, so the pH rises; with no buffer the rise is log10(p_in/p_out)."""
    buffer = value("ge_buffer") if buffer is None else buffer
    s = value("pf_co2_henry")
    alk = s * p_in * 10.0 ** (value("pf_ph") - value("pf_pk1"))      # bicarbonate at the tank's pH
    dph = np.log10(p_in / p_out)
    for _ in range(30):                                               # bicarbonate falls by buffer x dpH
        dph = np.log10(max(1e-9, alk - buffer * dph) / alk) + np.log10(p_in / p_out)
    return s * (p_in - p_out) + buffer * dph, float(dph)


# ----------------------------------------------------------------------------
# 2. One fibre: laminar flow inside a tube whose wall is a gas-exchange membrane
# ----------------------------------------------------------------------------
def membrane_k(gas: str, wall_um: float | None = None) -> float:
    """The membrane wall as a mass-transfer coefficient on the liquid's concentration scale, m/s:
    permeability / thickness / solubility. Dense silicone (PDMS), the steam-sterilisable choice."""
    wall = (value("ge_wall_um") if wall_um is None else wall_um) * 1e-6
    if wall <= 0:
        return float("inf")                                           # a microporous wall: no resistance
    perm = value("ge_pdms_co2" if gas == "co2" else "ge_pdms_o2") * BARRER
    sol = (value("pf_co2_henry") if gas == "co2" else value("ge_o2_henry")) * 1e-2   # mol/m3 per Pa
    return perm / wall / sol


def exchanged_fraction(length: float, d: float, v: float, gas: str, wall_um: float | None = None) -> float:
    """Fraction of the way to equilibrium with the sweep gas that the liquid gets in one pass through a
    fibre of bore d and length `length` (m) at mean velocity v (m/s)."""
    D = value("ge_d_co2" if gas == "co2" else "ge_d_o2")
    gz = v * d * d / (D * length)
    k_liq = max(1.62 * gz ** (1.0 / 3.0), 3.66) * D / d              # Leveque; 3.66 is the long-tube limit
    K = 1.0 / (1.0 / k_liq + 1.0 / membrane_k(gas, wall_um))
    return 1.0 - float(np.exp(-4.0 * K * length / (v * d)))


def fibre_length(frac: float, d: float, v: float, gas: str = "co2", wall_um: float | None = None) -> float:
    """Length of fibre (m) that exchanges `frac` of the gas in one pass (bisection)."""
    lo, hi = 1e-4, 50.0
    for _ in range(80):
        mid = (lo * hi) ** 0.5
        if exchanged_fraction(mid, d, v, gas, wall_um) < frac:
            lo = mid
        else:
            hi = mid
    return (lo * hi) ** 0.5


# ----------------------------------------------------------------------------
# 3. The loop, sized for a density
# ----------------------------------------------------------------------------
def loop_design(x: float, co2_frac: float | None = None, oxygen: bool = False, p_tank: float | None = None,
                p_sweep: float | None = None, bore_mm: float | None = None, shear: float | None = None,
                buffer: float | None = None, wall_um: float | None = None, sparge_velocity: float = 0.0,
                o2_bar: float | None = None, cost_m2: float | None = None, life_y: float | None = None,
                vessel_m3: float = 20.0, cells: fp.Cells | None = None) -> dict:
    """Size an external hollow-fibre loop for a tank at density x (g wet/L).

    `co2_frac`   how far each pass takes the liquid's CO2 towards the sweep gas (0.5 = 100 -> 55 mbar
                 against a 10 mbar sweep). More per pass means fewer passes but longer fibres.
    `oxygen`     False: the loop removes CO2 only and oxygen still comes from a sparger.
                 True: the loop must also carry all the oxygen (no sparging at all).
    `sparge_velocity`  gas still sparged (m/s); it carries off its own share of CO2 (the model's balance).
    Everything is per m3 of CULTURE unless it says per m3 of vessel."""
    cells = fp.GOOD_CELLS if cells is None else cells
    co2_frac = value("ge_co2_frac") if co2_frac is None else co2_frac
    p_tank = value("pf_pco2_limit") if p_tank is None else p_tank
    p_sweep = value("ge_sweep_pco2") if p_sweep is None else p_sweep
    d = (value("ge_bore_mm") if bore_mm is None else bore_mm) * 1e-3
    shear = value("ge_shear") if shear is None else shear
    o2_bar = value("ge_o2_bar") if o2_bar is None else o2_bar
    cost_m2 = value("ge_cost_m2") if cost_m2 is None else cost_m2
    life_y = value("ge_life_y") if life_y is None else life_y
    wv = value("pf_working_volume")

    co2, o2 = gas_load(x, cells)
    _T, depth = fp.tank_shape(vessel_m3)
    by_sparge = sparge_velocity / depth * 3600.0 * (p_tank * 100.0 / (R_GAS * T_K)) * value("pf_co2_strip_eff")
    co2_loop = max(0.0, co2 - by_sparge)

    v = shear * d / 8.0                                               # wall shear rate = 8 v / d
    length = fibre_length(co2_frac, d, v, "co2", wall_um)
    p_out = p_tank - co2_frac * (p_tank - p_sweep)
    per_pass, dph = co2_per_pass(p_tank, p_out, buffer)
    passes = co2_loop / per_pass                                      # tank volumes per hour, for CO2

    # oxygen through the same fibres: the liquid moves towards saturation with the gas in the bore
    o2_frac = exchanged_fraction(length, d, v, "o2", wall_um)
    o2_sat = value("ge_o2_henry") * o2_bar * 1000.0                   # mmol/L against the lumen gas
    o2_pass = o2_frac * (o2_sat - value("ge_do_setpoint"))            # mmol/L taken up per pass
    passes_o2 = o2 / o2_pass
    if oxygen:
        passes = max(passes, passes_o2)
    o2_share = min(1.0, passes * o2_pass / o2)                        # share of the oxygen the loop supplies

    area = passes / 3600.0 * 4.0 * length / (v * d)                   # m2 of fibre wall per m3 of culture
    mu = viscosity(x)
    dp = 32.0 * mu * v * length / d ** 2 * value("ge_headloss_x")     # Pa, fibres plus headers and piping
    power = passes / 3600.0 * dp / value("ge_pump_eff")               # W per m3 of culture
    flow = passes * wv * vessel_m3                                    # m3/h through the loop
    flux_co2 = co2_loop / area * 1000.0 if area > 0 else 0.0          # mmol per m2 per hour

    # money, per m3 of VESSEL (the plant's basis) and per kg
    area_vessel = area * wv
    capex = area_vessel * cost_m2 * value("ge_install_x") / 1000.0    # $k per m3 of vessel
    capex += value("ge_pump_cost") * (flow / value("ge_pump_flow")) ** 0.6 * value("ge_install_x") / 1000.0 / vessel_m3
    out_kg = wv * x * cells.mu * fp.HOURS * value("pf_uptime")        # kg per m3 of vessel per year
    replace = area_vessel * cost_m2 / life_y / out_kg                 # $/kg, membranes replaced every life_y
    energy = power * wv * fp.HOURS * value("pf_uptime") / 1000.0 * value("ge_power_price") / out_kg
    return {"x": x, "co2_load": co2, "o2_load": o2, "co2_by_loop": co2_loop, "per_pass": per_pass,
            "ph_rise": dph, "p_out": p_out, "passes": passes, "passes_o2_alone": passes_o2,
            "turnover_min": 60.0 / passes if passes > 0 else float("inf"), "flow_m3h": flow,
            "length_m": length, "velocity": v, "stay_s": length / v, "o2_frac": o2_frac, "o2_share": o2_share,
            "area_m2_m3": area, "area_total": area * wv * vessel_m3, "flux_co2": flux_co2,
            "flux_o2": passes * o2_pass / area * 1000.0 if area > 0 else 0.0,
            "dp_kpa": dp / 1000.0, "power_w_m3": power, "viscosity": mu, "wall_stress_pa": mu * shear,
            "fibres": passes / 3600.0 * wv * vessel_m3 / (v * np.pi * d * d / 4.0),
            "capex_k_m3": capex, "replace_kg": replace, "energy_kg": energy}


def loop_table(densities=(120.0, 150.0, 190.0, 250.0), **kw) -> list:
    return [loop_design(x, **kw) for x in densities]


def submerged_area(x: float, k_liq: float | None = None, o2_bar: float | None = None,
                   p_tank: float | None = None, cells: fp.Cells | None = None) -> dict:
    """Membrane placed IN the tank (tubing or fibre curtains), so no liquid has to be pumped round: the
    area per m3 of culture is the load over the flux, with the stirrer setting the liquid film."""
    k = value("ge_k_submerged") if k_liq is None else k_liq
    o2_bar = value("ge_o2_bar") if o2_bar is None else o2_bar
    p_tank = value("pf_pco2_limit") if p_tank is None else p_tank
    co2, o2 = gas_load(x, cells)
    f_co2 = 1.0 / (1.0 / k + 1.0 / membrane_k("co2")) * value("pf_co2_henry") * (p_tank - value("ge_sweep_pco2")) * 3600.0
    f_o2 = 1.0 / (1.0 / k + 1.0 / membrane_k("o2")) * (value("ge_o2_henry") * o2_bar * 1000.0
                                                         - value("ge_do_setpoint")) * 3600.0
    a_co2, a_o2 = co2 / f_co2, o2 / f_o2                              # mol/m3/h over mol/m2/h
    od = value("ge_tubing_od_mm") * 1e-3
    return {"flux_co2": f_co2 * 1000.0, "flux_o2": f_o2 * 1000.0, "area_co2": a_co2, "area_o2": a_o2,
            "tubing_km_m3": a_o2 / (np.pi * od) / 1000.0, "volume_share": a_o2 * od / 4.0}


def floor_with_loop(x_design: float | None = None, oxygen: bool = False, **case) -> dict:
    """The floor case with a membrane loop taking the CO2 out. The CO2 limit is lifted, so the next
    limit binds (mixing, then oxygen); the loop's capital goes on the plant, and membrane replacement
    and pumping power are added per kg. `case` passes other levers to floor_physics.explore (for
    example gas_velocity=0.002 for cells that tolerate little sparging) and loop settings to loop_design."""
    loop_keys = ("co2_frac", "p_sweep", "bore_mm", "shear", "buffer", "wall_um", "o2_bar", "cost_m2", "life_y")
    loop_kw = {k: case.pop(k) for k in loop_keys if k in case}
    base = fp.explore(**case)
    free_kw = dict(case, x_scale=1e6)                                 # the CO2 limit taken away
    if oxygen:                                                        # ... and the sparger's oxygen limit:
        free_kw["gas_velocity"] = 1.0                                 # mixing (or thickness) then binds
    free = fp.explore(**free_kw)
    cells = fp.Cells(mass_pg=case.get("mass_pg", 3000.0), doubling_h=case.get("doubling_h", 24.0))
    design = loop_design(free["density"] if x_design is None else x_design, oxygen=oxygen,
                         sparge_velocity=0.0 if oxygen else case.get("gas_velocity", value("pf_gas_velocity")),
                         p_tank=case.get("pco2_mbar"), vessel_m3=case.get("vessel_m3", 20.0), cells=cells, **loop_kw)
    charge = case.get("charge", value("plant_charge_mature"))
    capital = charge * design["capex_k_m3"] / free["output"]
    total = free["total"] + capital + design["replace_kg"] + design["energy_kg"]
    return {"base": base["total"], "density": free["density"], "limit": free["limit"], "no_co2_limit": free["total"],
            "loop_capital": capital, "loop_membranes": design["replace_kg"], "loop_energy": design["energy_kg"],
            "total": total, "design": design}


# ----------------------------------------------------------------------------
# 4. Tank shape, with the vessel's cost made to depend on it
# ----------------------------------------------------------------------------
def vessel_geometry(vessel_m3: float, aspect: float) -> dict:
    """An upright cylinder with two dished heads whose liquid, at the working volume, is `aspect` times
    as deep as the tank is wide. Wall thickness is taken proportional to diameter (pressure and vacuum
    design both scale that way), so steel mass ~ diameter x surface."""
    T, depth = fp.tank_shape(vessel_m3, aspect)
    height = depth / value("pf_working_volume")
    surface = np.pi * T * height + 2.0 * value("ge_head_area") * T * T
    return {"T": T, "depth": depth, "height": height, "surface": surface, "steel": T * surface,
            "footprint": (T + value("ge_clearance_m")) ** 2}


def shape_capex_factor(vessel_m3: float, aspect: float) -> dict:
    """How the plant's capital per m3 changes when a tank of the same volume is built to another shape,
    relative to the model's reference shape. Two parts: the vessel shell (steel mass to the power in
    the textbook cost correlation) on the vessel's share of the plant, and the floor it stands on."""
    g, g0 = vessel_geometry(vessel_m3, aspect), vessel_geometry(vessel_m3, value("pf_aspect"))
    shell = (g["steel"] / g0["steel"]) ** value("ge_vessel_cost_exp")
    floor = g["footprint"] / g0["footprint"]
    f = (1.0 + value("pf_bioreactor_capex_share") * (shell - 1.0) + value("ge_hall_share") * (floor - 1.0))
    return {"shell": shell, "floor": floor, "plant": f}


def shape_case(aspect: float, vessel_m3: float = 20.0, cells_in_shell: int = 1, gas_rule: str = "velocity",
               with_vessel_cost: bool = True, **case) -> dict:
    """One tank shape through the floor model.

    `cells_in_shell`  >1 treats a long horizontal vessel as that many stirred, sparged compartments side
                      by side, each with liquid `aspect` times as deep as it is wide: the gas and mixing
                      limits are those of one compartment, the cost that of the whole vessel.
    `gas_rule`        'velocity': the cells tolerate a gas velocity through the liquid surface (the
                      model's reading of Humbird). 'volume': they tolerate a gas flow per litre of
                      culture (vvm), which is what bubble-burst damage models imply. Then the gas a tank
                      may pass falls with its depth and shape no longer changes the CO2 limit."""
    v_cell = vessel_m3 / cells_in_shell
    us = case.pop("gas_velocity", value("pf_gas_velocity"))
    if gas_rule == "volume":                                           # same vvm as the 20 m3 reference tank
        us = us * fp.tank_shape(v_cell, aspect)[1] / fp.tank_shape(20.0, value("pf_aspect"))[1]
    f = shape_capex_factor(v_cell, aspect) if with_vessel_cost else {"shell": 1.0, "floor": 1.0, "plant": 1.0}
    capex_x = f["plant"]
    plant = case.get("plant", "sanitary")
    if cells_in_shell > 1 and fp.PLANT_CLASSES[plant][2]:              # priced as one vessel of the full size
        capex_x *= fp.capex_at_size(1.0, vessel_m3) / fp.capex_at_size(1.0, v_cell)
    r = fp.explore(vessel_m3=v_cell, aspect=aspect, gas_velocity=us, capex_x=capex_x, **case)
    T, depth = fp.tank_shape(v_cell, aspect)
    return {"aspect": aspect, "vessel_m3": vessel_m3, "T": T, "depth": depth, "gas_velocity": us,
            "vvm": us * 60.0 / depth, "density": r["density"], "limit": r["limit"], "total": r["total"],
            "capex_x": capex_x, "shell": f["shell"], "floor": f["floor"]}


def shape_table(aspects=(0.25, 0.5, 0.8, 1.0, 1.3, 1.6, 2.0, 2.5, 3.0), sizes=(5.0, 20.0, 50.0, 200.0), **kw) -> list:
    return [[shape_case(a, v, **kw) for a in aspects] for v in sizes]


def best_shape(vessel_m3: float = 20.0, **kw) -> dict:
    """The liquid depth-to-width ratio that costs least per kg, on a grid from 0.2 to 3."""
    grid = [shape_case(a, vessel_m3, **kw) for a in np.arange(0.2, 3.01, 0.05)]
    return min(grid, key=lambda r: r["total"])


def sparge_death(gas_velocity: float | None = None, depth: float | None = None, protected: bool = True,
                 cells: fp.Cells | None = None) -> dict:
    """Cells killed by bursting bubbles, from the measured rule that the death rate is proportional to
    the gas flow per litre of culture (Tramper 1988, Jobses 1991): k_d = killing volume x (u_s / depth).
    Returns the gas per litre (per hour and as vvm), the death rate per hour and its share of the
    growth rate. Defaults: the model's gas limit in its 20 m3 tank."""
    cells = fp.GOOD_CELLS if cells is None else cells
    us = value("pf_gas_velocity") if gas_velocity is None else gas_velocity
    depth = fp.tank_shape(20.0)[1] if depth is None else depth
    per_h = us / depth * 3600.0
    kd = value("ge_kill_protected" if protected else "ge_kill_unprotected") * per_h
    return {"gas_per_h": per_h, "vvm": per_h / 60.0, "death_per_h": kd, "share_of_growth": kd / cells.mu}


# ----------------------------------------------------------------------------
# 5. A published design against the CO2 balance
# ----------------------------------------------------------------------------
def co2_density_at(depth: float, gas_velocity: float, qo2: float, rq: float | None = None,
                   pco2_mbar: float | None = None) -> float:
    """The model's CO2 balance for any liquid depth (m) and oxygen uptake (mmol/g/h): g wet/L."""
    rq = value("pf_rq") if rq is None else rq
    pco2 = value("pf_pco2_limit") if pco2_mbar is None else pco2_mbar
    carry = pco2 * 100.0 / (R_GAS * T_K)
    return gas_velocity / depth * 3600.0 * carry * value("pf_co2_strip_eff") / (rq * qo2)


def gas_velocity_needed(x: float, depth: float, qo2: float, rq: float | None = None,
                        pco2_mbar: float | None = None) -> float:
    """Gas velocity through the liquid surface (m/s) that carries off the CO2 of x g/L."""
    return x / co2_density_at(depth, 1.0, qo2, rq, pco2_mbar)


def airlift_check(x: float = 100.0, vessel_m3: float | None = None, height: float | None = None,
                  our: float | None = None, rq: float = 1.2, pco2_mbar: float | None = None) -> dict:
    """Negulescu et al. 2023's airlift: 261.8 m3, 80% full, 100 g/L, oxygen uptake 10.3 mmol/L/h, CO2:O2 of
    1.2. The paper gives no dimensions; it builds on Li et al. 2020's 300 m3, 13.75 m design, so the
    height is scaled from that at the same proportions. Returns the gas the CO2 balance asks for and
    the density the model's gas limit allows, with the paper's oxygen uptake and with the model's."""
    vessel_m3 = value("ge_alr_volume") if vessel_m3 is None else vessel_m3
    height = (value("ge_alr_li_height") * (vessel_m3 / value("ge_alr_li_volume")) ** (1.0 / 3.0)
              if height is None else height)
    depth = height * value("pf_working_volume")
    our = value("ge_alr_our") if our is None else our
    out = {"height": height, "depth": depth}
    for tag, q in (("paper", our / x), ("model", fp.GOOD_CELLS.qo2)):
        us = gas_velocity_needed(x, depth, q, rq, pco2_mbar)
        out[tag] = {"qo2": q, "co2_load": rq * q * x, "gas_velocity": us, "vvm": us * 60.0 / depth,
                    "density_at_limit": co2_density_at(depth, value("pf_gas_velocity"), q, rq, pco2_mbar)}
    return out


# ----------------------------------------------------------------------------
def main() -> None:
    us = value("pf_gas_velocity")
    d0 = loop_design(190.0, sparge_velocity=us)
    print("1. MEMBRANE LOOP on a 20 m3 tank (16 m3 of culture)")
    print(f"  one pass: CO2 {value('pf_pco2_limit'):.0f} -> {d0['p_out']:.0f} mbar gives up {d0['per_pass']:.2f} mmol/L (pH +{d0['ph_rise']:.2f}); "
          f"fibres {value('ge_bore_mm')} mm bore, {d0['length_m'] * 100:.0f} cm long, {d0['velocity'] * 100:.1f} cm/s, "
          f"{d0['stay_s']:.1f} s inside; oxygen gets {d0['o2_frac']:.0%} of the way to saturation")
    hdr = (f"{'g/L':>5} {'CO2 by loop':>11} {'passes/h':>9} {'flow m3/h':>10} {'m2 per m3':>10} {'total m2':>9} {'flux':>5} "
           f"{'kPa':>5} {'W/m3':>6} {'$k/m3':>6} {'$/kg':>5}")
    for label, kw in (("A. CO2 only; the sparger stays at 6 mm/s and supplies the oxygen", dict(sparge_velocity=us)),
                      ("B. CO2 only; sparger at pharma practice, 1 mm/s (oxygen from fine bubbles, not modelled)", dict(sparge_velocity=0.001)),
                      ("C. CO2 and all the oxygen through the loop; nothing sparged", dict(oxygen=True)),
                      ("D. as C with oxygen at 2 bar in the fibres", dict(oxygen=True, o2_bar=2.0))):
        print(f"\n  {label}\n  {hdr}")
        for r in loop_table(**kw):
            print(f"  {r['x']:5.0f} {r['co2_by_loop']:11.1f} {r['passes']:9.1f} {r['flow_m3h']:10.0f} {r['area_m2_m3']:10.0f} "
                  f"{r['area_total']:9.0f} {r['flux_co2']:5.0f} {r['dp_kpa']:5.1f} {r['power_w_m3']:6.0f} {r['capex_k_m3']:6.0f} "
                  f"{r['replace_kg'] + r['energy_kg']:5.2f}")
    print("\n  what moves it (case A at 190 g/L): passes/h, m2 per m3 of culture, pH rise in the loop")
    for label, kw in (("as above", {}), ("80% stripped per pass", dict(co2_frac=0.8)), ("buffer 5 mmol/L per pH", dict(buffer=5.0)),
                      ("1 mm bore", dict(bore_mm=1.0)), ("porous wall (no membrane resistance)", dict(wall_um=0.0)),
                      ("3,400 per second shear", dict(shear=3400.0))):
        r = loop_design(190.0, sparge_velocity=us, **kw)
        print(f"    {label:<38} {r['passes']:5.1f} {r['area_m2_m3']:6.0f}  +{r['ph_rise']:.2f}  {r['dp_kpa']:5.1f} kPa  "
              f"{r['length_m'] * 100:4.0f} cm  flux {r['flux_co2']:.0f}")
    s = submerged_area(190.0)
    print(f"  membrane hung in the tank at 190 g/L: {s['area_co2']:.0f} m2/m3 for CO2 (flux {s['flux_co2']:.0f}), {s['area_o2']:.0f} for oxygen "
          f"(flux {s['flux_o2']:.0f}); as 3 mm tubing that is {s['tubing_km_m3']:.0f} km per m3 and {s['volume_share']:.0%} of the tank")
    print("\n  the floor with a loop ($/kg): today -> CO2 limit gone, free -> with the loop paid for")
    for label, kw in (("floor, loop for the CO2 above 120 g/L", dict()),
                      ("  membranes at $40 per m2", dict(cost_m2=40.0)), ("  membranes at $1,480 per m2", dict(cost_m2=1480.0)),
                      ("  membranes last 6 months", dict(life_y=0.5)),
                      ("floor, no sparging at all", dict(oxygen=True)), ("  with oxygen at 2 bar", dict(oxygen=True, o2_bar=2.0)),
                      ("cells that tolerate 2 mm/s of gas, CO2 loop", dict(gas_velocity=0.002)),
                      ("cells that tolerate 2 mm/s, no sparging", dict(gas_velocity=0.002, oxygen=True)),
                      ("fish cells (50 mbar), CO2 loop", dict(pco2_mbar=50.0, mass_pg=2500.0)),
                      ("yeast-style plant, CO2 loop", dict(plant="microbial"))):
        r = floor_with_loop(**kw)
        print(f"    {label:<46} ${r['base']:5.1f} -> ${r['no_co2_limit']:5.1f} -> ${r['total']:5.1f}  at {r['density']:.0f} g/L ({r['limit']}); "
              f"{r['design']['passes']:.0f} passes/h, {r['design']['area_total']:.0f} m2, ${r['design']['capex_k_m3']:.0f}k/m3")
    print("\n2. TANK SHAPE: liquid depth/width, density, $/kg without and with the vessel-cost term; then the per-litre gas rule")
    for v in (20.0, 200.0):
        print(f"  {v:.0f} m3")
        for a in (0.25, 0.5, 0.8, 1.0, 1.3, 1.6, 2.0, 3.0):
            r, r0, rv = shape_case(a, v), shape_case(a, v, with_vessel_cost=False), shape_case(a, v, gas_rule="volume")
            print(f"   {a:4.2f}  width {r['T']:.2f} m depth {r['depth']:.2f} m  {r['density']:4.0f} g/L ({r['limit']:<13}) ${r0['total']:5.1f} -> ${r['total']:5.1f}"
                  f"  shell x{r['shell']:.2f} floor x{r['floor']:.2f} plant x{r['capex_x']:.3f} | {rv['density']:4.0f} g/L ${rv['total']:5.1f}")
        b, bv = best_shape(v), best_shape(v, gas_rule="volume")
        print(f"   cheapest: depth/width {b['aspect']:.2f}, {b['density']:.0f} g/L, ${b['total']:.2f}/kg; per-litre gas rule: {bv['aspect']:.2f}, ${bv['total']:.2f}")
    r = shape_case(0.8, 200.0, cells_in_shell=10)
    print(f"  200 m3 horizontal vessel of ten stirred 20 m3 compartments, liquid 0.8 x as deep as wide: {r['density']:.0f} g/L ({r['limit']}), ${r['total']:.2f}/kg")
    print("  cells killed by bursting bubbles (death rate = killing volume x gas per litre), share of the growth rate:")
    for label, kw in (("floor: 6 mm/s in the 20 m3 tank, 1 g/L protectant", dict()),
                      ("the same with no protectant", dict(protected=False)),
                      ("squat tank (0.8) at 6 mm/s", dict(depth=fp.tank_shape(20.0, 0.8)[1])),
                      ("200 m3 tank at 6 mm/s", dict(depth=fp.tank_shape(200.0)[1]))):
        r = sparge_death(**kw)
        print(f"    {label:<50} {r['vvm']:.3f} vvm  {r['death_per_h']:.4f}/h  {r['share_of_growth']:.0%}")
    print("\n3. AIRLIFT (Negulescu 2023, 262 m3, 100 g/L)")
    a = airlift_check()
    print(f"  height {a['height']:.1f} m, liquid depth {a['depth']:.1f} m")
    for tag in ("paper", "model"):
        r = a[tag]
        print(f"  {tag}'s oxygen uptake ({r['qo2']:.3f} mmol/g/h): CO2 {r['co2_load']:.1f} mmol/L/h needs {r['gas_velocity'] * 1000:.1f} mm/s "
              f"({r['vvm']:.3f} vvm); at 6 mm/s it holds {r['density_at_limit']:.0f} g/L")
    r50 = airlift_check(pco2_mbar=50.0)
    print(f"  at 50 mbar: {r50['paper']['gas_velocity'] * 1000:.1f} / {r50['model']['gas_velocity'] * 1000:.1f} mm/s")


if __name__ == "__main__":
    main()
