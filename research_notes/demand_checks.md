# Is the model's response to price as strong as measured ones?

> Names (2026-11-19): the two examples are named by what they assume (the low-lactate example, the all-favourable example). Cells are described by their traits, never as a named kind of cell.

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50; cut cost rebuilt (0.8 cells + $2 matrix + $2 assembly beyond mince), cuts cheaper.

> Repinned 2026-11-19 (audit batch): cells dearer (ammonia tolerance 4 mM), seafood re-priced by consumption, the tier rule replaced by a blend penalty, the equal-price share drawn around its 13% setting; see audit_2026-11-19.md.

> Repinned 2026-11-19 (second round): shoppers' liking is a Student's t spread (standard deviation 3.9 utils, 4 degrees of freedom) on a 67-point grid, not a normal spread of 5 on fifteen points; see liking_spread.md.

> Repinned 2026-11-20 (engine batch): the scenarios' cells tolerate 35 mmol/L of lactate, bubble deaths and a harvest loss are charged, a washed tank takes twice the fed-batch crew, the membrane lasts 2,415 L/m2, and growth factors, utilities and the crew follow the Humbird back-test, so cells are dearer (the low-lactate example $32.80 to $49.96 a kilo, the all-favourable example $11.67 to $18.71, Published cells in fed-batch $209 to $323) and every share here fell; the demand model did not change; see full_review_2026-11-19.md and humbird_backtest.md.

> Repinned 2026-11-21 (fourth batch): plant-based meat has a class of committed buyers (7% of shoppers, 82% of the mainstream's
> plant-based meat, a quarter of other shoppers' response to its price; section 5). Its elasticity is -1.30: the check passes.
> The ordinary shoppers' solved real-meat weight rose from 3.40 to 5.11 utils, so a cut that is part plant protein is liked less,
> and the all-favourable example's cells with the ordinary demand fell from 6.1% to 5.6%. Section 6 tries the same machinery on
> every shopper, for farmed salmon. The salmon row is unchanged (3.7-4.2).

> Repinned 2026-11-20 (final pass): the all-favourable example is now `scenarios.all_favourable()` ($18.71 to $7.62 a kilo of cells), the low-lactate example costs $49.50; plant-based meat is anchored at 0.4% of meat by volume (was 1.2% of choices), incomes are nominal, conventional meat's price falls as cultivated meat takes sales, and the share of the world market closed by law is weighted by meat eaten (closed_markets.md). The salmon row's last column is a value recorded on 2026-11-18, not recomputed.

> Changed 2026-11-22 (fifth batch): the model has price-insensitive shoppers (8% of every segment, 0.11 times other shoppers'
> response to every price, liking cultivated meat as much as other shoppers in utils), and the spread of liking was refitted with
> them (3.55 utils, tail 7). Section 7. Every table here is regenerated; the low-lactate example's share of world meat rose from
> 0.045% to 0.26%.

Date: 2026-11-18; revised the same day when the model gained a spread of liking across shoppers (`liking_spread.md`). Code:
`demand_checks.py`; test: `tests/test_demand_checks.py`.

Access levels: **FT** full text read; **ABS** abstract only; **SNIP** search snippet.

**Why.** How fast cultivated meat's share falls as its price rises above meat's decides the share in every scenario but the all-favourable example:
the low-lactate example's shop price is 1.4 to 14 times the meat it sits beside (1.37 times prime beef, 14.4 times processed chicken).

**In short (2026-11-22, fifth batch).** Three of the four checks pass, and the fourth fails by less. With price-insensitive
shoppers in the model (section 7) the first-contact elasticity is -1.51 (measured about -1.5), the share at three times the price
1.3% (premium real meats 1.5%) and plant-based meat's elasticity -1.03 (measured -1.23, the category about -1.3; -1.30 before).
Farmed salmon's response is 1.5–4.0 (3.7–4.2 before): the dearest premium product is at the top of salmon's 1–1.5, the one
nearest its meat's price still at 4.0. No setting of the class within the evidence puts all four inside. The low-lactate
example's share now rests mostly on how much the price-insensitive shoppers like cultivated meat.

**In short (2026-11-21, fourth batch).** Three of the four checks pass. Plant-based meat's elasticity now passes (-1.30 against
-1.23 measured, the category about -1.3), because its buyers are represented as what the data show: a committed minority that
responds less to its price (section 5). Farmed salmon still fails; section 6 shows that no defensible change to the same
machinery closes it. What follows is the account of 2026-11-20, with its numbers updated.

**On 2026-11-20.** Two of the four checks passed and two failed, as before. The two that pass are about the demand curve
alone: the model is inside the choice experiment's range at equal price (-1.37 against about -1.5), and it holds 0.9% of a
meat's buyers at three times the price against premium real meats' 1.5%. The failure against farmed salmon grew when the
2026-11-20 engine batch made cells dearer: the model's premium products respond to a falling price at 3.7–4.3, about two and a
half to three times the top of salmon's range (3.6–3.7 before; 5.2–7.5 with the normal spread). It still fails on plant-based
meat's elasticity, now by more (-2.89 against -1.23), since plant-based meat was re-anchored at 0.4% of meat by volume. The
shape of the spread is fitted to the first three of these (`liking_spread.md` §2), so they are not independent checks of it.

## 1. The four checks

| what was measured | measured | the model | the model before 2026-11-18 |
|---|---|---|---|
| Cultivated meat at first contact and equal price: own-price elasticity (choice experiment, simulated from its fitted model) | about -1.5 (-1.1 to -1.65 across its arms) | -1.51 | -3.27 |
| Share of a meat at 3 times the ordinary one's price (sixteen premium real meats, fitted) | 1.5% | 1.3% | 0.1% |
| A premium product getting cheaper: percent more volume per percent lower price (farmed salmon) | 1–1.5 | 1.5–4.0 (organic chicken, heritage pork, premium fish fillets and shrimp, sushi-grade seafood: the premium products still dearer than their meat) | 3.0–3.4 (recorded on 2026-11-18 at that day's costs; not recomputed) |
| Plant-based meat's own-price elasticity (US retail; the category is about -1.3) | -1.23 | -1.03 | -2.89 (with no committed buyers, the model before 2026-11-21's fourth batch) |

- **The choice experiment** (Van Loo, Caputo & Lusk 2020) reports no elasticity. Simulated from its fitted model it is about −1.5 at
  equal price (−1.1 to −1.65 across its four arms). The range "−0.84 to −3.4" the model was checked against until 2026-11-18 is a
  formula applied to two of the paper's coefficients, not its aggregate response (`demand_heterogeneity_evidence.md` §1). The
  model gives -1.51 (-1.38 before the price-insensitive shoppers of 2026-11-22, section 7). **Passes**, inside the arms' range. The -1.53 of the normal spread was a numerical error (fifteen
  integration points); integrated properly that spread gave -1.34.
- **Sixteen premium real meats** hold about 1.5% of their category at three times the ordinary price. The model gives 1.3% (3.4%
  against 3.7% at twice the price, 0.76% against 0.63% at four times). **Passes**, well inside the fit's own typical miss (a factor
  of 2.4, `premium_curve.md`). Before the price-insensitive shoppers it gave 0.9% and 0.34%; the normal spread 0.8% and 0.1%; every
  shopper alike, 0.09%.
- **Farmed salmon** (`market_size_loop.md` §6): while it was still a premium product each 1% off its price brought 1.0–1.5% more volume
  along the demand curve. **Still fails, by less since 2026-11-22.** The check takes the premium products still dearer than
  their meat at the low-lactate example's cost (a price ratio above 1.5). Since 2026-11-20 they are four: organic chicken
  (4.69×), heritage pork (3.81×), premium fish fillets and shrimp (3.05×) and sushi-grade seafood (1.74×, which was near equal
  price and left out before). Between the low-lactate example's own cost ($48.68 a kilo of cells) and its cost once a
  food-grade membrane exists ($23.52 since 2026-11-22: more is sold, so the market-size loop reaches the membrane sooner; $24.05
  before) their shares rise by 1.5–4.0% for each 1% off the price: organic chicken 1.52, at the top
  of salmon's range, heritage pork 1.84, premium fillets and shrimp 2.36 and sushi-grade seafood 4.00 (3.7–4.2 before the
  price-insensitive shoppers of 2026-11-22). The dearer the product, the more of its buyers are price-insensitive and the flatter
  its response. Prime beef (1.35×) is the one product near equal price and is left out; it gives 4.3. The model before 2026-11-18
  gave 3.0–3.4 on 2026-11-18, at that day's costs; that value is recorded, not recomputed.
  - The history of this row. Until the audit batch the tier rule made buyers of cuts and premium products less sensitive to
    price, and organic chicken and heritage pork gave 1.3–1.5: a pass. The audit removed that rule because it raised cultivated
    meat's share wherever it was the dearer product (`audit_2026-11-19.md`, D3). With the normal spread alone the three products
    gave 5.2–7.5. The Student's t spread, with more buyers left at a high price, gave 3.6–3.7 at the cells' cost of 2026-11-19
    ($32.80 falling to $17.50). At the dearer cells of 2026-11-20 it gave 3.7–4.3 (3.7–4.2 in the fourth batch of 2026-11-21):
    every product started further from its meat's price, where the model's own elasticity was larger. Since 2026-11-22 the
    price-insensitive shoppers (section 7) give 1.5–4.0.
  - How to read it. Salmon was measured as a product that already held a visible part of its market at a modest premium.
    The model's premium products sit at 1.7–4.7 times the price. Far above meat's price their buyers are now mostly the
    price-insensitive shoppers, who respond to a falling price about as salmon's buyers did; nearer meat's price they are mostly
    ordinary shoppers, who respond more steeply. From three times the price to twice the model's share rises 2.5% per 1% off the
    price (3.1% before) and the curve fitted to the sixteen premium meats 2.2%. A falling price still probably unlocks a little
    less than the model says near twice meat's price. That bears on `market_size_loop.md`, whose gain from cheaper cells rests on
    this response.
- **Plant-based meat**: the measured −1.23 is an item-level figure for plant-based beef (GFI/NielsenIQ 2024); the category is about
  −1.3 to −1.5 (80% range −0.6 to −2.5). The model's is -1.03 at plant-based meat's 0.4% of meat by volume (-1.30 before the
  price-insensitive shoppers of 2026-11-22, who respond less to its price too). **Passes since 2026-11-21** (fourth batch), inside
  the category's range and 0.20 from the item-level figure. Without the committed buyers of section 5 it is -2.89, as it was.

The model's own elasticity for cultivated meat is now -1.31 at equal price, -2.5 at twice meat's price, -2.2 at three times and
-1.4 at four times: it steepens and then flattens, as the buyers left become mostly price-insensitive shoppers (before 2026-11-22:
-1.35, -2.7, -3.4 and -3.6, levelling off as a heavy tail does). With the normal spread it was -0.96, -3.1 and -5.9; with every
shopper alike it kept steepening with the price (−10.4 at three times).

## 2. The price responses compared

| price response | share of a meat at 1×, 1.25×, 1.5×, 2×, 3×, 4× its price | at first contact and equal price | world share, 4. Plus perfusion (the low-lactate example) | world share, 7. Plus everything else at its favourable end (the all-favourable example) |
|---|---|---|---|---|
| **the model: shoppers differ in how much they like cultivated meat (13% at equal price once familiar)** | 13.0%, 9.3%, 6.6%, 3.4%, 1.3%, 0.8% | -1.51 | 0.3% | 5.5% |
| the model before 2026-11-18: every shopper alike, 8.5 times as price-sensitive as meat in general | 51.6%, 31.3%, 16.1%, 3.2%, 0.1%, 0.003% | -3.27 | under 0.001% | 12.2% |
| every shopper alike, 4 times (no extra sensitivity for cultivated meat) | 51.6%, 41.7%, 32.3%, 17.5%, 3.9%, 0.8% | -1.54 | 0.02% | 17.1% |
| every shopper alike, with the slope of the sixteen premium meats (2.2 times) | 51.6%, 46.1%, 40.7%, 30.7%, 15.3%, 6.9% | -0.84 | 0.3% | 23.8% |
| one curve fitted to the sixteen premium meats (slope and level), with cultivated meat's corrections | 6.8%, 5.5%, 4.4%, 2.9%, 1.2%, 0.5% | -0.90 | 0.01% | 2.3% |
| the model of 2026-11-18: a normal spread of 5 utils (fifteen integration points) | 13.0%, 10.2%, 7.8%, 3.8%, 0.8%, 0.1% | -1.54 | 0.006% | 5.9% |

- The first row is the model. The second is the model before: too few buyers above twice the price.
- The third and fourth weaken the slope for every shopper and keep half the market at equal price. They are too generous: at twice
  meat's price they give 16–28%, where premium real meats take about 3.7%.
- The fifth takes slope and level from premium labels: too little near parity, because labels are never cheaper than the ordinary
  product.
- The last is the model as it stood on 2026-11-18 and through the audit batch, a normal spread of 5 utils, with no
  price-insensitive shoppers. Against it the model gives the low-lactate example about forty times the share (0.26% against
  0.006%) and the all-favourable example's cells about the same (5.5% against 5.9%).
- The rows with every shopper alike and the normal spread of 2026-11-18 are calibrated without the price-insensitive shoppers, as
  those models were.
- **Across one-kind responses the low-lactate example's share runs from under 0.001% to 0.3%.** The model's 0.26%, and 5.5% for
  the all-favourable example's cells, are its own reading; the share at equal price (`liking_spread.md`) and the price-insensitive
  shoppers' liking (section 7) carry most of what remains uncertain. The all-favourable example's column is its cells ($6.97 a
  kilo) with the model's ordinary demand, not its own 55% at equal price.
- **A weaker price response with every shopper alike gives the low-lactate example less than the model.** With every shopper four
  times as price-sensitive as for meat in general (the third row) it takes 0.02%, against the model's 0.26%. At $48.68 a kilo of
  cells most products are 4 to 14 times their meat's price, where the model's price-insensitive shoppers leave more buyers than
  shoppers who are all alike. Only the slope of the premium meats (2.2 times, the fourth row) gives about as much (0.3%). For the
  all-favourable example's cells, nearer equal price, both weaker responses give far more than the model (17.1% and 23.8% against
  5.5%), and the model before 2026-11-18 gives 12.2%, about twice the model.

## 3. Two smaller things from the same reading

- **A plant-based competitor at meat's price changes little here**: about 1% of cultivated meat's share, because the model's shoppers
  do not treat plant-based meat as real meat.
- **A plant that sells less than it was built for costs more per kilo** (`market_size_loop.underused`): the plant's charge and its
  labour are paid whatever it makes.

| share of the plant's capacity that is sold | Cautious | 4. Plus perfusion (the low-lactate example) | 7. Plus everything else at its favourable end (the all-favourable example) |
|---|---|---|---|
| 100% | $181.13 | $48.68 | $6.97 |
| 80% | $187.45 | $52.18 | $7.67 |
| 60% | $197.98 | $58.01 | $8.83 |
| 40% | $219.05 | $69.68 | $11.15 |

  Every scenario is at 100%. Beyond Meat's sales fell about 40% from their peak after its plants were built, and its costs run about 70%
  above a right-sized plant's (Knowles 2026). The market-size loop runs backwards as well as forwards.

## 4. What is left

- The response to a falling price at one and a half to three times meat's price: the salmon check still fails there (2.4–4.0
  for the three products nearest their meat's price), and no measurement at that premium exists for cultivated meat.
- Shares above five times a meat's price: now carried by the price-insensitive shoppers, and resting on how much they like
  cultivated meat, which two stated-choice studies measure (section 7; `liking_spread.md` §6).
- What the checks say about the model's response to price above parity: since 2026-11-22 the model is within a factor of 1.3 of
  premium real meats at two to four times the price (0.92, 0.82 and 1.21 of their share) and inside the choice experiment's range;
  the salmon check fails by a factor of 1.0 to 2.7 (2.5 to 2.9 before), and the far tail is not measured.

## 5. Plant-based meat's committed buyers (2026-11-21, fourth batch)

**Why a spread of liking alone could not fix it.** In a logit a shopper's own-price elasticity is the price coefficient times the
price times one minus that shopper's share of their choices. A spread of liking lowers the total elasticity only by giving some
shoppers a share near one. The data put plant-based meat's heavy buyers far from that: 7% of households buy 82% of it
(GFI/NielsenIQ 2022), so at 0.4% of meat by volume they give it about 4.7% of their meat. One minus 4.7% changes the elasticity by
5%. The same fact, read the other way: these buyers must respond less to its price per dollar, and that is what was measured
(Tonsor, Lusk & Schroeder 2021: −0.9 to −1.6 for Beyond Beef among people who do not regularly eat meat, −3.6 to −8.6 among regular
meat eaters; `demand_heterogeneity_evidence.md` section 4).

**What the model does.** A class of the mainstream segment, `pb_committed_share` = 7% of all shoppers, the committed buyers of
plant-based meat (`market_share` segment "K"). They are mainstream shoppers in every weight but two:

- they like plant-based meat more, by `pb_committed_liking` utils, solved so they buy `pb_committed_volume` = 82% of the
  mainstream's plant-based meat (75% in Circana's 2024 panel, range 75-90%);
- their response to plant-based meat's price, measured from conventional meat's, is `pb_committed_price_x` = 0.25 times other
  shoppers' (range 0.10-0.50), on both price channels, as closeness (`cult_sub_mult`) scales cultivated meat's.

The calibration keeps every target it had: plant-based meat 0.4% of meat by volume, 89% of it bought by the mainstream, 6% of
mainstream choices to whole foods. It solves one more unknown (the committed buyers' liking) to one more measured share (82%). The
price response is an input with a source, not fitted to the elasticity: the elasticity remains a check.

**Why only plant-based meat's price.** The evidence measures these buyers' response to plant-based meat's price. In the two
studies that split shoppers by price sensitivity, the price-insensitive buy organic and local meat and are the most hostile to
cultivated meat (`demand_heterogeneity_evidence.md` section 2). Giving the committed buyers of plant-based meat a low response to
every price would hand cultivated meat a block of price-insensitive buyers the evidence does not show. Section 6 tries it.

| plant-based meat's committed buyers | its own-price elasticity | its share of all choices | ordinary shoppers' real-meat weight, utils | committed buyers' liking for it, utils | cultivated meat's share of meat buyers at 3 times the price |
|---|---|---|---|---|---|
| the model | -1.03 | 0.40% | 5.28 | 3.27 | 1.42% |
| no committed buyers (the model before 2026-11-21's fourth batch) | -2.89 | 0.40% | 3.40 | — | 1.06% |
| their response to its price 0.10 times other shoppers' | -0.76 | 0.40% | 5.28 | 3.10 | 1.42% |
| 0.50 times | -1.47 | 0.40% | 5.28 | 3.56 | 1.42% |
| 2% of shoppers | -0.99 | 0.40% | 5.34 | 4.70 | 1.42% |
| 10% of shoppers | -1.04 | 0.40% | 5.25 | 2.87 | 1.42% |
| they buy 75% of the mainstream's plant-based meat | -1.14 | 0.40% | 4.94 | 2.85 | 1.42% |
| 90% | -0.91 | 0.40% | 5.90 | 3.96 | 1.41% |

- **The check passes across the inputs' ranges**: -0.76 to -1.47 since the price-insensitive shoppers of 2026-11-22 (-0.99 to
  -1.81 before), inside the category's 80% range (−0.6 to −2.5). The price response moves it most; the class's size hardly at all
  (with fewer committed buyers their liking is solved higher).
- **Cultivated meat barely moves with them** at a given price (1.42% of meat buyers at three times the price at every end but the
  last, 1.41%), but **its cuts do**: the ordinary shoppers buy plant-based meat far less than the mainstream did on average, so
  their solved real-meat weight is higher (5.28 utils since 2026-11-22, 5.11 in the fourth batch, 3.40 before it). A cut that is
  20% plant protein loses 20% of that weight (`meat_market.tier_offset`): 1.06 utils (0.68 before the committed buyers). In the
  fourth batch that took the all-favourable example's cells with the ordinary demand from 6.1% to 5.6% of world meat, and with its
  own demand from 24.7% to 23.4%. It is the existing rule applied to a better-measured weight; whether a blend should lose the
  ordinary shopper's full dislike of plant-based meat in proportion is itself unmeasured (TODO, cut cell share). The "no committed
  buyers" row is the model before the fourth batch in full (no price-insensitive shoppers, the spread of 3.9 and 4).

## 6. Farmed salmon with the same machinery (2026-11-21, fourth batch; superseded by section 7)

> Kept as the record of 2026-11-21. Since 2026-11-22 (fifth batch) a class like this is in the model, fitted within the
> evidence, with its liking read from two studies (section 7). The table below was built on the model of 2026-11-21 (spread 3.9,
> tail 4, calibrated without the class), with a wrapper; its numbers are not those of the model now.

The committed buyers above respond less to one price. Farmed salmon's history asks whether a premium product's buyers respond
less to its price across the board. The test: a class of shoppers, a share of the market, whose response to every price is a
multiple of other shoppers', and whose liking for cultivated meat is shifted by a set number of utils (negative: more hostile, as
section 5's evidence says), with the spread of liking refitted (Student's t, tail 4) and the mean liking solved so the long-run
share at equal price stays 13%. Each row is scored by the spread's own joint misfit (`liking_spread.objective`). A dated
exploratory calculation (a wrapper around `market_share.share`, mixing the two classes), not a module; the model's own row,
for comparison: spread 3.9, misfit 4.20 (0.54, 1.79, 1.87), salmon 3.68-4.19, the low-lactate example 0.045%.

| price-insensitive shoppers | their price response | their liking for cultivated meat, utils | spread of liking, utils | joint misfit (experiment, premium, salmon) | meets both requirements | first contact: elasticity | salmon response | share at 3x, 4x | low-lactate example, world |
|---|---|---|---|---|---|---|---|---|---|
| 12% | 0.17 | +0 | 2.5 | 3.46 (2.21, 0.54, 0.71) | no | -1.78 | 1.99–4.02 | 1.12%, 0.67% | 0.132% |
| 12% | 0.17 | +0 | 3.0 | 1.74 (0.87, 0.27, 0.6) | yes | -1.54 | 1.91–3.68 | 1.35%, 0.81% | 0.186% |
| 12% | 0.17 | +0 | 3.5 | 4.24 (3.26, 0.47, 0.51) | yes | -1.36 | 1.87–3.39 | 1.60%, 0.96% | 0.246% |
| 12% | 0.17 | +0 | 3.9 | 7.98 (6.65, 0.89, 0.45) | no | -1.24 | 1.85–3.18 | 1.81%, 1.08% | 0.298% |
| 12% | 0.17 | -2 | 2.5 | 15.37 (9.3, 4.83, 1.25) | no | -1.91 | 2.32–4.90 | 0.60%, 0.29% | 0.060% |
| 12% | 0.17 | -2 | 3.0 | 3.92 (1.13, 1.72, 1.07) | no | -1.65 | 2.28–4.36 | 0.84%, 0.42% | 0.095% |
| 12% | 0.17 | -2 | 3.5 | 1.72 (0.45, 0.37, 0.91) | yes | -1.45 | 2.24–3.92 | 1.12%, 0.56% | 0.138% |
| 12% | 0.17 | -2 | 3.9 | 3.59 (2.72, 0.07, 0.79) | no | -1.32 | 2.21–3.62 | 1.35%, 0.69% | 0.178% |
| 12% | 0.17 | -4 | 2.5 | 27.41 (14.86, 10.78, 1.77) | no | -1.96 | 2.77–5.40 | 0.42%, 0.16% | 0.033% |
| 12% | 0.17 | -4 | 3.0 | 8.91 (2.8, 4.6, 1.51) | no | -1.70 | 2.72–4.75 | 0.64%, 0.26% | 0.056% |
| 12% | 0.17 | -4 | 3.5 | 2.84 (0.02, 1.53, 1.29) | yes | -1.49 | 2.65–4.24 | 0.90%, 0.39% | 0.087% |
| 12% | 0.17 | -4 | 3.9 | 2.88 (1.34, 0.41, 1.13) | yes | -1.35 | 2.59–3.89 | 1.13%, 0.51% | 0.117% |
| 8% | 0.17 | +0 | 2.5 | 7.09 (4.51, 1.64, 0.94) | no | -1.85 | 2.16–4.41 | 0.85%, 0.48% | 0.092% |
| 8% | 0.17 | +0 | 3.0 | 1.81 (0.46, 0.52, 0.83) | yes | -1.60 | 2.12–4.02 | 1.07%, 0.59% | 0.131% |
| 8% | 0.17 | +0 | 3.5 | 2.20 (1.34, 0.14, 0.73) | yes | -1.41 | 2.10–3.69 | 1.31%, 0.72% | 0.175% |
| 8% | 0.17 | +0 | 3.9 | 4.90 (4.03, 0.22, 0.66) | no | -1.29 | 2.09–3.45 | 1.52%, 0.83% | 0.214% |
| 30% | 0.17 | -4 | 2.5 | 14.72 (9.16, 4.45, 1.1) | no | -1.91 | 2.05–4.87 | 0.61%, 0.31% | 0.074% |
| 30% | 0.17 | -4 | 3.0 | 2.94 (0.84, 1.21, 0.88) | yes | -1.64 | 1.99–4.26 | 0.90%, 0.47% | 0.124% |
| 30% | 0.17 | -4 | 3.5 | 1.66 (0.8, 0.17, 0.7) | yes | -1.43 | 1.93–3.77 | 1.23%, 0.67% | 0.188% |
| 30% | 0.17 | -4 | 3.9 | 4.57 (3.77, 0.23, 0.57) | no | -1.29 | 1.89–3.45 | 1.51%, 0.84% | 0.248% |
| 12% | 0.1 | +0 | 2.5 | 3.26 (2.1, 0.72, 0.44) | no | -1.76 | 1.31–3.70 | 1.38%, 0.98% | 0.301% |
| 12% | 0.1 | +0 | 3.0 | 2.98 (1.73, 0.87, 0.38) | yes | -1.53 | 1.31–3.43 | 1.59%, 1.10% | 0.381% |
| 12% | 0.1 | +0 | 3.5 | 6.19 (4.55, 1.32, 0.32) | no | -1.35 | 1.34–3.18 | 1.83%, 1.24% | 0.463% |
| 12% | 0.1 | +0 | 3.9 | 10.21 (8.1, 1.83, 0.28) | no | -1.23 | 1.36–3.01 | 2.03%, 1.35% | 0.529% |
| 20% | 0.1 | +0 | 2.5 | 7.48 (4.71, 2.51, 0.27) | no | -1.61 | 1.16–3.08 | 2.08%, 1.57% | 0.491% |
| 20% | 0.1 | +0 | 3.0 | 10.67 (7.22, 3.23, 0.22) | no | -1.40 | 1.12–2.87 | 2.31%, 1.73% | 0.616% |
| 20% | 0.1 | +0 | 3.5 | 15.90 (11.65, 4.08, 0.17) | no | -1.24 | 1.10–2.68 | 2.55%, 1.89% | 0.744% |
| 20% | 0.1 | +0 | 3.9 | 20.87 (15.9, 4.82, 0.14) | no | -1.13 | 1.10–2.54 | 2.76%, 2.02% | 0.844% |
| 12% | 0.25 | -2 | 2.5 | 19.46 (10.61, 7.18, 1.66) | no | -1.92 | 2.88–5.09 | 0.52%, 0.22% | 0.035% |
| 12% | 0.25 | -2 | 3.0 | 5.71 (1.47, 2.83, 1.41) | no | -1.66 | 2.78–4.51 | 0.76%, 0.33% | 0.058% |
| 12% | 0.25 | -2 | 3.5 | 2.22 (0.25, 0.77, 1.2) | yes | -1.46 | 2.69–4.04 | 1.02%, 0.47% | 0.089% |
| 12% | 0.25 | -2 | 3.9 | 3.45 (2.27, 0.13, 1.05) | no | -1.32 | 2.62–3.73 | 1.26%, 0.59% | 0.118% |

- **No row puts all four premium products inside salmon's 1-1.5.** Among the rows that meet the choice experiment's two
  requirements the response runs from 1.3 to 4.3; the cheapest product gets inside only with a tenth of the price response, and a
  fifth of shoppers at a tenth (1.1-3.1) breaks the first-contact requirement.
- **The joint misfit falls** (to 1.7-3.0 in the rows that meet the requirements, against 4.2), mostly in the premium-meat part: a
  price-insensitive class holds more buyers at three and four times the price. So a class like this is consistent with the data
  the spread is fitted to, and better than the model by that measure.
- **It is not in the model**, for two reasons. It is not needed to pass a check (salmon fails with it too). And its one free part,
  how much the price-insensitive like cultivated meat, is not measured: no study reports the correlation between price
  sensitivity and liking for cultivated meat (`demand_heterogeneity_evidence.md` section 2). The answer moves with it: the
  low-lactate example's share of world meat is 1.9 to 8.5 times the model's in the rows that meet the requirements (0.09-0.38%
  against 0.045%), most when the class is not hostile.
- **Why salmon fails, as far as the model can say.** Farmed salmon had buyers who liked it and paid little attention to its
  price. For cultivated meat the shoppers who pay little attention to price are, on the evidence, the ones who like it least.
  Cultivated meat's buyers far above meat's price are the keenest few of an ordinary-price-sensitive population, whose share
  falls by the model's elasticity (-3.4 at three times the price). The check fails because the two products have different
  buyers, not because the model's integration or fit is wrong; whether that is so can only be measured once cultivated meat sells.

## 7. The price-insensitive shoppers, in the model (2026-11-22, fifth batch)

Section 6 tried a class of price-insensitive shoppers on top of the model and left it out. It is now in the model, with its size
and price response fitted within what the evidence on price sensitivity allows, and its liking for cultivated meat read from the
two studies that measured it.

**What the model does** (`market_share.share`, `_rate`, `share_x_meat_many`; the page's `segShares`, `_rate`). A share
`price_insensitive_share` of every segment's shoppers (the ethical segment, the mainstream's ordinary shoppers and plant-based
meat's committed buyers alike) responds `price_insensitive_response` times as strongly as other shoppers to every price, on both
price channels and for every product: their price sensitivity is an elasticity override, as a per-tier one is. Their liking for
cultivated meat is the other shoppers' plus `price_insensitive_liking` utils, with the same spread around it. Nothing else about
them differs. They are in the calibration (plant-based meat's 0.4% of meat, the 89% bought by the mainstream, the committed
buyers' 82%, the meatless rate) and in every share with a spread of liking; with `liking_sd` = 0 (every shopper alike, the
comparisons with the model before 2026-11-18) they are not. The price coefficient is still derived for the other shoppers
(`_derive_beta`, with every shopper alike). The mean liking is solved with them in, so the long-run share at equal price is still
`equal_price_share` (13%) and, in the all-favourable example, `best_equal_price_share` (55%).

**Their liking for cultivated meat: the evidence, read in utils.** The two latent-class studies that split shoppers by price
sensitivity (`demand_heterogeneity_evidence.md` section 2) both call the price-insensitive group the most hostile to cultured meat.
That is a statement in money. In utils, the scale on which the model's shift is set, neither finds them more hostile:

| study | price-insensitive group | its price coefficient against the others' (weighted mean) | its utility for cultured over conventional meat | the others' (weighted mean) | in money |
|---|---|---|---|---|---|
| Washio et al. 2023, Japan, 4,421 shoppers, beef mince (FT, table A2) | "generous customers", 31.9% | -0.0002 against -0.0055 (0.036 times) | -1.90 | -1.95 | -9,010 yen per 100 g, against +185 to -971 for the other groups |
| Carzedda & Troiano 2021, Italy, 1,069 respondents, mostly students, burgers (FT, table 1) | "Italian organic supporters", 35% | -0.039 against -0.103 (0.38 times) | -0.54 | -2.49 | against plant-based meat -€11 a kg, the most hostile (the others -€7 to +€10); against conventional meat -€14, against -€46, -€36 and -€5 |

- The money figure is a utility gap divided by a price coefficient: a small coefficient turns the same dislike into a large sum.
  So in the model a shift of 0 utils already makes the price-insensitive the most hostile in money: at 0.11 times the price
  response the same dislike is nine times as many dollars. That is the mode, `price_insensitive_liking` = 0.
- Hostile in utils too is possible. Measured against plant-based meat rather than conventional meat, Carzedda's group dislikes
  cultured meat a little more than the others (-0.43 against +0.14); and if part of a latent class's small price coefficient is a
  small scale (in Carzedda all of its coefficients are small), its utils understate its dislike. The low end, -2 utils.
- Kinder in utils is also possible: Carzedda's +1.95 against conventional meat. The high end, +2 utils.
- Searched the other way: no study found shows price-insensitive shoppers among cultured meat's enthusiasts. The enthusiast groups
  (Washio's "novelty accepters", 12.8%; Carzedda's "cultured meat supporters", 16%) have middling and high price sensitivity
  (-0.0035 and -0.186 against their samples' -0.0055 and -0.10). Richer shoppers are less price-sensitive (Washio), and no
  study found reports how income moves liking for cultured meat within a latent-class fit.

**The size and the price response: fitted within the evidence.** The evidence bounds them (`demand_heterogeneity_evidence.md`
section 3): a price-insensitive group of 8-15% in real purchases (15-35% in stated choices) and 4-10 times between the most and
least price-sensitive groups (0.10-0.25). Within those bounds, with the liking shift at 0 and the spread of liking (its standard
deviation and its tail) re-fitted at each point, the joint fit was searched over a grid. The score is the spread's own joint misfit
(`liking_spread.objective`: the choice experiment's elasticities at four prices, premium real meats at 2, 3 and 4 times the price,
farmed salmon's response) plus plant-based meat's elasticity against -1.3, scaled by the category's 80% range (a misfit of 1 at
about -0.6 or -2.5). Every point kept meets the experiment's two requirements (first contact within -1.5 +/- 0.15, a miss of at
most 0.30).

| price-insensitive shoppers | their price response | best spread, utils | its tail | joint misfit, with plant-based meat's elasticity | first contact: share of all choices, elasticity | plant-based meat's elasticity | salmon response | low-lactate example, world |
|---|---|---|---|---|---|---|---|---|
| **8%** | **0.11** | **3.55** | **7** | **1.07** | 3.81%, -1.51 | -1.03 | 1.52-4.00 | 0.259% |
| 8% | 0.13 | 3.65 | 7 | 1.12 | 3.92%, -1.47 | -1.04 | 1.72-4.01 | 0.217% |
| 8% | 0.17 | 3.40 | 5 | 1.35 | 3.72%, -1.50 | -1.07 | 2.13-3.98 | 0.146% |
| 8% | 0.10 | 3.30 | 5 | 1.27 | 3.60%, -1.53 | -1.03 | 1.49-3.83 | 0.280% |
| 6% | 0.11 | 3.65 | 6 | 1.16 | 3.96%, -1.47 | -1.09 | 1.77-4.06 | 0.212% |
| 10% | 0.15 | 3.55 | 8 | 1.14 | 3.77%, -1.51 | -1.01 | 1.75-4.01 | 0.200% |
| 10% | 0.13 | 3.55 | 8 | 1.16 | 3.77%, -1.51 | -1.00 | 1.56-3.92 | 0.249% |
| 12% | 0.20 | 3.00 | 4 | 1.85 | 3.29%, -1.55 | -1.00 | 2.15-3.77 | 0.142% |
| 15% | 0.25 | 3.00 | 4 | 2.08 | 3.29%, -1.52 | -0.99 | 2.40-3.74 | 0.117% |
| none: the model before 2026-11-22's fifth batch | | 3.9 | 4 | 4.20 | 4.28%, -1.38 | -1.30 | 3.68-4.19 | 0.045% |

(The 12% and 15% rows are from a first, coarser grid at tails of 4; the other rows from finer ones. A dated grid search
of 2026-11-22, run on the module as built; not a module.)

- **The least misfit is at 8% of shoppers responding 0.11 times as strongly to price, with a spread of 3.55 utils and a tail of
  7.** That is the model. 6% fits worse (1.16), so the size is not at a bound the fit wants to cross; the response, nine times
  between the groups, is near the end of the evidence's range where the price-insensitive respond least. The fit is flat: from
  6% to 10% and from 0.10 to 0.15 the misfit stays within about 20% of the least. Over that flat region the low-lactate example's
  share runs from 0.20% to 0.28%.
- **The spread is refitted** (`liking_sd` 3.9 -> 3.55, `liking_tail` 4 -> 7; `liking_spread.md` section 2). The price-insensitive
  shoppers hold buyers far above meat's price, so the spread itself need not: a narrower spread with a lighter tail fits better.
  With the spread as now but no price-insensitive shoppers the misfit is 19.7: the two belong together.

**The checks before and after.**

| check | measured | before (2026-11-21) | now |
|---|---|---|---|
| first contact, equal price: elasticity | about -1.5 | -1.38 | -1.51 |
| share of a meat's buyers at 3 times the price | 1.5% (premium real meats) | 0.9% | 1.3% |
| farmed salmon: response to a falling price | 1-1.5 | 3.7-4.2 | 1.5-4.0 (organic chicken 1.52, heritage pork 1.84, premium fillets and shrimp 2.36, sushi-grade seafood 4.00) |
| plant-based meat's own-price elasticity | -1.23 (the category about -1.3) | -1.30 | -1.03 |
| the spread's joint misfit | | 4.20 (0.54, 1.79, 1.87) | 0.87 (0.02, 0.23, 0.63) |
| first contact, equal price: share of all choices | 4% (5% of meat buyers) | 4.3% | 3.8% |

- **Farmed salmon: closer, still failing.** The dearest premium product, organic chicken at 4.7 times its meat's price, is at the
  top of salmon's range (1.52). The nearer a product is to its meat's price, the less of its buyers are price-insensitive and the
  steeper its response: sushi-grade seafood, at 1.7 times, still responds at 4.0. With a tenth of the price response the cheapest
  gets to 1.42; with a sixth of shoppers (15%) at 0.11 the range is 1.23-3.29, but the misfit rises to 4.4. No point on the grid
  puts all four products inside 1-1.5.
- **Plant-based meat: passes, further from the measurement.** The price-insensitive shoppers lower its elasticity from -1.30 to
  -1.03: inside the category's 80% range (-0.6 to -2.5), 0.20 from the item-level -1.23. Their committed buyers' response to its
  price (`pb_committed_price_x`, 0.25) is a measured input and was not refitted; at 0.50 the elasticity would be -1.47.
- The other two checks and the misfit improve. The first-contact share falls a little further below the measured (3.8% of all
  choices against 4%).

**How the answer moves.** Long-run share of world meat by weight:

| | before (2026-11-21) | now |
|---|---|---|
| the low-lactate example, at its own cost of cells | 0.045% | 0.26% |
| the low-lactate example, middle of the draws (8 in 10) | 0.052% (0.009-0.26%) | 0.24% (0.06-1.16%) |
| the all-favourable example with its own demand | 23.4% | 25.1% |
| the all-favourable example with its own demand, middle of the draws (8 in 10) | 17.4% (10.7-26.3%) | 19.2% (12.4-28.0%) |
| the all-favourable example's cells with the ordinary demand | 5.6% | 5.5% |

- **The low-lactate example's share is now the price-insensitive shoppers'.** 97% of its sales go to them: at $48.68 a kilo of
  cells its products are 1.4 to 14 times their meat's price. For a shopper who responds a ninth as strongly, nine times meat's
  price weighs about what twice meat's price weighs for the others. Without them, the other shoppers alone, on the refitted spread, would
  buy 0.008% of world meat. In the all-favourable example, near meat's price, 13% of its sales go to them.
- **So the low-lactate example's share now rests on how much the price-insensitive like cultivated meat**, which only two
  stated-choice studies measure. From -2 to +2 utils it runs from 0.11% to 0.58% (the side table below, at the fitted spread). The
  all-favourable example barely moves with it (24.7% to 25.8%).
- **Far above meat's price the tail is longer.** A meat's buyers at 5, 8 and 10 times its price: 0.58%, 0.33% and 0.23% of all
  choices, against 0.15%, 0.03% and 0.01% before. The premium data stop at 3.6 times; above that it is the class's own response,
  not a measurement.

The class at each end of its inputs (the spread held at the model's 3.55 and 7; the mean liking re-solved each time):

| price-insensitive shoppers | joint misfit (experiment, premium, salmon) | meets the experiment's two requirements | first contact: elasticity | plant-based meat's elasticity | salmon response | share of a meat's buyers at 3x, 4x its price | low-lactate example, world | all-favourable example with its own demand, world |
|---|---|---|---|---|---|---|---|---|
| the model | 0.87 (0.02, 0.23, 0.63) | yes | -1.51 | -1.03 | 1.52–4.00 | 1.26%, 0.76% | 0.259% | 25.1% |
| no price-insensitive shoppers, the spread as it was (the model before 2026-11-22's fifth batch) | 4.20 (0.54, 1.79, 1.87) | yes | -1.38 | -1.30 | 3.68–4.19 | 0.93%, 0.34% | 0.045% | 23.4% |
| no price-insensitive shoppers, the spread as now | 19.71 (4.80, 11.04, 3.87) | no | -1.63 | -1.30 | 5.64–5.97 | 0.53%, 0.12% | 0.009% | 23.5% |
| they like cultivated meat 2 utils less than other shoppers | 4.38 (1.45, 1.68, 1.25) | yes | -1.57 | -1.03 | 2.14–4.76 | 0.85%, 0.39% | 0.112% | 24.7% |
| 2 utils more | 6.69 (4.29, 2.13, 0.27) | no | -1.37 | -1.03 | 1.12–3.09 | 2.01%, 1.46% | 0.575% | 25.8% |
| 10% of shoppers | 1.19 (0.27, 0.41, 0.51) | yes | -1.48 | -0.99 | 1.40–3.76 | 1.44%, 0.92% | 0.320% | 25.5% |
| 15% of shoppers | 4.40 (2.43, 1.63, 0.34) | yes | -1.40 | -0.88 | 1.23–3.29 | 1.90%, 1.32% | 0.472% | 26.6% |
| their price response 0.10 times other shoppers' | 0.87 (0.02, 0.25, 0.59) | yes | -1.51 | -1.03 | 1.42–3.96 | 1.28%, 0.79% | 0.290% | 25.2% |
| 0.25 times | 2.69 (0.30, 0.92, 1.47) | yes | -1.53 | -1.11 | 2.87–4.47 | 0.99%, 0.44% | 0.066% | 24.8% |

- **The liking shift moves the answer most**: -2 utils gives the low-lactate example 0.112%, +2 gives 0.575%. Both fit worse than
  0 (misfits 4.38 and 6.69 at this spread; a hostile class wants a wider spread). The evidence in utils points to 0.
- **The response matters next**: at 0.25 times (four times between groups) the low-lactate example is 0.066% and salmon 2.9-4.5.
- **Without the class, the refitted spread fails** (misfit 19.7, the requirements not met): the model before is the row above it.

## Sources

1. Knowles, "Why is plant-based meat still so expensive?", Net Primary Production, 16 November 2026 (FT).
2. GFI/NielsenIQ plant-based pricing fact sheet, November 2024 (FT); Zhao et al. 2023, AEPP (ABS).
3. Van Loo, Caputo & Lusk 2020, Food Policy (FT).
4. `premium_curve.md` and `market_size_loop.md` for the other two measurements and their sources.
5. GFI/NielsenIQ household panel, 2022 (7% of households, 82% of plant-based meat spending); Circana household panel, 2024 (a fifth
   of buyers, 75%); Tonsor, Lusk & Schroeder 2021 (elasticities by meat-eating habit); all as read for
   `demand_heterogeneity_evidence.md` section 4.
