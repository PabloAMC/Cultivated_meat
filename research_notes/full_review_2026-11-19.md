# Full review: the model against the books, the cost analyses and new evidence

Date: 2026-11-19 (evening), branch `claude/full-review`, on main at `28dc6a9`. Five independent readers with no prior context:
the 14 cost analyses in `Cultivated_meat_TEAs/`; the two books (*Cultivated Meat*, 440 pages; *Cellular Agriculture*, 2024) and the six
papers in `articles/`; a web search for evidence from 2024 to 2026 on the cost side; the shopper model and its evidence; and a port of
the retention study to the page. Costs quoted are for the low-lactate example (0.14 mol of ammonia a kilo, 0.42 mol of lactate per
mol of glucose, 36-hour doubling, perfusion at 20 m³; `central` in the code), which is $32.80 a kilo with every estimate at its most
likely value. I re-ran the figures marked **re-run**; the others are the readers' own runs or arithmetic. No default was changed by
this review: section 5 lists what I propose to change in one batch, because any change of default moves about 25 side studies.

## 1. Verdict

- **Nothing found overturns the qualitative answer.** The model's inputs sit inside the ranges of the books and the cost analyses for
  every parameter that could be checked (table in section 6).
- **The perfusion cases are optimistic in six places that the page did not show**, each worth $1 to $8 a kilo, all in the same
  direction (section 2). Together they would move the low-lactate example from about $33 to roughly $40-50 (my estimate, 60%
  that the sum is in that range; the items overlap, so they do not simply add).
- **Published cells in a fed-batch tank barely depend on those six**, because their cost is almost all tank time. They depend on one
  number with no range in the model: the lactate the cells tolerate (section 2, item 1).
- **The shopper model's arithmetic is right**, but its uncertainty band draws shoppers' acceptance twice, and the "price parity" line
  on the share map invited a reading that only holds for one kind of meat (section 3).

## 2. Cost side: findings that would change a number

| # | Finding | Evidence | Effect on the low-lactate example | Status |
|---|---|---|---|---|
| 1 | **Lactate tolerance is fixed at 50 mM with no range**, so the bands never draw it. *Cultivated Meat* (Table 2, book p. 120, citing Hassell 1991) gives under 10 to 22 mM; Pasitka 2024 held 30 mM. | `pf_lac_limit` | 50 or 35 mM: $32.80; 30: $33.38; 22: **$42.54**. Published cells in fed-batch: $209 at 50, **$298 at 35, $347 at 30, $473 at 22** (**re-run**). The low-lactate example sits on a knife-edge: lactate needs 35.8 L/kg at 30 mM against ammonia's 35. | Now a slider on the page. Proposed: give the input a range (20-50, mode 35-40) |
| 2 | **Medium preparation and sterile hold are sized for a fed-batch plant.** Humbird's fed-batch plant handles about 8.7 L/kg; the example passes 35 L/kg, 5.9 times more medium per m³ of tank a year. His perfusion design carries $18.0M of medium equipment for 192 m³ of tank (Table 4.8) against $7.2M for 480 m³ in fed-batch (Table 4.1). | `plant_items` "medium" item, no dependence on `medium_l` | +$1.5 (six-tenths scaling) to +$3.9 (linear). In-line dilution of a concentrate would cut it. | New. Proposed: scale the item with litres per m³ a year |
| 3 | **The membrane price is Humbird's but not his membrane life.** His Table 4.11 implies 2,415 L/m² ($0.61 a litre); the model pairs $1,450/m² with 3,960 L/m² ($0.37). | `rt_membrane_price`, `rt_membrane_life` | At 2,415: **$40.99**; at 1,500: $53.79 (**re-run**). Other direction: Pasitka reuses cassettes five times; food and water hollow fibres are quoted at €20-80/m² (a market summary, low quality). | Extends the open "filter pair" item. Both are now separate sliders |
| 4 | **The density is 2.3 times what any company reports.** SuperMeat 83 g/L; Lever VC 60-90 g/L; A. D. Little 55-100 g/L; the model runs 191 g/L. | density set by oxygen at 20 m³ | Capped at 150: $34.49; 120: $36.36; 83: **$40.61** (**re-run**) | New as a stated gap. The page's first result now shows the density and what limits it |
| 5 | **Bubble deaths are computed but never charged.** With the model's own kill constant (Jöbses 1991, 1 g/L protectant) deaths are about 11% of growth in the example; the lost cells lyse and are not harvested. | `gas_exchange.sparge_death` is only printed | +$1 to +$4 if the bench value holds at scale (the notes argue it overstates) | New. Proposed: charge it with a range |
| 6 | **Labour is half to a quarter of the analyses that assume perfusion.** Model 9.6 staff per kt; Humbird's perfusion design 19; CE Delft 20; SuperMeat 37. | `pf_labour` (fed-batch crew) | +$1.2 to +$3.6 | Now a slider. Proposed: Humbird's perfusion crew for perfusion |
| 7 | **No loss at harvest.** SuperMeat rejects 3%; Negulescu loses 2% in the decanter; Pasitka 1.3%. | `recovery` = 1 | +$0.7 to +$1.0 | Proposed: 2% |
| 8 | **The least medium flow is below Ozturk's range** (100 pL a cell a day in standard media, "several fold" less in concentrated media; the model allows 15). | `pf_min_perfusion` | $33.60 at 16.7 mL/g/day (**re-run**); the all-favourable example +42% | Already drawn (3.7-18.5); now a slider |
| 9 | **Viscosity**: Ozturk reports a 2-3 fold rise at 5e7 cells/mL; the model has no viscosity term below 258 g/L. | `thick_culture.py` is a side study | $34.5 to $37.1 | Overlaps item 4 |
| 10 | **Electricity**: CE Delft 21.7 kWh/kg at $0.095; the model about 7.6 kWh/kg at $0.064. | `pf_utilities` | +$0.15 to +$1.6 (35% that it is over $1) | Now a slider |

Also found, with no number attached: antifoam and protectant interact, and protection degrades over weeks at high density
(van der Pol thesis); a finite lifespan of 35-70 doublings means only immortal lines can fill and run a 20 m³ tank, while the
published traits come from primary bovine cells; a maturation stage, if the product needs muscle, adds tank time (+$5-30, the
reader's estimate); anchorage-dependent cells on carriers fall to fed-batch densities.

## 3. Shopper side

- **"At price parity the 50% line should pass through 50% of meat buyers."** For one kind of meat at its own price this holds
  exactly: the setting is defined as that share (14.5% gives 14.50%, 50% gives 50.00%). For the world total at the map's parity
  line it does not: 11.1%, 22.0%, 37.1% and 55.5% at settings of 14.5%, 30%, 50% and 70%. Three causes, at a setting of 50%: a steak
  or fillet costs more to make than mince at that cost of cells (+5.5 points); the average hides the spread of prices (chicken mince
  is at 1.9 times its price, steak at 0.6; +4.9 points); cuts and premium products carry a liking penalty (+2.7 points). Plant-based
  meat, the spread of liking and the two shopper groups do not contribute. No single "parity cost" can make it hold for a sum over
  meats with different prices. **Done on the page:** a new chart for one kind of meat, where the curve passes through the setting at
  the same price, with a mark for where each kind of meat sits at the reader's cost; the map's line is relabelled "mince at the
  price of the average kilo" and its note gives the total there and why. **Not done** (a decision): redefining the setting against
  the world total would make the map's property exact but would make the setting depend on region, retail margin and cell share,
  and today's 14.5% would have to be relabelled 11.1%.
- **The band draws acceptance twice.** `MC_DEMAND_INPUTS` still draws `accept_x` (0.6-1.0, one-sided) on top of
  `equal_price_share`, which the datasheet calls the net of everything. The equal-price median falls from 14.5% to 11.9%, and the
  share band is about a fifth lower than intended (0.42% against 0.54% at $26.4). It was left out when the other three dials were
  removed from the band on 2026-11-18. Proposed: remove it from the band.
- **Evidence on the setting itself** (13% of all choices, 14.5% of meat buyers): Van Loo 2020 gives 5% at first contact, Slade 2018
  11%; the step from 4.8% to 14.5% is the model's judgement that novelty fades. Plant-based meat's record runs against it (US
  household penetration 20% in 2021, 11% in 2025). No post-tasting choice share exists. 55-58% (the all-favourable example) has no
  empirical support. 55% that 13% is within a factor of two.
- **Blends.** A cut is 80% cells and loses 20% of the real-meat credit. Products on sale are 3-30% cells, and one was received as
  "another class of plant-based". If cuts lost half the credit the world share at $26.4 would fall from 0.43% to 0.36%.
- **Plant-based meat's share target** (1.2% by volume) looks about twice too high (0.7% of meat dollars in 2025 at 1.76 times the
  price); the effect on cultivated meat's share is small (0.43% to 0.41%).
- **Regional income is at purchasing-power parity while prices are in nominal dollars**: at a nominal world income the share at
  $26.4 is 0.35%, not 0.43%.
- **Left out and worth a sentence each in METHODS**: bans (eight US states, Italy, Hungary: timing, not the long-run share); halal
  and kosher status (about a quarter of the world; rulings are conditional); substitution across meats (cheap cultivated beef would
  also take from chicken); the response of conventional meat's price (only matters above a few percent of the market).

## 4. New evidence worth citing (none forces a change)

- **Believer's FDA memo** (CCC 000039, July 2025, read in full): the production tank is perfused; cell-bank doubling time under 30
  hours; insulin and FGF2 used only to make the cell bank; the ammonia and lactate removal step was optional and never used.
- **Wildtype's FDA memo** (CCC 000005, May 2025, read in full): suspension fed-batch in stainless tanks; FGF2 the only growth factor.
- **Believer's 20 m³ plant never validated its process** (trade press, December 2025): the only attempt at perfusion at that size.
- **Lever VC 2025**: 60-90 g/L, cells at $10-15 a kilo (investor claims); most companies choose fed-batch.
- **A. D. Little 2026** (trade press): product in the "low €40s" a kilo, medium near €0.20 a litre, 55-100 g/L.
- **Vow / Parima 2026** (press): a 1,500 kg harvest from a 22 m³ line, 68-85 g/L if it is one drain of wet cells (40% that it is).
- **Poloxamer 188** at about $20-25 a kilo in bulk (market summaries): supports `pf_protectant_price` $30.
- **Meatly 2025** (press): protein-free medium at £0.22 a litre; a 320 L vessel for £12,500.
- **Tufts DF-1 chicken fibroblasts** (preprint, September 2025): 30-hour doubling in suspension, about 1.0 ng a cell: both chicken
  fibroblast lines measured are 1 ng or less, against the model's 2 ng.
- **Negulescu 2023**: measured C2C12 yields of 252 g of amino acids and 1,157 g of glucose per kilo; supports `aa_intensity` 232.
- **Goodwin 2024**: the immortalised bovine cells behind the 15-hour doubling (with serum) doubled in 55 hours serum-free.
- **Gu 2025**: sorbents measured in culture medium (zeolite 60% of ammonia in 24 h); the `pf_sorbent_q` note says none was measured.
- Not found: any peer-reviewed cost analysis since Pasitka 2024; any measured oxygen uptake or CO₂ tolerance for a meat cell; any
  sales volumes.

## 5. What changed in this branch, and what waits

**Changed (no model number moved):**
- The page's first screen is rebuilt in four sections, each with its sliders before its result: the cells; the reactor and how it is
  run; the medium; the shoppers and the product. It opens on the published measurements. The named hypothetical cell types are gone
  from the page and the documents; where an example set is needed it is "the low-lactate example" or "the all-favourable example",
  defined by its traits.
- Twenty more inputs are sliders in collapsible groups (`build_interactive.PAGE_PARAMS`): ammonia, lactate, salt and CO₂ tolerated,
  oxygen use, upkeep share, gas flow, least medium flow; membrane price, life and flux, the yearly charge, oxygen transfer, labour,
  energy; amino-acid and glucose prices, growth factors, protectant dose and price. Each shows its source.
- The vessel (six types), the way it is run (five modes) and the retention device (nine, ported from `retention.py` to
  `page_retention.js` with a parity check) are choices on the first screen, with comparison tables at the reader's settings.
- The share map has a literal title and no reference points (a published cost says nothing about shoppers); published costs are
  ticks on the cost axis.
- The cost on the first screen is the cost at the settings shown; the draws are under "How uncertain is this cost", with each
  estimate's range. Every meat price names its kind of meat, and there is no single "price parity". White background, Computer
  Modern, and a summary bar that stays in view.
- Two source texts corrected: the protectant cuts bubble deaths about 20-fold at 1 g/L (Jöbses 1991; the text said "at least
  100-fold", against the model's own inputs); Pasitka's 2024 abstract gives 130 million cells/mL at 43% w/v.

**Proposed as one batch with one repin (waits on the author):** items 1, 2, 5, 6 and 7 of section 2; `accept_x` out of the band;
the filter pair (item 3) decided as a pair. Each is small; together they move every figure in RESULTS.

**Open questions for the author:** whether the page should open on Published cells in fed-batch ($209 a kilo) as it now does; whether
the meat-buyers setting should be redefined against the world total; the range for lactate tolerance.

## 6. Checked and consistent

Ammonia limit 4-5 mM (books: under 2 to 10, "usually 5"); CO₂ 100 mbar (40-100 optimal, above 130 inhibitory: top of range); oxygen
uptake 0.28-0.46 pmol a cell an hour (Ozturk 0.05-0.5: cautious end); respiratory quotient 1.2 (about 1: cautious); dissolved oxygen
0.10 mmol/L; kLa 26 per hour (5-55); mixing time 141 s ("several minutes"); lactate per glucose 1.05 measured (1-2 typical); cell
mass 2-3 ng (2-4 pL; 3.5 ng); doubling 24-43 h (24-40 h); fed-batch density 14-37 g/L; bubble size; shear in the filter loop 1.4 Pa
(critical 1-4); pH 7.2 and 37 °C. Humbird's inputs as transcribed (capital, financing, uptime, turnaround, labour, utilities,
consumables, growth factors, limits, gas velocity, pressure, oxygen price, viscosity limit, cell mass, ATF cost); water and
wastewater (inside utilities, under $0.3/kg in every analysis); sterile filters; uptime 82% against SuperMeat's 80%; the retail
margin applied once; volume weights; the plant-based calibration (1.200%); first-contact share 4.3-4.8%.

Not checked: Pasitka's and Negulescu's supplementary tables (not in the folder); Risner, Ashizawa and GFI 2021 were skimmed; the
books were read by contents and keyword, not cover to cover.
