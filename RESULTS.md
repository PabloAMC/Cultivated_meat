# Cultivated meat: how far can it get? — results

*Findings of a cost and demand model anchored to Pasitka et al. (Nature Food 2024), the only peer-reviewed cost
study built on measured production data, and to Humbird's (2021) feedstock floor. The
[interactive explorer](https://pabloamc.github.io/Cultivated_meat/interactive.html) explains the method in plain
language; [METHODS.md](METHODS.md) has the code-level detail. Everything below reproduces from the code.*

## Summary

- **Price:** made at scale with today's technology, cultivated meat would cost **~2.4× everyday meat** ($29 vs a
  $12 benchmark). Across the plausible range of costs, the median is 2.1×; no draws reach parity.
- **Floor:** cells can't cost less than **~$7.5/kg** (feedstock plus a minimal plant); parity needs $7. So even at
  the floor, cultivated meat is ~1.04× the price.
- **At equal price,** once familiar, it wins **~49%** of the market if seen as real meat, **~10%** if not. Taste and
  the value shoppers put on “no slaughter” move this between ~12% and ~75%.
- **At today's cost** that adds up to **~2.5% of world meat by weight** (Monte Carlo median; 80% range 0.6–7.7%),
  **7.5% in Europe**. Counted in animals it would be lower: most are chickens, where cultivated does worst.
- **Where:** beef and seafood. Chicken and pork stay dearer even at the floor. Luxury products are already
  beatable on price, but tiny.
- **When:** these are long-run ceilings, reached in about 25 years.

**For funders:** the binding constraints are reactor scale-up and medium cost at production scale, plus
independent at-scale plant-cost data.

## 1. Cost and the price ratio

| Pasitka reactor design | cells, $/kg | R vs $12 meat |
|---|---|---|
| large perfusion reactors (20 m³) | $22 | 2.25 |
| ten 5 m³ vessels (default) | $24 | 2.42 |
| many 0.5 m³ vessels (scale-up stalls) | $38.8 | 3.65 |

“Today's cost” is this projection for a large plant, not current pilot production. The medium ($0.63/L measured;
companies report $0.20/L or less, unverified at scale) and reactor scale matter most; no single lever reaches
parity on its own (the best gets to R ≈ 1.5). Reactor scale is the least demonstrated step and the biggest
downside.

```
basic product vs commodity meat ($12/kg), Monte Carlo over the cost inputs (N=20,000):
  price ratio R:   P50 = 2.09   80% CI [1.63, 2.63]   90% CI [1.52, 2.79]
  long-run share:  P50 = 7.3%   80% CI [1.9, 22.4]
  0% of draws reach parity (R ≤ 1)
```

The median is below 2.42 because cell efficiency can only improve on today's cells.

## 2. What share a price buys

| if cultivated meat, at equal price and once familiar… | share |
|---|---|
| tastes as good and is seen as real meat | **~49%** |
| tastes a little worse (0.8) / noticeably worse (0.6) | ~26% / ~12% |
| tastes as good, and “no slaughter” matters (0.5 / 1.0 / 1.5) | ~59% / ~68% / ~75% |
| tastes as good but isn't seen as real meat | ~10% |

At first contact it gets ~6% (a US choice experiment found ~5%); at today's price, ~9% in the long run (US).
Checks: adding cultivated takes 44 points from conventional meat and only 0.6 from plant-based; the same model
predicts ~15% for plant-based milk, close to reality (a weak test, since milk's inputs are set by hand). The
most consequential demand assumption above parity is how price-sensitive a cultivated product is relative to
meat overall (κ = 4, range 3–6: 3.4% to 13.7% at today's price).

## 3. By type of meat (US)

```
                            today's cost        cost floor
  meat type          $/kg    R     share        R     share
  chicken mince        5    5.80    0.3%       2.50   15.2%
  beef mince          11    2.64    8.2%       1.14   48.4%
  beef steak          20    1.75   13.9%       0.93   42.0%
  wagyu (premium)     45    0.78   23.9%       0.41   36.8%
  pork (processed)     8    3.63    2.8%       1.56   34.7%
  seafood fillet      24    1.46   20.1%       0.77   49.6%
  sushi-grade (prem.) 40    0.88   20.9%       0.46   34.0%
  TOTAL by weight: today 5.0%, at the floor 27.3%
```

Premium products get the biggest share of their category today, but authenticity holds them to about a quarter,
and their markets are small; beef and seafood cuts displace the most meat. At the floor, cuts and beef mince lead.

## 4. By region

```
total cultivated penetration of meat (N=30,000), 80% CI [P10, P90]:
  region   income/cap   by VOLUME (impact)        by VALUE ($ market)
  Europe    $62k        P50  7.5%  [2.4, 18.2]    P50 12.3%  [ 4.1, 27.7]  <- easiest (rich + priciest meat)
  US        $86k        P50  4.1%  [1.2, 11.8]    P50  6.5%  [ 2.0, 17.0]
  Global    $24k        P50  2.5%  [0.6,  7.7]    P50  4.6%  [ 1.3, 13.1]
  China     $27k        P50  2.1%  [0.6,  6.0]    P50  5.0%  [ 1.5, 12.9]
  Brazil    $22k        P50  0.6%  [0.1,  2.4]    P50  1.0%  [ 0.2,  3.6]
  India     $11k        P50  0.1%  [0.0,  0.5]    P50  0.4%  [ 0.1,  1.3]
  Nigeria    $6k        P50  0.1%  [0.0,  0.3]    P50  0.1%  [ 0.0,  0.5]  <- hardest (cheap meat + price-sensitive)
```

Dear meat and rich shoppers make Europe easiest; cheap meat and price-sensitive shoppers make low-income regions
hardest. The explorer's point estimates at the defaults are a little higher (Global 2.9%, Europe 9.5%, US 5.0%).
Against sushi-grade salmon, a structured product is at or below parity in 83% of draws, but structuring cost is
unmeasured.

## 5. Entry points, and timing

Luxury products compared at their everyday grade (farmed salmon, crossbred wagyu) are already beatable: foie gras,
bluefin tuna, sea urchin, wagyu, lobster. Each is a small market. Commodity beef, pork and chicken, where the
volume is, stay out of reach even at the floor. Foie gras stands out: unstructured, expensive, and increasingly
banned on welfare grounds.

From a near-zero start, cultivated meat reaches ~1% after 10 years and ~8% after 30 (US, everyday meat, costs
held fixed), levelling off around year 25. How wary shoppers are today (surveys: 5–60%) sets the speed, not the
ceiling.

## 6. What to fund

1. **Medium cost at production scale:** verify the sub-$0.20/L reports, and whether $0.63/L is reproducible.
2. **Reactor scale-up:** large-volume animal-cell perfusion (oxygen and CO₂ transfer, sterility). If it stalls,
   R stays near 3.65.
3. **Independent plant-cost data at scale:** the largest term in the floor, and GFI's main data gap.
4. **Structuring cost:** the biggest unmeasured number; it gates premium seafood.

A meat tax also works: raising conventional prices 25% lowers R as much as a 20% cut in every cost. Most of these
are public goods that industry underfunds.

## 7. What would change the conclusions

- **Up:** peer-reviewed animal-cell perfusion at 20,000 L or more; medium below $0.30/L confirmed at scale.
- **Down:** scale-up limits that bind, leaving R around 3 or more.
- **Demand:** acceptance and the value of “no slaughter” can't be measured before launch; the model carries the
  full range (10% to 75% at equal price).

Figures: `python report_figures.py` (cost vs inputs, cost waterfall, share tornado, share vs price, timing paths,
penetration by type and region). Parameters and sources: `python inputs.py`.
