# Shoppers differ in how much they like cultivated meat

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50; cut cost rebuilt (0.8 cells + $2 matrix + $3 assembly), cuts cheaper.

Date: 2026-11-18. **The model's default since that day** (`market_share.share`: `liking_sd`, `equal_price_share`). This module,
`liking_spread.py`, fits the spread and compares readings of the long run; test: `tests/test_liking_spread.py`. Evidence:
`demand_heterogeneity_evidence.md`.

## 1. The problem and the cause

With every shopper alike, the model's share fell two to four times too fast as the price rose above meat's (`demand_checks.md`). The
one experiment that estimated shoppers one by one (Van Loo, Caputo & Lusk 2020) found liking for the lab-grown burger spread very
widely: about half of respondents prefer it to buying nothing and half do not. With a wide spread the buyers left at a high price are
the ones who like it most, so the total falls off slowly, though each shopper is as price-sensitive as before.

An earlier attempt the same day gave the slow tail to "premium buyers" who buy organic and free-range meat. The evidence is against
it: in the two studies that split shoppers into groups, the price-insensitive organic buyers are the most hostile to cultivated meat
(`demand_heterogeneity_evidence.md` §2). It was not merged.

## 2. The fit

Cultivated meat's utility gets a normal spread across shoppers; the mean is set so that 5% buy at equal price at first contact, as in
the experiment. The table gives the model's own-price elasticity at four prices of the lab-grown burger against the experiment's.

| each shopper's price sensitivity (times meat's) | spread of liking, utils | elasticity at 0.6×, 1×, 1.4×, 1.8× beef's price | miss |
|---|---|---|---|
| **measured (Van Loo, Caputo & Lusk 2020, simulated from its fitted model)** | | -0.87, -1.50, -2.00, -2.40 | |
| 4 | 0 | -0.89, -1.55, -2.22, -2.89 | 0.27 |
| 4 | 2 | -0.66, -1.20, -1.80, -2.45 | 0.21 |
| 4 | 4 | -0.44, -0.80, -1.15, -1.48 | 0.75 |
| 4 | 5 | -0.39, -0.72, -1.01, -1.21 | 0.90 |
| 4 | 6 | -0.36, -0.69, -0.95, -1.07 | 0.97 |
| 6 | 0 | -1.28, -2.32, -3.36, -4.37 | 1.28 |
| 6 | 2 | -0.94, -1.79, -2.78, -3.86 | 0.84 |
| 6 | 4 | -0.62, -1.20, -1.72, -2.30 | 0.24 |
| 6 | 5 | -0.53, -1.09, -1.47, -1.71 | 0.51 |
| 6 | 6 | -0.49, -1.03, -1.35, -1.36 | 0.69 |
| 8.5 | 0 | -1.71, -3.29, -4.79, -6.22 | 2.56 |
| 8.5 | 2 | -1.25, -2.54, -4.08, -5.73 | 2.04 |
| 8.5 | 4 | -0.81, -1.71, -2.44, -3.66 | 0.68 |
| **8.5** | **5** | -0.67, -1.54, -1.98, -2.62 | **0.15** |
| 8.5 | 6 | -0.59, -1.46, -1.73, -1.80 | 0.36 |

- **A spread of 5 utils at the model's own price sensitivity (8.5) fits best** (miss 0.15). With no spread the model misses by
  2.56: its elasticity at equal price is -3.29 against the measured -1.5.
- The experiment estimated a spread of 3.75 on its scale, about 3.3 to 4.7 of the model's utils. The fit agrees.
- A lower price sensitivity with a smaller spread fits nearly as well (4 with 2: 0.21; 6 with 4: 0.24). The data
  pin a combination; keeping 8.5 changes nothing else in the model.

## 3. The share at equal price in the long run

| the long run | share at equal price | share of a meat at 1.25×, 1.5×, 2×, 3×, 4× its price | world share, 1. Today | world share, 3. Plus cells selected to grow faster on the low-waste feed (Central) | world share, 5. Plus engineered cells |
|---|---|---|---|---|---|
| first contact (as measured) | 5% | 3.4%, 2.4%, 1.1%, 0.2%, 0.02% | 0.00% | 0.1% | 1.4% |
| novelty fades by what the model assumes | 13% | 10.1%, 7.7%, 3.7%, 0.8%, 0.1% | 0.02% | 0.4% | 4.4% |
| shoppers indifferent on average (the premise before 2026-11-18) | 49% | 41.7%, 35.8%, 25.4%, 9.4%, 2.3% | 0.2% | 4.3% | 24.1% |
| the model before 2026-11-18 (every shopper alike) | 49% | 28.8%, 14.6%, 2.9%, 0.09%, 0.00% | 0.01% | 0.2% | 8.5% |
| premium real meats (the curve fitted to sixteen) | | —, 5.7%, 3.7%, 1.5%, 0.6% |  |  |  |

- **With every shopper alike**, removing first-contact wariness (the model's `neophobia_x0`, -2.8 utils) took cultivated meat from 5% to
  about half the market at equal price.
- **With the spread, the same removal takes it from 5% to 13%.** Half the market needs the average shopper's liking to recover by
  8.6 utils, three times the wariness the model assumes: shoppers indifferent between the two meats on average.
- **The middle reading lands on premium real meats without being fitted to them**: 3.7% at twice the price against their 3.7%,
  0.8% at three times against 1.5%.
- **It moves the answer more than any cost**: Central from 0.1% to 4.3% of world meat and the best case from
  1.4% to 24.1% across the three readings.

## 4. The default chosen

- `liking_sd` = 5 utils (fitted; range 3.5–6) and `equal_price_share` = 13% (judgement; range 5–49%, drawn in the bands as a
  triangle with that mode, median about 19%).
- Why 13%: a third of first-contact aversion fading, by two routes. The model's own novelty term is 2.8 of the 8.6 utils between first
  contact and indifference. In the survey corrections (`premium_curve.CORRECTIONS`), first contact is 45% of meat's price dearer
  (novelty 30, "unnatural" 20, less 5 for no killing) and the long-run central case is 30% (novelty halved, "unnatural" kept): 15 of
  45 points close.
- A reading of foods made by distrusted processes (`demand_heterogeneity_evidence.md` §6) puts the median near 18%: below 8% with
  0.17, 8–25% with 0.45, 25–40% with 0.24, above 40% with 0.14.
- Against premium meats' fall with price, combinations of a low share at equal price with a wide spread fit better than half the market
  with a narrower spread (rms log miss 0.63 at 13% and spread 5; 0.65 at 25% and 4; 1.11 at 49% and 3). Modest evidence: labels are
  not cultivated meat.
- The share at equal price is now the long-run dial; the no-slaughter, long-run novelty and health dials are parts of it, are no longer
  drawn in the bands, and stay on the page as what-ifs on top.

## 5. Limits

- One experiment, hypothetical choices, burgers, first contact, and the name "lab-grown". The spread in the long run may be narrower.
- The fit uses elasticities simulated from the paper's published coefficients, since the paper reports none.
- Price sensitivity also differs across shoppers (4 to 10 times between groups, `demand_heterogeneity_evidence.md` §3); not in the
  model, and not needed to match the experiment. Plant-based meat's own elasticity is still too strong (`demand_checks.md`).
- Fifteen integration points are used; seven are not enough (shares off by up to 27%).
