// render_probe.js — OPTIONAL headless inspection aid (not part of run_tests.sh).
//
// Renders a chart's SVG primitives under a mock DOM so you can verify chart STRUCTURE
// (e.g. the stacked cultivated+plant-based bars in Figure 1) without opening a browser.
// It is a debugging convenience, not a regression test — the committed guards are
// test_golden.py (numbers) and run_parity.py (JS==Python).
//
// Usage:
//   python -c "import re;h=open('interactive.html').read();\
//     b=[x for _,x in re.findall(r'<script([^>]*)>(.*?)</script>',h,re.S) if 'function utilities' in x][0];\
//     open('/tmp/model.js','w').write(b)"
//   node tests/render_probe.js /tmp/model.js
//
// Prints, for both the point-estimate (MC off) and Monte-Carlo (MC on) passes of drawBars:
// the rect-fill tally (tier colours + the plant-based green = stacked segments), the bar
// labels, the totals/legend texts, and the subtitle.

const fs = require("fs");
const code = fs.readFileSync(process.argv[2], "utf8");

// ---- minimal DOM mock (enough for el()/tx()/clear()/getElementById + the page bootstrap) ----
function mkEl(tag) {
  const e = { tag, attrs: {}, children: [], _text: "", _html: "",
    setAttribute(k, v) { this.attrs[k] = v; }, getAttribute(k){ return this.attrs[k]; },
    appendChild(c) { this.children.push(c); return c; },
    set textContent(t) { this._text = t; }, get textContent() { return this._text; },
    set innerHTML(h){ this._html = h; this.children = []; }, get innerHTML(){ return this._html; },
    get firstChild() { return this.children[0] || null; },
    removeChild(c) { this.children = this.children.filter(x => x !== c); },
    querySelector() { return mkEl("span"); }, querySelectorAll() { return []; },
    addEventListener() {}, append() {}, insertBefore(c){ this.children.push(c); return c; },
    classList: { add(){}, remove(){}, toggle() {} }, style: {},
    onchange: null, oninput: null, onclick: null, onmouseenter: null, onmouseleave: null,
    dataset: {}, value: "", checked: false };
  return e;
}
const bars = mkEl("svg"); bars.viewBox = "0 0 720 300";
const byId = {};
global.document = {
  createElementNS: (_ns, tag) => mkEl(tag),
  createElement: tag => mkEl(tag),
  getElementById: id => (byId[id] || (byId[id] = (id === "bars" ? bars : mkEl("div")))),
  addEventListener() {},
};
global.window = { matchMedia: () => ({ matches: false, addEventListener(){} }) };
global.MathJax = { typesetPromise: () => Promise.resolve(), typeset(){} };

eval(code + `
;global.__run = function(){
  MODEL.sliders.forEach(s => state[s.key] = s.default);
  MODEL.toggles.forEach(t => state[t.key] = false);
  state.region = "us"; state.income = C.REGION_INCOME.us; state.mc = false;
  KP = effConsts(state);
  drawBars(state, null);
  const pe = bars.children.slice();
  while(bars.firstChild) bars.removeChild(bars.firstChild);
  const ptmc = perTypeMC(state, 300);
  drawBars(state, ptmc);
  return { pe, mc: bars.children.slice(), sub: document.getElementById("barsub").textContent };
};`);

const out = global.__run();
function summarize(els, label) {
  const rects = els.filter(e => e.tag === "rect"), lines = els.filter(e => e.tag === "line"),
        texts = els.filter(e => e.tag === "text");
  const byColour = {};
  rects.forEach(r => { const c = r.attrs.fill; byColour[c] = (byColour[c] || 0) + 1; });
  console.log(`\n=== ${label} ===`);
  console.log(`  rects=${rects.length} lines=${lines.length} texts=${texts.length}`);
  console.log("  rect fills (tier colours + #5AAE61 = plant-based stack):", JSON.stringify(byColour));
  console.log("  some labels:", texts.map(t => t.textContent).filter(s => /%/.test(s)).slice(0, 10).join("  "));
  console.log("  legend/total texts:", texts.map(t => t.textContent).filter(s => /plant-based|cultivated total/i.test(s)));
}
summarize(out.pe, "POINT ESTIMATE (MC off)");
summarize(out.mc, "MONTE CARLO (MC on)");
console.log("\n  subtitle:", out.sub.slice(0, 170) + "...");
