# Cultivated meat as an even more premium meat, competing with welfare labels for premium buyers

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50.

Date: 2026-11-18. Code: `premium_buyers.py`; test: `tests/test_premium_buyers.py`. Builds on `premium_curve.md`. Nothing here changes a
default.

**Superseded in part (2026-11-18):** the premise that buyers of organic and welfare-labelled meat are cultivated meat's
price-insensitive buyers is contradicted by the two studies that split shoppers into groups (`demand_heterogeneity_evidence.md` §2),
and the model now has a spread of liking across all shoppers instead (`liking_spread.md`). The study is kept for what it says about
a welfare label on the same shelf. Its shares are on the model's demand as it now stands.

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
  1.91×, Label Rouge 1.78×, cage-free eggs 2.0×). Wagyu-type premium tiers get none; they are the premium product already. Within each
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

| no killing, valued over a welfare label (share of meat's price) | 3. Plus cells selected to grow faster on the low-waste feed (Central): share; sold to premium buyers; taken from the label, from conventional meat | 5. Plus engineered cells: share; sold to premium buyers; taken from the label, from conventional meat |
|---|---|---|
| +5% | 0.25%; 79%; 21%, 72% | 3.90%; 34%; 10%, 81% |
| +25% | 0.29%; 82%; 22%, 72% | 4.13%; 37%; 11%, 80% |
| +50% | 0.36%; 86%; 23%, 71% | 4.46%; 42%; 12%, 79% |
| +100% | 0.56%; 91%; 24%, 69% | 5.25%; 51%; 15%, 77% |
| the main model | 0.13% | 2.74% |
| +5%, no label on the shelf | 0.32% | 4.33% |

"Sold to premium buyers" is the share of cultivated meat's sales that go to the premium class. "Taken from" is where those sales come
from: the drop in each product's share when cultivated meat is added.

| premium buyers, share of shoppers | 3. Plus cells selected to grow faster on the low-waste feed (Central) | 5. Plus engineered cells |
|---|---|---|
| 5% | 0.25% | 3.75% |
| 10% | 0.25% | 3.90% |
| 20% | 0.23% | 3.88% |

- **Premium buyers about double Central's share**, from the model's 0.13% to 0.25%, with the evidence's +5% value of no killing.
  The best case rises less, from 2.74% to 3.90%, because near parity the mainstream already decides the share.
- **"Even more premium" helps, but slowly.** Valuing no killing at a whole extra meat price (+100%) takes Central to 0.56% and the best
  case to 5.25%. Cultivated meat at Central's price is 4–6 times chicken's, so even shoppers who value it highly mostly don't pay.
- **Competing for the same shoppers costs little in this model**: Central is 0.32% with no label on the shelf and 0.25% with one. Cultivated
  meat takes 21–24% of its sales from the label and about 69–72% from conventional meat.
- **But that last figure is the logit's assumption, and it is the weak point.** Within a class, a logit takes share from each product in
  proportion to its share. If premium buyers instead treated cultivated meat and the label as close substitutes, most of what cultivated
  meat sells to them (79% of its sales at Central, 91% at +100%) would come out of the label. So the truth for "taken from the label" lies
  between 21% and about four-fifths at Central. That matters for impact more than for share: a tonne sold to a premium buyer replaces a
  higher-welfare bird.
- **The size of the premium class barely matters** (0.23–0.25% at Central across 5–20%), because the fit trades size against liking.

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

- With premium buyers and a welfare label on the shelf Central's share is 0.25% against the model's 0.13%; with a strong no-killing value,
  0.56%. All stay well under 1%: at 4–6 times chicken's price there is no segment big enough or keen enough to change the answer.
- Near parity (the best case) the effect is smaller in relative terms: 3.90% against 2.74% (5.25% with the strong value).
- What cultivated meat displaces matters for its animal impact: between about a fifth and four-fifths of its sales at Central could
  come from welfare-labelled meat rather than factory-farmed meat.
- **Judgement:** that premium buyers raise Central's long-run share above the main model's: about 0.65 (the alternative is that
  novelty and the "unnatural" image keep premium buyers away, which the corrections' unfavourable end gives). That the share at
  Central exceeds 1% by this route: about 0.05.

## Sources

1. Agence Bio / L'ObSoCo, Baromètre de consommation et de perception des produits biologiques en France, 2026. https://lobsoco.com/wp-content/uploads/2026/02/LObSoCo_Agence-Bio_Barometre-2026-VDEF.pdf (FT)
2. Soil Association, Organic Market Report 2026. (FT, via a mirror: https://chilealimentos.com/wp-content/uploads/2026/03/soil-association-certification-organic-market-report-2026.pdf)
3. Gschwandtner et al. 2024, International Journal of the Economics of Business. https://kar.kent.ac.uk/106136/ (FT)
4. Luke, Tonsor & Schroeder 2026, Agricultural and Resource Economics Review 55(1). https://www.cambridge.org/core/product/13E1F30B93A6F9EAF11DF23236BAE171/core-reader (FT, tables did not render)
5. EIT Food Consumer Observatory, cultured meat factsheets, 2025. https://assets.eitfood.eu/files/EIT-Food-Consumer-Observatory_Cultured-Meat_Factsheets_V4_2025-05.pdf (FT)
