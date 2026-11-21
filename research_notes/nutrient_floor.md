# The nutrient floor, built from GFI's amino-acid prices

> Repinned 2026-11-20 (final pass). The all-favourable example is now the one case of `scenarios.all_favourable()` ($7.62; it was $18.71 in the first batch of 2026-11-20); the low-lactate example costs $49.50 ($49.96). The floor itself is still $2.00 a kilo of cells grown for the model cell ($1.99 for the all-favourable example's cells, $2.16 per kilo harvested). The table of section 6 is regenerated from `python nutrient_floor.py`. **What changed:** the all-favourable example now loses no runs (Humbird's design loses none, and the case takes the more favourable source), so it moves exactly dollar for dollar with the floor per kilo of cells grown; before, the medium lost with lost tanks made it move a little more. The conclusions are unchanged: the all-favourable example's medium is the floor, so every dollar of the floor is a dollar of its cost (per kilo grown); the low-lactate example moves by nearly the floor's rise (+$0.69 at feed-grade prices and 350 g/kg, +$1.22 at low food-grade prices and 232 g/kg).

> Repinned 2026-11-20 (first batch: lactate tolerance 35 mmol/L in the scenarios, cells killed by bursting bubbles, a 2% harvest loss, twice the fed-batch crew in perfusion, membrane life 2,415 L/m2, medium preparation capital, utilities in four parts, growth factors dosed per litre from Humbird's fed-batch 8.65 L/kg). One conclusion changed then: the low-lactate example moves with the floor. Its 35 litres per kilo grown at $0.20 cost $7.00, and its nutrients plus the growth factors inside that price come to within a few cents of that, so any dearer amino acids raise its cost by nearly the floor's rise. Before that batch it did not move until the floor passed about $3.3 a kilo. Said the other way: at 35 litres a kilo a complete medium at $0.20 a litre is at the least it can cost in the model.

> Names (2026-11-19): the low-lactate example was earlier called Central; the all-favourable example was earlier called the best case. Cells are described by their traits, never as a named kind of cell.

> **Decided 2026-11-19: the model's floor is GFI's cheapest, $2.00 a kilo** (section 6). Sections 1-5 are the analysis as of
> 2026-11-15, when the floor was $1.70; their figures are on the model of that date. Earlier repins (2026-11-19 scenario
> restructure and audit batch; 2026-11-16 recompute) are recorded in the changelog.

Date: 2026-11-20 (analysis 2026-11-15). Code: `nutrient_floor.py`; tests: `tests/test_nutrient_floor.py`; inputs `nf_*` in `inputs.py`. The source is
GFI, *Amino acid cost and supply chain analysis for cultivated meat* (December 2025; Table 1 and Fig. 9), read in full from the
PDF (text saved in `medium_cost_gfi_sources/`). Costs are 2025 dollars per kg of wet cells. No default changed.

## 1. The question

The model's medium cost is the larger of litres of medium per kilo times the price per litre, and a floor: what the cells must eat.
The floor is **$1.70 a kilo**: amino acids $0.67 (0.337 kg of bulk soy hydrolysate at $2/kg, Humbird's cheaper option), glucose
$0.13, everything else $0.90 (assumed). In the low-lactate example, litres times price ($5.72) was larger, so the floor does not bind. In the all-favourable
example ($1.72 a kilo) it did. Is the floor right?

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
- **The low-lactate example was not, unless amino acids are dear.** Litres times price ($5.72) is above the floor everywhere except the high
  food-grade tier at the worst bioconversion. GFI's own figure for its media, $0.20 a litre, agrees with that.
- **No scenario reaches price parity either way.** The all-favourable example needs $7 a kilo and already costs $9.66.

## 4. The $0.05 setting

A medium price down to $0.05 a litre was asked for as an aspiration. The "Price of the medium" switch then had one: **$0.05 a
litre**, tagged "feed or process", labelled as an aspiration. No one has reported it: the lowest company report is $0.07, and GFI's
amino acids alone cost $0.02–0.17. Below about $0.06 the floor binds, so this setting prices the medium at the floor. In the low-lactate example it
cost **$25.46** (−$3.96). In the all-favourable example it changes nothing. The all-favourable example kept $0.15. (Replaced on 2026-11-19 by the setting "at the nutrient floor", section 6.)

Since this section's result is that the floor is probably higher, a $0.05 medium at the model's $1.70 floor is optimistic. At the
cheapest GFI floor ($2.50) the low-lactate example at $0.05 would have cost about $26.3.

## 5. What this means, and what is open

1. **Raise the model's floor to GFI's?** Done on 2026-11-19 (section 6): the floor is GFI's cheapest tier, with the other
   nutrients re-estimated, $2.00 a kilo.
2. **The $0.90 for everything else is still an assumption.** Vitamins, salts, trace elements and lipids could be checked against
   the same GFI report's appendix and media-supplier quotes. It is the largest unsourced part of the floor.
3. **Weighting.** The mean price is unweighted. GFI's weighted figures are in charts and its spreadsheet, which was not downloaded.
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
GFI's favourable end. The low-lactate example and the other rungs pay the announced $0.20 a litre (35 litres a kilo since the audit batch, $7.00, or $7.15 with the
medium lost in lost tanks; it was 28 litres and $5.72), above any floor below the high food-grade tier. The amino-acid price is drawn in the scenarios' bands ($5.0-11.6 a kilo, mode $6.36).

**What it does.** The all-favourable example $9.66 to $9.96; Humbird's optimistic design $12.51 to $12.81. The low-lactate example did not move on this account
(it moved from $29.42 to $26.43 the same day, because growth factors are now counted inside the announced medium price,
`growth_factors_in_medium_price.md`). The medium switch's $0.05 and $0.15 a litre settings were replaced by one setting, "at the
nutrient floor": at the low-lactate example's 28 litres a kilo the floor was $0.07 a litre, and with it that example cost $25.77 (growth factors bought on
top, at 30% of Humbird's price).

**On the model of 2026-11-20 (final pass).** The all-favourable example costs $7.62 and the low-lactate example $49.50. With the
setting "at the nutrient floor" the low-lactate example costs $49.22 ($0.28 less; growth factors bought on top, at 30% of Humbird's
price). The table (`python nutrient_floor.py`; floor $/kg of cells grown for the model cell; the all-favourable example; the
low-lactate example, $/kg harvested):

| amino acids | need 232 g | need 350 g | need 650 g |
|---|---|---|---|
| feed-grade ($6.36) | floor $2.00; the all-favourable example $7.62; the low-lactate example $49.50 | $2.75; $8.43; $50.19 | $4.66; $10.50; $52.36 |
| low food-grade ($11.59) | $3.22; $8.93; $50.72 | $4.58; $10.41; $52.27 | $8.06; $14.18; $56.21 |
| high food-grade ($23.18) | $5.91; $11.84; $53.77 | $8.64; $14.80; $56.87 | $15.60; $22.33; $64.75 |

The all-favourable example moves exactly dollar for dollar with the floor per kilo grown ($2.58 a kilo grown from feed-grade at 232 g
to low food-grade at 350 g; $2.79 a kilo harvested, because 92.4% of the cells grown are harvested). The low-lactate example's $0.20 a
litre is a complete medium, so it cannot cost less than the nutrients plus the growth factors its price includes; at 35 litres a kilo
that sum is within a few cents of $7.00, so it rises by nearly the floor's rise from the cheapest floor up.

Still open: a supplier's tonne quote for the five amino acids hydrolysate cannot supply.

## 7. The weighted mean, checked (2026-11-21)

GFI's report gives the tonnes of each amino acid a 250 kt industry would need (the table on page 18): one column for the FSF4
medium at the most efficient need, one for the modified CHO medium at the least efficient. Weighting Table 1's prices by those
tonnes:

| need profile | feed-grade, $/kg | low food-grade, $/kg | amino acids at 232 g/kg, feed-grade | largest cost shares (feed-grade) |
|---|---|---|---|---|
| unweighted mean of 22 (the model) | 6.36 | 11.59 | $1.48 | |
| FSF4 medium | 5.74 | 11.87 | $1.33 | serine 30%, glutamine 13%, asparagine 11%, tyrosine 9% |
| modified CHO medium | 6.47 | 12.10 | $1.50 | serine 18%, asparagine 17%, proline 13%, glutamine 12% |

Check against GFI's Figure 6: FSF4 holds about 3.5 g of amino acids a litre (57 L/kg at 200 g/kg), and 3.5 g at $5.74 is $0.020 a
litre, GFI's "~$0.02". **The two weighted means bracket the unweighted one, so the model keeps $6.36**; the floor would be $1.85 to
$2.02 instead of $2.00. The cheap bulk amino acids (lysine, threonine, glycine, valine) are needed in small amounts; serine,
glutamine, asparagine and arginine are needed most, and serine is dear. This is why the unweighted mean does not overstate the price.

**Hydrolysate does not lower it much either.** The five amino acids hydrolysate cannot supply (arginine, asparagine, cystine,
glutamine, serine) are 51% of FSF4's amino acids by mass, at a weighted $6.86 a kilo feed-grade: $0.80 of a kilo of cells on their
own. If hydrolysate at Humbird's $2 a kilo supplied the other half with no waste, the amino acids would cost about $1.0 instead of
$1.33-1.50. Hydrolysates carry amino acids in the wrong proportions, so more must be bought than the cells use. A plausible
blend is therefore $1.1-1.3, a floor of about $1.65-1.85. This is not adopted: no tested blend has been published, and GFI's
price thresholds for one ($1.51-11.27 a kilo of hydrolysate) say the price is not known.

**Why a chicken is cheaper to feed.** A chicken also has a nutrient floor: about 3.5 kg of feed a kilo of boneless meat, about
0.7 kg of it crude protein, three times the 0.232 kg the cells take up. But soybean meal costs about $0.70 a kilo of protein,
against $5.7-6.5 for purified amino acids. The chicken's gut breaks intact protein down for free, and its body makes the
non-essential amino acids, serine among them, from grain. A culture medium must supply them already purified.

## 8. Today's prices against the long run (2026-11-21)

An evidence pass on the five amino acids hydrolysate cannot supply ([evidence_amino_acid_prices.md](evidence_amino_acid_prices.md))
found tonne-scale prices for arginine ($3–4.6 a kilo, close to GFI's) and glutamine (about $7, food grade), and none for
asparagine, cystine or serine. Serine decides the floor: it is 30% of the amino-acid cost, about 400 t a year are made, and
GFI's $10 a kilo for it is hypothetical. At today's quotes the floor would be about $2.35–2.45 a kilo of cells, not $2.00.

The floor is meant as a long-run price at industry scale, so $6.36 a kilo of amino acids is kept. That assumes new serine
capacity is built; comparable fermentation amino acids made at scale (threonine, lysine, valine) sell at $1–3 a kilo. The
band's top stays at $11.59 (GFI's low food-grade mean). A supplier's quote would settle it (TODO.md).
