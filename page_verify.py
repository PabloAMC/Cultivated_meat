#!/usr/bin/env python3
"""page_verify.py — "How this is worked out, and how to check it": one collapsed box under each main result of the page.

The owner, 2026-11-24: "add justifications that would help people verify all the data we present, but do so smartly ... easy to
verify but does not obstruct the view from the main results". Each box is closed by default and has the same four parts, so a
reader learns the pattern once:
  1. the steps from the settings to the figure;
  2. the inputs it rests on and where each comes from;
  3. checks against something measured or published, with what agrees and what does not;
  4. where to check it yourself: the section of this page, the code file and the research note.
Every number in a box is computed here, at build time, from the model at its own settings (not the reader's), and the box says so.
build_interactive.main() replaces each <!--VERIFY:name--> marker with boxes()[name]; tests/test_easy_view.py checks every marker
is filled.
"""
from __future__ import annotations

import html as _h

GH = "https://github.com/PabloAMC/Cultivated_meat/blob/main/"


def _e(t: str) -> str:
    return _h.escape(t, quote=False)


def _code(path: str, what: str = "") -> str:
    return f'<a href="{GH}{path}" target="_blank" rel="noopener"><code>{_e(path)}</code></a>' + (f" ({_e(what)})" if what else "")


def _here(anchor: str, text: str) -> str:
    """A link to a section of this page that may sit inside closed sections: pgOpenTo opens them first."""
    return f'<a href="#{anchor}" onclick="return pgOpenTo(\'{anchor}\')">{_e(text)}</a>'


def _box(steps: list, inputs: list, checks: str, yourself: list, note: str = "") -> str:
    li = lambda xs: "".join(f"<li>{x}</li>" for x in xs)
    return ('<details class="verify"><summary>How this is worked out, and how to check it</summary><div class="vb">'
            f'<p class="vh">How it is worked out</p><ol>{li(steps)}</ol>'
            f'<p class="vh">What it rests on</p><ul>{li(inputs)}</ul>'
            f'<p class="vh">Checked against</p>{checks}'
            f'<p class="vh">Check it yourself</p><ul>{li(yourself)}</ul>'
            + (f'<p class="small">{note}</p>' if note else "") + "</div></details>")


def _table(head: list, rows: list) -> str:
    return ('<div class="scrollx"><table class="sctab vt"><thead><tr>' + "".join(f"<th>{_e(h)}</th>" for h in head) +
            "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) +
            "</tbody></table></div>")


# ---------------------------------------------------------------------------------------------------------------------------
def tank() -> str:
    import humbird_check as HC
    fb, pf = HC.reproduce(HC.BEST, "today"), HC.reproduce("pf_aa", "2018")
    rows = [["Humbird's fed-batch tank, 20 m³, 90% oxygen", "120 g a litre (his Section 2.3, PDF pages 29 to 34; 115.6 at the end of "
             "a batch, Section 4.1)", f"{fb['density']:.0f} g a litre, limited by {_e(fb['limit'])}"],
            ["Humbird's perfusion tank, 2 m³, with two alternating-flow filters", "195 g a litre (his Section 4.2, PDF page 66)",
             f"{pf['density']:.0f} g a litre, limited by {_e(pf['limit'])}"]]
    return _box(
        ["Each limit is the densest culture one physical need allows: <b>oxygen in</b> (how fast the tank passes oxygen, kLa, times "
         "the oxygen gap, over what a gram of cells uses); <b>CO₂ out</b> (the gas bubbled through strips it, capped by the gas speed "
         "and the CO₂ the cells tolerate); <b>waste</b> (the ammonia and lactate tolerated over what a gram makes, where nothing "
         "washes them out); <b>mixing</b> (stirring must outpace oxygen use); <b>thickness</b> (cells at most a quarter of the volume).",
         "The lowest limit sets the density. The litres of medium a kilo are the largest of the needs listed (carrying the nutrients, "
         "washing out ammonia or lactate, the liquid that leaves with the cells).",
         "Tonnes a year from each m³ follow from the density, the growth rate and the time the tank is in use."],
        ["Every number is a lever in the side bar; each lever's <b>What this is</b> gives its source.",
         "The limits at the start are Humbird 2021's (Section 2.3): 5 mM of ammonia, 50 mM of lactate, 100 mbar of CO₂, gas at 6 mm a "
         "second, kLa of 26 an hour, cells at most 25% of the volume.",
         "What the cells make and use per gram follows from their traits (the four cell levers) and the oxygen per gram the model "
         "estimates."],
        _table(["Case", "Published", "This model"], rows),
        [_code("floor_physics.py", "explore(): every limit and the litres"), _code("humbird_check.py", "the back-test"),
         _code("research_notes/humbird_backtest.md")],
        "The checks are the model at Humbird's own settings, not at yours.")


def reactors() -> str:
    return _box(
        ["Each cell of the table is the engine run again with only the vessel (row) and the way it is run (column) changed; every "
         "other setting is yours.",
         "The tag says whether animal cells have been grown that way at that size, from published runs and company reports."],
        ["What each vessel can do (oxygen transfer, mixing, what it holds back) and what it costs: " + _code("vessels.py") + "."],
        "<p>The stirred tank in fed-batch at 20 m³ is the back-tested case: at Humbird's settings it gives his best estimate (the "
        "box under the cost breakdown). The rest of the table has no published cost to check against.</p>",
        [_code("vessels.py"), _code("research_notes/vessels_and_modes_sources/operating_modes.md", "sources for the tags")])


def cost() -> str:
    import humbird_check as HC
    h, r = HC.his_today(HC.BEST), HC.reproduce(HC.BEST, "today")
    eng = {k: float(r[k]) for k in ("growth_factors", "consumables", "utilities", "labour", "capital")}
    eng["nutrients"] = float(r["total"]) - sum(eng.values())
    names = {"nutrients": "Nutrients", "growth_factors": "Growth factors", "consumables": "Supplies", "utilities": "Energy and gas",
             "labour": "Labour", "capital": "Plant: payment, maintenance, insurance"}
    rows = [[names[k], f"${h[k]:.2f}", f"${eng[k]:.2f}"] for k in HC.LINES] + \
           [["<b>Total</b>", f"<b>${h['total']:.2f}</b>", f"<b>${float(r['total']):.2f}</b> ({(float(r['total']) / h['total'] - 1) * 100:+.1f}%)"]]
    return _box(
        ["<b>Plant</b>: what the plant costs per m³ of tank, times its yearly charge (the payment with interest, plus 9% for "
         "maintenance and insurance), over the tonnes each m³ makes a year.",
         "<b>Labour</b>: Humbird's crew per m³ of tank, more in perfusion, over the same tonnes.",
         "<b>Medium</b>: the price a litre times the litres a kilo, never less than the nutrients the cells eat; growth factors on top "
         "where they are bought.",
         "<b>Energy and supplies</b>: per kilo, from the gas and power the tank uses and Humbird's supplies."],
        ["The plant item by item: " + _code("plant_items.py") + ", from Humbird 2021's Tables 4.3 and 4.4.",
         "Prices are brought to 2025 dollars: consumer prices for running costs, a plant-cost index for the plant."],
        "<p>Humbird's best estimate (his Table 4.7, column 2), his lines in 2025 dollars against this model at his settings:</p>" +
        _table(["Line", "Humbird 2021", "This model"], rows),
        [_here("assumes", "Published cost estimates: the back-test line by line, with why each line differs"),
         _code("humbird_check.py"), _code("floor_physics.py")])


def plant_running() -> str:
    return _box(
        ["<b>Hollow dots</b>: each study's own plant and running costs, from the page or table its note names, in 2025 dollars by "
         "consumer prices (pounds at $1.28 and euros at $1.13, 2024 and 2025 averages typed from memory, to be checked against an "
         "official series).",
         "<b>Filled dots</b>: the study's starting set on this page's model. What the set changes from the study, assumption by "
         "assumption, is listed under the side bar's buttons when the set is loaded.",
         "Plant is the yearly payment with interest, maintenance and insurance; running is everything else."],
        ["Each study's figures and their pages: " + _code("study_assumptions.py", "SPLITS and SETS") + "."],
        "<p>Not a check: the plot compares studies. Studies count different products (a kilo of cells, of meat, of a product partly "
        "plant); each dot's note says which.</p>",
        [_code("research_notes/study_comparison.md", "section 13: every set's audit and every study's split"),
         _code("study_assumptions.py")])


def share_map() -> str:
    import demand_checks as D
    import market_share as M
    import market_size_loop as L
    import scenarios as S
    from inputs import value
    pr, s, m = S._demand(), D.summary(), D.menu_summary()
    v = s["variants"][0]
    resp = L.summary()["response"]["products"]
    still = [resp[n]["response"] for n in resp if resp[n]["R"][0] > 1.5]
    i3 = D.R_GRID.index(3.0)
    van, prem, pb = v["cold"], v["curve"][i3], s["pb"]["elasticity"]
    lo_s, hi_s = D.SALMON_ALONG_CURVE
    rows = [
        ["Cultivated meat at first contact and equal price: own-price elasticity", "Van Loo, Caputo and Lusk 2020, a US choice "
         f"experiment [8] (simulated from its fitted model)", f"about {D.VANLOO_AT_PARITY:g} ({min(D.VANLOO_ARMS):g} to {max(D.VANLOO_ARMS):g} across its arms)",
         f"{van:.2f}", "agrees" if min(D.VANLOO_ARMS) <= van <= max(D.VANLOO_ARMS) else "outside"],
        ["Share of a meat at 3 times the ordinary one's price", "sixteen premium real meats, fitted", f"{s['premium_3x']:.1f}%",
         f"{S.pct_num(prem)}%", "close" if abs(prem - s["premium_3x"]) < 0.5 else "differs"],
        ["Plant-based meat's own-price elasticity", "US retail scan data, GFI 2024", f"{D.PB_ELASTICITY_MEASURED:.2f} (the category "
         f"about {D.PB_CATEGORY_RANGE[0]:g} to {D.PB_CATEGORY_RANGE[1]:g})", f"{pb:.2f}",
         "within the category's range, less price-sensitive" if min(D.PB_CATEGORY_RANGE) <= pb <= max(D.PB_CATEGORY_RANGE) else "outside"],
        ["A premium product getting cheaper: % more volume per % lower price", "farmed salmon while it was a premium product",
         f"{lo_s:g} to {hi_s:g}", f"{min(still):.1f} to {max(still):.1f}",
         "the model responds more to price" if min(still) > hi_s else "agrees"],
        ["Plant-based meat added to a menu at meat's price: fall in meat's share", "a menu experiment, Hope 2026",
         f"{D.HOPE_FALL:g} points ({min(D.HOPE_CI):g} to {max(D.HOPE_CI):g})", f"{m['fall']:.2f} points",
         "inside the experiment's range, below its centre" if min(D.HOPE_CI) <= m["fall"] <= max(D.HOPE_CI) else "outside"],
    ]
    eps = pr.eps_own
    return _box(
        ["<b>Shop price</b>: for each cost of cells (across) and each kind of meat, the cost plus "
         f"${value('markup_add'):.2f} a kilo to reach the shelf, over one less the shop's {value('retail_margin') * 100:.0f}% margin "
         "(a steak or fillet also carries its plant protein).",
         "<b>Share of that meat's buyers</b>: the shopper model. Each shopper scores conventional meat, plant-based meat, cultivated "
         "meat and beans on price, taste, health, real meat and slaughter, and picks with a probability that rises smoothly with the "
         "score (a logit). The setting up the map moves how much shoppers like cultivated meat; at equal price it is the share of "
         "buyers who pick it, by definition.",
         "<b>All meat</b>: the shares of every kind of meat added up, weighted by the meat eaten, with conventional meat getting "
         "cheaper as it loses sales, and the markets closed by law left out. Each line joins the points of one total share.",
         "<b>The slope across the map</b> is the price response. The price weight is not typed in: meat as a category has a measured "
         f"elasticity of about {eps:g} [4]; one product on a shelf is taken to be {pr.kappa_base:g} times as price-sensitive as its "
         f"category, and cultivated meat's gap with the meat it copies counts {pr.cult_sub_mult:g} / {pr.kappa_base:g} times more "
         f"again, because the two are near-identical (κ = {pr.cult_sub_mult:g}). The weight is solved to give that at the calibration "
         f"price, ${pr.anchor_price:.2f} a kilo."],
        [f"Shoppers differ in how much they like cultivated meat: a spread of {pr.liking_sd:g} points of score with tails of "
         f"{pr.liking_tail:g}, and {pr.price_insensitive_share * 100:.0f}% of shoppers who respond to price far less. These and κ are "
         "fitted together to the choice experiment and to the premium meats below.",
         "Meat prices and the meat eaten, by kind and region: " + _code("meat_market.py") + " (GlobalProductPrices January 2026, "
         "USDA and BLS, FAO and USDA ERS; a few premium rows are estimates the file marks as unsourced).",
         "The shelf-price rule: " + _code("research_notes/retail_markup_form.md") + "."],
        _table(["What was measured", "Source", "Measured", "This model", "Verdict"], rows) +
        "<p class=\"small\"><b>Where it is weak.</b> No one has measured cultivated meat's price response once it is familiar: the one "
        "measurement for cultivated meat is a hypothetical choice at first contact. κ is a fitted judgement. Where cells are cheap the "
        "lines rest on the tails of the spread of liking, which few data reach. Two of the five checks miss: the model responds more "
        "to price than farmed salmon did, and takes less from meat than the menu experiment's centre.</p>",
        [_here("m_a1", "How the model works, A1: where the price weight comes from"),
         _here("shoppers", "The shopper model: its settings, the share at each price and what raises or lowers it"),
         _code("demand_checks.py", "the checks above"), _code("market_share.py", "the shopper model"),
         _code("research_notes/demand_heterogeneity_evidence.md")],
        "The checks are the model at its own settings, not at yours.")


def meats() -> str:
    return _box(
        ["Each bar is one product's long-run share of its own sales, at its own shop price for the cost of cells at your settings, "
         "from the shopper model (the box under the map).",
         "The total weights each product by the meat eaten of it; the dotted line weights by money spent.",
         "Plant-based meat's share is worked out by the same model at its own price, stacked on top."],
        ["Prices and the meat eaten of each product, by region: " + _code("meat_market.py") + " (sources named in the file; a few "
         "premium rows are marked as unsourced estimates)."],
        "<p>Plant-based meat's share with no cultivated meat on sale is set to its measured sales, about 0.4% of meat by volume (a "
        "calibration, not a check).</p>",
        [_code("meat_market.py"), _here("where", "Share by type of meat, by region and over time")])


def boxes() -> dict:
    return {"tank": tank(), "reactors": reactors(), "cost": cost(), "plant_running": plant_running(), "map": share_map(),
            "meats": meats()}


if __name__ == "__main__":
    for k, v in boxes().items():
        print(k, len(v))
