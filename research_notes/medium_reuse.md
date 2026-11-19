# Cleaning and reusing the medium: what each route could save

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50.

Date: 2026-11-16. Code: `medium_reuse.py`; test: `tests/test_medium_reuse.py`; inputs `mr_*`. Costs are 2025 dollars per kg of
wet cells. Nothing here changes a scenario. One accounting error in the model's sorbent lever was found and corrected on the
way (section 7). Access levels: **model** (computed here), **repo** (an earlier note, with its own sources), **book** (a chapter
of one of the two books Pablo supplied, read in part), **abstract**, **claim** (a patent claim, not data), **memory** (my
background knowledge, not checked this session).

**The question** (Pablo): can the ammonia be taken out and the liquid reused? Project G in `TODO.md`.

## 1. What a litre of medium costs, and why reuse cannot save all of it

In Central, 28 litres of medium pass through the tank for each kg of cells. Ammonia sets that figure: the cells make
0.14 mol per kg, the tank is held at 5 mmol/L, so 28 litres must leave to carry it out.

A litre that leaves costs $0.64: $0.20 of medium (a complete medium: its growth factors are in that price), $0.06 of bubble
protectant, and **$0.38 to pass it through the membranes that hold the cells back**. The filter is 59% of the cost of a litre.

That half is what most reuse schemes cannot save. To take a mole of ammonia out of a tank held at 5 mmol/L, 200 litres must leave
the tank through the cell filter, whether they are then thrown away or cleaned and returned. A device on the permeate (the
cell-free liquid the filter passes) saves the medium, with its growth factors, and the protectant in what it returns. It does not
save the filter. Only a device that takes the waste out with no liquid drawn through the cell filter saves that too: dialysis
across the culture, or a sorbent or an exchange membrane in the tank. Then the device's own membrane meets the cells.

One consequence: a device on the permeate must take more than 59% of the waste from a litre in one pass before it
saves anything, even if the device is free. Each litre it cleans is filtered once and stands in for only that share of a
litre thrown away.

## 2. The routes, in Central

| what sets the litres of medium (3. Plus cells selected to grow faster on the low-waste feed (Central)) | litres per kg of cells |
|---|---|
| ammonia, held at 5 mmol/L | 28.0 |
| the least flow the cells need for everything else | 16.2 |
| lactate, within the salt limit | 9.4 |
| the nutrients, as a concentrate | 8.0 |
| leaves with the cells, unfiltered | 5.2 |

| route | fresh medium, L/kg | cleaned and returned, L/kg | through the cell filter, L/kg | cells, $/kg | saves | pays if the device costs under |
|---|---|---|---|---|---|---|
| No reuse | 28.0 | 0 | 22.8 | **$26.43** | | |
| An ammonium exchanger on the permeate, taking 42% of the ammonia | 16.2 | 11.8 | 22.8 | **$25.80** | $0.63 | (priced by its sorbent: 0.15 mol/kg at $5/kg, used once) |
| Electrodialysis of the permeate | 16.3 | 13.0 | 24.1 | **$24.74** | $1.69 | $0.19 a litre |
| Dialysis of the permeate, dialysate thrown away | 28.0 | 0.0 | 22.8 | **$26.43** | nothing | never |
| Dialysis of the permeate, dialysate cleaned and reused | 21.7 | 7.0 | 23.5 | **$25.88** | $0.54 | $0.17 a litre |
| Dialysis across the culture, dialysate cleaned and reused; the exchange membrane costs what the cell filter does | 8.0 | 22.2 | 2.8 | **$24.89** | $1.54 | $0.17 a litre |
| The same; the exchange membrane clears 10 L/m²/h, twice what the filter passes | 8.0 | 22.2 | 2.8 | **$20.73** | $5.70 | $0.36 a litre |
| *A perfect, free device on the permeate* | 8.0 | 20.0 | 22.8 | *$22.45* | *$3.98* | |
| *A perfect, free device across the culture* | 8.0 | 20.1 | 2.8 | *$14.95* | *$11.48* | |

"Pays if the device costs under" is the cost per litre cleaned at which the route saves nothing.

- **An ammonium exchanger** (zeolite or resin) saves $0.6. It takes only ammonia, and its sorbent holds little in salty medium
  (`waste_tricks_sizing.md`).
- **Electrodialysis of the permeate** saves $1.7, to $24.74. It takes ammonium and lactate, so the litres fall to the
  least flow the cells need for everything else (16 L/kg), which it does not relieve.
- **Dialysis of the permeate** saves nothing if the dialysate is thrown away (it uses 2.1 litres of basal medium to clean one),
  and $0.5 if the dialysate is itself cleaned and reused, as two patents claim.
- **Dialysis across the culture** saves $1.5 if its exchange membrane costs what the cell filter does, litre for litre, and
  $5.7 (to $20.73) if it clears twice the litres per m², as a haemodialyser does on blood. At the filter's cost it now does
  a little worse than electrodialysis of the permeate ($24.89 against $24.74; before 2026-11-19 it was $0.9 better), and the
  exchanger now beats dialysis of the permeate with a cleaned dialysate ($25.80 against $25.88).
- **The bounds:** a perfect, free device saves $4.0 on the permeate and $11.5 across the culture.
- **Why every saving fell by $1–3 on 2026-11-19:** the growth factors are now counted inside the $0.20 a litre, not bought on
  top, and a complete medium is charged at least its nutrients plus its growth factors. Cutting the litres therefore saves less
  medium, while the growth factors a device loses in a pass are still charged (`mr_gf_kept`, section 4), and the dialysate is
  priced as basal medium (the $0.20 less its growth factors, but never below the nutrients).

## 3. Across the scenarios

| scenario | no reuse | exchanger on the permeate | electrodialysis of the permeate | dialysis of the permeate, dialysate reused | dialysis across the culture, at the filter's cost | the same, at twice the filter's clearance | perfect and free, on the permeate | perfect and free, across the culture |
|---|---|---|---|---|---|---|---|---|
| 1. Today: the best meat cells measured, in an ordinary 20 m³ perfusion tank | **$56.99** | $55.87 | $55.37 | $56.01 | $55.65 | $54.31 | $54.81 | $52.37 |
| 3. Plus cells selected to grow faster on the low-waste feed (Central) | **$26.43** | $25.80 | $24.74 | $25.88 | $24.89 | $20.73 | $22.45 | $14.95 |
| 5. Plus engineered cells: the best case, everything works | **$9.96** | $9.96 | $9.95 | $9.96 | $9.96 | $9.53 | $9.78 | $8.59 |

Reuse is worth most where the litres are set by ammonia and the medium is dear (rungs 1 to 4). In the best case the engineered
cells make so little ammonia that medium is already at the nutrient floor, and reuse is worth at most $1.4. For today's cells
the culture is thin (46 g/L), so 22 of the 28 litres leave with the harvested cells and little passes the filter; reuse is
capped at $4.6.

## 4. What moves the answer

Each row sets one input to the ends of its range and gives the saving in Central against the scenario with the same input.

| input | low | high | electrodialysis of the permeate saves | dialysis across the culture, at twice the filter's clearance, saves |
|---|---|---|---|---|
| electrodialysis, $ per litre treated (`mr_ed_cost_l`) | 0.005 | 0.1 | $1.88 to $0.65 | $6.40 to $1.97 |
| growth factors that survive a pass (`mr_gf_kept`) | 0.5 | 1 | $1.13 to $1.83 | $4.75 to $5.94 |
| ammonium electrodialysis takes in a pass (`mr_ed_nh3`) | 0.5 | 0.95 | nothing to $1.97 | $5.70 to $5.70 |
| waste dialysis takes in a pass (`mr_dial_removal`) | 0.7 | 0.95 | $1.69 to $1.69 | $4.05 to $6.00 |
| dialysate replaced per pass (`mr_dialysate_makeup`) | 0.05 | 0.5 | $1.69 to $1.69 | $5.92 to $3.96 |
| exchange membrane clearance, L/m²/h (`mr_exchange_clearance`) | 5 | 15 | $1.69 to $1.69 | $1.54 to $7.09 |
| litres a m² of cell filter lasts (`rt_membrane_life`) | 900 | 5500 | $0.31 to $1.82 | $16.76 to $4.79 |
| least medium flow, mL per g a day (`pf_min_perfusion`) | 3.7 | 18.5 | $2.46 to nothing | $5.70 to $9.93 |

- Electrodialysis stops paying if it takes only half the ammonium in a pass (section 1), or if the least medium flow is at the
  top of its range, where ammonia no longer sets the litres.
- The exchange membrane's clearance and the share of dialysate replaced decide the across-the-culture route.
- A shorter-lived cell filter makes everything on the permeate worse and the across-the-culture route better.
- The share of growth factors that survive a pass matters: half surviving cuts electrodialysis's saving to $1.1.

## 5. The evidence

| route | what has been shown | what is assumed here |
|---|---|---|
| Electrodialysis of the permeate | over 90% of ammonium and 99% of lactate taken from medium by selective membranes (Nir 2023, as cited in Soccol et al. 2024; the report itself was not found); hybridoma grew 30-50% better with ammonium and lactate removed electrically (Chang et al. 1995, abstract) | the cost per litre is my arithmetic; 90% of growth factors survive a pass; the other by-products stay |
| Dialysis of the permeate, dialysate thrown away | CHO at 73 million cells/mL held 10 days with no medium change; lactate down 92% (YekrangSafakar et al. 2022, which dialysed the culture itself, not a permeate) | 2.1 L of basal medium per litre cleaned; ammonia and the other by-products follow lactate |
| Dialysis of the permeate, dialysate cleaned and reused | patent claims only (Yissum / Future Meat WO2018011805: 90% recirculated; Avant Meats WO2023012523: bacteria and an enzyme clean the dialysate) | the dialysate is cleaned at the electrodialysis cost and 10% of it replaced |
| Dialysis across the culture, dialysate cleaned and reused; the exchange membrane costs what the cell filter does | the same study, on 2 billion cells and a 1.4 m² dialyser | litre for litre, the exchange membrane and its hardware cost what the cell filter does |
| The same; the exchange membrane clears 10 L/m²/h, twice what the filter passes | a haemodialyser's clearance on blood, over 4-hour sessions (from memory, not checked) | that clearance holds for weeks in a culture of 190 g/L |

Sources, with how far each was read:

- **Nir 2023**, "Selective separation of ammonium and lactate from cell culture media" (**book**: cited in Soccol et al. eds.,
  *Cultivated Meat*, Springer 2024, waste-management chapter, for "over 90%" of ammonium and "99%" of lactate by electrodialysis
  with selective membranes). The report itself was not found. Whether the figures are per pass, and what happened to amino acids,
  salts and growth factors, is not stated in the citation.
- **Chang, Grodzinsky and Wang 1995** (**abstract**): ammonium and lactate removed in place by an electric field across
  ion-exchange membranes at 50 A/m²; 10 mM of added ammonium and 45 mM of added lactate removed; hybridoma growth and antibody
  titre 30–50% higher. Bench scale.
- **YekrangSafakar et al. 2022** (**repo**, `waste_and_medium_evidence.md`): a 1.4 m² haemodialyser on the medium loop of a CHO
  culture at 73 million cells/mL; lactate down 92% in about 20 minutes; 10 days with no medium change; about 2.1 L of basal
  dialysate per litre regenerated. Ammonia and proteins not measured.
- **Patents** (**claim**): Yissum / Future Meat WO2018011805 (a dialyser with an ammonia filter on the dialysate, at least 90% of
  the perfusion liquid recirculated) and WO2021152536 (hollow fibres wrapped in absorbent, in the tank); Avant Meats WO2023012523
  (a membrane of 500 Da or more keeps growth factors in; nitrifying bacteria take the ammonia; an enzyme turns lactate into
  pyruvate).
- **Wimble, Ashizawa and Swartz** (found by a search pass; not read by me): a cost study of recovering lactic acid from spent
  medium by microfiltration, activated carbon, ion exchange, nanofiltration and evaporation. It reuses only the water, and the
  lactic acid sold offsets about $0.06 per kg of meat. So selling the waste is worth little; the value is in the litres saved.
- **Haemodialyser clearance** (**memory**): urea clearance of 250–300 mL/min over 1.8 m², about 10 L/m²/h, on blood at 30–40% cells
  for 4 hours. Not checked this session, and not measured on a culture over weeks.

## 6. The cost of electrodialysis per litre (my arithmetic, not a quote)

A litre of permeate at the tank's limits holds about 0.03 mol of ammonium and lactate against about 0.28 mol of other ions. If the
membranes were not selective, 5–20% of the current would do the useful work, so 0.15–0.6 mol of charge a litre:

- electricity: 0.006–0.024 kWh at 1.5 V a cell pair, $0.001–0.002;
- membranes: 0.04–0.16 m²·h at 100 A/m², $0.0005–0.005 at $200/m² over one to two years;
- the salt put back: $0.002–0.007.

That is $0.003–0.015 a litre. The model takes $0.02 and a range of $0.005–0.10, because no price for a food-grade, sterilisable
stack was found. Even at $0.10 the route still saves $0.6 in Central: the filter, not the device, is the larger cost.

## 7. A correction to the model's sorbent lever

`floor_physics.explore` has had a `sorbent` lever since the gas-exchange study: a share of the ammonium is taken from the permeate
by an exchanger and the permeate returns. It lowered the litres of fresh medium, and with them the litres through the cell
filter. That second step was wrong, for the reason in section 1: the returned liquid passes the filter too. Corrected on
2026-11-16, in Python and on the page. No scenario uses the lever, so no headline moved. The figure this repository's TODO list
quoted (a sorbent taking half the ammonia takes Central to $22.97) becomes $28.22 at half, and $27.01 at the best share (42%).
With the model of 2026-11-19 (Central $26.43): $27.01 at half, $25.80 at 42%.

## 8. Judgement

- Cleaning the permeate is worth **about $0.5–1.7 a kilo** in a Central-like process, by an exchanger, electrodialysis or dialysis
  with a cleaned dialysate ($2–4 before growth factors were counted inside the medium's price). The 50% I put on at least $2
  being reachable at scale was judged on the old figures and is not re-judged here: no permeate route now reaches $2 at the
  model's settings; the perfect, free device saves $4.0. The separations are ordinary; what is unmeasured is what they do to growth factors, amino acids and trace
  nutrients over many passes.
- Cleaning across the culture is worth **$1.5–5.7**, and up to $11.5 in the limit. I put about 25% on an exchange membrane holding
  twice the filter's clearance for weeks at 190 g/L. It is the same open question as the cell filter's own life
  (`filter_flux.md`): what a dense culture does to a membrane over a run.
- Reuse and a cheaper cell filter attack the same $0.38 a litre. A filter that lasts longer makes permeate-side reuse better and
  the across-the-culture route less necessary. The two should be studied together.
- Reuse does not replace cells that make less ammonia: the best case gets to 11 L/kg with no device at all.

## 9. What would settle it

1. **Electrodialysis of real spent medium, at the bench.** Ammonium and lactate removed per pass; glucose, amino acids, phosphate,
   trace metals and growth factors lost; energy per litre. Then cells grown on the returned liquid for several passes.
2. **A dialyser on a dense culture for weeks.** Clearance per m² against time, at 100–190 g/L. This is the test
   `retention_alternatives.md` already asks for, with one more measurement.
3. **The dialysate loop.** Whether a dialysate can be cleaned to under 10% make-up (the patents' claim) without building up the
   by-products nobody measures.
4. **What the least medium flow is made of.** It is 16 of Central's 28 litres. If it is nutrients, a concentrate lowers it; if it is
   small by-products, dialysis does; if it is larger than 500 Da, nothing here does.

## 10. Not found

- The Nir 2023 report, or any other measurement of selective electrodialysis on animal-cell medium with the nutrients tracked.
- Any price for an electrodialysis stack or a reusable dialyser rated for sterile food use.
- Ammonia removal, and growth-factor retention, measured across a dialyser in culture.
- Any run with a cleaned and reused dialysate, outside patent claims.
- Schneider, Marison and von Stockar 1996, the review both books cite, was not read.

## 11. A limit of the model noticed on the way, and fixed

`explore` let the fresh medium fall below the liquid that leaves with the harvested cells (the culture volume per kg, 22 L at
46 g/L). It cannot happen in a steady tank. No scenario was affected (all buy 28 L or run thicker). The floor was added to
`explore` the same day, as a medium term of its own; `medium_reuse.py` also applies it to the litres it sets.
