# Is the model's response to price as strong as measured ones?

Date: 2026-11-18. Code: `demand_checks.py`; test: `tests/test_demand_checks.py`. Changes no default; it argues for one (section 4).

Access levels: **FT** full text read; **ABS** abstract only; **SNIP** search snippet.

**Why.** How fast cultivated meat's share falls as its price rises above meat's decides the share in every scenario but the best case:
Central's shop price is 1.2 to 9 times the meat it sits beside. The model's price response was set from one choice experiment and six
premium products. Four measurements can now be set against it.

## 1. The four checks

| what was measured | measured | the model | verdict |
|---|---|---|---|
| Plant-based meat's own-price elasticity (US retail) | -1.23 | -2.85 | 2.3 times too strong |
| Slope of share against price across sixteen premium real meats (as a multiple of meat's own elasticity) | 2.2 | 8.5 | 3.8 times too strong |
| A premium product getting cheaper: percent more volume per percent lower price (farmed salmon) | 1–1.5 | 3.0–3.4 (prime beef, sushi-grade seafood) | 2 to 3 times too strong |
| Cultivated meat at first contact and equal price: own-price elasticity (choice experiment, simulated from its fitted model) | about -1.5 (-1.1 to -1.65 across its arms) | -3.27 | 2.2 times too strong |

- **Plant-based meat** is the only novel meat with sales data. Its measured own-price elasticity is -1.23 (GFI's US retail figure,
  as cited by Knowles 2026, FT; the GFI source was not read). The model's, at plant-based meat's own price (1.77 times meat's) and
  share (1.2%), is -2.85. The model was calibrated to plant-based meat's share, not to its response to price.
- **Sixteen premium real meats** (`premium_curve.md`): a curve fitted to them has shoppers 2.2 times as price-sensitive as meat in
  general, against the model's 8.5.
- **Farmed salmon** (`market_size_loop.md` §6): while it was still a premium product each 1% off its price brought 1.0–1.5% more volume
  along the demand curve; the model's prime beef and sushi-grade seafood respond with 3.0–3.4%.
- **The choice experiment** (Van Loo, Caputo & Lusk 2020) gives about -1.5 at equal price and first contact, simulated from
  its fitted model; the model's is -3.27. This row was corrected on 2026-11-18: the range "−0.84 to −3.4" used before, which the
  model sits inside, is a formula applied to two of the paper's coefficients and not a measured response
  (`demand_heterogeneity_evidence.md` §1).

Four measurements of different products, by different methods, say the same thing: **the model is two to four times too
price-sensitive.** The model's own elasticity for cultivated meat also grows with the price: -1.75 at equal price, -6.7 at twice
meat's price and -10.4 at three times. That steepening is a property of a logit in which every shopper likes the product equally, and
is what removes nearly all sales at Central's prices. The cause and the remedy are in `liking_spread.md`.

## 2. What a weaker response would give

| price response | share of a meat at 1×, 1.25×, 1.5×, 2×, 3×, 4× its price | at first contact and equal price | world share, 3. Plus cells selected to grow faster on the low-waste feed (Central) | world share, 5. Plus engineered cells |
|---|---|---|---|---|
| the model (cultivated meat 8.5 times as price-sensitive as meat in general) | 48.8%, 28.8%, 14.6%, 2.9%, 0.09%, 0.00% | -3.27 | 0.04% | 3.1% |
| no extra sensitivity for cultivated meat (4 times, as for any one product) | 48.8%, 38.9%, 29.9%, 15.9%, 3.6%, 0.7% | -1.54 | 0.3% | 9.9% |
| the slope of the sixteen premium meats (2.2 times), at the model's level | 48.8%, 43.2%, 37.9%, 28.1%, 13.7%, 6.1% | -0.85 | 1.9% | 19.4% |
| the curve fitted to the sixteen premium meats (slope and level), with cultivated meat's corrections | 6.8%, 5.5%, 4.4%, 2.9%, 1.2%, 0.5% | -0.90 | 0.1% | 1.8% |

Read across the last two columns: **the price response alone moves Central's share fifty-fold, from 0.04% to 1.9%, and the best
case's from 1.8% to 19.4%.** No cost input comes near that.

- The second and third rows weaken the slope and keep the model's level (half the market at equal price, if shoppers see it as real
  meat that tastes the same). They are too generous: at twice meat's price they give 16–28%, where premium real meats take 3–4%.
- The last row takes both slope and level from the premium meats, and corrects for what differs for cultivated meat (no killing,
  novelty, an "unnatural" image). It fits the premium data by construction. Its low level at equal price (7% where the model has 49%)
  is what premium labels show; but labels are never cheaper than the ordinary product and the data start at 1.5 times its price, so
  that level is an extrapolation, and it gives a product near parity too little.
- **None of these rows is the remedy.** The measurements are matched by letting shoppers differ in how much they like cultivated
  meat, with each shopper as price-sensitive as now (`liking_spread.md`).

## 3. Two smaller things from the same reading

- **A plant-based competitor at meat's price changes little here.** With plant-based meat at parity (it is at 1.77 times), cultivated
  meat's share moves from 0.043% to 0.042% at Central and from 3.11% to 3.03% in the best case: the model's shoppers do not treat
  plant-based meat as real meat. Plant-based meat's own share would rise from 1.2% to 4.1%.
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

## 4. What this says

- **The demand side, not the cost side, is the model's widest uncertainty**, and the default sits at its pessimistic end for every
  scenario but the best case.
- **The remedy is a spread of liking across shoppers** (`liking_spread.md`), not any of the single curves above. An earlier
  proposal here, to move the default to the last row, was withdrawn: it cut the best case's share though its cells are near parity.
- Judgement: that the model's price response is too strong by a factor of two or more: about 0.8. That Central's long-run share, at
  Central's cost, is above the model's 0.04%: about 0.8; above 0.5%: about 0.15.

## Sources

1. Knowles, "Why is plant-based meat still so expensive?", Net Primary Production, 16 November 2026 (FT; cites GFI for the elasticity and the 76% price premium).
2. Van Loo, Caputo & Lusk 2020, Food Policy (as used in `market_share.py`).
3. `premium_curve.md` and `market_size_loop.md` for the other two measurements and their sources.
