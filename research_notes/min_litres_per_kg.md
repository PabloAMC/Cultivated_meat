# The least medium per kg of cells that physics allows

> Names (2026-11-19): "Selected cells" was called Central; "Engineered cells, all favourable" was called the best case.

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50.
> Repinned 2026-11-19 (audit batch): ammonia tolerance 4 mM, lost runs pay for their membranes, glucose from the cells' balance (published cells need about 95 L/kg); see audit_2026-11-19.md.
> What this changed here: the floors did not move (5.8 and 6.4 L/kg). The model moved away from them: Best uses 13.75 L/kg (was 11.2)
> and Central 35 (was 28), both now set by ammonia. So Central is no longer within 10% of the bath bound; it is 1.4 times above it. At
> the scenarios' 4 mmol/L the ammonia that fits at the floor litres is 0.023 mol/kg, not 0.029. That figure and the leak table are my
> arithmetic: `min_litres.py` still divides by Humbird's 5 mmol/L (`pf_nh3_limit`) and prints 0.029. No cost in this note depends on it.

Recomputed 2026-11-16 on the current model (bubble protectant, antifoam's cost to oxygen transfer, bought oxygen in a yeast-style plant, dissolved oxygen held at half of air saturation, medium at least the culture that leaves with the cells).

Compiled 2026-11-15. Code: `min_litres.py` (bounds and costs), `tests/test_min_litres.py`. New inputs: `ml_*` in `inputs.py`. No default moved. Costs are 2025 dollars per kg of wet cells; every scenario is a 20 m3 stirred tank in perfusion with a TFF loop.

Access codes: **FULL** = full text read. **FT-sum** = full text read through a summariser. **PART** = a secondary page or article read, not the paper. **SNIP** = search snippet only. **INF** = my arithmetic. **RECALL** = from memory, no source read. Source access carried from `waste_and_medium_evidence.md`, `waste_tricks_sizing.md` and `perfusion_rate_osmolality.md` is marked EARLIER.

## Answer

1. Stoichiometry sets no floor. Nitrogen, carbon and energy balances all allow zero ammonia and zero lactate, so waste can fall to 0 L/kg. Warburg-null CHO and HEK show it for lactate (FULL); a glutamine-synthetase CHO line comes within 0.4% of zero for ammonia (INF from FT-sum).
2. Delivering the nutrients sets the floor. A kg of cells eats 0.58 kg (Best) to 0.64 kg (Central) of amino acids and glucose, 3.8-4.2 mol. The litres follow from how strong the feed can be:

| Feed | Best (24 h, 3 ng) | Selected cells (36 h, 2 ng) |
|---|---|---|
| The medium is what the cells sit in, at the salt limit, typical salts (250 mOsm/kg) | 23.1 L/kg | 25.1 L/kg |
| Same, salts cut to 150 | 14.4 | 15.7 |
| A concentrate of 50 g/L, diluted in the tank | 11.6 | 12.8 |
| A concentrate of 100 g/L (default) | **5.8** | **6.4** |
| A concentrate of 200 g/L | 2.9 | 3.2 |
| Lowest measured flow per cell (3.7 mL/g/day) over the growth rate | 5.3 | 8.0 |

3. Reading: if the medium must be iso-osmotic with the cells, as pharma perfusion media are, the floor is 14-25 L/kg. Central's 35 is 1.4 times the top of that range (it was within 10% of it at 28), and Best's 13.75 is still below the bottom of it. If a concentrate can be dosed into the tank, the floor is about 6-8 L/kg, and Best sits 2.4 times above it and Central 4.4-5.5 times. I put the physical floor at **5.8 L/kg (Best) and 6.4 L/kg (Central)**, and the floor that respects measured flows at 5.8 and 8.0.

## Where the model sits

| | Best | Selected cells | Floor |
|---|---|---|---|
| Litres per kg | 13.75 (ammonia 13.75, lactate 11.2, least flow 10.8) | 35.0 (ammonia; lactate 21.5) | 5.8 / 6.4 |
| Ammonia, mol/kg | 0.055 (1.9% of the cell's nitrogen) | 0.14 (4.9%) | 0; at the floor litres, 0.023 (0.8%) fits at 4 mmol/L |
| Lactate, mol per mol of all glucose taken up | 0.279 (0.56 mol/kg) | 0.42 (1.07 mol/kg) | 0; at the floor litres, 0.29 mol/kg fits, a yield of 0.15 |
| Least flow, mL/g/day | 7.5 | 7.5 | 3.7 measured (zero growth) |
| Doubling time | 24 h | 36 h | |

Both scenarios' litres are now set by ammonia alone, at the 4 mmol/L the scenarios' cells tolerate (5 before the audit batch, when lactate, ammonia and the least flow tied near 11 L/kg in Best). With zero waste and the default flow Central would need 16.2 L/kg, set by the 7.5 mL/g/day flow at a 36 h doubling. At 3.7 mL/g/day the model's own 8 L/kg nutrient floor binds. The published cells sit far above all of this: 95.5 L/kg, set by lactate (4.8 mol/kg at a yield of 1.05 on 4.5 mol of glucose).

## Cost at the bounds

`explore(medium_l=...)` with each scenario's other settings held. Scenario costs as they stand: Best $11.46, Central $32.80.

| Litres per kg | Best | Selected cells |
|---|---|---|
| Bath, typical salts (23.1 / 25.1) | $15.86 | $25.87 |
| Zero waste, default flow (10.8 / 16.2) | $10.07 | $20.13 |
| Model's litres (13.75 / 35.0) | $11.46 | $32.80 |
| Physical floor, 100 g/L feed (5.8 / 6.4) | $7.70 | $14.16 |
| Lowest measured flow (5.3 / 8.0) | $7.49 | $15.13 |
| Zero waste, lowest measured flow, model floor of 8 L/kg | $8.74 | $15.13 |

Best gains $3.75 at its floor (it was $2.33). Central gains $17.67 at 8 L/kg (it was $11.48), mostly in the filter loop ($12.79 of membranes to $1.19) and the medium ($7.15 to $2.95 of feedstock: below about 22 L/kg the $0.20 complete medium is charged its nutrients plus its growth factors). Central at 11 L/kg costs $16.95 (INF, same call). A bath of typical salts would now cost Central less than its own litres ($25.87 against $32.80); before the audit batch the two were within $2. The costs at the bounds rose by $0.05 to $1.27, because a lost run now throws its filter membranes away early. These costs assume the waste fits in the litres; at 5.8 L/kg that needs ammonia at or below 0.023 mol/kg and lactate at or below 0.29 mol/kg.

## The four bounds

### (a) Nitrogen balance

- A kg of cells holds 0.21 x 13.6 = **2.86 mol N** (Humbird's CH1.68 O0.34 N0.21, EARLIER). A protein-only count gives about 2.2 (195 g protein at 16% N), and nucleic acids add about 0.2 (INF).
- Amino acids supplied in the proportion the cell builds protein deliver that nitrogen without freeing ammonia: the nitrogen moves by transamination. Humbird's 0.26 kg of pure amino acids is 0.26 x 1000 / 128 = 2.03 mol; at 1.4 N each that is 2.86 mol, so the figures agree (INF).
- Protein turnover returns its amino acids to the pool. Purine and pyrimidine turnover is mostly salvaged (RECALL), and glutamine amide transfers release glutamate, not ammonia. I found no stoichiometric step that forces ammonia out. **Floor: 0 mol/kg, 0 L/kg.** I could not source a measured protein or nucleotide turnover rate for cultured meat cells; a search for the median protein half-life did not confirm any number (SNIP).
- The free parameter is the leak: the share of the 2.86 mol that leaves as ammonia. Litres = leak x 2.86 / 0.004 = **714 L/kg per unit leak** at the 4 mmol/L the scenarios' cells tolerate (572 at the 5 mmol/L used before the audit batch).

| Leak | mol/kg | L/kg at 4 mM | Source |
|---|---|---|---|
| 0.4% | 0.012 | 3.0 | CHO GS perfusion plateau, 0.54 fmol/cell/h taken to 0.35/day (range 0.0063-0.029). Mayrhofer 2020, FT-sum; extrapolation INF |
| 0.8% | 0.023 | 5.8 | what the floor litres allow |
| 1.9% | 0.055 | 13.75 | Best |
| 3.2% | 0.09 | 22.5 | bovine FAPs, shaker flask (Hubalek 2023, FT-sum) |
| 4.9% | 0.14 | 35 | Selected cells; bovine FAPs on alpha-ketoglutarate or pyruvate, at most (Hubalek 2023) |
| 24.5% | 0.70 | 175 | bovine FAPs, spinner, with glutamine (Hubalek 2023) |

Ammonia does not bind at the floor. It binds in Central (35 L/kg) because those cells leak 4.9%, and now in Best too (13.75 L/kg at a 1.9% leak). Best's leak is 2.6 times less than Central's; the one measured CHO line is 4.6 times below Best's. The floor litres now ask for a leak 2.4 times below Best's (it was 1.9 times at 5 mmol/L).

### (b) Carbon and energy balance

- **Lactate.** Glucose burned whole gives CO2 and no lactate, so the floor yield is zero. Hefzi et al. 2025 (Nat Metab, PMC12272911, FULL) report Warburg-null CHO-S, CHO-K1 and HEK293 with peak lactate sub-mM to single mM against 13-135 mM in wild type, growth "comparable to WT", but the rates sit in figures I could not read. Adapted CHO reached 0.39 mol/mol (Freund and Croughan 2018, EARLIER). Glucose per kg: the model's feedstock count gives 0.32 kg/kg = 1.78 mol at 24 h (Central 2.12). `pf_glc_kg` gives 1.116 mol; the two differ by 1.6 times, and I used the feedstock figure. Since 2026-11-19 the scenarios take glucose from the cells' own balance (`floor_physics.glucose_balance`): 1.74 mol (Best) and 2.07 (Central) with no lactate, within 2% of the feedstock figure, and 2.00 and 2.56 with the scenarios' lactate. So the feedstock figure was the right one, and `pf_glc_kg` no longer enters the scenarios. **Floor 0 L/kg.** At the 50 mM limit, 0.29 mol of lactate per kg fits the 5.8 L/kg floor. That is a yield of 0.16 on the glucose of a cell that makes no lactate, or 0.15 per mol of all the glucose taken up, the basis the scenarios now use (Best assumes 0.279, Central 0.42).
- **CO2.** The model burns 5.16 mol O2/kg (Best) and 7.14 (Central) and makes 6.2 and 8.6 mol CO2 at an RQ of 1.204. Kilburn et al. 1969 measured mouse fibroblasts at 1.6e-11 mol ATP per cell to build and 2.9e-11 per new cell for upkeep at a 27.6 h generation (PART: BioNumbers page, secondary). At 3 ng per cell and 5 ATP per O2 that is 13.7 mol ATP/kg against the model's 25.8 (Best, ratio 1.9) and 26.9 against 35.7 (Central, 1.3) (INF; the fibroblast's size is not on that page, so the ratio is good to a factor of 2). Burning glucose whole for Kilburn's ATP takes 0.43 mol glucose. CO2 could fall to about 3 mol/kg. It reaches the litres only through bicarbonate salt: 12.7 mOsm at 100 mbar and pH 7.2, nothing below about 80 mbar. **It does not bind.**

### (c) Osmolality budget

- Nutrients per kg: 2.03 mol amino acids + 1.78 mol glucose = **3.81 mol** (Best); 4.15 (Central). Each is about one osmole per mole (INF).
- If the medium is what the cells sit in: litres = 3.81 / ((415 - S) / 1000). S is the salt and buffer osmolality, 250 in a conventional medium (RECALL: about 100 mM NaCl, 25 mM bicarbonate; no sheet read). Result: **23.1 L/kg** at S = 250, 17.7 at 200, 14.4 at 150. Best's 13.75 L/kg would need a nutrient budget of 277 mOsm, so S <= 138. That is below the 150 I take as the low end for salts (at 11.2 L/kg, before the audit batch, it needed S <= 74).
- Check against practice: Mayrhofer et al. 2020 (FT-sum) ran perfusion media to a 400 mOsm/kg target and held 14-30 pL/cell/day at 0.15/day growth, which `waste_and_medium_evidence.md` converts to 31-67 L/kg. My bath bound of 25 L/kg at full growth sits below that, as a bound should.
- The salt limit does not apply to the feed if the feed is a concentrate diluted in the tank. The tank sees salts plus residual nutrient plus the waste salts (2 mOsm per mmol/L of lactate), and consumption removes the nutrient osmoles. The model's tank budget is already in `explore` (Best's tank is at 394 of 415 mOsm/kg; the published cells' tank is at 412.7). Then the feed is limited by what dissolves: litres = 0.58 kg / feed strength. At 100 g/L that is **5.8 L/kg** (Central 6.4). Tyrosine and cystine are the known solubility limit in concentrated feeds, and ultra-concentrated feeds have been made (SNIP: PMC4685332, page blocked). I found no number for the strongest feed, so 50-200 g/L is my judgement, and the 100 g/L default carries most of the uncertainty. Single-strength media carry roughly 10-30 g/L of these (RECALL).
- Cells can be made to grow at higher osmolality, which would raise the 415 limit: a CHO-S line adapted to 450 mOsm (Kamachi, conference abstract, SNIP) and constant 380-410 mOsm in CHO-DG44 perfusion with productivity up 66% (GEN News article, PART). Fed-batch CHO exposed to 545 mOsm/kg tripled in volume and stopped growing (Romanova 2021, SNIP). I did not carry this into the bound.
- If glucose is 1.116 mol/kg rather than 1.78, the bath bound is 19.1 and the feed bound 4.6 L/kg (Best).

### (d) Least perfusion flow per cell

- Model: `pf_min_perfusion` = 7.5 mL/g/day. Litres = flow / growth rate in 1/day: Best 10.8, Central 16.2.
- Measured, CHO (EARLIER, `perfusion_rate_osmolality.md`): 3.7 mL/g/day at 8-10 pL/cell/day with no net growth (Mayrhofer 2020, FT); 5.2-11 at 14-30 pL while growing at 0.15/day; 18.5 at 50 pL (Clincke 2013, FULL). At 3.7: Best 5.3, Central 8.0.
- Physics for the zero-growth figure: upkeep oxygen is 0.149 mmol O2/g/h x 0.5 = 1.8 mmol/g/day (West's law, as in `Cells.qo2`), or 0.30 mmol glucose/g/day burned whole. Mayrhofer's feed carried about 69 mM glucose (12.5 g/L), so the flow is 0.30 / 69 = 4.3 mL/g/day, against 3.0-3.7 measured (INF). The flow floor is therefore a delivery limit on a 400 mOsm medium, not a property of the cell. A stronger feed lowers it in proportion.
- The measured flows are for cells growing at 0 to 0.15/day. Nobody has measured the flow of cells growing at 0.46-0.69/day, so the flow bound at those rates is carried over, not seen.

## Which binds

| Case | Binding limit |
|---|---|
| Stoichiometric (a, b) | none; both wastes can reach zero |
| Medium must be a bath | (c) salt budget: 14-25 L/kg |
| Concentrate dosed into the tank | (c) feed strength: 5.8 (Best), 6.4 (Selected cells); measured flow adds a little above that for Selected cells (8.0) |
| The model as it stands | Best: ammonia, 13.75 (lactate 11.2 and flow 10.8 sit below it); Selected cells: ammonia, 35; published cells: lactate, 95.5 |

## Calibrated odds (my judgement)

| Event | Probability |
|---|---|
| Ammonia at or below 0.055 mol/kg is physically possible in a cell doubling in 30 h or less | 92% |
| A meat-relevant line shows it in a peer-reviewed report by 2030 | 30% |
| Lactate yield at or below 0.16 is physically possible at that growth | 95% |
| A meat-relevant line shows it by 2030 | 40% |
| A concentrate of 100 g/L or more can be dosed into a 20 m3 perfusion tank without hurting cells | 80% |
| Someone shows it with cells at 20 m3 by 2030 | 15% |
| A culture at 8 L/kg or less is physically possible | 80% |
| A culture at 6 L/kg or less is physically possible | 60% |
| A meat-cell process reports 11 L/kg or less by 2030 | 10% |
| Selected cells' 28 L/kg is within a factor of 2 of the best process reported by 2030 | 50% |

The last row was judged when Central used 28 L/kg. At 35 L/kg the same row asks for a best reported process at 17.5 L/kg or more, not 14, so its odds are if anything a little lower. I have not re-judged it. The other rows do not depend on the model's litres.

These odds rest on my reading of a dozen papers and snippets, not on a survey of the field. The feed-strength figure and the salt floor (S) have no source and move the answer most.

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
