# Does cultivated meat get cheaper as it sells more? Cost and share solved together

> **Current figures (2026-11-22, fifth batch).** The shopper model now has price-insensitive shoppers (8% of shoppers responding
> 0.11 times as strongly to every price; `demand_checks.md` section 7). They buy most of what sells far above meat's price, so the
> low-lactate example sells far more at its own cost (0.26% of world meat, 0.87 Mt a year, against 0.045%) and **crosses the
> membrane switch by a wide margin** (13.6 times its area); it rests at $23.52 and 0.79%. **Three conclusions changed.** With slow
> learning it now crosses on its own and has one resting point ($29.43 and 0.54%), not two. The switch's level no longer matters
> (across its range $23.49–23.85); the plant's learning rate matters most. And **published cells now cross the switch on their own
> sales** (0.036 Mt a year, 2.4 million m²): they rest at $84.88 and 0.09%, from $181.13 and 0.011%. The all-favourable example's
> cells rest at $6.30 and 6.14% (from $6.97 and 5.48%). The premium products' response to a falling price is 1.5–4.3 (3.7–4.2
> before). Sections below are rewritten; figures marked "before" are those of the fourth batch.

> **Figures of 2026-11-21 (fourth batch; tables regenerated, prose recomputed on 2026-11-22), now history.** Plant-based
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

**In short (2026-11-22, fifth batch).** At its point cost the low-lactate example sells enough to bring a food-grade membrane
supplier into being many times over, and gets much cheaper for it: its cells fall from $48.68 to $23.52 and its share rises from
0.26% to 0.79% of world meat. The all-favourable example's cells barely use the process membrane (they are kept with haemodialyser
fibres at $8 a m²), so the switch plays no part for them: the plant's learning alone takes them from $6.97 to $6.30 and from 5.48%
to 6.14%, short of the $6.14 that price parity with US minced beef or pork cuts ($12 a kilo) needs. Published cells cross too:
$181.13 to $84.88, 0.011% to 0.09%. (Fourth batch of 2026-11-21: the low-lactate example $24.05 and 0.48% from 0.05%; the
all-favourable example $6.30 and 6.27% from 5.58%; published cells never started.)

- **The low-lactate example's margin over the switch is wide.** Its first sales need 13.6 times the switch's membrane area (2.4
  times before). It crosses with slow learning too (one resting point, $29.43 and 0.54%), and without a food-grade supplier the
  plant's learning alone takes it to $47.92 and 0.27%. With the demand anchored on premium real meats it does not cross the switch
  at all (section 5).
- **Premium products alone just reach the switch** (1.10 million m² against 1.0); the four small premium markets alone do not
  (0.33 million). Ordinary cuts and mince carry it.
- **Where the switch sits no longer matters** for the low-lactate example ($23.49 to $23.85 across its range); the plant's learning
  rate matters most ($21.48 to $25.77).
- **The demand behind this rests on the price-insensitive shoppers.** 97% of the low-lactate example's sales at its own cost go to
  them, and 79% of its first sales are of products at more than four times their meat's price. How much those shoppers like
  cultivated meat is read from two stated-choice studies (`demand_checks.md` section 7).

About an eighth of the low-lactate example's gain is a loop, the rest one step. Between its own cost and its resting point its shop
price falls by half and its sales triple: a response of 1.6, near the top of farmed salmon's range along its demand curve (1–1.5);
the premium products respond at 1.5–2.4 for the three dearest and 4.0–4.3 for prime beef and sushi-grade seafood (section 6).

Premium products are about a twelfth of the low-lactate example's first sales, cuts most of them (57%), mince and processed meat a
third. Here "the all-favourable example" is its cells with the model's ordinary demand (14.4% of meat buyers at equal price), not its
own 55%.

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
| 0.01 | 0.00298% | 941 | 1,450 | 0.98× | $180.89 | 0.01% |
| 0.1 | 0.0298% | 9,412 | 87 | 0.89× | $87.95 | 0.09% |
| 0.5 | 0.149% | 47,059 | 55 | 0.75× | $83.74 | 0.10% |
| 2 | 0.595% | 188,236 | 50 | 0.61× | $81.54 | 0.10% |
| 10 | 2.98% | 941,182 | 50 | 0.48× | $79.66 | 0.11% |
| 35 | 10.4% | 3,294,138 | 50 | 0.40× | $78.46 | 0.11% |

**4. Plus perfusion (the low-lactate example)** (no learning: $48.68)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.00298% | 613 | 1,450 | 0.99× | $48.58 | 0.26% |
| 0.1 | 0.0298% | 6,125 | 132 | 0.92× | $27.31 | 0.61% |
| 0.5 | 0.149% | 30,626 | 83 | 0.79× | $25.41 | 0.69% |
| 2 | 0.595% | 122,504 | 56 | 0.65× | $23.81 | 0.77% |
| 10 | 2.98% | 612,522 | 50 | 0.52× | $22.51 | 0.85% |
| 35 | 10.4% | 2,143,826 | 50 | 0.43× | $21.73 | 0.90% |

**7. Plus everything else at its favourable end (the all-favourable example)** (no learning: $6.97)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.00298% | 185 | 1,450 | 1.00× | $6.96 | 5.48% |
| 0.1 | 0.0298% | 1,855 | 1,450 | 0.97× | $6.92 | 5.52% |
| 0.5 | 0.149% | 9,273 | 1,450 | 0.89× | $6.80 | 5.63% |
| 2 | 0.595% | 37,090 | 1,450 | 0.77× | $6.62 | 5.81% |
| 10 | 2.98% | 185,452 | 1,450 | 0.62× | $6.40 | 6.04% |
| 35 | 10.4% | 649,080 | 138 | 0.52× | $6.25 | 6.20% |

"Share that cost would buy" is the main model's long-run share at that cost. Where it exceeds the share the volume is, the market grows;
where it is less, it shrinks. With both items at their floors the cells cost $76.83 (published cells), $20.49 (the low-lactate
example) and $6.25 (the all-favourable example). The all-favourable example's membrane column stays at $1,450: at 0.00004 m² of
process membrane a kilo (the low-lactate example uses 0.015) its demand never reaches the switch, and only the plant learns.

## 3. Where cost and share agree

| scenario | learning | the main model: cells, share | resting point from below: cells, share, Mt a year | from above: cells, share, Mt a year |
|---|---|---|---|---|
| Cautious | central | $181.13, 0.01% | $84.88, 0.09%, 0.32 | $84.88, 0.09%, 0.32 |
| Cautious | no food-grade membrane supplier, slow plant learning | $181.13, 0.01% | $180.91, 0.01%, 0.04 | $180.91, 0.01%, 0.04 |
| Cautious | slow learning | $181.13, 0.01% | $180.91, 0.01%, 0.04 | $104.48, 0.06%, 0.19 |
| Cautious | fast learning | $181.13, 0.01% | $79.61, 0.11%, 0.36 | $79.61, 0.11%, 0.36 |
| 4. Plus perfusion (the low-lactate example) | central | $48.68, 0.26% | $23.52, 0.79%, 2.64 | $23.52, 0.79%, 2.64 |
| 4. Plus perfusion (the low-lactate example) | no food-grade membrane supplier, slow plant learning | $48.68, 0.26% | $47.92, 0.27%, 0.89 | $47.92, 0.27%, 0.89 |
| 4. Plus perfusion (the low-lactate example) | slow learning | $48.68, 0.26% | $29.43, 0.54%, 1.83 | $29.43, 0.54%, 1.83 |
| 4. Plus perfusion (the low-lactate example) | fast learning | $48.68, 0.26% | $20.97, 0.96%, 3.22 | $20.97, 0.96%, 3.22 |
| 7. Plus everything else at its favourable end (the all-favourable example) | central | $6.97, 5.48% | $6.30, 6.14%, 20.62 | $6.30, 6.14%, 20.62 |
| 7. Plus everything else at its favourable end (the all-favourable example) | no food-grade membrane supplier, slow plant learning | $6.97, 5.48% | $6.74, 5.70%, 19.14 | $6.74, 5.70%, 19.14 |
| 7. Plus everything else at its favourable end (the all-favourable example) | slow learning | $6.97, 5.48% | $6.74, 5.70%, 19.14 | $6.74, 5.70%, 19.14 |
| 7. Plus everything else at its favourable end (the all-favourable example) | fast learning | $6.97, 5.48% | $6.25, 6.20%, 20.82 | $6.25, 6.20%, 20.82 |

"From below" starts with no learning; "from above" starts with everything at its floor. Where the two differ there are two resting
points, and reaching the upper one needs someone to carry the industry across the gap.

- **The all-favourable example's cells do not reach parity by this route: $6.30 against the $6.14 parity needs, and 6.14% of
  world meat** (5.48% without learning). They rest 5 cents above the cost with both items at their floors ($6.25); fast learning
  gives $6.25, and without plant learning they would stay near $6.97. With the all-favourable example's own demand (55% at equal
  price, 25.1% without learning) they rest at the floors, $6.25, and take 27.5% of world meat. (Fourth batch of 2026-11-21: $6.30
  and 6.27%; with its own demand 23.4% and 25.8%.)
- **The low-lactate example: cells fall from $48.68 to $23.52 and the share rises from 0.26% to 0.79%**, about three times. Its
  0.87 Mt a year needs 13.6 million m² of membrane, 13.6 times the switch at 1.0, so it crosses on its own sales and has one
  resting point. (Fourth batch: $24.05 and 0.48% from 0.045%, on 0.15 Mt and 2.4 times the switch.)
- **With slow learning it has one resting point too**, $29.43 and 0.54%: a switch at 3 million m² is far below the 13.6 million
  its sales need. This has flipped five times: one point after the cut-cost repin, two after the audit batch, one with the heavier
  tail of liking, two from the engine batch of 2026-11-20 to the fourth batch ($48.38 and 0.05% left alone, $30.30 and 0.24% if
  pushed), and one since the price-insensitive shoppers. The conclusion follows the low-lactate example's sales at its own cost,
  which its cost and the demand far above meat's price decide.
- **Published cells now start on their own.** At $181.13 a kilo they sell 0.011% of world meat, about 36,000 tonnes a year, which
  needs 2.4 million m² of membrane: past the central switch. With central learning they rest at $84.88 and 0.09%; with fast
  learning at $79.61 and 0.11%. With slow learning (a 3 million m² switch) they stay at $180.91 left alone and reach $104.48 and
  0.06% only if pushed; without a food-grade supplier they stay at $180.91. With both items at their floors they would cost $76.83.
  (Before the price-insensitive shoppers they sold about a thousand tonnes and never started.)
- **Without a food-grade membrane supplier the plant's learning still moves the low-lactate example**: $47.92 and 0.27%. The
  all-favourable example, which does not need the supplier, gets $6.74 and 5.70% from slow plant learning.

## 4. The loop runs on ordinary cuts more than on premium products

| scenario | stage | cells, $/kg | sold, Mt a year: premium products, cuts, mince and processed | premium products' part of sales (without premium fillets and shrimp) | chicken (organic): price against it, share of it | pork (heritage): price against it, share of it | beef (prime/wagyu): price against it, share of it | seafood (premium fillet, shrimp): price against it, share of it | seafood (sushi): price against it, share of it |
|---|---|---|---|---|---|---|---|---|---|
| Cautious | no learning | $181.13 | 0.006, 0.03, 0.005 | 16% (4%) | 16.01×, 0.02% | 13.00×, 0.02% | 4.62×, 0.10% | 10.40×, 0.03% | 5.94×, 0.06% |
| Cautious | resting point | $84.88 | 0.03, 0.20, 0.08 | 10% (2%) | 7.78×, 0.12% | 6.32×, 0.15% | 2.25×, 0.43% | 5.06×, 0.18% | 2.89×, 0.27% |
| 4. Plus perfusion (the low-lactate example) | no learning | $48.68 | 0.07, 0.49, 0.31 | 8% (2%) | 4.69×, 0.27% | 3.81×, 0.32% | 1.35×, 1.72% | 3.05×, 0.37% | 1.74×, 0.71% |
| 4. Plus perfusion (the low-lactate example) | resting point | $23.52 | 0.45, 1.37, 0.82 | 17% (9%) | 2.54×, 0.69% | 2.06×, 0.98% | 0.73×, 23.67% | 1.65×, 1.56% | 0.94×, 8.17% |
| 7. Plus everything else at its favourable end (the all-favourable example) | no learning | $6.97 | 2.83, 9.69, 5.89 | 15% (5%) | 1.14×, 5.90% | 0.93×, 9.02% | 0.33×, 65.71% | 0.74×, 14.04% | 0.42×, 41.57% |
| 7. Plus everything else at its favourable end (the all-favourable example) | resting point | $6.30 | 3.03, 10.70, 6.89 | 15% (5%) | 1.09×, 6.57% | 0.88×, 9.93% | 0.31×, 67.00% | 0.71×, 15.25% | 0.40×, 43.33% |

| scenario | learning | sold at the scenario's own cost, Mt a year: premium products, premium products without premium fillets and shrimp, everything | membrane each needs, million m² a year | the switch, million m² a year | which of the three cross it alone? |
|---|---|---|---|---|---|
| Cautious | central | 0.006, 0.002, 0.04 | 0.39, 0.10, 2.38 | 1.0 | no, no, yes |
| Cautious | no food-grade membrane supplier, slow plant learning | 0.006, 0.002, 0.04 | 0.39, 0.10, 2.38 | never | no, no, no |
| Cautious | slow learning | 0.006, 0.002, 0.04 | 0.39, 0.10, 2.38 | 3.0 | no, no, no |
| Cautious | fast learning | 0.006, 0.002, 0.04 | 0.39, 0.10, 2.38 | 0.3 | yes, no, yes |
| 4. Plus perfusion (the low-lactate example) | central | 0.07, 0.02, 0.87 | 1.10, 0.33, 13.62 | 1.0 | yes, no, yes |
| 4. Plus perfusion (the low-lactate example) | no food-grade membrane supplier, slow plant learning | 0.07, 0.02, 0.87 | 1.10, 0.33, 13.62 | never | no, no, no |
| 4. Plus perfusion (the low-lactate example) | slow learning | 0.07, 0.02, 0.87 | 1.10, 0.33, 13.62 | 3.0 | no, no, yes |
| 4. Plus perfusion (the low-lactate example) | fast learning | 0.07, 0.02, 0.87 | 1.10, 0.33, 13.62 | 0.3 | yes, yes, yes |
| 7. Plus everything else at its favourable end (the all-favourable example) | central | 2.83, 0.98, 18.41 | 0.11, 0.04, 0.71 | 1.0 | no, no, no |
| 7. Plus everything else at its favourable end (the all-favourable example) | no food-grade membrane supplier, slow plant learning | 2.83, 0.98, 18.41 | 0.11, 0.04, 0.71 | never | no, no, no |
| 7. Plus everything else at its favourable end (the all-favourable example) | slow learning | 2.83, 0.98, 18.41 | 0.11, 0.04, 0.71 | 3.0 | no, no, no |
| 7. Plus everything else at its favourable end (the all-favourable example) | fast learning | 2.83, 0.98, 18.41 | 0.11, 0.04, 0.71 | 0.3 | no, no, yes |

**Which products count as premium (decided 2026-11-19).** Premium products are the rows the model labels premium: a cut priced at
2.5 times its species' cheapest form or more. When world seafood was re-priced by consumption the single fillet row ($16) was split
into whole fish and ordinary fillets ($7) and premium fillets and shrimp ($20: salmon, shrimp, cod, tuna loins). The new premium
row is premium by the model's rule, so it joins organic chicken, heritage pork, prime or wagyu beef and sushi-grade seafood in the
list and in the response table of section 6. It is a market of about 13 Mt a year, five times the other four together (2.6 Mt).
So the tables give every count twice: with it, and for the four small premium markets alone.

- **Premium products are where cultivated meat is closest to the price it competes with**: at the low-lactate example's cost
  it is 1.35 times prime or wagyu beef's price and 1.74 times sushi-grade seafood's. Those two markets are small
  (`premium_market_sizes.md`: about 0.5 Mt and 1.2 Mt a year). Against premium fillets and shrimp it is 3.05 times the price.
- **Most of the low-lactate example's first sales are ordinary cuts and mince.** Of 0.87 Mt a year at its own cost, 0.49 Mt are
  cuts (57%): beef steaks 14% of all its sales at 2.99 times their price, pork cuts 13% and chicken cuts 13% at seven to eight
  times theirs. Mince and processed meat are 0.31 Mt (35%), mostly at six to fourteen times their price. Premium products are 0.07
  Mt (8%): premium fillets and shrimp most of it. Without premium fillets and shrimp the four small premium markets are 2.4% of
  sales. 79% of these first sales are of products at more than four times their meat's price (two-fifths before the
  price-insensitive shoppers). Nothing measures demand that far out (`liking_spread.md` §6), and 97% of the sales go to the
  price-insensitive shoppers.
- A cut still costs less to make than mince whenever cells cost more than about $12 a kilo, as the low-lactate example's do: a
  cut is 0.8 kg of cells, a plant-protein matrix and $2 of assembly beyond what mince pays (`structuring_cost.md`).
  The buyers are the price-insensitive shoppers (`demand_checks.md` section 7) and the upper end of the spread of liking
  (`liking_spread.md`), not the buyers of organic meat as a group (the price-insensitive like cultivated meat no more than others
  in utils, and in money they are the most hostile; `demand_heterogeneity_evidence.md`).
- **Premium products alone just reach the switch.** The five need 1.10 million m² of membrane a year (0.68 before), a tenth
  above the switch at 1.0. The four small markets alone need 0.33 million. All of the low-lactate example's sales need 13.6
  million. So the premium start is neither needed nor the main carrier: without any premium product the other sales need 12.5
  million m², past even a switch at 3 million. The all-favourable example needs 0.71 million m² for all its 18.4 Mt a year, and
  does not cross the central switch at all.
- **The unlocking is large once the membrane is cheap.** At $23.52 a kilo of cells cultivated meat costs 0.73 times prime beef,
  0.94 times sushi-grade seafood and 1.65 times premium fillets and shrimp. Its share of prime beef rises from 1.72% to 23.7%, of
  sushi-grade seafood from 0.71% to 8.17%, and of premium fillets and shrimp from 0.37% to 1.56%.
- **The loop reaches prime beef and sushi-grade fish; the rest stays above its meat's price.** At the low-lactate example's
  resting point organic chicken is 2.54 times, heritage pork 2.06 times and premium fillets 1.65 times their price. Of its 2.64
  Mt a year, 1.37 Mt are cuts, 0.45 Mt premium products and 0.82 Mt mince and processed meat, for 0.79% of world meat. Only the
  all-favourable example's cells take the loop far into mince and processed meat (6.89 Mt a year at their resting point).

## 5. How strong is the loop, and how well is that known?

| scenario | its own cost and share | first pass: the learning its own volume brings | resting point | part of the share gain from later rounds | resting point with demand anchored on premium meats (its own share there) |
|---|---|---|---|---|---|
| 4. Plus perfusion (the low-lactate example) | $48.68, 0.26% | $24.75, 0.72% | $23.52, 0.79% | 12% | $48.26, 0.01% (0.01%) |
| 7. Plus everything else at its favourable end (the all-favourable example) | $6.97, 5.48% | $6.32, 6.12% | $6.30, 6.14% | 2% | $6.42, 2.51% (2.31%) |

| input, across its range | 4. Plus perfusion (the low-lactate example): cells, share | 7. Plus everything else at its favourable end (the all-favourable example): cells, share |
|---|---|---|
| Membrane demand at which a food-grade supplier appears (300000 to 3e+06 m2 a year) | $23.49 to $23.85, 0.79% to 0.77% | $6.30 to $6.30, 6.14% to 6.14% |
| That supplier's first price (60 to 400 $/m2) | $23.49 to $25.02, 0.79% to 0.71% | $6.30 to $6.30, 6.14% to 6.14% |
| Membrane's price fall per doubling (0.1 to 0.28 per doubling) | $24.09 to $23.49, 0.75% to 0.79% | $6.30 to $6.30, 6.14% to 6.14% |
| Membrane's price floor (20 to 120 $/m2) | $23.52 to $24.66, 0.79% to 0.73% | $6.30 to $6.30, 6.14% to 6.14% |
| Plant's cost fall per doubling (0.03 to 0.18 per doubling) | $25.77 to $21.48, 0.67% to 0.92% | $6.74 to $6.25, 5.70% to 6.20% |
| Animal-cell tanks installed today (6500 to 11800 m3) | $23.34 to $23.86, 0.80% to 0.77% | $6.28 to $6.35, 6.16% to 6.08% |
| World meat, boneless (300 to 384 Mt a year) | $23.65 to $23.38, 0.78% to 0.79% | $6.32 to $6.29, 6.12% to 6.15% |

- **It is mostly one step, not a loop.** 88% of the low-lactate example's gain in share comes on the first pass: the 0.87 Mt
  it already sells crosses the membrane switch, cells fall to $24.75 and the share rises to 0.72%. Later rounds, where cheaper
  cells sell more and more sales make cells cheaper again, add the other 12% (to $23.52 and 0.79%). For the all-favourable
  example's cells the first pass gives 98%. (Fourth batch: 69% and 31%; after the engine batch later rounds gave 32%.) So the
  result rests mostly on whether one event happens, a food-grade membrane supplier, and at what price.
- **The plant's learning rate matters most, then the food-grade supplier's first price and the membrane's floor**; the switch's
  level and the speed of the membrane's later fall matter little (table above). Across the switch's range (0.3 to 3 million m²) the
  low-lactate example rests at $23.49 to $23.85, because its sales need 13.6 million. (Before the price-insensitive shoppers a 3
  million m² switch left it at $47.66.)
- **The all-favourable example's cells are sturdy on cost**: $6.25–6.74 across every input; only the plant's learning rate moves
  them.
- **The share side is weaker than the cost side.** With the share taken from the single curve fitted to premium real meats
  (`premium_curve.md`) in place of the model's, the low-lactate example does not cross the switch: at its own cost the fitted
  curve gives 0.014% of world meat, about a twentieth of the model's 0.26%, and those sales need about 0.7 million m², short of
  the central switch, so it rests at $48.26 and 0.015%, not $23.52 and 0.79%. The all-favourable example's cells cost about the
  same ($6.42) and take 2.51%, not 6.14%. So whether the low-lactate example crosses at all depends on which demand side is right,
  and the model's side now rests on the price-insensitive shoppers.

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

| premium product | price against it: at $48.68 a kilo of cells, at $23.52 | cultivated meat's share of it | percent more share per percent lower price |
|---|---|---|---|
| chicken (organic) | 4.69×, 2.54× | 0.27%, 0.69% | 1.5 |
| pork (heritage) | 3.81×, 2.06× | 0.32%, 0.98% | 1.8 |
| beef (prime/wagyu) | 1.35×, 0.73× | 1.72%, 23.67% | 4.3 |
| seafood (premium fillet, shrimp) | 3.05×, 1.65× | 0.37%, 1.56% | 2.4 |
| seafood (sushi) | 1.74×, 0.94× | 0.71%, 8.17% | 4.0 |
| history, along the demand curve (farmed salmon while still a premium product) | | | 1–1.5 |
| history, in total, with demand growth mixed in (salmon, US broilers, US catfish) | | | 1.3–4.1 |

- Farmed salmon is the closest case: 13 kt in 1980 to over 1 Mt in 1999 while its real price fell to a third (Asche, Bjørndal & Young
  2001, FT; Bjørndal & Tusvik 2017, FT). Early growth was largely "a move down along the demand schedule"; since 2000 nearly all growth
  has been demand shifting at flat prices. US broilers: real price −67% and consumption per person up fourfold, 1955–87 (Bishop &
  Christensen, USDA 1989, FT).
- **The model's premium products respond to price more strongly than farmed salmon did along its demand curve, but the three
  dearest now come close. The check still fails.** Organic chicken responds at 1.5, at the top of salmon's range along the curve
  (1–1.5), heritage pork at 1.8 and premium fillets and shrimp at 2.4; sushi-grade seafood at 4.0 and prime beef at 4.3, nearest
  their meat's price, are two and a half to three times that top. All but prime beef are inside history's totals, where demand
  growth is mixed in (1.3–4.1). In the fourth batch all five gave 3.7–4.2. The change is the price-insensitive shoppers
  (`demand_checks.md` section 7): the dearer the product, the more of its buyers are price-insensitive, and they respond to a
  falling price about as salmon's buyers did; nearer its meat's price a product's buyers are mostly ordinary shoppers.
- **Why it moved before.** Until the audit batch the tier rule made buyers of cuts and premium products less sensitive to price;
  the audit removed it (`audit_2026-11-19.md`, D3), leaving the normal spread's tail (5.2–7.5); the Student's t spread fitted later
  the same day gave 3.6–3.7, and the dearer cells of 2026-11-20 3.7–4.3. The price-insensitive shoppers do, for every product,
  part of what the tier rule did for cuts and premium products, but they are a class of shoppers the evidence shows, with a
  liking for cultivated meat read from two studies, and they do not lift cultivated meat's share wherever it is the dearer product
  by rule.
- **What it means for the loop.** Between the low-lactate example's own cost and its resting point shop prices fall by about
  half (49%) and its sales triple, a response of about 1.6 overall. At the top of salmon's range along the curve (1.5) the same
  fall in price would multiply its sales by about 2.8, against the model's 3.0; at the top of history's totals (4.1) by about
  sixteen. The low-lactate example's gain from cheaper cells is now about what history supports. Its starting point, 0.26% of
  world meat at $48.68, is what rests on the price-insensitive shoppers, not the gain. With the demand anchored on premium real
  meats there is no fall in price: it does not cross the switch (section 5).

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
- **Five changes in four days moved the low-lactate example's first sales, and the conclusions with them.** The audit batch of
  2026-11-19 (cells dearer, $26.43 to $32.80; seafood re-priced; the tier rule replaced) cut its sales at its own cost from
  1.78 to 0.26 Mt a year and its margin over the switch from ten times to 2.3. The Student's t spread of liking and the
  restructure of the scenarios then raised them to 0.71 Mt and 6.2 times. The engine batch of 2026-11-20 (cells at $49.96, a
  shorter membrane life) cut them to 0.15 Mt and 2.5 times, and they stayed near there through the batches of 2026-11-21 (0.15 Mt
  and 2.4 times). The price-insensitive shoppers of 2026-11-22 raised them to 0.87 Mt and 13.6 times. Its resting point went from
  $15.05 and 2.49% to $17.75 and 0.98%, then $17.50 and 1.34%, $24.00 and 0.57%, $24.95 and 0.48%, $23.91 and 0.54%, $24.05 and
  0.48%, and now $23.52 and 0.79%.
- **The far tail of the demand curve.** 79% of the low-lactate example's first sales are of products at more than four times
  their meat's price, where the share is an extrapolation and is bought by the price-insensitive shoppers. Without them its sales
  would need about 2.9 million m²: past the central switch, just short of one at 3 million.
- **The low-lactate example's cost is itself uncertain.** Across draws its cells cost $39–76 a kilo (8 in 10), with a median of
  $52, above the $48.68 at most likely values. At $52 its sales need about 12 million m² of membrane; at $76 about 6 million, still
  six times the switch. Its sales would fall short of the switch only above about $150 a kilo (at the low-lactate example's membrane use a kilo).
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
  the low-lactate example's sales to pass the switch with no outside push: on the model's demand they do at every cost in its
  8-in-10 range and every switch in its range; on the curve fitted to premium real meats they fall short (about 0.7 million m²).
  For learning to take the low-lactate example above 1% of world meat: no learning case does at its point cost (the middle case
  rests at 0.79%, fast learning at 0.96%; slow learning 0.54%, no supplier 0.27%, the demand anchored on premium meats 0.015%).
  Those shares rest on how much the price-insensitive shoppers like cultivated meat: at 2 utils less than other shoppers the
  low-lactate example starts from 0.11% of world meat, at 2 more from 0.58% (`demand_checks.md` section 7).

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
