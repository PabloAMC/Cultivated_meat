# Cost scenarios: settings, why, what each needs, and what would move them

> **Updated 2026-11-15 (late), second time.** Every figure in this note is recomputed with the model as it now stands: the hollow-fibre
> filter loop with its membranes (`retention.py`), the bubble protectant (poloxamer 188, 2 g/L at an assumed $30/kg), antifoam's
> quarter cut to the sparger's oxygen transfer, and bought oxygen for a yeast-style plant. Earlier versions are in git history (best case
> $6.57 and central $18.14 with the old device; $8.95 and $26.64 with the filter loop alone). With antifoam counted, oxygen limits the
> central and cautious cases, and each scenario's tank design was chosen again.

Code: `scenarios.py` (the switches and presets), `page_sections.py` and `page_scenarios.js` (the page), `tests/test_scenarios.py`.
Inputs: `inputs.py`, the `sc_*` block (each with source, range, note). Every cost below is computed by `floor_physics.explore`; run
`python scenarios.py` to reproduce this note's numbers and `python scenarios.py --markdown` for the table.

## The ladder (2026-11-16)

The page and RESULTS now lead with a ladder: each rung adds one kind of change to the one before, easiest first. Rungs 3 to 5 are
exactly Central, Central with shared medium and the best case below, so the rest of this note stands. Rung 1 (`today`) is the
cautious scenario's cells, plant, gas and prices with no tank tricks in the ordinary tall tank; rung 2 (`process`) adds the tricks,
4 mm/s, a 14-day restart, growth factors at 30% and $0.20 medium. The cautious scenario is no longer on the page; `scenarios.ORDER`
keeps it for the side studies. The forecast row is the author's median for each switch by 2035 (RESULTS, "The forecast").

| scenario | cells, $/kg (10th–90th percentile) | R vs $12 meat | share of world meat, long run: at the point cost | median of draws (10th–90th) | hardest thing it needs |
|---|---|---|---|---|---|
| 1. Today: the best meat cells measured, in an ordinary 20 m³ perfusion tank | **$63.0** ($51–81) | 5.66 | 0.0% | **0.0%** (0.0–0.1%) | needs a change of feed, process or plant |
| 2. Plus process changes and cheaper inputs | **$30.7** ($28–39) | 2.98 | 0.4% | **0.2%** (0.0–0.6%) | needs a change of feed, process or plant |
| 3. Plus cells selected for low waste (Central) | **$29.4** ($27–38) | 2.87 | 0.4% | **0.2%** (0.1–0.6%) | needs selection or adaptation of cells |
| 4. Plus a food-grade plant with shared medium | **$26.6** ($25–35) | 2.63 | 0.5% | **0.3%** (0.1–0.8%) | needs selection or adaptation of cells |
| 5. Plus engineered cells: the best case, everything works | **$9.7** ($9–12) | 1.22 | 8.0% | **3.8%** (1.2–9.8%) | needs genetic engineering |
| Forecast for 2035: a first draft of the author's medians | **$24.8** ($23–33) | 2.48 | 0.6% | **0.3%** (0.1–0.9%) | needs selection or adaptation of cells |
| Humbird's optimistic design: engineered cells in an ordinary perfusion tank | **$12.5** ($10–15) | 1.46 | 4.3% | **2.4%** (0.7–6.9%) | needs genetic engineering |
| As a company reports (SuperMeat 2024) | **$34.4** | 3.28 | 0.3% | **0.2%** (0.0–0.6%) | a company's own report |

What each step is worth, from `scenarios.run`: today's cells cost $62.96 in the ordinary tank. The tank tricks alone take $20.57 off
(chosen by `design` with today's other switches), 4 mm/s of gas $17.17, a 14-day restart $2.30, growth factors at 30% $2.99, $0.20
medium $2.87; together, with the tank design chosen again, $32.23, to $30.73. Selection then takes $1.31 off (Central $29.42), the
plant with shared medium $2.86 ($26.56), and engineered cells with every switch at its cheapest plausible setting $16.90 ($9.66).

**Since 2026-11-16 every scenario holds dissolved oxygen at about half of air saturation** (`scenarios.always`, `sc_do_setpoint`), which
took Central from $29.92 to $29.42 and let the best case reach the thickness limit with recycled oxygen and a squat tank ($9.66). **The
sections below this one were computed before that change** and keep their figures (Central $29.92, best case $9.71); the differences are
under $0.6 a kilo.

## Why scenarios, not a floor

Until 2026-11-15 the model quoted one number, "the floor", $11.5/kg of cells. It was `explore()` at its defaults: a standard 20 m3
stirred tank in perfusion at 120 g/L, a food-grade plant, engineered cells, no tank tricks, no lost runs, no growth
factors. That is neither a best case (the model has since gained tank tricks, a plant built item by item, explicit ammonia and lactate)
nor a typical one (it assumes cells nobody has shown and ignores contamination). It stays as the labelled reference
(`scenarios.reference()`), and the cost is described by scenarios, each a preset of ten switches.

## The switches and where each setting comes from

Tags: **GE** needs genetic engineering; **SELECT** needs selection or adaptation of cells; **FEED** needs a change of feed, process or
plant design; **nothing new** has been done.

| switch | settings (tag) | evidence |
|---|---|---|
| kind of cells | engineered: ammonia 0.055 mol/kg, lactate 0.5 per glucose, 3 ng (GE) · selected on a low-waste feed: 0.14, 0.42, 2 ng (SELECT) · best meat cells measured: 0.14, lactate 1.05 per glucose, glucose 0.84 mol/kg, 2 ng (FEED) · ordinary: 0.70, 1.05, 0.84, 2 ng (nothing new) | Ammonia 0.054 is Humbird's enhanced cell; the CHO plateau that clears it (0.54 fmol/cell/h) is an upper bound from cells that were not net-growing. 0.14 is an upper bound from Hubalek 2023 (bovine cells, glutamine replaced by alpha-ketoglutarate, pyruvate or glutamate: "more than 5-fold" below 0.70). Lactate 0.39 was reached by adapting CHO; 0.42 allows a little for meat cells, for which nothing is measured. 1.05 is chicken (Pasitka 2024, snippet) and similar for bovine. Mass 2 ng: chicken cells are reported at 1.0 to 1.75 ng, Humbird's is 3; no mass was found for the bovine cells. (`waste_tricks_sizing.md`, `waste_and_medium_evidence.md`) |
| growth speed | 24 h (SELECT) · 30 h (SELECT) · 36 h (SELECT) · 43 h (nothing new) | See "Doubling time" below. |
| plant | lean (FEED) · sterile (nothing new) · pharma-style (nothing new) | `plant_items.py`, `cheap_plant_study.md`. Sterile: Humbird's plant with a sanitary hall in place of the clean room, $810k per m3. Lean: no clean room, food-grade tanks, a shared medium line, two seed trains, bought oxygen: $340k per m3 (2018 dollars; nobody has built one). Pharma-style: Humbird as designed, $910k. A plant as cheap as a yeast plant is **not offered**: the judgement is that nothing shows animal cells can be grown that way (Pablo, 2026-11-15). |
| gas the cells tolerate | 6 mm/s (FEED) · 4 (FEED) · 2 (nothing new) | Humbird's 6 mm/s is his conversion of a rule of thumb ("under 0.1 vvm"), not a measured limit; Nienow 2006 reports 0.1 to 2 mm/s in 8 to 20 m3 tanks; bubble death scales with gas per litre, foam with surface velocity (`gas_flow_cap.md`). 4 is a midpoint. |
| tank tricks | none · column on a pumped loop (FEED) · column and 1 bar gauge · column, pressure and recycled oxygen (all FEED) | `gas_exchange.column_design`, `gas_exchange_study.md`: sized by calculation; no animal cells have gone through such a column. |
| tank shape | liquid 0.5 / 0.75 / 1.0 / 1.6 times as deep as wide | geometry is certain; the extra steel and floor of a squat tank are counted (`gas_exchange.shape_capex_factor`); no cost data on tank shape. |
| runs lost | 0.2 / 0.6 / 1 / 2% a day | 0.2% is large pharma (`pf_hazard_pharma`); the survey of makers (Powell 2025: 11.2% of batches lost, 19.5% beyond flasks) implies 0.6 to 2.2% a day **if** runs lasted 10 to 20 days, which the survey does not state. |
| restart after a loss | 4 / 14 / 21 / 30 days | 4 days reseeding from a healthy neighbouring tank (FEED; added 2026-11-16; about 2 days to clean and steam, a doubling to regrow, a day for the neighbour's lost output; the donor must test clean); 14 days with a ready seed train (regrowing from a seed is about 7 doublings); 21 days when the seed trains must be regrown; 30 when one failure reaches every tank (`contamination.py`). |
| growth factors | none (GE) · 30% (FEED) · 60% · all of Humbird's price | His price assumes an industry far larger than today's; cells that make their own were shown in cattle cells by genetic engineering. 30% and 60% are judgement. |
| medium price | $0.05 / 0.15 / 0.20 / 0.30 / 0.50 a litre | $0.05 is an aspiration nobody has reported (lowest company report $0.07; GFI's amino acids alone $0.02-0.17; below it the medium costs what the cells must eat, `nutrient_floor.md`); $0.15 was this note's earlier estimate of the nutrients themselves; $0.20 is what several companies announced for 2025 (GFI 2026 report, p.8; not verified at scale); $0.50 is SuperMeat. |

## The scenarios, and the rule that defines each

| scenario | settings | rule |
|---|---|---|
| Best case: everything works | engineered cells, 24 h, food-grade plant with shared medium, 6 mm/s, 0.6% a day, 14-day restart, no growth factors, $0.15 a litre, **tank design: the column and 1 bar, a tank as deep as wide** | Cells, speed, plant, gas, medium and growth factors at their cheapest setting; losses at the low end of what makers report (0.2% is pharma's and is not assumed); tank design the cheapest pair whose loop passes the checks. |
| Central: selection and feed only, food-grade plant | selected cells, 36 h, food-grade plant, 4 mm/s, 1% a day, 14-day restart, growth factors 30%, $0.20 a litre, **tank design: the column and 1 bar, a tank as deep as wide** | Cells that have been measured or that selection can reach (no genetic engineering); every other switch at the setting nearest the middle of what is reported; tank design as above. |
| Central, food-grade plant with shared medium | the same in a food-grade plant with shared medium | As Central. |
| Cautious: the best meat cells measured so far | best measured cells, 43 h, food-grade plant, 2 mm/s, 1% a day, 21-day restart, growth factors 60%, $0.30 a litre, **tank design: the column and 1 bar, the ordinary tall tank** | Each switch at the setting that has actually been measured; tank design as above. |

"The checks" (`scenarios.design`): the loop must be pH-safe (the alkaline exposure within the 55 mbar, 0.5 m3 design) and at a pass rate dense
cultures have taken (15 to 24 tank volumes an hour). Without the checks a tall tank with all three tricks would be a little cheaper still.

Computed results (cells $/kg; shop; R against $12 meat; long-run share of world meat by weight; bands are 10th to 90th percentile, 4,000 draws; **the headline share is the median of the draws**, the point estimate is the share at the scenario's own point cost):

| scenario | cost | band | shop | R | **world share, median** | band incl. demand | world, point estimate | US (point) | Europe (point) | without the tank tricks | ordinary tall tank |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Best case | $9.71 | $9.2–12.2 | $14.7 | 1.23 | **3.8%** | 1.2–9.7% | 7.9% | 13.5% | 25.3% | $10.2 | $10.4 |
| Central, food-grade plant | $29.92 | $27.4–38.1 | $34.9 | 2.91 | **0.2%** | 0.1–0.6% | 0.4% | 0.9% | 2.3% | $33.5 | $36.2 |
| Central, food-grade plant with shared medium | $26.81 | $25.4–34.8 | $31.8 | 2.65 | **0.3%** | 0.1–0.7% | 0.5% | 1.2% | 3.5% | $28.5 | $29.9 |
| Cautious | $43.79 | $39.2–54.5 | $48.8 | 4.07 | **0.1%** | 0.0–0.2% | 0.1% | 0.3% | 0.5% | $63.0 | $63.0 |
| Reference (standard tank, no tricks) | $12.51 | | $17.5 | 1.46 | | | 4.3% | 8.5% | 19.6% | | |
| As a company reports | $34.35 | | $39.4 | 3.28 | | | 0.3% | 0.6% | 1.3% | | |

**Why the median and not the point estimate.** Each point cost sits below its band's median cost, because the estimates behind a scenario are drawn with
more room to fall short than to improve. The share rises steeply as the price falls, so the share at the point cost is higher than the median share.
A headline of 7.9% for the best case would be a number most draws do not reach, since the median is 3.8%. The page keeps the point estimate where
it is labelled as one. The band exists for the four scenarios. Once a reader changes a switch, the live strip shows the point estimate and says so.
At 1,000 draws the best case's median moved by 0.3 points between seeds (7.8 to 8.15, with the old device), so the bands use 4,000.

**Tank design nobody has run with animal cells.** Each scenario's tank design is the cheapest the loop checks allow. Each rests on tricks
that are calculated, not measured. Best case and Central: a column, 1 bar of extra pressure, and a tank as deep as it is wide. Cautious: the
column and the pressure in the ordinary tall tank. Recycled pure oxygen through the column would be cheaper still in Central (−$2.0) but fails the
loop checks. "Without the tank tricks" sets the tricks switch to "none" and keeps the tank shape (Central: +$3.6). "Ordinary tall tank" also takes
the shape back to Humbird's 1.6 (Central: +$6.3). The page and the scenario stories (`scenarios.tricks_sentence`) state this beside each scenario.

Each point sits below its band's median, because the estimates behind a scenario (the plant estimate, financing, the life of the filter membranes) are drawn with more room to fall short than to improve: the best case's point ($9.71) is at the 25th percentile of its draws (median $10.3), the central point ($29.92) at the 31st (median $31.7), the central point with shared medium at the 25th (median $28.6) and the cautious point at the 34th (median $46.2).

### What the bands vary, and what they do not

Each scenario's switches are held. The draws are the estimates behind a scenario: the plant estimate (a third to 1.5 times; for the food-grade plant with shared medium
not below a plant with everything animal cells must have), the financing charge (12.3 to 23.6%, mode 17.3%), the life of the filter
membranes (900 to 5,500 litres per m², mode 3,960), the upkeep share of respiration (31 to 100%), the medium price (0.6 to 1.5 times the setting) and the loss
rate (0.3 to 2 times). The cell traits and speed are not drawn: they are what the scenarios differ in, and "What to prioritise" shows what each is
worth. This differs from the earlier `floor_mc`, which drew the cell traits too (it was a band around engineered cells); that run is unchanged and kept.

## Doubling time: the evidence, my choice, the alternative

The measured low-waste meat-cell cultures never doubled in 24 hours:

- Hubalek et al. 2023 (bovine fibro-adipogenic progenitors, spinner flasks, full text): with glutamine, ammonia 0.70 mol/kg and a 25.7 h doubling;
  glutamine replaced by alpha-ketoglutarate 42.9 h, pyruvate 47.6, glutamate 48.8, alpha-ketoglutarate and pyruvate together 54.2 h; 38.0 h in the
  same paper's baseline culture. The difference is not significant at n = 5; the point estimates are 13 to 43% slower.
- The fastest low-ammonia growth I can source is 0.39 per day (42.9 h), not 0.69 (24 h). In every dataset in `waste_tricks_sizing.md` the growth rate
  is 0.35 to 0.65 per day when the low-waste condition holds, never 0.69 with the ammonia criterion met.
- Other measured meat cells: chicken in perfusion about 48 h (SuperMeat 2024); chicken in animal-free medium 61 h (Pasitka 2024); bovine muscle stem
  cells in serum-free medium 39 h (Stout 2022); fish (Mack1) 24 h on a surface with serum.

**Choice: 36 hours for the central case.** Selection acts most directly on growth rate, so the central value should sit nearer the ordinary cells'
speed (25.7 h) than the one measured low-waste culture (42.9 h), but the combination has never been shown. My odds (labelled judgement): 24 h together
with ammonia at or below 0.14 about 10%; 30 h or faster about 25%; 36 h or faster about 45%; 43 h or faster about 70%. **Alternative:** 24 h, as the
engineered-cell scenario assumes, costs $27.35 instead of $29.92 (−$2.6, about 9%); 30 h costs $28.68. For the food-grade plant with shared medium, $24.95 at 24 h, $25.92 at
30 h, $26.81 at 36 h. So speed is worth about $1.9 to 2.6 a kilo here, against $9.6 for engineered cells, $3.0 for no growth factors, $1.4 for medium at $0.15 a litre.

## What decides the central case

Each switch moved alone (cost change; change in world share in percentage points; `scenarios.priorities`):

| switch | best setting | worst setting |
|---|---|---|
| kind of cells | engineered −$9.6 (+0.7 pts) | ordinary +$83.6 (−0.4 pts) |
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

Interactions (computed, `scenarios.interactions`): engineered cells save $9.6 as things stand and $13.1 if cells also doubled every 24 h (they reinforce
each other); they save $8.3 with no growth factors and $7.2 at $0.05 a litre (they overlap: all three attack the same medium cost, and each litre of
medium must also pass the filter and carries protectant). 6 mm/s of gas would save $2.0 in Central but only $0.2 with recycled oxygen in the column;
in the cautious case $8.7 but only $0.5. The tricks do the job of the gas. A tank trick matters little if the cells waste a lot: with ordinary cells
no tank trick reaches the medium cost that washing out ammonia sets (the cells-by-tank grid on the page).

## What would move each scenario

- **Best case** (needs GE): a culture of engineered cells that doubles in 24 hours at ammonia of 0.055 mol/kg and lactate 0.5 per glucose at density (one mass balance
  run); a food-grade plant with shared medium costed and built for animal cells; a column run with dense meat cells (passes, pH, shear); cells that need no growth factors at scale.
  The tank tricks alone are worth only $0.7 here, so the best case rests on the cells.
- **Central** (needs SELECT): the doubling time of low-waste meat cells after adaptation (does it return to 26 to 30 h?); ammonia and lactate per kilo
  at a 36 h doubling in a stirred tank, not a spinner flask (the same paper's shaker value is ten times lower: cause unexplained); the price of medium and of
  growth factors at production scale on a stated mass basis; the gas flow dense meat cells tolerate at 20 m3 (4 mm/s) and whether a column is needed at all.
- **Cautious** (FEED at most): the one thing that would lower it is a repeat of the low-waste culture at 24 to 30 h; what would raise it is a loss rate above 1% a day
  at scale or a medium that stays at $0.50.

## Caveats

- The central values (36 h, 2 ng, 4 mm/s, 30% growth factors, $0.20 a litre, 1% a day) are judgement between measured points; each is labelled in `inputs.py`.
- The share is a long-run ceiling at the model's central demand settings, not a forecast, and falls steeply with cost: the central case's band spans 0.2% to 2.4%.
- Tank design is optimised (cheapest pair that passes the loop checks); a reader who moves a switch by hand can leave the checks, and the page says so.
- The scenarios inherit every limit of `floor_physics.explore`: perfusion at 20 m3 is not shown with a retention device, the gas-flow ceiling is a rule of thumb, and the model does not
  yet describe other vessels (airlift, bubble column) or operating modes (batch, fed-batch, chemostat), which a later session will add (`research_notes/page_structure.md`).
