# The all-favourable case, and the path to it from Humbird's design

> Extended 2026-11-20 (third pass): published studies are sources too (`study_assumptions.py`, `study_comparison.md`). Two values came from them, a 5.3 ng cell (Risner 2021, CE Delft 2021) and 25 m³ tanks (SuperMeat 2024), and the case moved from $7.56 to $7.02.

> Rewritten 2026-11-20 (second pass of the model batch). Until then this note described a second "every lever at its limit" figure: a ladder from the low-lactate example ($49.96) to $7.86, beside the all-favourable example at $18.71. The model now has one most favourable case, defined once. The earlier ladder and its figures are in this file's history.

> Names: the low-lactate example was earlier called Central; the all-favourable example was earlier called the best case. Cells are described by their traits.

Date: 2026-11-20. Code: `scenarios.all_favourable()`, `scenarios.favourable_levers()`, `scenarios.EXTRAS`, `frontier.py`. Tests: `tests/test_ordering.py`, `tests/test_frontier.py`. Costs are 2025 dollars per kilo of wet cells harvested, with every estimate at its most likely value.

## 1. Why there is one case

Before this change the model had three low figures that did not agree.

- Humbird's design as this model prices it (`scenarios.reference()`): $16.03.
- The all-favourable example (the scenario `best`): $18.71.
- The last row of the ladder in `frontier.py`, shown on the page as the "best level known": $7.86.

The all-favourable example cost more than Humbird's design. That made no sense, because people have proposed improvements on his design. The cause was that the example took this model's own settings on four levers where his design is the more favourable: a 2 ng cell where his weighs 3 ng, 4 mmol/L of ammonia tolerated where he takes 5, 35 mmol/L of lactate where he takes 50, and 0.6% of runs lost a day where he loses none.

The rule now is this. For every lever the engine has, the all-favourable case takes the most favourable value among (i) this model's own favourable end, (ii) Humbird's design and (iii) what any published study assumes without breaking a named limit of the model (the limits, each study's values and the rejected ones are in `study_comparison.md`). "This model's own favourable end" means the favourable setting of each switch, and the favourable end of an input's range where the earlier ladder already used it. The case is defined in one function, `scenarios.all_favourable()`. The scenario `best`, the last row of `frontier.ladder()` and the page's "best level known" are that one call, so they are the same number: **$7.02**.

The share of meat buyers who pick cultivated meat at equal price (58.5% in the all-favourable example, `best_equal_price_share`) is a setting about shoppers. It is separate and applies only where a share is quoted.

## 2. The case, lever by lever

| lever | value taken | from | this model's own favourable end | Humbird's design (2021) | favourable is |
|---|---|---|---|---|---|
| Ammonia the cells make (mol a kilo of cells) | 0.054 | Humbird's design (2021) | 0.055: the kind-of-cells switch at 'almost no ammonia or lactate' (sc_nh3_engineered) | 0.054: his enhanced cell (pf_nh3_efficient) | lower |
| Lactate the cells make (mol per mol of glucose) | 0.279 | this model's own favourable end | 0.279: the same setting (sc_lac_engineered) | 0.279: his enhanced cell: 0.5 per glucose burned or fermented | lower |
| Weight of a cell (pg) | 5300 | Risner 2021 | 2000: every setting of the kind-of-cells switch (sc_mass_selected_pg) | 3000: his assumed cell: a bigger cell uses less oxygen per gram | higher |
| Doubling time (hours) | 16 | this model's own favourable end | 16: the old frontier's lever (gf_and_doubling_bounds.md); the growth switch stops at 24 | 24: his model cell | lower |
| Ammonia the cells tolerate (mmol a litre) | 5 | Humbird's design (2021) | 4: what every scenario takes (sc_nh3_limit) | 5: his limit (pf_nh3_limit) | higher |
| Lactate the cells tolerate (mmol a litre) | 50 | Humbird's design (2021) | 35: what every scenario takes (sc_lac_limit) | 50: his limit (pf_lac_limit) | higher |
| Runs lost to contamination (share of runs a day) | 0 | Humbird's design (2021) | 0.002: the losses switch at pharma's 0.2% a day | 0: his design loses none | lower |
| Growth factors bought (share of Humbird's price) | 0 | this model's own favourable end | 0: the growth-factor switch at 'none bought' | 0: scenarios.reference() buys none | lower |
| Price of the medium ($ a litre above the nutrients the cells eat) | 0 | this model's own favourable end | 0: the medium switch at the nutrient floor: $2.00 a kilo of cells at GFI's feed-grade prices | 0.15: explore()'s default, which meets the same floor; his own nutrients cost $4.34 a kilo today, more | lower |
| Dissolved oxygen the tank is held at (mmol a litre) | 0.1 | this model's own favourable end | 0.1: what every scenario takes (sc_do_setpoint): a lower level passes more oxygen | none: his tank implies about 0.28 | lower |
| Least medium flow the cells need (mL a gram of cells a day) | 3.7 | this model's own favourable end | 3.7: the low end of pf_min_perfusion's range: the lowest flow measured (min_litres) | none: scenarios.reference() takes the model's own (pf_min_perfusion) | lower |
| Thickest culture the tank can stir (g a litre) | 320 | this model's own favourable end | 320: the old frontier's lever (thick_culture.md) | none: scenarios.reference() takes the model's 258 (pf_x_visc) | higher |
| The plant (setting of the plant switch) | lean | this model's own favourable end | lean: the plant switch at 'a food-grade plant with shared medium' | sterile: scenarios.reference(): his plant in a food-grade hall | whichever costs least |
| The device that holds the cells back (membrane device) | dialyser | this model's own favourable end | dialyser: the old frontier's lever: dialyser-grade hollow fibres (retention_alternatives.md), as explore() arguments {'flux': 2.5, 'membrane_life': 1000.0, 'membrane_price': 8.0, 'membrane_hw': 0.5} | tff: scenarios.reference(): the engine's own filter loop | whichever costs least |
| How the tank is run (setting of the mode switch) | perfusion | Humbird's design (2021) | perfusion, fedbatch100, fedbatch50, fedbatch: every setting of the mode switch | perfusion: scenarios.reference() | whichever costs least |
| Gas flow the cells tolerate (setting of the gas switch) | 6 | Humbird's design (2021) | 6, 4, 2: every setting of the gas switch: more gas passes more oxygen and kills more cells | 6: his 6 mm a second | whichever costs least |
| Added equipment for oxygen and CO₂, and tank shape (settings of the two tank-design switches) | pressure, squat | this model's own favourable end | design(): the cheapest pair that passes the checks on the CO₂ loop | none, tall: an ordinary tall tank | whichever costs least |
| Size of the tank (m³) | 25 | SuperMeat 2024 | 20: the model's tank (vm_str_m3) | 20: his fed-batch tanks; his perfusion tanks are 2 m³ (Sect. 4.2) | whichever costs least |
| Yearly payment that repays the plant (share of the plant's cost a year) | 0.08299 | this model's own favourable end | 0.08299: 5.4% over 20 years, the food-processing cost of capital Humbird quotes (plant_charge_mature, less the 9% of maintenance and insurance) | 0.1457: 7.5% over 10 years (Sect. 3.1); his yeast benchmark, 10% over 20 years, is 11.7% | lower |

The table shows two of the sources; `study_comparison.md` (section 3) has every study's value on every lever.

Three kinds of lever are in the table.

- **Levers with a direction** (the first twelve, and the yearly payment on the plant). The case takes the better value. Humbird's design supplies four of them: the ammonia the cells make, the ammonia and the lactate tolerated, and no lost runs. Risner 2021 supplies the cell's weight, 5.3 ng (CE Delft's scenario 8 has nearly the same). No study that charges interest repays a plant on better terms than the model's 5.4% over 20 years, so the yearly charge stays the model's.
- **Levers without a direction** (the plant, the device that holds the cells back, the way the tank is run, the gas flow, the tank design, the size of the tank). The case takes the setting that costs least with every other lever at its favourable value. More gas passes more oxygen and kills more cells, so the gas flow has no favourable direction; 6 mm/s costs least here. The tank design must pass the checks on the CO₂ loop, and it is chosen again for every tank size the studies use (2 to 211 m³): 25 m³ costs least.
- **Levers the switches cannot say.** The ten switches have no setting for a 5.3 ng cell, a 16-hour doubling, the tolerated ammonia and lactate, no lost runs, the least medium flow, the thickest culture, the dialyser-grade fibres or the 25 m³ tank. The scenario carries them as extra settings (`scenarios.EXTRAS`, applied in `explore_kwargs`, mirrored on the page in `scParams`). A lever that a switch owns (the cells' traits, the doubling time, the lost runs) applies only while that switch stays at its setting, so moving the switch on the page moves the lever with it. The draws behind the bands hold what the extra settings fix.

Held at the model's own value, as Humbird's design as this model prices it holds them too: the yearly charge on the plant (17.3%), the cells killed by bubbles, the 2% of cells lost at harvest, the bubble protectant, and the CO₂ and the salt the cells tolerate.

Not used, though the earlier ladder had them:

- **6.4 litres of medium a kilo.** That figure is the least the physics allows for cells that make no waste at all. This case's cells make 0.054 mol of ammonia a kilo, and in 6.4 litres that would stand at about 8 mmol/L, above the 5 the cells tolerate. The litres are what the engine derives: 12.0 a kilo harvested, set by ammonia.
- **Growth factors returned by the filter** and **runs lost 0.2% a day**. Humbird's design buys no growth factors and loses no runs, so neither lever has anything left to save.

## 3. The path from Humbird's design

| Step (each kept moved) | Cost | Change | Evidence |
|---|---|---|---|
| Humbird's design: his enhanced cells in an ordinary perfusion tank | **$16.04** |  | scenarios.reference(): a 3 ng cell that doubles in 24 hours and makes 0.054 mol of ammonia a kilo and 0.279 mol of lactate per mol of glucose; 5 mmol/L of ammonia and 50 of lactate tolerated; no lost runs; no growth factors bought; a food-grade plant; gas at up to 6 mm/s |
| Cells double in 16 hours | $12.32 | −3.72 | physics allows about 8 h (median); a meat line in suspension at 50 g/L or more doubling in 16 h or less by 2035: 7% (gf_and_doubling_bounds.md) |
| Cells of 5.3 ng in place of 3 ng | $12.16 | −0.16 | assumed by Risner 2021 (Table A2) and, as 5,000 µm³, by CE Delft 2021 (scenario 8); not measured in a meat cell line grown in suspension (study_comparison.md) |
| A food-grade plant with shared medium | $10.10 | −2.06 | nobody has built one (cheap_plant_study.md) |
| Dialyser-grade hollow fibres as the filter | $8.98 | −1.13 | nothing run with animal cells; holds 25% cells for a month: 15% (retention_alternatives.md) |
| Dissolved oxygen held at about half of air saturation | $8.98 | 0.00 | as pharma holds it; it changes nothing until the tank design makes oxygen the limit |
| The cheapest tank design that passes the checks on the CO₂ loop | $7.14 | −1.84 | nobody has run a stripping column or 1 bar of extra pressure with animal cells (gas_exchange_study.md) |
| Tanks of 25 m³ in place of 20 m³ | $7.02 | −0.12 | the size SuperMeat 2024 designs for; the tank design is chosen again and passes the same checks. The 211 m³ tanks of Negulescu 2023 cost more here: the cheapest design that passes the checks at that size has no extra pressure and holds a thinner culture (study_comparison.md) |
| The least medium flow at the lowest measured | $7.02 | 0.00 | changes nothing here: ammonia, not the least flow, sets the litres of medium |
| Culture up to 320 g/L in place of 258 | $7.02 | 0.00 | changes nothing here: oxygen holds the culture below both (thick_culture.md) |
| Medium at the nutrient floor | **$7.02** | 0.00 | changes nothing here: Humbird's design already pays only for what the cells eat, $2.00 a kilo (nutrient_floor.md) |

The path starts from Humbird's design, not from the low-lactate example, because every step is then one lever made more favourable. From the low-lactate example half the steps would be "take Humbird's value" on a lever where his design is the better.

The first row is `scenarios.reference()` with his cell written as its four traits (0.054 mol of ammonia a kilo, 0.279 mol of lactate per mol of glucose, 24 hours, 3 ng). It gives $16.04; `reference()` itself gives $16.03, because the traits are his figures to three decimals.

**What each step does.**

- **A 16-hour doubling (−$3.72).** A tank makes density times growth rate. Faster cells use more oxygen an hour, so the tank holds 96 g/L in place of 120, but it turns over half again as fast. The cells also spend less on upkeep per kilo, and the bubbles kill a smaller share of a faster growth.
- **Cells of 5.3 ng (−$0.16 here, −$0.42 once the tank design makes oxygen the limit).** A bigger cell uses less oxygen per gram, so the tank holds more of them: 111 g/L in place of 96 here, and 223 in place of 193 at the end of the path.
- **A food-grade plant with shared medium (−$2.06).**
- **Dialyser-grade fibres (−$1.13).**
- **Dissolved oxygen at about half of air saturation ($0.00).** CO₂ removal, not oxygen, holds the culture at 111 g/L here. The setpoint pays in the next step.
- **The tank design (−$1.84).** A stripping column takes the CO₂, 1 bar of extra pressure and a squat tank pass more oxygen, and the culture runs at 222 g/L.
- **Tanks of 25 m³ (−$0.12).** A slightly larger tank costs less per m³ to build. The 211 m³ tanks of Negulescu 2023 cost more ($7.67): the cheapest design that passes the checks at that size has no extra pressure and holds 156 g/L.
- **The last three steps change nothing here.** Ammonia sets the litres of medium, not the least flow. Oxygen holds the culture at 223 g/L, below both 258 and 320. Humbird's design already pays only for what the cells eat.

Each lever alone, from Humbird's design: the doubling time −$3.72, the plant −$2.96, the fibres −$1.87, the cell's weight −$0.86, the tank design −$0.59, the tank's size −$0.06, the others $0.00.

## 4. Where the $7.02 goes

| | $ a kilo harvested |
|---|---|
| Nutrients | 2.21 |
| Plant (capital, maintenance, insurance) | 1.90 |
| Labour | 0.95 |
| Bubble protectant | 0.72 |
| Utilities | 0.49 |
| Bought oxygen | 0.37 |
| Supplies and membranes | 0.39 |
| **Total** | **7.02** |

Bubbles kill 8.2% of the cells grown and 2% are lost at harvest, so 90% of the cells grown are harvested. The nutrient floor is $2.00 a kilo of cells grown.

With the estimates behind it drawn from their ranges (among them the plant's cost, the yearly charge, the upkeep share of the cells' oxygen, the protectant, the cells killed by bubbles), the cost is $8.5 at the median and 8 draws in 10 fall between $7.1 and $10.4. The point figure sits at the low end because the plant's cost and the bubble deaths can be much worse than their most likely values and only a little better.

Price parity with US minced beef or pork cuts ($12 a kilo) needs about $6.1 a kilo of cells (the shelf rule: cost plus $2.5, over 72%). The all-favourable case does not reach it.

## 5. The order the test holds

`tests/test_ordering.py` fails, naming the lever, if a later change breaks any of these.

1. `scenarios.all_favourable()`, the scenario `best`, the last row of `frontier.ladder()` and the page's "best level known" are one number from one set of `explore()` arguments.
2. The nutrient floor ($2.00) ≤ the all-favourable case ($7.02) ≤ Humbird's design, `scenarios.reference()` ($16.03) ≤ Humbird's best estimate with this model's additions ($36.21 with the model's own plant figure, $37.51 with his) ≤ the low-lactate example ($49.96) ≤ Published cells in perfusion ($183.15). No scenario costs less than the all-favourable case.
3. Lever by lever, the all-favourable case is at least as favourable as Humbird's design and as every scenario.
4. No lever, moved back to Humbird's value or to any other setting of its switch, makes the case cheaper.
5. Against the published studies (`study_comparison.md`): lever by lever the case is at least as favourable as every value a study states, unless the value is in the rejected list and breaks the limit it names; the case costs no more than each study's most favourable estimate in today's dollars, unless the study is listed as an exception (Risner 2021) with the assumptions that break a limit, and that study's design inside the limits is not below the case; every study is compared or listed with the reason it is not; no published tank size is cheaper with the tank design chosen again.

Humbird's best estimate sits above `scenarios.reference()` because they are different designs. His best estimate is fed-batch in a pharma-style plant at his own yearly charge (23.6%) with growth factors bought. `reference()` is his cells in perfusion in a food-grade plant at the mature-industry charge (17.3%) with no growth factors bought.

## 6. What this does not say

- It is not a forecast. Nobody has shown these levels together, and several have not been shown at all: a meat cell that makes this little waste, a 16-hour doubling in a dense suspension, dialyser-grade fibres holding animal cells for a month, a stripping column on a culture, a food-grade plant with shared medium.
- The tank is 25 m³, the cheapest of the sizes the published studies use. Sizes between those were not searched.
- Cleaning the medium for reuse and feeding fat are not in the case.
- The plant's cost per m³ and the staff are this model's own. Two studies cost a plant at a third as much; if that carried over, the case would be $6.03 (`study_comparison.md`, section 7).
