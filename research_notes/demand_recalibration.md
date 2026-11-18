# The shopper model recalibrated: two kinds of shopper for cultivated meat

Date: 2026-11-18. Changes defaults: `market_share.share` and four new inputs. Test: `tests/test_demand_recalibration.py`. Follows
`demand_checks.md`, which found the model's response to price two to four times too strong.

## 1. What was wrong, and the fix that was not taken

The model let cultivated meat's share fall very fast as its price rose above meat's: 0.09% of a meat's buyers at three times the price,
where premium real meats (organic and free-range chicken and eggs, Label Rouge) take about 1.5%. Three measurements said the
response was too strong (`demand_checks.md`).

The first proposal was to put cultivated meat on the single curve fitted to the sixteen premium meats, slope and level. Pablo
objected: that takes the best case from 3.1% to 1.8%, though its cells cost about $7 more than parity needs and cultivated beef would
be near or below beef's price. He was right. That curve takes its level from premium labels as well as its slope: 7% at equal price.
Labels are never cheaper than the ordinary product and the data start at 1.5 times its price, so the level at equal price is an
extrapolation, and a real meat at or below the ordinary one's price would take far more. Farmed salmon against wild is the case in
history: cheaper and equivalent took most of the market. The measurements say the model's **tail** is too thin. They say nothing
against most shoppers switching near parity.

## 2. The fix: two kinds of shopper

- **Most shoppers (90%) are as the model had them.** They switch near equal price and drop out fast above it (8.5 times as
  price-sensitive as meat demand in general).
- **Premium buyers (10%) respond as buyers of premium real meats do.** To them cultivated meat is another premium meat: 2.15
  times as price-sensitive as meat in general, with the liking for a premium meat that the sixteen products imply (+0.11 utils),
  both fitted with the mainstream held as it is (`premium_buyers.fit_at`; typical miss a factor of 2.4, the same as the single
  curve). It sells to them as if priced 0.30 of the ordinary meat's price dearer: a lasting wariness of a new food (0.15) and an
  "unnatural" image (0.20), less what no killing is worth over a welfare label (0.05) (`cultivated_vs_welfare_meat_evidence.md`).
- The share is the weighted sum. The 10% comes from purchase data, not from the fit, which cannot tell sizes apart (`premium_buyers.md`
  §4): about 5–8% of shoppers in the UK and US, 12–20% in France.

| price against the meat beside it | 0.6× | 0.8× | 1× | 1.25× | 1.5× | 2× | 3× | 4× | 6× |
|---|---|---|---|---|---|---|---|---|---|
| the model now | 76.1% | 63.6% | 48.3% | 29.8% | 16.6% | 5.2% | 1.3% | 0.6% | 0.1% |
| the model before | 78.7% | 65.2% | 48.8% | 28.8% | 14.6% | 2.9% | 0.09% | 0.00% | 0.00% |
| premium real meats (one curve fitted to sixteen) | — | — | — | — | 5.7% | 3.7% | 1.5% | 0.6% | 0.1% |

Share of a meat's buyers (reference shopper, long run).

## 3. What moves and what does not

| scenario | cells, $/kg | long-run share of world meat, before | now |
|---|---|---|---|
| 1. Today | $62.96 | 0.00% | 0.01% |
| 2. Plus process changes and cheaper inputs | $30.73 | 0.04% | 0.2% |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | $29.42 | 0.04% | 0.2% |
| 4. Plus a food-grade plant with shared medium | $26.56 | 0.06% | 0.3% |
| 5. Plus engineered cells | $9.66 | 3.1% | 4.5% |
| Forecast for 2035 | $24.80 | 0.08% | 0.4% |

- **Central's share rises from 0.04% to 0.2% of world meat and the best case's from 3.1% to 4.5%.** Central's rise is premium
  buyers paying three to six times the price for ordinary cuts, as a few percent of shoppers do for organic chicken; the best case's is
  the same buyers on top of a mainstream that was already switching.
- **At equal price the share is 48%** (it was 49%): the mainstream is unchanged, and premium buyers are a little below it because of
  the image handicap.
- **At three times the price it is 1.3%**, against premium meats' 1.5% and the old model's 0.09%.
- **At first contact and equal price the own-price elasticity is -3.06**, inside the choice experiment's −0.84 to −3.4.
- **The calibration is untouched**: the price coefficient, the solved weights, plant-based meat's 1.2% and every check on existing
  products are as before, because premium buyers differ from other shoppers only in how they see cultivated meat. With no cultivated
  meat on the shelf the two kinds are the same.
- Costs do not change.

## 4. What it still does not fix

- **Plant-based meat's own-price elasticity is still -2.85 in the model against a measured -1.23.** That belongs to the price
  terms all products share, and changing them re-solves the whole calibration. It matters little for cultivated meat's share
  (plant-based meat at parity moves it by under 3%), and the measured figure has not been read at its source. It stays in TODO.
- **The model's premium products still respond to price about twice as strongly as farmed salmon did** along its demand curve
  (2.7–3.0% more volume per 1% lower price, against 1.0–1.5%).
- **Premium buyers are assumed to treat every meat the same way.** The sixteen products are chicken, eggs, milk and "all organic
  meat"; nothing says the same shoppers would pay four times the price for cultivated pork mince.
- **The image handicap comes from stated-preference studies.** It is drawn in the uncertainty bands across −0.15 to +1.10.

## 5. On the page and in the bands

Two sliders, "Premium buyers" and "Image handicap for premium buyers", are in the advanced panel on shoppers. Setting premium buyers
to 0 gives the model as it was. The image handicap is drawn in every share band; the share of premium buyers is not, because their
liking and price sensitivity are fitted at 10%.

## 6. Judgement

- That two kinds of shopper describe demand above parity better than the model before: about 0.8.
- That Central's long-run share, at Central's cost, is within a factor of three of 0.2%: about 0.6.
- That the best case's is within a factor of two of 4.5%: about 0.5. Near parity the share still rests on the model's premise that
  shoppers see cultivated meat as real meat that tastes the same.
