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
        bleed = 1000.0 / r0["density"]
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

    c, p = s["central"], M.per_litre("central")
    names = list(M.routes())
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
