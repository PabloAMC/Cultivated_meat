# Species-specific cell parameters for cultivated-meat presets

Compiled 2026-11-14 from a bounded web search (about 45 tool calls). Every number is quoted as the source states it, then converted. Conversions and inferences that are mine are marked **[conv]** or **[inference]**.

Access levels, used throughout:

- **FT** = read in the full text.
- **ABS** = read in the abstract only.
- **SNIP** = seen only in a search-engine snippet; verify before publishing.
- **PRESS** = company claim or press, not peer-reviewed.

Baseline being replaced (Humbird 2021 model cell): 3,000 pg wet, 24 h doubling, 37 °C, P = 0.148 x M^0.75 pW.
[conv] 3000^0.75 = 405, so P = 60 pW per cell. With an oxycaloric equivalent of about 469 kJ/mol O2 (my assumption; check which value the model uses), that is 1.28e-16 mol O2/cell/s = 0.46 pmol/cell/h = 11 pmol/cell/day = 0.46 mmol per 10^9 cells per h = 0.15 mmol O2 per g wet per h.

## (a) Table by species group

| Species group | 1. Doubling time (line, medium, format) | 2. Temp | 3. Cell size / mass | 4. Specific O2 uptake, Q10 | 5. Highest suspension density (vessel) | 6. Continuous / spontaneously immortalised lines |
|---|---|---|---|---|---|---|
| **Chicken** | Best and typical: 20 ± 2 h after immortalisation, down from about 200 h initially (spontaneously immortalised fibroblasts; SNIP of figure text) [1]. Primary cells 25-150 h (SNIP) [1]. Doubling time in serum-free suspension: not retrieved (paywalled). | Not retrieved (methods paywalled). | 108 x 10^6 cells/mL = 36% w/v [1]; 130 x 10^6 cells/mL = 43% w/v [2] (both ABS). [conv] 0.36 g/mL / 1.08e8 = 3.3 ng = about 3,300 pg wet per cell (assumes % w/v is wet biomass). | No measurement found. | 130 x 10^6 cells/mL, 43% w/v, TFF perfusion, serum-free, over 20 days (ABS) [2]. Vessel volume not retrieved; the 50,000 L figure in [2] is a theoretical facility, not a run. | Yes: spontaneous immortalisation without genetic modification [1]. Lines are tied to Believer Meats; public availability not established. |
| **Cattle** | Typical serum-free: 39 h average over 7 passages (primary bovine satellite cells, Beefy-9, adherent; FT) [3]. Best: 17.4 h (P12-16) falling to 15.1 h (P32-36) for engineered immortalised iBSC, adherent (SNIP of preprint) [4]; vendor lists about 15 h [5]. Engineered iBSC in serum-free Beefy-9: 55-82 h (SNIP) [6]. | 37 °C is standard for these papers; not re-verified in text. | No direct measurement found. | No measurement found. | No measured single-cell suspension density found. Mosa Meat scale-up modelling uses 10 x 10^6 cells/mL as a planning assumption (SNIP) [7]. Microcarrier work reported at 3 L scale, density not retrieved (SNIP) [8]. | Engineered (not spontaneous) immortalised line iBSC1 exists and is sold via Kerafast [4][5]. No spontaneously immortalised bovine line found in this search. |
| **Pig** | Not retrieved for the muscle-derived line in [9]. Vendor claim: 14-16 h for porcine iPSC in 2D and 3D (PRESS) [10]. | Not retrieved. | Not retrieved. | No measurement found. | 2,000 L bioreactor yielded 97.18 kg wet biomass, serum-free suspension, semi-continuous (ABS; preprint, not peer-reviewed) [9]. [conv] 48.6 g/L wet if this is one 2,000 L working volume; it may be cumulative over harvests, so treat as an upper bound on a single-harvest density. Vendor claims: over 30 x 10^6 cells/mL fed-batch, over 60 x 10^6 perfusion for piPSC (PRESS) [10]. | Yes: spontaneously immortalised porcine muscle-derived line, over 255 population doublings by day 300, no genetic modification (ABS; preprint) [9]. Availability not stated. |
| **Fin fish** | Best: 24.3 ± 4.9 h post-crisis (Atlantic mackerel Mack1, L-15-based medium with 20% FBS, adherent; 63.9 ± 19.1 h pre-crisis; Mack2 22.9 ± 4.0 h; FT) [11]. Typical: about 2 days at the 20 °C optimum for rainbow trout RTG-2, slower at lower temperature (SNIP) [12]; GFI says many fish lines take several days (SNIP) [13]. Goldfish GTFe-2: 35 h at 27 °C, 25 h at 37 °C (SNIP; primary citation not confirmed) [14]. Zebrafish, salmon, seabass: no doubling-time data found. | 27 °C, no CO2 (mackerel; FT) [11]. 15-30 °C across fish lines [15]. 20 °C optimum for RTG-2 [12]. | Mackerel: 16.8 ± 0.17 µm post-crisis, 18.3 ± 0.53 µm pre-crisis (FT) [11]. [conv] sphere volume 2,480 µm3, about 2,500-2,600 pg wet at 1.0-1.05 g/mL. | No absolute per-cell or per-gram value found. Seahorse studies exist but are normalised per well or protein [16][17]. Sturgeon larval line: basal respiration significantly higher at 28 °C than at 20 or 25 °C, no change from 20 to 25 °C (FT) [16]. No measured Q10 for a fish cell line found. | No peer-reviewed suspension density found. CellX: nearly 20 x 10^6 cells/mL in a 200 L bioreactor, species unspecified (PRESS) [18]. Bluu Seafood: scaffold-free suspension adaptation, no numbers (PRESS) [19]. | Yes. Mack1 is spontaneously immortalised, over 130 passages (FT) [11]. Many older continuous fish lines exist (RTG-2, zebrafish ZF4 and others), mostly not muscle and not food-oriented. |
| **Crustaceans** | No data: no proliferating line. | 25-30 °C typical for crustacean cell culture [15]. | No data. | No data. | No data. | **No.** No continuous crustacean line as of 2019 [15]; continuous shrimp line still unavailable (ABS, 2024) [20]; 2025 review notes the current lack of cell lines (ABS) [21]. A 2025 paper uses a line named PmLyO-Sf9, which from its name looks like a shrimp-Sf9 hybrid; paper not read [22]. A patent claims a continuous shrimp culture method; not peer-reviewed evidence [23]. |
| **Insect (reference)** | Sf9: 20.7-26.9 h; High Five: 18.7-22 h; pooled value 22.7 h. S2R+: 34-42 h; value 38.5 h (FT, literature compilation) [24]. | 27 °C (Sf9, High Five); 28 °C (S2) [24]. | Sf9/High Five 2.16e-15 m3 (range 1.15-3.32e-15); S2 5.73e-16 m3 [24]. [conv] 2,160 µm3, about 16 µm sphere, about 2,200-2,300 pg; S2 573 µm3, about 10 µm, about 600 pg. | Sf9/High Five mean 3.07e-13 mol/h/cell, most values 1.5-6.6e-13; S2 1.12e-14 mol/h/cell [24]. Sf9 max 7.3e-17 mol O2/cell/s, S2 3.1e-18 mol O2/cell/s in a 1 L serum-free bioreactor (SNIP) [25]. [conv] 0.31 and 0.26 pmol/cell/h for Sf9; about 0.011 for S2. Per gram: 0.31 pmol/h / 2.27 ng = about 0.14 mmol O2/g wet/h. | Sf9 0.3-1.9 x 10^7 cells/mL; TEA assumes 2.0 x 10^7. S2 up to 1.04 x 10^8 cells/mL [24]. Sf9 10.7 x 10^6 and S2 51.2 x 10^6 cells/mL at 1 L (SNIP) [25]. Largest industrial vessel: expresSF+ used from 2 to 21,000 L [26]. | Yes: Sf9, Sf21, High Five, S2 are continuous, serum-free, suspension lines, commercially available. |

## (b) Items 7-9

### 7. Do fish cells cut oxygen demand, cooling load or CO2?

**What the literature claims (qualitative only).** Rubio et al. 2019 [15] argue that fish cells tolerate hypoxia, which could reduce the need for active oxygenation; that fish muscle has high buffering capacity; and that lower culture temperature (15-30 °C) reduces the energy needed to hold temperature and could reduce heat-transfer needs at scale. They give no measured oxygen uptake, heat output or CO2 production rates. Saad et al. 2023 [11] culture mackerel cells at 27 °C without CO2, which is a demonstrated operating simplification, not a metabolic-rate measurement.

**What I could not find.** No published measurement of specific oxygen uptake, heat generation or CO2 evolution for a fish cell line in absolute per-cell or per-gram units. No bioreactor mass or heat balance for fish cells. No BlueNalu, Wildtype or Finless publication with such data.

**GFI November 2025 report [27].** The technical summary (read in full) contains no species-specific or fish-specific parameters and nothing on cooling load. Its relevant statements: few datasets link oxygen consumption to growth rate; reported cell water content varies from about 70% to nearly 90%; estimating mass from diameter is unreliable; fastest doubling times in the literature are 4-8 h, with cultivated-meat lines expected at 12-24 h after optimisation. The full report sits behind a download form and was not read.

**Temperature dependence, mammalian cells only.**
- Jorjani and Ozturk 1999 [28]: specific O2 consumption falls about 10% per 1 °C; Arrhenius activation energy 80-90 kJ/mol between 6 and 37 °C (BHK, hybridoma, CHO; ABS). [conv] Q10 of 2.8-3.2 between 27 and 37 °C.
- Goudar et al. 2011 [29]: CHO perfusion steady states, qO2 3.97 pmol/cell/day at 30.5 °C and 5.53 at 37.5 °C (ABS). [conv] Q10 of about 1.6.
- The two disagree by a factor of two in Q10; the first is acute cooling in a respirometer, the second is steady-state culture.

**[inference] For the model.** The sourced data do not support a lower oxygen demand per unit of biomass grown for fish. Mack1 doubles in 24 h at 27 °C, the same as the model cell, and Sf9 at 27 °C has a per-cell O2 uptake (about 0.3 pmol/cell/h) in the same range as CHO at 37 °C (0.21-0.29). Oxygen demand appears to track growth rate and cell size more than setpoint temperature. A defensible fish preset changes temperature, cell mass and CO2 control, and leaves specific O2 uptake at the allometric value with a wide uncertainty band. Unsourced engineering note: a lower setpoint reduces the temperature difference to cooling water, which makes heat removal harder, not easier, in warm climates.

### 8. Insect cells

- **Doubling time, temperature, size, density, O2 uptake:** see table; all from the literature compilation in Ashizawa et al. 2022 [24], Tables 1 and A1.
- **Caution on [24]:** two O2 entries (2.1e-15 and 4.5e-15 mol/h/cell) sit 100-fold below the rest and look like outliers or unit errors. Its mammalian comparator, 1.8e-14 mol/h/cell inherited from Risner et al., is about 10-fold below measured CHO values in item 9, so its conclusion that insect cells consume more O2 per cell than mammalian cells rests on a low mammalian baseline.
- **Independent check:** Sf9 7.3e-17 mol/cell/s and S2 3.1e-18 mol/cell/s (SNIP) [25] agree with [24] after conversion.
- **Infected cells:** baculovirus-infected Sf9 8.6-26e-17 mol/cell/s (SNIP) [30]. [conv] 0.31-0.94 pmol/cell/h. Not relevant to food biomass, but it is the range often quoted.
- **Largest vessel:** expresSF+ cells used at 2 to 21,000 L (FT) [26]; the author worked for Protein Sciences, the Flublok maker. A second review mentions 2 x 21,000 L capacity (SNIP); operator not confirmed in what I read. Flublok antigens were also reported at 650 L, and CDMO GMP runs at 50-2,000 L (SNIP).
- **Claimed advantages:** more resilient in culture; lower requirements for CO2 and growth factors; ready adaptation to serum-free medium; suspension growth at high density [24][31]. [24] finds cost still dominated by cell size and medium.

### 9. Mammalian production-line baselines

Unit identity: 1 pmol/cell/h = 1 mmol per 10^9 cells per h = 24 pmol/cell/day.

| Line | As stated | [conv] mmol per 10^9 cells per h | Access | Source |
|---|---|---|---|---|
| CHO, perfusion, 36.5 °C | 5.14-5.77 pmol/cell/day; qCO2 5.31-6.36; RQ 0.98-1.14 | 0.21-0.24 | ABS | [29] |
| CHO, batch and continuous | 2.85e-13 and 2.54e-13 mol/cell/h | 0.29 and 0.25 | SNIP | [32] |
| Hybridoma | 4.2-13e-17 mol/cell/s | 0.15-0.47 | SNIP | [30] |
| Hybridoma, falling with density | 7 to 2.9 µmol/min per 10^9 cells | 0.42 to 0.17 | SNIP | [33] |
| Animal cells, average | 0.2e-12 mol/cell/h | 0.2 | SNIP | [34] |
| Mammalian cells, full range | under 1 to over 350 amol/cell/s | under 0.004 to over 1.26 | ABS | [35] |
| HEK293 | no value found | n/a | n/a | n/a |

Ranking at a given temperature: hybridoma lowest, CHO highest, BHK between (ABS) [28]. Density between 1 and 20 x 10^6 cells/mL does not change specific uptake [28].

[conv] The Humbird model cell at 0.46 mmol per 10^9 cells per h is about twice the measured CHO value per cell. Whether it is high per gram depends on CHO cell mass, which I did not source.

## (c) Sources

1. Pasitka L. et al. (2023). Spontaneous immortalization of chicken fibroblasts generates stable, high-yield cell lines for serum-free production of cultured meat. Nature Food 4:35-50. https://doi.org/10.1038/s43016-022-00658-w
2. Pasitka L. et al. (2024). Empirical economic analysis shows cost-effective continuous manufacturing of cultivated chicken using animal-free medium. Nature Food 5:693-702. https://doi.org/10.1038/s43016-024-01022-w
3. Stout A.J. et al. (2022). Simple and effective serum-free medium for sustained expansion of bovine satellite cells for cell cultured meat. Communications Biology 5:466. https://doi.org/10.1038/s42003-022-03423-8
4. Stout A.J. et al. (2022 preprint; published ACS Synthetic Biology 2023). Immortalized bovine satellite cells for cultured meat applications. https://www.biorxiv.org/content/10.1101/2022.12.02.518927v1.full
5. Kerafast product page, Immortalized Bovine Satellite Cell Line (iBSC1). https://kerafast.com/item/5997/immortalized-bovine-satellite-cell-line-ibsc1
6. Stout A.J. et al. (2023). Engineered autocrine signaling eliminates muscle cell FGF2 requirements for cultured meat production. bioRxiv. https://doi.org/10.1101/2023.04.17.537163
7. Mosa Meat authors (2024). Frontiers in Bioengineering and Biotechnology. https://doi.org/10.3389/fbioe.2024.1443914 (title not captured)
8. Scientific Reports, April 2025, microcarrier addition for bovine satellite cells, 3 L scale. https://doaj.org/article/c6edca91e0874b6393953259b8ded4f9 (authors and title not captured)
9. Zhao L. et al. (2026). Spontaneously immortalized porcine cells support scalable cultured pork production in serum-free suspension. Research Square preprint. https://doi.org/10.21203/rs.3.rs-11402436/v1
10. Roslin Technologies, porcine iPSC product page. https://www.roslintech.com/cells/porcine-ipsc/
11. Saad M.K. et al. (2023). Continuous fish muscle cell line with capacity for myogenic and adipogenic-like phenotypes. Scientific Reports 13:5098. https://doi.org/10.1038/s41598-023-31822-2
12. Plumb J.A., Wolf K. (1971). Fish cell growth rates: quantitative comparison of RTG-2 cell growth at 5-25 °C. In Vitro 7:42-45. https://doi.org/10.1007/BF02619003
13. GFI, Promoting stemness and proliferation in fish cell cultures. https://gfi.org/solutions/fish-cell-proliferation/
14. Goldfish GTFe-2 line data, scanned article. https://archive.org/download/biostor-106813/biostor-106813.pdf (citation not confirmed)
15. Rubio N., Datar I., Stachura D., Kaplan D., Krueger K. (2019). Cell-based fish: a novel approach to seafood production and an opportunity for cellular agriculture. Frontiers in Sustainable Food Systems 3:43. https://doi.org/10.3389/fsufs.2019.00043
16. Lutze P. et al. (2024). Effects of temperature adaptation on the metabolism and physiological properties of sturgeon fish larvae cell line. Cells 13:269. https://doi.org/10.3390/cells13030269
17. Beck B.H., Fuller S.A. (2012). The impact of mitochondrial and thermal stress on the bioenergetics and reserve respiratory capacity of fish cell lines. Journal of Aquatic Animal Health 24:244-250. https://doi.org/10.1080/08997659.2012.720637
18. Green Queen, CellX cultivated fish report. https://greenqueen.com.hk/?p=67443
19. The Fish Site, Bluu Seafood suspension milestone. https://thefishsite.com/articles/eu-cultivated-seafood-firm-reaches-new-r-d-milestone-bluu-seafood
20. Zhao Y., Guo L., Guo H. (2024). Routine development of long-term primary cell culture and finite cell line from the hemolymph of greasyback shrimp (Metapenaeus ensis) and virus susceptibility. Aquaculture. (URL not captured; found via Europe PMC)
21. Musgrove L., Russell F.D., Ventura T. (2025). Considerations for cultivated crustacean meat. Critical Reviews in Food Science and Nutrition 65. https://doi.org/10.1080/10408398.2024.2342480
22. Gopika V.S. et al. (2025). Marine Biotechnology. https://doi.org/10.1007/s10126-025-10505-1
23. US patent 11,873,509, Method for continuous culture of shrimp cells. https://patents.justia.com/patent/11873509
24. Ashizawa R. et al. (2022). Entomoculture: a preliminary techno-economic assessment. Foods 11:3037. https://pmc.ncbi.nlm.nih.gov/articles/PMC9564176/
25. Insect cells respiratory activity in bioreactor (2008). Cytotechnology. https://doi.org/10.1007/s10616-007-9118-8 (authors not captured)
26. Felberbaum R.S. (2015). The baculovirus expression vector system: a commercial manufacturing platform for viral vaccines and gene therapy vectors. Biotechnology Journal 10:702-714. https://pmc.ncbi.nlm.nih.gov/articles/PMC7159335
27. Harsini F., Frohlich B., Swartz E. (2025). Technical summary for optimizing cultivated meat techno-economics: cell growth modeling review and recommendations. GFI. https://doi.org/10.62468/ohpu7135 (full report: https://doi.org/10.62468/QBXK7437)
28. Jorjani P., Ozturk S.S. (1999). Effects of cell density and temperature on oxygen consumption rate for different mammalian cell lines. Biotechnology and Bioengineering 64:349-356. https://pubmed.ncbi.nlm.nih.gov/10397872/
29. Goudar C.T., Piret J.M., Konstantinov K.B. (2011). Estimating cell specific oxygen uptake and carbon dioxide production rates for mammalian cells in perfusion culture. Biotechnology Progress 27:1347-1357. https://doi.org/10.1002/btpr.646
30. Weidner T. et al. (2017). The components of shear stress affecting insect cells used with the baculovirus expression vector system. Zeitschrift fuer Naturforschung C. https://doi.org/10.1515/znc-2017-0066
31. Rubio N.R., Fish K.D., Trimmer B.A., Kaplan D.L. (2019). Possibilities for engineered insect tissue as a food source. Frontiers in Sustainable Food Systems 3:24. https://doi.org/10.3389/fsufs.2019.00024
32. EPFL record of a CHO oxygen uptake study. https://graphsearch.epfl.ch/en/publication/80790 (primary citation not captured)
33. Wohlpart D., Kirwan D., Gainer J. (1990). Effects of cell density and glucose and glutamine levels on the respiration rates of hybridoma cells. Biotechnology and Bioengineering 36. https://zendy.io/title/10.1002/bit.260360611
34. Ruffieux P.-A., von Stockar U., Marison I.W. (1998). Measurement of volumetric (OUR) and determination of specific (qO2) oxygen uptake rates in animal cell cultures. Journal of Biotechnology 63:85-95. (citation from memory; seen only as a snippet)
35. Wagner B.A., Venkataraman S., Buettner G.R. (2011). The rate of oxygen utilization by cells. Free Radical Biology and Medicine 51:700-712. https://doi.org/10.1016/j.freeradbiomed.2011.05.024

## (d) What is not known (from this search)

- **Fish cell oxygen uptake in absolute units.** No per-cell or per-gram value, no heat or CO2 production rate, and no measured Q10 for any fish cell line.
- **Fish suspension density.** No peer-reviewed number; only a company claim of about 20 x 10^6 cells/mL at 200 L.
- **Salmon, zebrafish, seabass.** No doubling time, cell size or density found for food-relevant muscle or fibroblast lines.
- **Crustaceans.** Every parameter, because no continuous line exists. I did not read the GFI seafood cell line guide v2.0 (May 2026); the page exceeded the fetch limit.
- **Oxygen uptake of any cultivated-meat line.** Nothing found for chicken fibroblasts, bovine satellite cells or porcine lines. GFI [27] names this as a data gap.
- **Chicken and pig methods details.** Culture temperature, suspension doubling time, vessel volume and cell diameter for [1], [2] and [9] were not retrieved (paywall or preprint body not accessible).
- **Bovine and porcine cell mass.** No direct measurement found; GFI [27] warns that diameter-based mass estimates are unreliable.
- **Bovine suspension density.** No measured single-cell suspension figure found.
- **HEK293 oxygen uptake.** No value found.
- **Items marked SNIP.** Sources 4, 6, 7, 8, 12, 14, 25, 30, 32, 33, 34 were not opened; numbers need checking against the papers.
