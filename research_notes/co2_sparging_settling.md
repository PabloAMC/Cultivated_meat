# CO2 tolerance, CO2 stripping, sparging limits, tank geometry and cell settling

Research notes, compiled 2026-11-14. Web search and reading only.

**How to read this file**

- Access level is given for every number: **full text** (I read the paper body), **abstract** (abstract only), **snippet** (a search-engine summary or a citing paper's description; not checked against the primary source).
- Most primary papers here are paywalled. A large share of the numbers are abstract or snippet level. Treat snippet-level numbers as leads, not as verified values.
- Conversions: 1 mmHg = 1.3332 mbar. 1 W/kg = 1000 W/m3 at a medium density of 1000 kg/m3.
- "Inference" marks my own arithmetic or judgement. It is not from a source.
- Source numbers in square brackets refer to the list at the end.

---

## 1. CO2 tolerance (growth)

| Cell type | System and scale | What was measured | Value as stated | Converted | Source, access |
|---|---|---|---|---|---|
| CHO | Perfusion, high density (scale not in abstract; a 500 L reactor is mentioned in one excerpt) | pCO2 range that maximised productivity | 30-76 mmHg | 40-101 mbar | Gray 1996 [1], snippet of abstract |
| CHO | Same | pCO2 causing growth inhibition and "dramatic reduction in productivity" | ">105 mm Hg" in one database copy of the abstract; ">150 mm Hg" in another | >140 mbar or >200 mbar | Gray 1996 [1], snippet. **The two copies conflict; the primary paper was not read** |
| CHO (antibody-fusion protein B1) | Bench bioreactors, osmolality held at about 350 mOsm/kg | Specific growth rate when pCO2 raised from 50 to 150 mmHg | 9% reduction | 67 to 200 mbar | Zhu 2005 [2], abstract |
| CHO (B1) | Bench bioreactors | Viable cell density at 140-160 mmHg combined with 400-450 mOsm/kg | 20% drop | 187-213 mbar | Zhu 2005 [2], snippet |
| CHO (B1) | Bench bioreactors | Osmolality alone, 400-450 mOsm/kg | No obvious change in viable cell density or titre | | Zhu 2005 [2], snippet |
| CHO (B1) | Bench bioreactors | Osmolality alone, 460-500 mOsm/kg | 5% lower viable cell density, 8% lower viability | | Zhu 2005 [2], snippet |
| CHO (B1) | "Large-scale" culture (volume not in abstract) | Observed levels | pCO2 "as high as 150 mmHg", 440 mOsm/kg | 200 mbar | Zhu 2005 [2], abstract |
| CHO (mAb producer) | 3 L batch and fed-batch | Control 12.5% (94 mmHg) vs elevated 20% (150 mmHg) | Growth and maximum viable cell density lower at 150 mmHg; lactate shift absent; titres 1.4 and 1.1 g/L vs 2.2 and 2.0 g/L. No growth percentages given in the text | 125 vs 200 mbar | Brunner 2018 [3], full text |
| CHO MT2-1-8 (tPA) | Not stated in snippet | Specific growth rate at 195 mmHg with 435 mOsm/kg | 30-40% inhibition | 260 mbar | Kimura and Miller (later paper, via deZengotita 2002 abstract) [4], snippet |
| Hybridoma AB2-143.2 | Well plates, constant pH | Growth rate at 195 mmHg, osmolality partly compensated to 361 mOsm/kg | 45% decrease | 260 mbar | deZengotita 1998 [5], abstract |
| Hybridoma AB2-143.2 | Well plates, constant pH | Growth rate at 195 mmHg, osmolality uncompensated at 415 mOsm/kg | 63% decrease | 260 mbar | deZengotita 1998 [5], abstract |
| Hybridoma AB2-143.2 | Well plates | Death rate at 250 mmHg, at 401 and 469 mOsm/kg | 31-fold and 64-fold increase | 333 mbar | deZengotita 1998 [5], abstract |
| Hybridoma AB2-143.2 | Continuous culture | Viable cell density at 140 mmHg | 25-40% decrease; death rate lower at the new steady state | 187 mbar | deZengotita 1998 [5], abstract |
| Hybridoma AB2-143.2 | Well plates | Glucose use and lactate production at 140 mmHg | 40-50% lower | 187 mbar | deZengotita 1998 [5], abstract |
| Hybridoma | Not stated | Intracellular pH at 140 mmHg | Drop of about 0.2 units | 187 mbar | deZengotita 2002 [4], snippet |
| Hybridoma, CHO | Not stated | 195 mmHg with 435 mOsm/kg | "About 50% growth inhibition"; reversed by added amino acids (osmoprotectants) in hybridoma | 260 mbar | deZengotita 2002 [4], snippet |
| Unspecified | "Industrial cell culture reactors" | Level that may be reached | 150-200 mmHg | 200-267 mbar | deZengotita 1998 [5], abstract |
| CHO (fed-batch) | Pilot plant (1000 L per a citing paper) vs bench | Dissolved CO2 before fixes | 179 ± 9 mmHg at pilot vs 68 ± 13 mmHg at bench | 239 vs 91 mbar | Mostafa and Gu 2003 [6], abstract |
| CHO (fed-batch) | Pilot plant | Target operating window over 14 days | 40-120 mmHg | 53-160 mbar | Mostafa and Gu 2003 [6], abstract |
| CHO (fed-batch) | Pilot plant | After sparger and impeller changes | 72 ± 9 mmHg; day-10 titre up 1.5-fold | 96 mbar | Mostafa and Gu 2003 [6], abstract |
| CHO, BHK | Review statement | Growth reduced under elevated pCO2 | No threshold given | | Snippet citing Kimura and Miller 1996 and Taticek 1998 |
| Animal cells (general) | Model assumption | Inhibition outside 40-100 mbar; design limit 100 mbar | 100 mbar | 75 mmHg | Humbird 2021 [7], full text, citing Gray 1996 |

**Roles of osmolality and pH**

- At constant pH, raising pCO2 raises bicarbonate and therefore osmolality in proportion (deZengotita 1998 [5], abstract). Many "CO2" effects in older data are partly osmolality effects.
- With osmolality held near 350 mOsm/kg, 150 mmHg cost CHO only 9% of growth rate (Zhu 2005 [2]). With osmolality allowed to rise to 400-450 mOsm/kg the loss was 20% of viable cell density. Elevated pCO2 and osmolality act together (deZengotita 2002 [4], snippet).
- Brunner 2018 [3] suggests that bicarbonate concentration at high pH and high pCO2 may matter more than pCO2 alone: cultures at pH 6.8 and 20% CO2 still switched to lactate consumption.

**Adaptation to high pCO2:** not found. No source describing selection or adaptation of a line to high pCO2.

---

## 2. CO2 stripping

| Topic | System and scale | Value as stated | Source, access |
|---|---|---|---|
| Sparge gas saturation | Four geometrically similar tanks, 15 L to 2500 L total (8 L to 2000 L fill), liquid height:diameter 1:1, sintered frit sparger with 10-20 um pores, DMEM with 10% serum | "The rate was limited by the saturation of the sparge gas by the carbon dioxide dissolved in the medium" | Bowers 2008 [8], full text (conference extended abstract, not peer reviewed) |
| kLa for CO2 from the sparger at 0.005 vvm | 15 L / 200 L / 500 L / 2500 L | 0.46 ± 0.09, 0.65 ± 0.25, 0.28 ± 0.05, 0.42 ± 0.08 per hour | Bowers 2008 [8], full text |
| kLa for O2 from the sparger at 0.005 vvm | Same | 3.4 ± 1.2, 9.3 ± 1.0, 3.0 ± 1.0, 3.7 ± 1.1 per hour | Bowers 2008 [8], full text |
| Ratio kLa(CO2)/kLa(O2) | Same | About 0.1 observed; 0.8-0.9 expected from film theory | Bowers 2008 [8], full text |
| Saturation-limited stripping formula | Same | (kLa,CO2)SAT = (H/RT)(60)(vvm), with H about 40 atm L/mol at 37 C, giving about 94 x vvm per hour (0.47 per hour at 0.005 vvm) | Bowers 2008 [8], full text. I checked the arithmetic: 40/(0.08206 x 310) x 60 = 94.3 |
| Surface (headspace) kLa for CO2, headspace flow 0.05 vvm | 15 L / 200 L / 500 L / 2500 L | 0.15, 0.08, 0.04, 0.03 per hour; proportional to surface area per volume | Bowers 2008 [8], full text |
| Consequence | Same | With pure O2 microsparging at 10% dissolved CO2, "the amount of carbon dioxide stripped will be less than half of the carbon dioxide produced by respiration" | Bowers 2008 [8], full text |
| kLa for CO2 at industrial scale | 15 kL tank, 12.5 kL liquid, 2 m diameter, 37 C | Rose with superficial gas velocity; did not respond to power input (about 5% change); "did not exceed 2.5 per hour" | Nickel 2024 [9], full text |
| kLa at laboratory scale, gas velocity 0.64 mm/s | 3 L | O2: 5.4 to 16.7 per hour and CO2: 4.4 to 9.5 per hour as power went from 10.3 to 82.2 W/m3 | Nickel 2024 [9], full text |
| Side sparger on a baffle at mid height | 15 kL | CO2 kLa up to +25.0%; O2 kLa +9.8% | Nickel 2024 [9], full text |
| Bubble saturation | Review statement | Bubbles quickly saturate with CO2 during the long rise in tall tanks; interfacial area is then of negligible importance | Nickel 2024 [9], full text, citing Sieblist 2011 and Xing 2017 |
| Gas-phase behaviour | Large-scale tanks (volume not in abstract) | Stripping is set mainly by the change in gas composition between sparger and headspace; gas is not in plug flow; model includes gas residence time | Sieblist 2011 [10], abstract only. No numbers obtained |
| CO2 kLa vs interfacial area | From 300 L upward | CO2 kLa, unlike O2 kLa, is not affected by changes in specific interfacial area | Sieblist dissertation 2012 [11], snippet |
| Stripping model without kLa | 5,000 L and 25,000 L CHO cultures | Stripping depends on gas flow, bubble residence time, time for bubbles to saturate, and CO2 concentration; kLa-based models failed to predict measured profiles | Xing 2016 conference paper [12], snippet |
| Sparger type | 1000 L pilot (per citing paper) | Open pipe gave "3- to 4-fold better dCO2 removal for the same kLa" than a sparge stone; less foam | Mostafa and Gu 2003 [6], abstract |
| Gas flow vs agitation | Cell-free tests, same paper | CO2 removal rate "a strong function of sparge rate and a weak function of agitator speed" | Mostafa and Gu 2003 [6], abstract |
| Impeller position | Same | Lowering the top impeller improved CO2 kLa 2-fold | Mostafa and Gu 2003 [6], abstract |
| Headspace sweep | Same | Raising headspace aeration from 0.02 to 0.04 vvm "had no impact" | Mostafa and Gu 2003 [6], abstract |
| Surface aeration vs scale | 80 L, 500 L, 2000 L, 10,000 L | CO2 kLa rose with surface aeration, but the gain shrank with scale as surface:volume fell. No numbers obtained | Matsunaga 2009 [13], abstract |
| Scale-up factor | Stainless tanks (scales not obtained) | Ratio of kLa(O2) to kLa(CO2) proposed as scale-up factor to control dissolved CO2 | Doi 2020 [14], snippet |
| Scale comparison | 5,000 L vs 5 L and 20 L, cell-free | 5,000 L had lower O2 transfer, longer mixing time and lower CO2 removal; configuration supported about 7 x 10^6 cells/mL; pH and oxygen gradients may exist | Xing 2009 [15], abstract. Equations not obtained |
| Minimum sparge rate | 500 L perfusion, 10^7 cells/mL | 0.006 vvm predicted to hold 76 mmHg | Gray 1996 [1], snippet |
| Microsparging trade-off | Review | Small pure-O2 bubbles cut foam and bursting but strip CO2 poorly; larger bubbles strip better; suggests separating O2 supply from CO2 removal | Hu, Berdugo and Chalmers 2011 [16], full text |

**Membrane or silicone-tubing aeration**

| Item | Value as stated | Source, access |
|---|---|---|
| Largest demonstrated scale found | Dynamic membrane aeration (silicone tubing on a rotor) at 12, 20, 100 and 200 L; doubles gas transfer at the same shear | Snippet pointing to PMC2677146 [17]. Paper not read |
| Scaling argument | Installable tubing area grows with the square of tank size, volume with the cube | Same snippet [17] |
| CO2 removal by silicone hollow-fibre modules | Reported only at 2 L and bench perfusion | Patent snippet |
| Transfer rates (kLa, mmol/L/h) for membrane aeration | Not found | |

---

## 3. Sparging and agitation limits

**Sparge rates**

| Item | System and scale | Value as stated | Converted | Source, access |
|---|---|---|---|---|
| Model limit | 20 m3 design | Superficial gas velocity 0.006 m/s = 0.1 vvm | | Humbird 2021 [7], full text, citing Ozturk 1996 (primary not obtained) |
| Industrial operating point | 15 kL tank, 12.5 kL liquid, 2 m diameter (Boehringer Ingelheim co-authors) | 0.64 mm/s submersed superficial gas velocity | 0.0096 vvm (0.64e-3 m/s x 3.14 m2 x 60 / 12.5 m3). Inference from stated geometry | Nickel 2024 [9], full text |
| "Typical operating conditions", microsparger | 15 L to 2500 L | 0.005 vvm sparge; 0.05 vvm headspace | | Bowers 2008 [8], full text |
| Headspace aeration | 1000 L pilot | 0.02-0.04 vvm | | Mostafa and Gu 2003 [6], abstract |
| Damage threshold, hybridoma | Not stated | Negative effect at 0.02 vvm | | Oh 1992, via Hu 2011 [16], full text of review |
| Damage threshold, Sf9 insect cells | Not stated | Detrimental at sparge rates "as low as 0.007 vvm" | | Kioukia 1996, via Hu 2011 [16]. Protectant status not stated in what I read |
| Sparger-hole damage, NS0 | 8 L spinner | First-order cell damage when gas entrance velocity exceeded 30 m/s; raising Pluronic F-68 from 0.5 to 2 g/L gave no extra protection against this | | Zhu 2008, via Hu 2011 [16] and snippet |
| Maximum sparge rate with vs without protectant at 10-25 m3 | | Not found | | |

**Bubble bursting and protectant**

| Item | Value as stated | Source, access |
|---|---|---|
| Energy dissipation rate at bubble rupture | "10^7-10^9 W/m3 when bubbles of 1-2 mm in diameter" rupture; rises as bubbles get smaller | Boulton-Stone and Blake 1993; Garcia-Briones 1994, via Hu 2011 [16], full text of review |
| Same, newer simulations | Earlier predictions 10^4 to 10^10 W/m3; new simulations find maxima "exceeding 10^15 W/m3" (mesh-dependent singularity) | Walls 2017 [18], full text |
| Lethal single-pass dissipation rate, CHO | 10^6 to 10^8 W/m3; similar for HeLa S3 and hybridoma; threshold drops nearly two orders of magnitude with repeated exposure | Walls 2017 [18], full text, citing Chalmers group |
| Liquid volume above 10^7 W/m3, 500 um bubble | 4.6% of surrounding liquid in water; 1.9% when surfactant lowers surface tension from 72 to 40.5 mN/m | Walls 2017 [18], full text |
| Cells killed per bubble, no protectant | About 1,050 per 3.5 mm bubble (insect cells at about 10^6 cells/mL) | Trinh 1994, via Hu 2011 [16] |
| Large bubbles, Sf9 | 1.75 mm radius bubbles gave "death rates exceeding 70%" | Walls 2017 [18], citing its ref. 26 |
| Cells carried into foam with protectant | About 10^3 cells per bubble at 10^7 cells/mL and 1 g/L Pluronic F-68 | Ma, Koelling and Chalmers 2004, via Hu 2011 [16] |
| Protectant mechanism | Pluronic F-68 lengthens cell-bubble attachment time to 5-20 s; attachment matters most for bubbles under 100 um | Michaels 1995; Meier 1999, via Hu 2011 [16] |
| Protectant depletion | CHO take up to 12 ug Pluronic F-68 per 10^6 cells, about 0.12 g/L at 10^7 cells/mL | Gigout 2008, via Hu 2011 [16] |
| Full protection concentration | 0.2% w/v Pluronic F-68 "fully protected" cells | Murhammer and Goochee 1990, snippet |
| Bubble size at fixed gas flow | Smaller bubbles "would be expected to damage a larger number of cells" | Walls 2017 [18], full text |

**Agitation power**

| Item | System and scale | Value as stated | Converted | Source, access |
|---|---|---|---|---|
| Model limit | Design rule | Smallest eddies near one cell, about 20 um; factor 50 between local maximum and mean dissipation | See inference below | Humbird 2021 [7], full text, citing Nienow |
| Typical mean dissipation from agitation | Animal cell reactors | About 0.01-1 W/kg | 10-1000 W/m3 | Snippet of a paper citing Hu 2011 |
| Range studied as industrially relevant | 3 L model of a 15 kL tank | 10.3 to 82.2 W/m3 | | Nickel 2024 [9], full text |
| CHO, fed-batch, bench scale | Dual Rushton | Maximum local dissipation up to about 25x (turbulent) and about 160x (laminar extensional) "typical commercial conditions": no significant effect on growth or viability; product quality unaffected | | Nienow 2013 [19], abstract |
| Same study, mean power | | "up to 250 W/m3" in one description and "up to 1000 W/m3" in another | | Nienow 2013 [19], snippets. **Not verified; the full text returned HTTP 403** |
| CHO, 2 L scale-down | | Cells "highly robust"; at 0.4 W/kg vs 0.01 W/kg, specific antibody productivity fell 25%; oscillating between the two, about 30%; metabolism and product quality unaffected | 400 vs 10 W/m3 | Sieck 2013 [20], snippet of abstract |
| CHO, repeated exposure | Flow device | Glycosylation changed at 6.0 x 10^4 W/m3 | | Godoy-Silva 2009, via Hu 2011 [16] |
| CHO-K1 | Flow device | Growth inhibited at one to two orders of magnitude below single-pass lysis levels | | Godoy-Silva 2009, via Hu 2011 [16] |
| THP1 | | About two orders of magnitude more sensitive than CHO | | Mollet 2008, via Hu 2011 [16] |
| Hybridoma | 2 L baffled, no gas-liquid interface | Viability held at 1,500 rpm | | Zhang and Thomas 1993, via Hu 2011 [16] |
| Local vs mean dissipation | Stirred tanks | Impeller region 22-280x the mean; bulk 0.06-0.65x | | Hu 2011 [16], Table 1 |

Inference (Kolmogorov arithmetic, mine): with kinematic viscosity 0.7e-6 m2/s, a 20 um eddy needs a local dissipation of (0.7e-6)^3 / (20e-6)^4 = 2.1 W/kg. Divided by Humbird's factor of 50 that is a mean of 0.043 W/kg, about 43 W/m3, which matches the 40-100 W/m3 assumption. A mean of 1000 W/m3 would give 9 um eddies near the impeller.

---

## 4. Tank geometry

| Item | Scale | Value as stated | Source, access |
|---|---|---|---|
| General guidance for stirred tanks | Not scale-specific | Height:diameter "within a range of 1:1 to 3:1"; "for animal cell cultivations, often a ratio of 2:1 is recommended" | BioProcess International article [21], snippet (trade press) |
| Industrial tank | 15 kL total, 12.5 kL liquid, 2 m diameter | Liquid height about 4.0 m, so height:diameter about 2.0 (12.5 / 3.14 / 2). Inference from stated volume and diameter, ignoring the dished bottom | Nickel 2024 [9], full text |
| Test tanks | 15 L to 2500 L | Filled to liquid height:diameter 1:1 | Bowers 2008 [8], full text |
| Patent claim | 1,000 L | Maximum aspect ratio about 1.8 to 2.1 | Patent snippet |
| "Many modern culture vessels" | Not stated | About 2.5:1 | Vendor blog, snippet |
| Humbird model | 20 m3 | No aspect ratio stated; two impellers, 80% working volume | Humbird 2021 [7], full text |
| Squat vs tall for gas exchange | General | Low ratio gives more surface per volume; high ratio gives longer bubble residence and better O2 transfer | BioProcess International [21], snippet |
| Tall tanks and CO2 | General | Long bubble rise in tall tanks leads to CO2 accumulation; hydrostatic pressure raises dissolved CO2 | Nickel 2024 [9]; trade snippets |
| Published aspect ratios for named 10-25 m3 cell-culture tanks | | Not found, other than the 12.5 kL case above | |

---

## 5. Cell settling and retention

**Settling velocities and densities**

| Item | Value as stated | Source, access |
|---|---|---|
| Hybridoma AB2-143.2, viable single cells | 2.9 cm/h | Patent US 8,667,832 citing Searles 1994 [22], snippet |
| CHO M1-59, viable single cells | 1.45 cm/h | Same [22], snippet |
| Non-viable vs viable hybridoma | Non-viable cells settled 33-50% slower; up to twofold variation among three hybridoma lines; velocity fell as the culture aged | Cleveland State settling-column study [23], snippet |
| CHO cell density | About 1.06 g/mL | Textbook table, snippet with poor OCR. Low confidence |
| CHO diameter | 10-20 um, average about 14.45 um | Trade article snippet |
| Medium density | Not found | |
| Measured settling velocity of aggregates or spheroids vs size | Not found | |

Inference (Stokes check, mine): diameter 14 um, density difference 0.05 g/mL, viscosity 0.7 mPa s gives 50 x 9.81 x (14e-6)^2 / (18 x 0.0007) = 7.6e-6 m/s = 2.7 cm/h. Consistent with the measured 1.45-2.9 cm/h. Stokes velocity scales with diameter squared, so a 200 um aggregate of the same density would settle about 200 times faster than a 14 um cell, before any correction for porosity. This is not a measurement.

**Inclined settlers**

| Item | Scale | Value as stated | Source, access |
|---|---|---|---|
| Largest perfusion use found | 3,000 L bioreactor (seed stage), CHO | Up to 158 x 10^5 cells/mL at 2,950 L/day; retention efficiency >85% | Pohlscheidt 2013 [24], abstract |
| Large-scale performance claim | Not stated | 99% efficiency at perfusion rates "over 2000 L/day" at 20 x 10^6 cells/mL or more | Vogel 2012, via Coronel 2020 [25], full text of citing paper |
| Run length | | Perfusion "can last up to 3-5 months" | Henzler 2012, via Coronel 2020 [25] |
| Large settler for bleed recycling, CHO | Built for a 2000 L perfusion reactor (1500 L working volume) | 40 channels, plates 30 x 29.7 cm, 0.5 cm gap, horizontal settling area 17,820 cm2, inner volume 30.4 L, clarification rate 4.6 mL/s, residence time 1.46 h at 500 L/day inlet; tested at 470, 600 and 730 L/day; separation efficiency fell to 94% above design capacity | Romann 2023 [26], full text |
| Lab settler, same study | 2 L reactor | 5 channels, 17.0 cm2, clarification 4.8e-3 mL/s, residence time 1.15 h | Romann 2023 [26], full text |
| Effect of residence time | Same | Abstract reports no negative impact on cell viability; lower debris removal than acoustic | Romann 2023 [26], full text (partly read) |
| Small settler, avian AGE1.CR.pIX | 1 L reactor, settler CS10, 0.046 m2, rated up to 8 L/day, dead volume about 275 mL | Up to 50 x 10^6 cells/mL; retention 96-99% in growth phase, falling to 85-94% after infection; recirculation 35 mL/min | Coronel 2020 [25], full text |
| Cooling, same study | | Heat exchanger at 20-27 C. At 20-22 C doubling time exceeded 48 h, so 25-27 C was used. Stated reasons for cooling: slower metabolism and better sedimentation | Coronel 2020 [25], full text |
| Growth penalty, same study | | Doubling time 26-32 h with settler (37 h in one run) vs 25 h with ATF | Coronel 2020 [25], full text |
| First CHO settler study | Lab scale | Three-port settler "maintained at lower temperatures" and vibrated; cells returning in the underflow had average residence time 1.46 h; cells resuspended by air bubbling returned within 32 minutes | Searles 1994 [27], snippet of abstract. Temperature not obtained |
| Settler residence time as a drawback | Review | Long residence in an uncontrolled environment | Voisard 2003 [28], via Coronel 2020 |
| Compact (conical) settlers | 1.2 L CHO demonstration; 150 L unit developed | 5-10x (or 6-10x) more settling area per footprint than lamellar | Kompala / Sudhin conference abstracts and slides [29], snippet. Vendor claims |
| Shen and Yanagimachi 2011; Batt 1990; Freeman 2017; Voisard 2003 capacity table | | Numbers not obtained | |

Inference (overflow velocity, mine): clarified flow divided by horizontal settling area gives 4.6 cm3/s / 17,820 cm2 = 0.93 cm/h (Romann large), 4.8e-3 / 17.0 = 1.0 cm/h (Romann lab), and 8 L/day / 0.046 m2 = 0.72 cm/h (Coronel). Working settlers are therefore designed at about 0.7-1.0 cm/h, which is 50-70% of the measured CHO single-cell velocity. On that basis, 1 reactor volume per day from a 20 m3 tank (20 m3/day) at 1 cm/h (0.24 m/day) needs about 83 m2 of horizontal settling area.

**Other retention devices**

| Device | Value as stated | Source, access |
|---|---|---|
| Acoustic settler | Tested up to 400 L/day on a 100 L reactor at 10^7 CHO cells/mL; best 96% separation at 200 L/day, separator at 35.1 C and 90 W | Gorenflo 2002 [30], snippet of abstract |
| Acoustic settler limit | "Successfully tested up to a clarification volume of 200 L/day"; larger units "very difficult due to the significant power input", causing heat generation | Romann 2023 [26], full text |
| Acoustic settler, vendor range | 1 to 1000 L/day, >95% efficiency | Applikon BioSep brochure, snippet. No independent data at 1000 L/day |
| Alternating tangential flow filter | Xcell ATF 10 up to 1000 L/day | Humbird 2021 [7], citing Pollock 2013 |
| Hydrocyclone | Scale, efficiency and pressure drop not found | |
| Centrifuges, spin filters | High perfusion capacity; acoustic and inclined settlers judged to have good scale-up potential. No numbers obtained | Voisard 2003 [28], snippet of abstract |

**Tolerance to no oxygen or no flow**

| Item | Value as stated | Source, access |
|---|---|---|
| Hybridoma (SP2/0-derived), batch, 37 C, full anoxia | Viable cell density constant for 25 h; viability 30% after 45 h; cells returned to oxygen after 22 h or 29 h showed no further apoptosis | "Induction of apoptosis in oxygen-deprived cultures of hybridoma cells", Cytotechnology [31], snippet of abstract |
| Hybridoma, chemostat | Could grow at 0% dissolved oxygen under nitrogen; critical dissolved oxygen 0.5% of air saturation | Chemostat studies, snippet |
| CHO, cyclic exposure to low oxygen in a recycle loop | No response up to 90 s residence time; beyond that, lactate accumulation and up to 15% lower viable cell density | 2021 scale-down study, snippet. **Paper not identified** |
| CHO in settlers | Residence 1.15-1.46 h with no reported viability loss | Romann 2023 [26]; Searles 1994 [27] |
| CHO at 30 C | Energy charge maintained; overall metabolism reduced; apoptosis delayed | Snippet |
| Tolerance when cooled to 4-20 C, in minutes | Not found | |

Inference (oxygen depletion time, mine): Hu 2011 [16] cites an oxygen uptake of 3.7 mmol/L/h at 2 x 10^7 cells/mL (Huang 2010). With about 0.1 mM dissolved oxygen at 50% air saturation (my assumed value), oxygen is gone in 0.1/3.7 h = 1.6 minutes, and in about 20 s at 10^8 cells/mL. Cells in any settler are therefore anoxic for nearly all of a 1-1.5 h residence, and they survive it. The cost seen in practice is slower growth, not death.

**Aggregates and spheroids**

| Item | Value as stated | Source, access |
|---|---|---|
| Necrotic core, common statement | Spheroids "larger than 400-500 um" show a necrotic core, a quiescent layer and a proliferating rim | Review, snippet (candidate sources [32]) |
| Necrotic core, lower figure | Develops "in spheroids exceeding 200 um in diameter" | Review, snippet [32] |
| Necrotic core, upper figure | Beyond a critical size of about 500 um | Snippet [32] |
| Diffusion-limited viable rim | 150-200 um | Review and modelling paper, snippet [32] |
| Growth in aggregates vs single cells | In-situ rate about 2.5-fold lower than the single-cell rate at 1300 um diameter (tumour spheroids) | Freyer and Sutherland, via modelling paper, snippet [32] |
| Bovine satellite cells without matrix | Spontaneously formed myospheres but showed cell-cycle arrest and inhibited proliferation | McMaster thesis [33], snippet |
| Chicken fibroblasts, single-cell suspension | 108 x 10^6 cells/mL, 36% w/v, continuous culture; follow-up 130 x 10^6 cells/mL, 43% w/v with tangential flow filtration | Pasitka 2023 and follow-up [34], abstract |
| Aggregate diameters, growth rates and necrosis thresholds for muscle, fibroblast or fish cells in stirred suspension | Not found | |

---

## Ranges a model could defensibly use

All three columns are my judgement, built from the tables above. "Basis" says which numbers are sourced and which are inferred.

| Parameter | Low | Central | High | Basis and confidence |
|---|---|---|---|---|
| pCO2 growth limit (mbar) | 100 | 160 | 200 | Low = upper end of Gray's productivity optimum (76 mmHg). Central = Mostafa and Gu's operating ceiling (120 mmHg). High = 150 mmHg, where CHO lost 9% of growth rate with osmolality controlled. About 50% growth loss occurs near 260 mbar (195 mmHg) with raised osmolality, in hybridoma and one CHO line. Medium confidence; CHO and hybridoma only, mostly abstracts. **No data for muscle, fibroblast, fish, HEK, NS0 or BHK** |
| Superficial gas velocity limit (m/s) | 0.0006 | 0.002 (inference) | 0.006 | Low = documented 15 kL industrial operating point (Nickel 2024), which is practice, not a damage limit. High = Humbird's value, attributed to Ozturk 1996, which I could not check. Central is a geometric mean with no direct evidence. Low confidence. The key finding is that documented industrial practice is about 0.005-0.02 vvm, 5 to 20 times below Humbird's 0.1 vvm |
| Tolerated mean power input (W/m3) | 40 | 100-250 | 400-1000 | Low = eddy-size rule (my arithmetic reproduces about 43 W/m3). Central = range in which Nienow 2013 reportedly saw no effect. High = Sieck 2013 at 400 W/m3 (growth robust, productivity down 25%) and an unverified 1000 W/m3 for Nienow 2013. Medium confidence for CHO up to about 250; low above that; nothing for muscle or fibroblast cells |
| Liquid height:diameter | 1.0 | 2.0 | 3.0 | Central from trade guidance and the one 12.5 kL tank I could compute (about 2.0). Medium-low confidence; little published geometry for 10-25 m3 tanks |
| Single-cell settling velocity (cm/h) | 1.0 | 1.5 | 2.9 | Central = CHO 1.45, high = hybridoma 2.9 (both snippet level, from a patent citing Searles 1994). Low = allowance for non-viable or smaller cells (33-50% slower) and matches the 0.7-1.0 cm/h at which real settlers are sized. Medium confidence; Stokes arithmetic agrees |
| Tolerated time without oxygen (minutes) | 1.5 | 60-90 | 1300 | Low = 90 s threshold for a metabolic response to repeated low-oxygen exposure in CHO (unidentified 2021 study). Central = settler residence times of 1.15-1.46 h run without reported viability loss. High = 22 h anoxia survived reversibly by a hybridoma. Low-medium confidence; the three numbers measure different things (metabolic shift, practical operation, survival). Nothing found for cooled cells |
| Aggregate diameter without a necrotic core (um) | 200 | 300-400 | 500 | Low and high are the two figures quoted in spheroid reviews; central = twice the 150-200 um viable rim. Low-medium confidence: tumour-spheroid literature at snippet level, not cultivated-meat cells, and the threshold depends on cell oxygen uptake and bulk oxygen level |

**A structural point for the model (inference):** if sparge gas leaves saturated with CO2, as Bowers 2008, Sieblist 2011, Xing 2016 and Nickel 2024 all indicate for tall tanks or fine bubbles, then CO2 removal equals gas flow times the equilibrium CO2 content of the gas. It no longer depends on kLa or power. Using Bowers's formula, the ceiling is about 94 x vvm per hour: 9.4 per hour at 0.1 vvm, 0.9 per hour at 0.01 vvm. At 100 mbar dissolved CO2 and 0.1 vvm the maximum removal is 6 L gas per L per hour x 0.0987 atm / 25.44 L atm/mol = 23 mmol/L/h, and ten times less at 0.01 vvm. This ignores hydrostatic pressure, water vapour and CO2 in the inlet gas. A kLa-based CO2 model will overstate stripping whenever its predicted kLa exceeds this ceiling.

---

## Sources

1. Gray DR, Chen S, Howarth W, Inlow D, Maiorella BL. CO2 in large-scale and high-density CHO cell perfusion culture. Cytotechnology 1996;22:65-78. https://doi.org/10.1007/BF00353925 . Snippet (abstract copies at https://data.zhenzhi.com/details/1/860906754 and scite.ai disagree on 105 vs 150 mmHg).
2. Zhu MM, Goyal A, Rank DL, Gupta SK, Vanden Boom T, Lee SS. Effects of elevated pCO2 and osmolality on growth of CHO cells and production of antibody-fusion protein B1: a case study. Biotechnol Prog 2005;21:70-77. https://zendy.io/title/10.1021/bp049815s . Abstract.
3. Brunner M, Doppler P, Klein T, Herwig C, Fricke J. Elevated pCO2 affects the lactate metabolic shift in CHO cell culture processes. Eng Life Sci 2018;18:204-214. https://pmc.ncbi.nlm.nih.gov/articles/PMC6999464 . Full text.
4. deZengotita VM, Schmelzer AE, Miller WM. Characterization of hybridoma cell responses to elevated pCO2 and osmolality (https://zendy.io/title/10.1002/bit.10176) and deZengotita et al., Selected amino acids protect hybridoma and CHO cells from elevated carbon dioxide and osmolality (https://zendy.io/title/10.1002/bit.10255). Biotechnol Bioeng 2002. Snippet.
5. deZengotita VM, Kimura R, Miller WM. Effects of CO2 and osmolality on hybridoma cells: growth, metabolism and monoclonal antibody production. Cytotechnology 1998;28:213-227. https://pmc.ncbi.nlm.nih.gov/articles/PMC3449846 . Abstract (body is PDF only).
6. Mostafa SS, Gu X. Strategies for improved dCO2 removal in large-scale fed-batch cultures. Biotechnol Prog 2003;19:45-51. https://zendy.io/title/10.1021/bp0256263 . Abstract.
7. Humbird D. Scale-up economics for cultured meat. Biotechnol Bioeng 2021;118:3239-3250. https://pmc.ncbi.nlm.nih.gov/articles/PMC8362201 . Full text.
8. Bowers JS. Sparger and surface gas transfer for cell culture bioreactors. AIChE Annual Meeting 2008, extended abstract. https://skoge.folk.ntnu.no/prost/proceedings/aiche-2008/data/papers/P118781.pdf . Full text. Not peer reviewed. States agitation as "approximately 2.5 mW/m3", which looks like a unit error.
9. Nickel N, Fitschen J, Haase I, Kuschel M, Schulz TW, Wucherpfennig T, Schlüter M. Novel sparging strategies to enhance dissolved carbon dioxide stripping in industrial scale stirred tank reactors. Front Chem Eng 2024;6:1470991. https://www.frontiersin.org/journals/chemical-engineering/articles/10.3389/fceng.2024.1470991/full . Full text.
10. Sieblist C, Hägeholz O, Aehle M, Jenzsch M, Pohlscheidt M, Lübbert A. Insights into large-scale cell-culture reactors: II. Gas-phase mixing and CO2 stripping. Biotechnol J 2011;6:1547-1556. https://doi.org/10.1002/biot.201100153 . Abstract only.
11. Sieblist C. Dissertation, Universität Halle, 2012. https://opendata.uni-halle.de/bitstream/1981185920/7773/1/OnlineVersion_Dissertation_Sieblist_19122012.pdf . Snippet (site blocked automated reading).
12. Xing Z et al. A carbon dioxide stripping model for mammalian cell culture in manufacturing scale bioreactors. Cell Culture Engineering XV, 2016. https://dc.engconfintl.org/cellculture_xv/26 . Snippet. (Journal version: Biotechnol Bioeng 2017; not read.)
13. Matsunaga N, Kano K, Maki Y, Dobashi T. Culture scale-up studies as seen from the viewpoint of oxygen supply and dissolved carbon dioxide stripping. J Biosci Bioeng 2009. https://agris.fao.org/search/ru/records/64724ac52c1d629bc979e12d . Abstract.
14. Doi T et al. Development of a scale-up strategy for CHO cell culture processes using the kLa ratio as a direct indicator of gas stripping conditions. Biotechnol Prog 2020. https://zendy.io/title/10.1002/btpr.3000 . Snippet. Title recalled from the search listing; check before citing.
15. Xing Z, Kenty BM, Li ZJ, Lee SS. Scale-up analysis for a CHO cell culture process in large-scale bioreactors. Biotechnol Bioeng 2009;103:733-746. https://doi.org/10.1002/bit.22287 . Abstract. The kLa correlation is taken from Humbird 2021, not from this paper directly.
16. Hu W, Berdugo C, Chalmers JJ. The potential of hydrodynamic damage to animal cells of industrial relevance: current understanding. Cytotechnology 2011;63:445-460. https://pmc.ncbi.nlm.nih.gov/articles/PMC3176934/ . Full text (first 100,000 characters read).
17. Dynamic membrane aeration paper. https://pmc.ncbi.nlm.nih.gov/articles/PMC2677146 . Snippet; citation details not confirmed.
18. Walls PLL, McRae O, Natarajan V, Johnson C, Antoniou C, Bird JC. Quantifying the potential for bursting bubbles to damage suspended cells. Sci Rep 2017;7:15102. https://pmc.ncbi.nlm.nih.gov/articles/PMC5678173 . Full text.
19. Nienow AW, Scott WH, Hewitt CJ, Thomas CR, Lewis G, Amanullah A, Kiss R, Meier SJ. Scale-down studies for assessing the impact of different stress parameters on growth and product quality during animal cell culture. Chem Eng Res Des 2013;91:2265-2274. https://repository.lboro.ac.uk/articles/journal_contribution/Scale-down_studies_for_assessing_the_impact_of_different_stress_parameters_on_growth_and_product_quality_during_animal_cell_culture/9244400 . Abstract (PDF returned HTTP 403).
20. Sieck JB et al. Development of a scale-down model of hydrodynamic stress to study the performance of an industrial CHO cell line under simulated production scale bioreactor conditions. J Biotechnol 2013;164:41-49. https://katalog.lib.cas.cz/KNAV/EdsRecord/edselp,S0168165613005439 . Snippet of abstract.
21. BioProcess International. Superior scalability of single-use bioreactors. https://bioprocessintl.com/single-use/superior-scalability-of-single-use-bioreactors . Snippet. Trade press.
22. US Patent 8,667,832. Method and system for particle settling velocity measurement. https://patents.google.com/patent/US8667832 . Snippet. Cites Searles 1994 for the velocities.
23. Belovich J et al. A simple apparatus for measuring cell settling velocity. Cleveland State University. https://engagedscholarship.csuohio.edu/encbe_facpub/46 . Snippet.
24. Pohlscheidt M et al. Optimizing capacity utilization by large scale 3000 L perfusion in seed train bioreactors. Biotechnol Prog 2013;29:222-229. https://katalog.lib.cas.cz/KNAV/EdsRecord/edsair,edsair.doi.dedup.....52b488f846ee299bb3bfc379f2bf2a8a . Abstract.
25. Coronel J, Gränicher G, Sandig V, Noll T, Genzel Y, Reichl U. Application of an inclined settler for cell culture-based influenza A virus production in perfusion mode. Front Bioeng Biotechnol 2020;8:672. https://www.frontiersin.org/journals/bioengineering-and-biotechnology/articles/10.3389/fbioe.2020.00672/full . Full text.
26. Romann P, Kolar J, Chappuis L, Herwig C, Villiger TK, Bielser J-M. Maximizing yield of perfusion cell culture processes: evaluation and scale-up of continuous bleed recycling. Biochem Eng J 2023;193:108873. https://irf.fhnw.ch/bitstreams/c89ee89e-90b8-4699-b46e-83b7e9522721/download . Full text (introduction and Table 1 read closely; results skimmed).
27. Searles JA, Todd P, Kompala DS. Viable cell recycle with an inclined settler in the perfusion culture of suspended recombinant Chinese hamster ovary cells. Biotechnol Prog 1994;10:198-206. https://zendy.io/title/10.1021/bp00026a600 . Snippet of abstract.
28. Voisard D, Meuwly F, Ruffieux P-A, Baer G, Kadouri A. Potential of cell retention techniques for large-scale high-density perfusion culture of suspended mammalian cells. Biotechnol Bioeng 2003;82:751-765. https://pubmed.ncbi.nlm.nih.gov/12701141 . Snippet of abstract.
29. Kompala DS, Batt B, Freeman C, Samuel P (Sudhin Biopharma). Compact cell settlers, Cell Culture Engineering XV (2016) and Integrated Continuous Biomanufacturing II. https://dc.engconfintl.org/cellculture_xv/134 ; https://dc.engconfintl.org/biomanufact_ii/32/ . Snippet. Vendor material.
30. Gorenflo VM, Smith L, Dedinsky B, Persson B, Piret JM. Scale-up and optimization of an acoustic filter for 200 L/day perfusion of a CHO cell culture. Biotechnol Bioeng 2002. https://zendy.io/title/10.1002/bit.10386 . Snippet of abstract.
31. Induction of apoptosis in oxygen-deprived cultures of hybridoma cells. Cytotechnology (1994; authors not confirmed, likely Mercille and Massie). https://link.springer.com/doi/10.1007/BF00762386 . Snippet of abstract.
32. Spheroid necrosis and diffusion-limit statements came from a search summary that did not tie each number to one paper. Candidate sources returned: https://pmc.ncbi.nlm.nih.gov/articles/PMC4835055 , https://pmc.ncbi.nlm.nih.gov/articles/PMC7934264 , https://pmc.ncbi.nlm.nih.gov/articles/PMC4961208 , https://pmc.ncbi.nlm.nih.gov/articles/3436947 . Snippet. Must be checked before citing.
33. McMaster University thesis on bovine satellite cells in 3D culture. https://macsphere.mcmaster.ca/handle/11375/30316 . Snippet.
34. Pasitka L et al. Spontaneous immortalization of chicken fibroblasts generates stable, high-yield cell lines for serum-free production of cultured meat. Nature Food 2023. https://cris.huji.ac.il/en/publications/spontaneous-immortalization-of-chicken-fibroblasts-generates-stab-2/ . Abstract. Follow-up: https://yaakovnahmias.huji.ac.il/node/3188801 .

---

## What could not be found

- **Primary text of the key paywalled papers:** Gray 1996 (so the 105 vs 150 mmHg conflict is unresolved), Kimura and Miller 1996, Xing 2009 (correlation seen only through Humbird), Sieblist 2011 (no numbers), Chisti 2000, Nienow 2006, Ozturk 1996 (the origin of the 0.006 m/s limit), Matsunaga 2009, Doi 2020, He 2019, Goudar, Batt 1990, Shen and Yanagimachi 2011, Voisard 2003 capacity table, Freeman 2017.
- **CO2 growth thresholds** for NS0, BHK, HEK, insect cells, and any muscle, fibroblast or fish cells. Onset level and 50% level as a clean dose-response for any one line.
- **Adaptation to high pCO2.**
- **pCO2 operating ranges and excursions in named 10-25 m3 commercial tanks.** Only general statements (150-200 mmHg "may be reached"; 150 mmHg in an unspecified large-scale CHO process; 179 mmHg at pilot scale).
- **A published correlation for CO2 removal vs gas flow and tank height.** Only the Bowers saturation formula and descriptions of the Sieblist and Xing models.
- **Maximum sparge rates at 10-25 m3 with and without Pluronic F-68**, and any dose-response of damage vs protectant concentration at scale.
- **Verification of "CHO tolerates about 1000 W/m3"** (Nienow 2013): only conflicting snippets (250 vs 1000 W/m3).
- **Aspect ratios of named large cell-culture tanks**, and any quantitative squat-vs-tall comparison for CO2.
- **Membrane aeration transfer rates**, and any scale above 200 L.
- **Medium density; measured settling velocities of aggregates or spheroids vs size; a reliable measured cell density.**
- **Whether the largest settlers (Pohlscheidt 2013; Romann 2023) were cooled, and to what temperature.** Searles 1994 temperature not obtained.
- **Hydrocyclone scale, efficiency and limits.**
- **Tolerance to anoxia when cooled**, and anoxia data for CHO or meat-relevant cells in minutes.
- **Aggregate culture of muscle, fibroblast or fish cells for cultivated meat:** aggregate sizes, necrotic-core thresholds and growth rates relative to single cells.
