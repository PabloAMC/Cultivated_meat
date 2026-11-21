"""
page_sections.py — the parts of interactive.html that are computed from the model at build time: the scenarios' bands,
the rows and columns of the cells-by-tank table, the vessel-by-mode table, the back-test against reported runs and
the model beside company cost claims.

Every figure in these tables comes from the model at build time; nothing is typed in. The page's JavaScript
(page_scenarios.js, page_vessels.js) recomputes the same numbers live when a setting moves.
"""
from __future__ import annotations

import html as _html

import scenarios as S

_esc = _html.escape
_CACHE: dict = {}


def bands(key: str) -> dict:
    """10th / 50th / 90th percentile of the cost and of the world's long-run share, for a scenario (cached)."""
    if key not in _CACHE:
        _CACHE[key] = S.bands(S.SCENARIOS[key].choice, eqs=S.eqs_of(key))
    return _CACHE[key]


def money(v: float, d: int = 1) -> str:
    return f"${v:.{d}f}"


# the cells x tank grid (build_interactive._cells_by_tank_html): each row is a set of cell traits (the switch's internal key, the
# doubling time, and a note after the traits, which the table writes out from scenarios.cell_traits)
_GRID_CELLS = (("engineered", "24", ""),
               ("selected", "36", ""),
               ("measured", "43", "the best measured in meat cells"),
               ("ordinary", "30", "meat cells fed glutamine, which double in 26 h"))
_GRID_TANKS = (("none", "Gas bubbled in only", "the standard tank"),
               ("column", "With a column", "a pumped loop strips CO₂"),
               ("oxygen", "Column, pressure and recycled oxygen", "all three tank tricks"))


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


def _vm_fallback_text(c: dict) -> str:
    """Why a vessel's cost uses fewer tank tricks than the scenario (mirrored by vmFallbackText in page_vessels.js)."""
    return ("The scenario clears CO₂ with “tank tricks”: a column beside the tank that strips it without bubbles, and the options that go "
            "with it. This vessel is taller, so the column would keep too much of the culture at a high pH, which slows cell growth. The cost "
            f"here uses what passes that check: “{_esc(c['tricks_fallback'])}”. With the scenario’s own tricks at full density it would be "
            f"{_vm_money(c['unchecked_cost'])}.")


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
                    extra = f"<br><span class='alt'>{_vm_fallback_text(c)}</span>"
                cells.append(f"<td title=\"{_esc(c['evidence'])}\"><b>{_vm_money(c['cost'])}</b><br><span class='alt'>"
                             f"{c['density']:.0f} g/L, limited by {_esc(lim)}. Biggest cost: {_esc(c['biggest'])}.</span><br>"
                             f"{_vm_tag(c['tag'])}"
                             + (f"<br><span class='alt vunshown'>{_esc(V.UNSHOWN_NOTE)}</span>" if c["density_unshown"] else "")
                             + f"{extra}</td>")
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


_GH = "https://github.com/PabloAMC/Cultivated_meat/blob/main/research_notes/"


def _vm_pointers() -> str:
    """Where to read more: the research note behind the table and its three source files."""
    links = (("vessels_and_modes.md", "the full study"),
             ("vessels_and_modes_sources/airlift_bubble_column_bags.md", "airlifts, bubble columns and bags"),
             ("vessels_and_modes_sources/packed_bed_hollow_fibre.md", "packed beds and hollow fibres"),
             ("vessels_and_modes_sources/operating_modes.md", "the ways of running a tank, and continuous harvest at scale"),
             ("retention_devices.md", "the devices that hold cells back in perfusion"))
    return ("<p class='fnote'><b>Read more.</b> " + "; ".join(f"<a href='{_GH}{p}'>{_esc(t)}</a>" for p, t in links) +
            ". Every source there says how much of it was read.</p>")


# ----------------------------------------------------------------------------
# Evidence: the back-test against reported runs, and the model beside company cost claims
# ----------------------------------------------------------------------------
def backtest_table() -> str:
    import floor_physics as fp
    rows = []
    for run_, what, obs, mod, note in fp.backtest():
        rows.append(f"<tr><td>{_esc(run_)}</td><td>{_esc(what)}</td><td class='n'>{obs:.1f}</td><td class='n'>{mod:.1f}</td>"
                    f"<td class='n'>{obs / mod:.2f}×</td><td class='s'>{_esc(note)}</td></tr>")
    return ("<div class='scrollx'><table class='sctab'><thead><tr><th>Reported run</th><th>Quantity</th><th>Observed</th><th>Model</th>"
            "<th>Observed / model</th><th>Note</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>")


def industry_claims() -> str:
    """The model against company cost claims, on the same basis (industry_claims.py): scenarios split into the plant
    charge and operating cost; the low-lactate example's cells run as Vow runs its tank; the claims with their basis."""
    import industry_claims as IC
    s = IC.summary()
    rows = []
    for k in S.PAGE_ORDER + ("reference",):
        d = s["split"][k]
        rows.append(f"<tr><td>{_esc(IC.NAMES[k])}</td><td class='n'>{money(d['total'])}</td><td class='n'>{money(d['capital'])}</td>"
                    f"<td class='n'><b>{money(d['operating'])}</b></td><td class='n'>{money(d['membranes'])}</td></tr>")
    t1 = ("<div class='scrollx'><table class='sctab'><thead><tr><th>Case</th><th>Cells, $/kg</th><th>Charge on the plant</th>"
          "<th>Operating cost</th><th>Of which filter membranes</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>")
    rows = []
    for (name, d), (_n, d27) in zip(s["vow"], s["vow27"]):
        rows.append(f"<tr><td>{_esc(name)} (${d['capex_k_m3']:.0f}k per m&sup3;)</td><td class='n'>{money(d['total'])}</td>"
                    f"<td class='n'>{money(d['capital'])}</td><td class='n'><b>{money(d['operating'])}</b></td>"
                    f"<td class='n'>{money(d27['total'])}</td></tr>")
    t2 = ("<p class='small'>The low-lactate example's cells in a 20 m&sup3; tank drained and refilled, as Vow runs its tank, in three plants. "
          f"Costs are a kilo of cells at the {s['vow'][0][1]['density']:.0f} g/L the model gives, and in the last column at the 27 g/L reported for meat cells.</p>"
          "<div class='scrollx'><table class='sctab'><thead><tr><th>Plant</th>"
          f"<th>Cells, $/kg</th><th>Charge on the plant</th><th>Operating cost</th>"
          "<th>Cells at 27 g/L</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>")
    rows = []
    for c in IC.CLAIMS:
        rows.append(f"<tr><td><a href='{_esc(c.source)}'>{_esc(c.who)}</a></td><td>{_esc(c.figure)}</td><td class='s'>{_esc(c.of_what)}</td>"
                    f"<td class='s'>{_esc(c.capital)}</td><td class='s'>{_esc(c.kind)}; checked by {_esc(c.checked)}</td><td>{_esc(c.date)}</td></tr>")
    t3 = ("<div class='scrollx'><table class='sctab'><thead><tr><th>Who</th><th>Figure</th><th>A cost of</th><th>Capital in it?</th>"
          "<th>Kind</th><th>Date</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>")
    ops = [d["operating"] for _n, d in s["vow"]]
    text = (f"<p class='expl'>Company cost figures are usually operating cost: medium, labour, utilities and consumables, with nothing "
            f"for the plant. Every scenario here includes a yearly charge on the plant. On operating cost alone, the low-lactate example's "
            f"cells in a tank drained and refilled, as Vow runs its 20 m&sup3; tank, cost ${min(ops):.1f}&ndash;{max(ops):.1f} a kilo, against "
            f"the $10&ndash;15 an investor reports for several companies on an unstated basis. The full cost adds the yearly charge on the "
            f"plant, and what a plant for animal cells costs to build is the number most worth checking. None of the company figures has "
            f"been audited.</p>")
    return text + t1 + t2 + t3
