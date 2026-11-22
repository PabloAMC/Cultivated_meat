# Cost scenarios: settings, why, what each needs, and what would move them

> Names (2026-11-19): the low-lactate example was earlier called Central; the all-favourable example was earlier called the best case. Cells are described by their traits, never as a named kind of cell.

> **Table regenerated 2026-11-22** from `scenarios.markdown_table()` (by its header line), on the model after the batches of
> 2026-11-21: Published cells $316.1, the low-lactate example $48.7 (median of draws $52, 0.05% of world meat), the all-favourable
> example $7.0 (median $8, 23.4% at its point cost with its own demand, median 17.4%), Humbird's optimistic design $15.7. The
> boxes below and the prose of the sections are as of the dates they give.

> **Repinned 2026-11-20, final pass.** The table below is regenerated from `scenarios.markdown_table()` (by its header line). There is now one all-favourable case (`scenarios.all_favourable()`): every lever takes the most favourable value among the model's own favourable end, Humbird's design and ten published studies that break no limit of the model (`study_comparison.md`). It allows his 5 mmol/L of ammonia and 50 of lactate, his 3 ng cell, a 16-hour doubling, no lost runs, a 4-day restart, dialyser-grade fibres and 42 m³ tanks, and costs $7.62 at most likely values (median of draws $9; world share 17.4% at the median, 22.6% at the point). **Changed:** (1) the all-favourable example is now below Humbird's optimistic design ($15.93), and no cost line of it is above his; the 2026-11-20 batch statement below, that his design costs less, no longer holds, because the all-favourable example now takes his tolerances and his cell weight where they are more favourable. (2) The other rungs moved by under 2%: $322.55, $311.29, $71.76, $49.50, $45.04 and $27.75; the cautious case $185.59; Humbird's design $15.93 (per-tank plant items, the harvested share applied to every cost line). (3) The low-lactate example's tank design is now the column and 1 bar in the ordinary tall tank, not a squarer tank: with both tricks oxygen holds the tall tank at 154 g/L against 151 in the squarer one, at $49.50 against $51.75. The tank tricks are now worth $5.7 a kilo there ($4.1 before), because the comparison is with the tall tank, which without the tricks is held by CO₂ at 87 g/L. A 24-hour doubling is worth $5.4 a kilo.

> **Repinned 2026-11-20 (model batch).** The scenarios' cells tolerate 35 mmol/L of lactate (50 before; Humbird's design keeps his 50); cells killed by bursting bubbles are charged, with the gas following what the culture needs; 2% of the cells are lost at harvest; a tank in perfusion carries twice the fed-batch crew; filter membranes are replaced after 2,415 L/m2 (3,960 before); medium preparation capital scales with the medium passed; growth factors and utilities follow the Humbird back-test (`humbird_backtest.md`; `full_review_2026-11-19.md`, section 2). All costs are per kilo of cells harvested. At most likely values the seven rungs cost $322.6, $309.6, $70.4, $50.0, $45.7, $28.1 and $18.7 ($209.1, $201.4, $64.9, $32.8, $29.9, $17.3 and $11.7 on 2026-11-19); the cautious case $183.1 ($92.2). **Three things changed besides the levels.** (1) Humbird's optimistic design ($16.0) now costs less than the all-favourable example ($18.7): his cells are allowed 50 mmol/L of lactate and wash with 12 litres a kilo against 19, his design loses no runs, and his cell weighs 3 ng. (2) Perfusion is worth $20 a kilo between rungs 3 and 4, not $32, and with the all-favourable example's switches a drained and refilled tank ($17.1) or a fed-batch of 50 m³ or more is cheaper than perfusion at 20 m³ (`no_perfusion_downside.md`, `tank_size.md`). (3) The published cells stop a batch at 9.5 g/L, not 14. A 24-hour doubling is worth $5.2 a kilo in the low-lactate example ($2.5 before) and the tank tricks $4.1 ($3.5). The sections below the table keep the figures of the dates they give.

> **Updated 2026-11-15 (late), second time.** Every figure in this note is recomputed with the model as it now stands: the hollow-fibre
> filter loop with its membranes (`retention.py`), the bubble protectant (poloxamer 188, 2 g/L at an assumed $30/kg), antifoam's
> quarter cut to the sparger's oxygen transfer, and bought oxygen for a yeast-style plant. Earlier versions are in git history (the all-favourable example $6.57 and the low-lactate example $18.14 with the old device; $8.95 and $26.64 with the filter loop alone). With antifoam counted, oxygen limits the
> central and cautious cases, and each scenario's tank design was chosen again.

Code: `scenarios.py` (the switches and presets), `page_sections.py` and `page_scenarios.js` (the page), `tests/test_scenarios.py`.
Inputs: `inputs.py`, the `sc_*` block (each with source, range, note). Every cost below is computed by `floor_physics.explore`; run
`python scenarios.py` to reproduce this note's numbers and `python scenarios.py --markdown` for the table.

## The ladder (rebuilt 2026-11-19, scenario restructure)

Since 2026-11-19 RESULTS leads with what it would take (`scenarios.what_it_would_take`) and cells as traits (`cell_traits.py`). The
ladder of reference points
starts from what has been shown and adds one kind of change per rung, likeliest first: 1. Published cells in a 20 m³ fed-batch (key
`today`; fed-batch is what pharma runs and Upside Foods reports at 20 m³); 2. process changes and cheaper inputs, still a batch
(`process`); 3. cells that make less lactate (0.42), still a batch (`selected`); 4. perfusion: the low-lactate example (`central`, unchanged); 5. the
shared-medium plant (`central_lean`); 6. cells that make almost no ammonia or lactate (`engineered`); 7. everything else at its favourable end: the all-favourable
example (`best`). A new switch, "How the tank is run", holds perfusion at 20 m³ or fed-batch at 20, 50 or 100 m³. A batch is held
by the waste mass balance (`vessels_and_modes.md` section 10). The cautious scenario keeps the published cells in perfusion
(`scenarios.ORDER`).

| scenario | cells, $/kg: median of draws (8 in 10 between) | $/kg if every estimate lands on its most likely value | shop price against US minced beef or pork cuts ($12 a kilo), at the median | share of world meat and seafood, long run: median of draws (8 in 10 between) | share at the most-likely-values cost | cell traits set beyond the best measured in meat cells |
|---|---|---|---|---|---|---|
| 1. Published cells: the best meat cells in the published record, grown in batches in a 20 m³ tank | **$337** ($235–475) | $316.1 | 39.3× | **0.001%** (under 0.001–0.02%) | 0.001% | none |
| 2. Plus process changes and cheaper inputs | **$322** ($223–458) | $304.8 | 37.6× | **0.002%** (under 0.001–0.02%) | 0.001% | none |
| 3. Plus cells that make less lactate (0.42 mol per mol of glucose) and double every 36 hours, still in batches | **$77** ($53–114) | $70.3 | 9.1× | **0.1%** (0.03–0.7%) | 0.1% | lactate |
| 4. Plus perfusion (the low-lactate example): waste washed out through a cell filter | **$52** ($39–76) | $48.7 | 6.3× | **0.2%** (0.06–1.2%) | 0.3% | lactate |
| 5. Plus a food-grade plant with shared medium | **$48** ($35–71) | $44.5 | 5.8× | **0.3%** (0.06–1.3%) | 0.3% | lactate |
| 6. Plus cells that make almost no ammonia or lactate (0.055 mol a kilo; 0.28 mol per mol of glucose) | **$33** ($25–45) | $27.3 | 4.1× | **0.5%** (0.1–2.1%) | 0.6% | ammonia, lactate |
| 7. Plus everything else at its favourable end (the all-favourable example) | **$8** ($7–10) | $7.0 | 1.3× | **19.2%** (12.4–28.0%) | 25.1% | ammonia, lactate |
| Humbird's optimistic design: his enhanced cells in an ordinary perfusion tank | **$22** ($17–29) | $15.7 | 2.8× | **0.9%** (0.3–3.9%) | 1.6% | ammonia, lactate |
| As a company reports (SuperMeat 2024) | **$34** (its own point figure) | $34.4 | 4.3× | **0.4%** (0.1–2.0%) | 0.4% | a company's own report |

*History (2026-11-16, the old five-rung ladder in perfusion):* what each step was worth, from `scenarios.run`: the published cells cost $62.96 in the ordinary tank. The tank tricks alone take $20.57 off
(chosen by `design` with the other switches as they then were), 4 mm/s of gas $17.17, a 14-day restart $2.30, growth factors at 30% $2.99, $0.20
medium $2.87; together, with the tank design chosen again, $32.23, to $30.73. Cells that make less lactate then took $1.31 off (the low-lactate example $29.42), the
plant with shared medium $2.86 ($26.56), and cells that make almost no ammonia or lactate with every switch at its cheapest plausible setting $16.90 ($9.66). *Now (2026-11-19, at most likely values):* $209.1,
$201.4, $64.9, $32.8, $29.9, $16.9 and $11.5 for the seven rungs; the steps are in RESULTS.md, "The ladder".

**Since 2026-11-16 every scenario holds dissolved oxygen at about half of air saturation** (`scenarios.always`, `sc_do_setpoint`), which
took the low-lactate example from $29.92 to $29.42 and let the all-favourable example reach the thickness limit with recycled oxygen and a squat tank ($9.66). **The
sections below this one were computed before that change** and keep their figures (the low-lactate example $29.92, the all-favourable example $9.71); the differences are
under $0.6 a kilo.

## Why scenarios, not a floor

Until 2026-11-15 the model quoted one number, "the floor", $11.5/kg of cells. It was `explore()` at its defaults: a standard 20 m3
stirred tank in perfusion at 120 g/L, a food-grade plant, cells that make almost no ammonia or lactate, no tank tricks, no lost runs, no growth
factors. That is neither the most favourable case (the model has since gained tank tricks, a plant built item by item, explicit ammonia and lactate)
nor a typical one (it assumes cells nobody has shown and ignores contamination). It stays as the labelled reference
(`scenarios.reference()`), and the cost is described by scenarios, each a preset of ten switches.

## The switches and where each setting comes from

Tags (since 2026-11-19): **CELLS** needs cells with other traits than the published ones (no route to them is assumed); **FEED** needs a
change of feed, process or plant design; **nothing new** has been done. Before 2026-11-19 the CELLS settings carried tags that named a
route; they are retired.

| switch | settings (tag) | evidence |
|---|---|---|
| kind of cells | almost no ammonia or lactate: ammonia 0.055 mol/kg, lactate 0.28 per glucose, 2 ng (CELLS) · less lactate on a low-waste feed: 0.14, 0.42, 2 ng (CELLS) · best meat cells measured: 0.14, lactate 1.05 per glucose, glucose 0.84 mol/kg, 2 ng (FEED) · ordinary: 0.70, 1.05, 0.84, 2 ng (nothing new) | Ammonia 0.054 is Humbird's enhanced cell; the CHO plateau that clears it (0.54 fmol/cell/h) is an upper bound from cells that were not net-growing. 0.14 is an upper bound from Hubalek 2023 (bovine cells, glutamine replaced by alpha-ketoglutarate, pyruvate or glutamate: "more than 5-fold" below 0.70). Lactate 0.39 has been measured in CHO cells; 0.42 allows a little for meat cells, for which nothing is measured. 1.05 is chicken (Pasitka 2024, snippet) and similar for bovine. Mass 2 ng: chicken cells are reported at 1.0 to 1.75 ng, Humbird's is 3; no mass was found for the bovine cells. (`waste_tricks_sizing.md`, `waste_and_medium_evidence.md`) |
| growth speed | 24 h (CELLS) · 30 h (CELLS) · 36 h (CELLS) · 43 h (nothing new) | See "Doubling time" below. |
| plant | lean (FEED) · sterile (nothing new) · pharma-style (nothing new) | `plant_items.py`, `cheap_plant_study.md`. Sterile: Humbird's plant with a sanitary hall in place of the clean room, $810k per m3. Lean: no clean room, food-grade tanks, a shared medium line, two seed trains, bought oxygen: $340k per m3 (2018 dollars; nobody has built one). Pharma-style: Humbird as designed, $910k. A plant as cheap as a yeast plant is **not offered**: nothing found shows animal cells grown in one (2026-11-15). |
| gas the cells tolerate | 6 mm/s (FEED) · 4 (FEED) · 2 (nothing new) | Humbird's 6 mm/s is his conversion of a rule of thumb ("under 0.1 vvm"), not a measured limit; Nienow 2006 reports 0.1 to 2 mm/s in 8 to 20 m3 tanks; bubble death scales with gas per litre, foam with surface velocity (`gas_flow_cap.md`). 4 is a midpoint. |
| tank tricks | none · column on a pumped loop (FEED) · column and 1 bar gauge · column, pressure and recycled oxygen (all FEED) | `gas_exchange.column_design`, `gas_exchange_study.md`: sized by calculation; no animal cells have gone through such a column. |
| tank shape | liquid 0.5 / 0.75 / 1.0 / 1.6 times as deep as wide | geometry is certain; the extra steel and floor of a squat tank are counted (`gas_exchange.shape_capex_factor`); no cost data on tank shape. |
| runs lost | 0.2 / 0.6 / 1 / 2% a day | 0.2% is large pharma (`pf_hazard_pharma`); the survey of makers (Powell 2025: 11.2% of batches lost, 19.5% beyond flasks) implies 0.6 to 2.2% a day **if** runs lasted 10 to 20 days, which the survey does not state. |
| restart after a loss | 4 / 14 / 21 / 30 days | 4 days reseeding from a healthy neighbouring tank (FEED; added 2026-11-16; about 2 days to clean and steam, a doubling to regrow, a day for the neighbour's lost output; the donor must test clean); 14 days with a ready seed train (regrowing from a seed is about 7 doublings); 21 days when the seed trains must be regrown; 30 when one failure reaches every tank (`contamination.py`). |
| growth factors | none (CELLS) · 30% (FEED) · 60% · all of Humbird's price | His price assumes an industry far larger than today's; cattle cells that make their own have been shown. 30% and 60% are rough judgements made while building the model with an AI assistant, not measured and not reviewed by an expert. |
| medium price | $0.05 / 0.15 / 0.20 / 0.30 / 0.50 a litre | $0.05 is an aspiration nobody has reported (lowest company report $0.07; GFI's amino acids alone $0.02-0.17; below it the medium costs what the cells must eat, `nutrient_floor.md`); $0.15 was this note's earlier estimate of the nutrients themselves; $0.20 is what several companies announced for 2025 (GFI 2026 report, p.8; not verified at scale); $0.50 is SuperMeat. |

## The scenarios, and the rule that defines each

| scenario | settings | rule |
|---|---|---|
| All-favourable example: everything works (since 2026-11-20, `scenarios.all_favourable`) | Humbird's 0.054 mol of ammonia a kilo and 0.28 of lactate per glucose, his 5 and 50 mmol/L tolerances and 3 ng cell, a 16-hour doubling, food-grade plant with shared medium, 6 mm/s, no lost runs, 4-day restart, no growth factors, medium at what the cells eat, dialyser-grade fibres, 42 m³ tanks, **tank design: the column and 1 bar, a tank as deep as wide** | Every lever at the most favourable value among the model's own favourable end, Humbird's design and the published studies that break no limit of the model; levers without a direction (plant, device, mode, gas, tank design, size) at the setting that costs least; tank design the cheapest pair whose loop passes the checks. |
| Low-lactate example: food-grade plant | cells that make less lactate (0.42), 36 h, food-grade plant, 4 mm/s, 1% a day, 14-day restart, growth factors 30%, $0.20 a litre, **tank design: the column and 1 bar, the ordinary tall tank (a tank as deep as wide before 2026-11-20, final pass)** | Cells defined by their traits; every other switch at the setting nearest the middle of what is reported; tank design as above. |
| Low-lactate example, food-grade plant with shared medium | the same in a food-grade plant with shared medium | As the low-lactate example. |
| Cautious: the best meat cells measured so far | best measured cells, 43 h, food-grade plant, 2 mm/s, 1% a day, 21-day restart, growth factors 60%, $0.30 a litre, **tank design: the column and 1 bar, the ordinary tall tank** | Each switch at the setting that has actually been measured; tank design as above. |

"The checks" (`scenarios.design`): the loop must be pH-safe (the alkaline exposure within the 55 mbar, 0.5 m3 design) and at a pass rate dense
cultures have taken (15 to 24 tank volumes an hour). Without the checks a tall tank with all three tricks would be a little cheaper still.

*The block below is from 2026-11-15 and is superseded: since then the scenarios became a ladder, dissolved oxygen is held lower,
and (2026-11-16) the bands draw the estimates the cost rests on most. Current figures are in the table near the top of this note
and in RESULTS.md, both checked by `tests/test_scenarios.py`.*

Computed results, 2026-11-15 (cells $/kg; shop; R against $12 meat; long-run share of world meat by weight; bands are 10th to 90th percentile, 4,000 draws; **the headline share is the median of the draws**, the point estimate is the share at the scenario's own point cost):

| scenario | cost | band | shop | R | **world share, median** | band incl. demand | world, point estimate | US (point) | Europe (point) | without the tank tricks | ordinary tall tank |
|---|---|---|---|---|---|---|---|---|---|---|---|
| All-favourable example | $9.71 | $9.2–12.2 | $14.7 | 1.23 | **3.8%** | 1.2–9.7% | 7.9% | 13.5% | 25.3% | $10.2 | $10.4 |
| Low-lactate example, food-grade plant | $29.92 | $27.4–38.1 | $34.9 | 2.91 | **0.2%** | 0.1–0.6% | 0.4% | 0.9% | 2.3% | $33.5 | $36.2 |
| Low-lactate example, food-grade plant with shared medium | $26.81 | $25.4–34.8 | $31.8 | 2.65 | **0.3%** | 0.1–0.7% | 0.5% | 1.2% | 3.5% | $28.5 | $29.9 |
| Cautious | $43.79 | $39.2–54.5 | $48.8 | 4.07 | **0.1%** | 0.0–0.2% | 0.1% | 0.3% | 0.5% | $63.0 | $63.0 |
| Reference (standard tank, no tricks) | $12.51 | | $17.5 | 1.46 | | | 4.3% | 8.5% | 19.6% | | |
| As a company reports | $34.35 | | $39.4 | 3.28 | | | 0.3% | 0.6% | 1.3% | | |

**Why the median and not the point estimate.** Each point cost sits below its band's median cost, because the estimates behind a scenario are drawn with
more room to fall short than to improve. The share rises steeply as the price falls, so the share at the point cost is higher than the median share.
A headline of 7.9% for the all-favourable example would be a number most draws do not reach, since the median is 3.8%. The page keeps the point estimate where
it is labelled as one. The band exists for the four scenarios. Once a reader changes a switch, the live strip shows the point estimate and says so.
At 1,000 draws the all-favourable example's median moved by 0.3 points between seeds (7.8 to 8.15, with the old device), so the bands use 4,000.

**Tank design nobody has run with animal cells.** Each scenario's tank design is the cheapest the loop checks allow. Each rests on tricks
that are calculated, not measured. The all-favourable example and the low-lactate example: a column, 1 bar of extra pressure, and a tank as deep as it is wide. Cautious: the
column and the pressure in the ordinary tall tank. Recycled pure oxygen through the column would be cheaper still in the low-lactate example (−$2.0) but fails the
loop checks. "Without the tank tricks" sets the tricks switch to "none" and keeps the tank shape (the low-lactate example: +$3.6). "Ordinary tall tank" also takes
the shape back to Humbird's 1.6 (the low-lactate example: +$6.3). (2026-11-15 figures; since 2026-11-20 the low-lactate example uses the tall tank, and the tricks are worth +$5.7.) The page and the scenario stories (`scenarios.tricks_sentence`) state this beside each scenario.

Each point sits below its band's median, because the estimates behind a scenario (the plant estimate, financing, the life of the filter membranes) are drawn with more room to fall short than to improve: the all-favourable example's point ($9.71) is at the 25th percentile of its draws (median $10.3), the central point ($29.92) at the 31st (median $31.7), the central point with shared medium at the 25th (median $28.6) and the cautious point at the 34th (median $46.2).

### What the bands vary, and what they do not

Each scenario's switches are held. The draws are the estimates behind a scenario: the plant estimate (a third to 1.5 times; for the food-grade plant with shared medium
not below a plant with everything animal cells must have), the financing charge (12.3 to 23.6%, mode 17.3%), the life of the filter
membranes (900 to 5,500 litres per m², mode 3,960), the upkeep share of respiration (31 to 100%), the medium price (0.6 to 1.5 times the setting) and the loss
rate (0.3 to 2 times). The cell traits and speed are not drawn: they are what the scenarios differ in, and "What to prioritise" shows what each is
worth. This differs from the earlier `floor_mc`, which drew the cell traits too (it was a band around cells that make almost no ammonia or lactate); that run is unchanged and kept.

## Doubling time: the evidence, the choice, the alternative

The measured low-waste meat-cell cultures never doubled in 24 hours:

- Hubalek et al. 2023 (bovine fibro-adipogenic progenitors, spinner flasks, full text): with glutamine, ammonia 0.70 mol/kg and a 25.7 h doubling;
  glutamine replaced by alpha-ketoglutarate 42.9 h, pyruvate 47.6, glutamate 48.8, alpha-ketoglutarate and pyruvate together 54.2 h; 38.0 h in the
  same paper's baseline culture. The difference is not significant at n = 5; the point estimates are 13 to 43% slower.
- The fastest low-ammonia growth found is 0.39 per day (42.9 h), not 0.69 (24 h). In every dataset in `waste_tricks_sizing.md` the growth rate
  is 0.35 to 0.65 per day when the low-waste condition holds, never 0.69 with the ammonia criterion met.
- Other measured meat cells: chicken in perfusion about 48 h (SuperMeat 2024); chicken in animal-free medium 61 h (Pasitka 2024); bovine muscle stem
  cells in serum-free medium 39 h (Stout 2022); fish (Mack1) 24 h on a surface with serum.

**Choice: 36 hours for the low-lactate example.** The value sits between the ordinary cells' speed (25.7 h) and the one measured low-waste
culture (42.9 h), nearer the slow end, because fast growth and low waste have never been shown together. Rough judgements made while
building the model with an AI assistant, not measured and not reviewed by an expert: 24 h together with ammonia at or below 0.14 about
10% (it would need the glutamine-fed speed without the glutamine's waste); 30 h or faster about 25%; 36 h or faster about 45%; 43 h or
faster about 70% (43 h is measured). What would have to be true for 24 h: a low-waste meat-cell culture growing as fast as a glutamine-fed
one. **Alternative (2026-11-15 figures):** 24 h costs $27.35 instead of $29.92 (−$2.6, about 9%); 30 h costs $28.68. For the food-grade plant with shared medium, $24.95 at 24 h, $25.92 at
30 h, $26.81 at 36 h. So speed is worth about $1.9 to 2.6 a kilo here, against $9.6 for cells that make almost no ammonia or lactate, $3.0 for no growth factors, $1.4 for medium at $0.15 a litre.

## What decides the low-lactate example

Each switch moved alone (cost change; change in world share in percentage points; `scenarios.priorities`):

| switch | best setting | worst setting |
|---|---|---|
| kind of cells | almost no ammonia or lactate −$9.6 (+0.7 pts) | ordinary +$83.6 (−0.4 pts) |
| price of the medium | $0.05 (an aspiration) −$4.0 (+0.2); $0.15 −$1.4 | $0.50 +$8.6 (−0.2) |
| growth factors | none −$3.0 (+0.1) | all +$7.0 (−0.2) |
| gas the cells tolerate | 6 mm/s −$2.0 (+0.1) | 2 mm/s +$5.4 (−0.1) |
| tank tricks | recycled pure oxygen too −$2.0 (+0.1), but it fails the loop checks | none +$3.6 (−0.1) |
| the plant | food-grade with shared medium −$3.1 (+0.1) | pharma-style +$0.9 (−0.0) |
| growth speed | 24 h −$2.6 (+0.1) | 43 h +$1.4 (−0.0) |
| runs lost | 0.2% a day −$1.0 (+0.0) | 2% +$1.4 (−0.0) |
| restart after a loss | 4 days, from a neighbouring tank −$0.8 (+0.0) | 30 days +$1.3 (−0.0) |
| tank shape | 1.6 −$0.4 (+0.0), but beyond the loop checks | 0.5 +$0.6 |

The share changes are at the point cost and are small because the central share is small (0.4% at the point cost). Gas matters more than it
did, because oxygen, not CO₂, now limits the central tank: more gas means more oxygen.

Interactions (computed, `scenarios.interactions`): cells that make almost no ammonia or lactate save $9.6 as things stand and $13.1 if cells also doubled every 24 h (they reinforce
each other); they save $8.3 with no growth factors and $7.2 at $0.05 a litre (they overlap: all three attack the same medium cost, and each litre of
medium must also pass the filter and carries protectant). 6 mm/s of gas would save $2.0 in the low-lactate example but only $0.2 with recycled oxygen in the column;
in the cautious case $8.7 but only $0.5. The tricks do the job of the gas. A tank trick matters little if the cells waste a lot: with ordinary cells
no tank trick reaches the medium cost that washing out ammonia sets (the cells-by-tank grid on the page).

## What would move each scenario

- **All-favourable example**: a culture that doubles in 24 hours at ammonia of 0.055 mol/kg and lactate 0.5 per glucose at density (one mass balance
  run); a food-grade plant with shared medium costed and built for animal cells; a column run with dense meat cells (passes, pH, shear); cells that need no growth factors at scale.
  The tank tricks alone are worth only $0.7 here, so the all-favourable example rests on the cells.
- **The low-lactate example** (needs CELLS): the doubling time of low-waste meat cells (can it reach 26 to 30 h?); ammonia and lactate per kilo
  at a 36 h doubling in a stirred tank, not a spinner flask (the same paper's shaker value is ten times lower: cause unexplained); the price of medium and of
  growth factors at production scale on a stated mass basis; the gas flow dense meat cells tolerate at 20 m3 (4 mm/s) and whether a column is needed at all.
- **Cautious** (FEED at most): the one thing that would lower it is a repeat of the low-waste culture at 24 to 30 h; what would raise it is a loss rate above 1% a day
  at scale or a medium that stays at $0.50.

## Caveats

- The central values (36 h, 2 ng, 4 mm/s, 30% growth factors, $0.20 a litre, 1% a day) are judgement between measured points; each is labelled in `inputs.py`.
- The share is a long-run ceiling at the model's central demand settings, not a forecast, and falls steeply with cost: the low-lactate example's band spans 0.2% to 2.4%.
- Tank design is optimised (cheapest pair that passes the loop checks); a reader who moves a switch by hand can leave the checks, and the page says so.
- The scenarios inherit every limit of `floor_physics.explore`: perfusion at 20 m3 is not shown with a retention device, and the gas-flow ceiling is a rule of thumb.
  Other vessels and operating modes are priced in `vessels.py` (`vessels_and_modes.md`).
