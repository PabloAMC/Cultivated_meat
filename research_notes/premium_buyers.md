# Cultivated meat as an even more premium meat, competing with welfare labels for premium buyers

> Names (2026-11-19): "Selected cells" was called Central; "Engineered cells, all favourable" was called the best case.

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50; cut cost rebuilt (0.8 cells + $2 matrix + $2 assembly beyond mince), cuts cheaper.

> Repinned 2026-11-19 (audit batch): cells dearer (ammonia tolerance 4 mM), seafood re-priced by consumption, the tier rule replaced by a blend penalty, the equal-price share drawn around its 13% setting; see audit_2026-11-19.md.

> Repinned 2026-11-19 (second round): shoppers' liking is a Student's t spread (standard deviation 3.9 utils, 4 degrees of freedom) on a 67-point grid, not a normal spread of 5 on fifteen points; see liking_spread.md.

Date: 2026-11-18. Code: `premium_buyers.py`; test: `tests/test_premium_buyers.py`. Builds on `premium_curve.md`. Nothing here changes a
default.

**Superseded in part (2026-11-18):** the premise that buyers of organic and welfare-labelled meat are cultivated meat's
price-insensitive buyers is contradicted by the two studies that split shoppers into groups (`demand_heterogeneity_evidence.md` §2),
and the model now has a spread of liking across all shoppers instead (`liking_spread.md`). The study is kept for what it says about
a welfare label on the same shelf. Its prices are the model's as it now stands, but its main class is the model before the spread
(every shopper alike): with no premium buyers and no label it gives 0.03% at Central and 5.4% for the best case's cells, against the
model's 0.16% and 2.74%. Compare its shares with that base, not with the model's. "The best case" here is its cells ($11.46 a kilo)
with the model's ordinary demand, not the best case's own 55% at equal price, which gives 13.8%. The change of the model's
spread to a Student's t on 2026-11-19 moved only the model's own figures; this study's shares, built on shoppers who are all alike,
did not move.

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
  sushi-grade seafood, organic chicken and heritage pork. Putting a label beside it too changes Central's share from 0.128% to 0.126%. Within each
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
| 5% | 0.84 | 1.94 | -1.21 | 0.897 | -2.68 |
| 10% | 0.11 | 2.15 | -1.76 | 0.893 | -2.37 |
| 20% | -0.50 | 2.36 | -3.22 | 0.890 | -1.47 |

**The premium products cannot tell the class sizes apart:** every size from 5% to 20% (and 30%, `premium_curve.md`) fits them equally well.
So the size has to come from who buys labels (section 4).

## 3. What it gives (long-run share of world meat by weight; premium buyers 10% of shoppers)

| no killing, valued over a welfare label (share of meat's price) | 4. Plus perfusion (Selected cells): share; sold to premium buyers; taken from the label, from conventional meat | 7. Plus everything else at its favourable end (Engineered cells, all favourable): share; sold to premium buyers; taken from the label, from conventional meat |
|---|---|---|
| +5% | 0.17%; 77%; 15%, 66% | 6.52%; 19%; 5%, 79% |
| +25% | 0.21%; 81%; 15%, 67% | 6.77%; 22%; 5%, 79% |
| +50% | 0.27%; 86%; 16%, 68% | 7.14%; 26%; 6%, 78% |
| +100% | 0.47%; 92%; 16%, 69% | 8.02%; 34%; 8%, 77% |
| the main model | 0.21% | 3.16% |
| +5%, no label on the shelf | 0.20% | 6.89% |

"Sold to premium buyers" is the share of cultivated meat's sales that go to the premium class. "Taken from" is where those sales come
from: the drop in each product's share when cultivated meat is added.

| premium buyers, share of shoppers | 4. Plus perfusion (Selected cells) | 7. Plus everything else at its favourable end (Engineered cells, all favourable) |
|---|---|---|
| 5% | 0.19% | 6.57% |
| 10% | 0.17% | 6.52% |
| 20% | 0.16% | 6.18% |

- **Premium buyers raise Central's share four times, but from very little**: from the base's 0.03% to 0.13%, with the evidence's
  +5% value of no killing. **That is now below the model's 0.16%**: the model's spread of liking, with its heavier tail since
  2026-11-19, already gives more buyers at a high price than this study's premium class adds to shoppers who are all alike. (With
  the normal spread the model gave 0.08% and the study was above it.) The best case's cells rise less, from 5.4% to 5.92%,
  because near parity the mainstream already decides the share. That is twice the model's 2.74% because the base has every shopper
  alike, not because of premium buyers. (Before the 2026-11-19 audit batch made cells dearer: 0.25% to 0.61% at Central, 10.7% to 11.35% in the best
  case.)
- **"Even more premium" helps, but slowly.** Valuing no killing at a whole extra meat price (+100%) takes Central to 0.37% and the best
  case's cells to 7.28%. Cultivated chicken at Central's price is 5.4 times chicken cuts' and 9.8 times processed chicken's, so even
  shoppers who value it highly mostly don't pay.
- **Competing for the same shoppers costs little in this model**: Central is 0.15% with no label on the shelf and 0.13% with one. Cultivated
  meat takes 15–16% of its sales from the label and about 66–69% from conventional meat.
- **But that last figure is the logit's assumption, and it is the weak point.** Within a class, a logit takes share from each product in
  proportion to its share. If premium buyers instead treated cultivated meat and the label as close substitutes, most of what cultivated
  meat sells to them (77% of its sales at Central, 92% at +100%) would come out of the label. So the truth for "taken from the label" lies
  between 15% and about three-quarters at Central. That matters for impact more than for share: a tonne sold to a premium buyer replaces a
  higher-welfare bird.
- **The size of the premium class matters little** (0.11–0.14% at Central across 5–20%), because the fit trades size against liking.

## 4. How many shoppers are premium buyers (evidence)

| finding | source | measure | access |
|---|---|---|---|
| 59% of French adults eat organic at least monthly; 37% of those eat organic poultry: about 22% eat organic poultry at some frequency | Agence Bio / ObSoCo barometer 2026 (fieldwork 2025), n = 6,127 | survey, persons | FT |
| 83% of GB households buy some organic in a year; 42% of households account for 95% of organic spend | Soil Association Organic Market Report 2026 (Worldpanel/NielsenIQ panel, 2025) | household panel, value | FT |
| 0.6% of UK chicken purchases carried an organic or Freedom Food label | Gschwandtner et al. 2024 (Kantar Worldpanel 2016, 26,658 households) | purchase occasions | FT |
| organic/natural meat demand is more price-elastic than no-claim demand (beef −1.39 against −0.47) | Luke, Tonsor & Schroeder, ARER 2026 (Circana scanner data 2009–18, US) | category elasticity | FT (text) |
| Label Rouge about 15–20% of French whole-chicken sales, much less for cuts | — | volume | MEM |

Habitual premium buyers are far fewer than occasional ones, and buying is concentrated. I take the premium class as **10% of shoppers
(80% range 4–20%)**: about 5–8% in the UK and US, 12–20% in France. Shoppers who only sometimes buy a label belong in the main class.

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

- With premium buyers and a welfare label on the shelf Central's share is 0.13%, against 0.03% without them and the model's 0.16%. With
  a strong no-killing value, a whole meat price against the evidence's +5% (−5% to +20%), it is 0.37%. Nothing here takes it past 1%
  (before the audit batch the strong value did, at 1.16%): at 5.4–9.8 times chicken's price no segment is big enough or keen
  enough to change the answer.
- Near parity (the best case's cells) the effect is smaller in relative terms: 5.92% against the base's 5.4% (7.28% with the strong
  value).
- What cultivated meat displaces matters for its animal impact: between about a sixth and three-quarters of its sales at Central could
  come from welfare-labelled meat rather than factory-farmed meat.
- **Judgement:** that premium buyers raise Central's long-run share above the main model's: about 0.4 (provisional; lowered from
  0.65 on 2026-11-19, second round). The study no longer shows it: its 0.13% is below the model's 0.16%, and only a no-killing
  value of about a third of meat's price or more takes it past the model (0.16% at +25%, 0.21% at +50%). The model's own spread of liking now does the work the
  premium class was meant to do. (The alternative, as before, is that novelty and the "unnatural" image keep premium buyers
  away, which the corrections' unfavourable end gives.) That the share at
  Central exceeds 1% by this route: about 0.03 (provisional; revised from 0.1 at the 2026-11-19 audit batch, when cells got dearer:
  even a no-killing value of a whole meat price now gives 0.37%).

## Sources

1. Agence Bio / L'ObSoCo, Baromètre de consommation et de perception des produits biologiques en France, 2026. https://lobsoco.com/wp-content/uploads/2026/02/LObSoCo_Agence-Bio_Barometre-2026-VDEF.pdf (FT)
2. Soil Association, Organic Market Report 2026. (FT, via a mirror: https://chilealimentos.com/wp-content/uploads/2026/03/soil-association-certification-organic-market-report-2026.pdf)
3. Gschwandtner et al. 2024, International Journal of the Economics of Business. https://kar.kent.ac.uk/106136/ (FT)
4. Luke, Tonsor & Schroeder 2026, Agricultural and Resource Economics Review 55(1). https://www.cambridge.org/core/product/13E1F30B93A6F9EAF11DF23236BAE171/core-reader (FT, tables did not render)
5. EIT Food Consumer Observatory, cultured meat factsheets, 2025. https://assets.eitfood.eu/files/EIT-Food-Consumer-Observatory_Cultured-Meat_Factsheets_V4_2025-05.pdf (FT)
