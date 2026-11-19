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
# 2026-11-19 repin: nutrient floor $2.00, growth factors inside complete media prices (Central and Cautious lose their
# growth-factor cost), Best's medium at the nutrient floor in place of $0.15 a litre
GOLDEN_SCAN = {
    "best": {16.0: 9.0304, 24.0: 9.9613, 43.0: 15.8043},
    "central": {16.0: 22.1112, 24.0: 24.0261, 36.0: 26.4296, 43.0: 27.7430},
    "cautious": {16.0: 27.0395, 36.0: 34.2364, 43.0: 36.4185},
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
    # --- pins ---
    pins = [("central $1 insulin", tab["central"][1.0]["insulin"]["shared"], 0.6816),
            ("central $1 transferrin", tab["central"][1.0]["transferrin"]["shared"], 1.1685),
            ("central $1 FGF", tab["central"][1.0]["fgf"]["shared"], 63.1958),
            ("central $1 TGF-beta", tab["central"][1.0]["tgfb"]["shared"], 1834.2358),
            ("best $3 insulin", tab["best"][3.0]["insulin"]["shared"], 5.1305),
            ("central reuse, full price", G.reuse("central")["full_reuse"], 1.9871),
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
