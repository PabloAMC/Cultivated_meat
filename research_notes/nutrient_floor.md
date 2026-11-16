# The nutrient floor, built from GFI's amino-acid prices

> **Note, 2026-11-15 (late).** The figures in this note were computed before three costs were counted: the bubble protectant
> (poloxamer 188), antifoam's quarter cut to the sparger's oxygen transfer, and the oxygen a yeast-style plant buys. Its test checks
> them with those three set back (`tests/_snapshot.py`, `floor_physics.BEFORE_PROTECTANT`). The comparisons hold; the levels are
> higher now. Current scenario costs (RESULTS.md), which also hold dissolved oxygen at half of air saturation: best case $9.66 (was
> $8.95), central $29.42 ($26.64), central with shared medium $26.56 ($24.34), cautious $42.39 ($38.97), reference $12.51 ($11.84).
> With antifoam counted, oxygen limits the central and cautious tanks, so levers that raise the CO₂ or thickness limits are worth
> less there than this note says.

Date: 2026-11-15. Code: `nutrient_floor.py`; tests: `tests/test_nutrient_floor.py`; inputs `nf_*` in `inputs.py`. The source is
GFI, *Amino acid cost and supply chain analysis for cultivated meat* (December 2025; Table 1 and Fig. 9), read in full from the
PDF (text saved in `medium_cost_gfi_sources/`). Costs are 2025 dollars per kg of wet cells. No default changed.

## 1. The question

The model's medium cost is the larger of litres of medium per kilo times the price per litre, and a floor: what the cells must eat.
The floor is **$1.70 a kilo**: amino acids $0.67 (0.337 kg of bulk soy hydrolysate at $2/kg, Humbird's cheaper option), glucose
$0.13, everything else $0.90 (assumed). In Central, litres times price ($5.72) is larger, so the floor does not bind. In the best
case ($1.72 a kilo) it does. Is the floor right?

## 2. What GFI's prices give

GFI prices 22 amino acids in three tiers (Table 1) and uses eight estimates of how much amino acid a kilo of cells needs, 200 to 650
g. The table takes the unweighted mean price of the 22 (GFI weights by need, in charts only) and three of the estimates.

| | Mean price, $/kg of amino acid | 232 g/kg | 350 g/kg | 650 g/kg |
|---|---|---|---|---|
| Feed-grade | 6.36 | $1.48 | $2.23 | $4.13 |
| Low food-grade | 11.59 | $2.69 | $4.06 | $7.53 |
| High food-grade | 23.18 | $5.38 | $8.11 | $15.07 |

These are amino acids per kilo of cells. The check: at the low food-grade price and 350 g/kg the crude mean gives $4.06, and GFI
reports "below about $5". The floor adds glucose ($0.13) and the other nutrients ($0.90, assumed): **$2.50 to $16.09 a kilo**,
against the model's $1.70.

**The model's floor is below every GFI figure.** Its amino acids ($0.67) cost less than GFI's cheapest tier at the best
bioconversion ($1.48). Two reasons: GFI's hydrolysates cannot supply glutamine, arginine, asparagine, cystine or serine, which
fermentation must supply, and the model uses no spiked amino acids. Humbird's own added glutamine and tyrosine (about $2.6 a kilo)
are also left out.

## 3. What it does to the scenarios

| Scenario | Now | Feed-grade, 232 g/kg | Low food-grade, 350 g/kg | High food-grade, 650 g/kg |
|---|---|---|---|---|
| Best case | $8.95 | $9.76 | $12.36 | $23.47 |
| Central | $26.64 | $26.64 | $26.64 | $37.39 |

- **The best case is sensitive.** Its medium is set by the floor (11 L/kg at $0.15), so every dollar of the floor is a dollar of
  cost. At GFI's cheapest tier it would cost $0.8 more; at the low food-grade tier and 350 g/kg, $3.4 more.
- **Central is not, unless amino acids are dear.** Litres times price ($5.72) is above the floor everywhere except the high
  food-grade tier at the worst bioconversion. GFI's own figure for its media, $0.20 a litre, agrees with that.
- **No scenario reaches price parity either way.** The best case needs $7 a kilo and already costs $8.95.

## 4. The $0.05 setting

You asked for a medium price down to $0.05 a litre as an aspiration. The "Price of the medium" switch now has one: **$0.05 a
litre**, tagged "feed or process", labelled as an aspiration. No one has reported it: the lowest company report is $0.07, and GFI's
amino acids alone cost $0.02–0.17. Below about $0.06 the floor binds, so this setting prices the medium at the floor. In Central it
costs **$22.68** (−$3.96). In the best case it changes nothing. The best case keeps $0.15. The preset rule says so.

Since this section's result is that the floor is probably higher, a $0.05 medium at the model's $1.70 floor is optimistic. At the
cheapest GFI floor ($2.50) Central at $0.05 would cost about $23.5.

## 5. What this means, and what is open

1. **A decision for Pablo:** raise the model's floor to GFI's? The cheapest GFI tier gives $2.50 a kilo, which moves the best case
   to $9.76. That is a judgement about hydrolysates, so I have not changed it.
2. **The $0.90 for everything else is still an assumption.** Vitamins, salts, trace elements and lipids could be checked against
   the same GFI report's appendix and media-supplier quotes. It is the largest unsourced part of the floor.
3. **Weighting.** The mean price is unweighted. GFI's weighted figures are in charts and its spreadsheet, which I did not download.
   Serine, arginine and glutamine are needed in the largest amounts, and serine is among the dearest, so a weighted mean is
   probably higher.
