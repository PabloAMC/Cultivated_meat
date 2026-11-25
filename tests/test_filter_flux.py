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
    # 2026-11-20 model batch: the default life moved from 3,960 L/m2 (one 33-day run at 5 L/m2/h, a time limit) to 2,415
    # (Humbird's replacement schedule: 51.0 million litres of perfusate over 1,920 membranes of 11 m2 a year, so the life and the
    # price are one source's pair). It was 3.3 to 8.8 times the measured CHO throughput (450-1,200 L/m2); it is 2.0 to 5.4 times.
    # The two checks that said "more than three times" and "a 33-day run at 5 L/m2/h" are rewritten to what is true now.
    if not 2.0 * value("ff_throughput_hi") < value("rt_membrane_life") < 3.0 * value("ff_throughput_hi"):
        fails.append("the default life should be between two and three times the most a measured membrane filtered")
    if not close(value("rt_membrane_life"), 51.0e6 / (1920.0 * 11.0), 1e-3):
        fails.append("the default life is Humbird's 51.0 million litres over 1,920 membranes of 11 m2")
    if not close(FF.time_limited_life(5.0), 3960.0, 1e-9) or not FF.time_limited_life(5.0) > 1.6 * value("rt_membrane_life"):
        fails.append("a membrane kept for a whole 33-day run at 5 L/m2/h would filter 3,960 L/m2, over 1.6 times the default life")
    # 2026-11-19 repin: growth factors inside complete media prices (the low-lactate example -$2.99), nutrient floor $2.00 (Best +$0.30)
    # 2026-11-19 audit batch: ammonia tolerance 4 mmol/L (the low-lactate example filters 35 L/kg, was 28) and a lost run
    # throws its membranes away early, so every litre filtered carries more membrane; both grow as the life shortens
    # 2026-11-20 model batch: every cost is per kilo harvested (bubble deaths, harvest loss), and the rest of the batch raised the
    # cost outside the filter: central (5, 1200) 62.2305 -> 74.3037, (2.5, 450) 132.8657 -> 155.2466, best (5, 1200) 20.1702 -> 26.3570
    # 2026-11-20 final model: central (5, 1200) 74.3037 -> 72.0527, (2.5, 450) 155.2466 -> 147.0528 (the last engine fixes:
    # the low-lactate example $49.96 -> $49.50 at the defaults). The all-favourable example is no longer pinned here: it
    # holds its cells back with dialyser-grade hollow fibres whose flux, life and price it passes to explore directly
    # (scenarios.all_favourable), so the cell filter's flux and life do not reach it. The check says so.
    if not close(FF.cost_at("best", 5.0, 1200.0), S.run(S.SCENARIOS["best"].choice)["total"], 1e-12):
        fails.append("the cell filter's flux and life should not move the all-favourable example, which uses its own device")
    # 2026-11-21: 72.0527 -> 71.6736, 147.0528 -> 148.1271 (the low-lactate example's design is now the thinned recycled-oxygen
    # column; the building's power by floor and class; the floor's glucose)
    # 2026-11-25 (the gas cap and loop thinning): 71.6736 -> 68.9702, 148.1271 -> 114.5006. With membranes this short-lived the
    # engine's cheapest design bubbles less than the cap and is held thinner by its column loop: 102 g/L and 59 g/L, not 168
    # (a thinner culture filters fewer litres a kilo). The engine does not search density as such: at (2.5, 450) a culture
    # capped at 30 g/L costs $79.86 (retention.density_scan), so these are the engine's design, not the cheapest density
    for (k, f, l), want in {("central", 5.0, 1200.0): 68.9702, ("central", 2.5, 450.0): 114.5006}.items():
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
    # 2026-11-20 model batch (the low-lactate example 32.80 -> 49.96 at the defaults; the break-even price of a 1,500 L/m2 membrane
    # is now $901 a m2, not $549, so $550 no longer reproduces the default: it is $9.36 below it)
    # 2026-11-20 final model: 54.9502 -> 54.1201, 64.6270 -> 63.0864, 40.6019 -> 40.8253, 33.9283 -> 34.6416
    # 2026-11-21: 54.1201 -> 53.3935, 63.0864 -> 62.5335, 40.8253 -> 39.8410, 34.6416 -> 33.5375 (as above)
    # 2026-11-25 (the gas cap and loop thinning): 53.3935 -> 53.3088, 62.5335 -> 61.4572 (run at 125 g/L, not 168)
    for (k, life, price), want in {("central", 2000.0, 1450.0): 53.3088, ("central", 1500.0, 1450.0): 61.4572,
                                   ("central", 1500.0, 550.0): 39.8410, ("central", 1000.0, 200.0): 33.5375}.items():
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
