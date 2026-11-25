#!/usr/bin/env python3
"""
retention.py — what it takes to hold the cells back in a 20 m3 perfusion tank, and what it costs.

Why
---
Every cost scenario uses a 20 m3 stirred tank in perfusion: fresh medium flows through, a device holds the cells back,
and the harvest is a steady bleed of cells. Nobody has run animal cells in perfusion above about 4 m3. The model used to
charge a hoped-for device at `pf_capex_retention` ($89k per m3 of tank, from one design study that does not name it).
This module sizes the real devices for the real duty. Since 2026-11-15 the model's default is the TFF hollow-fibre loop
priced here (floor_physics.explore); the hoped-for device is kept as a row for comparison.

The duty
--------
From floor_physics.explore() for a case (`duty`):
    liquid volume      V = working volume x tank size                        (16 m3 for a 20 m3 tank)
    harvest            H = output per tank-year / (8760 x uptime)            kg of wet cells an hour while the tank runs
    medium in          Q = litres per kg x H                                 m3/h
    bleed (harvest)    B = H / density                                       m3/h of whole culture: the product
    permeate           P = Q - B                                             m3/h of cell-free liquid the device must clear
Because the product is the cells, the bleed carries part of the liquid out. The device only clears the rest.

The devices
-----------
Each device is data (`DEVICES`, numbers in inputs.py `rt_*`): what flow it is sized on (permeate, or the whole outflow for
a separator that takes everything leaving the tank), its capacity per unit, price, installation factor, what it uses up,
power, and the densest culture and largest scale it has been shown at. `sizing(device, case)` gives the units, the capital per
m3 of tank, the running cost per kg; `scenario_cost(device, case)` reprices the case with that device through explore()'s
`retention` and `extra_opex` arguments. No default of the model changes.

Evidence: research_notes/retention_devices.md.

Cells in particles (2026-11-19): `aggregates` (cells grown as clumps of 100-300 um) and `microcarriers` (cells on edible beads)
are held back by a plain settler sized on the particle's settling speed. Each case is first run as it would be with them
(`particle_case`): its density is held to what the particles' volume allows, and aggregates lose the growth of cells too short
of oxygen to divide (`growth_penalty`). Evidence: research_notes/retention_aggregates.md.

Run
---
    python retention.py
"""
from __future__ import annotations

import math

import floor_physics as fp
from inputs import value

HOURS = 8760.0


def cases() -> dict:
    """The three cases the duty is worked out for: explore() arguments."""
    import scenarios as S
    return {"reference": {}, "central": S.explore_kwargs(S.SCENARIOS["central"].choice),
            "best": S.explore_kwargs(S.SCENARIOS["best"].choice)}


def duty(kw: dict | None = None, result: dict | None = None) -> dict:
    """What the retention device must do in a case (explore arguments): flows in m3/h, vessel volumes a day, the cells'
    volume fraction, and the case's own result. `kg_h` and `kg_year` are kilos HARVESTED, as explore's output is; the bleed
    carries out the cells GROWN (the harvested over `harvested_share`: cells killed by bubbles or lost at harvest were grown
    and bled too), as explore's own filter loop counts it (corrected 2026-11-20: it was the kilos harvested, which showed
    permeate, and charged membranes, where explore has none)."""
    kw = dict(kw or {})
    r = fp.explore(**kw) if result is None else result      # `result`: the case as it runs with a device (scenario_cost)
    v = kw.get("vessel_m3", 20.0)
    liquid = value("pf_working_volume") * v                                # m3
    tonnes = r["output"] * v                                                 # t of wet cells per tank-year
    harvest = tonnes * 1000.0 / (HOURS * r["uptime"])                        # kg/h while the tank runs
    medium = r["medium_l"] * harvest / 1000.0                                # m3/h
    bleed = harvest / r["harvested_share"] / r["density"]                    # m3/h of whole culture (kg grown an hour over kg/m3)
    permeate = max(0.0, medium - bleed)
    if permeate < 1e-9 * medium:                                             # the bleed carries out all the liquid (rounding apart)
        permeate = 0.0
    # the litres a sorbent or another device on the permeate cleans pass the filter again (2026-11-21; explore's filter loop
    # has charged them since 2026-11-16, this sizing did not)
    permeate += r.get("filter_extra_l", 0.0) * harvest / 1000.0
    phi = r["density"] / (value("pf_cell_density") * 1000.0)                # volume fraction of cells
    return {"vessel_m3": v, "liquid_m3": liquid, "density": r["density"], "phi": phi, "kg_h": harvest,
            "kg_year": tonnes * 1000.0, "medium_m3_h": medium, "bleed_m3_h": bleed, "permeate_m3_h": permeate,
            "outflow_m3_h": medium, "vvd_medium": medium * 24.0 / liquid, "vvd_permeate": permeate * 24.0 / liquid,
            "uptime": r["uptime"], "run_frac": r.get("run_frac", 1.0), "result": r}


# ----------------------------------------------------------------------------
# The devices
# ----------------------------------------------------------------------------
# Each: name, how it holds cells back, what it is sized on, the densest culture (volume fraction) it has held, the largest
# scale shown, and where its cost goes. The numbers are in inputs.py `rt_*`; the evidence in research_notes/retention_devices.md.
DEVICES = {
    "hoped": dict(name="Hoped-for device (the old default)", how="a filter-free device one design study priced",
                  shown="none: Pasitka's design study does not say what it is", phi_max=None),
    "atf": dict(name="ATF hollow-fibre filter", how="a diaphragm pulls culture back and forth through hollow fibres",
                shown="50 days on 50 L at 1e8 cells/mL (Ott 2024); 1.3e8 for days in 4 L (Clincke 2013); units rated to 5,000 L",
                phi_max="rt_atf_phi_max"),
    "tff": dict(name="TFF hollow-fibre loop (the model's default)", how="a pump circulates culture past hollow fibres",
                shown="2.14e8 cells/mL for days in a 4 L bag (Clincke 2013); one fibre lasted 30 days; nothing published above pilot scale",
                phi_max="rt_tff_phi_max"),
    "reuse": dict(name="Reused pharma hollow-fibre modules", how="the TFF loop, with each module cleaned and used again four times",
                  shown="no reuse data with animal cells; steam limits a module to about 10 cycles",
                  phi_max="rt_tff_phi_max"),
    "dialyser": dict(name="Dialyser-grade hollow fibres, replaced often", how="a bank of mass-made medical hollow-fibre filters",
                     shown="whole blood at 32-40% cells by volume, for hours; no animal-cell culture", phi_max="rt_dial_phi_max"),
    "ceramic": dict(name="Ceramic membranes run as a slow TFF loop", how="dairy-type ceramic elements, cleaned in place between runs",
                    shown="nothing with animal cells", phi_max="rt_ceramic_phi_max"),
    "settler": dict(name="Inclined (lamella) settler", how="cells settle on inclined plates and slide back to the tank",
                    shown="5e7 cells/mL (Coronel 2020); a 2,000 L tank (Romann 2023); a 3,000 L seed tank",
                    phi_max="rt_settle_phi_max"),
    "acoustic": dict(name="Acoustic settler", how="standing sound waves gather cells into clumps that settle",
                     shown="200-400 L of permeate a day in independent tests; 1,000 L/day the largest unit sold",
                     phi_max="rt_settle_phi_max"),
    "discstack": dict(name="Disc-stack separator on the outflow", how="a hermetic centrifuge takes the outflow, returns the "
                      "concentrated cells and lets the clear medium go",
                      shown="CHO harvests at up to 28% packed volume; yeast recycled 2-3 times a day for 250-280 days (not animal cells)",
                      phi_max="rt_ds_phi_max"),
    "hydrocyclone": dict(name="Hydrocyclone", how="a spinning flow throws cells to the wall and back to the tank",
                         shown="5e7 cells/mL in a 40 L bag (Bettinardi 2020)", phi_max="rt_hc_phi_max"),
    "aggregates": dict(name="Cells grown as aggregates, gravity settler", how="cells grow as clumps of 100-300 um that settle "
                       "about a hundred times faster than single cells; a settler sends them back and the clear medium goes",
                       shown="33-35e6 iPSC/mL in 150 mL for 7 days (Manstein 2021); aggregates held back in 8 L by a spiral "
                             "settler and a back-flushed 20 um filter (Huang 2020)", phi_max="rt_agg_phi_shown"),
    "microcarriers": dict(name="Cells on edible carriers, gravity settler", how="cells grow on beads of about 190 um that are "
                          "eaten with them; a settler sends the beads back",
                          shown="8e6 Vero/mL on Cytodex 3 in 3 L (Eppendorf); carriers at up to 6,000 L in vaccine plants",
                          phi_max="rt_mc_phi_shown"),
}
NOT_COSTED = {"spin": ("Spin filter", "Its screen sits inside the tank, so its area grows with the tank's width, not its volume; "
                                     "shown only at about 1e7 cells/mL or less, and it clogs within weeks."),
              "ksep": ("Fluidized-bed centrifuge (kSep)", "One cycle holds about 2.9 kg of cells; the central duty passes "
                                                         "about 250 kg an hour, about 86 cycles an hour. The 6000S is discontinued.")}
ORDER = ("hoped", "atf", "tff", "reuse", "dialyser", "ceramic", "settler", "acoustic", "discstack", "hydrocyclone",
         "aggregates", "microcarriers")


def atf_factor(escalate: bool = True) -> float:
    """Capital per dollar of an ATF unit's bare price, in 2025 dollars: Humbird's accounting for bought equipment, as
    floor_physics.tank_items prices each tank's makeup tanks and filter housings (bare x 1/0.9 for minor equipment x 2.3 for
    installation = 2.5556; x 1.84 for engineering, construction, fees and contingency), times pf_capex_escalation from his 2018
    prices (rt_atf_price is his bare price). Until 2026-11-20 the module took only rt_install = 1.84 on the bare price and did not
    escalate: 3.4 times less. `escalate=False` gives his own 2018 dollars, which humbird_check.atf_capex_2018 uses, so the two
    cannot drift apart."""
    import plant_items as PI
    return PI._equipment_direct(1.0) * PI.indirect() * (value("pf_capex_escalation") if escalate else 1.0)
PARTICLES = ("aggregates", "microcarriers")      # cells in particles that settle fast: research_notes/retention_aggregates.md
NOT_COSTED["mbr"] = ("Wastewater membrane (submerged, air-scoured)", "It cannot be steamed (rated to 40 C), is made for 3-20 g/L of "
                     "solids against 50-75 g/L dry here, and needs coarse bubbles in the culture.")
NOT_COSTED["pvdf"] = ("Food and beverage hollow fibres (wine, beer)", "Sanitised with hot water, not sterilised, used on fluids "
                      "with well under 1% solids; no price per m2 was found.")
# membrane devices: flux, hardware $k per m2, membrane price $ per m2, litres per m2 before replacement
_MEMB = {"reuse": ("rt_flux_lmh", "rt_tff_hw", "rt_membrane_price", "rt_reuse_life"),
         "dialyser": ("rt_dial_flux", "rt_dial_hw", "rt_dial_price", "rt_dial_life"),
         "ceramic": ("rt_flux_lmh", "rt_ceramic_hw", "rt_ceramic_price", "rt_ceramic_life")}


# ----------------------------------------------------------------------------
# Cells in particles: aggregates and carriers (research_notes/retention_aggregates.md)
# ----------------------------------------------------------------------------
# A particle settles at Stokes' speed, d^2 x (its density excess) x g / (18 x viscosity): a clump of 100 um settles about
# 20 times faster than one 3 ng cell, a carrier bead of 190 um about 70 times. Two things limit the route instead:
#   * thickness: a particle carries liquid inside it (between the cells of an aggregate, or the hydrogel of a bead), and the
#     viscosity of a suspension follows the volume its particles take. The model lets single cells take a quarter of the
#     volume (pf_x_visc); here the particles may take rt_part_phi_max, so the cells may take that times their share of a
#     particle's volume. For a carrier that share is small: a layer of cells a few um thick on a bead of 190 um.
#   * oxygen, for aggregates: it reaches the middle only by diffusion. With uptake Q per volume of aggregate (zero order) and
#     dissolved oxygen C_s at the surface, the middle of a sphere of radius r sits at C_s - Q r^2 / (6 D). Cells below
#     rt_o2_prolif are taken not to grow. The liquid film around the aggregate adds a drop of 2 Q r^2 / (3 Sh D_water).
#     A layer of cells on a solid bead is too thin for any of this to matter.

def _cells(kw: dict | None) -> fp.Cells:
    kw = kw or {}
    return fp.Cells(mass_pg=kw.get("mass_pg", 3000.0), doubling_h=kw.get("doubling_h", 24.0),
                    **({} if kw.get("maintenance_share") is None else {"maintenance_share": kw["maintenance_share"]}))


def surface_oxygen(kw: dict | None = None) -> float:
    """Dissolved oxygen the tank is held at (mmol/L): the case's `do_mmol`, or the level Humbird's tank implies (0.28)."""
    from gas_exchange import headspace_pressure
    kw = kw or {}
    return headspace_pressure(kw.get("p_top_barg"), kw.get("vessel_m3", 20.0), kw.get("aspect"), kw.get("do_mmol"))["c_liquid"]


def uptake_per_volume(cells: fp.Cells, share: float | None = None) -> float:
    """Oxygen uptake of an aggregate, mol per m3 of aggregate per second: qO2 (mmol/g/h) x g of cells per L of aggregate."""
    share = value("rt_agg_cell_share") if share is None else share
    return cells.qo2 * share * value("pf_cell_density") * 1000.0 / 3600.0


def _film() -> float:
    """The liquid film around an aggregate of radius R that takes up Q: its drop is flux x 2R / (Sh x D_water), with
    flux = Q R / 3 per area, so drop = Q R^2 F. Returns F, s/m2 x m3/mol units folded in (1/(m2/s))."""
    return 2.0 / (3.0 * value("rt_o2_sherwood") * value("rt_o2_diff_water"))


def critical_diameter(cells: fp.Cells, c_s: float, d_tissue: float | None = None, c_min: float | None = None,
                      share: float | None = None) -> float:
    """Largest aggregate (um across) whose middle stays at or above c_min (mmol/L) with c_s in the liquid around it. The
    drop from the liquid to the middle is Q R^2 (1/(6 D) + 2/(3 Sh D_water)): diffusion inside the aggregate (zero-order
    uptake Q) plus the liquid film around it. 0 when the liquid is already below c_min."""
    D = value("rt_o2_diff_tissue") if d_tissue is None else d_tissue
    c_min = value("rt_o2_prolif") if c_min is None else c_min
    if c_s <= c_min:
        return 0.0
    return 2.0 * math.sqrt((c_s - c_min) / (uptake_per_volume(cells, share) * (1.0 / (6.0 * D) + _film()))) * 1e6


def hypoxic_share(d_um: float, cells: fp.Cells, c_s: float, d_tissue: float | None = None, c_min: float | None = None,
                  share: float | None = None) -> float:
    """Share of an aggregate's volume below c_min. Inside a core of radius a nothing is taken up (those cells are starved);
    the shell from a to R takes up Q, so the drop across it is Q/(6D) (R^2 - a^2) + Q a^3/(3D) (1/R - 1/a), and the film
    outside carries the shell's uptake, a drop of 2 Q (R^3 - a^3) / (3 R Sh D_water). Returns (a/R)^3."""
    D = value("rt_o2_diff_tissue") if d_tissue is None else d_tissue
    c_min = value("rt_o2_prolif") if c_min is None else c_min
    Q, R, dc = uptake_per_volume(cells, share), d_um * 1e-6 / 2.0, c_s - c_min
    if dc <= 0:
        return 1.0
    F = _film()

    def drop(a):
        inside = Q / (6.0 * D) * (R * R - a * a) + (Q * a ** 3 / (3.0 * D) * (1.0 / R - 1.0 / a) if a > 0 else 0.0)
        return inside + Q * F * (R ** 3 - a ** 3) / R
    if drop(0.0) <= dc:
        return 0.0
    lo, hi = 0.0, R                                                     # drop falls from drop(0) to 0 as a goes to R
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if drop(mid) > dc else (lo, mid)
    return (0.5 * (lo + hi) / R) ** 3


def growth_penalty(kw: dict | None = None, c_s: float | None = None, d_max: float | None = None) -> float:
    """Share of the cells in aggregates that do not grow for want of oxygen. Aggregates grow from rt_agg_d_min_um to
    rt_agg_d_max_um and are then broken up. In steady state cells are spread evenly over log(aggregate size) (each
    aggregate spends equal time in each doubling of its mass), so the share is the mean hypoxic share over log(diameter).
    Worked out once with the case's cells as they are (the slower growth would lower their uptake a little)."""
    cells = _cells(kw)
    c_s = surface_oxygen(kw) if c_s is None else c_s
    d0 = value("rt_agg_d_min_um")
    d1 = value("rt_agg_d_max_um") if d_max is None else d_max
    n = 40
    ds = [d0 * (d1 / d0) ** ((i + 0.5) / n) for i in range(n)] if d1 > d0 else [d1]
    return sum(hypoxic_share(x, cells, c_s) for x in ds) / len(ds)


def particle(device: str, kw: dict | None = None) -> dict:
    """What a particle of `device` is: the cells' share of its volume (`share`), the diameter the settler must hold
    (`settle_um`, the smallest particle), its density excess over medium (kg/m3), and the densest culture the thickness rule
    allows (`cap`, g of cells per L). For carriers also: kg of dry carrier and litres of swollen bead per kg of wet cells."""
    kw = kw or {}
    rho_c, rho_m = value("pf_cell_density"), value("pf_medium_density")         # g/mL
    out = {"device": device}
    if device == "aggregates":
        s = value("rt_agg_cell_share")
        out.update(share=s, settle_um=value("rt_agg_d_min_um"), drho=s * (rho_c - rho_m) * 1000.0)
    elif device == "microcarriers":
        m = kw.get("mass_pg", 3000.0) * 1e-12                                     # g per cell
        sigma, db = value("rt_mc_cells_cm2"), value("rt_mc_d_um") * 1e-4         # cells/cm2, cm
        t = sigma * m / rho_c                                                     # cm: the cell layer, as a solid film
        s = 6.0 * t / (6.0 * t + db)                                              # cells' share of a loaded bead's volume
        bead_l = db / (6.0 * sigma * m)                                           # mL of bead per g of cells = L per kg
        out.update(share=s, layer_um=t * 1e4, settle_um=value("rt_mc_d_um") / (1.0 - s) ** (1.0 / 3.0),
                   drho=(s * (rho_c - rho_m) + (1.0 - s) * (value("rt_mc_density") - rho_m)) * 1000.0,
                   bead_l_kg=bead_l, carrier_kg=bead_l * value("rt_mc_solids"),
                   carrier_wet_share=bead_l * value("rt_mc_density") / (bead_l * value("rt_mc_density") + 1.0))
    else:
        raise KeyError(device)
    out["cap"] = value("rt_part_phi_max") * out["share"] * rho_c * 1000.0
    return out


def particle_case(device: str, kw: dict | None = None) -> tuple:
    """The case as it would run with cells in particles: (explore arguments, notes). Two changes, each only when it binds:
    the density is held to the particles' thickness cap (an explore `vm` cap), and for aggregates the doubling time is
    lengthened by the share of cells too short of oxygen to grow (doubling / (1 - that share))."""
    kw = dict(kw or {})
    p = particle(device, kw)
    note = {"cap": p["cap"], "capped": False, "penalty": 0.0, "density_wanted": fp.explore(**kw)["density"]}
    if device == "aggregates":
        pen = growth_penalty(kw)
        note["penalty"] = pen
        if pen > 0:
            kw["doubling_h"] = kw.get("doubling_h", 24.0) / (1.0 - pen)
    if fp.explore(**kw)["density"] > p["cap"] + 1e-9:
        vm = dict(kw.get("vm") or {})
        vm["caps"] = {**vm.get("caps", {}), "particles": p["cap"]}
        kw["vm"] = vm
        note["capped"] = True
    return kw, note


def sizing(device: str, kw: dict | None = None, d: dict | None = None) -> dict:
    """Size a device for a case's duty. Returns: what it takes (units, m2), capital per m3 of tank ($k), running cost per kg of
    wet cells harvested (`cons_kg`, $: membranes, power, maintenance; `cons_kg_grown` is the same per kilo grown, which is what
    explore's `extra_opex` takes), the share of grown cells it destroys or lets go (`loss`), the culture
    held outside the tank (m3), and whether the case's density is beyond what the device has held (`beyond`).
    For cells in particles (`PARTICLES`) the duty is the case as it would run with them (`particle_case`): `note` says
    whether its density was held to the particles' cap and how much growth the aggregates' oxygen costs."""
    note = None
    if device in PARTICLES:
        kw2, note = particle_case(device, kw)
        if d is None or kw2 != dict(kw or {}):
            d = duty(kw2)
        kw = kw2
    d = duty(kw) if d is None else d
    v, liq, P, B, phi = d["vessel_m3"], d["liquid_m3"], d["permeate_m3_h"], d["bleed_m3_h"], d["phi"]
    kg = d["kg_year"]
    out = {"device": device, "units": 0.0, "area_m2": 0.0, "capex_k_m3": 0.0, "cons_kg": 0.0, "loss": 0.0, "holdup_m3": 0.0}
    perm_l_kg = P * 1000.0 / d["kg_h"]                                     # litres of permeate per kg harvested
    hs = d["result"]["harvested_share"]                                    # kilos harvested per kilo grown
    # a lost run throws its membranes away early: their life is the litres of a full planned run times the share of it an
    # average start completes (as floor_physics.explore charges since 2026-11-19). Ceramics are cleaned and kept.
    run_frac = d.get("run_frac", 1.0)
    membranes = perm_l_kg * value("rt_membrane_price") / (value("rt_membrane_life") * run_frac)
    if device == "hoped":
        out["capex_k_m3"] = value("pf_capex_retention")
    elif device == "atf":
        n = math.ceil(P * 1000.0 / (value("rt_flux_lmh") * value("rt_atf_area")))
        out.update(units=n, area_m2=n * value("rt_atf_area"), cons_kg=membranes,
                   capex_k_m3=n * value("rt_atf_price") * atf_factor() / v)
    elif device == "tff":
        # the engine's own loop: the case's own flux, membrane life, price and hardware where it sets them (explore's arguments)
        k = kw or {}
        own = lambda arg, name: value(name) if k.get(arg) is None else k[arg]
        area = P * 1000.0 / own("flux", "rt_flux_lmh")
        out.update(area_m2=area, cons_kg=perm_l_kg * own("membrane_price", "rt_membrane_price") / (own("membrane_life", "rt_membrane_life") * run_frac),
                   capex_k_m3=area * own("membrane_hw", "rt_tff_hw") * value("rt_install") / v)
    elif device in _MEMB:
        flux, hw, price, life = (value(k) for k in _MEMB[device])
        area = P * 1000.0 / flux
        if device != "ceramic":
            life *= run_frac
        out.update(area_m2=area, cons_kg=perm_l_kg * price / life, capex_k_m3=area * hw * value("rt_install") / v)
    elif device == "settler":
        cells = fp.Cells(mass_pg=kw.get("mass_pg", 3000.0) if kw else 3000.0, doubling_h=24.0)
        d_um = (6.0 * cells.mass_pg * 1e-15 / (math.pi * value("pf_cell_density") * 1000.0)) ** (1.0 / 3.0) * 1e6
        v1 = fp._stokes(d_um, (value("pf_cell_density") - value("pf_medium_density")) * 1000.0)        # cm/h
        vd = v1 * (1.0 - phi) ** 4.65 * value("rt_settle_v_frac")                                   # design overflow, cm/h
        area = P / (vd / 100.0)
        out.update(area_m2=area, holdup_m3=area * value("rt_settle_holdup") / 1000.0, settle_cm_h=vd,
                   capex_k_m3=area * value("rt_settle_price") / v)
    elif device == "acoustic":
        n = math.ceil(P * 24.0 / value("rt_acoustic_cap"))
        out.update(units=n, capex_k_m3=n * value("rt_acoustic_price") * value("rt_install") / v)
    elif device == "discstack":
        c = value("rt_ds_conc")
        feed = P * (1.0 + phi / (c - phi))                                  # permeate plus the concentrate sent back
        run = math.ceil(feed / value("rt_ds_cap"))
        n = run + value("rt_ds_spares")
        capex = n * value("rt_ds_price")                                    # $k per tank, installed
        passes, bleed = feed * 24.0 / liq, B * 24.0 / liq                   # share of the culture through the bowl a day
        f = value("rt_ds_lysis") * passes
        power = run * value("rt_ds_power") * HOURS * d["uptime"] * value("ge_power_price") / kg
        out.update(units=n, feed_m3_h=feed, passes_day=passes, loss=f / (bleed + f),
                   capex_k_m3=capex / v, cons_kg=power + value("rt_maint") * capex * 1000.0 / kg)
    elif device == "hydrocyclone":
        feed = P / value("rt_hc_split")
        esc = (1.0 - value("rt_hc_eff")) * feed                             # culture-equivalent flow of cells lost
        out.update(feed_m3_h=feed, loss=esc / (B + esc), capex_k_m3=feed * value("rt_hc_price") / v)
    elif device in PARTICLES:
        p = particle(device, kw)
        phi_p = phi / p["share"]                                            # volume the particles take
        v1 = fp._stokes(p["settle_um"], p["drho"])                          # cm/h, the smallest particle held
        vd = v1 * (1.0 - phi_p) ** 4.65 * value("rt_settle_v_frac")         # design overflow, cm/h
        area = P / (vd / 100.0)
        # carriers are bought for the cells grown; per kilo harvested, as every other cost here
        carriers = p.get("carrier_kg", 0.0) * value("rt_mc_price") / hs if device == "microcarriers" else 0.0
        out.update(area_m2=area, holdup_m3=area * value("rt_settle_holdup") / 1000.0, settle_cm_h=vd, particle_cm_h=v1,
                   stay_min=value("pf_plate_gap") / (vd * 0.5) * 60.0,                    # on plates at 60 degrees, no oxygen
                   phi_particles=phi_p, capex_k_m3=area * value("rt_settle_price") / v, cons_kg=carriers,
                   carriers_kg=carriers, loss=value("rt_part_loss"), particle=p, note=note, density=d["density"])
    else:
        raise KeyError(device)
    out["cons_kg_grown"] = out["cons_kg"] * hs
    key = DEVICES[device]["phi_max"]
    out["phi_max"] = value(key) if key else None
    out["beyond"] = key is not None and phi > value(key) + 1e-9
    # not possible: a settler that would hold too much of the culture outside the tank, with no oxygen
    out["impossible"] = ("It would hold {:.0%} of the culture outside the tank, with no oxygen supply.".format(out["holdup_m3"] / liq)
                         if out["holdup_m3"] > value("rt_settle_holdup_max") * liq else "")
    return out


RESIZE_PASSES = 2                  # scenario_cost: passes that size a device from the design it runs


def scenario_cost(device: str, kw: dict | None = None) -> dict:
    """The case's cost per kg with this device: explore() with the device's capital (`retention`, a flat charge with no
    membranes) and running cost (`extra_opex`, per kilo grown: explore divides it by the harvested share itself; until
    2026-11-20 the cost per kilo harvested was passed and so divided twice), then every cost per kg divided by the share of grown cells that survive
    the device. The TFF loop is explore()'s own default, so it is explore() itself (its sizing here gives the same numbers)."""
    kw = dict(kw or {})
    d = duty(kw)
    sz = sizing(device, kw, None if device in PARTICLES else d)
    run = particle_case(device, kw)[0] if device in PARTICLES else kw      # the case as it runs with the device
    if device == "tff":
        r = fp.explore(**kw)
    else:
        r = fp.explore(**{**run, "retention": sz["capex_k_m3"], "extra_opex": kw.get("extra_opex", 0.0) + sz["cons_kg_grown"]})
        if device not in PARTICLES:
            # size the device from the design it runs (2026-11-25): the engine now picks the gas flow and how thin the culture
            # is, and with the engine's own filter loop (duty) it may pick another design than with this device, so a device
            # sized on the first duty ran a culture it was not sized for. RESIZE_PASSES passes; the page's rtCost the same
            for _ in range(RESIZE_PASSES):
                sz = sizing(device, kw, duty(kw, result=r))
                r = fp.explore(**{**run, "retention": sz["capex_k_m3"], "extra_opex": kw.get("extra_opex", 0.0) + sz["cons_kg_grown"]})
    total = r["total"] / (1.0 - sz["loss"])
    return {**sz, "total": total, "base": d["result"]["total"], "delta": total - d["result"]["total"],
            "capital": r["capital"] / (1.0 - sz["loss"]),          # the plant's yearly charge per kilo, as the page's rtCost gives it
            "density": r.get("density"), "medium_l": r.get("medium_l"), "output": r.get("output"), "limit": r.get("limit")}


# What sizing() reads for each device, by the short key the page's JavaScript uses (page_retention.js): {device: {short: input}}
_JS_INPUTS = {
    "atf": dict(flux="rt_flux_lmh", area="rt_atf_area", price="rt_atf_price",
                mem_price="rt_membrane_price", mem_life="rt_membrane_life"),
    "tff": dict(flux="rt_flux_lmh", hw="rt_tff_hw", install="rt_install", mem_price="rt_membrane_price",
                mem_life="rt_membrane_life"),
    **{dev: dict(flux=f, hw=h, price=p, life=l, install="rt_install") for dev, (f, h, p, l) in _MEMB.items()},
    "settler": dict(v_frac="rt_settle_v_frac", holdup="rt_settle_holdup", price="rt_settle_price"),
    "acoustic": dict(cap="rt_acoustic_cap", price="rt_acoustic_price", install="rt_install"),
    "discstack": dict(conc="rt_ds_conc", cap="rt_ds_cap", spares="rt_ds_spares", price="rt_ds_price", lysis="rt_ds_lysis",
                      power="rt_ds_power", maint="rt_maint", power_price="ge_power_price"),
    "hydrocyclone": dict(split="rt_hc_split", eff="rt_hc_eff", price="rt_hc_price"),
}


def js_model() -> dict:
    """What the page's JavaScript needs to size and price a device (page_retention.js mirrors duty, sizing and
    scenario_cost; tests/run_parity.py checks the two agree). Every device of ORDER but the hoped-for one and the two
    particle routes, which need the oxygen profile of an aggregate and stay in Python (`python_only`)."""
    ported = [k for k in ORDER if k != "hoped" and k not in PARTICLES]
    devices = {}
    for k in ported:
        D = DEVICES[k]
        devices[k] = {"key": k, "name": D["name"], "how": D["how"], "shown": D["shown"],
                      "inputs": {short: value(name) for short, name in _JS_INPUTS[k].items()}
                                | ({"factor": atf_factor()} if k == "atf" else {}),
                      "phi_max": value(D["phi_max"]) if D["phi_max"] else None}
    return {"order": ported, "devices": devices, "memb": list(_MEMB), "default": "tff",
            "particles": {k: {"key": k, "name": DEVICES[k]["name"], "how": DEVICES[k]["how"], "shown": DEVICES[k]["shown"],
                              "python_only": True} for k in PARTICLES},
            "not_costed": {k: {"name": n, "reason": why} for k, (n, why) in NOT_COSTED.items()},
            "holdup_max": value("rt_settle_holdup_max"), "hours": HOURS, "resize_passes": RESIZE_PASSES}


# The inputs behind each device, and which way is cheaper (+1: a higher value is cheaper; -1: a lower one is)
_DRIVERS = {
    "hoped": (("pf_capex_retention", -1),),
    "reuse": (("rt_flux_lmh", +1), ("rt_tff_hw", -1), ("rt_install", -1), ("rt_membrane_price", -1), ("rt_reuse_life", +1)),
    "dialyser": (("rt_dial_flux", +1), ("rt_dial_hw", -1), ("rt_install", -1), ("rt_dial_price", -1), ("rt_dial_life", +1)),
    "ceramic": (("rt_flux_lmh", +1), ("rt_ceramic_hw", -1), ("rt_install", -1), ("rt_ceramic_price", -1), ("rt_ceramic_life", +1)),
    "atf": (("rt_flux_lmh", +1), ("rt_atf_price", -1), ("rt_membrane_price", -1), ("rt_membrane_life", +1)),
    "tff": (("rt_flux_lmh", +1), ("rt_tff_hw", -1), ("rt_install", -1), ("rt_membrane_price", -1), ("rt_membrane_life", +1)),
    "settler": (("rt_settle_price", -1), ("rt_settle_v_frac", +1), ("rt_settle_holdup", -1)),
    "acoustic": (("rt_acoustic_cap", +1), ("rt_acoustic_price", -1), ("rt_install", -1)),
    "discstack": (("rt_ds_cap", +1), ("rt_ds_price", -1), ("rt_ds_conc", +1), ("rt_ds_lysis", -1), ("rt_ds_power", -1),
                  ("rt_maint", -1)),
    "hydrocyclone": (("rt_hc_eff", +1), ("rt_hc_split", +1), ("rt_hc_price", -1)),
    "aggregates": (("rt_agg_d_min_um", +1), ("rt_agg_d_max_um", -1), ("rt_agg_cell_share", +1), ("rt_o2_diff_tissue", +1),
                   ("rt_o2_prolif", -1), ("rt_o2_sherwood", +1), ("rt_part_phi_max", +1), ("rt_part_loss", -1), ("rt_settle_price", -1),
                   ("rt_settle_v_frac", +1)),
    "microcarriers": (("rt_mc_d_um", -1), ("rt_mc_cells_cm2", +1), ("rt_mc_solids", -1), ("rt_mc_price", -1),
                      ("rt_part_phi_max", +1), ("rt_part_loss", -1), ("rt_settle_price", -1), ("rt_settle_v_frac", +1)),
}


def _with(settings: dict):
    """Context manager: run with some inputs set to other values (restores them after)."""
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


def scenario_range(device: str, kw: dict | None = None) -> dict:
    """The case's cost with the device at the favourable and the unfavourable end of all its own inputs together:
    {'low': scenario_cost, 'mid': ..., 'high': ...}. The case itself is not varied."""
    from inputs import prior
    ends = {}
    for tag, sign in (("low", +1), ("high", -1)):
        st = {}
        for name, better in _DRIVERS[device]:
            _k, lo, hi, _m, _n = prior(name)
            st[name] = hi if better * sign > 0 else lo
        with _with(st):
            ends[tag] = scenario_cost(device, kw)
    return {"low": ends["low"], "mid": scenario_cost(device, kw), "high": ends["high"]}


def table() -> dict:
    """{case: {device: scenario_cost}} for the three cases."""
    return {name: {dev: scenario_cost(dev, kw) for dev in ORDER} for name, kw in cases().items()}


def summarise_duty() -> None:
    print("The duty of the retention device (20 m3 tank, 16 m3 of liquid):")
    print(f"  {'case':<10}{'g/L':>6}{'phi':>6}{'kg/h':>7}{'medium m3/h':>13}{'VVD':>6}{'bleed m3/h':>12}{'permeate m3/h':>15}{'VVD':>6}")
    for name, kw in cases().items():
        d = duty(kw)
        print(f"  {name:<10}{d['density']:>6.0f}{d['phi']:>6.2f}{d['kg_h']:>7.1f}{d['medium_m3_h']:>13.2f}{d['vvd_medium']:>6.2f}"
              f"{d['bleed_m3_h']:>12.3f}{d['permeate_m3_h']:>15.2f}{d['vvd_permeate']:>6.2f}")


def summarise() -> None:
    summarise_duty()
    for name, rows in table().items():
        print(f"\n  {name}: cost per kg of wet cells with each device (deltas against the model's default, the TFF loop)")
        for dev, c in rows.items():
            extra = ""
            if c.get("units"):
                extra += f" units {c['units']:.0f}"
            if c.get("area_m2"):
                extra += f" area {c['area_m2']:.0f} m2"
            if c.get("holdup_m3"):
                extra += f" outside the tank {c['holdup_m3']:.2f} m3"
            if c.get("passes_day"):
                extra += f" passes {c['passes_day']:.2f}/day"
            print(f"    {DEVICES[dev]['name']:<38} ${c['total']:7.2f} ({c['delta']:+6.2f})  capital ${c['capex_k_m3']:6.0f}k/m3  "
                  f"running ${c['cons_kg']:5.2f}/kg  loss {c['loss'] * 100:4.1f}%{'  BEYOND WHAT IS SHOWN' if c['beyond'] else ''}{'  NOT POSSIBLE' if c['impossible'] else ''}{'  HELD TO %.0f g/L' % c['density'] if (c.get('note') or {}).get('capped') else ''}{extra}")


def density_scan(kw: dict | None = None, caps=(258.0, 220.0, 180.0, 140.0, 100.0), membrane_life: float | None = None) -> list:
    """Does a thinner culture pay once filtering costs money? The case's cost with its density held at each cap (a
    density setpoint below what the tank allows), with the default filter loop. A thinner culture filters fewer litres a
    kilo, because the bleed of cells carries more of the liquid out, but each tank makes fewer kilos. Returns
    [(cap, total, membranes $/kg, plant capital $/kg)]."""
    rows = []
    for cap in caps:
        r = fp.explore(**{**(kw or {}), "vm": {"caps": {"chosen density": float(cap)}},
                          **({} if membrane_life is None else {"membrane_life": membrane_life})})
        rows.append((float(cap), r["total"], r["membranes"], r["capital"]))
    return rows


def oxygen_sizes(setpoints=(0.10, 0.21, 0.28)) -> dict:
    """{case: {'own': (setpoint, diameter), setpoint: diameter}}: the largest aggregate (um) whose middle stays at
    rt_o2_prolif, for each case's cells at its own dissolved-oxygen setpoint and at each of `setpoints` (mmol/L)."""
    out = {}
    for name, kw in cases().items():
        c, cs = _cells(kw), surface_oxygen(kw)
        out[name] = {"own": (cs, critical_diameter(c, cs)), **{x: critical_diameter(c, x) for x in setpoints}}
    return out


def aggregate_scan(kw: dict | None = None, sizes=(200.0, 300.0, 400.0, 500.0, 600.0), setpoints=(None, 0.28)) -> list:
    """The aggregate route's cost when aggregates are let grow larger before they are broken up, at the case's own
    dissolved-oxygen setpoint and at a higher one (which raises the size that stays oxygenated but lowers the tank's oxygen
    transfer, so its density). Returns [(setpoint, largest aggregate um, growth lost, density g/L, $/kg)]."""
    kw = dict(kw if kw is not None else cases()["central"])
    rows = []
    for sp in setpoints:
        k = kw if sp is None else {**kw, "do_mmol": sp}
        for dmax in sizes:
            with _with({"rt_agg_d_max_um": dmax}):
                c = scenario_cost("aggregates", k)
            rows.append((surface_oxygen(k), dmax, c["note"]["penalty"], c["density"], c["total"]))
    return rows


def summarise_particles() -> None:
    print("\n  cells in particles (research_notes/retention_aggregates.md):")
    for name, row in oxygen_sizes().items():
        print(f"    {name:<10} largest aggregate whose middle grows: {row['own'][1]:.0f} um at its own {row['own'][0]:.2f} mmol/L; "
              + ", ".join(f"{row[x]:.0f} um at {x:.2f}" for x in (0.10, 0.21, 0.28)))
    for name, kw in cases().items():
        for dev in PARTICLES:
            c = scenario_cost(dev, kw)
            p, n = c["particle"], c["note"]
            extra = (f"; carrier {p['carrier_kg']:.2f} kg dry and {p['bead_l_kg']:.1f} L of bead per kg of cells "
                     f"({p['carrier_wet_share']:.0%} of the wet product)" if dev == "microcarriers" else "")
            print(f"    {name:<10}{dev:<14} cells {p['share']:.0%} of a particle; cap {n['cap']:.0f} g/L"
                  f"{' (holds the case to it, from ' + format(n['density_wanted'], '.0f') + ')' if n['capped'] else ''}; "
                  f"growth lost {n['penalty']:.1%}; particle settles {c['particle_cm_h']:.0f} cm/h alone, plates at "
                  f"{c['settle_cm_h']:.1f} cm/h, {c['area_m2']:.1f} m2, {c['stay_min']:.0f} min on the plates{extra}")
    print("    central, aggregate route against the largest aggregate allowed (setpoint, um, growth lost, g/L, $/kg):")
    for sp, dmax, pen, x, t in aggregate_scan():
        print(f"      {sp:.2f} mmol/L  {dmax:4.0f} um  {pen:5.1%}  {x:4.0f} g/L  ${t:.2f}")


def summarise_ranges() -> None:
    print("\n  ranges (each device's own inputs at their favourable / unfavourable ends):")
    for name, kw in cases().items():
        for dev in ORDER:
            r = scenario_range(dev, kw)
            print(f"    {name:<10}{DEVICES[dev]['name']:<38} ${r['low']['total']:7.2f} - ${r['mid']['total']:7.2f} - ${r['high']['total']:7.2f}"
                  f"   capital ${r['low']['capex_k_m3']:5.0f}k - {r['high']['capex_k_m3']:5.0f}k per m3")


if __name__ == "__main__":
    summarise()
    summarise_particles()
    summarise_ranges()
    print("\n  does a thinner culture pay? central scenario, density capped at each value (the engine may run it thinner still; cost; membranes; plant capital):")
    for life in (None, 900.0):
        print("    membrane life " + ("default" if life is None else f"{life:.0f} L/m2") + ": " +
              "; ".join(f"{c:.0f} g/L ${t:.2f} (${m:.1f}, ${k:.1f})" for c, t, m, k in density_scan(cases()["central"], membrane_life=life)))
