"""test_easy_view.py — the page's first screen (build_interactive.py, page_scenarios.js), rebuilt 2026-11-19 around the reader's cells.

The page opens on a live sentence, three tiles, reference points that load the cells, a contour map with the reader's point and a cloud
of draws, the slider for meat buyers who would pick it at the same price (the map's y), "Change the cells" (four traits and the routes
verdict), "Change the plant" and "What it would take"; everything else sits in six levels that open in place. This test reads the BUILT
page (interactive.html), so run `python build_interactive.py` first. It checks

  * the structure: those pieces, in that order, the six levels after them, and none of the pieces the rebuild cut (the case bar, the
    banded chart, the forecast);
  * the names: Published cells, Selected cells, Engineered cells, all favourable, Humbird's optimistic design, as a company reports;
    never "Today's cells", "Central case" or "Best case" in what a reader sees;
  * the numbers the page's own JavaScript writes (run here under Node), for each reference point and for settings the reader moved:
    the cost tile is the median of the page's cloud and its most-likely-values figure is scenarios.run's; the shop price is the shelf
    price of the median; the share is scenarios.world_share at the median and the reader's meat buyers; the sentence states the routes
    verdict cell_traits.routes_needed gives, and never says engineering is necessary;
  * "What it would take" carries scenarios.what_it_would_take;
  * the words: no build stamp in the visible text, and no nonzero share printed as 0%.

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
import cell_traits as CT  # noqa: E402
from price_ratio import shelf_price  # noqa: E402

HTML = os.path.join(ROOT, "interactive.html")
REFS = (("today", "Published cells"), ("central", "Selected cells"), ("best", "Engineered cells, all favourable"),
        ("humbird", "Humbird's optimistic design"), ("company", "As a company reports"))
LEVELS = ("assumes", "moves", "where", "engineering", "shoppers", "method")
FIRST = ('id="deck"', 'id="tiles"', 'id="tp_refs"', 'id="tpmap"', 'id="tp_buyers"', 'id="tp_traits"', 'id="tp_verdict"', 'id="pl_perf"',
         'id="pl_capex"', 'id="pl_cpl"', 'id="pl_med"', 'id="tp_wit"')

# Runs in the same scope as the page's script (the DOM stubbed, the auto-run tail cut off): loads each reference point, then a few
# settings a reader would move, and returns what the first screen would show.
PROBE = r"""
;(function(){
  const def={}; MODEL.sliders.forEach(s=>def[s.key]=s.default);
  Object.assign(state,def,{region:"global",income:C.REGION_INCOME.global}); KP=effConsts(state);
  const show=()=>{ PGS.cloud=null; tpExtraNow(); const f=pgFacts();
    return {key:f.key, label:f.label, cost:f.cost, cb:f.cb, point:f.point, retail:f.retail, mult:f.mult, share:f.share, sb:f.sb, buyers:f.buyers,
            traits:tpTraitsShown(), rank:f.rn.rank, verdict:tpVerdictPlain(f.rn), tiles:pgTilesHTML(f), deck:pgDeck(f), choice:SCS.choice, base:SCS.base}; };
  const load=k=>{ const r=tpRef(k); SCS.ref=k; SCS.from=k; SCS.traits={}; SCS.held={};
    if(r.kind==="humbird"){ SCS.base="humbird"; SCS.hb={mode:"perfusion",plant:"sterile"}; } else { SCS.base="switches"; SCS.choice=Object.assign({},r.choice); SCS.redesign=r.redesign; }
    tpSetBuyers(r.buyers); };
  const out={refs:{}, labels:TP.refs.map(r=>[r.key,r.label]), wit:TP.wit};
  ["today","central","best","humbird"].forEach(k=>{ load(k); out.refs[k]=show(); });
  load("central"); SCS.ref=null; SCS.traits={lac_yield:0.2,doubling_h:20}; tpRedesign(); tpSetBuyers(0.4); out.moved=show();
  load("today"); SCS.ref=null; SCS.traits={nh3_kg:0.01}; SCS.held={capex_x:0.5,medium_price:0.1}; out.moved2=show();
  load("central"); SCS.ref=null; SCS.traits={doubling_h:13}; out.moved3=show();
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
    for gone in ('id="casebtns"', 'id="casebar"', 'id="l0chart"', 'id="eqs"', 'id="view_easy"', "setView(", 'id="pie"', 'id="sc_presets"',
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
    if re.search(r"\bbuild \d{4}-\d\d-\d\d", vis) or re.search(r"\bjs \d{4}-\d\d-\d\d", vis) or "__BUILD_STAMP__" in vis:
        fails.append("a build stamp is in the visible text")

    # --- the numbers the page's own script writes
    probe = _run_probe(html)
    if probe is None:
        print("  (node not found: the first screen's numbers were not checked)")
        return fails
    if [tuple(x) for x in probe["labels"]] != list(REFS):
        fails.append(f"the reference points should be {REFS}, got {probe['labels']}")
    cases = [(k, v) for k, v in probe["refs"].items()] + [("moved", probe["moved"]), ("moved2", probe["moved2"]), ("moved3", probe["moved3"])]
    for name, w in cases:
        lab = dict(REFS).get(name, "your settings")
        if name in probe["refs"]:
            if w["key"] != name or w["label"] != lab:
                fails.append(f"{lab}: the page does not call its own reference point by name (got {w['key']}, {w['label']})")
            want_buyers = S.meat_buyers_at_equal_price(None if name != "best" else __import__("inputs").value("best_equal_price_share"))
            if abs(w["buyers"] - want_buyers) > 1e-9:
                fails.append(f"{lab}: meat buyers at the same price {w['buyers']:.4f}, the model's {want_buyers:.4f}")
        elif w["key"] != "own" or not w["deck"].startswith("With your settings"):
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
        ws = S.world_share(w["cost"], w["buyers"])
        if abs(w["share"] - ws) > max(0.01, 0.003 * ws):
            fails.append(f"{lab}: the share tile is {w['share']:.4f}%, scenarios.world_share gives {ws:.4f}%")
        rn = CT.routes_needed(w["traits"])
        if w["rank"] != rn["rank"]:
            fails.append(f"{lab}: the routes verdict ranks the traits {w['rank']}, cell_traits {rn['rank']}")
        short = ["No genetic engineering has been needed", "No genetic engineering has been needed", "shown only with genetic engineering",
                 "not been shown by any route"][rn["rank"]]
        if short not in w["deck"]:
            fails.append(f"{lab}: the sentence does not give the routes verdict ('{short}'): {w['deck'][:200]}")
        for t in (w["deck"], w["verdict"]):
            if re.search(r"engineering is (necessary|needed|required)|needs? genetic engineering|must be engineered", t, re.I):
                fails.append(f"{lab}: the page says engineering is necessary: {t[:160]}")
        tiles = _text(w["tiles"])
        for want in ("Median of", "8 in 10 draws", "if every estimate lands on its most likely value", "kilo of everyday meat",
                     "Plant-based meat today: about", "result"):
            if want not in tiles:
                fails.append(f"{lab}: the tiles do not say '{want}' (they say: {tiles[:230]})")
        for t in (tiles, _text(w["deck"])):
            if "~0%" in t or re.search(r"(?<![\d.])0(\.0+)?%", t):
                fails.append(f"{lab}: a share is printed as 0%: {t[:200]}")
            if "most likely between" in t:
                fails.append(f"{lab}: a range still reads 'most likely between'")
    if probe["moved3"]["rank"] != 3:
        fails.append("a doubling every 13 hours has not been shown by any route; the page should say so")

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
