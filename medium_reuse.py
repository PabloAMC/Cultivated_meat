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
`cost` prices a route for a scenario from `floor_physics.explore`, plus the loop's filter, the growth factors it loses, the
dialysate and the device. `best` picks the litres to clean that cost least. `routes()` are the candidates, each with its
evidence. Nothing here changes a default.

    python medium_reuse.py              # the tables, as text
    python medium_reuse.py --markdown   # the tables the note and RESULTS.md quote
"""
from __future__ import annotations

import sys

import floor_physics as fp
import scenarios as S
from inputs import value

KEYS = ("today", "central", "best")


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
    culture, its membrane and hardware as a share of what filtering the same litres through the cell filter costs."""
    gf_kept = value("mr_gf_kept") if gf_kept is None else gf_kept
    kw, r0 = base(key)
    bleed = 1000.0 / r0["density"]
    b = balance(r0["medium_terms"], bleed, loop, nh3, lac, other, in_tank)
    r = fp.explore(**{**kw, "medium_l": b["fresh"]})
    perm0 = max(1e-9, r0["medium_l"] - bleed)
    charge = kw.get("charge", value("plant_charge_mature"))
    filter_l = r0["membranes"] / perm0 + charge * r0["retention_capex"] / r0["output"] / perm0   # $ per litre filtered
    # growth factors per litre, whether bought on top or inside a complete medium's price (scenarios.explore_kwargs)
    gf_l = (value("pf_growth_factors") * value("pf_opex_escalation") / fp.washout_litres(fp.GOOD_CELLS)
            * (kw.get("growth_factors", 0.0) + kw.get("gf_in_medium", 0.0)))
    # basal medium for the dialysate: the medium's price without its growth factors, and never below the nutrients a litre carries
    basal_l = max(kw.get("medium_price", 0.15) - (gf_l if kw.get("gf_in_medium", 0.0) else 0.0),
                  fp.feedstock(fp.GOOD_CELLS) / r0["medium_l"])
    extra = {"filter for the loop": 0.0 if in_tank else loop * filter_l,
             "exchange membrane": loop * filter_l * exchange_membrane if in_tank else 0.0,
             "growth factors lost": loop * (1.0 - gf_kept) * gf_l,
             "dialysate": loop * dialysate_l * basal_l,
             "device": loop * device_l}
    total = r["total"] + sum(extra.values())
    return {**b, "total": total, "saving": r0["total"] - total, "base": r0["total"], "extra": extra, "filter_l": filter_l,
            "bleed": bleed, "parts": {k: r[k] for k in ("feedstock", "growth_factors", "protectant", "membranes")}}


def per_litre(key: str = "central") -> dict:
    """What a litre of medium that leaves the tank costs, by part, $ per litre: the medium itself, its growth factors, its
    bubble protectant, and filtering it. `removal_to_pay`: the share of the waste a free device on the permeate must take in
    one pass before it saves anything (each litre cleaned is filtered once and stands in for that share of a litre)."""
    hi, lo = cost(key, loop=0.0), None
    kw, r0 = base(key)
    lo = fp.explore(**{**kw, "medium_l": r0["medium_l"] - 1.0})
    parts = {k: r0[k] - lo[k] for k in ("feedstock", "growth_factors", "protectant")}
    parts["filter"] = hi["filter_l"]
    parts["all"] = sum(parts.values())
    parts["removal_to_pay"] = parts["filter"] / parts["all"]
    return parts


def best(key: str = "central", **args) -> dict:
    """The route at the litres cleaned that cost least (none, if it never pays). The cost is piecewise linear in the litres,
    so a grid of 0.1 L/kg is exact enough."""
    t = base(key)[1]["medium_terms"]
    shares = [args.get(k, 0.0) for k in ("nh3", "lac", "other")]
    top = max(t[n] / s for n, s in zip(("ammonia", "lactate", "least flow"), shares) if s > 0)
    return min((cost(key, loop=i * 0.1, **args) for i in range(int(top * 10) + 2)), key=lambda c: c["total"])


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
             "the cost per litre is my arithmetic; 90% of growth factors survive a pass; the other by-products stay"),
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


def sorbent_best(key: str = "central") -> dict:
    """The ammonium exchanger on the permeate (explore's own `sorbent` lever), at the share that costs least."""
    kw, r0 = base(key)
    bleed = 1000.0 / r0["density"]                    # fresh medium cannot fall below the liquid that leaves with the cells
    runs = {s: fp.explore(**{**kw, "sorbent": s / 100.0}) for s in range(0, 91)}
    share = min((s for s, r in runs.items() if r["medium_l"] >= min(bleed, r0["medium_l"]) - 1e-9),
                key=lambda s: runs[s]["total"]) / 100.0
    r = runs[round(share * 100)]
    loop = share * r0["medium_terms"]["ammonia"]
    return {"share": share, "total": r["total"], "saving": r0["total"] - r["total"], "fresh": r["medium_l"], "loop": loop,
            "filtered": r["medium_l"] - 1000.0 / r0["density"] + loop, "base": r0["total"]}


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
    bleed = 1000.0 / r0["density"]
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
              f"{ {k: round(v, 1) for k, v in r0['medium_terms'].items()} }; bleed {1000 / r0['density']:.1f}")
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
