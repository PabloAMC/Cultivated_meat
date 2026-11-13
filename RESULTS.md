# Cultivated meat: how far can it get? — results

*Findings of a cost and demand model anchored to Pasitka et al. (Nature Food 2024), the only peer-reviewed cost
study built on measured production data, and to Humbird's (2021) feedstock floor. The
[interactive explorer](https://pabloamc.github.io/Cultivated_meat/interactive.html) explains the method in plain
language; [METHODS.md](METHODS.md) has the code-level detail. Everything below reproduces from the code.*

## Summary

*Revised 2026-11-13 after an independent review: premium tiers' price sensitivity is applied as documented, κ is
sampled (range 3–9), world beef is priced by consumption weights, the price-ratio weight is an input, and the
adoption time is measured against the long-run share. Details: METHODS.md, "Changes of 2026-11-13".*

*Revised 2026-11-14: the plant cost now includes the yearly capital charge (14.6% of the plant's cost) that
Pasitka lists in its supplement but leaves out of its published cost per kg. That adds $8.6/kg to the default
design and $5.5/kg to the floor, and roughly halves the shares below. Price sensitivity is unchanged: it stays
calibrated at the earlier $29/kg price. Details: METHODS.md, "Changes of 2026-11-14".*

- **Price:** made at scale with today's technology, cultivated meat would cost **~3.1× everyday meat** ($38 vs a
  $12 benchmark). Across the plausible range of costs, the median is 2.7×; no draws reach parity.
- **Floor:** cells can't cost less than **~$13.2/kg** (feedstock plus a minimal plant, its capital included); parity
  needs $7. So even at the floor, cultivated meat is ~1.5× the price. The plant term is Pasitka's; on Humbird's
  independent plant costs the floor would be about $16/kg.
- **At equal price,** once familiar, it wins **~49%** of the market if seen as real meat, **~10%** if not. Taste and
  the value shoppers put on “no slaughter” move this between ~12% and ~75%.
- **At today's cost** that adds up to **~0.5% of world meat by weight** (Monte Carlo median; 80% range 0.1–2.1%),
  **2.8% in Europe**. Counted in animals it would be lower: most are chickens, where cultivated does worst.
  These shares are best read as upper estimates: the model gives a real-meat product at a premium far more
  share than organic chicken actually has (§2).
- **Where:** beef and seafood. Chicken and pork stay dearer even at the floor. Luxury products are already
  beatable on price, but tiny.
- **When:** these are long-run ceilings; adoption reaches 90% of its long-run share after about 30 years.
- **A caveat on the anchor (unresolved):** Pasitka's biomass figures count 10 ng of wet mass per cell. Its own data
  imply far less: about 0.5 ng from the measured cell diameter (~10 µm), about 3.3 ng from the reported density
  (43% w/v at 130 million cells per mL). If its cost analysis rests on the same conversion, every cost per kg here
  is too low by a factor of three or more. The paper's Methods would settle it (METHODS.md, "Wet mass per cell").

**For funders:** the binding constraints are reactor scale-up and medium cost at production scale, plus
independent at-scale plant-cost data.

## 1. Cost and the price ratio

| Pasitka reactor design | cells, $/kg | R vs $12 meat |
|---|---|---|
| two large perfusion reactors (25 m³ each) | $27.5 | 2.71 |
| ten 5 m³ vessels (default) | $32.6 | 3.13 |
| twenty-five 2 m³ vessels (scale-up stalls) | $55.7 | 5.06 |

Each includes the yearly capital charge ($5.5, $8.6 and $16.9 per kg); Pasitka's published figures ($22, $24 and
$38.8) leave it out.

All three designs are perfusion: the cells stay in the vessel behind a retention device while medium flows
through. The cheapest one runs it in 25,000 L vessels, which nobody has shown publicly: perfusion with cell
retention is used commercially up to about 2,000 L, and Humbird caps it there. On Humbird's like-for-like
engineering, perfusion ($51/kg) costs more than fed-batch in 20,000 L stirred tanks ($37/kg), because the
retention devices and the many small vessels outweigh its higher productivity. So the default (5,000 L) and
above all the large design lean optimistic on reactor type (METHODS.md, "Reactor type and mode").

“Today's cost” is this projection for a large plant, not current pilot production. The medium ($0.63/L measured;
companies report $0.20/L or less, unverified at scale) and reactor scale matter most; no single lever reaches
parity on its own (the best gets to R ≈ 2.25). Reactor scale is the least demonstrated step and the biggest
downside.

```
basic product vs commodity meat ($12/kg), Monte Carlo over the cost inputs (N=20,000):
  price ratio R:   P50 = 2.72   80% CI [2.21, 3.31]   90% CI [2.08, 3.49]
  long-run share:  P50 = 1.1%   80% CI [0.1, 7.2]
  0% of draws reach parity (R ≤ 1)
```

The median is below 3.13 because cell efficiency can only improve on today's cells.

## 2. What share a price buys

| if cultivated meat, at equal price and once familiar… | share |
|---|---|
| tastes as good and is seen as real meat | **~49%** |
| tastes a little worse (0.8) / noticeably worse (0.6) | ~26% / ~12% |
| tastes as good, and “no slaughter” matters (0.5 / 1.0 / 1.5) | ~59% / ~68% / ~75% |
| tastes as good but isn't seen as real meat | ~10% |

At first contact it gets ~6% (a US choice experiment found ~5%); at today's price, ~3% in the long run (US).
Checks: adding cultivated takes 44 points from conventional meat and only 0.6 from plant-based; the same model
predicts ~15% for plant-based milk, close to reality (a weak test, since milk's inputs are set by hand).

**A harder check fails.** Organic chicken is real chicken at 1.44× the price of regular cuts, and takes ~2.4% of US
chicken. The model gives a real-meat product equal to conventional in all but price, at that premium, ~33% (~12%
at 2.6× mince). No κ inside the range the one price experiment on cultivated meat allows closes the gap (κ = 10
still gives ~18%), so it is not a matter of tuning κ: the choice model gives a nearly identical, dearer product a
sizeable share. So shares above equal price are best read as upper estimates. The most consequential demand
assumption above parity is how price-sensitive a cultivated product is relative to meat overall (κ = 4; the range
now runs 3–9, the most that experiment allows, because of this check: 5.9% at κ = 3, 2.9% at 4, 0.1% at 9, US
everyday meat at today's price).

## 3. By type of meat (US)

```
                            today's cost        cost floor
  meat type          $/kg    R     share        R     share
  chicken mince        5    7.52    0.0%       3.64    4.1%
  beef mince          11    3.42    2.5%       1.65   29.5%
  beef steak          20    2.18    8.5%       1.21   31.3%
  wagyu (premium)     45    0.97   18.6%       0.54   26.0%
  pork (processed)     8    4.70    0.6%       2.28   16.3%
  seafood fillet      24    1.82   12.8%       1.01   38.5%
  sushi-grade (prem.) 40    1.09   16.9%       0.61   24.2%
  TOTAL by weight: today 2.7%, at the floor 16.1%
```

Premium products get the biggest share of their category today, but authenticity holds them to about a quarter
even at the floor, and their markets are small. At the floor, seafood fillets, beef cuts and beef mince lead;
chicken stays under 10%.

## 4. By region

```
total cultivated penetration of meat (N=30,000), 80% CI [P10, P90]:
  region   income/cap   by VOLUME (impact)        by VALUE ($ market)
  Europe    $62k        P50  2.8%  [0.7,  9.2]    P50  5.3%  [ 1.4, 15.6]  <- easiest (rich + priciest meat)
  US        $86k        P50  1.3%  [0.3,  5.0]    P50  2.7%  [ 0.7,  8.6]
  Global    $24k        P50  0.5%  [0.1,  2.1]    P50  1.3%  [ 0.4,  4.2]
  China     $27k        P50  0.8%  [0.2,  2.6]    P50  2.3%  [ 0.6,  6.6]
  Brazil    $22k        P50  0.1%  [0.0,  0.7]    P50  0.3%  [ 0.1,  1.4]
  India     $11k        P50  0.1%  [0.0,  0.3]    P50  0.2%  [ 0.0,  0.9]
  Nigeria    $6k        P50  0.0%  [0.0,  0.1]    P50  0.0%  [ 0.0,  0.2]  <- hardest (cheap meat + price-sensitive)
```

Dear meat and rich shoppers make Europe easiest; cheap meat and price-sensitive shoppers make low-income regions
hardest. The explorer's point estimates at the defaults are higher (Global 1.0%, Europe 5.3%, US 2.7%): they hold κ at
4, while the band samples it up to 9. World beef is priced by consumption-weighted country prices (METHODS.md,
"World beef price"); an unweighted country average had put it above US beef.
Against sushi-grade salmon, a structured product is at or below parity in 41% of draws, but structuring cost is
unmeasured.

## 5. Entry points, and timing

Luxury products compared at their everyday grade (farmed salmon, crossbred wagyu) are already beatable: foie gras,
bluefin tuna, sea urchin, wagyu. Lobster is close (1.1×). Each is a small market. Commodity beef, pork and chicken, where the
volume is, stay out of reach even at the floor. Foie gras stands out: unstructured, expensive, and increasingly
banned on welfare grounds.

From a near-zero start, cultivated meat reaches ~0.3% after 10 years and ~2.6% after 30 (US, everyday meat, costs
held fixed), and 90% of its long-run share after about 30 years (15 to 73 across the plausible speeds at which
wariness fades). How wary shoppers are today (surveys: 5–60%) sets the speed, not the ceiling.

## 6. What to fund

1. **Medium cost at production scale:** verify the sub-$0.20/L reports, and whether $0.63/L is reproducible.
2. **Reactor scale-up:** large-volume animal-cell perfusion (oxygen and CO₂ transfer, sterility). If it stalls,
   R stays near 5.
3. **Independent plant-cost data at scale:** the largest term in the floor, and GFI's main data gap.
4. **Structuring cost:** the biggest unmeasured number; it gates premium seafood.

A meat tax also works: raising conventional prices 25% lowers R as much as a 20% cut in every cost. Most of these
are public goods that industry underfunds.

## 7. What would change the conclusions

- **Up:** peer-reviewed animal-cell perfusion at 20,000 L or more; medium below $0.30/L confirmed at scale.
- **Up:** a plant built for much less per tonne than Pasitka projects. Believer Meats' announced plant would
  cost about a fifth as much per tonne of capacity as Pasitka's default design, but it never ran at scale.
- **Down:** scale-up limits that bind, leaving R around 5; or a wet mass per cell well below the 10 ng in
  Pasitka's biomass figures (the caveat above), which would raise every cost per kg by the same factor. Humbird's
  independent plant cost (~$14.5/kg of non-nutrient cost in his most favourable design) now sits inside
  Pasitka's range with capital included ($11.5–18.5).
- **Demand:** acceptance and the value of “no slaughter” can't be measured before launch; the model carries the
  full range (10% to 75% at equal price).

Figures: `python report_figures.py` (cost vs inputs, cost waterfall, share tornado, share vs price, timing paths,
penetration by type and region). Parameters and sources: `python inputs.py`.
