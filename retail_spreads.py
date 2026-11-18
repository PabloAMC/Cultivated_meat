#!/usr/bin/env python3
"""
retail_spreads.py — is the meat retail markup a fixed $/kg or a percentage? A test on USDA's own prices.

USDA ERS Meat Price Spreads give, each month since 1970 (broilers since 1990), the retail value of a pound of meat and the
wholesale value of the meat that makes it, both per pound of retail weight. Two markup rules make opposite predictions for
how retail moves when wholesale moves:

    flat $/kg       retail = wholesale + a          -> a $1 rise in wholesale raises retail by $1
    percentage      retail = wholesale x b          -> a $1 rise raises retail by $b = retail / wholesale (1.7-2.5 here)

`pass_through` regresses the change in retail on the change in wholesale over h months (h = 12, 36, 60); `levels_fit`
regresses retail on wholesale and a linear trend since 2000. `fit_a` gives the per-kg part `a` of the model's rule
(cost + a) / (1 - m) that reproduces the last year's prices at a margin m. The data are a compact extract of ERS's
"Historical monthly price spread data for beef, pork, broilers" (research_notes/retail_markup_form_sources/), downloaded
2026-11-18. The write-up is research_notes/retail_markup_form.md.

    python retail_spreads.py
"""
from __future__ import annotations

import csv
import os

import numpy as np

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "research_notes", "retail_markup_form_sources",
                    "ers_meat_retail_wholesale_monthly.csv")
SERIES = {"beef": ("Choice beef retail value", "Choice beef wholesale value"),
          "pork": ("Pork retail value", "Pork wholesale value"),
          "broiler": ("Retail broiler composite", "Wholesale broiler composite")}
LB_PER_KG = 2.20462


def load(species: str):
    """(time in years, retail $/kg, wholesale $/kg) for one species, months where both exist."""
    rc, wc = SERIES[species]
    vals = {rc: {}, wc: {}}
    with open(DATA, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["item"] in vals:
                vals[r["item"]][(int(r["year"]), int(r["month"]))] = float(r["cents_per_lb_retail_weight"]) * LB_PER_KG / 100
    keys = sorted(set(vals[rc]) & set(vals[wc]))
    t = np.array([y + (m - 1) / 12 for y, m in keys])
    return t, np.array([vals[rc][k] for k in keys]), np.array([vals[wc][k] for k in keys])


def _ols(y, *x):
    X = np.column_stack([np.ones(len(y)), *x])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ b
    se = np.sqrt(np.diag(r @ r / (len(y) - X.shape[1]) * np.linalg.inv(X.T @ X)))
    return b, se


def pass_through(species: str, months: int) -> tuple:
    """Dollars of retail change per dollar of wholesale change over `months`, and its standard error (overlapping
    windows, so the error is understated)."""
    _t, R, W = load(species)
    b, se = _ols(R[months:] - R[:-months], W[months:] - W[:-months])
    return float(b[1]), float(se[1])


def last_year(species: str) -> dict:
    _t, R, W = load(species)
    r, w = float(R[-12:].mean()), float(W[-12:].mean())
    return {"retail": r, "wholesale": w, "spread": r - w, "ratio": r / w}


def levels_fit(species: str, since: float = 2000.0) -> tuple:
    """retail = c + slope * wholesale + trend * (year - since), on months since `since`: (c, slope, trend per year)."""
    t, R, W = load(species)
    s = t >= since
    b, _se = _ols(R[s], W[s], t[s] - since)
    return float(b[0]), float(b[1]), float(b[2])


def fit_a(species: str, margin: float) -> float:
    """The per-kg part a that makes (wholesale + a) / (1 - margin) equal last year's retail value."""
    ly = last_year(species)
    return ly["retail"] * (1.0 - margin) - ly["wholesale"]


RULES = (("flat $5 a kilo (the model before 2026-11-18)", 5.0, 0.0),
         ("per-kg $2.5 + a 15% margin", 2.5, 0.15),
         ("**per-kg $2.5 + a 28% margin (the model now)**", 2.5, 0.28),
         ("per-kg $2.5 + a 40% margin", 2.5, 0.40),
         ("$1 + 45%: the whole spread as a percentage (the 2026-11-16 audit)", 1.0, 0.45))


def rules_table() -> str:
    """Shelf price and long-run share of world meat at the best case's and Central's cost, under each markup rule."""
    import answer_rests_on as A
    import scenarios as S
    from inputs import value
    from price_ratio import shelf_price, cost_from_shelf
    cost = {k: S.run(S.SCENARIOS[k].choice)["total"] for k in ("best", "central")}
    out = ["| rule | cells' cost for parity with $%.0f meat | best case: shelf price, share | Central: shelf price, share |" % value("p_conv"),
           "|---|---|---|---|"]
    for name, a, m in RULES:
        cells = [f"${shelf_price(c, a, m):.1f}, {A.share_at(c, markup_add=a, retail_margin=m):.2f}%" for c in cost.values()]
        out.append(f"| {name} | ${cost_from_shelf(value('p_conv'), a, m):.2f} | {cells[0]} | {cells[1]} |")
    return "\n".join(out)


def main() -> None:
    for sp in SERIES:
        ly = last_year(sp)
        pts = ", ".join(f"{h} mo {pass_through(sp, h)[0]:.2f}" for h in (12, 36, 60))
        c, slope, trend = levels_fit(sp)
        print(f"  {sp:8s} retail ${ly['retail']:.2f}/kg, wholesale ${ly['wholesale']:.2f}, ratio {ly['ratio']:.2f} | "
              f"pass-through {pts} | levels since 2000: {c:.2f} + {slope:.2f} x wholesale + {trend:.3f}/yr | "
              f"a at a 28% margin ${fit_a(sp, 0.28):.2f}")
    print()
    print(rules_table())


if __name__ == "__main__":
    main()
