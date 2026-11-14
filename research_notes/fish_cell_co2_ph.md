# CO2 tolerance and pH of fish, crustacean and insect cells: literature lookup

Date: 2026-11-14. Web search and reading only. Question: should the model's single dissolved-CO2 limit (100 mbar = 75 mmHg, from CHO practice) differ for fish, crustacean or insect cells, and what pH are they cultured at.

Conventions
- 1 mmHg (= 1 Torr) = 1.333 mbar; 1 kPa = 10 mbar; 1 atm = 1013.25 mbar. Model default: 100 mbar / 1.333 = 75.0 mmHg.
- "Access" column: **FT** = full text read; **AB** = abstract read; **SN** = search-engine snippet or summary only (number not checked against the paper; treat as provisional).
- Anything marked **[my inference]** or **[my arithmetic]** is mine, not the source's.
- mg/L to partial pressure conversions are mine, using the Henry's constants in section 4 (pure water; in seawater CO2 is roughly 15-20% less soluble, so the same mg/L corresponds to a somewhat higher partial pressure; that correction is from my background knowledge, not looked up here).

Headline: **no measurement of growth versus CO2 partial pressure was found for any fish or crustacean cell line.** The only cell-level growth-versus-pCO2 data found outside mammals are for insect Sf-9 cells. Fish and shrimp values below are therefore inferences from whole-animal physiology and from routine culture practice.

---

## 1. In-vivo blood / hemolymph CO2 partial pressure and pH

| Group / species | pCO2 as stated | mbar [my arithmetic] | pH | Conditions | Source | Access |
|---|---|---|---|---|---|---|
| Rainbow trout, arterial, baseline | "about 1.7 torr" | 1.7 x 1.333 = 2.3 | about 7.95 | normocapnic water; rose to 6.2 torr (8.3 mbar) and pH 7.38 within 20 min of hypercapnia | [1] | SN |
| Rainbow trout, temperature effect | PCO2 "did not change with temperature"; pH regulated by changing plasma HCO3- | - | - | - | [1] | SN |
| White sturgeon (not a teleost), arterial, after return to normocapnia | 2.5 +/- 0.14 Torr | 3.3 | 7.75 +/- 0.04; HCO3- 7.4 mmol/L | post-recovery values, not a clean baseline | [2] | SN |
| A teleost under sustained hypercapnia (species not shown in snippet) | arterial PCO2 about 21.9 mmHg | 29.2 | fell only 0.15 units; plasma HCO3- rose to about 39.8 mmol/L | shows whole-animal compensation by bicarbonate accumulation | [3] | SN |
| Salmon, tilapia, seabass, zebrafish | **not found** | | | targeted search returned no baseline values | | |
| Green crab *Carcinus maenas*, hemolymph | "mean PCO2 was 2.94 Torr" | 3.9 | 7.85; HCO3- 9.85 mmol/L | 32 ppt seawater, 13.8 C; PCO2 fell to 1.70 Torr (2.3 mbar) at 50 ppt | [4] | FT |
| *Carcinus maenas*, ambient range used experimentally | water PCO2 "ca. 0.3 Torr" (low) and "ca. 4.3 Torr" (high) | 0.4 and 5.7 | - | hemolymph acidosis develops with raised hemolymph PCO2 | [5] | SN |
| Penaeid shrimp (*L. vannamei*, *P. monodon*) hemolymph pCO2 and pH | **not found** (papers that measured them were located, [6] [7], but control values were not retrievable) | | | | | |
| Insects, hemolymph pH (older in-vitro surveys) | - | - | roughly 6.4 to 8.0 across species; *Bombyx mori* 6.4-7.2; *Malacosoma americanum* 6.4-7.4 | older pooled-sample measurements, flagged as of questionable accuracy by a later review | [8] [9] | SN |
| Insects, in vivo (dragonfly nymphs) | - | - | 7.8 (aeshnid), 7.9 (libellulid) | modern in-vivo measurement | [8] | SN |
| Insect hemolymph pCO2 | **not found** | | | | | |
| Cow | 35-44 mm Hg | 46.7-58.7 | 7.35-7.50; HCO3- 20-30 mEq/L | reference range; table does not say arterial or venous | [10] | FT (table) |
| Horse | 36-46 mm Hg | 48.0-61.3 | 7.32-7.44 | same table | [10] | FT (table) |
| Chicken (Lohmann pullets) | mean 26.85 mm Hg | 35.8 | mean 7.49 | point-of-care reference study; sampling site not confirmed arterial | [11] | SN |
| Human arterial | about 40 mmHg (figure given in the task brief; standard textbook value, not looked up here) | 53.3 | about 7.40 | - | - | not sourced |

Reading: water-breathers (fish, crabs) run blood/hemolymph pCO2 of about 2-4 mbar, roughly 15-25 times lower than mammals (47-61 mbar), at a higher pH (7.8-7.95 at 10-15 C versus 7.4 at 37 C). The comparative-physiology reviews named in the brief (Heisler; Brauner and Baker; Perry and Gilmour; Truchot) could not be opened (one host unreachable, others paywalled), so the fish row rests on one trout study snippet plus the sturgeon value.

### 1b. Hemolymph osmolality (crustaceans)

| Species | Value as stated | Source | Access |
|---|---|---|---|
| *Penaeus monodon* body fluid | "687 (range of 687 to 750) mOsmol kg-1" | [12] | SN |
| *L. vannamei*, acclimated to 30 ppt | hemolymph regulated "slightly below ambient water osmolality" (no number in snippet) | [13] | SN |
| *L. vannamei*, at 15 and 5 ppt | hyper-regulates, hemolymph "between 200 and 400 mOsm above ambient" | [13] | SN |
| *L. vannamei*, transferred to 18 ppt | "declined slowly from 800 mOsm to 700 mOsm after 6 h and thereafter remained stable for 7 days" | [14] | SN |
| *Carcinus maenas* | osmoregulates below about 26 ppt, osmoconforms above (so about seawater osmolality at 32 ppt; number not extracted) | [4] | FT |

For comparison, mammalian culture media are about 280-320 mOsm/kg (background knowledge, not looked up).

---

## 2. Whole-animal tolerance to dissolved CO2 in aquaculture

Conversion factors used [my arithmetic, section 4]: 1 mg/L CO2 = 0.51 mbar at 15 C; 0.68 mbar at 25 C; 0.73 mbar at 28 C (pure water).

| Species / system | Limit or effect as stated | mbar [my arithmetic] | Source | Access |
|---|---|---|---|---|
| Atlantic salmon post-smolts, 43 days, flow-through, 15-16 C | low group "about 10.6 mg/L" "may represent a safe level"; plasma chloride fell at about 26 mg/L; growth and blood measures worse at about 44 mg/L; no nephrocalcinosis in any group | 10.6 x 0.51 = 5.4; 26 -> 13; 44 -> 22 | [15] Fivelstad et al. 1998 | SN |
| Atlantic salmon post-smolts, brackish RAS, 12 weeks, six levels 5-40 mg/L | growth "decreased linearly with increasing CO2"; maximum growth "below 12 mg/L"; each +10 mg/L costs about 0.2 units of thermal growth coefficient; no clear safe threshold | 12 -> 6.1; 40 -> 20 | [16] Mota et al. 2019 | SN (abstract-level) |
| Atlantic salmon post-smolts, commercial practice | "suggested to range from 15 to 20 mg/L" | 7.7-10 | [16] citing Fivelstad reviews | SN |
| Atlantic salmon, freshwater RAS, 384 days | "up to 20 mg/L CO2 without significantly impacting fish health and performance" at alkalinity 237 mg/L as CaCO3; no nephrocalcinosis | 10 | [17] Good/Summerfelt group | SN |
| Welfare standards | rainbow trout "< 10 mg CO2/L"; Atlantic salmon smolts "< 15 mg CO2/L" | 5.1; 7.7 | [18] | SN |
| Juvenile Atlantic salmon | "linear decrease in specific growth rate in the range of 2.9 - 25 mg CO2/L" | 1.5-13 | [18] | SN |
| Freshwater fish, general | estimated safe concentration for extended exposure 20 mg/L | 14 at 25 C | [19] Boyd | SN |
| Fish, general | avoid 10 mg/L or more; "most species tolerate up to 60 mg/L or more ... if there is plenty of dissolved oxygen" | 6.8; 41 at 25 C | [20] Boyd | SN |
| Nile tilapia, 114 g juveniles, 35 days | 12 h/day at 15-30 mg/L (oxygen held at 100% saturation) cut growth 38%, feed conversion 30% worse; survival unaffected | 15 x 0.73 = 11; 30 -> 22 (28 C assumed) | [21] Kubitza 2025 citing Hamad et al. 2023 | FT (article); primary not read |
| Nile tilapia | metabolic rates fall with dose up to 60 mg/L, partial recovery after 24 h | 44 | [22] DTU | SN |
| Tilapia, practical guidance | "active and healthy at CO2 concentrations of 40 mg/L"; not appreciably toxic unless "> 50 mg/L" for extended periods | 29; 37 | [23] [24] | SN |
| Marine shrimp | 96 h LC50 60 mg/L; estimated safe concentration for extended exposure "6" mg/L (species not named) | 44; 4.4 (pure-water factor at 28 C; higher in seawater) | [19] Boyd | SN |
| *Penaeus vannamei*, RAS | at 36 mg/L survival 58% versus 92% at 12 mg/L; growth 60% of control; feed conversion 2.8 vs 2.3; water pH 6.7 vs 7.3; histological damage in muscle, hepatopancreas, gill | 36 -> 26; 12 -> 8.8 | [21] citing Casillas-Hernandez et al. 2021 | FT (article); primary not read |
| *L. vannamei*, with hypoxia and *Vibrio* challenge | "Pco2 = 1.8 kPa; Po2 = 4 kPa" increased mortality | 18 | [25] | SN |
| *P. vannamei*, seawater pCO2 5000 and 10,000 uatm | standard metabolic rate more than doubled | 5.1 and 10.1 | [26] | SN |
| *L. vannamei* post-larvae, seawater pH | pH 7.6 to 7.0 "significantly adverse"; another study: 100 days at pH 7.6 no direct fitness effect | - | [27] | SN |
| Ponds and biofloc, general | "Levels above 10 mg per liter require corrective actions"; biofloc systems "often exceed 40 mg/L"; free CO2 is absent above pH 8.3 | 6.8; 27 | [21] [20] | FT; SN |
| Timmons and Ebeling textbook limits | **not found / not verified** | | | |
| Shrimp pond pH recommendation (Boyd-type range) | **not found** in the sources reached | | | |

Reading: chronic whole-animal limits are 5-10 mbar for salmonids, and effects on tilapia and shrimp growth appear at 10-25 mbar. All are far below the 100 mbar mammalian-cell default. **[my inference]** These limits are set by whole-organism mechanisms (gill gas exchange, blood oxygen transport with pH-sensitive haemoglobin or hemocyanin, kidney calcification, ion balance) and need not carry over to isolated cells in a pH-controlled medium.

---

## 3. Cell-level evidence

### 3a. Fish cells

| Item | Finding as stated | Source | Access |
|---|---|---|---|
| Growth of any fish cell line versus pCO2 or bicarbonate | **not found** | | |
| RTG-2 (rainbow trout gonad) pH | "growth is inhibited at a pH higher than 7.4" | [28] DSMZ | SN |
| RTG-2 medium pH | complete medium "normal pH (7.0 to 7.6)" (generic ATCC handling wording) | [29] ATCC CCL-55 | SN |
| 13 salmonid and 14 non-salmonid lines | nine salmonid lines "grew well in the normal sodium bicarbonate buffer in Eagle's MEM"; 11 non-salmonid lines grew better with HEPES-bicarbonate or Tris-bicarbonate; optimum 15-20 C salmonid, 20-30 C non-salmonid | [30] Fernandez et al. 1993 | SN (abstract-level) |
| Buffer levels used | Eagle's MEM with sodium bicarbonate 26 mM, or bicarbonate 8.9 mM plus Tris 16 mM | [31] Hokkaido group | SN |
| CO2-free practice | Leibovitz L-15 (buffered by salts and amino acids, no CO2 incubator) "widely used for fish cell lines"; lines grown routinely in L-15 at 28 +/- 2 C | [32] CMFRI manual | SN |
| Incubation temperatures | CHSE-214 at 15 C; EPC at 15-25 C | [33] AFS-FHS Blue Book | SN |
| Hypercapnia, trout hepatoma line RTH 149 | intracellular pH fell "without recovery as long as the elevated CO2 was maintained"; recovery from an acid load was slower under hypercapnia; a Na+/H+ exchanger is implicated; the line recovers faster than primary hepatocytes. CO2 level used **not retrieved** | [34] J Comp Physiol B 181:883-892 (2011) | SN |
| Antarctic fish primary hepatocytes | protein synthesis "inhibited by about 80% under conditions of severe acidosis" | [35] | SN |
| Atlantic cod gill and liver cells | in gill cells acidosis depressed respiration "independent of PCO2" | [36] | SN |
| Zebrafish, EPC, BF-2, CHSE-214 specific pH optima | **not found** | | |

**[my inference]** Routine growth of salmonid lines in Eagle's MEM with 26 mM bicarbonate implies those cells proliferate at a CO2 partial pressure of roughly 40-50 mbar. Arithmetic: at pH 7.4 and 20 C, taking an apparent pK1 of about 6.18 (the thermodynamic 6.38 of section 4 less about 0.2 for ionic strength, the same offset that turns 6.30 into the familiar 6.1 at 37 C), dissolved CO2 = 26 / 10^(7.4-6.18) = 1.57 mM; divided by 0.0390 mol/(L atm) = 0.040 atm = 41 mbar. The same sum at 37 C gives 26 / 10^(7.4-6.10) = 1.30 mM / 0.0249 = 0.052 atm = 53 mbar, i.e. the standard 5% CO2, which checks the method. The sources did not state the CO2 percentage or the resulting pH, so this is an inference, not a measurement.

### 3b. Fish versus mammalian muscle buffering

| Item | Value as stated | Source | Access |
|---|---|---|---|
| Rainbow trout white muscle intracellular pH at rest | 7.21 (falls to 6.62 after exhaustive exercise); another study 7.31 | [37] Milligan and Wood 1986; [38] | SN |
| Yellow perch white muscle non-bicarbonate buffering | 40.7 +/- 3.1 slykes (March) to 53.7 +/- 2.8 slykes (July) | [38] | SN |
| Eelpout *Zoarces viviparus* white muscle | 34.4 +/- 2.3 meq pH-1 kg cell water-1 at 12 C | [39] | SN |
| Ordering across vertebrates | marine mammals and pelagic fish buffer more than terrestrial mammals and deep-sea or shallow-water fish respectively | [40] citing Castellini and Somero 1981 | SN |
| Mammalian muscle value in slykes for direct comparison | **not found** (Castellini and Somero 1981 table not reached) | | |

### 3c. Insect cells

| Item | Finding as stated | mbar [my arithmetic] | Source | Access |
|---|---|---|---|---|
| Sf-9, 27 C, pH 6.2, 20% air saturation, constant CO2 | population doubling time 23.2 +/- 6.7 h at 0-37 mm Hg; 32.4 +/- 7.2 h at 73; 38.1 +/- 13.3 h at 147; 42.9 +/- 5.4 h at 183; 69.3 +/- 35.9 h at 220 mm Hg; viability above 90% throughout | 0-49; 97; 196; 244; 293 | [41] Vajrala and Murhammer 2016, Biotechnol Prog 32:465-469 | AB (via snippet of abstract) |
| Same, as relative growth rate [my arithmetic: 23.2 / doubling time] | 100%; 72%; 61%; 54%; 33% | at 0-49; 97; 196; 244; 293 mbar | derived from [41] | - |
| Sf-9 and High Five, unpurged bioreactor | CO2 "accumulated to a concentration of about 24 mM"; headspace purging cut doubling time "from 38 to 22 h" | not converted (unclear whether 24 mM is dissolved CO2 or total carbonate) | [42] Mitchell-Logean and Murhammer 1997 | SN |
| Culture pH | 6.2 was the controlled pH in [41]. Typical insect media pH of about 6.0-6.4 is my background knowledge; **not verified** in this lookup | | | |
| High Five and S2 growth versus pCO2 | **not found** beyond [42] | | | |

Sf-9 confidence intervals are wide (n = 3 or 4), so the curve is approximate. Note that at pH 6.2 very little bicarbonate forms, so high pCO2 adds much less osmolality than at pH 7.2.

### 3d. Crustacean (shrimp) cell culture

| Item | Finding as stated | Source | Access |
|---|---|---|---|
| Continuous cell line | none: "development of continuous shrimp cell lines ... remains elusive with an arduous history of over 25 years"; "no continuous shrimp cell lines have yet been established" | [43] Jayesh et al. 2012; [44] | SN |
| Basal medium | L-15 in 32 of 50 publications (64%); earlier review 11 of 19; 2x L-15 + 20% fetal bovine serum + 10% Chen's salt; Grace's insect medium + serum also reported best for *P. stylirostris* and *P. vannamei* | [43] [45] [46] [47] | SN |
| Osmolality | "approximately 730 +/- 10 mmol/kg" in L-15 (*P. monodon*); 700-750 mmol/kg with Grace's | [12] [47] | SN |
| pH and temperature | hemocytes: "osmolality of 730 +/- 20, pH of 7.2 and temperature of 28 C"; *P. monodon* optimum 25-28 C; a 2022 hemocyte study tested pH 7.5 and 8.0 (outcome not retrieved) | [48] [12] [49] | SN |
| Atmosphere | "incubation in a normal atmosphere" (no added CO2) | [12] | SN |
| Proliferation and passage | lymphoid-organ monolayers "passaged twice, after which cell density became too low to subculture because of the absence of active proliferation"; a 1995 study could not passage beyond primary; immortalisation attempts failed | [44] [50] | SN |
| Survival time of primary cultures (days or months) | **not found** | | |
| Growth versus CO2 or pH | **not found**, and not obtainable in principle while cells do not proliferate | | |

### 3e. Shrimp price and count (requested addition)

| Item | Value as stated | Per kg [my arithmetic, 1 lb = 0.4536 kg] | Source | Access |
|---|---|---|---|---|
| Count grades | 16/20, 21/25, 31/40 mean that many shrimp per pound; "U/20" means under 20 per pound | 16/20 -> 35-44 per kg; 21/25 -> 46-55; 26/30 -> 57-66; 31/40 -> 68-88 | [51] | SN |
| US wholesale, headless shell-on, 21-25 count | $3.60/lb | $7.94/kg | [52] S&P Global assessment (date not shown in snippet; the URL slug suggests 5 Oct 2026, my reading) | SN |
| US wholesale, headless shell-on, 26-30 count | $3.49/lb | $7.69/kg | [52] | SN |
| US wholesale, peeled deveined tail-off, 31-40 count | $3.70/lb | $8.16/kg | [52] | SN |
| US retail, 31/40 peeled (one supermarket listing) | $7.98/lb | $17.59/kg | [53] | SN (low quality) |
| US retail, wild Gulf shrimp | "about $14 to $28 per pound" | $30.9-61.7/kg | [53] | SN (low quality) |
| Gulf dockside and import wholesale trend | wholesale 16-20 count farmed shrimp at multi-year lows mid-2022 to early 2025; values only as an index | - | [54] Posadas, Mississippi State Extension, Dec 2025 | FT (no $ figures in text) |

Counts refer to the product form sold (headless or peeled), not whole live animals; a count of whole live animals per kg would be lower (heads and shell add weight) and was not sourced.

---

## 4. CO2 solubility and bicarbonate equilibrium versus temperature

Sources: Henry's constant for CO2 in water at 298.15 K is "3.4x10^-2" mol/(L atm) with temperature coefficient d ln H / d(1/T) = 2400 K ([55], FT; the article warns the formula holds over about 20 K, so the 15 C and 37 C values are at the edge of its validity). First dissociation constant: Harned and Davis 1943, log10 K1 = -3404.71/T + 14.8435 - 0.032786 T ([56], SN; equation as quoted by a later report).

All values in the table are **[my arithmetic]** from those two formulas: H(T) = 0.034 x exp[2400 x (1/T - 1/298.15)].

| T | Henry's constant, mol/(L atm) | mg/L CO2 per mbar (x 44,010 / 1013.25) | Dissolved CO2 at 100 mbar, mM (0.0987 atm x H) | pK1 (pure water, zero ionic strength) |
|---|---|---|---|---|
| 15 C | 0.034 x e^0.279 = 0.0450 | 1.95 | 4.44 | 6.42 |
| 20 C | 0.034 x e^0.137 = 0.0390 | 1.69 | 3.85 | 6.38 |
| 25 C | 0.0340 | 1.48 | 3.36 | 6.35 |
| 28 C | 0.034 x e^-0.080 = 0.0314 | 1.36 | 3.10 | 6.34 |
| 37 C | 0.034 x e^-0.311 = 0.0249 | 1.08 | 2.46 | 6.30 |

Consequences **[my inference]**:
- At the same partial pressure, a 15 C culture holds 4.44 / 2.46 = 1.8 times as much dissolved CO2 as a 37 C culture (1.26 times at 28 C). If toxicity follows dissolved concentration or intracellular acid load rather than partial pressure, a fixed-mbar limit is more severe for cold cultures.
- pK1 rises by about 0.12 between 37 C and 15 C, so at fixed pH and pCO2 the bicarbonate formed changes by 1.8 x 10^-0.12 = about 1.4 times more at 15 C; the osmolality and base-addition penalty of high pCO2 is correspondingly larger.
- In physiological media the apparent pK1 is about 0.2 lower than these values (ionic strength); that offset is background knowledge, not sourced here.
- Stripping is unaffected in kind but the liquid holds more CO2 per mbar of driving force at low temperature.

---

## 5. Mammalian bioprocess comparison

| Item | Value as stated | mbar [my arithmetic] | Source | Access |
|---|---|---|---|---|
| CHO perfusion, productivity optimum | pCO2 "in the range of 30-76 mm Hg" | 40-101 | [57] Gray et al. 1996, Cytotechnology | SN |
| CHO growth inhibition onset | reported as "> 150 mm Hg" in one rendering of the abstract and "> 105 mm Hg" in another; **not resolved** (publisher page not accessible) | 200 or 140 | [57] | SN, conflicting |
| CHO, osmolality controlled at about 350 mOsm/kg | raising pCO2 from 50 to 150 mmHg gave "a 9% reduction in specific cell growth rate" | 67 -> 200 | [58] Zhu et al. 2005, Biotechnol Prog | SN |
| CHO, combined stress | pCO2 140-160 mmHg with 400-450 mOsm/kg caused "a 20% drop in viable cell density" | 187-213 | [58] | SN |
| Industrial reactors | pCO2 "may reach 150-200 mm Hg" | 200-267 | [59] deZengotita et al. 1998 | FT |
| Hybridoma | growth down 45% at 195 mm Hg with partial osmolality compensation (361 mOsm/kg), 63% without (415 mOsm/kg); glucose use and lactate output 40-50% lower at 140 mm Hg | 260; 187 | [59] | FT |
| Manufacturing-scale data | CO2 "at or above 111 mmHg" reduced product quality (112 runs) | 148 | origin not pinned to a single paper in the search results | SN |

The model's 100 mbar sits at the top of the Gray et al. optimum window (101 mbar) and below every reported onset of CHO growth inhibition (140-200 mbar).

---

## What a model could defensibly assume

Tolerance means the dissolved-CO2 partial pressure at which growth is not materially slowed.

| Cell type | Low | Central | High | pH range | Basis |
|---|---|---|---|---|---|
| **Fish** | 10 mbar: **inferred from whole-animal data** (chronic salmonid limits 5-10 mbar; in-vivo arterial 2-4 mbar) | 50 mbar: **inferred from culture practice** (salmonid lines grow well in 26 mM bicarbonate medium, which implies about 40-50 mbar; my calculation in 3a) | 100 mbar: **unknown** (the mammalian default; no fish-cell measurement supports or refutes it) | 7.0-7.6 handled range (**measured/practice**, supplier documents); RTG-2 reported inhibited above 7.4; in-vivo blood 7.8-7.95 | No growth-versus-pCO2 measurement exists that I could find. One cell study shows trout cells do not recover intracellular pH under sustained high CO2 (level unknown). |
| **Insect (Sf-9)** | 50 mbar: **measured** (no slowdown at 0-37 mmHg) | 100 mbar: **measured** (growth rate about 72% of maximum at 73 mmHg = 97 mbar) | 200 mbar: **measured** (about 61% at 147 mmHg = 196 mbar; 33% at 293 mbar; viability stays above 90%) | 6.2 (**measured** condition of the CO2 study); 6.0-6.4 typical is unverified background | Single lab, wide confidence intervals, one cell line. High Five and S2 not separately measured. |
| **Shrimp / crustacean** | 5 mbar: **inferred from whole-animal data** (Boyd safe level 6 mg/L = about 4-5 mbar; crab hemolymph 3.9 mbar) | 25 mbar: **inferred from whole-animal data**, weak (36 mg/L = 26 mbar in RAS caused 42% mortality and tissue damage in whole shrimp, so this is an effect level, not a safe level) | **unknown**: no basis for any figure | 7.2 used for hemocytes (**measured/practice**, one study); shrimp hemolymph pH not found; crab hemolymph 7.85 | No proliferating shrimp cell culture exists, so cell-level tolerance is unmeasured and currently unmeasurable. Media run at about 700-750 mOsm/kg, 25-28 C, normal air, no added CO2. |

Caveats for the modeller **[my inference]**:
1. For fish, the honest position is that the limit is unknown between about 10 and 100 mbar. Whole-animal limits are driven by organ-level mechanisms and probably understate what isolated cells tolerate; the practice-based 50 mbar is the best-supported single number, and it is half the current default.
2. Because solubility rises at low temperature (section 4), expressing the limit as a dissolved concentration rather than a partial pressure would change the cold-water result: the mammalian 100 mbar at 37 C equals 2.46 mM, which is only 55 mbar at 15 C and 79 mbar at 28 C (2.46 / 4.44 x 100; 2.46 / 3.10 x 100). Which quantity matters biologically is not established by anything found here.
3. For insect cells the measured curve is gradual with no cliff, so a 100 mbar limit costs roughly a quarter of growth rate rather than nothing.
4. For shrimp, the dominant uncertainty is not CO2 but whether the cells divide at all.

Suggested probabilities **[my judgement, low confidence]**: that fish muscle-lineage cells grow without material slowdown at 100 mbar at their culture temperature, about 35%; at 50 mbar, about 70%; at 10 mbar, above 95%.

---

## What could not be found

- Any growth-versus-pCO2, growth-versus-bicarbonate or systematic growth-versus-pH curve for a fish cell line (RTG-2, CHSE-214, EPC, BF-2, zebrafish lines) or for amphibian or reptile lines.
- The CO2 level used in the RTH 149 hypercapnia study [34].
- Baseline arterial pCO2 and pH for Atlantic salmon, tilapia, seabass and zebrafish; the review sources named in the brief were unreachable or paywalled.
- Hemolymph pCO2 and pH for *L. vannamei* and *P. monodon* (papers [6] [7] measured them; control values not retrievable). Insect hemolymph pCO2.
- Timmons and Ebeling's tabulated CO2 limits; a sourced recommended pH range for shrimp ponds; the primary Fivelstad 2018 and Casillas-Hernandez 2021 papers (used via secondary reports).
- Castellini and Somero (1981) slyke values for mammalian muscle, so the fish-versus-mammal buffering comparison is qualitative only.
- Survival duration of shrimp primary cultures; a dated, citable wholesale shrimp price series (the S&P figures are from an undated snippet).
- The definitive Gray et al. (1996) inhibition threshold (105 or 150 mmHg).
- Sf-9, High Five and S2 pH optima from a primary source.

---

## Sources

1. Rainbow trout hypercapnia and temperature studies (Wood laboratory archive; Journal of Experimental Biology), as returned by search: https://www.zoology.ubc.ca/~woodcm/Woodblog/wp-content/uploads/2016/06/Wilkes-et-al-1981.pdf and https://cob.silverchair.com/jeb/article-pdf/57/3/673/3181470/jexbio_57_3_673.pdf (the search summary did not say which of the returned papers carried the 1.7 torr figure). SN.
2. Effects of hypercapnia on blood-gas and acid-base status in the white sturgeon: https://data.zhenzhi.com/details/1/914468764/1/4 . SN.
3. J Comp Physiol B (2010), doi 10.1007/s00360-010-0492-8: https://dx.doi.org/10.1007/s00360-010-0492-8 . SN.
4. Dal Pont G, Po B, Wang J, Wood CM (2022) How the green crab *Carcinus maenas* copes physiologically with a range of salinities. J Comp Physiol B, doi 10.1007/s00360-022-01458-1: https://www.zoology.ubc.ca/~woodcm/Woodblog/wp-content/uploads/2022/09/Dal-Pont-et-al.JCPB_.2022.pdf . FT (pages 1-8 read).
5. Truchot-group study of *Carcinus* hemolymph acid-base versus water alkalinity and PCO2: https://link.springer.com/doi/10.1007/BF00684414 . SN.
6. Chen J-C, Cheng S-Y (1995) J Comp Physiol B 164:530-535 (*P. monodon*, nitrite): https://link.springer.com/article/10.1007/BF00261393 . SN, values not retrieved.
7. Chang et al. (2007) Dopamine modulates the physiological response of the tiger shrimp *Penaeus monodon*, Aquaculture: https://bvbvf1.bib-bvb.de/vufind/PrimoRecord/cdi_proquest_miscellaneous_19736724 . SN, values not retrieved.
8. Insect acid-base review and dragonfly study, J Exp Biol: https://cob.silverchair.com/jeb/article-pdf/154/1/573/2458427/jexbio_154_1_573.pdf ; https://openpolar.no/Record/fthighwire:oai:open-archive.highwire.org:jexbio:222%2F22%2Fjeb210294 . SN.
9. Early insect hemolymph pH surveys, J Gen Physiol: https://rupress.org/jgp/article-pdf/7/5/599/1247091/599.pdf . SN.
10. Merck Veterinary Manual, Blood-Gas Analysis Reference Ranges: https://www.merckvetmanual.com/multimedia/table/blood-gas-analysis-reference-ranges . FT (table).
11. Age-specific whole blood biochemistry and gas reference intervals, Lohmann pullets and hens, Avian Diseases 66(1): https://bioone.org/journals/avian-diseases/volume-66/issue-1/21-00011/Establishment-of-Age-Specific-Whole-Blood-Biochemistry-and-Gas-Reference/10.1637/21-00011.full . SN.
12. A novel medium for the development of in vitro cell culture system from *Penaeus monodon*: https://ouci.dntb.gov.ua/works/4MLGjBN7 . SN.
13. Hemolymph osmolality and cation concentrations in *Litopenaeus vannamei*: https://scholarship.miami.edu/esploro/outputs/journalArticle/Hemolymph-osmolality-and-cation-concentrations-in/991031577502002976 . SN.
14. *L. vannamei* low-salinity osmoregulation study (record as returned): https://investigadores.anid.cl/es/public_search/work?id=481831 . SN (attribution of the 800 to 700 mOsm figure to this record is uncertain).
15. Fivelstad et al. (1998), Atlantic salmon post-smolts and CO2, Nofima record: https://nofima.no/publikasjon/622033/ . SN.
16. Mota VC et al. (2019) The effects of carbon dioxide on growth performance, welfare and health of Atlantic salmon post-smolt in recirculating aquaculture systems. Aquaculture 498: https://core.ac.uk/download/288307427.pdf ; summary at https://news-oceanacidification-icc.org/2018/09/06/the-effects-of-carbon-dioxide-on-growth-performance-welfare-and-health-of-atlantic-salmon-post-smolt-salmo-salar-in-recirculating-aquaculture-systems/ . SN.
17. Good/Summerfelt group, Atlantic salmon at 20 mg/L CO2 in freshwater RAS, FAO AGRIS record: https://agris.fao.org/search/en/records/65de763e4c5aef494fdc64a2 . SN.
18. Aarhus University-hosted Aquaculture (2024) paper citing welfare standards: https://pure.au.dk/ws/files/451434507/1-s2.0-S004484862400499X-main.pdf . SN.
19. Boyd CE, Toxicity of chemical substances in aquaculture, Global Seafood Alliance Advocate: https://www.globalseafood.org/advocate/toxicity-chemical-substances-aquaculture/ . SN.
20. Boyd CE, Atmospheric carbon dioxide and freshwater aquaculture, Global Seafood Alliance Advocate: https://www.globalseafood.org/advocate/atmospheric-carbon-dioxide-freshwater-aquaculture/ . SN.
21. Kubitza F (12 May 2025) The impact of water quality on health and performance of farmed fish and shrimp, Part 1: dissolved oxygen and carbon dioxide. Global Seafood Alliance Advocate: https://www.globalseafood.org/advocate/the-impact-of-water-quality-on-health-and-performance-of-farmed-fish-and-shrimp-part-1-dissolved-oxygen-and-carbon-dioxide/ . FT. Cites Hamad et al. 2023 (doi 10.1016/j.aquaculture.2023.739239) and Casillas-Hernandez et al. 2021 (doi 10.1111/are.15198), neither read directly.
22. Acid-base disturbances and effects on oxygen uptake rates in Nile tilapia, DTU: https://orbit.dtu.dk/en/publications/acid-base-disturbances-and-effects-on-oxygen-uptake-rates-in-nile/ . SN.
23. Global Seafood Alliance tilapia article: https://www.globalseafood.org/?p=68570 . SN.
24. Tilapia and carbon dioxide extension note: https://pic.hallikainen.org/techref/other/pond/tilapia/carbondioxide.htm . SN.
25. Hypercapnic hypoxia and immune response in shrimp (Burnett laboratory): https://sicb.org/?p=36196 . SN.
26. The effects of high seawater PCO2 on protein oxidative damage and ubiquitination in *Penaeus vannamei*: https://news-oceanacidification-icc.org/2025/10/13/the-effects-of-high-seawater-pco2-on-protein-oxidative-damage-and-ubiquitination-in-penaeus-vannamei . SN.
27. *L. vannamei* exposed to acidified seawater: https://news-oceanacidification-icc.org/2020/08/13/growth-biochemical-antioxidants-metabolic-enzymes-and-hemocytes-population-of-the-shrimp-litopenaeus-vannamei-exposed-to-acidified-seawater/ ; https://frontiersin.org/articles/10.3389/fmars.2021.748837/pdf . SN.
28. DSMZ, RTG-2 data sheet: https://webshop.dsmz.de/en/human-animal-cell-lines/RTG-2.html . SN.
29. ATCC CCL-55 (RTG-2): https://www.atcc.org/products/ccl-55 . SN.
30. Fernandez RD, Yoshimizu M, et al. (1993) Fish Pathology 28(1):27: https://www.jstage.jst.go.jp/article/jsfp1966/28/1/28_1_27/_article . SN.
31. Hokkaido University repository, fish cell line growth conditions: https://eprints.lib.hokudai.ac.jp/repo/huscap/all/38339/yoshimizu-114.pdf . SN.
32. CMFRI (2024) manual on fish cell culture: https://eprints.cmfri.org.in/18728/1/MFIS_260_2024_Sobhana%20K%20S.pdf . SN.
33. AFS Fish Health Section Blue Book, Cell Culture section: https://oldunitsstaging.fisheries.org/fhs/wp-content/uploads/sites/30/2017/08/S2-4.3-Cell-Culture-2007_2014.pdf . SN.
34. Effect of hypercapnia on intracellular pH regulation in a rainbow trout hepatoma cell line, RTH 149. J Comp Physiol B 181(7):883-892 (2011): https://pesquisa.bvsalud.org/sms/resource/pt/mdl-21538070 . SN (page itself returned 403).
35. Energy budget of hepatocytes from Antarctic fish, J Exp Biol 206:3895: https://cob.silverchair.com/jeb/article/206/22/3895/14087/Energy-budget-of-hepatocytes-from-Antarctic-fish . SN.
36. Differential impacts of elevated CO2 and acidosis on the energy budget of gill and liver cells from Atlantic cod: https://news-oceanacidification-icc.org/2015/06/01/differential-impacts-of-elevated-co2-and-acidosis-on-the-energy-budget-of-gill-and-liver-cells-from-atlantic-cod-gadus-morhua/ . SN.
37. Milligan CL, Wood CM (1986) J Exp Biol 123:123-144: https://www.zoology.ubc.ca/~woodcm/Woodblog/wp-content/uploads/2016/07/Milligan-Wood-1986-123-144.pdf . SN.
38. Fish white muscle buffering and pHi studies (yellow perch seasonal buffering; trout pHi 7.31): https://link.springer.com/article/10.1007/BF02183989 ; https://core.ac.uk/download/14982845.pdf . SN (which record carries which figure not confirmed).
39. Temperature-dependent shift of pHi in fish white muscle (*Zoarces viviparus*): https://acnpsearch.tweb-dev.unibo.it/singlejournalindex/3361645 . SN.
40. Reduced non-bicarbonate skeletal muscle buffering..., J Exp Biol 221:jeb172478, citing Castellini MA, Somero GN (1981) J Comp Physiol 143:191-198: https://cob.silverchair.com/jeb/article/221/10/jeb172478/220/Reduced-non-bicarbonate-skeletal-muscle-buffering . SN.
41. Vajrala SG, Murhammer DW (2016) Effect of CO2 on uninfected Sf-9 cell growth and metabolism. Biotechnol Prog 32(2):465-469, doi 10.1002/btpr.2229: https://iro.uiowa.edu/esploro/outputs/journalArticle/Effect-of-CO2-on-uninfected-Sf-9/9984003913002771 . AB via snippet.
42. Mitchell-Logean C, Murhammer DW (1997) Bioreactor headspace purging reduces dissolved carbon dioxide accumulation in insect cell cultures and enhances cell growth. Biotechnol Prog, doi 10.1021/bp970078s: https://iro.uiowa.edu/esploro/outputs/journalArticle/Bioreactor-Headspace-Purging-Reduces-Dissolved-Carbon/9984003912002771 . SN.
43. Jayesh P, Seena J, Singh ISB (2012) Establishment of shrimp cell lines: perception and orientation. Indian J Virol 23:244-251: https://dyuthi.cusat.ac.in/xmlui/handle/purl/4056 . SN (PDF host refused connection).
44. Improved primary cell culture and subculture of lymphoid organs of the greasyback shrimp (2013): https://mdanderson.elsevierpure.com/en/publications/improved-primary-cell-culture-and-subculture-of-lymphoid-organs-o . SN.
45. The media used in primary cell cultures of prawn tissues: a review (2001): https://researchportalplus.anu.edu.au/en/publications/the-media-used-in-primary-cell-cultures-of-prawn-tissues-a-review/ . SN.
46. Ghent University shrimp lymphoid cell culture work (2014): https://www.vliz.be/imisdocs/publications/278933.pdf . SN.
47. Luedeman R, Lightner DV, Development of an in vitro primary cell culture system from the penaeid shrimp: https://experts.arizona.edu/en/publications/development-of-an-in-vitro-primary-cell-culture-system-from-the-p/ . SN.
48. Shrimp hemocyte culture study reporting 730 +/- 20, pH 7.2, 28 C: https://peeref.com/works/7092941 . SN (attribution to this record not confirmed).
49. *P. vannamei* hemocyte medium optimisation (2022), Mol Biol Rep, doi 10.1007/s11033-022-07834-y: https://springerlink.bibliotecabuap.elogim.com/content/pdf/10.1007/s11033-022-07834-y.pdf . SN.
50. Lymphoid organ primary culture (1995), Exp Biol Med: https://www.ebm-journal.org/journals/experimental-biology-and-medicine/articles/10.3181/00379727-209-43880/full . SN.
51. Shrimp count and size guides: https://americanshrimp.com/shrimp-counts-and-sizes ; https://northcoastseafoods.com/blogs/know-seafood/shrimp-sizing-guide . SN.
52. S&P Global Commodity Insights, US shrimp assessments: https://www.spglobal.com/energy/en/news-research/latest-news/agriculture/100526-us-shrimp-assessments-move-after-weeks-of-limited-price-changes . SN.
53. ThePricer, shrimp cost (includes a supermarket listing): https://www.thepricer.org/shrimp-cost/ . SN, low quality.
54. Posadas B (17 Dec 2025) Mississippi MarketMaker Vol. 15 No. 12, Impacts of imported shrimp prices on US shrimp dockside prices: https://extension.msstate.edu/newsletters/mississippi-marketmaker/2025/vol-15-no-12-impacts-imported-shrimp-prices-us-shrimp-dockside-prices . FT.
55. Wikipedia, Henry's law (values from the Sander compilation): https://en.wikipedia.org/wiki/Henry%27s_law . FT. Not a primary source; primary alternatives are Weiss (1974) Marine Chemistry 2:203 (https://frouingroup.ucsd.edu/EEZ_Argentina/1-s2.0-0304420374900152-main.pdf) and the NIST review (https://srd.nist.gov/jpcrdreprint/1.555905.pdf), neither read.
56. Harned HS, Davis R (1943) J Am Chem Soc 65:2030, equation as quoted in Keeling et al., SIO Reference 77-29 (1977): https://scrippsCO2.ucsd.edu/assets/publications/keeling_sio_ref_series_thermodynamic_ionization_ref_no_77-29_1977.pdf . SN; I recomputed pK1 from the quoted equation.
57. Gray DR, Chen S, Howarth W, Inlow D, Maiorella BL (1996) CO2 in large-scale and high-density CHO cell perfusion culture. Cytotechnology 22:65-78 (author list and pages from my memory, not confirmed), doi 10.1007/BF00353925: https://www.doi.org/10.1007/BF00353925 . SN (publisher page required login).
58. Zhu MM et al. (2005) Effects of elevated pCO2 and osmolality on growth of CHO cells and production of antibody-fusion protein B1. Biotechnol Prog, doi 10.1021/bp049815s: https://zendy.io/title/10.1021/bp049815s . SN (authors and title given from my memory of the DOI, not confirmed in the search result).
59. deZengotita VM, Kimura R, Miller WM (1998) Effects of CO2 and osmolality on hybridoma cells: growth, metabolism and monoclonal antibody production. Cytotechnology 28:213-227: https://pmc.ncbi.nlm.nih.gov/articles/PMC3449846 . FT.
