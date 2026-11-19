# Shoppers differ in how much they like cultivated meat

> Names (2026-11-19): "Selected cells" was called Central; "Engineered cells, all favourable" was called the best case.

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50; cut cost rebuilt (0.8 cells + $2 matrix + $2 assembly beyond mince), cuts cheaper.

> Repinned 2026-11-19 (audit batch): cells dearer (ammonia tolerance 4 mM), seafood re-priced by consumption, the tier rule replaced by a blend penalty, the equal-price share drawn around its 13% setting; see audit_2026-11-19.md.

> Repinned 2026-11-19 (second round): shoppers' liking is a Student's t spread (standard deviation 3.9 utils, 4 degrees of freedom) on a 67-point grid, not a normal spread of 5 on fifteen points; see liking_spread.md.

Date: 2026-11-18; the shape of the spread re-fitted on 2026-11-19 (section 2). **The model's default** (`market_share.share`:
`liking_sd`, `liking_tail`, `equal_price_share`; `inputs.LIKING_FAMILY`). This module, `liking_spread.py`, fits the spread and
compares readings of the long run; test: `tests/test_liking_spread.py`. Evidence: `demand_heterogeneity_evidence.md`.

**In short.** Shoppers differ widely in how much they like cultivated meat, so the buyers left at a high price are the keenest, and
the share falls off slowly. Since 2026-11-19 the spread is a Student's t with a standard deviation of 3.9 utils and 4 degrees of
freedom, in place of a normal spread of 5 utils. Two things forced the change. The normal fit of 2026-11-18 rested on a numerical
error: its fifteen integration points were too few. And a normal tail falls too fast far above meat's price. The t fits the choice
experiment, the premium real meats and farmed salmon together better than the normal or the logistic. It leaves four worries
(section 6): the best case's share falls by a third, first contact comes out at 4.3% against the measured 5%, the response to a
falling price is still more than twice farmed salmon's, and above five times meat's price the tail is an extrapolation.

## 1. The problem and the cause

With every shopper alike, the model's share fell two to four times too fast as the price rose above meat's (`demand_checks.md`). The
one experiment that estimated shoppers one by one (Van Loo, Caputo & Lusk 2020) found liking for the lab-grown burger spread very
widely: about half of respondents prefer it to buying nothing and half do not. With a wide spread the buyers left at a high price are
the ones who like it most, so the total falls off slowly, though each shopper is as price-sensitive as before.

An earlier attempt the same day gave the slow tail to "premium buyers" who buy organic and free-range meat. The evidence is against
it: in the two studies that split shoppers into groups, the price-insensitive organic buyers are the most hostile to cultivated meat
(`demand_heterogeneity_evidence.md` §2). It was not merged.

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

| shape of the spread | parameters | choice experiment: miss | first contact, equal price: share, elasticity | share at 1.25×, 1.5×, 2×, 3×, 4× | salmon response | at half price, if free | joint misfit (experiment, premium, salmon) | meets both requirements | world share: 1. Published cells, 4. Plus perfusion (Selected cells), 7. Plus everything else at its favourable end (Engineered cells, all favourable), best with its own demand |
|---|---|---|---|---|---|---|---|---|---|
| **measured** | | | 5%, -1.5 | —, 5.7%, 3.7%, 1.5%, 0.6% (premium real meats) | 1–1.5 | | | | |
| normal, as it was (15 integration points) | spread 5 | 0.15 | 5.1%, -1.53 | 10.3%, 7.8%, 3.8%, 0.8%, 0.1% | 5.2–7.4 | 22%, 33% | 13.7 (1.0, 8.6, 4.2) | yes | under 0.001%, 0.1%, 3.3%, 21.6% |
| normal, integrated properly | spread 5 | 0.29 | 4.9%, -1.34 | 9.9%, 7.3%, 3.8%, 0.8%, 0.1% | 5.1–7.3 | 21%, 32% | 17.7 (3.7, 9.7, 4.2) | no | under 0.001%, 0.1%, 3.1%, 22.1% |
| logistic | spread 4.25 | 0.13 | 4.6%, -1.36 | 9.6%, 6.9%, 3.5%, 0.9%, 0.2% | 4.4–5.4 | 23%, 36% | 8.3 (0.7, 4.6, 2.9) | yes | under 0.001%, 0.1%, 3.1%, 17.8% |
| Student's t (the model) | spread 3.9, tail 4 | 0.13 | 4.3%, -1.37 | 9.2%, 6.5%, 3.3%, 1.0%, 0.3% | 3.6–3.7 | 25%, 42% | 4.0 (0.7, 1.6, 1.7) | yes | under 0.001%, 0.2%, 3.2%, 15.1% |
| mixture of two normals | spread 4.4; 5% of shoppers at 3 times the others' spread | 0.10 | 4.3%, -1.43 | 9.4%, 6.7%, 3.3%, 1.0%, 0.5% | 2.8–3.5 | 23%, 37% | 2.5 (0.5, 0.9, 1.1) | yes | under 0.001%, 0.3%, 3.2%, 17.5% |
| mixture, best on the grid (its corner) | spread 5.2; 2% of shoppers at 6 times the others' spread | 0.06 | 4.3%, -1.45 | 9.5%, 6.7%, 3.3%, 0.9%, 0.5% | 2.0–3.4 | 23%, 36% | 1.7 (0.2, 0.8, 0.8) | yes | under 0.001%, 0.5%, 3.2%, 18.3% |

The world shares use each scenario's cost of cells. "Best with its own demand" is the best case with its own 55% at equal price;
the column before it is the best case's cells with the model's ordinary 13%.

- **The t fits far better than the normal or the logistic**: a joint misfit of 4.0 against 13.8 (the normal as it was), 17.7 (the
  normal integrated properly, which fails the requirements) and 8.3 (logistic). It matches the experiment as well as the old fit
  claimed to (miss 0.13). It holds 1.0% and 0.3% of a meat's buyers at three and four times the price, against the premium meats'
  1.5% and 0.6% and the normal's 0.8% and 0.1%. The response to a falling price drops from 5.2–7.5 to 3.6–3.7.
- **The mixture fits better still, and was not chosen.** With 5% of shoppers at three times the others' spread its misfit is 2.5;
  the best on its grid is 1.7. Two reasons against it. It needs two extra parameters where the t needs one. And its best fit runs
  to the corner of the grid: 2% of shoppers with six times the others' spread. That is a small block of shoppers who buy at almost
  any price. It leaves 0.22% of a meat's buyers at eight times the price and 0.13% at ten times (the t: 0.03% and 0.01%), and it
  gives published cells, at $112 a kilo, 0.02% of world meat (the t: 0.002%). Nothing measured shows such a block; the evidence on
  price-insensitive shoppers is that they are the most hostile to cultivated meat (section 1).

**What the two numbers mean.**

- `liking_sd` = 3.9 utils: how far apart shoppers are. A shopper one standard deviation keener than another will pay about twice
  as much (2.1 times) for the same chance of buying. For comparison, the wariness at first contact is 2.8 utils.
- `liking_tail` = 4: how many shoppers sit far from the average. Against a normal spread of the same standard deviation, more
  shoppers are close to the average (77% within one standard deviation, against 68%) and more are very far from it: 1 in 150 is
  more than three standard deviations keener than average, against 1 in 740; 1 in 420 more than four, against 1 in 32,000.
  Those few are who still buys at three or four times meat's price.

**How well the data pin them.** Loosely (`liking_spread.profile`; `python liking_spread.py --families` prints it, the test does
not re-run it):

| tail (degrees of freedom) | best spread, utils | joint misfit |
|---|---|---|
| 2.2 | 4.6 | 4.59 |
| 2.5 | 3.85 | 3.85 |
| 3 | 3.7 | 3.67 |
| 3.5 | 3.75 | 3.80 |
| **4** | **3.9** | **4.02** |
| 4.5 | 4 | 4.30 |
| 5 | 4.05 | 4.69 |
| 6 | 4.2 | 5.38 |
| 8 | 4.35 | 7.06 |
| 12 | 4.55 | 9.43 |
| 30 (nearly normal) | 4.6 | 17.91 |

- The misfit is least at a tail of 3 with a spread of 3.7 (3.67). Within 20% of that: a spread of 3.45 to 4.15 and a tail of 2.5
  to 4.5. The model's 3.9 and 4 are inside, 10% above the least.
- **4 and not 3 is a choice, not a fit.** The misfit cannot tell them apart, and three things it does not count favour the lighter
  tail: first contact (4.3% at a tail of 4, 3.9% at 3, measured 5%); shares at ten or more times meat's price, where a heavier tail
  leaves more buyers than any premium meat shows; and the best case, which a narrower middle lowers (13.8% at 4, 12.0% at 3).
  Central would be 0.19% at a tail of 3, against 0.16%.
- The experiment alone would put the spread at 3.6 (miss 0.01, section 3). Its own estimate was 3.6–4.6 on its scale, about 3.3–4.7
  of the model's utils.

**The integration rule.** The model now integrates every shape but the normal over 67 points on a stretched grid
(`market_share.grid_quadrature`). Against a 20,001-point reference:

| shape | rule | points | largest error of the share at 1 to 5 times the price | error at 8 times |
|---|---|---|---|---|
| normal, spread 5 | Gauss-Hermite (the model of 2026-11-18) | 15 | 4.89% | 3.1% |
| normal, spread 5 | Gauss-Hermite | 61 | 0.03% | 0.0% |
| Student's t | Gauss-Legendre in probability | 60 | 11.53% | 85.0% |
| Student's t | Gauss-Legendre in probability | 120 | 0.14% | 0.8% |
| Student's t | stretched grid (the model's rule) | 67 | 0.03% | 0.3% |
| mixture | Gauss-Hermite per component | 62 | 5.62% | 0.1% |
| mixture | stretched grid | 67 | 0.01% | 0.6% |

The model's rule is within 0.03% at 1 to 5 times the price and 0.3% at eight times. The textbook rules need 120 points or more for
a heavy tail and are erratic far out. With `LIKING_FAMILY = "normal"` and `liking_sd = 5.0` the model of 2026-11-18 is reproduced to
the last digit (tested).

## 3. The fit to the choice experiment alone

Cultivated meat's utility gets the t spread (tail 4) across shoppers; the mean is set so that 5% buy at equal price at first
contact, as in the experiment. The table gives the model's own-price elasticity at four prices of the lab-grown burger against
the experiment's, for several spreads and for three values of each shopper's price sensitivity.

| each shopper's price sensitivity (times meat's) | spread of liking, utils | elasticity at 0.6×, 1×, 1.4×, 1.8× beef's price | miss |
|---|---|---|---|
| **measured (Van Loo, Caputo & Lusk 2020, simulated from its fitted model)** | | -0.87, -1.50, -2.00, -2.40 | |
| 4 | 0 | -0.89, -1.55, -2.22, -2.89 | 0.27 |
| 4 | 2 | -0.63, -1.08, -1.52, -1.94 | 0.41 |
| 4 | 3.6 | -0.42, -0.70, -0.96, -1.21 | 0.91 |
| 4 | 3.9 | -0.39, -0.65, -0.90, -1.13 | 0.97 |
| 4 | 5 | -0.31, -0.52, -0.71, -0.89 | 1.14 |
| 4 | 6 | -0.26, -0.43, -0.59, -0.75 | 1.25 |
| 6 | 0 | -1.28, -2.32, -3.36, -4.37 | 1.28 |
| 6 | 2 | -0.93, -1.62, -2.27, -2.85 | 0.27 |
| 6 | 3.6 | -0.63, -1.05, -1.43, -1.77 | 0.50 |
| 6 | 3.9 | -0.59, -0.97, -1.33, -1.64 | 0.59 |
| 6 | 5 | -0.47, -0.77, -1.05, -1.31 | 0.83 |
| 6 | 6 | -0.39, -0.65, -0.88, -1.11 | 0.98 |
| 8.5 | 0 | -1.71, -3.29, -4.79, -6.22 | 2.56 |
| 8.5 | 2 | -1.27, -2.29, -3.20, -3.86 | 1.04 |
| 8.5 | 3.6 | -0.89, -1.48, -2.00, -2.40 | 0.01 |
| **8.5** | **3.9** | -0.83, -1.38, -1.86, -2.24 | **0.13** |
| 8.5 | 5 | -0.67, -1.09, -1.47, -1.79 | 0.46 |
| 8.5 | 6 | -0.56, -0.92, -1.23, -1.52 | 0.67 |

- **At the model's own price sensitivity (8.5) a spread of 3.6 fits the experiment almost exactly** (miss 0.01). The model's 3.9,
  the joint fit with premium meats and salmon, misses by 0.13. With no spread the model misses by 2.56: its elasticity at equal
  price is -3.29 against the measured -1.5.
- A lower price sensitivity fits only with little or no spread, and worse (4 with none: 0.27; 6 with 2: 0.27). Keeping 8.5
  changes nothing else in the model.
- The table of 2026-11-18, for a normal spread, had 5 utils as the best fit with a miss of 0.15. That was the fifteen-point error
  (section 2).

## 4. The share at equal price in the long run

| the long run | share at equal price | share of a meat at 1.25×, 1.5×, 2×, 3×, 4× its price | world share, 1. Published cells | world share, 4. Plus perfusion (Selected cells) | world share, 7. Plus everything else at its favourable end (Engineered cells, all favourable) |
|---|---|---|---|---|---|
| first contact (as measured) | 5% | 3.6%, 2.5%, 1.4%, 0.5%, 0.2% | under 0.001% | 0.1% | 1.4% |
| novelty fades by what the model assumes | 15% | 10.8%, 7.7%, 3.8%, 1.1%, 0.4% | under 0.001% | 0.2% | 3.6% |
| shoppers indifferent on average (the premise before 2026-11-18) | 49% | 39.2%, 30.4%, 16.7%, 4.2%, 1.2% | under 0.001% | 0.7% | 12.8% |
| the model before 2026-11-18 (every shopper alike) | 49% | 28.8%, 14.6%, 2.9%, 0.09%, 0.003% | under 0.001% | 0.06% | 5.9% |
| premium real meats (the curve fitted to sixteen) | | —, 5.7%, 3.7%, 1.5%, 0.6% |  |  |  |

The world shares use each scenario's cost of cells with the reading's own demand. The best case's column is its cells at these
readings, not the best case's own 55% at equal price, which gives 13.8%.

- **With every shopper alike**, removing first-contact wariness (the model's `neophobia_x0`, -2.8 utils) took cultivated meat from 5% to
  about half the market at equal price.
- **With the spread, the same removal takes it from 5% to 15%.** Half the market needs the average shopper's liking to recover by
  6.5 utils, more than twice the wariness the model assumes: shoppers indifferent between the two meats on average.
- **The model's setting stays at 13%, a little below this reading.** With the normal spread the same removal gave 13%, and that is
  where the setting came from. With the t it gives 15%. The setting was kept: it is a judgement with two other supports (section
  5). Read backwards, 13% in the long run means 4.3% at first contact, against the measured 5%. The middle row's world shares
  are therefore a little above the model's: 0.18% against 0.16% for Central, 3.2% against 2.7% for the best case's cells.
- **The middle reading lands near premium real meats**: 3.8% at twice the price against their 3.7%, 1.1% at three times against
  1.5%, 0.4% at four times against 0.6%. Since 2026-11-19 the shape is fitted to them, so this is no longer an independent check.
- **Across the three readings Central runs from 0.1% to 0.7% of world meat**, about six-fold, and the best case's cells from
  1.4% to 12.8% (2026-11-19: the share of the meat sold; the best case's cells weigh 2 ng). For Central the cost matters more: across the 8-in-10 range of its cost of cells ($27 to $57 a kilo) the share
  at the 13% setting runs from 0.3% to 0.02%, about fourteen-fold.

## 5. The default chosen

- `LIKING_FAMILY` = Student's t, `liking_sd` = 3.9 utils (fitted; range 3.6–4.2), `liking_tail` = 4 (fitted loosely; range 3–6).
  Neither is drawn in the bands.
- `equal_price_share` = 13% (judgement). Since 2026-11-19 it is drawn in the bands from a lognormal with median 13% (5th–95th
  percentile about 3–52%). Before, it was drawn from a triangle from 5% to 49% with its mode at 13%, whose median was 21%, well
  above the setting (audit finding D1).
- Why 13%: a little over a third of first-contact aversion fading, by two routes. On the model's scale, 13% is 2.4 of the 6.5
  utils between first contact and indifference; the model's own novelty term is 2.8 utils, which would give 15%. In the survey
  corrections (`premium_curve.CORRECTIONS`), first contact is 45% of meat's price dearer (novelty 30, "unnatural" 20, less 5 for
  no killing) and the long-run central case is 30% (novelty halved, "unnatural" kept): 15 of 45 points close.
- A reading of foods made by distrusted processes (`demand_heterogeneity_evidence.md` §6) puts the median near 18%: below 8% with
  0.17, 8–25% with 0.45, 25–40% with 0.24, above 40% with 0.14. The literature review (`what_drives_choice.md`) puts the 10th, 50th
  and 90th percentiles at 2%, 10% and 35%.
- The share at equal price is the long-run dial; the no-slaughter, long-run novelty and health dials are parts of it, are not
  drawn in the bands, and stay on the page as what-ifs on top.
- The best case sets its own share at equal price, 55% (35–70%; `best_equal_price_share`).

## 6. Worries and limits

- **The best case falls by a third: 19.9% to 13.8% of world meat with its own demand.** Nothing about the best case changed. The
  fitted t is narrower in the middle: a smaller standard deviation (3.9 against 5) with more shoppers close to the average. With
  55% buying at equal price most shoppers sit near the tipping point, so a price above meat's loses them faster. No data measure
  the middle of the spread beyond the one experiment. The logistic gives 16.4% and the mixtures 16.1–16.8%, so the shapes that
  fit span about 14–17%; the normal gave 20%. With the model's ordinary 13% the best case's cells barely move (2.8% to 2.7%).
- **First contact comes out at 4.3%, against the measured 5%**, with an elasticity of -1.37 against -1.5 (inside the experiment's
  range across its arms, -1.1 to -1.65). Every shape that fits the tail has this: 4.3–4.6%.
- **Farmed salmon's response still fails**: 3.6–3.7% more share per 1% off the price, against 1–1.5%. Better than the normal's
  5.2–7.5, still more than twice the top of the range (`demand_checks.md`). The mixture is a little lower (2.8–3.5) and fails too.
- **Above five times meat's price the tail is an extrapolation.** The dearest premium meat in the data sits at 3.6 times its
  ordinary product, and the fit uses the curve at 2, 3 and 4 times. The model gives 0.15% of a meat's buyers at five times the
  price, 0.03% at eight and 0.01% at ten; nothing measures these. They matter where cells are dear: about a sixth of Central's
  sales at its own cost come from products at more than five times their meat's price, and a third from above four times. All
  of the published cells' 0.002% is from there.
- **The tail is loosely pinned** (2.5 to 4.5), and 4 was chosen over the least-misfit 3 on grounds the fit does not count.
- One experiment, hypothetical choices, burgers, first contact, and the name "lab-grown". The spread in the long run may be narrower.
- The fit uses elasticities simulated from the paper's published coefficients, since the paper reports none.
- Price sensitivity also differs across shoppers (4 to 10 times between groups, `demand_heterogeneity_evidence.md` §3); not in the
  model, and not needed to match the experiment. Plant-based meat's own elasticity is still too strong (`demand_checks.md`).
