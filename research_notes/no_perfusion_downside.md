# If perfusion cannot be run at 20 m³

> Recomputed 2026-11-16 on the current model (bubble protectant, antifoam's cost to oxygen transfer, bought oxygen in a yeast-style plant, dissolved oxygen held at half of air saturation, medium at least the culture that leaves with the cells).

Date: 2026-11-15. Code: `downside.py`; tests: `tests/test_downside.py`. Costs are 2025 dollars per kg of wet cells. Shares are the
long-run share of world meat by weight at the scenario's point cost (`scenarios.shares`), not the median of the bands.

## 1. The question

Every scenario uses a 20 m³ stirred tank in perfusion. A device holds the cells back and fresh medium washes the waste out.
Nobody has run animal cells in perfusion above about 4 m³ (Genzyme's tanks at Geel). The retention study (`retention_devices.md`)
puts 35% on any filter holding 258 g/L at 20 m³ for a month, and 75% on holding the reference case's 120 g/L. (258 g/L was the
central case's density when that judgement was made; oxygen supply now limits the central tank to 191 g/L.)
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
| Best case | **$9.66** (8.0%) | $13.87 (92 g/L, 3.3%) | $13.97 (92 g/L, 3.2%) | $42.77 (0.1%) | $43.11 (0.1%) |
| Central | **$29.42** (0.4%) | $41.36 (62 g/L, 0.2%) | $44.55 (62 g/L, 0.1%) | $92.16 (0.0%) | $99.45 (0.0%) |
| Central, food-grade plant with shared medium | **$26.56** (0.5%) | $29.19 (62 g/L, 0.4%) | $31.18 (62 g/L, 0.4%) | $63.96 (0.0%) | $68.50 (0.0%) |
| Cautious | **$42.39** (0.1%) | $61.09 (52 g/L, 0.0%) | $69.51 (52 g/L, 0.0%) | $113.70 (0.0%) | $129.56 (0.0%) |

- **Without perfusion every scenario costs more.** At the model's own cap, the best case goes from $9.66 to $13.87, Central from $29.42
  to $41.36, and the cautious case from $42.39 to $61.09.
- **The density that has been shown matters more than the mode.** At 27 g/L Central costs $92–99 a kilo and the best case $43. At
  that density the plant's capital is spread over a third as many kilos as at 92 g/L.
- **A plant that costs less cushions the fall.** In the food-grade plant with shared medium, fed-batch at the model's cap costs
  $29.19, only $2.63 above its perfusion cost. Capital is a small share of that scenario's cost, so losing the high density
  matters less. Apart from the best case, it is the only scenario that keeps about 0.4% of world meat without perfusion.
- **Fed-batch is cheaper than fill-and-draw in every scenario.** Fill-and-draw never reaches its cap in a cycle: it averages 72%
  of it. Fed-batch's cycle is Humbird's: two doublings and 10 hours to clean and refill.
- **The tank design changes.** Every fallback drops the column and the pressure (the cautious case keeps its column). This lowers
  Central's fed-batch cost from $42.87, the figure in the vessel grid (`vessels.py`), to $41.36. The grid holds the perfusion design
  fixed on purpose, so the two numbers answer different questions.

## 3. How likely is the fallback?

These are judgement, built from the retention note. They are not a forecast.

| Statement | Probability |
|---|---|
| Perfusion fails at 20 m³ (no device holds the culture for a month, at any cost): best case, Central | about 65% (35% that a filter holds 258 g/L) |
| The same for the reference case, at 120 g/L | about 25% |
| The same for the cautious case, at 120 g/L | about 50% |
| If it fails, an unwashed 20 m³ tank reaches the model's cap (52–92 g/L) with meat cells | about 25% |

The first and third rows were judged when the central case ran at 258 g/L and the cautious case at 145 g/L. Oxygen supply now
limits them to 191 and 120 g/L; the probabilities have not been judged again.

The last row is from the operating-modes research note (25% for fill-and-draw and chemostat holding a high density without
waste-reduced cells; 15% for a chemostat alone). So if perfusion fails, the likelier price for Central is nearer $92 than $41. The
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
