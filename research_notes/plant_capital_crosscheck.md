# Plant capital cross-check: capital per m3 of production bioreactor

Compiled 2026-11-14. Purpose: independent check on the model's three capital anchors
(Humbird fed-batch $683k/m3, Humbird perfusion $3.45M/m3, microbial "as built" $190k/m3).

Conventions
- "m3" is PRODUCTION (final-stage) vessel volume. Nominal vessel volume unless the source only gives working volume (WV); the basis is stated per row.
- Prices are as stated by the source, in the source's price year. Nothing is escalated or currency-converted.
- "TCI" = total capital investment including engineering/construction and contingency. "TDC" = total direct (installed) cost. "PEC" = purchased (bare) equipment cost.
- Arithmetic is shown as `capital / volume`. `[inferred]` marks anything not stated verbatim by the source. `[claim]` marks unaudited company statements.
- Access: OA = open access; local = text extraction in the session scratchpad `tea/`, `dl/`, `pas/` (PDFs in `~/Documents/Cultivated_meat_TEAs/`); web = trade press / company page.

---

## (a) Master table

### A1. Animal-cell design studies

| # | Source | Kind | Plant class | Vessels x size | Mode | Total prod. m3 | Capital figure and what it includes | Price year | $k per m3 | $ per t/yr | Access |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Humbird 2021, fed-batch (Tables 4.1-4.3) [S1] | Design study | Food product, but Class 8 clean room for cell culture, Class 6 labs; sterile ASME 316L vessels, non-cGMP | 24 x 20 m3 (+ seed train 24 x 16 m3 and smaller) | Fed-batch | 480 | TCI $327,907,000 (ISBL + OSBL + buildings = TDC $178.2M; + E&C 0.6xTDC; + fees and contingency 0.15xTPC) | 2018 | 327,907 / 480 = **683** (TDC basis: 178,210 / 480 = 371; PEC basis: 45,590 / 480 = 95) | 327.907M / 6,800 t wet = **48,200** | local, OA |
| 2 | Humbird 2021, perfusion (Tables 4.8-4.10) [S1] | Design study | Same as #1 | 96 x 2 m3 (+ 192 ATF-10) | Perfusion | 192 | TCI $662,628,000 (TDC $360.1M) | 2018 | 662,628 / 192 = **3,451** (TDC: 360,124 / 192 = 1,876) | 662.628M / 6,900 t wet = **96,000** | local, OA |
| 3 | CE Delft 2021 (Vergeer et al.), Table 2, Fig. 10, Annex C [S2] | Design study (industry-data based) | Food-grade; explicitly "does not include ... clean rooms" or FDA drug standards | 130 x 12.5 m3 STR (10 m3 WV) proliferation + 430 x 2.5 m3 perfusion reactors (2 m3 WV) differentiation + 107 x 60 L | Semi-continuous (3 harvests) then perfusion on scaffolds | STR 1,625 nominal (1,300 WV); PR 1,075 nominal (860 WV); both 2,700 nominal | "around $450 mln" = bare equipment x installation (Lang) factors; factors "including placement, instrumentation, piping, electrical, buildings, engineering and contractors"; overall Lang ~3. No separate contingency line. Split: PR $260M, STR $150M, 50 L STR $20M, media tanks $10M, CIP/SIP $7.5M | Not stated (2021 report; "conditional on ... steel prices towards 2030") | All vessels: 450,000 / 2,700 = **167**. On STR volume only: 450,000 / 1,625 = **277**. STR line alone: 150,000 / 1,625 = 92. PR line alone: 260,000 / 1,075 = 242 | 450M / 10,000 t = **45,000** | local, OA |
| 4 | Negulescu et al. 2023, 42K STR (Tables 1-2) [S3] | Design study (SuperPro) | Food-grade 304 SS, ASME, SIP/CIP; clean rooms not stated | 50 x 41.9 m3 (33.4 m3 WV) per facility `[inferred: 1,250 production bioreactors / 25 facilities]` | Fed-batch | 2,095 | "CAPEX per facility" $438M; composition not given in main text (SI Tables S3-S4 not in local extract) | CEPCI-adjusted to "current year" (2021 index cited); not stated explicitly | 438,000 / 2,095 = **209** | 438M / 4,000 t = **109,500** | local, OA |
| 5 | Negulescu 2023, 211K STR [S3] | Design study | as #4 | 50 x 211.1 m3 (168.9 WV) `[inferred: 250 / 5]` | Fed-batch | 10,555 | CAPEX per facility $1,172M | as #4 | 1,172,000 / 10,555 = **111** | 1,172M / 20,000 t = **58,600** | local, OA |
| 6 | Negulescu 2023, 262K airlift [S3] | Design study | as #4 | 50 x 261.8 m3 (209.4 WV) `[inferred: 200 / 4]` | Fed-batch, airlift | 13,088 | CAPEX per facility $366M (ALR priced from a 1997 Sulzer figure, $174,300 for 190 m3, scaled by 0.6 power) | as #4 | 366,000 / 13,088 = **28** | 366M / 25,000 t = **14,600** | local, OA |
| 7 | Garrison et al. 2022, sect. 2.3.1 [S4] | Design study (vendor quote) | "food-grade processing equipment"; clean rooms not stated; building leased, not in capital | 4 x 20 m3 (seed 200 L, 1,000 L, 5,000 L per line) | Batch, single harvest | 80 | $60,000,000 "with all equipment and setup included" (4 bioreactor lines, media prep, harvest, inactivation, CIP). Excludes building (leased) and $0.33M cold storage. No engineering/contingency line | Not stated (2022 paper) | 60,000 / 80 = **750** | 60M / 548.4 t = **109,400** | local, OA |
| 8 | Pasitka et al. 2024, ATF case (SI Tables S1-S4) [S5] | Design study (Believer Meats authors; Humbird method + vendor quotes) | "CNC" (controlled-not-classified) production floor at $3,759/m2 (same rate as Humbird's Class 8) | 25 x 2 m3 WV (+ 50 ATF-10) | Perfusion, continuous harvest | 50 (WV) | TCI $123,896,062 (TDC $67.3M; E&C 0.6x; fees/contingency 0.15x) | Not stated (2024 paper; Humbird 2018 basis plus quotes) | 123,896 / 50 = **2,478** | 123.9M / 1,070 t wet biomass = **115,800** | local, SI OA |
| 9 | Pasitka 2024, TFF case [S5] | Design study | as #8 | 10 x 5 m3 WV | Perfusion (TFF) | 50 (WV) | TCI $63,084,062 (TDC $34.3M) | as #8 | 63,084 / 50 = **1,262** | 63.08M / 1,070 = **59,000** | local |
| 10 | Pasitka 2024, "large-scale perfusion" (theoretical) [S5] | Design study | as #8 | 2 x 25 m3 WV | Perfusion (continuous centrifuge, hypothetical) | 50 (WV) | TCI $40,343,176 (TDC $21.9M) | as #8 | 40,343 / 50 = **807** | 40.34M / 1,070 = **37,700** | local |
| 11 | Risner et al. 2021 [S6]; Ashizawa et al. 2022 uses the same method [S7] | Design study, bioreactors ONLY ("minimum" capex) | "standard food-grade bioreactors" | 5,205 down to 50 x 20 m3 | Fed-batch | 104,100 (scenario 1) | $778,000 per 20 m3 bioreactor = $50,000/m3 unit cost x 20^0.6 x 1.29 inflation x Lang 2 `[decomposition per Ashizawa p.~6; 50,000 x 6.034 x 1.29 x 2 = 778,400]`. No seed train, buildings, utilities, indirects. "USD 4 billion to USD 37 million" total | 2021 paper; inflation-adjusted, year not stated | 778 / 20 = **39** | Scenario 1: 4,050M / 121,000 t = 33,500; scenario 4: 37M / 121,000 = 306 | local, OA |
| 12 | Humbird 2021 Table 3.3, single sterile bioreactor, installed [S1] | Equipment-level estimate (ACCE) | Sterile stirred tank, 316L, non-cGMP | 1 vessel of 1 / 2 / 5 / 10 / 20 / 50 / 100 / 200 m3 | n/a | n/a | Installed (direct) cost: $774k / $856k / $966k / $1.2M / $1.5M / $2.6M / $4.0M / $6.8M. Bare: $59k / $93k / $138k / $217k / $330k / $722k / $1.3M / $2.4M | 2018 | Installed: 774 / 428 / 193 / 120 / **75** / 52 / 40 / **34**. Bare: 59 / 47 / 28 / 22 / 16.5 / 14 / 13 / 12 | n/a | local |

Design studies with no usable capital number: Lever VC 2025 [S8] (qualitative only: reactors are "~30-40% of the total facility costs"; leading companies' expected CapEx "reduced by nearly an order of magnitude"; no $ figures); Quint/Ark 2023 [S9] (bioreactors "25-50%+ of total upstream factory cost"; exhibits only, no plant total in text); SuperMeat 2024 [S10] (25,000 L basis, no capital total in text); Gu 2025 [S11] and Goodwin 2024 [S12] only restate CE Delft / Negulescu / Risner / Garrison figures; GFI 2021 anticipatory LCA/TEA summary [S13] restates CE Delft "$450M USD (-20% to +40%)".

### A2. Animal-cell plants built, under construction, or announced

| # | Plant | Kind | Plant class | Vessels x size | Mode | Total prod. m3 | Capital figure and what it includes | Price year | $k per m3 | $ per t/yr | Source type |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 13 | Believer Meats, Wilson NC [S14-S18] | Built (Phase 1 complete Oct 2025; company then entered insolvency; never ran commercially) | Food (USDA grant of inspection); 200,000 sq ft | 50 L, 200 L, 2,000 L and 20,000 L vessels (AgFunder "understands", from sources, not filings). Count: not stated | Perfusion/continuous (per company's Nature Food paper) | Not stated | (i) $123.35M "initial planned investment" (company announcement, Dec 2022). (ii) "Over $150 million invested in designing, building and installing related equipment" (BDO sale teaser). (iii) $154M, "about 11% over initial projections" (GFI State of the Industry 2026, citing public filings). Whole facility incl. building and downstream | 2022-2025 nominal | Not computable from stated data. `[inferred, low confidence]`: if the claimed 10,000 t/yr product is 50% biomass at Pasitka's 1.8 kg/L/month (21.6 t/m3/yr), volume = 5,000 / 21.6 = 231 m3 and 154,000 / 231 = ~665 | 154M / 10,000 t `[claim: "at least 10,000 metric tons"]` = **15,400** | (i) company; (ii) sale document; (iii) GFI from filings |
| 14 | UPSIDE Foods EPIC, Emeryville CA [S19] | Built (2021) | Food; 53,000 sq ft; retrofit of a former grocery store | Cultivators up to 2,000 L (count not stated) | Not stated | Not stated | Cost not found in any source retrieved (a "$50M" figure I recalled could not be verified; do not use) | - | n/a | n/a. Output `[claim]`: >50,000 lb/yr (22.7 t) as configured, 400,000 lb/yr (181 t) max | company |
| 15 | UPSIDE Foods "Rubicon", Glenview IL [S20] | Announced Sep 2023, paused Feb 2024 | Food; 187,000 sq ft | "range of bioreactors up to 100,000 liters"; count not stated | Not stated | Not stated | $140M (company, via AgFunder interview) | 2023 | n/a | n/a ("millions of pounds" initially; >30M lb potential) | company |
| 16 | GOOD Meat / ABEC, US site [S21] | Announced May 2022; not built | Food | 10 x 250,000 L | Not stated | 2,500 | Not disclosed (Eat Just: total company investment "several hundred million dollars") | - | n/a | n/a; output `[claim]` 30M lb/yr (13,600 t) -> 5.4 t/m3/yr | company |
| 17 | Vow, Sydney Factory 2 [S22, S23] | Built | Food-grade, in-house fabricated | 1 x 20,000 L (later described as 22,000 L) | Not stated | 20 | VESSEL ONLY: "well under $1 million", commissioned in "under 14 weeks"; said to be 80% below an off-the-shelf biopharma-spec system. Factory total not stated | ~2024 | Vessel only: < 1,000 / 20 = **< 50** `[claim]` (cf. Humbird Table 3.3 installed 20 m3: 75; bare: 16.5) | n/a | CEO claim |
| 18 | BlueNalu, planned first large facility [S24] | Announced (TEA press release, Oct 2022) | "will follow GMP"; ~140,000 sq ft | 8 x 100,000 L | Not stated | 800 | Not stated | - | n/a | n/a; output `[claim]` 6M lb/yr (2,720 t) -> 3.4 t/m3/yr | company |
| 19 | Mosa Meat, Maastricht [S25] | Built (2023) | Food; 2,760 m2 | 1,000 L bioreactors (count not stated) | Not stated | Not stated | Not stated | - | n/a | n/a | company |
| 20 | Ivy Farm, Oxford pilot [S26] | Built (2022) | Pilot; 18,000 sq ft | 1 x 600 L terminal | Not stated | 0.6 | Not stated | - | n/a | n/a; `[claim]` 2.8 t/yr -> 4.7 t/m3/yr | company |
| 21 | Meatable, Leiden pilot [S27] | Built (2023) | Pilot; 3,300 m2 | 200 L, later 500 L | Not stated | 0.2-0.5 | Not stated | - | n/a | n/a | company |
| 22 | Aleph Farms (Rehovot pilot; Modi'in; Thailand plan) [S28] | Built pilot / announced | - | Thailand plan: 2,000-5,000 L, < 1,000 t/yr | Not stated | Not stated | Not stated | - | n/a | n/a | company |
| 23 | Wildtype, San Francisco pilot | Built | Pilot | Not found | - | - | Not found | - | n/a | n/a | - |
| 24 | Meatly (UK) [S16] | Built | Food-grade | 1 x 320 L | - | 0.32 | Bioreactor "reported to cost 95% less" than off-the-shelf; no absolute figure | - | n/a | n/a | company, via GFI |

Bottom line for built animal-cell plants: **no built plant has both a published capital cost and a published production volume.** The only hard total is Believer ($123M announced, ~$150-154M spent). Per tonne of claimed capacity it is $15.4k/t, about one third of Humbird fed-batch ($48k/t), but the capacity was never demonstrated.

### A3. Microbial / fermentation plants

| # | Source | Kind | Plant class | Vessels x size | Mode | Total prod. m3 | Capital figure and what it includes | Price year | k per m3 | per t/yr | Access |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 25 | Humbird 2021 App. A, baker's yeast, standard (Table A.1, A.5) [S1] | Design study | Non-sterile-class Lang factor 4.5; 316L jacketed bubble columns; no clean room | 6 x 200 m3 BCR (seed: 2 x 85 m3 and smaller) | Fed-batch, 24 h turnaround | 1,200 | TCI $68,742,000 = TPEC $15,276,000 x Lang 4.5 | 2018 | 68,742 / 1,200 = **$57** (PEC basis: 15,276 / 1,200 = 12.7) | 68.742M / 17,300 t dry = **$3,970 per t dry**; `[inferred from his $1.89 dry = $0.57 wet, i.e. 30% DM]` 57,700 t wet -> $1,190 per t wet | local, OA |
| 26 | Humbird 2021 App. A, yeast constrained to animal-cell-like limits (Table A.5) [S1] | Design study | as #25 | 27 x 20 m3 | Fed-batch | 540 | "Total CAPEX $70M" | 2018 | 70,000 / 540 = **$130** | 70M / 1,700 t dry = $41,200 per t dry | local |
| 27 | Liberation Labs, Richmond IN [S29, S30] | Under construction (start-up slipped from end-2024 to 2026) | Food-grade precision fermentation, with dedicated downstream | 600,000 L total. "4 x 150 m3" is NOT confirmed by any source I retrieved | Fed-batch `[inferred]` | 600 | "expected to cost around $115M" (CEO estimate, 2023; whole project incl. DSP). No updated total found | 2023 | 115,000 / 600 = **$192** `[claim]` | Not stated | company |
| 28 | Quorn / Marlow Foods, fermenters Q2 and Q3 (1990s) [S31] | Built | Food, continuous sterile airlift | 155 m3 each | Continuous airlift | 155 | "each cost GBP 37.5M to build" (textbook, secondary) | ~1993-94 GBP | 37,500 / 155 = **GBP 242** | Not stated | OA textbook |
| 29 | Quorn, "third fermenter" project completed July 2015 [S32] | Built (brownfield; project started 2007, mothballed 2008/09) | as #28 | 1 fermenter; size not stated in the news items (`[inferred]` 155 m3 twin) | Continuous airlift | 155 `[inferred]` | GBP 30M | 2014-15 GBP | 30,000 / 155 = **GBP 194** `[inferred volume]` | 30M / 14,000 t paste = GBP 2,140 (one source; another says +50-60% capacity) | trade press / company |
| 30 | Quorn, Billingham expansion opened Nov 2018 [S33] | Built | as #28 | Fermenter count/volume not stated | Continuous | Not stated | GBP 150M total, incl. a GBP 27M product-forming building; adds ~20,000 t/yr | 2018 GBP | n/a | 150M / 20,000 t = GBP 7,500 (includes downstream food processing) | company |
| 31 | Solar Foods Factory 01, Vantaa [S34] | Built (2024), at design capacity Oct 2025 | Food; gas fermentation (H2/CO2), first of a kind, incl. electrolysis | 1 x 20,000 L | Continuous gas fermentation | 20 | "approximately EUR 42 million" total investment | 2022-24 EUR | 42,000 / 20 = **EUR 2,100** | 42M / 160 t = EUR 262,500 | company |
| 32 | ENOUGH, Sas van Gent [S35] | Built (2022) | Food; continuous mycoprotein; co-located with Cargill (feedstock/utilities over the fence) | Not found | Continuous | Not found | EUR 42M reported for the 15,000 m2 plant (one trade source; other sources quote only the EUR 16.9M CBE-JU grant) | 2021-22 EUR | n/a | 42M / 10,000 t = EUR 4,200 `[claim capacity]` | trade press |
| 33 | BCG x Synonym 2024, standardised "biofoundry" [S36] | Benchmark (consultancy/company) | Food precision fermentation | "at least 2 million liters" | Fed-batch | >= 2,000 | "$300 million to $400 million each" | 2024 | 300,000-400,000 / 2,000 = **$150-200** `[my arithmetic]` | Not stated | OA web |
| 34 | Cauldron CEO remark [S37] | Benchmark (company claim) | Precision fermentation | 500,000 L batch facility | Batch | 500 | "$100 to 200 million to build" | ~2024 | 100,000-200,000 / 500 = **$200-400** `[my arithmetic]` | - | trade press |
| 35 | Risner et al. 2023 mycoprotein TEA [S38] | Design study (minimum capex; excludes land, working capital, start-up) | 304 SS airlift | 155 m3 airlifts; count `[inferred]` 2 (one at ~$42M, "additional" at ~$29M) | Continuous | 310 `[inferred]` | ~$108M mycoprotein capex (bioreactors, RNA-reduction vessels ~$18M, centrifuges ~$13M, chillers ~$4M) | Not stated (2022-23) | 108,000 / 310 = **$348** `[inferred count]` | 108M / (2,000 kg/h x 8,760 h = 17,520 t wet paste `[inferred, 100% uptime]`) = $6,200 | OA (web summary only; tables not checked) |
| 36 | Petrides/SuperPro example plants as tabulated by Humbird Table 3.1 [S1] | Reference Lang factors | lysine (non-sterile outdoors) / beer / lactase / insulin (cGMP) / mAb (cGMP cell culture) | final vessel 500 / 135 / 90 / 50 / 20 m3 | - | - | Overall Lang factor 4.7 / 6.1 / 7.1 / 8.8 / 10.9; cost of a 20 m3 vessel $133k / $168k / $1.01M / $1.01M / $1.96M | - | - | - | local |

Not found: Nature's Fynd (Chicago 200,000 sq ft; "price was not disclosed"), Perfect Day, The Every Co. (both use contract manufacturers; no plant capital found), Synonym "State of Global Fermentation" (2023; capacity census of 246 facilities, no $/L capex found in public excerpts).

### Ranges on the common basis

| Group | Range, $k per m3 production vessel | Notes |
|---|---|---|
| Animal-cell designs, full plant, fed-batch/batch, 20-40 m3 vessels | 167-277 (CE Delft, food-grade, Lang ~3) ; 209 (Negulescu 42 m3) ; **683** (Humbird) ; 750 (Garrison) | Humbird sits at the upper end; the two lower ones assume no clean rooms and a Lang factor of ~3 vs 7.2 |
| Animal-cell designs, large vessels (211-262 m3) | 28-111 (Negulescu) | Hypothetical scale |
| Animal-cell designs, perfusion, 2-25 m3 | 807 / 1,262 / 2,478 (Pasitka, WV basis) ; **3,451** (Humbird) | Pasitka ATF case at 2 m3 is 28% below Humbird at the same vessel size |
| Bioreactor-only "minimum" | 39 (Risner/Ashizawa) ; 34-75 installed (Humbird Table 3.3, 200-20 m3) ; < 50 (Vow vessel claim) | Not plant costs |
| Built animal-cell plants | None computable. Believer `[inferred]` ~665 | See A2 |
| Microbial, design | 57 (Humbird yeast, 200 m3) ; 130 (same, forced to 20 m3) ; ~348 (Risner mycoprotein, inferred) | |
| Microbial, built/announced | **192** (Liberation Labs, $, claim) ; GBP 194-242 (Quorn 155 m3 airlift) ; 150-400 (BCG, Cauldron benchmarks) ; EUR 2,100 (Solar Foods, 20 m3 first-of-a-kind gas fermentation) | The model's $190k/m3 matches Liberation Labs and Quorn-in-GBP; it is 3.3x Humbird's own yeast design (57) |

---

## (b) Humbird: baker's yeast plant vs animal-cell fed-batch plant, line by line

The yeast plant (Appendix A, Table A.1) is costed as purchased equipment x one overall Lang factor (4.5); Humbird does NOT tabulate its direct costs by area. The animal-cell plant (Tables 4.1-4.3) is built bottom-up (ISBL, OSBL, buildings, then indirects). To compare them, both are shown per m3 of production vessel; yeast lines below TPEC are therefore `[inferred]` from the Lang factor.

| Line | Animal cell, fed-batch (24 x 20 m3 = 480 m3) | $k/m3 | Yeast (6 x 200 m3 = 1,200 m3) | $k/m3 | Ratio animal/yeast |
|---|---|---|---|---|---|
| Production bioreactors, bare | 24 x ~$330k = $7.92M `[inferred from Table 3.3; Table 4.1 gives only bare total for all bioreactors, $13,794,000]` | 16.5 | 6 x $818,000 = $4,908,000 | 4.1 | 4.0 |
| Seed train, bare | $13.794M - $7.92M = $5.87M `[inferred]` | 12.2 | $1,369,000 | 1.1 | 10.7 |
| Production bioreactors, installed | $33,922,000 | 70.7 | not tabulated | - | - |
| Seed bioreactors, installed | $22,673,000 | 47.2 | not tabulated | - | - |
| Media prep / sterilisation, bare (fill tanks $1.660M, HTST $0.702M, makeup tanks $3.370M, filter housings $1.481M) | $7,213,000 | 15.0 | Pasteurizer $221,000 + prep tank $593,000 = $814,000 | 0.7 | 22 |
| Harvest / dewatering, bare | Disk-stack centrifuges 4 x 35 gpm, $1,744,000 | 3.6 | Centrifuges $1,728,000 + rotary vacuum filters $652,000 = $2,380,000 | 2.0 | 1.8 |
| Gas supply, bare | O2 VPSA $8,840,000 + O2 compressor $295,000 = $9,135,000 | 19.0 | Air compressors 2 x $1,375,000 = $2,750,000 | 2.3 | 8.3 |
| CIP tanks, bare | 12 x 42 m3, $4,136,000 | 8.6 | not listed (in "missing capital") | - | - |
| Other utilities, bare (boiler $154k, chiller $551k, cooling tower $24k) | $729,000 | 1.5 | "utilities equipment" estimated but not itemised | - | - |
| Missing/minor equipment allowance | 10%: ISBL $7,284,000 + OSBL $1,556,000 = $8,840,000 | 18.4 | 20%: $3,055,000 | 2.5 | 7.2 |
| **Purchased equipment (PEC)** | $45.59M `[sum: 13.794 + 7.213 + 1.744 + 7.284 + 14.000 + 1.556; matches TCI / 7.2]` | **95.0** | TPEC $15,276,000 | **12.7** | **7.5** |
| Installation | $21,113,000 (ISBL, 1.3x on non-bioreactor PEC) + $20,223,000 (OSBL) + bioreactor installation $42.80M `[= 33.922 + 22.673 - 13.794]` = $84.14M | 175.3 | inside Lang factor | - | - |
| ISBL total direct | $93,949,000 | 195.7 | - | - | - |
| OSBL total direct | $35,779,000 | 74.5 | - | - | - |
| Buildings | $48,482,000 (of which Class 8 cell-culture hall 5,268 m2 x 2 levels: $39,607,000; Class 6 labs $3.86M; shop, warehouse, office, slab $5.0M) | 101.0 | inside Lang factor (Table 3.1 lysine-class building factor: 0.10 x PEC = ~$1.5M `[inferred]`) | ~1.3 `[inferred]` | ~80 |
| **Total direct cost (TDC)** | $178,210,000 | **371.3** | `[inferred]` $68.742M / (1.6 x 1.15) = $37.4M | **31.1** | **11.9** |
| Engineering and construction | 0.6 x TDC = $106,926,000 | 222.8 | same factors per Table 3.1 (0.25 + 0.35) | 18.7 `[inferred]` | 11.9 |
| Fees and contingency | 0.15 x TPC = $42,770,000 | 89.1 | same factors (0.05 + 0.10) | 7.5 `[inferred]` | 11.9 |
| **TCI** | **$327,907,000** | **683.1** | **$68,742,000** | **57.3** | **11.9** |
| Overall Lang factor (TCI/PEC) | 7.2 | | 4.5 | | 1.6 |
| Annual output | 6.8 kTA wet (14.2 t wet per m3-yr) | | 17.3 kTA dry (14.4 t dry per m3-yr; ~48 t wet per m3-yr at 30% DM `[inferred]`) | | |
| TCI per t/yr | $48,200 per t wet | | $3,970 per t dry; ~$1,190 per t wet `[inferred]` | | ~40 on a wet basis |

Reading of the comparison
1. The 11.9x gap per m3 factors as 7.5x in purchased equipment per m3 times 1.6x in Lang factor (7.2 vs 4.5). The indirect-cost multipliers are identical (x1.84) in both cases, so the Lang difference is entirely direct-cost (installation and buildings).
2. Within equipment, the vessel itself is the smaller part: bare production vessel is $16.5k/m3 (sterile stirred 20 m3) vs $4.1k/m3 (200 m3 bubble column), a 4x gap, of which ~1.4x is pure scale on Humbird's own sterile curve (Table 3.3: 16.5 at 20 m3 vs 12 at 200 m3) and ~2.9x is vessel type/spec (12 vs 4.1 at 200 m3). The bigger multipliers are the seed train (10.7x per m3), media prep/sterilisation (22x), O2 supply (8x) and the missing-equipment allowance.
3. Sterile bioreactor installation is the single largest line: installed/bare is 4.1x for the animal bioreactors ($56.6M vs $13.8M), consistent with Table 3.3's direct-cost factor of 3.5 at 20 m3 (vs 1.8 at 200 m3).
4. Buildings: $101k/m3 for the animal plant (82% of it the Class 8 hall) vs roughly $1k/m3 implied for an outdoor lysine-class plant. Dropping the clean room to Humbird's "sanitary" rate would remove most of this line; CE Delft and Negulescu assume exactly that.
5. Humbird's own bridge: the yeast plant forced to 20 m3 vessels, low OTR and low growth rate costs the same $70M for 27 x 20 m3 = $130k/m3 (Table A.5), so vessel scale alone moves yeast from 57 to 130; the remaining 5.3x to 683 is sterility class, seed train, O2, media handling and clean-room building.

---

## Accuracy classes and stated uncertainty

| Source | Statement |
|---|---|
| Humbird 2021, sect. 1 (p. ~14) [S1] | "When performed responsibly, estimates from TEA can claim to be accurate to within 50% [80]", where [80] is the AACE cost-estimate classification system. No AACE class is named for the capital estimates specifically; method is factored (Lang) from ACCE/SuperPro equipment costs, i.e. AACE Class 4/5 in character `[my characterisation]` |
| CE Delft 2021, sect. 2.3.2 and Annex C [S2] | "Cost estimates are at FEL-1 stage"; STR, tanks and CIP/SIP unit costs carry "an uncertainty bandwidth ... of -20% to +40%"; "The estimated value for the perfusion reactor has a larger uncertainty bandwidth" (the perfusion reactors are 58% of the $450M) |
| Garrison 2022 [S4] | Vendor "warns ... the total cost could increase or decrease by up to 30%" |
| Pasitka 2024 [S5] | TCI sensitivity run from "15% lower and up to 45% higher" (results) and "varying the TCI by 60%" (discussion); no class stated |
| Risner 2021 [S6] | Explicitly a "minimum" capital estimate; "a Lang factor of 2 is considered to be low ... for a brand new facility" |
| Risner 2023 [S38] | One-at-a-time +/-25% sensitivity; excludes land, working capital, start-up |
| Negulescu 2023 [S3] | No accuracy statement found in the main text |
| BCG/Synonym [S36] | No range; "Standardization can reduce the capital investment for later biofoundries by up to 30%" |
| Believer (realised vs plan) [S14, S16] | $123.35M announced -> ~$154M reported = +25% on the announced figure (GFI says +11% vs "initial projections", implying an internal baseline of ~$139M `[inferred]`). The only realised-vs-estimate data point found |

---

## (c) Sources

Local files are in the session scratchpad (`.../scratchpad/tea/`, `dl/`, `pas/`); originals in `~/Documents/Cultivated_meat_TEAs/`.

- [S1] Humbird, D. (2021) "Scale-up economics for cultured meat: techno-economic analysis and due diligence" (long report). `dl/pre.txt` (= `tea/Humbird21Cultivated.txt`). Table 3.1 (Lang factors), Table 3.2 (building $/m2, 2018$), Table 3.3 (bioreactor costs), Tables 4.1-4.3 (fed-batch), Tables 4.8-4.10 (perfusion), Appendix A Tables A.1, A.5 (yeast), sect. 1 accuracy remark.
- [S2] Vergeer, Sinke, Odegard (CE Delft, 2021) "TEA of cultivated meat", report 190254. `tea/Delft21Cultivated.txt`. Sect. 2.3.1-2.3.2, Table 2, Figure 10, Annex C.
- [S3] Negulescu et al. (2023) Biotechnol. Bioeng. 120:1055, doi 10.1002/bit.28324. `tea/Negulescu22Technoeconomic.txt`. Sect. 2.3, Tables 1-2. (SI Tables S3-S4 not available locally.)
- [S4] Garrison, Biermacher, Brorsen (2022) J. Agric. Food Res. 10:100358. `tea/Garrison22How.txt`. Sect. 2.3.1-2.3.3.
- [S5] Pasitka et al. (2024) Nature Food, doi 10.1038/s43016-024-01022-w. `pas/p.txt` (main), `dl/si1.txt` (Supplementary Tables S1-S4, S8-S10).
- [S6] Risner et al. (2021) Foods 10:3. `tea/Risner21Preliminary.txt`. Sect. 2.1, Table 2, discussion.
- [S7] Ashizawa et al. (2022) Foods. `tea/Ashizawa22Entomoculture.txt`. Methods (bioreactor cost: $50,000/m3, 0.6 exponent, 1.29, Lang 2).
- [S8] Lever VC (2025) "A Second Generation of Cultivated Meat Companies Breaks Through". `tea/Lever25Insights.txt`.
- [S9] Quint / Ark Biotech (2023) "Cultivated meat's path to price parity". `tea/Quint23Cultivated.txt`.
- [S10] SuperMeat (2024) "Cultivating the Future". `tea/Supermeat24Cultivating.txt`.
- [S11] Gu et al. (2025). `tea/Gu25Scaling.txt`. [S12] Goodwin et al. (2024) Nature Food review. `tea/Goodwin24Review.txt` (Table 1). [S13] GFI (2021) anticipatory LCA/TEA summary. `tea/GFI21Anticipatory.txt`.
- [S14] Believer groundbreaking, $123.35M, 200,000 sq ft, >= 10,000 t (company announcement): https://www.foodnavigator-usa.com/Article/2022/12/08/BELIEVER-Meats-breaks-ground-on-largest-cultivated-meat-production-center-in-the-world-in-North-Carolina ; https://www.fooddive.com/news/believer-meats-commercial-scale-cultivated-meat-groundbreaking-future-meat-technologies/638263/
- [S15] AgFunder, UPSIDE $50M stalking-horse bid; BDO teaser "Over $150 million invested"; Gray Construction claim $36.4M; "20,000-L scale" (journalist's understanding): https://agfundernews.com/exclusive-upside-foods-submits-50m-stalking-horse-bid-for-believer-meats-us-cultivated-meat-facility
- [S16] GFI, 2026 State of the Industry: Cultivated meat, seafood and ingredients. `tea/GFI_2026-State-of-the-Industry-report-...txt`, lines ~1415-1424 (Believer $154M) and ~1497-1500 (Vow -80%, Meatly -95%).
- [S17] AgFunder, "What went wrong at Believer Meats?" (vessel sizes 50 L to 20,000 L): https://agfundernews.com/what-went-wrong-at-believer-meats-sources-point-to-risk-scale-and-timing
- [S18] Believer Phase 1 completion (Oct 2025): https://www.tradeandindustrydev.com/region/north-carolina/news/nc-believer-meats-completes-wilson-manufacturing-35035
- [S19] UPSIDE EPIC (53,000 sq ft; 50,000 lb -> 400,000 lb): https://www.fooddive.com/news/upside-foods-cultivated-cell-based-meat-plant-epic/609182/ ; 2,000 L cultivators: https://agfundernews.com/upside-foods-large-scale-cultivated-meat-plant-on-hold-until-it-delivers-key-proof-points-at-smaller-site
- [S20] UPSIDE Glenview $140M, 187,000 sq ft, up to 100,000 L: https://agfundernews.com/upside-foods-to-pump-140m-into-commercial-scale-cultivated-meat-plant-near-chicago
- [S21] GOOD Meat / ABEC 10 x 250,000 L, 30M lb (company announcement): https://foodnavigator-usa.com/Article/2022/05/25/GOOD-Meat-plans-US-cultivated-meat-facility-with-capacity-to-produce-up-to-30m-lbs-of-meat ; https://www.businesswire.com/news/home/20220525005345/en
- [S22] Vow 20,000 L vessel "well under $1 million", "under 14 weeks" (CEO claim): https://agfundernews.com/humbird-was-spectacularly-wrong-on-cultivated-meat-economics-says-report-as-vow-predicts-it-will-soon-be-unit-margin-positive
- [S23] Vow output with the 20,000 L vessel: https://thespoon.tech/vow-get-greenlight-in-australia-as-it-hits-1200-pounds-per-week-of-cultivated-quail/
- [S24] BlueNalu 8 x 100,000 L, 6M lb, ~140,000 sq ft (company press release): https://www.bluenalu.com/press-releases/bluenalu-cracks-the-code-to-significant-profitability-in-first-large-scale-facility
- [S25] Mosa Meat Maastricht, 1,000 L, 2,760 m2: https://agfundernews.com/mosa-meat-opens-facility-sees-a-clear-path-towards-price-parity
- [S26] Ivy Farm pilot, 600 L, 2.8 t/yr: https://agfundernews.com/uks-ivy-farm-opens-the-largest-cultivated-meat-pilot-plant-in-europe
- [S27] Meatable Leiden pilot: https://www.just-food.com/news/cultivated-meat-company-meatable-ups-capacity-with-new-facility
- [S28] Aleph Farms: https://www.businesswire.com/news/home/20230228005341/en ; https://agfundernews.com/aleph-farms-partners-with-bbgi-fermbox-bio-in-thailand-as-part-of-step-by-step-de-risking-process-for-cultivated-meat
- [S29] Liberation Labs $115M / 600,000 L (company): https://www.ibj.com/articles/maker-of-alternative-proteins-taps-richmond-for-115m-fermentation-plant ; https://agfundernews.com/liberation-labs-bags-25m-usda-backed-loan-to-fund-us-biomanufacturing-hub-what-matters-is-whether-the-capacity-is-fit-for-purpose
- [S30] Liberation Labs financing and timeline: https://www.greenqueen.com.hk/liberation-labs-precision-fermentation-facility-saudi-arabia-funding/
- [S31] Moore, Robson, Trinci, "21st Century Guidebook to Fungi", sect. 17.18 (155 m3 airlift; GBP 37.5M each): https://davidmoore.org.uk/21st_century_guidebook_to_fungi_platinum/Ch17_18.htm ; tower heights: https://microbiologysociety.org/resource/mycoprotein-production-and-food-sustainability.html
- [S32] Quorn GBP 30M third fermenter: https://www.foodnavigator.com/Article/2014/04/25/Meat-free-demand-prompts-30M-injection-at-Quorn-Foods/ ; https://www.foodmanufacture.co.uk/Article/2015/09/07/Quorn-boosts-production-by-50-as-US-sales-surge/ ; https://www.foodmanufacture.co.uk/Article/2015/02/11/Meat-free-firm-s-investment-for-growth/
- [S33] Quorn GBP 150M, +20,000 t, GBP 27M forming building: https://www.just-food.com/news/quorn-to-spend-gbp150m-to-increase-production-at-uk-plant ; https://www.foodnavigator.com/Article/2018/11/15/Quorn-opens-world-s-biggest-meat-alternative-production-facility
- [S34] Solar Foods Factory 01 (EUR 42M; 20,000 L; 160 t/yr): https://solarfoods.com/factory-01-press-kit/ ; https://solarfoods.com/factory/ ; https://www.inderes.fi/en/releases/solar-foods-factory-01-has-reached-its-productivity-targets
- [S35] ENOUGH Sas van Gent (EUR 42M; 10,000 t/yr): https://www.agro-chemistry.com/news/worlds-largest-protein-plant-to-be-build-in-the-netherlands/ ; https://www.cbe.europa.eu/achievements/flagship-biorefinery-makes-much-needed-non-animal-protein
- [S36] BCG x Synonym (2024) "Breaking the cost barrier on biomanufacturing": https://www.bcg.com/publications/2024/breaking-the-cost-barrier-on-biomanufacturing
- [S37] Cauldron CEO interview (AgFunder): https://agfundernews.com/%f0%9f%8e%a5cauldron-on-precision-fermentation-a-continuous-process-will-unlock-cost-of-goods-for-low-value-high-volume-products
- [S38] Risner et al. (2023) Front. Sustain. Food Syst. 7:1204307: https://www.frontiersin.org/articles/10.3389/fsufs.2023.1204307/full
- Capacity census (no capex): GFI fermentation manufacturing capacity analysis, https://gfi.org/fermentation-manufacturing ; Synonym State of Global Fermentation (Nov 2023), coverage at https://vegconomist.com/fermentation/fermentation-report-scaling-not-only-solution-price-parity-animal-products/

---

## (d) What could not be found, and caveats

1. No built animal-cell plant publishes both capital and production vessel volume. Believer's bioreactor count is not in the court documents or press; the ~$665k/m3 figure is my back-calculation from claimed capacity and Pasitka's yield, not data.
2. UPSIDE EPIC build cost: not found (do not cite "$50M" as the plant cost; $50M in the 2025-26 press is UPSIDE's bid for Believer's plant).
3. GOOD Meat/ABEC contract value, Vow Factory 2 total, Mosa, Aleph, Wildtype, BlueNalu, Meatable, Ivy Farm capital: not disclosed.
4. Liberation Labs: the "4 x 150 m3" configuration was not confirmed by any retrieved source (only "600,000 liters"); no post-2023 cost update found although start-up slipped ~2 years, so $115M is likely a floor (my estimate: ~65% probability the final cost exceeds $115M by >15%).
5. Quorn: the news items on the GBP 30M fermenter do not state its volume (155 m3 is inferred from the "twin" description in the textbook); the GBP 37.5M figure is from a textbook, not company accounts. The model's "$190k/m3 (Quorn)" therefore rests on GBP figures of different vintages; in the source currency it is GBP 194-242k/m3.
6. ENOUGH fermenter volume; Nature's Fynd, Perfect Day, The Every Co. plant capital: not found.
7. Synonym "State of Global Fermentation" and GFI capacity reports: capacity counts only; no public $/L capex benchmark located. The BCG/Cauldron per-m3 values are my division of their round numbers.
8. Negulescu SI (Tables S3-S4: equipment list, what CAPEX includes) and the Risner 2023 appendix were not read; the per-facility bioreactor counts for both are inferred.
9. Humbird does not tabulate the yeast plant by area; the right-hand column of section (b) below TPEC is reconstructed from the Lang factor and Table 3.1.
10. CE Delft volume basis is ambiguous (proliferation STRs vs perfusion "production" reactors); both are given. Price years for CE Delft, Garrison, Negulescu and Pasitka are not stated explicitly.
