# Cultivated meat: how far can it get? — results

*A cost and demand model of cultivated meat, anchored to the only peer-reviewed cost study built on
measured production data (Pasitka et al., Nature Food 2024) and bounded by the physical feedstock floor
(Humbird 2021). This is the results brief. The plain-language explanation of how the model works is in the
[interactive explorer](https://pabloamc.github.io/Cultivated_meat/interactive.html) (“How the model works”);
code-level methods and every parameter source are in [METHODS.md](METHODS.md). Every number here reproduces
from the code: `python report_figures.py` for the figures, the per-module scripts for the tables.*

---

## Summary

- **Made at scale with today's technology, cultivated meat would cost about 2.4× as much as everyday meat.**
  In Pasitka's projection for a large plant, built on their measured production data (mid-sized reactor design,
  measured medium price), a kilo of cells costs about $24 and sells for about $29, against a $12 benchmark for
  everyday meat. Current pilot production costs far more. Across the plausible range of every cost input, the median is **R ≈ 2.1** (80% range
  1.6–2.6), and no draws reach parity. The median is lower than 2.4 only because the cell-efficiency range
  allows improvement but not deterioration.
- **Price parity needs costs at their physical floor.** The cells must eat a fixed amount of amino acids and
  glucose, and even an ideal plant has running costs: together about **$7.5/kg**. Parity with $12 meat and a
  $5 markup needs **$7/kg**. So the floor sits right at the parity line (R ≈ 1.04).
- **At the same price, and once shoppers are used to it, cultivated meat would win about 49% of the market,
  if they accept it as real meat.** Not credited as real meat, it gets about 10%. Whether it tastes as good (26% if it tastes a bit worse)
  and whether mainstream shoppers come to value “no slaughter” (up to 68%) are open questions that only
  shelf data can settle; the model leaves them as dials.
- **At today's cost that adds up to little:** about **2.5% of the meat market worldwide by weight** (Monte
  Carlo median; 80% range 0.6–7.7%), **7.5% in Europe**, where meat is dearest, and 4.1% in the US. Counted in
  animals it would be lower still, because most land animals raised for meat are chickens, where cultivated
  does worst.
- **Its best chances are in beef and seafood.** Chicken and pork are cheap enough that cultivated stays more
  expensive even at the cost floor. Premium products (wagyu, sushi-grade fish) are already beatable on price,
  but authenticity holds cultivated to about a quarter of those small markets; beef and seafood cuts displace
  the most meat. Where cultivated can already win (foie gras, bluefin tuna), the markets are tiny.
- **These are long-run ceilings at today's cost.** From a near-zero start, a new product takes roughly two
  decades to get close to its ceiling; falling costs would raise the ceiling along the way.

**For funders:** the binding constraints are **reactor scale-up** and **medium cost at production scale**,
both undemonstrated, plus independent at-scale facility-cost data. Another bench-scale medium win is not
the gap.

---

## 1. What the model is

Four steps, computed for each kind of meat and region (the explorer's four-step strip):

1. **Cost → price.** Medium + plant running cost (+ scaffold for cuts) + retail markup, divided by the price of
   the conventional meat it replaces: the price ratio **R**.
2. **Price → choice.** A discrete-choice (logit) model: shoppers choose between conventional meat,
   plant-based meat, cultivated meat and beans, weighing price, taste, “is it real meat?”, health and animal
   welfare. Two kinds of shopper (95% mainstream, 5% vegetarian or vegan). Calibrated so plant-based meat
   reproduces its observed ~1.2% share and its ~89% mainstream buyer base.
3. **Every meat, every region.** Repeat at each meat type's local price (mince, cuts, premium), then add up
   by volume (animal impact) and by value (money).
4. **Over time.** Adoption starts from today's wary shoppers and rises as the product spreads (Bass
   diffusion) and stops feeling new.

The two outputs deserve different levels of trust. **The price ratio R** is a cost built from measured data,
divided by an observed price: fairly solid. **The market share** it buys depends on how people will treat a
product nobody can buy yet, so it is always shown as a band, never a single number.

---

## 2. Cost and the price ratio

| Pasitka reactor design (Fig. 4) | cells, $/kg | R vs $12 meat | reading |
|---|---|---|---|
| large perfusion reactors (20 m³) | $22 | 2.25 | scale-up succeeds |
| ten 5 m³ vessels (the default) | $24 | 2.42 | Pasitka's mid design |
| many small 0.5 m³ vessels | $38.8 | 3.65 | scale-up stalls: the downside |

“Today's cost” throughout means this projection for a large plant built with today's demonstrated technology,
not what pilot production costs now. The $12 is a round benchmark for everyday meat (range $10–14); the per-type
and regional results use each meat's own local price.

Medium costs about $14/kg at the measured $0.63 per litre (22.4 L per kilo of cells). Companies reported
$0.20/L or less in 2025, and a GFI and MG Consulting analysis of amino-acid prices supports that level
(GFI 2026), but there is no peer-reviewed measurement at production scale. Pasitka's continuous run was at
1.8 L, with pilot hardware at 300 L; the cheap projections assume reactor volumes nobody has yet built for
animal cells.

**The floor** is about $7.5/kg: amino acids ($0.5, Humbird), glucose ($1, assumed) and a minimal plant ($6,
from Pasitka's cost breakdown). It assumes the
reducible costs (recombinant proteins, single-use parts, small-scale capital) are engineered away, but not
Humbird's scale-up limits (oxygen and CO₂ transfer, sterility), which, if they bind, put the floor out of
reach at any medium price.

**Where R lands** (Monte Carlo over the cost inputs and the meat price, N = 20,000):

```
basic product vs commodity meat ($12/kg):
  price ratio R:   P50 = 2.09   80% CI [1.63, 2.63]   90% CI [1.52, 2.79]
  long-run share:  P50 = 7.3%   80% CI [1.9, 22.4]
  0% of draws reach parity (R ≤ 1)
```

**What moves R** (each input swept across its range, the others at their central values):

```
  input          R(lo)  R(hi)  swing  width%   optimistic end
  media_price     1.61   3.11   1.49    19%    $0.20/L (company reports)
  efficiency      1.54   2.42   0.88     0%    0.25x (cells four times leaner)
  p_conv          2.90   2.07   0.83     7%    $14/kg (dearer meat, or a meat tax)
  overhead        2.09   2.84   0.75     9%    $6/kg (very large plants)
  markup_add      2.17   2.58   0.42     2%    $2/kg
  swing = the full low-to-high move. width% = how much the Monte Carlo band narrows if this input is
  fixed (not a variance share; it under-credits one-sided ranges such as efficiency).
```

No single input reaches parity: the best one alone gets to R ≈ 1.5. Medium price leads on both measures
because its range runs both ways: medium could also be *dearer* than Pasitka's $0.63/L for processes that
haven't matched their results. Cell efficiency has a large swing but ~0% width because its range starts at
today's cells and can only improve. Reactor scale's width (9%) understates it: it carries the largest
downside (the small-vessel stall at R ≈ 3.65, deliberately kept outside the central range) and is the least
demonstrated step.

---

## 3. What share a price buys

**At equal price** (R = 1), once shoppers are familiar with it and with everything else neutral, mainstream
shoppers see two near-identical real meats and split that market. Shares are of a four-way choice that includes
skipping meat for beans:

| if cultivated meat… | its share at equal price |
|---|---|
| tastes as good and counts as real meat (the default) | **~49%** |
| …without its small health edge over conventional | ~47% |
| tastes a little worse (taste 0.8) | ~26% |
| tastes noticeably worse (taste 0.6) | ~12% |
| is judged tastier (taste 1.1) | ~61% |
| tastes as good, and mainstream shoppers value “no slaughter” a little (0.5) | ~59% |
| tastes as good, and they value it strongly (1.0) | ~68% |
| tastes as good, and they value it very strongly (1.5, beyond the Monte Carlo range) | ~75% |
| tastes as good but is not accepted as real meat at all | ~10% |

At first contact, before shoppers are familiar with it, the model gives about 6% at equal price, in line with the
~5% in a US choice experiment (the starting wariness is set to match it).

**At today's price** (R ≈ 2.4) the model gives about **9%** in the long run (US, everyday meat): price is the
binding constraint. The share falls slowly just above parity and faster further out (once familiar, the
elasticity is about −0.8 at parity, −1.7 at R = 1.5, −3.6 at R = 2.4).

**Checks on the demand model:**

- **Where cultivated's buyers come from.** Adding cultivated meat at equal price takes 44 points from
  conventional meat and only 0.6 points from plant-based. The shared “real meat” attribute produces this
  without a nested logit.
- **Plant-based milk, out of sample.** The same model, with only the product's facts changed to milk's (near
  price and taste parity in coffee, no cheap alternative), predicts ~15%, close to milk's market share. The model
  was fitted to plant-based *meat*, not milk, but milk's facts are set by hand and other products (margarine,
  plant-based nuggets) fit less well, so this is a weak test.
- **Ethical shoppers** choose cultivated at parity (~20%) but not at a premium (~9% at R = 1.6): the cheap
  whole-food option that keeps plant-based meat low also beats a pricey cultivated product for them.
- **Price sensitivity is tied to data.** A US choice experiment that priced lab-grown meat at six levels
  (Van Loo, Caputo & Lusk 2020) puts its elasticity at parity between −0.84 and −3.4; the model's implied
  value in that setting (equal price, first-contact wariness) is −1.5. The −3.6 at today's price is an
  assumption (κ × ε): no experiment has priced cultivated meat that far above parity. That closeness parameter
  (κ = 4, range 3–6) is the most consequential demand assumption above parity.
- **One calibration target is assumed:** ~6% of mainstream meals skipping meat by choice has no clean source.
  It barely moves the result (0.3 pp across 4–14%).

**What moves the share most** at today's price (the share tornado): the cost levers (medium price, cell
efficiency, meat price, plant cost), then the demand dials: long-run novelty, the value of “no slaughter”,
taste, price sensitivity and health image.

These demand parameters are **calibrated to a few facts, not estimated** from purchase data, which don't
exist yet; the model is partial-equilibrium (prices are given, no supply response) with two kinds of shopper.

---

## 4. By type of meat: price and demand pull in opposite directions

Cultivated meat costs about the same whatever animal it copies, but conventional prices vary widely, so R
and share differ by meat type. Premium is defined per species: a cut costing at least 2.5 times the species'
cheapest form. US, neutral dials; left at today's cost, right at the cost floor:

```
                                    today's cost          at the cost floor
  meat type              $/kg  vol%   R     share            R     share
  chicken (ground/proc.)   5   20%   5.80     0.3%         2.50    15.2%
  chicken (cuts)           9   20%   3.89     1.2%         2.06    13.2%
  beef (ground)           11   13%   2.64     8.2%         1.14    48.4%
  beef (steak/cuts)       20   10%   1.75    13.9%         0.93    42.0%
  beef (prime/wagyu)      45   ~0%   0.78    23.9%         0.41    36.8%   premium
  pork (processed)         8   12%   3.63     2.8%         1.56    34.7%
  pork (cuts)             12    8%   2.92     3.5%         1.54    22.3%
  seafood (fillet)        24    4%   1.46    20.1%         0.77    49.6%
  seafood (sushi)         40    2%   0.88    20.9%         0.46    34.0%   premium
  TOTAL, US: today 5.0% by volume (8.4% by value); at the floor 27.3% (31.8%)
```

- **Beef and seafood are where cultivated can compete.** Chicken and pork stay above parity even at the
  floor (R ≥ 1.5).
- **Today, premium products get the biggest share of their category:** cultivated is already cheaper than
  wagyu or sushi-grade fish, but authenticity and low price sensitivity hold it to roughly a quarter. (At
  the cost floor, R = 0.41, a mince product at wagyu's price would take ~86%; wagyu takes ~37%.) These
  markets are small.
- **Beef and seafood cuts displace the most meat by volume**, and if costs fell to the floor, cuts and even
  ground beef would overtake premium. The tier values behind this (authenticity +0.2 / −0.4 / −1.5, price
  sensitivity ×1 / ×0.8 / ×0.3) are judgement, scaled by one “premium resistance” dial that the Monte Carlo
  samples between 0.5 and 1.5.

(Rows for turkey, heritage pork, organic chicken, canned seafood and rabbit are in `python meat_market.py`.)

---

## 5. Total penetration, by region

Rolling up across meat types, sampling costs, the acceptance dials, price sensitivity, long-run novelty,
health image and premium resistance, **at each region's own meat prices and income**
(`report_regional_band`):

```
total cultivated penetration of meat (N=30,000), 80% CI [P10, P90]:
  region   income/cap   by VOLUME (impact)        by VALUE ($ market)
  Europe    $62k        P50  7.5%  [2.4, 18.2]    P50 12.3%  [ 4.1, 27.7]  <- easiest (rich + priciest meat)
  US        $86k        P50  4.1%  [1.2, 11.8]    P50  6.5%  [ 2.0, 17.0]
  Global    $24k        P50  2.5%  [0.6,  7.7]    P50  4.6%  [ 1.3, 13.1]
  China     $27k        P50  2.1%  [0.6,  6.0]    P50  5.0%  [ 1.5, 12.9]
  Brazil    $22k        P50  0.6%  [0.1,  2.4]    P50  1.0%  [ 0.2,  3.6]
  India     $11k        P50  0.1%  [0.0,  0.5]    P50  0.4%  [ 0.1,  1.3]
  Nigeria    $6k        P50  0.1%  [0.0,  0.3]    P50  0.1%  [ 0.0,  0.5]  <- hardest (cheap meat + price-sensitive)
```

Two forces compound. **Local meat prices:** Europe's expensive meat puts parity nearest. **Income:** the same
premium is a bigger bite of a smaller income, so poorer shoppers are more price-sensitive (the
Berry–Levinsohn–Pakes form, damped so the rich–poor gap matches the roughly twofold difference seen in food
data). Low-income regions combine cheap meat with high price sensitivity, so cultivated barely registers
there at today's cost; their meat prices and mixes are rough. The bands are wide and skewed: the low end is
the world where scale-up stalls or shoppers resist; the long tail is the one where scale-up succeeds and
shoppers embrace it. The Monte Carlo medians are a little below the explorer's point estimates at the default
settings (Global 2.9%, Europe 9.5%, US 5.0%), because the sampled ranges are not centred on the defaults (for
example, taste can match conventional meat but not beat it). Shares by volume are by weight of meat; a count of
animals would be lower, since chickens dominate it.

**Premium seafood is the one place parity is within reach today.** A structured product against sushi-grade
salmon ($40/kg) has a median R of 0.85, and 83% of draws are at or below parity. But its biggest unknown is
the cost of structuring the product (no published cost study), and premium buyers are reluctant.

---

## 6. Entry points: which products first

The explorer's chart 7 looks at specific products, comparing cultivated's cost with the price of the
product's *everyday* grade (farmed rather than wild salmon, crossbred rather than A5 wagyu), because the
luxury premium is for pedigree that cultivated meat can't copy. A prestige core of buyers (25% by default, a
proxy from the share of supply in the only two published grade splits) never switches. The pattern at the
defaults:

- **Already cheaper:** foie gras, bluefin tuna, sea urchin, wagyu, lobster. But these markets are tiny,
  thousands to hundreds of thousands of tonnes a year.
- **Not reachable on price, where the volume is:** commodity beef, pork and chicken, each tens of millions of
  tonnes (chart 7 uses whole-category volumes), stay out of reach even at the cost floor at world commodity
  prices. A small share of these would displace far more meat than winning a luxury niche outright.

Chart 7 gives luxury products much higher shares than chart 1: it removes the prestige core and treats the rest
like ordinary cuts, where chart 1 applies one large authenticity penalty to the whole premium category. They are
two ways of modelling the same resistance; chart 1 is the conservative one.

That is the usual path of a new technology: start where buyers pay a premium, then move down-market as costs
fall with experience. Foie gras stands out as a first product: unstructured (no scaffold), expensive, and
increasingly banned on welfare grounds that don't apply to a cultivated version. The model assumes sale at
cost (no margin), so this is about reach and impact, not profitability.

---

## 7. Over time

At today's price and cost, held fixed, cultivated meat starts near 0%, reaches about 1% after 10 years and
about 8% after 30, close to its long-run ceiling of about 9% (US, everyday meat), levelling off around year 25.
Timing is rougher than the ceilings: it uses a Bass curve built for durable goods plus a separate familiarity
fade, which may partly overlap. How wary
shoppers are today is the widest demand uncertainty: surveys range from ~5% (a cold choice experiment) to
~60% (“cultivated chicken in a restaurant”) depending on framing. The model starts at the cold end and
samples the whole range. `cost_paths_timing` shows penetration over 30 years for different cost-milestone
paths: low and flat if costs stall, rising after a breakthrough year.

---

## 8. What a technical funder should prioritise

1. **Medium cost at production scale.** It leads both the swing and the band width, because it could go
   either way: the question is not only how cheap, but whether $0.63/L is reproducible at all for other cell
   lines and processes. Verify the sub-$0.20/L company reports at scale, and de-risk the dearer tail.
2. **Reactor scale-up**, the biggest physical risk: least demonstrated, and the source of the largest
   downside (R ≈ 3.65 if production stays in small vessels). Demonstrating large-volume animal-cell perfusion
   (oxygen and CO₂ transfer, shear, sterility at scale) is the step the cheap projections assume.
3. **Plant costs at scale**, the largest term in the floor: independent, at-scale facility-cost data would
   show where the floor really sits relative to parity. GFI's 2026 report flags this as the field's main
   data gap.
4. **The meat price is a policy lever.** A tax that raises conventional prices by 25% lowers R as much as
   cutting every cultivated cost by 20%.
5. **Scaffolding cost** is the biggest number no one has measured, and it gates the premium-seafood route.
   A scaffolding cost study is the literature's clearest hole.

These are mostly public goods (at-scale demonstrations, independent cost studies), underfunded by industry
and a good fit for philanthropy.

---

## 9. What would change the conclusions

- **Upward:** a peer-reviewed demonstration of animal-cell perfusion at 20,000 L or more, holding density and
  sterility, would remove the scale-up downside and pull R toward the large-perfusion case. Independent
  confirmation of medium below $0.30/L at scale would move cheap medium from upside into the central case.
- **Downward:** if the scale-up limits (CO₂-limited vessel size, clean-room costs) prove binding, the floor is
  out of reach at any medium price, and R stays around 3 or more.
- **Demand:** whether shoppers accept cultivated as real meat, and whether they come to value “no slaughter”,
  can't be measured until it is on shelves. The honest position is to carry the full range (10% to 75% at
  equal price) and let each reader set it.

---

### Key parameters (the full datasheet: `python inputs.py`)

| parameter | central | Monte Carlo range | source | what it controls |
|---|---|---|---|---|
| `p_conv` | $12/kg | 10–14 | retail data | everyday meat price; with the markup, the parity threshold; the meat-tax lever |
| `markup_add` | $5/kg | 2–7 | USDA farm-to-retail spread | biomass-to-retail cost, added per kilo |
| `overhead` | $9.9/kg | 6–15 (stall case 24.7) | Pasitka Fig. 4 | plant running cost, set by reactor scale |
| `media_price` | $0.63/L | 0.20–1.00 | Pasitka (measured); GFI 2026 (company reports) | medium cost, both directions |
| `efficiency` | 1.0 | 0.25–1.0 | Pasitka's cells; CHO cells | medium used per kilo, relative to today's cells |
| `accept_x` | 1.0 | 0.6–1.0 | judgement | cultivated's taste vs conventional |
| `theta_free_M` | 0 | 0–1.0 | judgement | how much mainstream shoppers value “no slaughter” |
| `real_tissue_x` | 1 | not sampled | the model's premise | whether cultivated counts as real meat |
| `neophobia_x` | 0 | −2 to +1 | judgement | long-run novelty attitude (− wary, + drawn) |
| `health_x` | 0 | −0.5 to +0.5 | surveys go both ways | cultivated's health image |
| `eps_own` | −0.9 | −1.4 to −0.5 | grocery scanner data | price sensitivity of meat as a category |
| `cult_sub_mult` (κ) | 4 | 3–6 (not sampled) | bracketed by Van Loo, Caputo & Lusk 2020 | how much more price-sensitive a cultivated product is than meat overall |
| `premium_resistance` | 1 | 0.5–1.5 | judgement | how strongly cuts and premium resist (scales the tier values) |
| `process_cost` | $5/kg | 1–15 | no published data | scaffolding process cost (structured products only) |

### Figures (`python report_figures.py`; diagnostics in `figures/diagnostics/`)

1. `cost_vs_inputs`: biomass cost against the medium price, one line per reactor design, with the floor.
2. `cost_waterfall`: from the small-vessel case down to the floor; reactor scale is the biggest single step.
3. `sensitivity_tornado_share`: which inputs move the long-run share most.
4. `share_vs_ratio`: the share a given price ratio buys.
5. `pb_milk_vs_meat`: the plant-based milk check, same model, different product facts (~15% vs ~1%).
6. `cost_paths_timing`: penetration over 30 years for different cost-milestone paths.
7. `penetration_by_type_{us,eu,china,global}`: share by type of meat, at the cost floor.
8. `report_regional_band`: the regional totals with their bands.
