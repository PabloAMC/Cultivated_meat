# Cultivated meat: how far can it get? — results

*Findings of a cost and demand model. The default cost is what a company reports for its own process (SuperMeat
2024); the scenarios (`scenarios.py`) describe what has to go right for the cost to fall, from physics and published plant
costs (Humbird 2021). The [interactive explorer](https://pabloamc.github.io/Cultivated_meat/interactive.html) explains the
method in plain language and lets you change every assumption; [METHODS.md](METHODS.md) has the code-level detail.
Everything below reproduces from the code.*

## Summary

*Revised 2026-11-15, third time: three costs earlier versions left out are now counted. (1) The bubble protectant
(poloxamer 188, 2 g per litre), which leaves with every litre of medium: about $0.06 a litre at an assumed $30 a kilo
(only catalogue prices, $230–260, were found). (2) Antifoam's cut to the oxygen the sparger delivers, taken at the middle
of the reported range (a quarter lost; it was none). In the central and cautious cases oxygen now limits the density.
(3) Oxygen bought by the yeast-style plant class, whose price has no oxygen unit. The plant ladder now uses the model's own
cost for its perfusion rows, so the cost-side input `plant_floor` moved from $9.8 to $10.8. Every scenario costs more:
the central case $29.9 in place of $26.6, the best case $9.7 in place of $8.9. Earlier the same day the device that holds
the cells back was priced as a real hollow-fibre filter loop (TFF, `retention.py`, `research_notes/retention_devices.md`),
in place of a hoped-for device at $89k per m³ with no membranes. Earlier still the cost stopped being one number, "the
floor": it is described by **scenarios**, each a preset of ten switches (kind of cells, growth speed, plant, gas the cells
tolerate, tank tricks, tank shape, runs lost, restart time, growth factors, medium price), with what has to go right for
it stated and every figure computed from the model (`scenarios.py`, `research_notes/cost_scenarios.md`). On 2026-11-14 the
cost side was rebuilt. The earlier anchor (Pasitka et al. 2024) turned out to count a kilogram that is mostly liquid and to
leave out the cost of the plant, so it is no longer used.*

All costs are per kg of real cells: about 70% water and 20% protein, like meat. Plant costs are in 2025 prices. "Share" is
the long-run share of the meat sold by weight, once cultivated meat is on every shelf and no longer feels new; it is not a
forecast of when.

| scenario | cells, $/kg (10th–90th percentile) | R vs $12 meat | share of world meat by weight, long run: median (10th–90th, cost and demand uncertain) | hardest thing it needs |
|---|---|---|---|---|
| Best case: everything works | **$9.7** ($9–12) | 1.23 | **3.8%** (1.2–9.7%) | needs genetic engineering |
| Central: selection and feed only, a food-grade plant | **$29.9** ($27–38) | 2.91 | **0.2%** (0.1–0.6%) | needs selection or adaptation of cells |
| Central, food-grade plant with shared medium | **$26.8** ($25–35) | 2.65 | **0.3%** (0.1–0.7%) | needs selection or adaptation of cells |
| Cautious: the best meat cells measured so far | **$43.8** ($39–54) | 4.07 | **0.1%** (0.0–0.2%) | needs a change of feed, process or plant |
| Reference: a standard perfusion tank, no tricks | $12.5 | 1.46 | 4.3% (point estimate) | needs genetic engineering |
| As a company reports (SuperMeat 2024) | $34.4 | 3.28 | 0.3% (point estimate) | a company's own report |

The bands: each scenario's switches are held, and the estimates behind it (plant cost, financing, the life of the filter
membranes, the upkeep share of respiration, medium price and loss rate) are allowed to be off; the share band lets demand vary too (4,000 draws).
**The share quoted for a scenario is the median of those draws.** It is not the share at the scenario's own point cost. The point cost sits below
the median cost, because the estimates behind it have more room to fall short than to improve. The share also rises steeply as the price falls, so the point
estimate is higher than the median (best case: 7.9% at the point cost, 3.8% median). Where a point estimate appears, it is labelled.

- **There is no single cost; it depends on what goes right.** In the **best case** everything works at once: cells engineered to
  make almost no waste, doubling every 24 hours, a food-grade plant with shared medium, a tank that clears CO₂ without more bubbles, no growth factors to buy.
  That costs about **$9.7/kg of cells** (1.23× everyday meat, $14.7 in the shop against $12), and cultivated meat takes **about 4%
  of world meat** in the long run. That is the median of draws in which cost and demand are uncertain, and 80% of the draws fall between 1% and 10%.
  At exactly $9.7 the point estimate is 7.9%, with 14% in the US and 25% in Europe. The best case needs genetic engineering of the cells and a plant
  nobody has built. It also needs a tank design nobody has run with animal cells: a column beside the tank that strips CO₂, 1 bar of extra pressure,
  and a tank whose liquid is as deep as it is wide. Without these tricks it costs $10.2 a kilo in a tank of the same shape. In the ordinary tall tank it costs $10.4.
- **The central scenario needs no genetic engineering.** Cells that make little waste because glutamine is replaced in the feed
  and the best lines are chosen, doubling every 36 hours, in a food-grade plant: about **$30/kg** (2.9×), or $26.8 in a
  food-grade plant with shared medium (Humbird's plant without a clean hall, an oxygen plant or eight seed tanks, and with one
  medium line for all the tanks; the shared line is the smallest of these savings), and **~0.2% of world meat**. That is the median, and 80% of draws fall between 0.1% and 0.6%. At exactly $29.9 the point estimate is 0.4%
  (0.9% in the US, 2.3% in Europe). In a food-grade plant with shared medium the median is about 0.3%. **Nobody has run the central tank design with animal cells.**
  It uses a column beside the tank that strips CO₂ without bubbles, 1 bar of extra pressure, and a tank whose liquid is as deep as it is wide.
  Oxygen, not CO₂, now limits it, at 177 g/L: antifoam is taken to cost a quarter of the sparger's oxygen transfer, which is worth $1.8 a kilo here.
  Without the tricks a kilo costs **$33.5** in a tank of the same shape (+$3.6). In the ordinary tall tank it costs **$36.2**.
  Doubling time is an explicit assumption, and 36 hours is a judgement. Low-waste meat-cell cultures have doubled in 43 to 54 hours. Only cultures fed
  glutamine have doubled in about 26 hours, and glutamine is what makes the waste. The author puts the odds of 24 hours at this waste level at about 10%.
  At 30 hours the central case costs $28.7, and at 24 hours $27.4. A 24-hour doubling is worth about $2.6 a kilo, much less than the kind of cells.
- **The cautious scenario uses what has been measured:** the best low-waste meat cells (43 hours), a food-grade plant, the most gas
  that has been run in tanks of this size (2 mm/s), 1% of runs lost a day with three weeks to restart, growth factors at 60% of
  Humbird's price, medium at $0.30/L. About **$44/kg** (4.1×), **~0.1% of world meat** (median; 0.0–0.2%; 0.1% at the point cost). It also uses a column and extra pressure,
  and nobody has run these with animal cells. Without them it costs $63.0 a kilo.
- **Holding the cells back costs more than the model used to assume.** Every scenario uses a 20 m³ tank in perfusion. A filter loop
  must clear the medium the bleed of cells does not carry out, and its membranes cost about $0.37 per litre they filter. The central
  cells need 28 litres of medium a kilo at 177 g/L, so the filter clears 22 litres a kilo: the membranes alone cost $8.2 a kilo. The
  reference case clears 2.8 litres a kilo and pays $1.0. A disc-stack separator on the outflow would cost about the same in the central
  case, through cells burst in it. Nobody has held animal cells in perfusion above about 4 m³ (`research_notes/retention_devices.md`).
- **The bubble protectant is a real cost.** At 2 g/L it is 22 g a kilo of cells in the reference and best cases and 56 g in the central and
  cautious cases: $0.7 and $1.7 a kilo at the assumed $30 a kilo, $5.6 and $14 at the catalogue price. A bulk quote would settle it.
- **Company cost claims are operating cost; the scenarios include the plant.** On operating cost alone the central cells cost
  $13.7–14.0 a kilo in a tank run as Vow runs its 20 m³ tank, inside the $10–15 an investor reports for several companies. The plant
  charge is the difference (section 1, "Against what companies report").
- **No scenario reaches price parity.** Parity with $12 meat and a $5 markup needs $7/kg of cells. The best case costs $9.7, and its own
  band is $9.2–12.2. A plant as cheap as a yeast plant is not used in any scenario: nothing shows that animal cells can be grown that way.
- **What decides it** (from the central scenario, each switch moved alone to its best or its worst setting): the kind of cells
  (−$9.6 with engineered cells, +$84 with ordinary meat cells), the medium price (−$4.0 at an aspirational $0.05 a litre to +$8.6),
  growth factors (−$3.0 to +$7.0), the gas the cells tolerate (−$2.0 at 6 mm/s, +$5.4 at 2), tank tricks (up to +$3.6 if none work),
  the plant (−$3.1 with shared medium), growth speed (−$2.6 at 24 hours). The kind of cells matters
  most because waste sets the litres of medium a kilo, and each litre must also pass the filter and carries protectant. Some switches interact. The page ranks
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

*Since 2026-11-15 the perfusion rows below are the model's own `explore()`: the hollow-fibre filter loop with its membranes,
the bubble protectant, antifoam's cut to oxygen transfer, and the oxygen a yeast-style plant must buy. The other rows are
earlier designs and cases and do not change.*

| case | cells, $/kg | R vs $12 meat | source and status |
|---|---|---|---|
| cautious: pharma-style plant, cells at half the density, reported medium | $49.2 | 4.52 | physics-based plant cost (`floor_physics.py`); nearer to reported harvests |
| **as reported by a company, with a return on capital (default)** | **$34.4** | **3.28** | SuperMeat 2024; 10 L runs scaled on paper; not peer reviewed; its own figure with depreciation only is $29.5 |
| Humbird's fed-batch design, 2025 prices | $24.6 | 2.47 | a detailed design with efficient cells; not built |
| cautious reference: pharma-style plant, tanks drained and refilled | $19.4 | 2.03 | physics-based; efficient cells at this density not shown |
| reference case with first-plant financing | $14.8 | 1.65 | the row below at 23.6% of the plant's cost a year |
| **reference (what earlier versions called the floor): a standard perfusion tank, no tricks; no clean rooms, perfusion, efficient cells, food-industry financing** | **$12.5** | **1.46** | physics-based; each piece shown separately, never together; a hollow-fibre filter loop holds the cells back, never run at 20 m³ |
| microbial-class plant: the reference case in a plant as cheap as a yeast plant (no scenario assumes it), buying its oxygen | **$8.0** | **1.08** | such plants exist for microbes; none built or costed for animal cells |
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
this size and cell density; we put the odds that it works at about even, and at 5 mm/s the reference would be $13.4
(`research_notes/gas_flow_cap.md`). Plant cost per m³ comes from Humbird's design: about $910k with clean rooms, about $810k
with a sanitary hall in their place. Microbial fermentation plants are built for about $190k, which no scenario assumes
(METHODS.md, "The reference case's plant term").

**Financing matters as much as engineering.** Humbird charges 23.6% of a plant's cost a year: money at 7.5%
repaid in 10 years, plus 4% maintenance and 5% insurance. That fits a first plant, and the default and the
cautious tiers use it. His own report gives the food-processing sector's cost of capital as 5.4% and uses a
20-year life for a yeast plant; that makes the charge 17.3%. The scenarios are long-run cases set
against meat, a mature industry, so they use 17.3%. It is worth $2.3/kg in the reference case.

**How the tank is run matters less than the plant and the cells.** Perfusion is worth about $6/kg in the reference case
against tanks that are drained and refilled (the vessel grid below); removing clean rooms saves about a tenth of the plant cost; a
microbial-class plant cuts the reference by about a third. (How the tank is run, and other vessel types, are the subject of
later work: `research_notes/page_structure.md`.)

The medium and the plant matter most; no single lever reaches parity on its own (from the default: the reference
plant cost gives R ≈ 2.59, medium at $0.20/L 2.52, efficient cells 2.33).

```
basic product vs commodity meat ($12/kg), Monte Carlo over the cost inputs (N=20,000):
  price ratio R:   P50 = 3.29   80% CI [2.55, 4.17]   90% CI [2.37, 4.44]
  long-run share:  P50 = 0.0%   80% CI [0.0, 0.8]
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
| the engineered cells [genetic engineering] | $12.5 ($12.7); yeast-style $8.0 ($8.8); 120 g/L CO₂, 11 L/kg | $11.7 ($11.9); yeast-style $8.1 ($8.8); 150 g/L CO₂, 11 L/kg | $11.9 ($12.0); yeast-style $8.2 ($8.9); 146 g/L oxygen, 11 L/kg | $10.4 ($10.5); yeast-style $8.4 ($8.9); 258 g/L thickness, 11 L/kg |
| best shown in meat cells (bovine, glutamine replaced) [feed or process] | $26.2 ($26.5); yeast-style $19.8 ($21.3); 154 g/L CO₂, 28 L/kg | $24.7 ($24.9); yeast-style $19.6 ($20.9); 192 g/L CO₂, 28 L/kg | $25.0 ($25.3); yeast-style $19.7 ($21.1); 187 g/L oxygen, 28 L/kg | $23.3 ($23.5); yeast-style $19.5 ($20.6); 258 g/L thickness, 28 L/kg |
| ordinary meat cells (bovine) | $88.1 ($88.4); yeast-style $83.4 ($85.3); 124 g/L CO₂, 140 L/kg | $87.2 ($87.5); yeast-style $83.5 ($85.2); 155 g/L CO₂, 140 L/kg | $87.4 ($87.7); yeast-style $83.6 ($85.3); 151 g/L oxygen, 140 L/kg | $85.9 ($86.1); yeast-style $83.8 ($85.2); 258 g/L thickness, 140 L/kg |

*Without genetic engineering.* The engineered cell is replaced by what selection and feed alone have
shown: ammonia 0.14 mol/kg with glutamine replaced, lactate 0.39 per glucose as in adapted CHO cells, at the
engineered cell's 24-hour doubling:

| cells | sparger only | sparger, fat in the feed, oxygen held at 0.08 | packed column on a loop | column with oxygen sweep, 1 bar gauge |
|---|---|---|---|---|
| the engineered cells by selection and feed only [selection or adaptation] | $22.3 ($22.5); yeast-style $17.8 ($18.7); 120 g/L CO₂, 28 L/kg | $21.5 ($21.7); yeast-style $17.9 ($18.7); 150 g/L CO₂, 28 L/kg | $21.7 ($21.9); yeast-style $18.0 ($18.9); 146 g/L oxygen, 28 L/kg | $20.2 ($20.3); yeast-style $18.2 ($18.8); 258 g/L thickness, 28 L/kg |
| best shown in meat cells (bovine, glutamine replaced) [feed or process] | $26.2 ($26.5); yeast-style $19.8 ($21.3); 154 g/L CO₂, 28 L/kg | $24.7 ($24.9); yeast-style $19.6 ($20.9); 192 g/L CO₂, 28 L/kg | $25.0 ($25.3); yeast-style $19.7 ($21.1); 187 g/L oxygen, 28 L/kg | $23.3 ($23.5); yeast-style $19.5 ($20.6); 258 g/L thickness, 28 L/kg |
| ordinary meat cells (bovine) | $88.1 ($88.4); yeast-style $83.4 ($85.3); 124 g/L CO₂, 140 L/kg | $87.2 ($87.5); yeast-style $83.5 ($85.2); 155 g/L CO₂, 140 L/kg | $87.4 ($87.7); yeast-style $83.6 ($85.3); 151 g/L oxygen, 140 L/kg | $85.9 ($86.1); yeast-style $83.8 ($85.2); 258 g/L thickness, 140 L/kg |

"Best shown in meat cells" is bovine cells with glutamine replaced: 0.14 mol of ammonia per kg and a 43-hour
doubling (Hubalek 2023); "ordinary" is the same cells with glutamine, 0.70 mol and 26 hours. Both take chicken
cells' lactate yield (1.05 per glucose, Pasitka 2024) at 0.84 mol of glucose per kg. "Fat in the feed" means
the cells take all their lipid from the medium instead of making it from glucose; making lipid from glucose
gives off CO₂ without using oxygen, and on Humbird's cell that is why CO₂ made per oxygen used is 1.20 rather
than 1.0 (fed, 0.97; a carbon balance, the note's section 10). Holding dissolved oxygen at 0.08 mmol/L (38% of
air saturation, a usual pharma setpoint) in place of the 0.28 the standard tank's oxygen supply implies widens the
oxygen driving force by about a fifth; it matters only where oxygen binds.

Reading the tables (all with the filter loop, the protectant and antifoam counted): the tricks take the engineered cells
from $12.5 to $10.4, still above the $7 parity mark, and in a yeast-style plant they do not pay ($8.0 with the sparger alone, $8.4 with
everything). Since the filter loop is priced, a denser culture saves less: the bleed carries out less liquid, so more passes the
membranes. Without genetic engineering the engineered cell needs 28 litres of medium per kg (ammonia sets it), and the tricks take
it from $22.3 to $20.2 ($17.8 in a yeast-style plant, sparger only). With cells that have actually been measured, ammonia sets the
medium and the tank tricks are worth little: the cells decide the cost before the tank does. Losing runs adds $0.1–1.9 per kg. The
loss model counts the lost time and the tankful lost with each failure; it does not yet count a failed restart, and long continuous
runs are more exposed per run than short batches.

When the cells tolerate only a capped gas flow, the cheapest combination of tank shape, column and headspace
pressure (`gas_exchange.cheapest_tricks`; the sparger runs at its cap, a squatter tank pays for its steel):

| gas cap | food-grade plant, sparger only | cheapest combination, any circulation | the same, keeping the loop within the tested passes and the safe pH exposure | yeast-style: sparger only / any / within limits |
|---|---|---|---|---|
| 1 mm/s | $49.3 | $10.78: column with oxygen sweep, the ordinary tall tank, 1 bar gauge; **94 passes** | $20.9: column for CO₂, liquid twice as deep as wide, 1 bar gauge; 6 passes | $20.4 / $8.67 / $10.6 |
| 2 mm/s | $26.6 | $10.68: column with oxygen sweep, the ordinary tall tank, 1 bar gauge; **75 passes** | $13.9: column for CO₂, liquid twice as deep as wide, 1 bar gauge; 10 passes | $12.3 / $8.11 / $8.1 |
| 4 mm/s | $15.2 | $10.49: column with oxygen sweep, the ordinary tall tank, 1 bar gauge; **43 passes** | $11.6: column for CO₂, liquid 1.3 times as deep as wide, 1 bar gauge; 12 passes | $8.3 / $7.88 / $7.9 |
| 6 mm/s | $12.5 | $10.36: column with oxygen sweep, the ordinary tall tank, 1 bar gauge; **22 passes** | $10.7: column for CO₂, liquid as deep as wide, 1 bar gauge; 10 passes | $8.0 / $7.87 / $7.9 |

Passes are tank volumes pumped through the column an hour. Dense cultures have been pumped through fibres at up
to about 15-24 an hour for weeks, at 1-4 litres (Clincke 2013; a vendor note); nothing beyond that is tested.
Culture leaving the column stays alkaline (+0.26 pH at 55 mbar) until it is back in the tank, so the share of
the culture that is alkaline grows with the passes. The safe limit used here is the 55 mbar, 0.5 m3 design that
the gas-exchange note found 3 to 6 times below an exposure that slowed CHO cells (Paul 2020). At 22 passes the
loop is 1.9 times that limit (about half the harmful exposure); at 75 passes, 6.4 times (about twice the harmful
one). **Within those limits the reference case depends on the gas the cells tolerate again**: $10.7 at 6 mm/s, $11.6 at
4, $13.9 at 2, $20.9 at 1. In the cells-by-tank tables above, the last column ("column with oxygen sweep, 1 bar
gauge") runs at 22 passes an hour for the engineered cells, beyond the tested range. None of the tricks has been
tried with meat cells.

### If perfusion cannot be run at 20 m³

Every scenario uses a perfusion tank, which nobody has run above about 4 m³. Without cell retention a tank is capped by waste.
Central costs **$41–45** a kilo in a stirred tank in fed-batch or fill-and-draw at the model's own cap (62 g/L), and **$92–99** at
the 27 g/L reported for meat cells at 20 m³, against $29.92 in perfusion. The best case goes from $9.71 to $13.87 (or $43). The food-grade plant
with shared medium cushions it most: $26.81 to $29.19. We put about 65% on perfusion failing at 20 m³ for the best case and
Central (`research_notes/no_perfusion_downside.md`).

### Against what companies report (`industry_claims.py`)

Company figures are usually operating cost (COGS): medium, labour, utilities and consumables, with nothing for the plant. Every
scenario cost here includes a yearly charge on the plant. Split the same way:

| case | cells, $/kg | of which: charge on the plant | operating cost | of which: filter membranes | medium and growth factors |
|---|---|---|---|---|---|
| Reference: a standard perfusion tank | $12.5 | $6.4 | **$6.1** | $1.0 | $1.7 |
| Best case | $9.7 | $2.3 | **$7.4** | $2.5 | $1.7 |
| Central | $29.9 | $8.2 | **$21.7** | $8.2 | $8.7 |
| Central, shared medium | $26.8 | $4.8 | **$22.1** | $8.2 | $8.7 |
| Cautious | $43.8 | $15.9 | **$27.9** | $6.9 | $14.6 |

| Central's cells, 20 m³ tank drained and refilled (as Vow runs), in | cells, $/kg | charge on the plant | operating cost | at the 27 g/L reported for meat cells |
|---|---|---|---|---|
| the scenario's food-grade plant ($856k per m³) | $46.2 (62 g/L) | $32.5 | **$13.7** | $103.2 (operating $29.0) |
| a food-grade plant with shared medium ($476k per m³) | $32.1 (62 g/L) | $18.1 | **$14.0** | $70.6 (operating $29.3) |
| a yeast plant with what animal cells need ($246k per m³) | $23.3 (62 g/L) | $9.3 | **$14.0** | $50.6 (operating $29.3) |

| who | figure | a cost of | capital in it? | kind | checked by | date |
|---|---|---|---|---|---|---|
| [Lever VC (investor), across several companies](https://agfundernews.com/humbird-was-spectacularly-wrong-on-cultivated-meat-economics-says-report-as-vow-predicts-it-will-soon-be-unit-margin-positive) | $10–15/kg; some below $10/kg | cell mass; wet or dry not stated; scale not stated | excluded (COGS) | vetted under NDA | the investor; data not public | April 2025 |
| [Lever VC (investor)](https://agfundernews.com/humbird-was-spectacularly-wrong-on-cultivated-meat-economics-says-report-as-vow-predicts-it-will-soon-be-unit-margin-positive) | medium at $1/L or less, several under $0.50/L | medium per litre; litres per kg not stated | not applicable | vetted under NDA | the investor; data not public | April 2025 |
| [Gourmey (now PARIMA), modelled by Arthur D. Little](https://parima.bio/blog/gourmey-sets-new-cost-benchmark-in-cultivated-meat-production-with-3-4-lb-model-independently-validated) | €7/kg at 5,000 L scale; medium €0.20/L | production cost; product basis not stated | not stated | model | a consultancy, commissioned by whom not stated | May 2025 |
| [Arthur D. Little (consultancy)](https://www.adlittle.com/en/insights/viewpoints/cultivated-meat-one-year) | low €40s/kg in 2026; about €10/kg by 2030 | finished product | not stated | model | nobody named | 2025 |
| [SuperMeat (company white paper)](https://supermeat.com/wp-content/uploads/2024/11/A-Deep-Dive-Into-Cost-Effective-Cultivated-Meat-Production-V.pdf) | $29.5/kg with depreciation ($26.0 without) | 100% chicken cells, wet; 10 L runs scaled on paper to 25,000 L | depreciation only | model from runs | nobody; not peer reviewed | November 2024 |
| [Vow (company)](https://agfundernews.com/humbird-was-spectacularly-wrong-on-cultivated-meat-economics-says-report-as-vow-predicts-it-will-soon-be-unit-margin-positive) | a 20,000 L bioreactor built for “well under $1 million” | one vessel; whether piping and installation are in it not stated | a capital cost | company statement | nobody | April 2025 |

Reading it (company figures are claims; none has been audited):

- **On operating cost the model agrees with what companies claim.** Lever VC reports $10–15 a kilo of cell mass for several companies,
  some below $10. Central's cells in a tank drained and refilled, as Vow runs its 20 m³ tank, cost $13.7–14.0 a kilo to operate. With
  engineered cells in perfusion the operating cost is $13.0, and the best case $7.4.
- **The difference is the plant.** A tank drained and refilled at 62 g/L makes little in a year, so the plant charge is $9–33 a kilo
  depending on what the plant costs. Company COGS leave this out. Gourmey's €7/kg does not say whether it includes it.
- **The plant's price is the number most worth checking against industry.** In a plant built like a yeast plant with what animal
  cells need ($246k per m³), Central's cells drained and refilled cost $23.3, below Central in perfusion ($29.9) and with no filter
  to hold the cells back. Nobody has published what such a plant costs to build for animal cells; Vow says its 20 m³ vessel cost
  well under $1 million, without saying whether piping and installation are in that.
- **The density is the other open number.** The 62 g/L above is the model's waste limit for these cells. At the 27 g/L reported for
  meat cells at 20 m³ the same cases cost $51–103 a kilo, $29 of it operating cost.

### Vessel types and operating modes

A stirred tank and perfusion are not alternatives: one is a vessel, the other a way of running it. `vessels.py` changes only
those two and holds the rest (research_notes/vessels_and_modes.md has both grids, with sources).

| reference case, $/kg | Batch | Fed-batch | Fill-and-draw | Chemostat | Perfusion |
|---|---|---|---|---|---|
| Stirred tank, 20 m3 | 65.35 | 18.85 | 18.46 | 34.75 | **12.51** |
| Airlift, 20 m3 | 62.37 | 20.79 | 20.35 | 33.18 | 14.78 |
| Single-use bag, 5 m3 | 1,080 | 293.45 | 38.83 | 75.58 | 20.91 |
| Packed bed, 65 L | 3,730 | as batch | not possible | not possible | 3,726 |
| Hollow fibres, 0.5 L | 610,043 | as batch | not possible | not possible | 610,039 |

In the central scenario the stirred tank costs $103.12, $42.87, $46.21, $90.40 and $29.92 across the same modes. Perfusion
includes the filter loop that holds the cells back (`retention.py`); the other modes need no such device.

- Perfusion in a stirred tank is the cheapest combination in both settings. Nobody has run animal cells in perfusion above
  about 4 m3.
- Fed-batch and fill-and-draw, which run at 20 m3 today, cost about $19 in the reference case and $43-46 in the central
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
  Europe    $62k        P50  0.8%  [0.2,  3.7]    P50  2.0%  [ 0.5,  7.5]  <- easiest (rich + priciest meat)
  US        $86k        P50  0.4%  [0.1,  1.5]    P50  1.1%  [ 0.3,  3.6]
  Global    $24k        P50  0.2%  [0.0,  0.6]    P50  0.6%  [ 0.1,  1.9]
  China     $27k        P50  0.3%  [0.1,  1.1]    P50  1.1%  [ 0.3,  3.5]
  Brazil    $22k        P50  0.0%  [0.0,  0.2]    P50  0.1%  [ 0.0,  0.4]
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
   hollow-fibre filter loop whose membranes have never filtered a culture this thick for a month; how long they last is the open
   number, worth $20 a kilo or more in Central.
6. **Contamination is not the main obstacle to a cheaper plant, on this model:** the food-grade plant with shared medium stays cheaper than a sterile one until
   it loses a run about every 25 days. Measured loss rates in food-grade tanks would test this.
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
