# Model audit: drift, accuracy and whether the costs are reasonable price points

> Names (2026-11-19): "Selected cells" was called Central; "Engineered cells, all favourable" was called the best case.

Date: 2026-11-15; recomputed 2026-11-16 after PR #32 (protectant, antifoam, the plant ladder tied to `explore`) and again after the scenarios' lower dissolved-oxygen setpoint. Code: `audit.py` (global uncertainty and the retail translation), `audit_history.py` (the history of the headline
numbers), `tests/test_audit.py`. Costs are 2025 dollars per kg of wet cells. This note changes no default.

> Repinned 2026-11-19 (audit batch): ammonia tolerance 4 mM, lost runs pay for their membranes, glucose from the cells' balance (published cells need about 95 L/kg); see audit_2026-11-19.md.
> Sections 1 to 6 are the audit as written on 2026-11-16, when Central cost $29.42 and the best case $9.66. They are a snapshot and
> were not rewritten. Section 0 gives the same figures on the model of 2026-11-19.

## 0. On the model of 2026-11-19 (after the audit batch)

**The points.** Humbird's optimistic design $12.81, Central $32.80, the best case $11.46, Published cells $111.89.

**Drift since section 2 was written.** Two more rows, added by hand:

| When | Reference | Selected cells | Best | What changed |
|---|---|---|---|---|
| 19 Nov, first repin | $12.81 | $26.43 | $9.96 | nutrient floor $2.00; growth factors counted inside the announced medium prices (Selected cells' first large step down) |
| 19 Nov, audit batch | $12.81 | **$32.80** | **$11.46** | cells tolerate 4 mmol/L of ammonia, not 5; a lost run throws its membranes away; glucose from the cells' own balance |

So the last correction was upward again, by 24% for Central and 15% for the best case. Section 2's warning stands: a model whose
corrections mostly go one way was optimistic, and may still be.

**Everything uncertain at once (`audit.py` as it draws today; 4,000 draws, two seeds agree).**

| | Point | 10th percentile | Median | 90th percentile | Point's percentile | Chance at or below $12 / $18 |
|---|---|---|---|---|---|---|
| Selected cells | $32.80 | $34.1 | **$46.2** | $64.7 | 7th | 0% / 0% |
| Engineered cells, all favourable | $11.46 | $14.0 | **$18.9** | $27.5 | below the 1st | 1% / 43% |

Rank correlation with cost (Central): the ammonia the cells make +0.75, membrane life −0.39, medium price +0.26, growth factors
+0.22, plant estimate +0.18.

**These draws lag the scenarios in three ways, and overstate the cost.** I found this in the repin and did not change the draws.

1. Central's $0.20 a litre is now a complete medium, with its growth factors in the price. The draws still buy growth factors on
   top of it. That counts them twice, about $5 at the median.
2. The best case's medium is now at the nutrient floor. The draws still charge it $0.15 to $0.50 a litre.
3. The ammonia the cells tolerate is now an input with a range (2 to 8 mmol/L, most likely 4). The draws hold it at 4.

With the three put right (a side calculation, same seeds, with the amino-acid price behind the floor drawn too):

| | Point | 10th percentile | Median | 90th percentile | Point's percentile | Chance at or below $12 / $18 |
|---|---|---|---|---|---|---|
| Selected cells | $32.80 | $28.2 | **$38.3** | $58.0 | 27th | 0% / 0% |
| Engineered cells, all favourable | $11.46 | $10.8 | **$14.4** | $21.7 | 17th | 23% / 77% |

This agrees with the scenario bands the results now report (Central $27 / $37 / $57, best case $11 / $14 / $20), which draw the
tolerance too. The top driver for Central is then the ammonia the cells tolerate (−0.55), ahead of the ammonia they make (+0.49)
and membrane life (−0.37).

**What changes in the reading below.**

- Section 1, item 3, and section 4: Central's median is about **$38** and its middle 80% **$28–58** (it was $36 and $27–50). The
  median moved less than the point because the tolerance's range leans to the tolerant side. The top of the band rose by $8.
- Section 4, item 3: no draw of Central reaches $12 either way. The best case reaches $12 in 1% of draws as drawn and 23% with the
  three points put right (16% on 16 November).
- Section 3e: Central's shelf price is **$49** under the model's rule, (cost + $2.5) ÷ (1 − 28%); $38 with the old flat $5; $61
  with the whole spread as a percentage. Parity with $12 meat still needs cells at $6.1.
- Section 3d was not recomputed. Its membrane-life row is larger now, since Central filters 30 litres a kilo and not 23.

## 1. The short answer

1. **Yes, the costs have drifted, and only upward.** The company-reported default went from $24.01 to $34.35 (+43%) on 14 November. Central
   went from $18.14 to $26.64 (+47%) and the best case from $6.57 to $8.95 (+36%) in the last half day; then
   Central to $29.92 (+12%) and the best case to $9.71 (+9%) when the protectant and antifoam were counted (PR #32). Every step up to then
   added a cost that an earlier version left out. The first step down came on 16 November: holding dissolved oxygen at half of air
   saturation, as pharma does, took Central to $29.42 and the best case to $9.66.
2. **The model has been optimistic, and the evidence says it still is, in a few known places.** Its own back-test finds it needs less
   medium than every reported perfusion run (1.2 to 2.8 times less) and predicts more than twice the output of the one working 20 m³ plant.
3. **Central's $29.42 is the most likely value of each input, not the most likely cost.** Draw every documented range at once and
   Central's median is **$36**, with 80% of draws between **$27 and $50**. The $29.42 point sits at the **19th percentile**. The best
   case's $9.66 sits at the 1st.
4. **The $49–94 for Central is a sensitivity, not a new central value.** It is the cost if membranes last as long as CHO membranes did.
5. **Costs are cell cost, not shelf price.** A flat $5 markup gives Central a shelf price of $34. A markup that is a share of the price
   (as conventional spreads are) gives $55, and lowers the cost at which cultivated meat reaches parity from $7 to $5.6.

## 2. Drift

The history was measured by checking out each commit that touched the cost code and running the model (`audit_history.py`).

| Commit | Time | Default | Reference | Selected cells | Best | What changed |
|---|---|---|---|---|---|---|
| 503fb37 | 10 Jun | $24.01 | | | | first model |
| e92504c | 14 Nov 00:23 | $32.61 | | | | Pasitka's capital charge added to the plant cost (it had been left out) |
| 04ca52d | 14 Nov 12:01 | $29.45 | | | | cost side re-anchored on a company's report; plant classes grounded |
| 6dba0c8 | 14 Nov 12:29 | **$34.35** | | | | an independent audit of the cost side applied |
| 164b78c | 14 Nov 12:54 | $34.35 | $11.48 | | | the reference case financed like a mature food industry |
| da06954 | 15 Nov 00:19 | $34.35 | $11.48 | **$18.14** | **$6.57** | cost scenarios in place of one number |
| 563024d | 15 Nov 12:57 | $34.35 | $11.84 | **$26.64** | **$8.95** | the filter loop's membranes added to perfusion |
| 80b5411 | 16 Nov 00:35 | $34.35 | $12.51 | **$29.92** | **$9.71** | bubble protectant, antifoam's cut to oxygen transfer, the yeast-style plant's oxygen (PR #32) |
| (PR #39) | 16 Nov | $34.35 | $12.51 | **$29.42** | **$9.66** | dissolved oxygen held at half of air saturation in every scenario (the first step down) |

Between 563024d and 80b5411 nine pull requests (retention devices, medium, nutrient floor, tank size, thick culture and the rest) added
analysis and left every pinned value alone, by design. The last two rows are added by hand; `audit_history.py` reproduces them when run.

- **Each step was a correction.** The capital charge, the audit's findings and the membranes were real omissions. The filter loop is the
  clearest: the model had priced the device that holds the cells back at $89k per m³ and nothing for its membranes, which come to $8.33 a
  kilo in Central. That is 28% of the cost.
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
| Model: reference / Selected cells / best | $12.51 / $29.42 / $9.66 a kilo of wet cells | a 20 m³ perfusion plant; see the scenario definitions |
| Humbird 2021 | "$37/kg wet cell mass" (as quoted in `post_harvest_costs.md`) | design with his own medium, which GFI says was far costlier |
| Pasitka 2024 | $13.7 a kilo of a 50/50 hybrid (a third party puts pure cells at $13.75–22.27) | model of a 50,000 L plant from bench data; the kilogram counted is most likely about 18 times the mass of its cells (METHODS.md, "Why Pasitka is not the anchor") |
| SuperMeat 2024 | $26–29.5, $34.4 with the model's capital charge | model of a 25,000 L plant from 10 L runs |
| Aleph, Gourmey (company-commissioned) | about $8–14 a kilo of product | confidential inputs; products contain plant protein |
| Vow raw slurry (company claim) | under $50 a pound, about $110 a kilo | real operation at up to 20,000 L |
| PARIMA on Vow's line (press) | the low €40s a kilo of finished product | tonne-scale run in a 22,000 L vessel, partly plant-based |

The model's range ($10–30) sits between the modelled claims ($5–15) and the cost of what has actually been run ($46–110 a kilo).
Central's shelf price, $34 to $55 depending on the markup rule, is near PARIMA's finished-product figure. The reactor-progress note
puts the gap between real runs and modelled claims at 3 to 6 times. **None of these is an audited cost of goods from a plant.**

### 3c. Everything uncertain at once (`audit.py`)

Each scenario's uncertain inputs are drawn together from the documented triangular ranges (low, most likely, high) in `inputs.py`: the
waste, speed and size of the cells, gas, medium price, growth factors, restart and loss rate, the plant estimate, financing, and the
filter loop's flux, membrane price, hardware and membrane life. 4,000 draws; two seeds agree.

| | Point | 10th percentile | Median | 90th percentile | Point's percentile | Chance at or below $12 / $18 / the point |
|---|---|---|---|---|---|---|
| Selected cells | $29.42 | $26.8 | **$36.4** | $49.9 | 19th | 0% / 0.2% / 19% |
| Engineered cells, all favourable | $9.66 | $11.4 | **$15.1** | $21.5 | 1st | 16% / 74% / 0% |

- **The point is at the low end because the ranges are skewed up.** Each input's most likely value is its point; its high end is far
  further from the point than its low end. So the median is above the point.
- **The cells' ammonia drives it.** Rank correlation with cost (Central): ammonia +0.78, membrane life −0.32, medium price +0.26, plant estimate
  +0.23, growth factors +0.22, gas −0.13.
- **What this leaves out makes the true spread wider and more skewed.** The draws are independent (good cell traits come together, which
  fattens both tails). The tank design, the 20 m³ size, the plant class and the density limit are held. The omissions in 3d are not in it.
  The best case's ranges are partly unsourced: its 24-hour doubling has no range.

### 3d. What the cost leaves out

| Item | Direction and size | Basis |
|---|---|---|
| First-plant financing (23.6% a year) instead of the mature 17.3% | **+$2.78 Selected cells, +$0.77 best** | `humbird_plant_charge`; computed |
| Membrane life at the measured CHO throughput (450–1,200 L/m²) instead of 3,960 | **+$19 to +$64 Selected cells** | `filter_flux.md` (a sensitivity) |
| Density: Selected cells' fed-batch fallback at 27 g/L instead of 62 | +$50 (only if perfusion fails) | `no_perfusion_downside.md` |
| Medium: the model needs less than every reported perfusion run | up to 1.2 to 2.8 times more medium and filtering | back-test (3a) |
| Nutrient floor: GFI's amino-acid prices instead of the model's $1.70 | +$0.8 to +$3.4 Engineered cells, all favourable; none in Selected cells | `nutrient_floor.md` |
| Disposal of spent medium (28 L/kg in Selected cells) | small, assumed under $0.15 a kilo; not costed | no wastewater cost anywhere in the model |
| Quality control, analytics, working capital, start-up | not costed separately; partly in Humbird's labour and the capital charge | `plant_capital_crosscheck.md` |
| Scaffold and forming for structured products | +$6 a kilo for structured products (a model assumption, separate) | `post_harvest_costs.md` |
| Items that could go the other way | a cheaper plant than the model's (two published designs assume a third of Humbird's); cheaper medium | `plant_capital_crosscheck.md`; `medium_cost_gfi.md` |

### 3e. From a kilo of cells to a shelf price

The model adds a flat $5 a kilo (`markup_add`, range $3–8.7). USDA's conventional spreads are closer to proportional: the
wholesale-to-retail spread is 42–65% of the retail price (`post_harvest_costs.md`). A proportional chain,
(cost + $1 of processing) ÷ (1 − 45%), gives:

| | Cost of cells | Shelf price, flat $5 | Shelf price, proportional |
|---|---|---|---|
| Engineered cells, all favourable | $9.66 | $14.66 | $19.38 |
| Selected cells, shared-medium plant | $26.56 | $31.56 | $50.10 |
| Selected cells | $29.42 | $34.42 | $55.30 |
| **Cost of cells at parity with $12 meat** | | **$7.0** | **$5.6** (3.2 to 6.0 across shares of 42–65%) |

Which is right is open. A flat spread is plausible if the retail chain's work does not scale with the product's price. The conventional
spread does scale. **Settled 2026-11-18** (`retail_markup_form.md`): neither. The model now uses per-kg costs plus a percentage margin,
(cost + $2.5)/(1 − 28%), which gives Central a $44 shelf price and parity at $6.1; the whole-spread percentage above double-counts the
per-kg part. At the proportional rule parity needs the cost of cells to fall below about $5.6, a level no single lever reaches.

## 4. Are the costs reasonable price points?

My reading, as judgement and not as a forecast:

1. **Central ($29.42) is a fair "if these things work" number, and a poor expectation.** It assumes cells that make 0.14 mol of ammonia a kilo,
   36-hour doubling, a food-grade plant, a filter that lasts 3,960 litres a m², and perfusion at 20 m³. Given the documented ranges the
   median is about **$36**, and the middle 80% runs **$27–50**.
2. **The best case ($9.66) is an everything-works number.** Under the model's own ranges it is a 1st-percentile result. It is a bound on
   what the levers could give if all went right (`frontier.md`, after PR #32, reaches about $7, with levers each of which has low odds).
3. **Parity (a cost of cells near $7, or $5.6 on a proportional markup) is not reached by any scenario.** Under the global draws the chance
   that Central falls to $12 is under 0.1%, and the best case's is 16%.
4. **A realistic band for a first 20 m³ perfusion plant's cell cost is therefore $27–50, with the best case the lower tail.** Real
   runs so far are at $46–110 a kilo, which the model's gap of 3 to 6 times to modelled claims already leads one to expect.
5. **Perfusion at 20 m³ is itself unshown.** If it fails, the fed-batch fallback costs $41–45 at the model's density cap and $92–99 at the
   27 g/L reported (`no_perfusion_downside.md`).

## 5. What I would do

1. **Show the spread, not just the point.** Replace the scenario bands (which draw six inputs) with this global spread, and say that each
   scenario's headline is the most likely value of its inputs. A reader sees "$29, most likely about $36".
2. **Decide three defaults:** the membrane life (`filter_flux.md`), first-plant or mature financing (+$2.8 in Central), and the nutrient
   floor (`nutrient_floor.md`). Each is a judgement, and each moves Central by $2 or more.
3. **Close the medium gap in the back-test.** The model's litres per kilo are below every reported run. Either the model's waste
   assumption is optimistic or the runs were not optimised. This is the largest single source of possible bias.
4. **Treat the markup rule as a scenario switch**: flat or proportional. It decides whether parity needs $7 or $5.6.
5. **Measure what the model cannot:** the waste per kilo of a meat cell line, the life of a filter at a quarter cells by volume, and the
   doubling time of a low-waste line in suspension. They are the three biggest drivers.
6. **Keep a drift log.** `audit_history.py` reproduces the table in section 2. If the headline moves again, the pattern in section 2
   will say whether the model is converging.

## 6. Limits of this audit

- The ranges in `inputs.py` come from earlier sessions' judgement and from sources of mixed quality. A wrong range gives a wrong spread.
- The global draws are independent. The best case's doubling time has no range, so it is held.
- The comparison in 3b is not like for like: products, scales and cost definitions differ, and none is audited.
- I have not checked the shelf-price inputs beyond the USDA numbers in `post_harvest_costs.md`.
