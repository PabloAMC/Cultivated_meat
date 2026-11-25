# Model audit: drift, accuracy and whether the costs are reasonable price points

2026-11-25 (the gas cap and loop thinning): the engine now tries every gas flow up to the cells' cap and holds a design whose
column loop is overloaded thinner, so draws that priced an overloaded loop as if it coped now cost what a passing loop costs.
`audit.py`'s draws (seed 0, 1,000): the low-lactate example's median $57.68 to $57.22 and 10th percentile $42.62 to $42.36; the
all-favourable example's median $8.22 to $8.11. The points ($48.68, $6.97) sit at the 26th and 11th percentiles; membrane life,
then the lactate and ammonia the cells tolerate, still lead the ranking. The sections below are not rewritten.

Date: 2026-11-15; recomputed 2026-11-16 after PR #32 (protectant, antifoam, the plant ladder tied to `explore`) and again after
the scenarios' lower dissolved-oxygen setpoint. Section 0 is the audit on the final model of 2026-11-20. Sections 1 to 6 are the
audit as written on 2026-11-16, when the low-lactate example cost $29.42 and the all-favourable example $9.66; they are a snapshot
and were not rewritten. Code: `audit.py` (global uncertainty and the retail translation), `audit_history.py` (the history of the
headline numbers), `tests/test_audit.py`. Costs are 2025 dollars per kg of wet cells. This note changes no default.

## 0. On the final model (2026-11-20)

**The points.** Humbird's optimistic design as this model prices it (`scenarios.reference()`) $15.93, the low-lactate example
$49.50, the all-favourable example $7.62, Published cells $322.55.

**Drift since section 2 was written.** Rows added by hand:

| When | Reference | Low-lactate example | All-favourable example | What changed |
|---|---|---|---|---|
| 19 Nov, first repin | $12.81 | $26.43 | $9.96 | nutrient floor $2.00; growth factors counted inside the announced medium prices (the low-lactate example's first large step down) |
| 19 Nov, audit batch | $12.81 | $32.80 | $11.46 | cells tolerate 4 mmol/L of ammonia, not 5; a lost run throws its membranes away; glucose from the cells' own balance |
| 20 Nov, model batch | $15.93 | **$49.50** | **$7.62** | lactate tolerated 35 mmol/L, not 50; bubble deaths and a 2% harvest loss charged; twice the crew in perfusion; membrane life 2,415 L/m²; medium preparation sized by the medium passed; thick cultures take up oxygen more slowly. The all-favourable example was redefined as one case, the most favourable value of every lever among this model's ranges, Humbird's design and ten published studies (`scenarios.all_favourable`, 42 m³ tank, dialyser-grade fibres) |

So the last corrections went up again for the low-lactate example, by 51%, as section 2 warned. The all-favourable example fell
because it is now a different case, not because a cost was removed.

**Everything uncertain at once (`audit.py` as it draws today; 4,000 draws, seeds 0 and 1 agree within 1%).**

| | Point | 10th percentile | Median | 90th percentile | Point's percentile | Chance at or below $12 / $18 |
|---|---|---|---|---|---|---|
| Low-lactate example | $49.50 | $50 | **$64** | $86 | 10th | 0% / 0% |
| All-favourable example | $7.62 | $8.9 | **$11.3** | $15.0 | below the 1st | 62% / 99% |

Rank correlation with cost, the low-lactate example: membrane life −0.51, the ammonia the cells make +0.47, the lactate they make
+0.27, growth factors +0.27, medium price +0.23. The all-favourable example: the ammonia the cells make +0.76, medium price +0.57,
plant estimate +0.22.

**These draws lag the scenarios, and overstate the cost.** Found in the repins and not changed in the draws:

1. The low-lactate example's $0.20 a litre is a complete medium, with its growth factors in the price. The draws still buy growth
   factors on top of it.
2. The all-favourable example takes the favourable end of every lever: its medium is at the nutrient floor, it loses no runs, its
   cells make Humbird's 0.054 mol of ammonia a kilo. The draws charge its medium $0.15 to $0.50 a litre, draw runs lost and draw its
   ammonia from a wider range, so almost every draw costs more than its point. Its membrane life is passed to the engine directly,
   so the membrane-life draw does not reach it.
3. The ammonia and the lactate the cells tolerate, the culture bubbles kill and the harvest recovery are inputs with ranges that
   the scenario bands draw; these draws hold them.

The side calculation of 19 November that put the first three right was not redone. Read the scenario bands of the results, which
draw the tolerances, for the uncertainty of each case.

**Shelf price.** The low-lactate example's shelf price is **$72** under the model's rule, (cost + $2.5) ÷ (1 − 28%); $55 with the
old flat $5; $92 with the whole spread as a percentage. Parity with US minced beef or pork cuts ($12 a kilo) needs cells at $6.1.

## 1. The short answer

1. **Yes, the costs have drifted, and only upward.** The company-reported default went from $24.01 to $34.35 (+43%) on 14 November. The low-lactate example
   went from $18.14 to $26.64 (+47%) and the all-favourable example from $6.57 to $8.95 (+36%) in the last half day; then
   the low-lactate example to $29.92 (+12%) and the all-favourable example to $9.71 (+9%) when the protectant and antifoam were counted (PR #32). Every step up to then
   added a cost that an earlier version left out. The first step down came on 16 November: holding dissolved oxygen at half of air
   saturation, as pharma does, took the low-lactate example to $29.42 and the all-favourable example to $9.66.
2. **The model has been optimistic, and the evidence says it still is, in a few known places.** Its own back-test finds it needs less
   medium than every reported perfusion run (1.2 to 2.8 times less) and predicts more than twice the output of the one working 20 m³ plant.
3. **The low-lactate example's $29.42 is the most likely value of each input, not the most likely cost.** Draw every documented range at once and
   the low-lactate example's median is **$36**, with 80% of draws between **$27 and $50**. The $29.42 point sits at the **19th percentile**. The all-favourable
   example's $9.66 sits at the 1st.
4. **The $49–94 for the low-lactate example is a sensitivity, not a new central value.** It is the cost if membranes last as long as CHO membranes did.
5. **Costs are cell cost, not shelf price.** A flat $5 markup gives the low-lactate example a shelf price of $34. A markup that is a share of the price
   (as conventional spreads are) gives $55, and lowers the cost at which cultivated meat reaches parity from $7 to $5.6.

## 2. Drift

The history was measured by checking out each commit that touched the cost code and running the model (`audit_history.py`).

| Commit | Time | Default | Reference | Low-lactate example | All-favourable example (then) | What changed |
|---|---|---|---|---|---|---|
| 503fb37 | 10 Jun | $24.01 | | | | first model |
| e92504c | 14 Nov 00:23 | $32.61 | | | | Pasitka's capital charge added to the plant cost (it had been left out) |
| 04ca52d | 14 Nov 12:01 | $29.45 | | | | cost side re-anchored on a company's report; plant classes grounded |
| 6dba0c8 | 14 Nov 12:29 | **$34.35** | | | | an independent audit of the cost side applied |
| 164b78c | 14 Nov 12:54 | $34.35 | $11.48 | | | Humbird's optimistic design financed like a mature food industry |
| da06954 | 15 Nov 00:19 | $34.35 | $11.48 | **$18.14** | **$6.57** | cost scenarios in place of one number |
| 563024d | 15 Nov 12:57 | $34.35 | $11.84 | **$26.64** | **$8.95** | the filter loop's membranes added to perfusion |
| 80b5411 | 16 Nov 00:35 | $34.35 | $12.51 | **$29.92** | **$9.71** | bubble protectant, antifoam's cut to oxygen transfer, the yeast-style plant's oxygen (PR #32) |
| (PR #39) | 16 Nov | $34.35 | $12.51 | **$29.42** | **$9.66** | dissolved oxygen held at half of air saturation in every scenario (the first step down) |

Between 563024d and 80b5411 nine pull requests (retention devices, medium, nutrient floor, tank size, thick culture and the rest) added
analysis and left every pinned value alone, by design. The last two rows are added by hand; `audit_history.py` reproduces them when run.

- **Each step was a correction.** The capital charge, the audit's findings and the membranes were real omissions. The filter loop is the
  clearest: the model had priced the device that holds the cells back at $89k per m³ and nothing for its membranes, which come to $8.33 a
  kilo in the low-lactate example. That is 28% of the cost.
- **A pattern of one-way corrections is a warning.** If a model is unbiased, corrections go both ways. These did not, which says the early model
  was optimistic. It would be wrong to assume the last correction was the last. Sections 3 and 4 look for what remains.
- **The model changed fast.** The headline numbers moved only on 14 and 15 November, driven by successive reviews, and have not moved
  since the filter loop was added.

## 3. Accuracy

### 3a. Against reported runs (`floor_physics.backtest`)

Reported runs against what the model gives for the same cells and vessel. Nothing was tuned to them. Observed ÷ model:

| Run | Quantity | Observed | Model | Ratio |
|---|---|---|---|---|
| CHO, wave bag (Clincke 2013) | medium, L per kg | 59.5 | 21.4 | 2.8× |
| CHO, optimised medium (Mayrhofer 2020) | medium, L per kg | 58.7 | 50.0 | 1.2× |
| Chicken, 10 L perfusion (SuperMeat 2024) | medium, L per kg | 30.5 | 21.6 | 1.4× |
| Chicken, 10 L perfusion (SuperMeat 2024) | density held, g/L | 112 | 214 | 0.5× |
| Quail, 20 m³ drained and refilled (Vow) | output, t per m³ a year | 5.1 | 11.5 | **0.44×** |
| SuperMeat, scaled on paper | output, t per m³ a year | 24.3 | 10.3 | 2.4× (the report does not add up) |
| Pasitka 2024 bench perfusion | density claimed, g/L | 430 | 72 | 6.0× (not cell mass) |

- **In all three perfusion runs the model needs less medium than the run used.** Medium litres per kilo set the medium, growth-factor and
  filtering costs together (`frontier.md`), so this is the model's most consequential optimism.
- **The one working plant makes less than half the model's output.** The model gives efficient cells in the same mode. That gap is mostly the
  density: the model's cap is 92 g/L and Vow's harvests imply about 27 g/L.

### 3b. Against published and claimed costs

| Source | Cost | What it is |
|---|---|---|
| Model: reference / the low-lactate example / best | $12.51 / $29.42 / $9.66 a kilo of wet cells | a 20 m³ perfusion plant; see the scenario definitions |
| Humbird 2021 | "$37/kg wet cell mass" (as quoted in `post_harvest_costs.md`) | design with his own medium, which GFI says was far costlier |
| Pasitka 2024 | $13.7 a kilo of a 50/50 hybrid (a third party puts pure cells at $13.75–22.27) | model of a 50,000 L plant from bench data; the kilogram counted is most likely about 18 times the mass of its cells (METHODS.md, "Why Pasitka is not the anchor") |
| SuperMeat 2024 | $26–29.5, $34.4 with the model's capital charge | model of a 25,000 L plant from 10 L runs |
| Aleph, Gourmey (company-commissioned) | about $8–14 a kilo of product | confidential inputs; products contain plant protein |
| Vow raw slurry (company claim) | under $50 a pound, about $110 a kilo | real operation at up to 20,000 L |
| PARIMA on Vow's line (press) | the low €40s a kilo of finished product | tonne-scale run in a 22,000 L vessel, partly plant-based |

The model's range ($10–30) sits between the modelled claims ($5–15) and the cost of what has actually been run ($46–110 a kilo).
The low-lactate example's shelf price, $34 to $55 depending on the markup rule, is near PARIMA's finished-product figure. The reactor-progress note
puts the gap between real runs and modelled claims at 3 to 6 times. **None of these is an audited cost of goods from a plant.**

### 3c. Everything uncertain at once (`audit.py`)

Each scenario's uncertain inputs are drawn together from the documented triangular ranges (low, most likely, high) in `inputs.py`: the
waste, speed and size of the cells, gas, medium price, growth factors, restart and loss rate, the plant estimate, financing, and the
filter loop's flux, membrane price, hardware and membrane life. 4,000 draws; two seeds agree.

| | Point | 10th percentile | Median | 90th percentile | Point's percentile | Chance at or below $12 / $18 / the point |
|---|---|---|---|---|---|---|
| Low-lactate example | $29.42 | $26.8 | **$36.4** | $49.9 | 19th | 0% / 0.2% / 19% |
| All-favourable example | $9.66 | $11.4 | **$15.1** | $21.5 | 1st | 16% / 74% / 0% |

- **The point is at the low end because the ranges are skewed up.** Each input's most likely value is its point; its high end is far
  further from the point than its low end. So the median is above the point.
- **The cells' ammonia drives it.** Rank correlation with cost (the low-lactate example): ammonia +0.78, membrane life −0.32, medium price +0.26, plant estimate
  +0.23, growth factors +0.22, gas −0.13.
- **What this leaves out makes the true spread wider and more skewed.** The draws are independent (good cell traits come together, which
  fattens both tails). The tank design, the 20 m³ size, the plant class and the density limit are held. The omissions in 3d are not in it.
  The all-favourable example's ranges are partly unsourced: its 24-hour doubling has no range.

### 3f. Why the all-favourable example's point cost is below most of its draws (2026-11-21)

TODO item: the point ($7.62 then, $6.97 now) was below 89% of the draws of its own band (`scenarios.scenario_mc`); now 95%. The cause
was looked for lever by lever: each drawn estimate alone, the rest at the point (4,000 draws, seed 0, model of 2026-11-21).

| Drawn alone | Share of draws below the point | Median of the cost with only this drawn |
|---|---:|---:|
| price of the bubble protectant (most likely $30 a kilo, drawn up to $120; median draw $49) | 18% | $7.43 |
| its dose (most likely 2 g/L, drawn 1-5; median 2.6) | 20% | above the point |
| amino-acid price (most likely $6.36, drawn $5-11.59; median $7.39) | 21% | above the point |
| cells bubbles kill (most likely the bench figure, drawn a quarter of it to three times) | 28% | $7.22 |
| plant estimate (the shared-medium plant's range starts at the yeast-style plant's cost) | 48% | $6.99 |
| yearly charge, antifoam | 45-50% | about the point |
| upkeep share of respiration, slower oxygen uptake of a thick culture | 65-73% | below the point |

It is not a defect. The point is every estimate at its most likely value (the mode of its prior); the all-favourable example takes
the favourable end only of the levers the published studies and Humbird's design set, not of these estimates. Several priors are
skewed to the costly side: the most likely value sits near the low end of the range. A cost at the modes then lies below the
median of the draws. No draw is centred elsewhere than the case's own value, and the medium-price and runs-lost draws do not reach
the case (its medium is at the nutrient floor, it loses no runs). The low-lactate example shows the same effect less strongly (its
point at the 26th percentile in `audit.py`, and $48.68 against a band median of $52.93), because more of its drawn estimates are symmetric. The
page's story of the all-favourable example now says so.

### 3d. What the cost leaves out

| Item | Direction and size | Basis |
|---|---|---|
| First-plant financing (23.6% a year) instead of the mature 17.3% | **+$2.78 the low-lactate example, +$0.77 best** | `humbird_plant_charge`; computed |
| Membrane life at the measured CHO throughput (450–1,200 L/m²) instead of 3,960 | **+$19 to +$64 the low-lactate example** | `filter_flux.md` (a sensitivity) |
| Density: the low-lactate example's fed-batch fallback at 27 g/L instead of 62 | +$50 (only if perfusion fails) | `no_perfusion_downside.md` |
| Medium: the model needs less than every reported perfusion run | up to 1.2 to 2.8 times more medium and filtering | back-test (3a) |
| Nutrient floor: GFI's amino-acid prices instead of the model's $1.70 | +$0.8 to +$3.4 the all-favourable example; none in the low-lactate example | `nutrient_floor.md` |
| Disposal of spent medium (28 L/kg in the low-lactate example) | small, assumed under $0.15 a kilo; not costed | no wastewater cost anywhere in the model |
| Quality control, analytics, working capital, start-up | not costed separately; partly in Humbird's labour and the capital charge | `plant_capital_crosscheck.md` |
| Scaffold and forming for structured products | +$6 a kilo for structured products (a model assumption, separate) | `post_harvest_costs.md` |
| Items that could go the other way | a cheaper plant than the model's (two published designs assume a third of Humbird's); cheaper medium | `plant_capital_crosscheck.md`; `medium_cost_gfi.md` |

### 3e. From a kilo of cells to a shelf price

The model adds a flat $5 a kilo (`markup_add`, range $3–8.7). USDA's conventional spreads are closer to proportional: the
wholesale-to-retail spread is 42–65% of the retail price (`post_harvest_costs.md`). A proportional chain,
(cost + $1 of processing) ÷ (1 − 45%), gives:

| | Cost of cells | Shelf price, flat $5 | Shelf price, proportional |
|---|---|---|---|
| All-favourable example | $9.66 | $14.66 | $19.38 |
| Low-lactate example, shared-medium plant | $26.56 | $31.56 | $50.10 |
| Low-lactate example | $29.42 | $34.42 | $55.30 |
| **Cost of cells at parity with US minced beef or pork cuts ($12 a kilo)** | | **$7.0** | **$5.6** (3.2 to 6.0 across shares of 42–65%) |

Which is right is open. A flat spread is plausible if the retail chain's work does not scale with the product's price. The conventional
spread does scale. **Settled 2026-11-18** (`retail_markup_form.md`): neither. The model now uses per-kg costs plus a percentage margin,
(cost + $2.5)/(1 − 28%), which gives the low-lactate example a $44 shelf price and parity at $6.1; the whole-spread percentage above double-counts the
per-kg part. At the proportional rule parity needs the cost of cells to fall below about $5.6, a level no single lever reaches.

## 4. Are the costs reasonable price points?

My reading, as judgement and not as a forecast:

1. **The low-lactate example ($29.42) is a fair "if these things work" number, and a poor expectation.** It assumes cells that make 0.14 mol of ammonia a kilo,
   36-hour doubling, a food-grade plant, a filter that lasts 3,960 litres a m², and perfusion at 20 m³. Given the documented ranges the
   median is about **$36**, and the middle 80% runs **$27–50**.
2. **The all-favourable example ($9.66) is an everything-works number.** Under the model's own ranges it is a 1st-percentile result. It is a bound on
   what the levers could give if all went right (`frontier.md`, after PR #32, reaches about $7, with levers each of which has low odds).
3. **Parity (a cost of cells near $7, or $5.6 on a proportional markup) is not reached by any scenario.** Under the global draws the chance
   that the low-lactate example falls to $12 is under 0.1%, and the all-favourable example's is 16%.
4. **A realistic band for a first 20 m³ perfusion plant's cell cost is therefore $27–50, with the all-favourable example the lower tail.** Real
   runs so far are at $46–110 a kilo, which the model's gap of 3 to 6 times to modelled claims already leads one to expect.
5. **Perfusion at 20 m³ is itself unshown.** If it fails, the fed-batch fallback costs $41–45 at the model's density cap and $92–99 at the
   27 g/L reported (`no_perfusion_downside.md`).

## 5. What I would do

1. **Show the spread, not just the point.** Replace the scenario bands (which draw six inputs) with this global spread, and say that each
   scenario's headline is the most likely value of its inputs. A reader sees "$29, most likely about $36".
2. **Decide three defaults:** the membrane life (`filter_flux.md`), first-plant or mature financing (+$2.8 in the low-lactate example), and the nutrient
   floor (`nutrient_floor.md`). Each is a judgement, and each moves the low-lactate example by $2 or more.
3. **Close the medium gap in the back-test.** The model's litres per kilo are below every reported run. Either the model's waste
   assumption is optimistic or the runs were not optimised. This is the largest single source of possible bias.
4. **Treat the markup rule as a scenario switch**: flat or proportional. It decides whether parity needs $7 or $5.6.
5. **Measure what the model cannot:** the waste per kilo of a meat cell line, the life of a filter at a quarter cells by volume, and the
   doubling time of a low-waste line in suspension. They are the three biggest drivers.
6. **Keep a drift log.** `audit_history.py` reproduces the table in section 2. If the headline moves again, the pattern in section 2
   will say whether the model is converging.

## 6. Limits of this audit

- The ranges in `inputs.py` come from earlier sessions' judgement and from sources of mixed quality. A wrong range gives a wrong spread.
- The global draws are independent. The all-favourable example's doubling time has no range, so it is held.
- The comparison in 3b is not like for like: products, scales and cost definitions differ, and none is audited.
- I have not checked the shelf-price inputs beyond the USDA numbers in `post_harvest_costs.md`.
