# Post-harvest costs: evidence for the $5/kg markup and the $6/kg scaffold assumption

Compiled 2026-11-14 from a bounded web search (about 45 tool calls). Every number is quoted as the source states it, then converted. Conversions and inferences that are mine are marked **[conv]** or **[inference]**.

Access levels:

- **FT** = read in the full text (or the full data file).
- **PART** = full text opened but only partly read (long page truncated by the fetch tool).
- **SNIP** = seen only in a search-engine snippet; verify before publishing.
- **PRESS** = company claim or trade press, not peer-reviewed.

Unit conversion used throughout: 1 cent/lb = $0.022046/kg (1 kg = 2.2046 lb).

Model assumptions under test: `markup_add` = $5/kg (additive, biomass to retail) and `SCAF` = $6/kg (0.2 kg scaffold/kg x $5/kg material + $5/kg process).

---

## 1. Conventional meat price spreads

### 1a. USDA ERS Meat Price Spreads, annual, cents per lb of retail equivalent [1][2]

Basis: all values are "measured in cents per pound of retail weight" [3]. Farm-to-wholesale spread = "Wholesale value minus net farm value"; wholesale-to-retail spread = "Retail value minus wholesale value"; wholesale value = "Average value of the meat as it leaves the packing plant" [3]. Conversion factors: "2.40 pounds of the standard steer to produce a pound of retail beef", "1.14 pounds of wholesale beef to produce 1 pound of retail beef"; pork 1.869 lb hog and 1.04 lb wholesale cuts per lb retail [3]. The documentation page does not itemise what the spreads cover; by construction farm-to-wholesale is slaughter and packing (net of by-product credit) and wholesale-to-retail is everything from packer dock to shelf (transport, cold chain, cutting and trimming loss from wholesale to retail weight, packaging, shrink, retailer costs and profit) **[inference]**.

| Species, year | Retail value | Wholesale value | Net farm value | Farm-to-wholesale | Wholesale-to-retail | Total farm-to-retail | [conv] W-to-R, $/kg retail | [conv] total, $/kg retail | W-to-R as % of retail | Access |
|---|---|---|---|---|---|---|---|---|---|---|
| Choice beef 2023 | 798.3 | 452.9 | 381.8 | 71.1 | 345.4 | 416.5 | 345.4 x 0.022046 = 7.61 | 9.18 | 43% | FT [1] |
| Choice beef 2024 | 823.5 | 468.7 | 413.3 | 55.4 | 354.8 | 410.2 | 7.82 | 9.04 | 43% | FT [1] |
| Choice beef 2025 | 938.0 | 544.5 | 501.6 | 42.9 | 393.5 | 436.4 | 8.68 | 9.62 | 42% | FT [1] |
| Pork 2023 | 480.9 | 166.8 | 99.3 | 67.5 (see note) | 314.1 | 381.6 | 6.92 | 8.41 | 65% | FT [2] |
| Pork 2024 | 487.3 | 179.2 | 106.4 | 72.8 (see note) | 308.1 | 380.9 | 6.79 | 8.40 | 63% | FT [2] |
| Pork 2025 | 494.7 | 195.8 | 118.7 | 77.1 (see note) | 298.9 | 376.0 | 6.59 | 8.29 | 60% | FT [2] |

Note on pork farm-to-wholesale: the fetch tool returned a "farm-to-wholesale" row of 14.0 / 14.9 / 15.6 for 2023-25, which does not equal wholesale minus net farm value. The values in the table are **[conv]** wholesale minus net farm (e.g. 195.8 - 118.7 = 77.1). The 2026 monthly file [4] gives 39-64 cents/lb, consistent with the recomputed figure, not with 15. **Open the CSV and check that row before citing.**

### 1b. ERS monthly, May to October 2026 [4] (FT, data file)

| Series | Range, cents/lb | [conv] $/kg retail |
|---|---|---|
| Choice beef retail value | 994.4 - 1048.7 | 21.92 - 23.12 |
| Beef farm-to-wholesale | 6.5 - 70.9 | 0.14 - 1.56 |
| Beef wholesale-to-retail | 432.8 - 491.1 | 9.54 - 10.83 |
| Pork retail value | 485.5 - 494.1 | 10.70 - 10.89 |
| Pork farm-to-wholesale | 39.3 - 64.0 | 0.87 - 1.41 |
| Pork wholesale-to-retail | 306.1 - 353.6 | 6.75 - 7.80 |
| Retail broiler composite | 237.0 - 243.9 | 5.22 - 5.38 |
| Wholesale-retail broiler spread ("Cents per pound, retail weight") | 137.2 - 150.1 | 3.02 - 3.31 |

Broilers have no farm price (integrator contracts), so ERS reports only the wholesale-to-retail spread [3]. [conv] Broiler spread as share of retail: 150/243.9 = 61%.

Broilers 2025: monthly spread 121.4 - 164.5 cents/lb, my average of 12 months 139.3 cents/lb = [conv] $3.07/kg. Source is a third-party republication of the ERS series [5], not checked against the ERS historical file (SNIP-grade).

### 1c. What this says about the $5/kg markup

- If harvested cell mass is treated as the analogue of boneless meat leaving the packing plant, the relevant comparator is the **wholesale-to-retail** spread: $3.0-3.3/kg (broilers), $6.6-7.8/kg (pork), $7.6-10.8/kg (beef), 2023-2026.
- The spread is closer to proportional than flat: 42-43% of retail for beef, 60-65% for pork, about 61% for broilers.
- These are whole-carcass, mostly whole-cut baskets. They are not the spread for ground or formed product. **Not found**: an ERS (or other) spread specific to ground beef, sausage or nuggets.

### 1d. EU

| Item | As stated | [conv] | Access |
|---|---|---|---|
| France, OFPM 2026 report (2025 data): beef "panier saisonnier" in supermarkets | Of 100 EUR spent: 63.4 raw material, 24.8 large retail, 11.9 slaughter and cutting. Basket price 14.43 EUR (2024) to 15.83 EUR (2025); unit not stated in the snippet, probably EUR/kg | Retail gross margin 0.248 x 15.83 = 3.93 EUR/kg; slaughter-cutting 0.119 x 15.83 = 1.88 EUR/kg; sum 5.81 EUR/kg | SNIP of trade press on [6] |
| France, OFPM 2025 report: Label Rouge ready-to-cook chicken retail price | 6.46 EUR/kg in 2024 | Margin split not retrieved | SNIP [6] |
| EU-wide farm/processing/retail split for meat | **Not found.** DG AGRI dashboards give farm-level prices only | | |

---

## 2. Further processing, packaging, cold chain, retailer margin

| Item | As stated | [conv] $/kg product | Year | Access / quality |
|---|---|---|---|---|
| Humbird: bulk cell mass to supermarket | "After further processing, packaging, distribution, and profit, unstructured products made 100% from bulk cell mass at $25/kg might be expected to reach a minimum of $50/kg at the supermarket." | Implied post-harvest add-on of at least $25/kg at a $25/kg input, i.e. a 100% markup (multiplicative, not a flat $5). No derivation given | 2021 | FT [7]. Author judgement, not a costed estimate |
| US grocery store gross margin, all departments (Census Annual Retail Trade Survey) | 28.0% of sales in 2022, 27.3% in 2021 | On a $10/kg shelf price: 0.28 x 10 = $2.80/kg; on $20/kg: $5.60/kg | 2022 | SNIP, via a blog citing Census [8]. Pull ARTS directly before citing |
| Frozen food department gross margin (USDA ERS-235, eight departments) | "gross margins around 25.6% of sales" | On $10/kg: $2.56/kg | Old report; date not retrieved (ERS-235 series is 1960s) | SNIP [9] |
| Meat department gross margin | 25-30%, 28-35%, 30-40% in three consultant/blog guides | On $10/kg: $2.5-4.0/kg | 2025-26 | SNIP, unsourced blogs. Weak |
| Custom (small-plant) grinding fee | "$.50 per pound" and "$1.10 per lb" in two 2024 price sheets; "70 to 90 cents per pound, hanging weight" | $1.10-2.43/kg | 2024 | SNIP. Small custom processors, an upper bound for industrial cost |
| Custom patty forming | about "$1.25 per lb" (10 lb minimum) | $2.76/kg | 2024 | SNIP. Small custom processor, upper bound |
| Chicken nugget manufacturing cost | "around $0.50" per pound | $1.10/kg | undated | SNIP, unsourced consumer site. Do not cite |
| Plant-based patty: distribution and storage | "around $0.41 per unit" (raw materials "$3.54" per serving; Zhong et al. 2023 as cited in an HME review) | Not convertible: patty mass not retrieved | 2023 | SNIP |
| Industrial cost of grinding/forming/breading per kg (USDA or academic) | **Not found** | | | |
| Packaging cost per kg for fresh or frozen meat | **Not found** | | | |
| Refrigerated/frozen distribution cost per kg | **Not found** (only the per-unit figure above) | | | |
| Retailer gross margin for fresh vs frozen meat from a primary source (FMI, Progressive Grocer, Cornell) | **Not found** | | | |

---

## 3. Plant-based meat manufacturing and filler ingredients

### 3a. GFI 2021, "Plant-based meat: Anticipating 2030 production requirements" [10] (FT, PDF text extracted)

Model facilities, "24 hours per day, seven days a week, 350 days per year at 85% of maximum potential throughput capacity". [conv] Annual output = kg/h x 24 x 350 x 0.85 = kg/h x 7,140.

Output is structured plant protein (SPP), not finished retail product. LME = low-moisture (dry) extrudate, HME = high-moisture. Miscellaneous "include property tax, rent (if the space is leased), and the cost of packaging and shipping materials". Raw material costs "extrapolated from bulk retail prices of commercial vendors at online marketplaces (e.g., Alibaba)". The report says opex excludes maintenance, fringe benefits and minor items, so is understated.

| | A: medium LME | B: large LME | C: medium HME | D: large HME |
|---|---|---|---|---|
| Throughput, kg/h (Sec. 3.1) | 1,000 | 10,000 | 1,000 | 10,000 |
| [conv] Output, t/yr | 7,140 | 71,400 | 7,140 | 71,400 |
| Total CapEx, $M (Table 4) | 12.7 | 60.2 | 18.2 | 91.2 |
| of which extrusion lines, $M | 2.0 | 16.0 | 4.9 | 36.0 |
| Opex: electricity, $M/yr (Table 5) | 0.3 | 1.8 | 0.9 | 4.4 |
| Opex: raw materials, $M/yr | 4.2 | 21.0 | 10.2 | 51.3 |
| Opex: labor, $M/yr | 6.1 | 11.0 | 6.1 | 11.0 |
| Opex: miscellaneous, $M/yr | 2.2 | 4.9 | 2.5 | 6.6 |
| Total opex, $M/yr | 12.8 | 38.7 | 19.7 | 73.4 |
| [conv] Total opex, $/kg SPP | 12.8/7.14 = 1.79 | 0.54 | 2.76 | 1.03 |
| [conv] Raw materials, $/kg SPP | 0.59 | 0.29 | 1.43 | 0.72 |
| [conv] **Conversion opex excl. raw materials, $/kg SPP** | (12.8-4.2)/7.14 = **1.20** | **0.25** | **1.33** | **0.31** |
| [conv] CapEx per annual kg, $ | 1.78 | 0.84 | 2.55 | 1.28 |
| [conv] Capital charge at 10%/yr of CapEx (my assumption), $/kg | 0.18 | 0.08 | 0.25 | 0.13 |
| [conv] **Conversion cost incl. capital charge, $/kg SPP** | **1.38** | **0.33** | **1.58** | **0.44** |

Caveats: 2021 dollars; "directional and order-of-magnitude"; the implied raw-material cost per kg differs twofold between A and B, which the report does not explain. Industry aggregate: "$27B" CapEx and "at least $17B" annual opex for 25 MMT, [conv] 17/25 = $0.68/kg all-in opex including raw materials.

### 3b. Ingredient prices

| Ingredient | As stated | [conv] $/kg ingredient | Year | Access / quality |
|---|---|---|---|---|
| Textured vegetable protein, global trade unit values (Tridge customs data) | 2023: "$1.36 USD per kg and $6.42 USD per kg"; 2024: "$0.89 to $5.59 USD per kg"; Turkey imports "$0.50 USD and $1.30 USD per kg" | 0.5 - 5.6 (dry TVP; hydrates roughly 1:2 to 1:3, so per kg hydrated is about a third: my general knowledge, not sourced) | 2023-24 | SNIP [11]. Mixed grades |
| Soy protein isolate | $2.50 - 4.20/kg | same | 2026 | SNIP, equipment-vendor blog [12]. Weak |
| Soy protein concentrate | $1.50 - 2.20/kg | same | 2026 | SNIP [12]. Weak |
| Defatted soy flour | $0.80 - 1.20/kg | same | 2026 | SNIP [12]. Weak |
| Plant protein concentrates (soy, pea), GFI meta-analysis | median "around $6.00 per kg of protein" | At 65-70% protein: about $3.9-4.2/kg concentrate **[conv, my protein-content assumption]** | not retrieved | SNIP, secondary report of a GFI analysis [13] |
| Pea protein isolate price | **Not found** | | | |

### 3c. Not found

- Co-manufacturing / tolling fees per kg for extrusion or forming: **not found** in any public source searched.
- GFI Europe / Bright Green Partners per-kg cost breakdown: **not found**. Their public capacity study [14] covers capacity, not unit costs.
- GFI "Reducing the price of alternative proteins" (2022) [15] (FT): has a sample cost-composition chart ("Sample cost drivers on a per-unit-sold basis", a GFI estimate) but the numbers are in an image and were not extractable; the text gives only qualitative outlooks per cost line.
- Academic TEA of high-moisture extrusion with $/kg: **not found**. One freeze-alignment (not extrusion) TEA reports raw materials about 32% and labor about 24% of production cost (SNIP, via an HME review).

---

## 4. Cultivated meat downstream

| Source | What it says | [conv] $/kg final product | Access |
|---|---|---|---|
| Humbird 2021 [7]: harvest | "Upon harvest, the cell mass is dewatered to 20% solids in a disk-stack centrifuge." Dewatering capital in Table 2: $4M (fed-batch), $2M (perfusion). Cost basis is "$37/kg wet cell mass" for facilities "that produce bulk animal cell mass" | Dewatering is inside the $37/kg. [inference] $4M over roughly 6.8 kt/yr (facility output recalled from memory, not re-read) is about $0.6 per annual kg, i.e. under $0.1/kg at a 15% capital charge. Verify output before citing | FT |
| Humbird 2021 [7]: after the bioreactor | Nothing past dewatering is costed. Further processing, packaging, distribution, profit are named only in the "$25/kg ... minimum of $50/kg at the supermarket" sentence. Scaffolds: "Advanced concepts propose to deposit cultured animal cells onto an edible scaffold that provides form." No cost | None given for structuring | FT |
| CE Delft 2021 TEA [16]: scope | Product is "a slurry or paste made out of meat cells (comparable to very finely ground meat) suitable for further formulation". Water "70% (baseline) to 77%". "Costs for packaging and transportation to the food-processing industry are not included." "Further formulation, processing, packaging and post-production transport are outside the scope." Included stages list "harvesting and food safety measures". Excluded: "centrifuge for recycling media; cell banking system; air (elevated concentration of CO2)" | Harvesting cost is a visible bar in the figures but the $/kg value was not read off | FT (PDF text) |
| CE Delft 2021 TEA [16]: scaffolds | "Harvested cells are seeded onto scaffolds in perfusion reactors (PR)", 4 PRs of 2,000 L per line. Annex price table: "Scaffolds, Hydrogel (not electrospun), $/ton 135, Data from various experts." Scaffold quantity from 8 companies, confidential | Scaffold material $0.135/kg of hydrogel. The companion LCA is reported to use 0.1 kg plant-based scaffold (per kg product; SNIP of the GFI summary, basis not verified): 0.1 x 0.135 = **$0.014/kg product**. Scaffolds are a line in the COGS bars but far too small to read | FT for price; SNIP for quantity |
| Bomkamp et al. 2022, Adv. Sci. [17] | Table 5 design criteria: scaffold cost "ideally <USD $0.10 per kg of final product at scale"; scaffolding "perhaps <5% of the production cost"; benchmark "commodity meat prices of approximately USD $2 per kg". Perfusion bioreactors "will likely contribute substantially to the overall cost of production of CM, with sterility maintenance acting as a major cost driver" (no figure) | Target, not an estimate: **<$0.10/kg product**. No material price list, no scaffold mass fraction, no fabrication cost found in the first 200,000 of 418,000 characters | PART |
| Gelatex (company) | Currently available scaffolding materials "a huge €100,000 per kilogram"; its nanofibre material could reach "€1000 per kilogram" | Per kg of scaffold, not of product; mass fraction not given, so not convertible. At an illustrative 1% inclusion: 10 EUR/kg product **[inference, illustrative only]** | SNIP, PRESS [18] |
| Pasitka et al. 2024, Nature Food (Believer) | "$6.20 (€5.60) per pound (0.45kg)"; a third-party comparison says this is for a 50/50 hybrid, with pure cell mass at $13.75-22.27/kg | 6.20 x 2.2046 = $13.67/kg of hybrid product. No separate downstream line | SNIP [19][20] |
| Garrison et al. 2022, J. Agric. Food Res. [21] | "$63/kg" in a "$60 million" facility producing "540,000 kg" per year; includes "cold storage infrastructure"; medium, bioreactors and labor "over 80%" | Scaffold/macrocarrier and post-harvest lines: **not retrieved** (ScienceDirect returned 403) | SNIP / ABS |
| Risner et al. 2021 | "limit[s] our analysis here to the core bioreactor system, leaving out industrial-scale scaffolding and processing" | Nothing | SNIP |
| Rethink Priorities TEA comparison | The TEAs "do not investigate the question of scaffolding (converting cell slurry into structured meat products)" | Nothing | SNIP [22] |
| Gu et al. 2025, CRFSFS e70221 [23] | Review; names scaffold fabrication as one of four cost levers | No scaffold $/kg seen in snippets; full text (PMC12241508) not opened | SNIP |
| GFI "Cultivated meat end products" deep dive [24] | Qualitative: "substantial amounts of scaffold material" may remain in the product. No cost figures for scaffolding, extrusion, bioprinting or post-harvest processing | Nothing | FT |
| Hollow-fibre TEA (Cellular Agriculture Ltd, in RAU "Culture Clash" Appendix 1, 2024) [25] | Model built on a proprietary hollow-fibre bioprocess; "140 L/kg" media | Total or structuring cost per kg not seen | SNIP |

Bottom-up check of the model's decomposition **[inference]**: at the model's 0.2 kg scaffold per kg product, a TVP or soy-concentrate scaffold at $0.9-4.2/kg (3b) is 0.2 x 0.9 to 0.2 x 4.2 = $0.18-0.84/kg product, against the model's 0.2 x 5 = $1.00. If the "process" step resembled HME texturising, 3a gives $0.3-1.6/kg, against the model's $5.00. Neither figure covers a perfusion or tissue bioreactor stage for a thick cut, for which no costing was found.

---

## 5. Cell content of commercial or approved products

| Company, product, market | Cell content as stated | Balance | Year | Access / quality |
|---|---|---|---|---|
| Eat Just / GOOD Meat, "GOOD Meat 3", retail, Singapore (Huber's) | "3% cultivated chicken" | Plant proteins (97%) | 2024 | Trade press [26]. PRESS |
| Eat Just / GOOD Meat, earlier foodservice chicken, Singapore | "70% chicken cells" | 30% plant material "to reduce costs and provide structure" | about 2020-23 | GFI page citing MeatPoultry [24]. PRESS |
| GOOD Meat, US-approved chicken | **Not found** | | | |
| Upside Foods, Chicken Filet, US | "over 99% cultivated chicken cells"; label: "Cell-cultivated chicken, Maltodextrin, Transglutaminase (Binding Agent)" | <1% binders | 2023 | Company site and trade press [27]. PRESS; USDA label not read |
| Upside Foods, ground / "Chicken Essentials" line | Blended with plant ingredients incl. soy protein; percent **not found**; was pending review | | undated | Company site. PRESS |
| Vow, Forged Parfait, Singapore | "cultured Japanese quail (60%)" | Butter, shallot, tapioca starch, wines, etc. | 2024 | Trade press quoting the ingredient list [28]. PRESS |
| Vow, Smoked Cultured Quail Spread, Australia | "40% cultivated meat" | Unsalted butter (main), water, glucose, salt | 2025 | Trade press [29]. PRESS |
| Vow, Forged Gras, Australia/Singapore | "51%" cultured quail | Not listed | 2025 | Trade press [29]. PRESS |
| Aleph Farms, Aleph Cuts (approved Israel; not yet sold at retail) | Cell inclusion "between 10% and 20%" | Soy and wheat protein matrix | 2024-25 | Company statement via trade press [30]. PRESS |
| Wildtype, salmon saku, US | Cells are "the first ingredient in our salmon (after water)"; percent not disclosed | Plant-based ingredients / scaffold | 2025 | Company FAQ [31]. PRESS |
| Mission Barns, meatballs and bacon, US | "small amounts of cultivated pork fat"; percent not disclosed. FDA memo: harvested cell material "an average of 5.85% total fat" (describes the cell material, not the product) | Pea protein base | 2025 | Trade press; FDA memo. SNIP |
| Believer Meats | 50/50 hybrid implied by the Pasitka cost basis [20]; commercial product percent **not found** | | | SNIP |
| SCiFi Foods (never commercialised) | "<20% cultivated beef cells" planned | Plant-based burger | 2022 | GFI page citing FoodNavigator [24]. PRESS |
| SuperMeat sensory work (not a product) | "as little as 5% cultured hepatocytes" improved plant-based meat; 13% as good as 27% for sausage/schnitzel | | | GFI page citing a patent analysis [24] |

Read-across: products sold so far span 3% to over 99% cells; the only whole-cut-style product with a disclosed scaffold (Aleph) is 10-20% cells on 80-90% textured plant protein. The model's 0.2 kg scaffold per kg product is the inverse of the one disclosed scaffolded product.

---

## Sources

1. USDA ERS, Meat Price Spreads, "Choice beef values and spreads and the all-fresh retail value" (CSV, updated 2026-11-10). https://ers.usda.gov/media/5020/choice-beef-values-and-spreads-and-the-all-fresh-retail-value.csv?v=37414
2. USDA ERS, Meat Price Spreads, "Pork values and spreads" (CSV, updated 2026-11-10). https://ers.usda.gov/media/5026/pork-values-and-spreads.csv?v=73278
3. USDA ERS, Meat Price Spreads, Documentation. https://ers.usda.gov/data-products/meat-price-spreads/documentation
4. USDA ERS, Meat Price Spreads, "Summary of retail prices and price spreads" (CSV, updated 2026-11-10). https://ers.usda.gov/media/5025/summary-of-retail-prices-and-price-spreads.csv?v=25460 (landing page: https://ers.usda.gov/data-products/meat-price-spreads)
5. ProteinReport, "U.S. Meat Price Spreads" (republishes ERS). https://www.proteinreport.org/data/prices/us-meat-price-spreads
6. Observatoire de la formation des prix et des marges (FranceAgriMer), reports 2025 and 2026. https://observatoire-prixmarges.franceagrimer.fr/ ; trade summary: https://www.reussir.fr/bovins-viande/viande-bovine-les-marges-brutes-de-labattage-decoupe-ont-fondu-en-2025 ; poultry: https://www.reussir.fr/lesmarches/volaille-les-marges-sous-la-loupe-du-rapport-ofpm-2025
7. Humbird, D. (2021) "Scale-up economics for cultured meat", Biotechnol. Bioeng. 118, 3239. https://pmc.ncbi.nlm.nih.gov/articles/PMC8362201
8. Blog citing US Census Annual Retail Trade Survey grocery gross margin. https://www.tarostack.com/articles/grocery-store-profit-margins-by-department (primary: https://www.census.gov/programs-surveys/arts.html, not opened)
9. USDA ERS, ERS-235 (frozen food department margins). https://ageconsearch.umn.edu/record/320609/files/ERS-235.pdf
10. GFI (2021) "Plant-based meat: Anticipating 2030 production requirements". https://gfi.org/wp-content/uploads/2021/11/Plant-based-meat_-anticipating-2030-production-requirements.pdf
11. Tridge, TVP price data. https://dir.tridge.com/prices/textured-vegetable-protein-tvp
12. Loyal Food Machine, "Soy Protein Meat Production Cost: 2026 Budget Guide" (vendor blog). https://loyal-foodmachine.com/soy-protein-meat-production-cost/
13. Report of a GFI meta-analysis of protein costs. https://www.mycostories.com/post/gfi-meta-analysis-fermentation-protein-costs-are-closing-in-on-beef-and-pork
14. Bright Green Partners / GFI, "Plant-based meat manufacturing capacity and pathways for expansion". https://brightgreenpartners.com/plant-based-meat-manufacturing-capacity/
15. GFI (2022) "Reducing the price of alternative proteins". https://gfi.org/wp-content/uploads/2021/12/Reducing-the-price-of-alternative-proteins_GFI_2022.pdf
16. CE Delft (2021) "TEA of cultivated meat: Future projections of different scenarios" (corrigendum). https://gfieurope.org/wp-content/uploads/2022/04/CE_Delft_190254_TEA_of_Cultivated_Meat_FINAL_corrigendum.pdf ; GFI summary: https://gfi.org/wp-content/uploads/2021/03/cultured-meat-LCA-TEA-technical.pdf
17. Bomkamp, C. et al. (2022) "Scaffolding Biomaterials for 3D Cultivated Meat: Prospects and Challenges", Adv. Sci. 9, 2102908. https://pmc.ncbi.nlm.nih.gov/articles/PMC8787436
18. Vegconomist on Gelatex scaffolds. https://vegconomist.com/cultivated-cell-cultured-biotechnology/gelatex-cultivated-meat-scaffolds/
19. FoodNavigator on Pasitka et al. 2024. https://www.foodnavigator.com/Article/2024/09/03/Breakthrough-in-cultivated-meat-can-lower-production-costs
20. Unjournal, "TEA Comparison: What Do the Studies Actually Say?". https://unjournal.github.io/cm_pq_modeling/compare.html
21. Garrison, G., Biermacher, J., Brorsen, B.W. (2022) "How much will large-scale production of cell-cultured meat cost?", J. Agric. Food Res. 10, 100358. https://www.sciencedirect.com/science/article/pii/S2666154322000916
22. Rethink Priorities, "Cultured meat: a comparison of techno-economic analyses". https://rethinkpriorities.org/publications/cultured-meat-a-comparison-of-techno-economic-analyses
23. Gu, H. et al. (2025) "Scaling Cultured Meat: Challenges and Solutions for Affordable Mass Production", Compr. Rev. Food Sci. Food Saf. 24, e70221. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12241508/
24. GFI, "Deep dive: Cultivated meat end products". https://gfi.org/science/the-science-of-cultivated-meat/deep-dive-cultivated-meat-end-products/
25. Royal Agricultural University, "Culture Clash" Appendix 1 (July 2024). https://www.rau.ac.uk/sites/default/files/2024-07/Culture_Clash_July_2024_Appendix_1.pdf
26. FoodNavigator-Asia on GOOD Meat 3. https://foodnavigator-asia.com/Article/2024/05/21/expert-opinions-clash-over-good-meat-s-3-cultivated-chicken-launch-in-singapore
27. Upside Foods. https://upsidefoods.com/food ; https://upsidefoods.com/blog/upside-is-approved-for-sale-in-the-us-heres-what-you-need-to-know
28. Green Queen on Vow Forged Parfait. https://www.greenqueen.com.hk/vow-food-cultivated-quail-forged-parfait-george-peppou-singapore/
29. Green Queen / Vegconomist on Vow in Australia. https://www.greenqueen.com.hk/vow-cultured-quail-lab-grown-cultivated-meat-australia-forged ; https://vegconomist.com/retail-e-commerce/vow-introduces-australias-first-home-ready-cultured-meat-product-cultured-quail-sprad/
30. Aleph Farms inclusion rate. https://proteinproductiontechnology.com/post/what-comes-after-the-cultivated-meat-hype-didier-toubia-is-finding-out ; https://aleph-farms.com/faqs/
31. Wildtype FAQ. https://wildtypefoods.com/faqs/why-are-there-other-ingredients-besides-cells-in-wildtype-salmon

---

## What could not be found

1. Any published cost study (TEA) of structuring cultivated meat into a whole cut: scaffold fabrication, seeding, perfusion/tissue bioreactor, bioprinting, or extrusion of cell mass. Humbird, CE Delft, Risner and (per Rethink Priorities) the other TEAs stop at cell slurry. No Aleph Farms or Steakholder cost figure.
2. Scaffold material price lists ($/kg for alginate, gelatin, cellulose, mycelium, decellularised tissue) in a cultivated-meat source. Bomkamp gives a target only. CE Delft gives one hydrogel price ($135/t).
3. Scaffold mass per kg of product from a costed source. CE Delft's quantity is confidential; the 0.1 kg figure is a snippet.
4. Garrison et al. 2022 internal cost lines (paywall/403); Gu et al. 2025 full text not opened; Tuomisto TEA not searched.
5. A separate $/kg figure for harvest/dewatering in Humbird or CE Delft (both fold it into total COGS).
6. Industrial per-kg cost of grinding, forming, breading, packaging and refrigerated distribution for comminuted meat from USDA, academic or trade sources. Only small custom-processor fees were found.
7. Retailer gross margin for fresh vs frozen meat from a primary source; ERS spread for ground beef or processed products specifically.
8. Co-manufacturing / tolling fees for extrusion or forming; GFI Europe / Bright Green Partners unit-cost breakdown; an academic HME TEA; pea protein isolate price; the numbers in GFI's 2022 sample cost-composition chart.
9. EU-wide farm/processor/retailer split for meat; only a French (OFPM) beef split at snippet level.
10. Cell percentage for Wildtype, Mission Barns, Believer, GOOD Meat's US product and Upside's blended line.
11. ERS annual broiler series from the primary historical file (2025 figure here is from a third-party copy), and the pork farm-to-wholesale row needs rechecking in the CSV.
