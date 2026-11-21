#!/usr/bin/env python3
"""
medium_reuse.py — can the medium be cleaned and reused, and what would that save?

Why
---
After the tank's gas limits, the litres of medium per kg of cells are the largest cost left (design_space.py). In perfusion
those litres are set by waste: enough liquid must leave the tank to carry the ammonia out at the level cells tolerate. Each
litre costs its nutrients, its growth factors, its bubble protectant, and a pass through the membranes that hold the cells
back. A device that takes the waste out of the liquid and returns it could save some of that. This module asks how much.

The accounting that matters
---------------------------
To take a mole of ammonia out of a tank held at 4 mmol/L (the scenarios' limit, `sc_nh3_limit`), 250 litres of liquid must leave
the tank through the cell filter,
whether they are thrown away or cleaned and returned. So a device ON THE PERMEATE (the cell-free liquid the filter passes)
saves the medium, the growth factors and the protectant in the liquid it returns, but not the filter. Only a device that
takes the waste out with no liquid drawn through the cell filter (dialysis across the culture, a sorbent or an exchange
membrane in the tank) saves the filter too, and then its own membrane meets the cells.

`balance` gives the litres: fresh medium bought, liquid cleaned and returned, liquid through the cell filter.
`cost` prices a route for a scenario. Since 2026-11-20 the calculation itself lives in `floor_physics.explore` (its `clean`
argument, with the litres cleaned as `clean_loop`): the litres each waste still asks for, the loop's passes through the cell
filter, the growth factors it loses, the dialysate and the device. `cost` calls it, so there is one implementation, and the
page's levers use the same one. `best` picks the litres to clean that cost least. `routes()` are the candidates, each with
its evidence; `PAGE_ROUTES` are the three the page offers. Nothing here changes a default.

All litres here are per kilo of cells harvested, as explore reports them (`harvested_share`: bubbles kill some of the cells
grown and the harvest loses some).

    python medium_reuse.py              # the tables, as text
    python medium_reuse.py --markdown   # the tables the note and RESULTS.md quote
"""
from __future__ import annotations

import sys

import floor_physics as fp
import scenarios as S
from inputs import value

KEYS = ("cautious", "central", "best")    # 2026-11-19 restructure: rung 1 ("today") is fed-batch, which has no permeate to clean; the published cells in perfusion are "cautious"


def base(key: str = "central") -> tuple:
    """(explore arguments, explore result) of a scenario."""
    kw = S.explore_kwargs(S.SCENARIOS[key].choice)
    return kw, fp.explore(**kw)


def balance(terms: dict, bleed: float, loop: float = 0.0, nh3: float = 0.0, lac: float = 0.0, other: float = 0.0,
            in_tank: bool = False) -> dict:
    """Litres per kg of cells. `terms` are explore's `medium_terms` (the litres each limit asks for); `loop` is the liquid
    cleaned and returned; `nh3`, `lac` and `other` are the shares of each waste the device takes from a litre in one pass
    (`other`: the by-products behind the least medium flow). Each litre cleaned stands in for that share of a litre thrown
    away. Fresh medium cannot fall below the liquid that leaves with the harvested cells. fresh: medium bought; filtered: liquid through the cell filter (the loop too, unless `in_tank`)."""
    need = {"ammonia": max(0.0, terms["ammonia"] - loop * nh3), "lactate": max(0.0, terms["lactate"] - loop * lac),
            "least flow": max(0.0, terms["least flow"] - loop * other), "nutrients": terms["nutrients"],
            "the liquid that leaves with the cells": bleed}
    fresh = max(need.values())
    return {"fresh": fresh, "set_by": max(need, key=need.get), "loop": loop,
            "filtered": max(0.0, fresh - bleed) + (0.0 if in_tank else loop)}


def cost(key: str = "central", loop: float = 0.0, nh3: float = 0.0, lac: float = 0.0, other: float = 0.0,
         in_tank: bool = False, gf_kept: float | None = None, device_l: float = 0.0, dialysate_l: float = 0.0,
         exchange_membrane: float = 0.0) -> dict:
    """Cost per kg of cells of a scenario with `loop` litres per kg cleaned and returned. `device_l`: $ per litre cleaned;
    `dialysate_l`: litres of basal medium bought per litre cleaned (dialysis); `exchange_membrane`: for a device across the
    culture, its membrane and hardware as a share of what filtering the same litres through the cell filter costs.
    The calculation is floor_physics.explore's (`clean` as a dict of these numbers, `clean_loop` the litres per kilo grown)."""
    gf_kept = value("mr_gf_kept") if gf_kept is None else gf_kept
    kw, r0 = base(key)
    live = r0["harvested_share"]                        # kilos harvested per kilo grown
    route = {"nh3": nh3, "lac": lac, "other": other, "in_tank": in_tank, "gf_kept": gf_kept, "device_l": device_l,
             "dialysate_l": dialysate_l, "exchange_membrane": exchange_membrane}
    r = fp.explore(**{**kw, "clean": route, "clean_loop": loop * live}) if loop > 0 else r0
    return _report(kw, r0, r, loop, in_tank)


def _report(kw: dict, r0: dict, r: dict, loop: float, in_tank: bool) -> dict:
    """A route's explore result `r` against the scenario's own `r0`, as the tables read it (litres per kilo harvested)."""
    bleed = 1000.0 / r0["density"] / r0["harvested_share"]
    perm0 = max(1e-9, r0["medium_l"] - bleed)
    charge = kw.get("charge", value("plant_charge_mature"))
    filter_l = r0["membranes"] / perm0 + charge * r0["retention_capex"] / r0["output"] / perm0   # $ per litre filtered
    extra = {k: r["clean_parts"].get(k, 0.0) for k in ("filter for the loop", "exchange membrane", "growth factors lost",
                                                       "dialysate", "device")}
    return {"fresh": r["medium_l"], "set_by": r["medium_set_by"], "loop": loop,
            "filtered": max(0.0, r["medium_l"] - bleed) + (0.0 if in_tank else loop),
            "total": r["total"], "saving": r0["total"] - r["total"], "base": r0["total"], "extra": extra, "filter_l": filter_l,
            "bleed": bleed, "parts": {k: r[k] for k in ("feedstock", "growth_factors", "protectant", "membranes")}}


def per_litre(key: str = "central") -> dict:
    """What a litre of medium that leaves the tank costs, by part, $ per litre: the medium itself, its growth factors, its
    bubble protectant, and filtering it. `removal_to_pay`: the share of the waste a free device on the permeate must take in
    one pass before it saves anything (each litre cleaned is filtered once and stands in for that share of a litre)."""
    hi, lo = cost(key, loop=0.0), None
    kw, r0 = base(key)
    live = r0["harvested_share"]                        # explore's `medium_l` argument is per kilo grown
    lo = fp.explore(**{**kw, "medium_l": (r0["medium_l"] - 1.0) * live})
    parts = {k: r0[k] - lo[k] for k in ("feedstock", "growth_factors", "protectant")}
    parts["filter"] = hi["filter_l"]
    parts["all"] = sum(parts.values())
    parts["removal_to_pay"] = parts["filter"] / parts["all"]
    return parts


def best(key: str = "central", **args) -> dict:
    """The route at the litres cleaned that cost least (none, if it never pays): explore's own search (`clean` with no share
    given), every 0.1 litre per kilo. The cost is piecewise linear in the litres, so that grid is exact enough."""
    kw, r0 = base(key)
    route = {"gf_kept": value("mr_gf_kept"), **args}
    r = fp.explore(**{**kw, "clean": route})
    return _report(kw, r0, r, r["clean_loop"], bool(route.get("in_tank")))


def breakeven_device(key: str, args: dict) -> float:
    """The device cost per litre cleaned below which the route saves anything (negative: never)."""
    free = {**args, "device_l": 0.0}
    t = base(key)[1]["medium_terms"]
    return max(cost(key, loop=x, **free)["saving"] / x for x in (0.5 * i for i in range(1, int(2 * max(t.values()) / 0.5))))


def exchange_share() -> float:
    """An exchange membrane across the culture, as a share of the cell filter's cost per litre: the same fibre and hardware,
    clearing more litres per m2 by diffusion than the filter passes by flow."""
    return value("rt_flux_lmh") / value("mr_exchange_clearance")


def routes() -> dict:
    """The candidate routes: name -> (arguments of `cost`, what has been shown, what is assumed)."""
    ed = {"nh3": value("mr_ed_nh3"), "lac": value("mr_ed_lac"), "device_l": value("mr_ed_cost_l")}
    d, dl = value("mr_dial_removal"), value("mr_dialysate_l")
    dial = {"nh3": d, "lac": d, "other": d}
    reused = {"dialysate_l": value("mr_dialysate_makeup") * dl}        # basal medium bought, per litre cleaned
    clean = dl * value("mr_ed_cost_l")                                  # cleaning the dialysate, per litre of medium cleaned
    return {
        "Electrodialysis of the permeate":
            (ed, "over 90% of ammonium and 99% of lactate taken from medium by selective membranes (Nir 2023, as cited in "
                 "Soccol et al. 2024; the report itself was not found); hybridoma grew 30-50% better with ammonium and "
                 "lactate removed electrically (Chang et al. 1995, abstract)",
             "the cost per litre is an estimate from first principles (section 6 of the note); 90% of growth factors survive a pass; the other by-products stay"),
        "Dialysis of the permeate, dialysate thrown away":
            ({**dial, "dialysate_l": dl, "device_l": value("mr_dial_cost_l")},
             "CHO at 73 million cells/mL held 10 days with no medium change; lactate down 92% (YekrangSafakar et al. 2022, "
             "which dialysed the culture itself, not a permeate)",
             "2.1 L of basal medium per litre cleaned; ammonia and the other by-products follow lactate"),
        "Dialysis of the permeate, dialysate cleaned and reused":
            ({**dial, **reused, "device_l": value("mr_dial_cost_l") + clean},
             "patent claims only (Yissum / Future Meat WO2018011805: 90% recirculated; Avant Meats WO2023012523: bacteria "
             "and an enzyme clean the dialysate)",
             "the dialysate is cleaned at the electrodialysis cost and 10% of it replaced"),
        "Dialysis across the culture, dialysate cleaned and reused; the exchange membrane costs what the cell filter does":
            ({**dial, **reused, "in_tank": True, "exchange_membrane": 1.0, "device_l": clean},
             "the same study, on 2 billion cells and a 1.4 m² dialyser",
             "litre for litre, the exchange membrane and its hardware cost what the cell filter does"),
        "The same; the exchange membrane clears 10 L/m²/h, twice what the filter passes":
            ({**dial, **reused, "in_tank": True, "exchange_membrane": exchange_share(), "device_l": clean},
             "a haemodialyser's clearance on blood, over 4-hour sessions (from memory, not checked)",
             "that clearance holds for weeks in a culture of 190 g/L"),
    }


def page_routes() -> dict:
    """The routes the page's lever offers (floor_physics.explore's `clean`): key -> name, what it is in one line, what has
    been shown so far, and what limits it. The numbers behind each are floor_physics.clean_route(key); the dialysis route is
    the fourth of `routes()` (across the culture, the dialysate cleaned and reused, its membrane at the cell filter's cost)."""
    rt = routes()
    names = list(rt)
    return {
        "none": {"name": "None: every litre is used once",
                 "what": "Spent medium leaves the tank and is thrown away.", "shown": "", "limits": ""},
        "exchanger": {
            "name": "An ammonium exchanger",
            "what": "The cell-free liquid the filter passes runs through a bed of mineral or resin that takes up ammonium and "
                    "gives back sodium, then returns to the tank.",
            "shown": "No one has measured how much ammonium such a bed holds in culture medium; the model's figure "
                     f"({value('pf_sorbent_q'):.2f} mol a kilo of sorbent) is derived from measurements in simpler solutions.",
            "limits": "It takes out ammonia only, so it saves nothing where lactate sets the litres. The liquid it cleans "
                      "still passes the cell filter. The sodium it gives back adds salt."},
        "electrodialysis": {
            "name": "Electrodialysis",
            "what": "The cell-free liquid the filter passes runs between membranes under a voltage, which pulls ammonium and "
                    "lactate out of it, then returns to the tank.",
            "shown": _plain(rt[names[0]][1]),
            "limits": "The liquid it cleans still passes the cell filter. The other by-products stay in it. Its cost a litre "
                      f"(${value('mr_ed_cost_l'):.2f}) is this model's arithmetic, not a quoted price."},
        "dialysis": {
            "name": "Dialysis across a membrane",
            "what": "The culture, or its cell-free liquid, passes one side of a membrane and a cheap salt solution the other. "
                    "Ammonia and lactate cross into the salt solution; proteins and cells do not. Here the culture itself "
                    "passes the membrane, and the salt solution is cleaned and used again.",
            "shown": _plain(rt[names[1]][1]) + ". Reusing the salt solution: " + rt[names[2]][1] + ".",
            "limits": "Its membrane meets the cells, so it is priced as the cell filter is, litre for litre. Nobody has run "
                      "one for weeks in a culture as dense as these. Ammonia and the other by-products are assumed to cross "
                      "as lactate does; that has not been measured."},
    }


def _plain(text: str) -> str:
    """A route's evidence in the page's words: the cell line named for what it is, a first capital."""
    t = text.replace("CHO at", "hamster ovary cells (CHO) at").replace("hybridoma", "antibody-making cells (hybridoma)")
    return t[0].upper() + t[1:]


def sorbent_best(key: str = "central") -> dict:
    """The ammonium exchanger on the permeate (explore's `clean="exchanger"`, the same calculation as its `sorbent` lever), at
    the share that costs least (explore's own search: hundredths, up to 90%)."""
    kw, r0 = base(key)
    bleed = 1000.0 / r0["density"] / r0["harvested_share"]   # fresh medium cannot fall below the liquid that leaves with the cells
    r = fp.explore(**{**kw, "clean": "exchanger"})
    loop = r["clean_share"] * r0["medium_terms"]["ammonia"]
    return {"share": r["clean_share"], "total": r["total"], "saving": r0["total"] - r["total"], "fresh": r["medium_l"], "loop": loop,
            "filtered": r["medium_l"] - bleed + loop, "base": r0["total"]}


def sensitivity(key: str = "central") -> list:
    """How the saving of two routes moves when one uncertain input goes to the low or high end of its range:
    [(input, low, high, {route: (saving at low, saving at high)})]."""
    from inputs import REGISTRY
    names = list(routes())
    pick = (names[0], names[4])
    rows = []
    for k in ("mr_ed_cost_l", "mr_gf_kept", "mr_ed_nh3", "mr_dial_removal", "mr_dialysate_makeup", "mr_exchange_clearance",
              "rt_membrane_life", "pf_min_perfusion"):
        res = {}
        for end in ("lo", "hi"):
            with fp._inputs_set({k: getattr(REGISTRY[k], end)}):
                rt = routes()
                for n in pick:
                    res.setdefault(n, []).append(best(key, **rt[n][0])["saving"])
        rows.append((k, REGISTRY[k].lo, REGISTRY[k].hi, {n: tuple(v) for n, v in res.items()}))
    return rows


def bounds(key: str = "central") -> dict:
    """What a perfect, free device could save: on the permeate (the filter stays) and across the culture (the filter goes)."""
    return {"on the permeate": best(key, nh3=1.0, lac=1.0, other=1.0, gf_kept=1.0),
            "across the culture": best(key, nh3=1.0, lac=1.0, other=1.0, gf_kept=1.0, in_tank=True)}


def summary() -> dict:
    out = {}
    for key in KEYS:
        _kw, r0 = base(key)
        out[key] = {"base": r0, "sorbent": sorbent_best(key), "bounds": bounds(key),
                    "routes": {n: best(key, **a) for n, (a, _s, _x) in routes().items()},
                    "breakeven": {n: breakeven_device(key, a) for n, (a, _s, _x) in routes().items()}}
    return out


# ----------------------------------------------------------------------------
def _money(x: float) -> str:
    return "nothing" if abs(x) < 0.005 else f"${x:.2f}"


def markdown(key: str = "central") -> str:
    s = summary()[key]
    r0, t = s["base"], s["base"]["medium_terms"]
    bleed = 1000.0 / r0["density"] / r0["harvested_share"]
    name = S.SCENARIOS[key].name
    nh3_limit = base(key)[0].get("nh3_limit", value("pf_nh3_limit"))     # the scenarios' own limit (sc_nh3_limit, 4 mmol/L)
    out = [f"| what sets the litres of medium ({name}) | litres per kg of cells |", "|---|---|",
           f"| ammonia, held at {nh3_limit:.0f} mmol/L | {t['ammonia']:.1f} |",
           f"| the least flow the cells need for everything else | {t['least flow']:.1f} |",
           f"| lactate, within the salt limit | {t['lactate']:.1f} |",
           f"| the nutrients, as a concentrate | {t['nutrients']:.1f} |",
           f"| leaves with the cells, unfiltered | {bleed:.1f} |", "",
           "| route | fresh medium, L/kg | cleaned and returned, L/kg | through the cell filter, L/kg | cells, $/kg | saves | "
           "pays if the device costs under |", "|---|---|---|---|---|---|---|",
           f"| No reuse | {r0['medium_l']:.1f} | 0 | {r0['medium_l'] - bleed:.1f} | **${r0['total']:.2f}** | | |"]
    sb = s["sorbent"]
    out.append(f"| An ammonium exchanger on the permeate, taking {sb['share'] * 100:.0f}% of the ammonia | {sb['fresh']:.1f} | "
               f"{sb['loop']:.1f} | {sb['filtered']:.1f} | **${sb['total']:.2f}** | {_money(sb['saving'])} | (priced by its "
               f"sorbent: {value('pf_sorbent_q'):.2f} mol/kg at ${value('pf_sorbent_price'):.0f}/kg, used once) |")
    for n, c in s["routes"].items():
        be = s["breakeven"][n]
        out.append(f"| {n} | {c['fresh']:.1f} | {c['loop']:.1f} | {c['filtered']:.1f} | **${c['total']:.2f}** | "
                   f"{_money(c['saving'])} | {'$%.2f a litre' % be if be > 0 else 'never'} |")
    for lab, c in s["bounds"].items():
        out.append(f"| *A perfect, free device {lab}* | {c['fresh']:.1f} | {c['loop']:.1f} | {c['filtered']:.1f} | "
                   f"*${c['total']:.2f}* | *{_money(c['saving'])}* | |")
    return "\n".join(out)


def markdown_scenarios() -> str:
    s = summary()
    names = list(routes())
    out = ["| scenario | no reuse | exchanger on the permeate | electrodialysis of the permeate | dialysis of the permeate, "
           "dialysate reused | dialysis across the culture, at the filter's cost | the same, at twice the filter's clearance | "
           "perfect and free, on the permeate | perfect and free, across the culture |", "|---|---|---|---|---|---|---|---|---|"]
    for key in KEYS:
        d = s[key]
        cells = [d["sorbent"]["total"], d["routes"][names[0]]["total"], d["routes"][names[2]]["total"],
                 d["routes"][names[3]]["total"], d["routes"][names[4]]["total"], d["bounds"]["on the permeate"]["total"],
                 d["bounds"]["across the culture"]["total"]]
        out.append(f"| {S.SCENARIOS[key].name} | **${d['base']['total']:.2f}** | " + " | ".join(f"${c:.2f}" for c in cells) + " |")
    return "\n".join(out)


SENS_NAMES = {"mr_ed_cost_l": "electrodialysis, $ per litre treated", "mr_gf_kept": "growth factors that survive a pass",
              "mr_ed_nh3": "ammonium electrodialysis takes in a pass", "mr_dial_removal": "waste dialysis takes in a pass",
              "mr_dialysate_makeup": "dialysate replaced per pass", "mr_exchange_clearance": "exchange membrane clearance, L/m²/h",
              "rt_membrane_life": "litres a m² of cell filter lasts", "pf_min_perfusion": "least medium flow, mL per g a day"}


def markdown_sensitivity(key: str = "central") -> str:
    rows = sensitivity(key)
    names = list(rows[0][3])
    out = ["| input | low | high | electrodialysis of the permeate saves | dialysis across the culture, at twice the filter's "
           "clearance, saves |", "|---|---|---|---|---|"]
    for k, lo, hi, res in rows:
        out.append(f"| {SENS_NAMES[k]} (`{k}`) | {lo:g} | {hi:g} | " +
                   " | ".join(f"{_money(res[n][0])} to {_money(res[n][1])}" for n in names) + " |")
    return "\n".join(out)


def markdown_evidence() -> str:
    out = ["| route | what has been shown | what is assumed here |", "|---|---|---|"]
    out += [f"| {n} | {shown} | {assumed} |" for n, (_a, shown, assumed) in routes().items()]
    return "\n".join(out)


def main() -> None:
    if "--markdown" in sys.argv:
        print("\n\n".join((markdown(), markdown_scenarios(), markdown_sensitivity(), markdown_evidence())))
        return
    s = summary()
    for key in KEYS:
        d = s[key]
        r0 = d["base"]
        print(f"\n{S.SCENARIOS[key].name}: ${r0['total']:.2f}, {r0['medium_l']:.1f} L/kg; terms "
              f"{ {k: round(v, 1) for k, v in r0['medium_terms'].items()} }; bleed {1000 / r0['density'] / r0['harvested_share']:.1f}")
        sb = d["sorbent"]
        print(f"   exchanger on the permeate, {sb['share'] * 100:.0f}%: ${sb['total']:.2f} (saves {sb['saving']:.2f}), {sb['fresh']:.1f} L fresh")
        for n, c in d["routes"].items():
            print(f"   {n[:70]:<70} ${c['total']:6.2f} (saves {c['saving']:+.2f}); fresh {c['fresh']:.1f}, loop {c['loop']:.1f}, "
                  f"filtered {c['filtered']:.1f}; pays under ${d['breakeven'][n]:.3f}/L; "
                  f"{ {k: round(v, 2) for k, v in c['extra'].items() if v} }")
        for lab, c in d["bounds"].items():
            print(f"   perfect and free, {lab}: ${c['total']:.2f} (saves {c['saving']:.2f}); fresh {c['fresh']:.1f}, loop {c['loop']:.1f}")


if __name__ == "__main__":
    main()
