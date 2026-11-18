# Does cultivated meat get cheaper as it sells more? Cost and share solved together

Date: 2026-11-18. Code: `market_size_loop.py`; test: `tests/test_market_size_loop.py`. Nothing here changes a default.

Access levels: **FT** full text read; **ABS** abstract only; **SNIP** search snippet; **MEM** background knowledge, unchecked.

**The idea** (Pablo): the model runs one way, from a cost to a share. But the cell filter's membrane and the plant are priced as today's
small biopharma supply industry prices them, and even a fraction of a percent of world meat would need several times all the
animal-cell tank volume that exists. So the cost should fall as the market grows. And the loop should start in premium products: where
cultivated meat first undercuts the premium product it competes with (Wildtype's salmon against sushi-grade salmon), the demand that
unlocks is the volume that makes everything cheaper.

## 1. What learns, and how

- **The membrane: a switch, then learning.** The model's $1,450 a m² is a pharma price, not a cost. Similar hollow fibre sells for about
  $7–10 a m² as sterile dialysers (about 0.6 billion m² a year) and $20–50 for water treatment. Pharma consumables have not got cheaper
  with volume (single-use prices rose about 20% over 2020–22, SNIP). So the price stays at $1,450 until yearly demand is large enough for
  a food-grade supplier, taken as 1 million m² a year (range 0.3–3). That supplier starts at $250 a m² (150–400), and the price then falls
  18% (10–28%) for each doubling of yearly area, to a floor of $60 (30–150) for a module that takes steam and a quarter cells by volume.
- **The plant and the filter loop's hardware: slow learning.** 10% (3–18%) for each doubling of the animal-cell tank volume installed over
  today's 8,000 m³ (6,500–11,800), at a fixed tank size, down to a microbial plant with everything animal cells must have (the floor the
  scenarios' bands use: 0.29 of Central's plant, 0.52 of the best case's).
- **Nothing else learns here**: feed, growth factors and the protectant are bought in bulk markets or are scenario switches already.
- World meat is taken as 270 Mt a year of boneless weight (384 Mt of carcass weight, FAO 2025, SNIP).

## 2. Cost against volume

**1. Today** (no learning: $62.96)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.0037% | 2,533 | 1,450 | 0.96× | $61.50 | 0.00% |
| 0.1 | 0.037% | 25,335 | 1,450 | 0.80× | $56.00 | 0.01% |
| 0.5 | 0.185% | 126,674 | 1,450 | 0.65× | $50.51 | 0.02% |
| 2 | 0.741% | 506,698 | 178 | 0.53× | $44.16 | 0.03% |
| 10 | 3.7% | 2,533,490 | 112 | 0.42× | $39.97 | 0.05% |
| 35 | 13% | 8,867,215 | 79 | 0.34× | $37.34 | 0.07% |

**3. Plus cells selected to grow faster on the low-waste feed (Central)** (no learning: $29.42)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.0037% | 485 | 1,450 | 0.99× | $29.35 | 0.16% |
| 0.1 | 0.037% | 4,854 | 1,450 | 0.93× | $28.90 | 0.16% |
| 0.5 | 0.185% | 24,271 | 185 | 0.81× | $20.73 | 0.41% |
| 2 | 0.741% | 97,086 | 124 | 0.68× | $19.40 | 0.48% |
| 10 | 3.7% | 485,428 | 78 | 0.53× | $18.09 | 0.57% |
| 35 | 13% | 1,698,999 | 60 | 0.44× | $17.30 | 0.64% |

**5. Plus engineered cells** (no learning: $9.66)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.0037% | 227 | 1,450 | 1.00× | $9.65 | 3.70% |
| 0.1 | 0.037% | 2,267 | 1,450 | 0.96× | $9.58 | 3.78% |
| 0.5 | 0.185% | 11,334 | 1,450 | 0.87× | $9.41 | 3.99% |
| 2 | 0.741% | 45,335 | 172 | 0.75× | $6.80 | 9.21% |
| 10 | 3.7% | 226,676 | 109 | 0.60× | $6.38 | 10.51% |
| 35 | 13% | 793,367 | 76 | 0.52× | $6.16 | 11.28% |

"Share that cost would buy" is the main model's long-run share at that cost. Where it exceeds the share the volume is, the market grows;
where it is less, it shrinks. With both items at their floors the cells cost $35.25 (today's cells), $16.15 (Central) and
$6.13 (the best case).

## 3. Where cost and share agree

| scenario | learning | the main model: cells, share | resting point from below: cells, share, Mt a year | from above: cells, share, Mt a year |
|---|---|---|---|---|
| 1. Today | central | $62.96, 0.00% | $61.14, 0.00%, 0.01 | $61.14, 0.00%, 0.01 |
| 1. Today | no food-grade membrane supplier, slow plant learning | $62.96, 0.00% | $62.49, 0.00%, 0.01 | $62.49, 0.00%, 0.01 |
| 1. Today | slow learning | $62.96, 0.00% | $62.49, 0.00%, 0.01 | $62.49, 0.00%, 0.01 |
| 1. Today | fast learning | $62.96, 0.00% | $58.89, 0.01%, 0.02 | $58.89, 0.01%, 0.02 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | central | $29.42, 0.16% | $19.86, 0.45%, 1.22 | $19.86, 0.45%, 1.22 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no food-grade membrane supplier, slow plant learning | $29.42, 0.16% | $29.01, 0.16%, 0.44 | $29.01, 0.16%, 0.44 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | slow learning | $29.42, 0.16% | $29.01, 0.16%, 0.44 | $22.63, 0.33%, 0.88 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | fast learning | $29.42, 0.16% | $17.57, 0.62%, 1.67 | $17.57, 0.62%, 1.67 |
| 5. Plus engineered cells | central | $9.66, 3.69% | $6.16, 11.26%, 30.39 | $6.16, 11.26%, 30.39 |
| 5. Plus engineered cells | no food-grade membrane supplier, slow plant learning | $9.66, 3.69% | $9.37, 4.03%, 10.89 | $9.37, 4.03%, 10.89 |
| 5. Plus engineered cells | slow learning | $9.66, 3.69% | $7.15, 8.25%, 22.28 | $7.15, 8.25%, 22.28 |
| 5. Plus engineered cells | fast learning | $9.66, 3.69% | $6.07, 11.57%, 31.25 | $6.07, 11.57%, 31.25 |

"From below" starts with no learning; "from above" starts with everything at its floor. Where the two differ there are two resting
points, and reaching the upper one needs someone to carry the industry across the gap.

- **Central: cells fall from $29.42 to $19.86 and the share rises from 0.16% to 0.45%.** Almost all of the fall
  is the membrane. It still rests well under 1% of world meat.
- **The best case reaches parity by this route: $6.16 against the $6.14 parity needs, and 11.26% of world meat**
  (3.69% without learning). This is the only route found so far to parity that does not need better cells than the best
  case already assumes.
- **Today's cells are stuck.** At $63 they sell about 0.01 Mt a year, fifty times too little membrane demand for the switch, in every case.
- **Without a food-grade membrane supplier little changes**: Central $29.01, the best case $9.37. The plant's learning alone
  is worth under a dollar.

## 4. The loop starts in premium products

| scenario | stage | cells, $/kg | sold, Mt a year: premium products, cuts, mince and processed | premium products' part of sales | chicken (organic): price against it, share of it | pork (heritage): price against it, share of it | beef (prime/wagyu): price against it, share of it | seafood (sushi): price against it, share of it |
|---|---|---|---|---|---|---|---|---|
| 1. Today | no learning | $62.96 | 0.01, 0.00, 0.00 | 100% | 7.63×, 0.0% | 6.20×, 0.0% | 2.21×, 0.3% | 2.84×, 0.1% |
| 1. Today | resting point | $61.14 | 0.01, 0.00, 0.00 | 100% | 7.44×, 0.0% | 6.05×, 0.0% | 2.15×, 0.4% | 2.76×, 0.1% |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no learning | $29.42 | 0.41, 0.00, 0.00 | 99% | 4.05×, 0.3% | 3.29×, 0.5% | 1.17×, 10.7% | 1.50×, 5.0% |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | resting point | $19.86 | 1.08, 0.14, 0.01 | 88% | 3.03×, 1.1% | 2.46×, 2.0% | 0.88×, 24.9% | 1.13×, 13.3% |
| 5. Plus engineered cells | no learning | $9.66 | 2.56, 4.55, 2.85 | 26% | 1.94×, 5.4% | 1.58×, 7.9% | 0.56×, 49.5% | 0.72×, 32.5% |
| 5. Plus engineered cells | resting point | $6.16 | 3.27, 12.62, 14.50 | 11% | 1.57×, 8.9% | 1.27×, 12.4% | 0.45×, 58.6% | 0.58×, 41.6% |

| scenario | learning | premium products sold at the scenario's own cost, Mt a year | membrane that needs, million m² a year | the switch, million m² a year | do premium products alone cross it? |
|---|---|---|---|---|---|
| 1. Today | central | 0.01 | 0.02 | 1.0 | no |
| 1. Today | no food-grade membrane supplier, slow plant learning | 0.01 | 0.02 | never | no |
| 1. Today | slow learning | 0.01 | 0.02 | 3.0 | no |
| 1. Today | fast learning | 0.01 | 0.02 | 0.3 | no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | central | 0.41 | 2.38 | 1.0 | yes |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no food-grade membrane supplier, slow plant learning | 0.41 | 2.38 | never | no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | slow learning | 0.41 | 2.38 | 3.0 | no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | fast learning | 0.41 | 2.38 | 0.3 | yes |
| 5. Plus engineered cells | central | 2.56 | 4.71 | 1.0 | yes |
| 5. Plus engineered cells | no food-grade membrane supplier, slow plant learning | 2.56 | 4.71 | never | no |
| 5. Plus engineered cells | slow learning | 2.56 | 4.71 | 3.0 | yes |
| 5. Plus engineered cells | fast learning | 2.56 | 4.71 | 0.3 | yes |

- **At Central's cost, 99% of cultivated meat's sales are premium products**: sushi-grade seafood at 1.50 times its price and prime
  or wagyu beef at 1.17 times. These 0.41 Mt a year are the whole early industry.
- **That volume alone crosses the membrane switch** in the central case (it needs 2.4 million m² a year against a switch at 1.0). The
  cheaper membrane takes cells to about $20, which puts cultivated meat **below the price of prime beef (0.88 times) and near
  sushi-grade seafood's (1.13 times)**. Their shares more than double (prime beef 10.7% to 24.9%, sushi-grade seafood 5.0% to 13.3%), and
  premium products sold rise from 0.41 to 1.08 Mt a year. This is the unlocking Pablo describes.
- **With slow learning it does not cross (switch at 3.0 million m² a year), and Central has two resting points**: 0.16% at $29.01 if
  nobody moves first, 0.33% at $22.63 once the food-grade supplier exists. The gap is a coordination problem: a membrane maker will not
  build for a market that is not there, and the market is not there at pharma prices.
- **Premium products are not enough to reach mass meat.** At Central's resting point 88% of sales are still premium; cuts and mince stay at
  2–3 times their conventional price. Only the best case's cells carry the loop into ordinary cuts and mince.

## 5. How strong is the loop, and how well is that known?

| scenario | its own cost and share | first pass: the learning its own volume brings | resting point | part of the share gain from later rounds | resting point with demand anchored on premium meats (its own share there) |
|---|---|---|---|---|---|
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | $29.42, 0.16% | $20.90, 0.40% | $19.86, 0.45% | 18% | $19.81, 0.48% (0.16%) |
| 5. Plus engineered cells | $9.66, 3.69% | $6.38, 10.51% | $6.16, 11.26% | 10% | $6.44, 2.91% (1.83%) |

| input, across its range | 3. Plus cells selected to grow faster on the low-waste feed (Central): cells, share | 5. Plus engineered cells: cells, share |
|---|---|---|
| Membrane demand at which a food-grade supplier appears (300000 to 3e+06 m2 a year) | $19.59 to $28.02, 0.47% to 0.18% | $6.13 to $6.22, 11.38% to 11.07% |
| That supplier's first price (150 to 400 $/m2) | $19.49 to $20.43, 0.47% to 0.42% | $6.13 to $6.25, 11.38% to 10.95% |
| Membrane's price fall per doubling (0.1 to 0.28 per doubling) | $20.14 to $19.57, 0.44% to 0.47% | $6.27 to $6.13, 10.89% to 11.38% |
| Membrane's price floor (30 to 150 $/m2) | $19.86 to $19.90, 0.45% to 0.45% | $6.16 to $6.29, 11.26% to 10.81% |
| Plant's cost fall per doubling (0.03 to 0.18 per doubling) | $21.33 to $18.27, 0.38% to 0.56% | $6.80 to $6.16, 9.22% to 11.26% |
| Animal-cell tanks installed today (6500 to 11800 m3) | $19.69 to $20.17, 0.46% to 0.44% | $6.16 to $6.21, 11.26% to 11.09% |
| World meat, boneless (250 to 384 Mt a year) | $19.94 to $19.48, 0.45% to 0.48% | $6.17 to $6.15, 11.24% to 11.31% |

- **It is mostly one step, not a loop.** 82% of Central's gain in share, and 90% of the best case's, comes on the first
  pass: the volume each scenario already sells is enough for the membrane switch. Later rounds, where cheaper cells sell more and more
  sales make cells cheaper again, add only 18% and 10%. So the result does not rest on the strength of a feedback, which could
  not be measured; it rests on whether one event happens (a food-grade membrane supplier) and at what price.
- **The learning rates matter little; the switch matters a lot.** Across their ranges the membrane's rate, floor and first price each
  move Central's cells by under a dollar. The plant's rate moves them by $3. The switch's threshold alone takes Central from $19.59 to
  $28.02: at 3 million m² a year Central's own volume does not reach it.
- **The cost side is sturdier than the share side.** With the share taken from the curve fitted to premium real meats
  (`premium_curve.md`) in place of the main model's, the cells cost about the same (the best case $6.44) but the best case's share
  is 2.91%, not 11.26%. How much a price at or below parity sells is the model's least-tested part, with or without learning.
- **What is not known at all:** whether a food-grade module works at a quarter cells by volume; the size of the premium markets; how
  fast any of this happens.
- **What would check it:** a supplier's quote for 100,000 m² or more of steam-cleanable hollow-fibre module; trade figures for
  sushi-grade seafood and prime beef; and the record of farmed salmon, a premium product whose price fell and whose sales multiplied,
  as a test of how much a price cut unlocks (not yet done).

## 6. Evidence

| finding | source | access |
|---|---|---|
| Membrane-bioreactor membrane cost per m² in 2025 at 0.3 of its 2005 level (18–26% a doubling if area doubled 4–6 times) | Abbott, WIOA conference 2025 | FT; the doublings are MEM |
| Seawater reverse-osmosis plants: 15% a doubling, 4,237 plants, 1977–2015; 12% with scale removed, and slower in the last ten years | Caldera & Breyer 2017; Mayor 2020 | ABS |
| Dialysers: about 171 million sold by one maker in 2025, at roughly $13–17 each and 1.5–2.2 m² | Fresenius investor pages; market listings; Membranes 2021 | SNIP; FT for the area |
| Corn ethanol: processing cost 13% a doubling; capital charges −83% at constant plant size over 7 doublings (about 20% a doubling, overstated by falling interest rates) | Hettinga et al. 2009 | FT |
| Power plants: nuclear negative to 6%, coal 8%, gas turbines 15%, hydro 1.4%, solar 23% | Rubin et al. 2015, Table 1 | FT |
| Electrolysers: 18–47% globally but 0.6–9% within countries | Cambridge EPRG WP 2024 | SNIP |
| Mammalian cell-culture capacity "nearly 6,500 kL" (2023); 10.9–11.8 million L on another basis | BDO/BPTC via BioProcess International 2023; BioPlan | FT; SNIP |

**Not found:** the yearly area of bioprocess perfusion filters (guessed at 0.1–0.3 million m²), a price for a food-grade steam-cleanable
hollow-fibre module, and any price history for dialysers.

## 7. What this rests on, and what could be wrong

- **The switch is a judgement** (about 65% that a food-grade supplier appears once demand passes 1 million m² a year). It is the whole
  result: without it nothing much moves (section 3).
- **The dialyser-price membrane may not exist for this job.** The filter must hold a quarter cells by volume for weeks and take steam or
  caustic. `retention_alternatives.md` puts 15% on dialyser-grade fibre doing it. The $60 floor is far above dialyser prices for that
  reason, but it is still a guess.
- **The size of the premium markets is assumed, not sourced**: sushi-grade seafood is 2% of world meat by weight in the model's market
  table (5.4 Mt a year) and prime or wagyu beef 0.5% (1.35 Mt). If they are half that, premium products need 1.2 million m² a year at
  Central's cost and only just cross the switch. The switch's range (0.3–3) stands in for this.
- **Resting points, not a path.** Nothing says how long it takes, and learning is counted on yearly scale, not cumulative output.
- **Not combined with the premium-buyer study** (`premium_buyers.md`), which would add to Central's early volume.
- **Judgement:** that a food-grade membrane at $250 a m² or less exists if cultivated meat sells 0.5 Mt a year: about 0.6. That
  learning of this kind takes the best case's cells to $7 or less, given the best case's cells exist: about 0.55. That it takes Central
  above 1% of world meat: about 0.1.

## Sources

1. Abbott, "Membrane bioreactors: 20 years on", WIOA conference 2025 (FT).
2. Caldera & Breyer 2017, Water Resources Research (ABS); Mayor 2020, Water Resources Research (ABS).
3. Hettinga et al. 2009, Energy Policy 37 (FT).
4. Rubin, Azevedo, Jaramillo & Yeh 2015, Energy Policy 86 (FT).
5. BDO/BPTC capacity survey, via BioProcess International, October 2023 (FT).
6. Humbird 2021, Biotechnology and Bioengineering (FT): $16,000 per ATF membrane, the model's $1,450 a m².
7. FAO Food Outlook, November 2025 (SNIP).
