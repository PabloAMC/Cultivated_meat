# Is the model's response to price as strong as measured ones?

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50; cut cost rebuilt (0.8 cells + $2 matrix + $2 assembly beyond mince), cuts cheaper.

Date: 2026-11-18; revised the same day when the model gained a spread of liking across shoppers (`liking_spread.md`). Code:
`demand_checks.py`; test: `tests/test_demand_checks.py`.

Access levels: **FT** full text read; **ABS** abstract only; **SNIP** search snippet.

**Why.** How fast cultivated meat's share falls as its price rises above meat's decides the share in every scenario but the best case:
Central's shop price is 0.8 to 8 times the meat it sits beside.

## 1. The four checks

| what was measured | measured | the model | the model before 2026-11-18 |
|---|---|---|---|
| Cultivated meat at first contact and equal price: own-price elasticity (choice experiment, simulated from its fitted model) | about -1.5 (-1.1 to -1.65 across its arms) | -1.53 | -3.27 |
| Share of a meat at 3 times the ordinary one's price (sixteen premium real meats, fitted) | 1.5% | 0.8% | 0.09% |
| A premium product getting cheaper: percent more volume per percent lower price (farmed salmon) | 1–1.5 | 5.2–7.5 (organic chicken, heritage pork, seafood (premium fillet, shrimp): the premium products still dearer than their meat) | 3.0–3.4 |
| Plant-based meat's own-price elasticity (US retail; the category is about -1.3) | -1.23 | -2.85 | -2.85 |

- **The choice experiment** (Van Loo, Caputo & Lusk 2020) reports no elasticity. Simulated from its fitted model it is about −1.5 at
  equal price. The range "−0.84 to −3.4" the model was checked against until 2026-11-18 is a formula applied to two of the paper's
  coefficients, not its aggregate response (`demand_heterogeneity_evidence.md` §1). **Passes now.**
- **Sixteen premium real meats** hold about 1.5% of their category at three times the ordinary price. The model gives 0.8%, about
  half. **Low, but inside the fit's own typical miss** (a factor of 2.4, `premium_curve.md`). The model before gave 0.09%.
- **Farmed salmon** (`market_size_loop.md` §6): while it was still a premium product each 1% off its price brought 1.0–1.5% more volume
  along the demand curve. **Passes for the products the measurement applies to**: the premium products still dearer than their meat at
  Central's cost, organic chicken (2.8×) and heritage pork (2.3×), give 1.3–1.5. Until 2026-11-19 the row used prime beef and
  sushi-grade seafood (then 1.0–1.2). Since cuts got cheaper, cultivated prime beef sells at 0.80 times wagyu's price and sushi-grade
  seafood at 1.03 times; they are no longer premium products in salmon's sense, and at or below equal price the response is weaker
  (0.6–0.7). `demand_checks.py` now takes the products with a price ratio above 1.5.
- **Plant-based meat**: the measured −1.23 is an item-level figure for plant-based beef (GFI/NielsenIQ 2024); the category is about
  −1.3 to −1.5. The model's is -2.85. **Still fails.** It belongs to the price terms all products share, and the remaining
  buyers are a concentrated minority (7% of households make 82% of spending) whom the model does not represent (TODO).

The model's own elasticity for cultivated meat is now -0.96 at equal price, -3.1 at twice meat's price and -5.9 at three times.
With every shopper alike it kept steepening with the price (−10.4 at three times).

## 2. The price responses compared

| price response | share of a meat at 1×, 1.25×, 1.5×, 2×, 3×, 4× its price | at first contact and equal price | world share, 3. Plus cells selected to grow faster on the low-waste feed (Central) | world share, 5. Plus engineered cells |
|---|---|---|---|---|
| **the model: shoppers differ in how much they like cultivated meat (13% at equal price once familiar)** | 13.0%, 10.3%, 7.8%, 3.8%, 0.8%, 0.1% | -1.53 | 0.08% | 2.8% |
| the model before 2026-11-18: every shopper alike, 8.5 times as price-sensitive as meat in general | 48.8%, 28.8%, 14.6%, 2.9%, 0.09%, 0.003% | -3.27 | 0.03% | 5.4% |
| every shopper alike, 4 times (no extra sensitivity for cultivated meat) | 48.8%, 38.9%, 29.9%, 15.9%, 3.6%, 0.7% | -1.54 | 0.2% | 9.2% |
| every shopper alike, with the slope of the sixteen premium meats (2.2 times) | 48.8%, 43.2%, 37.9%, 28.1%, 13.7%, 6.1% | -0.85 | 1.5% | 16.6% |
| one curve fitted to the sixteen premium meats (slope and level), with cultivated meat's corrections | 6.8%, 5.5%, 4.4%, 2.9%, 1.2%, 0.5% | -0.90 | 0.1% | 1.4% |

- The first row is the model. The second is the model before: too few buyers above twice the price.
- The third and fourth weaken the slope for every shopper and keep half the market at equal price. They are too generous: at twice
  meat's price they give 16–28%, where premium real meats take 3–4%.
- The last takes slope and level from premium labels: too little near parity, because labels are never cheaper than the ordinary
  product.
- **Across one-kind responses Central's share runs from 0.2% to 6.0%.** The model's 0.5% and 5.0% are its own reading; the share at equal
  price (`liking_spread.md`) carries most of what remains uncertain.

## 3. Two smaller things from the same reading

- **A plant-based competitor at meat's price changes little here**: under 3% of cultivated meat's share, because the model's shoppers
  do not treat plant-based meat as real meat.
- **A plant that sells less than it was built for costs more per kilo** (`market_size_loop.underused`): the plant's charge and its
  labour are paid whatever it makes.

| share of the plant's capacity that is sold | 1. Today | 3. Plus cells selected to grow faster on the low-waste feed (Central) | 5. Plus engineered cells |
|---|---|---|---|
| 100% | $56.99 | $26.43 | $9.96 |
| 80% | $67.61 | $28.67 | $10.64 |
| 60% | $85.32 | $32.40 | $11.78 |
| 40% | $120.73 | $39.86 | $14.06 |

  Every scenario is at 100%. Beyond Meat's sales fell about 40% from their peak after its plants were built, and its costs run about 70%
  above a right-sized plant's (Knowles 2026). The market-size loop runs backwards as well as forwards.

## 4. What is left

- Plant-based meat's elasticity, with its concentrated buyers (TODO).
- Judgement: that the model's response to price for cultivated meat is within a factor of two of the truth above parity: about 0.65.

## Sources

1. Knowles, "Why is plant-based meat still so expensive?", Net Primary Production, 16 November 2026 (FT).
2. GFI/NielsenIQ plant-based pricing fact sheet, November 2024 (FT); Zhao et al. 2023, AEPP (ABS).
3. Van Loo, Caputo & Lusk 2020, Food Policy (FT).
4. `premium_curve.md` and `market_size_loop.md` for the other two measurements and their sources.
