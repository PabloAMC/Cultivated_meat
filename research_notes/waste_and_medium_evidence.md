# Waste yields, medium use and waste-handling alternatives: evidence review

Compiled 2026-11-14 from web search and page reads. Nothing was measured here. Written to answer one question for the model: where do real cells sit on the `waste` dial (0 = Humbird's enhanced cells, about 11 L medium per kg wet cells; 1 = wild-type cells, about 190 L/kg)?

## Summary (10 lines)

1. No source I could open measures litres of medium per kg of wet cells directly for any meat-relevant cell. Every L/kg figure below is derived by me from rates, with the conversion shown.
2. Ordinary cells: the best meat-relevant number is bovine FAPs (Hubalek 2023) at 56 fmol NH3/cell/h in spinner flasks. That is about 0.70 mol/kg wet and about 140 L/kg at a 5 mM limit (dial about 0.7). The same paper gives about 10-fold lower in shaker flasks, so the range is wide.
3. Ammonia, not lactate, sets the washout volume for ordinary cells. Replacing glutamine with alpha-ketoglutarate, pyruvate or glutamate cut ammonia production more than 5-fold in bovine FAPs (13-43% slower doubling, not statistically significant at n = 5). Lactate was not quantified there.
4. Lactate is the more fixable waste in pharma cells: lactate-adapted CHO gave 0.39 vs 1.41 mol lactate per mol glucose, and pH-triggered glucose feeding (HIPDOG) or glucose-limited perfusion pushes cells into net lactate consumption. Ldha/Pdk knockouts reach about zero lactate, but only in a preprint.
5. Best pharma perfusion practice (Mayrhofer 2020, CHO-K1 GS) is 14-30 pL/cell/day while still growing at about 0.15 /day, and 8-10 pL/cell/day at zero net growth. Converted at about 2.7 ng per cell, that is about 30-70 L/kg produced, not 11. Reaching 11 L/kg at a 24 h doubling needs about 23 pL/cell/day at 4.6-fold faster growth than pharma has shown.
6. In optimised pharma perfusion, nutrient supply (glucose, glutamate), osmolality (about 400 mOsm/kg) and viability limit the floor, not ammonia or lactate. Waste is already small in those runs.
7. Best meat-relevant demonstration, Pasitka 2024 (chicken fibroblasts, TFF perfusion): 145 g glucose, 76 g lactate and 2.4 g ammonia, held at under 30 mM lactate and 3 mM ammonia. If those grams are per kg of cells (the paper's basis is NOT confirmed), the washout need is about 28-47 L/kg (dial about 0.2). But the paper's own $0.63/L medium and $13.7/kg cost cap medium at about 21 L/kg, so the two do not fit. This is the most valuable unresolved point.
8. Waste removal alternatives: zeolite and ion exchange for ammonia are shown with hybridoma (ammonia held at 1-4 mM, density up 300% in a 1994 study, snippet only). Alkaline stripping is shown on lamb satellite-cell spent medium (82% removal at pH 12, bench). Dialysis-loop regeneration is shown with CHO (92% lactate removal). None has a published cost per litre, a scale above bench, or a proven effect on growth factors.
9. Engineered and co-culture routes are early: cyanobacteria co-culture cut lactate 30% and ammonium over 90% (rat liver cells, Sci Rep 2024, snippet); a GFI-funded project to make a bovine line without lactate and ammonia is 2026-27 and has no results. I found no peer-reviewed pyruvate-carboxylase or urea-cycle result for meat cells.
10. Central estimates on the dial: ordinary cells 0.7 (0.35-1.3); best pharma practice 0.16 (0.08-0.33); best demonstrated meat-relevant 0.2 (0.1-0.7), low confidence. The model's `waste = 0.25` (about 56 L/kg) is about what the best pharma practice gives today for cells growing at about 0.15-0.35 per day; `waste = 0` has not been demonstrated.

## Conventions

Access codes: **PDF** = I downloaded the file and text-searched it myself. **FT-sum** = full text fetched but read through an automatic page summariser, so wording is the summariser's; spot-check before publishing. **ABS** = abstract or record only. **SNIP** = search-result snippet only (a lead, not a verified figure). **CITED** = number quoted from another paper I read. **INF** = my own arithmetic or inference. Items marked "from earlier note" are carried from `waste_handling.md` or `perfusion_rate_osmolality.md` and were not re-opened by me unless stated.

Cell mass: Humbird uses 3000 pg wet per cell, so 1 kg = 3.33e11 cells. Clincke 2013 measured 17 um CHO cells (2.57 pL, about 2.7 ng at 1.05 g/mL, from the earlier note), so the Humbird figure is within about 10% for CHO. Real meat-relevant cells may differ by a factor of about 2 either way, and that factor passes straight into every mol/kg and L/kg below.

Dial conversion: L = 11 + 179 x waste, so waste = (L - 11)/179.

Model-style washout: L/kg = max(mol NH3 per kg / limit, mol lactate per kg / limit), limits 5 mM and 50 mM (Humbird; `floor_physics.py` `washout_litres`).

### Check of `waste_handling.md`

The file is cut off mid-row at the end of section 3 ("Lactic acid rec"); sections beyond that do not exist. What I re-checked:

- Hubalek numbers (56.3 +/- 17.3 fmol/cell/h, DT 25.7 h; DTs 38.0 / 42.9 / 47.6 / 48.8 / 54.2 h; 5 mM and 2 mM thresholds): confirmed (FT-sum). Added: the same paper's shaker value is about 5 fmol/cell/h, 10-fold lower, which the earlier note mentions but does not treat as a source of uncertainty (see Q1).
- Pasitka 145 / 76 / 2.4 g and the 3 mM / 30 mM set-points: confirmed in two snippets. The earlier note's "2 L bioreactors" is not confirmed by anything I could open. A second snippet gives 252 g glucose and 131 g lactate for the 50,000 L analysis. Basis still unknown.
- Humbird: confirmed the limits (5 mM NH3, 50 mM lactate), the 195 g/L at 1 RV/d enhanced case, 20 g/L at 2 RV/d wild type, and stoichiometry (Lac/Glc 1.77 stated for wild type; reaction coefficients imply 1.42 and 0.28; the summariser's derivation, not stated by the paper). The paper states no L/kg figure; the model's 11 and 190 L/kg are the project's own derivation.
- Not re-checked: Ozturk 1992 (4 mM, 55 mM), Lao and Toth 1997, Freund and Croughan 2018, Hefzi 2024, Wieczorkiewicz 2020, Podolinnaia 2023, YekrangSafakar 2022.

---

## Q1. Measured waste yields

### 1a. Ordinary (high-waste) cells

| Cell, system | Quantity | Value as stated | Conversion to mol/kg wet (3000 pg/cell) | Source, access |
|---|---|---|---|---|
| Bovine FAPs, spinner flasks, GlutaMAX 2 mM, 17 mM glucose | Specific ammonia production rate qAmm | 56.3 +/- 17.3 fmol/cell/h; DT 25.7 +/- 1.7 h | mu = 0.693/25.7 = 0.0270 /h; Y = 56.3/0.0270 = 2087 fmol = 2.09 pmol/cell; x 3.33e11 = **0.70 mol NH3/kg**; at 5 mM this is 0.70/0.005 = **140 L/kg** | Hubalek et al. 2023, Front Bioeng Biotechnol 11:1202165, doi 10.3389/fbioe.2023.1202165. FT-sum |
| Same cells, orbital shaker, short term | qAmm | "about 5 fmol/cell/h" (DT for this condition only in a figure) | If DT 38 h: mu = 0.0182 /h; Y = 274 fmol; **0.09 mol/kg**; 18 L/kg at 5 mM. If DT 25.7 h: 0.06 mol/kg | Same. FT-sum. **Disagrees 10-fold with the spinner value in the same paper; cause not explained** (vessel? degradation of GlutaMAX? measurement window?) |
| Same cells | Ammonia accumulation model | 5 mM would be reached in 11 h at 7e6 cells/mL | Check: 56.3 fmol x 7e9 cells/L = 0.39 mM/h, so 5 mM in about 13 h. Consistent with the spinner value, not the shaker value | Same. FT-sum, INF check |
| CHO DG44, shake flask, osmolality-adapted control | Lactate yield on glucose; qLac | Y = 1.411 +/- 0.284 mol/mol; qLac 0.112 +/- 0.032 umol/1e6 cells/h; mu 0.027 /h | 0.112/0.027 = 4.15 pmol/cell = **1.38 mol lactate/kg**; 28 L/kg at 50 mM, 46 L/kg at 30 mM | Freund and Croughan 2018, Biotechnol Prog, from earlier note. FT-sum (earlier note) |
| General "non-shifted" mammalian cultures | Lactate/glucose | "about 2" mol/mol | - | Patent text (continuous-culture patent, US 6156570), SNIP. Secondary; use only as an upper reference |
| Humbird wild-type model cell | Per mol dry cell mass | 0.070 NH3 and 0.474 lactate (glucose 0.333); Lac/Glc 1.77 | Model's 0.95 mol NH3/kg and 6.4 mol lactate/kg | Humbird 2021, Biotechnol Bioeng 118:3239, PMC8362201. FT-sum |
| Chicken fibroblast line (Pasitka), unmodified | Lactate/glucose; NH3/glucose | 76 g lactate per 145 g glucose = 0.844 mol per 0.805 mol = **1.05 mol/mol**; 2.4 g NH3 = 0.141 mol, so 0.175 mol NH3 per mol glucose | No per-kg value derivable (basis not stated in what I could read) | Pasitka et al. 2024, Nature Food 5:693, doi 10.1038/s43016-024-01022-w. SNIP (paper itself blocked: paywall page, ResearchGate 403) |
| MsNAC insect line (Manduca sexta; suspension, SF900 III, 4e6 cells/mL batch) | Spent medium | Glucose "not consumed"; lactate "less than 1 mmol"; ammonia "over 15 mmol over 7 days"; glutamate exhausted | If "15 mmol" means mM and density 4e6 cells/mL: 15 umol/mL / 4e6 cells/mL = 3.75 pmol/cell = about **1.25 mol NH3/kg** (INF; units in the preprint are unclear; cell mass assumed 3000 pg) | Letcher et al. bioRxiv 2024, doi 10.1101/2024.10.18.618906 (later Sci Rep 2025, doi 10.1038/s41598-025-86921-z). PDF (preprint) |
| Sf9 and other lepidopteran lines | Qualitative | Lactate and ammonia "lack" of production under glucose and glutamine excess; ammonia appears under glucose limitation | - | Search snippets of several 1990s-2000s papers. SNIP only; no numbers |

**Not found:** CHO or HEK ammonia yield per glutamine (mol/mol) or per cell with numbers; the CHO-K1 flux paper (Altamirano et al., PMC3980355) has the data only in figures. Lactate yield for bovine, chicken (beyond Pasitka), fish or quail cells. No data at all for Vow quail, UPSIDE or Mosa Meat beyond Hubalek.

### 1b. Reduced-waste cells and processes

| Cell, system | Intervention | Value as stated | Conversion / comment | Source, access |
|---|---|---|---|---|
| Bovine FAPs | GlutaMAX replaced by 10 mM alpha-ketoglutarate, pyruvate or glutamate | "No or even negative" ammonia production without Gln; abstract: "more than 5-fold" lower | < 0.14 mol/kg, so < 28 L/kg at 5 mM (INF). Growth cost: DT 42.9 (aKG), 47.6 (Pyr), 48.8 (Glt), 54.2 h (aKG/Pyr) vs 38.0 h; not significant, n = 5. 13-43% slower point estimates | Hubalek 2023. FT-sum. Lactate not quantified in text |
| CHO DG44 | Lactate adaptation (35 mM) | Y_lac/glc 0.388 +/- 0.344 vs 1.411 mol/mol; qLac 0.022 vs 0.112; mu 0.025 vs 0.027 /h; fed-batch peak lactate 10 mM vs 94 mM; peak VCD 35e6 vs 22e6; ammonium production about 50% lower | 0.29 vs 1.38 mol lactate/kg (INF) | Freund and Croughan 2018. FT-sum (earlier note) |
| CHO-S, CHO-K1, HEK293 | Ldha + Pdk1-4 knockout | Peak lactate sub-mM to single mM vs 13-135 mM in wild type; growth comparable | Lactate yield about 0 | Hefzi et al. 2024, bioRxiv preprint (no peer-reviewed version found). FT-sum (earlier note) |
| CHO | LDH-A siRNA knockdown | Specific lactate production 45-79% of control (75-89% LDH-A activity cut); growth not impaired | Partial only; complete LDHA knockout reported lethal in CHO | Snippets of an siRNA LDH-A study (authors not captured). SNIP |
| CHO | LDH-A knockdown + Bcl-2 | Specific lactate rate 21-65% and lactate/glucose yield 37-78% of control | - | SNIP |
| CHO fed-batch, bench to 2,500 L | HIPDOG: glucose delivered only when pH rises | "Dramatically reduce or eliminate lactate accumulation"; final titre about doubled for 8 cell lines; glucose below about 1 mM leads to lactate uptake | No mol/mol | Gagnon et al. 2011, Biotechnol Bioeng 108:1328, doi 10.1002/bit.23072. ABS/SNIP |
| CHO-K1 GS, perfusion | Glucose-limited (feed-supplemented) | "After day three, glucose limitation stopped lactate production and cultures switched to lactate consumption"; ammonia in bioreactor below 30 mg/L | If 30 mg/L as NH4+ = 1.7 mM. Steady-state net rate at 130e6 cells/mL and 1 vvd: 1.7 mM x 1 L/d per 1.3e11 cells/L = 13 fmol/cell/d = **0.5 fmol/cell/h**, about 100-fold below Hubalek spinner control (INF; plateau culture, not growing) | Mayrhofer et al. 2020, Biotechnol Prog 36:e2933, doi 10.1002/btpr.2933. FT-sum (this session) |
| BHK-21 | Glutamate for glutamine | Ammonia accumulation down more than 60% | - | SNIP, primary not identified |
| CHO | Glutamine-free (GS) | Ammonia "greatly decreased"; lactate excretion not lower in later phases in a CHO-K1 flux study | No numbers | SNIP; PMC3980355 |
| Humbird "enhanced" | Target only | 0.004 NH3 and 0.041 lactate per mol dry cell mass; Lac/Glc 0.50; Gln/Glc 0.025 | 0.054 and 0.56 mol/kg in the model; **an assumption, not a measurement** | Humbird 2021. FT-sum |

**Reading:** the Humbird-enhanced numbers have been approached for lactate in pharma (adapted, knocked-out, or glucose-limited CHO) and for ammonia only by removing glutamine. No source shows both together in a meat-relevant cell.

---

## Q2. Medium used per kg of cells in reported dense or perfusion runs

Conversion used: L/kg held per day = CSPR (pL/cell/day) x 3.33e11 cells/kg / 1e12 pL/L = CSPR x 0.333 L/kg/day. L per kg *produced* = (L/kg/day held) / mu, where mu (per day) is the net growth rate balanced by the bleed. Example: 50 pL at mu 0.35 per day: 16.7/0.35 = 48 L/kg.

| # | Reported process | CSPR | mu (per day) | L/kg held per day | L/kg produced (INF) | Source, access |
|---|---|---|---|---|---|---|
| 1 | CHO IgG, WAVE, ATF/TFF, commercial medium; "0.05 nL/cell/day selected"; max 2.14e8 cells/mL at 8-10 RV/d | 47-60 pL | 0.35 moderate density; about 0.15 above 1.5e8 | 16-20 | 45-57 at mu 0.35-0.4; about 100-130 at mu 0.15 | Clincke 2013 Part I, Biotechnol Prog 29:754, from earlier note, FT |
| 2 | Same, higher test | 80 pL | not improved | 27 | - | same |
| 3 | CHO-K1 GS, optimised medium, plateau | 8-10 pL (130e6 at 1 vvd; 220e6 at 2 vvd) | about 0 | 2.7-3.3 | undefined (no net production) | Mayrhofer 2020, FT |
| 4 | Same clone, ActiPro + feed supplements, constant CSPR 30 falling to 14 pL, up to 240e6 cells/mL at 96% viability | 14-30 pL | about 0.15 (figure reading, earlier note: 100 to 240e6 over about 6 days) | 4.7-10 | **31-67** | Mayrhofer 2020, FT |
| 5 | CHO N-1 perfusion, real-time CSPR control | 36-113 pL; "no plateau up to 113"; viability fell 98 to 89% when CSPR was ramped down | not given in what I read | 12-38 | - | Walther et al. 2025, Front Bioeng Biotechnol 13:1608889. FT-sum |
| 6 | Industry typical, no optimised medium | 50-300 pL | - | 17-100 | - | Mayrhofer intro, CITED |
| 7 | Reports of 15-20 pL | 15-20 pL | - | 5-6.7 | - | Mayrhofer intro, CITED |
| 8 | Schulze 2021 (cited by Walther) | 50 pL, then 20 pL for last 2 days | - | 6.7 | - | CITED, primary not read |
| 9 | Dowd 2003 (cited by Walther) | metabolic plateau at 200 pL or more | - | 67 | - | CITED |
| 10 | CHO anti-IL8, push-to-low at steady state | CSPRmin about 100 pL; lower by other methods | - | 33 | - | Biochem Eng J 2023 (article 108779; authors not confirmed), ADS record. SNIP |
| 11 | Hybridoma, Konstantinov push-to-low | target below 50 pL; reduced growth and more apoptosis at low CSPR | - | below 17 | - | Konstantinov et al. 2006, Adv Biochem Eng Biotechnol 101:75. SNIP |
| 12 | Fortified media in review | 23 and 15 pL in two processes; low-lactate/ammonia lines 25-50 pL "or lower" | - | 5-17 | - | Review snippet (Bielser et al. 2018, Biotechnol Adv 36:1328 is the likely source; page 403, not read). SNIP |
| 13 | Chotteau group abstract | specific productivity independent of CSPR below 52 pL; lactate and glucose rates rise with CSPR | - | - | - | KTH/ECI abstract, SNIP |
| 14 | Pasitka 2024, chicken fibroblasts, TFF, ACF medium | not stated in what I read; 130e6 cells/mL, 43% w/v yield, harvests over 20+ days | - | at 1 RV/d: 430 g/L wet gives 2.3 L/kg held per day (INF; the RV/d is unknown) | unknown | Nature Food 2024 abstract; FEI article. SNIP |
| 15 | Secondary estimates of medium per kg | - | - | - | "up to 42 L/kg" (Pakbin 2025 intro, no primary found); "about 50 L/kg" (Arch Microbiol 2022, s00203-022-03234-9); GFI 8-13 L/kg (assumption); industry targets about 20 L/kg | SNIP; these are estimates, not measurements |
| 16 | Humbird model, for reference | - | - | 1 RV/d at 195 g/L = 5.1 L/kg held per day; wild type 2 RV/d at 20 g/L = 100 L/kg held per day | - | Humbird 2021, FT-sum |

**What limited going lower:**

- Mayrhofer 2020: no single limit stated. Their modelling says a medium supporting 50e6 cells/mL at 1 vvd (about 20 pL) needs about 12.5 g/L glucose and 550 mg/L glutamate, so supply of glucose and glutamate (as markers for other nutrients) and a 400 mOsm/kg osmolality ceiling set the floor. Ammonia stayed below 30 mg/L. (FT-sum)
- Clincke 2013: packed cell volume (0.5 at 2e8 cells/mL), pCO2 (31 kPa at 2e8) and growth (mu fell to about 0.15 per day). Not waste. (earlier note, FT)
- Walther 2025: viability fell and metabolic rates became unstable at the lowest CSPR (0.04-0.05 nL). Lactate and ammonia rates fell as CSPR fell (r = -0.83 and -0.9 on their sign convention). (FT-sum)
- Konstantinov (snippet): reduced growth and more apoptosis at low CSPR.

**What this means for the model:** pharma data show CSPR of 14-30 pL only at mu about 0.15 per day. The model's 11 L/kg at a 24 h doubling (mu = 0.69 per day) implies CSPR = 11 x 0.69 / 3.33e11 per day = 23 pL/cell/day. So the floor is not far from pharma's CSPR, but it needs 4-5 times faster growth at that CSPR. Not demonstrated. Whether the 4-fold growth gap is bridgeable by a medium that is not nutrient-limited is the real open question; it is a nutrient-supply question, not a waste question.

---

## Q3. Tolerance (concentration that roughly halves growth, or onset)

| Cell | Ammonia | Lactate | Notes | Source, access |
|---|---|---|---|---|
| Hybridoma, batch | halving at about 4 mM | halving at about 55 mM (osmolality part of it suspected) | Initial-concentration spiking | Ozturk, Riley, Palsson 1992, Biotechnol Bioeng 39:418; earlier note, ABS. Not re-checked |
| Hybridoma, osmolality | - | - | 290 to 435 mOsm/kg halves growth | Ozturk and Palsson 1991 via earlier note, SNIP |
| CHO, batch | no inhibition up to 10 mM | 25% growth reduction up to 60 mM after osmolality correction | Disagrees with ammonia 2-10 mM onset below | Lao and Toth 1997, ABS |
| CHO, manufacturing fed-batch | growth inhibited above 5.1 mM | viability affected above 58 mM and 382 mOsm/kg | Authorship uncertain | Biotechnol Prog 2008, SNIP |
| CHO, literature summary | onset 2-10 mM, often 2-4 mM | 20-40 mM | - | Freund and Croughan 2018, earlier note |
| CHO osmolality | - | - | 10% growth loss at about 345, halved at about 430-465 mOsm/kg | Alhuthali 2021; Zhu 2005; earlier note |
| **Bovine FAPs** | proliferation inhibited above 5 mM (day 4); adipogenic differentiation reduced from 2 mM | not measured | Spiked NH4Cl; no IC50 | Hubalek 2023. FT-sum |
| **MsNAC insect line**, 5-day exposure, 48-well | growth slowed above 6.25 mM; "most dramatic" above 25 mM; pH stayed 6.09-6.22 in all conditions | no effect to 12.5 mM; drastic fall above 25 mM | Ammonia produced in batch (over 15 mmol) is inside the inhibitory range | Letcher bioRxiv 2024. PDF |
| **Channel catfish ovary (CCO) fish line** | 2.5 mM reduced growth rate by 44.2% | 2.5 mM reduced it by 14% (range tested 0-20 mM) | Authors state there were no earlier data on fish cell lines. One line only | Cytotechnology 2010, doi 10.1007/s10616-010-9312-y. SNIP (full text redirected to a login) |
| **Chicken fibroblast, perfusion** | operated below 3 mM | operated below 30 mM | Set-points, not measured limits | Pasitka 2024. SNIP |
| C2C12, chick, tilapia myotubes | 10-50 mM ammonium acetate for 24 h; tilapia unaffected, mouse most sensitive | - | Differentiation endpoint, not proliferation | Wieczorkiewicz 2020, from earlier note |
| Lamb satellite cells | literature 1.8-33 mM quoted | above 40 mM | Spent medium was only 1.2 mM | Pakbin 2025, from earlier note |
| Sf9 | up to 10 mM no effect (1993 study) | - | SNIP only |  search snippet of a 1990s paper |

**Disagreements:** CHO ammonia tolerance spans "no effect to 10 mM" to "onset 2-4 mM". Meat-relevant cells show onset of 2.5-6 mM (bovine FAP 5, catfish 2.5, insect 6.25), consistent with the model's 5 mM. Lactate: pharma 25-58 mM; insect 12.5-25 mM; catfish already 14% at 2.5 mM. The model's 50 mM lactate is generous for meat-relevant cells; the Pasitka set-point of 30 mM is more cautious. Neither the pH dependence of ammonia toxicity nor adaptation of meat-relevant cells was found.

---

## Q4 and Q5. Alternatives to washing waste out, and evidence class

Evidence class: **M** = shown with meat-relevant cells (or spent meat-cell medium); **P** = pharma cells only; **N** = not shown with cells.

| Alternative | Best evidence | Scale | Cost number | Class | Source, access |
|---|---|---|---|---|---|
| **Alkaline stripping of ammonia, then re-use blended 50:50 with fresh** | pH 12, 15 min, 1,400 rpm: 82.45% removal (1.214 to 0.213 mM). Treated spent medium blended 50:50 with fresh improved lamb satellite cell growth without morphology change. Glucose reduced at alkaline pH; amino acids, growth factors and lactate NOT measured | Bench | None; authors argue cost-effective, no figures | **M** (spent medium from lamb cells at 1.2 mM, below inhibition) | Pakbin et al. 2025, Front Bioeng Biotechnol, doi 10.3389/fbioe.2025.1617115. FT (earlier note) + SNIP |
| **Zeolite adsorption (cell-free permeate loop)** | Hybridoma serum-free perfusion, zeolite bed on permeate held ammonia at 1-4 mM; a 1994 follow-up reports peak density up over 300% and titre about 10-fold (snippets). Zeolite A-3, anchorage-dependent CHO and Vero versions: Vero virus productivity 2.6-fold. In lamb spent medium: zeolite 5 and 20 g/L "decreased significantly", no percentage; clinoptilolite 35.8% (CITED, primary not located) | Bench to small perfusion | None found | **P** (hybridoma, CHO, Vero); **M** only as a bench adsorption test | Nayve et al. 1991/1994 (SNIP); Kameda 2021 cited by Pakbin; Pakbin 2025 |
| **Zeolite capacity in medium** | In water 0.35-0.87 mmol NH4+/g; competing Na+ (about 140 mM) and K+ in medium make this an upper bound (INF). Nikkiso/Tohoku patent: at least 0.005 g/mL gives at least 10% ammonia adsorption, 0.1 g/mL or less keeps glucose loss to 20% or less | Patent text, not data | None | **N** for meat | Earlier note, SNIP |
| **Other ammonia sorbents** | Prussian blue maximum 10% in medium; struvite and TiO2 no significant removal; sodium zirconium phosphate cited as used on spent medium | Bench | None | P / N | Pakbin 2025 (CITED) |
| **Gas-membrane or electrokinetic removal** | Hybridoma, in-situ electrokinetic removal at 50 A/m2: growth +30%, titre +50% (1995); hollow-fibre gas membrane: better growth, no better specific secretion | Lab, 1990s | None | **P** | Chang, Grodzinsky, Wang 1995; J Biotechnol 1995 (SNIP). Never scaled |
| **Lactate removal by adsorbent** | Mg-Al and Cu-Al layered double hydroxide/oxide: selective L-lactate removal, glucose mostly retained, but dose-dependent toxicity to hiPSC and C2C12 | Bench | None | **M-ish** (C2C12 toxicity tested; removal capacity not retrieved) | Podolinnaia, Kameda et al. 2023, SNIP |
| **Dialysis of the medium loop (haemodialyser, basal-medium dialysate)** | CHO at 72.8e6 cells/mL, 2e9 cells: lactate down 92% and glucose restored from 21% to 100% in about 20 min; culture held 10 days without medium replacement. Dialysate used about 2.1 L per L of medium regenerated (INF), so it saves proteins and growth factors but not basal medium or water. Ammonia and protein retention not measured | 2e9 cells, 1.4 m2 dialyser | None | **P** | YekrangSafakar et al. 2022, from earlier note, PDF |
| **Electrodialysis for lactate** | Shown on microbial fermentation broth and cell-free solutions; none in mammalian culture | Industrial (fermentation) | None for cells | **N** | Patent and thesis snippets |
| **Enzymatic conversion (lactate oxidase, LDH, urease-type ammonia)** | I found no data for mammalian culture medium | - | - | **N** | Searched; nothing |
| **Lower-waste feeding (HIPDOG, glucose limitation)** | Lactate "reduced or eliminated" during growth phase, 2,500 L fed-batch, titre about doubled across 8 lines | Up to 2,500 L | Titre gain, no cost | **P** | Gagnon 2011, ABS/SNIP |
| **Glutamine substitution** | See Q1b. More than 5-fold lower ammonia in bovine FAPs; slower DT point estimates | 100 mL spinner, 6-well planar | None | **M** (bovine FAPs, one lab) | Hubalek 2023 |
| **Cell engineering: Ldha/Pdk knockout** | Lactate about 0 in CHO-S, CHO-K1, HEK293, growth like wild type, up to 3 g/L antibody in 270 mL | Up to 270 mL bioreactor | None | **P**, preprint | Hefzi 2024 preprint |
| **Cell engineering for meat cells** | GFI grant (2026-27) to engineer a bovine line that makes no lactate or ammonia: description only | - | - | **N** (planned) | GFI grant page, SNIP |
| **Glutamine synthetase, urea cycle, pyruvate carboxylase** | GS selection removes glutamine need in CHO and cuts ammonia; no meat-cell data. I found no source on urea cycle or pyruvate carboxylase expression; remembered literature (yeast PYC2 in CHO) NOT verified | - | - | **P** for GS; **N** otherwise | Searches; nothing quantitative |
| **Co-culture with waste-consuming cyanobacteria** | Rat liver cells + engineered lactate-consuming Synechococcus: lactate down 30%, ammonium down over 90%; conditioned medium supported muscle cell growth without serum. Earlier paper: Synechococcus PCC 7002 with animal muscle cells | Lab culture | None | **M-ish** (muscle cells used as the recipient, not co-grown at density) | Waseda group, Sci Rep 2024, doi 10.1038/s41598-024-70377-8 (SNIP); Arch Microbiol 2023 (SNIP) |
| **Spent-medium use for algae or yeast** | UQ study: spent cultivated-meat medium grown into microalgae, 60-90% cost cut claimed (snippet); a yeast-based circular system concept (SSRN) | Lab | 60-90% (claim, SNIP) | **N** (does not recycle to the meat cells) | SNIP |
| **Commercial "rejuvenation"** | CellRev + Saint-Gobain Life Sciences: toxin removal and nutrient replenishment after harvest; announced Aug 2023; no data, no reuse fraction, no cost | - | None | **N** (no published data) | FoodNavigator 2023, read |
| **Growth-factor retention by ultrafiltration** | Reviews say retention and reuse is needed, and that FGF-2 and TGF-b can be about 98% of cost in one medium. I found no measurement of ultrafiltration or TFF retention of growth factors in cultivated-meat perfusion | - | GFI scenario: growth factors at 10% of cost = $1/kg | **N** | Review snippets; Yang et al. 2023, Trends Food Sci Technol 138:564 (abstract level) |

Review judgement (not evidence): Yang et al. 2023 conclude adsorption is the most promising route; Pakbin says very few efforts exist on ammonia removal from spent medium.

**Note on the scale of what these can do (INF):** an adsorbent or stripper that removes a fraction f of ammonia and lactate per pass cuts washout volume by about 1/(1-f) only if the treated stream can be returned to the culture at full nutrient value. Pakbin's 82% on 1.2 mM spent medium is a different regime from a loop that must hold 3-5 mM; Nikkiso's remark that dialysis conditioning tanks have been more than 10 times the culture volume suggests the loop hardware is the cost.

---

## Where real cells sit on the model's waste dial

All three estimates assume the model's 3000 pg per cell, a 5 mM ammonia and 50 mM lactate limit, and the L-to-dial mapping above. Confidence is low: no source gave L/kg directly.

| Case | Best estimate L/kg | Range L/kg | Dial value (best, range) | Basis |
|---|---|---|---|---|
| (i) Ordinary cells | **140** | 70-250 | **0.72** (0.33-1.3) | Bovine FAPs in spinner flasks, 0.70 mol NH3/kg at 5 mM (140 L/kg). Lower end from the shaker value (0.09 mol/kg, 18 L/kg) and from Pasitka-type ammonia limit 3 mM raising it; CHO lactate (1.38 mol/kg) gives only 28-46 L/kg, so ammonia binds. Pharma "typical" CSPR 50-300 pL at mu 0.3-0.4 gives 40-330 L/kg, same order. Hubalek's 190 L/kg (dial 1) is therefore reasonable or slightly pessimistic for glutamine-fed media |
| (ii) Best demonstrated pharma practice | **40** | 25-70 | **0.16** (0.08-0.33) | Mayrhofer 14-30 pL at mu about 0.15 per day: 31-67 L/kg; Clincke/commercial 47-60 pL at mu 0.35-0.4: 45-57 L/kg. Zero-growth 8-10 pL plateaus are not counted since they produce no net cells. Lactate- and ammonia-limited runs do better than L/kg suggests, because nutrients, not waste, set these floors |
| (iii) Best demonstrated meat-relevant | **45** | 25-140 | **0.19** (0.08-0.72) | Low confidence. (a) Pasitka: at its 3 mM and 30 mM set-points, 0.141 mol NH3 and 0.844 mol lactate give 47 and 28 L, so about 47 L/kg IF the grams are per kg of cells. (b) Bovine FAP with alpha-ketoglutarate: ammonia under 0.14 mol/kg so under 28 L/kg, but lactate and the growth-rate cost unmeasured. (c) The ordinary-cell range 70-250 if neither holds. **Cross-check against Pasitka's own economics: medium at $0.63/L and total cost $13.7/kg cap medium at about 21 L/kg (dial under 0.06) even if medium were all of the cost, which contradicts reading (a). Either the grams are not per kg, or their model assumes recycling or a lower washout than their experiment** |

Reading for the model: `waste = 0.25` (about 56 L/kg) is roughly where today's best pharma-like perfusion sits when cells are still growing, and plausibly where Pasitka-class meat cells sit. `waste = 1` is an acceptable stand-in for unadapted glutamine-fed meat cells. `waste = 0` is only supported by Humbird's assumed metabolism and by single-trait demonstrations (lactate near zero in knockouts; ammonia near zero without glutamine), never both in one culture.

---

## Bench measurements that would most reduce the uncertainty

1. **Full mass balance on the model's own cells.** Fed-batch or perfusion in a 1-2 L stirred bioreactor (or 4 shake flasks), daily glucose, lactate, ammonium, glutamine/glutamate, plus pellet wet mass per cell. Gives mol lactate and ammonia per kg wet on the real cell, with and without glutamine replacement, and resolves the 10-fold spinner vs shaker disagreement. About 6-8 weeks; $15-30k including analyser time.
2. **Clarify the Pasitka basis.** Ask the authors, or read the supplement, for what 145 g / 76 g / 2.4 g (and 252 g / 131 g) are per. Also the RV/d, the bleed and the medium litres per kg. Free; days to weeks; it decides whether a meat-cell run has already reached about 45 L/kg or under 21 L/kg.
3. **Push-to-low perfusion with a bleed at fixed growth.** 1-2 L (ambr250 or small TFF/ATF) with the target meat cell, step CSPR from about 100 down to 20 pL/cell/day, record mu, viability, NH4, lactate, osmolality. Shows what limits the floor (waste vs nutrient vs osmolality) and gives L/kg produced at known mu. 8-12 weeks; $40-80k.
4. **Ammonia and lactate dose-response with pH and osmolality controlled.** Shake flasks or 96-well, 0-40 mM, 5-7 day exposure, growth rate and viability, on the real cell; include a lactate dose with matched osmolality. 2-3 weeks; under $5k. Replaces the borrowed 5 mM and 50 mM limits, which move the washout volume proportionally.
5. **Adsorbent test on real spent medium.** Zeolite (clinoptilolite, A-3), sodium zirconium phosphate and a cation resin at 5-100 g/L in spent medium from run 1; measure NH4, Na, K, glucose, amino acids, FGF-2 by ELISA, then grow cells in treated-and-blended medium. Gives a capacity per gram in real medium and a growth-factor loss. 2-3 weeks; $3-8k.

---

## Not verified / not found

- Pasitka 2024 full text, the basis of 145 g / 76 g / 2.4 g and 252 g / 131 g, bioreactor volume, perfusion rate, and any L/kg: paper not accessible (paywall; ResearchGate 403). Only snippets and press.
- Hubalek lactate and glucose rates (figures only); cause of the 10-fold spinner vs shaker ammonia difference.
- Any quantitative CHO/HEK ammonia yield per glutamine or per cell; GS-CHO vs glutamine-fed ammonia numbers.
- Lactate and ammonia yields for fish, quail (Vow), Sf9 (only qualitative), UPSIDE, SuperMeat, Mosa Meat beyond Hubalek, Stout/Kaplan immortalised bovine lines (searches returned nothing on metabolite yields).
- Bielser 2018 review, Konstantinov 2006, Wolf 2019/2020, Karst 2016, Schwarz, Clincke minimum values: Bielser page blocked (403); others only via snippets or citing papers. The lowest CSPR I can source is Mayrhofer 2020 (full text via summariser).
- Primary papers for the CCO fish study (login wall), Nayve zeolite studies, Waseda cyanobacteria Sci Rep 2024, Podolinnaia 2023, Gagnon 2011 (all snippet/abstract level); Biochem Eng J 2023 CSPRmin author and DOI not confirmed.
- Pyruvate carboxylase and urea-cycle expression in CHO or meat cells: nothing sourced (anything from memory is unverified and not used).
- Costs per litre or per kg for any waste-removal or recycling method: none found.
- Whether adsorbents or strippers remove growth factors, amino acids or vitamins; growth-factor retention by ultrafiltration in cultivated meat.
- The "42 L/kg" and "50 L/kg" estimates: primary derivation not found.
- Whether insect "15 mmol" ammonia is a concentration (mM) and the cell mass of the insect line.
