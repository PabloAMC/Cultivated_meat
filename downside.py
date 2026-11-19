#!/usr/bin/env python3
"""
downside.py — what each scenario costs if perfusion cannot be run at 20 m3.

Every scenario uses a stirred tank in perfusion: a device holds the cells back and waste is washed out. Nobody has run
animal cells in perfusion above about 4 m3 (`vm_perf_max_m3`). The fallback is a tank run without cell retention, in
fed-batch or in fill-and-draw (vessels.py), where waste and the least medium flow cap the density, and the one 20 m3
plant for meat cells reports harvests of about 27 g/L (`vm_x_meat_shown`).

For each scenario this module prices both modes in the stirred tank, at two densities:
  * the model's own cap (what waste allows: 25-92 g/L), and
  * the density shown for meat cells in a vessel of 1 m3 or more (`vm_x_meat_shown`).
Everything else is the scenario's: cells, plant, losses, gas the cells tolerate, medium and growth factors. The tank design
(tricks, shape) is chosen again for each mode, because a trick that lifts the perfusion tank's gas limits adds capital
without raising the density of a tank whose waste caps it (`scenarios.design` does the same for perfusion).

Run
---
    python downside.py
"""
from __future__ import annotations

import floor_physics as fp
import scenarios as S
import vessels as V
from inputs import value

MODES = ("fedbatch", "filldraw")
CAPS = ("model", "shown")                   # the model's own density cap, or the density shown for meat cells


def _run(choice: dict, mode: str, cap: str) -> dict:
    """The scenario's cost in a stirred tank in `mode`, tank design chosen again. Returns explore()'s result."""
    best = None
    for tk in S.SW["tricks"].settings:
        for sh in S.SW["shape"].settings:
            kw = V.explore_kwargs("stirred", mode, S.explore_kwargs({**choice, "tricks": tk.key, "shape": sh.key}))
            if cap == "shown":
                kw["vm"] = {**kw["vm"], "caps": {"shown for meat cells": value("vm_x_meat_shown")}}
            r = fp.explore(**kw)
            if not V._loop_ok(r):
                continue
            if best is None or r["total"] < best["total"] - 1e-12:
                best = {**r, "tricks": tk.key, "shape": sh.key}
    return best


def costs(key: str) -> dict:
    """{(mode, cap): {'cost', 'density', 'limit', 'tricks', 'shape', 'share'}} for a scenario key, plus 'perfusion'."""
    choice = S.SCENARIOS[key].choice
    out = {"perfusion": S.run(choice)["total"]}
    for mode in MODES:
        for cap in CAPS:
            r = _run(choice, mode, cap)
            out[(mode, cap)] = {"cost": r["total"], "density": r["density"], "limit": r["limit"],
                                "tricks": r["tricks"], "shape": r["shape"], "share": S.shares(r["total"])["global"]}
    out["perfusion_share"] = S.shares(out["perfusion"])["global"]
    return out


def summarise() -> None:
    print("  cost of a kilo of cells if perfusion cannot be run at 20 m3 (stirred tank, $/kg; world share %, point estimate)")
    print(f"  {'scenario':<14}{'perfusion':>11}   {'fed-batch, model cap':>22}{'fed-batch, 27 g/L':>20}"
          f"{'fill-and-draw, model cap':>26}{'fill-and-draw, 27 g/L':>23}")
    for k in S.ORDER:
        c = costs(k)
        cell = lambda m, cap: f"${c[(m, cap)]['cost']:6.2f} ({c[(m, cap)]['density']:.0f} g/L, {c[(m, cap)]['share']:.1f}%)"
        print(f"  {k:<14}${c['perfusion']:6.2f} ({c['perfusion_share']:.1f}%) {cell('fedbatch', 'model'):>24}"
              f"{cell('fedbatch', 'shown'):>26}{cell('filldraw', 'model'):>26}{cell('filldraw', 'shown'):>26}")


if __name__ == "__main__":
    summarise()
