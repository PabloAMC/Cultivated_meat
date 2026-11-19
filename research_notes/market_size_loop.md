# Does cultivated meat get cheaper as it sells more? Cost and share solved together

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50; cut cost rebuilt (0.8 cells + $2 matrix + $2 assembly beyond mince), cuts cheaper.

> Repinned 2026-11-19 (audit batch): cells dearer (ammonia tolerance 4 mM), seafood re-priced by consumption, the tier rule replaced by a blend penalty, the equal-price share drawn around its 13% setting; see audit_2026-11-19.md.

Date: 2026-11-18; revised twice the same day: after the checks in section 6 (the premium markets were sized from data) and after the
shopper model gained a spread of liking across shoppers (`liking_spread.md`). Code: `market_size_loop.py`; test: `tests/test_market_size_loop.py`.
The study itself changes no default.

Access levels: **FT** full text read; **ABS** abstract only; **SNIP** search snippet; **MEM** background knowledge, unchecked.

**The idea** (Pablo): the model runs one way, from a cost to a share. But the cell filter's membrane and the plant are priced as today's
small biopharma supply industry prices them, and even a fraction of a percent of world meat would need several times all the
animal-cell tank volume that exists. So the cost should fall as the market grows. And the loop should start in premium products: where
cultivated meat first undercuts the premium product it competes with (Wildtype's salmon against sushi-grade salmon), the demand that
unlocks is the volume that makes everything cheaper.

**In short (2026-11-19, after the audit batch).** At their point costs Central and the best case's cells both sell enough to
bring a food-grade membrane supplier into being, and both get much cheaper for it. Central's cells fall from $32.80 to $17.75 and
its share rises from 0.08% to 0.98% of world meat. The best case's cells come close to price parity but do not reach it ($6.66
against $6.14). Three things are weaker than before the batch:

- **Central's margin over the switch is thin.** Its sales need 2.3 times the switch's membrane area, where they needed ten times.
  With slow learning it no longer crosses on its own: it stays at $32.48 and 0.08% unless someone else brings the supplier.
- **About a third of Central's gain is now a loop**, not one step, and the loop's strength is not measured.
- **The model's response to price, which drives the gain, is several times stronger than history shows** (section 6).

Premium products are about half of Central's first sales and beef steaks the other half. Published cells sell almost nothing and
never start. Here "the best case" is its cells with the model's ordinary demand (13% at equal price), not its own 55%. (Before the
audit batch: Central $15.05 and 2.49%, with one resting point even under slow learning; the best case $6.41 and 8.30%. Before
the cut cost was rebuilt the same day: Central $15.83 and 0.86%, the best case $6.49.)

## 1. What learns, and how

- **The membrane: a switch, then learning.** The model's $1,450 a m² is a pharma price, not a cost. Process hollow-fibre modules sell at
  $800–1,200 a m² (Repligen KrosFlo, SNIP), with no sign of volume discounts; water-treatment modules of the same polymer sell at
  about $66 a m² (inge dizzer, SNIP), sanitary dairy spirals at $27–62, and sterile dialysers at under $10. So the price stays at $1,450
  until yearly demand is large enough for a food-grade supplier, taken as 1 million m² a year (range 0.3–3). Today's whole market for
  bioprocess perfusion filters is about 30,000 m² a year (8,000–100,000; a Fermi estimate from Repligen's filtration revenue), so the
  switch is 10–100 times today's market. That supplier starts at $150 a m² (60–400), and the price then falls 18% (10–28%) for each
  doubling of yearly area, to a floor of $50 (20–120) for a wide-bore module that takes steam and a quarter cells by volume.
- **The plant and the filter loop's hardware: slow learning.** 10% (3–18%) for each doubling of the animal-cell tank volume installed over
  today's 8,000 m³ (6,500–11,800), at a fixed tank size, down to a microbial plant with everything animal cells must have (the floor the
  scenarios' bands use: 0.29 of Central's plant, 0.52 of the best case's).
- **Nothing else learns here**: feed, growth factors and the protectant are bought in bulk markets or are scenario switches already.
- World meat and seafood are taken as 336 Mt a year of edible weight (range 300–384): about 250 Mt of boneless meat (380 Mt of
  carcass weight) and about 87 Mt of edible seafood (FAO, SNIP).

## 2. Cost against volume

**1. Published cells** (no learning: $111.89)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.00298% | 2,533 | 1,450 | 0.96× | $110.41 | under 0.01% |
| 0.1 | 0.0298% | 25,335 | 120 | 0.80× | $75.65 | under 0.01% |
| 0.5 | 0.149% | 126,674 | 76 | 0.65× | $69.09 | under 0.01% |
| 2 | 0.595% | 506,698 | 51 | 0.53× | $64.19 | under 0.01% |
| 10 | 2.98% | 2,533,490 | 50 | 0.42× | $60.01 | under 0.01% |
| 35 | 10.4% | 8,867,215 | 50 | 0.34× | $57.39 | under 0.01% |

**3. Plus cells selected to grow faster on the low-waste feed (Central)** (no learning: $32.80)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.00298% | 485 | 1,450 | 0.99× | $32.74 | 0.08% |
| 0.1 | 0.0298% | 4,854 | 1,450 | 0.93× | $32.28 | 0.09% |
| 0.5 | 0.149% | 24,271 | 98 | 0.81× | $19.45 | 0.73% |
| 2 | 0.595% | 97,086 | 66 | 0.68× | $18.17 | 0.91% |
| 10 | 2.98% | 485,428 | 50 | 0.53× | $16.98 | 1.12% |
| 35 | 10.4% | 1,698,999 | 50 | 0.44× | $16.29 | 1.26% |

**5. Plus engineered cells** (no learning: $11.46)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.00298% | 227 | 1,450 | 1.00× | $11.45 | 2.82% |
| 0.1 | 0.0298% | 2,267 | 1,450 | 0.96× | $11.38 | 2.85% |
| 0.5 | 0.149% | 11,334 | 137 | 0.87× | $7.59 | 5.46% |
| 2 | 0.595% | 45,335 | 92 | 0.75× | $7.22 | 5.83% |
| 10 | 2.98% | 226,676 | 58 | 0.60× | $6.82 | 6.26% |
| 35 | 10.4% | 793,367 | 50 | 0.52× | $6.63 | 6.48% |

"Share that cost would buy" is the main model's long-run share at that cost. Where it exceeds the share the volume is, the market grows;
where it is less, it shrinks. With both items at their floors the cells cost $55.30 (published cells), $15.13 (Central) and
$6.63 (the best case).

## 3. Where cost and share agree

| scenario | learning | the main model: cells, share | resting point from below: cells, share, Mt a year | from above: cells, share, Mt a year |
|---|---|---|---|---|
| 1. Published cells | central | $111.89, under 0.01% | $111.89, under 0.01%, 0.00 | $111.89, under 0.01%, 0.00 |
| 1. Published cells | no food-grade membrane supplier, slow plant learning | $111.89, under 0.01% | $111.89, under 0.01%, 0.00 | $111.89, under 0.01%, 0.00 |
| 1. Published cells | slow learning | $111.89, under 0.01% | $111.89, under 0.01%, 0.00 | $111.89, under 0.01%, 0.00 |
| 1. Published cells | fast learning | $111.89, under 0.01% | $111.89, under 0.01%, 0.00 | $111.89, under 0.01%, 0.00 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | central | $32.80, 0.08% | $17.75, 0.98%, 3.28 | $17.75, 0.98%, 3.28 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no food-grade membrane supplier, slow plant learning | $32.80, 0.08% | $32.48, 0.08%, 0.28 | $32.48, 0.08%, 0.28 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | slow learning | $32.80, 0.08% | $32.48, 0.08%, 0.28 | $22.07, 0.47%, 1.58 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | fast learning | $32.80, 0.08% | $15.54, 1.42%, 4.78 | $15.54, 1.42%, 4.78 |
| 5. Plus engineered cells | central | $11.46, 2.81% | $6.66, 6.43%, 21.62 | $6.66, 6.43%, 21.62 |
| 5. Plus engineered cells | no food-grade membrane supplier, slow plant learning | $11.46, 2.81% | $11.18, 2.95%, 9.92 | $11.18, 2.95%, 9.92 |
| 5. Plus engineered cells | slow learning | $11.46, 2.81% | $7.87, 5.20%, 17.47 | $7.87, 5.20%, 17.47 |
| 5. Plus engineered cells | fast learning | $11.46, 2.81% | $6.54, 6.57%, 22.09 | $6.54, 6.57%, 22.09 |

"From below" starts with no learning; "from above" starts with everything at its floor. Where the two differ there are two resting
points, and reaching the upper one needs someone to carry the industry across the gap.

- **The best case's cells come close to parity by this route but do not reach it: $6.66 against the $6.14 parity needs, and 6.43% of
  world meat** (2.81% without learning). They rest 3 cents above the cost with both items at their floors ($6.63), and no single
  input across its range takes them lower (section 5); fast learning, all its inputs at once, gives $6.54. With the best case's
  own demand (55% at equal price, 19.9% without learning) they rest at the floors, $6.63, and take 35.6% of world meat. (Before
  the audit batch, with the model's ordinary demand: $6.41 and 8.30%. Before the medium was repriced on 2026-11-19 they reached
  $6.17, which counted as parity.)
- **Central: cells fall from $32.80 to $17.75 and the share rises from 0.08% to 0.98%**, twelve-fold. Its 0.26 Mt a year needs
  2.33 million m² of membrane, 2.3 times the switch at 1.0, so in the central case it crosses on its own sales and has one resting
  point. It crosses on its own as long as the switch is below about 2.9 million m² (the switch's range is 0.3–3).
- **With slow learning Central has two resting points again.** A switch at 3 million m² is above what its sales need. Left alone
  it stays at $32.48 and 0.08%; once someone else has brought the food-grade supplier it rests at $22.07 and 0.47%. This reverses
  the finding of the cut-cost repin earlier on 2026-11-19, when Central sold 1.78 Mt a year, needed 10.2 million m², and had one
  resting point at $18.69 and 1.48% even with slow learning. It returns to what the note said before that repin.
- **Published cells never start.** At $112 a kilo they sell under 0.01% of world meat in every case, fast learning included, so
  no learning begins. Even with both items at their floors they would cost $55.30. (Before the audit batch they cost $57 and
  fast learning got them a food-grade membrane.)
- **Without a food-grade membrane supplier little changes**: Central $32.48 and 0.08%, the best case $11.18 and 2.95%. The plant's
  learning alone is worth about 30 cents a kilo.

## 4. The loop starts on premium products and beef steaks

| scenario | stage | cells, $/kg | sold, Mt a year: premium products, cuts, mince and processed | premium products' part of sales (without premium fillets and shrimp) | chicken (organic): price against it, share of it | pork (heritage): price against it, share of it | beef (prime/wagyu): price against it, share of it | seafood (premium fillet, shrimp): price against it, share of it | seafood (sushi): price against it, share of it |
|---|---|---|---|---|---|---|---|---|---|
| 1. Published cells | no learning | $111.89 | 0.00, 0.00, 0.00 | almost nothing is sold | 10.09×, under 0.01% | 8.20×, under 0.01% | 2.91×, under 0.01% | 6.56×, under 0.01% | 3.75×, under 0.01% |
| 1. Published cells | resting point | $111.89 | 0.00, 0.00, 0.00 | almost nothing is sold | 10.09×, under 0.01% | 8.20×, under 0.01% | 2.91×, under 0.01% | 6.56×, under 0.01% | 3.75×, under 0.01% |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no learning | $32.80 | 0.12, 0.14, 0.00 | 47% (30%) | 3.33×, 0.04% | 2.70×, 0.12% | 0.96×, 7.57% | 2.16×, 0.33% | 1.24×, 2.78% |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | resting point | $17.75 | 0.92, 2.10, 0.26 | 28% (11%) | 2.04×, 1.35% | 1.66×, 2.37% | 0.59×, 26.47% | 1.33×, 4.28% | 0.76×, 14.28% |
| 5. Plus engineered cells | no learning | $11.46 | 1.89, 5.90, 1.67 | 20% (6%) | 1.50×, 3.99% | 1.22×, 6.61% | 0.43×, 37.07% | 0.98×, 9.89% | 0.56×, 25.04% |
| 5. Plus engineered cells | resting point | $6.66 | 2.89, 12.42, 6.30 | 13% (4%) | 1.09×, 8.85% | 0.89×, 11.74% | 0.32×, 47.61% | 0.71×, 15.92% | 0.41×, 33.57% |

| scenario | learning | sold at the scenario's own cost, Mt a year: premium products, premium products without premium fillets and shrimp, everything | membrane each needs, million m² a year | the switch, million m² a year | which of the three cross it alone? |
|---|---|---|---|---|---|
| 1. Published cells | central | 0.00, 0.00, 0.00 | 0.00, 0.00, 0.00 | 1.0 | no, no, no |
| 1. Published cells | no food-grade membrane supplier, slow plant learning | 0.00, 0.00, 0.00 | 0.00, 0.00, 0.00 | never | no, no, no |
| 1. Published cells | slow learning | 0.00, 0.00, 0.00 | 0.00, 0.00, 0.00 | 3.0 | no, no, no |
| 1. Published cells | fast learning | 0.00, 0.00, 0.00 | 0.00, 0.00, 0.00 | 0.3 | no, no, no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | central | 0.12, 0.08, 0.26 | 1.09, 0.71, 2.33 | 1.0 | yes, no, yes |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no food-grade membrane supplier, slow plant learning | 0.12, 0.08, 0.26 | 1.09, 0.71, 2.33 | never | no, no, no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | slow learning | 0.12, 0.08, 0.26 | 1.09, 0.71, 2.33 | 3.0 | no, no, no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | fast learning | 0.12, 0.08, 0.26 | 1.09, 0.71, 2.33 | 0.3 | yes, yes, yes |
| 5. Plus engineered cells | central | 1.89, 0.58, 9.46 | 5.19, 1.60, 25.99 | 1.0 | yes, yes, yes |
| 5. Plus engineered cells | no food-grade membrane supplier, slow plant learning | 1.89, 0.58, 9.46 | 5.19, 1.60, 25.99 | never | no, no, no |
| 5. Plus engineered cells | slow learning | 1.89, 0.58, 9.46 | 5.19, 1.60, 25.99 | 3.0 | yes, no, yes |
| 5. Plus engineered cells | fast learning | 1.89, 0.58, 9.46 | 5.19, 1.60, 25.99 | 0.3 | yes, yes, yes |

**Which products count as premium (decided 2026-11-19).** Premium products are the rows the model labels premium: a cut priced at
2.5 times its species' cheapest form or more. When world seafood was re-priced by consumption the single fillet row ($16) was split
into whole fish and ordinary fillets ($7) and premium fillets and shrimp ($20: salmon, shrimp, cod, tuna loins). The new premium
row is premium by the model's rule, so it joins organic chicken, heritage pork, prime or wagyu beef and sushi-grade seafood in the
list and in the response table of section 6. It is a market of about 13 Mt a year, five times the other four together (2.6 Mt).
So the tables give every count twice: with it, and for the four small premium markets alone.

- **Premium products are where cultivated meat is closest to the price it competes with**: at Central's cost it is level with
  prime or wagyu beef (0.96 times its price) and 1.24 times sushi-grade seafood. Those two markets are small
  (`premium_market_sizes.md`: about 0.5 Mt and 1.2 Mt a year). Against premium fillets and shrimp it is 2.16 times the price.
- **Central's first sales are half premium products, half beef steaks.** Of 0.26 Mt a year at its own cost, 0.12 Mt are premium
  products (47% of sales): premium fillets and shrimp 0.044 Mt, prime beef 0.043 Mt, sushi-grade seafood 0.037 Mt. Another
  0.124 Mt (47%) are beef steaks at 2.12 times their price, and 0.011 Mt sheep and goat. Mince is under 1%. Without premium
  fillets and shrimp the four small premium markets are 30% of sales. Before the audit batch premium products were 11% of a much
  larger 1.78 Mt. Three things changed: cells are dearer; ordinary fish fillets, where Central sold 0.70 Mt at 2.26 times a
  $16 price, are now a $7 product that cultivated fish costs 6.2 times; and buyers of cuts are no longer less sensitive to price.
- A cut still costs less to make than mince whenever cells cost more than about $12 a kilo, as Central's do: a cut is 0.8 kg of
  cells, a plant-protein matrix and $2 of assembly beyond what mince pays (`structuring_cost.md`).
  The buyers are the upper end of the spread of liking (`liking_spread.md`), not buyers of organic meat, who are the most hostile
  to it (`demand_heterogeneity_evidence.md`).
- **Premium products alone just reach the switch, and only with premium fillets and shrimp.** The five need 1.09 million m² of
  membrane a year, 9% past the switch at 1.0. The four small markets alone need 0.71 million and fall short. All of Central's
  sales need 2.33 million. So the premium start matters again: without its premium products, or without its beef steaks, Central
  would cross by only a quarter (1.24 million m² either way). No single group of products carries it with room to spare.
- **The unlocking is large once the membrane is cheap.** At $17.75 a kilo of cells cultivated meat costs 0.59 times prime beef,
  0.76 times sushi-grade seafood and 1.33 times premium fillets and shrimp. Its share of prime beef rises from 7.6% to 26.5%, of
  sushi-grade seafood from 2.8% to 14.3%, and of premium fillets and shrimp from 0.33% to 4.3%. These rises are far steeper than
  history supports (section 6).
- **The loop reaches beef steaks and premium fish, not chicken, pork or mince.** At Central's resting point cultivated beef steak
  is 1.30 times the price of the animal one and premium fillet 1.33 times; sheep and goat 1.9 times; chicken and pork cuts
  3.0–3.3 times; ordinary fish 3.8 times; mince 2.5–5.6 times. Of its 3.28 Mt a year, 2.10 Mt are cuts (beef steaks 1.41 Mt),
  0.92 Mt premium products (premium fillets and shrimp 0.57 Mt) and 0.26 Mt mince, for 0.98% of world meat. Only the best case's
  cells take the loop into mince and processed meat (6.30 Mt a year at their resting point).

## 5. How strong is the loop, and how well is that known?

| scenario | its own cost and share | first pass: the learning its own volume brings | resting point | part of the share gain from later rounds | resting point with demand anchored on premium meats (its own share there) |
|---|---|---|---|---|---|
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | $32.80, 0.08% | $20.04, 0.66% | $17.75, 0.98% | 35% | $18.18, 0.59% (0.10%) |
| 5. Plus engineered cells | $11.46, 2.81% | $6.83, 6.24% | $6.66, 6.43% | 5% | $6.83, 2.76% (1.44%) |

| input, across its range | 3. Plus cells selected to grow faster on the low-waste feed (Central): cells, share | 5. Plus engineered cells: cells, share |
|---|---|---|
| Membrane demand at which a food-grade supplier appears (300000 to 3e+06 m2 a year) | $17.68 to $31.66, 0.99% to 0.10% | $6.66 to $6.70, 6.43% to 6.39% |
| That supplier's first price (60 to 400 $/m2) | $17.68 to $18.79, 0.99% to 0.82% | $6.66 to $6.88, 6.43% to 6.19% |
| Membrane's price fall per doubling (0.1 to 0.28 per doubling) | $18.09 to $17.68, 0.92% to 0.99% | $6.75 to $6.66, 6.33% to 6.43% |
| Membrane's price floor (20 to 120 $/m2) | $17.75 to $18.38, 0.98% to 0.88% | $6.65 to $6.86, 6.45% to 6.21% |
| Plant's cost fall per doubling (0.03 to 0.18 per doubling) | $19.73 to $15.87, 0.69% to 1.35% | $7.28 to $6.63, 5.76% to 6.48% |
| Animal-cell tanks installed today (6500 to 11800 m3) | $17.59 to $18.07, 1.01% to 0.93% | $6.63 to $6.73, 6.47% to 6.36% |
| World meat, boneless (300 to 384 Mt a year) | $17.86 to $17.63, 0.96% to 1.00% | $6.68 to $6.64, 6.41% to 6.46% |

- **For Central about a third of the gain is a loop; for the best case it is one step.** 65% of Central's gain in share comes on
  the first pass: the 0.26 Mt it already sells crosses the membrane switch, cells fall to $20.04 and the share rises to 0.66%.
  Later rounds, where cheaper cells sell more and more sales make cells cheaper again, add the other 35% (to $17.75 and 0.98%).
  For the best case's cells the first pass gives 95%. Before the audit batch the first pass gave 81% of Central's gain. The reason
  is the thin margin: at 2.3 times the switch the first pass buys membrane at $118 a m² and a plant at 0.86 of today's cost; the
  later rounds take them to $57 and 0.63. So Central's result rests on one event, a food-grade membrane supplier, and for a third
  of it on the strength of a feedback that cannot be measured.
- **For Central the switch's level now matters most.** With a switch at 3 million m² and everything else central it stays at
  $31.66 and 0.10%; at 0.3 million it rests at $17.68 and 0.99%. Before the audit batch a 3 million m² switch cost it 11 cents.
  Then come the plant's learning rate ($19.73 to $15.87, 0.69% to 1.35%), the supplier's first price and the membrane's floor;
  the speed of the membrane's later fall matters little.
- **The best case's cells are sturdy on cost**: $6.63–7.28 across every input.
- **The share side is weaker than the cost side.** With the share taken from the single curve fitted to premium real meats
  (`premium_curve.md`) in place of the model's, the cells cost about the same ($18.18 and $6.83) but Central's share is 0.59%, not
  0.98%, and the best case's 2.76%, not 6.43%. At Central's own cost the two demand sides are close (0.10% against 0.08%), and on
  the fitted curve Central's own sales also cross the switch (3.0 million m²). They part as cells get cheaper, because the
  fitted curve gains less from a falling price.

## 6. The checks (2026-11-18)

**How big are the premium markets?** Several times smaller than the model's tables had them (`premium_market_sizes.md`): sushi-grade
seafood about 1.2 Mt a year (the table had 5.4) and prime or wagyu beef about 0.5 Mt (1.35). The tables were corrected. Since the
seafood re-pricing of 2026-11-19 the model also has premium fillets and shrimp, about 13 Mt a year at $20 a kilo
(`world_seafood_prices.md`). The four small premium markets alone do not carry Central past the switch (0.71 million m² against
1.0); with premium fillets and shrimp the premium products just do (1.09 million m²); section 4.

**Would a food-grade membrane exist, and at what price?** No price is published for any steam- or caustic-tolerant food-grade
hollow-fibre or tubular module (Pentair X-Flow, Microza, ROMICON, Membralox and TAMI are quote-only). The neighbours bracket it:

| module | price | source | access |
|---|---|---|---|
| Repligen KrosFlo process hollow fibre, about 10 m² | $800–1,200 a m² | store.repligen.com, 2026 | SNIP |
| Repligen ATF, 11 m² (the model's) | $1,450 a m² | Humbird 2021 | FT |
| inge dizzer XL water ultrafiltration module, 60 m², cleaned at pH 1–13 | about $66 a m², one unit | distributor listing; specifications read | SNIP; FT |
| Koch sanitary dairy spiral (not steam-tolerant: 50 °C, pH 1.8–11) | $27–62 a m² | reseller; Koch data sheet | SNIP; FT |
| Ceramic module for water | "US$100/m2" (a vendor's claim) | trade article | SNIP |
| Sterile dialysers | under $10 a m² | market listings | SNIP |

Judgement: $150 a m² at a million m² a year (80% range 60–400; about 70% that it is $250 or less), and a floor of about $50 (20–120).

**Can a hollow fibre hold a quarter cells by volume for a month?** Partly shown, at bench scale only.
- Clincke et al. 2013 (FT): CHO cells on a 0.2 µm hollow fibre in a 4 L tank reached 2.1 × 10⁸ cells a ml and held 0.9–1.3 × 10⁸ (about
  27–35% cells by volume, from their cell diameters) for over two weeks; one fibre ran 30 days. The limits were viscosity and
  pressure, not fouling.
- Yeast cell-recycle fermentation on hollow fibres ran routinely at 100–150 g of dry cells a litre (Lee & Chang 1987, ABS), but food
  uses at high solids clean after hours to days (brewery yeast on ceramic, Brauwelt, FT).
- Nothing was found above bench scale for a month. Judgement: about 50–60% that one module holds it for a month at industrial size, about
  75% with a mid-run backflush or a standby module.

**How much does a price cut unlock?** The model against history (percent more volume per percent lower price):

| premium product | price against it: at $32.80 a kilo of cells, at $17.75 | cultivated meat's share of it | percent more share per percent lower price |
|---|---|---|---|
| chicken (organic) | 3.33×, 2.04× | 0.04%, 1.35% | 7.5 |
| pork (heritage) | 2.70×, 1.66× | 0.12%, 2.37% | 6.0 |
| beef (prime/wagyu) | 0.96×, 0.59× | 7.57%, 26.47% | 2.6 |
| seafood (premium fillet, shrimp) | 2.16×, 1.33× | 0.33%, 4.28% | 5.2 |
| seafood (sushi) | 1.24×, 0.76× | 2.78%, 14.28% | 3.3 |
| history, along the demand curve (farmed salmon while still a premium product) | | | 1–1.5 |
| history, in total, with demand growth mixed in (salmon, US broilers, US catfish) | | | 1.3–4.1 |

- Farmed salmon is the closest case: 13 kt in 1980 to over 1 Mt in 1999 while its real price fell to a third (Asche, Bjørndal & Young
  2001, FT; Bjørndal & Tusvik 2017, FT). Early growth was largely "a move down along the demand schedule"; since 2000 nearly all growth
  has been demand shifting at flat prices. US broilers: real price −67% and consumption per person up fourfold, 1955–87 (Bishop &
  Christensen, USDA 1989, FT).
- **The model's premium products now respond to price far more strongly than history shows. This check fails.** Where cultivated
  meat stays dearer than the premium product (organic chicken, heritage pork, premium fillets and shrimp: 2.2–3.3 times their
  price at Central's own cost, 1.3–2.0 times at $17.75) the response is 5.2–7.5. That is above even history's totals (1.3–4.1) and
  over three times the top of farmed salmon's range along the demand curve (1–1.5). Where it ends well below the premium product's
  price (prime beef 0.59 times, sushi-grade seafood 0.76 times) the response is 2.6 and 3.3: above salmon's range along the curve,
  inside the totals. Before the audit batch the four products then listed gave 0.6–1.5, inside or below history's range.
- **Why it changed.** Until the audit batch the tier rule made buyers of cuts and premium products less sensitive to price. The
  audit found the rule raised cultivated meat's share wherever it was the dearer product, and removed it (`audit_2026-11-19.md`,
  D3). What is left is the model's own curve. At two to three times a meat's price only the few shoppers who like cultivated meat
  most buy it, and each percent off the price brings in 3–6% more of them (`demand_checks.md`).
- **What it means for the loop.** Between Central's own cost and its resting point shop prices fall by about 39% and its sales
  rise twelve-fold, a response of 5.1 overall. At the top of salmon's range along the curve (1.5) the same fall in price would
  roughly double its sales (to about 0.16% of world meat); at the top of history's totals (4.1) it would give about seven times
  (about 0.6%). The demand anchored on premium real meats gives 0.59% (section 5). Salmon was measured as a product that already
  held part of its market at a modest premium, so the comparison is not exact. But the size of Central's gain rests on a response
  that history does not support, and is more likely too large than too small.

**How fast?** The model has no time in it. History, given success: a hundred-fold growth took farmed salmon about 18 years (29% a
year), US corn ethanol about 29 years for 76-fold (with a mandate), US broilers 45–50 years; Quorn has not done it in 40. A fair range
is 15–30 years, with something like a one-in-three chance of stalling as Quorn and plant-based meat did (the last is a judgement).

## 7. Evidence on learning rates

| finding | source | access |
|---|---|---|
| Membrane-bioreactor membrane cost per m² in 2025 at 0.3 of its 2005 level (18–26% a doubling if area doubled 4–6 times) | Abbott, WIOA conference 2025 | FT; the doublings are MEM |
| Seawater reverse-osmosis plants: 15% a doubling, 4,237 plants, 1977–2015; 12% with scale removed, and slower in the last ten years | Caldera & Breyer 2017; Mayor 2020 | ABS |
| Corn ethanol: processing cost 13% a doubling; capital charges −83% at constant plant size over 7 doublings (about 20% a doubling, overstated by falling interest rates) | Hettinga et al. 2009 | FT |
| Power plants: nuclear negative to 6%, coal 8%, gas turbines 15%, hydro 1.4%, solar 23% | Rubin et al. 2015, Table 1 | FT |
| Electrolysers: 18–47% globally but 0.6–9% within countries | Cambridge EPRG WP 2024 | SNIP |
| Mammalian cell-culture capacity "nearly 6,500 kL" (2023); 10.9–11.8 million L on another basis | BDO/BPTC via BioProcess International 2023; BioPlan | FT; SNIP |
| Repligen: filtration revenue about $403M of $738M (2025); ATF at "500+" sites | earnings summaries | SNIP |

## 8. What this rests on, and what is still unknown

- **The switch is a judgement** (about 65% that a food-grade supplier appears once demand passes 1 million m² a year). Without it
  little moves.
- **The audit batch of 2026-11-19.** Cells got dearer (Central $26.43 to $32.80: ammonia tolerance 4 mM, membranes thrown away
  with lost runs), world seafood was re-priced by consumption, and the tier rule was replaced by a blend penalty with no lower
  price sensitivity for cuts or premium products. Central's sales at its own cost fell from 1.78 to 0.26 Mt a year, its margin
  over the switch from ten times to 2.3 times, and its resting point from $15.05 and 2.49% to $17.75 and 0.98%.
- **Central's cost is itself uncertain.** Across draws its cells cost $27–57 a kilo (8 in 10), with a median of $37. At $37 its
  sales need 1.1 million m² of membrane, barely past the switch; at $57 they need under 0.1 million. Only at the point cost or
  below does it cross with any room.
- **The cut cost.** Since 2026-11-19 a cut costs 0.8 kg of cells, a $2 plant-protein matrix and $2 of assembly beyond what
  mince pays (`structuring_cost.md`). With the old rule (a full kilo of cells and a $6 scaffold) Central rested at $15.83 and 0.86%
  at the costs of that morning.
- **Still unknown:** an actual quote for a steam-tolerant food-grade module; a month-long run of animal cells at a quarter by volume
  above bench scale; the yearly area of perfusion filters sold today (estimated, not published); retail prices of the premium
  products by grade.
- **Resting points, not a path.** Learning is counted on yearly scale, not cumulative output, and nothing says who pays for the early
  years.
- **Judgement:** that a food-grade membrane at $250 a m² or less exists if cultivated meat sells 0.5 Mt a year: about 0.6. That
  learning of this kind takes the best case's cells to $7 or less, given the best case's cells exist: about 0.55 (not revised; the
  central case now gives $6.66 where it gave $6.41, and slow plant learning alone gives $7.28). That Central's sales pass the
  switch with no outside push: about 0.4 (provisional; revised from 0.7 at the audit batch of 2026-11-19, and from 0.5 before
  that). At its point cost its sales need 2.3 times the switch's area, where they needed ten times; at the median of its cost
  draws they barely reach it; a switch near the top of its range (3 million m²) stops it; and the curve fitted to premium real
  meats agrees at its own cost (0.10% against 0.08%). That learning takes Central above 1% of world meat: about 0.1
  (provisional; revised from 0.4 at the audit batch, and from 0.15 before that). The central case rests just under 1% (0.98%);
  only fast learning passes it (1.42%); slow learning gives 0.08% left alone and 0.47% with a push, no supplier 0.08%, and the
  demand anchored on premium meats 0.59%. The response to price behind these gains is stronger than history shows, and the
  switch is itself only about 65%.

## Sources

1. Abbott, "Membrane bioreactors: 20 years on", WIOA conference 2025 (FT).
2. Caldera & Breyer 2017, Water Resources Research (ABS); Mayor 2020, Water Resources Research (ABS).
3. Hettinga et al. 2009, Energy Policy 37 (FT); Rubin, Azevedo, Jaramillo & Yeh 2015, Energy Policy 86 (FT).
4. BDO/BPTC capacity survey, via BioProcess International, October 2023 (FT).
5. Humbird 2021, Biotechnology and Bioengineering (FT): $16,000 per ATF membrane, the model's $1,450 a m².
6. Clincke et al. 2013, Biotechnology Progress, PMC3752962 (FT). Lee & Chang 1987, Biotechnology and Bioengineering 29(9) (ABS).
7. Asche, Bjørndal & Young 2001 (FT); Bjørndal & Tusvik 2017, NTNU (FT); Asche, Roll & Tveterås 2013 (FT); Bishop & Christensen, USDA 1989 (FT).
8. Moore, on Quorn's history (FT); GFI on US plant-based retail sales 2025 (FT); EIA via AFDC on US ethanol output (FT).
9. FAO Food Outlook, November 2025 (SNIP).
