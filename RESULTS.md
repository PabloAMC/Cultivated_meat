# Cultivated meat: how far can it get? — results

*These are the findings of a cost and demand model. The default cost is what a company reports for its own process (SuperMeat
2024). The scenarios (`scenarios.py`) describe what has to go right for the cost to fall. They use physics and published plant
costs (Humbird 2021). The [interactive explorer](https://pabloamc.github.io/Cultivated_meat/interactive.html) explains the
method in plain language and lets you change every assumption. [METHODS.md](METHODS.md) has the code-level detail.
Everything below reproduces from the code.*

## Summary

*Revised 2026-11-16, second time: every scenario now holds dissolved oxygen at about half of air saturation, as pharma does
(Humbird's tank implies 130%); the design search found this free and unused. Central costs $29.4 in place of $29.9. Earlier the same
day: the scenarios are now a **ladder** ordered by how hard each change is (below), every row gives both the share
at its point cost and the median of draws, and the old reference is named for what it is, Humbird's optimistic design. Revised 2026-11-15, third time. Three costs that earlier versions left out are now counted. (1) The bubble protectant
(poloxamer 188, 2 g per litre) leaves with every litre of medium. It costs about $0.06 a litre at an assumed $30 a kilo; only
catalogue prices, $230–260, were found. (2) Antifoam cuts the oxygen the sparger delivers. The model takes the middle of the
reported range, a quarter lost; it used to take none. In the central and cautious cases oxygen now limits the density. (3) A
yeast-style plant has no oxygen unit in its price, so it now buys its oxygen. The plant ladder now uses the model's own cost for its
perfusion rows, so the cost-side input `plant_floor` moved from $9.8 to $10.8. Every scenario costs more. The central case costs
$29.9 in place of $26.6, and the best case $9.7 in place of $8.9. Earlier the same day, the device that holds the cells back was
priced as a real hollow-fibre filter loop (TFF, `retention.py`, `research_notes/retention_devices.md`). It used to be a hoped-for
device at $89k per m³ with no membranes. Before that, the cost stopped being one number, called "the floor". Scenarios now
describe the cost. Each scenario is a preset of ten switches (kind of cells, growth speed, plant, gas the cells tolerate, tank
tricks, tank shape, runs lost, restart time, growth factors, medium price). Each one states what has to go right, and the model
computes every figure (`scenarios.py`, `research_notes/cost_scenarios.md`). On 2026-11-14 the cost side was rebuilt. The earlier
anchor (Pasitka et al. 2024) counted a kilogram that is mostly liquid and left out the cost of the plant, so the model no longer
uses it.*

All costs are per kg of real cells, which are about 70% water and 20% protein, like meat. Plant costs are in 2025 prices. "Share" is
the long-run share of the meat sold by weight, once cultivated meat is on every shelf and no longer feels new. It is not a
forecast of when.

| scenario | cells, $/kg (10th–90th percentile) | R vs $12 meat | share of world meat, long run: at the point cost | median of draws (10th–90th) | hardest thing it needs |
|---|---|---|---|---|---|
| 1. Today: the best meat cells measured, in an ordinary 20 m³ perfusion tank | **$63.0** ($51–81) | 5.66 | 0.0% | **0.0%** (0.0–0.1%) | needs a change of feed, process or plant |
| 2. Plus process changes and cheaper inputs | **$30.7** ($28–39) | 2.98 | 0.4% | **0.2%** (0.0–0.6%) | needs a change of feed, process or plant |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | **$29.4** ($27–38) | 2.87 | 0.4% | **0.2%** (0.1–0.6%) | needs selection or adaptation of cells |
| 4. Plus a food-grade plant with shared medium | **$26.6** ($25–35) | 2.63 | 0.5% | **0.3%** (0.1–0.8%) | needs selection or adaptation of cells |
| 5. Plus engineered cells: the best case, everything works | **$9.7** ($9–12) | 1.22 | 8.0% | **3.8%** (1.2–9.8%) | needs genetic engineering |
| Forecast for 2035: a first draft of the author's medians | **$24.8** ($23–33) | 2.48 | 0.6% | **0.3%** (0.1–0.9%) | needs selection or adaptation of cells |
| Humbird's optimistic design: engineered cells in an ordinary perfusion tank | **$12.5** ($10–15) | 1.46 | 4.3% | **2.4%** (0.7–6.9%) | needs genetic engineering |
| As a company reports (SuperMeat 2024) | **$34.4** | 3.28 | 0.3% | **0.2%** (0.0–0.6%) | a company's own report |

**The ladder.** The first five rows add one kind of change at a time, easiest first. Row 1 is the best meat cells measured,
in the ordinary tall tank with no tricks, at today's prices for medium and growth factors. Row 2 adds changes that need no new
cells: the tank tricks, more gas with a protectant, faster restarts, and medium and growth factors at the prices companies
announce. Row 3 adds cells selected on the low-waste feed until they double every 36 hours, not 43; this is the central case of earlier versions. Row 4
adds a food-grade plant with shared medium. Row 5 adds engineered cells and puts every switch at its cheapest plausible
setting; this is the best case. The forecast row is the author's median for each switch by 2035 (below). Humbird's optimistic
design, the old reference ("the reference case" in the sections below), is not a rung: it assumes the hardest change (engineered cells) and none of the easy ones (the tank
tricks).

**The bands.** Each row's switches stay fixed, but the estimates behind it (plant cost, financing, the life of the filter
membranes, the upkeep share of respiration, medium price and loss rate) can be off. The share band lets demand vary too (4,000 draws).
Every row gives both the share at its own point cost and the median of the draws, so rows can be compared on either. The point
cost sits below the median cost, because the estimates behind it have more room to fall short than to improve. The share rises
steeply as the price falls, so the share at the point cost is higher than the median (best case: 8.0% at the point cost, 3.8% median).

- **The easy changes are worth the most, and they come first.** Today's measured cells in an ordinary tank cost **$63.0 a kilo**. The
  changes in row 2 halve that, to **$30.7**, without touching the cells. The tank tricks alone are worth $20.6 for these cells, the
  largest single step anywhere on the ladder, and more gas is worth nearly as much ($17.2); the two overlap, because both clear CO₂.
- **Selecting cells adds little on its own: $1.3, to $29.4 (Central), and all of it comes from faster growth.** The cells of rows 1
  and 2 already make little ammonia, because glutamine is replaced in the feed. Selection adds a 36-hour doubling in place of 43, and
  a lower lactate yield that saves nothing, because ammonia sets the litres of medium for both kinds of cell. Nobody
  has run the central tank design with animal cells. Oxygen, not CO₂, limits it, at 191 g/L: antifoam is taken to cost a quarter of the
  sparger's oxygen transfer, worth $1.7 a kilo here. Without the tricks a kilo costs $33.1 in a tank of the same shape, and $36.2 in the
  ordinary tall tank. At 30 hours Central costs $28.2, and at 24 hours $27.0. The author puts the odds of 24 hours at this waste level at
  about 10%.
- **A cheaper plant takes $2.9 off, to $26.6.** It is Humbird's plant without a clean hall, an oxygen plant or eight seed tanks, and with
  one medium line for all the tanks; nobody has built one.
- **Engineered cells take off $16.9, to $9.7, the best case.** They make almost no waste, so they need 11 litres of medium a kilo
  instead of 28, and every litre less is also a litre less through the filter and less protectant. Its tank reaches the thickness limit
  (258 g/L) with the column, 1 bar of pressure, recycled oxygen and a squat tank. With the cheapest plausible setting of every other
  switch, cultivated meat then takes about **4% of world meat** (median; 80% of draws between 1% and 10%; 8.0% at the point cost, with
  14% in the US and 25% in Europe).
- **The forecast for 2035 is $24.8 a kilo and about 0.3% of world meat** (median; 0.1–0.9%). It is the ladder's row 4 with fewer lost
  runs and $0.15 medium: the author's median for each switch keeps selected cells, not engineered ones. See "The forecast" below.
- **Humbird's optimistic design costs $12.5 (median share 2.4%).** It sits between rows 4 and 5 because it has engineered cells but no
  tank tricks and no growth factors to buy.
- **Holding the cells back costs more than the model used to assume.** Every scenario uses a 20 m³ tank in perfusion. A filter loop
  must clear the medium that the bleed of cells does not carry out, and its membranes cost about $0.37 per litre they filter. The central
  cells need 28 litres of medium a kilo at 191 g/L, so the filter clears 23 litres a kilo. The membranes alone cost $8.3 a kilo. The
  reference case clears 2.8 litres a kilo and pays $1.0. A disc-stack separator on the outflow would cost about the same in the central
  case, because it bursts some of the cells. Nobody has held animal cells in perfusion above about 4 m³ (`research_notes/retention_devices.md`).
- **The bubble protectant is a real cost.** At 2 g/L it is 22 g a kilo of cells for engineered cells (Humbird's design, the best case) and 56 g for the others,
  which need 28 litres of medium a kilo. That is $0.7 and $1.7 a kilo at the assumed $30 a kilo, or $5.6 and $14 at the catalogue price. A bulk quote would settle it.
- **Company cost claims are operating cost, and the scenarios include the plant.** On operating cost alone the central cells cost
  $13.7–14.0 a kilo in a tank run as Vow runs its 20 m³ tank. That is inside the $10–15 an investor reports for several companies. The plant
  charge is the difference (section 1, "Against what companies report").
- **No scenario reaches price parity.** Parity with $12 meat and a $5 markup needs $7/kg of cells. The best case costs $9.7, and its own
  band is $9.2–12.3. No scenario uses a plant as cheap as a yeast plant, because nothing shows that animal cells can grow in one.
- **What decides it.** This list moves each switch alone from the central scenario to its best or its worst setting. The kind of cells
  matters most (−$9.5 with engineered cells, +$84 with ordinary meat cells). Next come the medium price (−$4.0 at an aspirational $0.05 a litre to +$8.6),
  growth factors (−$3.0 to +$7.0), the gas the cells tolerate (−$1.8 at 6 mm/s, +$5.0 at 2), tank tricks (up to +$3.7 if none work),
  the plant (−$2.9 with shared medium) and growth speed (−$2.4 at 24 hours). The kind of cells matters most because waste sets the litres of
  medium a kilo, and each litre must also pass the filter and carries protectant. The switches interact, and the page ranks them around
  any scenario you choose.
- **At equal price,** once cultivated meat is familiar, it wins **~49%** of the market if shoppers see it as real meat and **~10%** if they do not. Taste and
  the value shoppers put on "no slaughter" change this to between ~12% and ~75%.
- **As a company reports its process, with capital counted,** cultivated chicken costs about **$34/kg of cells,
  ~3.3× everyday meat** ($39 in the shop). This is SuperMeat's 2024 process for 100% cell mass, from 10-litre runs
  scaled on paper to 25,000-litre tanks, with a yearly charge on the plant. The company's own figure, with
  depreciation only, is $29.5/kg. Nobody has peer reviewed it. At that cost the share is **~0.3% of world meat** (0.6%
  in the US). The Monte Carlo median over the cost and demand ranges is 0.2%, with an 80% range of 0.0–0.6%. Nearly all of it is
  premium beef and seafood.
- **Where:** beef and seafood. Chicken and pork stay dearer even in the best case. Cultivated meat can already beat the price of a few luxury products,
  but those markets are tiny.
- **When:** these are long-run ceilings. Adoption reaches 90% of its long-run share after about 30 years.

**For funders,** in order: better cells (low waste, fast-growing and robust, which is what the central case rests on), the price of medium and of growth
factors at production scale, tank tricks that clear CO₂ without bubbles, and a cheaper class of plant for animal cells.

## The forecast for 2035

The forecast row puts each switch at the setting the author thinks as likely as not to be reached at production scale by 2035.
It is a judgement built from the odds in the research notes, and a first draft for Pablo to adjust.

| switch | median by 2035 | the odds behind it |
|---|---|---|
| kind of cells | selected for low waste (glutamine replaced, lactate 0.42 per glucose) | engineered low-waste lines in production by 2035: about 25% (judgement); feed and selection already shown in flasks (Hubalek 2023) |
| growth speed | 36 hours | low-waste cells at 24 h about 10%, at 30 h or faster 25%, 36 h 45%, 43 h 70% (`cost_scenarios.md`) |
| plant | food-grade with shared medium | a food-grade plant at or below that cost, about 65% (`cheap_plant_study.md`) |
| gas the cells tolerate | 4 mm/s | about even odds for 6 mm/s at 20 m³ (`gas_flow_cap.md`) |
| tank tricks | the column and 1 bar, as the loop checks allow | cells on a stripping column 60%, at 2 bar absolute 85% (`gas_exchange_study.md`) |
| runs lost | 0.6% a day | makers report 0.6–2.2% a day today; the low end by 2035 (judgement) |
| restart after a loss | 14 days | |
| growth factors | 30% of Humbird's price | GFI's target is growth factors at 10% of cost (`medium_cost_gfi.md`) |
| medium | $0.15 a litre | announced $0.20 for 2025, lowest report $0.07 (`medium_cost_gfi.md`) |

Two cautions. The median of each switch is not the median outcome: the switches are linked (good cells tend to come together) and
cost is not linear in them, so a forecast should draw the switches from these odds; this row does not yet. And the band in the
table varies only the estimates behind the row, not the switches, so it is narrower than the forecast's real uncertainty.

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

### The frontier: every lever at its limit

Moving the central scenario's levers one at a time to the limits the research notes support, each kept moved, takes it from
$29.42 to **$6.86** a kilo ($7.66 with GFI's amino-acid prices). The least medium the physics allows (6.4 L/kg) is the largest
step on its own ($13.76), then a cheaper filter, then cells doubling in 16 hours; the levers share what they save, because fewer litres
of medium also mean less to filter. The frontier is just under the $7 that parity needs. With antifoam counted, oxygen limits
the tank, so a thicker culture adds nothing (without the antifoam effect the frontier is $6.16). No step is shown for meat
cells, and the odds of all of them together are far below any single one (`research_notes/frontier.md`).

### How far tank design can go (`design_space.py`)

The aim of tank design is a tank where CO₂, oxygen and mixing no longer bind, so that only the thickness of the culture does
(258 g/L). `design_space.py` first prices that aim (the ordinary tank with every gas limit lifted for free), then searches every
combination of the tank options the model has, 144 designs a scenario, keeping those whose column loop passes its checks.

| case | ordinary tank | the scenario's design | cheapest design, no cage | cheapest design, with a bubble cage | perfect gas exchange |
|---|---|---|---|---|---|
| 1. Today's cells | $62.96 (46 g/L, CO₂) | $62.96 | $38.66 (175 g/L, oxygen; 4 unproven) | $35.38 (258 g/L, thickness; 4 unproven) | **$34.80** (258 g/L) |
| 2. Plus process changes | $38.77 (93 g/L, CO₂) | $30.73 | $29.14 (258 g/L, thickness; 4 unproven) | $28.95 (254 g/L, CO₂; 3 unproven) | **$28.51** (258 g/L) |
| 3. Central | $36.20 (87 g/L, CO₂) | $29.42 | $27.93 (258 g/L, thickness; 5 unproven) | $27.62 (258 g/L, thickness; 3 unproven) | **$27.19** (258 g/L) |
| 4. Shared-medium plant | $29.86 (87 g/L, CO₂) | $26.56 | $25.80 (258 g/L, thickness; 5 unproven) | $25.57 (258 g/L, thickness; 2 unproven) | **$25.28** (258 g/L) |
| 5. Best case | $10.40 (120 g/L, CO₂) | $9.66 | $9.60 (258 g/L, thickness; 4 unproven) | $9.48 (258 g/L, thickness; 3 unproven) | **$9.33** (258 g/L) |
| Forecast for 2035 | $27.83 (87 g/L, CO₂) | $24.80 | $24.11 (258 g/L, thickness; 5 unproven) | $23.89 (258 g/L, thickness; 2 unproven) | **$23.61** (258 g/L) |

- **Tank design matters most for today's cells:** $28 a kilo between the ordinary tank and perfect gas exchange. From rung 2 on, the
  scenarios' designs are within $1.2–2.2 of the ideal, and the best case within $0.3.
- **Designs that leave only the thickness limit exist on paper:** with a bubble cage and 1 bar of pressure, or without a cage at 2
  bar. Each needs two to five elements nobody has run with animal cells. The cage's numbers are judgements.
- **The search found one free improvement, and the scenarios now use it:** holding dissolved oxygen at half of air saturation, as
  pharma does. It is worth $0.5 a kilo in Central.
- **After the gas limits, the litres of medium are what is left.** In Central perfect gas exchange saves $1.7 a kilo; medium at the
  least the physics allows saves $15.7. Tables and method: `research_notes/design_space.md`.

### Cleaning and reusing the medium (`medium_reuse.py`)

After the gas limits, the litres of medium are the largest cost left. Ammonia sets them: 28 litres per kg in Central. Can the
ammonia be taken out and the liquid reused? Partly, and the limit is the cell filter. A litre that leaves the tank costs $0.75 in
Central, and $0.38 of that is the membranes that hold the cells back. A device that cleans the filtered liquid (the permeate)
and returns it saves the medium, the growth factors and the protectant, but the liquid has passed the filter either way. Only
a device that takes the waste out with no liquid drawn through the cell filter, such as dialysis across the culture, saves the
filter too.

| what sets the litres of medium (3. Plus cells selected to grow faster on the low-waste feed (Central)) | litres per kg of cells |
|---|---|
| ammonia, held at 5 mmol/L | 28.0 |
| the least flow the cells need for everything else | 16.2 |
| lactate, within the salt limit | 9.4 |
| the nutrients, as a concentrate | 8.0 |
| leaves with the cells, unfiltered | 5.2 |

| route | fresh medium, L/kg | cleaned and returned, L/kg | through the cell filter, L/kg | cells, $/kg | saves | pays if the device costs under |
|---|---|---|---|---|---|---|
| No reuse | 28.0 | 0 | 22.8 | **$29.42** | | |
| An ammonium exchanger on the permeate, taking 42% of the ammonia | 16.2 | 11.8 | 22.8 | **$27.01** | $2.40 | (priced by its sorbent: 0.15 mol/kg at $5/kg, used once) |
| Electrodialysis of the permeate | 16.2 | 13.1 | 24.1 | **$25.95** | $3.47 | $0.29 a litre |
| Dialysis of the permeate, dialysate thrown away | 28.0 | 0.0 | 22.8 | **$29.42** | nothing | never |
| Dialysis of the permeate, dialysate cleaned and reused | 8.6 | 21.6 | 24.9 | **$26.15** | $3.26 | $0.24 a litre |
| Dialysis across the culture, dialysate cleaned and reused; the exchange membrane costs what the cell filter does | 8.0 | 22.2 | 2.8 | **$25.06** | $4.35 | $0.24 a litre |
| The same; the exchange membrane clears 10 L/m²/h, twice what the filter passes | 8.0 | 22.2 | 2.8 | **$20.90** | $8.52 | $0.43 a litre |
| *A perfect, free device on the permeate* | 8.0 | 20.0 | 22.8 | *$22.12* | *$7.29* | |
| *A perfect, free device across the culture* | 8.0 | 20.1 | 2.8 | *$14.62* | *$14.79* | |

| scenario | no reuse | exchanger on the permeate | electrodialysis of the permeate | dialysis of the permeate, dialysate reused | dialysis across the culture, at the filter's cost | the same, at twice the filter's clearance | perfect and free, on the permeate | perfect and free, across the culture |
|---|---|---|---|---|---|---|---|---|
| 1. Today: the best meat cells measured, in an ordinary 20 m³ perfusion tank | **$62.96** | $60.29 | $59.80 | $60.77 | $60.41 | $59.06 | $59.24 | $56.80 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | **$29.42** | $27.01 | $25.95 | $26.15 | $25.06 | $20.90 | $22.12 | $14.62 |
| 5. Plus engineered cells: the best case, everything works | **$9.66** | $9.66 | $9.65 | $9.66 | $9.66 | $9.20 | $9.47 | $8.28 |

- **Cleaning the permeate is worth $2–4 a kilo in Central:** $2.4 with an ammonium exchanger, $3.5 with electrodialysis (to
  $25.95), $3.3 with dialysis if the dialysate is itself cleaned. A perfect, free device would save $7.3. A device on the
  permeate must take more than 50% of the waste from a litre in one pass before it saves anything.
- **Cleaning across the culture is worth more, and is less proven:** $4.4 if the exchange membrane costs what the cell filter
  does, $8.5 (to $20.90) if it clears twice the litres per m², as a haemodialyser does on blood for a few hours. The limit
  is $14.8.
- **The evidence is thin.** Electrodialysis took over 90% of ammonium and 99% of lactate from medium in one report, cited in a
  book and not found; dialysis held a dense CHO culture for 10 days at the bench; a reused dialysate exists only in patent claims.
  The cost of electrodialysis per litre is my arithmetic. What these devices do to growth factors and nutrients over many passes
  has not been measured.
- **Reuse does not replace better cells.** In the best case the cells make so little ammonia that reuse is worth under $1.5.
- The model's own sorbent lever counted the filter as saved; it no longer does (no scenario used it). Sources, sensitivity and
  the experiments that would settle it: `research_notes/medium_reuse.md`.

### If perfusion cannot be run at 20 m³

Every scenario uses a perfusion tank, which nobody has run above about 4 m³. Without cell retention a tank is capped by waste.
Central costs **$41–45** a kilo in a stirred tank in fed-batch or fill-and-draw at the model's own cap (62 g/L), and **$92–99** at
the 27 g/L reported for meat cells at 20 m³, against $29.42 in perfusion. The best case goes from $9.66 to $13.87 (or $43). The food-grade plant
with shared medium cushions it most: $26.56 to $29.19. We put about 65% on perfusion failing at 20 m³ for the best case and
Central (`research_notes/no_perfusion_downside.md`).

### Against what companies report (`industry_claims.py`)

Company figures are usually operating cost (COGS): medium, labour, utilities and consumables, with nothing for the plant. Every
scenario cost here includes a yearly charge on the plant. Split the same way:

| case | cells, $/kg | of which: charge on the plant | operating cost | of which: filter membranes | medium and growth factors |
|---|---|---|---|---|---|
| 1. Today's cells, ordinary tank | $63.0 | $35.7 | **$27.3** | $2.4 | $14.6 |
| 2. Plus process changes | $30.7 | $8.6 | **$22.2** | $8.5 | $8.7 |
| 3. Central (selected cells) | $29.4 | $7.6 | **$21.8** | $8.3 | $8.7 |
| 4. Plus a plant with shared medium | $26.6 | $4.5 | **$22.1** | $8.3 | $8.7 |
| 5. Best case (engineered cells) | $9.7 | $2.1 | **$7.5** | $2.7 | $1.7 |
| Forecast for 2035 | $24.8 | $4.2 | **$20.6** | $8.3 | $7.2 |
| Humbird's optimistic design | $12.5 | $6.4 | **$6.1** | $1.0 | $1.7 |

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
  engineered cells in perfusion the operating cost is $13.1, and the best case $7.5.
- **The difference is the plant.** A tank drained and refilled at 62 g/L makes little in a year, so the plant charge is $9–33 a kilo
  depending on what the plant costs. Company COGS leave this out. Gourmey's €7/kg does not say whether it includes it.
- **The plant's price is the number most worth checking against industry.** In a plant built like a yeast plant with what animal
  cells need ($246k per m³), Central's cells drained and refilled cost $23.3, below Central in perfusion ($29.4) and with no filter
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
| Stirred tank with a bubble cage, 20 m3 | 67.59 | 19.46 | 19.05 | 35.93 | 11.08 |
| Airlift, 20 m3 | 62.37 | 20.79 | 20.35 | 33.18 | 15.07 |
| Single-use bag, 5 m3 | 1,080 | 293.45 | 38.83 | 75.58 | 20.91 |
| Packed bed, 65 L | 3,730 | as batch | not possible | not possible | 3,726 |
| Hollow fibres, 0.5 L | 610,043 | as batch | not possible | not possible | 610,039 |

In the central scenario the stirred tank costs $103.12, $42.87, $46.21, $90.40 and $29.42 across the same modes. Perfusion
includes the filter loop that holds the cells back (`retention.py`); the other modes need no such device.

- Perfusion in a stirred tank is the cheapest combination in both settings. Nobody has run animal cells in perfusion above
  about 4 m3.
- Fed-batch and fill-and-draw, which run at 20 m3 today, cost about $19 in the reference case and $43-46 in the central
  scenario. The central cells make more ammonia, and a culture that is not washed out stops at 62 g/L. These costs assume
  62-92 g of cells a litre. Nobody has shown that density for meat cells at this size: the one 20 m3 plant for meat cells
  reports harvests of about 27 g/L.
- An airlift costs about what a stirred tank costs when waste is not washed out. In perfusion its tall shape clears less CO2.
- A stirred tank with a bubble cage (Pablo's design, 2026-11-16): an inner cylinder of fine mesh holds a strong sparger, and the cells
  live in the ring around it with soft bubbling. Only medium crosses the mesh, so the cage's gas counts at 80% of its
  strength (a judgement). In perfusion it costs $11.08 in the reference case and $27.72 in Central, against
  $12.51 and $29.42 in the plain tank. Caged aeration exists only with microcarriers in small tanks.
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
