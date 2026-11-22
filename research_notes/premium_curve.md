# Anchoring cultivated meat's demand on premium real meats

> Names (2026-11-19): the two examples are named by what they assume (the low-lactate example, the all-favourable example). Cells are described by their traits, never as a named kind of cell.

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50; cut cost rebuilt (0.8 cells + $2 matrix + $2 assembly beyond mince), cuts cheaper.

> Repinned 2026-11-19 (audit batch): cells dearer (ammonia tolerance 4 mM), seafood re-priced by consumption, the tier rule replaced by a blend penalty, the equal-price share drawn around its 13% setting; see audit_2026-11-19.md.

> Repinned 2026-11-19 (second round): shoppers' liking is a Student's t spread (standard deviation 3.9 utils, 4 degrees of freedom) on a 67-point grid, not a normal spread of 5 on fifteen points; see liking_spread.md.

> Repinned 2026-11-21 (engine batch): the cost of cells moved (the all-favourable example $7.62 -> $6.97, its tank design now holds the culture thinner so its oxygen column passes its checks; the low-lactate example $49.50 -> $48.68; published cells $322.55 -> $316.11), because the design search runs a culture thinner when its loop fails, the building's power follows its floor and its class, and part of the crew is counted per tank. Nothing in the demand model changed; the shares that follow from the costs are recomputed.

> Repinned 2026-11-20 (engine batch): the scenarios' cells tolerate 35 mmol/L of lactate, bubble deaths and a harvest loss are charged, a washed tank takes twice the fed-batch crew, the membrane lasts 2,415 L/m2, and growth factors, utilities and the crew follow the Humbird back-test, so cells are dearer (the low-lactate example $32.80 to $49.96 a kilo, the all-favourable example $11.67 to $18.71, Published cells in fed-batch $209 to $323) and every share here fell; the demand model did not change; see full_review_2026-11-19.md and humbird_backtest.md.

> Repinned 2026-11-20 (final pass): the all-favourable example is now `scenarios.all_favourable()` ($18.71 to $7.62 a kilo of cells), the low-lactate example costs $49.50; the demand side is anchored on plant-based meat at 0.4% of meat by volume, incomes are nominal, conventional meat's price falls as cultivated meat takes sales, and the share of the world market closed by law is weighted by meat eaten (closed_markets.md). The main model's curve for a premium real meat rose a little (0.09% to 0.10% at 3 times).

> Repinned 2026-11-22 (fifth batch): the model has price-insensitive shoppers (`demand_checks.md` section 7) and a refitted
> spread of liking; the main model's column and the conclusions of section 3 are recomputed. The anchored curve, with every shopper
> alike, barely moves.

Date: 2026-11-17. Code: `premium_curve.py`; test: `tests/test_premium_curve.py`. Data: `high_premium_analogues_data.md` (ten new
premium/share pairs, 1.7–3.6×) and `premium_meat_analogues.md` (the six the model already used); the corrections:
`cultivated_vs_welfare_meat_evidence.md`. Nothing here changes a default.

**The idea** (Pablo): premium real meats such as organic or free-range chicken, pasture-raised eggs and Label Rouge are "real meat plus a
virtue, at a premium". Cultivated meat is the same with a different virtue (no animal killed) and two costs (novelty, and an image of being
unnatural). So fit the curve the premium meats trace, share against price premium, and place cultivated meat on it, shifted by what
differs. Upside Foods reportedly prices its chicken like very high-end free-range chicken; this note asks what share that kind of price
buys.

## 1. What premium real meats show

- **Share falls as the premium rises, but slowly.** Every source that compares premiums within one dataset shows it falling: US eggs from
  8.6% (cage-free, 2.0×) to 0.3% (pasture-raised, 3.2×); French chicken from 13% (Label Rouge, 1.8×) to 1% (organic, 2.7×).
- **The model's curve falls far faster.** Its demand for a real-meat product at a premium, with no virtue and every shopper alike,
  gives 0.10% at 3× and under 0.01% at 4×. It misses the sixteen premium products by a typical factor of about 6 (rms log error 1.78).
- **A curve fitted to them** misses by a factor of about 2.4 (error 0.89). Its shoppers are about a quarter as
  price-sensitive as the model's (κ 2.2 against 8.5), and start from a lower level.
  Its cold at-parity elasticity (-0.90) is inside the range the one choice experiment on cultivated meat measured
  (Van Loo, Caputo and Lusk 2020, −0.84 to −3.4); the fit is held to that range.
- **No loyal niche.** A small segment that pays whatever the premium, beside the model's mainstream, fits no better; it runs to its 30%
  cap. The six points used so far had suggested a flat 2–7%; with the high-premium pairs that flatness goes.

| share of the category at premium R | 1× | 1.25× | 1.5× | 2× | 2.5× | 3× | 4× | 5× |
|---|---|---|---|---|---|---|---|---|
| the main model | 51.34% | 31.23% | 16.09% | 3.24% | 0.58% | 0.10% | under 0.01% | under 0.01% |
| fitted to all sixteen premium products | 8.69% | 7.06% | 5.72% | 3.72% | 2.40% | 1.54% | 0.63% | 0.26% |

| data | curve | parameters | typical miss (rms log error) | cold at-parity elasticity |
|---|---|---|---|---|
| the six used so far | the main model as it is | κ 8.5, no virtue term | 1.03 | -3.27 |
| the six used so far | one kind of shopper | κ 2.05, v -2.73 | 0.46 | -0.84 |
| the six used so far | the model's mainstream plus a loyal minority | κ 8.50, v -15.21, loyal share 5%, v loyal 3.67, κ loyal 7.63 | 0.44 | -0.84 |
| all sixteen | the main model as it is | κ 8.5, no virtue term | 1.77 | -3.27 |
| all sixteen | one kind of shopper | κ 2.19, v -2.46 | 0.89 | -0.90 |
| all sixteen | the model's mainstream plus a loyal minority | κ 8.50, v -19.87, loyal share 30%, v loyal -1.09, κ loyal 2.34 | 0.89 | -0.94 |
| sixteen plus Ibérico | the main model as it is | κ 8.5, no virtue term | 2.07 | -3.27 |
| sixteen plus Ibérico | one kind of shopper | κ 2.05, v -2.41 | 0.96 | -0.84 |
| sixteen plus Ibérico | the model's mainstream plus a loyal minority | κ 8.50, v -2.79, loyal share 30%, v loyal -1.47, κ loyal 1.46 | 0.95 | -1.71 |

## 2. Cultivated meat on the curve

The corrections, as the fraction of meat's price a shopper would pay for each difference (`cultivated_vs_welfare_meat_evidence.md`;
hypothetical willingness to pay, so levels inflated and ratios better supported): no killing +5% (−5% to +20%), novelty −30%
(−15% to −60%; half of it fades in the long run, the middle case), unnatural −20% (−5% to −45%; likely to persist, as for GM foods).
A correction moves cultivated meat along the premium axis: it sells like a label product priced that much higher or lower. The
long-run middle case nets -30%: cultivated meat sells like a premium label priced 30% of meat's price higher.

World long-run share, by the model's own roll-up across meat types and regions. Every row uses the model's ordinary demand; the
last row is the all-favourable example's cells with that demand (5.48%), not the all-favourable example's own 55% at equal price, which gives 25.1%:

| scenario | cells, $/kg | the main model | as a premium label (no correction) (+0%) | first contact (-45%) | long run, central (-30%) | long run, favourable (novelty gone) (+15%) | long run, unfavourable (novelty stays) (-110%) |
|---|---|---|---|---|---|---|---|
| 1. Published cells | $316.11 | **under 0.01%** | under 0.01% | under 0.01% | under 0.01% | under 0.01% | under 0.01% |
| 4. Plus perfusion (the low-lactate example) | $48.68 | **0.26%** | 0.02% | 0.01% | 0.01% | 0.03% | under 0.01% |
| 7. Plus everything else at its favourable end (the all-favourable example) | $6.97 | **5.48%** | 3.16% | 1.98% | 2.31% | 3.69% | 1.01% |

## 3. What this says

- **At the low-lactate example's price the model is far above the premium curve, and far above the curve's own range.**
  Anchored on premium meats, the low-lactate example takes 0.01% in the long run (0.00–0.03% across the corrections), against the
  model's 0.26%. Unrounded: 0.014% (0.004–0.028%) against 0.259%. The anchored share is about a twentieth of the model's, and the
  model's share is about nine times the favourable end of the range. (Since 2026-11-22's fifth batch: the model's
  price-insensitive shoppers, `demand_checks.md` section 7, buy most of what sells far above meat's price, and the curve, with
  every shopper alike, has none; before it, 0.015% (0.005–0.029%) against 0.045%, a third, and 1.6 times the favourable end.)
  (Before the 2026-11-20 engine batch made cells dearer the anchored share was two-fifths below the model's, 0.12% against 0.21%,
  and the model's was inside the range, 0.04–0.24%.) The gap is the model's demand far above meat's price: at $48.68 a kilo of
  cells chicken cuts, pork cuts, mince and processed meat are 7 to 15 times their meat's price, where no premium product is
  observed (the dearest of the sixteen is at 3.6 times), and there a shopper who responds a ninth as strongly to price still buys.
  Both figures are extrapolations there. Which is nearer the truth is the question `demand_checks.md` section 7 leaves open: the
  price-insensitive shoppers fit the premium meats at 2 to 4 times the price and farmed salmon better than the model without them,
  but their liking for cultivated meat is read from two stated-choice studies.
- **Near price parity the model is above the curve and above the corrections' range.** The all-favourable example's cells
  ($6.97 a kilo since 2026-11-21) take 2.3% anchored on premium meats (1.0–3.7%), against the model's 5.5%: the model gives 2.4 times
  the curve's central figure and 1.5 times its favourable end (before the fifth batch of 2026-11-22: 2.3%, 1.0–3.7%, against
  5.6%; before the fourth batch of 2026-11-21: 2.7%, 1.2–4.4%, against 6.1%; at $7.62: 2.5%, 1.1–4.0%, against 5.4%). At that cost the products of the world market are at 0.35 to 2.9 times their
  meat's price (beef cuts, premium seafood and dearer products below it). The single curve takes its level at equal price from
  premium labels (8.7%), which are never cheaper than the ordinary product, and the premium data start at 1.5×; the model sets
  that level as a judgement (14.4% of meat buyers, `liking_spread.md`) and its spread of liking holds more shoppers below and
  near equal price. Before the final pass the example's cells cost $18.71 and the model was 1.7 times the curve's central figure,
  just inside its favourable end (1.13% against 0.66%, range 0.24–1.17%).
  (History, the anchored share against the model's, low-lactate example then all-favourable example: with the flat $5 markup
  0.40% against 0.41% and 2.5% against 8.0%; with the shop's percentage margin, 0.16% against 0.16% and 1.8% against 3.7%; with
  the premium markets sized from data and every shopper alike, 0.14% against 0.04% and 1.8% against 3.1%; with a spread of
  liking, before the medium was repriced on 2026-11-19, 0.16% against 0.08% and 1.9% against 2.9%; before the cut cost was
  rebuilt on 2026-11-19, 0.23% against 0.13% and 1.8% against 2.7%; before the audit batch of 2026-11-19, 0.48% against 0.53%
  and 2.6% against 5.0%; after it, with the normal spread, 0.10% against 0.08% and 1.4% against 2.8%; with the Student's t
  spread, before the 2026-11-20 batch, 0.12% against 0.21% and 1.6% against 3.2%; after the engine batch, 0.020% against 0.046%
  and 0.66% against 1.13%.)
- **The no-killing bonus is small, and the penalties win.** In stated preferences "without harming animals" counts for about as much as a
  health claim, so the corrections net out against cultivated meat in every case but the favourable one.
- **Other fits change little.** The loyal-minority fit gives the low-lactate example 0.02%; adding Ibérico ham (a share of
  ibérico ham only, a luxury niche) gives 0.03%.

What would have to be true for the low-lactate example to reach 1% of the world in the long run: shoppers would have to like it
far more than the model's reading of the evidence gives (shoppers indifferent on average give about 1.7% at its cost since
2026-11-22, `liking_spread.md`). Its long-run share at $48.68 lies between the corrections' ends, 0.00–0.03%, and the model's 0.26%;
the share at equal price, and how much the price-insensitive shoppers like cultivated meat, are uncertain on top. The
all-favourable example's cells with the model's ordinary demand take 1.0–3.7% anchored on premium meats and 5.5% in the model; a share above about 5% needs the model's level at equal price rather than the
premium labels'. The high-premium data did not bear out the expectation, held before this study, that anchoring would raise the
share.

## 4. Caveats

- **The shares are not all alike.** Some are of volume, some of value, of purchases or of production; premiums are cut-matched in some
  sources and not others. The fit's typical miss of a factor of 2.4 reflects that.
- **Supply limits.** Above about 2.3× several shares are capped by supply or stocking (UK organic chicken is absent from discount
  stores; French organic supply is shrinking; bellota output is capped by the acorn pastures). Demand at those premiums may be higher.
- **Hypothetical corrections.** No study prices cultivated meat and a welfare label for the same respondents; the corrections are
  assembled across studies.
- **Nothing changes in the model.** The note is a check on its demand side. Whether to show this second estimate on the page, or to
  refit κ, is open (`TODO.md`).
