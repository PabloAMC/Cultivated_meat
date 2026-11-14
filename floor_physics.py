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
                "litres of medium per kilo (set the medium price to $0.50 for the reported cost). Chicken "
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


def explore(doubling_h: float = 24.0, mass_pg: float = 3000.0, vessel_m3: float = 20.0,
            plant: str = "sanitary", mode: str = "perfusion", charge: float | None = None,
            uptime: float | None = None, maintenance_share: float | None = None,
            capex_x: float = 1.0, retention: float | None = None, x_scale: float = 1.0,
            hazard: float = 0.0, run_days: float | None = None, restart_fail_days: float | None = None,
            medium_l: float | None = None, medium_price: float = 0.20, growth_factors: bool = False,
            cell_share: float = 1.0) -> dict:
    """One case from the levers a reader can move, with the physics applied:

      * smaller cells respire more per gram (West's law), so the tank holds fewer of them;
      * output per m3 is density x growth rate, so it rises as the doubling time falls;
      * respiration is part upkeep and part the energy of growth (pf_maintenance_share), so faster cells
        respire more per hour and the tank holds fewer of them; per kg, the upkeep part of glucose and of
        utilities scales with the doubling time;
      * the tank must mix faster than it transfers oxygen (pf_mix_ratio_20m3), which tightens with size;
      * a larger vessel costs less per m3 (Humbird Eq. 3.1, bioreactor share only) but holds a thinner
        culture, because CO2 is harder to strip (pf_co2_size_exponent);
      * perfusion needs a device to hold cells back (pf_capex_retention); fill-and-draw does not, but
        waste then caps the density and the tank averages f/ln(1/(1-f)) of its peak output.

      * a run ends at its planned length or when it is contaminated (a constant chance per day, `hazard`),
        then the tank is cleaned and regrown; a contaminated run also loses the cells in the tank;
      * the medium costs litres per kg x price, but never less than the nutrients the cells must eat;
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
    limits = {"oxygen supply": value("pf_otr_cap") / cells.qo2,
              "thickness of the culture": value("pf_x_visc"),
              "mixing": value("pf_otr_cap") / cells.qo2 * value("pf_mix_ratio_20m3") * (vessel_m3 / 20.0) ** (-2.0 / 9.0),
              "CO2 removal": x_scale * co2_cap(cells) * (vessel_m3 / 20.0) ** value("pf_co2_size_exponent")}
    if mode != "perfusion":
        limits["waste build-up"] = waste_cap(cells)
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
    medium_l = value("pf_medium_l_floor") if medium_l is None else medium_l
    feed = max(feedstock(cells), medium_l * medium_price) / (1.0 - lost)   # medium in a lost tank is lost too
    gf = value("pf_growth_factors") * ox if growth_factors else 0.0
    total = capital + labour + utilities + consumables + feed + gf
    product = cell_share * total + (1.0 - cell_share) * value("pf_blend_filler_price")
    return {"density": float(x), "limit": limit, "output": float(out), "capex": float(capex),
            "capital": float(capital), "labour": float(labour), "utilities": float(utilities),
            "consumables": consumables, "feedstock": float(feed), "growth_factors": float(gf),
            "uptime": float(uptime), "total": float(total), "product": float(product)}


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
    # a factored estimate from one design study is good to about -30% / +50% (AACE class 4) [assumed]
    "capex_x":           (0.7, 1.0, 1.5),
    # Humbird's uptime is the top of the range (he calls it 'rather aggressive'); 0.75 from long-run pharma
    "uptime":            (0.75, value("pf_uptime"), value("pf_uptime")),
    # CO2-limited density at 20 m3: 60 g/L (twice the largest reported harvest) to Humbird Fig. 2.8b's 150
    "x_scale":           (value("pf_x_half") / value("pf_x_co2_20m3"), 1.0, 150.0 / value("pf_x_co2_20m3")),
    # cells: 18 h is fast for an animal line, 48 h is what one company reports in perfusion
    "doubling_h":        (18.0, 24.0, 48.0),
    # cells: 1 ng (reported chicken cells) to the 3 ng model cell
    "mass_pg":           (1000.0, 3000.0, 3000.0),
}


def floor_mc(n: int = 4000, seed: int = 0, plant: str = "sanitary") -> dict:
    """Monte Carlo over the floor case's own inputs: the plant estimate, uptime, the density limit, the
    cells, the retention device, financing and the upkeep share of respiration. Everything else in the
    case (perfusion at 20 m3, floor-price medium, no growth factors) is held. Returns the draws of
    total cost ($/kg) and of each input."""
    from inputs import prior
    rng = np.random.default_rng(seed)
    tri = lambda lo, mode, hi: rng.triangular(lo, mode, hi, n) if hi > lo else np.full(n, mode)
    draws = {k: tri(*v) for k, v in FLOOR_PRIORS.items()}
    for key, name in (("retention", "pf_capex_retention"), ("charge", "plant_charge_mature"),
                      ("maintenance_share", "pf_maintenance_share")):
        _kind, lo, hi, mode, _note = prior(name)
        draws[key] = tri(lo, mode, hi)
    if plant == "microbial":                           # the class's own range replaces the estimate's accuracy
        _kind, lo, hi, mode, _note = prior("pf_capex_fermentation")
        draws["capex_x"] = tri(lo, mode, hi) / mode
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
