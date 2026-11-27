#!/usr/bin/env python3
"""
demand_checks.py — is the model's response to price as strong as measured ones? Four checks, and what each would change; and
since 2026-11-22 (sixth batch) a fifth, the menu check: what adding plant-based meat to a menu takes from meat (Hope 2026).

Why
---
Four independent measurements now say something about how strongly sales of a novel or premium meat respond to its price:
  1. plant-based meat's own-price elasticity in US retail data, -1.23 (GFI, as cited by Knowles 2026);
  2. the slope of share against price premium across sixteen premium real meats (`premium_curve.py`);
  3. farmed salmon while it was still a premium product: 1.0-1.5% more volume per 1% lower price (`market_size_loop.md`);
  4. the one choice experiment on cultivated meat, at first contact and equal price: about -1.5 (Van Loo, Caputo & Lusk 2020;
     simulated from the paper's fitted model, which reports no elasticity). Until 2026-11-18 this module used "-0.84 to -3.4", the
     range the model's own check carries (market_share.LUSK_ELAS_BRACKET): those two numbers are a formula applied to two of the
     paper's price coefficients, not its aggregate response (research_notes/demand_heterogeneity_evidence.md).
The model was set against that range and to six of the sixteen. This module computes the model's own figure for each, so the
comparison is checked by a test and not by eye, and shows what the long-run share would be under the price responses the
measurements point to. It changes no default.

    python demand_checks.py
"""
from __future__ import annotations

from dataclasses import replace

import market_share as M
import meat_market as mm
import premium_curve as P
import scenarios as S
from inputs import value

PB_ELASTICITY_MEASURED = -1.23        # GFI/NielsenIQ fact sheet, November 2024: item-level, plant-based beef (demand_heterogeneity_evidence.md §4)
PB_CATEGORY_RANGE = (-2.5, -0.6)      # the category's long-run elasticity, 80% range around about -1.3 (same note; low confidence)
SALMON_ALONG_CURVE = (1.0, 1.5)       # percent more volume per percent lower price (market_size_loop.HISTORY_ALONG_CURVE)
LUSK = P.LUSK                         # (-3.4, -0.84): the model's own check; not a measured elasticity (see the docstring)
VANLOO_AT_PARITY = -1.5               # the experiment's aggregate own-price elasticity at equal price, first contact (simulated)
VANLOO_ARMS = (-1.65, -1.1)           # across its four information arms
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
    the first-contact elasticity at equal price, and the world share at the low-lactate example's and the all-favourable example's cost. The first row is the
    model (a spread of liking since 2026-11-18, heavier-tailed than a normal since 2026-11-19); the next three have every shopper
    alike (liking_sd=0); the last is the normal spread the model had on 2026-11-18."""
    pr0 = S._demand()
    income = mm.REGION_INCOME["global"]

    def row(name, pr=pr0, **kw):
        def world(cost):
            def share_of(mt, R, base, res):
                return M.share(R, pr, tier_offset=mm.tier_offset(mt, base, res, pr), income=income, p_ref=mt.p_conv, which="x_meat", **kw)
            return mm._rollup(mm.MARKETS["global"], cost, value("markup_add"), value("premium_resistance"), share_of)[1] * 100.0
        return {"name": name, "curve": [M.share(R, pr, **kw) * 100.0 for R in R_GRID],
                "cold": elasticity_at(1.0, pr, neophobia_x=value("neophobia_x0"), **kw), "world": _world(world)}

    # the rows with every shopper alike, and the normal spread of 2026-11-18, are the model before its price-insensitive
    # shoppers (2026-11-22, fifth batch): calibrated without them, as those models were
    pr = before = M.DemandParams(price_insensitive_share=0.0, equal_price_share=0.13)   # 13% of all choices: the default until 2026-11-24
    rows = [row("**the model: shoppers differ in how much they like cultivated meat (50% of meat buyers at equal price once familiar)**"),
            row("the model before 2026-11-18: every shopper alike, 8.5 times as price-sensitive as meat in general", pr=before, liking_sd=0.0),
            row("every shopper alike, 4 times (no extra sensitivity for cultivated meat)", pr=before, liking_sd=0.0, kappa=pr.kappa_base),
            row("every shopper alike, with the slope of the sixteen premium meats (2.2 times)", pr=before, liking_sd=0.0,
                kappa=P.summary()["main"]["kappa"])]
    main, d = P.summary()["main"], P.delta_cases()["long run, central"]
    rows.append({"name": "one curve fitted to the sixteen premium meats (slope and level), with cultivated meat's corrections",
                 "curve": [P.curve(max(R - d, 0.05), main) * 100.0 for R in R_GRID], "cold": P.parity_elasticity(main),
                 "world": _world(lambda c: P.cultivated_share(c, main, d_price=d))})
    rows.append(row("the model of 2026-11-18: a normal spread of 5 utils (fifteen integration points)",
                    pr=replace(before, liking_family="normal", liking_sd=5.0)))
    return rows


_SUM: dict = {}


def summary() -> dict:
    if not _SUM:
        pr = S._demand()
        _SUM.update(pb=pb_elasticity(), pb_before=pb_elasticity(M.DemandParams(pb_committed_share=0.0, price_insensitive_share=0.0)),
                    pb_committed=committed_buyers(), cold=cold_parity_elasticity(), at={R: elasticity_at(R) for R in R_GRID},
                    premium_3x=P.curve(3.0, P.summary()["main"]) * 100.0,
                    kappa_fit=P.summary()["main"]["kappa"], kappa=pr.cult_sub_mult, variants=variants(),
                    model_world=_world(lambda c: S.shares(c, regions=("global",))["global"]))
    return _SUM


def markdown_checks() -> str:
    """The model and the model before 2026-11-18 (every shopper alike) against each measurement."""
    s = summary()
    import market_size_loop as L
    resp = L.summary()["response"]["products"]
    # farmed salmon was measured while still a premium product, so compare the model's products that are still dearer than their meat
    # at the low-lactate example's cost (price ratio above 1.5). Since 2026-11-20 only prime beef (1.37 times its meat's price) is
    # near equal price and drops out; sushi-grade seafood (1.77 times) and premium fillets and shrimp (3.09 times) are in.
    # The last column is a recorded value: the model before 2026-11-18 run through the market-size study on 2026-11-18. It is not
    # recomputed, because that study's response is the model's own; the column says so.
    names = {"chicken (organic)": "organic chicken", "pork (heritage)": "heritage pork", "beef (prime/wagyu)": "prime beef",
             "seafood (premium fillet, shrimp)": "premium fish fillets and shrimp", "seafood (sushi)": "sushi-grade seafood"}
    still = [n for n, v in resp.items() if v["R"][0] > 1.5]
    pick = [resp[n]["response"] for n in still]
    label = ", ".join(names.get(n, n) for n in still)
    v = s["variants"]
    i3 = R_GRID.index(3.0)
    out = ["| what was measured | measured | the model | the model before 2026-11-18 |", "|---|---|---|---|",
           f"| Cultivated meat at first contact and equal price: own-price elasticity (choice experiment, simulated from its fitted model) | "
           f"about {VANLOO_AT_PARITY:g} ({VANLOO_ARMS[1]:g} to {VANLOO_ARMS[0]:g} across its arms) | {v[0]['cold']:.2f} | {v[1]['cold']:.2f} |",
           f"| Share of a meat at 3 times the ordinary one's price (sixteen premium real meats, fitted) | {s['premium_3x']:.1f}% | "
           f"{S.pct_num(v[0]['curve'][i3])}% | {S.pct_num(v[1]['curve'][i3])}% |",
           f"| A premium product getting cheaper: percent more volume per percent lower price (farmed salmon) | "
           f"{SALMON_ALONG_CURVE[0]:g}–{SALMON_ALONG_CURVE[1]:g} | {min(pick):.1f}–{max(pick):.1f} ({label}: the premium products still dearer than their meat) | 3.0–3.4 (recorded on 2026-11-18 at that day's costs; not recomputed) |",
           f"| Plant-based meat's own-price elasticity (US retail; the category is about -1.3) | {PB_ELASTICITY_MEASURED:.2f} | "
           f"{s['pb']['elasticity']:.2f} | {s['pb_before']['elasticity']:.2f} (with no committed buyers, the model before 2026-11-21's fourth batch) |"]
    m = menu_summary()
    b = m["before"][0]
    out.append(f"| Adding plant-based meat priced like the meat it copies to a menu: fall in meat's share, points, and the share of the new "
               f"option's orders taken from meat (menu experiment, Hope 2026; US) | {HOPE_FALL:g} ({HOPE_CI[0]:g} to {HOPE_CI[1]:g}; "
               f"{HOPE_RULED_OUT:g} or more ruled out); about {HOPE_FROM_MEAT * 100:.0f}% from meat | {m['fall']:.2f}; "
               f"{m['from_meat'] * 100:.0f}% from meat | {b['fall']:.2f}; {b['from_meat'] * 100:.0f}% from meat (with no committed "
               f"buyers, the model before 2026-11-21's fourth batch) |")
    return "\n".join(out)


COMMITTED_CASES = (("the model", {}),
                   ("no committed buyers (the model before 2026-11-21's fourth batch)", {"pb_committed_share": 0.0, "price_insensitive_share": 0.0,
                                                                                         "liking_sd": 3.9, "liking_tail": 4.0}),
                   ("their response to its price 0.10 times other shoppers'", {"pb_committed_price_x": 0.10}),
                   ("0.50 times", {"pb_committed_price_x": 0.50}),
                   ("2% of shoppers", {"pb_committed_share": 0.02}),
                   ("10% of shoppers", {"pb_committed_share": 0.10}),
                   ("they buy 75% of the mainstream's plant-based meat", {"pb_committed_volume": 0.75}),
                   ("90%", {"pb_committed_volume": 0.90}))


def committed_buyers() -> list:
    """Plant-based meat's elasticity with its committed buyers (market_share segment "K") at each end of their three inputs, and
    what the calibration solves: the ordinary mainstream shoppers' real-meat weight and the committed buyers' liking."""
    rows = []
    for name, kw in COMMITTED_CASES:
        pr = M.DemandParams(**kw)
        rows.append({"name": name, "elasticity": pb_elasticity(pr)["elasticity"], "share": pb_elasticity(pr)["share"],
                     "w_realtissue_M": pr.w_realtissue_M, "liking": pr.pb_committed_liking if pr.pb_committed_share > 0 else None,
                     "x3": M.share(3.0, pr, which="x_meat") * 100.0})
    return rows


def markdown_committed() -> str:
    out = ["| plant-based meat's committed buyers | its own-price elasticity | its share of all choices | ordinary shoppers' real-meat "
           "weight, utils | committed buyers' liking for it, utils | cultivated meat's share of meat buyers at 3 times the price |",
           "|---|---|---|---|---|---|"]
    for r in summary()["pb_committed"]:
        out.append(f"| {r['name']} | {r['elasticity']:.2f} | {r['share']:.2f}% | {r['w_realtissue_M']:.2f} | "
                   f"{'—' if r['liking'] is None else format(r['liking'], '.2f')} | {r['x3']:.2f}% |")
    return "\n".join(out)


# ---------------------------------------------------------------------------- the price-insensitive shoppers (2026-11-22, fifth batch)
BEFORE_FIFTH = {"price_insensitive_share": 0.0, "liking_sd": 3.9, "liking_tail": 4.0, "equal_price_share": 0.13}   # the model before 2026-11-22's fifth batch
INSENSITIVE_CASES = (("the model", {}),
                     ("no price-insensitive shoppers, the spread as it was (the model before 2026-11-22's fifth batch)", BEFORE_FIFTH),
                     ("no price-insensitive shoppers, the spread as now", {"price_insensitive_share": 0.0}),
                     ("they like cultivated meat 2 utils less than other shoppers", {"price_insensitive_liking": -2.0}),
                     ("2 utils more", {"price_insensitive_liking": 2.0}),
                     ("10% of shoppers", {"price_insensitive_share": 0.10}),
                     ("15% of shoppers", {"price_insensitive_share": 0.15}),
                     ("their price response 0.10 times other shoppers'", {"price_insensitive_response": 0.10}),
                     ("0.25 times", {"price_insensitive_response": 0.25}))


def checks_of(pr: M.DemandParams, blend_curve=None) -> dict:
    """Every check for one demand model (calibrated): the spread's joint misfit and its parts (liking_spread.objective), the
    first-contact elasticity, plant-based meat's elasticity, farmed salmon's response (the premium products still dearer than
    their meat), the share of a meat's buyers at 3 times its price, and the low-lactate and all-favourable examples' world shares
    (the latter with its own demand). blend_curve: the exponent of the cut's blend rule (None = the input; 1 = the linear rule
    used until 2026-11-27, for a row that reproduces an earlier model)."""
    import liking_spread as LS
    m = LS.miss(None, pr.liking_sd, pr=pr)
    cold = cold_parity_elasticity(pr)
    resp = {n: r for n, (R0, r) in LS.salmon_response(pr, blend_curve).items() if R0 > LS.STILL_DEARER}
    curve = {R: M.share(R, pr) * 100.0 for R in (1.5,) + LS.PREMIUM_AT}   # 1.5 too: the premium block compares shapes (2026-11-24)
    out = {"cold": cold, "miss": m["miss"], "response": resp, "curve": curve, "pb": pb_elasticity(pr)["elasticity"],
           "first": M.share(1.0, pr, neophobia_x=value("neophobia_x0")) * 100.0}
    out.update(LS.objective({"elasticity": m["elasticity"], "curve": curve, "response": resp, "cold": cold, "miss": m["miss"]}))
    cost = {k: S.run(S.SCENARIOS[k].choice)["total"] for k in SCEN}
    world = lambda p, c: mm.penetration(mm.MARKETS["global"], c, income=mm.REGION_INCOME["global"], pr=p, blend_curve=blend_curve)[1] * 100.0
    out["world"] = {"central": world(pr, cost["central"]),
                    "best": world(replace(pr, equal_price_share=value(S.SCENARIOS["best"].equal_price_share)), cost["best"])}
    return out


def insensitive_cases() -> list:
    """The checks with the price-insensitive shoppers at each end of their three inputs, without them, and as the model was."""
    if "insensitive" not in _SUM:
        _SUM["insensitive"] = [{"name": name, **checks_of(M.DemandParams(**kw), blend_curve=1.0 if kw is BEFORE_FIFTH else None)}
                               for name, kw in INSENSITIVE_CASES]   # the model before had the linear blend rule
    return _SUM["insensitive"]


def markdown_insensitive() -> str:
    out = ["| price-insensitive shoppers | joint misfit (experiment, premium, salmon) | meets the experiment's two requirements | "
           "first contact: elasticity | plant-based meat's elasticity | salmon response | share of a meat's buyers at 3x, 4x its "
           "price | low-lactate example, world | all-favourable example with its own demand, world |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in insensitive_cases():
        p = r["J_parts"]
        rs = list(r["response"].values())
        out.append(f"| {r['name']} | {r['J']:.2f} ({p[0]:.2f}, {p[1]:.2f}, {p[2]:.2f}) | {'yes' if r['meets'] else 'no'} | "
                   f"{r['cold']:.2f} | {r['pb']:.2f} | {min(rs):.2f}–{max(rs):.2f} | {r['curve'][3.0]:.2f}%, {r['curve'][4.0]:.2f}% | "
                   f"{r['world']['central']:.3f}% | {r['world']['best']:.1f}% |")
    return "\n".join(out)


# ---------------------------------------------------------------------------- the menu check (2026-11-22, sixth batch)
# Hope, Green, Peacock and Mathur 2026 (Food Quality and Preference 143:105931): a randomised online menu, Chipotle-style, 4,431 US
# adults. The control menu had meat fillings and a vegetarian option; the treatment added Sofritas and a chicken-style plant-based
# meat priced like chicken and pictured as chicken. Meat orders fell by 2.1 points (95% CI -4.4 to +0.1); a fall of 5 points or more
# was ruled out. Orders by arm (as reported by Green Queen, 2026): control meat 89.1%, vegetarian 9.2%; both new options added: meat
# 87.6%, vegetarian 5.7%. So of the about 5.0 points the new options took, 1.5 came from meat (about 30%) and 3.5 from the
# vegetarian option: "most" came from the vegetarian option, as the authors say.
HOPE_FALL = 2.1                     # points of meat orders, the study's estimate
HOPE_CI = (0.0, 4.4)                # the fall's 95% interval, read as a fall (the interval's top end is a rise of 0.1)
HOPE_RULED_OUT = 5.0                # a fall this large or larger was ruled out: the pass mark
HOPE_ARMS = {"control": {"meat": 89.1, "veg": 9.2}, "both": {"meat": 87.6, "veg": 5.7}}
HOPE_FROM_MEAT = ((HOPE_ARMS["control"]["meat"] - HOPE_ARMS["both"]["meat"])
                  / ((HOPE_ARMS["control"]["meat"] - HOPE_ARMS["both"]["meat"]) + (HOPE_ARMS["control"]["veg"] - HOPE_ARMS["both"]["veg"])))
MENU_GROUPS = ((None, "every shopper"), ("M", "the mainstream (its ordinary shoppers and plant-based meat's committed buyers)"),
               ("O", "the mainstream's ordinary shoppers"), ("K", "plant-based meat's committed buyers"), ("E", "the ethical segment"))


def menu_check(pr: M.DemandParams | None = None, price: float = 1.0) -> list:
    """The menu experiment in the model. The model's four choices map onto the menu as: conventional meat = the meat fillings, the
    whole-food outside option = the vegetarian option, plant-based meat = the new options, and cultivated meat absent (it was not on
    the menu). The control menu is the model without plant-based meat; the treatment adds it at `price` times the meat it copies
    (1: priced like chicken, as in the study), with the taste the model gives plant-based meat. US shoppers (the reference income),
    for every shopper and for each group. Returns, for each group: the shares before and after (%), the fall in meat's share in
    points, and the share of the new option's choices that came from meat."""
    pr = S._demand() if pr is None else pr
    old = pr.price_pb_mult
    pr.price_pb_mult = price
    try:
        out = []
        for seg, name in MENU_GROUPS:
            if seg == "K" and pr.pb_committed_share <= 0.0:
                continue
            g = lambda which, pb: M.share(1.0, pr, cultivated_present=False, plant_based_present=pb, which=which, segment=seg) * 100.0
            c0, w0, c1, w1, p1 = g("c", False), g("w", False), g("c", True), g("w", True), g("p", True)
            out.append({"group": name, "meat_before": c0, "veg_before": w0, "meat_after": c1, "veg_after": w1, "new": p1,
                        "fall": c0 - c1, "from_meat": (c0 - c1) / p1 if p1 > 0 else float("nan")})
        return out
    finally:
        pr.price_pb_mult = old


def menu_summary() -> dict:
    """The menu check: the size of the fall in meat's share (passes when under HOPE_RULED_OUT and inside HOPE_CI) and its source
    (the share of the new option's choices taken from meat, against the study's about 30%)."""
    if "menu" not in _SUM:
        rows = menu_check()
        own = menu_check(price=S._demand().price_pb_mult)
        before = menu_check(M.DemandParams(pb_committed_share=0.0, price_insensitive_share=0.0))
        t = rows[0]
        _SUM["menu"] = {"rows": rows, "own_price": own, "before": before, "fall": t["fall"], "from_meat": t["from_meat"],
                        "size_passes": HOPE_CI[0] <= t["fall"] < HOPE_RULED_OUT and t["fall"] <= HOPE_CI[1],
                        "source_passes": t["from_meat"] < 0.5}
    return _SUM["menu"]


def markdown_menu() -> str:
    m = menu_summary()
    out = ["| shoppers | meat, without plant-based meat | vegetarian (the whole-food option), without | meat, with plant-based meat at "
           "meat's price | vegetarian, with | plant-based meat | fall in meat's share, points | of plant-based meat's choices, "
           "taken from meat |", "|---|---|---|---|---|---|---|---|"]
    for r in m["rows"]:
        out.append(f"| {r['group']} | {r['meat_before']:.2f}% | {r['veg_before']:.2f}% | {r['meat_after']:.2f}% | {r['veg_after']:.2f}% | "
                   f"{r['new']:.2f}% | {r['fall']:.2f} | {r['from_meat'] * 100:.0f}% |")
    h = HOPE_ARMS
    out.append(f"| Hope 2026, the menu experiment (both new options) | {h['control']['meat']:.1f}% | {h['control']['veg']:.1f}% | "
               f"{h['both']['meat']:.1f}% | {h['both']['veg']:.1f}% | about {100 - h['both']['meat'] - h['both']['veg'] - (100 - h['control']['meat'] - h['control']['veg']):.1f}% | "
               f"{HOPE_FALL:g} (95% interval {HOPE_CI[0]:g} to {HOPE_CI[1]:g}; 5 or more ruled out) | about {HOPE_FROM_MEAT * 100:.0f}% |")
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
    print(markdown_checks()); print(); print(markdown_variants()); print(); print(markdown_committed()); print()
    print(markdown_insensitive()); print(); print(markdown_menu())
    s = summary()
    print("\ncultivated meat's own-price elasticity by price ratio:", {R: round(e, 2) for R, e in s["at"].items()})


if __name__ == "__main__":
    main()
