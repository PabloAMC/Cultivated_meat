# Exploring the tank's design options: price the limits first, then search the designs

Date: 2026-11-16; regenerated 2026-11-20 on the final model (every table below is the module's output, and section 4 is
rewritten to match). Code: `design_space.py`; test: `tests/test_design_space.py`. Costs are 2025 dollars per kg of wet cells
harvested. Nothing here changes a default or a scenario. Names: the low-lactate example and the all-favourable example are
reference points defined by their cells' traits; "Published cells" are the cells as published.

**The aim** (Pablo): design the tank until CO₂, oxygen and the other compounds are no longer the bottleneck, so that only the
thickness of the culture is (258 g/L, Humbird's viscosity estimate). **The question:** how to explore the design options
efficiently.

## 1. The method

1. **Price each limit before designing anything** (`limit_prices`). For a scenario, lift each limit for free and read the cost. That
   is the most any design attacking that limit could be worth. A limit worth $0.3 a kilo needs no design work.
2. **Search the designs the model already has** (`designs`, `frontier`). Every combination of five options, 144 designs a scenario:
   the column (none, CO₂ only, with recycled oxygen), headspace pressure (0.33, 1, 2 bar), tank shape (liquid 1.6, 1.0, 0.75, 0.5
   times as deep as wide), fat in the feed, and a bubble cage. (The first version also had the dissolved-oxygen setpoint as an option;
   see point 3 of section 4.) A design is kept only if its column loop passes the pH and pass-rate checks. Each is scored by cost and
   by how many of its elements nobody has run with animal cells.
3. **Compare with the ideal** (`ideal`): the ordinary tall tank with every gas and mixing limit lifted for free (and so with almost no
   gas bubbled and almost no cells killed by bubbles). No design that keeps the scenario's feed can cost less; the gap is what is left
   to gain from the tank's gas exchange. A design that takes fat from the feed can cost less than the ideal, for cells whose lactate
   sets the medium (section 4, point 2).
4. **Only then** send the surviving designs to CFD (for the numbers that depend on geometry, `cfd_plan.md`) and to bench tests (for
   the cells).

**Each case is searched at its own tank size** (`vessel_kwargs`, 2026-11-20): 20 m³ for every case except the all-favourable example,
which takes 42 m³, the published size that costs least (`scenarios.all_favourable`). The search does not search the size of the tank;
`tank_size.md` does. The scenarios' own tank designs are a subset of this search, and the search reproduces each of them exactly.

## 2. What the search finds

| case | ordinary tank | the scenario's design | cheapest design, no cage | cheapest design, with a bubble cage | perfect gas exchange |
|---|---|---|---|---|---|
| Published cells, in perfusion | $205.78 (46 g/L, CO₂) | $185.59 | $129.40 (142 g/L, oxygen; 4 unproven) | $123.53 (258 g/L, thickness; 5 unproven) | **$167.45** (258 g/L) |
| 4. Low-lactate example | $55.21 (87 g/L, CO₂) | $49.50 | $47.39 (207 g/L, oxygen; 4 unproven) | $46.26 (258 g/L, thickness; 4 unproven) | **$42.97** (258 g/L) |
| 5. Shared-medium plant | $47.69 (87 g/L, CO₂) | $45.04 | $43.99 (207 g/L, oxygen; 4 unproven) | $43.41 (258 g/L, thickness; 4 unproven) | **$40.35** (258 g/L) |
| 6. Cells that make almost no ammonia or lactate | $30.29 (87 g/L, CO₂) | $27.75 | $23.76 (207 g/L, oxygen; 4 unproven) | $23.22 (258 g/L, thickness; 5 unproven) | **$24.23** (258 g/L) |
| 7. All-favourable example | $10.85 (75 g/L, CO₂) | $7.62 | $7.01 (208 g/L, oxygen; 5 unproven) | $6.18 (320 g/L, thickness; 6 unproven) | **$5.59** (320 g/L) |

"Unproven" counts elements nobody has run with animal cells: the column (1; 2 with recycled oxygen), 1 bar of extra pressure (1; 2
bar counts 2), a tank squatter than those in use (1), fat taken from the feed (1), the bubble cage (1). A tank as deep as wide is
standard practice and counts 0. **The cage's three numbers are judgements** (`vm_cage_*`), so its column is shown apart.

The cheapest design for each number of unproven elements:

| Published cells, in perfusion, no cage: unproven elements | cheapest design that passes the checks | cost | density, limit |
|---|---|---|---|
| 0 | liquid as deep as wide | $200.95 | 63 g/L, CO₂ |
| 1 | liquid as deep as wide, and fat taken from the feed | $145.44 | 71 g/L, oxygen |
| 2 | a column that strips CO₂, and fat taken from the feed | $141.19 | 73 g/L, oxygen |
| 3 | a column that strips CO₂, 1 bar of extra pressure, and fat taken from the feed | $134.31 | 103 g/L, oxygen |
| 4 | a column that strips CO₂, 2 bar of extra pressure, and fat taken from the feed | $129.40 | 142 g/L, oxygen |

| Published cells, in perfusion, with a bubble cage: unproven elements | cheapest design that passes the checks | cost | density, limit |
|---|---|---|---|
| 0 | liquid as deep as wide | $200.95 | 63 g/L, CO₂ |
| 1 | liquid as deep as wide, and fat taken from the feed | $145.44 | 71 g/L, oxygen |
| 2 | fat taken from the feed, and a stirred tank with a bubble cage | $127.48 | 167 g/L, oxygen |
| 3 | 1 bar of extra pressure, fat taken from the feed, and a stirred tank with a bubble cage | $125.72 | 197 g/L, CO₂ |
| 4 | a column that strips CO₂ and feeds recycled oxygen, fat taken from the feed, and a stirred tank with a bubble cage | $123.79 | 254 g/L, mixing |
| 5 | a column that strips CO₂, 2 bar of extra pressure, fat taken from the feed, and a stirred tank with a bubble cage | $123.53 | 258 g/L, thickness |

| 4. Low-lactate example, no cage: unproven elements | cheapest design that passes the checks | cost | density, limit |
|---|---|---|---|
| 0 | liquid as deep as wide | $54.91 | 108 g/L, oxygen |
| 1 | a column that strips CO₂ | $52.47 | 112 g/L, oxygen |
| 2 | a column that strips CO₂, and 1 bar of extra pressure | $49.50 | 154 g/L, oxygen |
| 4 | a column that strips CO₂, 2 bar of extra pressure, and fat taken from the feed | $47.39 | 207 g/L, oxygen |

| 4. Low-lactate example, with a bubble cage: unproven elements | cheapest design that passes the checks | cost | density, limit |
|---|---|---|---|
| 0 | liquid as deep as wide | $54.91 | 108 g/L, oxygen |
| 1 | a stirred tank with a bubble cage | $48.07 | 186 g/L, oxygen |
| 2 | 1 bar of extra pressure, and a stirred tank with a bubble cage | $47.87 | 191 g/L, CO₂ |
| 3 | a column that strips CO₂, 1 bar of extra pressure, and a stirred tank with a bubble cage | $46.51 | 246 g/L, oxygen |
| 4 | a column that strips CO₂, 2 bar of extra pressure, and a stirred tank with a bubble cage | $46.26 | 258 g/L, thickness |

## 3. What each limit is worth

| Published cells, in perfusion: if this were free | cost | change | density, what then binds |
|---|---|---|---|
| the scenario as it is | $185.59 |  | 103 g/L, oxygen |
| CO₂ removal lifted | $185.59 |  | 103 g/L, oxygen |
| oxygen supply lifted | $174.14 | −$11.45 | 258 g/L, thickness |
| mixing lifted | $185.59 |  | 103 g/L, oxygen |
| every gas limit lifted (CO₂, oxygen, mixing) | $167.72 | −$17.87 | 258 g/L, thickness |
| every gas limit lifted, and the culture as thick as 320 g/L | $166.62 | −$18.97 | 320 g/L, thickness |
| medium at the least the physics allows (6.7 L/kg; this thin culture needs 10.4, what leaves with the cells) | $31.30 | −$154.29 | 103 g/L, oxygen |
| filter membranes that never wear out | $89.88 | −$95.71 | 103 g/L, oxygen |
| no bubble protectant to buy | $176.82 | −$8.77 | 103 g/L, oxygen |
| no growth factors to buy | $185.59 |  | 103 g/L, oxygen |
| no runs lost | $165.56 | −$20.03 | 103 g/L, oxygen |
| a yeast plant with what animal cells need | $171.18 | −$14.41 | 103 g/L, oxygen |

| 4. Low-lactate example: if this were free | cost | change | density, what then binds |
|---|---|---|---|
| the scenario as it is | $49.50 |  | 154 g/L, oxygen |
| CO₂ removal lifted | $49.50 |  | 154 g/L, oxygen |
| oxygen supply lifted | $46.12 | −$3.38 | 258 g/L, thickness |
| mixing lifted | $49.50 |  | 154 g/L, oxygen |
| every gas limit lifted (CO₂, oxygen, mixing) | $43.20 | −$6.30 | 258 g/L, thickness |
| every gas limit lifted, and the culture as thick as 320 g/L | $42.44 | −$7.05 | 320 g/L, thickness |
| medium at the least the physics allows (6.4 L/kg; this thin culture needs 7.2, what leaves with the cells) | $17.93 | −$31.56 | 154 g/L, oxygen |
| filter membranes that never wear out | $27.22 | −$22.28 | 154 g/L, oxygen |
| no bubble protectant to buy | $47.17 | −$2.33 | 154 g/L, oxygen |
| no growth factors to buy | $49.50 |  | 154 g/L, oxygen |
| no runs lost | $44.35 | −$5.15 | 154 g/L, oxygen |
| a yeast plant with what animal cells need | $42.50 | −$7.00 | 154 g/L, oxygen |

| 7. All-favourable example: if this were free | cost | change | density, what then binds |
|---|---|---|---|
| the scenario as it is | $7.62 |  | 155 g/L, oxygen |
| CO₂ removal lifted | $7.62 |  | 155 g/L, oxygen |
| oxygen supply lifted | $5.98 | −$1.64 | 320 g/L, thickness |
| mixing lifted | $7.62 |  | 155 g/L, oxygen |
| every gas limit lifted (CO₂, oxygen, mixing) | $5.73 | −$1.89 | 320 g/L, thickness |
| every gas limit lifted, and the culture as thick as 320 g/L | $5.73 | −$1.89 | 320 g/L, thickness |
| medium at the least the physics allows (5.5 L/kg; this thin culture needs 7.0, what leaves with the cells) | $7.01 | −$0.61 | 155 g/L, oxygen |
| filter membranes that never wear out | $7.58 | −$0.04 | 155 g/L, oxygen |
| no bubble protectant to buy | $6.92 | −$0.70 | 155 g/L, oxygen |
| no growth factors to buy | $7.62 |  | 155 g/L, oxygen |
| no runs lost | $7.62 |  | 155 g/L, oxygen |
| a yeast plant with what animal cells need | $6.76 | −$0.86 | 155 g/L, oxygen |

## 4. What this says

Rung numbers are the ladder's (4: the low-lactate example; 5: plus a plant with shared medium; 6: plus cells that make almost no
ammonia or lactate; 7: the all-favourable example).

1. **The aim is reachable on paper only with a cage, and it is worth a few dollars a kilo.** With every gas limit lifted only the
   thickness binds, and the low-lactate example costs $42.97 against $49.50 with the scenario's own design: $6.5 a kilo. The gap is
   $4.7 at rung 5, $3.5 at rung 6 and $2.0 in the all-favourable example. Part of the gap is the cells bubbles kill: 8.0% of the cells
   grown in the low-lactate example's design, 1.9% when oxygen and CO₂ are supplied some other way.
   **Without a cage no case reaches the thickness limit.** The cheapest design without a cage is the column, 2 bar and fat from the
   feed in an ordinary tall tank in the low-lactate example ($47.39 at 207 g/L, held by oxygen); rungs 5 and 6 stop at the same
   207 g/L, and the all-favourable example at 208 g/L. With a cage every case reaches the thickness limit, with 4 to 6 unproven
   elements.
2. **For the published cells gas exchange is worth $38 a kilo, and it is not what matters most.** Perfect gas exchange takes them
   from $205.78 to $167.45, about a fifth of the cost. A column and 1 bar of pressure give $185.59, which is $20.2 of it with two
   unproven elements. What sets their cost is the medium. These cells turn so much glucose into lactate that washing the lactate out
   at 35 mmol/L takes 146 litres per kilo harvested, and no tank design changes that.
   **Fat taken from the feed is the largest single option for these cells.** It takes the ordinary tank from $205.78 to $146.83. Fed
   fat replaces glucose the cells would turn into fat, so they make 3.3 mol of lactate a kilo instead of 4.8, and need 101 litres of
   medium instead of 146. That is why the cheapest design without a cage ($129.40) costs less than "perfect gas exchange" ($167.45):
   the ideal keeps the scenario's feed. With fat fed and every gas limit lifted the same tank costs $118.56, and no fat-fed design
   costs less than that.
   **The same holds at rung 6.** Lactate, not ammonia, sets the litres of the cells that make almost no ammonia or lactate (21.1 L
   per kilo harvested, at 35 mmol/L tolerated), so the cheapest designs ($23.22 with a cage, $23.76 without) cost less than the
   scenario-feed ideal ($24.23); with fat fed and every gas limit lifted the tank costs $21.49. In rungs 4 and 5 ammonia sets the
   medium. The all-favourable example takes Humbird's 50 mmol/L of lactate tolerated, so ammonia sets its medium too (11.7 L per kilo
   harvested). In those three no design costs less than the ideal. This result rests on two things nobody has measured: how much fed
   fat displaces, and that the cells keep the same lactate per mol of glucose when they take up less. It is the least certain number
   in this note.
3. **A free improvement, adopted on 2026-11-16: the dissolved-oxygen setpoint.** Humbird's numbers imply the tank is held at 0.28
   mmol/L, 130% of air saturation. Holding it at about half of air saturation, as pharma does, widens the oxygen driving force and
   needs nothing unproven. The first run of this search found it worth $0.5 in the low-lactate example ($29.92 to $29.42, on the model
   of 2026-11-16), and unused by the scenarios. Every scenario now carries it (`scenarios.always`, input `sc_do_setpoint`); the tables
   here include it.
4. **The litres of medium are still the largest cost.** In the low-lactate example, every gas limit lifted saves $6.3; medium at the
   least the physics allows saves $31.6; membranes that never wear out save $22.3. Ammonia does not limit the density of a perfusion
   tank; it sets the litres, and the litres set the medium, its preparation equipment and the filtering. For the published cells
   lactate sets the litres, and the same two rows save $154.3 and $95.7, against $17.9 for every gas limit lifted. "No runs lost" is
   worth $5.2 in the low-lactate example. (Growth factors are inside the complete medium's price, so "no growth factors to buy" saves
   nothing in any case shown.) In the all-favourable example no single row saves more than $1.9: its medium is at the nutrient floor,
   its membranes are dialyser-grade and it loses no runs.
5. **Thicker than 258 g/L is worth under $1.** Raising the thickness limit to 320 g/L saves $0.8 in the low-lactate example once the
   gas limits are lifted. The all-favourable example already takes 320 g/L.
6. **2 bar of pressure alone does not do what the cage does.** Without a cage the 2 bar designs stop at about 140 to 210 g/L, held
   by oxygen (point 1). Cells at 3 bar absolute were not examined in the gas-exchange study; it is the top of the pressure input's
   range.
7. **The cage.** A caged tank bubbles softly in the ring where the cells are and hard inside the mesh cylinder, where there are none.
   Since 2026-11-20 the cylinder's gas exchanges oxygen and CO₂ but is not charged for killing cells (`vessels.explore_kwargs` passes
   it as `gas_away`; before, it was charged, and the cage rows were overstated). A cage alone in an ordinary tall tank is the
   cheapest one-element design in the low-lactate example ($48.07 at 186 g/L, against $52.47 for the column alone). The cage's three
   inputs are judgements.

## 5. Limits of this search

- It searches the options the model has. Two spargers, gas exchange on the filter loop, impeller choice and membranes are not in it
  (`bioreactor_design_tricks.md`); each needs a lever first.
- It does not search the size of the tank: each case is searched at its own size (section 1).
- "Unproven" is a count, not a probability.
- The ideal lifts gas limits only. It keeps the scenario's cells, feed, plant, losses and prices. So it does not bound a design
  that changes the feed (fat taken from the feed).
- The loop checks rest on one study of pH exposure (`gas_exchange_study.md` §8). A design whose loop fails at full density is dropped;
  running it thinner might pass (the vessel grid now does this, `vessels._thinned`; the search does not yet).
