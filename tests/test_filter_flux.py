#!/usr/bin/env python3
"""test_filter_flux.py — the filter's flux limit and measured membrane life (filter_flux.py)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import filter_flux as FF
import scenarios as S
from inputs import value


def close(a, b, tol=1e-3):
    return abs(a - b) <= tol * max(1.0, abs(b))


def check() -> list:
    fails = []
    a = 8.5e-6                                          # the research pass's cell radius (17 um across)
    # the formula as printed (Vyas 1999, Eq. 2.18) reproduces the two cells of the research pass's table
    for (L, g, pb), want in {(0.3, 1000.0, 0.25): 85.3, (1.0, 1000.0, 0.25): 57.0, (0.3, 4000.0, 0.12): 801.0}.items():
        got = FF.backtransport_lmh(pb, shear=g, length=L, radius=a)
        if not close(got, want, 0.01):
            fails.append(f"ceiling at L={L} shear={g} phi_b={pb}: {got:.1f} != {want}")
    # the scalings: proportional to shear, to L^(-1/3)
    b0 = FF.backtransport_lmh(0.25, shear=1000.0, length=0.3, radius=a)
    if not close(FF.backtransport_lmh(0.25, shear=2000.0, length=0.3, radius=a), 2.0 * b0, 1e-9):
        fails.append("flux should be proportional to the shear rate")
    if not close(FF.backtransport_lmh(0.25, shear=1000.0, length=2.4, radius=a), 0.5 * b0, 1e-9):
        fails.append("flux should fall with the cube root of the length")
    # 5 L/m2/h is far below the ceiling everywhere in the grid, even with the yeast shortfall
    for L in (0.3, 1.0):
        for g in (1000.0, 2000.0, 4000.0):
            for pb in (0.12, 0.25):
                m = FF.margin(pb, shear=g, length=L)
                if not m["cut_ratio"] > 2.0:
                    fails.append(f"ceiling too close to 5 L/m2/h at L={L} shear={g} phi_b={pb}")
    # the defaults are untouched, and a shorter membrane life costs more
    if not close(FF.cost_at("central", value("rt_flux_lmh"), value("rt_membrane_life")), S.run(S.SCENARIOS["central"].choice)["total"], 1e-12):
        fails.append("the default flux and life should reproduce the low-lactate example")
    c = [FF.cost_at("central", 5.0, life) for life in (3960.0, 1200.0, 450.0)]
    if not (c[0] < c[1] < c[2]):
        fails.append("a shorter life should cost more")
    # the default life is above the measured throughput
    if not value("rt_membrane_life") > 3.0 * value("ff_throughput_hi"):
        fails.append("the default life should be more than three times the measured throughput")
    if not close(FF.time_limited_life(5.0), value("rt_membrane_life"), 1e-3):
        fails.append("the default life is a 33-day run at 5 L/m2/h")
    # 2026-11-19 repin: growth factors inside complete media prices (the low-lactate example -$2.99), nutrient floor $2.00 (Best +$0.30)
    # 2026-11-19 audit batch: ammonia tolerance 4 mmol/L (the low-lactate example filters 35 L/kg, was 28) and a lost run
    # throws its membranes away early, so every litre filtered carries more membrane; both grow as the life shortens
    for (k, f, l), want in {("central", 5.0, 1200.0): 62.2305, ("central", 2.5, 450.0): 132.8657, ("best", 5.0, 1200.0): 20.1702}.items():   # best: 2 ng cells (2026-11-19)
        got = FF.cost_at(k, f, l)
        if not close(got, want, 1e-3):
            fails.append(f"{k} flux {f} life {l}: {got:.4f} != pinned {want}")
    # life and price act together: the membrane adds price / life per litre, so a shorter life costs nothing extra at the break-even price
    if not close(FF.break_even_price(value("rt_membrane_life")), value("rt_membrane_price"), 1e-12):
        fails.append("the break-even price at the default life should be the default price")
    default = S.run(S.SCENARIOS["central"].choice)["total"]
    for life in (2000.0, 1500.0, 1000.0):
        got = FF.cost_at_life_price("central", life, FF.break_even_price(life))
        if not close(got, default, 1e-6):
            fails.append(f"central at life {life:g} and its break-even price: {got:.4f} != default {default:.4f}")
    if not FF.cost_at_life_price("central", 1500.0, 1450.0) > default > FF.cost_at_life_price("central", 1500.0, 200.0):
        fails.append("a shorter life should cost more at the default price and less at a much lower one")
    # 2026-11-19 audit batch: ammonia tolerance 4 mmol/L and membranes for lost runs (the low-lactate example 26.43 -> 32.80 at the defaults)
    for (k, life, price), want in {("central", 2000.0, 1450.0): 45.3415, ("central", 1500.0, 1450.0): 53.7860,
                                   ("central", 1500.0, 550.0): 32.8204, ("central", 1000.0, 200.0): 26.9967}.items():
        got = FF.cost_at_life_price(k, life, price)
        if not close(got, want, 1e-3):
            fails.append(f"{k} life {life:g} price {price:g}: {got:.4f} != pinned {want}")
    return fails


def test_filter_flux():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    print("PASS — the filter flux limit holds." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
