// render_probe.js — OPTIONAL headless inspection aid (not part of run_tests.sh).
//
// Draws the first screen's "Share of each kind of meat" bars (tpSellBars in page_scenarios.js) under a stub DOM, at the
// page's starting settings, so you can check the chart's structure (cultivated bars, plant-based meat stacked on them,
// the totals) without opening a browser. It is a debugging convenience, not a regression test: the committed guards are
// test_golden.py (numbers) and run_parity.py (JS == Python).
//
// Usage (from the repository root, after `python build_interactive.py`):
//   python -c "import re;h=open('interactive.html').read();\
//     b=[x for _,x in re.findall(r'<script([^>]*)>(.*?)</script>',h,re.S) if 'function utilities' in x][0];\
//     open('/tmp/model.js','w').write(b)"
//   node tests/render_probe.js /tmp/model.js [width]
//
// Prints, for the width given (default 720: upright bars; under 560: bars on their side), the count of bars by fill
// colour, the bar labels, the totals and the chart's subtitle numbers.
"use strict";
const fs = require("fs");

// ---- a stub DOM (as tests/js_probe.js): every element is a chainable no-op, except the chart's own svg ----
const NOOP = () => {};
let CHAIN;
const ELEM = new Proxy({}, {
  get(_t, p) {
    if (p === "style") return {};
    if (p === "classList") return { toggle: NOOP, add: NOOP, remove: NOOP };
    if (p === "querySelector") return () => ELEM;
    if (p === "querySelectorAll") return () => [];
    if (p === "appendChild" || p === "removeChild" || p === "setAttribute") return NOOP;
    if (p === "firstChild") return null;
    if (p === "textContent" || p === "innerHTML" || p === "value") return "";
    return CHAIN;
  },
  set() { return true; },
});
CHAIN = new Proxy(function () { return ELEM; }, { get: () => CHAIN, apply: () => ELEM });
const SBARS = { innerHTML: "", attrs: {}, setAttribute(k, v) { this.attrs[k] = v; } };
global.document = {
  getElementById: id => (id === "tp_sbars" ? SBARS : ELEM),
  createElement: () => ELEM, createElementNS: () => ELEM,
  querySelector: () => ELEM, querySelectorAll: () => [],
};
global.window = {};
const realLog = console.log;
console.log = NOOP;            // silence the page's build-stamp console.log

const WIDTH = +(process.argv[3] || 720);
let js = fs.readFileSync(process.argv[2], "utf8");
js = js.replace(/console\.log\([^\n]*\);/, "");            // drop the build-stamp log
js = js.replace(/buildRail\(\);[\s\S]*$/, "");             // drop the auto-run tail
js += `
;(function(){
  pgWidth = () => ${WIDTH};                                // the chart's container width
  const def = {}; MODEL.sliders.forEach(s => def[s.key] = s.default);
  Object.assign(state, def, { region: "global", income: C.REGION_INCOME.global });
  KP = effConsts(state);
  if (SCS.buyers === null) tpSetBuyers(tpRef(SCS.from).buyers);
  state.equal_price_share = tpDial(SCS.buyers);
  pgSetCost();
  const f = pgFacts();
  tpSellBars(f.animals);
  global.__out = { A: f.animals, cost: f.cost };
})();`;
eval(js);

const svg = SBARS.innerHTML, A = global.__out.A;
const fills = {};
(svg.match(/<rect [^>]*>/g) || []).forEach(r => {
  const c = (r.match(/fill="([^"]*)"/) || [])[1], pale = /fill-opacity/.test(r) ? " (paler: plant-based)" : "";
  fills[c + pale] = (fills[c + pale] || 0) + 1;
});
const texts = (svg.match(/<text[^>]*>([^<]*)<\/text>/g) || []).map(t => t.replace(/<[^>]*>/g, ""));
realLog(`width ${WIDTH}: viewBox ${SBARS.attrs.viewBox}`);
realLog("bars by fill:", JSON.stringify(fills));
realLog("labels:", texts.filter(s => /%/.test(s)).slice(0, 20).join("  "));
realLog("totals:", texts.filter(s => /by weight|by value|all meat/i.test(s)).join("  |  "));
realLog(`cost of cells $${global.__out.cost.toFixed(2)}; all meat and seafood ${A.total.toFixed(2)}% by weight, ` +
        `${A.value.toFixed(2)}% by value; plant-based ${A.pbv.toFixed(2)}% by weight`);
