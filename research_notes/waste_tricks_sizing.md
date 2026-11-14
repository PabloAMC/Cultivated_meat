# Sizing three tricks against ammonia and lactate: sorbent loop, low-ammonia cells, feeding control

Compiled 2026-11-14. Companion to `waste_and_medium_evidence.md` (same conventions). Nothing was measured here. Every conversion is shown. A number marked **from memory** is not from a source I opened this session.

## Basis (fixed by the brief)

- 120 g wet cells per litre, doubling every 24 h (mu = 0.693 per day), cell-free permeate, limits 5 mM NH3 and 50 mM lactate (30 mM as the cautious case).
- Floor of 11 L medium per kg wet cells needs ammonia excretion E <= 11 L x 5 mM = **0.055 mol/kg** (and lactate <= 0.55 mol/kg at 50 mM, 0.33 mol/kg at 30 mM).
- Cell mass for per-cell to per-kg conversions: 3000 pg wet per cell, so 1 kg = 3.333e11 cells (Humbird's figure, as in the earlier note).
- Nitrogen assimilated, 2.2 mol/kg (brief's estimate). Fraction allowed to leave as NH3 at the floor: 0.055/2.2 = 2.5%, so 97.5% must end in biomass or harmless products. Bovine FAP spinner 0.70/2.2 = 32% leaves as NH3; with glutamine replaced, 0.14/2.2 = 6.4%.

Access codes: **FULL** = full text opened and searched by me. **ABS** = abstract (PubMed record) only. **SNIP** = search-result snippet only. **PAT** = patent full text. **CITED** = taken from a paper I read. **EARLIER** = carried from `waste_and_medium_evidence.md`, not re-opened. **INF** = my arithmetic.

---

## Trick A. Take ammonium out of the cell-free permeate with a sorbent and return the permeate

### A1. Sourced numbers

| Item | Value | Conditions | Source, access |
|---|---|---|---|
| Hybridoma perfusion with zeolite A-3 bed on cell-free permeate | NH3 held at 1-4 mM; 1e7 cells/mL, viability above serum cultures | Serum-free, spinner flasks, ceramic cross-flow filter, bench | Nayve et al. 1991, Cytotechnology 6:121, PMID 1369336. ABS |
| Same group, with medium supplementation | Peak viable density 2.5e7 cells/mL, over 300% above ordinary perfusion; antibody about 10-fold | As above | Nayve et al. 1994, J Biotechnol, PMID 7764955. ABS |
| Clinoptilolite column vs hollow-fibre gas module on used hybridoma medium | "Better cell growth, but not a better specific antibody secretion"; no numbers in the abstract | Hybridoma, used medium passed through clinoptilolite | Capiaumont et al. 1995, J Biotechnol 39:49, PMID 7766010. ABS |
| Jeong and Wang, zeolite (phillipsite-gismondine) in alginate beads or dialysis membrane | Ammonium inhibits growth and MAb; in-situ removal described. No numbers retrieved | Hybridoma | KSBB J 1996 record. SNIP |
| Zeolite on spent cultivated-meat medium (lamb satellite cells) | 5 and 20 g/L natural zeolite, 1 and 4 days: ammonium "significantly decreased", dose-dependent; glucose unchanged. Percentages are in figures only | Spent medium at about 1.2 mM NH4+; room temperature, shaken | Pakbin et al. 2025, Front Bioeng Biotechnol 13:1617115. FULL (figures not readable) |
| Zeolite and Prussian blue in culture solutions, maximum NH3 removal | 60% and 10% | Aqueous/culture solutions | Kameda et al. 2021, Colloids Surf A 622:126595, via Pakbin. CITED |
| Pakbin's own statement on competing ions | Mg, K, Ca, Na in medium "competitively adsorbed", zeolite efficiency "significantly reduced"; zirconium phosphate, resin, activated carbon named as alternatives (no data) | - | Pakbin 2025 citing Yang 2023 and Kameda 2021. FULL |
| Tohoku/Nikkiso sorbents in a stem-cell medium | L-type zeolite, ferrierite, ZSM-5, H-form strong-acid resin, Prussian blue; start 10 mM NH4+, 0.0005-0.2 g/mL, 37 C, 24 h; ammonia adsorption higher than glucose adsorption at all doses; glucose loss up to 32%; per-gram capacity only in figures | StemFit AK02N | US 2021/0178359 A1. PAT |
| Zirconium phosphate (ZrP), commercial amorphous "BZS" control, in dialysate | **17.5-25 mg NH4-N/g = 1.25-1.78 mmol/g** (INF, /14.007) | Feed 100 mg/dL NH4-N = **71 mM**; background 105 mEq/L NaCl + 35 mEq/L NaHCO3 (140 mM Na) | US 8,640,887 B2, Table 4J. PAT. Not 1-5 mM |
| Same patent, sol-gel ZrP | 45-49 mg N/g in the "water" test (higher than dialysate test); 20-25 in dialysate | as above | Same. PAT |
| alpha-Na2-ZrP maximum NH4+ uptake | 5.5 mmol/g, "close to the theoretical limit of exchangeable sites" | Lab maximum, not a competing-ion test | Langmuir-type paper on encapsulated crystalline ZrP, abstract. SNIP |
| ZrP in presence of Ca2+ and other cations | Selectivity "limited in the presence of competing ions"; Ca2+, Mg2+, K+ uptake consumes more of the cartridge capacity than NH4+ from urea; a perfluorocarbon coating raised NH4+/Ca2+ selectivity (about 4-fold) | Dialysis oral-sorbent papers | Langmuir 2024; PMC10249412; PubMed 35786968. SNIP |
| Clinoptilolite selectivity order | Ames: Cs > Rb > K > NH4 > Ba > Sr > Na > Ca > Fe > Al > Mg > Li. Dryden and Weatherley 1987 at 0.01 N: K > NH4 > Na > Ca > Mg | Aqueous | SNIP of review text. Source dependent |
| Clinoptilolite NH4/Na exchange | Standard free energy about **-0.7 kcal/mol** NH4 for Na at 0.05 M ionic strength (Fort LaClede deposit) | Aqueous | Clays and Clay Minerals paper, snippet. SNIP |
| Clinoptilolite total capacity | 1.6 meq/g (vendor, "theoretical"); about 2.25 meq/g (review); fitted maxima 15.7 mg NH4+/g (0.87 mmol/g) in a Bioengineered 2022 study and 20-30 mg/g in a thesis | Pure ammonium solutions | SNIP. Secondary |
| Clinoptilolite at low concentration | 1-10 mg/L feed gave 65-86% removal; packed-bed capacity about 0.5 mg NH4+/g (0.03 mmol/g) | Water | Vendor page. SNIP, weak |
| Strong-acid cation resin selectivity (AG 50W-X8) | K+ = 2.5 relative to H+ = 1.0 confirmed; Na+ 1.5 and NH4+ 1.95 appeared in the extracted table but labels were garbled | Aqueous | Bio-Rad manual, search extract. SNIP. Na and NH4 values **from memory** |
| Regeneration, clinoptilolite | Best: 20 g/L NaCl (0.34 M) with 0.1 M NaOH; loaded material 8.1-16.6 mg NH4+/g; cycles not reported in what I saw | Wastewater sludge liquor | Wasielewski et al. 2022, Nanomaterials 12:525. ABS/SNIP |
| Natural zeolite price | **USD 50-300 per metric ton** (all natural zeolites, all grades); average unit value about USD 200/t in 2024 | Bulk, mostly construction and agriculture | USGS Mineral Commodity Summaries 2026. FULL (PDF opened) |
| Price of sterile, medium-grade zeolite, cation resin or ZrP | **Not found.** Placeholders below are my assumptions, not data | - | - |

**Not found:** any ammonium capacity (mmol/g) measured at 1-5 mM NH4+ in 110-150 mM Na, 4-5 mM K at pH 7-7.4, for any sorbent. Any measured selectivity coefficient of ZrP or resin for NH4 over Na, K, Ca, Mg in that background. Any measurement of lysine, arginine, histidine, growth factor or trace metal uptake by a sorbent in medium. The 1990s hybridoma papers are only available to me as abstracts, so I could not read how much of the benefit was ammonia removal vs. nutrient supplementation (Nayve 1994 combined both). No CHO or cultivated-meat perfusion with a sorbent loop. No regeneration cycle count in medium. No price of ZrP or resin.

### A2. Capacity in the real background (my derivation, not measurement)

Mass-action ion exchange with Na as reference, equivalent fraction of exchanger carrying NH4:
y = K x [NH4] / (140 + K x [NH4]), capacity q = y x Q (Q = total exchange capacity). Feed [NH4] is what the permeate carries (the loop must hold 1-5 mM). Potassium and divalents ignored unless stated, so these are upper bounds.

- Clinoptilolite: K_NH4/Na = exp(0.7/RT) = 3.1 at 37 C (3.3 at 25 C), from the -0.7 kcal/mol snippet (aqueous, 0.05 M; assumed to hold at 0.14 M). Q = 1.6-2.25 meq/g.
- ZrP: no measured K. Back-calculated from the patent test: 71 mM NH4 in 140 mM Na gives 1.25-1.78 mmol/g; if Q = 5.5 mmol/g then y = 0.23-0.33 and K_app = [y/(1-y)]/(71.4/140) = **0.6-0.9**. This assumes the patent's ZrP has Q about 5.5 mmol/g; if its Q is larger, K_app is smaller. Taken at face value, the dialysis ZrP does not prefer NH4 over Na.
- Strong-acid resin: K = 1.95/1.5 = 1.3 (**from memory**), Q = 4.8 meq/g dry (**from memory**).

| Sorbent | q at 1 mM NH4 | q at 3 mM | q at 5 mM |
|---|---|---|---|
| Clinoptilolite (Q 1.6-2.25, K 3.1-3.2) | 0.04-0.05 mmol/g | 0.10-0.14 | 0.16-0.23 |
| Same, with K+ 4.5 mM at twice NH4 selectivity (assumption) | - | - | 0.14-0.20 |
| ZrP (Q 5.5, K_app 0.6-0.9) | 0.02-0.04 | 0.07-0.11 | 0.12-0.18 |
| Cation resin (Q 4.8, K 1.3, memory) | 0.04 | 0.13 | 0.21 |

All three land at about **0.1-0.2 mmol/g** at a 3-5 mM feed, 10 to 50 times below the pure-solution capacities (0.9-5.5 mmol/g), because Na is 28-140 times more abundant than NH4. The arithmetic only changes if a sorbent has K_NH4/Na of order 10 or more: to reach 1 mmol/g from Q = 5.5 at a 5 mM feed needs K = (0.18/0.82) x 140/5 = **6.1**; 2 mmol/g needs K about 15. No source shows such a sorbent in medium. Design values used below: **q = 0.10, 0.15, 0.25 mmol/g**. Divalent ions (Ca 1.8 plus Mg 0.8 mM, **from memory** of typical media) would take more capacity on resin and ZrP, which prefer them; clinoptilolite prefers NH4 over Ca and Mg (Ames order), so it is the least affected.

### A3. Sizing

Ammonia to be removed by the sorbent per kg wet cells = E - 0.055 (the 11 L of permeate already carries 0.055 mol at 5 mM):

- E = 0.14 mol/kg: excess 0.085 mol (1.5x the allowance)
- E = 0.70 mol/kg: excess 0.645 mol (11.7x the allowance)

Sorbent mass per kg wet cells = excess (mol) / q (mol/kg), single use:

| q (mmol/g) | E = 0.14 | E = 0.70 |
|---|---|---|
| 0.25 | 0.085/0.25 = **0.34 kg** | 0.645/0.25 = **2.6 kg** |
| 0.15 | **0.57 kg** | **4.3 kg** |
| 0.10 | **0.85 kg** | **6.5 kg** |

Per kg of cells, at 120 g/L that is 0.34-0.85 kg sorbent per 8.3 L of culture (E = 0.14), or 2.6-6.5 kg per 8.3 L (E = 0.70), so at E = 0.70 the sorbent outweighs the cells by 20-50 times.

Cost per kg cells = mass x price. Price is the missing number; bulk zeolite is USD 0.05-0.30/kg (USGS), a sterile, endotoxin-controlled, medium-grade material will cost more. Assumptions marked A:

| Price assumption | E = 0.14 (0.34-0.85 kg) | E = 0.70 (2.6-6.5 kg) |
|---|---|---|
| USD 0.05/kg (USGS low, bulk, unsterile) | 0.02-0.04 | 0.13-0.32 |
| USD 0.30/kg (USGS high) | 0.10-0.26 | 0.77-1.9 |
| USD 5/kg (A, graded and sterilised) | 1.7-4.3 | 13-32 |
| USD 20/kg (A, resin or ZrP medical grade) | 6.8-17 | 52-129 |
| Break-even price for USD 1 per kg cells | 1.2-2.9 USD/kg | 0.16-0.39 USD/kg |

**Regenerated.** Sorbent cost per kg cells divides by the number of cycles N, plus regenerant. Regenerant arithmetic: each exchanged mole needs at least 1 mol Na; I assume 10x excess (A). NaCl at 0.34 M (the Wasielewski optimum) at 10x: E = 0.14, 0.85 mol Na = 50 g NaCl in 2.5 L brine per kg cells; E = 0.70, 6.45 mol = 377 g NaCl in 19 L brine per kg cells. Salt is cheap (USD 0.04 at 0.1 USD/kg); the brine volume (2.5-19 L/kg) is the same order as the medium itself, and the ammonium-laden brine must be disposed of. Sorbent cost with N = 50 and the USD 5/kg assumption: E = 0.14, 0.03-0.09; E = 0.70, 0.26-0.65 USD/kg cells. With USD 20/kg: 0.14-0.34 and 1.0-2.6. No cycle count in medium was found; fouling by protein and sterilisation between cycles are untested, so N = 50 is a hope, not a number.

**What must be added back (INF unless stated).**

- **Sodium rises (it is the counter-ion).** Na gained = NH4 removed spread over the fresh-medium flow: E = 0.14, 0.085 mol/11 L = **+7.7 mM**; E = 0.70, 0.645/11 = **+59 mM** (about 59 extra mOsm/kg; the earlier note puts CHO growth halving at 430-465 mOsm/kg, and 10% loss at about 345). So for E = 0.70 the loop is osmolality-limited as well as mass-limited unless the base medium is made low in Na. Alternatively the H-form releases protons and strips 10-35 mmol/L Na (dialysis patent text, SNIP), which needs pH control.
- **Divalents.** If a resin or ZrP took all Ca and Mg in 11 L: 2.6 mM x 11 L = 28.6 mmol (57 meq) per kg cells, 0.67x the 85 meq of ammonia excess even at E = 0.14. Whether they do is unmeasured. Replacement is easy (salts) if the loss is known.
- **Basic amino acids.** Lys + Arg at about 1.2 mM (**from memory**, DMEM-like) x 11 L = 13 mmol/kg per pass. If a resin or ZrP captured them like NH4, the loss would be of order 13 mmol per pass out of 85 mmol exchanged. Size exclusion would protect a zeolite (pores about 0.4 nm, **from memory**), not a resin or ZrP. No measurement found.
- **Growth factors.** FGF2 is cationic (**from memory**, pI about 9.6) but a zeolite bed excludes proteins by size; resin and ZrP not shown. No measurement found. Growth factor retention by the retention device is a separate unknown (earlier note).
- **Trace metals (Zn, Cu, Fe, Mn).** Transition metals are strongly bound by ZrP and resins (**from memory**); no medium data. Re-dosing is cheap in mass but must be controlled.
- **Glucose.** Nikkiso patent: up to 32% adsorbed at high dose of their sorbents; Pakbin: no zeolite effect on glucose.

### A4. Verdict, Trick A

- **Settled by calculation:** at 140 mM Na and 3-5 mM NH4, any exchanger with a selectivity near the measured or assumed 0.6-3 loads only 0.1-0.2 mmol/g, so the loop needs 0.34-0.85 kg sorbent per kg cells at E = 0.14 (about USD 0.02-4 per kg single use depending on grade) and 2.6-6.5 kg at E = 0.70 (USD 0.13-129), and E = 0.70 also adds about 59 mM Na.
- **Settled by literature:** zeolite in a permeate loop kept hybridoma ammonia at 1-4 mM and raised density 3-fold (abstracts, 1991 and 1994), and clinoptilolite improved growth in a second hybridoma study (abstract); no capacity, selectivity, amino acid or growth factor loss, regeneration cycle count or price was found in medium.
- **Only a bench test can tell:** capacity at 1-5 mM NH4 in the real medium (a 24 h batch isotherm, 4-6 sorbents), loss of Lys, Arg, His, FGF2, trace metals and vitamins across the bed, growth in treated-and-blended medium, and sorbent life over 20+ regenerations.

---

## Trick B. Make the cells excrete nitrogen harmlessly, or not at all

### B1. Sourced numbers

| Cell, condition | Quantity | Value | Source, access |
|---|---|---|---|
| Bovine FAPs, spinner, GlutaMAX (Ala-Gln) 2 mM, 17 mM glucose | qAmm; DT | 56.3 +/- 17.3 fmol/cell/h; 25.7 +/- 1.7 h (mu = 0.693/25.7 = 0.0270 per h = **0.65 per day**) | Hubalek 2023, Front Bioeng Biotechnol 11:1202165. FULL |
| Same, orbital shaker, proliferation medium | qAmm with GlutaMAX; with aKG, Pyr, Glt | about 5 fmol/cell/h; replacement substrates "did not" produce ammonia | Hubalek 2023. FULL. 10-fold disagreement with spinner unexplained |
| Same, five donors, planar, DT | GlutaMAX control | 38.0 +/- 9.1 h (mu 0.44 per day) | Hubalek 2023. FULL |
| Same, GlutaMAX replaced by 10 mM aKG / Pyr / Glt | DT | 42.9 +/- 4.4 / 47.6 +/- 6.8 / 48.8 +/- 13.9 h (mu **0.39 / 0.35 / 0.34 per day**); ammonia production rate "reduced more than 5-fold" (abstract) | Hubalek 2023. FULL. Significance of DT change not established at n = 5 |
| Same | Ammonia threshold | proliferation inhibited above 5 mM, adipogenesis from 2 mM | Hubalek 2023. FULL |
| Hubalek intro | Ammonium forces alanine excretion for detoxification (cites Martinelle and Haggstrom 1993; Schneider 1996) | no numbers | Hubalek 2023 text. FULL |
| GS-expressing CHO, glutamine-free vs with glutamine | "Production of ammonia was greatly decreased"; recombinant protein +18%; no numbers in the retrievable text | - | Zhang et al. 2006, Cytotechnology (PMC3449477). ABS (rest not retrievable as text) |
| CHO-K1 dynamic flux, 0-8 mM Gln | Ammonia, alanine and glutamate excretion "increased with increasing glutamine concentration"; rates in figures only | batch and fed-batch | Wahrheit et al. 2013, BMC Proc 7(S6):P44 (PMC3980355 record). FULL (text only, no rates) |
| MDCK, BHK21, CHO-K1, serum and serum-free | 2 mM Gln replaced by 10 mM pyruvate: growth "without reduction in growth rate", 19 passages; MDCK grew with 1 mM pyruvate "without accumulation of ammonia"; lower glucose uptake and lactate | no rates, no per-cell numbers | Genzel et al. 2005, Biotechnol Prog, PMID 15903241. ABS |
| Hybridoma, glutamate for glutamine | Medium ammonia lower; no per-cell numbers | - | Capiaumont 1995. ABS |
| CHO-K1 GS perfusion, optimised medium, 1 vvd, 130e6 cells/mL | Bioreactor ammonia "below 30 mg/L" | 30 mg/L as NH4+ = 30/18.04 = 1.66 mM. qNH4 <= 1.66 mM x 1 L/d / 1.3e11 cells = 1.3e-14 mol/cell/d = **13 fmol/cell/d = 0.54 fmol/cell/h** (upper bound; plateau, mu about 0) | Mayrhofer et al. 2020, Biotechnol Prog 36:e2933. EARLIER (FT-sum) |
| GS-CHO clones | qNH4 rises with MSX selection stringency; units umol/1e6 cells/h; values in tables I did not extract | - | Sci Rep 2018, PMC5876325. FULL text opened, table values not extracted |
| Chicken fibroblasts, perfusion | operated below 3 mM NH3; 2.4 g NH3 total in the run; basis (per kg? per run?) not established | - | Pasitka 2024, Nature Food 5:693. Paper is behind a paywall in this session; only abstract/snippets. EARLIER |
| Duck fibroblasts and myoblasts expressing GS | Patent describes ammonia with and without glutamine; no numbers retrieved | - | Patent 11,479,792 family. SNIP |
| Alanine as nitrogen sink | CHO under ammonia stress shift nitrogen to alanine; valine feeding led to alanine as the "primary mechanism" lowering ammonium. No concentration or rate retrieved | - | Search snippets of CHO ammonia-stress papers. SNIP |
| Alanine growth effect | Hybridoma: added alanine gave no improvement; alanine rescued starving hybridoma cells from apoptosis. **No inhibitory concentration found for any cell** | - | Patent text and a hybridoma paper. SNIP |

**Not found:** per-cell ammonia rate (with or without glutamine) in a GS-CHO, NS0 or HEK culture as a number. Any ammonia rate for porcine, fish, quail or insect-free chicken cells under glutamine-free conditions. Mol alanine excreted per mol glutamine or per kg of cells. Any alanine concentration that slows growth. Fastest growth in a low-ammonia run beyond the ones in the table.

### B2. Sizing against 0.055 mol/kg

Yield per kg = (specific rate, mol/cell/h) / (mu, per h) x 3.333e11 cells/kg. This assumes the rate was measured in exponentially growing cells (as Hubalek did).

| Case | mol NH3/kg | x requirement (0.055) | L/kg at 5 mM | mu (per day) | Status |
|---|---|---|---|---|---|
| FAP spinner, GlutaMAX | 56.3e-15/0.0270 x 3.333e11 = **0.70** | 12.7x | 140 | 0.65 | measured (Hubalek) |
| FAP shaker, GlutaMAX | 5e-15/0.0182 x 3.333e11 = **0.091** (DT 38 h); 0.062 if DT 25.7 h | 1.7x; 1.1x | 18; 12 | 0.44 | measured; conflicts with spinner |
| FAP, aKG replacement | "more than 5-fold" below 0.70, so **<= 0.14**; the shaker data says about 0 | <= 2.5x | <= 28 | 0.39 | bound from abstract |
| FAP, pyruvate | same bound, <= 0.14 | <= 2.5x | <= 28 | 0.35 | bound |
| CHO-K1 GS perfusion plateau | 0.54 fmol/cell/h; if the same per-cell rate held at mu 0.15 per day: 13.1e-15/0.15 x 3.333e11 = **0.029**; at 0.35: **0.012**; at 0.69: **0.0063** | 0.53x; 0.23x; 0.11x | 5.8; 2.5; 1.3 | 0.15 measured, others hypothetical | upper bound on plateau cells, extrapolated to growth without evidence |
| Pasitka chicken, 2.4 g NH3 = 0.141 mol | per what? | unknown | unknown | unknown | unresolved |

Reading, in plain words:

1. **The data that clears 0.055 is the CHO GS plateau rate (0.54 fmol/cell/h), which is 100 times below the bovine spinner rate and about 10 times below the bovine shaker rate.** But it is an upper bound from a stated ammonia ceiling, measured in cells that were not net-growing (mu about 0.15 per day for the run, 0 at plateau), and in a CHO line selected for ammonia handling. It cannot be extrapolated to a 24 h doubling because growth itself consumes amino acid nitrogen and its excretion pattern is not known.
2. **For a meat-relevant cell, the best measured low-ammonia case is bovine FAPs on aKG or pyruvate: about 0.14 mol/kg or less (up to 2.5x the requirement), at mu 0.35-0.39 per day (not 0.69).** In the shaker run the measured production was not positive, so the bound is conservative; but the same paper's spinner rate was 10x higher than its shaker rate, which no one has reconciled.
3. **Alanine is the cell's alternative sink.** If all of the nitrogen above the allowance left as alanine (1 N each) in 11 L: E = 0.14 gives 0.085/11 = **7.7 mM**; E = 0.70 gives 0.645/11 = **59 mM**. Allowed alanine at 10, 20 or 50 mM in 11 L is 0.11, 0.22 or 0.55 mol/kg, so a diversion of 0.085 mol is fine at any of those, and a diversion of 0.645 mol only fits if the threshold is above about 59 mM. I found no source on the threshold, so these three are placeholders. Alanine also costs carbon: each alanine made from glucose-derived pyruvate takes 0.5 mol glucose, so diverting 0.645 mol takes 0.32 mol glucose per kg (compared with 0.67-1.0 mol per kg total), which is a nutrient cost, not a waste cost.
4. **Nitrogen must be supplied as something.** Replacing glutamine with aKG or pyruvate removes the glutamine source but not the nitrogen demand (2.2 mol/kg). Where the nitrogen enters instead (other amino acids, glutamate formed from aKG plus ammonia recycling, or proteins in medium) is not shown by any source I read; in Hubalek, Gln accumulated in the pyruvate adipogenesis medium, which suggests the cells made glutamine themselves.

### B3. Verdict, Trick B

- **Settled by calculation:** 0.055 mol/kg is 2.5% of the 2.2 mol/kg of nitrogen taken up, and with glutamine replaced the best bovine bound is 6.4% (<= 0.14 mol/kg), so replacement alone is at most 2.5x short; a diversion to alanine of 0.085 mol/kg is only 7.7 mM in 11 L.
- **Settled by literature:** glutamine replacement cuts bovine FAP ammonia more than 5-fold with a 13-43% slower point estimate for doubling and no significance at n = 5; GS-CHO, pyruvate and glutamate substitutions lower ammonia in CHO, MDCK, BHK and hybridoma (abstracts, no rates); the fastest low-ammonia growth I can source is 0.39 per day, not 0.69; no alanine threshold and no per-cell GS-CHO numbers were found.
- **Only a bench test can tell:** ammonia, alanine and glutamate yields per kg of wet cells at a 24 h doubling in the actual line with glutamine replaced (one mass balance run), whether the 10-fold spinner-versus-shaker difference is real, and the alanine concentration that slows growth (a 0-60 mM dose-response).

---

## Trick C. No lactate by control of feeding

### C1. Sourced numbers

| Case | Lactate yield (mol/mol glucose) | mu (per day) | Source, access |
|---|---|---|---|
| CHO DG44 shake flask, control | 1.411 +/- 0.284; qLac 0.112 umol/1e6 cells/h | 0.027/h = **0.65** | Freund and Croughan 2018, Int J Mol Sci 19:385. EARLIER |
| Same, lactate-adapted | 0.388 +/- 0.344 | 0.025/h = **0.60** | same. EARLIER |
| Chicken fibroblasts (Pasitka), unmodified | 76 g per 145 g glucose = 0.844/0.805 = **1.05** | not found | Pasitka 2024. EARLIER, SNIP |
| HIPDOG (pH-triggered glucose feed), CHO fed-batch to 2,500 L | "dramatically reduce or eliminate lactate accumulation during the growth phase"; cells take up lactate when glucose is below about 1 mM; titre about doubled in 8 lines. **No yield, no mu given in the abstract** | not found | Gagnon et al. 2011, Biotechnol Bioeng 108:1328 (PMID 21328318). ABS |
| Glucose-limited CHO-K1 GS perfusion | Lactate production stopped after day 3, net consumption; yield not reported | about 0.15 | Mayrhofer 2020. EARLIER |
| Lactate-consuming states in CHO-S | Net lactate consumption after glutamine depletion in one line and in two of three media; "lactate production is typical for fast growing cells" | not given | Zagari et al. 2013, New Biotechnol (PMID 22683938). ABS |
| Warburg-null CHO-S, CHO-K1, HEK293 (Ldha plus Pdk1-4 knockouts) | Peak lactate sub-mM (clones 0-F4, 0-F5) to single mM (0-B6) vs **13-135 mM** in wild type or Warburg-positive; glucose uptake "drastically" reduced; oxygen uptake higher; growth "comparable to WT", also over 87 days of passaging; yield not given | Numbers only in a figure; WT CHO-S typically 0.7-1.0 per day (**from memory**) | Hefzi et al. 2025, Nat Metab (PMC12272911). FULL. **This is the peer-reviewed version of the bioRxiv preprint cited in the earlier note.** All cultures got 4-8 mM glutamine, so ammonia was not addressed |
| LDH-A knockdown plus Bcl-2, CHO | Specific lactate rate 21-65% and yield 37-78% of control; growth not impaired in LDH-A siRNA work | not given | Jeon et al. 2011. SNIP |
| Complete LDHA knockout with Pdk1-3 down-regulated | Lethal | - | Yip et al. 2014, Mol Biotechnol. SNIP. Superseded by Hefzi |
| Pyruvate carboxylase (yeast PYC2) in BHK-21, CHO-K1 | Less lactate, more glucose tolerance; effects of up to 70% lower lactate cited in related lines | not given | Irani et al. 1999, 2002; review. SNIP |
| Hybridoma, chemostat | Lactate yield falls with decreasing dilution rate (0.012-0.039 per h) | 0.29-0.94 per day (INF: 0.012-0.039 x 24), yield values not retrieved | Snippets of hybridoma and CHO chemostat papers. SNIP |

**Is there a report of yield under 0.1 mol/mol at growth above 0.5 per day?** The only candidate is the Warburg-null cell (lactate about 0 and growth "comparable to wild type", and wild-type CHO-S growth is about 0.7-1.0 per day from memory). I could not read the growth number or the yield from text, since both are plotted. For HIPDOG, glucose-limited perfusion and lactate-consuming states I found no yield and no growth rate above 0.5 per day. So: **probably yes, in Warburg-null cells, not confirmed by any number I could read.**

### C2. Sizing

Glucose per kg wet cells with the brief's range: 0.4-0.6 kg per kg dry x 0.30 kg dry per kg wet = 0.12-0.18 kg = 0.12/0.18016 to 0.18/0.18016 = **0.67-1.00 mol glucose per kg wet**. Cross-check: Freund's measured 1.38 mol lactate/kg at Y = 1.411 implies 0.98 mol glucose/kg, inside the range. Lactate per kg = Y x glucose. Litres = lactate / limit.

| Case | Y | mol lactate/kg | L/kg at 50 mM | L/kg at 30 mM | meets 11 L? |
|---|---|---|---|---|---|
| CHO control | 1.411 | 0.94-1.41 | 19-28 | 31-47 | no |
| Pasitka-type chicken | 1.05 | 0.70-1.05 | 14-21 | 23-35 | no |
| Adapted CHO | 0.388 | 0.26-0.39 | 5.2-7.8 | 8.6-13 | yes at 50 mM; borderline at 30 mM |
| Y = 0.2 | 0.2 | 0.13-0.20 | 2.7-4.0 | 4.4-6.7 | yes |
| Y = 0.1 | 0.1 | 0.067-0.10 | 1.3-2.0 | 2.2-3.3 | yes |
| Y = 0 (Warburg-null) | 0 | 0 | 0 | 0 | yes |

Maximum yield that still allows 11 L: 0.55/(0.67 to 1.0) = **0.55-0.82 at 50 mM**, 0.33/(0.67 to 1.0) = **0.33-0.50 at 30 mM**. So lactate does not need a yield under 0.1; it needs under about 0.5.

Caveat on the glucose range. It is an input from the brief and is consistent with measured CHO at Y = 1.4. But Humbird's wild-type cell (earlier note: 6.4 mol lactate/kg at Lac/Glc 1.77) implies 6.4/1.77 = 3.6 mol glucose/kg, 3.6-5.4 times higher; at that glucose use, Y = 1.41 would give 5.1 mol lactate/kg = 102 L/kg at 50 mM. Which glucose use applies to a real meat cell is unmeasured.

### C3. Verdict, Trick C

- **Settled by calculation:** with 0.67-1.0 mol glucose per kg wet cells, lactate stays within 11 L/kg for yields up to about 0.55-0.82 mol/mol at 50 mM (0.33-0.50 at 30 mM), so the lactate-adapted CHO yield of 0.39 already fits at 50 mM and nothing near zero is needed.
- **Settled by literature:** yields of 1.0-1.4 are normal at growth near 0.65 per day, adapted CHO reaches 0.39 at 0.60 per day, Warburg-null CHO and HEK show near-zero lactate with wild-type growth in a peer-reviewed paper (rates only in figures), and HIPDOG and glucose-limited perfusion are shown to switch cells to lactate consumption but without a stated yield or growth rate.
- **Only a bench test can tell:** the lactate yield and glucose use per kg wet in the actual meat line at a 24 h doubling under glucose-limited or pH-triggered feeding, and whether adaptation or knockout transfers to the line at all (nothing has been shown for bovine, chicken or fish cells).

---

## Which trick or combination gets closest to 11 L/kg, and what it costs

Requirement recap: NH3 <= 0.055 mol/kg, lactate <= 0.33-0.55 mol/kg. The question is which one binds.

1. **Lactate is the smaller problem.** Adapted-cell yields (0.39) and glucose-limited feeding put lactate inside 11 L at 50 mM and at the edge at 30 mM. This costs nothing in sorbent, though it needs adaptation or feed control and (unmeasured) may cost growth rate.
2. **Ammonia is the binding waste.** At 0.70 mol/kg, Trick A alone needs 2.6-6.5 kg of sorbent per kg cells, adds about 59 mM sodium, and is not credible. Trick B alone with glutamine replaced gives about 0.14 or less (<= 28 L/kg at 5 mM, 2.5x short) at mu 0.35-0.39 per day.
3. **Closest single trick: B (glutamine replaced), conditional on the measured bound.** On the one meat-relevant data set, it reaches at most 2.5x the requirement; on the CHO GS plateau figure, it would pass outright (0.006-0.029 mol/kg), but that is not shown at fast growth or in a meat cell.
4. **Closest combination: B plus C plus a small A.** Glutamine replacement (E <= 0.14) plus adapted or glucose-limited lactate (Y <= 0.4), plus a sorbent loop only for the leftover 0.085 mol/kg of ammonia. The sorbent need is 0.34-0.85 kg per kg cells at q = 0.10-0.25 mmol/g, adds +7.7 mM Na, and costs:
   - **USD 0.02-0.26 per kg cells** at USGS bulk zeolite prices (0.05-0.30 USD/kg), single use;
   - **USD 1.7-17 per kg cells** if a sterile medium-grade sorbent costs 5-20 USD/kg (assumed), single use;
   - **USD 0.03-0.34 per kg cells** with 50 regenerations at those assumed prices, plus about 50 g NaCl and 2.5 L brine per kg cells.
   - The substitute substrate: 10 mM aKG x 11 L = 0.11 mol = 16 g aKG (or 12 g sodium pyruvate) per kg cells; price not sourced, so cost not stated (likely cents; **from memory** that bulk prices are of the order of USD 5-20/kg would give 0.08-0.32 USD/kg cells).
   So the order of cost is **about USD 0.1-1 per kg cells in the optimistic case and under about USD 20 in the pessimistic one**, almost all of it set by the unknown price and life of the sorbent.

What this combination does not settle: the 11 L floor also needs the nutrient supply to keep up at a 24 h doubling (the earlier note's central open issue), and in every dataset above mu is 0.35-0.65 per day when the low-waste condition holds, never 0.69 with the ammonia criterion met.

## Corrections to the earlier note
- Hefzi et al. is now peer-reviewed (Nat Metab 2025, PMC12272911), not only a preprint.
- Hubalek's DT list (38.0, 42.9, 47.6, 48.8 h) is confirmed from full text; the 54.2 h entry (aKG/Pyr combined) was not re-checked.
- The Pasitka paper is not open in this session; the 145/76/2.4 g basis remains unresolved.

## What I could not verify
- Any sorbent capacity at 1-5 mM NH4 in 140 mM Na (my 0.1-0.2 mmol/g is derived from an exchange isotherm, with K from a clinoptilolite free energy snippet, a back-calculation from a dialysis patent, and a resin value from memory).
- Sorbent effects on amino acids, growth factors, trace metals; cycle life; any price except bulk zeolite.
- Full text of Capiaumont 1995, Nayve 1991/1994, Jeong and Wang, Genzel 2005, Zhang 2006 (rates), Gagnon 2011, Zagari 2013, Mayrhofer 2020 (re-opened only via the earlier note), Freund and Croughan 2018 (earlier note), Pasitka 2024.
- Alanine inhibition threshold, alanine yield per kg, and any ammonia number for GS-CHO, NS0, HEK, fish, porcine or quail cells.
- The growth-rate and lactate-yield numbers of Warburg-null cells (plotted only).
- Whether the 3000 pg per cell basis holds for these cells (a factor of 2 passes into every per-kg figure).
