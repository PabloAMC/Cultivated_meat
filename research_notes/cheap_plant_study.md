# Cheap-plant study: what animal cells need of a sterile plant, and how much contamination a cheaper one can afford

Compiled 2026-11-14. Calculations: `plant_items.py` (part 1), `contamination.py` (part 2), checked by
`tests/test_plant_items.py`, which also checks that the figures quoted here match the code. Sources are
numbered in section 7 with how each was read.

Conventions. Capital is total investment (equipment, installation, buildings, engineering, construction,
fees and contingency) per m³ of production tank, in Humbird's 2018 dollars unless a figure says "today's
prices" (× 1.33). Cost per kg is per kg of real wet cells, from `floor_physics.explore` at the floor's
settings: perfusion, 20 m³ tanks, 120 g/L, food-industry financing.

## 1. Answer in brief

1. **The fivefold gap is now itemised.** Humbird's animal-cell plant costs $683k per m³ and his own yeast
   plant with the same 20 m³ tanks $130k. The $553k between them is: the hall round the tanks $142k, the
   installed tanks $103k, the oxygen plant $85k, the seed train $80k, medium preparation $69k, cleaning and
   utilities $33k, labs and support buildings $34k, harvest $9k.
2. **About three fifths of the gap buys things animal cells do not need, or need less of.** The clean room
   (pharma itself no longer requires one round closed tanks), an owned oxygen plant (oxygen can be bought),
   seed capacity for a restart every 57 hours (runs of weeks need a fifth of it), and electropolish and
   triple probes on the tanks. Removing these gives a "lean" plant at $340k per m³ and cells at $9.0 per kg,
   against $11.5 at the floor.
3. **What animal cells certainly need is cheap in itself.** A yeast plant plus cell labs, sterilisation of all
   the medium and bought oxygen is $175k per m³ and $7.3 per kg. The open question between $175k and $340k is
   almost entirely the installed cost of a sealed, steam-sterilised tank with its piping, and how much
   cleaning plant goes with it.
4. **Contamination does not decide it at the loss rates seen today.** The lean plant stays cheaper than the
   floor's sterile plant until each tank loses a run about every 28 days (3.5% a day); the yeast plant with
   additions until one every 13 days (7.6% a day). Pharma loses about 0.2% a day. Cultivated-meat makers
   report 11 to 20% of batches, which is 0.6 to 2.2% a day if their batches run 10 to 20 days.
5. **Ordinary sensors stop the run but do not protect the product.** A contaminant needs about 51 doublings
   to show on oxygen readings: 17 hours at a 20-minute doubling time, 51 hours at 60 minutes. The food limits
   in the filings are crossed 6 to 17 hours earlier. So harvests must be held until the tank is known clean,
   and a contaminated tank is a lost tank unless a regulator accepts a kill step, which none has been asked to.

## 2. The plant, item by item

Humbird's fed-batch plant (24 × 20 m³; his Tables 4.1 to 4.3) and his yeast plant held to animal-cell limits
(27 × 20 m³; Table A.5) on one list of nine items. "Lean" and "yeast+" are defined in section 4.

| Item | Humbird | Lean | Yeast+ | Yeast | Humbird − yeast |
|---|---|---|---|---|---|
| Hall round the bioreactors | 152 | 46 | 10 | 10 | 142 |
| Production tanks, installed | 163 | 115 | 61 | 61 | 103 |
| Oxygen supply | 89 | 0 | 0 | 5 | 85 |
| Seed train | 109 | 42 | 30 | 30 | 80 |
| Medium preparation and sterilising | 71 | 38 | 38 | 2 | 69 |
| Cleaning system and utilities | 48 | 48 | 15 | 15 | 33 |
| Office, shop, warehouse, slab | 19 | 19 | 0 | 0 | 19 |
| Cell and quality labs | 15 | 15 | 15 | 0 | 15 |
| Harvest | 17 | 17 | 8 | 8 | 9 |
| **Total, $k per m³** | **683** | **340** | **175** | **130** | **553** |
| In today's prices | 909 | 452 | 233 | 172 | |

How the two totals are reproduced.

- **Animal-cell plant: exact.** Each line of Table 4.1 is carried to total investment by his own rules:
  bioreactors are bought installed (Eq. 3.1: $1,414k for 20 m³); other equipment is bare cost, plus 10% for
  minor items (as listed / 0.9), plus installation at 1.3 times on top; buildings are Table 4.2; then × 1.6
  for engineering and construction and × 1.15 for fees and contingency. The nine items sum to $327.9M, his
  Table 4.3, and the two sub-totals (ISBL $93.9M, OSBL $35.8M) are reproduced.
- **Yeast plant with 20 m³ tanks: reproduced with one solved number.** Humbird gives only the total, "$70M",
  in a column headed "equal CAPEX" (his standard plant is $68.7M), so the figure is rounded and partly set by
  construction. I rebuilt it from the equipment list of his standard plant (Table A.1): compressors,
  centrifuges, filters and feed equipment resized by the six-tenths rule to the smaller plant's oxygen, broth
  and feed flows (Table A.5), 27 production columns and 14 seed columns (Fig. A.4b), 20% for minor items, and
  his overall factor of 4.5. The vessel size exponent is then solved so the total is $70M. It comes out at
  0.49, an ordinary value (0.6 is the textbook default; with 0.6 throughout the rebuild gives $56M, 20% low).
  The factor of 4.5 is split across items as his Table 3.1 splits the lysine plant's factor. The split is my
  inference; the total is his.

Three things the itemisation corrects in what this repository said before.

- The earlier line-by-line comparison (`plant_capital_crosscheck.md`, part b) set the animal plant against the
  yeast plant with 200 m³ tanks. Its ratios (vessel 4 times, seed train 11 times, medium 22 times) are per m³
  against much larger tanks, not at the same tank size.
- At the same size the bare vessel is not the problem. A yeast-plant column of 20 m³ is about $266k bare; his
  sterile stirred tank is $330k (Table 3.3) to $403k (his note 127). The gap is in what is bolted on: a
  sterile tank installed is $1,414k, of which piping is $360k, instruments and electrical $476k,
  internals and seals $164k and surface treatment $132k.
- With engineering and contingency loaded on, the clean room is the largest single item ($152k per m³), not
  the roughly 10% that dropping it to a sanitary hall saves.

## 3. What animal cells need: the switches

Verdicts: **not needed**, **probably not needed**, **needed**, **unknown**. The same table is in
`plant_items.STATUS`.

| Step | Saves, $k per m³ | Verdict | Reason and evidence |
|---|---|---|---|
| Clean room → sanitary hall | 72 | Not needed | Pharma's own industry group argues closed, steam-sterilised steps can stand in unclassified space, and says several plants have done so with regulators' approval [7]. Humbird: "the clean room is a risk-reduction measure" for equipment whose sterility is self-contained [1]. CE Delft assumes none [2]. Vow runs a 20 m³ tank and reports none [9, 10]. An engineering firm calls clean rooms for cultured meat "not well-grounded" [8, search result]. |
| Sanitary hall → plain industrial building | 34 | Probably not needed | Same argument: the tank is the sterile boundary. Open steps (thawing cells, first seed steps, sampling) need a small clean area, which the labs provide. No direct evidence either way for animal cells at scale. |
| Building → outdoors, as a yeast plant | 36 | Unknown | Usual for amino-acid and yeast plants. Nobody has run animal cells outdoors. Small saving. |
| Cell and quality labs | 15 | Needed | The cell bank and first seed steps are open handling of a culture that cannot outgrow anything. UPSIDE's filing: "a production run will fail if the starting seed cells are not sterile" [14]. |
| Sterile packaged tank → food-grade sterilisable tank ($1,414k → $1,000k) | 48 | Probably not needed | Electropolish and triple probes are pharma habits; without them Humbird's own tank is about $1,190k. Vow says its tank cost "well under $1 million" [9], Meatly claims 95% off for a 320 L vessel [11, search result]. But these are company claims, and it is not stated whether Vow's figure includes piping and installation. |
| Food-grade stirred tank → yeast-plant column | 55 | Unknown | The largest unknown left. The tank must stay a sealed pressure vessel with steam, sterile gas and sterile feed lines, and that piping is most of its cost. Whether animal cells can do without a stirrer at 20 m³ is also open (Negulescu's airlift design assumes so [3]). No vendor price for a 20 m³ food-grade sterilisable fermenter was found. |
| Seed train for 57-hour cycles → two small trains | 67 | Not needed, for runs of ten days or more | Humbird sizes 8 final seed tanks because every production tank restarts every 57 hours. Twenty-four tanks on 10-day runs need 1.4 final seed tanks, on 33-day runs 0.5. Two small trains (one a spare) cost $42k per m³. Pasitka prices one seed train for a whole plant at about the same per m³ [5]. |
| Two seed trains → one | 21 | Needed | With one train, one contaminated seed stops every restart. |
| A makeup tank and filters per bioreactor → shared | 33 | Unknown | Shared lines are cheaper, but one failure reaches every tank on the line (section 5). CE Delft and Negulescu assume shared heat sterilisation of 90 to 98% of the medium [2, 3]; pharma does heat-treat media, with precipitation problems [12, search result]. |
| Sterilised medium → a pasteuriser | 36 | Needed | The medium is rich and neutral and the cells cannot outgrow anything, so all of it must be sterile. Amino acids and glucose cannot be heated together [1], so at least two streams. |
| Owned oxygen plant → bought oxygen | 89 | Not needed | Capital moves to running cost: $0.33 per kg of cells at an assumed $0.10 per kg of oxygen, against about $1.5 per kg for owning it at Humbird's capital loading. Pasitka prices an oxygen plant of 60% the size at less than a quarter of Humbird's figure [5], so his is high in any case. Bulk liquid oxygen is the supply described for pharma plants [13, search result]. |
| Oxygen → air | 0 (5 dearer) | Needed at the floor's density | At 120 g/L the cells need enriched gas under the bubbling limits. At 20 to 30 g/L air may do [13]. |
| Harvest, cleaning and utilities → as a yeast plant | 42 | Needed in some form; size unknown | Cells must be separated and tanks cleaned and steamed either way. Humbird's 12 × 42 m³ cleaning tanks may be generous: CE Delft prices one cleaning skid for a far larger plant [2]. |

Summing the "not needed" and "probably not needed" rows gives the lean plant. The rows marked unknown, plus the
labs, are the difference between lean and the yeast plant.

### Cross-check of items against the other studies

| Item | Humbird 2021 | CE Delft 2021 [2] | Negulescu 2023 [3] | Garrison 2022 [4] | Pasitka 2024 [5] |
|---|---|---|---|---|---|
| Production tank | $330k bare, $1,414k installed, 20 m³, 316L | $325k purchased, 12.5 m³; × 3.5 all-in | from $300k for 20 m³ in 304 steel, exponent 0.6 | no unit price | $2,200k for 25 m³, installed |
| Seed train | 24 vessels, 16% of the plant | only the 60 L step costed ($20M of $450M) | one train fills 10 tanks | one train per tank | one train per plant, $0.6–1.1M for 50 m³ |
| Medium | $15k per m³ bare | $1.6k per m³ purchased; 90% heat-sterilised | 98% heat-sterilised; cost in SI, not read | inside the quote | $16k per m³ |
| Oxygen | $8.8M for 25 kt a year | none listed | none in main text | none | $2.0M for 15 kt a year |
| Cleaning | $8.6k per m³ bare (tanks) | one skid, $3.5M purchased, whole plant | not in main text | three units, inside the quote | none listed |
| Building | Class 8 clean room, $3,760 per m² | none; inside the factor | not stated | leased warehouse | unclassified, but priced at $3,759 per m² |
| Factors | 1.3 × installation; × 1.84 indirect; 7.2 overall | about 3 overall | not in main text | none: all-in quote | 0.3 × installation; 5.4–7.1 overall |
| Whole plant, $k per m³ | 683 | 167–277 | 209 | 750 | 807–2,478 (perfusion) |

Reading. Nobody disputes the bare tank: three studies put a 12 to 20 m³ tank at $300k to $330k. The studies
differ in everything round it. CE Delft and Negulescu get plants at $170k to $280k by assuming an overall
factor of about 3 and no clean room, without itemising why. **Garrison is the evidence against a cheap plant**:
the only vendor quote in the set, from a food-grade equipment maker, comes to $750k per m³. It is for a small
plant (four tanks), with a full seed train for every tank, and the vendor gives ±30%; it shows that a
food-grade label alone does not make the plant cheap.

## 4. The named plants

| Plant | What it is | $k per m³ | Today's prices | Cells, $/kg (perfusion) | Cells, $/kg (drained and refilled) |
|---|---|---|---|---|---|
| Humbird's | every item as designed | 683 | 909 | $12.2 | $19.3 |
| The floor's | the same in a sanitary hall | 611 | 813 | $11.5 | $17.8 |
| Lean | plain building; food-grade tank at $1M; two small seed trains; shared medium lines; bought oxygen | 340 | 452 | $9.0 | $12.7 |
| Yeast+ | the yeast plant plus cell labs, shared sterilisation of all medium, bought oxygen | 175 | 233 | $7.3 | $9.4 |
| Yeast | every item as in his yeast plant | 130 | 172 | $6.5 | $8.2 |

The model's existing frontier class, $190k in today's prices from built microbial plants, sits between yeast
and yeast+. Bought oxygen is charged at $0.33 per kg in the lean and yeast+ plants. Each $100k per m³
is worth about $1.0 per kg at the floor's output.

Two cautions. The lean plant's seed train suits runs of ten days or more, not Humbird's two-day batches. And
the item list is the fed-batch plant's; the floor is a perfusion plant that adds a device to hold cells back
($89k per m³), which is the same in every row.

## 5. Contamination as dynamics

### What happens in the tank

- **Nothing the cells do holds a contaminant back.** It doubles in 20 to 60 minutes; the cells double in a
  day. Perfusion at about one tank volume a day cannot wash out something that multiplies 24 to 72 times
  faster. Yeast plants tolerate bacteria because yeast is fast, the broth is acid and batches last 16 hours.
  None of that applies. So the only defences are keeping it out, seeing it early, and affording the loss.
- **Time to detection.** From one cell in a 20 m³ tank to a density that sensors see takes
  log2(threshold × volume) doublings. Oxygen and off-gas readings see a contaminant when it shifts the tank's
  oxygen uptake by about 5% [assumed]. A dense culture hides more: the threshold is about 2 × 10⁸ bacteria
  per mL at 120 g/L and 4 × 10⁷ at 27 g/L. That is 51 doublings: **17 hours** at a 20-minute doubling time,
  **51 hours** at 60 minutes. The literature's "18 to 24 hours at the earliest" for gross contamination
  agrees [17, search result]. The result is insensitive: a threshold five times lower saves two doublings; a
  tank a thousand times smaller saves ten.
- **Slow organisms are the exception.** At a 6-hour doubling time (mycoplasma [16]) the same sum gives 13
  days. In the measured case the readings moved 1 to 5 days after a spike of 15 to 300 cells per mL [16].
  Some pass 0.2 µm filters and give no oxygen or pH signal at all (the Leptospira case at Genentech [18,
  abstract]). These are not caught by sensors; they are caught by testing the seed.
- **What is lost at detection.** The contaminant is then about 0.2% of the biomass. The cells are all still
  there. The loss is regulatory, not physical.
- **The product is over the limit before the sensors see anything.** Harvest specifications in the filings
  are 10² to 10⁴ cells per gram (UPSIDE under 100 [14], GOOD Meat under 1,000 [15], Vow under 10⁴ [10]).
  The tank crosses 10⁴ per gram of cells about 6 hours before detection for a fast contaminant and 17 hours
  for a slow one. With continuous harvest, that product has already left the tank.
- **Salvage has no precedent.** All three filings treat the tank as sterile; Vow's says batches outside the
  limits "will be discarded" [10]. Raw meat at the end of its shelf life carries 10⁶ to 10⁷ per gram [19],
  so a cooked product from a tank stopped at 10⁸ per mL is not absurd on counts, but toxins are unaddressed
  and no regulator has been asked. Salvage is a lever in the model (`salvage`), set to zero.

### Routes, and which ones scale with what

| Route | Scales with | Evidence |
|---|---|---|
| Seed and start-up | each start | UPSIDE: a run fails if the seed is not sterile [14]. A seed stage of 57 hours passes a 20-minute contaminant on unseen 30% of the time and a 60-minute one 90% (it enters too late to show before transfer). |
| Seals, gas filters, valves | each day the tank runs | Merck's pilot plant cut contamination by replacing diaphragm valves and re-piping [20, abstract]. |
| Feeds and medium | litres fed; and every tank on a shared line | Cultivated-meat makers name media and consumables in 23% of nominations [6]. |
| Sampling and harvest | each event | "Anytime you open the sterile envelope" (Vow's chief executive, on daily sampling) [9]. Exposure during harvest was named by half the survey's respondents [6]. |
| People, equipment preparation | each start and intervention | 55% of nominations in the survey; improper equipment sterilisation the most named single cause [6]. |

No source gives rates per route. The model therefore takes two numbers: a chance per day while the tank runs
(`hazard`) and a chance per start (`start_fail`).

### Shared seed trains and medium lines

If the chance of a failure is per vessel or per line, sharing does not change the expected number of tanks
lost: one seed vessel feeding three tanks loses three tanks with the chance that three separate vessels would
each lose one. What sharing changes is that losses come together, and then the tanks queue to restart. A seed
train with two final seed tanks starts 2.5 tanks a day. If all 24 tanks go down at once the average tank waits
4.5 days more; that lowers the lean plant's break-even from 3.5% to 2.8% a day. So the lean plant's cheap seed
train and shared medium lines cost it about a fifth of its tolerance, not the whole of it. What would hurt
more is a slow organism in the seed train that is passed to every tank before any test shows it: the model
does not price that, and a spare train and a tested cell bank are the protection.

### Break-even loss rates

The chance per day of losing a run at which a cheaper plant costs the same per kg as the floor's sterile plant
losing runs at pharma's 0.2% a day. Fourteen days to restart after a loss; nothing salvaged.

| Run length planned | Lean | Yeast+ | Yeast |
|---|---|---|---|
| 5 days | 5.1% a day (one loss per tank every 20 days) | 10.7% (9 days) | 13.4% (7 days) |
| 10 days | 4.2% (24 days) | 9.0% (11 days) | 11.4% (9 days) |
| 20 days | 3.7% (27 days) | 8.0% (12 days) | 10.3% (10 days) |
| 33 days | **3.5%** (28 days) | **7.6%** (13 days) | **9.7%** (10 days) |
| 60 days | 3.3% (30 days) | 7.2% (14 days) | 9.3% (11 days) |

The threshold barely moves with run length once runs are longer than the time between losses, because the
loss then ends the run whatever was planned. Drained-and-refilled tanks tolerate more (lean 4.7%, yeast+ 10.2%
at 33 days) because their capital per kg is higher, so a cheaper plant saves more.

What moves the 33-day threshold:

| Change | Lean | Yeast+ |
|---|---|---|
| Base | 3.5% | 7.6% |
| 30 days to restart, not 14 | 1.9% | 4.2% |
| All 24 tanks lost together, two seed tanks | 2.8% | 6.1% |
| Cells of a lost run salvaged | 4.3% | 9.9% |
| Or, with running losses at pharma's rate, the share of starts that may fail | 51% | 71% |

### What the reference rates imply

| Reference | Batches lost | Per day | Against the thresholds |
|---|---|---|---|
| Pharma, plants over 1,000 L [21] | 2.3% (3.2% in 2022) | 0.17–0.23% | 15 to 40 times under |
| Cultivated meat, all respondents [6] | 11.2% (range 0–52%, 11 companies) | 0.6–1.2% if batches ran 20 or 10 days | 3 to 12 times under |
| Cultivated meat, beyond flasks [6] | 19.5% (6 companies) | 1.1–2.2% | 1.6 to 7 times under |

At 1.5% a day the lean plant makes cells at $10.1, yeast+ at $8.0 and the yeast plant at $7.1, against $11.7
for the floor's plant at pharma's rate. So if the cheaper plants can be built at these prices and lose runs
no more often than cultivated-meat makers do today, in whatever plants they have, they win. The survey's worst
respondent (52% of batches) would be over the lean threshold if its batches ran under about 20 days.

Limits of this. The survey is 11 companies, gives no run lengths or tank sizes, and pharma's loss rate is
three times higher above 1,000 L than below [21], so rates at 20 m³ may be worse than the survey's. Perfusion
adds a route (the retention device and its flows) that nobody has operated at this size. And these are
thresholds: the model says what a plant must achieve, not what it will.

## 6. Judgement

- **Probability that a plant at or under $450k per m³ in today's prices (the lean plant) can run animal cells
  at 20 m³ under its break-even loss rate: about 65%** (range 45–80%). It needs nothing undemonstrated in
  kind; the doubt is whether "well under $1 million" for a tank holds with piping and installation.
- **Probability for a plant at or near yeast-style cost, taken as $250k per m³ or less in today's prices
  (yeast+ is $233k; the model's frontier $190k): about 30%** (range 15–45%). It hinges on two things, in
  this order: (a) the installed cost of a sealed, steam-sterilised 20 m³ tank with its sterile piping in a
  food-grade build, which must come to roughly $500k to $650k against Humbird's $1,414k and Vow's "under $1
  million"; (b) that such a plant keeps losses under about 7% a day, which I rate likely (about 75%) given
  that today's makers report 0.6 to 2.2%.
- **The loss rate it must stay under: one run per tank every two weeks (7.6% a day) at yeast+ cost, every
  four weeks (3.5%) at lean cost.** Half those if a loss takes a month to recover from.
- **The measurement that would settle it:** the as-built cost of one food-grade 20 m³ line, split into tank,
  piping and instruments, seed vessels, medium sterilisation and cleaning, together with its run log (runs
  started, days run, runs lost and to what). Vow holds both. Short of that, one vendor quote for a 20 m³
  sterilisable food-grade fermenter with its piping settles item (a), which is worth about $55k per m³ and
  $0.6 per kg on its own.

What I am least sure of: the split of the yeast plant's cost across items (my inference from one total); the
lean plant's shared medium lines (no evidence either way); the oxygen price (assumed); and two bacterial
constants taken from memory (oxygen uptake and cell mass), which move the detection time by under 10%.

## 7. Sources and how each was read

| # | Source | Read as |
|---|---|---|
| 1 | Humbird, D. (2021) *Scale-up economics for cultured meat: techno-economic analysis and due diligence* (long report). Tables 3.1–3.3, 4.1–4.3, 4.8–4.10, A.1, A.5; Figs 4.3, A.4; notes 127, 144; sect. 2.4, 3.1, 4.1 | Full text (local extract) |
| 2 | Vergeer, Sinke, Odegard (CE Delft, 2021) *TEA of cultivated meat*. Table 2, sect. 2.3, Annex C | Full text (local extract) |
| 3 | Negulescu et al. (2023) *Biotechnol. Bioeng.* 120:1055, doi 10.1002/bit.28324 | Full text of the main paper (local extract); supplementary tables not read |
| 4 | Garrison, Biermacher, Brorsen (2022) *J. Agric. Food Res.* 10:100358 | Full text (local extract) |
| 5 | Pasitka et al. (2024) *Nature Food*, doi 10.1038/s43016-024-01022-w, Supplementary Tables S1–S4 | Full text (local extract) |
| 6 | Powell, Li, Smith, Chen (2025) "Cultivated meat microbiological safety considerations and practices", *Compr. Rev. Food Sci. Food Saf.*, doi 10.1111/1541-4337.70077 | Full text (PMC11681928) |
| 7 | Johnson et al. (BioPhorum, 2011) "Challenging the cleanroom paradigm for biopharmaceutical manufacturing of bulk drug substances", *BioPharm International* | Full text |
| 8 | CRB, "Cultured meat" (engineering firm's web article) | Search result only (page refused) |
| 9 | AgFunderNews (2025) "Humbird was 'spectacularly wrong' on cultivated meat economics, says report, as Vow predicts it will soon be unit margin positive" | Full text |
| 10 | FSANZ (April 2025) Application A1269, Supporting Document 1, risk assessment (Vow's cultured quail) | Full text |
| 11 | Food and Drink Technology (May 2025) "Meatly reduces bioreactor costs by 95%" | Search result only |
| 12 | Amgen authors (2013) on heat treatment of cell-culture media, *PDA J. Pharm. Sci. Technol.* 67(1):63 | Search result only |
| 13 | Muralidharan et al. (AGC Biologics, 2024) on oxygen transfer in a 20,000 L bioreactor, *BioProcess International*; a gas supplier's page on bulk liquid oxygen | Full text; search result |
| 14 | FDA (Nov 2022) scientific memo, cell culture consultation CCC 000002 (UPSIDE Foods) | Full text |
| 15 | FDA (2023) scientific memo CCC 000001 and GOOD Meat's dossier | Full text |
| 16 | Fratz-Berilla et al. (2019) mycoplasma in CHO perfusion, *Biotechnol. Bioeng.* (PMC6900124) | Full text |
| 17 | Linderholm et al. (2025) *Anal. Bioanal. Chem.* 417:1165 | Abstract and search result |
| 18 | Chen et al. (2012) Leptospira licerasiae at Genentech, *PDA J.* 66(6):580 | Abstract |
| 19 | FSANZ 2022 and Singapore Food Agency figures for raw meat, as cited in [6] | Second-hand, through [6] |
| 20 | Junker et al. (2006) "Sustainable reduction of bioreactor contamination in an industrial fermentation pilot plant", *J. Biosci. Bioeng.* 102:251 | Abstract only; its rates and causes by route could not be read |
| 21 | Langer (2008) "Biotech facilities average a batch failure every 40.6 weeks", *BioProcess International* (BioPlan survey, 145 organisations); 2022 figures as quoted in GFI's 2024 bioprocessing survey | Full text; second-hand |
| 22 | Lever VC (April 2025) "A second generation of cultivated meat companies breaks through projected cost barriers" | Full text, read in part |
| 23 | BioNumbers 103514 (E. coli doubling time) | Search result |

Looked for and not found: a vendor price for a 20 m³ food-grade sterilisable fermenter; contamination rates
by route for any industrial fermenter (Junker 2006 and the survey in Stanbury's textbook are behind paywalls);
contamination rates for plant-cell, insect-cell, microalgal or veterinary-vaccine plants; run lengths and tank
sizes behind the cultivated-meat survey; the contaminant density at which oxygen or pH readings move (derived
here instead); a named pharma plant with bioreactors in unclassified or outdoor space; the price of bulk
oxygen. Two searches naming a veterinary vaccine were refused by the model's safeguard and were not pursued.
Stated from memory and not verified: bacterial oxygen uptake (10–20 mmol per g dry per hour) and cell mass
(0.3 pg dry); that pharma production batches last 10 to 14 days.
