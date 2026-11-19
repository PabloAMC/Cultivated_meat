#!/usr/bin/env python3
"""
liking_spread.py — what if shoppers differ in how much they like cultivated meat? The model's price response, re-derived.

Why
---
The shopper model gives every mainstream shopper the same liking for cultivated meat; shoppers differ only through the logit's noise.
Its share then falls very fast above meat's price, twice to four times faster than four measurements say (`demand_checks.py`).
The one choice experiment on cultivated meat that estimated shoppers individually (Van Loo, Caputo & Lusk 2020, a random-parameter
logit on 1,830 US respondents) found the opposite of sameness: a very wide spread of liking for the lab-grown burger (standard
deviation 3.6-4.6 against a mean near zero, on a scale where a dollar a pound is 0.7). A wide spread flattens the aggregate curve
without making any one shopper less price-sensitive: the people still buying at a high price are the ones who like it most.

What this module does
---------------------
1. `share`: the model's share with a normal spread of liking for cultivated meat (mean `mu`, standard deviation `sd`, in the model's
   utils, added to cultivated meat's utility), integrated with Gauss-Hermite nodes. Everything else is the model's.
2. `fit`: the spread, and how price-sensitive each shopper is (kappa), that best reproduce the experiment at first contact: 5% of
   buyers at equal price and its own-price elasticities at four prices (`VANLOO_ELASTICITY`, simulated from the paper's fitted model).
3. `levels`: the long-run question the spread exposes. With every shopper alike, removing first-contact wariness (the model's
   `neophobia_x0`) takes cultivated meat from 5% to about half the market at equal price. With a wide spread the same removal takes it
   to about an eighth. So "about half at equal price" is a premise about how far the average shopper's liking recovers, and the
   module reports the shares under three readings of it.
Since 2026-11-18 the spread is in the model itself (market_share.share; liking_sd, equal_price_share): this module now fits it and
compares the readings of the long run. Its own shares are computed on the model with the spread switched off (liking_sd=0), with the
spread added here, so the fit does not count the spread twice.

    python liking_spread.py
"""
from __future__ import annotations

import numpy as np

import market_share as M
import meat_market as mm
import premium_curve as P
import scenarios as S
from inputs import value

# Van Loo, Caputo & Lusk 2020 (Food Policy 95), control arm, first contact. Share of buyers choosing the lab-grown burger with all
# four burgers at $5 a lb (full text read): 5%. Own-price elasticity of the lab-grown burger with the others at $5: not reported in
# the paper; simulated from its published random-parameter logit, which reproduces the published shares
# (research_notes/demand_heterogeneity_evidence.md). Keys are the lab-grown price as a ratio to beef's.
VANLOO_SHARE = 0.05
VANLOO_ELASTICITY = {0.6: -0.87, 1.0: -1.5, 1.4: -2.0, 1.8: -2.4}
VANLOO_ARMS = (-1.65, -1.1)                    # the elasticity at equal price across the paper's four information arms
KAPPAS = (4.0, 6.0, 8.5)
SDS = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0)
NODES = 15
R_GRID = (1.0, 1.25, 1.5, 2.0, 3.0, 4.0)
SCEN = ("today", "central", "best")

_X, _W = np.polynomial.hermite_e.hermegauss(NODES)
_W = _W / _W.sum()
_PR = None


def demand() -> M.DemandParams:
    global _PR
    if _PR is None:
        _PR = S._demand()
    return _PR


def share(R: float, mu: float, sd: float, kappa: float | None = None, nodes=None, **kw) -> float:
    """Cultivated meat's share at price ratio R when liking for it is spread normally across shoppers (mean mu, sd, utils)."""
    pr = demand()
    off = kw.pop("tier_offset", 0.0)
    x, w = (_X, _W) if nodes is None else nodes
    return float(sum(wi * M.share(R, pr, kappa=kappa, tier_offset=off + mu + sd * xi, liking_sd=0.0, **kw) for xi, wi in zip(x, w)))


def solve_mu(target: float, sd: float, kappa: float | None = None, R: float = 1.0, **kw) -> float:
    """The mean liking at which the share at R is `target`."""
    lo, hi = -60.0, 60.0
    for _ in range(70):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if share(R, mid, sd, kappa, **kw) < target else (lo, mid)
    return 0.5 * (lo + hi)


def elasticity(R: float, mu: float, sd: float, kappa: float | None = None, h: float = 1e-3) -> float:
    return (share(R * (1 + h), mu, sd, kappa) - share(R * (1 - h), mu, sd, kappa)) / (2 * h * share(R, mu, sd, kappa))


def miss(kappa: float, sd: float) -> dict:
    """How far the model with this spread and this price sensitivity is from the experiment's four elasticities (root mean square),
    with the mean liking set so that 5% buy at equal price."""
    mu = solve_mu(VANLOO_SHARE, sd, kappa)
    es = {R: elasticity(R, mu, sd, kappa) for R in VANLOO_ELASTICITY}
    return {"kappa": kappa, "sd": sd, "mu": mu, "elasticity": es,
            "miss": float(np.sqrt(np.mean([(es[R] - VANLOO_ELASTICITY[R]) ** 2 for R in es])))}


_SUM: dict = {}


def fit() -> dict:
    """The grid of misses, the best spread at the model's own price sensitivity (cult_sub_mult), and the best pair overall."""
    if "fit" not in _SUM:
        grid = {(k, sd): miss(k, sd) for k in KAPPAS for sd in SDS}
        k0 = demand().cult_sub_mult
        own = min((grid[(k0, sd)] for sd in SDS), key=lambda r: r["miss"])
        _SUM["fit"] = {"grid": grid, "own": own, "best": min(grid.values(), key=lambda r: r["miss"]), "none": grid[(k0, 0.0)]}
    return _SUM["fit"]


def levels() -> dict:
    """Three readings of the long run, at the fitted spread and the model's price sensitivity. Each: the mean liking and the share
    at equal price. 'first contact' is the experiment; 'novelty fades' removes the model's first-contact wariness (neophobia_x0)
    from every shopper; 'indifferent on average' was the model's premise before 2026-11-18, its share at equal price with every shopper alike."""
    f = fit()["own"]
    sd, k = f["sd"], f["kappa"]
    mu0 = f["mu"]
    mu1 = mu0 - value("neophobia_x0")
    par = M.share(1.0, demand(), liking_sd=0.0)          # the model's premise before 2026-11-18: every shopper alike
    mu2 = solve_mu(par, sd, k)
    return {"first contact (as measured)": {"mu": mu0, "parity": share(1.0, mu0, sd, k)},
            "novelty fades by what the model assumes": {"mu": mu1, "parity": share(1.0, mu1, sd, k)},
            "shoppers indifferent on average (the premise before 2026-11-18)": {"mu": mu2, "parity": share(1.0, mu2, sd, k)}}


def world_share(cost: float, mu: float, sd: float, kappa: float | None = None, region: str = "global") -> float:
    """Long-run share of meat by weight, %, by the model's roll-up across meat types and regions."""
    pr = demand()
    income = mm.REGION_INCOME[region]

    def share_of(mt, R, base, res):
        return share(R, mu, sd, kappa, tier_offset=mm.tier_authenticity(mt, base, res, None),
                     eps_own=pr.eps_own * mm.tier_eps_mult(mt, base, res), income=income, p_ref=mt.p_conv)
    return mm._rollup(mm.MARKETS[region], cost, value("markup_add"), value("premium_resistance"), share_of)[1] * 100.0


def summary() -> dict:
    if "summary" in _SUM:
        return _SUM["summary"]
    f = fit()
    sd, k = f["own"]["sd"], f["own"]["kappa"]
    lev = levels()
    costs = {key: S.run(S.SCENARIOS[key].choice)["total"] for key in SCEN}
    rows = {}
    for name, v in lev.items():
        rows[name] = {"parity": v["parity"] * 100.0, "mu": v["mu"], "curve": [share(R, v["mu"], sd, k) * 100.0 for R in R_GRID],
                      "world": {key: world_share(c, v["mu"], sd, k) for key, c in costs.items()}}
    seven = np.polynomial.hermite_e.hermegauss(7)
    seven = (seven[0], seven[1] / seven[1].sum())
    mu1 = lev["novelty fades by what the model assumes"]["mu"]
    _SUM["summary"] = {"fit": f, "sd": sd, "kappa": k, "levels": rows, "costs": costs,
                       "model": {"curve": [M.share(R, demand(), liking_sd=0.0) * 100.0 for R in R_GRID],
                                 "world": {key: world_share(c, 0.0, 0.0, k) for key, c in costs.items()},
                                 "cold": M.lusk_at_parity_elasticity(M.DemandParams(liking_sd=0.0))},
                       "default": {"world": {key: S.shares(c, regions=("global",))["global"] for key, c in costs.items()},
                                   "parity": M.share(1.0, demand()) * 100.0},
                       "premium": [P.curve(R, P.summary()["main"]) * 100.0 if R >= 1.5 else None for R in R_GRID],
                       "nodes_error": max(abs(share(R, mu1, sd, k, nodes=seven) / share(R, mu1, sd, k) - 1.0) for R in R_GRID)}
    return _SUM["summary"]


def _name(key: str) -> str:
    return S.SCENARIOS[key].name.split(":")[0]


def markdown_fit() -> str:
    f = fit()
    Rs = list(VANLOO_ELASTICITY)
    out = ["| each shopper's price sensitivity (times meat's) | spread of liking, utils | elasticity at " +
           ", ".join(f"{R:g}×" for R in Rs) + " beef's price | miss |", "|---|---|---|---|",
           "| **measured (Van Loo, Caputo & Lusk 2020, simulated from its fitted model)** | | " +
           ", ".join(f"{VANLOO_ELASTICITY[R]:.2f}" for R in Rs) + " | |"]
    for k in KAPPAS:
        for sd in (0.0, 2.0, 4.0, 5.0, 6.0):
            r = f["grid"][(k, sd)]
            mark = "**" if (k, sd) == (f["own"]["kappa"], f["own"]["sd"]) else ""
            out.append(f"| {mark}{k:g}{mark} | {mark}{sd:g}{mark} | " + ", ".join(f"{r['elasticity'][R]:.2f}" for R in Rs) + f" | {mark}{r['miss']:.2f}{mark} |")
    return "\n".join(out)


def markdown_levels() -> str:
    s = summary()
    out = ["| the long run | share at equal price | share of a meat at " + ", ".join(f"{R:g}×" for R in R_GRID[1:]) + " its price | " +
           " | ".join(f"world share, {_name(k)}" for k in SCEN) + " |", "|---|---|---|" + "---|" * len(SCEN)]
    for name, r in s["levels"].items():
        out.append(f"| {name} | {r['parity']:.0f}% | " + ", ".join(f"{S.pct_num(v)}%" for v in r["curve"][1:]) + " | " +
                   " | ".join(f"{S.pct_num(r['world'][k])}%" for k in SCEN) + " |")
    m = s["model"]
    out.append(f"| the model before 2026-11-18 (every shopper alike) | {m['curve'][0]:.0f}% | " + ", ".join(f"{S.pct_num(v)}%" for v in m["curve"][1:]) + " | " +
               " | ".join(f"{S.pct_num(m['world'][k])}%" for k in SCEN) + " |")
    out.append("| premium real meats (the curve fitted to sixteen) | | " +
               ", ".join("—" if v is None else f"{S.pct_num(v)}%" for v in s["premium"][1:]) + " | " + " | ".join("" for _ in SCEN) + " |")
    return "\n".join(out)


def main() -> None:
    print(markdown_fit()); print(); print(markdown_levels())
    s = summary()
    print(f"\nspread {s['sd']:g} utils at kappa {s['kappa']:g}; seven nodes in place of fifteen change a share by at most {s['nodes_error']:.1%}")


if __name__ == "__main__":
    main()
