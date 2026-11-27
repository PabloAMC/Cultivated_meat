# Cultivated meat as an even more premium meat, competing with welfare labels for premium buyers

> Names (2026-11-19): the two examples are named by what they assume (the low-lactate example, the all-favourable example). Cells are described by their traits, never as a named kind of cell.

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50; cut cost rebuilt (0.8 cells + $2 matrix + $2 assembly beyond mince), cuts cheaper.

> Repinned 2026-11-19 (audit batch): cells dearer (ammonia tolerance 4 mM), seafood re-priced by consumption, the tier rule replaced by a blend penalty, the equal-price share drawn around its 13% setting; see audit_2026-11-19.md.

> Repinned 2026-11-19 (second round): shoppers' liking is a Student's t spread (standard deviation 3.9 utils, 4 degrees of freedom) on a 67-point grid, not a normal spread of 5 on fifteen points; see liking_spread.md.

> Repinned 2026-11-21 (engine batch): the cost of cells moved (the all-favourable example $7.62 -> $6.97, its tank design now holds the culture thinner so its oxygen column passes its checks; the low-lactate example $49.50 -> $48.68; published cells $322.55 -> $316.11), because the design search runs a culture thinner when its loop fails, the building's power follows its floor and its class, and part of the crew is counted per tank. Nothing in the demand model changed; the shares that follow from the costs are recomputed.

> Repinned 2026-11-20 (engine batch): the scenarios' cells tolerate 35 mmol/L of lactate, bubble deaths and a harvest loss are charged, a washed tank takes twice the fed-batch crew, the membrane lasts 2,415 L/m2, and growth factors, utilities and the crew follow the Humbird back-test, so cells are dearer (the low-lactate example $32.80 to $49.96 a kilo, the all-favourable example $11.67 to $18.71, Published cells in fed-batch $209 to $323) and every share here fell; the demand model did not change; see full_review_2026-11-19.md and humbird_backtest.md.

> Repinned 2026-11-20 (final pass): the all-favourable example is now `scenarios.all_favourable()` ($18.71 to $7.62 a kilo of cells), the low-lactate example costs $49.50; the demand side is anchored on plant-based meat at 0.4% of meat by volume, incomes are nominal, conventional meat's price falls as cultivated meat takes sales, and the share of the world market closed by law is weighted by meat eaten (closed_markets.md).

> Repinned 2026-11-27 (the nitrogen and carbon balance: each case's cells are charged the amino acids their ammonia takes and the glucose they ferment). The all-favourable example costs $7.02 ($6.97); with premium buyers and a label its cells take 12.28% of world meat (12.41%), 13.67% with the strong no-killing value (13.80%) and 12.72% with no label (12.85%); the base with every shopper alike is about 12.0% (12.1%). The main model gives 20.38% (20.52%). The low-lactate example's cost and shares did not move. The conclusions are unchanged.

> Repinned 2026-11-27 (later; the blend rule is a curve: a cut that is 80% cells keeps 0.8^1.2 = 77% of the credit shoppers give real meat, not 80%; `hybrid_demand_evidence.md`). Costs did not move; every share that includes cuts fell by about a twentieth. With premium buyers and a label the all-favourable example's cells take 11.59% of world meat (12.28%), 12.91% with the strong no-killing value (13.67%) and 12.00% with no label (12.72%). The main model gives 1.37% and 19.76% (1.43% and 20.38%). The conclusions are unchanged.

Date: 2026-11-18. Code: `premium_buyers.py`; test: `tests/test_premium_buyers.py`. Builds on `premium_curve.md`. Nothing here changes a
default.

**Superseded in part (2026-11-18):** the premise that buyers of organic and welfare-labelled meat are cultivated meat's
price-insensitive buyers is contradicted by the two studies that split shoppers into groups (`demand_heterogeneity_evidence.md` §2),
and the model now has a spread of liking across all shoppers instead (`liking_spread.md`). The study is kept for what it says about
a welfare label on the same shelf. Its prices are the model's as it now stands, but its main class is the model before the spread
(every shopper alike): with no premium buyers and no label it gives under 0.001% at the low-lactate example and about 12% for the
all-favourable example's cells, against the model's 0.26% and 5.43% (0.05% and 5.58% before the price-insensitive shoppers of
2026-11-22's fifth batch; 13.03% and 6.07% for the base and the model before the fourth batch of 2026-11-21, when plant-based meat's
committed buyers raised the blend penalty on cuts; 11.43% and 5.44% at $7.62 a kilo, before 2026-11-21). Compare its shares with that base, not with the model's.
"The all-favourable example" here is its cells ($7.02 a kilo) with the model's ordinary demand, not the all-favourable example's
own 55% at equal price, which gives 25.0%. The change of the model's spread to a Student's t on 2026-11-19 moved only the model's
own figures; this study's shares, built on shoppers who are all alike, did not move then. The cost and demand changes of
2026-11-20 moved all of them.

Access levels: **FT** full text read; **ABS** abstract only; **SNIP** search snippet; **MEM** background knowledge, unchecked.

**The idea** (Pablo): shoppers may come to see cultivated meat as a step above organic or free-range chicken, if they value that no
animal is killed. But then it competes with those labels for the same group of shoppers. The main model cannot say this: each meat type
is a choice between conventional meat, plant-based, cultivated and a whole-food option, so no welfare label stands beside cultivated meat
and nobody is a "premium buyer".

## 1. What the module adds

- **Two classes of shopper.** The main class (90% of shoppers) is the main model as it is, with a weak liking for a welfare label. The
  premium class (10%) likes the label and is less price-sensitive. Both are fitted to the sixteen premium products of `premium_curve.md`,
  held to the at-parity elasticity Van Loo, Caputo and Lusk measured.
- **A fifth product on every shelf:** a welfare label (real meat, not slaughter-free) at 2× the conventional price (US organic chicken
  1.91×, Label Rouge 1.78×, cage-free eggs 2.0×). Products the model labels premium get none; they are the premium product already.
  Since seafood was re-priced on 2026-11-19 that includes the new row of premium fillets and shrimp (4% of volume) beside prime beef,
  sushi-grade seafood, organic chicken and heritage pork. Within each
  class, conventional meat, the label, cultivated meat, plant-based and the whole-food option share one logit, so cultivated meat and the
  label compete for the same shoppers.
- **Cultivated meat in the premium class** sells like a label priced lower by its net correction: the value of no killing over a
  welfare label, less novelty (half fading) and "unnatural" (`premium_curve.CORRECTIONS`: +5%, −15%, −20% of meat's price). "Even more
  premium" is a larger value of no killing. In the main class cultivated meat is the main model's.
- With no premium buyers and no label it reproduces the main model exactly; with no cultivated meat the label's share is the fitted
  premium curve (both tested).

## 2. The fits

| premium buyers, share of shoppers | their liking for a label (utils) | their price sensitivity κ | main class's liking | typical miss (rms log error) | at-parity elasticity |
|---|---|---|---|---|---|
| 5% | 0.73 | 1.95 | -1.35 | 0.897 | -2.69 |
| 10% | -0.00 | 2.17 | -1.95 | 0.893 | -2.35 |
| 20% | -0.62 | 2.38 | -3.83 | 0.890 | -1.31 |

**The premium products cannot tell the class sizes apart:** every size from 5% to 20% (and 30%, `premium_curve.md`) fits them equally well.
So the size has to come from who buys labels (section 4).

## 3. What it gives (long-run share of world meat by weight; premium buyers 10% of shoppers)

| no killing, valued over a welfare label (share of meat's price) | 4. Plus perfusion (the low-lactate example): share; sold to premium buyers; taken from the label, from conventional meat | 7. Plus everything else at its favourable end (the all-favourable example): share; sold to premium buyers; taken from the label, from conventional meat |
|---|---|---|
| +5% | 0.01%; 98%; 17%, 70% | 11.59%; 12%; 3%, 84% |
| +25% | 0.02%; 99%; 17%, 70% | 11.81%; 14%; 4%, 83% |
| +50% | 0.02%; 99%; 16%, 70% | 12.13%; 17%; 5%, 83% |
| +100% | 0.05%; 100%; 15%, 70% | 12.91%; 22%; 6%, 82% |
| the main model | 1.37% | 19.76% |
| +5%, no label on the shelf | 0.02% | 12.00% |

"Sold to premium buyers" is the share of cultivated meat's sales that go to the premium class. "Taken from" is where those sales come
from: the drop in each product's share when cultivated meat is added.

| premium buyers, share of shoppers | 4. Plus perfusion (the low-lactate example) | 7. Plus everything else at its favourable end (the all-favourable example) |
|---|---|---|
| 5% | 0.02% | 11.75% |
| 10% | 0.01% | 11.59% |
| 20% | 0.01% | 10.95% |

- **Premium buyers give the low-lactate example nearly all of its share in this study, and it is very little**: from the
  base's under 0.001% to 0.01% (0.015% unrounded; 0.020% before the fourth batch of 2026-11-21), with the evidence's +5% value of
  no killing; 98% of those sales go to the premium class. **That is about a seventeenth of the model's 0.26%** (a third of its 0.05%
  before 2026-11-22): the model's price-insensitive shoppers, who like cultivated meat as much as others in utils and respond a
  ninth as strongly to price, give far more buyers at a high price than this study's premium class, built on shoppers who are
  all alike and drawn to a welfare label. (After the
  2026-11-20 engine batch: 0.022% against 0.05%; before it: 0.03% to 0.17%, against the model's 0.21%. With the normal spread
  the model gave 0.08% and the study was above it.) The all-favourable example's cells rise less, from about 12% to 11.59%. That is
  2.3 times the model's 5.43% (12.41% against 5.48% before 2026-11-27; 12.49% against 5.58% before 2026-11-22; 13.03% to 13.44% against 6.07% before the fourth batch of 2026-11-21; 11.43% to 11.88% against 5.44% at $7.62, before 2026-11-21). **Changed again in the final pass of 2026-11-20:** the base with every shopper alike (12.19%) is
  now well above the model (5.58%); after the engine batch it was a little below (1.07% against 1.13%). At $7.02 a kilo most of
  the example's products are within three times their meat's price and several below it, where shoppers who are all alike buy
  more than the model's spread gives; at $18.71 they were further from it, where the spread holds more. So the study's excess
  over the model there comes from the base, not from the premium buyers. (Before the 2026-11-19 audit batch: 0.25% to 0.61% at
  the low-lactate example, 10.7% to 11.35% in the all-favourable example.)
- **"Even more premium" helps, but slowly.** Valuing no killing at a whole extra meat price (+100%) takes the low-lactate
  example to 0.05% and the all-favourable example's cells to 12.91%. Cultivated chicken at the low-lactate example's price is 7.7
  times chicken cuts' and 14.4 times processed chicken's, so even shoppers who value it highly mostly don't pay.
- **Competing for the same shoppers costs a sixth of the share in this model**: the low-lactate example is 0.018% with no label
  on the shelf and 0.015% with one (the all-favourable example: 12.00% and 11.59%). At the low-lactate example cultivated meat
  takes 15–17% of its sales from the label and about 71% from conventional meat; at the all-favourable example 3–6% and 82–84%.
- **But that last figure is the logit's assumption, and it is the weak point.** Within a class, a logit takes share from each product in
  proportion to its share. If premium buyers instead treated cultivated meat and the label as close substitutes, most of what cultivated
  meat sells to them (98% of its sales at the low-lactate example) would come out of the label. So the truth for "taken from
  the label" lies between a sixth and nearly all at the low-lactate example. That matters for impact more than for share: a
  tonne sold to a premium buyer replaces a higher-welfare bird.
- **The size of the premium class matters little** (0.02–0.03% at the low-lactate example across 5–20%), because the fit
  trades size against liking.

## 4. How many shoppers are premium buyers (evidence)

| finding | source | measure | access |
|---|---|---|---|
| 59% of French adults eat organic at least monthly; 37% of those eat organic poultry: about 22% eat organic poultry at some frequency | Agence Bio / ObSoCo barometer 2026 (fieldwork 2025), n = 6,127 | survey, persons | FT |
| 83% of GB households buy some organic in a year; 42% of households account for 95% of organic spend | Soil Association Organic Market Report 2026 (Worldpanel/NielsenIQ panel, 2025) | household panel, value | FT |
| 0.6% of UK chicken purchases carried an organic or Freedom Food label | Gschwandtner et al. 2024 (Kantar Worldpanel 2016, 26,658 households) | purchase occasions | FT |
| organic/natural meat demand is more price-elastic than no-claim demand (beef −1.39 against −0.47) | Luke, Tonsor & Schroeder, ARER 2026 (Circana scanner data 2009–18, US) | category elasticity | FT (text) |
| Label Rouge about 15–20% of French whole-chicken sales, much less for cuts | — | volume | MEM |

Habitual premium buyers are far fewer than occasional ones, and buying is concentrated. The study takes the premium class as **10% of shoppers
(80% range 4–20%)**: about 5–8% in the UK and US, 12–20% in France. That is a rough judgement made while building the model with an AI assistant; not measured and not reviewed by an expert. Shoppers who only sometimes buy a label belong in the main class.

**A caution on the class's low price sensitivity.** The fit gives premium buyers κ ≈ 2 against the main class's 8.5, from how slowly
premium products' shares fall with their premium across products. Scanner data measure something else, the response of one category's
sales to its own price, and find organic and natural meat *more* price-elastic than conventional. Both can hold: occasional buyers
leave a label when its price rises while habitual buyers stay. But no study splits the elasticity by kind of buyer, so the premium class's
low price sensitivity is a fit, not a measurement.

**Overlap with interest in cultivated meat** was not found as a cross-tabulation. Willingness to eat cultivated meat tracks perceived
ethics, not income or education (a meta-analysis, SNIP), while organic buying rises with income (Gschwandtner et al.). The EIT Food
Consumer Observatory (2025, FT) finds omnivores who see organic meat as the responsible choice but are "priced out" of it. So the overlap
is probably partial, and may run more through people who want premium meat than through those who buy it.

## 5. What this says

- With premium buyers and a welfare label on the shelf the low-lactate example's share is 0.01% (0.015%), against under 0.001%
  without them and the model's 0.26%. With a strong no-killing value, a whole meat price against the evidence's +5% (−5% to +20%), it
  is 0.05%. Nothing here takes it past 0.1% (before the 2026-11-20 engine batch the strong value gave 0.47%; before the audit
  batch, 1.16%): at 7.7–14.4 times chicken's price no segment is big enough or keen enough to change the answer.
- Near parity (the all-favourable example's cells) the effect is smaller in relative terms: 11.59% against the base's about 12%
  (12.91% with the strong value).
- What cultivated meat displaces matters for its animal impact: between about a sixth and nearly all of its sales at the
  low-lactate example could come from welfare-labelled meat rather than factory-farmed meat.
- **What would have to be true for premium buyers to raise the low-lactate example's long-run share above the main model's:**
  since 2026-11-22 no value of no killing in the study's range does (0.02% at +25%, 0.03% at +50%, 0.05% at +100%, against the
  model's 0.26%); before, about 80% of meat's price (against the model's 0.05%; about 60% before the fourth batch of 2026-11-21),
  where the evidence gives +5% (−5% to +20%). The model's price-insensitive shoppers do the work the premium class was meant to do. (The alternative, as before, is that novelty and the "unnatural" image keep premium buyers
  away, which the corrections' unfavourable end gives.) No setting in this study takes the low-lactate example near 1%.

## Sources

1. Agence Bio / L'ObSoCo, Baromètre de consommation et de perception des produits biologiques en France, 2026. https://lobsoco.com/wp-content/uploads/2026/02/LObSoCo_Agence-Bio_Barometre-2026-VDEF.pdf (FT)
2. Soil Association, Organic Market Report 2026. (FT, via a mirror: https://chilealimentos.com/wp-content/uploads/2026/03/soil-association-certification-organic-market-report-2026.pdf)
3. Gschwandtner et al. 2024, International Journal of the Economics of Business. https://kar.kent.ac.uk/106136/ (FT)
4. Luke, Tonsor & Schroeder 2026, Agricultural and Resource Economics Review 55(1). https://www.cambridge.org/core/product/13E1F30B93A6F9EAF11DF23236BAE171/core-reader (FT, tables did not render)
5. EIT Food Consumer Observatory, cultured meat factsheets, 2025. https://assets.eitfood.eu/files/EIT-Food-Consumer-Observatory_Cultured-Meat_Factsheets_V4_2025-05.pdf (FT)
