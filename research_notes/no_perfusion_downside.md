# If perfusion cannot be run at 20 m³

Date: 2026-11-15. Code: `downside.py`; tests: `tests/test_downside.py`. Costs are 2025 dollars per kg of wet cells. Shares are the
long-run share of world meat by weight at the scenario's point cost (`scenarios.shares`), not the median of the bands.

## 1. The question

Every scenario uses a 20 m³ stirred tank in perfusion. A device holds the cells back and fresh medium washes the waste out.
Nobody has run animal cells in perfusion above about 4 m³ (Genzyme's tanks at Geel). The retention study (`retention_devices.md`)
puts 35% on any filter holding the central case's 258 g/L at 20 m³ for a month, and 75% on holding the reference case's 120 g/L.
This note prices the fallback: the same tank with no cell retention, run in fed-batch or in fill-and-draw.

Without retention, waste is not washed out. Ammonia, lactate and the least medium flow a cell needs cap the density. The one
20 m³ plant for meat cells reports harvests of about 27 g/L (Vow: 538 kg from 20,000 L). So each scenario is priced at two
densities: the model's own cap, and the density shown for meat cells (`vm_x_meat_shown`).

Everything else is the scenario's: the cells, the plant, the losses, the gas the cells tolerate, the medium and the growth factors.
The tank design (tricks and shape) is chosen again for each mode. A column, pressure and recycled oxygen lift the perfusion tank's
gas limits, but they add capital without raising the density of a tank that waste caps.

## 2. Results

| Scenario | Perfusion (the model) | Fed-batch, model cap | Fill-and-draw, model cap | Fed-batch, 27 g/L | Fill-and-draw, 27 g/L |
|---|---|---|---|---|---|
| Best case | **$8.95** (9.3%) | $13.22 (92 g/L, 3.7%) | $13.32 (92 g/L, 3.7%) | $40.55 (0.2%) | $40.89 (0.2%) |
| Central | **$26.64** (0.5%) | $40.39 (62 g/L, 0.2%) | $43.58 (62 g/L, 0.1%) | $89.94 (0.0%) | $97.22 (0.0%) |
| Central, food-grade plant with shared medium | **$24.34** (0.7%) | $28.22 (62 g/L, 0.5%) | $30.20 (62 g/L, 0.4%) | $61.74 (0.0%) | $66.28 (0.0%) |
| Cautious | **$38.97** (0.2%) | $59.93 (52 g/L, 0.0%) | $68.35 (52 g/L, 0.0%) | $111.48 (0.0%) | $127.34 (0.0%) |

- **Without perfusion every scenario costs more.** At the model's own cap, the best case goes from $8.95 to $13.22, Central from $26.64
  to $40.39, and the cautious case from $38.97 to $59.93.
- **The density that has been shown matters more than the mode.** At 27 g/L Central costs $90–97 a kilo and the best case $41. At
  that density the plant's capital is spread over a third as many kilos as at 92 g/L.
- **A plant that costs less cushions the fall.** In the food-grade plant with shared medium, fed-batch at the model's cap costs
  $28.22, only $3.88 above its perfusion cost. Capital is a small share of that scenario's cost, so losing the high density
  matters less. This is also the only scenario that stays above 0.4% of world meat without perfusion.
- **Fed-batch is cheaper than fill-and-draw in every scenario.** Fill-and-draw never reaches its cap in a cycle: it averages 72%
  of it. Fed-batch's cycle is Humbird's: two doublings and 10 hours to clean and refill.
- **The tank design changes.** Every fallback drops the column and the pressure (the cautious case keeps its column). This lowers
  Central's fed-batch cost from $45.29, the figure in the vessel grid (`vessels.py`), to $40.39. The grid holds the perfusion design
  fixed on purpose, so the two numbers answer different questions.

## 3. How likely is the fallback?

These are judgement, built from the retention note. They are not a forecast.

| Statement | Probability |
|---|---|
| Perfusion fails at 20 m³ (no device holds the culture for a month, at any cost): best case, Central | about 65% (35% that a filter holds 258 g/L) |
| The same for the reference case, at 120 g/L | about 25% |
| The same for the cautious case, at 145 g/L | about 50% |
| If it fails, an unwashed 20 m³ tank reaches the model's cap (52–92 g/L) with meat cells | about 25% |

The last row is from the operating-modes research note (25% for fill-and-draw and chemostat holding a high density without
waste-reduced cells; 15% for a chemostat alone). So if perfusion fails, the likelier price for Central is nearer $90 than $40. The
fallback is also not the only way perfusion could fail: a device could hold the cells back at a lower density than the scenario
assumes. The retention note and `retention.density_scan` cover that case: a thinner culture costs more.

## 4. What would reduce this risk

- **A device that holds the cells back at 20 m³.** Nothing else closes the gap. The cheaper-membrane routes in
  `retention_alternatives.md` would only lower its cost.
- **A food-grade plant with shared medium.** It cushions the fall more than any other change, because the penalty is mostly
  capital.
- **Cells that make less waste.** A drained tank's density is set by waste, so better cells raise it.
- **A run of fed-batch or fill-and-draw at 20 m³ that reports its density, with meat cells.** Today's only figure is Vow's
  27 g/L, which comes from press reports about one harvest.

## 5. What was not done

- Chemostat as a fallback. It costs more than fill-and-draw in the vessel grid.
- A 5–10 m³ perfusion tank, the next size down from 20 m³, where perfusion has precedent. Plants of many smaller tanks cost more
  per m³. A later piece of work could price it.
- A mixture of the outcomes into one expected cost: the weights above are too uncertain to support one number.
