# The frontier: what is possible if every lever goes to its limit

Date: 2026-11-15; recomputed 2026-11-16 with the protectant, antifoam and the plant ladder of PR #32. Code: `frontier.py`; tests: `tests/test_frontier.py`. Costs are 2025 dollars per kg of wet cells. The scenarios say what
the model assumes. This asks what is possible. It starts from the central scenario ($29.92) and moves one lever at a time to the
limit that the research notes support, keeping each one moved. It changes no default.

## 1. The ladder

| Step (each kept moved) | Cost | Change | Odds, from the note that studied it |
|---|---|---|---|
| Central scenario | **$29.92** | | |
| Medium at the least the physics allows: 6.4 L/kg, fed as a concentrate | $14.27 | −15.65 | physically possible, 60% (6 L/kg or less); a meat-cell process reporting 11 L/kg or less by 2030, 10% (`min_litres_per_kg.md`) |
| Cells double in 16 hours | $10.32 | −3.95 | physics allows about 8 h; a meat line in suspension at 50 g/L or more doubling in 16 h or less by 2035, 7% (`gf_and_doubling_bounds.md`) |
| Dialyser-grade hollow fibres as the filter | $10.32 | 0.00 | holds 25% cells for a month, 15% (`retention_alternatives.md`) |
| Medium at $0.05 a litre | $10.32 | 0.00 | an aspiration; the lowest company report is $0.07 (`medium_cost_gfi.md`) |
| Growth factors returned by the filter | $10.32 | 0.00 | a filter that halves growth-factor cost, 20% (`gf_and_doubling_bounds.md`) |
| Culture at 320 g/L in place of 258 | $10.32 | 0.00 | held for a month at 20 m³ with everything solved, 6% (`thick_culture.md`) |
| A food-grade plant with shared medium | $8.38 | −1.93 | nobody has built one (`cheap_plant_study.md`) |
| Runs lost 0.2% a day, as in pharma | $8.02 | −0.36 | makers report 0.6–2% a day |
| Gas at up to 6 mm/s | **$7.03** | −0.99 | about even odds that it works at this size (`gas_flow_cap.md`) |

With GFI's cheapest amino-acid prices in the nutrient floor (`nutrient_floor.md`), the frontier is **$7.83**. Price parity with $12
meat needs about $7 a kilo of cells.

## 2. Each lever on its own, from Central

| Lever | Cost alone | Change |
|---|---|---|
| Medium at 6.4 L/kg | $14.27 | −15.65 |
| Dialyser-grade hollow fibres | $21.92 | −8.01 |
| Cells double in 16 hours | $25.30 | −4.62 |
| Medium at $0.05 a litre | $25.96 | −3.96 |
| A food-grade plant with shared medium | $26.81 | −3.11 |
| Growth factors returned by the filter | $27.58 | −2.34 |
| Gas at up to 6 mm/s | $27.91 | −2.01 |
| Runs lost 0.2% a day | $28.89 | −1.03 |
| Culture at 320 g/L | $29.92 | 0.00 |

Before PR #32 (protectant, antifoam, plant ladder) these matched the studies they come from ($18.00, $22.68, $22.49 and $24.34); those
studies' notes are snapshots of that model.

## 3. What this says

1. **The litres of medium per kilo are the lever.** At 6.4 L/kg, Central costs $14.27 with nothing else changed. Fewer litres cut three
   costs at once: the medium, the growth factors, and the filtering (the filter clears the litres the bleed does not carry out). The
   central cells make more ammonia, which is why they need 28.
2. **Levers share what they save.** The dialyser-grade fibres save $8.01 alone and nothing after the medium is cut, because there is
   then almost no liquid to filter. The $0.05 medium saves $3.96 alone and nothing after, because at 6.4 L/kg the medium is already at
   the nutrient floor. Returning the growth factors saves $2.34 alone and nothing after, because at 6.4 L/kg the bleed already carries
   out most of the liquid. Read the ladder as one path. The single-lever table shows each lever's weight if it were the only one.
3. **Physics allows a cost at about parity, not below it.** The frontier is $7.03, at the $7 that parity needs, and $7.83 with GFI's
   prices. Before the protectant and antifoam were counted it was $5.49. Antifoam matters most: with a quarter of the sparger's oxygen
   transfer lost, oxygen limits the tank at 177 g/L, so the 320 g/L step adds nothing; with no antifoam effect the frontier would be
   $6.33. Every step is possible by the notes' own calculations. None is shown for meat cells. The odds above are for single levers.
   The odds of all of them together are far below any one of them.
4. **Doubling time is the second lever.** Cells at 16 hours save $3.95 after the medium is cut. The note puts 7% on a meat line
   reaching it by 2035.
5. **What to measure first**, by the size of the step: the litres of medium a kilo of meat cells need at a doubling time near 24
   hours (waste per kilo); then the doubling time of low-waste cells in suspension; then how much oxygen transfer antifoam costs in a
   dense culture; then whether any filter holds a quarter cells by volume for a month.

## 4. What it assumes and holds fixed

- The 6.4 L/kg needs a concentrate of 100 g/L dosed into the tank and a salt budget. The feed strength and the salt floor are
  unsourced judgements in `min_litres_per_kg.md`, and they move the answer most.
- The scenario's tank design (tricks and shape, chosen for Central) and a 20 m³ stirred tank in perfusion are held. A tank
  design chosen again for the new case, and the cheapest size, would add less than 1%: `tank_size.md` finds the cheapest size within
  0.5% of 20 m³.
- Oxygen, with antifoam counted, binds at 177 g/L before the thickness limit, so the 320 g/L step is worth nothing here. Without the
  antifoam effect it would be bound by the column loop's checks first (`thick_culture.md`).
- If perfusion fails at 20 m³, the answer is `no_perfusion_downside.md`, not this ladder.
- The order of the steps affects each step's size. The total does not depend on it.
