# Is the model's response to price as strong as measured ones?

> Names (2026-11-19): the two examples are named by what they assume (the low-lactate example, the all-favourable example). Cells are described by their traits, never as a named kind of cell.

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50; cut cost rebuilt (0.8 cells + $2 matrix + $2 assembly beyond mince), cuts cheaper.

> Repinned 2026-11-19 (audit batch): cells dearer (ammonia tolerance 4 mM), seafood re-priced by consumption, the tier rule replaced by a blend penalty, the equal-price share drawn around its 13% setting; see audit_2026-11-19.md.

> Repinned 2026-11-19 (second round): shoppers' liking is a Student's t spread (standard deviation 3.9 utils, 4 degrees of freedom) on a 67-point grid, not a normal spread of 5 on fifteen points; see liking_spread.md.

> Repinned 2026-11-20 (engine batch): the scenarios' cells tolerate 35 mmol/L of lactate, bubble deaths and a harvest loss are charged, a washed tank takes twice the fed-batch crew, the membrane lasts 2,415 L/m2, and growth factors, utilities and the crew follow the Humbird back-test, so cells are dearer (the low-lactate example $32.80 to $49.96 a kilo, the all-favourable example $11.67 to $18.71, Published cells in fed-batch $209 to $323) and every share here fell; the demand model did not change; see full_review_2026-11-19.md and humbird_backtest.md.

> Repinned 2026-11-20 (final pass): the all-favourable example is now `scenarios.all_favourable()` ($18.71 to $7.62 a kilo of cells), the low-lactate example costs $49.50; plant-based meat is anchored at 0.4% of meat by volume (was 1.2% of choices), incomes are nominal, conventional meat's price falls as cultivated meat takes sales, and the share of the world market closed by law is weighted by meat eaten (closed_markets.md). The salmon row's last column is a value recorded on 2026-11-18, not recomputed.

Date: 2026-11-18; revised the same day when the model gained a spread of liking across shoppers (`liking_spread.md`). Code:
`demand_checks.py`; test: `tests/test_demand_checks.py`.

Access levels: **FT** full text read; **ABS** abstract only; **SNIP** search snippet.

**Why.** How fast cultivated meat's share falls as its price rises above meat's decides the share in every scenario but the all-favourable example:
the low-lactate example's shop price is 1.4 to 14 times the meat it sits beside (1.37 times prime beef, 14.4 times processed chicken).

**In short (2026-11-20).** Two of the four checks pass and two fail, as before. The two that pass are about the demand curve
alone: the model is inside the choice experiment's range at equal price (-1.37 against about -1.5), and it holds 0.9% of a
meat's buyers at three times the price against premium real meats' 1.5%. The failure against farmed salmon grew when the
2026-11-20 engine batch made cells dearer: the model's premium products respond to a falling price at 3.7–4.3, about two and a
half to three times the top of salmon's range (3.6–3.7 before; 5.2–7.5 with the normal spread). It still fails on plant-based
meat's elasticity, now by more (-2.89 against -1.23), since plant-based meat was re-anchored at 0.4% of meat by volume. The
shape of the spread is fitted to the first three of these (`liking_spread.md` §2), so they are not independent checks of it.

## 1. The four checks

| what was measured | measured | the model | the model before 2026-11-18 |
|---|---|---|---|
| Cultivated meat at first contact and equal price: own-price elasticity (choice experiment, simulated from its fitted model) | about -1.5 (-1.1 to -1.65 across its arms) | -1.37 | -3.27 |
| Share of a meat at 3 times the ordinary one's price (sixteen premium real meats, fitted) | 1.5% | 0.9% | 0.1% |
| A premium product getting cheaper: percent more volume per percent lower price (farmed salmon) | 1–1.5 | 3.7–4.3 (organic chicken, heritage pork, premium fish fillets and shrimp, sushi-grade seafood: the premium products still dearer than their meat) | 3.0–3.4 (recorded on 2026-11-18 at that day's costs; not recomputed) |
| Plant-based meat's own-price elasticity (US retail; the category is about -1.3) | -1.23 | -2.89 | -2.89 |

- **The choice experiment** (Van Loo, Caputo & Lusk 2020) reports no elasticity. Simulated from its fitted model it is about −1.5 at
  equal price (−1.1 to −1.65 across its four arms). The range "−0.84 to −3.4" the model was checked against until 2026-11-18 is a
  formula applied to two of the paper's coefficients, not its aggregate response (`demand_heterogeneity_evidence.md` §1). The
  model gives -1.37. **Passes**, inside the arms' range. The -1.53 of the normal spread was a numerical error (fifteen
  integration points); integrated properly that spread gave -1.34.
- **Sixteen premium real meats** hold about 1.5% of their category at three times the ordinary price. The model gives 0.9%,
  three-fifths of it (3.3% against 3.7% at twice the price, 0.34% against 0.63% at four times). **Passes, on the low side**, well
  inside the fit's own typical miss (a factor of 2.4, `premium_curve.md`). The normal spread gave 0.8% and 0.1%; every shopper
  alike, 0.09%.
- **Farmed salmon** (`market_size_loop.md` §6): while it was still a premium product each 1% off its price brought 1.0–1.5% more volume
  along the demand curve. **Still fails, by more since 2026-11-20.** The check takes the premium products still dearer than
  their meat at the low-lactate example's cost (a price ratio above 1.5). Since 2026-11-20 they are four: organic chicken
  (4.75×), heritage pork (3.86×), premium fish fillets and shrimp (3.09×) and sushi-grade seafood (1.77×, which was near equal
  price and left out before). Between the low-lactate example's own cost ($49.50 a kilo of cells) and its cost once a
  food-grade membrane exists ($24.95) their shares rise by 3.7–4.3% for each 1% off the price, about two and a half to three
  times the top of salmon's range. Prime beef (1.37×) is the one product near equal price and is left out; it gives 4.2. The
  model before 2026-11-18 gave 3.0–3.4 on 2026-11-18, at that day's costs; that value is recorded, not recomputed.
  - The history of this row. Until the audit batch the tier rule made buyers of cuts and premium products less sensitive to
    price, and organic chicken and heritage pork gave 1.3–1.5: a pass. The audit removed that rule because it raised cultivated
    meat's share wherever it was the dearer product (`audit_2026-11-19.md`, D3). With the normal spread alone the three products
    gave 5.2–7.5. The Student's t spread, with more buyers left at a high price, gave 3.6–3.7 at the cells' cost of 2026-11-19
    ($32.80 falling to $17.50). At the dearer cells of 2026-11-20 it gives 3.7–4.3: the demand curve is the same, but every
    product starts further from its meat's price, where the model's own elasticity is larger (-3.4 at three times the price
    and -3.6 at four, against -2.7 at twice).
  - How to read it. Salmon was measured as a product that already held a visible part of its market at a modest premium.
    The model's premium products sit at 1.8–4.75 times the price, where under 0.8% of buyers choose them, far out in the spread of liking.
    The response there is still steeper than premium real meats show across products: from three times the price to twice, the
    model's share rises 3.1% per 1% off the price and the curve fitted to the sixteen premium meats 2.2%. So a falling price
    probably unlocks less than the model says. That bears on `market_size_loop.md`, whose gain from cheaper cells rests on this
    response.
- **Plant-based meat**: the measured −1.23 is an item-level figure for plant-based beef (GFI/NielsenIQ 2024); the category is about
  −1.3 to −1.5. The model's is -2.89 at plant-based meat's 0.4% of meat by volume (it was -2.85 at the old 1.2% anchor).
  **Still fails.** It belongs to the price terms all products share, and the remaining
  buyers are a concentrated minority (7% of households make 82% of spending) whom the model does not represent (TODO).

The model's own elasticity for cultivated meat is now -1.35 at equal price, -2.7 at twice meat's price, -3.4 at three times and
-3.6 at four times: it levels off, as a heavy tail does. With the normal spread it was -0.96, -3.1 and -5.9; with every shopper
alike it kept steepening with the price (−10.4 at three times).

## 2. The price responses compared

| price response | share of a meat at 1×, 1.25×, 1.5×, 2×, 3×, 4× its price | at first contact and equal price | world share, 4. Plus perfusion (the low-lactate example) | world share, 7. Plus everything else at its favourable end (the all-favourable example) |
|---|---|---|---|---|
| **the model: shoppers differ in how much they like cultivated meat (13% at equal price once familiar)** | 13.0%, 9.2%, 6.5%, 3.3%, 0.9%, 0.3% | -1.37 | 0.05% | 5.4% |
| the model before 2026-11-18: every shopper alike, 8.5 times as price-sensitive as meat in general | 49.6%, 29.7%, 15.2%, 3.1%, 0.1%, 0.003% | -3.27 | under 0.001% | 11.4% |
| every shopper alike, 4 times (no extra sensitivity for cultivated meat) | 49.6%, 39.9%, 30.7%, 16.5%, 3.7%, 0.7% | -1.54 | 0.02% | 16.6% |
| every shopper alike, with the slope of the sixteen premium meats (2.2 times) | 49.6%, 44.2%, 38.9%, 29.0%, 14.3%, 6.4% | -0.85 | 0.3% | 23.8% |
| one curve fitted to the sixteen premium meats (slope and level), with cultivated meat's corrections | 6.8%, 5.5%, 4.4%, 2.9%, 1.2%, 0.5% | -0.90 | 0.02% | 2.5% |
| the model of 2026-11-18: a normal spread of 5 utils (fifteen integration points) | 13.0%, 10.2%, 7.8%, 3.8%, 0.8%, 0.1% | -1.53 | 0.006% | 5.7% |

- The first row is the model. The second is the model before: too few buyers above twice the price.
- The third and fourth weaken the slope for every shopper and keep half the market at equal price. They are too generous: at twice
  meat's price they give 16–28%, where premium real meats take about 3.7%.
- The fifth takes slope and level from premium labels: too little near parity, because labels are never cheaper than the ordinary
  product.
- The last is the model as it stood on 2026-11-18 and through the audit batch, a normal spread of 5 utils. Against it the
  Student's t gives the low-lactate example about seven times the share (0.047% against 0.006%) and the all-favourable
  example's cells about the same (5.4% against 5.7%).
- **Across one-kind responses the low-lactate example's share runs from under 0.001% to 0.3%.** The model's 0.05% (0.047%),
  and 5.4% for the all-favourable example's cells, are its own reading; the share at equal price (`liking_spread.md`) carries
  most of what remains uncertain. The all-favourable example's column is its cells ($7.62 a kilo) with the model's ordinary
  demand, not its own 55% at equal price.
- **Since 2026-11-20 a weaker price response with every shopper alike no longer always gives the low-lactate example more than
  the model.** With every shopper four times as price-sensitive as for meat in general (the third row) it takes 0.02%, under
  half the model's 0.05%; before the engine batch that row gave 0.3% against the model's 0.2%. At $49.50 a kilo of cells most
  products are 4 to 14 times their meat's price, where the model's spread of liking leaves more buyers than shoppers who are all
  alike, even less price-sensitive ones. Only the slope of the premium meats (2.2 times, the fourth row) still gives more
  (0.3%). For the all-favourable example's cells, nearer equal price, both weaker responses give far more than the model (16.6%
  and 23.8% against 5.4%), and the model before 2026-11-18 gives 11.4%, about twice the model.

## 3. Two smaller things from the same reading

- **A plant-based competitor at meat's price changes little here**: about 1% of cultivated meat's share, because the model's shoppers
  do not treat plant-based meat as real meat.
- **A plant that sells less than it was built for costs more per kilo** (`market_size_loop.underused`): the plant's charge and its
  labour are paid whatever it makes.

| share of the plant's capacity that is sold | Cautious | 4. Plus perfusion (the low-lactate example) | 7. Plus everything else at its favourable end (the all-favourable example) |
|---|---|---|---|
| 100% | $185.59 | $49.50 | $7.62 |
| 80% | $193.36 | $53.27 | $8.50 |
| 60% | $206.32 | $59.56 | $9.96 |
| 40% | $232.23 | $72.13 | $12.89 |

  Every scenario is at 100%. Beyond Meat's sales fell about 40% from their peak after its plants were built, and its costs run about 70%
  above a right-sized plant's (Knowles 2026). The market-size loop runs backwards as well as forwards.

## 4. What is left

- Plant-based meat's elasticity, with its concentrated buyers (TODO).
- The response to a falling price at two to three times meat's price: the salmon check fails, and no measurement at that premium
  exists for cultivated meat.
- Shares above five times a meat's price: an extrapolation of the tail (`liking_spread.md` §6).
- What the checks say about the model's response to price above parity: the Student's t spread is within a factor of two of
  premium real meats at two to four times the price (nine-tenths of their share at twice, just over half at four times) and
  inside the choice experiment's range; the salmon check fails, by a factor of 2.5 to 2.9 since 2026-11-20 (2.4 before), and
  the far tail is not measured. For the model to be within a factor of two of the truth above parity, the premium real meats
  would have to be the better guide to cultivated meat than salmon's history.

## Sources

1. Knowles, "Why is plant-based meat still so expensive?", Net Primary Production, 16 November 2026 (FT).
2. GFI/NielsenIQ plant-based pricing fact sheet, November 2024 (FT); Zhao et al. 2023, AEPP (ABS).
3. Van Loo, Caputo & Lusk 2020, Food Policy (FT).
4. `premium_curve.md` and `market_size_loop.md` for the other two measurements and their sources.
