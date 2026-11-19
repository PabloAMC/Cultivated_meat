# Exploring the tank's design options: price the limits first, then search the designs

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50.

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
3. **Compare with the ideal** (`ideal`): the ordinary tall tank with every gas and mixing limit lifted for free. No design here can
   cost less; the gap is what is left to gain from the tank.
4. **Only then** send the surviving designs to CFD (for the numbers that depend on geometry, `cfd_plan.md`) and to bench tests (for
   the cells).

The scenarios' own tank designs are a subset of this search, and the search reproduces each of them exactly.

## 2. What the search finds

| case | ordinary tank | the scenario's design | cheapest design, no cage | cheapest design, with a bubble cage | perfect gas exchange |
|---|---|---|---|---|---|
| 1. Today's cells | $56.99 (46 g/L, CO₂) | $56.99 | $32.69 (175 g/L, oxygen; 4 unproven) | $29.41 (258 g/L, thickness; 4 unproven) | **$28.82** (258 g/L) |
| 2. Plus process changes | $35.79 (93 g/L, CO₂) | $27.74 | $26.15 (258 g/L, thickness; 4 unproven) | $25.97 (254 g/L, CO₂; 3 unproven) | **$25.53** (258 g/L) |
| 3. Central | $33.21 (87 g/L, CO₂) | $26.43 | $24.94 (258 g/L, thickness; 5 unproven) | $24.63 (258 g/L, thickness; 3 unproven) | **$24.20** (258 g/L) |
| 4. Shared-medium plant | $26.88 (87 g/L, CO₂) | $23.57 | $22.81 (258 g/L, thickness; 5 unproven) | $22.58 (258 g/L, thickness; 2 unproven) | **$22.29** (258 g/L) |
| 5. Best case | $10.71 (120 g/L, CO₂) | $9.96 | $9.90 (258 g/L, thickness; 4 unproven) | $9.79 (258 g/L, thickness; 3 unproven) | **$9.64** (258 g/L) |
| Forecast for 2035 | $26.27 (87 g/L, CO₂) | $23.24 | $22.54 (258 g/L, thickness; 5 unproven) | $22.32 (258 g/L, thickness; 2 unproven) | **$22.05** (258 g/L) |

"Unproven" counts elements nobody has run with animal cells: the column (1; 2 with recycled oxygen), 1 bar of extra pressure (1; 2
bar counts 2), a tank squatter than those in use (1), fat taken from the feed (1), the bubble cage (1). A tank as deep as wide is
standard practice and counts 0. **The cage's three numbers are judgements**
(`vm_cage_*`), so its column is shown apart.

The cheapest design for each number of unproven elements:

| 1. Today's cells, no cage: unproven elements | cheapest design that passes the checks | cost | density, limit |
|---|---|---|---|
| 0 | liquid as deep as wide | $49.15 | 63 g/L, CO₂ |
| 1 | a column that strips CO₂ | $42.77 | 82 g/L, oxygen |
| 2 | a column that strips CO₂, and 1 bar of extra pressure | $36.42 | 120 g/L, oxygen |
| 4 | a column that strips CO₂, 2 bar of extra pressure, liquid as deep as wide, and fat taken from the feed | $32.69 | 175 g/L, oxygen |

| 1. Today's cells, with a bubble cage: unproven elements | cheapest design that passes the checks | cost | density, limit |
|---|---|---|---|
| 0 | liquid as deep as wide | $49.15 | 63 g/L, CO₂ |
| 1 | liquid as deep as wide, and a stirred tank with a bubble cage | $31.08 | 210 g/L, oxygen |
| 2 | a column that strips CO₂, and a stirred tank with a bubble cage | $30.61 | 217 g/L, oxygen |
| 3 | 1 bar of extra pressure, liquid as deep as wide, fat taken from the feed, and a stirred tank with a bubble cage | $29.56 | 258 g/L, thickness |
| 4 | a column that strips CO₂, 1 bar of extra pressure, fat taken from the feed, and a stirred tank with a bubble cage | $29.41 | 258 g/L, thickness |

| 3. Central, no cage: unproven elements | cheapest design that passes the checks | cost | density, limit |
|---|---|---|---|
| 0 | liquid as deep as wide | $30.15 | 119 g/L, CO₂ |
| 1 | a column that strips CO₂ | $28.82 | 133 g/L, oxygen |
| 2 | a column that strips CO₂, 1 bar of extra pressure, and liquid as deep as wide | $26.43 | 191 g/L, oxygen |
| 3 | a column that strips CO₂, 1 bar of extra pressure, and fat taken from the feed | $25.98 | 196 g/L, oxygen |
| 4 | a column that strips CO₂, 2 bar of extra pressure, and liquid half as deep as wide | $25.27 | 258 g/L, thickness |
| 5 | a column that strips CO₂, 2 bar of extra pressure, liquid 0.75 times as deep as wide, and fat taken from the feed | $24.94 | 258 g/L, thickness |

| 3. Central, with a bubble cage: unproven elements | cheapest design that passes the checks | cost | density, limit |
|---|---|---|---|
| 0 | liquid as deep as wide | $30.15 | 119 g/L, CO₂ |
| 1 | liquid as deep as wide, and a stirred tank with a bubble cage | $25.09 | 241 g/L, oxygen |
| 2 | 1 bar of extra pressure, liquid as deep as wide, and a stirred tank with a bubble cage | $24.73 | 258 g/L, thickness |
| 3 | a column that strips CO₂, 1 bar of extra pressure, and a stirred tank with a bubble cage | $24.63 | 258 g/L, thickness |

## 3. What each limit is worth

| 1. Today's cells: if this were free | cost | change | density, what then binds |
|---|---|---|---|
| the scenario as it is | $56.99 |  | 46 g/L, CO₂ |
| CO₂ removal lifted | $42.18 | −$14.81 | 82 g/L, oxygen |
| oxygen supply lifted | $56.99 |  | 46 g/L, CO₂ |
| mixing lifted | $56.99 |  | 46 g/L, CO₂ |
| every gas limit lifted (CO₂, oxygen, mixing) | $28.82 | −$28.16 | 258 g/L, thickness |
| every gas limit lifted, and the culture as thick as 320 g/L | $27.63 | −$29.36 | 320 g/L, thickness |
| medium at the least the physics allows (6.7 L/kg; this thin culture needs 21.6, what leaves with the cells) | $52.37 | −$4.62 | 46 g/L, CO₂ |
| filter membranes that never wear out | $54.63 | −$2.36 | 46 g/L, CO₂ |
| no bubble protectant to buy | $55.31 | −$1.68 | 46 g/L, CO₂ |
| no growth factors to buy | $56.99 |  | 46 g/L, CO₂ |
| no runs lost | $49.44 | −$7.55 | 46 g/L, CO₂ |
| a yeast plant with what animal cells need | $31.92 | −$25.07 | 46 g/L, CO₂ |

| 3. Central: if this were free | cost | change | density, what then binds |
|---|---|---|---|
| the scenario as it is | $26.43 |  | 191 g/L, oxygen |
| CO₂ removal lifted | $26.43 |  | 191 g/L, oxygen |
| oxygen supply lifted | $24.72 | −$1.71 | 258 g/L, thickness |
| mixing lifted | $26.43 |  | 191 g/L, oxygen |
| every gas limit lifted (CO₂, oxygen, mixing) | $24.72 | −$1.71 | 258 g/L, thickness |
| every gas limit lifted, and the culture as thick as 320 g/L | $23.77 | −$2.66 | 320 g/L, thickness |
| medium at the least the physics allows (6.4 L/kg) | $14.09 | −$12.34 | 191 g/L, oxygen |
| filter membranes that never wear out | $18.09 | −$8.33 | 191 g/L, oxygen |
| no bubble protectant to buy | $24.75 | −$1.68 | 191 g/L, oxygen |
| no growth factors to buy | $26.43 |  | 191 g/L, oxygen |
| no runs lost | $25.22 | −$1.21 | 191 g/L, oxygen |
| a yeast plant with what animal cells need | $21.63 | −$4.80 | 191 g/L, oxygen |

| 5. Best case: if this were free | cost | change | density, what then binds |
|---|---|---|---|
| the scenario as it is | $9.96 |  | 258 g/L, thickness |
| CO₂ removal lifted | $9.96 |  | 258 g/L, thickness |
| oxygen supply lifted | $9.96 |  | 258 g/L, thickness |
| mixing lifted | $9.96 |  | 258 g/L, thickness |
| every gas limit lifted (CO₂, oxygen, mixing) | $9.96 |  | 258 g/L, thickness |
| every gas limit lifted, and the culture as thick as 320 g/L | $9.83 | −$0.13 | 320 g/L, thickness |
| medium at the least the physics allows (5.8 L/kg) | $7.63 | −$2.33 | 258 g/L, thickness |
| filter membranes that never wear out | $7.29 | −$2.67 | 258 g/L, thickness |
| no bubble protectant to buy | $9.29 | −$0.67 | 258 g/L, thickness |
| no growth factors to buy | $9.96 |  | 258 g/L, thickness |
| no runs lost | $9.75 | −$0.21 | 258 g/L, thickness |
| a yeast plant with what animal cells need | $9.02 | −$0.94 | 258 g/L, thickness |

## 4. What this says

1. **The aim is reachable on paper, and it is worth little beyond rung 1.** Designs exist that leave only the thickness limit binding:
   with a bubble cage and 1 bar of pressure (2–4 unproven elements), or without a cage at 2 bar (4–5; today's cells then reach only
   175 g/L). But from rung 2 on the scenario's own design is already within $1.2–2.2 of the ideal, and the best case within $0.3.
2. **For today's cells the tank is worth $28 a kilo** ($56.99 to $28.82). A column and 1 bar of pressure give $36.42, which is $20.6 of it with two unproven elements. This is the
   case where tank design matters.
3. **A free improvement, now adopted: the dissolved-oxygen setpoint.** Humbird's numbers imply the tank is held at 0.28 mmol/L, 130%
   of air saturation. Holding it at about half of air saturation, as pharma does, widens the oxygen driving force and needs nothing
   unproven. The first run of this search found it worth $0.5 in Central ($29.92 to $29.42, on the model of 2026-11-16) and $0.6 at rung 2, and unused by the
   scenarios. Every scenario now carries it (`scenarios.always`, input `sc_do_setpoint`); the tables here include it.
4. **Once the gas limits are lifted, the cost that remains is the litres of medium.** In Central, perfect gas exchange saves $1.7;
   medium at the least the physics allows saves $12.3; membranes that never wear out save $8.3. Ammonia does not limit the density
   of a perfusion tank; it sets the litres, and the litres set the medium and the filtering. (Growth factors are now inside the complete
   medium's price, so "no growth factors to buy" saves nothing in Central or for today's cells.)
5. **Thicker than 258 g/L is worth about $1.** Raising the thickness limit to 320 g/L saves about $1 in Central once the gas limits
   are lifted, and $0.1 in the best case, because a denser culture sends more permeate through the filter.
6. **2 bar of pressure does what the cage does**, with steel instead of mesh: it reaches the thickness limit without a cage. Cells at
   3 bar absolute were not examined in the gas-exchange study; it is the top of the pressure input's range.

## 5. Limits of this search

- It searches the options the model has. Two spargers, gas exchange on the filter loop, impeller choice and membranes are not in it
  (`bioreactor_design_tricks.md`); each needs a lever first.
- "Unproven" is a count, not a probability. The odds in the research notes (column 60%, 2 bar absolute 85%) could weight it.
- The ideal lifts gas limits only. It keeps the scenario's cells, plant, losses and prices.
- The loop checks rest on one study of pH exposure (`gas_exchange_study.md` §8). A design whose loop fails at full density is dropped;
  running it thinner might pass (the vessel grid now does this, `vessels._thinned`; the search does not yet).
