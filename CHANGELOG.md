# Change log

## 2026-11-14

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
