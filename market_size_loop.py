#!/usr/bin/env python3
"""
market_size_loop.py — does cultivated meat get cheaper as it sells more? Cost and share solved together.

Why
---
The model runs one way: a cost of cells gives a shelf price, and the price gives a share of the meat people buy. Nothing comes back.
But two of the larger cost items are priced as today's small biopharma supply industry prices them: the cell filter's membrane
($1,450 a m2) and the plant (Humbird's equipment prices). Even a fraction of a percent of world meat would need several times all the
animal-cell tank volume that exists, and the suppliers would be remade around it (Pablo, 2026-11-18).

What this module does
---------------------
1. `learned(volume)`: the membrane's price and the plant's cost multiplier at a yearly output of cultivated meat.
   The membrane: $1,450 a m2 is a pharma price, not a cost (similar hollow fibre sells at $7-10 a m2 as dialysers and $20-50 for water
   treatment), and pharma consumables have not got cheaper with volume. So the price stays there until yearly demand is large enough for
   a food-grade supplier (a switch), and from that supplier's first price it falls by a fixed fraction for each doubling of yearly area
   (Wright's law, on yearly scale because nothing is known about the path), down to a floor. The plant and the filter loop's hardware fall
   by a fixed fraction for each doubling of the animal-cell tank volume installed over today's, down to a microbial fermentation plant
   with everything animal cells must have (`plant_items` 'yeastplus'), the floor the scenarios' bands use.
2. `cost_at(choice, volume)`: the scenario's cost with those prices (`floor_physics.explore`, nothing else changed).
3. `solve(choice)`: the yearly volume at which the share the cost buys is the share that volume is. Solved from below (starting with
   no learning) and from above (starting at the floors): if the two differ there are two resting points, and the upper one needs
   someone to carry the industry across the gap.
4. `ladder(choice)`: cost against volume, with the share that cost would buy beside the share that volume is.
5. `composition(cost)`: which products the volume comes from. The loop runs on premium products first (Pablo, 2026-11-18): at
   Central's cost nearly all sales are sushi-grade seafood and prime or wagyu beef, where cultivated meat is nearest the price it
   competes with. Their volume is what can carry the industry past the membrane switch, and the cheaper cells that follow take
   cultivated meat below those products' prices, which unlocks more of them (`premium_start`).
Nothing here changes a default. With both learning rates at zero it reproduces the scenarios exactly (tested).

    python market_size_loop.py              # the tables
"""
from __future__ import annotations

import math

import floor_physics as fp
import plant_items
import scenarios as S
from inputs import REGISTRY, value

VOLUMES = (0.01, 0.1, 0.5, 2.0, 10.0, 35.0)      # Mt of cultivated meat a year
SCEN = ("today", "central", "best")
NEVER = float("inf")
CASES = {"central": {},
         "no food-grade membrane supplier, slow plant learning": {"ms_switch_area": NEVER, "ms_lr_plant": "lo"},
         "slow learning": {"ms_lr_membrane": "lo", "ms_lr_plant": "lo", "ms_membrane_floor": "hi", "ms_food_membrane": "hi",
                           "ms_switch_area": "hi"},
         "fast learning": {"ms_lr_membrane": "hi", "ms_lr_plant": "hi", "ms_membrane_floor": "lo", "ms_food_membrane": "lo",
                           "ms_switch_area": "lo"}}


def _case(name: str) -> dict:
    return {k: (getattr(REGISTRY[k], end) if isinstance(end, str) else end) for k, end in CASES[name].items()}


def _plant_floor(kw: dict) -> float:
    """The lowest plant-cost multiplier: a microbial plant with what animal cells need, over this scenario's own plant (both in
    2018 $k per m3 of tank, as plant_items and Humbird's classes give them)."""
    if kw.get("items"):
        own = plant_items.capital(**kw["items"])["total"]
    else:
        own = value(fp.PLANT_CLASSES[kw.get("plant", "sanitary")][0])
    return min(1.0, plant_items.capital("yeastplus")["total"] / own)


def base_run(choice: dict) -> dict:
    kw = S.explore_kwargs(choice)
    r = fp.explore(**kw)
    return {"kw": kw, "cost": r["total"], "output": r["output"],                       # t per m3 of tank a year
            "area_per_kg": r["membranes"] / value("rt_membrane_price")}               # m2 of membrane used per kg of cells


def learned(volume_mt: float, base: dict, over: dict | None = None) -> dict:
    """Membrane price ($/m2), plant multiplier and the doublings behind them at `volume_mt` Mt a year of cultivated meat.
    Membrane: pharma pricing (rt_membrane_price) until yearly demand passes ms_switch_area, when a food-grade supplier sells at
    ms_food_membrane; from there it falls by ms_lr_membrane a doubling, to ms_membrane_floor. Plant and filter hardware: fall by
    ms_lr_plant for each doubling of installed tank volume over today's, to the microbial-plant floor."""
    v = lambda k: (over or {}).get(k, value(k))
    kg = volume_mt * 1e9
    area, tanks = kg * base["area_per_kg"], volume_mt * 1e6 / base["output"]          # m2 a year; m3 installed
    p0 = value("rt_membrane_price")
    if area < v("ms_switch_area"):
        d_mem, price = 0.0, p0
    else:
        d_mem = math.log2(area / v("ms_switch_area"))
        price = min(p0, max(v("ms_membrane_floor"), v("ms_food_membrane") * (1.0 - v("ms_lr_membrane")) ** d_mem))
    d_plant = math.log2(1.0 + tanks / v("ms_base_tanks"))
    plant = max(_plant_floor(base["kw"]), (1.0 - v("ms_lr_plant")) ** d_plant)
    return {"membrane_price": price, "plant_x": plant, "doublings_membrane": d_mem, "doublings_plant": d_plant,
            "area_m2": area, "tanks_m3": tanks}


def cost_at(choice: dict, volume_mt: float, over: dict | None = None, base: dict | None = None) -> dict:
    base = base_run(choice) if base is None else base
    L = learned(volume_mt, base, over)
    with fp._inputs_set({"rt_membrane_price": L["membrane_price"], "rt_tff_hw": value("rt_tff_hw") * L["plant_x"]}):
        r = fp.explore(**{**base["kw"], "capex_x": base["kw"].get("capex_x", 1.0) * L["plant_x"]})
    return {**L, "cost": r["total"]}


def _share(cost: float) -> float:
    return S.shares(cost, regions=("global",))["global"]


def share_of_volume(volume_mt: float, over: dict | None = None) -> float:
    return 100.0 * volume_mt / (over or {}).get("ms_world_meat", value("ms_world_meat"))


def solve(choice: dict, over: dict | None = None, start: str = "below", share=_share) -> dict:
    """The resting point: the volume whose learned cost buys exactly that volume's share. start='below' begins with no learning,
    'above' at the floors. Damped fixed-point iteration on log volume."""
    base = base_run(choice)
    W = (over or {}).get("ms_world_meat", value("ms_world_meat"))
    vol = 1e-6 if start == "below" else W
    for _ in range(200):
        c = cost_at(choice, vol, over, base)
        new = max(1e-6, share(c["cost"]) / 100.0 * W)
        if abs(math.log(new / vol)) < 1e-6:
            break
        vol = math.exp(0.5 * math.log(vol) + 0.5 * math.log(new))
    c = cost_at(choice, vol, over, base)
    return {**c, "volume_mt": vol, "share": share(c["cost"])}


def composition(cost: float, over: dict | None = None) -> dict:
    """Where the volume comes from at a cost of cells: Mt a year by tier (premium, cut, basic), the premium tier's own share of
    its market, and each premium product's price ratio and share. Same roll-up as the share (meat_market.penetration)."""
    import meat_market as mm
    W = (over or {}).get("ms_world_meat", value("ms_world_meat"))
    mk = mm.MARKETS["global"]
    bases, wsum = mm.species_bases(mk), sum(mt.w_vol for mt in mk)
    rows, _vol, _val = mm.penetration(mk, cost, income=mm.REGION_INCOME["global"], pr=S._demand())
    mt_tier = lambda mt: mm.tier(mt, bases[mm.animal_of(mt)])
    out = {"premium": 0.0, "cut": 0.0, "basic": 0.0, "products": {}}
    market = {"premium": 0.0, "cut": 0.0, "basic": 0.0}
    for mt, R, sh in rows:
        t = mt_tier(mt)
        out[t] += mt.w_vol / wsum * sh * W
        market[t] += mt.w_vol / wsum * W
        if t == "premium":
            out["products"][mt.name] = {"R": float(R), "share": float(sh) * 100.0, "mt": mt.w_vol / wsum * sh * W,
                                        "market_mt": mt.w_vol / wsum * W, "price": mt.p_conv}
    out["total"] = out["premium"] + out["cut"] + out["basic"]
    out["premium_market_mt"] = market["premium"]
    out["premium_of_sales"] = out["premium"] / out["total"] if out["total"] else 0.0
    return out


def premium_start(choice: dict, over: dict | None = None) -> dict:
    """Do premium products alone carry the industry past the membrane switch? Their volume at the scenario's own cost (no learning),
    the membrane area that needs, and the switch."""
    base = base_run(choice)
    comp = composition(base["cost"], over)
    area = comp["premium"] * 1e9 * base["area_per_kg"]
    switch = (over or {}).get("ms_switch_area", value("ms_switch_area"))
    return {"premium_mt": comp["premium"], "area_m2": area, "switch_m2": switch, "crosses": area >= switch,
            "switch_mt": switch / base["area_per_kg"] / 1e9}


def ladder(choice: dict, over: dict | None = None) -> list:
    base = base_run(choice)
    rows = []
    for vol in VOLUMES:
        c = cost_at(choice, vol, over, base)
        rows.append({**c, "volume_mt": vol, "share_is": share_of_volume(vol, over), "share_bought": _share(c["cost"])})
    return rows


# ---------------------------------------------------------------------------- how strong is the loop, and what is it sensitive to
SENS_INPUTS = ("ms_switch_area", "ms_food_membrane", "ms_lr_membrane", "ms_membrane_floor", "ms_lr_plant", "ms_base_tanks",
               "ms_world_meat")
SENS_NAMES = {"ms_switch_area": "Membrane demand at which a food-grade supplier appears", "ms_food_membrane": "That supplier's first price",
              "ms_lr_membrane": "Membrane's price fall per doubling", "ms_membrane_floor": "Membrane's price floor",
              "ms_lr_plant": "Plant's cost fall per doubling", "ms_base_tanks": "Animal-cell tanks installed today",
              "ms_world_meat": "World meat, boneless"}


def passes(choice: dict) -> dict:
    """How much of the gain is a loop: the scenario's own cost and share; the cost with the learning its own volume brings and the
    share that buys (the first pass); and the resting point. `later_rounds` is the part of the share gain that comes after the first."""
    base = base_run(choice)
    s0 = _share(base["cost"])
    c1 = cost_at(choice, s0 / 100.0 * value("ms_world_meat"), None, base)
    s1 = _share(c1["cost"])
    r = solve(choice)
    return {"own": (base["cost"], s0), "first": (c1["cost"], s1), "rest": (r["cost"], r["share"]),
            "later_rounds": (r["share"] - s1) / (r["share"] - s0) if r["share"] > s0 else 0.0}


def sensitivity(choice: dict) -> list:
    """The resting point with each market-size input at the ends of its range, the others at their values."""
    rows = []
    for name in SENS_INPUTS:
        v = REGISTRY[name]
        lo, hi = solve(choice, {name: v.lo}), solve(choice, {name: v.hi})
        rows.append({"key": name, "lo": v.lo, "hi": v.hi, "cost": (lo["cost"], hi["cost"]), "share": (lo["share"], hi["share"])})
    return rows


def anchored(choice: dict) -> dict:
    """The demand side checked: the resting point with the share taken from the curve fitted to premium real meats
    (premium_curve, long-run central corrections) in place of the main model's."""
    import premium_curve as P
    main, d = P.summary()["main"], P.delta_cases()["long run, central"]
    f = lambda cost: P.cultivated_share(cost, main, d_price=d)
    r = solve(choice, share=f)
    return {"own": f(base_run(choice)["cost"]), "cost": r["cost"], "share": r["share"]}


# What history shows for a premium animal product whose price fell (research_notes/market_size_loop.md, section 6): percent more
# volume per percent lower price. Along the demand curve, while the product is still premium (farmed salmon, published
# elasticities); and in total, with demand growth mixed in (salmon 1985-96 2.2, salmon 1982-99 3.7, US broilers 1955-87 1.3,
# US catfish 1980-99 4.1).
HISTORY_ALONG_CURVE = (1.0, 1.5)
HISTORY_TOTAL = (1.3, 4.1)


def premium_response(choice: dict) -> dict:
    """How strongly the model's premium products respond to price: percent more share per percent lower price ratio, for each
    premium product, between the scenario's own cost and its cost once the food-grade membrane exists ('from above')."""
    c0, c1 = base_run(choice)["cost"], solve(choice, start="above")["cost"]
    a, b = composition(c0)["products"], composition(c1)["products"]
    out = {}
    for n in a:
        if a[n]["share"] > 0 and b[n]["R"] < a[n]["R"]:
            out[n] = {"R": (a[n]["R"], b[n]["R"]), "share": (a[n]["share"], b[n]["share"]),
                      "response": math.log(b[n]["share"] / a[n]["share"]) / math.log(a[n]["R"] / b[n]["R"])}
    return {"costs": (c0, c1), "products": out}


# ---------------------------------------------------------------------------- the loop backwards: a plant built for sales that fall
UTILISATION = (1.0, 0.8, 0.6, 0.4)     # Beyond Meat's sales fell about 40% from their peak after its plants were built (Knowles 2026)


def underused(choice: dict, utilisation: float) -> dict:
    """Cost of a kilo of cells from a plant that sells only `utilisation` of what it was built for: the plant's yearly charge and
    its labour are paid whatever it makes, so each is divided by the utilisation; everything else scales with output. The
    scenarios are at 1 (every kilo the plant can make is sold)."""
    r = fp.explore(**S.explore_kwargs(choice))
    fixed = r["capital"] + r["labour"]
    return {"cost": r["total"] + fixed * (1.0 / utilisation - 1.0), "fixed": fixed, "own": r["total"]}


def markdown_underused() -> str:
    out = ["| share of the plant's capacity that is sold | " + " | ".join(_name(k) for k in SCEN) + " |", "|---|" + "---|" * len(SCEN)]
    for u in UTILISATION:
        out.append(f"| {u:.0%} | " + " | ".join(f"${underused(S.SCENARIOS[k].choice, u)['cost']:.2f}" for k in SCEN) + " |")
    return "\n".join(out)


# ---------------------------------------------------------------------------- summary and tables
_SUM: dict = {}


def summary() -> dict:
    if _SUM:
        return _SUM
    choices = {k: S.SCENARIOS[k].choice for k in SCEN}
    _SUM.update(base={k: base_run(c) for k, c in choices.items()},
                model_share={k: _share(base_run(c)["cost"]) for k, c in choices.items()},
                ladder={k: ladder(c) for k, c in choices.items()},
                solved={(k, case, start): solve(c, _case(case), start) for k, c in choices.items() for case in CASES
                        for start in ("below", "above")},
                floor={k: cost_at(c, 1e6) for k, c in choices.items()},
                start={(k, case): premium_start(c, _case(case)) for k, c in choices.items() for case in CASES})
    _SUM.update(passes={k: passes(choices[k]) for k in ("central", "best")},
                sens={k: sensitivity(choices[k]) for k in ("central", "best")},
                anchored={k: anchored(choices[k]) for k in ("central", "best")},
                response=premium_response(choices["central"]))
    sv = _SUM["solved"]
    _SUM["comp"] = {}
    for k in SCEN:
        lo, hi = sv[(k, "central", "below")], sv[(k, "central", "above")]
        stages = [("no learning", _SUM["base"][k]["cost"]), ("resting point", lo["cost"])]
        if hi["volume_mt"] > 1.001 * lo["volume_mt"]:           # two resting points: show the upper one too
            stages.append(("upper resting point", hi["cost"]))
        for stage, cost in stages:
            _SUM["comp"][(k, stage)] = {**composition(cost), "cost": cost}
    return _SUM


def _name(k: str) -> str:
    return S.SCENARIOS[k].name.split(":")[0]


def markdown_ladder() -> str:
    s = summary()
    out = []
    for k in SCEN:
        out += [f"**{_name(k)}** (no learning: ${s['base'][k]['cost']:.2f})", "",
                "| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | "
                "cells, $/kg | share that cost would buy |", "|---|---|---|---|---|---|---|"]
        for r in s["ladder"][k]:
            out.append(f"| {r['volume_mt']:g} | {r['share_is']:.3g}% | {r['tanks_m3']:,.0f} | {r['membrane_price']:,.0f} | "
                       f"{r['plant_x']:.2f}× | ${r['cost']:.2f} | {r['share_bought']:.2f}% |")
        out.append("")
    return "\n".join(out).rstrip()


def markdown_solved() -> str:
    s = summary()
    out = ["| scenario | learning | the main model: cells, share | resting point from below: cells, share, Mt a year | from above: cells, share, "
           "Mt a year |", "|---|---|---|---|---|"]
    for k in SCEN:
        for case in CASES:
            lo, hi = s["solved"][(k, case, "below")], s["solved"][(k, case, "above")]
            out.append(f"| {_name(k)} | {case} | ${s['base'][k]['cost']:.2f}, {s['model_share'][k]:.2f}% | "
                       f"${lo['cost']:.2f}, {lo['share']:.2f}%, {lo['volume_mt']:.2f} | ${hi['cost']:.2f}, {hi['share']:.2f}%, {hi['volume_mt']:.2f} |")
    return "\n".join(out)


def markdown_composition() -> str:
    s = summary()
    names = list(s["comp"][(SCEN[0], "no learning")]["products"])
    out = ["| scenario | stage | cells, $/kg | sold, Mt a year: premium products, cuts, mince and processed | premium products' part of sales | " +
           " | ".join(f"{n}: price against it, share of it" for n in names) + " |", "|---|---|---|---|---|" + "---|" * len(names)]
    for k in SCEN:
        for stage in ("no learning", "resting point", "upper resting point"):
            if (k, stage) not in s["comp"]:
                continue
            c = s["comp"][(k, stage)]
            cost = c["cost"]
            out.append(f"| {_name(k)} | {stage} | ${cost:.2f} | {c['premium']:.2f}, {c['cut']:.2f}, {c['basic']:.2f} | {c['premium_of_sales']:.0%} | " +
                       " | ".join(f"{c['products'][n]['R']:.2f}×, {c['products'][n]['share']:.1f}%" for n in names) + " |")
    return "\n".join(out)


def markdown_start() -> str:
    s = summary()
    out = ["| scenario | learning | premium products sold at the scenario's own cost, Mt a year | membrane that needs, million m² a year | "
           "the switch, million m² a year | do premium products alone cross it? |", "|---|---|---|---|---|---|"]
    for k in SCEN:
        for case in CASES:
            st = s["start"][(k, case)]
            sw = "never" if st["switch_m2"] == NEVER else f"{st['switch_m2'] / 1e6:.1f}"
            out.append(f"| {_name(k)} | {case} | {st['premium_mt']:.2f} | {st['area_m2'] / 1e6:.2f} | {sw} | {'yes' if st['crosses'] else 'no'} |")
    return "\n".join(out)


def markdown_passes() -> str:
    s = summary()
    out = ["| scenario | its own cost and share | first pass: the learning its own volume brings | resting point | part of the share gain "
           "from later rounds | resting point with demand anchored on premium meats (its own share there) |", "|---|---|---|---|---|---|"]
    for k in ("central", "best"):
        p, a = s["passes"][k], s["anchored"][k]
        out.append(f"| {_name(k)} | ${p['own'][0]:.2f}, {p['own'][1]:.2f}% | ${p['first'][0]:.2f}, {p['first'][1]:.2f}% | ${p['rest'][0]:.2f}, {p['rest'][1]:.2f}% | "
                   f"{p['later_rounds']:.0%} | ${a['cost']:.2f}, {a['share']:.2f}% ({a['own']:.2f}%) |")
    return "\n".join(out)


def markdown_sensitivity() -> str:
    s = summary()
    out = ["| input, across its range | " + " | ".join(f"{_name(k)}: cells, share" for k in ("central", "best")) + " |", "|---|---|---|"]
    for i, name in enumerate(SENS_INPUTS):
        v = REGISTRY[name]
        cells = []
        for k in ("central", "best"):
            r = s["sens"][k][i]
            cells.append(f"${r['cost'][0]:.2f} to ${r['cost'][1]:.2f}, {r['share'][0]:.2f}% to {r['share'][1]:.2f}%")
        out.append(f"| {SENS_NAMES[name]} ({v.lo:g} to {v.hi:g} {v.unit}) | " + " | ".join(cells) + " |")
    return "\n".join(out)


def markdown_response() -> str:
    r = summary()["response"]
    out = [f"| premium product | price against it: at ${r['costs'][0]:.2f} a kilo of cells, at ${r['costs'][1]:.2f} | cultivated meat's share of it | "
           "percent more share per percent lower price |", "|---|---|---|---|"]
    for n, v in r["products"].items():
        out.append(f"| {n} | {v['R'][0]:.2f}×, {v['R'][1]:.2f}× | {v['share'][0]:.2f}%, {v['share'][1]:.2f}% | {v['response']:.1f} |")
    out.append(f"| history, along the demand curve (farmed salmon while still a premium product) | | | {HISTORY_ALONG_CURVE[0]:g}–{HISTORY_ALONG_CURVE[1]:g} |")
    out.append(f"| history, in total, with demand growth mixed in (salmon, US broilers, US catfish) | | | {HISTORY_TOTAL[0]:g}–{HISTORY_TOTAL[1]:g} |")
    return "\n".join(out)


def main() -> None:
    print(markdown_ladder()); print(); print(markdown_solved()); print(); print(markdown_composition()); print(); print(markdown_start())
    print(); print(markdown_passes()); print(); print(markdown_sensitivity()); print(); print(markdown_response()); print(); print(markdown_underused())
    s = summary()
    print("\ncost with both items at their floors:", {k: round(v["cost"], 2) for k, v in s["floor"].items()})


if __name__ == "__main__":
    main()
