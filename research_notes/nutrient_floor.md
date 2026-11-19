# The nutrient floor, built from GFI's amino-acid prices

> Repinned 2026-11-19 (scenario restructure): every kind of cell weighs 2 ng, so the all-favourable example's cells are no longer Humbird's 3 ng; it costs $11.67 at most likely values, not $11.46, and its figures here are the earlier ones unless a table says otherwise (the tests pin the new ones). The ammonia range of the low-lactate example's cells now runs from 0.04 mol/kg.

> Names (2026-11-19): the low-lactate example was earlier called Central; the all-favourable example was earlier called the best case. Cells are described by their traits, never as a named kind of cell.

> **Decided 2026-11-19 (Pablo): the model's floor is now GFI's cheapest, $2.00 a kilo** (section 6). Sections 1-5 are the analysis
> as of 2026-11-15, when the floor was $1.70; their figures are on the model of that date.

> Recomputed 2026-11-16 on the current model (bubble protectant, antifoam's cost to oxygen transfer, bought oxygen in a yeast-style plant, dissolved oxygen held at half of air saturation, medium at least the culture that leaves with the cells).

> Repinned 2026-11-19 (audit batch): ammonia tolerance 4 mM, lost runs pay for their membranes, glucose from the cells' balance (published cells need about 95 L/kg); see audit_2026-11-19.md.
> What this changed here (section 6 only): the all-favourable example is $11.46 and Central $32.80. Central uses 35 litres a kilo, so its $0.20 medium
> costs $7.00, and it takes a dearer amino-acid floor than before to move it. The floor itself is still $2.00.

Date: 2026-11-15. Code: `nutrient_floor.py`; tests: `tests/test_nutrient_floor.py`; inputs `nf_*` in `inputs.py`. The source is
GFI, *Amino acid cost and supply chain analysis for cultivated meat* (December 2025; Table 1 and Fig. 9), read in full from the
PDF (text saved in `medium_cost_gfi_sources/`). Costs are 2025 dollars per kg of wet cells. No default changed.

## 1. The question

The model's medium cost is the larger of litres of medium per kilo times the price per litre, and a floor: what the cells must eat.
The floor is **$1.70 a kilo**: amino acids $0.67 (0.337 kg of bulk soy hydrolysate at $2/kg, Humbird's cheaper option), glucose
$0.13, everything else $0.90 (assumed). In Central, litres times price ($5.72) is larger, so the floor does not bind. In the all-favourable
example ($1.72 a kilo) it does. Is the floor right?

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
| All-favourable example | $9.66 | $10.47 | $13.07 | $24.18 |
| Low-lactate example | $29.42 | $29.42 | $29.42 | $40.17 |

- **The all-favourable example is sensitive.** Its medium is set by the floor (11 L/kg at $0.15), so every dollar of the floor is a dollar of
  cost. At GFI's cheapest tier it would cost $0.8 more; at the low food-grade tier and 350 g/kg, $3.4 more.
- **Central is not, unless amino acids are dear.** Litres times price ($5.72) is above the floor everywhere except the high
  food-grade tier at the worst bioconversion. GFI's own figure for its media, $0.20 a litre, agrees with that.
- **No scenario reaches price parity either way.** The all-favourable example needs $7 a kilo and already costs $9.66.

## 4. The $0.05 setting

You asked for a medium price down to $0.05 a litre as an aspiration. The "Price of the medium" switch now has one: **$0.05 a
litre**, tagged "feed or process", labelled as an aspiration. No one has reported it: the lowest company report is $0.07, and GFI's
amino acids alone cost $0.02–0.17. Below about $0.06 the floor binds, so this setting prices the medium at the floor. In Central it
costs **$25.46** (−$3.96). In the all-favourable example it changes nothing. The all-favourable example keeps $0.15. The preset rule says so.

Since this section's result is that the floor is probably higher, a $0.05 medium at the model's $1.70 floor is optimistic. At the
cheapest GFI floor ($2.50) Central at $0.05 would cost about $26.3.

## 5. What this means, and what is open

1. **A decision for Pablo:** raise the model's floor to GFI's? The cheapest GFI tier gives $2.50 a kilo, which moves the all-favourable example
   to $10.47. That is a judgement about hydrolysates, so I have not changed it.
2. **The $0.90 for everything else is still an assumption.** Vitamins, salts, trace elements and lipids could be checked against
   the same GFI report's appendix and media-supplier quotes. It is the largest unsourced part of the floor.
3. **Weighting.** The mean price is unweighted. GFI's weighted figures are in charts and its spreadsheet, which I did not download.
   Serine, arginine and glutamine are needed in the largest amounts, and serine is among the dearest, so a weighted mean is
   probably higher.

## 6. The decision (2026-11-19)

The floor is now feed-grade amino acids at GFI's most efficient need, with the other nutrients re-estimated:

| part of the floor | per kilo of wet cells | basis |
|---|---|---|
| amino acids: 232 g at $6.36 a kilo | $1.48 | GFI, feed-grade mean of 22 (unweighted); the most efficient of eight need estimates |
| glucose | $0.13 | 0.32 kg at $0.40 (unchanged) |
| salts, buffer, vitamins, trace elements | $0.40 | was $0.90, assumed; DMEM/F12's salts, bicarbonate and vitamins at bulk prices are about $0.005-0.01 a litre, $0.1-0.3 a kilo at 11-28 litres |
| **total** | **$2.00** | was $1.70 |

**Why the old floor was too low.** Not a mass balance: 0.337 kg of hydrolysate supplies about the 0.26 kg of amino acids the cells
take up (Humbird's stoichiometry; wet cells are 15-20% protein). It was the price: hydrolysis destroys or converts glutamine,
arginine, asparagine, cystine and serine, which the cells need, so they must come from fermentation at amino-acid prices.

**Why the cheapest tier.** The floor binds only where the medium costs no more than what the cells eat: the all-favourable example, Humbird's
optimistic design and the setting "at the nutrient floor". The all-favourable example takes the favourable end of every input, so its floor is
GFI's favourable end. Central and the other rungs pay the announced $0.20 a litre (35 litres a kilo since the audit batch, $7.00, or $7.15 with the
medium lost in lost tanks; it was 28 litres and $5.72), above any floor below the high food-grade tier. The amino-acid price is drawn in the scenarios' bands ($5.0-11.6 a kilo, mode $6.36).

**What it does.** The all-favourable example $9.66 to $9.96; Humbird's optimistic design $12.51 to $12.81. Central does not move on this account
(it moved from $29.42 to $26.43 the same day, because growth factors are now counted inside the announced medium price,
`growth_factors_in_medium_price.md`). The medium switch's $0.05 and $0.15 a litre settings were replaced by one setting, "at the
nutrient floor": at Central's 28 litres a kilo the floor was $0.07 a litre, and with it Central cost $25.77 (growth factors bought on
top, at 30% of Humbird's price).

**After the audit batch (2026-11-19).** The all-favourable example costs $11.46 and Central $32.80. At Central's 35 litres a kilo the floor is
$0.06 a litre, and with the setting "at the nutrient floor" Central costs $31.45 ($1.35 less; growth factors bought on top, at 30%
of Humbird's price). The table is on this model:

| amino acids | need 232 g | need 350 g | need 650 g |
|---|---|---|---|
| feed-grade ($6.36) | floor $2.00; best $11.46; the low-lactate example $32.80 | $2.75; $12.21; $32.80 | $4.66; $14.14; $34.25 |
| low food-grade ($11.59) | $3.22; $12.68; $32.80 | $4.58; $14.06; $34.17 | $8.06; $17.57; $37.73 |
| high food-grade ($23.18) | $5.91; $15.39; $35.53 | $8.64; $18.15; $38.32 | $15.60; $25.17; $45.43 |

The all-favourable example still moves dollar for dollar with the floor. Central's $0.20 a litre is a complete medium, so it cannot cost less than
the nutrients plus the growth factors its price includes (about $3.7 a kilo at 35 litres). That sum passes its $7.00 only when the
floor is above about $3.3 a kilo. So Central is now less sensitive to amino-acid prices than before the audit batch: it does not
move at feed-grade prices and 350 g, or at low food-grade prices and 232 g (it rose at both when it used 28 litres), and it rises
with the floor from $4.58 up.

Still open: the weighted mean price (serine, arginine and glutamine are needed most; serine is dear), and a supplier's tonne quote
for the five amino acids hydrolysate cannot supply.
