# Cultivated meat: how far can it get? — results

*Findings of a cost and demand model. The default cost is what a company reports for its own process (SuperMeat
2024); the floor is derived from physics and published plant costs (Humbird 2021). The
[interactive explorer](https://pabloamc.github.io/Cultivated_meat/interactive.html) explains the method in plain
language; [METHODS.md](METHODS.md) has the code-level detail. Everything below reproduces from the code.*

## Summary

*Revised 2026-11-14: the cost side was rebuilt. The earlier anchor (Pasitka et al. 2024) turned out to count a
kilogram that is mostly liquid and to leave out the cost of the plant, so it is no longer used. The default is
now a company's reported cost on a sound basis, and the floor is derived from physics. On the demand side one
thing changed: how steeply share falls above equal price is now set by what premium meat, milk and eggs
actually sell (it was set by one choice experiment alone). Shares at equal price are unchanged; shares above it
are several times lower. Details: METHODS.md, "Changes of 2026-11-14".*

All costs are per kg of real cells: about 70% water and 20% protein, like meat. Plant costs are in 2025 prices.

- **The floor is about $11.5/kg of cells, ~1.4× everyday meat** ($16.5 in the shop vs a $12 benchmark), if
  everything that has been costed for animal cells works together and the plant is financed like a mature food
  industry: a sterile plant without clean rooms, perfusion in 20,000-litre tanks with a device that holds the
  cells back, efficient cells, floor-price medium. Each piece has been shown or claimed somewhere, never together,
  and the device does not exist yet. With the financing of a first plant the same case costs $14. The floor is the
  best case: if its inputs are allowed to fall short within their plausible ranges, the median is $19/kg (80%
  range $12–30), and most of that distance is the cells: speed, density, waste and size.
- **At the floor it takes ~5% of world meat by weight** in the long run, 10% in the US and 22% in Europe. How
  steeply share falls above equal price is set by six premium animal products (organic milk, eggs, chicken,
  meat), which take 2–7% of sales at 1.5 to 2.2 times the price, within the range one choice experiment on
  cultivated meat allows. Across the plausible range of price sensitivity the world figure runs from 4% to 12%.
  Counted in animals it is lower still: cultivated meat sells mostly as beef and seafood, so a tonne sold spares
  about 34 land animals in the US, against 250 for a tonne of the average meat mix.
- **Price parity needs a cheaper class of plant.** Plants for yeast and other microbes are built today for about
  a quarter of the cost per cubic metre. In such a plant the floor would be about **$6.6/kg**, just under the $7
  that parity needs. That plant cost is not only a yeast plant's: Humbird's own yeast plant costs about that
  with 20 m³ tanks, and two published cultivated-meat designs (CE Delft, Negulescu) assume it. Humbird's
  animal-cell plant costs five times more for sterile seed trains, medium handling, oxygen supply and clean
  rooms. Nobody has run animal cells in the cheaper kind. Allowing its inputs to fall short, the median is
  $12/kg, with about a 5% chance of $7 or less. This is the frontier that decides whether cultivated meat can match the price of everyday meat.
- **At equal price,** once familiar, it wins **~49%** of the market if seen as real meat, **~10%** if not. Taste and
  the value shoppers put on “no slaughter” move this between ~12% and ~75%.
- **As a company reports its process, with capital counted,** cultivated chicken costs about **$34/kg of cells,
  ~3.3× everyday meat** ($39 in the shop). This is SuperMeat's 2024 process for 100% cell mass, from 10-litre runs
  scaled on paper to 25,000-litre tanks, with a yearly charge on the plant; the company's own figure, with
  depreciation only, is $29.5/kg. It is not peer reviewed. At that cost the share is **~0.3% of world meat** (0.6%
  in the US; Monte Carlo median over the cost and demand ranges 0.2%, 80% range 0.0–0.6%), nearly all of it
  premium beef and seafood.
- **Where:** beef and seafood. Chicken and pork stay dearer even at the floor. A few luxury products are beatable
  on price already, but tiny.
- **When:** these are long-run ceilings; adoption reaches 90% of its long-run share after about 30 years.

**For funders:** in order, cheaper classes of plant for animal cells, better cells (efficient, fast-growing,
robust), a way to hold cells back in large tanks, and medium cost at production scale.

## 1. Cost and the price ratio

| case | cells, $/kg | R vs $12 meat | source and status |
|---|---|---|---|
| cautious: pharma-style plant, cells at half the density, reported medium | $49.2 | 4.52 | physics-based plant cost (`floor_physics.py`); nearer to reported harvests |
| **as reported by a company, with a return on capital (default)** | **$34.4** | **3.28** | SuperMeat 2024; 10 L runs scaled on paper; not peer reviewed; its own figure with depreciation only is $29.5 |
| Humbird's fed-batch design, 2025 prices | $24.6 | 2.47 | a detailed design with efficient cells; not built |
| cautious floor: pharma-style plant, tanks drained and refilled | $19.4 | 2.03 | physics-based; efficient cells at this density not shown |
| floor case with first-plant financing | $14.1 | 1.59 | the row below at 23.6% of the plant's cost a year |
| **floor: no clean rooms, perfusion, efficient cells, food-industry financing** | **$11.5** | **1.38** | physics-based; each piece shown separately, never together; the cell-retention device is hoped for |
| **frontier: the floor in a microbial-class plant** | **$6.6** | **0.97** | such plants exist for microbes; none built or costed for animal cells |
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

**The floor is physics divided into engineering.** The plant's cost per kg is its cost per m³ of tank divided by
what a m³ produces in a year. Output is limited by how much oxygen and CO₂ a tank can exchange without bubbles
killing the cells. Plant cost per m³ comes from Humbird's design: about $910k with clean rooms, about $810k
with a sanitary hall in their place. Microbial fermentation plants are built for about $190k. The model reports the floor together with the
frontier and the cautious case, because which one applies depends on what can be made to work (METHODS.md, "The
floor's plant term").

**Financing matters as much as engineering.** Humbird charges 23.6% of a plant's cost a year: money at 7.5%
repaid in 10 years, plus 4% maintenance and 5% insurance. That fits a first plant, and the default and the
cautious cases use it. His own report gives the food-processing sector's cost of capital as 5.4% and uses a
20-year life for a yeast plant; that makes the charge 17.3%. The floor and the frontier are long-run cases set
against meat, a mature industry, so they use 17.3%. It is worth $2.6/kg at the floor.

**How the tank is run matters less than the plant and the cells.** Perfusion is worth about $3–4/kg at the floor
against tanks that are drained and refilled; removing clean rooms saves about a tenth of the plant cost; a
microbial-class plant nearly halves the floor.

The medium and the plant matter most; no single lever reaches parity on its own (from the default: the floor's
plant cost gives R ≈ 2.50, medium at $0.20/L 2.52, efficient cells 2.33).

```
basic product vs commodity meat ($12/kg), Monte Carlo over the cost inputs (N=20,000):
  price ratio R:   P50 = 3.27   80% CI [2.51, 4.16]   90% CI [2.33, 4.43]
  long-run share:  P50 = 0.0%   80% CI [0.0, 0.9]
  0% of draws reach parity (R ≤ 1)
```

The median is close to the default 3.28: the plant-cost range is wider on the high side (reported harvests are
less dense than the floor assumes), while the medium price and cell efficiency can improve on the report. The
Monte Carlo does not include the frontier.

## 2. What share a price buys

| if cultivated meat, at equal price and once familiar… | share |
|---|---|
| tastes as good and is seen as real meat | **~49%** |
| tastes a little worse (0.8) / noticeably worse (0.6) | ~26% / ~12% |
| tastes as good, and “no slaughter” matters (0.5 / 1.0 / 1.5) | ~59% / ~68% / ~75% |
| tastes as good but isn't seen as real meat | ~10% |

At first contact it gets ~6% (a US choice experiment found ~5%). Against $12 everyday meat (US, long run) it
gets ~21% at the floor (1.4× the price) and next to nothing at the reported cost (3.3×).
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
                            default cost        cost floor
  meat type          $/kg    R     share        R     share
  chicken mince        5    7.87    0.0%       3.30    0.3%
  beef mince          11    3.58    0.0%       1.50   18.1%
  beef steak          20    2.27    0.8%       1.13   29.4%
  wagyu (premium)     45    1.01   17.9%       0.50   39.1%
  pork (processed)     8    4.92    0.0%       2.06    4.6%
  seafood fillet      24    1.89    2.1%       0.94   44.6%
  sushi-grade (prem.) 40    1.13   14.5%       0.56   34.4%
  TOTAL by weight: default 0.6%, at the floor 10.0%
```

At the default cost only products priced like wagyu and sushi-grade fish sell; their markets are small. At the
floor, seafood, beef cuts and beef mince lead; pork is under 5% and chicken close to zero.

**With the cells that have been published.** The floor assumes an efficient model cell for every species. Using
each species' published doubling time and cell size in the same plant, and for fish a lower tolerance of CO₂
(chicken and turkey cost 1.75× as much, beef 1.3×, seafood 1.8×; no data for pork), the US total at the floor's
plant is 5.5%, not 10% (world 2.7%, Europe 14%). The cell data are thin (METHODS.md, "Species costs in the
market model").

**Seafood rests on an untested assumption.** Seafood is the category closest to price parity at the floor,
with a 45% share for fillets. That assumes fish cells tolerate as much dissolved CO₂ as pharma cells do. Fish
live with about 2–4 mbar of CO₂ in their blood, against about 50 in mammals, and nobody has measured how fish
cells grow against CO₂. If they tolerate 50 mbar, not 100, fish cells cost $21/kg in the floor's plant and the
fillet share falls to 16%. No shrimp cell line exists at all.

**Animals.** A tonne of cultivated meat, sold where the model says it sells, spares about 34 land animals at
the floor (US) and about 18 at the reported cost; a tonne of the average US meat mix is about 250. Almost none
of it is chicken, where the animals are. Seafood animals are not counted, and seafood is about a third of
sales at the floor.

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
samples κ from 4 to 11 and plant costs from the floor to the cautious case. World beef is priced by consumption-weighted country prices (METHODS.md, "World beef price").
Against sushi-grade salmon, a structured product is at or below parity in 17% of draws, but structuring cost is
unmeasured.

## 5. Entry points, and timing

Luxury products compared at their everyday grade (farmed salmon, crossbred wagyu) are already beatable: foie gras,
bluefin tuna, sea urchin, wagyu. Lobster is close (R ≈ 1.1). Each is a small market. Commodity beef, pork and chicken,
where the volume is, stay out of reach even at the floor. Foie gras stands out: unstructured, expensive, and
increasingly banned on welfare grounds.

From a near-zero start, cultivated meat reaches 90% of its long-run share after about 30 years (16 to 74 across
the plausible speeds at which wariness fades), at the floor as at the reported cost. Current wariness (surveys: 5–60%) sets the speed, not the ceiling.

## 6. What to fund

1. **Cheaper classes of plant for animal cells:** whether animal cells can be grown in plants built like those
   for yeast and other microbes. It is the only route the model finds to price parity, and nobody has built or
   costed one.
2. **Better cells:** lines that waste little glucose, make little ammonia, grow fast and reach high density. The
   floor assumes them; nobody has shown them at scale.
3. **A way to hold cells back in large tanks:** perfusion stops at about 2,000 litres today because of filters.
   The floor prices a device nobody has built at what one study hopes it will cost.
4. **Contamination is not the main obstacle to a cheap plant, on this model:** with continuous harvest a
   yeast-style plant stays cheaper than a sterile one until it loses a run about every 11 days. Measured loss
   rates in food-grade tanks would test this.
5. **Medium cost at production scale:** verify the $0.50/L and sub-$0.20/L reports on a stated mass basis.
6. **Open, comparable data:** cost claims per kg of dry matter or protein, with capital included (METHODS.md, "A
   checklist for cost claims"). Most published analyses leave out all or part of the cost of capital.
7. **Structuring cost:** the biggest unmeasured number; it gates premium seafood.

A meat tax also works: raising conventional prices 25% lowers R as much as a 20% cut in every cost. Most of these
are public goods that industry underfunds.

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
  10-year depreciation period (20 years would add $8/kg). The floor's plant costs are one engineer's design
  (Humbird 2021) in 2025 prices. Neither has been reproduced.
- **Demand:** acceptance and the value of “no slaughter” can't be measured before launch; the model carries the
  full range (10% to 75% at equal price).

Figures: `python report_figures.py` (cost vs inputs, cost waterfall, share tornado, share vs price, timing paths,
penetration by type and region). Parameters and sources: `python inputs.py`.
