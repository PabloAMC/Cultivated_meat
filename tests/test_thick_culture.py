#!/usr/bin/env python3
"""test_thick_culture.py — how thick a culture can be (thick_culture.py).

Checks the viscosity laws against the model's own (gas_exchange.viscosity), the stirrer and oxygen arithmetic, the limits of three
tanks, and the cost of each scenario at other density limits; and that nothing the model reports has moved (258 g/L is still
the default, and a cap of 258 reproduces every scenario's own cost). Run directly or under pytest.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import floor_physics as fp
import gas_exchange as ge
import scenarios as S
import thick_culture as TC
from inputs import value

# $/kg: the design held, loop checks off ('fixed') and the design chosen again with the loop checks ('checked'), at each density limit
# repinned 2026-11-19: nutrient floor $2.00 (+$0.30 where it binds), growth factors inside complete media prices
# 2026-11-19 audit batch: ammonia tolerance 4 mmol/L (more medium and membranes a kilo), membranes for lost runs, and glucose
# from the cells' balance (cautious: the published cells' lactate sets 95 L/kg, $36.42 -> $92.17)
GOLDEN_CAP = {
    # 2026-11-19 restructure: the best case's cells weigh 2 ng (were 3): oxygen limits its tank at 218 g/L, so a thicker limit no longer helps
    "best":         {180.0: (11.8378, 11.8185), 320.0: (11.6738, 11.6738), 400.0: (11.6738, 11.6738)},
    "central":      {180.0: (33.1795, 33.1795), 320.0: (32.8028, 32.8028), 400.0: (32.8028, 32.8028)},
    "central_lean": {180.0: (30.1249, 30.1249), 320.0: (29.9417, 29.9417), 400.0: (29.9417, 29.9417)},
    "cautious":     {180.0: (92.1653, 92.1653), 320.0: (92.1653, 92.1653), 400.0: (92.1653, 92.1653)},
}
# cost if viscosity lowers the oxygen a sparger can feed (Best takes its oxygen from the closed loop, so it does not move)
# 2026-11-19 audit batch: the same three changes; the viscosity-corrected oxygen limits (151 and 103 g/L) do not move
GOLDEN_O2 = {"central": (34.4508, 150.69), "cautious": (94.3605, 102.72)}


def close(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(1.0, abs(b))


def check() -> list:
    fails = []
    # nothing in the model moved
    if value("pf_x_visc") != 258.0:
        fails.append("the model's default density limit has moved")
    # the viscosity law is the model's own
    for x in (50.0, 120.0, 258.0, 400.0):
        if not close(TC.apparent_viscosity(x, "thomas", thin=1.0), ge.viscosity(x), 1e-12):
            fails.append(f"Thomas viscosity at {x} g/L differs from gas_exchange.viscosity")
    hb = TC.humbird_basis()
    if not (close(hb["cells_ml"], 86e6, 1e-9) and 0.248 < hb["phi"] < 0.250 and 17.6 < hb["diameter_um"] < 17.8):
        fails.append(f"258 g/L should be 86 million 17.7 um cells/mL at a volume fraction of 0.249: {hb}")
    if not (2.41 < hb["thomas"] < 2.42 and 2.18 < hb["krieger"] < 2.20):
        fails.append(f"relative viscosity at 258 g/L (Thomas 2.42, Krieger 2.19): {hb['thomas']:.3f}, {hb['krieger']:.3f}")
    if TC.rel_viscosity(0.65, "krieger") != float("inf") or not TC.rel_viscosity(0.5, "thomas") > TC.rel_viscosity(0.5, "krieger"):
        fails.append("Krieger should diverge at the maximum packing and sit under Thomas at half cells")
    last = 0.0
    for p in (0.05, 0.1, 0.2, 0.3, 0.4, 0.5):
        v = TC.rel_viscosity(p, "thomas")
        if not v > last:
            fails.append("viscosity should rise with volume fraction")
        last = v
    # yield stress: small until the cells are close-packed (Iordan et al. scaling)
    if not (TC.yield_stress(258.0) < 1e-3 and 0.10 < TC.yield_stress(TC.x_of(0.5)) < 0.20):
        fails.append("yield stress: under 1e-3 Pa at a quarter cells, 0.1-0.2 Pa at half")
    # the stirrer
    prev = float("inf")
    for p in (0.1, 0.25, 0.4, 0.5):
        s = TC.stirrer(TC.x_of(p))
        if not (s["Re"] < prev):
            fails.append("Reynolds number should fall as the culture thickens")
        prev = s["Re"]
        if not s["turbulent"] or not close(s["power_for_same_mixing"], value("ge_stir_power"), 1e-12):
            fails.append(f"phi {p}: the flow should stay turbulent at 43 W/m3 with the same mixing time")
        if not s["cavern_fills_tank"]:
            fails.append(f"phi {p}: the yield-stress cavern should fill the tank")
    s = TC.stirrer(258.0)
    if not (46.0 < s["rpm"] < 48.0 and 2.0e5 < s["Re"] < 2.4e5):
        fails.append(f"stirrer at 258 g/L: about 47 rpm and Re 2.2e5, got {s['rpm']:.1f}, {s['Re']:.0f}")
    if not (550.0 < TC.turbulence_limit() < 650.0):
        fails.append(f"the stirrer should stay turbulent to about 600 g/L, got {TC.turbulence_limit():.0f}")
    if not close(TC.gas_power(258.0), 60.0, 0.02):
        fails.append("the rising gas should give about 60 W/m3 at 6 mm/s")
    # oxygen transfer
    if not close(TC.oxygen_limit(195.0, exponent=0.0), 195.0, 1e-9) or TC.oxygen_limit(float("inf")) != float("inf"):
        fails.append("with no viscosity exponent the oxygen limit is the model's; infinity stays infinite")
    for base in (120.0, 195.0, 301.0):
        xo = TC.oxygen_limit(base)
        if not (xo < base and close(xo, base * TC.kla_factor(xo), 1e-6)):
            fails.append(f"oxygen limit from {base}: not the fixed point of x = base x kLa factor")
    if not (150.0 < TC.oxygen_limit(195.0) < 156.0 and 212.0 < TC.oxygen_limit(301.4) < 216.0):
        fails.append("viscosity-corrected oxygen limits: 195 -> about 153, 301 -> about 214 g/L")
    # hold-up, settling, heat
    if not (TC.holdup(104.0) < TC.holdup(258.0) < TC.holdup(414.0) < 0.1):
        fails.append("gas hold-up should rise with density and stay under 10% at 414 g/L")
    if not (TC.settling(414.0)["v_cm_h"] < TC.settling(258.0)["v_cm_h"] < TC.settling(104.0)["v_cm_h"]):
        fails.append("settling should slow as the culture thickens")
    if not (TC.settling(258.0)["over_gas_velocity"] < 1e-3):
        fails.append("cells settle far slower than the gas rises")
    if not close(TC.heat_w_m3(120.0), 2400.0, 0.05):
        fails.append(f"heat at 120 g/L should be about 2.4 kW/m3 (gas_flow_cap.md), got {TC.heat_w_m3(120.0):.0f}")
    if not (390.0 < TC.heat_limit() < 400.0 and TC.heat_limit(aspect=0.5) < TC.heat_limit()):
        fails.append("the jacket's cooling limit: about 396 g/L in the tall tank, lower in a squat one")
    # which limit binds first
    L = TC.limits_at()
    if L["first"] != "CO2 removal" or not close(L["x"], 120.0, 1e-3):
        fails.append(f"in Humbird's plain tank CO2 binds first at 120 g/L, got {L['first']} at {L['x']:.0f}")
    Lc = TC.limits_at(S.explore_kwargs(S.SCENARIOS["central"].choice))
    if Lc["first"] != "oxygen supply, with viscosity" or not (148.0 < Lc["x"] < 154.0):
        fails.append(f"the low-lactate example: oxygen with viscosity should bind first near 151 g/L, got {Lc['first']} at {Lc['x']:.0f}")
    Lb = TC.limits_at(S.explore_kwargs(S.SCENARIOS["best"].choice))
    # 2026-11-19 restructure: with 2 ng cells (were Humbird's 3 ng) the best case's design is column + 1 bar without recycled oxygen,
    # and oxygen with viscosity binds first, near 167 g/L (it was the column loop's checks near 271)
    if Lb["first"] != "oxygen supply, with viscosity" or not (162.0 < Lb["x"] < 172.0):
        fails.append(f"Best: oxygen with viscosity should bind first near 167 g/L, got {Lb['first']} at {Lb['x']:.0f}")
    # the cost at other density limits
    for k in S.ORDER:
        own = S.run(S.SCENARIOS[k].choice)["total"]
        c = TC.cost_by_cap(k, caps=(180.0, 258.0, 320.0, 400.0))
        for mode in ("fixed", "checked"):
            if not close(c[258.0][mode]["cost"], own, 1e-9):
                fails.append(f"{k}: a cap of 258 g/L should give the scenario's own cost (${own:.4f}), got ${c[258.0][mode]['cost']:.4f}")
        costs = [c[x]["fixed"]["cost"] for x in (180.0, 258.0, 320.0, 400.0)]
        if any(b > a + 1e-9 for a, b in zip(costs, costs[1:])):
            fails.append(f"{k}: a thicker culture should never cost more with the design held ({costs})")
        for cap, (fixed, checked) in GOLDEN_CAP[k].items():
            if not (close(c[cap]["fixed"]["cost"], fixed, 1e-4) and close(c[cap]["checked"]["cost"], checked, 1e-4)):
                fails.append(f"{k} at {cap:.0f} g/L: ${c[cap]['fixed']['cost']:.4f}/${c[cap]['checked']['cost']:.4f} != pinned ${fixed}/${checked}")
    # cost if viscosity lowers the oxygen a sparger can feed
    for k in S.ORDER:
        v = TC.cost_viscous_oxygen(k)
        if v["oxygen_base"] == float("inf"):
            if not close(v["cost"], v["base_cost"], 1e-12):
                fails.append(f"{k}: oxygen by the loop does not depend on kLa; the cost should not move")
        elif k in GOLDEN_O2:
            want_cost, want_x = GOLDEN_O2[k]
            if not (close(v["cost"], want_cost, 1e-4) and abs(v["oxygen_viscous"] - want_x) < 1.0):
                fails.append(f"{k}: viscous-oxygen cost ${v['cost']:.4f} at {v['oxygen_viscous']:.0f} g/L != pinned ${want_cost} at {want_x}")
    return fails


def test_thick_culture():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the thick-culture limits hold." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
