# Cultivated meat: how far can it get? — results

*Findings of a cost and demand model. The default cost is what a company reports for its own process (SuperMeat
2024); the scenarios (`scenarios.py`) describe what has to go right for the cost to fall, from physics and published plant
costs (Humbird 2021). The [interactive explorer](https://pabloamc.github.io/Cultivated_meat/interactive.html) explains the
method in plain language and lets you change every assumption; [METHODS.md](METHODS.md) has the code-level detail.
Everything below reproduces from the code.*

## Summary

*Revised 2026-11-15, second time: the device that holds the cells back in a perfusion tank is now priced as a real one, a
hollow-fibre filter loop (TFF), sized on the liquid it must filter (`retention.py`, `research_notes/retention_devices.md`). The
model used to charge a hoped-for device at $89k per m³ of tank and nothing for its membranes. Every scenario costs more: the
central case $26.6 in place of $18.1, the best case $8.9 in place of $6.6. Earlier the same day: the cost is no longer one
number, "the floor". That number was a standard perfusion tank with no tank tricks, engineered cells and no lost runs. It is
kept as a labelled reference. The cost is now described by **scenarios**, each a preset of ten switches (kind of cells, growth
speed, plant, gas the cells tolerate, tank tricks, tank shape, runs lost, restart time, growth factors, medium price), with what
has to go right for it stated and every figure computed from the model (`scenarios.py`, `research_notes/cost_scenarios.md`).
On 2026-11-14 the cost side was rebuilt. The earlier anchor (Pasitka et al. 2024) turned out to count a kilogram that is mostly
liquid and to leave out the cost of the plant, so it is no longer used.*

All costs are per kg of real cells: about 70% water and 20% protein, like meat. Plant costs are in 2025 prices. "Share" is
the long-run share of the meat sold by weight, once cultivated meat is on every shelf and no longer feels new; it is not a
forecast of when.

| scenario | cells, $/kg (10th–90th percentile) | R vs $12 meat | share of world meat by weight, long run: median (10th–90th, cost and demand uncertain) | hardest thing it needs |
|---|---|---|---|---|
| Best case: everything works | **$8.9** ($9–12) | 1.16 | **4.4%** (1.3–11.2%) | needs genetic engineering |
| Central: selection and feed only, a food-grade plant | **$26.6** ($24–35) | 2.64 | **0.3%** (0.1–0.8%) | needs selection or adaptation of cells |
| Central, food-grade plant with shared medium | **$24.3** ($23–33) | 2.44 | **0.3%** (0.1–1.0%) | needs selection or adaptation of cells |
| Cautious: the best meat cells measured so far | **$39.0** ($35–49) | 3.66 | **0.1%** (0.0–0.3%) | needs a change of feed, process or plant |
| Reference: a standard perfusion tank, no tricks | $11.8 | 1.40 | 5.0% (point estimate) | needs genetic engineering |
| As a company reports (SuperMeat 2024) | $34.4 | 3.28 | 0.3% (point estimate) | a company's own report |

The bands: each scenario's switches are held, and the estimates behind it (plant cost, financing, the life of the filter
membranes, the upkeep share of respiration, medium price and loss rate) are allowed to be off; the share band lets demand vary too (4,000 draws).
**The share quoted for a scenario is the median of those draws.** It is not the share at the scenario's own point cost. The point cost sits below
the median cost, because the estimates behind it have more room to fall short than to improve. The share also rises steeply as the price falls, so the point
estimate is higher than the median (best case: 9.3% at the point cost, 4.4% median). Where a point estimate appears, it is labelled.

- **There is no single cost; it depends on what goes right.** In the **best case** everything works at once: cells engineered to
  make almost no waste, doubling every 24 hours, a food-grade plant with shared medium, a tank that clears CO₂ without more bubbles, no growth factors to buy.
  That costs about **$8.9/kg of cells** (1.16× everyday meat, $13.9 in the shop against $12), and cultivated meat takes **about 4%
  of world meat** in the long run. That is the median of draws in which cost and demand are uncertain, and 80% of the draws fall between 1% and 11%.
  At exactly $8.9 the point estimate is 9.3%, with 15% in the US and 27% in Europe. The best case needs genetic engineering of the cells and a plant
  nobody has built. It also needs a tank design nobody has run with animal cells: a column beside the tank that strips CO₂, 1 bar of extra pressure,
  and a tank whose liquid is 0.75 times as deep as wide. Without these tricks it costs $9.2 a kilo in a tank of the same shape. In the ordinary tall tank it costs $9.7.
- **The central scenario needs no genetic engineering.** Cells that make little waste because glutamine is replaced in the feed
  and the best lines are chosen, doubling every 36 hours, in a food-grade plant: about **$27/kg** (2.6×), or $24.3 in a
  food-grade plant with shared medium, and **~0.3% of world meat**. That is the median, and 80% of draws fall between 0.1% and 0.8%. At exactly $26.6 the point estimate is 0.5%
  (1.2% in the US, 3.6% in Europe). In a food-grade plant with shared medium the median is also about 0.3%. **Nobody has run the central tank design with animal cells.**
  It uses a column beside the tank that strips CO₂ without bubbles, 1 bar of extra pressure, pure oxygen recycled through the column, and a tank
  whose liquid is half as deep as wide. Without these tricks a kilo costs **$30.2** in a tank of the same shape (+$3.5). In the ordinary tall tank it costs **$34.5**.
  Doubling time is an explicit assumption, and 36 hours is a judgement. Low-waste meat-cell cultures have doubled in 43 to 54 hours. Only cultures fed
  glutamine have doubled in about 26 hours, and glutamine is what makes the waste. The author puts the odds of 24 hours at this waste level at about 10%.
  At 30 hours the central case costs $26.0, and at 24 hours $25.0. A 24-hour doubling is worth about $1.7 a kilo, much less than the kind of cells.
- **The cautious scenario uses what has been measured:** the best low-waste meat cells (43 hours), a food-grade plant, the most gas
  that has been run in tanks of this size (2 mm/s), 1% of runs lost a day with three weeks to restart, growth factors at 60% of
  Humbird's price, medium at $0.30/L. About **$39/kg** (3.7×), **~0.1% of world meat** (median; 0.0–0.3%; 0.2% at the point cost). It also uses a column, extra pressure and
  a squarer tank, and nobody has run these with animal cells. Without them it costs $53.4 a kilo, or $61.3 in the ordinary tall tank.
- **Holding the cells back costs more than the model used to assume.** Every scenario uses a 20 m³ tank in perfusion. A filter loop
  must clear the medium the bleed of cells does not carry out, and its membranes cost about $0.37 per litre they filter. The central
  cells need 28 litres of medium a kilo at 258 g/L, so the filter clears 24 litres a kilo: the membranes alone cost $8.8 a kilo. The
  reference case clears 2.9 litres a kilo and pays $1.0. A disc-stack separator on the outflow would cost about the same in the central
  case, through cells burst in it. Nobody has held animal cells in perfusion above about 4 m³ (`research_notes/retention_devices.md`).
- **No scenario reaches price parity.** Parity with $12 meat and a $5 markup needs $7/kg of cells. The best case costs $8.9, and its own
  band is $8.5–11.6. A plant as cheap as a yeast plant is not used in any scenario: nothing shows that animal cells can be grown that way.
- **What decides it** (from the central scenario, each switch moved alone to its best or its worst setting): the kind of cells
  (−$8.2 with engineered cells, +$77 with ordinary meat cells), the medium price (−$1.4 to +$8.6), growth factors (−$3.0 to +$7.0), tank
  tricks (up to +$3.5 if none work), growth speed (−$2.5 at 24 hours), the plant (−$2.3 with shared medium). The kind of cells matters
  most because waste sets the litres of medium a kilo, and each litre must also pass the filter. Some switches interact. The page ranks
  them around any scenario you choose.
- **At equal price,** once familiar, it wins **~49%** of the market if seen as real meat, **~10%** if not. Taste and
  the value shoppers put on "no slaughter" move this between ~12% and ~75%.
- **As a company reports its process, with capital counted,** cultivated chicken costs about **$34/kg of cells,
  ~3.3× everyday meat** ($39 in the shop). This is SuperMeat's 2024 process for 100% cell mass, from 10-litre runs
  scaled on paper to 25,000-litre tanks, with a yearly charge on the plant; the company's own figure, with
  depreciation only, is $29.5/kg. It is not peer reviewed. At that cost the share is **~0.3% of world meat** (0.6%
  in the US; Monte Carlo median over the cost and demand ranges 0.2%, 80% range 0.0–0.6%), nearly all of it
  premium beef and seafood.
- **Where:** beef and seafood. Chicken and pork stay dearer even in the best case. A few luxury products are beatable
  on price already, but tiny.
- **When:** these are long-run ceilings; adoption reaches 90% of its long-run share after about 30 years.

**For funders:** in order, better cells (low waste, fast-growing, robust: what the central case rests on), the price of medium and of growth
factors at production scale, tank tricks that clear CO₂ without bubbles, and a cheaper class of plant for animal cells.

## 1. Cost and the price ratio

*Read this section with one change in mind. Since 2026-11-15 the model prices the device that holds the cells back in a
perfusion tank as a hollow-fibre filter loop, with its membranes (`retention.py`). The tier table below and the tables from
the gas-exchange and cheap-plant studies were computed with the old hoped-for device ($89k per m³ of tank, no membranes), and
their scripts still reproduce them that way. With the filter loop, every perfusion case here costs more: about $0.4 a kilo for
the reference case, and about $0.37 for each litre of medium a kilo that the bleed of cells does not carry out. The summary
and the vessel section use the new device.*

| case | cells, $/kg | R vs $12 meat | source and status |
|---|---|---|---|
| cautious: pharma-style plant, cells at half the density, reported medium | $49.2 | 4.52 | physics-based plant cost (`floor_physics.py`); nearer to reported harvests |
| **as reported by a company, with a return on capital (default)** | **$34.4** | **3.28** | SuperMeat 2024; 10 L runs scaled on paper; not peer reviewed; its own figure with depreciation only is $29.5 |
| Humbird's fed-batch design, 2025 prices | $24.6 | 2.47 | a detailed design with efficient cells; not built |
| cautious reference: pharma-style plant, tanks drained and refilled | $19.4 | 2.03 | physics-based; efficient cells at this density not shown |
| reference case with first-plant financing | $14.1 | 1.59 | the row below at 23.6% of the plant's cost a year |
| **reference (what earlier versions called the floor): a standard perfusion tank, no tricks; no clean rooms, perfusion, efficient cells, food-industry financing** | **$11.5** | **1.38** | physics-based; each piece shown separately, never together; the cell-retention device is hoped for |
| microbial-class plant: the reference case in a plant as cheap as a yeast plant (no scenario assumes it) | **$6.6** | **0.97** | such plants exist for microbes; none built or costed for animal cells |
| rough lower bound | $3.1 | 0.68 | a bound, not a design |

**The default.** SuperMeat reports 30.5 L of medium per kg at under $0.50/L, $11.8/lb ($26.0/kg) without
depreciation and $13.4/lb ($29.5/kg) with it. Its kilogram is 100% cells at a realistic weight per cell. Every
other case here carries a yearly charge on the plant of 23.6% of its cost (Humbird's rate: return on capital,
maintenance, insurance), so the default does too: the company's running costs ($10.8/kg beyond the medium) plus
$8.3/kg, which assumes its depreciation is spread over 10 years. That gives $34.4/kg. Two cautions: it is a
company's claim, and its stated tank sizes, densities and bleed rate account for only about half of its stated
output, so the plant cost per kg cannot be checked. Humbird's independent design for efficient cells comes to
$25–46/kg in 2025 prices, and the published design analyses as a whole to about $18–65/kg with capital counted
(METHODS.md, "Other analyses").

**The cost is physics divided into engineering.** The plant's cost per kg is its cost per m³ of tank divided by
what a m³ produces in a year. Output is limited by how much oxygen and CO₂ a tank can exchange, which is set by
how much gas can be bubbled through it. The reference case uses 6 mm/s of gas, a rule of thumb that has not been tested at
this size and cell density; we put the odds that it works at about even, and at 5 mm/s the reference would be $13.1
(`research_notes/gas_flow_cap.md`). Plant cost per m³ comes from Humbird's design: about $910k with clean rooms, about $810k
with a sanitary hall in their place. Microbial fermentation plants are built for about $190k, which no scenario assumes
(METHODS.md, "The reference case's plant term").

**Financing matters as much as engineering.** Humbird charges 23.6% of a plant's cost a year: money at 7.5%
repaid in 10 years, plus 4% maintenance and 5% insurance. That fits a first plant, and the default and the
cautious tiers use it. His own report gives the food-processing sector's cost of capital as 5.4% and uses a
20-year life for a yeast plant; that makes the charge 17.3%. The scenarios are long-run cases set
against meat, a mature industry, so they use 17.3%. It is worth $2.6/kg in the reference case.

**How the tank is run matters less than the plant and the cells.** Perfusion is worth about $3–4/kg in the reference case
against tanks that are drained and refilled; removing clean rooms saves about a tenth of the plant cost; a
microbial-class plant nearly halves the reference. (How the tank is run, and other vessel types, are the subject of
later work: `research_notes/page_structure.md`.)

The medium and the plant matter most; no single lever reaches parity on its own (from the default: the reference
plant cost gives R ≈ 2.50, medium at $0.20/L 2.52, efficient cells 2.33).

```
basic product vs commodity meat ($12/kg), Monte Carlo over the cost inputs (N=20,000):
  price ratio R:   P50 = 3.27   80% CI [2.51, 4.16]   90% CI [2.33, 4.43]
  long-run share:  P50 = 0.0%   80% CI [0.0, 0.9]
  0% of draws reach parity (R ≤ 1)
```

The median is close to the default 3.28: the plant-cost range is wider on the high side (reported harvests are
less dense than the reference case assumes), while the medium price and cell efficiency can improve on the report. The
Monte Carlo does not include the scenarios or a yeast-class plant.

**What the tricks do, and what the cells decide.** Research notes size ways round the tank's limits
(`research_notes/gas_exchange_study.md`, `waste_tricks_sizing.md`); `floor_physics.explore` carries them as
levers, and the page's panel shows each limit as a bar. Each trick and each kind of cell is tagged by what it
needs: **feed or process** (no change to the cells), **selection or adaptation** (cells chosen or adapted, not
engineered; easier to regulate), or **genetic engineering**. Every tank trick here is feed or process.

Cost per kg of cells in the reference tank's food-grade plant, in brackets with runs lost to contamination at 0.2% a day
(pharma's rate, 14-day restart); then the yeast-style plant, in brackets at 2.2% a day (the top of what a survey
of makers implies; 0.6% a day sits between); then the density, what binds, and litres of medium per kg.

*All tricks, all cells:*

| cells | sparger only | sparger, fat in the feed, oxygen held at 0.08 | packed column on a loop | column with oxygen sweep, 1 bar gauge |
|---|---|---|---|---|
| the engineered cells [genetic engineering] | $11.5 ($11.7); yeast-style $6.6 ($7.7); 120 g/L CO₂, 11 L/kg | $9.9 ($10.1); yeast-style $6.0 ($6.9); 150 g/L CO₂, 11 L/kg | $8.6 ($8.8); yeast-style $5.5 ($6.3); 189 g/L mixing, 11 L/kg | $7.3 ($7.4); yeast-style $5.0 ($5.6); 258 g/L thickness, 11 L/kg |
| best shown in meat cells (bovine, glutamine replaced) [feed or process] | $17.5 ($17.8); yeast-style $10.7 ($12.5); 154 g/L CO₂, 28 L/kg | $15.3 ($15.5); yeast-style $9.8 ($11.3); 192 g/L CO₂, 28 L/kg | $13.5 ($13.7); yeast-style $9.2 ($10.5); 242 g/L mixing, 28 L/kg | $13.1 ($13.3); yeast-style $9.1 ($10.3); 258 g/L thickness, 28 L/kg |
| ordinary meat cells (bovine) | $31.1 ($31.4); yeast-style $26.0 ($27.8); 124 g/L CO₂, 140 L/kg | $29.5 ($29.7); yeast-style $25.4 ($27.0); 155 g/L CO₂, 140 L/kg | $28.1 ($28.3); yeast-style $24.9 ($26.4); 195 g/L mixing, 140 L/kg | $26.9 ($27.1); yeast-style $24.5 ($25.7); 258 g/L thickness, 140 L/kg |

*Without genetic engineering.* The engineered cell is replaced by what selection and feed alone have
shown: ammonia 0.14 mol/kg with glutamine replaced, lactate 0.39 per glucose as in adapted CHO cells, at the
engineered cell's 24-hour doubling:

| cells | sparger only | sparger, fat in the feed, oxygen held at 0.08 | packed column on a loop | column with oxygen sweep, 1 bar gauge |
|---|---|---|---|---|
| the engineered cells by selection and feed only [selection or adaptation] | $14.0 ($14.2); yeast-style $9.1 ($10.2); 120 g/L CO₂, 28 L/kg | $12.4 ($12.6); yeast-style $8.5 ($9.4); 150 g/L CO₂, 28 L/kg | $11.1 ($11.3); yeast-style $8.0 ($8.8); 189 g/L mixing, 28 L/kg | $9.8 ($9.9); yeast-style $7.5 ($8.2); 258 g/L thickness, 28 L/kg |
| best shown in meat cells (bovine, glutamine replaced) [feed or process] | $17.5 ($17.8); yeast-style $10.7 ($12.5); 154 g/L CO₂, 28 L/kg | $15.3 ($15.5); yeast-style $9.8 ($11.3); 192 g/L CO₂, 28 L/kg | $13.5 ($13.7); yeast-style $9.2 ($10.5); 242 g/L mixing, 28 L/kg | $13.1 ($13.3); yeast-style $9.1 ($10.3); 258 g/L thickness, 28 L/kg |
| ordinary meat cells (bovine) | $31.1 ($31.4); yeast-style $26.0 ($27.8); 124 g/L CO₂, 140 L/kg | $29.5 ($29.7); yeast-style $25.4 ($27.0); 155 g/L CO₂, 140 L/kg | $28.1 ($28.3); yeast-style $24.9 ($26.4); 195 g/L mixing, 140 L/kg | $26.9 ($27.1); yeast-style $24.5 ($25.7); 258 g/L thickness, 140 L/kg |

"Best shown in meat cells" is bovine cells with glutamine replaced: 0.14 mol of ammonia per kg and a 43-hour
doubling (Hubalek 2023); "ordinary" is the same cells with glutamine, 0.70 mol and 26 hours. Both take chicken
cells' lactate yield (1.05 per glucose, Pasitka 2024) at 0.84 mol of glucose per kg. "Fat in the feed" means
the cells take all their lipid from the medium instead of making it from glucose; making lipid from glucose
gives off CO₂ without using oxygen, and on Humbird's cell that is why CO₂ made per oxygen used is 1.20 rather
than 1.0 (fed, 0.97; a carbon balance, the note's section 10). Holding dissolved oxygen at 0.08 mmol/L (38% of
air saturation, a usual pharma setpoint) in place of the 0.28 the standard tank's oxygen supply implies widens the
oxygen driving force by about a fifth; it matters only where oxygen binds.

Reading the tables: the tricks take the engineered cells from $11.5 to $7.3, about the parity mark, and the
cheap plant to $5.0. Without genetic engineering the engineered cell needs 28 litres of medium per kg (ammonia
sets it), and the tricks take it from $14.0 to $9.8 ($7.5 in a yeast-style plant). With cells that have
actually been measured, ammonia sets the medium and the tank tricks are worth much less: the cells decide the
cost before the tank does. Losing runs adds $0.1–2.5 per kg. The loss model counts the lost time and the
tankful lost with each failure; it does not yet count a failed restart, and long continuous runs are more
exposed per run than short batches.

When the cells tolerate only a capped gas flow, the cheapest combination of tank shape, column and headspace
pressure (`gas_exchange.cheapest_tricks`; the sparger runs at its cap, a squatter tank pays for its steel):

| gas cap | food-grade plant, sparger only | cheapest combination, any circulation | the same, keeping the loop within the tested passes and the safe pH exposure | yeast-style: sparger only / any / within limits |
|---|---|---|---|---|
| 1 mm/s | $52.9 | $7.66: column with oxygen sweep, 1 bar gauge; **85 passes an hour** | $17.2: column for CO₂, liquid twice as deep as wide, 1 bar gauge; 9 passes | $23.6 / $5.40 / $9.2 |
| 2 mm/s | $28.0 | $7.52: the same; **61 passes** | $11.7: column for CO₂, liquid as deep as wide, 1 bar gauge; 11 passes | $13.4 / $5.26 / $6.8 |
| 4 mm/s | $15.6 | $7.33: the same; **29 passes** | $8.5: column for CO₂, liquid half as deep as wide, 1 bar gauge; 7 passes | $8.3 / $5.07 / $5.3 |
| 6 mm/s | $11.5 | $7.20: column for CO₂ only, 1 bar gauge; **22 passes** | $7.45: the same, liquid 0.75 as deep as wide; 10 passes | $6.6 / $4.91 / $4.91 (no column) |

Passes are tank volumes pumped through the column an hour. Dense cultures have been pumped through fibres at up
to about 15-24 an hour for weeks, at 1-4 litres (Clincke 2013; a vendor note); nothing beyond that is tested.
Culture leaving the column stays alkaline (+0.26 pH at 55 mbar) until it is back in the tank, so the share of
the culture that is alkaline grows with the passes. The safe limit used here is the 55 mbar, 0.5 m3 design that
the gas-exchange note found 3 to 6 times below an exposure that slowed CHO cells (Paul 2020). At 22 passes the
loop is 1.9 times that limit (about half the harmful exposure); at 61 passes, 5.2 times (1.5 times the harmful
one). **Within those limits the reference case depends on the gas the cells tolerate again**: $7.45 at 6 mm/s, $8.5 at
4, $11.7 at 2, $17.2 at 1. In the cells-by-tank tables above, the last column ("column with oxygen sweep, 1 bar
gauge") runs at 22 passes an hour for the engineered cells, beyond the tested range. None of the tricks has been
tried with meat cells.

### If perfusion cannot be run at 20 m³

Every scenario uses a perfusion tank, which nobody has run above about 4 m³. Without cell retention a tank is capped by waste.
Central costs **$40–44** a kilo in a stirred tank in fed-batch or fill-and-draw at the model's own cap (62 g/L), and **$90–97** at
the 27 g/L reported for meat cells at 20 m³, against $26.64. The best case goes from $8.95 to $13.22 (or $41). The food-grade plant
with shared medium cushions it most: $24.34 to $28.22. We put about 65% on perfusion failing at 20 m³ for the best case and
Central (`research_notes/no_perfusion_downside.md`).

### Vessel types and operating modes

A stirred tank and perfusion are not alternatives: one is a vessel, the other a way of running it. `vessels.py` changes only
those two and holds the rest (research_notes/vessels_and_modes.md has both grids, with sources).

| reference case, $/kg | Batch | Fed-batch | Fill-and-draw | Chemostat | Perfusion |
|---|---|---|---|---|---|
| Stirred tank, 20 m3 | 62.95 | 18.20 | 17.81 | 33.67 | **11.84** |
| Airlift, 20 m3 | 59.97 | 20.03 | 19.59 | 32.10 | 14.11 |
| Single-use bag, 5 m3 | 1,078 | 292.80 | 38.18 | 74.50 | 17.23 |
| Packed bed, 65 L | 3,730 | as batch | not possible | not possible | 3,726 |
| Hollow fibres, 0.5 L | 610,043 | as batch | not possible | not possible | 610,039 |

In the central scenario the stirred tank costs $109.07, $45.29, $48.95, $96.32 and $26.64 across the same modes. Perfusion
includes the filter loop that holds the cells back (`retention.py`); the other modes need no such device.

- Perfusion in a stirred tank is the cheapest combination in both settings. Nobody has run animal cells in perfusion above
  about 4 m3.
- Fed-batch and fill-and-draw, which run at 20 m3 today, cost about $18 in the reference case and $45-49 in the central
  scenario. The central cells make more ammonia, and a culture that is not washed out stops at 62 g/L. These costs assume
  62-92 g of cells a litre. Nobody has shown that density for meat cells at this size: the one 20 m3 plant for meat cells
  reports harvests of about 27 g/L.
- An airlift costs about what a stirred tank costs when waste is not washed out. In perfusion its tall shape clears less CO2.
- A single-use bag pays for a bag each run; it comes close to steel only in perfusion.
- Packed beds and hollow fibres cost thousands of dollars a kilo as built. A 20 m3 bed at a stirred tank's price, with free
  carriers, still costs $42.19 in the reference case: it is seeded thin and emptied every run.

## 2. What share a price buys

| if cultivated meat, at equal price and once familiar… | share |
|---|---|
| tastes as good and is seen as real meat | **~49%** |
| tastes a little worse (0.8) / noticeably worse (0.6) | ~26% / ~12% |
| tastes as good, and “no slaughter” matters (0.5 / 1.0 / 1.5) | ~59% / ~68% / ~75% |
| tastes as good but isn't seen as real meat | ~10% |

At first contact it gets ~6% (a US choice experiment found ~5%). Against $12 everyday meat (US, long run) it
gets ~21% in the reference case (1.4× the price) and next to nothing at the reported cost (3.3×).
Checks: adding cultivated takes 44 points from conventional meat and only 0.6 from plant-based; the same model
predicts ~15% for plant-based milk, close to reality (a weak test, since milk's inputs are set by hand).

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

κ is how many times more price-sensitive a cultivated product is than meat as a whole. At the old default of 4
the model over-predicted these about sixfold. The best fit is κ = 10; the one choice experiment on cultivated
meat (Lusk 2020) allows up to about 8.8. The default is now 8.5: the typical miss is a factor of 2.6. To make
this possible κ was changed to act only on cultivated's price difference from the conventional meat beside it,
so it moves nothing at equal price and leaves the rest of the calibration as published. What remains wrong: the
model still over-predicts at small premiums and under-predicts at large ones. Real premium buyers look like a
small group that pays whatever the premium, which one number cannot capture.

## 3. By type of meat (US)

```
                            default cost        reference cost
  meat type          $/kg    R     share        R     share
  chicken mince        5    7.87    0.0%       3.30    0.3%
  beef mince          11    3.58    0.0%       1.50   18.1%
  beef steak          20    2.27    0.8%       1.13   29.4%
  wagyu (premium)     45    1.01   17.9%       0.50   39.1%
  pork (processed)     8    4.92    0.0%       2.06    4.6%
  seafood fillet      24    1.89    2.1%       0.94   44.6%
  sushi-grade (prem.) 40    1.13   14.5%       0.56   34.4%
  TOTAL by weight: default 0.6%, in the reference case 10.0%
```

At the default cost only products priced like wagyu and sushi-grade fish sell; their markets are small. In the
reference case, seafood, beef cuts and beef mince lead; pork is under 5% and chicken close to zero.

**With the cells that have been published.** The reference case assumes an efficient model cell for every species. Using
each species' published doubling time and cell size in the same plant, and for fish a lower tolerance of CO₂
(chicken and turkey cost 1.75× as much, beef 1.3×, seafood 1.8×; no data for pork), the US total in the reference case's
plant is 5.5%, not 10% (world 2.7%, Europe 14%). The cell data are thin (METHODS.md, "Species costs in the
market model").

**Seafood rests on an untested assumption.** Seafood is the category closest to price parity in the reference case,
with a 45% share for fillets. That assumes fish cells tolerate as much dissolved CO₂ as pharma cells do. Fish
live with about 2–4 mbar of CO₂ in their blood, against about 50 in mammals, and nobody has measured how fish
cells grow against CO₂. If they tolerate 50 mbar, not 100, fish cells cost $21/kg in the reference tank's plant and the
fillet share falls to 16%. No shrimp cell line exists at all.

**Animals.** A tonne of cultivated meat, sold where the model says it sells, spares about 34 land animals in
the reference case (US) and about 18 at the reported cost; a tonne of the average US meat mix is about 250. Almost none
of it is chicken, where the animals are. Seafood animals are not counted, and seafood is about a third of
sales in the reference case.

## 4. By region

```
total cultivated penetration of meat (N=30,000), 80% CI [P10, P90]:
  region   income/cap   by VOLUME (impact)        by VALUE ($ market)
  Europe    $62k        P50  0.9%  [0.2,  3.9]    P50  2.0%  [ 0.5,  7.9]  <- easiest (rich + priciest meat)
  US        $86k        P50  0.4%  [0.1,  1.5]    P50  1.1%  [ 0.3,  3.7]
  Global    $24k        P50  0.2%  [0.0,  0.6]    P50  0.6%  [ 0.1,  2.0]
  China     $27k        P50  0.3%  [0.1,  1.1]    P50  1.1%  [ 0.3,  3.7]
  Brazil    $22k        P50  0.0%  [0.0,  0.2]    P50  0.1%  [ 0.0,  0.5]
  India     $11k        P50  0.0%  [0.0,  0.1]    P50  0.1%  [ 0.0,  0.4]
  Nigeria    $6k        P50  0.0%  [0.0,  0.0]    P50  0.0%  [ 0.0,  0.1]  <- hardest (cheap meat + price-sensitive)
```

Dear meat and rich shoppers make Europe easiest; cheap meat and price-sensitive shoppers make low-income regions
hardest. This table is at the reported cost. The point estimates there are Global 0.3%, Europe 1.3%, US 0.6%; the band
samples κ from 4 to 11 and plant costs from the reference to the cautious case. World beef is priced by consumption-weighted country prices (METHODS.md, "World beef price").
Against sushi-grade salmon, a structured product is at or below parity in 17% of draws, but structuring cost is
unmeasured.

## 5. Entry points, and timing

Luxury products compared at their everyday grade (farmed salmon, crossbred wagyu) are already beatable: foie gras,
bluefin tuna, sea urchin, wagyu. Lobster is close (R ≈ 1.1). Each is a small market. Commodity beef, pork and chicken,
where the volume is, stay out of reach even in the reference case. Foie gras stands out: unstructured, expensive, and
increasingly banned on welfare grounds.

From a near-zero start, cultivated meat reaches 90% of its long-run share after about 30 years (16 to 74 across
the plausible speeds at which wariness fades), in the reference case as at the reported cost. Current wariness (surveys: 5–60%) sets the speed, not the ceiling.

## 6. What to fund

1. **Better cells:** lines that make little ammonia and lactate, grow fast and reach high density, on a low-waste feed. The kind of
   cells is the largest switch in every scenario (the central case costs $18 with selected cells, $14 with engineered ones,
   and $53 with ordinary meat cells). Low waste and fast growth have each been shown, never together in
   one culture; a culture that does both is the single most useful measurement.
2. **The price of medium and of growth factors at production scale:** verify the $0.20/L reports and the price of growth factors on a
   stated mass basis. Together they are worth more than any plant or tank choice in the central case.
3. **Tank tricks that clear CO₂ without bubbles** (a column on a pumped loop, pressure, recycled oxygen) and **the gas flow cells
   tolerate:** calculated, never tried with meat cells. Without them the central case costs $5 more.
4. **A cheaper class of plant for animal cells:** a food-grade plant with shared medium (no clean room, shared medium line, bought oxygen) is worth $2–3/kg, and
   nobody has built one. A plant as cheap as a yeast plant is not counted: nothing shows animal cells can be grown that way.
5. **A way to hold cells back in large tanks:** perfusion stops at about 2,000 litres today because of filters. Every scenario prices a
   device nobody has built at what one study hopes it will cost.
6. **Contamination is not the main obstacle to a cheaper plant, on this model:** the food-grade plant with shared medium stays cheaper than a sterile one until
   it loses a run about every 28 days. Measured loss rates in food-grade tanks would test this.
7. **Open, comparable data:** cost claims per kg of dry matter or protein, with capital included (METHODS.md, "A
   checklist for cost claims"). Most published analyses leave out all or part of the cost of capital.
7. **Structuring cost:** the biggest unmeasured number; it gates premium seafood.

A meat tax also works: raising conventional prices 25% lowers R as much as a 20% cut in every cost. Most of these
are public goods that industry underfunds.

**The one working plant.** Vow grows animal cells in a food-grade 20,000-litre tank with no clean room,
drained and refilled, at an output that implies about 27 g of cells per litre. Reconstructed in the model, that
operation costs about $28/kg in a yeast-style plant and over $70/kg in a plant at Humbird's cost, so the cheap
class of plant is probably what it runs. It shows that food-grade tanks work for short runs. It does not show
the density or the weeks-long perfusion runs the reference case assumes (METHODS.md, "A working plant as a reference
point").

**How the physics fares against reported runs.** Fed the cells and vessels of published runs, the model is
cautious about how dense a culture a vessel can hold (a small vessel has held twice its limit), and optimistic
about medium (real perfusion runs used 1.2 to 2.8 times more) and about output in practice (the one working
20 m³ plant makes under half of what the model's efficient cells would). It also flags two reports whose own
numbers do not add up (METHODS.md, "Back-test against reported runs").

## 7. What would change the conclusions

- **Up:** animal cells grown in a plant built like a microbial fermentation plant; efficient cells shown at pilot
  scale with a full mass balance; perfusion with a scalable way to hold cells back at 20,000 litres; medium below
  $0.30/L confirmed at scale.
- **Down:** if the reported figures do not survive review or scale-up; cells that reach only half the density in
  a pharma-style plant (R ≈ 4.5); frequent contamination with slow restarts (METHODS.md, "Losing runs").
- **Demand above parity is the weakest part.** It now rests on six premium products and one choice experiment,
  and the model reproduces the six only to within a factor of about 2.6. Shoppers who differ in price
  sensitivity would fit better; there is not yet enough data to pin that down.
- **What rests on one source.** The default is one company's report, with a capital charge that assumes a
  10-year depreciation period (20 years would add $8/kg). The reference case's plant costs are one engineer's design
  (Humbird 2021) in 2025 prices. Neither has been reproduced.
- **Demand:** acceptance and the value of “no slaughter” can't be measured before launch; the model carries the
  full range (10% to 75% at equal price).

Figures: `python report_figures.py` (cost vs inputs, cost waterfall, share tornado, share vs price, timing paths,
penetration by type and region). Parameters and sources: `python inputs.py`.
