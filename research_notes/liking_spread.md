# Shoppers differ in how much they like cultivated meat

> Names (2026-11-19): the low-lactate example was earlier called Central; the all-favourable example was earlier called the best case. Cells are described by their traits, never as a named kind of cell.

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50; cut cost rebuilt (0.8 cells + $2 matrix + $2 assembly beyond mince), cuts cheaper.

> Repinned 2026-11-19 (audit batch): cells dearer (ammonia tolerance 4 mM), seafood re-priced by consumption, the tier rule replaced by a blend penalty, the equal-price share drawn around its 13% setting; see audit_2026-11-19.md.

> Repinned 2026-11-19 (second round): shoppers' liking is a Student's t spread (standard deviation 3.9 utils, 4 degrees of freedom) on a 67-point grid, not a normal spread of 5 on fifteen points; see liking_spread.md.

> Repinned 2026-11-20 (engine batch): the scenarios' cells tolerate 35 mmol/L of lactate, bubble deaths and a harvest loss are charged, a washed tank takes twice the fed-batch crew, the membrane lasts 2,415 L/m2, and growth factors, utilities and the crew follow the Humbird back-test, so cells are dearer (the low-lactate example $32.80 to $49.96 a kilo, the all-favourable example $11.67 to $18.71, Published cells in fed-batch $209 to $323) and every share here fell; the demand model did not change; see full_review_2026-11-19.md and humbird_backtest.md. The spread itself (3.9 utils, tail 4) was not refitted. Its joint misfit moved, because the farmed-salmon part of the fit is computed at the low-lactate example's cost of cells (section 2).

> Repinned 2026-11-21 (engine batch): the cost of cells moved (the all-favourable example $7.62 -> $6.97, its tank design now holds the culture thinner so its oxygen column passes its checks; the low-lactate example $49.50 -> $48.68; published cells $322.55 -> $316.11), because the design search runs a culture thinner when its loop fails, the building's power follows its floor and its class, and part of the crew is counted per tank. Nothing in the demand model changed; the shares that follow from the costs are recomputed.

> Repinned 2026-11-21 (fourth batch): plant-based meat's committed buyers (`demand_checks.md` section 5) raise the ordinary
> shoppers' real-meat weight, so cuts that are part plant protein are liked less; the spread was checked and not refitted
> (misfit 4.20 at 3.9 and 4). The tables are regenerated, and the figures in the prose of sections 2, 4 and 6 recomputed
> (2026-11-22); the all-favourable example with its own demand is 23.4% of world meat (24.7% before), its cells with the ordinary
> demand 5.6% (6.1%).

> Repinned 2026-11-20 (model batch): the all-favourable example keeps haemodialyser fibres for its cells, so its cells cost $7.62 a kilo, not $18.71 (the low-lactate example $49.50); the plant-based share target fell from 1.2% to 0.4%; incomes became nominal dollars (income_ref $86,170, phi 0.32); and the share of the world's market closed to cultivated meat is weighted by meat eaten (1.14%, was 0.42%). The spread was not refitted; every table here is regenerated, and the 2026-11-18 model is reproduced to the last digit only with those three demand inputs at their old values (tested).

> Refitted 2026-11-22 (fifth batch): the model now has price-insensitive shoppers (8% of every segment, responding 0.11 times as
> strongly to every price, liking cultivated meat as much as other shoppers in utils; `demand_checks.md` section 7). The spread
> was refitted with them in: a standard deviation of 3.55 utils (was 3.9) and a tail of 7 (was 4), joint misfit 0.87 (was 4.20).
> The other shapes were refitted to their best spread with them in; every table here is regenerated.

Date: 2026-11-18; the shape of the spread re-fitted on 2026-11-19 and on 2026-11-22 (section 2). **The model's default** (`market_share.share`:
`liking_sd`, `liking_tail`, `equal_price_share`; `inputs.LIKING_FAMILY`). This module, `liking_spread.py`, fits the spread and
compares readings of the long run; test: `tests/test_liking_spread.py`. Evidence: `demand_heterogeneity_evidence.md`.

**In short.** Shoppers differ widely in how much they like cultivated meat, so the buyers left at a high price are the keenest, and
the share falls off slowly. Since 2026-11-19 the spread is a Student's t, in place of a normal spread of 5 utils. Two things forced
the change. The normal fit of 2026-11-18 rested on a numerical error: its fifteen integration points were too few. And a normal
tail falls too fast far above meat's price. Since 2026-11-22 the model also has price-insensitive shoppers, who hold buyers far
above meat's price on their own, and the t was refitted with them: a standard deviation of 3.55 utils and 7 degrees of freedom
(3.9 and 4 before). It fits the choice experiment, the premium real meats and farmed salmon together a little better than the
logistic and far better than the normal or a mixture. It leaves four worries (section 6): the all-favourable example's share is
about a fifth below the normal spread's, first contact comes out at 3.8% of all choices against the measured 4%, the response to a
falling price is still above farmed salmon's for three of four products, and above five times meat's price the tail is an
extrapolation, now carried by the price-insensitive shoppers.

## 1. The problem and the cause

With every shopper alike, the model's share fell two to four times too fast as the price rose above meat's (`demand_checks.md`). The
one experiment that estimated shoppers one by one (Van Loo, Caputo & Lusk 2020) found liking for the lab-grown burger spread very
widely: about half of respondents prefer it to buying nothing and half do not. With a wide spread the buyers left at a high price are
the ones who like it most, so the total falls off slowly, though each shopper is as price-sensitive as before.

An earlier attempt the same day gave the slow tail to "premium buyers" who buy organic and free-range meat. The evidence is against
it: in the two studies that split shoppers into groups, the price-insensitive organic buyers are the most hostile to cultivated meat
(`demand_heterogeneity_evidence.md` §2). It was not merged. Since 2026-11-22 the model has price-insensitive shoppers of its own (8% of
shoppers), but not as the slow tail of liking: their liking for cultivated meat is the other shoppers' in utils, which, at their
small price response, makes them the most hostile in money, as those two studies found (`demand_checks.md` section 7).

## 2. The shape of the spread (2026-11-19)

**Why the fit was redone.** Two faults in the normal spread of 2026-11-18.

- **Its fit rested on a numerical error.** The spread was integrated over fifteen points. For a spread of 5 utils that is too coarse:
  shares at 1 to 5 times meat's price were off by up to 4.9%, and the slope more. On fifteen points the normal spread gave a
  first-contact elasticity of -1.53 and missed the experiment by 0.15. Integrated properly it gives -1.34 and misses by 0.29.
  No normal spread, properly integrated, meets both requirements below.
- **Its tail falls too fast.** At four times the ordinary price premium real meats hold 0.6% of their category; the normal spread
  gave 0.1%. This is audit finding D3 (`audit_2026-11-19.md`).

**The four shapes.** Each gives every shopper a liking for cultivated meat drawn from a spread with a set standard deviation.

- *Normal*: the bell curve; very few shoppers far from the average.
- *Logistic*: a bell with somewhat heavier tails; no extra parameter.
- *Student's t*: a bell with heavier tails still, set by one extra parameter (its degrees of freedom, `liking_tail`). The smaller
  it is, the more shoppers who like or dislike cultivated meat far more than the typical spread. At 30 or more it is a normal.
- *A mixture of two normals*: most shoppers in a narrow bell and a small minority in a much wider one. Two extra parameters: the
  minority's size and how much wider its spread is.

**What they are fitted to.** One joint misfit, the sum of three parts with equal weights (`liking_spread.objective`): (i) the choice
experiment's own-price elasticity at four prices; (ii) the share premium real meats hold at 2, 3 and 4 times the ordinary price
(3.7%, 1.5%, 0.6%, from the curve fitted to sixteen products); (iii) farmed salmon's response to its falling price (1–1.5% more
volume per 1% off the price), for the premium products still dearer than their meat. Two requirements on top: the first-contact
elasticity at equal price within -1.5 ± 0.15, and a miss on the experiment's four prices of at most 0.30.

| shape of the spread | parameters | choice experiment: miss | first contact, equal price: share, elasticity | share at 1.25×, 1.5×, 2×, 3×, 4× | salmon response | at half price, if free | joint misfit (experiment, premium, salmon) | meets both requirements | world share: 1. Published cells, 4. Plus perfusion (the low-lactate example), 7. Plus everything else at its favourable end (the all-favourable example), best with its own demand |
|---|---|---|---|---|---|---|---|---|---|
| **measured** | | | 5%, -1.5 | —, 5.7%, 3.7%, 1.5%, 0.6% (premium real meats) | 1–1.5 | | | | |
| normal, as it was (15 integration points) | spread 5 | 0.20 | 5.2%, -1.43 | 10.4%, 8.2%, 4.4%, 1.6%, 0.9% | 1.4–4.0 | 21%, 31% | 2.9 (1.8, 0.4, 0.7) | yes | under 0.001%, 0.4%, 6.3%, 31.1% |
| normal, integrated properly | spread 5 | 0.17 | 5.0%, -1.25 | 10.1%, 7.7%, 4.4%, 1.5%, 0.8% | 1.4–4.0 | 21%, 30% | 2.2 (1.3, 0.3, 0.7) | no | under 0.001%, 0.3%, 6.2%, 31.6% |
| logistic | spread 3.65 | 0.04 | 4.0%, -1.47 | 9.4%, 6.8%, 3.5%, 1.3%, 0.8% | 1.5–4.1 | 24%, 39% | 0.9 (0.1, 0.2, 0.7) | yes | under 0.001%, 0.3%, 5.6%, 25.6% |
| Student's t (the model) | spread 3.55, tail 7 | 0.02 | 3.8%, -1.51 | 9.3%, 6.6%, 3.4%, 1.3%, 0.8% | 1.5–4.0 | 24%, 40% | 0.9 (0.0, 0.2, 0.6) | yes | 0.001%, 0.3%, 5.5%, 25.1% |
| mixture of two normals | spread 3.5; 5% of shoppers at 3 times the others' spread | 0.17 | 3.5%, -1.59 | 9.1%, 6.3%, 3.2%, 1.3%, 0.9% | 1.9–3.5 | 25%, 41% | 2.2 (1.2, 0.4, 0.5) | yes | 0.004%, 0.2%, 5.3%, 24.5% |
| mixture with a small wide block (2% of shoppers at 6 times the others' spread) | spread 4.2; 2% of shoppers at 6 times the others' spread | 0.18 | 3.5%, -1.60 | 9.2%, 6.4%, 3.2%, 1.4%, 1.1% | 1.2–3.2 | 24%, 40% | 2.5 (1.4, 0.8, 0.3) | yes | 0.02%, 0.4%, 5.3%, 25.3% |

The world shares use each scenario's cost of cells. "Best with its own demand" is the all-favourable example with its own 55% at equal price;
the column before it is the all-favourable example's cells with the model's ordinary 13%.

- **With the price-insensitive shoppers in, the t fits best, the logistic nearly as well**: a joint misfit of 0.87 against 0.90
  (logistic), 2.2 (a mixture of two normals), 2.5 (a mixture with a small wide block), 2.9 (the normal as it was) and 2.2 (the
  normal integrated properly, which fails the first-contact requirement). It matches the experiment almost exactly (miss 0.02). It
  holds 1.3% and 0.8% of a meat's buyers at three and four times the price, against the premium meats' 1.5% and 0.6%. The response
  to a falling price is 1.5–4.0.
- **Before the price-insensitive shoppers** (2026-11-19 to 2026-11-21) the t at 3.9 and 4 had a misfit of 4.2, against 17.1 for
  the normal as it was, 21.3 for the normal integrated properly and 10.0 for the logistic; the mixtures fitted better (2.7, and
  1.4 at the corner of their grid, 2% of shoppers at six times the others' spread) and were not chosen, because their best fit was
  a small block of shoppers who buy at almost any price, which nothing measured shows. The price-insensitive shoppers are such a
  block, but one the evidence does show (`demand_heterogeneity_evidence.md` section 3) and whose liking is read from two studies
  (`demand_checks.md` section 7). With them in, the mixtures' extra block is not needed and they fit worse than the t.
- The salmon part of the misfit is computed between the low-lactate example's own cost of cells and its cost once a food-grade
  membrane exists ($48.68 and $23.52 since 2026-11-22; $24.05 before).

**What the two numbers mean.**

- `liking_sd` = 3.55 utils: how far apart shoppers are. A shopper one standard deviation keener than another will pay about twice
  as much (2.0 times) for the same chance of buying. For comparison, the wariness at first contact is 2.8 utils.
- `liking_tail` = 7: how many shoppers sit far from the average. Against a normal spread of the same standard deviation, more
  shoppers are close to the average (73% within one standard deviation, against 68%) and more are very far from it: 1 in 210 is
  more than three standard deviations keener than average, against 1 in 740; 1 in 940 more than four, against 1 in 32,000.
  (At a tail of 4: 77%, 1 in 150 and 1 in 420.) Far above meat's price the buyers left are now mostly price-insensitive shoppers
  (`demand_checks.md` section 7), not the far tail of this spread.

**How well the data pin them.** Loosely (`liking_spread.profile`; `python liking_spread.py --families` prints it, the test does
not re-run it):

| tail (degrees of freedom) | best spread, utils | joint misfit |
|---|---|---|
| 3 | 3 (the lowest spread searched) | 2.46 |
| 4 | 3.1 | 1.39 |
| 5 | 3.3 | 1.03 |
| 6 | 3.45 | 0.90 |
| **7** | **3.55** | **0.87** |
| 8 | 3.65 | 0.88 |
| 10 | 3.85 | 0.94 |
| 12 | 3.95 | 1.00 |
| 30 (nearly normal) | 4.35 | 1.33 |

(With the price-insensitive shoppers in, at the model's 8% and 0.11; spreads from 3.0 to 4.6 in steps of 0.05.)

- The misfit is least at a tail of 7 with a spread of 3.55 (0.87): the model. Within 20% of that: a spread of 3.25 to 4.0 and a
  tail of 5 to 12. At a tail of 7, spreads from 3.45 to 3.65 are within 20%.
- **The tail moved from 4 to 7 with the price-insensitive shoppers.** Before them, the misfit was least at a tail of 3 with a spread
  of 3.7 (3.69), and 4 was chosen over 3 on three grounds the misfit does not count: first contact nearer the measured, fewer
  buyers at ten or more times meat's price, and a higher all-favourable example. All three still favour the lighter tail, and the
  misfit now does too. First contact is 3.8% of all choices at a tail of 7 (3.6% at 5, 4.1% at 10; measured 4%).
- The experiment alone puts the spread near the model's (miss 0.02 at 3.55, section 3). Its own estimate was 3.6–4.6 on its scale,
  about 3.3–4.7 of the model's utils.

**The integration rule.** The model now integrates every shape but the normal over 67 points on a stretched grid
(`market_share.grid_quadrature`). Against a 20,001-point reference:

| shape | rule | points | largest error of the share at 1 to 5 times the price | error at 8 times |
|---|---|---|---|---|
| normal, spread 5 | Gauss-Hermite (the model of 2026-11-18) | 15 | 3.36% | 1.0% |
| normal, spread 5 | Gauss-Hermite | 61 | 0.02% | 0.0% |
| Student's t (tail 7) | Gauss-Legendre in probability | 60 | 1.42% | 0.4% |
| Student's t (tail 7) | Gauss-Legendre in probability | 120 | 0.08% | 0.4% |
| Student's t (tail 7) | stretched grid (the model's rule) | 67 | 0.00% | 0.0% |
| mixture | Gauss-Hermite per component | 62 | 1.44% | 1.0% |
| mixture | stretched grid | 67 | 0.00% | 0.0% |

(Since 2026-11-22, with the price-insensitive shoppers in and the refitted spreads; `liking_spread.markdown_quadrature`.) The model's
rule is within 0.01% at 1 to 5 times the price and at eight times. The errors are smaller than with a tail of 4 (0.03% and 0.3%;
Gauss-Legendre with 60 points 11.1% and 86%), and the price-insensitive shoppers, who buy far above meat's price on the middle of
the spread rather than its tail, make the share less sensitive to the rule. With `LIKING_FAMILY = "normal"`, `liking_sd = 5.0`, no
price-insensitive shoppers, no committed buyers of plant-based meat, and the plant-based share target, the reference income and its
exponent at their values of 2026-11-18 (1.2%, $85,810, 0.5), the model of 2026-11-18 is reproduced to the last digit (tested).

## 3. The fit to the choice experiment alone

Cultivated meat's utility gets the t spread (tail 7) across shoppers, with the model's price-insensitive shoppers; the mean is set so that 5% buy at equal price at first
contact, as in the experiment. The table gives the model's own-price elasticity at four prices of the lab-grown burger against
the experiment's, for several spreads and for three values of each shopper's price sensitivity.

| each shopper's price sensitivity (times meat's) | spread of liking, utils | elasticity at 0.6×, 1×, 1.4×, 1.8× beef's price | miss |
|---|---|---|---|
| **measured (Van Loo, Caputo & Lusk 2020, simulated from its fitted model)** | | -0.87, -1.50, -2.00, -2.40 | |
| 4 | 0 | -0.89, -1.56, -2.24, -2.93 | 0.29 |
| 4 | 2 | -0.61, -1.04, -1.46, -1.83 | 0.47 |
| 4 | 3.6 | -0.41, -0.69, -0.96, -1.21 | 0.92 |
| 4 | 3.55 | -0.41, -0.70, -0.97, -1.23 | 0.91 |
| 4 | 5 | -0.31, -0.52, -0.72, -0.91 | 1.13 |
| 4 | 6 | -0.26, -0.43, -0.60, -0.77 | 1.24 |
| 6 | 0 | -1.29, -2.34, -3.39, -4.42 | 1.31 |
| 6 | 2 | -0.89, -1.57, -2.18, -2.58 | 0.13 |
| 6 | 3.6 | -0.61, -1.03, -1.43, -1.77 | 0.50 |
| 6 | 3.55 | -0.62, -1.05, -1.45, -1.79 | 0.49 |
| 6 | 5 | -0.46, -0.77, -1.07, -1.34 | 0.82 |
| 6 | 6 | -0.39, -0.65, -0.90, -1.14 | 0.97 |
| 8.5 | 0 | -1.72, -3.32, -4.84, -6.29 | 2.61 |
| 8.5 | 2 | -1.21, -2.22, -3.01, -3.20 | 0.76 |
| 8.5 | 3.6 | -0.85, -1.46, -2.00, -2.36 | 0.03 |
| **8.5** | **3.55** | -0.86, -1.48, -2.02, -2.38 | **0.02** |
| 8.5 | 5 | -0.65, -1.10, -1.50, -1.83 | 0.44 |
| 8.5 | 6 | -0.55, -0.92, -1.27, -1.56 | 0.65 |

- **At the model's own price sensitivity (8.5) the model's spread, 3.55, fits the experiment almost exactly** (miss 0.02; 3.6:
  0.03). Since 2026-11-22 the joint fit with premium meats and salmon and the fit to the experiment alone agree (before, 3.9 against
  3.6). With no spread the model misses by 2.61: its elasticity at equal price is -3.32 against the measured -1.5.
- A lower price sensitivity fits only with little or no spread (4 with none: 0.29; 6 with 2: 0.13). Keeping 8.5 changes nothing
  else in the model.
- The table of 2026-11-18, for a normal spread, had 5 utils as the best fit with a miss of 0.15. That was the fifteen-point error
  (section 2).

## 4. The share at equal price in the long run

| the long run | share at equal price | share of a meat at 1.25×, 1.5×, 2×, 3×, 4× its price | world share, 1. Published cells | world share, 4. Plus perfusion (the low-lactate example) | world share, 7. Plus everything else at its favourable end (the all-favourable example) |
|---|---|---|---|---|---|
| first contact (as measured) | 5% | 3.5%, 2.4%, 1.2%, 0.5%, 0.3% | under 0.001% | 0.09% | 2.2% |
| novelty fades by what the model assumes | 16% | 11.9%, 8.6%, 4.5%, 1.6%, 1.0% | 0.001% | 0.3% | 6.9% |
| shoppers indifferent on average (the premise before 2026-11-18) | 52% | 42.9%, 34.6%, 20.9%, 7.4%, 3.9% | 0.005% | 1.7% | 23.2% |
| the model before 2026-11-18 (every shopper alike) | 52% | 31.3%, 16.1%, 3.2%, 0.1%, 0.003% | under 0.001% | under 0.001% | 12.2% |
| premium real meats (the curve fitted to sixteen) | | —, 5.7%, 3.7%, 1.5%, 0.6% |  |  |  |

The world shares use each scenario's cost of cells with the reading's own demand. The all-favourable example's column is its cells at these
readings, not the all-favourable example's own 55% at equal price, which gives 25.1%.

- **With every shopper alike**, removing first-contact wariness (the model's `neophobia_x0`, -2.8 utils) took cultivated meat from 5% to
  about half the market at equal price.
- **With the spread, the same removal takes it from 5% to 16%** (15% before the price-insensitive shoppers of 2026-11-22). Half the
  market needs the average shopper's liking to recover by 6.6 utils, more than twice the wariness the model assumes: shoppers
  indifferent between the two meats on average.
- **The model's setting stays at 13%, a little below this reading.** With the normal spread the same removal gave 13%, and that is
  where the setting came from. With the t it gives 16%. The setting was kept: it is a judgement with two other supports (section
  5). Read backwards, 13% in the long run means 3.8% of all choices at first contact (4.3% of meat buyers), against the measured
  4% (5%). The middle row's world shares are therefore above the model's: 0.34% against 0.26% for the low-lactate example, 6.9%
  against 5.5% for the all-favourable example's cells (before 2026-11-22: 0.049% against 0.045%, 6.4% against 5.6%).
- **The middle reading lands near premium real meats**: 4.5% at twice the price against their 3.7%, 1.6% at three times against
  1.5%, 1.0% at four times against 0.6%. Since 2026-11-19 the shape is fitted to them, so this is no longer an independent check.
- **Across the three readings the low-lactate example runs from 0.09% to 1.7% of world meat**, about nineteen-fold, and the
  all-favourable example's cells from 2.2% to 23.2%, about elevenfold (before 2026-11-22: 0.03% to 0.1% and 2.4% to 21.6%). The
  reading matters more for the low-lactate example than it did: at $48.68 a kilo of cells its buyers are now mostly the
  price-insensitive shoppers, whose liking moves with the mean, not the far tail of the spread. Its cost matters less: across the
  8-in-10 range of its cost of cells ($39 to $76 a kilo) the share at the 13% setting runs from 0.36% to 0.12%, about threefold
  (elevenfold before).

## 5. The default chosen

- `LIKING_FAMILY` = Student's t, `liking_sd` = 3.55 utils (fitted; range 3.3–3.9), `liking_tail` = 7 (fitted loosely; range
  5–12), with the price-insensitive shoppers (`price_insensitive_share` 8%, `price_insensitive_response` 0.11,
  `price_insensitive_liking` 0 utils; `demand_checks.md` section 7). None of these is drawn in the bands.
- `equal_price_share` = 13% (judgement). Since 2026-11-19 it is drawn in the bands from a lognormal with median 13% (5th–95th
  percentile about 3–52%). Before, it was drawn from a triangle from 5% to 49% with its mode at 13%, whose median was 21%, well
  above the setting (audit finding D1).
- Why 13%: a little over a third of first-contact aversion fading, by two routes. On the model's scale, 13% is 2.2 of the 6.6
  utils between first contact and indifference; the model's own novelty term is 2.8 utils, which would give 16%. In the survey
  corrections (`premium_curve.CORRECTIONS`), first contact is 45% of meat's price dearer (novelty 30, "unnatural" 20, less 5 for
  no killing) and the long-run middle case is 30% (novelty halved, "unnatural" kept): 15 of 45 points close.
- A reading of foods made by distrusted processes (`demand_heterogeneity_evidence.md` §6) puts the median near 18%: below 8% with
  0.17, 8–25% with 0.45, 25–40% with 0.24, above 40% with 0.14. The literature review (`what_drives_choice.md`) puts the 10th, 50th
  and 90th percentiles at 2%, 10% and 35%.
- The share at equal price is the long-run dial; the no-slaughter, long-run novelty and health dials are parts of it, are not
  drawn in the bands, and stay on the page as what-ifs on top.
- The all-favourable example sets its own share at equal price, 55% (35–70%; `best_equal_price_share`).

## 6. Worries and limits

- **The all-favourable example is about a fifth below the normal spread: 31.1% against 25.1% of world meat with its own demand**
  (29.8% against 23.4% before the price-insensitive shoppers of 2026-11-22). The fitted t is narrower in the middle than a normal of
  5: with 55% buying at equal price most shoppers sit near the tipping point, so a price above meat's loses them faster. No data
  measure the middle of the spread beyond the one experiment. The logistic gives 25.6% and the mixtures 24.5–25.3%, so the shapes
  that fit span 24.5–25.6%. With the model's ordinary 13% the all-favourable example's cells barely move (6.3% with the normal,
  5.5% with the t).
- **First contact comes out at 3.8% of all choices (4.3% of meat buyers), against the measured 4% (5%)**, with an elasticity of
  -1.51 against -1.5. Every shape that fits has 3.5–4.0%; the normal of 5 gives 5.0–5.2% but fails elsewhere.
- **Farmed salmon's response still fails, by less**: 1.5–4.0% more share per 1% off the price, against 1–1.5%. The dearest product
  (organic chicken) is now at the top of the range; sushi-grade seafood, nearest its meat's price, is still at 4.0
  (`demand_checks.md` section 7).
- **Above five times meat's price the tail is an extrapolation, now carried by the price-insensitive shoppers.** The dearest
  premium meat in the data sits at 3.6 times its ordinary product, and the fit uses the curve at 2, 3 and 4 times. The model gives
  0.58% of a meat's buyers at five times the price, 0.33% at eight and 0.23% at ten (0.15%, 0.02% and 0.01% before 2026-11-22);
  nothing measures these. They matter where cells are dear: 72% of the low-lactate example's sales at its own cost come from
  products at more than five times their meat's price, and 79% from above four times (three-tenths and two-fifths before), and 97%
  of them go to the price-insensitive shoppers. Published cells sell 0.001% of world meat with the t.
- **The tail is loosely pinned** (5 to 12); since 2026-11-22 the least misfit and the three grounds it does not count agree on 7.
- One experiment, hypothetical choices, burgers, first contact, and the name "lab-grown". The spread in the long run may be narrower.
- The fit uses elasticities simulated from the paper's published coefficients, since the paper reports none.
- Price sensitivity also differs across shoppers (4 to 10 times between groups, `demand_heterogeneity_evidence.md` §3). Since
  2026-11-21 (fourth batch) plant-based meat's committed buyers respond less to its price (`demand_checks.md` section 5); since
  2026-11-22 (fifth batch) 8% of shoppers respond 0.11 times as strongly to every price (section 7 there). Their liking for
  cultivated meat is read from two stated-choice studies as no different from other shoppers' in utils; at -2 or +2 utils the
  low-lactate example would be 0.11% or 0.58% of world meat, against 0.26%. That is now the demand side's largest unknown for the
  low-lactate example, after the share at equal price.
