# Published cost studies against this model, lever by lever

Date: 2026-11-20. Code: `study_assumptions.py` (`STUDIES`, `STUDY_LEVERS`, `REJECTED`, `limits()`, `ESTIMATES`, `EXCEPTIONS`, `comparison()`, `modifications()`, `markdown()`), `scenarios.favourable_levers()` and `all_favourable()`, `page_studies.js`. Tests: `tests/test_ordering.py` (section 5), `tests/test_study_assumptions.py`. Costs are dollars per kilo of wet cells; "today's dollars" are 2025 dollars. The tables in sections 3 to 6 and 8 are printed by `study_assumptions.markdown()`.

The owner's rule (2026-11-20): the all-favourable case "should not lose to Humbird nor to any newer TEA", and "we should be rigorous, I think Risner had issues that conflicted with what Humbird showed was necessary".

> **Current figures (2026-11-22).** The tables of sections 5 and 8 are regenerated from `study_assumptions.markdown()`. The
> all-favourable case costs **$6.97** (section 1 below gives $7.62, as of 2026-11-20; the second batch of 2026-11-21 moved it).
> The mass-balance limit is 311 g of glucose a kilo (320 until 2026-11-21). In section 8, Humbird's own perfusion plant now adds
> $23.49 to his best estimate (+$16.98 on 2026-11-20), Negulescu's 211 m³ tanks
> $16.38 (+$18.80), every raising modification together $353.31 (+$275.01) and all together $335.48 (+$295.71). Prose figures
> outside the tables are as of 2026-11-20.

## 1. Result

- The all-favourable case is **$7.62** a kilo (2026-11-20, after the model's additions and the three corrections of section 12; it was
  $7.02, and $7.56 before the studies were added). One value now comes from a published study: tanks of 42 m³ (Negulescu 2023's
  smaller design), which cost least once a plant's cost follows what each tank brings with it. Cells of 5.3 ng (Risner 2021, CE
  Delft 2021) are no longer taken: no meat cell growing in suspension has been measured heavier than Humbird's 3 ng (section 12, A).
  At 5.3 ng the case would be $7.26.
- One published estimate is below it: Risner 2021's scenario 4, $1.95 in 2019 dollars, $2.46 today. It rests on four assumptions
  that break a limit (section 5). With those brought inside the limits its own design costs $8.89 in this engine.
- Every other estimate is above it. The closest is CE Delft 2021's $6.43, which is **$7.64** in today's dollars if its dollars are those
  of 2021 (the study does not say): two cents above the case. Its 30 years at no interest is rejected (section 12, B); taken, the case
  would be $6.99.
- Eleven study values are not taken (section 5). Two kinds of assumption are neither taken nor rejected, because they are not like for
  like with a lever of the engine (section 7). They need a decision.

## 2. The rule, and the limits

For every lever the engine has, the all-favourable case takes the most favourable value among this model's own favourable end, Humbird's design, and what any study in `STUDIES` assumes. A study's value is not taken when it breaks one of these limits:

| limit | value | source |
|---|---|---|
| The nutrient floor: cells cannot cost less than the nutrients they are built from | $2.00 a kilo of cells | `inputs.py`: 232 g of amino acids at feed-grade prices (GFI 2025), glucose, salts and vitamins; `nutrient_floor.md` |
| The mass balance: cells cannot be built and fuelled from less sugar than they burn | 311 g of glucose a kilo of cells (320 until 2026-11-21) | `inputs.py` `glucose_intensity`; Humbird 2021, Section 2.2: 0.36 kg a kilo of wet cells for his enhanced cell |
| The thickest culture that still flows | 258 g/L (cells at 25% of the volume) | Humbird 2021, Section 2.1 and Table 2.2, PDF pages 19 and 20. He takes a packing limit of 65% and stops where the culture is about twice as viscous as water |
| Oxygen transfer and CO₂ removal for the tank | computed by the engine | Humbird 2021, Section 2.3, PDF pages 29 to 34: gas at 0.006 m/s at most, 100 mbar of CO₂; a 20 m³ tank on 90% oxygen holds 120 g/L |
| The waste the cells tolerate against what they make | computed by the engine | Humbird 2021, Section 2.3, PDF page 31: 5 mmol/L of ammonia, 50 of lactate |
| A growth rate faster than any measured in animal cells | 15 hours to double | `inputs.py` `cr_td_engineering`: immortalised bovine muscle cells with serum, Stout 2023. Humbird (PDF page 24) adds that fast growth and little waste do not go together |
| A meat cell heavier than any measured growing in suspension | 3,000 pg (3 ng) | `inputs.py` `cr_mass_measured_max_pg`: the larger of Humbird's 3 ng and the heaviest credible measurement of a meat cell in suspension (SuperMeat 2024, 1.75 ng weighed, about 2.3 ng from its diameter). Added 2026-11-20 (section 12, A) |
| The plant must be repaid at a market rate of interest | 8.3% of the plant's cost a year (5.4% over 20 years) | An economic condition, not a physical limit: a long-run price must pay for the money a plant ties up, at a market rate. Humbird 2021, Section 3.1, PDF page 44, quotes 5.4% as the cost of capital of food processing, the lowest he gives |

**The financing condition is this note's addition.** The task named the first six limits. Without it, CE Delft's repayment over 30 years at no interest and Pasitka's cost lines with no payment on the plant would have to be taken, and the all-favourable case would be $6.99 or $6.57. Both are rejected for that reason (section 5). The page's interest lever still goes to 0%, with a chip "no interest (CE Delft 2021)", so a reader can see the effect.

**On the 320 g/L the all-favourable case allows.** Humbird's limit is 258 g/L. The 320 comes from this model's own side study (`thick_culture.md`), which gives a 20 m³ tank at 320 g/L a 6% chance of working. It changes nothing: oxygen holds the case at 155 g/L, below both. No study value between 258 and 320 is accepted because of it. Rejections on thickness are stated against Humbird's 258.

**In today's dollars no study's medium is below the nutrient floor.** Risner's $1.70 a kilo in 2019 dollars is $2.14 today, against the floor's $2.00. What Risner's and CE Delft's media break is the mass balance: 45 g and 15 g of sugar for a kilo, against about 320 g.

## 3. The all-favourable case, lever by lever

**Ammonia the cells make** (mol a kilo of cells; lower is favourable). Taken: **0.054**, from Humbird's design (2021).

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | 0.055 | the kind-of-cells switch at 'almost no ammonia or lactate' (sc_nh3_engineered) |
| Humbird's design (2021) | 0.054 | his enhanced cell (pf_nh3_efficient) |
| Pasitka 2024 | 0.14 | 2.4 g of ammonia a kilo of wet cells, measured (PDF page 4); derived: 2.4 / 17.03 |

Not stated by: CE Delft 2021, Risner 2021, Negulescu 2023, Garrison 2022, SuperMeat 2024, Lever VC 2025, GFI 2021, GFI 2026.

**Lactate the cells make** (mol per mol of glucose; lower is favourable). Taken: **0.279**, from this model's own favourable end.

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | 0.279 | the same setting (sc_lac_engineered) |
| Humbird's design (2021) | 0.279 | his enhanced cell: 0.5 per glucose burned or fermented |
| Pasitka 2024 | 1.05 | 76 g of lactate from 145 g of glucose a kilo of wet cells, measured (PDF page 4); derived |

Not stated by: CE Delft 2021, Risner 2021, Negulescu 2023, Garrison 2022, SuperMeat 2024, Lever VC 2025, GFI 2021, GFI 2026.

**Weight of a cell** (pg; higher is favourable). Taken: **3000**, from Humbird's design (2021).

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | 2000 | every setting of the kind-of-cells switch (sc_mass_selected_pg) |
| Humbird's design (2021) | 3000 | his assumed cell: a bigger cell uses less oxygen per gram |
| CE Delft 2021 | none | none that respects the limits; its 3610 is not taken (it breaks a limit: study_comparison.md); its 5160 is not taken (it breaks a limit: study_comparison.md) |
| Risner 2021 | none | none that respects the limits; its 5300 is not taken (it breaks a limit: study_comparison.md) |
| Negulescu 2023 | 3000 | 3 ng a cell (Section 2.2, PDF page 4) |
| SuperMeat 2024 | 1040 | 1.04 g per billion stem cells (PDF page 18) |

Not stated by: Garrison 2022, Pasitka 2024, Lever VC 2025, GFI 2021, GFI 2026.

**Doubling time** (hours; lower is favourable). Taken: **16**, from this model's own favourable end.

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | 16 | the old frontier's lever (gf_and_doubling_bounds.md); the growth switch stops at 24 |
| Humbird's design (2021) | 24 | his model cell |
| CE Delft 2021 | 30 | Table 5, PDF page 36 |
| Risner 2021 | 16 | scenarios 2 and 3 (Table A2, PDF page 19); its 8 is not taken (it breaks a limit: study_comparison.md) |
| Negulescu 2023 | 23 | Section 2.2, PDF page 4 |
| Pasitka 2024 | 61 | through the 20-day continuous run, measured (PDF page 2) |
| SuperMeat 2024 | 48 | 0.5 doublings a day while bleeding (PDF page 18); derived |

Not stated by: Garrison 2022, Lever VC 2025, GFI 2021, GFI 2026.

**Ammonia the cells tolerate** (mmol a litre; higher is favourable). Taken: **5**, from Humbird's design (2021).

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | 4 | what every scenario takes (sc_nh3_limit) |
| Humbird's design (2021) | 5 | his limit (pf_nh3_limit) |
| Pasitka 2024 | 3 | ammonia held below 3 mM (PDF page 2) |

Not stated by: CE Delft 2021, Risner 2021, Negulescu 2023, Garrison 2022, SuperMeat 2024, Lever VC 2025, GFI 2021, GFI 2026.

**Lactate the cells tolerate** (mmol a litre; higher is favourable). Taken: **50**, from Humbird's design (2021).

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | 35 | what every scenario takes (sc_lac_limit) |
| Humbird's design (2021) | 50 | his limit (pf_lac_limit) |
| Pasitka 2024 | 30 | lactate held below 30 mM (PDF page 2) |

Not stated by: CE Delft 2021, Risner 2021, Negulescu 2023, Garrison 2022, SuperMeat 2024, Lever VC 2025, GFI 2021, GFI 2026.

**Runs lost to contamination** (share of runs a day; lower is favourable). Taken: **0**, from Humbird's design (2021).

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | 0.002 | the losses switch at pharma's 0.2% a day |
| Humbird's design (2021) | 0 | his design loses none |

Not stated by: CE Delft 2021, Risner 2021, Negulescu 2023, Garrison 2022, Pasitka 2024, SuperMeat 2024, Lever VC 2025, GFI 2021, GFI 2026.

**Growth factors bought** (share of Humbird's price; lower is favourable). Taken: **0**, from this model's own favourable end.

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | 0 | the growth-factor switch at 'none bought' |
| Humbird's design (2021) | 0 | scenarios.reference() buys none |
| Risner 2021 | 0 | scenario 4 prices insulin, transferrin, FGF-2 and TGF-β at nothing (Table A3, PDF page 20) |

Not stated by: CE Delft 2021, Negulescu 2023, Garrison 2022, Pasitka 2024, SuperMeat 2024, Lever VC 2025, GFI 2021, GFI 2026.

**Price of the medium** ($ a litre above the nutrients the cells eat; lower is favourable). Taken: **0**, from this model's own favourable end.

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | 0 | the medium switch at the nutrient floor: $2.00 a kilo of cells at GFI's feed-grade prices |
| Humbird's design (2021) | 0.15 | explore()'s default, which meets the same floor; his own nutrients cost $4.34 a kilo today, more |

Not stated by: CE Delft 2021, Risner 2021, Negulescu 2023, Garrison 2022, Pasitka 2024, SuperMeat 2024, Lever VC 2025, GFI 2021, GFI 2026.

**Dissolved oxygen the tank is held at** (mmol a litre; lower is favourable). Taken: **0.1**, from this model's own favourable end.

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | 0.1 | what every scenario takes (sc_do_setpoint): a lower level passes more oxygen |
| Humbird's design (2021) | none | his tank implies about 0.28 |

Not stated by: CE Delft 2021, Risner 2021, Negulescu 2023, Garrison 2022, Pasitka 2024, SuperMeat 2024, Lever VC 2025, GFI 2021, GFI 2026.

**Least medium flow the cells need** (mL a gram of cells a day; lower is favourable). Taken: **3.7**, from this model's own favourable end.

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | 3.7 | the low end of pf_min_perfusion's range: the lowest flow measured (min_litres) |
| Humbird's design (2021) | none | scenarios.reference() takes the model's own (pf_min_perfusion) |

Not stated by: CE Delft 2021, Risner 2021, Negulescu 2023, Garrison 2022, Pasitka 2024, SuperMeat 2024, Lever VC 2025, GFI 2021, GFI 2026.

**Thickest culture the tank can stir** (g a litre; higher is favourable). Taken: **320**, from this model's own favourable end.

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | 320 | the old frontier's lever (thick_culture.md) |
| Humbird's design (2021) | none | scenarios.reference() takes the model's 258 (pf_x_visc) |
| CE Delft 2021 | 258 | 50 million cells a mL of 5,000 µm³ in scenario 8 (Table 5, PDF page 37; PDF page 27); derived: 25% of the volume, Humbird's own limit |
| Risner 2021 | 53 | scenario 1: 10 million cells a mL (Table A1, PDF page 19); derived at 5.3 ng: 5% of the volume; its 504 is not taken (it breaks a limit: study_comparison.md); its 1060 is not taken (it breaks a limit: study_comparison.md) |
| Negulescu 2023 | 100 | each step ends at 100 g of fresh cells a litre (Section 2.2, PDF page 4) |
| Pasitka 2024 | none | none that respects the limits; its 430 is not taken (it breaks a limit: study_comparison.md) |
| SuperMeat 2024 | 83 | 80 million cells a mL at 1.04 ng (PDF page 18); derived |
| Lever VC 2025 | 90 | 60 to 90 g/L at several companies (PDF page 3) |

Not stated by: Garrison 2022, GFI 2021, GFI 2026.

**The plant** (setting of the plant switch; the setting that costs least is taken). Taken: **lean**, from this model's own favourable end.

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | lean | the plant switch at 'a food-grade plant with shared medium' |
| Humbird's design (2021) | sterile | scenarios.reference(): his plant in a food-grade hall |

Not stated by: CE Delft 2021, Risner 2021, Negulescu 2023, Garrison 2022, Pasitka 2024, SuperMeat 2024, Lever VC 2025, GFI 2021, GFI 2026.

**The device that holds the cells back** (membrane device; the setting that costs least is taken). Taken: **dialyser**, from this model's own favourable end.

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | dialyser | the old frontier's lever: dialyser-grade hollow fibres (retention_alternatives.md), as explore() arguments {'flux': 2.5, 'membrane_life': 1000.0, 'membrane_price': 8.0, 'membrane_hw': 0.5} |
| Humbird's design (2021) | tff | scenarios.reference(): the engine's own filter loop |

Not stated by: CE Delft 2021, Risner 2021, Negulescu 2023, Garrison 2022, Pasitka 2024, SuperMeat 2024, Lever VC 2025, GFI 2021, GFI 2026.

**How the tank is run** (setting of the mode switch; the setting that costs least is taken). Taken: **perfusion**, from Humbird's design (2021).

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | perfusion, fedbatch100, fedbatch50, fedbatch | every setting of the mode switch |
| Humbird's design (2021) | perfusion | scenarios.reference() |

Not stated by: CE Delft 2021, Risner 2021, Negulescu 2023, Garrison 2022, Pasitka 2024, SuperMeat 2024, Lever VC 2025, GFI 2021, GFI 2026.

**Gas flow the cells tolerate** (setting of the gas switch; the setting that costs least is taken). Taken: **6**, from Humbird's design (2021).

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | 6, 4, 2 | every setting of the gas switch: more gas passes more oxygen and kills more cells |
| Humbird's design (2021) | 6 | his 6 mm a second |

Not stated by: CE Delft 2021, Risner 2021, Negulescu 2023, Garrison 2022, Pasitka 2024, SuperMeat 2024, Lever VC 2025, GFI 2021, GFI 2026.

**Added equipment for oxygen and CO₂, and tank shape** (settings of the two tank-design switches; the setting that costs least is taken). Taken: **pressure, square**, from this model's own favourable end.

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | design() | the cheapest pair that passes the checks on the CO₂ loop |
| Humbird's design (2021) | none, tall | an ordinary tall tank |

Not stated by: CE Delft 2021, Risner 2021, Negulescu 2023, Garrison 2022, Pasitka 2024, SuperMeat 2024, Lever VC 2025, GFI 2021, GFI 2026.

**Size of the tank** (m³; the setting that costs least is taken). Taken: **42**, from this model's own favourable end.

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | 20 | the model's tank (vm_str_m3) |
| Humbird's design (2021) | 20 | his fed-batch tanks; his perfusion tanks are 2 m³ (Sect. 4.2) |
| CE Delft 2021 | 10 | stirred tanks of 10 m³ working volume (Table 2, PDF page 13) |
| Risner 2021 | 20 | Table A1, PDF page 19 |
| Negulescu 2023 | 211 | stirred tanks of 211 m³; also 42 m³, and an airlift of 262 m³ that this engine does not price (Table 2, PDF page 8) |
| Garrison 2022 | 20 | four 20 m³ tanks (Section 2.3.1, PDF page 4) |
| Pasitka 2024 | 5 | 10 tanks of 5 m³ with tangential-flow filters; also 25 of 2 m³ and 2 of 25 m³ (PDF page 6) |
| SuperMeat 2024 | 25 | 25,000-litre tanks (PDF pages 18 and 20) |

Not stated by: Lever VC 2025, GFI 2021, GFI 2026.

**Yearly payment that repays the plant** (share of the plant's cost a year; lower is favourable). Taken: **0.08299**, from this model's own favourable end.

| source | value | where it is from |
|---|---|---|
| this model's own favourable end | 0.08299 | 5.4% over 20 years, the food-processing cost of capital Humbird quotes (plant_charge_mature, less the 9% of maintenance and insurance) |
| Humbird's design (2021) | 0.1457 | 7.5% over 10 years (Sect. 3.1); his yeast benchmark, 10% over 20 years, is 11.7% |
| CE Delft 2021 | 0.25 | payback in 4 years, its commercial criterion (Section 3.2.3, PDF page 24); its 0.0333333 is not taken (it breaks a limit: study_comparison.md) |
| Risner 2021 | 0.0882 | 90% debt at 5% and equity at 15% over 20 years, each with its own repayment (Table A7, PDF page 22); derived: 0.9 x 8.02% + 0.1 x 15.98% |
| Negulescu 2023 | 0.095 | straight-line depreciation over 10 years to a 5% salvage value, no interest (Section 2.3, PDF page 6) |
| Garrison 2022 | 0.1627 | 10% over 10 years (Section 2.3, PDF page 4; Table 2, PDF page 5) |
| Pasitka 2024 | none | none that respects the limits; its 0 is not taken (it breaks a limit: study_comparison.md) |

Not stated by: SuperMeat 2024, Lever VC 2025, GFI 2021, GFI 2026.


## 4. What a kilo of cells is fed

| study | medium for a kilo of cells, today's dollars | glucose for a kilo of cells, g |
|---|---|---|
| CE Delft 2021 |  | 15: 15 g of sugars for a kilo of meat, low medium use (Table 11, PDF page 41) |
| Risner 2021 | $2.14: scenario 4: 7.1 litres a kilo at $0.24 a litre, $1.70 in 2019 dollars (Table 2, PDF page 9); derived | 45: scenario 4: 0.0356 mol a litre (Table A4, PDF page 20) in 7.1 litres a kilo; derived |
| Negulescu 2023 | $15.62: 10.2 litres a kilo at $1.396 a litre, $14.2 (Section 2.2.1, PDF page 6); derived |  |
| Garrison 2022 | $21.63: $19.66 (Table 2, PDF page 5) |  |
| Pasitka 2024 | $14.47: 22.4 litres a kilo at $0.63 a litre, $14.1 (PDF pages 1 and 6); derived |  |
| SuperMeat 2024 | $15.70: 30.5 litres a kilo at $0.50 a litre, $15.3 (PDF page 20); derived |  |


## 5. Study values that are not taken, and the limit each breaks

| study | what it assumes | where | its value | the limit allows | the limit | the limit's source |
|---|---|---|---|---|---|---|
| Risner 2021 | 200 million cells a mL, each of 5,000 µm³ (scenario 4). The cells fill 100% of the tank, with no room for medium, which the study itself notes (Appendix A, PDF page 12). Humbird's limit for a culture that still flows is 25% of the volume. | Tables A1 and A2, PDF page 19 | 1060 g of wet cells a litre | 258 | the thickest culture that still flows | Humbird 2021, Section 2.1 and Table 2.2, PDF pages 19 and 20: cells at 25% of the volume, where the culture is about twice as viscous as water; spheres cannot pack beyond 65%. The all-favourable case allows 320 g/L (31%), this model's own stretch (research_notes/thick_culture.md gives a 20 m³ tank at 320 g/L a 6% chance); no study's value between 258 and 320 depends on it |
| Risner 2021 | 95 million cells a mL, each of 5,000 µm³ (scenarios 2 and 3). The cells are 47.5% of the tank's volume, against Humbird's limit of 25%. | Tables A1 and A2, PDF page 19 | 504 g of wet cells a litre | 258 | the thickest culture that still flows | Humbird 2021, Section 2.1 and Table 2.2, PDF pages 19 and 20: cells at 25% of the volume, where the culture is about twice as viscous as water; spheres cannot pack beyond 65%. The all-favourable case allows 320 g/L (31%), this model's own stretch (research_notes/thick_culture.md gives a 20 m³ tank at 320 g/L a 6% chance); no study's value between 258 and 320 depends on it |
| Risner 2021 | cells that double every 8 hours (scenario 4). No animal cell line has been measured doubling faster than about 15 hours. | Table A2, PDF page 19 | 8 hours to double | 15 | a growth rate faster than any measured in animal cells | inputs.py cr_td_engineering: immortalised bovine muscle cells with serum, Stout 2023, the fastest doubling of a meat cell line found; Humbird 2021, Section 2.2, PDF page 24, adds that fast growth and little waste do not go together |
| Risner 2021 | 0.0356 mol of glucose a litre in 7.1 litres of medium a kilo of cells (scenario 4). The medium holds 45 g of glucose for a kilo of cells, a seventh of what Humbird's most efficient cell burns. | Table A4, PDF page 20; Table 2, PDF page 9 | 45 g of glucose a kilo of cells | 311 | the mass balance: cells cannot be built and fuelled from less sugar than they burn | inputs.py glucose_intensity, from Humbird 2021, Section 2.2: 0.36 kg of glucose a kilo of wet cells for his enhanced cell (Reaction 2.11) |
| CE Delft 2021 | 15 g of sugars for a kilo of meat (low medium use). The medium holds 15 g of sugars for a kilo of meat, about a twentieth of what Humbird's most efficient cell burns. | Table 11, PDF page 41 | 15 g of glucose a kilo of cells | 311 | the mass balance: cells cannot be built and fuelled from less sugar than they burn | inputs.py glucose_intensity, from Humbird 2021, Section 2.2: 0.36 kg of glucose a kilo of wet cells for his enhanced cell (Reaction 2.11) |
| CE Delft 2021 | the plant paid back over 30 years with no interest (scenarios 6 to 8). The plant must be repaid at a market rate of interest: money lent for 30 years at no interest is not a cost of production. The study calls it a social criterion. | Section 3.2.3, PDF page 24 | 0.03333 share of the plant's cost a year | 0.083 | the plant must be repaid at a market rate of interest | an economic condition, not a physical limit: a long-run price must pay for the money a plant ties up, at a market rate. Humbird 2021, Section 3.1, PDF page 44, quotes 5.4% as the cost of capital of food processing, the lowest he gives; this model's 5.4% over 20 years is a payment of 8.3% a year. The interest lever still goes to 0%, with a chip 'no interest (CE Delft 2021)', so the effect can be seen |
| Pasitka 2024 | 130 million cells a mL, 43% weight per volume, in 5-litre glass tanks with serum. 43% is a weight of wet pellet in a 5-litre tank, not a culture stirred at scale; the study's own cell counts give 3.3 ng and 9.8 ng a cell. Its cost projection does not use it: it rests on a run held at 10 to 28 million cells a mL. | Abstract and Figure 1, PDF pages 1 and 3 | 430 g of wet cells a litre | 258 | the thickest culture that still flows | Humbird 2021, Section 2.1 and Table 2.2, PDF pages 19 and 20: cells at 25% of the volume, where the culture is about twice as viscous as water; spheres cannot pack beyond 65%. The all-favourable case allows 320 g/L (31%), this model's own stretch (research_notes/thick_culture.md gives a 20 m³ tank at 320 g/L a 6% chance); no study's value between 258 and 320 depends on it |
| Pasitka 2024 | no payment on the plant among its cost lines. The plant must be repaid at a market rate of interest: a plant that is never repaid is not a cost of production. Its Table S4 computes a charge of 14.6% of the plant a year, but Table S10 leaves it out of the total: with it, the large-scale case is $26.99 a kilo of cells in 2024 dollars, not $21.49. | Figure 4, PDF page 7; Supplementary Tables S4 and S10 | 0 share of the plant's cost a year | 0.083 | the plant must be repaid at a market rate of interest | an economic condition, not a physical limit: a long-run price must pay for the money a plant ties up, at a market rate. Humbird 2021, Section 3.1, PDF page 44, quotes 5.4% as the cost of capital of food processing, the lowest he gives; this model's 5.4% over 20 years is a payment of 8.3% a year. The interest lever still goes to 0%, with a chip 'no interest (CE Delft 2021)', so the effect can be seen |
| Risner 2021 | a cell of 5.00e-15 m³ at 1,060 kg per m³, 5.3 ng (every scenario). An assumption of the analysis, not a measurement. No meat cell growing in suspension has been measured above about 2.3 ng (SuperMeat 2024), so the heaviest allowed is Humbird's 3 ng. | Table A2, PDF page 19 | 5300 pg | 3000 | a meat cell heavier than any measured growing in suspension | inputs.py cr_mass_measured_max_pg: the larger of Humbird's 3 ng and the heaviest credible measurement of a meat cell growing in suspension (SuperMeat 2024, 1.75 ng weighed, about 2.3 ng from its diameter). The same rule as for growth: a value beyond what has been measured is rejected unless a measurement exists |
| CE Delft 2021 | a cell of 5,000 µm³ in scenario 8, 5.2 ng at 1.03 g/mL. An assumption of the analysis, not a measurement, beyond any meat cell measured growing in suspension. | Section 3.2.5, PDF page 27 | 5160 pg | 3000 | a meat cell heavier than any measured growing in suspension | inputs.py cr_mass_measured_max_pg: the larger of Humbird's 3 ng and the heaviest credible measurement of a meat cell growing in suspension (SuperMeat 2024, 1.75 ng weighed, about 2.3 ng from its diameter). The same rule as for growth: a value beyond what has been measured is rejected unless a measurement exists |
| CE Delft 2021 | a cell of 3,500 µm³, 3.6 ng at 1.03 g/mL. An assumption of the analysis, not a measurement, beyond any meat cell measured growing in suspension. | Table 5, PDF page 37 | 3610 pg | 3000 | a meat cell heavier than any measured growing in suspension | inputs.py cr_mass_measured_max_pg: the larger of Humbird's 3 ng and the heaviest credible measurement of a meat cell growing in suspension (SuperMeat 2024, 1.75 ng weighed, about 2.3 ng from its diameter). The same rule as for growth: a value beyond what has been measured is rejected unless a measurement exists |


## 6. Each study's most favourable estimate against the all-favourable case ($7.62)

| study | as published | where | as a kilo of wet cells | year of its dollars | in today's dollars | against the case |
|---|---|---|---|---|---|---|
| Humbird 2021 | $21.00 a kilo of wet cells | Table 4.7, column 2, PDF page 62 | $21.00: already a kilo of wet cells, with the yearly charge on the plant | 2018: his buildings and equipment are in 2018 dollars (Table 3.2, PDF page 40) | **$26.92** (consumer prices (BLS CPI-U), 2025 over 2018: x 1.282) | above |
| CE Delft 2021 | $6.43 a kilo of cultivated meat | Section 3.2.5, PDF page 28 (scenario 8) | $6.43: the product is cells after maturation, 70 to 77% water (PDF page 10), so it is taken as a kilo of wet cells; the plant is repaid over 30 years with no interest | 2021: not stated; the year of publication is taken (prices were collected from December 2020) | **$7.64** (consumer prices (BLS CPI-U), 2025 over 2021: x 1.188) | above |
| Risner 2021 | $1.95 a kilo of cell-based meat | Table 2, PDF page 9 (scenario 4) | $1.95: its meat is the wet mass of the cells (Appendix A, PDF page 15); only the tanks are charged as capital | 2019: energy prices are in January 2019 dollars and the medium at 2019 prices (PDF pages 5 and 6) | **$2.46** (consumer prices (BLS CPI-U), 2025 over 2019: x 1.259) | **below** |
| Negulescu 2023 | $16 a kilo of product without depreciation, $17 with | Table 2, PDF page 8 (262 m³ airlift) | $16.49: the product is about 97% wet cells (PDF page 6): $16 / 0.97, with the other 3% counted as free | 2022: not stated; it uses a 2021 plant-cost index and 2022 glucose prices | **$18.15** (consumer prices (BLS CPI-U), 2025 over 2022: x 1.100) | above |
| Garrison 2022 | $63.69 a kilo of meat; $17.10 with the cheapest published medium and tanks and labour cut by 75% | Table 2, PDF page 5; Section 3.2, PDF page 6 | $17.10: the meat is all cells, packed and delivered; the lower figure is a variant the study computes, not its estimate | 2022: not stated; the year of publication is taken | **$18.81** (consumer prices (BLS CPI-U), 2025 over 2022: x 1.100) | above |
| Pasitka 2024 | $6.2 a pound of a product that is half cells | Abstract, PDF page 1; Figure 4, PDF page 7 | $21.34: a kilo of product is half a kilo of wet cells and $3 of plant ingredients, as the study's own $6.8 a pound and $24.06 a kilo of cells imply: ($6.2 x 2.2046 - $3) x 2; no payment on the plant | 2024: not stated; the year of publication is taken (it compares with a 2024 retail price) | **$21.90** (consumer prices (BLS CPI-U), 2025 over 2024: x 1.026) | above |
| SuperMeat 2024 | $11.8 a pound without depreciation, $13.4 with | PDF page 20 | $26.01: the product is all cells after a short maturation: $11.8 x 2.2046 | 2024: not stated; the year of publication is taken | **$26.70** (consumer prices (BLS CPI-U), 2025 over 2024: x 1.026) | above |
| Lever VC 2025 | $10 to $15 a kilo of cell mass; some companies below $10, with no figure | PDF page 3 | $10.00: the low end of the range it states; wet or dry mass and whether the plant is charged are not stated | 2025: the year of the report | **$10.00** (consumer prices (BLS CPI-U), 2025 over 2025: x 1.000) | above |
| GFI 2021 | $6.43 a kilo ($2.92 a pound) | PDF page 2 | $6.43: CE Delft's figure, which this report summarises | 2021: as CE Delft 2021 | **$7.64** (consumer prices (BLS CPI-U), 2025 over 2021: x 1.188) | above |
| GFI 2026 | none | PDF pages 8 and 30 | not compared: it gives no cost of cells or of meat, only prices of medium a litre | | | |


## 7. Not taken and not rejected: two decisions for the owner

- **What the plant costs to build.** CE Delft 2021 gives $167k to $277k per m³ of tank (derived; Section 3.2.3, PDF page 23), Negulescu 2023 $209k per m³ at 42 m³ (derived; Table 2, PDF page 8), Risner 2021 $39k per m³ for the tanks alone (PDF page 7). The all-favourable case builds this model's own food-grade plant with shared medium, item by item from Humbird's equipment list: $609k per m³ in today's dollars. No physical limit rules the studies' figures out. They are not taken because the plants hold different equipment and make different amounts per m³, so a cost per m³ does not carry over. If the plant cost a third as much (the page's lowest setting, "two published designs"), the case would be **$6.03**; with CE Delft's financing as well, **$5.77**. Risner's tanks-only plant leaves out everything Humbird lists beside the tanks (seed train, medium preparation, harvest, utilities, buildings).
- **Staff.** Risner 2021 and Lever VC 2025 state none; CE Delft counts 130 to 200 for 10,000 tonnes. The case keeps the model's staff per m³ of tank, from Humbird.

A sensitivity value is not a study's assumption. Negulescu's 12-hour doubling with free medium ($2.5 a kilo, PDF page 9), SuperMeat's table down to $8.35 a pound (PDF page 21) and Humbird's $16 a kilo at a hundred thousand tonnes a year (PDF page 58) are ranges those studies scan, not designs they defend. Garrison's $17.10 is the lowest variant it computes and is compared.

## 8. The modifications on Humbird's best estimate ($26.99)

| modification | cost alone | change | the study's own reported cost |
|---|---:|---:|---|
| CE Delft 2021 and Negulescu 2023: Humbird 2021 design but with a food-grade plant without clean rooms | $25.15 | -1.84 | $6.43 a kilo of meat (CE Delft); $35 a kilo (Negulescu, 42 m³ tanks) |
| Humbird 2021, Appendix A: his design but with the financing of his baker's-yeast benchmark, 10% interest over 20 years | $25.22 | -1.77 | $21.00 a kilo (his best estimate) |
| CE Delft 2021: Humbird 2021 design but with the plant paid back over 30 years at no interest | $19.95 | -7.04 | $6.43 a kilo of meat |
| CE Delft 2021 and Negulescu 2023: Humbird 2021 design but with a plant that costs a third as much to build | $17.23 | -9.76 | $6.43 a kilo of meat (CE Delft); $35 a kilo (Negulescu, 42 m³ tanks) |
| Negulescu 2023: Humbird 2021 design but with a complete medium at $1.40 a litre | $34.32 | +7.33 | $35 a kilo (42 m³ tanks) |
| GFI 2026: Humbird 2021 design but with a complete medium at the $0.20 a litre companies announced | $24.65 | -2.34 | no cost a kilo reported |
| SuperMeat 2024 and Lever VC 2025: Humbird 2021 design but with a complete medium at $0.50 a litre | $26.82 | -0.17 | $29.5 a kilo (SuperMeat); $10 to $15 (Lever VC) |
| SuperMeat 2024: Humbird 2021 design but with perfusion through a membrane filter in 25 m³ tanks | $24.51 | -2.48 | $29.5 a kilo with depreciation (derived from $13.4 a pound) |
| Humbird 2021, Table 4.13: his design but with his own perfusion plant, 2 m³ tanks with an alternating-flow filter | $50.48 | +23.49 | $51.29 a kilo (his perfusion case, amino acids bought one by one) |
| Negulescu 2023: Humbird 2021 design but with stirred tanks of 211 m³ | $43.37 | +16.38 | $25 a kilo (211 m³ tanks) |
| SuperMeat 2024 and Lever VC 2025: Humbird 2021 design but with a culture no denser than the 83 g/L companies report | $37.05 | +10.05 | $29.5 a kilo (SuperMeat); $10 to $15 (Lever VC) |
| Humbird 2021, Table 4.6: his design but with amino acids bought one by one at his prices | $47.54 | +20.55 | $36.79 a kilo |
| Humbird 2021, Table 4.7: his design but with the waste of his wild-type cells, not his enhanced ones | $384.84 | +357.85 | $225.03 a kilo (fed-batch on hydrolysate) |
| Pasitka 2024: Humbird 2021 design but with the cells they measured in continuous perfusion | $685.04 | +658.04 | about $21 to $24 a kilo of wet cells (derived) |
| SuperMeat 2024: Humbird 2021 design but with the cells they report, 1.04 ng each and doubling every 48 hours | $58.02 | +31.03 | $29.5 a kilo with depreciation (derived from $13.4 a pound) |
| Every modification that lowers the cost alone, together | $17.10 | -9.89 | |
| Every modification that raises the cost alone, together | $614.59 | +587.60 | |
| All together (where two set the same lever, the later is used) | $362.47 | +335.48 | |

## 9. Levers added or widened on the page

| lever | before | now | why |
|---|---|---|---|
| Densest culture allowed, g of cells a litre (new; the engine's `x_visc`) | none | 20 to 450, starts at the model's 258 | companies report 55 to 100 g/L; Humbird's perfusion design 195 |
| Price of amino acids, $ a kilo | 2 to 20 | 2 to 110 | Humbird's amino acids bought one by one: ($19.08 − $0.10 of glucose) × 1.28 / 0.232 kg = $105 a kilo in today's dollars |
| Size of a stirred tank, m³ | 4 to 250 | 2 to 250 | Humbird's and Pasitka's 2 m³ perfusion tanks |
| Doubling time, hours | 12 to 60 | 12 to 61 | Pasitka's 61 hours |
| Interest rate, % a year | 2 to 15 | 0 to 15 | CE Delft and Negulescu charge none |
| Weight of one cell, ng | 1.0 to 3.5 in steps of 0.05 | 1.0 to 5.5 in steps of 0.01 | SuperMeat's 1.04 ng; Risner's 5.3 ng |

Still not representable: Negulescu's 262 m³ airlift (the page's airlift is 20 m³); Risner's 8-hour doubling (the lever stops at 12, and the value is rejected). Pasitka's 430 g/L can be set and changes nothing.

## 10. Corrections to earlier notes and to the study records

Checked against the PDFs on 2026-11-20 (every recorded assumption of every study, by a reader with no prior context, then the items below by hand).

| where | what it said | what the source says |
|---|---|---|
| `inputs.py` `plant_charge_mature`, and the panel's first version | Humbird's yeast benchmark supports cheaper financing | The benchmark is 10% over 20 years (Appendix A, PDF page 99): a higher interest rate than his 7.5%. Its yearly payment is lower (11.7% against 14.6%) only because of the 20 years. The 5.4% is the food-processing cost of capital he quotes in Section 3.1 |
| the panel's first version | CE Delft "at 2% interest", the lever's floor then | It states payback years (4 or 30) and divides the investment by them: $110M or $15M a year (PDF page 24). No interest rate is used |
| CE Delft record | 4,300 perfusion reactors | Table 5 (PDF page 36) prints 4,300; Table 2 (PDF page 13) and the costing use 430 |
| CE Delft record | "$116 to $22,421 at current medium prices" | Current prices are scenarios 1 to 3: $150 to $22,421. $116 already assumes cheaper growth factors (Figure 4, PDF page 18) |
| CE Delft record | cells are 17.5% of the volume | In scenario 8, the $6.43 one, the cell is 5,000 µm³: 25% of the volume (PDF page 27) |
| Garrison record | medium at "$374/L" | A misprint on PDF page 6. Table 2 prices it at $3,743 a kL and PDF page 3 says $3.74 a litre |
| Garrison record | 10% over 10 years stated "for the cold store" | Stated for the tanks (Section 2.3, PDF page 4) |
| `frontier.md` ("a larger tank a few per cent cheaper") and the panel's first version ("larger tanks raise the cost") | one sentence each way on tank size | Negulescu's cost falls with size because it sets no limit from CO₂ (PDF page 11). In this model both sentences are partly right: see section 8 |
| Pasitka record, `inputs.py` `cr_mass_feed`, the page's chip at 3.3 ng | 430 g/L in the 1.8-litre continuous run; 3.3 ng a cell | The 130 million cells a mL (43% w/v) are from 5-litre glass tanks with 10% serum (Figure 1, PDF page 3). The continuous run was held at 10 to 28 million a mL. Its 1.7 kg from 173 billion cells gives 9.8 ng a cell (PDF page 2), so the weights are of wet pellet and do not agree. The chip is removed and the modification leaves the cell's weight at Humbird's |
| Pasitka record | $6.8 a pound on PDF pages 1 and 6 | $6.2 a pound in the abstract (PDF page 1); $6.80 and $6.22 in Figure 4 (PDF page 7) |
| Risner record | a cost of "meat" | Its meat is the wet mass of the cells (Appendix A, PDF page 15) |
| Lever VC record | "operating cost only (no charge on the plant)" | The report says only "production COGS for cell mass" (PDF page 3). Whether the plant is charged is not stated |
| Humbird record | wild-type lactate 1.44 mol per mol of glucose | 0.474 / 0.333 = 1.42 (Reaction 2.9) |
| `LEVER_REFS` | Pasitka's 61-hour doubling missing | Added, with each study's value on every lever it states |

Not verified: that all of Humbird's costs are in 2018 dollars (only his buildings and equipment are labelled so); Negulescu's supplementary tables (not in the folder). Pasitka's are public and were read on 2026-11-21
([evidence_pasitka_supplement.md](evidence_pasitka_supplement.md)): the missing plant payment is confirmed (Tables S4 and S10).
They also list 81 g of amino acids a kilo of cells at $30.6 a kilo, a third of this model's 232 g; whether its "other"
nutrients ($5.85 a kilo) include a hydrolysate that makes up the rest is not stated, so it is not counted as a broken limit.

## 12. Three corrections (2026-11-20, second pass)

**A. The weight of a cell follows the rule for the doubling time.** The case had adopted 5.3 ng a cell from Risner 2021 (Table A2)
and CE Delft 2021 (5,000 µm³ in scenario 8, 5.2 ng; its base cell is 3,500 µm³, 3.6 ng). These are assumptions of those analyses,
not measurements. A doubling faster than any measured in animal cells is rejected; by the same rule a meat cell heavier than any
measured is rejected unless a meat cell growing in suspension has been measured at that weight. The heaviest found (repository
notes, the two books' text, the FDA filings):

| cell | weight | grown | source |
|---|---|---|---|
| Atlantic mackerel Mack1 before its crisis, 18.3 µm | 3.3 to 3.4 ng | on a surface, 20% serum | Saad et al. 2023 (`species_cell_parameters.md`) |
| Mack1 after its crisis, 16.8 µm | 2.6 ng | on a surface | the same |
| SuperMeat's fat-differentiated chicken cells | 1.75 ng weighed; 2.2 to 2.3 ng from a 16 µm diameter | in suspension, scaffold-free | SuperMeat 2024, PDF pages 3 and 15-16 (company report) |
| chicken DF-1 fibroblasts | about 1.0 ng | in suspension | Tufts preprint, 2025 |

Not used as the bound: Pasitka 2024's 3.3 ng (430 g/L over 130 million cells a mL) and 9.8 ng (1.7 kg over 173 billion cells): both
are wet-pellet weight over cell count and disagree with each other by a factor of three; the Cultivated Meat book's 3.5 ng, which is
calculated from a techno-economic analysis (Myers et al. 2023). No mature adipocyte has a measured size in suspension. So the bound is
the larger of Humbird's 3 ng and the heaviest credible suspension measurement (about 2.3 ng): **3 ng**. Risner's 5.3 ng and CE Delft's
5.2 and 3.6 ng are recorded as rejected. Cost effect: the all-favourable case at 5.3 ng is $7.26, at 3 ng $7.62 (+$0.36).

**B. Financing is an economic condition, not a physical limit.** The rule stays: a long-run price must pay for the money a plant ties
up at a market rate. The rejections table names it "the plant must be repaid at a market rate of interest"; CE Delft's 30 years at
no interest and Pasitka's plant with no payment are rejected for that reason. 0% stays reachable on the interest lever, with the chip
"no interest (CE Delft 2021)".

**C. Dollars of other years.** The consumer-price figures were typed from memory. They are now the official BLS CPI-U annual
averages (series CUUR0000SA0), fetched from the BLS API on 2026-11-20 and stored once in `inputs.py` (`cpi_u_2018` to `cpi_u_2025`:
251.107, 255.657, 258.811, 270.970, 292.655, 304.702, 313.689, 321.943; BLS has no October 2025 figure, its 2025 average is its own).
Every study, Humbird's included, is converted the same way (`study_assumptions.cpi`). Until now Humbird's estimate took the plant-cost
index on his capital and consumer prices on the rest ($27.45); by consumer prices alone it is $26.92 (−1.9%). Every other estimate
moved by 0.03% or less. None moved by more than 2%.

## 11. What moved, and what is not repinned

The all-favourable case moved from $7.56 to $7.02, and its ladder gained two steps (`frontier.md`). Repinned here: `tests/test_frontier.py`, `tests/test_ordering.py`, `tests/test_easy_view.py` (the new lever), `tests/test_study_assumptions.py`. Not repinned, and they quote the all-favourable case, its density (193 g/L, now 223), its band or its share: `tests/test_golden.py`, `tests/test_scenarios.py`, and any test or note that pins `SCENARIOS["best"]`; `RESULTS.md`, `METHODS.md`, `README.md`, `CHANGELOG.md`, `TODO.md`; the notes that cite $7.56 (`cost_scenarios.md`, `thick_culture.md`, `tank_size.md`, `nutrient_floor.md` and others).

Since 2026-11-24 the medium lever reaches $1.40 a litre, so Negulescu's $1.40 is a modification in the table above and Pasitka's $0.63 can be set. The page also offers six starting sets (`study_assumptions.SETS`): every assumption of one study that has a lever, together on Humbird's best estimate.

## 13. The starting sets: each study as a reasonable but ambitious long-term estimate, assumption by assumption (2026-11-24)

The owner, 2026-11-24: optimistic assumptions are fine "but they should be possible too"; of Pasitka's 61 hours, "that is not the
long term ambition ... Revise all the TEAs to make sure they propose reasonable but ambitious long term estimates"; and "We should
make clear exactly what we modified from each TEA, so it is auditable". Each set (`study_assumptions.SETS`) is the study's own
design on Humbird's best estimate; every assumption is listed below with what the study says and where, what the set uses, and why.
The page shows the same table under the side bar's buttons; the used values are written from the settings the page prices, and
tests/test_study_assumptions.py checks that every lever a set moves has a row. Anything not listed is Humbird's best estimate.

The reasons:

- **Kept**: the study's value.
- **The study's own projection**: the study's more favourable scenario or sensitivity, not its base case.
- **Long-term target**: the study's value is what one lab run or today's ingredients gave; the set uses the long-term target.
- **Corrected**: the study's value is beyond a limit of this model; the set uses the nearest possible value.
- **Not stated: Humbird's**: the study does not give it; Humbird's best estimate is kept.
- **Not stated: this model's**: the study does not give it, and Humbird's design has no equivalent the set can keep; this model's default is used.
- **Not set on this page**: the page has no lever for it; the set leaves it out.
- **Worked out by this model**: this model works it out from the cells and the tank, whatever the study states.

The long-term targets: Humbird's design cells (doubling every 24 hours, his low ammonia and lactate; most studies project 23 to 30
hours, and no serum-free meat cell has been published doubling this fast: 39 hours, Stout 2022) and a complete medium at $0.20 a
litre (what several companies announced in 2025, GFI 2026, not audited; the model never charges less than the $2.00 of nutrients a
kilo of cells eats). The correction on financing: a plant is repaid with interest at a market rate, Humbird's 7.5% over the study's
own years where it charges none.

### Humbird's perfusion design (2021): $50.48 a kilo of cells (plant $32.94, running $17.54)

His other design: perfusion in 2 m³ tanks with an alternating-flow filter, on the plant hydrolysate of his best estimate. The study itself reports $51.29 a kilo of wet cells in 2018 dollars with amino acids bought one by one (his Table 4.13).

| assumption | what the study says, and where | what the set uses | why |
|---|---|---|---|
| Vessel and way of running | perfusion in 96 stirred tanks (Section 4.2, PDF page 66) | a stirred tank in perfusion | Kept |
| Tank size | 2 m³, the largest an ATF 10 serves (Section 4.2, PDF page 66) | 2 m³ | Kept |
| Device that holds the cells back | alternating-flow filters (Section 4.2, PDF page 66) | alternating-flow filters | Kept |
| Nutrients | amino acids bought one by one, $18.39 a kilo of cells (Table 4.13, PDF page 69) | his plant hydrolysate, as in his best estimate (Table 4.7, column 2) | The study's own projection |
| Density | 195 g of cells a litre (Section 4.2, PDF page 66) | 146 g of cells a litre, limited by oxygen supply | Worked out by this model |
| Everything else | his best estimate's cells, plant and financing | the same | Kept |

### CE Delft 2021's assumptions on Humbird's design: $12.96 a kilo of cells (plant $5.28, running $7.67)

Its most favourable scenario (8): a cheap food-grade plant without clean rooms paid back over 30 years, 10 m³ tanks, cells of 3.6 ng doubling every 30 hours. The study itself reports $6.43 a kilo of meat in its most favourable scenario.

| assumption | what the study says, and where | what the set uses | why |
|---|---|---|---|
| Plant grade | food grade, no clean rooms (Section 2.3.2, PDF page 13) | a food-grade plant | Kept |
| Plant cost | about $167k to $277k per m³ of tank (derived; Section 3.2.3, PDF pages 23 and 27) | 0.34 times this model's plant: $353k per m³ of tank | Corrected |
| Years to repay the plant | 30, its social criterion (Section 3.2.3, PDF page 24) | 30 years | Kept |
| Interest on the plant | none: the investment divided by 30 years (Section 3.2.3, PDF page 24) | 7.5% interest | Corrected |
| Tank size | 10 m³ working volume (Table 2, PDF page 13) | 10 m³ | Kept |
| Way of running | semi-continuous, three harvests (Table 5, PDF page 36) | fed-batch, as Humbird | Not set on this page |
| Doubling time | 30 hours (Table 5, PDF page 36) | 30 hours | Kept |
| Weight of a cell | 3,500 µm³ (Table 5, PDF page 37); 3.6 ng at 1.03 g/mL (derived) | 3.61 ng | Kept |
| Medium price | low medium use at future prices, with cheaper growth factors; no price a litre (Table 11, PDF page 41; Section 3.2.5) | $0.20 a litre in 2025 dollars, growth factors in it | Long-term target |
| Growth factors bought on top | included in its medium at future prices (Section 3.2.5) | none | Long-term target |
| Sugar fed | 15 g of sugars a kilo of meat (Table 11, PDF page 41) | what this model's mass balance gives (311 g of glucose a kilo of cells at Humbird's growth) | Corrected |
| Density | 50 million cells a mL, 18% of the volume (Table 5, PDF page 37) | 117 g of cells a litre, limited by waste build-up | Worked out by this model |
| Maturation | a second stage in 2 m³ perfusion reactors (Table 2, PDF page 13) | left out: cells as grown | Not set on this page |
| Waste the cells make | not stated | Humbird's | Not stated: Humbird's |

### Risner 2021's assumptions on Humbird's design: $10.95 a kilo of cells (plant $3.39, running $7.56)

Its most favourable scenario (4), brought inside the limits. The study itself reports $1.95 a kilo of wet cells in 2019 dollars (scenario 4).

| assumption | what the study says, and where | what the set uses | why |
|---|---|---|---|
| Tank size | 20 m³ (Table A1, PDF page 19) | 20 m³ | Kept |
| Way of running | batches (Appendix A, PDF page 12) | fed-batch, as this page prices the scenario elsewhere | Not set on this page |
| Doubling time | 8 hours in scenario 4 (Table A2, PDF page 19) | 15 hours | Corrected |
| Weight of a cell | 5,000 µm³, 5.3 ng (Table A2, PDF page 19) | 3 ng, Humbird's; heavier than any measured for meat cells | Corrected |
| Density | 200 million cells a mL, which fills the tank (Table A1, PDF page 19) | 92 g of cells a litre, limited by CO2 removal | Corrected |
| Medium price | $0.24 a litre in 2019 dollars in scenario 4 (Section 3, PDF page 9) | $0.30 a litre in 2025 dollars, growth factors in it | The study's own projection |
| Growth factors bought on top | priced at nothing in scenario 4 (Table A3, PDF page 20) | none | The study's own projection |
| Plant cost | the tanks only, $778,000 for a 20 m³ tank (PDF page 7) | 0.34 times this model's plant: $309k per m³ of tank | Corrected |
| Interest on the plant | 90% debt at 5%, equity at 15% (Table A7, PDF page 22) | 6% interest | Kept |
| Years to repay the plant | 20 (Table A7, PDF page 22) | 20 years | Kept |
| Fixed manufacturing costs | 15% of the plant a year (Tables A1 and A7) | this model's labour, energy and supplies | Not set on this page |
| Waste the cells make, and what they tolerate | no limit set (Appendix A, PDF page 16) | Humbird's | Corrected |

### Negulescu 2023's assumptions on Humbird's design: $11.06 a kilo of cells (plant $4.85, running $6.21)

Its smaller stirred plant: fed-batch in 42 m³ tanks to 100 g a litre, a cheap food-grade plant, cells doubling every 23 hours. The study itself reports $35 a kilo of product with 42 m³ tanks.

| assumption | what the study says, and where | what the set uses | why |
|---|---|---|---|
| Plant grade | food grade, 304 stainless steel (Section 2.3, PDF page 6) | a food-grade plant | Kept |
| Plant cost | $438M for the 42 m³ plant (Table 2, PDF page 8) | 0.34 times this model's plant: $236k per m³ of tank | Corrected |
| Interest on the plant | none: straight-line depreciation (Section 2.3, PDF page 6) | 7.5% interest | Corrected |
| Years to repay the plant | 10, with a 5% salvage value (Section 2.3, PDF page 6) | 10 years | Kept |
| Tank size | 42 m³; also 211 m³ and a 262 m³ airlift (Table 2, PDF page 8) | 42 m³ | Kept |
| Way of running | fed-batch (Section 2.2, PDF page 4) | fed-batch | Kept |
| Densest culture | 100 g of cells a litre (Section 2.2, PDF page 4) | no more than 100 g of cells a litre | Kept |
| Doubling time | 23 hours (Section 2.2, PDF page 4) | 23 hours | Kept |
| Medium price | $1.396 a litre, from 2022 bulk prices of a published serum-free medium (Section 2.2.1, PDF page 6) | $0.20 a litre in 2025 dollars, growth factors in it | Long-term target |
| Growth factors bought on top | included in its medium (Section 2.2.1, PDF page 6) | none | Kept |
| Differentiation | 10 days in the tank (Section 2.2, PDF page 4) | left out: cells as grown | Not set on this page |
| Waste the cells make | Humbird's enhanced metabolism (Section 2.2.1, PDF page 6) | Humbird's | Kept |

### Garrison 2022's assumptions on Humbird's design: $10.97 a kilo of cells (plant $5.39, running $5.58)

Its most favourable variant: Specht's cheapest medium, labour and bioreactors cut by 75%. The study itself reports $17.10 a kilo of meat, packed and delivered, in its most favourable variant; $63.69 as its base case.

| assumption | what the study says, and where | what the set uses | why |
|---|---|---|---|
| Tank size | four 20 m³ tanks (Section 2.3.1, PDF page 4) | 20 m³ | Kept |
| Way of running | half of each tank harvested ten times in a 51-day cycle (Section 2.3.1, PDF page 4) | fed-batch | Not set on this page |
| Medium price | $0.28 a litre, Specht 2020's lowest scenario, in its variant; $3.74 in its base case (Section 3.2.1, PDF page 6) | $0.35 a litre in 2025 dollars, growth factors in it | The study's own projection |
| Growth factors bought on top | included in the medium (Section 3.2.1, PDF page 6) | none | The study's own projection |
| Labour | 94 staff, cut by 75% in its variant (Table 2; Section 3.2.1) | 0.25 times this model's labour | The study's own projection |
| Plant cost | $60M of equipment for 80 m³, $750k per m³ (derived), cut by 75% in its variant (Section 2.3.1; Section 3.2.1) | 0.34 times this model's plant: $309k per m³ of tank | Corrected |
| Interest on the plant | 10% (Section 2.3, PDF page 4) | 10% interest | Kept |
| Years to repay the plant | 10 (Section 2.3, PDF page 4) | 10 years | Kept |
| Cells | not described | Humbird's | Not stated: Humbird's |

### Pasitka 2024's assumptions on Humbird's design: $17.63 a kilo of cells (plant $11.51, running $6.12)

Its plant with tangential-flow filters, with the long-term targets for the cells and the medium. The study itself reports $24.06 a kilo of wet cells for this design in 2024 dollars (its Table S10), or $32.66 with the payment on the plant its Table S4 works out.

| assumption | what the study says, and where | what the set uses | why |
|---|---|---|---|
| Vessel and way of running | continuous perfusion (PDF page 6) | a stirred tank in perfusion | Kept |
| Device that holds the cells back | tangential-flow filters (PDF page 6) | a membrane filter loop (tangential flow) | Kept |
| Tank size | 10 tanks of 5 m³ (PDF page 6) | 5 m³ | Kept |
| Plant cost | $63.1M for 50 m³ of tank (Table S4) | 0.76 times this model's plant: $1,293k per m³ of tank | Kept |
| Interest on the plant | 14.6% a year worked out in Table S4 and left out of the total (Table S10) | Humbird's | Corrected |
| Years to repay the plant | with the 14.6% above (Table S4) | Humbird's | Corrected |
| Filter membranes | 24 a year at $16,000 for about 24 million litres, about 2 cents a litre filtered (Table S6) | $50 a m² | Kept |
| Cells lost | 1.3% of production (PDF page 6) | 1.3% | Kept |
| Medium price | $0.63 a litre, the 2024 price of its animal-free medium (Abstract) | $0.20 a litre in 2025 dollars, growth factors in it | Long-term target |
| Growth factors bought on top | included in its medium (Figure 2b) | none | Kept |
| Doubling time | 61 hours in a 1.8-litre run (PDF page 2) | Humbird's design cells (the long-term target: most studies project 23 to 30 hours): 24 hours | Long-term target |
| Waste the cells make | 0.14 mol of ammonia a kilo, 1.05 mol of lactate per mol of glucose, in that run (PDF page 4) | Humbird's design cells (the long-term target: most studies project 23 to 30 hours) | Long-term target |
| Ammonia and lactate the cells tolerate | held below 3 mM and 30 mM in that run (PDF page 2) | Humbird's 5 mM and 50 mM | Long-term target |
| Glucose and amino acids fed | 145 g and 81 g a kilo of cells (PDF page 4; Table S5) | what this model's mass balance gives | Corrected |
| Weight of a cell | 3.3 ng or 9.8 ng, from two of its figures (Abstract; PDF page 2) | 3 ng | Not stated: Humbird's |
| Density | up to 130 million cells a mL with serum in 5-litre tanks (Abstract) | 146 g of cells a litre, limited by oxygen supply | Worked out by this model |
| Labour | Table S8 | this model's | Not set on this page |

### SuperMeat 2024's assumptions on Humbird's design: $25.46 a kilo of cells (plant $13.64, running $11.82)

Its plant: perfusion through a membrane filter in 25 m³ tanks, its medium at scale, with the long-term target for the cells. The study itself reports $29.5 a kilo of cultivated chicken with depreciation (derived from $13.4 a pound).

| assumption | what the study says, and where | what the set uses | why |
|---|---|---|---|
| Vessel and way of running | perfusion with continuous bleeding (PDF page 18) | a stirred tank in perfusion | Kept |
| Tank size | 25,000 litres (PDF pages 18 and 20) | 25 m³ | Kept |
| Weight of a cell | 1.04 g per billion stem cells (PDF page 18) | 1.04 ng | Kept |
| Doubling time | half a doubling a day while bled, from 10-litre runs (PDF page 18) | Humbird's design cells (the long-term target: most studies project 23 to 30 hours): 24 hours | Long-term target |
| Density | 80 million cells a mL, 83 g a litre, from 10-litre runs (PDF page 18) | 85 g of cells a litre, limited by CO2 removal | Long-term target |
| Medium price | under $0.50 a litre at scale (PDF pages 3 and 18) | $0.50 a litre in 2025 dollars, growth factors in it | Kept |
| Growth factors bought on top | included in its medium (PDF page 7) | none | Kept |
| Cells lost | 3% rejected (PDF page 18) | 3% | Kept |
| Interest on the plant | none: depreciation only (PDF page 20) | 7.5% interest | Corrected |
| Years to repay the plant | not stated | 10 years | Not stated: Humbird's |
| Plant cost | not given per m³ | Humbird's | Not stated: Humbird's |
| Labour | 100 staff and 13 outsourced (PDF page 18) | this model's | Not set on this page |

### Ark Biotech 2023's assumptions on Humbird's design: $28.75 a kilo of cells (plant $19.28, running $9.47)

Its levers within reach: 25 m³ fed-batch tanks to 75 g a litre and a medium at $0.25 a litre. The study itself reports $4.4 a kilo of cells with all four of its levers ($2.0 a pound); $65.0 as its baseline.

| assumption | what the study says, and where | what the set uses | why |
|---|---|---|---|
| Tank size | 25,000-litre stirred tanks (Exhibit 8, PDF page 12) | 25 m³ | Kept |
| Way of running | fed-batch (Exhibit 6, PDF page 8) | fed-batch | Kept |
| Weight of a cell | 2,500 picograms (Exhibit 1, PDF page 4) | 2.50 ng | Kept |
| Doubling time | 24 hours after a 2-day lag (Exhibit 3, PDF page 7) | 24 hours | Kept |
| Densest culture | 30 million cells a mL as its lever, 20 million as baseline (Exhibit 1, PDF page 4) | no more than 75 g of cells a litre | The study's own projection |
| Medium price | $0.25 a litre as its lever, $2 as baseline (Exhibit 1, PDF page 4) | $0.26 a litre in 2025 dollars, growth factors in it | The study's own projection |
| Growth factors bought on top | included in its medium (Exhibit 2, PDF page 5) | none | Kept |
| Interest on the plant | none: depreciation (Exhibit 8, PDF page 12) | 7.5% interest | Corrected |
| Years to repay the plant | 15 (Exhibit 8, PDF page 12) | 15 years | Kept |
| Larger tanks | its own design up to 1,000 m³ as a lever (Exhibit 8, PDF page 12) | left out: this model finds larger tanks dearer, because they clear less CO₂ | Not set on this page |
| Differentiation | a 128% gain in mass as a lever (Exhibit 1, PDF page 4) | left out: cells as grown | Not set on this page |
| Plant cost | not given per m³ | Humbird's | Not stated: Humbird's |

### Gourmey and Arthur D. Little 2025's assumptions on Humbird's design: $16.65 a kilo of cells (plant $9.63, running $7.02)

Its announced plant: six 5 m³ tanks run continuously, cells doubling in under 16 hours, medium at €0.20 a litre. The study itself reports €7 a kilo, of cells or of a product half cells (not stated).

| assumption | what the study says, and where | what the set uses | why |
|---|---|---|---|
| Vessel and way of running | continuous runs in suspension (company announcement, 28 May 2025) | a stirred tank in perfusion | Kept |
| Device that holds the cells back | not stated | a membrane filter loop (tangential flow) | Not stated: this model's |
| Tank size | six 5,000-litre bioreactors (company announcement, 28 May 2025) | 5 m³ | Kept |
| Plant cost | under €35M a facility, under €1.17M per m³ (derived; company announcement) | 0.76 times this model's plant: $1,316k per m³ of tank | Kept |
| Doubling time | under 16 hours (press report, Green Queen, 28 May 2025) | 16 hours | Kept |
| Medium price | €0.20 a litre (company announcement, 28 May 2025) | $0.23 a litre in 2025 dollars, growth factors in it | Kept |
| Growth factors bought on top | none (company announcement, 28 May 2025) | none | Kept |
| Output | 1,700 tonnes a year from 30 m³, 57 tonnes a m³ (derived; company announcement) | 32.3 tonnes a m³ of tank a year | Worked out by this model |
| Density, litres of medium, weight of a cell, financing | not stated | Humbird's, or this model's limits | Not stated: Humbird's |

The all-favourable example: $6.97 (plant $1.87, running $5.09).

No button: Humbird's wild-type cells (a sensitivity case of his, not a long-term estimate; it stays as a box in "Why published cost studies disagree"); Lever VC 2025 and Aleph Farms 2025 (no design published); GFI 2021 (CE Delft's study); GFI 2026 (a medium price only); Cellular Agriculture Ltd 2024 (hollow-fibre reactors at a scale this page cannot price).

Earlier versions of the Pasitka set, the same day: $259.07 (the measured ratio of lactate to glucose on this engine's glucose
burn and the run's 3 and 30 mM), $91.13 (lactate per kilo as measured), $59.16 (the study's plant cost and Humbird's tolerances),
$45.52 (the study's own filter cost, which an earlier version had wrongly replaced with Humbird's pharma membranes); then the
long-term targets. The Negulescu set cost $106.98 with its 10 days of differentiation; the sets price cells as grown.

### Plant against running costs

The page plots each study's own plant and running costs a kilo (`study_assumptions.SPLITS`, 2025 dollars) and its set on this
page's model, joined by a line, with the nutrient floor ($2.00 of running cost), the all-favourable example and the total a 1% share
needs. "Plant" is the yearly payment with interest, maintenance and insurance.

| study | as it reports it: plant | running | how |
|---|---:|---:|---|
| Humbird 2021, best estimate | $15.07 | $12.38 | his Table 4.7, column 2: plant (capital charge, maintenance, insurance) $11.33, the rest $9.67, in 2018 dollars |
| Humbird 2021, perfusion | $30.07 | $36.74 | his Table 4.13: plant $22.61, the rest $28.68, in 2018 dollars, with amino acids bought one by one (the set uses his hydrolysate) |
| CE Delft 2021 | $1.27 | $6.37 | scenario 8: $6.43 a kilo; its plant, $320M over 30 years with no interest, on 10,000 tonnes a year is $1.07 (derived; Section 3.2.5, PDF page 27); the rest $5.36. The year of its dollars is not stated: 2021 is taken |
| Negulescu 2023 | $11.00 | $27.50 | 42 m³ tanks: $35 a kilo with depreciation, $25 without (Table 2, PDF page 8), so $10 of plant; the year of its dollars is not stated: 2022 is taken. Its medium at $1.40 a litre (the set uses $0.20) |
| Garrison 2022 | $4.90 | $13.91 | its most favourable variant, $17.10 a kilo (Section 3.2.1, PDF page 6): tanks and equipment at a quarter of its $17.81 (Table 2, PDF page 5), $4.45 (derived); the rest $12.65 |
| Pasitka 2024 | $5.45 | $19.24 | its design with tangential-flow filters, $24.06 a kilo (Table S10): maintenance and insurance $5.31, the rest $18.75. It leaves out the payment on the plant its Table S4 works out, $8.60 a kilo. Its cells and medium are those of its 1.8-litre run (the set uses the long-term targets) |
| SuperMeat 2024 | $3.62 | $26.70 | $13.4 a pound with depreciation and $11.8 without (PDF page 20): $3.53 and $26.01 a kilo (derived). Its cells are those of its 10-litre runs (the set uses the long-term targets) |
| Ark Biotech 2023, baseline | $9.08 | $59.63 | its baseline, $29.5 a pound: depreciation $3.9, the rest $25.6 (Exhibit 2, PDF page 5); $8.60 and $56.44 a kilo (derived). Its lever case, which the set models, gives no split |
| Cellular Agriculture Ltd 2024 | $4.70 | $14.57 | the factory of 60 tonnes a week: plant £3.58, running costs £11.09 (Table 5, PDF page 7), at $1.28 a pound sterling; the plant divided over 20 years with no interest |

## Added 2026-11-24: four analyses by parties with a stake in the result

Ark Biotech 2023 (a bioreactor maker) and Cellular Agriculture Ltd 2024 (a hollow-fibre bioreactor maker) were read in full. Gourmey's (by Arthur D. Little, 2025) and Aleph Farms's (by Eridia, 2025) are not public: only the companies' announcements are recorded, and GFI's 2026 report says of both that sensitive details were omitted. None is peer reviewed. The all-favourable case is unchanged ($6.97): no value of theirs that respects the limits is more favourable than the one it already takes. The earlier sections of this note are as they were before these four.

| study | as published | where | as a kilo of wet cells | year of its dollars | in 2025 dollars | against the case |
|---|---|---|---|---|---|---|
| Ark Biotech 2023 | $2.0 a pound with all four of its levers ($29.5 as its baseline) | Exhibit 1, PDF page 4 | $4.41: a kilo of cells leaving the tank, with no differentiation credit removed: $2.0 x 2.2046. The headline figure is taken; its Exhibit 10 (PDF page 14) also shows example paths down to $0.3 a pound, which need cells that gain 3,000% in mass while differentiating | 2023 (not stated; the year of publication is taken) | **$4.66** | **below** |
| Cellular Agriculture Ltd 2024 | £14.68 a kilo of cultured biomass (factory of 60 tonnes a week) | Table 5, PDF page 7 | $18.79: already a kilo of cultured biomass; pounds to dollars at 1.28, about the 2024 average rate (typed from memory, not fetched from an official series) | 2024 (not stated; the year of publication is taken) | **$19.28** | above |
| Gourmey and Arthur D. Little 2025 | €7 a kilo ($3.43 a pound) | company announcement, 28 May 2025 | $7.56: the company's own dollar figure, $3.43 x 2.2046, read as a kilo of cells, the more favourable reading: the announcement does not say of what, and the press reports a product about half cells. Whether the plant is charged is not stated | 2025 (the year of the announcement) | **$7.56** | above |
| Aleph Farms and Eridia 2025 | as low as $4.08 a pound of end products ($6.45 as its estimate, with the plant) | company announcement, September 2025 | $8.99: the low end of its sensitivity analysis, $4.08 x 2.2046, read as a kilo of cells, the more favourable reading: the share of cells in the product is not stated | 2025 (the year of the announcement) | **$8.99** | above |

Values not taken, and the limit each breaks:

| study | what it assumes | where | its value | the limit allows | the limit |
|---|---|---|---|---|---|
| Ark Biotech 2023 | the plant written off over 15 years with no interest. The plant must be repaid at a market rate of interest: depreciation alone leaves out what the money costs. The study also counts nothing after the bioreactor. | Exhibit 8, PDF page 12 | 0.0667 share of the plant's cost a year | 0.083 | the plant must be repaid at a market rate of interest |
| Cellular Agriculture Ltd 2024 | the plant divided over 20 years of output with no interest. The plant must be repaid at a market rate of interest: depreciation alone leaves out what the money costs. | Fixed cost estimation, PDF page 2 | 0.05 share of the plant's cost a year | 0.083 | the plant must be repaid at a market rate of interest |

Open: the pound-to-dollar rate for Cellular Agriculture Ltd (1.28) was typed from memory. Ark's design is not re-priced inside the limits, because it does not publish its plant cost; its tanks of 100 to 1,000 m³ and its gain in mass during differentiation are not levers of this engine. No modification on Humbird's best estimate was added for these four.

Line by line against the study's Tables S4 to S10 (a kilo of wet cells; the set, then the study): medium $17.87 and $14.11 (28.4 and 22.4 litres); filter membranes $0.49 and $0.43; the plant with its upkeep $20.50 and $13.91; labour $4.81 and $2.03; energy $1.55 and $2.18; total $45.52 and $32.66. The plant and labour differ because a m³ of tank makes 15.0 tonnes a year here and 21.4 in the study: at a 61-hour doubling the study's output needs about 239 g of cells a litre, and a 5 m³ tank passes the oxygen for 209. With cells doubling every 36 hours the engine gives the study's output (21.2 tonnes) and $38.39. Until later on 2026-11-24 the set kept Humbird's pharma membranes ($14.13 a kilo, $59.16 in all); the study's filter cost is the membrane lever's own food-grade reference, so that was not a correction.
