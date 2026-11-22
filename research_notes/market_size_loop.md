# Does cultivated meat get cheaper as it sells more? Cost and share solved together

> **Current figures (2026-11-21, fourth batch; tables regenerated, prose recomputed on 2026-11-22).** Plant-based
> meat's committed buyers raised the ordinary shoppers' real-meat weight and with it the blend penalty on cuts
> (`demand_checks.md` section 5). The low-lactate example comes to rest at $24.05 and 0.48% of world meat (from $48.68 and
> 0.05%; $23.91 and 0.54% in the third batch); its first sales need 2.4 times the switch's membrane area (2.6); premium products alone
> need 0.68 and 0.34 million m² with and without premium fillets and shrimp (0.75 and 0.38). With slow learning: $48.38 and
> 0.05% left alone, $30.30 and 0.24% if pushed ($48.37, 0.05%; $30.17, 0.27%). The all-favourable example's cells rest at $6.30
> and 6.27% (from $6.97 and 5.58%; $6.29, 6.81% from 6.07% in the third batch), $0.16 above parity. **One conclusion changed:**
> with the demand anchored on premium real meats the low-lactate example's own sales need 0.76 million m², short of the switch,
> so it does not cross (it rests at $48.25 and 0.015%); in the third batch they reached the switch exactly (section 5).

> 2026-11-19 (scenario restructure): the published cells are priced in perfusion as the cautious scenario (rung 1 of the ladder is a batch, with no filter to learn on); shares are the share of the meat sold; every kind of cell weighs 2 ng.

> Repinned 2026-11-21 (engine batch): the cost of cells moved (the all-favourable example $7.62 -> $6.97, its tank design now holds the culture thinner so its oxygen column passes its checks; the low-lactate example $49.50 -> $48.68; published cells $322.55 -> $316.11), because the design search runs a culture thinner when its loop fails, the building's power follows its floor and its class, and part of the crew is counted per tank. Nothing in the demand model changed; the shares that follow from the costs are recomputed. The tables are regenerated and the figures in the summary and sections 2, 3 and 5 updated; in section 4 the first-sales figures are today's, and the figures at the low-lactate example's resting point (the unlocking and the reach of the loop) are as of 2026-11-20 (final pass), when it rested at $24.95.
> Repinned 2026-11-20 (engine batch): the scenarios' cells tolerate 35 mmol/L of lactate, bubble deaths and a harvest loss are charged, a washed tank takes twice the fed-batch crew, the membrane lasts 2,415 L/m2, and growth factors, utilities and the crew follow the Humbird back-test, so cells are dearer (the low-lactate example $32.80 to $49.96 a kilo, the all-favourable example $11.67 to $18.71, Published cells in fed-batch $209 to $323) and every share here fell; the demand model did not change; see full_review_2026-11-19.md and humbird_backtest.md. Tables and prose were both redone on 2026-11-20; figures marked "before" are history.

> Repinned 2026-11-20 (final pass): the all-favourable example is now `scenarios.all_favourable()` ($18.71 to $7.62 a kilo of cells), which keeps its cells with haemodialyser fibres at $8 a m² and so buys almost no process membrane; the low-lactate example costs $49.50; the demand side is anchored on plant-based meat at 0.4% of meat by volume, incomes are nominal, conventional meat's price falls as cultivated meat takes sales, and the share of the world market closed by law is weighted by meat eaten (closed_markets.md). Tables and prose were redone; figures marked "after the engine batch" are history.

> Names (2026-11-19): the two examples are named by what they assume (the low-lactate example, the all-favourable example). Cells are described by their traits, never as a named kind of cell.

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

**In short (2026-11-21).** At its point cost the low-lactate example sells enough to bring a food-grade membrane
supplier into being, and gets much cheaper for it: its cells fall from $48.68 to $24.05 and its share rises from 0.05% to 0.48%
of world meat. The all-favourable example's cells barely use the process membrane (they are kept with haemodialyser fibres at
$8 a m²), so the switch plays no part for them: the plant's learning alone takes them from $6.97 to $6.30 and from 5.58% to
6.27%, short of the $6.14 that price parity with US minced beef or pork cuts ($12 a kilo) needs. (Third batch of 2026-11-21: $23.91
and 0.54%; $6.29 and 6.07% to 6.81%. 2026-11-20, final pass: the
low-lactate example $49.50 to $24.95 and 0.05% to 0.48%; the all-favourable example $7.62 to $6.77 and 5.44% to 6.28%.)

- **The low-lactate example's margin over the switch is thin.** Its sales need 2.4 times the switch's membrane area. With slow
  learning, where the switch is at 3 million m², it does not cross on its own and has two resting points: $48.38 and 0.05% left
  alone, $30.30 and 0.24% if pushed. With the demand anchored on premium real meats it does not cross the switch at all
  (section 5).
- **Premium products alone do not reach the switch**, with or without premium fillets and shrimp (0.68 and 0.34 million m²
  against 1.0). Ordinary cuts carry it.
- **Where the switch sits matters most** among the market-size inputs: at the top of its range it leaves the low-lactate example
  at $47.66.

About a third of the low-lactate example's gain is a loop, the rest one step. The model's response to price is well above what
history shows along a demand curve (3.7–4.2 against 1–1.5), and for prime beef and sushi-grade seafood just above history's
totals too (section 6). The size of the gain rests on it.

Premium products are about three-tenths of the low-lactate example's first sales, beef steaks about a third, other cuts most of
the rest. Published cells sell about a thousand tonnes and never start on their own. Here "the all-favourable example" is its
cells with the model's ordinary demand (14.4% of meat buyers at equal price), not its own 55%. (After the engine batch of
2026-11-20: the low-lactate example $24.00 and 0.57% from 0.05%; the all-favourable example, then $18.71, $9.78 and 4.28%. Before
it: $17.50 and 1.34% from 0.21%; $6.95 and 6.89%. After the 2026-11-19 audit batch, with a normal spread of liking: $17.75 and
0.98% from 0.08%; $6.66 and 6.43%. Before the audit batch: $15.05 and 2.49%; $6.41 and 8.30%.)

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
  scenarios' bands use: 0.29 of the low-lactate example's plant, 0.52 of the all-favourable example's).
- **Nothing else learns here**: feed, growth factors and the protectant are bought in bulk markets or are scenario switches already.
- World meat and seafood are taken as 336 Mt a year of edible weight (range 300–384): about 250 Mt of boneless meat (380 Mt of
  carcass weight) and about 87 Mt of edible seafood (FAO, SNIP).

## 2. Cost against volume

**Cautious** (no learning: $181.13)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.00298% | 941 | 1,450 | 0.98× | $180.89 | under 0.01% |
| 0.1 | 0.0298% | 9,412 | 87 | 0.89× | $87.95 | under 0.01% |
| 0.5 | 0.149% | 47,059 | 55 | 0.75× | $83.74 | under 0.01% |
| 2 | 0.595% | 188,236 | 50 | 0.61× | $81.54 | under 0.01% |
| 10 | 2.98% | 941,182 | 50 | 0.48× | $79.66 | under 0.01% |
| 35 | 10.4% | 3,294,138 | 50 | 0.40× | $78.46 | under 0.01% |

**4. Plus perfusion (the low-lactate example)** (no learning: $48.68)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.00298% | 613 | 1,450 | 0.99× | $48.58 | 0.05% |
| 0.1 | 0.0298% | 6,125 | 132 | 0.92× | $27.31 | 0.33% |
| 0.5 | 0.149% | 30,626 | 83 | 0.79× | $25.41 | 0.41% |
| 2 | 0.595% | 122,504 | 56 | 0.65× | $23.81 | 0.49% |
| 10 | 2.98% | 612,522 | 50 | 0.52× | $22.51 | 0.58% |
| 35 | 10.4% | 2,143,826 | 50 | 0.43× | $21.73 | 0.64% |

**7. Plus everything else at its favourable end (the all-favourable example)** (no learning: $6.97)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.00298% | 185 | 1,450 | 1.00× | $6.96 | 5.59% |
| 0.1 | 0.0298% | 1,855 | 1,450 | 0.97× | $6.92 | 5.63% |
| 0.5 | 0.149% | 9,273 | 1,450 | 0.89× | $6.80 | 5.74% |
| 2 | 0.595% | 37,090 | 1,450 | 0.77× | $6.62 | 5.93% |
| 10 | 2.98% | 185,452 | 1,450 | 0.62× | $6.40 | 6.17% |
| 35 | 10.4% | 649,080 | 138 | 0.52× | $6.25 | 6.33% |

"Share that cost would buy" is the main model's long-run share at that cost. Where it exceeds the share the volume is, the market grows;
where it is less, it shrinks. With both items at their floors the cells cost $76.83 (published cells), $20.49 (the low-lactate
example) and $6.25 (the all-favourable example). The all-favourable example's membrane column stays at $1,450: at 0.00004 m² of
process membrane a kilo (the low-lactate example uses 0.015) its demand never reaches the switch, and only the plant learns.

## 3. Where cost and share agree

| scenario | learning | the main model: cells, share | resting point from below: cells, share, Mt a year | from above: cells, share, Mt a year |
|---|---|---|---|---|
| Cautious | central | $181.13, under 0.01% | $181.10, under 0.01%, 0.001 | $181.10, under 0.01%, 0.001 |
| Cautious | no food-grade membrane supplier, slow plant learning | $181.13, under 0.01% | $181.12, under 0.01%, 0.001 | $181.12, under 0.01%, 0.001 |
| Cautious | slow learning | $181.13, under 0.01% | $181.12, under 0.01%, 0.001 | $181.12, under 0.01%, 0.001 |
| Cautious | fast learning | $181.13, under 0.01% | $181.08, under 0.01%, 0.001 | $84.91, under 0.01%, 0.02 |
| 4. Plus perfusion (the low-lactate example) | central | $48.68, 0.05% | $24.05, 0.48%, 1.61 | $24.05, 0.48%, 1.61 |
| 4. Plus perfusion (the low-lactate example) | no food-grade membrane supplier, slow plant learning | $48.68, 0.05% | $48.38, 0.05%, 0.16 | $48.38, 0.05%, 0.16 |
| 4. Plus perfusion (the low-lactate example) | slow learning | $48.68, 0.05% | $48.38, 0.05%, 0.16 | $30.30, 0.24%, 0.79 |
| 4. Plus perfusion (the low-lactate example) | fast learning | $48.68, 0.05% | $21.33, 0.67%, 2.25 | $21.33, 0.67%, 2.25 |
| 7. Plus everything else at its favourable end (the all-favourable example) | central | $6.97, 5.58% | $6.30, 6.27%, 21.07 | $6.30, 6.27%, 21.07 |
| 7. Plus everything else at its favourable end (the all-favourable example) | no food-grade membrane supplier, slow plant learning | $6.97, 5.58% | $6.74, 5.81%, 19.52 | $6.74, 5.81%, 19.52 |
| 7. Plus everything else at its favourable end (the all-favourable example) | slow learning | $6.97, 5.58% | $6.74, 5.81%, 19.52 | $6.74, 5.81%, 19.52 |
| 7. Plus everything else at its favourable end (the all-favourable example) | fast learning | $6.97, 5.58% | $6.25, 6.33%, 21.27 | $6.25, 6.33%, 21.27 |

"From below" starts with no learning; "from above" starts with everything at its floor. Where the two differ there are two resting
points, and reaching the upper one needs someone to carry the industry across the gap.

- **The all-favourable example's cells do not reach parity by this route: $6.30 against the $6.14 parity needs, and 6.27% of
  world meat** (5.58% without learning). They rest 5 cents above the cost with both items at their floors ($6.25); fast learning
  gives $6.25, and without plant learning they would stay near $6.97. With the all-favourable example's own demand (55% at equal
  price, 23.4% without learning; 24.7% before the fourth batch of 2026-11-21) they rest at the floors, $6.25, and take 25.8% of
  world meat (27.2% before). (2026-11-20, final pass, at
  $7.62: $6.77 and 6.28%; with its own demand $6.75 and 25.4%.) (After the engine batch, at
  $18.71: $9.78 and 4.28%. Before it: $6.95 and 6.89%.)
- **The low-lactate example: cells fall from $48.68 to $24.05 and the share rises from 0.05% to 0.48%**, about ten times. Its
  0.15 Mt a year needs 2.39 million m² of membrane, 2.4 times the switch at 1.0, so it crosses on its own sales and has one
  resting point. It would cross on its own with a switch up to about 2.4 million m², inside the switch's range (0.3–3).
- **With slow learning the low-lactate example has two resting points**: $48.38 and 0.05% left alone, $30.30 and 0.24% if
  pushed. A switch at 3 million m² is above the 2.39 million its sales need, so someone has to carry it across the gap. This
  has flipped four times. After the cut-cost repin: one point ($18.69 and 1.48%). After the audit batch, with its sales at
  0.26 Mt: two points ($32.48 and 0.08% left alone, $22.07 and 0.47% if pushed). With the heavier tail of liking: one ($21.74
  and 0.76%). Since the engine batch of 2026-11-20: two. The conclusion follows the low-lactate example's sales at its own cost,
  which its cost and the model's far tail decide. It is not robust.
- **Published cells never start on their own.** At $181.13 a kilo they sell 0.0003% of world meat, about a thousand tonnes a
  year, which needs 0.06 million m² of membrane. Left alone they stay within 10 cents of their own cost in every case. Only with
  fast learning and an outside push is there an upper resting point, at $84.91 and under 0.01% of world meat. With central
  learning there is no second resting point. With both items at their floors they would cost $76.83.
- **Without a food-grade membrane supplier little changes for the low-lactate example**: $48.38 and 0.05%. The all-favourable
  example, which does not need the supplier, gets $6.74 and 5.81% from slow plant learning.

## 4. The loop runs on ordinary cuts more than on premium products

| scenario | stage | cells, $/kg | sold, Mt a year: premium products, cuts, mince and processed | premium products' part of sales (without premium fillets and shrimp) | chicken (organic): price against it, share of it | pork (heritage): price against it, share of it | beef (prime/wagyu): price against it, share of it | seafood (premium fillet, shrimp): price against it, share of it | seafood (sushi): price against it, share of it |
|---|---|---|---|---|---|---|---|---|---|
| Cautious | no learning | $181.13 | under 0.001, 0.001, under 0.001 | almost nothing is sold | 16.00×, under 0.01% | 13.00×, under 0.01% | 4.62×, under 0.01% | 10.40×, under 0.01% | 5.94×, under 0.01% |
| Cautious | resting point | $181.10 | under 0.001, 0.001, under 0.001 | almost nothing is sold | 16.00×, under 0.01% | 13.00×, under 0.01% | 4.62×, under 0.01% | 10.40×, under 0.01% | 5.94×, under 0.01% |
| 4. Plus perfusion (the low-lactate example) | no learning | $48.68 | 0.04, 0.09, 0.02 | 28% (14%) | 4.69×, 0.06% | 3.81×, 0.10% | 1.35×, 2.08% | 3.05×, 0.16% | 1.74×, 0.71% |
| 4. Plus perfusion (the low-lactate example) | resting point | $24.05 | 0.47, 0.94, 0.20 | 29% (16%) | 2.58×, 0.57% | 2.10×, 0.93% | 0.75×, 24.98% | 1.68×, 1.62% | 0.96×, 8.56% |
| 7. Plus everything else at its favourable end (the all-favourable example) | no learning | $6.97 | 3.02, 10.13, 5.60 | 16% (6%) | 1.14×, 6.29% | 0.93×, 9.52% | 0.33×, 72.07% | 0.74×, 14.80% | 0.42×, 45.08% |
| 7. Plus everything else at its favourable end (the all-favourable example) | resting point | $6.30 | 3.22, 11.21, 6.64 | 15% (5%) | 1.09×, 6.98% | 0.88×, 10.46% | 0.31×, 73.43% | 0.71×, 16.06% | 0.40×, 47.03% |

| scenario | learning | sold at the scenario's own cost, Mt a year: premium products, premium products without premium fillets and shrimp, everything | membrane each needs, million m² a year | the switch, million m² a year | which of the three cross it alone? |
|---|---|---|---|---|---|
| Cautious | central | under 0.001, under 0.001, 0.001 | 0.02, 0.01, 0.06 | 1.0 | no, no, no |
| Cautious | no food-grade membrane supplier, slow plant learning | under 0.001, under 0.001, 0.001 | 0.02, 0.01, 0.06 | never | no, no, no |
| Cautious | slow learning | under 0.001, under 0.001, 0.001 | 0.02, 0.01, 0.06 | 3.0 | no, no, no |
| Cautious | fast learning | under 0.001, under 0.001, 0.001 | 0.02, 0.01, 0.06 | 0.3 | no, no, no |
| 4. Plus perfusion (the low-lactate example) | central | 0.04, 0.02, 0.15 | 0.68, 0.34, 2.39 | 1.0 | no, no, yes |
| 4. Plus perfusion (the low-lactate example) | no food-grade membrane supplier, slow plant learning | 0.04, 0.02, 0.15 | 0.68, 0.34, 2.39 | never | no, no, no |
| 4. Plus perfusion (the low-lactate example) | slow learning | 0.04, 0.02, 0.15 | 0.68, 0.34, 2.39 | 3.0 | no, no, no |
| 4. Plus perfusion (the low-lactate example) | fast learning | 0.04, 0.02, 0.15 | 0.68, 0.34, 2.39 | 0.3 | yes, yes, yes |
| 7. Plus everything else at its favourable end (the all-favourable example) | central | 3.02, 1.06, 18.75 | 0.12, 0.04, 0.72 | 1.0 | no, no, no |
| 7. Plus everything else at its favourable end (the all-favourable example) | no food-grade membrane supplier, slow plant learning | 3.02, 1.06, 18.75 | 0.12, 0.04, 0.72 | never | no, no, no |
| 7. Plus everything else at its favourable end (the all-favourable example) | slow learning | 3.02, 1.06, 18.75 | 0.12, 0.04, 0.72 | 3.0 | no, no, no |
| 7. Plus everything else at its favourable end (the all-favourable example) | fast learning | 3.02, 1.06, 18.75 | 0.12, 0.04, 0.72 | 0.3 | no, no, yes |

**Which products count as premium (decided 2026-11-19).** Premium products are the rows the model labels premium: a cut priced at
2.5 times its species' cheapest form or more. When world seafood was re-priced by consumption the single fillet row ($16) was split
into whole fish and ordinary fillets ($7) and premium fillets and shrimp ($20: salmon, shrimp, cod, tuna loins). The new premium
row is premium by the model's rule, so it joins organic chicken, heritage pork, prime or wagyu beef and sushi-grade seafood in the
list and in the response table of section 6. It is a market of about 13 Mt a year, five times the other four together (2.6 Mt).
So the tables give every count twice: with it, and for the four small premium markets alone.

- **Premium products are where cultivated meat is closest to the price it competes with**: at the low-lactate example's cost
  it is 1.35 times prime or wagyu beef's price and 1.74 times sushi-grade seafood's. Those two markets are small
  (`premium_market_sizes.md`: about 0.5 Mt and 1.2 Mt a year). Against premium fillets and shrimp it is 3.05 times the price.
- **Most of the low-lactate example's first sales are ordinary cuts.** Of 0.15 Mt a year at its own cost, 0.09 Mt are cuts
  (62%): beef steaks about a third of all its sales (31%) at 2.99 times their price, then pork cuts, chicken cuts and sheep and goat at
  four to eight times theirs. Premium products are 0.04 Mt (28%): premium fillets and shrimp about half of that,
  prime beef and sushi-grade seafood most of the rest. Without premium fillets and shrimp the four small premium markets are 14%
  of sales. Mince and processed meat are 0.015 Mt (10%). Two-fifths of these first sales (41%) are of products at more than four
  times their meat's price. Nothing measures demand that far out (`liking_spread.md` §6).
- A cut still costs less to make than mince whenever cells cost more than about $12 a kilo, as the low-lactate example's do: a
  cut is 0.8 kg of cells, a plant-protein matrix and $2 of assembly beyond what mince pays (`structuring_cost.md`).
  The buyers are the upper end of the spread of liking (`liking_spread.md`), not buyers of organic meat, who are the most hostile
  to it (`demand_heterogeneity_evidence.md`).
- **Premium products alone do not reach the switch.** The five need 0.68 million m² of membrane a year, a third short of
  the switch at 1.0. The four small markets alone need 0.34 million. All of the low-lactate example's sales need 2.39 million. So
  the premium start is neither enough nor needed at the central switch: without any premium product the other sales need 1.72
  million m², past a switch at 1.0 but short of one at 3 million. The all-favourable example needs 0.72 million m² for all its
  18.8 Mt a year (0.79 million for 20.4 Mt before the fourth batch of 2026-11-21; 0.48 million for 18.3 Mt before 2026-11-21: its denser, thinned-design tank sends more permeate a kilo), and
  does not cross the central switch at all.
- **The unlocking is large once the membrane is cheap.** At $24.05 a kilo of cells cultivated meat costs 0.75 times prime beef,
  0.96 times sushi-grade seafood and 1.68 times premium fillets and shrimp. Its share of prime beef rises from 2.08% to 25.0%, of
  sushi-grade seafood from 0.71% to 8.56%, and of premium fillets and shrimp from 0.16% to 1.62%. These rises are steeper than
  farmed salmon's history supports (section 6).
- **The loop reaches prime beef and sushi-grade fish; the rest stays above its meat's price.** At the low-lactate example's
  resting point organic chicken is 2.58 times, heritage pork 2.10 times and premium fillets 1.68 times their price. Of its 1.61
  Mt a year, 0.94 Mt are cuts, 0.47 Mt premium products and 0.20 Mt mince and processed meat, for 0.48% of world meat. Only the
  all-favourable example's cells take the loop far into mince and processed meat (6.64 Mt a year at their resting point).

## 5. How strong is the loop, and how well is that known?

| scenario | its own cost and share | first pass: the learning its own volume brings | resting point | part of the share gain from later rounds | resting point with demand anchored on premium meats (its own share there) |
|---|---|---|---|---|---|
| 4. Plus perfusion (the low-lactate example) | $48.68, 0.05% | $26.83, 0.35% | $24.05, 0.48% | 31% | $48.25, 0.02% (0.01%) |
| 7. Plus everything else at its favourable end (the all-favourable example) | $6.97, 5.58% | $6.32, 6.25% | $6.30, 6.27% | 2% | $6.42, 2.53% (2.33%) |

| input, across its range | 4. Plus perfusion (the low-lactate example): cells, share | 7. Plus everything else at its favourable end (the all-favourable example): cells, share |
|---|---|---|
| Membrane demand at which a food-grade supplier appears (300000 to 3e+06 m2 a year) | $23.88 to $47.66, 0.49% to 0.05% | $6.30 to $6.30, 6.27% to 6.27% |
| That supplier's first price (60 to 400 $/m2) | $23.88 to $25.96, 0.49% to 0.38% | $6.30 to $6.30, 6.27% to 6.27% |
| Membrane's price fall per doubling (0.1 to 0.28 per doubling) | $24.63 to $23.88, 0.45% to 0.49% | $6.30 to $6.30, 6.27% to 6.27% |
| Membrane's price floor (20 to 120 $/m2) | $24.05 to $25.10, 0.48% to 0.42% | $6.30 to $6.30, 6.27% to 6.27% |
| Plant's cost fall per doubling (0.03 to 0.18 per doubling) | $26.11 to $21.97, 0.38% to 0.62% | $6.74 to $6.25, 5.81% to 6.33% |
| Animal-cell tanks installed today (6500 to 11800 m3) | $23.85 to $24.43, 0.49% to 0.46% | $6.28 to $6.35, 6.30% to 6.22% |
| World meat, boneless (300 to 384 Mt a year) | $24.20 to $23.88, 0.47% to 0.49% | $6.32 to $6.29, 6.25% to 6.29% |

- **It is mostly one step, not a loop.** 69% of the low-lactate example's gain in share comes on the first pass: the 0.15 Mt
  it already sells crosses the membrane switch, cells fall to $26.83 and the share rises to 0.35%. Later rounds, where cheaper
  cells sell more and more sales make cells cheaper again, add the other 31% (to $24.05 and 0.48%). For the all-favourable
  example's cells the first pass gives 98%. (2026-11-20, final pass: 68%, $27.87, 0.34%, then $24.95 and 0.48%; 97%.) (After the engine batch later rounds gave 32% and 10%; before it 24% and 5%; after the
  audit batch, with the normal spread, 35% of the low-lactate example's gain; before it, 19%.) So the result rests mostly on
  whether one event happens, a food-grade membrane supplier, and at what price, and for a third on the strength of a feedback
  that cannot be measured.
- **The switch's level matters most, then the plant's learning rate, the food-grade supplier's first price and the membrane's
  floor**; the speed of the membrane's later fall matters little (table above). A 3 million m² switch is above the 2.39 million
  m² the low-lactate example's sales need, so it leaves it at $47.66 and 0.05%; a switch anywhere up to about 2.4 million gives
  about $24. Before the engine batch of 2026-11-20 a 3 million m² switch cost it 21 cents.
- **The all-favourable example's cells are sturdy on cost**: $6.25–6.74 across every input; only the plant's learning rate moves
  them.
- **The share side is weaker than the cost side.** With the share taken from the single curve fitted to premium real meats
  (`premium_curve.md`) in place of the model's, the low-lactate example does not cross the switch: at its own cost the fitted curve gives 0.015% of
  world meat, a third of the model's 0.045%, and those sales need about 0.76 million m², a quarter short of the central switch,
  so it rests at $48.25 and 0.015%, not $24.05 and 0.48%. The all-favourable example's cells cost about the same ($6.42) and take
  2.53%, not 6.27%. So whether the low-lactate example crosses at all depends on which demand side is right, and on the fitted
  curve it does not. (In the third batch of 2026-11-21 its sales on the fitted curve needed about 1.0 million m², the central
  switch itself, and it rested at $24.69 and 0.27%; the fourth batch's demand changes moved it below the switch.)

## 6. The checks (2026-11-18)

**How big are the premium markets?** Several times smaller than the model's tables had them (`premium_market_sizes.md`): sushi-grade
seafood about 1.2 Mt a year (the table had 5.4) and prime or wagyu beef about 0.5 Mt (1.35). The tables were corrected. Since the
seafood re-pricing of 2026-11-19 the model also has premium fillets and shrimp, about 13 Mt a year at $20 a kilo
(`world_seafood_prices.md`). The four small premium markets alone do not carry the low-lactate example past the switch (0.34
million m² against 1.0); nor do the premium products with premium fillets and shrimp (0.68 million m²); ordinary cuts carry it
(section 4).

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

Judgement: $150 a m² at a million m² a year (80% range 60–400; about 70% that it is $250 or less), and a floor of about $50 (20–120). These are a rough judgement made while building the model with an AI assistant; not measured and not reviewed by an expert; their reasoning is the neighbours' prices above.

**Can a hollow fibre hold a quarter cells by volume for a month?** Partly shown, at bench scale only.
- Clincke et al. 2013 (FT): CHO cells on a 0.2 µm hollow fibre in a 4 L tank reached 2.1 × 10⁸ cells a ml and held 0.9–1.3 × 10⁸ (about
  27–35% cells by volume, from their cell diameters) for over two weeks; one fibre ran 30 days. The limits were viscosity and
  pressure, not fouling.
- Yeast cell-recycle fermentation on hollow fibres ran routinely at 100–150 g of dry cells a litre (Lee & Chang 1987, ABS), but food
  uses at high solids clean after hours to days (brewery yeast on ceramic, Brauwelt, FT).
- Nothing was found above bench scale for a month. Judgement: about 50–60% that one module holds it for a month at industrial size, about
  75% with a mid-run backflush or a standby module (a rough judgement made while building the model with an AI assistant; not measured and not reviewed by an expert; from the bench results above and the short cleaning intervals of food
  uses).

**How much does a price cut unlock?** The model against history (percent more volume per percent lower price):

| premium product | price against it: at $48.68 a kilo of cells, at $24.05 | cultivated meat's share of it | percent more share per percent lower price |
|---|---|---|---|
| chicken (organic) | 4.69×, 2.58× | 0.06%, 0.57% | 3.7 |
| pork (heritage) | 3.81×, 2.10× | 0.10%, 0.93% | 3.8 |
| beef (prime/wagyu) | 1.35×, 0.75× | 2.08%, 24.98% | 4.2 |
| seafood (premium fillet, shrimp) | 3.05×, 1.68× | 0.16%, 1.62% | 3.9 |
| seafood (sushi) | 1.74×, 0.96× | 0.71%, 8.56% | 4.2 |
| history, along the demand curve (farmed salmon while still a premium product) | | | 1–1.5 |
| history, in total, with demand growth mixed in (salmon, US broilers, US catfish) | | | 1.3–4.1 |

- Farmed salmon is the closest case: 13 kt in 1980 to over 1 Mt in 1999 while its real price fell to a third (Asche, Bjørndal & Young
  2001, FT; Bjørndal & Tusvik 2017, FT). Early growth was largely "a move down along the demand schedule"; since 2000 nearly all growth
  has been demand shifting at flat prices. US broilers: real price −67% and consumption per person up fourfold, 1955–87 (Bishop &
  Christensen, USDA 1989, FT).
- **The model's premium products respond to price more strongly than farmed salmon did along its demand curve. This check
  fails.** All five respond at 3.7–4.2. That is about two and a half to three times the top of salmon's range along the curve
  (1–1.5). Organic chicken, heritage pork and premium fillets and shrimp (3.7–3.9) are inside history's totals, where demand
  growth is mixed in (1.3–4.1); prime beef and sushi-grade seafood (4.2 each) are just above them. After the engine batch of
  2026-11-20 the five gave 3.8–4.3; before it 2.7–3.7, all inside the totals. The responses rose with the engine batch because
  dearer cells put every product further from its meat's price: prime beef starts at 1.35 times its price with 2.1% of its
  market, where before it started below its price with 13%, and a share that small has more room to rise for each percent off.
  With the normal spread of the audit batch the dearer three gave 5.2–7.5. Before the audit batch the four products then listed
  gave 0.6–1.5.
- **Why it changed.** Until the audit batch the tier rule made buyers of cuts and premium products less sensitive to price; the
  audit removed it (`audit_2026-11-19.md`, D3). What was left was the normal spread's tail, which thins very fast at two to three
  times a meat's price. The Student's t spread fitted later the same day has a heavier tail: more buyers at a high price to begin
  with, so fewer are added by each percent off (`liking_spread.md`). Its fit counts this check as one of three, and the best joint fit still leaves it
  outside the range.
- **What it means for the loop.** Between the low-lactate example's own cost and its resting point shop prices fall by about
  48% and its sales rise about ten times, a response of about 3.6 overall. At the top of salmon's range along the curve (1.5) the
  same fall in price would multiply its sales by about two and a half (to about 0.12% of world meat); at the top of history's
  totals (4.1) it would give about fifteen times. With the demand anchored on premium real meats there is no fall in price: it
  does not cross the switch (section 5). Salmon was
  measured as a product that already held part of its market at a modest premium, so the comparison is not exact. But the size
  of the low-lactate example's gain rests on a response at the very top of what history shows, and is more likely too large
  than too small.

**How fast?** The model has no time in it. History, given success: a hundred-fold growth took farmed salmon about 18 years (29% a
year), US corn ethanol about 29 years for 76-fold (with a mandate), US broilers 45–50 years; Quorn has not done it in 40. A fair range
is 15–30 years, with something like a one-in-three chance of stalling as Quorn and plant-based meat did (the last is a rough judgement made while building the model with an AI assistant; not measured and not reviewed by an expert; from the two stalls among the four cases).

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

- **The switch is a judgement** (about 65% that a food-grade supplier appears once demand passes 1 million m² a year; a rough judgement made while building the model with an AI assistant; not measured and not reviewed by an expert;
  from the neighbouring markets of section 6, which already sell food and water membranes at that scale). Without it little moves.
- **Four changes in three days moved the low-lactate example's first sales, and the conclusions with them.** The audit batch of
  2026-11-19 (cells dearer, $26.43 to $32.80; seafood re-priced; the tier rule replaced) cut its sales at its own cost from
  1.78 to 0.26 Mt a year and its margin over the switch from ten times to 2.3. The Student's t spread of liking and the
  restructure of the scenarios then raised them to 0.71 Mt and 6.2 times. The engine batch of 2026-11-20 (cells at $49.96, a
  shorter membrane life) cut them to 0.15 Mt and 2.5 times; the final pass (cells at $49.50, the demand anchor and nominal
  incomes, conventional meat's price falling with the share) left them at 0.16 Mt and 2.4 times, and the batches of 2026-11-21 at 0.15 Mt and 2.4 times. Its resting point went from
  $15.05 and 2.49% to $17.75 and 0.98%, then $17.50 and 1.34%, $24.00 and 0.57%, $24.95 and 0.48%, $23.91 and 0.54%, and now
  $24.05 and 0.48%.
- **The far tail of liking.** Two-fifths of the low-lactate example's first sales are of products at more than four times
  their meat's price, where the spread of liking is an extrapolation. Without them its sales would need about 1.4 million m²:
  past the central switch, short of one at 3 million.
- **The low-lactate example's cost is itself uncertain.** Across draws its cells cost $39–76 a kilo (8 in 10), with a median of
  $52, above the $48.68 at most likely values. At $52 its sales need about 1.9 million m² of membrane, 1.9 times the switch;
  above about $62, between the median and the 90th percentile of the draws, they fall short of it; at $76 they need about 0.5
  million.
- **The cut cost.** Since 2026-11-19 a cut costs 0.8 kg of cells, a $2 plant-protein matrix and $2 of assembly beyond what
  mince pays (`structuring_cost.md`). With the old rule (a full kilo of cells and a $6 scaffold) the low-lactate example rested
  at $15.83 and 0.86% at the costs of that morning.
- **Still unknown:** an actual quote for a steam-tolerant food-grade module; a month-long run of animal cells at a quarter by volume
  above bench scale; the yearly area of perfusion filters sold today (estimated, not published); retail prices of the premium
  products by grade.
- **Resting points, not a path.** Learning is counted on yearly scale, not cumulative output, and nothing says who pays for the early
  years.
- **What would have to be true.** For the all-favourable example's cells to reach $6.14 (price parity) by learning: the plant
  would have to learn faster than the fast case (which gives $6.25, the floors), since the membrane plays no part in them. For
  the low-lactate example's sales to pass the switch with no outside push: its cells must cost under about $62 and the switch
  sit under about 2.4 million m², on the model's demand; on the curve fitted to premium real meats its sales fall short of the
  switch (0.76 million m²). For learning to take the low-lactate example above 1% of world meat: no learning case does at its point cost (the
  middle case rests at 0.48%, fast learning at 0.67%; slow learning 0.05% unaided, no supplier 0.05%, the demand anchored on
  premium meats 0.015%), and the response to price behind these gains is already at the top of what history shows.

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
