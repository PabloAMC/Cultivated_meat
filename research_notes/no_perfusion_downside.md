# If perfusion cannot be run at 20 m³

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50.

> Repinned 2026-11-19 (audit batch): ammonia tolerance 4 mM, lost runs pay for their membranes, glucose from the cells' balance (published cells need about 95 L/kg); see audit_2026-11-19.md.

> Recomputed 2026-11-16 on the current model (bubble protectant, antifoam's cost to oxygen transfer, bought oxygen in a yeast-style plant, dissolved oxygen held at half of air saturation, medium at least the culture that leaves with the cells).

Date: 2026-11-15. Code: `downside.py`; tests: `tests/test_downside.py`. Costs are 2025 dollars per kg of wet cells. Shares are the
long-run share of world meat by weight at the scenario's point cost (`scenarios.shares`), not the median of the bands.

## 1. The question

Every scenario uses a 20 m³ stirred tank in perfusion. A device holds the cells back and fresh medium washes the waste out.
Nobody has run animal cells in perfusion above about 4 m³ (Genzyme's tanks at Geel). The retention study (`retention_devices.md`)
puts 35% on any filter holding 258 g/L at 20 m³ for a month, and 75% on holding the reference case's 120 g/L. (258 g/L was the
central case's density when that judgement was made; oxygen supply now limits the central tank to 191 g/L.)
This note prices the fallback: the same tank with no cell retention, run in fed-batch or in fill-and-draw.

Without retention, waste is not washed out. Ammonia, lactate and the least medium flow a cell needs cap the density. Since the
2026-11-19 audit the cap follows whichever waste is further above the engineered cells' level: ammonia for the selected cells,
lactate for the published cells. The one
20 m³ plant for meat cells reports harvests of about 27 g/L (Vow: 538 kg from 20,000 L). So each scenario is priced at two
densities: the model's own cap, and the density shown for meat cells (`vm_x_meat_shown`).

Everything else is the scenario's: the cells, the plant, the losses, the gas the cells tolerate, the medium and the growth factors.
The tank design (tricks and shape) is chosen again for each mode. A column, pressure and recycled oxygen lift the perfusion tank's
gas limits, but they add capital without raising the density of a tank that waste caps.

## 2. Results

| Scenario | Perfusion (the model) | Fed-batch, model cap | Fill-and-draw, model cap | Fed-batch, 27 g/L | Fill-and-draw, 27 g/L |
|---|---|---|---|---|---|
| Best case | **$11.46** (2.8%) | $14.18 (92 g/L, 1.8%) | $14.28 (92 g/L, 1.8%) | $39.17 (0.0%) | $39.53 (0.0%) |
| Central | **$32.80** (0.1%) | $44.13 (56 g/L, 0.0%) | $47.67 (56 g/L, 0.0%) | $88.21 (0.0%) | $95.50 (0.0%) |
| Central, food-grade plant with shared medium | **$29.94** (0.1%) | $30.59 (56 g/L, 0.1%) | $32.80 (56 g/L, 0.1%) | $60.01 (0.0%) | $64.55 (0.0%) |
| Cautious (published cells) | **$92.17** (0.0%) | $113.56 (25 g/L, 0.0%) | $130.61 (25 g/L, 0.0%) | $113.56 (25 g/L: the cap is under 27) | $130.61 (25 g/L) |

- **Without perfusion every scenario costs more.** At the model's own cap, the best case goes from $11.46 to $14.18, Central from
  $32.80 to $44.13, and the cautious case from $92.17 to $113.56.
- **The gap is smaller than it was for Central.** Before the 2026-11-19 audit Central lost $13.73 a kilo without perfusion ($26.43
  to $40.16). It now loses $11.33. Perfusion became dearer by $6.37: 35 litres of medium a kilo instead of 28, and membranes for
  lost runs. The fallback became dearer by $3.97: at 4 mmol/L of ammonia the unwashed tank stops at 56 g/L, not 62.
- **The cautious case's cap is now below the density Vow reports.** The cautious case uses the published cells. With glucose taken
  from the cells' own balance they make 4.8 mol of lactate a kilo, 8.5 times the engineered cells' 0.56. Washing that out sets the
  perfusion medium at 95 litres a kilo ($92.17, up from $36.42). Without washing it out, lactate stops the tank at 25 g/L (it was
  52 g/L, when only ammonia and the least medium flow counted). So the fallback costs $113.56 in fed-batch and $130.61 in
  fill-and-draw (they were $57.33 and $65.75), and the two 27 g/L columns are the same tank: these cells do not reach 27 g/L
  unwashed. The cap is a scaling from the engineered cells' unwashed tank, not the 50 mmol/L limit perfusion holds: at 25 g/L
  the culture would hold about 120 mmol/L of lactate. Held to 50 mmol/L it would stop near 10 g/L and cost more than twice as much.
- **The density that has been shown matters more than the mode.** At 27 g/L Central costs $88–96 a kilo and the best case $39–40. At
  that density the plant's capital is spread over a third as many kilos as at 92 g/L.
- **A plant that costs less cushions the fall, if the tank reaches its cap.** In the food-grade plant with shared medium, fed-batch
  at the model's cap costs $30.59, only $0.65 (2%) above its perfusion cost (it was $4.42, 19%, before the audit). Capital is a
  small share of that scenario's cost, so losing the high density matters less, and fed-batch buys 18 litres of medium a kilo
  against perfusion's 35. Apart from the best case, it is the only scenario that keeps about 0.1% of world meat without perfusion
  (0.12% at the model's cap, against 0.13% with perfusion). At its cap the culture would hold about 60 mmol/L of lactate and
  8 mmol/L of ammonia, above what perfusion holds (50 and 4): the unwashed cap is a looser test than the perfusion limits.
- **Fed-batch is cheaper than fill-and-draw in every scenario.** Fill-and-draw never reaches its cap in a cycle: it averages 72%
  of it. Fed-batch's cycle is Humbird's: two doublings and 10 hours to clean and refill.
- **The tank design changes.** Every fallback drops the column and the pressure. This lowers
  Central's fed-batch cost from $45.81, the figure in the vessel grid (`vessels.py`), to $44.13. The grid holds the perfusion design
  fixed on purpose, so the two numbers answer different questions.

## 3. How likely is the fallback?

These are judgement, built from the retention note. They are not a forecast.

| Statement | Probability |
|---|---|
| Perfusion fails at 20 m³ (no device holds the culture for a month, at any cost): best case, Central | about 65% (35% that a filter holds 258 g/L) |
| The same for the reference case, at 120 g/L | about 25% |
| The same for the cautious case, at 120 g/L | about 50% |
| If it fails, an unwashed 20 m³ tank reaches the model's cap (25–92 g/L) with meat cells | about 25% |

The first and third rows were judged when the central case ran at 258 g/L and the cautious case at 145 g/L. Oxygen supply now
limits them to 191 and 120 g/L; the probabilities have not been judged again. The last row was judged for caps of 52–92 g/L;
the cautious case's cap is now 25 g/L, about the density Vow reports, and has not been judged again.

The last row is from the operating-modes research note (25% for fill-and-draw and chemostat holding a high density without
waste-reduced cells; 15% for a chemostat alone). So if perfusion fails, the likelier price for Central is nearer $88 than $44. The
fallback is also not the only way perfusion could fail: a device could hold the cells back at a lower density than the scenario
assumes. The retention note and `retention.density_scan` cover that case: a thinner culture costs more.

## 4. What would reduce this risk

- **A device that holds the cells back at 20 m³.** Nothing else closes the gap. The cheaper-membrane routes in
  `retention_alternatives.md` would only lower its cost.
- **A food-grade plant with shared medium.** It cushions the fall more than any other change, because the penalty is mostly
  capital.
- **Cells that make less waste.** A drained tank's density is set by waste, so better cells raise it. For the published cells the
  waste that matters is lactate: a lower lactate yield raises their cap above 25 g/L and cuts their perfusion medium too.
- **A run of fed-batch or fill-and-draw at 20 m³ that reports its density, with meat cells.** Today's only figure is Vow's
  27 g/L, which comes from press reports about one harvest.

## 5. What was not done

- Chemostat as a fallback. It costs more than fill-and-draw in the vessel grid.
- A 5–10 m³ perfusion tank, the next size down from 20 m³, where perfusion has precedent. Plants of many smaller tanks cost more
  per m³. A later piece of work could price it.
- A mixture of the outcomes into one expected cost: the weights above are too uncertain to support one number.
