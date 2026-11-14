# Cost scenarios: settings, why, what each needs, and what would move them

Code: `scenarios.py` (the switches and presets), `page_sections.py` and `page_scenarios.js` (the page), `tests/test_scenarios.py`.
Inputs: `inputs.py`, the `sc_*` block (each with source, range, note). Every cost below is computed by `floor_physics.explore`; run
`python scenarios.py` to reproduce this note's numbers and `python scenarios.py --markdown` for the table.

## Why scenarios, not a floor

Until 2026-11-15 the model quoted one number, "the floor", $11.5/kg of cells. It was `explore()` at its defaults: a standard 20 m3
stirred tank in perfusion at 120 g/L, a sterile plant without clean rooms, engineered cells, no tank tricks, no lost runs, no growth
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
| restart after a loss | 14 / 21 / 30 days | `contamination.py`; 21 days when the seed trains must be regrown; 30 when one failure reaches every tank. |
| growth factors | none (GE) · 30% (FEED) · 60% · all of Humbird's price | His price assumes an industry far larger than today's; cells that make their own were shown in cattle cells by genetic engineering. 30% and 60% are judgement. |
| medium price | $0.15 / 0.20 / 0.30 / 0.50 a litre | $0.15 is the cost of the nutrients themselves (the medium cannot cost less); $0.20 is what several companies announced for 2025 (GFI 2026 report, p.8; not verified at scale); $0.50 is SuperMeat. |

## The scenarios, and the rule that defines each

| scenario | settings | rule |
|---|---|---|
| Best case: everything works | engineered cells, 24 h, lean plant, 6 mm/s, 0.6% a day, 14-day restart, no growth factors, $0.15 a litre, **tank design: the column and 1 bar, a squat tank** | Cells, speed, plant, gas, medium and growth factors at their cheapest setting; losses at the low end of what makers report (0.2% is pharma's and is not assumed); tank design the cheapest pair whose loop passes the checks. |
| Central: selection and feed only, sterile plant | selected cells, 36 h, sterile plant, 4 mm/s, 1% a day, 14-day restart, growth factors 30%, $0.20 a litre, **tank design: all three tricks, a very squat tank** | Cells that have been measured or that selection can reach (no genetic engineering); every other switch at the setting nearest the middle of what is reported; tank design as above. |
| Central, lean plant | the same in a lean plant | As Central. |
| Cautious: the best meat cells measured so far | best measured cells, 43 h, sterile plant, 2 mm/s, 1% a day, 21-day restart, growth factors 60%, $0.30 a litre, **tank design: column and pressure, a squarer tank** | Each switch at the setting that has actually been measured; tank design as above. |

"The checks" (`scenarios.design`): the loop must be pH-safe (the alkaline exposure within the 55 mbar, 0.5 m3 design) and at a pass rate dense
cultures have taken (15 to 24 tank volumes an hour). Without the checks a tall tank with all three tricks would be a little cheaper still.

Computed results (cells $/kg; shop; R against $12 meat; long-run share of world meat by weight; bands are 10th to 90th percentile, 1,000 draws):

| scenario | cost | band | shop | R | world | band incl. demand | US | Europe |
|---|---|---|---|---|---|---|---|---|
| Best case | $6.57 | $6.3–8.1 | $11.6 | 0.96 | 15.2% | 2.7–17.2% | 22.5% | 33.6% |
| Central, sterile plant | $18.14 | $16.2–21.8 | $23.1 | 1.93 | 1.5% | 0.2–2.4% | 3.5% | 10.7% |
| Central, lean plant | $15.84 | $14.8–18.9 | $20.8 | 1.74 | 2.3% | 0.3–3.2% | 5.0% | 14.0% |
| Cautious | $32.29 | $29.2–41.0 | $37.3 | 3.11 | 0.3% | 0.0–0.5% | 0.7% | 1.7% |
| Reference (standard tank, no tricks) | $11.48 | | $16.5 | 1.37 | 5.4% | | 10.0% | 21.6% |
| As a company reports | $34.35 | | $39.4 | 3.28 | 0.3% | | 0.6% | 1.3% |

Each point sits below its band's median, because the estimates behind a scenario (the plant estimate, financing, the retention device) are drawn with more room to fall short than to improve: the best case's point ($6.57) is at the 18th percentile of its draws (median $7.2), the central point ($18.14) at the 37th (median $18.9), the lean central point at the 27th and the cautious point at the 31st.

### What the bands vary, and what they do not

Each scenario's switches are held. The draws are the estimates behind a scenario: the plant estimate (a third to 1.5 times; for the lean plant
not below a plant with everything animal cells must have), the financing charge (12.3 to 23.6%, mode 17.3%), the retention device
($0 to $460k per m3, mode $89k), the upkeep share of respiration (31 to 100%), the medium price (0.6 to 1.5 times the setting) and the loss
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
engineered-cell scenario assumes, costs $16.84 instead of $18.14 (−$1.3, about 7%); 30 h costs $17.80. For the lean plant, $14.89 at 24 h, $15.55 at
30 h, $15.84 at 36 h. So speed is worth about $1 to 1.5 a kilo here, against $3.8 for engineered cells, $3.0 for no growth factors, $1.4 for the cheapest medium.

## What decides the central case

Each switch moved alone (cost change; change in world share in percentage points; `scenarios.priorities`):

| switch | best setting | worst setting |
|---|---|---|
| kind of cells | engineered −$3.8 (+1.5 pts) | ordinary +$34.8 (−1.5 pts) |
| price of the medium | $0.15 −$1.4 (+0.4) | $0.50 +$8.6 (−1.0) |
| growth factors | none −$3.0 (+1.0) | all +$7.0 (−0.9) |
| tank tricks | (already all three) | none +$4.9 (−0.7) |
| growth speed | 24 h −$2.7 (+0.9) | 43 h +$1.6 (−0.3) |
| the plant | lean −$2.3 (+0.7) | pharma-style +$0.7 (−0.2) |
| runs lost | 0.2% a day −$0.8 (+0.2) | 2% +$1.1 (−0.2) |
| restart after a loss | (14 days) | 30 days +$1.0 (−0.2) |
| tank shape | 1.6 −$0.7 (+0.2), but beyond the loop checks | 0.5 $0.0 |
| gas the cells tolerate | 6 mm/s −$0.3 (+0.1) | 2 mm/s +$0.4 (−0.1) |

Interactions (computed, `scenarios.interactions`): engineered cells save $3.8 as things stand and $5.4 if cells also doubled every 24 h (they reinforce
each other); they save $2.5 with no growth factors and $3.2 at $0.15 a litre (they overlap: all three attack the same medium cost). In the cautious case, 6 mm/s of
gas would save $7.0 but only $0.4 if all three tank tricks were in place: the tricks do the job of the gas. A tank trick matters little if the cells waste a lot:
with ordinary cells no tank trick reaches the medium cost that washing out ammonia sets (the cells-by-tank grid on the page).

## What would move each scenario

- **Best case** (needs GE): a culture of engineered cells that doubles in 24 hours at ammonia of 0.055 mol/kg and lactate 0.5 per glucose at density (one mass balance
  run); a lean plant costed and built for animal cells; a column run with dense meat cells (passes, pH, shear); cells that need no growth factors at scale.
  The tank tricks alone are worth only $0.8 here, so the best case rests on the cells.
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
