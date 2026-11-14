# Cultivated meat: how far can it get? — results

*Findings of a cost and demand model. Costs rest on Humbird's (2021) engineering analysis and on a physics-based
floor; Pasitka et al. (Nature Food 2024) supplies the default cost stack, read as a projection (§1). The
[interactive explorer](https://pabloamc.github.io/Cultivated_meat/interactive.html) explains the method in plain
language; [METHODS.md](METHODS.md) has the code-level detail. Everything below reproduces from the code.*

## Summary

*Revised 2026-11-14. Three changes, all on the cost side: (1) the plant cost includes the capital charge Pasitka
leaves out of its published cost per kg; (2) costs are read per kg of real cells, after finding that Pasitka's
"wet biomass" is mostly liquid, so its cost per kg is not a cost per kg of meat; (3) the floor's plant term is
derived from physics. The demand side is unchanged (its price sensitivity stays calibrated at $29/kg). Earlier
revision (2026-11-13, independent review): METHODS.md. Details of this one: METHODS.md, "Changes of 2026-11-14".*

All costs are per kg of real cells: 70% water and about 20% protein, like meat. Plant costs are in 2025 prices.

- **The one peer-reviewed measured run** (Pasitka 2024), restated per kg of real cells, costs about **$220/kg,
  roughly 18× everyday meat**. The range is $86–593 because the paper does not report how wet its biomass was. A
  2024 company report (SuperMeat) claims about $30–55/kg, without peer review.
- **With efficient cells in a large plant, a projection:** about **$33/kg, ~3.1× everyday meat** ($38 in the shop
  vs a $12 benchmark). Efficient cells waste little glucose and make little ammonia; nobody has shown them at
  scale. The figure uses Pasitka's cost stack and sits inside Humbird's (2021) design range for such cells. Across
  the plausible range of costs the median is 2.75×; no draws reach parity. This is the case every share below
  refers to.
- **Floor:** about **$14/kg** with a sterile plant (feedstock $1.7 plus a plant cost of $12.5 derived from oxygen
  physics and Humbird's plant costs); parity needs $7. So even at the floor, cultivated meat is ~1.6× the price.
- **Parity needs a different class of plant.** If animal cells could be grown like yeast, in food-fermentation
  plants without clean rooms, the floor would be about $5/kg, below parity. Nobody has shown that. Physics alone
  allows about $3/kg.
- **At equal price,** once familiar, it wins **~49%** of the market if seen as real meat, **~10%** if not. Taste and
  the value shoppers put on “no slaughter” move this between ~12% and ~75%.
- **At the projected cost** that adds up to **~0.5% of world meat by weight** (Monte Carlo median; 80% range
  0.1–2.0%), **2.7% in Europe**. Counted in animals it would be lower: most are chickens, where cultivated does
  worst. These shares are best read as upper estimates: the model gives a real-meat product at a premium far more
  share than organic chicken actually has (§2).
- **Where:** beef and seafood. Chicken and pork stay dearer even at the floor. A few luxury products are beatable
  on price at the projected cost, but tiny.
- **When:** these are long-run ceilings; adoption reaches 90% of its long-run share after about 30 years.

**For funders:** the binding constraints are, in order, the cells themselves (efficient, fast-growing, robust
lines), the class of plant they can be grown in, and medium cost at production scale. Reactor type matters less
than it looked.

## 1. Cost and the price ratio

| case | cells, $/kg | R vs $12 meat | source and status |
|---|---|---|---|
| Pasitka's 2024 run, per kg of real cells | ~$220 (86–593) | ~18 (8–50) | the one peer-reviewed measured run, restated; a company report (SuperMeat 2024) claims $30–55 |
| projection: efficient cells, small vessels (scale-up stalls) | $55.7 | 5.06 | Pasitka's cost stack; efficient cells not shown at scale |
| **projection: efficient cells, large plant (default)** | **$32.6** | **3.13** | Pasitka's cost stack, inside Humbird's design range; efficient cells not shown at scale |
| projection: efficient cells, largest perfusion design | $27.5 | 2.71 | Pasitka's cost stack; perfusion at this size is "theoretical" in its own words |
| floor, sterile plant run continuously | $14.2 | 1.60 | physics-based (`floor_physics.py`), Humbird's plant costs in 2025 prices; not shown |
| floor, food-fermentation-class plant | $5.2 | 0.85 | physics-based, fermentation-plant costs; not shown for animal cells |

**What the default is.** The three projection rows use Pasitka's cost stack (22.4 L of medium at $0.63/L, plus its
plant costs with the capital charge added). Pasitka reports those per kg of "wet biomass", a centrifuged pellet
that is mostly liquid: about 15% cells by our estimate (5–40%), and 1% protein by its own cost table against ~20%
in meat. So they are not what its process delivers per kg of cells. The model keeps them as a projection because
they fall inside Humbird's independent range for efficient cells: $21/kg on hydrolysate, $37/kg on individual
amino acids, per kg of real cells in his 2019 prices (about $27–48 in 2025 prices). Details: METHODS.md, "Wet mass per cell".

**Reactor type.** All of Pasitka's designs are perfusion; the cheapest assumes it in 25,000 L vessels, which nobody
has shown (commercial perfusion stops near 2,000 L). In the physics-based floor, reactor type matters less than
expected: continuous harvest, larger vessels and cheap perfusion all land within $2/kg of each other. What moves
the floor is the class of plant: about $900k per m³ of vessel for a sterile, pharma-style plant (Humbird, in 2025 prices) against about $70k
for a food-fermentation plant (METHODS.md, "A physics-based floor").

The medium ($0.63/L in the default; companies report $0.20/L or less, unverified at scale) and plant scale matter
most within the projection; no single lever reaches parity on its own (the best gets to R ≈ 2.25).

```
basic product vs commodity meat ($12/kg), Monte Carlo over the cost inputs (N=20,000):
  price ratio R:   P50 = 2.75   80% CI [2.24, 3.33]   90% CI [2.12, 3.50]
  long-run share:  P50 = 1.0%   80% CI [0.1, 6.9]
  0% of draws reach parity (R ≤ 1)
```

The median is below 3.13 because cell efficiency can only improve on the projection. The Monte Carlo spans the
projection only; it does not include the restated Pasitka run.

## 2. What share a price buys

| if cultivated meat, at equal price and once familiar… | share |
|---|---|
| tastes as good and is seen as real meat | **~49%** |
| tastes a little worse (0.8) / noticeably worse (0.6) | ~26% / ~12% |
| tastes as good, and “no slaughter” matters (0.5 / 1.0 / 1.5) | ~59% / ~68% / ~75% |
| tastes as good but isn't seen as real meat | ~10% |

At first contact it gets ~6% (a US choice experiment found ~5%); at the projected price, ~3% in the long run (US).
Checks: adding cultivated takes 44 points from conventional meat and only 0.6 from plant-based; the same model
predicts ~15% for plant-based milk, close to reality (a weak test, since milk's inputs are set by hand).

**A harder check fails.** Organic chicken is real chicken at 1.44× the price of regular cuts, and takes ~2.4% of US
chicken. The model gives a real-meat product equal to conventional in all but price, at that premium, ~33% (~12%
at 2.6× mince). No κ inside the range the one price experiment on cultivated meat allows closes the gap (κ = 10
still gives ~18%), so it is not a matter of tuning κ: the choice model gives a nearly identical, dearer product a
sizeable share. So shares above equal price are best read as upper estimates. The most consequential demand
assumption above parity is how price-sensitive a cultivated product is relative to meat overall (κ = 4; the range
now runs 3–9, the most that experiment allows, because of this check: 5.9% at κ = 3, 2.9% at 4, 0.1% at 9, US
everyday meat at the projected price).

## 3. By type of meat (US)

```
                            projected cost      cost floor
  meat type          $/kg    R     share        R     share
  chicken mince        5    7.52    0.0%       3.84    3.2%
  beef mince          11    3.42    2.5%       1.75   26.7%
  beef steak          20    2.18    8.5%       1.26   29.6%
  wagyu (premium)     45    0.97   18.6%       0.56   25.6%
  pork (processed)     8    4.70    0.6%       2.40   14.0%
  seafood fillet      24    1.82   12.8%       1.05   36.8%
  sushi-grade (prem.) 40    1.09   16.9%       0.63   23.8%
  TOTAL by weight: projected 2.7%, at the floor 14.6%
```

Premium products get the biggest share of their category at the projected cost, but authenticity holds them to about a quarter
even at the floor, and their markets are small. At the floor, seafood fillets, beef cuts and beef mince lead;
chicken stays under 10%.

## 4. By region

```
total cultivated penetration of meat (N=30,000), 80% CI [P10, P90]:
  region   income/cap   by VOLUME (impact)        by VALUE ($ market)
  Europe    $62k        P50  2.7%  [0.7,  8.9]    P50  5.2%  [ 1.4, 15.1]  <- easiest (rich + priciest meat)
  US        $86k        P50  1.3%  [0.3,  4.8]    P50  2.7%  [ 0.7,  8.3]
  Global    $24k        P50  0.5%  [0.1,  2.0]    P50  1.3%  [ 0.3,  4.1]
  China     $27k        P50  0.7%  [0.2,  2.5]    P50  2.2%  [ 0.6,  6.4]
  Brazil    $22k        P50  0.1%  [0.0,  0.7]    P50  0.3%  [ 0.1,  1.3]
  India     $11k        P50  0.1%  [0.0,  0.3]    P50  0.2%  [ 0.0,  0.9]
  Nigeria    $6k        P50  0.0%  [0.0,  0.1]    P50  0.0%  [ 0.0,  0.2]  <- hardest (cheap meat + price-sensitive)
```

Dear meat and rich shoppers make Europe easiest; cheap meat and price-sensitive shoppers make low-income regions
hardest. The explorer's point estimates at the defaults are higher (Global 1.0%, Europe 5.3%, US 2.7%): they hold κ at
4, while the band samples it up to 9. World beef is priced by consumption-weighted country prices (METHODS.md,
"World beef price"); an unweighted country average had put it above US beef.
Against sushi-grade salmon, a structured product is at or below parity in 39% of draws, but structuring cost is
unmeasured.

## 5. Entry points, and timing

Luxury products compared at their everyday grade (farmed salmon, crossbred wagyu) are already beatable: foie gras,
bluefin tuna, sea urchin, wagyu. Lobster is close (1.1×). Each is a small market. Commodity beef, pork and chicken, where the
volume is, stay out of reach even at the floor. Foie gras stands out: unstructured, expensive, and increasingly
banned on welfare grounds.

From a near-zero start, cultivated meat reaches ~0.3% after 10 years and ~2.6% after 30 (US, everyday meat, costs
held fixed), and 90% of its long-run share after about 30 years (15 to 73 across the plausible speeds at which
wariness fades). Current wariness (surveys: 5–60%) sets the speed, not the ceiling.

## 6. What to fund

1. **Better cells:** lines that waste little glucose, make little ammonia, grow fast and are large. They are the
   difference between about $220/kg and about $33/kg, and nobody has shown them at scale.
2. **Cheaper classes of plant:** whether animal cells can be grown in large, food-grade vessels without clean
   rooms. This is the only route the model finds below price parity.
3. **Medium cost at production scale:** verify the sub-$0.20/L reports on a stated mass basis.
4. **Open, comparable data:** cost claims per kg of dry matter or protein, with capital included. Pasitka's
   kilogram is not comparable with meat, and most published analyses leave out all or part of the cost of capital.
5. **Structuring cost:** the biggest unmeasured number; it gates premium seafood.

A meat tax also works: raising conventional prices 25% lowers R as much as a 20% cut in every cost. Most of these
are public goods that industry underfunds.

## 7. What would change the conclusions

- **Up:** efficient cells shown at pilot scale with a full mass balance; animal cells grown at density in
  food-grade vessels of 100 m³ or more; medium below $0.30/L confirmed at scale. A company white paper (SuperMeat
  2024) claims about $26–30/kg of cell mass before capital from 10 L runs scaled to 25 m³; if that held up under
  review, the restated Pasitka figure above would be a poor guide to the field.
- **Down:** scale-up limits that bind, leaving R around 5 even with efficient cells; contamination losses in
  long continuous runs, which the floor does not model; plant costs above Humbird's design.
- **How this model sits among others.** Restated per kg of real cells with capital included, the published design
  analyses run from about $18 to $65/kg (CE Delft, Negulescu, Humbird, Garrison, Ark), all for efficient cells
  that have not been shown; the $33 default sits inside that range. None of them shares Pasitka's mass-basis
  problem (METHODS.md, "Other analyses").
- **Demand:** acceptance and the value of “no slaughter” can't be measured before launch; the model carries the
  full range (10% to 75% at equal price).

Figures: `python report_figures.py` (cost vs inputs, cost waterfall, share tornado, share vs price, timing paths,
penetration by type and region). Parameters and sources: `python inputs.py`.
