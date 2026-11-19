# Cultivated meat: how far can it get? Results

*These are the findings of a cost and demand model. The scenarios (`scenarios.py`) describe what has to go right for the cost to
fall. They use physics and published plant costs (Humbird 2021). One more row gives the cost a company reports for its own process
(SuperMeat 2024). The [interactive explorer](https://pabloamc.github.io/Cultivated_meat/interactive.html) explains the
method in plain language and lets you change every assumption. [METHODS.md](METHODS.md) has the code-level detail.
Everything below reproduces from the code.*

## Summary

*Last revised 2026-11-19. What changed, and when, is in [CHANGELOG.md](CHANGELOG.md).*

**The answer.** With the best meat cells in the published record, grown as they are grown today (in batches, in a 20 m³ tank), a
kilo of cells costs about **$219** (median; 8 in 10 draws between $162 and $282; $209.1 at most likely values), 26 times the shop
price of everyday meat, and cultivated meat takes under 0.001% of world meat and seafood. What it would take to matter:

| long-run share of world meat and seafood | with this share of meat buyers picking it at equal price | cells must cost (most likely values) | the cells tried that reach it with the fewest traits beyond the best measured in meat cells | at | traits beyond the best measured in meat cells (each against its own best measurement) |
|---|---|---|---|---|---|
| 1% | 14.5% | $19.7 a kilo or less | ammonia 0.055 mol/kg, lactate 0.42 mol/mol, a doubling every 15 h, 2 ng | $19.4, a food-grade plant, fed-batch at 20 m³ | ammonia 0.055 mol/kg wet, against 0.14 measured; lactate 0.42 mol/mol, against 1.05 measured |
| 10% | 14.5% | $4.9 a kilo or less | none of the sets tried |  |  |
| 1% | 50.0% | $29.8 a kilo or less | ammonia 0.14 mol/kg, lactate 0.42 mol/mol, a doubling every 20 h, 2 ng | $29.4, a food-grade plant, perfusion | lactate 0.42 mol/mol, against 1.05 measured |
| 10% | 50.0% | $12.9 a kilo or less | ammonia 0.055 mol/kg, lactate 0.279 mol/mol, a doubling every 15 h, 2 ng | $11.8, a food-grade plant with shared medium, perfusion | ammonia 0.055 mol/kg wet, against 0.14 measured; lactate 0.279 mol/mol, against 1.05 measured |

- **A 1% share needs cells at about $20 a kilo** with the model's 14.5% of meat buyers picking cultivated meat at equal price, and
  about $30 if half of meat buyers did. Among the sets tried, the first is reached with two traits beyond the best measured in meat
  cells, ammonia at 0.055 mol a kilo (0.14 measured) and lactate at 0.42 mol per mol of glucose (1.05 measured), in a 20 m³ batch,
  the mode that has been shown, not in perfusion; the second with one, the lactate.
- **A 10% share needs cells at $4.9 a kilo at 14.5% of meat buyers**, below every set of traits tried, and below the $6.1 of parity
  with a $12 kilo of everyday meat. At 50% of meat buyers it needs $12.9, which the sets tried reach only with ammonia and lactate
  both well beyond the best measured in meat cells.
- **The table says what has been measured, not how cells would get there.** For each trait the best value measured in meat cells is
  0.14 mol of ammonia a kilo (Hubalek 2023, bovine fat-precursor cells fed without glutamine), 1.05 mol of lactate per mol of glucose
  (Pasitka 2024, chicken fibroblasts in perfusion), a doubling every 15 hours (Stout 2023, immortalised bovine muscle cells, with serum)
  and 3.3 ng a cell (Pasitka 2024, chicken cells, from their density); `cell_traits.best_in_meat_cells`. Each trait is set against its
  own best measurement. Nothing here says how cells would come to have a trait.

The reference points, each defined by its cells' traits and the plant and process around them (`scenarios.py`), are in the table
below. With the Selected cells case's traits (ammonia 0.14 mol a kilo, lactate 0.42 mol per mol of glucose, a doubling every 36 hours,
2 ng a cell) in perfusion a kilo costs about **$36** (8 in 10 draws between $26 and $55; $32.8 at most likely values), and cultivated
meat takes about **0.17%** of world meat and seafood (0.03–0.9%; 0.21% at the most-likely-values cost). With Engineered cells, all
favourable (0.055, 0.28, 24 hours, 2 ng, every other setting at its favourable end) it costs about **$15** ($12–20; $11.7) and takes
**7.7%** (3.1–16.2%; 15.1%) if 58.5% of meat buyers come to pick it at equal price, or 1.5% (0.5–5.7%; 3.2%) at the ordinary 14.5%. No
case reaches price parity with a $12 kilo of everyday meat, which needs about **$6.1** a kilo of cells (the world's average kilo, at
$9.43, needs about $4.29). The cost rests on a handful of numbers, and the weakest of them have never been measured on meat cells
("What the answer rests on", below).

**What changed on 2026-11-19 (scenario restructure).** CHANGELOG.md has the figures before and after.

- **A batch is held by a mass balance.** In any mode, the litres a kilo of cells leaves with must hold its waste at the level the
  cells tolerate. A tank that is not washed out may end its batch 1.3 times above the level perfusion is held to, as Humbird's own
  fed-batch design does, and its last doublings grow slower there. Before, Humbird's fed-batch density was scaled by the cells'
  waste, which let the Selected cells case's batch end at 7.8 mmol/L of ammonia against the 4 its perfusion is held to. Those cells
  now stop a batch at 37 g/L, not 56, and the published cells at 14 g/L, not 25 (`research_notes/vessels_and_modes.md`, section 10).
- **How the tank is run is a switch**: fed-batch at 20, 50 or 100 m³, or perfusion at 20 m³. Fed-batch at 20 m³ is what has been shown
  for meat cells (Upside Foods, 2026); perfusion has not been run with animal cells above about 4 m³.
- **Cells are four traits**, set directly, each set against the best value measured in meat cells (`cell_traits.best_in_meat_cells`;
  the evidence is in `research_notes/cell_trait_routes.md`). The named cases are reference points defined by their traits.
- **The share is the share of the meat sold**: cultivated over cultivated plus conventional meat, for each product. It was the share of
  all four choices (with plant-based meat and no meat). Every share rose, by 13–28% of itself, most where the share is small.
- **Every kind of cell weighs 2 ng** (range 1–3 ng, drawn in the bands). The low-waste setting changes the metabolism, not the size;
  it was Humbird's 3 ng. Engineered cells, all favourable costs $11.7 at most likely values, not $11.5.
- **The ammonia the selected cells make** keeps its value (0.14 mol a kilo, the one stirred measurement), with its low end widened
  from 0.07 to 0.04 after a two-sided evidence pass (`research_notes/ammonia_tolerance_and_filter_life.md`, section 10).
- **Names.** "Central" is now Selected cells, and "the best case" Engineered cells, all favourable.
- **No forecast.** A forecast drawn from the author's odds for 2035 was built and dropped on the same day: the uncertainty is shown as
  clouds of draws over the estimates nobody has measured, for any setting of traits and choices, not as odds on the choices.

**What moved the answer earlier on 2026-11-19.** An audit (`research_notes/audit_2026-11-19.md`) led to eight changes. The figures before
and after each are in CHANGELOG.md.

- **Ammonia.** The scenarios' cells tolerate 4 mmol/L of ammonia, the evidence note's own median, in place of Humbird's 5.
- **Lost runs.** A run lost to contamination now pays for the filter membranes it throws away early.
- **Glucose.** The glucose a kilo of cells takes up now comes from the cells' own balance of what they build, burn and ferment. The
  published cells ferment most of their glucose. They need about 4.5 mol of it and about 95 litres of medium a kilo, and cost about
  $112 a kilo, not $57.
- **Seafood.** World seafood is priced by who eats it: a mass market near $7 a kilo of edible fish and a premium tier near $20, in
  place of one row at $16 (`research_notes/world_seafood_prices.md`).
- **Cuts.** A cut is 80% cells bound with plant protein, plus $2 a kilo to assemble it (`research_notes/structuring_cost.md`).
- **Premium products.** The rule that made buyers of cuts and premium products less sensitive to price is gone: it raised the share
  whenever cultivated meat was the dearer product. In its place a cut is liked less in proportion to the plant protein in it, and a
  premium product is liked less by an amount that rises smoothly with its price.
- **Share at equal price.** The bands draw it around the model's own setting (14.5% of meat buyers, 13% of all choices), not from a range whose median was 21% of all choices.
- **The spread of liking.** How much shoppers like cultivated meat is now spread as a Student's t (standard deviation 3.9 utils, 4
  degrees of freedom), in place of a normal spread of 5 utils. The normal spread, fitted on 2026-11-18, rested on an integration
  that was too coarse. The new shape has more shoppers very far from the average, more very close to it, and fewer in between.
  More buy at several times meat's price, which doubled Selected cells' share. Fewer are moderately keener than average, and those
  are the buyers at one to three times the price, which cut the Engineered cells, all favourable case's share by nearly a third.

> **What the words mean**
>
> - **Cost** is per kilo of real cells, which are about 70% water and 20% protein, like meat. Plant costs are in 2025 prices.
> - **Share** is cultivated meat's share of all meat and seafood sold, by weight, in the long run: once it is on every shelf and
>   no longer feels new. It is not a forecast of when. Seafood is about a quarter of that total (24%). A fifth of a cultivated
>   cut is plant protein, and the share counts the whole cut. Since 2026-11-19 it is exactly that: for each product, cultivated
>   over cultivated plus conventional meat. Before, it was cultivated meat's share of all four choices (with plant-based meat and
>   no meat), which understated it: a market where every product costs the same and half of meat buyers prefer cultivated meat
>   showed 46.5%, and now shows 50.0%. Plant-based meat's own share keeps its definition.
> - **Share at equal price.** Of the shoppers who buy meat, the share who would pick cultivated meat when it costs the same as the
>   meat beside it and is familiar: **14.5% of meat buyers**, in every case but one; 50% would mean no preference either way.
>   Engineered cells, all favourable takes 58.5%. It is a judgement, not a measurement: the bands draw it between 3.4% and 55.5%
>   of meat buyers (5th to 95th percentile; median 14.5%). A lower price does not win everyone: for mince against $12 meat, 27%
>   of meat buyers pick cultivated meat at half the price and 45% if it were free, so about 55% never pick it at any price. With
>   every product at the price of its own meat the world share would be 13.1% of the meat sold, a little under 14.5%, because a
>   fifth of a cut is plant protein, which shoppers like less, and premium products carry a further offset. The model itself
>   works with all shoppers' choices among meat, cultivated meat, plant-based meat and no meat. There the same setting is 13% of
>   all choices (55% for Engineered cells, all favourable; drawn between 3% and 52%), the figure the inputs use.
> - **Median of draws.** Each headline number is the median of 4,000 draws in which the estimates behind a case vary, and "8 in 10
>   draws between" is their 10th to 90th percentile. Cost, shop price and share are all given this way.
> - **At most likely values** puts every estimate at its single most likely value. It is given second. It is lower than the median
>   cost, because most estimates have more room to fall short than to improve: 37% of the Selected cells case's draws and 10% of those of
>   Engineered cells, all favourable come in below it. Steps of the ladder and the side tables use it, so that they can be subtracted from one another.

| scenario | cells, $/kg: median of draws (8 in 10 between) | $/kg if every estimate lands on its most likely value | shop price against $12 meat, at the median | share of world meat and seafood, long run: median of draws (8 in 10 between) | share at the most-likely-values cost | cell traits set beyond the best measured in meat cells |
|---|---|---|---|---|---|---|
| 1. Published cells: the best meat cells in the published record, grown in batches in a 20 m³ tank | **$219** ($162–282) | $209.1 | 25.6× | **under 0.001%** (9 in 10 draws under 0.002%) | under 0.001% | none |
| 2. Plus process changes and cheaper inputs | **$210** ($153–274) | $201.4 | 24.6× | **under 0.001%** (9 in 10 draws under 0.003%) | under 0.001% | none |
| 3. Plus cells that make less lactate (0.42 mol per mol of glucose) and double every 36 hours, still in batches | **$67** ($43–105) | $64.9 | 8.0× | **0.02%** (0.003–0.2%) | 0.02% | lactate |
| 4. Plus perfusion (Selected cells): waste washed out through a cell filter | **$36** ($26–55) | $32.8 | 4.4× | **0.2%** (0.03–0.9%) | 0.2% | lactate |
| 5. Plus a food-grade plant with shared medium | **$33** ($24–52) | $29.9 | 4.1× | **0.2%** (0.04–1.1%) | 0.3% | lactate |
| 6. Plus cells that make almost no ammonia or lactate (0.055 mol a kilo; 0.28 mol per mol of glucose) | **$24** ($18–34) | $17.3 | 3.0× | **0.5%** (0.1–2.3%) | 1.4% | ammonia, lactate |
| 7. Plus everything else at its favourable end (Engineered cells, all favourable) | **$15** ($12–20) | $11.7 | 2.0× | **7.7%** (3.1–16.2%) | 15.1% | ammonia, lactate |
| Humbird's optimistic design: his enhanced cells in an ordinary perfusion tank | **$16** ($13–22) | $12.8 | 2.2× | **1.3%** (0.4–4.7%) | 2.7% | ammonia, lactate |
| As a company reports (SuperMeat 2024) | **$34** (its own point figure) | $34.4 | 4.3× | **0.2%** (0.06–1.0%) | 0.2% | a company's own report |

**The steps between the reference points.** The first seven rows change one kind of thing at a time, from what has been shown to
every setting at its favourable end. They explain what each change is worth; they are not a path anyone must follow, and the order
says nothing about which route gets the cells there. In this section every cost is at most likely values unless it says "median",
so that the steps can be subtracted; the table gives the medians.

- **Row 1, Published cells ($209.1).** The cells are not one cell line. They combine the best published figure for each trait, never
  measured together in one line: ammonia (0.14 mol a kilo) and a 43-hour doubling from primary bovine fibro-adipogenic progenitor
  (fat-precursor) cells fed alpha-ketoglutarate in place of glutamine (Hubalek et al. 2023, Mosa Meat and Maastricht University,
  spinner flasks, five donors); lactate (1.05 mol per mol of glucose) from chicken fibroblasts in perfusion (Pasitka et al. 2024,
  Believer Meats); a cell mass of 2 ng (chicken cells are reported at 1.0–1.75 ng and about 3.3 ng; Humbird assumed 3 ng); and glucose
  from the cells' own balance. Companies may hold better cells they have not published. They are grown as a fed-batch in an ordinary
  20 m³ tank, the mode and size pharma runs and Upside Foods reports (`research_notes/vessels_and_modes.md`, section 11). Medium
  costs $0.30 a litre, between the $0.20 companies announce and the $0.50 one company reports.
- **Row 2, Plus process changes and cheaper inputs ($201.4).** The same cells and mode. Medium at the announced $0.20 a litre and
  growth factors at 30% of Humbird's price; more gas, the tank tricks and a faster restart do nothing for a batch held by its waste.
- **Row 3, less lactate and faster growth ($64.9).** Cells that make 0.42 mol of lactate per mol of glucose (the best measured in meat
  cells is 1.05) and double every 36 hours, grown in a 20 m³ batch.
- **Row 4, Selected cells ($32.8).** The same cells in perfusion.
- **Row 5, Plus a food-grade plant with shared medium ($29.9).** Its two small seed trains serve only long runs, so it follows
  perfusion; a fed-batch plant with shared medium keeps Humbird's full seed train.
- **Row 6, almost no ammonia or lactate ($17.3).** 0.055 mol of ammonia a kilo and 0.28 mol of lactate per mol of glucose, the
  metabolism of Humbird's efficient cell, at 2 ng a cell, doubling every 36 hours, with $0.20 medium. The best measured in meat
  cells are 0.14 mol of ammonia a kilo and 1.05 mol of lactate per mol of glucose.
- **Row 7, Engineered cells, all favourable ($11.7).** The cells double every 24 hours and need no bought growth factors, gas at 6 mm/s, and a
  medium that costs only what the cells eat (the nutrient floor, $2.00 a kilo of cells at GFI's feed-grade amino-acid prices). It
  takes the favourable end of demand too: once cultivated meat is familiar, 58.5% of meat buyers pick it at equal price, against 14.5%
  in every other row. It is not every switch at its cheapest: it loses 0.6% of runs a day, not pharma's 0.2%, and restarts in 14
  days, not 4.

**Why this order.** Each row needs nothing from the one after it, and the early rows need the least that is new: fed-batch at 20 m³
is shown, cheaper inputs need no new biology, and perfusion at 20 m³ has not been run with animal cells. The shared-medium plant
comes after perfusion because its saving on seed trains needs long runs. Perfusion is worth the most after the cells: $32.1 a kilo
with the Selected cells case's traits, $124.7 with the published ones (row 2, $201.4, against the same cells in perfusion with the
process changes, $76.7).

An announced or reported medium price is taken to include its growth factors (`growth_factors_in_medium_price.md`), so no row
with such a medium buys growth factors on top. Only the Engineered cells, all favourable case's medium would have them added, and its cells need none. Humbird's optimistic
design is not a row of the steps: it assumes cells with almost no waste (Humbird's 3 ng cell) and none of the tank tricks.

**The bands.** Each row's switches stay fixed, and the estimates behind it are drawn (4,000 draws). On the cost side: the plant's
cost and financing, the life and price of the filter membranes, the upkeep share of respiration, the medium price, the loss
rate, the ammonia the cells tolerate, the ammonia the selected and published cells make, the protectant's price and dose, the
least medium flow, antifoam's cost to oxygen transfer, the price of amino acids and the weight of a cell. On the demand side: the share at equal price,
the two price sensitivities, taste, the costs of reaching the shelf, the shop's margin, how much less buyers of premium products
like a cultivated version, and a cut's cell share and assembly cost. The kind of cells and their speed are not drawn: they are
what the rows differ in.

- **The published cells cost $209.1 a kilo in a batch, and lactate is the reason.** They turn most of their glucose into lactate
  (1.05 mol per mol of glucose taken up). By their own balance they need about 4.5 mol of glucose a kilo and make 4.8 mol of
  lactate. Nothing washes it out of a batch, so held to 1.3 times the 50 mmol/L perfusion allows, the batch stops at 14 g/L. The
  plant then makes few kilos: its charge is $151.0 a kilo and labour $28.9. Each kilo leaves with 73 litres of medium ($22.9). In
  perfusion with the tank tricks the same cells would cost $76.7: 95 litres of medium a kilo, but a tank 15 times denser.
- **Process changes and cheaper inputs take $7.6 off, to $201.4, without touching the cells.** All of it is the cheaper medium. A
  batch this thin is not held by gas, so more gas, the tank tricks and a faster restart are worth nothing (a lost batch costs its
  cells and 2 days, whatever the restart switch says).
- **Less lactate takes $136.5 off, to $64.9: the largest step in dollars.** These cells make 0.42 mol of lactate per mol of
  glucose (the best measured in meat cells is 1.05): 1.1 mol a kilo, against 4.8. Ammonia (0.14 mol a kilo, held to 1.3 times 4 mmol/L) then holds
  the batch at 37 g/L, nearly three times denser. The lower lactate alone is worth $126.4; the 36-hour doubling in place of 43 adds
  $10.1. Upside's reported capacity implies 33–136 g/L a batch, and Vow reports 27 g/L, so the companies' cells already make less
  lactate than the published ones (about 0.6–0.7 mol per mol of glucose would do).
- **Perfusion takes $32.1 off, to $32.8 (Selected cells).** Washing the waste out lets the tank hold 191 g/L, five times the batch, so the
  plant charge falls from $47.0 to $7.7 a kilo. It adds what a batch does not pay: 35 litres of medium a kilo where the batch used
  27, of which 30 pass a filter at $12.8 a kilo. Nobody has run the central tank design with animal cells. Oxygen limits it, at
  191 g/L: antifoam is taken to cost a quarter of the sparger's oxygen transfer, worth $1.6 a kilo here. Without the tricks a kilo
  costs $36.3 in a tank of the same shape, and $39.2 in the ordinary tall tank. At 30 hours the Selected cells case costs $31.6, and at 24 hours
  $30.3. The author puts the odds of 24 hours at this waste level at about 10%.
- **A cheaper plant takes $2.9 off, to $29.9.** It is Humbird's plant without a clean hall, an oxygen plant or eight seed tanks,
  and with one medium line for all the tanks. Nobody has built one. In a batch it would save more ($15.4, to $49.5), because a
  batch's cost is mostly plant; but a batch needs a fresh seed every three or four days, so it keeps Humbird's seed train.
- **Almost no ammonia or lactate takes $12.7 off, to $17.3.** Such cells need 16 litres of medium a kilo, not 35, set by the least
  flow a cell needs; every litre less is also a litre less through the filter and less protectant ($4.7 of membranes, not $12.8).
  The median of their draws is $24, and only 7% of draws come in below $17.3: almost every estimate has more room to hurt than to
  help. Neither level has been measured in meat cells (0.14 and 1.05 are the best measured there).
- **Everything else at its favourable end takes $5.6 off, to $11.7 (Engineered cells, all favourable).** A 24-hour doubling alone is
  worth $3.3. Oxygen limits the tank, at 218 g/L, with the column, 1 bar of pressure and a squat tank (2 ng cells respire more per
  gram than Humbird's 3 ng, so the tank no longer reaches the thickness limit). The median of its draws is $15, and only 10% of draws
  come in below $11.7.
- **Engineered cells, all favourable has two shares, and the demand judgement sets the gap.** With 58.5% of meat buyers picking it
  at equal price the median is 7.7% of world meat and seafood (8 in 10 draws between 3.1% and 16.2%; 15.1% at the
  most-likely-values cost, with 24.1% in the US and 31.7% in Europe). With the ordinary 14.5% the same cells give a median of 1.5%
  (0.5–5.7%; 3.2% at the most-likely-values cost). The 58.5% is the favourable end of a judgement: the literature review puts about 3%
  odds on more than 49% of all choices, about 52.5% of meat buyers (`research_notes/what_drives_choice.md`). It depends on the shape of the spread of liking
  near its middle, which no data pin (section 2).
- **Humbird's optimistic design costs about $16 (median; $13–22; $12.8 at most likely values) and takes 1.3% (0.4–4.7%; 2.7% at
  the most-likely-values cost).** It has cells with almost no waste, of 3 ng, but no tank tricks. It already uses perfusion and pays
  the same nutrient floor as Engineered cells, all favourable, which beats it on density and plant and holds ammonia at 4 mmol/L, not
  5, with lost runs.
- **Holding the cells back is the largest single cost in the Selected cells case.** Selected cells and the rungs above it use a 20 m³ tank in perfusion. A filter loop
  must clear the medium that the bleed of cells does not carry out. Its membranes cost $0.37 per litre they filter if every run
  lasts its planned 33 days, and $0.43 in the Selected cells case, where a run has a 1% chance a day of being lost. The central cells need 35 litres of medium
  a kilo at 191 g/L, so the filter clears 30 litres a kilo and the membranes cost $12.8 a kilo. Humbird's optimistic design clears
  2.8 litres a kilo and pays $1.0. A disc-stack separator on the outflow would cost $27.49 in the Selected cells case, $5.3 less, even though
  about a quarter of the cells are lost in it; its sterile price is assumed, because none was found. Nobody has held animal cells
  in perfusion above about 4 m³ (`research_notes/retention_devices.md`).
- **Cells grown as clumps could be held back without membranes, but the biology is unshown.** Aggregates of 100–300 µm settle
  30–280 times faster than single cells, so a plain settler of about 22 m² could hold Selected cells' culture back for about $4k per m³
  of tank. The Selected cells case would then cost $20.4 a kilo ($20–29 across the study's inputs) against $32.8 with the filter loop. Oxygen does
  not limit it: at the scenarios' 0.10 mmol/L an aggregate's middle keeps dividing up to about 300 µm. What nobody has shown is the
  culture. The densest aggregate culture found is about 40 g/L, for a week, in 150 mL, and every process breaks the aggregates up
  every 5–8 days. Our judgement is about 8% that aggregates hold Selected cells' 191 g/L in a 20 m³ tank for a month by 2035 (15% at
  120 g/L), so the default stays the filter loop. Edible microcarriers do not help: the beads take up the tank, which holds Selected cells
  to 26 g/L ($84 a kilo), and the product would be 90% bead by weight (`research_notes/retention_aggregates.md`).
- **The bubble protectant is a real cost.** At 2 g/L it is 22 g a kilo of cells in Humbird's optimistic design, 28 g in the best
  case and 70 g in the Selected cells case, which needs 35 litres of medium a kilo. That is $0.7, $0.8 and $2.1 a kilo at the assumed $30 a kilo
  of protectant, or $5.8, $7.2 and $18 at the catalogue price ($260). A bulk quote would settle it.
- **Company cost claims are operating cost, and the scenarios include the plant.** On operating cost alone the central cells cost
  $18.8–19.1 a kilo in a tank run as Vow runs its 20 m³ tank, a little above the $10–15 an investor reports for several
  companies. The plant charge is the difference (section 1, "Against what companies report").
- **No scenario reaches price parity with a $12 kilo of everyday meat (the US anchor).** That needs $6.1 a kilo of cells ($2.5 a
  kilo to reach the shelf and the shop's 28% margin): the shop price of a $12 kilo of everyday meat. For the world the bar is
  lower still: the volume-weighted world price is $9.43 a kilo, so the same shop price as the average kilo eaten in the world needs
  about $4.29 of cells (the US $10.93 needs $5.37; Europe's $13.63, $7.31). Engineered cells, all favourable costs $11.7 at most likely values and $12–20 across 8 in 10 draws; none of its 4,000 draws is
  at or below $6.1. No scenario uses a plant as cheap as a yeast plant, because nothing shows that animal cells can grow in one.
- **What decides it.** Each switch is moved alone from the Selected cells case ($32.8) to its best and its worst setting. The kind of cells
  matters most: −$12.7 with cells that make almost no ammonia or lactate, +$38.2 with the published cells, +$98.5 with ordinary meat cells. Next comes how the
  tank is run: in a 20 m³ batch, with Selected cells' tank design held, a kilo costs $34.6 more (with the design chosen again, $32.1 more;
  in a 100 m³ batch, $25.3 more). Then the medium price (−$1.4 at the nutrient floor, +$10.7 at $0.50 a litre), the gas the cells
  tolerate (−$1.7 at 6 mm/s, +$4.7 at 2), runs lost (−$2.5 at 0.2% a day, +$3.4 at 2%), the tank tricks (+$3.5 if none work),
  growth speed (−$2.5 at 24 hours, +$1.3 at 43) and the plant (−$2.9 with shared medium). Growth factors are inside Selected cells'
  medium price. Their switch still sets the least such a medium can cost: nothing at 30% of Humbird's price or less, +$2.5 at 60%
  and +$7.6 if all were bought at his price. The kind of cells matters most because waste sets the litres of medium a kilo, and
  each litre must also pass the filter and carries protectant; in a batch, waste sets the density instead. The switches interact,
  and the page ranks them around any scenario you choose.
- **At equal price,** once cultivated meat is familiar, 14.5% of meat buyers pick it if shoppers see it as real meat, and about 6%
  if they do not. The 14.5% is a judgement: about 5% of meat buyers picked it at first contact, and half would need the average
  shopper to end up indifferent. A worse taste lowers it to 7–10%; a value on "no slaughter" raises it to 18–27%.
- **As a company reports its process, with capital counted,** cultivated chicken costs about **$34 a kilo of cells, 4.3 times
  everyday meat** ($51 in the shop). This is SuperMeat's 2024 process for 100% cell mass, from 10-litre runs scaled on paper to
  25,000-litre tanks, with a yearly charge on the plant. The company's own figure, with depreciation only, is $29.5 a kilo. Nobody
  has peer reviewed it. With its cost and demand both drawn, the share is 0.22% of world meat and seafood (median; 8 in 10 draws
  0.06–1.0%), and 0.18% at the reported cost itself (0.5% in the US). Beef steaks are 31% of those sales, premium fillets and
  shrimp 14%, prime beef 10%, pork cuts 8%, sushi-grade fish 7%, and sheep and goat and chicken cuts 7% each.
- **Where.** In the Selected cells case, mostly beef and premium fish: beef is 47% of sales and seafood 27%. Pork is 10% and chicken 7%, sold to
  the few shoppers who like cultivated meat enough to pay about five times the price of the cut beside it. More than a quarter of
  Selected cells' sales (28%) are of products at more than four times the price of their meat. That rests on the far tail of the spread of liking,
  which is an extrapolation: the premium meats it was fitted to stop at 3.6 times. In the
  Engineered cells, all favourable every meat sells (above). A few luxury products are already within reach on price, but their markets are tiny.
- **When.** These are long-run ceilings. If nothing stalls and supply keeps up, adoption reaches 90% of the long-run share after
  21 years in the Selected cells case (14 to 46 across the speeds at which wariness fades) and 22 in the Engineered cells, all favourable case (14 to 51). The speeds come
  from durable goods; they are assumed, not estimated for a food.

**What the answer rests on** (`answer_rests_on.py`). The model has 556 inputs, 257 of them with a range. Moving
each across its range, one at a time, with each scenario's tank design held as it is: only 18 move Selected cells' or the best
case's cost by $1 or more, and 11 move Selected cells by more than $3. The rest serve side studies or tank detail. Costs in the table are
at most likely values.

| input | its range (model's value) | Selected cells, $/kg | Selected cells' share of world meat | Engineered cells, all favourable, $/kg | where the value comes from | in the uncertainty band? |
|---|---|---|---|---|---|---|
| Litres a m² of cell filter passes before it is replaced | 900–5500 L/m2 (3960) | $76.3 to $29.2 | 0.009% to 0.3% | $24.2 to $10.6 | derived from pharma runs (fouled in 4.5 days to lasted 30); no meat-cell run; probably the generous end (median about 1,500), and read with the membrane price | yes |
| Ammonia the cells tolerate in the tank | 2–8 mmol/L (4) | $57.4 to $23.3 | 0.03% to 0.6% | $18.2 to $10.7 | the evidence note's median, 3.5–4 mmol/L (80% interval 2–8): meat-relevant cells measured lose 10–55% of growth at 2.5–5, meat-cell processes hold 2–3, none measured at density | yes |
| Ammonia the cells of Selected cells make per kilo grown | 0.04–0.25 mol/kg wet (0.14) | $23.6 to $52.1 | 0.6% to 0.04% | $11.7 to $11.7 | measured once, in bovine cells with glutamine replaced (Hubalek 2023): 'more than 5-fold' below the 0.70 with glutamine | yes |
| Price of the bubble protectant (poloxamer 188), bought by the tonne | 10–120 $/kg (30) | $31.4 to $39.1 | 0.2% to 0.1% | $11.1 to $14.1 | assumed: only catalogue prices ($230–260/kg) found | yes |
| Salt strength the cells tolerate (osmolality) | 350–450 mOsm/kg (415) | $38.4 to $32.8 | 0.1% to 0.2% | $16.3 to $11.7 | CHO measurements (`perfusion_rate_osmolality.md`) | no: moves the Engineered cells, all favourable case's median by about $0.1, at forty times the computing time |
| Yearly charge on the plant's capital (financing and recovery) | 0.123–0.236 of TCI per yr (0.173) | $30.6 to $35.6 | 0.3% to 0.2% | $11.0 to $12.6 | derived from Humbird's financing, at a mature industry's rates | yes |
| Oxygen transfer the sparger keeps with antifoam present | 0.5–1 - (0.75) | $35.9 to $31.2 | 0.2% to 0.2% | $12.1 to $11.5 | judgement: reported effects range from none to half | yes |
| Dose of bubble protectant in the medium | 1–5 g/L (2) | $31.8 to $36.0 | 0.2% to 0.2% | $11.3 to $12.9 | dense pharma cultures (`gas_flow_cap.md`) | yes |
| Least medium flow the cells need for everything but ammonia and lactate | 3.7–18.5 mL per g wet cells per day (7.5) | $32.8 to $36.3 | 0.2% to 0.1% | $11.7 to $17.8 | judgement within CHO measurements | yes |
| Price of cell-filter membrane | 1050–1450 $/m2 (1450) | $29.3 to $32.8 | 0.3% to 0.2% | $10.7 to $11.7 | Humbird's ATF price; retail modules a quarter less | yes |
| Pressure at the top of the tank, where the pressure trick is used | 0.33–2 bar gauge (1) | $35.1 to $31.7 | 0.2% to 0.2% | $11.9 to $11.6 | vendor data sheets (vessels rated to 3–4 bar); no culture has been run at 1 bar | no: a design choice |
| Weight of one cell (every kind of cells since 2026-11-19) | 1000–3000 pg wet per cell (2000) | $34.2 to $32.1 | 0.2% to 0.2% | $12.1 to $11.5 | judgement between the 1.0–1.75 ng reported for chicken cells and Humbird's 3 ng | yes |
| Share of a cell's oxygen use that is upkeep, not growth | 0.31–1 of O2 uptake (0.5) | $32.2 to $34.3 | 0.2% to 0.2% | $11.7 to $11.7 | judgement from GFI and Miller 1987 | yes |
| Amino acids a kilo of cells takes up (the nutrient floor) | 0.2–0.65 kg amino acids/kg wet (0.232) | $32.8 to $34.3 | 0.2% to 0.2% | $11.5 to $14.4 | GFI's eight estimates, 200–650 g; the model takes the most efficient (`nutrient_floor.md`) | no: a trait of the cells, as glucose use is; the Engineered cells, all favourable case takes the efficient end |
| Rise in plant construction costs since 2018 | 1.17–1.4 x (1.33) | $31.9 to $33.2 | 0.2% to 0.2% | $11.4 to $11.8 | construction cost index, 2024 estimated | partly: the plant's cost is drawn, not this index |
| Density a tank reaches without perfusion | 50–150 g wet/L (120) | $32.0 to $33.1 | 0.2% to 0.2% | $11.3 to $11.9 | Humbird's fed-batch limit | **no** |
| Price of amino acids (the nutrient floor) | 5–11.59 $/kg amino acids (6.36) | $32.8 to $32.8 | 0.2% to 0.2% | $11.4 to $12.9 | GFI's feed-grade mean of 22, to low food-grade (`nutrient_floor.md`) | yes |
| Ammonia the low-waste cells make per kilo grown | 0.054–0.14 mol/kg wet (0.055) | $32.8 to $32.8 | 0.2% to 0.2% | $11.6 to $21.7 | Humbird's enhanced cell; the best measured in meat cells is 0.14 (Hubalek 2023) | no: the Engineered cells, all favourable case assumes cells that reach it |

*Left out: The gas flow the tank takes is a scenario switch (2, 4 or 6 mm/s). The input of that name is also the reference speed of Humbird's oxygen figure, so moving it alone rescales that figure ($31.2 to $35.2 in Selected cells) without changing any tank; it is left out.*
*Also left out: the settings of the scenario switches themselves (medium price, growth factors bought, runs lost, gas flow, doubling time, restart time). "What to prioritise" shows what each switch is worth.*

- **Four numbers carry most of Selected cells' uncertainty, and none has been measured on meat cells at production density.** The life
  of the cell filter ($76.3 to $29.2), the ammonia the cells tolerate ($57.4 to $23.3), the ammonia the selected cells make
  ($23.6 to $52.1) and the price of the bubble protectant ($31.4 to $39.1). The first three dwarf the rest. The filter life is
  derived from pharma runs, the tolerance is the median of an evidence note, the ammonia made was measured once, in flasks, and the
  protectant's price is assumed.
- **the Selected cells case sits at the generous end on the filter.** The evidence note (`research_notes/ammonia_tolerance_and_filter_life.md`)
  finds that small-pore fibres in dense culture last about 180–2,500 L/m², against the model's 3,960. Its median is about 1,500,
  and it puts about 20% on 3,960 being within a factor of 1.5 of the truth. Life and price go together: a membrane costs its price
  divided by its life per litre. A life of 1,500 costs nothing extra if the membrane sells at $549 a m² or less, and takes
  Selected cells to $53.8 at today's $1,450 (`filter_flux.break_even_price`). The model keeps the pair as it is on the judgement that a
  shorter life would come with a cheaper membrane; the band draws both.
- **The ammonia tolerance is the note's own median.** The meat-relevant cells measured so far (catfish ovary, 3T3 fibroblasts, pig
  muscle stem cells, bovine fibro-adipogenic cells) lose 10–55% of growth at 2.5–5 mmol/L when ammonia is added. They were
  not run at density. The note gives a median of 3.5–4 mmol/L for the cells of the scenarios, with 8 in 10 odds on 2–8. The
  scenarios use 4. At Humbird's 5, the Selected cells case would cost $27.9.
- **The bands draw all four,** and the other estimates listed under "The bands". Not drawn: the salt the cells tolerate (it moves
  the Engineered cells, all favourable case's median by about $0.1, at forty times the computing time), the pressure at the top of the tank (a design choice)
  and the traits the kind-of-cells switch holds (amino-acid uptake, the engineered cells' ammonia); the weight of a cell is drawn since 2026-11-19. The protectant's
  prior stops at $120 a kilo, about half the small-pack catalogue price ($260); that is a judgement, and a quote would settle it.
- **Each of the four is cheaper to settle by a measurement or a quote than by more modelling**: a weeks-long filter run at high
  density, the ammonia limit of a meat-cell line, the ammonia a selected line makes per kilo grown, and a tonne price for
  poloxamer.

| input | its range (model's value) | share at Selected cells' cost | share at the Engineered cells, all favourable case's cost | where the value comes from | in the uncertainty band? |
|---|---|---|---|---|---|
| Share of buyers who choose cultivated meat at equal price, once familiar | 0.03 to 0.49 of all choices (0.13) | 0.08% to 0.7% | 0.9% to 12.9% | a judgement: a third of first-contact aversion fading; the literature review puts the 10th, 50th and 90th percentiles at 2%, 10% and 35% (`what_drives_choice.md`) | yes |
| How wary people are of a novel food, in the long run | -2 to 1 utils (0) | 0.1% to 0.3% | 1.6% to 4.5% | a judgement on long-run behaviour | no: part of the share at equal price, which is drawn |
| Retailer's gross margin, as a share of the shelf price | 0.15 to 0.4 of shelf price (0.28) | 0.4% to 0.1% | 4.8% to 1.9% | US meat-department margins (28–32%) and French supermarket data | yes |
| How much more price-sensitive cultivated meat is than meat in general | 4 to 11 x (8.5) | 1.0% to 0.1% | 5.5% to 2.7% | bracketed by data on close substitutes | yes |
| Cost of assembling a cut, beyond what mince pays | 0.5 to 7 $/kg (2) | 0.3% to 0.1% | 4.0% to 1.7% | analogues, no study of cultivated meat: plant-protein extrusion, surimi forming, binder prices (`structuring_cost.md`) | yes |
| Price elasticity of meat demand | -1.4 to -0.5 elasticity (-0.9) | 0.1% to 0.7% | 2.8% to 4.8% | scanner-data meta-analysis | yes |
| Share of a cut that is plant protein, not cells | 0.1 to 0.5 kg/kg (0.2) | 0.2% to 0.6% | 2.9% to 4.0% | assumed: the cuts sold or approved so far are 10–30% cells, and no mostly-cell cut has been shown with the texture of meat (`structuring_cost.md`) | yes |
| How price sensitivity falls with income | 0 to 1 exponent (0.5) | 0.4% to 0.2% | 3.6% to 3.0% | USDA demand estimates | no: each value re-solves the demand model's calibration |

- **The demand side cannot rescue Selected cells.** At Selected cells' cost ($32.8), no single demand input moved across its range takes the
  share above 1.0%: the eight inputs span 0.08–1.0%. The low end is set by the share at equal price and the high end by how
  price-sensitive cultivated meat is. At the Engineered cells, all favourable case's cost, with the ordinary demand, the same inputs span 0.9–12.9%. There, how
  people take to a new food matters as much as the cost.
- **The share at equal price is the widest row, and it is a judgement.** There are no sales data for cultivated meat. The
  literature review puts its median at 10% and its 10th and 90th percentiles at 2% and 35% (`what_drives_choice.md`).
- **The cut is the product, and it is not yet shown.** About nine-tenths of Selected cells' sales are cuts that are 80% cells. The
  cut's cell share and its assembly cost are both drawn in the bands. Fewer cells make a cut cheaper and less liked: at half
  plant protein Selected cells' share is 0.6%, at a tenth 0.2%. Only one survey has asked shoppers about blends.
- **The shape of the spread of liking is fitted, loosely.** Its two numbers (a standard deviation of 3.9 utils and a tail of 4
  degrees of freedom) are not table rows, because across their ranges they move Selected cells only from 0.17% to 0.25% and from 0.14%
  to 0.27%. The shape matters more than that suggests: it replaced a normal spread on 2026-11-19, and Selected cells doubled.
- **Far above parity the two cross-checks disagree.** Products still dearer than their meat respond to price more strongly than
  farmed salmon did (3.6–3.7 against 1–1.5; section 2), which says the model's share falls too fast as the price rises. The
  curve anchored on premium real meats gives Selected cells 0.12% (0.04–0.24%), below the model's 0.21%, which says the opposite.
  Above about four times the price of meat there are no data at all.
- **A floor on the dollar channel.** Price enters through dollars (scaled by income) and through the ratio to meat's price, and the
  two are calibrated together. The dollar coefficient stops at zero (`market_share._derive_beta`), so a strong loss aversion cannot
  make shoppers gain from paying more.
- **Left open: dollars or ratios.** How much of the price response is in dollars and how much is a ratio to the cut's own price is
  not pinned by the data the model uses. Toward ratios, cultivated steak and fillet look cheaper, and Selected cells' share rises from
  0.18% to 0.36% across the weight's range. Each value re-solves the calibration, so it is not in the bands. It does not change
  the answer.

**For funders,** in order: cells that make less lactate and ammonia and still grow fast, which is the ladder's largest step; a
filter, or another way of holding cells back, that lasts in a dense culture; the two ammonia measurements; the price of medium at
production scale; tank tricks that clear CO₂ without bubbles; and a cheaper class of plant for animal cells. Section 6 gives the
reasons.

## 1. Cost and the price ratio

*The cases in this table are older cases kept for comparison. They are not the scenarios. Each is one fixed design with every
estimate at its most likely value. They use Humbird's engineered 3 ng cell, his ammonia limit of 5 mmol/L, medium that costs only
what the cells eat and no lost runs, unless the row says otherwise. R is the shop price against $12 meat.*

| case | cells, $/kg | R vs $12 meat | source and status |
|---|---|---|---|
| the reported process in a pharma-style plant with cells at half the density | $49.2 | 5.99 | physics-based plant cost (`floor_physics.py`) with the company's medium; nearer to reported harvests |
| **as a company reports, with a return on capital (the reported cost)** | **$34.4** | **4.27** | SuperMeat 2024; 10 L runs scaled on paper; not peer reviewed; its own figure with depreciation only is $29.5 |
| Humbird's fed-batch design, 2025 prices | $24.9 | 3.17 | a detailed design with efficient cells; not built |
| a pharma-style plant, tanks drained and refilled, first-plant financing | $19.7 | 2.57 | physics-based; efficient cells at this density not shown |
| Humbird's optimistic design with first-plant financing | $15.1 | 2.04 | the row below at 23.6% of the plant's cost a year |
| **Humbird's optimistic design (what earlier versions called the floor): a standard perfusion tank, no tricks; no clean rooms, perfusion, efficient cells, food-industry financing** | **$12.8** | **1.77** | physics-based; each piece shown separately, never together; a hollow-fibre filter loop holds the cells back, never run at 20 m³ |
| Humbird's optimistic design in a plant as cheap as a yeast plant (no scenario assumes it), buying its oxygen | **$8.3** | **1.25** | such plants exist for microbes; none built or costed for animal cells |
| rough lower bound | $3.0 | 0.63 | a bound, not a design |

**The reported cost.** SuperMeat reports 30.5 L of medium per kg at under $0.50/L, $11.8/lb ($26.0/kg) without
depreciation and $13.4/lb ($29.5/kg) with it. Its kilogram is 100% cells at a realistic weight per cell. The older cases
in this table carry a yearly charge on the plant of 23.6% of its cost (Humbird's rate: return on capital,
maintenance, insurance), so the reported cost does too: the company's running costs ($10.8/kg beyond the medium) plus
$8.3/kg, which assumes its depreciation is spread over 10 years. That gives $34.4/kg. Two cautions: it is a
company's claim, and its stated tank sizes, densities and bleed rate account for only about half of its stated
output, so the plant cost per kg cannot be checked. Humbird's independent design for efficient cells comes to
$25–46/kg in 2025 prices, and the published design analyses as a whole to about $18–65/kg with capital counted
(METHODS.md, "Other analyses").

**The cost is physics divided into engineering.** The plant's cost per kg is its cost per m³ of tank divided by
what a m³ produces in a year. Output is limited by how much oxygen and CO₂ a tank can exchange, which is set by
how much gas can be bubbled through it. Humbird's optimistic design uses 6 mm/s of gas, a rule of thumb that has not been
tested at this size and cell density. We put the odds that it works at about even, and at 5 mm/s the design would cost $13.7
(`research_notes/gas_flow_cap.md`). Plant cost per m³ comes from Humbird's design: about $910k with clean rooms, about $810k
with a sanitary hall in their place. Microbial fermentation plants are built for about $190k, which no scenario assumes
(METHODS.md, "The plant term of Humbird's optimistic design").

**Financing matters as much as engineering.** Humbird charges 23.6% of a plant's cost a year: money at 7.5%
repaid in 10 years, plus 4% maintenance and 5% insurance. That fits a first plant, and the reported cost and the two
pharma-style rows use it. His own report gives the food-processing sector's cost of capital as 5.4% and uses a
20-year life for a yeast plant; that makes the charge 17.3%. The scenarios are long-run cases set
against meat, a mature industry, so they use 17.3%. It is worth $2.3/kg in Humbird's optimistic design.

**How the tank is run matters as much as anything but the cells.** Perfusion is worth about $6/kg in Humbird's optimistic design
against tanks that are drained and refilled (the vessel grid below), and $32.1 with the Selected cells case's switches, whose batch
is held at 37 g/L by the waste mass balance. The plant-cost axis below compares the two modes on the same assumptions. Removing
clean rooms saves about a tenth of the plant cost. A plant as cheap as a yeast plant cuts the design's cost by about a third.

The medium and the plant matter most. No single lever reaches parity on its own. From the reported cost (R = 4.27): the plant
cost of Humbird's optimistic design gives R ≈ 3.30, medium at $0.20/L 3.21, and efficient cells 2.94.

```
basic product vs commodity meat ($12/kg), Monte Carlo over the cost inputs (N=20,000):
  price ratio R:   P50 = 4.20   80% CI [3.17, 5.49]   90% CI [2.91, 5.88]
  long-run share:  P50 = 0.3%   80% CI [0.1, 1.6]
  0% of draws reach parity (R ≤ 1)
```

This draw is around the reported cost, for mince against $12 meat in the US. Its share is of all choices, as `uncertainty.py`
computes it; as a share of meat buyers it would be about an eighth higher. The median R is close to the reported 4.27: the
plant-cost range is wider on the high side (reported harvests are less dense than Humbird's optimistic design assumes), while the
medium price and cell efficiency can improve on the report. It does not include the scenarios or a yeast-class plant.

**What the tricks do, and what the cells decide.** Research notes size ways round the tank's limits
(`research_notes/gas_exchange_study.md`, `waste_tricks_sizing.md`); `floor_physics.explore` carries them as
levers, and the page's panel shows each limit as a bar. Every tank trick here is a change of feed or process; the
kinds of cell are set by their traits, against the best measured in meat cells.

The settings of these tables are not the scenarios'. They run `explore()` as Humbird's optimistic design does: a tall 20 m³
perfusion tank with gas at 6 mm/s, cells of 3 ng, his ammonia limit of 5 mmol/L (the scenarios use 4), medium at $0.15 a litre and
never below what the cells eat, and no lost runs outside the brackets. Glucose comes from the cells' own balance, as in the
scenarios, for every kind of cell but Humbird's enhanced one, which keeps his figure (the two agree). So the published cells
cost $62.3 in the first table and $111.9 as row 1 of the ladder: the same ammonia and lactate yield, and 90 litres of medium a
kilo against 95, but here with a 3 ng cell, gas at 6 mm/s, cheaper medium, a higher ammonia limit and no lost runs. Read the tables for what the tricks do,
not for the cost of a kind of cell.

Each cell gives the cost per kg of cells in the food-grade plant of Humbird's optimistic design, in brackets with runs lost to
contamination at 0.2% a day (pharma's rate, 14-day restart); then the yeast-style plant, in brackets at 2.2% a day (the top of
what a survey of makers implies; 0.6% a day sits between); then the density, what binds, and litres of medium per kg.

*All tricks, all cells:*

| cells | sparger only | sparger, fat in the feed, oxygen held at 0.08 | packed column on a loop | column with oxygen sweep, 1 bar gauge |
|---|---|---|---|---|
| Humbird's enhanced cells (0.055 mol of ammonia a kilo, 0.28 lactate per glucose) | $12.8 ($13.0); yeast-style $8.3 ($9.6); 120 g/L CO₂, 11 L/kg | $12.0 ($12.2); yeast-style $8.4 ($9.8); 150 g/L CO₂, 11 L/kg | $12.2 ($12.4); yeast-style $8.5 ($9.9); 146 g/L oxygen, 11 L/kg | $10.7 ($10.9); yeast-style $8.7 ($10.3); 258 g/L thickness, 11 L/kg |
| best shown in meat cells (bovine, glutamine replaced) | $62.3 ($63.7); yeast-style $55.8 ($70.4); 154 g/L CO₂, 90 L/kg | $43.6 ($44.6); yeast-style $38.5 ($48.4); 192 g/L CO₂, 60 L/kg | $61.1 ($62.4); yeast-style $55.8 ($70.4); 187 g/L oxygen, 90 L/kg | $59.3 ($60.6); yeast-style $55.6 ($70.2); 258 g/L thickness, 90 L/kg |
| ordinary meat cells (bovine) | $88.1 ($90.0); yeast-style $83.4 ($104.9); 124 g/L CO₂, 140 L/kg | $87.2 ($89.1); yeast-style $83.5 ($105.1); 155 g/L CO₂, 140 L/kg | $87.4 ($89.3); yeast-style $83.6 ($105.2); 151 g/L oxygen, 140 L/kg | $85.9 ($87.7); yeast-style $83.8 ($105.5); 258 g/L thickness, 140 L/kg |

*With more ammonia and lactate.* Humbird's enhanced cell with ammonia at 0.14 mol/kg (the best measured in meat
cells, glutamine replaced) and lactate at 0.39 per glucose (the best measured in meat cells is 1.05), at its
24-hour doubling:

| cells | sparger only | sparger, fat in the feed, oxygen held at 0.08 | packed column on a loop | column with oxygen sweep, 1 bar gauge |
|---|---|---|---|---|
| Humbird's enhanced cells with 0.14 ammonia and 0.39 lactate | $22.3 ($22.8); yeast-style $17.8 ($21.7); 120 g/L CO₂, 28 L/kg | $21.5 ($21.9); yeast-style $17.9 ($21.9); 150 g/L CO₂, 28 L/kg | $21.7 ($22.1); yeast-style $18.0 ($22.0); 146 g/L oxygen, 28 L/kg | $20.2 ($20.6); yeast-style $18.2 ($22.4); 258 g/L thickness, 28 L/kg |
| best shown in meat cells (bovine, glutamine replaced) | $62.3 ($63.7); yeast-style $55.8 ($70.4); 154 g/L CO₂, 90 L/kg | $43.6 ($44.6); yeast-style $38.5 ($48.4); 192 g/L CO₂, 60 L/kg | $61.1 ($62.4); yeast-style $55.8 ($70.4); 187 g/L oxygen, 90 L/kg | $59.3 ($60.6); yeast-style $55.6 ($70.2); 258 g/L thickness, 90 L/kg |
| ordinary meat cells (bovine) | $88.1 ($90.0); yeast-style $83.4 ($104.9); 124 g/L CO₂, 140 L/kg | $87.2 ($89.1); yeast-style $83.5 ($105.1); 155 g/L CO₂, 140 L/kg | $87.4 ($89.3); yeast-style $83.6 ($105.2); 151 g/L oxygen, 140 L/kg | $85.9 ($87.7); yeast-style $83.8 ($105.5); 258 g/L thickness, 140 L/kg |

"Best shown in meat cells" is bovine cells with glutamine replaced: 0.14 mol of ammonia per kg and a 43-hour
doubling (Hubalek 2023); "ordinary" is the same cells with glutamine, 0.70 mol and 26 hours. Both take chicken
cells' lactate yield (1.05 per glucose taken up, Pasitka 2024). "Fat in the feed" means
the cells take all their lipid from the medium instead of making it from glucose; making lipid from glucose
gives off CO₂ without using oxygen, and on Humbird's cell that is why CO₂ made per oxygen used is 1.20 rather
than 1.0 (fed, 0.97; a carbon balance, the note's section 10). Holding dissolved oxygen at 0.08 mmol/L (38% of
air saturation, a usual pharma setpoint) in place of the 0.28 the standard tank's oxygen supply implies widens the
oxygen driving force by about a fifth; it matters only where oxygen binds.

Reading the tables (all with the filter loop, the protectant and antifoam counted): the tricks take the enhanced cells
from $12.8 to $10.7, still above the $6.1 parity mark, and in a yeast-style plant they do not pay ($8.3 with the sparger alone, $8.7 with
everything). Since the filter loop is priced, a denser culture saves less: the bleed carries out less liquid, so more passes the
membranes. With 0.14 ammonia and 0.39 lactate the enhanced cell needs 28 litres of medium per kg (ammonia sets it), and the tricks take
it from $22.3 to $20.2 ($17.8 in a yeast-style plant, sparger only). With cells that have actually been measured, waste sets the
medium and the tank tricks are worth little: every trick together takes the best meat cells from $62.3 to $59.3, 5%, against 17%
for the enhanced cells. The tricks raise the density, not the litres of medium, and for these cells the litres are most of the
cost: lactate sets them at 90 a kilo. The one tank-side change that helps them is fat in the feed, $62.3 to $43.6: cells that
take their fat from the feed need less glucose (4.3 mol a kilo falls to 2.9), make less lactate (4.5 mol falls to 3.0) and need
60 litres of medium, not 90. That assumes their lactate yield stays at 1.05 when fat is fed, which nobody has measured. The
cells decide the cost before the tank does. Losing runs at 0.2% a day adds
$0.2–1.9 per kg. At 2.2% a day in the yeast-style plant it adds $1.3–1.6 for the enhanced cells, $10–15 for the best meat
cells and about $22 for ordinary cells: a lost run loses its time, its tankful and its filter membranes, and wasteful cells
filter the most. The loss model does not yet count a failed restart, and long continuous runs are more exposed per run than short
batches.

When the cells tolerate only a capped gas flow, the cheapest combination of tank shape, column and headspace
pressure (`gas_exchange.cheapest_tricks`; the sparger runs at its cap, a squatter tank pays for its steel):

| gas cap | food-grade plant, sparger only | cheapest combination, any circulation | the same, keeping the loop within the tested passes and the safe pH exposure | yeast-style: sparger only / any / within limits |
|---|---|---|---|---|
| 1 mm/s | $57.5 | $11.08: column with oxygen sweep, the ordinary tall tank, 1 bar gauge; **94 passes** | $22.4: column for CO₂, liquid twice as deep as wide, 1 bar gauge; 6 passes | $28.6 / $8.97 / $12.1 |
| 2 mm/s | $29.5 | $10.98: column with oxygen sweep, the ordinary tall tank, 1 bar gauge; **75 passes** | $14.2: column for CO₂, liquid twice as deep as wide, 1 bar gauge; 10 passes | $15.2 / $8.41 / $8.4 |
| 4 mm/s | $15.6 | $10.79: column with oxygen sweep, the ordinary tall tank, 1 bar gauge; **43 passes** | $11.9: column for CO₂, liquid 1.3 times as deep as wide, 1 bar gauge; 12 passes | $8.6 / $8.18 / $8.2 |
| 6 mm/s | $12.8 | $10.66: column with oxygen sweep, the ordinary tall tank, 1 bar gauge; **22 passes** | $11.0: column for CO₂, liquid as deep as wide, 1 bar gauge; 10 passes | $8.3 / $8.17 / $8.2 |

Passes are tank volumes pumped through the column an hour. Dense cultures have been pumped through fibres at up
to about 15-24 an hour for weeks, at 1-4 litres (Clincke 2013; a vendor note); nothing beyond that is tested.
Culture leaving the column stays alkaline (+0.26 pH at 55 mbar) until it is back in the tank, so the share of
the culture that is alkaline grows with the passes. The safe limit used here is the 55 mbar, 0.5 m3 design that
the gas-exchange note found 3 to 6 times below an exposure that slowed CHO cells (Paul 2020). At 22 passes the
loop is 1.9 times that limit (about half the harmful exposure); at 75 passes, 6.4 times (about twice the harmful
one). **Within those limits Humbird's optimistic design depends on the gas the cells tolerate again**: $11.0 at 6 mm/s, $11.9 at
4, $14.2 at 2, $22.4 at 1. In the cells-by-tank tables above, the last column ("column with oxygen sweep, 1 bar
gauge") runs at 22 passes an hour for the enhanced cells, beyond the tested range. None of the tricks has been
tried with meat cells.

### What it would take, against what has been measured in meat cells (`scenarios.what_it_would_take`, `cell_traits.best_in_meat_cells`)

The cost of cells a long-run share needs, at the model's 14.5% of meat buyers picking cultivated meat at equal price and at 50% (no
preference), with every estimate at its most likely value; and, among the sets of traits tried (ammonia 0.14, 0.055 or 0 mol a kilo;
lactate 1.05, 0.42, 0.28 or 0 mol per mol of glucose; a doubling every 43, 36, 25.7, 20 or 15 hours; 2 ng cells; a food-grade plant
with or without shared medium; perfusion or a 20 m³ batch; the Selected cells case's other switches), the set that reaches it with
the fewest traits beyond the best measured in meat cells, then the shortest way beyond them, then the dearest. Each trait is set
against its own best measurement in meat cells: 0.14 mol of ammonia a kilo (Hubalek 2023), 1.05 mol of lactate per mol of glucose
(Pasitka 2024), a doubling every 15 hours (Stout 2023) and 3.3 ng a cell (Pasitka 2024). No odds, and no claim about how cells would
come to have a trait (until 2026-11-19 this ranked traits by the routes said to have shown them; the author had that removed):

| long-run share of world meat and seafood | with this share of meat buyers picking it at equal price | cells must cost (most likely values) | the cells tried that reach it with the fewest traits beyond the best measured in meat cells | at | traits beyond the best measured in meat cells (each against its own best measurement) |
|---|---|---|---|---|---|
| 1% | 14.5% | $19.7 a kilo or less | ammonia 0.055 mol/kg, lactate 0.42 mol/mol, a doubling every 15 h, 2 ng | $19.4, a food-grade plant, fed-batch at 20 m³ | ammonia 0.055 mol/kg wet, against 0.14 measured; lactate 0.42 mol/mol, against 1.05 measured |
| 10% | 14.5% | $4.9 a kilo or less | none of the sets tried |  |  |
| 1% | 50.0% | $29.8 a kilo or less | ammonia 0.14 mol/kg, lactate 0.42 mol/mol, a doubling every 20 h, 2 ng | $29.4, a food-grade plant, perfusion | lactate 0.42 mol/mol, against 1.05 measured |
| 10% | 50.0% | $12.9 a kilo or less | ammonia 0.055 mol/kg, lactate 0.279 mol/mol, a doubling every 15 h, 2 ng | $11.8, a food-grade plant with shared medium, perfusion | ammonia 0.055 mol/kg wet, against 0.14 measured; lactate 0.279 mol/mol, against 1.05 measured |

A 1% share is within reach of sets with two traits beyond the best measured in meat cells (ammonia 0.055 and lactate 0.42) at the
model's own liking, and one (the lactate) with half of meat buyers favouring it. A 10% share needs $4.9 a kilo of cells at the model's
own liking, below every set tried and below parity's $6.1, and, with half of meat buyers favouring it, ammonia and lactate both well
beyond the best measured in meat cells. `research_notes/cell_trait_routes.md` gives the evidence for each measurement. The draws
(`scenario_mc(choice, traits=...)`) can be run for any of these sets.

### Perfusion against fed-batch as the plant gets cheaper (`scenarios.plant_axis`)

The two ways of running the tank are compared here with the same assumptions on both sides: the same cells, plant, losses, medium
and estimates, each with its own tank design. Fed-batch's handicap is capital only: a batch held by its waste makes a fifth to a half
of the kilos a perfusion tank makes, and pays no filter. So a cheaper plant narrows the gap. The table moves the plant's cost
(buildings and tanks, not the filter loop or the column) from its modelled value down to a third of it, the bands' range:

| switches as in | $/kg with the plant at its modelled cost: perfusion / fed-batch 20 m³ / fed-batch 100 m³ | plant at 0.75× | plant at 0.5× | plant at 0.34× | fed-batch at 20 m³ is cheaper with the plant below | fed-batch at 100 m³, below |
|---|---|---|---|---|---|---|
| Published cells (rung 2's switches) | 76.7 / 201.4 / 179.5 | 74.7 / 163.7 / 147.3 | 72.7 / 125.9 / 115.0 | 71.4 / 101.8 / 94.3 | 0.13× | 0.15× |
| Selected cells (Selected cells' switches, rungs 3–4) | 32.8 / 64.9 / 58.1 | 31.0 / 53.1 / 48.0 | 29.2 / 41.4 / 38.0 | 28.1 / 33.9 / 31.6 | 0.19× | 0.23× |
| Selected cells, plant with shared medium (rung 5) | 29.9 / 49.5 / 45.0 | 28.9 / 41.7 / 38.3 | 27.9 / 33.9 / 31.6 | 27.3 / 28.9 / 27.3 | 0.28× | 0.34× |
| Engineered cells (rung 6) | 17.3 / 31.1 / 28.5 | 16.3 / 26.4 / 24.5 | 15.3 / 21.7 / 20.5 | 14.6 / 18.7 / 18.0 | 0.06× | 0.06× |
| The Engineered cells, all favourable case's switches (rung 7) | 11.7 / 15.7 / 14.6 | 11.1 / 13.5 / 12.7 | 10.5 / 11.4 / 10.9 | 10.2 / 10.0 / 9.7 | 0.36× | 0.43× |

- **With the mass balance, fed-batch wins only on a very cheap plant.** With Selected cells' switches a 20 m³ batch is cheaper than
  perfusion only below 0.19 times the modelled plant cost, and a 100 m³ batch below 0.23; with the shared-medium plant, below 0.28
  and 0.34; with the Engineered cells, all favourable case's switches, below 0.38 and 0.44. Engineered cells at 36 hours favour perfusion most (0.07): their batch
  is held at 62 g/L by the least flow a cell needs, while perfusion reaches 211 g/L.
- **This reverses an earlier reading.** Before the mass balance a batch of the Selected cells case's cells reached 56 g/L, and the same comparison
  had fed-batch winning at about half the plant's cost. At 37 g/L it needs a fifth. Which is likelier to work is a separate question:
  fed-batch at 20 m³ is shown, perfusion is not.
- **A bigger batch helps a little.** 100 m³ is about 10% cheaper than 20 m³ (`research_notes/tank_size.md`, section 10); no size
  closes the gap at the modelled plant cost.

### The frontier: every lever at its limit

Moving Selected cells' levers one at a time to the limits the research notes support, each kept moved, takes it from $32.80 to
**$7.16** a kilo. The least medium the physics allows (6.4 L/kg) is the largest step: it saves $18.64 on its own and takes
Selected cells to $14.16. Then come cells doubling in 16 hours, a food-grade plant with shared medium, runs lost at pharma's 0.2% a day
and gas at 6 mm/s. The levers share what they save, because fewer litres of medium also mean less to filter: a cheaper filter
saves $12.52 alone and nothing once the litres are cut. With antifoam counted, oxygen limits the tank, so a thicker culture adds
nothing. The frontier is about $1 above the $6.1 that parity needs.

The frontier is below the Engineered cells, all favourable case ($11.7) because it is a different thing. The Engineered cells, all favourable case puts each switch at a favourable
setting. The frontier also moves estimates to the limit the notes think physically possible: 6.4 litres of medium a kilo where the
Engineered cells, all favourable needs 14, a doubling every 16 hours where the Engineered cells, all favourable case has 24, and 0.2% of runs lost a day where the Engineered cells, all favourable case has
0.6%. No step is shown for meat cells, and the odds of all of them together are far below any single one
(`research_notes/frontier.md`).

### How far tank design can go (`design_space.py`)

The aim of tank design is a tank where CO₂, oxygen and mixing no longer bind, so that only the thickness of the culture does
(258 g/L). `design_space.py` first prices that aim (the ordinary tank with every gas limit lifted for free), then searches every
combination of the tank options the model has, 144 designs a scenario, keeping those whose column loop passes its checks.

| case | ordinary tank | the scenario's design | cheapest design, no cage | cheapest design, with a bubble cage | perfect gas exchange |
|---|---|---|---|---|---|
| Published cells, in perfusion | $111.89 (46 g/L, CO₂) | $92.17 | $64.94 (175 g/L, oxygen; 4 unproven) | $61.78 (258 g/L, thickness; 4 unproven) | **$84.85** (258 g/L) |
| 4. Selected cells | $39.18 (87 g/L, CO₂) | $32.80 | $31.40 (258 g/L, thickness; 5 unproven) | $31.09 (258 g/L, thickness; 3 unproven) | **$30.66** (258 g/L) |
| 5. Shared-medium plant | $32.85 (87 g/L, CO₂) | $29.94 | $29.27 (258 g/L, thickness; 5 unproven) | $29.04 (258 g/L, thickness; 2 unproven) | **$28.75** (258 g/L) |
| 6. Engineered cells | $20.17 (87 g/L, CO₂) | $17.27 | $16.60 (258 g/L, thickness; 5 unproven) | $16.37 (258 g/L, thickness; 2 unproven) | **$16.08** (258 g/L) |
| 7. Engineered cells, all favourable | $12.29 (108 g/L, CO₂) | $11.67 | $11.48 (258 g/L, thickness; 4 unproven) | $11.39 (258 g/L, thickness; 2 unproven) | **$11.20** (258 g/L) |

- **The search covers the cases run in perfusion** (since 2026-11-19). Rungs 1–3 of the ladder are batches held by their waste,
  which no tank design moves; the published cells are searched in perfusion as the cautious scenario, which has the old rung 1's
  switches.
- **Tank design matters most for the published cells:** $27 a kilo between the ordinary tank and perfect gas exchange ($111.89 to
  $84.85). The cheapest designs for these cells ($64.94 and $61.78) are below that ideal, because the search also lets the cells
  take their fat from the feed, which cuts their glucose, their lactate and so their medium, from 95 to 66 litres a kilo. In
  rows 2 to 4 the scenarios' designs are within $1.2–2.1 of the ideal, and in the Engineered cells, all favourable case within $0.5.
- **Designs that leave only the thickness limit exist on paper:** with a bubble cage and 1 bar of pressure, or without a cage at 2
  bar. Each needs two to five elements nobody has run with animal cells. The cage's numbers are judgements.
- **The search found one free improvement, and the scenarios now use it:** holding dissolved oxygen at half of air saturation, as
  pharma does. It is worth $0.5 a kilo in the Selected cells case.
- **After the gas limits, the litres of medium are what is left.** In the Selected cells case perfect gas exchange saves $2.1 a kilo; medium at the
  least the physics allows saves $18.6. Tables and method: `research_notes/design_space.md`.

### Cleaning and reusing the medium (`medium_reuse.py`)

After the gas limits, the litres of medium are the largest cost left. Ammonia sets them: 35 litres per kg in the Selected cells case. Can the
ammonia be taken out and the liquid reused? Partly, and the limit is the cell filter. A litre that leaves the tank costs $0.70 in
Selected cells, and $0.44 of that is the membranes that hold the cells back. A device that cleans the filtered liquid (the permeate)
and returns it saves the medium, the growth factors and the protectant, but the liquid has passed the filter either way. Only
a device that takes the waste out with no liquid drawn through the cell filter, such as dialysis across the culture, saves the
filter too.

| what sets the litres of medium (4. Plus perfusion (Selected cells): waste washed out through a cell filter) | litres per kg of cells |
|---|---|
| ammonia, held at 4 mmol/L | 35.0 |
| the least flow the cells need for everything else | 16.2 |
| lactate, within the salt limit | 21.5 |
| the nutrients, as a concentrate | 8.0 |
| leaves with the cells, unfiltered | 5.2 |

| route | fresh medium, L/kg | cleaned and returned, L/kg | through the cell filter, L/kg | cells, $/kg | saves | pays if the device costs under |
|---|---|---|---|---|---|---|
| No reuse | 35.0 | 0 | 29.8 | **$32.80** | | |
| An ammonium exchanger on the permeate, taking 38% of the ammonia | 21.7 | 13.3 | 29.8 | **$31.06** | $1.74 | (priced by its sorbent: 0.15 mol/kg at $5/kg, used once) |
| Electrodialysis of the permeate | 16.3 | 20.8 | 31.8 | **$29.92** | $2.88 | $0.18 a litre |
| Dialysis of the permeate, dialysate thrown away | 35.0 | 0.0 | 29.8 | **$32.80** | nothing | never |
| Dialysis of the permeate, dialysate cleaned and reused | 21.7 | 14.8 | 31.2 | **$31.74** | $1.06 | $0.16 a litre |
| Dialysis across the culture, dialysate cleaned and reused; the exchange membrane costs what the cell filter does | 8.0 | 30.0 | 2.8 | **$30.46** | $2.35 | $0.16 a litre |
| The same; the exchange membrane clears 10 L/m²/h, twice what the filter passes | 8.0 | 30.0 | 2.8 | **$23.88** | $8.93 | $0.38 a litre |
| *A perfect, free device on the permeate* | 8.0 | 27.0 | 29.8 | *$26.97* | *$5.83* | |
| *A perfect, free device across the culture* | 8.0 | 27.0 | 2.8 | *$15.13* | *$17.68* | |

| scenario | no reuse | exchanger on the permeate | electrodialysis of the permeate | dialysis of the permeate, dialysate reused | dialysis across the culture, at the filter's cost | the same, at twice the filter's clearance | perfect and free, on the permeate | perfect and free, across the culture |
|---|---|---|---|---|---|---|---|---|
| Cautious: the best meat cells measured so far, in perfusion | **$92.17** | $92.17 | $68.05 | $78.44 | $73.60 | $52.32 | $61.45 | $23.14 |
| 4. Plus perfusion (Selected cells): waste washed out through a cell filter | **$32.80** | $31.06 | $29.92 | $31.74 | $30.46 | $23.88 | $26.97 | $15.13 |
| 7. Plus everything else at its favourable end (Engineered cells, all favourable) | **$11.67** | $11.67 | $11.67 | $11.67 | $11.67 | $10.74 | $11.33 | $8.96 |

- **Cleaning the permeate is worth about $1–3 a kilo in the Selected cells case:** $1.7 with an ammonium exchanger, $2.9 with electrodialysis (to
  $29.92), $1.1 with dialysis if the dialysate is itself cleaned. A perfect, free device would save $5.8. A device on the
  permeate must take more than 62% of the waste from a litre in one pass before it saves anything.
- **Cleaning across the culture is worth more, and is less proven:** $2.3 if the exchange membrane costs what the cell filter
  does, $8.9 (to $23.88) if it clears twice the litres per m², as a haemodialyser does on blood for a few hours. The limit
  is $17.7.
- **For the published cells the waste is lactate, and the routes differ.** Priced in perfusion (the cautious scenario, $92.17; rung
  1 is a batch with nothing to reuse), an ammonium exchanger saves them nothing. Electrodialysis, which also takes lactate, saves
  $24.1, and the best route modelled $39.9. That still leaves them at $52, against the Selected cells case's $32.80 with no reuse.
- **The evidence is thin.** Electrodialysis took over 90% of ammonium and 99% of lactate from medium in one report, cited in a
  book and not found; dialysis held a dense CHO culture for 10 days at the bench; a reused dialysate exists only in patent claims.
  The cost of electrodialysis per litre is my arithmetic. What these devices do to growth factors and nutrients over many passes
  has not been measured.
- **Reuse does not replace better cells.** In the Engineered cells, all favourable case the cells make so little waste that the routes priced here save at
  most $0.9, and a perfect, free device $2.7.
- The model's own sorbent lever counted the filter as saved; it no longer does (no scenario used it). Sources, sensitivity and
  the experiments that would settle it: `research_notes/medium_reuse.md`.

### If perfusion cannot be run at 20 m³

The Selected cells case and the rungs above it use a perfusion tank, which nobody has run above about 4 m³. Without cell
retention a tank is held by the waste mass balance: its density is at most 1.3 times the waste level perfusion is held to, over the
waste a kilo makes. The Selected cells case costs **$65–71** a kilo in a stirred tank in fed-batch or fill-and-draw at that cap
(37 g/L), and **$88–96** at the 27 g/L reported for meat cells at 20 m³, against $32.80 in perfusion. Engineered cells, all
favourable goes from $11.67 to $14.44–15.71 at 92 g/L (or $40–44 at 27 g/L). The food-grade plant with shared medium cushions it most:
$29.94 to $47.94 (fill-and-draw, which keeps its two small seed trains). The published cells stop at 14 g/L unwashed, because of
their lactate. Re-judged at the Selected cells case's 191 g/L, a filter holding the culture for a month is about 45% possible, and
about 20% in production by 2035, a judgement the model does not use (`research_notes/no_perfusion_downside.md`).

### Against what companies report (`industry_claims.py`)

Company figures are usually operating cost (COGS): medium, labour, utilities and consumables, with nothing for the plant. Every
scenario cost here includes a yearly charge on the plant. Split the same way:

| case | cells, $/kg | of which: charge on the plant | operating cost | of which: filter membranes | medium and growth factors |
|---|---|---|---|---|---|
| 1. Published cells, fed-batch | $209.1 | $151.0 | **$58.1** | $0.0 | $22.9 |
| 2. Plus process changes | $201.4 | $151.0 | **$50.4** | $0.0 | $15.3 |
| 3. Plus cells that make less lactate, fed-batch | $64.9 | $47.0 | **$17.9** | $0.0 | $5.6 |
| 4. Selected cells (perfusion) | $32.8 | $7.7 | **$25.1** | $12.8 | $7.2 |
| 5. Plus a plant with shared medium | $29.9 | $4.5 | **$25.4** | $12.8 | $7.2 |
| 6. Plus cells that make almost no ammonia or lactate | $17.3 | $4.4 | **$12.9** | $4.7 | $3.8 |
| 7. Engineered cells, all favourable | $11.7 | $2.5 | **$9.2** | $3.7 | $2.0 |
| Humbird's optimistic design | $12.8 | $6.4 | **$6.4** | $1.0 | $2.0 |

| the Selected cells case's cells, 20 m³ tank drained and refilled (as Vow runs), in | cells, $/kg | charge on the plant | operating cost | at the 27 g/L reported for meat cells |
|---|---|---|---|---|
| the scenario's food-grade plant ($856k per m³) | $73.4 (37 g/L) | $54.6 | **$18.8** | $99.3 (operating $25.0) |
| a food-grade plant with shared medium ($476k per m³) | $49.5 (37 g/L) | $30.4 | **$19.1** | $66.7 (operating $25.3) |
| a yeast plant with what animal cells need ($246k per m³) | $34.8 (37 g/L) | $15.7 | **$19.1** | $46.6 (operating $25.3) |

| who | figure | a cost of | capital in it? | kind | checked by | date |
|---|---|---|---|---|---|---|
| [Lever VC (investor), across several companies](https://agfundernews.com/humbird-was-spectacularly-wrong-on-cultivated-meat-economics-says-report-as-vow-predicts-it-will-soon-be-unit-margin-positive) | $10–15/kg; some below $10/kg | cell mass; wet or dry not stated; scale not stated | excluded (COGS) | vetted under NDA | the investor; data not public | April 2025 |
| [Lever VC (investor)](https://agfundernews.com/humbird-was-spectacularly-wrong-on-cultivated-meat-economics-says-report-as-vow-predicts-it-will-soon-be-unit-margin-positive) | medium at $1/L or less, several under $0.50/L | medium per litre; litres per kg not stated | not applicable | vetted under NDA | the investor; data not public | April 2025 |
| [Gourmey (now PARIMA), modelled by Arthur D. Little](https://parima.bio/blog/gourmey-sets-new-cost-benchmark-in-cultivated-meat-production-with-3-4-lb-model-independently-validated) | €7/kg at 5,000 L scale; medium €0.20/L | production cost; product basis not stated | not stated | model | a consultancy, commissioned by whom not stated | May 2025 |
| [Arthur D. Little (consultancy)](https://www.adlittle.com/en/insights/viewpoints/cultivated-meat-one-year) | low €40s/kg in 2026; about €10/kg by 2030 | finished product | not stated | model | nobody named | 2025 |
| [SuperMeat (company white paper)](https://supermeat.com/wp-content/uploads/2024/11/A-Deep-Dive-Into-Cost-Effective-Cultivated-Meat-Production-V.pdf) | $29.5/kg with depreciation ($26.0 without) | 100% chicken cells, wet; 10 L runs scaled on paper to 25,000 L | depreciation only | model from runs | nobody; not peer reviewed | November 2024 |
| [Vow (company)](https://agfundernews.com/humbird-was-spectacularly-wrong-on-cultivated-meat-economics-says-report-as-vow-predicts-it-will-soon-be-unit-margin-positive) | a 20,000 L bioreactor built for “well under $1 million” | one vessel; whether piping and installation are in it not stated | a capital cost | company statement | nobody | April 2025 |

Reading it (company figures are claims; none has been audited):

- **On operating cost the model is a little above what companies claim.** Lever VC reports $10–15 a kilo of cell mass for several
  companies, some below $10. The Selected cells case's cells in a tank drained and refilled, as Vow runs its 20 m³ tank, cost
  $18.8–19.1 a kilo to operate (it was $13.4–13.7 before the waste mass balance of 2026-11-19: a batch held at 37 g/L, not 56,
  spreads the crew over fewer kilos). With cells that make almost no waste, in perfusion, the operating cost is $12.6, and Engineered cells, all
  favourable $9.3. The Selected cells case itself, in perfusion, costs $25.1 to operate, half of it filter membranes. Cells that make
  less waste than the selected ones, or a batch run to higher waste levels, would bring the batch's figure into the investor's range.
- **The difference is the plant.** A tank drained and refilled at 37 g/L makes little in a year, so the plant charge is $16–55 a
  kilo depending on what the plant costs. Company COGS leave this out. Gourmey's €7/kg does not say whether it includes it.
- **The plant's price is the number most worth checking against industry.** In a plant built like a yeast plant with what animal
  cells need ($246k per m³), the Selected cells case's cells drained and refilled cost $34.8, just above the Selected cells case in
  perfusion ($32.8), with no filter to hold the cells back. Before the mass balance this route came out below perfusion. Nobody has
  published what such a plant costs to build for animal cells; Vow says its 20 m³ vessel cost well under $1 million, without saying
  whether piping and installation are in that.
- **The density is the other open number.** The 37 g/L above is the model's waste limit for these cells. At the 27 g/L reported for
  meat cells at 20 m³ the same cases cost $47–99 a kilo, $25 of it operating cost.

### Vessel types and operating modes

A stirred tank and perfusion are not alternatives: one is a vessel, the other a way of running it. `vessels.py` changes only
those two and holds the rest (research_notes/vessels_and_modes.md has both grids, with sources).

| Humbird's optimistic design, $/kg | Batch | Fed-batch | Fill-and-draw | Chemostat | Perfusion |
|---|---|---|---|---|---|
| Stirred tank, 20 m3 | 65.35 | 19.16 | 18.76 | 34.75 | **12.81** |
| Stirred tank with a bubble cage, 20 m3 | 67.59 | 19.76 | 19.35 | 35.93 | 11.38 |
| Airlift, 20 m3 | 62.37 | 20.89 | 20.45 | 33.18 | 15.17 |
| Single-use bag, 5 m3 | 1,080 | 293.75 | 39.14 | 75.58 | 21.21 |
| Packed bed, 65 L | 3,730 | as batch | not possible | not possible | 3,726 |
| Hollow fibres, 0.5 L | 610,043 | as batch | not possible | not possible | 610,039 |

In the Selected cells case the stirred tank costs $98.86, $67.42, $73.40, $112.62 and $32.80 across the same modes (with the perfusion tank's design held; the waste mass balance since 2026-11-19). Perfusion
includes the filter loop that holds the cells back (`retention.py`); the other modes need no such device.

- Perfusion is the cheapest mode in both settings, in a stirred tank ($12.81 and $32.80) or in one with a bubble cage ($11.38
  and $31.19). Nobody has run animal cells in perfusion above about 4 m3, and nobody has run the cage with cells in suspension.
- Fed-batch and fill-and-draw, which run at 20 m3 today, cost about $19 in Humbird's optimistic design and $67-73 in the Selected cells case.
  The selected cells make more ammonia, and a culture that is not washed out stops at 37 g/L, 1.3 times the waste level perfusion is
  held to. These costs assume 37-92 g of cells a litre. Nobody has shown that density for meat cells at this size: the one 20 m3 plant for meat cells
  reports harvests of about 27 g/L.
- An airlift costs about what a stirred tank costs when waste is not washed out. In perfusion its tall shape clears less CO2.
- A stirred tank with a bubble cage (Pablo's design, 2026-11-16): an inner cylinder of fine mesh holds a strong sparger, and the cells
  live in the ring around it with soft bubbling. Only medium crosses the mesh, so the cage's gas counts at 80% of its
  strength (a judgement). In perfusion it costs $11.38 in Humbird's optimistic design and $31.19 in the Selected cells case, against
  $12.81 and $32.80 in the plain tank. Caged aeration exists only with microcarriers in small tanks.
- A single-use bag pays for a bag each run; it comes close to steel only in perfusion.
- Packed beds and hollow fibres cost thousands of dollars a kilo as built. A 20 m3 bed at a stirred tank's price, with free
  carriers, still costs $42.49 in Humbird's optimistic design: it is seeded thin and emptied every run.

## 2. What share a price buys

Shares of a single meat here are shares of meat buyers (cultivated over cultivated plus conventional, as in every reported share).
The model's inputs are set as shares of all shoppers' choices, with plant-based meat and meals without meat; that figure is given
second where a reader needs it to match the inputs.

| if cultivated meat, at equal price and once familiar… | share of meat buyers | share of all choices (the model's input) |
|---|---|---|
| tastes as good and is seen as real meat | **14.5%** (the setting; drawn between 3.4% and 55.5%, median 14.5%) | 13% (drawn between 3% and 52%) |
| tastes a little worse (0.8) / noticeably worse (0.6) | 9.8% / 6.6% | 9% / 6% |
| tastes as good, and “no slaughter” matters (0.5 / 1.0 / 1.5) | 17.8% / 21.9% / 27.1% | 15% / 18% / 21% |
| tastes as good but isn't seen as real meat | 6.2% | 6% |

At first contact it gets 4.8% of meat buyers (4.3% of all choices); the US choice experiment found 5% and 4%. For mince against
$12 everyday meat (US, long run) it gets 5.1% of meat buyers at the cost of Humbird's optimistic design (1.8 times the price),
0.37% at Selected cells' (4.1 times) and 0.31% at the reported cost (4.3 times). The share does not reach everyone as the price
falls: 27% of meat buyers at half the price of meat and 45% if free, so about 55% of meat buyers never pick it.

Checks, in shares of all choices. At equal price cultivated meat takes 11.7 points from conventional meat, 0.15 from plant-based
meat and 1.1 from meals without meat. In proportion it takes about the same from each: 13% of conventional's sales, 13% of plant-based's and 11% of the
meatless meals'. So total meat eaten, conventional and cultivated, rises by about 1.5%. The model has no switching between kinds of meat and no response of
conventional prices. The same model predicts about 15% for plant-based milk, close to reality (a weak test, since milk's inputs
are set by hand).

**A harder check, and what it changed.** Six premium animal products show what share a product takes when it is
the ordinary one plus a virtue, at a higher price:

| product (US) | price vs conventional | share of volume | model at κ = 4 | model at κ = 8.5 |
|---|---|---|---|---|
| organic milk | 1.63× | 7.0% | 25.6% | 9.8% |
| cage-free eggs (before mandates) | 1.63× | 2.8% | 25.6% | 9.8% |
| omega-3 eggs | 1.63× | 6.1% | 25.6% | 9.8% |
| organic eggs | 2.19× | 2.2% | 12.2% | 1.5% |
| organic chicken | 1.91× | 4.6% | 18.0% | 4.0% |
| all organic meat | 1.50× | 2.2% | 29.9% | 14.6% |

κ is how many times more price-sensitive a cultivated product is than meat as a whole. This table is the model with every shopper
alike, which is how κ was set, and its shares are of all choices. At 4 it over-predicted these products about sixfold. The best fit is κ = 10. The model uses 8.5,
where the typical miss is a factor of 2.6. κ acts only on cultivated meat's price difference from the conventional meat beside it,
so it moves nothing at equal price. What remains wrong: with every shopper alike the model over-predicts at small premiums and
under-predicts at large ones. Ten more products up to 3.6 times the price (below) show that share does fall with the premium,
only far more slowly than that curve. The spread of liking (below) corrects most of it.

**Shoppers differ in how much they like cultivated meat** (`liking_spread.py`, `research_notes/liking_spread.md`). The experiment
that estimated shoppers one by one found liking spread very widely. With a wide spread, the buyers left at a high price are the
keenest, so the share falls off slowly as the price rises, though each shopper is as price-sensitive as before.

- **The spread is a Student's t: a standard deviation of 3.9 utils and 4 degrees of freedom.** A shopper one standard deviation
  keener than another will pay about twice as much (2.1 times) for the same chance of buying. Against a bell curve of the same
  width, more shoppers are close to the average (77% within one standard deviation, against 68%) and more are very far from it
  (1 in 150 more than three standard deviations keener, against 1 in 740). Those few are who still buys at three or four times
  the price of meat.
- **It replaced a normal spread of 5 utils on 2026-11-19, for two reasons.** The normal fit of 2026-11-18 rested on an
  integration that was too coarse: fifteen points, which put shares off by up to 5%. Integrated properly, that spread gives a
  first-contact response to price of −1.34, not the −1.53 reported, and misses the choice experiment by 0.29, not 0.15. And a
  normal tail falls too fast: at four times the ordinary price premium real meats hold 0.6% of their category, and the normal
  spread gave 0.1%.
- **The t was fitted to three things together:** the choice experiment's response at four prices, the share sixteen premium real
  meats hold at two, three and four times the ordinary price, and farmed salmon's response to its falling price. Its joint
  misfit is 4.0, against 13.8 for the normal as it was and 8.3 for a logistic. So the experiment and the premium meats are no
  longer independent checks of the model: it was fitted to them.
- **The data pin the shape loosely.** The misfit is least at a tail of 3 and a spread of 3.7; the model's 4 and 3.9 are 10% above
  that, and 4 rather than 3 is a choice, not a fit. A mixture of two groups fits better still (2.5) and was not chosen: its best
  fit is a small block of shoppers who buy at almost any price, which nothing measured shows.
- **The Engineered cells, all favourable case fell by nearly a third, because the fitted spread is narrower in the middle.** With
  its own 58.5% of meat buyers at equal price it takes 15.1% of world meat and seafood; the normal spread it replaced would give
  21.6%. Most of its products are still one to four times the price of their meat, and what matters there is how many shoppers
  are moderately keener than average. The t puts more shoppers close to the average and fewer moderately above it. No data
  measure that part of the spread beyond the one experiment, and the shapes that fit give 15% to 18%. Selected cells went the
  other way, from 0.11% under the normal spread to 0.21%, because its sales are in the tail.
- **Three worries remain** (the note's section 6): the Engineered cells, all favourable case's fall; a response to a falling price still more than twice
  farmed salmon's; and the tail above five times the price of meat, which is an extrapolation (the premium data stop at 3.6
  times), although 15% of Selected cells' first sales come from products above five times and 28% from products above four.
  The note lists a fourth, first contact at 4.3% against a measured 5%; read as 5% of meat buyers and 4% of all choices,
  the experiment is matched (next paragraph).

What the model had been assuming about the long run, and what three readings of it give. In this table and the next, the share at
equal price and the share of a meat at each price are shares of all choices, the scale of the choice experiment and of the model's
inputs; the world shares are shares of the meat sold:

| the long run | share at equal price | share of a meat at 1.25×, 1.5×, 2×, 3×, 4× its price | world share, 1. Published cells | world share, 4. Plus perfusion (Selected cells) | world share, 7. Plus everything else at its favourable end (Engineered cells, all favourable) |
|---|---|---|---|---|---|
| first contact (as measured) | 5% | 3.6%, 2.5%, 1.4%, 0.5%, 0.2% | under 0.001% | 0.1% | 1.4% |
| novelty fades by what the model assumes | 15% | 10.8%, 7.7%, 3.8%, 1.1%, 0.4% | under 0.001% | 0.2% | 3.6% |
| shoppers indifferent on average (the premise before 2026-11-18) | 49% | 39.2%, 30.4%, 16.7%, 4.2%, 1.2% | under 0.001% | 0.7% | 12.8% |
| the model before 2026-11-18 (every shopper alike) | 49% | 28.8%, 14.6%, 2.9%, 0.09%, 0.003% | under 0.001% | 0.06% | 5.9% |
| premium real meats (the curve fitted to sixteen) | | —, 5.7%, 3.7%, 1.5%, 0.6% |  |  |  |

With every shopper alike, the fading of first-contact wariness took cultivated meat from 5% to half the market at equal price.
With the spread, the same fading (2.8 utils) takes it to 15% of all choices (about 17% of meat buyers) if the experiment's 5% is
read as a share of all choices. The model's setting stays at 14.5% of meat buyers, 13% of all choices (`equal_price_share`): read
back through the t spread it gives 4.8% of meat buyers at first contact and 4.3% of all choices, and the experiment measured 5% and
4%, so the setting reproduces both. Half of meat buyers would need the
average shopper to end up indifferent between the two meats, with the appeal of no killing outweighing the "unnatural" image.
Across the three readings Selected cells' share runs from 0.1% to 0.7% and, at the Engineered cells, all favourable case's cost, from 1.4% to 12.8%; the model
gives 0.21% and 3.2%. The long-run share at equal price is the model's largest unknown on the demand side. The bands draw it
from a distribution whose median is 14.5% of meat buyers and whose 5th and 95th percentiles are 3.4% and 55.5% (13%, 3% and 52%
of all choices). Two outside readings, both on the model's scale of all choices, bracket the setting: the literature review puts
the median at 10%, about 11% of meat buyers (`research_notes/what_drives_choice.md`), and a reading of how other foods made by
distrusted processes fared puts it near 18%, about 20% of meat buyers (`research_notes/demand_heterogeneity_evidence.md` §6). For
Selected cells the cost matters as much: across 8 in 10 of its cost draws ($26–55) the share runs from 0.4% to 0.03%.

**The model's response to price, against four measurements** (`demand_checks.py`, `research_notes/demand_checks.md`). The model
passes two and fails two. The first three rows are now what the spread was fitted to, so a pass is a fit, not a test:

| what was measured | measured | the model | the model before 2026-11-18 |
|---|---|---|---|
| Cultivated meat at first contact and equal price: own-price elasticity (choice experiment, simulated from its fitted model) | about -1.5 (-1.1 to -1.65 across its arms) | -1.37 | -3.27 |
| Share of a meat at 3 times the ordinary one's price (sixteen premium real meats, fitted) | 1.5% | 1.0% | 0.09% |
| A premium product getting cheaper: percent more volume per percent lower price (farmed salmon) | 1–1.5 | 3.6–3.7 (organic chicken, heritage pork, premium fish fillets and shrimp: the premium products still dearer than their meat) | 3.0–3.4 |
| Plant-based meat's own-price elasticity (US retail; the category is about -1.3) | -1.23 | -2.85 | -2.85 |

- **It is inside the choice experiment's range at equal price** (−1.37 against about −1.5; the arms run from −1.1 to −1.65).
- **It is on the low side of premium real meats at 3 times the price** (1.0% against 1.5%). Between 2 and 3 times the price its
  share falls with a slope of 3.1, against the premium meats' 2.2.
- **The salmon check still fails.** The model's premium products that are still dearer than their meat respond to a falling
  price at 3.6–3.7, where farmed salmon showed 1–1.5. That is half as far out as with the normal spread (5.2–7.5), and still
  more than twice the top of the measured range.
- **Plant-based meat still fails:** the model gives -2.85 against a measured -1.23. Its remaining buyers are probably a committed
  minority that a spread of liking for cultivated meat does not represent (TODO).

Once familiar, the model's response to its own price is −1.3 at equal price, −2.7 at twice the price, −3.4 at three times and
−3.6 at four times. With every shopper alike, across the single price responses the measurements could support, Selected cells' share
runs from 0.06% to 1.8%; the model gives 0.21%, and at the Engineered cells, all favourable case's cost 3.2%.

**Anchored on premium real meats** (`premium_curve.py`, `research_notes/premium_curve.md`). Ten more premium products, up to
3.6× the price (pasture-raised eggs, organic and Label Rouge chicken in France, Britain, Denmark and Switzerland), show share falling
as the premium rises: US eggs from 8.6% at 2.0× to 0.3% at 3.2×; French chicken from 13% at 1.8× to 1% at 2.7×. A curve fitted to
the sixteen products misses them by a typical factor of about 2.4, with shoppers about a quarter as price-sensitive as in the
model with every shopper alike. Placing cultivated meat on that curve, corrected for what differs from a welfare label (no killing
+5% of meat's price, novelty −30% with half of it fading, unnatural −20%; hypothetical studies), gives Selected cells **0.12%** of world
meat and seafood in the long run (0.04–0.24%), against the model's 0.21%. The curve is two-fifths below the model; the model is
inside the curve's range, near its top. At the Engineered cells, all favourable case's cost the curve gives 1.6% (0.7–2.8%) against the model's 3.2% with
Selected cells' demand: the model is about twice the curve and above its range. The premium data start at 1.5× the price, and limited
distribution holds premium labels down, so the curve is weakest near parity.

**Premium buyers, and a welfare label on the same shelf** (`premium_buyers.py`, `research_notes/premium_buyers.md`; on the model
with every shopper alike, which gives Selected cells 0.06% and the Engineered cells, all favourable case's cost 5.9%). If about 10% of shoppers were habitual premium
buyers who treat cultivated meat as a premium meat, with a welfare label at 2× beside it, Selected cells' long-run share would be 0.17%
of world meat and seafood (0.47% if they value no killing at a whole extra meat price), and at the Engineered cells, all favourable case's cost 6.52% (8.02%).
For comparison the main model, with its spread of liking, gives 0.21% and 3.16%: its tail now does for the Selected cells case more than this
group of buyers would. Cultivated meat would take 15% of its sales from the label (16% at the high value) on the logit's
proportional assumption. Nothing in this study takes Selected cells past 1%. Its premise, that buyers of organic and welfare meat are
cultivated meat's keenest buyers, is contradicted by the evidence (`research_notes/demand_heterogeneity_evidence.md`). No
setting of the model was changed by it.

**Cost falling as the market grows** (`market_size_loop.py`, `research_notes/market_size_loop.md`; every share here uses Selected cells'
demand, 14.5% of meat buyers at equal price). The membrane is priced at a pharma price ($1,450 a m²) and the plant at today's equipment prices. If a
food-grade membrane supplier appears once demand passes a million m² a year ($150 a m², then 18% cheaper for each doubling, to
$50) and the plant gets 10% cheaper for each doubling of installed tanks, cost and share can be solved together.

- **the Selected cells case comes to rest at $17.50 a kilo of cells and 1.34%** (from $32.80 and 0.21%). There is one resting point: started from
  above it also ends at $17.50. The Engineered cells, all favourable case's cells come to rest at $6.95 and 6.89% (from $11.67 and 3.16%): close to parity
  ($6.14) but not at it. Those cells, with the Engineered cells, all favourable case's own demand, reach the same lowest cost the
  two learning curves allow, $6.95, and take 30.4%.
- **The margin over the membrane switch is wide.** Selected cells' first sales, 0.21% of the world's meat and seafood, need 6.2
  times the membrane area that brings a food-grade supplier; with the plant's own learning, the Selected cells case would pass a
  switch up to about 7.5 times higher unaided. Cuts are 59% of those first sales (beef steaks 31%), premium products 32% and mince
  9%. Most of the gain is one step: later rounds add a quarter of it (24%). With slow learning there is still one resting point
  ($21.74 and 0.76%).
- **This depends on the far tail of the spread of liking.** Selected cells' first sales are what the tail decides, and the slow-learning
  result flipped three times in a day as the demand model changed. Over the whole fall shop prices fall 43% and sales rise 6.4
  times, a response to price of 3.3; the model's five premium products respond at 2.7–3.7. That is above farmed salmon's 1 to 1.5
  and inside the range of history's totals (1.3–4.1). At a response of 1.5 the Selected cells case would end near 0.5%. Anchored
  on premium real meats it ends at $18.01 and 0.72%.
- **The published cells sell too little to start.** In perfusion (the cautious scenario, $92.17) they take 0.004%, and learning
  moves their cost by under $0.4.
- The switch itself is a judgement (about 65% that such a supplier appears once demand passes a million m² a year); no price is
  published for a steam-tolerant food-grade module. The note puts about 65% on the Selected cells case passing the switch with no outside push,
  and about 20% on learning taking Selected cells above 1% (both provisional). The study changes no setting of the model.

## 3. By type of meat

Shares in this section are at most likely values, and each is a share of that meat sold (of its buyers). "Price against that
meat" is the shop price of the cultivated product over the price of the meat it sits beside. A cut costs less than mince per kilo
here, because a fifth of it is plant protein.

**Selected cells and the Engineered cells, all favourable case, world.**

| type of meat (world) | its price, $/kg | its share of all meat and seafood | Selected cells: price against that meat | Selected cells: share of that meat | Engineered cells, all favourable: price against that meat | Engineered cells, all favourable: share of that meat, shoppers favouring it (58.5% of meat buyers at equal price) | Engineered cells, all favourable: share of that meat, Selected cells' demand (14.5%) |
|---|---|---|---|---|---|---|---|
| chicken, minced or processed | 5 | 11.1% | 9.8× | 0.02% | 3.9× | 2.4% | 0.5% |
| chicken cuts | 8 | 15.1% | 5.4× | 0.09% | 2.5× | 8.5% | 1.5% |
| organic chicken | 13 | 0.1% | 3.3× | 0.3% | 1.5× | 23.4% | 3.9% |
| duck and goose, whole | 7 | 2.0% | 7.0× | 0.04% | 2.8× | 7.0% | 1.2% |
| duck and goose cuts | 10 | 0.8% | 4.3× | 0.2% | 2.0× | 15.1% | 2.5% |
| pork, processed | 6 | 13.1% | 8.2× | 0.03% | 3.3× | 4.4% | 0.8% |
| pork cuts | 9 | 13.8% | 4.8× | 0.1% | 2.2× | 11.6% | 1.9% |
| heritage pork | 16 | 0.1% | 2.7× | 0.4% | 1.2× | 34.7% | 6.3% |
| beef mince | 11.2 | 7.4% | 4.4× | 0.1% | 1.8× | 23.3% | 3.9% |
| beef steaks and cuts | 20.4 | 7.2% | 2.1× | 0.9% | 1.0× | 56.8% | 13.7% |
| prime beef and wagyu | 45 | 0.2% | 1.0× | 13.2% | 0.4× | 95.0% | 69.6% |
| sheep and goat | 14 | 4.1% | 3.1× | 0.3% | 1.4× | 31.1% | 5.4% |
| seafood, canned or minced | 7 | 6.5% | 7.0× | 0.04% | 2.8× | 7.0% | 1.2% |
| whole fish and ordinary fillets | 7 | 13.2% | 6.2× | 0.06% | 2.8× | 5.8% | 1.1% |
| premium fillets and shrimp | 20 | 3.9% | 2.2× | 0.7% | 1.0× | 48.9% | 10.5% |
| sushi-grade fish | 35 | 0.4% | 1.2× | 4.0% | 0.6× | 84.6% | 39.5% |
| rabbit | 14 | 1.0% | 3.1× | 0.3% | 1.4× | 31.1% | 5.4% |
| **all meat and seafood** | | 100% | | **0.21%** | | **15.1%** | **3.2%** |

- **Selected cells sells most where meat is dear, and a little everywhere.** Beef steaks are 32% of its sales, premium fillets and
  shrimp 14%, prime beef 10% and sushi-grade fish 8%. Pork cuts are 8%, sheep and goat 7% and chicken cuts 6%, although
  cultivated meat costs three to five and a half times as much as they do: these are large markets, and the tail of the spread of liking
  leaves about one meat buyer in 600 to cultivated meat at five times the price. It takes 0.20% of meat proper and 0.23% of
  seafood. More than a quarter of these sales (28%) are at more than four times the price of the meat, beyond the 3.6 times at
  which the premium meats behind the fit stop.
- **The Engineered cells, all favourable case sells everywhere, if shoppers favour it.** Its sales are 40% beef, 23% seafood, 15% pork, 10% chicken and 8%
  sheep and goat. It takes 8.5% of chicken cuts at 2.5 times their price and 4.4% of processed pork at 3.3 times. With Selected cells'
  demand the same cost gives 1.5% and 0.8% of those two, and the total is 3.2%, not 15.1%.

**The reported cost and Humbird's optimistic design, US.** At the cost a company reports ($34.4 a kilo of cells) and at Humbird's
optimistic design ($12.8), with Selected cells' demand:

```
                            reported cost       Humbird's optimistic design
  meat type          $/kg    R     share        R     share
  chicken mince        5   10.24    0.0%       4.25    0.6%
  chicken cuts         9    5.00    0.2%       2.34    2.4%
  beef mince          11    4.65    0.2%       1.93    4.2%
  beef steak          20    2.25    1.5%       1.05   11.3%
  prime beef, wagyu   45    1.00    8.5%       0.47   33.5%
  pork (processed)     8    6.40    0.1%       2.66    2.1%
  pork cuts           12    3.75    0.4%       1.75    4.4%
  seafood fillet      24    1.87    2.2%       0.88   13.9%
  sushi-grade fish    40    1.12    6.0%       0.53   26.7%
  TOTAL by weight: at the reported cost 0.5%, in Humbird's optimistic design 4.3%
```

At the reported cost prime beef and sushi-grade fish sell best (8.5% and 6% of their small markets), with fillets and steaks
at 1.5–2% and the other rows of the table under half a percent. In Humbird's optimistic design prime beef takes 34%, sushi-grade fish 27%,
fillets 14% and steaks 11%; beef mince takes 4%, pork 2–4% and chicken mince 0.6%. The world totals are 0.18% and 2.7%.

**What a cut costs.** A steak or fillet made from cells grown in suspension is 80% cells bound with plant protein ($2 a kilo), plus
$2 a kilo to assemble it after harvest (binding, setting, slicing, yield loss), on top of the forming and packing every product
already pays in the shop add-on. Companies have dropped growing tissue on a scaffold in a
second bioreactor; it would add about $10 a kilo. No study has costed assembly for cultivated meat, so the $2 (range $0.5–7) comes
from plant-protein extrusion, surimi forming and binder prices. The larger unknown is the cell share: the whole cuts sold or
approved so far are 10–30% cells, and no cut made mostly of suspension-grown cells has been shown to have the texture of meat. When
cells cost more than about $12 a kilo, a cut costs less than mince, because a fifth of it is plant protein. Shoppers are taken
to like a cut less than mince in proportion to the plant protein in it (METHODS.md, "Step 3"), so fewer cells are cheaper and
less liked. Selected cells' share is 0.12% if a cut is all cells, 0.21% at 80%, 0.59% at 50% and 1.4% at 30%. Both the cell share and
the assembly cost are drawn in the bands (`research_notes/structuring_cost.md`).

**With the cells that have been published.** Humbird's optimistic design assumes an efficient model cell for every species. Using
each species' published doubling time and cell size in the same plant, and for fish a lower tolerance of CO₂
(chicken and turkey cost 2.0× as much, beef 1.5×, seafood 1.6×; no data for pork), the US total in that
plant is 2.3%, not 4.3% (world 1.3%, not 2.7%; Europe 3.8%, not 6.9%). The cell data are thin (METHODS.md, "Species costs in the
market model").

**Seafood rests on an untested assumption.** Seafood fillets take 14% in Humbird's optimistic design (US). That assumes fish cells
tolerate as much dissolved CO₂ as pharma cells do. Fish live with about 2–4 mbar of CO₂ in their blood, against about 50 in
mammals, and nobody has measured how fish cells grow against CO₂. If they tolerate 50 mbar, not 100, fish cells cost $21/kg in
that plant and the fillet share falls to 7%. No shrimp cell line exists at all.

**Animals.** A tonne of cultivated meat, sold where the model says it sells, spares about 67 land animals in the Selected cells case and at the
reported cost (US), against about 250 for a tonne of the average US meat mix. A tenth of those sales are chicken, and a
chicken is where the animals are. In Humbird's optimistic design it is about 96, and in the Engineered cells, all favourable case, with shoppers favouring
it, about 120. Seafood animals are not counted. Seafood is about three-tenths of sales in the Selected cells case and at the reported cost,
about a fifth in Humbird's optimistic design and about a sixth in the Engineered cells, all favourable case (US).

## 4. By region

At the reported cost, with its cost and demand both drawn:

```
total cultivated share of meat and seafood (N=30,000), 80% CI [P10, P90]:
  region   income/cap   by VOLUME (impact)        by VALUE ($ market)
  Europe    $62k        P50  0.9%  [0.3,  3.7]    P50  1.7%  [ 0.5,  6.9]  <- easiest (rich + priciest meat)
  US        $86k        P50  0.5%  [0.2,  2.3]    P50  1.0%  [ 0.3,  4.2]
  Global    $24k        P50  0.2%  [0.1,  1.0]    P50  0.5%  [ 0.1,  1.9]
  China     $27k        P50  0.2%  [0.1,  1.0]    P50  0.5%  [ 0.1,  2.5]
  Brazil    $22k        P50  0.1%  [0.0,  0.4]    P50  0.1%  [ 0.0,  0.6]
  India     $11k        P50  0.0%  [0.0,  0.2]    P50  0.1%  [ 0.0,  0.4]
  Nigeria    $6k        P50  0.0%  [0.0,  0.1]    P50  0.0%  [ 0.0,  0.1]  <- hardest (cheap meat + price-sensitive)
```

Dear meat and rich shoppers make Europe easiest; cheap meat and price-sensitive shoppers make low-income regions
hardest. To two decimals the world median is 0.22% (8 in 10 draws 0.06–1.0%). At the reported cost itself the shares are
0.18% for the world, 0.9% for Europe and 0.5% for the US. The band draws the share at equal price, κ from 4 to 11, and plant
costs from the plant term of Humbird's optimistic design to a pharma-style plant at half the density. World beef and world
seafood are priced by who eats them (METHODS.md, "World beef price" and "World seafood prices").

| the two headline cases | world | US | Europe |
|---|---|---|---|
| Selected cells: median of draws (8 in 10 between) | 0.17% (0.03–0.9%) | 0.4% (0.09–2.0%) | 0.7% (0.14–3.2%) |
| Selected cells: at the most-likely-values cost | 0.21% | 0.6% | 1.0% |
| Engineered cells, all favourable, shoppers favouring it: median of draws (8 in 10 between) | 7.7% (3.1–16.2%) | 13.6% (6.8–24.2%) | 19.5% (11.0–30.8%) |
| Engineered cells, all favourable, shoppers favouring it: at the most-likely-values cost | 15.1% | 24.1% | 31.7% |
| Engineered cells, all favourable, Selected cells' demand: median of draws (8 in 10 between) | 1.5% (0.5–5.7%) | 2.6% (0.8–9.3%) | 4.1% (1.3–13.7%) |
| Engineered cells, all favourable, Selected cells' demand: at the most-likely-values cost | 3.2% | 4.9% | 7.8% |

Against sushi-grade salmon, a structured product at the reported cost is at or below parity in 37% of draws (median R 1.08). How
much of a cut can be cells, and what assembling it costs, are unmeasured.

## 5. Entry points, and timing

At the reported cost, a few luxury products are already within reach on price when compared at their everyday grade (farmed
salmon, crossbred wagyu): foie gras, bluefin tuna, sea urchin, wagyu. Lobster is close (R ≈ 1.1). Each is a small market.
Commodity pork and chicken, where the volume is, stay above parity even in the Engineered cells, all favourable case. Foie gras stands out: unstructured,
expensive, and increasingly banned on welfare grounds.

From a near-zero start, cultivated meat reaches 90% of its long-run share after 21 years at the reported cost and in Selected cells
(14 to 46 across the plausible speeds at which wariness fades), 24 in Humbird's optimistic design (14 to 55) and 22 in the
Engineered cells, all favourable (14 to 51). This
assumes that nothing stalls and that supply keeps up. The rollout speeds are the usual ones for durable goods, so the years are
assumed, not estimated; history puts the chance of a stall at roughly one in three (METHODS.md, "How fast"). Current wariness
(surveys: 5–60%) sets the speed, not the ceiling.

## 6. What to fund

Costs here are at most likely values. The swings are from "What the answer rests on" and "What decides it" in the Summary.

1. **Cells that make less lactate and ammonia, and still grow fast.** This is the ladder's largest step: $136.5 a kilo in a 20 m³
   batch, from $201.4 to $64.9, almost all of it from lower lactate ($126.4); in perfusion it would be $43.9. Cells that make almost no ammonia or lactate are worth another $12.7 from the Selected cells case, by whatever route they come (`research_notes/cell_trait_routes.md`). Low waste and fast growth
   have each been shown, never together in one culture. A culture that does both, with the glucose taken up and the lactate and
   ammonia made reported per kilo of real cells, is the single most useful measurement. The published cells' glucose is derived
   from their energy balance here, because nobody has reported it on the low-waste feed.
2. **A way to hold cells back in large tanks, and a filter that lasts.** Nobody has run animal cells in perfusion above about
   4 m³. It is worth $32.1 a kilo with the Selected cells case's traits (row 3 to row 4). Every scenario from the Selected cells case on prices a hollow-fibre filter loop whose membranes have never filtered a culture this thick for a month.
   Membranes are Selected cells' largest cost ($12.8 of $32.8), and the filter's life moves Selected cells between $29 and $76. A weeks-long
   run at high density, and a price for a food-grade membrane, would settle most of it.
3. **The two ammonia numbers:** how much ammonia meat cells tolerate at density ($23 to $57 in the Selected cells case across its range) and how
   much the selected cells make per kilo grown ($24 to $52; measured once, in flasks).
4. **The price of medium and of the bubble protectant at production scale:** verify the $0.20 a litre reports and what is in the
   medium, on a stated mass basis. Medium at $0.50 adds $10.7 to the Selected cells case. A tonne quote for poloxamer 188 would settle $31 to $39.
5. **Tank tricks that clear CO₂ without bubbles** (a column on a pumped loop, pressure, recycled oxygen) and **the gas flow cells
   tolerate:** calculated, never tried with meat cells. Without the tricks the Selected cells case costs $3.5 more in a tank of the same shape and
   $6.4 more in the ordinary tall tank. For the published cells in perfusion they are worth $18.7; in a batch, nothing.
6. **A cheaper class of plant for animal cells:** a food-grade plant with shared medium (no clean room, shared medium line, bought
   oxygen) is worth $2.9 a kilo in the Selected cells case, and nobody has built one. A plant as cheap as a yeast plant is not counted: nothing
   shows animal cells can be grown that way.
7. **Contamination is not the main obstacle to a cheaper plant, on this model:** the food-grade plant with shared medium stays
   cheaper than a sterile one until it loses a run per tank about every 32 days (3.1% a day). Measured loss rates in food-grade
   tanks would test this.
8. **How much of a cut can be cells, and whether shoppers accept a blend:** cuts sold today are 10–30% cells. Whether a steak or
   fillet can be mostly suspension-grown cells, with the texture of meat, sets most of what a cut costs and how shoppers see it.
   Across the cell share's range Selected cells' share runs from 0.2% to 0.6%. The cost of assembling a cut is unmeasured too ($0.5–7
   a kilo beyond mince).
9. **How shoppers respond once they can buy it:** the share at equal price is a judgement (14.5% of meat buyers, drawn between
   3.4% and 55.5%). The
   spread of liking is fitted to one choice experiment, sixteen premium meats and farmed salmon, and it decides both ends of the answer: its
   tail gives Selected cells its sales and its middle sets the Engineered cells, all favourable case. Repeat-purchase data from the first markets, at known prices,
   would replace both.
10. **Open, comparable data:** cost claims per kg of dry matter or protein, with capital included (METHODS.md, "A
   checklist for cost claims"). Most published analyses leave out all or part of the cost of capital.

A meat tax also works: raising conventional prices 25% lowers R as much as a 20% cut in every cost. Most of these
are public goods that industry underfunds.

**The one working plant.** Vow grows animal cells in a food-grade 20,000-litre tank with no clean room,
drained and refilled, at an output that implies about 27 g of cells per litre. Reconstructed in the model, that
operation costs about $31/kg in a yeast-style plant and $74/kg in a food-grade plant at Humbird's cost, so the cheap
class of plant is probably what it runs. It shows that food-grade tanks work for short runs. It does not show
the density or the weeks-long perfusion runs the scenarios assume (METHODS.md, "A working plant as a reference
point").

**How the physics fares against reported runs.** Fed the cells and vessels of published runs, the model is
conservative about how dense a culture a vessel can hold (a small vessel has held twice its limit), and optimistic
about medium (real perfusion runs used 1.2 to 2.8 times more) and about output in practice (the one working
20 m³ plant makes under half of what the model's efficient cells would). It also flags two reports whose own
numbers do not add up (METHODS.md, "Back-test against reported runs").

## 7. What would change the conclusions

- **Up:** a meat-cell line shown to make little lactate and ammonia while doubling in 36 hours or less, with a full mass balance;
  perfusion at 20 m³ with a filter that lasts a month in a dense culture, or a cheaper way to hold cells back; medium at
  $0.20 a litre or less confirmed at scale with its growth factors; animal cells grown in a plant built like a microbial
  fermentation plant; shoppers who come to favour cultivated meat, which is worth more than any cost in the Engineered cells, all favourable case.
- **Down:** a filter life near the evidence note's median (1,500 L/m²) with membranes still at pharma prices (Selected cells $53.8);
  cells that tolerate 2 mmol/L of ammonia, not 4 (Selected cells $57.4); perfusion failing at 20 m³ (the Selected cells case $65–96); cuts that cannot
  be mostly cells; frequent contamination with slow restarts (METHODS.md, "Losing runs"); the reported figures not surviving
  review or scale-up.
- **Demand is the weakest part, at both ends.** The share at equal price is a judgement with no sales data behind it. The spread
  of liking was refitted on 2026-11-19 as a Student's t, to one choice experiment, sixteen premium products and farmed salmon
  together, so those are no longer independent checks. Its tail, above about four times the price of meat, is an extrapolation
  that carries more than a quarter of Selected cells' sales. Its middle, which no data pin, sets the Engineered cells, all favourable case: 15.1% here, 21.6% under the normal
  spread it replaced. The model still responds to a falling price more than twice as strongly as farmed salmon did (3.6–3.7
  against 1–1.5). Selected cells' share is 0.17% at the median and 0.21% at most likely values; the cross-check anchored on premium
  meats gives 0.12% (0.04–0.24%). In 8% of Selected cells' draws the share is above 1%.
- **What rests on one source.** The reported cost is one company's report, with a capital charge that assumes a
  10-year depreciation period (20 years would add $8/kg). The scenarios' plant costs are one engineer's design
  (Humbird 2021) in 2025 prices. The ammonia the low-waste cells make is one paper's flask measurement (Hubalek 2023). None has
  been reproduced.
- **The cells' glucose is derived, not measured.** The published cells' $209 in a batch ($112 in perfusion) follows from a lactate yield measured in chicken
  cells and a glucose need computed from the model's own oxygen use. A cell on the low-waste feed may ferment less than that. A
  measured glucose and lactate balance for such a cell would move rows 1 and 2 by tens of dollars; the Selected cells case would not move unless
  its cells made more than about 0.6 mol of lactate per mol of glucose.

Figures: `python report_figures.py` (cost vs inputs, cost waterfall, share tornado, share vs price, timing paths,
penetration by type and region). Parameters and sources: `python inputs.py`.
