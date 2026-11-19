"""test_easy_view.py — the page's first screen (build_interactive.py, page_scenarios.js), rebuilt 2026-11-19 around the reader's cells.

The page opens on a live sentence, reference points that load the cells, three figures (how far the cost is from what matters, on one
log axis; where the money goes, grouped by what drives it; where it would sell, by kind and type of meat, as bars or a disk), a contour
map with the reader's point and the range of the draws, the slider for meat buyers who would pick it at the same price (the map's y),
"Change the cells" (four traits, each marked with the best measured in meat cells, and the plant protein in a steak or fillet), "Change
the plant" and "What it would take"; everything else sits in six levels that open in place. Since 2026-11-19 (the author: "I would
remove it") the page makes no claim about the route (feed change, selection, adaptation, engineering) that would give a trait: it says
only what has been measured in meat cells (cell_traits.best_in_meat_cells). This test reads the BUILT
page (interactive.html), so run `python build_interactive.py` first. It checks

  * the structure: those pieces, in that order, the six levels after them, and none of the pieces the rebuilds cut (the case bar, the
    banded chart, the forecast, the three context-free tiles);
  * the names: Published cells, Selected cells, Engineered cells, all favourable, Humbird's optimistic design, as a company reports;
    never "Today's cells", "Central case" or "Best case" in what a reader sees;
  * the numbers the page's own JavaScript writes (run here under Node), for each reference point and for settings the reader moved:
    the cost is the median of the page's cloud and its most-likely-values figure is scenarios.run's; the costs 1% and 10% need are
    scenarios.cost_for_share's; the share is scenarios.world_share at the median and the reader's meat buyers; the cost split by driver
    adds up to the most-likely-values cost; the share by animal adds up to the share, its weights and prices are meat_market's grouped
    by animal_of, and the share by weight of cells is the share by weight of product with each cut's plant protein taken out; the
    sentence gives the yardsticks, never mentions engineering (beyond a case's name) or any other route; each trait carries the best
    value measured in meat cells, with its source, from cell_traits.best_in_meat_cells; the traits a set takes beyond them are
    cell_traits.beyond_measured's; every number in the figures' words has its yardstick beside it;
  * "What it would take" carries scenarios.what_it_would_take;
  * the words: no build stamp in the visible text, no em dash, and no nonzero share printed as 0%.

Runs as a script or under pytest.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import scenarios as S  # noqa: E402
import meat_market as mm  # noqa: E402
import cell_traits as CT  # noqa: E402
from price_ratio import shelf_price  # noqa: E402

HTML = os.path.join(ROOT, "interactive.html")
REFS = (("today", "Published cells"), ("central", "Selected cells"), ("best", "Engineered cells, all favourable"),
        ("humbird", "Humbird's optimistic design"), ("company", "As a company reports"))
LEVELS = ("assumes", "moves", "where", "engineering", "shoppers", "method")
FIRST = ('id="deck"', 'id="tp_refs"', 'id="regionsel"', 'id="tp_costline"', 'id="tp_groups"', 'id="tp_animals"', 'id="tp_sbars"', 'id="tp_disk"',
         'id="tpmap"', 'id="tp_buyers"', 'id="tp_traits"', 'id="pl_perf"', 'id="pl_capex"', 'id="pl_cpl"', 'id="pl_med"', 'id="tp_wit"')
# words that claim a route by which cells would get a trait (the author, 2026-11-19: remove them all); a case's name is not one
ROUTE_WORDS = re.compile(r"engineer|genetic|selection|selected (on|for|to)|adapt|by (any|which) route|routes? (that|verdict)|feed change|"
                         r"other cells|shown together|not (yet )?shown (together|by any)|least intrusive|knocked", re.I)
CASE_NAMES = ("Engineered cells, all favourable", "Engineered cells", "Selected cells", "Check the engineering")

# Runs in the same scope as the page's script (the DOM stubbed, the auto-run tail cut off): loads each reference point, then a few
# settings a reader would move, and returns what the first screen would show.
PROBE = r"""
;(function(){
  const def={}; MODEL.sliders.forEach(s=>def[s.key]=s.default);
  Object.assign(state,def,{region:"global",income:C.REGION_INCOME.global}); KP=effConsts(state);
  // the words the three figures write, caught from a stand-in document
  const words=f=>{ const cap={}, get=document.getElementById;
    document.getElementById=id=>new Proxy({}, {set(t,p,v){ if(p==="innerHTML") cap[id]=v; return true; },
      get(t,p){ return p==="innerHTML"?cap[id]:(p==="style"?{}:(p==="clientWidth"?0:()=>{})); }});
    try{ tpLineText(f); tpGroupsText(f); tpAnimalsRender(f); } finally{ document.getElementById=get; }
    return cap; };
  const show=()=>{ PGS.cloud=null; tpExtraNow(); const f=pgFacts();
    return {key:f.key, label:f.label, cost:f.cost, cb:f.cb, point:f.point, retail:f.retail, mult:f.mult, share:f.share, sb:f.sb, buyers:f.buyers,
            one:f.one, ten:f.ten, parity:f.parity, groups:f.groups, animals:f.animals, words:words(f),
            traits:tpTraitsShown(), beyond:tpBeyond(tpTraitsShown()), deck:pgDeck(f), choice:SCS.choice, base:SCS.base, cut:state.cut_cells}; };
  const load=k=>{ const r=tpRef(k); SCS.ref=k; SCS.from=k; SCS.traits={}; SCS.held={};
    if(r.kind==="humbird"){ SCS.base="humbird"; SCS.hb={mode:"perfusion",plant:"sterile"}; } else { SCS.base="switches"; SCS.choice=Object.assign({},r.choice); SCS.redesign=r.redesign; }
    tpSetBuyers(r.buyers); };
  const out={refs:{}, labels:TP.refs.map(r=>[r.key,r.label]), wit:TP.wit,
             best:Object.fromEntries(TRAIT_KEYS.map(k=>[k,[TP.traits[k].best,TP.traits[k].best_src,tpBestText(k)]])),
             witwords:TP.wit.map(r=>r.pick?tpBeyondWords(r.pick.traits):null)};
  ["today","central","best","humbird"].forEach(k=>{ load(k); out.refs[k]=show(); });
  load("central"); SCS.ref=null; SCS.traits={lac_yield:0.2,doubling_h:20}; tpRedesign(); tpSetBuyers(0.4); out.moved=show();
  load("today"); SCS.ref=null; SCS.traits={nh3_kg:0.01}; SCS.held={capex_x:0.5,medium_price:0.1}; out.moved2=show();
  load("central"); SCS.ref=null; SCS.traits={doubling_h:13}; out.moved3=show();
  // the plant protein in a steak or fillet (the first screen's slider): every figure follows it
  load("central"); state.cut_cells=0.5; out.cut50=show(); state.cut_cells=def.cut_cells;
  console.log=__realLog; console.log(JSON.stringify(out));
})();
"""

STUB = r"""
"use strict";
const fs=require("fs");
const NOOP=()=>{}; let CHAIN;
const ELEM=new Proxy({}, {get(_t,p){ if(p==="style") return {}; if(p==="classList") return {toggle:NOOP,add:NOOP,remove:NOOP};
  if(p==="querySelector") return ()=>ELEM; if(p==="querySelectorAll") return ()=>[];
  if(p==="appendChild"||p==="removeChild"||p==="setAttribute"||p==="addEventListener") return NOOP;
  if(p==="firstChild") return null; if(p==="textContent"||p==="innerHTML"||p==="value") return ""; return CHAIN; }, set(){ return true; }});
CHAIN=new Proxy(function(){ return ELEM; }, {get:()=>CHAIN, apply:()=>ELEM});
global.document={getElementById:()=>ELEM, createElement:()=>ELEM, createElementNS:()=>ELEM, querySelector:()=>ELEM, querySelectorAll:()=>[]};
global.window={};
global.__realLog=console.log; console.log=NOOP;
let js=fs.readFileSync(process.argv[2],"utf8");
js=js.replace(/console\.log\([^\n]*\);/,"");
js=js.replace(/buildRail\(\);[\s\S]*$/,"");
(0,eval)(js+fs.readFileSync(process.argv[3],"utf8"));
"""


def _model_js(html: str) -> str:
    bodies = [b for _a, b in re.findall(r"<script([^>]*)>(.*?)</script>", html, flags=re.S) if "function utilities" in b]
    if not bodies:
        raise RuntimeError("could not find the model <script> in interactive.html")
    return bodies[0]


def _run_probe(html: str) -> dict | None:
    node = shutil.which("node")
    if node is None:
        return None
    d = tempfile.mkdtemp(prefix="first_screen_")
    paths = {n: os.path.join(d, n) for n in ("model.js", "probe.js", "stub.js")}
    open(paths["model.js"], "w", encoding="utf-8").write(_model_js(html))
    open(paths["probe.js"], "w", encoding="utf-8").write(PROBE)
    open(paths["stub.js"], "w", encoding="utf-8").write(STUB)
    try:
        out = subprocess.run([node, paths["stub.js"], paths["model.js"], paths["probe.js"]], capture_output=True, text=True, timeout=180)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    if out.returncode != 0:
        raise RuntimeError(f"the first-screen probe failed:\n{out.stderr or out.stdout}")
    return json.loads(out.stdout.strip().splitlines()[-1])


def _visible(html: str) -> str:
    """The page's static text: scripts, styles and tags removed (what a reader sees before any script runs)."""
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t)


def _text(fragment: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment))


def check() -> list:
    fails = []
    if not os.path.exists(HTML):
        return [f"{HTML} missing: run `python build_interactive.py` first"]
    html = open(HTML, encoding="utf-8").read()
    vis = _visible(html)

    # --- structure: the first screen's pieces in order, then six levels that open in place
    pos = [html.find(p) for p in FIRST]
    for p, i in zip(FIRST, pos):
        if i < 0:
            fails.append(f"the first screen no longer has: {p}")
    if all(i >= 0 for i in pos) and pos != sorted(pos):
        fails.append("the first screen should run: sentence, tiles, reference points, map, meat-buyers slider, cells, plant, what it would take")
    first = html.find('<section id="first"')
    for lv in LEVELS:
        m = re.search(r'<details class="level[^"]*" id="%s">' % lv, html)
        if not m:
            fails.append(f"level #{lv} is not a section that opens in place")
        elif m.start() < first:
            fails.append(f"level #{lv} comes before the first screen")
        if f'href="#{lv}"' not in html:
            fails.append(f"nothing links to level #{lv}")
    for gone in ('id="tiles"', 'class="tile"', 'pgTilesHTML', 'id="casebtns"', 'id="casebar"', 'id="l0chart"', 'id="eqs"', 'id="view_easy"', "setView(", 'id="sc_presets"', 'id="tp_verdict"', 'tpRoutesNeeded', 'tpVerdict', 'cldot',
                 'class="chain"', 'onclick="fxApply()"'):
        if gone in html:
            fails.append(f"the page still carries a piece the rebuild cut: {gone}")

    # --- names and words
    for bad in ("Today's cells", "Today’s cells", "today's cells", "today’s cells"):
        if bad in html:
            fails.append(f"the old case name is still on the page: {bad}")
    for bad in ("Central case", "Best case", "best case", "the default cost", "the reference case", "The short version", "Rung ",
                "forecast for 2035", "Forecast for 2035", "2035 forecast", "author's odds"):
        if bad in vis:
            fails.append(f"the visible text still says: {bad}")
    bare_vis = vis
    for n in CASE_NAMES + ("Humbird's optimistic design", "Bioengineering", "engineering design", "Engineering"):
        bare_vis = bare_vis.replace(n, "")
    for m in ROUTE_WORDS.finditer(bare_vis):
        fails.append(f"the page's static text names a route: ...{bare_vis[max(0, m.start() - 80):m.end() + 40]}...")
    if re.search(r"\bbuild \d{4}-\d\d-\d\d", vis) or re.search(r"\bjs \d{4}-\d\d-\d\d", vis) or "__BUILD_STAMP__" in vis:
        fails.append("a build stamp is in the visible text")

    # --- the numbers the page's own script writes
    probe = _run_probe(html)
    if probe is None:
        print("  (node not found: the first screen's numbers were not checked)")
        return fails
    if [tuple(x) for x in probe["labels"]] != list(REFS):
        fails.append(f"the reference points should be {REFS}, got {probe['labels']}")
    cases = [(k, v) for k, v in probe["refs"].items()] + [("moved", probe["moved"]), ("moved2", probe["moved2"]), ("moved3", probe["moved3"]), ("cut50", probe["cut50"])]
    for name, w in cases:
        lab = dict(REFS).get(name, "your settings")
        if name in probe["refs"]:
            if w["key"] != name or w["label"] != lab:
                fails.append(f"{lab}: the page does not call its own reference point by name (got {w['key']}, {w['label']})")
            want_buyers = S.meat_buyers_at_equal_price(None if name != "best" else __import__("inputs").value("best_equal_price_share"))
            if abs(w["buyers"] - want_buyers) > 1e-9:
                fails.append(f"{lab}: meat buyers at the same price {w['buyers']:.4f}, the model's {want_buyers:.4f}")
        elif name != "cut50" and (w["key"] != "own" or not w["deck"].startswith("With your settings")):
            fails.append(f"{name}: moving a setting should make the page 'your settings'")
        # the most-likely-values cost: scenarios.run with the reader's traits (Humbird's design: explore() at its defaults)
        if w["base"] == "humbird":
            point = S.reference()["total"]
        else:
            tr = {k: v for k, v in w["traits"].items()} if name.startswith("moved") else {}
            held = {"moved2": {"capex_x": 0.5, "medium_price": 0.1}}.get(name, {})
            point = S.run(w["choice"], **{k: tr[k] for k in tr if name.startswith("moved")}, **held)["total"]
        if abs(w["point"] - point) > 1e-6 * max(1.0, point):
            fails.append(f"{lab}: the most-likely-values cost is {w['point']:.4f}, the model gives {point:.4f}")
        if not (w["cb"][0] <= w["cost"] <= w["cb"][2]) or abs(w["cost"] - w["cb"][1]) > 1e-12:
            fails.append(f"{lab}: the cost tile is not the median of the cloud")
        if abs(w["retail"] - shelf_price(w["cost"])) > 1e-6:
            fails.append(f"{lab}: the shop price is not the shelf price at the median cost")
        ws = S.world_share(w["cost"], w["buyers"])     # (at the model's own plant-protein share; cut50 sets another)
        if name != "cut50" and abs(w["share"] - ws) > max(0.01, 0.003 * ws):
            fails.append(f"{lab}: the share tile is {w['share']:.4f}%, scenarios.world_share gives {ws:.4f}%")
        # no route claims: the traits beyond what is measured in meat cells are cell_traits', and the sentence names no route
        if sorted(w["beyond"]) != sorted(CT.beyond_measured(w["traits"])):
            fails.append(f"{lab}: the traits beyond the best measured in meat cells are {w['beyond']}, cell_traits gives {CT.beyond_measured(w['traits'])}")
        bare = w["deck"]
        for n in CASE_NAMES:
            bare = bare.replace(n, "")
        if ROUTE_WORDS.search(bare):
            fails.append(f"{lab}: the sentence names a route ('{ROUTE_WORDS.search(bare).group(0)}'): {w['deck'][:200]}")
        # the share by weight of cells: the share by weight of product with each cut's plant protein taken out
        cells = sum(t["w"] * t["sh"] * (w["cut"] if t["structured"] else 1.0) for t in w["animals"]["types"]) * 100
        if abs(cells - w["animals"]["cells"]) > 1e-9 * max(1.0, cells) or w["animals"]["cells"] > w["animals"]["total"] + 1e-12:
            fails.append(f"{lab}: the share by weight of cells is {w['animals']['cells']:.5f}%, the products give {cells:.5f}%")
        if not re.search(r"by weight of product \(.*by weight of cells\)", w["deck"]) and w["sb"][2] >= 0.00095:
            fails.append(f"{lab}: the sentence does not give the share by weight of product and of cells: {w['deck'][-260:]}")
        # the yardsticks: the costs 1% and 10% of world meat need, at the reader's meat buyers
        for t, got in ((1.0, w["one"]), (10.0, w["ten"])):
            want = S.cost_for_share(t, w["buyers"])
            if name == "cut50":
                continue
            if (want is None) != (got is None) or (want is not None and abs(want - got) / want > 0.003):
                fails.append(f"{lab}: the cost {t:g}% needs is {got}, scenarios.cost_for_share gives {want}")
        # where the money goes: the groups add up to the most-likely-values cost, and the litres are stated
        g = w["groups"]
        if abs(g["sum"] - w["point"]) > 1e-9 * max(1.0, w["point"]) or abs(g["total"] - w["point"]) > 1e-9 * max(1.0, w["point"]):
            fails.append(f"{lab}: the cost by driver adds up to {g['sum']:.4f}, the most-likely-values cost is {w['point']:.4f}")
        if [x["key"] for x in g["groups"]] != ["litres", "time", "other"]:
            fails.append(f"{lab}: the cost should be grouped by litres, time in the tank, everything else")
        for x in g["groups"]:
            if abs(sum(i["v"] for i in x["items"]) - x["v"]) > 1e-9:
                fails.append(f"{lab}: the items of '{x['name']}' do not add up to it")
        # where it would sell: by animal, from the per-type roll-up
        a = w["animals"]
        if abs(a["total"] - w["share"]) > 1e-9 * max(1.0, w["share"]):
            fails.append(f"{lab}: the share by animal adds up to {a['total']:.5f}%, the share is {w['share']:.5f}%")
        if w["share"] > 0 and abs(sum(r["part"] for r in a["rows"]) - 1) > 1e-9:
            fails.append(f"{lab}: the animals' parts of the sales do not add up to all of it")
        if abs(sum(r["x"] for r in a["rows"]) * 100 - a["total"]) > 1e-9 * max(1.0, a["total"]):
            fails.append(f"{lab}: the animals' shares do not roll up to the total")
        names = [r["name"] for r in a["rows"]]
        for n in ("Beef", "Sheep and goat", "Seafood", "Pork", "Chicken"):
            if n not in names:
                fails.append(f"{lab}: the share by animal has no row for {n}")
        mk = mm.MARKETS["global"]
        W = sum(t.w_vol for t in mk)
        for r in a["rows"]:
            keys = [r["key"]] if r["key"] != "Other" else ["Duck", "Rabbit", "Turkey"]
            ts = [t for t in mk if mm.animal_of(t).replace("/\n", "/") in keys]
            pw = sum(t.w_vol for t in ts) / W
            pp = sum(t.w_vol * t.p_conv for t in ts) / sum(t.w_vol for t in ts)
            if abs(pw - r["w"]) > 1e-9 or abs(pp - r["price"]) > 1e-9:
                fails.append(f"{lab}: {r['name']} is {r['w']:.4f} of world meat at ${r['price']:.2f}; meat_market gives {pw:.4f} at ${pp:.2f}")
        # the words: the sentence carries its yardsticks; each figure says what it compares with
        deck = _text(w["deck"])
        for want in ("8 in 10 draws, if the estimates you have not set vary", "1% of the world's meat and seafood", "a kilo of cells that would match the price of the average kilo eaten",
                     "of the cost scales with", "of meat buyers would pick it at the same price", "plant protein" if w["cut"] < 1 else "all cells"):
            if want not in deck:
                fails.append(f"{lab}: the sentence does not say '{want}': {deck[:240]}")
        ws_ = {k: _text(v) for k, v in w["words"].items()}
        bt = f"{w['buyers'] * 100:.1f}".rstrip("0").rstrip(".") + "% of meat buyers"
        for k, want in (("tp_cl_note", "Price parity: at"), ("tp_cl_note", "draws of the estimates nobody has measured"),
                        ("tp_cl_note", "most likely value"), ("tp_cl_note", "move that slider and they move"), ("tp_groups_sub", "every estimate at its most likely value"),
                        ("tp_groups_say", "1% of"), ("tp_groups_say", bt), ("tp_groups_table", "litres a kilo of cells"), ("tp_animals_sub", "at the median cost of"),
                        ("tp_animals_total", "Plant-based meat: about"), ("tp_animals_total", "by weight of cells"), ("tp_animals_say", "of its sales"),
                        ("tp_cl_alt", "8 in 10 draws"), ("tp_cl_alt", "if the estimates you have not set vary"), ("tp_groups_alt", "split by what drives the cost"),
                        ("tp_animals_alt", "Long-run share of each product"), ("tp_animals_alt", "by weight of cells")):
            if want not in ws_.get(k, ""):
                fails.append(f"{lab}: #{k} does not say '{want}': {ws_.get(k, '')[:200]}")
        for t in [deck] + list(ws_.values()):
            if "~0%" in t or re.search(r"(?<![\d.])0(\.0+)?%", t):
                fails.append(f"{lab}: a share is printed as 0%: {t[:200]}")
            if "most likely between" in t:
                fails.append(f"{lab}: a range still reads 'most likely between'")
            if "\u2014" in t:
                fails.append(f"{lab}: an em dash in the first screen's words: {t[:200]}")
            bare = t
            for n in CASE_NAMES:
                bare = bare.replace(n, "")
            if ROUTE_WORDS.search(bare):
                fails.append(f"{lab}: the first screen's words name a route ('{ROUTE_WORDS.search(bare).group(0)}'): {t[:160]}")
    if "doubling_h" not in probe["moved3"]["beyond"]:
        fails.append("a doubling every 13 hours is faster than the best measured in meat cells (15 hours); the page should say so")
    # the plant protein in a steak or fillet moves every first-screen figure that sells cuts
    c50, c0 = probe["cut50"], probe["refs"]["central"]
    if abs(c50["share"] - c0["share"]) < 1e-6 or (c50["one"] is not None and c0["one"] is not None and abs(c50["one"] - c0["one"]) < 1e-6):
        fails.append("half plant protein in a cut should move the share and the cost 1% needs")
    # the best value measured in meat cells, on each trait, with its source: cell_traits' data, nothing else
    best = CT.best_in_meat_cells()
    for k, (v, src, txt) in probe["best"].items():
        if v != best[k]["value"] or src != best[k]["short"]:
            fails.append(f"trait {k}: the page marks {v} ({src}), cell_traits gives {best[k]['value']} ({best[k]['short']})")
        if not txt.startswith("Best measured in meat cells: ") or src not in txt or ROUTE_WORDS.search(txt):
            fails.append(f"trait {k}: the mark's words should give the measurement and its source only: {txt}")
    for t in [x for x in probe["witwords"] if x]:
        if ROUTE_WORDS.search(t):
            fails.append(f"'What it would take' names a route: {t}")

    # --- what it would take: the model's table
    py = S.what_it_would_take()
    if len(py) != len(probe["wit"]):
        fails.append("'What it would take' does not carry the model's rows")
    for a, b in zip(py, probe["wit"]):
        if a["target"] != b["target"] or abs(a["buyers"] - b["buyers"]) > 1e-12 or (a["need"] is None) != (b["need"] is None) \
                or (a["need"] is not None and abs(a["need"] - b["need"]) > 1e-9) or (a["pick"] is None) != (b["pick"] is None):
            fails.append(f"'What it would take' row {a['target']}% at {a['buyers']:.1%} differs from scenarios.what_it_would_take")
    return fails


def test_easy_view():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    if fails:
        sys.exit(1)
    print("first screen: all checks passed")
