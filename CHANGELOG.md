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
