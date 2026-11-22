# Cultivated meat: how far can it get? Results

*These are the findings of a cost and demand model. The scenarios (`scenarios.py`) describe what has to go right for the cost to
fall. They use physics and published plant costs (Humbird 2021). One more row gives the cost a company reports for its own process
(SuperMeat 2024). The [interactive explorer](https://pabloamc.github.io/Cultivated_meat/interactive.html) explains the
method in plain language and lets you change every assumption. [METHODS.md](METHODS.md) has the code-level detail.
Everything below reproduces from the code.*

## Summary

*Last revised 2026-11-21. What changed, and when, is in [CHANGELOG.md](CHANGELOG.md).*

**The answer.** With the best meat cells in the published record, grown as they are grown today (in batches, in a 20 m³ tank), a
kilo of cells costs **$316.1** at most likely values; if the unmeasured estimates are drawn from their ranges, the middle draw is
$337 and 8 in 10 fall between $235 and $475. That is about 37 times the shop price of US minced beef or pork cuts ($12 a kilo), and
cultivated meat takes under 0.001% of world meat and seafood. What it would take to matter:

| long-run share of world meat and seafood | with this share of meat buyers picking it at equal price | cells must cost (most likely values) | the cells tried that reach it with the fewest traits beyond the best measured in meat cells | at | traits beyond the best measured in meat cells (each against its own best measurement) |
|---|---|---|---|---|---|
| 1% | 14.4% | $18.3 a kilo or less | ammonia 0.055 mol/kg, lactate 0.279 mol/mol, a doubling every 15 h, 2 ng | $15.7, a food-grade plant with shared medium, fed-batch at 20 m³ | ammonia 0.055 mol/kg wet, against 0.14 measured; lactate 0.279 mol/mol, against 1.05 measured |
| 10% | 14.4% | $3.7 a kilo or less | none of the sets tried |  |  |
| 1% | 50.0% | $28.4 a kilo or less | ammonia 0.055 mol/kg, lactate 0.42 mol/mol, a doubling every 15 h, 2 ng | $24.1, a food-grade plant with shared medium, perfusion | ammonia 0.055 mol/kg wet, against 0.14 measured; lactate 0.42 mol/mol, against 1.05 measured |
| 10% | 50.0% | $11.4 a kilo or less | ammonia 0 mol/kg, lactate 0 mol/mol, a doubling every 15 h, 2 ng | $9.7, a food-grade plant with shared medium, perfusion | ammonia 0 mol/kg wet, against 0.14 measured; lactate 0 mol/mol, against 1.05 measured |

- **A 1% share needs cells at about $19 a kilo** with the model's 14.4% of meat buyers picking cultivated meat at equal price, and
  about $29 if half of meat buyers did. Among the sets tried, each is reached only with two traits beyond the best measured in meat
  cells: ammonia at 0.055 mol a kilo (0.14 measured) and lactate at 0.28 mol per mol of glucose (1.05 measured) for the first, in
  a 20 m³ fed-batch in a food-grade plant with shared medium; the same ammonia with lactate at 0.42 for the second, in perfusion.
- **A 10% share needs cells at $4.1 a kilo at 14.4% of meat buyers**, below every set of traits tried, and below the $6.1 of parity
  with a $12 kilo of US minced beef or pork cuts. At 50% of meat buyers it needs $12.0, which among the sets tried only cells that
  make no ammonia and no lactate at all reach ($11.6).
- **The table says what has been measured, not how cells would get there.** For each trait the best value measured in meat cells is
  0.14 mol of ammonia a kilo (Hubalek 2023, bovine fat-precursor cells fed without glutamine), 1.05 mol of lactate per mol of glucose
  (Pasitka 2024, chicken fibroblasts in perfusion), a doubling every 15 hours (Stout 2023, immortalised bovine muscle cells, with serum)
  and 3.3 ng a cell (Pasitka 2024, chicken cells, from their density); `cell_traits.best_in_meat_cells`. Each trait is set against its
  own best measurement. Nothing here says how cells would come to have a trait.

The reference points, each defined by its cells' traits and the plant and process around them (`scenarios.py`), are in the table
below. The low-lactate example means cells that make 0.14 mol of ammonia a kilo (the published figure) and 0.42 mol of lactate per
mol of glucose (the best published is 1.05), double every 36 hours and weigh 2 ng, grown in perfusion in a 20 m³ tank in a
food-grade plant with medium at $0.20 a litre. A kilo costs **$48.7** at most likely values (middle draw $52; 8 in 10 between $39
and $76), and at that cost cultivated meat takes **0.05%** of world meat and seafood (middle draw 0.05%; 8 in 10 between 0.009% and
0.3%).

The all-favourable example (`scenarios.all_favourable`) is the one most favourable case: every lever at its most favourable value
among this model's own favourable end, Humbird's design (2021) and nine other published cost studies, taking no study value that
breaks one of the model's limits (`study_assumptions.py`, `research_notes/study_comparison.md`). Lever by lever it is no worse than
Humbird's design or any published study that respects those limits. Its cells weigh 3 ng, make 0.054 mol of ammonia a kilo and
0.28 mol of lactate per mol of glucose, double every 16 hours and tolerate 5 mmol/L of ammonia and 50 of lactate. They grow in
perfusion in 42 m³ tanks, in a food-grade plant with shared medium, with medium at the cost of its nutrients, no growth factors
bought, no lost runs and dialyser-grade hollow fibres holding the cells back; its tank holds the culture at 219 g/L, the densest at
which its loop that strips CO₂ and feeds oxygen passes its checks; 58.6% of meat buyers pick it at the same price. It
costs **$7.0** ($6.97) at most likely values (middle draw $8.3; 8 in 10 between $7.1 and $10.0; most draws cost more than the
point, because several unmeasured estimates can be much worse than likely and only a little better: `research_notes/model_audit.md`
section 3f) and at that cost takes **23.4%** of world meat and seafood with that 58.6% of meat buyers (middle draw 17.4%; 8 in 10
between 10.7% and 26.3%), or 5.6% at the ordinary 14.4% (middle draw 3.9%; 1.4–12.7%). No case reaches price parity with a $12 kilo of US minced beef or pork cuts at most likely values:
that needs about **$6.1** a kilo of cells, and the all-favourable example's mince sells at 1.10 times the price (the world's meat
and seafood, at a volume-weighted $9.43 a kilo, needs about $4.29). The cost rests on a handful of numbers, and the weakest of them
have never been measured on meat cells ("What the answer rests on", below).

**What changed in the second batch of 21 November** (CHANGELOG.md; `research_notes/humbird_backtest.md` items 11-12,
`research_notes/two_spargers_and_loop.md`). Each figure is the cost before and after, for Humbird's optimistic design; Published
cells; the low-lactate example; the all-favourable example.

1. The back-test of Humbird's perfusion design: the building's power follows its floor and the class of each building (his Table
   3.2: a sanitary hall draws 50 W per m², a clean room 410), and part of the crew is counted per tank, as he counts it. His
   perfusion design's growth factors, labour and utilities were +62%, −42% and −54% against his table; now −4%, 0% and −27% (the
   rest is 13.5 L a kilo of process water his report does not itemise). $15.93 → $15.72; $322.55 → $316.11; $49.50 → $49.22;
   $7.62 → $7.42.
2. In a tank that is not washed out, the least medium flow stands for by-products that build up and may end a batch 1.3 times
   above their level, as ammonia and lactate may. It capped Humbird's fed-batch at 92 g/L and added $6.4 to his best estimate;
   now it does not bind it. His best estimate with the model's additions: $37.38 → $30.49 (the page's start, $26.99, is unchanged).
3. The tank design search holds a culture thinner when its CO₂ loop fails its checks at full density. The loop that also feeds
   recycled oxygen, held at the densest culture it passes, is now the cheapest design in every perfusion case: the low-lactate
   example at 168 g/L ($49.22 → $48.68), the all-favourable example at 219 g/L ($7.42 → $6.98), Published cells in perfusion
   $185.09 → $181.13.
4. Two new levers, off at the start: a second, fine-bubble sparger for oxygen, and the CO₂ column on the filter loop sharing its
   pump. Two spargers save nothing once the oxygen-feeding loop is chosen; the column on the loop saves $0.01-0.06 and the
   all-favourable example takes it ($6.98 → $6.97).
5. The glucose in the nutrient floor is the mass balance's (0.311 kg a kilo, not 0.32): $2.0035 → $1.9999 (still $2.00).
6. The plant ladder's fill-and-draw rows are `explore()` itself; the cautious end of the default's plant range is $20.3 (was $17.7)
   and the plant knob's range $13.5-37.1 (was $13.8-34.0).
7. Together: Humbird's optimistic design $15.72 (was $15.93); Published cells $316.1 (was $322.6); the low-lactate example $48.68
   (was $49.50; share 0.05%); the all-favourable example $6.97 (was $7.62; share 24.7% with its own demand, was 22.6%; 23.4% since the fourth batch of 2026-11-21); the
   nutrient floor $2.00.

**What changed on 20 and 21 November** (CHANGELOG.md, METHODS.md), before the second batch. Each change was undone alone in the code; in brackets is the cost
now less the cost with it undone, for Published cells; the low-lactate example; the all-favourable example as it now stands.

1. The scenarios' cells tolerate 35 mmol/L of lactate, not Humbird's 50 (+$95.4; nothing; nothing, since the all-favourable example takes his 50).
2. Bursting bubbles kill cells, charged on the gas the cells meet, and the dead are not harvested (+$3.2; +$4.0; +$0.4). 2% of the cells are lost at harvest (+$6.5; +$1.0; +$0.2).
3. Membranes last 2,415 litres a m², Humbird's own replacement schedule, not 3,960 (nothing; +$8.7; nothing).
4. A thick culture takes up oxygen more slowly, so the low-lactate example runs at 154 g/L, not 191 (nothing; +$1.8; +$0.7).
5. A perfusion tank takes twice the fed-batch crew (nothing; +$1.8; +$0.7); medium-preparation equipment grows with the medium passed (nothing; +$1.7; +$0.3).
6. Plant items are charged per tank as well as per m³ (nothing; −$0.1; −$0.1), so larger tanks now save 5–7% (section 1). The back-test against Humbird's tables also reset growth factors, utilities and the crew, and six defects were fixed; these replaced code and cannot be undone one at a time.
7. The all-favourable example is now one case, with Humbird's levers and published studies' where they are more favourable: $7.6, against $11.7 for the example of that name on 19 November.
8. Demand: plant-based meat's anchor is 0.4% of meat by volume, not 1.2%; incomes are nominal; conventional meat's price falls as it loses sales; markets closed by law take none, weighted by meat eaten (1.14% of the world). In world share points, for the low-lactate example and the all-favourable example: −0.003 and −0.8; +0.003 and +0.2; nothing and −3.9; −0.001 and −0.2.
9. Cleaning the medium and maturation are levers, off by default. The page opens on Humbird's best estimate as he counts it, $26.99 in 2025 dollars ($21.00 in his 2018 dollars), with what this model counts and he does not as levers.
10. Together: Published cells cost $322.6 (was $209.1 on 19 November), the low-lactate example $49.5 (was $32.8; share 0.05%, was 0.21%) and Humbird's optimistic design $15.9 (was $12.8).

Earlier changes (19 November and before) are in CHANGELOG.md.

> **What the words mean**
>
> - **Cost** is per kilo of real cells, which are about 70% water and 20% protein, like meat. It is per kilo harvested: the cells
>   that bubbles kill and the 2% lost at harvest are paid for by the kilos that are sold. Costs are in 2025 dollars.
> - **Share** is cultivated meat's share of all meat and seafood sold, by weight, in the long run: once it is on every shelf and
>   no longer feels new. It is not a forecast of when. Seafood is about a quarter of that total. A fifth of a cultivated cut is
>   plant protein, and the share counts the whole cut. For each product it is cultivated over cultivated plus conventional meat.
>   Markets closed to cultivated meat by law (1.14% of the world's meat, weighted by meat eaten; 10.2% of the US) take none, and
>   conventional meat's price falls as cultivated meat takes its sales.
> - **Share at equal price.** Of the shoppers who buy meat, the share who would pick cultivated meat when it costs the same as the
>   meat beside it and is familiar: **14.4% of meat buyers**, in every case but one; 50% would mean no preference either way.
>   The all-favourable example takes 58.6%. It is a judgement, not a measurement, and the bands draw it. A lower price does not win
>   everyone: for mince against US minced beef or pork cuts at $12 a kilo, 27% of meat buyers pick cultivated meat at half the price
>   and 45% if it were free, so about 55% never pick it at any price. The model itself works with all shoppers' choices among meat,
>   cultivated meat, plant-based meat and no meat. There the same setting is 13% of all choices, the figure the inputs use.
> - **At most likely values** puts every estimate at its single most likely value. It is the figure given first for every case,
>   and the one the page shows at the settings shown. Steps of the ladder and the side tables use it, so that they can be
>   subtracted from one another.
> - **The draws.** For each case, 4,000 draws vary the estimates nobody has measured. "The middle draw" is their median, and "8 in
>   10 between" is their 10th to 90th percentile. Cost, shop price and share are all drawn this way, and given right after the
>   figure at most likely values. The middle draw of the cost is above the cost at most likely values, because most estimates have
>   more room to fall short than to improve: 39% of the low-lactate example's draws and 8% of those of the all-favourable example
>   come in below it.

| scenario | cells, $/kg: median of draws (8 in 10 between) | $/kg if every estimate lands on its most likely value | shop price against US minced beef or pork cuts ($12 a kilo), at the median | share of world meat and seafood, long run: median of draws (8 in 10 between) | share at the most-likely-values cost | cell traits set beyond the best measured in meat cells |
|---|---|---|---|---|---|---|
| 1. Published cells: the best meat cells in the published record, grown in batches in a 20 m³ tank | **$337** ($235–475) | $316.1 | 39.3× | **under 0.001%** | under 0.001% | none |
| 2. Plus process changes and cheaper inputs | **$322** ($223–458) | $304.8 | 37.6× | **under 0.001%** | under 0.001% | none |
| 3. Plus cells that make less lactate (0.42 mol per mol of glucose) and double every 36 hours, still in batches | **$77** ($53–114) | $70.3 | 9.1× | **0.01%** (0.002–0.09%) | 0.01% | lactate |
| 4. Plus perfusion (the low-lactate example): waste washed out through a cell filter | **$52** ($39–76) | $48.7 | 6.3× | **0.05%** (0.009–0.3%) | 0.05% | lactate |
| 5. Plus a food-grade plant with shared medium | **$48** ($35–71) | $44.5 | 5.8× | **0.07%** (0.01–0.3%) | 0.06% | lactate |
| 6. Plus cells that make almost no ammonia or lactate (0.055 mol a kilo; 0.28 mol per mol of glucose) | **$33** ($25–45) | $27.3 | 4.1× | **0.2%** (0.05–0.9%) | 0.3% | ammonia, lactate |
| 7. Plus everything else at its favourable end (the all-favourable example) | **$8** ($7–10) | $7.0 | 1.3× | **17.4%** (10.7–26.3%) | 23.4% | ammonia, lactate |
| Humbird's optimistic design: his enhanced cells in an ordinary perfusion tank | **$22** ($17–29) | $15.7 | 2.8× | **0.7%** (0.2–2.6%) | 1.4% | ammonia, lactate |
| As a company reports (SuperMeat 2024) | **$34** (its own point figure) | $34.4 | 4.3× | **0.2%** (0.05–0.8%) | 0.2% | a company's own report |

**The steps between the reference points.** The first seven rows change one kind of thing at a time, from what has been shown to
every setting at its favourable end. They explain what each change is worth; they are not a path anyone must follow, and the order
says nothing about which route gets the cells there. In this section every cost is at most likely values unless it says "middle
draw", so that the steps can be subtracted; the table gives both.

- **Row 1, Published cells ($316.1).** The cells are not one cell line. They combine the best published figure for each trait, never
  measured together in one line: ammonia (0.14 mol a kilo) and a 43-hour doubling from primary bovine fibro-adipogenic progenitor
  (fat-precursor) cells fed alpha-ketoglutarate in place of glutamine (Hubalek et al. 2023, Mosa Meat and Maastricht University,
  spinner flasks, five donors); lactate (1.05 mol per mol of glucose) from chicken fibroblasts in perfusion (Pasitka et al. 2024,
  Believer Meats); a cell mass of 2 ng (chicken cells are reported at 1.0–1.75 ng and about 3.3 ng; Humbird assumed 3 ng); and glucose
  from the cells' own balance. Companies may hold better cells they have not published. They are grown as a fed-batch in an ordinary
  20 m³ tank, the mode and size pharma runs and Upside Foods reports (`research_notes/vessels_and_modes.md`, section 11). Medium
  costs $0.30 a litre, between the $0.20 companies announce and the $0.50 one company reports.
- **Row 2, Plus process changes and cheaper inputs ($304.8).** The same cells and mode. Medium at the announced $0.20 a litre and
  growth factors at 30% of Humbird's price; more gas, the tank tricks and a faster restart do nothing for a batch held by its waste.
- **Row 3, less lactate and faster growth ($70.3).** Cells that make 0.42 mol of lactate per mol of glucose and double every 36
  hours, grown in a 20 m³ batch.
- **Row 4, the low-lactate example ($48.7).** The same cells in perfusion.
- **Row 5, Plus a food-grade plant with shared medium ($44.5).** Its two small seed trains serve only long runs, so it follows
  perfusion; a fed-batch plant with shared medium keeps Humbird's full seed train.
- **Row 6, almost no ammonia or lactate ($27.3).** 0.055 mol of ammonia a kilo and 0.28 mol of lactate per mol of glucose, the
  metabolism of Humbird's efficient cell, at 2 ng a cell, doubling every 36 hours, with $0.20 medium.
- **Row 7, the all-favourable example ($7.0).** Every lever at its most favourable value, as above. It takes the favourable end of
  demand too: once cultivated meat is familiar, 58.6% of meat buyers pick it at equal price, against 14.4% in every other row.

**Why this order.** Each row needs nothing from the one after it, and the early rows need the least that is new: fed-batch at 20 m³
is shown, cheaper inputs need no new biology, and perfusion at 20 m³ has not been run with animal cells. The shared-medium plant
comes after perfusion because its saving on seed trains needs long runs. Perfusion is worth $21.6 a kilo with the low-lactate
example's traits (2026-11-21; it was $22.3).

An announced or reported medium price is taken to include its growth factors (`growth_factors_in_medium_price.md`), so no row
with such a medium buys growth factors on top. Humbird's optimistic design is not a row of the steps: it assumes cells with almost
no waste (Humbird's 3 ng cell) and none of the tank tricks. The path from it to the all-favourable example, one lever at a time, is
in section 1.

**The bands.** Each row's switches stay fixed, and the estimates behind it are drawn (4,000 draws). On the cost side: the plant's
cost and financing, the life and price of the filter membranes, the upkeep share of respiration, the medium price, the loss
rate, the ammonia and the lactate the cells tolerate, the ammonia the low-lactate example's cells and the published cells make, the
cells that bursting bubbles kill, the protectant's price and dose, the least medium flow, antifoam's cost to oxygen transfer, the
price of amino acids and the weight of a cell. On the demand side: the share at equal price, the two price sensitivities, the costs
of reaching the shelf, the shop's margin, how much less buyers of premium products like a cultivated version, and a cut's cell share
and assembly cost. Taste is not drawn on top of the share at equal price, which is already the net of every taste effect. The kind
of cells and their speed are not drawn: they are what the rows differ in.

- **The published cells cost $316.1 a kilo in a batch, and lactate is the reason.** They turn most of their glucose into lactate
  (1.05 mol per mol of glucose taken up). By their own balance they need about 4.5 mol of glucose a kilo and make 4.8 mol of
  lactate. Nothing washes it out of a batch, so held to 1.3 times the 35 mmol/L perfusion allows, the batch stops at 10 g/L. The
  plant then makes few kilos: its charge is $222.3 a kilo, labour $41.6 and utilities $11.7 (since 2026-11-21 the food-grade hall
  draws an eighth of a clean room's power). Each kilo leaves with 108 litres of medium ($33.8). In perfusion with the tank tricks
  the same cells would cost $181.1 (the cautious scenario): 146 litres of medium a kilo, but a tank 14 times denser (134 g/L).
- **Process changes and cheaper inputs take $11.3 off, to $304.8, without touching the cells.** All of it is the cheaper medium. A
  batch this thin is not held by gas, so more gas, the tank tricks and a faster restart are worth nothing.
- **Less lactate takes $234.5 off, to $70.3: the largest step in dollars.** These cells make 1.1 mol of lactate a kilo, against 4.8.
  Ammonia (0.14 mol a kilo, held to 1.3 times 4 mmol/L) then holds the batch at 37 g/L, nearly four times denser. The lower lactate
  alone is worth $228.3; the 36-hour doubling in place of 43 adds $11.2. Upside's reported capacity implies 33–136 g/L a batch, and
  Vow reports 27 g/L. On this model the published cells stop at 10 g/L, so the companies' cells make less lactate than the
  published ones, or tolerate more of it.
- **Perfusion takes $21.6 off, to $48.7 (the low-lactate example).** Washing the waste out lets the tank hold 168 g/L, 4.5 times
  the batch, so the plant charge falls from $49.6 to $10.8 a kilo. It adds what a batch does not pay: 39 litres of medium a kilo where
  the batch used 28, whose filtering costs $22.7 a kilo; and the gas a dense tank bubbles kills 8% of the cells grown, against 3% in
  the batch. Since 2026-11-21 the tank's design is a column beside the tank that strips CO₂ and feeds recycled oxygen, with 1 bar of
  extra pressure, held at 168 g/L: the densest culture at which that loop passes its checks on pH and on passes an hour (the design
  search drops no design whose loop fails at full density any more; it runs it thinner). Before, oxygen held the tank at 154 g/L
  ($49.50). Nobody has run this tank design with animal cells. Without the tank tricks a kilo costs $54.7. At 30 hours the
  low-lactate example costs $46.3, and at 24 hours $43.8.
- **A cheaper plant takes $4.2 off, to $44.5.** It is Humbird's plant without a clean hall, an oxygen plant or eight seed tanks,
  and with one medium line for all the tanks. Nobody has built one. In a batch it would save more ($16.4, to $53.9), because a
  batch's cost is mostly plant; but a batch needs a fresh seed every three or four days, so it keeps Humbird's seed train.
- **Almost no ammonia or lactate takes $17.3 off, to $27.3.** Such cells need 21 litres of medium a kilo, not 39, set by their
  lactate at the 35 mmol/L the cells tolerate; every litre less is also a litre less through the filter and less protectant ($10.2 of
  membranes, not $22.7). The middle draw is $33 and 8 in 10 fall between $25 and $45. Neither
  level has been measured in meat cells.
- **Everything else at its most favourable value takes $20.3 off, to $7.0 (the all-favourable example, $6.97).** Seen from Humbird's
  optimistic design ($15.7), the levers that move it are cells that double in 16 hours ($3.7 off), the food-grade plant with shared
  medium ($2.3), dialyser-grade hollow fibres as the filter ($0.2), tanks of 42 m³ and the cheapest tank design that passes the
  checks, a flat tank with the column that strips CO₂ and feeds recycled oxygen, held at 219 g/L, the column sharing the filter loop's
  pump ($2.5 together); section 1 has the path. Ammonia sets its 12 litres of medium a kilo. Its membranes cost $0.06 a kilo. The
  middle draw is $8.3 (8 in 10 between $7.1 and $10.0), and about 8% of draws come in below $7.0: several unmeasured estimates can be
  much worse than likely and only a little better (`research_notes/model_audit.md`, section 3f).
- **The all-favourable example has two shares, and the demand judgement sets the gap.** With 58.6% of meat buyers picking it at
  equal price it takes 23.4% of world meat and seafood at its most-likely-values cost (28.4% in the US and 36.9% in Europe); the
  middle draw is 17.4% and 8 in 10 fall between 10.7% and 26.3%. With the ordinary 14.4% the same cells take 5.6% (middle draw
  3.9%; 1.4–12.7%). The 58.6% is the favourable end of a judgement: the literature review puts about 3% odds on more than 49% of
  all choices, about 52.5% of meat buyers (`research_notes/what_drives_choice.md`). It depends on the shape of the spread of liking
  near its middle, which no data pin (section 2). Conventional meat's lower price, as cultivated meat takes its sales, takes 4.1
  points off the 23.4% (its prices fall by about a tenth).
- **Humbird's optimistic design costs $15.7 (middle draw $22; 8 in 10 between $17 and $29) and takes 1.4% at that cost (middle
  draw 0.7%; 0.2–2.6%).** It has cells with almost no waste, of 3 ng, but no tank tricks, a 24-hour doubling, the engine's own
  filter loop and a plant without shared medium. The all-favourable example is by construction never dearer than it, because it
  takes every lever on which his design is the more favourable.
- **Holding the cells back is the largest single cost in the low-lactate example.** A filter loop must clear the medium that the
  bleed of cells does not carry out. Its membranes cost $0.60 per litre they filter if every run lasts its planned 33 days
  (Humbird's price over his own replacement schedule, 2,415 litres a m²), and $0.70 in the low-lactate example, where a run has a
  1% chance a day of being lost. The filter clears 32 litres a kilo, and the membranes cost $22.7 a kilo, 47% of the $48.7.
  Humbird's optimistic design clears 4 litres a kilo and pays $1.9. Among real devices (`research_notes/retention_devices.md`), a
  disc-stack separator on the outflow would cost $33.5 in the low-lactate example, $15.2 less, though a fifth of the cells
  are lost in it and its sterile price is assumed. The alternating tangential-flow filter (ATF), priced as Humbird charges bought
  equipment (6.25 times its bare price, $1,689k per m³ of tank), is the dearest: $66.3, $17.6 above the loop. Nobody has held animal
  cells in perfusion above about 4 m³.
- **Cells grown as clumps could be held back without membranes, but the biology is unshown.** Aggregates of 100–300 µm settle
  30–280 times faster than single cells, so a plain settler could hold the culture back. The low-lactate example would then cost
  $26.5 a kilo, against $48.7 with the filter loop. What nobody has shown is the culture: the densest aggregate culture found is
  about 40 g/L, for a week, in 150 mL, and every process breaks the aggregates up every 5–8 days, so the default stays the filter
  loop. Edible microcarriers do not help: the beads take up the tank ($96.5 a kilo), and the product would be mostly bead by weight
  (`research_notes/retention_aggregates.md`).
- **The bubble protectant is a real cost.** At 2 g/L it is 25 g a kilo of cells in Humbird's optimistic design, 24 g in the
  all-favourable example and 78 g in the low-lactate example, which needs 39 litres of medium a kilo. That is $0.7, $0.7 and $2.3 a
  kilo at the assumed $30 a kilo of protectant, or $6.4, $6.3 and $20 at the catalogue price ($260). A bulk quote would settle it.
- **Company cost claims are operating cost, and the scenarios include the plant.** On operating cost alone the low-lactate example's
  cells cost $20.0–20.1 a kilo to operate in a tank run as Vow runs its 20 m³ tank, above the $10–15 an investor reports for several
  companies. The plant charge comes on top (section 1, "Against what companies report").
- **No scenario reaches price parity with a $12 kilo of US minced beef or pork cuts (the US anchor).** That needs $6.1 a kilo of
  cells ($2.5 a kilo to reach the shelf and the shop's 28% margin). For the world the bar is lower still: the volume-weighted world
  price of meat and seafood is $9.43 a kilo, and the same shop price as that needs about $4.29 of cells (the US $10.93 needs $5.37;
  Europe's $13.63, $7.31). The all-favourable example costs $7.0 at most likely values, and 8 in 10 of its draws fall between $7 and
  $10; 11 of its 4,000 draws are at or below $6.1. No scenario uses a plant as cheap as a yeast plant, because nothing shows that animal
  cells can grow in one.
- **What decides it.** Each switch is moved alone from the low-lactate example ($48.7) to its best and its worst setting, with its
  tank design held. The kind of cells matters most: −$17.7 with cells that make almost no ammonia or lactate, +$106.4 with the
  published cells, +$160.3 with ordinary meat cells. Next comes how the tank is run: in a 20 m³ batch a kilo costs $21.6 more (in a
  100 m³ batch, $5.9 more). Then growth factors (+$5.3 at 60% of Humbird's price and +$12.6 if all were bought at his price; nothing
  at 30% or less, since they are inside the medium price), the medium price (−$0.3 at the nutrient floor, +$11.9 at $0.50 a litre),
  the tank tricks (+$6.1 if none work; the example already takes the cheapest), runs lost (−$4.1 at 0.2% a day, +$5.5 at 2%), growth
  speed (−$5.5 at 24 hours, +$3.3 at 43), the plant (−$4.2 with shared medium) and the gas the cells tolerate: with the
  oxygen-feeding column, 2 mm/s costs $1.9 less than the example's 4 mm/s, because fewer bubbles kill fewer cells and the column
  supplies the oxygen, and 6 mm/s costs $2.1 more. The kind of cells matters most because waste sets the litres of medium a kilo, and each litre must also pass the
  filter and carries protectant; in a batch, waste sets the density instead. The switches interact, and the page ranks them around
  any scenario you choose.
- **At equal price,** once cultivated meat is familiar, 14.4% of meat buyers pick it. It is a judgement: about 5% of meat buyers
  picked it at first contact, and half would need the average shopper to end up indifferent. A worse taste lowers it to 7–10%; a
  value on "no slaughter" raises it to 18–27%.
- **As a company reports its process, with capital counted,** cultivated chicken costs about **$34 a kilo of cells, 4.3 times
  US minced beef or pork cuts ($12 a kilo)** ($51 in the shop). This is SuperMeat's 2024 process for 100% cell mass, from 10-litre
  runs scaled on paper to 25,000-litre tanks, with a yearly charge on the plant. The company's own figure, with depreciation only,
  is $29.5 a kilo. Nobody has peer reviewed it. At the reported cost the share is 0.16% of world meat and seafood (0.4% in the US);
  with its cost and demand both drawn, the middle draw is 0.19% and 8 in 10 fall between 0.05% and 0.8%.
- **Where.** In the low-lactate example, mostly beef and premium fish: beef steaks are 31% of sales, premium fillets and shrimp
  14%, pork cuts 9%, prime beef 8%, chicken cuts and sheep and goat 7% each. They are sold to the few shoppers who like cultivated
  meat enough to pay several times the price of the cut beside it: two-fifths of the sales (40%) are of products at more than four
  times the price of their meat. That rests on the far tail of the spread of liking, which is an extrapolation: the premium meats it
  was fitted to stop at 3.6 times. In the all-favourable example every meat sells, at 0.4 to 2.9 times the price of its meat.
- **When.** These are long-run ceilings. If nothing stalls and supply keeps up, adoption reaches 90% of the long-run share after
  20 years in the low-lactate example and 20 in the all-favourable example, with repeat buying and dropping out borrowed from
  plant-based meat. The speeds come from durable goods; they are assumed,
  not estimated for a food.

**What the answer rests on** (`answer_rests_on.py`). The model has 611 inputs, 281 of them with a range. Moving each across its
range, one at a time, with each scenario's tank design held as it is: only 19 move the low-lactate example's or the all-favourable
example's cost by $1 or more, and 13 move the low-lactate example by more than $3. The rest serve side studies or tank detail.
Costs in the table are at most likely values.

| input | its range (model's value) | Low-lactate example, $/kg | The low-lactate example's share of world meat | All-favourable example, $/kg | where the value comes from | in the uncertainty band? |
|---|---|---|---|---|---|---|
| Litres a m² of cell filter passes before it is replaced | 900–5500 L/m2 (2415) | $86.9 to $35.9 | 0.005% to 0.1% | $7.0 to $7.0 | derived from pharma runs (fouled in 4.5 days to lasted 30); no meat-cell run; probably the generous end (median about 1,500), and read with the membrane price | yes |
| Ammonia the cells tolerate in the tank | 2–8 mmol/L (4) | $89.0 to $43.8 | 0.005% to 0.07% | $7.0 to $6.9 | the evidence note's median, 3.5–4 mmol/L (80% interval 2–8): meat-relevant cells measured lose 10–55% of growth at 2.5–5, meat-cell processes hold 2–3, none measured at density | yes |
| Ammonia the cells of the low-lactate example make per kilo grown | 0.04–0.25 mol/kg wet (0.14) | $44.5 to $80.4 | 0.06% to 0.007% | $7.0 to $7.0 | measured once, in bovine cells with glutamine replaced (Hubalek 2023): 'more than 5-fold' below the 0.70 with glutamine | yes |
| Lactate the cells tolerate in the tank | 20–50 mmol/L (35) | $70.3 to $48.7 | 0.01% to 0.05% | $7.0 to $7.0 | Cultivated Meat (book), Table 2, citing Hassell 1991; Pasitka 2024; Humbird 2021, judgement | yes |
| Lactate the cells of the low-lactate example make per mol of glucose | 0.39–0.6 mol lactate / mol glucose (0.42) | $48.7 to $65.5 | 0.05% to 0.02% | $7.0 to $7.0 | waste_tricks_sizing.md | **no** |
| Culture whose cells bursting bubbles kill, per volume of gas passed | 0.0001–0.0012 L of culture per L of gas (0.0004) | $45.7 to $58.9 | 0.06% to 0.02% | $6.5 to $8.7 | Jobses, Martens, Tramper 1991, read in full | yes |
| Salt strength the cells tolerate (osmolality) | 350–450 mOsm/kg (415) | $57.9 to $48.7 | 0.02% to 0.05% | $8.3 to $7.0 | CHO measurements (`perfusion_rate_osmolality.md`) | no: moves the all-favourable example's median by about $0.1, at forty times the computing time |
| Price of the bubble protectant (poloxamer 188), bought by the tonne | 5–100 $/kg (30) | $46.7 to $54.1 | 0.05% to 0.03% | $6.4 to $8.7 | assumed: only catalogue prices ($230–260/kg) found | yes |
| Yearly charge on the plant's capital (financing and recovery) | 0.123–0.236 of TCI per yr (0.173) | $45.6 to $52.6 | 0.06% to 0.03% | $6.4 to $7.7 | derived from Humbird's financing, at a mature industry's rates | yes |
| Price of cell-filter membrane | 1050–1450 $/m2 (1450) | $42.4 to $48.7 | 0.07% to 0.05% | $7.0 to $7.0 | Humbird's ATF price; retail modules a quarter less | yes |
| Least medium flow the cells need for everything but ammonia and lactate | 3.7–18.5 mL per g wet cells per day (7.5) | $48.7 to $54.5 | 0.05% to 0.03% | $7.0 to $7.0 | judgement within CHO measurements | yes |
| Dose of bubble protectant in the medium | 1–5 g/L (2) | $47.5 to $52.2 | 0.05% to 0.04% | $6.6 to $8.1 | dense pharma cultures (`gas_flow_cap.md`) | yes |
| Staff a plant in perfusion needs, against a fed-batch plant | 1.4–3.9 x the fed-batch crew (2) | $47.7 to $51.7 | 0.05% to 0.04% | $6.7 to $7.9 | Humbird 2021; CE Delft 2021; SuperMeat 2024, derived | **no** |
| Amino acids a kilo of cells takes up (the nutrient floor) | 0.2–0.65 kg amino acids/kg wet (0.232) | $48.7 to $51.5 | 0.05% to 0.04% | $6.7 to $10.0 | GFI's eight estimates, 200–650 g; the model takes the most efficient (`nutrient_floor.md`) | no: a trait of the cells, as glucose use is; the all-favourable example takes the efficient end |
| How the cost of medium preparation equipment rises with the medium passed (exponent) | 0.6–1 exponent (0.6) | $48.7 to $51.1 | 0.05% to 0.04% | $7.0 to $7.4 | assumed | **no** |
| Weight of one cell (every kind of cells since 2026-11-19) | 1000–3000 pg wet per cell (2000) | $50.1 to $47.9 | 0.04% to 0.05% | $7.0 to $7.0 | judgement between the 1.0–1.75 ng reported for chicken cells and Humbird's 3 ng | yes |
| Rise in plant construction costs since 2018 | 1.17–1.4 x (1.33) | $47.5 to $49.2 | 0.05% to 0.04% | $6.8 to $7.1 | construction cost index, 2024 estimated | partly: the plant's cost is drawn, not this index |
| CO₂ level at which the culture leaves the stripping column | 20–70 mbar (55) | $50.5 to $49.3 | 0.04% to 0.04% | $7.2 to $7.0 | design choice | **no** |
| Price of amino acids (the nutrient floor) | 5–11.59 $/kg amino acids (6.36) | $48.7 to $49.9 | 0.05% to 0.04% | $6.6 to $8.3 | GFI's feed-grade mean of 22, to low food-grade (`nutrient_floor.md`) | yes |

*Left out: The gas flow the tank takes is a scenario switch (2, 4 or 6 mm/s). The input of that name is also the reference speed of Humbird's oxygen figure, so moving it alone rescales that figure ($48.56 to $48.68 in the low-lactate example) without changing any tank; it is left out.*
*Left out: Maturation, the hours the cells spend in the tank without growing before harvest, is a choice of product, not an estimate. The products near market are bulk cell mass and take none; 4 to 28 days to mature muscle or fat would take the low-lactate example from $48.68 to $75.46 (4 days) or $232.75 (28 days). It is a lever on the page; it is left out here.*
*Also left out: the settings of the scenario switches themselves (medium price, growth factors bought, runs lost, gas flow, doubling time, restart time). "What to prioritise" shows what each switch is worth.*

- **Five numbers carry most of the low-lactate example's uncertainty, and none has been measured on meat cells at production
  density.** The life of the cell filter ($86.9 to $35.9), the ammonia the cells tolerate ($89.0 to $43.8), the ammonia its cells
  make ($44.5 to $80.4), the lactate the cells tolerate ($70.3 to $48.7) and the lactate its cells make ($48.7 to $65.5). Next come
  the cells that bursting bubbles kill ($45.7 to $58.9) and the salt the cells tolerate. The filter life is Humbird's replacement
  schedule, the two tolerances are judgements within published ranges, the ammonia made was measured once, in flasks, and the
  lactate made is a setting of the example (not drawn).
- **The filter life is Humbird's own pair of price and life.** The model takes 2,415 litres a m² (his 1,920 membranes a year for
  51 million litres of perfusate) with his price of $1,450 a m². The evidence note (`research_notes/ammonia_tolerance_and_filter_life.md`)
  finds that small-pore fibres in dense culture last about 180–2,500 L/m², with a median of about 1,500, so 2,415 is at the generous
  end. Life and price go together: a membrane costs its price divided by its life per litre. A life of 1,500 takes the low-lactate
  example to $62.5 at $1,450 a m². The band draws both.
- **The ammonia tolerance is the note's own median.** The meat-relevant cells measured so far lose 10–55% of growth at 2.5–5 mmol/L
  when ammonia is added. They were not run at density. The scenarios use 4. At Humbird's 5, the low-lactate example would cost $43.8.
- **The lactate tolerance is a judgement between three sources.** A textbook gives under 10 to 22 mmol/L, one company held 30 in a
  running culture (Pasitka 2024), and Humbird takes 50. The scenarios take 35 (range 20–50). At 50 the low-lactate example does
  not move, because ammonia sets its litres; at 20 it costs $70.3. The published cells, whose batch lactate holds, cost $222.7 at 50.
- **Not drawn:** the salt the cells tolerate (it moves the all-favourable example's median by about $0.1, at forty times the computing
  time), the lactate the low-lactate example's cells make and amino-acid uptake (traits the kind-of-cells switch holds), the crew of a
  perfusion plant, the exponent of the medium-preparation equipment and the CO₂ level at the column's outlet; the table's last
  column marks each. (How fast oxygen uptake falls in a thick culture and the share recovered at harvest left the table on
  2026-11-21: with the thinned oxygen-column designs each moves the low-lactate example by under $1.) The protectant's prior runs
  from $5 a kilo (an industrial-grade copolymer) to $100 (pharma grade by the tonne) since 2026-11-21
  (`research_notes/evidence_poloxamer_price.md`); it was $10 to $120. A quote would settle it.
- **Each of the first four is cheaper to settle by a measurement than by more modelling**: a weeks-long filter run at high density,
  the ammonia and lactate limits of a meat-cell line, and the ammonia and lactate a meat-cell line fed without glutamine makes per
  kilo grown.

| input | its range (model's value) | share at the low-lactate example's cost | share at the all-favourable example's cost | where the value comes from | in the uncertainty band? |
|---|---|---|---|---|---|
| Share of buyers who choose cultivated meat at equal price, once familiar | 0.03 to 0.49 of all choices (0.13) | 0.02% to 0.1% | 1.5% to 20.4% | a judgement: a third of first-contact aversion fading; the literature review puts the 10th, 50th and 90th percentiles at 2%, 10% and 35% (`what_drives_choice.md`) | yes |
| How wary people are of a novel food, in the long run | -2 to 1 utils (0) | 0.03% to 0.06% | 2.7% to 7.9% | a judgement on long-run behaviour | no: part of the share at equal price, which is drawn |
| Whether people see cultivated meat as healthier or less healthy | -0.5 to 0.5 norm (0) | 0.04% to 0.06% | 3.8% to 8.2% | a scenario dial: no data | no: part of the share at equal price, which is drawn |
| Retailer's gross margin, as a share of the shelf price | 0.15 to 0.4 of shelf price (0.28) | 0.09% to 0.02% | 7.6% to 3.8% | US meat-department margins (28–32%) and French supermarket data | yes |
| How price sensitivity falls with income | 0 to 1 exponent (0.32) | 0.1% to 0.1% | 5.7% to 9.2% | USDA demand estimates | no: each value re-solves the demand model's calibration |
| Cost of assembling a cut, beyond what mince pays | 0.5 to 7 $/kg (2) | 0.05% to 0.03% | 6.8% to 3.3% | analogues, no study of cultivated meat: plant-protein extrusion, surimi forming, binder prices (`structuring_cost.md`) | yes |
| How fully mainstream buyers credit cultivated meat's taste | 0.6 to 1 fraction (1) | 0.03% to 0.05% | 2.7% to 5.6% | a scenario dial | no: part of the share at equal price, which is drawn (left the bands on 2026-11-20) |
| Value mainstream buyers put on meat without slaughter | 0 to 1 utils (0) | 0.05% to 0.07% | 5.6% to 8.4% | a scenario dial: surveys disagree | no: part of the share at equal price, which is drawn |
| Per-kg costs from cells to the shop shelf (forming, packing, cold chain), $ per kg | 1.5 to 3.5 $/kg (2.5) | 0.05% to 0.04% | 6.8% to 4.6% | fitted to USDA ERS meat spreads, plus forming | yes |
| How much more price-sensitive cultivated meat is than meat in general | 4 to 11 x (8.5) | 0.3% to 0.02% | 7.3% to 5.3% | bracketed by data on close substitutes | yes |

- **The demand side cannot rescue the low-lactate example.** At its cost ($48.7), no single demand input moved across its range takes
  the share above 0.3%: the inputs span 0.02–0.3%. The low end is set by the retailer's margin and the high end by how
  price-sensitive cultivated meat is. At the all-favourable example's cost, with the ordinary demand, the same inputs span 1.5–20.4%.
  There, how people take to a new food matters far more than any cost input: the largest cost input in the table above, the
  amino acids a kilo of cells takes up, moves the all-favourable example by $3.2.
- **The share at equal price is the widest row, and it is a judgement.** There are no sales data for cultivated meat. The
  literature review puts its median at 10% and its 10th and 90th percentiles at 2% and 35% (`what_drives_choice.md`).
- **The cut is the product, and it is not yet shown.** Most of the low-lactate example's sales are cuts that are 80% cells, and
  three-tenths are premium products. The cut's cell share and its assembly cost are both drawn in the bands. Fewer cells make a cut
  cheaper and less liked: at half plant protein the low-lactate example's share is 0.13%; if a cut were all cells, 0.03%.
- **The shape of the spread of liking is fitted, loosely.** Its two numbers (a standard deviation of 3.9 utils and a tail of 4
  degrees of freedom) are not table rows, because across their ranges they move the low-lactate example's share little. The shape
  matters more than that suggests: it replaced a normal spread on 2026-11-19, and the share far above parity doubled.
- **Far above parity the two cross-checks disagree.** Products still dearer than their meat respond to price more strongly than
  farmed salmon did (3.7–4.2 against 1–1.5; section 2), which says the model's share falls too fast as the price rises. The
  curve anchored on premium real meats gives the low-lactate example 0.02% (0.01–0.04%), below the model's 0.05%, which says the
  opposite. Above about four times the price of meat there are no data at all, and at $48.7 a kilo of cells two-fifths of the sales
  are there.
- **A floor on the dollar channel.** Price enters through dollars (scaled by income) and through the ratio to meat's price, and the
  two are calibrated together. The dollar coefficient stops at zero (`market_share._derive_beta`), so a strong loss aversion cannot
  make shoppers gain from paying more.
- **Left open: dollars or ratios.** How much of the price response is in dollars and how much is a ratio to the cut's own price is
  not pinned by the data the model uses. Each value re-solves the calibration, so it is not in the bands.

**For funders,** in order: cells that make less lactate and ammonia and still grow fast, which is the ladder's largest step; a
filter, or another way of holding cells back, that lasts in a dense culture; the ammonia and lactate measurements; how many cells
bubbles kill in a dense culture with protectant; the price of medium at production scale; tank tricks that clear CO₂ without
bubbles; and a cheaper class of plant for animal cells. Section 6 gives the reasons.

## 1. Cost and the price ratio

Here the low-lactate example means cells that make 0.14 mol of ammonia a kilo (the published figure) and 0.42 mol of lactate per mol of glucose (the best published is 1.05), double every 36 hours and weigh 2 ng, grown in perfusion in a 20 m³ tank in a food-grade plant with medium at $0.20 a litre. The all-favourable example (`scenarios.all_favourable`) means every lever at its most favourable value among this model's own favourable end, Humbird's design and nine other published studies, within the model's limits: cells of 3 ng that make 0.054 mol of ammonia a kilo and 0.28 mol of lactate per mol of glucose, double every 16 hours and tolerate 5 mmol/L of ammonia and 50 of lactate, grown in perfusion in 42 m³ tanks in a food-grade plant with shared medium, with medium at the cost of its nutrients, no growth factors bought, no lost runs and dialyser-grade hollow fibres holding the cells back, and 58.6% of meat buyers picking it at the same price.

*The cases in this table are older cases kept for comparison. They are not the scenarios. Each is one fixed design with every
estimate at its most likely value. They use Humbird's enhanced 3 ng cell (almost no ammonia or lactate), his limits of 5 mmol/L of ammonia and 50 of lactate, medium that costs only
what the cells eat and no lost runs, unless the row says otherwise. R is the shop price against US minced beef or pork cuts ($12 a kilo).*

| case | cells, $/kg | R vs US minced beef or pork cuts ($12 a kilo) | source and status |
|---|---|---|---|
| the reported process in a pharma-style plant with cells at half the density | $52.4 | 6.35 | physics-based plant cost (`floor_physics.explore` since 2026-11-21) with the company's medium; nearer to reported harvests |
| **as a company reports, with a return on capital (the reported cost)** | **$34.4** | **4.27** | SuperMeat 2024; 10 L runs scaled on paper; not peer reviewed; its own figure with depreciation only is $29.5 |
| Humbird's fed-batch design, 2025 prices | $24.9 | 3.18 | a detailed design with efficient cells; not built |
| a pharma-style plant, tanks drained and refilled, first-plant financing | $22.5 | 2.90 | physics-based; efficient cells at this density not shown |
| Humbird's optimistic design with first-plant financing | $18.4 | 2.42 | the row below at 23.6% of the plant's cost a year |
| **Humbird's optimistic design (what earlier versions called the floor): a standard perfusion tank, no tricks; no clean rooms, perfusion, efficient cells, food-industry financing** | **$15.7** | **2.11** | physics-based; each piece shown separately, never together; a hollow-fibre filter loop holds the cells back, never run at 20 m³ |
| Humbird's optimistic design in a plant as cheap as a yeast plant (no scenario assumes it), buying its oxygen | **$10.7** | **1.53** | such plants exist for microbes; none built or costed for animal cells |
| rough lower bound | $3.0 | 0.63 | a bound, not a design |

*Since 2026-11-20* Humbird's optimistic design costs more than the $12.8 of 19 November: bubbles kill 8% of its
cells, 2% are lost at harvest, its membranes last 2,415 litres a m², its crew is twice a fed-batch crew, its medium-preparation
equipment is sized for its litres, and its plant items are charged per tank. It was $15.9 on 20 November and is $15.7 since
2026-11-21, when the building's power began to follow its floor and class. The main cost model (`cost_model.py`) carries the plant
term of that design as an input (`plant_floor`, $13.5 a kilo since 2026-11-21; $13.8 on 20 November, $10.8 before), so its own
reference cost (`cost_floor`) is $15.5 and R 2.08. It is $0.2 below the engine's $15.7 because it adds the nutrient floor per kilo
grown, not per kilo harvested.

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
tested at this size and cell density. Whether it works at 20 m³ is open (`research_notes/gas_flow_cap.md`); at 5 mm/s the design
would cost $16.2. Since 2026-11-20 gas also has a cost: bursting bubbles kill cells in proportion to the gas
passed per litre of culture, 8% of the cells grown in this design. Plant cost per m³ comes from Humbird's design: about $910k with clean rooms, about $810k
with a sanitary hall in their place. Microbial fermentation plants are built for about $190k, which no scenario assumes
(METHODS.md, "The plant term of Humbird's optimistic design").

**Financing matters as much as engineering.** Humbird charges 23.6% of a plant's cost a year: money at 7.5%
repaid in 10 years, plus 4% maintenance and 5% insurance. That fits a first plant, and the reported cost and the two
pharma-style rows use it. His own report gives the food-processing sector's cost of capital as 5.4% and uses a
20-year life for a yeast plant; that makes the charge 17.3%. The scenarios are long-run cases set
against meat, a mature industry, so they use 17.3%. It is worth $2.7/kg in Humbird's optimistic design ($18.4 against $15.7).

**How the tank is run matters more for wasteful cells.** Perfusion is worth $0.8–1.6/kg in Humbird's optimistic design against
tanks that are drained and refilled (the vessel grid below: $15.7 against $16.5 and $17.3; since 2026-11-21 his cells' batch
reaches 116 g/L, held by its waste, where the least medium flow had held it at 92), and $21.6 with the low-lactate example's
switches, whose batch is held at 37 g/L by the waste mass balance. The plant-cost axis below compares the two modes on the same assumptions. Removing
clean rooms saves about a tenth of the plant cost. A plant as cheap as a yeast plant cuts the design's cost by about a third.

The medium and the plant matter most. No single lever reaches parity on its own. From the reported cost (R = 4.27): the plant
term the main cost model carries for Humbird's optimistic design (`plant_floor`, $13.5 a kilo; $13.8 before 2026-11-21) gives R ≈ 3.62, medium at $0.20/L 3.21, and efficient cells 2.94.

```
basic product vs commodity meat (US minced beef or pork cuts, $12/kg), Monte Carlo over the cost inputs (N=20,000):
  price ratio R:   P50 = 4.42   80% CI [3.36, 5.75]   90% CI [3.11, 6.17]
  long-run share:  P50 = 0.3%   80% CI [0.1, 1.6]
  0% of draws reach parity (R ≤ 1)
```

This draw is around the reported cost, for mince against US minced beef or pork cuts at $12 a kilo. Its share is of all choices, as `uncertainty.py`
computes it; as a share of meat buyers it would be about an eighth higher. Two changes of 2026-11-20 moved it in opposite
directions: taste stopped being drawn on top of the share at equal price, and the low end of the plant-cost range rose with
Humbird's optimistic design (the median R was 4.20). On 2026-11-21 the plant-cost range became $13.5–37.1 (was $13.8–34.0: its
high end is the half-density tier, now priced by `explore` itself), which moved the median R from 4.32 to 4.42. The median R is close to the reported 4.27: the
plant-cost range is wider on the high side (reported harvests are less dense than Humbird's optimistic design assumes), while the
medium price and cell efficiency can improve on the report. It does not include the scenarios or a yeast-class plant.

**What the tricks do, and what the cells decide.** Research notes size ways round the tank's limits
(`research_notes/gas_exchange_study.md`, `waste_tricks_sizing.md`); `floor_physics.explore` carries them as
levers, and the page's panel shows each limit as a bar. Every tank trick here is a change of feed or process; the
kinds of cell are set by their traits, against the best measured in meat cells.

The settings of these tables are not the scenarios'. They run `explore()` as Humbird's optimistic design does: a tall 20 m³
perfusion tank with gas at 6 mm/s, cells of 3 ng, his limits of 5 mmol/L of ammonia and 50 of lactate (the scenarios use 4 and 35), medium at $0.15 a litre and
never below what the cells eat, and no lost runs outside the brackets. Glucose comes from the cells' own balance, as in the
scenarios, for every kind of cell but Humbird's enhanced one, which keeps his figure (the two agree). So the published cells
cost $105.0 in the first table, $181.1 in perfusion with the scenarios' settings and $316.1 as row 1 of the ladder, which is a batch: the same ammonia and lactate yield, and 107 litres of medium a
kilo against 146 in the scenarios' perfusion, but here with a 3 ng cell, gas at 6 mm/s, cheaper medium, higher ammonia and lactate limits and no lost runs. Read the tables for what the tricks do,
not for the cost of a kind of cell.

Each cell gives the cost per kg of cells in the food-grade plant of Humbird's optimistic design, in brackets with runs lost to
contamination at 0.2% a day (pharma's rate, 14-day restart); then the yeast-style plant, in brackets at 2.2% a day (the top of
what a survey of makers implies; 0.6% a day sits between); then the density, what binds, and litres of medium per kg.

*All tricks, all cells:*

| cells | sparger only | sparger, fat in the feed, oxygen held at 0.08 | packed column on a loop | column with oxygen sweep, 1 bar gauge |
|---|---|---|---|---|
| Humbird's enhanced cells (0.055 mol of ammonia a kilo, 0.28 lactate per glucose) | $15.7 ($16.0); yeast-style $10.7 ($12.7); 120 g/L CO₂, 12 L/kg | $15.3 ($15.6); yeast-style $11.0 ($13.2); 139 g/L oxygen, 12 L/kg | $15.8 ($16.1); yeast-style $10.8 ($12.9); 121 g/L oxygen, 12 L/kg | $13.9 ($14.2); yeast-style $11.8 ($14.5); 258 g/L thickness, 12 L/kg |
| best shown in meat cells (bovine, glutamine replaced) | $105.0 ($107.5); yeast-style $97.1 ($124.8); 148 g/L oxygen, 107 L/kg | $73.2 ($75.0); yeast-style $66.3 ($85.0); 169 g/L oxygen, 72 L/kg | $105.0 ($107.5); yeast-style $97.1 ($124.8); 148 g/L oxygen, 107 L/kg | $100.5 ($103.0); yeast-style $96.2 ($123.9); 258 g/L thickness, 107 L/kg |
| ordinary meat cells (bovine) | $141.9 ($145.3); yeast-style $136.7 ($175.5); 124 g/L CO₂, 156 L/kg | $141.2 ($144.5); yeast-style $136.7 ($175.6); 142 g/L oxygen, 156 L/kg | $142.0 ($145.3); yeast-style $136.8 ($175.6); 124 g/L oxygen, 156 L/kg | $138.8 ($142.1); yeast-style $136.4 ($175.7); 258 g/L thickness, 156 L/kg |

*With more ammonia and lactate.* Humbird's enhanced cell with ammonia at 0.14 mol/kg (the best measured in meat
cells, glutamine replaced) and lactate at 0.39 per glucose (the best measured in meat cells is 1.05), at its
24-hour doubling:

| cells | sparger only | sparger, fat in the feed, oxygen held at 0.08 | packed column on a loop | column with oxygen sweep, 1 bar gauge |
|---|---|---|---|---|
| Humbird's enhanced cells with 0.14 ammonia and 0.39 lactate | $32.0 ($32.8); yeast-style $27.0 ($33.8); 120 g/L CO₂, 31 L/kg | $31.6 ($32.3); yeast-style $27.3 ($34.2); 139 g/L oxygen, 31 L/kg | $32.1 ($32.8); yeast-style $27.1 ($34.0); 121 g/L oxygen, 31 L/kg | $30.0 ($30.7); yeast-style $27.9 ($35.3); 258 g/L thickness, 31 L/kg |
| best shown in meat cells (bovine, glutamine replaced) | $105.0 ($107.5); yeast-style $97.1 ($124.8); 148 g/L oxygen, 107 L/kg | $73.2 ($75.0); yeast-style $66.3 ($85.0); 169 g/L oxygen, 72 L/kg | $105.0 ($107.5); yeast-style $97.1 ($124.8); 148 g/L oxygen, 107 L/kg | $100.5 ($103.0); yeast-style $96.2 ($123.9); 258 g/L thickness, 107 L/kg |
| ordinary meat cells (bovine) | $141.9 ($145.3); yeast-style $136.7 ($175.5); 124 g/L CO₂, 156 L/kg | $141.2 ($144.5); yeast-style $136.7 ($175.6); 142 g/L oxygen, 156 L/kg | $142.0 ($145.3); yeast-style $136.8 ($175.6); 124 g/L oxygen, 156 L/kg | $138.8 ($142.1); yeast-style $136.4 ($175.7); 258 g/L thickness, 156 L/kg |

"Best shown in meat cells" is bovine cells with glutamine replaced: 0.14 mol of ammonia per kg and a 43-hour
doubling (Hubalek 2023); "ordinary" is the same cells with glutamine, 0.70 mol and 26 hours. Both take chicken
cells' lactate yield (1.05 per glucose taken up, Pasitka 2024). "Fat in the feed" means
the cells take all their lipid from the medium instead of making it from glucose; making lipid from glucose
gives off CO₂ without using oxygen, and on Humbird's cell that is why CO₂ made per oxygen used is 1.20 rather
than 1.0 (fed, 0.97; a carbon balance, the note's section 10). Holding dissolved oxygen at 0.08 mmol/L (38% of
air saturation, a usual pharma setpoint) in place of the 0.28 the standard tank's oxygen supply implies widens the
oxygen driving force by about a fifth; it matters only where oxygen binds.

Reading the tables (all with the filter loop, the protectant, antifoam, bubble deaths and the harvest loss counted): the tricks take the enhanced cells
from $15.7 to $13.9, still above the $6.1 parity mark, and in a yeast-style plant they do not pay ($10.7 with the sparger alone, $11.8 with
everything). Since the filter loop is priced, a denser culture saves less: the bleed carries out less liquid, so more passes the
membranes. With 0.14 ammonia and 0.39 lactate the enhanced cell needs 31 litres of medium per kg (ammonia sets it), and the tricks take
it from $32.0 to $30.0 ($27.0 in a yeast-style plant, sparger only). With cells that have actually been measured, waste sets the
medium and the tank tricks are worth little: every trick together takes the best meat cells from $105.0 to $100.5, 4%, against 11%
for the enhanced cells. The tricks raise the density, not the litres of medium, and for these cells the litres are most of the
cost: lactate sets them at 107 a kilo. The one tank-side change that helps them is fat in the feed, $105.0 to $73.2: cells that
take their fat from the feed need less glucose (4.3 mol a kilo falls to 2.9), make less lactate (4.5 mol falls to 3.0) and need
72 litres of medium, not 107. That assumes their lactate yield stays at 1.05 when fat is fed, which nobody has measured. The
cells decide the cost before the tank does. Losing runs at 0.2% a day adds
$0.3–3.4 per kg. At 2.2% a day in the yeast-style plant it adds $2.0–2.7 for the enhanced cells, $19–28 for the best meat
cells and about $39 for ordinary cells: a lost run loses its time, its tankful and its filter membranes, and wasteful cells
filter the most. The loss model does not yet count a failed restart, and long continuous runs are more exposed per run than short
batches.

When the cells tolerate only a capped gas flow, the cheapest combination of tank shape, column and headspace
pressure (`gas_exchange.cheapest_tricks`; the sparger runs at its cap, a squatter tank pays for its steel):

| gas cap | food-grade plant, sparger only | cheapest combination, any circulation | the same, keeping the loop within the tested passes and the safe pH exposure | yeast-style: sparger only / any / within limits |
|---|---|---|---|---|
| 1 mm/s | $68.0 | $13.41: column with oxygen sweep, the ordinary tall tank, 1 bar gauge; **94 passes** | $27.5: column for CO₂, liquid twice as deep as wide, 1 bar gauge; 5 passes | $38.3 / $10.64 / $16.1 |
| 2 mm/s | $34.7 | $13.49: column with oxygen sweep, the ordinary tall tank, 1 bar gauge; **75 passes** | $17.2: column for CO₂, liquid twice as deep as wide, 1 bar gauge; 8 passes | $19.8 / $10.39 / $10.4 |
| 4 mm/s | $18.2 | $13.67: column with oxygen sweep, the ordinary tall tank, 1 bar gauge; **43 passes** | $14.9: column for CO₂, liquid twice as deep as wide, 1 bar gauge; 10 passes | $10.7 / $10.04 / $10.0 |
| 6 mm/s | $15.7 | $13.92: column with oxygen sweep, the ordinary tall tank, 1 bar gauge; **22 passes** | $14.5: column for CO₂, liquid twice as deep as wide, 1 bar gauge; 11 passes | $10.7 / $10.29 / $10.3 |

Passes are tank volumes pumped through the column an hour. Dense cultures have been pumped through fibres at up
to about 15-24 an hour for weeks, at 1-4 litres (Clincke 2013; a vendor note); nothing beyond that is tested.
Culture leaving the column stays alkaline (+0.26 pH at 55 mbar) until it is back in the tank, so the share of
the culture that is alkaline grows with the passes. The safe limit used here is the 55 mbar, 0.5 m3 design that
the gas-exchange note found 3 to 6 times below an exposure that slowed CHO cells (Paul 2020). At 22 passes the
loop is 1.9 times that limit (about half the harmful exposure); at 75 passes, 6.4 times (about twice the harmful
one). **Within those limits Humbird's optimistic design depends on the gas the cells tolerate**: $14.5 at 6 mm/s, $14.9 at
4, $17.2 at 2, $27.5 at 1. With any circulation allowed the order reverses since 2026-11-20: the column does the gas exchange, and
a sparger run more gently kills fewer cells ($13.41 at 1 mm/s against $13.92 at 6). In the cells-by-tank tables above, the last column ("column with oxygen sweep, 1 bar
gauge") runs at 22 passes an hour for the enhanced cells, beyond the tested range. None of the tricks has been
tried with meat cells.

### The engine against Humbird's own tables (`humbird_check.py`, `research_notes/humbird_backtest.md`)

The page opens on Humbird's best estimate: his fed-batch design with enhanced cells on soy hydrolysate, **$21.00 a kilo of wet
cells in 2018 dollars** (his Table 4.7). Before starting there, the engine (`floor_physics.explore`) was run at his conditions for
the four columns of that table and for his perfusion design (Table 4.13), line by line. Costs are converted to 2025 dollars with
the plant-cost index for capital (×1.33) and consumer prices for the rest (×1.28, BLS CPI-U).

| Line | Humbird, 2018 $ | Humbird, 2025 $ | Engine like for like, 2025 $ | Engine with the model's additions, 2025 $ |
|---|---:|---:|---:|---:|
| Nutrients (his macronutrients) | 3.39 | 4.34 | 4.34 | 4.80 |
| Growth factors (his micronutrients) | 3.12 | 3.99 | 3.84 | 4.38 |
| Consumables | 0.81 | 1.04 | 1.03 | 0.90 |
| Utilities | 0.93 | 1.19 | 1.18 | 1.34 |
| Labour | 1.42 | 1.82 | 1.81 | 2.08 |
| Plant (capital charge, maintenance, insurance) | 11.33 | 15.07 | 14.79 | 16.94 |
| **Total** | **21.00** | **27.45** | **26.99** | **30.45** |

| Design | Humbird, 2018 $ | Engine like for like, 2018 $ | Engine like for like, 2025 $ | Engine with the model's additions, 2025 $ | Density with the additions, g/L |
|---|---:|---:|---:|---:|---:|
| Fed-batch, enhanced cells, amino acids | 36.79 | 36.37 | 47.11 | 53.54 | 116 |
| Fed-batch, enhanced cells, soy hydrolysate (his best estimate) | 21.00 | 20.65 | 26.99 | 31.28 | 116 |
| Fed-batch, wild-type cells, amino acids | 236.58 | 261.61 | 344.25 | 376.61 | 7 |
| Fed-batch, wild-type cells, soy hydrolysate | 225.03 | 248.15 | 327.03 | 358.98 | 7 |
| Perfusion in 2 m³ tanks, enhanced cells, amino acids | 51.29 | 49.74 | 64.73 | 112.45 | 121 |

(`python humbird_check.py`, 2026-11-21. The first table's last column is the model's own version of his best estimate, with the
model's plant figure and flat supplies; the second keeps his plant cost, yearly charge and filter sets, so his best estimate reads
$31.28 there.)

- **Like for like the engine gives $20.65 against his $21.00, and $26.99 in 2025 dollars.** His three designs with enhanced cells
  are within 3.0%. His two wild-type designs come out 10% high, from the plant: since the engine prices each plant item by item
  (per tank and per m³), it gives $683k per m³ of tank to every fed-batch plant, while his wild-type plants cost $596–600k, because
  their oxygen plant, utilities and medium equipment serve 6% of the output. His perfusion plant of 2 m³ tanks is reproduced to
  6% ($3,244k per m³ against his $3,451k).
- **What is entered as his conditions, and what the engine reproduces.** Entered: his cells, tanks and cycle, his limits (5 mmol/L
  of ammonia, 50 of lactate, 100 mbar of CO₂, 6 mm/s of gas), his nutrient cost and his yearly charge (23.6%). Reproduced by the
  engine from those: the plant cost per m³ of tank, the density at harvest (120 g/L against his 115.6) and the output per m³ of tank
  (14.5 t a year against 14.4), and with them the plant charge per kilo, labour, utilities, consumables and growth factors. What he
  does not count is switched off for the comparison: cells killed by bubbles, cells lost at harvest, a least medium flow beyond
  ammonia and lactate, bubble protectant, antifoam, slower oxygen uptake in a thick culture, slower growth near the end of a batch,
  and lost runs.
- **It led to six fixes in the engine.** Growth factors are his $3.13 a kilo over his fed-batch's 8.65 litres a kilo ($0.36 a
  litre), bought like for like only in his share of the litres. Utilities are four parts (by the year and by the run per m³ of tank,
  by the litre of medium, by the kilo), in place of a flat $0.94 a kilo; his wild-type columns, which pay $14.52 a kilo in the same
  plant, show that most of it does not scale with the kilos. The building's power follows its floor and the class of each building
  (his Table 3.2). The crew per m³ of tank uses his plant's 14.2 tonnes per m³ a year, and part of it is counted per tank. The
  plant's items are charged per tank as well as per m³, in his own accounting (`floor_physics.tank_items`).
- **Residuals left open.** In his perfusion design the growth factors are −4%, labour 0% and utilities −27% against his table
  (they were +62%, −42% and −54% before 2026-11-21); the rest of the utilities is 13.5 litres a kilo of process water his report
  does not itemise. With his wild-type cells labour is 15% high (his plant has 81 staff, not 95). The building cost per tank is a
  fit to his two plants, not his rule.
- **What the model adds to his best estimate.** With the model's additions on, his design costs $30.45 a kilo in 2025 dollars.
  One at a time: the model's flat supplies in place of his filter sets, with his yearly charge unrounded (−$0.75); slower oxygen
  uptake in a thick culture (nothing); the least medium flow the cells need (nothing: since 2026-11-21 a batch may end 1.3 times
  above it, as above ammonia and lactate, and it no longer binds; it had capped the tank at 92 g/L and added $6.4); all the waste a
  kilo made counted at the end of a batch (+$0.73); cells killed by bubbles (+$2.27, the largest); cells lost at harvest (+$0.60);
  and bubble protectant (+$0.61).
- **The page's start is the like-for-like figure, $26.99.** The page offers five additions as levers. Switched on alone they
  add $2.35 (bubble deaths), $0.55 (harvest loss), $0.50 (protectant) and nothing (least medium flow, slower oxygen uptake); all
  five together give $30.49 with his plant cost, yearly charge and filter sets kept (it was $37.38 before 2026-11-21). Published
  cells is the page's other start.

### Against ten published cost studies (`study_assumptions.py`, `research_notes/study_comparison.md`)

The all-favourable example takes, for every lever, the most favourable value among this model's own favourable end, Humbird's
design and what nine other published studies assume (CE Delft 2021, Risner 2021, Negulescu 2023, Garrison 2022, Pasitka 2024,
SuperMeat 2024, Lever VC 2025, GFI 2021, GFI 2026), and does not take a value that breaks one of these limits: the nutrient floor
($2.00 a kilo of cells), the mass balance (311 g of glucose a kilo of cells), the thickest culture that still flows (Humbird's
258 g/L), the oxygen, CO₂ and waste limits the engine computes, a doubling no faster than any measured in animal cells (15 hours),
a cell no heavier than any meat cell measured in suspension (Humbird's 3 ng), and a plant repaid at a market rate of interest (8.3%
of its cost a year). One value comes from a study: tanks of 42 m³ (Negulescu 2023's smaller design). Each study's own most
favourable estimate, in 2025 dollars by consumer prices:

| study | as published | as a kilo of wet cells, 2025 $ | against the all-favourable example ($6.97) |
|---|---|---:|---|
| Humbird 2021 | $21.00 a kilo of wet cells (2018 $) | $26.92 | above |
| CE Delft 2021 | $6.43 a kilo of cultivated meat (2021 $, year not stated) | $7.64 | above |
| Risner 2021 | $1.95 a kilo of cell-based meat (2019 $), scenario 4 | $2.46 | **below** |
| Negulescu 2023 | $16 a kilo of product without depreciation | $18.15 | above |
| Garrison 2022 | $17.10 a kilo, its cheapest variant | $18.81 | above |
| Pasitka 2024 | $6.2 a pound of a product that is half cells | $21.90 | above |
| SuperMeat 2024 | $11.8 a pound without depreciation | $26.70 | above |
| Lever VC 2025 | $10 to $15 a kilo of cell mass | $10.00 | above |
| GFI 2021 | CE Delft's figure | $7.64 | above |
| GFI 2026 | prices of medium a litre only | not compared | |

(Humbird's $26.92 is his total by consumer prices alone; the $26.99 of the page escalates his capital by the plant-cost index and
is the engine's like-for-like figure.)

**The one estimate below it, and the limits it breaks.** Risner 2021's scenario 4 rests on four assumptions beyond the limits:

| what scenario 4 assumes | its value | the limit allows | the limit |
|---|---|---|---|
| cells that fill the tank (200 million a mL of 5,000 µm³) | 1,060 g of wet cells a litre | 258 | the thickest culture that still flows (Humbird 2021, Section 2.1) |
| a doubling every 8 hours | 8 hours | 15 | a growth rate no faster than any measured in animal cells (Stout 2023) |
| 45 g of glucose for a kilo of cells | 45 g | 311 | the mass balance: cells cannot be built and fuelled from less sugar than they burn |
| a cell of 5.3 ng | 5,300 pg | 3,000 | no meat cell growing in suspension has been measured heavier than Humbird's 3 ng |

With those four brought inside the limits, its own design (20 m³ batch tanks, tanks-only capital, its financing and $0.24 a litre
of medium) costs $8.62 in this engine. CE Delft 2021's $6.43 becomes $7.64 in 2025 dollars, $0.67 above the all-favourable
example; it rests on repaying the plant over 30 years at no interest, which the financing limit rejects (with it the example would
cost $6.43, its design held). Not taken and not rejected: what the plant costs to build per m³ in other studies (with a plant a
third as costly the example would cost $5.98, its design held) and their staff numbers, because the plants hold different
equipment.

**Humbird's best estimate with each study's assumptions** (`study_assumptions.modifications`, from $26.99): those that lower it
alone are a food-grade plant without clean rooms ($25.15), his yeast benchmark's financing ($25.22), CE Delft's 30 years at no
interest ($19.95), a plant a third as costly ($17.23), medium at the announced $0.20 a litre ($24.65), medium at $0.50 ($26.82) and
perfusion in 25 m³ tanks ($24.51); all of them together give $17.10. Pasitka's measured cells in continuous perfusion take it to
$685.04, and all the modifications together to $362.47.

### From Humbird's design to the all-favourable example, one lever at a time (`frontier.py`)

`frontier.ladder()` runs from Humbird's optimistic design to the all-favourable example, each lever kept moved:

| step | cells, $/kg | change |
|---|---|---|
| Humbird's optimistic design: his enhanced cells in an ordinary perfusion tank | $15.74 | |
| Cells double in 16 hours | $12.07 | −$3.66 |
| Cells of 3 ng, Humbird's, the heaviest allowed | $12.07 | nothing |
| A food-grade plant with shared medium | $9.75 | −$2.33 |
| Dialyser-grade hollow fibres as the filter | $9.50 | −$0.24 |
| Dissolved oxygen held at about half of air saturation | $9.50 | nothing |
| The cheapest tank design that passes the checks on the CO₂ loop | $7.50 | −$2.00 |
| Tanks of 42 m³ in place of 20 m³ | $6.97 | −$0.53 |
| The least medium flow at the lowest measured | $6.97 | nothing |
| Culture up to 320 g/L in place of 258 | $6.97 | nothing |
| Medium at the nutrient floor | $6.97 | nothing |

(`python frontier.py`, 2026-11-21. The path starts at $15.74, not the $15.72 of `scenarios.reference()`: `frontier` writes
Humbird's cell as its four traits.)

- **Five levers carry it:** faster cells, the cheaper plant, the cheaper filter, the tank design and the larger tank. Alone, from
  Humbird's design, the first three and the larger tank are worth $3.66, $2.89, $1.87 and $0.73. The tank design chosen for the
  end of the path costs $0.60 more alone: it is a flat tank with the column that feeds recycled oxygen, held at the density its
  loop passes, which pays only once the cells grow fast and the filter is cheap ($2.00 at that point on the path).
- **Four levers change nothing here.** The cell is already Humbird's 3 ng; ammonia, not the least flow, sets the litres of medium;
  the loop's checks hold the culture at 219 g/L, below 258; and Humbird's design already pays only for what the cells eat.
- **What is not taken.** Cleaning the medium and fat fed to the cells are not used.
- **The all-favourable example is $0.9 above the $6.1 that parity needs.** No step is shown for meat cells
  (`research_notes/frontier.md`, `gf_and_doubling_bounds.md`).

### What it would take, against what has been measured in meat cells (`scenarios.what_it_would_take`, `cell_traits.best_in_meat_cells`)

The cost of cells a long-run share needs, at the model's 14.4% of meat buyers picking cultivated meat at equal price and at 50% (no
preference), with every estimate at its most likely value; and, among the sets of traits tried (ammonia 0.14, 0.055 or 0 mol a kilo;
lactate 1.05, 0.42, 0.28 or 0 mol per mol of glucose; a doubling every 43, 36, 25.7, 20 or 15 hours; 2 ng cells; a food-grade plant
with or without shared medium; perfusion or a 20 m³ batch; the low-lactate example's other switches), the set that reaches it with
the fewest traits beyond the best measured in meat cells, then the shortest way beyond them, then the dearest. Each trait is set
against its own best measurement in meat cells: 0.14 mol of ammonia a kilo (Hubalek 2023), 1.05 mol of lactate per mol of glucose
(Pasitka 2024), a doubling every 15 hours (Stout 2023) and 3.3 ng a cell (Pasitka 2024). No odds, and no claim about how cells would
come to have a trait:

| long-run share of world meat and seafood | with this share of meat buyers picking it at equal price | cells must cost (most likely values) | the cells tried that reach it with the fewest traits beyond the best measured in meat cells | at | traits beyond the best measured in meat cells (each against its own best measurement) |
|---|---|---|---|---|---|
| 1% | 14.4% | $18.3 a kilo or less | ammonia 0.055 mol/kg, lactate 0.279 mol/mol, a doubling every 15 h, 2 ng | $15.7, a food-grade plant with shared medium, fed-batch at 20 m³ | ammonia 0.055 mol/kg wet, against 0.14 measured; lactate 0.279 mol/mol, against 1.05 measured |
| 10% | 14.4% | $3.7 a kilo or less | none of the sets tried |  |  |
| 1% | 50.0% | $28.4 a kilo or less | ammonia 0.055 mol/kg, lactate 0.42 mol/mol, a doubling every 15 h, 2 ng | $24.1, a food-grade plant with shared medium, perfusion | ammonia 0.055 mol/kg wet, against 0.14 measured; lactate 0.42 mol/mol, against 1.05 measured |
| 10% | 50.0% | $11.4 a kilo or less | ammonia 0 mol/kg, lactate 0 mol/mol, a doubling every 15 h, 2 ng | $9.7, a food-grade plant with shared medium, perfusion | ammonia 0 mol/kg wet, against 0.14 measured; lactate 0 mol/mol, against 1.05 measured |

A 1% share needs two traits beyond the best measured in meat cells at either liking: ammonia at 0.055 mol a kilo with lactate at
0.28 mol per mol of glucose at the model's own liking ($19.1, in a 20 m³ fed-batch in a food-grade plant with shared medium), and the
same ammonia with lactate at 0.42 if half of meat buyers favoured it ($29.3, in perfusion in a food-grade plant with shared medium),
each with a doubling every 20 hours. A 10% share needs $4.1 a kilo of cells at the model's own liking, below every set tried and
below parity's $6.1, and, with half of meat buyers favouring it, $12.0, which only cells that make no ammonia and no lactate and
double every 15 hours reach among the sets tried ($11.6). The sets tried keep
the low-lactate example's other switches: its filter loop, its limits of 4 mmol/L of ammonia and 35 of lactate, its 2 ng cell and
its lost runs. The all-favourable example, which takes Humbird's limits and cell, dialyser-grade fibres, 42 m³ tanks and no lost
runs, costs $7.0. `research_notes/cell_trait_routes.md` gives the evidence for each measurement. The draws
(`scenario_mc(choice, traits=...)`) can be run for any of these sets.

### Perfusion against fed-batch as the plant gets cheaper (`scenarios.plant_axis`)

The two ways of running the tank are compared here with the same assumptions on both sides: the same cells, plant, losses, medium
and estimates, each with its own tank design. A batch held by its waste makes a fifth to a half
of the kilos a perfusion tank makes, so it pays more for the plant; it pays no filter, a fed-batch crew, and loses few cells to
bubbles. So a cheaper plant narrows the gap. The table moves the plant's cost
(buildings and tanks, not the filter loop or the column) from its modelled value down to a third of it, the bands' range:

| switches as in | $/kg with the plant at its modelled cost: perfusion 20 m³ / perfusion 100 m³ / fed-batch 20 m³ / fed-batch 100 m³ | plant at 0.75× | plant at 0.5× | plant at 0.34× | fed-batch is cheaper than perfusion, both at 20 m³, with the plant below | both at 100 m³, below |
|---|---|---|---|---|---|---|
| Published cells (rung 2's switches) | 170.0 / 162.2 / 304.8 / 234.4 | 167.6 / 159.9 / 249.3 / 191.2 | 165.2 / 157.6 / 193.7 / 148.0 | 163.6 / 156.1 / 158.2 / 120.4 | 0.37× | 0.56× |
| Low-lactate example (the low-lactate example's switches, rungs 3–4) | 48.7 / 45.9 / 70.3 / 54.6 | 46.6 / 43.8 / 57.9 / 44.9 | 44.4 / 41.8 / 45.5 / 35.3 | 43.1 / 40.5 / 37.6 / 29.1 | 0.47× | 0.71× |
| Low-lactate example, plant with shared medium (rung 5) | 44.5 / 42.0 / 53.9 / 43.6 | 43.3 / 40.8 / 45.6 / 36.8 | 42.1 / 39.6 / 37.4 / 29.9 | 41.4 / 38.9 / 32.1 / 25.5 | 0.67× | 0.93× |
| Cells that make almost no ammonia or lactate (rung 6) | 27.3 / 25.3 / 31.6 / 25.6 | 26.1 / 24.1 / 27.0 / 21.9 | 24.9 / 22.9 / 22.3 / 18.1 | 24.1 / 22.2 / 19.4 / 15.7 | 0.68× | 0.96× |
| The all-favourable example's switches (rung 7) | 7.0 / 7.1 / 11.0 / 9.3 | 6.6 / 6.7 / 9.8 / 8.3 | 6.2 / 6.3 / 8.5 / 7.2 | 6.0 / 6.0 / 7.7 / 6.6 | never (0.05–1.5×) | 0.13× |

- **Fed-batch wins only on a plant at about half to nine tenths of the modelled cost, comparing tanks of the same size.**
  Perfusion is cheaper than fed-batch at the modelled plant cost in every row, at 20 m³ and at 100 m³. With the low-lactate
  example's switches a 20 m³ batch is cheaper than 20 m³ perfusion below 0.47 times the modelled plant cost, and a 100 m³ batch
  than 100 m³ perfusion below 0.71; with the shared-medium plant, below 0.67 and 0.93; with cells that make almost no ammonia or
  lactate, doubling every 36 hours, below 0.68 and 0.96 (their batch is held at 68 g/L by its waste, while perfusion reaches
  168 g/L at 20 m³ and 132 g/L at 100 m³). The published cells favour perfusion more (0.37 and 0.56): their batch is held at
  10 g/L by lactate, while perfusion reaches 179 g/L. Until 2026-11-21 this table set fed-batch at 100 m³ against perfusion at
  20 m³, which made a 100 m³ batch look cheaper than perfusion with the shared-medium plant ($43.6 against $44.5); in a 100 m³
  tank perfusion costs $42.0. A larger tank helps both ways of running from 20 to 100 m³: perfusion by 6% to 7% (not the all-favourable example's, which costs
  $0.1 more), fed-batch by 19% to 23%.
- **With the all-favourable example's switches perfusion wins at any plant cost the bands draw** ($7.0 against $11.0 at 20 m³
  and $7.1 against $9.3 at 100 m³ at the modelled cost, and still ahead at a third of it; a 100 m³ batch would win only below 0.13
  times the modelled plant cost). Its dialyser-grade fibres make holding the cells back almost free, so a batch has no filter cost
  to save. Its perfusion columns run in its own 42 m³ tank, the size its search chose. Until 2026-11-21 its fed-batch columns ran
  in that 42 m³ tank too ($9.8 at both sizes), because the example's own tank size overrode the fed-batch settings' 20 and 100 m³.
- **Perfusion's advantage over fed-batch is smaller than on 2026-11-19** where the filter is the engine's own loop: then a batch of
  the low-lactate example's cells needed a plant at a fifth of the modelled cost to win. The changes of 2026-11-20 fall mostly on
  perfusion: membranes that last 2,415 litres a m², not 3,960; a crew twice the fed-batch crew; bubbles, which kill 8% of the cells
  in a dense perfusion tank and 3% in a thin batch; and a thick culture's slower uptake of oxygen. Which is likelier to work is a
  separate question: fed-batch at 20 m³ is shown, perfusion is not, and no animal cells have been grown above about 25 m³.
- **A bigger batch helps.** A 100 m³ batch costs 19% to 23% less than a 20 m³ one with the scenarios' switches ($70.3 to $54.6 in
  the low-lactate example; `research_notes/tank_size.md`, section 10).

### How far tank design can go (`design_space.py`)

The aim of tank design is a tank where CO₂, oxygen and mixing no longer bind, so that only the thickness of the culture does
(258 g/L). `design_space.py` first prices that aim (the ordinary tank with every gas limit lifted for free), then searches every
combination of the tank options the model has, 144 designs a scenario, keeping those whose column loop passes its checks.

| case | ordinary tank | the scenario's design | cheapest design, no cage | cheapest design, with a bubble cage | perfect gas exchange |
|---|---|---|---|---|---|
| Published cells, in perfusion | $204.67 (46 g/L, CO₂) | $181.13 | $127.36 (166 g/L, the loop's checks; 5 unproven, run thinner) | $123.33 (258 g/L, thickness; 5 unproven) | **$167.26** (258 g/L) |
| 4. Low-lactate example | $54.73 (87 g/L, CO₂) | $48.68 | $47.19 (207 g/L, oxygen; 4 unproven) | $46.10 (258 g/L, thickness; 4 unproven) | **$42.81** (258 g/L) |
| 5. Shared-medium plant | $47.15 (87 g/L, CO₂) | $44.53 | $43.76 (207 g/L, oxygen; 4 unproven) | $43.22 (258 g/L, thickness; 4 unproven) | **$40.18** (258 g/L) |
| 6. Cells that make almost no ammonia or lactate | $29.74 (87 g/L, CO₂) | $27.26 | $23.53 (207 g/L, oxygen; 4 unproven) | $23.03 (258 g/L, thickness; 5 unproven) | **$24.05** (258 g/L) |
| 7. All-favourable example | $10.43 (75 g/L, CO₂) | $6.97 | $6.54 (275 g/L, the loop's checks; 6 unproven, run thinner) | $6.07 (302 g/L, the loop's checks; 5 unproven, run thinner) | **$5.49** (320 g/L) |

- **The search covers the cases run in perfusion** (since 2026-11-19). Rungs 1–3 of the ladder are batches held by their waste,
  which no tank design moves; the published cells are searched in perfusion as the cautious scenario.
- **Tank design matters most for the published cells:** $37 a kilo between the ordinary tank and perfect gas exchange ($204.67 to
  $167.26). The cheapest designs for these cells ($127.36 and $123.33) are below that ideal, because the search also lets the cells
  take their fat from the feed, which cuts their glucose, their lactate and so their medium. The same holds for the cells that make
  almost no ammonia or lactate and for the all-favourable example, whose cheapest designs feed fat too.
- **The scenarios' designs are $1.5–5.9 from the ideal:** $5.9 a kilo in the low-lactate example, $4.4 with the shared-medium plant,
  $3.2 with cells that make almost no ammonia or lactate and $1.5 in the all-favourable example. For the all-favourable example
  perfect gas exchange would give $5.49, below the $6.1 that parity needs; its cheapest design with a bubble cage gives $6.07.
- **Designs that leave only the thickness limit exist on paper,** with a bubble cage in every case but the all-favourable example
  (whose caged design is held thinner by its loop's checks) and without a cage in none.
  Each needs four to six elements nobody has run with animal cells. The cage's numbers are judgements.
- **Every scenario holds dissolved oxygen at about half of air saturation, as pharma does** (found by the search on 2026-11-16).
- **After the gas limits, the litres of medium are what is left.** In the low-lactate example every gas limit lifted saves $5.9 a
  kilo against its design; medium at the least the physics allows saves $31.8. Tables and method: `research_notes/design_space.md`.
- **A design whose loop fails at full density is run thinner** (since 2026-11-21): the culture is held at the densest density at
  which its loop passes its checks ("run thinner" in the table). That is how the recycled-oxygen column became every scenario's
  design.

### Cleaning and reusing the medium (`medium_reuse.py`; `explore(clean=...)`, `wash_price`)

After the gas limits, the litres of medium are the largest cost left. Ammonia sets them: 39 litres per kg in the low-lactate
example. Can the ammonia be taken out and the liquid reused? Partly, and the limit is the cell filter. A litre that leaves the
tank costs $0.98 in the low-lactate example, and $0.71 of that is the membranes that hold the cells back. A device that cleans the
filtered liquid (the permeate) and returns it saves the medium, the growth factors and the protectant, but the liquid has passed
the filter either way. Only a device that takes the waste out with no liquid drawn through the cell filter, such as dialysis
across the culture, saves the filter too.

**As levers of the engine and the page (since 2026-11-20; all off by default).** `floor_physics.explore` takes `clean`: "exchanger"
(an ammonium exchanger on the permeate), "electrodialysis" (of the permeate) or "dialysis" (across the culture, the dialysate
cleaned and reused, its exchange membrane at the cell filter's cost). With no share given it cleans the litres that cost least, so a
route never costs more than no route. It also takes `wash_price`: the litres beyond those that carry a kilo's nutrients only wash
waste out, and can be charged at the price of a solution of salts, buffer and glucose ($0.066 a litre, `pf_wash_price`) instead of
the medium's price. At most likely values:

| case | no cleaning | ammonium exchanger | electrodialysis | dialysis across the culture | wash litres at $0.066, no cleaning |
|---|---|---|---|---|---|
| Low-lactate example | $48.68 (39 L/kg fresh) | $47.89 (34 L) | $45.24 (18 L) | $44.83 (9 L) | $48.52 |
| Published cells in perfusion (the cautious scenario) | $181.13 (146 L) | $181.13 (146 L) | $135.54 (21 L) | $145.79 (9 L) | $179.81 |
| Humbird's optimistic design (perfusion) | $15.72 (12 L) | $15.72 (12 L) | $15.69 (12 L) | $15.72 (12 L) | $15.72 |

- **In the low-lactate example the routes save $0.8 to $3.9 a kilo.** Electrodialysis halves the fresh medium and saves $3.4,
  because what it cleans still passes the cell filter. Dialysis across the culture cuts the fresh medium to 9 litres and the cell
  filter's membranes from $22.7 to $1.7 a kilo, but its own exchange membrane is priced like the cell filter, so it saves $3.9.
- **For the published cells the waste is lactate.** The ammonium exchanger saves nothing. Electrodialysis saves $45.6 and dialysis
  across the culture $35.3.
- **Humbird's design has almost nothing to clean:** its cells need 12 litres a kilo, of which 9 leave with the cells.
- **The wash price alone saves little where the medium is already near what the cells eat:** $0.2 in the low-lactate example,
  because the price of a complete medium cannot fall below its nutrients and the growth factors in every litre, and $1.3 for the
  published cells in perfusion.

The side study behind the levers prices more routes for the low-lactate example, at the litres that cost least:

| what sets the litres of medium (4. Plus perfusion (the low-lactate example): waste washed out through a cell filter) | litres per kg of cells |
|---|---|
| ammonia, held at 4 mmol/L | 38.8 |
| the least flow the cells need for everything else | 18.0 |
| lactate, within the salt limit | 34.1 |
| the nutrients, as a concentrate | 8.9 |
| leaves with the cells, unfiltered | 6.6 |

| route | fresh medium, L/kg | cleaned and returned, L/kg | through the cell filter, L/kg | cells, $/kg | saves | pays if the device costs under |
|---|---|---|---|---|---|---|
| No reuse | 38.8 | 0 | 32.2 | **$48.68** | | |
| An ammonium exchanger on the permeate, taking 12% of the ammonia | 34.2 | 4.7 | 32.2 | **$47.89** | $0.79 | (priced by its sorbent: 0.15 mol/kg at $5/kg, used once) |
| Electrodialysis of the permeate | 18.0 | 23.1 | 34.5 | **$45.24** | $3.44 | $0.21 a litre |
| Dialysis of the permeate, dialysate thrown away | 36.3 | 2.8 | 32.5 | **$48.59** | $0.09 | $0.08 a litre |
| Dialysis of the permeate, dialysate cleaned and reused | 8.9 | 33.2 | 35.5 | **$46.49** | $2.20 | $0.20 a litre |
| Dialysis across the culture, dialysate cleaned and reused; the exchange membrane costs what the cell filter does | 8.9 | 33.2 | 2.3 | **$44.83** | $3.86 | $0.20 a litre |
| The same; the exchange membrane clears 10 L/m²/h, twice what the filter passes | 8.9 | 33.3 | 2.3 | **$32.95** | $15.73 | $0.56 a litre |
| *A perfect, free device on the permeate* | 8.9 | 29.9 | 32.2 | *$40.17* | *$8.52* | |
| *A perfect, free device across the culture* | 8.9 | 30.0 | 2.3 | *$18.77* | *$29.91* | |

| scenario | no reuse | exchanger on the permeate | electrodialysis of the permeate | dialysis of the permeate, dialysate reused | dialysis across the culture, at the filter's cost | the same, at twice the filter's clearance | perfect and free, on the permeate | perfect and free, across the culture |
|---|---|---|---|---|---|---|---|---|
| Cautious: the best meat cells measured so far, in perfusion | **$181.13** | $181.13 | $135.54 | $153.43 | $145.79 | $91.18 | $123.46 | $25.13 |
| 4. Plus perfusion (the low-lactate example): waste washed out through a cell filter | **$48.68** | $47.89 | $45.24 | $46.49 | $44.83 | $32.95 | $40.17 | $18.77 |
| 7. Plus everything else at its favourable end (the all-favourable example) | **$6.97** | $6.97 | $6.70 | $6.97 | $6.91 | $6.89 | $6.63 | $6.58 |

- **Cleaning the permeate is worth about $1–3.5 a kilo in the low-lactate example:** $0.8 with an ammonium exchanger, $3.4 with
  electrodialysis (to $45.24), $2.2 with dialysis if the dialysate is itself cleaned. A perfect, free device would save $8.5. A
  device on the permeate must take more than 73% of the waste from a litre in one pass before it saves anything.
- **Cleaning across the culture is worth more, and is less proven:** $3.9 if the exchange membrane costs what the cell filter
  does, $15.7 (to $32.95) if it clears twice the litres per m², as a haemodialyser does on blood for a few hours. That clearance
  is a dialyser's data-sheet figure (checked 2026-11-21: 278 mL/min of urea over 1.8 m²), held for hours on blood, not weeks in a
  culture. The limit is $29.9.
- **For the published cells the waste is lactate, and the routes differ.** Priced in perfusion (the cautious scenario, $181.13;
  rung 1 is a batch with nothing to reuse), an ammonium exchanger saves them nothing. Electrodialysis, which also takes lactate,
  saves $45.6, and the best route modelled $90.0. That still leaves them at $91, against the low-lactate example's $48.68 with no
  reuse.
- **The evidence is thin.** Electrodialysis took over 90% of ammonium and 99% of lactate from medium in one report, cited in a
  book and not found; dialysis held a dense CHO culture for 10 days at the bench; a reused dialysate exists only in patent claims.
  The cost of electrodialysis per litre is an estimate made for this model. What these devices do to growth factors and nutrients
  over many passes has not been measured.
- **Reuse does not replace better cells.** In the all-favourable example the cells make so little waste, and the filter costs so
  little, that the routes priced here save at most $0.3, and a perfect, free device $0.4.
- Sources, sensitivity and the experiments that would settle it: `research_notes/medium_reuse.md`.

### If perfusion cannot be run at 20 m³

The low-lactate example and the rungs above it use a perfusion tank, which nobody has run above about 4 m³. Without cell
retention a tank is held by the waste mass balance: its density is at most 1.3 times the waste level perfusion is held to, over the
waste a kilo makes. The low-lactate example costs **$70–75** a kilo in a stirred tank in fed-batch or fill-and-draw at that cap
(37 g/L), and **$95–100** at the 27 g/L reported for meat cells at 20 m³, against $48.68 in perfusion. The all-favourable
example goes from $6.97 to $9.13 in fill-and-draw and $11.03 in fed-batch at its cap of 120 g/L (or $28–37 at 27 g/L); every
fallback costs more than perfusion. The food-grade plant with shared medium cushions the low-lactate example most: $44.53 to
$50.60 (fill-and-draw, which keeps its two small seed trains). The published cells stop at 10 g/L unwashed, because of their
lactate, and cost $316 in fed-batch (`research_notes/no_perfusion_downside.md`; `python downside.py`, 2026-11-21).

### Against what companies report (`industry_claims.py`)

Company figures are usually operating cost (COGS): medium, labour, utilities and consumables, with nothing for the plant. Every
scenario cost here includes a yearly charge on the plant. Split the same way:

| case | cells, $/kg | of which: charge on the plant | operating cost | of which: filter membranes | medium and growth factors |
|---|---|---|---|---|---|
| 1. Published cells, fed-batch | $316.1 | $222.3 | **$93.8** | $0.0 | $33.8 |
| 2. Plus process changes | $304.8 | $222.3 | **$82.6** | $0.0 | $22.5 |
| 3. Plus cells that make less lactate, fed-batch | $70.3 | $49.6 | **$20.7** | $0.0 | $6.3 |
| 4. Low-lactate example (perfusion) | $48.7 | $10.8 | **$37.9** | $22.7 | $7.9 |
| 5. Plus a plant with shared medium | $44.5 | $6.3 | **$38.2** | $22.7 | $7.9 |
| 6. Plus cells that make almost no ammonia or lactate | $27.3 | $5.7 | **$21.6** | $10.2 | $5.3 |
| 7. All-favourable example | $7.0 | $1.9 | **$5.1** | $0.1 | $2.2 |
| Humbird's optimistic design | $15.7 | $7.4 | **$8.3** | $1.9 | $2.2 |

| the low-lactate example's cells, 20 m³ tank drained and refilled (as Vow runs), in | cells, $/kg | charge on the plant | operating cost | at the 27 g/L reported for meat cells |
|---|---|---|---|---|
| the scenario's food-grade plant ($813k per m³) | $74.8 (37 g/L) | $54.8 | **$20.0** | $100.1 (operating $26.3) |
| a food-grade plant with shared medium ($452k per m³) | $50.6 (37 g/L) | $30.5 | **$20.1** | $67.5 (operating $26.4) |
| a yeast plant with what animal cells need ($233k per m³) | $35.8 (37 g/L) | $15.7 | **$20.1** | $47.5 (operating $26.3) |

| who | figure | a cost of | capital in it? | kind | checked by | date |
|---|---|---|---|---|---|---|
| [Lever VC (investor), across several companies](https://agfundernews.com/humbird-was-spectacularly-wrong-on-cultivated-meat-economics-says-report-as-vow-predicts-it-will-soon-be-unit-margin-positive) | $10–15/kg; some below $10/kg | cell mass; wet or dry not stated; scale not stated | excluded (COGS) | vetted under NDA | the investor; data not public | April 2025 |
| [Lever VC (investor)](https://agfundernews.com/humbird-was-spectacularly-wrong-on-cultivated-meat-economics-says-report-as-vow-predicts-it-will-soon-be-unit-margin-positive) | medium at $1/L or less, several under $0.50/L | medium per litre; litres per kg not stated | not applicable | vetted under NDA | the investor; data not public | April 2025 |
| [Gourmey (now PARIMA), modelled by Arthur D. Little](https://parima.bio/blog/gourmey-sets-new-cost-benchmark-in-cultivated-meat-production-with-3-4-lb-model-independently-validated) | €7/kg at 5,000 L scale; medium €0.20/L | production cost; product basis not stated | not stated | model | a consultancy, commissioned by whom not stated | May 2025 |
| [Arthur D. Little (consultancy)](https://www.adlittle.com/en/insights/viewpoints/cultivated-meat-one-year) | low €40s/kg in 2026; about €10/kg by 2030 | finished product | not stated | model | nobody named | 2025 |
| [SuperMeat (company white paper)](https://supermeat.com/wp-content/uploads/2024/11/A-Deep-Dive-Into-Cost-Effective-Cultivated-Meat-Production-V.pdf) | $29.5/kg with depreciation ($26.0 without) | 100% chicken cells, wet; 10 L runs scaled on paper to 25,000 L | depreciation only | model from runs | nobody; not peer reviewed | November 2024 |
| [Vow (company)](https://agfundernews.com/humbird-was-spectacularly-wrong-on-cultivated-meat-economics-says-report-as-vow-predicts-it-will-soon-be-unit-margin-positive) | a 20,000 L bioreactor built for “well under $1 million” | one vessel; whether piping and installation are in it not stated | a capital cost | company statement | nobody | April 2025 |

Reading it (company figures are claims; none has been audited):

- **On operating cost the model is above what companies claim.** Lever VC reports $10–15 a kilo of cell mass for several
  companies, some below $10. The low-lactate example's cells in a tank drained and refilled, as Vow runs its 20 m³ tank, cost
  $20.0–20.1 a kilo to operate (utilities charge the building's power and the cleaning of the tank to the kilos it makes). With
  cells that make almost no waste, in perfusion, the operating cost is $21.2 to $21.6, and the all-favourable example $5.1. The low-lactate
  example itself, in perfusion, costs $37.9 to operate, three-fifths of it filter membranes. Cells that make less waste than the
  low-lactate example's, or a batch run to higher waste levels, would bring the batch's figure towards the investor's range.
- **The difference is the plant.** A tank drained and refilled at 37 g/L makes little in a year, so the plant charge is $16–55 a
  kilo depending on what the plant costs. Company COGS leave this out. Gourmey's €7/kg does not say whether it includes it.
- **The plant's price is the number most worth checking against industry.** In a plant built like a yeast plant with what animal
  cells need ($233k per m³), the low-lactate example's cells drained and refilled cost $35.8, $12.9 below the low-lactate example in
  perfusion ($48.7), with no filter to hold the cells back. Nobody has published what such a plant costs to build for animal cells;
  Vow says its 20 m³ vessel cost well under $1 million, without saying whether piping and installation are in that.
- **The density is the other open number.** The 37 g/L above is the model's waste limit for these cells. At the 27 g/L reported for
  meat cells at 20 m³ the same cases cost $47–100 a kilo, $26 of it operating cost.

### Vessel types and operating modes

A stirred tank and perfusion are not alternatives: one is a vessel, the other a way of running it. `vessels.py` changes only
those two and holds the rest (research_notes/vessels_and_modes.md has both grids, with sources).

| Humbird's optimistic design, $/kg | Batch | Fed-batch | Fill-and-draw | Chemostat | Perfusion |
|---|---|---|---|---|---|
| Stirred tank, 20 m3 | 70.48 | 17.32 | 16.50 | 36.67 | **15.72** |
| Stirred tank with a bubble cage, 20 m3 | 72.03 | 17.29 | 16.50 | 37.12 | 14.70 |
| Airlift, 20 m3 | 67.90 | 38.35 | 36.20 | 35.20 | 29.96 |
| Single-use bag, 5 m3 | 1,189 | 284.32 | 48.93 | 113.14 | 35.56 |
| Packed bed, 65 L | 32,689 | as batch | not possible | not possible | 32,683 |
| Hollow fibres, 0.5 L | 361,225,720 | as batch | not possible | not possible | 361,225,714 |

In the low-lactate example the stirred tank costs $102.01, $70.32, $74.75, $123.79 and $48.68 across the same modes (the waste
mass balance since 2026-11-19). Perfusion includes the filter loop that holds the cells back
(`retention.py`); the other modes need no such device. The vessel grids are `vessels.markdown_table()`; both are in
`research_notes/vessels_and_modes.md` (`python vessels.py`, 2026-11-21).

- Perfusion is the cheapest mode in both settings, in a stirred tank ($15.72 and $48.68) or in one with a bubble cage ($14.70
  and $46.16). Nobody has run animal cells in perfusion above about 4 m3, and nobody has run the cage with cells in suspension.
- Fed-batch and fill-and-draw, which run at 20 m3 today, cost $16.5–17.3 in Humbird's optimistic design and $70–75 in the
  low-lactate example. Since 2026-11-21 Humbird's cells reach 116 g/L in a batch, held by their waste (the least medium flow had
  held them at 92), so perfusion saves only $0.8–1.6 there. The low-lactate example's cells make more ammonia, and a culture that is
  not washed out stops at 37 g/L, 1.3 times the waste level perfusion is held to. These costs assume 37-116 g of cells a litre.
  Nobody has shown that density for meat cells at this size: the one 20 m3 plant for meat cells reports harvests of about 27 g/L.
- **The airlift does not beat the stirred tank.** Since 2026-11-20 it follows the stirred tank's mixing rule, and its tall column
  mixes a thick culture poorly: mixing holds it at 45 g/L in Humbird's optimistic design ($29.96 in perfusion, against $15.72) and
  at 87 g/L in the low-lactate example ($52.73, against $48.68). Only in the modes held by waste, where its culture is thin anyway,
  is it a little cheaper there ($67.66 in fed-batch against $70.32). How it compares depends on its shape (TODO). Nobody has run an
  airlift in perfusion with animal cells.
- A stirred tank with a bubble cage (2026-11-16): an inner cylinder of fine mesh holds a strong sparger, and the cells live in the
  ring around it with soft bubbling. Only medium crosses the mesh, so the cage's gas counts at 80% of its strength (a judgement),
  and since 2026-11-20 its cells are charged bubble deaths only on the gas they meet. In perfusion it costs $14.70 in Humbird's
  optimistic design and $46.16 in the low-lactate example, against $15.72 and $48.68 in the plain tank. Caged aeration exists only
  with microcarriers in small tanks.
- A single-use bag pays for a bag each run; it comes closest to steel in perfusion.
- Packed beds and hollow fibres cost thousands of dollars a kilo or more as built.

## 2. What share a price buys

Here the low-lactate example means cells that make 0.14 mol of ammonia a kilo (the published figure) and 0.42 mol of lactate per mol of glucose (the best published is 1.05), double every 36 hours and weigh 2 ng, grown in perfusion in a 20 m³ tank in a food-grade plant with medium at $0.20 a litre. The all-favourable example (`scenarios.all_favourable`) means every lever at its most favourable value among this model's own favourable end, Humbird's design and nine other published studies, within the model's limits: cells of 3 ng that make 0.054 mol of ammonia a kilo and 0.28 mol of lactate per mol of glucose, double every 16 hours and tolerate 5 mmol/L of ammonia and 50 of lactate, grown in perfusion in 42 m³ tanks in a food-grade plant with shared medium, with medium at the cost of its nutrients, no growth factors bought, no lost runs and dialyser-grade hollow fibres holding the cells back, and 58.6% of meat buyers picking it at the same price.

Shares of a single meat here are shares of meat buyers (cultivated over cultivated plus conventional, as in every reported share).
The model's inputs are set as shares of all shoppers' choices, with plant-based meat and meals without meat; that figure is given
second where a reader needs it to match the inputs.

| if cultivated meat, at equal price and once familiar… | share of meat buyers | share of all choices (the model's input) |
|---|---|---|
| tastes as good and is seen as real meat | **14.4%** (the setting) | 13% (drawn between 3% and 52%) |
| tastes a little worse (0.8) / noticeably worse (0.6) | 9.8% / 6.6% | 9% / 6% |
| tastes as good, and “no slaughter” matters (0.5 / 1.0 / 1.5) | 17.7% / 21.8% / 26.9% | 15% / 18% / 21% |
| tastes as good but isn't seen as real meat (liking otherwise held) | 4.0% | 4% |

At first contact it gets 4.3% of all choices; the US choice experiment found 5% of meat buyers and 4% of all choices. For mince
against US minced beef or pork cuts at $12 a kilo (US, long run) it gets 12.7% of meat buyers at the all-favourable example's cost
(1.1 times the price), 3.1% at the cost of Humbird's optimistic design (2.1 times), 0.30% at the reported cost (4.3 times) and 0.09%
at the low-lactate example's (5.9 times). The share does not reach everyone as the price
falls: 27% of meat buyers at half the price of meat and 45% if free, so about 55% of meat buyers never pick it.

Checks, in shares of all choices. At equal price cultivated meat takes 11.9 points from conventional meat, 0.05 from plant-based
meat (whose share is anchored at 0.4% of meat by volume since 2026-11-20) and 1.0 from meals without meat. In proportion it takes
about the same from each: 13% of conventional's sales, 12% of plant-based's and 9% of the meatless meals'. So total meat eaten,
conventional and cultivated, rises by about 1%. The model has no switching between kinds of meat. Since 2026-11-20 conventional
meat's price falls as cultivated meat takes its sales: by (1 − share)^0.38, from the supply and demand elasticities
(`meat_market.conv_exponent`), which matters only where the share is large (the all-favourable example loses 4.1 points to it). The same model predicts about 15% for plant-based milk, close to reality (a weak test, since milk's inputs
are set by hand).

**A harder check, and what it changed.** Six premium animal products show what share a product takes when it is
the ordinary one plus a virtue, at a higher price:

| product (US) | price vs conventional | share of volume | model at κ = 4 | model at κ = 8.5 |
|---|---|---|---|---|
| organic milk | 1.63× | 7.0% | 26.5% | 10.2% |
| cage-free eggs (before mandates) | 1.63× | 2.8% | 26.5% | 10.2% |
| omega-3 eggs | 1.63× | 6.1% | 26.5% | 10.2% |
| organic eggs | 2.19× | 2.2% | 12.7% | 1.6% |
| organic chicken | 1.91× | 4.6% | 18.6% | 4.1% |
| all organic meat | 1.50× | 2.2% | 30.7% | 15.2% |

κ is how many times more price-sensitive a cultivated product is than meat as a whole. This table is the model with every shopper
alike, which is how κ was set, and its shares are of all choices. At 4 it over-predicted these products about sixfold. The best fit is κ = 10. The model uses 8.5,
where the typical miss is a factor of 2.7. κ acts only on cultivated meat's price difference from the conventional meat beside it,
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
  misfit is 4.2, against 17.1 for the normal as it was and 10.0 for a logistic (4.0, 13.7 and 8.3 on 2026-11-19: the salmon
  part is computed on the model's premium products at the scenarios' costs, which rose; the shape was not refitted). So the experiment and the premium meats are no
  longer independent checks of the model: it was fitted to them.
- **The data pin the shape loosely.** The misfit is least at a tail of 3 and a spread of 3.7; the model's 4 and 3.9 are 14% above
  that, and 4 rather than 3 is a choice, not a fit. A mixture of two groups fits better still (2.7) and was not chosen: its best
  fit is a small block of shoppers who buy at almost any price, which nothing measured shows.
- **Between one and four times the price of meat the fitted spread gives less than the normal spread it replaced, because it is
  narrower in the middle.** What matters there is how many shoppers are moderately keener than average, and the t puts more
  shoppers close to the average and fewer moderately above it. No data measure that part of the spread beyond the one
  experiment. The all-favourable example ($7.0 a kilo) has most of its products at one to three times the price of their meat or
  below it, and takes 23.4% with its own demand; its share under the other shapes has not been recomputed. The low-lactate
  example's sales are in the tail, which the t makes heavier.
- **Three worries remain** (the note's section 6): the all-favourable example's fall; a response to a falling price still more than twice
  farmed salmon's; and the tail above five times the price of meat, which is an extrapolation (the premium data stop at 3.6
  times), although 31% of the low-lactate example's first sales come from products above five times and 40% from products above four.
  The note lists a fourth, first contact at 4.3% against a measured 5%; read as 5% of meat buyers and 4% of all choices,
  the experiment is matched (next paragraph).

What the model had been assuming about the long run, and what three readings of it give. In this table and the next, the share at
equal price and the share of a meat at each price are shares of all choices, the scale of the choice experiment and of the model's
inputs; the world shares are shares of the meat sold:

| the long run | share at equal price | share of a meat at 1.25×, 1.5×, 2×, 3×, 4× its price | world share, 1. Published cells | world share, 4. Plus perfusion (the low-lactate example) | world share, 7. Plus everything else at its favourable end (the all-favourable example) |
|---|---|---|---|---|---|
| first contact (as measured) | 5% | 3.5%, 2.5%, 1.3%, 0.5%, 0.2% | under 0.001% | 0.03% | 2.4% |
| novelty fades by what the model assumes | 15% | 10.8%, 7.6%, 3.8%, 1.1%, 0.4% | under 0.001% | 0.05% | 6.4% |
| shoppers indifferent on average (the premise before 2026-11-18) | 52% | 41.9%, 32.7%, 18.2%, 4.6%, 1.3% | under 0.001% | 0.1% | 21.6% |
| the model before 2026-11-18 (every shopper alike) | 52% | 31.3%, 16.1%, 3.2%, 0.1%, 0.003% | under 0.001% | under 0.001% | 12.2% |
| premium real meats (the curve fitted to sixteen) | | —, 5.7%, 3.7%, 1.5%, 0.6% |  |  |  |

With every shopper alike, the fading of first-contact wariness took cultivated meat from 5% to half the market at equal price.
With the spread, the same fading (2.8 utils) takes it to 15% of all choices (about 17% of meat buyers) if the experiment's 5% is
read as a share of all choices. The model's setting stays at 13% of all choices (`equal_price_share`), 14.4% of meat buyers: read
back through the t spread it gives 4.3% of all choices at first contact, and the experiment measured 4% of all choices (5% of meat
buyers), so the setting reproduces it. Half of meat buyers would need the
average shopper to end up indifferent between the two meats, with the appeal of no killing outweighing the "unnatural" image.
Across the three readings the low-lactate example's share runs from 0.03% to 0.1% and, at the all-favourable example's cost with the
ordinary demand, from 2.4% to 21.6%; the model gives 0.05% and 5.6%. The long-run share at equal price is the model's largest
unknown on the demand side. The bands draw it from a distribution whose median is 13% of all choices and whose 5th and 95th
percentiles are 3% and 52%. Two outside readings, both on the model's scale of all choices, bracket the setting: the literature review puts
the median at 10%, about 11% of meat buyers (`research_notes/what_drives_choice.md`), and a reading of how other foods made by
distrusted processes fared puts it near 18%, about 20% of meat buyers (`research_notes/demand_heterogeneity_evidence.md` §6). For
the low-lactate example the cost matters as much: across 8 in 10 of its cost draws ($39–76) the share runs from about 0.1% to 0.009%.

**The model's response to price, against four measurements** (`demand_checks.py`, `research_notes/demand_checks.md`). The model
passes three and fails one. The first three rows are now what the spread was fitted to, so a pass is a fit, not a test:

| what was measured | measured | the model | the model before 2026-11-18 |
|---|---|---|---|
| Cultivated meat at first contact and equal price: own-price elasticity (choice experiment, simulated from its fitted model) | about -1.5 (-1.1 to -1.65 across its arms) | -1.38 | -3.27 |
| Share of a meat at 3 times the ordinary one's price (sixteen premium real meats, fitted) | 1.5% | 0.9% | 0.1% |
| A premium product getting cheaper: percent more volume per percent lower price (farmed salmon) | 1–1.5 | 3.7–4.2 (organic chicken, heritage pork, premium fish fillets and shrimp, sushi-grade seafood: the premium products still dearer than their meat) | 3.0–3.4 (recorded on 2026-11-18 at that day's costs; not recomputed) |
| Plant-based meat's own-price elasticity (US retail; the category is about -1.3) | -1.23 | -1.30 | -2.89 (with no committed buyers, the model before 2026-11-21's fourth batch) |

- **It is inside the choice experiment's range at equal price** (−1.38 against about −1.5; the arms run from −1.1 to −1.65).
- **It is on the low side of premium real meats at 3 times the price** (0.9% against 1.5%).
- **The salmon check still fails.** The model's premium products that are still dearer than their meat respond to a falling
  price at 3.7–4.2, where farmed salmon showed 1–1.5: more than twice the top of the measured range. It was 3.6–3.7 before
  2026-11-20; at the higher costs sushi-grade seafood is also still dearer than its fish, and every product sits further up the curve.
  A price-insensitive class of shoppers for every product, with the spread refitted, does not close it either (1.3–4.3 across
  the fits that meet the choice experiment's requirements; `research_notes/demand_checks.md` section 6): farmed salmon's buyers
  liked it and paid little attention to price, while for cultivated meat the shoppers who pay little attention to price are, on
  the evidence, the ones who like it least.
- **Plant-based meat passes since 2026-11-21:** the model gives -1.30 against a measured -1.23 (the category about −1.3). Its
  buyers are a committed minority (7% of households buy 82% of it) who respond less to its price, and the model now has them: 7%
  of shoppers who buy 82% of the mainstream's plant-based meat and respond a quarter as strongly to its price (Tonsor, Lusk &
  Schroeder 2021), a measured input, not fitted to the elasticity. Without them it was -2.89. They raise the ordinary shoppers'
  real-meat weight (3.40 to 5.11 utils), so cuts that are part plant protein are liked less: the all-favourable example falls from
  24.7% to 23.4% with its own demand (`research_notes/demand_checks.md` section 5).

Once familiar, the model's response to its own price is −1.4 at equal price, −2.7 at twice the price, −3.4 at three times and
−3.6 at four times. With every shopper alike, across the single price responses the measurements could support, the low-lactate example's share
runs from under 0.001% to 0.3%; the model gives 0.05%. At the all-favourable example's cost, with the ordinary demand, the model
gives 5.6%, and every shopper alike would give 12.2%: close to parity a single kind of shopper buys far more.

**Anchored on premium real meats** (`premium_curve.py`, `research_notes/premium_curve.md`). Ten more premium products, up to
3.6× the price (pasture-raised eggs, organic and Label Rouge chicken in France, Britain, Denmark and Switzerland), show share falling
as the premium rises: US eggs from 8.6% at 2.0× to 0.3% at 3.2×; French chicken from 13% at 1.8× to 1% at 2.7×. A curve fitted to
the sixteen products misses them by a typical factor of about 2.4, with shoppers about a quarter as price-sensitive as in the
model with every shopper alike. Placing cultivated meat on that curve, corrected for what differs from a welfare label (no killing
+5% of meat's price, novelty −30% with half of it fading, unnatural −20%; hypothetical studies), gives the low-lactate example **0.01%** of world
meat and seafood in the long run (0.00–0.03%), against the model's 0.05%. The curve is a third of the model, and the model is
above the curve's range. At the all-favourable example's cost the curve gives 2.3% (1.0–3.7%) against the model's 5.6% with
the low-lactate example's demand: the model is 2.4 times the curve and above its range. The premium data start at 1.5× the price, and limited
distribution holds premium labels down, so the curve is weakest near parity.

**Premium buyers, and a welfare label on the same shelf** (`premium_buyers.py`, `research_notes/premium_buyers.md`; on the model
with every shopper alike, which gives the low-lactate example under 0.001% and the all-favourable example's cost 12.19%). If about 10% of shoppers were habitual premium
buyers who treat cultivated meat as a premium meat, with a welfare label at 2× beside it, the low-lactate example's long-run share would be 0.02%
of world meat and seafood (0.06% if they value no killing at a whole extra meat price), and at the all-favourable example's cost 12.49% (13.88%).
For comparison the main model, with its spread of liking, gives 0.05% and 5.58%: its tail does for the low-lactate example more than this
group of buyers would, unless they value no killing very highly, and near parity its spread gives less than a model with every shopper alike. Cultivated meat would take 17% of its sales from the label (15% at the high value) on the logit's
proportional assumption. Nothing in this study takes the low-lactate example past 0.1%. Its premise, that buyers of organic and welfare meat are
cultivated meat's keenest buyers, is contradicted by the evidence (`research_notes/demand_heterogeneity_evidence.md`). No
setting of the model was changed by it.

**Cost falling as the market grows** (`market_size_loop.py`, `research_notes/market_size_loop.md`; every share here uses the
model's ordinary demand, 14.4% of meat buyers at equal price). The membrane is priced at a pharma price ($1,450 a m²) and the plant
at current equipment prices. If a food-grade membrane supplier appears once demand passes a million m² a year ($150 a m², then 18%
cheaper for each doubling, to $50) and the plant gets 10% cheaper for each doubling of installed tanks, cost and share can be solved
together.

- **The low-lactate example comes to rest at $24.05 a kilo of cells and 0.48%** (from $48.68 and 0.05%). There is one resting
  point: started from above it also ends at $24.05. The all-favourable example's cells, with the ordinary demand, come to rest at
  $6.30 and 6.27% (from $6.97 and 5.58%): $0.16 above parity ($6.14). Their filter is already dialyser-grade fibre, so only the
  plant's learning moves them.
- **The margin over the membrane switch is thin.** The low-lactate example's first sales need 2.4 times the membrane area that
  brings a food-grade supplier. Its premium products alone do not reach the switch; ordinary cuts carry it.
- **With slow learning the low-lactate example has two resting points.** If the switch needs three times the demand, a start
  from its own cost stays there ($48.38 and 0.05%), and only a start from above the switch ends lower ($30.30 and 0.24%).
- **This depends on the far tail of the spread of liking.** The low-lactate example's first sales are what the tail decides:
  two-fifths of them are of products at more than four times the price of their meat, where there are no data.
- **With the demand anchored on premium real meats there is no crossing.** The curve fitted to premium real meats gives the
  low-lactate example 0.015% at its own cost, a third of the model's 0.045%; those sales need 0.76 million m² of membrane, short
  of the switch, so it stays at $48.25 and 0.015% (`research_notes/market_size_loop.md` section 5).
- **The published cells sell too little to start.** About a thousand tonnes, and learning barely moves their cost.
- The switch itself is a judgement: no price is published for a steam-tolerant food-grade module. The study changes no setting of
  the model.

## 3. By type of meat

Here the low-lactate example means cells that make 0.14 mol of ammonia a kilo (the published figure) and 0.42 mol of lactate per mol of glucose (the best published is 1.05), double every 36 hours and weigh 2 ng, grown in perfusion in a 20 m³ tank in a food-grade plant with medium at $0.20 a litre. The all-favourable example (`scenarios.all_favourable`) means every lever at its most favourable value among this model's own favourable end, Humbird's design and nine other published studies, within the model's limits: cells of 3 ng that make 0.054 mol of ammonia a kilo and 0.28 mol of lactate per mol of glucose, double every 16 hours and tolerate 5 mmol/L of ammonia and 50 of lactate, grown in perfusion in 42 m³ tanks in a food-grade plant with shared medium, with medium at the cost of its nutrients, no growth factors bought, no lost runs and dialyser-grade hollow fibres holding the cells back, and 58.6% of meat buyers picking it at the same price.

Shares in this section are at most likely values, and each is a share of that meat sold (of its buyers). "Price against that
meat" is the shop price of the cultivated product over the price of the meat it sits beside. A cut costs less than mince per kilo
here, because a fifth of it is plant protein.

**The low-lactate example and the all-favourable example, world.**

| type of meat (world) | its price, $/kg | its share of all meat and seafood | Low-lactate example: price against that meat | Low-lactate example: share of that meat | All-favourable example: price against that meat | All-favourable example: share of that meat, shoppers favouring it (58.6% of meat buyers at equal price) | All-favourable example: share of that meat, the low-lactate example's demand (14.4%) |
|---|---|---|---|---|---|---|---|
| chicken, minced or processed | 5 | 11.3% | 14.2× | 0.004% | 2.9× | 9.1% | 1.8% |
| chicken cuts | 8 | 15.3% | 7.6× | 0.02% | 2.0× | 14.4% | 2.7% |
| organic chicken | 13 | 0.1% | 4.7× | 0.06% | 1.2× | 31.0% | 6.3% |
| duck and goose, whole | 7 | 2.1% | 10.2× | 0.01% | 2.1× | 20.7% | 4.0% |
| duck and goose cuts | 10 | 0.8% | 6.1× | 0.04% | 1.6× | 22.7% | 4.3% |
| pork, processed | 6 | 13.3% | 11.8× | 0.007% | 2.4× | 14.7% | 2.8% |
| pork cuts | 9 | 14.1% | 6.8× | 0.03% | 1.8× | 18.5% | 3.5% |
| heritage pork | 16 | 0.1% | 3.8× | 0.1% | 1.0× | 41.7% | 9.5% |
| beef mince | 11.2 | 7.5% | 6.3× | 0.03% | 1.3× | 44.1% | 10.2% |
| beef steaks and cuts | 20.4 | 7.3% | 3.0× | 0.2% | 0.8× | 61.4% | 19.1% |
| prime beef and wagyu | 45 | 0.2% | 1.4× | 2.1% | 0.4× | 92.8% | 72.1% |
| sheep and goat | 14 | 4.2% | 4.4× | 0.08% | 1.1× | 39.2% | 8.6% |
| seafood, canned or minced | 7 | 6.6% | 10.2× | 0.01% | 2.1× | 20.7% | 4.0% |
| whole fish and ordinary fillets | 7 | 13.4% | 8.7× | 0.02% | 2.3× | 10.6% | 2.1% |
| premium fillets and shrimp | 20 | 4.0% | 3.0× | 0.2% | 0.8× | 54.0% | 14.8% |
| sushi-grade fish | 35 | 0.4% | 1.7× | 0.7% | 0.5× | 83.0% | 45.1% |
| rabbit | 14 | 1.0% | 4.4× | 0.08% | 1.1× | 39.2% | 8.6% |
| **all meat and seafood** | | 100% | | **0.05%** | | **23.4%** | **5.6%** |

- **The low-lactate example sells most where meat is dear, and a little everywhere.** Beef steaks are 31% of its sales, premium
  fillets and shrimp 14%, pork cuts 9%, prime beef 8%, chicken cuts and sheep and goat 7% each. Chicken and pork cuts sell although
  cultivated meat costs about seven times as much as they do: these are large markets, and the tail of the spread of liking
  leaves a few meat buyers in ten thousand to cultivated meat at that price. It takes 0.05% of meat proper and 0.05% of seafood.
  Two-fifths of these sales (41%) are at more than four times the price of the meat, beyond the 3.6 times at which the premium
  meats behind the fit stop.
- **The all-favourable example sells everywhere, if shoppers favour it.** It takes 14.4% of chicken cuts at 2.0 times their price
  and 14.7% of processed pork at 2.4 times, and most of beef steaks and seafood where it is cheaper than the meat beside it. With
  the ordinary demand the same cost gives 2.7% and 2.8% of those two, and the total is 5.6%, not 23.4%.

**The reported cost and Humbird's optimistic design, US.** At the cost a company reports ($34.4 a kilo of cells) and at Humbird's
optimistic design ($15.7), with the low-lactate example's demand:

```
                            reported cost       Humbird's optimistic design
  meat type          $/kg    R     share        R     share
  chicken mince       5   10.25    0.0%       5.10    0.3%
  chicken cuts        9    5.00    0.2%       2.72    1.1%
  beef mince         11    4.66    0.2%       2.32    2.3%
  beef steak         20    2.25    1.1%       1.22    5.9%
  prime beef, wagyu  45    1.00    6.1%       0.54    21.3%
  pork (processed)    8    6.41    0.1%       3.19    1.1%
  pork cuts          12    3.75    0.3%       2.04    2.1%
  seafood fillet     24    1.88    1.5%       1.02    7.6%
  sushi-grade fish   40    1.13    4.3%       0.61    16.2%
  TOTAL by weight: at the reported cost 0.4%, in Humbird's optimistic design 2.3%
```

At the reported cost prime beef and sushi-grade fish sell best (6.1% and 4.3% of their small markets), with fillets and steaks
at 1.1–1.5% and the other rows of the table under half a percent. In Humbird's optimistic design prime beef takes 21%, sushi-grade
fish 16%, fillets 7.6% and steaks 5.9%; beef mince takes 2.3%, pork 1.1–2.1% and chicken mince 0.3%. The world totals are 0.16% and
1.4%. The US totals count the 10.2% of the US closed to cultivated meat by state law as taking none.

**What a cut costs.** A steak or fillet made from cells grown in suspension is 80% cells bound with plant protein ($2 a kilo), plus
$2 a kilo to assemble it after harvest (binding, setting, slicing, yield loss), on top of the forming and packing every product
already pays in the shop add-on. Companies have dropped growing tissue on a scaffold in a
second bioreactor; it would add about $10 a kilo. No study has costed assembly for cultivated meat, so the $2 (range $0.5–7) comes
from plant-protein extrusion, surimi forming and binder prices. The larger unknown is the cell share: the whole cuts sold or
approved so far are 10–30% cells, and no cut made mostly of suspension-grown cells has been shown to have the texture of meat. When
cells cost more than about $12 a kilo, a cut costs less than mince, because a fifth of it is plant protein. Shoppers are taken
to like a cut less than mince in proportion to the plant protein in it (METHODS.md, "Step 3"), so fewer cells are cheaper and
less liked. The low-lactate example's share is 0.03% if a cut is all cells, 0.05% at 80%, 0.13% at 50% and 0.32% at 30%. Both the cell share and
the assembly cost are drawn in the bands (`research_notes/structuring_cost.md`).

**With the cells that have been published.** Humbird's optimistic design assumes an efficient model cell for every species. Using
each species' published doubling time and cell size in the same plant, and for fish a lower tolerance of CO₂
(chicken and turkey cost 2.4× as much, beef 1.75×, seafood 1.6×; no data for pork), the US total in that
plant is 1.0%, not 2.3% (world 0.6%, not 1.4%; Europe 1.7%, not 4.2%; `meat_market.species_market`, recomputed in the fourth
batch of 2026-11-21).
The cell data are thin (METHODS.md, "Species costs in the
market model").

**Seafood rests on an untested assumption.** Seafood fillets take 7.6% in Humbird's optimistic design (US). That assumes fish cells
tolerate as much dissolved CO₂ as pharma cells do. Fish live with about 2–4 mbar of CO₂ in their blood, against about 50 in
mammals, and nobody has measured how fish cells grow against CO₂. If they tolerate 50 mbar, not 100, the design costs $24.6/kg and
the US fillet share falls to 4.0% (recomputed 2026-11-21). No shrimp cell line exists at all.

**Animals.** A tonne of cultivated meat, sold where the model says it sells, spares about 66 land animals in the low-lactate example and 68 at the
reported cost (US), against about 250 for a tonne of the US meat mix as eaten. A tenth of those sales are chicken, and a
chicken is where the animals are. In Humbird's optimistic design it is about 87, and in the all-favourable example, with shoppers favouring
it, about 144. Seafood animals are not counted. Seafood is about three-tenths of sales in the low-lactate example and at the reported cost,
about a quarter in Humbird's optimistic design and about a seventh in the all-favourable example (US).

## 4. By region

Here the low-lactate example means cells that make 0.14 mol of ammonia a kilo (the published figure) and 0.42 mol of lactate per mol of glucose (the best published is 1.05), double every 36 hours and weigh 2 ng, grown in perfusion in a 20 m³ tank in a food-grade plant with medium at $0.20 a litre. The all-favourable example (`scenarios.all_favourable`) means every lever at its most favourable value among this model's own favourable end, Humbird's design and nine other published studies, within the model's limits: cells of 3 ng that make 0.054 mol of ammonia a kilo and 0.28 mol of lactate per mol of glucose, double every 16 hours and tolerate 5 mmol/L of ammonia and 50 of lactate, grown in perfusion in 42 m³ tanks in a food-grade plant with shared medium, with medium at the cost of its nutrients, no growth factors bought, no lost runs and dialyser-grade hollow fibres holding the cells back, and 58.6% of meat buyers picking it at the same price.

At the reported cost, with its cost and demand both drawn:

```
total cultivated share of meat and seafood (N=30,000), 80% CI [P10, P90]:
  region   income/cap   by VOLUME (impact)        by VALUE ($ market)
  Europe    $43k        P50  0.7%  [0.2,  3.0]    P50  1.5%  [ 0.4,  5.7]  <- easiest (priciest meat)
  US        $86k        P50  0.4%  [0.1,  1.7]    P50  0.8%  [ 0.2,  3.2]
  Global    $14k        P50  0.2%  [0.0,  0.8]    P50  0.4%  [ 0.1,  1.6]
  China     $13k        P50  0.2%  [0.0,  0.8]    P50  0.4%  [ 0.1,  2.0]
  Brazil    $10k        P50  0.1%  [0.0,  0.3]    P50  0.1%  [ 0.0,  0.5]
  India     $3k         P50  0.0%  [0.0,  0.1]    P50  0.1%  [ 0.0,  0.3]
  Nigeria   $1k         P50  0.0%  [0.0,  0.1]    P50  0.0%  [ 0.0,  0.1]  <- hardest (cheap meat + price-sensitive)
```

Dear meat makes Europe easiest; cheap meat and price-sensitive shoppers make low-income regions hardest. Incomes are GDP per
head in nominal dollars since 2026-11-20 (they were at purchasing-power parity), and the US share counts the 10.2% of the US
closed to cultivated meat by state law as taking none. To two decimals the world median is 0.19% (8 in 10 draws 0.05–0.81%). At the
reported cost itself the shares are 0.16% for the world, 0.7% for Europe and 0.4% for the US. The band draws the share at equal price, κ from 4 to 11, and plant
costs from the plant term of Humbird's optimistic design to a pharma-style plant at half the density. World beef and world
seafood are priced by who eats them (METHODS.md, "World beef price" and "World seafood prices").

| the two headline cases | world | US | Europe |
|---|---|---|---|
| Low-lactate example: at the most-likely-values cost | 0.05% | 0.13% | 0.22% |
| Low-lactate example: middle draw (8 in 10 between) | 0.05% (0.009–0.3%) | 0.14% (0.03–0.6%) | 0.23% (0.04–1.1%) |
| All-favourable example, shoppers favouring it: at the most-likely-values cost | 23.4% | 28.4% | 36.9% |
| All-favourable example, shoppers favouring it: middle draw (8 in 10 between) | 17.4% (10.7–26.3%) | 22.5% (15.4–30.9%) | 30.1% (22.6–38.9%) |
| All-favourable example, the low-lactate example's demand: at the most-likely-values cost | 5.6% | 6.7% | 11.0% |
| All-favourable example, the low-lactate example's demand: middle draw (8 in 10 between) | 3.9% (1.4–12.7%) | 5.1% (1.8–16.1%) | 8.4% (3.1–22.9%) |

Against sushi-grade salmon, a structured product at the reported cost is at or below parity in 37% of draws (median R 1.08). How
much of a cut can be cells, and what assembling it costs, are unmeasured.

## 5. Entry points, and timing

Here the low-lactate example means cells that make 0.14 mol of ammonia a kilo (the published figure) and 0.42 mol of lactate per mol of glucose (the best published is 1.05), double every 36 hours and weigh 2 ng, grown in perfusion in a 20 m³ tank in a food-grade plant with medium at $0.20 a litre. The all-favourable example (`scenarios.all_favourable`) means every lever at its most favourable value among this model's own favourable end, Humbird's design and nine other published studies, within the model's limits: cells of 3 ng that make 0.054 mol of ammonia a kilo and 0.28 mol of lactate per mol of glucose, double every 16 hours and tolerate 5 mmol/L of ammonia and 50 of lactate, grown in perfusion in 42 m³ tanks in a food-grade plant with shared medium, with medium at the cost of its nutrients, no growth factors bought, no lost runs and dialyser-grade hollow fibres holding the cells back, and 58.6% of meat buyers picking it at the same price.

At the reported cost, a few luxury products are already within reach on price when compared at their ordinary grade (farmed
salmon, crossbred wagyu): foie gras, bluefin tuna, sea urchin, wagyu. Lobster is close (R ≈ 1.1). Each is a small market.
Commodity pork and chicken, where the volume is, stay above parity even in the all-favourable example (1.8 to 2.9 times their price). Foie gras stands out: unstructured,
expensive, and increasingly banned on welfare grounds.

From a near-zero start, cultivated meat reaches 90% of its long-run share after 21 years at the reported cost
(15 to 45 across the plausible speeds at which wariness fades), 20 in the low-lactate example (15 to 40), 24 in Humbird's optimistic design (16 to 54) and 20 in the all-favourable
example (15 to 43), as a share of the meat sold, with 62% of first purchases turning into repeat buying and 14% of buyers
stopping each year (plant-based meat's figures, `adoption_timing.years_for_cost`; first purchase only it was 21, 19, 24 and 21). This
assumes that nothing stalls and that supply keeps up. The rollout speeds are the usual ones for durable goods, so the years are
assumed, not estimated; history puts the chance of a stall at roughly one in three (METHODS.md, "How fast"). Current wariness
(surveys: 5–60%) sets the speed, not the ceiling.

## 6. What to fund

Here the low-lactate example means cells that make 0.14 mol of ammonia a kilo (the published figure) and 0.42 mol of lactate per mol of glucose (the best published is 1.05), double every 36 hours and weigh 2 ng, grown in perfusion in a 20 m³ tank in a food-grade plant with medium at $0.20 a litre. The all-favourable example (`scenarios.all_favourable`) means every lever at its most favourable value among this model's own favourable end, Humbird's design and nine other published studies, within the model's limits: cells of 3 ng that make 0.054 mol of ammonia a kilo and 0.28 mol of lactate per mol of glucose, double every 16 hours and tolerate 5 mmol/L of ammonia and 50 of lactate, grown in perfusion in 42 m³ tanks in a food-grade plant with shared medium, with medium at the cost of its nutrients, no growth factors bought, no lost runs and dialyser-grade hollow fibres holding the cells back, and 58.6% of meat buyers picking it at the same price.

Costs here are at most likely values. The swings are from "What the answer rests on" and "What decides it" in the Summary.

1. **Cells that make less lactate and ammonia, and still grow fast.** This is the ladder's largest step: $234.5 a kilo in a 20 m³
   batch, from $304.8 to $70.3, almost all of it from lower lactate ($228.3); in perfusion, with the low-lactate example's other
   switches, it would be $106.4 ($155.0 to $48.7). Cells that make almost no ammonia or lactate are worth another $17.7 from the low-lactate example (the published evidence on each trait is in `research_notes/cell_trait_routes.md`). Low waste and fast growth
   have each been shown, never together in one culture. A culture that does both, with the glucose taken up and the lactate and
   ammonia made reported per kilo of real cells, is the single most useful measurement. The published cells' glucose is derived
   from their energy balance here, because nobody has reported it on the low-waste feed.
2. **A way to hold cells back in large tanks, and a filter that lasts.** Nobody has run animal cells in perfusion above about
   4 m³. It is worth $21.6 a kilo with the low-lactate example's traits (row 3 to row 4). Every scenario from the low-lactate example on prices a hollow-fibre filter loop whose membranes have never filtered a culture this thick for a month.
   Membranes are the low-lactate example's largest cost ($22.7 of $48.7), and the filter's life moves the low-lactate example between $36 and $87.
   The all-favourable example assumes dialyser-grade fibres do the job at $0.06 a kilo; nobody has run them on a dense culture for weeks. A weeks-long
   run at high density, and a price for a food-grade membrane, would settle most of it.
3. **The ammonia and lactate numbers:** how much ammonia and lactate meat cells tolerate at density ($44 to $89 in the low-lactate example across
   ammonia's range, $49 to $70 across lactate's) and how
   much ammonia the low-lactate example's cells make per kilo grown ($44 to $80; measured once, in flasks).
4. **The price of medium and of the bubble protectant at production scale:** verify the $0.20 a litre reports and what is in the
   medium, on a stated mass basis. Medium at $0.50 adds $11.9 to the low-lactate example. A tonne quote for poloxamer 188 would settle $47 to $54.
5. **Tank tricks that clear CO₂ without bubbles** (a column on a pumped loop, pressure, recycled oxygen) and **the gas flow cells
   tolerate:** calculated, never tried with meat cells. Without the tricks the low-lactate example costs $6.1 more. For the published
   cells in perfusion they are worth $23.5; in a batch, nothing. Since 2026-11-20 gas also kills: how many cells bursting bubbles kill
   in a dense, protected culture moves the low-lactate example between $46 and $59, and rests on one bench study.
6. **A cheaper class of plant for animal cells:** a food-grade plant with shared medium (no clean room, shared medium line, bought
   oxygen) is worth $4.2 a kilo in the low-lactate example, and nobody has built one. A plant as cheap as a yeast plant is not counted: nothing
   shows animal cells can be grown that way.
7. **Contamination is not the main obstacle to a cheaper plant, on this model:** the food-grade plant with shared medium stays
   cheaper than the food-grade plant at the low-lactate example's 1% a day until it loses a run per tank about every 55 days
   (1.8% a day; 2026-11-21, with the low-lactate example's design held). Measured loss rates in food-grade
   tanks would test this.
8. **How much of a cut can be cells, and whether shoppers accept a blend:** cuts sold today are 10–30% cells. Whether a steak or
   fillet can be mostly suspension-grown cells, with the texture of meat, sets most of what a cut costs and how shoppers see it.
   Across the cell share's range the low-lactate example's share runs from 0.03% to 0.13%. The cost of assembling a cut is unmeasured too ($0.5–7
   a kilo beyond mince).
9. **How shoppers respond once they can buy it:** the share at equal price is a judgement (14.4% of meat buyers; 13% of all
   choices, drawn between 3% and 52%). The
   spread of liking is fitted to one choice experiment, sixteen premium meats and farmed salmon, and it decides both ends of the answer: its
   tail gives the low-lactate example its sales and its middle sets the all-favourable example. Repeat-purchase data from the first markets, at known prices,
   would replace both.
10. **Open, comparable data:** cost claims per kg of dry matter or protein, with capital included (METHODS.md, "A
   checklist for cost claims"). Most published analyses leave out all or part of the cost of capital.

A meat tax also works: raising conventional prices 25% lowers R as much as a 20% cut in every cost. Most of these
are public goods that industry underfunds.

**The one working plant.** Vow grows animal cells in a food-grade 20,000-litre tank with no clean room,
drained and refilled, at an output that implies about 27 g of cells per litre. Reconstructed in the model, that
operation costs about $48/kg in a yeast-style plant and $100/kg in a food-grade plant at Humbird's cost (`industry_claims.py`),
so the cheap class of plant is probably what it runs. It shows that food-grade tanks work for short runs. It does not show
the density or the weeks-long perfusion runs the scenarios assume (METHODS.md, "A working plant as a reference
point").

**How the physics fares against reported runs.** Fed the cells and vessels of published runs, the model is
conservative about how dense a culture a vessel can hold (a small vessel has held twice its limit), and optimistic
about medium (real perfusion runs used 1.2 to 2.8 times more) and about output in practice (the one working
20 m³ plant makes under half of what the model's efficient cells would). It also flags two reports whose own
numbers do not add up (METHODS.md, "Back-test against reported runs").

## 7. What would change the conclusions

Here the low-lactate example means cells that make 0.14 mol of ammonia a kilo (the published figure) and 0.42 mol of lactate per mol of glucose (the best published is 1.05), double every 36 hours and weigh 2 ng, grown in perfusion in a 20 m³ tank in a food-grade plant with medium at $0.20 a litre. The all-favourable example (`scenarios.all_favourable`) means every lever at its most favourable value among this model's own favourable end, Humbird's design and nine other published studies, within the model's limits: cells of 3 ng that make 0.054 mol of ammonia a kilo and 0.28 mol of lactate per mol of glucose, double every 16 hours and tolerate 5 mmol/L of ammonia and 50 of lactate, grown in perfusion in 42 m³ tanks in a food-grade plant with shared medium, with medium at the cost of its nutrients, no growth factors bought, no lost runs and dialyser-grade hollow fibres holding the cells back, and 58.6% of meat buyers picking it at the same price.

- **Up:** a meat-cell line shown to make little lactate and ammonia while doubling in 36 hours or less, with a full mass balance;
  perfusion at 20 m³ with a filter that lasts a month in a dense culture, or a cheaper way to hold cells back; medium at
  $0.20 a litre or less confirmed at scale with its growth factors; animal cells grown in a plant built like a microbial
  fermentation plant; shoppers who come to favour cultivated meat, which is worth more than any cost in the all-favourable example.
- **Down:** a filter life near the evidence note's median (1,500 L/m²) with membranes still at pharma prices (the low-lactate example $62.5);
  cells that tolerate 2 mmol/L of ammonia, not 4 (the low-lactate example $89.1), or 20 mmol/L of lactate, not 35 ($70.3); bubbles that kill
  three times the bench figure ($58.9); perfusion failing at 20 m³ (the low-lactate example $70–100); cuts that cannot
  be mostly cells; frequent contamination with slow restarts (METHODS.md, "Losing runs"); the reported figures not surviving
  review or scale-up.
- **Demand is the weakest part, at both ends.** The share at equal price is a judgement with no sales data behind it. The spread
  of liking was refitted on 2026-11-19 as a Student's t, to one choice experiment, sixteen premium products and farmed salmon
  together, so those are no longer independent checks. Its tail, above about four times the price of meat, is an extrapolation
  that carries two-fifths of the low-lactate example's sales. Its middle, which no data pin, sets the share at one to four times the
  price of meat. The model still responds to a falling price more than twice as strongly as farmed salmon did (3.7–4.2
  against 1–1.5). The low-lactate example's share is 0.05% at most likely values and at the middle draw; the cross-check anchored on premium
  meats gives 0.01% (0.00% to 0.03%). For the all-favourable example the demand judgement is most of the answer: 23.4% with 58.6% of
  meat buyers at equal price, 5.6% with 14.4%.
- **What rests on one source.** The reported cost is one company's report, with a capital charge that assumes a
  10-year depreciation period (20 years would add $8/kg). The scenarios' plant costs are one engineer's design
  (Humbird 2021) in 2025 prices. The ammonia the low-waste cells make is one paper's flask measurement (Hubalek 2023). None has
  been reproduced.
- **The cells' glucose is derived, not measured.** The published cells' $316 in a batch ($181 in perfusion) follows from a lactate yield measured in chicken
  cells and a glucose need computed from the model's own oxygen use. A cell on the low-waste feed may ferment less than that. A
  measured glucose and lactate balance for such a cell would move rows 1 and 2 by tens of dollars; the low-lactate example would not move unless
  its cells made more than about 0.48 mol of lactate per mol of glucose, a little above its 0.42.

Figures: `python report_figures.py` (cost vs inputs, cost waterfall, share tornado, share vs price, timing paths,
penetration by type and region). Parameters and sources: `python inputs.py`.
