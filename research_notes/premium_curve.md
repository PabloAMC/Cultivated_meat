# Anchoring cultivated meat's demand on premium real meats

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50.

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
- **The model's curve falls far faster.** Its demand for a real-meat product at a premium, with no virtue, gives 0.09% at 3× and nothing
  at 4×. It misses the sixteen premium products by a typical factor of about 6 (rms log error 1.79).
- **A curve fitted to them** misses by a factor of about 2.4 (error 0.89). Its shoppers are about a quarter as
  price-sensitive as the model's (κ 2.2 against 8.5), and start from a lower level.
  Its cold at-parity elasticity (-0.90) is inside the range the one choice experiment on cultivated meat measured
  (Van Loo, Caputo and Lusk 2020, −0.84 to −3.4); the fit is held to that range.
- **No loyal niche.** A small segment that pays whatever the premium, beside the model's mainstream, fits no better; it runs to its 30%
  cap. The six points used so far had suggested a flat 2–7%; with the high-premium pairs that flatness goes.

| share of the category at premium R | 1× | 1.25× | 1.5× | 2× | 2.5× | 3× | 4× | 5× |
|---|---|---|---|---|---|---|---|---|
| the main model | 47.78% | 28.33% | 14.39% | 2.90% | 0.53% | 0.09% | 0.00% | 0.00% |
| fitted to all sixteen premium products | 8.68% | 7.06% | 5.72% | 3.72% | 2.40% | 1.54% | 0.63% | 0.26% |

| data | curve | parameters | typical miss (rms log error) | cold at-parity elasticity |
|---|---|---|---|---|
| the six used so far | the main model as it is | κ 8.5, no virtue term | 0.96 | -3.27 |
| the six used so far | one kind of shopper | κ 2.07, v -2.58 | 0.46 | -0.84 |
| the six used so far | the model's mainstream plus a loyal minority | κ 8.50, v -63.44, loyal share 5%, v loyal 3.86, κ loyal 7.77 | 0.43 | -0.84 |
| all sixteen | the main model as it is | κ 8.5, no virtue term | 1.79 | -3.27 |
| all sixteen | one kind of shopper | κ 2.22, v -2.31 | 0.89 | -0.90 |
| all sixteen | the model's mainstream plus a loyal minority | κ 8.50, v -11.20, loyal share 30%, v loyal -0.94, κ loyal 2.36 | 0.89 | -0.94 |
| sixteen plus Ibérico | the main model as it is | κ 8.5, no virtue term | 2.10 | -3.27 |
| sixteen plus Ibérico | one kind of shopper | κ 2.07, v -2.26 | 0.96 | -0.84 |
| sixteen plus Ibérico | the model's mainstream plus a loyal minority | κ 8.50, v -2.46, loyal share 30%, v loyal -1.35, κ loyal 1.43 | 0.95 | -1.83 |

## 2. Cultivated meat on the curve

The corrections, as the fraction of meat's price a shopper would pay for each difference (`cultivated_vs_welfare_meat_evidence.md`;
hypothetical willingness to pay, so levels inflated and ratios better supported): no killing +5% (−5% to +20%), novelty −30%
(−15% to −60%; half of it fades in the long run, the central case), unnatural −20% (−5% to −45%; likely to persist, as for GM foods).
A correction moves cultivated meat along the premium axis: it sells like a label product priced that much higher or lower. The
long-run central case nets -30%: cultivated meat sells like a premium label priced 30% of meat's price higher.

World long-run share, by the model's own roll-up across meat types and regions:

| scenario | cells, $/kg | the main model | as a premium label (no correction) (+0%) | first contact (-45%) | long run, central (-30%) | long run, favourable (novelty gone) (+15%) | long run, unfavourable (novelty stays) (-110%) |
|---|---|---|---|---|---|---|---|
| 1. Today | $56.99 | **0.01%** | 0.02% | 0.01% | 0.01% | 0.02% | 0.01% |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | $26.43 | **0.13%** | 0.31% | 0.19% | 0.23% | 0.37% | 0.10% |
| Forecast for 2035 | $23.24 | **0.22%** | 0.46% | 0.28% | 0.33% | 0.54% | 0.14% |
| 5. Plus engineered cells | $9.96 | **2.74%** | 2.50% | 1.59% | 1.85% | 2.91% | 0.83% |

## 3. What this says

- **At Central's price the premium curve gives nearly twice the model's share.** Anchored on premium meats, Central takes 0.23% in the
  long run (0.10–0.37% across the corrections), against the model's 0.13%. Since 2026-11-18 the model has a spread of liking across
  shoppers (`liking_spread.md`), which gives it a slow tail like the premium meats' (0.8% of a meat's buyers at three times the price,
  against their 1.5%); the two now differ by a factor of under two, not five.
- **Near price parity they disagree the other way.** The best case takes 1.8% anchored on premium meats (0.8–2.9%),
  against the model's 2.7%. The single curve takes its level at equal price from premium labels (7%), which are never cheaper than
  the ordinary product, and the premium data start at 1.5×. The model sets that level as a judgement (13%, `liking_spread.md`).
  (History: with the flat $5 markup Central was 0.40% against 0.41% and the best case 2.5% against 8.0%; with the shop's percentage
  margin, 0.16% against 0.16% and 1.8% against 3.7%; with the premium markets sized from data and every shopper alike, 0.14% against
  0.04% and 1.8% against 3.1%; with a spread of liking, before the medium was repriced on 2026-11-19, 0.16% against 0.08% and 1.9%
  against 2.9%.)
- **The no-killing bonus is small, and the penalties win.** In stated preferences "without harming animals" counts for about as much as a
  health claim, so the corrections net out against cultivated meat in every case but the favourable one.
- **Other fits change little.** The loyal-minority fit gives Central 0.22%; adding Ibérico ham (a share of
  ibérico ham only, a luxury niche) gives 0.29%.

Probabilities (judgement): Central's long-run share is within a factor of 2 of 0.4%: about 65%. Anchoring on premium meats raises it above
0.6%: about 20%; before this study I had put about 55% on it rising, which the high-premium data did not bear out. The best case's
long-run share is below 4%: about 55%.

## 4. Caveats

- **The shares are not all alike.** Some are of volume, some of value, of purchases or of production; premiums are cut-matched in some
  sources and not others. The fit's typical miss of a factor of 2.4 reflects that.
- **Supply limits.** Above about 2.3× several shares are capped by supply or stocking (UK organic chicken is absent from discount
  stores; French organic supply is shrinking; bellota output is capped by the acorn pastures). Demand at those premiums may be higher.
- **Hypothetical corrections.** No study prices cultivated meat and a welfare label for the same respondents; the corrections are
  assembled across studies.
- **Nothing changes in the model.** The note is a check on its demand side. Whether to show this second estimate on the page, or to
  refit κ, is open (`TODO.md`).
