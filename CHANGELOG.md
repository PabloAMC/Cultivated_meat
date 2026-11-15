# Change log

## 2026-11-15

What GFI reports about the cost of medium (`research_notes/medium_cost_gfi.md`; no number moved)
- GFI's December 2025 amino acid analysis and January 2023 growth factor report, read in full: amino acids $0.02-0.17 a litre against
  $0.24-0.54 on Humbird's prices; Humbird's amino acids about $18-19 a kilo of cells; company reports of $0.20, $0.07 and $0.63 a
  litre. The model's Central case matches GFI; the best case's medium ($1.72 a kilo, 11 L/kg) sits below it.
- **Correction:** the tier "Humbird fed-batch, as designed" uses the model's feedstock (his cheaper bulk hydrolysate), not his own
  medium cost, which was far higher. The name was not changed.

If perfusion cannot be run at 20 m3 (`downside.py`, `research_notes/no_perfusion_downside.md`; no number moved)
- Each scenario priced in a stirred tank without cell retention, in fed-batch and in fill-and-draw, at the model's own density cap
  and at the 27 g/L shown for meat cells, with the tank design chosen again. Central: $26.64 with perfusion, $40.39 (fed-batch) or
  $43.58 (fill-and-draw) at 62 g/L, $90-97 at 27 g/L. Best case $8.95 -> $13.22 at 92 g/L, $41 at 27 g/L. The food-grade plant with
  shared medium cushions it most ($24.34 -> $28.22). `tests/test_downside.py`, in `run_tests.sh`.

Cheaper membranes for holding cells back (`research_notes/retention_alternatives.md`; no default changed)
- Three routes priced in `retention.py`, from a research pass on reusable and cleanable membranes (new `rt_reuse_*`, `rt_dial_*`,
  `rt_ceramic_*` inputs, each with source and range). Central case, against $26.64 with the default TFF loop: dialyser-grade
  hollow fibres $18.00, ceramic membranes run as a slow TFF loop $19.14, reused pharma modules $20.72. Nothing has been run with
  animal cells at this density for any of them; the odds the central case gets a tenfold cheaper membrane are about 15%.
- Wastewater and food-industry membranes are listed as not costed, with reasons. Dialysis with a cleaned dialysate and cells held
  back without a filter were not researched.

Does a thinner culture pay once filtering costs money? (`retention.density_scan`; no number moved)
- No, for the best, central and shared-medium cases: their tank designs, chosen again under the filter cost, are unchanged, and
  holding the culture below the density the tank allows saves membranes but costs more plant capital per kilo (central: $28.75 at
  180 g/L against $26.64 at 258). The cautious case would save $1.10 at 180 g/L with all three tricks; there is no density
  setpoint switch, so the model does not use it. Membrane life moves the central case by about $30; density barely does.

The filter loop is the model's default (Pablo's decision; numbers move)
- `floor_physics.explore` now prices the device that holds cells back in perfusion as a TFF hollow-fibre loop: hardware per m² of
  membrane sized on the cell-free liquid the bleed does not carry out, plus membranes at about $0.37 a litre filtered. A number
  for `retention` still charges a flat capital and no membranes. `rt_tff_default = 0` restores the old hoped-for device.
- Scenario costs: best $6.57 → **$8.95** (R 0.96 → 1.16: **no scenario reaches price parity now**; median world share 7.9% →
  4.4%), central $18.14 → **$26.64** (0.8% → 0.3%), central with shared medium $15.84 → $24.34, cautious $32.29 → $38.97,
  reference $11.48 → $11.84. The scenarios' tank designs did not change.
- The tornado's retention row is now the life of the filter membranes (5,500 to 900 litres per m²); the widest bar at the reference
  case is now the waste the cells make. The reference-case and scenario Monte Carlo runs draw the membrane life in place of a flat
  retention capital (floor Monte Carlo median $18.6 → $25.7).
- Pinned values updated in `test_floor_physics`, `test_scenarios`, `test_vessels`, `test_retention`. The gas-exchange and
  cheap-plant tests check their notes with the old device; those notes, `cost_scenarios.md` and `vessels_and_modes.md` carry a dated
  line saying so. RESULTS (summary rewritten: no parity, the filter as a cost driver) and METHODS (scenario table, tornado table,
  the default device) follow. The tier ladder keeps the old device.
- The page's JavaScript mirror prices the same loop; parity holds.

Holding the cells back in a 20 m3 perfusion tank (`retention.py`, `research_notes/retention_devices.md`; no default changed)
- The duty from the model: the reference case clears 0.16 m3/h of cell-free permeate (the bleed carries most of the liquid);
  the central case clears 1.88 m3/h from a culture that is a quarter cells; the best case 0.86 m3/h.
- Each real device sized and costed (`rt_*` inputs, each with source and range). Reference case: $10.82-12.25 with any device
  that works, against $11.48. Central: $25.69 (disc-stack separator, 28% of cells burst) to $30.43 (ATF), against $18.14; range
  $21-80. A settler is not possible at 258 g/L; acoustic devices and hydrocyclones are beyond what has been shown.
- Membranes, not hardware, set the cost of filtering the central culture: about $0.37 per litre of permeate, $8.83 a kilo.
- `tests/test_retention.py` (balances, the default reproduced exactly, sizing rules, ranges, pinned headline), in `run_tests.sh`.

Densities not shown for meat cells (no number moved)
- A cell tagged "done at this size" now says "This density is not shown for meat cells" when its density is above the 27 g/L
  reported for meat cells in a vessel of 1 m3 or more (new input `vm_x_meat_shown`: Vow's 538 kg harvest from 20,000 L; range
  27-68 g/L). This flags fed-batch and fill-and-draw in the stirred tank, fed-batch in the bag and the packed bed. The legend
  says the tag is about the vessel, the mode and the size, not the density. The takeaway says the 20 m3 fed-batch and
  fill-and-draw costs assume 62-92 g/L. Python, the JS mirror (parity-checked), the Markdown table, RESULTS, METHODS and the
  research note follow.

Plant names (Pablo's choice; no number moved)
- "A sterile plant without clean rooms" is now **"A food-grade plant"** (Humbird's plant with a sanitary hall in place of the clean
  room). "A lean plant" is now **"A food-grade plant with shared medium"** (the same plant with a shared medium line, two seed
  trains and bought oxygen; nobody has built one). The scenario names follow ("Central: selection and feed only, a food-grade
  plant"; "Central, food-grade plant with shared medium"). The pharma-style plant keeps its name. Internal keys (`lean`, `sterile`,
  `sanitary`) are unchanged. Entries below this one keep the old names.
- The page says above the scenario table and in the vessel section that every scenario uses a 20 m³ stirred tank in perfusion,
  with a continuous harvest, and that nobody has run animal cells in perfusion above about 4 m³.

Vessel types against operating modes (`vessels.py`, `page_vessels.js`, `research_notes/vessels_and_modes.md`)
- **New grid**: five vessels (stirred tank 20 m3, airlift 20 m3, single-use bag 5 m3, packed bed 65 L, hollow fibres 0.5 L) against
  five modes (batch, fed-batch, fill-and-draw, chemostat, perfusion). Only the vessel and the mode change; cells, plant, tank tricks
  and losses are those of the reference case or a scenario. Each cell: cost, density and what limits it, the largest cost item, a
  maturity tag (done at this size / only done smaller / never done with animal cells), or "not possible" with the reason.
- **The modes no longer collapse.** Reference case, stirred tank: batch $62.95, fed-batch $18.20, fill-and-draw $17.81 (unchanged),
  chemostat $33.67, perfusion $11.48 (unchanged). Central scenario: $109.07, $45.29, $48.95, $96.32, $18.14 (unchanged).
- `floor_physics.explore(vm=...)`: a new, optional argument (vessel and mode numbers). Left out, `explore` is unchanged: every golden
  value holds ($11.4801 reference, $18.14 central). The JS mirror `floorExplore` takes the same `vm`; parity is checked over 100 cells
  (reference case, central, best, cautious). `fxCell` now also returns the doubling time.
- New inputs `vm_*` (sizes, airlift shape and oxygen transfer, unit prices, bag/bed/set prices, bed and cartridge densities and cycles,
  batch density, chemostat dilution, restart after a lost cycle, labour exponent, largest perfusion run), each with source and range.
  Bag, bed and set prices are assumptions: no price was found.
- Page: the "Vessel types and operating modes" section is filled. The table follows the switches in "What decides it", with a
  button for the reference case, a one-sentence reading guide, a legend, a plain takeaway, the limits of each vessel and the
  evidence behind each tag. The placeholder from the scenarios work is gone.
- Tests: `tests/test_vessels.py` (anchors, fed-batch against Humbird's formula, chemostat against fill-and-draw, impossible cells,
  expected orderings, golden grid), added to `run_tests.sh`.

Cost scenarios in place of "the floor" (`scenarios.py`, `research_notes/cost_scenarios.md`)
- **The floor is retired as a name.** $11.5/kg was `floor_physics.explore()` at its defaults (a standard 20 m3 perfusion tank,
  120 g/L, a sterile plant, engineered cells, no tank tricks, no lost runs): neither a best case (the best case is $6.6) nor a
  typical one. It is kept, unchanged, as the labelled reference "a standard perfusion tank, no tricks" (`scenarios.reference()`;
  `cost_floor` keeps its name in the code). Every golden value that rests on it is unchanged: $11.4801 in `test_floor_physics`, 11.5020
  `cost_floor` in `test_golden`.
- **Scenarios**: ten switches (kind of cells, growth speed, plant, gas the cells tolerate, tank tricks, tank shape, runs lost, restart
  time, growth factors, medium price), each setting an `explore` argument set with a plain label and a tag for what it needs (genetic
  engineering / selection or adaptation / feed, process or plant / nothing new). Scenarios are presets of the switches:
  best case $6.57 (0.96x, world share 7.9% median, 2.8-17.3%; 15.2% at the point cost, needs genetic engineering), central $18.14 (1.93x, 0.8%
  median, 0.2-2.5%; 1.5% at the point cost; $15.84 in a lean plant, 1.1% median), cautious $32.29 (3.11x, 0.2% median; 0.3% at the point
  cost), the reference $11.48 (5.4%, point estimate), as a company reports $34.35 (0.3%, point estimate). Doubling time is an explicit switch; the
  central case takes 36 h (cost at 30 h $17.80, at 24 h $16.84). Tank design of each scenario = the cheapest the loop checks allow.
- **Review of PR 16 (2026-11-15), the share headline and what the tank design relies on.** The share quoted for a scenario is now the
  **median of its band**, where cost and demand are both uncertain. The 10th-90th percentile sits beside it. The point estimate is kept, labelled.
  Best case 15.2% -> **7.9%** (2.8-17.3), central 1.5% -> **0.8%** (0.2-2.5), central lean 2.3% -> **1.1%** (0.3-3.2), cautious 0.3% -> **0.2%**
  (0.0-0.5). The bands use 4,000 draws (`scenarios.BAND_N`; at 1,000 the best case's median moved by 0.3 points between seeds). No
  cost and no golden value changed. Each scenario now says which tank tricks it uses and what it costs without them (central $23.0, or $30.0
  in the ordinary tall tank; best $7.4 / $9.4; cautious $51.7 / $62.8). The central scenario's story gives the reasoning for 36 h and says what
  24 h is worth ($1.3/kg). `tests/test_scenarios.py` checks the median headline in RESULTS/METHODS/the page and the tricks sentences.
- **New on the page**: the answer table; "What decides it" (switches, live result, what to prioritise, two switches together, which
  switches interact), mirrored in `page_scenarios.js` and checked by `tests/run_parity.py` (16 choices, priorities, interactions, design).
- **Moved (deliberate)**: `floor_physics.explore(growth_factors=)` is a share, not only a flag (`True` still means all; the page's checkbox
  became a slider; tornado range 0 to 1). `cost_model.biomass_cost` is no longer floored at the reference cost (it was never
  reached by the defaults; the page never applied it). The page opens on the central scenario, not on the reference case; its cost
  sliders (medium price, plant running cost, cell efficiency) now start at the reported process and apply only to "As a company reports";
  the Monte Carlo on the page holds the scenario's cost. The "reference plant" label replaces "floor plant" in `PLANT_CONFIGS`.
  The page headline tokens `*_FLOOR*`, `FLOOR_MC_*`, `COST_FLOOR_LEAN` are replaced by scenario tokens. The cells-by-tank grid on
  the page is recomputed from the central scenario (sterile and lean plant; each cell names its limit); the "what stands in the way"
  table is recomputed from the central scenario.
- New inputs (all `sc_*`, with source, range and note): `sc_nh3_*`, `sc_lac_*`, `sc_glc_measured`, `sc_mass_selected_pg`, `sc_td_*`, `sc_gas_*`,
  `sc_hazard_*`, `sc_restart_*`, `sc_gf_*`, `sc_medium_*`, `sc_aspect_*`, `sc_p_top`.
- Docs: README, RESULTS (summary rewritten around the scenarios), METHODS (new section "Cost scenarios"). Numbers that moved in the prose:
  the headline "the floor is about $11.5/kg ... ~5% of world meat" is now the reference row; "price parity needs a cheaper class of plant"
  became "price parity needs the best case or nearly"; the funding list was reordered (better cells first); the lean plant's break-even
  loss rate is about once in 28 days. Section 3's shares by type are unchanged and now labelled "reference case".

Page reorganised (`research_notes/page_structure.md`)
- Order: the answer (scenario table), what decides it, how the cost is built up, from cost to market share, evidence and checks, method and
  sources (collapsed); a jump bar links them. Charts lose their numbers and are named in the text. Each share chart has its explanation under its title,
  in the order of the reasoning (price ratio, how shoppers choose, each kind of meat, how fast).
- New: **Vessel types and operating modes** (`#vessels`): operating mode against plant class for the chosen scenario, and a marked place for the
  airlift, bubble column, batch, fed-batch and chemostat a later session will add. The old mixed list of cases lives on in the method.
- New: cost-model back-test table, "what has and has not been measured", and "the measurements that would move the answer" (each priced from the switches).
- Changed: the all-levers panel (Build your own case) is collapsed, starts from the chosen scenario and has a "Start from a scenario" control; "Use this case"
  sends its cost to the charts. Tank shape slider goes down to 0.5. The scenario table restacks into cards on a phone.
- No golden value moved: `tests/test_golden.py` is unchanged apart from a label ("reference cost").

## 2026-11-14

Gas flow
- What caps the sparge gas flow was researched mechanism by mechanism (`research_notes/gas_flow_cap.md`).
  Humbird's 6 mm/s is a rule of thumb, not a measured limit; the floor keeps it and still costs $11.5/kg.
- Moved: the tornado range for gas flow is 2–9 mm/s, was 2–6, so its bar runs $28.0–8.7, was $28.0–11.5. The
  prior range of `pf_gas_velocity` is 0.002–0.009 m/s, was 0.0006–0.006. No other pinned number moved.
- `explore` reports what the oxygen fed with the sparge gas costs (`gas`, $0.52/kg at the floor) and what
  charging it by gas flow would change (`gas_extra`); neither is added to the total (`floor_physics.oxygen_fed`).

Cost side
- Re-anchored. The default is a company's reported process (SuperMeat 2024) with a yearly charge on its plant;
  Pasitka et al. 2024 is no longer used (its kilogram is mostly liquid and its cost leaves out the plant).
- The floor is derived from physics and published plant costs (`floor_physics.py`), financed like a mature food
  industry: $11.5/kg of cells; $6.6 in a yeast-style plant.
- The CO2 limit on tank density is computed from a gas balance. Further limits: mixing, the energy of growth,
  waste and medium use, salt strength, a least medium flow per cell, contamination.
- Species presets with their own CO2 tolerance; a reconstruction of the one working 20 m3 plant.
- Uncertainty on the floor's own inputs, alone and together with demand; a back-test against reported runs;
  a cross-check of plant costs against other published designs.
- The plant item by item (`plant_items.py`): Humbird's animal-cell plant ($683k per m3) and his yeast plant
  with the same tanks ($130k) rebuilt on one list of nine items, each with options; two new plants in between
  (lean $340k, a yeast plant with additions $175k); the panel's class of plant now sets the items, and they
  can be chosen one by one. Contamination as dynamics (`contamination.py`): time to detection, what is lost,
  and the loss rate at which a cheaper plant stops paying. Write-up: `research_notes/cheap_plant_study.md`.

- Side-study of gas exchange (`gas_exchange.py`, `research_notes/gas_exchange_study.md`): a membrane loop,
  tank shape with the vessel's cost, and a check of a published airlift. Not used in the floor or on the page.
- Tricks as levers (deliberate additions; the floor, $11.48 and 11.16 L/kg, and every earlier number unchanged):
  `explore` gains `column`, `col_pout`, `p_top_barg`, `nh3_kg`, `lac_yield`, `glc_kg`, `sorbent` (+ capacity,
  price, uses) and returns every cap (`limits`) and what sets the medium (`medium_terms`). The page gains a
  "Tricks" group and a "What limits this tank" chart, mirrored in `floorExplore` with nine new parity cases.
  Two new tornado rows: pressure at the top of the tank, ammonia per kg. New inputs `pf_glc_kg`,
  `pf_sorbent_q`, `pf_sorbent_price`, `pf_sorbent_cycles`. RESULTS.md gains the cells-by-tank tables and the
  cheapest combination by gas cap. The waste notes `waste_tricks_sizing.md` and `waste_and_medium_evidence.md`
  are now versioned.
- Cell-side levers (defaults unchanged): `fat_fed` (CO₂ per oxygen from 1.204 to 0.966 when all lipid is fed;
  Humbird's Reaction 2.2), `rq`, `do_mmol` (dissolved-oxygen setpoint; default the 0.28 mmol/L his numbers
  imply), and outputs for oxygen and CO₂ per kg split into upkeep and growth. Inputs `pf_rq_lipid`, `pf_fat_kg`,
  `pf_fat_price`, `ge_atp_per_o2`. Tags (feed or process / selection or adaptation / genetic engineering) on the
  page and in RESULTS.md, whose tables now come with and without genetic engineering.
- Deliberate change: the packed column now takes in culture at the tank's dissolved oxygen (0.28 mmol/L) rather
  than an assumed 0.05, so the oxygen-sweep cases cost up to $0.13/kg more (e.g. $7.43 to $7.52 at 2 mm/s) and an
  air sweep can no longer add oxygen. The note and RESULTS.md were updated.
- Deliberate change: a tank shape other than the default now carries its steel and floor cost in `explore` and on
  the page (`shape_cost`, default on). Moved: the tank-shape tornado row $9.3–25.2 to $9.5–24.4; in METHODS'
  CO₂ table the squat tank $9.3 to $9.5, 150 mbar with the squat tank $8.5 to $8.7, the 200 m³ squat tank at
  200 mbar $10.1 (153 g/L) to $11.3 (137 g/L). The default floor is unchanged.
- The page's "Build your own case" panel, with the tricks and the limits chart, now stands above "How the model
  works" instead of inside it.
- Deliberate change (review of PR 10): the column's default outlet CO2 (`ge_col_pout`) is now 55 mbar, not 20, so
  `explore(column="co2")` moves from $8.60 to $8.62; section 7 of the gas-exchange note keeps its 20 mbar design
  as the first one, and its tests pass 20 explicitly. New: passes an hour, pumped flow, loop volume and alkaline
  exposure in the column's output and on the page (inputs `ge_loop_transit`, `ge_passes_tested`);
  `cheapest_tricks(ph_safe=, tested=)`. RESULTS.md's cheapest-combination table gains the passes and a column
  within the tested passes and the safe pH exposure ($7.45 / $8.5 / $11.7 / $17.2 at 6 / 4 / 2 / 1 mm/s), and no
  longer says the floor barely depends on gas flow.

Demand side
- Price sensitivity above equal price is set by six premium animal products within the range of the one
  choice experiment on cultivated meat. It now acts only on cultivated meat's price difference from
  conventional. Shares at equal price are unchanged; above it they are several times lower.

Page
- Opens on the floor case. "Build your own case" panel with levers, a tornado chart of limiting factors with
  an information card per factor, and a button that sends a case to the main model.

Repository
- Tests run in CI. Research notes behind the new numbers are in `research_notes/`, with how each was read.

## 2026-11-13

- Independent review of the published model; organic-chicken check added; calibration price fixed.
