# The frontier: what is possible if every lever goes to its limit

> Names (2026-11-19): the low-lactate example was earlier called Central; the all-favourable example was earlier called the best case. Cells are described by their traits, never as a named kind of cell.

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50.
> Repinned 2026-11-19 (audit batch): ammonia tolerance 4 mM, lost runs pay for their membranes, glucose from the cells' balance (published cells need about 95 L/kg); see audit_2026-11-19.md.
> What this changed here: Central rose from $26.43 to $32.80 and the frontier stayed at $7.16. The first step, cutting the medium to
> 6.4 L/kg, is now worth $18.64, not $12.34: Central starts from 35 L/kg, and the frontier's litres do not depend on the ammonia tolerance.
> Central is now 4.6 times the frontier, not 3.7 times.
> Lost runs are a bigger lever on their own ($2.53, was $0.97), because a lost run now also throws its membranes away.

Date: 2026-11-15; recomputed 2026-11-16 with the protectant, antifoam and the plant ladder of PR #32, and again with the scenarios' lower dissolved-oxygen setpoint and with the medium floored at the culture that leaves with the cells (the frontier went from $6.85 to $6.86, the steps after faster growth up by $0.36). Code: `frontier.py`; tests: `tests/test_frontier.py`. Costs are 2025 dollars per kg of wet cells. The scenarios say what
the model assumes. This asks what is possible. It starts from the central scenario ($32.80) and moves one lever at a time to the
limit that the research notes support, keeping each one moved. It changes no default.

## 1. The ladder

| Step (each kept moved) | Cost | Change | Odds, from the note that studied it |
|---|---|---|---|
| Low-lactate example | **$32.80** | | |
| Medium at the least the physics allows: 6.4 L/kg, fed as a concentrate | $14.16 | −18.64 | physically possible, 60% (6 L/kg or less); a meat-cell process reporting 11 L/kg or less by 2030, 10% (`min_litres_per_kg.md`) |
| Cells double in 16 hours | $10.56 | −3.60 | physics allows about 8 h; a meat line in suspension at 50 g/L or more doubling in 16 h or less by 2035, 7% (`gf_and_doubling_bounds.md`) |
| Dialyser-grade hollow fibres as the filter | $10.56 | 0.00 | holds 25% cells for a month, 15% (`retention_alternatives.md`) |
| Medium at the nutrient floor | $10.55 | −0.01 | only what the cells eat, at GFI's feed-grade amino-acid prices; the lowest company report is $0.07 a litre (`nutrient_floor.md`) |
| Growth factors returned by the filter | $10.55 | 0.00 | a filter that halves growth-factor cost, 20% (`gf_and_doubling_bounds.md`) |
| Culture at 320 g/L in place of 258 | $10.55 | 0.00 | held for a month at 20 m³ with everything solved, 6% (`thick_culture.md`) |
| A food-grade plant with shared medium | $8.78 | −1.77 | nobody has built one (`cheap_plant_study.md`) |
| Runs lost 0.2% a day, as in pharma | $8.44 | −0.34 | makers report 0.6–2% a day |
| Gas at up to 6 mm/s | **$7.16** | −1.28 | about even odds that it works at this size (`gas_flow_cap.md`) |

The nutrient floor is now GFI's feed-grade amino acids (`nutrient_floor.md`), so the frontier already carries GFI's prices. It was
$6.86 on the old floor and $7.66 with GFI's prices; it is $7.16 because the salts, buffer and vitamins were also cut from $0.90 to $0.40 a kilo. Price parity with $12 meat needs about $6.1 a kilo of cells (the shelf rule: cost plus $2.5, over 72%).

**Why the nutrient-floor step adds almost nothing.** Central's $0.20 a litre is a complete medium, with the growth factors in the
price. At 6.4 L/kg that is $1.28 a kilo, under what its nutrients and growth factors cost, so the model charges those (the $2.00
nutrient floor plus Central's 30% of Humbird's growth-factor price). The floor setting charges the same things, so it adds
nothing once the litres are cut.

## 2. Each lever on its own, from the low-lactate example

| Lever | Cost alone | Change |
|---|---|---|
| Medium at 6.4 L/kg | $14.16 | −18.64 |
| Dialyser-grade hollow fibres | $20.29 | −12.52 |
| Cells double in 16 hours | $28.30 | −4.50 |
| A food-grade plant with shared medium | $29.94 | −2.86 |
| Runs lost 0.2% a day | $30.27 | −2.53 |
| Gas at up to 6 mm/s | $31.13 | −1.67 |
| Medium at the nutrient floor | $31.45 | −1.35 |
| Growth factors returned by the filter | $32.80 | 0.00 |
| Culture at 320 g/L | $32.80 | 0.00 |

These are the model's figures on 2026-11-19, after the audit batch. The studies they come from (`retention_alternatives.md`,
`nutrient_floor.md`, `gf_and_doubling_bounds.md`, `no_perfusion_downside.md`) are repinned in the same batch. The three levers
that act on the medium and its filtering grew, because Central now uses 35 L/kg: the least medium (from $12.34 to $18.64), the
dialyser-grade fibres ($8.15 to $12.52) and the nutrient floor ($0.66 to $1.35). Fewer lost runs grew from $0.97 to $2.53 and now
rank above the gas: a lost run throws its filter membranes away early, and Central has more membranes to lose.

## 3. What this says

1. **The litres of medium per kilo are the lever.** At 6.4 L/kg, Central costs $14.16 with nothing else changed. That one step is
   73% of the way from Central to the frontier (it was 64%). Fewer litres cut two
   costs at once: the medium (with its growth factors, which are in Central's $0.20 a litre), and the filtering (the filter clears the litres the bleed does not carry out). The low-lactate example's cells make more ammonia, which is why they need 35 (28 before the tolerance fell from 5 to 4 mmol/L).
2. **Levers share what they save.** The dialyser-grade fibres save $12.52 alone and nothing after the medium is cut, because there is
   then almost no liquid to filter. The medium at the nutrient floor saves $1.35 alone and nothing after, because at 6.4 L/kg the
   $0.20 medium is already charged its nutrients plus its growth factors (section 1). Returning the growth factors saves nothing
   alone, because Central's growth factors are inside its medium's price, and nothing after, because at 6.4 L/kg the bleed already
   carries out most of the liquid. (Before 2026-11-19, with growth factors bought on top, the $0.05 medium saved $3.96 alone and
   returning them $2.39.) Read the ladder as one path. The single-lever table shows each lever's weight if it were the only one.
3. **Physics allows a cost near parity, not at it.** The frontier is $7.16, about $1 above the $6.1 that parity with $12 meat needs.
   The audit batch did not move it. The 6.4 L/kg step assumes cells that release no ammonia, so the tolerance does not enter. And at
   16 hours the bleed carries out all the liquid, so there is no filter membrane to lose with a lost run. What moved is the distance to it. Central is now 4.6 times the frontier, not 3.7 times.
   (The frontier was $6.86 before the nutrient floor rose to GFI's feed-grade prices on 2026-11-19; an earlier version of this note put parity
   at $7, under the old shelf rule of cost plus $5). Before the protectant and antifoam were counted it was $5.49. Antifoam matters most: with a quarter of the sparger's oxygen
   transfer lost, oxygen limits the tank, so the 320 g/L step adds nothing; with no antifoam effect the frontier would be
   $6.46. Every step is possible by the notes' own calculations. None is shown for meat cells. The odds above are for single levers.
   The odds of all of them together are far below any one of them.
4. **Doubling time is the second lever.** Cells at 16 hours save $3.60 after the medium is cut. The note puts 7% on a meat line
   reaching it by 2035.
5. **What to measure first**, by the size of the step: the litres of medium a kilo of meat cells need at a doubling time near 24
   hours (waste per kilo); then the doubling time of low-waste cells in suspension; then how much oxygen transfer antifoam costs in a
   dense culture; then whether any filter holds a quarter cells by volume for a month.

## 4. What it assumes and holds fixed

- The 6.4 L/kg needs a concentrate of 100 g/L dosed into the tank and a salt budget. The feed strength and the salt floor are
  unsourced judgements in `min_litres_per_kg.md`, and they move the answer most.
- The scenario's tank design (tricks and shape, chosen for Central) and a 20 m³ stirred tank in perfusion are held. A tank
  design chosen again for the new case, and the cheapest size, would add less than 2%: `tank_size.md` finds Central's cheapest size at
  43 m³, 1.6% below 20 m³.
- Oxygen, with antifoam counted, binds before the thickness limit, so the 320 g/L step is worth nothing here
  (`thick_culture.md`: in Central, oxygen with the culture's viscosity binds first, at 151 g/L).
- If perfusion fails at 20 m³, the answer is `no_perfusion_downside.md`, not this ladder.
- The order of the steps affects each step's size. The total does not depend on it.
