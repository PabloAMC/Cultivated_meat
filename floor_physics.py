#!/usr/bin/env python3
"""
floor_physics.py — side-study to Rung 2: a physics-based floor for the cost of cultivated
cells, by reactor type and plant class.  (NOT used in the headline cost.)

Why
---
This module builds the floor's plant term from physics
and published engineering, per kg of REAL wet cells (70% water, ~21% protein: Humbird's
basis, comparable with meat), and shows how far creative options could push it.

The chain of reasoning
----------------------
1. A cell burns energy at a rate set by its size (West's 3/4-power law, Humbird Eq. 2.8),
   and that energy needs oxygen:

       power per cell      P = 0.148 * M^0.75                 [pW, M in pg]
       oxygen uptake    qO2 = P / (heat per mol O2) / M       [mmol O2 per g wet per h]

2. A reactor can only deliver so much oxygen (OTR cap). Bubbles kill animal cells, so the
   cap is far below a microbial fermenter's. That limits the cell density:

       X_O2 = OTR / qO2            and never above the viscosity limit X_visc (258 g/L)

   If waste is not washed out (fed-batch, fill-and-draw, chemostat), ammonia and CO2 cap
   the density lower still (X_unperfused, 120 g/L for efficient cells in 20 m3).

3. Output per m3 of vessel per year follows from density and growth rate mu = ln2 / t_d:

       perfusion (cells retained):    wv * X * mu * 8760 * uptime
       fill-and-draw (no retention):  wv * X * mu * f/ln(1/(1-f)) * 8760 * uptime
       fed-batch:                     wv * X / (n * t_d + turnaround) * 8760

   In fill-and-draw a fraction f of the tank is drained each cycle and the culture must climb
   back to the cap, so it averages 72% of (cap x maximum growth rate) at f = 0.5. An earlier
   version of this module took the cap and the maximum growth rate at once; no way of running
   a tank without cell retention delivers that.

4. The plant's yearly cost is a fixed share of its capital (capital charge 14.6% + maintenance
   4% + insurance 5% = 23.6%, Humbird), so

       plant capital per kg = 0.236 * (capital per m3) / (output per m3 per year)

   plus labour (scaled with vessel-time per kg), utilities and consumables.

5. Capital per m3 depends on the CLASS of plant far more than on anything else:
       sterile stirred tanks with ATF perfusion at 2 m3   $3,450k/m3   (Humbird, 2018 prices)
       sterile stirred tanks with clean rooms, 20 m3        $683k/m3   (Humbird, 2018 prices)
       the same with a sanitary hall, no clean room         $611k/m3   (derived from his Tables 3.2, 4.2)
       microbial fermentation plants as built               $190k/m3   (pf-tea evidence, 2024)
   Humbird's figures are escalated to today's prices in the tiers (x1.33 on capital by the
   plant-cost index, x1.28 on running costs by consumer prices).
   Dropping the clean room saves only about 11%: Humbird's vessels are already priced
   without pharma compliance. Whether animal cells can ever be grown in the last class is
   the open question that decides whether price parity is reachable.

The module reproduces Humbird's two designs (tests/test_floor_physics.py) and then prices a
ladder of tiers, from "as engineered" to "physics limit". Each tier says what it assumes
and whether anyone has demonstrated it.

Run
---
    python floor_physics.py                # the tier table + figure
    python floor_physics.py --no-latex --formats png
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace

import numpy as np
import matplotlib.pyplot as plt

from common import setup_style, _save
from inputs import value, AA_FLOOR, GLUCOSE_FLOOR
from cost_model import CostParams, parity_cost

LN2 = float(np.log(2.0))
HOURS = 8760.0


# ----------------------------------------------------------------------------
# Physics
# ----------------------------------------------------------------------------
@dataclass
class Cells:
    mass_pg: float = value("pf_cell_mass_pg")      # wet mass per cell
    doubling_h: float = value("pf_doubling_h")     # doubling time
    maintenance_share: float = value("pf_maintenance_share")   # share of O2 uptake at 24 h that is upkeep

    @property
    def mu(self) -> float:                          # 1/h
        return LN2 / self.doubling_h

    @property
    def power_pw(self) -> float:                    # metabolic power per cell, pW
        return value("pf_power_coef") * self.mass_pg ** 0.75

    @property
    def qo2(self) -> float:
        """Oxygen uptake, mmol O2 per g wet cells per hour. West's law gives it for a cell doubling
        every 24 h; a share of that is upkeep and the rest scales with the growth rate (the energy of
        growth itself), so faster cells respire more per hour and slower ones less."""
        j_per_h = self.power_pw * 1e-12 * 3600.0                     # J per cell per hour
        mol_per_h = j_per_h / (value("pf_heat_per_o2") * 1e3)        # mol O2 per cell per hour
        q24 = mol_per_h / (self.mass_pg * 1e-12) * 1e3               # per gram, in mmol, at 24 h
        m = self.maintenance_share
        return q24 * (m + (1.0 - m) * self.mu / (LN2 / value("pf_doubling_h")))

    @property
    def o2_per_kg(self) -> float:
        """Oxygen burned per kg of cells grown, kg O2 per kg wet (qO2 / mu): the upkeep part grows
        with the time a kg takes to make, the growth part does not. Slower or smaller cells burn more."""
        return self.qo2 / self.mu * 32.0 / 1000.0


GOOD_CELLS = Cells()
PASITKA_CELLS = Cells(mass_pg=value("pf_cell_mass_small_pg"), doubling_h=value("pf_doubling_slow_h"))


def _per_cell_load(cells: Cells) -> float:
    """CO2 and waste made per gram of cells per hour, relative to the model cell. Both follow oxygen
    uptake, so the densities Humbird derives for his 3 ng cell fall in proportion for cells that
    respire more per gram."""
    return cells.qo2 / GOOD_CELLS.qo2


def waste_cap(cells: Cells) -> float:
    """Density (g/L) at which waste stops a culture that is not washed out (efficient cells)."""
    return value("pf_x_unperfused") / _per_cell_load(cells)


def co2_cap(cells: Cells) -> float:
    """Density (g/L) a 20 m3 tank can hold in perfusion before CO2 removal limits it."""
    return value("pf_x_co2_20m3") / _per_cell_load(cells)


def tank_shape(vessel_m3: float, aspect: float | None = None) -> tuple:
    """(diameter T, liquid depth H_L) in metres of a tank filled to its working volume, for a liquid
    depth-to-diameter ratio `aspect`."""
    aspect = value("pf_aspect") if aspect is None else aspect
    T = (4.0 * value("pf_working_volume") * vessel_m3 / (np.pi * aspect)) ** (1.0 / 3.0)
    return T, aspect * T


def co2_limited_density(cells: Cells, vessel_m3: float = 20.0, pco2_mbar: float | None = None,
                        gas_velocity: float | None = None, aspect: float | None = None) -> float:
    """Density (g wet/L) at which the cells make CO2 as fast as the sparge gas can carry it off.
    Removal = (gas velocity / liquid depth) x (pCO2 / RT) x how close the exhaust comes to equilibrium;
    production = RQ x oxygen uptake per gram. Reproduces Humbird's Fig. 2.8b (see pf_co2_strip_eff)."""
    pco2 = value("pf_pco2_limit") if pco2_mbar is None else pco2_mbar
    us = value("pf_gas_velocity") if gas_velocity is None else gas_velocity
    _T, depth = tank_shape(vessel_m3, aspect)
    carry = pco2 * 100.0 / (8.314 * 310.15)                    # mol CO2 per m3 of gas at the limit
    removal = us / depth * 3600.0 * carry * value("pf_co2_strip_eff")   # mol per m3 of liquid per hour = mmol/L/h
    return removal / (value("pf_rq") * cells.qo2)


def mixing_time_ratio(vessel_m3: float, aspect: float | None = None) -> float:
    """Mixing time relative to the reference 20 m3 tank (Humbird Eq. 2.18 at fixed stirring power):
    t_m ~ T^(2/3) x (H_L/T)^2.5."""
    T, _d = tank_shape(vessel_m3, aspect)
    T0, _d0 = tank_shape(20.0, value("pf_aspect"))
    a = value("pf_aspect") if aspect is None else aspect
    return (T / T0) ** (2.0 / 3.0) * (a / value("pf_aspect")) ** 2.5


def density(cells: Cells, otr: float, washed: bool) -> float:
    """Highest cell density (g wet/L) the reactor supports: oxygen, viscosity and, if waste is not
    washed out, the ammonia/CO2 limit."""
    x = min(value("pf_x_visc"), otr / cells.qo2)
    return x if washed else min(x, waste_cap(cells))


def output_per_m3(cells: Cells, mode: str, otr: float | None = None, uptime: float | None = None,
                  x_cap: float | None = None) -> float:
    """Tonnes of wet cells per m3 of production vessel per year.

    mode 'fedbatch'   fill, grow two doublings, empty, clean (Humbird's fed-batch design).
    mode 'filldraw'   never emptied: a fraction f is drained and refilled each cycle, no cell retention.
                      The culture climbs back to the cap each cycle, so average output is
                      f / ln(1/(1-f)) of (cap x maximum growth rate): 0.72 at f = 0.5.
    mode 'perfusion'  cells retained and waste washed out, so the culture sits at its oxygen-limited
                      density and the harvest is a steady bleed at the growth rate.
    `uptime` is the share of the year the tank produces (not used by 'fedbatch', whose cycle already
    includes its turnaround)."""
    otr = value("pf_otr_cap") if otr is None else otr
    uptime = value("pf_uptime_realistic") if uptime is None else uptime
    wv = value("pf_working_volume")
    if mode == "fedbatch":
        x = density(cells, otr, washed=False) if x_cap is None else x_cap
        cycle = value("pf_fedbatch_doublings") * cells.doubling_h + value("pf_turnaround_h")
        return wv * x / cycle * HOURS / 1000.0
    if mode == "filldraw":
        x = density(cells, otr, washed=False) if x_cap is None else min(x_cap, density(cells, otr, washed=False))
        f = value("pf_draw_fraction")
        return wv * x * cells.mu * f / np.log(1.0 / (1.0 - f)) * HOURS * uptime / 1000.0
    if mode == "perfusion":
        x = density(cells, otr, washed=True) if x_cap is None else min(x_cap, density(cells, otr, washed=True))
        return wv * x * cells.mu * HOURS * uptime / 1000.0
    raise ValueError(f"unknown mode {mode!r}")


def capex_at_size(capex_20m3: float, vessel_m3: float) -> float:
    """Scale an aseptic plant's capital per m3 from 20 m3 vessels to another size. Only the
    bioreactor share scales, with Humbird's packaged-vessel cost (Eq. 3.1: $k = 30.7 V + 800)."""
    per_m3 = lambda v: (30.7 * v + 800.0) / v
    share = value("pf_bioreactor_capex_share")
    return capex_20m3 * ((1.0 - share) + share * per_m3(vessel_m3) / per_m3(20.0))


def plant_cost(cells: Cells, mode: str, capex_k_per_m3: float, consumables: float,
               otr: float | None = None, capex_x: float = 1.0, opex_x: float = 1.0,
               uptime: float | None = None, x_cap: float | None = None,
               labour: float | None = None, escalate_consumables: bool = True) -> dict:
    """Plant cost per kg of wet cells: the yearly charge on capital, labour, utilities, consumables.
    capex_x / opex_x escalate Humbird's 2018 prices to today's (1.0 = as published, used to check the
    module against his tables)."""
    out = output_per_m3(cells, mode, otr, uptime, x_cap)                    # t per m3 per year
    capital = value("humbird_plant_charge") * capex_k_per_m3 * capex_x / out   # $k/t = $/kg
    ref = output_per_m3(GOOD_CELLS, "fedbatch")                             # Humbird's fed-batch plant
    # same crew per m3 of vessel, unless the design states its own labour (Humbird's perfusion plant
    # has many small tanks and more staff per m3)
    labour = (value("pf_labour") * ref / out if labour is None else labour) * opex_x
    utilities = value("pf_utilities") * opex_x
    consumables = consumables * (opex_x if escalate_consumables else 1.0)
    return {"output": out, "capital": capital, "labour": labour,
            "utilities": utilities, "consumables": consumables,
            "plant": capital + labour + utilities + consumables}


def feedstock(cells: Cells, cheap: bool = False) -> float:
    """What the cells must eat, $/kg wet: amino acids (stoichiometric), glucose (half of it burned
    for maintenance, so it scales with oxygen per kg), salts and vitamins."""
    aa = value("aa_intensity") * (value("pf_aa_price_cheap") if cheap else value("aa_bulk_price"))
    burn = cells.o2_per_kg / GOOD_CELLS.o2_per_kg                           # maintenance relative to the model cell
    glucose = GLUCOSE_FLOOR * (0.5 + 0.5 * burn)
    other = value("pf_other_nutrients_cheap") if cheap else value("other_nutrients_floor")
    return aa + glucose + other


# ----------------------------------------------------------------------------
# Build your own case (the page's lever controls call the JS mirror of this)
# ----------------------------------------------------------------------------
PLANT_CLASSES = {                      # key: (capital input, escalate from Humbird's 2018 prices?, scale with vessel size?)
    "pharma":    ("pf_capex_aseptic_fedbatch", True, True),
    "sanitary":  ("pf_capex_no_cleanroom", True, True),
    "microbial": ("pf_capex_fermentation", False, False),   # built plants with 150 m3 vessels: taken as quoted
}


# Species presets for the cell levers. (label, doubling time h, wet mass pg, litres of medium per kg if
# reported, what the numbers are and how good they are). Sources and access levels: research_notes/species_cell_parameters.md.
SPECIES_PRESETS = {
    "model": ("Humbird's model cell", 24.0, 3000.0, None,
              "The efficient cell every case on this page assumes [2]. No meat cell line has been shown to match it."),
    "chicken": ("Chicken, as reported in perfusion", 48.0, 1400.0, 30.5,
                "SuperMeat's 2024 report [1]: half a doubling a day in perfusion, 1.0 to 1.75 ng per cell, 30.5 "
                "litres of medium per kilo (the waste lever is set to match; put the medium price at $0.50 for the reported "
                "cost). Chicken "
                "fibroblasts double in about 20 hours when grown on a surface; another measured run in "
                "animal-free medium took 61 hours [20]."),
    "cattle": ("Cattle, serum-free", 39.0, 3000.0, None,
               "Primary bovine muscle stem cells in serum-free medium on a surface: 39 hours on average "
               "(Stout et al. 2022). Engineered lines reach 15 to 17 hours with serum. No cell mass was found, so the "
               "model cell's is used. No suspension culture at density has been published."),
    "fish": ("Fish (Atlantic mackerel)", 24.0, 2500.0, None,
             "The Mack1 line: 24 hours at 27 °C, 16.8 µm across, grown on a surface with 20% serum (Saad et al. "
             "2023). Many fish lines take two days or more. No measurement shows that fish cells need less oxygen "
             "per gram, so none is assumed."),
    "insect": ("Insect (Sf9), for reference", 23.0, 2200.0, None,
               "Sf9 cells: about 23 hours at 27 °C, grown in suspension in tanks up to 21,000 litres for vaccines "
               "(Ashizawa et al. 2022). Measured oxygen uptake per gram is close to the model's."),
}
SPECIES_MISSING = ("Shrimp and other crustaceans are missing because no cell line that keeps dividing exists for "
                   "them (reviews of 2024 and 2025).")


def waste_per_kg(cells: Cells, waste: float = 0.0) -> tuple:
    """(ammonia, lactate) made per kg of cells grown, mol/kg wet. `waste` runs from 0 (Humbird's enhanced
    cells) to 1 (ordinary wild-type cells). Both come from catabolism, so they scale with the oxygen
    burned per kg relative to the model cell."""
    burn = cells.o2_per_kg / GOOD_CELLS.o2_per_kg
    mix = lambda lo, hi: (value(lo) + waste * (value(hi) - value(lo))) * burn
    return mix("pf_nh3_efficient", "pf_nh3_wild"), mix("pf_lac_efficient", "pf_lac_wild")


def washout_litres(cells: Cells, waste: float = 0.0, nh3_limit: float | None = None) -> float:
    """Litres of liquid that must pass per kg of cells to hold ammonia and lactate under their limits
    (steady state: what is made = what leaves). 11 L/kg for Humbird's enhanced cells, 190 for ordinary
    ones; his 195 g/L at one tank volume a day plus the bleed is the same balance."""
    nh3, lac = waste_per_kg(cells, waste)
    nh3_limit = value("pf_nh3_limit") if nh3_limit is None else nh3_limit
    return max(nh3 / (nh3_limit / 1000.0), lac / (value("pf_lac_limit") / 1000.0))


def explore(doubling_h: float = 24.0, mass_pg: float = 3000.0, vessel_m3: float = 20.0,
            plant: str = "sanitary", mode: str = "perfusion", charge: float | None = None,
            uptime: float | None = None, maintenance_share: float | None = None,
            capex_x: float = 1.0, retention: float | None = None, x_scale: float = 1.0,
            hazard: float = 0.0, run_days: float | None = None, restart_fail_days: float | None = None,
            medium_l: float | None = None, medium_price: float = 0.15, growth_factors: bool = False,
            cell_share: float = 1.0, waste: float = 0.0, nh3_limit: float | None = None,
            pco2_mbar: float | None = None, gas_velocity: float | None = None, aspect: float | None = None) -> dict:
    """One case from the levers a reader can move, with the physics applied:

      * smaller cells respire more per gram (West's law), so the tank holds fewer of them;
      * output per m3 is density x growth rate, so it rises as the doubling time falls;
      * respiration is part upkeep and part the energy of growth (pf_maintenance_share), so faster cells
        respire more per hour and the tank holds fewer of them; per kg, the upkeep part of glucose and of
        utilities scales with the doubling time;
      * the tank must mix faster than it transfers oxygen (pf_mix_ratio_20m3), which tightens with size;
      * a larger vessel costs less per m3 (Humbird Eq. 3.1, bioreactor share only) but holds a thinner
        culture: CO2 leaves only in the sparge gas, and a deeper tank passes less gas per litre
        (co2_limited_density). More CO2 tolerance, more gas flow or a squatter tank all raise the limit;
        gas flow also raises oxygen transfer (kLa ~ u_s^0.8) and tank shape changes the mixing time;
      * perfusion needs a device to hold cells back (pf_capex_retention); fill-and-draw does not, but
        waste then caps the density and the tank averages f/ln(1/(1-f)) of its peak output.

      * a run ends at its planned length or when it is contaminated (a constant chance per day, `hazard`),
        then the tank is cleaned and regrown; a contaminated run also loses the cells in the tank;
      * the litres of medium per kg follow from the waste the cells make (`waste`: 0 = Humbird's enhanced
        cells, 1 = ordinary cells): in perfusion enough liquid must pass to wash ammonia and lactate out;
        in a drained-and-refilled tank waste caps the density instead. The medium costs litres x price,
        but never less than the nutrients the cells must eat (at the default $0.15/L the two meet);
        growth factors can be added at Humbird's large-scale price;
      * the product can be a blend: `cell_share` of cells, the rest plant ingredients.

    `uptime`, if given, overrides the run-length calculation. The defaults reproduce the floor tier at the
    mature-industry capital charge."""
    cells = Cells(mass_pg=mass_pg, doubling_h=doubling_h,
                  maintenance_share=value("pf_maintenance_share") if maintenance_share is None else maintenance_share)
    charge = value("plant_charge_mature") if charge is None else charge
    lost = 0.0                                          # share of output lost with contaminated tanks
    if uptime is None:
        clean = value("pf_uptime") if mode == "perfusion" else value("pf_uptime_realistic")
        restart = value("pf_run_days") * (1.0 / clean - 1.0)            # days to clean, restart and regrow
        L = value("pf_run_days") if run_days is None else run_days
        T = L if hazard <= 0 else (1.0 - np.exp(-hazard * L)) / hazard  # expected days before the run ends
        p_fail = 0.0 if hazard <= 0 else 1.0 - np.exp(-hazard * L)
        # after a contamination the plant must sterilise and regrow a seed train, which can take longer
        down = restart if restart_fail_days is None else (1.0 - p_fail) * restart + p_fail * max(restart, restart_fail_days)
        uptime = T / (T + down)
        lost = min(0.9, p_fail / (cells.mu * 24.0 * T))                 # one tankful per failed run
    key, escalate, sized = PLANT_CLASSES[plant]
    capex = value(key) * (value("pf_capex_escalation") if escalate else 1.0)
    if sized:
        capex = capex_at_size(capex, vessel_m3)
    capex *= capex_x                                   # uncertainty in the plant estimate (floor_mc)
    if mode == "perfusion":
        capex += value("pf_capex_retention") if retention is None else retention
    us_rel = (value("pf_gas_velocity") if gas_velocity is None else gas_velocity) / value("pf_gas_velocity")
    x_o2 = value("pf_otr_cap") * us_rel ** 0.8 / cells.qo2
    limits = {"oxygen supply": x_o2,
              "thickness of the culture": value("pf_x_visc"),
              "mixing": value("pf_otr_cap") / cells.qo2 * value("pf_mix_ratio_20m3") / mixing_time_ratio(vessel_m3, aspect),
              "CO2 removal": x_scale * co2_limited_density(cells, vessel_m3, pco2_mbar, gas_velocity, aspect)}
    wf = waste_per_kg(cells, waste)[0] / waste_per_kg(cells, 0.0)[0]       # waste relative to enhanced cells
    wf *= value("pf_nh3_limit") / (value("pf_nh3_limit") if nh3_limit is None else nh3_limit)
    if mode != "perfusion":
        limits["waste build-up"] = waste_cap(cells) / wf
    limit = min(limits, key=limits.get)
    x = limits[limit]
    shape = 1.0
    if mode != "perfusion":
        f = value("pf_draw_fraction")
        shape = f / np.log(1.0 / (1.0 - f))
    out = value("pf_working_volume") * x * cells.mu * shape * HOURS * uptime / 1000.0 * (1.0 - lost)
    ox = value("pf_opex_escalation")
    burn = cells.o2_per_kg / GOOD_CELLS.o2_per_kg
    capital = charge * capex / out
    labour = value("pf_labour") * output_per_m3(GOOD_CELLS, "fedbatch") / out * ox
    utilities = value("pf_utilities") * ox * (0.5 + 0.5 * burn)
    consumables = value("pf_consumables_low")
    if medium_l is None:                                # derived: nutrients need a minimum; waste needs more
        need = washout_litres(cells, waste, nh3_limit) if mode == "perfusion" else 1000.0 / x
        medium_l = max(value("pf_medium_l_floor"), need)
    feed = max(feedstock(cells), medium_l * medium_price) / (1.0 - lost)   # medium in a lost tank is lost too
    gf = value("pf_growth_factors") * ox if growth_factors else 0.0
    total = capital + labour + utilities + consumables + feed + gf
    product = cell_share * total + (1.0 - cell_share) * value("pf_blend_filler_price")
    return {"density": float(x), "limit": limit, "output": float(out), "capex": float(capex),
            "capital": float(capital), "labour": float(labour), "utilities": float(utilities),
            "consumables": consumables, "feedstock": float(feed), "growth_factors": float(gf),
            "uptime": float(uptime), "medium_l": float(medium_l), "total": float(total),
            "product": float(product)}


def _stokes(d_um: float, drho: float) -> float:
    """Stokes settling velocity, cm/h, of a sphere d_um across with density excess drho (kg/m3)."""
    d = d_um * 1e-6
    v = d * d * drho * 9.81 / (18.0 * value("pf_medium_viscosity") * 1e-3)        # m/s
    return v * 100.0 * 3600.0


def settler_spec(cells: Cells = None, x: float | None = None, medium_l: float | None = None,
                 anoxia_min: float | None = None, vessel_m3: float = 20.0) -> dict:
    """Can a gravity settler hold the cells back in a large perfusion tank? First-principles sizing.

    A single cell settles at Stokes' velocity, slowed by crowding (Richardson-Zaki, (1 - phi)^4.65). An
    inclined settler needs projected plate area = liquid flow / settling velocity, and a cell stays in
    it for about plate gap / (velocity x cos 60). The stay is without oxygen, so it must be shorter than
    the cells tolerate. Clumps settle faster (velocity ~ diameter^2 x packing), which gives the
    specification: the clump size at which the stay fits the tolerated time. Returns velocities (cm/h),
    plate area per tank (m2), stay (minutes) for single cells, and the clump diameter needed (um)."""
    cells = GOOD_CELLS if cells is None else cells
    x = co2_limited_density(cells, vessel_m3) if x is None else x
    medium_l = washout_litres(cells) if medium_l is None else medium_l
    tol = value("pf_anoxia_min") if anoxia_min is None else anoxia_min
    rho_c, rho_m = value("pf_cell_density") * 1000.0, value("pf_medium_density") * 1000.0
    d_cell = (6.0 * cells.mass_pg * 1e-15 / (np.pi * rho_c)) ** (1.0 / 3.0) * 1e6       # um
    phi = x / rho_c                                                                    # volume fraction of cells
    crowd = (1.0 - phi) ** 4.65
    v1 = _stokes(d_cell, rho_c - rho_m)
    v1h = v1 * crowd
    out = value("pf_working_volume") * x * cells.mu * HOURS * value("pf_uptime") / 1000.0   # t per m3 per yr
    flow = medium_l * out * 1000.0 / HOURS / 1000.0 * vessel_m3                        # m3 of liquid per hour, per tank
    gap, cos60 = value("pf_plate_gap"), 0.5
    stay = lambda v: gap / (v * cos60) * 60.0                                           # minutes
    pack = value("pf_clump_packing")
    # clump whose (crowded) velocity makes the stay equal the tolerated time: v ~ d^2 x packing
    v_need = gap / (tol / 60.0 * cos60)                                                # cm/h
    d_need = d_cell * np.sqrt(v_need / (v1h * pack))
    return {"cell_um": float(d_cell), "single_cell_cm_h": float(v1), "crowded_cm_h": float(v1h),
            "flow_m3_h": float(flow), "plate_area_m2": float(flow / (v1h / 100.0)),
            "stay_min": float(stay(v1h)), "oxygen_lasts_s": float(0.044 / (x * cells.qo2) * 3600.0),
            "clump_um_needed": float(d_need), "cells_per_clump": float(pack * (d_need / d_cell) ** 3),
            "plate_area_clumps_m2": float(flow / (v_need / 100.0))}


def temperature_check(delta_c: float = 10.0, heat_price: float = 0.05) -> dict:
    """Does a lower culture temperature (fish, insect cells at about 27 C against 37 C) save energy?
    Per kg of cells: the heat the cells give off (oxygen burned x 483 kJ per mol), the heat needed to
    warm the medium by `delta_c` (4.18 kJ per litre per degree) at the floor's 8 L/kg and at the
    reported 30.5 L/kg, and what that heat costs at `heat_price` $/kWh (industrial steam or gas heat
    [assumed]). At production scale the culture gives off several times more heat than warming its
    feed takes, so tanks are cooled, not heated; a lower setpoint saves cents per kg at most and makes
    cooling harder. Small lab vessels lose heat through their walls and do need heating."""
    kwh = lambda kj: kj / 3600.0
    met = GOOD_CELLS.o2_per_kg / 0.032 * value("pf_heat_per_o2")            # kJ per kg of cells
    heat = lambda litres: litres * 4.18 * delta_c
    lo, hi = value("pf_medium_l_floor"), value("media_intensity")
    return {"metabolic_heat_kwh": kwh(met), "heating_10c_kwh": kwh(heat(lo)), "heating_10c_kwh_reported": kwh(heat(hi)),
            "heating_10c_usd": kwh(heat(lo)) * heat_price, "heating_10c_usd_reported": kwh(heat(hi)) * heat_price,
            "utilities_usd": value("pf_utilities") * value("pf_opex_escalation")}


# What is uncertain about the floor case, as triangular (low, mode, high). The mode is the point value.
FLOOR_PRIORS = {
    # the plant estimate: Humbird calls his own "within 50%"; two other published designs for animal cells
    # come in far lower per m3 (Negulescu 2023 $209k, CE Delft 2021 $167-277k, against his $611k without
    # clean rooms), so the low end is their level (research_notes/plant_capital_crosscheck.md)
    "capex_x":           (0.34, 1.0, 1.5),
    # Humbird's uptime is the top of the range (he calls it 'rather aggressive'); 0.75 from long-run pharma
    "uptime":            (0.75, value("pf_uptime"), value("pf_uptime")),
    # CO2-limited density at 20 m3: 60 g/L (twice the largest reported harvest) to Humbird Fig. 2.8b's 150
    "x_scale":           (value("pf_x_half") / value("pf_x_co2_20m3"), 1.0, 150.0 / value("pf_x_co2_20m3")),
    # cells: 18 h is fast for an animal line, 48 h is what one company reports in perfusion
    "doubling_h":        (18.0, 24.0, 48.0),
    # cells: 1 ng (reported chicken cells) to the 3 ng model cell
    "mass_pg":           (1000.0, 3000.0, 3000.0),
    # cells: waste from Humbird's enhanced cells (0) to a quarter of the way to ordinary cells; the 30.5 L/kg
    # one company reports is about a tenth of the way
    "waste":             (0.0, 0.0, 0.25),
}
# The inputs that describe how good the cells are, with the sign that means "better". Good traits tend to
# come together (a well-adapted line is fast, dense and frugal), so they are sampled with a shared
# correlation `cell_corr` [assumed 0.5; 0 = independent]. Correlation fattens both tails.
CELL_QUALITY = {"x_scale": +1, "doubling_h": -1, "mass_pg": +1, "waste": -1}


# The limiting factors for the tornado chart on the page: (label, explore() argument, low value, high value,
# low text, high text, what it is / where the range comes from / how solid). Each is moved alone, the rest
# held at the case being viewed. Ranges are the ones the uncertainty run uses (FLOOR_PRIORS, input priors)
# or the literature ranges in research_notes/. Only things that can limit the cost are here: a product
# choice such as blending is not.
TORNADO = [
    ("Gas flow the cells tolerate", "gas_velocity", 0.002, 0.006, "2 mm/s", "6 mm/s",
     "CO\u2082 leaves the tank only in the gas bubbled through it, so the density a tank can hold is "
     "proportional to the gas flow. Too much gas kills cells when bubbles burst. <b>Range:</b> 6 mm/s is the top "
     "of the published guidance, which the floor uses [2]. Large pharma tanks usually run at 5 to 20 times less, "
     "because their thin cultures need no more; 2 mm/s is a judgement between the two. <b>Evidence:</b> weak. "
     "Nobody has run cells this dense at this size."),
    ("Tank shape (liquid depth / width)", "aspect", 1.0, 3.0, "1.0", "3.0",
     "A deeper tank passes less gas per litre of liquid, so it clears less CO\u2082, and it mixes more slowly. "
     "<b>Range:</b> Humbird's tank has liquid 1.6 times as deep as it is wide [2]; tanks in use run from about 1 "
     "to 3. <b>Evidence:</b> the geometry is certain. What a squat vessel costs is not modelled."),
    ("Tank size", "vessel_m3", 5.0, 200.0, "5 m\u00b3", "200 m\u00b3",
     "A larger tank costs less per litre but is deeper, so it clears less CO\u2082 and must run thinner. "
     "<b>Range:</b> 5 to 200 m\u00b3; the floor uses 20. <b>Evidence:</b> the vessel cost and the CO\u2082 limit "
     "both follow Humbird [2]. Animal cells have not been grown above about 25 m\u00b3, and only in pharma."),
    ("Plant estimate", "capex_x", 0.34, 1.5, "a third of Humbird's", "+50%",
     "What the whole plant costs per cubic metre of tank. <b>Range:</b> Humbird calls his own estimate good to "
     "within 50% [2]. Two other published designs for animal cells (Negulescu, CE Delft) assume plants at about a "
     "third of his cost. <b>Evidence:</b> design studies only. No built plant publishes both its cost and its "
     "tank volume."),
    ("Class of plant", "plant", "microbial", "pharma", "built like a yeast plant", "pharma-style",
     "How sterile the plant is built. The floor uses a sterile plant without clean rooms ($810k per m\u00b3). "
     "<b>Range:</b> a plant built like a yeast plant ($190k) to a pharma-style plant with clean rooms ($910k). "
     "Humbird's own yeast plant with 20 m\u00b3 tanks costs about the lower figure, and two published "
     "cultivated-meat designs assume it. <b>Evidence:</b> nobody has run animal cells in the cheaper kind."),
    ("Waste the cells make", "waste", 0.0, 0.25, "efficient cells", "a quarter of the way to ordinary",
     "Cells make ammonia and lactate, which stop growth. In perfusion fresh medium must wash them out, so "
     "wasteful cells need more medium. <b>Range:</b> Humbird's efficient cells need 11 litres per kilo and "
     "ordinary cells 190 [2]; one company reports 30.5 for chicken, about a tenth of the way [1]. "
     "<b>Evidence:</b> the efficient cell is an assumption, not shown for meat cells."),
    ("Doubling time", "doubling_h", 18.0, 48.0, "18 h", "48 h",
     "A tank's output is its density times how fast the cells grow. Faster cells also respire more, so the "
     "tank holds fewer of them. <b>Range:</b> 24 hours is Humbird's model cell [2]; 18 is fast for an animal "
     "line; one company reports 48 in perfusion [1]. <b>Evidence:</b> measured for a few lines, mostly grown on "
     "a surface, not in dense suspension."),
    ("Cell mass", "mass_pg", 1000.0, 3000.0, "1 ng", "3 ng",
     "Smaller cells respire more per gram, so the tank holds fewer of them. <b>Range:</b> the model cell is "
     "3 ng [2]; chicken cells are reported at 1 to 1.75 ng [1]. <b>Evidence:</b> the scaling law is well "
     "established; cell mass is rarely reported on a sound basis."),
    ("CO\u2082 the cells tolerate", "pco2_mbar", 100.0, 200.0, "100 mbar", "200 mbar",
     "The density a tank can hold is proportional to the dissolved CO\u2082 the cells tolerate. <b>Range:</b> "
     "100 mbar is a pharma limit that also protects protein quality [2]; pharma cells lose about a tenth of "
     "their growth at 200. <b>Evidence:</b> nothing is published for muscle or fish cells. This is the "
     "measurement that would move the floor most."),
    ("Yearly charge on the plant", "charge", 0.123, 0.236, "12.3%", "23.6%",
     "The share of the plant's cost charged each year: return on capital, maintenance, insurance. "
     "<b>Range:</b> 23.6% is Humbird's first-plant figure; the floor's 17.3% uses the food industry's cost of "
     "capital over 20 years; 12.3% is a 30-year payback with no return. <b>Evidence:</b> a financing choice, "
     "not a scientific unknown. Loan guarantees move it."),
    ("Retention device", "retention", 0.0, 460.0, "free", "Humbird's filters",
     "Perfusion needs something that holds the cells in the tank while spent medium leaves. <b>Range:</b> the "
     "floor prices it at what one study hopes it will cost ($89k per m\u00b3); the filters pharma uses would "
     "cost about $460k. <b>Evidence:</b> a gravity settler runs today at 3,000 litres; a 20 m\u00b3 tank needs "
     "4.5 times the flow."),
    ("Growth factors", "growth_factors", False, True, "none", "bought",
     "Proteins that tell cells to grow. The floor leaves them out: cells that need none, or make their own. "
     "<b>Range:</b> bought at Humbird's large-scale price they add about $4 a kilo [2]. <b>Evidence:</b> that "
     "price assumes an industry far larger than today's."),
    ("Medium price", "medium_price", 0.10, 0.50, "$0.10 a litre", "$0.50 a litre",
     "What a litre of the nutrient liquid costs. It can never cost less than the nutrients the cells eat, so "
     "it matters more the more medium the cells need. <b>Range:</b> companies report $0.20 to $0.50 a litre [1]. "
     "<b>Evidence:</b> company reports, not verified at scale."),
    ("How the tank is run", "mode", "perfusion", "filldraw", "perfusion", "drained and refilled",
     "In perfusion a device holds the cells back while medium flows through, so the tank stays at its densest. "
     "A tank that is half drained and refilled needs no device, but averages 72% of peak output and waste "
     "caps its density. <b>Evidence:</b> draining and refilling is used at 20 m\u00b3; perfusion is not, "
     "beyond 2 to 3 m\u00b3."),
    ("Runs lost to contamination", "hazard", 0.0, 0.02, "none", "2% a day",
     "A contaminated run ends early; the tank must be cleaned and regrown (14 days here) and a tankful is "
     "lost. <b>Range:</b> large pharma plants lose about 0.2% of runs a day; cultivated-meat makers report "
     "losses that work out to roughly 1 to 2% a day. <b>Evidence:</b> one survey, with run lengths not stated."),
    ("Oxygen used for upkeep", "maintenance_share", 0.31, 1.0, "31%", "100%",
     "Part of a cell's oxygen use runs whether or not it grows; the rest rises with growth. It matters only "
     "when the doubling time is not 24 hours. <b>Range:</b> measurements put the upkeep share at 31% to 62%; "
     "Humbird assumes 100% [2]. <b>Evidence:</b> few measurements, none for meat cells."),
]


def floor_tornado(**case) -> list:
    """Cost of the case ($/kg) with each limiting factor at the low and the high end of its range, the
    others as in `case` (default: the floor). Contamination is evaluated with a 14-day restart after a
    lost run. Returns rows (label, cost at low, cost at high, low text, high text), widest first."""
    case = dict(case)
    case.setdefault("restart_fail_days", 14.0)
    rows = []
    for label, arg, lo, hi, lo_txt, hi_txt, _info in TORNADO:
        a = explore(**{**case, arg: lo})["total"]
        b = explore(**{**case, arg: hi})["total"]
        rows.append((label, a, b, lo_txt, hi_txt))
    return sorted(rows, key=lambda r: -abs(r[2] - r[1]))


def _tri_ppf(u, lo, mode, hi):
    """Inverse CDF of a triangular distribution (vectorised); a point mass if hi == lo."""
    if hi <= lo:
        return np.full_like(u, mode, dtype=float)
    fc = (mode - lo) / (hi - lo)
    return np.where(u < fc, lo + np.sqrt(u * (hi - lo) * (mode - lo)),
                    hi - np.sqrt((1.0 - u) * (hi - lo) * (hi - mode)))


def floor_mc(n: int = 4000, seed: int = 0, plant: str = "sanitary", cell_corr: float = 0.5) -> dict:
    """Monte Carlo over the floor case's own inputs: the plant estimate, uptime, the density limit, the
    cells (speed, size, waste), the retention device, financing and the upkeep share of respiration.
    Everything else in the case (perfusion at 20 m3, no growth factors) is held. The cell-quality inputs
    share a correlation `cell_corr` (Gaussian copula). Returns the draws of total cost ($/kg) and of
    each input."""
    from inputs import prior
    from math import erf, sqrt
    rng = np.random.default_rng(seed)
    pri = dict(FLOOR_PRIORS)
    for key, name in (("retention", "pf_capex_retention"), ("charge", "plant_charge_mature"),
                      ("maintenance_share", "pf_maintenance_share")):
        _kind, lo, hi, mode, _note = prior(name)
        pri[key] = (lo, mode, hi)
    if plant == "microbial":                           # the class's own range replaces the estimate's accuracy
        _kind, lo, hi, mode, _note = prior("pf_capex_fermentation")
        pri["capex_x"] = (lo / mode, 1.0, hi / mode)
    common = rng.standard_normal(n)                    # the shared "how good are the cells" factor
    phi = np.vectorize(lambda z: 0.5 * (1.0 + erf(z / sqrt(2.0))))
    draws = {}
    for k, (lo, mode, hi) in pri.items():
        z = rng.standard_normal(n)
        if k in CELL_QUALITY:
            z = CELL_QUALITY[k] * (sqrt(cell_corr) * common + sqrt(1.0 - cell_corr) * z)
        draws[k] = _tri_ppf(phi(z), lo, mode, hi)
    total = np.array([explore(plant=plant, **{k: float(v[i]) for k, v in draws.items()})["total"]
                      for i in range(n)])
    return {"total": total, **draws}


def summarise_floor_mc(pr: CostParams, n: int = 4000) -> None:
    pc = parity_cost(pr)
    print(f"\n  uncertainty on the floor case (N={n}, seed 0), cells $/kg:")
    for plant, label in (("sanitary", "sterile plant, no clean rooms"), ("microbial", "yeast-style plant")):
        mc = floor_mc(n, plant=plant)
        t = mc["total"]
        p10, p50, p90 = np.percentile(t, [10, 50, 90])
        print(f"    {label:<32} point {explore(plant=plant)['total']:5.1f}   P10 {p10:5.1f}  P50 {p50:5.1f}  "
              f"P90 {p90:5.1f}   P(<= ${pc:.0f}) {np.mean(t <= pc):.2f}   P(<= $10) {np.mean(t <= 10):.2f}")
        ind = floor_mc(n, plant=plant, cell_corr=0.0)["total"]
        print(f"      with independent cell traits: P10 {np.percentile(ind, 10):5.1f}  P50 {np.percentile(ind, 50):5.1f}  "
              f"P90 {np.percentile(ind, 90):5.1f}   P(<= ${pc:.0f}) {np.mean(ind <= pc):.2f}")
        if plant == "sanitary":
            rk = lambda a: np.argsort(np.argsort(a))
            rho = {k: float(np.corrcoef(rk(v), rk(t))[0, 1]) for k, v in mc.items() if k != "total"}
            print("      what moves it (rank correlation): " +
                  ", ".join(f"{k} {v:+.2f}" for k, v in sorted(rho.items(), key=lambda kv: -abs(kv[1]))))


# ----------------------------------------------------------------------------
# The ladder of tiers
# ----------------------------------------------------------------------------
def tiers() -> list:
    """Each tier: (name, what it assumes, demonstrated?, cost breakdown). Ordered from 'as engineered'
    down to 'physics limit'."""
    fb = value("pf_capex_aseptic_fedbatch")
    rows = []

    cx, ox = value("pf_capex_escalation"), value("pf_opex_escalation")

    def add(name, assumes, shown, cells, mode, capex, consumables, gf, cheap=False, otr=None, humbird_capex=True,
            uptime=None, x_cap=None, labour=None, humbird_consumables=False, retention=False):
        # capital: Humbird's figures are escalated from 2018 prices; the others are recent. The retention
        # device (2024 prices) is added after escalation.
        cap = capex * (cx if humbird_capex else 1.0) + (value("pf_capex_retention") if retention else 0.0)
        pc = plant_cost(cells, mode, cap, consumables, otr, capex_x=1.0, opex_x=ox, uptime=uptime, x_cap=x_cap,
                        labour=labour, escalate_consumables=humbird_consumables)
        gf = gf * ox
        feed = feedstock(cells, cheap)
        # the same plant financed like a mature food industry (plant_charge_mature in place of
        # humbird_plant_charge): only the capital line changes
        saving = pc["capital"] * (1.0 - value("plant_charge_mature") / value("humbird_plant_charge"))
        rows.append({"name": name, "assumes": assumes, "shown": shown, **pc,
                     "feedstock": feed, "growth_factors": gf,
                     "total": pc["plant"] + feed + gf,
                     "plant_mature": pc["plant"] - saving, "total_mature": pc["plant"] + feed + gf - saving})

    low = value("pf_consumables_low")           # assumed, in 2025 prices
    design_uptime = value("pf_uptime")          # Humbird's own figure; he calls it "rather aggressive"
    ncr = value("pf_capex_no_cleanroom")
    add("Humbird fed-batch, as designed", "sterile 20 m3 stirred tanks with clean rooms, filled and emptied every ~2 days; efficient 3 ng cells; growth factors bought",
        "designed, not built", GOOD_CELLS, "fedbatch", fb, value("pf_consumables_fedbatch"),
        value("pf_growth_factors"), humbird_consumables=True)
    add("Humbird perfusion, as designed", "sterile 2 m3 tanks, cells held back by ATF filters; same cells",
        "designed; perfusion at 2 m3 exists in pharma", GOOD_CELLS, "perfusion",
        value("pf_capex_aseptic_perfusion"), value("pf_consumables_perfusion"), value("pf_growth_factors"),
        uptime=design_uptime, labour=value("pf_labour_perfusion"), humbird_consumables=True)
    add("Same fed-batch plant, small slow cells", "cells of 0.55 ng doubling every 61 h; each tank turns over far more slowly",
        "cells exist; this plant does not", PASITKA_CELLS, "fedbatch", fb, value("pf_consumables_fedbatch"),
        value("pf_growth_factors"), humbird_consumables=True)
    add("Pharma-style plant, half the density", "the cautious case below with cells at 60 g/L, not 120",
        "nearer to reported harvests (about 27 g/L)", GOOD_CELLS, "filldraw", fb, low, 0.0, x_cap=value("pf_x_half"))
    add("Pharma-style plant, fill-and-draw", "Humbird's sterile plant with clean rooms; 20 m3 tanks half drained and refilled each cycle, no cell retention, 85% uptime; efficient cells",
        "fill-and-draw is filed as an option at 20 m3; this density is not shown", GOOD_CELLS, "filldraw", fb, low, 0.0)
    add("No clean rooms, fill-and-draw", "the same culture in a food-grade building: Humbird's plant with a sanitary hall in place of the clean room",
        "food-grade 20 m3 tanks run today; this density is not shown", GOOD_CELLS, "filldraw", ncr, low, 0.0)
    add("No clean rooms, perfusion", "the floor: food-grade sterile plant; 20 m3 tanks in perfusion at 120 g/L, cells held back by a hoped-for filter-free device; efficient cells; 91% uptime",
        "each piece shown or claimed separately, never together", GOOD_CELLS, "perfusion",
        ncr, low, 0.0, uptime=design_uptime, x_cap=co2_cap(GOOD_CELLS), retention=True)
    add("Microbial-fermentation-class plant", "the frontier: the floor case in a plant that costs what microbial fermentation plants cost when built",
        "such plants exist for microbes; not costed or built for animal cells", GOOD_CELLS, "perfusion",
        value("pf_capex_fermentation"), low, 0.0, humbird_capex=False, uptime=design_uptime,
        x_cap=co2_cap(GOOD_CELLS), retention=True)
    add("Rough lower bound", "the cheapest modelled fermentation plant, small-tank density, oxygen at the animal-cell ceiling, amino acids at half price",
        "a rough bound, not a design", GOOD_CELLS, "perfusion", value("pf_bound_capex"), low, 0.0,
        cheap=True, otr=value("pf_bound_otr"), humbird_capex=False, uptime=design_uptime)
    return rows


def summarise(pr: CostParams) -> None:
    pc = parity_cost(pr)
    for label, c in (("efficient model cell (3 ng, 24 h)", GOOD_CELLS), ("small slow cell (0.55 ng, 61 h)", PASITKA_CELLS)):
        print(f"  {label}: oxygen uptake {c.qo2:.3f} mmol/g/h, {c.o2_per_kg:.2f} kg O2 per kg cells; "
              f"oxygen-limited density {density(c, value('pf_otr_cap'), True):.0f} g/L")
    print(f"\n  parity needs cells at <= ${pc:.0f}/kg (with a ${pr.markup_add:.0f} markup against ${pr.p_conv:.0f} meat)\n")
    print(f"  first-plant financing {value('humbird_plant_charge'):.1%} a year; 'mature' = food-industry financing "
          f"{value('plant_charge_mature'):.1%}")
    print(f"  {'tier':<36}{'t/m3/yr':>8}{'capital':>9}{'labour':>8}{'util+cons':>10}{'feed':>7}{'GF':>6}{'TOTAL':>8}   R   mature")
    for r in tiers():
        R = (r["total"] + pr.markup_add) / pr.p_conv
        print(f"  {r['name']:<36}{r['output']:>8.1f}{r['capital']:>9.2f}{r['labour']:>8.2f}"
              f"{r['utilities'] + r['consumables']:>10.2f}{r['feedstock']:>7.2f}{r['growth_factors']:>6.1f}"
              f"{r['total']:>8.1f}  {R:.2f}  {r['total_mature']:>6.1f}")
    st = settler_spec()
    print(f"\n  holding cells back by settling, 20 m3 perfusion tank at the floor case:")
    print(f"    a {st['cell_um']:.0f} um cell settles at {st['single_cell_cm_h']:.1f} cm/h ({st['crowded_cm_h']:.1f} when crowded); "
          f"{st['flow_m3_h']:.2f} m3/h of liquid needs {st['plate_area_m2']:.0f} m2 of plate")
    print(f"    cells would stay {st['stay_min']:.0f} min in the settler; their oxygen lasts {st['oxygen_lasts_s']:.0f} s")
    print(f"    to keep the stay under {value('pf_anoxia_min'):.0f} min: clumps of {st['clump_um_needed']:.0f} um "
          f"(about {st['cells_per_clump']:.0f} cells), {st['plate_area_clumps_m2']:.0f} m2 of plate")
    base = explore()["total"]
    print(f"\n  what limits the floor case (${base:.1f}/kg): each factor alone, low end -> high end of its range")
    for label, a, b, lo_txt, hi_txt in floor_tornado():
        print(f"    {label:<36} {lo_txt:>28} ${a:5.1f}   {hi_txt:<34} ${b:5.1f}")
    summarise_floor_mc(pr)
    print("\n  what each tier assumes, and whether it has been shown:")
    for r in tiers():
        print(f"    {r['name']}: {r['assumes']}  [{r['shown']}]")


def fig_floor_tiers(pr: CostParams, outdir, fmts) -> None:
    rows = tiers()[::-1]
    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    parts = [("feedstock", "feedstock", "#029E73"), ("growth_factors", "growth factors", "#DE8F05"),
             ("capital", "plant capital", "#0173B2"), ("opex", "labour, utilities, consumables", "#56B4E9")]
    y = np.arange(len(rows))
    left = np.zeros(len(rows))
    for key, label, colour in parts:
        vals = np.array([r["labour"] + r["utilities"] + r["consumables"] if key == "opex" else r[key] for r in rows])
        ax.barh(y, vals, left=left, color=colour, label=label, height=0.62)
        left += vals
    for yi, r in zip(y, rows):
        ax.text(r["total"] + 0.6, yi, f"\\${r['total']:.0f}", va="center", fontsize=8)
        ax.plot([r["total_mature"]], [yi], marker="|", ms=13, mew=1.6, color="k",
                label="with food-industry financing" if yi == 0 else None)
    ax.axvline(parity_cost(pr), ls=":", lw=1.2, color="#CC3311")
    ax.text(parity_cost(pr) + 0.4, len(rows) - 0.45, "parity", fontsize=7.5, color="#CC3311")
    ax.set_yticks(y)
    ax.set_yticklabels([r["name"] for r in rows], fontsize=8)
    ax.set_xlabel(r"Cost of real wet cells (\$/kg)")
    ax.set_xlim(0, min(max(r["total"] for r in rows) * 1.12, 80))
    ax.set_title("The class of plant sets the physics-allowed cost floor")
    ax.legend(fontsize=7.5, frameon=False, loc="lower right")
    ax.grid(axis="y", visible=False)
    _save(fig, outdir, "floor_tiers", fmts)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outdir", default="figures")
    ap.add_argument("--no-latex", action="store_true")
    ap.add_argument("--formats", default="png,pdf")
    args = ap.parse_args()
    setup_style(use_latex=not args.no_latex)
    fmts = [f.strip() for f in args.formats.split(",") if f.strip()]
    pr = CostParams()
    print("Rung 2 side-study — physics-based floor, per kg of real wet cells:")
    summarise(pr)
    fig_floor_tiers(pr, args.outdir, fmts)
    print("Done.")


if __name__ == "__main__":
    main()
