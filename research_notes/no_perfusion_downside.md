# If perfusion cannot be run at 20 m³

> Names (2026-11-19): the low-lactate example was earlier called Central; the all-favourable example was earlier called the best case. Cells are described by their traits, never as a named kind of cell.

> Repinned 2026-11-20 (final pass). The all-favourable example is now the one case of `scenarios.all_favourable()` ($7.62): Humbird's 5 mmol/L of ammonia and 50 mmol/L of lactate, 0.054 mol of ammonia a kilo, dialyser-grade hollow fibres, 42 m³ tanks in perfusion. Bubble deaths are now charged only on the gas the cells meet, and a column that strips nothing no longer lowers them. **Changed conclusions:** no fallback now costs less than perfusion (the all-favourable example in fill-and-draw costs $9.35 against $7.62 in perfusion; in the first batch of 2026-11-20 it cost $17.06 against $18.71); the all-favourable example's unwashed tank is held at 120 g/L by its ammonia, not 77 g/L by its lactate; the "column of no size" that every fallback took is gone, so the suspected defect reported in the first batch is fixed; perfusion is worth about $22 a kilo in the low-lactate example.

> Repinned 2026-11-20 (first batch: lactate tolerance 35 mmol/L in the scenarios, cells killed by bursting bubbles, a 2% harvest loss, twice the fed-batch crew in perfusion, membrane life 2,415 L/m2, medium preparation capital, utilities in four parts).

> Repinned 2026-11-19 (scenario restructure): the density of a tank that is not washed out is set by the waste mass balance (`pf_batch_end_x`); a fed-batch plant with shared medium keeps Humbird's full seed train. Earlier repins on 2026-11-19 (nutrient floor $2.00, audit batch) and 2026-11-16 are recorded in the changelog.

Date: 2026-11-20; section 2 regenerated 2026-11-21. Code: `downside.py`; tests: `tests/test_downside.py`. Costs are 2025 dollars per kg of wet cells. Shares are the
long-run share of world meat by weight at the scenario's point cost (`scenarios.shares`), not the median of the bands.

## 1. The question

The low-lactate example and the scenarios above it on the ladder use a stirred tank in perfusion (20 m³; 42 m³ in the
all-favourable example). A device holds the cells back and fresh medium washes the waste out. Nobody has run animal cells in
perfusion above about 4 m³ (Genzyme's tanks at Geel). This note prices the fallback: a 20 m³ tank with no cell retention, run in
fed-batch or in fill-and-draw. Since the scenario restructure of 2026-11-19 fed-batch at 20 m³ is also a setting of the scenarios'
switch "How the tank is run", and the first three rungs of the ladder use it; this note keeps the four scenarios the side studies share.

Without retention, waste is not washed out. **Since 2026-11-19 the cap is a mass balance** (`vessels_and_modes.md`, section 10):
the litres a kilo leaves with (1000 / density) must hold its ammonia and its lactate at the level perfusion is held to, times 1.3
for a batch that ends above it (`pf_batch_end_x`, Humbird's own fed-batch design). The least medium flow a cell needs, or the oxygen
the tank can supply, can cap it lower. Each scenario is priced at two densities: the model's own cap, and the density reported for
meat cells at 20 m³ (Vow: 538 kg from 20,000 L, about 27 g/L, `vm_x_meat_shown`). Upside Foods' reported capacity implies
33-136 g/L in a batch (`vessels_and_modes.md`, section 11).

Everything else is the scenario's: the cells, the plant, the losses, the gas the cells tolerate, the medium and the growth factors.
The tank design (tricks and shape) is chosen again for each mode. A fed-batch plant with shared medium keeps Humbird's full seed train,
because it restarts each tank every three or four days; fill-and-draw runs for 33 days and keeps the plant's two small seed trains.

## 2. Results

`python downside.py` prints this table (regenerated 2026-11-21, after the second batch of engine fixes and the thinner designs
in the design search).

| Scenario | Perfusion (the model) | Fed-batch, model cap | Fill-and-draw, model cap | Fed-batch, 27 g/L | Fill-and-draw, 27 g/L |
|---|---|---|---|---|---|
| All-favourable example | **$6.97** (6.1%) | $11.03 (120 g/L, 3.1%) | $9.13 (120 g/L, 4.2%) | $36.56 (0.1%) | $28.35 (0.3%) |
| Low-lactate example | **$48.68** (0.05%) | $70.32 (37 g/L, 0.01%) | $74.75 (37 g/L, 0.01%) | $94.67 (0.004%) | $100.10 (0.003%) |
| Low-lactate example, food-grade plant with shared medium | **$44.53** (0.07%) | $53.88 (37 g/L, 0.03%) | $50.60 (37 g/L, 0.04%) | $72.27 (0.01%) | $67.45 (0.01%) |
| Cautious (published cells) | **$181.13** (under 0.001%) | $316.11 (10 g/L) | $358.73 (10 g/L) | $316.11 (10 g/L: the cap is under 27) | $358.73 (10 g/L) |

Shares in brackets are the long-run share of world meat and seafood at the point cost, with the ordinary demand (14.4% of meat
buyers at equal price). All costs are per kilo of cells harvested.

- **Every fallback costs more than perfusion.** The all-favourable example holds its cells back with dialyser-grade fibres ($0.06
  a kilo of membranes) and runs 42 m³ tanks. Its perfusion makes 53.9 tonnes per m³ a year against 20.5 in fill-and-draw at
  20 m³, and pays $1.87 a kilo of capital against $4.12. Fill-and-draw costs $2.16 a kilo more (31%), fed-batch $4.06 more.
  These fallbacks run at 20 m³, the size this note asks about; perfusion runs at the case's own 42 m³.
- **Perfusion is worth about $22 a kilo in the low-lactate example.** That is rung 3 (the same cells in a batch, $70.3) to rung 4
  (the low-lactate example, $48.7). Perfusion carries twice the fed-batch crew, its membranes cost $22.7 a kilo, and its dense
  tank (168 g/L, held there so its oxygen-feeding column passes its checks) bubbles enough gas to kill 8.0% of its cells against
  3.4% in a 37 g/L batch. The batch makes 2.8 tonnes per m³ a year against perfusion's 16.3, so it pays $49.6 a kilo of capital
  against $10.8.
- **The mass balance sets the unwashed densities.** Held to 1.3 times the 4 mmol/L of ammonia its perfusion is held to, the
  low-lactate example's batch ends at 37 g/L. The all-favourable example's cells make 0.054 mol of ammonia a kilo and tolerate
  Humbird's 5 mmol/L; held to 1.3 times that, they stop at 120 g/L, Humbird's own fed-batch density; the pressure lifts its
  oxygen supply to that cap. The published cells make 4.8 mol of lactate a kilo; held to 1.3 times 35 mmol/L, they stop at
  10 g/L.
- **Fed-batch's handicap is capital, and a cheaper plant or a larger tank removes it.** Fed-batch at 20 m³ is cheaper than
  perfusion if the whole plant costs under 0.47 of its modelled cost with the low-lactate example's switches, and under 0.67 with
  the shared-medium plant. Fed-batch at 100 m³ crosses at 0.80 and 1.04: with the shared-medium plant a 100 m³ batch is already
  a little cheaper than perfusion ($43.6 against $44.5). With the all-favourable example's switches fed-batch is not cheaper
  anywhere between 0.05 and 1.5 times the modelled plant cost. `scenarios.plant_axis`; RESULTS, the plant-cost axis
  (`python -c "import scenarios as S; print(S.plant_axis_markdown())"`).
- **The density companies report at 20 m³ is below the model's cap for cells that make less lactate (0.42).** At 27 g/L the
  low-lactate example costs $95 in fed-batch and $100 in fill-and-draw; its own cap is 37 g/L. The published cells cannot reach
  27 g/L at all in a batch: they would need a lactate yield of about 0.56 mol per mol of glucose, not 1.05.
- **Fill-and-draw beats fed-batch in a plant with shared medium.** It needs a seed only to restart after a loss, so the plant's
  two small seed trains suffice; fed-batch needs Humbird's full seed train for a new seed every three or four days. In Humbird's own
  plant fed-batch is cheaper, because fill-and-draw averages only 72% of its cap over a cycle. The two are within 15% of each other,
  except in the all-favourable example, where fed-batch costs 21% more.
- **The tank design.** Every fallback runs the ordinary tall tank, except the all-favourable example's, which takes the pressure
  (above).

## 3. How likely is the fallback?

**A dated snapshot (set on 2026-11-20, not re-judged).** The probabilities below are a rough judgement made while building the
model with an AI assistant; not measured and not reviewed by an expert. They are not used by the model. They were set for the
densities the cases ran at on 2026-11-20 (in brackets); the cases now run denser, at 168, 219 and 134 g/L, so by the reasoning
below each would be lower. The derivation of the first from a density factor in `tank_size.md` no longer holds: that factor was
deleted from the note on 2026-11-21.

| Statement | Probability (the model's rough judgement, 2026-11-20) |
|---|---|
| A filter holds the low-lactate example's culture at 20 m³ for a month, at any cost (so perfusion does not fail) (then 154 g/L; now 168) | about 40-50% |
| The same for the all-favourable example, in 42 m³ tanks (then 155 g/L; now 219) | about 35-50% |
| The same for Humbird's optimistic design, at 120 g/L and a light duty (unchanged) | about 75% |
| The same for the cautious case, at a lower density but 146 litres of medium a kilo harvested (then 103 g/L; now 134) | about 50-60% |
| If perfusion is not used, a 20 m³ batch reaches the model's mass-balance cap with the scenario's cells | about 70% |

- **Density.** The odds fall with the density at which the filter must work: 75% at 120 g/L, 35% at 258 g/L (the model's rough
  judgement in `retention_devices.md`). For: one fibre lasted 30 days at about half the volume in cells (Clincke 2013, 4 L), and
  perfusion is routine at 2 m³ in pharma. Against: nothing above about 4 m³ in thirty years of pharma, and the low-lactate example
  filters 32 litres a kilo, eight times Humbird's optimistic design's 4. Hence the range.
- **The all-favourable example** works denser and in 42 m³ tanks, ten times the largest perfusion tank run; dialyser fibres are
  priced from kidney dialysis, not from a month on a culture (`retention_alternatives.md`). The lower end reflects that.
- **The cautious case** (published cells) works at a lower density but passes 146 litres of medium a kilo, nearly four times the
  low-lactate example.
- **The cap.** It is a mass balance at 1.3 times the perfusion level, not an extrapolation of Humbird's cells. Upside's capacity
  implies 33-136 g/L in a batch, Vow reports 27 g/L, and pharma batches end above the levels they perfuse at. What would have to be
  true for it to fail: the cells stop growing below their waste limits, as the published cells do below 27 g/L.

So, if perfusion fails, the low-lactate example's cost is near $70 at the mass-balance cap, and $95 if its cells only reach the
density Vow reports.

## 4. What would reduce this risk

- **A device that holds the cells back at 20 m³.** Nothing else closes the gap. The cheaper-membrane routes in
  `retention_alternatives.md` would only lower its cost.
- **A food-grade plant with shared medium.** It cushions the fall more than any other change, because the penalty is mostly
  capital.
- **Cells that make less waste.** A drained tank's density is set by waste, so better cells raise it. For the published cells the
  waste that matters is lactate: a lower lactate yield raises their cap above 9.5 g/L and cuts their perfusion medium too.
- **A larger fed-batch tank.** It helps fed-batch (about 22% at 100 m³: $54.58 against $70.32 in the low-lactate example,
  `scenarios.plant_axis`) and helps perfusion less (under 5%, `tank_size.md`).
- **A run of fed-batch or fill-and-draw at 20 m³ that reports its density and waste levels, with meat cells.** Vow's 27 g/L
  comes from press reports about one harvest; Upside's 33-136 g/L is arithmetic on a capacity claim. Upside's promised FDA memo
  may give the first measured figure.

## 5. What was not done

- Chemostat as a fallback. It costs more than fill-and-draw in the vessel grid: it sits at its density all the time, so it is held to
  the perfusion level itself (end factor 1).
- A 5–10 m³ perfusion tank, the next size down from 20 m³, where perfusion has precedent. Plants of many smaller tanks cost more
  per m³. A later piece of work could price it.
- The fallback at the all-favourable example's 42 m³: `downside.py` prices every fallback at 20 m³.
- A mixture of the outcomes into one expected cost or a forecast.
