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

// FIRST SCREEN (page_scenarios.js): with a second argument, a JSON file of cases from tests/run_parity.py, the probe runs only
// the first screen's functions: the draws of the cost (on Python's own draws, and on the page's), the traits beyond the best
// measured in meat cells, the tank design for set traits, the meat-buyers scale of the contour map, and the plant's capital per m3
// and the nutrient floor the plant sliders show. Prints { tp: ... }.
const TP_IN = process.argv[3] ? JSON.parse(fs.readFileSync(process.argv[3], "utf8")) : null;
if (TP_IN) js += `
;(function(){
  const IN = ${JSON.stringify(TP_IN)};
  const def = {}; MODEL.sliders.forEach(s => def[s.key] = s.default);
  Object.assign(state, def, { region: "global", income: C.REGION_INCOME.global });
  KP = effConsts(state);
  const st = c => ({ base: c.base, choice: c.choice, hb: c.hb || { mode: "perfusion", plant: "sterile" }, traits: c.traits || {}, held: c.held || {} });
  const exact = IN.exact.map(c => tpCloudFor(st(c), c.draws.length, c.draws).cost);
  const stat = IN.stat.map(c => tpCloudFor(st(c)).q);
  const points = IN.stat.map(c => floorExplore(tpParamsFor(st(c))).total);
  const beyond = IN.routes.map(t => tpBeyond(t));
  const best = Object.fromEntries(TRAIT_KEYS.map(k => [k, [TP.traits[k].best, TP.traits[k].best_src]]));
  const plant = IN.stat.map(c => { const r = floorExplore(tpParamsFor(st(c))); return [r.capex, r.nutrients]; });
  const design = IN.design.map(c => { const d = scWithExtra(c.traits, () => scDesign(c.choice)); return [d.tricks, d.shape]; });
  const dial = IN.buyers.map(b => tpDial(b));
  const shares = IN.shares.map(([c, b]) => tpShare(c, b, "global"));
  const costfor = IN.costfor.map(([t, b]) => tpCostFor(t, b, "global"));
  const parity = ["global", "us", "eu"].map(r => [tpAvgPrice(r), tpParity(r)]);
  // the first screen's "where the money goes": the engine's cost result grouped by what drives it
  const groups = IN.stat.map(c => { const G = tpCostGroups(floorExplore(tpParamsFor(st(c)))), items = {};
    G.groups.forEach(g => g.items.forEach(i => { items[i.key] = [g.key, i.v]; })); return { items, sum: G.sum, total: G.total, ml: G.ml }; });
  realLog(JSON.stringify({ tp: { exact, stat, points, beyond, best, plant, design, dial, shares, costfor, parity, groups,
    humbird: floorExplore(Object.assign({}, tpRef("humbird").base)).total } }));
})();
`;
// The probe runs IN THE SAME SCOPE as the page JS (so it can see effConsts, shareCalc, …).
// It builds the default-slider constants, then samples the demand model over a grid plus
// the headline self-check numbers and a timing-rung trajectory.
if (!TP_IN) js += `
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
  // time to 90% of the long-run share at the same options and R (mirror of years_to_stabilize)
  const tstabs = [0.05, 0.15, 0.5].map(rate => yearsToStabilize({
    R: Rx, nb0: def.neophobia_x0, nbL: def.neophobia_x, rate, p: def.p_innov, q: def.q_imit,
    ax: def.accept_x, tfM: def.theta_free_M, income: def.income, which: "x" }));

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

  // OFFSET of a cut / premium product (mirror of meat_market.tier_offset): 0 for mince; for a structured product the blend
  // penalty -(1 - cell share) x w_realtissue_M plus premium-resistance r x the full premium penalty x a ramp in the product's
  // price against its species' cheapest form ($10 here). Each case: [kind, structured, price, r, cell share, offset], at the
  // default premium penalty ("def") and at a custom one set through the page's slider ("cust").
  const authCheck = [];
  const offCase = (kind, structured, price, r, cells) => {
    const mt = { name: "x", p_conv: price, structured: structured };
    authCheck.push([kind, structured, price, r, cells, tierOffset(structured, premiumRamp(mt, 10.0), r, cells, KP)]); };
  [[false, 10, 1.0, 0.8], [false, 60, 1.5, 0.5], [true, 10, 1.0, 0.8], [true, 19.9, 1.0, 0.8], [true, 20, 1.0, 0.8],
   [true, 24, 1.0, 0.8], [true, 25, 1.5, 0.8], [true, 30, 0.5, 0.8], [true, 39.9, 1.0, 1.0], [true, 40, 1.0, 0.8],
   [true, 80, 2.0, 0.3], [true, 28.3, 0.0, 0.6], [true, 12, 1.0, 1.0]].forEach(c => offCase("def", ...c));
  state.auth_premium_extra = -2.5;                                           // a custom premium penalty via the slider
  [[false, 10, 1.0, 0.8], [true, 10, 1.0, 0.8], [true, 30, 1.0, 0.8], [true, 50, 0.8, 0.5]].forEach(c => offCase("cust", ...c));
  delete state.auth_premium_extra;                                           // restore the default

  // IMPORTANCE BREAKDOWN parity (mirror of market_share.utility_breakdown): the per-factor utils
  // decomposition of cultivated vs conventional (mainstream). Sample a few operating points/dials.
  const bdCases = [
    { R: 2.42, o: { ax: 1, tfM: 0, toff: 0, eps: C.eps_own, income: C.income_ref, nbx: 0, nbp: 0, which: "x" } },
    { R: 1.0, o: { ax: 0.8, tfM: 0.5, toff: 0, eps: C.eps_own, income: C.income_ref, nbx: -1, nbp: 0, which: "x" } },
    { R: 1.6, o: { ax: 1, tfM: 0, toff: -1.5, eps: -1.2, income: 27105, nbx: 0, nbp: 0, hx: 0.3, which: "x" } },
    // per-PRODUCT point: a premium cut at its own local reference price (pRef) — exercises the p_ref path
    { R: 0.46, o: { ax: 1, tfM: 0, toff: -1.5, eps: -0.27, income: 85810, nbx: 0, nbp: 0, pRef: 40, which: "x" } },
  ];
  bdCases.forEach(c => { c.out = breakdownCalc(c.R, KP, "M", c.o); });

  // PREMISE DIALS: "seen as real meat" (cultivated b_x, plant-based b_p) are what-ifs applied AFTER the
  // calibration, which always runs in the observed world. Page and Python once disagreed here (Python
  // re-derived beta with b_x and re-fitted the weights with b_p, a degenerate solve at b_p=1).
  const premise = [];
  for (const bx of [0, 0.5]) {
    const K = effConsts(Object.assign({}, def, { real_tissue_x: bx }));
    premise.push(["x", bx, shareCalc(1.0, K, { ax: 1, tfM: 0 }), K.beta_ref, K.w_realtissue_M]);
  }
  {
    const K = effConsts(Object.assign({}, def, { real_tissue_p: 1 }));
    premise.push(["p", 1, shareCalc(1.0, K, { present: false, which: "pb" }), K.beta_ref, K.w_realtissue_M]);
  }

  // MONTE CARLO (statistical parity): the page's penetration band must sample the SAME inputs as
  // meat_market.monte_carlo. The two use different PRNGs, so compare medians within sampling noise.
  // (They once sampled different sets — health_x vs neophobia_x — and disagreed by ~1.4 pp.)
  const med = a => pctl(a.slice().sort((x, y) => x - y), 50);
  const mcUS = monteCarlo(Object.assign({}, def, { region: "us", income: C.income_ref }), 3000);
  const mcCheck = { region: "us", n: 3000, inputs: C.mc_inputs,
                    vol_p50: med(mcUS.vol), val_p50: med(mcUS.val) };
  // the samplers themselves: 10th / 50th / 90th percentile of 40,000 draws of every input the bands sample (mirror of inputs.draw)
  _seedRng(11);
  const drawCheck = Array.from(new Set(C.mc_inputs.concat(C.mc_timing_inputs))).map(k => {
    const a = []; for (let i = 0; i < 40000; i++) a.push(priorDraw(k)); a.sort((x, y) => x - y);
    return [k, pctl(a, 10), pctl(a, 50), pctl(a, 90)]; });

  const fxGrid = [];
  [16, 24, 48].forEach(dh => [550, 3000].forEach(m => [5, 20, 200].forEach(v =>
    ["pharma", "sanitary", "microbial"].forEach(pl => ["perfusion", "filldraw"].forEach(mo => {
      const p = { doubling_h: dh, mass_pg: m, vessel_m3: v, plant: pl, mode: mo, charge: 0.173, maint: dh === 48 ? 0.31 : undefined,
                  hazard: v === 5 ? 0.02 : 0, run_days: 25, restart_fail: 14, waste: v === 200 ? 0.3 : 0, pco2: dh === 24 ? 160 : undefined, gas_v: m === 3000 ? 0.009 : undefined, aspect: v === 5 ? 1.0 : undefined, osm_limit: pl === "sanitary" ? 380 : undefined, ph: mo === "filldraw" ? 7.0 : undefined, min_perfusion: v === 20 ? 12 : undefined, medium_l: m === 550 ? 30.5 : undefined,
                  medium_price: 0.5, growth_factors: dh === 16, cell_share: pl === "pharma" ? 0.5 : 1 };
      const r = floorExplore(p);
      fxGrid.push([dh, m, v, pl, mo, r.product, r.density, r.output, r.limit]);
    })))));
  // plants built item by item (plant_items): each named plant, and single items switched
  const fxItems = [];
  const itemCases = [C.fx.plant_items.lean, C.fx.plant_items.yeastplus, C.fx.plant_items.microbial, { hall: "shed" },
                     { oxygen: "bought", seed: "one" }, { vessels: "food", medium: "shared" }];
  itemCases.forEach((its, i) => ["perfusion", "filldraw"].forEach(mo => {
    const r = floorExplore({ doubling_h: 24, mass_pg: 3000, vessel_m3: i === 3 ? 50 : 20, plant: "sanitary", items: its, mode: mo,
                             charge: 0.173, hazard: i === 1 ? 0.015 : 0, run_days: 33, restart_fail: 14 });
    fxItems.push([i, mo, r.total, r.capex]);
  }));
  // tornado around the floor case and around a second case (JS argument names)
  const fxTor = [{ doubling_h: 24, mass_pg: 3000, vessel_m3: 20, plant: "sanitary", mode: "perfusion", charge: 0.173 },
                 { doubling_h: 40, mass_pg: 1500, vessel_m3: 50, plant: "microbial", mode: "perfusion", charge: 0.2, waste: 0.1 }]
    .map(p => fxTornadoRows(p).map(r => [r[0], r[1], r[2]]));
  fxTor.push(fxTornadoRows({ doubling_h: 24, mass_pg: 3000, vessel_m3: 20, plant: "sanitary", items: C.fx.plant_items.lean,
                             mode: "perfusion", charge: 0.173 }).map(r => [r[0], r[1], r[2]]));
  fxTor.push(fxTornadoRows({ doubling_h: 24, mass_pg: 2500, vessel_m3: 20, plant: "sanitary", mode: "perfusion", charge: 0.173, pco2: 50 },
                           [10, 100]).map(r => [r[0], r[1], r[2]]));
  // the tricks (column, pressure, explicit wastes, sorbent): the same cases as tests/run_parity.py FX_TRICKS
  const fxTricks = [{"column": "co2"}, {"column": "o2_closed", "p_top": 1.0, "gas_v": 0.002, "col_pout": 55.0}, {"p_top": 0.5, "aspect": 1.0}, {"nh3_kg": 0.14, "lac_yield": 1.05, "glc_kg": 0.84, "doubling_h": 42.9}, {"nh3_kg": 0.7, "sorbent": 0.8, "sorbent_price": 0.3}, {"column": "co2", "plant": "microbial", "vessel_m3": 50, "p_top": 0.0}, {"mode": "filldraw", "nh3_kg": 0.2}, {"sorbent": 0.5, "nh3_kg": 0.3, "lac_yield": 0.4, "osm_limit": 380, "sorbent_cycles": 10}, {"column": "o2_closed", "p_top": 1.0, "aspect": 0.8, "doubling_h": 30, "mass_pg": 2000, "nh3_kg": 0.1}, {"fat_fed": 1.0}, {"do_mmol": 0.05, "doubling_h": 48, "maint": 0.31}, {"rq": 1.0, "gas_v": 0.003}, {"column": "o2_closed", "do_mmol": 0.08, "gas_v": 0.002, "fat_fed": 0.5, "fat_price": 10.0}, {"column": "co2", "p_top": 0.5, "do_mmol": 0.15, "aspect": 1.2}, {"aspect": 1.0}, {"aspect": 0.8, "shape_cost": false}, {"aspect": 2.5, "vessel_m3": 100}, {"mode": "filldraw", "nh3_kg": 0.14, "lac_yield": 1.05, "glc_balance": true, "doubling_h": 43.0, "mass_pg": 2000.0}, {"mode": "filldraw", "vm": {"kind": "cyclic", "washed": false, "n_doublings": 2.0, "turnaround_h": 10.0, "restart_days": 2.0}, "nh3_kg": 0.14, "lac_yield": 0.42, "glc_balance": true, "doubling_h": 36.0, "mass_pg": 2000.0, "nh3_limit": 4.0, "hazard": 0.01}, {"mode": "filldraw", "vm": {"washed": false, "shape": 1.0, "dil_frac": 0.6}, "nh3_kg": 0.2, "nh3_limit": 3.0}, {"mode": "filldraw", "nh3_kg": 0.3, "nh3_limit": 4.0, "doubling_h": 30.0}].map(c => {
    const r = floorExplore(Object.assign({ doubling_h: 24, mass_pg: 3000, vessel_m3: 20, plant: "sanitary", mode: "perfusion",
                                           charge: 0.173 }, c));
    return [r.total, r.density, r.limit, r.medium_l, r.medium_set_by, r.limits, r.o2_kg, r.o2_kg_upkeep, r.co2_kg,
            r.column ? [r.column.passes, r.column.loop_volume, r.column.ph_vs_safe] : null];
  });
  // the scenarios (page_scenarios.js): the presets, twelve spread-out choices of the switches, what to prioritise, interactions, design
  const scChoices = SC.order.map(k => SC.presets[k].choice);
  for (let i = 0; i < 12; i++) { const ch = {}; SC.switches.forEach((sw, j) => { ch[sw.key] = sw.settings[(i * 7 + j * 3 + (i >> 1)) % sw.settings.length].key; }); scChoices.push(ch); }
  const scCases = scChoices.map(ch => { const r = scEval(ch);
    return [SC.keys.map(k => ch[k]), r.total, r.limit, r.medium_l, scShare(r.total, "global"), scShare(r.total, "us")]; });
  const scPri = scPriorities(SC.presets.central.choice, true).map(r => [r.switch, r.best, r.worst, r.d_best, r.d_worst, r.share_best, r.share_worst]);
  const scInt = scInteractions(SC.presets.central.choice, 6, 0.25).map(x => [x.a, x.b, x.gap]);
  const scDes = SC.order.map(k => { const d = scDesign(Object.assign({}, SC.presets[k].choice, { tricks: "none", shape: "tall" })); return [d.tricks, d.shape]; });
  // vessel types against operating modes (page_vessels.js): the reference case, the central scenario, two other presets
  const vmBases = [{ doubling_h: 24, mass_pg: 3000, vessel_m3: 20, plant: "sanitary", mode: "perfusion", charge: C.fx.charge_mature }]
    .concat(["central", "best", "cautious"].map(k => scParams(SC.presets[k].choice)));
  const vmCases = vmBases.map(b => VM.vorder.map(v => VM.morder.map(m => { const c = vmCell(v, m, b);
    return c.possible ? [v, m, true, c.cost, c.limit, c.density, c.tricks_fallback, c.unchecked_cost, c.density_unshown] : [v, m, false]; })));
  // the retention devices (page_retention.js): Humbird's reference case and three presets, every device on the page; and
  // floorExplore's extra_opex and flat retention capital alone (the same cases as tests/run_parity.py RT_FX)
  const rtBases = [{ doubling_h: 24, mass_pg: 3000, vessel_m3: 20, plant: "sanitary", mode: "perfusion", charge: C.fx.charge_mature }]
    .concat(["central", "best", "today"].map(k => scParams(SC.presets[k].choice)));
  const rtCases = rtBases.map(b => RT.order.map(dev => { const c = rtCost(dev, b), s = c.res;
    return [dev, c.total, c.capex_k_m3, c.cons_kg, c.loss, c.beyond, c.impossible, c.base, c.units, c.area_m2,
            s.capital + s.labour + s.utilities + s.consumables + s.feedstock + s.growth_factors + s.extra_opex, s.total]; }));
  const rtFx = [{ extra_opex: 1.5 }, { extra_opex: 0.7, hazard: 0.02, plant: "microbial" }, { retention: 40, extra_opex: 0.3, hazard: 0.01 },
                { retention: 0 }, { mode: "filldraw", retention: 40, extra_opex: 2 }].map(c => {
    const r = floorExplore(Object.assign({ doubling_h: 24, mass_pg: 3000, vessel_m3: 20, plant: "sanitary", mode: "perfusion",
                                           charge: 0.173 }, c));
    return [r.total, r.extra_opex, r.capex, r.consumables, r.run_frac]; });
  realLog(JSON.stringify({ headline, grid, healthGrid, foothold, weightCases, authCheck, bdCases, fxGrid, fxItems, fxTor, fxTricks,
                           rt: { cases: rtCases, fx: rtFx, order: RT.order },
                           mcCheck, drawCheck, premise, timing: { R: Rx, share: tr.share, tstabs }, vm: vmCases, sc: { cases: scCases, pri: scPri, inter: scInt, design: scDes } }));
})();
`;

try {
  eval(js);                                  // runs page JS + the probe IIFE in one scope
} catch (e) {
  realLog(JSON.stringify({ error: String(e && e.stack || e) }));
  process.exit(1);
}
