# Tank size: is 20 m³ the right size?

Research date: 2026-11-15. Code: `tank_size.py` (`size_scan`, `summary`, `what_ifs`, `flatter`), `tests/test_tank_size.py`. Costs are 2025 dollars per kg of wet
cells. Every scenario uses a 20 m³ stirred tank in perfusion with a TFF filter loop. No default, scenario or pinned number moves: the scan calls
`floor_physics.explore(vessel_m3=...)` and adds no physics.

## 1. The answer

**Yes, for cost: 20 m³ is within 0.4% to 2.3% of the cheapest size in every scenario, and the curve is flat.** Another size saves $0.09 to $0.89 a kilo.
**Yes, for risk: no animal cells have run above about 25 m³.**

| Scenario | Cost at 20 m³ | Cheapest size the model finds | Cost there | Saving | Sizes within 1% of the minimum |
|---|---|---|---|---|---|
| Best | $8.95 | 55 m³ | $8.82 | $0.13 (1.5%) | 23 to 55 m³ |
| Central | $26.64 | 23 m³ | $26.50 | $0.14 (0.5%) | 18 to 34 m³ |
| Central, food-grade plant with shared medium | $24.34 | 34 m³ | $24.25 | $0.09 (0.4%) | 16 to 34 m³ |
| Cautious | $38.97 | 46 m³ | $38.08 | $0.89 (2.3%) | 26 to 104 m³ |
| Reference (Humbird's tank, no tricks) | $11.84 | 14 m³ | $11.78 | $0.06 (0.5%) | 9 to 23 m³ |

- **Smaller tanks cost more, and the penalty grows fast below 10 m³.** At 10 m³ a kilo costs 2% to 4% more (best $9.27, central $27.35, cautious $40.69). At 5 m³ it
  costs 6% to 16% more. At 2 m³ it costs 20% to 50% more.
- **Larger tanks save little because the loop checks rule out the tricks, not because gas transfer fails.** Without the checks, the cheapest design holds the culture at 258 g/L (238 g/L for
  the best case at 50 m³) up to 200 m³, and the best case would save 3.4% at 200 m³, the central case 2.7%. The pH check on the column loop rules those designs out above about 23 to
  26 m³. Relaxing it to twice the safe dose moves the limit to 34 m³ (best, central) and 95 m³ (cautious).
- **The model's one assumption that would move the answer is labour.** It charges the same crew per m³ at every size. If staff per m³ fell with tank size as they do between
  Humbird's 2 m³ and 20 m³ plants, the best case would be 7.6% cheaper at 200 m³. Section 5 says why that is an upper bound.
- **Only the cautious scenario gains more than 2%.** Its saving rests on the same pH check: with it, 46 m³ is cheapest; without it, 67 m³ saves 2.8%.

## 2. How the scan works

For each case and size, the scan tries every pair of tank tricks (none, column, column and 1 bar extra pressure, column and pressure and recycled oxygen) and tank shape
(liquid 1.6, 1.0, 0.75 or 0.5 times as deep as wide). That is 16 designs, as `scenarios.design` tries at 20 m³. It keeps the cheapest design whose column loop
- is pH-safe: its alkaline dose is at most 1.0 times that of the design judged safe (55 mbar out, 0.5 m³ of loop in a 20 m³ tank), and
- runs at a pass rate dense cultures have taken: at most `ge_passes_tested` (15) tank volumes an hour.

At 20 m³ the scan returns each scenario's own design and cost (the test checks this). Everything else about the scenario is held fixed. The reference case is
shown twice: as defined (Humbird's tall tank, no tricks) and with the design chosen again.

Two things set what a design costs at a size. The bioreactor share of the plant (32%) gets cheaper per m³ with size (Humbird's vessel cost, `capex_at_size`): the
per-m³ price is 2.7 times the 20 m³ price at 5 m³ and 0.49 times at 200 m³. And a deeper tank clears less CO₂ and mixes more slowly, so each trick has a size above which it
no longer lifts the limit.

## 3. Cost against size, and what binds

"Capital" is the tank, plant and column. "Loop" is the retention loop's hardware. "Medium" is feed plus growth factors. "Other" is utilities, other consumables and bought oxygen.
"Density limit" is the cap that sets the culture's density. "Loop checks cost" is what the pH or pass check adds against the cheapest design that fails it.

#### Best

| m³ | design | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit | loop checks cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | column + 1 bar, tall 1.6 | **11.55** | 4.66 | 0.06 | 0.61 | 2.67 | 1.72 | 1.83 | 258 | thickness | none |
| 5 | column + 1 bar, square 1.0 | **9.76** | 2.87 | 0.06 | 0.61 | 2.67 | 1.72 | 1.83 | 258 | thickness | none |
| 10 | column + 1 bar, square 1.0 | **9.27** | 2.38 | 0.06 | 0.61 | 2.67 | 1.72 | 1.83 | 258 | thickness | $0.06 (pH) |
| 20 | column + 1 bar, squat 0.75 | **8.95** | 2.06 | 0.06 | 0.61 | 2.67 | 1.72 | 1.84 | 258 | thickness | $0.13 (pH) |
| 50 | column + 1 bar, flat 0.5 | **8.83** | 1.94 | 0.06 | 0.61 | 2.67 | 1.72 | 1.84 | 258 | thickness | $0.20 (pH) |
| 100 | column, flat 0.5 | **9.07** | 2.45 | 0.05 | 0.81 | 2.20 | 1.72 | 1.84 | 195 | oxygen supply | $0.50 (pH) |
| 200 | column, flat 0.5 | **9.03** | 2.41 | 0.05 | 0.81 | 2.20 | 1.72 | 1.84 | 195 | oxygen supply | $0.50 (pH) |

#### Central

| m³ | design | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit | loop checks cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | column + 1 bar + O₂, tall 1.6 | **34.78** | 14.25 | 0.21 | 0.97 | 8.83 | 8.71 | 1.80 | 258 | thickness | none |
| 5 | column + 1 bar + O₂, square 1.0 | **29.18** | 8.66 | 0.21 | 0.97 | 8.83 | 8.71 | 1.80 | 258 | thickness | $0.25 (pH) |
| 10 | column + 1 bar + O₂, squat 0.75 | **27.35** | 6.82 | 0.21 | 0.97 | 8.83 | 8.71 | 1.81 | 258 | thickness | $0.41 (pH) |
| 20 | column + 1 bar + O₂, flat 0.5 | **26.64** | 6.11 | 0.21 | 0.97 | 8.83 | 8.71 | 1.80 | 258 | thickness | $0.71 (pH) |
| 50 | column, square 1.0 | **28.35** | 8.22 | 0.19 | 1.64 | 7.85 | 8.71 | 1.74 | 153 | oxygen supply | $3.05 (pH) |
| 100 | column, squat 0.75 | **28.34** | 8.21 | 0.19 | 1.64 | 7.85 | 8.71 | 1.74 | 153 | oxygen supply | $3.01 (pH) |
| 200 | column, flat 0.5 | **28.80** | 8.67 | 0.19 | 1.64 | 7.85 | 8.71 | 1.74 | 153 | oxygen supply | $3.58 (pH) |

#### Central, food-grade plant with shared medium

| m³ | design | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit | loop checks cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | column + 1 bar, square 1.0 | **29.17** | 8.43 | 0.21 | 1.06 | 8.70 | 8.71 | 2.06 | 236 | oxygen supply | none |
| 5 | column + 1 bar + O₂, square 1.0 | **25.89** | 5.03 | 0.21 | 0.97 | 8.83 | 8.71 | 2.13 | 258 | thickness | $0.08 (pH) |
| 10 | column + 1 bar + O₂, squat 0.75 | **24.79** | 3.93 | 0.21 | 0.97 | 8.83 | 8.71 | 2.14 | 258 | thickness | $0.16 (pH) |
| 20 | column + 1 bar + O₂, flat 0.5 | **24.34** | 3.48 | 0.21 | 0.97 | 8.83 | 8.71 | 2.13 | 258 | thickness | $0.32 (pH) |
| 50 | column, square 1.0 | **25.11** | 4.65 | 0.19 | 1.64 | 7.85 | 8.71 | 2.07 | 153 | oxygen supply | $1.47 (pH) |
| 100 | column, squat 0.75 | **25.07** | 4.62 | 0.19 | 1.64 | 7.85 | 8.71 | 2.07 | 153 | oxygen supply | $1.45 (pH) |
| 200 | column, flat 0.5 | **25.32** | 4.86 | 0.19 | 1.64 | 7.85 | 8.71 | 2.07 | 153 | oxygen supply | $1.76 (pH) |

#### Cautious

| m³ | design | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit | loop checks cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | column + 1 bar, tall 1.6 | **58.43** | 31.89 | 0.20 | 2.18 | 7.73 | 14.60 | 1.84 | 145 | oxygen supply | $12.85 (pH) |
| 5 | column + 1 bar, tall 1.6 | **45.20** | 18.66 | 0.20 | 2.18 | 7.73 | 14.60 | 1.84 | 145 | oxygen supply | $7.36 (pH) |
| 10 | column + 1 bar, tall 1.6 | **40.69** | 14.15 | 0.20 | 2.18 | 7.73 | 14.60 | 1.84 | 145 | oxygen supply | $5.49 (pH) |
| 20 | column + 1 bar, square 1.0 | **38.97** | 12.43 | 0.20 | 2.18 | 7.73 | 14.60 | 1.84 | 145 | oxygen supply | $5.11 (pH) |
| 50 | column + 1 bar, flat 0.5 | **38.80** | 12.26 | 0.20 | 2.18 | 7.73 | 14.60 | 1.84 | 145 | oxygen supply | $5.75 (pH) |
| 100 | column + 1 bar, flat 0.5 | **38.33** | 11.79 | 0.20 | 2.18 | 7.73 | 14.60 | 1.84 | 145 | oxygen supply | $5.28 (pH) |
| 200 | column, tall 1.6 | **41.24** | 14.92 | 0.16 | 3.38 | 6.34 | 14.60 | 1.84 | 94 | oxygen supply | $8.30 (pH) |

#### Reference, tank design chosen again

| m³ | design | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit | loop checks cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | column + 1 bar, tall 1.6 | **14.28** | 7.78 | 0.06 | 0.57 | 2.67 | 1.70 | 1.50 | 258 | thickness | none |
| 5 | column + 1 bar, square 1.0 | **11.28** | 4.79 | 0.06 | 0.57 | 2.67 | 1.70 | 1.50 | 258 | thickness | none |
| 10 | column + 1 bar, square 1.0 | **10.33** | 3.83 | 0.06 | 0.57 | 2.67 | 1.70 | 1.50 | 258 | thickness | $0.13 (pH) |
| 20 | column + 1 bar, squat 0.75 | **9.85** | 3.35 | 0.06 | 0.57 | 2.67 | 1.70 | 1.51 | 258 | thickness | $0.25 (pH) |
| 50 | column + 1 bar, flat 0.5 | **9.69** | 3.19 | 0.06 | 0.57 | 2.67 | 1.70 | 1.51 | 258 | thickness | $0.31 (pH) |
| 100 | column, flat 0.5 | **10.26** | 4.05 | 0.05 | 0.75 | 2.20 | 1.70 | 1.51 | 195 | oxygen supply | $1.02 (pH) |
| 200 | column, flat 0.5 | **10.20** | 3.99 | 0.05 | 0.75 | 2.20 | 1.70 | 1.51 | 195 | oxygen supply | $1.02 (pH) |

#### Reference as defined (Humbird's tall tank, no tricks)

| m³ | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 16.52 | 10.32 | 0.05 | 0.75 | 2.20 | 1.70 | 1.50 | 195 | oxygen supply |
| 5 | 12.37 | 6.18 | 0.05 | 0.77 | 2.16 | 1.70 | 1.50 | 190 | CO₂ removal |
| 10 | 11.83 | 5.96 | 0.04 | 0.97 | 1.66 | 1.70 | 1.50 | 151 | CO₂ removal |
| 20 | 11.84 | 6.36 | 0.02 | 1.22 | 1.04 | 1.70 | 1.50 | 120 | CO₂ removal |
| 50 | 12.55 | 7.70 | 0.00 | 1.65 | 0.00 | 1.70 | 1.50 | 88 | CO₂ removal |
| 100 | 14.59 | 9.30 | 0.00 | 2.08 | 0.00 | 1.70 | 1.50 | 70 | CO₂ removal |
| 200 | 17.30 | 11.47 | 0.00 | 2.62 | 0.00 | 1.70 | 1.50 | 56 | CO₂ removal |

### What binds at each size

- **2 to 10 m³: capital.** A small tank costs more per m³. Capital per kilo falls from $4.66 at 2 m³ to $2.38 at 10 m³ in the best case. The tricks lift every gas limit, so the culture sits at
  the 258 g/L thickness cap. The loop check does not bind at 2 m³ and costs under $0.50 at 5 to 10 m³ in the best and central cases.
- **20 m³: the pH check.** The check already costs $0.13 (best), $0.71 (central) and $5.11 (cautious): a cheaper design exists (a taller tank, or the oxygen trick in the cautious case) and
  fails the pH check. The culture still sits at 258 g/L (best, central) or 145 g/L (cautious, set by oxygen supply because it runs at 2 mm/s of gas).
- **50 m³ and above: the pH check, then oxygen supply.** A deeper tank clears less CO₂ through the sparger, so the loop must make more passes, and the alkaline dose rises with
  the passes. The 20 m³ designs fail the check at 23 to 26 m³. Above that, the cheapest passing design drops the oxygen trick, so the sparger supplies the oxygen and
  the density falls to 153 g/L (central) or 195 g/L (best, reference). The loop checks cost $3.05 to $3.58 a kilo in the central case at 50 to 200 m³.
  The best case holds 258 g/L to 55 m³ because its sparger runs at 6 mm/s: it clears more CO₂ without the loop, so the loop needs fewer passes.
- **Mixing never binds** in a chosen design: a flat tank mixes fast. In the reference case as defined (tall tank, no tricks), CO₂ removal binds from 5 m³ up and the culture thins from
  190 g/L to 56 g/L. That is why the reference's own cost curve turns up above 14 m³.
- **Heat is not modelled.** The cells give off 5 kW per m³ of culture at 258 g/L (best, central) and 2.5 kW/m³ at 145 g/L (cautious). The wall of a squat tank of 200 m³ has
  1.4 m² per m³, so a jacket alone must take 2.0 to 2.7 kW/m² (central, best) against 1.6 to 1.8 kW/m² at 20 m³. That is near the top of what a jacket removes
  (my estimate, 1 to 5 kW/m², low confidence). An external heat exchanger on the column loop would take the rest; its cost is not in the model.

## 4. The retention loop and size

The TFF loop is sized on permeate per m³ of tank (`floor_physics.explore`, `retention.py`): permeate per kilo is the medium per kilo less what the bleed of cells carries out
(1000 / density); membrane area per m³ is that permeate times the harvest rate per m³, divided by the flux (5 L/m²/h); hardware is $1k per m² times 1.84 for installation; membranes cost $1,450 per
m² and last 3,960 litres.

**What this does at each size.** The area per m³ of tank, and so the loop's cost per kilo, is the same at every size for the same density and medium (the test checks it). The loop is not what
decides the size.

| | Best, 20 m³ | Best, 200 m³ | Central, 20 m³ | Central, 200 m³ |
|---|---|---|---|---|
| Membrane area | 172 m² | 1,073 m² | 375 m² | 1,972 m² |
| ATF-10 equivalents (11 m² each) | 16 | 98 | 34 | 179 |
| Loop hardware, $/kg | 0.06 | 0.05 | 0.21 | 0.19 |
| Membranes, $/kg | 2.67 | 2.20 | 8.83 | 7.85 |
| Membranes, share of the cost | 30% | 24% | 33% | 27% |

**Assumptions in the sizing that favour or penalise a size:**
1. *Hardware per m² does not fall with size.* A big skid costs less per m² than a small one. That penalises large tanks. The what-if (`ts_loop_hw_exp` = 0.3, hardware as V^0.7) changes the best
   optimum from 1.5% to 1.6% and the central from 0.5% to 0.6%. The hardware is under 1% of the cost, so this barely matters.
2. *Membranes cost the same per litre at every size.* They are 24% to 33% of the cost, and they set the loop's cost. They fall at large sizes only because the thinner culture needs less
   permeate per kilo ($8.83 to $7.85 in the central case). The price per m² would fall with a bigger order, but that has nothing to do with tank size.
3. *Flux is 5 L/m²/h whatever the density.* A thinner culture at large size would hold a higher flux. That favours large tanks slightly, through hardware only, so the effect is under $0.05 a kilo.
4. *No unit rounding.* A 2 m³ tank needs 1 to 3 ATF-10 units' worth of membrane; the model charges the fraction. That flatters the smallest tanks by a few cents.
5. *Not charged at any size:* pumping power for the loop, labour and downtime to change membranes (a full set per 33-day run, so 74 to 179 ATF-10 equivalents at 200 m³), sterile connections, and the time culture spends in
   the loop outside the tank. The column loop has a pH and a pass check; the TFF loop pumps the whole culture through fibres and has none. All of these grow with area, so they would penalise
   large tanks, but nothing in the repo prices them.
6. *In the reference case as defined, the model charges no loop at 50 m³ and above.* The bleed at 88, 70 and 56 g/L carries 11.3, 14.3 and 18.0 litres of liquid a kilo, at least the 11.2 litres of
   medium the cells need, so permeate is zero. But the medium bought is 11.2 litres a kilo (the feed floor of $1.70 holds), not the 14.3 or 18.0 the bleed removes. At 100 and 200 m³ the reference is
   low by $0.44 and $0.99 a kilo; at 50 m³ it is right. This affects only the reference as defined. In every scenario design the medium exceeds what the bleed removes.

## 5. Other assumptions that favour or penalise a size

The plant model scales only the bioreactor share with size. The rest (buildings, utilities, seed trains) is priced per m³ at its 20 m³ value.

| Assumption | Effect | Direction |
|---|---|---|
| Labour: the same crew per m³ at every size | Humbird's two plants (95 staff for 24 × 20 m³, 132 for 96 × 2 m³) give crew per m³ ∝ (tank size)^-0.54. Extrapolated to 200 m³ it cuts labour by 71%. | Penalises large tanks, rewards small tanks. The exponent comes from two sizes at or below 20 m³; above 20 m³ it is an extrapolation. |
| The chance of losing a run per tank-day is the same at every size | A bigger tank has more ports and seals and loses a whole tankful. BioPlan's survey found larger facilities had about 3 times the contamination of smaller ones (facilities, not tanks). | Flatters large tanks. |
| Seed train and restart time are the same at every size | A 200 m³ tank needs about 3 more doublings of seed than a 20 m³ tank. | Flatters large tanks. |
| Shape: a squat tank mixes faster, by Humbird's Eq. 2.18 (t_m ∝ T^(2/3) (H/T)^2.5) | Used below its fitted range (H/T from 1.6). Wide flat tanks (7 m across at 200 m³) need several impellers. | Flatters large flat tanks. |
| Gas speed through the surface is fixed (the model's rule) | `gas_exchange_study.md` section 2.3 reads the bubble-damage evidence as gas per litre, not per surface: then a deeper tank can pass faster gas (up to 13 mm/s at 200 m³, a speed whose foam nobody has measured). | Penalises large tanks. |

The what-ifs below change one at a time and report the cheapest size and the saving against 20 m³. Each is zero at 20 m³ by construction (the test checks it).

| What-if | Best | Central | Central, shared medium | Cautious | Reference, redesigned |
|---|---|---|---|---|---|
| As modelled | 55 m³, 1.5% | 23 m³, 0.5% | 34 m³, 0.4% | 46 m³, 2.3% | 55 m³, 1.8% |
| No loop checks (physics only) | 200 m³, 3.4% | 200 m³, 2.7% | 76 m³, 1.9% | 67 m³, 2.8% | 200 m³, 4.4% |
| pH check relaxed to twice the safe dose | 78 m³, 1.9% | 34 m³, 1.6% | 34 m³, 1.0% | 93 m³, 3.4% | 34 m³, 2.5% |
| Pass limit at the top of its range (24 an hour) | 55 m³, 1.5% | 23 m³, 0.5% | 34 m³, 0.4% | 46 m³, 2.3% | 55 m³, 1.8% |
| Labour follows Humbird's crew rule | 200 m³, 7.6% | 34 m³, 1.2% | 163 m³, 1.9% | 104 m³, 5.0% | 55 m³, 4.2% |
| Loop hardware has economies of scale | 55 m³, 1.6% | 23 m³, 0.6% | 34 m³, 0.5% | 46 m³, 2.4% | 55 m³, 2.0% |
| Chance of losing a run grows with size (V^0.33) | 25 m³, 0.6% | 23 m³, 0.3% | 23 m³, 0.2% | 26 m³, 0.8% | 55 m³, 1.8% |
| Gas per litre held at its 20 m³ value | 200 m³, 4.2% | 200 m³, 3.9% | 200 m³, 2.8% | 51 m³, 7.2% | 200 m³, 5.8% |
| Favourable to large tanks (pH check relaxed, crew rule, loop economies) | 200 m³, 7.7% | 53 m³, 2.9% | 200 m³, 3.4% | 168 m³, 6.9% | 78 m³, 5.7% |

- **The pass limit never binds first.** The pH check fails before the pass count reaches 15.
- **The crew rule is the largest single effect, and the least supported above 20 m³.** It would put the best case at 200 m³ and 7.6% cheaper. No source gives crew against tank size above 20 m³.
- **A chance of loss that grows with size removes the large-tank gain.** At V^0.33 the best case's optimum drops to 25 m³ and 0.6%.
- **Even the most favourable mix saves under 3% for the central case.** The best and cautious cases save 7%, at 200 m³ and 168 m³, sizes nobody has run with animal cells.
- **A flatter tank does not help much.** At 50 m³ the central case with the liquid 0.3 times as deep as wide (5.5 m across, 1.7 m deep) passes the check with the oxygen trick for $26.60,
  the same as at 20 m³ ($26.64). At 100 m³ it needs 0.2 and costs $27.08. At 200 m³ the best aspect (0.2) gives $27.52. So flatter tanks hold the cost flat out to 50 m³ and add 2% at 100 m³ and
  3% at 200 m³ (`tank_size.flatter`). The scenarios do not offer these shapes, and nobody has built a tank this wide for cells.

## 6. The largest size at which each design passes

| Scenario | The 20 m³ design | Its limit with the model's checks | Limit with the pH check at twice the safe dose | Largest size that keeps the 20 m³ density, with the design chosen again |
|---|---|---|---|---|
| Best | column + 1 bar, squat | 24.8 m³ | 34.7 m³ | 54.6 m³ |
| Central | column + 1 bar + O₂, flat | 23.3 m³ | 34.1 m³ | 23.2 m³ |
| Central, shared medium | column + 1 bar + O₂, flat | 23.3 m³ | 34.1 m³ | 23.2 m³ |
| Cautious | column + 1 bar, square | 26.3 m³ | 94.5 m³ | 104.5 m³ |

- **The limit sits 17% to 31% above 20 m³.** A design fails when its pH dose passes 1.0 times the safe dose. At 20 m³ the dose is 0.81 (best), 0.88 (central) and 0.94 (cautious).
  So each 20 m³ design already runs at 81% to 94% of the check, and 20 m³ is close to the largest size those designs allow.
- **A re-chosen design holds 258 g/L (best) to 55 m³, and the central case to 23 m³.** Above that, the central case drops to 153 g/L and costs $1.85 a kilo more at 50 m³ ($28.35) than at 23 m³ ($26.50).
- **The check is a judgement, not a physical limit.** The safe dose is 0.29 of the dose that slowed CHO cells (Paul et al. 2020, via a summary in `gas_exchange_study.md` section 8): one study, and a measure
  (rise × share) the study did not use. At 3.4 times the safe dose the loop would reach that harm. Between 1.0 and 3.4 nothing is measured.

## 7. How likely is each size?

These are judgement, built from the notes cited. They are not a forecast.

**Sources of evidence.** Animal cells have run in a stirred tank at 25 m³ (pharma fed-batch, `Continuous harvest bioreactor progress/biopharma_continuous_culture.md`), at 21 m³ (insect cells,
`floor_physics.SPECIES_PRESETS`, Ashizawa 2022) and at 20 m³ for food (Vow; `Continuous harvest bioreactor progress/cultivated_meat_reactor_progress.md`). Perfusion with a retention device has run at 4 m³
(Genzyme Geel). Vendor ratings stop at 5 m³. Nobody has run animal-cell perfusion above about 4 m³. For meat cells, no perfusion above 10 L is reported, and besides Vow no vessel above 2 m³.
Microbial tanks of 150 m³ and more exist (Quorn's 155 m³ airlift runs continuously), so the steel is not the problem. `vessels_and_modes_sources/operating_modes.md` puts 2% to 3% on anyone having run
animal-cell perfusion at 20 m³ for a month, and 6% at 10 m³ or more.

Three events, for a tank of each size. "Possible" means: with funding and a development programme of up to ten years, nothing in the model's physics or the evidence stops it.

- **H**: the tank is built and run with animal cells for a production run of at least two weeks (any mode, any density).
- **R**: the tank is run in perfusion with a retention device for at least four weeks at 100 g/L or more.
- **D**: the scenario's own design works at that size (R, at the design's density, with its tricks for at least four weeks).

| Size | H, possible | R, possible | R, shown by end of 2035 | D, best | D, central | D, cautious |
|---|---|---|---|---|---|---|
| 2 m³ | 99% | 97% | already shown | 14% | 12% | 19% |
| 5 m³ | 99% | 93% | already shown (4 m³) | 13% | 11% | 19% |
| 10 m³ | 98% | 85% | 25% | 12% | 10% | 17% |
| 20 m³ | 97% | 75% | 12% | 11% | 9% | 15% |
| 50 m³ | 88% | 55% | 4% | 8% | 12% | 11% |
| 100 m³ | 78% | 42% | 2% | 8% | 10% | 8% |
| 200 m³ | 62% | 30% | 1% | 6% | 7% | 8% |

How each column is built:
- **H.** Nothing in the physics stops a stirred tank above 25 m³. Large pharma tanks stop at 25 m³ for batch-size reasons, and the one report at 25 m³ found lower viability traced to CO₂ stripping.
  The odds fall with the size of the step beyond 25 m³ (shear, mixing time, pH and dissolved-gas zones): 88% at 50 m³, 78% at 100 m³, 62% at 200 m³. By the end of 2035 I put H, shown, at about 12% for 50 m³,
  5% for 100 m³ and 2% for 200 m³: the largest vessels in use or planned are 20 to 22 m³ (Vow, Meatly, Orbillion), and the 100,000 L and 250,000 L plans (UPSIDE Glenview, GOOD Meat, BlueNalu) were paused, abandoned or not started.
- **R.** The anchor is `retention_devices.md`: a filter holds 120 g/L at 20 m³ for a month at 75%. Each doubling of size above 20 m³ multiplies the odds by about 0.82, because the area (and the number of
  parallel units, 16 to 179) grows with the tank, and a failure in one unit has more units to occur in. Below 20 m³ the odds rise toward the 2 m³ perfusion tanks that are standard in pharma.
- **D.** D multiplies R by a density factor and a tricks factor, and takes the two as independent (they are probably positively correlated, which would raise D by a third). The density factor is 0.47 at 258 g/L (35% against 75%
  in `retention_devices.md`), 0.57 at 195 g/L, 0.65 at 153 g/L and 0.67 at 145 g/L (50% against 75%, `no_perfusion_downside.md`). The tricks factor is 0.30 for the column with pressure (a column loop works at 20 m³: 35%,
  `gas_exchange_study.md` section 5; pressure 85%), 0.26 with the recycled oxygen too, and 0.35 for the column alone. Central at 50 m³ rises to 12% because its design drops the oxygen trick and the density to 153 g/L.
  Example, best at 20 m³: 0.75 × 0.47 × 0.30 = 11%. Each entry is uncertain by a factor of 1.5 either way.

**What the odds say about size.** The chance that the scenario's own design works falls with size, but slowly: it is 11% to 19% at 2 to 5 m³, 9% to 15% at 20 m³ and 6% to 12% at 50 to 200 m³. The small
tanks are likelier but cost 6% to 50% more. Beyond 20 m³ the odds that any perfusion run works fall from 75% to 55%, 42% and 30% (R), and the best saving is $0.89 a kilo (cautious) or less. So the odds-adjusted
answer favours 10 to 20 m³. At 10 m³ the cost is 2% to 4% higher and R rises from 75% to 85%.

## 8. What would change the answer

1. **A measured pH limit for the column loop.** The largest size depends on one check set at 0.29 of the dose that slowed CHO cells. If cells tolerate 3 times the safe dose, the best and central
   cases run to 78 m³ and 34 m³ and save 1.9% and 1.6%. The experiment is the bench test in `gas_exchange_study.md` section 8.
2. **Labour by tank size above 20 m³.** If crew falls as Humbird's plants suggest, the best case saves 7.6% at 200 m³. A plant design with 100 m³ tanks and a crew count would settle it.
3. **Whether bubbles hurt by surface speed or by gas per litre.** The second rule moves every scenario toward 50 to 200 m³ (3% to 7%). `gas_exchange_study.md` section 2.3 puts 85% on bubble death scaling with gas per litre, but foam at 13 mm/s is unmeasured.
4. **A retention device that scales with the tank.** A settler or disc-stack separator has fewer parallel units, which would make large tanks more likely. The retention note puts 5% on a settler at 258 g/L.

## 9. Not done

- No size above 200 m³. Without the loop checks the best case still falls slowly at 200 m³ (3.4% below 20 m³), and Humbird's vessel cost (`30.7 V + 800` $k) is extrapolated above his range.
- No separate price for a tank built to a different shape beyond the model's steel and floor factor (`gas_exchange.shape_capex_factor`).
- No seed-train sizing, no heat exchanger, no impeller design, no run-length effect on membrane life with size.
- The search offers 16 designs per size. Intermediate pressures and a column outlet other than 55 mbar (`ge_col_pout`) are not searched; either could extend the sizes that pass the pH check.
