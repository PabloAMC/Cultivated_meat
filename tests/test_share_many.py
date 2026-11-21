"""test_share_many.py — the Monte Carlo's vectorised share is the scalar share, draw by draw (2026-11-21).

meat_market.monte_carlo used to call market_share.share once per draw; it now calls market_share.share_x_meat_many for all
draws at once. This test draws every input the Monte Carlo varies over its own priors (and well beyond them: prices from
a tenth to ten times conventional, closeness on both sides of its base, every meat type's tier offset and price, poor and
rich regions) and checks the two agree to 1e-12 in relative terms. It also checks the plant-item cache
(inputs.memo_on_inputs) recomputes when an input it read is swapped, and gives the uncached result.
"""
from __future__ import annotations

import os
import sys
from dataclasses import replace

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import inputs as I  # noqa: E402
from market_share import DemandParams, share, share_x_meat_many  # noqa: E402


def check_share() -> list:
    fails = []
    pr = DemandParams()
    rng = np.random.default_rng(3)
    n = 400
    for income in (2500.0, 12000.0, pr.income_ref, 90000.0):
        R = np.exp(rng.uniform(np.log(0.1), np.log(10.0), n))
        R[:3] = 1.0                                              # exactly at parity too
        toff = rng.uniform(-3.0, 1.0, n)
        eps = pr.eps_own * rng.uniform(0.2, 2.0, n)
        kap = pr.kappa_base * rng.uniform(0.3, 3.0, n)
        kap[:5] = pr.kappa_base                                  # the kr == 1 branch
        pref = rng.uniform(2.0, 60.0, n)
        eq = rng.uniform(0.01, 0.6, n)
        vec = share_x_meat_many(R, pr, tier_offset=toff, eps_own=eps, kappa=kap, income=income, p_ref=pref, equal_share=eq)
        ref = np.array([share(R[i], pr, tier_offset=float(toff[i]), eps_own=eps[i], kappa=kap[i], income=income,
                              p_ref=float(pref[i]), equal_share=eq[i], which="x_meat") for i in range(n)])
        rel = np.abs(vec - ref) / np.maximum(np.abs(ref), 1e-300)
        if not np.all(np.isfinite(vec)) or rel.max() > 1e-12:
            i = int(np.nanargmax(rel))
            fails.append(f"income {income:.0f}: vectorised share differs from share() by {rel[i]:.2e} at draw {i} "
                         f"(R {R[i]:.3f}: {vec[i]!r} against {ref[i]!r})")
    return fails


def check_memo() -> list:
    import plant_items as PI
    fails = []
    a = PI.options()
    if a != PI.options.__wrapped__():
        fails.append("plant_items.options(): the cached result is not the uncached one")
    a["hall"]["class8"] = (0.0, "edited by a caller")
    if PI.options()["hall"]["class8"][0] == 0.0:
        fails.append("plant_items.options(): a caller's edit reached the cache")
    k = "pi_bldg_hall"
    old = I.REGISTRY[k]
    try:
        I.REGISTRY[k] = replace(old, value=old.value * 2.0)
        swapped = PI.options()
        if swapped["hall"]["sanitary"][0] == a["hall"]["sanitary"][0]:
            fails.append(f"plant_items.options() did not recompute when {k} was swapped")
        if swapped != PI.options.__wrapped__():
            fails.append(f"plant_items.options(): with {k} swapped the cached result is not the uncached one")
    finally:
        I.REGISTRY[k] = old
    if PI.options() != PI.options.__wrapped__():
        fails.append("plant_items.options(): after the input was put back, the cache gave a stale result")
    if PI.humbird() != PI.humbird.__wrapped__():
        fails.append("plant_items.humbird(): the cached result is not the uncached one")
    return fails


if __name__ == "__main__":
    fails = check_share() + check_memo()
    for f in fails:
        print("FAIL:", f)
    if fails:
        sys.exit(1)
    print("vectorised share and plant-item cache: all checks passed")
