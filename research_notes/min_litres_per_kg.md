# The least medium per kg of cells that physics allows

> **Repinned 2026-11-27 (the nitrogen and carbon balance).** `min_litres.nutrients` takes the cost floor's 0.232 kg of amino acids and the balance's glucose (`floor_physics.nutrient_balance`), not Humbird's 0.26 kg, so the salt-limited bounds need fewer litres; the cases' cells eat what their ammonia and lactate imply. The all-favourable example costs $7.02: bath 23.2 L/kg ($8.36), physical and practical 5.84 L/kg ($6.22), measured flow 5.12 L/kg ($6.13). The low-lactate example: bath 26.1 L/kg ($36.13), physical 6.72 L/kg ($16.77), practical 8.88 L/kg ($18.90). The tables below are as of 2026-11-21; the conclusions are unchanged.
>
> **Repinned 2026-11-21 (fourth batch, documents).** The tables of the answer and of the cost at the bounds, and the figures in their prose, are
> recomputed from `python min_litres.py`. Since 2026-11-21 the all-favourable example runs at 219 g/L (its CO₂ loop held at the densest culture it
> passes), not 155, and costs $6.97; the low-lactate example runs at 168 g/L and costs $48.68. Less culture leaves with the all-favourable
> example's cells (4.6 L per kilo grown, was 6.4), so its physical floor (5.5 L) now binds and its bounds separate again; 89.1% of
> its cells grown are harvested (92.4% before). The nutrients' glucose is the mass balance's (0.311 kg a kilo), so the bath and
> feed bounds fell by about 1%. The box below is the 2026-11-20 repin; its figures are as of that day.

> Repinned 2026-11-20 (final pass). The all-favourable example is now the one case of `scenarios.all_favourable()` ($7.62): cells doubling every 16 hours, 3 ng a cell, 0.054 mol of ammonia a kilo, a lactate yield of 0.279, Humbird's tolerances of 5 mmol/L of ammonia and 50 of lactate, the lowest measured medium flow (3.7 mL/g/day), 155 g/L. `min_litres.costs_at` now gives every row's litres per kilo harvested, as the costs are. **What changed:** (1) the all-favourable example's litres are set by ammonia again (10.80 L per kilo grown, lactate 10.25); in the first batch of 2026-11-20 they were set by lactate at 35 mmol/L. The test that compared this module's nitrogen term with `explore()`'s had assumed 4 mmol/L for both examples; it now uses each example's own limit, and the two agree exactly (a stale check, not an inconsistency). (2) The all-favourable example's physical floor is 5.5 L per kilo grown, but the culture that leaves with its cells is 6.4, so the model's litres can fall only to that: from the model's 11.7 litres a kilo harvested to 7.0 saves $0.61 a kilo ($7.62 to $7.01). (3) The low-lactate example's bounds did not move; its costs did ($49.50 at the model's litres, $17.93 at the physical floor). Every table below is regenerated from `python min_litres.py`.

> Earlier repins (2026-11-20 first batch; 2026-11-19 scenario restructure, nutrient floor and audit batch; 2026-11-16 recompute) are recorded in the changelog.

> Names (2026-11-19): the low-lactate example was earlier called Central; the all-favourable example was earlier called the best case. Cells are described by their traits, never as a named kind of cell.

Date: 2026-11-20 (compiled 2026-11-15). Code: `min_litres.py` (bounds and costs), `tests/test_min_litres.py`. Inputs: `ml_*` in `inputs.py`. No default moved. Costs are 2025 dollars per kg of wet cells. The low-lactate example is a 20 m3 stirred tank in perfusion with a TFF loop; the all-favourable example a 42 m3 tank with dialyser-grade fibres.

Access codes: **FULL** = full text read. **FT-sum** = full text read through a summariser. **PART** = a secondary page or article read, not the paper. **SNIP** = search snippet only. **INF** = my arithmetic. **RECALL** = from memory, no source read. Source access carried from `waste_and_medium_evidence.md`, `waste_tricks_sizing.md` and `perfusion_rate_osmolality.md` is marked EARLIER.

## Answer

1. Stoichiometry sets no floor. Nitrogen, carbon and energy balances all allow zero ammonia and zero lactate, so waste can fall to 0 L/kg. Warburg-null CHO and HEK show it for lactate (FULL); a glutamine-synthetase CHO line comes within 0.4% of zero for ammonia (INF from FT-sum).
2. Delivering the nutrients sets the floor. A kg of cells eats 0.55 kg (the all-favourable example) to 0.64 kg (the low-lactate example) of amino acids and glucose, 3.7-4.1 mol. The litres follow from how strong the feed can be (litres per kilo of cells grown, `min_litres.bounds`):

| Feed | All-favourable example (16 h, 3 ng) | Low-lactate example (36 h, 2 ng) |
|---|---|---|
| The medium is what the cells sit in, at the salt limit, typical salts (250 mOsm/kg) | 21.9 L/kg | 24.8 L/kg |
| Same, salts cut to 150 | 13.6 | 15.4 |
| A concentrate of 50 g/L, diluted in the tank | 10.9 | 12.6 |
| A concentrate of 100 g/L (default) | **5.5** | **6.3** |
| A concentrate of 200 g/L | 2.7 | 3.2 |
| Lowest measured flow per cell (3.7 mL/g/day) over the growth rate | 3.6 | 8.0 |

3. Reading: if the medium must be iso-osmotic with the cells, as pharma perfusion media are, the floor is 14-25 L/kg. The low-lactate example's 35 is 1.4 times the top of that range, and the all-favourable example's 10.8 is below the bottom of it. If a concentrate can be dosed into the tank, the floor is about 6-8 L/kg, and the low-lactate example sits 4.4-5.6 times above it, the all-favourable example 2.0 times. The physical floor is **5.5 L/kg (the all-favourable example) and 6.3 L/kg (the low-lactate example)**, and the floor that respects measured flows 5.5 and 8.0. In the all-favourable example the culture that leaves with each kilo of cells (4.6 L at 219 g/L) is below its floor, so the floor binds; only the lowest measured flow alone (3.6 L) falls below that culture, and is raised to it.

## Where the model sits

Litres per kilo of cells grown; the model reports them per kilo harvested (89.1% of the cells grown in the all-favourable example, 90.2% in the low-lactate example).

| | All-favourable example | Low-lactate example | Floor |
|---|---|---|---|
| Litres per kg grown (per kg harvested) | 10.80 (12.12): ammonia 10.80, lactate 10.25, nutrients 8.0, culture leaving with the cells 4.6, least flow 3.6 | 35.0 (38.8): ammonia; lactate 30.7, least flow 16.2 | 5.5 / 6.3 |
| Ammonia tolerated, mmol/L | 5 (Humbird's) | 4 | |
| Ammonia, mol/kg | 0.054 (1.9% of the cell's nitrogen) | 0.14 (4.9%) | 0; at the floor litres, 0.028 (1.0%) fits at 5 mmol/L, 0.026 (0.9%) at 4 |
| Lactate, mol per mol of all glucose taken up | 0.279 (0.51 mol/kg) | 0.42 (1.07 mol/kg) | 0; at the floor litres, 0.28 mol/kg fits at 50 mmol/L (a yield of 0.16), 0.22 at 35 mmol/L (0.10) |
| Least flow, mL/g/day | 3.7 (the measured low end) | 7.5 | 3.7 measured (zero growth) |
| Doubling time | 16 h | 36 h | |

Both examples' litres are set by ammonia, each at its own tolerance. With zero waste the all-favourable example would need the model's own nutrient floor of 8 L/kg grown (9.0 per kilo harvested); the low-lactate example would need 16.2 L/kg grown, set by the 7.5 mL/g/day flow at a 36 h doubling, and at 3.7 mL/g/day 8.0. The published cells sit far above all of this: 146 L per kilo harvested (136 grown), set by lactate (4.8 mol/kg at a yield of 1.05).

## Cost at the bounds

`min_litres.costs_at`: `explore(medium_l=...)` with each example's other settings held. Litres per kilo harvested, as `explore` reports them; `explore` raises a bound below the culture that leaves with the cells to that culture.

| Row (bound, L per kg grown: all-favourable / low-lactate) | All-favourable example | Low-lactate example |
|---|---|---|
| Model's litres (10.80 / 35.0) | 12.1 L, $6.97 | 38.8 L, $48.68 |
| Bath, typical salts (21.9 / 24.8) | 24.6 L, $8.47 | 27.5 L, $37.35 |
| Zero waste, model's own flow (8.0 / 16.2) | 9.0 L, $6.58 | 18.0 L, $27.94 |
| Physical floor, 100 g/L feed (5.5 / 6.3) | 6.1 L, $6.21 | 7.0 L, $16.90 |
| Lowest measured flow (3.6 / 8.0) | 5.1 L, $6.08 | 8.9 L, $18.78 |
| Zero waste, lowest measured flow, model floor of 8 L/kg (8.0 / 8.0) | 9.0 L, $6.58 | 8.9 L, $18.78 |

The all-favourable example gains $0.76 at its floor. Its medium is the nutrient floor ($2.23 a kilo whatever the litres) and its dialyser fibres cost $0.06 a kilo, so litres are cheap there; the bath row, at 25 litres a kilo, costs it $1.50 more than its own litres. The low-lactate example gains $29.90 at 8 L/kg grown, mostly in the filter loop ($22.71 of membranes to $1.60) and the medium ($7.94 of feedstock to $3.55: below about 22 L/kg the $0.20 complete medium is charged its nutrients plus its growth factors). At 11 L/kg grown it costs $22.14 (INF, same call). A bath of typical salts costs the low-lactate example less than its own litres ($37.35 against $48.68). Zero waste with the model's own flow costs the all-favourable example more than its floor, because the model's nutrient floor of 8 L/kg binds there and not in a run whose litres are set from outside. These costs assume the waste fits in the litres; at the floor that needs the ammonia and lactate in the table above.

## The four bounds

### (a) Nitrogen balance

- A kg of cells holds 0.21 x 13.6 = **2.86 mol N** (Humbird's CH1.68 O0.34 N0.21, EARLIER). A protein-only count gives about 2.2 (195 g protein at 16% N), and nucleic acids add about 0.2 (INF).
- Amino acids supplied in the proportion the cell builds protein deliver that nitrogen without freeing ammonia: the nitrogen moves by transamination. Humbird's 0.26 kg of pure amino acids is 0.26 x 1000 / 128 = 2.03 mol; at 1.4 N each that is 2.86 mol, so the figures agree (INF).
- Protein turnover returns its amino acids to the pool. Purine and pyrimidine turnover is mostly salvaged (RECALL), and glutamine amide transfers release glutamate, not ammonia. I found no stoichiometric step that forces ammonia out. **Floor: 0 mol/kg, 0 L/kg.** I could not source a measured protein or nucleotide turnover rate for cultured meat cells; a search for the median protein half-life did not confirm any number (SNIP).
- The free parameter is the leak: the share of the 2.86 mol that leaves as ammonia. Litres = leak x 2.86 / 0.004 = **714 L/kg per unit leak** at the 4 mmol/L the low-lactate example's cells tolerate, and 571 at Humbird's 5 mmol/L, which the all-favourable example takes.

| Leak | mol/kg | L/kg at 4 mM | L/kg at 5 mM | Source |
|---|---|---|---|---|
| 0.4% | 0.012 | 3.0 | 2.4 | CHO GS perfusion plateau, 0.54 fmol/cell/h taken to 0.35/day (range 0.0063-0.029). Mayrhofer 2020, FT-sum; extrapolation INF |
| 1.0% | 0.028 | 6.9 | 5.5 | what the all-favourable example's floor litres allow |
| 1.9% | 0.054 | 13.5 | **10.8** | the all-favourable example (Humbird's enhanced cell) |
| 3.2% | 0.09 | 22.5 | 18 | bovine FAPs, shaker flask (Hubalek 2023, FT-sum) |
| 4.9% | 0.14 | **35** | 28 | the low-lactate example; bovine FAPs on alpha-ketoglutarate or pyruvate, at most (Hubalek 2023) |
| 24.5% | 0.70 | 175 | 140 | bovine FAPs, spinner, with glutamine (Hubalek 2023) |

Ammonia does not bind at the floor. It binds in the low-lactate example (35 L/kg) because those cells leak 4.9%, and in the all-favourable example (10.8 L/kg at a 1.9% leak and 5 mmol/L). The all-favourable example's leak is 2.6 times less than the low-lactate example's; the one measured CHO line is 4.5 times below it. Its floor litres ask for a leak 1.9 times below its own.

### (b) Carbon and energy balance

- **Lactate.** Glucose burned whole gives CO2 and no lactate, so the floor yield is zero. Hefzi et al. 2025 (Nat Metab, PMC12272911, FULL) report Warburg-null CHO-S, CHO-K1 and HEK293 with peak lactate sub-mM to single mM against 13-135 mM in wild type, growth "comparable to WT", but the rates sit in figures I could not read. Adapted CHO reached 0.39 mol/mol (Freund and Croughan 2018, EARLIER). Glucose per kg: the model's feedstock count gives 1.63 mol for the all-favourable example's cells (16 h, 3 ng) and 2.12 for the low-lactate example's (36 h, 2 ng). `pf_glc_kg` gives 1.116 mol. Since 2026-11-19 the scenarios take glucose from the cells' own balance (`floor_physics.glucose_balance`): 1.60 mol (the all-favourable example) and 2.07 (the low-lactate example) with no lactate, within 3% of the feedstock figure, and 1.84 and 2.56 with their lactate. So the feedstock figure is the right one, and `pf_glc_kg` does not enter the scenarios. **Floor 0 L/kg.** At 50 mmol/L, 0.28 mol of lactate per kg fits the all-favourable example's 5.5 L/kg floor: a yield of 0.17 on the glucose of a cell that makes no lactate, or 0.16 per mol of all the glucose taken up, the basis the scenarios use (it assumes 0.279). At 35 mmol/L, 0.22 mol fits the low-lactate example's 6.4 L/kg floor, a yield of 0.10 (it assumes 0.42).
- **CO2.** The model burns 4.30 mol O2/kg (the all-favourable example) and 7.14 (the low-lactate example) and makes 5.2 and 8.6 mol CO2 at an RQ of 1.204. Kilburn et al. 1969 measured mouse fibroblasts at 1.6e-11 mol ATP per cell to build and 2.9e-11 per new cell for upkeep at a 27.6 h generation (PART: BioNumbers page, secondary). At each example's cell weight and doubling time and 5 ATP per O2 that is 10.9 mol ATP/kg against the model's 21.5 (the all-favourable example, ratio 2.0) and 26.9 against 35.7 (the low-lactate example, 1.3) (INF; the fibroblast's size is not on that page, so the ratio is good to a factor of 2). Burning glucose whole for Kilburn's ATP takes 0.34 and 0.84 mol glucose. CO2 could fall to about half. It reaches the litres only through bicarbonate salt: 12.7 mOsm at 100 mbar and pH 7.2, nothing below about 80 mbar. **It does not bind.**

### (c) Osmolality budget

- Nutrients per kg: 2.03 mol amino acids + 1.63 mol glucose = **3.66 mol** (the all-favourable example); 4.15 (the low-lactate example). Each is about one osmole per mole (INF).
- If the medium is what the cells sit in: litres = 3.81 / ((415 - S) / 1000). S is the salt and buffer osmolality, 250 in a conventional medium (RECALL: about 100 mM NaCl, 25 mM bicarbonate; no sheet read). Result (the all-favourable example): **22.2 L/kg** at S = 250, 17.0 at 200, 13.8 at 150. Its 10.8 L/kg would need a nutrient budget of 339 mOsm, so S <= 76, half the 150 taken as the low end for salts.
- Check against practice: Mayrhofer et al. 2020 (FT-sum) ran perfusion media to a 400 mOsm/kg target and held 14-30 pL/cell/day at 0.15/day growth, which `waste_and_medium_evidence.md` converts to 31-67 L/kg. My bath bound of 25 L/kg at full growth sits below that, as a bound should.
- The salt limit does not apply to the feed if the feed is a concentrate diluted in the tank. The tank sees salts plus residual nutrient plus the waste salts (2 mOsm per mmol/L of lactate), and consumption removes the nutrient osmoles. The model's tank budget is already in `explore` (the all-favourable example's tank is at 408 of 415 mOsm/kg, the low-lactate example's at 374). Then the feed is limited by what dissolves: litres = 0.55 kg / feed strength. At 100 g/L that is **5.5 L/kg** (the low-lactate example 6.4). Tyrosine and cystine are the known solubility limit in concentrated feeds, and ultra-concentrated feeds have been made (SNIP: PMC4685332, page blocked). No number was found for the strongest feed, so 50-200 g/L is a judgement, and the 100 g/L default carries most of the uncertainty. Single-strength media carry roughly 10-30 g/L of these (RECALL).
- Cells can be made to grow at higher osmolality, which would raise the 415 limit: a CHO-S line adapted to 450 mOsm (Kamachi, conference abstract, SNIP) and constant 380-410 mOsm in CHO-DG44 perfusion with productivity up 66% (GEN News article, PART). Fed-batch CHO exposed to 545 mOsm/kg tripled in volume and stopped growing (Romanova 2021, SNIP). I did not carry this into the bound.

### (d) Least perfusion flow per cell

- Model: `pf_min_perfusion` = 7.5 mL/g/day (the all-favourable example takes the measured low end, 3.7). Litres = flow / growth rate in 1/day: the low-lactate example 16.2 at 7.5; the all-favourable example 3.6 at 3.7.
- Measured, CHO (EARLIER, `perfusion_rate_osmolality.md`): 3.7 mL/g/day at 8-10 pL/cell/day with no net growth (Mayrhofer 2020, FT); 5.2-11 at 14-30 pL while growing at 0.15/day; 18.5 at 50 pL (Clincke 2013, FULL). At 3.7: the all-favourable example 3.6, the low-lactate example 8.0.
- Physics for the zero-growth figure: upkeep oxygen is 0.149 mmol O2/g/h x 0.5 = 1.8 mmol/g/day (West's law, as in `Cells.qo2`), or 0.30 mmol glucose/g/day burned whole. Mayrhofer's feed carried about 69 mM glucose (12.5 g/L), so the flow is 0.30 / 69 = 4.3 mL/g/day, against 3.0-3.7 measured (INF). The flow floor is therefore a delivery limit on a 400 mOsm medium, not a property of the cell. A stronger feed lowers it in proportion.
- The measured flows are for cells growing at 0 to 0.15/day. Nobody has measured the flow of cells growing at 0.46-1.04/day, so the flow bound at those rates is carried over, not seen.

## Which binds

| Case | Binding limit |
|---|---|
| Stoichiometric (a, b) | none; both wastes can reach zero |
| Medium must be a bath | (c) salt budget: 14-25 L/kg |
| Concentrate dosed into the tank | (c) feed strength: 5.5 (the all-favourable example; the culture leaving with its cells, 6.4, binds above it), 6.4 (the low-lactate example); measured flow adds a little above that for the low-lactate example (8.0) |
| The model as it stands | the all-favourable example: ammonia, 10.8 (lactate 10.25 and the nutrient floor 8.0 sit below it); the low-lactate example: ammonia, 35; published cells: lactate, 136 per kilo grown |

## Judgements

The probabilities below are a rough judgement made while building the model with an AI assistant; not measured and not reviewed by an expert. The model does not use them.

| Event | Probability | Reasoning |
|---|---|---|
| Ammonia at or below 0.054 mol/kg is physically possible in a cell doubling in 30 h or less | about 90% | stoichiometry allows zero, and a GS CHO line is at 0.012 |
| Lactate yield at or below 0.16 is physically possible at that growth | about 95% | Warburg-null CHO and HEK grow with almost no lactate |
| A concentrate of 100 g/L or more can be dosed into a 20 m3 perfusion tank without hurting cells | about 80% | the tank, not the feed, sees the salt limit; tyrosine and cystine solubility is the known obstacle |
| A culture at 8 L/kg or less is physically possible | about 80% | the feed bound is 5.5-6.4 L/kg at 100 g/L |
| A culture at 6 L/kg or less is physically possible | about 60% | it needs a feed of 100 g/L or more and a leak of 1% or less |

These rest on a reading of a dozen papers and snippets, not on a survey of the field. The feed-strength figure and the salt floor (S) have no source and move the answer most.

## Sources

1. Humbird D (2021) Biotechnol Bioeng 118:3239, PMC8362201. Composition, nutrients, limits. FT-sum (EARLIER).
2. Mayrhofer et al. (2020) Biotechnol Prog 36:e2933, doi 10.1002/btpr.2933. 8-30 pL/cell/day, 400 mOsm target, ammonia below 30 mg/L. FT-sum (EARLIER).
3. Hubalek et al. (2023) Front Bioeng Biotechnol 11:1202165. Bovine FAP ammonia. FT-sum (EARLIER).
4. Hefzi et al. (2025) Nat Metab, PMC12272911. Warburg-null cells. FULL (EARLIER).
5. Clincke et al. (2013) Biotechnol Prog 29:754, PMC3752962. 50 pL/cell/day, 17 um cells. FULL (EARLIER).
6. Freund and Croughan (2018) Int J Mol Sci 19:385. Adapted CHO lactate yield. FT-sum (EARLIER).
7. Kilburn DG, Lilly MD, Webb FC (1969) J Cell Sci 4:645. ATP to build and keep a cell; read at https://bionumbers.hms.harvard.edu/bionumber.aspx?id=101985. PART.
8. GEN News, steady hyperosmotic conditions aid perfusion cell cultures (CHO-DG44, 380-410 mOsm/kg held, specific productivity +66%). PART.
9. Kamachi (2016, Takeda) conference abstract, CHO-S adapted to 450 mOsm, https://dc.engconfintl.org/cellculture_xv/80. SNIP.
10. Romanova et al. (2021) hyperosmolality in CHO fed-batch, 545 mOsm/kg. SNIP.
11. Manufacturing ultra-concentrated liquid feeds (cysteine and tyrosine solubility), https://pmc.ncbi.nlm.nih.gov/articles/PMC4685332/. SNIP (page blocked).
12. Alhuthali et al. (2021) Int J Mol Sci 22:3290; Zhu et al. (2005) Biotechnol Prog 21:70. Osmolality tolerance. FULL and AB (EARLIER).

## Not found

- A measured upper limit for the strength of a feed mixed into a perfusion tank, in g/L or mOsm/kg.
- How low the salts of a medium can go for meat cells, and any medium sheet to pin S.
- Measured protein or nucleotide turnover and its nitrogen leak in meat cells; any ammonia rate for a meat cell at a 24-36 h doubling.
- Medium flow per cell at growth above 0.15/day.
- The size of Kilburn's cells, which sets the ATP cross-check.
- Why `pf_glc_kg` (1.116 mol) and the feedstock glucose (1.78 mol) differ. (Settled on 2026-11-19 for the scenarios: the cells' own balance gives 1.74 mol with no lactate, and `pf_glc_kg` is no longer used by them; see `audit_2026-11-19.md`.)

## Bench work that would most narrow it

1. Feed strength: dose a 100-200 g/L amino-acid and glucose concentrate into a 1-2 L perfusion at 0.5/day growth and hold the tank under 415 mOsm/kg. Two to three weeks.
2. Mass balance on a meat line on glutamine-free medium: ammonia, alanine, lactate and glucose per kg of wet cells at a 30-36 h doubling. Six to eight weeks.
3. Salt floor: grow the line at 150, 200 and 250 mOsm/kg of salts, with sucrose or amino acids making up the tonicity. Two weeks.
