#!/usr/bin/env python3
"""
premium_buyers.py — cultivated meat as an even more premium meat, competing with welfare labels for the same shoppers.

Why
---
Pablo (2026-11-18): people may come to see cultivated meat as a step above organic or free-range chicken, if they value that no animal
is killed; but then it competes with those labels for the same group of shoppers. The main model cannot say this: each meat type is a
separate choice between conventional meat, plant-based, cultivated and a whole-food option, so a welfare label is never on the shelf
beside cultivated meat, and nobody in the model is a "premium buyer".

What this module does
---------------------
1. Two classes of shopper, as in `premium_curve` ("the model's mainstream plus a loyal minority"): the main class (share 1 - pi) is the
   main model as it is, with a weak liking `v` for a welfare label; the premium class (share pi) likes the label (`v_l`) and is less
   price-sensitive (`kappa_l`). `fit_at(pi)` fits v, v_l and kappa_l to the sixteen premium products at a given pi, held to the at-parity
   elasticity Van Loo, Caputo and Lusk measured. The products fit equally well for any pi from 5% to 30%, so pi is set from who buys
   labels (research note), not from the share curve.
2. A fifth product on every shelf: the welfare label `L`, real meat, not slaughter-free, at `LABEL_PREMIUM` times the conventional price.
   Within each class and segment, conventional meat, plant-based, cultivated, the whole-food option and the label share one logit, so
   cultivated meat and the label compete for the same shoppers.
3. Cultivated meat in the premium class sells like a label at a premium lower by `d`: the no-killing value it adds over a welfare label
   (`no_killing`, a fraction of the conventional price; the evidence's central value is 0.05, and "even more premium" is larger) less
   the novelty and "unnatural" costs (`premium_curve.CORRECTIONS`). In the main class cultivated meat is the main model's.
4. `world_share` rolls this up across meat types and regions as the main model does, and says where cultivated meat's sales come from:
   conventional meat, the label, or the rest.
Nothing here changes a default. With pi = 0 and no label it reproduces the main model exactly (tested).

    python premium_buyers.py              # the tables
    python premium_buyers.py --markdown   # the tables the note quotes
"""
from __future__ import annotations

import sys

import numpy as np

import market_share as M
import meat_market as mm
import premium_curve as P
from inputs import value

LABEL_PREMIUM = 2.0        # the welfare label's price against conventional: organic chicken US 1.91x, Label Rouge 1.78x, cage-free eggs 2.0x
PI_CENTRAL = 0.10          # share of meat shoppers in the premium class: habitual premium buyers (research_notes/premium_buyers.md)
PI_CASES = (0.05, 0.10, 0.20)
NO_KILLING_CASES = (0.05, 0.25, 0.50, 1.00)   # value of no killing over a welfare label, fraction of the conventional price


# ---------------------------------------------------------------------------- the fit at a given premium-class share
_FITS: dict = {}


def fit_at(pi: float) -> dict:
    """Fit the main class's liking for the label (v), the premium class's (v_l) and its price sensitivity (kappa_l) to the sixteen
    premium products, with the premium class fixed at pi of shoppers and the main class's kappa the model's."""
    if pi in _FITS:
        return _FITS[pi]
    rows, k = P.data(), P.demand().cult_sub_mult
    unpack = lambda x: {"kappa": k, "v": float(x[2]), "pi": pi, "v_l": float(x[0]), "kappa_l": float(np.exp(x[1]))}
    f = lambda x: P.rms_log_error(unpack(x), rows) + 20.0 * P._outside_lusk(unpack(x))
    best = None
    for s in ([0.0, np.log(2.0), -3.0], [2.0, np.log(0.5), -1.0], [-1.0, np.log(3.0), -6.0], [1.0, np.log(1.0), -10.0]):
        x, v = P._nelder_mead(f, s, [0.4] * 3)
        if best is None or v < best[1]:
            best = (x, v)
    p = unpack(best[0])
    _FITS[pi] = {"params": p, "rms_log_error": P.rms_log_error(p, rows), "elasticity": P.parity_elasticity(p)}
    return _FITS[pi]


# ---------------------------------------------------------------------------- five products, two classes, two segments
def _slot(R, pr, beta, seg, *, kappa, offset, sf, income, p_ref, ratio_scale, accept_x, theta, neophobia_x, health_x):
    """Utilities [w, c, p, slot] from the main model, with the fourth product described by the keyword arguments."""
    return M._utilities(R, pr, beta, seg, accept_x=accept_x, theta_free_M=theta, tier_offset=offset, neophobia_x=neophobia_x,
                        neophobia_p=pr.neophobia_p, income=income, health_x=health_x, p_ref=p_ref, ratio_scale=ratio_scale,
                        kappa=kappa, slaughter_free_x=sf)


def shares(R_x: float, p: dict, *, d: float = 0.0, R_L: float | None = LABEL_PREMIUM, tier_offset: float = 0.0,
           eps_own: float | None = None, income: float | None = None, p_ref: float | None = None, cultivated: bool = True) -> dict:
    """Shares of {c, x, L, p, w} for one meat type. R_x: cultivated meat's price ratio; p: the fit (kappa, v, pi, v_l, kappa_l);
    d: the net correction that moves cultivated meat along the premium axis in the premium class (fraction of the conventional price);
    R_L: the label's price ratio (None = no label on the shelf); tier_offset, eps_own, income, p_ref: as in market_share.share."""
    pr = P.demand()
    eps = pr.eps_own if eps_own is None else eps_own
    inc = pr.income_ref if income is None else income
    beta = M._effective_beta(pr, eps, inc, p_ref)
    rs = eps / pr.eps_own
    out = dict.fromkeys(("c", "x", "L", "p", "w"), 0.0)
    x_premium = 0.0                                   # cultivated meat's sales to the premium class
    for cls, weight in (("main", 1.0 - p["pi"]), ("premium", p["pi"])):
        if weight <= 0.0:
            continue
        kap, v = (p["kappa"], p["v"]) if cls == "main" else (p["kappa_l"], p["v_l"])
        kq = pr.pb_committed_share / (1.0 - pr.w_eth)   # the mainstream's committed buyers of plant-based meat (2026-11-21)
        segs = (("M", (1.0 - pr.w_eth) * (1.0 - kq)), ("K", (1.0 - pr.w_eth) * kq), ("E", pr.w_eth))
        for seg, sw in segs:
            if sw <= 0.0:
                continue
            base = dict(income=inc, p_ref=p_ref, ratio_scale=rs, accept_x=1.0, theta=0.0, neophobia_x=0.0, health_x=0.0)
            V = list(_slot(1.0, pr, beta, seg, kappa=kap, offset=0.0, sf=0.0, **base)[:3])     # w, c, p
            names = ["w", "c", "p"]
            if cultivated:
                if cls == "main":     # the main model's cultivated meat, unchanged
                    Vx = M._utilities(R_x, pr, beta, seg, accept_x=pr.accept_x, theta_free_M=pr.theta_free_M,
                                      tier_offset=tier_offset, neophobia_x=pr.neophobia_x, neophobia_p=pr.neophobia_p, income=inc,
                                      p_ref=p_ref, ratio_scale=rs)[3]
                else:                 # a label product that sells as if priced d lower
                    Vx = _slot(max(R_x - d, 0.05), pr, beta, seg, kappa=kap, offset=tier_offset + v, sf=0.0, **base)[3]
                V.append(Vx); names.append("x")
            if R_L is not None:
                V.append(_slot(R_L, pr, beta, seg, kappa=kap, offset=v, sf=0.0, **base)[3]); names.append("L")
            sh = M._softmax(np.array(V))
            for n, s in zip(names, sh):
                out[n] += weight * sw * float(s)
                if n == "x" and cls == "premium":
                    x_premium += weight * sw * float(s)
    out["x_premium"] = x_premium
    return out


# ---------------------------------------------------------------------------- the roll-up across meat types and regions
def world_share(cost: float, p: dict, *, d: float, region: str = "global", R_L: float | None = LABEL_PREMIUM) -> dict:
    """Long-run share of meat by weight, %, for cells costing `cost`, and where cultivated meat's sales come from (fractions of its
    sales taken from conventional meat, from the label and from the rest), by the main model's roll-up (meat_market._rollup).
    Products the model labels premium (meat_market.tier: prime or wagyu beef, sushi-grade seafood, organic chicken, heritage pork and,
    since seafood was re-priced on 2026-11-19, premium fillets and shrimp) get no label beside them: they are the premium product
    already."""
    pr = P.demand()
    income = mm.REGION_INCOME[region]
    res = value("premium_resistance")
    bases = mm.species_bases(mm.MARKETS[region])
    took = {"c": 0.0, "L": 0.0, "rest": 0.0}
    sold = {"all": 0.0, "premium": 0.0}

    def share_of(mt, R, base, r):
        kw = dict(tier_offset=mm.tier_offset(mt, base, r, pr), eps_own=pr.eps_own,
                  income=income, p_ref=mt.p_conv, R_L=None if mm.tier(mt, base) == "premium" else R_L, d=d)
        w = mt.w_vol
        on, off = shares(R, p, **kw), shares(R, p, cultivated=False, **kw)
        took["c"] += w * (off["c"] - on["c"])
        took["L"] += w * (off["L"] - on["L"])
        took["rest"] += w * (off["p"] + off["w"] - on["p"] - on["w"])
        sold["all"] += w * on["x"]
        sold["premium"] += w * on["x_premium"]
        return on["x"] / max(on["x"] + on["c"] + on["L"], 1e-300)   # share of the meat sold (2026-11-19, as meat_market)

    _rows, vol, _val = mm._rollup(mm.MARKETS[region], cost, value("markup_add"), res, share_of)
    tot = sum(took.values()) or 1.0
    return {"share": vol * 100.0, "from_conventional": took["c"] / tot, "from_label": took["L"] / tot, "from_rest": took["rest"] / tot,
            "to_premium_buyers": sold["premium"] / (sold["all"] or 1.0)}


def d_for(no_killing: float, case: str = "long run, central") -> float:
    """Net correction for a value of no killing over a welfare label: no_killing plus the novelty and 'unnatural' costs of the case."""
    nk, nov, un = (P.CORRECTIONS[k] for k in ("no killing", "novelty", "unnatural"))
    if case == "long run, central":
        return no_killing + P.NOVELTY_LEFT_LONG_RUN * nov[0] + un[0]
    if case == "long run, favourable (novelty gone)":
        return no_killing + un[2]
    raise ValueError(case)


# ---------------------------------------------------------------------------- summary and tables
_SUM: dict = {}
SCEN = ("central", "best")


def summary() -> dict:
    if _SUM:
        return _SUM
    import scenarios as S
    costs = {k: S.run(S.SCENARIOS[k].choice)["total"] for k in SCEN}
    fits = {pi: fit_at(pi) for pi in PI_CASES}
    pc = fits[PI_CENTRAL]["params"]
    model = {k: S.shares(c)["global"] for k, c in costs.items()}
    no_label = {k: world_share(c, pc, d=d_for(0.05), R_L=None)["share"] for k, c in costs.items()}
    grid = {(k, nk): world_share(c, pc, d=d_for(nk)) for k, c in costs.items() for nk in NO_KILLING_CASES}
    by_pi = {(k, pi): world_share(c, fits[pi]["params"], d=d_for(0.05))["share"] for k, c in costs.items() for pi in PI_CASES}
    _SUM.update(costs=costs, fits=fits, model=model, no_label=no_label, grid=grid, by_pi=by_pi)
    return _SUM


def markdown_fits() -> str:
    s = summary()
    out = ["| premium buyers, share of shoppers | their liking for a label (utils) | their price sensitivity κ | main class's liking | "
           "typical miss (rms log error) | at-parity elasticity |", "|---|---|---|---|---|---|"]
    for pi, f in s["fits"].items():
        p = f["params"]
        out.append(f"| {pi:.0%} | {p['v_l']:.2f} | {p['kappa_l']:.2f} | {p['v']:.2f} | {f['rms_log_error']:.3f} | {f['elasticity']:.2f} |")
    return "\n".join(out)


def markdown_shares() -> str:
    import scenarios as S
    s = summary()
    out = ["| no killing, valued over a welfare label (share of meat's price) | " +
           " | ".join(f"{S.SCENARIOS[k].name.split(':')[0]}: share; sold to premium buyers; taken from the label, from conventional meat"
                      for k in SCEN) + " |",
           "|---|" + "---|" * len(SCEN)]
    for nk in NO_KILLING_CASES:
        cells = []
        for k in SCEN:
            g = s["grid"][(k, nk)]
            cells.append(f"{g['share']:.2f}%; {g['to_premium_buyers']:.0%}; {g['from_label']:.0%}, {g['from_conventional']:.0%}")
        out.append(f"| {nk:+.0%} | " + " | ".join(cells) + " |")
    out.append("| the main model | " + " | ".join(f"{s['model'][k]:.2f}%" for k in SCEN) + " |")
    out.append("| +5%, no label on the shelf | " + " | ".join(f"{s['no_label'][k]:.2f}%" for k in SCEN) + " |")
    return "\n".join(out)


def markdown_pi() -> str:
    import scenarios as S
    s = summary()
    out = ["| premium buyers, share of shoppers | " + " | ".join(S.SCENARIOS[k].name.split(":")[0] for k in SCEN) + " |",
           "|---|" + "---|" * len(SCEN)]
    for pi in PI_CASES:
        out.append(f"| {pi:.0%} | " + " | ".join(f"{s['by_pi'][(k, pi)]:.2f}%" for k in SCEN) + " |")
    return "\n".join(out)


def main() -> None:
    print(markdown_fits()); print(); print(markdown_shares()); print(); print(markdown_pi())


if __name__ == "__main__":
    main()
