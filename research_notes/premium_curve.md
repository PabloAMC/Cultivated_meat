# Anchoring cultivated meat's demand on premium real meats

> Names (2026-11-19): "Selected cells" was called Central; "Engineered cells, all favourable" was called the best case.

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50; cut cost rebuilt (0.8 cells + $2 matrix + $2 assembly beyond mince), cuts cheaper.

> Repinned 2026-11-19 (audit batch): cells dearer (ammonia tolerance 4 mM), seafood re-priced by consumption, the tier rule replaced by a blend penalty, the equal-price share drawn around its 13% setting; see audit_2026-11-19.md.

> Repinned 2026-11-19 (second round): shoppers' liking is a Student's t spread (standard deviation 3.9 utils, 4 degrees of freedom) on a 67-point grid, not a normal spread of 5 on fifteen points; see liking_spread.md.

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
  gives 0.09% at 3× and under 0.01% at 4×. It misses the sixteen premium products by a typical factor of about 6 (rms log error 1.79).
- **A curve fitted to them** misses by a factor of about 2.4 (error 0.89). Its shoppers are about a quarter as
  price-sensitive as the model's (κ 2.2 against 8.5), and start from a lower level.
  Its cold at-parity elasticity (-0.90) is inside the range the one choice experiment on cultivated meat measured
  (Van Loo, Caputo and Lusk 2020, −0.84 to −3.4); the fit is held to that range.
- **No loyal niche.** A small segment that pays whatever the premium, beside the model's mainstream, fits no better; it runs to its 30%
  cap. The six points used so far had suggested a flat 2–7%; with the high-premium pairs that flatness goes.

| share of the category at premium R | 1× | 1.25× | 1.5× | 2× | 2.5× | 3× | 4× | 5× |
|---|---|---|---|---|---|---|---|---|
| the main model | 47.78% | 28.33% | 14.39% | 2.90% | 0.53% | 0.09% | under 0.01% | under 0.01% |
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

World long-run share, by the model's own roll-up across meat types and regions. Every row uses the model's ordinary demand; the
last row is the best case's cells with that demand (2.74%), not the best case's own 55% at equal price, which gives 13.8%:

| scenario | cells, $/kg | the main model | as a premium label (no correction) (+0%) | first contact (-45%) | long run, central (-30%) | long run, favourable (novelty gone) (+15%) | long run, unfavourable (novelty stays) (-110%) |
|---|---|---|---|---|---|---|---|
| 1. Published cells | $209.05 | **under 0.01%** | under 0.01% | under 0.01% | under 0.01% | under 0.01% | under 0.01% |
| 4. Plus perfusion (Selected cells) | $32.80 | **0.21%** | 0.19% | 0.10% | 0.12% | 0.24% | 0.04% |
| 7. Plus everything else at its favourable end (Engineered cells, all favourable) | $11.67 | **3.16%** | 2.35% | 1.38% | 1.64% | 2.81% | 0.65% |

## 3. What this says

- **At Central's price the model is now above the premium curve, inside the curve's own range.** Anchored on premium meats, Central
  takes 0.12% in the long run (0.04–0.24% across the corrections), against the model's 0.21%. The model's share is 1.6 times the
  anchored one and sits near the favourable end of the range. Since 2026-11-19 the model's spread of liking across shoppers is a
  Student's t (`liking_spread.md`), whose tail is fitted to these same premium meats at 2, 3 and 4 times the price: it holds 1.0%
  of a meat's buyers at three times the price, against their 1.5%. The heavier tail doubled the model's share at Central's price
  (0.08% to 0.16%); the anchored share does not depend on the spread and did not move. So the order has flipped again: the
  anchored share was a tenth below the model's before the audit batch, a third above it after, and is now two-fifths below.
  For one shopper at the model's reference income, buying a product that is all cells, the two would be about equal. The gap
  comes from the blend penalty on cuts and the world's lower income: both cut a curve with every shopper alike by more than
  they cut a wide spread of liking.
- **Near price parity they disagree the same way, and by more than the corrections span.** The best case's cells take 1.6% anchored
  on premium meats (0.7–2.8%), against the model's 3.2%: the model gives twice the curve's central figure and sits above its
  favourable end. The single curve takes its level at equal price from premium labels (7%), which are never cheaper than
  the ordinary product, and the premium data start at 1.5×. The model sets that level as a judgement (13%, `liking_spread.md`).
  (History: with the flat $5 markup Central was 0.40% against 0.41% and the best case 2.5% against 8.0%; with the shop's percentage
  margin, 0.16% against 0.16% and 1.8% against 3.7%; with the premium markets sized from data and every shopper alike, 0.14% against
  0.04% and 1.8% against 3.1%; with a spread of liking, before the medium was repriced on 2026-11-19, 0.16% against 0.08% and 1.9%
  against 2.9%; before the cut cost was rebuilt on 2026-11-19, 0.23% against 0.13% and 1.8% against 2.7%; before the audit batch
  of 2026-11-19, 0.48% against 0.53% and 2.6% against 5.0%; after it, with the normal spread, 0.10% against 0.08% and 1.4%
  against 2.8%.)
- **The no-killing bonus is small, and the penalties win.** In stated preferences "without harming animals" counts for about as much as a
  health claim, so the corrections net out against cultivated meat in every case but the favourable one.
- **Other fits change little.** The loyal-minority fit gives Central 0.10%; adding Ibérico ham (a share of
  ibérico ham only, a luxury niche) gives 0.13%.

Probabilities (judgement; provisional, revised twice on 2026-11-19), each given the scenario's cost of cells. Central's
long-run share is within a factor of 2 of 0.13% (0.065–0.26%): about 45%. The model (0.16%) and the anchored curve (0.10%) both
sit there, but the corrections alone span 0.04–0.24% and the share at equal price is uncertain on top (0.09% to 0.6% across its
three readings, `liking_spread.md`). It is above 1%: about 3% (even shoppers indifferent on average give 0.6%). Before the audit
batch these read "within a factor of 2 of 0.5%: about 65%" and "above 1%: about 20%". Before this study I had put about 55% on
anchoring raising the share, which the high-premium data did not bear out. The best case's cells with the model's ordinary demand
take less than 4% in the long run: about 70% (the model gives 2.7%, the anchored curve 1.4%, and the curve's favourable end 2.5%;
before the audit batch, about 45%, with the model at 5.0% and the curve at 2.6%).

## 4. Caveats

- **The shares are not all alike.** Some are of volume, some of value, of purchases or of production; premiums are cut-matched in some
  sources and not others. The fit's typical miss of a factor of 2.4 reflects that.
- **Supply limits.** Above about 2.3× several shares are capped by supply or stocking (UK organic chicken is absent from discount
  stores; French organic supply is shrinking; bellota output is capped by the acorn pastures). Demand at those premiums may be higher.
- **Hypothetical corrections.** No study prices cultivated meat and a welfare label for the same respondents; the corrections are
  assembled across studies.
- **Nothing changes in the model.** The note is a check on its demand side. Whether to show this second estimate on the page, or to
  refit κ, is open (`TODO.md`).
