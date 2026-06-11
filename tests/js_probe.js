/* js_probe.js — run the interactive page's embedded model JS headless, under Node,
 * and emit the SAME model outputs the page would compute, so a Python test can assert
 * the JS mirror agrees with the Python source of truth (market_share / meat_market / etc).
 *
 * The page JS is written to drive a browser DOM (buildRail/recompute/selfTest at the
 * bottom). We stub a minimal DOM so loading it doesn't crash, strip the auto-run tail,
 * then call the model functions directly and print JSON.
 *
 * Usage (driven by tests/run_parity.py):
 *     node js_probe.js <path-to-extracted-model.js>
 * Prints one JSON object to stdout: { headline, grid, timing }.
 *
 * No third-party deps — only Node's stdlib. */
"use strict";
const fs = require("fs");

// ---------------------------------------------------------------------------
// Minimal DOM stub: every getElementById/createElement returns a chainable
// no-op element so the page's UI-building code runs without a real browser.
// ---------------------------------------------------------------------------
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

global.document = {
  getElementById: () => ELEM,
  createElement: () => ELEM,
  createElementNS: () => ELEM,
  querySelector: () => ELEM,
  querySelectorAll: () => [],
};
global.window = {};
const realLog = console.log;
console.log = NOOP;            // silence the page's build-stamp console.log

// ---------------------------------------------------------------------------
// Load the page model JS, stripped of its DOM auto-run tail.
// ---------------------------------------------------------------------------
const jsPath = process.argv[2];
if (!jsPath) { realLog(JSON.stringify({ error: "no model-js path given" })); process.exit(2); }
let js = fs.readFileSync(jsPath, "utf8");
js = js.replace(/console\.log\([^\n]*\);/, "");            // drop the build-stamp log
js = js.replace(/buildRail\(\);[\s\S]*$/, "");             // drop everything from the auto-run tail

// The probe runs IN THE SAME SCOPE as the page JS (so it can see effConsts, shareCalc, …).
// It builds the default-slider constants, then samples the demand model over a grid plus
// the headline self-check numbers and a timing-rung trajectory.
js += `
;(function(){
  const def = {}; MODEL.sliders.forEach(s => def[s.key] = s.default);
  def.region = "us"; def.income = C.income_ref;
  KP = effConsts(def);                       // calibrate at the defaults (the page's recompute does this)

  const headline = {
    basicR:          basicR(def),
    beta_ref:        KP.beta_ref,
    anchor_price:    KP.anchor_price,
    w_realtissue_M:  KP.w_realtissue_M,
    K_wholefood_M:   KP.K_wholefood_M,
    K_wholefood_E:   KP.K_wholefood_E,
    pb:              shareCalc(1.0, KP, { present: false, which: "pb" }),
    parity:          shareCalc(1.0, KP, { ax: 1, tfM: 0 }),
    milk:            milkCheck(),
  };

  // share over a grid that exercises price, both acceptance dials, elasticity, and income
  // (income is the channel that previously diverged between JS and Python).
  const Rs      = [0.8, 1.0, 1.6, 2.0, 2.42, 3.0];
  const axs     = [0.6, 0.8, 1.0, 1.1];
  const tfMs    = [0.0, 0.5, 1.0, 1.5];
  const epss    = [-1.4, -0.9, -0.5];
  const incomes = [500000, 85810, 62266, 27105, 24248, 11159, 6440];
  const grid = [];
  for (const R of Rs) for (const ax of axs) for (const tfM of tfMs)
    for (const eps of epss) for (const income of incomes)
      grid.push([R, ax, tfM, eps, income, shareCalc(R, KP, { ax, tfM, eps, income })]);

  // HEALTH grid: sweep the cultivated (hx) and plant-based (hp) health-perception dials
  // — the scenario term most recently added to the JS — at a few price ratios, reading
  // BOTH the cultivated and plant-based shares so the term is exercised on each product.
  const healthVals = [-0.5, -0.25, 0.0, 0.5, 1.0];
  const healthGrid = [];
  for (const R of [0.8, 1.0, 2.42])
    for (const hx of healthVals) for (const hp of healthVals) {
      healthGrid.push([R, hx, hp, "x", shareCalc(R, KP, { hx, hp, which: "x" })]);
      healthGrid.push([R, hx, hp, "p", shareCalc(R, KP, { hx, hp, which: "p" })]);
    }

  // timing rung (cultivated trajectory) at the default R — exercises bassTrajectory + the fade.
  const Rx = basicR(def);
  const tr = bassTrajectory({
    R: Rx, nb0: def.neophobia_x0, nbL: def.neophobia_x, rate: def.accept_rate,
    p: def.p_innov, q: def.q_imit, ax: def.accept_x, tfM: def.theta_free_M,
    income: def.income, which: "x",
  });

  realLog(JSON.stringify({ headline, grid, healthGrid, timing: { R: Rx, share: tr.share } }));
})();
`;

try {
  eval(js);                                  // runs page JS + the probe IIFE in one scope
} catch (e) {
  realLog(JSON.stringify({ error: String(e && e.stack || e) }));
  process.exit(1);
}
