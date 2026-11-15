# Packed-bed / fixed-bed and hollow-fibre vessels: evidence for the cultivated-meat cost model

Compiled 2026-11-15, about 40 tool calls. Repo not edited. Not repeated here: what is already in `research_notes/Continuous harvest bioreactor progress/cultivated_meat_reactor_progress.md` (Ever After 10 kg/35 L, IntegriCulture, Cellular Agriculture Ltd) is only cross-checked.

**Tags.** MEAS = measured in a paper/application note. VEND = vendor claim. REV = review claim. INF = my inference or arithmetic. Access: FT = read in full, PART = read part, ABS = abstract/search-result summary only, SEC = secondary report or snippet.

**Conversion basis (INF).** Wet mass per cell: the model's 3,000 pg (Humbird; chicken 3.3 ng in `species_cell_parameters.md`). Vero and HEK cells are probably nearer 2 ng, so every mass figure below scales linearly: multiply by 0.67 for 2 ng. Specific O2 uptake 0.15 mmol O2/g wet/h (the model's value for 3,000 pg).

## Summary table

| Item | Fixed bed (iCELLis / scale-X) | Hollow fibre (Quantum / FiberCell) | Stirred tank (model) |
|---|---|---|---|
| Cells per cm2 of carrier, best measured | 4.9e5 (Vero, 200 m2, 6.9 d, FT, MEAS); 1.2e6 vendor FAQ max (SEC) | 1e5 (HEK293T, 2.1 m2, 4 d, PART, MEAS) | n/a |
| g wet cell per m2 carrier (3 ng) | 14.7 (INF) | 3.0 (INF) | n/a |
| g wet cell per L of bed/cartridge | 294 (INF) | 300 at vendor 1e8 cells/mL (VEND/INF) | 120-258 free |
| g wet cell per L of whole working vessel | about 110 (INF, iCELLis 500: 7.35 kg in 59-71 L) | about 13 for the Quantum circuit (INF); 100-300 for a bare cartridge only (VEND) | 120-258 |
| Output, kg wet/m3 working vessel/yr | about 3,000 (range 1,500-8,000) (INF) | about 1,000-3,000 system basis, very uncertain (INF) | about 16,000-22,000 by the module's own formula (INF) |
| Largest animal-cell run | 660 m2, 1.5e12 Vero cells (PART); scale-X nitro 600 m2/60 L offered (SEC) | 2.1 m2 Quantum; 1 L cartridge only a prototype proposal | 20 m3 design |
| Harvest | enzyme plus agitation, no iCELLis-specific recovery number found | enzyme flush, 90-95% expected (SEC, VEND) | continuous bleed |

## 1. Packed bed / fixed bed

### 1a. Density, area, volume

- **iCELLis 500 geometry.** 500 m2 of PET macrocarriers (11.2 cm2 each) in a 25 L doughnut-shaped bed; bioreactor working volume 59-71 L; bed height 10 cm at full size. VEND, FT. https://bioprocessintl.com/bioreactors/simpler-and-more-efficient-viral-vaccine-manufacturing (ATMI/Pall article, 2013). Cytiva product table lists the same (500 m2, 25 L, 10 cm). SEC. https://www.cytivalifesciences.com/products/items/icellis-single-use-fixed-bed-bioreactor-systems-p-36959
- **Bed sizes and heights.** Six sizes from 66 to 500 m2; surface is changed by bed height (2, 4, 10 cm) and compaction (low/high) inside one shell, so the cross-section is constant. Pall application note, FT. https://cdn.cytivalifesciences.com/api/public/content/sw5mVjp19EWGN_7Svqt77g-pdf
- **Bed volume of the 200 m2 run (INF).** 4 cm high bed, high compaction, so 200/500 x 25 L = 10 L. Cross-section 10 L / 4 cm = 2,500 cm2, the same as the 500 m2 bed (25 L / 10 cm), which is a consistency check.
- **Densities measured (Pall application note, FT, MEAS).** Vero, 200 m2 iCELLis 500, 4 cm high-compaction bed: **490,000 cells/cm2, 9.9e11 cells total, after 6.9 days**, seeded at 5,000 cells/cm2; global doubling time 1.04 d; growth slowed after about 100 h, when lactate reached 13 mM (the note suggests perfusion could keep the doubling time up). Total culture volume 500 L (recirculated batch).
- **Other measured values (Lesch/Europe PMC XML, read in full via https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3980293/fullTextXML, MEAS):** 660 m2 Vero 2.3e5 cells/cm2, 1.5e12 cells in 11 days; MDBK 3.3e5 at 500 (133 m2) scale; CEF 3.9e5. Reported cell counts per cm2 are the same order everywhere: 1e5-5e5.
- **Higher figures, not verified.** Pall FAQ snippet: HEK293 and Vero may reach up to 800,000 cells/cm2, and a retroviral vector study 1.18e6 cells/cm2 (SEC, ABS; the Pall FAQ page itself returned 404 on fetch). I treat 5e5 as the evidence-supported value and 1.2e6 as an upper case.
- **Volumetric density.** The vendor article gives 30-100e6 cells/mL (bed vs medium not stated; VEND, FT). INF: 200 cm2/mL of bed x 4.9e5 = 9.8e7 cells/mL of bed, inside that range.
- **Conversions (INF, 3 ng):**
  - per m2: 4.9e9 cells x 3 ng = **14.7 g/m2** (9.8 g/m2 at 2 ng).
  - per L of bed: 9.8e7/mL x 3 ng = **294 g/L bed**; cells then fill about 29% of the bed volume (3 pL each), so this is physically fine. At 1.2e6/cm2 cells would need 72% of bed volume, which is implausible for 3 pL cells; so the 1.2e6 value probably applies to smaller cells or is not typical.
  - 500 m2 unit at 4.9e5: 2.45e12 cells = 7.35 kg in 59-71 L working = **104-125 g/L of the whole unit** (central 113). The 200 m2 run: 2.97 kg in about 70 L = 42 g/L; counted over the full 500 L recirculation volume it is only 5.9 g/L.
- **scale-X (Univercells).** Brochure, FT: carbo 10 m2 in 1.8 L working volume; 30 m2 in 4.2 L; 30 m2 replaces 68 g microcarriers (4,400 cm2/g), 50 L stirred tank, 350 roller bottles. https://informaconnect.com/uploads/20190314-Univercells-scale-X-carbo-Brochure-v1-22a23947958f945ea2279923e4dce7e3.pdf . Nitro 600 m2 in a 60 L bioreactor (search snippet only, SEC); the brochure shows the family 2.4 / 10 / 30 / 200 / 600 m2. No Univercells cells/cm2 found. INF at 14.7 g/m2: carbo 10 = 82 g/L, carbo 30 = 105 g/L, nitro 600 = 147 g/L of working volume. These are conversions with the iCELLis density, not measurements.
- **Corning Ascent** (stacked PET mesh discs): ~96% harvest efficiency and ~98% viability reported in a preprint (ABS/SEC); no densities read. The PDF (corning.com) returned 403.

### 1b. Oxygen, gradient, CO2, pH

- **Oxygen route (FT, Pall).** Bubble-free: medium falls as a thin film down the bed wall; the film height (0-10 cm) sets kLa. No external aeration loop. A numeric kLa for the 500 was not found (the Catalent page "Comparison kLa of iCELLis Nano and 500" exists but I did not read it). pH by CO2 in the gas overlay and 1 N NaOH; DO measured before and after the bed and kept above 70% air saturation by air plus O2 overlay.
- **Flow through the bed.** Linear speed 2 cm/s at inoculation, 1 cm/s in culture, kept constant on scale-up (FT, Pall). Impeller speed for 1 cm/s: 220 rpm at 200 m2. Recirculation (medium loop) 240-450 mL/min at 200 m2.
- **Gradient (MEAS, FT).** Cell count top vs bottom of the bed: 16% variability vertically at 500 scale, 28% at nano; horizontal 10-17%. This is cell distribution, not an oxygen profile. Pall states bed height and compaction maxima were chosen experimentally to limit gradients. A 2025 study (insights.bio, ABS) says falling-film height became the main DO lever at 50 m2.
- **Maximum oxygen delivery (INF, my calculation, not found in a source).** Bed cross-section 2,500 cm2 x 1 cm/s = 150 L/min through the bed. If the pre-bed to post-bed DO drop may be 30% of air saturation (the Pall >70% rule), air-saturated medium (0.21 mM at 37 C) loses 0.063 mM per pass, so the bed can deliver about 23 mmol O2/L of bed/h at 1 cm/s, equal to about 9 mmol/L of the 65 L working volume/h. With the overlay enriched with O2 (several times the air-saturation concentration) and 2 cm/s, I estimate 30-70 mmol/L working/h is possible on paper. Demand at 113 g/L x 0.15 = 17 mmol/L working/h (44 mmol/L of bed/h). So oxygen is feasible with enrichment but is flow-limited; it rises with linear speed, which is capped by shear and by bed uniformity. Confidence in the order of magnitude: moderate; the shear cap on speed is not quantified in what I read.
- **CO2.** Stripping by the falling film into the overlay gas (VEND, qualitative). No CO2 numbers found. In food-cell mass at 7 kg per unit, CO2 production is about the same per gram as in the stirred tank, with the same film for removal, so pH is likely controllable but no data.

### 1c. Harvest

- **Enzyme detachment is the weak point.** A US patent on fixed-bed detachment states trypsin alone often gives only limited detachment because dense packing hampers distribution through the bed (US10781417, SEC, https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10781417). The remedy proposed is agitation or vibration plus liquid-level cycling. The Pall note says nothing about harvest. I found **no published iCELLis or scale-X harvest recovery percentage** (searched: "iCELLis harvest recovery TrypLE", "fixed bed harvest efficiency"). Comparators: Pall Xpansion about 7% of cells remained after the first harvest (SEC); 96% for the Corning mesh preprint (SEC); microcarrier harvest 88-98% (Thermo Harvestainer notes, SEC).
- **Not continuous.** A fixed bed has no bleed of product cells. Cells are harvested once per run after stopping the culture; the bed is then discarded (single-use) or re-packed. Releasing cells into a bleed would require partial in-situ detachment that nobody has shown (P(shown at pilot scale by 2028) < 10%, my estimate). Cell loss to effluent during perfusion is not reported.
- **Two harvest types.** (i) Detached cells (enzyme, buffer wash, per the above, plus a harvest tank and a separation from carriers). (ii) Whole bed as product: IntegriCulture harvests "cell paste along with the scaffold" (gelatin-based, food-grade) from its custom packed bed (bioRxiv 2026-01-08, FT, read via PDF text: https://www.biorxiv.org/content/10.64898/2026.01.08.698307v1.full.pdf). Ever After Foods uses an "edible packed bed" in which cells stay on edible scaffold, but cells for seeding it come off non-edible carriers by patented vibration (agfundernews/foodnavigator, SEC). In (ii) detachment disappears but the scaffold mass becomes part of the product and the bed cannot be reused.

### 1d. Scale, maturity, cultivated-meat data

- Largest animal-cell fixed-bed runs: iCELLis 500 at 200 m2 (9.9e11 cells) and a 660 m2 prototype (1.5e12 cells) (MEAS, FT). Catalogue top size 500 m2 (iCELLis 500+) and 600 m2 (scale-X nitro). Pall quotes 500 m2 as the largest fixed bed (SEC). Scale-up is by **bed diameter at constant height, then by number of units**; height is capped (10 cm) for gradient reasons. A larger industrial unit than 500-660 m2 has not been shown.
- Maturity: commercial for viral vaccines and vectors (hundreds of m2). For food cells: **none** at scale.
- Cultivated meat: IntegriCulture, seven runs in 2025, 3.6e9 cells per batch (about 11 g wet at 3 ng, INF), cell yield plateaued at 2.88-fold, 21.1% of the theoretical 13.65-fold; no bed volume given (not found) (FT of the preprint text). Ever After Foods: claims 10 kg in 35 L, later "10 kg per 25 L", a 1,400 L unit for 400 kg, and "over 40 per cent cultivated meat per litre" (company CEO claims via https://agfundernews.com/ever-after-foods-addresses-critical-scaling-challenge-in-cultivated-meat, https://www.foodnavigator-usa.com/Article/2025/04/01/ever-after-foods-and-buhler-aim-to-lower-cultivated-meat-costs/; SEC). INF: 10 kg/35 L = 286 g/L; 10 kg/25 L = 400 g/L; 400 kg/1,400 L = 286 g/L. These count cells **plus edible scaffold**, no run time is given, and no independent data exist. Mission Barns uses an undisclosed adherent reactor (SEC from repo note). The 90 million cells/mL figure attributed to Ever After rests on a single article (ABS).

### 1e. Capital, consumables, mode

- **Capital per m3 or per m2:** not found for iCELLis or scale-X (searched: "iCELLis 500 price", cost modelling). The insights.bio cost model (Pall-authored, 2019) reports cost per dose $21k at 200 L, $10k at 800 L (iCELLis), 25% below multi-trays, with media 2.4 L/m2 at $90/L and 19 days per run; capital and consumable per run only in figures (not read). https://www.insights.bio/cell-and-gene-therapy-insights/journal/article/15/cost-modelling-comparison-of-adherent-multitrays-with-suspension-and-fixedbed-bioreactors-for-the-manufacturing-of-gene-therapy-products (PART, VEND-funded).
- **Consumable per run (INF).** Each run uses a new single-use bed (500 m2 PET) plus bag. No price found. Reasoning: even at $10,000 per bed-run (my guess for order of magnitude, P(order $5k-50k) about 80%, unsourced), 7.35 kg gives $1,360/kg of cells. To keep carrier cost under $5/kg at the iCELLis 500 density, the bed would have to cost under about $35 per run, which is not a vaccine-grade single-use bag. So the fixed-bed route only has a chance with a cheap or edible/consumed carrier.
- **Runs per year (INF).** 6.9 d culture (Vero, batch) + about 3 d for bed set-up, equilibration, harvest and cleaning = about 10 d, so about 33-35 runs per year per unit at 90% uptime; seed train needs 1 TF150, 2 TF300, 9 MT10 for one 200 m2 run, but at 5,000 cells/cm2 and a 17-fold concentration factor at seeding the seed train is shorter than for a stirred tank (FT).
- **Mode.** The vendor says the bioreactor can run perfusion or recirculated batch; the 200 m2 case was recirculated batch with a 500 L loop (2.5 L/m2). INF medium use: 500 L / 2.97 kg = **168 L per kg** wet cells (5% FBS DMEM, glucose-limited, not optimised). Cellular Agriculture Ltd's hollow-fibre model claims 140 L/kg (repo note, SEC), so the two are similar. Fed-batch in the strict sense is not described; recirculated batch is the practical equivalent. Perfusion is "natural" because cells are held.

### 1f. Food-cell operating limits

- Contamination: single-use, gamma-sterilised, aseptic connections (C-flex welds), so sterilisation in place is not a feature; reuse/cleaning not demonstrated. Open-sampling of carriers is done non-sterile at the end only. Labour: seeding 2 operators under a hood < 1 h (FT).
- Detachment losses during culture: not found. Cell-number consistency: nano and 500 gave similar density (FT).
- Limits for meat cells: growth plateau came from lactate at 13 mM (batch); Vero is a line with 1 d doubling. Food cells with slower doubling (IntegriCulture 36.8 h; many cell lines longer) would lengthen runs and lower runs/yr.

### 1g. Output estimate, fixed bed

Chain (INF): 113 g/L working (4.9e5/cm2, 3 ng) x 90% harvest recovery (assumed, no source) x 35 runs = **3.6 t/m3 working/yr**. At 2 ng 2.4 t; at the upper-case 1.2e6/cm2 and 3 ng about 8 t. Central **about 3 t/m3/yr (1.5-8)**. Per unit (500 m2): about 230 kg/yr, so **1,000 t/yr needs about 4,300 units** (scale by number of units; 10 cm height cap). The module's stirred-tank formula (wv x X x mu x 8,760 x uptime) at X = 120 g/L, mu = 0.029/h, wv = 0.8, uptime 0.9 gives about 22 t/m3/yr; so the fixed bed is roughly 6-7 times lower per m3 of working volume before any carrier cost. P(fixed bed output per m3 working >= half the stirred tank's) < 5%. This ignores the 500 L external loop; counted over the loop the fixed-bed number falls by another factor of several.

Edible-bed case (Ever After): 286 g/L cells-plus-scaffold; run time not found. If 14-21 days incl. turnaround (assumed), 15-20 runs/yr gives roughly 4-6 t/m3/yr of product mass, of which the scaffold share is unknown; P(independently confirmed cell-only wet density > 200 g/L) about 10%.

## 2. Hollow fibre

### 2a. Density, area, volume

- **Quantum (Terumo)**: 11,520 fibres, 2.1 m2 intracapillary (IC) surface, 124 mL IC fibre volume (ABS/SEC from Keele and PMC snippets), IC circuit 175 mL and EC circuit 305 mL (SEC, one Terumo paper), 189 mL IC in another source. HEK293T run: **2.14e9 +/- 0.18e9 viable cells from 2.5e8 seeded in about 100 h, 9.5e4-1.1e5 cells/cm2, seeding efficiency 90%, viability > 96%** (read via Europe PMC XML, PART/MEAS; paper "An optimized HEK293T cell expansion protocol using a hollow-fiber bioreactor system", PMC10504471). Compartment volumes were not stated in that paper.
- **Conversions (INF, 3 ng):** 2.14e9 cells = 6.4 g (4.3 g at 2 ng). Per m2: 3.1 g/m2 (one fifth of iCELLis's per m2; the iCELLis Vero density is 5 times higher per cm2). Per L of the Quantum circuit (IC + EC about 0.48 L): **about 13 g/L** (9 g/L at 2 ng); per L of IC fibre lumen (124 mL): 52 g/L.
- **FiberCell / classic hollow fibre (VEND, SEC).** 150-200 cm2 of area per mL of cartridge; cell densities of 1-2e8 cells/mL; the C2011 cartridge has 4,000 cm2 in under 20 mL; C2018 1.2 m2 in 60 mL (search-result summaries of FiberCell marketing). A review/vendor article (Biopharm International, read in full: https://www.biopharminternational.com/potential-application-hollow-fiber-bioreactors-large-scale-production) says "cell densities of 1-2e8 or more" are achieved, 100-200 cm2/mL, and proposes a **1 L cartridge supporting as many cells as a 100 L stirred tank** (claim, never run at that scale; the article itself says use has been limited to laboratory scale). INF at 1e8 cells/mL x 3 ng: 300 g/L cartridge; the cells would occupy 30% of cartridge volume. A model study cited in a search snippet put the Ehrlich ascites cell density at 1.1e8/mL of ECS, 7e7/mL for the whole reactor (ABS).
- **Whole-system basis.** The cartridge is not the whole vessel: the oxygenator, reservoir, pump and tubing add volume; I could not find a figure. Only the Quantum circuit (0.48 L) is quantified above. I take the system volume as 2-5 times the cartridge (INF, a guess).
- **Tissue in a hollow-fibre array (cultivated chicken).** University of Tokyo, Trends in Biotechnology (search summaries, SEC): 1,125 fibres in a 7.00 x 4.05 x 2.25 cm unit gave about 10 g of chicken muscle tissue. INF: 63.8 mL device, 157 g/L of device, tissue left in place as the product, centimetre scale, no continuous output. https://www.foodingredientsfirst.com/news/study-examines-scalable-tissue-biofabrication-via-perfusable-hollow-fibers-for-cultured-meat.html

### 2b. Oxygen

- Gas exchange through the fibre wall: medium or gas flows in the lumen (or a separate oxygenator in the loop; Quantum uses an integrated gas-transfer module circulating EC fluid, FT of the HEK293T paper, 5 mL/min IC and 100 mL/min EC flows). The limit is the **axial oxygen gradient along the fibre**: oxygen falls downstream, so fibre length and cell density are linked; Piret and Cooney (1991) and Drury et al. (1988) are the standard model papers (ABS only, values not read). A patent (SEC) says scale-up of hollow fibres is limited by how far the fibre can be lengthened before oxygen becomes limiting.
- INF: at 1e8 cells/mL (300 g/L) uptake would be 45 mmol O2/L cartridge/h at 0.15 mmol/g/h; air-saturated medium carries only about 0.2 mM, so even full extraction would need about 220 L of medium per L of cartridge per hour (INF); in practice this is why the Biopharm article cites 5-10 L/min gravity pumps and 50-100 L/day medium for one 1 L cartridge (read in full). No oxygen-transfer figure per L is given in that article. Maximum OUR per litre achievable: **not found**.
- CO2/pH: by the gas-transfer module (5% CO2 mixes) in Quantum (FT); no data for large units.

### 2c. Harvest

- Quantum: IC wash-out with trypsin, vendor says 90-95% recovery expected (SEC; search snippet of Terumo statement, not a measured value) and harvest in as little as 20 minutes (Terumo RUO, SEC); HEK293T viability > 96%.
- Classic ECS-loaded cartridges (FiberCell): cells are not removed; the products are what is harvested (Biopharm article, FT). **The Biopharm article gives no cell-harvest numbers**, and a FEASTS deliverable (SEC) notes that fibre material complicates cell harvest. No continuous cell bleed has been demonstrated. Two forms: detaching cells from the lumen (as Quantum) or taking the whole cartridge/tissue (Tokyo). For food, a hollow-fibre-grown tissue block is the second form.

### 2d. Scale and maturity

- Quantum 2.1 m2 (2.14e9 cells) is the commercial benchmark; the Biopharm article's 1 L prototype is the largest design mentioned. Cellular Agriculture Ltd: Corsham pilot site, "world's longest hollow fibre bioreactor" (2024), claims 200x smaller and 70% cheaper to run (company statements); no volumes, densities or yields published (searched: company news, Campden BRI, Innovate UK; SEC). An RAU report cites its TEA at 140 L/kg medium (repo note).
- Scale-up is by number of cartridges and by fibre length (limited by oxygen). Maturity: good for antibodies and small cell-therapy doses; none for kilogram cell mass.

### 2e. Capital, consumables

- Quantum system: a reseller lists about EUR 25,316 and a used Quantum Flex about $23k (SEC; only the instrument; disposable set prices not found). Hollow-fibre membrane price "USD 40-200/m2", 5-year life (Eng. Proc. 2023, quoted from `gas_exchange_study.md`, SEC), so the membrane in a Quantum fibre bundle is only $84-420; the cartridge price is mostly other things (housing, set). Capital per m3: not found.
- Runs per year (INF): about 7 doublings from seed to 1e8 cells/mL at 24 h doubling = 7 d, plus 2 d lag and 2 d for harvest, clean and set-up = 11 d, so about 28-30 runs/yr. The cartridges are single-use (Quantum) or long-life (FiberCell, months), in which case cells are not harvested at all.
- Mode: inherently perfusion. Batch is not sensible because of the dense ECS; fed-batch is used for the Quantum expansion only as short expansion.

### 2f. Food-cell limits

- Contamination: like the fixed bed (single-use sets). Long run of months for product-secreting lines is a classic benefit but is irrelevant for cell mass. Necrotic cells form inside packed ECS at high density (Biopharm article, FT), with no measure of what share is viable when the whole cartridge is harvested; large inter-fibre gaps caused necrotic zones. Labour: automated for Quantum.

### 2g. Output estimate, hollow fibre

INF chain for a bare cartridge: 150-300 g/L cartridge (1-2e8 cells/mL vendor, partial occupancy) x 0.9 recovery x 28 runs = 3.8-7.6 t/m3 cartridge/yr. On a system basis (cartridge 20-50% of system volume) **about 1-3 t/m3/yr**; Quantum as measured (13 g/L of the circuit x 0.9 x about 30 runs of 4-7 d, if one counted 50 runs/yr, 0.6 t/m3/yr at 50 runs) is about 0.4-0.6 t/m3/yr. Central estimate **about 1 t/m3/yr, range 0.3-3**, i.e. 10-20 times below the stirred tank by the module's formula. P(a >100 L hollow-fibre cultivated-meat unit with published density and yield by 2028) about 15%. P(>80% of cells recovered from a dense cartridge at scale without damage) about 25%. P(hollow fibre beats the stirred tank on cost per kg of wet cell) < 5%, because cells per litre are not higher once the loop is counted and a continuous bleed is not possible.

## 3. Judgement summary (my probabilities)

| Judgement | Probability |
|---|---|
| iCELLis-type fixed bed delivers > 100 g/L of the whole working volume at 500 m2 (at 3 ng/cell) | 60% |
| Output per m3 working of fixed bed is within a factor of 2 of the stirred tank | < 5% |
| Fixed bed cost per kg beats the stirred tank with a disposable PET bed | < 5% |
| An edible/consumed scaffold packed bed gives > 200 g/L of cell mass (not scaffold) independently confirmed within 3 years | about 10% |
| Edible-scaffold packed bed beats the stirred tank on cost per kg (if its density claim holds, 286-400 g/L) | about 20% |
| Hollow fibre yields > 1 t/m3 system/yr in practice | about 35% |
| Either support type permits harvest as a continuous bleed | < 10% |

## 4. Not found

- iCELLis 500 or scale-X kLa; maximum OUR per litre in any source (my calculation above is INF).
- iCELLis/scale-X harvest recovery percentage; detachment losses during culture.
- Price of an iCELLis 500 bed/bag, of a Quantum disposable set, of any hollow-fibre cartridge; capital per m3 or m2 for any of them. Searched: price, "cost per run", "capital cost", BioSolve-based cost models (numbers only in figures).
- Bed volume of the IntegriCulture packed bed; run duration of Ever After's runs; any independent Ever After data.
- Cellular Agriculture Ltd cell density, volume, yield.
- Pages not readable: Pall FAQ (404), PMC (anti-bot page), Corning application paper (403), authorea preprint (403); Catalent kLa page not fetched.

## 5. Sources (URL, access)

1. Pall application note, iCELLis linear scalability 1.6 to 200 m2 (Vero), https://cdn.cytivalifesciences.com/api/public/content/sw5mVjp19EWGN_7Svqt77g-pdf, FT.
2. Bioprocess International / ATMI, "Simpler and More Efficient Viral Vaccine Manufacturing" (2013), https://bioprocessintl.com/bioreactors/simpler-and-more-efficient-viral-vaccine-manufacturing, FT (vendor).
3. Lesch et al., linear scalability of virus production in iCELLis (PMC3980293), via Europe PMC XML, https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3980293/fullTextXML, FT (summarised by the fetch tool).
4. Univercells scale-X carbo brochure, https://informaconnect.com/uploads/20190314-Univercells-scale-X-carbo-Brochure-v1-22a23947958f945ea2279923e4dce7e3.pdf, FT. Nitro 600 m2/60 L from https://www.pharmaceuticalprocessingworld.com/ (search snippet), SEC.
5. Pall FAQ numbers (up to 800,000 and 1.18e6 cells/cm2, 500 cells/cm2 seeding) via search summary only, https://www.pall.com/en/biotech/faq/faq-cell-culture.html, SEC (page 404 on fetch).
6. Cytiva iCELLis product page (500 m2, 25 L), https://www.cytivalifesciences.com/products/items/icellis-single-use-fixed-bed-bioreactor-systems-p-36959, SEC.
7. IntegriCulture packed bed preprint, https://www.biorxiv.org/content/10.64898/2026.01.08.698307v1.full.pdf, PART (PDF text read for the packed-bed sections).
8. Ever After Foods, https://agfundernews.com/ever-after-foods-addresses-critical-scaling-challenge-in-cultivated-meat and https://www.foodnavigator-usa.com/Article/2025/04/01/ever-after-foods-and-buhler-aim-to-lower-cultivated-meat-costs/, SEC (company claims).
9. Cost modelling of adherent multitray, suspension and fixed bed, Cell & Gene Therapy Insights 2019, URL in section 1e, PART.
10. US patent 10781417 on fixed-bed detachment, https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10781417, SEC.
11. HEK293T Quantum protocol (PMC10504471), https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10504471/fullTextXML, PART/FT of the extraction.
12. Quantum volumes and 90-95% recovery claim: search results on https://pmc.ncbi.nlm.nih.gov/articles/PMC6686483 and Terumo pages, SEC.
13. Biopharm International, "Potential Application of Hollow Fiber Bioreactors to Large-Scale Production", https://www.biopharminternational.com/potential-application-hollow-fiber-bioreactors-large-scale-production, FT.
14. FiberCell cartridge specs via GEN and BioBuzz, e.g. https://www.genengnews.com/insights/hollow-fibers-enhance-protein-expression/, SEC (vendor).
15. Cellular Agriculture Ltd, https://vegconomist.com/company-news/cellular-agriculture-ltd-strengthens-industry-position-new-facility-breakthrough-bioreactor-systems/ and https://www.foodanddrinktechnology.com/news/51223/, SEC (company claims).
16. University of Tokyo hollow-fibre chicken tissue, https://www.foodingredientsfirst.com/news/study-examines-scalable-tissue-biofabrication-via-perfusable-hollow-fibers-for-cultured-meat.html, SEC.
17. Piret and Cooney 1991 and Drury et al. 1988 on hollow-fibre oxygen limits, via search results (zendy.io), ABS.
