# Cleaning spent medium: electrodialysis, dialysis, algae, stripping, and the 1996 review

Research date: 2026-11-21. Evidence pass only; no input changed. The model prices electrodialysis and dialysis from first
principles (`medium_reuse.py`, `research_notes/medium_reuse.md`), resting on "over 90% of ammonium and 99% of lactate" (Nir 2023,
as cited by Soccol et al. 2024; not found) and patent claims.

## Short answer

**No measured removal rate or cost for electrodialysis of animal-cell medium was found.** Nir 2023 was still not located
(searched by its title and by topic). The measured numbers that exist are for other routes (algae, high-pH stripping,
ion-concentration polarisation) and are all bench-scale, with no cost per litre. The model's electrodialysis cost stays a
first-principles estimate.

## What was found

| route | source | removal / result | cells grew on it? | cost | strength |
|---|---|---|---|---|---|
| Electrodialysis | Nir 2023 "Selective separation of ammonium and lactate from cell culture media" | not found again | — | — | secondary citation only |
| Electrodialysis, other broths | bipolar-membrane ED separating ammonium and lactic acid from *Lactobacillus* broth; pilot ammonia removal averaging 83.6% per batch (patent) | 84% per batch in a fermentation broth, not cell medium | n/a | not given | patent / search summary |
| Dialysis loop with ammonia filter | Yissum (inventor Nahmias), WO2018011805A2, priority 2016-07-11, status "ceased" | claims ≥90% (preferably 98%) of perfusate returned, ≥95% of cells retained; 10–60 kDa dialyser (30 kDa in prototype, 2,200 cm²), counter-flow protein-free dialysate cleaned by **carbon or zeolite** filter; prototype dialysis about 3 mL/min per g of cells; ≤5 L chambers, about 100 sharing one dialysis system; says ammonia "limits cell growth when it reaches 5 mM"; quotes 230 L/kg and ≥$4,600/kg of medium for conventional culture | not quantified | none | patent claims, read in part (Google Patents text) |
| Ion-concentration polarisation (ICP) | "Regeneration of Spent Culture Media for Sustainable and Continuous mAb Production via Ion Concentration Polarization", Biotechnol Bioeng 2025, doi:10.1002/bit.28888 | "up to 75% of spent culture media can be regenerated and reused without affecting the cell viability" (CHO); water mass intensity improved up to 33%; authors argue it scales to 50 L perfusion | yes (CHO viability) | not given | peer-reviewed, abstract |
| High-pH stripping | Pakbin et al. 2025, Front Bioeng Biotechnol 13:1617115 | 82% of ammonia removed at pH 12, 15 min (1.21 → 0.21 mM); 39–98% across the design; zeolite partial; struvite and TiO2 failed | lamb satellite cells: treated spent medium better than untreated (p = 0.0002); a 50:50 blend with fresh medium no different from fresh; 72 h only | "cost-effective" stated, no number; glucose loss reported inconsistently | peer-reviewed, read in part |
| Microalgae (*Chlorococcum littorale*, *Chlorella vulgaris*) on C2C12 waste medium | Haraguchi et al. 2021, Arch Microbiol 203, doi:10.1007/s00203-021-02509-x | **80%** (C. littorale) and 26% (C. vulgaris) of ammonia and 15–16% of phosphorus consumed over 7 days; algae grew 3.2× and 1.6× | not tested in that paper | none | peer-reviewed, abstract |
| Circular culture with algae | Haraguchi, Okamoto & Shimizu 2022, Arch Microbiol, doi:10.1007/s00203-022-03234-9 | C2C12 grew 4.0× in 48 h in cycle 1; cycle 2 in algal waste medium plus algal nutrients grew at the same rate | yes, equal over two cycles | none | peer-reviewed, abstract |
| Lactate-consuming cyanobacteria | 2023, Arch Microbiol, doi:10.1007/s00203-023-03607-8 | recombinant *Synechococcus* took up lactate and ammonia; C2C12 grew 3.6× then 3.9× in 3 days in the reused medium, serum-free | yes, two cycles | none | peer-reviewed, abstract |
| Heterotrophic alga at 37 °C | Thyden et al. 2024, Syst Microbiol Biomanuf, doi:10.1007/s43393-024-00280-w | *Chlorella sorokiniana* "can rapidly eliminate all ammonia" from 4- and 8-day QM7 spent medium, in the dark | QM7 metabolic activity 80.9 ± 12.0% of fresh in treated vs 44.6 ± 10.8% in untreated spent medium | none | peer-reviewed, abstract |
| The 1996 review | Schneider, Marison & von Stockar, J Biotechnol 46:161–185, doi:10.1016/0168-1656(95)00196-4 | lists glutamine substitution, controlled glutamine feeding, and removal by ion-exchange resins, ion-exchange membranes, gas-permeable membranes or electrodialysis; the authors' own PTFE gas-membrane method (Enzyme Microb Technol 1994) gave ammonia fluxes "of the same order of magnitude" as cell production, and about **50% lower ammonia** in hybridoma batches (1997 follow-up) | yes (hybridoma) | none | review, abstract only (full text paywalled) |

## Reading

- The one figure the model needs most, **removal per pass with growth factors and amino acids tracked, on real meat-cell
  medium**, does not exist publicly. The closest: ICP's 75% reuse on CHO, and the algae and stripping results, which remove
  ammonia but either consume glucose (stripping at pH 12; algae, which also eat sugar) or add a second organism and a
  separation step.
- Gas-permeable membranes at a pH gradient (Schneider 1994/1997) are an old, simple option the model does not list: 50% lower
  ammonia in batch, no electrical cost. Worth a line in `medium_reuse.md` as a candidate, not a priced lever.
- Patent numbers (90–98% recirculation) are claims of what a controller does, not measured cleaning.

## Recommendation for the parent session (not applied)

- No input change. Keep the electrodialysis and dialysis costs labelled as first-principles estimates.
- In `medium_reuse.md`, add: Haraguchi 2021 (80% ammonia uptake by *C. littorale* in 7 days), Thyden 2024 (complete removal by
  *C. sorokiniana* at 37 °C, QM7 activity 81% of fresh), Pakbin 2025 (82% stripping at pH 12), ICP 2025 (75% of medium reused,
  CHO), Schneider 1994/1997 (gas-permeable membrane, about 50% lower ammonia); and that Nir 2023 remains unlocated.
- The dialysis variant's "10 L/m²/h clearance" (TODO) is still unchecked: WO2018011805 gives only a prototype rate (about 3 mL/min
  per gram of cells across 2,200 cm²), which is a dialysate flow, not a clearance.

## Sources

URLs: WO2018011805A2 https://patents.google.com/patent/WO2018011805A2/en ; Pakbin 2025 https://www.frontiersin.org/articles/10.3389/fbioe.2025.1617115/full ;
Thyden 2024 https://journal.hep.com.cn/smab/EN/10.1007/s43393-024-00280-w ; Haraguchi 2021, 2022 and the 2023 cyanobacteria paper,
and the ICP 2025 paper, via the Europe PMC REST API (abstracts), https://www.ebi.ac.uk/europepmc/webservices/rest/search ;
Schneider 1996 abstract via EPFL Infoscience, https://infoscience.epfl.ch/record/80751 ; lactate/ammonium ED in *Lactobacillus* broth
and the 83.6% pilot figure via search summaries of US patents (e.g. https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5814498).
