# Alternative A: reusable, cleanable membranes from wastewater, food and medicine

Research date: 2026-11-15. Scope note: the brief reached me cut off after "1. Wastewater membrane bioreactors (... Suez ZeeWeed,
Kubota, M[itsubishi])". I covered the candidates the brief names or implies: (1) wastewater MBR membranes, (2) dairy/food ceramic
membranes, (3) food-and-beverage polymeric hollow fibres (wine, beer), (4) reusable pharma hollow fibres, (5) medical hollow
fibres (haemodialysers, plasma separators). I did not repeat what `research_notes/retention_devices.md` and
`retention_devices_sources/membrane_filters.md` already hold.

Labels: **MEAS** measured; **VEND** vendor claim; **REV** review/secondary; **INF** my arithmetic or judgement.
Access: **full** (text extracted and searched), **part** (page fetched, extract read), **snippet** (search-tool summary of the
result only; not read). Most numbers below are **snippet**: treat them as leads, not checked figures. No membrane price here
comes from a quote.

## 0. The target

The model charges $1,450/m2 / 3,960 L/m2 = **$0.37 per L of permeate**. 10x cheaper means **≤ $0.037/L**. Cost per litre of
any membrane = price per m2 / litres per m2 over its life, and litres per m2 = flux x hours of life. So a 10x cut needs one of:

- the same life at ≤ $145/m2 (a cheaper membrane, even single-use);
- the same price with ≥ 39,600 L/m2 of life (≈ 10 runs of 33 days at 5 LMH, i.e. cleaning that really restores it);
- some mix.

The price gap is the easy half. Mass-market hollow fibres of the same polymers cost $3-150/m2 (below), 10-500 times less than the
model's pharma price. **The hard half is life at 12-25% cells by volume, which nobody has measured for a month in any membrane
(existing note s.7). Switching supplier does not change that unknown.**

## 1. Candidates

### 1a. Wastewater MBR membranes (Suez/Veolia ZeeWeed 500D, Kubota flat sheet, Mitsubishi/Toray)

| Item | Value | Label | Source, access |
|---|---|---|---|
| ZeeWeed 500D: pore, material limits | 0.04 um nominal PVDF; **max operating temperature 40 °C**; pH 5-9.5 in operation, 2-10.5 in cleaning; cleaning Cl2 up to 1,000 ppm; modules 31.6 and 40.9 m2 | VEND | GE-era brochure via https://www.environmental-expert.com/downloads/zeeweed-500-membrane-bioreactor-mbr-brochure-397017 and https://spertasystems.com/parameter-suez-zeeweed-500d/ , *snippet* |
| Kubota flat sheet | 0.2 um average (0.4 um maximum); MLSS up to 20,000 mg/L (ES/EK series); 5-40 °C (reseller) | VEND | https://www.kubota.com/products/solutions/lineup/pdf/KUBOTA_Submerged_Membrane_Unit_SP_Series.pdf , *snippet* |
| MLSS operated | 3,000-15,000 mg/L (GE packaged systems) | VEND | https://manualmachine.com/gepw/packagedsystems/1565852-user-manual , *snippet* |
| Life | Manufacturer recommends 10 years; one Virginia plant (ZeeWeed 500D-type cassettes) got up to 16 years; full replacement there $5-6M | MEAS (utility report) | https://www.hazenandsawyer.com/projects/optimization-helps-virginia-plant-use-membranes-60-longer , *part (fetch)*. Fleet average 12.5+ years: WEF buyers' guide https://wefbuyersguide.wef.org/documents/22365 , *snippet* |
| Price | Toray hollow fibre ≈ $45/m2, flat sheet ≈ $65/m2 (vendor article, may include frame); a cost study used $85/m2 at 12 LMH; a US market report $80-150/m2 for complete municipal modules; Chinese PVDF fibre $11-40/m2 | VEND/REV | https://spertasystems.com/how-much-is-the-mbr-membrane/ ; https://www.researchgate.net/publication/329597193_Sidestream_vs_immersed_membrane_bioreactors_a_cost_analysis ; https://www.indexbox.io/store/united-states-hollow-fiber-mbr-module-market-analysis-forecast-size-trends-and-insights/ ; https://hydropurewater.com/blog/175-hollow-fiber-mbr-cost-price-2025-breakdown-by-module-material-capacity.html — all *snippet* |
| Design flux | 10-12 LMH in a cost study; 15-30 LMH vendor; worked example 12 LMH at 120 m2 of membrane per m3 of module | REV/VEND | ResearchGate cost study above; https://www.cedengineering.com/userfiles/Biological%20Wastewater%20Treatment%20III%20-%20MBR%20Processes%20R1.pdf , *snippet* |
| Air scour | Full-scale SADm 0.18-1.28 Nm3 air per m2 per h; vendors recommend 0.5-1.5 | REV | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12029511/ ; https://www.mdpi.com/2077-0375/15/4/111 , *snippet* |

Cost per litre (INF): $45-150/m2 over 10 years at 5 LMH and 8,000 h/yr (400,000 L/m2) = **$0.0001-0.0004/L**; even at a 1-year life,
$0.001-0.004/L. 100-1,000x below the model. **The price is not the obstacle; everything else is:**

- **Sterility.** PVDF modules rated to 40 °C with potting and open frames cannot be steamed. Chlorine (1,000 ppm) sanitises; it does not
  sterilise, and a 33-day run in rich medium amplifies any survivor (INF).
- **Solids.** MBRs run at 3-20 g/L of dry sludge. 258 g/L of wet cells is about 50-75 g/L dry (INF, assuming 20-30% dry matter):
  3-4 times the highest rating found.
- **Air scour inside a cell tank.** At the central duty and 5 LMH (376 m2), SADm 0.18-1.28 Nm3/m2/h is 70-480 Nm3/h into 16 m3 of
  culture, 0.07-0.5 vvm of coarse bubbles (INF). Foam, bubble-burst damage and Pluronic demand at that rate are untested with animal
  cells. No precedent found for an air-scoured submerged membrane in animal-cell perfusion (searched); the closest is a patent for an
  external gas-scrubbed hollow-fibre filter (US12157877, https://patents.google.com/patent/US12157877 , *snippet*).
- **Space.** At 120 m2 per m3 of module, 376 m2 takes 3.1 m3 inside a 16 m3 stirred tank; at Ott's 0.68 LMH (2,765 m2) it takes 23 m3
  (INF). An external submerged tank brings back the settler's no-oxygen problem (existing note s.3).

Verdict: **not usable as built.** The useful fact is the price: PVDF hollow fibre costs tens of dollars per m2 when made by the
million m2.

### 1b. Dairy/food ceramic membranes (Pall Membralox, Tetra Pak/APV, TAMI)

| Item | Value | Label | Source, access |
|---|---|---|---|
| Life | "10+ years" | VEND | https://www.tetrapak.com/ca/processing/membrane-filtration/membrane-types , *snippet* |
| Temperature | Pall Membralox GP listing: sanitizable/sterilizable, but max 95 °C and 10 bar on the listed housing | VEND | https://shop.pall.com/us/en/food-beverage/food-ingredients/fruit-juice-clarification/zidgri78ly3 , *snippet* |
| Price | Alumina/zirconia ceramic membranes **$500-3,000/m2**; commercial alumina ≈ $500/m2; polymeric $20-200/m2 | REV | Alsubei et al. 2024, J Membr Sci 690:122226 (citing their ref. 9), https://discovery.ucl.ac.uk/id/eprint/10180859/1/1-s2.0-S0376738823008827-main.pdf , *full (pdftotext, searched)* |
| Milk MF operating point | 1.4 um ceramic, **crossflow 6.2 m/s**, TMP 128 kPa | MEAS | https://core.ac.uk/download/10833648.pdf , *snippet* |
| Animal-cell use | Patents list ceramic and stainless hollow fibres as allowed materials; **no cell-culture perfusion data with ceramic found** (searched) | — | WO2017180814A1, https://patents.google.com/patent/WO2017180814A1/en , *snippet* |

Cost per litre (INF): $500-3,000/m2 over 10 years at 5 LMH (400,000 L/m2) = **$0.001-0.008/L**; over 1 year, $0.013-0.075/L. 5-300x
below the model. Problems:

- **Shear.** Ceramic dairy MF works because of turbulence. At 6.2 m/s in a 4 mm channel, Re ≈ 25,000 and the wall stress is ≈ 100 Pa
  (Fanning f ≈ 0.079 Re^-0.25; INF), about 25 times the ATF lumen's ≈ 4 Pa (2,000 s^-1 x 2.2 mPa s; existing note). A centrifugal
  pump at that flow adds more. At the 10 passes/h the central case needs (existing note), I expect large lysis (INF, untested).
- **At low crossflow** (laminar, 0.3-0.5 m/s like TFF), ceramic loses its flux advantage and behaves like a reusable TFF module. Then
  its value is reuse only: same fouling unknown, at 0.3-2x the pharma price per m2 but cleanable with hot caustic and acid for years.
- **Steam.** Ceramic itself takes steam; the housings and gaskets set the limit (95 °C on the Pall listing). Stainless housings rated
  for SIP exist in pharma but I found no price.

Verdict: **the strongest candidate for a reusable, steamable module, run slowly as TFF.** Unproven on animal cells.

### 1c. Food and beverage polymeric hollow fibres (Pall Oenoflow, PROFi)

| Item | Value | Label | Source, access |
|---|---|---|---|
| Wine crossflow PVDF hollow fibre | Hot-water sanitisable; pH 1-14 cleaning; **service life 6-8 years** | VEND | https://www.pall.com/content/dam/pall/food-beverage/literature-library/non-gated/How_to_choose_a_wine_crossflow_microfiltration_system.pdf , *snippet* |
| Oenoflow XL-S cleaning | max 65 °C | VEND | https://shop.pall.com/us/en/products/systems/zidgri78ly6 , *snippet* |
| Beer crossflow total membrane cost | **$0.42 per hL = $0.0042/L** (2001), the same as kieselguhr | MEAS (industry) | MBAA TQ 2001, https://mbaa.com/publications/tq/tqPastIssues/2001/Abstracts/tq01ab25.htm , *snippet* |
| Scale | > 150 million hL of beer a year filtered by crossflow | VEND | https://www.pall.com/content/dam/pall/food-beverage/literature-library/non-gated/articles/FBPUBPROFICRAFTEN.pdf , *snippet* |
| Price per m2 | **not found** | — | |

INF: beer at $0.0042/L total is ~90x below the model's $0.37/L. But beer reaches the membrane at well under 1% solids (often after
a centrifuge, per the PROFi page), at fluxes far above 5 LMH, for runs of hours between cleanings. At 25% cells the flux and the run
length both fall; neither the 6-8 years nor the $/hL transfers. The relevant fact is that cleanable PVDF/PES hollow fibres of
pharma-like geometry run in food plants with hot-water sanitisation, which is a food-safety standard, not a sterility standard.

Verdict: **plausible as a food-grade TFF module if sanitisation is accepted as enough**; price unknown.

### 1d. Reusable pharma hollow fibres (Sartorius Reuse Line, Cobetter Lab+, autoclavable Spectrum/WaterSep)

| Item | Value | Label | Source, access |
|---|---|---|---|
| Cleaning | 0.5-1.0 N NaOH; store in 0.1 N NaOH | VEND | https://shop.sartorius.com.cn/cn/p/reuse-line/M_Reuse_Line , *snippet* |
| Steam | 30 autoclave cycles (121 °C, 30 min); 10 SIP cycles at 123 °C | VEND | https://shop.cobetter.com/products/1mm-lab-hollow-fiber-tff-mpes-membrane-autoclavable-1 , *snippet* |
| Recovery | Typical water-flux recovery after cleaning 70-80%; a 10-cycle case: ≈ 30 LMH for 4 cycles, then ≈ 23 LMH (protein process, not cells) | VEND | https://cobetter.com/technical/cobetter-hollow-fiber-cleaning-and-reuse-guidelines.html , *part (fetch)* |
| Reuse life | One capsule's reuse life was only **30-40% of its first life** | patent | US 6,261,457, https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6261457 , *snippet* |

Cost per litre (INF): same ≈ $1,450/m2. Cleaned between runs (the plant turns the tank around anyway) and reused up to 4 more times
at 30-80% of the first life: throughput 3,960 x (1 + 4 x 0.3-0.8) = 8,700-16,600 L/m2, i.e. **$0.09-0.17/L: a 2-4x cut, not 10x.**
The SIP limit (10 cycles) and protein-specific recovery data cap it. No reuse data on cell-culture fouling found.

Verdict: **easiest to adopt (same validated module, same sterility), but 2-4x at most.**

### 1e. Medical hollow fibres: haemodialysers and plasma separators

| Item | Value | Label | Source, access |
|---|---|---|---|
| Dialyser price | Average selling price **≈ $6 per unit** (North America, 2024, manufacturer level); $14 retail (Nipro, eBay); **$24.51** per high-flux dialyser (Tanzania, 2015) | REV/VEND/MEAS | https://www.kenresearch.com/industry-reports/north-america-dialyzer-market.md ; https://www.ebay.com/itm/306420006431 ; https://healtheconomicsreview.biomedcentral.com/articles/10.1186/s13561-015-0064-4/tables/5 — *snippet* |
| Fresenius FX 80 | **1.8 m2, 185 um fibre bore**; KUF ≈ 59 mL/h/mmHg **measured with human blood at haematocrit 32%**; inline steam sterilised | VEND | https://www.FreseniusMedicalCare.com/en/healthcare-professionals/hemodialysis/dialyzers/fx-high-and-low-flux-dialyzers , *snippet* |
| Filtration from whole blood | Post-dilution HDF: 17-27 L of convection per 4 h session; filtration fraction 20-30% of blood flow; high haematocrit lowers convection (-1.4 L per 10 points) | MEAS (clinical) | https://pmc.ncbi.nlm.nih.gov/articles/PMC4354295 , *snippet* |
| Reuse | Historically 3-5 reuses in the mid-1980s; Taiwan recommends 6 for high-flux; discard below 80% of initial fibre volume | REV | https://www.tsn.org.tw/archive/20210901/59600e31-c8ec-4009-a423-94c9473ed90a/59600e31-c8ec-4009-a423-94c9473ed90a.pdf ; patent US 6,945,257 — *snippet* |
| Plasma separator (Asahi Plasmaflo OP) | 0.2/0.5/0.8 m2; **0.3 um maximum pore**; polyethylene with EVOH coating; gamma sterilised; **price not found** | VEND | https://www.asahi-kasei.co.jp/medical/en/apheresis/product/plasma/op/spec.html , *part (fetch)* |

Arithmetic (INF):
- Price: $6-25 / 1.8 m2 = **$3-14/m2**, 100-500x below $1,450.
- Flux from blood: 17-27 L / 4 h / ≈ 2 m2 = **2-3.4 LMH**, from a suspension that is ≈ 30-40% cells by volume (red cells are 8 um and
  deformable; these cells are 17 um and stiffer). This is the only mass-produced membrane I found that routinely filters a fluid as
  thick as the central case, under sterility.
- Cost per litre at 2.5 LMH: life of 4 days (Veje-like fouling) = 240 L/m2 → $0.013-0.06/L (6-30x cut); life of a 33-day run = 2,000
  L/m2 → $0.002-0.007/L (50-200x).
- Size: central duty 1,880 L/h / 2.5 LMH = 750 m2 = **≈ 420 dialysers** in parallel; reference 160 L/h → 36 dialysers. The
  manifolds, sterile connections and pumps, not the fibres, become the cost (the model's assumed $1k/m2 of hardware would be $0.75M
  bare at central: I cannot check it for dialyser arrays).

Catches:
- **Bore.** 185 um is 11 cell diameters. Meat-cell aggregates (Veje saw 36-50% of CHO in aggregates; existing note) would plug fibres;
  plasma separators (≈ 330 um bores, from the patent tables; *snippet*, garbled) are safer.
- **High-flux dialysers are ultrafilters**: they hold back albumin and most growth factors. The permeate would be protein-free.
  Either a defect (proteins accumulate: at the central Q/B = 7.3, a fed protein would rise up to ~7x unless fed only at the bleed
  rate) or an opportunity (feed proteins only to replace what the bleed removes, cutting recombinant-protein use per kg by up to
  Q/B; INF, untested, and some secreted inhibitors would also accumulate).
- They are designed for 4 h with anticoagulant. Month-long life is unknown.

Verdict: **the cheapest sterile membrane per m2 by far, and the only one proven on a ~35%-cells fluid.** Most promising for a 10x
cut, but no one has run animal-cell perfusion on dialyser arrays that I found.

## 2. Summary table (membrane cost only; INF)

| Candidate | $/m2 | Life basis | $/L permeate | vs $0.37 | Sterile for 33 d? | Shown on animal cells at ≥ 12% by volume? |
|---|---|---|---|---|---|---|
| Model (pharma single-use) | 1,450 | 3,960 L/m2 | 0.37 | 1x | yes | days, 4 L (Clincke) |
| Pharma reusable, 5 uses | ≈ 1,450 | 8,700-16,600 L/m2 | 0.09-0.17 | 2-4x | yes (SIP ≤ 10 cycles) | no reuse data |
| Dialysers, single use | 3-14 | 240-2,000 L/m2 | 0.002-0.06 | 6-200x | yes (steam/gamma) | no (blood only) |
| Food PVDF hollow fibre | not found | 6-8 yr in wine | beer: 0.004 total | ~90x (beer) | sanitised, not sterile | no |
| Ceramic, run as slow TFF | 500-3,000 | 1-10 yr | 0.001-0.075 | 5-300x | steamable element; housing-limited | no |
| MBR PVDF, submerged | 11-150 | 10-16 yr | 0.0001-0.004 | 100-1,000x | no (40 °C) | no |

The membrane line in the central case would fall from $8.83/kg to $0.9/kg at a 10x cut. Holding everything else, the central
scenario moves from $26.64 toward about $18.7 (INF, linear; ignores any extra capital for CIP skids, A/B banks or stainless
housings, which reusable systems need and which I could not price).

## 3. Probabilities (judgement)

| Statement | P |
|---|---|
| Some membrane retention, at any cost, holds the central case for 33 days (existing note) | 35% |
| Given that, a non-pharma or reusable membrane does it at ≤ $0.037/L (10x) | 45% |
| → unconditional: central case gets ≤ $0.037/L membranes | **≈ 15%** |
| Reference case gets ≤ $0.037/L membranes (75% x 55%) | ≈ 40% |
| Dialyser or plasma-separator arrays hold 12% by volume for 33 days | 30% |
| Same at 25% by volume | 15% |
| Ceramic run as slow TFF holds 25% for 33 days and recovers ≥ 80% flux after CIP for ≥ 10 runs | 15% |
| Ceramic at dairy crossflow (≥ 5 m/s) keeps viability ≥ 90% | 5% |
| A submerged, air-scoured MBR module works in a 33-day sterile animal-cell run | 5% |
| Reusing pharma modules gives ≥ 10x | 5% |

## 4. What this means

1. **Price per m2 is 10-500x compressible**: the same polymers in dialysers and MBRs cost $3-150/m2. The model's $1,450/m2 is a
   pharma low-volume price, not a materials floor.
2. **Life at 25% cells is the binding unknown** and is the same for every candidate. A 10x cut via cheaper membranes still needs
   ≥ 400 L/m2 of life (≈ 3-4 days at 5 LMH) at $14/m2, which is about what Veje's CHO membranes reached.
3. Best routes, in order: (a) dialyser/plasma-separator-grade hollow fibres bought at medical volume, used once per run or per few
   days (cheap, sterile, proven on blood); (b) ceramic or stainless-housed modules cleaned in place between runs (only if cleaning
   restores flux after cell fouling); (c) reused pharma modules (2-4x only).
4. Wastewater MBR hardware is out: not sterilisable, rated for a quarter of the solids, and needs air scour in the culture.

## 5. Not found (searched)

- Any animal-cell perfusion with ceramic, MBR-type, dialyser or plasma-separator membranes as cell retention.
- Price per m2 of food PVDF/PES hollow fibres (Pall, Pentair), of Plasmaflo plasma separators, of SIP-rated stainless/ceramic housings.
- Flux recovery after CIP for membranes fouled by animal cells (only protein-process data).
- A primary, peer-reviewed MBR membrane price series (only vendor articles and one cost study's assumption).
