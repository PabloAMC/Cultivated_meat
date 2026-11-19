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
1. `share`: the model's share with a spread of liking for cultivated meat (mean `mu`, standard deviation `sd`, in the model's
   utils, added to cultivated meat's utility), integrated over the model's own nodes (market_share.spread_quadrature) or the ones
   passed. Everything else is the model's.
2. `fit`: how far the model is from the experiment at first contact (5% of buyers at equal price and its own-price elasticities
   at four prices, `VANLOO_ELASTICITY`, simulated from the paper's fitted model), over a grid of spreads and of how
   price-sensitive each shopper is (kappa).
3. `levels`: the long-run question the spread exposes. With every shopper alike, removing first-contact wariness (the model's
   `neophobia_x0`) takes cultivated meat from 5% to about half the market at equal price. With a wide spread the same removal takes it
   to about a seventh. So "about half at equal price" is a premise about how far the average shopper's liking recovers, and the
   module reports the shares under three readings of it.
4. `families` (2026-11-19, audit finding D3): the SHAPE of the spread. A normal spread's tail falls too fast far above price
   parity: premium real meats hold 0.6% of their category at four times the ordinary price, the normal spread gave 0.1%. Four
   shapes (normal, logistic, Student's t, a mixture of two normals) are fitted jointly to (i) the choice experiment, (ii) the
   premium real meats at 2, 3 and 4 times the price and (iii) farmed salmon's response to a falling price (`objective`), and
   compared. The model's default is the Student's t (inputs.LIKING_FAMILY, liking_sd, liking_tail). `profile` gives the range of
   each of its two parameters within 20% of the best misfit; `quadrature_table` the integration rules against a 20,001-point
   reference.
Since 2026-11-18 the spread is in the model itself (market_share.share; liking_sd, equal_price_share): this module fits it and
compares the readings of the long run. Its own shares are computed on the model with the mean set here, so the fit does not
count the spread twice.

    python liking_spread.py              # the experiment's fit and the long-run readings
    python liking_spread.py --families   # the shapes compared, the profile and the integration rules (about a minute)
"""
from __future__ import annotations

import math
import sys
from dataclasses import replace

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
SDS = (0.0, 1.0, 2.0, 3.0, 3.6, value("liking_sd"), 4.2, 5.0, 6.0)
SDS_SHOWN = (0.0, 2.0, 3.6, value("liking_sd"), 5.0, 6.0)
R_GRID = (1.0, 1.25, 1.5, 2.0, 3.0, 4.0)
SCEN = ("today", "central", "best")

_PR = None


def demand() -> M.DemandParams:
    global _PR
    if _PR is None:
        _PR = S._demand()
    return _PR


def share(R: float, mu: float, sd: float, kappa: float | None = None, nodes=None, pr: M.DemandParams | None = None, **kw) -> float:
    """Cultivated meat's share at price ratio R when liking for it is spread across shoppers with mean mu and standard deviation
    sd (utils). `nodes` = (nodes, weights) of a standardised spread; None: the model's own (pr.spread). sd = 0: every shopper
    alike, shifted by mu."""
    pr = demand() if pr is None else pr
    off = kw.pop("tier_offset", 0.0)
    if sd <= 0.0:
        return M.share(R, pr, kappa=kappa, tier_offset=off + mu, liking_sd=0.0, **kw)
    return M.share(R, pr, kappa=kappa, tier_offset=off, liking_sd=sd, liking_mean=mu, spread=nodes, **kw)


def solve_mu(target: float, sd: float, kappa: float | None = None, R: float = 1.0, **kw) -> float:
    """The mean liking at which the share at R is `target`."""
    lo, hi = -90.0, 60.0
    for _ in range(70):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if share(R, mid, sd, kappa, **kw) < target else (lo, mid)
    return 0.5 * (lo + hi)


def elasticity(R: float, mu: float, sd: float, kappa: float | None = None, h: float = 1e-3, **kw) -> float:
    return (share(R * (1 + h), mu, sd, kappa, **kw) - share(R * (1 - h), mu, sd, kappa, **kw)) / (2 * h * share(R, mu, sd, kappa, **kw))


def miss(kappa: float | None, sd: float, **kw) -> dict:
    """How far the model with this spread and this price sensitivity is from the experiment's four elasticities (root mean square),
    with the mean liking set so that 5% buy at equal price."""
    mu = solve_mu(VANLOO_SHARE, sd, kappa, **kw)
    es = {R: elasticity(R, mu, sd, kappa, **kw) for R in VANLOO_ELASTICITY}
    return {"kappa": kappa, "sd": sd, "mu": mu, "elasticity": es,
            "miss": float(np.sqrt(np.mean([(es[R] - VANLOO_ELASTICITY[R]) ** 2 for R in es])))}


_SUM: dict = {}


def fit() -> dict:
    """The grid of misses against the experiment. 'own': the model's own spread (liking_sd, fitted jointly with the tail to the
    experiment, premium meats and salmon: `families`) at its own price sensitivity (cult_sub_mult). 'experiment': the spread on
    the grid that fits the experiment alone best, at that price sensitivity. 'best': the best pair on the grid. 'none': every
    shopper alike."""
    if "fit" not in _SUM:
        grid = {(k, sd): miss(k, sd) for k in KAPPAS for sd in SDS}
        k0 = demand().cult_sub_mult
        _SUM["fit"] = {"grid": grid, "own": grid[(k0, value("liking_sd"))],
                       "experiment": min((grid[(k0, sd)] for sd in SDS), key=lambda r: r["miss"]),
                       "best": min(grid.values(), key=lambda r: r["miss"]), "none": grid[(k0, 0.0)]}
    return _SUM["fit"]


def levels() -> dict:
    """Three readings of the long run, at the model's spread and price sensitivity. Each: the mean liking and the share
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
        return share(R, mu, sd, kappa, tier_offset=mm.tier_offset(mt, base, res, pr), income=income, p_ref=mt.p_conv, which="x_meat")
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
    pr = demand()
    ref = reference_nodes(pr.liking_family, pr.liking_tail, pr.liking_minority)
    mu1 = lev["novelty fades by what the model assumes"]["mu"]
    _SUM["summary"] = {"fit": f, "sd": sd, "kappa": k, "levels": rows, "costs": costs,
                       "model": {"curve": [M.share(R, demand(), liking_sd=0.0) * 100.0 for R in R_GRID],
                                 "world": {key: world_share(c, 0.0, 0.0, k) for key, c in costs.items()},
                                 "cold": M.lusk_at_parity_elasticity(M.DemandParams(liking_sd=0.0))},
                       "default": {"world": {key: S.shares(c, regions=("global",))["global"] for key, c in costs.items()},
                                   "parity": M.share(1.0, demand()) * 100.0},
                       "premium": [P.curve(R, P.summary()["main"]) * 100.0 if R >= 1.5 else None for R in R_GRID],
                       "nodes_error": max(abs(share(R, mu1, sd, k) / share(R, mu1, sd, k, nodes=ref) - 1.0) for R in R_GRID)}
    return _SUM["summary"]


# ---------------------------------------------------------------------------- the shape of the spread (2026-11-19, audit D3)
# The joint misfit. Three blocks, each the mean of squared residuals in units of what the measurement can bear, added with equal
# weights:
#   (i)   the choice experiment: the four elasticities above, each against 0.15 (the miss of the 2026-11-18 fit);
#   (ii)  premium real meats: the log of the model's share at 2, 3 and 4 times the price over the fitted curve's (3.7%, 1.5%,
#         0.6%), each against 0.35 (the curve is fitted to sixteen products with a typical miss of a factor of 2.4, so its own
#         level is uncertain by about a third);
#   (iii) farmed salmon: the log of the response of each premium product still dearer than its meat, where it is outside 1-1.5,
#         against log 2.
# and two requirements: the first-contact elasticity at equal price within -1.5 +/- 0.15, and the four-price miss at most 0.30.
SIGMA_ELASTICITY, SIGMA_PREMIUM, SIGMA_SALMON = 0.15, 0.35, math.log(2.0)
COLD_BAND, MISS_MAX = (-1.65, -1.35), 0.30
PREMIUM_AT = (2.0, 3.0, 4.0)
CURVE_AT = (1.25, 1.5, 2.0, 3.0, 4.0)
STILL_DEARER = 1.5                               # the salmon check takes the premium products above this price ratio (demand_checks.py)
WORLD_CASES = ("today", "central", "best")
# The fitted parameters of each shape (`fit_family` finds them; `python liking_spread.py --families` prints the table).
FITTED = {
    "normal, as it was (15 integration points)": dict(liking_family="normal", liking_sd=5.0),
    "normal, integrated properly": dict(liking_family="normal", liking_sd=5.0, _reference=True),
    "logistic": dict(liking_family="logistic", liking_sd=4.25),
    "Student's t (the model)": dict(liking_family="student", liking_sd=value("liking_sd"), liking_tail=value("liking_tail")),
    "mixture of two normals": dict(liking_family="mixture", liking_sd=4.4, liking_tail=3.0, liking_minority=0.05),
    "mixture, best on the grid (its corner)": dict(liking_family="mixture", liking_sd=5.2, liking_tail=6.0, liking_minority=0.02),
}


def _premium_target() -> dict:
    main = P.summary()["main"]
    return {R: P.curve(R, main) * 100.0 for R in (1.5,) + PREMIUM_AT}


def variant(**kw) -> M.DemandParams:
    """The model with another spread (liking_family, liking_sd, liking_tail, liking_minority) or share at equal price. The
    calibration is not re-solved: it does not depend on the spread."""
    return replace(demand(), **kw)


def _world(pr: M.DemandParams, cost: float) -> float:
    return mm.penetration(mm.MARKETS["global"], cost, income=mm.REGION_INCOME["global"], pr=pr)[1] * 100.0


def salmon_response(pr: M.DemandParams) -> dict:
    """market_size_loop.premium_response for a demand model: percent more share per percent lower price ratio of each premium
    product, between the low-lactate example's cost and its cost once a food-grade membrane exists; {name: (price ratio at the low-lactate example's cost, response)}."""
    import market_size_loop as L
    choice = S.SCENARIOS["central"].choice
    c0 = L.base_run(choice)["cost"]
    c1 = L.solve(choice, start="above", share=lambda cost: _world(pr, cost))["cost"]
    mk, inc = mm.MARKETS["global"], mm.REGION_INCOME["global"]
    bases = mm.species_bases(mk)
    a, b = mm.penetration(mk, c0, income=inc, pr=pr)[0], mm.penetration(mk, c1, income=inc, pr=pr)[0]
    return {mt.name: (float(R0), math.log(s1 / s0) / math.log(R0 / R1)) for (mt, R0, s0), (_m, R1, s1) in zip(a, b)
            if mm.tier(mt, bases[mm.animal_of(mt)]) == "premium" and s0 > 0 and R1 < R0}


def evaluate(world: bool = False, _reference: bool = False, **kw) -> dict:
    """Everything the comparison of shapes reports for one spread (keyword arguments as `variant`). `_reference`: integrate over
    the 20,001-point reference in place of the family's own nodes."""
    pr = variant(**kw)
    nodes = reference_nodes(pr.liking_family, pr.liking_tail, pr.liking_minority) if _reference else None
    if _reference:                                     # the model's own machinery, on the reference nodes
        pr.spread = nodes
        M._solve_liking(pr)
    m = miss(None, pr.liking_sd, pr=pr)
    nx0, h = value("neophobia_x0"), 1e-4
    cold = lambda r: M.share(r, pr, neophobia_x=nx0)
    resp = salmon_response(pr)
    out = {"params": kw, "miss": m["miss"], "elasticity": m["elasticity"],
           "fades_to": share(1.0, m["mu"] - nx0, pr.liking_sd, pr=pr) * 100.0,      # 5% at first contact, less the model's wariness
           "cold": (cold(1 + h) - cold(1 - h)) / (2 * h * cold(1.0)), "first": cold(1.0) * 100.0,
           "curve": {R: M.share(R, pr) * 100.0 for R in CURVE_AT}, "half": M.share(0.5, pr) * 100.0, "free": M.share(1e-4, pr) * 100.0,
           "far": {R: M.share(R, pr) * 100.0 for R in (5.0, 8.0, 10.0, 20.0)},
           "response": {n: r for n, (R0, r) in resp.items() if R0 > STILL_DEARER}}
    out.update(objective(out))
    if world:
        costs = {k: S.run(S.SCENARIOS[k].choice)["total"] for k in WORLD_CASES}
        out["world"] = {k: _world(pr, c) for k, c in costs.items()}
        best = replace(pr, equal_price_share=value(S.SCENARIOS["best"].equal_price_share))
        if _reference:
            best.spread = nodes
            M._solve_liking(best)
        out["world"]["best, own demand"] = _world(best, costs["best"])
    return out


def objective(m: dict) -> dict:
    """The joint misfit of an `evaluate` result: J = experiment + premium + salmon (each a mean of squared scaled residuals),
    and whether the two requirements hold."""
    target = _premium_target()
    j1 = float(np.mean([((m["elasticity"][R] - VANLOO_ELASTICITY[R]) / SIGMA_ELASTICITY) ** 2 for R in VANLOO_ELASTICITY]))
    j2 = float(np.mean([(math.log(m["curve"][R] / target[R]) / SIGMA_PREMIUM) ** 2 for R in PREMIUM_AT]))
    lo, hi = _salmon_range()
    out = lambda r: max(0.0, math.log(r / hi), math.log(lo / r))
    j3 = float(np.mean([(out(r) / SIGMA_SALMON) ** 2 for r in m["response"].values()])) if m["response"] else 0.0
    return {"J": j1 + j2 + j3, "J_parts": (j1, j2, j3),
            "meets": COLD_BAND[0] <= m["cold"] <= COLD_BAND[1] and m["miss"] <= MISS_MAX}


def _salmon_range() -> tuple:
    import market_size_loop as L
    return L.HISTORY_ALONG_CURVE


def fit_family(family: str, sds=None, tails=(0.0,), minorities=(0.0,)) -> dict:
    """Grid search of one shape: the parameters with the least joint misfit among those that meet the two requirements.
    Returns {'best': evaluate result, 'grid': {(sd, tail, minority): (J, meets)}}."""
    sds = np.round(np.arange(3.0, 6.01, 0.1), 2) if sds is None else sds
    grid, best = {}, None
    for t in tails:
        for p in minorities:
            for sd in sds:
                m = evaluate(liking_family=family, liking_sd=float(sd), liking_tail=float(t) or 4.0, liking_minority=float(p) or 0.05)
                grid[(float(sd), float(t), float(p))] = (m["J"], m["meets"])
                if m["meets"] and (best is None or m["J"] < best["J"]):
                    best = m
    return {"best": best, "grid": grid}


def profile(within: float = 0.20) -> dict:
    """How well the data pin the Student's two parameters: the range of each, with the other re-fitted, whose joint misfit is
    within `within` of the best and which meets the two requirements. {'best': (sd, tail, J), 'sd': (lo, hi), 'tail': (lo, hi),
    'by_tail': {tail: (best sd, J)}, 'by_sd': {sd: (best tail, J)}}."""
    if "profile" not in _SUM:
        tails = (2.2, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 8.0, 12.0, 30.0)
        g = {k: v for k, v in fit_family("student", sds=np.round(np.arange(3.3, 4.61, 0.05), 2), tails=tails)["grid"].items() if v[1]}
        best = min(g, key=lambda k: g[k][0])
        cut = g[best][0] * (1.0 + within)
        by_tail = {t: min(((sd, J) for (sd, tt, _p), (J, _ok) in g.items() if tt == t), key=lambda x: x[1], default=None) for t in tails}
        sds = sorted({k[0] for k in g})
        by_sd = {sd: min(((t, J) for (s, t, _p), (J, _ok) in g.items() if s == sd), key=lambda x: x[1]) for sd in sds}
        ok_t = [t for t, v in by_tail.items() if v is not None and v[1] <= cut]
        ok_s = [sd for sd, v in by_sd.items() if v[1] <= cut]
        _SUM["profile"] = {"best": (best[0], best[1], g[best][0]), "sd": (min(ok_s), max(ok_s)), "tail": (min(ok_t), max(ok_t)),
                           "by_tail": by_tail, "by_sd": by_sd}
    return _SUM["profile"]


def families(world: bool = True) -> dict:
    """Each shape at its fitted parameters (FITTED): the comparison table's rows."""
    if "families" not in _SUM:
        _SUM["families"] = {name: evaluate(world=world, **kw) for name, kw in FITTED.items()}
    return _SUM["families"]


# ---------------------------------------------------------------------------- integration rules, against a reference
def reference_nodes(family: str, tail: float = 0.0, minority: float = 0.0, n: int = 20001, reach: float = 100.0) -> tuple:
    """A 20,001-point reference for a standardised spread: the trapezoid rule in y with z = sinh(y), out to 100 standard deviations."""
    Y = math.asinh(reach)
    y = np.linspace(-Y, Y, n)
    z = np.sinh(y)
    w = M.spread_density(family, tail, minority)(z) * np.cosh(y)
    return z, w / w.sum()


def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction of the incomplete beta function (modified Lentz)."""
    tiny = 1e-300
    c, d = 1.0, 1.0 - (a + b) * x / (a + 1.0)
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 400):
        for aa in (m * (b - m) * x / ((a - 1.0 + 2 * m) * (a + 2 * m)), -(a + m) * (a + b + m) * x / ((a + 2 * m) * (a + 1.0 + 2 * m))):
            d = 1.0 + aa * d
            d = 1.0 / (d if abs(d) > tiny else tiny)
            c = 1.0 + aa / c
            c = c if abs(c) > tiny else tiny
            h *= d * c
        if abs(d * c - 1.0) < 1e-15:
            break
    return h


def _betainc(a: float, b: float, x: float) -> float:
    """Regularised incomplete beta function I_x(a, b)."""
    if x <= 0.0 or x >= 1.0:
        return 0.0 if x <= 0.0 else 1.0
    ln = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(ln) * _betacf(a, b, x) / a
    return 1.0 - math.exp(ln) * _betacf(b, a, 1.0 - x) / b


def student_quantile(u: float, nu: float) -> float:
    """Quantile of Student's t with nu degrees of freedom (numpy and math only): bisection on the upper tail
    P(T > x) = I_{nu/(nu+x^2)}(nu/2, 1/2) / 2. Checked against the closed forms at nu = 2 and 4."""
    if u == 0.5:
        return 0.0
    q = min(u, 1.0 - u)
    sf = lambda x: 0.5 * _betainc(0.5 * nu, 0.5, nu / (nu + x * x))
    lo, hi = 0.0, 1.0
    while sf(hi) > q:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if sf(mid) > q else (lo, mid)
        if hi - lo < 1e-14 * max(1.0, hi):
            break
    x = 0.5 * (lo + hi)
    return x if u > 0.5 else -x


def rule_nodes(family: str, n: int, tail: float = 0.0, minority: float = 0.0) -> tuple:
    """The textbook rule for each shape, with n nodes (per component for the mixture): Gauss-Hermite for the normal and for each
    component of the mixture; Gauss-Legendre nodes in probability mapped through the quantile function for the logistic and the
    Student's t. The model uses these only for the normal (market_share.spread_quadrature); they are here to be compared."""
    if family in ("normal", "mixture"):
        x, w = np.polynomial.hermite_e.hermegauss(n)
        w = w / w.sum()
        if family == "normal":
            return x, w
        s1 = 1.0 / math.sqrt(1.0 - minority + minority * tail * tail)
        return np.concatenate([s1 * x, s1 * tail * x]), np.concatenate([(1.0 - minority) * w, minority * w])
    x, w = np.polynomial.legendre.leggauss(n)
    u, w = 0.5 * (x + 1.0), 0.5 * w
    if family == "logistic":
        return np.log(u / (1.0 - u)) * math.sqrt(3.0) / math.pi, w
    if family == "student":
        return np.array([student_quantile(float(v), tail) for v in u]) * math.sqrt((tail - 2.0) / tail), w
    raise ValueError(family)


QUADRATURE_AT = (1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 5.0)


def quadrature_error(nodes: tuple, far: float | None = None, **kw) -> float:
    """Largest relative error of the share at 1 to 5 times meat's price (or at `far` times) when the spread `kw` (as `variant`)
    is integrated over `nodes`, against the 20,001-point reference. The mean liking is the reference's."""
    pr = variant(**kw)
    ref = reference_nodes(pr.liking_family, pr.liking_tail, pr.liking_minority)
    pr.spread = ref
    M._solve_liking(pr)
    Rs = QUADRATURE_AT if far is None else (far,)
    return max(abs(M.share(R, pr, spread=nodes) / M.share(R, pr, spread=ref) - 1.0) for R in Rs)


def quadrature_table() -> list:
    """Rows (shape, rule, nodes, error at 1-5 times the price, error at 8 times) for the fitted shapes."""
    rows = []
    cases = (("normal", dict(liking_family="normal", liking_sd=5.0), (15, 31, 61)),
             ("logistic", FITTED["logistic"], (60, 80, 100, 110, 120, 140)),
             ("Student's t", FITTED["Student's t (the model)"], (60, 80, 100, 110, 120, 140)),
             ("mixture", FITTED["mixture of two normals"], (15, 31, 61, 91)))
    for name, kw, ns in cases:
        fam, tail, mino = kw["liking_family"], kw.get("liking_tail", 0.0), kw.get("liking_minority", 0.0)
        rule = "Gauss-Hermite" + (" per component" if fam == "mixture" else "") if fam in ("normal", "mixture") else "Gauss-Legendre in probability"
        for n in ns:
            nd = rule_nodes(fam, n, tail, mino)
            rows.append((name, rule, len(nd[0]), quadrature_error(nd, **kw), quadrature_error(nd, far=8.0, **kw)))
        nd = M.grid_quadrature(M.spread_density(fam, tail, mino))
        rows.append((name, "stretched grid (the model's rule for every shape but the normal)", len(nd[0]), quadrature_error(nd, **kw),
                     quadrature_error(nd, far=8.0, **kw)))
    return rows


# ---------------------------------------------------------------------------- tables
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
        for sd in SDS_SHOWN:
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


def _params(kw: dict) -> str:
    fam = kw["liking_family"]
    if fam == "student":
        return f"spread {kw['liking_sd']:g}, tail {kw['liking_tail']:g}"
    if fam == "mixture":
        return f"spread {kw['liking_sd']:g}; {kw['liking_minority']:.0%} of shoppers at {kw['liking_tail']:g} times the others' spread"
    return f"spread {kw['liking_sd']:g}"


def markdown_families() -> str:
    fam = families()
    t = _premium_target()
    lo, hi = _salmon_range()
    out = ["| shape of the spread | parameters | choice experiment: miss | first contact, equal price: share, elasticity | share at " +
           ", ".join(f"{R:g}×" for R in CURVE_AT) + " | salmon response | at half price, if free | joint misfit (experiment, premium, salmon) | "
           "meets both requirements | world share: " + ", ".join(_name(k) for k in WORLD_CASES) + ", best with its own demand |",
           "|---|---|---|---|---|---|---|---|---|---|",
           f"| **measured** | | | 5%, -1.5 | —, " + ", ".join(f"{t[R]:.1f}%" for R in (1.5,) + PREMIUM_AT) + f" (premium real meats) | {lo:g}–{hi:g} | | | | |"]
    for name, m in fam.items():
        r = list(m["response"].values())
        w = m["world"]
        out.append(f"| {name} | {_params(m['params'])} | {m['miss']:.2f} | {m['first']:.1f}%, {m['cold']:.2f} | " +
                   ", ".join(f"{S.pct_num(m['curve'][R])}%" for R in CURVE_AT) + f" | {min(r):.1f}–{max(r):.1f} | {m['half']:.0f}%, {m['free']:.0f}% | "
                   f"{m['J']:.1f} ({m['J_parts'][0]:.1f}, {m['J_parts'][1]:.1f}, {m['J_parts'][2]:.1f}) | {'yes' if m['meets'] else 'no'} | " +
                   ", ".join(f"{S.pct_num(w[k])}%" for k in WORLD_CASES) + f", {S.pct_num(w['best, own demand'])}% |")
    return "\n".join(out)


def markdown_profile() -> str:
    p = profile()
    out = [f"best: spread {p['best'][0]:g}, tail {p['best'][1]:g} (joint misfit {p['best'][2]:.2f}); within 20% of it: spread "
           f"{p['sd'][0]:g} to {p['sd'][1]:g}, tail {p['tail'][0]:g} to {p['tail'][1]:g}", "",
           "| tail (degrees of freedom) | best spread | joint misfit |", "|---|---|---|"]
    out += [f"| {t:g} | {v[0]:g} | {v[1]:.2f} |" for t, v in p["by_tail"].items() if v is not None]
    return "\n".join(out)


def markdown_quadrature() -> str:
    out = ["| shape | rule | nodes | largest error of the share at 1 to 5 times the price | error at 8 times |", "|---|---|---|---|---|"]
    out += [f"| {a} | {b} | {n} | {e:.2%} | {e8:.1%} |" for a, b, n, e, e8 in quadrature_table()]
    return "\n".join(out)


def main() -> None:
    if "--families" in sys.argv:
        print(markdown_families()); print(); print(markdown_profile()); print(); print(markdown_quadrature())
        return
    print(markdown_fit()); print(); print(markdown_levels())
    s = summary()
    print(f"\nspread {s['sd']:g} utils at kappa {s['kappa']:g}; against a 20,001-point reference the model's integration rule "
          f"changes a share by at most {s['nodes_error']:.2%}")


if __name__ == "__main__":
    main()
