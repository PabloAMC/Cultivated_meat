# What GFI reports about the cost of medium

> Names (2026-11-19): the low-lactate example was earlier called Central; the all-favourable example was earlier called the best case. Cells are described by their traits, never as a named kind of cell.

Date: 2026-11-15. Two GFI reports were read in full (text extracted from the PDFs, saved in `medium_cost_gfi_sources/`). The
fetch tool could not read them, so the 2026 State of the Industry report (10 MB, over the tool's limit) was **not** checked. Its
page 8 is quoted from the December 2025 report, which cites the same company claims. No number in the model changed.

## 1. What the reports say

**GFI, Amino acid cost and supply chain analysis for cultivated meat, December 2025** (Gibbons, Bess, Swartz; full text read):

- Real prices for food- and feed-grade amino acids are "up to 10× lower" than those Humbird used. His were closer to pharma-grade
  prices, according to the interviewees.
- Humbird's amino-acid cost was about **$18–19 per kg of cells**, up to half his total cost. GFI's updated prices could bring it
  **below $5 per kg**, if the industry buys at the lower end of the food-grade range and the cells convert amino acids
  efficiently.
- Amino acids alone cost **$0.02–0.17 per litre** of medium, depending on the formulation and price. Humbird's prices give
  $0.24–0.54 per litre. GFI concludes that total media costs under $0.20 per litre are "likely feasible".
- Company reports it cites: Believer's peer-reviewed $0.63 per litre (Pasitka 2024); Meatly and Gourmey at about $0.20; **Clever
  Carnivore at $0.07, the lowest cited**. These are company reports. GFI did not audit them.
- Litres of medium per kg of cells depend on the formulation and on how well the cells convert amino acids (200–650 g of amino
  acid per kg of cells): about 28–90 L/kg with a modified CHO formulation and 57–183 L/kg with another (FSF4).
- Not covered: growth factors, vitamins, salts, carbohydrates, lipids.

**GFI, Anticipated growth factor and recombinant protein costs, January 2023** (Swartz et al.; full text read):

- The target is growth factors at **10% of production cost**, or about $1 per kg of a $10 product, with medium use of 8, 13 and
  42 L/kg (from Sinke et al. 2021).
- It notes that Humbird's growth factors come to about $3–4 per kg, roughly 10% of his total cost.

## 2. A correction to my earlier answer

I said Humbird's medium, with growth factors, was about $5.7 of $24.6 a kilo. That was the model's price, not his. The model's
feedstock uses Humbird's cheaper **bulk soy hydrolysate** at $2 per kg (`aa_bulk_price`, 0.337 kg per kg of cells: $0.67 a kilo
of cells). His base case bought amino acids at $15–16 per kg. So "Humbird fed-batch, as designed" in `floor_physics.tiers()` is his
plant with the model's feedstock, not his own total. His own medium was far costlier. **The tier's name overstates what it
reproduces.** I have not changed the name, because the page text is being rewritten elsewhere.

This answers the puzzle Pablo raised. The repo does not hold Humbird's published total, so I cannot compare it directly. The
repo's $24.6 is his plant with the model's cheaper medium. On the same plant, his own amino acids (about $18–19 a kilo, against
$0.67) would add roughly $17 a kilo. So a total near ours does not mean his medium was cheap. It means the model's medium is far
cheaper than his, and that is where GFI says the progress has been.

## 3. What the model assumes, against GFI

| | Model | GFI |
|---|---|---|
| Price per litre | $0.20 in the low-lactate example, $0.15 in the all-favourable example | $0.20 (several companies), $0.07 (one), $0.63 (peer-reviewed) |
| Amino acids per kg of cells | $0.67 (the floor), inside the medium cost | below $5 at the lower end |
| Litres per kg | 28 in the low-lactate example, 11 in the all-favourable example | 28–90 (CHO) or 57–183 (FSF4), from medium formulations |
| Growth factors | $3.0 in the low-lactate example, 0 in the all-favourable example | 10% of cost: about $1 a kilo at $10 |

- **Central matches GFI.** Its medium costs 28 L × $0.20 = $5.72 a kilo. That is the same order as GFI's amino acids "below $5"
  plus the other components.
- **The all-favourable example sits below GFI.** Its medium costs $1.72 a kilo, set by the model's $0.67 amino-acid floor. GFI's own range for the
  CHO formulation (28–90 L/kg at $0.02–0.17 per litre for amino acids alone) gives $1.4–15 a kilo. The all-favourable example's 11 L/kg uses
  less medium than any GFI formulation. This is the all-favourable example's biggest optimism on medium. I have not changed it.
- **A lower price would matter in Central.** At $0.15, $0.10 and $0.07 a litre, Central costs $25.21, $23.78 and $22.92, against
  $26.64 at $0.20. The all-favourable example does not move: the nutrient floor already binds.

## 4. What the model could do

The "Price of the medium" switch has four settings ($0.15, $0.20, $0.30, $0.50). GFI's December 2025 report supports adding one
for **$0.07** (the lowest company report, unverified). If it were added, the all-favourable example's rule ("cheapest setting") would pick it,
and the page's "what decides it" numbers for the medium price would change. **That is a decision for Pablo, so it is not done
here.**
