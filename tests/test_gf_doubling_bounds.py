#!/usr/bin/env python3
"""test_gf_doubling_bounds.py — growth-factor prices and the fastest doubling time (gf_doubling_bounds.py).

Checks that required prices rebuild their cost target, that the per-litre price the module uses is the one explore() charges,
that reuse obeys the liquid balance of retention.duty, that the energy limit agrees with floor_physics.Cells, that the scan at
a scenario's own doubling time is the scenario, and pins the headline numbers. Run directly or under pytest.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import floor_physics as fp
import gf_doubling_bounds as G
import scenarios as S
from inputs import value

# $/kg of cells, each scenario's tank design held fixed, at other doubling times
# 2026-11-19 repin: nutrient floor $2.00, growth factors inside complete media prices (the low-lactate example and Cautious lose their
# growth-factor cost), Best's medium at the nutrient floor in place of $0.15 a litre
# 2026-11-19 audit batch: ammonia tolerance 4 mmol/L (the low-lactate example 28 -> 35 L/kg, Best 11.16 -> 13.75), lost runs pay for their
# membranes, and glucose from the cells' own balance (the cautious case, the published cells, 28 -> 95.5 L/kg, set by lactate)
# 2026-11-20 model batch: lactate tolerated 35 mmol/L (the cautious case 95.5 -> 146 L per kilo harvested; lactate now sets Best's
# litres too), bubble deaths and the harvest loss charged (a larger share of the cells grown the slower they grow), twice the crew,
# membrane life 2,415 L/m2, medium preparation with the medium passed. Before: best 10.5385 / 11.6738 / 16.5504, central 28.3001 /
# 30.3220 / 32.8028 / 34.1441, cautious 63.1348 / 84.9106 / 92.1653.
# 2026-11-20 final model: "best" is now the all-favourable case (scenarios.all_favourable, $7.62 at its own 16 h: Humbird's
# cell traits and lactate tolerance, 42 m3, dialyser-grade fibres), so its scan fell from 14.7554 / 18.7144 / 27.1815; the
# last engine fixes moved central (40.7736 / 44.7155 / 49.9616 / 53.0032) and cautious (124.1438 / 167.9874 / 183.1481).
GOLDEN_SCAN = {
    # 2026-11-21 (the building's power by floor and class, labour per tank, the floor's glucose, thinned tank designs, the
    # column on the filter loop): best 7.6209/8.8480/12.2433, central 40.0833/44.1421/49.4977/52.5557, cautious
    # 124.3331/169.8311/185.5915 before. Best at 43 h rose: its thinned recycled-oxygen design is chosen at 16 h and does not
    # suit slow cells
    # 2026-11-25 (the gas cap and loop thinning): the engine now picks the gas flow up to the cap and thins an overloaded column
    # loop itself, at every doubling time, so the design held fixed is the scenario's tank, column and cells, no longer a thinned
    # density chosen at the scenario's own doubling time. best 8.6524 -> 7.9720 (24 h), 13.6671 -> 11.3876 (43 h); central
    # 39.6525 -> 39.5912 (16 h), 43.1886 -> 43.8138 (24 h), 52.0237 -> 51.4158 (43 h); cautious 122.6137 -> 123.1127 (16 h),
    # 165.5675 -> 165.5430 (36 h), 181.1270 -> 179.9020 (43 h, own)
    # 2026-11-27 (nutrient balance): best 6.9686 -> 7.0205, 7.9720 -> 8.0285, 11.3876 -> 11.4507
    "best": {16.0: 7.0205, 24.0: 8.0285, 43.0: 11.4507},
    "central": {16.0: 39.5912, 24.0: 43.8138, 36.0: 48.6815, 43.0: 51.4158},
    "cautious": {16.0: 123.1127, 36.0: 165.5430, 43.0: 179.9020},
}

def close(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(1.0, abs(b))


def check() -> list:
    fails = []
    # --- A. required prices rebuild the target ---
    if not close(sum(G.shares().values()), 1.0, 1e-12):
        fails.append("cost shares do not sum to 1")
    tab = G.price_table()
    for k in G.SCENARIOS:
        L = tab[k]["litres"]
        if not close(L, S.run(S.SCENARIOS[k].choice)["medium_l"], 1e-12):
            fails.append(f"{k}: litres are not explore's")
        for T in G.TARGETS:
            r = tab[k][T]
            if not close(L * sum(G.conc(f) * r[f]["shared"] for f in G.FACTORS), T, 1e-9):
                fails.append(f"{k} ${T}: shared prices do not give the target")
            for f in G.FACTORS:
                if not close(L * G.conc(f) * r[f]["alone"], T, 1e-9):
                    fails.append(f"{k} ${T} {f}: 'alone' price does not give the target")
                if not close(r[f]["shared"] / r[f]["humbird_2025"], r["x_humbird"], 1e-9):
                    fails.append(f"{k} ${T} {f}: shared price is not a common fraction of Humbird's")
        # twice the budget, twice the price
        if not close(tab[k][2.0]["insulin"]["shared"], 2.0 * tab[k][1.0]["insulin"]["shared"], 1e-9):
            fails.append(f"{k}: price is not linear in the target")
    # the price per litre is the one explore() charges: growth_factors = 1 gives per-litre x litres
    for k in G.SCENARIOS:
        r = S.run(S.SCENARIOS[k].choice, growth_factors=1.0)
        if not close(r["growth_factors"], G.model_per_litre() * r["medium_l"], 1e-9):
            fails.append(f"{k}: explore's growth-factor cost is not the module's per-litre price x litres")
        if not close(S.run(S.SCENARIOS[k].choice)["growth_factors"], G.reuse(k)["own"], 1e-9):
            fails.append(f"{k}: the scenario's own growth-factor cost is not reuse()['own']")
    # Humbird's four prices at his concentrations give his $3.13/kg at 8.65 L/kg in his dollars
    if not close(G.humbird_per_litre(False) * 8.65, 3.13, 0.02):
        fails.append("Humbird's per-litre price x 8.65 L/kg should be about $3.13/kg")
    # the volume line round trip
    v = G.meat_volume_for_price(2.0, "insulin", 28.0)
    if not close(G.price_at_volume(v["meat_Mt_y"], "insulin", 28.0), 2.0, 1e-9):
        fails.append("volume line: price at the volume found is not the price asked")
    if not close(G.cost_on_volume_line(G.meat_volume_for_total(3.0, 28.0), 28.0), 3.0, 1e-6):
        fails.append("volume line: total cost at the volume found is not the target")
    # --- reuse ---
    for k in G.SCENARIOS:
        r = G.reuse(k)
        if not close(r["bleed_l"] + r["permeate_l"], r["litres"], 1e-9):
            fails.append(f"{k}: bleed + permeate != medium")
        if not (r["full_reuse"] < r["full_reuse_fgf_decay"] < r["full_price"]):
            fails.append(f"{k}: reuse costs out of order (reuse < reuse with FGF decay < no reuse)")
        if not close(r["full_price"] - r["full_reuse"], G.model_per_litre() * (r["permeate_l"] - r["fill_l"]), 1e-9):
            fails.append(f"{k}: the saving is not the permeate litres less the first fill")
        if r["fgf_litres_with_decay"] > r["litres"] + 1e-9:
            fails.append(f"{k}: FGF litres exceed fresh medium")
        # a protein that does not decay costs what the bleed carries out
        if not close(G.reuse(k, fgf_half_life_h=1e9)["full_reuse_fgf_decay"], r["full_reuse"], 1e-6):
            fails.append(f"{k}: a stable FGF should match bleed-only reuse")
    # --- B. energy ---
    c = fp.Cells()
    for k in (1.5, 2.0, 3.0):
        m = G.model_energy_limit(k)
        if not close(m["qo2"], k * c.qo2, 1e-9):
            fails.append(f"model energy limit at {k}x: Cells.qo2 is not {k} x its 24 h value")
        e = G.energy_limit(k, growth_atp=G.model_growth_atp())
        if not close(e["doubling_h"], m["doubling_h"], 1e-9):
            fails.append(f"energy_limit with the model's growth cost should equal model_energy_limit at {k}x")
    d = [G.energy_limit(k)["doubling_h"] for k in (1.0, 1.5, 2.0, 3.0)]
    if not all(a > b for a, b in zip(d, d[1:])):
        fails.append("more respiration should mean faster doubling")
    if not close(G.energy_limit(1.0)["doubling_h"], 24.0, 1e-9):
        fails.append("at West's own rate the doubling time is 24 h")
    b = G.biosynthesis_atp()
    if not close(sum(b[x] for x in ("protein", "lipid", "rna_dna", "carbohydrate")), b["dry"], 1e-9):
        fails.append("biosynthesis parts do not sum")
    if not G.biosynthesis_atp(lipid_made=False)["wet"] < b["wet"]:
        fails.append("fed lipid should cost less ATP")
    if not (0.0 < G.implied_upkeep_share(b["wet"]) < 1.0):
        fails.append("bottom-up growth cost should leave a share for upkeep")
    ch = G.cho_check()
    if not (0.95 * ch["measured_lo"] <= ch["model"] <= 1.05 * ch["measured_hi"]):
        fails.append(f"model oxygen uptake at CHO's doubling time {ch['model']:.3f} is outside the measured range")
    t = G.translation_limit()
    if not close(G.translation_limit(rna_share=G.rna_share_for(t["doubling_h"]))["doubling_h"], t["doubling_h"], 1e-9):
        fails.append("rna_share_for does not invert translation_limit")
    # --- scan ---
    for k in G.SCENARIOS:
        own = S.SCENARIOS[k].choice
        own_h = S.explore_kwargs(own)["doubling_h"]
        sc = G.scan_doubling(k, (own_h, 16.0, 24.0, 43.0))
        if not close(sc[own_h]["total"], S.run(own)["total"], 1e-12):
            fails.append(f"{k}: the scan at its own doubling time is not the scenario")
        tots = [G.scan_doubling(k, (16.0, 20.0, 24.0, 30.0, 36.0, 43.0))[h]["total"] for h in (16.0, 20.0, 24.0, 30.0, 36.0, 43.0)]
        if not all(a < b for a, b in zip(tots, tots[1:])):
            fails.append(f"{k}: a slower doubling time should cost more")
        for h, want in GOLDEN_SCAN[k].items():
            if not close(G.scan_doubling(k, (h,))[h]["total"], want, 1e-4):
                fails.append(f"{k} at {h} h: {G.scan_doubling(k, (h,))[h]['total']:.4f} != pinned {want}")
    # 2026-11-19 audit batch: the cautious case no longer shares the low-lactate example's litres (95.5 against 35 L/kg), so it needs lower
    # prices than the low-lactate example, and Best (13.75 L/kg) allows higher ones. The note's table has a row for each.
    # (2026-11-20, final model: 146.2, 38.8 and 11.7 L per kilo harvested; the order holds.)
    if not (tab["cautious"]["litres"] > tab["central"]["litres"] > tab["best"]["litres"]):
        fails.append("litres should rise from Best to the low-lactate example to the cautious case")
    if not (tab["cautious"][1.0]["x_humbird"] < tab["central"][1.0]["x_humbird"] < tab["best"][1.0]["x_humbird"]):
        fails.append("the cautious case should need the lowest prices and Best the highest")
    # lactate sets the cautious case's medium, and glucose follows oxygen use, so its litres fall with speed; ammonia holds
    # the low-lactate example's litres whatever the doubling time
    sc_c = G.scan_doubling("cautious", (16.0, 43.0))
    if not (sc_c[43.0]["medium_set_by"] == "lactate" and sc_c[16.0]["medium_l"] < sc_c[43.0]["medium_l"]):
        fails.append("the cautious case's medium should be set by lactate and shrink with speed")
    # 2026-11-20 model batch: ammonia still sets it at every doubling time, and the litres per kilo GROWN are still the same
    # (35.0). The litres explore reports are per kilo HARVESTED, and bubbles kill a larger share of slow cells (13% of the cells
    # grown at 43 h, 5% at 16 h), so those now rise with the doubling time: 37.5 at 16 h, 41.1 at 43 h. The check compares per
    # kilo grown, and asks for the rise per kilo harvested.
    sc_m = G.scan_doubling("central", (16.0, 43.0))
    grown = {h: sc_m[h]["medium_l"] * sc_m[h]["harvested_share"] for h in sc_m}
    if not (sc_m[43.0]["medium_set_by"] == sc_m[16.0]["medium_set_by"] == "ammonia" and close(grown[16.0], grown[43.0], 1e-9)):
        fails.append("the low-lactate example's medium should be set by ammonia at every doubling time, at the same litres per kilo grown")
    if not sc_m[16.0]["medium_l"] < sc_m[43.0]["medium_l"]:
        fails.append("per kilo harvested, slower cells should need more medium (bubbles kill a larger share of them)")
    # --- pins ---
    # 2026-11-19 audit batch: the low-lactate example's litres 28 -> 35 (ammonia tolerance 5 -> 4 mmol/L) lower every required price by a
    # fifth; Best's litres 11.16 -> 13.75 (ammonia now sets them, not lactate) lower its prices by 19%
    # 2026-11-20 model batch: litres per kilo harvested: the low-lactate example 35 -> 40.1, Best 13.75 -> 18.65 (lactate sets
    # them at 35 mmol/L), the cautious case 95.5 -> 146.2, so every required price fell: central $1 insulin 0.5453 -> 0.4759,
    # transferrin 0.9348 -> 0.8158, FGF 50.5566 -> 44.1185, TGF-beta 1467.3886 -> 1280.5239; best $3 insulin 4.1641 -> 3.0695;
    # cautious $1 insulin 0.1998 -> 0.1305.
    # Reuse at full price 1.9871 -> 2.5973: the model's price per litre is now Humbird's own (his $3.13 over his 8.65 L/kg, not
    # over 11.2). This pin rests on retention.duty's bleed (5.24 L per kilo), which is per kilo harvested at the density, where
    # explore's own is 6.00 (per kilo grown, over the harvested share): reported 2026-11-20 with test_frontier's two failing
    # checks. With explore's bleed the figure would be about 2.95. Repin when the two agree.
    # 2026-11-20 final model: retention.duty now bleeds per kilo grown, so its bleed is explore's (7.22 L per kilo harvested in
    # the low-lactate example, the culture that leaves with the cells), and reuse at full price is 3.5484. The litres moved
    # again (the low-lactate example 40.1 -> 38.8; the all-favourable case 18.65 -> 11.7, ammonia sets them, since it takes
    # Humbird's 50 mmol/L of lactate tolerated): central $1 insulin 0.4759 -> 0.4916, transferrin 0.8158 -> 0.8427, FGF
    # 44.1185 -> 45.5783, TGF-beta 1280.5239 -> 1322.8953; best $3 insulin 3.0695 -> 4.8992; cautious unchanged.
    pins = [("central $1 insulin", tab["central"][1.0]["insulin"]["shared"], 0.4916),
            ("central $1 transferrin", tab["central"][1.0]["transferrin"]["shared"], 0.8427),
            ("central $1 FGF", tab["central"][1.0]["fgf"]["shared"], 45.5783),
            ("central $1 TGF-beta", tab["central"][1.0]["tgfb"]["shared"], 1322.8953),
            ("best $3 insulin", tab["best"][3.0]["insulin"]["shared"], 4.7252),   # 4.8992 until 2026-11-21
            # 2026-11-25 (the gas cap and loop thinning): 0.1305 -> 0.1338 (the cautious case's litres 146.2 -> 142.6 per kilo harvested)
            ("cautious $1 insulin", tab["cautious"][1.0]["insulin"]["shared"], 0.1338),
            ("central reuse, full price", G.reuse("central")["full_reuse"], 3.2475),   # 3.5484 until 2026-11-21
            # 0 since 2026-11-19 (were 0.5961 and 1.9183): their complete media carry the growth factors in the price
            ("central own, reuse", G.reuse("central")["own_reuse"], 0.0),
            ("cautious own, reuse", G.reuse("cautious")["own_reuse"], 0.0),
            ("bottom-up ATP per g wet", G.biosynthesis_atp()["wet"], 15.7986),
            ("energy limit at 2x, bottom-up", G.energy_limit(2.0)["doubling_h"], 9.1139),
            ("energy limit at 2x, model split", G.model_energy_limit(2.0)["doubling_h"], 8.0),
            ("translation limit at 5% RNA", G.translation_limit()["doubling_h"], 15.2884)]
    for name, got, want in pins:
        if not close(got, want, 1e-4):
            fails.append(f"{name}: {got:.4f} != pinned {want}")
    return fails


def test_gf_doubling_bounds():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the growth-factor and doubling-time bounds hold." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
