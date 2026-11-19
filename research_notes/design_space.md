# Exploring the tank's design options: price the limits first, then search the designs

> Repinned 2026-11-19 (scenario restructure): every kind of cell weighs 2 ng, so the best case's (Engineered cells, all favourable) cells are no longer Humbird's 3 ng; it costs $11.67 at most likely values, not $11.46, and its figures here are the earlier ones unless a table says otherwise (the tests pin the new ones). The selected cells' ammonia range now runs from 0.04 mol/kg.

> Names (2026-11-19): "Selected cells" was called Central; "Engineered cells, all favourable" was called the best case.

> 2026-11-19 (scenario restructure): rungs 1-3 of the ladder are now batches (fed-batch at 20 m³), held by their waste, which no tank
> design moves, so the search covers the cases run in perfusion. The published cells are searched in perfusion as the cautious scenario
> (the old rung 1's switches; same figures). The old rung 2 (published cells in perfusion with the process changes) is no longer a case;
> its figures below are kept as history. Rung numbers in the text are the old ladder's.

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50.

> Repinned 2026-11-19 (audit batch): ammonia tolerance 4 mM, lost runs pay for their membranes, glucose from the cells' balance (published cells need about 95 L/kg); see audit_2026-11-19.md.

Date: 2026-11-16; recomputed the same day after the scenarios adopted the lower dissolved-oxygen setpoint this search found. Code: `design_space.py`; test: `tests/test_design_space.py`. Costs are 2025 dollars per kg of wet cells. Nothing
here changes a default or a scenario.

**The aim** (Pablo): design the tank until CO₂, oxygen and the other compounds are no longer the bottleneck, so that only the
thickness of the culture is (258 g/L, Humbird's viscosity estimate). **The question:** how to explore the design options
efficiently.

## 1. The method

1. **Price each limit before designing anything** (`limit_prices`). For a scenario, lift each limit for free and read the cost. That
   is the most any design attacking that limit could be worth. A limit worth $0.3 a kilo needs no design work.
2. **Search the designs the model already has** (`designs`, `frontier`). Every combination of five options, 144 designs a scenario,
   in about a second for all six scenarios: the column (none, CO₂ only, with recycled oxygen), headspace pressure (0.33, 1, 2 bar),
   tank shape (liquid 1.6, 1.0, 0.75, 0.5 times as deep as wide), fat in the feed, and a bubble cage. (The first version also had the
   dissolved-oxygen setpoint as an option; see point 3 of section 4.) A design is kept only if its column loop passes the pH and pass-rate
   checks. Each is scored by cost and by how many of its elements nobody has run with animal cells.
3. **Compare with the ideal** (`ideal`): the ordinary tall tank with every gas and mixing limit lifted for free. No design that keeps
   the scenario's feed can cost less; the gap is what is left to gain from the tank's gas exchange. Since the 2026-11-19 audit a
   design that takes fat from the feed can cost less than the ideal, for cells whose lactate sets the medium (section 4, point 2).
4. **Only then** send the surviving designs to CFD (for the numbers that depend on geometry, `cfd_plan.md`) and to bench tests (for
   the cells).

The scenarios' own tank designs are a subset of this search, and the search reproduces each of them exactly.

## 2. What the search finds

| case | ordinary tank | the scenario's design | cheapest design, no cage | cheapest design, with a bubble cage | perfect gas exchange |
|---|---|---|---|---|---|
| Published cells, in perfusion | $111.89 (46 g/L, CO₂) | $92.17 | $64.94 (175 g/L, oxygen; 4 unproven) | $61.78 (258 g/L, thickness; 4 unproven) | **$84.85** (258 g/L) |
| 4. Selected cells | $39.18 (87 g/L, CO₂) | $32.80 | $31.40 (258 g/L, thickness; 5 unproven) | $31.09 (258 g/L, thickness; 3 unproven) | **$30.66** (258 g/L) |
| 5. Shared-medium plant | $32.85 (87 g/L, CO₂) | $29.94 | $29.27 (258 g/L, thickness; 5 unproven) | $29.04 (258 g/L, thickness; 2 unproven) | **$28.75** (258 g/L) |
| 6. Engineered cells | $20.17 (87 g/L, CO₂) | $17.27 | $16.60 (258 g/L, thickness; 5 unproven) | $16.37 (258 g/L, thickness; 2 unproven) | **$16.08** (258 g/L) |
| 7. Engineered cells, all favourable | $12.29 (108 g/L, CO₂) | $11.67 | $11.48 (258 g/L, thickness; 4 unproven) | $11.39 (258 g/L, thickness; 2 unproven) | **$11.20** (258 g/L) |

"Unproven" counts elements nobody has run with animal cells: the column (1; 2 with recycled oxygen), 1 bar of extra pressure (1; 2
bar counts 2), a tank squatter than those in use (1), fat taken from the feed (1), the bubble cage (1). A tank as deep as wide is
standard practice and counts 0. **The cage's three numbers are judgements**
(`vm_cage_*`), so its column is shown apart.

The cheapest design for each number of unproven elements:

| Published cells, in perfusion, no cage: unproven elements | cheapest design that passes the checks | cost | density, limit |
|---|---|---|---|
| 0 | liquid as deep as wide | $104.42 | 63 g/L, CO₂ |
| 1 | liquid as deep as wide, and fat taken from the feed | $75.89 | 79 g/L, oxygen |
| 2 | a column that strips CO₂, and fat taken from the feed | $74.58 | 82 g/L, oxygen |
| 3 | a column that strips CO₂, 1 bar of extra pressure, and fat taken from the feed | $68.51 | 120 g/L, oxygen |
| 4 | a column that strips CO₂, 2 bar of extra pressure, liquid as deep as wide, and fat taken from the feed | $64.94 | 175 g/L, oxygen |

| Published cells, in perfusion, with a bubble cage: unproven elements | cheapest design that passes the checks | cost | density, limit |
|---|---|---|---|
| 0 | liquid as deep as wide | $104.42 | 63 g/L, CO₂ |
| 1 | liquid as deep as wide, and fat taken from the feed | $75.89 | 79 g/L, oxygen |
| 2 | liquid as deep as wide, fat taken from the feed, and a stirred tank with a bubble cage | $63.45 | 210 g/L, oxygen |
| 3 | 1 bar of extra pressure, liquid as deep as wide, fat taken from the feed, and a stirred tank with a bubble cage | $61.93 | 258 g/L, thickness |
| 4 | a column that strips CO₂, 1 bar of extra pressure, fat taken from the feed, and a stirred tank with a bubble cage | $61.78 | 258 g/L, thickness |

| 4. Selected cells, no cage: unproven elements | cheapest design that passes the checks | cost | density, limit |
|---|---|---|---|
| 0 | liquid as deep as wide | $36.32 | 119 g/L, CO₂ |
| 1 | a column that strips CO₂ | $35.05 | 133 g/L, oxygen |
| 2 | a column that strips CO₂, 1 bar of extra pressure, and liquid as deep as wide | $32.80 | 191 g/L, oxygen |
| 3 | a column that strips CO₂, 1 bar of extra pressure, and fat taken from the feed | $32.36 | 196 g/L, oxygen |
| 4 | a column that strips CO₂, 2 bar of extra pressure, and liquid half as deep as wide | $31.73 | 258 g/L, thickness |
| 5 | a column that strips CO₂, 2 bar of extra pressure, liquid 0.75 times as deep as wide, and fat taken from the feed | $31.40 | 258 g/L, thickness |

| 4. Selected cells, with a bubble cage: unproven elements | cheapest design that passes the checks | cost | density, limit |
|---|---|---|---|
| 0 | liquid as deep as wide | $36.32 | 119 g/L, CO₂ |
| 1 | liquid as deep as wide, and a stirred tank with a bubble cage | $31.54 | 241 g/L, oxygen |
| 2 | 1 bar of extra pressure, liquid as deep as wide, and a stirred tank with a bubble cage | $31.19 | 258 g/L, thickness |
| 3 | a column that strips CO₂, 1 bar of extra pressure, and a stirred tank with a bubble cage | $31.09 | 258 g/L, thickness |

## 3. What each limit is worth

| Published cells, in perfusion: if this were free | cost | change | density, what then binds |
|---|---|---|---|
| the scenario as it is | $92.17 |  | 120 g/L, oxygen |
| CO₂ removal lifted | $92.17 |  | 120 g/L, oxygen |
| oxygen supply lifted | $85.21 | −$6.96 | 258 g/L, thickness |
| mixing lifted | $92.17 |  | 120 g/L, oxygen |
| every gas limit lifted (CO₂, oxygen, mixing) | $85.21 | −$6.96 | 258 g/L, thickness |
| every gas limit lifted, and the culture as thick as 320 g/L | $84.03 | −$8.14 | 320 g/L, thickness |
| medium at the least the physics allows (6.7 L/kg; this thin culture needs 8.3, what leaves with the cells) | $23.14 | −$69.03 | 120 g/L, oxygen |
| filter membranes that never wear out | $54.69 | −$37.48 | 120 g/L, oxygen |
| no bubble protectant to buy | $86.44 | −$5.73 | 120 g/L, oxygen |
| no growth factors to buy | $92.17 |  | 120 g/L, oxygen |
| no runs lost | $82.81 | −$9.35 | 120 g/L, oxygen |
| a yeast plant with what animal cells need | $82.69 | −$9.48 | 120 g/L, oxygen |

| 4. Selected cells: if this were free | cost | change | density, what then binds |
|---|---|---|---|
| the scenario as it is | $32.80 |  | 191 g/L, oxygen |
| CO₂ removal lifted | $32.80 |  | 191 g/L, oxygen |
| oxygen supply lifted | $31.18 | −$1.63 | 258 g/L, thickness |
| mixing lifted | $32.80 |  | 191 g/L, oxygen |
| every gas limit lifted (CO₂, oxygen, mixing) | $31.18 | −$1.63 | 258 g/L, thickness |
| every gas limit lifted, and the culture as thick as 320 g/L | $30.27 | −$2.53 | 320 g/L, thickness |
| medium at the least the physics allows (6.4 L/kg) | $14.16 | −$18.64 | 191 g/L, oxygen |
| filter membranes that never wear out | $20.01 | −$12.79 | 191 g/L, oxygen |
| no bubble protectant to buy | $30.70 | −$2.10 | 191 g/L, oxygen |
| no growth factors to buy | $32.80 |  | 191 g/L, oxygen |
| no runs lost | $29.66 | −$3.14 | 191 g/L, oxygen |
| a yeast plant with what animal cells need | $28.00 | −$4.80 | 191 g/L, oxygen |

| 7. Engineered cells, all favourable: if this were free | cost | change | density, what then binds |
|---|---|---|---|
| the scenario as it is | $11.67 |  | 218 g/L, oxygen |
| CO₂ removal lifted | $11.67 |  | 218 g/L, oxygen |
| oxygen supply lifted | $11.51 | −$0.17 | 258 g/L, thickness |
| mixing lifted | $11.67 |  | 218 g/L, oxygen |
| every gas limit lifted (CO₂, oxygen, mixing) | $11.51 | −$0.17 | 258 g/L, thickness |
| every gas limit lifted, and the culture as thick as 320 g/L | $11.32 | −$0.35 | 320 g/L, thickness |
| medium at the least the physics allows (6.0 L/kg) | $8.00 | −$3.67 | 218 g/L, oxygen |
| filter membranes that never wear out | $7.98 | −$3.69 | 218 g/L, oxygen |
| no bubble protectant to buy | $10.85 | −$0.82 | 218 g/L, oxygen |
| no growth factors to buy | $11.67 |  | 218 g/L, oxygen |
| no runs lost | $11.08 | −$0.59 | 218 g/L, oxygen |
| a yeast plant with what animal cells need | $10.56 | −$1.12 | 218 g/L, oxygen |

## 4. What this says

1. **The aim is reachable on paper, and it is worth little beyond the published cells.** Designs exist that leave only the thickness limit binding:
   with a bubble cage and 1 bar of pressure (2–4 unproven elements), or without a cage at 2 bar (4–5; the published cells then reach
   only 175 g/L). But for the selected and engineered cells the scenario's own design is already within $0.3–2.1 of the ideal, and the best case within $0.3.
2. **For the published cells gas exchange is still worth $27 a kilo, but it is no longer what matters most.** Perfect gas exchange
   takes them from $111.89 to $84.85. Before the 2026-11-19 audit it took them from $56.99 to $28.82: the same dollars, then half
   the cost, now a quarter. A column and 1 bar of pressure give $92.17, which is $19.7 of it with two unproven elements. What changed
   is the medium. With glucose taken from the cells' own balance, these cells turn so much of it into lactate that washing the
   lactate out takes 95 litres a kilo, and no tank design changes that.
   **Fat taken from the feed is now the largest single option for these cells.** It takes the ordinary tank from $111.89 to $81.78.
   Fed fat replaces glucose the cells would turn into fat, so they take up 3.2 mol of glucose a kilo instead of 4.5, make 3.3 mol
   of lactate instead of 4.8, and need 66 litres of medium instead of 95. That is why the cheapest designs ($64.94 without a cage,
   $61.78 with one) cost less than "perfect gas exchange" ($84.85): the ideal keeps the scenario's feed. With fat fed and every gas
   limit lifted the same tank costs $61.26, and no fat-fed design costs less than that. The same holds at rung 2 ($54.58 and $54.39
   against an ideal of $74.59; $54.02 with fat fed). From rung 3 on ammonia sets the medium, fed fat does not cut the litres, and no
   design costs less than the ideal. This result rests on two things nobody has measured: how much fed fat displaces, and that the
   cells keep the same lactate per mol of glucose when they take up less. It is the least certain number in this note.
3. **A free improvement, now adopted: the dissolved-oxygen setpoint.** Humbird's numbers imply the tank is held at 0.28 mmol/L, 130%
   of air saturation. Holding it at about half of air saturation, as pharma does, widens the oxygen driving force and needs nothing
   unproven. The first run of this search found it worth $0.5 in Central ($29.92 to $29.42, on the model of 2026-11-16) and $0.6 at rung 2, and unused by the
   scenarios. Every scenario now carries it (`scenarios.always`, input `sc_do_setpoint`); the tables here include it.
4. **Once the gas limits are lifted, the cost that remains is the litres of medium.** In Central, perfect gas exchange saves $1.6;
   medium at the least the physics allows saves $18.6; membranes that never wear out save $12.8. Ammonia does not limit the density
   of a perfusion tank; it sets the litres, and the litres set the medium and the filtering. For the published cells lactate sets
   the litres, and the same two rows save $59.5 and $31.8, more than perfect gas exchange ($27.0). "No runs lost" is worth more than
   it was ($3.1 in Central, $1.2 before), because a lost run now also throws its membranes away. (Growth factors are inside the
   complete medium's price, so "no growth factors to buy" saves nothing in Central or for the published cells.)
5. **Thicker than 258 g/L is worth about $1.** Raising the thickness limit to 320 g/L saves about $1 in Central once the gas limits
   are lifted, and $0.1 in the best case, because a denser culture sends more permeate through the filter.
6. **2 bar of pressure does what the cage does**, with steel instead of mesh: it reaches the thickness limit without a cage. Cells at
   3 bar absolute were not examined in the gas-exchange study; it is the top of the pressure input's range.

## 5. Limits of this search

- It searches the options the model has. Two spargers, gas exchange on the filter loop, impeller choice and membranes are not in it
  (`bioreactor_design_tricks.md`); each needs a lever first.
- "Unproven" is a count, not a probability. The odds in the research notes (column 60%, 2 bar absolute 85%) could weight it.
- The ideal lifts gas limits only. It keeps the scenario's cells, feed, plant, losses and prices. So it does not bound a design
  that changes the feed (fat taken from the feed).
- The loop checks rest on one study of pH exposure (`gas_exchange_study.md` §8). A design whose loop fails at full density is dropped;
  running it thinner might pass (the vessel grid now does this, `vessels._thinned`; the search does not yet).
