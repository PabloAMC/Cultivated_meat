# Cleaning and reusing the medium: what each route could save

> Names (2026-11-19): "Selected cells" was called Central; "Engineered cells, all favourable" was called the best case.

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50.
> Repinned 2026-11-19 (audit batch): ammonia tolerance 4 mM, lost runs pay for their membranes, glucose from the cells' balance (published cells need about 95 L/kg); see audit_2026-11-19.md.
> What this changed here: every route saves more. Central has more litres to save (35, was 28) and each litre filtered costs more
> ($0.44, was $0.38). One conclusion reversed: for the published cells reuse was capped at $4.6 and is now worth the most, because
> lactate sets their 95.5 litres and 74 of them pass the filter. An ammonium exchanger does nothing for them.

Date: 2026-11-16. Code: `medium_reuse.py`; test: `tests/test_medium_reuse.py`; inputs `mr_*`. Costs are 2025 dollars per kg of
wet cells. Nothing here changes a scenario. One accounting error in the model's sorbent lever was found and corrected on the
way (section 7). Access levels: **model** (computed here), **repo** (an earlier note, with its own sources), **book** (a chapter
of one of the two books Pablo supplied, read in part), **abstract**, **claim** (a patent claim, not data), **memory** (my
background knowledge, not checked this session).

**The question** (Pablo): can the ammonia be taken out and the liquid reused? Project G in `TODO.md`.

## 1. What a litre of medium costs, and why reuse cannot save all of it

In Central, 35 litres of medium pass through the tank for each kg of cells. Ammonia sets that figure: the cells make
0.14 mol per kg, the tank is held at 4 mmol/L, so 35 litres must leave to carry it out.

A litre that leaves costs $0.70: $0.20 of medium (a complete medium: its growth factors are in that price), $0.06 of bubble
protectant, and **$0.44 to pass it through the membranes that hold the cells back**. The filter is 62% of the cost of a litre.
(It was $0.38 before the audit batch. A lost run now throws its membranes away early.)

That part is what most reuse schemes cannot save. To take a mole of ammonia out of a tank held at 4 mmol/L, 250 litres must leave
the tank through the cell filter, whether they are then thrown away or cleaned and returned. A device on the permeate (the
cell-free liquid the filter passes) saves the medium, with its growth factors, and the protectant in what it returns. It does not
save the filter. Only a device that takes the waste out with no liquid drawn through the cell filter saves that too: dialysis
across the culture, or a sorbent or an exchange membrane in the tank. Then the device's own membrane meets the cells.

One consequence: a device on the permeate must take more than 62% of the waste from a litre in one pass before it
saves anything, even if the device is free. Each litre it cleans is filtered once and stands in for only that share of a
litre thrown away.

## 2. The routes, in Selected cells

| what sets the litres of medium (4. Plus perfusion (Selected cells): waste washed out through a cell filter) | litres per kg of cells |
|---|---|
| ammonia, held at 4 mmol/L | 35.0 |
| the least flow the cells need for everything else | 16.2 |
| lactate, within the salt limit | 21.5 |
| the nutrients, as a concentrate | 8.0 |
| leaves with the cells, unfiltered | 5.2 |

| route | fresh medium, L/kg | cleaned and returned, L/kg | through the cell filter, L/kg | cells, $/kg | saves | pays if the device costs under |
|---|---|---|---|---|---|---|
| No reuse | 35.0 | 0 | 29.8 | **$32.80** | | |
| An ammonium exchanger on the permeate, taking 38% of the ammonia | 21.7 | 13.3 | 29.8 | **$31.06** | $1.74 | (priced by its sorbent: 0.15 mol/kg at $5/kg, used once) |
| Electrodialysis of the permeate | 16.3 | 20.8 | 31.8 | **$29.92** | $2.88 | $0.18 a litre |
| Dialysis of the permeate, dialysate thrown away | 35.0 | 0.0 | 29.8 | **$32.80** | nothing | never |
| Dialysis of the permeate, dialysate cleaned and reused | 21.7 | 14.8 | 31.2 | **$31.74** | $1.06 | $0.16 a litre |
| Dialysis across the culture, dialysate cleaned and reused; the exchange membrane costs what the cell filter does | 8.0 | 30.0 | 2.8 | **$30.46** | $2.35 | $0.16 a litre |
| The same; the exchange membrane clears 10 L/m²/h, twice what the filter passes | 8.0 | 30.0 | 2.8 | **$23.88** | $8.93 | $0.38 a litre |
| *A perfect, free device on the permeate* | 8.0 | 27.0 | 29.8 | *$26.97* | *$5.83* | |
| *A perfect, free device across the culture* | 8.0 | 27.0 | 2.8 | *$15.13* | *$17.68* | |

"Pays if the device costs under" is the cost per litre cleaned at which the route saves nothing.

- **An ammonium exchanger** (zeolite or resin) saves $1.7. It takes only ammonia, so the litres cannot fall below what lactate asks
  (21.5 L/kg; the exchanger pays best taking 38% of the ammonia, at 21.7), and its sorbent holds little in salty medium (`waste_tricks_sizing.md`).
- **Electrodialysis of the permeate** saves $2.9, to $29.92. It takes ammonium and lactate, so the litres fall to the
  least flow the cells need for everything else (16 L/kg), which it does not relieve.
- **Dialysis of the permeate** saves nothing if the dialysate is thrown away (it uses 2.1 litres of basal medium to clean one),
  and $1.1 if the dialysate is itself cleaned and reused, as two patents claim.
- **Dialysis across the culture** saves $2.3 if its exchange membrane costs what the cell filter does, litre for litre, and
  $8.9 (to $23.88) if it clears twice the litres per m², as a haemodialyser does on blood. At the filter's cost it still does
  a little worse than electrodialysis of the permeate ($30.46 against $29.92), and the exchanger still beats dialysis of the
  permeate with a cleaned dialysate ($31.06 against $31.74).
- **The bounds:** a perfect, free device saves $5.8 on the permeate and $17.7 across the culture.
- **Why every saving fell by $1–3 on 2026-11-19 (growth factors inside the medium's price):** the growth factors are counted
  inside the $0.20 a litre, not bought on top, and a complete medium is charged at least its nutrients plus its growth factors.
  Cutting the litres therefore saves less medium, while the growth factors a device loses in a pass are still charged
  (`mr_gf_kept`, section 4), and the dialysate is priced as basal medium (the $0.20 less its growth factors, but never below
  the nutrients).
- **Why every saving then rose in the audit batch, the same day:** the cells tolerate 4 mmol/L of ammonia, not 5, so Central
  starts from 35 litres and not 28, and there are 7 more litres to save. Each litre filtered also costs more ($0.44, was $0.38).
  The routes that save anything save $1.1 to $8.9; they saved $0.5 to $5.7. The order of the routes did not change.

## 3. Across the scenarios

| scenario | no reuse | exchanger on the permeate | electrodialysis of the permeate | dialysis of the permeate, dialysate reused | dialysis across the culture, at the filter's cost | the same, at twice the filter's clearance | perfect and free, on the permeate | perfect and free, across the culture |
|---|---|---|---|---|---|---|---|---|
| Cautious: the best meat cells measured so far, in perfusion | **$92.17** | $92.17 | $68.05 | $78.44 | $73.60 | $52.32 | $61.45 | $23.14 |
| 4. Plus perfusion (Selected cells): waste washed out through a cell filter | **$32.80** | $31.06 | $29.92 | $31.74 | $30.46 | $23.88 | $26.97 | $15.13 |
| 7. Plus everything else at its favourable end (the Engineered cells, all favourable case) | **$11.46** | $11.46 | $11.46 | $11.46 | $11.46 | $10.53 | $11.11 | $8.74 |

**The published cells: this conclusion reversed.** Before the audit batch they used 28 litres, 22 of which left with the
harvested cells (the culture is thin, 46 g/L), so little passed the filter and reuse was capped at $4.6. Their glucose now comes
from their own balance. At a lactate yield of 1.05 they take up 4.5 mol of glucose a kilo and make 4.8 mol of lactate, so lactate
sets their medium at 95.5 litres, of which 74 pass the filter. Reuse is now worth more here than anywhere:

- An ammonium exchanger saves nothing. Ammonia asks for only 35 litres; lactate sets the 95.5.
- Electrodialysis of the permeate, which takes lactate too, saves $23.6 (to $88.27).
- Dialysis of the permeate with a cleaned dialysate saves $12.6; across the culture, $16.7 at the filter's cost and $34.8 at
  twice the filter's clearance (to $77.13).
- A perfect, free device saves $27.0 on the permeate and $59.5 across the culture.

These rest on the same unmeasured inputs as Central's, at three times the litres: 99% of the lactate taken in a pass
(`mr_ed_lac`, a figure cited second-hand), and growth factors that survive. And the best route modelled still leaves the
published cells at $77, against $32.80 for Central's cells with no device. Cells that make less lactate do more than any device.

In the best case the engineered cells make so little waste that reuse is worth at most $2.7 (a perfect, free device across the
culture); of the routes modelled only dialysis across the culture at twice the filter's clearance saves anything ($0.9).

## 4. What moves the answer

Each row sets one input to the ends of its range and gives the saving in Central against the scenario with the same input.

| input | low | high | electrodialysis of the permeate saves | dialysis across the culture, at twice the filter's clearance, saves |
|---|---|---|---|---|
| electrodialysis, $ per litre treated (`mr_ed_cost_l`) | 0.005 | 0.1 | $3.19 to $1.23 | $9.87 to $3.89 |
| growth factors that survive a pass (`mr_gf_kept`) | 0.5 | 1 | $1.99 to $3.10 | $7.65 to $9.25 |
| ammonium electrodialysis takes in a pass (`mr_ed_nh3`) | 0.5 | 0.95 | nothing to $3.39 | $8.93 to $8.93 |
| waste dialysis takes in a pass (`mr_dial_removal`) | 0.7 | 0.95 | $2.88 to $2.88 | $6.42 to $9.38 |
| dialysate replaced per pass (`mr_dialysate_makeup`) | 0.05 | 0.5 | $2.88 to $2.88 | $9.22 to $6.58 |
| exchange membrane clearance, L/m²/h (`mr_exchange_clearance`) | 5 | 15 | $2.88 to $2.88 | $2.35 to $11.12 |
| litres a m² of cell filter lasts (`rt_membrane_life`) | 900 | 5500 | $0.25 to $3.13 | $26.47 to $7.48 |
| least medium flow, mL per g a day (`pf_min_perfusion`) | 3.7 | 18.5 | $3.59 to nothing | $8.93 to $10.83 |

- Electrodialysis stops paying if it takes only half the ammonium in a pass (section 1), or if the least medium flow is at the
  top of its range, where ammonia no longer sets the litres.
- The exchange membrane's clearance and the share of dialysate replaced decide the across-the-culture route.
- A shorter-lived cell filter makes everything on the permeate worse and the across-the-culture route better.
- The share of growth factors that survive a pass matters: half surviving cuts electrodialysis's saving to $2.0.

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
stack was found. Even at $0.10 the route still saves $1.2 in Central: the filter, not the device, is the larger cost.

## 7. A correction to the model's sorbent lever

`floor_physics.explore` has had a `sorbent` lever since the gas-exchange study: a share of the ammonium is taken from the permeate
by an exchanger and the permeate returns. It lowered the litres of fresh medium, and with them the litres through the cell
filter. That second step was wrong, for the reason in section 1: the returned liquid passes the filter too. Corrected on
2026-11-16, in Python and on the page. No scenario uses the lever, so no headline moved. The figure this repository's TODO list
quoted (a sorbent taking half the ammonia takes Central to $22.97) becomes $28.22 at half, and $27.01 at the best share (42%).
With the model of 2026-11-19 (Central $26.43): $27.01 at half, $25.80 at 42%. After the audit batch (Central $32.80): $33.47 at
half, which is worse than no exchanger, and $31.06 at the best share (38%).

## 8. Judgement

- Cleaning the permeate is worth **about $1.1–2.9 a kilo** in a Central-like process, by an exchanger, electrodialysis or dialysis
  with a cleaned dialysate ($0.5–1.7 before the audit batch; $2–4 before growth factors were counted inside the medium's price).
  The 50% I put on at least $2 being reachable at scale was judged on the first figures and is not re-judged here. At the model's
  settings one permeate route now reaches $2 again: electrodialysis, at $2.9. The perfect, free device saves $5.8. The separations
  are ordinary; what is unmeasured is what they do to growth factors, amino acids and trace nutrients over many passes.
- Cleaning across the culture is worth **$2.3–8.9**, and up to $17.7 in the limit. I put about 25% on an exchange membrane holding
  twice the filter's clearance for weeks at 190 g/L. It is the same open question as the cell filter's own life
  (`filter_flux.md`): what a dense culture does to a membrane over a run.
- Reuse and a cheaper cell filter attack the same $0.44 a litre. A filter that lasts longer makes permeate-side reuse better and
  the across-the-culture route less necessary. The two should be studied together.
- Reuse does not replace cells that make less waste: the best case gets to 14 L/kg with no device at all, and Central's cells
  cost $32.80 with no device where the published cells cost $77 with the best route modelled.
- For the published cells the model now puts $13–35 on a route that takes lactate. I have not put odds on it. It needs the
  lactate removal the citation claims, held over many passes at 74 litres filtered per kilo.

## 9. What would settle it

1. **Electrodialysis of real spent medium, at the bench.** Ammonium and lactate removed per pass; glucose, amino acids, phosphate,
   trace metals and growth factors lost; energy per litre. Then cells grown on the returned liquid for several passes.
2. **A dialyser on a dense culture for weeks.** Clearance per m² against time, at 100–190 g/L. This is the test
   `retention_alternatives.md` already asks for, with one more measurement.
3. **The dialysate loop.** Whether a dialysate can be cleaned to under 10% make-up (the patents' claim) without building up the
   by-products nobody measures.
4. **What the least medium flow is made of.** It is 16 of Central's 35 litres. If it is nutrients, a concentrate lowers it; if it is
   small by-products, dialysis does; if it is larger than 500 Da, nothing here does.

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
