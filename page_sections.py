"""
page_sections.py — the parts of interactive.html that are computed from the scenarios (scenarios.py).

Every figure in these tables comes from the model at build time; nothing is typed in. The page's JavaScript
(page_scenarios.js) recomputes the same numbers live when a switch moves.
"""
from __future__ import annotations

import html as _html

import contamination
import scenarios as S
from inputs import value, prior

_esc = _html.escape
_CACHE: dict = {}


def bands(key: str) -> dict:
    """10th / 50th / 90th percentile of the cost and of the world's long-run share, for a scenario (cached)."""
    if key not in _CACHE:
        _CACHE[key] = S.bands(S.SCENARIOS[key].choice)
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
        tr = S.tricks_report(sc.choice)
        trick_html = ""
        if tr["used"]:
            trick_html = (f"<p class='fxn tricks'><b>Nobody has run this tank design with animal cells.</b> It uses {_esc(S.plain_list(tr['used']))}. "
                          f"Without these tricks, a kilo costs <b>{money(tr['no_tricks'])}</b> in a tank of the same shape ({money(tr['d_no_tricks'])} more). "
                          f"In the ordinary tall tank, it costs <b>{money(tr['ordinary_tank'])}</b>.</p>")
        rows.append(
            f"<tr data-sc='{key}'><td class='scname'><b>{_esc(sc.name)}</b><br><span class='story'>{_esc(S.story_text(key))}</span><br>"
            f"<button class='btn scbtn small' onclick=\"scApply('{key}');location.hash='decide';return false\">Use these assumptions</button></td>"
            f"<td>{chip(S.hardest_need(sc.choice))}{trick_html}<details class='scdet'><summary>All ten assumptions</summary><ul>{items}</ul>"
            f"<p class='fxn'><b>Rule:</b> {_esc(sc.rule)}</p></details></td>"
            f"<td class='n'><b>{money(sm['cost'])}</b><br><span class='alt'>{money(b['cost'][0])}–{money(b['cost'][2])} "
            f"(10th–90th percentile of the estimates behind it)</span>{alts}</td>"
            f"<td class='n'>{money(sm['retail'], 0)}<br><span class='alt'>{sm['ratio']:.2f}× everyday meat</span></td>"
            f"<td class='n'><b>{b['share'][1]:.1f}%</b><br><span class='alt'>The median. 80% of draws fall between {b['share'][0]:.1f}% and "
            f"{b['share'][2]:.1f}%, with cost and demand both uncertain. At the point cost the share is {sm['world']:.1f}% "
            f"(US {sm['us']:.1f}%, Europe {sm['eu']:.1f}%).</span></td>"
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
        f"<td class='n'><b>{rs['world']:.1f}%</b><br><span class='alt'>point estimate; US {rs['us']:.1f}%, Europe {rs['eu']:.1f}%</span></td>"
        f"<td class='s'>{_esc(limit_text(ref))}</td></tr>")
    rows.append(
        f"<tr data-sc='reported'><td class='scname'><b>As a company reports</b><br><span class='story'>SuperMeat's 2024 process: chicken "
        f"cells in perfusion, scaled up on paper to 25,000-litre tanks, 30.5 litres of medium a kilo at $0.50 a litre, plus the "
        f"company's running costs and a yearly charge on its plant. A company's figure, not peer reviewed.</span><br>"
        f"<button class='btn scbtn small' onclick=\"scApply('reported');return false\">Use this in the charts</button></td>"
        f"<td><span class='tagchip none'>a company's own report</span></td>"
        f"<td class='n'><b>{money(rp['cost'])}</b></td><td class='n'>{money(rp['retail'], 0)}<br><span class='alt'>{rp['ratio']:.2f}×</span></td>"
        f"<td class='n'><b>{rp['world']:.1f}%</b><br><span class='alt'>point estimate; US {rp['us']:.1f}%, Europe {rp['eu']:.1f}%</span></td>"
        f"<td class='s'>30.5 litres of medium per kilo at $0.50 a litre; the company reports no tank limit.</td></tr>")
    head = ("<thead><tr><th>Scenario: what has to go right</th><th>What it needs</th><th>Cost of a kilo of cells</th>"
            "<th>In the shop</th><th>Share of world meat, long run (median)</th><th>What limits the tank</th></tr></thead>")
    labels = ("", "What it needs", "Cost of a kilo of cells", "In the shop", "Share of world meat, long run", "What limits the tank")

    def label_row(row: str) -> str:                    # the phone layout stacks each row and prints these in front of each cell
        out, k = [], 0
        for part in row.split("<td")[1:]:
            out.append(f"<td data-label='{labels[k]}'" + part if labels[k] else "<td" + part)
            k += 1
        return row.split("<td")[0] + "".join(out)

    rows = [label_row(r) for r in rows]
    return f"<div class='scrollx'><table class='sctab stack'>{head}<tbody>{''.join(rows)}</tbody></table></div>"


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


# ----------------------------------------------------------------------------
# Vessel types and operating modes (vessels.py): one table, vessel rows, mode columns; page_vessels.js redraws it
# ----------------------------------------------------------------------------
def _vm_money(x: float) -> str:
    return f"${x:,.0f}" if x >= 1000 else f"${x:.2f}"


def _vm_tag(t: str) -> str:
    import vessels as V
    cls = {V.TODAY: "vt-today", V.PILOT: "vt-pilot", V.PAPER: "vt-paper"}[t]
    return f"<span class='vtag {cls}'>{_esc(t)}</span>"


def _vm_size(m3: float) -> str:
    if m3 >= 1:
        return f"{m3:.0f} m³ a unit"
    return f"{m3 * 1000:.0f} litres a unit" if m3 * 1000 >= 1 else f"{m3 * 1e6:.0f} mL a unit"


def vessel_grid_html(base: dict | None) -> str:
    """The table for one case (explore arguments; {} = the reference case). The same markup as page_vessels.js."""
    import vessels as V
    g = V.grid(base)
    head = ("<thead><tr><th>Vessel ↓ &nbsp; How it is run →</th>" + "".join(
        f"<th>{_esc(V.MODES[m]['name'])}<br><span class='alt'>{_esc(V.MODES[m]['what'])}</span></th>" for m in V.MODE_ORDER)
        + "</tr></thead>")
    rows = []
    for v in V.VESSEL_ORDER:
        vv = V.VESSELS[v]
        cells = []
        for m in V.MODE_ORDER:
            c = g[(v, m)]
            if not c["possible"]:
                cells.append(f"<td class='vno'><b>Not possible</b><br><span class='alt'>{_esc(c['reason'])}</span></td>")
            elif c["same_as"]:
                cells.append(f"<td class='vsame'><b>As batch</b><br><span class='alt'>{_esc(V.SAME_AS[(v, m)][1])}</span></td>")
            else:
                lim = V.LIMIT_PLAIN.get(c["limit"], c["limit"])
                extra = ""
                if c["tricks_fallback"]:
                    extra = (f"<br><span class='alt'>The tank tricks’ loop fails its pH check in this vessel, so these are with "
                             f"“{_esc(c['tricks_fallback'])}”; with the tricks it would be {_vm_money(c['unchecked_cost'])}.</span>")
                cells.append(f"<td title=\"{_esc(c['evidence'])}\"><b>{_vm_money(c['cost'])}</b><br><span class='alt'>"
                             f"{c['density']:.0f} g/L, limited by {_esc(lim)}; biggest cost: {_esc(c['biggest'])}</span><br>"
                             f"{_vm_tag(c['tag'])}{extra}</td>")
        rows.append(f"<tr><th>{_esc(vv['name'])}<br><span class='alt'>{_vm_size(vv['size'])}. {_esc(vv['what'])}</span></th>"
                    + "".join(cells) + "</tr>")
    return f"<div class='scrollx'><table class='sctab vmtab'>{head}<tbody>{''.join(rows)}</tbody></table></div>"


def vessel_facts() -> dict:
    """The numbers the text around the table quotes (reference case and central scenario)."""
    import vessels as V
    st = V.settings()
    ref, cen = V.grid(st["reference"]), V.grid(st["central"])
    possible = lambda g: [c["cost"] for c in g.values() if c["possible"]]
    return {"ref": ref, "cen": cen, "bed": V.what_if_bed(st["reference"])["total"],
            "bed_c": V.what_if_bed(st["central"])["total"], "ref_min": min(possible(ref)), "cen_min": min(possible(cen))}


def vessels() -> str:
    """The vessel-by-mode section: a reading guide, the table (for the scenario chosen in the switches, or the reference
    case), what each vessel's limits are, and a plain takeaway. Every figure is computed."""
    import vessels as V
    f = vessel_facts()
    R, C = f["ref"], f["cen"]
    m = _vm_money
    S_ = ("stirred", "perfusion")
    guide = ("<p class='blkp'>Each cell is the cost of a kilo of cells when only the vessel (the row) and the way it is run (the "
             "column) change, with the cells, plant, tank tricks and losses of <b id='vm_case'>the central scenario</b> held fixed.</p>"
             "<p class='blkp'><button class='btn small vmbtn on' data-vm='scenario' onclick=\"vmSet('scenario');return false\">"
             "The scenario chosen above</button> <button class='btn small vmbtn' data-vm='reference' onclick=\"vmSet('reference');"
             "return false\">The reference case</button></p>")
    lim_rows = "".join(f"<li><b>{_esc(V.VESSELS[v]['name'])}</b> ({_vm_size(V.VESSELS[v]['size'])}): {_esc(V.VESSELS[v]['limits'])}</li>"
                       for v in V.VESSEL_ORDER)
    take = (
        f"<p class='fnote'><b>What the table says.</b> Perfusion in a stirred tank is the cheapest combination: "
        f"{m(R[S_]['cost'])} a kilo in the reference case and {m(C[S_]['cost'])} in the central scenario. Nobody has run animal "
        f"cells in perfusion above about {value('vm_perf_max_m3'):.0f} m³. The modes that run at 20 m³ today cost more. In the reference case a fed-batch "
        f"stirred tank costs {m(R[('stirred', 'fedbatch')]['cost'])} and fill-and-draw {m(R[('stirred', 'filldraw')]['cost'])}. "
        f"In the central scenario they cost {m(C[('stirred', 'fedbatch')]['cost'])} and {m(C[('stirred', 'filldraw')]['cost'])}, "
        f"because cells that make more waste cap a culture that is not washed out at a lower density. "
        f"A chemostat costs more than fill-and-draw ({m(R[('stirred', 'chemostat')]['cost'])} in the reference case), because it "
        f"must run below the cells' top growth rate. Batch costs most of the stirred-tank modes "
        f"({m(R[('stirred', 'batch')]['cost'])}), because one fill of medium feeds only a thin culture.</p>"
        f"<p class='fnote'>An airlift costs about what a stirred tank costs when the culture is not washed out. In perfusion it "
        f"costs more ({m(R[('airlift', 'perfusion')]['cost'])} in the reference case), because its tall shape passes less gas per litre "
        f"and clears less CO₂. A single-use bag needs a new bag every run. That makes it close to a stirred tank only in perfusion "
        f"({m(R[('bag', 'perfusion')]['cost'])}), where a run lasts a month. Packed beds and hollow fibres exist only as small units, "
        f"so they cost {m(R[('packed', 'perfusion')]['cost'])} and {m(R[('hollow', 'perfusion')]['cost'])} a kilo in the reference "
        f"case. Even a 20 m³ bed priced like a stirred tank, with carriers that cost nothing, would cost {m(f['bed'])}: the bed is "
        f"seeded thin and emptied every run, so it makes a fraction of a perfusion tank's output.</p>")
    legend = ("<p class='fnote'>Under each cost: how dense the culture gets, what limits it, and the largest item of cost. The tag says "
              "whether anyone has grown animal cells this way at this size, for any product: "
              f"{_vm_tag(V.TODAY)} {_vm_tag(V.PILOT)} {_vm_tag(V.PAPER)}. Only Vow's stirred tank grows cells for food at 20 m³.</p>")
    ev = "".join(f"<li><b>{_esc(V.VESSELS[v]['name'])}, {_esc(V.MODES[m]['name'].lower())}:</b> {_esc(V.TAGS[(v, m)][1])}</li>"
                 for v in V.VESSEL_ORDER for m in V.MODE_ORDER if V.TAGS[(v, m)][1] and (v, m) not in V.SAME_AS)
    return (guide + f"<div id='vm_grid'>{vessel_grid_html(V.settings()['central'])}</div>" + legend + take +
            f"<details class='scdet'><summary>The evidence behind each tag</summary><ul>{ev}</ul></details>" +
            f"<details class='scdet'><summary>What limits each vessel</summary><ul>{lim_rows}</ul><p class='fxn'>Perfusion assumes "
            f"a device that holds the cells back at the price one design study hopes for (${value('pf_capex_retention'):.0f}k per m³ of "
            f"tank; the filters pharma uses would cost about ${prior('pf_capex_retention')[2]:.0f}k). Batch and fed-batch run "
            f"{value('pf_fedbatch_doublings'):.0f} doublings a cycle from a seed, plus {value('pf_turnaround_h'):.0f} hours to clean and refill "
            f"(Humbird's design). A lost cycle costs the cycle and {value('vm_restart_cycle_days'):.0f} more days. Each vessel is priced at "
            f"the largest unit built for animal cells, up to {value('vm_str_m3'):.0f} m³. Evidence and sources: research_notes/vessels_and_modes.md.</p></details>")


# ----------------------------------------------------------------------------
# Evidence: the back-test, what has and has not been measured, what would move the scenarios
# ----------------------------------------------------------------------------
def backtest_table() -> str:
    import floor_physics as fp
    rows = []
    for run_, what, obs, mod, note in fp.backtest():
        rows.append(f"<tr><td>{_esc(run_)}</td><td>{_esc(what)}</td><td class='n'>{obs:.1f}</td><td class='n'>{mod:.1f}</td>"
                    f"<td class='n'>{obs / mod:.2f}×</td><td class='s'>{_esc(note)}</td></tr>")
    return ("<div class='scrollx'><table class='sctab'><thead><tr><th>Reported run</th><th>Quantity</th><th>Observed</th><th>Model</th>"
            "<th>Observed / model</th><th>Note</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>")


def experiments() -> str:
    """What one measurement would be worth to the central scenario: the cost if a switch moved to the setting the measurement would show."""
    c0 = S.SCENARIOS["central"].choice
    base = S.run(c0)["total"]
    base_sh = S.shares(base)["global"]
    plan = (
        ("A culture of low-waste meat cells that doubles every 24 hours in a stirred tank", {"growth": "24"},
         "the combination has never been shown; the central case takes 36 hours"),
        ("Cells that need no growth factors, or that make their own, at scale", {"gf": "none"},
         "shown in cattle cells by genetic engineering; the central case buys 30% of Humbird's price"),
        ("Medium at $0.15 a litre, verified on a stated mass basis", {"medium": "0.15"},
         "companies announced $0.20; none verified at scale"),
        ("A lean plant built and run for animal cells", {"plant": "lean"}, "nobody has built one"),
        ("A column, pressure and recycled oxygen turn out not to work with dense meat cells", {"tricks": "none"},
         "calculated, never tried with meat cells; the central case counts all three"),
        ("Loss rates of 0.2% a day in a food-grade tank at 20,000 litres", {"losses": "0.2"},
         "the survey of makers implies 0.6 to 2.2% a day if runs last 10 to 20 days; run lengths are not stated"),
        ("The gas flow dense meat cells tolerate at this size", {"gas": "6"}, "6 mm/s has never been run with dense cells; 2 mm/s is the most that has"),
    )
    rows = []
    for text, ch, why in plan:
        r = S.run({**c0, **ch})["total"]
        d = r - base
        sh = S.shares(r)["global"] - base_sh
        rows.append(f"<tr><td>{_esc(text)}</td><td class='n'><b>{'−' if d < 0 else '+'}{money(abs(d))}</b> a kilo<br><span class='alt'>{sh:+.1f} points of world share</span></td>"
                    f"<td class='s'>{_esc(why[0].upper() + why[1:])}.</td></tr>")
    return (f"<p class='blkp'>One measurement at a time. The central scenario costs {money(base)} a kilo and has a point-estimate share of {base_sh:.1f}% of world meat "
            "(the table at the top gives the median). Each row shows what the scenario would cost if that measurement came out as the row says. "
            "The measurement comes out in its favour, except where the row says it fails. These are the same switches as in “What decides it”, "
            "so the figures are computed, not estimated by hand.</p><div class='scrollx'><table class='sctab'><thead><tr><th>The measurement</th>"
            "<th>Worth to the central scenario if it comes out this way</th><th>What is known now</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>")


def measured() -> str:
    """Two lists: what has been measured and what has not (the evidence behind the scenarios), each a sentence."""
    done = [
        "Perfusion at 100 to 214 million cells per millilitre at bench scale (CHO in a wave bag, Clincke 2013; chicken, SuperMeat 2024; Pasitka 2024).",
        "Ammonia made by meat cells with and without glutamine (bovine, Hubalek 2023): 0.70 mol per kilo with, under 0.14 without; doubling 26 hours and 43 to 54.",
        "A 20,000-litre food-grade stirred tank growing animal cells, drained and refilled, with no clean room (Vow; company reports).",
        "Contamination losses across makers: 11.2% of batches (19.5% beyond flasks), with run lengths not stated (Powell 2025).",
        "Gas flow in 8 to 20 cubic-metre tanks with animal cells: 0.1 to 2 mm a second (Nienow 2006).",
    ]
    todo = [
        "Anything with dense meat cells in a tank above about 25 cubic metres.",
        "Meat cells that make this little waste and still double in 24 to 30 hours.",
        "CO₂ tolerance of muscle or fish cells; how much gas and foam dense cultures stand at 20 cubic metres.",
        "A pumped column, extra pressure or recycled oxygen with meat cells.",
        "A way to hold cells back at 20 cubic metres, and a lean plant's real cost.",
        "Medium at $0.20 a litre and growth factors at scale, on a stated mass basis.",
    ]
    li = lambda xs: "".join(f"<li>{_esc(x)}</li>" for x in xs)
    return (f"<div class='scpair'><div><h4>Has been measured</h4><ul>{li(done)}</ul></div><div><h4>Has not been measured</h4><ul>{li(todo)}</ul></div></div>")
