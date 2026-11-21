# Back-test: the engine against Humbird's own tables

2026-11-20. Code: `humbird_check.py`; test: `tests/test_humbird_check.py`. Source: Humbird 2021, *Scale-up economics for cultured
meat: techno-economic analysis and due diligence* (the full report; page numbers are the report's own).

## Why

The page now starts from "Humbird's best estimate (2021)": his fed-batch design with enhanced cells on soy hydrolysate, **$21.00 a
kilo of wet cells in 2018 dollars** (Table 4.7, second column, p. 57). Before starting there, the engine
(`floor_physics.explore`) was run at his conditions for the four columns of Table 4.7 and for his perfusion design (Table 4.13,
p. 64), line by line. Each gap above 5% on a line or 3% on a total was traced to its cause in his report. Where the engine
misread him it was changed; where the gap could not be closed from his report it is left and explained here.

## His conditions

| | Fed-batch (Sect. 4.1, pp. 48-52) | Perfusion (Sect. 4.2, pp. 59-60) |
|---|---|---|
| Tanks | 24 × 20 m³, 80% working volume | 96 × 2 m³, two ATF 10 filters each |
| Cells | 3 ng, 24 h doubling; Reaction 2.11 or 2.13 (enhanced), 2.9 or 2.12 (wild type) | Reaction 2.11 |
| A run | 482 kg of seed cells in 13.2 m³ to 1,849 kg in 16 m³ in about 48 h, then 10 h to drain, clean and refill; 3,600 batches a year | fed-batch to 120 g/L, then perfusion at one tank volume a day (1,600 L) to 195 g/L; 9 kg an hour bled from each tank; 10 turnarounds a year, 91% uptime |
| Limits | 5 mmol/L ammonia, 50 mmol/L lactate, 100 mbar CO₂, 6 mm/s of gas (Sect. 2.3, note 64) | the same; oxygen limits the density |
| Plant | $328M (amino acids) or $330M (hydrolysate) for 480 m³ of production tank, Class 8 clean room | $663M for 192 m³ |
| Yearly charge | 14.6% (7.5% over 10 years) + 4% maintenance + 5% insurance = 23.6% of the plant's cost | the same |
| Staff | 95 (94 on hydrolysate; 81 with wild-type cells) | 132 |

What he does not count, and the back-test switches off: cells killed by bubbles, cells lost at harvest, a least medium flow
beyond ammonia and lactate, bubble protectant, antifoam, slower growth near the end of a batch, lost runs.

## Result (2018 dollars a kilo; `python humbird_check.py`)

Regenerated 2026-11-21 (after items 11 and 12 below).

### Fed-batch, enhanced cells, amino acids (Table 4.7, column 1 (and Table 4.6), p. 57)

| Line | Humbird, 2018 $ | Engine at his conditions, 2018 $ | Gap | Engine, 2025 $ |
|---|---:|---:|---:|---:|
| Nutrients (his macronutrients) | 19.08 | 19.08 | +0.0% | 24.42 |
| Growth factors (his micronutrients) | 3.13 | 3.00 | -4.2% | 3.84 |
| Consumables | 0.85 | 0.84 | -1.6% | 1.07 |
| Utilities | 0.94 | 0.92 | -2.2% | 1.18 |
| Labour | 1.45 | 1.42 | -2.3% | 1.81 |
| Plant (capital charge, maintenance, insurance) | 11.33 | 11.12 | -1.9% | 14.79 |
| Total | 36.79 | 36.37 | -1.1% | 47.11 |
| Density at harvest, g/L | 115.6 | 120.0 | +3.8% | 120.0 |
| Output, t per m3 of tank a year | 14.2 | 14.5 | +2.3% | 14.5 |
| Plant, $k per m3 of tank | 683 | 683 | -0.0% | 908 |

### Fed-batch, enhanced cells, soy hydrolysate (his best estimate) (Table 4.7, column 2, p. 57)

| Line | Humbird, 2018 $ | Engine at his conditions, 2018 $ | Gap | Engine, 2025 $ |
|---|---:|---:|---:|---:|
| Nutrients (his macronutrients) | 3.39 | 3.39 | +0.0% | 4.34 |
| Growth factors (his micronutrients) | 3.12 | 3.00 | -3.9% | 3.84 |
| Consumables | 0.81 | 0.81 | -0.2% | 1.03 |
| Utilities | 0.93 | 0.92 | -1.1% | 1.18 |
| Labour | 1.42 | 1.42 | -0.2% | 1.81 |
| Plant (capital charge, maintenance, insurance) | 11.33 | 11.12 | -1.9% | 14.79 |
| Total | 21.00 | 20.65 | -1.7% | 26.99 |
| Density at harvest, g/L | 115.6 | 120.0 | +3.8% | 120.0 |
| Output, t per m3 of tank a year | 14.4 | 14.5 | +0.8% | 14.5 |
| Plant, $k per m3 of tank | 688 | 683 | -0.7% | 908 |

### Fed-batch, wild-type cells, amino acids (Table 4.7, column 3, p. 57)

| Line | Humbird, 2018 $ | Engine at his conditions, 2018 $ | Gap | Engine, 2025 $ |
|---|---:|---:|---:|---:|
| Nutrients (his macronutrients) | 18.24 | 18.24 | +0.0% | 23.35 |
| Growth factors (his micronutrients) | 4.60 | 4.53 | -1.5% | 5.80 |
| Consumables | 12.56 | 12.58 | +0.2% | 16.11 |
| Utilities | 14.52 | 14.47 | -0.3% | 18.53 |
| Labour | 20.70 | 23.94 | +15.6% | 30.64 |
| Plant (capital charge, maintenance, insurance) | 165.94 | 187.84 | +13.2% | 249.83 |
| Total | 236.58 | 261.61 | +10.6% | 344.25 |
| Density at harvest, g/L | 7.0 | 7.1 | +1.5% | 7.1 |
| Output, t per m3 of tank a year | 0.9 | 0.9 | +0.5% | 0.9 |
| Plant, $k per m3 of tank | 596 | 683 | +14.6% | 908 |

### Fed-batch, wild-type cells, soy hydrolysate (Table 4.7, column 4, p. 57)

| Line | Humbird, 2018 $ | Engine at his conditions, 2018 $ | Gap | Engine, 2025 $ |
|---|---:|---:|---:|---:|
| Nutrients (his macronutrients) | 4.27 | 4.27 | +0.0% | 5.47 |
| Growth factors (his micronutrients) | 4.62 | 4.55 | -1.5% | 5.83 |
| Consumables | 13.05 | 13.08 | +0.2% | 16.74 |
| Utilities | 14.81 | 14.47 | -2.3% | 18.53 |
| Labour | 20.86 | 23.94 | +14.8% | 30.64 |
| Plant (capital charge, maintenance, insurance) | 167.43 | 187.84 | +12.2% | 249.83 |
| Total | 225.03 | 248.15 | +10.3% | 327.03 |
| Density at harvest, g/L | 7.0 | 7.1 | +1.5% | 7.1 |
| Output, t per m3 of tank a year | 0.9 | 0.9 | +0.5% | 0.9 |
| Plant, $k per m3 of tank | 600 | 683 | +13.8% | 908 |

### Perfusion in 2 m3 tanks, enhanced cells, amino acids (Table 4.13 (and Table 4.14, column 1), p. 64)

| Line | Humbird, 2018 $ | Engine at his conditions, 2018 $ | Gap | Engine, 2025 $ |
|---|---:|---:|---:|---:|
| Nutrients (his macronutrients) | 18.39 | 18.39 | +0.0% | 23.54 |
| Growth factors (his micronutrients) | 2.78 | 2.66 | -4.1% | 3.41 |
| Consumables | 4.56 | 4.61 | +1.1% | 5.90 |
| Utilities | 0.98 | 0.72 | -26.9% | 0.92 |
| Labour | 1.99 | 2.00 | +0.3% | 2.55 |
| Plant (capital charge, maintenance, insurance) | 22.61 | 21.36 | -5.5% | 28.41 |
| Total | 51.29 | 49.74 | -3.0% | 64.73 |
| Density at harvest, g/L | 195.0 | 194.6 | -0.2% | 194.6 |
| Output, t per m3 of tank a year | 35.9 | 35.8 | -0.3% | 35.8 |
| Plant, $k per m3 of tank | 3,451 | 3,244 | -6.0% | 4,315 |

### His best estimate against the model's own version of his design (2025 dollars)

| Line | Humbird, 2018 $ | Humbird, 2025 $ | Engine like for like | Engine with the model's additions |
|---|---:|---:|---:|---:|
| Nutrients (his macronutrients) | 3.39 | 4.34 | 4.34 | 4.80 |
| Growth factors (his micronutrients) | 3.12 | 3.99 | 3.84 | 4.38 |
| Consumables | 0.81 | 1.04 | 1.03 | 0.90 |
| Utilities | 0.93 | 1.19 | 1.18 | 1.34 |
| Labour | 1.42 | 1.82 | 1.81 | 2.08 |
| Plant (capital charge, maintenance, insurance) | 11.33 | 15.07 | 14.79 | 16.94 |
| Total | 21.00 | 27.45 | 26.99 | 30.45 |

### All five designs: totals

| Design | Humbird, 2018 $ | Engine like for like, 2018 $ | Engine like for like, 2025 $ | Engine with the model's additions, 2025 $ | Density with the additions, g/L |
|---|---:|---:|---:|---:|---:|
| Fed-batch, enhanced cells, amino acids | 36.79 | 36.37 | 47.11 | 53.54 | 116 |
| Fed-batch, enhanced cells, soy hydrolysate (his best estimate) | 21.00 | 20.65 | 26.99 | 31.28 | 116 |
| Fed-batch, wild-type cells, amino acids | 236.58 | 261.61 | 344.25 | 376.61 | 7 |
| Fed-batch, wild-type cells, soy hydrolysate | 225.03 | 248.15 | 327.03 | 358.98 | 7 |
| Perfusion in 2 m3 tanks, enhanced cells, amino acids | 51.29 | 49.74 | 64.73 | 112.45 | 121 |

### What the model adds to his best estimate, one at a time

| Step | $ a kilo | Change |
|---|---:|---:|
| His design, like for like | 26.99 | +0.00 |
| The model's flat $0.30 of supplies in place of his filter sets, and his yearly charge unrounded | 26.24 | -0.75 |
| A thick culture takes up oxygen more slowly (kLa falls with the viscosity) | 26.24 | +0.00 |
| The least medium flow the cells need (other by-products build up, and a batch may end above their level as above the others') | 26.24 | +0.00 |
| All the waste a kilo made counted at the end of a batch, which may end 1.3 times above the limit | 26.97 | +0.73 |
| Cells killed by bursting bubbles | 29.24 | +2.27 |
| Cells lost at harvest (2%) | 29.84 | +0.60 |
| Bubble protectant in the medium: the model's own version of his design | 30.45 | +0.61 |

### The page's start, and what the page's five levers add (2025 dollars)

| Setting | $ a kilo | Change |
|---|---:|---:|
| The page's start: his design, like for like | 26.99 | |
| Thick cultures take up oxygen more slowly, switched on alone | 26.99 | +0.00 |
| A least flow of medium the cells need, switched on alone | 26.99 | +0.00 |
| Cells killed by bursting bubbles, switched on alone | 29.34 | +2.35 |
| Cells lost at harvest, switched on alone | 27.54 | +0.55 |
| A bubble protectant in the medium, switched on alone | 27.49 | +0.50 |
| All five switched on (his yearly charge and filter sets kept) | 30.49 | +3.50 |

Since 2026-11-20 the plant is the engine's own for all five designs (item 7). His best estimate like for like is $20.65 in 2018
dollars and $26.99 in 2025 dollars; his wild-type designs $261.61 and $248.15 (+10.6% and +10.3%, the plant); his perfusion design
$49.74 (−3.0%; it was $50.47, −1.6%, while its growth factors and labour residuals partly cancelled its utilities').

## Gaps found, their cause, and what was done

A quick run before this work gave, for his fed-batch conditions, 92 g/L and 11.2 t per m³ a year against his 115.6 g/L (1,849 kg in
16 m³; he rounds it to 120) and 14.2 to 14.4.

1. **Density 92 g/L in fed-batch: a model addition, not a misreading. Switched off for the back-test** (and no longer binding
   since 2026-11-21, item 11). The cap was "other
   by-products": the least medium flow a cell needs (`pf_min_perfusion`, 7.5 mL per gram a day), which in a tank that is not
   washed out caps the density at 1000 × 0.693 / 7.5 = 92 g/L. He has no such limit. With it off the engine gives 116 to 120 g/L.
   It was not the batch-end rule of 2026-11-19 (item 2).
2. **The end of a batch (`pf_batch_end_x`): the note misdescribed his design; the engine's number was right. Note corrected, no
   change of value.** The note said his design "ends at 6.5 mmol/L of ammonia". By his own count it ends at 5 (Sect. 4.1, p. 49:
   the reaction is "designed to cause the batch to reach an NH3 limit simultaneously with a pCO2 limit"). The difference is what is
   counted. His simulation starts a tank from fresh medium plus 482 kg of seed cells and counts the waste made by the 1,367 kg
   grown in that tank: 120 g/L × (1 − 482/1,849) × 0.0563 mol/kg = 5.0 mmol/L, which is his Fig. 2.8b; his wild-type cells the
   same way, 7.0 g/L × 0.75 × 0.952 = 5.0 (Fig. 2.7a, p. 26). The seed cells arrive in about 4 m³ of seed culture that ended at
   the same level, which he leaves out. The engine counts all the waste a kilo made, so by its count his batch ends at 1.30 times
   the limit at his real 115.6 g/L and 1.35 at the 120 g/L of Fig. 2.8b. The default 1.3 stays. The back-test sets 1.35
   (`his_batch_end`) and turns the slowdown off.
3. **Growth factors under-priced by a quarter in his own fed-batch design ($2.39 against $3.12): engine misread him. Fixed.**
   He doses growth factors by concentration and counts what leaves when the tank is emptied (Sect. 3.2, pp. 44-45; Table 4.4,
   p. 56: insulin 310 g a batch = 19.4 mg/L × 16,000 L). So $3.13 a kilo is for 8.65 litres a kilo, $0.36 a litre. The engine
   divided by the 11.2 litres his cells need in perfusion ($0.28 a litre). Now `pf_growth_factors` (3.13, was 3.1) over
   `pf_medium_prep_l_kg` (8.7). `gf_doubling_bounds.py` had already noted the discrepancy.
4. **Utilities flat per kilo ($0.94 whatever the tank made): engine misread him. Fixed.** His Table 4.4 (p. 56) is mostly per
   batch and per year: of $1,700 a batch, $543 is power for the building, $773 water and steam to clean and sterilise the tank,
   $326 the water of the medium, $123 power for oxygen, stirring, cooling and dewatering. His wild-type columns show it: the same
   plant making 6% as much pays $14.52 a kilo. The engine now charges four parts (`pf_util_time`, `pf_util_run`, `pf_util_water`,
   `pf_util_kg`): by the year and by the run per m³ of tank, by the litre of medium, by the kilo. They sum to $0.94 at his plant
   and give $14.47 for his wild type.
5. **Crew per m³ of tank 2% high: engine misread him. Fixed.** Labour was his $1.45 a kilo times 14.5 t per m³ a year (a 58-hour
   cycle at a nominal 120 g/L). His plant makes 6.8 kTA from 480 m³, 14.2 (Tables 4.1, 4.7), and $1.45 × 14.2 × 480 is his $9.9M a
   year (Table 4.5, p. 57). `floor_physics.humbird_fedbatch_output()` now gives the 14.2, for labour and for the reference
   throughput of the medium-preparation equipment.
6. **Density 146 g/L in perfusion at 2 m³: a model addition. Switched off.** Antifoam is taken to cost a quarter of the oxygen
   transfer (`pf_antifoam_otr` 0.75): 195 × 0.75 = 146. With it at 1 the engine gives his 195 g/L.
7. **Plant of 2 m³ tanks: closed to −6% (2026-11-20, additions brief). His plant cost is no longer entered for any design.** Until
   then the engine scaled only the bioreactor share of the 20 m³ plant with Eq. 3.1 ($1,890k per m³ at 2 m³ against his $3,450k), and
   the back-test entered his plant cost. Now `floor_physics.tank_items` adds, per production tank, what he itemises: the tank (Eq. 3.1,
   ×1.2556 for minor equipment), its makeup tanks (fed-batch $140k bare a tank for three, perfusion $139k for two) and filter
   housings ($62k and $28k), in his accounting (ISBL = 1.2556 × bioreactors + 2.5556 × other equipment; TCI = direct cost × 1.84),
   and buildings at $74.4k per m³ + $533k per tank of direct cost (a fit to his two plants, not his rule). Seed trains, fill tanks,
   sterilisers, centrifuges and outside utilities stay at the fed-batch plant's cost per m³ of tank. His ATF units are added in his
   own accounting ($38,530k bare × 2.5556 × 1.84 = $940k per m³; the retention module's ATF takes only ×1.84 on the bare price, 2.56
   times less). Result: fed-batch $683k per m³ (his $683k and $688k), perfusion **$3,244k** against his **$3,451k (−6.0%)**: his 2 m³
   plant spends $493k per m³ on the seed train, sterilisers, centrifuges and outside utilities, the engine $286k. His wild-type plants
   ($596k, $600k) are **14% below** the engine's $683k: their oxygen plant, utilities and medium equipment serve 6% of the output.
   Those three residuals are in `humbird_check.RESIDUALS`. At larger tanks (480 m³ of tank in all, fed-batch) the rule gives $570k per
   m³ at 50 m³ and $532k at 100 m³, against $582k and $534k from the six-tenths rule in his accounting.
8. **Perfusion residuals (2026-11-21, item 12 below): growth factors and labour closed, utilities halved.** They were growth
   factors +62%, utilities −54%, labour −42%; they are now −4.1%, −26.9% and +0.3%.
9. **Wild-type labour +15%: left.** His wild-type plant has 81 staff, not 95; the engine keeps the crew per m³ of tank.
10. **Ammonia per kilo 0.054 against 0.056: left.** Reaction 2.11 prints 0.004 mol per mol; Reaction 2.10's one ammonia per ten
    lactate gives 0.0041. Lactate sets the litres in his design either way.

11. **The least medium flow in a tank that is not washed out (2026-11-21): engine error in the counting. Fixed.** In fed-batch the
    least flow (`pf_min_perfusion`, a perfusion measurement) capped the density at 1000 × 0.693 / 7.5 = 92 g/L and added $6.4 to
    his design. Of its two parts, the nutrients that run out are supplied by a fed-batch's concentrated feeds, so they cannot
    bind; the by-products that build up are waste like ammonia and lactate. The engine lets a batch end above the level
    perfusion holds ammonia and lactate to (`pf_batch_end_x`, 1.3; his own design ends at 1.35 by the engine's count, item 2) but
    held the other by-products to 1.0. Now the same factor applies to all three, and the by-products' level counts towards the
    slower growth at the end of a batch. The cap is 120 g/L (124 at his count), so it no longer binds his design: switched on alone
    at the page's start it adds nothing (it added $6.73), the model's own version of his design costs $30.45 (was $36.21) and
    the page with its five additions $30.49 (was $37.38). Against applying it at all in fed-batch: nobody has measured it in a
    dense fed-batch of meat cells; CHO fed-batch cultures top out near the same 30-40 million cells/mL, but there ammonia,
    lactate and osmolality are the stated causes, which the engine counts separately. The fill-and-draw rows of the plant ladder
    and the vessel grid's batch rows move with it (`floor_physics.tiers`, `vessels.py`).
12. **Humbird's perfusion design (2026-11-21).** Each of the three residuals of item 8, traced in his report:
    * **Growth factors +62%: a deliberate difference, now matched like for like.** His Table 4.11 buys 940 kg of insulin a year,
      at 19.4 mg/L the 48 million litres that pass the filters (1,600 L a day per tank at 91% uptime: 51 million); the culture
      bled out with the 9 kg an hour of cells (5.1 L a kilo at 195 g/L) is not counted, as it is not for his nutrients ("assuming
      a perfusion rate of 1/d (1,600 L/d) at residual concentrations", Sect. 4.2). The growth factors in that culture are lost
      with it, so the engine keeps dosing every litre that leaves. Like for like, `conditions` buys them only in his share of the
      litres (7.4 of 12.5 L a kilo): $2.66 against his $2.78 (−4.1%; the rest is his perfusion plant's price per kilo of growth
      factor at its global demand).
    * **Labour −42%: an engine error in how the crew scales, fixed; the rest deliberate.** His perfusion crew is counted per tank
      (Table 4.12): 8 hours per inoculation, 2 hours per change of the day tanks, 10% of the online time, over 80% efficiency,
      194,789 hours a year for 96 tanks, 0.975 staff a tank, plus 38 continuous staff. The engine's crew per m³ did not depend on
      the tank size. Now (`floor_physics.crew_multiplier`) a tank run continuously in perfusion takes `pf_labour_perfusion_x`
      times the fed-batch crew per m³ at 20 m³ plus `pf_labour_tank_perfusion` (0.975) staff per tank for a smaller tank (fewer
      for a larger), and a batch tank's crew has his batch workers' share (13 of 21 a shift, `pf_labour_tank_share`) counted per
      tank. At 20 m³ nothing changes. Like for like, `conditions` takes his own rest of the crew (`his_perfusion_crew_x`, 1.26 times
      the fed-batch crew per m³): $2.00 against $1.99. The model's own 2.0 (staff per thousand tonnes in analyses that assume
      perfusion; SuperMeat 2024 has 0.41 staff per m³ of 25 m³ tanks) is kept as a deliberate difference: at his design it would
      give 160 staff against his 132.
    * **Utilities −54%: an engine error, half closed; the rest left.** His perfusion plant pays $0.36 a kilo of facility power
      against $0.29 in fed-batch: 53.4 GWh for 13,073 m² of Class 8 hall, the same load per m² as the fed-batch hall. The engine
      charged every plant the fed-batch plant's building power per m³ of tank, whatever its tank size or its class. Now
      (`floor_physics.building_power`) the building's power follows the buildings' cost per m³ at that tank size (the $74.4k per
      m³ + $533k per tank fit) and the electric load of each building's class in his Table 3.2 (a Class 8 hall 410 W/m², a
      sanitary hall 50, a warehouse-like shed 5, Class 6 labs 1,000). His 2 m³ plant comes out at 3.4 times the fed-batch plant's
      building power per m³ against his 3.2. Left: his process water, 183,020 t a year, 26.5 L a kilo ($0.53), against the
      engine's medium (12.5 L) and tank cleaning (0.5 L). His report does not itemise the other 13.5 L; cleaning the 192 day
      tanks each time they are refilled would fit, but he does not say so, so it is not charged. −26.9% is the residual.
    * **What it did to the model's cases:** the sanitary hall's lower power takes $0.2-0.6 off every food-grade case (Humbird's
      optimistic design $15.93 → $15.72, the low-lactate example $49.50 → $49.22, published cells $322.55 → $316.11 before the
      design-search change); the per-tank crew changes only cases at other tank sizes (the all-favourable example's 42 m³ tanks;
      the tank-size study, where large tanks now gain more).

## What the fixes of 2026-11-20 did to the model's other cases (cost of a kilo of cells, 2025 dollars)

| Case | Before | After | Change | Utilities | Labour |
|---|---:|---:|---:|---|---|
| Published cells (today) | 306.95 | 322.55 | +5.1% | 1.58 → 18.15 | 42.54 → 41.57 |
| process | 294.07 | 309.58 | +5.3% | 1.57 → 18.05 | 42.31 → 41.34 |
| selected | 67.24 | 70.37 | +4.7% | 1.49 → 4.44 | 9.32 → 9.10 |
| Low-lactate example (central) | 50.14 | 49.96 | -0.3% | 1.65 → 1.51 | 2.99 → 2.93 |
| central_lean | 45.74 | 45.67 | -0.2% | 1.60 → 1.59 | 4.17 → 4.07 |
| engineered | 28.04 | 28.07 | +0.1% | 1.65 → 1.03 | 2.99 → 2.93 |
| All-favourable example (best) | 19.33 | 18.71 | -3.2% | 1.41 → 0.84 | 2.28 → 2.23 |
| cautious | 180.26 | 183.15 | +1.6% | 1.65 → 4.57 | 5.64 → 5.51 |
| scenarios.reference() | 16.70 | 16.03 | -4.0% | 1.33 → 0.70 | 2.70 → 2.64 |

Thin cultures (the published cells' fed-batch at 10 g/L) now pay for the building's power and the cleaning of tanks that give few
cells, as his wild-type columns do; dense perfusion cases pay less than the flat figure. No case buys growth factors on top of the
medium at these settings; where growth factors set the floor of a complete medium's price (selected, engineered) the medium costs
more.

## The page's start

`with_additions(case)` (the totals table above) keeps his plant cost, yearly charge and filter sets and turns the model's additions on; for his best estimate it gives $31.3 (2025 dollars; $37.5 before 2026-11-21, item 11). The model's own version of his design is $30.45 (was $36.21): it takes the model's own plant figure ($683k per m³ in 2018 dollars against his $688k), its flat $0.30 of supplies in place of his filter sets, and 23.57% in place of his rounded 23.6%. The page starts at his design like for like, $26.99, and its five additions together bring it to $30.49.

`humbird_check.start_kwargs()`: his cell as the four traits, fed-batch in 20 m³ tanks, the plant with clean rooms, 7.5% over 10
years plus 9% (23.57%; he rounds to 23.6%), limits of 5 and 50 mmol/L and 100 mbar, 6 mm/s of gas, growth factors bought, in
2025 dollars, with the model's own additions on. The medium is at his nutrient cost ($3.39 a kilo in 2018 dollars, $4.34
in 2025 dollars), not the model's ingredient floor ($2.00): it is his estimate, and his cost is the higher. The page's medium lever takes a
price per litre, so it is entered as $0.40 a litre (his cost over the litres a kilo grown takes
at the start).

## Open

* How buildings, support equipment and crew scale with tank size (item 7): the buildings rule is fitted to his two designs alone,
  and the seed train, sterilisers, centrifuges and outside utilities are held per m³ of tank, which neither design follows exactly
  (his 2 m³ plant spends more on them per m³, his wild-type plant less). It matters for every case that changes the tank size.
* The least medium flow in a tank that is not washed out (items 1 and 11): since 2026-11-21 it is counted as the batch's other
  waste is and no longer binds his design. Nobody has measured it in a dense fed-batch of meat cells.
* His perfusion plant's process water (item 12): 13.5 L a kilo not itemised in his report.
