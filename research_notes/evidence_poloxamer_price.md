# Poloxamer 188 by the tonne

Research date: 2026-11-21. Evidence pass only; no input changed. The model charges `pf_protectant_dose` 2 g/L ×
`pf_protectant_price` $30/kg (assumed, range $10–260) on every litre through a sparged vessel.

## What was found

| grade | evidence | $/kg | strength |
|---|---|---|---|
| Pharma (Kolliphor P 188 / Parteck PLX 188), catalogue | Sigma-Aldrich 25 kg $6,475–6,760; EMPROVE EXPERT 25 kg $7,140 | 259–286 | catalogue, firm |
| Pharma, small lots | Alfa Aesar 1 kg $236; Fisher $295–482; Sigma "micro" 1 kg $825 | 236–825 | catalogue |
| Chinese supplier, 25 kg drums | ChemicalBook listing, $5 / $3 / $2 per kg at 1 / 10 / 50 kg (updated 2024-08-20) | 2–5 | listing, weak (asking price, grade unverified) |
| Industrial grade, same molecule | BASF Pluronic PE 6800 (EO/PO block copolymer, the industrial counterpart of F68) sold in **600 kg IBCs** through BTC Europe for industrial formulators; no price shown | — | product listing: shows a tonne route exists |
| Analogue: commodity non-ionic surfactants | UN Comtrade, Germany exports 2024: HS 3402.42 (non-ionic surface-active agents) $1,031 M for 311 kt = **$3.31/kg**; HS 3907.29 (other polyethers) $1,271 M for 401 kt = **$3.17/kg** | ~3.2–3.3 | trade statistics, but a basket, not poloxamer |
| Trade aggregator | Pharmaoffer poloxamer 188 page: 19 B2B transactions, price per kg behind paywall | — | — |
| Indian customs | Zauba poloxamer imports (pages blocked; one search summary shows an average "$3.67" with unit not stated) | ? | unusable |

**Not found:** any published tonne quote for pharma- or cell-culture-grade poloxamer 188; any 2025–2026 price index.

## Reading

- The molecule is a commodity EO/PO copolymer; industrial grades of that chemistry trade near **$3–5/kg**. Pharma grade adds
  purification, GMP and documentation; the catalogue's $260/kg is a 25 kg research-and-development price, not a tonne price.
- **Grade matters for cells.** Poloxamer 188 is known for lot-to-lot differences in shear protection (a hydrophobic,
  higher-molecular-weight fraction in poor lots); suppliers sell a "cell culture" qualified grade for that reason. A plant
  would need a screened grade, which sits between industrial and pharma prices. This is from memory of the bioprocess
  literature, not re-checked in this pass.
- **Food status.** GOOD Meat's FDA memo (CCC 000001, 2023) lists Pluronic F-68 as a medium component used to reduce clumping,
  tested in the washed product, not detected, and bounded at no more than 10 mg per 100 g of product (FDA scientific memo,
  https://www.fda.gov/media/166348/download). So it is already accepted in one US clearance; a food-use grade will be required.
- A rough judgement (mine, not measured): a tonne price for a cell-culture-qualified, food-acceptable grade most likely lies
  at **$15–40/kg**, with $5 possible if an industrial grade passes screening and $100 if only pharma grade is accepted.

Effect at 2 g/L (from the figures in `gas_flow_cap.md`, follow-up 1): $0.67 a kilo of cells at $30 and 11.2 L/kg, $1.68 at
28 L/kg. At $15: $0.34 / $0.84. At $5: $0.11 / $0.28. At $100: $2.24 / $5.60.

## Recommendation for the parent session (not applied)

Keep **$30** as the most likely value (it sits inside the plausible $15–40 band; no source contradicts it), but narrow the
range to **lo $5, hi $100**: $5 = industrial-grade EO/PO copolymer near commodity surfactant prices; $100 = pharma grade bought
by the tonne at roughly a third of the 25 kg catalogue price (a guess, labelled as such). Keep $260 only as a named
stress case ("catalogue price"), not the band's top. Replace with a quote when one arrives
([evidence_outreach_drafts.md](evidence_outreach_drafts.md), draft b).

## Sources

- Sigma-Aldrich poloxamer 188 / Kolliphor P 188 product pages, e.g. https://www.sigmaaldrich.com/US/en/product/mm/137112 and
  https://sigmaaldrich.com/CA/en/product/sigma/15759 ; VWR Kolliphor P 188 NF, https://us.vwr.com/store/product/21495340 ;
  Fisher, https://www.fishersci.com/shop/products/poloxamer-188-thermo-scientific/AAJ6608736 (via search summaries).
- ChemicalBook poloxamer 188 supplier listing, https://chemicalbook.com/ProductDetail_EN_poloxamer-188_1945758.htm (via search summary).
- BTC Europe, Pluronic PE 6800, 600 kg IBC, https://www.btc-europe.com/app/shop/products/50567658/fr/pluronic-pe-6800 ; BASF Care 360,
  https://care360.basf.com/global/en/Product-Finder/30044097 (descriptions only).
- UN Comtrade public preview API, reporter Germany (276), exports, HS 340242 and 390729, 2024, queried 2026-11-21.
- FDA, CCC 000001 scientific memo (GOOD Meat), 2023-03-17, https://www.fda.gov/media/166348/download (read in full).
