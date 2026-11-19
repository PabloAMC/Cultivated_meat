#!/usr/bin/env python3
"""
premium_curve.py — anchor cultivated meat's demand on the curve that premium real meats trace.

Why
---
Premium real meats (organic and free-range chicken, organic eggs and milk, wagyu, Ibérico) are "real meat plus a virtue, at a
premium". Cultivated meat is the same with a different virtue (no animal killed) and two extra costs (novelty, and an image of being
unnatural). So the share cultivated meat can win at a given price premium is the curve the premium meats trace, shifted by what differs
(Pablo, 2026-11-17).

The main model (`market_share`) fits one price-sensitivity number (κ = `cult_sub_mult`) to six premium products treated as "equal to
conventional except price", so their virtue is absorbed into κ, and its logit falls steeply with price: a real-meat product at 3x the
price takes 0.1% and at 4x 0.003%. The premium products instead hold a nearly flat 2-7% from 1.5x up, as if a group of shoppers paid
for the virtue whatever the premium. Cultivated meat sits at 2.5-6x, where the model only extrapolates.

What this module does
---------------------
1. `fit()`: fits the curve with the virtue kept explicit, a utility `v` for the label's virtue, and two kinds of shopper: most with the
   price sensitivity κ, a share `pi` with a lower one, κ_L. The analogue product is real meat and not slaughter-free
   (`share(..., slaughter_free_x=0)`). Fits: 'one' (κ and v, one kind of shopper) and 'two' (κ, v, pi, κ_L).
2. `cultivated_share()`: the world's long-run share of meat for a cost of cells, by the model's own roll-up across meat types and
   regions (`meat_market._rollup`), with cultivated meat placed on the fitted curve and shifted by `delta` utils: (no killing against
   a welfare label) - novelty - unnatural. delta = 0 is "cultivated meat as a premium label".
Nothing here changes a default.

    python premium_curve.py              # the fits and the shares
    python premium_curve.py --markdown   # the tables the note quotes
"""
from __future__ import annotations

import sys

import numpy as np

import market_share as M
import meat_market as mm

# (name, premium ratio against the conventional counterpart, share of category volume %, note). The first six are the main
# model's (market_share.ANALOGUES); research_notes/high_premium_analogues_data.md adds pairs above 2.5x.
ANALOGUES = [(n, R, s, note) for n, R, s, note in M.ANALOGUES]
# research_notes/high_premium_analogues_data.md (2026-11-17): (premium ratio, share %), ids H1-H20 there. Shares are of category
# volume unless noted; above about 2.3x supply and stocking cap several of them, so they may understate demand at that premium.
ANALOGUES_HIGH = [
    ("pasture-raised eggs, US (H1)",       3.21, 0.34, "retail scanner 2008-18 volume, mean; price 2012-18 vs white conventional"),
    ("free-range eggs, US (H2)",           2.36, 2.84, "same source as H1"),
    ("organic eggs, US (H3)",              2.32, 7.66, "same source as H1"),
    ("cage-free eggs, US (H4)",            2.00, 8.63, "same source as H1"),
    ("organic chicken, Great Britain (H11)", 2.22, 0.56, "Kantar panel 2016, share of purchases; premium not cut-matched"),
    ("organic chicken, Denmark (H12)",     3.55, 3.8, "one shelf comparison of whole birds; share basis not stated (GfK 2017)"),
    ("organic chicken, France (H13)",      2.67, 1.0, "share of production 2023; price from an industry-body quote"),
    ("Label Rouge chicken, France (H14)",  1.78, 13.0, "share of slaughter 2024; same price quote as H13"),
    ("organic chicken, Switzerland (H19)", 1.95, 2.9, "volume 2025; premium 1.6-2.3x by cut, midpoint"),
    ("organic eggs, Austria (H20)",        1.74, 12.7, "household purchases 2024, volume"),
]
# kept out of the main set and used as a sensitivity: a share of ibérico ham only, itself a luxury niche (H16)
ANALOGUES_IBERICO = [("Ibérico de bellota ham, Spain (H16)", 3.07, 9.29, "share of ibérico ham seals 2023; 2.78-3.37x by format")]


def data(high: bool = True) -> list:
    return ANALOGUES + (ANALOGUES_HIGH if high else [])


# ---------------------------------------------------------------------------- the curve
_PR = None


def demand() -> M.DemandParams:
    global _PR
    if _PR is None:
        _PR = M.DemandParams()
    return _PR


def curve(R: float, p: dict, **kw) -> float:
    """Share (fraction) of a premium real-meat product at premium R. p = {kappa, v} for one kind of shopper; with 'pi' also, a loyal
    segment of size pi with its own liking for the virtue (v_l) and its own price sensitivity (kappa_l), beside the mainstream
    (kappa, v). Extra keyword arguments go to market_share.share (a tier offset adds to both segments' utility)."""
    pr = demand()
    base = dict(accept_x=1.0, theta_free_M=0.0, neophobia_x=0.0, health_x=0.0, slaughter_free_x=0.0, liking_sd=0.0)   # a label, not cultivated meat
    base.update(kw)
    off = base.pop("tier_offset", 0.0)
    main = M.share(R, pr, kappa=p["kappa"], tier_offset=off + p["v"], **base)
    if p.get("pi", 0.0) <= 0.0:
        return main
    loyal = M.share(R, pr, kappa=p["kappa_l"], tier_offset=off + p["v_l"], **base)
    return (1.0 - p["pi"]) * main + p["pi"] * loyal


def rms_log_error(p: dict, rows: list) -> float:
    return float(np.sqrt(np.mean([(np.log(max(curve(R, p), 1e-12)) - np.log(s / 100.0)) ** 2 for _n, R, s, _x in rows])))


def _nelder_mead(f, x0, step, iters=600, tol=1e-7):
    """A small Nelder-Mead minimiser (scipy is not in the environment)."""
    n = len(x0)
    pts = [np.array(x0, float)] + [np.array(x0, float) + np.eye(n)[i] * step[i] for i in range(n)]
    vals = [f(x) for x in pts]
    for _ in range(iters):
        order = np.argsort(vals)
        pts, vals = [pts[i] for i in order], [vals[i] for i in order]
        if abs(vals[-1] - vals[0]) < tol:
            break
        c = np.mean(pts[:-1], axis=0)
        xr = c + (c - pts[-1]); fr = f(xr)
        if fr < vals[0]:
            xe = c + 2.0 * (c - pts[-1]); fe = f(xe)
            pts[-1], vals[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < vals[-2]:
            pts[-1], vals[-1] = xr, fr
        else:
            xc = c + 0.5 * (pts[-1] - c); fc = f(xc)
            if fc < vals[-1]:
                pts[-1], vals[-1] = xc, fc
            else:
                pts = [pts[0] + 0.5 * (x - pts[0]) for x in pts]
                vals = [f(x) for x in pts]
    i = int(np.argmin(vals))
    return pts[i], vals[i]


def _unpack(x, kind: str) -> dict:
    """'one': x = (log kappa, v), one kind of shopper. 'loyal': the mainstream is the main model as it stands (kappa = cult_sub_mult,
    pinned by the one choice experiment on cultivated meat through the at-parity elasticity), with its own liking for the virtue v,
    plus a loyal minority; x = (logit of pi/PI_MAX, v_l, log kappa_l, v), so that 0 < pi < PI_MAX."""
    if kind == "one":
        return {"kappa": float(np.exp(x[0])), "v": float(x[1])}
    return {"kappa": demand().cult_sub_mult, "v": float(x[3]), "pi": PI_MAX / (1.0 + np.exp(-x[0])), "v_l": float(x[1]),
            "kappa_l": float(np.exp(x[2]))}


PI_MAX = 0.30            # the loyal segment is a minority: at most 30% of shoppers
LUSK = (-3.4, -0.84)      # the cold-start at-parity elasticity Van Loo, Caputo and Lusk 2020 measured (market_share.LUSK_ELAS_BRACKET)


def _outside_lusk(p: dict) -> float:
    e = parity_elasticity(p)
    return max(0.0, LUSK[0] - e, e - LUSK[1])


def fit(kind: str = "loyal", rows: list | None = None, respect_lusk: bool = True) -> dict:
    """Fit the curve to the analogues by the root-mean-square error of log share. kind: 'one' or 'two' kinds of shopper.
    `respect_lusk`: add a penalty that keeps the fit's at-parity elasticity inside the experiment's range, so the premium products
    and the one choice experiment on cultivated meat are both respected. Several starts, because the error surface has flat valleys."""
    rows = data() if rows is None else rows
    f = lambda x: rms_log_error(_unpack(x, kind), rows) + (20.0 * _outside_lusk(_unpack(x, kind)) if respect_lusk else 0.0)
    if kind == "one":
        starts = [[np.log(8.5), 0.0], [np.log(4.0), 1.0], [np.log(12.0), 2.0], [np.log(3.0), -1.0]]
    else:
        starts = [[np.log(pi / (PI_MAX - pi)), v, np.log(k), vm] for pi in (0.03, 0.1) for v in (0.0, 3.0) for k in (0.5, 2.0)
                  for vm in (0.0, -1.0)]
    best = None
    for s in starts:
        x, v = _nelder_mead(f, s, [0.4] * len(s))
        if best is None or v < best[1]:
            best = (x, v)
    p = _unpack(best[0], kind)
    return {"kind": kind, "params": p, "rms_log_error": rms_log_error(p, rows), "n": len(rows),
            "elasticity": parity_elasticity(p), "respects_lusk": _outside_lusk(p) < 1e-3}


def parity_elasticity(p: dict) -> float:
    """The fitted curve's cold-start at-parity own-price elasticity for cultivated meat, the quantity Van Loo, Caputo and Lusk 2020
    measured (-0.84 to -3.4): as market_share.lusk_at_parity_elasticity, with the fit's kinds of shopper."""
    from inputs import value
    nx0, h = value("neophobia_x0"), 1e-4
    g = lambda r: curve(r, p, neophobia_x=nx0, slaughter_free_x=1.0)
    return float((g(1.0 + h) - g(1.0 - h)) / (2.0 * h * g(1.0)))


# ---------------------------------------------------------------------------- cultivated meat on the curve
# The corrections from cultivated meat to a welfare-labelled real meat, as fractions of the conventional price a shopper would pay
# for the difference (research_notes/cultivated_vs_welfare_meat_evidence.md; hypothetical willingness-to-pay studies, so the levels
# are inflated and the ratios between them better supported). A correction d moves cultivated meat along the premium axis: it sells
# like a label product priced d lower (d > 0) or higher (d < 0).
CORRECTIONS = {"no killing": (0.05, -0.05, 0.20), "novelty": (-0.30, -0.60, -0.15), "unnatural": (-0.20, -0.45, -0.05)}
#               (central, unfavourable end, favourable end)
NOVELTY_LEFT_LONG_RUN = 0.5      # P(at least half fades within about 10 years) = 0.55 in the evidence note: half is the central case


def delta_cases() -> dict:
    """Net corrections (fractions of the conventional price) for the cases the note reports."""
    nk, nov, un = (CORRECTIONS[k] for k in ("no killing", "novelty", "unnatural"))
    return {"as a premium label (no correction)": 0.0,
            "first contact": nk[0] + nov[0] + un[0],
            "long run, central": nk[0] + NOVELTY_LEFT_LONG_RUN * nov[0] + un[0],
            "long run, favourable (novelty gone)": nk[2] + un[2],
            "long run, unfavourable (novelty stays)": nk[1] + nov[1] + un[1]}


def cultivated_share(cost: float, p: dict, delta: float = 0.0, region: str = "global", d_price: float = 0.0) -> float:
    """World (or regional) long-run share of meat, %, for cells costing `cost` $/kg, with cultivated meat on the fitted curve,
    shifted by `d_price` (a fraction of each meat type's conventional price, CORRECTIONS) and `delta` (utils). Same roll-up as the
    main model (meat types, tiers, regional income); cultivated meat is real meat and not counted as slaughter-free, because its
    no-killing value is inside the correction."""
    pr = demand()
    income = mm.REGION_INCOME[region]
    from inputs import value
    res = value("premium_resistance")

    def share_of(mt, R, base, r):
        return curve(max(R - d_price, 0.05), p, tier_offset=mm.tier_authenticity(mt, base, r, None) + delta,
                     eps_own=pr.eps_own * mm.tier_eps_mult(mt, base, r), income=income, p_ref=mt.p_conv)
    return mm._rollup(mm.MARKETS[region], cost, value("markup_add"), res, share_of)[1] * 100.0


R_GRID = (1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0)
_SUM: dict = {}


def summary() -> dict:
    """Everything the note quotes: the fits on three data sets, the curves, and each scenario's share under each correction."""
    if _SUM:
        return _SUM
    import scenarios as S
    model = {"kappa": demand().cult_sub_mult, "v": 0.0}
    sets = {"the six used so far": data(high=False), "all sixteen": data(), "sixteen plus Ibérico": data() + ANALOGUES_IBERICO}
    fits = {name: {k: fit(k, rows) for k in ("one", "loyal")} for name, rows in sets.items()}
    main = fits["all sixteen"]["one"]["params"]
    costs = {k: S.run(S.SCENARIOS[k].choice)["total"] for k in ("today", "central", "forecast", "best")}
    cases = delta_cases()
    shares = {k: {lab: cultivated_share(c, main, d_price=d) for lab, d in cases.items()} for k, c in costs.items()}
    _SUM.update(model=model, sets=sets, fits=fits, main=main, costs=costs, cases=cases, shares=shares,
                model_rms={n: rms_log_error(model, rows) for n, rows in sets.items()},
                model_share={k: S.shares(c)["global"] for k, c in costs.items()},
                loyal_central={k: cultivated_share(c, fits["all sixteen"]["loyal"]["params"], d_price=cases["long run, central"])
                               for k, c in costs.items()},
                iberico_central={k: cultivated_share(c, fits["sixteen plus Ibérico"]["one"]["params"], d_price=cases["long run, central"])
                                 for k, c in costs.items()})
    return _SUM


def _p(p: dict) -> str:
    names = {"kappa": "κ", "v": "v", "pi": "loyal share", "v_l": "v loyal", "kappa_l": "κ loyal"}
    return ", ".join(f"{names[a]} {b * 100:.0f}%" if a == "pi" else f"{names[a]} {b:.2f}" for a, b in p.items())


def markdown_fits() -> str:
    s = summary()
    out = ["| data | curve | parameters | typical miss (rms log error) | cold at-parity elasticity |", "|---|---|---|---|---|"]
    for name in s["sets"]:
        out.append(f"| {name} | the main model as it is | κ {s['model']['kappa']:.1f}, no virtue term | {s['model_rms'][name]:.2f} | "
                   f"{parity_elasticity(s['model']):.2f} |")
        for k, lab in (("one", "one kind of shopper"), ("loyal", "the model's mainstream plus a loyal minority")):
            f = s["fits"][name][k]
            out.append(f"| {name} | {lab} | {_p(f['params'])} | {f['rms_log_error']:.2f} | {f['elasticity']:.2f} |")
    return "\n".join(out)


def markdown_curve() -> str:
    s = summary()
    out = ["| share of the category at premium R | " + " | ".join(f"{R:g}×" for R in R_GRID) + " |", "|---|" + "---|" * len(R_GRID)]
    out.append("| the main model | " + " | ".join(f"{curve(R, s['model']) * 100:.2f}%" for R in R_GRID) + " |")
    out.append("| fitted to all sixteen premium products | " + " | ".join(f"{curve(R, s['main']) * 100:.2f}%" for R in R_GRID) + " |")
    return "\n".join(out)


def markdown_shares() -> str:
    import scenarios as S
    s = summary()
    labs = list(s["cases"])
    out = ["| scenario | cells, $/kg | the main model | " + " | ".join(f"{lab} ({s['cases'][lab]:+.0%})" for lab in labs) + " |",
           "|---|---|---|" + "---|" * len(labs)]
    for k, c in s["costs"].items():
        out.append(f"| {S.SCENARIOS[k].name.split(':')[0]} | ${c:.2f} | **{s['model_share'][k]:.2f}%** | " +
                   " | ".join(f"{s['shares'][k][lab]:.2f}%" for lab in labs) + " |")
    return "\n".join(out)


def main() -> None:
    if "--markdown" in sys.argv:
        print(markdown_fits() + "\n\n" + markdown_curve() + "\n\n" + markdown_shares())
        return
    print(markdown_fits()); print(); print(markdown_curve()); print(); print(markdown_shares())
    s = summary()
    print("loyal-minority fit, long run central:", {k: round(v, 2) for k, v in s["loyal_central"].items()})
    print("with Ibérico, long run central:", {k: round(v, 2) for k, v in s["iberico_central"].items()})


if __name__ == "__main__":
    main()
