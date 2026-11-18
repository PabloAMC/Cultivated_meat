# Is the model's response to price as strong as measured ones?

Date: 2026-11-18; revised the same day after the shopper model gained premium buyers (`demand_recalibration.md`), which this note led
to. Code: `demand_checks.py`; test: `tests/test_demand_checks.py`. The checks themselves change no default.

Access levels: **FT** full text read; **ABS** abstract only; **SNIP** search snippet.

**Why.** How fast cultivated meat's share falls as its price rises above meat's decides the share in every scenario but the best case:
Central's shop price is 1.2 to 9 times the meat it sits beside. The model's price response was set from one choice experiment and six
premium products. Four measurements can be set against it.

## 1. The four checks

| what was measured | measured | the model | the model before 2026-11-18 |
|---|---|---|---|
| Share of a meat at 3 times the ordinary one's price (sixteen premium real meats, fitted) | 1.5% | 1.3% | 0.09% |
| Cultivated meat at first contact and equal price: own-price elasticity (choice experiment) | -0.84 to -3.4 | -3.06 | -3.27 |
| A premium product getting cheaper: percent more volume per percent lower price (farmed salmon) | 1–1.5 | 2.7–3.0 (prime beef, sushi-grade seafood) | 3.0–3.4 |
| Plant-based meat's own-price elasticity (US retail) | -1.23 | -2.85 | -2.85 |

- **Sixteen premium real meats** (`premium_curve.md`) hold about 1.5% of their category at three times the ordinary price. The model
  before had 0.09% there. With premium buyers it has 1.3%. **Passes now.**
- **The choice experiment** (Van Loo, Caputo & Lusk 2020): **inside**, before and now.
- **Farmed salmon** (`market_size_loop.md` §6): while it was still a premium product each 1% off its price brought 1.0–1.5% more volume
  along the demand curve. The model's prime beef and sushi-grade seafood respond with 2.7–3.0%. **Still about twice too strong.**
- **Plant-based meat** is the only novel meat with sales data. Its measured own-price elasticity is -1.23 (GFI's US retail figure,
  as cited by Knowles 2026, FT; the GFI source was not read). The model's, at plant-based meat's own price (1.77 times meat's) and
  share (1.2%), is -2.85. **Still over twice too strong.** It belongs to the price terms all products share; the
  model was calibrated to plant-based meat's share, not to its response to price.

The model's own elasticity for cultivated meat is now -1.63 at equal price, -4.1 at twice meat's price and -2.8 at three times.
Before, it kept steepening with the price (-10.4 at three times), which removed nearly all sales at Central's prices.

## 2. The price responses compared

| price response | share of a meat at 1×, 1.25×, 1.5×, 2×, 3×, 4× its price | at first contact and equal price | world share, 3. Plus cells selected to grow faster on the low-waste feed (Central) | world share, 5. Plus engineered cells |
|---|---|---|---|---|
| **the model: most shoppers as before, and premium buyers (10%) who respond as buyers of premium meats do** | 48.3%, 29.8%, 16.6%, 5.2%, 1.3%, 0.6% | -3.06 | 0.2% | 4.5% |
| the model before 2026-11-18: one kind of shopper, 8.5 times as price-sensitive as meat in general | 48.8%, 28.8%, 14.6%, 2.9%, 0.09%, 0.00% | -3.27 | 0.04% | 3.1% |
| one kind of shopper, 4 times (no extra sensitivity for cultivated meat) | 48.8%, 38.9%, 29.9%, 15.9%, 3.6%, 0.7% | -1.54 | 0.3% | 9.9% |
| one kind of shopper, with the slope of the sixteen premium meats (2.2 times) | 48.8%, 43.2%, 37.9%, 28.1%, 13.7%, 6.1% | -0.85 | 1.9% | 19.4% |
| one kind of shopper on the curve fitted to the sixteen premium meats (slope and level), with cultivated meat's corrections | 6.8%, 5.5%, 4.4%, 2.9%, 1.2%, 0.5% | -0.90 | 0.1% | 1.8% |

- The first row is the model. The second is the model before: too few buyers above twice the price.
- The third and fourth weaken the slope for every shopper and keep the level at equal price. They are too generous: at twice meat's
  price they give 16–28%, where premium real meats take 3–4%.
- The last takes both slope and level from the premium meats. It was the first candidate for the default and was not taken: its 7% at
  equal price comes from labels, which are never cheaper than the ordinary product, and it would cut the best case to 1.8%
  (`demand_recalibration.md` §1).
- **Across the one-kind responses Central's share runs from 0.04% to 1.9%.** The demand side, not the cost side, is the
  model's widest uncertainty. The model's 0.2% and 4.5% sit inside that range.

## 3. Two smaller things from the same reading

- **A plant-based competitor at meat's price changes little here**: under 3% of cultivated meat's share, because the model's shoppers
  do not treat plant-based meat as real meat. Plant-based meat's own share would rise from 1.2% to 4.1%.
- **A plant that sells less than it was built for costs more per kilo** (`market_size_loop.underused`): the plant's charge and its
  labour are paid whatever it makes.

| share of the plant's capacity that is sold | 1. Today | 3. Plus cells selected to grow faster on the low-waste feed (Central) | 5. Plus engineered cells |
|---|---|---|---|
| 100% | $62.96 | $29.42 | $9.66 |
| 80% | $73.59 | $31.65 | $10.34 |
| 60% | $91.29 | $35.38 | $11.48 |
| 40% | $126.71 | $42.85 | $13.75 |

  Every scenario is at 100%. Beyond Meat's sales fell about 40% from their peak after its plants were built, and its costs run about 70%
  above a right-sized plant's (Knowles 2026). The market-size loop runs backwards as well as forwards.

## 4. What is left

- Plant-based meat's elasticity: verify the -1.23 at its source, then decide whether it becomes a calibration target. It needs the
  split between the dollar and the ratio price terms re-solved (TODO).
- Judgement: that the model's response to price for cultivated meat is now within a factor of two of the truth above parity:
  about 0.5. That it is still too strong, not too weak: about 0.65.

## Sources

1. Knowles, "Why is plant-based meat still so expensive?", Net Primary Production, 16 November 2026 (FT; cites GFI for the elasticity and the 76% price premium).
2. Van Loo, Caputo & Lusk 2020, Food Policy (as used in `market_share.py`).
3. `premium_curve.md` and `market_size_loop.md` for the other two measurements and their sources.
