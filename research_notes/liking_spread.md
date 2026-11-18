# Shoppers differ in how much they like cultivated meat: the price response re-derived

Date: 2026-11-18. Code: `liking_spread.py`; test: `tests/test_liking_spread.py`. Evidence: `demand_heterogeneity_evidence.md`. Nothing
here changes a default; it sets out the change that should be made and the one decision it needs.

## 1. The problem and the cause

The model's share falls two to four times too fast as the price rises above meat's (`demand_checks.md`). The model gives every
mainstream shopper the same liking for cultivated meat. The one experiment that estimated shoppers one by one (Van Loo, Caputo & Lusk
2020) found liking spread very widely: about half of respondents prefer the lab-grown burger to nothing and half do not. With a wide
spread, the buyers left at a high price are the ones who like it most, so the total falls off slowly, though each shopper is as
price-sensitive as before.

An earlier attempt the same day gave the slow tail to "premium buyers", shoppers who buy organic and free-range meat. The evidence is
against it: in the two studies that split shoppers into groups, the price-insensitive organic buyers are the most hostile to cultivated
meat (`demand_heterogeneity_evidence.md` §2). That work was not merged.

## 2. The fit

Cultivated meat's utility gets a normal spread across shoppers; the mean is set so that 5% buy at equal price, as in the experiment.
The table gives the model's own-price elasticity at four prices of the lab-grown burger against the experiment's.

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
- The experiment itself estimated a spread of 3.75 on its scale, which is about 3.3 to 4.7 of the model's utils. The fit agrees.
- A lower price sensitivity with a smaller spread fits nearly as well (4 with 2: 0.21; 6 with 4: 0.24). The data
  pin a combination, not each number. Keeping 8.5 changes nothing else in the model.

## 3. What it exposes: the share at equal price in the long run

| the long run | share at equal price | share of a meat at 1.25×, 1.5×, 2×, 3×, 4× its price | world share, 1. Today | world share, 3. Plus cells selected to grow faster on the low-waste feed (Central) | world share, 5. Plus engineered cells |
|---|---|---|---|---|---|
| first contact (as measured) | 5% | 3.4%, 2.4%, 1.1%, 0.2%, 0.02% | 0.00% | 0.02% | 0.7% |
| novelty fades by what the model assumes | 13% | 10.1%, 7.7%, 3.7%, 0.8%, 0.1% | 0.01% | 0.07% | 2.6% |
| shoppers indifferent on average (the model's premise) | 49% | 41.7%, 35.8%, 25.4%, 9.4%, 2.3% | 0.07% | 1.0% | 17.3% |
| the model today (every shopper alike) | 49% | 28.8%, 14.6%, 2.9%, 0.09%, 0.00% | 0.00% | 0.04% | 3.1% |
| premium real meats (the curve fitted to sixteen) | | —, 5.7%, 3.7%, 1.5%, 0.6% |  |  |  |

- **With every shopper alike**, removing first-contact wariness (the model's `neophobia_x0`, -2.8 utils) takes cultivated meat from 5%
  to about half the market at equal price. That is how the model gets its 49%.
- **With the spread, the same removal takes it from 5% to 13%.** For half the market the average shopper's liking has to recover by
  8.6 utils, three times the wariness the model assumes. So "about half at equal price" is a premise: that familiarity leaves the
  average shopper indifferent between cultivated and conventional meat.
- **The second row lands on premium real meats without being fitted to them**: 3.7% at twice the price against their 3.7%,
  0.8% at three times against 1.5%.
- **The long-run share at equal price moves the answer more than anything else**: Central from 0.02% to 1.0% of world meat and
  the best case from 0.7% to 17.3%, across the three readings.

## 4. What should be the default

- **The spread should go into the model.** It is the only reading that reproduces the experiment's price response, and it replaces a
  check the model only appeared to pass.
- **The share at equal price should become an explicit setting**, shown with the headline, in place of a premise buried in the
  novelty term. Evidence on where it ends up is thin and points below a half: products that are physically the same but made by a
  process people distrust keep a lasting discount (lab-grown diamonds sell at a fraction of mined ones' price; irradiated meat never
  sold; from memory, unchecked), and in the experiment about half of respondents would not take the burger at any price tested.
- A central value near the second row, with the first and third as its range, is my judgement: about 0.5 that the long-run share at
  equal price is between 8% and 25%, about 0.25 that it is above, about 0.25 below.

## 5. Limits

- One experiment, hypothetical choices, burgers, first contact. The spread in the long run may be narrower than at first contact.
- The fit uses elasticities simulated from the paper's published coefficients, since the paper reports none.
- Price sensitivity also differs across shoppers (4 to 10 times between groups, `demand_heterogeneity_evidence.md` §3). It is not in
  this study, and is not needed to match the experiment.
- Fifteen integration points are used; seven are not enough (shares off by up to 27%), which matters for the page.
