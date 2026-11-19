# What caps the sparge gas flow in a large animal-cell tank

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50.

> **Current figures** (`floor_physics.explore`, 2026-11-19). The costs in the body were computed on 2026-11-14, when the case
> called "the floor" (now the reference case) was $11.5; since then the filter loop, the bubble protectant, antifoam's cut to oxygen
> transfer and the $2.00 nutrient floor have been added. Now, with the body's figures in brackets: the reference case at 6 mm/s
> $12.81 ($11.5); at 5 mm/s $13.70 ($13.1); at 2 mm/s $29.49 ($28.0); at 9 mm/s $11.33 ($8.7); at 0.5 mm/s $113 ($100); with the
> exhaust 70% saturated with CO₂ $14.59 ($14.6), 85% $13.39 ($12.6). The protectant is now charged ($0.67 a kilo at $30/kg). The
> 45% odds on 6 mm/s and the 2 / 5 / 9 mm/s range are unchanged.

Research note, compiled 2026-11-14. Reading, search and arithmetic only; no experiment.

**The question.** The floor ($11.5/kg) holds 120 g/L of cells in a 20 m³ stirred tank. That density is set by CO₂
removal, which is proportional to the gas bubbled through the tank. The model takes Humbird's limit, a gas
velocity of 6 mm/s (0.1 tank volumes of gas per minute, "vvm", at 20 m³). This note asks where that limit comes
from, what physically caps the gas flow, and what range is defensible at 20 m³ and 120 g/L.

**Reference case used throughout** (from `floor_physics.py`): 16 m³ of liquid, tank 2.34 m wide, liquid 3.74 m
deep, 4.28 m² cross-section, stirring power about 43 W/m³. At 6 mm/s that is 93 m³ of gas an hour, 0.096 vvm,
5.8 volumes of gas per volume of liquid per hour.

**How each number was read.** FT = full text read (by me or by a reading agent in this session). ABS = abstract
only. SNIP = search-engine summary only. 2nd = reported by another paper that was read. VEND = vendor or
regulatory document, read. CALC = my arithmetic. Numbers in square brackets refer to the source list at the end.
About half of the primary papers are paywalled and were read as abstracts; this is stated source by source.

---

## For the experiments list

Floor figures are from `floor_physics.explore` with only the named argument changed from the floor case
($11.5/kg). Costs and times of experiments are my rough estimates, not quotes.

**1. How much gas a large, dense tank can take**
- Unknown: whether a 20 m³ tank of cells at 120 g/L can be bubbled at 6 mm/s (0.1 volumes of gas per volume of
  liquid per minute) without foam or bubble damage stopping it.
- Worth: resolves well, $11.5/kg (`gas_velocity=0.006`), or $8.7 if 9 mm/s works (`gas_velocity=0.009`);
  resolves badly, $28.0/kg (`gas_velocity=0.002`, the most that has been run with cells). At my central
  5 mm/s, $13.1.
- Probability it resolves well (6 mm/s usable): about 45%. Bubble damage looks manageable with a protectant
  (75–80%), but foam grows with gas velocity and has never been measured against it in a cell culture.
- Deciding experiment: in a tall vessel (2–4 m of liquid, 100–500 L, ring sparger with 1–2 mm holes), step the
  gas through 1, 2, 4, 6 and 9 mm/s for two to three days each, in perfusion at 50 million cells per mL or
  more, and measure death rate, foam height, antifoam needed per day, oxygen transfer and CO₂ in liquid and
  exhaust. CHO cells first, then a suspension-adapted meat line (chicken fibroblasts are the only one shown
  at this density). A cheap first stage needs no live culture: foam height against gas velocity in spent
  medium from a dense culture, with and without antifoam.
- Rough cost and time: first stage $20–50k and 1–2 months; the full run $300–800k and 6–12 months, mostly
  medium and pilot-plant time. Who: a contract manufacturer or university pilot plant with a 200–500 L
  stainless tank that can be fitted with a tall column (pharma process-development groups, bioprocess
  institutes), or a cultivated-meat company with a pilot tank.
- Evidence strength today: measured in pharma cells only, and only up to about 3 mm/s and 200 L; inferred
  above that. Nothing in meat cells.

**2. How much CO₂ each volume of gas carries out**
- Unknown: how close to saturated with CO₂ the gas leaves a 3.7 m deep tank at this gas flow (the model
  assumes 96%).
- Worth: resolves well, $11.5/kg (96%); resolves badly, $14.6/kg at 70% (`x_scale=0.7/0.9605`); $12.6 at 85%.
- Probability it resolves well (90% or more): about 40%. Bubbles of 2–5 mm should saturate in 3–4 s and rise
  for 5–15 s, but drilled-hole spargers in shallow tanks measured 42% of the ceiling, which scales to about
  80% at this depth.
- Deciding experiment: CO₂ stripping from cell-free medium (with protectant and antifoam) in a tank or column
  with 3–4 m of liquid, at 1 to 9 mm/s, measuring CO₂ in the liquid and in the exhaust. No cells needed. It
  comes free with experiment 1.
- Rough cost and time: $20–60k and 1–2 months alone. Who: any group with a tall pilot vessel and an exhaust
  gas analyser; the Hamburg group that runs the transparent 15 m³ pharma tank has the equipment and has
  measured this up to 0.95 mm/s.
- Evidence strength today: measured without cells up to 0.95 mm/s at 15 m³ and in tanks up to 2 m³; inferred
  at 6 mm/s.

**3. Whether meat cells can be protected from bubbles with something cheap and allowed in food**
- Unknown: whether muscle, fibroblast or fish cells are protected by poloxamer 188 as CHO cells are, at what
  dose, at what bulk price, and whether its residue is accepted in food.
- Worth: resolves well, $11.5/kg plus $0.2–1.1 for the protectant at an assumed bulk price of $10–20/kg (not
  in the model). Resolves badly on price, plus $3.6–9/kg at the only price found (catalogue, $165/kg).
  Resolves badly on protection, the gas flow is limited to about 0.5 mm/s and the sparged tank is not viable
  ($100/kg at `gas_velocity=0.0005`).
- Probability it resolves well: about 70%. The mechanism (it stops cells sticking to bubbles) is not specific
  to a cell type and one cultivated-meat maker already uses it at 1 g/L with residue below detection, but no
  measurement exists for meat cells, the dose needed rises with cell density, and cartilage cells took up
  five times more of it than CHO.
- Deciding experiment: bench bubble columns (0.1–1 L) with a meat cell line in suspension, death rate against
  gas flow at 0, 0.5, 1, 2 and 5 g/L of poloxamer and of food-grade alternatives (methylcellulose), plus
  supplier quotes for tonne lots and a residue measurement in washed cells.
- Rough cost and time: $30–80k and 2–3 months. Who: any cell-culture lab with a suspension meat line; the
  quotes need only emails to two or three suppliers.
- Evidence strength today: measured in pharma, hybridoma and insect cells only; nothing in meat cells.

**Highest gas velocity actually demonstrated with animal cells, by scale**

| Scale | Highest found with cells | Cells per mL | Access |
|---|---|---|---|
| Bench, under 10 L | under 1 mm/s (0.07–0.2 vvm) | 60–80 million | abstract, vendor notes |
| 40–200 L | about 1.5–2.8 mm/s (0.06–0.2 vvm; velocity rests on a tank geometry I assumed) | 60–264 million | abstract, vendor notes |
| 1–5 m³ | 0.012–0.02 vvm; velocity not computable (tank dimensions not given), probably under 1 mm/s | 30–40 million | vendor notes |
| 8–25 m³ | "typically" 0.1–2 mm/s (Nienow's range); the one run with numbers is 0.2 mm/s at 8 m³ | up to about 10 million | full text |
| Any scale at 6 mm/s | none found | | |

Equipment is rated higher than it has been run: 2.5–5 mm/s at 2 m³ (datasheets, no cells).

**Do the cost and food status of the protectant change the answer?** They do not change what caps the gas
flow, but they can change the floor. Without a protectant the sparged design fails outright. With one, the
cost is somewhere between $0.2 and $9 per kg of cells depending on a bulk price nobody has published, and it
is not a clearly permitted food additive in the US (the one filing that names it relies on residues below
detection); EU status was not verified. So it belongs on the experiments list as a quote and a residue test,
not as a physics question.

**Which way this points for the membrane loop.** The evidence does not show that sparging can run at the
model's default velocity: I put that at about 45%, and at my central 5 mm/s the floor is $13.1, not $11.5. So
a membrane loop is not made redundant; it remains a hedge worth pricing against a roughly even chance that the
sparged tank must run thinner. Two things soften this. First, the most likely cap is foam, and a loop that
only removes CO₂ still leaves the oxygen to be sparged, so it lowers the gas flow needed but does not remove
foam. Second, if experiment 1 shows 6 mm/s works, the loop's case rests only on going beyond 120 g/L.

---

## Summary

1. **The 6 mm/s limit is not a measured threshold.** Humbird (FT [1]) writes that guidance on maximum sparge
   rate is "usually <0.1 vvm", citing Ozturk 1996 and Pörtner 2015, and converts 0.1 vvm to 6 mm/s for his 20 m³
   tank. Neither cited source could be read (both paywalled). The only independent restatement found says
   Ozturk attributes the limit to "cell lysis and foaming" with no scale or cell density (2nd, via [5]). Humbird
   himself says 0.01 vvm is what is common and calls the limits "dubious" and possibly "needlessly
   conservative" (FT [1], Sect. 5).
2. **Nothing found is a hard physical cap near 6 mm/s.** Of the six mechanisms, four are design items
   (hold-up, evaporation, exhaust, gas cost). Two can bind: bubble damage, which depends on the protectant, and
   foam, which nobody has measured against gas velocity in a cell culture.
3. **Bubble damage scales with gas per litre of culture (vvm), not with gas velocity, and so does CO₂ removal.**
   So what small tanks tolerate in vvm should carry over to large ones as far as this mechanism goes. With
   2 g/L of protectant and millimetre bubbles, 0.2 vvm did no harm at 60–80 million cells per mL in tanks up to
   200 L (ABS [20]). Without protectant, 0.1 vvm would kill cells about ten times faster than they grow.
4. **Foam is the most likely binding limit, and it scales with velocity.** At 20 m³, 0.1 vvm puts 2 to 4 times
   more gas through each square metre of surface than any run with cells that was found. Dense perfusion
   cultures already foam heavily at lower velocities, and the antifoam used to control it accumulates, slows
   growth above about 50 ppm, fouls filters and is limited to 10 ppm in US food.
5. **No published run combines high density with gas flow near the limit at scale.** Tanks of 1 to 25 m³ are
   reported at 0.002–0.02 vvm and 7–40 million cells per mL. Runs at 0.05 vvm or more with 50 million cells per
   mL or more exist only at 200 L or less, which is 1–3 mm/s. No culture at 6 mm/s was found at any scale.
6. **Defensible range: 2 / 5 / 9 mm/s** (low / my central estimate / high). My probability that 6 mm/s is usable
   at 20 m³ with cells at 120 g/L is about 45% (I would not defend a figure outside 30–60%).
7. **The model keeps 6 mm/s for the floor**, because the floor takes the favourable end of each range and the
   evidence neither refutes 6 mm/s nor supports a specific lower number. The tornado range becomes 2–9 mm/s.
   At my central 5 mm/s the floor is $13.1/kg; at 2 mm/s, $28.0; at 9 mm/s, $8.7.
8. **Three costs or limits the model does not carry were found on the way**: the protectant (poloxamer 188) is
   not costed and is not a clearly permitted food additive; antifoam may cut oxygen transfer by up to half; and
   the exhaust gas may leave less saturated with CO₂ than the model's 96%. They are listed under "Follow-ups".

---

## 0. Where the 0.006 m/s comes from

| Item | What it says | Source, access |
|---|---|---|
| Humbird, Sect. 1.2 | Typical limits for animal cell culture are "~0.01 vvm and ~100 W/m³" (against ~2 vvm for fermentation) | [1] FT |
| Humbird, Sect. 2.3 | Guidance on maximum sparge rate "is usually <0.1 vvm", citing Ozturk 1996 and Pörtner 2015; margin note: "0.01 vvm is common" (citing Nienow 2010), and protectant at more than 0.5 g/L is recommended in vigorously sparged cultures | [1] FT |
| Humbird, Sect. 2.3 | He recasts the limit as a superficial velocity of 0.006 m/s at the top of the vessel, equal to 0.1 vvm in a 20 m³ tank of his shape with 5 psig back pressure | [1] FT. CALC check: 0.1 vvm of standard gas on 16 m³, at 37 °C and 1.34 bar, over 4.28 m² is 5.3 mm/s; on the full 20 m³ it is 6.7. Consistent |
| Humbird, Sect. 5 | The limits "generally exceed the requirements of typical cell-culture processes"; at these extremes they are "dubious" and may be "needlessly conservative" (citing Nienow 2006) | [1] FT |
| Ozturk 1996 | Not readable (paywalled, not in PubMed Central). The abstract has no gas-flow number | [2] ABS |
| Ozturk 1996, as restated | Cell lysis and foaming limit sparging to about 0.1 vvm. No scale or density | 2nd, via Sieblist 2011 [5] (one passage, read by automated extraction) |
| Pörtner 2015 | Not readable. Abstract has no numbers | [3] ABS |
| Nienow 2006 | No numeric maximum anywhere. Typical in 8–20 m³ tanks: velocity 0.1 to 2 mm/s, 0.005–0.01 vvm; 0.003 vvm at 20 m³. The upper limit on velocity with protectant present "is not established" and cannot be tested at bench scale; he calls for pilot-scale work including foam | [4] FT |
| Xing 2009 (source of the oxygen-transfer formula) | Not readable. The range of gas velocity it was fitted over was not found. A later paper says its data lie below the usual range for such correlations (2nd, via [6]); so using it at 6 mm/s is probably an extrapolation (my estimate 80%) | [7] ABS |

**Conclusion.** The 0.1 vvm figure is a rule of thumb from the 1990s. Humbird turned it into a velocity for one
tank. Converting it to a velocity matters: 0.1 vvm is 6 mm/s at 20 m³ but under 1 mm/s in a bench tank, so a rule
written for small perfusion tanks says nothing about 6 mm/s. Nienow's statement that the limit is not
established is the most authoritative thing found, and nothing published since changes it.

---

## 1. Cell damage from bubbles

### At the surface, where bubbles burst

**Physics.** Cells stick to rising bubbles and are carried to the surface. When the bubble's film bursts, the
liquid around it is torn apart at 10⁷–10⁹ W/m³ for 1–2 mm bubbles (2nd, via [8] FT), enough to kill cells
(10⁶–10⁸ W/m³ for CHO, [9] FT). Damage in the bulk liquid is not the issue: with the free surface removed, cells
without any protectant tolerated sparging plus hard stirring ([10] ABS).

**Scaling law (the Tramper "killing volume" model).** Each volume of gas kills the cells in a fixed volume of
liquid, X′ (m³ of liquid per m³ of gas). Deaths per hour as a fraction of the culture:

    k_d = X′ × (gas flow / liquid volume) = X′ × vvm × 60        [per hour]

read in full in van der Pol's thesis ([11] FT, chapters 2–3), which reproduces the published papers. It was
validated at bench scale: k_d was linear in gas flow, in 1/height and in 1/diameter². X′ does not depend on
bubble size above 2 mm; bubbles of 0.2–1.6 mm are worse ([11] FT). The authors' own caution: no such model had
been validated beyond small pilot scale ([12] ABS).

**What this means for the model.** CO₂ removal is also proportional to gas per litre of culture. So the density
a tank can hold and the death rate from bursting bubbles rise together, in a ratio that does not depend on tank
size or shape:

    at the CO₂ limit:  k_d / growth rate = X′ × (gas volume needed per kg of cells) × density

At the floor case the tank passes 5.8 volumes of gas per hour, so k_d = 5.8 × X′ per hour, against a growth rate
of 0.029 per hour.

| Condition | X′ | k_d at the floor's gas flow, per hour | Share of growth lost | Source, access |
|---|---|---|---|---|
| Serum-free, no protectant (hybridoma) | about 0.05 | 0.29 | cells die 10 times faster than they grow | k_d from [11] FT; X′ CALC |
| No protectant (insect cells, single 3.5 mm bubbles, about 1,050 cells lost per bubble) | about 0.047 | 0.27 | same | [13] ABS; X′ CALC |
| 10% serum + methylcellulose (insect cells) | 0.004 | 0.023 | 80% | [11] FT |
| 2.5–10% serum (hybridoma) | 0.012–0.002 | 0.07–0.013 | 45% to all | [11] FT |
| A good polymer protectant at 1 g/L (PEG 6000; hybridoma) | at most 0.0005 | at most 0.003 | at most 10% | [11] FT, Table 1 of ch. 5: k_d fell from 107.5 to 1.0 × 10⁻⁵ per s. The author warns the low values are at the limit of what he could measure, so this is an upper bound |
| Poloxamer above 0.5 g/L, as assumed in a 2026 cultivated-meat model | 0.0004 | 0.0023 | 8% | Brorens et al. 2026 [14] FT, citing Jöbses 1991 (not read) |

So bubble damage rules out the floor's gas flow without a protectant, and with one it costs 10% of growth or
less, if bench numbers hold. A death rate of a quarter of the growth rate would be reached at X′ = 0.0005 at
about 0.24 vvm, which is 14 mm/s in the 20 m³ tank; with weak protection (X′ = 0.004) at 0.03 vvm, 1.8 mm/s.

**Protectant (poloxamer 188, sold as Pluronic F-68).**
- Mechanism: it stops cells sticking to bubbles. The time a cell needs to attach rises from 0.05–0.5 s to 5–20 s
  ([15] ABS); at 1 g/L bubbles are coated at their source ([16] ABS).
- Dose-response for poloxamer itself: no full curve found. One study (human PER.C6 cells): cells carried per
  bubble fell from about 1,000 at 0.001 g/L to about 120 at 3 g/L ([17] ABS).
- Direct test at high density: CHO perfusion at 60–80 million cells per mL, 3 L and 200 L tanks. With 2 g/L and
  a sparger of 0.5 mm drilled holes, no damage at about 0.20 vvm. With a 20 µm sintered sparger, 2 g/L was not
  enough at 0.025 vvm; 5 g/L protected up to about 0.10 vvm ([20] ABS; the abstract does not say which scale the
  0.20 vvm condition was run at).
- Does damage per unit of gas fall at high density? **No evidence that it does.** The chance that an attached
  cell dies is independent of cell concentration, and more cells are trapped in foam per bubble as density
  rises ([17] ABS). Cells also take the protectant up: 11.7 µg per million CHO cells ([18] ABS), which
  extrapolates (far outside the measured range, CALC) to 0.6 g/L at 50 million cells per mL. Cartilage cells
  took up five times more ([18] ABS), a warning for primary-like meat cells. Practice in dense perfusion is up to
  5 g/L ([19] ABS), ten times Humbird's 0.5.
- Foam entrapment: at 10 million cells per mL and 1 g/L, about 1,000 cells per bubble were still carried into
  the foam layer ([17] ABS, via [8] FT). CALC: that is about 0.1 µL of culture per bubble; for 3 mm bubbles at
  the floor's gas flow about 4% of the culture passes through the foam each hour. If those cells died it would
  exceed the growth rate; if the foam drains back quickly they survive. This links damage to foam (section 2).
- Meat-relevant cells (muscle, fibroblast, bird, fish): **not found**; Brorens et al. say the same ([14] FT).

### At the sparger, where bubbles form

Damage follows the gas velocity through the sparger holes, not the total flow. NS0 cells: death rate rose from
0.04 to 0.18 per day as hole velocity went from 2.3 to 82.9 m/s, with a threshold near 30 m/s; more protectant
did not help ([21] ABS). CHO: above 60 m/s proposed; 170 m/s harmed a 12,000 L culture and holes plug during a
run ([22] ABS). Vendors design to 15–23 m/s ([23] VEND). CALC for the floor case: 20 L/s at the sparger needs
6.7 cm² of holes to stay under 30 m/s, about 210 holes of 2 mm; at 15 m/s, about 430. **A design item, not a
cap**, but it means a ring or grid with hundreds of holes, not the open pipe pharma tanks use. One 20,000 L
pharma tank reaches its 60 m/s criterion at only 0.012 vvm with its existing sparger ([24] FT).

### Bubble size

Per unit of gas, small bubbles do more harm. Simulation: the liquid volume exposed to more than 10⁷ W/m³ is 49%
of the bubble's volume for a 0.2 mm bubble and 4.6% for a 1 mm bubble (1.9% with surfactant) ([9] FT). The
experiment above agrees: the sintered sparger needed 2.5 times the protectant for half the gas flow.

**Number for this mechanism.** With 2–5 g/L of poloxamer and drilled holes: low 2 mm/s (weak protection, as with
serum only), central 14 mm/s, high above 20. Without a protectant: under 0.5 mm/s. Confidence that surface
damage does not bind at the floor's gas flow, given protectant and millimetre bubbles: about 75–80%.

---

## 2. Foam

**Physics.** Foam is made at the surface in proportion to the gas arriving per square metre, which is the
superficial velocity. A simple rule (Bikerman) puts the standing foam height at a "foaminess" time multiplied by
the velocity (from memory; no foaminess value for cell-culture broth was found). So foam, unlike bubble damage,
gets worse with tank size at fixed vvm: 0.1 vvm is under 1 mm/s in a 3 L tank and 6 mm/s at 20 m³.

**Evidence.**

| Finding | Source, access |
|---|---|
| Foam height against gas velocity in cell-culture medium with cells: **not found** | |
| Without antifoam most animal-cell cultures foam; 500 mg/L of secreted protein is enough; "the effect of scale-up on foaming cannot be predicted" | Varley and Birch 1999 [25] FT (keyword passages) |
| 1,000 L CHO tank at 0.002–0.01 vvm: older runs showed "excessive foaming" and were harvested early | Mostafa and Gu 2003 [26] ABS |
| 230 mL perfusion at 80 million cells per mL: 0.07 vvm of oxygen "caused excessive foaming" (velocity under 0.2 mm/s) | [27] VEND |
| 3 L and 50 L CHO perfusion at 85–100 million cells per mL: the gas flow needed causes "excessive foaming"; antifoam fed continuously or the tank foams out; risk named is foam wetting the exhaust filter and loss of sterility | Madabhushi 2025 [28] FT |
| Same study: the silicone antifoam does not pass the 0.2 µm cell-retention filter and builds up to 250–500 ppm; it fouls the filter from 75 ppm and blocks it at 500; growth falls above about 50 ppm; a run with 24 times less antifoam kept viability above 90% for 28 days against a fall to about 55% | [28] FT |
| 40 L tanks at 160–264 million cells per mL ran at 0.06–0.2 vvm of oxygen with antifoam dosed by a foam sensor; viability about 95%; one run ended on filter fouling | Thermo notes [23] VEND |
| Antifoam doses that did no harm: 30 ppm of silicone emulsion per addition. Two polyether antifoams were toxic at 10 ppm | [29] FT; [30] ABS |
| Antifoam cuts oxygen transfer: up to 50% above 30 ppm with drilled-hole spargers (2nd, via [24] FT); 25% at 1,000 L (2nd, via [4] FT); none at 50 ppm in a bubble column with a protein-poor medium ([31] FT) | |
| US food limit on the silicone (dimethylpolysiloxane): 10 ppm in food | 21 CFR 173.340 [32] VEND |
| Mechanical foam breaking by an upper impeller worked in 12–30 m³ microbial fermenters at much higher stirring power; nothing found for animal cells | [33] ABS |
| Larger bubbles foam less: an open pipe gave "significantly less" foam than a sintered sparger | [26] ABS |

**Reading.** Dense cultures foam hard at gas velocities far below 6 mm/s, and the standard remedy has four side
effects that all bite harder as gas flow rises: slower growth, less oxygen transfer, filter fouling, and a food
residue limit. Microbial fermenters with protein-rich broths run at ten times this velocity with antifoam and
foam breakers, so foam at 6 mm/s is not physically unmanageable; whether it is manageable with animal cells at
120 g/L, food-acceptable additives and a cell-retention device is untested. A gravity settler (which the floor
assumes) would let antifoam leave with the spent medium, unlike a 0.2 µm filter; that is my inference, not a
finding.

**Number for this mechanism.** No sourced cap. As a judgement: low 2 mm/s (the top of what has been run with
cells), central 5, high 10 or more. This is the mechanism I think most likely to bind (about 60%).

---

## 3. Gas hold-up and flooding of the impeller

**Flooding.** An impeller is "flooded" when the gas rises straight through it instead of being thrown outward.
Nienow's rule for a Rushton turbine: flooding when gas flow / (speed × diameter³) exceeds 30 × (D/T)^3.5 ×
(speed² × D / g) (form confirmed at SNIP level only). CALC for the reference tank with two turbines of a third
of the tank width at 43 W/m³ (37 rpm): flooded above **1.4 mm/s**; at 100 W/m³ above 3.1; at 250 W/m³ above
7.9. A reading agent's independent calculation for three wide "elephant ear" impellers, as in a real 15 m³
pharma tank, puts 6 mm/s at 1.1 times the flooding flow at 40 W/m³ and 0.45 times at 100 W/m³. Varley and Birch
say large animal-cell tanks are "generally in the flooding regime" anyway, because they are stirred so gently
([25] FT). Up-pumping wide-blade impellers handle gas better (Nienow [4] FT, qualitative).

**Gas power.** Rising gas stirs the tank with a power of density × g × velocity = 59 W/m³ at 6 mm/s (CALC; 52
with gas expansion counted), against 43 W/m³ from the impeller. **At the floor's gas flow the tank is a bubble
column with a stirrer in it.** Humbird notes bubble columns have not been used for animal cells beyond the
bench ([1] FT); the reason he gives is bubble damage, which section 1 covers.

**Does that stop it working?** Probably not for oxygen or mixing:
- Oxygen: bubble-column measurements in a synthetic culture medium with 1 g/L poloxamer gave 7 per hour at
  4.2 mm/s and 16 per hour at 7.7 mm/s without any stirring (air, room temperature, [31] FT, read from figures).
  The model's formula gives 26 per hour at 6 mm/s. So the model's oxygen transfer at 6 mm/s may be up to twice
  too high. With 90% oxygen the floor still has room (it needs 62% of the model's cap), but not if antifoam
  halves the transfer as well.
- In the 15 m³ pharma tank (cell-free), oxygen transfer rose almost in proportion to gas velocity and only 50%
  across the whole stirring range; CO₂ removal did not respond to stirring at all ([34] FT). Tested only up to
  0.95 mm/s.
- One fitted model of a 20,000 L tank has oxygen transfer peaking near 0.03–0.055 vvm, which its authors
  suggest is flooding ([24] FT; weak, eight runs).
- No measurement of oxygen transfer, mixing or hold-up was found for any 1–25 m³ cell-culture tank above
  2 mm/s.

**Hold-up** (share of the tank that is gas): 3.5% at 4.2 mm/s and 4.5% at 7.7 mm/s for 3–4 mm bubbles, under 10%
more with poloxamer ([31] FT). About 4% at 6 mm/s, 0.6 m³ in the reference tank. Negligible. A sintered sparger
would give several times more (no number found).

**Number for this mechanism.** Not a cap on gas flow. It caps what the model's oxygen formula can be trusted
for: about 2 mm/s. Above that the formula is extrapolated.

---

## 4. Evaporation and exhaust

All CALC unless marked. Exhaust leaves saturated with water at 37 °C: 44 g per m³ of gas. At 6 mm/s the
reference tank loses 250 g of water per m³ of liquid per hour, 0.6% of its volume a day, about 100 kg a day. In
perfusion at about one volume a day this is under 1% of the liquid passing through. It also removes 170 W/m³ of
heat, 7% of the 2.4 kW/m³ the cells give off. Exhaust filter area is trivial: one 10-inch cartridge passes
200 L/min at 0.12 psi (SNIP), and the tank needs about 1,500 L/min. The real exhaust risk is foam or condensate
wetting the filter (section 2). With oxygen-rich gas the exhaust is itself oxygen-rich, a fire-safety design
item ([35] ABS). No source reports evaporation limiting a sparge rate.

**Number for this mechanism.** No cap below 20 mm/s. Confidence 90%.

---

## 5. Cost of the gas

**Gas per kg is fixed by CO₂, not by the gas velocity.** A kg of cells makes 6.2 mol of CO₂ (5.2 mol of oxygen
used × 1.2). At 100 mbar a m³ of exhaust carries 3.7 mol. So every kg needs 1.67 m³ of gas, about 87 mol,
whatever the velocity; more velocity lets the same tank make more kg. The cells use 6% of the oxygen in it.

**Oxygen.** Humbird's design sparges 90% oxygen made on site. His plant table lists an oxygen unit of 25,000 t
a year for a plant making 6,800 t of cells: 3.7 kg of oxygen fed per kg of cells, of which the cells use 0.2
([1] FT, Tables 4.1 and Sect. 4). At steady state in perfusion the floor case feeds 2.5 kg per kg (CALC). He
quotes on-site oxygen at $0.10–0.20 per kg; his own tables imply $0.25–0.33 (unit at $8.84M bare, about 13% of
direct plant cost once installed, plus $0.05/kg of cells in power; CALC).

| Per kg of cells, floor case | Value | Basis |
|---|---|---|
| Oxygen fed | 2.5 kg | CALC: 8.6 kg per m³ of liquid per hour ÷ 3.47 kg of cells per m³ per hour |
| Cost at $0.15/kg O₂, today's prices | **$0.52** | CALC; $0.35–1.15 over $0.10–0.33 |
| Compressing the gas | 0.09 kWh, under $0.01 | CALC, 1 to 2.5 bar, 70% efficiency |
| If the gas were blended to the 55% oxygen the cells need at 120 g/L | about $0.25 | CALC; not Humbird's design |

So the gas costs about 5% of the floor and does not cap the flow. It is already inside Humbird's plant cost
and utilities, but tied to the tank, not to the gas flow: a case with a third of the gas is still charged for
the full oxygen plant. **In the model:** `floor_physics.oxygen_fed` computes the oxygen fed, and `explore`
reports its cost per kg (`gas`) and what charging it in proportion to gas per litre would change (`gas_extra`):
nothing at the floor, −$1.05 at 2 mm/s, +$0.17 at 9 mm/s, +$0.14 for a squat tank, −$0.60 at 200 m³. It is
reported, not added to the total. I first added it, then took it out when merging with the gas-exchange and
plant-items work: the correction is under $1/kg in every case on the page, it rests on one quoted oxygen price,
and it would have moved some 35 pinned results of those studies for no change in any conclusion.

**Protectant, not in the model.** At 2–5 g/L and 11 litres of medium per kg, a kg of cells takes 22–55 g of
poloxamer. Only catalogue prices were found: $165/kg in 25 kg lots ([36] VEND listing), which would add
$3.6–9/kg of cells. Bulk technical grades are quoted at $2–80/kg (SNIP, unverified); at $10–20/kg it would add
$0.2–1.1. Humbird mentions it in one margin note and does not cost it.

**Number for this mechanism.** No cap.

---

## 6. Sparger type and CO₂ stripping

**Why gas volume cannot be traded for small bubbles.** A bubble takes up CO₂ until it is in balance with the
liquid, then carries no more. Measured on sintered spargers in 15–2,500 L tanks, CO₂ transfer was a tenth of
oxygen transfer, set by saturation of the gas: ceiling = 94 × vvm per hour ([37] FT). The same is reported at
5,000–25,000 L (saturation in 5–9 s, bubble residence 17–29 s; [38] ABS and 2nd) and at 15 m³, where CO₂
removal rose with gas velocity to the power 0.81 and with stirring to the power 0.03 ([34] FT). The model's
balance has the right form.

**How saturated does the gas leave?** CALC: a bubble of diameter d approaches balance with a time constant of
d × 1.58 / (6 × k_L): 2.6 s at 3 mm and 3.8 s at 5 mm. A bubble rising alone through 3.74 m takes about 15 s
(98–99.7% saturated); carried up in a fast plume, about 5 s (74–85%). Measurements:
- Drilled-hole spargers in 3–2,000 L tanks: CO₂ transfer = 40 × vvm per hour ([39] ABS, via [40] FT), which is
  42% of the ceiling in tanks 1–1.7 m deep. Scaled to 3.74 m by the same time constant: about 80% (CALC).
- The 15 m³ tank measured 1.3–2 times the ceiling ([34] FT, as computed by a reading agent; the excess is
  unexplained, possibly surface transfer or gas-volume units), so it confirms the form but cannot calibrate
  the level.
- The model's 0.96 is fitted to Humbird's figure, not measured. **A range of 0.7–0.96 is defensible**; at 0.85
  the floor would be $12.6 and at 0.7, $14.6. This is a separate input (`pf_co2_strip_eff`) and was not changed.

**Drilled holes against sintered spargers.**

| | Drilled holes, ring or pipe (bubbles 2–4 mm) | Sintered or micro-sparger (well under 1 mm) |
|---|---|---|
| Oxygen transfer per unit of gas | lower | 4–20 times higher ([39] ABS, 2nd) |
| CO₂ stripping per unit of gas | near the ceiling in a deep tank | at the ceiling, no more; 60% above drilled holes in shallow tanks ([39]) |
| Cell damage per unit of gas | lower | about ten times higher (section 1) |
| Foam | less ([26] ABS) | more; "uncontrollable" in one 300 L case (2nd, via [25]) |
| Fouling at high density | holes can plug ([22] ABS) | "not recommended for perfusion" ([23] VEND) |
| Antifoam penalty on oxygen transfer | 40–50% (SNIP) | none (SNIP) |

A micro-sparger saves gas only when oxygen sets the gas flow. Here CO₂ sets it, so the tank needs the full gas
volume anyway and the gentler drilled-hole sparger is the right one. In an existing 15 m³ tank an extra side
sparger with large bubbles gave 25% more CO₂ removal for 50% more gas ([34] FT).

**Number for this mechanism.** No cap on gas flow; it fixes the sparger as hundreds of 1–2 mm holes and puts
the stripping efficiency at 0.7–0.96.

---

## 7. What has actually been reported

Full ledger with arithmetic: 33 rows were collected; the ones that matter are below. Velocities marked * rest
on a tank geometry assumed from memory.

| Run or rating | Scale | Cells per mL | Gas, vvm | Velocity, mm/s | Observed | Source, access |
|---|---|---|---|---|---|---|
| Typical large-scale practice | 8–20 m³ | up to 10 million | 0.003–0.01 | 0.1–2 | | Nienow 2006 [4] FT |
| CHO fed-batch | 8 m³ | | 0.005 (CALC) | 0.2 (CALC) | weakly stirred, "flooding regime" | [25] FT |
| CHO fed-batch | 5 and 25 m³ | 7–12 million | up to about 0.01 | not found | exhaust saturated with CO₂ | [38] ABS; flow from a figure axis via [40] |
| CHO fed-batch, single-use tank | 5 m³ | 30–40 million | 0.012–0.017 (rated to 0.15) | not computable | CO₂ held under 80 mmHg | [23] VEND |
| CHO fed-batch | 1 m³ | | 0.002–0.01 | | foam; CO₂ 179 mmHg before fixes | [26] ABS |
| CHO perfusion, sintered sparger | 0.5 m³ | CO₂-limited to 2.4 million | 0.002 | | CO₂, not oxygen, limits | [41] ABS |
| Cell-free tests | 12.5 m³ | none | 0.005–0.014 | 0.32–0.95 | | [34] FT |
| Cell-free tests | 16.8 m³ | none | 0.015–0.054 | not given | | [24] FT |
| Equipment ratings | 2 m³ | | 0.1 (sparger), 0.2 (total) | 2.5, 5.1 | | Sartorius datasheet [42] VEND |
| Equipment rating | 2 m³ | | 0.1 | about 3* | | Thermo datasheet [23] VEND |
| CHO perfusion, drilled holes, 2 g/L poloxamer | 3 and 200 L | 60–80 million | 0.20 | up to about 2.8* | no damage | [20] ABS |
| CHO perfusion, single-use tank | 40 L | 160–264 million | 0.06–0.2 | up to about 1.5* | viability about 95%; antifoam by sensor | [23] VEND |
| CHO perfusion | 0.23 L | 80 million | 0.07 | under 0.2 | "excessive foaming" | [27] VEND |
| CHO perfusion, wave bag | 4 L | 214 million | not sparged | 0 | limits were viscosity, filter, CO₂ | Clincke 2013 [43] FT |
| Chicken fibroblasts, perfusion | lab; 300 L shown | 108–130 million | not found | | | [44] ABS |
| Humbird's model | 20 m³ | 40–80 million (120 g/L) | 0.1 | 6 | | [1] FT |

**Answers.**
- Gas velocities reported with cells in tanks of 1–25 m³: 0.1 to 2 mm/s, at up to 40 million cells per mL.
- Highest velocity found with cells at any scale: about 1.5–2.8 mm/s (both on assumed geometry).
- Any run combining 50 million cells per mL or more with 0.05 vvm or more above 200 L: **none found.**
- Any animal-cell culture at 6 mm/s: **none found.** Equipment is rated to 2.5–5 mm/s at 2 m³.
- Not found at all: gas flows for the 21 m³ insect-cell tanks, Vow's 15–20 m³ tanks, Lonza's airlifts, and
  commercial 12–25 m³ pharma tanks other than those above.
- Humbird's remark that record densities are unsparged cites the wave-bag run above and a microcarrier culture
  at about 0.3 million cells per mL (SNIP), so it is out of date: the 40 L runs above are sparged.

Confidence that no such large-scale run is in the open literature: about 85%; that none exists in the paywalled
full texts not read: about 60%.

---

## 8. The table: what each mechanism allows

Gas velocity in mm/s for the reference tank (20 m³, liquid 3.74 m deep, 120 g/L, protectant at 2–5 g/L, drilled
holes). Divide by 62 for vvm.

| Mechanism | Low | Central | High | Scales with | Basis |
|---|---|---|---|---|---|
| 1a. Bursting bubbles, with protectant | 2 | 14 | above 20 | vvm | Killing-volume model with X′ = 0.004 / 0.0005 / under 0.0003, death rate held to a quarter of growth. Direct support: 0.2 vvm harmless at up to 200 L. Sourced (bench scale) |
| 1a. The same without protectant | under 0.5 | | | vvm | X′ = 0.05. Sourced |
| 1b. Bubble formation at the sparger | no cap | | | hole velocity | Design item: 200–450 holes of 2 mm |
| 2. Foam and antifoam side effects | 2 | 5 | 10 or more | velocity | **No sourced number.** Low = most that has been run with cells; the rest is judgement |
| 3. Flooding and hold-up | no cap | | | | Impeller flooded above 1.4–3 mm/s; tank becomes a stirred bubble column. Limits trust in the oxygen formula, not the gas flow |
| 4. Evaporation and exhaust | above 20 | | | | 0.6% of volume a day at 6 mm/s. Arithmetic |
| 5. Gas cost | no cap | | | per kg, fixed | $0.52/kg at any velocity while CO₂ binds. Arithmetic on Humbird's prices |
| 6. Sparger type | no cap | | | | Sets efficiency of stripping at 0.7–0.96 |
| Oxygen supply and mixing at this gas flow | | bind near 10–12 | | | In the model (at 12 mm/s mixing binds at 189 g/L). Sooner if antifoam or the bubble-column regime cut oxygen transfer by half |
| **Overall** | **2** | **5** | **9** | | Binding mechanism: foam (my estimate 60%), bubble damage through too little or unsuitable protectant (25%), something not listed (15%) |

**Why 2 / 5 / 9.**
- 2 mm/s is the top of what large tanks are documented to use and about the highest velocity found with cells.
  I put about 12% on the true cap being below it.
- 9 mm/s is just below where mixing and oxygen supply start to bind in the model and is still below the damage estimate with good
  protection. I put about 25% on it being usable.
- 6 mm/s: about 45%. The damage evidence supports it (75–80%), the foam evidence is absent (my 60% that foam can
  be handled), and the two are not independent.
- For CHO in a pharma medium I would say 55%; for meat cells with food-acceptable additives, 40%.

**One structural consequence.** If bubble damage is the cap, the limit is in vvm and the density a tank can hold
does not depend on its size or shape. If foam is the cap, the limit is a velocity through the surface, as the
model assumes, and squat tanks gain. The model's tornado bars for tank shape and tank size assume the second. My
split is about 60:40 for a velocity cap.

---

## 9. What changed in the model, and what did not

- `pf_gas_velocity` stays at 0.006 m/s. The floor takes the favourable end of each input, 6 mm/s has roughly
  even odds, and no specific lower value is supported. Its range is now 0.002–0.009 (was 0.0006–0.006) and its
  note says what the evidence is.
- Tornado bar "Gas flow the cells tolerate": 2 to 9 mm/s (was 2 to 6), $28.0 to $8.7 around the floor's $11.5.
  It is still the widest bar.
- New: `oxygen_fed`, inputs `pf_o2_price`, `pf_o2_purity`, `pf_back_pressure`, and `gas` / `gas_extra` in
  `explore`'s result (section 5), reported and not added to the total. **The floor did not move**, and no
  other case did.
- Not changed, though this note bears on them: `pf_co2_strip_eff`, the oxygen-transfer formula, protectant and
  antifoam costs (see below).

## 10. The experiment that would settle it

A pilot tank deep enough to reach the velocity, which bench tanks cannot (Nienow's point, [4]). Minimum version:
a column or stirred tank with 2–4 m of liquid and 100–500 L (a tall narrow vessel reaches 6 mm/s at modest
volume), a ring sparger with 1–2 mm holes, a meat-relevant suspension line (or CHO first) in perfusion at
50 million cells per mL or more, poloxamer at 1, 2 and 5 g/L. Step the gas through 1, 2, 4, 6 and 9 mm/s for
two to three days each and record: death rate (released LDH against growth), foam height with and without
antifoam, antifoam needed per day, oxygen transfer, and CO₂ in liquid and exhaust (which gives the stripping
efficiency directly). The first half can be done without cells: foam height against velocity in spent medium
from a dense culture, with and without antifoam, would by itself move my 45% by 15–20 points either way.

## Follow-ups (not done here)

1. **Protectant cost and food status.** Poloxamer 188 at 2–5 g/L is uncosted in the model and in Humbird;
   only catalogue prices found. US food-additive rules do not clearly cover it (21 CFR 172.808 [32], read;
   GOOD Meat's own filing says it is "not specifically stated", and reports residue under 100 mg/kg in the
   product [45] VEND). EU status not verified (from memory: not authorised as an additive).
   *Update 2026-11-15 (late): now in the model.* The price is still catalogue only: Sigma-Aldrich 25 kg at $6,475 (about
   $259/kg) and 10 kg at $2,320 ($232/kg) [search summary of the catalogue pages]; a B2B trade tracker has a 2,000 kg+ band
   behind a paywall. No bulk price. Poloxamer is dissolved in the medium, so it leaves with every litre unless recovered. The model
   now charges `pf_protectant_dose` (2 g/L, range 1–5) × litres × `pf_protectant_price` ($30/kg assumed for tonnes, range $10–260,
   the top being the catalogue price) in every sparged vessel, with a tornado bar. At $30 that is $0.67 a kilo of cells in the
   reference case and the best case (11.2 L/kg) and $1.68 in Central and Cautious (28 L/kg); at the catalogue price $5.6 and
   $14. Medium prices are taken to exclude it. A web search found no EU food-additive authorisation for poloxamers and no EFSA
   opinion; cultivated meat is assessed as a novel food, so the residue would be dealt with in that dossier. Not verified in the
   Union list itself. A supplier quote would replace the assumed price.
2. **Antifoam.** Its effect on oxygen transfer (0 to −50%), on growth, and the 10 ppm food limit are not in the
   model. With transfer halved the floor's oxygen limit falls from 195 to 97 g/L and would bind.
   *Done 2026-11-15 (late):* `explore(antifoam_otr=)` and input `pf_antifoam_otr`, applied to the sparger's oxygen only, with a
   tornado bar. **The default is 0.75**, the middle of the reported 0–50% cut (a judgement; it was 1). At 0.75 the reference tank is
   unchanged (CO₂ still binds at 120 g/L), but oxygen now limits Central (177 g/L in place of 236; +$1.8) and Cautious (+$3.7).
   Halved: reference $13.55 (oxygen binds at 97 g/L), best case $10.16, Central $33.18, Cautious $51.18. With no effect: $12.51,
   $9.56, $28.15, $40.07. The effect on growth and the food limit are still not in the model.
3. **Stripping efficiency.** 0.7–0.96 against the model's 0.96; worth a tornado bar.
   *Done 2026-11-15 (late):* `explore(strip_eff=)` with a tornado bar (0.70 to 0.96). At 0.70 the reference tank holds 87 g/L in
   place of 120 and costs $14.27; the scenarios, whose columns take the CO₂, move by under $0.1.
4. **Velocity or vvm.** If the cap is in vvm, tank shape and size stop mattering for CO₂.
5. **Yeast-style plant.** That plant class has no oxygen unit in its price; the oxygen ($0.5/kg) is not added
   there.
6. **Read the paywalled primaries** if library access is available: Ozturk 1996, Xing 2009 and 2017, Xu et al.
   2017 (both), Ma 2004, Zhu 2008, Sieblist 2011.

## Searches stopped by the safeguard

One web search and three page fetches about the killing-volume model were refused (wording such as "killing
volume" and "death rate"). Neutral wording and the Europe PMC interface worked, and the thesis [11] was then
read in full, so nothing in section 1 is missing for that reason.

---

## Sources

1. Humbird D. Scale-up economics for cultured meat: techno-economic analysis and due diligence. 2021 report (local PDF `Cultivated_meat_TEAs/Humbird21Cultivated.pdf`). **FT** (Sects. 1.2, 2.3, 4.1, 5; Tables 4.1, 4.4), read by me.
2. Ozturk SS. Engineering challenges in high density cell culture systems. Cytotechnology 1996;22:3–16. https://doi.org/10.1007/BF00353919 . **ABS**. Full text not accessible.
3. Pörtner R. Bioreactors for mammalian cells. In: Animal Cell Culture, Springer 2015. https://doi.org/10.1007/978-3-319-10320-4_4 . **ABS**. Full text not accessible.
4. Nienow AW. Reactor engineering in large scale animal cell culture. Cytotechnology 2006;50:9–33. https://pmc.ncbi.nlm.nih.gov/articles/PMC3476006/ . **FT**.
5. Sieblist C et al. Cytotechnology 2011;63:49–55. https://pmc.ncbi.nlm.nih.gov/articles/PMC3021147/ . One passage, by automated extraction.
6. Sieblist C, Jenzsch M, Pohlscheidt M. Equipment characterization to mitigate risks during transfers of cell culture manufacturing processes. Cytotechnology 2016. https://pmc.ncbi.nlm.nih.gov/articles/PMC4960186/ . Passages mentioning Xing read.
7. Xing Z, Kenty BM, Li ZJ, Lee SS. Scale-up analysis for a CHO cell culture process in large-scale bioreactors. Biotechnol Bioeng 2009;103:733–746. https://doi.org/10.1002/bit.22287 . **ABS**.
8. Hu W, Berdugo C, Chalmers JJ. The potential of hydrodynamic damage to animal cells of industrial relevance. Cytotechnology 2011;63:445–460. https://pmc.ncbi.nlm.nih.gov/articles/PMC3176934/ . **FT**.
9. Walls PLL et al. Quantifying the potential for bursting bubbles to damage suspended cells. Sci Rep 2017;7:15102. https://pmc.ncbi.nlm.nih.gov/articles/PMC5678173 . **FT**.
10. Michaels JD, Mallik AK, Papoutsakis ET. Biotechnol Bioeng 1996;51:399. https://pubmed.ncbi.nlm.nih.gov/18629792/ . **ABS**.
11. van der Pol LA. Sparging-shear sensitivity of animal cells. PhD thesis, Wageningen. https://edepot.wur.nl/198209 . **FT** (reproduces van der Pol et al. 1990, 1992, 1993, 1995).
12. Tramper J, Vlak JM, de Gooijer CD. Cytotechnology 1996;20:221. https://doi.org/10.1007/bf00350402 . **ABS**.
13. Trinh K, Garcia-Briones M, Chalmers JJ, Hink F. Biotechnol Bioeng 1994;43:37. https://doi.org/10.1002/bit.260430106 . **ABS**.
14. Brorens, Ottens, Haringa. Biotechnol Bioeng 2026. https://doi.org/10.1002/bit.70308 . **FT** (equations read from page images).
15. Michaels JD et al. Biotechnol Bioeng 1995;47:407. https://doi.org/10.1002/bit.260470402 . **ABS**.
16. Jordan M et al. Biotechnol Bioeng 1994;43:446. https://doi.org/10.1002/bit.260430603 . **ABS**.
17. Ma N, Chalmers JJ, Auniņs JG, Zhou W, Xie L. Biotechnol Prog 2004;20:1183. https://doi.org/10.1021/bp0342405 . **ABS**.
18. Gigout A, Buschmann MD, Jolicoeur M. Biotechnol Bioeng 2008;100:975. https://doi.org/10.1002/bit.21840 . **ABS**.
19. Wei Z et al. Biotechnol Prog 2023;39:e3340. https://doi.org/10.1002/btpr.3340 . **ABS**. Also Tharmalingam and Goudar 2015, https://doi.org/10.1002/bit.25491 , **ABS**.
20. Xu S, Jiang R, Chen Y, Wang F, Chen H. Impact of Pluronic F68 on hollow fiber filter-based perfusion culture performance. Bioprocess Biosyst Eng 2017;40:1317. https://doi.org/10.1007/s00449-017-1790-2 . **ABS**.
21. Zhu Y, Cuenca JV, Zhou W, Varma A. NS0 cell damage by high gas velocity sparging. Biotechnol Bioeng 2008;101:751. https://doi.org/10.1002/bit.21950 . **ABS**.
22. Chaudhary G et al. Biotechnol Bioeng 2020;117:1684. https://doi.org/10.1002/bit.27314 . **ABS**.
23. Thermo Fisher application notes and datasheets, **VEND** (read): DynaDrive scale-up parts 1–2, https://assets.thermofisher.com/TFS-Assets/BPD/Application-Notes/dynadrive-cho-cells-application-note.pdf ; 50 L DynaDrive perfusion, https://documents.thermofisher.com/TFS-Assets/BPD/Application-Notes/dyna-drive-perfusion-cell-culture-application-note.pdf ; enhancements for high-density perfusion, https://assets.thermofisher.com/TFS-Assets/BPD/Application-Notes/sub-enhancements-perfusion-cultures-app-note.pdf ; drilled-hole sparger data sheet 091.
24. Muralidharan N, Bolduc E, Davis M. Characterizing oxygen mass transfer and shear during cell culture in a 20,000-liter stirred-tank bioreactor. BioProcess Int 2024;22(1–2). https://bioprocessintl.com/2024/january-february-2024/characterizing-oxygen-mass-transfer-and-shear-during-cell-culture-calculating-the-maximum-cell-density-supported-by-a-20000-liter-stirred-tank-bioreactor/ . **FT** (figures not read). Trade journal.
25. Varley J, Birch J. Reactor design for large scale suspension animal cell culture. Cytotechnology 1999;29:177–205. https://pmc.ncbi.nlm.nih.gov/articles/PMC3463394/ . **FT, keyword passages only**.
26. Mostafa SS, Gu X. Biotechnol Prog 2003;19:45. https://pubmed.ncbi.nlm.nih.gov/12573005/ . **ABS**, plus 2nd via [4] and [40].
27. Schwarz et al. Eppendorf Application Note 457. **VEND** (read).
28. Madabhushi SR et al. Systematic investigation of impact of antifoam and extracellular vesicles on fouling of hollow fiber filters in intensified perfusion. Biotechnol Bioeng 2025;122:1684. https://europepmc.org/article/PMC/PMC12152464 . **FT** (supplementary figures not seen).
29. Velugula-Yellela SR et al. Biotechnol Prog 2018;34:262. https://europepmc.org/article/PMC/PMC5821576 . **FT**.
30. Flynn J et al. Biotechnol Prog 2024;40:e3450. https://pubmed.ncbi.nlm.nih.gov/38476025/ . **ABS**.
31. Toye D et al. Influence of medium composition on oxygen transfer rate in animal cell culture. WCCE8, 2009. https://orbi.uliege.be/bitstream/2268/25283/1/TOYE%20%20-%20GLS9%20-%20WCCE8.pdf . **FT**, values read from figures. Conference paper.
32. 21 CFR 173.340 and 172.808. https://www.law.cornell.edu/cfr/text/21/173.340 . **VEND** (regulation text read).
33. Hoeks FWJMM et al. J Ind Microbiol Biotechnol 2003;30:118. https://doi.org/10.1007/s10295-003-0023-7 . **ABS**.
34. Nickel N et al. Front Chem Eng 2024;6:1470991. https://www.frontiersin.org/journals/chemical-engineering/articles/10.3389/fceng.2024.1470991/full . **FT**. Geometry from Hofmann et al. 2024 (https://tore.tuhh.de/bitstreams/9f6cd045-3dbc-45f9-a0cc-bad79b3587e6/download , FT) and US patent 12,371,651 (FT).
35. Xing Z et al. J Biotechnol 2024;387:79. https://doi.org/10.1016/j.jbiotec.2024.02.006 . **ABS**.
36. ChemicalBook price listing for CAS 9003-11-6. https://www.chemicalbook.com/Price/9003-11-6.htm . Listing read; other prices SNIP.
37. Bowers JS. Sparger and surface gas transfer for cell culture bioreactors. AIChE 2008. https://skoge.folk.ntnu.no/prost/proceedings/aiche-2008/data/papers/P118781.pdf . **FT**. Not peer reviewed.
38. Xing Z, Lewis AM, Borys MC, Li ZJ. A carbon dioxide stripping model for mammalian cell culture in manufacturing scale bioreactors. Biotechnol Bioeng 2017;114:1184. https://doi.org/10.1002/bit.26232 . **ABS**; numbers 2nd via [40].
39. Xu S, Hoshan L et al. A practical approach in bioreactor scale-up and process transfer using a combination of constant P/V and vvm. Biotechnol Prog 2017;33:1146. https://doi.org/10.1002/btpr.2489 . **ABS**; correlation 2nd via [40].
40. Chaudhry. Lessons in bioreactor scale-up, parts 8 and 9. BioProcess Int 2025;23(10) and 23(11–12). **FT**. Trade journal review.
41. Gray DR et al. Cytotechnology 1996;22:65. https://doi.org/10.1007/BF00353925 . **ABS**.
42. Sartorius Biostat STR Generation 3 datasheet. https://www.sartorius.hr/media/z03b0y0w/biostat-str-flexsafe-datasheet-en-b-2580438-sartorius.pdf . **VEND** (read).
43. Clincke M-F et al. Biotechnol Prog 2013;29:754. https://pmc.ncbi.nlm.nih.gov/articles/PMC3752962/ . **FT**.
44. Pasitka L et al. Nat Food 2023;4:35 and 2024;5:693. **ABS** and figure captions.
45. GOOD Meat dossier for FDA consultation CCC 000001. https://www.fda.gov/media/166346/download . **VEND** (read). UPSIDE Foods memo, https://www.fda.gov/media/163261/download (names classes only); Vow, FSANZ A1269 risk assessment (unnamed antifoam).

## Could not be found or read

- Full text of Ozturk 1996, Pörtner 2015, Nienow 2010 and 2015, Xing 2009 and 2017, Xu 2017 (both), Ma 2004,
  Zhu 2008, Chisti 2000, Mostafa and Gu 2003, Gray 1996, Sieblist 2011 I and II.
- A death rate against gas flow with poloxamer present; a poloxamer dose-response; the concentration used at
  200 million cells per mL.
- Foam height or foam rate against gas velocity in any cell-culture broth; a foam-limited gas velocity.
- Oxygen transfer, mixing or hold-up in any 1–25 m³ cell-culture tank above 2 mm/s.
- A flooding rule for the up-pumping impellers cell-culture tanks use.
- Any sparging data for muscle, fibroblast, bird or fish cells.
- A bulk price for poloxamer 188.
