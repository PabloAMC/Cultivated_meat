#!/usr/bin/env python3
"""test_medium_reuse.py — cleaning and reusing the medium (medium_reuse.py).

Checks the liquid balance, the point the study rests on (a device on the permeate cannot lower the litres through the cell
filter, in `medium_reuse` and in `explore`'s own sorbent lever), the ordering of the bounds, and that RESULTS.md and the note
carry the module's tables and the figures their prose quotes. Run directly or under pytest.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import floor_physics as fp  # noqa: E402
import medium_reuse as M  # noqa: E402


def check() -> list:
    fails = []
    s = M.summary()
    for key in M.KEYS:
        kw, r0 = M.base(key)
        d = s[key]
        bleed = 1000.0 / r0["density"] / r0["harvested_share"]   # litres per kilo harvested, as explore reports them
        none = M.cost(key, loop=0.0)
        if abs(none["total"] - r0["total"]) > 1e-9 or abs(none["fresh"] - r0["medium_l"]) > 1e-9:
            fails.append(f"{key}: no reuse should reproduce the scenario")
        filtered0 = r0["medium_l"] - bleed
        for n, (args, _a, _b) in M.routes().items():
            c = d["routes"][n]
            if c["total"] > r0["total"] + 1e-9:
                fails.append(f"{key}: {n} costs more than no reuse at its best litres")
            if c["fresh"] < min(bleed, r0["medium_l"]) - 1e-9:
                fails.append(f"{key}: {n} buys less medium than leaves with the cells")
            if not args.get("in_tank") and c["filtered"] < filtered0 - 1e-9:
                fails.append(f"{key}: {n} is on the permeate but lowers the litres through the cell filter")
        perm, tank = d["bounds"]["on the permeate"], d["bounds"]["across the culture"]
        if not tank["total"] <= perm["total"] <= r0["total"]:
            fails.append(f"{key}: the bounds are out of order")
        if abs(perm["filtered"] - filtered0) > 0.11:
            fails.append(f"{key}: a perfect device on the permeate should leave the filter's litres as they were")
        for n, c in d["routes"].items():
            if c["total"] < (tank if M.routes()[n][0].get("in_tank") else perm)["total"] - 1e-9:
                fails.append(f"{key}: {n} beats the perfect, free device")
        # explore's own sorbent lever: the permeate it cleans still passes the filter
        for share in (0.2, 0.5, 0.8):
            r = fp.explore(**{**kw, "sorbent": share})
            if r["membranes"] < r0["membranes"] * (1.0 - 1e-9) and r["medium_l"] >= bleed:
                fails.append(f"{key}: a sorbent taking {share:.0%} lowers the membrane cost")
    if abs(M.exchange_share() - 0.5) > 1e-9:
        fails.append("the exchange membrane's share of the filter's cost has moved; the route's name says 'twice'")

    # 2026-11-19 audit batch: the published cells' glucose comes from their own balance (4.5 mol a kilo at a lactate yield
    # of 1.05), so lactate, not ammonia, sets their litres (95.5, was 28). An ammonium exchanger then saves nothing, and a
    # route that takes lactate saves more than it does in the low-lactate example. Before, reuse was capped at $4.6 for these cells.
    names = list(M.routes())
    # 2026-11-19 restructure: rung 1 ("today") is a fed-batch with nothing to reuse; the published cells in perfusion are "cautious"
    # (the same switches as the old rung 1, with the added equipment for oxygen and CO₂ and the tank design chosen)
    t0, c0 = s["cautious"], s["central"]
    if t0["base"]["medium_set_by"] != "lactate" or c0["base"]["medium_set_by"] != "ammonia":
        fails.append("lactate should set the published cells' litres and ammonia the low-lactate example's")
    if t0["sorbent"]["saving"] > 1e-9:
        fails.append("an ammonium exchanger should save nothing where lactate sets the litres")
    if not t0["routes"][names[0]]["saving"] > c0["routes"][names[0]]["saving"] > 0:
        fails.append("electrodialysis should save more for the published cells than in the low-lactate example")
    if not t0["bounds"]["across the culture"]["saving"] > c0["bounds"]["across the culture"]["saving"]:
        fails.append("a perfect device should be worth more for the published cells than in the low-lactate example")
    # reuse does not replace better cells: the published cells with the best route modelled cost more than the low-lactate example with none
    if not min(c["total"] for c in t0["routes"].values()) > c0["base"]["total"]:
        fails.append("the published cells with the best route should still cost more than the low-lactate example with no device")
    # the order of the low-lactate example's routes. Until 2026-11-20 electrodialysis beat dialysis across the culture at the filter's
    # cost ($29.92 against $30.46) and the exchanger beat dialysis of the permeate with a cleaned dialysate ($31.06 against $31.74).
    # 2026-11-20 model batch: both reversed ($46.46 against $46.06; $49.16 against $47.78), a consequence of the batch and not a
    # defect. (1) The cells tolerate 35 mmol/L of lactate, not 50, so lactate asks for 35.2 of the 40.1 litres: an exchanger, which
    # takes ammonia alone, can cut 5 litres (it cut 13), and electrodialysis stops at the least flow (18.6 L) while the dialysis
    # routes, which take the other by-products too, reach 9.2. (2) A litre passed costs more (membrane $0.60 a litre filtered, was
    # $0.37; medium preparation capital with the litres), so the routes that cut the most litres gained the most.
    # Section 2 of the note is rewritten for the new order.
    if not (c0["routes"][names[3]]["total"] < c0["routes"][names[0]]["total"]
            and c0["routes"][names[2]]["total"] < c0["sorbent"]["total"] < c0["base"]["total"]):
        fails.append("the order of the low-lactate example's routes has changed; rewrite section 2 of the note")
    # the exchanger's best share stops where lactate takes over: its fresh litres are lactate's
    if abs(c0["sorbent"]["fresh"] - c0["base"]["medium_terms"]["lactate"]) > 0.15:
        fails.append("the exchanger's best share should leave the litres lactate asks for")
    # the table's ammonia row names the limit the scenarios use
    if f"| ammonia, held at {M.base('central')[0]['nh3_limit']:.0f} mmol/L |" not in M.markdown():
        fails.append("the ammonia row should name the scenarios' own limit (sc_nh3_limit)")

    c, p = s["central"], M.per_litre("central")
    ed, dp, dc, dh = (c["routes"][names[i]] for i in (0, 2, 3, 4))
    quoted = [f"${p['all']:.2f}", f"${p['filter']:.2f}", f"{p['removal_to_pay'] * 100:.0f}%",
              f"${c['sorbent']['saving']:.1f}", f"${ed['saving']:.1f}", f"${dp['saving']:.1f}", f"${dc['saving']:.1f}",
              f"${dh['saving']:.1f}", f"${c['bounds']['on the permeate']['saving']:.1f}",
              f"${c['bounds']['across the culture']['saving']:.1f}", f"${dh['total']:.2f}", f"${ed['total']:.2f}"]
    for name in ("RESULTS.md", os.path.join("research_notes", "medium_reuse.md")):
        text = open(os.path.join(ROOT, name), encoding="utf-8").read()
        tables = [M.markdown(), M.markdown_scenarios()] + ([M.markdown_sensitivity(), M.markdown_evidence()]
                                                           if name != "RESULTS.md" else [])
        for line in "\n".join(tables).splitlines():
            if line.strip() and line not in text:
                fails.append(f"{name} does not carry: {line[:90]}")
        for q in quoted:
            if q not in text:
                fails.append(f"{name} does not quote {q}")
    return fails


def main() -> None:
    fails = check()
    if fails:
        print("FAIL — medium reuse:")
        for f in fails:
            print("  " + f)
        sys.exit(1)
    print("PASS — the medium-reuse study holds.")


if __name__ == "__main__":
    main()
