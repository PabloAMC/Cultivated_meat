# Does cultivated meat get cheaper as it sells more? Cost and share solved together

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50; cut cost rebuilt (0.8 cells + $2 matrix + $2 assembly beyond mince), cuts cheaper.

> Repinned 2026-11-19 (audit batch): cells dearer (ammonia tolerance 4 mM), seafood re-priced by consumption, the tier rule replaced by a blend penalty, the equal-price share drawn around its 13% setting; see audit_2026-11-19.md.

> Repinned 2026-11-19 (second round): shoppers' liking is a Student's t spread (standard deviation 3.9 utils, 4 degrees of freedom) on a 67-point grid, not a normal spread of 5 on fifteen points; see liking_spread.md.

Date: 2026-11-18; revised twice the same day: after the checks in section 6 (the premium markets were sized from data) and after the
shopper model gained a spread of liking across shoppers (`liking_spread.md`). Code: `market_size_loop.py`; test: `tests/test_market_size_loop.py`.
The study itself changes no default.

Access levels: **FT** full text read; **ABS** abstract only; **SNIP** search snippet; **MEM** background knowledge, unchecked.

**The idea** (Pablo): the model runs one way, from a cost to a share. But the cell filter's membrane and the plant are priced as today's
small biopharma supply industry prices them, and even a fraction of a percent of world meat would need several times all the
animal-cell tank volume that exists. So the cost should fall as the market grows. And the loop should start in premium products: where
cultivated meat first undercuts the premium product it competes with (Wildtype's salmon against sushi-grade salmon), the demand that
unlocks is the volume that makes everything cheaper.

**In short (2026-11-19, second round: shoppers' liking is a Student's t spread).** At their point costs Central and the best
case's cells both sell enough to bring a food-grade membrane supplier into being, and both get much cheaper for it. Central's
cells fall from $32.80 to $17.69 and its share rises from 0.16% to 1.06% of world meat. The best case's cells come close to price
parity but do not reach it ($6.67 against $6.14). The audit batch earlier the same day had weakened three things; the heavier tail
of liking restores two of them:

- **Central's margin over the switch is comfortable again.** Its sales need 4.9 times the switch's membrane area (2.3 times after
  the audit batch, ten times before it). With slow learning it crosses on its own and has one resting point, $21.91 and 0.59%.
- **About a quarter of Central's gain is a loop**, the rest one step (a third after the audit batch, a fifth before it).
- **The model's response to price is still more than twice what history shows along a demand curve** (3.3–3.7 against 1–1.5),
  though now inside history's totals (section 6). The size of Central's gain rests on it.

Premium products are about a quarter of Central's first sales, beef steaks a third, other cuts most of the rest. Published cells
sell a few thousand tonnes and never start on their own. Here "the best case" is its cells with the model's ordinary demand (13%
at equal price), not its own 55%. (After the audit batch, with a normal spread of liking: Central $17.75 and 0.98% from 0.08%, two
resting points under slow learning; the best case $6.66 and 6.43%. Before the audit batch: Central $15.05 and 2.49%; the best case
$6.41 and 8.30%.)

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
| 0.5 | 0.149% | 126,674 | 76 | 0.65× | $69.09 | 0.01% |
| 2 | 0.595% | 506,698 | 51 | 0.53× | $64.19 | 0.01% |
| 10 | 2.98% | 2,533,490 | 50 | 0.42× | $60.01 | 0.02% |
| 35 | 10.4% | 8,867,215 | 50 | 0.34× | $57.39 | 0.02% |

**3. Plus cells selected to grow faster on the low-waste feed (Central)** (no learning: $32.80)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.00298% | 485 | 1,450 | 0.99× | $32.74 | 0.16% |
| 0.1 | 0.0298% | 4,854 | 1,450 | 0.93× | $32.28 | 0.17% |
| 0.5 | 0.149% | 24,271 | 98 | 0.81× | $19.45 | 0.83% |
| 2 | 0.595% | 97,086 | 66 | 0.68× | $18.17 | 0.99% |
| 10 | 2.98% | 485,428 | 50 | 0.53× | $16.98 | 1.17% |
| 35 | 10.4% | 1,698,999 | 50 | 0.44× | $16.29 | 1.30% |

**5. Plus engineered cells** (no learning: $11.46)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.00298% | 227 | 1,450 | 1.00× | $11.45 | 2.74% |
| 0.1 | 0.0298% | 2,267 | 1,450 | 0.96× | $11.38 | 2.77% |
| 0.5 | 0.149% | 11,334 | 137 | 0.87× | $7.59 | 5.26% |
| 2 | 0.595% | 45,335 | 92 | 0.75× | $7.22 | 5.63% |
| 10 | 2.98% | 226,676 | 58 | 0.60× | $6.82 | 6.05% |
| 35 | 10.4% | 793,367 | 50 | 0.52× | $6.63 | 6.26% |

"Share that cost would buy" is the main model's long-run share at that cost. Where it exceeds the share the volume is, the market grows;
where it is less, it shrinks. With both items at their floors the cells cost $55.30 (published cells), $15.13 (Central) and
$6.63 (the best case).

## 3. Where cost and share agree

| scenario | learning | the main model: cells, share | resting point from below: cells, share, Mt a year | from above: cells, share, Mt a year |
|---|---|---|---|---|
| 1. Published cells | central | $111.89, under 0.01% | $110.99, under 0.01%, 0.006 | $110.99, under 0.01%, 0.006 |
| 1. Published cells | no food-grade membrane supplier, slow plant learning | $111.89, under 0.01% | $111.63, under 0.01%, 0.006 | $111.63, under 0.01%, 0.006 |
| 1. Published cells | slow learning | $111.89, under 0.01% | $111.63, under 0.01%, 0.006 | $111.63, under 0.01%, 0.006 |
| 1. Published cells | fast learning | $111.89, under 0.01% | $110.16, under 0.01%, 0.006 | $75.43, under 0.01%, 0.03 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | central | $32.80, 0.16% | $17.69, 1.06%, 3.56 | $17.69, 1.06%, 3.56 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no food-grade membrane supplier, slow plant learning | $32.80, 0.16% | $32.33, 0.17%, 0.58 | $32.33, 0.17%, 0.58 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | slow learning | $32.80, 0.16% | $21.91, 0.59%, 1.99 | $21.91, 0.59%, 1.99 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | fast learning | $32.80, 0.16% | $15.53, 1.45%, 4.88 | $15.53, 1.45%, 4.88 |
| 5. Plus engineered cells | central | $11.46, 2.74% | $6.67, 6.21%, 20.88 | $6.67, 6.21%, 20.88 |
| 5. Plus engineered cells | no food-grade membrane supplier, slow plant learning | $11.46, 2.74% | $11.18, 2.86%, 9.61 | $11.18, 2.86%, 9.61 |
| 5. Plus engineered cells | slow learning | $11.46, 2.74% | $7.88, 5.01%, 16.82 | $7.88, 5.01%, 16.82 |
| 5. Plus engineered cells | fast learning | $11.46, 2.74% | $6.54, 6.36%, 21.36 | $6.54, 6.36%, 21.36 |

"From below" starts with no learning; "from above" starts with everything at its floor. Where the two differ there are two resting
points, and reaching the upper one needs someone to carry the industry across the gap.

- **The best case's cells come close to parity by this route but do not reach it: $6.67 against the $6.14 parity needs, and 6.21% of
  world meat** (2.74% without learning). They rest 4 cents above the cost with both items at their floors ($6.63), and no single
  input across its range takes them lower (section 5); fast learning, all its inputs at once, gives $6.54. With the best case's
  own demand (55% at equal price, 13.8% without learning) they rest at the floors, $6.63, and take 29.0% of world meat. (With the
  normal spread: $6.66 and 6.43%, and 35.6% with its own demand. Before the audit batch: $6.41 and 8.30%.)
- **Central: cells fall from $32.80 to $17.69 and the share rises from 0.16% to 1.06%**, six and a half times. Its 0.55 Mt a year
  needs 4.86 million m² of membrane, 4.9 times the switch at 1.0, so it crosses on its own sales and has one resting point. It
  would cross on its own with a switch up to about 5.8 million m², beyond the top of the switch's range (0.3–3).
- **With slow learning Central has one resting point again**: $21.91 and 0.59%. A switch at 3 million m² is below what its sales
  need, so there is no gap for anyone to carry it across. This has flipped three times in a day. After the cut-cost repin: one
  point ($18.69 and 1.48%). After the audit batch, with Central's sales at 0.26 Mt: two points ($32.48 and 0.08% left alone,
  $22.07 and 0.47% if pushed). Now, with the heavier tail of liking doubling its first sales: one. The conclusion follows
  Central's sales at its own cost, which the model's far tail decides.
- **Published cells never start on their own.** At $112 a kilo they sell 0.002% of world meat, about 6,000 tonnes a year, which
  needs 0.12 million m² of membrane. Left alone they stay within $2 of their own cost in every case. Only with fast learning and
  an outside push is there an upper resting point, at $75.43 and under 0.01% of world meat. With both items at their floors they
  would cost $55.30.
- **Without a food-grade membrane supplier little changes**: Central $32.33 and 0.17%, the best case $11.18 and 2.86%. The plant's
  learning alone is worth 30 to 50 cents a kilo.

## 4. The loop runs on ordinary cuts more than on premium products

| scenario | stage | cells, $/kg | sold, Mt a year: premium products, cuts, mince and processed | premium products' part of sales (without premium fillets and shrimp) | chicken (organic): price against it, share of it | pork (heritage): price against it, share of it | beef (prime/wagyu): price against it, share of it | seafood (premium fillet, shrimp): price against it, share of it | seafood (sushi): price against it, share of it |
|---|---|---|---|---|---|---|---|---|---|
| 1. Published cells | no learning | $111.89 | 0.001, 0.004, 0.001 | 22% (7%) | 10.09×, under 0.01% | 8.20×, under 0.01% | 2.91×, 0.02% | 6.56×, under 0.01% | 3.75×, 0.02% |
| 1. Published cells | resting point | $110.99 | 0.001, 0.004, 0.001 | 22% (7%) | 10.01×, under 0.01% | 8.13×, under 0.01% | 2.89×, 0.03% | 6.51×, under 0.01% | 3.72×, 0.02% |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no learning | $32.80 | 0.15, 0.34, 0.06 | 27% (13%) | 3.33×, 0.22% | 2.70×, 0.35% | 0.96×, 6.30% | 2.16×, 0.59% | 1.24×, 2.50% |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | resting point | $17.69 | 0.88, 2.20, 0.48 | 25% (11%) | 2.04×, 1.33% | 1.65×, 2.17% | 0.59×, 31.34% | 1.32×, 3.69% | 0.76×, 14.98% |
| 5. Plus engineered cells | no learning | $11.46 | 1.87, 5.60, 1.73 | 20% (8%) | 1.50×, 3.44% | 1.22×, 5.44% | 0.43×, 50.20% | 0.98×, 8.83% | 0.56×, 28.99% |
| 5. Plus engineered cells | resting point | $6.67 | 3.26, 11.98, 5.64 | 16% (5%) | 1.09×, 7.58% | 0.89×, 11.28% | 0.32×, 64.82% | 0.71×, 16.97% | 0.41×, 43.72% |

| scenario | learning | sold at the scenario's own cost, Mt a year: premium products, premium products without premium fillets and shrimp, everything | membrane each needs, million m² a year | the switch, million m² a year | which of the three cross it alone? |
|---|---|---|---|---|---|
| 1. Published cells | central | 0.001, under 0.001, 0.006 | 0.03, 0.01, 0.12 | 1.0 | no, no, no |
| 1. Published cells | no food-grade membrane supplier, slow plant learning | 0.001, under 0.001, 0.006 | 0.03, 0.01, 0.12 | never | no, no, no |
| 1. Published cells | slow learning | 0.001, under 0.001, 0.006 | 0.03, 0.01, 0.12 | 3.0 | no, no, no |
| 1. Published cells | fast learning | 0.001, under 0.001, 0.006 | 0.03, 0.01, 0.12 | 0.3 | no, no, no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | central | 0.15, 0.07, 0.55 | 1.31, 0.62, 4.86 | 1.0 | yes, no, yes |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no food-grade membrane supplier, slow plant learning | 0.15, 0.07, 0.55 | 1.31, 0.62, 4.86 | never | no, no, no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | slow learning | 0.15, 0.07, 0.55 | 1.31, 0.62, 4.86 | 3.0 | no, no, yes |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | fast learning | 0.15, 0.07, 0.55 | 1.31, 0.62, 4.86 | 0.3 | yes, yes, yes |
| 5. Plus engineered cells | central | 1.87, 0.70, 9.19 | 5.13, 1.92, 25.26 | 1.0 | yes, yes, yes |
| 5. Plus engineered cells | no food-grade membrane supplier, slow plant learning | 1.87, 0.70, 9.19 | 5.13, 1.92, 25.26 | never | no, no, no |
| 5. Plus engineered cells | slow learning | 1.87, 0.70, 9.19 | 5.13, 1.92, 25.26 | 3.0 | yes, no, yes |
| 5. Plus engineered cells | fast learning | 1.87, 0.70, 9.19 | 5.13, 1.92, 25.26 | 0.3 | yes, yes, yes |

**Which products count as premium (decided 2026-11-19).** Premium products are the rows the model labels premium: a cut priced at
2.5 times its species' cheapest form or more. When world seafood was re-priced by consumption the single fillet row ($16) was split
into whole fish and ordinary fillets ($7) and premium fillets and shrimp ($20: salmon, shrimp, cod, tuna loins). The new premium
row is premium by the model's rule, so it joins organic chicken, heritage pork, prime or wagyu beef and sushi-grade seafood in the
list and in the response table of section 6. It is a market of about 13 Mt a year, five times the other four together (2.6 Mt).
So the tables give every count twice: with it, and for the four small premium markets alone.

- **Premium products are where cultivated meat is closest to the price it competes with**: at Central's cost it is level with
  prime or wagyu beef (0.96 times its price) and 1.24 times sushi-grade seafood. Those two markets are small
  (`premium_market_sizes.md`: about 0.5 Mt and 1.2 Mt a year). Against premium fillets and shrimp it is 2.16 times the price.
- **Most of Central's first sales are ordinary cuts.** Of 0.55 Mt a year at its own cost, 0.34 Mt are cuts (62%): beef steaks
  0.18 Mt at 2.12 times their price, then pork cuts, sheep and goat and chicken cuts at three to five and a half times theirs (0.04–0.05 Mt each).
  Premium products are 0.15 Mt (27%): premium fillets and shrimp 0.08 Mt, prime beef and sushi-grade seafood 0.03–0.04 Mt each.
  Without premium fillets and shrimp the four small premium markets are 13% of sales. Mince and processed meat are 0.06 Mt (11%).
  With the normal spread of the audit batch Central sold half as much (0.26 Mt), half of it premium products and half beef
  steaks, and almost nothing at more than three times a meat's price. The heavier tail adds buyers of products at four to ten times
  their meat's price: a third of these first sales. Nothing measures demand that far out (`liking_spread.md` §6).
- A cut still costs less to make than mince whenever cells cost more than about $12 a kilo, as Central's do: a cut is 0.8 kg of
  cells, a plant-protein matrix and $2 of assembly beyond what mince pays (`structuring_cost.md`).
  The buyers are the upper end of the spread of liking (`liking_spread.md`), not buyers of organic meat, who are the most hostile
  to it (`demand_heterogeneity_evidence.md`).
- **Premium products alone reach the switch, but only with premium fillets and shrimp.** The five need 1.31 million m² of
  membrane a year, 31% past the switch at 1.0. The four small markets alone need 0.62 million and fall short. All of Central's
  sales need 4.86 million. So the premium start is not needed: without any premium product Central's other sales need 3.55
  million m², past even a switch at 3 million.
- **The unlocking is large once the membrane is cheap.** At $17.69 a kilo of cells cultivated meat costs 0.59 times prime beef,
  0.76 times sushi-grade seafood and 1.32 times premium fillets and shrimp. Its share of prime beef rises from 6.3% to 31.3%, of
  sushi-grade seafood from 2.5% to 15.0%, and of premium fillets and shrimp from 0.59% to 3.7%. These rises are steeper than
  farmed salmon's history supports (section 6).
- **The loop reaches beef steaks and premium fish; chicken, pork and mince stay far above their meat's price.** At Central's
  resting point cultivated beef steak is 1.30 times the price of the animal one and premium fillet 1.32 times; sheep and goat
  1.9 times; chicken and pork cuts 2.9–3.3 times; ordinary fish 3.8 times; mince 2.5–5.6 times. Of its 3.56 Mt a year, 2.20 Mt
  are cuts (beef steaks 1.18 Mt), 0.88 Mt premium products (premium fillets and shrimp 0.49 Mt) and 0.48 Mt mince, for 1.06% of
  world meat. Only the best case's cells take the loop far into mince and processed meat (5.64 Mt a year at their resting point).

## 5. How strong is the loop, and how well is that known?

| scenario | its own cost and share | first pass: the learning its own volume brings | resting point | part of the share gain from later rounds | resting point with demand anchored on premium meats (its own share there) |
|---|---|---|---|---|---|
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | $32.80, 0.16% | $19.36, 0.84% | $17.69, 1.06% | 25% | $18.18, 0.59% (0.10%) |
| 5. Plus engineered cells | $11.46, 2.74% | $6.84, 6.03% | $6.67, 6.21% | 5% | $6.83, 2.76% (1.44%) |

| input, across its range | 3. Plus cells selected to grow faster on the low-waste feed (Central): cells, share | 5. Plus engineered cells: cells, share |
|---|---|---|
| Membrane demand at which a food-grade supplier appears (300000 to 3e+06 m2 a year) | $17.63 to $17.90, 1.07% to 1.03% | $6.67 to $6.71, 6.21% to 6.17% |
| That supplier's first price (60 to 400 $/m2) | $17.63 to $18.66, 1.07% to 0.92% | $6.67 to $6.89, 6.21% to 5.97% |
| Membrane's price fall per doubling (0.1 to 0.28 per doubling) | $18.02 to $17.63, 1.01% to 1.07% | $6.76 to $6.67, 6.11% to 6.21% |
| Membrane's price floor (20 to 120 $/m2) | $17.69 to $18.31, 1.06% to 0.97% | $6.66 to $6.87, 6.22% to 5.99% |
| Plant's cost fall per doubling (0.03 to 0.18 per doubling) | $19.66 to $15.85, 0.80% to 1.39% | $7.28 to $6.63, 5.56% to 6.26% |
| Animal-cell tanks installed today (6500 to 11800 m3) | $17.53 to $17.99, 1.08% to 1.01% | $6.63 to $6.74, 6.25% to 6.14% |
| World meat, boneless (300 to 384 Mt a year) | $17.79 to $17.57, 1.04% to 1.08% | $6.69 to $6.65, 6.19% to 6.24% |

- **It is mostly one step, not a loop.** 75% of Central's gain in share comes on the first pass: the 0.55 Mt it already sells
  crosses the membrane switch, cells fall to $19.36 and the share rises to 0.84%. Later rounds, where cheaper cells sell more and
  more sales make cells cheaper again, add the other 25% (to $17.69 and 1.06%). For the best case's cells the first pass gives
  95%. (After the audit batch, with the normal spread, later rounds gave 35% of Central's gain; before it, 19%.) The first pass
  buys membrane at $95 a m² and a plant at 0.80 of today's cost; the later rounds take them to $56 and 0.62. So the result rests
  mostly on whether one event happens, a food-grade membrane supplier, and at what price, and for a quarter on the strength of a
  feedback that cannot be measured.
- **The plant's learning rate matters most, then the food-grade supplier's first price and the membrane's floor**; the speed of
  the membrane's later fall matters little (table above). The switch's level matters little again: a 3 million m² switch costs
  Central 21 cents. With the normal spread of the audit batch it stopped Central at $31.66.
- **The best case's cells are sturdy on cost**: $6.63–7.28 across every input.
- **The share side is weaker than the cost side.** With the share taken from the single curve fitted to premium real meats
  (`premium_curve.md`) in place of the model's, the cells cost about the same ($18.18 and $6.83) but Central's share is 0.59%, not
  1.06%, and the best case's 2.76%, not 6.21%. At Central's own cost the model now gives more than the fitted curve (0.16% against
  0.10%). On the fitted curve Central's own sales need 3.0 million m²: past the central switch, and only level with a switch at
  3 million. So with slow learning the one resting point depends on which demand side is right.

## 6. The checks (2026-11-18)

**How big are the premium markets?** Several times smaller than the model's tables had them (`premium_market_sizes.md`): sushi-grade
seafood about 1.2 Mt a year (the table had 5.4) and prime or wagyu beef about 0.5 Mt (1.35). The tables were corrected. Since the
seafood re-pricing of 2026-11-19 the model also has premium fillets and shrimp, about 13 Mt a year at $20 a kilo
(`world_seafood_prices.md`). The four small premium markets alone do not carry Central past the switch (0.62 million m² against
1.0); with premium fillets and shrimp the premium products do (1.31 million m²); ordinary cuts carry it anyway (section 4).

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

| premium product | price against it: at $32.80 a kilo of cells, at $17.69 | cultivated meat's share of it | percent more share per percent lower price |
|---|---|---|---|
| chicken (organic) | 3.33×, 2.04× | 0.22%, 1.33% | 3.6 |
| pork (heritage) | 2.70×, 1.65× | 0.35%, 2.17% | 3.7 |
| beef (prime/wagyu) | 0.96×, 0.59× | 6.30%, 31.34% | 3.3 |
| seafood (premium fillet, shrimp) | 2.16×, 1.32× | 0.59%, 3.69% | 3.7 |
| seafood (sushi) | 1.24×, 0.76× | 2.50%, 14.98% | 3.6 |
| history, along the demand curve (farmed salmon while still a premium product) | | | 1–1.5 |
| history, in total, with demand growth mixed in (salmon, US broilers, US catfish) | | | 1.3–4.1 |

- Farmed salmon is the closest case: 13 kt in 1980 to over 1 Mt in 1999 while its real price fell to a third (Asche, Bjørndal & Young
  2001, FT; Bjørndal & Tusvik 2017, FT). Early growth was largely "a move down along the demand schedule"; since 2000 nearly all growth
  has been demand shifting at flat prices. US broilers: real price −67% and consumption per person up fourfold, 1955–87 (Bishop &
  Christensen, USDA 1989, FT).
- **The model's premium products respond to price more strongly than farmed salmon did along its demand curve. This check
  still fails, by less.** All five respond at 3.3–3.7, whether cultivated meat stays dearer than the product (organic chicken,
  heritage pork, premium fillets and shrimp) or ends well below its price (prime beef, sushi-grade seafood). That is more than
  twice the top of salmon's range along the curve (1–1.5), and inside history's totals, where demand growth is mixed in
  (1.3–4.1). With the normal spread of the audit batch the dearer three gave 5.2–7.5, above even the totals. Before the audit
  batch the four products then listed gave 0.6–1.5.
- **Why it changed.** Until the audit batch the tier rule made buyers of cuts and premium products less sensitive to price; the
  audit removed it (`audit_2026-11-19.md`, D3). What was left was the normal spread's tail, which thins very fast at two to three
  times a meat's price. The Student's t spread fitted later the same day has a heavier tail: more buyers at a high price to begin
  with, so fewer are added by each percent off (`liking_spread.md`). Its fit counts this check as one of three, and the best joint fit still leaves it
  outside the range.
- **What it means for the loop.** Between Central's own cost and its resting point shop prices fall by about 39% and its sales
  rise six and a half times, a response of 3.8 overall. At the top of salmon's range along the curve (1.5) the same fall in price
  would roughly double its sales (to about 0.34% of world meat); at the top of history's totals (4.1) it would give seven and a
  half times. The demand anchored on premium real meats gives 0.59% (section 5). Salmon was measured as a product that already
  held part of its market at a modest premium, so the comparison is not exact. But the size of Central's gain rests on a response
  at the strong end of what history shows, and is more likely too large than too small.

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
- **Two changes on 2026-11-19 moved Central's first sales, and the conclusions with them.** The audit batch (cells dearer, $26.43
  to $32.80; seafood re-priced; the tier rule replaced) cut its sales at its own cost from 1.78 to 0.26 Mt a year and its margin
  over the switch from ten times to 2.3. The Student's t spread of liking then raised them to 0.55 Mt and 4.9 times. Its resting
  point went from $15.05 and 2.49% to $17.75 and 0.98%, and now $17.69 and 1.06%.
- **The far tail of liking.** A third of Central's first sales are of products at four to ten times their meat's price, where
  the spread of liking is an extrapolation. Without them its sales would still need about 3.3 million m², past both switches.
- **Central's cost is itself uncertain.** Across draws its cells cost $27–57 a kilo (8 in 10), with a median of $37. At $37 its
  sales need 3.2 million m² of membrane, three times the switch; at $57 they need 0.65 million and fall short.
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
  central case gives $6.67, and slow plant learning alone $7.28). That Central's sales pass the switch with no outside push:
  about 0.65 (provisional; 0.5 at first, 0.7 after the cut-cost repin, 0.4 after the audit batch). At its point cost its sales
  need 4.9 times the switch's area and at the median of its cost draws three times; they fall short only near the top of its
  cost range; the curve fitted to premium real meats also crosses (0.10% at its own cost against the model's 0.16%). Against
  that, a third of those sales rest on the far tail of liking. That learning takes Central above 1% of world meat: about 0.2
  (provisional; 0.15 at first, 0.4 after the cut-cost repin, 0.1 after the audit batch). The central case rests just above 1%
  (1.06%) and fast learning at 1.45%; slow learning gives 0.59%, no supplier 0.17%, and the demand anchored on premium meats
  0.59%. The response to price behind these gains is more than twice farmed salmon's, and the switch is itself only about 65%.

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
