# The frontier: what is possible if every lever goes to its limit

Date: 2026-11-15. Code: `frontier.py`; tests: `tests/test_frontier.py`. Costs are 2025 dollars per kg of wet cells. The scenarios say what
the model assumes. This asks what is possible. It starts from the central scenario ($26.64) and moves one lever at a time to the
limit that the research notes support, keeping each one moved. It changes no default.

## 1. The ladder

| Step (each kept moved) | Cost | Change | Odds, from the note that studied it |
|---|---|---|---|
| Central scenario | **$26.64** | | |
| Medium at the least the physics allows: 6.4 L/kg, fed as a concentrate | $12.28 | −14.36 | physically possible, 60% (6 L/kg or less); a meat-cell process reporting 11 L/kg or less by 2030, 10% (`min_litres_per_kg.md`) |
| Cells double in 16 hours | $7.79 | −4.49 | physics allows about 8 h; a meat line in suspension at 50 g/L or more doubling in 16 h or less by 2035, 7% (`gf_and_doubling_bounds.md`) |
| Dialyser-grade hollow fibres as the filter | $7.15 | −0.64 | holds 25% cells for a month, 15% (`retention_alternatives.md`) |
| Medium at $0.05 a litre | $7.15 | 0.00 | an aspiration; the lowest company report is $0.07 (`medium_cost_gfi.md`) |
| Growth factors returned by the filter | $6.97 | −0.18 | a filter that halves growth-factor cost, 20% (`gf_and_doubling_bounds.md`) |
| Culture at 320 g/L in place of 258 | $6.36 | −0.61 | held for a month at 20 m³ with everything solved, 6% (`thick_culture.md`) |
| A food-grade plant with shared medium | $5.76 | −0.60 | nobody has built one (`cheap_plant_study.md`) |
| Runs lost 0.2% a day, as in pharma | $5.59 | −0.16 | makers report 0.6–2% a day |
| Gas at up to 6 mm/s | **$5.49** | −0.10 | about even odds that it works at this size (`gas_flow_cap.md`) |

With GFI's cheapest amino-acid prices in the nutrient floor (`nutrient_floor.md`), the frontier is **$6.29**. Price parity with $12
meat needs about $7 a kilo of cells.

## 2. Each lever on its own, from Central

| Lever | Cost alone | Change |
|---|---|---|
| Medium at 6.4 L/kg | $12.28 | −14.36 |
| Dialyser-grade hollow fibres | $18.00 | −8.64 |
| Cells double in 16 hours | $22.49 | −4.15 |
| Medium at $0.05 a litre | $22.68 | −3.96 |
| Growth factors returned by the filter | $24.09 | −2.55 |
| A food-grade plant with shared medium | $24.34 | −2.30 |
| Culture at 320 g/L | $25.71 | −0.92 |
| Runs lost 0.2% a day | $25.83 | −0.81 |
| Gas at up to 6 mm/s | $26.39 | −0.25 |

These match the studies they come from: the same $18.00, $22.68, $22.49 and $24.34 as in their pull requests.

## 3. What this says

1. **The litres of medium per kilo are the lever.** At 6.4 L/kg, Central costs $12.28 with nothing else changed. Fewer litres cut three costs at once: the medium, the
   growth factors, and the filtering (the filter clears the litres the bleed does not carry out). The central cells make more
   ammonia, which is why they need 28.
2. **Levers share what they save.** The dialyser-grade fibres save $8.64 alone and only $0.64 after the medium is cut, because
   there is then little liquid to filter. The $0.05 medium saves $3.96 alone and nothing after, because at 6.4 L/kg the medium is
   already at the nutrient floor. Read the ladder as one path. The single-lever table shows each lever's weight if it were
   the only one.
3. **Physics allows a cost below parity.** The frontier is $5.49, below the $7 that parity needs, and $6.29 with GFI's prices.
   Every step is possible by the notes' own calculations. None is shown for meat cells. The odds above are for single levers.
   The odds of all of them together are far below any one of them.
4. **Doubling time is the second lever.** Cells at 16 hours save $4.49 after the medium is cut. The note puts 7% on a meat line
   reaching it by 2035.
5. **What to measure first**, by the size of the step: the litres of medium a kilo of meat cells need at a doubling time near 24
   hours (waste per kilo); then the doubling time of low-waste cells in suspension; then whether any filter holds a quarter cells by
   volume for a month.

## 4. What it assumes and holds fixed

- The 6.4 L/kg needs a concentrate of 100 g/L dosed into the tank and a salt budget. The feed strength and the salt floor are
  unsourced judgements in `min_litres_per_kg.md`, and they move the answer most.
- The scenario's tank design (tricks and shape, chosen for Central) and a 20 m³ stirred tank in perfusion are held. A tank
  design chosen again for the new case, and the cheapest size, would add less than 1%: `tank_size.md` finds the cheapest size within
  0.5% of 20 m³.
- At 320 g/L the column loop's checks may bind first (`thick_culture.md`). That step is worth $0.61 here, and may be worth $0.4 less.
- If perfusion fails at 20 m³, the answer is `no_perfusion_downside.md`, not this ladder.
- The order of the steps affects each step's size. The total does not depend on it.
