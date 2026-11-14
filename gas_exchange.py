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


def suspension_buffer(x: float, medium: float | None = None, beta_i: float | None = None) -> float:
    """Non-bicarbonate buffer of the culture, mmol/L per pH unit per litre of suspension, IF the cells'
    insides take part within a pass (that needs carbonic anhydrase inside the cells, not shown for these
    cells): the medium's own (phosphate) plus the cells' intracellular buffer on their water."""
    medium = value("ge_buffer_medium") if medium is None else medium
    beta_i = value("ge_beta_i") if beta_i is None else beta_i
    return medium + cell_volume_fraction(x) * value("ge_cell_water") * beta_i


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


def acid_side(x: float = 190.0, acid_mm: float = 10.0, sparge_velocity: float | None = None,
              medium_price: float = 0.15, cells: fp.Cells | None = None) -> dict:
    """The acid-side option, as in medical CO2 removal: add `acid_mm` mmol/L of acid to the culture just
    before the fibres, so that much bicarbonate turns into CO2 and can be stripped, then add the same
    amount of base after them so the tank stays at its pH.

    Two versions. (1) Bought acid and base: every pass adds acid_mm of salt (for example NaCl), which the
    perfusion must wash out under the salt limit (pf_osm_limit). (2) Acid and base made from water by
    bipolar electrodialysis in contact with the liquid itself: no salt, but ion-exchange membranes cannot
    take a cell suspension, so the loop's liquid must first be filtered free of cells."""
    cells = fp.GOOD_CELLS if cells is None else cells
    us = value("pf_gas_velocity") if sparge_velocity is None else sparge_velocity
    plain = loop_design(x, sparge_velocity=us, cells=cells)
    frac = value("ge_co2_frac")
    # acid raises the CO2 entering the fibres by acid_mm; a pass strips `frac` of the excess over the sweep
    s = value("pf_co2_henry")
    p_in = value("pf_pco2_limit") + acid_mm / s                       # the acid's CO2 counted as pressure
    per_pass = frac * s * (p_in - value("ge_sweep_pco2"))
    passes = plain["co2_by_loop"] / per_pass
    extra = per_pass - plain["per_pass"]                               # CO2 per pass that came from bicarbonate
    # salt: acid_mm of acid and acid_mm of base added per pass -> acid_mm of salt per pass
    gain = x * cells.mu                                               # g of cells grown per L per h
    salt_per_kg = passes * acid_mm / gain                             # mol of salt per kg of cells
    hco3 = s * value("pf_pco2_limit") * 10.0 ** (value("pf_ph") - value("pf_pk1"))
    room = value("pf_osm_limit") - value("pf_osm_base") - 2.0 * max(0.0, hco3 - value("pf_hco3_base"))   # mOsm
    lac = fp.waste_per_kg(cells)[1]
    litres = 2.0 * (lac + salt_per_kg) / (room / 1000.0)              # L/kg to hold the salt limit
    base_litres = max(value("pf_medium_l_floor"), 2.0 * lac / (room / 1000.0))
    # electrodialysis: protons made per pass = acid_mm; cell-free liquid needed = the whole loop flow
    flow = passes * value("pf_working_volume") * 20.0                 # m3/h through the loop (20 m3 tank)
    ed_kwh_kg = salt_per_kg * value("ge_ed_volt") * 96485.0 / 3.6e6
    filter_m2 = flow * 1000.0 / value("ge_filtrate_flux")
    return {"per_pass": per_pass, "per_pass_plain": plain["per_pass"], "from_bicarbonate": extra,
            "passes": passes, "passes_plain": plain["passes"], "flow_m3h": flow,
            "salt_mol_kg": salt_per_kg, "medium_l": litres, "medium_l_base": base_litres,
            "extra_medium_cost": (litres - base_litres) * medium_price,
            "ed_kwh_kg": ed_kwh_kg, "ed_filter_m2": filter_m2,
            "ed_filter_vs_atf": filter_m2 / value("ge_atf_area")}


# ----------------------------------------------------------------------------
# 3b. The loop without a membrane: a packed (falling-film) stripping column
# ----------------------------------------------------------------------------
def suspension_density(x: float) -> float:
    """kg/m3 of the culture: medium plus cells."""
    phi = cell_volume_fraction(x)
    return 1000.0 * ((1.0 - phi) * value("pf_medium_density") + phi * value("pf_cell_density"))


def packing_film(x: float, liquid_load: float | None = None) -> dict:
    """The culture running as a film over sheet-metal structured packing (Mellapak 250Y type).
    Wetted area: Tsai et al. 2011. Film: Nusselt laminar film along channels at the packing angle.
    Liquid-side coefficient: Rocha, Bravo and Fair 1996 (penetration theory over one corrugation side, with
    the film velocity). `liquid_load` in m3 of culture per m2 of column cross-section per hour."""
    uL = (value("ge_pk_load") if liquid_load is None else liquid_load) / 3600.0       # m/s superficial
    ap, th, S = value("ge_pk_area"), np.radians(value("ge_pk_angle")), value("ge_pk_side")
    rho, mu, g = suspension_density(x), viscosity(x), 9.81
    ae = min(1.0, 1.34 * ((rho / value("ge_surface_tension")) * g ** (1.0 / 3.0) * (uL / ap) ** (4.0 / 3.0)) ** 0.116)
    q = uL / (ae * ap * np.sin(th))                                   # flow along the channel per m of wetted width
    delta = (3.0 * mu * q / (rho * g * np.sin(th))) ** (1.0 / 3.0)    # film thickness
    u = q / delta                                                     # mean film velocity
    kl = {gas: 2.0 * np.sqrt(value("ge_d_co2" if gas == "co2" else "ge_d_o2") * value("ge_pk_ce") * u / (np.pi * S))
          for gas in ("co2", "o2")}
    return {"uL": uL, "ae": ae, "q": q, "film_mm": delta * 1000.0, "u": u, "kl_co2": kl["co2"], "kl_o2": kl["o2"],
            "htu_co2": uL / (kl["co2"] * ae * ap), "htu_o2": uL / (kl["o2"] * ae * ap),
            "holdup": delta * ae * ap, "wall_shear_pa": rho * g * np.sin(th) * delta,
            "shear_rate": 3.0 * u / delta, "viscosity": mu}


def column_cost(area: float, height: float) -> float:
    """Purchased cost ($, today's prices) of a stainless packed column: packing, shell and internals, from the
    vendor-quote fits in Wang's 2015 thesis (Table 6.4 and Eq. 6-6, 2014 dollars): packing 7.31 a_p + 203 $/m3;
    shell 575 W^0.609 (W in lb of stainless); liquid distributor 15,355 D^0.1764, its supports 5/6 of that,
    support grid 12,019 D^0.1792 (D in m). Escalated by the plant-cost index."""
    d = np.sqrt(4.0 * area / np.pi)
    h = height + value("ge_col_extra_height")
    steel = (np.pi * d * h + 2.0 * value("ge_head_area") * d * d) * value("ge_col_wall") * 8000.0 / 0.4536   # lb
    packing = area * height * (7.31 * value("ge_pk_area") + 203.05)
    internals = 15355.0 * d ** 0.1764 * (1.0 + 5.0 / 6.0) + 12019.0 * d ** 0.1792
    return (packing + 575.0 * steel ** 0.609 + internals) * value("ge_cepci_2014")


def column_stresses(x: float = 189.0, drop_height: float = 0.05, drop_mm: float = 4.0, liquid_load: float | None = None,
                    vessel_m3: float = 20.0, p_top_barg: float = 1.0) -> dict:
    """What a cell meets on the packed column and in a pressurised tank, as numbers to set against measured
    damage thresholds (section 8 of the note).

    Film: in a laminar falling film the shear rate falls linearly from the wall to the free surface, so the
    energy dissipated per volume is mu * gamma^2: at most mu * gamma_w^2 at the wall, a third of that on
    average. Re-forming of the film where packing sheets cross: of order u^3 / delta per kg (an estimate).
    Drips from the distributor: a drop falling `drop_height` hits at v = sqrt(2 g h) and its energy is spent
    within about one drop size, so of order v^3 / d per kg (an estimate, not a simulation).
    Pressure: the absolute pressure at the top and bottom of the liquid, today and with `p_top_barg`."""
    f = packing_film(x, liquid_load)
    rho, mu = suspension_density(x), f["viscosity"]
    gw = f["shear_rate"]
    v = np.sqrt(2.0 * 9.81 * drop_height)
    _T, depth = fp.tank_shape(vessel_m3)
    head = rho * 9.81 * depth / 1e5
    p0 = value("ge_p_top_base")
    return {"wall_shear_pa": mu * gw, "shear_rate": gw,
            "film_dissipation_max": mu * gw ** 2, "film_dissipation_mean": mu * gw ** 2 / 3.0,   # W/m3
            "junction_dissipation": rho * f["u"] ** 3 / (f["film_mm"] / 1000.0),                 # W/m3
            "drop_speed": v, "drop_dissipation": rho * v ** 3 / (drop_mm / 1000.0),              # W/m3
            "surface_renewal_s": value("ge_pk_side") / f["u"],
            "p_bottom_today": 1.01325 + p0 + head, "p_top_new": 1.01325 + p_top_barg,
            "p_bottom_new": 1.01325 + p_top_barg + head}


def loop_ph_exposure(p_out: float | None = None, loop_volume: float | None = None, buffer: float | None = None,
                     vessel_m3: float = 20.0) -> dict:
    """How much of the culture is alkaline at any moment, and by how much. Liquid that leaves the column at
    p_out has lost CO2 and is alkaline until it re-mixes with the tank; that is its whole time in the loop
    (packing, sump, return pipe), so the share of the culture exposed is the loop's liquid volume over the
    tank's, whatever the flow. Compared with the one quantified case found: Paul et al. 2020, CHO, alkaline
    zone of about 7.5% of the volume at +0.37 pH, which cut peak cell density by 18-52%."""
    p_out = value("ge_col_pout") if p_out is None else p_out
    vol = value("ge_loop_volume") if loop_volume is None else loop_volume
    _amount, dph = co2_per_pass(value("pf_pco2_limit"), p_out, buffer)
    share = vol / (value("pf_working_volume") * vessel_m3)
    dose = dph * share
    paul = value("ge_paul_dph") * value("ge_paul_share")
    return {"ph_rise": dph, "share": share, "dose": dose, "paul_dose": paul, "vs_paul": dose / paul}


def drop_height_for(dissipation: float, drop_mm: float = 4.0) -> float:
    """Fall height (m) at which a drop's impact dissipates `dissipation` W/m3 (the v^3/d estimate)."""
    v = (dissipation / 1000.0 * drop_mm / 1000.0) ** (1.0 / 3.0)
    return v * v / (2.0 * 9.81)


def o2_supply_sparger(x: float, gas_velocity: float, p_top_barg: float | None = None, vessel_m3: float = 20.0,
                      aspect: float | None = None) -> float:
    """Oxygen the sparger delivers, mmol/L/h: the model's cap scaled by gas flow (kLa ~ u_s^0.8) and by the
    headspace pressure (`headspace_pressure`)."""
    f = headspace_pressure(p_top_barg, vessel_m3, aspect)["otr_factor"] if p_top_barg is not None else 1.0
    return value("pf_otr_cap") * (gas_velocity / value("pf_gas_velocity")) ** 0.8 * f


def column_design(x: float, sparge_velocity: float | None = None, p_out: float | None = None,
                  oxygen: bool = False, sweep: str = "air", liquid_load: float | None = None,
                  p_top_barg: float | None = None, buffer: float | None = None, vessel_m3: float = 20.0,
                  aspect: float | None = None, cells: fp.Cells | None = None) -> dict:
    """Size a packed stripping column on a pumped loop for a tank at density x (g wet/L).

    The culture is pumped to the top of the column, runs down the packing as a film against a sweep gas
    flowing up, and drains back to the tank. CO2 leaves as dissolved gas only (the alkalinity argument
    of section 1.2 holds whatever the contactor), from p_tank to `p_out` mbar. Bicarbonate's slow
    reaction (seconds) does not matter without a buffer, because only dissolved CO2 can leave.
    `oxygen`: the loop must also make up whatever oxygen the sparger does not supply, from a sweep of
    air or of oxygen ('o2_open': once through and vented; 'o2_closed': recycled through a lime scrubber
    that takes the CO2 out)."""
    cells = fp.GOOD_CELLS if cells is None else cells
    us = value("pf_gas_velocity") if sparge_velocity is None else sparge_velocity
    p_tank = value("pf_pco2_limit")
    p_out = value("ge_col_pout") if p_out is None else p_out
    wv = value("pf_working_volume")
    co2, o2 = gas_load(x, cells)
    _T, depth = fp.tank_shape(vessel_m3, aspect)
    by_sparge = us / depth * 3600.0 * (p_tank * 100.0 / (R_GAS * T_K)) * value("pf_co2_strip_eff")
    co2_loop = max(0.0, co2 - by_sparge)
    o2_short = max(0.0, o2 - o2_supply_sparger(x, us, p_top_barg, vessel_m3, aspect)) if oxygen else 0.0

    film = packing_film(x, liquid_load)
    # counter-current: fresh sweep (ge_col_gas_in) meets the culture leaving at the bottom; the sweep leaves
    # the top at ge_col_gas_out against culture arriving at p_tank. Log-mean driving force.
    d1, d2 = p_tank - value("ge_col_gas_out"), p_out - value("ge_col_gas_in")
    ntu = (p_tank - p_out) / ((d1 - d2) / np.log(d1 / d2) if abs(d1 - d2) > 1e-9 else d1)
    height = ntu * film["htu_co2"]
    per_pass, dph = co2_per_pass(p_tank, p_out, buffer)
    o2_frac = 1.0 - np.exp(-height / film["htu_o2"])
    y_o2 = 0.21 if sweep == "air" else value("ge_o2_sweep_purity")
    o2_pass = o2_frac * (value("ge_o2_henry") * y_o2 * 1013.0 - value("ge_do_setpoint"))
    passes_co2 = co2_loop / per_pass
    passes_o2 = o2_short / o2_pass if o2_pass > 0 else 0.0
    passes = max(passes_co2, passes_o2)
    flow = passes * wv * vessel_m3                                    # m3/h through the column
    area = flow / (film["uL"] * 3600.0)                               # m2 of cross-section
    co2_removed = passes * per_pass * wv * vessel_m3                  # mol/h (mmol/L x m3)
    o2_given = passes * o2_pass * wv * vessel_m3                      # mol/h
    # sweep gas: enough that its CO2 leaves at ge_col_gas_out mbar
    gas_mol = co2_removed / ((value("ge_col_gas_out") - value("ge_col_gas_in")) / 1013.0)   # mol/h
    gas_m3h = gas_mol * R_GAS * T_K / 101325.0
    gas_u = gas_m3h / 3600.0 / area if area > 0 else 0.0
    f_factor = gas_u * np.sqrt(1.2)
    head = height + value("ge_col_head_extra")
    power = suspension_density(x) * 9.81 * head * flow / 3600.0 / value("ge_pump_eff")      # W
    stay = film["holdup"] * height / film["uL"]                       # s on the packing
    # money: packing, shell and distributor, pump; installed
    capex = (column_cost(area, height) + value("ge_pump_cost") * (flow / value("ge_pump_flow")) ** 0.6) * value("ge_install_x")
    capex_k_m3 = capex / 1000.0 / vessel_m3
    out_kg = wv * x * cells.mu * fp.HOURS * value("pf_uptime")        # kg per m3 of vessel per year
    hours = fp.HOURS * value("pf_uptime")
    energy = power * hours / 1000.0 * value("ge_power_price") / vessel_m3 / out_kg
    gas_cost = 0.0
    if sweep == "o2_open":
        gas_cost = gas_mol * 0.032 * hours * value("ge_o2_price") / vessel_m3 / out_kg
    elif sweep == "o2_closed":                                        # make-up = oxygen given + lime for the CO2
        gas_cost = (o2_given * 0.032 * value("ge_o2_price") + co2_removed * 0.074 * value("ge_lime_price")
                    / value("ge_lime_use")) * hours / vessel_m3 / out_kg
    return {"x": x, "co2_by_loop": co2_loop, "o2_short": o2_short, "per_pass": per_pass, "ph_rise": dph,
            "ntu": ntu, "height_m": height, "o2_frac": o2_frac, "o2_pass": o2_pass,
            "passes": passes, "passes_co2": passes_co2, "passes_o2": passes_o2, "flow_m3h": flow,
            "area_m2": area, "diameter_m": np.sqrt(4.0 * area / np.pi), "stay_s": stay,
            "gas_m3h": gas_m3h, "gas_velocity": gas_u, "f_factor": f_factor, "head_m": head,
            "power_w_m3": power / (wv * vessel_m3), "capex_k_m3": capex_k_m3, "energy_kg": energy,
            "gas_kg": gas_cost, "o2_mmol_l_h": o2_given / (wv * vessel_m3), **film}


def headspace_pressure(p_top_barg: float | None = None, vessel_m3: float = 20.0, aspect: float | None = None) -> dict:
    """Oxygen transfer with the tank's headspace held at a higher pressure. Oxygen in the gas dissolves in
    proportion to its partial pressure, so the driving force C* - C rises with the (mean) pressure in the
    liquid. The model's 29 mmol/L/h (pf_otr_cap) is taken as Humbird's: 90% oxygen with the top at
    pf ge_p_top_base bar gauge; the dissolved-oxygen level that makes it consistent with his kLa is solved
    for and held fixed. CO2 is not affected: at a fixed gas velocity at the top the gas carries the same
    CO2 per unit volume (pCO2 / RT), whatever the pressure."""
    p0 = value("ge_p_top_base") if p_top_barg is None else p_top_barg
    _T, depth = fp.tank_shape(vessel_m3, aspect)
    rho_gh = 1007.0 * 9.81 * depth / 1e5 / 2.0                        # bar: half the hydrostatic head
    c_star = lambda p: value("ge_o2_henry") * value("ge_sparge_o2") * (1.01325 + p + rho_gh) * 1000.0
    kla = value("pf_otr_cap") / (c_star(value("ge_p_top_base")) - 0.0)   # first pass, to get C_L
    c_l = c_star(value("ge_p_top_base")) - value("pf_otr_cap") / value("ge_kla_20m3")
    f = (c_star(p0) - c_l) / (c_star(value("ge_p_top_base")) - c_l)
    return {"p_top_barg": p0, "c_star": c_star(p0), "c_star_base": c_star(value("ge_p_top_base")),
            "c_liquid_implied": c_l, "otr_factor": f, "otr": value("pf_otr_cap") * f,
            "x_o2": value("pf_otr_cap") * f / fp.GOOD_CELLS.qo2, "kla_unused": kla}


def loop_mixing(x: float, passes: float, nozzle_velocity: float | None = None, vessel_m3: float = 20.0) -> dict:
    """Does the loop's return flow help the tank mix? Compares the loop's turnover time with the model's
    mixing time (141 s at 20 m3, Humbird Eq. 2.18), and adds the return jet's power to the stirrer's: mixing
    time goes as (power per volume)^(-1/3) in the same equation. Also the oxygen check that the model's
    mixing rule stands for: the culture uses qO2 X x t_m of oxygen in one mixing time, which the dissolved
    oxygen must cover."""
    v = value("ge_nozzle_velocity") if nozzle_velocity is None else nozzle_velocity
    culture = value("pf_working_volume") * vessel_m3
    q = passes * culture / 3600.0                                     # m3/s
    p_jet = 0.5 * 1000.0 * v ** 2 * q / culture                       # W/m3
    t_m = value("ge_mix_time_20m3") * fp.mixing_time_ratio(vessel_m3)
    mix_x = ((value("ge_stir_power") + p_jet) / value("ge_stir_power")) ** (1.0 / 3.0)
    use = fp.GOOD_CELLS.qo2 * x * t_m / 3600.0                        # mmol/L used in one mixing time
    return {"turnover_s": 3600.0 / passes if passes > 0 else float("inf"), "mix_time_s": t_m,
            "jet_w_m3": p_jet, "mix_x": mix_x, "o2_used_in_mix_time": use}


def floor_with_column(sparge_velocity: float | None = None, oxygen: bool = False, sweep: str = "air",
                      p_top_barg: float | None = None, p_out: float | None = None, **case) -> dict:
    """The floor with a packed-column loop and optionally headspace pressure, through floor_physics.explore's
    `column` and `p_top_barg` levers (one path for Python and the page). `oxygen` with sweep "o2_closed" is
    explore's column="o2_closed"; otherwise column="co2". Returns the floor before and after."""
    us = value("pf_gas_velocity") if sparge_velocity is None else sparge_velocity
    column = "o2_closed" if (oxygen and sweep == "o2_closed") else "co2"
    if oxygen and sweep != "o2_closed":
        raise ValueError("explore's column carries oxygen only with the recycled oxygen sweep ('o2_closed')")
    base = fp.explore(gas_velocity=us, **case)
    r = fp.explore(gas_velocity=us, column=column, p_top_barg=p_top_barg, col_pout=p_out, **case)
    d = r["column"]
    return {"base": base["total"], "density": r["density"], "limit": r["limit"], "total": r["total"],
            "capital": r["capital"], "energy": d["energy_kg"], "gas": d["gas_kg"], "design": d, "result": r}


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
# 6. Named cases: what the cells are like x what the tank has (RESULTS.md tables)
# ----------------------------------------------------------------------------
# explore() arguments. Sources: research_notes/waste_tricks_sizing.md (Hubalek 2023, bovine fibro-adipogenic
# progenitors, full text; Pasitka 2024 chicken lactate yield, snippet), and the floor's own assumptions.
CELL_CASES = {
    "floor": ("the floor's assumption (Humbird's enhanced cells)", {}),
    "best_meat": ("best shown in meat cells (bovine, glutamine replaced)",
                  {"doubling_h": 42.9, "nh3_kg": 0.14, "lac_yield": 1.05, "glc_kg": 0.84}),
    "ordinary": ("ordinary meat cells (bovine, with glutamine)",
                 {"doubling_h": 25.7, "nh3_kg": 0.70, "lac_yield": 1.05, "glc_kg": 0.84}),
}
TANK_CASES = {
    "sparger": ("sparger only", {}),
    "column": ("packed column on a loop", {"column": "co2", "col_pout": 55.0}),
    "all": ("column with oxygen sweep, 1 bar gauge", {"column": "o2_closed", "col_pout": 55.0, "p_top_barg": 1.0}),
}
LOSS_RATES = {"sanitary": (0.0, 0.002), "microbial": (0.0, 0.006, 0.022)}   # chance of losing a run per day


def cases_table(plant: str = "sanitary", hazard: float = 0.0, restart_days: float = 14.0, **extra) -> list:
    """[(cell label, tank label, $/kg, g/L, binding limit, L/kg, what sets the litres)] for the 3 x 3 grid."""
    rows = []
    for _ck, (clab, ckw) in CELL_CASES.items():
        for _tk, (tlab, tkw) in TANK_CASES.items():
            kw = dict(plant=plant, **ckw, **tkw, **extra)
            if hazard > 0:
                kw.update(hazard=hazard, restart_fail_days=restart_days)
            r = fp.explore(**kw)
            rows.append((clab, tlab, r["total"], r["density"], r["limit"], r["medium_l"], r["medium_set_by"]))
    return rows


def cheapest_tricks(sparge_cap: float, plant: str = "sanitary", aspects=(0.5, 0.75, 1.0, 1.3, 1.6, 2.0),
                    pressures=(None, 0.5, 1.0), columns=("none", "co2", "o2_closed"), **cells) -> dict:
    """The cheapest combination of tank shape, column and headspace pressure when the cells tolerate at most
    `sparge_cap` m/s of gas. The sparger runs at the cap (gas is not priced here); a squatter tank pays for its
    extra steel and floor (shape_capex_factor); the column takes whatever CO2 (and, with an oxygen sweep,
    oxygen) the sparger cannot."""
    best = None
    for a in aspects:
        cx = shape_capex_factor(20.0, a)["plant"]
        for p in pressures:
            for c in columns:
                kw = dict(plant=plant, gas_velocity=sparge_cap, aspect=a, capex_x=cx, p_top_barg=p, column=c, **cells)
                if c != "none":
                    kw["col_pout"] = 55.0
                r = fp.explore(**kw)
                if best is None or r["total"] < best["total"]:
                    best = dict(r, aspect=a, p_top_barg=p, column_mode=c)
    return best


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
    print("\n4. CELLS x TANK ($/kg, g/L, what binds)")
    for plant, rates in LOSS_RATES.items():
        for hz in rates:
            print(f"  {plant}, runs lost {hz * 100:.1f}% a day")
            for row in cases_table(plant, hz):
                print(f"    {row[0]:<52} {row[1]:<40} ${row[2]:6.2f} {row[3]:4.0f} g/L {row[4]:<25} {row[5]:5.1f} L/kg ({row[6]})")
    print("\n5. CHEAPEST COMBINATION BY GAS CAP")
    for cap in (0.001, 0.002, 0.004, 0.006):
        for plant in ("sanitary", "microbial"):
            b = cheapest_tricks(cap, plant)
            print(f"  {cap * 1000:.0f} mm/s {plant:<10} ${b['total']:5.2f}  depth/width {b['aspect']}  column {b['column_mode']}  "
                  f"pressure {b['p_top_barg']}  {b['density']:.0f} g/L ({b['limit']})  sparger only ${fp.explore(gas_velocity=cap, plant=plant)['total']:.2f}")
    r50 = airlift_check(pco2_mbar=50.0)
    print(f"  at 50 mbar: {r50['paper']['gas_velocity'] * 1000:.1f} / {r50['model']['gas_velocity'] * 1000:.1f} mm/s")


if __name__ == "__main__":
    main()
