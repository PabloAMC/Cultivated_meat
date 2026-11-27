#!/usr/bin/env python3
"""
nutrient_floor.py — the cheapest the medium can be per kg of cells, built from amino-acid prices instead of assumed.

Why
---
The model's medium cost is the larger of two things: litres of medium per kg x price per litre, and a floor, what the cells
must eat. GFI's December 2025 analysis gives amino-acid prices per kilo for three tiers (feed-grade, low and high food-grade) and
a range of amino acid needs per kilo of cells (200-650 g). This module prices the floor that way.

Since 2026-11-19 the model's own floor IS the cheapest of these: feed-grade amino acids at the most efficient need (232 g at
$6.36, $1.48), glucose ($0.13) and other nutrients ($0.40): $2.00 a kilo. Before, it was $1.70, with the amino acids as 0.337 kg
of soy hydrolysate at $2 ($0.67), which cannot supply glutamine, arginine, asparagine, cystine and serine (GFI). The module now
shows what the dearer tiers and needs would do.

Run
---
    python nutrient_floor.py
"""
from __future__ import annotations

import floor_physics as fp
import retention
import scenarios as S
from inputs import value

TIERS = {"feed": "nf_aa_price_feed", "low": "nf_aa_price_low", "high": "nf_aa_price_high"}
NEEDS = {"eff": "nf_aa_g_eff", "mid": "nf_aa_g_mid", "low": "nf_aa_g_low"}


def aa_cost(tier: str, need: str) -> float:
    """$ per kg of cells for the amino acids: price per kg of amino acid x kg of amino acid per kg of cells."""
    return value(TIERS[tier]) * value(NEEDS[need]) / 1000.0


def floor(tier: str, need: str) -> float:
    """The nutrient floor, $/kg of cells, with amino acids at this tier and need: amino acids + glucose + the other nutrients."""
    return aa_cost(tier, need) + fp.nutrient_balance(fp.GOOD_CELLS)["glc_kg"] * value("glucose_price") + value("other_nutrients_floor")


def scenario_cost(key: str, tier: str, need: str) -> dict:
    """A scenario's cost with the amino acids at this tier's price and this need (`aa_bulk_price` and `aa_intensity`). Since
    2026-11-27 the need is set directly, not folded into the price: the amino acids a case's ammonia takes
    (floor_physics.nutrient_balance) are bought at the tier's price, not at a price inflated by the need."""
    with retention._with({"aa_bulk_price": value(TIERS[tier]), "aa_intensity": value(NEEDS[need]) / 1000.0}):
        r = fp.explore(**S.explore_kwargs(S.SCENARIOS[key].choice))
    return {"total": r["total"], "medium": r["feedstock"], "floor_binds": r["feedstock"] <= floor(tier, need) + 1e-9}


def summarise() -> None:
    print(f"  model floor: ${fp.feedstock(fp.GOOD_CELLS):.2f}/kg (amino acids ${value('aa_intensity') * value('aa_bulk_price'):.2f})")
    print("  amino acids $/kg cells; floor $/kg (amino acids + glucose + other)")
    for t in TIERS:
        print(f"    {t:<5}" + "".join(f"  {n}: ${aa_cost(t, n):5.2f} (${floor(t, n):5.2f})" for n in NEEDS))
    for k in ("best", "central"):
        base = S.run(S.SCENARIOS[k].choice)["total"]
        print(f"  {k}: ${base:.2f} now")
        for t in TIERS:
            print(f"    {t:<5}" + "".join(f"  {n}: ${scenario_cost(k, t, n)['total']:6.2f}" for n in NEEDS))


if __name__ == "__main__":
    summarise()
