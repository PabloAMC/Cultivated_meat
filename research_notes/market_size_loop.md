# Does cultivated meat get cheaper as it sells more? Cost and share solved together

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50.

Date: 2026-11-18; revised twice the same day: after the checks in section 6 (the premium markets were sized from data) and after the
shopper model gained a spread of liking across shoppers (`liking_spread.md`). Code: `market_size_loop.py`; test: `tests/test_market_size_loop.py`.
The study itself changes no default.

Access levels: **FT** full text read; **ABS** abstract only; **SNIP** search snippet; **MEM** background knowledge, unchecked.

**The idea** (Pablo): the model runs one way, from a cost to a share. But the cell filter's membrane and the plant are priced as today's
small biopharma supply industry prices them, and even a fraction of a percent of world meat would need several times all the
animal-cell tank volume that exists. So the cost should fall as the market grows. And the loop should start in premium products: where
cultivated meat first undercuts the premium product it competes with (Wildtype's salmon against sushi-grade salmon), the demand that
unlocks is the volume that makes everything cheaper.

**In short.** Both Central and the best case sell enough to bring a food-grade membrane supplier into being, and both get much
cheaper for it: Central's cells fall from $26 to about $16 and its share rises from 0.13% to 0.86% of world meat; the best
case comes close to price parity but no longer reaches it ($6.49 against $6.14). Central gets there on the purchases of
the shoppers who like cultivated meat most, of ordinary cuts as well as premium products; premium products alone are too small a market. Today's cells sell too little to start.

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
- World meat is taken as 270 Mt a year of boneless weight (378–384 Mt of carcass weight, FAO, SNIP).

## 2. Cost against volume

**1. Today** (no learning: $56.99)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.00298% | 2,533 | 1,450 | 0.96× | $55.53 | 0.01% |
| 0.1 | 0.0298% | 25,335 | 1,450 | 0.80× | $50.03 | 0.01% |
| 0.5 | 0.149% | 126,674 | 1,450 | 0.65× | $44.54 | 0.02% |
| 2 | 0.595% | 506,698 | 107 | 0.53× | $38.07 | 0.03% |
| 10 | 2.98% | 2,533,490 | 67 | 0.42× | $33.92 | 0.04% |
| 35 | 10.4% | 8,867,215 | 50 | 0.34× | $31.32 | 0.06% |

**3. Plus cells selected to grow faster on the low-waste feed (Central)** (no learning: $26.43)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.00298% | 485 | 1,450 | 0.99× | $26.36 | 0.13% |
| 0.1 | 0.0298% | 4,854 | 1,450 | 0.93× | $25.92 | 0.14% |
| 0.5 | 0.149% | 24,271 | 111 | 0.81× | $17.32 | 0.66% |
| 2 | 0.595% | 97,086 | 75 | 0.68× | $16.13 | 0.81% |
| 10 | 2.98% | 485,428 | 50 | 0.53× | $14.94 | 1.01% |
| 35 | 10.4% | 1,698,999 | 50 | 0.44× | $14.26 | 1.15% |

**5. Plus engineered cells** (no learning: $9.96)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.00298% | 227 | 1,450 | 1.00× | $9.95 | 2.74% |
| 0.1 | 0.0298% | 2,267 | 1,450 | 0.96× | $9.89 | 2.78% |
| 0.5 | 0.149% | 11,334 | 1,450 | 0.87× | $9.71 | 2.88% |
| 2 | 0.595% | 45,335 | 103 | 0.75× | $6.98 | 4.90% |
| 10 | 2.98% | 226,676 | 65 | 0.60× | $6.61 | 5.25% |
| 35 | 10.4% | 793,367 | 50 | 0.52× | $6.41 | 5.44% |

"Share that cost would buy" is the main model's long-run share at that cost. Where it exceeds the share the volume is, the market grows;
where it is less, it shrinks. With both items at their floors the cells cost $29.26 (today's cells), $13.11 (Central) and
$6.41 (the best case).

## 3. Where cost and share agree

| scenario | learning | the main model: cells, share | resting point from below: cells, share, Mt a year | from above: cells, share, Mt a year |
|---|---|---|---|---|
| 1. Today | central | $56.99, 0.01% | $53.06, 0.01%, 0.04 | $53.06, 0.01%, 0.04 |
| 1. Today | no food-grade membrane supplier, slow plant learning | $56.99, 0.01% | $55.92, 0.01%, 0.03 | $55.92, 0.01%, 0.03 |
| 1. Today | slow learning | $56.99, 0.01% | $55.92, 0.01%, 0.03 | $55.92, 0.01%, 0.03 |
| 1. Today | fast learning | $56.99, 0.01% | $49.02, 0.01%, 0.04 | $49.02, 0.01%, 0.04 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | central | $26.43, 0.13% | $15.83, 0.86%, 2.89 | $15.83, 0.86%, 2.89 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no food-grade membrane supplier, slow plant learning | $26.43, 0.13% | $26.01, 0.14%, 0.45 | $26.01, 0.14%, 0.45 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | slow learning | $26.43, 0.13% | $26.01, 0.14%, 0.45 | $19.33, 0.45%, 1.51 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | fast learning | $26.43, 0.13% | $13.69, 1.28%, 4.29 | $13.69, 1.28%, 4.29 |
| 5. Plus engineered cells | central | $9.96, 2.74% | $6.49, 5.37%, 18.03 | $6.49, 5.37%, 18.03 |
| 5. Plus engineered cells | no food-grade membrane supplier, slow plant learning | $9.96, 2.74% | $9.69, 2.89%, 9.73 | $9.69, 2.89%, 9.73 |
| 5. Plus engineered cells | slow learning | $9.96, 2.74% | $7.51, 4.43%, 14.90 | $7.51, 4.43%, 14.90 |
| 5. Plus engineered cells | fast learning | $9.96, 2.74% | $6.36, 5.50%, 18.47 | $6.36, 5.50%, 18.47 |

"From below" starts with no learning; "from above" starts with everything at its floor. Where the two differ there are two resting
points, and reaching the upper one needs someone to carry the industry across the gap.

- **The best case comes close to parity by this route but does not reach it: $6.49 against the $6.14 parity needs, and 5.37% of
  world meat** (2.74% without learning). Even with both items at their floors its cells cost $6.41, and no input across its range
  takes them below $6.42 (section 5). (Before the medium was repriced on 2026-11-19 it reached $6.17, which counted as parity.)
- **Central: cells fall from $26.43 to $15.83 and the share rises from 0.13% to 0.86%.** Its 0.42 Mt a year needs 2.4 million m²
  of membrane, past the switch at 1.0, so it has one resting point. With slow learning (a switch at 3 million m²) it has two: left
  alone $26.01 and 0.14%, or $19.33 and 0.45% once someone else brings the food-grade supplier.
- **Today's cells are stuck** in every case: at $57 they sell almost nothing.
- **Without a food-grade membrane supplier little changes**: Central $26.01, the best case $9.69. The plant's learning alone
  is worth under a dollar.

## 4. The loop starts in premium products, and they are a small base

| scenario | stage | cells, $/kg | sold, Mt a year: premium products, cuts, mince and processed | premium products' part of sales | chicken (organic): price against it, share of it | pork (heritage): price against it, share of it | beef (prime/wagyu): price against it, share of it | seafood (sushi): price against it, share of it |
|---|---|---|---|---|---|---|---|---|
| 1. Today | no learning | $56.99 | 0.03, 0.00, 0.00 | 100% | 7.00×, 0.1% | 5.68×, 0.2% | 2.02×, 2.0% | 2.60×, 1.3% |
| 1. Today | resting point | $53.06 | 0.04, 0.00, 0.00 | 99% | 6.58×, 0.2% | 5.34×, 0.3% | 1.90×, 2.3% | 2.44×, 1.6% |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no learning | $26.43 | 0.13, 0.27, 0.02 | 31% | 3.73×, 1.7% | 3.03×, 2.2% | 1.08×, 7.7% | 1.39×, 5.6% |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | resting point | $15.83 | 0.21, 2.10, 0.58 | 7% | 2.60×, 3.3% | 2.11×, 4.1% | 0.75×, 10.9% | 0.97×, 8.8% |
| 5. Plus engineered cells | no learning | $9.96 | 0.26, 5.72, 3.22 | 3% | 1.97×, 4.9% | 1.60×, 5.9% | 0.57×, 13.0% | 0.73×, 10.7% |
| 5. Plus engineered cells | resting point | $6.49 | 0.29, 9.85, 7.89 | 2% | 1.60×, 6.2% | 1.30×, 7.2% | 0.46×, 14.4% | 0.59×, 11.9% |

| scenario | learning | premium products sold at the scenario's own cost, Mt a year | membrane that needs, million m² a year | the switch, million m² a year | do premium products alone cross it? |
|---|---|---|---|---|---|
| 1. Today | central | 0.03 | 0.05 | 1.0 | no |
| 1. Today | no food-grade membrane supplier, slow plant learning | 0.03 | 0.05 | never | no |
| 1. Today | slow learning | 0.03 | 0.05 | 3.0 | no |
| 1. Today | fast learning | 0.03 | 0.05 | 0.3 | no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | central | 0.13 | 0.76 | 1.0 | no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no food-grade membrane supplier, slow plant learning | 0.13 | 0.76 | never | no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | slow learning | 0.13 | 0.76 | 3.0 | no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | fast learning | 0.13 | 0.76 | 0.3 | yes |
| 5. Plus engineered cells | central | 0.26 | 0.47 | 1.0 | no |
| 5. Plus engineered cells | no food-grade membrane supplier, slow plant learning | 0.26 | 0.47 | never | no |
| 5. Plus engineered cells | slow learning | 0.26 | 0.47 | 3.0 | no |
| 5. Plus engineered cells | fast learning | 0.26 | 0.47 | 0.3 | yes |

- **Premium products are where cultivated meat is closest to the price it competes with**: prime or wagyu beef at 1.08 times its
  price and sushi-grade seafood at 1.39 times, at Central's cost. But those markets are small (`premium_market_sizes.md`: about 1.2 Mt
  and 0.5 Mt a year), and they are only 31% of Central's sales.
- **Most of Central's early volume is ordinary cuts and mince bought by the shoppers who like cultivated meat most**, at two and a half
  to three and a half times their price (mostly beef cuts and fish fillets): 0.27 and 0.02 Mt a year, against 0.13 Mt of
  premium products. They are the upper end of the spread of liking (`liking_spread.md`), not buyers of organic meat, who are the most hostile to it (`demand_heterogeneity_evidence.md`).
  Premium products alone would need 0.76 million m² of membrane a year, short of the switch; with all its sales Central
  needs 2.4 million and crosses.
- **The unlocking is real once the membrane is cheap.** At $15.83 a kilo of cells cultivated meat costs 0.75 times prime beef and
  0.97 times sushi-grade seafood, and its shares of them rise by about half (prime beef 7.7% to 10.9%,
  sushi-grade seafood 5.6% to 8.8%).
- **Premium products and the keenest shoppers are not enough to reach mass meat.** At Central's resting point cultivated meat is still
  one and a half to two and a half times the price of ordinary cuts and mince, and its share is under 1% (0.86%). Only the best
  case's cells carry the loop into the mainstream.

## 5. How strong is the loop, and how well is that known?

| scenario | its own cost and share | first pass: the learning its own volume brings | resting point | part of the share gain from later rounds | resting point with demand anchored on premium meats (its own share there) |
|---|---|---|---|---|---|
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | $26.43, 0.13% | $17.46, 0.64% | $15.83, 0.86% | 30% | $15.86, 0.83% (0.23%) |
| 5. Plus engineered cells | $9.96, 2.74% | $6.63, 5.23% | $6.49, 5.37% | 5% | $6.61, 2.97% (1.85%) |

| input, across its range | 3. Plus cells selected to grow faster on the low-waste feed (Central): cells, share | 5. Plus engineered cells: cells, share |
|---|---|---|
| Membrane demand at which a food-grade supplier appears (300000 to 3e+06 m2 a year) | $15.72 to $16.00, 0.88% to 0.83% | $6.48 to $6.53, 5.38% to 5.33% |
| That supplier's first price (60 to 400 $/m2) | $15.72 to $16.61, 0.88% to 0.75% | $6.48 to $6.67, 5.38% to 5.19% |
| Membrane's price fall per doubling (0.1 to 0.28 per doubling) | $16.04 to $15.72, 0.83% to 0.88% | $6.55 to $6.48, 5.30% to 5.38% |
| Membrane's price floor (20 to 120 $/m2) | $15.83 to $16.18, 0.86% to 0.81% | $6.49 to $6.61, 5.37% to 5.25% |
| Plant's cost fall per doubling (0.03 to 0.18 per doubling) | $17.72 to $13.97, 0.61% to 1.21% | $7.09 to $6.42, 4.80% to 5.43% |
| Animal-cell tanks installed today (6500 to 11800 m3) | $15.67 to $16.15, 0.89% to 0.81% | $6.45 to $6.56, 5.40% to 5.30% |
| World meat, boneless (300 to 384 Mt a year) | $15.94 to $15.71, 0.84% to 0.88% | $6.51 to $6.46, 5.34% to 5.39% |

- **It is mostly one step, not a loop.** 70% of Central's gain in share, and 95% of the best case's, comes on the first
  pass: the volume each already sells is enough for the membrane switch. Later rounds, where cheaper cells sell more and more sales
  make cells cheaper again, add 30% and 5%. So the result does not rest on the strength of a feedback, which could not be
  measured; it rests on whether one event happens (a food-grade membrane supplier) and at what price.
- **The plant's learning rate matters most, then the food-grade supplier's first price**; the membrane's later price matters
  little (table above). The switch's level now matters little on its own (a 3 million m² switch costs Central 17 cents), but with
  slow plant learning as well it leaves Central stuck (section 3).
- **The best case is sturdy on cost**: $6.4–7.1 across every input.
- **The share side is weaker than the cost side.** With the share taken from the single curve fitted to premium real meats
  (`premium_curve.md`) in place of the model's, the cells cost about the same but the best case's share is 2.97%, not 5.37%, and
  Central's 0.83%, not 0.86%.

## 6. The checks (2026-11-18)

**How big are the premium markets?** Several times smaller than the model's tables had them (`premium_market_sizes.md`): sushi-grade
seafood about 1.2 Mt a year (the table had 5.4) and prime or wagyu beef about 0.5 Mt (1.35). The tables were corrected. Premium
products alone no longer carry Central past the switch; premium buyers' purchases of ordinary meat do.

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

| premium product | price against it: at $26.43 a kilo of cells, at $15.83 | cultivated meat's share of it | percent more share per percent lower price |
|---|---|---|---|
| chicken (organic) | 3.73×, 2.60× | 1.70%, 3.28% | 1.8 |
| pork (heritage) | 3.03×, 2.11× | 2.18%, 4.09% | 1.7 |
| beef (prime/wagyu) | 1.08×, 0.75× | 7.73%, 10.94% | 1.0 |
| seafood (sushi) | 1.39×, 0.97× | 5.62%, 8.80% | 1.2 |
| history, along the demand curve (farmed salmon while still a premium product) | | | 1–1.5 |
| history, in total, with demand growth mixed in (salmon, US broilers, US catfish) | | | 1.3–4.1 |

- Farmed salmon is the closest case: 13 kt in 1980 to over 1 Mt in 1999 while its real price fell to a third (Asche, Bjørndal & Young
  2001, FT; Bjørndal & Tusvik 2017, FT). Early growth was largely "a move down along the demand schedule"; since 2000 nearly all growth
  has been demand shifting at flat prices. US broilers: real price −67% and consumption per person up fourfold, 1955–87 (Bishop &
  Christensen, USDA 1989, FT).
- **The model's premium products now respond to price about as history did**: from the response along the demand curve to a
  little above it (1.0–1.8 against 1–1.5), and no stronger than the totals. (With every shopper alike they responded two to three times more strongly.)

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
- **Still unknown:** an actual quote for a steam-tolerant food-grade module; a month-long run of animal cells at a quarter by volume
  above bench scale; the yearly area of perfusion filters sold today (estimated, not published); retail prices of the premium
  products by grade.
- **Resting points, not a path.** Learning is counted on yearly scale, not cumulative output, and nothing says who pays for the early
  years.
- **Judgement:** that a food-grade membrane at $250 a m² or less exists if cultivated meat sells 0.5 Mt a year: about 0.6. That
  learning of this kind takes the best case's cells to $7 or less, given the best case's cells exist: about 0.55. That Central crosses
  the switch with no outside push: about 0.5 (it rests on the keenest shoppers paying two and a half to three and a half times the price for ordinary cuts). That
  learning takes Central above 1% of world meat: about 0.15 (judged when its resting point was 0.45%; it is now 0.86%, and 1.2–1.3%
  with fast learning or fast plant learning, so this needs revisiting).

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
