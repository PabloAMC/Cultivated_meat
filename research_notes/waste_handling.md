# Waste handling beyond Humbird's wash-out: ammonia and lactate levers

Compiled 2026-11-14. Web research only; nothing here was measured or re-derived from raw data.

## How to read this note

**Model baseline being improved on** (Humbird 2021 [S1]): perfusion volume per kg wet cells = max(Y_NH3 / C_NH3,max , Y_lac / C_lac,max).

| Cell type | Y_NH3 (mol/kg wet) | Y_lac (mol/kg wet) | NH3 term (5 mM) | Lactate term (50 mM) | Binding |
|---|---|---|---|---|---|
| Enhanced | 0.054 | 0.56 | 0.054/0.005 = 10.8 L/kg | 0.56/0.05 = 11.2 L/kg | both (~11) |
| Wild type | 0.95 | 6.4 | 0.95/0.005 = 190 L/kg | 6.4/0.05 = 128 L/kg | ammonia |

So for ordinary cells ammonia binds first, but lactate is only 1.5x behind: removing ammonia alone cuts 190 to 128 L/kg, no further. Both must be handled to get large gains.

**Access codes** (how each number was obtained):
- `FT` = full text fetched, but read through an automated page summariser. Quotes are as returned by it; spot-check against the paper before publishing.
- `PDF` = PDF downloaded and text-searched directly (highest confidence in the transcription).
- `ABS` = abstract or repository record only.
- `SNIP` = search-result snippet only. Treat as a lead, not a verified figure.

**Conversion constant used throughout**: Humbird's 3000 pg hydrated mass per cell [S1, FT], so 1 kg wet cells = 1/(3.0e-9 g) x 1000 g = 3.33e11 cells. This is Humbird's generic assumption; CHO cells are smaller and primary livestock cells may differ, so every "mol/kg wet" I derive from a per-cell rate carries that uncertainty (my estimate: a factor of ~2).

Per-cell yield from a specific rate: Y = q / mu, with mu = ln2 / doubling time.

---

## 1. Cells that make less waste

### 1a. Ammonia

| Cell type, scale | Intervention | Number as stated | Conversion | Source, access |
|---|---|---|---|---|
| Bovine fibro-adipogenic progenitors (FAPs), Cytodex-1 microcarriers, 100 mL spinner | Control: 17 mM glucose + 2 mM GlutaMAX | "qAmm = 56.3 +/- 17.3 fmol/cell/h with an average DT of 25.7 +/- 1.7 h" | mu = 0.693/25.7 = 0.0270 /h; Y = 56.3/0.0270 = 2087 fmol/cell = 2.09 pmol/cell; x 3.33e11 cells/kg = **0.70 mol/kg wet** (close to Humbird wild type 0.95) | Hubalek 2023 [S2], FT |
| Same cells, orbital shaker | Same control medium | "around 5 fmol/cell/h for all three donors" | DT for this condition not stated. If DT = 38 h (their long-term passaging value): mu = 0.0182 /h; Y = 274 fmol/cell = **0.09 mol/kg wet** (my inference; DT mismatch possible) | [S2], FT |
| Same cells | GlutaMAX replaced by 10 mM alpha-ketoglutarate, pyruvate or glutamate | "in all conditions without GlnX, no or even negative Amm production was observed"; abstract: specific rate "reduced more than 5-fold" | >5-fold on 0.70 gives **< 0.14 mol/kg wet**; "no or negative" gives ~0 | [S2], FT |
| Same cells, growth cost of substitution | DT: GlutaMAX 38.0 +/- 9.1 h; aKG 42.9 +/- 4.4 h; pyruvate 47.6 +/- 6.8 h; glutamate 48.8 +/- 13.9 h; aKG/Pyr 54.2 +/- 8.4 h | Authors: not significantly different | Point estimates are 13 to 43% slower (42.9/38.0 = 1.13; 54.2/38.0 = 1.43); n = 5, so a real penalty of this size cannot be excluded | [S2], FT |
| Same cells, differentiation | Gluc/Gln vs galactose/pyruvate | "4.2 +/- 0.1 mM on day 7" vs "<2 mM" | - | [S2], FT |
| CHO DG44, shake flask and fed-batch | Lactate supplementation and adaptation (35 mM Na-lactate) | "50% reduction in ammonium production" (flasks); specific ammonium production ~50% lower in fed-batch | Absolute values only in figures | Freund & Croughan 2018 [S3], FT |
| BHK-21 | Mole-for-mole glutamate for glutamine | ammonia accumulation "reduced significantly (>60%)" | - | [S4], SNIP (primary paper not identified) |
| Chicken fibroblast-derived line, TFF perfusion (2 L bioreactors per press coverage) | Animal-component-free medium, perfusion | cells "consumed 145 g of glucose to produce 76 g of lactate and 2.4 g of ammonia" | 2.4/17.03 = 0.141 mol NH3; 145/180.16 = 0.805 mol glucose; NH3/glucose = **0.175 mol/mol**. Basis (per kg biomass? per run?) NOT established, so no mol/kg can be derived | Pasitka 2024 [S5], SNIP |
| Humbird "enhanced" target | GS transfection, lactate re-uptake selection, glucose/pH feedback | 0.004 mol NH3 per mol dry cell mass vs 0.070 wild type | Ratio 17.5x, consistent with model's 0.95/0.054 = 17.6x | [S1], FT |

**GS-CHO vs glutamine-fed quantitative ammonia yields: not found** (qualitative only: GS lines grow glutamine-free, sometimes slower; [S4] SNIP).
**GlutaMAX/dipeptide ammonia yield per biomass: not found** beyond the Hubalek control above (which already uses GlutaMAX and still gives 0.70 mol/kg).
**O'Neill 2022 [S6] did not measure ammonia** (FT). Glutamine is the most-used amino acid on an absolute scale; per-cell rates only as a figure (axis up to 10 ng/cell/day).

### 1b. Lactate

| Cell type, scale | Intervention | Number as stated | Conversion | Source, access |
|---|---|---|---|---|
| CHO DG44, shake flask | Osmolality-adapted control | Y_lac/glc = 1.411 +/- 0.284 mol/mol; qLac 0.112 +/- 0.032 umol/1e6 cell-h; mu 0.027 /h | 0.112/0.027 = 4.15 pmol/cell; x 3.33e11 = 1.38 mol/kg wet (CHO is smaller than 3000 pg, so true per-kg value is higher) | [S3], FT |
| CHO DG44, shake flask | Lactate-adapted (LSA) | Y_lac/glc = **0.388 +/- 0.344 mol/mol**; qLac 0.022 +/- 0.018; mu 0.025 /h | 0.022/0.025 = 0.88 pmol/cell = 0.29 mol/kg wet; 1.411/0.388 = 3.6x lower yield | [S3], FT |
| CHO DG44, fed-batch bioreactor | LSA | peak lactate rise "from 94 mM for the OA cells down to only 10 mM for the LA cells"; peak VCD 35e6 vs 22e6 cells/mL | 9.4x | [S3], FT |
| CHO-S, CHO-K1, HEK293; shake flask, ambr15 (15 mL), DASGIP (270 mL) | Knockout of Ldha + Pdk1-4 ("Warburg-null") | max lactate "sub-millimolar" (2 clones), single-mM (1 clone) vs "~13-135 mM" in wild type; growth rate "comparable to WT"; rituximab "up to ~3 g/L" | Lactate yield ~0; >13x to >100x reduction in peak concentration | Hefzi 2024 preprint [S7], FT. Preprint; no peer-reviewed version found |
| CHO, bench and 2,500 L fed-batch | HIPDOG (pH-triggered glucose feed) | "dramatically reduce or eliminate lactate accumulation during the growth phase"; ~doubling of final titre for eight cell lines | No mol/mol value retrieved | Gagnon 2011 [S8], ABS/SNIP |
| Literature (Fleischaker, via [S3]) | Glucose limitation | ~0.1 mM glucose needed to largely eliminate lactate | - | [S3], FT (secondary) |
| CHO | Glucose then galactose | cells consume glucose first, then grow on galactose "simultaneously consuming the endogenous lactate" | No yield retrieved; patents note low or no growth on galactose-only basal medium | Altamirano 2006 [S9], ABS/SNIP |
| Chicken fibroblast line, TFF perfusion | Unmodified | 145 g glucose to 76 g lactate | 76/90.08 = 0.844 mol; /0.805 mol glucose = **1.05 mol/mol** | [S5], SNIP |
| Rat cardiac / C2C12 cell sheets, dish scale | None vs algae co-culture | Lac/Glc 1.40 +/- 0.07 (1 layer), 1.82 +/- 0.04 (5 layers), 1.71 +/- 0.14 (10 layers); with algae 1.36 to 1.41 | Shows oxygen limitation raises yield from 1.4 to 1.8 | Haraguchi 2017 [S10], FT |
| Humbird | Wild type vs enhanced | stated Lac/Glc 1.77 vs target 0.50 mol/mol | The page summariser flagged that Reactions 2 and 3 coefficients give 1.42 and 0.28 instead; **unverified, check the paper** | [S1], FT |

**Lactate yield for bovine/fish cells in mol/mol: not found.** O'Neill [S6] reports lactate only qualitatively in text (rises as glucose falls; chicken muscle precursors use glucose more slowly than chicken fibroblasts or C2C12). Hubalek [S2] gives lactate only in figures.
**Fructose feeding, LDH knockdown (partial) quantitative yields: not retrieved.**

---

## 2. Tolerance

| Cell type | Measurement | Ammonia | Lactate | Source, access |
|---|---|---|---|---|
| Hybridoma, batch | Initial concentration that halves specific growth rate | **4 mM** | **55 mM** (authors suspect part is osmolarity) | Ozturk, Riley, Palsson 1992 [S11], ABS |
| Recombinant CHO, batch, NH4Cl 0-10 mM, Na-lactate 0-60 mM, NaCl 0-60 mM | Growth vs concentration | "High ammonium concentrations did not inhibit cell growth" (up to 10 mM) | after correcting for osmolarity, lactate "inhibit[ed] growth by 25%" (at up to 60 mM) | Lao & Toth 1997 [S12], ABS |
| CHO, manufacturing-scale fed-batch | Thresholds from process data | growth inhibited above **5.1 mM** | viability affected above **58 mM** and **382 mOsm/kg** | Biotechnol. Prog. 2008, attributed to "Li et al." in snippet [S13], SNIP (authorship unverified) |
| CHO DG44 | Adaptation | - | Adapted to 35 +/- 10 mM; net lactate production driven "to zero at approximately 40 mM" | [S3], FT |
| CHO, literature summary | Typical onset | "2 to 10 mM"; often 2-4 mM | 20-40 mM | [S3], FT (secondary) |
| Mammalian cells, literature summary | Range | "2-10 mM NH3" (cites Xie & Zhou 2005); Humbird adopts 5 mM | adopts 50 mM, loosely sourced | [S1], FT |
| **Bovine FAPs** (cultivated-meat relevant), NH4Cl spiking | Onset | proliferation inhibited "above 5 mM", adipogenic differentiation "above 2 mM" | not measured | [S2], FT. Authors caution spiking may not mimic slow accumulation; no IC50 |
| **Chicken fibroblast line**, perfusion | Operating set-points, not measured limits | kept below **3 mM** | kept below **30 mM** | [S5], SNIP |
| C2C12, primary chick, primary tilapia myoblasts; ammonium acetate 10/25/50 mM for 24 h | Myotube diameter, myostatin | C2C12 myotubes smaller at all doses; chick larger than control at 10-25, reduced at 50; tilapia no effect; 100 mM killed C2C12 and chick cells | - | Wieczorkiewicz et al. 2020 [S14], FT. Proliferation NOT measured; 24 h acute differentiation endpoint, pH not reported. Suggests species ranking tilapia > chick > mouse, nothing more |
| Lamb satellite cells | Literature ranges quoted | "1.8-33 mmol/L" inhibitory/toxic for most mammalian cells; spent medium measured at only 1.214 mM | "above 40 mmol/L" | Pakbin 2025 [S15], FT (secondary for thresholds) |
| Porcine muscle stem cells | Proteome-constrained model fitted to low/high initial ammonium cultures | Numbers exist in paper, **not accessed** | Same | Qiu et al., Metab. Eng. 2026 [S16], ABS |
| Outlier | Literature claim in a methods paper | "adversely affecting cell viability at concentrations higher than 0.6 mM" | - | [S17], FT (secondary; inconsistent with everything else here) |

**Not found:** an IC50 for ammonia or lactate on proliferation of bovine, porcine, chicken or fish satellite cells/myoblasts (only the FAP onset above); quantitative pH dependence of ammonia toxicity; adaptation of meat-relevant cells to higher ammonia. The osmolality interaction is evidenced only for CHO/hybridoma [S11-S13].

---

## 3. Removing waste from the medium

| Method | System, scale | Number as stated | Conversion / caveat | Source, access |
|---|---|---|---|---|
| Alkalisation + stripping | Lamb satellite cell spent DMEM (20% FBS), bench | pH 12, 15 min, 1,400 rpm: removal 82.45% (1.214 to 0.213 mmol/L NH4+); design range 38.63 to 98.43% | Spent NH4+ was already 4x below the 5 mM limit. Needs base then re-neutralisation: adds salt/osmolality each cycle (my inference). Glucose significantly reduced at alkaline pH; amino acids and growth factors **not measured**; lactate **not measured** | [S15], FT |
| Zeolite | Same | 5 and 20 g/L, 1-5 days: "decreased significantly", no % | - | [S15], FT |
| Struvite precipitation; TiO2 nanoparticles | Same | No significant removal | - | [S15], FT |
| Zeolite; Prussian blue | Culture medium | max 60%; max 10% | As cited by [S15] from Kameda 2021 [S18]; primary not accessed | [S15], FT (secondary) |
| Clinoptilolite | Spent medium | 35.8% removal | Attributed to Wu & Vaneeckhaute 2022; **primary not located** | [S15], FT (secondary) |
| L-type zeolite / ferrierite / ZSM-5 / cation resin / Prussian blue | Patent, Nikkiso + Tohoku Univ. | >= 0.005 g/mL gives >= 10% ammonia adsorption; <= 0.1 g/mL keeps glucose adsorption <= 20%. States dialysis has needed a conditioning tank ">10x" the culture tank | 5 to 100 g adsorbent per L. Patent text, not performance data | [S18], SNIP |
| Zeolite A-3 packed bed on cell-free permeate | Hybridoma, perfusion | ammonia held at 1-4 mmol/L; 1e7 cells/mL reported with zeolite beads | Capacity per g not retrieved | [S19], SNIP |
| Membrane-immobilised zeolite | CHO under high ammonium | 3x max cell density, +40% tPA productivity | - | KSBB J. [S20], SNIP |
| Zeolite capacity, NOT in culture medium | Natural zeolite in water; clinoptilolite in manure effluent; zeolite in bacterial culture | Langmuir Q0 = 1.59 mmol/g; 15.7 mg NH4+/g; ~6.3 mg/g | 15.7/18.04 = 0.87 mmol/g; 6.3/18.04 = 0.35 mmol/g. In medium, ~140 mM Na+ and ~5 mM K+ compete, so expect the low end or below (my inference) | [S21], SNIP |
| In-situ electrokinetic / electrodialysis | Hybridoma, lab | 50 A/m2 removed cell-produced ammonium; growth +30%, titre +50%; companion: 1.5x density, IgG 170 to 505 mg/L; lactate removal shown cell-free only | 1995, never scaled | Chang, Grodzinsky, Wang 1995 [S22], ABS/SNIP |
| Hydrophobic microporous hollow-fibre (gas membrane) | Hybridoma | Better growth, no gain in specific antibody secretion; no removal number | - | [S22], SNIP |
| Mg-Al / Cu-Al layered double hydroxide/oxide (lactate adsorbent) | hiPSC and myoblast-relevant media, bench | Selective L-lactate removal, "mostly retaining" glucose; dose-dependent cytotoxicity to hiPSC and C2C12 | Capacity (mmol/g) and % **not retrieved** | Podolinnaia, Kameda et al. 2023 [S23], SNIP |
| **Haemodialyser in the medium loop** | CHO, rolled-scaffold bioreactor, 2e9 cells, 72.8e6 cells/mL | Revaclear 300 dialyser, 1.4 m2; medium 46 mL/min vs dialysate (Ham's F-12K basal medium) 96 mL/min countercurrent; "about 20 minutes"; lactate "reduced by 92%"; glucose "recovered from 21% to 100%"; culture kept 10 days "without replacing the media" | Dialysate used = 96 x 20 = 1,920 mL per 46 x 20 = 920 mL medium = **2.1 L basal dialysate per L medium regenerated**. So dialysis swaps complete medium for basal medium; it saves proteins/growth factors, not basal nutrients or water. Ammonia not measured; protein retention not measured | YekrangSafakar et al. 2022 [S24], PDF (author manuscript) |
| Lactic acid rec