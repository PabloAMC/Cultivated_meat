# What it costs to turn cells into a cut

> Names (2026-11-19): "Selected cells" was called Central; "Engineered cells, all favourable" was called the best case.

Date: 2026-11-19. Two bounded web searches (about 100 tool calls), building on `post_harvest_costs.md` (2026-11-14), which
found no costed source for structuring and is not repeated here. Access tags: FT full text, PART partly read, SNIP search
snippet only, PRESS company or trade press. [conv] marks a unit conversion of mine, [inference] a judgement of mine. Section 4 records
what the model adopted.

The model today: a cut costs a full kilo of cells plus $6 (0.2 kg of scaffold at $5/kg plus $5 of "process", the process figure
unsourced). Its kilo of wet cells is 30% dry matter (`gb_dry_per_wet`), firmer than muscle (about 25%), so dewatering is
already inside the cell cost.

## 1. There are two routes, and the industry has left the dearer one

| Route | What happens | Who |
|---|---|---|
| A. Assembly after harvest | Cells grown in suspension are harvested (no longer alive) and bound or textured with food ingredients | Wildtype since 2023, Aleph Farms since 2025, Upside's 2026 line, BlueNalu (cold extrusion) |
| B. Tissue grown on a scaffold | Harvested cells are seeded onto an edible scaffold and matured, for days to weeks, in a second, perfused bioreactor | Wildtype until 2023, Aleph until 2025, Upside's 2023 filet (adherent, 2 L roller bottles) |

- Wildtype's FDA memo (May 2025, FT): its 2022 process had "a maturation step occurring on a plant-based scaffold"; in 2023 it
  "changed its process to remove this maturation step", and cells "are combined with food ingredients post-harvest, when they
  are no longer viable".
- Aleph Farms (AgFunder, Mar 2025, FT) dropped the "second bioreactor where they are seeded onto plant-based scaffolds" to
  "remove costly steps and reduce media costs".
- Upside (AgFunder, Nov 2026, FT) replaced its two-vessel process with cells "grown in a single vessel" blended with soy
  protein, including a "chef's cut", at "a double-digit percentage" of cells.
- BlueNalu (AgFunder, Jun 2026, FT) avoids "pricy secondary bioreactors or scaffolding". Fork & Good makes ground meat.

The model's cells are grown in suspension, so route A is its route. Route B is costed in section 4 as an upper alternative.

## 2. Route A: what assembly costs

**Binders** (SNIP, dose × bulk price [conv]): transglutaminase $8–15/kg at 0.5–1.5%, $0.04–0.23/kg of product; sodium alginate
$10–15/kg at 0.5–1%, $0.05–0.15; methylcellulose $8–18/kg at 1–2%, $0.10–0.40. Upside's filet label: transglutaminase and
maltodextrin under 1%. Binder package about $0.1–0.6/kg [inference].

**Conversion** (forming, setting, cooking, freezing, slicing), from analogues, none of them a cultivated product:
- High-moisture extrusion of plant protein: $0.44–1.58/kg including capital (GFI 2021, in `post_harvest_costs.md` §3a).
- Surimi crab sticks: secondary processing about 25% of cost in Tridge's illustrative split (PART), about $1.0–1.3/kg at
  $4–5/kg ex-works [inference]; Alaska pollock surimi $2.39–2.77/kg (2023–24, SNIP).
- Printers: $100k at 10–100 kg/h is $0.03–0.25/kg of capital [conv]; labour, QA and yield dominate (PRESS).
- Beyond Meat, formed plant protein at under-used capacity: cost of goods $8.6–9.0/kg including ingredients (2024, SNIP).

**Matrix** (when plant protein is part of the cut): textured vegetable protein $0.5–5.6/kg dry (Tridge 2023–24, SNIP); soy
concentrate $1.5–2.2/kg (weak SNIP); structured plant protein from extrusion $0.7–2.8/kg all in [conv from GFI 2021].

**How many cells a cut can hold** is the open question, not the cost:
- Baeghbali et al. 2026, *Food Hydrocolloids* 172:112154 (FT): Ivy Farm cell paste (87.5% water) at 10% of an extrusion feed
  with pea protein made the fibres "largely disappear", while hardness and chewiness rose.
- A high-moisture-extrusion patent (ipiq 7156245, PART) claims 1–65% cells, with chicken-breast-like anisotropy at 35% when acid
  is added; no numbers given.
- Kim et al. 2024, *Food Sci. Anim. Resour.* 44(6) (PART): 10–30% freeze-dried chicken cells in wet-spun plant fibres gave shear
  force close to meat.
- Products with disclosed shares: Aleph Cuts 10–20% cells; Upside 2026 "double-digit"; Lever VC "low tens of percent"
  (Apr 2025, FT); Wildtype undisclosed, "the first ingredient after water", finished product 79.5% water and 4.4% protein
  (FDA memo, FT), so probably a minority of cells [inference].

No cut made mostly of suspension-grown cells has been shown. Every whole-cut product on sale or approved is a blend.

**Estimate for route A, structuring on top of the ingredients** [inference, first search agent]: low $1.0, central $3.0,
high $8.0 per kg of product. P(under $2) about 35%, P($2–5) about 45%, P(over $5) about 20%. Yield loss in forming and slicing
(5–15% of a $10–26 ingredient) may be the largest hidden term.

## 3. Route B: tissue grown on a scaffold

- CE Delft 2021 (FT): harvested cells "seeded onto scaffolds in perfusion reactors", 2,000 L working volume, 10-day runs;
  430 reactors at $600,000, $260M installed of $450M total capital for 10 kt/yr. [conv] 58% of capital; about $300/L against
  $115/L for its stirred tanks; $26 of capital per annual kg, $2.6–5.2/kg a year at a 10–20% charge, plus about $0.8 upkeep.
- Cellular Agriculture Ltd for RAU, July 2024 (FT): hollow fibres for every stage up to "final muscle tissue", 140 L/kg medium
  with about 70% regenerated; cost of goods £14.7–20.6/kg ($18.6–26.2 [conv]), structuring into product not costed. Company
  built, favourable medium prices, not reviewed.
- Gu et al. 2025, CRFSFS e70221 (PART): no structuring cost; synthetic scaffolds "under $10/kg", gels "up to $200/kg" (uncited);
  maturation runs of 10–60 days in the studies it reviews.
- Thickness: oxygen reaches about 280–400 µm into tissue at 10⁸ cells/mL [inference: √(2DC₀/q)], so a thick cut needs channels
  under about 0.7 mm apart (packed bed, hollow fibres).
- Scaffold material is cheap per kilo of meat: Ever After says under 2% of product weight (PRESS); at 2–30% and $1–13/kg it is
  $0.02–4, about $0.3–0.5 central [inference]. Only nanofibre at today's €1,000/kg (Gelatex) would matter.
- Ever After / Roslin claim 326 g/L wet in 9 days on an edible scaffold, 19× the protein productivity of stirred tanks (PRESS,
  unverified). If true, route B could replace suspension volume instead of adding to it.

**Estimate for route B, on top of suspension cells** [inference, second search agent]:

| | Low | Selected cells | High |
|---|---|---|---|
| Scaffold material | 0.05 | 0.5 | 3 |
| Maturation reactor capital and upkeep | 1.5 | 4 | 12 |
| Maturation medium (10–60 L/kg at $0.1–0.4/L) | 1 | 4 | 15 |
| Seeding, handling, labour, yield loss | 0.5 | 2 | 6 |
| **Total, $/kg of product** | **about 3–4** | **about 10** | **about 35** |

P(over $6) about 65%, P(over $20) about 20%, P(under $3) about 15%.

## 4. What this means for the model (adopted 2026-11-19)

1. **The cut's cost formula counted the scaffold on top of a full kilo of cells.** If 20% of a cut is matrix, a kilo of cut holds
   0.8 kg of cells: cost = 0.8 × cells + 0.2 × matrix + assembly (`price_ratio.structured_cost`).
2. **Assembly is charged beyond what mince already pays.** The shop add-on ($2.5 a kilo) already carries about $1 of dewatering,
   forming, packing and quality control for every product (`au_processing`). Route A's all-in estimate is $1–8, central $3, so the
   model takes **$2 (range $0.5–7)** on top. Matrix **$2 a kilo (1–5)**; cell share **0.8 (0.5–0.9)**.
3. **Route B is about $10 on top of the cells**, so the old $6 was too low for scaffold-grown tissue and too high for assembly.
4. **Cell share is the real uncertainty.** Products sold today are 10–30% cells; a cut that is 80% suspension cells has not been
   shown to have the texture of meat (BlueNalu says its toro will be all cells, not yet sold). A 20%-cell blend costs mostly plant
   protein, but is a different product for shoppers. The model keeps 0.8 by default and exposes it as a slider.
5. When cells cost more than about $12 a kilo a cut now costs less than mince, because a fifth of it is $2 plant protein.

Cut cost and the cell cost a cut needs for price parity (shelf = (cost + $2.5)/0.72) [conv]:

| | Before (cells + $6) | Now (0.8 cells + $0.4 + $2) |
|---|---|---|
| Selected cells cut, cells $26.43 | $32.43 | $23.54 |
| Best-case cut, cells $9.96 | $15.96 | $10.37 |
| Beef steak and cuts ($20.4): cells needed | $6.19 | $12.23 |
| Seafood fillet ($16.0): cells needed | $3.02 | $8.27 |
| Pork cuts ($9.0): cells needed | below zero | $1.97 |
| Chicken cuts ($8.0): cells needed | below zero | $1.07 |

## Sources

- FDA, Wildtype memo (May 2025): https://www.fda.gov/media/186753/download ; https://www.fda.gov/media/186754/download
- Baeghbali et al. 2026, Food Hydrocolloids 172:112154: https://mfic.gre.ac.uk/images/documents/publications/high-moisture-extrusion-based-texturization-functional-modulation-pea-protein-isolate-integration-cultivated-beef.pdf
- HME patent: https://ipiq.io/patents/7156245
- Kim et al. 2024: https://koreascience.kr/article/JAKO202432635894159.page
- Tridge, surimi supply chain: https://blog.tridge.com/blog-posts/alaska-pollock-surimi-supply-chain-how-product-actually-movesand-where-cost-quality-and-risk-get-locked-in
- Rival Foods shear cell: https://agfundernews.com/rival-foods-ramps-up-shear-cell-texturizing-tech-for-plant-based-whole-cuts
- CE Delft 2021 TEA: https://cedelft.eu/wp-content/uploads/sites/2/2021/02/CE_Delft_190254_TEA_of_Cultivated_Meat_FINAL_corrigendum.pdf
- Cellular Agriculture Ltd / RAU, Culture Clash Appendix 1: https://www.rau.ac.uk/sites/default/files/2024-07/Culture_Clash_July_2024_Appendix_1.pdf
- Gu et al. 2025: https://pmc.ncbi.nlm.nih.gov/articles/PMC12241508/
- Aleph Farms, Mar 2025: https://agfundernews.com/exclusive-aleph-farms-raises-30m-unveils-lower-cost-version-of-whole-cut-technology
- AgFunder deep dive, Jun 2026: https://agfundernews.com/cultivated-meat-deep-dive-after-the-crash-whos-still-standing
- Upside, Nov 2026: https://agfundernews.com/cultivated-meats-comeback-moment-upside-foods-unveils-dramatic-scale-up-eyes-fresh-funding
- Lever VC, Apr 2025: https://www.levervc.com/wp-content/uploads/2025/04/Lever-VC-A-Second-Generation-of-Cultivated-Meat-Companies-Breaks-Through-Projected-Cost-Barriers-4.pdf
- Ever After / Roslin: https://www.greenqueen.com.hk/?p=89159
- Alginate prices: https://www.imarcgroup.com/sodium-alginate-price-trend ; TVP prices: https://dir.tridge.com/prices/product/textured-vegetable-protein-tvp
- Binder prices and doses, Beyond Meat cost of goods, printer throughputs: search snippets (specialingredients.it, Tridge,
  modernistpantry.com, sfp.sonac.biz, Beyond Meat 2024 earnings, Steakholder, Redefine Meat, Revo Foods pages).
