#!/usr/bin/env python3
"""
demand_checks.py — is the model's response to price as strong as measured ones? Four checks, and what each would change.

Why
---
Four independent measurements now say something about how strongly sales of a novel or premium meat respond to its price:
  1. plant-based meat's own-price elasticity in US retail data, -1.23 (GFI, as cited by Knowles 2026);
  2. the slope of share against price premium across sixteen premium real meats (`premium_curve.py`);
  3. farmed salmon while it was still a premium product: 1.0-1.5% more volume per 1% lower price (`market_size_loop.md`);
  4. the one choice experiment on cultivated meat, at first contact and equal price: -0.84 to -3.4 (Van Loo, Caputo & Lusk 2020).
The model was calibrated to the fourth and to six of the sixteen. This module computes the model's own figure for each, so the
comparison is checked by a test and not by eye, and shows what the long-run share would be under the price responses the
measurements point to. It changes no default.

    python demand_checks.py
"""
from __future__ import annotations

import market_share as M
import meat_market as mm
import premium_curve as P
import scenarios as S
from inputs import value

PB_ELASTICITY_MEASURED = -1.23        # GFI, US retail scanner data, as cited by Knowles 2026 (the GFI source itself was not read)
SALMON_ALONG_CURVE = (1.0, 1.5)       # percent more volume per percent lower price (market_size_loop.HISTORY_ALONG_CURVE)
LUSK = P.LUSK                         # (-3.4, -0.84)
SCEN = ("central", "best")
R_GRID = (1.0, 1.25, 1.5, 2.0, 3.0, 4.0)


def pb_elasticity(pr: M.DemandParams | None = None) -> dict:
    """Plant-based meat's own-price elasticity in the model, at its own price (price_pb_mult) and with no cultivated meat on the
    shelf, as in the data."""
    pr = S._demand() if pr is None else pr
    Rp, h = pr.price_pb_mult, 1e-3

    def share(mult: float) -> float:
        old = pr.price_pb_mult
        pr.price_pb_mult = mult
        try:
            return M.share(1.0, pr, which="p", cultivated_present=False)
        finally:
            pr.price_pb_mult = old
    return {"elasticity": (share(Rp * (1 + h)) - share(Rp * (1 - h))) / (2 * h * share(Rp)), "share": share(Rp) * 100.0, "price": Rp}


def elasticity_at(R: float, pr: M.DemandParams | None = None, **kw) -> float:
    """Cultivated meat's own-price elasticity at price ratio R (reference shopper, long run unless a novelty is passed)."""
    pr = S._demand() if pr is None else pr
    h = 1e-4
    g = lambda r: M.share(r, pr, **kw)
    return (g(R * (1 + h)) - g(R * (1 - h))) / (2 * h * g(R))


def cold_parity_elasticity(pr: M.DemandParams | None = None, **kw) -> float:
    """At equal price and first contact: what Van Loo, Caputo and Lusk measured."""
    return elasticity_at(1.0, pr, neophobia_x=value("neophobia_x0"), **kw)


def _world(share_of_cost) -> dict:
    return {k: share_of_cost(S.run(S.SCENARIOS[k].choice)["total"]) for k in SCEN}


def variants() -> list:
    """The long-run share under different price responses. Each row: name, the curve (share at each price ratio in R_GRID, %),
    the cold at-parity elasticity, and the world share at Central's and the best case's cost. The first row is the model: two
    kinds of shopper since 2026-11-18. The next three have one kind only (premium_share=0)."""
    pr = S._demand()
    income = mm.REGION_INCOME["global"]

    def row(name, **kw):
        def world(cost):
            def share_of(mt, R, base, res):
                return M.share(R, pr, tier_offset=mm.tier_authenticity(mt, base, res, None),
                               eps_own=pr.eps_own * mm.tier_eps_mult(mt, base, res), income=income, p_ref=mt.p_conv, **kw)
            return mm._rollup(mm.MARKETS["global"], cost, value("markup_add"), value("premium_resistance"), share_of)[1] * 100.0
        return {"name": name, "curve": [M.share(R, pr, **kw) * 100.0 for R in R_GRID],
                "cold": elasticity_at(1.0, pr, neophobia_x=value("neophobia_x0"), **kw), "world": _world(world)}

    rows = [row("**the model: most shoppers as before, and premium buyers (10%) who respond as buyers of premium meats do**"),
            row("the model before 2026-11-18: one kind of shopper, 8.5 times as price-sensitive as meat in general", premium_share=0.0),
            row("one kind of shopper, 4 times (no extra sensitivity for cultivated meat)", premium_share=0.0, kappa=pr.kappa_base),
            row("one kind of shopper, with the slope of the sixteen premium meats (2.2 times)", premium_share=0.0,
                kappa=P.summary()["main"]["kappa"])]
    main, d = P.summary()["main"], P.delta_cases()["long run, central"]
    rows.append({"name": "one kind of shopper on the curve fitted to the sixteen premium meats (slope and level), with cultivated meat's corrections",
                 "curve": [P.curve(max(R - d, 0.05), main) * 100.0 for R in R_GRID], "cold": P.parity_elasticity(main),
                 "world": _world(lambda c: P.cultivated_share(c, main, d_price=d))})
    return rows


_SUM: dict = {}


def summary() -> dict:
    if not _SUM:
        pr = S._demand()
        _SUM.update(pb=pb_elasticity(), cold=cold_parity_elasticity(), at={R: elasticity_at(R) for R in R_GRID},
                    premium_3x=P.curve(3.0, P.summary()["main"]) * 100.0,
                    kappa_fit=P.summary()["main"]["kappa"], kappa=pr.cult_sub_mult, variants=variants(),
                    model_world=_world(lambda c: S.shares(c, regions=("global",))["global"]))
    return _SUM


def markdown_checks() -> str:
    """The model (two kinds of shopper) and the model before 2026-11-18 (one kind) against each measurement."""
    s = summary()
    import market_size_loop as L
    resp = L.summary()["response"]["products"]
    lo = min(v["response"] for n, v in resp.items() if n in ("beef (prime/wagyu)", "seafood (sushi)"))
    hi = max(v["response"] for n, v in resp.items() if n in ("beef (prime/wagyu)", "seafood (sushi)"))
    v = s["variants"]
    out = ["| what was measured | measured | the model | the model before 2026-11-18 |", "|---|---|---|---|",
           f"| Share of a meat at 3 times the ordinary one's price (sixteen premium real meats, fitted) | {s['premium_3x']:.1f}% | "
           f"{v[0]['curve'][R_GRID.index(3.0)]:.1f}% | {S.pct_num(v[1]['curve'][R_GRID.index(3.0)])}% |",
           f"| Cultivated meat at first contact and equal price: own-price elasticity (choice experiment) | {LUSK[1]:.2f} to {LUSK[0]:.1f} | "
           f"{v[0]['cold']:.2f} | {v[1]['cold']:.2f} |",
           f"| A premium product getting cheaper: percent more volume per percent lower price (farmed salmon) | "
           f"{SALMON_ALONG_CURVE[0]:g}–{SALMON_ALONG_CURVE[1]:g} | {lo:.1f}–{hi:.1f} (prime beef, sushi-grade seafood) | 3.0–3.4 |",
           f"| Plant-based meat's own-price elasticity (US retail) | {PB_ELASTICITY_MEASURED:.2f} | {s['pb']['elasticity']:.2f} | "
           f"{s['pb']['elasticity']:.2f} |"]
    return "\n".join(out)


def markdown_variants() -> str:
    s = summary()
    out = ["| price response | share of a meat at " + ", ".join(f"{R:g}×" for R in R_GRID) + " its price | at first contact and equal price | " +
           " | ".join(f"world share, {S.SCENARIOS[k].name.split(':')[0]}" for k in SCEN) + " |", "|---|---|---|" + "---|" * len(SCEN)]
    for r in s["variants"]:
        out.append(f"| {r['name']} | " + ", ".join(f"{S.pct_num(v)}%" for v in r["curve"]) + f" | {r['cold']:.2f} | " +
                   " | ".join(f"{S.pct_num(r['world'][k])}%" for k in SCEN) + " |")
    return "\n".join(out)


def main() -> None:
    print(markdown_checks()); print(); print(markdown_variants())
    s = summary()
    print("\ncultivated meat's own-price elasticity by price ratio:", {R: round(e, 2) for R, e in s["at"].items()})


if __name__ == "__main__":
    main()
