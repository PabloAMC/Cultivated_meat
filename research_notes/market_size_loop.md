# Does cultivated meat get cheaper as it sells more? Cost and share solved together

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50; cut cost rebuilt (0.8 cells + $2 matrix + $2 assembly beyond mince), cuts cheaper.

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
cheaper for it: Central's cells fall from $26 to about $15 and its share rises from 0.53% to 2.49% of world meat; the best
case comes close to price parity but does not reach it ($6.41 against $6.14). Central gets there mostly on ordinary cuts, beef
steaks and fish fillets, bought by the shoppers who like cultivated meat most. Premium products alone just reach the switch, but
they are a small part of its sales. Today's cells sell too little to start. (Before the cut cost was rebuilt on 2026-11-19:
Central $15.83 and 0.86%, the best case $6.49.)

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
| 0.01 | 0.00298% | 2,533 | 1,450 | 0.96× | $55.53 | 0.02% |
| 0.1 | 0.0298% | 25,335 | 1,450 | 0.80× | $50.03 | 0.03% |
| 0.5 | 0.149% | 126,674 | 1,450 | 0.65× | $44.54 | 0.05% |
| 2 | 0.595% | 506,698 | 107 | 0.53× | $38.07 | 0.11% |
| 10 | 2.98% | 2,533,490 | 67 | 0.42× | $33.92 | 0.19% |
| 35 | 10.4% | 8,867,215 | 50 | 0.34× | $31.32 | 0.28% |

**3. Plus cells selected to grow faster on the low-waste feed (Central)** (no learning: $26.43)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.00298% | 485 | 1,450 | 0.99× | $26.36 | 0.53% |
| 0.1 | 0.0298% | 4,854 | 1,450 | 0.93× | $25.92 | 0.57% |
| 0.5 | 0.149% | 24,271 | 111 | 0.81× | $17.32 | 1.80% |
| 2 | 0.595% | 97,086 | 75 | 0.68× | $16.13 | 2.14% |
| 10 | 2.98% | 485,428 | 50 | 0.53× | $14.94 | 2.53% |
| 35 | 10.4% | 1,698,999 | 50 | 0.44× | $14.26 | 2.77% |

**5. Plus engineered cells** (no learning: $9.96)

| cultivated meat sold, Mt a year | that is, of world meat | tanks needed, m³ | membrane, $/m² | plant cost against today's | cells, $/kg | share that cost would buy |
|---|---|---|---|---|---|---|
| 0.01 | 0.00298% | 227 | 1,450 | 1.00× | $9.95 | 4.97% |
| 0.1 | 0.0298% | 2,267 | 1,450 | 0.96× | $9.89 | 5.02% |
| 0.5 | 0.149% | 11,334 | 1,450 | 0.87× | $9.71 | 5.15% |
| 2 | 0.595% | 45,335 | 103 | 0.75× | $6.98 | 7.63% |
| 10 | 2.98% | 226,676 | 65 | 0.60× | $6.61 | 8.07% |
| 35 | 10.4% | 793,367 | 50 | 0.52× | $6.41 | 8.30% |

"Share that cost would buy" is the main model's long-run share at that cost. Where it exceeds the share the volume is, the market grows;
where it is less, it shrinks. With both items at their floors the cells cost $29.26 (today's cells), $13.11 (Central) and
$6.41 (the best case).

## 3. Where cost and share agree

| scenario | learning | the main model: cells, share | resting point from below: cells, share, Mt a year | from above: cells, share, Mt a year |
|---|---|---|---|---|
| 1. Today | central | $56.99, 0.02% | $49.54, 0.03%, 0.12 | $49.54, 0.03%, 0.12 |
| 1. Today | no food-grade membrane supplier, slow plant learning | $56.99, 0.02% | $55.11, 0.02%, 0.08 | $55.11, 0.02%, 0.08 |
| 1. Today | slow learning | $56.99, 0.02% | $55.11, 0.02%, 0.08 | $55.11, 0.02%, 0.08 |
| 1. Today | fast learning | $56.99, 0.02% | $33.67, 0.20%, 0.67 | $33.67, 0.20%, 0.67 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | central | $26.43, 0.53% | $15.05, 2.49%, 8.36 | $15.05, 2.49%, 8.36 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no food-grade membrane supplier, slow plant learning | $26.43, 0.53% | $25.64, 0.59%, 1.97 | $25.64, 0.59%, 1.97 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | slow learning | $26.43, 0.53% | $18.69, 1.48%, 4.97 | $18.69, 1.48%, 4.97 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | fast learning | $26.43, 0.53% | $13.03, 3.27%, 10.99 | $13.03, 3.27%, 10.99 |
| 5. Plus engineered cells | central | $9.96, 4.97% | $6.41, 8.30%, 27.90 | $6.41, 8.30%, 27.90 |
| 5. Plus engineered cells | no food-grade membrane supplier, slow plant learning | $9.96, 4.97% | $9.64, 5.20%, 17.46 | $9.64, 5.20%, 17.46 |
| 5. Plus engineered cells | slow learning | $9.96, 4.97% | $7.44, 7.13%, 23.96 | $7.44, 7.13%, 23.96 |
| 5. Plus engineered cells | fast learning | $9.96, 4.97% | $6.36, 8.37%, 28.13 | $6.36, 8.37%, 28.13 |

"From below" starts with no learning; "from above" starts with everything at its floor. Where the two differ there are two resting
points, and reaching the upper one needs someone to carry the industry across the gap.

- **The best case comes close to parity by this route but does not reach it: $6.41 against the $6.14 parity needs, and 8.30% of
  world meat** (4.97% without learning). It rests at the cost with both items at their floors ($6.41), and no single input across
  its range takes its cells lower (section 5); fast learning, all its inputs at once, gives $6.36. (Before the medium was repriced on 2026-11-19 it reached $6.17, which counted as parity;
  before the cut cost was rebuilt the same day it rested at $6.49 and 5.37%.)
- **Central: cells fall from $26.43 to $15.05 and the share rises from 0.53% to 2.49%.** Its 1.78 Mt a year needs 10.2 million m²
  of membrane, ten times the switch at 1.0, so it has one resting point. With slow learning (a switch at 3 million m²) it
  still crosses on its own sales and has one resting point: $18.69 and 1.48%. There is no gap for anyone to carry it across.
  (Before the cut cost was rebuilt it sold 0.42 Mt a year, needed 2.4 million m², and with slow learning had two resting points:
  $26.01 and 0.14% left alone, $19.33 and 0.45% once someone else brought the food-grade supplier.)
- **Today's cells are stuck** in almost every case: at $57 they sell almost nothing, and the central case's learning takes them only
  to $49.54 and 0.03%. Only fast learning, with a switch at 0.3 million m², gets them a food-grade membrane: $33.67 and 0.20%.
- **Without a food-grade membrane supplier little changes**: Central $25.64 and 0.59%, the best case $9.64 and 5.20%. The plant's
  learning alone is worth under a dollar.

## 4. The loop runs on ordinary cuts more than on premium products

| scenario | stage | cells, $/kg | sold, Mt a year: premium products, cuts, mince and processed | premium products' part of sales | chicken (organic): price against it, share of it | pork (heritage): price against it, share of it | beef (prime/wagyu): price against it, share of it | seafood (sushi): price against it, share of it |
|---|---|---|---|---|---|---|---|---|
| 1. Today | no learning | $56.99 | 0.06, 0.01, 0.00 | 89% | 5.39×, 0.5% | 4.38×, 0.8% | 1.56×, 3.8% | 2.00×, 2.6% |
| 1. Today | resting point | $49.54 | 0.08, 0.03, 0.00 | 71% | 4.76×, 0.8% | 3.87×, 1.2% | 1.37×, 5.1% | 1.77×, 3.5% |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no learning | $26.43 | 0.19, 1.57, 0.02 | 11% | 2.78×, 2.9% | 2.26×, 3.7% | 0.80×, 10.4% | 1.03×, 8.3% |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | resting point | $15.05 | 0.27, 7.36, 0.73 | 3% | 1.81×, 5.5% | 1.47×, 6.5% | 0.52×, 13.6% | 0.67×, 11.2% |
| 5. Plus engineered cells | no learning | $9.96 | 0.31, 13.16, 3.22 | 2% | 1.37×, 7.1% | 1.12×, 8.1% | 0.40×, 15.4% | 0.51×, 12.7% |
| 5. Plus engineered cells | resting point | $6.41 | 0.35, 19.52, 8.04 | 1% | 1.07×, 8.3% | 0.87×, 9.2% | 0.31×, 16.9% | 0.40×, 13.9% |

| scenario | learning | premium products sold at the scenario's own cost, Mt a year | membrane that needs, million m² a year | the switch, million m² a year | do premium products alone cross it? |
|---|---|---|---|---|---|
| 1. Today | central | 0.06 | 0.10 | 1.0 | no |
| 1. Today | no food-grade membrane supplier, slow plant learning | 0.06 | 0.10 | never | no |
| 1. Today | slow learning | 0.06 | 0.10 | 3.0 | no |
| 1. Today | fast learning | 0.06 | 0.10 | 0.3 | no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | central | 0.19 | 1.11 | 1.0 | yes |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | no food-grade membrane supplier, slow plant learning | 0.19 | 1.11 | never | no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | slow learning | 0.19 | 1.11 | 3.0 | no |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | fast learning | 0.19 | 1.11 | 0.3 | yes |
| 5. Plus engineered cells | central | 0.31 | 0.57 | 1.0 | no |
| 5. Plus engineered cells | no food-grade membrane supplier, slow plant learning | 0.31 | 0.57 | never | no |
| 5. Plus engineered cells | slow learning | 0.31 | 0.57 | 3.0 | no |
| 5. Plus engineered cells | fast learning | 0.31 | 0.57 | 0.3 | yes |

- **Premium products are where cultivated meat is closest to the price it competes with**: at Central's cost it is already cheaper
  than prime or wagyu beef (0.80 times its price) and level with sushi-grade seafood (1.03 times). But those markets are small
  (`premium_market_sizes.md`: about 1.2 Mt and 0.5 Mt a year), and they are only 11% of Central's sales.
- **Most of Central's early volume is ordinary cuts bought by the shoppers who like cultivated meat most**: 1.57 Mt a year of cuts
  and 0.02 Mt of mince, against 0.19 Mt of premium products. Most of it is beef steaks at 1.77 times their price (0.61 Mt) and
  fish fillets at 2.26 times (0.70 Mt). Since the cut cost was rebuilt on 2026-11-19 (a cut is 0.8 kg of cells, a plant-protein
  matrix and $2 of assembly beyond what mince pays), a cut costs less to make than mince whenever cells cost more than about $12
  a kilo, as Central's do.
  These buyers are the upper end of the spread of liking (`liking_spread.md`), not buyers of organic meat, who are the most hostile
  to it (`demand_heterogeneity_evidence.md`).
- **Premium products alone just reach the switch.** They need 1.11 million m² of membrane a year, 11% past the switch at 1.0, but
  short of a switch at 3 million. With all its sales Central needs 10.2 million and crosses by a wide margin. So the premium start is
  no longer needed; the cuts carry it. (Before the cut cost was rebuilt, premium products needed 0.76 million m² and fell short.)
- **The unlocking is real once the membrane is cheap.** At $15.05 a kilo of cells cultivated meat costs 0.52 times prime beef and
  0.67 times sushi-grade seafood, and its shares of them rise by about a third (prime beef 10.4% to 13.6%, sushi-grade seafood
  8.3% to 11.2%).
- **The loop reaches ordinary cuts, not mince.** At Central's resting point cultivated beef steak is 1.15 times the price of the
  animal one and fish fillet 1.47 times; chicken and pork cuts are still 2.6–2.9 times, and mince 2.2–4.9 times. Of its 8.36 Mt
  a year, 7.36 Mt are cuts and 0.73 Mt mince, for 2.49% of world meat. Only the best case's cells take the loop into mince and
  processed meat (8.04 Mt a year at its resting point).

## 5. How strong is the loop, and how well is that known?

| scenario | its own cost and share | first pass: the learning its own volume brings | resting point | part of the share gain from later rounds | resting point with demand anchored on premium meats (its own share there) |
|---|---|---|---|---|---|
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | $26.43, 0.53% | $16.22, 2.11% | $15.05, 2.49% | 19% | $15.45, 1.41% (0.48%) |
| 5. Plus engineered cells | $9.96, 4.97% | $6.50, 8.19% | $6.41, 8.30% | 3% | $6.55, 3.91% (2.60%) |

| input, across its range | 3. Plus cells selected to grow faster on the low-waste feed (Central): cells, share | 5. Plus engineered cells: cells, share |
|---|---|---|
| Membrane demand at which a food-grade supplier appears (300000 to 3e+06 m2 a year) | $15.05 to $15.16, 2.49% to 2.45% | $6.41 to $6.44, 8.30% to 8.27% |
| That supplier's first price (60 to 400 $/m2) | $15.05 to $15.58, 2.49% to 2.31% | $6.41 to $6.56, 8.30% to 8.12% |
| Membrane's price fall per doubling (0.1 to 0.28 per doubling) | $15.26 to $15.05, 2.42% to 2.49% | $6.47 to $6.41, 8.23% to 8.30% |
| Membrane's price floor (20 to 120 $/m2) | $15.04 to $15.49, 2.49% to 2.34% | $6.41 to $6.54, 8.31% to 8.15% |
| Plant's cost fall per doubling (0.03 to 0.18 per doubling) | $17.32 to $13.22, 1.81% to 3.19% | $7.04 to $6.41, 7.57% to 8.30% |
| Animal-cell tanks installed today (6500 to 11800 m3) | $14.91 to $15.31, 2.54% to 2.40% | $6.41 to $6.47, 8.30% to 8.23% |
| World meat, boneless (300 to 384 Mt a year) | $15.13 to $14.96, 2.46% to 2.52% | $6.43 to $6.41, 8.29% to 8.30% |

- **It is mostly one step, not a loop.** 81% of Central's gain in share, and 97% of the best case's, comes on the first
  pass: the volume each already sells is enough for the membrane switch. Later rounds, where cheaper cells sell more and more sales
  make cells cheaper again, add 19% and 3%. So the result does not rest on the strength of a feedback, which could not be
  measured; it rests on whether one event happens (a food-grade membrane supplier) and at what price.
- **The plant's learning rate matters most, then the food-grade supplier's first price and the membrane's floor**; the speed of the
  membrane's later fall matters little (table above). The switch's level matters little: a 3 million m² switch costs Central
  11 cents, and even with slow plant learning as well Central crosses on its own sales (section 3). Only with no food-grade supplier
  at all does it stay near its own cost.
- **The best case is sturdy on cost**: $6.4–7.0 across every input.
- **The share side is weaker than the cost side.** With the share taken from the single curve fitted to premium real meats
  (`premium_curve.md`) in place of the model's, the cells cost about the same ($15.45 and $6.55) but the best case's share is
  3.91%, not 8.30%, and Central's 1.41%, not 2.49%. At Central's own cost the two demand sides nearly agree (0.48% against 0.53%);
  they part as cells get cheaper, because the fitted curve gains less from a falling price.

## 6. The checks (2026-11-18)

**How big are the premium markets?** Several times smaller than the model's tables had them (`premium_market_sizes.md`): sushi-grade
seafood about 1.2 Mt a year (the table had 5.4) and prime or wagyu beef about 0.5 Mt (1.35). The tables were corrected. Premium
products alone no longer carry Central past the switch; premium buyers' purchases of ordinary meat do. (Since the cut cost was
rebuilt on 2026-11-19 premium products alone just reach the switch again, at 1.11 million m², but ordinary cuts carry most of the
volume; section 4.)

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

| premium product | price against it: at $26.43 a kilo of cells, at $15.05 | cultivated meat's share of it | percent more share per percent lower price |
|---|---|---|---|
| chicken (organic) | 2.78×, 1.81× | 2.93%, 5.48% | 1.5 |
| pork (heritage) | 2.26×, 1.47× | 3.67%, 6.49% | 1.3 |
| beef (prime/wagyu) | 0.80×, 0.52× | 10.40%, 13.60% | 0.6 |
| seafood (sushi) | 1.03×, 0.67× | 8.27%, 11.20% | 0.7 |
| history, along the demand curve (farmed salmon while still a premium product) | | | 1–1.5 |
| history, in total, with demand growth mixed in (salmon, US broilers, US catfish) | | | 1.3–4.1 |

- Farmed salmon is the closest case: 13 kt in 1980 to over 1 Mt in 1999 while its real price fell to a third (Asche, Bjørndal & Young
  2001, FT; Bjørndal & Tusvik 2017, FT). Early growth was largely "a move down along the demand schedule"; since 2000 nearly all growth
  has been demand shifting at flat prices. US broilers: real price −67% and consumption per person up fourfold, 1955–87 (Bishop &
  Christensen, USDA 1989, FT).
- **Where cultivated meat is still dearer than the premium product, it responds to price about as history did; where it is already
  cheaper, it responds less.** Against organic chicken and heritage pork, where cultivated meat costs 1.5–2.8 times their price, the
  response is in the upper part of farmed salmon's range along the demand curve (1.3–1.5 against 1–1.5). Against prime beef and
  sushi-grade seafood, which cultivated meat already matches or undercuts at Central's own cost, it is 0.6–0.7: its share of them
  levels off at 10–17% as it gets cheaper. Salmon's price fell while it was still the dearer, premium product, so the first pair is
  the closer comparison. None responds more strongly than the totals (1.3–4.1). (With every shopper alike the response was two to
  three times stronger. Before the cut cost was rebuilt on 2026-11-19 cultivated meat was dearer than all four at Central's cost,
  and the response was 1.0–1.8.)

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
- **The cut cost.** Since 2026-11-19 a cut costs 0.8 kg of cells, a $2 plant-protein matrix and $2 of assembly beyond what
  mince pays (`structuring_cost.md`). That more than quadrupled Central's sales at its own cost (0.42 to 1.78 Mt a year) and moved the loop's base from
  premium products to ordinary cuts. With the old rule (a full kilo of cells and a $6 scaffold) Central rested at $15.83 and 0.86%.
- **Still unknown:** an actual quote for a steam-tolerant food-grade module; a month-long run of animal cells at a quarter by volume
  above bench scale; the yearly area of perfusion filters sold today (estimated, not published); retail prices of the premium
  products by grade.
- **Resting points, not a path.** Learning is counted on yearly scale, not cumulative output, and nothing says who pays for the early
  years.
- **Judgement:** that a food-grade membrane at $250 a m² or less exists if cultivated meat sells 0.5 Mt a year: about 0.6. That
  learning of this kind takes the best case's cells to $7 or less, given the best case's cells exist: about 0.55. That Central's sales
  pass the switch with no outside push: about 0.7 (provisional, revised from 0.5 at the 2026-11-19 repin). Its own sales need ten
  times the switch's area, and the curve fitted to premium real meats gives nearly the same share at its own cost (0.48% against 0.53%).
  It rests on the rebuilt cut cost (`structuring_cost.md`) and on the keenest shoppers buying beef steaks at 1.8 times and fish fillets
  at 2.3 times their price. That learning takes Central above 1% of world meat: about 0.4 (provisional, revised from 0.15). Every
  case with a food-grade supplier puts it above 1% (1.48–3.27%), and so does the demand anchored on premium meats (1.41%); it fails
  if no supplier appears (0.59%), and the switch is itself only about 65%.

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
