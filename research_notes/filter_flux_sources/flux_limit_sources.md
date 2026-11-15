# Flux limit for hollow-fibre cell retention at 12-25% v/v cells: sources and numbers

Question: is a sustained 5 L/m2/h (LMH) for 30 days (3,960 L/m2 per membrane) above a physical limit (shear-induced back-transport, critical flux, cake)?

Access levels: FULL = I read the full text locally (PDF/XML converted to text; key page visually checked where noted). ABSTRACT = abstract only. SNIPPET = search-engine summary only (NOT read; listed only so you know it exists). Tags: [measured], [model], [review], [vendor/patent].

## Bottom line

1. The shear-induced-diffusion back-transport limit, as printed in a source I read, is 57-800 LMH for your parameter grid (tables below), i.e. 11x to 160x above 5 LMH. Even the worst corner (L = 1 m, gamma_w = 1000 1/s, phi_b = 0.25) gives about 57-60 LMH. Dividing by 4 (the real-yeast shortfall of Redkar and Davis, 1993) still gives about 14 LMH. By this model, 5 LMH is NOT above the back-transport limit. It would need gamma_w of only about 25-90 1/s to reach 5 LMH.
2. Caveats: (a) the model is for rigid, non-adhesive, near-monodisperse spheres and the Davis-Sherwood form states validity for phi_b < 0.1, so phi_b = 0.12 and 0.25 are extrapolations (the printed ln form requires phi_w - phi_b << phi_w, which fails at phi_b = 0.25); (b) it ignores fouling by cell debris, DNA, protein, antifoam, which is what limits real perfusion; (c) it ignores concentration of the retentate along the fibre.
3. Measured long-term sustainable flux in mammalian perfusion is much lower than the back-transport limit: typical 2-3 LMH (Veje 2024, citing literature; Radoniqi 2018: 2 LMH), runs at 1-2 LMH ending with TMP rise after 450-1,200 L/m2 (Pinto 2020). Veje 2024 saw fouling at 8.3 LMH after about 3-6 days (about 600-1,200 L/m2, my arithmetic). Your 3,960 L/m2 per membrane is about 3-9x higher than those throughputs. So the practical risk to the 5 LMH assumption is fouling and TMP rise, not cell back-transport.
4. One counter-example: a reverse-asymmetric hollow fibre (open 40 um side facing feed) in ATF mode ran 14 days at 152-229 LMH with no fouling, but in a 1.5 L culture with a 0.00041 m2 module and VCD not stated in the text (see section 4). Treat as evidence that high flux is not physically barred, not as evidence for a 30-day run at 25% v/v.
5. Calibration (my judgement, not sourced): P(5 LMH is above the cell back-transport physical limit) under 5%. P(5 LMH for 30 days per membrane, 3,960 L/m2, at 12-25% v/v is achievable with a standard microfiltration hollow fibre without TMP-driven replacement) about 15-25%. Flux at 12-25% v/v cells (about 10x the volume fraction of the 1-2e7 cells/mL regimes most data come from) is largely untested in the sources I could read.

## 1. Back-transport formulas as printed

### 1a. Belfort, Davis and Zydney 1994 form, restated in a PhD thesis [model/review], FULL
- Source: H. K. Vyas, "Crossflow microfiltration of suspensions containing lactalbumin particles", PhD thesis, Massey University 1999. URL: https://mro.massey.ac.nz/bitstreams/9a5858c5-4545-45cb-bb8c-3b9aea52c143/download . Section 2.6.2.2, thesis page 2.26 (PDF page 43). I rendered the page image and checked the equations visually.
- Text: "The permeate flux (length averaged) as given by Belfort et al. (1994) can be obtained by"
  - Eq 2.18: J = 0.078 gamma . (phi_w r_p^4 / (phi_b L))^(1/3) . ln(phi_w/phi_b)  when phi_w - phi_b << phi_w
  - Eq 2.19: J = 0.126 gamma . (phi_w r_p^4 / (phi_b L))^(1/3)  when phi_b << phi_w
- Symbols (thesis): gamma = shear rate (1/s) (wall shear rate in the usual application); r_p = particle radius (m); L = membrane/tube length; phi_w, phi_b = particle volume fraction at the wall and in the bulk.
- IMPORTANT correction to the form you quoted: the cube root applies to (phi_w r_p^4/(phi_b L)); the ln(phi_w/phi_b) is OUTSIDE the cube root (first power), and phi_w/phi_b is inside the cube root. Your form J = 0.078 gamma (a^4/L)^(1/3) [ln(phi_w/phi_b)]^(1/3) is not what is printed here.
- Same thesis, same section: Zydney and Colton (1986) replaced Brownian diffusivity by shear-induced diffusivity, using Ds ~ (coefficient) gamma r_p^2 from Eckstein et al. (1977). The OCR printed the coefficient as "0.3"; I did not check it visually (another source, the search summary of a ScienceDirect paper, SNIPPET, gives 0.03 gamma_w a^2; unresolved). Davis and Sherwood (1990) and Sethi and Wiesner (1997) used Leighton and Acrivos (1987): Ds = gamma a^2 . 0.33 phi^2 (1 + 0.5 e^(8.8 phi)).
- Quote on regime: "The shear-induced diffusion dominates in typical CFMF applications involving micron sized and larger particles."

### 1b. Davis and Sherwood similarity solution, restated in a PhD thesis [model], FULL
- Source: J. Kromkamp, "Particle separation and fractionation by microfiltration", PhD thesis, Wageningen 2005 (author name from title page). URL: https://edepot.wur.nl/121692 . Text extract read (OCR/text layer, not visually checked).
- Eq 5.2 / 6.2 / 8.28: J_ss = 0.072 gamma_wall,0 . (phi_c a^4 / (phi_b L_m))^(1/3). Symbols (thesis, eq 6.2 text): gamma_wall,0 = nominal wall shear rate; phi_c (also phi_w) and phi_b = particle volume fraction in the particle layer and in the bulk; a = particle radius; L_m = total membrane length; angle brackets = length-averaged flux. Attributed to Davis and Sherwood [81] (exact similarity solution of the Romero-Davis model).
- Validity as printed: "valid for a bulk particle volume fraction phi_b < 0.1, ... cake-dominated resistance ... membrane length much longer than the length of the particle-layer-free zone". phi_c = 0.6 used in the thesis calculations (eq 8.28 text).
- Ds = 0.33 gamma a^2 phi^2 (1 + 0.5 e^(8.8 phi)) (eq 5.1/6.1), attributed to Leighton and Acrivos.

### 1c. Primary papers
- Zydney and Colton 1986, Chem. Eng. Commun. 47(1-3):1-21, DOI 10.1080/00986448608911751. ABSTRACT (paraphrase from Penn State Pure page, https://pure.psu.edu/en/publications/a-concentration-polarization-model-for-the-filtrate-flux-in-cross/ ): flux limited by a dynamic concentration-polarization layer; model includes shear-enhanced diffusivity of large particles from mutually induced velocity fields in concentrated shear flow; predictions agree well with data for several particulate suspensions. No formula in the abstract. Note: one search result lists the volume as "41"; Penn State gives 47.
- Davis and Leighton 1987, Romero and Davis 1988/1991, Belfort/Davis/Zydney 1994 (J. Membr. Sci. 96:1-58): NOT FOUND in readable form (paywalled). Searches: web search for "shear-induced diffusion" "0.078" "a^4"; the 0.078 constant appears only in the Massey thesis among what I read.

## 2. Flux calculation (my arithmetic)

Inputs: a = 8.5 um = 8.5e-6 m (a^4 = 5.22e-21 m^4), phi_w = 0.6. Base term B = gamma (phi_w a^4/(phi_b L))^(1/3), in m/s; multiply by 3.6e6 to get LMH. Worked example (gamma = 1000, phi_b = 0.25, L = 0.3): phi_w a^4/(phi_b L) = 0.6 x 5.22e-21 / (0.25 x 0.3) = 4.17e-20; cube root = 3.47e-7 m^(1/3)... (units m^(4/3 -1/3)... result in m); B = 3.47e-4 m/s. Eq 2.18: 0.078 x 3.47e-4 x ln(2.4 = 0.875) = 2.37e-5 m/s = 85.3 LMH. Davis-Sherwood: 0.072 x 3.47e-4 = 2.50e-5 m/s = 89.9 LMH.

| L (m) | gamma_w (1/s) | phi_b | Eq 2.18 (0.078 ln) LMH | D-S 0.072 LMH | Eq 2.19 (0.126) LMH |
|---|---|---|---|---|---|
| 0.3 | 1000 | 0.12 | 200 | 115 | 201 |
| 0.3 | 1000 | 0.25 | 85 | 90 | 157 |
| 0.3 | 2000 | 0.12 | 401 | 230 | 402 |
| 0.3 | 2000 | 0.25 | 171 | 180 | 315 |
| 0.3 | 4000 | 0.12 | 801 | 459 | 804 |
| 0.3 | 4000 | 0.25 | 341 | 360 | 629 |
| 1.0 | 1000 | 0.12 | 134 | 77 | 135 |
| 1.0 | 1000 | 0.25 | 57 | 60 | 105 |
| 1.0 | 2000 | 0.12 | 268 | 154 | 269 |
| 1.0 | 2000 | 0.25 | 114 | 120 | 211 |
| 1.0 | 4000 | 0.12 | 536 | 308 | 538 |
| 1.0 | 4000 | 0.25 | 228 | 241 | 421 |

Comparison with 5 LMH: every cell is 11x (57/5) to about 160x (801/5) above. Shear rate at which the model gives exactly 5 LMH: Eq 2.18: 25 (L 0.3, phi_b 0.12), 59 (0.3, 0.25), 37 (1.0, 0.12), 88 (1.0, 0.25) 1/s; D-S: 44, 56, 65, 83 1/s. Flux scales as gamma, a^(4/3), L^(-1/3).
Note on Eq 2.19 vs 2.18 at phi_b = 0.12: 0.126 is the phi_b << phi_w limit; at phi_b/phi_w = 0.2 the two agree numerically by coincidence of ln(5) = 1.61 x 0.078 = 0.126. At phi_b = 0.25 the ln form is the more conservative; I do not know which is right in that regime.
These numbers are a model ceiling for hydrodynamically-limited cake-free steady state. They say nothing about fouling.

## 3. Measured fluxes, shear rates, fibres

### Redkar and Davis 1993, yeast [measured], ABSTRACT
- Biotechnol. Prog. 9(6):625-634, DOI 10.1021/bp00024a009, PMID 7764351. Retrieved via NCBI E-utilities (efetch abstract text).
- Cross-flow MF of yeast in 0.2 um ceramic and polypropylene tubes. "The steady-state fluxes for unwashed yeast in deionized water or fermentation media are typically 2-4 times lower than those predicted by a model based on ... nonadhesive, rigid spheres undergoing shear-induced back-diffusion. In contrast, the steady-state fluxes observed for washed yeast cells ... are only 10-30% below the predicted values." Steady-state fluxes increase with shear rate and decreasing feed concentration, nearly independent of TMP. No numeric flux in the abstract.

### Veje, Quiros, Kristensen, Jorgensen 2024, CHO, ATF [measured], FULL
- J. Membr. Sci. 701:122764, open access CC BY. URL: https://vbn.aau.dk/ws/files/763659375/1-s2.0-S0376738824003582-main.pdf . Full text read; Fig. 3 viewed.
- Setup: asymmetric polysulfone hollow fibres (Asahi Kasei), nominal 0.4 um, 9 fibres, length 65 cm, inner radius 0.7 mm, 0.025 m2; inside-out ATF mode (XCell ATF2). ATF rate 0.8 L/min; "a shear rate of 5500 s-1 at the inner wall" from gamma = 8v/D = 4Q/(pi r^3) (Eq. 4); I reproduced 5.5e3 1/s from Q = 0.8/9 L/min, r = 0.7 mm. Cell diameters are in their Fig. 4 (not read).
- Cells: VCD from Fig. 3 about 50-63e6 cells/mL at maximum (read from the plot, approximate). Volume fraction not stated; my estimate for 17 um cells (about 2.6 pL each) is about 0.13-0.16.
- Critical flux (improved flux-step method): steps about 0.5, 1, 2, 5, 10, 20, 40, 69 LMH; "fluxes of up to 69 LMH were used without exceeding the critical flux. No sign of fouling was observed for the short-term (<3.5 h) critical flux experiment" (abstract). Flux vs TMP linear for fluxes above 5 LMH (R2 > 0.85). Permeability at high cell density was lower than in clean medium (about 10-11 LMH/bar vs about 22 LMH/bar and above), "indicating increased viscosity or an effect on the boundary layer".
- Long term: harvest started day 3 at 4.3 LMH, 8.3 LMH from day 4. "during prolonged operation at 8.3 LMH the TMP jumped to 0.9-0.95 bar, indicating fouling." Membrane operational times 5.9 and 2.9 days (Exp 1, membranes 1 and 2) and 5.0 and 3.8 days (Exp 2) (my estimate: up to about 1,200 L/m2 for 5.9 d at 8.3 LMH). Authors: 8.3 LMH is "very high compared to typical flux values reported in this area which is 2-3 LMH [8]"; they note the 5500 1/s shear may also contribute (cell lysis).
- Reading: a short-term critical flux above 69 LMH at about 10-16% v/v and 5500 1/s is consistent with the back-transport model (ceiling hundreds of LMH), while sustained flux is limited by slow fouling at far lower flux. Short-term critical flux does not predict 30-day operation.

### Radoniqi, Zhang, Bardliving, Shamlou, Coffman 2018, ATF CFD [measured + model], FULL
- Biotechnol. Bioeng. 115(11), DOI 10.1002/bit.26813, open access. URL: https://rcastoragev2.blob.core.windows.net/8bf3cf23c9fee123d75d5b5164474ff7/PMC6221016.pdf (PMC6221016); text via pdftotext.
- Abstract: "the small average permeate flux values of 2 L m-2 h-1 traditionally used in perfusion bioreactor membranes lead to approximately 50% of the membrane length utilized for permeate flow during each pressure and exhaust phase". Module: 75 lumens, 0.2 um nominal, 20 cm long, 1 mm ID. Experiments were on cell-free supernatant (cells at about 30e6/mL, 75% viability at harvest day 29) with 2 L/m2/h; higher crossflow gave more local flux and more reversible and irreversible resistance. No critical flux stated.

### Pinto et al. 2020, CHO TFF perfusion [measured], FULL
- Biotechnol. Bioeng., DOI 10.1002/bit.27504, PMC7689868, open access. Full text XML via Europe PMC (https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7689868/fullTextXML).
- 75 +/- 10e6 cells/mL (74 +/- 3e6 average). "crossflow shear rates between 1,250 and 3,000 s-1 and permeate flux rates between 1 and 2 L m-2 hr-1, which are commonly employed in perfusion cell culture." Volumetric throughput until TMP rise: about 900-1,200 L/m2 for the 0.2 um Microza at 1-2 LMH ("consistent with previous microfiltration perfusion reports (Clincke, 2017)"); 450-900 L/m2 for 0.65 um. Higher shear gave worse sieving decay. Hollow fibre: 1 mm ID, 20 cm best case. Cites Vickroy, Lorenz and Kelly 2007: lysis proportional to shear stress and lumen residence time.

### Mostafavi et al. 2025 (Zydney and Wickramasinghe groups), CHO clarification [measured], FULL
- Membranes 15(3):78, DOI 10.3390/membranes15030078, PMC11943935. Full text via Europe PMC.
- Introduction: ATF "operating filtrate flux in these systems is typically <3 L m-2 h-1 [9]" (review claim).
- ATF with BioOptimal MF-SL (reverse asymmetric: 0.4 um on permeate side, 40 um open side facing feed; PS; area 0.00041 m2): 14-day perfusion; "average permeate flux was about 152 L m-2 h-1 for the first 5 days and 229 L m-2 h-1 for the remainder ... No fouling occurred and the TMP was below 0.5 psi (2.5 kPa)". Cultures were CHO-S with "cell titers of up to 25 million cells/mL"; the 1.5 vessel volumes/day step was triggered above 10e6 viable cells/mL; peak VCD is in Fig. 8 (not read). Small scale (1.5 L, 1.5 mL/min), short (14 d). Batch concentration at 2000 1/s: initial 1100 LMH with an open-structured fibre; hydrocyclone-TFF with wall shear 620 and 1280 1/s.
- Caveat: operated at low VCD relative to your 12-25% v/v (25e6 cells/mL is about 4-7% v/v for 17 um cells).

### Plasmapheresis, haematocrit about 40% [vendor/patent], PARTIAL (HTML read)
- EP 0112173 "Plasmapheresis process", EPO register HTML: https://data.epo.org/publication-server/rest/v1.2/patents/EP0112173NWA2/document.html . Read via text extraction; I did not read all tables. Statements: examples use whole blood at haematocrit 34-40%; "a flux of about 0.04 mL/minute/cm2 represents a desirable compromise since, at this value an hematocrit of 65% is readily achievable"; claims shear rate 200-2500 1/s ("although higher fluxes are achievable"). 0.04 mL/min/cm2 = 24 L/m2/h (my conversion: 0.04 x 60 x 10^4 / 1000). This is a design target in a patent for a pulsed, recycled process, not a measured critical flux.
- J. Chem. Eng. Japan 20(4):345 (hollow-fibre plasma separation), https://www.jstage.jst.go.jp/article/jcej1968/20/4/20_4_345/_article : ABSTRACT only (paraphrase via fetch): RBC polarization layer is 50-80% of total resistance; plasma viscosity, haematocrit and wall shear rate govern filtrate flux; an estimation equation is proposed but not shown. No numbers.
- Not found: a peer-reviewed table of plasma flux (LMH) vs wall shear rate at Hct 40%. Searches: web search on plasmapheresis flux hematocrit shear; Europe PMC search returned nothing relevant. Okazaki and Yoshida 1976 (Ann. Biomed. Eng.): SNIPPET only (back-diffusion coefficient scales with shear^(1/3)).

## 4. Shear rates and cell damage

- Typical fibre ID and shear: 1 mm ID (Radoniqi, Pinto), 0.7 mm radius (Veje; 1.4 mm ID). Wall shear: 1,250-3,000 1/s (Pinto, "commonly employed"), 2,000 1/s (Mostafavi, "chosen based on the manufacturer's recommendations and previous studies"), 5,500 1/s (Veje, noted as high).
- Damage: Vickroy, Lorenz and Kelly 2007, Biotechnol. Prog. 23:194-199, DOI 10.1021/bp060183e, ABSTRACT: model of shear-induced decrease in live cells during tangential flow filtration; capillary experiments with "maximum laminar shear stress ranged from 10-300 Pa"; "K values ... ranged from 0.06 to 12.5 s-1 ... increased with shear stress, as expected, and also as the solution viability decreased." (Reported verbatim from abstract; no threshold value given in the abstract.) For orientation, my conversion tau = mu x gamma with mu about 1 mPa.s gives 5.5 Pa at 5,500 1/s and 1-3 Pa for 1,250-3,000 1/s (not from a source). So the surveyed ATF/TFF range is below the 10-300 Pa damage-study range, but viscosity of 12-25% v/v suspension would be several times higher (Krieger-type), raising stress at fixed shear rate.
- Wang et al. 2017 (J. Biotechnol. 246:52-60, DOI 10.1016/j.jbiotec.2017.01.020), ABSTRACT: peristaltic pump is the major contributor to shear stress and lysis in TFF; a low-shear centrifugal pump gave TFF comparable to ATF. No numbers.
- A specific lysis-onset shear threshold for CHO or other animal cells: NOT FOUND in a source I could read in full.

## 5. Critical / sustainable flux statements

- Veje 2024 (above): critical flux greater than 69 LMH short-term in ATF at about 50-60e6 cells/mL; sustained 8.3 LMH fouled in days; literature typical 2-3 LMH. FULL.
- Radoniqi 2018 (above): 2 LMH traditional. FULL.
- Pinto 2020 (above): 1-2 LMH commonly employed; 450-1,200 L/m2 throughput to TMP rise. FULL.
- Kelly et al. 2014, Biotechnol. Prog. 30(6) (DOI 10.1002/btpr.1953, PMID 25078788) ABSTRACT: time to fouling in ATF depends on cell density, viability, permeate flow rate and antifoam; model with sticking factors for cells and antifoam micelles. No numbers in abstract. (Not Veje's "critical flux".)
- Clincke et al. 2013 (Biotechnol. Prog., DOI 10.1002/btpr.1704, Parts I and II): SNIPPET only. Search summary said membrane capacity and pCO2 limited TFF cell density, and maximum densities of about 1.3e8 cells/mL, but I did not read the paper; do not cite numbers from it. Searched Europe PMC/web; the full text was not reachable.
- Karst et al. 2016 (Biochem. Eng. J. 110:17-26): NOT FOUND (no abstract or full text retrieved); only citations by later papers (ATF sieving better than TFF).
- Repligen guidance: only a poster snippet (ATF run at 5.7 LMH, vendor material) was returned and I did not read it. Not verified.
- Latulippe et al. 2007 critical flux (DNA transmission) appears in Pinto 2020 as a molecule-transmission concept, not a cell cake limit.

## 6. What was not found / searches used
- Primary Zydney-Colton, Davis-Leighton, Romero-Davis, Belfort 1994 full texts: paywalled; not read. Formulas verified only via two theses (Vyas 1999; Kromkamp 2005) and the Zydney-Colton abstract.
- Plasmapheresis peer-reviewed flux vs shear at Hct 40%; yeast flux numbers in LMH; CHO flux at 100-200e6 cells/mL: not found with numbers in full text.
- Tools: web search (several queries on the formula, critical flux perfusion, plasmapheresis, Veje, Karst), Europe PMC REST and NCBI efetch (abstracts, XML full texts), pdftotext on downloaded PDFs. No repo files edited.
- Arithmetic: Python with the stated inputs; shear check for Veje Eq. 4 reproduced 5.5e3 1/s.
