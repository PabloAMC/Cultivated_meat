# Is the model's response to price as strong as measured ones?

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50; cut cost rebuilt (0.8 cells + $2 matrix + $2 assembly beyond mince), cuts cheaper.

> Repinned 2026-11-19 (audit batch): cells dearer (ammonia tolerance 4 mM), seafood re-priced by consumption, the tier rule replaced by a blend penalty, the equal-price share drawn around its 13% setting; see audit_2026-11-19.md.

Date: 2026-11-18; revised the same day when the model gained a spread of liking across shoppers (`liking_spread.md`). Code:
`demand_checks.py`; test: `tests/test_demand_checks.py`.

Access levels: **FT** full text read; **ABS** abstract only; **SNIP** search snippet.

**Why.** How fast cultivated meat's share falls as its price rises above meat's decides the share in every scenario but the best case:
Central's shop price is 1 to 10 times the meat it sits beside (0.96 times prime beef, 9.8 times processed chicken).

**In short (2026-11-19, after the audit batch).** Two of the four checks pass and two fail. The model matches the one choice
experiment at equal price, and is low but within the fit's miss against premium real meats at three times the price. It now
fails the check against farmed salmon: its premium products respond to a falling price more than three times as strongly as the top of
salmon's range. And it still fails on plant-based meat's elasticity. The salmon check passed before largely because the tier rule made buyers
of premium products less sensitive to price, and the audit removed that rule because it worked backwards (finding D3).

## 1. The four checks

| what was measured | measured | the model | the model before 2026-11-18 |
|---|---|---|---|
| Cultivated meat at first contact and equal price: own-price elasticity (choice experiment, simulated from its fitted model) | about -1.5 (-1.1 to -1.65 across its arms) | -1.53 | -3.27 |
| Share of a meat at 3 times the ordinary one's price (sixteen premium real meats, fitted) | 1.5% | 0.8% | 0.09% |
| A premium product getting cheaper: percent more volume per percent lower price (farmed salmon) | 1–1.5 | 5.2–7.5 (organic chicken, heritage pork, premium fish fillets and shrimp: the premium products still dearer than their meat) | 3.0–3.4 |
| Plant-based meat's own-price elasticity (US retail; the category is about -1.3) | -1.23 | -2.85 | -2.85 |

- **The choice experiment** (Van Loo, Caputo & Lusk 2020) reports no elasticity. Simulated from its fitted model it is about −1.5 at
  equal price. The range "−0.84 to −3.4" the model was checked against until 2026-11-18 is a formula applied to two of the paper's
  coefficients, not its aggregate response (`demand_heterogeneity_evidence.md` §1). **Passes now.**
- **Sixteen premium real meats** hold about 1.5% of their category at three times the ordinary price. The model gives 0.8%, about
  half. **Low, but inside the fit's own typical miss** (a factor of 2.4, `premium_curve.md`). The model before gave 0.09%.
- **Farmed salmon** (`market_size_loop.md` §6): while it was still a premium product each 1% off its price brought 1.0–1.5% more volume
  along the demand curve. **Fails now.** The check takes the premium products still dearer than their meat at Central's cost (a price
  ratio above 1.5): organic chicken (3.3×), heritage pork (2.7×) and premium fish fillets and shrimp (2.2×, a row new since seafood
  was re-priced). Between Central's own cost ($32.80 a kilo of cells) and its cost once a food-grade membrane exists ($17.75) their
  shares rise by 5.2–7.5% for each 1% off the price, more than three times the top of salmon's range. Prime beef (0.96×) and sushi-grade
  seafood (1.24×) are near equal price and are left out; they give 2.6 and 3.3, also above salmon's range.
  - Why it changed. Until the audit batch the tier rule made buyers of cuts and premium products less sensitive to price, and
    organic chicken and heritage pork gave 1.3–1.5 (at 2.8 and 2.3 times their price; dearer cells have also moved them further out). The audit found that rule raised cultivated meat's share wherever it was the dearer product, and
    removed it (`audit_2026-11-19.md`, D3). What is left is the model's own curve: an elasticity of -3.1 at twice meat's
    price and -5.9 at three times.
  - How to read it. Salmon was measured as a product that already held a visible part of its market at a modest premium.
    The model's premium products sit at 2–3 times the price, where under 0.4% of buyers choose them, far out in the spread of liking.
    The response there is steeper than premium real meats show across products as well: from three times the price to twice, the
    model's share rises 3.8% per 1% off the price and the curve fitted to the sixteen premium meats 2.2%. So either the model's
    shares at 2–3 times the price are too low (the premium meats suggest by about half), or a falling price unlocks less than
    the model says. The second reading bears on `market_size_loop.md`, whose gain from cheaper cells rests on this response.
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
  meat's price they give 16–28%, where premium real meats take about 3.7%.
- The last takes slope and level from premium labels: too little near parity, because labels are never cheaper than the ordinary
  product.
- **Across one-kind responses Central's share runs from 0.03% to 1.5%**, a fifty-fold range. The model's 0.08%, and 2.8% for the best
  case's cells, are its own reading; the share at equal price (`liking_spread.md`) carries most of what remains uncertain. The best
  case's column is its cells ($11.46 a kilo) with the model's ordinary demand, not its own 55% at equal price.

## 3. Two smaller things from the same reading

- **A plant-based competitor at meat's price changes little here**: under 2% of cultivated meat's share, because the model's shoppers
  do not treat plant-based meat as real meat.
- **A plant that sells less than it was built for costs more per kilo** (`market_size_loop.underused`): the plant's charge and its
  labour are paid whatever it makes.

| share of the plant's capacity that is sold | 1. Published cells | 3. Plus cells selected to grow faster on the low-waste feed (Central) | 5. Plus engineered cells |
|---|---|---|---|
| 100% | $111.89 | $32.80 | $11.46 |
| 80% | $122.68 | $35.06 | $12.14 |
| 60% | $140.65 | $38.81 | $13.29 |
| 40% | $176.59 | $46.33 | $15.58 |

  Every scenario is at 100%. Beyond Meat's sales fell about 40% from their peak after its plants were built, and its costs run about 70%
  above a right-sized plant's (Knowles 2026). The market-size loop runs backwards as well as forwards.

## 4. What is left

- Plant-based meat's elasticity, with its concentrated buyers (TODO).
- The response to a falling price at two to three times meat's price: the salmon check fails, and no measurement at that premium
  exists for cultivated meat.
- Judgement: that the model's response to price for cultivated meat is within a factor of two of the truth above parity: about 0.5
  (provisional; lowered from 0.65 at the 2026-11-19 audit batch, because the salmon check no longer passes and the model's slope at
  2–3 times the price is nearly twice the premium meats').

## Sources

1. Knowles, "Why is plant-based meat still so expensive?", Net Primary Production, 16 November 2026 (FT).
2. GFI/NielsenIQ plant-based pricing fact sheet, November 2024 (FT); Zhao et al. 2023, AEPP (ABS).
3. Van Loo, Caputo & Lusk 2020, Food Policy (FT).
4. `premium_curve.md` and `market_size_loop.md` for the other two measurements and their sources.
