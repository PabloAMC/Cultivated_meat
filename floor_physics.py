#!/usr/bin/env python3
"""
floor_physics.py — the cost of a kilo of cultivated cells from tank physics and published plant costs,
by reactor type and plant class (`explore`). The cost scenarios (scenarios.py) are sets of `explore` arguments;
its defaults are the labelled reference case "a standard perfusion tank, no added equipment for oxygen and CO₂" ($12.81/kg), which earlier
versions called the floor. (NOT used in the default cost of the share model.)

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

   If waste is not washed out (fed-batch, fill-and-draw, chemostat), the waste mass balance caps
   the density lower still: X <= end factor x level allowed / waste made per kg (explore; since
   2026-11-19). Humbird's own fed-batch design (X_unperfused, 120 g/L for efficient cells in 20 m3)
   is kept for his tiers and for the labour per m3 of his fed-batch plant.

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
from cost_model import CostParams, parity_cost, ratio

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
    """Density (g/L) at which waste stops a culture that is not washed out, scaled from Humbird's fed-batch design. Used only by
    his own designs (tiers, density, output_per_m3); explore() uses the waste mass balance instead (2026-11-19)."""
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
                        gas_velocity: float | None = None, aspect: float | None = None,
                        rq: float | None = None) -> float:
    """Density (g wet/L) at which the cells make CO2 as fast as the sparge gas can carry it off.
    Removal = (gas velocity / liquid depth) x (pCO2 / RT) x how close the exhaust comes to equilibrium;
    production = RQ x oxygen uptake per gram. Reproduces Humbird's Fig. 2.8b (see pf_co2_strip_eff)."""
    pco2 = value("pf_pco2_limit") if pco2_mbar is None else pco2_mbar
    us = value("pf_gas_velocity") if gas_velocity is None else gas_velocity
    _T, depth = tank_shape(vessel_m3, aspect)
    carry = pco2 * 100.0 / (8.314 * 310.15)                    # mol CO2 per m3 of gas at the limit
    removal = us / depth * 3600.0 * carry * value("pf_co2_strip_eff")   # mol per m3 of liquid per hour = mmol/L/h
    return removal / ((value("pf_rq") if rq is None else rq) * cells.qo2)


def oxygen_fed(vessel_m3: float = 20.0, gas_velocity: float | None = None, aspect: float | None = None,
               p_top_barg: float | None = None) -> float:
    """Oxygen fed with the sparge gas, kg O2 per m3 of liquid per hour: (gas velocity / liquid depth) tank
    volumes of gas per second, at the pressure at the top of the vessel, of which pf_o2_purity is oxygen.
    It depends on the gas flow and the tank, not on what the cells use: nearly all of it leaves in the
    exhaust, because the gas flow is set by CO2 removal. With the defaults (Humbird's 20 m3 tank at 6 mm/s)
    it is 8.6 kg per m3 an hour; his plant's oxygen unit averages 7.4 over a fed-batch cycle (Table 4.1).
    A higher pressure at the top (`p_top_barg`) puts more gas into the same velocity, in proportion."""
    us = value("pf_gas_velocity") if gas_velocity is None else gas_velocity
    _T, depth = tank_shape(vessel_m3, aspect)
    bar = value("pf_back_pressure")
    if p_top_barg is not None:
        bar *= (1.01325 + p_top_barg) / (1.01325 + value("ge_p_top_base"))
    mol_gas = us / depth * 3600.0 * bar * 1e5 / (8.314 * 310.15)       # mol gas per m3 liquid per hour
    return mol_gas * value("pf_o2_purity") * 0.032


def mixing_time_ratio(vessel_m3: float, aspect: float | None = None) -> float:
    """Mixing time relative to the reference 20 m3 tank (Humbird Eq. 2.18 at fixed stirring power):
    t_m ~ T^(2/3) x (H_L/T)^2.5."""
    T, _d = tank_shape(vessel_m3, aspect)
    T0, _d0 = tank_shape(20.0, value("pf_aspect"))
    a = value("pf_aspect") if aspect is None else aspect
    return (T / T0) ** (2.0 / 3.0) * (a / value("pf_aspect")) ** 2.5


def rel_viscosity(phi: float, law: str = "thomas", phi_max: float | None = None) -> float:
    """Viscosity of a suspension of cells over that of the medium, at high shear, at a volume fraction `phi` of cells.
    'thomas':  1 + 2.5 phi + 10.05 phi^2 + 0.00273 exp(16.6 phi), the equation Clincke et al. 2013 used for CHO and the one the
               model uses everywhere (gas_exchange.viscosity).
    'krieger': (1 - phi/phi_max)^(-2.5 phi_max), Krieger and Dougherty; Iordan et al. 2007 fitted it to CHO at 1,000 per second
               with phi_max = 0.65 (`tc_phi_max`). Infinite at phi_max. (Moved here from thick_culture.py, 2026-11-20.)"""
    if law == "thomas":
        return 1.0 + 2.5 * phi + 10.05 * phi ** 2 + 0.00273 * float(np.exp(16.6 * phi))
    if law == "krieger":
        pm = value("tc_phi_max") if phi_max is None else phi_max
        return float("inf") if phi >= pm else (1.0 - phi / pm) ** (-2.5 * pm)
    raise ValueError(f"unknown viscosity law {law!r}")


def apparent_rel_viscosity(x: float, law: str = "thomas", thin: float | None = None) -> float:
    """Viscosity the impeller and the bubbles see at x g of wet cells a litre, over the medium's: the high-shear value, with its
    excess over the medium raised by `thin` (`tc_thin`, 1.33: CHO at 1e8 cells/mL is 2.4 mPa s at the shear of 50 rpm in a
    250 mL tank against 1.8 at 45 per second). The volume fraction is x / (cell density x 1000)."""
    thin = value("tc_thin") if thin is None else thin
    phi = x / (value("pf_cell_density") * 1000.0)
    return 1.0 + (rel_viscosity(phi, law) - 1.0) * thin


def kla_factor(x: float, law: str = "thomas", thin: float | None = None, exponent: float | None = None) -> float:
    """kLa of a culture at x g/L over the kLa in medium: the apparent viscosity to the power -`tc_kla_exp` (0.40: Yagi and
    Yoshida's net viscosity exponent, -1.5 + 0.5 + 0.6, in stirred tanks)."""
    n = value("tc_kla_exp") if exponent is None else exponent
    if n == 0.0:
        return 1.0
    return apparent_rel_viscosity(x, law, thin) ** (-n)


O2_HALVINGS = 40                   # oxygen_limit's bisection; the page's fxO2Visc uses the same count
_O2_MEMO: dict = {}


def oxygen_limit(x_base: float, law: str = "thomas", thin: float | None = None, exponent: float | None = None) -> float:
    """Density (g/L) a sparger can feed once viscosity is counted. `x_base` is the density the oxygen supply gives with the kLa
    of medium. Oxygen use rises in proportion to density and kLa falls with it, so the limit is the fixed point
    x = x_base x kla_factor(x), found by bisection (40 halvings, to about 1e-12 of x_base; 60 until 2026-11-25, finer than any
    figure can show; the page's fxO2Visc mirrors it). Infinite stays infinite."""
    if not np.isfinite(x_base):
        return float("inf")
    n = value("tc_kla_exp") if exponent is None else exponent
    if n == 0.0:
        return float(x_base)
    # memoised (2026-11-25: 91% of calls repeat one exactly, and this was a third of the engine's time): the key holds every
    # input the fixed point reads, so a changed input is a new key, never a stale value
    key = (float(x_base), law, thin, n, value("tc_thin"), value("pf_cell_density"), value("tc_phi_max"))
    hit = _O2_MEMO.get(key)
    if hit is not None:
        return hit
    if len(_O2_MEMO) > 500_000:
        _O2_MEMO.clear()
    lo, hi = 0.0, float(x_base)
    for _ in range(O2_HALVINGS):
        mid = 0.5 * (lo + hi)
        if mid > x_base * kla_factor(mid, law, thin, n):
            hi = mid
        else:
            lo = mid
    _O2_MEMO[key] = out = 0.5 * (lo + hi)
    return out


def _kla_exponent(viscous_kla) -> float:
    """explore's `viscous_kla`: True = the datasheet's tc_kla_exp, False = 0 (Humbird: no effect), a number = that exponent."""
    if viscous_kla is True:
        return value("tc_kla_exp")
    if viscous_kla is False or viscous_kla is None:
        return 0.0
    return float(viscous_kla)


def density(cells: Cells, otr: float, washed: bool) -> float:
    """Highest cell density (g wet/L) the reactor supports: oxygen, viscosity and, if waste is not
    washed out, the ammonia/CO2 limit."""
    x = min(value("pf_x_visc"), otr / cells.qo2)
    return x if washed else min(x, waste_cap(cells))


def batch_slowdown(end_x: float, doublings: float, half_x: float | None = None, steps: int = 40) -> float:
    """How much longer a culture that is not washed out takes to grow its last `doublings`, against growth at the switch's
    speed, when its waste builds up with its cells and ends at `end_x` times the level a perfusion tank is held at
    (2026-11-19 restructure). Waste concentration is in proportion to density, so at s = ln(x / x_end) it is end_x e^s.
    Growth is the switch's speed up to the steady-state level (the model charges perfusion nothing there) and above it falls as
    (1 + 1/9) / (1 + (c / K)^h): a 10% loss at the level and 50% at K = `half_x` times it (pf_batch_half_x), h = ln 9 / ln K.
    Midpoint rule in ln x; page JS mirrors it (fxBatchSlow)."""
    if end_x <= 1.0 or doublings <= 0:
        return 1.0
    K = value("pf_batch_half_x") if half_x is None else half_x
    h = float(np.log(9.0) / np.log(K))
    span = doublings * LN2
    tot = 0.0
    for i in range(steps):
        c = end_x * float(np.exp(-span * (i + 0.5) / steps))        # waste level / steady-state level
        tot += 1.0 if c <= 1.0 else (1.0 + (c / K) ** h) / (1.0 + 1.0 / 9.0)
    return tot / steps


def glucose_balance(o2_kg: float, nh3_kg: float, lac_yield: float, fat_fed: float = 0.0) -> float:
    """Glucose a kilo of wet cells takes up, mol, from what it builds, burns and ferments (audit 2026-11-19):
        G = [anabolic x (1 - 0.75 fat_fed) + (O2 - 2.25 NH3) / 6] / (1 - Y / 2)
    anabolic: glucose built into lipid, carbohydrate and nucleotides (pf_glc_anabolic; three-quarters of it is lipid);
    O2 / 6: glucose burned for the oxygen the cell uses, less the part burned from amino acids (2.25 O2 per NH3 released);
    Y: mol lactate per mol of ALL glucose taken up (two lactate per glucose fermented). Reproduces Humbird's enhanced cell."""
    burned = max(0.0, o2_kg - 2.25 * nh3_kg) / 6.0
    return (value("pf_glc_anabolic") * (1.0 - 0.75 * fat_fed) + burned) / max(0.05, 1.0 - lac_yield / 2.0)


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


def humbird_fedbatch_output() -> float:
    """Tonnes of wet cells a year per m3 of production tank in Humbird's fed-batch plant, from his tables: 6.8 kTA from 24 tanks
    of 20 m3 (Tables 4.1, 4.7) = 14.2. His crew, his utilities and his medium preparation equipment are for this output.
    (output_per_m3(GOOD_CELLS, "fedbatch") gives 14.5: a 58-hour cycle at a nominal 120 g/L; back-test 2026-11-20.)"""
    return value("humbird_output_fedbatch") / (value("pi_n_tanks") * value("pi_tank_m3")) / 1000.0


_RATIOS: dict = {}
_PI_NAMES: list = [0, ()]          # (registry size when listed, the pi_ input names): the cache keys below read only these


def _pi_values() -> tuple:
    """The values of the pi_ inputs (the plant's items), in name order: the key of the plant's memos. The names are listed once
    (2026-11-25: listing them on every call, by sorting and scanning the whole registry, was a third of the engine's time), and
    again only if the registry grows."""
    import inputs as I
    if _PI_NAMES[0] != len(I.REGISTRY):
        _PI_NAMES[0], _PI_NAMES[1] = len(I.REGISTRY), tuple(sorted(k for k in I.REGISTRY if k.startswith("pi_")))
    return tuple((k, value(k)) for k in _PI_NAMES[1])


def plant_ratios(choices: dict | None = None) -> tuple:
    """(vessel, buildings, dedicated medium) of a plant built item by item against Humbird's: its production tanks' cost per m3
    over his, its buildings (hall, labs, support) over his, and whether each tank has its own makeup tanks and filter housings
    (plant_items 'medium' = 'dedicated'). None is Humbird's plant: (1, 1, True). Memoised on the pi_ inputs."""
    import inputs as I
    import plant_items as PI
    c = PI.choices_for("humbird", **(choices or {}))
    key = (tuple(sorted(c.items())), _pi_values())
    if key not in _RATIOS:
        o, h = PI.options(), PI.humbird()
        bh = h["hall"] + h["labs"] + h["support"]
        _RATIOS[key] = (o["vessels"][c["vessels"]][0] / h["vessels"],
                        (o["hall"][c["hall"]][0] + o["labs"][c["labs"]][0] + o["support"][c["support"]][0]) / bh,
                        c["medium"] == "dedicated")
    return _RATIOS[key]


def tank_items(vessel_m3: float, perfusion: bool = False, choices: dict | None = None) -> dict:
    """What the production tanks bring with them, $k per m3 of production tank (2018 dollars, total investment), in Humbird's
    accounting (2026-11-20): the tank itself (Eq. 3.1, $30.7k x V + $800k installed, times 1.2556 for minor equipment and its
    installation), its makeup tanks and filter housings (bare, times 2.5556; fed-batch three makeup tanks and $62k of housings
    per tank, perfusion two and $28k: pi_makeup_*, pi_filters_*), and the buildings ($74.4k per m3 + $533k per tank of direct
    cost, a fit to his two plants: pi_bldg_*), all times 1.84 for engineering, construction, fees and contingency. A plant
    built item by item (`choices`, plant_items) scales the tank and the buildings by its own items against his, and has no
    makeup tanks or housings per tank if its medium line is shared. Seed trains, fill tanks, sterilisers, centrifuges and the
    utilities outside the process are not here: they stay in the plant's cost per m3 of tank (and the medium preparation
    grows with the medium a case passes: explore's medium_prep_capex). Cell-retention devices are priced by explore itself."""
    import plant_items as PI
    vr, br, dedicated = plant_ratios(choices)
    ind = PI.indirect()
    bio = PI._bioreactor_direct(1.0)                                   # 1.2556
    eqp = PI._equipment_direct(1.0)                                    # 2.5556
    vessel = ind * bio * PI.eq31(vessel_m3) / vessel_m3 * vr
    per_tank = (value("pi_makeup_pf_tank") + value("pi_filters_pf_tank")) if perfusion else \
        (value("pi_makeup_fb_tank") + value("pi_filters_fb_tank"))
    items = ind * eqp * per_tank / vessel_m3 if dedicated else 0.0
    bldg = ind * (value("pi_bldg_per_m3") + value("pi_bldg_per_tank") / vessel_m3) * br
    return {"vessel": vessel, "items": items, "buildings": bldg, "total": vessel + items + bldg}


# the shares of the gas through a fine-bubble sparger that explore(spargers=2) tries (2026-11-21): fine near 0, where the cost of
# the cells it kills is small, then coarser; a share above what lifts oxygen to the next limit is cut to that share
MICRO_GRID = (0.0, 0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02, 0.03, 0.04, 0.05, 0.065, 0.08, 0.1, 0.13, 0.16, 0.2, 0.25, 0.3,
              0.4, 0.5, 0.65, 0.8, 1.0)
_BPOWER: dict = {}


def building_power_parts() -> dict:
    """{item: {option: W}}: the electric load of the buildings of Humbird's fed-batch plant for each building option of
    plant_items (hall, labs, support), from his Table 3.2 (W per m2-level) and his floor areas (Table 4.2: the hall's and the
    labs' area are their cost over his rate per m2). A hall of another class has his hall's area at its own load; a yeast
    plant's hall is mostly outdoors and its labs and support are not costed apart, so they draw nothing. Memoised on the inputs."""
    import inputs as I
    key = _pi_values()
    if key not in _BPOWER:
        hall_m2 = value("pi_bldg_hall") * 1000.0 / value("pi_rate_class8")
        labs_m2 = (value("pi_bldg_cell_lab") + value("pi_bldg_qc_lab")) * 1000.0 / value("pi_rate_class6")
        _BPOWER.clear()
        _BPOWER[key] = {
            "hall": {"class8": hall_m2 * value("pi_w_class8"), "sanitary": hall_m2 * value("pi_w_sanitary"),
                     "shed": hall_m2 * value("pi_w_warehouse"), "yeast": 0.0},
            "labs": {"class6": labs_m2 * value("pi_w_class6"), "yeast": 0.0},
            "support": {"humbird": value("pi_w_support") * 1000.0, "yeast": 0.0}}
    return _BPOWER[key]


def building_power(vessel_m3: float = 20.0, choices: dict | None = None, sized: bool = True) -> float:
    """The power a plant's buildings draw per m3 of production tank, as a multiple of Humbird's fed-batch plant's (2026-11-21;
    explore() charges pf_util_time times it). His 'facility power' is floor area times the load of each class (Table 3.2), so
    it follows the floor: per m3 of tank it scales with the buildings' cost per m3 at this tank size (tank_items: $74.4k per
    m3 + $533k per tank), and with the class of each building (`choices`, plant_items options; a sanitary hall draws 50 W per
    m2 against the clean room's 410). His perfusion plant of 2 m3 tanks pays $13.1k a year per m3 of tank for it, 3.2 times
    his fed-batch plant's $4.07k; this rule gives 3.4 times. `sized=False` (a plant class priced as quoted): no size term."""
    import plant_items as PI
    parts = building_power_parts()
    c = PI.choices_for("humbird", **(choices or {}))
    h = PI.choices_for("humbird")
    p = sum(parts[k][c[k]] for k in ("hall", "labs", "support")) / sum(parts[k][h[k]] for k in ("hall", "labs", "support"))
    if sized:
        b = lambda v: value("pi_bldg_per_m3") + value("pi_bldg_per_tank") / v
        p *= b(vessel_m3) / b(value("pi_tank_m3"))
    return p


def crew_multiplier(vessel_m3: float, perfusion: bool) -> float:
    """The crew per m3 of tank as a multiple of Humbird's fed-batch crew per m3 at 20 m3 (2026-11-21). He counts most of the
    hours per bioreactor (Sect. 3.3; Tables 4.5 and 4.12), so many small tanks need more staff per m3 than few large ones.
    A tank that is not run continuously in perfusion: (1 - s) + s x 20 / size, s = pf_labour_tank_share (his batch workers'
    share of his fed-batch crew). A tank run continuously in perfusion: pf_labour_perfusion_x (at 20 m3) plus
    pf_labour_tank_perfusion staff per tank, counted against the 20 m3 tank's share of them."""
    v0 = value("pi_tank_m3")
    if perfusion:
        crew_m3 = value("pf_labour_staff_fedbatch") / (value("pi_n_tanks") * v0)          # staff per m3 of his fed-batch plant
        return value("pf_labour_perfusion_x") + value("pf_labour_tank_perfusion") / crew_m3 * (1.0 / vessel_m3 - 1.0 / v0)
    s = value("pf_labour_tank_share")
    return (1.0 - s) + s * v0 / vessel_m3


def capex_at_size(capex_20m3: float, vessel_m3: float, perfusion: bool = False, choices: dict | None = None,
                  vessel_ratio: float = 1.0) -> float:
    """A sterile plant's capital per m3 of production tank (2018 dollars) at another tank size or way of running, from its
    figure for 20 m3 tanks in fed-batch: plus the change in what the tanks bring with them (tank_items), the tank itself at
    `vessel_ratio` times a packaged stirred tank's price (another vessel type). Until 2026-11-20 only the bioreactor share
    (pf_bioreactor_capex_share) was scaled, with Eq. 3.1."""
    a, b = tank_items(vessel_m3, perfusion, choices), tank_items(20.0, False, choices)
    return capex_20m3 + a["vessel"] * vessel_ratio + a["items"] + a["buildings"] - b["total"]


def capex_at_size_old(capex_20m3: float, vessel_m3: float) -> float:
    """The rule before 2026-11-20 (explore's per_tank=False): only the bioreactor share scales, with Eq. 3.1."""
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


# Species presets for the cell levers: (label, doubling time h, wet mass pg, litres of medium per kg if
# reported, CO2 tolerance in mbar if it differs from the default, the plausible range of that tolerance,
# other panel settings the preset fixes (a dict of explore() arguments, or None for a cells-only preset),
# what the numbers are and how good they are). Sources and access levels:
# research_notes/species_cell_parameters.md and research_notes/fish_cell_co2_ph.md.
SPECIES_PRESETS = {
    "model": ("Humbird's model cell", 24.0, 3000.0, None, None, (100.0, 200.0), None,
              "The efficient cell every case on this page assumes [2]. No meat cell line has been shown to match it."),
    "chicken": ("Chicken, as reported in perfusion", 48.0, 1400.0, 30.5, None, (100.0, 200.0), None,
                "SuperMeat's 2024 report [1] gives half a doubling a day in perfusion, 1.0 to 1.75 ng per cell and 30.5 "
                "litres of medium per kilo. The preset sets the waste lever to match. Put the medium price at $0.50 for the reported "
                "cost. Chicken "
                "fibroblasts double in about 20 hours when grown on a surface. Another measured run in "
                "animal-free medium took 61 hours [20]."),
    "cattle": ("Cattle, serum-free", 39.0, 3000.0, None, None, (100.0, 200.0), None,
               "Primary bovine muscle stem cells in serum-free medium on a surface doubled in 39 hours on average "
               "(Stout et al. 2022). Immortalised lines (Stout 2023) reach 15 to 17 hours with serum. No cell mass was found, so the "
               "preset uses the model cell's mass. Nobody has published a suspension culture at density."),
    "fish": ("Fish (Atlantic mackerel)", 24.0, 2500.0, None, 50.0, (10.0, 100.0), None,
             "The Mack1 line doubles in 24 hours at 27 °C. Its cells are 16.8 µm across, and it grows on a surface with 20% serum (Saad et al. "
             "2023). Many fish lines take two days or more. <b>CO\u2082:</b> the preset sets it to 50 mbar, half the default. Fish "
             "live with about 2 to 4 mbar in their blood, against about 50 in mammals, and fish farms keep it "
             "under 5 to 10. Salmon and trout cell lines do grow in a medium that implies about 40 to 50 mbar. "
             "Nobody has measured how fish cells grow against CO\u2082, so the range is 10 to 100."),
    "shrimp": ("Shrimp (hypothetical: no cell line exists)", 24.0, 2500.0, None, 50.0, (15.0, 100.0), None,
               "No shrimp or other crustacean cell culture that keeps dividing exists, so this is not a cost "
               "estimate. The preset gives shrimp the fish cell's size and speed [assumed]. <b>CO\u2082:</b> 50 mbar, which is a "
               "judgement, with a range of 15 to 100. Shrimp carry only about 4 mbar in their blood, and farms keep them "
               "under about 5. Fish carry as little, but their cells grow at 40 to 50. Insect cells, the "
               "nearest relatives with data, show no slowdown up to 49. The limits for whole animals reflect gills "
               "and blood pigment, not cells. Shrimp cells have only ever been cultured in open air, so there "
               "is no direct evidence. A tonne of shrimp is tens of thousands of animals, which is why the "
               "case is worth showing."),
    "insect": ("Insect (Sf9), for reference", 23.0, 2200.0, None, 50.0, (50.0, 200.0), None,
               "Sf9 cells double in about 23 hours at 27 °C. They are grown in suspension in tanks of up to 21,000 litres for vaccines "
               "(Ashizawa et al. 2022). Measured oxygen uptake per gram is close to the model's. <b>CO\u2082:</b> "
               "Vajrala and Murhammer (2016) measured no slowdown up to 49 mbar, a doubling time of 32 hours at "
               "97 mbar and 38 hours at 196. The preset uses 50 mbar, where the 23 hours holds."),
    "vow": ("A working plant: Vow's 20,000-litre tank", 24.0, 3000.0, None, None, (100.0, 200.0),
            {"mode": "filldraw", "plant": "microbial", "charge": 0.236, "waste": 0.205},
            "This is the one plant that grows animal cells at this size (quail cells, in Sydney). It is a food-grade stirred tank "
            "built in-house, with no clean room. The tank is emptied or partly drained and refilled, and nothing holds the "
            "cells back (GFI's 2026 industry report and the company's food-standards filing). Its stated target "
            "is 130 tonnes a year from 35,000 litres. That is 3.7 to 6.5 tonnes per m\u00b3 a year, which implies about "
            "27 g of cells per litre. The company publishes no cell traits, plant cost or loss rates, so this "
            "preset is a reconstruction. It sets the waste lever so that the tank holds 27 g per litre, prices the plant like a "
            "yeast plant (its vessel is said to have cost under $50k per m\u00b3), and uses first-plant financing. "
            "To return to Humbird's optimistic design, choose perfusion and the food-grade plant again."),
}
SPECIES_MISSING = ""


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


# Settings that restore what earlier notes were computed with, for the tests that check those notes' figures:
# before the filter loop became the default (2026-11-15), and before the protectant, the antifoam and the yeast-style
# plant's oxygen were counted (2026-11-15, late). Use with _inputs_set / retention._with. Since 2026-11-16 only parts of
# tests/test_gas_exchange.py and tests/test_plant_items.py still use them; the other side studies run on the current model.
BEFORE_PROTECTANT = {"pf_antifoam_otr": 1.0, "pf_protectant_dose": 0.0, "pf_o2_microbial": 0.0,
                     "sc_do_scenarios": 0.0}    # and before the scenarios held dissolved oxygen low (2026-11-16)
BEFORE_FILTER_LOOP = {"rt_tff_default": 0.0, **BEFORE_PROTECTANT}


def _inputs_set(settings: dict):
    """Context manager: run with some inputs set to other values, and restore them after (as retention._with)."""
    import contextlib
    from dataclasses import replace
    import inputs as I

    @contextlib.contextmanager
    def cm():
        old = {k: I.REGISTRY[k] for k in settings}
        try:
            for k, v in settings.items():
                I.REGISTRY[k] = replace(I.REGISTRY[k], value=v)
            yield
        finally:
            I.REGISTRY.update(old)
    return cm()


CLEAN_NAMES = ("none", "exchanger", "electrodialysis", "dialysis")


def clean_route(clean) -> dict | None:
    """The numbers of a route that cleans the medium so it can be used again, as explore() takes them (`clean`): None for
    "none"; {"sorbent": True} for the ammonium exchanger on the permeate (explore's `sorbent` lever, priced by its sorbent);
    the side study's own inputs (medium_reuse.routes(), the mr_ inputs) for electrodialysis of the permeate and for dialysis
    across the culture with the dialysate cleaned and reused, its exchange membrane at the cost of the cell filter. A dict
    is taken as it is. Read at call time, so a test can move an mr_ input."""
    if clean is None or clean == "none":
        return None
    if isinstance(clean, dict):
        return clean
    if clean == "exchanger":
        return {"sorbent": True}
    if clean == "electrodialysis":
        return {"nh3": value("mr_ed_nh3"), "lac": value("mr_ed_lac"), "device_l": value("mr_ed_cost_l")}
    if clean == "dialysis":
        d = value("mr_dial_removal")
        return {"nh3": d, "lac": d, "other": d, "in_tank": True, "exchange_membrane": 1.0,
                "dialysate_l": value("mr_dialysate_makeup") * value("mr_dialysate_l"),      # basal medium bought, per litre cleaned
                "device_l": value("mr_dialysate_l") * value("mr_ed_cost_l")}               # cleaning the dialysate, per litre cleaned
    raise KeyError(f"no cleaning route {clean!r}")


def clean_loops(terms: dict, route: dict) -> list:
    """The litres cleaned per kilo of cells harvested that the search for the cheapest tries: every 0.1 litre from none up to
    the litres that take out all of the waste the route handles (`terms`: explore's `medium_terms` with nothing cleaned)."""
    takes = (("ammonia", route.get("nh3", 0.0)), ("lactate", route.get("lac", 0.0)), ("least flow", route.get("other", 0.0)))
    top = max([terms[n] / sh for n, sh in takes if sh > 0] or [0.0])
    return [i * 0.1 for i in range(int(top * 10) + 2)]


def explore(doubling_h: float = 24.0, mass_pg: float = 3000.0, vessel_m3: float = 20.0,
            plant: str = "sanitary", mode: str = "perfusion", charge: float | None = None,
            uptime: float | None = None, maintenance_share: float | None = None,
            capex_x: float = 1.0, retention: float | None = None, x_scale: float = 1.0,
            hazard: float = 0.0, run_days: float | None = None, restart_fail_days: float | None = None,
            medium_l: float | None = None, medium_price: float = 0.15, growth_factors: float = 0.0, gf_in_medium: float = 0.0,
            cell_share: float = 1.0, waste: float = 0.0, nh3_limit: float | None = None,
            pco2_mbar: float | None = None, gas_velocity: float | None = None, aspect: float | None = None,
            osm_limit: float | None = None, ph: float | None = None, min_perfusion: float | None = None,
            capex_2018: float | None = None, extra_opex: float = 0.0, start_fail: float = 0.0,
            salvage: float = 0.0, items: dict | None = None,
            nh3_kg: float | None = None, lac_yield: float | None = None, glc_kg: float | None = None,
            glc_balance: bool = False,
            sorbent: float = 0.0, sorbent_q: float | None = None, sorbent_price: float | None = None,
            sorbent_cycles: float | None = None, column: str = "none", p_top_barg: float | None = None,
            col_pout: float | None = None, rq: float | None = None, fat_fed: float = 0.0,
            fat_price: float | None = None, do_mmol: float | None = None, shape_cost: bool = True,
            vm: dict | None = None, membrane_life: float | None = None, flux: float | None = None,
            strip_eff: float | None = None, antifoam_otr: float | None = None,
            protectant_price: float | None = None, lac_limit: float | None = None, kill: float | None = None,
            wash_price: float | None = None, clean: str | dict = "none", clean_share: float | None = None,
            clean_loop: float | None = None, x_visc: float | None = None,
            membrane_price: float | None = None, membrane_hw: float | None = None, viscous_kla=True,
            mature_h: float | None = None, per_tank: bool = True, spargers: int | None = None,
            micro_share: float | None = None, col_on_loop: bool | None = None, _search: bool = True) -> dict:
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
      * perfusion needs a device to hold cells back. By default it is a TFF hollow-fibre loop sized on the cell-free
        liquid it must clear (medium per kg less what the bleed of cells carries out, 1000 / density): membrane area =
        that flow / `flux` (rt_flux_lmh), hardware rt_tff_hw per m2 times rt_install, and membranes at rt_membrane_price
        per m2 over `membrane_life` litres per m2 (retention.py, research_notes/retention_devices.md). A number for
        `retention` instead charges that much capital per m3 of tank and no membranes (the old hoped-for device was
        pf_capex_retention). Fill-and-draw needs no device, but
        waste then caps the density and the tank averages f/ln(1/(1-f)) of its peak output.

      * a run ends at its planned length or when it is contaminated (a constant chance per day, `hazard`),
        then the tank is cleaned and regrown; a contaminated run also loses the cells in the tank, less the
        share `salvage` that can still be harvested and sold. A share `start_fail` of starts is contaminated
        from the outset (through the seed or the start-up): it costs the seed and the days until it shows;
      * `items` builds the plant item by item in place of a plant class: a dict of plant_items options
        ({"hall": "shed", "oxygen": "bought", ...}; items left out are Humbird's). It sets the capital per
        m3 (Humbird's 2018 dollars, escalated and sized like his plant) and adds the cost of bought oxygen.
        `capex_2018` and `extra_opex` set the same two numbers directly;
      * the litres of medium per kg follow from the waste the cells make (`waste`: 0 = Humbird's enhanced
        cells, 1 = ordinary cells): in perfusion enough liquid must pass to wash ammonia and lactate out;
        in a drained-and-refilled tank waste caps the density instead. The medium costs litres x price,
        but never less than the nutrients the cells must eat (at the default $0.15/L the two meet);
        growth factors can be added at Humbird's large-scale price, scaled with the litres of medium;
      * the product can be a blend: `cell_share` of cells, the rest plant ingredients.

      * salt strength: holding the pH against dissolved CO2 takes bicarbonate, and lactate comes with its
        base, so both add salt (2 mOsm per mmol/L). In perfusion the lactate the culture may hold is what
        the salt limit leaves after the bicarbonate, which sets the litres needed to wash it out. If the
        limit binds, the tank is run at the CO2 level, at or below what the cells tolerate, that costs
        least (a search over 60 levels);
      * the least medium flow a cell needs for everything else (other by-products, nutrients that run
        out): litres per kg = that flow / growth rate, so slow cells need more.

      Tricks (sized in gas_exchange.py and research_notes/gas_exchange_study.md, waste_tricks_sizing.md):
      * `column`: a packed stripping column on a pumped loop takes the CO2 the sparger cannot ("co2", air
        sweep), or also makes up the oxygen ("o2_closed", oxygen sweep recycled through a lime scrubber); its
        capital, pumping, oxygen and lime are added. `col_pout` is the CO2 the culture leaves it at (mbar).
      * `p_top_barg`: pressure at the top of the tank (default Humbird's 0.33 bar gauge); oxygen transfer, and
        with it the mixing limit, scale with the driving force; CO2 removal does not change.
      * `nh3_kg` (mol ammonia per kg wet cells) and `lac_yield` x `glc_kg` (mol lactate per mol glucose x mol
        glucose per kg) set the two wastes explicitly, as measured, with no scaling; left unset, `waste` sets
        both as before (0 = Humbird's enhanced cells, 1 = ordinary cells). With `glc_balance` (the scenarios) and no
        `glc_kg`, glucose per kg comes from `glucose_balance` and `lac_yield` is per mol of all the glucose taken up.
      * `sorbent` (the filter still passes the liquid the exchanger treats, so only medium, growth factors and
        protectant are saved, not membranes; corrected 2026-11-16, medium_reuse.py): the share of the ammonium taken out
        of the cell-free permeate by an exchanger before it
        returns, at `sorbent_q` mmol/g, `sorbent_price` $/kg and `sorbent_cycles` uses; the sodium it gives back
        stays in the medium and counts towards the salt limit.
      Cell side:
      * `fat_fed`: the share of the cells' lipid taken from the feed instead of made from glucose. Making
        lipid from glucose releases CO2 without using oxygen (Humbird's Reaction 2.2: 0.090 of the 0.455 mol
        CO2 per mol of dry cell mass), so CO2 made per oxygen used (`rq`, default 1.204) falls to 0.966 when
        all of it is fed; the fat is bought at `fat_price`. `rq` can also be set directly.
      * `aspect` other than the model's 1.6 also changes the plant's cost: more steel and floor for a squat tank,
        less for a tall one (gas_exchange.shape_capex_factor); `shape_cost=False` leaves it out.
      * `do_mmol`: dissolved oxygen the tank is held at. Humbird's 29 mmol/L/h implies about 0.28 mmol/L;
        a lower setpoint widens the driving force for oxygen (and, by the mixing rule, the mixing limit).
    The result carries every cap (`limits`, g/L), what sets the litres of medium (`medium_terms`, L/kg), and
    the oxygen and CO2 per kg of cells (`o2_kg`, split into growth and upkeep; `co2_kg`).

      Vessel and mode (vessels.py): `vm`, a dict of the numbers that make a vessel type and an operating mode. Left out,
      the case is a stirred tank in `mode` 'perfusion' or 'filldraw', as before. Its keys are listed in `vessels.VM_KEYS`.
      For the vessel: the oxygen-transfer multiplier, whether oxygen, mixing and CO2 follow the sparged-tank rules or are
      replaced by a density cap of the vessel's own, its cost relative to a stirred tank, what it throws away each run,
      how much of the grown cells it gives back, and its working volume. For the mode: whether waste is washed out,
      whether the tank is run in cycles (batch, fed-batch) or continuously, the length of a cycle or a run, and how fast
      the culture is diluted (chemostat).

      Gas-side uncertainties (research_notes/gas_flow_cap.md, follow-ups 2 and 3): `strip_eff`, how close the exhaust gas
      comes to equilibrium with the liquid's CO2 (pf_co2_strip_eff, calibrated to Humbird at 0.96; 0.7 is the low end
      reported), used by the sparger and by the column's sparger share; `antifoam_otr`, the oxygen transfer left with
      antifoam present (pf_antifoam_otr; 1 = no effect, 0.5 = halved), applied to the sparger's oxygen only (the mixing
      rule is left as it is).
      The bubble protectant (poloxamer 188, research_notes/gas_flow_cap.md follow-up 1) is dissolved in the medium and
      leaves with every litre: pf_protectant_dose g/L x medium litres x price (`protectant_price`, default
      pf_protectant_price), in consumables, for every vessel that is sparged. Medium prices are taken to exclude it.
      A plant of the yeast-style class (`plant="microbial"`) has no oxygen unit in its price, so it buys its oxygen as
      a plant built item by item does (pi_o2_feed x pi_o2_price, `o2_bought` in the result).

      Since 2026-11-20 (research_notes/full_review_2026-11-19.md, section 2):
      * `lac_limit`: the lactate the cells tolerate, mmol/L (default Humbird's pf_lac_limit; the scenarios pass sc_lac_limit).
      * medium preparation: the plant's capital is Humbird's fed-batch plant, whose medium preparation and sterilising
        equipment (plant_items 'medium') is sized for pf_medium_prep_l_kg litres per kilo at his fed-batch output. A case that
        passes more medium per m3 of tank a year pays for more of it: the plant's own medium item x (ratio ^
        pf_medium_prep_exp - 1), never less than nothing (`medium_prep_capex`, $k per m3, added like the filter loop's).
      * bubble deaths: cells die at `kill` (default ge_kill_protected, L of culture per L of gas) x the gas passed per litre of
        culture, in every tank whose cells meet sparged gas. The dead cells lyse and are not harvested: the share
        `death_share` = death rate / growth rate (at most 0.5) comes off the output, and every cost per kilo and the litres
        of medium per kilo are per kilo harvested (divided by 1 - death_share: the dead cells used their medium too).
        The gas passed is the gas the culture needs from its sparger (corrected 2026-11-20, second pass): the gas-velocity cap
        x min(1, density / the smaller of the two densities the SPARGER ALONE could serve, for oxygen and for CO2). A column
        does not change those two: it is sized for the CO2 (and, with an oxygen sweep, the oxygen) the sparger at its cap
        cannot handle (gas_exchange.column_design), so a column that strips nothing leaves the gas, and the deaths, as they
        were, and a culture beyond what the sparger alone could serve bubbles the full cap whatever the column. A vessel whose
        sparger passes oxygen or CO2 better (`otr_mult`, `co2_mult`) needs that much less gas. A vessel that sparges nothing
        through the culture (`o2_gas` and `co2_gas` both off) has no bubble deaths and buys no protectant. `gas_used`, m/s.
        `vm["gas_away"]` (m/s; the bubble cage): that part of the gas velocity is sparged where there are no cells. It counts
        for oxygen and CO2 as the rest does, but only the remainder kills cells (`gas_cells`, m/s, in the same proportion).
      * labour: Humbird's fed-batch crew per m3 of tank (pf_labour at his fed-batch output), times pf_labour_perfusion_x for a
        tank in perfusion (washed, run continuously). pf_labour_perfusion, his perfusion design's own figure, is a cross-check.
      * harvest: pf_harvest_recovery of the cells grown are recovered, times a vessel's own `recovery` (cells left on a
        support). The cells lost were grown with their share of medium, membranes and everything else, so both are treated as
        the death share is: every cost per kilo and the litres of medium per kilo are divided by them (a vessel's `recovery`
        scaled only the output until 2026-11-20, which left its medium and growth factors per kilo too low).
      * `x_visc`: the thickest culture the tank can stir, g/L (default pf_x_visc).
      * `membrane_price` ($ per m2, default rt_membrane_price) and `membrane_hw` ($k of hardware per m2, default rt_tff_hw):
        with `flux` and `membrane_life` they make the filter loop another membrane device (retention._MEMB: dialyser-grade
        fibres are flux rt_dial_flux, life rt_dial_life, price rt_dial_price, hardware rt_dial_hw), priced by the same lines.

      Cleaning and reusing the medium (medium_reuse.py, research_notes/medium_reuse.md; all off by default):
      * `wash_price` ($ a litre; None: every litre at `medium_price`): the litres that carry the nutrients (pf_medium_l_floor,
        'nutrients' in `medium_terms`) are charged at `medium_price` and the rest, which only wash waste out, at `wash_price`.
        The nutrient floor (what the cells eat, plus the growth factors inside a complete medium for every litre) still applies.
      * `clean`: a route that takes waste out of the medium so it can be used again: "none", "exchanger" (the ammonium
        exchanger on the permeate: the same calculation as `sorbent`), "electrodialysis" (of the permeate), "dialysis" (across
        the culture, the dialysate cleaned and reused) or a dict of a route's own numbers (medium_reuse.routes(): `nh3`,
        `lac`, `other` = share of each waste a litre cleaned gives up; `in_tank`; `gf_kept`; `device_l` $ per litre cleaned;
        `dialysate_l` litres of basal medium bought per litre cleaned; `exchange_membrane`, for a device across the culture,
        its membrane and hardware as a share of the cell filter's for the same litres). CLEAN_ROUTES holds the named ones.
        Each litre cleaned and returned stands in for that share of a litre thrown away, so the litres each waste asks for
        fall by litres cleaned x share. A device on the permeate does not lower the litres through the cell filter: what it
        cleans passes the filter too. Only a device across the culture does, and then its own membrane meets the cells.
        `clean_share` (0 to 1): the litres cleaned, as a share of the litres that would take out all of the waste the route
        handles (for the exchanger, the share of the ammonia taken). None: the litres that cost least, searched as the side
        study searches them (`clean_loops`: every 0.1 litre per kilo; the exchanger: its share in hundredths up to 90%).
        `clean_loop` sets the litres cleaned per kilo of cells grown directly (medium_reuse.cost).
        The result reports `clean_capex` ($k per m3 of tank: the membrane hardware the route adds, of which
        `clean_filter_capex` is inside `retention_capex`; `clean_capital` is its yearly charge per kilo, inside `capital`), `clean_opex` ($ per kilo: membranes for the litres cleaned, the
        device, the dialysate, the growth factors lost, the sorbent; of which `clean_filter_membranes` is inside `membranes`),
        `clean_loop` (L/kg cleaned and returned, per kilo harvested), and the litres of medium without the route (`medium_l_unclean`) beside `medium_l`.

      Since 2026-11-20 (additions brief):
      * `viscous_kla` (True: the exponent tc_kla_exp; False or 0: none, as Humbird; a number: that exponent): a thick culture takes
        up oxygen more slowly, kLa x (apparent viscosity / medium's)^-n, the apparent viscosity from Thomas's law with its excess
        raised by tc_thin; the oxygen limit is then the fixed point of `oxygen_limit`.
      * `per_tank` (default True): the plant's cost per m3 at another tank size or way of running is the 20 m3 fed-batch plant's
        plus the change in what each tank brings with it (`tank_items`: the tank, its makeup tanks and filter housings,
        buildings); False restores the bioreactor-share rule (capex_at_size_old).
      * `mature_h` (default pf_mature_h, 0): hours at no growth before harvest. A cycle lasts that much longer; a continuous tank
        holds its harvested stream in a maturation vessel (`mature_capex`, $k per m3 of tank); the medium the cells use while
        maturing, at their upkeep rate, is added to the litres (`mature_l`).

      Since 2026-11-21 (levers, off by default; research_notes/two_spargers_and_loop.md):
      * `spargers` (default ge_spargers, 1): 2 puts a fine-bubble sparger for oxygen beside the drilled pipe. A share `micro`
        of the gas cap goes through it, passing ge_micro_o2_x times the oxygen per litre of gas and killing ge_micro_kill_x
        times the cells; both kinds of bubble strip CO2 alike. The oxygen limit is the cap's oxygen x (m s^0.8 + (1-s)^0.8).
        `micro_share` sets the share (never more than lifts oxygen to the next limit: more would only kill more cells); left
        unset, the share that costs least on MICRO_GRID. The second sparger costs ge_sparger2_k per tank.
      * `col_on_loop` (default ge_col_on_loop, off): a CO2 column on a perfusion tank's filter loop shares its pump, so the
        column's own pump (gas_exchange.column_design, flow up to what the filter loop carries) is not bought.

    `uptime`, if given, overrides the run-length calculation. The defaults reproduce the floor tier at the
    mature-industry capital charge."""
    if strip_eff is not None or antifoam_otr is not None:   # run the case with those two inputs set, then restore them
        over = {k: v for k, v in (("pf_co2_strip_eff", strip_eff), ("pf_antifoam_otr", antifoam_otr)) if v is not None}
        kw = {k: v for k, v in locals().items() if k not in ("strip_eff", "antifoam_otr", "over")}
        with _inputs_set(over):
            return explore(**kw)
    vm = vm or {}
    mature_h = value("pf_mature_h") if mature_h is None else float(mature_h)
    washed = vm.get("washed", mode == "perfusion")     # is waste washed out (cells retained, or fixed to a support)?
    if clean != "none" and washed and medium_l is None and clean_share is None and clean_loop is None:
        # the litres cleaned that cost least, on the side study's own grids (medium_reuse.best, sorbent_best). None cleaned is
        # on both, so a route never costs more than no route
        kw = {k: v for k, v in locals().items() if k not in ("kw", "washed", "clean_share", "clean_loop")}
        if clean_route(clean).get("sorbent"):          # the exchanger: the share of the ammonia taken, 0 to 90% in hundredths
            return min((explore(clean_share=i / 100.0, **kw) for i in range(91)), key=lambda r: r["total"])
        r0 = explore(clean_share=0.0, **kw)            # the others: every 0.1 litre per kilo harvested, up to all it handles
        return min((explore(clean_loop=loop * r0["harvested_share"], **kw) if loop > 0 else r0
                    for loop in clean_loops(r0["medium_terms"], clean_route(clean))), key=lambda r: r["total"])
    if (spargers if spargers is not None else value("ge_spargers")) >= 1.5 and micro_share is None:
        # two spargers: the share of the gas through the fine-bubble one that costs least (MICRO_GRID; the page's floorExplore
        # searches the same grid)
        kw = {k: v for k, v in locals().items() if k not in ("kw", "washed", "micro_share")}
        return min((explore(micro_share=sh, **kw) for sh in MICRO_GRID), key=lambda r: r["total"])
    args = {k: v for k, v in locals().items() if k not in ("pco2_mbar", "_search", "washed")}
    cyclic = vm.get("kind") == "cyclic"                # cycles (batch, fed-batch) in place of a continuous run
    wv = vm.get("wv", value("pf_working_volume"))
    if vm.get("dil_frac"):                             # a chemostat grows at its dilution rate, below the maximum
        doubling_h = doubling_h / vm["dil_frac"]
    cells = Cells(mass_pg=mass_pg, doubling_h=doubling_h,
                  maintenance_share=value("pf_maintenance_share") if maintenance_share is None else maintenance_share)
    prep_item = None                                   # a plant class has no item breakdown: Humbird's item (set below)
    item_choices = {"hall": "sanitary"} if plant == "sanitary" else None   # the class's items, for what each tank brings (tank_items)
    if items is not None:                              # a plant built item by item
        import plant_items
        cap = plant_items.capital(**items)
        item_choices = dict(items)
        capex_2018, extra_opex, items = cap["total"], extra_opex + cap["extra_opex"], None
        prep_item = cap["items"]["medium"]             # this plant's own medium preparation equipment, $k per m3 (2018)
    elif plant == "microbial" and capex_2018 is None and vm.get("o2_gas", True) and value("pf_o2_microbial") >= 0.5:
        extra_opex = extra_opex + value("pi_o2_feed") * value("pi_o2_price")   # no oxygen unit in this class's price
    # the buildings whose power the plant pays (building_power): the yeast-style class is a yeast plant's buildings
    power_choices = item_choices
    if items is None and plant == "microbial" and capex_2018 is None:
        import plant_items
        power_choices = dict(plant_items.PLANTS["yeast"])
    # --- salt strength: how much lactate the culture may hold at this CO2 level and pH ----------------
    pco2_tol = value("pf_pco2_limit") if pco2_mbar is None else pco2_mbar
    osm_limit = value("pf_osm_limit") if osm_limit is None else osm_limit
    ph = value("pf_ph") if ph is None else ph
    hco3 = value("pf_co2_henry") * pco2_tol * 10.0 ** (ph - value("pf_pk1"))          # mmol/L at this CO2 and pH
    osm_co2 = 2.0 * max(0.0, hco3 - value("pf_hco3_base"))                             # mOsm/kg from added bicarbonate
    lac_lim = value("pf_lac_limit") if lac_limit is None else lac_limit                # the lactate the cells tolerate
    lac_room = min(lac_lim, max(1.0, (osm_limit - value("pf_osm_base") - osm_co2) / 2.0))
    if _search and washed and medium_l is None and lac_room < lac_lim:
        # the salt limit binds: run the tank at the CO2 level, up to what the cells tolerate, that costs least
        kw = dict(args, _search=False)
        best = None
        for i in range(60):
            r = explore(pco2_mbar=pco2_tol * (i + 1) / 60.0, **kw)
            if best is None or r["total"] < best["total"]:
                best = r
        return best
    charge = value("plant_charge_mature") if charge is None else charge
    lost = 0.0                                          # share of output lost with contaminated tanks
    run_frac = 1.0                                      # share of the planned run an average start completes (filter membranes)
    cycle_h = runs_yr = None
    def _cycle(slow: float = 1.0):
        # a cycle: n doublings from the seed to the final density, then the tank is emptied, cleaned and refilled.
        # A contamination loses the cycle's cells and adds a restart; the seed train for the next cycle is ready.
        # `slow`: the last doublings take longer when the batch ends above the steady-state waste level (batch_slowdown).
        grow_h = vm["n_doublings"] * cells.doubling_h * slow
        cycle_h = grow_h + vm["turnaround_h"] + mature_h      # maturation: hours in the tank at no growth before harvest
        ok = 1.0 - start_fail
        p_late = 0.0 if hazard <= 0 else ok * (1.0 - np.exp(-hazard * cycle_h / 24.0))
        p_fail = start_fail + p_late
        cycle_h += 24.0 * (p_fail * vm["restart_days"] + start_fail * value("ct_start_detect_days"))
        lost = min(0.9, p_late * (1.0 - salvage) + start_fail)
        return cycle_h, lost, grow_h / cycle_h, HOURS / cycle_h     # uptime: share of the year the tank grows cells
    if cyclic:
        cycle_h, lost, uptime, runs_yr = _cycle()
    elif uptime is None:
        clean_up = vm.get("clean_uptime", value("pf_uptime") if mode == "perfusion" else value("pf_uptime_realistic"))
        restart = value("pf_run_days") * (1.0 / clean_up - 1.0)            # days to clean, restart and regrow
        L = vm.get("run_days", value("pf_run_days")) if run_days is None else run_days
        ok = 1.0 - start_fail                                          # share of starts that are clean
        T = ok * (L if hazard <= 0 else (1.0 - np.exp(-hazard * L)) / hazard)   # expected productive days per start
        p_late = 0.0 if hazard <= 0 else ok * (1.0 - np.exp(-hazard * L))       # lost to a contamination in the run
        p_fail = start_fail + p_late
        # after a contamination the plant must sterilise and regrow a seed train, which can take longer
        down = restart if restart_fail_days is None else (1.0 - p_fail) * restart + p_fail * max(restart, restart_fail_days)
        down += start_fail * value("ct_start_detect_days")              # a bad start runs until it shows
        uptime = T / (T + down)
        runs_yr = 365.0 / (T + down)
        run_frac = T / L                                # a lost run throws its membranes away early (audit 2026-11-19)
        # a tankful per run lost in mid-run (less what is salvaged); a bad start loses its seed
        tankfuls = p_late * (1.0 - salvage) + start_fail * value("ct_seed_share")
        lost = min(0.9, tankfuls / (cells.mu * 24.0 * T))
    key, escalate, sized = PLANT_CLASSES[plant]
    capex = value(key) * (value("pf_capex_escalation") if escalate else 1.0)
    if capex_2018 is not None:                         # a plant built item by item (plant_items), or its cost given directly
        capex, sized = capex_2018 * value("pf_capex_escalation"), True
    tank_perf = washed and not cyclic                  # a tank run continuously in perfusion: its own makeup tanks and housings
    if per_tank and sized:
        # the 20 m3 fed-batch plant's cost plus the change in what each tank brings with it (2026-11-20): the tank (at
        # `capex_ratio` times a stirred tank's price for another vessel type), its makeup tanks and filter housings, buildings
        esc = value("pf_capex_escalation")
        capex = capex_at_size(capex / esc, vessel_m3, tank_perf, item_choices, vm.get("capex_ratio", 1.0)) * esc
    elif "capex_ratio" in vm:                          # another vessel type: its unit costs `capex_ratio` times a
        share = value("pf_bioreactor_capex_share")     # packaged stirred vessel of its size (bioreactor share only)
        size_f = (30.7 * vessel_m3 + 800.0) / vessel_m3 / ((30.7 * 20.0 + 800.0) / 20.0) if sized else 1.0
        capex *= (1.0 - share) + share * size_f * vm["capex_ratio"]
    elif sized:
        capex = capex_at_size_old(capex, vessel_m3)
    capex *= capex_x                                  # uncertainty in the plant estimate (floor_mc)
    if shape_cost and aspect is not None:              # a squatter tank needs more steel and floor (gas_exchange.py)
        from gas_exchange import shape_capex_factor
        capex *= shape_capex_factor(vessel_m3, aspect)["plant"]
    tff = washed and not vm.get("own_retention") and retention is None and value("rt_tff_default") >= 0.5
    if washed and not vm.get("own_retention") and not tff:                 # a flat charge in place of the TFF loop
        capex += value("pf_capex_retention") if retention is None else retention
    us = value("pf_gas_velocity") if gas_velocity is None else gas_velocity
    us_rel = us / value("pf_gas_velocity")
    f_p = 1.0
    if p_top_barg is not None or do_mmol is not None:  # oxygen driving force: pressure, setpoint (gas_exchange.py)
        from gas_exchange import headspace_pressure
        f_p = headspace_pressure(p_top_barg, vessel_m3, aspect, do_mmol)["otr_factor"]
    rq_eff = (value("pf_rq") - value("pf_rq_lipid") * fat_fed) if rq is None else rq
    x_o2 = value("pf_otr_cap") * us_rel ** 0.8 / cells.qo2 * f_p * value("pf_antifoam_otr")
    x_co2 = x_scale * co2_limited_density(cells, vessel_m3, pco2_mbar, gas_velocity, aspect, rq_eff)
    limits = {"oxygen supply": float("inf") if column == "o2_closed" else x_o2,
              "thickness of the culture": value("pf_x_visc") if x_visc is None else x_visc,
              "mixing": value("pf_otr_cap") / cells.qo2 * value("pf_mix_ratio_20m3") / mixing_time_ratio(vessel_m3, aspect) * f_p,
              "CO2 removal": float("inf") if column != "none" else x_co2}
    # the densities the sparger alone could serve at the gas cap, whatever a column adds: they set the gas the culture needs
    sparger = [x_o2 * vm.get("otr_mult", 1.0) if vm.get("o2_gas", True) else float("inf"),
               x_co2 * vm.get("co2_mult", 1.0) if vm.get("co2_gas", True) else float("inf")]
    if vm:                                             # the vessel's own gas exchange (vessels.py)
        limits["oxygen supply"] *= vm.get("otr_mult", 1.0)
        if not vm.get("mixing", True):
            limits["mixing"] = float("inf")
        if not vm.get("co2_gas", True):
            limits["CO2 removal"] = float("inf")
        limits["CO2 removal"] *= vm.get("co2_mult", 1.0)    # gas exchanged away from the cells (a bubble cage)
        if not vm.get("o2_gas", True):
            limits["oxygen supply"] = float("inf")
    # a thick culture takes up oxygen more slowly: kLa x (apparent viscosity / medium's)^-n, so the oxygen limit is a fixed point in
    # density (2026-11-20; thick_culture.py had it as a side study). Off (n = 0) in Humbird's like-for-like reproduction
    kexp = _kla_exponent(viscous_kla)
    if kexp > 0.0:
        limits["oxygen supply"] = oxygen_limit(limits["oxygen supply"], exponent=kexp)
        sparger[0] = oxygen_limit(sparger[0], exponent=kexp)
    if vm:
        for name, cap in vm.get("caps", {}).items():   # density caps of the vessel or the mode, g per litre of vessel
            limits[name] = cap
    burn = cells.o2_per_kg / GOOD_CELLS.o2_per_kg
    nh3_w, lac_w = waste_per_kg(cells, waste)
    nh3 = nh3_w if nh3_kg is None else nh3_kg          # mol per kg wet cells
    if lac_yield is None:
        lac = lac_w
    else:
        if glc_kg is None and glc_balance:      # glucose from what the cells build, burn and ferment (yield on total glucose)
            glc_kg = glucose_balance(cells.o2_per_kg * 1000.0 / 32.0, nh3, lac_yield, fat_fed)   # kg O2 -> mol
        lac = lac_yield * (value("pf_glc_kg") if glc_kg is None else glc_kg)
    flow = value("pf_min_perfusion") if min_perfusion is None else min_perfusion
    nh3_lim = value("pf_nh3_limit") if nh3_limit is None else nh3_limit
    steady = bool(vm.get("dil_frac"))                  # a chemostat sits at its density: no batch end above the level
    end_x = 1.0 if steady else value("pf_batch_end_x")
    if not washed:
        # A tank that is not washed out holds what its cells make: the litres a kilo leaves with (1000 / density) must hold its
        # ammonia and its lactate at the level the tank allows, the level perfusion is held to (the ammonia limit; the lactate
        # the salt leaves room for) times pf_batch_end_x for a batch that ends above it (2026-11-19 restructure; it was
        # Humbird's fed-batch 120 g/L scaled by the waste, which let the low-lactate example's fed-batch end at 7.8 mmol/L of ammonia).
        # mmol/L / (mol/kg) = g/L.
        limits["waste build-up"] = end_x * min(nh3_lim / max(nh3, 1e-12), lac_room / max(lac, 1e-12))
        # a drained-and-refilled tank gets 1/density litres per kg, so the least medium flow a cell needs caps the density:
        # 1000 / (flow / growth rate per day). Since 2026-11-21 times pf_batch_end_x, as ammonia and lactate are: in a tank that
        # is not washed out the least flow stands for by-products that build up (its other part, nutrients that run out, a
        # fed-batch's feeds supply), and a batch may end above the level perfusion holds them to, as it may for the other two
        # (research_notes/humbird_backtest.md, item 11). It capped Humbird's fed-batch at 92 g/L and added $6.4 to his design
        limits["other by-products"] = end_x * 1000.0 * cells.mu * 24.0 / flow
    # two spargers (2026-11-21): `micro_share` of the gas through the fine-bubble sparger, never more than lifts oxygen to the
    # next limit
    n_sparg = int(round(value("ge_spargers") if spargers is None else spargers))
    micro = 0.0
    if n_sparg >= 2 and (micro_share or 0.0) > 0.0 and vm.get("o2_gas", True) and np.isfinite(limits["oxygen supply"]):
        m = value("ge_micro_o2_x")
        x1 = x_o2 * vm.get("otr_mult", 1.0)                       # one drilled sparger, before the viscosity
        g = lambda s_: m * s_ ** 0.8 + (1.0 - s_) ** 0.8
        f = lambda s_: oxygen_limit(x1 * g(s_), exponent=kexp) if kexp > 0.0 else x1 * g(s_)
        nxt = min(v for k, v in limits.items() if k != "oxygen supply")
        if limits["oxygen supply"] < nxt:
            s_max = min(float(micro_share), m ** 5 / (1.0 + m ** 5))   # m^5 / (1 + m^5): the share that gives the most oxygen
            if f(s_max) <= nxt:
                micro = s_max
            else:
                lo_s, hi_s = 0.0, s_max
                for _ in range(40):
                    mid = 0.5 * (lo_s + hi_s)
                    if f(mid) >= nxt:
                        hi_s = mid
                    else:
                        lo_s = mid
                micro = hi_s
            limits["oxygen supply"] = f(micro)
            sparger[0] = f(micro)
    limit = min(limits, key=limits.get)
    x = limits[limit]
    shape = 1.0
    slow = 1.0
    if not washed:
        # the waste level at the end of a cycle, against the level perfusion is held to; above 1 the last doublings grow slower
        end_ratio = 1.0 if steady else x * max(nh3 / nh3_lim, lac / lac_room, flow / (1000.0 * cells.mu * 24.0))
        f = value("pf_draw_fraction")
        shape = f / np.log(1.0 / (1.0 - f))
        slow = batch_slowdown(end_ratio, vm["n_doublings"] if cyclic else float(np.log2(1.0 / (1.0 - f))))
        if cyclic:
            cycle_h, lost, uptime, runs_yr = _cycle(slow)
    shape = vm.get("shape", shape)
    if not cyclic:
        shape /= slow                                  # fill-and-draw climbs back to its cap more slowly
    rec = vm.get("recovery", 1.0)                      # share of the grown cells the vessel's own harvest gives back (in `live`, below)
    if cyclic:                                         # a tankful per cycle
        out = wv * x * HOURS / cycle_h / 1000.0 * (1.0 - lost)
    else:
        out = wv * x * cells.mu * shape * HOURS * uptime / 1000.0 * (1.0 - lost)
    ox = value("pf_opex_escalation")
    col = None
    if column != "none":                               # the column is sized for the density it allows
        from gas_exchange import column_design
        col = column_design(x, sparge_velocity=us, p_out=col_pout, oxygen=(column == "o2_closed"),
                            sweep="air" if column == "co2" else "o2_closed", p_top_barg=p_top_barg,
                            vessel_m3=vessel_m3, aspect=aspect, cells=cells, rq=rq_eff, do_mmol=do_mmol)
        loop_pump = 0.0
        if washed and not vm.get("own_retention") and (value("ge_col_on_loop") >= 0.5 if col_on_loop is None else col_on_loop):
            # on the filter loop (2026-11-21): the loop's pumps carry the column's flow, up to what a dense filter loop has run
            fl = min(col["flow_m3h"], value("ge_passes_tested") * value("pf_working_volume") * vessel_m3)
            loop_pump = value("ge_pump_cost") * (fl / value("ge_pump_flow")) ** 0.6 * value("ge_install_x") / 1000.0 / vessel_m3
        col["loop_pump_k_m3"] = loop_pump
        capex += col["capex_k_m3"] - loop_pump
    sparger2_capex = 0.0
    if n_sparg >= 2:
        import plant_items as _PI
        sparger2_capex = (value("ge_sparger2_k") * _PI.indirect() * _PI._bioreactor_direct(1.0) / vessel_m3
                          * value("pf_capex_escalation"))
        capex += sparger2_capex
    capital = charge * capex / out
    # Humbird's fed-batch crew per m3 of tank; a tank in perfusion (washed, run continuously) takes pf_labour_perfusion_x
    # times it (staff per thousand tonnes in analyses that assume perfusion against his fed-batch crew; 2026-11-20). Since
    # 2026-11-21 part of each crew is counted per tank, as he counts it (crew_multiplier): small tanks need more staff per m3
    crew = value("pf_labour") * humbird_fedbatch_output() * crew_multiplier(vessel_m3, washed and not cyclic)
    labour = crew / out * ox * vm.get("labour_mult", 1.0)
    consumables = value("pf_consumables_low")
    if vm.get("cons_run"):                             # what the vessel throws away each run ($k per m3 of vessel)
        consumables += vm["cons_run"] * (runs_yr if runs_yr is not None else 365.0 / (run_days or value("pf_run_days"))) / out
    osm = float("nan")
    terms = {}
    sorb = sorbent if washed else 0.0
    # a route that cleans the medium so it can be used again (medium_reuse.py): only where waste is washed out and the litres
    # are derived. The ammonium exchanger is the `sorbent` lever; the others clean `loop` litres per kilo grown and return them
    route = clean_route(clean) if (washed and medium_l is None) else None
    loop = 0.0                                         # litres cleaned and returned, per kilo of cells grown
    medium_l_unclean = None
    amm_all = nh3 / (nh3_lim / 1000.0)                 # litres that carry all the ammonia out at the tank's level
    share_used = 0.0                                   # the share cleaned, as `clean_share`
    if route is not None and route.get("sorbent"):
        sorb = (clean_loop / amm_all) if clean_loop is not None else float(clean_share)
        share_used, route = sorb, None
    suspended = not vm.get("own_retention")            # cells in suspension leave with their liquid; cells on a support do not
    if medium_l is None:                                # derived: nutrients need a minimum; waste needs more
        if washed:
            terms = {"ammonia": nh3 / (nh3_lim / 1000.0), "lactate": lac / (lac_room / 1000.0),
                     "least flow": flow / (cells.mu * 24.0)}
            if suspended:                              # the culture that leaves with the harvested cells must be replaced
                terms["harvest"] = 1000.0 / x
            medium_l_unclean = max(value("pf_medium_l_floor"), max(terms.values()))     # with no sorbent and no route
            terms["ammonia"] *= (1.0 - sorb)
            if sorb > 0:                               # sodium given back by the exchanger stays in the medium
                room = max(2.0, osm_limit - value("pf_osm_base") - osm_co2)
                terms = {**{k: terms[k] for k in ("ammonia", "lactate", "least flow")},
                         "salt": 1000.0 * (2.0 * lac + sorb * nh3) / room, **{k: v for k, v in terms.items() if k == "harvest"}}
            if route is not None:
                # each litre cleaned stands in for the share of a litre thrown away that the device takes of each waste
                takes = (("ammonia", route.get("nh3", 0.0)), ("lactate", route.get("lac", 0.0)),
                         ("least flow", route.get("other", 0.0)))
                top = max([terms[n] / sh for n, sh in takes if sh > 0] or [0.0])    # litres that take out all it handles
                loop = float(clean_loop) if clean_loop is not None else float(clean_share) * top
                share_used = loop / top if top > 0 else 0.0
                lac_out = min(terms["lactate"], loop * route.get("lac", 0.0)) * lac_room / 1000.0   # mol of lactate taken per kg
                for n, sh in takes:
                    terms[n] = max(0.0, terms[n] - loop * sh)
            need = max(terms.values())
        else:                                           # all the medium leaves with the cells (2026-11-19: named as such)
            terms = {"harvest": 1000.0 / x}
            need = 1000.0 / x
        terms["nutrients"] = value("pf_medium_l_floor")
        medium_l = max(value("pf_medium_l_floor"), need)
        if washed:
            osm = value("pf_osm_base") + osm_co2 + (2.0 * (lac - (lac_out if loop > 0 else 0.0)) + sorb * nh3) / medium_l * 1000.0
    elif washed and suspended:                          # a set figure cannot be less than the culture that leaves either
        medium_l = max(medium_l, 1000.0 / x)
    ret_capex = membranes = 0.0
    in_tank = bool(route and route.get("in_tank"))
    # litres per kg that pass the cell filter a second time: what a device on the permeate cleans and returns (the exchanger:
    # the litres that hold the ammonium it takes, at the tank's level)
    loop_filtered = sorb * amm_all + (0.0 if in_tank else loop)
    clean_parts = {}                                   # what the route adds, $ per kg of cells, capital charge included
    clean_capex = clean_filter_capex = clean_filter_membranes = clean_opex = 0.0
    if tff:                                            # the TFF loop clears what the bleed of cells does not carry out
        perm = max(0.0, medium_l - 1000.0 / x) + loop_filtered                         # litres per kg grown
        kg_h = out * 1000.0 / (HOURS * uptime)                                          # kg per hour per m3 of tank
        hw_l = kg_h / (value("rt_flux_lmh") if flux is None else flux) * (value("rt_tff_hw") if membrane_hw is None else membrane_hw) * value("rt_install")   # $k per m3 of tank, per L/kg
        # the membrane's life is the litres it filters over a full planned run; a run that ends early filters fewer
        mem_l = (value("rt_membrane_price") if membrane_price is None else membrane_price) / ((value("rt_membrane_life") if membrane_life is None else membrane_life) * run_frac)   # $ per litre
        ret_capex = perm * hw_l                                                         # $k per m3 of tank
        membranes = perm * mem_l
        capex += ret_capex
        capital += charge * ret_capex / out
        consumables += membranes
        clean_filter_capex, clean_filter_membranes = loop_filtered * hw_l, loop_filtered * mem_l
        clean_capex, clean_opex = clean_filter_capex, clean_filter_membranes
        if loop_filtered > 0:
            clean_parts["filter for the loop"] = clean_filter_membranes + charge * clean_filter_capex / out
        if in_tank:        # a membrane across the culture: the cell filter's fibre and hardware for the litres cleaned, times its share
            xm = loop * route.get("exchange_membrane", 0.0)
            capex += xm * hw_l
            capital += charge * xm * hw_l / out
            consumables += xm * mem_l
            clean_capex += xm * hw_l
            clean_opex += xm * mem_l
            clean_parts["exchange membrane"] = xm * mem_l + charge * xm * hw_l / out
    # maturation (2026-11-20; `mature_h`, default 0: bulk cell mass, as in the regulatory filings): hours at no growth before harvest.
    # The cells respire at their upkeep rate, so they use medium at that rate: the litres of growth times the upkeep oxygen of
    # those hours over the oxygen of growing a kilo, and the glucose they burn. A continuous tank holds its harvested stream that
    # long in a maturation vessel at the harvest density, priced as tank capacity at the plant's cost per m3; a cycle simply
    # lasts that much longer (_cycle). The maturation vessel's crew and utilities are not counted.
    mat_ratio = mat_capex = mat_l = 0.0
    if mature_h > 0:
        up, gr = o2_split(cells)
        mat_ratio = up * cells.mu * mature_h / (up + gr)
        mat_l = medium_l * mat_ratio
        medium_l += mat_l
        if not cyclic:
            mat_vol = out * 1000.0 / (HOURS * uptime) * mature_h / x        # m3 of maturation vessel per m3 of production tank
            mat_capex = mat_vol * (capex - ret_capex)
            capex += mat_capex
            capital += charge * mat_capex / out
    if loop > 0:
        # growth factors per litre, whether bought on top or inside a complete medium's price
        gf_l = value("pf_growth_factors") * ox / value("pf_medium_prep_l_kg") * (float(growth_factors) + float(gf_in_medium))
        # the dialysate is basal medium: the medium's price without its growth factors, never below the nutrients a litre carries
        basal_l = max(medium_price - (gf_l if gf_in_medium else 0.0), feedstock(GOOD_CELLS) / medium_l_unclean)
        clean_parts["growth factors lost"] = loop * (1.0 - route.get("gf_kept", value("mr_gf_kept"))) * gf_l
        clean_parts["dialysate"] = loop * route.get("dialysate_l", 0.0) * basal_l
        clean_parts["device"] = loop * route.get("device_l", 0.0)
        running = clean_parts["growth factors lost"] + clean_parts["dialysate"] + clean_parts["device"]
        consumables += running
        clean_opex += running
    # medium preparation and sterilising: Humbird's fed-batch plant is sized for pf_medium_prep_l_kg litres per kilo at its own
    # output; a case that passes more medium per m3 of tank a year buys more of that equipment (never less)
    if prep_item is None:
        import plant_items
        prep_item = plant_items.humbird()["medium"]
    prep_ratio = medium_l * out / (value("pf_medium_prep_l_kg") * humbird_fedbatch_output())
    prep_capex = prep_item * value("pf_capex_escalation") * (max(1.0, prep_ratio) ** value("pf_medium_prep_exp") - 1.0)
    capex += prep_capex
    capital += charge * prep_capex / out
    # utilities in Humbird's four parts (his Table 4.4; inputs pf_util_*; back-test 2026-11-20): building power by the year and
    # cleaning water and steam by the run, both per m3 of tank; the water of the medium by the litre; power for oxygen,
    # stirring, cooling and dewatering by the kilo, with the oxygen burned
    # Since 2026-11-21 the building's power follows its floor and its class (building_power): per m3 of tank it grows for small
    # tanks, and a sanitary hall or a plain shed draws a fraction of a clean room's
    runs = runs_yr if runs_yr is not None else 365.0 / (run_days or value("pf_run_days"))
    bpow = building_power(vessel_m3, power_choices, sized)
    utilities = ox * ((value("pf_util_time") * bpow + value("pf_util_run") * runs) / out
                      + value("pf_util_water") * medium_l + value("pf_util_kg") * burn)
    if col is not None:
        utilities += col["energy_kg"] + col["gas_kg"]
    if fat_fed > 0:                                    # lipid bought instead of made from glucose
        consumables += fat_fed * value("pf_fat_kg") * (value("pf_fat_price") if fat_price is None else fat_price)
    if sorb > 0:                                       # exchanger bought per mol of ammonium taken, over its uses
        q = value("pf_sorbent_q") if sorbent_q is None else sorbent_q                     # mol per kg of sorbent
        sorbent_cost = sorb * nh3 / q * (value("pf_sorbent_price") if sorbent_price is None else sorbent_price) \
            / (value("pf_sorbent_cycles") if sorbent_cycles is None else sorbent_cycles)
        consumables += sorbent_cost
        clean_opex += sorbent_cost
        clean_parts["sorbent"] = sorbent_cost
    protectant = 0.0
    death = 0.0                                        # share of the cells grown that bursting bubbles kill
    gas_used = 0.0                                     # gas velocity the culture needs from its sparger, m/s
    gas_cells = 0.0                                    # the part of it bubbled where the cells are, m/s
    if (vm.get("o2_gas", True) or vm.get("co2_gas", True)) and not vm.get("no_protectant"):   # bubbles meet the cells
        # the gas the culture needs: the cap x density / the smaller of the densities the sparger alone could serve (oxygen,
        # CO2). A column takes only what the sparger at its cap cannot, so it does not lower this
        served = [v for v in sparger if np.isfinite(v)]
        gas_used = us * (min(1.0, x / min(served)) if served else 0.0)
        gas_cells = gas_used * max(0.0, 1.0 - vm.get("gas_away", 0.0) / us) if us > 0 else 0.0   # a cage's gas meets no cells
        # death rate per hour = killing volume x gas passed per litre of culture per hour (gas_exchange.sparge_death)
        death_h = (value("ge_kill_protected") if kill is None else kill) * gas_cells / tank_shape(vessel_m3, aspect)[1] * 3600.0
        death_h *= 1.0 + micro * (value("ge_micro_kill_x") - 1.0)   # fine bubbles kill more cells per litre of gas
        death = min(0.5, death_h / cells.mu)
        protectant = medium_l * value("pf_protectant_dose") / 1000.0 * (
            value("pf_protectant_price") if protectant_price is None else protectant_price)
        consumables += protectant
    # growth factors are dosed per litre of medium, so their cost scales with the litres used (Humbird's figure is for his
    # fed-batch's 8.65 L/kg: he doses by concentration and counts what leaves with the emptied tank; back-test 2026-11-20)
    gf_per = value("pf_growth_factors") * ox * medium_l / value("pf_medium_prep_l_kg")
    gf = gf_per * float(growth_factors)
    # a complete medium (scenarios.explore_kwargs, sc_medium_complete) carries `gf_in_medium` of the growth factors inside its
    # price: it cannot cost less than the nutrients the cells eat plus those growth factors (2026-11-19)
    # `wash_price`: the litres that carry the nutrients at the medium's price, the rest (they only wash waste out) at the wash price
    carry = min(medium_l, value("pf_medium_l_floor"))
    bought = medium_l * medium_price if wash_price is None else carry * medium_price + (medium_l - carry) * wash_price
    eat = feedstock(cells) + 0.5 * GLUCOSE_FLOOR * burn * mat_ratio      # the glucose burned while maturing
    feed = max(eat + gf_per * float(gf_in_medium), bought) / (1.0 - lost)   # medium in a lost tank is lost too
    # the sparge gas: oxygen fed per kg of cells x its price, REPORTED but not added. The plant prices
    # (capital per m3, utilities) already contain the oxygen supply of the design they come from (20 m3,
    # Humbird's tank shape, his gas limit and back pressure). `gas` is what that supply costs per kg in
    # this case; `gas_extra` is what charging it in proportion to the gas passed per litre would add or
    # take off (zero at the floor). It is left out of the total: it is under $1/kg in every case on the
    # page and rests on one quoted oxygen price (research_notes/gas_flow_cap.md, section 5).
    o2_cost = value("pf_o2_price") * ox * value("pf_working_volume") * HOURS / (out * 1000.0)   # $ per kg cells per (kg O2/m3/h)
    gas = o2_cost * oxygen_fed(vessel_m3, gas_velocity, aspect, p_top_barg)
    gas_extra = gas - o2_cost * oxygen_fed()
    # the cells bubbles kill lyse and are not harvested, and pf_harvest_recovery of the rest is recovered: the cells lost were
    # grown with their share of everything, so output and every cost per kilo (and the litres) are per kilo harvested
    clean_capital = charge * clean_capex / out         # the yearly charge on the route's hardware, $ per kg (inside `capital`)
    live = (1.0 - death) * value("pf_harvest_recovery") * rec
    if medium_l_unclean is None:
        medium_l_unclean = medium_l
    if live != 1.0:
        out *= live
        capital, labour, utilities, consumables, feed, gf, extra_opex = (
            v / live for v in (capital, labour, utilities, consumables, feed, gf, extra_opex))
        membranes, protectant, gas, gas_extra, medium_l = (v / live for v in (membranes, protectant, gas, gas_extra, medium_l))
        clean_opex, clean_capital, clean_filter_membranes, loop, loop_filtered, medium_l_unclean = (
            v / live for v in (clean_opex, clean_capital, clean_filter_membranes, loop, loop_filtered, medium_l_unclean))
        clean_parts = {k: v / live for k, v in clean_parts.items()}
        terms = {k: v / live for k, v in terms.items()}
    total = capital + labour + utilities + consumables + feed + gf + extra_opex
    product = cell_share * total + (1.0 - cell_share) * value("pf_blend_filler_price")
    return {"density": float(x), "limit": limit, "output": float(out), "capex": float(capex),
            "retention_capex": float(ret_capex), "membranes": float(membranes), "protectant": float(protectant),
            "medium_prep_capex": float(prep_capex), "mature_capex": float(mat_capex), "mature_l": float(mat_l / live), "death_share": float(death), "gas_used": float(gas_used), "gas_cells": float(gas_cells), "micro_share": float(micro), "sparger2_capex": float(sparger2_capex),
            "harvested_share": float(live), "clean_capex": float(clean_capex), "clean_opex": float(clean_opex),
            "clean_capital": float(clean_capital),
            "clean_filter_capex": float(clean_filter_capex), "clean_filter_membranes": float(clean_filter_membranes),
            "clean_loop": float(loop_filtered if not in_tank else loop), "filter_extra_l": float(loop_filtered), "clean_share": float(share_used), "clean_parts": {k: float(v) for k, v in clean_parts.items()},
            "medium_l_unclean": float(medium_l_unclean),
            "capital": float(capital), "labour": float(labour), "utilities": float(utilities),
            "gas": float(gas), "gas_extra": float(gas_extra),
            "consumables": consumables, "extra_opex": float(extra_opex), "feedstock": float(feed), "growth_factors": float(gf),
            "uptime": float(uptime), "run_frac": float(run_frac), "medium_l": float(medium_l), "total": float(total),
            "product": float(product), "pco2_used": float(pco2_tol), "osmolality": float(osm),
            "limits": {k: float(v) for k, v in limits.items()},
            "medium_terms": {k: float(v) for k, v in terms.items()},
            "medium_set_by": max(terms, key=terms.get) if terms else "",
            "nh3_kg": float(nh3), "lac_kg": float(lac), "column": col,
            "rq": float(rq_eff), "o2_kg": float(cells.qo2 / cells.mu), "o2_kg_upkeep": float(o2_split(cells)[0]),
            "o2_kg_growth": float(o2_split(cells)[1]), "co2_kg": float(rq_eff * cells.qo2 / cells.mu)}


def o2_split(cells: Cells) -> tuple:
    """(upkeep, growth) oxygen per kg of cells grown, mol/kg wet. Upkeep runs per hour, so per kg it grows with
    the time a kg takes to make; growth's share is fixed per kg (see Cells.qo2)."""
    q24 = cells.qo2 / (cells.maintenance_share + (1.0 - cells.maintenance_share) * cells.mu / (LN2 / value("pf_doubling_h")))
    return (q24 * cells.maintenance_share / cells.mu,
            q24 * (1.0 - cells.maintenance_share) / (LN2 / value("pf_doubling_h")))


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


def backtest() -> list:
    """Reported runs against what the model gives for the same cells and vessel. Not a fit: nothing in the
    model was tuned to these (Humbird's two designs, which it was tuned to, are left out). Each row is
    (run, quantity, observed, model, note). Sources: research_notes/perfusion_rate_osmolality.md,
    species_cell_parameters.md, the SuperMeat and Pasitka reports, and the continuous-harvest report."""
    rows = []
    day = 24.0

    def cell(mass_pg, mu_per_day):
        return Cells(mass_pg=mass_pg, doubling_h=LN2 / mu_per_day * day)

    def caps(c):                                   # what the model lets a small, well-gassed vessel hold
        return {"oxygen supply": value("pf_otr_cap") / c.qo2, "thickness of the culture": value("pf_x_visc")}

    def litres(c, flow=None):                      # litres of medium per kg in perfusion, efficient-cell waste
        flow = value("pf_min_perfusion") if flow is None else flow
        return max(washout_litres(c), flow / (c.mu * day), value("pf_medium_l_floor"))

    # 1. Clincke et al. 2013: CHO in a wave bag with perfusion, the densest culture on record
    c = cell(2400.0, 0.35)                         # 16.4 um cells at the top density; growth 0.35 per day
    obs_x = 2.14e8 * 2400e-12 * 1000.0             # g wet per litre
    k = min(caps(c), key=caps(c).get)
    rows.append(("CHO, wave-bag perfusion (Clincke 2013)", "densest culture held, g/L", obs_x, caps(c)[k],
                 f"model limit: {k}. The run reached a packed-cell fraction of 0.5; its authors advise 0.37"))
    obs_l = 50e-12 / (2400e-15 * 0.35)             # 50 pL per cell per day
    rows.append(("CHO, wave-bag perfusion (Clincke 2013)", "medium, L per kg of cells", obs_l, litres(c),
                 "50 pL per cell a day. More gave no benefit, and nobody tried less."))
    # 2. Mayrhofer et al. 2020: CHO at 2.2-2.4e8 cells/mL on optimised medium
    c = cell(2500.0, 0.15)
    rows.append(("CHO, optimised perfusion medium (Mayrhofer 2020)", "medium, L per kg of cells",
                 22e-12 / (2500e-15 * 0.15), litres(c),
                 "14-30 pL per cell a day at about 0.15 per day growth. The cell size is assumed to be 2.5 ng."))
    # 3. SuperMeat 2024 (company report): chicken cells, 10 L perfusion with bleed
    c = cell(1400.0, 0.5 * LN2)                    # half a doubling a day; 1.0-1.75 ng per cell
    obs_x = 80e6 * 1400e-12 * 1000.0
    k = min(caps(c), key=caps(c).get)
    rows.append(("Chicken, 10 L perfusion (SuperMeat 2024)", "density held, g/L", obs_x, caps(c)[k],
                 f"model limit: {k}. The run had 80 million cells per mL at 1.0-1.75 ng."))
    rows.append(("Chicken, 10 L perfusion (SuperMeat 2024)", "medium, L per kg of cells", 30.5, litres(c),
                 "as reported for the scaled-up process"))
    out = value("pf_working_volume") * obs_x * c.mu * HOURS * value("pf_uptime") / 1000.0
    rows.append(("Chicken, scaled up on paper (SuperMeat 2024)", "output, t per m3 a year", 3039.0 / 125.0, out,
                 "The stated output differs from what its own density and growth rate give. The report does not add up."))
    # 4. Pasitka et al. 2024: chicken fibroblasts at 130 million cells per mL
    c = cell(550.0, LN2 / (61.0 / day))            # 10 um cells; 61 h doubling in animal-free medium
    rows.append(("Chicken, bench perfusion (Pasitka 2024)", "density claimed, g/L", 430.0, 130e6 * 550e-12 * 1000.0,
                 "The report says '43% w/v', but its cell count times the mass of a 10 um cell gives much less. The claimed figure is not cell mass."))
    # 5. Vow: the one 20 m3 plant, drained and refilled
    r = explore(mode="filldraw", charge=value("humbird_plant_charge"))
    rows.append(("Quail, 20 m3 drained and refilled (Vow)", "output, t per m3 a year", (3.7 + 6.5) / 2.0, r["output"],
                 "The stated target is 3.7-6.5, compared here with the model's efficient cells in the same mode."))
    return rows


def summarise_backtest() -> None:
    print("\n  back-test: reported runs against the model for the same cells (observed / model):")
    for run, what, obs, mod, note in backtest():
        print(f"    {run:<50} {what:<28} {obs:7.1f} / {mod:7.1f}  = {obs / mod:4.2f}x   {note}")


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
    ("Gas flow the cells tolerate", "gas_velocity", 0.002, 0.009, "2 mm/s", "9 mm/s",
     "CO\u2082 leaves the tank only in the gas bubbled through it, so the density a tank can hold is "
     "proportional to the gas flow. <b>Range:</b> Humbird's optimistic design uses 6 mm/s, his reading of a rule of thumb "
     "[2]. It is not a measured limit. Large pharma tanks run at 0.1 to 2 mm/s because their thin cultures need "
     "no more, and 2 is about the most that has been run with cells. 9 is what bubble damage would allow with "
     "enough protectant. <b>What caps it:</b> bursting bubbles kill cells, but a protectant cuts that about "
     "20-fold at 1 g a litre in the one small culture measured, and small tanks at 60 to 80 million cells per mL took twice Humbird's optimistic design's gas per litre. Foam is "
     "the likelier cap. It grows with gas velocity, and the antifoam that controls it slows growth and oxygen "
     "transfer. <b>Evidence:</b> weak. Nobody has run cells this dense at this size, or any culture at 6 mm/s. "
     "The model's rough judgement is an even chance that 6 mm/s works at this size."),
    ("CO\u2082 carried off by the exhaust gas", "strip_eff", 0.70, 0.9605, "70% of the most it could carry", "96%",
     "Gas bubbled through the tank leaves carrying CO\u2082, but the bubbles do not quite reach balance with the liquid. "
     "<b>Range:</b> 96% makes the model's CO\u2082 balance reproduce Humbird's density limits [2]. Stripping models of "
     "pharma tanks put it lower, down to about 70% (research_notes/gas_flow_cap.md). The density a sparged tank can hold "
     "falls in proportion. <b>Evidence:</b> pharma tanks of 2 to 20 m\u00b3 with thinner cultures, read mostly at abstract level."),
    ("Oxygen transfer left with antifoam", "antifoam_otr", 0.5, 1.0, "halved", "no effect",
     "Bubbling hard makes foam. The antifoam that controls it coats the bubbles and slows the oxygen they pass to the liquid. "
     "<b>Range:</b> reported effects run from none to about half (research_notes/gas_flow_cap.md). The model takes the middle, "
     "a quarter lost. Halved, the tank of Humbird's optimistic design is limited by oxygen at about {antifoam_half_x} g/L instead of by CO\u2082 at {ref_x}. "
     "<b>Evidence:</b> weak. It depends on the antifoam, its dose and the medium, and it has not been measured in dense "
     "meat-cell cultures. Only the sparger is affected here, not a column or the mixing rule."),
    ("Price of the bubble protectant", "protectant_price", 10.0, 260.0, "$10 a kilo", "$260 a kilo (catalogue)",
     "A protectant (poloxamer 188, 2 g per litre) keeps bursting bubbles from killing cells. It leaves with every litre of "
     "medium. <b>Range:</b> only catalogue prices were found, $230 to $260 a kilo in 25 kg packs. The model assumes $30 for "
     "tonnes. At $30 it adds $0.06 a litre, about {protectant_kg} a kilo of cells here. <b>Evidence:</b> no bulk price. A supplier "
     "quote would settle it."),
    ("Tank shape (liquid depth / width)", "aspect", 1.0, 3.0, "1.0", "3.0",
     "A deeper tank passes less gas per litre of liquid, so it clears less CO\u2082, and it mixes more slowly. "
     "<b>Range:</b> Humbird's tank has liquid 1.6 times as deep as it is wide [2]. Tanks in use run from about 1 "
     "to 3. <b>Evidence:</b> the geometry is certain. The model counts a squat tank's extra steel and floor space "
     "(its wall thickens with its width). There are no cost data on tank shape."),
    ("Pressure at the top of the tank", "p_top_barg", 0.0, 1.0, "0 bar gauge", "1 bar gauge",
     "Oxygen dissolves in proportion to its pressure, so a higher pressure in the headspace raises oxygen transfer "
     "and, by the model's mixing rule, the mixing limit. It does nothing for CO\u2082. <b>Range:</b> Humbird's tank "
     "is at 0.33 bar gauge [2]. Steaming at 121 \u00b0C already takes 1 bar, and stainless culture vessels are "
     "rated to 3-4 bar (vendor data sheets). <b>Evidence:</b> this is calculated. Cells already see about 1.7 bar absolute "
     "at the bottom of the tank. Nobody has run a culture at 1 bar gauge."),
    ("Ammonia the cells make", "nh3_kg", 0.055, 0.14, "0.055 mol/kg", "0.14 mol/kg",
     "Ammonia per kilo of cells grown, which fresh medium must wash out at 5 mmol/L. <b>Range:</b> 0.055 is what "
     "Humbird's efficient cells make. 0.14 is the best measured in meat cells, bovine cells with glutamine "
     "replaced (Hubalek 2023, read in full). Ordinary bovine cells made 0.70. <b>Evidence:</b> one study of meat "
     "cells. The efficient cell is an assumption."),
    ("Tank size", "vessel_m3", 5.0, 200.0, "5 m\u00b3", "200 m\u00b3",
     "A larger tank costs less per litre but is deeper, so it clears less CO\u2082 and must run thinner. "
     "<b>Range:</b> 5 to 200 m\u00b3, and Humbird's optimistic design uses 20. <b>Evidence:</b> the vessel cost and the CO\u2082 limit "
     "both follow Humbird [2]. Nobody has grown animal cells above about 25 m\u00b3, and only in pharma."),
    ("Plant estimate", "capex_x", 0.34, 1.5, "a third of Humbird's", "+50%",
     "What the whole plant costs per cubic metre of tank. <b>Range:</b> Humbird calls his own estimate good to "
     "within 50% [2]. Two other published designs for animal cells (Negulescu, CE Delft) assume plants at about a "
     "third of his cost. <b>Evidence:</b> design studies only. No built plant publishes both its cost and its "
     "tank volume."),
    ("Class of plant", "plant", "microbial", "pharma", "built like a yeast plant", "pharma-style",
     "This sets how clean the plant is built. Humbird's optimistic design uses a food-grade plant ($810k per m\u00b3). "
     "<b>Range:</b> from a plant built like a yeast plant ($190k) to a pharma-style plant with clean rooms ($910k). "
     "Humbird's own yeast plant with 20 m\u00b3 tanks costs about the lower figure, and two published "
     "cultivated-meat designs assume it. <b>Evidence:</b> nobody has run animal cells in the cheaper kind of plant."),
    ("Waste the cells make", "waste", 0.0, 0.25, "efficient cells", "a quarter of the way to ordinary",
     "Cells make ammonia and lactate, which stop growth. In perfusion, fresh medium must wash them out, so "
     "wasteful cells need more medium. <b>Range:</b> Humbird's efficient cells need 11 litres per kilo and "
     "ordinary cells 190 [2]. One company reports 30.5 for chicken, about a tenth of the way [1]. "
     "<b>Evidence:</b> the efficient cell is an assumption, not shown for meat cells."),
    ("Doubling time", "doubling_h", 18.0, 48.0, "18 h", "48 h",
     "A tank's output is its density times how fast the cells grow. Faster cells also respire more, so the "
     "tank holds fewer of them. <b>Range:</b> 24 hours is Humbird's model cell [2]. 18 is fast for an animal "
     "line. One company reports 48 in perfusion [1]. <b>Evidence:</b> measured for a few lines, mostly grown on "
     "a surface, not in dense suspension."),
    ("Cell mass", "mass_pg", 1000.0, 3000.0, "1 ng", "3 ng",
     "Smaller cells respire more per gram, so the tank holds fewer of them. <b>Range:</b> the model cell is "
     "3 ng [2]. Chicken cells are reported at 1 to 1.75 ng [1]. <b>Evidence:</b> the scaling law is well "
     "established, but cell mass is rarely reported on a sound basis."),
    ("CO\u2082 the cells tolerate", "pco2_mbar", 100.0, 200.0, "100 mbar", "200 mbar",
     "The density a tank can hold is proportional to the dissolved CO\u2082 the cells tolerate. <b>Range:</b> "
     "100 mbar is a pharma limit that also protects protein quality [2]. Pharma cells lose about a tenth of "
     "their growth at 200. Fish, shrimp and insect cells get their own, lower ranges (choose one in the first "
     "control). <b>Evidence:</b> nothing is published for muscle or fish cells. This is the measurement that "
     "would change Humbird's optimistic design most."),
    ("Yearly charge on the plant", "charge", 0.123, 0.236, "12.3%", "23.6%",
     "The share of the plant's cost charged each year: return on capital, maintenance, insurance. "
     "<b>Range:</b> 23.6% is Humbird's first-plant figure. Humbird's optimistic design's 17.3% uses the food industry's cost of "
     "capital over 20 years. 12.3% is a 30-year payback with no return. <b>Evidence:</b> this is a financing choice, "
     "not a scientific unknown. Loan guarantees change it."),
    ("Life of the filter membranes", "membrane_life", 5500.0, 900.0, "5,500 litres per m\u00b2", "900 litres per m\u00b2",
     "Perfusion needs a device that holds the cells in the tank while spent medium leaves. The model prices a hollow-fibre "
     "filter loop. Its membranes, not its hardware, set the cost: about $1,450 per m\u00b2, replaced after filtering "
     "2,415 litres per m\u00b2. <b>Range:</b> one fibre filtered about 5,500 litres per m\u00b2 over 30 days. Membranes "
     "pushed harder fouled after about 900. <b>Evidence:</b> small vessels only. Nobody has filtered a culture this thick "
     "for a month at 20 m\u00b3."),
    ("Growth factors", "growth_factors", 0.0, 1.0, "none", "all bought",
     "Proteins that tell cells to grow. Humbird's optimistic design leaves them out, which assumes cells that need none or make their own. "
     "<b>Range:</b> bought at Humbird's large-scale price, they add about {gf_all} a kilo [2]. <b>Evidence:</b> that "
     "price assumes an industry far larger than the current one."),
    ("Medium price", "medium_price", 0.10, 0.50, "$0.10 a litre", "$0.50 a litre",
     "What a litre of the nutrient liquid costs. It can never cost less than the nutrients the cells eat, so "
     "it matters more the more medium the cells need. <b>Range:</b> companies report $0.20 to $0.50 a litre [1]. "
     "<b>Evidence:</b> company reports. Nobody has verified them at scale."),
    ("How the tank is run", "mode", "perfusion", "filldraw", "perfusion", "drained and refilled",
     "In perfusion a device holds the cells back while medium flows through, so the tank stays at its densest. "
     "A tank that is half drained and refilled needs no device, but it averages 72% of peak output and waste "
     "caps its density. <b>Evidence:</b> draining and refilling is used at 20 m\u00b3. Perfusion is not used "
     "beyond 2 to 3 m\u00b3."),
    ("Runs lost to contamination", "hazard", 0.0, 0.02, "none", "2% a day",
     "A contaminated run ends early. The tank must be cleaned and regrown (14 days here), and a tankful is "
     "lost. <b>Range:</b> large pharma plants lose about 0.2% of runs a day. Cultivated-meat makers report "
     "losses that work out to roughly 1 to 2% a day. <b>Evidence:</b> one survey, which does not state run lengths."),
    ("Salt strength the cells tolerate", "osm_limit", 350.0, 450.0, "350 mOsm/kg", "450 mOsm/kg",
     "Holding the pH against dissolved CO\u2082 takes bicarbonate, and lactate comes with the base that "
     "neutralises it. Both add salt, and cells stop growing when the total is too high. So the more CO\u2082 "
     "a tank runs at, the less lactate it may hold, and the more medium it needs. <b>Range:</b> fresh medium "
     "is about 300. Humbird's optimistic design's 415 is what Humbird's own CO\u2082 and lactate limits imply together [2]. "
     "Across four studies of pharma cells, growth starts to fall at about 320 to 400 and is halved at about "
     "430 to 465. <b>Evidence:</b> pharma cells only. A single limit stands in for a gradual decline."),
    ("pH held in the tank", "ph", 6.9, 7.4, "6.9", "7.4",
     "A lower pH needs less bicarbonate for the same CO\u2082, which leaves more room under the salt limit. A "
     "higher pH needs more. <b>Range:</b> animal-cell tanks are usually held between about 6.9 and 7.4. "
     "<b>Evidence:</b> the chemistry is certain. How growth of meat cells changes across this range is not "
     "in the model."),
    ("Least medium flow the cells need", "min_perfusion", 3.7, 18.5, "3.7 mL per g a day", "18.5 mL per g a day",
     "Besides ammonia and lactate, other by-products build up and nutrients run out, so a cell needs a least "
     "flow of medium per day. Litres per kilo are that flow divided by the growth rate, so slow cells need "
     "more. <b>Range:</b> pharma perfusion runs measured this. 50 picolitres per cell a day sustained very dense "
     "cultures, 14 to 30 did so at slow growth, and 8 to 10 only kept cells alive. For cells of that size, "
     "this is about 3.7 to 18.5 mL per gram a day, typically 9. Humbird's optimistic design's 7.5 is better than typical "
     "practice. <b>Evidence:</b> pharma cells only. One company's chicken process works out to about 10.6."),
    ("Oxygen used for upkeep", "maintenance_share", 0.31, 1.0, "31%", "100%",
     "Part of a cell's oxygen use goes on whether or not it grows, and the rest rises with growth. It matters only "
     "when the doubling time is not 24 hours. <b>Range:</b> measurements put the upkeep share at 31% to 62%. "
     "Humbird assumes 100% [2]. <b>Evidence:</b> there are few measurements, and none for meat cells."),
]


def tornado_rows() -> list:
    """TORNADO with the figures its texts quote computed from `explore()` at Humbird's optimistic design (since 2026-11-22; they
    were typed in and had gone stale: the growth factors' "$4" was $5.7, the oxygen limit with antifoam halved "97 g/L" was 86)."""
    ref = explore()
    fig = {"gf_all": f"${explore(growth_factors=1.0)['growth_factors']:.1f}",
           "antifoam_half_x": f"{explore(antifoam_otr=0.5)['density']:.0f}",
           "ref_x": f"{ref['density']:.0f}", "protectant_kg": f"${ref['protectant']:.1f}"}
    return [(*row[:6], row[6].format(**fig)) for row in TORNADO]


def floor_tornado(pco2_range: tuple | None = None, **case) -> list:
    """Cost of the case ($/kg) with each limiting factor at the low and the high end of its range, the
    others as in `case` (default: the floor). Contamination is evaluated with a 14-day restart after a
    lost run. `pco2_range` replaces the CO2-tolerance range for a species whose cells differ (fish,
    shrimp, insect: SPECIES_PRESETS). Returns rows (label, cost at low, cost at high, low text, high
    text), widest first."""
    case = dict(case)
    case.setdefault("restart_fail_days", 14.0)
    rows = []
    for label, arg, lo, hi, lo_txt, hi_txt, _info in TORNADO:
        if arg == "pco2_mbar" and pco2_range is not None:
            lo, hi = pco2_range
            lo_txt, hi_txt = f"{lo:.0f} mbar", f"{hi:.0f} mbar"
        base = {k: v for k, v in case.items() if k != "items"} if arg == "plant" else case   # a class replaces the items
        a = explore(**{**base, arg: lo})["total"]
        b = explore(**{**base, arg: hi})["total"]
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
    cells (speed, size, waste), the life of the retention membranes, financing and the upkeep share of respiration.
    Everything else in the case (perfusion at 20 m3, no growth factors) is held. The cell-quality inputs
    share a correlation `cell_corr` (Gaussian copula). Returns the draws of total cost ($/kg) and of
    each input."""
    from inputs import prior
    from math import erf, sqrt
    rng = np.random.default_rng(seed)
    pri = dict(FLOOR_PRIORS)
    for key, name in (("membrane_life", "rt_membrane_life"), ("charge", "plant_charge_mature"),
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
    for plant, label in (("sanitary", "food-grade plant"), ("microbial", "yeast-style plant")):
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
    def from_explore(name, assumes, shown, **kw):
        # the perfusion tiers are explore() itself, so the ladder and the explorer cannot drift apart: the same
        # filter loop, protectant and oxygen. `total` at the first-plant charge, `total_mature` at the mature one.
        first, mature = explore(charge=value("humbird_plant_charge"), **kw), explore(**kw)
        plant = lambda r: r["total"] - r["feedstock"] - r["growth_factors"]
        rows.append({"name": name, "assumes": assumes, "shown": shown, "output": first["output"],
                     "capital": first["capital"], "labour": first["labour"], "utilities": first["utilities"],
                     "consumables": first["consumables"] + first.get("extra_opex", 0.0), "plant": plant(first),
                     "feedstock": first["feedstock"], "growth_factors": first["growth_factors"], "total": first["total"],
                     "plant_mature": plant(mature), "total_mature": mature["total"]})

    # the fill-and-draw tiers are explore() too since 2026-11-21 (they were plant_cost(), which skipped the waste build-up and
    # the least medium flow, the bubble deaths and the harvest loss: $19.7 and $18.2 against explore's $24 and $22 then)
    from_explore("Pharma-style plant, half the density", "the cautious case below with cells at 60 g/L, not 120",
                 "nearer to reported harvests (about 27 g/L)", mode="filldraw", plant="pharma", x_visc=value("pf_x_half"))
    from_explore("Pharma-style plant, fill-and-draw", "Humbird's sterile plant with clean rooms; 20 m3 tanks half drained and refilled each cycle, no cell retention, 85% uptime; efficient cells",
                 "fill-and-draw is filed as an option at 20 m3; this density is not shown", mode="filldraw", plant="pharma")
    from_explore("No clean rooms, fill-and-draw", "the same culture in a food-grade building: Humbird's plant with a sanitary hall in place of the clean room",
                 "food-grade 20 m3 tanks run today; this density is not shown", mode="filldraw", plant="sanitary")
    from_explore("No clean rooms, perfusion", "Humbird's optimistic design: food-grade plant; 20 m3 tanks in perfusion at 120 g/L, cells held back by a hollow-fibre filter loop; efficient cells; 91% uptime",
                 "each piece shown or claimed separately, never together")
    from_explore("Microbial-fermentation-class plant", "the frontier: Humbird's optimistic design in a plant that costs what microbial fermentation plants cost when built, buying its oxygen",
                 "such plants exist for microbes; not costed or built for animal cells", plant="microbial")
    add("Rough lower bound", "the cheapest modelled fermentation plant, small-tank density, oxygen at the animal-cell ceiling, amino acids at $1 a kilo (about the price of soybean-meal protein; GFI's feed grade is $6.36)",
        "a rough bound, not a design", GOOD_CELLS, "perfusion", value("pf_bound_capex"), low, 0.0,
        cheap=True, otr=value("pf_bound_otr"), humbird_capex=False, uptime=design_uptime)
    return rows


def summarise(pr: CostParams) -> None:
    pc = parity_cost(pr)
    for label, c in (("efficient model cell (3 ng, 24 h)", GOOD_CELLS), ("small slow cell (0.55 ng, 61 h)", PASITKA_CELLS)):
        print(f"  {label}: oxygen uptake {c.qo2:.3f} mmol/g/h, {c.o2_per_kg:.2f} kg O2 per kg cells; "
              f"oxygen-limited density {density(c, value('pf_otr_cap'), True):.0f} g/L")
    print(f"\n  parity needs cells at <= ${pc:.0f}/kg (with ${pr.markup_add:.1f}/kg to the shelf and a {pr.retail_margin:.0%} retail margin against ${pr.p_conv:.0f} meat)\n")
    print(f"  first-plant financing {value('humbird_plant_charge'):.1%} a year; 'mature' = food-industry financing "
          f"{value('plant_charge_mature'):.1%}")
    print(f"  {'tier':<36}{'t/m3/yr':>8}{'capital':>9}{'labour':>8}{'util+cons':>10}{'feed':>7}{'GF':>6}{'TOTAL':>8}   R   mature")
    for r in tiers():
        R = ratio(r["total"], pr)
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
    summarise_backtest()
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
    ax.set_title("The class of plant sets the cost")
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
    print("Physics-based cost of cells, per kg of real wet cells (Humbird's optimistic design is explore() at its defaults):")
    summarise(pr)
    fig_floor_tiers(pr, args.outdir, fmts)
    print("Done.")


if __name__ == "__main__":
    main()
