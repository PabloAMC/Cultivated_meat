# Research task A: membrane retention devices and the thick-culture question

Scope: ATF, TFF, TFDF, spin filters, rotating/vibrating membranes for a 20 m3 tank (16 m3 liquid) in perfusion for about 33 days, with the bleed as the harvest. The repo notes already cover settlers, acoustic, centrifuges, Pasitka's capex lines and the Clincke densities and CSPR (`operating_modes.md` s.4, `perfusion_rate_osmolality.md` rows 1-11, `co2_sparging_settling.md` s.5). This note does not repeat them except where a new number is attached.

Labels: **MEAS** = measured in the cited work; **VEND** = vendor claim; **REV** = review or secondary claim; **INF** = my inference or arithmetic. Access: **full** = whole text extracted and searched (pdftotext or fetch); **part** = sections read; **abstract**; **snippet** = search-engine snippet only, not read.

## 0. Converting the model's duties into membrane terms

The membrane sees only the **permeate**. The bleed (whole culture, the harvest) goes round it. Permeate duties: reference 0.16 m3/h (160 L/h); central 1.88 m3/h (1,880 L/h, 2.8 tank-volumes of liquid per day); best 0.86 m3/h (860 L/h).

Cell count (INF): a 17 um sphere is 2.57 pL. φ = 0.25 is therefore 0.25 / 2.57e-12 mL = **0.97e8 cells/mL**, and φ = 0.12 is 0.47e8 cells/mL. The model's 258 g/L is about 1e8 cells/mL. The literature's "2e8 cells/mL" means φ ≈ 0.5, which Clincke also estimated (see s.3). Humbird's 195 g/L = 65e6 cells/mL works out to 3 ng per cell (Humbird, PMC8362201, *part*).

## 1. Devices

### 1a. ATF (Repligen XCell; formerly Refine Technology)

| Item | Value | Label | Source, access |
|---|---|---|---|
| Sizes: culture volume / displacement / filter area | ATF 1: 0.5-2 L / 0.017 L / 0.022 m2; ATF 2: 2-10 L / 0.1 L / 0.13 m2; ATF 4: 10-50 L / 0.4 L / 0.77 m2; ATF 6: 50-200 L / 1.3 L / 2.5 m2; **ATF 10: 200-5,000 L / 6 L / 11 m2**. ATF 2, 6 and 10 come in single-use and stainless; ATF 10 is the largest. | VEND | Repligen XCell ATF brochure, Nov 2024, https://repligen.com/Products/xcell-atf/BR_XCell_ATF_System_Brochure_11122024.pdf , *full* |
| ATF 10 flow range | 30-80 L/min; 80 L/min is the "recommended maximum for scale-up"; the C410 datasheet gives a ratio of 19 between maximum ATF rate and filtration rate; the C410 datasheet lists 200-1,000 L rather than 5,000 L | VEND | Repligen size guide and controller datasheets, https://www.repligen.com/technologies/xcell-atf/XCell-ATF-Devices-and-Controllers , *snippet* |
| Recommended design flux | "12 mL/min/fiber and 4-6 LMH" | VEND | same, *snippet* |
| Per-unit perfusion capacity | "up to 1000 L/d" per ATF 10 | REV (Humbird citing Pollock 2013) | Humbird 2021, https://pmc.ncbi.nlm.nih.gov/articles/PMC8362201/ , *part*. INF: 1,000 L/d / 11 m2 = 3.8 LMH, consistent with 4-6 LMH |
| "Traditional" perfusion flux | about 2 LMH | REV | 2018 CFD study of ATF, https://rcastoragev2.blob.core.windows.net/8bf3cf23c9fee123d75d5b5164474ff7/PMC6221016.pdf , *snippet* |
| Best long-run demonstration (closest to the reference case) | 50 L (DynaDrive), **one ATF 6 single-use (2.5 m2) for 50 days, no filter change**; VCV 134 ± 9 and 125 ± 11 mm3/mL (φ ≈ 0.13) from day 10 to 50; viability > 90%; CSPR 7.5-8.0 uL/mm3/d (≈ 1.0 VVD); bleed 0.19 d^-1; ATF rate 17 L/min; shear 2,005 s^-1; IgG retention by the membrane rose to 30-40% | MEAS | Ott et al. 2024, Processes 12:806, https://digitalcollection.zhaw.ch/bitstream/11475/30490/3/2024_Ott-etal_Scaling-antibody-production-bioreactors_MDPI.pdf , *full* |
| Flux in that run | permeate ≈ (1.0 − 0.19) × 50 L/d = 40 L/d = 1.7 L/h over 2.5 m2 = **0.68 LMH** | INF from MEAS | as above |
| Highest density with ATF | 1.32e8 cells/mL (ATF 2, 4 L wave bag, 0.085 m2 hollow fibre), up to 6 RV/d. **Limit: "vacuum capacity failing to pull the highly viscous fluid"**; it needed about −0.53 bar; interruptions at 1.32e8 and 1.23e8; runs of 9.7-12.8 d at high density | MEAS | Clincke 2013 Part I, https://pmc.ncbi.nlm.nih.gov/articles/PMC3752962/ , *full (fetch)* |
| Fluxes in Clincke | ATF peak 6 RV/d × 4 L = 24 L/d / 0.085 m2 = 11.8 LMH; average 3.1 RV/d = 6.1 LMH | INF from MEAS | as above |
| 1e8 at pilot scale | BMS N-1 perfusion: 195 L working volume, **one single-use ATF 6**, final VCD 103 ± 4.6e6 cells/mL (target 90-120e6); a short seed stage (days), not a month | MEAS | Xu et al. 2020, mAbs 12:1770669, https://rcastoragev2.blob.core.windows.net/b3e2974853c6954722e6d5ee9038f5e8/PMC7531520.pdf , *part* |
| Fouling versus flux (CHO, Novo Nordisk) | Short flux steps up to 69 LMH did not exceed the critical flux (< 3.5 h); **at a sustained 8.3 LMH the TMP rose to 0.9-0.95 bar and membranes lasted 2.9-5.9 days**; cell aggregates rose from 5% to 36-50% over the run; 0.025 m2 modules | MEAS | Veje et al. 2024, J Membr Sci 701:122764, https://vbn.aau.dk/ws/files/763659375/1-s2.0-S0376738824003582-main.pdf , *full (searched)* |
| Mechanistic fouling | Time to fouling depends on cell density, viability, flux and antifoam; cells and antifoam micelles deposit on the membrane | MEAS (PER.C6) | Kelly et al. 2014, Biotechnol Prog 30:1291, https://zendy.io/title/10.1002/btpr.1953 , *abstract* |
| ATF vs TFF shear | ATF had lower maximum shear than TFF driven by a bearingless centrifugal pump; TFF retained up to 50% of the mAb | MEAS | Karst 2016, Biochem Eng J 110:17, https://re.public.polimi.it/handle/11311/1014184 , *snippet* |
| Price, device | Implied by Pasitka $350k per ATF-10 (repo). **New INF**: Humbird lists $38.5M of ATF filters (caller-supplied, before install) for 96 vessels × 2 ATF 10 = 192 units, i.e. **$200k per ATF 10**. Humbird's Table 2 line "Perfusion equipment" is $89M (*part*), so $38.5M is probably the bare equipment and $89M the installed value; the ratio is 2.3 | INF | Humbird, *part* |
| Price, membrane | $16k per ATF membrane, 20 per bioreactor per year (Humbird, *part*). INF: $16k / 11 m2 = $1,450/m2. Retail check: Repligen Spectrum 0.2 um mPES 0.52 m2 module at $547-657, i.e. $1,050-1,260/m2 | REV / snippet | lifesciencestrading.com listing, https://lifesciencestrading.com/collections/new-arrivals/products/repligen-spectrum-hollow-fiber-filter-0-2-um-5200-cm2 , *snippet* |
| Power | Not found (searched the brochure and the datasheet snippets). INF: wall shear 2,000 s^-1 in a 1 mm lumen implies v = γd/8 = 0.25 m/s. Laminar ΔP over 0.6 m at 2.2 mPa s (φ = 0.25) = 32 × 0.0022 × 0.6 × 0.25 / (1e-3)^2 ≈ 0.11 bar. At 80 L/min (1.33e-3 m3/s) the hydraulic power is about 14 W per ATF 10, or 50 W at 30% pump efficiency. Clincke's 0.8-1 bar at 2e8 would make it 10 times that | INF | |

### 1b. TFF (recirculating, peristaltic or levitated centrifugal pump)

| Item | Value | Label | Source, access |
|---|---|---|---|
| Highest density | 2.14e8 viable (2.24e8 total) cells/mL, 4 L wave bag, 0.085 m2 hollow fibre, up to 10 RV/d; **limit: membrane capacity for the high viscosity, plus pCO2 (31 kPa)**; at about 2e8, P1 (inlet pressure) reached 0.8-1 bar; adding a third hollow fibre did not lower P1, so the cause was viscosity, not fouling; two in parallel brought P1 below 0.6 bar | MEAS | Clincke 2013, *full (fetch)* |
| Run and membrane life | TFF#10 ran 47.7 d. **One hollow fibre lasted 30 d** (including about 1 week at about 1e8); another lasted 14 d; one was replaced after 6 days of rising P2 ("probably partial fouling") | MEAS | same |
| Fluxes | peak 10 RV/d × 4 L / 0.085 m2 = 19.6 LMH; average 3.9 RV/d = 7.6 LMH | INF | |
| Implied throughput per m2 | about 30 d × 24 h × 7.6 LMH ≈ 5,500 L/m2 over one hollow fibre's life (best case) | INF | |
| Recirculation | 0.3-1 L/min on 4 L (4.5-15 passes per hour), wall shear 1,000-3,400 s^-1; viability mostly > 90% | MEAS | same |
| Meat cells | Chicken fibroblasts, TFF, up to 130e6 cells/mL, "43% w/v", harvests over 20+ days; scale not obtained | MEAS (claim) | Pasitka 2024 Nature Food 5:693, abstract via https://cris.huji.ac.il/en/publications/empirical-economic-analysis-shows-cost-effective-continuous-manuf-2/ , *abstract*. Repo METHODS.md already notes that 43% w/v is about 6 times the mass of the cells counted |
| Largest TFF perfusion scale | Not found as a published run above lab or pilot scale (searched "Levitronix TFF perfusion 2000 L" and "TFF perfusion 2000 L"). Pasitka's design study assumes 10 TFF units for 10 × 5 m3 (repo) | — | |
| Price | Pasitka $175k per unit (repo). Generic 0.2 um modules cost about $1,000-1,450/m2 (above) | | |

### 1c. TFDF (Repligen KrosFlo, 2-5 um tubular depth filter)

| Item | Value | Label | Source, access |
|---|---|---|---|
| Pore and flux | 2-5 um polypropylene/PET depth wall; up to 1,950 LMH (clarification, not perfusion); a patent recites 800-1,000 LMH | VEND | https://repligen.com/technologies/tfdf ; patent US 2025/0032997, https://patents.justia.com/patent/20250032997 , *snippet* |
| Perfusion density shown | HEK293 at about 9-10e6 cells/mL (lentivirus and AAV); perfusion for days around transfection | VEND | Repligen app note AP0168 and posters, *snippet* |
| > 5e7 cells/mL, CHO, or month-long runs | **Not found** (searched TFDF perfusion with CHO, high density, 100 million) | — | |
| Note | A 2-5 um wall passes debris and some small cells. That suits a harvest stream, but at 1e8 cells/mL in a meat process I would expect loss of cells into the permeate (INF, untested) | INF | |

### 1d. Spin filters

| Item | Value | Label | Source, access |
|---|---|---|---|
| Largest data found | 12 L and 175 L working volume; "very high cell densities (10^7 mL^-1)"; screen fouling depends on mixing and perfusion rate | MEAS | Yabannavar et al. 1994, https://scilit.com/publications/669826d533ac7b842ca76adef01a7f7f , *abstract snippet* |
| Life | Small apertures can clog in about one week | patent | US 5,019,512, *snippet* |
| Vibration | A piezo-vibrated filter lasted 113% longer (CHO) | MEAS | Vallez-Chetreanu 2006 EPFL thesis, *snippet* |
| Scale-up | Filter acceleration is the parameter to conserve; area does not scale with volume (repo) | REV | |
| Verdict (INF) | Not a candidate at 20 m3 and 1e8 cells/mL | | |

### 1e. Rotating-disc and vibrating (VSEP-type) dynamic filtration

| Item | Value | Label | Source, access |
|---|---|---|---|
| Rotating-disc filter, CHO perfusion | About 400 h at about 1e7 cells/mL, viability > 90%, no progressive TMP rise | MEAS | Castilho, Anspach & Deckwer 2002, Biotechnol Prog, https://zendy.io/title/10.1021/bp0255154 , *snippet* |
| CFD design (CHO and BHK) | 2.5 h test with no fouling | MEAS | Castilho & Anspach 2003, https://read.qxmd.com/read/12827693/ , *snippet* |
| Shear in dynamic filters | 1-3e5 s^-1, about 10 times crossflow | REV | Jaffrin review, https://hal.archives-ouvertes.fr/hal-00338917 , *snippet* |
| VSEP on animal cells | **Not found** (searched); data cover yeast and milk only | — | |
| Verdict (INF) | Peak shear is 50-100 times the ATF lumen's 2,000 s^-1. It is unproven above 1e7 cells/mL, and no large perfusion unit was found | | |

## 2. Sizing for the three duties

Design fluxes, with their basis:
- **(A) 5 LMH**: vendor's 4-6 LMH. Unproven for weeks at φ = 0.25: Veje fouled within 3-6 d at 8.3 LMH and a lower density.
- **(B) 2 LMH**: the "traditional" perfusion flux (snippet).
- **(C) 0.68 LMH**: what Ott ran for 50 d at φ = 0.13 with no change (a measured long-run point).

The ATF 10 has 11 m2. Device price: $200k (Humbird/Pollock, bare) to $350k (Pasitka) per ATF 10. Those are equipment prices; multiply by 1.84 for installed. The model's $89k/m3 is installed; bare it is $48k/m3.

**Membrane area = permeate (L/h) / flux:**

| Duty (permeate) | (A) 5 LMH | (B) 2 LMH | (C) 0.68 LMH |
|---|---|---|---|
| Reference (160 L/h) | 32 m2 → 2.9 → **3 ATF 10** | 80 m2 → **8** | 235 m2 → **22** |
| Central (1,880 L/h) | 376 m2 → **35** | 940 m2 → **86** | 2,765 m2 → **252** |
| Best (860 L/h) | 172 m2 → **16** | 430 m2 → **40** | 1,265 m2 → **115** |

**Capital per m3 of tank (20 m3), bare equipment, at $200k-350k per unit** (× 1.84 for installed):

| Duty | (A) | (B) | (C) |
|---|---|---|---|
| Reference | 3 × 200-350k / 20 = **$30-53k/m3** (installed $55-97k) | $80-140k | $220-385k |
| Central | 35 → **$350-613k/m3** (installed $0.64-1.13M) | $0.86-1.5M | $2.5-4.4M |
| Best | 16 → **$160-280k/m3** (installed $0.29-0.52M) | $400-700k | $1.15-2.0M |

The model's $89k/m3 installed is matched only by the reference case at about 5 LMH. For the central duty at $89k/m3 installed, a $200k ATF 10 budget buys 20 × 48.4k / 200k = 4.8 units = 53 m2. That requires 1,880 / 53 = **35 LMH sustained for a month**, 6-7 times the vendor's design flux and 4 times the flux at which Veje's membranes fouled in days (INF).

The cheaper route is plain TFF: generic hollow-fibre modules at about $1,000-1,450/m2 plus pumps. At (A) the central duty needs 376 m2, which is $0.38-0.55M of modules per fill ($19-27k/m3). Pumps and skids could plausibly bring the capex near Pasitka's $35-48k/m3. The cost then moves into consumables (INF).

**Consumables.** Tank output (caller's numbers): reference 55.5 × 8,760 × 0.91 = **442,400 kg/yr**; central 77.8 × 8,760 × 0.82 = **558,900 kg/yr**; best 118 × 8,760 × 0.85 = **878,600 kg/yr**. Operating days: 332, 299 and 310.

Membrane cost per kg = (permeate per kg) × ($/m2) / (litres filtered per m2 over a membrane's life). Permeate per kg: reference 160 / 55.5 = **2.9 L/kg**; central 1,880 / 77.8 = **24.2 L/kg**; best 860 / 118 = **7.3 L/kg**. Throughput per m2 over a life:
- Veje: 8.3 LMH × about 4.5 d × 24 ≈ 900 L/m2.
- Ott: 0.68 × 50 × 24 = 816 L/m2. This is a lower bound, because the membrane was not exhausted.
- Clincke: about 5,500 L/m2 (best hollow fibre).
- (A) with one change per 33-d run: 5 × 33 × 24 = 3,960 L/m2.

At $1,450/m2 the cost per litre of permeate is $1,450 / 5,500 to $1,450 / 900 = **$0.26-1.61 per L**.

| Duty | Membrane $/kg wet cells (900-5,500 L/m2 life) | Check by unit count: (A), 1 change per 33 d, $16k per module |
|---|---|---|
| Reference | 2.9 × 0.26-1.61 = **$0.76-4.6/kg** | 3 × (332/33) × 16k = $483k/yr / 442,400 = **$1.09/kg** |
| Central | 24.2 × 0.26-1.61 = **$6.4-39/kg** | 35 × (299/33) × 16k = $5.07M / 558,900 = **$9.1/kg** |
| Best | 7.3 × 0.26-1.61 = **$1.9-11.7/kg** | 16 × (310/33) × 16k = $2.40M / 878,600 = **$2.7/kg** |

INF: Humbird's assumption (20 changes per bioreactor per year with 2 ATF 10s, i.e. each module lasts about 36 d) matches the 33-d column. Membrane consumables, not device capex, decide the central case: $6-39/kg is comparable to or larger than the whole target cost of meat. The reference case is $1-5/kg. **Reusable (CIP) ceramic or stainless membranes for animal-cell perfusion: not found** (not specifically searched beyond the price search). They are the obvious route to lower $/kg.

**Shear and passes** (INF). Passes per hour = units × 80 L/min × 60 / 16,000 L:
- Reference (3 units): 0.9/h.
- Central (35 units): 10.5/h.
- Best (16 units): 4.8/h.

Demonstrations ran at higher exposure: Ott 17 L/min × 60 / 50 L = 20/h for 50 d with viability > 90%; Clincke ATF 15/h. Lumen shear stays about 2,000 s^-1 because the ATF heights are uniform (VEND). **Shear is therefore not the binding constraint. Flux, fouling and membrane cost are** (INF; the cells are CHO, not meat cells).

## 3. Thick culture

**Viscosity.**
- Measured: CHO suspensions from 0 to 60% by volume (hematocrit-tube φ) are shear-thinning. A yield stress and elastic plateau appear, and elastic cell-cell interactions "become effective at large concentrations (φ ≥ 0.4)". The authors reference the Krieger-type form η/η0 = (1 − φ/φ0)^(−2.5φ0) with φ0 of 0.64-0.74. Iordan, Duperray & Verdier 2007, arXiv:0709.3671, https://arxiv.org/pdf/0709.3671 , *part* (text read; the plotted values could not be extracted).
- Clincke used a Brookfield DV-II+ on concentrated broth and Thomas's equation. They gave no absolute values; they estimated φ = 0.1 at 4e7 and **φ = 0.5 at 2e8 cells/mL**, and recommended ≤ 1.46e8 cells/mL (≥ 2 um between cells) (*full*).
- A 2025 MDPI Processes paper (13:955) fits high-density CHO to a Sisko model, https://www.mdpi.com/2227-9717/13/4/955 , *snippet* (403 on fetch).

**Relative viscosity, my arithmetic** (Thomas: ηr = 1 + 2.5φ + 10.05φ² + 0.00273·e^(16.6φ); Krieger with φ0 = 0.64):

| φ | Thomas | Krieger | Meaning |
|---|---|---|---|
| 0.12 (reference) | 1.45 | 1.39 | negligible for membranes |
| 0.25 (model limit) | 2.27 | 2.21 | doubles lumen ΔP; manageable |
| 0.37 (Clincke's 1.46e8) | about 4.9 | about 4.0 | the onset of the measured elastic regime |
| 0.5 (2e8) | 15.8 | 11.4 | where ATF vacuum failed and TFF inlet reached 1 bar |

**Ultra-high-density results.**
- Clincke 2013: 2.14e8 with TFF and 1.32e8 with ATF (above).
- Zamani et al. 2018, Biotechnol J 13:e1800036: > 200e6 viable cells/mL over a 45-day CHO perfusion; device and scale not confirmed (https://pubmed.ncbi.nlm.nih.gov/29957873/ , *abstract snippet*).
- Matrix-anchored (non-woven) CHO reached 200e6 peak and about 130e6 stable, with no membrane (https://www.sciencedirect.com/science/article/pii/S0168165615300638 , *snippet*).
- Repligen claims "100-130 million" VCD in long-term perfusion and "two weeks to 60+ days" runs (brochure, VEND, *full*).
- Mayrhofer 2020, Wolf 2019, and the Xu/Chen high-density papers: **not read** (out of budget). Cite them only after reading.

**Where membranes stop (INF from MEAS).**
- **ATF:** limited by its diaphragm pump and vacuum at about 1.2-1.3e8 (φ ≈ 0.3) at 4 L. It has held φ ≈ 0.13 for 50 d at 50 L and about 1e8 for days at 195 L.
- **TFF:** a positive-pressure pump pushed to about 2e8 (φ ≈ 0.5) at 4 L for days, with ~1 bar inlet pressure. It is the more density-tolerant of the two.
- **TFDF, spin filter, rotating disc:** shown only at ≤ about 1e7 cells/mL.

Plausible month-long ceilings (judgement):

| Device | Ceiling for a month |
|---|---|
| ATF | φ ≈ 0.15-0.25 |
| TFF | φ ≈ 0.25-0.35 |
| TFDF | φ ≤ 0.1 (unknown) |
| Spin filter | φ ≈ 0.05 |
| Dynamic filtration | φ ≈ 0.05 (unknown) |

The model's φ = 0.25 limit sits at the edge of what membranes have done, and only for days.

## 4. Probabilities (my judgement, CHO evidence transferred to meat cells)

| Statement | P |
|---|---|
| ATF/TFF (parallel ATF 10s or hollow-fibre TFF) holds **120 g/L at 20 m3 for ≥ 30 d at the reference duty**, module swaps allowed mid-run | **75%** |
| Same, with no module change during the run | 45% |
| The reference case is met at ≤ $89k/m3 installed and ≤ $2/kg membranes | 45% |
| A filter-based device holds **258 g/L at 20 m3 for a month at the central duty** (1.88 m3/h permeate), technically, at any cost | **35%** |
| Same, and at ≤ $89k/m3 installed and ≤ $3/kg membranes | **8%** |
| Best duty (258 g/L, 0.86 m3/h), technically | 40% |
| Best duty at ≤ $89k/m3 installed and ≤ $3/kg | 15% |
| TFDF, a spin filter or a dynamic filter holds 258 g/L at 20 m3 for a month | < 7% |

Main uncertainties:
- Membrane life at 2-5 LMH and φ = 0.25, for which no month-long data exist.
- Whether meat cells (aggregating, larger fibroblasts) foul faster than CHO. Veje's aggregates rose to 36-50%.
- The ATF price, with $200k against $350k per unit unresolved, and a used-device listing at $10k (repo).

## 5. Not found (searched)
- Published TFF or ATF perfusion at ≥ 1,000 L held at ≥ 1e8 cells/mL for weeks.
- ATF device and controller list prices.
- Power figures for ATF or TFF pumps.
- TFDF above 1e7 cells/mL.
- VSEP or vibrating membranes on animal cells.
- Spin filters above 175 L.
- Absolute viscosities (mPa s) of CHO suspensions at φ = 0.2-0.4. They exist in Iordan 2007 Fig. 1 but could not be extracted.
