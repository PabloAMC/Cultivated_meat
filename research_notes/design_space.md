# Exploring the tank's design options: price the limits first, then search the designs

Date: 2026-11-16. Code: `design_space.py`; test: `tests/test_design_space.py`. Costs are 2025 dollars per kg of wet cells. Nothing
here changes a default or a scenario.

**The aim** (Pablo): design the tank until CO₂, oxygen and the other compounds are no longer the bottleneck, so that only the
thickness of the culture is (258 g/L, Humbird's viscosity estimate). **The question:** how to explore the design options
efficiently.

## 1. The method

1. **Price each limit before designing anything** (`limit_prices`). For a scenario, lift each limit for free and read the cost. That
   is the most any design attacking that limit could be worth. A limit worth $0.3 a kilo needs no design work.
2. **Search the designs the model already has** (`designs`, `frontier`). Every combination of six options, 288 designs a scenario,
   in under two seconds for all six scenarios: the column (none, CO₂ only, with recycled oxygen), headspace pressure (0.33, 1, 2 bar),
   tank shape (liquid 1.6, 1.0, 0.75, 0.5 times as deep as wide), the dissolved-oxygen setpoint (as Humbird's tank implies, or half
   of air saturation), fat in the feed, and a bubble cage. A design is kept only if its column loop passes the pH and pass-rate
   checks. Each is scored by cost and by how many of its elements nobody has run with animal cells.
3. **Compare with the ideal** (`ideal`): the ordinary tall tank with every gas and mixing limit lifted for free. No design here can
   cost less; the gap is what is left to gain from the tank.
4. **Only then** send the surviving designs to CFD (for the numbers that depend on geometry, `cfd_plan.md`) and to bench tests (for
   the cells).

The scenarios' own tank designs are a subset of this search, and the search reproduces each of them exactly.

## 2. What the search finds

| case | ordinary tank | the scenario's design | cheapest design, no cage | cheapest design, with a bubble cage | perfect gas exchange |
|---|---|---|---|---|---|
| 1. Today's cells | $62.96 (46 g/L, CO₂) | $62.96 | $38.66 (175 g/L, oxygen; 4 unproven) | $35.38 (258 g/L, thickness; 4 unproven) | **$34.80** (258 g/L) |
| 2. Plus process changes | $38.77 (93 g/L, CO₂) | $31.33 | $29.14 (258 g/L, thickness; 4 unproven) | $28.95 (254 g/L, CO₂; 3 unproven) | **$28.51** (258 g/L) |
| 3. Central | $36.20 (87 g/L, CO₂) | $29.92 | $27.93 (258 g/L, thickness; 5 unproven) | $27.62 (258 g/L, thickness; 3 unproven) | **$27.19** (258 g/L) |
| 4. Shared-medium plant | $29.86 (87 g/L, CO₂) | $26.81 | $25.80 (258 g/L, thickness; 5 unproven) | $25.57 (258 g/L, thickness; 2 unproven) | **$25.28** (258 g/L) |
| 5. Best case | $10.40 (120 g/L, CO₂) | $9.71 | $9.60 (258 g/L, thickness; 4 unproven) | $9.48 (258 g/L, thickness; 3 unproven) | **$9.33** (258 g/L) |
| Forecast for 2035 | $27.83 (87 g/L, CO₂) | $25.04 | $24.11 (258 g/L, thickness; 5 unproven) | $23.89 (258 g/L, thickness; 2 unproven) | **$23.61** (258 g/L) |

"Unproven" counts elements nobody has run with animal cells: the column (1; 2 with recycled oxygen), 1 bar of extra pressure (1; 2
bar counts 2), a tank squatter than those in use (1), fat taken from the feed (1), the bubble cage (1). A tank as deep as wide and a
dissolved-oxygen setpoint at half of air saturation are standard practice and count 0. **The cage's three numbers are judgements**
(`vm_cage_*`), so its column is shown apart.

The cheapest design for each number of unproven elements:

| 1. Today's cells, no cage: unproven elements | cheapest design that passes the checks | cost | density, limit |
|---|---|---|---|
| 0 | liquid as deep as wide | $55.12 | 63 g/L, CO₂ |
| 1 | a column that strips CO₂, and dissolved oxygen held at about half of air saturation | $48.74 | 82 g/L, oxygen |
| 2 | a column that strips CO₂, 1 bar of extra pressure, and dissolved oxygen held at about half of air saturation | $42.39 | 120 g/L, oxygen |
| 4 | a column that strips CO₂, 2 bar of extra pressure, liquid as deep as wide, dissolved oxygen held at about half of air saturation, and fat taken from the feed | $38.66 | 175 g/L, oxygen |

| 1. Today's cells, with a bubble cage: unproven elements | cheapest design that passes the checks | cost | density, limit |
|---|---|---|---|
| 0 | liquid as deep as wide | $55.12 | 63 g/L, CO₂ |
| 1 | liquid as deep as wide, dissolved oxygen held at about half of air saturation, and a stirred tank with a bubble cage | $37.05 | 210 g/L, oxygen |
| 2 | a column that strips CO₂, dissolved oxygen held at about half of air saturation, and a stirred tank with a bubble cage | $36.59 | 217 g/L, oxygen |
| 3 | 1 bar of extra pressure, liquid as deep as wide, fat taken from the feed, and a stirred tank with a bubble cage | $35.53 | 258 g/L, thickness |
| 4 | a column that strips CO₂, 1 bar of extra pressure, fat taken from the feed, and a stirred tank with a bubble cage | $35.38 | 258 g/L, thickness |

| 3. Central, no cage: unproven elements | cheapest design that passes the checks | cost | density, limit |
|---|---|---|---|
| 0 | liquid as deep as wide, and dissolved oxygen held at about half of air saturation | $33.14 | 119 g/L, CO₂ |
| 1 | a column that strips CO₂, and dissolved oxygen held at about half of air saturation | $31.81 | 133 g/L, oxygen |
| 2 | a column that strips CO₂, 1 bar of extra pressure, liquid as deep as wide, and dissolved oxygen held at about half of air saturation | $29.42 | 191 g/L, oxygen |
| 3 | a column that strips CO₂, 1 bar of extra pressure, dissolved oxygen held at about half of air saturation, and fat taken from the feed | $28.96 | 196 g/L, oxygen |
| 4 | a column that strips CO₂, 2 bar of extra pressure, and liquid half as deep as wide | $28.26 | 258 g/L, thickness |
| 5 | a column that strips CO₂, 2 bar of extra pressure, liquid 0.75 times as deep as wide, and fat taken from the feed | $27.93 | 258 g/L, thickness |

| 3. Central, with a bubble cage: unproven elements | cheapest design that passes the checks | cost | density, limit |
|---|---|---|---|
| 0 | liquid as deep as wide, and dissolved oxygen held at about half of air saturation | $33.14 | 119 g/L, CO₂ |
| 1 | liquid as deep as wide, dissolved oxygen held at about half of air saturation, and a stirred tank with a bubble cage | $28.08 | 241 g/L, oxygen |
| 2 | 1 bar of extra pressure, liquid as deep as wide, and a stirred tank with a bubble cage | $27.72 | 258 g/L, thickness |
| 3 | a column that strips CO₂, 1 bar of extra pressure, and a stirred tank with a bubble cage | $27.62 | 258 g/L, thickness |

## 3. What each limit is worth

| 1. Today's cells: if this were free | cost | change | density, what then binds |
|---|---|---|---|
| the scenario as it is | $62.96 |  | 46 g/L, CO₂ |
| CO₂ removal lifted | $51.29 | −$11.67 | 70 g/L, oxygen |
| oxygen supply lifted | $62.96 |  | 46 g/L, CO₂ |
| mixing lifted | $62.96 |  | 46 g/L, CO₂ |
| every gas limit lifted (CO₂, oxygen, mixing) | $34.80 | −$28.16 | 258 g/L, thickness |
| every gas limit lifted, and the culture as thick as 320 g/L | $33.60 | −$29.36 | 320 g/L, thickness |
| medium at the least the physics allows (6.7 L/kg) | $48.14 | −$14.82 | 46 g/L, CO₂ |
| filter membranes that never wear out | $60.60 | −$2.36 | 46 g/L, CO₂ |
| no bubble protectant to buy | $61.28 | −$1.68 | 46 g/L, CO₂ |
| no growth factors to buy | $56.99 | −$5.97 | 46 g/L, CO₂ |
| no runs lost | $55.42 | −$7.55 | 46 g/L, CO₂ |
| a yeast plant with what animal cells need | $37.89 | −$25.07 | 46 g/L, CO₂ |

| 3. Central: if this were free | cost | change | density, what then binds |
|---|---|---|---|
| the scenario as it is | $29.92 |  | 177 g/L, oxygen |
| CO₂ removal lifted | $29.92 |  | 177 g/L, oxygen |
| oxygen supply lifted | $27.70 | −$2.22 | 258 g/L, thickness |
| mixing lifted | $29.92 |  | 177 g/L, oxygen |
| every gas limit lifted (CO₂, oxygen, mixing) | $27.70 | −$2.22 | 258 g/L, thickness |
| every gas limit lifted, and the culture as thick as 320 g/L | $26.75 | −$3.17 | 320 g/L, thickness |
| medium at the least the physics allows (6.4 L/kg) | $14.27 | −$15.65 | 177 g/L, oxygen |
| filter membranes that never wear out | $21.74 | −$8.19 | 177 g/L, oxygen |
| no bubble protectant to buy | $28.24 | −$1.68 | 177 g/L, oxygen |
| no growth factors to buy | $26.94 | −$2.99 | 177 g/L, oxygen |
| no runs lost | $28.64 | −$1.29 | 177 g/L, oxygen |
| a yeast plant with what animal cells need | $24.73 | −$5.20 | 177 g/L, oxygen |

| 5. Best case: if this were free | cost | change | density, what then binds |
|---|---|---|---|
| the scenario as it is | $9.71 |  | 226 g/L, oxygen |
| CO₂ removal lifted | $9.71 |  | 226 g/L, oxygen |
| oxygen supply lifted | $9.56 | −$0.14 | 258 g/L, thickness |
| mixing lifted | $9.71 |  | 226 g/L, oxygen |
| every gas limit lifted (CO₂, oxygen, mixing) | $9.56 | −$0.14 | 258 g/L, thickness |
| every gas limit lifted, and the culture as thick as 320 g/L | $9.36 | −$0.34 | 320 g/L, thickness |
| medium at the least the physics allows (5.8 L/kg) | $7.38 | −$2.33 | 226 g/L, oxygen |
| filter membranes that never wear out | $7.24 | −$2.47 | 226 g/L, oxygen |
| no bubble protectant to buy | $9.04 | −$0.67 | 226 g/L, oxygen |
| no growth factors to buy | $9.71 |  | 226 g/L, oxygen |
| no runs lost | $9.48 | −$0.23 | 226 g/L, oxygen |
| a yeast plant with what animal cells need | $8.67 | −$1.03 | 226 g/L, oxygen |

## 4. What this says

1. **The aim is reachable on paper, and it is worth little beyond rung 1.** Designs exist that leave only the thickness limit binding:
   with a bubble cage and 1 bar of pressure (2–4 unproven elements), or without a cage at 2 bar (4–5; today's cells then reach only
   175 g/L). But from rung 2 on the scenario's own design is already within $1.4–2.8 of the ideal, and the best case within $0.4.
2. **For today's cells the tank is worth $28 a kilo** ($62.96 to $34.80). A column, 1 bar of pressure and a lower oxygen setpoint give $42.39, which is $20.6 of it with two unproven elements. This is the
   case where tank design matters.
3. **A free improvement the scenarios do not use: the dissolved-oxygen setpoint.** Humbird's numbers imply the tank is held at
   0.28 mmol/L, 130% of air saturation. Holding it at about half of air saturation, as pharma does, widens the oxygen driving
   force. It is worth $0.5 in Central ($29.92 to $29.42) and $0.6 at rung 2, with nothing unproven. A decision for Pablo, because it
   would move the scenarios (TODO.md).
4. **Once the gas limits are lifted, the cost that remains is the litres of medium.** In Central, perfect gas exchange saves $2.2;
   medium at the least the physics allows saves $15.7; membranes that never wear out save $8.2. Ammonia does not limit the density
   of a perfusion tank; it sets the litres, and the litres set the medium, the growth factors and the filtering.
5. **Thicker than 258 g/L is worth about $1.** Raising the thickness limit to 320 g/L saves $0.9–1.2 in rungs 2 and 3 and $0.2 in the
   best case, because a denser culture sends more permeate through the filter.
6. **2 bar of pressure does what the cage does**, with steel instead of mesh: it reaches the thickness limit without a cage. Cells at
   3 bar absolute were not examined in the gas-exchange study; it is the top of the pressure input's range.

## 5. Limits of this search

- It searches the options the model has. Two spargers, gas exchange on the filter loop, impeller choice and membranes are not in it
  (`bioreactor_design_tricks.md`); each needs a lever first.
- "Unproven" is a count, not a probability. The odds in the research notes (column 60%, 2 bar absolute 85%) could weight it.
- The ideal lifts gas limits only. It keeps the scenario's cells, plant, losses and prices.
- The loop checks rest on one study of pH exposure (`gas_exchange_study.md` §8).
