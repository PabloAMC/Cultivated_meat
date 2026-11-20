#!/usr/bin/env python3
"""
tank_size.py — is 20 m3 the right tank size?

Why
---
Every scenario uses a 20 m3 stirred tank in perfusion. Larger tanks cost less per m3 (Humbird's vessel cost, bioreactor
share only: floor_physics.capex_at_size) but are deeper, so they clear less CO2 and mix more slowly. The scenarios'
tank tricks (a stripping column, extra pressure, recycled oxygen, a squat shape) are meant to lift those limits. This
module scans cost against tank size, 2 to 200 m3, for each scenario and for the reference case. At each size it chooses
the tank design again, as `scenarios.design` does at 20 m3: the cheapest pair of tricks and shape (16 pairs) whose
column loop is pH-safe and runs at a pass rate dense cultures have taken. It calls `floor_physics.explore` and adds no
physics of its own: the what-if rows adjust a result after the call (labour, loop hardware) or change an argument
(`hazard`, `gas_velocity`).

What it reports
---------------
size_scan()    per case and size: the design chosen, the cost and its split (capital, loop hardware, labour,
               membranes, medium, other), the density and the limit that sets it, the loop check that stopped a
               cheaper design, the retention loop's membrane area, and the heat the wall must remove.
summary()      per case: the largest size at which the 20 m3 design still passes the checks, the largest size at
               which a re-chosen design still holds the 20 m3 density, and the cost-minimising size and its saving.
what_ifs()     the same optimum when one assumption that favours or penalises a size is changed: no loop checks, a
               looser pH check, labour that follows Humbird's crew rule, economies of scale in the loop hardware, a
               chance of losing a run that grows with tank size, gas per litre held at its 20 m3 value.
flatter()      a side check: tanks squatter than the scenarios' flattest, in case a flatter tank lets a bigger one pass.

Evidence and probabilities: research_notes/tank_size.md.

Run
---
    python tank_size.py
"""
from __future__ import annotations

import math

import floor_physics as fp
import gas_exchange as gx
import scenarios as S
from inputs import prior, value

SIZES = (2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0)       # m3, the scan the page of results is built on
CASES = ("reference", "reference_redesigned", "best", "central", "central_lean", "cautious")
LABELS = {"reference": "Reference (Humbird's tank, no tricks)", "reference_redesigned": "Reference, tank design chosen again",
          "best": "Best", "central": "Low-lactate example", "central_lean": "Low-lactate example, food-grade plant with shared medium",
          "cautious": "Cautious", "engineered": "Cells that make almost no ammonia or lactate (rung 6)"}
SEARCH_RANGE = (2.0, 200.0)                              # the sizes the optimum is searched over
GRID_RATIO = 1.03                                        # step of the geometric search grid
HOURS = fp.HOURS

# The what-if assumptions. `checks`: apply the loop's pH and pass checks; `ph_max` and `passes_max` are their limits (the
# model's are 1.0 times the safe dose and ge_passes_tested); `crew`: labour per kg follows Humbird's crew rule (staff per
# m3 fall with tank size as (20/V)^vm_labour_exp); `loop_exp`: the loop's hardware per m2 falls as (V/20)^-loop_exp;
# `hazard_exp`: the chance of losing a run per tank-day grows as (V/20)^hazard_exp; `gas`: 'velocity' (the model's rule:
# the same gas speed through the surface) or 'litre' (the same gas per litre of culture as the 20 m3 tank of that shape).
BASE = {"checks": True, "ph_max": 1.0, "passes_max": None, "crew": False, "loop_exp": 0.0, "hazard_exp": 0.0, "gas": "velocity"}
WHAT_IFS = (
    ("as modelled", {}),
    ("no loop checks (physics only)", {"checks": False}),
    ("pH check relaxed to twice the safe dose", {"ph_max": "ph_relaxed"}),
    ("pass limit at the top of its range", {"passes_max": "passes_hi"}),
    ("labour follows Humbird's crew rule", {"crew": True}),
    ("loop hardware has economies of scale", {"loop_exp": "loop_hw"}),
    ("chance of losing a run grows with tank size", {"hazard_exp": "hazard"}),
    ("gas per litre held at its 20 m3 value", {"gas": "litre"}),
    ("favourable to large tanks: pH check relaxed, crew rule, loop economies",
     {"ph_max": "ph_relaxed", "crew": True, "loop_exp": "loop_hw"}),
)


def _opts(change: dict | None) -> dict:
    o = {**BASE, **(change or {})}
    o["ph_max"] = value("ts_ph_relaxed") if o["ph_max"] == "ph_relaxed" else o["ph_max"]
    o["passes_max"] = (prior("ge_passes_tested")[2] if o["passes_max"] == "passes_hi"
                       else value("ge_passes_tested") if o["passes_max"] is None else o["passes_max"])
    o["loop_exp"] = value("ts_loop_hw_exp") if o["loop_exp"] == "loop_hw" else o["loop_exp"]
    o["hazard_exp"] = value("ts_hazard_exp") if o["hazard_exp"] == "hazard" else o["hazard_exp"]
    return o


def _designs(case: str) -> list:
    """The (tricks, shape) pairs a case may choose from, in `scenarios.design`'s order. The reference as defined has
    one: no tricks, Humbird's tall tank."""
    if case == "reference":
        return [("none", "tall")]
    return [(tk.key, sh.key) for tk in S.SW["tricks"].settings for sh in S.SW["shape"].settings]


def _kwargs(case: str, tricks: str, shape: str, v: float, o: dict, aspect: float | None = None) -> dict:
    if case.startswith("reference"):
        kw = {**S.setting("tricks", tricks).kw, **S.setting("shape", shape).kw}
    else:
        kw = S.explore_kwargs({**S.SCENARIOS[case].choice, "tricks": tricks, "shape": shape})
    kw["vessel_m3"] = v
    if aspect is not None:                               # a shape the switch does not offer (see `flatter`)
        kw["aspect"] = aspect
    if o["hazard_exp"]:
        kw["hazard"] = kw.get("hazard", 0.0) * (v / 20.0) ** o["hazard_exp"]
    if o["gas"] == "litre":
        us = kw.get("gas_velocity", value("pf_gas_velocity"))
        kw["gas_velocity"] = us * fp.tank_shape(v, kw.get("aspect"))[1] / fp.tank_shape(20.0, kw.get("aspect"))[1]
    return kw


def _split(r: dict, v: float, o: dict) -> dict:
    """The cost split of an explore result, with the what-if adjustments. capital: tank, plant and column; loop: the
    retention loop's hardware; labour; membranes; medium: feed, and growth factors if any; other: utilities, other
    consumables, bought oxygen and the like. The parts add to `total`."""
    out = r["output"]
    loop = value("plant_charge_mature") * r["retention_capex"] / out
    labour = r["labour"]
    if o["crew"]:
        labour *= (20.0 / v) ** value("vm_labour_exp")
    loop *= (v / 20.0) ** (-o["loop_exp"])
    p = {"capital": r["capital"] - value("plant_charge_mature") * r["retention_capex"] / out, "loop": loop, "labour": labour,
         "membranes": r["membranes"], "medium": r["feedstock"] + r["growth_factors"]}
    rest = r["total"] - (r["capital"] + r["labour"] + r["membranes"] + r["feedstock"] + r["growth_factors"])
    p["other"] = rest
    p["total"] = sum(p.values())
    return p


def _check(r: dict, o: dict) -> tuple:
    """(passes, kind, why not): the column loop's two checks, 'pH' and 'passes'. A tank with no column has nothing to
    check."""
    d = r["column"]
    if d is None:
        return True, "", ""
    if d["ph_vs_safe"] > o["ph_max"] + 1e-9:
        return False, "pH", f"pH dose {d['ph_vs_safe']:.2f} times the safe dose"
    if d["passes"] > o["passes_max"] + 1e-9:
        return False, "passes", f"{d['passes']:.1f} passes an hour against {o['passes_max']:g} tested"
    return True, "", ""


def _heat(r: dict, v: float, kw: dict) -> dict:
    """The heat the cells give off, and the wall's share of it per m2: a tank cooled through its wall alone."""
    cells = fp.Cells(mass_pg=kw.get("mass_pg", 3000.0), doubling_h=kw.get("doubling_h", 24.0))
    kw_m3 = cells.qo2 * r["density"] * value("pf_heat_per_o2") / 3600.0               # kW per m3 of culture
    aspect = kw.get("aspect", value("pf_aspect"))
    wall = gx.vessel_geometry(v, aspect)["surface"] / (value("pf_working_volume") * v)   # m2 of wall per m3 of culture
    return {"heat_kw_m3": kw_m3, "wall_m2_m3": wall, "wall_flux_kw_m2": kw_m3 / wall}


def evaluate(case: str, tricks: str, shape: str, v: float, change: dict | None = None, aspect: float | None = None) -> dict:
    """One design at one size: explore()'s answer, the cost split, the loop checks. `aspect` overrides the shape's liquid
    depth-to-width ratio."""
    o = _opts(change)
    kw = _kwargs(case, tricks, shape, v, o, aspect)
    r = fp.explore(**kw)
    ok, kind, why = _check(r, o)
    sp = _split(r, v, o)
    T, depth = fp.tank_shape(v, kw.get("aspect"))
    area_m3 = r["retention_capex"] / (value("rt_tff_hw") * value("rt_install"))     # m2 of membrane per m3 of tank
    d = r["column"]
    return {"case": case, "size": v, "tricks": tricks, "shape": shape, "aspect": kw.get("aspect", value("pf_aspect")),
            "total": sp["total"], "parts": {k: x for k, x in sp.items() if k != "total"}, "density": r["density"],
            "limit": r["limit"], "limits": r["limits"], "ok": ok, "kind": kind, "why": why,
            "passes": d["passes"] if d else 0.0, "ph": d["ph_vs_safe"] if d else 0.0,
            "width_m": T, "depth_m": depth, "loop_area_m2": area_m3 * v, "loop_area_m2_m3": area_m3,
            "loop_units": area_m3 * v / value("rt_atf_area"), "medium_l": r["medium_l"], "uptime": r["uptime"],
            **_heat(r, v, kw)}


def design_at(case: str, v: float, change: dict | None = None) -> dict:
    """Choose the design again at size v. Returns {'best', 'unchecked', 'rows'}: the cheapest design that passes the
    checks, the cheapest whatever the checks say, and every design tried. Ties go to the first pair, as in
    `scenarios.design`."""
    o = _opts(change)
    rows = [evaluate(case, tk, sh, v, change) for tk, sh in _designs(case)]
    best = unchecked = None
    for r in rows:
        if unchecked is None or r["total"] < unchecked["total"] - 1e-12:
            unchecked = r
        if (r["ok"] or not o["checks"]) and (best is None or r["total"] < best["total"] - 1e-12):
            best = r
    return {"best": best, "unchecked": unchecked, "rows": rows}


def size_scan(sizes=SIZES, cases=CASES, change: dict | None = None) -> dict:
    """{case: [row per size]}. A row is `design_at`'s best design, plus `unchecked` (the cost of the cheapest design
    without the loop checks), `check_binds` (a cheaper design was ruled out by a check), `check_cost` (what the checks
    cost, $/kg), `check_kind` and `check_why` (which check stopped that design), and `binding` (the density limit in
    words)."""
    out = {}
    for c in cases:
        rows = []
        for v in sizes:
            d = design_at(c, v, change)
            b = dict(d["best"])
            b["unchecked"] = d["unchecked"]["total"]
            b["unchecked_design"] = (d["unchecked"]["tricks"], d["unchecked"]["shape"])
            b["check_binds"] = d["unchecked"]["total"] < b["total"] - 1e-9 and not d["unchecked"]["ok"]
            b["check_cost"] = b["total"] - d["unchecked"]["total"] if b["check_binds"] else 0.0
            b["check_kind"] = d["unchecked"]["kind"] if b["check_binds"] else ""
            b["check_why"] = d["unchecked"]["why"] if b["check_binds"] else ""
            b["binding"] = S.LIMIT_PLAIN.get(b["limit"], b["limit"])
            rows.append(b)
        out[c] = rows
    return out


# ----------------------------------------------------------------------------
# Where the checks and the density hold
# ----------------------------------------------------------------------------
def _grid(lo: float = SEARCH_RANGE[0], hi: float = SEARCH_RANGE[1], ratio: float = GRID_RATIO) -> list:
    n = int(math.ceil(math.log(hi / lo) / math.log(ratio)))
    return [lo * (hi / lo) ** (i / n) for i in range(n + 1)]


def design_limit(case: str, change: dict | None = None, hi: float = 2000.0) -> float:
    """The largest size at which the 20 m3 design of a scenario (its own tricks and shape) passes the loop checks:
    found by stepping up from 20 m3 and then halving the last step. `inf` if the design has no column."""
    if case.startswith("reference"):
        return float("inf")
    ch = S.SCENARIOS[case].choice
    ok = lambda v: evaluate(case, ch["tricks"], ch["shape"], v, change)["ok"]
    if not ok(20.0):
        return float("nan")
    if ch["tricks"] == "none":
        return float("inf")
    lo, up = 20.0, 20.0
    while ok(up):
        lo, up = up, up * 1.5
        if up > hi:
            return float("inf")
    for _ in range(40):
        mid = 0.5 * (lo + up)
        lo, up = (mid, up) if ok(mid) else (lo, mid)
    return lo


def density_limit(case: str, change: dict | None = None, tol: float = 1e-3) -> float:
    """The largest size on the search grid up to which a re-chosen design holds the density the 20 m3 design holds
    (within `tol`), with no smaller size losing it."""
    ref = design_at(case, 20.0, change)["best"]["density"]
    last = 20.0
    for v in [x for x in _grid() if x >= 20.0]:
        if design_at(case, v, change)["best"]["density"] < ref * (1.0 - tol):
            return last
        last = v
    return last


def _within(curve: list, best: float, pct: float) -> tuple:
    """(smallest, largest) size on the curve whose cost is within `pct` per cent of the minimum."""
    ok = [v for v, t in curve if t <= best * (1.0 + pct / 100.0) + 1e-12]
    return (min(ok), max(ok))


def optimum(case: str, change: dict | None = None, lo: float = SEARCH_RANGE[0], hi: float = SEARCH_RANGE[1]) -> dict:
    """The cost-minimising size on a geometric grid from lo to hi (ratio GRID_RATIO, plus the 20 m3 case), the design
    chosen there, and the saving against 20 m3 in $/kg and in per cent. `at_edge` is True if the minimum is at the end
    of the range, in which case the true optimum may lie beyond it. `within_1pct`, `within_3pct`: the sizes (smallest,
    largest) whose cost is within that share of the minimum. `curve`: (size, cost) on the grid."""
    grid = sorted(set(_grid(lo, hi)) | {20.0})
    best = base = None
    curve = []
    for v in grid:
        b = design_at(case, v, change)["best"]
        curve.append((v, b["total"]))
        if v == 20.0:
            base = b
        if best is None or b["total"] < best["total"] - 1e-12:
            best = b
    return {"case": case, "curve": curve, "size": best["size"], "total": best["total"], "tricks": best["tricks"],
            "shape": best["shape"], "base": base["total"], "saving": base["total"] - best["total"],
            "saving_pct": 100.0 * (base["total"] - best["total"]) / base["total"],
            "at_edge": best["size"] >= hi * 0.999 or best["size"] <= lo * 1.001, "density": best["density"],
            "within_1pct": _within(curve, best["total"], 1.0), "within_3pct": _within(curve, best["total"], 3.0)}


def summary(cases=CASES) -> dict:
    """Per case: the largest size at which the 20 m3 design passes the checks, the largest size that keeps the 20 m3
    density, and the optimum (with the checks, and with none)."""
    out = {}
    for c in cases:
        out[c] = {"design_limit": design_limit(c), "design_limit_relaxed": design_limit(c, {"ph_max": "ph_relaxed"}),
                  "density_limit": density_limit(c), "optimum": optimum(c), "optimum_unchecked": optimum(c, {"checks": False})}
    return out


def flatter(case: str, v: float, aspects=(0.2, 0.3, 0.4, 0.5), change: dict | None = None) -> list:
    """[(aspect, best row)]: the cheapest tricks that pass the checks at size v for tanks squatter than the scenarios' flattest
    (liquid half as deep as wide). The scenarios do not offer these shapes; this is a side check on whether a flatter tank
    lets a larger one pass the loop checks."""
    out = []
    for a in aspects:
        rows = [evaluate(case, tk.key, "flat", v, change, aspect=a) for tk in S.SW["tricks"].settings]
        ok = [r for r in rows if r["ok"] or not _opts(change)["checks"]]
        out.append((a, min(ok, key=lambda r: r["total"])))
    return out


def what_ifs(cases=CASES) -> list:
    """[(label, {case: optimum})] for each what-if in WHAT_IFS."""
    return [(label, {c: optimum(c, ch) for c in cases}) for label, ch in WHAT_IFS]


# ----------------------------------------------------------------------------
FB_SIZES = (20.0, 50.0, 100.0, 200.0)
FB_CASES = ("central", "central_lean", "engineered", "best")


def fedbatch_at(case: str, v: float) -> dict:
    """A scenario's switches run in fed-batch at `v` m3 (2026-11-19 restructure: bigger tanks help fed-batch, whose handicap is
    capital), tank design chosen again under the loop checks. explore()'s result, with the design."""
    import vessels as V
    base = {k: x for k, x in S.SCENARIOS[case].choice.items() if k not in ("tricks", "shape")}
    best = None
    for tk in S.SW["tricks"].settings:
        for sh in S.SW["shape"].settings:
            r = S.run({**base, "mode": "fedbatch", "tricks": tk.key, "shape": sh.key}, vessel_m3=v)
            if not V._loop_ok(r):
                continue
            if best is None or r["total"] < best["total"] - 1e-12:
                best = {**r, "tricks": tk.key, "shape": sh.key}
    return best


def fedbatch_markdown(cases=FB_CASES, sizes=FB_SIZES) -> str:
    out = ["| switches as in | perfusion at 20 m³, $/kg | " + " | ".join(f"fed-batch at {v:.0f} m³" for v in sizes) + " |",
           "|---|---|" + "---|" * len(sizes)]
    for c in cases:
        cells = []
        for v in sizes:
            r = fedbatch_at(c, v)
            cells.append(f"${r['total']:.2f} ({r['density']:.0f} g/L)")
        out.append(f"| {LABELS[c]} | ${S.run(S.SCENARIOS[c].choice)['total']:.2f} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def main() -> None:
    scan = size_scan()
    for c in CASES:
        print(f"\n{LABELS[c]}")
        print(f"{'m3':>5} {'tricks':<9}{'shape':<8}{'$/kg':>7}  {'capital':>7}{'loop':>6}{'labour':>7}{'memb.':>6}{'medium':>7}{'other':>6}"
              f"  {'g/L':>5}  {'density limit':<28}{'checks cost':>12}  {'loop m2':>8}{'kW/m2':>6}")
        for r in scan[c]:
            p = r["parts"]
            chk = f"{r['check_cost']:.2f} ({r['check_kind']})" if r["check_binds"] else "-"
            print(f"{r['size']:5g} {r['tricks']:<9}{r['shape']:<8}{r['total']:7.2f}  {p['capital']:7.2f}{p['loop']:6.2f}{p['labour']:7.2f}"
                  f"{p['membranes']:6.2f}{p['medium']:7.2f}{p['other']:6.2f}  {r['density']:5.0f}  {r['binding'][:27]:<28}{chk:>12}  "
                  f"{r['loop_area_m2']:8.0f}{r['wall_flux_kw_m2']:6.1f}")
    print("\nSummary")
    for c, s in summary().items():
        o, u = s["optimum"], s["optimum_unchecked"]
        print(f"  {LABELS[c]:<46} 20 m3 design passes up to {s['design_limit']:7.1f} m3 (pH check at twice the safe dose: "
              f"{s['design_limit_relaxed']:.1f}); density held to {s['density_limit']:6.1f} m3; cheapest {o['size']:6.1f} m3 at "
              f"${o['total']:.2f} ({o['saving']:.2f} below 20 m3, {o['saving_pct']:.1f}%; within 1% from {o['within_1pct'][0]:.0f} to "
              f"{o['within_1pct'][1]:.0f} m3); no checks: {u['size']:.0f} m3, {u['saving_pct']:.1f}%")
    print("\nFlatter tanks than the scenarios offer ($/kg of the cheapest tricks that pass the checks; liquid depth / width = 0.2 ... 0.5)")
    for c in ("best", "central", "cautious"):
        for v in (20.0, 50.0, 100.0, 200.0):
            print(f"  {c:<8}{v:5g} m3  " + "  ".join(f"{a:g}: {r['total']:6.2f} ({r['tricks']})" for a, r in flatter(c, v)))
    print("\nWhat-ifs: cost-minimising size (saving against 20 m3, %)")
    for label, res in what_ifs():
        print(f"  {label:<72}" + "".join(f"{c.split('_')[0][:5]:>7}:{r['size']:5.0f} ({r['saving_pct']:4.1f})" for c, r in res.items()))


if __name__ == "__main__":
    main()
