# Cultivated meat: how far can it get? — results

*Findings of a cost and demand model. The default cost is what a company reports for its own process (SuperMeat
2024); the floor is derived from physics and published plant costs (Humbird 2021). The
[interactive explorer](https://pabloamc.github.io/Cultivated_meat/interactive.html) explains the method in plain
language; [METHODS.md](METHODS.md) has the code-level detail. Everything below reproduces from the code.*

## Summary

*Revised 2026-11-15: the cost side was rebuilt. The earlier anchor (Pasitka et al. 2024) turned out to count a
kilogram that is mostly liquid and to leave out the cost of the plant, so it is no longer used. The default is
now a company's reported cost on a sound basis, and the floor is derived from physics. The demand side is
unchanged. Details: METHODS.md, "Changes of 2026-11-14/15".*

All costs are per kg of real cells: about 70% water and 20% protein, like meat. Plant costs are in 2025 prices.

- **As a company reports it,** cultivated chicken would cost about **$29.5/kg of cells, ~2.9× everyday meat** ($34
  in the shop vs a $12 benchmark). This is SuperMeat's 2024 figure for 100% cell mass, from 10-litre runs scaled on
  paper to 25,000-litre tanks. It is not peer reviewed and leaves out a return on capital. Across the plausible
  range of costs the median is 3.1×; no draws reach parity.
- **The floor is about $13/kg, ~1.5× everyday meat,** if everything that has been costed for animal cells works
  together: a sterile plant without clean rooms, perfusion in 20,000-litre tanks, efficient cells, floor-price
  medium. Each piece has been shown or claimed somewhere, never together.
- **Price parity needs a cheaper class of plant.** Plants for yeast and other microbes are built today for about
  a quarter of the cost per cubic metre. In such a plant the floor would be about **$6.5/kg**, just below the $7
  that parity needs. Nobody has built or costed one for animal cells. This is the frontier that decides whether
  cultivated meat can match the price of everyday meat.
- **At equal price,** once familiar, it wins **~49%** of the market if seen as real meat, **~10%** if not. Taste and
  the value shoppers put on “no slaughter” move this between ~12% and ~75%.
- **At the default cost** that adds up to **~0.3% of world meat by weight** (Monte Carlo median; 80% range
  0.1–1.5%), **1.8% in Europe**. At the default settings exactly, 1.4% of world meat and 3.6% in the US; at the
  floor, 16% in the US. Counted in animals it would be lower: most are chickens, where cultivated does worst.
  These shares are best read as upper estimates: the model gives a real-meat product at a premium far more share
  than organic chicken actually has (§2).
- **Where:** beef and seafood. Chicken and pork stay dearer even at the floor. A few luxury products are beatable
  on price already, but tiny.
- **When:** these are long-run ceilings; adoption reaches 90% of its long-run share after about 30 years.

**For funders:** in order, cheaper classes of plant for animal cells, better cells (efficient, fast-growing,
robust), a way to hold cells back in large tanks, and medium cost at production scale.

## 1. Cost and the price ratio

| case | cells, $/kg | R vs $12 meat | source and status |
|---|---|---|---|
| cautious: pharma-style plant, cells at half the density, reported medium | $49.2 | 4.52 | physics-based plant cost (`floor_physics.py`); nearer to reported harvests |
| **as reported by a company (default)** | **$29.5** | **2.87** | SuperMeat 2024; 10 L runs scaled on paper; depreciation only; not peer reviewed |
| Humbird's fed-batch design, 2025 prices | $24.6 | 2.47 | a detailed design with efficient cells; not built |
| cautious floor: pharma-style plant, tanks drained and refilled | $19.6 | 2.05 | physics-based; efficient cells not shown |
| **floor: no clean rooms, perfusion, efficient cells** | **$13.2** | **1.52** | physics-based; each piece shown separately, never together |
| **frontier: the floor in a microbial-class plant** | **$6.5** | **0.96** | such plants exist for microbes; none built or costed for animal cells |
| physics limit | $3.2 | 0.69 | a bound, not a design |

**The default.** SuperMeat reports 30.5 L of medium per kg at under $0.50/L, and $13.4/lb ($29.5/kg) in all "with
depreciation". Its kilogram is 100% cells at a realistic weight per cell. It is a company's claim, and it does
not include a return on the money invested in the plant. Humbird's independent design for efficient cells comes
to $25–47/kg in 2025 prices, and the published design analyses as a whole to about $18–65/kg with capital counted
(METHODS.md, "Other analyses").

**The floor is physics divided into engineering.** The plant's cost per kg is its cost per m³ of tank divided by
what a m³ produces in a year. Output is limited by how much oxygen and CO₂ a tank can exchange without bubbles
killing the cells. Plant cost per m³ comes from Humbird's design: about $900k with clean rooms, about $800k
without. Microbial fermentation plants are built for about $190k. The model reports the floor together with the
frontier and the cautious case, because which one applies depends on what can be made to work (METHODS.md, "The
floor's plant term").

**How the tank is run matters less than the plant and the cells.** Perfusion is worth about $5/kg at the floor
against tanks that are drained and refilled; removing clean rooms saves about a tenth of the plant cost; a
microbial-class plant halves the floor.

The medium and the plant matter most; no single lever reaches parity on its own (the best, efficient cells, gets
to R ≈ 1.92).

```
basic product vs commodity meat ($12/kg), Monte Carlo over the cost inputs (N=20,000):
  price ratio R:   P50 = 3.09   80% CI [2.36, 3.99]   90% CI [2.19, 4.27]
  long-run share:  P50 = 0.5%   80% CI [0.0, 5.0]
  0% of draws reach parity (R ≤ 1)
```

The median is above the default 2.87 because the plant-cost range is wider on the high side: the reported figure
leaves out a return on capital, and reported harvests are less dense than the floor assumes. The Monte Carlo does
not include the frontier.

## 2. What share a price buys

| if cultivated meat, at equal price and once familiar… | share |
|---|---|
| tastes as good and is seen as real meat | **~49%** |
| tastes a little worse (0.8) / noticeably worse (0.6) | ~26% / ~12% |
| tastes as good, and “no slaughter” matters (0.5 / 1.0 / 1.5) | ~59% / ~68% / ~75% |
| tastes as good but isn't seen as real meat | ~10% |

At first contact it gets ~6% (a US choice experiment found ~5%); at the default cost, ~4% in the long run (US).
Checks: adding cultivated takes 44 points from conventional meat and only 0.6 from plant-based; the same model
predicts ~15% for plant-based milk, close to reality (a weak test, since milk's inputs are set by hand).

**A harder check fails.** Organic chicken is real chicken at 1.44× the price of regular cuts, and takes ~2.4% of US
chicken. The model gives a real-meat product equal to conventional in all but price, at that premium, ~33% (~12%
at 2.6× mince). No κ inside the range the one price experiment on cultivated meat allows closes the gap (κ = 10
still gives ~18%), so it is not a matter of tuning κ: the choice model gives a nearly identical, dearer product a
sizeable share. So shares above equal price are best read as upper estimates. The most consequential demand
assumption above parity is how price-sensitive a cultivated product is relative to meat overall (κ = 4; the range
now runs 3–9, the most that experiment allows, because of this check: 8.1% at κ = 3, 4.4% at 4, 0.2% at 9, US
everyday meat at the default cost).

## 3. By type of meat (US)

```
                            default cost        cost floor
  meat type          $/kg    R     share        R     share
  chicken mince        5    6.89    0.1%       3.64    4.1%
  beef mince          11    3.13    3.9%       1.65   29.5%
  beef steak          20    2.02   10.8%       1.21   31.3%
  wagyu (premium)     45    0.90   19.7%       0.54   26.0%
  pork (processed)     8    4.31    1.1%       2.28   16.3%
  seafood fillet      24    1.69   15.7%       1.01   38.5%
  sushi-grade (prem.) 40    1.01   18.0%       0.61   24.2%
  TOTAL by weight: default 3.6%, at the floor 16.1%
```

Premium products get the biggest share of their category at the default cost, but authenticity holds them to
about a quarter even at the floor, and their markets are small. At the floor, seafood fillets, beef cuts and beef
mince lead; chicken stays under 10%.

## 4. By region

```
total cultivated penetration of meat (N=30,000), 80% CI [P10, P90]:
  region   income/cap   by VOLUME (impact)        by VALUE ($ market)
  Europe    $62k        P50  1.8%  [0.4,  7.2]    P50  3.6%  [ 0.8, 12.6]  <- easiest (rich + priciest meat)
  US        $86k        P50  0.9%  [0.2,  3.8]    P50  2.0%  [ 0.5,  6.9]
  Global    $24k        P50  0.3%  [0.1,  1.5]    P50  0.9%  [ 0.2,  3.3]
  China     $27k        P50  0.5%  [0.1,  2.0]    P50  1.7%  [ 0.4,  5.3]
  Brazil    $22k        P50  0.1%  [0.0,  0.5]    P50  0.2%  [ 0.0,  1.0]
  India     $11k        P50  0.1%  [0.0,  0.2]    P50  0.2%  [ 0.0,  0.7]
  Nigeria    $6k        P50  0.0%  [0.0,  0.1]    P50  0.0%  [ 0.0,  0.1]  <- hardest (cheap meat + price-sensitive)
```

Dear meat and rich shoppers make Europe easiest; cheap meat and price-sensitive shoppers make low-income regions
hardest. The explorer's point estimates at the defaults are higher (Global 1.4%, Europe 6.7%, US 3.6%): they hold κ
at 4 and the plant cost at its reported value, while the band samples κ up to 9 and plant costs up to the cautious
case. World beef is priced by consumption-weighted country prices (METHODS.md, "World beef price").
Against sushi-grade salmon, a structured product is at or below parity in 24% of draws, but structuring cost is
unmeasured.

## 5. Entry points, and timing

Luxury products compared at their everyday grade (farmed salmon, crossbred wagyu) are already beatable: foie gras,
bluefin tuna, sea urchin, wagyu. Lobster is at parity. Each is a small market. Commodity beef, pork and chicken,
where the volume is, stay out of reach even at the floor. Foie gras stands out: unstructured, expensive, and
increasingly banned on welfare grounds.

From a near-zero start, cultivated meat reaches ~0.5% after 10 years and ~4% after 30 (US, everyday meat, costs
held fixed), and 90% of its long-run share after about 30 years (15 to 73 across the plausible speeds at which
wariness fades). Current wariness (surveys: 5–60%) sets the speed, not the ceiling.

## 6. What to fund

1. **Cheaper classes of plant for animal cells:** whether animal cells can be grown in plants built like those
   for yeast and other microbes. It is the only route the model finds to price parity, and nobody has built or
   costed one.
2. **Better cells:** lines that waste little glucose, make little ammonia, grow fast and reach high density. The
   floor assumes them; nobody has shown them at scale.
3. **A way to hold cells back in large tanks:** perfusion stops at about 2,000 litres today because of filters.
4. **Medium cost at production scale:** verify the $0.50/L and sub-$0.20/L reports on a stated mass basis.
5. **Open, comparable data:** cost claims per kg of dry matter or protein, with capital included (METHODS.md, "A
   checklist for cost claims"). Most published analyses leave out all or part of the cost of capital.
6. **Structuring cost:** the biggest unmeasured number; it gates premium seafood.

A meat tax also works: raising conventional prices 25% lowers R as much as a 20% cut in every cost. Most of these
are public goods that industry underfunds.

## 7. What would change the conclusions

- **Up:** animal cells grown in a plant built like a microbial fermentation plant; efficient cells shown at pilot
  scale with a full mass balance; perfusion with a scalable way to hold cells back at 20,000 litres; medium below
  $0.30/L confirmed at scale.
- **Down:** if the reported figures do not survive review or scale-up; cells that reach only half the density in
  a pharma-style plant (R ≈ 4.5); contamination losses in long runs, which the model does not count.
- **What rests on one source.** The default is one company's report. The floor's plant costs are one engineer's
  design (Humbird 2021) in 2025 prices. Neither has been reproduced.
- **Demand:** acceptance and the value of “no slaughter” can't be measured before launch; the model carries the
  full range (10% to 75% at equal price).

Figures: `python report_figures.py` (cost vs inputs, cost waterfall, share tornado, share vs price, timing paths,
penetration by type and region). Parameters and sources: `python inputs.py`.
