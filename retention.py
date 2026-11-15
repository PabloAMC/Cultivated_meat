#!/usr/bin/env python3
"""
retention.py — what it takes to hold the cells back in a 20 m3 perfusion tank, and what it costs.

Why
---
Every cost scenario uses a 20 m3 stirred tank in perfusion: fresh medium flows through, a device holds the cells back,
and the harvest is a steady bleed of cells. Nobody has run animal cells in perfusion above about 4 m3. The model charges
a hoped-for device at `pf_capex_retention` ($89k per m3 of tank, from one design study). If perfusion fails at 20 m3, the
central scenario moves from about $18 to $45-49 a kilo (vessels.py). This module sizes the real devices for the real duty.

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


def duty(kw: dict | None = None) -> dict:
    """What the retention device must do in a case (explore arguments): flows in m3/h, vessel volumes a day, the cells'
    volume fraction, and the case's own result."""
    kw = dict(kw or {})
    r = fp.explore(**kw)
    v = kw.get("vessel_m3", 20.0)
    liquid = value("pf_working_volume") * v                                # m3
    tonnes = r["output"] * v                                                 # t of wet cells per tank-year
    harvest = tonnes * 1000.0 / (HOURS * r["uptime"])                        # kg/h while the tank runs
    medium = r["medium_l"] * harvest / 1000.0                                # m3/h
    bleed = harvest / r["density"]                                           # m3/h of whole culture (kg/h over kg/m3)
    permeate = max(0.0, medium - bleed)
    phi = r["density"] / (value("pf_cell_density") * 1000.0)                # volume fraction of cells
    return {"vessel_m3": v, "liquid_m3": liquid, "density": r["density"], "phi": phi, "kg_h": harvest,
            "kg_year": tonnes * 1000.0, "medium_m3_h": medium, "bleed_m3_h": bleed, "permeate_m3_h": permeate,
            "outflow_m3_h": medium, "vvd_medium": medium * 24.0 / liquid, "vvd_permeate": permeate * 24.0 / liquid,
            "uptime": r["uptime"], "result": r}


# ----------------------------------------------------------------------------
# The devices
# ----------------------------------------------------------------------------
# Each: name, how it holds cells back, what it is sized on, the densest culture (volume fraction) it has held, the largest
# scale shown, and where its cost goes. The numbers are in inputs.py `rt_*`; the evidence in research_notes/retention_devices.md.
DEVICES = {
    "hoped": dict(name="Hoped-for device (the model's default)", how="a filter-free device one design study priced",
                  shown="none: Pasitka's design study does not say what it is", phi_max=None),
    "atf": dict(name="ATF hollow-fibre filter", how="a diaphragm pulls culture back and forth through hollow fibres",
                shown="50 days on 50 L at 1e8 cells/mL (Ott 2024); 1.3e8 for days in 4 L (Clincke 2013); units rated to 5,000 L",
                phi_max="rt_atf_phi_max"),
    "tff": dict(name="TFF hollow-fibre loop", how="a pump circulates culture past hollow fibres",
                shown="2.14e8 cells/mL for days in a 4 L bag (Clincke 2013); one fibre lasted 30 days; nothing published above pilot scale",
                phi_max="rt_tff_phi_max"),
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
}
NOT_COSTED = {"spin": ("Spin filter", "Its screen sits inside the tank, so its area grows with the tank's width, not its volume; "
                                     "shown only at about 1e7 cells/mL or less, and it clogs within weeks."),
              "ksep": ("Fluidized-bed centrifuge (kSep)", "One cycle holds about 2.9 kg of cells; the central duty passes "
                                                         "485 kg an hour, about 170 cycles an hour. The 6000S is discontinued.")}
ORDER = ("hoped", "atf", "tff", "settler", "acoustic", "discstack", "hydrocyclone")


def sizing(device: str, kw: dict | None = None, d: dict | None = None) -> dict:
    """Size a device for a case's duty. Returns: what it takes (units, m2), capital per m3 of tank ($k), running cost per kg of
    wet cells grown ($: membranes, power, maintenance), the share of grown cells it destroys or lets go (`loss`), the culture
    held outside the tank (m3), and whether the case's density is beyond what the device has held (`beyond`)."""
    d = duty(kw) if d is None else d
    v, liq, P, B, phi = d["vessel_m3"], d["liquid_m3"], d["permeate_m3_h"], d["bleed_m3_h"], d["phi"]
    kg = d["kg_year"]
    out = {"device": device, "units": 0.0, "area_m2": 0.0, "capex_k_m3": 0.0, "cons_kg": 0.0, "loss": 0.0, "holdup_m3": 0.0}
    perm_l_kg = P * 1000.0 / d["kg_h"]                                     # litres of permeate per kg grown
    membranes = perm_l_kg * value("rt_membrane_price") / value("rt_membrane_life")
    if device == "hoped":
        out["capex_k_m3"] = value("pf_capex_retention")
    elif device == "atf":
        n = math.ceil(P * 1000.0 / (value("rt_flux_lmh") * value("rt_atf_area")))
        out.update(units=n, area_m2=n * value("rt_atf_area"), cons_kg=membranes,
                   capex_k_m3=n * value("rt_atf_price") * value("rt_install") / v)
    elif device == "tff":
        area = P * 1000.0 / value("rt_flux_lmh")
        out.update(area_m2=area, cons_kg=membranes, capex_k_m3=area * value("rt_tff_hw") * value("rt_install") / v)
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
    else:
        raise KeyError(device)
    key = DEVICES[device]["phi_max"]
    out["phi_max"] = value(key) if key else None
    out["beyond"] = key is not None and phi > value(key) + 1e-9
    # not possible: a settler that would hold too much of the culture outside the tank, with no oxygen
    out["impossible"] = ("It would hold {:.0%} of the culture outside the tank, with no oxygen supply.".format(out["holdup_m3"] / liq)
                         if out["holdup_m3"] > value("rt_settle_holdup_max") * liq else "")
    return out


def scenario_cost(device: str, kw: dict | None = None) -> dict:
    """The case's cost per kg with this device in place of the model's hoped-for one: explore() with the device's capital
    (`retention`) and running cost (`extra_opex`), then every cost per kg divided by the share of grown cells that survive
    the device. No default changes."""
    kw = dict(kw or {})
    d = duty(kw)
    sz = sizing(device, kw, d)
    r = fp.explore(**{**kw, "retention": sz["capex_k_m3"], "extra_opex": kw.get("extra_opex", 0.0) + sz["cons_kg"]})
    total = r["total"] / (1.0 - sz["loss"])
    return {**sz, "total": total, "base": d["result"]["total"], "delta": total - d["result"]["total"]}


# The inputs behind each device, and which way is cheaper (+1: a higher value is cheaper; -1: a lower one is)
_DRIVERS = {
    "hoped": (("pf_capex_retention", -1),),
    "atf": (("rt_flux_lmh", +1), ("rt_atf_price", -1), ("rt_install", -1), ("rt_membrane_price", -1), ("rt_membrane_life", +1)),
    "tff": (("rt_flux_lmh", +1), ("rt_tff_hw", -1), ("rt_install", -1), ("rt_membrane_price", -1), ("rt_membrane_life", +1)),
    "settler": (("rt_settle_price", -1), ("rt_settle_v_frac", +1), ("rt_settle_holdup", -1)),
    "acoustic": (("rt_acoustic_cap", +1), ("rt_acoustic_price", -1), ("rt_install", -1)),
    "discstack": (("rt_ds_cap", +1), ("rt_ds_price", -1), ("rt_ds_conc", +1), ("rt_ds_lysis", -1), ("rt_ds_power", -1),
                  ("rt_maint", -1)),
    "hydrocyclone": (("rt_hc_eff", +1), ("rt_hc_split", +1), ("rt_hc_price", -1)),
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
        print(f"\n  {name}: cost per kg of wet cells with each device (the model's default is the first row)")
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
                  f"running ${c['cons_kg']:5.2f}/kg  loss {c['loss'] * 100:4.1f}%{'  BEYOND WHAT IS SHOWN' if c['beyond'] else ''}{'  NOT POSSIBLE' if c['impossible'] else ''}{extra}")


def summarise_ranges() -> None:
    print("\n  ranges (each device's own inputs at their favourable / unfavourable ends):")
    for name, kw in cases().items():
        for dev in ORDER:
            r = scenario_range(dev, kw)
            print(f"    {name:<10}{DEVICES[dev]['name']:<38} ${r['low']['total']:7.2f} - ${r['mid']['total']:7.2f} - ${r['high']['total']:7.2f}"
                  f"   capital ${r['low']['capex_k_m3']:5.0f}k - {r['high']['capex_k_m3']:5.0f}k per m3")


if __name__ == "__main__":
    summarise()
    summarise_ranges()
