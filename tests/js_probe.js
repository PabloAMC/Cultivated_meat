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
    w_health_M:      KP.w_health_M,
    w_health_E:      KP.w_health_E,
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

  // FOOTHOLD rung: per-product price ratio R (footR) at the defaults. This is the cost->R
  // machinery shared with foothold.product_R — the ONE foothold quantity that is a true Python
  // mirror (the rest of the panel is a JS-only visualization), and the exact corner a scaffold-cost
  // mismatch slipped through once. [label, R] per injected (non-no_referent) product.
  const foothold = C.foothold_products.map(pd => [pd.label, footR(def, pd)]);

  // EXPERT attribute-weight parity: changing a pinned/assumed weight (w_taste, w_slaughter_E)
  // re-solves the others; OVERRIDING a solved weight pins it (breaking its moment). Mirror of
  // market_share pinned_weights / the w_taste|w_slaughter_E constructor inputs. Each case sets
  // the values, marks the pinned ones (key+"_ovr"=true), and reads the solved weights + shares.
  const weightCases = [
    { vals: { w_taste: 7.0 }, pin: [] },
    { vals: { w_slaughter_E: 6.0 }, pin: [] },
    { vals: { w_realtissue_E: 1.5 }, pin: [] },
    { vals: { w_realtissue_M: 1.5 }, pin: ["w_realtissue_M"] },
    { vals: { w_health_M: 0.4 }, pin: ["w_health_M"] },
    { vals: { w_health_E: 2.6 }, pin: ["w_health_E"] },
    { vals: { w_realtissue_M: 3.0, w_health_M: 0.5, w_health_E: 2.5 },
      pin: ["w_realtissue_M", "w_health_M", "w_health_E"] },
  ];
  weightCases.forEach(c => {
    const sd = Object.assign({}, def);
    Object.keys(c.vals).forEach(k => sd[k] = c.vals[k]);
    c.pin.forEach(k => sd[k + "_ovr"] = true);
    const K = effConsts(sd);
    c.out = { w_realtissue_M: K.w_realtissue_M, w_health_M: K.w_health_M, w_health_E: K.w_health_E,
              parity: shareCalc(1.0, K, { ax: 1, tfM: 0 }),
              pb: shareCalc(1.0, K, { present: false, which: "pb" }) };
  });

  // AUTHENTICITY ladder parity: the per-tier offset = premium-resistance r × τ_tier, with τ either
  // the datasheet ladder (default) or the user's authenticity sliders. Mirror of
  // meat_market.tier_authenticity. Read tAuth for each tier at default τ and at a custom τ.
  const authCheck = [];
  [["basic", 1.0], ["cut", 1.0], ["premium", 1.0], ["cut", 1.5], ["premium", 0.5]].forEach(
    ([t, r]) => authCheck.push(["def", t, r, tAuth(t, r)]));
  state.auth_basic = 0.5; state.auth_cut = -1.0; state.auth_premium = -2.5;   // custom τ via the sliders
  [["basic", 1.0], ["cut", 1.0], ["premium", 1.0], ["premium", 0.8]].forEach(
    ([t, r]) => authCheck.push(["cust", t, r, tAuth(t, r)]));
  delete state.auth_basic; delete state.auth_cut; delete state.auth_premium;  // restore defaults

  // IMPORTANCE BREAKDOWN parity (mirror of market_share.utility_breakdown): the per-factor utils
  // decomposition of cultivated vs conventional (mainstream). Sample a few operating points/dials.
  const bdCases = [
    { R: 2.42, o: { ax: 1, tfM: 0, toff: 0, eps: C.eps_own, income: C.income_ref, nbx: 0, nbp: 0, which: "x" } },
    { R: 1.0, o: { ax: 0.8, tfM: 0.5, toff: 0, eps: C.eps_own, income: C.income_ref, nbx: -1, nbp: 0, which: "x" } },
    { R: 1.6, o: { ax: 1, tfM: 0, toff: -1.5, eps: -1.2, income: 27105, nbx: 0, nbp: 0, hx: 0.3, which: "x" } },
  ];
  bdCases.forEach(c => { c.out = breakdownCalc(c.R, KP, "M", c.o); });

  realLog(JSON.stringify({ headline, grid, healthGrid, foothold, weightCases, authCheck, bdCases,
                           timing: { R: Rx, share: tr.share } }));
})();
`;

try {
  eval(js);                                  // runs page JS + the probe IIFE in one scope
} catch (e) {
  realLog(JSON.stringify({ error: String(e && e.stack || e) }));
  process.exit(1);
}
