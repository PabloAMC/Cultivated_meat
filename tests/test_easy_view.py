#!/usr/bin/env python3
"""test_easy_view.py — the page's first screen (build_interactive.py, page_scenarios.js).

The page opens on one case selector, three numbers and one chart; everything else sits in six levels that open in place.
This test reads the BUILT page (interactive.html), so run `python build_interactive.py` first. It checks

  * the structure: the case bar, the tiles, the chart, the slider, the six levels, and no short/everything toggle;
  * the names: the four cases are Published cells, Central case, Best case and Your own settings, and the old name
    "Today's cells" appears nowhere in the page or its scripts;
  * the numbers: for each named case the tiles the page's own JavaScript writes (run here under Node) carry the model's
    bands (scenarios.bands): the median cost, its 8-in-10 range, the most-likely-values cost and the median share;
  * the words: no build stamp in the visible text, and no nonzero share printed as 0%;
  * the author's odds quoted on the page are still the ones the repo states.

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
from price_ratio import shelf_price  # noqa: E402
from inputs import value  # noqa: E402

HTML = os.path.join(ROOT, "interactive.html")
CASES = (("today", "Published cells"), ("central", "Central case"), ("best", "Best case"))
OWN = "Your own settings"
LEVELS = ("assumes", "moves", "where", "engineering", "shoppers", "method")

# Runs in the same scope as the page's script (the DOM stubbed, the auto-run tail cut off): puts the page on each named
# case, in two regions, and returns what the first screen would show.
PROBE = r"""
;(function(){
  const out={cases:{}, labels:MODEL.page.cases.map(c=>c.label), ownLabel:MODEL.page.own_label, keys:MODEL.page.cases.map(c=>c.key)};
  const put=(key,region)=>{ MODEL.sliders.forEach(s=>{ state[s.key]=s.start; if(s.solved) state[s.key+"_ovr"]=false; });
    state.region=region; state.income=C.REGION_INCOME[region];
    SCS.src="scenario"; SCS.choice=Object.assign({},SC.presets[key].choice); SCS.preset=key;
    state.equal_price_share=SC.presets[key].eqs; KP=effConsts(state); pgSetCost(); };
  MODEL.page.cases.forEach(c=>{ out.cases[c.key]={};
    ["global","us"].forEach(r=>{ put(c.key,r); const f=pgFacts();
      out.cases[c.key][r]={key:f.key, cost:f.cost, cb:f.cb, point:f.point, retail:f.retail, mult:f.mult, share:f.share, sb:f.sb,
                           tiles:pgTilesHTML(f), deck:pgDeck(f)}; }); });
  put("central","global"); state.equal_price_share=0.30; KP=effConsts(state); pgSetCost();
  { const f=pgFacts(); out.own={key:f.key, hasCostBand:!!f.cb, hasShareBand:!!f.sb, tiles:pgTilesHTML(f), deck:pgDeck(f), share:f.share}; }
  put("central","global"); SCS.choice.growth="24"; SCS.preset=scPresetOf(SCS.choice); pgSetCost();
  { const f=pgFacts(); out.own2={key:f.key, hasCostBand:!!f.cb, cost:f.cost, point:f.point, tiles:pgTilesHTML(f)}; }
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

    # --- structure: one case bar, three tiles, one chart, one slider; six levels that open in place; no second mode
    for piece in ('id="casebtns"', 'id="regionsel"', 'id="tiles"', 'id="l0chart"', 'id="l0legend"', 'id="l0alt"', 'id="l0table"',
                  'id="eqs"', 'id="sharedef"', 'id="deck"'):
        if piece not in html:
            fails.append(f"the first screen no longer has: {piece}")
    first = html.find('<section id="first"')
    for lv in LEVELS:
        m = re.search(r'<details class="level[^"]*" id="%s">' % lv, html)
        if not m:
            fails.append(f"level #{lv} is not a section that opens in place")
        elif m.start() < first:
            fails.append(f"level #{lv} comes before the first screen")
        if f'href="#{lv}"' not in html:
            fails.append(f"nothing links to level #{lv}")
    for gone in ('id="view_easy"', 'id="view_full"', "setView(", 'id="pie"', 'id="sc_presets"', 'id="sc_railsel"', 'id="easy_pick"', 'class="chain"'):
        if gone in html:
            fails.append(f"the page still carries a piece the rebuild cut: {gone}")
    if html.find('id="tiles"') > html.find('id="l0chart"') or html.find('id="l0chart"') > html.find('id="assumes"'):
        fails.append("the first screen should run tiles, then the chart, then the levels")

    # --- names
    for bad in ("Today's cells", "Today’s cells", "today's cells", "today’s cells"):
        if bad in html:
            fails.append(f"the old case name is still on the page: {bad}")
    for bad in ("the default cost", "the reference case", "The short version", "Rung "):
        if bad in vis:
            fails.append(f"the visible text still says: {bad}")

    # --- no build stamp in what a reader sees
    if re.search(r"\bbuild \d{4}-\d\d-\d\d", vis) or re.search(r"\bjs \d{4}-\d\d-\d\d", vis) or "__BUILD_STAMP__" in vis:
        fails.append("a build stamp is in the visible text")

    # --- the numbers the page's own script writes, against the model's bands
    probe = _run_probe(html)
    if probe is None:
        print("  (node not found: the first screen's numbers were not checked)")
        return fails
    if probe["labels"] != [lab for _k, lab in CASES] or probe["keys"] != [k for k, _lab in CASES]:
        fails.append(f"the three named cases should be {[lab for _k, lab in CASES]}, got {probe['labels']}")
    if probe["ownLabel"] != OWN:
        fails.append(f"the fourth case should be '{OWN}', got '{probe['ownLabel']}'")
    import meat_market as mm
    import numpy as np
    for key, label in CASES:
        b = S.bands(S.SCENARIOS[key].choice, eqs=S.eqs_of(key))
        point = S.run(S.SCENARIOS[key].choice)["total"]
        w = probe["cases"][key]["global"]
        if w["key"] != key:
            fails.append(f"{label}: the page does not recognise its own case (got '{w['key']}')")
        if abs(w["cost"] - b["cost"][1]) > 1e-6 or max(abs(x - y) for x, y in zip(w["cb"], b["cost"])) > 1e-6:
            fails.append(f"{label}: the cost tile is not the median of the draws ({w['cost']:.3f} against {b['cost'][1]:.3f})")
        if abs(w["point"] - point) > 1e-6:
            fails.append(f"{label}: the most-likely-values cost is {w['point']:.3f}, the model gives {point:.3f}")
        if abs(w["share"] - b["share"][1]) > 1e-9 or max(abs(x - y) for x, y in zip(w["sb"], b["share"])) > 1e-9:
            fails.append(f"{label}: the share tile is not the median of the draws")
        if abs(w["retail"] - shelf_price(b["cost"][1])) > 1e-6 or abs(w["mult"] - shelf_price(b["cost"][1]) / value("p_conv")) > 1e-6:
            fails.append(f"{label}: the shop price is not the shelf price at the median cost")
        tiles = _text(w["tiles"])
        for want in (f"About ${b['cost'][1]:.0f}", f"8 in 10 draws: ${b['cost'][0]:.0f}–{b['cost'][2]:.0f}", f"${point:.1f} if every estimate lands",
                     f"${shelf_price(b['cost'][1]):.0f} a kilo", f"{shelf_price(b['cost'][1]) / value('p_conv'):.1f} times everyday meat",
                     f"{S.pct_num(b['share'][1])}%", "Plant-based meat today: about"):
            if want not in tiles:
                fails.append(f"{label}: the tiles do not say '{want}' (they say: {tiles[:230]})")
        if "Median." not in tiles:
            fails.append(f"{label}: the tiles do not say that the headline is a median")
        # one region besides the world, from the same draws (scenarios.scenario_mc for cost, meat_market.monte_carlo for demand)
        cost = S.scenario_mc(S.SCENARIOS[key].choice, S.BAND_N, 0)["total"]
        us = np.percentile(mm.monte_carlo("us", S.BAND_N, seed=1, biomass=cost, equal_share_input=S.eqs_of(key))["vol"], [10, 50, 90])
        if abs(probe["cases"][key]["us"]["share"] - us[1]) > 1e-9:
            fails.append(f"{label}: the United States share on the page ({probe['cases'][key]['us']['share']:.4f}) is not the median of the draws ({us[1]:.4f})")
        for region in ("global", "us"):
            for name in ("tiles", "deck"):
                t = _text(probe["cases"][key][region][name])
                if "~0%" in t or re.search(r"(?<![\d.])0(\.0+)?%", t):
                    fails.append(f"{label}, {region}: a share is printed as 0% in the {name}: {t[:200]}")
                if "most likely between" in t:
                    fails.append(f"{label}: a range still reads 'most likely between'")
    own = probe["own"]
    if own["key"] != "own" or not own["hasCostBand"] or own["hasShareBand"]:
        fails.append("moving the equal-price slider should make the page 'Your own settings', keep the cost's draws and drop the share's")
    if "single estimate" not in _text(own["tiles"]).lower():
        fails.append("your own settings: the share tile should say it is a single estimate")
    own2 = probe["own2"]
    if own2["key"] != "own" or own2["hasCostBand"] or abs(own2["cost"] - own2["point"]) > 1e-9:
        fails.append("moving a switch should make the page 'Your own settings' at the most-likely-values cost, with no draws")

    # --- the author's odds: the page quotes only what the repo states
    import build_interactive as B
    stated = (open(os.path.join(ROOT, "RESULTS.md"), encoding="utf-8").read() + open(os.path.join(ROOT, "inputs.py"), encoding="utf-8").read())
    for k, (_what, odds) in B.ODDS.items():
        m = re.search(r"(\d+)(?: to (\d+))?%", odds)
        if m and not any(f"{n}%" in stated or f"0.{n}" in stated or f"-{n}%" in stated for n in m.groups() if n):
            fails.append(f"the page states odds of {odds} for '{k}', which neither RESULTS.md nor inputs.py carries")
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
