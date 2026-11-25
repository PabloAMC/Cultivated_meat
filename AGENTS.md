# Cultivated meat: cost and market share. The edition for AI agents

This is the cultivated-meat cost and demand model written for AI agents: what it answers, how, on what inputs, how it is checked, what was tried and withdrawn, what is open, and how to change it. It is generated from the code by `agents_edition.py`; do not edit it by hand. Every number below was computed by the model when the file was written. The model asks two questions: how cheap can a kilo of cultivated meat cells plausibly get, and at that cost, how much conventional meat would cultivated meat displace? The first is a cost built from tank physics and published plant designs (fairly solid where it rests on measurements). The second depends on how people will treat a product nobody can buy yet, so it is always a band. The model makes no forecast of when any cost is reached.

Contents: 1. The question and the answer in ten lines. 2. The causal chain as functions. 3. Every input. 4. The checks. 5. Dead ends and corrections. 6. Open questions, ranked. 7. How to extend.

## 1. The question and the answer in ten lines

1. Units: every cost is US dollars of 2025 per kilo of wet cells (about 70% water) leaving the tank, at most likely values; every share is cultivated meat's long-run share of world meat and seafood sold, by weight.
2. Humbird's best estimate (2021), his fed-batch design with enhanced cells on soy hydrolysate in 20 m³ tanks: $21.00 a kilo in 2018 dollars; this model's engine at his conditions gives $26.99 in 2025 dollars, and $30.49 with what this model counts and he does not (cells killed by bubbles, cells lost at harvest, a least medium flow, the bubble protectant, slower oxygen uptake in a thick culture). From `humbird_check.page_start()` and `page_with_additions()`.
3. Humbird's optimistic design (his enhanced cells in a 20 m³ perfusion tank): $15.72. From `floor_physics.explore()` with no arguments.
4. Published cells (the best value of each trait in the published record, grown in 20 m³ batches): $316.1, and a share of 0.0045%. From `scenarios.SCENARIOS['today']`.
5. The low-lactate example (0.14 mol of ammonia a kilo, 0.42 mol of lactate per mol of glucose, a doubling every 36 hours, 2 ng a cell, perfusion in a 20 m³ tank): $48.68, and a share of 1.4%. From `scenarios.SCENARIOS['central']`.
6. The all-favourable example (every lever at its most favourable value among this model's favourable end, Humbird's design and the published cost studies, inside the model's limits; cells of 3 ng doubling every 16 hours): $6.97, and a share of 25.1% if 58.7% of meat buyers pick it at equal price, 20.5% at the model's ordinary 50.0%. From `scenarios.all_favourable()`.
7. The nutrient floor (what a kilo of cells must eat: amino acids at feed grade and the most efficient published need, glucose and other nutrients): $2.00; the medium is never charged less. From `floor_physics.feedstock(floor_physics.GOOD_CELLS)`, `nutrient_floor.py`.
8. Price parity with a $12 kilo of US minced beef or pork cuts needs cells at $6.14 or less (shelf price = (cost + per-kilo costs to the shelf) / (1 - retail margin)). From `price_ratio.parity_cost`.
9. Long-run share at equal price, once familiar: 46.4% of all choices (range 5% to 80%), which is 50.0% of meat buyers. A judgement from the literature on first-contact aversion fading, not a measurement: the input `equal_price_share`, `scenarios.meat_buyers_at_equal_price()`.
10. A 1% long-run share of world meat needs cells at $62.7 a kilo or less; 10% needs $12.7, below every set of traits tried. From `scenarios.cost_for_share`.

## 2. The causal chain as functions

Each step is one function. The examples were run when this file was generated; the outputs are real. Run them from the repository root with the repository on `PYTHONPATH`. Costs are $ per kilo of wet cells in 2025 dollars, unless said.

### Step 0. Inputs: `inputs.value(name)`, `inputs.prior(name)`, `inputs.REGISTRY`

Every number lives once in `inputs.py` as an `Input(value, unit, source, lo, hi, mode, kind, note)`. `value` gives the point value; `prior` gives the Monte Carlo prior as (kind, lo, hi, mode, note). Swap a REGISTRY entry with `dataclasses.replace` to move an input (answer_rests_on.py does this); restore it after.

```python
>>> import inputs
>>> inputs.value("media_price"), inputs.REGISTRY["media_price"].unit
(0.5, '$/L')
>>> inputs.prior("media_price")[:4]
('triangular', 0.2, 1.0, 0.5)
>>> len(inputs.REGISTRY)
615
```

### Step 1. Traits of the cells, the tank and the plant, to the settings of the engine: `scenarios.explore_kwargs(choice)`

A reference point is a `choice`: a dict of eleven switches (mode, cells, growth, plant, gas, tricks, shape, losses, restart, gf, medium) plus extras. `explore_kwargs` turns it into the keyword arguments of the engine: doubling time in hours (`doubling_h`), cell mass in pg (`mass_pg`), ammonia in mol per kilo (`nh3_kg`), lactate in mol per mol of glucose (`lac_yield`), tank size in m³ (`vessel_m3`, 20 when not given), medium price in $ a litre (`medium_price`), and so on.

```python
>>> import scenarios as S
>>> choice = S.SCENARIOS["central"].choice
>>> kw = S.explore_kwargs(choice)
>>> {k: kw[k] for k in ("doubling_h", "mass_pg", "nh3_kg", "lac_yield", "mode", "plant", "medium_price", "nh3_limit", "lac_limit")}
{'doubling_h': 36.0, 'mass_pg': 2000.0, 'nh3_kg': 0.14, 'lac_yield': 0.42, 'mode': 'perfusion', 'plant': 'sanitary', 'medium_price': 0.2, 'nh3_limit': 4.0, 'lac_limit': 35.0}
```

### Step 2. Settings to the cost of a kilo of cells: `floor_physics.explore(**kw)`

The engine. Oxygen and CO₂ transfer, waste build-up, salt strength and the cell filter set the density the tank holds (`density`, g/L) and what limits it (`limit`); density and growth rate set the output; the output spreads the plant's yearly charge, labour and utilities; the waste the cells make sets the litres of medium. It returns a dict; `total` is the cost, and the lines below add up to it with the smaller items (filters, protectant, gas). With no arguments it is Humbird's optimistic design.

```python
>>> import floor_physics as fp
>>> r = fp.explore(**kw)
>>> round(r["total"], 2), round(r["density"]), r["limit"], round(r["medium_l"], 1)
(48.68, 168, 'what the column can strip safely', 38.8)
>>> {k: round(float(r[k]), 2) for k in ("feedstock", "growth_factors", "consumables", "utilities", "labour", "capital")}
{'feedstock': 7.94, 'growth_factors': 0.0, 'consumables': 25.37, 'utilities': 1.38, 'labour': 3.22, 'capital': 10.78}
>>> round(fp.explore()["total"], 2)
15.72
```

### Step 3. Cost to shelf price and price ratio: `price_ratio.shelf_price`, `ratio`, `parity_cost`

shelf price = (cost + markup_add) / (1 - retail_margin); R = shelf price / price of the conventional meat it copies. Cuts (fillets, steaks) are part plant protein: `price_ratio.structured_cost(cells)`.

```python
>>> import price_ratio as PR
>>> cost = r["total"]
>>> round(PR.shelf_price(cost), 2)
71.09
>>> round(PR.ratio(cost, inputs.value("markup_add"), inputs.value("p_conv")), 2)
5.92
>>> round(PR.parity_cost(inputs.value("markup_add"), inputs.value("p_conv")), 2)
6.14
```

### Step 4. Price ratio to choice: `market_share.share(R, DemandParams(), which="x_meat")`

A two-segment (mainstream and ethical) flat logit over four products (conventional meat, plant-based meat, cultivated meat, a whole-food option), with shoppers differing in how much they like cultivated meat (a Student's t spread) and a price-insensitive minority. Calibrated so that plant-based meat takes its observed 0.4% of meat by volume. `which="x_meat"` returns cultivated meat's share of the meat sold, x / (x + c), long run, at the reference (US) income and a $12 meat.

```python
>>> from market_share import DemandParams, share
>>> pr = DemandParams()
>>> [round(share(R, pr, which="x_meat") * 100, 3) for R in (1.0, 1.5, 2.0, 3.0)]
[49.998, 32.834, 19.551, 6.946]
```

### Step 5. Every meat type and region: `meat_market.penetration(market, cost, income=..., pr=...)`

Repeats step 4 for each meat type at its own local price and the region's income, turns cells into cuts, lowers conventional meat's price as it loses sales, gives closed markets none, and adds up by volume and by value. It returns (rows, share by volume, share by value) as fractions. `scenarios.shares(cost)` wraps it for three regions, in percent.

```python
>>> import meat_market as mm
>>> rows, vol, val = mm.penetration(mm.MARKETS["global"], cost, income=mm.REGION_INCOME["global"], pr=pr)
>>> round(vol * 100, 3), round(val * 100, 3)
(1.429, 1.69)
>>> {k: round(v, 3) for k, v in S.shares(cost).items()}
{'global': 1.429, 'us': 1.902, 'eu': 2.485}
```

### Step 6. Over time: `adoption_timing.years_for_cost(cost)`

Bass diffusion for the rollout and first-contact wariness fading towards the long-run attitude. Years to 90% of the long-run share, at the point value of the fading rate and at the fast and slow ends of its range.

```python
>>> import adoption_timing as AT
>>> AT.years_for_cost(cost)
(23, 16, 51)
```

### Shortcuts

- `scenarios.run(choice)`: steps 1 and 2, with the tank design chosen; `scenarios.SCENARIOS` holds the reference points, `scenarios.LADDER` their order.
- `scenarios.bands(choice)`: the Monte Carlo band over the unmeasured estimates (cost and share).
- `scenarios.cost_for_share(target_percent)`: the cost of cells that gives a long-run world share.
- `answer_rests_on.cost_drivers()`, `demand_drivers()`: every ranged input moved to each end, one at a time.


## 3. Every input

There are 615 inputs, each defined once in `inputs.py` and listed in full, with its whole source and note, in `inputs.json`. The evidence class is read mechanically from the source tag (the text in its first square brackets); it is not a review of the evidence. The inputs that matter are described by hand in `answer_rests_on.EVIDENCE` (the column "where the value comes from" below).

| evidence class | what it means | inputs |
|---|---|---|
| setting | a setting of the model or a design choice, not an estimate | 13 |
| judgement | a judgement or assumption of the model, not measured | 137 |
| fitted | fitted to data: the model solves it so that it reproduces an observed figure | 10 |
| derived | derived by arithmetic from published figures | 50 |
| company | a company's or a vendor's figure, not peer reviewed | 60 |
| published_partly | a published figure, read only in part (a snippet, an abstract or a second-hand citation) | 49 |
| published | a published or observed figure (a paper, a report read in full, a market price, official statistics) | 295 |
| untagged | no source tag | 1 |

### The inputs that move the cost most

Every input with a range moved to each end, one at a time (`answer_rests_on.cost_drivers()`); kept when it moves the low-lactate example's or the all-favourable example's cost by $1 a kilo or more. Largest swing in the low-lactate example first. Marked **[cost]** in the full list below.

| input | its range (model's value) | Low-lactate example, $/kg | The low-lactate example's share of world meat | All-favourable example, $/kg | where the value comes from | in the uncertainty band? |
|---|---|---|---|---|---|---|
| Litres a m² of cell filter passes before it is replaced | 900–5500 L/m2 (2415) | $86.9 to $35.9 | 0.5% to 2.1% | $7.0 to $7.0 | derived from pharma runs (fouled in 4.5 days to lasted 30); no meat-cell run; probably the generous end (median about 1,500), and read with the membrane price | yes |
| Ammonia the cells tolerate in the tank | 2–8 mmol/L (4) | $89.0 to $43.8 | 0.5% to 1.6% | $7.0 to $6.9 | the evidence note's median, 3.5–4 mmol/L (80% interval 2–8): meat-relevant cells measured lose 10–55% of growth at 2.5–5, meat-cell processes hold 2–3, none measured at density | yes |
| Ammonia the cells of the low-lactate example make per kilo grown | 0.04–0.25 mol/kg wet (0.14) | $44.5 to $80.4 | 1.6% to 0.6% | $7.0 to $7.0 | measured once, in bovine cells with glutamine replaced (Hubalek 2023): 'more than 5-fold' below the 0.70 with glutamine | yes |
| Lactate the cells tolerate in the tank | 20–50 mmol/L (35) | $70.3 to $48.7 | 0.8% to 1.4% | $7.0 to $7.0 | Cultivated Meat (book), Table 2, citing Hassell 1991; Pasitka 2024; Humbird 2021, judgement | yes |
| Lactate the cells of the low-lactate example make per mol of glucose | 0.39–0.6 mol lactate / mol glucose (0.42) | $48.7 to $65.5 | 1.4% to 0.9% | $7.0 to $7.0 | waste_tricks_sizing.md | **no** |
| Culture whose cells bursting bubbles kill, per volume of gas passed | 0.0001–0.0012 L of culture per L of gas (0.0004) | $45.7 to $58.9 | 1.5% to 1.1% | $6.5 to $8.7 | Jobses, Martens, Tramper 1991, read in full | yes |
| Salt strength the cells tolerate (osmolality) | 350–450 mOsm/kg (415) | $57.9 to $48.7 | 1.1% to 1.4% | $8.3 to $7.0 | CHO measurements (`perfusion_rate_osmolality.md`) | no: moves the all-favourable example's median by about $0.1, at forty times the computing time |
| Price of the bubble protectant (poloxamer 188), bought by the tonne | 5–100 $/kg (30) | $46.7 to $54.1 | 1.5% to 1.2% | $6.4 to $8.7 | assumed: only catalogue prices ($230–260/kg) found | yes |
| Yearly charge on the plant's capital (financing and recovery) | 0.123–0.236 of TCI per yr (0.173) | $45.6 to $52.6 | 1.6% to 1.3% | $6.4 to $7.7 | derived from Humbird's financing, at a mature industry's rates | yes |
| Price of cell-filter membrane | 1050–1450 $/m2 (1450) | $42.4 to $48.7 | 1.7% to 1.4% | $7.0 to $7.0 | Humbird's ATF price; retail modules a quarter less | yes |
| Least medium flow the cells need for everything but ammonia and lactate | 3.7–18.5 mL per g wet cells per day (7.5) | $48.7 to $54.5 | 1.4% to 1.2% | $7.0 to $7.0 | judgement within CHO measurements | yes |
| Dose of bubble protectant in the medium | 1–5 g/L (2) | $47.5 to $52.2 | 1.5% to 1.3% | $6.6 to $8.1 | dense pharma cultures (`gas_flow_cap.md`) | yes |
| Staff a plant in perfusion needs, against a fed-batch plant | 1.4–3.9 x the fed-batch crew (2) | $47.7 to $51.7 | 1.5% to 1.3% | $6.7 to $7.9 | Humbird 2021; CE Delft 2021; SuperMeat 2024, derived | **no** |
| Amino acids a kilo of cells takes up (the nutrient floor) | 0.2–0.65 kg amino acids/kg wet (0.232) | $48.7 to $51.5 | 1.4% to 1.3% | $6.7 to $10.0 | GFI's eight estimates, 200–650 g; the model takes the most efficient (`nutrient_floor.md`) | no: a trait of the cells, as glucose use is; the all-favourable example takes the efficient end |
| How the cost of medium preparation equipment rises with the medium passed (exponent) | 0.6–1 exponent (0.6) | $48.7 to $51.1 | 1.4% to 1.3% | $7.0 to $7.4 | assumed | **no** |
| Weight of one cell (every kind of cells since 2026-11-19) | 1000–3000 pg wet per cell (2000) | $50.1 to $47.9 | 1.4% to 1.5% | $7.0 to $7.0 | judgement between the 1.0–1.75 ng reported for chicken cells and Humbird's 3 ng | yes |
| Rise in plant construction costs since 2018 | 1.17–1.4 x (1.33) | $47.5 to $49.2 | 1.5% to 1.4% | $6.8 to $7.1 | construction cost index, 2024 estimated | partly: the plant's cost is drawn, not this index |
| CO₂ level at which the culture leaves the stripping column | 20–70 mbar (55) | $50.5 to $49.3 | 1.4% to 1.4% | $7.2 to $7.0 | design choice | **no** |
| Price of amino acids (the nutrient floor) | 5–11.59 $/kg amino acids (6.36) | $48.7 to $49.9 | 1.4% to 1.4% | $6.6 to $8.3 | GFI's feed-grade mean of 22, to low food-grade (`nutrient_floor.md`) | yes |

*Left out: The gas flow the tank takes is a scenario switch (2, 4 or 6 mm/s). The input of that name is also the reference speed of Humbird's oxygen figure, so moving it alone rescales that figure ($48.56 to $48.68 in the low-lactate example) without changing any tank; it is left out.*
*Left out: Maturation, the hours the cells spend in the tank without growing before harvest, is a choice of product, not an estimate. The products near market are bulk cell mass and take none; 4 to 28 days to mature muscle or fat would take the low-lactate example from $48.68 to $75.46 (4 days) or $232.75 (28 days). It is a lever on the page; it is left out here.*
*Also left out: the settings of the scenario switches themselves (medium price, growth factors bought, runs lost, gas flow, doubling time, restart time). "What to prioritise" shows what each switch is worth.*

### The inputs that move the share most

The demand inputs moved the same way (`answer_rests_on.demand_drivers()`); kept when they move the share by 0.2 points at the low-lactate example's cost or 2 at the all-favourable example's. Largest at the all-favourable example first. Marked **[share]** below.

| input | its range (model's value) | share at the low-lactate example's cost | share at the all-favourable example's cost | where the value comes from | in the uncertainty band? |
|---|---|---|---|---|---|
| Share of buyers who choose cultivated meat at equal price, once familiar | 0.05 to 0.8 of all choices (0.464) | 0.09% to 4.3% | 2.2% to 42.9% | a judgement: an even split for meat buyers, the neutral start where no good data exist (since 2026-11-24; 13% of all choices before); the literature review puts the 10th, 50th and 90th percentiles at 2%, 10% and 35% (`what_drives_choice.md`) | yes |
| How wary people are of a novel food, in the long run | -2 to 1 utils (0) | 0.6% to 2.1% | 11.2% to 26.4% | a judgement on long-run behaviour | no: part of the share at equal price, which is drawn |
| Whether people see cultivated meat as healthier or less healthy | -0.5 to 0.5 norm (0) | 0.9% to 2.2% | 14.7% to 27.3% | a scenario dial: no data | no: part of the share at equal price, which is drawn |
| How much more price-sensitive cultivated meat is than meat in general | 4 to 11 x (8.5) | 3.0% to 1.0% | 28.8% to 18.0% | bracketed by data on close substitutes | yes |
| Retailer's gross margin, as a share of the shelf price | 0.15 to 0.4 of shelf price (0.28) | 1.8% to 1.1% | 25.8% to 15.2% | US meat-department margins (28–32%) and French supermarket data | yes |
| Price elasticity of meat demand | -1.4 to -0.5 elasticity (-0.9) | 0.9% to 2.5% | 17.2% to 26.7% | scanner-data meta-analysis | yes |
| How fully mainstream buyers credit cultivated meat's taste | 0.6 to 1 fraction (1) | 0.6% to 1.4% | 11.2% to 20.5% | a scenario dial | no: part of the share at equal price, which is drawn (left the bands on 2026-11-20) |
| Cost of assembling a cut, beyond what mince pays | 0.5 to 7 $/kg (2) | 1.5% to 1.3% | 23.4% to 14.3% | analogues, no study of cultivated meat: plant-protein extrusion, surimi forming, binder prices (`structuring_cost.md`) | yes |
| Value mainstream buyers put on meat without slaughter | 0 to 1 utils (0) | 1.4% to 2.3% | 20.5% to 27.3% | a scenario dial: surveys disagree | no: part of the share at equal price, which is drawn |
| Per-kg costs from cells to the shop shelf (forming, packing, cold chain), $ per kg | 1.5 to 3.5 $/kg (2.5) | 1.5% to 1.4% | 23.8% to 17.7% | fitted to USDA ERS meat spreads, plus forming | yes |
| How price sensitivity falls with income | 0 to 1 exponent (0.32) | 1.8% to 0.9% | 22.3% to 17.6% | USDA demand estimates | no: each value re-solves the demand model's calibration |
| Whether a price above meat's hurts more than a price below helps (off by default) | 1 to 2.25 ratio (1) | 1.4% to 1.2% | 20.5% to 16.3% | an alternative model of price, not a measured value; with it, part of the price response moves from dollars to the ratio to meat's price | no: each value re-solves the demand model's calibration |
| Share of a cut that is plant protein, not cells | 0.1 to 0.5 kg/kg (0.2) | 1.5% to 1.4% | 21.5% to 17.9% | assumed: the cuts sold or approved so far are 10–30% cells, and no mostly-cell cut has been shown with the texture of meat (`structuring_cost.md`) | yes |
| Price of everyday meat | 10 to 14 $/kg (12) | 1.7% to 1.3% | 21.8% to 19.7% | market prices | no: an observed price |
| How much shoppers differ in liking cultivated meat | 3.3 to 3.9 utils (3.55) | 1.3% to 1.6% | 19.7% to 21.6% | fitted to the one random-parameter choice experiment, premium real meats and farmed salmon, jointly | no: the share at equal price is set given it |
| Share of mainstream meat meals where shoppers choose a whole-food plant protein instead of meat | 0.04 to 0.14 share (0.06) | 1.4% to 1.7% | 20.2% to 21.9% | assumed, SOFT | **no** |
| How much more the price-insensitive shoppers like cultivated meat than other shoppers, utils | -2 to 2 utils (0) | 0.7% to 2.7% | 20.0% to 21.3% | two latent-class studies, read in utils: no more hostile than other shoppers (`demand_checks.md` section 7) | no: the share at equal price is set given it |
| Weight on the price compared with meat's | 0.5 to 1.5 utils per unit ratio (1) | 1.4% to 1.6% | 21.2% to 19.9% | judgement: how much of the price response is a ratio to meat's price rather than dollars | no: each value re-solves the demand model's calibration |
| Share of shoppers who respond much less to price than the others | 0.08 to 0.15 of all shoppers (0.08) | 1.4% to 2.6% | 20.5% to 21.7% | latent-class studies: 15-35% in stated choices, probably 8-15% in purchases; fitted within that to the demand checks (`demand_checks.md` section 7) | no: the share at equal price is set given it |
| How strongly those price-insensitive shoppers respond to price, times other shoppers' response | 0.1 to 0.25 x other shoppers' (0.11) | 1.6% to 0.4% | 20.5% to 20.2% | 4-10 times between groups in purchases; fitted within that to the demand checks (`demand_checks.md` section 7) | no: the share at equal price is set given it |

### All inputs

Value, unit, Monte Carlo range (triangular lo, mode, hi unless marked lognormal: median, 5th and 95th percentiles), evidence class and source tag. Full sources and notes are in `inputs.json`.

| input | value | unit | range | evidence | moves | source tag |
|---|---|---|---|---|---|---|
| `markup_add` | 2.5 | $/kg | 1.5, 2.5, 3.5 | judgement | **[share]** | USDA ERS fit, judgement |
| `retail_margin` | 0.28 | of shelf price | 0.15, 0.28, 0.4 | published_partly | **[share]** | Progressive Grocer ~2011 (snippet); Cooperative Grocer 2016 (read); OFPM 2025 via Reussir (read) |
| `p_conv` | 12 | $/kg | 10, 12, 14 | published | **[share]** | market |
| `years` | 30 | years | fixed | judgement |  | assumed |
| `media_intensity` | 30.5 | L/kg wet | fixed | company |  | SuperMeat |
| `media_price` | 0.5 | $/L | 0.2, 0.5, 1 | company |  | SuperMeat |
| `efficiency` | 1 | x media-use | 0.25, 1, 1 | company |  | SuperMeat |
| `overhead` | 19.1 | $/kg | 13.5, 19.1, 37.1 | derived |  | SuperMeat, capital restated |
| `aa_intensity` | 0.232 | kg amino acids/kg wet | 0.2, 0.232, 0.65 | company | **[cost]** | GFI Dec 2025, read in full; research_notes/nutrient_floor.md; chosen 2026-11-19 |
| `aa_bulk_price` | 6.36 | $/kg amino acids | 5, 6.36, 11.59 | company | **[cost]** | GFI Dec 2025, Table 1, read in full |
| `glucose_intensity` | 0.311 | kg/kg wet | fixed | derived |  | derived 2026-11-21: floor_physics.glucose_balance for Humbird's enhanced cell (3 ng, 24 h, 0.054 mol of ammonia a kilo) making no lactate: 1.724 mol x 0.180 kg |
| `glucose_price` | 0.4 | $/kg | fixed | company |  | GFI25 |
| `other_nutrients_floor` | 0.4 | $/kg | fixed | judgement |  | assumed, 2026-11-19 |
| `plant_floor` | 13.5 | $/kg | fixed | published |  | floor_physics; 13.8 until 2026-11-21, when the building's power began to follow its floor and class |
| `plant_floor_lo` | 8.5 | $/kg | fixed | published |  | floor_physics; 8.76 until 2026-11-21 (the building's power by floor and class) |
| `plant_floor_hi` | 20.3 | $/kg | fixed | published |  | floor_physics |
| `plant_charge_mature` | 0.173 | of TCI per yr | 0.123, 0.173, 0.236 | derived | **[cost]** | Humbird-R, derived |
| `humbird_plant_cost` | 14.5 | $/kg | fixed | published |  | Humbird |
| `humbird_tci_fedbatch` | 3.28e+08 | $ | fixed | published |  | Humbird |
| `humbird_output_fedbatch` | 6.8e+06 | kg wet/yr | fixed | published |  | Humbird |
| `humbird_plant_charge` | 0.236 | of TCI per yr | fixed | published |  | Humbird |
| `believer_capex` | 1.2335e+08 | $ | fixed | company |  | Believer |
| `believer_capacity` | 1e+07 | kg/yr | fixed | company |  | Believer |
| `eff_best` | 0.25 | x media-use | fixed | judgement |  | assumed |
| `cleanroom_cost` | 1.6 | $/kg | fixed | derived |  | Humbird-R, derived |
| `gr_tau_ref` | 24 | h | fixed | judgement |  | assumed |
| `gr_time_share` | 0.8 | of overhead | 0.5, 0.8, 1 | judgement |  | assumed |
| `gr_tau_star` | 48 | h | 30, 48, 96 | judgement |  | assumed |
| `gr_bp_time_share` | 0.2 | of by-product | 0, 0.2, 0.5 | judgement |  | assumed |
| `gr_next_level` | 0.6 | x volume | 0.25, 0.6, 1 | judgement |  | assumed |
| `gr_nut_time_share` | 0.3 | of nutrient need | 0.1, 0.3, 0.6 | judgement |  | assumed |
| `gr_death_rate` | 0.002 | 1/h | 0, 0.002, 0.005 | judgement |  | assumed |
| `pf_capex_escalation` | 1.33 | x | 1.17, 1.33, 1.4 | published | **[cost]** | pf-tea |
| `pf_opex_escalation` | 1.28 | x | fixed | published |  | pf-tea |
| `cpi_u_2018` | 251.107 | index | fixed | published |  | BLS CPI-U annual average, series CUUR0000SA0, BLS API v2, fetched 2026-11-20 |
| `cpi_u_2019` | 255.657 | index | fixed | published |  | BLS CPI-U annual average, series CUUR0000SA0, BLS API v2, fetched 2026-11-20 |
| `cpi_u_2020` | 258.811 | index | fixed | published |  | BLS CPI-U annual average, series CUUR0000SA0, BLS API v2, fetched 2026-11-20 |
| `cpi_u_2021` | 270.97 | index | fixed | published |  | BLS CPI-U annual average, series CUUR0000SA0, BLS API v2, fetched 2026-11-20 |
| `cpi_u_2022` | 292.655 | index | fixed | published |  | BLS CPI-U annual average, series CUUR0000SA0, BLS API v2, fetched 2026-11-20 |
| `cpi_u_2023` | 304.702 | index | fixed | published |  | BLS CPI-U annual average, series CUUR0000SA0, BLS API v2, fetched 2026-11-20 |
| `cpi_u_2024` | 313.689 | index | fixed | published |  | BLS CPI-U annual average, series CUUR0000SA0, BLS API v2, fetched 2026-11-20 |
| `cpi_u_2025` | 321.943 | index | fixed | published |  | BLS CPI-U annual average, series CUUR0000SA0, BLS API v2, fetched 2026-11-20 |
| `pf_cell_mass_pg` | 3000 | pg wet | fixed | published |  | Humbird-R |
| `cr_mass_measured_max_pg` | 3000 | pg wet | fixed | published |  | 2026-11-20: the larger of Humbird's 3 ng and the heaviest credible measurement of a meat cell growing in suspension |
| `pf_cell_mass_small_pg` | 550 | pg wet | fixed | derived |  | Pasitka, derived |
| `pf_doubling_h` | 24 | h | fixed | published |  | Humbird-R |
| `pf_doubling_slow_h` | 61 | h | fixed | published |  | Pasitka |
| `pf_power_coef` | 0.148 | pW/pg^0.75 | fixed | published |  | Humbird-R |
| `pf_heat_per_o2` | 483 | kJ/mol O2 | fixed | published |  | Humbird-R |
| `pf_x_visc` | 258 | g wet/L | fixed | published |  | Humbird-R |
| `pf_x_unperfused` | 120 | g wet/L | 50, 120, 150 | published |  | Humbird-R |
| `pf_batch_end_x` | 1.3 | x the steady-state limit | 1, 1.3, 2 | judgement |  | Humbird-R, derived; judgement |
| `pf_batch_half_x` | 3 | x the steady-state limit | 2, 3, 5 | judgement |  | ammonia_tolerance_and_filter_life.md, judgement |
| `pf_x_co2_20m3` | 120 | g wet/L | fixed | published |  | Humbird-R |
| `pf_otr_cap` | 29 | mmol O2/L/h | 13, 29, 50 | published |  | Humbird-R |
| `pf_working_volume` | 0.8 | of vessel | fixed | published |  | Humbird-R |
| `pf_uptime` | 0.91 | of year | fixed | published |  | Humbird-R |
| `pf_uptime_realistic` | 0.85 | of year | 0.75, 0.85, 0.91 | judgement |  | assumed |
| `pf_draw_fraction` | 0.5 | of tank | 0.3, 0.5, 0.8 | judgement |  | assumed |
| `pf_turnaround_h` | 10 | h | fixed | published |  | Humbird-R |
| `pf_mature_h` | 0 | h | 0, 0, 672 | company |  | GOOD Meat, Believer, Wildtype and Vow regulatory filings: bulk cell mass, no maturation |
| `pf_fedbatch_doublings` | 2 | doublings | fixed | published |  | Humbird-R |
| `pf_capex_aseptic_fedbatch` | 683 | $k/m3 | fixed | published |  | Humbird-R |
| `pf_capex_aseptic_perfusion` | 3450 | $k/m3 | fixed | published |  | Humbird-R |
| `pf_capex_pasitka_large` | 810 | $k/m3 | fixed | published |  | Pasitka |
| `pf_capex_no_cleanroom` | 611 | $k/m3 | fixed | derived |  | Humbird-R, derived |
| `pf_capex_retention` | 89 | $k/m3 | 0, 89, 460 | derived |  | Pasitka SI Tables S1 and S4, derived |
| `pf_run_days` | 33 | days | fixed | published |  | Humbird-R |
| `pf_hazard_pharma` | 0.002 | per day | fixed | derived |  | research pass, derived |
| `pf_blend_filler_price` | 3 | $/kg | fixed | published |  | Pasitka |
| `pf_medium_l_floor` | 8 | L/kg | fixed | derived |  | Humbird-R, derived |
| `pf_nh3_efficient` | 0.054 | mol/kg wet | fixed | derived |  | Humbird-R, derived |
| `pf_nh3_wild` | 0.952 | mol/kg wet | fixed | derived |  | Humbird-R, derived |
| `pf_lac_efficient` | 0.558 | mol/kg wet | fixed | derived |  | Humbird-R, derived |
| `pf_lac_wild` | 6.45 | mol/kg wet | fixed | derived |  | Humbird-R, derived |
| `pf_glc_kg` | 1.116 | mol glucose/kg wet | 0.67, 1.116, 3.6 | derived |  | Humbird-R, derived |
| `pf_glc_anabolic` | 0.884 | mol glucose/kg wet | fixed | derived |  | Humbird-R, reaction 2.11, derived |
| `pf_sorbent_q` | 0.15 | mmol/g = mol/kg | 0.1, 0.15, 0.25 | derived |  | derived, not measured; waste_tricks_sizing.md A2 |
| `pf_sorbent_price` | 5 | $/kg | 0.05, 5, 20 | judgement |  | assumed |
| `pf_sorbent_cycles` | 1 | uses | 1, 1, 50 | judgement |  | assumed |
| `pf_nh3_limit` | 5 | mmol/L | 2, 5, 10 | published |  | Humbird-R |
| `pf_lac_limit` | 50 | mmol/L | 20, 50, 50 | published |  | Humbird-R |
| `pf_maintenance_share` | 0.5 | of O2 uptake | 0.31, 0.5, 1 | judgement |  | GFI 2025 / Miller 1987, judgement |
| `pf_mix_ratio_20m3` | 0.97 | - | fixed | derived |  | Humbird-R, derived |
| `pf_osm_base` | 300 | mOsm/kg | fixed | judgement |  | typical |
| `pf_osm_limit` | 415 | mOsm/kg | 350, 415, 450 | derived | **[cost]** | Humbird-R, derived; Zhu 2005 |
| `pf_ph` | 7.2 | pH | 6.9, 7.2, 7.4 | judgement |  | typical |
| `pf_pk1` | 6.1 | pK | fixed | published |  | textbook |
| `pf_co2_henry` | 0.0246 | mmol/L per mbar | fixed | published |  | textbook |
| `pf_hco3_base` | 24.6 | mmol/L | fixed | derived |  | derived |
| `pf_min_perfusion` | 7.5 | mL per g wet cells per day | 3.7, 7.5, 18.5 | judgement | **[cost]** | judgement within a measured range |
| `pf_cell_density` | 1.036 | g/mL | 1.03, 1.036, 1.06 | published |  | calibrated; research_notes/co2_sparging_settling.md |
| `pf_medium_density` | 1.007 | g/mL | fixed | judgement |  | typical |
| `pf_medium_viscosity` | 0.75 | mPa s | fixed | judgement |  | typical |
| `pf_plate_gap` | 1 | cm | fixed | judgement |  | typical |
| `pf_anoxia_min` | 60 | min | 10, 60, 90 | published |  | research_notes/co2_sparging_settling.md |
| `pf_clump_packing` | 0.6 | - | fixed | judgement |  | assumed |
| `pf_pco2_limit` | 100 | mbar | 80, 100, 250 | published |  | Humbird-R |
| `pf_gas_velocity` | 0.006 | m/s | 0.002, 0.005, 0.009 | published |  | Humbird-R |
| `pf_aspect` | 1.6 | H/T | 0.8, 1.6, 2.5 | published |  | Humbird-R |
| `pf_rq` | 1.204 | mol CO2/mol O2 | fixed | derived |  | Humbird-R, derived |
| `pf_rq_lipid` | 0.2381 | mol CO2/mol O2 | fixed | derived |  | Humbird-R, derived |
| `pf_fat_kg` | 0.045 | kg/kg wet | fixed | derived |  | Humbird-R, derived |
| `pf_fat_price` | 1.5 | $/kg | 1, 1.5, 20 | judgement |  | assumed |
| `ge_atp_per_o2` | 5 | mol ATP/mol O2 | fixed | published |  | textbook |
| `pf_protectant_dose` | 2 | g/L | 1, 2, 5 | published | **[cost]** | gas_flow_cap.md |
| `pf_protectant_price` | 30 | $/kg | 5, 30, 100 | judgement | **[cost]** | assumed |
| `pf_o2_microbial` | 1 | switch | fixed | setting |  | model choice, 2026-11-15 |
| `pf_antifoam_otr` | 0.75 | - | 0.5, 0.75, 1 | judgement |  | judgement, effect reported |
| `pf_co2_strip_eff` | 0.9605 | - | fixed | published |  | calibrated |
| `pf_o2_purity` | 0.9 | mol/mol | fixed | published |  | Humbird-R |
| `pf_back_pressure` | 1.33 | bar | fixed | published |  | Humbird-R |
| `pf_o2_price` | 0.15 | $/kg O2 | 0.1, 0.15, 0.33 | published |  | Humbird-R |
| `ge_d_co2` | 2.5e-09 | m2/s | fixed | published |  | textbook, scaled |
| `ge_d_o2` | 2.8e-09 | m2/s | fixed | published |  | textbook, scaled |
| `ge_o2_henry` | 0.001 | mmol/L per mbar | fixed | published |  | textbook |
| `ge_do_setpoint` | 0.05 | mmol/L | fixed | judgement |  | typical |
| `ge_o2_bar` | 1 | bar | 1, 1, 2 | judgement |  | assumed |
| `ge_buffer` | 0 | mmol/L per pH unit | 0, 0, 5 | judgement |  | assumed |
| `ge_buffer_medium` | 0.47 | mmol/L per pH unit | fixed | published |  | textbook arithmetic |
| `ge_beta_i` | 15 | mmol/L per pH unit of cell water | 10, 15, 30 | published_partly |  | search snippet and memory |
| `ge_cell_water` | 0.7 | of cell mass | fixed | published |  | Humbird-R |
| `ge_ed_volt` | 2 | V per proton | fixed | published |  | memory, unverified |
| `ge_filtrate_flux` | 3.8 | L per m2 per h | fixed | company |  | Humbird-R; vendor size guide, snippet |
| `ge_atf_area` | 11 | m2 | fixed | company |  | vendor size guide, snippet |
| `ge_pk_area` | 250 | m2/m3 | fixed | company |  | vendor designation |
| `ge_pk_angle` | 45 | degrees | fixed | company |  | vendor designation |
| `ge_pk_side` | 0.0187 | m | fixed | derived |  | Wang 2015 thesis, Table 5.1, full text; derived |
| `ge_pk_ce` | 0.9 | - | fixed | judgement |  | Rocha, Bravo and Fair 1996; form read in Wang 2015, value from memory |
| `ge_pk_load` | 40 | m3/m2/h | 10, 40, 80 | setting |  | design choice |
| `ge_surface_tension` | 0.05 | N/m | fixed | judgement |  | assumed |
| `ge_col_pout` | 55 | mbar | 20, 55, 70 | setting | **[cost]** | design choice |
| `ge_loop_transit` | 8 | s | 4, 8, 20 | judgement |  | assumed |
| `ge_passes_tested` | 15 | tank volumes per hour | 15, 15, 24 | published |  | Clincke et al. 2013, read in full |
| `ge_col_gas_out` | 20 | mbar | fixed | setting |  | design choice |
| `ge_col_gas_in` | 0.4 | mbar | fixed | published |  | textbook |
| `ge_loop_volume` | 0.5 | m3 | 0.2, 0.5, 2 | setting |  | design choice |
| `ge_paul_dph` | 0.37 | pH units | fixed | published_partly |  | Paul et al. 2020, PMC7401239, full text via a summary |
| `ge_paul_share` | 0.075 | of volume | fixed | published |  | Paul et al. 2020, as above |
| `ge_col_head_extra` | 4 | m | fixed | judgement |  | assumed |
| `ge_col_extra_height` | 2.5 | m | fixed | judgement |  | assumed |
| `ge_col_wall` | 0.006 | m | fixed | published |  | textbook rule |
| `ge_cepci_2014` | 1.39 | x | fixed | published |  | pf-tea basis |
| `ge_o2_sweep_purity` | 0.9 | mol/mol | fixed | published |  | Humbird-R |
| `ge_o2_price` | 0.15 | $/kg O2 | fixed | published |  | Humbird-R |
| `ge_lime_price` | 0.24 | $/kg | fixed | published_partly |  | USGS Mineral Commodity Summaries 2025, lime, search snippet |
| `ge_lime_use` | 0.7 | - | fixed | judgement |  | assumed |
| `ge_p_top_base` | 0.33 | bar gauge | fixed | published |  | Humbird-R |
| `ge_sparge_o2` | 0.9 | mol/mol | fixed | published |  | Humbird-R |
| `ge_kla_20m3` | 26.4 | 1/h | fixed | derived |  | Humbird-R, derived |
| `ge_mix_time_20m3` | 141 | s | fixed | derived |  | Humbird-R, derived |
| `ge_stir_power` | 43 | W/m3 | fixed | derived |  | Humbird-R, derived |
| `ge_nozzle_velocity` | 3 | m/s | fixed | judgement |  | assumed |
| `ge_co2_frac` | 0.5 | - | 0.3, 0.5, 0.8 | setting |  | design choice |
| `ge_sweep_pco2` | 10 | mbar | fixed | setting |  | design choice |
| `ge_bore_mm` | 0.5 | mm | 0.5, 0.5, 1 | published |  | Clincke et al. 2013, read in full |
| `ge_shear` | 1000 | 1/s | 500, 1000, 3400 | published |  | Clincke et al. 2013, read in full |
| `ge_wall_um` | 100 | um | fixed | judgement |  | assumed |
| `ge_pdms_co2` | 3250 | Barrer | fixed | published_partly |  | memory; search results give 3,190-3,970 |
| `ge_pdms_o2` | 600 | Barrer | fixed | company |  | vendor data sheet, search result |
| `ge_headloss_x` | 2 | x | fixed | judgement |  | assumed |
| `ge_pump_eff` | 0.6 | - | fixed | judgement |  | assumed |
| `ge_power_price` | 0.08 | $/kWh | fixed | judgement |  | assumed |
| `ge_cost_m2` | 200 | $/m2 | 80, 200, 1480 | published |  | distributor listings, Nov 2026 |
| `ge_life_y` | 2 | years | 0.1, 2, 5 | judgement |  | judgement |
| `ge_install_x` | 3 | x | fixed | published_partly |  | CE Delft 2021, via research_notes/plant_capital_crosscheck.md |
| `ge_pump_cost` | 30000 | $ | fixed | judgement |  | assumed |
| `ge_pump_flow` | 300 | m3/h | fixed | judgement |  | assumed |
| `ge_spargers` | 1 | spargers | fixed | published |  | Humbird-R, Sect. 2.3 |
| `ge_micro_o2_x` | 4 | x drilled holes | 4, 4, 20 | published_partly |  | research_notes/gas_flow_cap.md: 'Oxygen transfer per unit of gas 4-20 times higher', ref. 39 abstract and a secondary source |
| `ge_micro_kill_x` | 10 | x drilled holes | 5, 10, 20 | published |  | research_notes/gas_flow_cap.md: 'Cell damage per unit of gas: about ten times higher', section 1 |
| `ge_sparger2_k` | 41 | $k installed per tank | 10, 41, 82 | judgement |  | Humbird-R, Table 3.3, derived; the share is assumed |
| `ge_col_on_loop` | 0 | switch | fixed | published |  | bioreactor_design_tricks.md, table B |
| `ge_k_submerged` | 2e-05 | m/s | fixed | judgement |  | assumed order of magnitude |
| `ge_tubing_od_mm` | 3 | mm | fixed | published |  | Frahm et al. 2009, read in full |
| `ge_head_area` | 1.084 | x D^2 | fixed | published |  | textbook |
| `ge_vessel_cost_exp` | 0.6 | - | fixed | published |  | Seider et al. 2017, read as code in BioSTEAM |
| `ge_hall_share` | 0.131 | of direct cost | fixed | derived |  | Humbird-R, derived |
| `ge_clearance_m` | 2 | m | fixed | judgement |  | assumed |
| `ge_kill_protected` | 0.0004 | L of culture per L of gas | 0.0001, 0.0004, 0.0012 | published | **[cost]** | Jobses, Martens, Tramper 1991, read in full |
| `ge_kill_unprotected` | 0.0088 | L of culture per L of gas | fixed | published |  | Jobses et al. 1991, read in full |
| `ge_alr_volume` | 261.754 | m3 | fixed | published |  | Negulescu et al. 2023, read in full |
| `ge_alr_our` | 10.3 | mmol O2/L/h | fixed | published |  | Negulescu et al. 2023, read in full |
| `ge_alr_li_height` | 13.75 | m | fixed | published |  | Negulescu et al. 2023, read in full, describing Li et al. 2020 |
| `ge_alr_li_volume` | 300 | m3 | fixed | published |  | as above |
| `pf_x_half` | 60 | g wet/L | fixed | judgement |  | assumed |
| `pf_capex_fermentation` | 190 | $k/m3 | 70, 190, 300 | published |  | pf-tea |
| `pf_bioreactor_capex_share` | 0.32 | of direct cost | fixed | published |  | Humbird-R |
| `pf_labour` | 1.45 | $/kg | fixed | published |  | Humbird-R |
| `pf_labour_perfusion_x` | 2 | x the fed-batch crew | 1.4, 2, 3.9 | derived | **[cost]** | Humbird 2021; CE Delft 2021; SuperMeat 2024, derived |
| `pf_labour_tank_share` | 0.619 | of the fed-batch crew | fixed | published |  | Humbird-R |
| `pf_labour_tank_perfusion` | 0.975 | staff per tank | fixed | published |  | Humbird-R |
| `pf_labour_staff_fedbatch` | 95 | staff | fixed | published |  | Humbird-R |
| `pf_medium_prep_l_kg` | 8.7 | L/kg | fixed | published |  | Humbird-R |
| `pf_medium_prep_exp` | 0.6 | exponent | 0.6, 0.6, 1 | judgement | **[cost]** | assumed |
| `pf_harvest_recovery` | 0.98 | fraction | 0.97, 0.98, 0.99 | company |  | SuperMeat 2024; Negulescu 2023; Pasitka 2024 |
| `pf_wash_price` | 0.066 | $/L | 0.01, 0.066, 0.066 | derived |  | derived from glucose_intensity, glucose_price, other_nutrients_floor and pf_medium_l_floor |
| `pf_utilities` | 0.94 | $/kg | fixed | published |  | Humbird-R |
| `pf_util_time` | 4.07 | $k per m3 of tank a year | fixed | derived |  | Humbird-R, Table 4.4, derived |
| `pf_util_run` | 0.0386 | $k per m3 of tank per run | fixed | derived |  | Humbird-R, Table 4.4 and Sect. 4.1, derived |
| `pf_util_water` | 0.0204 | $/L of medium | fixed | published |  | Humbird-R, Sect. 3.2 'Water' and Table 4.4 |
| `pf_util_kg` | 0.0665 | $/kg | fixed | derived |  | Humbird-R, Table 4.4, derived |
| `pf_consumables_fedbatch` | 0.85 | $/kg | fixed | published |  | Humbird-R |
| `pf_consumables_perfusion` | 4.56 | $/kg | fixed | published |  | Humbird-R |
| `pf_labour_perfusion` | 1.99 | $/kg | fixed | published |  | Humbird-R |
| `pf_bound_capex` | 70 | $k/m3 | fixed | published |  | pf-tea |
| `pf_bound_otr` | 50 | mmol O2/L/h | fixed | published |  | pf-tea, citing Humbird 2021 |
| `pf_consumables_low` | 0.3 | $/kg | fixed | judgement |  | assumed |
| `pf_growth_factors` | 3.13 | $/kg | fixed | published |  | Humbird-R |
| `pf_aa_price_cheap` | 1 | $/kg amino acids | fixed | judgement |  | assumed |
| `pf_other_nutrients_cheap` | 0.3 | $/kg | fixed | judgement |  | assumed |
| `pi_n_tanks` | 24 | tanks | fixed | published |  | Humbird-R |
| `pi_tank_m3` | 20 | m3 | fixed | published |  | Humbird-R |
| `pi_prod_installed` | 33922 | $k | fixed | published |  | Humbird-R |
| `pi_seed_installed` | 22673 | $k | fixed | published |  | Humbird-R |
| `pi_bioreactor_bare` | 13794 | $k | fixed | published |  | Humbird-R |
| `pi_fill_tanks` | 1660 | $k | fixed | published |  | Humbird-R |
| `pi_htst` | 702 | $k | fixed | published |  | Humbird-R |
| `pi_makeup_tanks` | 3370 | $k | fixed | published |  | Humbird-R |
| `pi_filter_housings` | 1481 | $k | fixed | published |  | Humbird-R |
| `pi_centrifuge` | 1744 | $k | fixed | published |  | Humbird-R |
| `pi_vpsa` | 8840 | $k | fixed | published |  | Humbird-R |
| `pi_o2_compressor` | 295 | $k | fixed | published |  | Humbird-R |
| `pi_boiler` | 154 | $k | fixed | published |  | Humbird-R |
| `pi_cip_tanks` | 4136 | $k | fixed | published |  | Humbird-R |
| `pi_chiller` | 551 | $k | fixed | published |  | Humbird-R |
| `pi_cooling_tower` | 24 | $k | fixed | published |  | Humbird-R |
| `pi_missing` | 0.1 | share | fixed | published |  | Humbird-R |
| `pi_install` | 1.3 | x bare | fixed | published |  | Humbird-R |
| `pi_engineering` | 0.6 | x direct | fixed | published |  | Humbird-R |
| `pi_fees` | 0.15 | x plant cost | fixed | published |  | Humbird-R |
| `pi_bldg_hall` | 39607 | $k | fixed | published |  | Humbird-R |
| `pi_bldg_cell_lab` | 2575 | $k | fixed | published |  | Humbird-R |
| `pi_bldg_qc_lab` | 1287 | $k | fixed | published |  | Humbird-R |
| `pi_bldg_office` | 527 | $k | fixed | published |  | Humbird-R |
| `pi_bldg_compressor` | 162 | $k | fixed | published |  | Humbird-R |
| `pi_bldg_shop` | 1648 | $k | fixed | published |  | Humbird-R |
| `pi_bldg_warehouse` | 1491 | $k | fixed | published |  | Humbird-R |
| `pi_bldg_slab` | 1185 | $k | fixed | published |  | Humbird-R |
| `pi_rate_class8` | 3760 | $/m2-level | fixed | published |  | Humbird-R |
| `pi_rate_sanitary` | 1980 | $/m2-level | fixed | published |  | Humbird-R |
| `pi_rate_warehouse` | 1130 | $/m2-level | fixed | published |  | Humbird-R |
| `pi_rate_class6` | 8750 | $/m2-level | fixed | published |  | Humbird-R |
| `pi_w_class8` | 410 | W/m2-level | fixed | published |  | Humbird-R |
| `pi_w_sanitary` | 50 | W/m2-level | fixed | published |  | Humbird-R |
| `pi_w_warehouse` | 5 | W/m2-level | fixed | published |  | Humbird-R |
| `pi_w_class6` | 1000 | W/m2-level | fixed | published |  | Humbird-R |
| `pi_w_support` | 85.8 | kW | fixed | derived |  | Humbird-R, Tables 3.2 and 4.2, derived |
| `pi_eq31_slope` | 30.7 | $k/m3 | fixed | published |  | Humbird-R |
| `pi_eq31_fixed` | 800 | $k | fixed | published |  | Humbird-R |
| `pi_eq31_small_slope` | 2285 | $k/m3 | fixed | published |  | Humbird-R |
| `pi_eq31_small_fixed` | 49.5 | $k | fixed | published |  | Humbird-R |
| `pi_makeup_fb_tank` | 140.4 | $k bare per production tank | 100, 140.4, 180 | published |  | Humbird-R |
| `pi_makeup_pf_tank` | 139 | $k bare per production tank | 100, 139, 180 | published |  | Humbird-R |
| `pi_filters_fb_tank` | 61.7 | $k bare per production tank | 40, 61.7, 90 | published |  | Humbird-R |
| `pi_filters_pf_tank` | 27.7 | $k bare per production tank | 15, 27.7, 45 | published |  | Humbird-R |
| `pi_bldg_per_m3` | 74.4 | $k direct per m3 of production tank | 50, 74.4, 100 | derived |  | derived: a fit to Humbird's two plants, not his rule |
| `pi_bldg_per_tank` | 533 | $k direct per production tank | 300, 533, 800 | derived |  | derived: the same fit to Humbird's two plants |
| `pi_bare_coef` | 51 | $k | fixed | published |  | Humbird-R |
| `pi_bare_exp` | 0.69 | exponent | fixed | published |  | Humbird-R |
| `pi_t33_vessel` | 330 | $k | fixed | published |  | Humbird-R |
| `pi_t33_piping` | 360 | $k | fixed | published |  | Humbird-R |
| `pi_t33_instr` | 476 | $k | fixed | published |  | Humbird-R |
| `pi_t33_other` | 22 | $k | fixed | published |  | Humbird-R |
| `pi_t33_internals` | 164 | $k | fixed | published |  | Humbird-R |
| `pi_t33_surface` | 132 | $k | fixed | published |  | Humbird-R |
| `pi_seed_trains` | 4 | trains | fixed | published |  | Humbird-R |
| `pi_seed_f0_m3` | 0.15 | m3 | fixed | published |  | Humbird-R |
| `pi_seed_f1_m3` | 0.55 | m3 | fixed | published |  | Humbird-R |
| `pi_seed_f2_m3` | 2.1 | m3 | fixed | published |  | Humbird-R |
| `pi_seed_f3_m3` | 8.1 | m3 | fixed | published |  | Humbird-R |
| `pi_seed_f4_m3` | 15.6 | m3 | fixed | published |  | Humbird-R |
| `pi_seed_tanks_per_f4` | 3 | tanks | fixed | published |  | Humbird-R |
| `pi_stage_h` | 57 | h | fixed | published |  | Humbird-R |
| `pi_yeast_bcr_200` | 818 | $k | fixed | published |  | Humbird-R |
| `pi_yeast_seed` | 1369 | $k | fixed | published |  | Humbird-R |
| `pi_yeast_pasteurizer` | 221 | $k | fixed | published |  | Humbird-R |
| `pi_yeast_prep_tank` | 593 | $k | fixed | published |  | Humbird-R |
| `pi_yeast_compressors` | 2750 | $k | fixed | published |  | Humbird-R |
| `pi_yeast_centrifuges` | 1728 | $k | fixed | published |  | Humbird-R |
| `pi_yeast_rvf` | 652 | $k | fixed | published |  | Humbird-R |
| `pi_yeast_missing` | 0.2 | x listed | fixed | published |  | Humbird-R |
| `pi_yeast_lang` | 4.5 | x equipment | fixed | published |  | Humbird-R |
| `pi_yeast20_capex` | 70000 | $k | fixed | published |  | Humbird-R |
| `pi_yeast20_tanks` | 27 | tanks | fixed | published |  | Humbird-R |
| `pi_yeast_output_ratio` | 0.0982659 | ratio | fixed | published |  | Humbird-R |
| `pi_yeast_oxygen_ratio` | 0.075 | ratio | fixed | published |  | Humbird-R |
| `pi_yeast_broth_ratio` | 0.271214 | ratio | fixed | published |  | Humbird-R |
| `pi_yeast_feed_ratio` | 0.121468 | ratio | fixed | published |  | Humbird-R |
| `pi_scale_exp` | 0.6 | exponent | 0.5, 0.6, 0.7 | judgement |  | assumed |
| `pi_lys_install` | 1.07 | x equipment | fixed | published |  | Humbird-R |
| `pi_lys_buildings` | 0.2 | x equipment | fixed | published |  | Humbird-R |
| `pi_lys_aux` | 0.3 | x equipment | fixed | published |  | Humbird-R |
| `pi_vessel_food_k` | 1000 | $k per 20 m3 tank | 450, 1000, 1414 | published |  | company claim, trade press |
| `pi_o2_feed` | 3.3 | kg O2/kg wet cells | fixed | derived |  | Humbird-R, derived |
| `pi_o2_price` | 0.1 | $/kg | 0.05, 0.1, 0.2 | judgement |  | assumed |
| `ct_doubling_fast_min` | 20 | min | fixed | published_partly |  | BioNumbers 103514, search result |
| `ct_doubling_slow_min` | 60 | min | fixed | judgement |  | assumed |
| `ct_doubling_cryptic_h` | 6 | h | fixed | published |  | Fratz-Berilla et al. 2019, Biotechnol. Bioeng., full text |
| `ct_bact_qo2` | 15 | mmol O2/g dry/h | 5, 15, 20 | judgement |  | from memory, textbook range 10-20 for E. coli growing fast; not verified at source |
| `ct_bact_dry_pg` | 0.3 | pg dry per cell | 0.15, 0.3, 1 | judgement |  | from memory, BioNumbers: an E. coli cell is about 0.3 pg dry (1 pg wet); not verified at source |
| `ct_detect_shift` | 0.05 | share | 0.01, 0.05, 0.1 | judgement |  | assumed |
| `ct_inoculum_cfu` | 1 | cells | fixed | judgement |  | assumed |
| `ct_food_limit_cfu` | 10000 | CFU/g | fixed | published |  | FSANZ A1269 risk assessment, April 2025, full text |
| `ct_start_detect_days` | 1 | days | 0.7, 1, 5 | published_partly |  | Linderholm et al. 2025, Anal. Bioanal. Chem., search result |
| `ct_seed_share` | 0.304167 | of a tankful | fixed | published |  | Humbird-R |
| `ct_batch_loss_pharma` | 0.023 | of batches | fixed | published |  | Langer 2008, BioProcess Int., full text |
| `ct_batch_loss_cm` | 0.112 | of batches | 0, 0.112, 0.52 | published |  | Powell et al. 2025, Compr. Rev. Food Sci. Food Saf., full text |
| `ct_batch_loss_cm_scaled` | 0.195 | of batches | fixed | published |  | Powell et al. 2025, full text |
| `ct_hazard_frontier` | 0.015 | per day | 0.006, 0.015, 0.022 | judgement |  | derived, with an assumed run length |
| `sc_nh3_engineered` | 0.055 | mol/kg wet | 0.054, 0.055, 0.14 | derived |  | Humbird-R, derived; waste_tricks_sizing.md |
| `sc_nh3_selected` | 0.14 | mol/kg wet | 0.04, 0.14, 0.25 | published | **[cost]** | Hubalek et al. 2023, full text; waste_tricks_sizing.md |
| `sc_nh3_ordinary` | 0.7 | mol/kg wet | 0.09, 0.7, 0.95 | published |  | Hubalek et al. 2023, full text |
| `sc_lac_engineered` | 0.279 | mol lactate / mol glucose | 0.06, 0.279, 0.28 | published |  | Humbird-R, reaction 2.11 |
| `sc_lac_selected` | 0.42 | mol lactate / mol glucose | 0.39, 0.42, 0.6 | published | **[cost]** | waste_tricks_sizing.md |
| `sc_lac_measured` | 1.05 | mol lactate / mol glucose | 0.8, 1.05, 1.4 | published_partly |  | Pasitka et al. 2024, snippet; waste_tricks_sizing.md |
| `sc_glc_measured` | 0.84 | mol glucose/kg wet | 0.67, 0.84, 3.6 | published |  | waste_tricks_sizing.md section C2: 0.4-0.6 kg glucose per kg dry cells, cross-checked by Freund's CHO, 0.98 mol/kg |
| `sc_mass_selected_pg` | 2000 | pg wet per cell | 1000, 2000, 3000 | judgement | **[cost]** | judgement |
| `sc_td_central` | 36 | h | 26, 36, 43 | judgement |  | Hubalek et al. 2023; judgement |
| `sc_td_fast` | 30 | h | 26, 30, 36 | judgement |  | judgement |
| `sc_td_measured` | 43 | h | 38, 43, 54 | published |  | Hubalek et al. 2023, full text |
| `sc_gas_mid` | 0.004 | m/s | 0.002, 0.004, 0.006 | published |  | research_notes/gas_flow_cap.md |
| `sc_gas_low` | 0.002 | m/s | 0.001, 0.002, 0.004 | published |  | Nienow 2006, full text; gas_flow_cap.md |
| `sc_hazard_mid` | 0.006 | per day | 0.002, 0.006, 0.015 | published |  | Powell et al. 2025; ct_hazard_frontier |
| `sc_hazard_cm` | 0.01 | per day | 0.006, 0.01, 0.022 | judgement |  | Powell et al. 2025, full text; assumed run length |
| `sc_hazard_high` | 0.02 | per day | 0.015, 0.02, 0.022 | published |  | Powell et al. 2025 |
| `vm_cage_exchange` | 0.8 | - | 0.5, 0.8, 1 | judgement |  | judgement |
| `vm_cage_gas` | 0.006 | m/s | 0.003, 0.006, 0.012 | judgement |  | judgement, gas_flow_cap.md |
| `vm_cage_capex_ratio` | 1.15 | x stirred tank | 1.05, 1.15, 1.4 | judgement |  | judgement |
| `mr_ed_nh3` | 0.9 | share removed per pass | 0.5, 0.9, 0.95 | published_partly |  | Nir 2023, as cited in Soccol et al. 2024, ch. 'Waste management'; secondary, primary not found |
| `mr_ed_lac` | 0.99 | share removed per pass | 0.5, 0.99, 0.99 | published_partly |  | Nir 2023, as cited in Soccol et al. 2024; secondary |
| `mr_ed_cost_l` | 0.02 | $/L treated | 0.005, 0.02, 0.1 | published |  | my arithmetic, not a quote |
| `mr_dial_removal` | 0.9 | share removed per pass | 0.7, 0.9, 0.95 | published_partly |  | YekrangSafakar et al. 2022, via waste_and_medium_evidence.md |
| `mr_dialysate_l` | 2.1 | L per L treated | 1, 2.1, 4 | published |  | YekrangSafakar et al. 2022, my reading in waste_and_medium_evidence.md |
| `mr_dialysate_makeup` | 0.1 | share replaced | 0.05, 0.1, 0.5 | published |  | patent claim WO2018011805, Yissum / Future Meat: 'at least 90% of the perfusion solution recirculated' |
| `mr_dial_cost_l` | 0.05 | $/L treated | 0.01, 0.05, 0.37 | judgement |  | assumed |
| `mr_gf_kept` | 0.9 | share kept per pass | 0.5, 0.9, 1 | judgement |  | assumed |
| `mr_exchange_clearance` | 10 | L/m2/h | 5, 10, 15 | judgement |  | Fresenius Medical Care, FX high-flux dialyser table, in vitro (ISO 8637, QD 500 mL/min), checked 2026-11-21; the FX CorAL 80 510(k) summary K220721 gives 277 |
| `sc_wide_bands` | 1 | switch | fixed | setting |  | model choice, 2026-11-16 |
| `sc_nh3_limit` | 4 | mmol/L | 2, 4, 8 | judgement | **[cost]** | research_notes/ammonia_tolerance_and_filter_life.md, judgement |
| `sc_lac_limit` | 35 | mmol/L | 20, 35, 50 | judgement | **[cost]** | Cultivated Meat (book), Table 2, citing Hassell 1991; Pasitka 2024; Humbird 2021, judgement |
| `sc_do_setpoint` | 0.1 | mmol O2/L | 0.05, 0.1, 0.28 | published_partly |  | gas_exchange_study.md 10.2; pharma practice, snippet-level sources |
| `sc_do_scenarios` | 1 | switch | fixed | setting |  | model choice, 2026-11-16 |
| `sc_restart_neighbour` | 4 | days | 3, 4, 7 | judgement |  | arithmetic, judgement |
| `sc_restart_base` | 14 | days | 7, 14, 30 | published |  | contamination.py; Humbird-R Sect. 4.1 seed train |
| `sc_restart_slow` | 21 | days | 14, 21, 30 | published |  | plant_items.py, contamination.py |
| `sc_restart_long` | 30 | days | 21, 30, 60 | published |  | contamination.common_mode_restart_days |
| `sc_gf_part` | 0.3 | of Humbird's growth-factor cost | 0, 0.3, 1 | judgement |  | judgement; Humbird-R, Sect. 3.1 price of large-scale growth factors |
| `sc_medium_complete` | 1 | switch | fixed | published |  | research_notes/growth_factors_in_medium_price.md |
| `sc_gf_most` | 0.6 | of Humbird's growth-factor cost | 0, 0.6, 1 | judgement |  | judgement |
| `sc_medium_mid` | 0.2 | $/L | 0.15, 0.2, 0.5 | company |  | GFI 2026 industry report, p.8 |
| `sc_medium_high` | 0.3 | $/L | 0.2, 0.3, 0.5 | judgement |  | judgement |
| `sc_aspect_flat` | 0.5 | depth/width | 0.5, 0.5, 0.75 | published |  | gas_exchange.cheapest_tricks |
| `sc_aspect_squat` | 0.75 | depth/width | 0.5, 0.75, 1 | published |  | gas_exchange_study.md |
| `sc_aspect_mid` | 1 | depth/width | 0.75, 1, 1.6 | judgement |  | judgement |
| `sc_p_top` | 1 | bar gauge | 0.33, 1, 2 | company |  | gas_exchange_study.md; vendor data sheets |
| `cr_nh3_feed` | 0.14 | mol/kg wet | fixed | published |  | Hubalek et al. 2023, full text |
| `cr_nh3_select_other` | 0.054 | mol/kg wet | fixed | published |  | Mayrhofer et al. 2020, FT-sum; Humbird 2021 |
| `cr_nh3_engineering` | 0 | mol/kg wet | fixed | company |  | ISCCM11 poster, 2025, culturedmeatconference.com |
| `cr_lac_feed` | 1.05 | mol/mol glucose | fixed | published_partly |  | Pasitka et al. 2024, snippet |
| `cr_lac_select_other` | 0 | mol/mol glucose | fixed | published_partly |  | Gagnon et al. 2011, abstract; Mayrhofer et al. 2020, FT-sum; Freund and Croughan 2018 |
| `cr_lac_engineering` | 0 | mol/mol glucose | fixed | published |  | Hefzi et al. 2024, preprint |
| `cr_td_feed` | 25.7 | h | fixed | published |  | Hubalek et al. 2023 |
| `cr_td_select_meat` | 20 | h | fixed | published_partly |  | Pasitka et al. 2023, Nature Food, snippet of figure text |
| `cr_td_engineering` | 15 | h | fixed | published |  | Stout et al. 2023, ACS Synth Biol / preprint; species_cell_parameters.md |
| `cr_mass_feed` | 3300 | pg wet per cell | fixed | derived |  | Pasitka et al. 2024 abstract, converted in species_cell_parameters.md |
| `vm_str_m3` | 20 | m3 | fixed | published |  | Humbird-R |
| `vm_perf_max_m3` | 4 | m3 | fixed | published_partly |  | research pass, read part |
| `vm_x_meat_shown` | 27 | g wet/L | 27, 27, 68 | published |  | research_notes/Continuous harvest bioreactor progress/cultivated_meat_reactor_progress.md, company and press reports |
| `vm_labour_exp` | 0.54 | - | 0.3, 0.54, 1 | derived |  | Humbird-R, derived |
| `vm_restart_cycle_days` | 2 | days | 1, 2, 14 | judgement |  | assumed |
| `vm_batch_x` | 25 | g wet/L | 12, 25, 45 | judgement |  | assumed from pharma |
| `vm_chemostat_dil` | 0.6 | of mu_max | 0.4, 0.6, 0.9 | published_partly |  | HeLa chemostat, Korean J. Biotechnol. 1989, abstract only |
| `vm_alr_aspect` | 3 | depth/width | 2, 3, 8 | judgement |  | assumed |
| `vm_alr_otr_mult` | 1 | x stirred | 0.7, 1, 1.2 | published |  | Hubbard 2024 preprint, read in full, quoting Negulescu 2023's correlation |
| `vm_alr_capex_ratio` | 0.8 | x a stirred vessel | 0.5, 0.8, 1 | judgement |  | assumed, research pass |
| `vm_bag_m3` | 5 | m3 | fixed | company |  | Thermo Fisher launch, 2021, secondary; Patheon white paper, read in full |
| `vm_bag_capex_ratio` | 0.5 | x a stirred vessel | 0.4, 0.5, 1 | company |  | vendor claim, secondary |
| `vm_bag_cost_run` | 20 | $k/m3 per run | 5, 20, 30 | judgement |  | assumed |
| `vm_bed_m3` | 0.065 | m3 working | fixed | company |  | Pall application note, read in full |
| `vm_bed_x` | 113 | g wet/L | 60, 113, 275 | derived |  | Pall application note, read in full; converted |
| `vm_bed_doublings` | 6.6 | doublings | 4, 6.6, 7 | company |  | Pall application note, read in full |
| `vm_bed_turnaround_h` | 72 | h | 24, 72, 120 | judgement |  | assumed, research pass |
| `vm_bed_recovery` | 0.9 | of cells | 0.7, 0.9, 0.96 | judgement |  | assumed |
| `vm_bed_capex_ratio` | 1 | x a stirred vessel | 0.3, 1, 1.5 | judgement |  | assumed |
| `vm_bed_cost_run` | 154 | $k/m3 per run | 31, 154, 460 | judgement |  | assumed |
| `vm_hf_m3` | 0.00048 | m3 working | fixed | published_partly |  | HEK293T paper, PMC10504471, read part; Terumo papers, snippet |
| `vm_hf_x` | 13 | g wet/L | 9, 13, 150 | derived |  | PMC10504471, read part; converted |
| `vm_hf_doublings` | 3.1 | doublings | 3, 3.1, 7 | published_partly |  | PMC10504471, read part |
| `vm_hf_turnaround_h` | 96 | h | 48, 96, 144 | judgement |  | assumed, research pass |
| `vm_hf_recovery` | 0.9 | of cells | 0.7, 0.9, 0.95 | published_partly |  | Terumo, snippet |
| `vm_hf_capex_ratio` | 0.035 | x a stirred vessel | 0.02, 0.035, 0.1 | published_partly |  | reseller listing, snippet |
| `vm_hf_cost_run` | 6250 | $k/m3 per run | 2000, 6250, 20000 | judgement |  | assumed |
| `rt_tff_default` | 1 | switch | fixed | setting |  | model choice, 2026-11-15 |
| `rt_install` | 1.84 | x | 1.5, 1.84, 2.5 | published |  | Pasitka SI Tables S1 and S4, as for pf_capex_retention |
| `rt_flux_lmh` | 5 | L/m2/h | 2, 5, 8.3 | published_partly |  | Repligen design guidance, snippet; Ott 2024, Veje 2024, read in full |
| `rt_atf_area` | 11 | m2 | fixed | company |  | Repligen XCell ATF 10 brochure, read in full |
| `rt_atf_price` | 200 | $k per unit | 100, 200, 350 | derived |  | Humbird 2021, read in part, derived |
| `rt_atf_phi_max` | 0.31 | volume fraction | 0.25, 0.31, 0.35 | published |  | Clincke et al. 2013, read in full |
| `rt_tff_hw` | 1 | $k per m2 | 0.5, 1, 3 | judgement |  | assumed, research pass |
| `rt_tff_phi_max` | 0.5 | volume fraction | 0.3, 0.5, 0.5 | published |  | Clincke et al. 2013, read in full |
| `rt_membrane_price` | 1450 | $/m2 | 1050, 1450, 1450 | derived | **[cost]** | Humbird 2021, read in part, derived |
| `rt_membrane_life` | 2415 | L/m2 | 900, 2415, 5500 | derived | **[cost]** | Humbird 2021, Table 4.11, derived |
| `rt_reuse_life` | 12000 | L/m2 | 8700, 12000, 16600 | published_partly |  | Cobetter and Sartorius reuse guidance, snippets; patent US 6,261,457, snippet |
| `rt_dial_price` | 8 | $/m2 | 3, 8, 14 | published_partly |  | market reports and a retailer, snippets |
| `rt_dial_flux` | 2.5 | L/m2/h | 2, 2.5, 3.4 | company |  | Fresenius FX 80 data sheet, snippet; haemodiafiltration study, snippet |
| `rt_dial_life` | 1000 | L/m2 | 240, 1000, 2000 | judgement |  | assumed, between the two cases the research pass worked |
| `rt_dial_hw` | 0.5 | $k per m2 | 0.2, 0.5, 1 | judgement |  | assumed |
| `rt_dial_phi_max` | 0.35 | volume fraction | 0.3, 0.35, 0.4 | company |  | Fresenius FX 80 data sheet, snippet |
| `rt_ceramic_price` | 1500 | $/m2 | 500, 1500, 3000 | published_partly |  | research pass, snippets |
| `rt_ceramic_life` | 40000 | L/m2 | 15000, 40000, 200000 | judgement |  | assumed |
| `rt_ceramic_hw` | 3 | $k per m2 | 1, 3, 6 | judgement |  | assumed |
| `rt_ceramic_phi_max` | 0.12 | volume fraction | 0.05, 0.12, 0.25 | judgement |  | assumed |
| `rt_settle_price` | 3.5 | $k per m2 | 2, 3.5, 5 | judgement |  | assumed, research pass |
| `rt_settle_holdup` | 17 | L per m2 | 10, 17, 25 | published_partly |  | Romann et al. 2023, read in full, via the repo notes |
| `rt_settle_v_frac` | 0.5 | of hindered velocity | 0.3, 0.5, 0.7 | published |  | research notes, practice |
| `rt_settle_holdup_max` | 0.05 | of the tank's liquid | 0.02, 0.05, 0.1 | judgement |  | assumed |
| `rt_settle_phi_max` | 0.12 | volume fraction | 0.1, 0.12, 0.2 | published_partly |  | Coronel 2020; Romann 2023, via the repo notes |
| `rt_acoustic_cap` | 1 | m3/day per unit | 0.2, 1, 1 | company |  | Getinge BioSep product page, snippet |
| `rt_acoustic_price` | 100 | $k per unit | 50, 100, 200 | judgement |  | assumed |
| `rt_ds_cap` | 2 | m3/h per unit | 1, 2, 2 | company |  | Alfa Laval Culturefuge 100, vendor, snippet |
| `rt_ds_price` | 800 | $k per unit installed | 400, 800, 1500 | judgement |  | assumed, research pass |
| `rt_ds_spares` | 1 | units | fixed | judgement |  | assumed |
| `rt_ds_conc` | 0.7 | volume fraction | 0.6, 0.7, 0.8 | published_partly |  | Hundley and Konigsson 2020, BioProcess Int., read in part |
| `rt_ds_lysis` | 0.04 | per pass | 0.02, 0.04, 0.125 | company |  | same, measured by the vendor's staff |
| `rt_ds_phi_max` | 0.28 | volume fraction | 0.2, 0.28, 0.3 | published_partly |  | Hundley and Konigsson 2020, read in part |
| `rt_ds_power` | 10 | kW per running unit | 5, 10, 20 | company |  | research pass, inference from vendor data |
| `rt_maint` | 0.04 | of capital a year | 0.02, 0.04, 0.08 | judgement |  | assumed |
| `rt_hc_eff` | 0.96 | of cells | 0.89, 0.96, 0.97 | published_partly |  | Bettinardi et al. 2020, abstract; Pinto et al. 2008, snippet |
| `rt_hc_split` | 0.5 | of feed | 0.3, 0.5, 0.7 | judgement |  | assumed |
| `rt_hc_price` | 50 | $k per m3/h of feed, installed | 20, 50, 150 | judgement |  | assumed |
| `rt_hc_phi_max` | 0.12 | volume fraction | 0.06, 0.12, 0.2 | published_partly |  | Bettinardi et al. 2020, abstract |
| `rt_part_phi_max` | 0.249 | volume fraction | 0.2, 0.249, 0.35 | published |  | model rule, pf_x_visc |
| `rt_part_loss` | 0.03 | of cells grown | 0.01, 0.03, 0.08 | published_partly |  | settling-tube patent, snippet: every bead held, over 95% of cells held; Huang 2020, full: a plain dip-tube settler let aggregates go |
| `rt_agg_d_min_um` | 100 | um | 60, 100, 150 | published |  | Huang 2020 and Manstein 2021, full: aggregates are reseeded at 100-150 um and grow to 250-300 um |
| `rt_agg_d_max_um` | 300 | um | 200, 300, 450 | published |  | Huang 2020, full: mean held below 300 um by stirring, passaged every 5 days; Manstein 2021, full: 250-280 um at 80 rpm, 320-480 um at 60 rpm |
| `rt_agg_cell_share` | 0.75 | of aggregate volume | 0.6, 0.75, 0.85 | published_partly |  | spheroid extracellular space about 15% (arXiv 2011.01131, snippet); random packing of spheres 0.64; iPSC aggregates hold cavities (Manstein 2021, full) |
| `rt_agg_phi_shown` | 0.04 | volume fraction | 0.03, 0.04, 0.06 | published |  | Manstein 2021, full: 33-35e6 iPSC/mL in 150 mL, 7 days, 20-40 um outflow filter |
| `rt_o2_diff_tissue` | 2e-09 | m2/s | 1.5e-09, 2e-09, 2.5e-09 | published |  | Grimes & Currell, bioRxiv 271890, full: 2e-9 used for spheroids |
| `rt_o2_diff_water` | 3e-09 | m2/s | fixed | judgement |  | typical |
| `rt_o2_sherwood` | 10 | - | 3, 10, 20 | published |  | calculation: Kolmogorov-scale mass transfer to a 200 um particle in a stirred tank at 0.01-0.1 W/kg gives Sh of about 6-15; Sh = 2 in still liquid |
| `rt_o2_prolif` | 0.026 | mmol O2/L | 0.013, 0.026, 0.065 | published |  | Gomes et al. 2016, PLoS ONE, PMC5004916, full: about 20 mmHg sustains proliferation, half of it is lost below |
| `rt_mc_d_um` | 190 | um | 100, 190, 250 | company |  | Cytiva Cytodex 1 datasheet, snippet: median 190 um, 147-248 |
| `rt_mc_cells_cm2` | 180000 | cells/cm2 | 100000, 180000, 300000 | published_partly |  | El Wajgali 2011, full: 3.9e6 Vero/mL on 5 g/L Cytodex 1, 106-311 cells a bead; Eppendorf note 414, snippet: 8e6/mL on 10 g/L Cytodex 3, about 3e5/cm2 |
| `rt_mc_solids` | 0.07 | g dry/mL of bead | 0.04, 0.07, 0.2 | company |  | Cytiva datasheet, snippet: 4,400 cm2/g and 4.3e6 beads/g at 190 um give 0.07 g of dextran per mL of swollen bead |
| `rt_mc_density` | 1.03 | g/mL | fixed | company |  | Cytiva datasheet, snippet: Cytodex 1 1.03, Cytodex 3 1.04 |
| `rt_mc_price` | 10 | $/kg dry | 3, 10, 50 | judgement |  | assumed; no price for an edible carrier was found |
| `rt_mc_phi_shown` | 0.02 | volume fraction | 0.01, 0.02, 0.04 | published_partly |  | Eppendorf note 414, snippet: 8e6 Vero/mL on Cytodex 3 in 3 L with a spin filter; El Wajgali 2011, full: 3.9e6/mL |
| `nf_aa_price_feed` | 6.36 | $/kg AA | 3, 6.36, 12 | company |  | GFI amino acid analysis, Dec 2025, Table 1, read in full; unweighted mean of 22 amino acids |
| `nf_aa_price_low` | 11.59 | $/kg AA | 7, 11.59, 16 | company |  | GFI Dec 2025, Table 1; unweighted mean |
| `nf_aa_price_high` | 23.18 | $/kg AA | 15, 23.18, 35 | company |  | GFI Dec 2025, Table 1; unweighted mean |
| `nf_aa_g_eff` | 232 | g AA/kg wet cells | 200, 232, 350 | company |  | GFI Dec 2025, Fig. 9, read in full |
| `nf_aa_g_mid` | 350 | g AA/kg wet cells | 232, 350, 500 | company |  | GFI Dec 2025, Fig. 9 |
| `nf_aa_g_low` | 650 | g AA/kg wet cells | 500, 650, 650 | company |  | GFI Dec 2025, Fig. 9 |
| `au_retail_share` | 0.45 | of retail price | 0.42, 0.45, 0.65 | published_partly |  | USDA ERS Meat Price Spreads, via research_notes/post_harvest_costs.md, full data read |
| `au_processing` | 1 | $/kg | 0.3, 1, 3 | judgement |  | assumed |
| `ms_world_meat` | 336 | Mt a year | 300, 336, 384 | judgement |  | FAO Food Outlook Nov 2025, FAO SOFIA 2024/2026, snippets; conversions assumed |
| `ms_switch_area` | 1e+06 | m2 a year | 300000, 1e+06, 3e+06 | judgement |  | judgement, research pass |
| `ms_food_membrane` | 150 | $/m2 | 60, 150, 400 | published_partly |  | inge dizzer XL water UF module, 60 m2, cleaned at pH 1-13: $66 a m2 (distributor listing, snippet; specs read); Koch sanitary dairy spiral $27-62 a m2 (snippet, not steam-tolerant); Repligen KrosFlo process hollow fibre $800-1,200 a m2 (snippet) |
| `ms_lr_membrane` | 0.18 | per doubling | 0.1, 0.18, 0.28 | published_partly |  | Abbott 2025 (WIOA, read): MBR membrane cost per m2 fell to 0.3 of its 2005 level by 2025, 18-26% a doubling if area doubled 4-6 times; Caldera & Breyer 2017 (abstract): seawater RO plants 15% |
| `ms_membrane_floor` | 50 | $/m2 | 20, 50, 120 | judgement |  | judgement, research pass |
| `ms_lr_plant` | 0.1 | per doubling | 0.03, 0.1, 0.18 | published |  | Rubin et al. 2015, Table 1, read: nuclear negative to 6%, coal 8%, gas turbines 15%, hydro 1.4%; Hettinga et al. 2009, read: corn ethanol capital about 20% at constant plant size, overstated by falling interest; RO plants 12-15% |
| `ms_base_tanks` | 8000 | m3 | 6500, 8000, 11800 | published_partly |  | BDO/BPTC via BioProcess International 2023, read: 'nearly 6,500 kL' of mammalian capacity; BioPlan basis 10.9-11.8 million L |
| `ff_phi_w` | 0.6 | volume fraction | 0.5, 0.6, 0.64 | published |  | Kromkamp 2005 (Wageningen thesis, text extract read); Vyas 1999 (Massey thesis, full text read) |
| `ff_coef_belfort` | 0.078 | - | fixed | published |  | Vyas 1999 (Massey thesis), Eq. 2.18, full text read, page image checked, restating Belfort, Davis and Zydney 1994 |
| `ff_coef_ds` | 0.072 | - | fixed | published |  | Kromkamp 2005, Eq. 5.2, text extract read, restating Davis and Sherwood 1990 |
| `ff_yeast_shortfall` | 4 | x | 1.3, 4, 4 | published_partly |  | Redkar and Davis 1993, abstract only |
| `ff_shear` | 2000 | 1/s | 1250, 2000, 5500 | published |  | Pinto et al. 2020, full text read; Mostafavi et al. 2025, full text read |
| `ff_length` | 0.3 | m | 0.2, 0.3, 1 | published |  | Pinto 2020 and Radoniqi 2018, full text read: 0.2 m; Veje 2024: 0.65 m |
| `ff_throughput_lo` | 450 | L/m2 | 450, 450, 900 | published |  | Pinto et al. 2020, full text read |
| `ff_throughput_hi` | 1200 | L/m2 | 900, 1200, 1200 | published |  | Pinto 2020; Veje 2024, full text read |
| `ff_flux_typical` | 2.5 | L/m2/h | 1, 2.5, 3 | published |  | Veje 2024 (full text, citing the literature: 2-3); Radoniqi 2018 (full text: 2); Pinto 2020 (1-2) |
| `elasticity_anchor_price` | 29.012 | $/kg | fixed | fitted |  | calibration |
| `eps_own` | -0.9 | elasticity | -1.4, -0.9, -0.5 | published | **[share]** | scanner |
| `kappa_base` | 4 | x | fixed | published |  | structural |
| `liking_sd` | 3.55 | utils | 3.3, 3.55, 3.9 | fitted | **[share]** | fitted, liking_spread.families |
| `liking_tail` | 7 | dof | 5, 7, 12 | fitted |  | fitted, liking_spread.families |
| `equal_price_share` | 0.464 | of all choices | 0.05, 0.464, 0.8 | judgement | **[share]** | judgement, research_notes/liking_spread.md |
| `best_equal_price_share` | 0.55 | of buyers | 0.35, 0.55, 0.7 | judgement |  | the model's rough judgement, 2026-11-19 |
| `cult_sub_mult` | 8.5 | x | 4, 8.5, 11 | published | **[share]** | data-bracketed |
| `loss_aversion` | 1 | ratio | 1, 1, 2.25 | untagged | **[share]** | REFERENCE-DEPENDENT price asymmetry lambda (OFF by default). |
| `w_ratio` | 1 | utils per unit ratio | 0.5, 1, 1.5 | judgement | **[share]** | judgement |
| `theta_free_M` | 0 | utils | 0, 0, 1 | judgement | **[share]** | NEUTRAL DIAL |
| `accept_x` | 1 | fraction | 0.6, 1, 1 | judgement | **[share]** | DIAL |
| `premium_resistance` | 1 | x | 0.5, 1, 1.5 | judgement |  | assumed |
| `real_tissue_x` | 1 | 0/1 | fixed | judgement |  | IDENTIFYING PREMISE, now a DIAL |
| `real_tissue_p` | 0 | 0/1 | fixed | setting |  | product position |
| `health_x` | 0 | norm | -0.5, 0, 0.5 | judgement | **[share]** | SCENARIO, unidentified |
| `health_p` | 0 | norm | -0.5, 0, 0.5 | judgement |  | SCENARIO, unidentified |
| `health_w` | 2 | norm | fixed | setting |  | position |
| `health_c` | -0.1 | norm | fixed | setting |  | position |
| `neophobia_p0` | -1 | utils | -2, -1, 0.5 | judgement |  | behavioural |
| `price_pb_mult` | 1.77 | x p_conv | 1.5, 1.77, 2.2 | company |  | GFI |
| `price_wf_mult` | 0.25 | x p_conv | fixed | published |  | BLS |
| `taste_quality_w` | -0.7 | norm | -1, -0.7, -0.3 | judgement |  | assumed |
| `income_ref` | 86170 | $/yr | fixed | published |  | World Bank API, NY.GDP.PCAP.CD |
| `income_gradient` | 0.32 | exponent | 0, 0.32, 1 | published | **[share]** | Muhammad/ERS |
| `taste_quality_p` | -0.2 | norm | -0.4, -0.2, 0 | company |  | Nectar |
| `w_taste` | 5 | utils | fixed | fitted |  | calibration |
| `w_eth` | 0.05 | fraction | 0.04, 0.05, 0.1 | published |  | Gallup |
| `w_realtissue_M` | 2 | utils | fixed | fitted |  | calibration, SOLVED |
| `pb_mainstream_frac` | 0.89 | fraction | 0.82, 0.89, 0.93 | company |  | GFI |
| `wf_mainstream_target` | 0.06 | share | 0.04, 0.06, 0.14 | judgement | **[share]** | assumed, SOFT |
| `w_health_M` | 1.2 | utils | fixed | fitted |  | calibration, SOLVED |
| `w_realtissue_E` | 0 | utils | fixed | judgement |  | assumed |
| `w_slaughter_E` | 4 | utils | fixed | judgement |  | assumed |
| `mk_supply_elast` | 2 | - | 0.5, 2, 10 | published |  | Brester, Marsh and Atwood 2004: 10-year supply elasticities cattle 3.24, hogs 1.8, poultry 14; Geibel et al. 2021, Table 1: simulated combined elasticities 0.4 to 4.6 |
| `mk_demand_elast` | -0.65 | - | -0.8, -0.65, -0.5 | published |  | USDA ERS Technical Bulletin 1956: beef -0.56, pork -0.79, chicken -0.58 |
| `meat_displaced_per_kg` | 1 | kg of conventional meat a kg sold | 0.5, 1, 1 | judgement |  | assumed; no study measures it for cultivated meat |
| `mk_closed_us_permanent` | 0.1017 | share of the US | fixed | published |  | US Census Vintage 2025 |
| `mk_closed_us_temporary` | 0.1159 | share of the US | fixed | published |  | US Census Vintage 2025 |
| `mk_closed_eu_contested` | 0.1389 | share of the EU-27's meat | fixed | published |  | Eurostat, 1 Jan 2025; FAO food balance sheets 2023 |
| `mk_world_pop_m` | 8231.6 | million people | fixed | published |  | UN World Population Prospects 2024 |
| `mk_closed_religious_against` | 0.0154 | share of world meat | 0.007, 0.0154, 0.0154 | published |  | FAO food balance sheets 2023; Our World in Data population 2023 |
| `mk_closed_religious_conditions` | 0.106 | share of world meat | 0.08, 0.106, 0.13 | published |  | FAO food balance sheets 2023, latest year for Sudan, Somalia, Mali, Chad and Brunei; Our World in Data population 2023 |
| `mk_closed_level` | 1 | level | fixed | published |  | the brief's default |
| `pb_share_target` | 0.004 | share | 0.0025, 0.004, 0.006 | derived |  | GFI/SPINS; GFI/NIQ; derived |
| `pb_committed_share` | 0.07 | of all shoppers | 0.02, 0.07, 0.1 | company |  | GFI/NielsenIQ 2022; Circana 2024 |
| `pb_committed_volume` | 0.82 | of the mainstream's plant-based meat | 0.75, 0.82, 0.9 | company |  | GFI/NielsenIQ 2022; Circana 2024 |
| `pb_committed_price_x` | 0.25 | x other shoppers' | 0.1, 0.25, 0.5 | published |  | Tonsor, Lusk & Schroeder 2021; demand_heterogeneity_evidence.md sections 3-4 |
| `pb_committed_liking` | 4 | utils | fixed | fitted |  | calibration, SOLVED |
| `price_insensitive_share` | 0.08 | of all shoppers | 0.08, 0.08, 0.15 | fitted | **[share]** | Lusk 2019 report to FFAR/FMI; Washio et al. 2023; Carzedda & Troiano 2021; demand_heterogeneity_evidence.md section 3; size fitted within that range, demand_checks.md section 7 |
| `price_insensitive_response` | 0.11 | x other shoppers' | 0.1, 0.11, 0.25 | fitted | **[share]** | demand_heterogeneity_evidence.md section 3; fitted within its range, demand_checks.md section 7 |
| `price_insensitive_liking` | 0 | utils | -2, 0, 2 | published | **[share]** | Washio et al. 2023; Carzedda & Troiano 2021; demand_checks.md section 7 |
| `w_health_E` | 2.3 | utils | fixed | fitted |  | calibration, SOLVED |
| `neophobia_x` | 0 | utils | -2, 0, 1 | judgement | **[share]** | behavioural |
| `neophobia_p` | 0 | utils | -2, 0, 1 | judgement |  | behavioural |
| `neophobia_x0` | -2.8 | utils | -3.5, -2.8, 1.5 | published |  | DATA-ANCHORED |
| `p_innov` | 0.02 | 1/yr | 0.005, 0.02, 0.05 | published |  | literature |
| `q_imit` | 0.4 | 1/yr | 0.2, 0.4, 0.6 | published |  | literature |
| `accept_rate` | 0.15 | 1/exposure | 0.05, 0.15, 0.5 | judgement |  | assumed |
| `repeat_rate` | 0.62 | of first-time buyers | 0.5, 0.62, 0.75 | company |  | GFI, 'Analyzing plant-based meat and seafood sales', SPINS consumer panel to 30 Nov 2025 |
| `lapse_rate` | 0.14 | 1/yr | 0.05, 0.14, 0.3 | derived |  | derived from GFI/SPINS household reach |
| `milestone_year_breakthrough` | 10 | year | 5, 10, 20 | judgement |  | assumed |
| `biomass_cost_nearterm` | 25.2 | $/kg | fixed | derived |  | derived |
| `scaffold_frac` | 0.2 | kg/kg | 0.1, 0.2, 0.5 | judgement | **[share]** | assumed; products: structuring_cost.md |
| `material_price` | 2 | $/kg | 1, 2, 5 | published |  | TVP, extrusion, binders: structuring_cost.md |
| `process_cost` | 2 | $/kg | 0.5, 2, 7 | published | **[share]** | analogues: structuring_cost.md |
| `p_conv_premium_fish` | 25 | $/kg | 20, 25, 30 | published |  | market |
| `p_conv_sushi_salmon` | 40 | $/kg | 32, 40, 48 | published |  | market |
| `ts_ph_relaxed` | 2 | x the safe dose | 1, 2, 3.4 | derived |  | derived, research_notes/gas_exchange_study.md section 8 |
| `ts_loop_hw_exp` | 0.3 | - | 0, 0.3, 0.4 | judgement |  | assumed |
| `ts_hazard_exp` | 0.333 | - | 0, 0.333, 0.667 | judgement |  | assumed |
| `tc_phi_max` | 0.65 | volume fraction | 0.64, 0.65, 0.74 | published |  | Iordan, Duperray and Verdier 2007, arXiv:0709.3671, read in full |
| `tc_thin` | 1.33 | - | 1, 1.33, 3 | published |  | Tregidgo et al. 2023, Chem Eng Res Des 194:344, read in full |
| `tc_kla_exp` | 0.4 | - | 0, 0.4, 0.6 | published_partly |  | Yagi and Yoshida 1975, as listed in a university course note, snippet |
| `tc_np` | 5 | - | 1.3, 5, 5 | published |  | Tregidgo et al. 2023, read in full |
| `tc_re_turb` | 10000 | - | 5600, 10000, 10000 | published |  | Tregidgo et al. 2023, read in full |
| `tc_bubble_mm` | 3.5 | mm | 2, 3.5, 5 | published |  | research_notes/gas_flow_cap.md, section 3, citing a bubble-column measurement in synthetic medium with poloxamer |
| `tc_holdup` | 0.04 | of the tank | 0.03, 0.04, 0.06 | published |  | research_notes/gas_flow_cap.md, section 3 |
| `tc_yield_sigma` | 1.4 | Pa | 0.5, 1.4, 5 | published |  | Iordan, Duperray and Verdier 2007, read in full |
| `tc_yield_exp` | 8.4 | - | 6, 8.4, 11 | published |  | Iordan, Duperray and Verdier 2007, read in full |
| `tc_peak_dissipation` | 50 | - | 20, 50, 100 | published_partly |  | Humbird 2021, Eq. 2.17 after Nienow 2010, read in part |
| `tc_jacket_u` | 400 | W/m2/K | 200, 400, 700 | judgement |  | assumed |
| `tc_cool_dt` | 10 | K | 5, 10, 15 | judgement |  | assumed |
| `ml_dry_mol_kg` | 13.6 | mol/kg wet | fixed | derived |  | Humbird-R, derived |
| `ml_n_per_dry` | 0.21 | mol N/mol dry | fixed | published |  | Humbird-R |
| `ml_aa_pure_kg` | 0.26 | kg/kg wet | fixed | published |  | Humbird-R |
| `ml_aa_mw` | 128 | g/mol | 120, 128, 140 | published |  | textbook |
| `ml_glc_mw` | 180.16 | g/mol | fixed | published |  | textbook |
| `ml_salts_osm` | 250 | mOsm/kg | 150, 250, 260 | judgement |  | judgement; research_notes/min_litres_per_kg.md |
| `ml_feed_g_l` | 100 | g/L | 50, 100, 200 | judgement |  | judgement; research_notes/min_litres_per_kg.md |
| `ml_nh3_chogs` | 0.012 | mol/kg wet | 0.0063, 0.012, 0.029 | derived |  | Mayrhofer et al. 2020, via waste_tricks_sizing.md B2, derived |
| `ml_atp_bio` | 1.6e-11 | mol ATP/cell | fixed | published_partly |  | Kilburn, Lilly and Webb 1969, J Cell Sci 4:645, via the BioNumbers page (ID 101985), read |
| `ml_atp_maint` | 2.9e-11 | mol ATP/cell | fixed | published |  | Kilburn et al. 1969, as above |
| `ml_kilburn_td_h` | 27.6 | h | fixed | published |  | Kilburn et al. 1969 |
| `gb_conc_insulin` | 0.0194 | g/L | fixed | company |  | Humbird-R Sect. 3.1, FT; GFI 2023 footnote 4, FT; Chen et al. 2011 Essential 8 |
| `gb_conc_transferrin` | 0.0107 | g/L | fixed | company |  | Humbird-R Sect. 3.1, FT; GFI 2023 footnote 4, FT |
| `gb_conc_fgf` | 0.0001 | g/L | fixed | company |  | Humbird-R Sect. 3.1, FT; GFI 2023 footnote 4, FT |
| `gb_conc_tgfb` | 2e-06 | g/L | fixed | company |  | Humbird-R Sect. 3.1, FT; GFI 2023 footnote 4, FT |
| `gb_price_insulin` | 7 | $/g | fixed | published |  | Humbird-R Table 4.4, FT |
| `gb_price_transferrin` | 12 | $/g | fixed | published |  | Humbird-R Table 4.4, FT |
| `gb_price_fgf` | 649 | $/g | fixed | published |  | Humbird-R Table 4.4, FT |
| `gb_price_tgfb` | 18837 | $/g | fixed | published |  | Humbird-R Table 4.4, FT |
| `gb_pv_intercept` | 4.9 | log10 $/kg | fixed | published |  | Humbird-R Eq. 3.4, FT |
| `gb_pv_slope` | 0.861 | - | fixed | published |  | Humbird-R Eq. 3.4, FT |
| `gb_gfi_target_rp` | 1 | $/g | fixed | company |  | GFI 2023 (Swartz et al.), Table 1, FT |
| `gb_gfi_target_gf` | 100 | $/g | fixed | company |  | GFI 2023, Table 1, FT |
| `gb_gfi_litres_low` | 8 | L/kg | fixed | company |  | GFI 2023, Box 2, FT; Sinke et al. 2021 Table 16 |
| `gb_gfi_litres_mid` | 13 | L/kg | fixed | company |  | GFI 2023, Box 2, FT |
| `gb_gfi_litres_high` | 42 | L/kg | fixed | company |  | GFI 2023, Box 2, FT |
| `gb_mkt_insulin` | 24.75 | $/g | fixed | published_partly |  | Gotham, Barber & Hill 2018, BMJ Global Health 3:e000850, full text via Europe PMC |
| `gb_mkt_transferrin` | 182.3 | $/g | fixed | published |  | Stout et al. 2022 Beefy-9 Supplementary Table 3, read in full by the pf-tea evidence file |
| `gb_mkt_fgf2` | 196000 | $/g | fixed | company |  | GFI growth-factor-cost page, FT |
| `gb_mkt_fgf2_inhouse` | 7470 | $/g | fixed | company |  | GFI growth-factor-cost page, FT; Venkatesan et al. not read |
| `gb_mkt_tgfb` | 2.9e+07 | $/g | fixed | published |  | Humbird-R footnote 111, FT |
| `gb_floor_enzyme_lo` | 12 | $/kg | fixed | company |  | GFI 2023 footnote 8, FT, second-hand |
| `gb_floor_enzyme_hi` | 25 | $/kg | fixed | company |  | GFI 2023 footnote 8, FT, second-hand |
| `gb_floor_albumin_trade` | 55 | $/kg | 40, 55, 70 | company |  | pf-tea evidence, grade C: GFI 2025 and trade data |
| `gb_floor_tf_model` | 314 | $/kg | fixed | published |  | pf-tea model result, my own: results/analyses.json, case tf/100/humbird |
| `gb_floor_tf_published` | 949 | $/kg | fixed | published |  | pf-tea model result: tf_finnis2010/100/humbird |
| `gb_fgf2_half_life_h` | 10 | h | 5, 10, 10 | company |  | vendor pages and a review, SNIP |
| `gb_fgf2_g3_half_life_h` | 168 | h | 168, 168, 480 | company |  | Qkine and Reprocell vendor pages, SNIP; Dvorak et al. preprint reports >20 days |
| `gb_f_protein` | 0.7 | g/g dry | fixed | published |  | Humbird-R Table 2.1, FT |
| `gb_f_lipid` | 0.15 | g/g dry | fixed | published |  | Humbird-R Table 2.1, FT |
| `gb_f_carb` | 0.1 | g/g dry | fixed | published |  | Humbird-R Table 2.1, FT |
| `gb_f_rna` | 0.05 | g/g dry | fixed | published |  | Humbird-R Table 2.1, FT |
| `gb_dry_per_wet` | 0.3 | g/g wet | fixed | published_partly |  | Humbird-R, via pf_fat_kg |
| `gb_aa_g_mol` | 110 | g/mol | fixed | published |  | textbook, MEM |
| `gb_atp_peptide` | 4 | ATP/bond | 4, 4, 6 | published |  | textbook, MEM |
| `gb_lipid_g_mol` | 256 | g/mol | fixed | published |  | Humbird-R Table 2.1: lipid taken as palmitate |
| `gb_atp_fa16` | 42 | ATP/palmitate | 30, 42, 50 | published |  | textbook, MEM |
| `gb_nt_g_mol` | 330 | g/mol | fixed | published |  | textbook, MEM |
| `gb_atp_nt` | 9 | ATP/nucleotide | 6, 9, 12 | published |  | textbook, MEM |
| `gb_glycosyl_g_mol` | 162 | g/mol | fixed | published |  | textbook |
| `gb_atp_glycosyl` | 2 | ATP/unit | 1, 2, 3 | published |  | textbook, MEM |
| `gb_biosyn_overhead` | 1 | x | 1, 1, 1.6 | judgement |  | judgement |
| `gb_resp_scope` | 2 | x | 1.5, 2, 3 | judgement |  | judgement; typical maximal-to-basal respiration of cultured cells under an uncoupler is about 2-4, MEM, not read in this pass |
| `gb_elong_aa_s` | 5.6 | aa/s | 2, 5.6, 6 | published_partly |  | Ingolia et al. 2011, mouse embryonic stem cells; bionumbers snippet, SNIP |
| `gb_ribosome_kda` | 4300 | kDa | fixed | published |  | textbook, MEM |
| `gb_rrna_in_ribosome` | 0.65 | of ribosome mass | fixed | published |  | textbook, MEM |
| `gb_rrna_in_rna` | 0.8 | of RNA | fixed | published |  | textbook, MEM |
| `gb_cho_mass_pg` | 1167 | pg wet | fixed | published |  | Humbird-R footnote 41, FT |
| `gb_cho_qo2_pmol_h` | 0.227 | pmol O2/cell/h | 0.214, 0.227, 0.24 | published_partly |  | Goudar et al. 2011, ABS, via species_cell_parameters.md |
| `gb_cho_doubling_h` | 15 | h | 14, 15, 16 | published |  | species_cell_parameters.md |

## 4. The checks

### 4.1 The back-test against Humbird's own tables (`humbird_check.py`)

The engine run at Humbird's own conditions (his cells, tanks, plant cost, yearly charge, nutrient cost and limits; everything he does not count switched off), in his 2018 dollars, against his Tables 4.7 and 4.13. The line-by-line tables are in `research_notes/humbird_backtest.md`; `tests/test_humbird_check.py` holds each line within its tolerance (5% a line, 3% on the total, unless a residual below is named).

| design | Humbird, 2018 $ | engine at his conditions, 2018 $ | gap | engine, 2025 $ | tolerance on the total | within it |
|---|---:|---:|---:|---:|---:|---|
| Fed-batch, enhanced cells, amino acids | 36.79 | 36.37 | -1.1% | 47.11 | 3% | yes |
| Fed-batch, enhanced cells, soy hydrolysate (his best estimate) | 21.00 | 20.65 | -1.7% | 26.99 | 3% | yes |
| Fed-batch, wild-type cells, amino acids | 236.58 | 261.61 | +10.6% | 344.25 | 12% | yes |
| Fed-batch, wild-type cells, soy hydrolysate | 225.03 | 248.15 | +10.3% | 327.03 | 12% | yes |
| Perfusion in 2 m3 tanks, enhanced cells, amino acids | 51.29 | 49.74 | -3.0% | 64.73 | 5% | yes |

The residuals that could not be closed from his report, each with its reason:

- Perfusion in 2 m3 tanks, enhanced cells, amino acids, Utilities: gap -26.9% (tolerance 30%). His plant of 2 m3 tanks uses 26.5 litres of process water a kilo ($0.53, Table 4.11); the engine counts the medium (12.5 L) and the tank's cleaning at his fed-batch rate (0.5 L). His report does not itemise the other 13.5 L; daily cleaning of the 192 day tanks would fit.
- Fed-batch, wild-type cells, amino acids, Labour: gap +15.6% (tolerance 20%). His wild-type plant has 81 staff where the enhanced one has 95; the engine keeps the crew per m3 of tank.
- Fed-batch, wild-type cells, soy hydrolysate, Labour: gap +14.8% (tolerance 20%). As the amino-acid column: 81 staff against 95.
- Fed-batch, wild-type cells, amino acids, Plant (capital charge, maintenance, insurance): gap +13.2% (tolerance 16%). His wild-type plant costs $286M against $328M for the same 24 tanks: the oxygen plant, the utilities and the medium equipment are sized for 6% of the output. The engine's plant is the enhanced one's, scaled with tanks.
- Fed-batch, wild-type cells, amino acids, capex: gap +14.6% (tolerance 16%). As its plant line.
- Fed-batch, wild-type cells, soy hydrolysate, Plant (capital charge, maintenance, insurance): gap +12.2% (tolerance 16%). As the amino-acid column: $288M against $330M.
- Fed-batch, wild-type cells, soy hydrolysate, capex: gap +13.8% (tolerance 16%). As its plant line.
- Perfusion in 2 m3 tanks, enhanced cells, amino acids, Plant (capital charge, maintenance, insurance): gap -5.5% (tolerance 7%). The engine prices his 2 m3 plant 6% under his: its seed train, sterilisers, centrifuges and outside utilities stay at the fed-batch plant's cost per m3 of tank ($286k), where his 2 m3 plant spends $493k per m3 on them.
- Perfusion in 2 m3 tanks, enhanced cells, amino acids, capex: gap -6.0% (tolerance 7%). As its plant line.

What this model adds to his best estimate, one lever at a time from the page's start ($26.99, 2025 dollars):

| lever switched on alone | adds, $ a kilo |
|---|---:|
| Thick cultures take up oxygen more slowly | +0.00 |
| A least flow of medium the cells need | +0.00 |
| Cells killed by bursting bubbles | +2.35 |
| Cells lost at harvest | +0.55 |
| A bubble protectant in the medium | +0.50 |
| all of them together | +3.50 |

### 4.2 Five checks on the response to price (`demand_checks.py`)

The demand model has never seen cultivated meat on sale, so its response to price is checked against five measurements of novel or premium foods. Details in `research_notes/demand_checks.md`; `tests/test_demand_checks.py` pins each result. The pass rule for each is stated in the row.

| check | measured | the model | rule | result |
|---|---|---|---|---|
| 1. Cultivated meat at first contact and equal price: own-price elasticity (Van Loo, Caputo and Lusk 2020, simulated from the paper's fitted model) | about -1.5 (-1.1 to -1.65 across its arms) | -1.17 | inside the arms' range | passes |
| 2. Share of a meat at 3 times the ordinary one's price (sixteen premium real meats, fitted; `premium_curve.py`) | 1.5% | 6.2% | within a factor of 1.3 | **misses** |
| 3. A premium product getting cheaper: % more volume per % lower price (farmed salmon while it was premium) | 1 to 1.5 | 1.5 to 3.5 (the model's premium products still dearer than their meat at the low-lactate example's cost) | every product inside the range | **misses** |
| 4. Plant-based meat's own-price elasticity (US retail; GFI/NielsenIQ) | -1.23 (category -2.5 to -0.6) | -1.03 | inside the category's range | passes |
| 5a. Adding plant-based meat priced like meat to a menu: fall in meat's share, points (Hope 2026, US) | 2.1 (95% interval 0 to 4.4; 5 or more ruled out) | 0.54 | inside the interval, under the ruled-out size | passes |
| 5b. The same menu: share of the new option's orders taken from meat | about 30% | 79% | under 50% | **misses** |

Misses: 3 (farmed salmon), 5b (where the menu's new orders come from), 2. In the model a flat logit within each group of shoppers takes a new option's sales from each product in proportion to its share, so most of plant-based meat's orders come from meat, the largest product; the menu experiment found most came from the vegetarian option. The salmon check says the model's premium products respond more strongly to price than farmed salmon did.

### 4.3 The published cost studies (`study_assumptions.py`, `research_notes/study_comparison.md` section 13)

Each study's design as a set of modifications on Humbird's best estimate, with its assumptions made reasonable but ambitious long-term estimates and corrected where they break a limit of this model (every assumption, what the study says and where, what the set uses and why: section 13 of the note; `tests/test_study_assumptions.py` checks that every lever a set moves has a row). Plant is every cost that scales with what the plant cost to build; running is the rest.

| set | the study's own figure | this engine, $ a kilo of cells | plant | running |
|---|---|---:|---:|---:|
| Humbird's perfusion design (2021) | $51.29 a kilo of wet cells in 2018 dollars with amino acids bought one by one (his Table 4.13) | 50.48 | 32.94 | 17.54 |
| CE Delft 2021's assumptions on Humbird's design | $6.43 a kilo of meat in its most favourable scenario | 12.96 | 5.28 | 7.67 |
| Risner 2021's assumptions on Humbird's design | $1.95 a kilo of wet cells in 2019 dollars (scenario 4) | 10.95 | 3.39 | 7.56 |
| Negulescu 2023's assumptions on Humbird's design | $35 a kilo of product with 42 m³ tanks | 11.06 | 4.85 | 6.21 |
| Garrison 2022's assumptions on Humbird's design | $17.10 a kilo of meat, packed and delivered, in its most favourable variant; $63.69 as its base case | 10.97 | 5.39 | 5.58 |
| Pasitka 2024's assumptions on Humbird's design | $24.06 a kilo of wet cells for this design in 2024 dollars (its Table S10), or $32.66 with the payment on the plant its Table S4 works out | 17.63 | 11.51 | 6.12 |
| SuperMeat 2024's assumptions on Humbird's design | $29.5 a kilo of cultivated chicken with depreciation (derived from $13.4 a pound) | 25.46 | 13.64 | 11.82 |
| Ark Biotech 2023's assumptions on Humbird's design | $4.4 a kilo of cells with all four of its levers ($2.0 a pound); $65.0 as its baseline | 28.75 | 19.28 | 9.47 |
| Gourmey and Arthur D. Little 2025's assumptions on Humbird's design | €7 a kilo, of cells or of a product half cells (not stated) | 16.65 | 9.63 | 7.02 |

Each study's own most favourable estimate, in 2025 dollars a kilo of wet cells, against the all-favourable example ($6.97):

| study | its estimate as published | as a kilo of wet cells, 2025 $ | below the all-favourable example |
|---|---|---:|---|
| Humbird 2021 | $21.00 a kilo of wet cells | 26.92 |  |
| CE Delft 2021 | $6.43 a kilo of cultivated meat | 7.64 |  |
| Risner 2021 | $1.95 a kilo of cell-based meat | 2.46 | yes |
| Negulescu 2023 | $16 a kilo of product without depreciation, $17 with | 18.15 |  |
| Garrison 2022 | $63.69 a kilo of meat; $17.10 with the cheapest published medium and tanks and labour cut by 75% | 18.81 |  |
| Pasitka 2024 | $6.2 a pound of a product that is half cells | 21.90 |  |
| SuperMeat 2024 | $11.8 a pound without depreciation, $13.4 with | 26.70 |  |
| Lever VC 2025 | $10 to $15 a kilo of cell mass; some companies below $10, with no figure | 10.00 |  |
| GFI 2021 | $6.43 a kilo ($2.92 a pound) | 7.64 |  |
| GFI 2026 | no cost published | not compared: it gives no cost of cells or of meat, only prices of medium a litre |  |
| Ark Biotech 2023 | $2.0 a pound with all four of its levers ($29.5 as its baseline) | 4.66 | yes |
| Cellular Agriculture Ltd 2024 | £14.68 a kilo of cultured biomass (factory of 60 tonnes a week) | 19.28 |  |
| Gourmey and Arthur D. Little 2025 | €7 a kilo ($3.43 a pound) | 7.56 |  |
| Aleph Farms and Eridia 2025 | as low as $4.08 a pound of end products ($6.45 as its estimate, with the plant) | 8.99 |  |

- Risner 2021 is below it because of assumptions beyond this model's limits: 200 million cells a mL, each of 5,000 µm³ (scenario 4) (breaks: the thickest culture that still flows); cells that double every 8 hours (scenario 4) (breaks: a growth rate faster than any measured in animal cells); 0.0356 mol of glucose a litre in 7.1 litres of medium a kilo of cells (scenario 4) (breaks: the mass balance: cells cannot be built and fuelled from less sugar than they burn); a cell of 5.00e-15 m³ at 1,060 kg per m³, 5.3 ng (every scenario) (breaks: a meat cell heavier than any measured growing in suspension). Inside the limits its design costs $8.62.

- Ark Biotech 2023 is below it because of assumptions beyond this model's limits: the plant written off over 15 years with no interest (breaks: the plant must be repaid at a market rate of interest).

## 5. Dead ends and corrections, dated

Assumptions, anchors and structures tried in this model and withdrawn or corrected, oldest first, so they are not tried again without new evidence. Each names the file where it is recorded.

| date | what was tried | why it was withdrawn, and what replaced it | recorded in |
|---|---|---|---|
| 2026-11-13 | The note said the loss-aversion parameter lambda leaves the regional roll-up unchanged. | Corrected: absorbing lambda pushes the price weight beta positive (+0.051 at 2.25), so poorer shoppers become less price-sensitive and the world share rises from 2.5% to 6.3%. The default stays 1.0, the range is capped at 2.25, and results with lambda above about 1.65 are flagged as not meaningful. | inputs.py, the loss_aversion note (corrected 2026-11-13) |
| 2026-11-14 | Pasitka et al. 2024 was the model's cost anchor. | Dropped as the anchor because its kilogram is a wet pellet that is mostly liquid and its cost leaves out capital. The default was re-anchored on SuperMeat 2024's reported process, with a floor from physics. | CHANGELOG.md 2026-11-14; METHODS.md, "Why Pasitka is not the anchor"; inputs.py, "RE-ANCHORED 2026-11-14" |
| 2026-11-14 | One number, cult_sub_mult, set the price weight beta that every product shares. | Raising it made shoppers more sensitive to every price, beans and plant-based meat included, and strained the calibration (at 9 a solved weight fell to zero). It was split: kappa_base (4) sets beta, and cult_sub_mult / kappa_base scales only cultivated meat's price difference from conventional meat. | inputs.py, the kappa_base note (ADDED 2026-11-14) |
| 2026-11-15 | $11.5 a kilo from floor_physics.explore() at its defaults was presented as the floor. | The name was retired: it was neither the most favourable case nor a typical one (20 m³ perfusion, 120 g/L, no tank tricks, no lost runs). It is kept as a labelled reference, Humbird's optimistic design, and the scenarios are built from switches. | CHANGELOG.md 2026-11-15, "Cost scenarios in place of the floor" |
| 2026-11-15 | Perfusion used a hoped-for cell-retention device with a flat capital and no membrane cost. | Replaced as the default by a priced hollow-fibre filter loop (membranes about $0.37 a litre filtered). The most favourable scenario went from $6.57 to $8.95 and no scenario reached price parity. The old device stays behind rt_tff_default = 0. | CHANGELOG.md 2026-11-15, "The filter loop is the model's default" |
| 2026-11-15 | Antifoam took nothing off oxygen transfer, and the bubble protectant (poloxamer 188) was not charged. | Antifoam's central value became 0.75 (the middle of the reported 0 to 50% cut), so oxygen now limits the low-lactate example. The protectant is charged at 2 g/L at an assumed bulk price below the $230 to 260 catalogue price, pending a supplier quote. | CHANGELOG.md 2026-11-15, "Three costs counted"; TODO.md |
| 2026-11-16 | The protectant price prior ran from $10 to $260 a kg, with the catalogue price as its top. | At that top the median tonne price drawn was $87, above what the catalogue-to-bulk gap suggests. The range was cut to $10 to 120, and later to $5 to 100 (2026-11-21). | CHANGELOG.md 2026-11-16, "Wider bands"; research_notes/evidence_poloxamer_price.md |
| 2026-11-16 | The dollar channel's price coefficient in _derive_beta was left uncapped. | Loss aversion above about 1.6 drove it positive, so paying more raised utility and the share rose with loss aversion (0.4% to 1.4%). It is capped at zero in Python and on the page. The split between dollars and ratios is still open. | CHANGELOG.md 2026-11-16, "Demand flaw"; TODO.md |
| 2026-11-16 | The sorbent lever lowered the litres through the cell filter along with the fresh medium. | Corrected: the liquid a device on the permeate cleans has already passed the cell filter. A sorbent taking half the ammonia gives $28.22, not $22.97. Cleaning the permeate saves $2 to 4 a kilo, not more. | CHANGELOG.md 2026-11-16; research_notes/medium_reuse.md |
| 2026-11-16 | The scenarios held dissolved oxygen at Humbird's implied 0.28 mmol/L (130% of air saturation). | Pharma holds 30 to 50%, so the scenarios hold 0.10 mmol/L (sc_do_setpoint). Humbird's optimistic design keeps his level. | CHANGELOG.md 2026-11-16 |
| 2026-11-18 | The step from a kilo of cells to the shelf was a flat $5 a kilo (range $3 to 8.7). | Shop prices move about dollar for dollar with wholesale prices, but shops set a percentage margin (USDA ERS). The rule is now (cost + $2.5) / (1 - 28%). Parity moved from $7.00 to $6.14 a kilo of cells. A claim that margins rise with the quality tier was unsourced, and the one comparison found runs the other way. | CHANGELOG.md 2026-11-18; research_notes/retail_markup_form.md |
| 2026-11-18 | The premium rows of the market tables (sushi-grade seafood 5.4 Mt, prime beef, heritage pork and organic chicken 1.35 Mt each) were used without a source. | They were several times too large (about 1.2, 0.5, 0.4 and 0.4 Mt). Resizing cut the low-lactate example's share from 0.16% to 0.04%. An earlier agreement with the premium-meat anchoring was a coincidence of the oversized rows. | CHANGELOG.md 2026-11-18; research_notes/premium_market_sizes.md |
| 2026-11-18 | A recalibration treated buyers of organic and welfare-labelled meat as cultivated meat's price-insensitive buyers. | Not merged. In the two studies that split shoppers into groups, the price-insensitive organic buyers are the most hostile to cultivated meat. It was replaced by a spread of liking across all shoppers. | research_notes/premium_buyers.md; research_notes/liking_spread.md section 1; TODO.md |
| 2026-11-18 | The demand check used -0.84 to -3.4 as the choice experiment's measured elasticity. | That range is a formula on two of the experiment's coefficients, not a reported elasticity. The experiment's fitted model simulates to about -1.5, which the check now uses. | CHANGELOG.md 2026-11-18; research_notes/demand_heterogeneity_evidence.md |
| 2026-11-19 | Shoppers' liking was a normal spread of 5 utils integrated on 15 points. | Fifteen points were too few (integrated properly it gave -1.34, not -1.53, and missed the experiment), and a normal tail fell too fast above parity (0.1% at 4 times the price against premium meats' 0.6%). Replaced by a Student's t, refitted on 2026-11-22 to 3.55 utils and tail 7. | CHANGELOG.md 2026-11-19; research_notes/liking_spread.md section 2 |
| 2026-11-19 | A tier rule made buyers of cuts and premium products less price-sensitive (x0.8, x0.3), and a product became premium at 2.5 times its species' cheapest form. | It worked backwards above about 1.5 times the price: more resistance gave cultivated meat a higher share (it added 41% to the low-lactate example). Removed. A cut now carries a penalty for its non-cell part, and premium products an offset that rises smoothly from 2 to 4 times the cheapest form. | research_notes/audit_2026-11-19.md finding D3; CHANGELOG.md 2026-11-19 |
| 2026-11-19 | The bands drew the equal-price share from a triangular 5/13/49% distribution. | Its median was 21%, well above the 13% point it was meant to surround. It is now lognormal around 13%. | research_notes/audit_2026-11-19.md finding D1 |
| 2026-11-19 | Every scenario took an ammonia tolerance of 5 mmol/L. | The model's own evidence note gives a median of 3.5 to 4. Set to 4 mmol/L (sc_nh3_limit, range 2 to 8); Humbird's optimistic design keeps 5. | research_notes/audit_2026-11-19.md finding C2 |
| 2026-11-19 | Published cells were given 0.84 mol of glucose a kilo, a figure drawn partly from CHO data and Pasitka's per-kilo-of-biomass figure. | 0.84 could not supply their own oxygen use. Glucose now comes from the cells' own balance (about 4.5 mol a kilo), so lactate sets their medium at about 95 litres a kilo, not 28. | research_notes/audit_2026-11-19.md finding C5 |
| 2026-11-19 | A kilo of cut was charged a full kilo of cells plus a $6 scaffold. | The scaffold sat on top of the cells it replaces, and companies dropped scaffold-grown tissue. A kilo of cut is now 0.8 kg of cells, 0.2 kg of plant-protein matrix and an assembly cost. | CHANGELOG.md 2026-11-19; research_notes/structuring_cost.md |
| 2026-11-19 | The nutrient floor was $1.70 a kilo on soy hydrolysate, medium settings at $0.05 and $0.15 a litre were offered, and growth factors were bought on top of announced medium prices. | Hydrolysate cannot supply glutamine, arginine, asparagine, cystine or serine. The floor became $2.00 (232 g of feed-grade amino acids at $6.36, GFI December 2025). The two cheap settings were dropped. Announced prices are treated as complete media with growth factors inside; without that rule a culture under about 20 L a kilo got its growth factors free. | research_notes/nutrient_floor.md section 6; research_notes/growth_factors_in_medium_price.md |
| 2026-11-19 | The density of a tank that is not perfused was Humbird's 120 g/L scaled by the waste the cells make. | This broke the waste mass balance. The density is now end factor x level allowed / waste per kilo. The low-lactate example's batch fell from 56 to 37 g/L. | CHANGELOG.md 2026-11-19; TODO.md |
| 2026-11-19 | A forecast for 2035 (a Monte Carlo over the switches, with odds for each way of reaching a trait) was built. | Dropped the same day: the model gives no forecasts. The record of its odds was deleted on 2026-11-21. | CHANGELOG.md 2026-11-19 and 2026-11-21 |
| 2026-11-19 | Hypothetical sets of cells were given names, with tags saying how the cells would be obtained. | All named kinds of cell were retired the same day. Cells are described only by their traits (the low-lactate example, the all-favourable example), each trait is set against the best value measured in meat cells, and no claim is made about how cells would come to have a trait. | CHANGELOG.md 2026-11-19, "Names" |
| 2026-11-19 | The share reported was cultivated meat's share of all four choices. | A flat market at 50% of meat buyers showed 46.5%. The share is now x / (x + c), the share of the meat sold. Shares rose about a quarter at the low-lactate example's cost. | CHANGELOG.md 2026-11-19 and 2026-11-21 |
| 2026-11-19 | The headline share was the median of the Monte Carlo band, and the page led with the median cost and an 8-in-10 range. | The all-favourable example's point sat below the 10th percentile of its own draws, and a median mixed cost and demand draws. The page shows the cost at the settings shown, with the draws in their own section. | CHANGELOG.md 2026-11-19 and 2026-11-21 |
| 2026-11-19 | A source text said a protectant cuts bubble deaths at least 100-fold. | Jöbses 1991, the model's own input, gives about 20-fold at 1 g/L. | CHANGELOG.md 2026-11-19, "Two source texts corrected" |
| 2026-11-20 | The scenarios' cells tolerated 50 mmol/L of lactate with no range. | That value decided the fed-batch cost ($209 at 50, $298 at 35). It is now 35 (sc_lac_limit, 20 to 50, drawn). Humbird's design keeps 50. | research_notes/full_review_2026-11-19.md section 7; CHANGELOG.md 2026-11-20 |
| 2026-11-20 | Filter membranes were given a life of 3,960 L/m² at the pharma price. | That was the generous end (CHO membranes fouled after 450 to 1,200 L/m²; the evidence median is about 1,500). It is now Humbird's own replacement schedule at his price, 2,415 L/m². | research_notes/filter_flux.md; CHANGELOG.md 2026-11-20 |
| 2026-11-20 | Plant-based meat's anchor was 1.2% of meat by volume, and regional incomes were at purchasing-power parity with an income gradient of 0.5. | The 1.2% contradicted its own note (under 1% by volume) and became 0.4%. Incomes became nominal GDP per head, with the gradient solved again (0.32). | CHANGELOG.md 2026-11-20; inputs.py, the pb_share_target note |
| 2026-11-20 | The all-favourable example took 5.3 ng a cell from Risner 2021 (and CE Delft 2021's 5.2 and 3.6 ng). | Those are assumptions of the analyses, not measurements, and no meat cell in suspension has been measured above about 2.3 ng. Rejected; the bound is Humbird's 3 ng. Pasitka's 3.3 and 9.8 ng are wet-pellet weights and are not used. | research_notes/study_comparison.md sections 5 and 12 |
| 2026-11-20 | Consumer-price factors for other years' dollars were typed from memory, and Humbird's yeast benchmark was read as support for cheaper financing. | The factors are BLS CPI-U annual averages stored in inputs.py. The benchmark is 10% over 20 years, a higher rate than his 7.5%. CE Delft states payback years with no interest rate. | research_notes/study_comparison.md sections 10 and 12 |
| 2026-11-20 | The engine priced Humbird's growth factors over 11.2 L a kilo and charged his utilities as a flat $0.94 a kilo. | Both misread his tables. Growth factors are over his fed-batch's 8.65 L a kilo, and utilities have four parts (by time, run, litre and kilo). | research_notes/humbird_backtest.md, "Gaps found" |
| 2026-11-21 | In a tank that is not perfused, the least medium flow capped the density, held to 1.0 times the perfusion level. | A counting error: the by-products it stands for may end a batch 1.3 times above the level, as ammonia and lactate do. It no longer binds Humbird's design; the page's start with the additions went from $37.38 to $30.49. | research_notes/humbird_backtest.md item 11; CHANGELOG.md 2026-11-21 |
| 2026-11-21 | Fed-batch at 100 m³ was compared with perfusion at 20 m³, which made the batch look cheaper. | Like for like, perfusion is cheaper at every size up to 100 m³ in every rung. Only cells making almost no ammonia or lactate at 200 m³ favour fed-batch. | CHANGELOG.md 2026-11-21; TODO.md |
| 2026-11-24 | Published estimates that write the plant off with no interest (Ark Biotech 2023, Cellular Agriculture Ltd 2024, CE Delft 2021, Pasitka 2024 with no plant payment) were candidates for the favourable end. | Rejected: a long-run price must repay the plant at a market rate. Pasitka's own Table S4 charge, with the plant included, gives a higher cost than its headline. | research_notes/study_comparison.md sections 5 and 12; research_notes/evidence_pasitka_supplement.md |

Still open (decisions, not withdrawn):

- Whether the range of the long-run share at equal price for the ordinary demand (`equal_price_share`) should reach about 60%, now that the all-favourable example assumes about that share of meat buyers (TODO.md).
- How much the price-insensitive shoppers like cultivated meat: most of the low-lactate example's sales go to them (research_notes/demand_checks.md section 7; TODO.md).
- Whether to add a nest for meat-free options, since the flat logit takes most of plant-based meat's choices from meat against about 30% measured on a menu (research_notes/demand_checks.md section 8; TODO.md).
- Membrane life and price are drawn separately in the bands; drawing price over life as one quantity would change every band (TODO.md).
- How the price response splits between dollars and the ratio to meat's price, which no data pin (`w_ratio`; TODO.md).

## 6. Open questions, ranked by how much they would move the answer

Ranked by how far the input, moved across its range, moves the low-lactate example's long-run share of world meat (a cost input moves the share through the cost). Each comes with the measurement that would settle it, and the current evidence (`answer_rests_on.EVIDENCE`). Inputs whose evidence is an observed price or a measured elasticity are listed for completeness: the ranking is by leverage, not by weakness of evidence.

| rank | input | moves the low-lactate example's share | moves the cost | evidence now | the measurement that would settle it |
|---:|---|---|---|---|---|
| 1 | Share of buyers who choose cultivated meat at equal price, once familiar (`equal_price_share`) | 0.093% to 4.3% (all-favourable 2.2% to 42.9%) | no | a judgement: an even split for meat buyers, the neutral start where no good data exist (since 2026-11-24; 13% of all choices before); the literature review puts the 10th, 50th and 90th percentiles at 2%, 10% and 35% (`what_drives_choice.md`) | a repeated-purchase study (a market test or a panel) of a cultivated product sold at the price of the meat it copies, after the first purchase: the share of meat buyers who keep choosing it |
| 2 | How much more price-sensitive cultivated meat is than meat in general (`cult_sub_mult`) | 3.0% to 1.0% (all-favourable 28.8% to 18.0%) | no | bracketed by data on close substitutes | a price-variation test of cultivated meat on sale (a discount or a premium at random stores or weeks): its own price elasticity against that of the meat it copies |
| 3 | How much more the price-insensitive shoppers like cultivated meat than other shoppers, utils (`price_insensitive_liking`) | 0.69% to 2.7% (all-favourable 20.0% to 21.3%) | no | two latent-class studies, read in utils: no more hostile than other shoppers (`demand_checks.md` section 7) | the same analysis: the two classes' liking for cultivated meat, in utils |
| 4 | Price elasticity of meat demand (`eps_own`) | 0.90% to 2.5% (all-favourable 17.2% to 26.7%) | no | scanner-data meta-analysis | already measured (scanner meta-analyses); a test on cultivated meat itself would replace it |
| 5 | Litres a m² of cell filter passes before it is replaced (`rt_membrane_life`) | 0.55% to 2.1% | $86.9 to $35.9 (all-favourable $7.0 to $7.0) | derived from pharma runs (fouled in 4.5 days to lasted 30); no meat-cell run; probably the generous end (median about 1,500), and read with the membrane price | the litres a square metre of cell filter passes before it is replaced, in a long meat-cell perfusion run |
| 6 | How wary people are of a novel food, in the long run (`neophobia_x`) | 0.63% to 2.1% (all-favourable 11.2% to 26.4%) | no | a judgement on long-run behaviour | the share of first-time buyers who buy again, months after launch |
| 7 | Whether people see cultivated meat as healthier or less healthy (`health_x`) | 0.90% to 2.2% (all-favourable 14.7% to 27.3%) | no | a scenario dial: no data | a choice experiment that varies health information on cultivated meat |
| 8 | Share of shoppers who respond much less to price than the others (`price_insensitive_share`) | 1.4% to 2.6% (all-favourable 20.5% to 21.7%) | no | latent-class studies: 15-35% in stated choices, probably 8-15% in purchases; fitted within that to the demand checks (`demand_checks.md` section 7) | a latent-class analysis of purchase data (not stated choices) for a premium or novel meat |
| 9 | How strongly those price-insensitive shoppers respond to price, times other shoppers' response (`price_insensitive_response`) | 1.6% to 0.39% (all-favourable 20.5% to 20.2%) | no | 4-10 times between groups in purchases; fitted within that to the demand checks (`demand_checks.md` section 7) | the same latent-class analysis: the ratio of the two classes' price coefficients |
| 10 | Ammonia the cells tolerate in the tank (`sc_nh3_limit`) | 0.52% to 1.6% | $89.0 to $43.8 (all-favourable $7.0 to $6.9) | the evidence note's median, 3.5–4 mmol/L (80% interval 2–8): meat-relevant cells measured lose 10–55% of growth at 2.5–5, meat-cell processes hold 2–3, none measured at density | growth rate of meat cells at 2, 4, 8 and 16 mmol/L of ammonia, at production density in perfusion |
| 11 | Ammonia the cells of the low-lactate example make per kilo grown (`sc_nh3_selected`) | 1.6% to 0.64% | $44.5 to $80.4 (all-favourable $7.0 to $7.0) | measured once, in bovine cells with glutamine replaced (Hubalek 2023): 'more than 5-fold' below the 0.70 with glutamine | ammonia made per kilo of meat cells grown, measured in perfusion at density on a glutamine-free feed |
| 12 | How price sensitivity falls with income (`income_gradient`) | 1.8% to 0.87% (all-favourable 22.3% to 17.6%) | no | USDA demand estimates | price elasticities of meat by income group (already measured for conventional meat) |
| 13 | Value mainstream buyers put on meat without slaughter (`theta_free_M`) | 1.4% to 2.3% (all-favourable 20.5% to 27.3%) | no | a scenario dial: surveys disagree | a choice experiment that states the no-slaughter attribute and measures its value to mainstream buyers |
| 14 | How fully mainstream buyers credit cultivated meat's taste (`accept_x`) | 0.63% to 1.4% (all-favourable 11.2% to 20.5%) | no | a scenario dial | a blind sensory test of cultivated meat against the meat it copies |
| 15 | Retailer's gross margin, as a share of the shelf price (`retail_margin`) | 1.8% to 1.1% (all-favourable 25.8% to 15.2%) | no | US meat-department margins (28–32%) and French supermarket data | retailers' gross margin on a cultivated product once it is stocked at volume |
| 16 | Lactate the cells tolerate in the tank (`sc_lac_limit`) | 0.83% to 1.4% | $70.3 to $48.7 (all-favourable $7.0 to $7.0) | Cultivated Meat (book), Table 2, citing Hassell 1991; Pasitka 2024; Humbird 2021, judgement | growth rate of meat cells at 20, 40 and 80 mmol/L of lactate, at density |
| 17 | Lactate the cells of the low-lactate example make per mol of glucose (`sc_lac_selected`) | 1.4% to 0.93% | $48.7 to $65.5 (all-favourable $7.0 to $7.0) | waste_tricks_sizing.md | mol of lactate made per mol of glucose by meat cells at density, in perfusion |
| 18 | Culture whose cells bursting bubbles kill, per volume of gas passed (`ge_kill_protected`) | 1.5% to 1.1% | $45.7 to $58.9 (all-favourable $6.5 to $8.7) | Jobses, Martens, Tramper 1991, read in full | the share of meat cells killed per litre of gas sparged, with the bubble protectant, in a stirred tank |
| 19 | Price of everyday meat (`p_conv`) | 1.7% to 1.3% (all-favourable 21.8% to 19.7%) | no | market prices | observed; not open |
| 20 | Salt strength the cells tolerate (osmolality) (`pf_osm_limit`) | 1.1% to 1.4% | $57.9 to $48.7 (all-favourable $8.3 to $7.0) | CHO measurements (`perfusion_rate_osmolality.md`) | the growth of meat cells against osmolality (salt strength), at density |
| 21 | Share of mainstream meat meals where shoppers choose a whole-food plant protein instead of meat (`wf_mainstream_target`) | 1.4% to 1.7% (all-favourable 20.2% to 21.9%) | no | assumed, SOFT | no measurement named yet: add one to SETTLE in agents_edition.py |
| 22 | Price of cell-filter membrane (`rt_membrane_price`) | 1.7% to 1.4% | $42.4 to $48.7 (all-favourable $7.0 to $7.0) | Humbird's ATF price; retail modules a quarter less | a volume quote for hollow-fibre membrane, per m² |
| 23 | Yearly charge on the plant's capital (financing and recovery) (`plant_charge_mature`) | 1.6% to 1.3% | $45.6 to $52.6 (all-favourable $6.4 to $7.7) | derived from Humbird's financing, at a mature industry's rates | the financing terms (rate and years) lenders give a food-grade cell-culture plant |
| 24 | Price of the bubble protectant (poloxamer 188), bought by the tonne (`pf_protectant_price`) | 1.5% to 1.2% | $46.7 to $54.1 (all-favourable $6.4 to $8.7) | assumed: only catalogue prices ($230–260/kg) found | a bulk (tonne) quote for food-grade poloxamer 188 |
| 25 | How much shoppers differ in liking cultivated meat (`liking_sd`) | 1.3% to 1.6% (all-favourable 19.7% to 21.6%) | no | fitted to the one random-parameter choice experiment, premium real meats and farmed salmon, jointly | a random-parameter choice experiment on cultivated meat with real purchases, which estimates the spread of willingness to pay across shoppers |
| 26 | Whether a price above meat's hurts more than a price below helps (off by default) (`loss_aversion`) | 1.4% to 1.2% (all-favourable 20.5% to 16.3%) | no | an alternative model of price, not a measured value; with it, part of the price response moves from dollars to the ratio to meat's price | a test of whether shoppers respond more to a price above meat's than to one below it |
| 27 | Weight on the price compared with meat's (`w_ratio`) | 1.4% to 1.6% (all-favourable 21.2% to 19.9%) | no | judgement: how much of the price response is a ratio to meat's price rather than dollars | a choice experiment that varies the absolute price and the price relative to meat separately |
| 28 | Least medium flow the cells need for everything but ammonia and lactate (`pf_min_perfusion`) | 1.4% to 1.2% | $48.7 to $54.5 (all-favourable $7.0 to $7.0) | judgement within CHO measurements | the least medium flow per cell at which meat cells keep growing when ammonia and lactate are removed |
| 29 | Dose of bubble protectant in the medium (`pf_protectant_dose`) | 1.5% to 1.3% | $47.5 to $52.2 (all-favourable $6.6 to $8.1) | dense pharma cultures (`gas_flow_cap.md`) | the least dose of protectant that keeps meat cells alive under sparging |
| 30 | Cost of assembling a cut, beyond what mince pays (`process_cost`) | 1.5% to 1.3% (all-favourable 23.4% to 14.3%) | no | analogues, no study of cultivated meat: plant-protein extrusion, surimi forming, binder prices (`structuring_cost.md`) | the cost of assembling a cut at a pilot line, per kilo |
| 31 | Staff a plant in perfusion needs, against a fed-batch plant (`pf_labour_perfusion_x`) | 1.5% to 1.3% | $47.7 to $51.7 (all-favourable $6.7 to $7.9) | Humbird 2021; CE Delft 2021; SuperMeat 2024, derived | staff per tank in a perfusion plant against a fed-batch plant of the same output |
| 32 | Amino acids a kilo of cells takes up (the nutrient floor) (`aa_intensity`) | 1.4% to 1.3% | $48.7 to $51.5 (all-favourable $6.7 to $10.0) | GFI's eight estimates, 200–650 g; the model takes the most efficient (`nutrient_floor.md`) | the amino acids taken up per kilo of meat cells grown, from a mass balance on the medium |
| 33 | How the cost of medium preparation equipment rises with the medium passed (exponent) (`pf_medium_prep_exp`) | 1.4% to 1.3% | $48.7 to $51.1 (all-favourable $7.0 to $7.4) | assumed | quotes for medium-preparation equipment at two or more flows |
| 34 | Share of a cut that is plant protein, not cells (`scaffold_frac`) | 1.5% to 1.4% (all-favourable 21.5% to 17.9%) | no | assumed: the cuts sold or approved so far are 10–30% cells, and no mostly-cell cut has been shown with the texture of meat (`structuring_cost.md`) | the cell share of cuts that reach the texture of meat in a blind sensory test |
| 35 | Per-kg costs from cells to the shop shelf (forming, packing, cold chain), $ per kg (`markup_add`) | 1.5% to 1.4% (all-favourable 23.8% to 17.7%) | no | fitted to USDA ERS meat spreads, plus forming | the cost from harvested cells to the shelf (forming, packing, cold chain) reported by a producer selling at volume |
| 36 | Weight of one cell (every kind of cells since 2026-11-19) (`sc_mass_selected_pg`) | 1.4% to 1.5% | $50.1 to $47.9 (all-favourable $7.0 to $7.0) | judgement between the 1.0–1.75 ng reported for chicken cells and Humbird's 3 ng | dry and wet mass per cell of meat cells at harvest (a cell count against a weighed, drained pellet) |
| 37 | Rise in plant construction costs since 2018 (`pf_capex_escalation`) | 1.5% to 1.4% | $47.5 to $49.2 (all-favourable $6.8 to $7.1) | construction cost index, 2024 estimated | the construction cost index for the year the plant is priced |
| 38 | CO₂ level at which the culture leaves the stripping column (`ge_col_pout`) | 1.4% to 1.4% | $50.5 to $49.3 (all-favourable $7.2 to $7.0) | design choice | the CO₂ level a stripping column on a cell-culture loop reaches at its design flow |
| 39 | Price of amino acids (the nutrient floor) (`aa_bulk_price`) | 1.4% to 1.4% | $48.7 to $49.9 (all-favourable $6.6 to $8.3) | GFI's feed-grade mean of 22, to low food-grade (`nutrient_floor.md`) | food-grade bulk quotes for the amino acids of a defined medium, at tonne scale |

## 7. How to extend

### Run the model

```bash
pip install -r requirements.txt        # numpy and matplotlib; Node.js 18+ for the parity test
python inputs.py                       # the datasheet: every input, its source and range
python scenarios.py                    # the reference points: cost, density, limit, share
python humbird_check.py                # the back-test
python answer_rests_on.py              # what the answer rests on (several minutes)
python build_interactive.py            # rebuild interactive.html from the Python
./run_tests.sh                         # rebuild the page, then every test in parallel (15 to 20 minutes)
python agents_edition.py               # rewrite AGENTS.md, llms.txt and inputs.json
```

Run from the repository root. The scripts import each other by module name, so the root must be on `PYTHONPATH` (`PYTHONPATH=. python ...` if it is not).

### The tests (`run_tests.sh`)

- `tests/test_agents_edition.py`: the edition for AI agents matches the model (AGENTS.md, llms.txt, inputs.json)
- `tests/test_share_many.py`: the Monte Carlo's vectorised share against share(), and the plant-item cache
- `tests/test_golden.py`: golden-value regression
- `tests/test_growth_rate.py`: doubling-time envelope
- `tests/test_floor_physics.py`: physics-based floor
- `tests/test_plant_items.py`: plant by items, contamination
- `tests/test_scenarios.py`: cost scenarios
- `tests/test_vessels.py`: vessel types against operating modes
- `tests/test_retention.py`: cell retention for a 20 m3 perfusion tank
- `tests/test_downside.py`: downside: no perfusion at 20 m3
- `tests/test_tank_size.py`: cost against tank size
- `tests/test_thick_culture.py`: how thick a culture can be
- `tests/test_min_litres.py`: least medium per kg of cells that physics allows
- `tests/test_nutrient_floor.py`: nutrient floor
- `tests/test_gas_exchange.py`: gas-exchange side study
- `tests/test_gf_doubling_bounds.py`: growth-factor prices and the fastest doubling time
- `tests/test_audit.py`: model audit: global uncertainty and the retail translation
- `tests/test_frontier.py`: the path from Humbird's design to the all-favourable case
- `tests/test_ordering.py`: one all-favourable case, and the order of the reference points
- `tests/test_filter_flux.py`: the filter flux limit
- `tests/test_industry_claims.py`: the model against company claims
- `tests/test_design_space.py`: the tank design search
- `tests/test_premium_curve.py`: cultivated meat anchored on premium real meats
- `tests/test_premium_buyers.py`: cultivated meat competing with welfare labels for premium buyers
- `tests/test_market_size_loop.py`: cost falling with market size, solved with the share
- `tests/test_demand_checks.py`: the model's response to price against four measurements
- `tests/test_liking_spread.py`: a spread of liking for cultivated meat across shoppers
- `tests/test_answer_rests_on.py`: what the answer rests on
- `tests/test_medium_reuse.py`: cleaning and reusing the medium
- `tests/test_retail_spreads.py`: the retail markup rule against USDA's meat spreads
- `tests/test_humbird_check.py`: the engine against Humbird's own tables
- `tests/test_easy_view.py`: the page's short version
- `tests/test_study_assumptions.py`: published cost studies: Humbird's design with one study's assumptions at a time
- `tests/run_parity.py`: Python <-> JS parity

### Rules a change must keep

1. **Python is the source of truth.** Never hand-edit `interactive.html`: `build_interactive.py` writes it, ports the model to JavaScript and fills every number in its text. Change the Python, rebuild, then run `./run_tests.sh`. `tests/run_parity.py` checks the JavaScript against the Python to 1e-4.
2. **One source for every number.** A new number goes into `inputs.py` as an `Input` with its unit, a source tag in square brackets, a range if it is uncertain, and a note. Never type a model number into prose: the page's text uses build-time tokens and `tests/test_golden.py` checks the numbers quoted in RESULTS.md and METHODS.md.
3. **Golden values move only on purpose.** If a change moves a headline output, update `GOLDEN` in `tests/test_golden.py` in the same commit, and say in CHANGELOG.md what moved and why.
4. **This file is generated.** After any change, run `python agents_edition.py`; `tests/test_agents_edition.py` fails if AGENTS.md, llms.txt or inputs.json differ from a fresh run. The scan of what the answer rests on is stored in `agents_edition_scan.json`; when an input or the engine changes, the test asks for `python agents_edition.py --scan`, which runs it again split over the machine's cores.
5. **Wording rules** (enforced on the page by `tests/test_easy_view.py`, and on this file by `tests/test_agents_edition.py`):
   - retired names, never used: 'Selected cells', 'Engineered cells', "Today's cells", 'Today’s cells', 'Central case', 'Best case', 'best case', 'central case';
   - no judgement or odds attributed to the owner or the author (the pattern `OWNER_JUDGED` in the test): a judgement is the model's, labelled as such, with its range;
   - a converted cost names the year of its dollars ("2025 dollars"), never the present (the pattern `TODAY_COST`);
   - no em dash in visible text;
   - cells are described by their traits (ammonia, lactate, doubling time, mass), never by how cells would come to have them: no route words (the pattern `ROUTE_WORDS`); never imply that a trait needs one method;
   - no forecast in the summary; literal section titles, not figurative ones; explanatory names are kept long.
6. **Calibrated claims.** A value nobody has measured is called a judgement or an assumption, with its range, and the answer's dependence on it is shown (answer_rests_on.py). Evidence is searched in both directions.

### Add a published cost study as a starting set (with its audit)

1. Put the study's PDF in `Cultivated_meat_TEAs/` (outside this repository) and add an entry to `study_assumptions.STUDIES`: name, year, citation, the system it models in one plain sentence, its own reported cost and basis, and each assumption as (what, value as the source gives it, reference with the PDF page). Record only values read in the source; a value worked out from them says "derived" and shows the arithmetic.
2. Add what it assumes on each lever of the all-favourable example to `STUDY_LEVERS`. A value that breaks a limit of the model (`LIMITS`) goes into `REJECTED` with the limit and its source, and is never a source for `scenarios.all_favourable()`.
3. Add its most favourable estimate to `ESTIMATES` (basis, year of its dollars) so `estimates()` brings it to a kilo of wet cells in 2025 dollars.
4. Express its design in the page's levers as modifications over Humbird's best estimate (`_mods()`: traits, held, plant, vm, device); an assumption the levers cannot say carries `not_representable` and the reason.
5. Add a `SETS` entry with `audit`: one row per assumption, (assumption, the setting it moves or None, what the study says and where, one of the reasons in `AUDIT_WHY`, what the set uses when it is not the study's value). The reasons: the study's value; the study's more favourable scenario or sensitivity, not its base case; the study's value is what one lab run or today's ingredients gave; the set uses the long-term target; the study's value is beyond a limit of this model; the set uses the nearest possible value; the study does not give it; Humbird's best estimate is kept; the study does not give it, and Humbird's design has no equivalent the set can keep; this model's default is used; the page has no lever for it; the set leaves it out; this model works it out from the cells and the tank, whatever the study states.
6. If it publishes a plant and running split, add it to `SPLITS`.
7. Regenerate section 13 of `research_notes/study_comparison.md` from `study_assumptions.markdown()`, rebuild the page, run `./run_tests.sh` (`tests/test_study_assumptions.py` checks that every lever a set moves has an audit row and that the page gives the same cost), then `python agents_edition.py`.

### Where things are

- `RESULTS.md`: the findings, with Monte Carlo bands. `METHODS.md`: the methods and sources at code level. `CHANGELOG.md`: what changed, dated. `TODO.md`: open work and decisions waiting.
- `research_notes/`: one note per question, with the evidence read and the reasoning; the module docstrings name their notes.
- The page: https://pabloamc.github.io/Cultivated_meat/interactive.html. The repository: https://github.com/PabloAMC/Cultivated_meat.
