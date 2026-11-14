# Perfusion rate (CSPR) and osmolality limits for mammalian cell culture

Literature lookup, 2026-11-14. Web search and reading only.

Access codes used in the tables:

- **FT** = full text read (open-access paper or PDF pages).
- **FT-fig** = my reading of a figure in a full text (approximate).
- **AB** = abstract only.
- **SN** = search-engine snippet or a secondary source quoting the paper; not verified against the original.
- **INF** = my own inference or arithmetic, not stated by the source.
- **RECALL** = standard textbook value from my memory, not confirmed in any source read in this session. Treat as unsourced.

Several target papers could not be opened (paywall, empty page or cookie wall): Konstantinov 2006, Ozturk 1996, Dowd, Warikoo 2012, Bielser 2018, Wolf 2019/2020, Chotteau 2015, Ozturk and Palsson 1991 (full text), Zhu 2005 (full text), deZengotita 2002, Kimura and Miller 1996, Takagi, Kiehl 2011. Where they appear below it is through snippets or through another paper citing them.

---

## 1. Cell-specific perfusion rate (CSPR)

### 1a. Unit conversion used throughout (INF)

- Cell diameter 17 um (Clincke 2013, measured). Sphere volume = pi/6 x 17^3 = 0.5236 x 4913 = 2572 um^3 = **2.57 pL per cell**.
- Cross-check from the same paper: packed-cell fraction 0.5 at 2 x 10^8 cells/mL gives 0.5 mL / 2 x 10^8 = 2.5 pL per cell. Consistent.
- Wet density assumed 1.05 g/mL (my assumption, not sourced): 2.57 pL x 1.05 = 2.70 ng per cell, i.e. 3.7 x 10^8 cells per gram wet.
- Therefore **mL medium per g wet cells per day = CSPR (pL/cell/day) / 2.70**. Example: 50 / 2.70 = 18.5 mL/g/day.
- Sensitivity: a 14 um cell is 1.44 pL (1.51 ng), so the same CSPR gives 1.8x more mL/g/day (50 pL/cell/day = 33 mL/g/day). Cell size was not obtained for the low-CSPR studies (Mayrhofer), so the mL/g figures for those carry this uncertainty.

### 1b. Table

| # | Quantity | Value as stated | Converted | Cell line, system | Source | Access |
|---|---|---|---|---|---|---|
| 1 | CSPR setpoint | "A CSPR of 0.05 nL/cell/day was selected based on previous work"; observed 0.05-0.06 nL/cell/day | 50-60 pL/cell/day = 18.5-22 mL/g/day | CHO (IgG), WAVE with ATF or TFF, IS CHO CD XP medium with hydrolysate + 3% feed + 4 mM Gln | [1] | FT |
| 2 | Higher CSPR test | Raising to 0.08 nL/cell/day did not improve growth or maximum density | 80 pL/cell/day = 30 mL/g/day | same | [1] | FT |
| 3 | Maximum density, TFF | 2.14 x 10^8 cells/mL (day 44), at 8-10 RV/day | 10 RV/day / 2.14 x 10^8 = 47 pL/cell/day (INF) | same | [1] | FT |
| 4 | Maximum density, ATF | 1.32 x 10^8 cells/mL at 6 RV/day | 6 / 1.32 x 10^8 = 45 pL/cell/day (INF) | same | [1] | FT |
| 5 | Recommended ceiling | "cell densities under 1.46 x 10^8 cell/mL" (intercellular distance about 2 um for 17 um cells; zero at 2 x 10^8) | packed fraction about 0.37 (INF: 1.46e8 x 2.57 pL) | same | [1] | FT |
| 6 | Cell diameter | 17.1 um at 20-35 x 10^6 cells/mL; 17.3 um at 0.3-1.3 x 10^8; 16.4 um above 1.5 x 10^8 | 2.6, 2.7, 2.3 pL (INF) | same | [1] | FT |
| 7 | Cell volume fraction | 0.1 at 4 x 10^7 cells/mL; 0.5 at 2 x 10^8 cells/mL | 2.5 pL per cell | same | [1] | FT |
| 8 | Growth rate in perfusion | 0.35 /day at moderate density; 0.4 to 0.3 /day between 0.2 and 1.3 x 10^8; about 0.15 /day above 1.5 x 10^8 | doubling time ln2/mu = 2.0 d, 1.7-2.3 d, 4.6 d (INF) | same | [1] | FT |
| 9 | Viability | "mostly above 90%" moderate density; "mostly around 95%" very high density | | same | [1] | FT |
| 10 | pCO2 at very high density | below 22 kPa mostly, 31 kPa at 2 x 10^8 cells/mL ("a level known to affect the growth rate") | 31 kPa = 233 mmHg | same | [1] | FT |
| 11 | Part II densities | 1.27 x 10^8 (TFF) and 1.01 x 10^8 cells/mL (ATF) at 5.5 RV/day; 25 x 10^6 at 1.5 RV/day; diameter about 17.5 um | 5.5/1.27e8 = 43 pL/cell/day; 1.5/25e6 = 60 pL/cell/day (INF) | CHO | [2] | FT |
| 12 | Literature range of minimum CSPR | "Minimum CSPR as low as 50 to 300 pL/c/d were reported in literature but some groups even achieved 15-20 pL/c/d" | 18.5-111 and 5.6-7.4 mL/g/day | review statement in intro | [3] | FT |
| 13 | Lowest CSPR, optimised medium, constant volumetric rate | Steady 130 x 10^6 c/mL at 1 vvd and 220 x 10^6 c/mL at 2 vvd, "translating into a minimum CSPR of 8-10 pL/c/d" | 1/130e6 = 7.7; 2/220e6 = 9.1 pL/cell/day; = 3.0-3.7 mL/g/day at 17 um | CHO-K1 GS (IgG), 500 mL Wave, CDM4NS0 + 11% Cell Boost 1 + 20% Cell Boost 3, pH 7.0 | [3] | FT |
| 14 | Lowest CSPR, optimised medium, constant CSPR | Fixed CSPR 30 pL/c/d from day 3, "subsequently decreased to 14 pL/c/d"; "up to 240 x 10^6 c/ml at 96% viability" in 16 days | 14-30 pL/cell/day = 5.2-11 mL/g/day at 17 um | same clone, ActiPro + 13.9% CB1 + 15.8% CB3 | [3] | FT |
| 15 | Growth state at those CSPR | Row 13: plateaus, i.e. net growth about zero at 8-10 pL/c/d (no bleed described). Row 14: density rose from about 100 to 240 x 10^6 over about 6 days | mu about ln(2.4)/6 = 0.15 /day at 14-30 pL/cell/day (INF from figure) | same | [3] | FT-fig |
| 16 | Control without feed spike | Glucose-spiked CDM4NS0 at 1-2 vvd reached only about 60-90 x 10^6 c/mL | about 11-17 pL/cell/day at plateau (INF) | same | [3] | FT-fig |
| 17 | Perfusion medium osmolality | Feed-spiked media formulated to "a maximum target osmolality of 400 mOsm/kg" | | same | [3] | FT |
| 18 | Push-to-low target | "a strategic target ... should be the decrease of the cell-specific perfusion rate to below 0.05 nL/cell/day", at 20-60 x 10^6 cells/mL; reduced growth rate and more apoptosis seen at low CSPR | below 50 pL/cell/day = below 18.5 mL/g/day | mouse hybridoma (anti-TNF) | [4] | SN |
| 19 | Low-CSPR conference reports | "CSPR values as low as 10 pL/c/d at 2 x 10^8 c/mL", workflow at 20 pL/c/d; separately 22 pL/cell/day at over 100 x 10^6 vc/mL | 3.7, 7.4, 8.1 mL/g/day | CHO, conference abstracts (not peer reviewed) | [5], [6] | SN |
| 20 | Typical process point | 20 x 10^6 cells/mL at 1 RV/day, bleed loss about 10% | 50 pL/cell/day (INF) | CHO, Wolf et al. 2019 | [7] | SN |

Notes:

- Row 13 is the lowest peer-reviewed figure found, but it is a zero-net-growth plateau, closer to a maintenance requirement than to a growth-supporting minimum.
- No hybridoma, HEK or PER.C6 CSPR numbers were obtained beyond the Konstantinov snippet.
- The Chotteau presentation figure "CSPR = 50-60 pL/cell/day" (SN) matches [1].

---

## 2. Osmolality, pH and the CO2/bicarbonate system

| # | Quantity | Value as stated | Converted / comment | Cell line | Source | Access |
|---|---|---|---|---|---|---|
| 1 | Fresh medium design range | "osmolarity in the range of 260 and 320 milliosmoles (mOsm)", serum 290 mOsm/kg | | general | [8] | SN |
| 2 | Fresh medium, measured | Control 320 mOsm/kg (CD CHO); control 316 mOsm/kg | | CHO | [9], [10] | FT, SN |
| 3 | Growth vs osmolality, hybridoma | Raising osmolarity from 290 to 435 mOsm decreased specific growth rate by a factor of about 2 | halving at about +145 mOsm, i.e. about 435 | murine hybridoma 167.4G5.3, IMDM, NaCl/PBS/sucrose | [8] | SN |
| 4 | Growth vs osmolality, CHO | Linear decline of about 0.008 /h per 100 mOsm/kg; about 60% lower growth at 450 vs control 316 mOsm/kg | implied control mu about 0.018 /h; 10% loss at about 340, 50% at about 430 mOsm/kg (INF: 0.5 x 0.018 / 0.00008 = 112 above 316) | CHO, antibody-fusion B1 | [10] | SN (abstract excerpt) |
| 5 | Same study, production runs | No visible change in viable density or titre at 400-450 mOsm/kg; at 460-500, density down about 5% and viability down about 8% | | CHO | [10] | SN |
| 6 | Growth vs osmolality, CHO | mu_max = -1.4 x 10^-4 x Osm + 0.085 (per h, Osm in mOsm/kg), tested 320-500; text elsewhere gives slope -1.1 x 10^-4 (inconsistent within the paper) | mu(320) = 0.040 /h; 10% loss at about 350; 50% at (0.085 - 0.0201)/1.4e-4 = 464 mOsm/kg (INF) | CHO (GS, IgG), NaCl or feed, no significant difference between the two | [9] | FT |
| 7 | Literature slope | -9.3 x 10^-5 /h per mOsm/kg for NaCl-spiked CHO | | CHO | cited in [9] | FT of citing paper |
| 8 | Critical osmolality | "critical osmolality value was 450 mOsm kg-1 for suspension culture", lower for adherent | | CHO, Takagi et al. | cited in [9] | FT of citing paper |
| 9 | Combined CO2 and osmolality | 30% growth-rate reduction at 333 mbar pCO2, 45% with high osmolality added (Kimura and Miller 1996); 400-450 mOsm with 180-213 mbar pCO2 gave about 20% lower viable density (Zhu 2005) | 333 mbar = 250 mmHg | CHO | cited in [11] | FT of citing review |
| 10 | CO2 inhibition onset | "pCO2 > 100 mbar marks the beginning of growth inhibition"; physiological 41-72 mbar | 100 mbar = 75 mmHg | mammalian | [11] | FT |
| 11 | Hybridoma, CO2 and osmolality | "pCO2 and osmolality made dose-dependent contributions to the inhibition of hybridoma cell growth"; more apoptosis at high osmolality | no numbers obtained | hybridoma | [12] | SN (truncated abstract) |
| 12 | Cell size response | Cell volume rises with osmolality; up to 4x cell volume reported at +70% osmolality | relevant to the pL-to-gram conversion | CHO | [9] | FT |
| 13 | Henry's constant, CO2, 37 C, pure water | 25 mmol/(bar L), from 34.5 at 25 C by van't Hoff; real media "may be even doubled" (authors' unpublished data) | 25 / 750.06 = 0.0333 mmol/L/mmHg; 25.3 mmol/L/atm | | [11] | FT |
| 14 | Henry's constant, alternative | 3.0 x 10^-2 mol/L/atm at 37 C | = 30 mmol/L/atm = 0.039 mmol/L/mmHg; at odds with row 13 | | [13] | SN |
| 15 | pK1 carbonic acid | K1 = 10^-6.3 M (temperature and ionic strength not stated); 6.35 at 25 C standard conditions, needs correction for 37 C and ionic strength (medium ionic strength 0.115 M) | | | [11], [14] | FT, SN |
| 16 | CO2 speciation at pH 7 | 83.3% HCO3-, 16.7% CO2 | implies pK1 = 7 - log(83.3/16.7) = 6.30 (INF) | | [11] | FT |
| 17 | pH setpoint in perfusion | 7.0, controlled with CO2 or 8% sodium bicarbonate | | CHO-K1 | [3] | FT |
| 18 | pH range tested | 6.85 to 7.80 in pH-controlled bioreactors at 32.5 and 37.0 C; qEPO roughly constant across pH at 37 C; glucose and glutamine uptake rose with pH | growth rate vs pH not obtained | CHO (EPO) | [15] | SN (abstract fragments) |
| 19 | pH effect, direction | Lower external pH and lower temperature mainly reduce growth and metabolism | no numbers obtained | CHO (Epo-Fc), Trummer 2006 | [16] | SN |

Unsourced standard values (RECALL, flag before use):

- Apparent pK1 of the CO2/bicarbonate system at 37 C and physiological ionic strength: 6.1; plasma CO2 solubility 0.0307 mmol/L/mmHg (23.0 mmol/L/atm). These are the clinical Henderson-Hasselbalch constants. Not confirmed in any source read here. The pure-water value in row 13 is about 8% higher, which is the expected direction (salting out).
- Bicarbonate in classical media: DMEM 44 mM (3.7 g/L), RPMI 1640 about 24 mM (2.0 g/L), with 10% and 5% CO2 respectively. Not confirmed here.
- Osmotic coefficient of NaCl-type 1:1 salts at about 0.15 mol/kg is about 0.93, so 1 mM NaHCO3 or Na-lactate adds about 2 x 0.93 = 1.86 mOsm/kg (ideal upper bound 2.0). No source found that states this for culture medium; only the qualitative statement that base addition and lactate raise osmolality.

Worked example with the RECALL constants (INF): at pH 7.0 and pCO2 100 mbar (75 mmHg), dissolved CO2 = 75 x 0.0307 = 2.3 mM; HCO3- = 2.3 x 10^(7.0 - 6.1) = 18.3 mM, contributing about 18.3 x 1.86 = 34 mOsm/kg with its sodium counter-ion. With row 13 and pK1 6.3 the same point gives 2.5 x 10^0.7 = 12.5 mM. The choice of pK1 changes bicarbonate by about 1.5x, so it is worth pinning down.

---

## 3. Ranges a model could use

Minimum CSPR (conversion at 17 um, 2.57 pL, 1.05 g/mL; multiply mL/g by up to 1.8 for 14 um cells):

| | Low | Central | High | Basis |
|---|---|---|---|---|
| pL per cell per day | 10 | 25 | 50 | Low: [3] plateau at about zero net growth, best optimised medium. Central: [3] 14-30 with mu about 0.15 /day and 15-22 in rows 12 and 19. High: [1], [4], [7], commercial medium, mu 0.3-0.4 /day |
| mL per g wet cells per day | 3.7 | 9.3 | 18.5 | CSPR / 2.70 |

Typical industrial values without a perfusion-optimised medium: 50-300 pL/cell/day (18.5-111 mL/g/day), from [3] row 12.

Growth rate cost of low CSPR: about 0.35 /day at 50 pL/cell/day [1]; about 0.15 /day at 14-30 (figure reading, [3]); about zero at 8-10 [3]. This coupling is the main thing the central value hides.

Osmolality (mOsm/kg), fresh medium baseline 290-320:

| | Low | Central | High | Basis |
|---|---|---|---|---|
| Growth starts to fall (about 10% loss) | 320 (linear from baseline, no threshold) | 345 | 400 | Linear fits in [9], [10]; high value from production runs in [10] showing no visible effect at 400-450 |
| Growth roughly halved | 430 | 450 | 465 | [10] 430 (INF), [8] 435, Takagi 450, [9] 464 (INF) |

Culture pH: setpoint 7.0 [3]; tested range 6.85-7.80 [15]. A model range of 6.8-7.4 is my judgement of conventional practice, not a sourced growth-tolerance window.

---

## 4. Sources

1. Clincke M-F et al. (2013) Very high density of CHO cells in perfusion by ATF or TFF in WAVE Bioreactor, Part I. Biotechnol Prog 29:754-767. https://pmc.ncbi.nlm.nih.gov/articles/PMC3752962/ (full text)
2. Clincke M-F et al. (2013) Part II. Biotechnol Prog 29:768-777. https://pmc.ncbi.nlm.nih.gov/articles/PMC3752935 (full text)
3. Mayrhofer P, Reinhart D, Castan A, Kunert R (2020) Rapid development of clone-specific, high-performing perfusion media from established feed supplements. Biotechnol Prog 36:e2933. https://doi.org/10.1002/btpr.2933 (full text, pages 1-6 and 8-12 of 14; page 7 and supporting information not read)
4. Konstantinov K et al. (2006) The "push-to-low" approach for optimization of high-density perfusion cultures of animal cells. Adv Biochem Eng Biotechnol 101:75-98. https://link.springer.com/chapter/10.1007/10_016 (search snippet only; paywalled)
5. ECI conference abstract, Optimization and evaluation of perfusion media in high cell density mammalian cell culture systems. https://dc.engconfintl.org/ccexvi/69 (snippet; attribution of the 10 pL/c/d figure between this and https://dc.engconfintl.org/biomanufact_iv/50 is uncertain)
6. Brau et al. (2018) ECI conference abstract, Perfusion cell culture: challenges and potentials between lab and manufacturing scale. https://dc.engconfintl.org/ccexvi/144 (snippet)
7. Wolf MKF et al. (2019) Process design and development of a mammalian cell perfusion culture in shake-tube and benchtop bioreactors. Biotechnol Bioeng. https://doi.org/10.1002/bit.26999 (snippet)
8. Ozturk SS, Palsson BO (1991) Effect of medium osmolarity on hybridoma growth, metabolism, and antibody production. Biotechnol Bioeng 37:989-993. https://doi.org/10.1002/bit.260371015 ; PDF at https://deepblue.lib.umich.edu/bitstream/2027.42/37906/1/260371015_ftp.pdf (snippet only; PDF did not parse, PubMed has no abstract)
9. Alhuthali S, Kotidis P, Kontoravdi C (2021) Osmolality effects on CHO cell growth, cell volume, antibody productivity and glycosylation. Int J Mol Sci 22:3290. https://pmc.ncbi.nlm.nih.gov/articles/PMC8037477 (full text, first 100k of 108k characters)
10. Zhu MM et al. (2005) Effects of elevated pCO2 and osmolality on growth of CHO cells and production of antibody-fusion protein B1. Biotechnol Prog 21:70-77. https://doi.org/10.1021/bp049815s (abstract excerpts via search)
11. Blombach B, Takors R (2015) CO2 - intrinsic product, essential substrate, and regulatory trigger of microbial and mammalian production processes. Front Bioeng Biotechnol 3:108. https://pmc.ncbi.nlm.nih.gov/articles/PMC4522908 (full text, first 100k of 132k characters)
12. deZengotita VM, Schmelzer AE, Miller WM (2002) Characterization of hybridoma cell responses to elevated pCO2 and osmolality. Biotechnol Bioeng 77:369-380. PMID 11787010. https://pubmed.ncbi.nlm.nih.gov/11787010/ (truncated abstract)
13. Public Health England culture collections, CO2 concentration and pH control in the cell culture laboratory. https://www.phe-culturecollections.org.uk/culture-collection-news/co2-concentration-and-ph-control-in-the-cell-culture-laboratory/ (snippet; not peer reviewed)
14. NTNU conference paper on CO2 estimation in CHO bioreactors (CAB 2007). https://skoge.folk.ntnu.no/prost/proceedings/dycops2007-and-cab2007/CAB/Monday/Estimation/M32_89_Final_ManuscriptStampedno.pdf (snippet)
15. Yoon SK et al. (2005) Effect of culture pH on erythropoietin production by CHO cells grown in suspension at 32.5 and 37.0 C. Biotechnol Bioeng 89:345-356. https://doi.org/10.1002/bit.20353 (abstract fragments via search)
16. Trummer E et al. (2006) Process parameter shifting, Part I. Biotechnol Bioeng 94:1033-1044. https://doi.org/10.1002/bit.21013 (snippet)

---

## 5. Not found

- Konstantinov 2006 experimental CSPR steps and the minimum reached (only the "below 0.05 nL/cell/day" target, from a snippet).
- Ozturk 1996, Dowd et al., Warikoo 2012, Bielser 2018, Chotteau 2015, Wolf and Morbidelli 2020: no numbers obtained. Wolf 2019 minimum CSPR value not obtained.
- CSPR data for HEK and PER.C6; hybridoma only via the Konstantinov snippet.
- Cell diameter in the low-CSPR study [3] (page 7 not read) and for hybridoma.
- A growth-supporting minimum CSPR measured with a bleed at steady state (mu fixed, CSPR pushed down). The lowest figures are plateau cultures.
- Whether adaptation raises osmolality tolerance: nothing found in the sources read.
- Kimura and Miller 1996, Takagi, Kiehl 2011 primary data; deZengotita 2002 numbers.
- Per-osmolality growth rates from Ozturk and Palsson 1991 (only the 290 to 435 halving, snippet).
- A sourced osmotic coefficient or mOsm/kg per mM for sodium bicarbonate or sodium lactate in medium.
- Sourced typical bicarbonate concentration in CHO bioreactor media.
- Growth rate as a function of pH for CHO (tolerated range); only setpoints and tested ranges.
- Apparent pK1 at 37 C in culture medium and a peer-reviewed Henry's constant in medium rather than pure water.
