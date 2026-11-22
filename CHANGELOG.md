# Change log

## 2026-11-22 (fifth batch), page

No change to the model's arithmetic or inputs. The page has one set of controls, and the setting "Tank tricks" has a literal name.

- **The side bar is the page's only set of controls.** The level "How the tank and the plant set the cost" had two control sets of
  its own (the eleven scenario switches with "Pick the cheapest tank design", and the explorer "Every cell and tank setting" with its
  own sliders, "Start from a reference point" and "Start from a kind of cell"), which synced one way and could show a cost the side
  bar did not. What the side bar lacked moved into it, by section:
  - *The cells*: "Reported cells", presets that take a reported cell's doubling time and weight, and its CO₂ tolerance where one is
    reported, named by their traits and source (Humbird's 2021 design; chicken cells in perfusion, SuperMeat 2024; bovine muscle stem
    cells without serum, Stout 2022; Atlantic mackerel cells, Saad 2023; insect cells, Ashizawa 2022), with "Where these come from";
    under "More settings for the cells": glucose used per kilo of cells (shows the cells' own balance until set) and fat taken from
    the feed.
  - *The reactor*: the tank design ("Added equipment for oxygen and CO₂" and "Tank shape") with the button "Pick the cheapest tank
    design for these settings" and its explanation; the plant item by item; two more classes of plant (a yeast plant plus what animal
    cells must have; a plant built like a yeast plant); under "More settings": the chance of losing a run, days to restart after a
    contamination, planned length of a continuous run, pressure at the top of the tank, CO₂ the culture leaves the column at, the
    dissolved oxygen held, and the pH.
  - *The medium*: growth factors bought on top of the medium's price.
  - *Near the top*: the other reference points (the low-lactate example, the all-favourable example, Humbird's optimistic design) as
    chips under the two starting points, and "Where each reference point comes from".
  Each new lever shows the engine's own value until it is moved (tested: set to what it shows, the cost does not move, for every
  reference point). A switch picked in the table of two settings frees the lever that sets the same thing.
- **The level shows results only**, all from the side bar's state and priced as the first screen prices it (with the vessel, the
  retention device, the class of plant and the items): the result card, "What limits this tank", the plant item by item, the cost
  in six parts, the factors moved one at a time (whose buttons now set the side bar's levers), the table of two settings (its
  outlined figure is the side bar's own cost), the vessel table, the cost as the medium gets cheaper. Its intro says the side bar
  sets it. Removed, not moved: the controls the side bar already had (doubling time, cell mass, yearly charge, medium price, upkeep
  share, CO₂ and gas tolerated, salt, least flow, tank size, mode, ammonia, lactate, the eleven switch selects), the waste dial
  (the side bar sets ammonia and lactate directly), the share of the product that is cells (the side bar's plant protein in a cut),
  the sorbent's share, price and uses (the side bar's ammonium-exchanger route), and the explorer's own US share sentence.
- **Links**: the address carries the new settings (`pc:` class of plant, `it:` items, `h.<lever>`); links written before still
  read. The explorer had no saved state.
- **"Tank tricks" is now "Added equipment for oxygen and CO₂"** (the column that strips CO₂ without bubbles, extra pressure, and
  recycled pure oxygen) on the page, in scenarios.py's labels and notes, in RESULTS, METHODS and the research notes, and in the tests'
  messages. Code keys (`tricks`, "none"/"column"/"pressure"/"oxygen") are unchanged.
- Tests: `tests/test_easy_view.py` checks the new side-bar pieces in order, that the level has no controls and says the side bar sets
  it, that its result card gives the side bar's cost in four states, the address round trip and an old link.

## 2026-11-21 (fourth batch), documents

No change to the model's behaviour or inputs. Prose that quoted figures the engine had moved past, recomputed from the modules
(tables by their header line). Old → new:

- **RESULTS and METHODS.** The all-favourable example's draws in METHODS $8.6 ($7.2–10.4) and $9 ($8–11) → $8.3 ($7.1–10.0), as
  the table has; the low-lactate example's $53 ($40–77) → $52 ($39–76); Humbird's optimistic design takes 1.6% (0.8%, 0.2–3.0%)
  → 1.4% (0.7%, 0.2–2.6%); the all-favourable cells with the ordinary demand, middle draw 4.4% (1.5–13.8%) → 3.9% (1.4–12.7%);
  conventional meat's price response takes 4.5 (and 3.9) points off the all-favourable example → 4.1 (fixed price 26.4% → 27.4%;
  supply-elasticity range 19.3–25.3% → 19.9–26.2%); closed markets 22.8% → 22.6% became 23.6% → 23.4%; the flat-$5 comparison
  at the low-lactate example's cost (shelf $54.5/$72.2 → $53.7/$71.1, share 0.05% → 0.045%; the all-favourable example 6.9%/5.4% →
  6.8%/5.6%); mince against US minced beef or pork cuts at the all-favourable example's cost 11.5% (1.2×) → 12.7% (1.1×), at the
  low-lactate example's 0.08% (6.0×) → 0.09% (5.9×); the spread's misfits 4.3/9.8/16.6/20.6 → 4.2/10.0/17.1/21.3, least 3.75 →
  3.69, the all-favourable example with the t and the normal spread 22.6%/29.3% → 23.4%/30.2%, other shapes 25.3–26.0% →
  26.2–26.9%; salmon's response 3.7–4.3 → 3.7–4.2; first-contact elasticity −1.37 → −1.38; the adoption curve 70- to 100-fold,
  half in 10–12 years, 90% in 19–24 → 72- to 105-fold, 11–13, 20–24; the sensitivity tornado (plant's cost 2.34 → 2.73, width
  19% → 24%; share swings 1.5/1.1/0.8/0.7/0.7/0.4 → 1.7/1.2/0.8/0.8/0.8/0.5 pp, in shares of the meat sold); glucose 0.32 →
  0.311 kg a kilo where quoted as current; the vessel grid's fill-and-draw $19.98 → $16.50 and airlift $30.48 → $29.96 against
  $15.72; cleaning routes $48.70/$46.03/$45.59 → $47.89/$45.24/$44.83; per-tank rule $16.03/$49.63 → $15.82/$48.80; seven days of
  maturation $98.25/$22.32 → $95.34/$19.71. RESULTS gains one line on the demand anchored on premium meats (below).
- **A conclusion that moved with the fourth batch, now written down** (`market_size_loop.md` section 5, RESULTS section 2): with
  the share taken from the curve fitted to premium real meats, the low-lactate example's own sales need 0.76 million m² of
  membrane, short of the switch, so it no longer crosses (rests at $48.25 and 0.015%; in the third batch it reached the switch
  exactly and rested at $24.69 and 0.27%).
- **`market_size_loop.md`**: the prose kept under a box since the third batch is recomputed (rest $23.91/0.54% → $24.05/0.48%; the
  all-favourable cells $6.29/6.81% → $6.30/6.27%; 2.6 → 2.4 times the switch; first sales 0.17 → 0.15 Mt; premium 0.75/0.38 →
  0.68/0.34 million m²; slow learning $30.17/0.27% → $30.30/0.24%; the 8-in-10 cost range $41–79 → $39–76).
- **`liking_spread.md`**: sections 2, 4 and 6 recomputed (31.0% → 29.8% with the normal spread, shapes that fit 24.7–28.1% →
  23.4–26.9%, the band ends $41–82 → $39–76 and fourteen- → elevenfold).
- **Side-study notes** (TODO "Side-study notes are snapshots" narrowed): `min_litres_per_kg.md` tables and prose (the
  all-favourable example at 219 g/L: its physical floor now binds, $7.01 → $6.21), `filter_flux.md` section 4 ($49.50 → $48.68,
  1,200 L/m² $72.05 → $71.67), `gf_and_doubling_bounds.md` sections 1-2 (the all-favourable example's litres 11.7 → 12.1),
  `gas_flow_cap.md` (Humbird's design at 6 mm/s $15.93 → $15.72, at 2 mm/s $35.25 → $34.67), the status box of
  `ammonia_tolerance_and_filter_life.md`, `demand_checks.md` section 5's salmon products; tables regenerated in `cost_scenarios.md`
  and `study_comparison.md` (Humbird's own perfusion plant +$16.98 → +$23.49 on his best estimate; a box says the rest is as of
  2026-11-20).
- **Prose strings in code**: the page's tornado notes now compute their figures (`floor_physics.tornado_rows`, used by
  `build_interactive.py`): growth factors at Humbird's price "about $4" → $5.7 a kilo, the oxygen limit with antifoam halved
  "97 g/L" → 86, the protectant's $0.7 and the 120 g/L; `frontier.py`'s printout computes the parity cost ($6.1). `figures/` regenerated (`report_figures.py`, `sensitivity.py`).

## 2026-11-21 (fourth batch): the demand model's open items

**Plant-based meat's committed buyers, repeat buying, and the side analyses on the share of the meat sold.** Evidence:
`research_notes/demand_checks.md` (sections 5 and 6), `demand_heterogeneity_evidence.md` (sections 3, 4 and 5). The long-run share
at equal price is untouched (`equal_price_share` 13%, `best_equal_price_share` 55%; 14.4% and 58.6% of meat buyers).

- **Plant-based meat's committed buyers** (`market_share` segment "K", mirrored in the page's `mainShares`, `segShares`,
  `solveCalibration` and in `share_x_meat_many`): 7% of shoppers (`pb_committed_share`, 2-10%; GFI/NielsenIQ 2022) buy 82% of
  the mainstream's plant-based meat (`pb_committed_volume`, 75-90%; Circana 2024 has 75%), through a solved liking
  (`pb_committed_liking`, 3.14 utils), and respond 0.25 times as strongly to its price (`pb_committed_price_x`, 0.10-0.50; Tonsor,
  Lusk & Schroeder 2021). Plant-based meat's own-price elasticity −2.89 → −1.30 (measured −1.23, the category about −1.3): the
  check passes, and stays inside the category's range at every end of the three inputs (−0.99 to −1.81). A spread of liking alone
  could not do it (a logit buyer's elasticity falls only as their own share nears one; these buyers give plant-based meat about
  5% of their meat).
- **Knock-on**: the ordinary mainstream shoppers buy plant-based meat less, so the solved real-meat weight `w_realtissue_M`
  3.40 → 5.11 utils, and a cut that is 20% plant protein loses 1.02 utils, was 0.68 (`meat_market.tier_offset`). Headline shares
  of the meat sold, world: the low-lactate example 0.050% → 0.045% (median of draws 0.058% → 0.052%, 8 in 10 0.009-0.30% →
  0.009-0.26%); the all-favourable example with its own demand 24.7% → 23.4% (median 18.9% → 17.4%), its cells with the
  ordinary demand 6.1% → 5.6%; the reported cost 0.17% → 0.16%. With the blend penalty at the old weight the all-favourable
  example would be 24.6%.
- **Price sensitivity across all shoppers, and farmed salmon**: tried with a price-insensitive class for every product and the
  spread of liking refitted (`demand_checks.md` section 6). The spread's misfit falls (4.2 → 1.7-3.0), salmon still fails (1.3-4.3
  against 1-1.5, never all four products inside), and the low-lactate example's share rises 2 to 8 times depending on how much
  those shoppers like cultivated meat, which nothing measures. Not added; left for a decision. Salmon stays failing (3.7-4.2).
- **`taste_quality_w`'s upper end** re-solves cleanly across its range (checked; METHODS's remark was stale).
- **Repeat buying and dropping out** (`adoption_timing._step`, `buying_long_run`; the page's `repStep`): `repeat_rate` 0.62
  (0.50-0.75; GFI/SPINS, 2025) and `lapse_rate` 0.14 a year (0.05-0.30; plant-based meat's US household reach 20% → 11%,
  2021-25), both drawn in the timing band (`MC_TIMING_INPUTS`, after the others). The long-run share is unchanged; at the
  reported cost the share after 5 years is 19% lower, after 10 years 16% lower; the years to 90% barely move (21 at the reported
  cost; 14 → 15 at the fast end of the fade).
- **The side analyses count the share of the meat sold**, x / (x + c): `uncertainty.py` (now through `share_x_meat_many`;
  median 0.3%, 8 in 10 0.1-1.6% → 0.1-1.8%), `sensitivity.py` (the share tornado) and `adoption_timing.py` (and the page's timing
  curve). `adoption_timing.years_for_cost` computes the years the documents quote.
- **Repinned** (old → new): `tests/test_golden.py` w_realtissue_M 3.39863 → 5.11335, w_health_M 1.39169 → 2.20457, w_health_E
  2.36651 → 2.35875, beta_ref −0.052663 → −0.054036, lusk_elas_parity_cold −1.37392 → −1.38249, income_us 1.89075 → 1.86976,
  income_china 1.38545 → 1.36397, income_nigeria 0.799218 → 0.781302, health_x_half 16.9996 → 19.656, us_pen_vol 0.423594 →
  0.379082, us_pen_val 0.83839 → 0.741859, world_pen_vol 0.172079 → 0.15554, organic_vs_cuts 20.1926 → 21.397, the elasticity
  at R = 1 in the page's prose −1.3 → −1.4 (−1.349 → −1.354); `tests/test_answer_rests_on.py` the low-lactate example's share
  0.0496 → 0.0455, the all-favourable example's with the ordinary demand 6.0674 → 5.5816, inputs 605 → 611, with a range 276 →
  281, the share spans (0.0234, 0.3429) → (0.0216, 0.3103) and (1.6331, 21.6175) → (1.5030, 20.4019);
  `tests/test_floor_physics.py` the analogue misfit at κ = 4 1.84 → 1.92; `tests/test_tank_size.py` the all-favourable switches'
  fed-batch at 100 m³ $9.4878 → $9.3395 (already failing at the base commit 4e78588, not a demand change); the 2026-11-18
  reproduction in `tests/test_liking_spread.py` now also sets `pb_committed_share` 0. `premium_buyers.shares` carries the committed
  buyers as a third segment.
- Tables regenerated by header line: `demand_checks.md`, `liking_spread.md`, `premium_curve.md`, `premium_buyers.md`,
  `market_size_loop.md`, `retail_markup_form.md`, `tank_size.md` (the fed-batch table), RESULTS and METHODS (scenarios, what it
  would take, the plant axis, what the answer rests on, the checks, the regional block).

## 2026-11-21 (fourth batch), page

No change to the model's outputs. The page's wording, its charts on a phone, and which figure it leads with (three quoted
figures change because of that, below).

- **Charts on a phone.** The charts of "How the tank and the plant set the cost" and "How a shop price becomes a share" (cost
  against the price of medium, the cost in six parts, what limits the tank and the litres it needs, the tornado, the four options
  against price, what helps and hurts, the shopper histogram, the other products, the products it could enter first) were drawn
  at a fixed width and shrank to about half size on a 375 px screen. Under 560 px they are now drawn at the box's width
  (`lvW`, `lvBox` in `build_interactive.py`; `scPartsSVG` takes the box's width): line names go inside the plot, keys and long
  captions under it, and the bar charts put each name on its own line. Wide screens draw as before. Label overlaps fixed on the
  way: the cost chart's side labels (at most eight), "equal price" under the legend, the six-part chart's column headings.
- **The entry-points chart** has one colour for every product: no zones ("cheaper now", "only in the all-favourable example",
  "not even then") and no zone words in its caption; the bar from price to cost says which is lower.
- **The point, not the median.** Level 1's cards, its steps chart (the bar ends at the most-likely-values cost; the median dot is
  gone), the steps table (columns: most likely values, 8 in 10 draws, median draw, saved), the table of Humbird's optimistic design
  and the company's report, the methods prose on the cases and Step 1, and the price calculation's first line now give the cost with every
  estimate at its most likely value, with the 8-in-10 range beside it. The ratios quoted in Step 1 follow: the low-lactate example
  6.3 → 5.9 times US minced beef or pork cuts, the all-favourable example 1.3 → 1.1, and the share at the low-lactate example's
  price 0.06% → 0.08%. The shopper histogram's caption no longer calls the cost "the median of the first screen's cloud".
- **Cells named by traits.** Level 4's switch "Kind of cells" is "The cells' ammonia and lactate", its settings named by their
  values (`scenarios.py`); the cells-by-tank table's rows are written from `scenarios.cell_traits`; "a low-ammonia feed" is "a feed
  without glutamine"; "Engineered lines" (Stout 2023) is "Immortalised lines"; the ammonia-tolerance note no longer says
  "selection could raise it".
- **Wording (#19).** Every meat price names its meat: "same shop price as meat" → "as US minced beef or pork cuts"; "the price of
  meat" → "the price of the conventional meat it copies". Literal verbs: "frame", "beat", "out of reach", "path", "price ladder",
  "quality ladder" replaced.
- **Leftovers.** `page_sections.py` loses nine unused generators (`scenario_table`, `bottlenecks`, `cells_by_tank`, `vessels`,
  `experiments`, `measured`, `chip`, `limit_text`, `tank_in_every_scenario`); `tests/render_probe.js` drew the removed `drawBars`
  and now draws the first screen's bars of each kind of meat (`tpSellBars`) at any width.
- TODO: #19, the page leftovers and the page rebuild ticked; what is left of the page is one item with three decisions.

## 2026-11-21 (third batch): fed-batch against perfusion in a tank of the same size

- `scenarios.plant_axis` now runs perfusion at 100 m³ too, and each fed-batch crosses perfusion of its own size. Before, fed-batch
  at 100 m³ was set against perfusion at 20 m³, which made a 100 m³ batch look cheaper with the shared-medium plant ($43.6 against
  $44.5). Like for like, perfusion is cheaper at the modelled plant cost in every rung ($42.0 against $43.6 at rung 5); the
  crossings at 100 m³ move 0.61/0.80/1.04/1.16 → 0.56/0.71/0.93/0.96.
- `tank_size.fedbatch_markdown` shows perfusion and fed-batch at each size (`tank_size.perfusion_at`). Only the cells that make
  almost no ammonia or lactate, at 200 m³, are cheaper in fed-batch ($24.63 against $24.94).
- RESULTS, `tank_size.md`, `no_perfusion_downside.md` and TODO corrected; `tests/test_tank_size.py` checks perfusion is cheaper at
  the same size up to 100 m³.

## 2026-11-21 (second batch): Humbird's perfusion design reconciled, the least medium flow in a batch, thinner cultures in the design search, two new levers

**The open TODO items that could move the long-run cost.** Evidence: `research_notes/humbird_backtest.md` (items 11 and 12),
`research_notes/two_spargers_and_loop.md`, `research_notes/model_audit.md` (section 3f). Headline numbers, old → new (2025 dollars a
kilo of cells): Humbird's best estimate on the page $26.99 → $26.99; with the model's five additions $37.38 → $30.49; Humbird's
optimistic design $15.93 → $15.72; the all-favourable example $7.62 → $6.97; the low-lactate example $49.50 → $48.68; Published
cells $322.55 → $316.11; Published cells in perfusion (cautious) $185.59 → $181.13; the nutrient floor $2.00 → $2.00 ($2.0035 →
$1.9999).

- **Engine** (`floor_physics.explore`, mirrored in the page's `floorExplore`):
  1. Building power follows the floor and the class of each building (`building_power`; Humbird's Table 3.2 loads: Class 8 410
     W/m², sanitary 50, warehouse 5, Class 6 1,000; inputs `pi_w_*`, `pi_rate_class6`). It was his clean-room fed-batch plant's at
     every size and class. Closes half of his perfusion design's utilities gap (−54% → −27%).
  2. Part of the crew is counted per tank, as Humbird counts it (`crew_multiplier`; `pf_labour_tank_share` 0.619,
     `pf_labour_tank_perfusion` 0.975 staff a tank, `pf_labour_staff_fedbatch` 95). Nothing moves at 20 m³; small tanks need more
     staff per m³, large ones fewer. His perfusion design's labour closes like for like (−42% → 0%) with his own rest of the crew
     (`humbird_check.his_perfusion_crew_x`); the model's own 2.0 at 20 m³ stays.
  3. In a tank that is not washed out the least medium flow's cap is times `pf_batch_end_x`, as ammonia's and lactate's are, and
     counts towards the slower end of a batch. It capped Humbird's fed-batch at 92 g/L (+$6.4 on his design); it no longer binds it.
  4. Two levers, off by default: `spargers=2` (a fine-bubble sparger for oxygen: `ge_micro_o2_x` 4, `ge_micro_kill_x` 10,
     `ge_sparger2_k` $41k a tank; the share of gas through it searched on `MICRO_GRID`) and `col_on_loop` (the CO₂ column shares the
     filter loop's pump). The all-favourable example takes the second ($6.98 → $6.97), not the first.
  5. The floor's glucose is the mass balance's, 0.311 kg a kilo (`glucose_intensity`, was 0.32).
- **Design search**: `scenarios.design` (and `_design_traits`, `design_space.run`, the page's `scDesign`) runs a design whose CO₂
  loop fails at full density at the densest culture it passes (`thinned`, the choice's `thin`). The loop that feeds recycled oxygen
  now wins in every perfusion case: the low-lactate example 168 g/L ($49.22 → $48.68), the all-favourable example 219 g/L in a flat
  tank ($7.42 → $6.98), cautious $185.09 → $181.13.
- **Humbird back-test**: his perfusion design's growth factors are bought, like for like, only in his share of the litres (+62% →
  −4%); totals within 3.0%. The back-test tables are in 2025 dollars, not "today's".
- **Smaller**: `retention.duty` counts the litres a sorbent cleans as permeate (`filter_extra_l`); the dialyser's clearance
  (`mr_exchange_clearance`) checked against Fresenius's FX 80 table (278 mL/min at 300 mL/min over 1.8 m², 9.3 L/m²/h); `audit.py`
  draws put right (growth factors inside a complete medium, no price per litre on a floor medium, the tolerated waste, the bubble
  kill and the harvest recovery drawn: the low-lactate example's median $64.6 → $57.7, the all-favourable example's $11.4 → $8.2);
  the plant ladder's fill-and-draw rows are `explore()` itself (`plant_floor_hi` $17.7 → $20.3; the plant knob's range $13.8-34.0
  → $13.5-37.1; `plant_floor` $13.8 → $13.5, `plant_floor_lo` $8.76 → $8.50); METHODS no longer calls CO₂ tolerance the
  measurement that would move Humbird's optimistic design most (above 100 mbar oxygen binds; the gas flow tolerated moves it more).
- **Why the all-favourable example's point is below most of its draws** (95% now): its estimates sit at the modes of priors skewed
  to the costly side (protectant price and dose, bubble kill, amino-acid price, the plant estimate). Not a defect; said in its story.
- Tests repinned on purpose with the old values in dated comments; side-study notes' tables regenerated.
- **Documents after the batch** (2026-11-21): RESULTS.md's prose recomputed from the code outside the summary table (Humbird back-test,
  frontier, study comparison, cells-by-tank and gas-cap tables, vessels, reuse, fallback, plant axis, design search, regions, meat
  types; the species-cell and 50-mbar fish figures recomputed: US 1.2%, world 0.6%, fish cells $24.6); METHODS' tier table,
  tornado and frontier regenerated; scenario table rows and the protectant row repinned for its $5-100 band (`test_answer_rests_on`
  pin $46.74-54.12); "the reference case" renamed in the notes; judgement tables labelled as the model's rough judgement and dated
  (the odds appendix of `cell_trait_routes.md` deleted); owner-attributed comments in `inputs.py` reworded; `test_gas_exchange`
  and `test_plant_items` mark their `BEFORE_FILTER_LOOP` pins as history and pin current figures (`_check_current`). No value changed.

## 2026-11-20 and 2026-11-21

**The model batch from the full review, the back-test against Humbird's tables, one most favourable case checked against ten
published studies, four changes to the shopper side, and the page opening on Humbird's best estimate.** The final state is
described here; the evidence is in `research_notes/full_review_2026-11-19.md` (section 7), `humbird_backtest.md`,
`study_comparison.md`, `frontier.md`, `thick_culture.md`, `tank_size.md` and `closed_markets.md`. In brackets, what each change
adds to Published cells, the low-lactate example and the all-favourable example, undone alone in the final model.

- **Engine and inputs** (`floor_physics.explore`, `inputs.py`, `scenarios.py`):
  1. The scenarios' cells tolerate 35 mmol/L of lactate (`sc_lac_limit`, 20-50, drawn); Humbird's design keeps 50 (+$95.4; nothing; nothing).
  2. Bubble deaths are charged on the gas the cells meet: death share = `ge_kill_protected` × gas per litre / growth rate, drawn in
     the bands (+$3.2; +$4.0; +$0.4). A column that strips nothing no longer lowers them; the bubble cage is charged only on the
     gas its cells meet.
  3. A harvest loss, `pf_harvest_recovery` 0.98, on every cost and litre per kilo (+$6.5; +$1.0; +$0.2); a vessel's own recovery
     now scales every cost too.
  4. Membrane life `rt_membrane_life` 2,415 L/m², Humbird's replacement schedule at his price; it was 3,960 (nothing; +$8.7; nothing).
  5. Labour in a washed, continuous tank is the fed-batch crew × `pf_labour_perfusion_x` (2.0) (nothing; +$1.8; +$0.7).
  6. Medium-preparation capital scales with the medium passed (`pf_medium_prep_l_kg` 8.7, `pf_medium_prep_exp` 0.6) (nothing; +$1.7; +$0.3).
  7. A thick culture takes up oxygen more slowly (`viscous_kla`: kLa × (viscosity ratio)^−`tc_kla_exp`, 0.40, with `tc_thin`
     1.33); the low-lactate example runs at 154 g/L, not 191 (nothing; +$1.8; +$0.7).
  8. Plant items per tank (`floor_physics.tank_items`, `capex_at_size`): each tank brings its vessel, makeup tanks, filter housings
     and buildings, in Humbird's accounting (nothing; −$0.1; −$0.1). Larger tanks now save 5-7% (at about 90-170 m³).
  9. From the back-test: growth factors are his $3.13 over his fed-batch's 8.65 L/kg; utilities are four inputs (`pf_util_time`,
     `pf_util_run`, `pf_util_water`, `pf_util_kg`) in place of a flat $0.94; the crew per m³ uses his 14.2 t per m³.
  10. The ATF is priced as Humbird charges bought equipment (6.25 times its bare price): $66.6 in the low-lactate example, the
      dearest retention device. Defects fixed: `retention.duty` bleeds per kilo grown; `plant_items.cost_per_kg` uses
      `explore(items)`; `min_litres` made consistent; the airlift follows the stirred tank's mixing rule, and no longer beats it.
  11. `accept_x` is no longer drawn in the demand and timing bands. New levers, off by default: maturation (`mature_h`) and cleaning
      the medium (`clean` = exchanger, electrodialysis or dialysis; `wash_price`, `pf_wash_price` $0.066 a litre).
- **One most favourable case** (`scenarios.all_favourable`, `favourable_levers`): every lever at its most favourable value among
  this model's favourable end, Humbird's design and nine other published studies (`study_assumptions.py`), taking no study value
  that breaks a limit (nutrient floor, mass balance, 258 g/L, the engine's gas and waste limits, a 15-hour doubling, a 3 ng cell, a
  market rate of interest). It is the all-favourable example, $7.62 (it was $11.67 on 19 November under the old definition), in
  42 m³ tanks (Negulescu 2023); `frontier.ladder()` runs from Humbird's design ($15.95) to it. Risner 2021's scenario 4 ($2.46 in
  2025 dollars) is the one published estimate below it, and breaks four limits (a culture that fills the tank, an 8-hour doubling,
  45 g of glucose a kilo, a 5.3 ng cell); brought inside them its design costs $8.89. `plant_floor` 10.8 → 13.8, so `cost_floor`
  12.8 → 15.8.
- **Shopper side** (`market_share.py`, `meat_market.py`): plant-based meat's anchor is 0.4% of meat by volume (`pb_share_target`,
  was 1.2%); incomes are nominal GDP per head (`REGION_INCOME`, `income_ref` 86,170, `income_gradient` 0.32 re-solved, was PPP
  and 0.5); conventional meat's price falls as cultivated meat takes its sales (`conv_exponent`, (1 − share)^0.38); markets closed
  by law take none (`closed_share`, weighted by meat eaten: 1.14% of the world, 10.2% of the US). The share at equal price reads
  14.4% of meat buyers (13% of all choices, unchanged).
- **Back-test** (`humbird_check.py`): like for like the engine gives $20.65 against his $21.00 (2018 dollars) for his best
  estimate, $26.99 in 2025 dollars (capital by the plant-cost index ×1.33, the rest by consumer prices ×1.28), and is within 1.7%
  on his three designs with enhanced cells; his wild-type plants come out 10% high (their plant per m³). With the model's additions
  his design costs $36.2.
- **Headline figures** (at most likely values; middle draw; 8 in 10 of the draws): Published cells $322.6 ($347; $243–486), was
  $209.1; the low-lactate example $49.5 ($54; $41–79), share 0.05%, was $32.8 and 0.21%; the all-favourable example $7.6 ($9;
  $8–11), 22.6% with its own demand (58.6% of meat buyers) and 5.4% with the ordinary 14.4%; Humbird's optimistic design $15.9,
  was $12.8.
- **The page** opens on Humbird's best estimate as he counts it ($26.99 in 2025 dollars), with what this model counts and he does
  not as five levers and one button ($37.38 with all five); tank size, maturation and medium cleaning are levers; the interest
  rate, the years and the upkeep replace the single yearly charge; a worked calculation, a glossary and the published studies'
  values on each lever (`page_studies.js`) are added.
- **Documents** (2026-11-21): RESULTS.md, METHODS.md, README.md, TODO.md and the three retention notes rewritten to the final
  model; `tests/test_golden.py` repinned for the shopper-side changes.

## 2026-11-19

**Full review; the first screen by sections; no named cell types (no model number changed).**
- **Review** (`research_notes/full_review_2026-11-19.md`): five readers went through the 14 cost analyses, the two books and six
  papers, evidence from 2024-26, the shopper model and the retention study. Nothing overturns the answer. The perfusion cases are
  optimistic in six places not shown before (medium preparation sized for fed-batch, membrane life against Humbird's own, density
  2.3 times what companies report, bubble deaths not charged, labour, harvest loss), and lactate tolerance (50 mM) has no range
  though it decides the fed-batch cost ($209 at 50 mM, $298 at 35). The uncertainty band draws shoppers' acceptance twice
  (`accept_x` beside `equal_price_share`). No default changed: the note proposes one batch.
- **Names** (the author's decision): no named kinds of hypothetical cell anywhere. The two names introduced earlier today for the
  examples beside Published cells are gone from the page, its address, RESULTS, METHODS, README, TODO and the notes.
  Cells are described by their traits. Where a document needs an example set it is "the low-lactate example" (code key `central`)
  or "the all-favourable example" (`best`), each defined by its traits where it first appears.
- **The opening gives one figure only: the best the model can find, as a range** (the author: "I would not lead with any number
  except perhaps the best we can possibly do"): $2.0 a kilo of cells (the nutrients) to $7.2 (every lever at its known limit), with
  the shop price of two named meats beside it. Published cells are where the levers start, not a headline: companies say their own
  cells do better and have not published them. The reader's cost and share are a readout labelled "At your settings".
- **The levers are in a bar at the side** (as on the page of early November), in four groups (cells, reactor, medium, shoppers);
  the results are beside them and follow each lever. Under most levers are **reference values** someone has published
  (`build_interactive.LEVER_REFS`), each a button that sets the lever, and "What this is" with the model's source.
- **How the page was first rebuilt today, by sections with the settings above each result**: (1) the cells, then what they allow in the
  tank (density and what limits it, litres of medium a kilo and what sets them, output per m³); (2) the reactor and how it is run;
  (3) the medium; then what a kilo of cells costs; (4) the shoppers and the product; then how much meat it would replace. It opens
  on Published cells (the best published figure for each trait, fed-batch at 20 m³), not on a hypothetical set of cells.
- **Twenty more settings** in collapsible groups (`build_interactive.PAGE_PARAMS`, each with its source): the ammonia, lactate,
  salt strength and CO₂ the cells tolerate, the oxygen they use, the upkeep share, gas flow, least medium flow; the membranes'
  price, life and flux (in place of the one "filter cost a litre" slider), the yearly charge, kLa, labour, energy; the prices of
  amino acids and glucose, growth factors, the protectant's dose and price. A setting the reader sets leaves the 8-in-10 range.
- **The vessel, the way it is run and the retention device are choices on the first screen**: six vessels and five modes
  (`vessels.py`, already mirrored on the page) and nine retention devices (`retention.py`, now mirrored in `page_retention.js`;
  `floorExplore` gained `extra_opex`; `tests/run_parity.py` checks 36 device-cases), with two comparison tables at the reader's
  settings.
- **Shoppers.** A new chart for one kind of meat: the share of its buyers who pick the cultivated one against its price, which
  passes through the reader's setting at the same price (that is the setting's definition), with a mark for where each kind of meat
  sits at the reader's cost. The share map has a literal title ("Long-run share of the meat sold, for any cost of cells and any
  preference of shoppers") and no reference points on it, because a published cost says nothing about shoppers; published costs are
  ticks on the cost axis. Its "price parity" line is labelled "mince at the price of the average kilo", and the note says why the
  50% line does not pass through 50% there (37% with the world's mix of meats).
- **Two source texts corrected**: a protectant cuts bubble deaths about 20-fold at 1 g/L (Jöbses 1991, the model's own inputs), not
  "at least 100-fold"; Pasitka's 2024 abstract gives 130 million cells/mL at 43% w/v (3.3 ng, unchanged).
- **The cost shown is the cost at the settings shown** (the author: "should we remove that and just leave the point for
  simplicity?"). The first screen no longer leads with the median of draws and an "8 in 10" range. A section under the cost, "How
  uncertain is this cost", opens to the draws: the middle draw, the range that holds 8 in 10, and a table of every estimate varied
  with its lowest, most likely and highest value. RESULTS and METHODS still lead with the median for their examples (TODO).
- **Every meat price names its kind of meat** (the author: "different meats have different prices"). No "price parity" with an
  average kilo: the cost axis and the share map mark the cost at which it would sell at the shop price of the cheapest large kind,
  the most eaten kind of another animal, a steak and the dearest, each with its price; the sentence compares the shop price with
  two named meats; "everyday meat" is "US minced beef or pork cuts ($12 a kilo)" in the page and RESULTS.
- **Look**: white background in every colour scheme (the dark theme is removed), Computer Modern (CMU Serif from jsDelivr, falling
  back to Georgia), the earlier page's blue for values, and a summary bar that stays in view while a slider moves: the cost, the
  shop price against two named meats, and the long-run share.
- `tests/test_easy_view.py` rewritten for the sections: the order of the pieces, no retired names, each further setting finite at
  both ends and exact when freed, the vessel and device choices against their studies, and the same-price property.

**Page fixes from the author's list; no route claims anywhere (no model number changed).**
- **No route claims** (the author: "I would remove it"): the page, RESULTS, METHODS and README no longer say a trait has been shown
  by a feed change, selection, adaptation or engineering, or "in other cells", or "not together". Each trait carries only the best
  value measured in meat cells, with its source (`cell_traits.best_in_meat_cells`: ammonia 0.14 mol a kilo, Hubalek 2023; lactate
  1.05 per glucose, Pasitka 2024; doubling 15 h, Stout 2023; 3.3 ng, Pasitka 2024). "What it would take" picks, among the sets
  tried, the one with the fewest traits beyond those measurements (was: the lowest route rank), so two of its rows change their
  example set; the costs a share needs do not. The headline table's last column lists the traits beyond the measurements. The
  scenario tags `selection or adaptation` and `genetic engineering` became one neutral tag, `cells` (cells with other traits than
  those published). `cell_traits.routes_needed` and `research_notes/cell_trait_routes.md` stay as the record of the evidence.
- **First screen.** The cloud of dots is gone (cost line and map): the reader's point (the median, as before) with a thin 8-in-10
  whisker, "if the estimates you have not set vary", and a tooltip listing them. The 1% and 10% labels say the meat buyers they
  assume; labels that do not depend on that slider no longer move when it moves. The cost bar has a hue per group and a shade per
  item, named where they fit. Plant cost in dollars per m³ of tank, filter cost with the membrane life, medium price with its
  nutrient floor marked. The plant protein in a steak or fillet is a first-screen slider, and shares are given by weight of
  product and of cells. "Where it would sell" brings back the original bars by species and type of meat and the disk, with a toggle.
  Reference-point descriptions and ladder steps stand alone. Text spans the cards' width.

**Case names (2026-11-19, the author's decision):** "Central" is now **"Selected cells"** and "the best case" **"Engineered cells,
all favourable"**, in the model's texts, RESULTS, METHODS, README, TODO and the generated tables (code keys `central`, `best`
unchanged; research notes carry a glossary line). The page keeps the old names until it is rebuilt. The share at equal price is
introduced as a share of meat buyers (14.5%; 58.5% for Engineered cells, all favourable), with all choices (13%, 55%) second.

**Scenario restructure: cells as traits, what it would take, a ladder from fed-batch, and the mass balance of a batch**
(`floor_physics.py`, `scenarios.py`, `cell_traits.py`, `meat_market.py`, `market_share.py`, `inputs.py` `pf_batch_*` and `cr_*`, the
page's JS engine, the side studies; **defaults changed**)
- **Mass balance of a tank that is not washed out.** Its density is at most end factor x level allowed / waste made per kilo, with the
  same ammonia limit and lactate room as perfusion; a batch may end 1.3 times above the level (`pf_batch_end_x`, Humbird's own
  fed-batch design; range 1.0-2.0) and its last doublings above it grow slower (`pf_batch_half_x`). A chemostat is held to the level.
  Before, Humbird's 120 g/L was scaled by the waste. The Selected cells case's batch: 56 -> **37 g/L**, $44.13 -> **$64.90**; the
  published cells': 25 -> **14 g/L**, $113.56 -> **$209.05**; Humbird's design and the reference case's batch barely move.
- **A switch for how the tank is run**: perfusion at 20 m³, or fed-batch at 20, 50 or 100 m³ (fed-batch at 20 m³ is what has been
  shown for meat cells). A fed-batch plant with shared medium keeps Humbird's full seed train.
- **Cells as four traits** (ammonia per kilo, lactate per glucose, doubling time, cell mass), set directly (`scenarios.run(...,
  **traits)`, `scenario_mc(traits=...)`), with a table of the best level each route has shown (`cell_traits.py`, `cr_*`,
  `research_notes/cell_trait_routes.md`) and `routes_needed`, which says what a set of traits has been shown with and never that
  engineering is necessary. The headline table's last column is that verdict, in place of "the hardest thing it needs".
- **What it would take** (`scenarios.what_it_would_take`, deterministic): a 1% share needs cells at $19.7 a kilo at 14.5% of meat
  buyers ($29.8 at 50%), reached by traits each shown without engineering (some only in CHO); 10% needs $4.9 (none of the trait sets
  tried) or $12.9 at 50% (no ammonia and no lactate, shown so far only with engineering). It leads RESULTS.
- **The ladder** of reference points, seven rows labelled by what changes (medians; most likely values): Published cells in a 20 m³
  batch **$219** ($209.1; was $128 / $111.9 in perfusion); cheaper inputs **$210** ($201.4); less lactate and faster growth, still a
  batch **$67** ($64.9); perfusion = **Selected cells $36** ($32.8); shared-medium plant **$33** ($29.9); almost no ammonia or lactate
  **$24** ($17.3); Engineered cells, all favourable **$15** ($11.7). Keys kept; `today` and `process` now mean the batch rows, new keys
  `selected` and `engineered`; `cautious` keeps the published cells in perfusion.
- **A forecast for 2035 was built and dropped** the same day at the author's direction ("I like the idea of clouds, but I do not like
  the idea of forecasts"): no Monte Carlo over the switches; the odds are kept as a record in `cell_trait_routes.md`, unused.
- **The share is the share of the meat sold** (audit 6a): x / (x + c) for each product, in the point estimate, the
  roll-up's Monte Carlo, the side studies' roll-ups and the page's JS. Not yet in `uncertainty.py`, `sensitivity.py` and
  `adoption_timing.py`, which still report mince's share of all four choices (labelled so in RESULTS and METHODS; TODO). It was x, the share of all four choices: a flat market at 50% of meat buyers
  showed 46.5%, now 50.0%. Shares rose by about a quarter at the Selected cells case's cost (0.16% -> 0.21% at most likely values).
- **Every kind of cell weighs 2 ng** (`sc_mass_selected_pg`, 1-3 ng, drawn in the bands and in "what the answer rests on"); the
  engineered setting changes the metabolism only (it was Humbird's 3 ng; Humbird's design keeps it). Engineered cells, all favourable
  $11.46 -> $11.67.
- **The selected cells' ammonia**: a two-sided pass kept 0.14 mol a kilo (the one stirred measurement) and widened the low end from 0.07
  to 0.04, so it overlaps the engineered cells' 0.055 (`ammonia_tolerance_and_filter_life.md` section 10).
- **Plant-cost axis** (`scenarios.plant_axis`): with the mass balance, fed-batch at 20 m³ beats perfusion only if the plant costs under
  0.19 times its modelled cost with the Selected cells case's switches (0.28 with the shared-medium plant). The earlier symmetric
  comparison (about half) rested on the old 56 g/L cap.
- **Parity** is labelled as parity with a $12 kilo of everyday meat ($6.1 of cells); the world's volume-weighted $9.43 needs about
  $4.29 (US $10.93: $5.37; Europe $13.63: $7.31).
- **Upside Foods' 20 m³ process** (AgFunderNews, 17 Nov 2026) in `vessels_and_modes.md` section 11; fed-batch tank size in
  `tank_size.md` section 10. Side studies repinned (downside, vessels, tank size, design search on perfusion cases, medium reuse on
  `cautious`, industry claims, market-size loop, demand checks, liking spread, premium curve and buyers).

**Cell retention: aggregates and edible microcarriers** (`retention.py`, `research_notes/retention_aggregates.md`; defaults unchanged)
- Two membrane-free routes added to the retention study. Cells grown as 100-300 µm aggregates settle fast enough for a plain settler:
  Central $20.4 a kilo against $32.8 with the filter loop; oxygen does not limit aggregates under about 300 µm. Unshown: the densest
  aggregate culture is about 40 g/L for a week; about 8% by 2035 at Central's density. Edible microcarriers hold Central to 26 g/L
  ($84) because the beads fill the tank.

**Shoppers' liking: a Student's t spread, and an integration error found** (`market_share.py`, `inputs.py`,
`liking_spread.py --families`, `research_notes/liking_spread.md`; **defaults changed**)
- The normal spread of 5 utils fitted on 2026-11-18 was integrated on 15 points, too few for a spread that wide. Integrated properly it
  gives a first-contact elasticity of -1.34, not -1.53, and misses the choice experiment (0.29, not 0.15).
- A normal tail also falls too fast far above price parity: against sixteen premium real meats at 4 times the price (0.6%) it gave 0.1%,
  and against farmed salmon's history (1-1.5% more volume per 1% lower price) it gave 5.2-7.5.
- Now a Student's t spread, standard deviation **3.9 utils**, **4 degrees of freedom**, on a 67-point grid, fitted to the choice
  experiment and the premium meats together. Shares at 2, 3, 4 times the price: 3.3%, 1.0%, 0.35% (premium meats 3.7%, 1.5%, 0.6%);
  salmon response 3.6-3.7 (still fails, by half as much); first contact 4.3% of all choices, 4.8% of those who buy a meat (the
  experiment: 4% and 5%), so the 13% at equal price stays. At half the price of meat 24.5%; if free 41.5%.
- Compared and not chosen: logistic (helps little), a two-group mixture (fits best, but with two parameters on a ridge and a block of
  shoppers who ignore price).
- Shares: Central 0.08% -> **0.16%** at the most-likely-values cost, median **0.11%** (0.02-0.6%); best case 20% -> **13.8%**, median
  **6.8%** (2.5-14.8%), 2.7% with Central's demand; forecast median 0.07% -> 0.2%. The best case fell because the fitted spread is
  narrower in the middle, which no data pin. Years to nine-tenths of the long-run share at the reported cost: 28 -> 21.

**The page rebuilt** (`build_interactive.py`, `page_scenarios.js`; spec and review in the audit note)
- One page, one case selector (Published cells, Central case, Best case, Your own settings), no short and detailed modes.
- First screen: one generated sentence, three numbers (cost, shop price, long-run share: medians with their ranges), and one chart of
  long-run share against the cost of cells, shaded by the share of shoppers who would choose it at equal price.
- Six levels that open in place: what each case assumes (with a ladder), what would move it most (switches, unmeasured estimates and
  shopper judgements in one ranking), where and when, check the engineering, check the shopper model, method and sources.
- One link style; the reviewer's text errors fixed; no build stamp.

**The audit before sending: one batch of fixes** (`research_notes/audit_2026-11-19.md`; four reviewers with no prior context read
the cost side, the demand side, the page and the literature on shoppers' choices; **defaults changed**)

Cost of cells:
- Ammonia the cells tolerate: 5 -> **4 mmol/L** in every scenario (`sc_nh3_limit`, 2-8), the evidence note's own median. Humbird's
  optimistic design keeps his 5.
- A lost run throws its filter membranes away early; they were charged for a full run (`floor_physics.explore`, `retention.sizing`).
- Glucose from the cells' own balance (`floor_physics.glucose_balance`; lactate yields are now per mol of all glucose taken up). The
  published cells, which ferment most of their glucose, need about 4.5 mol a kilo, not the 0.84 they were given (which could not supply
  their own oxygen use), so lactate sets their medium: about 95 litres a kilo, not 28. Reported runs use 140-230.
- A tank that is not perfused is capped by lactate as well as ammonia.
- "What the answer rests on" could not see scenario settings (they are read when `scenarios.py` is imported); it reloads now. The
  ammonia the selected cells make (measured once; $23.5-52.1 across its range) is the third-largest estimate and is drawn in the bands.
- Costs at the most likely value of every estimate: published cells $57.0 -> **$111.9**; process changes $27.7 -> $76.7; Central
  $26.4 -> **$32.8**; shared-medium plant $23.6 -> $29.9; best case $10.0 -> **$11.5**; forecast $23.2 -> $28.8; Humbird's optimistic
  design $12.8 (unchanged). The largest step on the ladder is now selecting cells that make less lactate.

Demand:
- World seafood re-priced by who eats the fish (`research_notes/world_seafood_prices.md`): a mass market near $7 a kilo edible and a
  premium tier (salmon, shrimp, tuna) near $20, in place of one "fillet" row at $16 for 64% of seafood. China's fillet row $14 -> $9,
  the EU's $28 -> $21, India's $8 -> $6.
- The tier rule is gone. It made cuts and premium products less sensitive to price, which raised cultivated meat's share whenever
  it was the dearer product, and flipped a product to "premium" at 2.5 times its species' cheapest form. Now: mince has no offset; a
  cut carries a penalty for the part that is not cells (its cell share times the model's real-meat credit: 0.45 utils at 80% cells);
  premium products carry a further offset that rises smoothly from 2 to 4 times the cheapest form.
- The share at equal price is drawn around its own 13% setting (lognormal, 5th-95th about 3-52%), not from a triangle whose median
  was 21%. A cut's cell share (50-90%) and assembly cost ($0.5-7) are drawn too.
- Shares of world meat and seafood: Central 0.53% -> **0.08%** at the most-likely-values cost, **0.04%** median (under 0.001-0.7%);
  best case 30% -> **20%**, 11% median (4-23%), 2.8% with Central's demand; forecast 0.8% -> 0.07% median.
- Cost of the removal: the model now responds to price more strongly than farmed salmon's history and premium meats' slope far above
  parity (two of four demand checks fail; three passed). The premium-meat anchoring still agrees at Central (0.10% against 0.08%).

Presentation:
- The scenario table leads with the median of the draws; the cost with every estimate at its most likely value is second. The best
  case's point ($11.5) sat below the 10th percentile of its own draws.
- The first case is **"Published cells"**: the best meat cells in the published record. Companies may hold better ones.
- RESULTS and METHODS rewritten against the new figures; names unified; "share" defined once.

**What a cut costs: cells bound with plant protein, assembled after harvest** (`price_ratio.structured_cost`, `inputs.py`,
`meat_market.py`, `uncertainty.py`, `scaffolding.py`, the page's `cutCost` and a new slider; `research_notes/structuring_cost.md`;
**defaults changed**)
- A cut was charged a full kilo of cells plus a $6 scaffold, so the 0.2 kg of scaffold sat on top of the cells it replaces. Now a
  kilo of cut is 0.8 kg of cells (range 0.5-0.9), 0.2 kg of plant-protein matrix and binder at $2 a kilo (1-5), and $2 to assemble
  it (0.5-7) beyond the $1 of forming and packing every product already pays in the shop add-on. Evidence: Wildtype (FDA memo, 2025), Aleph Farms (2025) and Upside (2026) dropped growing tissue on a scaffold for binding
  harvested cells with plant protein; assembly is costed from plant-protein extrusion (GFI 2021), surimi forming and binder prices.
  Growing tissue on a scaffold would add about $10 a kilo (3-35). The cell share is the larger unknown: cuts sold so far are 10-30%
  cells. Above about $12 a kilo of cells a cut now costs less than mince.
- The page: slider c (share of a cut that is cells) beside k (now the assembly cost, $2).
- Shares: Central 0.13% -> **0.53%** of world meat (median 0.55%, 0.07-2.8%); best case 21.4% -> **30.1%** (median 18.3%, 9.2-30.4%;
  5.0% with Central's demand); forecast 0.2% -> **0.8%** (median); Humbird's optimistic design median 1.3% -> 3.2%. Steaks and fish
  fillets carry the gain. Sushi-grade salmon: median price ratio 1.57 -> 1.08. Side studies repinned (notes carry a dated line).

**The medium: growth factors inside announced prices, the nutrient floor from GFI, simpler settings** (`inputs.py`, `scenarios.py`,
`floor_physics.py`, `research_notes/nutrient_floor.md` §6, `research_notes/growth_factors_in_medium_price.md`; **defaults changed**)
- Growth factors: announced and reported medium prices ($0.20, $0.30, $0.50 a litre) are complete media with growth factors inside
  (about 0.85 likely); `sc_medium_complete` is on. A complete medium cannot cost less than the nutrients plus its growth factors
  (`explore(gf_in_medium=...)`; found while repinning: without it, a culture under about 20 litres a kilo got its growth factors free).
- The nutrient floor: $1.70 -> **$2.00** a kilo of cells (Pablo, following GFI). Amino acids 232 g at $6.36 a kilo (GFI December 2025,
  feed grade, the most efficient need) in place of soy hydrolysate, which cannot supply glutamine, arginine, asparagine, cystine
  or serine; other nutrients $0.40 (was $0.90, assumed). The amino-acid price is drawn in the scenarios' bands ($5.0-11.6).
- The medium switch: $0.05 and $0.15 a litre dropped; new setting "at the nutrient floor" (growth factors bought on top). The best case
  takes it; the forecast takes $0.20.
- Costs: Central $29.42 -> **$26.43** (0.13% of world meat at the point cost, median 0.14%); best case $9.66 -> **$9.96** (21.4%,
  median 11.5%; 2.7% with Central's demand); rung 4 $26.56 -> $23.57; today $62.96 -> $56.99; forecast $24.80 -> $23.24; Humbird's
  optimistic design $12.51 -> $12.81.
- What changed in the side studies: the best case no longer reaches parity by learning ($6.49 against $6.14; was $6.17); Central's
  resting point is $15.83 and 0.86%. Cleaning the permeate is worth $0.5-1.7 a kilo in Central (was $2-4), because a litre saved no
  longer saves bought growth factors. The physical frontier is $7.16 (was $6.86), about $1 above parity. Every cost study repinned
  (notes carry a dated line). Parity was quoted as "$7" in places; it is $6.1 under the shelf rule.

**The best case takes the favourable end of demand too** (`inputs.best_equal_price_share`, `scenarios.py`; **default changed for the
best case only**)
- Pablo: "best" should mean the favourable end of every uncertain input, and demand is one of them; the precedents for distrusted
  foods (irradiation, margarine, modified crops) all competed with a natural product, while cultivated meat's competitor is
  factory-farmed meat.
- The best case now takes 55% at equal price once familiar (shoppers slightly favour it), drawn 35–70% in its band; every other
  row keeps 13%. Best case: **22.2%** of world meat at the point cost (was 2.9%), median of draws **11.5%** (3.7–23.5%; was 2.1%),
  US 29%, Europe 35%. At its cost with Central's demand it is still 2.9%; at 55%, Central would take 1.4%.
- Side studies (premium curve, premium buyers, market-size loop, demand checks, liking spread, what the answer rests on) stay at
  Central's demand; RESULTS now says "at the best case's cost" where they quote it.
- METHODS: conventional meat's price response re-bounded for the new best case (it takes about 40% of beef buyers): a tenth to an
  eighth off its share (22.2% → 19–21%).
- Page: choosing a scenario sets the demand slider to that scenario's value; the slider now runs to 80%; the short version has
  its own slider for the share at equal price, and shows the band only at the case's own demand setting.

## 2026-11-18

**Shoppers differ in how much they like cultivated meat: now the default** (`market_share.py`, `liking_spread.py`,
`research_notes/liking_spread.md`; **defaults changed**)
- The shopper model has a normal spread of liking for cultivated meat across shoppers (`liking_sd` 5 utils, fifteen integration
  points), fitted to the one choice experiment that estimated shoppers one by one. Its mean is set so that the share at equal price,
  once cultivated meat is familiar, is a new visible setting, `equal_price_share`: **13%** (5% at first contact, as measured; 49% if
  the average shopper ends up indifferent). The calibration (price coefficient, solved weights, plant-based share) is unchanged.
- The bands draw `equal_price_share` (triangular 5/13/49%, median about 19%) and no longer draw the no-killing value, first-contact
  wariness or the health dial, which were parts of the same thing. Taste acceptance is still drawn.
- The model now passes three of four price-response checks (first contact -1.53 against about -1.5; farmed salmon; three times the
  share at a third of the premium). Plant-based meat's elasticity still fails (-2.85 against about -1.3; TODO).
- Central: **0.08%** of world meat at the point cost (was 0.04%), median 0.1% (80% of draws 0.01–0.8%). Best case: **2.9%** (was
  3.1%), median 2.1% (0.4–7.6%; was 0.5%). Forecast for 2035: median 0.2% (0.02–1.4%). Market-size loop: Central $19.35 and 0.45%,
  best case $6.17 and 5.69%. Animals spared per tonne in the reference case: about 80 (was 17).
- Page: the spread is mirrored in the page's JavaScript (parity test passes) and the setting is a slider.

Market tables: China, the low-income regions and seafood's weight (`meat_market.py`, `research_notes/premium_market_sizes.md` §6)
- China's sushi-grade seafood row 4% → 0.8%, wagyu 0.5% → 0.1%, heritage pork 0.5% → 1.5% (black pigs); Brazil's picanha/prime 2% →
  0.5%; India's premium chicken 1% → 0.1%; Nigeria's premium goat 1% → 0.2%.
- Seafood is about a quarter of the world's meat plus seafood by edible weight; the Global table had it at 9% and now has 24%.
  `ms_world_meat` (the market-size study's total) is meat plus seafood, 336 Mt.

Smaller fixes
- `sc_glc_measured` re-derived: the central 0.84 rests on CHO data, not Pasitka; range 0.67–3.6 (was narrower). It moves today's
  cells, not Central.
- `meat_market.species_market` crashed when the cost case already set the cells (a keyword passed twice); the species' cells now replace the case's.
- Growth factors in the medium price: about 0.85 that announced prices include them (`research_notes/growth_factors_in_medium_price.md`).
  The rule is in the code behind `sc_medium_complete`, **off**; turning it on (Central $29.42 → $26.43) is the next change.
- METHODS: a bound on joint products (displacing prime cuts makes the herd smaller, so the rest of the carcass is dearer, not
  cheaper; the effect is 10–20% at best and not modelled) and a check of adoption speed against history (the model's hundredfold
  rise over 17 years is at the fast end of 15–30 years, with no stall).

Shoppers differ in how much they like cultivated meat: evidence, a corrected check and a side study (`liking_spread.py`,
`research_notes/demand_heterogeneity_evidence.md`, `research_notes/liking_spread.md`; **no default changed**)
- Three reading passes on how shoppers differ. (1) The choice experiment the model was set against reports no elasticity: the
  "-0.84 to -3.4" the model's check uses is a formula on two of its coefficients; its fitted model simulates to about -1.5 at equal
  price, half the model's -3.27. So the model fails all four price-response checks, not three. (2) In the two studies that split
  shoppers into groups, cultivated-meat enthusiasts (13-16%) are not price-insensitive, and the price-insensitive organic buyers are
  the most hostile to it. (3) Plant-based meat's -1.23 is an item-level figure for plant-based beef; the category is about -1.3 to
  -1.5, and 7% of households make 82% of its spending.
- A premium-buyer recalibration built earlier the same day (branch `claude/recalibrate-demand`) was **not merged**: it rested on
  organic buyers being cultivated meat's price-insensitive buyers.
- `liking_spread.py`: a normal spread of liking for cultivated meat across shoppers (5 utils, each shopper as price-sensitive as
  now) reproduces the experiment's price response at four prices (miss 0.15 against 2.56). With it, the fading of first-contact
  wariness takes cultivated meat to 13% at equal price, not half; half is a premise. Across the three readings of the long run
  Central's share is 0.02% to 1.0% and the best case's 0.7% to 17.3%.
- `demand_checks.py`: the fourth check now uses the simulated -1.5.

The model's response to price checked against four measurements (`demand_checks.py`, `research_notes/demand_checks.md`; **no
default changed**)
- Prompted by Knowles 2026 on plant-based meat's prices. Plant-based meat's own-price elasticity is -1.23 in US retail data
  (GFI, as cited); the model's is -2.85. Sixteen premium meats fit a price sensitivity of 2.2 times meat's against the model's
  8.5. Farmed salmon responded 1.0–1.5% per 1% of price against the model's 3.0–3.4% for premium beef and seafood. Only the one
  choice experiment the model was set to agrees with it. So the model is probably two to four times too price-sensitive.
- Across the price responses the measurements point to, Central's share runs from 0.04% to 1.9%: the demand side is now the model's
  widest uncertainty. The curve that passes all four checks (slope and level from the premium meats) gives Central 0.1% and the
  best case 1.8%. Moving the default to it is the next step (TODO).
- Also: a plant that sells 60% of its capacity makes Central's cells cost $35.38, not $29.42 (`market_size_loop.underused`);
  plant-based meat at price parity would change cultivated meat's share by under 3%.

The page opens on a short version (`build_interactive.py`, `page_scenarios.js`; no number changed)
- Pablo: the page can overwhelm a new reader. It now opens on a short version: pick one of three cases (today's cells, Central, the best
  case) and see three numbers (cost to grow a kilo, shop price against everyday meat, long-run share of the world's meat), a plain
  description of the case, and where the cost goes. Every long section is folded under its heading with a one-line summary and opens on
  a click; "Everything" shows the page as before. The choice is remembered in the browser. At phone width the page opens about 2,600
  pixels tall, against about 29,000.
- The short version computes nothing of its own: the numbers come from the same functions as the full page (`tests/test_easy_view.py`).
The premium markets sized from data, and the checks on the market-size loop (`meat_market.py`, `research_notes/premium_market_sizes.md`,
`market_size_loop.py`; **defaults changed**)
- Pablo asked for the loop study's checks to be done and its unknowns found. The first check found a fault in the main model: the
  premium rows of the market tables were unsourced and several times too large. Sushi-grade seafood is about 1.2 Mt a year in the world
  (the Global table had 5.4), prime or wagyu beef at $45 or more about 0.5 Mt (1.35), heritage pork and organic chicken about 0.4 Mt
  each (1.35 each). The Global, US and Europe rows were resized; what was removed went to the same species' cut row. China and the
  low-income tables were not checked.
- **Central's long-run share falls from 0.16% to 0.04% of world meat** at its point cost (median 0.02%, was 0.1%), because nearly all
  its sales were to those rows. The best case moves from 3.7% to 3.1% (median 0.5%, was 0.8%); the US at Central from 0.35% to 0.21%.
  Costs are unchanged. Shares under 0.1% are now printed with two decimals in the tables and on the page.
- Anchored on premium real meats, Central is 0.14%: the earlier agreement with the model (0.16% each) was a coincidence of the oversized
  rows. With premium buyers, Central is 0.17% (0.38% with a strong no-killing value).
- The loop study, revised: with real premium markets Central's sales need 0.64 million m² of membrane a year, short of the million
  taken to bring a food-grade supplier, so Central has two resting points ($28.81, or $20.52 and 0.14% if the cheap membrane exists
  anyway). The best case still reaches parity ($6.11, 10.91%). The food-grade membrane's first price is now $150 a m² (was $250) and
  its floor $50 (was $60), from the prices of water and dairy modules; no steam-tolerant food-grade price is published.
- Other checks, recorded in the note: hollow fibres have held 27–35% animal cells by volume for over two weeks at 4 L (nothing for a
  month above bench scale); the model's premium products respond to price two to three times more strongly than farmed salmon did
  along its demand curve; a hundred-fold scale-up took such industries 15–30 years when it happened.

Cost falling as the market grows, solved with the share (`market_size_loop.py`, `research_notes/market_size_loop.md`; **no default
changed**)
- Pablo's idea: membranes and reactors get cheaper with market size, and the loop starts in premium products that cultivated meat
  comes to undercut. The membrane ($1,450 a m², a pharma price) switches to a food-grade supplier at $250 once demand passes a million
  m² a year, then falls 18% a doubling to $60; the plant falls 10% for each doubling of installed animal-cell tanks, to a microbial
  plant with what animal cells need. Seven new inputs (`ms_*`), used only here.
- Resting points: Central $19.86 and 0.45% of world meat (from $29.42, 0.16%); the best case $6.16 and 11.26% (from $9.66,
  3.69%), which is parity. Today's cells are stuck. Without a food-grade membrane supplier little moves.
- At Central's cost 99% of sales are premium products (sushi-grade seafood, prime beef); their volume alone crosses the membrane
  switch in the central case, not with slow learning, where Central has two resting points.

Cultivated meat as an even more premium meat, competing with welfare labels (`premium_buyers.py`, `research_notes/premium_buyers.md`;
**no default changed**)
- Pablo's idea: shoppers may see cultivated meat as a step above organic or free-range, but it then competes with those labels for the
  same shoppers. Adds a premium class of shoppers (10%, from household panel and survey data; range 5–20%) fitted to the sixteen
  premium products, and a welfare label at 2× on every non-premium shelf, competing with cultivated meat in one logit.
- Central's long-run share 0.29% (main model 0.16%); 0.51% if premium buyers value no killing at a whole extra meat price. Best case 4.61%
  (3.69%). The label on the shelf costs cultivated meat little (0.33% without it). It takes 11–16% of its sales from the label under the
  logit's proportional assumption, up to about half if the two are close substitutes.
- Caveat: the premium class's low price sensitivity is a fit across products; scanner data find organic meat demand more price-elastic.

The shelf price is now per-kg costs plus the shop's percentage margin (`retail_spreads.py`, `research_notes/retail_markup_form.md`)
- Question (Pablo, after Gemini argued the markup should be multiplicative): is the step from a kilo of cells to the shelf a fixed
  $/kg or a percentage? Neither alone. USDA ERS monthly meat prices (1970–2025) show shop prices moving about dollar for dollar with
  wholesale prices over one to five years (beef 0.99–1.17, pork 0.77–0.92, broilers 0.78–0.84), far from the 1.7–2.5 a pure
  percentage would give. But shops set a percentage gross margin (US meat departments 28–32%), which a new, permanently dearer
  product would carry in dollars.
- New rule: shelf = (cost + `markup_add`) / (1 − `retail_margin`), with `markup_add` $2.5/kg (was a flat $5; range $1.5–3.5, was
  $3–8.7) and the new `retail_margin` 28% (15–40%). Fitted to USDA's 2025 spreads at 28%, the per-kg part is $1.6 for broilers and
  $2.9 for beef; the $2.5 adds about $1 for forming cells into a product. Both are drawn in every uncertainty band. One function,
  `price_ratio.shelf_price`, carries the rule in Python, `shelfPrice` on the page; the page gains a shop-margin slider (0 and $5
  give the old flat rule).
- What moved: parity needs cells at $6.14 (was $7.00). Shelf prices of anything above parity rise: Central $44 (was $34), best case
  $16.9 (was $14.7). Long-run share of world meat at the point cost: Central 0.16% (was 0.41%), best case 3.7% (was 8.0%); medians
  of the bands: Central 0.1%, best case 0.8% (0.2–3.4%, was 1.9%). The demand calibration is unchanged (its anchor price is
  frozen). The premium-meat anchoring now gives Central 0.16% (agrees with the model) and the best case 1.8% against the model's
  3.7%. Costs per kg of cells are unchanged.
- Gemini's further claim that margins rise with the quality tier is unsourced, and the one comparison found (French Label Rouge
  chicken 25% against a standard fillet 36%) runs the other way; the 40% end of the range covers a slow-selling niche product.

## 2026-11-17

Pasitka 2024: the mass-basis finding worked through (METHODS and comments only; no number moved)
- The paper's own figures for the mass of a cell disagree: 0.55 ng (10 μm, Extended Data Fig. 4b), 3.3 ng (130 × 10⁶ cells per ml =
  43% w/v) and 9.8 ng (1.7 kg from 173 × 10⁹ cells). Worked through from its figures, the most likely explanation (about 70%) is that the
  cells are 10 μm as reported and both mass figures are counts times a fixed cells-per-gram factor, not weights of cells: the
  micrographs show 9–11 μm cells against their scale bar; the counts match density times harvested volume; 1.7 kg cannot be a pellet from
  about 8 L of culture holding 90 mL of cells; the 2023 paper's "36% w/v" at 108 × 10⁶ has the same ratio as the 43%; and the glucose
  burned could not build 1.7 kg of cells (it fits 0.3–0.65 kg for cells like the model's, the one piece that leans above 95 g). So about 95 g of cells in the 1.7 kg, as METHODS first said, now with the reasoning and the
  odds. A bound that does not depend on cell size (81 g of amino acids per kg of biomass) gives at least 2.5.
- Knock-on recorded in TODO: `sc_glc_measured` draws partly on the paper's per-kg-of-biomass glucose figure.
- Dropped as evidence: Supplementary Table S5's two nutrient costs differing by exactly 100 (more likely a units artefact than "1% protein").
- The decision to drop the paper as the anchor stands: its medium use and plant output scale from the same 10 ng, and even at 3 times
  too wet its $23–26 per kg of wet biomass is $70 or more per kg of cells before capital. The back-test row in METHODS now gives both
  readings (density 72 or 240 g/L against 430 claimed).

Cultivated meat anchored on premium real meats (`premium_curve.py`, `research_notes/premium_curve.md`; **no default changed**)
- Pablo's idea: premium real meats are "real meat plus a virtue, at a premium"; fit the curve they trace and place cultivated meat on it,
  corrected for what differs (no killing, novelty, unnatural).
- Data: ten more premium/share pairs up to 3.6× (`research_notes/high_premium_analogues_data.md`: US eggs by label, organic and
  Label Rouge chicken in France, Britain, Denmark and Switzerland, Austrian organic eggs, Ibérico as a sensitivity). Share falls with
  the premium in every within-source comparison, but far more slowly than the model's curve, which misses the sixteen products by a
  factor of about 6; a fitted curve (shoppers a quarter as price-sensitive, held to the measured at-parity elasticity) misses by 2.4.
  No sign of a loyal niche paying whatever the premium.
- Corrections (`research_notes/cultivated_vs_welfare_meat_evidence.md`, hypothetical studies): no killing +5% of meat's price, novelty
  −30% (half fades), unnatural −20% (likely persists).
- Result: Central 0.40% of world meat in the long run (0.18–0.63%) against the model's 0.41%, an independent check that passes. The best
  case 2.5% (1.2–3.9%) against 8.0%: near parity the two disagree, and the premium data do not reach there.
- `market_share.share(..., slaughter_free_x=1.0)`: an optional switch so a product can be real meat without counting as slaughter-free;
  the default is unchanged. `tests/test_premium_curve.py`, in `run_tests.sh`. RESULTS has a paragraph, and its old line about a
  small group paying whatever the premium is corrected.

## 2026-11-16

Page: where the cost goes (`page_scenarios.js`, `scPartsSVG`; no number moved)
- Under the scenario result, a bar of the cost of a kilo of cells split into six parts (medium, growth factors, bubble protectant,
  filter membranes, running the plant, the plant's capital charge), drawn in dollars so it shrinks as the switches lower the cost,
  each part labelled in dollars and share where it fits. A bracket marks the four parts that scale with the litres of medium;
  ticks mark parity and Central. A list gives each part's dollars, share and change against Central (against the best case when
  Central is chosen). Colours follow the repo's figures and pass a colour-blind check.

Wider bands, and a flaw in the demand model fixed (**headline bands move; no point cost moves**)
- **Bands** (`scenarios.MC_ESTIMATES`, switch `sc_wide_bands`): the scenarios' cost bands now also draw the estimates the cost rests on
  most, each from its own prior: the ammonia the cells tolerate, the protectant's price and dose, the least medium flow, antifoam's cost
  to oxygen transfer and the membrane price. Not drawn: glucose use (a cell trait, held by the switch), salt tolerance (no effect on
  the median, forty times slower), gas flow (a switch).
  - Central $27–38 → **$25–47**, median share 0.2% (unchanged); best case $9–12 → **$10–19**, median share 3.8% → **1.9%**;
    Humbird's design 2.4% → 1.3%. The best case's point cost now sits at about the 4th percentile of its draws.
  - `pf_protectant_price` range 10–260 → **10–120** $/kg: at the catalogue price as the top, the draws' median tonne price was $87.
- **Demand flaw**: `_derive_beta` splits price sensitivity between a dollar channel (income-scaled) and a ratio channel and pins their
  sum at one anchor. Loss aversion above about 1.6 drove the dollar coefficient positive (paying more raised utility), which made
  Central's share rise with loss aversion (0.4% → 1.4%). The coefficient is now capped at zero, in Python and on the page; inert at the
  defaults. The remaining sensitivity to how price splits between dollars and ratios (0.3–0.7%) is recorded as open.
- `answer_rests_on.py`: the band column follows the new draws; the gas-velocity row is left out with the reason (it only rescales
  Humbird's oxygen reference). RESULTS prose, the scenario tables in RESULTS, METHODS and `cost_scenarios.md` updated.

Consolidation: what the answer rests on, and every side study on the current model (`answer_rests_on.py`; **no scenario moves**)
- **What the answer rests on** (`answer_rests_on.py`, a section near the top of RESULTS): every input with a range is moved to
  each end, one at a time. Of 513 inputs (237 with a range), 14 move Central's or the best case's cost by $1 or more and 8 move
  Central by more than $3. The four largest (the ammonia the cells tolerate, the cell filter's life, the protectant's price, the
  least medium flow) have not been measured on meat cells. 11 of the 14 are not in the scenarios' uncertainty bands, so Central's
  band ($27–38) is too narrow. On the demand side, no single input takes the share at Central's cost outside 0.1–1.4%; at the
  best case's cost the same inputs span 1.5–15.6%. `tests/test_answer_rests_on.py`.
- **RESULTS summary**: the revision history at its top is replaced by a four-sentence answer (the history is in this file).
  The bands paragraph says which large inputs the bands leave out. The disc-stack sentence now gives its cost ($26.85 in Central).
- **The seven side studies that ran on a snapshot of an older model now run on the current one** (`tests/_snapshot.py` removed):
  tank size, thick culture, without perfusion, cell retention, nutrient floor, growth-factor and doubling bounds, the least medium
  per kg. Tests re-pinned, notes' tables and prose recomputed. What changed in their conclusions:
  - tank size: 20 m³ is within 0.5–1.8% of the cheapest size (was 0.5%), except the cautious case, 4.6% at 111 m³;
  - thick culture: only the best case reaches 258 g/L; in Central oxygen with the culture's viscosity binds first (151 g/L), so a
    thicker-culture limit is worth nothing there;
  - doubling bounds: "past 16 hours, speed adds little" no longer holds for Central (16 → 8 h saves $3.1), because oxygen now
    limits the density of fast cells;
  - cell retention: Central's filter duty is 8 times the reference's (was 12); the cautious case can no longer run all three tank
    tricks at 180 g/L;
  - without perfusion, the nutrient floor and the least medium per kg: levels move, conclusions hold.
  Probabilities in these notes were judged on the older model and not judged again; the notes say so where it matters.
- Stale quotes fixed in the frontier, audit, design-tricks and TODO notes, the dialyser input's note and the centrifuge text.

The medium cannot be less than the culture that leaves with the cells (`explore`, a medium term "harvest"; **no scenario moves, four side figures do**)
- Cells in suspension are harvested with 1000 / density litres of culture per kg. `explore` let the medium fall below that in thin
  cultures of low-waste cells. It is now a term of the medium balance, in Python and on the page (shown as a bar in the lever
  panel), and a medium figure set by hand is raised to it. Cells on a support are exempt.
- No scenario or tier moved. What did, all thin cultures:
  - the airlift in perfusion: $14.78 → $15.07 in the reference case ($79.17 → $81.94 with today's cells), at 79 g/L;
  - the tank-size study's reference at 100 and 200 m³: $14.59 → $15.02 and $17.30 → $18.29 (its note had said the reference was
    low there by exactly these amounts);
  - the gas-exchange study's cheapest design at 1 mm/s: $17.18 → $17.57;
  - the frontier: $6.85 → **$6.86**, with the steps after "cells double in 16 hours" up by $0.36 (faster cells run thinner);
  - the design search's "medium at the least the physics allows" for today's cells: saves $6.2, not $14.8, because 21.6 litres
    leave with each kg at 46 g/L.

Page: two fixes Pablo asked for
- **"Cost against the price of medium":** labels overlapped and rung 1 ($63) was off the top. The scenarios and the parity line
  are now named in a column at the right, spaced apart, with the axis reaching the dearest scenario.
- **"Selected on a low-waste feed" and "the best meat cells measured" cost the same** in every scenario: they differ only in
  lactate, and ammonia sets the litres of medium for both. Both options now say so. Rung 3's gain over rung 2 ($30.73 → $29.42)
  comes from faster growth (43 → 36 h), not from less waste.
- **Rung 3 renamed** "3. Plus cells selected to grow faster on the low-waste feed (Central)" (was "selected for low waste"); its
  story and the prose in RESULTS and on the page say where its $1.3 comes from. The figure's label column widens to fit.

Cleaning and reusing the medium (`medium_reuse.py`, `research_notes/medium_reuse.md`; one lever corrected, no scenario moved)
- Question: can the ammonia be taken out and the liquid reused (project G)? Method: a liquid balance per kg of cells (fresh medium
  bought, litres cleaned and returned, litres through the cell filter), priced with `explore`, for an ammonium exchanger,
  electrodialysis, dialysis with a thrown-away or a cleaned dialysate, and dialysis across the culture; each route cleans the litres
  that cost least. New inputs `mr_*`, each with its source and range.
- Finding: the liquid a device on the permeate cleans has passed the cell filter either way, and the filter is $0.38 of the $0.75 a
  litre costs in Central. So permeate-side reuse saves $2–4 a kilo (limit $7.3); dialysis across the culture saves $4.4–8.5
  (limit $14.8) if its membrane holds up, which nobody has shown. The evidence is one cited report, one bench study and patent claims.
- **Correction:** `explore`'s `sorbent` lever lowered the litres through the cell filter along with the fresh medium. It no longer
  does (Python and page). No scenario uses the lever; golden figures unchanged. A sorbent taking half the ammonia takes Central to
  $28.22, not $22.97; the best share (42%) gives $27.01.
- `tests/test_medium_reuse.py`, in `run_tests.sh`. RESULTS has a section; METHODS' lever table and the page's sorbent note say the
  filter is not saved.

Every scenario holds dissolved oxygen at half of air saturation (`scenarios.always`, `sc_do_setpoint`; **numbers move, down**)
- Humbird's oxygen transfer implies a tank held at 0.28 mmol/L (130% of air saturation). Pharma holds 30-50%. The scenarios now hold
  0.10 mmol/L (about 47%), which widens the oxygen driving force and needs nothing new. Found by `design_space.py`. Humbird's optimistic
  design keeps his level. Switch `sc_do_scenarios` = 0 restores the earlier figures; the side studies' snapshot tests use it.
- Scenarios (designs chosen again): rung 2 $31.33 → $30.73, Central $29.92 → **$29.42** (191 g/L, oxygen), with shared medium $26.81 →
  $26.56, best case $9.71 → **$9.66** (now at the thickness limit, with recycled oxygen and a squat tank), forecast $25.04 → $24.80.
  Median shares unchanged to one decimal. The first change in this model's history that lowers a headline.
- Recomputed with it: the frontier ($7.03 → $6.85, just under parity), filter flux (Central $48.59 at 1,200 L/m², $94.63 at 450), the
  audit (Central's median over all ranges $36), the company-claims split, the design search (the setpoint is no longer an option: 144
  designs), the vessel grid, RESULTS, METHODS and the notes' ladder sections.
- Vessel grid: a vessel whose column loop fails its checks at full density now runs thinner until it passes (`vessels._thinned`,
  mirrored on the page), in place of dropping the tricks. Central in an airlift: $30.88 at 139 g/L.
- `scenarios.interactions` breaks ties by the switches' order, so Python and the page sort alike.

How far tank design can go (`design_space.py`, `research_notes/design_space.md`; no default changed, no number moved)
- Method: price each limit first (`limit_prices`: the cost if CO₂, oxygen, mixing, the thickness limit, the litres of medium, the
  membranes and others were free), then search every combination of the tank options the model has (288 designs a scenario, under two
  seconds for all), keep those whose column loop passes its checks, and compare with the ordinary tank with every gas limit lifted.
- Findings: tank design is worth $28/kg for today's cells ($62.96 to $34.80) and $1.4–2.8 beyond the scenarios' own designs from
  rung 2 on ($0.4 in the best case). Designs that leave only the thickness limit binding exist: a bubble cage with 1 bar, or 2 bar
  without a cage. Holding dissolved oxygen at half of air saturation is standard practice, unused by the scenarios, and worth $0.5 in
  Central. After the gas limits, the litres of medium dominate ($15.7 in Central against $2.2 for perfect gas exchange).
- The search reproduces every scenario's own tank design exactly. `tests/test_design_space.py`, in `run_tests.sh`.

Bioreactor design tricks and a CFD plan (`research_notes/bioreactor_design_tricks.md`, `research_notes/cfd_plan.md`; no number moved)
- A catalogue of tank design tricks by what they relieve (CO₂, oxygen, mixing, salt, heat), whether something fundamental stops them
  scaling (surface-to-volume, depth, flow-path length, foam, regulation), and where each sits in the model. Today's cells are CO₂-bound;
  Central and the best case are oxygen-bound, so oxygen per watt (two spargers, impellers, antifoam) is now the lever. Not yet in the
  model: two spargers, gas exchange on the filter loop. Perfluorocarbon oxygen carriers are PFAS, close to a non-starter for food.
- The CFD plan: four steps from validation to bubbles, each replacing a named model input. FluidX3D v3.9 builds and runs on the Apple M4
  (505 million updates a second in 32-bit, 766 in 16-bit; one buffer of at most 2.27 GB caps the grid at about 30 or 60 million cells).
  The laminar pipe-flow check converges to 0.16% error in 32-bit but stalls at 23% (FP16S) and 15% (FP16C): use 32-bit for validation.

A stirred tank with a bubble cage (Pablo's design; `vessels.py` row "caged", inputs `vm_cage_*`; no scenario uses it, no number moved)
- An inner cylinder of fine mesh holds a strong sparger; the cells live in the ring around it with the scenario's own soft bubbling.
  The cage's gas (6 mm/s over the tank, 3-12) adds to the ring's, discounted to 80% (0.5-1) because only medium crosses the mesh;
  capital 1.15x a stirred tank. All three are judgements; caged aeration is known only with microcarriers in small tanks.
- Perfusion: reference $11.08 (plain tank $12.51), Central $27.72 ($29.92), today's cells $39.23 ($62.96).
- `vessels_and_modes.md` section 9: the design, the gas-filled variant (a membrane: about 9 m² of wall against 1,200-1,500 m² needed
  for CO₂), and a table of other ways to keep bubbles from cells. RESULTS' vessel table gains the row. `floor_physics.explore` reads
  two new vessel keys, `co2_mult` and `no_protectant` (unused by any row now), mirrored in the page.

Restart from a neighbouring tank (`sc_restart_neighbour`, a fourth setting of "Restart after a loss"; no scenario uses it, no number moved)
- A lost tank reseeded with half the culture of a healthy neighbour: 4 days (3-7) in place of 14 with a fresh seed train, which needs
  about 7 doublings. Worth $0.8 a kilo in Central, $5.6 for today's cells (rung 1, which restarts in 21 days). The donor must test clean.
- The page explains why the company sliders are locked and when oxygen, not CO₂, limits the tank (PR #36).

The scenarios as a ladder ordered by difficulty (`scenarios.LADDER`, `PAGE_ORDER`; Pablo's review; no cost of an existing scenario moved)
- Five rungs, each adding one kind of change: 1. today's measured cells in an ordinary tank, no tricks, today's prices ($63.0);
  2. plus process changes and cheaper inputs ($31.3; the tank tricks alone are worth $19.2); 3. plus selected cells = Central ($29.9);
  4. plus a plant with shared medium ($26.8); 5. plus engineered cells = the best case ($9.7). A forecast row for 2035 ($25.0, median
  share 0.3%) is a first draft of the author's medians, with the odds behind each in RESULTS.
- The reference is renamed "Humbird's optimistic design" and sits beside the ladder: it assumes engineered cells and no tank tricks.
- Every row of the headline table gives the share at its point cost and the median of draws (`bands(None)` for Humbird's design,
  `reported_band` for the company's process), so rows compare: Humbird's design 2.4% median, best case 3.8%.
- `ORDER` keeps the four scenarios the side studies use; `cautious` leaves the page. Page prose, RESULTS, METHODS, README,
  `cost_scenarios.md`, the company-claims table and tests follow. Roadmap: CFD target A5, oxygen transfer per watt for impellers and spargers.

Model audit: drift, accuracy and whether the costs are reasonable price points (`audit.py`, `audit_history.py`, `research_notes/model_audit.md`; no default changed; recomputed after PR #32)
- **Drift:** measured at every commit that touched the cost code. Default $24.01 -> $34.35 (14 Nov), Central $18.14 -> $26.64 -> $29.92, best $6.57 -> $8.95
  -> $9.71 (15-16 Nov). Every step that moved a headline added a cost an earlier version left out; none lowered one.
- **Accuracy:** the model needs 1.2 to 2.8 times less medium than every reported perfusion run and predicts 2.3 times the output of the one
  working 20 m3 plant. Drawing every documented range at once, Central's median is $37 (10th-90th percentile $27-51; the $29.92 point is at the
  19th percentile) and the best case's is $15.1 ($9.71 is the 1st percentile).
- **Shelf price:** a flat $5 markup gives Central $35; a markup proportional to the price (as conventional spreads are) gives $56 and lowers the
  cost at which cultivated meat reaches parity from $7 to $5.6. New inputs `au_retail_share`, `au_processing`. `tests/test_audit.py`, in `run_tests.sh`.

Can a filter hold 5 L/m2/h at 25% cells? (`filter_flux.py`, `research_notes/filter_flux.md`; no default changed)
- The physical ceiling (shear-induced back-transport, as printed in two theses) is 57 to 800 L/m2/h for the model's cells: 5 L/m2/h is not above it
  (under 5% in my judgement). The limit is fouling: CHO membranes fouled after 450-1,200 L/m2 (Pinto 2020, Veje 2024, read in
  full), 3 to 9 times below the default 3,960. At those throughputs Central costs $49-94 and the best case $15-29 (recomputed after PR #32). The flux
  itself barely moves the cost (about $0.2 for halving it); the membrane's throughput does. `tests/test_filter_flux.py`, in `run_tests.sh`.

The frontier: every lever at its limit (`frontier.py`, `research_notes/frontier.md`; no default changed; recomputed after PR #32)
- Central ($29.92) with one lever at a time moved to the limit its research note supports, each kept moved: least medium 6.4 L/kg
  $14.27, 16 h doubling $10.32, shared-medium plant $8.38, 0.2% losses $8.02, gas 6 mm/s **$7.03** ($7.83 with GFI's amino-acid floor).
  At the $7 that parity needs, not below it. With antifoam counted oxygen binds at 177 g/L, so 320 g/L adds nothing ($6.33 without the
  antifoam effect). The litres of medium per kilo are the lever: they set the medium, growth-factor and filtering costs together.
- Growth factors returned by the filter: the share charged is now capped at what is charged without the filter. Once the medium is cut
  to 6.4 L/kg the bleed carries out as much liquid as comes in, and the uncapped formula made returning the proteins cost more.
- `tests/test_frontier.py`, in `run_tests.sh`.

The model against company cost claims (`industry_claims.py`, RESULTS section 1, the page's evidence section; no number moved)
- Each scenario split into the yearly charge on the plant and operating cost. Company figures are operating cost (COGS); the
  scenarios include the plant. Central: $29.9 = $8.2 plant + $21.7 operating, of which $8.2 filter membranes.
- Central's cells in a 20 m³ tank drained and refilled (as Vow runs): operating cost $13.7–14.0, inside the $10–15 an investor reports
  for several companies (Lever VC, NDA data). The plant charge is $9–33 depending on the plant; in a yeast plant with what animal cells
  need, $23.3 in all, below Central in perfusion. At the 27 g/L reported for meat cells, $51–103.
- A table of six claims with their basis (what it is a cost of, capital in or out, model or run, who checked it).
- `tests/test_industry_claims.py` (in `run_tests.sh`) checks RESULTS carries the tables and the figures its prose quotes.

## 2026-11-15

Three costs counted, the plant ladder tied to `explore` (Pablo asked for the long-term choice on each; **numbers move**)
- **Bubble protectant** (poloxamer 188): new inputs `pf_protectant_dose` (2 g/L, 1–5) and `pf_protectant_price` ($30/kg assumed, $10–260;
  catalogue $230–260), charged per litre of medium in every sparged vessel; `explore(protectant_price=)`, a tornado bar, the JS mirror.
- **Antifoam**: `pf_antifoam_otr` default 1 → **0.75** (the middle of the reported 0–50% cut; judgement). Oxygen now limits Central (177 g/L)
  and Cautious.
- **Yeast-style plant buys its oxygen** (`pi_o2_feed` × `pi_o2_price`, $0.33/kg), as item-built plants already did; switch `pf_o2_microbial`.
- **The plant ladder's perfusion rows are `explore()` itself** (filter loop, protectant, oxygen), so they cannot drift again: reference
  tier $11.5 → $12.5 (first plant $14.1 → $14.8), microbial tier $6.6 → $8.0. `plant_floor` 9.8 → 10.8, `plant_floor_lo` 4.9 → 6.3, the
  `overhead` range starts at 10.8. Golden `cost_floor` 11.502 → 12.502.
- Scenarios (designs chosen again): best $8.95 → **$9.71** (R 1.23, median world share 3.8%), central $26.64 → **$29.92** (R 2.91, 0.2%),
  central with shared medium $24.34 → $26.81, cautious $38.97 → $43.79, reference $11.84 → $12.51. Best case and Central now use the column,
  1 bar and a tank as deep as wide (recycled oxygen fails the loop checks); Cautious the column and 1 bar in the tall tank.
- The default's Monte Carlo: R median 3.27 → 3.29; regional bands updated.
- Docs: RESULTS (summary, cost table, the cells-by-tricks tables and the gas-cap table recomputed: they still carried pre-filter-loop
  figures, e.g. bovine cells with glutamine replaced at $17.5 where the model now gives $26.2), METHODS (scenario, tier, tornado, CO₂, species,
  floor Monte Carlo tables: the last still showed a median of $18.6), `cost_scenarios.md`, `vessels_and_modes.md`, `gas_flow_cap.md`.
- **Side studies are now snapshots with a stated basis**: `floor_physics.BEFORE_PROTECTANT` / `BEFORE_FILTER_LOOP` and `tests/_snapshot.py` run
  their tests with the settings their notes were computed with; each note says so at the top and gives the current scenario costs.

Housekeeping (`TODO.md`; no default changed, no headline moved)
- **`TODO.md`**: one list of open PRs, decisions waiting on Pablo, housekeeping and project ideas; `research_notes/roadmap_2026-11-15.md`
  keeps the reasoning for the projects.
- Two new levers from the gas-flow follow-ups, each with a tornado bar and the page mirror (parity holds):
  `explore(strip_eff=)` (CO₂ carried off by the exhaust gas, 0.70–0.96; at 0.70 the reference holds 87 g/L and costs $13.60) and
  `explore(antifoam_otr=)` with new input `pf_antifoam_otr` (default 1, range 0.5–1; sparger oxygen only). Halved, the reference
  becomes oxygen-limited at 97 g/L ($12.88) and Cautious goes from $38.97 to $50.58.
- Poloxamer 188: catalogue price only (~$230–260/kg); at 2 g/L that is $5.6–14 a kilo of cells. Not added; in `gas_flow_cap.md`
  and TODO.md as a decision.
- Notes recomputed with the filter loop: `cost_scenarios.md`, `vessels_and_modes.md` (every figure). `cheap_plant_study.md` and
  `gas_exchange_study.md` stay dated snapshots (their tests pin the old device) with a box of current figures: the tank tricks are
  worth about half as much (the gentler column saves $1.47, not $2.86); the lean plant's break-even loss rate is 3.9% a day.
- `interactive.html` rebuilt (main's copy was older than its source); untracked notes and the growth-rate proposal committed.

Is 20 m3 the right tank size? (`tank_size.py`, `research_notes/tank_size.md`; no number moved)
- Cost against tank size, 2 to 200 m3, for each scenario and the reference, with the tank design (tricks, shape) chosen again at each size
  under the column loop's pH and pass-rate checks. 20 m3 is within 0.4% to 2.3% of the cheapest size: best $8.95 -> $8.82 at 55 m3,
  central $26.64 -> $26.50 at 23 m3, central with shared medium $24.34 -> $24.25 at 34 m3, cautious $38.97 -> $38.08 at 46 m3. The
  20 m3 designs fail the pH check at 23 to 26 m3; without the checks the best case would save 3.4% at 200 m3. Smaller tanks cost
  2% to 4% more at 10 m3 and 20% to 50% more at 2 m3. Labour per m3 is the one assumption that could move the answer (the best case
  would be 7.6% cheaper at 200 m3 if crew per m3 kept falling as in Humbird's plants). Odds for each size are in the note. New inputs
  `ts_ph_relaxed`, `ts_loop_hw_exp`, `ts_hazard_exp` (what-if rows only). `tests/test_tank_size.py`, in `run_tests.sh`.
The least medium per kg of cells that physics allows (`min_litres.py`, `research_notes/min_litres_per_kg.md`; no number moved)
- Waste sets no floor: nitrogen, carbon and energy balances all allow zero ammonia and zero lactate. Delivering the nutrients
  does: 0.58 kg (Best) to 0.64 kg (Central) of amino acids and glucose per kg of cells. If the medium must be what the cells
  sit in, the floor is 14-25 L/kg (Central's 28 is within 10% of it; Best's 11 is not possible). If a concentrate of 100 g/L is
  diluted in the tank, it is 5.8 L/kg (Best) and 6.4 (Central), or 8.0 at the lowest flow per cell measured. Costs at those
  litres: Best $6.94, Central $12.28-13.05, against $8.95 and $26.64. New `ml_*` inputs; `tests/test_min_litres.py`, in
  `run_tests.sh`.
The nutrient floor from GFI's amino-acid prices, and a $0.05 medium setting (`nutrient_floor.py`, `research_notes/nutrient_floor.md`)
- The model's nutrient floor ($1.70 a kilo) is below every figure GFI's December 2025 prices give ($2.50 to $16.09): its amino acids
  are $0.67, against $1.48 at GFI's cheapest tier. The best case, whose medium is set by the floor, would cost $9.76 to $12.36 at
  the cheaper tiers (now $8.95); Central does not move unless amino acids are dear. No default changed.
- New "Price of the medium" setting: **$0.05 a litre**, an aspiration tagged "feed or process". Central at $0.05: $22.68 (the floor
  binds). The best case keeps $0.15, and its rule text says so. "What decides it" for Central now shows the medium price worth
  −$3.96 at its best setting.

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
