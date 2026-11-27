# Cleaning and reusing the medium: what each route could save

> Repinned 2026-11-27 (the nitrogen and carbon balance: each case's cells are charged the amino acids their ammonia takes and the glucose they ferment; a cleaning route's dialysate is floored at the case's own nutrients). The cases with no reuse do not move except the all-favourable example ($6.97 -> $7.02). In the low-lactate example every route rises by about $0.12 (electrodialysis $45.24 -> $45.37, dialysis across the culture $44.83 -> $44.95, at twice the clearance $32.95 -> $33.07) and a litre that leaves costs $0.95, not $0.98, because the cells' own nutrients ($2.13 a kilo grown) now nearly bind the medium's price; the filter is 75% of a litre, not 73%. The published cells eat $2.28 a kilo grown, not the model cell's $2.00, so their routes rise by about $0.25 to $0.30 (electrodialysis $135.02 -> $135.28); section 3 is recomputed. The conclusions are unchanged.

2026-11-25 (the gas cap and loop thinning): the engine now tries every gas flow up to the cells' cap, and holds a design whose
column loop is overloaded thinner, for each amount of medium cleaned. The published cells with no reuse fell from $181.13 to
$179.90 (1 mm/s of gas, 109 g/L); electrodialysis of their permeate from $135.54 to $135.02; at the short end of the cell filter's
life (900 L/m²) electrodialysis saves $0.23, not $0.70, and dialysis across the culture $26.56, not $31.51. The low-lactate and
all-favourable examples did not move. Tables regenerated from `medium_reuse.py`; section 3's prose on the published cells updated.

Date: 2026-11-16; every table and figure regenerated 2026-11-20 on the final model. Code: `medium_reuse.py`; test: `tests/test_medium_reuse.py`; inputs `mr_*`. Costs are 2025 dollars per kg of
wet cells. Nothing here changes a scenario. One accounting error in the model's sorbent lever was found and corrected on the
way (section 7). Access levels: **model** (computed here), **repo** (an earlier note, with its own sources), **book** (a chapter
of one of the two books Pablo supplied, read in part), **abstract**, **claim** (a patent claim, not data), **memory** (my
background knowledge, not checked this session).

**The question** (Pablo): can the ammonia be taken out and the liquid reused? Project G in `TODO.md`.

## 1. What a litre of medium costs, and why reuse cannot save all of it

In the low-lactate example, 39 litres of medium pass through the tank for each kg of cells harvested (35 for each kg grown: bubbles kill 8% of the cells grown and the harvest loses 2%). Ammonia sets that figure: the cells make
0.14 mol per kg, the tank is held at 4 mmol/L, so 35 litres must leave to carry it out.

A litre that leaves costs $0.95: $0.18 of medium (a complete medium: its growth factors are in that price), $0.06 of bubble
protectant, and **$0.71 to pass it through the membranes that hold the cells back**. The filter is 75% of the cost of a litre.
(The medium is less than its $0.20 a litre since 2026-11-27: the cells' own nutrients, $2.13 a kilo grown, nearly use up the part
of the price that is not growth factors, so a litre less saves little more than its growth factors. It was $0.98 and 73%.)
(It was $0.44 of $0.70 before 2026-11-20, when a m² of membrane was replaced after 3,960 litres, not 2,415.)

That part is what most reuse schemes cannot save. To take a mole of ammonia out of a tank held at 4 mmol/L, 250 litres must leave
the tank through the cell filter, whether they are then thrown away or cleaned and returned. A device on the permeate (the
cell-free liquid the filter passes) saves the medium, with its growth factors, and the protectant in what it returns. It does not
save the filter. Only a device that takes the waste out with no liquid drawn through the cell filter saves that too: dialysis
across the culture, or a sorbent or an exchange membrane in the tank. Then the device's own membrane meets the cells.

One consequence: a device on the permeate must take more than 75% of the waste from a litre in one pass before it
saves anything, even if the device is free. Each litre it cleans is filtered once and stands in for only that share of a
litre thrown away.

## 2. The routes, in the low-lactate example

| what sets the litres of medium (4. Plus perfusion (the low-lactate example): waste washed out through a cell filter) | litres per kg of cells |
|---|---|
| ammonia, held at 4 mmol/L | 38.8 |
| the least flow the cells need for everything else | 18.0 |
| lactate, within the salt limit | 34.1 |
| the nutrients, as a concentrate | 8.9 |
| leaves with the cells, unfiltered | 6.6 |

| route | fresh medium, L/kg | cleaned and returned, L/kg | through the cell filter, L/kg | cells, $/kg | saves | pays if the device costs under |
|---|---|---|---|---|---|---|
| No reuse | 38.8 | 0 | 32.2 | **$48.68** | | |
| An ammonium exchanger on the permeate, taking 12% of the ammonia | 34.2 | 4.7 | 32.2 | **$48.01** | $0.67 | (priced by its sorbent: 0.15 mol/kg at $5/kg, used once) |
| Electrodialysis of the permeate | 18.0 | 23.1 | 34.5 | **$45.37** | $3.31 | $0.21 a litre |
| Dialysis of the permeate, dialysate thrown away | 38.2 | 0.7 | 32.3 | **$48.66** | $0.02 | $0.08 a litre |
| Dialysis of the permeate, dialysate cleaned and reused | 8.9 | 33.2 | 35.5 | **$46.61** | $2.07 | $0.20 a litre |
| Dialysis across the culture, dialysate cleaned and reused; the exchange membrane costs what the cell filter does | 8.9 | 33.2 | 2.3 | **$44.95** | $3.73 | $0.20 a litre |
| The same; the exchange membrane clears 10 L/m²/h, twice what the filter passes | 8.9 | 33.3 | 2.3 | **$33.07** | $15.61 | $0.56 a litre |
| *A perfect, free device on the permeate* | 8.9 | 29.9 | 32.2 | *$40.29* | *$8.39* | |
| *A perfect, free device across the culture* | 8.9 | 30.0 | 2.3 | *$18.90* | *$29.79* | |

"Pays if the device costs under" is the cost per litre cleaned at which the route saves nothing. Litres are per kilo of cells harvested.

- **An ammonium exchanger** (zeolite or resin) saves $0.7. It takes only ammonia, so the litres cannot fall below what lactate asks
  (34.1 L/kg; the exchanger pays best taking 12% of the ammonia, at 34.2), and its sorbent holds little in salty medium
  (`waste_tricks_sizing.md`). Before 2026-11-20 it saved $1.7 taking 38%: lactate, then tolerated to 50 mmol/L, asked for only
  21.5 litres.
- **Electrodialysis of the permeate** saves $3.3, to $45.37. It takes ammonium and lactate, so the litres fall to the
  least flow the cells need for everything else (18 L/kg), which it does not relieve.
- **Dialysis of the permeate** saves $0.02 if the dialysate is thrown away (it uses 2.1 litres of basal medium to clean one),
  and $2.1 if the dialysate is itself cleaned and reused, as two patents claim.
- **Dialysis across the culture** saves $3.7 if its exchange membrane costs what the cell filter does, litre for litre, and
  $15.6 (to $33.07) if it clears twice the litres per m², as a haemodialyser does on blood.
- **The order.** At the filter's cost, dialysis across the culture does a little better than electrodialysis of the permeate
  ($44.95 against $45.37), and dialysis of the permeate with a cleaned dialysate beats the exchanger ($46.61 against $48.01).
  Before 2026-11-20 both were the other way round ($30.46 against $29.92; $31.74 against $31.06). Two changes did it. Lactate,
  tolerated to 35 mmol/L, not 50, now asks for 34 of the 39 litres, so a route that takes ammonia alone can cut only 5 litres,
  and electrodialysis, which stops at the least flow of 18, cuts 21; the two dialysis routes take the other by-products too and
  cut 30. And a litre of fresh medium costs more to pass (its membrane, and the medium preparation equipment sized by the
  litres), so the routes that cut the most litres gained the most.
- **The bounds:** a perfect, free device saves $8.4 on the permeate and $29.8 across the culture.
- **Growth factors inside the medium's price (2026-11-19):** the growth factors are counted inside the $0.20 a litre, not bought
  on top, and a complete medium is charged at least its nutrients plus its growth factors. Cutting the litres therefore saves
  less medium, while the growth factors a device loses in a pass are still charged (`mr_gf_kept`, section 4), and the dialysate
  is priced as basal medium (the $0.20 less its growth factors, but never below the nutrients).

## 3. Across the scenarios

| scenario | no reuse | exchanger on the permeate | electrodialysis of the permeate | dialysis of the permeate, dialysate reused | dialysis across the culture, at the filter's cost | the same, at twice the filter's clearance | perfect and free, on the permeate | perfect and free, across the culture |
|---|---|---|---|---|---|---|---|---|
| Cautious: the best meat cells measured so far, in perfusion | **$179.90** | $179.90 | $135.28 | $153.70 | $146.05 | $91.44 | $123.73 | $25.40 |
| 4. Plus perfusion (the low-lactate example): waste washed out through a cell filter | **$48.68** | $48.01 | $45.37 | $46.61 | $44.95 | $33.07 | $40.29 | $18.90 |
| 7. Plus everything else at its favourable end (the all-favourable example) | **$7.02** | $7.02 | $6.75 | $7.02 | $6.97 | $6.94 | $6.68 | $6.63 |

**The published cells.** (They are priced in perfusion as the cautious scenario: $179.90 with no reuse, at 109 g/L and 1 mm/s
of gas. Rung 1 of the ladder is a batch, which has no permeate to clean.) At a lactate yield of 1.05 they make 4.8 mol of lactate
a kilo. With lactate tolerated to 35 mmol/L, lactate sets their medium at 143 litres per kilo harvested, of which 133 pass the
filter. Reuse is worth more here than anywhere:

- An ammonium exchanger saves nothing. Ammonia asks for only 37 litres; lactate sets the 143.
- Electrodialysis of the permeate, which takes lactate too, saves $44.6 (to $135.28).
- Dialysis of the permeate with a cleaned dialysate saves $26.2; across the culture, $33.9 at the filter's cost and $88.5 at
  twice the filter's clearance (to $91.44).
- A perfect, free device saves $56.2 on the permeate and $154.5 across the culture.
- With the dialysis routes and the perfect devices the engine runs these cells denser (134 g/L at 2 mm/s, the densest at which
  the column loop then passes its checks). So these routes' litres are another design's, and the
  litre balance is checked with the design held (`tests/test_medium_reuse.py`).

These rest on the same unmeasured inputs as the low-lactate example's, at almost four times the litres: 99% of the lactate taken
in a pass (`mr_ed_lac`, a figure cited second-hand), and growth factors that survive. And the best route modelled still leaves the
published cells at $91, against $48.68 for the low-lactate example with no device. Cells that make less lactate do more than any
device.

**The all-favourable example** needs 11.7 litres a kilo harvested, set by ammonia (lactate asks for 11.1; it takes Humbird's
50 mmol/L of lactate tolerated), and holds its cells back with dialyser-grade fibres that add little to a litre. So no route is
worth much: electrodialysis of the permeate saves $0.27, and a perfect, free device across the culture $0.39.

## 4. What moves the answer

Each row sets one input to the ends of its range and gives the saving in the low-lactate example against the scenario with the same input.

| input | low | high | electrodialysis of the permeate saves | dialysis across the culture, at twice the filter's clearance, saves |
|---|---|---|---|---|
| electrodialysis, $ per litre treated (`mr_ed_cost_l`) | 0.005 | 0.1 | $3.66 to $1.47 | $16.66 to $10.02 |
| growth factors that survive a pass (`mr_gf_kept`) | 0.5 | 1 | $2.04 to $3.63 | $13.77 to $16.07 |
| ammonium electrodialysis takes in a pass (`mr_ed_nh3`) | 0.5 | 0.95 | nothing to $4.23 | $15.61 to $15.61 |
| waste dialysis takes in a pass (`mr_dial_removal`) | 0.7 | 0.95 | $3.31 to $3.31 | $11.57 to $16.35 |
| dialysate replaced per pass (`mr_dialysate_makeup`) | 0.05 | 0.5 | $3.31 to $3.31 | $15.83 to $13.88 |
| exchange membrane clearance, L/m²/h (`mr_exchange_clearance`) | 5 | 15 | $3.31 to $3.31 | $3.73 to $19.57 |
| litres a m² of cell filter lasts (`rt_membrane_life`) | 900 | 5500 | $0.11 to $4.23 | $26.44 to $10.35 |
| least medium flow, mL per g a day (`pf_min_perfusion`) | 3.7 | 18.5 | $4.89 to nothing | $15.61 to $18.80 |

- Electrodialysis stops paying if it takes only half the ammonium in a pass (section 1), or if the least medium flow is at the
  top of its range, where ammonia no longer sets the litres.
- The exchange membrane's clearance and the share of dialysate replaced decide the across-the-culture route.
- A shorter-lived cell filter makes everything on the permeate worse and the across-the-culture route better.
- The share of growth factors that survive a pass matters: half surviving cuts electrodialysis's saving to $2.0.

## 5. The evidence

| route | what has been shown | what is assumed here |
|---|---|---|
| Electrodialysis of the permeate | over 90% of ammonium and 99% of lactate taken from medium by selective membranes (Nir 2023, as cited in Soccol et al. 2024; the report itself was not found); hybridoma grew 30-50% better with ammonium and lactate removed electrically (Chang et al. 1995, abstract) | the cost per litre is an estimate from first principles (section 6 of the note); 90% of growth factors survive a pass; the other by-products stay |
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

## 6. The cost of electrodialysis per litre (arithmetic, not a quote)

A litre of permeate at the tank's limits holds about 0.03 mol of ammonium and lactate against about 0.28 mol of other ions. If the
membranes were not selective, 5–20% of the current would do the useful work, so 0.15–0.6 mol of charge a litre:

- electricity: 0.006–0.024 kWh at 1.5 V a cell pair, $0.001–0.002;
- membranes: 0.04–0.16 m²·h at 100 A/m², $0.0005–0.005 at $200/m² over one to two years;
- the salt put back: $0.002–0.007.

That is $0.003–0.015 a litre. The model takes $0.02 and a range of $0.005–0.10, because no price for a food-grade, sterilisable
stack was found. Even at $0.10 the route still saves $1.6 in the low-lactate example: the filter, not the device, is the larger cost.

## 7. A correction to the model's sorbent lever

`floor_physics.explore` has had a `sorbent` lever since the gas-exchange study: a share of the ammonium is taken from the permeate
by an exchanger and the permeate returns. It lowered the litres of fresh medium, and with them the litres through the cell
filter. That second step was wrong, for the reason in section 1: the returned liquid passes the filter too. Corrected on
2026-11-16, in Python and on the page. No scenario uses the lever, so no headline moved. The figure this repository's TODO list
quoted (a sorbent taking half the ammonia takes the low-lactate example to $22.97) becomes $28.22 at half, and $27.01 at the best share (42%).
With the model of 2026-11-19 (the low-lactate example $26.43): $27.01 at half, $25.80 at 42%. After the audit batch (the low-lactate example $32.80): $33.47 at
half, which is worse than no exchanger, and $31.06 at the best share (38%). On the final model of 2026-11-20 (the low-lactate
example $49.50): $61.09 at half, and $48.70 at the best share, which is now 12%. Past 12% lactate sets the litres, so more sorbent buys
nothing.

## 8. Judgement

- Cleaning the permeate is worth **about $0.8–3.5 a kilo** in a process like the low-lactate example, by an exchanger, dialysis
  with a cleaned dialysate or electrodialysis. Two permeate routes reach $2 at the model's settings: dialysis with a cleaned
  dialysate, at $2.1, and electrodialysis, at $3.3. The perfect, free device saves $8.4. The separations are ordinary; what is
  unmeasured is what they do to growth factors, amino acids and trace nutrients over many passes. For $2 or more to be reached
  at scale, a device would have to take most of the ammonium and lactate in one pass and lose under half the growth factors,
  over many passes.
- Cleaning across the culture is worth **$3.7–15.6**, and up to $29.8 in the limit. The upper figure needs an exchange membrane
  that holds twice the filter's clearance for weeks at 150–190 g/L. It is the same open question as the cell filter's own life
  (`filter_flux.md`): what a dense culture does to a membrane over a run.
- Reuse and a cheaper cell filter attack the same $0.71 a litre. A filter that lasts longer makes permeate-side reuse better and
  the across-the-culture route less necessary. The two should be studied together.
- Reuse does not replace cells that make less waste: the all-favourable example needs 12 L/kg with no device at all, and the
  low-lactate example's cells cost $48.68 with no device where the published cells cost $91 with the best route modelled.
- An ammonium exchanger alone is not worth studying for these cells: lactate asks for nearly as many litres as ammonia. A route
  has to take both.
- For the published cells the model puts $26–89 on a route that takes lactate. It needs the lactate removal the citation claims,
  held over many passes at 133 litres filtered per kilo.

## 9. What would settle it

1. **Electrodialysis of real spent medium, at the bench.** Ammonium and lactate removed per pass; glucose, amino acids, phosphate,
   trace metals and growth factors lost; energy per litre. Then cells grown on the returned liquid for several passes.
2. **A dialyser on a dense culture for weeks.** Clearance per m² against time, at 100–190 g/L. This is the test
   `retention_alternatives.md` already asks for, with one more measurement.
3. **The dialysate loop.** Whether a dialysate can be cleaned to under 10% make-up (the patents' claim) without building up the
   by-products nobody measures.
4. **What the least medium flow is made of.** It is 18 of the low-lactate example's 39 litres. If it is nutrients, a concentrate lowers it; if it is
   small by-products, dialysis does; if it is larger than 500 Da, nothing here does.

*Evidence pass 2026-11-21* ([evidence_medium_cleaning.md](evidence_medium_cleaning.md)): ammonia removal has been shown at
bench scale, none with a cost. Haraguchi 2021: the alga *C. littorale* took up 80% of the ammonia in 7 days. Thyden 2024:
*C. sorokiniana* removed all of it at 37 °C, and QM7 cells grew at 81% of the rate on fresh medium. Pakbin 2025: air stripping
at pH 12 removed 82%. An ion-concentration-polarisation device (2025) reused 75% of a CHO medium. Schneider 1994/1997: a
gas-permeable membrane cut ammonia by about half. Nir 2023 remains unlocated. No input changes.

## 10. Not found

- The Nir 2023 report, or any other measurement of selective electrodialysis on animal-cell medium with the nutrients tracked.
- Any price for an electrodialysis stack or a reusable dialyser rated for sterile food use.
- Ammonia removal, and growth-factor retention, measured across a dialyser in culture.
- Any run with a cleaned and reused dialysate, outside patent claims.
- Schneider, Marison and von Stockar 1996, the review both books cite, was not read.

## 11. A limit of the model noticed on the way, and fixed

`explore` let the fresh medium fall below the liquid that leaves with the harvested cells (the culture volume per kg, 22 L at
46 g/L). It cannot happen in a steady tank. No scenario was affected (all bought 28 L or more, or ran thicker). The floor was added to
`explore` the same day, as a medium term of its own; `medium_reuse.py` also applies it to the litres it sets.
