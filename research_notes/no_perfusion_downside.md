# If perfusion cannot be run at 20 m³

> Names (2026-11-19): the low-lactate example was earlier called Central; the all-favourable example was earlier called the best case. Cells are described by their traits, never as a named kind of cell.

> Repinned 2026-11-19 (scenario restructure): the density of a tank that is not washed out is set by the waste mass balance (`pf_batch_end_x`); a fed-batch plant with shared medium keeps Humbird's full seed train; the probabilities are re-judged at Central's 191 g/L. Sections 1-3 rewritten.

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50.

> Repinned 2026-11-19 (audit batch): ammonia tolerance 4 mM, lost runs pay for their membranes, glucose from the cells' balance (published cells need about 95 L/kg); see audit_2026-11-19.md.

> Recomputed 2026-11-16 on the current model (bubble protectant, antifoam's cost to oxygen transfer, bought oxygen in a yeast-style plant, dissolved oxygen held at half of air saturation, medium at least the culture that leaves with the cells).

Date: 2026-11-15. Code: `downside.py`; tests: `tests/test_downside.py`. Costs are 2025 dollars per kg of wet cells. Shares are the
long-run share of world meat by weight at the scenario's point cost (`scenarios.shares`), not the median of the bands.

## 1. The question

Central and the scenarios above it on the ladder use a 20 m³ stirred tank in perfusion. A device holds the cells back and fresh
medium washes the waste out. Nobody has run animal cells in perfusion above about 4 m³ (Genzyme's tanks at Geel). This note prices
the fallback: the same tank with no cell retention, run in fed-batch or in fill-and-draw. Since the scenario restructure of
2026-11-19 fed-batch at 20 m³ is also a setting of the scenarios' switch "How the tank is run", and the first three rungs of the
ladder use it; this note keeps the four scenarios the side studies share.

Without retention, waste is not washed out. **Since 2026-11-19 the cap is a mass balance** (`vessels_and_modes.md`, section 10):
the litres a kilo leaves with (1000 / density) must hold its ammonia and its lactate at the level perfusion is held to, times 1.3
for a batch that ends above it (`pf_batch_end_x`, Humbird's own fed-batch design). Before, Humbird's fed-batch 120 g/L was scaled by
the cells' waste, which let Central's batch end at 7.8 mmol/L of ammonia against the 4 its perfusion is held to. The least medium
flow a cell needs can cap it lower ("other by-products"). Each scenario is priced at two densities: the model's own cap, and the
density reported for meat cells at 20 m³ (Vow: 538 kg from 20,000 L, about 27 g/L, `vm_x_meat_shown`). Upside Foods' reported
capacity implies 33-136 g/L in a batch (`vessels_and_modes.md`, section 11).

Everything else is the scenario's: the cells, the plant, the losses, the gas the cells tolerate, the medium and the growth factors.
The tank design (tricks and shape) is chosen again for each mode. A fed-batch plant with shared medium keeps Humbird's full seed train,
because it restarts each tank every three or four days; fill-and-draw runs for 33 days and keeps the plant's two small seed trains.

## 2. Results

| Scenario | Perfusion (the model) | Fed-batch, model cap | Fill-and-draw, model cap | Fed-batch, 27 g/L | Fill-and-draw, 27 g/L |
|---|---|---|---|---|---|
| All-favourable example | **$11.67** (3.2%) | $15.71 (92 g/L, 1.7%) | $14.44 (92 g/L, 2.1%) | $44.07 (0.07%) | $39.60 (0.11%) |
| Low-lactate example | **$32.80** (0.21%) | $64.90 (37 g/L, 0.02%) | $70.62 (37 g/L, 0.01%) | $88.21 (under 0.01%) | $95.50 (under 0.01%) |
| Low-lactate example, food-grade plant with shared medium | **$29.94** (0.29%) | $49.51 (37 g/L, 0.05%) | $47.94 (37 g/L, 0.05%) | $67.04 (0.02%) | $64.55 (0.02%) |
| Cautious (published cells) | **$92.17** (under 0.01%) | $209.05 (14 g/L) | $242.02 (14 g/L) | $209.05 (14 g/L: the cap is under 27) | $242.02 (14 g/L) |

Shares in brackets are the long-run share of world meat and seafood at the point cost (the share of the meat sold, since 2026-11-19).

- **Without perfusion every scenario costs much more than the old figures said.** At the model's own cap Central goes from $32.80 to
  $64.90 in fed-batch (it was $44.13), and the cautious case from $92.17 to $209.05 (it was $113.56). The all-favourable example barely moves
  ($15.71 in fed-batch, $14.44 in fill-and-draw): its cells are held by other by-products at 92 g/L, not by their waste.
- **The mass balance is the reason.** Held to 1.3 times the 4 mmol/L its perfusion is held to, Central's batch ends at 37 g/L, not
  56. Its plant charge per kilo rises in proportion. The published cells make 4.8 mol of lactate a kilo; held to 1.3 times 50
  mmol/L, they stop at 14 g/L. The old cap let them reach 25 g/L at about 120 mmol/L of lactate.
- **Perfusion is worth about $32 a kilo in Central, not $11.** That is the largest single step of the new ladder's middle: rung 3
  (cells that make less lactate (0.42) in a batch, $64.9) to rung 4 (Central, $32.8). Fed-batch's handicap is capital: the same plant makes a fifth of
  the kilos. A cheaper plant narrows it (section 1 of RESULTS, the plant-cost axis): fed-batch at 20 m³ is cheaper than perfusion only
  if the whole plant costs under about a fifth of its modelled cost (0.19×) with Central's switches, 0.28× with the shared-medium
  plant.
- **The density companies report at 20 m³ is close to the model's cap for cells that make less lactate (0.42).** At 27 g/L Central costs $88 in fed-batch
  and $95 in fill-and-draw. Cells that make less lactate (0.42) reach 37 g/L. The published cells cannot reach 27 g/L at all in a batch: they would need
  a lactate yield of about 0.7 mol per mol of glucose, not 1.05.
- **Fill-and-draw beats fed-batch in a plant with shared medium.** It needs a seed only to restart after a loss, so the plant's
  two small seed trains suffice; fed-batch needs Humbird's full seed train for a new seed every three or four days. In Humbird's own
  plant fed-batch is cheaper, because fill-and-draw averages only 72% of its cap over a cycle. The two are within 10% of each other.
- **The tank design changes.** Every fallback drops the column and the pressure and runs the ordinary tall tank: a batch held by its
  waste gains nothing from more gas exchange.

## 3. How likely is the fallback?

Judgement, from the retention note, re-judged on 2026-11-19 at the scenarios' current densities. Not dated unless the row says so.

| Statement | Probability |
|---|---|
| A filter holds the low-lactate example's 191 g/L at 20 m³ for a month, at any cost (so perfusion does not fail) | about 45% (re-judged; it was 35% at 258 g/L) |
| The same for the all-favourable example, at 258 g/L | about 35% |
| The same for the reference case, at 120 g/L and a light duty | about 75% |
| The same for the cautious case, at 120 g/L but 87 litres of permeate a kilo | about 60% |
| Filter perfusion at the low-lactate example's density in production by 2035 (45% possible x 45% in use by 2035; a judgement, not used by the model) | about 20% |
| Aggregates on a settler hold the low-lactate example's density by 2035 (`retention_aggregates.md`) | about 8% |
| If perfusion is not used, a 20 m³ batch reaches the model's mass-balance cap with the scenario's cells | about 70% |

- **191 g/L.** The odds fall with the density at which the filter must work: 75% at 120 g/L, 35% at 258 g/L (`retention_devices.md`).
  `tank_size.md` scales them by a density factor that gives 0.59 of the 120 g/L odds at 191 g/L, that is 44%. For: one fibre lasted
  30 days at about half the volume in cells (Clincke 2013, 4 L), and perfusion is routine at 2 m³ in pharma. Against: nothing above
  about 4 m³ in thirty years of pharma, and Central's permeate is ten times the reference's. About 45%.
- **The cautious case** (published cells, 120 g/L) is easier on density than Central but filters 87 litres a kilo, three times
  Central's; it was given 50% at 145 g/L. About 60%.
- **The cap.** It is now a mass balance at 1.3 times the perfusion level, not an extrapolation of Humbird's enhanced cells, so it is
  likelier to be reached. Upside's capacity implies 33-136 g/L in a batch, Vow reports 27 g/L, and pharma batches end above the levels
  they perfuse at. The risk is the cells: the published cells do not reach 27 g/L. About 70% for cells as good as the scenario says.

So, if perfusion fails, Central's likelier cost is near $65 (the mass-balance cap), and $88 if its cells only reach the density Vow
reports.

## 4. What would reduce this risk

- **A device that holds the cells back at 20 m³.** Nothing else closes the gap. The cheaper-membrane routes in
  `retention_alternatives.md` would only lower its cost.
- **A food-grade plant with shared medium.** It cushions the fall more than any other change, because the penalty is mostly
  capital.
- **Cells that make less waste.** A drained tank's density is set by waste, so better cells raise it. For the published cells the
  waste that matters is lactate: a lower lactate yield raises their cap above 14 g/L and cuts their perfusion medium too.
- **A larger fed-batch tank.** It helps fed-batch (about 10% at 100 m³, `tank_size.md` section 10) and barely helps perfusion.
- **A run of fed-batch or fill-and-draw at 20 m³ that reports its density and waste levels, with meat cells.** Vow's 27 g/L
  comes from press reports about one harvest; Upside's 33-136 g/L is arithmetic on a capacity claim. Upside's promised FDA memo
  may give the first measured figure.

## 5. What was not done

- Chemostat as a fallback. It costs more than fill-and-draw in the vessel grid: it sits at its density all the time, so it is held to
  the perfusion level itself (end factor 1).
- A 5–10 m³ perfusion tank, the next size down from 20 m³, where perfusion has precedent. Plants of many smaller tanks cost more
  per m³. A later piece of work could price it.
- A mixture of the outcomes into one expected cost or a forecast: a forecast built from these odds on 2026-11-19 was dropped at the
  author's direction; the odds are kept in `cell_trait_routes.md` (appendix) as a record, not used by the model.
