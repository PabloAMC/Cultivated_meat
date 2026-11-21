# Ammonia tolerated at high density, and filter life with meat cells: second pass

Research date: 2026-11-21. Evidence pass only; no input changed. This pass searched for what the first pass
(`ammonia_tolerance_and_filter_life.md`, 2026-11-16) did not find, in both directions. Model now: `sc_nh3_limit` 4 mmol/L
(range 2–8), Humbird's design `pf_nh3_limit` 5; `rt_membrane_life` 2,415 L/m² (range 900–5,500).

## Short answer

- **Still no published ammonium dose-response for bovine, chicken or fish muscle cells, fibroblasts or MSCs in serum-free
  perfusion at high density.** The searches found nothing newer than the rows already in the first pass (catfish ovary, pig
  muscle stem cells (Qiu 2026), bovine FAPs (Hubalek 2023), fibroblast lines).
- **Still no measured filter life with any meat cell.** The only meat-relevant figures are a company cost assumption
  (Pasitka 2024: one ATF membrane change a month, implying about 3,600–9,200 L/m²) and process statements without numbers.
- Evidence is thin in both directions; the current inputs remain inside it.

## New or newly read items

| item | direction | what it says | strength |
|---|---|---|---|
| Pasitka 2024 SI, Table S6 (`evidence_pasitka_supplement.md`) | filter life **higher** than 2,415 | 600 ATF membranes a year on 50 ATF-10 (one per device per month): about 3,640 L/m² if all medium is permeate, up to 9,240 if all process water is | company design assumption, not measured |
| Believer FDA memo (CCC 000039, 2025) | neutral | harvest "using filtration followed by washing ... within a continuous closed system"; no filter life | regulatory summary |
| Wildtype FDA memo (CCC 000005, 2025) | neutral (mode) | salmon cells in "suspension fed-batch"; no ammonia data | regulatory summary |
| "Myogenic response to increasing concentrations of ammonia differs between mammalian, avian, and fish species" (2020, PMC7464490) | ammonia tolerance **higher** for avian and fish cells (differentiation only) | chick myotubes kept a positive myogenic response at 10 mM ammonium acetate; tilapia myotube diameter unaffected at 10–50 mM; C2C12 negative. 24 h exposures, differentiation not proliferation | peer-reviewed, abstract/summary |
| Pakbin et al. 2025, Front Bioeng Biotechnol 13:1617115 (Texas A&M) | neutral | lamb satellite cells grew in spent medium after ammonia stripping (82% of 1.21 mM removed at pH 12, 15 min); spent medium held only about 1.2 mM; 72 h test | peer-reviewed, read in part |
| Díaz-Maneh et al. 2026, Food Bioprocess Technol 19:168 (duck fibroblasts, perfusion on microcarriers) | not informative | 0.49 million cells/mL, far below 10–20% by volume; no ammonia or filter data | peer-reviewed, read |
| Coffman 2021, Madabhushi 2025 (CHO, already in first pass) | filter life **lower** | 1,000 L/m² design figure; filter swap at 85–100 million cells/mL "only extends the culture duration by a couple of days" | peer-reviewed |
| A flat-plate patent (via search summary): 2–10 µm membranes changed every 5–7 days at 1–4 L/m²/h | filter life **lower** for wide-pore flat plates | about 120–670 L/m²; 10 µm retained under 70% of cells | patent, secondary |

**Not found:** ammonium IC10/IC50 for any meat-relevant cell at over 50 million cells/mL; any cell held for weeks at a fixed
ammonium level in perfusion; any hollow-fibre run with meat cells; any wide-pore fibre at a stated density over 50 million
cells/mL.

## Reading

- The avian and fish myotube result is the only "higher" signal on ammonia, but it is a 24 h differentiation readout, not
  growth at steady state, so it does not move a proliferation limit. A rough judgement: it raises the chance that a chicken or
  fish line tolerates over 5 mM in growth by a few points, not more.
- Pasitka's implied 3,600–9,200 L/m² is the only meat-relevant filter number and it is an assumption. CHO measurements at
  similar density (first pass) sit at about 180–2,500 L/m². The model's 2,415 sits between them.

## Recommendation for the parent session (not applied)

No change to `sc_nh3_limit`, `pf_nh3_limit` or `rt_membrane_life`. Add the Pasitka S6 line (with its arithmetic and the
"assumption, not measurement" label) to the `rt_membrane_life` note, since it is the only meat-cell figure and it argues for
the upper half of the range. The bench test in [evidence_outreach_drafts.md](evidence_outreach_drafts.md) (draft d) is
the only way to move either input with evidence.

## Sources

- Pasitka et al. 2024, Nature Food, SI Table S6, https://static-content.springer.com/esm/art%3A10.1038%2Fs43016-024-01022-w/MediaObjects/43016_2024_1022_MOESM1_ESM.pdf
- FDA scientific memos, CCC 000039 https://www.fda.gov/media/188065/download and CCC 000005 https://www.fda.gov/media/186753/download
- "Myogenic Response to Increasing Concentrations of Ammonia Differs between Mammalian, Avian, and Fish Species", 2020,
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7464490/ (search summary; full text not opened: PMC returned a verification page)
- Pakbin B. et al. 2025, "Development and optimization of an ammonia removal strategy for sustainable recycling of cell culture
  spent media in cultivated meat production", https://www.frontiersin.org/articles/10.3389/fbioe.2025.1617115/full
- Díaz-Maneh A. et al. 2026, "Proof-of-Concept for Cell Culture-Based Duck Fat Production on a Laboratory Scale", doi:10.1007/s11947-026-04259-4,
  https://ddd.uab.cat/pub/artpub/2026/326459/FooBioTec_a2026v19p168.pdf
- Flat-plate membrane patent quoted in search results (Woodside 1998 data as quoted in WO2017180814A1; see first pass).
