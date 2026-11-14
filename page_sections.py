"""
page_sections.py — the parts of interactive.html that are computed from the scenarios (scenarios.py).

Every figure in these tables comes from the model at build time; nothing is typed in. The page's JavaScript
(page_scenarios.js) recomputes the same numbers live when a switch moves.
"""
from __future__ import annotations

import html as _html

import contamination
import scenarios as S
from inputs import value

_esc = _html.escape
_CACHE: dict = {}


def bands(key: str) -> dict:
    """10th / 50th / 90th percentile of the cost and of the world's long-run share, for a scenario (cached)."""
    if key not in _CACHE:
        _CACHE[key] = S.bands(S.SCENARIOS[key].choice, n=1000)
    return _CACHE[key]


def chip(tag: str) -> str:
    cls = {S.GE: "ge", S.SELECT: "sel", S.FEED: "feed", S.NOTHING: "none"}[tag]
    return f"<span class='tagchip {cls}'>{_esc(S.TAG_PLAIN[tag])}</span>"


def money(v: float, d: int = 1) -> str:
    return f"${v:.{d}f}"


def limit_text(r: dict) -> str:
    lim = S.LIMIT_PLAIN.get(r["limit"], r["limit"])
    med = S.MEDIUM_PLAIN.get(r["medium_set_by"], r["medium_set_by"])
    return (f"The tank holds {r['density']:.0f} g of cells a litre, limited by {lim}. Each kilo needs "
            f"{r['medium_l']:.0f} litres of medium, set by {med}.")


def scenario_table() -> str:
    """The answer: one row per scenario (cost, shop price, share, what must go right), the reference and the reported process."""
    rows = []
    for key in S.ORDER:
        sc = S.SCENARIOS[key]
        r = S.run(sc.choice)
        sm = S.summary(sc.choice, r)
        b = bands(key)
        alts = "".join(f"<br><span class='alt'>{lab}: {money(S.alt_cost(key, ch))}</span>" for lab, ch in sc.alt)
        need = S.needs(sc.choice)
        items = "".join(f"<li>{_esc(n)}: {_esc(lab)} <i>({_esc(t)})</i></li>" for n, lab, t in need)
        rows.append(
            f"<tr data-sc='{key}'><td class='scname'><b>{_esc(sc.name)}</b><br><span class='story'>{_esc(sc.story)}</span><br>"
            f"<button class='btn scbtn small' onclick=\"scApply('{key}');location.hash='decide';return false\">Use these assumptions</button></td>"
            f"<td>{chip(S.hardest_need(sc.choice))}<details class='scdet'><summary>All ten assumptions</summary><ul>{items}</ul>"
            f"<p class='fxn'><b>Rule:</b> {_esc(sc.rule)}</p></details></td>"
            f"<td class='n'><b>{money(sm['cost'])}</b><br><span class='alt'>{money(b['cost'][0])}–{money(b['cost'][2])} "
            f"(10th–90th percentile of the estimates behind it)</span>{alts}</td>"
            f"<td class='n'>{money(sm['retail'], 0)}<br><span class='alt'>{sm['ratio']:.2f}× everyday meat</span></td>"
            f"<td class='n'><b>{sm['world']:.1f}%</b><br><span class='alt'>{b['share'][0]:.1f}–{b['share'][2]:.1f}% with "
            f"demand uncertain too; US {sm['us']:.1f}%, Europe {sm['eu']:.1f}%</span></td>"
            f"<td class='s'>{_esc(limit_text(r))}</td></tr>")
    ref = S.reference()
    rs = S.summary(r=ref)
    rep = S.reported_cost()
    rp = S.summary(cost=rep, r={"density": float("nan"), "limit": "", "medium_l": value("media_intensity"),
                                "medium_set_by": "", "uptime": float("nan"), "output": float("nan")})
    rows.append(
        f"<tr class='ref'><td class='scname'><b>Reference: a standard perfusion tank, no tricks</b><br><span class='story'>"
        f"What earlier versions of this page called the floor. Humbird's 20,000-litre stirred tank run in perfusion at "
        f"120 g/L, a sterile plant, engineered cells, no tank tricks, no growth factors, no lost runs. Kept as a labelled "
        f"reference, not as a limit: the best case is below it.</span></td><td>{chip(S.GE)}</td>"
        f"<td class='n'><b>{money(rs['cost'])}</b></td><td class='n'>{money(rs['retail'], 0)}<br><span class='alt'>{rs['ratio']:.2f}×</span></td>"
        f"<td class='n'><b>{rs['world']:.1f}%</b><br><span class='alt'>US {rs['us']:.1f}%, Europe {rs['eu']:.1f}%</span></td>"
        f"<td class='s'>{_esc(limit_text(ref))}</td></tr>")
    rows.append(
        f"<tr data-sc='reported'><td class='scname'><b>As a company reports</b><br><span class='story'>SuperMeat's 2024 process: chicken "
        f"cells in perfusion, scaled up on paper to 25,000-litre tanks, 30.5 litres of medium a kilo at $0.50 a litre, plus the "
        f"company's running costs and a yearly charge on its plant. A company's figure, not peer reviewed.</span><br>"
        f"<button class='btn scbtn small' onclick=\"scApply('reported');return false\">Use this in the charts</button></td>"
        f"<td><span class='tagchip none'>a company's own report</span></td>"
        f"<td class='n'><b>{money(rp['cost'])}</b></td><td class='n'>{money(rp['retail'], 0)}<br><span class='alt'>{rp['ratio']:.2f}×</span></td>"
        f"<td class='n'><b>{rp['world']:.1f}%</b><br><span class='alt'>US {rp['us']:.1f}%, Europe {rp['eu']:.1f}%</span></td>"
        f"<td class='s'>30.5 litres of medium per kilo at $0.50 a litre; the company reports no tank limit.</td></tr>")
    head = ("<thead><tr><th>Scenario: what has to go right</th><th>What it needs</th><th>Cost of a kilo of cells</th>"
            "<th>In the shop</th><th>Share of world meat, long run</th><th>What limits the tank</th></tr></thead>")
    return f"<div class='scrollx'><table class='sctab'>{head}<tbody>{''.join(rows)}</tbody></table></div>"


# What stands in the way: each switch of the central scenario moved to a worse setting, with what it would take to meet it.
# (switch, headline, central assumes, [(label, change)], how it could be met, how solid)
def bottlenecks() -> str:
    c0 = S.SCENARIOS["central"].choice
    r0 = S.run(c0)
    base = r0["total"]
    ordinary = S.run({**c0, "cells": "ordinary"})
    be = 1.0 / contamination.breakeven_hazard("lean")

    def cost(change: dict) -> str:
        return money(S.run({**c0, **change})["total"])

    rows = [
        ("Waste the cells make",
         "Ammonia and lactate are what cells give off as they grow; they slow growth, so fresh medium must wash them out. The "
         f"central case assumes a low-waste feed and selected cells (0.14 mol of ammonia per kilo of cells, {r0['medium_l']:.0f} litres of medium a kilo).",
         f"{cost({'cells': 'measured'})} with the best meat cells measured (more lactate); {cost({'cells': 'ordinary'})} with ordinary "
         f"meat cells ({ordinary['medium_l']:.0f} litres of medium a kilo)",
         "Replace glutamine in the feed; select or adapt cells that waste less; engineer them (the best case, "
         f"{cost({'cells': 'engineered'})}); or take the ammonium out of the used medium",
         "The feed change was measured once, in cattle cells. The engineered level has been seen only in pharma cells."),
        ("Clearing CO₂ from a dense tank",
         "Cells give off CO₂, which leaves a tank only in the gas bubbled through it. The central case uses a column beside the "
         "tank that strips CO₂ without bubbles (a pumped loop over a packed tower), pressure and recycled oxygen.",
         f"{cost({'tricks': 'none'})} with none of these tank tricks; {cost({'gas': '2'})} if the cells tolerate only 2 mm of gas a second",
         "The column, extra pressure and recycled oxygen are sized by calculation; a squat tank also helps",
         "Calculated. Nobody has run animal cells over such a column, and 4 mm a second is untested at this size."),
        ("The cost of the plant",
         "A sterile plant without clean rooms.",
         f"{cost({'plant': 'pharma'})} if it must be built like a pharma plant",
         f"Leave out what animal cells do not need (a clean-room hall, an owned oxygen plant, spare seed tanks): {cost({'plant': 'lean'})}. "
         "A plant as cheap as a yeast plant is not counted: nothing shows animal cells can be grown that way",
         f"Nobody has built a lean plant for animal cells. It pays only while a tank loses a run less often than about once in "
         f"{be:.0f} days; the one survey of makers implies more losses, from small vessels."),
        ("Fast growth and low waste together",
         "Cells that double every 36 hours while making little waste.",
         f"{cost({'growth': '43'})} at 43 hours, the pace of the best low-waste culture measured; {cost({'growth': '24'})} at 24 hours",
         "Select faster lines on the low-waste feed",
         "Each has been shown alone, never both in one culture."),
        ("Runs lost to contamination",
         f"A run is lost {value('sc_hazard_cm') * 100:.0f}% of days; the tank is out for {value('sc_restart_base'):.0f} days.",
         f"{cost({'losses': '2', 'restart': '30'})} at 2% a day with a month to restart; {cost({'losses': '0.2'})} at pharma's 0.2%",
         "Sealed, steam-sterilised tanks, tested seed trains, strict hygiene",
         "One survey of makers; run lengths were not stated."),
        ("Growth factors",
         "Proteins that tell cells to grow. The central case buys 30% of Humbird's price per litre.",
         f"{cost({'gf': 'all'})} if all are bought at his price",
         f"Cheaper factors, lines that need fewer, or cells that make their own ({cost({'gf': 'none'})} with none bought)",
         "Cells that make their own have been shown in cattle cells, by genetic engineering."),
        ("Price of the medium",
         "$0.20 a litre, what several companies announced for 2025.",
         f"{cost({'medium': '0.50'})} at $0.50 a litre, what SuperMeat reports",
         "Cheaper amino acids and recycled medium",
         "Company announcements; none verified at scale."),
    ]
    h = ["<table><thead><tr><th>What stands in the way</th><th>The central case assumes</th><th>If that fails</th>"
         "<th>How it could be met</th><th>How solid</th></tr></thead><tbody>"]
    for name, assumes, fail, met, solid in rows:
        h.append(f"<tr><td><b>{name}</b></td><td>{assumes}</td><td>{fail}</td><td>{met}</td><td>{solid}</td></tr>")
    h.append("</tbody></table>")
    return (f"<p class='blkp'>Starting from the central case ({money(base)} a kilo), each row moves one assumption to a worse "
            "setting and leaves the rest, so the cost shown is what that one failure adds. All figures are dollars per kilo of "
            "wet cells.</p><div class='scrollx'>" + "".join(h) + "</div>")


# the cells x tank grid: each cell a case, with the limit that binds, in plain words
_GRID_CELLS = (("engineered", "24", "Engineered cells (24 h doubling)"),
               ("selected", "36", "Selected cells on a low-waste feed (36 h)"),
               ("measured", "43", "The best meat cells measured (43 h)"),
               ("ordinary", "30", "Ordinary meat cells (about 26 h measured; 30 h used)"))
_GRID_TANKS = (("none", "Gas bubbled in only", "the standard tank"),
               ("column", "With a column", "a pumped loop strips CO₂"),
               ("oxygen", "Column, pressure and recycled oxygen", "all three tank tricks"))


def cells_by_tank() -> str:
    """Cost per kilo of cells for every kind of cell in every tank, central settings otherwise; each figure is a case
    that loads into the switches."""
    c0 = S.SCENARIOS["central"].choice
    h = ["<thead><tr><th>Cells ↓ &nbsp; Tank →</th>" + "".join(f"<th>{t}<br><span class='alt'>{d}</span></th>" for _k, t, d in _GRID_TANKS) + "</tr></thead><tbody>"]
    for ck, gk, clab in _GRID_CELLS:
        h.append(f"<tr><th>{clab}</th>")
        for tk, _t, _d in _GRID_TANKS:
            shape = "flat" if tk != "none" else "tall"
            cs = {**c0, "cells": ck, "growth": gk, "tricks": tk, "shape": shape}
            r = S.run(cs)
            lean = S.run({**cs, "plant": "lean"})
            lim = S.LIMIT_PLAIN.get(r["limit"], r["limit"])
            h.append(f"<td onclick=\"scApplyChoice({{cells:'{ck}',growth:'{gk}',tricks:'{tk}',shape:'{shape}'}})\" class='gcell'>"
                     f"<b>{money(r['total'])}</b> <span class='alt'>({money(lean['total'])} in a lean plant)</span><br>"
                     f"<span class='alt'>{r['density']:.0f} g/L, limited by {_esc(lim)}</span></td>")
        h.append("</tr>")
    h.append("</tbody>")
    return ("<p class='blkp'><b>Cells against tank.</b> Cost per kilo of cells for each kind of cell in each kind of tank, in a "
            "sterile plant (the lean plant in brackets), everything else as in the central case. Click a figure to load it into the switches.</p>"
            f"<div class='scrollx'><table class='sctab grid2'>{''.join(h)}</table></div>"
            "<p class='fnote'>The tank tricks help most when the cells are good: with ordinary meat cells, medium washing waste "
            "out sets most of the cost and no tank trick reaches it.</p>")
