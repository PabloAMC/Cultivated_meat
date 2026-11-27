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
  * the names: Published cells, Humbird's optimistic design, as a company reports, and no named kind of hypothetical cell;
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
import build_interactive as BI  # noqa: E402
REFS = tuple((k, BI.REF_TEXT[k][0]) for k in BI.REF_ORDER)
import humbird_check as HC  # noqa: E402
LEVELS = ("assumes", "moves", "where", "engineering", "shoppers", "method")
# the first screen runs by sections, each with its settings before its result (the author, 2026-11-19): the cells and what they allow
# in the tank; the reactor, how it is run and the plant; the medium; then the cost; the shoppers; then the share
FIRST = ('id="deck"', 'id="levers"', 'id="tp_refs"', 'id="regionsel"', 'id="tp_refs_more"', 'id="st_cells"', 'id="tp_traits"', 'id="tp_cellrefs"',
         'id="tp_g_cells"', 'id="tp_g_cells_more"',
         'id="st_reactor"', 'id="pl_vessel"', 'id="pl_size"', 'id="pl_vmode"', 'id="pl_device"', 'id="pl_plant"', 'id="pl_items"', 'id="pl_capex"',
         'id="pl_tricks"', 'id="pl_shape"', 'id="pl_design_btn"', 'id="tp_g_reactor"', 'id="tp_g_reactor_more"', 'id="st_medium"', 'id="pl_med"', 'id="tp_g_medium"', 'id="st_shoppers"', 'id="tp_buyers"', 'id="tp_cuthost"',
         'id="sumbar"', 'id="tp_calc"', 'id="studies"', 'id="tp_studies"', 'id="tp_cellres"', 'id="tp_vmgrid"', 'id="tp_rtgrid"', 'id="tp_yours"', 'id="tp_groups"',
         'id="tp_unc"', 'id="tpmap"', 'id="tp_cl_note"', 'id="tp_animals"', 'id="tp_sbars"', 'id="tp_disk"', 'id="tp_wit"')
# words that claim a route by which cells would get a trait (the author, 2026-11-19: remove them all); a case's name is not one
ROUTE_WORDS = re.compile(r"engineer|genetic|selection|selected (on|for|to)|adapt|by (any|which) route|routes? (that|verdict)|feed change|"
                         r"other cells|shown together|not (yet )?shown (together|by any)|least intrusive|knocked", re.I)
CASE_NAMES = ("How the tank and the plant set the cost",)

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
  const load=k=>{ const r=tpRef(k); SCS.ref=k; SCS.from=k; SCS.traits={}; SCS.held={}; SCS.vessel="stirred"; SCS.vmode=null; SCS.device="tff"; SCS.clean=tpCleanNone();
    if(r.kind==="humbird"){ SCS.base="humbird"; SCS.hbKey=k; SCS.hb=Object.assign({},r.hb); } else { SCS.base="switches"; SCS.choice=Object.assign({},r.choice); SCS.redesign=r.redesign; }
    tpSetBuyers(r.buyers); };
  const out={refs:{}, labels:TP.refs.map(r=>[r.key,r.label]), wit:TP.wit,
             best:Object.fromEntries(TRAIT_KEYS.map(k=>[k,[TP.traits[k].best,TP.traits[k].best_src,tpBestText(k)]])),
             witwords:TP.wit.map(r=>r.pick?tpBeyondWords(r.pick.traits):null)};
  // the state the page opens in, before anything is loaded: the start, with every lever showing the value the engine uses
  { PGS.cloud=null; tpExtraNow(); const p0=tpParams(), r0=tpEval(SCS,p0), tr=tpTraitsShown();
    out.open={ref:SCS.ref, base:SCS.base, hbKey:SCS.hbKey, total:r0.total, params:p0, traits:tr, mode:tpVMode(), vessel:SCS.vessel, plant:tpPlant(),
      washed:tpWashed(p0), clean:SCS.clean.route, medium:p0.medium_price, density:r0.density, limit:r0.limit, retail:shelfPrice(r0.total,state),
      refText:tpRef(SCS.ref).text, refLabel:tpRef(SCS.ref).label,
      levers:TP.params.map(q=>({key:q.key, kind:q.kind, arg:q.arg, scale:q.scale, shown:tpParamDefault(q,p0), min:q.min, max:q.max})),
      fin:tpFin(SCS), charge:p0.charge, fx:{kill:C.fx.kill, harvest_loss:C.fx.harvest_loss, protect_dose:C.fx.protect_dose, gf:C.fx.gf, nh3_limit:C.fx.nh3_limit,
        lac_limit:C.fx.lac_limit, min_perfusion:C.fx.min_perfusion, gas_v:C.fx.gas_v, pco2:C.fx.pco2, osm_limit:C.fx.osm_limit, maint_share:C.fx.maint_share, wv:C.fx.wv}};
    // each lever set to the value it shows: the cost must not move
    out.open.same=TP.params.map(q=>{ SCS.held={[q.key]:tpParamDefault(q,p0)}; PGS.cloud=null; tpExtraNow(); const t=tpEval(SCS,tpParams()).total; SCS.held={}; return [q.key,t]; });
    out.open.sameTraits=TRAIT_KEYS.map(k=>{ SCS.traits={[k]:tr[k]}; PGS.cloud=null; tpExtraNow(); const t=tpEval(SCS,tpParams()).total; SCS.traits={}; return [k,t]; });
    tpExtraNow(); }
  ["humbird_best","today","central","best","humbird"].forEach(k=>{ load(k); out.refs[k]=show(); });
  load("central"); SCS.ref=null; SCS.traits={lac_yield:0.2,doubling_h:20}; tpRedesign(); tpSetBuyers(0.4); out.moved=show();
  load("today"); SCS.ref=null; SCS.traits={nh3_kg:0.01}; SCS.held={capex_x:0.5,medium_price:0.1}; out.moved2=show();
  load("central"); SCS.ref=null; SCS.traits={doubling_h:13}; out.moved3=show();
  // the plant protein in a steak or fillet (the first screen's slider): every figure follows it
  load("central"); state.cut_cells=0.5; out.cut50=show(); state.cut_cells=def.cut_cells;
  // one kind of meat at the same price: the share of its buyers who pick the cultivated one IS the setting
  out.same=[0.05,0.145,0.3,0.5,0.7,0.9].map(b=>[b,shareCalc(1,KP,{ax:state.accept_x,tfM:state.theta_free_M,income:C.income_ref,nbx:state.neophobia_x,hx:state.health_x,lmean:tpLmean(b),which:"x_meat"})]);
  // every further setting: set at each end of its slider it gives a finite cost, and freed it gives the starting cost back exactly
  const pt=()=>{ PGS.cloud=null; tpExtraNow(); return tpEval(SCS,tpParams()).total; };
  out.params=[]; ["humbird_best","today","central","best"].forEach(k=>{ load(k); const base=pt();
    TP.params.forEach(q=>{ SCS.held={[q.key]:q.min}; const lo=pt(); SCS.held={[q.key]:q.max}; const hi=pt(); SCS.held={}; const back=pt();
      SCS.held={[q.key]:tpParamDefault(q,tpParams())}; const same=pt(); SCS.held={};
      out.params.push({ref:k,key:q.key,base:base,lo:lo,hi:hi,back:back,same:same}); }); });
  // cleaning and reusing the medium: each route gives a finite cost (at the share that costs least, and at a set share), a leaner
  // feed for the washing litres too, and "none" gives the starting cost back exactly
  out.clean=[]; ["humbird_best","today","central","best","humbird"].forEach(k=>{ load(k); const base=pt();
    TP.clean.order.forEach(c=>{ SCS.clean={route:c,share:null,wash:null}; const best=pt(); const picked=c==="none"?0:tpCleanBest();
      SCS.clean={route:c,share:c==="none"?null:0.5,wash:null}; const half=pt(), g=tpCostGroups(tpEval(SCS,tpParams()));
      SCS.clean={route:c,share:c==="none"?null:picked,wash:null}; const atPicked=pt();
      SCS.clean=tpCleanNone(); out.clean.push({ref:k,route:c,base:base,best:best,half:half,picked:atPicked,back:pt(),gsum:g.sum,gtotal:g.total}); });
    SCS.clean={route:"none",share:null,wash:TP.clean.wash_ref}; const w=pt(); SCS.clean=tpCleanNone();
    out.clean.push({ref:k,route:"wash",base:base,best:w,half:w,picked:w,back:pt(),gsum:w,gtotal:w}); });
  out.cleanOrder=TP.clean.order; out.cleanTexts=TP.clean.routes;
  // the vessel and the way it is run: the page's cost is the vessel table's own cell
  out.vessels=[]; load("central"); const vb=tpParams();
  VM.vorder.forEach(v=>VM.morder.forEach(m=>{ if(!vmPossible(v,m)) return; const c=vmCell(v,m,vb);
    SCS.vessel=v; SCS.vmode=(v==="stirred"&&(m==="perfusion"||m==="fedbatch"))?null:m; SCS.choice.mode=(v==="stirred"&&m==="fedbatch")?"fedbatch":"perfusion";
    out.vessels.push({v:v,m:m,cell:c.cost,page:pt()}); }));
  load("central");
  // the retention device: the page's cost is retention.py's (page_retention.js, checked against Python by run_parity.py)
  out.devices=MODEL.rt.order.map(d=>{ SCS.device=d; const page=pt(); SCS.device="tff"; return {d:d,page:page,rt:rtCost(d,tpParams()).total}; });
  // Humbird's best estimate: the model's four additions are levers at his value; the button switches them on and off; loading
  // the other starting point, or this one again, resets every lever (the page's own tpLoad and tpToggleAdds, the redraw cut out)
  { const rc=recompute; recompute=()=>{}; try{
    const shown=()=>{ PGS.cloud=null; tpExtraNow(); const p=tpParams(); return {total:tpEval(SCS,p).total, held:Object.keys(SCS.held), ref:SCS.ref, base:SCS.base,
      levers:Object.fromEntries(TP.params.map(q=>[q.key,SCS.held[q.key]===undefined?tpParamDefault(q,p):SCS.held[q.key]])), medium:p.medium_price, on:tpAddsOn(SCS), has:!!tpAddsRef(SCS),
      fx:{kill:C.fx.kill, harvest_loss:C.fx.harvest_loss, protect_dose:C.fx.protect_dose}, flow:p.min_perfusion}; };
    tpLoad("humbird_best"); const a0=shown(), live=tpAddsLive(SCS), text=tpAddsText(live);
    tpToggleAdds(); const a1=shown(); tpToggleAdds(); const a2=shown();
    tpToggleAdds(); tpSetHeld("nh3_limit",3,false); tpLoad("today"); const b=shown();
    tpSetHeld("killx",3,false); tpLoad("humbird_best"); const a3=shown();
    load("today"); const b0=shown();
    out.adds={start:a0, live:live, text:text, on:a1, off:a2, today:b, today0:b0, again:a3, model:Object.fromEntries(tpRef("humbird_best").adds.map(a=>[a[0],tpAddModel(a[0])]))};
  } finally{ recompute=rc; } }
  // conventional meat's price response and the closed share of the market: finite at both ends, and set back they give the start
  out.mk=(()=>{ load("best"); const sh=()=>{ PGS.cloud=null; tpExtraNow(); return pgFacts().share; };
    const s0=sh(), es0=state.mk_supply, cl0=[state.closed_level,state.closed_custom], r={s0:s0, demand:C.mk_demand, es:{}};
    [0.5,2,10,Infinity].forEach(v=>{ state.mk_supply=v; r.es[String(v)]=sh(); }); state.mk_supply=es0; r.back=sh();
    r.closed=C.closed[state.region].map((_x,l)=>{ state.closed_level=l; state.closed_custom=null; return sh(); });
    state.closed_custom=0.3; r.custom=sh(); state.closed_level=cl0[0]; state.closed_custom=cl0[1]; r.cback=sh(); return r; })();
  load("today"); out.lead=pgLead(); out.pubs=TP_PUBS; out.publ=TP_PUBL; out.frontier=TP.frontier; out.floor=C.FEEDSTOCK_FLOOR;
  out.shown=TP_SHOWN; out.start=TP_START; out.npar=TP.params.length;
  // 2026-11-22 (fifth batch): the level "How the tank and the plant set the cost" has no settings of its own; its result card is the
  // side bar's case, priced as the first screen prices it, whatever the side bar holds (and the address carries the new settings)
  { const rc=recompute; recompute=()=>{}; try{
    const l4=()=>{ PGS.cloud=null; tpExtraNow(); const c=pgPointCost(); return {point:c, text:scResultHTML(SCS.choice,PGS.cloud.res), res:PGS.cloud.res.total}; };
    out.l4=[];
    tpLoad("humbird_best"); out.l4.push(l4());
    tpLoad("central"); tpSetHeld("hazard",1.5,false); tpSetHeld("p_top",0.6,false); tpSetTrait("doubling_h",30,false); out.l4.push(l4());
    tpSetPlant("yeastplus"); tpSetItem("hall","shed"); tpSetDevice(MODEL.rt.order[MODEL.rt.order.length-1]); out.l4.push(l4());
    tpTakeCells("chicken"); scPick("tricks","column"); out.l4.push(l4());
    const h=scSettingsHash(), c0=pgPointCost(), keep={pc:SCS.plantClass, it:JSON.stringify(SCS.items)};
    tpLoad("today"); scReadHash(h); PGS.cloud=null; tpExtraNow();
    out.hash={h:h, before:c0, after:pgPointCost(), pc:[keep.pc,SCS.plantClass], it:[keep.it,JSON.stringify(SCS.items)]};
    // a link written before 2026-11-22 (switches, traits and levers only) still reads
    tpLoad("today"); scReadHash("from:central,base:switches,buyers:0.2,ch:perfusion/lowlactate/36/sterile/4/column/tall/1/14/none/0.20,rd:0,t.doubling_h:30,h.capex_x:0.8");
    PGS.cloud=null; tpExtraNow(); out.oldhash={cost:pgPointCost(), base:SCS.base, dh:SCS.traits.doubling_h, cx:SCS.held.capex_x, pc:SCS.plantClass};
  } finally{ recompute=rc; } }
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


# the whole page's words (the owner, 2026-11-20): converted costs say "2025 dollars", never "today"; no retired name; every meat price
# names its kind of meat; no judgement attributed to the owner; the levels are named for what they hold, not "Level 1-6"
RETIRED = ("Selected cells", "Engineered cells", "Today's cells", "Today’s cells", "Central case", "Best case", "best case", "central case")
OWNER_JUDGED = re.compile(r"Pablo's odds|Pablo’s odds|re-judged by Pablo|the author judges|the author's judgement|the author thinks|"
                          r"the owner judges|the owner thinks|Pablo judges|Pablo thinks|the author puts|the author chose|the owner puts|"
                          r"the owner chose", re.I)
TODAY_COST = re.compile(r"today['’]s dollars|in today['’]s\b|\$[\d.,]+[^.<]{0,40}\btoday\b|\btoday\b[^.<]{0,25}\$\d", re.I)


def _page_strings(html: str) -> str:
    """Everything a reader can see once the scripts have run: the static text, the tooltips and alt texts, and the string literals of
    the page's scripts (what they write into the page), with the code's comments taken out."""
    attrs = " ".join(re.findall(r'(?:title|alt|aria-label|data-tip|data-help)="([^"]*)"', html))
    js = " ".join(b for _a, b in re.findall(r"<script([^>]*)>(.*?)</script>", html, flags=re.S))
    js = re.sub(r"/\*.*?\*/", " ", js, flags=re.S)
    js = re.sub(r"(?m)(^|[;{}\s])//[^\n]*", " ", js)
    lits = " ".join(m.group(2) for m in re.finditer(r"(['\"])((?:\\.|(?!\1).){3,}?)\1", js) if " " in m.group(2))
    return attrs + " " + lits


def _check_words(html: str, vis: str) -> list:
    fails = []
    body = html[html.find("<body"):]
    every = vis + " " + _page_strings(body)
    for bad in RETIRED:
        if bad in every:
            fails.append(f"a retired name is on the page: {bad}")
    for bad in ("everyday meat", "average kilo", "Level 1", "Level 6", "the reference case", "The reference case", "the reference tank"):
        if bad in every:
            fails.append(f"the page still says '{bad}'")
    for m in TODAY_COST.finditer(every):
        fails.append(f"a cost is said in today's dollars, not 2025 dollars: ...{every[max(0, m.start() - 60):m.end() + 40]}...")
    for m in OWNER_JUDGED.finditer(every):
        fails.append(f"a judgement is attributed to the owner: ...{every[max(0, m.start() - 60):m.end() + 40]}...")
    if "\u2014" in vis:
        fails.append("an em dash in the page's visible text")
    for m in re.finditer(r'<details class="level[^"]*" id="(\w+)">\s*<summary>(.*?)</summary>', html, flags=re.S):
        if 'class="lv"' in m.group(2) or "Level " in m.group(2):
            fails.append(f"level #{m.group(1)} is still labelled by its number")
    return fails


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
        fails.append("the first screen should run: the opening, the levers at the side (cells, reactor, medium, shoppers), then the results beside them (tank, reactors, cost, share), then what it would take")
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
                 'class="chain"', 'onclick="fxApply()"', 'id="sc_switches"', 'id="fxwrap"', 'id="fx_sc"', 'id="fx_sp"', 'fxFromScenario', 'fxSpecies(',
                 'oninput="fxRender()"'):
        if gone in html:
            fails.append(f"the page still carries a piece the rebuild cut: {gone}")

    # --- names and words
    for bad in ("Today's cells", "Today’s cells", "today's cells", "today’s cells"):
        if bad in html:
            fails.append(f"the old case name is still on the page: {bad}")
    for bad in ("Selected cells", "selected cells", "Engineered cells", "engineered cells", "Where your cells land", 'id="pl_cpl"', 'id="pl_perf"'):
        if bad in html[html.find("<body"):html.find("<script", html.find("<body"))] or bad in vis:
            fails.append(f"a retired name or control is still on the page: {bad}")
    for bad in ("Central case", "Best case", "best case", "the default cost", "the reference case", "The short version", "Rung ",
                "forecast for 2035", "Forecast for 2035", "2035 forecast", "author's odds"):
        if bad in vis:
            fails.append(f"the visible text still says: {bad}")
    bare_vis = vis
    for n in CASE_NAMES + ("Humbird's optimistic design", "Bioengineering", "engineering design", "Engineering"):
        bare_vis = bare_vis.replace(n, "")
    for m in ROUTE_WORDS.finditer(bare_vis):
        fails.append(f"the page's static text names a route: ...{bare_vis[max(0, m.start() - 80):m.end() + 40]}...")
    fails += _check_words(html, vis)
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
            point = HC.page_start()["total"] if name == "humbird_best" else S.reference()["total"]
        else:
            tr = {k: v for k, v in w["traits"].items()} if name.startswith("moved") else {}
            held = {"moved2": {"capex_x": 0.5, "medium_price": 0.1}}.get(name, {})
            point = S.run(w["choice"], **{k: tr[k] for k in tr if name.startswith("moved")}, **held)["total"]
        if abs(w["point"] - point) > 1e-6 * max(1.0, point):
            fails.append(f"{lab}: the most-likely-values cost is {w['point']:.4f}, the model gives {point:.4f}")
        # the cost shown is the cost at the settings shown (the author, 2026-11-19: "just leave the point for simplicity"); the draws
        # are under "How uncertain is this cost", with what is varied and by how much
        if abs(w["cost"] - w["point"]) > 1e-12:
            fails.append(f"{lab}: the cost shown is {w['cost']:.4f}, not the cost at the settings shown ({w['point']:.4f})")
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
        for want in ("1% of the world's meat and seafood", "in the shop it would cost", "the price of chicken mince ($", "a kilo in the world)",
                     "of the cost scales with", "of meat buyers would pick it at the same price", "plant protein" if w["cut"] < 1 else "all cells"):
            if want not in deck:
                fails.append(f"{lab}: the sentence does not say '{want}': {deck[:240]}")
        ws_ = {k: _text(v) for k, v in w["words"].items()}
        bt = f"{w['buyers'] * 100:.1f}".rstrip("0").rstrip(".") + "% of meat buyers"
        for k, want in (("tp_cl_note", "Each kind of meat has its own price"), ("tp_cl_note", "same shop price as chicken mince at $"),
                        ("tp_cl_note", "a kilo in the shop)"), ("tp_cl_note", "These costs are the dashed lines on the map"), ("tp_groups_sub", "every estimate at its most likely value"),
                        ("tp_groups_say", "1% of"), ("tp_groups_say", bt), ("tp_groups_table", "litres a kilo of cells"), ("tp_animals_sub", "at the cost of"),
                        ("tp_animals_total", "Plant-based meat: about"), ("tp_animals_total", "by weight of cells"), ("tp_animals_say", "of its sales"),
                        ("tp_groups_alt", "split by what drives the cost"),
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
    for name, w in cases:
        for t in [w["deck"]] + [v for k, v in w["words"].items() if k in ("tp_cl_note", "tp_cl_alt")]:
            if "average kilo" in t or "everyday meat" in t:
                fails.append(f"{name}: a meat price is quoted without naming the kind of meat: {t[:200]}")
            if "8 in 10" in t or "draws" in t:
                fails.append(f"{name}: the first screen's cost words still speak of draws: {t[:200]}")
    # one kind of meat at the same price: the share is the setting (the author, 2026-11-19: "at price parity, the 50% curve should cut
    # the 50% preference"); it holds for one product and cannot hold for a sum over meats with different prices
    for b, x in probe["same"]:
        if abs(b - x) > 2e-4:
            fails.append(f"at the same price {b:.1%} of meat buyers should pick it; the page's curve gives {x:.4%}")
    # the further settings (PAGE_PARAMS): finite at both ends, and freed or set to their own value they change nothing
    if probe["npar"] != len(BI.PAGE_PARAMS) or probe["npar"] < 18:
        fails.append(f"the page carries {probe['npar']} further settings; build_interactive.PAGE_PARAMS has {len(BI.PAGE_PARAMS)}")
    moved = set()
    for r in probe["params"]:
        if not all(isinstance(r[k], (int, float)) and r[k] == r[k] and 0 < r[k] < 1e6 for k in ("lo", "hi", "back", "same")):
            fails.append(f"setting {r['key']} from {r['ref']}: a cost is not a finite number ({r})")
            continue
        if abs(r["back"] - r["base"]) > 1e-9 * r["base"]:
            fails.append(f"setting {r['key']} from {r['ref']}: freed, the cost is {r['back']:.6f}, it started at {r['base']:.6f}")
        if abs(r["same"] - r["base"]) > 1e-6 * r["base"]:
            fails.append(f"setting {r['key']} from {r['ref']}: set to its own starting value the cost is {r['same']:.6f}, not {r['base']:.6f}")
        if abs(r["lo"] - r["hi"]) > 1e-6 * r["base"]:
            moved.add(r["key"])
    # 2026-11-21: the slower oxygen uptake of a thick culture moves none of the four starting points any more. Humbird's design is
    # held by CO2, the published cells by their waste, and the low-lactate and all-favourable examples now feed oxygen through
    # their column loop (the oxygen-feeding loop held thinner wins the design search), so oxygen binds in none of them
    still = {q[0] for q in BI.PAGE_PARAMS} - moved - {"kla_exp"}
    if still:
        fails.append(f"these settings move no cost from either starting point: {sorted(still)}")
    for r in probe["vessels"]:
        if abs(r["page"] - r["cell"]) > 1e-6 * r["cell"]:
            fails.append(f"{r['v']} run as {r['m']}: the page gives {r['page']:.4f}, the vessel table {r['cell']:.4f}")
    if len(probe["vessels"]) < 20:
        fails.append("the vessel and mode choices should cover the vessel table")
    for r in probe["devices"]:
        if abs(r["page"] - r["rt"]) > 1e-9 * r["rt"]:
            fails.append(f"retention device {r['d']}: the page gives {r['page']:.4f}, retention gives {r['rt']:.4f}")
    # the page opens on the best the model can find, as a range, and on no other cost or share (the author, 2026-11-19)
    lead = probe["lead"]
    for want in (f"${probe['floor']:.0f} at feed-grade prices", f"about ${probe['frontier']:.0f} a kilo", "Companies say their own cells do better", "chicken mince", "beef steak"):
        if want.lower() not in lead.lower():
            fails.append(f"the opening sentence does not say '{want}': {lead[:240]}")
    if re.search(r"\d%", lead.replace("to within about 2%", "")) or f"${probe['refs']['today']['cost']:.0f}" in lead:
        fails.append(f"the opening sentence gives a share or the published cells' cost: {lead[:240]}")
    # the opening says where the levers start (the owner, 2026-11-20): Humbird's best estimate, reproduced to within about 2%
    for want in ("The levers start at the best estimate of Humbird's 2021 analysis", "reproduces to within about 2%", "“Published cells” loads the best values published for meat cells instead"):
        if want not in lead:
            fails.append(f"the opening does not say '{want}': {lead[-400:]}")
    if lead.count("<p>") != 3:
        fails.append("the opening should be three short paragraphs")
    # 2.5% since 2026-11-20: his plant is no longer entered (the engine's own gives $20.65 against his $21.00)
    if abs(HC.reproduce(HC.BEST, "2018")["total"] / HC.HIS[HC.BEST]["total"] - 1.0) > 0.025:
        fails.append("the engine no longer reproduces Humbird's best estimate to within about 2%: change the opening's words")
    if not (0 <= html.find('id="deck"') < html.find('id="levers"') < html.find('id="sumbar"')):
        fails.append("the readout of the reader's settings should come after the opening and the levers, not lead the page")
    # cleaning and reusing the medium: every route and the leaner wash feed give a finite cost; off, they change nothing; a route
    # at the share that costs least never costs more than none; its lines in the cost breakdown add up to the total
    import floor_physics as FP
    import medium_reuse as MR
    import math
    from inputs import value
    if probe["cleanOrder"] != list(FP.CLEAN_NAMES) or set(probe["cleanTexts"]) != set(MR.page_routes()):
        fails.append(f"the page's cleaning routes {probe['cleanOrder']} are not floor_physics.CLEAN_NAMES")
    for r in probe["clean"]:
        tag = f"cleaning the medium, {r['ref']}, {r['route']}"
        if any(r[k] is None or not math.isfinite(r[k]) or r[k] <= 0 for k in ("best", "half", "picked", "back")):
            fails.append(f"{tag}: not a finite cost ({r})")
            continue
        if r["back"] != r["base"]:
            fails.append(f"{tag}: turned off again the cost is {r['back']!r}, it started at {r['base']!r}")
        if r["route"] == "none" and (r["best"] != r["base"] or r["half"] != r["base"]):
            fails.append(f"{tag}: 'none' should give the starting cost back exactly")
        if r["best"] > r["base"] + 1e-9 or abs(r["picked"] - r["best"]) > 1e-9:
            fails.append(f"{tag}: at the share that costs least it costs {r['best']:.4f} (the lever's own start {r['picked']:.4f}), none costs {r['base']:.4f}")
        if abs(r["gsum"] - r["gtotal"]) > 1e-6 * r["gtotal"]:
            fails.append(f"{tag}: the cost breakdown adds up to {r['gsum']:.4f}, the total is {r['gtotal']:.4f}")
    if abs(value("pf_wash_price") - (value("glucose_intensity") * value("glucose_price") + value("other_nutrients_floor")) / value("pf_medium_l_floor")) > 5e-4:
        fails.append("pf_wash_price is no longer (glucose + salts, buffer and trace elements a kilo of cells) / the litres that carry a kilo's nutrients")
    for k, t in MR.page_routes().items():
        if k != "none" and not (t["what"] and t["shown"] and t["limits"]):
            fails.append(f"cleaning route {k}: the page needs what it is, what has been shown and what limits it")
    # the reference values under the levers: each belongs to a lever and sits inside its slider's range
    rng = {q[0]: (q[8], q[9]) for q in BI.PAGE_PARAMS}
    rng.update({k: (v[2], v[3]) for k, v in BI.TRAIT_PAGE.items()})
    rng.update({"capex_x": (0.0, 3.0), "medium_price": (0.0, 1.40), "wash_price": (0.0, 1.40), "buyers": (1.0, 99.0), "cut": (0.0, 90.0), "displaced": (0.0, 1.0),
                "closed": (0.0, float(len(mm.CLOSED_LEVELS) - 1))})   # the closed-market lever: a level of meat_market.closed_share
    for k, refs in BI.LEVER_REFS.items():
        if k not in rng:
            fails.append(f"reference values are given for '{k}', which is not a lever")
            continue
        for v, who in refs:
            if not (rng[k][0] - 1e-9 <= v <= rng[k][1] + 1e-9) or not who:
                fails.append(f"lever {k}: the reference {v} ({who}) is outside its slider ({rng[k][0]} to {rng[k][1]})")
    if len(BI.LEVER_REFS) < 20:
        fails.append("most levers should carry published reference values")
    # the level on the tank and the plant: its result card gives the side bar's cost; the address keeps the settings that moved there
    for i, w in enumerate(probe["l4"]):
        if abs(w["res"] - w["point"]) > 1e-12 or f"${w['point']:.1f} a kilo of cells" not in w["text"]:
            fails.append(f"the level on the tank and the plant (case {i}) does not show the side bar's cost ${w['point']:.2f}: {w['text'][:160]}")
    hs = probe["hash"]
    if abs(hs["after"] - hs["before"]) > 1e-9 * hs["before"] or hs["pc"][0] != hs["pc"][1] or hs["it"][0] != hs["it"][1]:
        fails.append(f"the address does not carry the class of plant, its items or the new levers: {hs}")
    oh = probe["oldhash"]
    if not (oh["base"] == "switches" and oh["dh"] == 30 and oh["cx"] == 0.8 and oh["pc"] is None and 0 < oh["cost"] < 1e6):
        fails.append(f"a link written before 2026-11-22 no longer reads: {oh}")
    eng = html[html.find('<details class="level" id="engineering">'):html.find('<details class="level" id="shoppers">')]
    ctl = [m for m in re.findall(r'<(?:input|select)[^>]*id="(\w+)"', eng) if m not in ("sc_ga", "sc_gb")]
    if ctl:
        fails.append(f"the level on the tank and the plant should show results only (the side bar sets them), but it has controls: {ctl}")
    if "side bar sets everything in this section" not in _text(eng):
        fails.append("the level on the tank and the plant should say that the side bar sets it")
    if probe["start"] != "humbird_best" or probe["shown"] != ["humbird_best", "today", "best"]:
        fails.append(f"the page should open on Humbird's best estimate and offer it, the published cells and the all-favourable example (got {probe['start']}, {probe['shown']})")
    fails += _check_start(probe, html, vis)
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

    # --- conventional meat's price response and the markets closed by law behave as their help says (2026-11-20)
    mk = probe["mk"]
    vals = list(mk["es"].values()) + mk["closed"] + [mk["custom"], mk["back"], mk["cback"]]
    if not all(isinstance(v, (int, float)) and 0 < v < 100 for v in vals):
        fails.append(f"the meat-price or closed-market lever gives a share that is not a finite positive number: {mk}")
    elif abs(mk["back"] - mk["s0"]) > 1e-12 or abs(mk["cback"] - mk["s0"]) > 1e-12:
        fails.append(f"set back to the model's value, the meat-price or closed-market lever does not give the start ({mk})")
    else:
        e = mk["es"]
        if not (e["0.5"] < e["2"] < e["10"] < e["Infinity"]):
            fails.append(f"a less elastic supply should lower conventional meat's price more and the share with it: {e}")
        if any(b > a + 1e-12 for a, b in zip(mk["closed"], mk["closed"][1:])) or not mk["custom"] < mk["closed"][0]:
            fails.append(f"closing more of the market should never raise the share: {mk['closed']}, 30% closed {mk['custom']}")
    # the help's figure: a supply elasticity of 2 lowers the price by about 4% for each 10% of the market taken
    if abs((1 - 0.9 ** (1 / (2 - mk["demand"]))) - 0.04) > 0.005:
        fails.append("the meat-price lever's help ('about 4% for each 10% of the market') no longer holds")

    # --- what it would take: the model's table
    py = S.what_it_would_take()
    if len(py) != len(probe["wit"]):
        fails.append("'What it would take' does not carry the model's rows")
    for a, b in zip(py, probe["wit"]):
        if a["target"] != b["target"] or abs(a["buyers"] - b["buyers"]) > 1e-12 or (a["need"] is None) != (b["need"] is None) \
                or (a["need"] is not None and abs(a["need"] - b["need"]) > 1e-9) or (a["pick"] is None) != (b["pick"] is None):
            fails.append(f"'What it would take' row {a['target']}% at {a['buyers']:.1%} differs from scenarios.what_it_would_take")
    return fails


def _check_start(probe: dict, html: str, vis: str) -> list:
    """The page opens exactly on Humbird's best estimate (2021) in today's dollars: the engine's like-for-like figure of the
    back-test (humbird_check.reproduce, page_start), with every lever showing the value the engine actually uses, so that moving
    nothing, or setting a lever to what it shows, leaves the cost where it is. What this model counts and he does not (a least
    medium flow, bubble deaths, a harvest loss, the protectant) are levers that start at his value, none, and one button
    switches them on (the owner, 2026-11-20: "stick to Humbird design unless he missed something important")."""
    from inputs import value
    fails = []
    o, py, like = probe["open"], HC.page_start(), HC.reproduce(HC.BEST, "today")
    kw, over = HC.conditions(HC.BEST, "today")
    tr, fin = HC.page_traits(), HC.page_finance()
    if o["ref"] != "humbird_best" or o["base"] != "humbird" or o["hbKey"] != "humbird_best" or o["refLabel"] != "Humbird's best estimate (2021)":
        fails.append(f"the page should open on Humbird's best estimate (2021), got {o['ref']}, {o['base']}, {o['hbKey']}, {o['refLabel']}")
    # the start cannot drift from the back-test: the page's own JavaScript gives the like-for-like figure in today's dollars
    if abs(o["total"] - like["total"]) > 1e-6 * like["total"] or abs(py["total"] - like["total"]) > 1e-12:
        fails.append(f"the start costs {o['total']:.6f} on the page; humbird_check's like-for-like figure in today's dollars is {like['total']:.6f}")
    if abs(probe["refs"]["humbird_best"]["point"] - o["total"]) > 1e-12:
        fails.append("loading Humbird's best estimate again should give the cost the page opened on")
    if abs(o["density"] - like["density"]) > 1e-6 * like["density"] or o["limit"] != like["limit"]:
        fails.append(f"the start's culture is {o['density']:.2f} g/L ({o['limit']}), the back-test's {like['density']:.2f} ({like['limit']})")
    # the four traits, the selects and the medium: what is shown is what the engine is given
    for k, v in tr.items():
        if abs(o["traits"][k] - v) > 1e-12 or abs(o["params"][k] - v) > 1e-12 or abs(v - HC.START_TRAITS[k]) > 5e-3 * abs(HC.START_TRAITS[k]):
            fails.append(f"start, trait {k}: shown {o['traits'][k]}, the engine takes {o['params'].get(k)}, his cell is {v}")
    vm = o["params"].get("vm") or {}
    if o["mode"] != "fedbatch" or o["vessel"] != "stirred" or vm.get("kind") != "cyclic" or o["washed"]:
        fails.append(f"the start should be a stirred tank run as a fed-batch (got {o['vessel']}, {o['mode']}, {vm})")
    if o["plant"] != "pharma" or o["params"].get("plant") != "pharma" or o["params"].get("items"):
        fails.append(f"the start should be the plant with clean rooms (select {o['plant']}, engine {o['params'].get('plant')})")
    if o["clean"] != "none" or o["params"].get("clean") not in (None, "none"):
        fails.append("the start should not clean the medium")
    if abs(o["medium"] - py["medium_price"]) > 1e-9 or o["params"].get("growth_factors") != 1.0 or not 0.0 < o["medium"] <= 1.40:
        fails.append(f"the start's medium should be his cost per litre with growth factors bought (got {o['medium']}, {o['params'].get('growth_factors')})")
    if abs(o["params"]["vessel_m3"] - 20.0) > 1e-12:
        fails.append("the start's tank should be 20 m3")
    # what is his and has no lever: his plant's cost, his filter sets a batch, no antifoam effect, his count of the end of a batch,
    # growth at full speed to the end, no extra medium-preparation equipment, no lost runs
    fxo = o["params"].get("fxo") or {}
    # since 2026-11-20 his plant is the engine's own (no plant cost entered): the plant class is his, pharma-style
    if o["params"].get("capex_2018") is not None or kw.get("plant") != "pharma":
        fails.append("start: the plant should be the engine's own pharma-style plant, with no plant cost entered")
    his = {"cons_run": (vm.get("cons_run"), kw["vm"]["cons_run"]),
           "antifoam_otr": (o["params"].get("antifoam_otr"), over["pf_antifoam_otr"]), "batch_end": (fxo.get("batch_end"), over["pf_batch_end_x"]),
           "batch_half": (fxo.get("batch_half"), over["pf_batch_half_x"]), "medium_prep_exp": (fxo.get("medium_prep_exp"), over["pf_medium_prep_exp"]),
           "consumables": (fxo.get("consumables"), over["pf_consumables_low"]), "hazard": (o["params"].get("hazard", 0.0), kw["hazard"])}
    for k, (got, want_) in his.items():
        if got is None or abs(got - want_) > 1e-12 * max(1.0, abs(want_)):
            fails.append(f"start: {k} should be Humbird's ({want_}), the page's engine is given {got}")
    if set(over) != {"pf_harvest_recovery", "pf_protectant_dose", "pf_antifoam_otr", "pf_medium_prep_exp", "pf_batch_half_x", "pf_consumables_low", "pf_batch_end_x"}:
        fails.append(f"humbird_check.conditions sets inputs this test does not follow to the page: {sorted(over)}")
    # the finance levers: his 7.5% over 10 years and the rest of his 23.6% a year, and that is the charge the engine uses
    crf = fin["rate"] / 100.0 / (1.0 - (1.0 + fin["rate"] / 100.0) ** -fin["life"])
    if o["fin"] != fin or abs(o["charge"] - value("humbird_plant_charge")) > 1e-12 or abs(crf + fin["upkeep"] / 100.0 - o["charge"]) > 1e-12 \
            or abs(fin["upkeep"] - 9.0) > 0.05 or (fin["rate"], fin["life"]) != (7.5, 10.0):
        fails.append(f"the start's finance levers should show {fin} and give the engine his {value('humbird_plant_charge')} (got {o['fin']}, {o['charge']})")
    # every further lever: the value it shows is the engine's own argument or datasheet constant at the start. The model's four
    # additions start at Humbird's value, none
    want = {"nh3_limit": 5.0, "lac_limit": 50.0, "pco2": 100.0, "gas_v": 6.0, "tank_m3": 20.0, "fin_rate": 7.5, "fin_life": 10.0, "fin_upkeep": fin["upkeep"],
            "min_perfusion": 0.0, "kla_exp": 0.0, "mature_d": 0.0, "osm_limit": value("pf_osm_limit"), "maint": value("pf_maintenance_share") * 100.0,
            "killx": 0.0, "o2x": 1.0, "labourx": 1.0, "energyx": 1.0, "gfx": 1.0, "harvest_loss": 0.0,
            "protect_dose": 0.0, "protect_price": value("pf_protectant_price"), "aa_price": value("aa_bulk_price"),
            "glucose_price": value("glucose_price"), "mem_price": value("rt_membrane_price"), "mem_life": value("rt_membrane_life"),
            "flux": value("rt_flux_lmh"), "kla": value("ge_kla_20m3"),
            "x_cap": value("pf_x_visc"),                 # the densest culture allowed starts at the model's own limit, so nothing moves
            "spargers": 1.0, "col_loop": 0.0,            # 2026-11-21: one sparger, no column on the filter loop, as in his design
            # 2026-11-22 (fifth batch): the settings that moved into the side bar from "Every cell and tank setting". Each shows the
            # engine's own value at his design: his growth factors bought at his price, glucose from his cell's own balance, no fat fed,
            # no lost runs, the engine's restart after a loss and run length, his top pressure, the column's design outlet, the
            # dissolved oxygen his oxygen supply implies, and the model's pH
            "gf_buy": 100.0, "glc_kg": py["lac_kg"] / tr["lac_yield"], "fat_fed": 0.0, "lipid_share": 15.0, "hazard": 0.0,
            "restart_fail": value("pf_run_days") * (1.0 / value("pf_uptime_realistic") - 1.0), "run_days": value("pf_run_days"),
            "p_top": value("ge_p_top_base"), "col_pout": value("ge_col_pout"),
            "do_mmol": __import__("gas_exchange").headspace_pressure()["c_liquid_implied"], "ph": value("pf_ph")}
    for lv in o["levers"]:
        k = lv["key"]
        if k not in want:
            fails.append(f"start: lever {k} has no expected value in this test")
        elif abs(lv["shown"] - want[k]) > 1e-9 * max(1.0, abs(want[k])):
            fails.append(f"start: lever {k} shows {lv['shown']}, the engine uses {want[k]}")
        if lv["kind"] == "kw":                                    # an engine argument: the one passed, or the engine's own default
            arg = o["params"].get(lv["arg"])
            if arg is not None and abs(arg * lv["scale"] - lv["shown"]) > 1e-9 * max(1.0, abs(lv["shown"])):
                fails.append(f"start: lever {k} shows {lv['shown']}, the engine is given {arg * lv['scale']}")
        if not (lv["min"] - 1e-9 <= lv["shown"] <= lv["max"] + 1e-9):
            fails.append(f"start: lever {k} shows {lv['shown']}, outside its slider ({lv['min']} to {lv['max']})")
    if o["params"].get("min_perfusion") != 0 or fxo.get("kill") != 0 or fxo.get("harvest_loss") != 0 or fxo.get("protect_dose") != 0:
        fails.append(f"start: the engine should be given no least flow, bubble deaths, harvest loss or protectant (got {o['params'].get('min_perfusion')}, {fxo})")
    # ... with the case itself: the datasheet's constants, which every other figure on the page reads, stay the model's own
    if (o["fx"]["kill"], o["fx"]["harvest_loss"], o["fx"]["protect_dose"]) != (value("ge_kill_protected"), 1.0 - value("pf_harvest_recovery"), value("pf_protectant_dose")):
        fails.append(f"the start should not change the datasheet's constants for the rest of the page (got {o['fx']})")
    # explore()'s own defaults for the limits the start leaves out are Humbird's (so the levers above are the engine's)
    if (value("pf_nh3_limit"), value("pf_lac_limit"), value("pf_pco2_limit"), value("pf_gas_velocity")) != (kw["nh3_limit"], kw["lac_limit"], kw["pco2_mbar"], kw["gas_velocity"]):
        fails.append("the engine's own limits are no longer Humbird's: the start must pass his")
    for k, t in o["same"] + o["sameTraits"]:
        if abs(t - o["total"]) > 1e-9 * o["total"]:
            fails.append(f"start: lever {k} set to the value it shows moves the cost from {o['total']:.6f} to {t:.6f}")
    # --- the button "Add what this model counts and he does not": the four levers at the model's own values, and back
    a, four = probe["adds"], [x[0] for x in HC.PAGE_ADDITIONS]
    model = {"kla_exp": value("tc_kla_exp"), "min_perfusion": value("pf_min_perfusion"), "killx": 1.0, "harvest_loss": (1.0 - value("pf_harvest_recovery")) * 100.0, "protect_dose": value("pf_protectant_dose")}
    padd, pall = HC.page_additions(), HC.page_with_additions()["total"]
    if not a["start"]["has"] or a["start"]["on"] or abs(a["start"]["total"] - o["total"]) > 1e-12 or a["start"]["ref"] != "humbird_best":
        fails.append("loading Humbird's best estimate should give the start, with the button off")
    for k in four:
        if abs(a["model"][k] - model[k]) > 1e-9 or abs(a["on"]["levers"][k] - model[k]) > 1e-9 or a["start"]["levers"][k] != 0 or a["off"]["levers"][k] != 0 or a["again"]["levers"][k] != 0:
            fails.append(f"addition {k}: it should start at 0, be {model[k]} after the button and 0 after a second click or a reload "
                         f"(got {a['start']['levers'][k]}, {a['on']['levers'][k]}, {a['off']['levers'][k]}, {a['again']['levers'][k]})")
        if abs(a["today"]["levers"][k] - model[k]) > 1e-9:
            fails.append(f"Published cells keeps the model's own estimates on: lever {k} shows {a['today']['levers'][k]}, the model's is {model[k]}")
    if not a["on"]["on"] or abs(a["on"]["total"] - pall) > 1e-6 * pall or abs(a["live"]["all"] - pall) > 1e-6 * pall:
        fails.append(f"after the button the page costs {a['on']['total']:.6f} (its text says {a['live']['all']:.6f}); humbird_check.page_with_additions gives {pall:.6f}")
    if a["off"]["on"] or a["off"]["held"] or abs(a["off"]["total"] - o["total"]) > 1e-12 or abs(a["live"]["base"] - o["total"]) > 1e-12:
        fails.append(f"a second click should put Humbird's values back (cost {a['off']['total']:.6f}, levers still set: {a['off']['held']})")
    if len(a["live"]["rows"]) != len(padd):
        fails.append("the text beside the button should list every addition")
    for row, (key, name, d) in zip(a["live"]["rows"], padd):
        # the viscosity lever adds nothing at his fed-batch, whose 120 g/L is held by CO2 (2026-11-20)
        # 2026-11-21: nor does the least medium flow, whose cap in his batch is now 1.35 x 92 = 124 g/L
        if row["key"] != key or row["name"] != name or abs(row["adds"] - d) > 1e-6 * pall or (d <= 0 and key not in ("kla_exp", "min_perfusion")):
            fails.append(f"addition {key}: switched on alone the page says it adds {row['adds']:.4f}, humbird_check.page_additions {d:.4f}")
        if (f"${d:.1f} a kilo." not in a["text"] and not (abs(d) < 0.05 and "nothing at these settings" in a["text"])) or name not in a["text"]:
            fails.append(f"the text beside the button does not say what '{name}' adds (${d:.1f} a kilo): {a['text']}")
    # 2026-11-21: 37.38 -> 30.49 (the least medium flow no longer caps his batch at 92 g/L)
    if not pall > o["total"] + 3.0 or abs(pall - 30.49) > 0.005 * 30.49:
        fails.append(f"with the five additions on, his design costs {pall:.2f} (pinned 30.49; 37.38 before 2026-11-21, 37.51 before the engine's own plant)")
    # loading Published cells after Humbird's start, and the reverse, resets every lever
    b, b0, a3 = a["today"], a["today0"], a["again"]
    if b["held"] or b["has"] or b["base"] != "switches" or b["ref"] != "today" or abs(b["total"] - b0["total"]) > 1e-12 or abs(b["total"] - probe["refs"]["today"]["point"]) > 1e-12 \
            or any(abs(b["levers"][k] - b0["levers"][k]) > 1e-12 for k in b0["levers"]) or (b["fx"]["kill"], b["fx"]["harvest_loss"], b["fx"]["protect_dose"]) != \
            (value("ge_kill_protected"), 1.0 - value("pf_harvest_recovery"), value("pf_protectant_dose")):
        fails.append(f"loading Published cells after Humbird's start with levers moved should reset every lever to the model's own (got {b})")
    if a3["held"] or a3["on"] or a3["ref"] != "humbird_best" or abs(a3["total"] - o["total"]) > 1e-12 or any(abs(a3["levers"][k] - a["start"]["levers"][k]) > 1e-12 for k in a3["levers"]):
        fails.append(f"loading Humbird's best estimate after Published cells with a lever moved should give the start back (got {a3})")
    # "How this is worked out, and how to check it" (the owner, 2026-11-24): one closed box under each main result, every marker
    # filled, each with its four parts, and every file it links to present in the repository
    if "<!--VERIFY:" in html:
        fails.append("a verification box marker was not filled")
    import page_verify
    n_boxes = html.count('<details class="verify">')
    # the verdicts follow from the numbers: the choice experiment's elasticity sits inside its arms' range at the model's settings
    if ">Cultivated meat at first contact and equal price: own-price elasticity</td>" in html and \
            not re.search(r"own-price elasticity</td>(?:<td>[^<]*(?:<[^>]+>[^<]*)*</td>){3}<td>agrees</td>", html):
        fails.append("the share map's box does not say the choice-experiment check agrees")
    if n_boxes != 6:
        fails.append(f"{n_boxes} verification boxes on the page; 6 expected")
    for part in ("How it is worked out", "What it rests on", "Checked against", "Check it yourself"):
        if html.count(f'<p class="vh">{part}</p>') != n_boxes:
            fails.append(f"a verification box lacks the part '{part}'")
    for path in set(re.findall(r'href="' + re.escape(page_verify.GH) + r'([^"]+)"', html)):
        if not os.path.exists(os.path.join(ROOT, path)):
            fails.append(f"a verification box links to {path}, which is not in the repository")
    for anchor in set(re.findall(r"pgOpenTo\('([^']+)'\)", html)):
        if f'id="{anchor}"' not in html:
            fails.append(f"a verification box links to #{anchor}, which is not on the page")
    for w in ('id="tp_adds_btn"', ">Add what this model counts and he does not</button>"):
        if w not in html:
            fails.append(f"the page has no button to add what this model counts: '{w}'")
    if not (0 <= html.find('id="tp_refs"') < html.find('id="tp_adds"') < html.find('id="tp_refnote"')):
        fails.append("the button for the model's additions should sit under the starting points, above the starting point's text")
    for k in four:
        refs_k = dict((round(v, 6), who) for v, who in BI.LEVER_REFS[k])
        if "this model's estimate" not in refs_k.get(round(model[k], 6), "") or "Humbird 2021" not in refs_k.get(0, ""):
            fails.append(f"lever {k} should carry the chips 'Humbird 2021' at 0 and 'this model's estimate' at {model[k]} (got {BI.LEVER_REFS[k]})")
    # the words: his own figure, the same in today's dollars, that the page starts there, that no meat cell has his cells' traits,
    # what this model would add and where to switch it on; never the old reference's name, a named kind of cell or a route
    txt = o["refText"]
    his, like18 = HC.HIS[HC.BEST], HC.reproduce(HC.BEST, "2018")
    for w in (f"${his['total']:.2f} a kilo of cells in 2018 dollars (his Table 4.7)", f"about ${HC.his_today()['total']:.0f} in 2025 dollars", "The page starts there",
              f"${like18['total']:.1f} in 2018 dollars", f"${like['total']:.1f} in 2025 dollars", "No meat cell has been shown to have these traits",
              "least flow of medium", "bubbles", "lost at harvest", "protectant", "each is a lever that starts at zero", "Add what this model counts and he does not",
              "filter sets", "fed-batch", "clean rooms", "soy hydrolysate", "7.5% over 10 years"):
        if w not in txt:
            fails.append(f"the start's text does not say '{w}': {txt}")
    if ROUTE_WORDS.search(txt) or re.search(r"Selected cells|Engineered cells", txt + a["text"]):
        fails.append(f"the start's text names a kind of cell or a route: {txt}")
    if "optimistic" in txt or "optimistic" in probe["refs"]["humbird_best"]["deck"] or "optimistic" in probe["refs"]["humbird_best"]["label"]:
        fails.append("the start is described as Humbird's optimistic design")
    if "humbird" in probe["pubs"] or "humbird_best" not in probe["pubs"] or "optimistic" in json.dumps(probe["publ"]):
        fails.append(f"the cost axis should mark Humbird's best estimate, not the perfusion variation (got {probe['pubs']})")
    old = BI.REF_TEXT["humbird"][1]
    if "variation on Humbird's cells, not a figure from his report" not in old:
        fails.append("the older reference should say it is this model's variation on his cells, not a figure from his report")
    # the lower level carries the back-test table
    for w in ("Humbird's best estimate (2021), line by line", "His count (the page's start)", f"${his['total']:.2f}", f"${like['total']:.2f}",
              f"${pall:.2f}", "All five of his designs"):
        if w not in html:
            fails.append(f"the section 'Published cost estimates, and the examples on this page' does not carry the back-test: '{w}'")
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
