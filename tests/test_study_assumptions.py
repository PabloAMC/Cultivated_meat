"""test_study_assumptions.py — Humbird's best estimate with one study's assumptions at a time (study_assumptions.py, page_studies.js).

Checks
  * every study entry has a citation, a system, a reported cost with its basis, and a source reference for each recorded assumption;
  * every modification's label reads "<Study> <year>[, where]: Humbird 2021 design but with ..." (or "his design but with ..." for
    Humbird's own), names the studies it is labelled with, and its lever settings name real levers and sit inside the sliders' ranges;
  * each modification alone gives a finite cost on Humbird's best estimate, and no settings gives the page's start
    (humbird_check.page_start); the panel shows the estimates below the most favourable case with the limits they break;
  * an assumption that cannot be represented carries a reason and no settings;
  * the words a reader sees follow the page's rules (no acronym for a cost study, no named kinds of cell, no route to a trait);
  * the page agrees: its own JavaScript (run under Node as tests/test_easy_view.py does, on the BUILT interactive.html, so run
    `python build_interactive.py` first) gives the same cost for each modification alone and for all together, to 1e-6 relative,
    and writing a modification into the page's state and taking it out again gives the same figures.

Runs as a script or under pytest.
"""
from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_interactive as BI  # noqa: E402
import floor_physics as fp  # noqa: E402
import retention  # noqa: E402
import scenarios as S  # noqa: E402
import study_assumptions as SA  # noqa: E402
import vessels  # noqa: E402
import test_easy_view as EV  # noqa: E402

TOL = 1e-6
LABEL = re.compile(r"^(?P<who>[^:]+): (Humbird 2021 design|his design) but with \S")
BAD_WORDS = re.compile(r"\bTEAs?\b|[Ss]elected cells|[Ee]ngineered cells|—")

PROBE = r"""
;(function(){
  const def={}; MODEL.sliders.forEach(s=>def[s.key]=s.default);
  Object.assign(state,def,{region:"global",income:C.REGION_INCOME.global}); KP=effConsts(state);
  const out=stCosts();
  // the page's own state: Humbird's design loaded, a modification written in, then taken out
  const load=()=>{ const r=tpRef(ST_KEY); SCS.ref=ST_KEY; SCS.from=ST_KEY; SCS.traits={}; SCS.held={}; SCS.vessel="stirred"; SCS.vmode=null;
    SCS.device="tff"; SCS.clean=tpCleanNone(); SCS.base="humbird"; SCS.hbKey=ST_KEY; SCS.hb=Object.assign({},r.hb); tpSetBuyers(r.buyers); };
  const pt=()=>{ PGS.cloud=null; tpExtraNow(); return tpEval(SCS,tpParams()).total; };
  load(); out.state=ST_MODS.map(m=>{ const before=ST_MODS.filter(stOn).length; stApplyTo(SCS,m.settings); const on=stOn(m), c=pt();
    const others=ST_MODS.filter(o=>o!==m&&stOn(o)&&!stClash(o,m)).length;
    stClear(SCS,m.settings); return {key:m.key, before:before, on:on, cost:c, others:others, off:stOn(m), back:pt()}; });
  SCS.base="switches"; out.off_humbird=ST_MODS.filter(stOn).length; load();
  // the starting sets: priced on a state built for the purpose, and written into the page's state as the buttons do
  out.sets=stSetCosts(); out.sets_state={}; ST_SETS.forEach(e=>{ load(); stApplyTo(SCS,e.settings); out.sets_state[e.key]=pt(); }); load();
  out.set_names=ST_SETS.map(e=>[e.key,e.label,e.name]);
  out.set_splits=stSplits();
  out.n=[ST_MODS.length, ST_NOTES.length, ST.studies.length];
  out.start=tpRef(ST_KEY).point; out.key=ST_KEY; out.fav=[ST.all_favourable, TP.frontier, ST.below.map(b=>b.name)];
  const host={innerHTML:""}; const gd=document.getElementById; document.getElementById=id=>id==="tp_studies"?host:gd.call(document,id);
  try{ stRender(); out.html=host.innerHTML; }catch(e){ out.html="ERROR "+e.message; } document.getElementById=gd;
  console.log=__realLog; console.log(JSON.stringify(out));
})();
"""


def _js() -> dict | None:
    node = shutil.which("node")
    if node is None:
        return None
    html = open(EV.HTML, encoding="utf-8").read()
    d = tempfile.mkdtemp(prefix="studies_")
    paths = {n: os.path.join(d, n) for n in ("model.js", "probe.js", "stub.js")}
    open(paths["model.js"], "w", encoding="utf-8").write(EV._model_js(html))
    open(paths["probe.js"], "w", encoding="utf-8").write(PROBE)
    open(paths["stub.js"], "w", encoding="utf-8").write(EV.STUB)
    try:
        out = subprocess.run([node, paths["stub.js"], paths["model.js"], paths["probe.js"]], capture_output=True, text=True, timeout=180)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    if out.returncode != 0:
        raise RuntimeError(f"the studies probe failed:\n{out.stderr or out.stdout}")
    return json.loads(out.stdout.strip().splitlines()[-1])


def _in_range(settings: dict) -> list:
    bad = []
    par = {p[0]: p for p in BI.PAGE_PARAMS}
    for k, v in settings.get("traits", {}).items():
        if k not in BI.TRAIT_PAGE:
            bad.append(f"no trait {k}")
            continue
        _n, _u, lo, hi, _st, scale, _h = BI.TRAIT_PAGE[k]
        if not lo - 1e-9 <= v * scale <= hi + 1e-9:
            bad.append(f"trait {k}={v * scale:g} is outside its slider {lo:g} to {hi:g}")
    for k, v in settings.get("held", {}).items():
        if k == "capex_x":
            lo, hi = S.MC_PRIORS["capex_x"][0], S.MC_PRIORS["capex_x"][2]
        elif k == "medium_price":
            lo, hi = 0.0, 1.40
        elif k in par:
            lo, hi = par[k][8], par[k][9]
        else:
            bad.append(f"no lever {k}")
            continue
        if not lo - 1e-9 <= v <= hi + 1e-9:
            bad.append(f"lever {k}={v:g} is outside its slider {lo:g} to {hi:g}")
    if "plant" in settings and settings["plant"] not in [st.key for st in S.setting.__globals__["SWITCHES"][3].settings]:
        bad.append(f"no plant {settings['plant']}")
    if "vm" in settings and (settings["vm"][0] not in vessels.VESSELS or settings["vm"][1] not in vessels.MODES):
        bad.append(f"no vessel and mode {settings['vm']}")
    if "device" in settings and settings["device"] not in retention.ORDER:
        bad.append(f"no retention device {settings['device']}")
    for k in settings:
        if k not in SA.LEVER_KINDS:
            bad.append(f"unknown kind of lever {k}")
    return bad


def check() -> list:
    fails = []
    # --- the studies
    for key, s in SA.STUDIES.items():
        for f in ("name", "citation", "system", "cost", "basis", "explains"):
            if not str(s.get(f, "")).strip():
                fails.append(f"{key}: no {f}")
        if not s["assumptions"]:
            fails.append(f"{key}: no assumptions recorded")
        for a in s["assumptions"]:
            if len(a) != 3 or not all(str(x).strip() for x in a):
                fails.append(f"{key}: an assumption without a value or a source reference: {a}")
            # a study known only from a company's announcement has no page: the dated announcement or press report is its reference
            elif not re.search(r"PDF page|Table|Section|Figure|Reaction|Abstract|Appendix|company announcement, |press report, ", a[2]):
                fails.append(f"{key}: the source reference names no page, table or section: {a}")
    # --- the modifications
    mods = SA.modifications()
    real = [m for m in mods if not m.get("not_representable")]
    if not 8 <= len(real) <= 15:
        fails.append(f"{len(real)} modifications; 8 to 15 expected")
    if len({m["key"] for m in mods}) != len(mods):
        fails.append("two modifications share a key")
    base = SA.cost({})
    import humbird_check as HC
    if abs(base - HC.page_start()["total"]) > 1e-9 * base:
        fails.append(f"no settings should give Humbird's best estimate, the page's start: {base} against {HC.page_start()['total']}")
    if any(k in m["label"] for m in mods for k in ("clean rooms of his own", "his own financing", "with fed-batch")):
        fails.append("a modification restates the base: his clean rooms, his financing and fed-batch are the starting point")
    py = {}
    for m in mods:
        mt = LABEL.match(m["label"])
        if not mt:
            fails.append(f"{m['key']}: the label should read '<Study> <year>: Humbird 2021 design but with ...': {m['label']}")
        else:
            who = mt.group("who")
            for name in m["study_names"]:
                if name not in who:
                    fails.append(f"{m['key']}: the label does not name {name} before the colon")
            if ("his design" in m["label"]) != (m["studies"] == ["humbird2021"]):
                fails.append(f"{m['key']}: 'his design' is for Humbird's own variants only")
        for s in m["studies"]:
            if s not in SA.STUDIES:
                fails.append(f"{m['key']}: no study {s}")
        for f in ("text", "own"):
            if not m.get(f, "").strip():
                fails.append(f"{m['key']}: no {f}")
        if m.get("not_representable"):
            if not m.get("reason", "").strip() or "{" in m["reason"] or m.get("settings"):
                fails.append(f"{m['key']}: an assumption that cannot be represented needs a reason and no settings")
            continue
        if not m.get("solid", "").strip():
            fails.append(f"{m['key']}: nothing on how solid the assumption is")
        if not SA.levers(m["settings"]):
            fails.append(f"{m['key']}: no lever settings")
        fails += [f"{m['key']}: {b}" for b in _in_range(m["settings"])]
        c = SA.cost(m["settings"])
        py[m["key"]] = c
        if not (math.isfinite(c) and c > 0):
            fails.append(f"{m['key']}: cost {c}")
        elif abs(c - base) < 1e-6:
            fails.append(f"{m['key']}: changes nothing on Humbird's design")
    t = SA.table()
    if [r["key"] for r in t["rows"]] != [m["key"] for m in real] or any(abs(r["cost"] - py[r["key"]]) > 1e-9 for r in t["rows"]):
        fails.append("table() does not carry each modification's own cost")
    # --- the starting sets: one study's assumptions together on Humbird's best estimate
    keys = {m["key"] for m in real}
    for e in SA.sets():
        if e["study"] not in SA.STUDIES or not set(e["mods"]) <= keys:
            fails.append(f"set {e['key']}: an unknown study or modification")
        elif any(e["study"] not in m["studies"] for m in real if m["key"] in e["mods"]):
            fails.append(f"set {e['key']}: a modification that is not this study's")
        for f in ("label", "name", "text", "own"):
            if not str(e.get(f, "")).strip():
                fails.append(f"set {e['key']}: no {f}")
        # a plant is repaid with interest (the owner, 2026-11-24): no set charges none, and one that changes a study's
        # financing says so under `corrected`
        if e["settings"]["held"].get("fin_rate", 7.5) < 5.0:
            fails.append(f"set {e['key']}: the plant is repaid at {e['settings']['held']['fin_rate']}% interest")
        # the audit (the owner, 2026-11-24: "make clear exactly what we modified from each TEA, so it is auditable"): every lever
        # the set moves has a row, every row's reason is one of the named kinds and cites where the study says it
        rows = e["audit_rows"]
        moved = {f"trait:{k}" for k in e["settings"].get("traits", {})} | {f"held:{k}" for k in e["settings"].get("held", {})} | \
                {k for k in ("vm", "device", "plant") if k in e["settings"]}
        missing = moved - {r["lever"] for r in rows}
        if missing:
            fails.append(f"set {e['key']}: levers it moves with no row in its audit: {sorted(missing)}")
        for r in rows:
            if r["why"] not in SA.AUDIT_KINDS:
                fails.append(f"set {e['key']}: '{r['item']}' has the reason '{r['why']}'")
            if r["why"] not in (SA.HUMBIRD,) and r["study"] != "not stated" and not re.search(
                    r"PDF page|Table|Section|Figure|Exhibit|Abstract|Appendix|company announcement|press report|as in his|his best", r["study"]):
                fails.append(f"set {e['key']}: '{r['item']}' does not say where the study gives it: {r['study']}")
        if e["study"] != "humbird2021" and not any(r["lever"] == "held:fin_rate" for r in rows) and \
                not any("financing" in r["item"].lower() for r in rows):
            fails.append(f"set {e['key']}: the audit does not say how the plant is repaid")
        # the long-term targets (the owner, 2026-11-24): no set keeps a lab run's doubling time or today's medium price
        if e["settings"]["traits"].get("doubling_h", SA.LT_DOUBLING_H) > 30.0:
            fails.append(f"set {e['key']}: cells doubling every {e['settings']['traits']['doubling_h']} hours, slower than any study projects")
        if e["study"] != "humbird2021" and e["settings"]["held"].get("medium_price", SA.LT_MEDIUM) > 0.60:
            fails.append(f"set {e['key']}: a medium at ${e['settings']['held']['medium_price']} a litre is today's price, not a long-term one")
        if SA.STUDIES[e["study"]]["name"] not in e["label"]:
            fails.append(f"set {e['key']}: the label does not name its study")
        fails += [f"set {e['key']}: {b}" for b in _in_range(e["settings"])]
        c = SA.cost(e["settings"])
        if not (math.isfinite(c) and c > 0) or abs(c - base) < 1e-6:
            fails.append(f"set {e['key']}: cost {c}")
    # the Pasitka set: the lactate the study measured for a kilo of cells, and the study's own plant cost
    rp = SA.result({e["key"]: e for e in SA.sets()}["pasitka"]["settings"])
    rg = SA.result({e["key"]: e for e in SA.sets()}["gourmey"]["settings"])
    if abs(rg["capex"] / SA.GOURMEY_CAPEX_K_M3 - 1.0) > 0.03:
        fails.append(f"the Gourmey set's plant costs ${rg['capex']:.0f}k per m³; the announcement's is ${SA.GOURMEY_CAPEX_K_M3:.0f}k: reset GOURMEY_CAPEX_X")
    # plant against running costs: every study's own split is positive and adds up to a plausible total; every set's split adds up
    for d in SA.splits_reported():
        if not (0 < d["plant"] < 100 and 0 < d["running"] < 100) or (d["set"] and d["set"] not in [e["key"] for e in SA.sets()] + ["humbird_best"]):
            fails.append(f"split {d['key']}: {d['plant']:.2f} and {d['running']:.2f}, set {d['set']}")
    for e in SA.sets():
        sp = SA.split(e["settings"])
        if abs(sp["plant"] + sp["running"] - SA.cost(e["settings"])) > 1e-9 * sp["total"] or sp["plant"] <= 0:
            fails.append(f"set {e['key']}: its plant and running costs do not add up to its cost: {sp}")
    if abs(rp["capex"] / (SA.PASITKA_CAPEX_K_M3 * SA.cpi(2024)) - 1.0) > 0.03:
        fails.append(f"the Pasitka set's plant costs ${rp['capex']:.0f}k per m³; the study's is ${SA.PASITKA_CAPEX_K_M3 * SA.cpi(2024):.0f}k: reset PASITKA_CAPEX_X")
    if len({e["key"] for e in SA.sets()}) != len(SA.SETS):
        fails.append("two starting sets share a key")
    # --- the words a reader sees
    pd = SA.page_data()
    seen = [(m["key"], " ".join(str(m.get(f, "")) for f in ("label", "text", "solid", "own", "reason"))) for m in pd["mods"]] + \
           [(s["key"], " ".join(s[f] for f in ("name", "system", "cost", "basis", "explains"))) for s in pd["studies"]] + \
           [(e["key"], " ".join([e[f] for f in ("label", "name", "text", "own")] + [r[k] for r in e["audit_rows"] for k in ("item", "study", "used")]))
            for e in pd["sets"]] + \
           [(d["key"], " ".join(d[f] for f in ("label", "basis", "how"))) for d in pd["splits"]] + \
           [("sets_not_offered", pd["sets_not_offered"])]
    for key, txt in seen:
        for rx in (BAD_WORDS, EV.ROUTE_WORDS):
            mt = rx.search(txt)
            if mt:
                fails.append(f"{key}: the words a reader sees contain '{mt.group(0)}': ...{txt[max(0, mt.start() - 60):mt.end() + 30]}...")
    # --- the page
    html = open(EV.HTML, encoding="utf-8").read() if os.path.exists(EV.HTML) else ""
    if not html:
        return fails + [f"{EV.HTML} missing: run `python build_interactive.py` first"]
    if not re.search(r'<details class="more" id="studies">\s*<summary>Why published cost studies disagree: Humbird\'s design with one '
                     r'study\'s assumptions at a time</summary>\s*<div id="tp_studies"', html):
        fails.append("the page has no collapsed #studies section holding #tp_studies")
    if "/*__ST_JS__*/" in html or "function stRender" not in html or 'onclick="stReset()"' not in html or "tpLoad(ST_KEY)" not in html:
        fails.append("page_studies.js is not in the built page")
    js = _js()
    if js is None:
        print("  (node not found: the page's figures were not checked)")
        return fails
    rel = lambda a, b: abs(a - b) / max(1.0, abs(a), abs(b))
    if js["n"] != [len(real), len(mods) - len(real), len(SA.STUDIES)]:
        fails.append(f"the page carries {js['n']} modifications, notes and studies; Python has {[len(real), len(mods) - len(real), len(SA.STUDIES)]}")
    if rel(js["base"], base) > TOL:
        fails.append(f"Humbird's design: python {base:.6f} page {js['base']:.6f}")
    for k, c in py.items():
        if k not in js["rows"] or rel(js["rows"][k], c) > TOL:
            fails.append(f"{k}: python {c:.6f} page {js['rows'].get(k)}")
    if rel(js["all"], t["all"]) > TOL:
        fails.append(f"all together: python {t['all']:.6f} page {js['all']:.6f}")
    for r in js["state"]:
        if r["before"] != 0 or not r["on"] or r["off"] or r["others"] != 0:
            fails.append(f"{r['key']}: written into the page's state, the boxes shown ticked are wrong: {r}")
        if rel(r["cost"], py[r["key"]]) > TOL or rel(r["back"], base) > TOL:
            fails.append(f"{r['key']}: in the page's state it gives {r['cost']:.6f} (python {py[r['key']]:.6f}) and taken out {r['back']:.6f} (python {base:.6f})")
    # the starting sets: the page prices each as Python does, by both paths
    for e in SA.sets():
        c = SA.cost(e["settings"])
        for path in ("sets", "sets_state"):
            if e["key"] not in js[path] or rel(js[path][e["key"]], c) > TOL:
                fails.append(f"set {e['key']} ({path}): python {c:.6f} page {js[path].get(e['key'])}")
    for e in SA.sets():
        sp, jp = SA.split(e["settings"]), js["set_splits"].get(e["key"], {})
        if any(k not in jp or rel(jp[k], sp[k]) > TOL for k in ("plant", "running")):
            fails.append(f"set {e['key']}: the plot's plant and running costs are not Python's: page {jp}, python {sp}")
    for w in ('id="st_pvr"', "function stPvrDraw"):
        if w not in html:
            fails.append(f"the page has no plot of plant against running costs: '{w}'")
    if [x[0] for x in js["set_names"]] != [e["key"] for e in SA.sets()]:
        fails.append("the page's starting sets are not Python's, in order")
    for w in ('id="tp_setsnote"', "stLoadSet("):
        if w not in html:
            fails.append(f"the page has no buttons for the starting sets: '{w}'")
    if js["off_humbird"] != 0:
        fails.append("a box shows ticked when the page is not on Humbird's design")
    if js["key"] != SA.BASE_KEY or rel(js["start"], base) > TOL:
        fails.append(f"the modifications' base is not the page's start: {js['key']} at {js['start']}")
    # the table of estimates below the most favourable case, and the line that states it
    c = SA.comparison()
    fav = S.all_favourable()["cost"]
    if rel(js["fav"][0], fav) > 1e-12 or rel(js["fav"][1], fav) > 1e-12 or js["fav"][2] != [b["name"] for b in c["below"]]:
        fails.append(f"the panel's most favourable case or its list of estimates below it is not Python's: {js['fav']}")
    panel = js["html"]
    if panel.startswith("ERROR"):
        fails.append(f"stRender failed: {panel}")
    else:
        want = ["Published estimates below this model's most favourable case, and why", f"${fav:.2f}</b> a kilo of cells",
                "No published estimate that respects those limits is below"] + [b["name"] for b in c["below"]]
        for b in c["below"]:
            want += [f"${b['today']:.2f} a kilo of wet cells in 2025 dollars"] + ([f"${b['inside']:.2f} a kilo"] if b["inside"] else [])
        for w in want:
            if w not in panel:
                fails.append(f"the panel does not show: {w}")
        for rx in (BAD_WORDS, EV.ROUTE_WORDS, re.compile(r"\bCentral\b|Best case")):
            mt = rx.search(re.sub(r"<[^>]+>", " ", panel))
            if mt:
                fails.append(f"the panel's words contain '{mt.group(0)}'")
    for b in pd["below"]:
        for a_ in b["assumptions"]:
            for rx in (BAD_WORDS, EV.ROUTE_WORDS):
                if rx.search(a_["assumption"] + " " + a_["why"]):
                    fails.append(f"{b['name']}: a rejected assumption's words break the page's rules")
    return fails


def test_study_assumptions():
    fails = check()
    assert not fails, "\n".join(fails)


if __name__ == "__main__":
    f = check()
    if f:
        print("\n".join("FAIL: " + x for x in f))
        sys.exit(1)
    print(f"study assumptions: all checks passed ({len(SA.STUDIES)} studies, {len(SA.modifications(with_notes=False))} modifications)")
