# Does cultivated meat get cheaper as it sells more? Cost and share solved together

Date: 2026-11-18; revised the same day after the checks in section 6 (the premium markets were sized from data, which changed the
conclusion for Central). Code: `market_size_loop.py`; test: `tests/test_market_size_loop.py`. The study itself changes no default.

Access levels: **FT** full text read; **ABS** abstract only; **SNIP** search snippet; **MEM** background knowledge, unchecked.

**The idea** (Pablo): the model runs one way, from a cost to a share. But the cell filter's membrane and the plant are priced as today's
small biopharma supply industry prices them, and even a fraction of a percent of world meat would need several times all the
animal-cell tank volume that exists. So the cost should fall as the market grows. And the loop should start in premium products: where
cultivated meat first undercuts the premium product it competes with (Wildtype's salmon against sushi-grade salmon), the demand that
unlocks is the volume that makes everything cheaper.

**In short.** The best case reaches price parity this way. Central does not get there by itself: its sales are almost all premium
products, and those markets are too small to bring a food-grade membrane supplier into being. If someone else does (a subsidy, an order
book, another industry), Central's cells fall from $29 to about $21 and its share roughly triples, to 0.14% of world meat.

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

**1. Today** (no learning: $62.96)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.0037% | 2,533 | 1,450 | 0.96× | $61.50 | 0.00% |
| 0.1 | 0.037% | 25,335 | 1,450 | 0.80× | $56.00 | 0.00% |
| 0.5 | 0.185% | 126,674 | 1,450 | 0.65× | $50.51 | 0.00% |
| 2 | 0.741% | 506,698 | 107 | 0.53× | $44.04 | 0.01% |
| 10 | 3.7% | 2,533,490 | 67 | 0.42× | $39.90 | 0.01% |
| 35 | 13% | 8,867,215 | 50 | 0.34× | $37.30 | 0.02% |

**3. Plus cells selected to grow faster on the low-waste feed (Central)** (no learning: $29.42)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.0037% | 485 | 1,450 | 0.99× | $29.35 | 0.04% |
| 0.1 | 0.037% | 4,854 | 1,450 | 0.93× | $28.90 | 0.05% |
| 0.5 | 0.185% | 24,271 | 111 | 0.81× | $20.31 | 0.15% |
| 2 | 0.741% | 97,086 | 75 | 0.68× | $19.12 | 0.19% |
| 10 | 3.7% | 485,428 | 50 | 0.53× | $17.93 | 0.24% |
| 35 | 13% | 1,698,999 | 50 | 0.44× | $17.25 | 0.28% |

**5. Plus engineered cells** (no learning: $9.66)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.0037% | 227 | 1,450 | 1.00× | $9.65 | 3.12% |
| 0.1 | 0.037% | 2,267 | 1,450 | 0.96× | $9.58 | 3.19% |
| 0.5 | 0.185% | 11,334 | 1,450 | 0.87× | $9.41 | 3.41% |
| 2 | 0.741% | 45,335 | 103 | 0.75× | $6.68 | 9.03% |
| 10 | 3.7% | 226,676 | 65 | 0.60× | $6.30 | 10.24% |
| 35 | 13% | 793,367 | 50 | 0.52× | $6.11 | 10.91% |

"Share that cost would buy" is the main model's long-run share at that cost. Where it exceeds the share the volume is, the market grows;
where it is less, it shrinks. With both items at their floors the cells cost $35.24 (today's cells), $16.10 (Central) and
$6.11 (the best case).

## 3. Where cost and share agree

| scenario | learning | the main model: cells, share | resting point from below: cells, share, Mt a year | from above: cells, share, Mt a year |
|---|---|---|---|---|
| 1. Today | central | $62.96, 0.00% | $62.45, 0.00%, 0.00 | $62.45, 0.00%, 0.00 |
| 1. Today | no food-grade membrane supplier, slow plant learning | $62.96, 0.00% | $62.82, 0.00%, 0.00 | $62.82, 0.00%, 0.00 |
| 1. Today | slow learning | $62.96, 0.00% | $62.82, 0.00%, 0.00 | $62.82, 0.00%, 0.00 |
| 1. Today | fast learning | $62.96, 0.00% | $61.95, 0.00%, 0.00 | $61.95, 0.00%, 0.00 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | central | $29.42, 0.04% | $28.81, 0.05%, 0.13 | $20.52, 0.14%, 0.39 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no food-grade membrane supplier, slow plant learning | $29.42, 0.04% | $29.24, 0.04%, 0.12 | $29.24, 0.04%, 0.12 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | slow learning | $29.42, 0.04% | $29.24, 0.04%, 0.12 | $29.24, 0.04%, 0.12 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | fast learning | $29.42, 0.04% | $18.64, 0.21%, 0.56 | $18.64, 0.21%, 0.56 |
| 5. Plus engineered cells | central | $9.66, 3.11% | $6.11, 10.91%, 29.47 | $6.11, 10.91%, 29.47 |
| 5. Plus engineered cells | no food-grade membrane supplier, slow plant learning | $9.66, 3.11% | $9.39, 3.43%, 9.27 | $9.39, 3.43%, 9.27 |
| 5. Plus engineered cells | slow learning | $9.66, 3.11% | $7.16, 7.65%, 20.67 | $7.16, 7.65%, 20.67 |
| 5. Plus engineered cells | fast learning | $9.66, 3.11% | $6.05, 11.11%, 30.00 | $6.05, 11.11%, 30.00 |

"From below" starts with no learning; "from above" starts with everything at its floor. Where the two differ there are two resting
points, and reaching the upper one needs someone to carry the industry across the gap.

- **The best case reaches parity by this route: $6.11 against the $6.14 parity needs, and 10.91% of world meat** (3.11% without
  learning). It has one resting point: its own sales are enough to bring the food-grade membrane. This is the only route found so far to
  parity that needs no better cells than the best case already assumes.
- **Central has two resting points.** Left alone it stays at $28.81 and 0.05% of world meat: its 0.11 Mt a year needs 0.64 million m²
  of membrane, short of the switch at 1.0. If the food-grade membrane exists anyway, Central rests at $20.52 and 0.14%.
  With fast learning (a switch at 0.3 million m²) it crosses by itself, to $18.64 and 0.21%.
- **Today's cells are stuck** in every case: at $63 they sell almost nothing.
- **Without a food-grade membrane supplier little changes**: Central $29.24, the best case $9.39. The plant's learning alone
  is worth under a dollar.

## 4. The loop starts in premium products, and they are a small base

| scenario | stage | cells, $/kg | sold, Mt a year: premium products, cuts, mince and processed | premium products' part of sales | chicken (organic): price against it, share of it | pork (heritage): price against it, share of it | beef (prime/wagyu): price against it, share of it | seafood (sushi): price against it, share of it |
|---|---|---|---|---|---|---|---|---|
| 1. Today | no learning | $62.96 | 0.00, 0.00, 0.00 | 100% | 7.63×, 0.0% | 6.20×, 0.0% | 2.21×, 0.3% | 2.84×, 0.1% |
| 1. Today | resting point | $62.45 | 0.00, 0.00, 0.00 | 100% | 7.58×, 0.0% | 6.16×, 0.0% | 2.19×, 0.3% | 2.82×, 0.1% |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no learning | $29.42 | 0.11, 0.00, 0.00 | 96% | 4.05×, 0.3% | 3.29×, 0.5% | 1.17×, 10.7% | 1.50×, 5.0% |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | resting point | $28.81 | 0.12, 0.01, 0.00 | 95% | 3.99×, 0.3% | 3.24×, 0.6% | 1.15×, 11.3% | 1.48×, 5.3% |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | upper resting point | $20.52 | 0.27, 0.11, 0.01 | 69% | 3.10×, 1.0% | 2.52×, 1.8% | 0.90×, 23.6% | 1.15×, 12.4% |
| 5. Plus engineered cells | no learning | $9.66 | 0.66, 4.88, 2.85 | 8% | 1.94×, 5.4% | 1.58×, 7.9% | 0.56×, 49.5% | 0.72×, 32.5% |
| 5. Plus engineered cells | resting point | $6.11 | 0.83, 13.82, 14.81 | 3% | 1.56×, 9.0% | 1.27×, 12.5% | 0.45×, 58.7% | 0.58×, 41.7% |

| scenario | learning | premium products sold at the scenario's own cost, Mt a year | membrane that needs, million m² a year | the switch, million m² a year | do premium products alone cross it? |
|---|---|---|---|---|---|
| 1. Today | central | 0.00 | 0.00 | 1.0 | no |
| 1. Today | no food-grade membrane supplier, slow plant learning | 0.00 | 0.00 | never | no |
| 1. Today | slow learning | 0.00 | 0.00 | 3.0 | no |
| 1. Today | fast learning | 0.00 | 0.00 | 0.3 | no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | central | 0.11 | 0.64 | 1.0 | no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no food-grade membrane supplier, slow plant learning | 0.11 | 0.64 | never | no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | slow learning | 0.11 | 0.64 | 3.0 | no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | fast learning | 0.11 | 0.64 | 0.3 | yes |
| 5. Plus engineered cells | central | 0.66 | 1.21 | 1.0 | yes |
| 5. Plus engineered cells | no food-grade membrane supplier, slow plant learning | 0.66 | 1.21 | never | no |
| 5. Plus engineered cells | slow learning | 0.66 | 1.21 | 3.0 | no |
| 5. Plus engineered cells | fast learning | 0.66 | 1.21 | 0.3 | yes |

- **At Central's cost, 96% of cultivated meat's sales are premium products**: prime or wagyu beef at 1.17 times its price and
  sushi-grade seafood at 1.50 times. That is the whole early industry, as Pablo expected.
- **But those markets are small.** Sized from data (`premium_market_sizes.md`), sushi-grade seafood is about 1.2 Mt a year and prime or
  wagyu beef about 0.5 Mt. Central's share of them is 0.11 Mt a year, which needs 0.64 million m² of membrane a year: about twenty
  times today's whole perfusion-filter market, but short of the million taken to bring a food-grade supplier.
- **The unlocking is real once the membrane is cheap.** At $20.52 a kilo of cells cultivated meat costs 0.90 times prime beef and
  1.15 times sushi-grade seafood, and its shares of them more than double (prime beef 10.7% to 23.6%,
  sushi-grade seafood 5.0% to 12.4%). Premium products sold rise from 0.11 to 0.27 Mt a year.
- **So Central's gap is a coordination problem**: a membrane maker will not build for a market that is not there, and the market is
  not there at pharma prices. Whoever closes it (a subsidy, a purchase commitment, a supplier who already sells to another industry)
  moves Central from 0.05% to 0.14%.
- **Premium products are not enough to reach mass meat.** At Central's upper resting point 69% of sales are still premium; cuts and
  mince stay at two to three times their conventional price. Only the best case's cells carry the loop into ordinary cuts and mince
  (where 97% of its sales are).

## 5. How strong is the loop, and how well is that known?

| scenario | its own cost and share | first pass: the learning its own volume brings | resting point | part of the share gain from later rounds | resting point with demand anchored on premium meats (its own share there) |
|---|---|---|---|---|---|
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | $29.42, 0.04% | $28.84, 0.05% | $28.81, 0.05% | 5% | $19.48, 0.48% (0.14%) |
| 5. Plus engineered cells | $9.66, 3.11% | $6.34, 10.11% | $6.11, 10.91% | 10% | $6.35, 2.97% (1.83%) |

| input, across its range | 3. Plus cells selected to grow faster on the low-waste feed (Central): cells, share | 5. Plus engineered cells: cells, share |
|---|---|---|
| Membrane demand at which a food-grade supplier appears (300000 to 3e+06 m2 a year) | $20.29 to $28.81, 0.15% to 0.05% | $6.11 to $6.14, 10.91% to 10.81% |
| That supplier's first price (60 to 400 $/m2) | $28.81 to $28.81, 0.05% to 0.05% | $6.11 to $6.26, 10.91% to 10.40% |
| Membrane's price fall per doubling (0.1 to 0.28 per doubling) | $28.81 to $28.81, 0.05% to 0.05% | $6.17 to $6.11, 10.70% to 10.91% |
| Membrane's price floor (20 to 120 $/m2) | $28.81 to $28.81, 0.05% to 0.05% | $6.11 to $6.24, 10.93% to 10.46% |
| Plant's cost fall per doubling (0.03 to 0.18 per doubling) | $29.24 to $28.26, 0.04% to 0.05% | $6.74 to $6.11, 8.83% to 10.91% |
| Animal-cell tanks installed today (6500 to 11800 m3) | $28.70 to $28.97, 0.05% to 0.05% | $6.11 to $6.16, 10.91% to 10.73% |
| World meat, boneless (250 to 384 Mt a year) | $28.84 to $20.16, 0.05% to 0.15% | $6.11 to $6.11, 10.91% to 10.91% |

- **It is mostly one step, not a loop.** 90% of the best case's gain in share comes on the first pass: the volume it already
  sells is enough for the membrane switch. Later rounds, where cheaper cells sell more and more sales make cells cheaper again, add
  10%. So the result does not rest on the strength of a feedback, which could not be measured; it rests on whether one event happens
  (a food-grade membrane supplier) and at what price.
- **For Central everything turns on the switch.** At 0.3 million m² a year it crosses and its cells fall to about $20; at 1 or 3 million it
  does not. World meat at the top of its range (counting carcass weight) is also enough. The learning rates and the membrane's later
  price move nothing while Central is below the switch.
- **The best case is sturdy on cost**: $6.1–6.8 across every input.
- **The share side is weaker than the cost side.** With the share taken from the curve fitted to premium real meats (`premium_curve.md`)
  in place of the main model's, the best case's cells cost about the same ($6.35) but its share is 2.97%, not 10.91%. For Central the
  two disagree the other way: on that curve Central sells 0.14% without learning, enough to cross the switch, and rests at 0.48%.
  How much a given price sells is the model's least-tested part, with or without learning.

## 6. The checks (2026-11-18)

**How big are the premium markets?** Several times smaller than the model's tables had them (`premium_market_sizes.md`): sushi-grade
seafood about 1.2 Mt a year (the table had 5.4) and prime or wagyu beef about 0.5 Mt (1.35). The tables were corrected. This is what
turned Central from "crosses the switch" into "needs a push".

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

| premium product | price against it: at $29.42 a kilo of cells, at $20.52 | cultivated meat's share of it | percent more share per percent lower price |
|---|---|---|---|
| chicken (organic) | 4.05×, 3.10× | 0.26%, 1.03% | 5.2 |
| pork (heritage) | 3.29×, 2.52× | 0.51%, 1.79% | 4.7 |
| beef (prime/wagyu) | 1.17×, 0.90× | 10.68%, 23.63% | 3.0 |
| seafood (sushi) | 1.50×, 1.15× | 4.95%, 12.44% | 3.4 |
| history, along the demand curve (farmed salmon while still a premium product) | | | 1–1.5 |
| history, in total, with demand growth mixed in (salmon, US broilers, US catfish) | | | 1.3–4.1 |

- Farmed salmon is the closest case: 13 kt in 1980 to over 1 Mt in 1999 while its real price fell to a third (Asche, Bjørndal & Young
  2001, FT; Bjørndal & Tusvik 2017, FT). Early growth was largely "a move down along the demand schedule"; since 2000 nearly all growth
  has been demand shifting at flat prices. US broilers: real price −67% and consumption per person up fourfold, 1955–87 (Bishop &
  Christensen, USDA 1989, FT).
- **The model's premium products respond to price about as strongly as history's totals, and two to three times more strongly than
  history along the demand curve.** So the later rounds of the loop, and the size of the unlocking in section 4, are more likely
  overstated than understated. The first pass, which is most of the result, does not depend on this.

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

- **The switch is a judgement** (about 65% that a food-grade supplier appears once demand passes 1 million m² a year). It decides
  Central's result.
- **Still unknown:** an actual quote for a steam-tolerant food-grade module; a month-long run of animal cells at a quarter by volume
  above bench scale; the yearly area of perfusion filters sold today (estimated, not published); retail prices of the premium
  products by grade.
- **Resting points, not a path.** Learning is counted on yearly scale, not cumulative output, and nothing says who pays for the early
  years.
- **Not combined with the premium-buyer study** (`premium_buyers.md`), which would add to Central's early volume.
- **Judgement:** that a food-grade membrane at $250 a m² or less exists if cultivated meat sells 0.5 Mt a year: about 0.6. That
  learning of this kind takes the best case's cells to $7 or less, given the best case's cells exist: about 0.55. That Central crosses
  the switch with no outside push: about 0.3. That learning takes Central above 1% of world meat: about 0.03.

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
