# Research A: airlift, bubble column, rocking bag and single-use stirred tank, against the 20 m3 stirred tank (STR)

Date: 2026-11-15. About 45 tool calls. The repo was not edited.

Labels used for every number:
- **M** = measured in a document I read.
- **V** = vendor claim.
- **R** = review-article claim.
- **MODEL** = a published model or techno-economic analysis (TEA).
- **INF** = my own inference or arithmetic (assumptions stated).
- **Animal** or **Non-animal** is marked on every volume record.

Access levels: FULL (read in full text via pdftotext or the page), PART (read part), ABS (abstract only), SEC (secondary, i.e. a search-engine summary of the page; I did not see the page).

I did not repeat what is already in `gas_flow_cap.md`, `gas_exchange_study.md` and the three `Continuous harvest...` notes. Where those notes already hold a number I say "already in repo".

---

## 0. Bottom line (probabilities are my judgement)

| Question | Answer | Prob. |
|---|---|---|
| Airlift holds 100 g/L wet of meat cells at 20 m3 or more, shown in operation, by 2030 | Not shown at any scale. Largest animal-cell airlift with a published run is about 2 m3 (Lonza, low density). | 7% |
| Airlift could hold 100 g/L at about 260 m3 in principle (O2, CO2, shear, foam all manageable, with O2-enriched gas and shear protectant) | Hubbard's CFD says O2 is "likely viable with small modifications". Nobody has modelled CO2 or foam. | 30% |
| In an airlift at 100 g/L, CO2 binds before O2 does | The CO2 check needs 10-14 mm/s, which is at the usual practical ceiling, so CO2 and foam bind first. With air, O2 is also marginal (section 1a). | 70% |
| A plain bubble column does better than an airlift for 100+ g/L cells | No. Same gas-per-litre and shear physics, worse mixing, no animal-cell record beyond bench. | 90% that it is no better |
| A rocking bag of 500 L (or a 5,000 L single-use stirred tank) is a route to a cheap kilogram | No, because of the bag consumable alone. At an assumed $5-30 per litre per run, the bag is $20-250 per kg of wet cells (section 5). | 95% no, at today's bag prices |

---

## 1. Airlift and external-loop airlift

### 1a. Oxygen transfer

| Item | Value | Label | Source and access |
|---|---|---|---|
| Correlation Negulescu used for an airlift | kLa = 0.32 us^0.7 (s^-1, us in m/s; the exponent on power is zero) | MODEL | Hubbard 2024, https://engrxiv.org/preprint/download/3788/6856, FULL. It states Negulescu's constants were A=0.32, alpha=0, beta=0.7 for airlifts, against A=0.002, 0.7, 0.2 for stirred tanks. |
| OTR Negulescu claims for the 262 m3 airlift | 13.5 mmol/L/h, against a need of 10.3 | MODEL | Negulescu 2023 preprint, https://engrxiv.org/preprint/download/2414/4659/3571, FULL (lines 268-271) |
| Same correlation evaluated by me | us = 6 mm/s gives kLa 32 /h, OTR about 6.7; 10 mm/s gives 46 /h, about 9.6; 14 mm/s gives 58 /h, about 12; 15.8 mm/s gives 63 /h, about 13 mmol/L/h | INF | Assumes air, C* = 0.2 mmol/L at 1 bar and 37 C, 1.5 bar mean pressure, dissolved O2 at 30% of saturation. This agrees with Negulescu's 13.5, so the 13.5 comes from about 14-16 mm/s in air. |
| Humbird's STR cap | 29 mmol/L/h at 6 mm/s and 43 W/m3 | given in the brief | Not re-checked. |
| Any measured OTR for an animal-cell airlift above 1 m3 | **Not found.** Searched: "airlift animal cell kLa hybridoma", "Celltech/Lonza airlift kLa", Chisti and Varley and Birch abstracts. Full texts of Birch and Arathoon 1990 and Varley and Birch 1999 were not retrievable. | | |
| Chisti-era figure "0.6-1.0 mmol/L/h in airlift devices" | A search summary of a Scribd copy of Chisti 1987. It is a low-density-cell regime figure, not a capacity. | SEC | https://www.scribd.com/document/403318966/1-chisti1987-pdf, SEC. Do not use it. |
| Coarse-bubble regime in the Quorn airlift | 1 cm coarse bubbles in a central plume; "only about 1%" of the transferable O2 dissolves by the top of a 50 m column; the culture is "oxygen starved in general". This is a mathematical-physics group's calculation (Zimmerman and co-workers), not a plant measurement. | MODEL, non-animal | Sheffield paper, https://eprints.whiterose.ac.uk/id/eprint/232799/1/1-s2.0-S0960308524000646-main.pdf, PART (intro read by pdftotext). Note it gives 3 x 50 m tall, about 225 m3 vessels, against 155 m3 elsewhere. |
| Yeast bubble columns | Practical OTR limit 150 mol O2/m3/h (= 150 mmol/L/h) "before excessive foaming or jet flooding"; 200 m3 columns; Humbird models 6 x 200 m3 at $818k each | MODEL, non-animal | Humbird report, https://engrxiv.org/preprint/download/1438/2973/2173, FULL (appendix; line 5306). Yeast broths are not animal-cell medium. |

**What limits OTR in an animal-cell airlift.** The limits are (i) the usual ceiling of 10-15 mm/s on gas velocity (already in repo, snippet), (ii) foam and antifoam (repo section 2 of `gas_flow_cap.md`; I found no airlift-specific foam data), and (iii) in tall loops, depletion of O2 in the unsparged downcomer (Humbird: "O2 depletion in the ungassed downcomer can become prohibitive" at large scale, FULL; see 1c).

**Judgement (INF).** On air, an airlift at its usual gas velocity gives about 7-13 mmol/L/h, which is 25-45% of Humbird's 29 for a stirred tank, and below the 15-18 mmol/L/h the model cell needs at 100 g/L (the repo note section 3 already shows this: 14.9 needed, 13.5 supplied). Oxygen-enriched gas can lift this by a factor of up to about 4.8 (pure O2 against air), but gas flow is then set by CO2, not O2.

### 1b. CO2 removal, and the depth penalty

Arithmetic (INF, from the model's own relation: gas per litre = us / depth):
- The model's 20 m3 STR has D = 2.52 m and depth 4.02 m, so 6 mm/s is 0.089 vvm.
- A 10.5 m deep airlift (the repo's scaling of Li et al.'s 13.75 m, 300 m3 design) needs **15.8 mm/s** for the same 0.089 vvm.
- It reaches only 0.057 vvm at 10 mm/s and 0.086 vvm at 15 mm/s.
- A 20 m deep column (Quorn-like height) needs 30 mm/s for the same gas per litre.

So **the depth penalty is real: a tall column is worse for CO2 at a given superficial velocity** (CO2-limited density is proportional to us/depth). An airlift only catches up with a squat STR if it runs at 15 mm/s or more, which is at or above the usual practical maximum.

Offsets (INF):
- The bubble contact time is longer in a tall column (about 40 s over 10 m, against about 16 s over 4 m at 0.25 m/s rise velocity). The model's strip efficiency of 0.96 is therefore, if anything, conservative for a tall column.
- Bubble-burst death per litre per hour is also proportional to us/depth in the model (`gas_flow_cap.md`). So the same gas per litre in a tall column costs the same deaths per litre, at a higher velocity.
- The gas power is rho g us = 59 W/m3 at 6 mm/s, 98 at 10 mm/s and 137 at 14 mm/s. This is 2-3 times the STR's 43 W/m3 impeller power. It is all delivered through bubbles. Whether this matters for cells is unknown.

**Check of the model's Negulescu 2023 treatment (`airlift_check`): I found nothing that contradicts it, and four small points.**
1. Depth scaling from Li et al. (13.75 m at 300 m3, proportional to the cube root) is an assumption. Negulescu gives no dimensions (confirmed: I grepped the full preprint text; there is no height or diameter). A taller, thinner loop would make the CO2 check worse; Quorn's loops are 30-50 m.
2. The check uses vessel-average us and per-litre gas. In an airlift the gas goes only through the riser at about 2x the average velocity, but gas per litre is what the CO2 balance needs, so this is fine.
3. CO2 build-up in the unsparged downcomer is small. About 18 mmol/L/h x 60 s of transit is 0.3 mmol/L, which is about 10 mbar at 0.03 mmol/L/mbar. That is about a tenth of the 100 mbar limit (INF; Henry constant from memory).
4. The check uses Negulescu's own oxygen-uptake figure, and Humbird and Hubbard both say that class of figure is low. The repo already handles this with the "model cell" column.

The reference to 10-15 mm/s as the usual maximum rests on a thesis snippet (https://core.ac.uk/download/323206707.pdf; the fetch returned HTTP 403, so SEC only). I did not verify it. A second search summary of the same thesis says "airlift superficial velocities of 0.01-0.015 m/s are typical in large industrial airlifts" (SEC); that is not an animal-cell limit.

### 1c. Mixing, shear, and can it hold 100+ g/L

- **Mixing and circulation.** Li et al. 2020 (via Humbird footnote 54, FULL): a 20 s downcomer transit; 46% (3.2 mg/L) dissolved O2 at the top of the riser, about half used in the downcomer; their uptake was half the authors' own reference, so O2 would run out. Hubbard (FULL) re-simulated with a lattice-Boltzmann CFD (2 mm bubbles): at Li's density (770 g/L wet) "large areas of no oxygen consumption"; at Negulescu's 100 g/L "small regions of limited uptake", so "reasonable to expect that small changes in geometry and/or operating conditions would enable this cell density". Hubbard says 1.5 mm bubbles might double the viable yield (extrapolated from a 20 m3 STR run). Hubbard does not treat CO2, foam, or shear damage (checked in the full text: CO2 only in the discussion as a possible extension).
- **Measured mixing times for an animal-cell airlift:** not found. For comparison, the single-use XDR-2000 stirred tank (Cytiva note, FULL, https://cdn.cytivalifesciences.com/api/public/content/digi-18410-pdf) had tm95 up to 199 s at 2000 L and 25 rpm; its longest and shortest probe positions differed by 37 s on average.
- **Shear and bubble damage.** The consensus is that bubble-burst and bubble-collapse damage is real and impeller shear is overstated (Humbird, FULL; Chisti 2000 review, ABS only: https://acnpsearch.tweb-dev.unibo.it/singlejournalindex/75846935). Chisti's 2001 review says bubble columns and airlifts are the commonest gas-agitated vessels for animal cells (SEC). Damage figures are already in `gas_flow_cap.md` section 1.
- **Can an airlift or bubble column hold 100+ g/L of cells?**
  - Viscosity is not the obstacle (INF). A rigid-sphere suspension (Krieger-Dougherty, maximum packing 0.64) has relative viscosity of 1.3 at 10% volume fraction (about 100 g/L wet), 1.8 at 20% and 2.2 at 25%. The real figure for deformable cells is not found. The 500 L Wave CHO run reached 1.5-3 x 10^7 cells/mL (about 45-90 g/L wet at 3 ng/cell, INF) with oxygenation "not an issue", but the limits at 3 x 10^7 were nutrients and lactate, not viscosity (Pierce and Shabram 2004, FULL, https://bioprocessingjournal.com/afp/J34-Pierce.pdf). The 4 L perfusion bag at 214 million cells/mL already in repo (Clincke 2013) had viscosity listed among its limits.
  - **The density at which gas holdup collapses: not found for animal cells.** Searched: "gas holdup cell suspension animal cell airlift", viscosity searches. My judgement is that holdup collapse is not the issue below 25% volume fraction. The issue is bubble coalescence and foam. Cell-laden, protein-rich medium foams and antifoam hurts both O2 transfer and cells (already in repo).
  - Probability that an airlift physically sustains 100 g/L wet in a cultivated-meat cell culture at 20 m3 or more: 30% in principle (see section 0).

### 1d. Largest volumes

| Record | Volume | Animal or not | Label and source |
|---|---|---|---|
| Celltech/Lonza airlifts, hybridoma/CHO/myeloma, batch, low density | 100-2,000 L | Animal | FULL: Chimia 51 (1997) 290-291, https://chimia.ch/chimia/article/download/1997_290/2172/12827. It cites Birch and Arathoon 1990 for it. |
| Celltech 1,000 L production airlifts; a 10,000 L "designed" | 1,000 L operated | Animal | Already in repo (Lambert 1987, jstage). |
| "Up to 10 m3, though 1-2 m3 are more common" for animal cells | 10 m3 | Animal | R (Humbird, FULL, citing Stanbury). No primary source found: I could not retrieve the Birch papers. |
| Ark Biotech airlift, unnamed cultivated-meat partner, late 2023 | 1,250 L | Animal (cultivated meat) | CO via AgFunderNews and Green Queen, already in repo; confirmed again by a SEC search summary. No density, no duration, no publication. Ark claims designs up to 1,000 m3 and a bioreactor "90% cheaper" (company claims). |
| GOOD Meat and ABEC | 250,000 L x 10 announced (2022); a 6,000 L ABEC unit in Singapore | Animal | SEC (Green Queen). Announced only. No evidence they were airlifts. |
| Other cultivated-meat airlifts (Aleph, UPSIDE, Wildtype, Vow, Mosa) | **Not found** | | Searched by company with "airlift". GFI's survey says some respondents use airlift (already in repo). |
| Quorn airlifts (pressure-cycle, external loop), continuous | 155 m3 (some sources 225 m3); vessels above 30 m tall in towers over 40 m; the first, Quorn 1, was 40 m3, about 30 m tall | **Non-animal** (fungus) | Frontiers Sust. Food Syst. 2023, https://www.frontiersin.org/articles/10.3389/fsufs.2023.1204307/full, PART via fetch summary: 155 m3, biomass 10-15 g/L wet basis, about 1,000 h continuous, about 2 t/h, 304 stainless. Heights from the Moore guidebook (SEC) and the Sheffield paper (PART). |
| ICI Pruteen pressure-cycle airlift, 1979 | 1,500 m3 | **Non-animal** (bacteria) | R (Humbird, FULL): foaming and sterility control redesigned in 1980, decommissioned by 1987. |
| Baker's yeast bubble columns | about 200 m3 | **Non-animal** | R/MODEL (Humbird, FULL). |

**What the non-animal records prove (INF).** They prove that a 150-1,500 m3 gas-lift loop can be built, kept sterile for weeks and operated continuously. They do not prove anything about cell tolerance of bubbles, CO2 at 100 g/L, or foam with protein medium. Quorn's cell mass is 10-15 g/L wet, an order lower than the 100+ g/L we need, and its air is coarse-bubbled at 1 cm.

### 1e. Capital per m3 against a stirred tank

| Item | Value | Label | Source and access |
|---|---|---|---|
| Negulescu STR price basis | $300,000 for 20 m3 food-industry tank, scaled with exponent 0.6 | MODEL | Negulescu preprint FULL (Maroulis and Saravacos 2008) |
| Negulescu airlift price basis | $174,300 listed for a 190 m3 airlift in a Sulzer Chemtech paper (Zuber 1997), scaled with 0.6 | MODEL | Negulescu preprint FULL. I did not read Zuber 1997; I do not know what the airlift was (probably non-aseptic). |
| Ratio inside Negulescu's own pricing, at 262 m3 | Airlift $0.21 M = $0.8k/m3; STR scaled the same way $1.40 M = $5.4k/m3 | INF (arithmetic) | **Airlift:STR = 0.15** in their model, and both bare-vessel prices are 1-2 orders of magnitude below Humbird's $611k/m3 (an installed, aseptic, cell-culture price). So Negulescu's ALR advantage comes from a cheap price list, not an evidenced property of airlifts. |
| Facility capex per m3 of production vessel, Negulescu | about $27k/m3 (ALR), $110k/m3 (210 m3 STR), $207k/m3 (42 m3 STR) | MODEL | Already in repo (arithmetic by the earlier note). |
| Quorn 155 m3 airlift | about $42M for one reactor in 304 stainless = $271k/m3; 66.7% of a $108M mycoprotein plant | MODEL (a TEA, not a plant record) | Frontiers 2023, PART via fetch summary. Real plant figures in repo: GBP 30M (third fermenter, 2014-15), GBP 37.5M each (older, not inflation-adjusted). |
| Humbird's 20 m3 STR scaled to 155 m3 with exponent 0.6 | $611k x (155/20)^-0.4 = about $270k/m3 | INF | **This equals the Quorn TEA's $271k/m3.** |

**Reading.** The only like-for-like pair I could build says an aseptic stainless airlift costs about the same per m3 as a stirred tank of the same size (ratio about 1.0). Negulescu's 0.15 comes from the price list. **Reasoned range for airlift:STR capital per m3 at equal volume and equal sterility spec: 0.5-1.0, central 0.8 (assumption).** The reasons for a discount are no impeller, drive or seal. The reasons against are a taller and thicker shell, a compressor, bigger exhaust and a gas filter train, and a possibly pressurised loop. The caveat is that airlift volume must also be larger for the same cell mass if gas per litre cannot be raised (below).

### 1f. Maximum practical volume

- Animal cells: 2 m3 (demonstrated, Lonza), 10 m3 (claimed, Humbird), 1.25 m3 (Ark, cultivated meat). Nothing above that.
- Engineering limit: the same 200 m3 sterility limit Humbird quotes for all vessels ("not practicably sterilized to a level suitable for animal cell culture above about 200 m3", already in repo). Microbial gas-lift loops reach 150 m3 (Quorn, years of operation) and 1,500 m3 (Pruteen, failed commercially).
- My judgement: 100-300 m3 is feasible mechanically; whether the cells are alive at the top of a 13 m column is untested.

---

## 2. Plain bubble column

- **OTR, CO2, scale.** Humbird (FULL): "Judicious sparging rules out the bubble-column bioreactor, which has not been successfully used for animal cell culture beyond the bench scale." My search found no counter-example. Sucker et al. 1994 "bubble bed reactor" exists (title only in the PMC reference list; not read). The repo's `gas_flow_cap.md` proposes bench bubble columns (0.1-1 L) as the deciding experiment.
- **OTR in microbial columns:** 150 mmol/L/h in 200 m3 yeast columns (above), with foam as the limit. For animal cells in a column: not found.
- **Mixing and shear.** A column has no circulation loop, so mixing is by bubble wake only. A thesis (SEC, not read: https://core.ac.uk/download/323206707.pdf) says the airlift "has better mixing at large scale than the bubble column", and I take that as consistent with general airlift theory. In a column all cells pass the bubble zone and the surface, as in an airlift.
- **CO2.** Same per-litre arithmetic as 1b. No loop means no unsparged downcomer, so there is no O2 depletion route, but also no guaranteed circulation.
- **Largest animal-cell volume:** bench (Humbird); I found no pilot record. **Non-animal:** 200 m3 baker's yeast.
- **Capital:** simpler than an airlift (no draft tube). The only figure is Humbird's yeast columns at $818k per 200 m3 = $4.1k/m3. That is a non-aseptic yeast figure and is not usable for an animal-cell vessel (INF).
- **Judgement:** 90% that it is no better than an airlift for the model.

---

## 3. Rocking-motion (wave) bag, at its scale limit

| Item | Value | Label | Source and access |
|---|---|---|---|
| Largest wave bag for animal cells in a paper | **500 L working volume** (Wave System1000), CHO perfusion, scale-up 25 L to 100 L to 500 L "straightforward" with comparable growth, protein and doubling time | M, Animal | Pierce and Shabram, BioProcessing Journal 2004, https://bioprocessingjournal.com/afp/J34-Pierce.pdf, FULL (by pdftotext). Densities 1.5 x 10^7 cells/mL or more; at 2 x 10^7 and 3 x 10^7 the 25 L run was limited by nutrients and lactate; oxygenation was "not an issue", dissolved O2 held at 73-100%. I did not extract the exact peak density of the 500 L run. |
| Current catalogue | Cytiva rocking bags are 1-25 L | SEC | https://www.cytivalifesciences.com/shop/cell-culture-and-fermentation/rocking-bioreactors/consumables-and-accessories (search summary). Another summary says 600 L (BIOSTAT CultiBag RM) and 1,000 L (Wave) exist (CHIMIA paper, SEC). I did not verify any current large rocking product. |
| kLa, rocked bags 10-50 L | O2: 3.5-29 /h; CO2: 0.6-2.7 /h | M (thesis) | UCL thesis (Marsh), https://discovery-pp.ucl.ac.uk/id/eprint/1534658/1/Marsh_DTJM%20Thesis%20Final_CR%20fig%20removed.pdf, SEC |
| kLa, 20 L Wave | maximum 4 /h (Singh); 10 L: linear to 25 rpm then 4x at 40 rpm | M | BPI article, https://bioprocessintl.com/bioreactors/oxygen-mass-transfer-correlation-for-a-rocking-motion-bioreactor-system, PART. Largest bag tested 50 L; kLa at 50% fill similar for 20 and 50 L. |
| OTR in mmol/L/h | 4 /h gives about 0.6; 15 /h about 2; 29 /h about 4 (air, 70% DO driving force) | INF | With O2-enriched gas about 5x more. |
| What this means at density | A CHO culture at 2 x 10^7 cells/mL (about 60 g/L wet) takes roughly 7 mmol/L/h by Meuwly's qmax of 9.44e-17 mol/cell/s (qmax quoted in Hubbard, FULL) | INF | So wave bags need O2 enrichment and the top of what they have shown is about 30% of Humbird's STR cap. |
| CO2 removal | Surface and overlay gas only, no sparging. CO2 kLa 0.6-2.7 /h at 10-50 L. Clincke's 4 L bag at 214 million cells/mL was limited by viscosity, filter and CO2 (already in repo). | M | UCL thesis SEC. |
| Scale-limiting reason | Surface-to-volume ratio falls with scale, and the bag must be rocked; the bag film and platform limit it. Humbird: gamma-sterilisation totes are 60 cm deep, so an impeller bag has a maximum of about 4 m3 working volume; single-use units to 6 m3 are on sale, "aimed at lower cell-density processes". | R | Humbird, FULL |

**Largest in any single-use format:**
- 2,000 L: XDR-2000 stirred bag; kLa measured 1.1-19.7 /h with 20 L/min air (0.01 vvm), 400-2,000 L, 25-115 rpm (Cytiva note, FULL; vendor-measured with water, NaCl, poloxamer and 50 ppm antifoam). The note does not give a CO2 kLa. This is 2.8 mmol/L/h in air at best (INF), against 29 in the model's tank, though more gas and O2 enrichment would raise it.
- 5,000 L: Thermo DynaDrive S.U.B. 3,000 and 5,000 L launched 2021 (V). The brochure claims "mixing power of greater than 80 W/m3" and "better kLa", with no number I could see. Sources: https://www.labmanager.com/thermo-fisher-scientific-launches-3-000-l-and-5-000-l-hyperforma-dynadrive-single-use-bioreactors-s-u-b-s-for-cell-culture-production-25369 (SEC) and the Patheon white paper (FULL, no kLa numbers). WuXi has installed 5,000 L units (already in repo).
- A 5 m3 single-use CHO fed-batch at 30-40 million cells/mL and 0.012-0.017 vvm (already in repo, [23]).
- No animal-cell run above about 6 m3 in single-use. Humbird: single-use economics vanish at about 10 t/y of mAb, and bags are inconsistent with food-scale production. The brief lets me add: Humbird's own number for a 15% charge on a $10M cell-therapy plant is $833k/kg.

### 3e. Cost of a bag per run

- **Bag price: not found.** Searched: "single-use bioreactor bag price 2000 L", "cost per run", Pollock, Klutz and Sinclair. Only the following turned up.
  - A forum commenter (the Effective Altruism forum, attributed in the search result to Humbird's thread) quotes about $30k for a 1,000 L bag, "ballpark" for biopharma. Not sourced; I could not fetch the page (connection refused). SEC.
  - A pharma column assumes a $5,000 1,000 L mixer bag (an assumption, a mixer rather than a bioreactor). SEC.
- **Capex saving claim:** 40-50% lower capex for single-use (an analyst guide, unverified, SEC).
- **Crossover claim:** stainless is cheaper per batch above about 2,000-5,000 L and 100-200 batches per year; for 2,000 L, single-use wins up to about 10 batches per year (Fujifilm, SEC).
- **Changeover:** 1-2 days single-use against 5-10 days stainless, 44 against 40 batches per year in a Cytiva simulation (vendor, SEC).

**Reasoned range (INF, assumption).** Take a bag at $15-30 per litre of working volume per run (from the $30k/1,000 L figure, halved for a food-grade, larger, thinner bag). At 14-21 day runs the number is 17-26 runs per year, so about $250-780 per litre per year.
- That is 2.5-8 times the annualised capital of the model's stainless tank (about $100k/m3/yr at $611k/m3 and a 15-17% charge).
- Per kg of wet cells, at one harvest of 120-250 g/L per run: $15-30 per litre divided by 0.12-0.25 kg/L is $60-250 per kg from the bag alone. Even $3 per litre would be $12-25/kg.
- For the bag to match stainless capital, the bag price would have to fall to about $3-5 per litre per run.

**Capital ratio bag against stainless STR (INF):** a single-use tank has no jacketing, no CIP and no steam-in-place, so the reusable hardware is much cheaper; the vendor claim is 40-50% less capex. I could not find a per-litre value. Given the consumable above, I put the *annualised* cost ratio (capital plus bag) at 2-6 times stainless for continuous food-scale operation (assumption). I put 70% on "bags cannot be below stainless in $/kg at any food scale before 2035".

### 3f. Maximum practical volume
- Wave-type bag: 500 L working in an animal-cell paper (2004), 1,000 L at most in vendor catalogues I could not confirm, 25 L in current Cytiva rocking bags (SEC). Why: rocking motion transfers by surface only, and the bag film and platform bear the load.
- Single-use stirred: 2,000 L widespread, 5,000 L now, 6 m3 reported, about 4 m3 for the gamma-sterilisation tote with the standard geometry (Humbird). Why: the sterilisation tote and the bag-film weight.

---

## 4. Head-to-head airlift against stirred for animal cells

**Not found.** Searched: "comparison airlift versus stirred tank bioreactor hybridoma CHO productivity cell density", "Tramper OR Merchuk OR Jusczyk"-style combinations. The closest items are:
- A 2 L perfusion airlift matched the antibody productivity of a 50 L batch airlift (patent US4806484, SEC), which is not airlift against stirred.
- A claim that "the higher overall mass transfer coefficient obtained in the airlift explains airlift productivity relative to stirred vessels" (SEC), with no data seen.
- Varley and Birch 1999 (ABS only, https://pmc.ncbi.nlm.nih.gov/articles/PMC3463394): stirred tanks are the commonest and airlifts "also used, albeit less commonly"; "no specific guidelines have been published for large scale (≥10 000 L)".
- Industrial practice itself: Lonza and Celltech used airlifts in the 1980s and 1990s, then the industry moved to stirred tanks. I have no document giving the reason, and I do not want to assert one.

---

## 5. Summary table against the model's STR

| | STR (model) | Airlift, 100-260 m3 | Bubble column | Wave bag 500 L | Single-use STR 2,000-5,000 L |
|---|---|---|---|---|---|
| OTR, mmol/L/h | 29 (Humbird cap) | about 7-13 in air at 6-16 mm/s (INF from Negulescu's kLa); Negulescu claims 13.5 | not found for animal cells | about 0.6-4 in air (INF from kLa 4-29 /h) | about 2.8 in air at 0.01 vvm (INF from XDR kLa 19.7); more with gas and O2 |
| Gas per litre at 20 m3 | 0.09 vvm at 6 mm/s | 0.057 vvm at 10 mm/s, 0.086 at 15 mm/s (10.5 m deep) | same as airlift | surface only | 0.01 vvm tested |
| CO2 | sparge only | needs 14-16 mm/s for the same gas per litre as the STR | same | CO2 kLa 0.6-2.7 /h | as STR |
| Largest animal-cell volume | 20 m3 (Vow, claim) | 2 m3 published (Lonza), 1.25 m3 cultivated meat (Ark) | bench | 500 L (2004) | 5-6 m3 |
| Largest non-animal | many | 155 m3 (Quorn, continuous); 1,500 m3 (Pruteen, failed commercially) | 200 m3 (yeast) | none relevant | none |
| Capital per m3, same sterility | 1.0 | 0.5-1.0 central 0.8 (assumption; Quorn TEA gives about 1.0; Negulescu price list gives 0.15) | below airlift (assumption) | n/a (consumable) | 0.5-0.6 for hardware (vendor claim) plus $15-30/L/run bag (assumption) |
| Max practical volume | about 200 m3 (sterility) | 100-300 m3 mechanically | not shown | 500 L | 5-6 m3 |

---

## 6. Gaps and what would change my mind
1. Any pilot-scale measurement of CO2 and foam in an airlift with cells at 50+ g/L. Ark's 1,250 L run is the nearest and is unpublished. This is the single most useful datum.
2. A real price for an aseptic 100+ m3 airlift. Zuber 1997 (Sulzer) was not read. If it is a waste-water loop, Negulescu's $0.8k/m3 is not applicable.
3. The Birch and Arathoon 1990 chapter and Varley and Birch 1999 full text, for airlift kLa and CO2 at 1-10 m3.
4. A bag price from a vendor or a published TEA.
5. The 500 L Wave peak density (Pierce Fig. 2).

## 7. Sources, with access level

| Source | URL | Access |
|---|---|---|
| Hubbard 2024, CFD of 20 and 42 m3 STR and 300 m3 airlift | https://engrxiv.org/preprint/download/3788/6856 | FULL |
| Negulescu et al. preprint (2022; published 2023) | https://engrxiv.org/preprint/download/2414/4659/3571 | FULL |
| Humbird 2020 report | https://engrxiv.org/preprint/download/1438/2973/2173 | FULL (relevant sections) |
| Cytiva XDR-2000 characterisation note | https://cdn.cytivalifesciences.com/api/public/content/digi-18410-pdf | FULL |
| Thermo 5,000 L white paper (Patheon-hosted) | https://www.patheon.com/content/dam/patheon/global/library/resources/whitepapers/wp-5-000L-Single-use-bioreactors-The-next-generation-in-biologics-manufacturing.pdf | FULL (no kLa numbers) |
| Pierce and Shabram 2004, Wave 25-500 L perfusion | https://bioprocessingjournal.com/afp/J34-Pierce.pdf | FULL (peak 500 L density not extracted) |
| Lonza, Chimia 1997 | https://chimia.ch/chimia/article/download/1997_290/2172/12827 | FULL (two paragraphs) |
| BPI rocking-bag kLa article | https://bioprocessintl.com/bioreactors/oxygen-mass-transfer-correlation-for-a-rocking-motion-bioreactor-system | PART |
| Frontiers 2023, mycoprotein TEA | https://www.frontiersin.org/articles/10.3389/fsufs.2023.1204307/full | PART (fetch summary) |
| Sheffield Quorn airlift paper | https://eprints.whiterose.ac.uk/id/eprint/232799/1/1-s2.0-S0960308524000646-main.pdf | PART |
| Varley and Birch 1999 | https://pmc.ncbi.nlm.nih.gov/articles/PMC3463394 | ABS |
| Chisti 2000 | https://acnpsearch.tweb-dev.unibo.it/singlejournalindex/75846935 | ABS |
| Thesis on disposable reactors | https://core.ac.uk/download/323206707.pdf | SEC (HTTP 403) |
| UCL Marsh thesis | https://discovery-pp.ucl.ac.uk/id/eprint/1534658/1/Marsh_DTJM%20Thesis%20Final_CR%20fig%20removed.pdf | SEC |
| Cytiva rocking consumables page | https://www.cytivalifesciences.com/shop/cell-culture-and-fermentation/rocking-bioreactors/consumables-and-accessories | SEC |
| Thermo DynaDrive launch | https://www.labmanager.com/thermo-fisher-scientific-launches-3-000-l-and-5-000-l-hyperforma-dynadrive-single-use-bioreactors-s-u-b-s-for-cell-culture-production-25369 | SEC |
| Forum comment on bag price | https://ea.greaterwrong.com/posts/y8jHKDkhPXApHp2gb/cultured-meat-a-comparison-of-techno-economic-analyses/comment/b8C4qCGmBrjrt4Tyr | SEC (fetch failed) |
| Moore, Quorn fermentation chapter | https://davidmoore.org.uk/21st_century_guidebook_to_fungi_platinum/Ch17_18.htm | SEC |
| Scribd Chisti 1987 copy | https://www.scribd.com/document/403318966/1-chisti1987-pdf | SEC |
| US 4806484 perfusion airlift patent | https://patents.google.com/patent/US4806484 | SEC |
| Ark Biotech, GOOD Meat/ABEC | https://agfundernews.com/cultivated-meat-in-the-spotlight-at-tufts-cellular-ag-day-focusing-on-science-experiments-that-cannot-scale-is-misleading-people ; https://www.greenqueen.com.hk/?p=61899 | SEC |
