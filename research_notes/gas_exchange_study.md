# Gas exchange for a 20 m³ tank of animal cells: membrane loop, tank shape, and a published airlift

Compiled 2026-11-14. Calculations: `gas_exchange.py` (run it to reproduce every table). Tests:
`tests/test_gas_exchange.py`. Nothing here is used in the headline cost or on the page.

**How to read this file**

- Every sourced number carries its access level: **full text** (the paper body was read), **abstract**,
  **snippet** (a search-engine summary, not checked against the source), **vendor** (a data sheet or
  product page), **memory** (recalled, not looked up).
- **[INF]** marks my own inference or arithmetic. Most of section 1 is first-principles engineering
  (textbook transport equations applied to the model's cell), cross-checked against published devices.
- Three web lookups were stopped by the model's safeguard (bubble damage to cells, twice, and one
  repository PDF). Pablo then downloaded the papers and section 2.3 was rewritten from their full text.
- Unit conversions: 1 mL of CO₂ per minute per m² (the medical unit, at standard conditions) = 2.68 mmol per
  m² per hour. 1 mmHg = 1.333 mbar.

---

## For the experiments list

*Revised after section 7.* Three unknowns stay open, and all three are about the cells; the engineering is settled
by calculation. Floor numbers are $/kg of cells from `floor_physics.explore` (today's floor: `explore()` =
$11.5) or `gas_exchange.floor_with_column`. **Dependence on the gas-flow session (what-caps-gas-flow):** with the
packed column and headspace pressure of unknowns 2 and 3, the floor is $7.2–7.4 whatever gas the cells tolerate
(6 or 2 mm/s); without them it is $11.5 at 6 mm/s and $28 at 2 mm/s. The membrane loop of the earlier version is
superseded: a steel column does the same job without the module problems (section 7).

**1. More gas per litre of culture**
- *Unknown:* Can a 20 m³ tank of dense cells (120–190 g/L) be sparged at 0.15–0.2 litres of gas per litre of
  culture per minute, twice today's assumption, without bubbles killing cells or foam stopping the run?
- *Worth:* well, **$8.5** (`explore(gas_velocity=0.0125)`, 0.2 vvm in the floor's tank) or **$8.8** for a
  squat tank at today's gas speed (`gas_exchange.shape_case(0.8)`); badly, **$11.5** (`explore()`). Neither
  number includes the protectant (see the note below the list).
- *Probability it resolves well:* **50%**. Vendors rate 2,000-litre tanks to 0.2 vvm, and dense pharma
  cultures have run at 0.1–0.2 vvm with 2–5 g/L of protectant at 50–200 litres; foam at 20 m³ and at these
  densities has not been measured.
- *Deciding experiment:* a perfusion run of a meat cell line in suspension at 100+ g/L in a 200–2,000 L
  sparged tank, stepping gas from 0.1 to 0.2 vvm at 2 and 5 g/L protectant; measure cell death rate, foam,
  antifoam used and dissolved CO₂.
- *Cost and time:* roughly $100–300k and 2–3 months [my estimate]; a contract manufacturer with pilot
  perfusion tanks, or a cultivated-meat company with a pilot plant.
- *Evidence today:* measured in pharma cells only (CHO, hybridoma, insect cells).

**2. Cells on a packed stripping column** (revised in section 8)
- *Unknown:* With the culture pumped 11 times an hour over stainless packing as a 0.3 mm film, laid on without
  drips, and stripped only to 55 mbar (pH up 0.26 while in the loop), do meat cells keep growing for a month
  without coating the packing?
- *Worth:* well, **$8.6** (`floor_with_column(p_out=55.0)`, sparger at 6 mm/s) and **$8.9** if the sparger is cut
  to 2 mm/s (`floor_with_column(p_out=55.0, sparge_velocity=0.002, oxygen=True, sweep="o2_closed")`); badly,
  **$11.5** (`explore()`), or **$28** at 2 mm/s (`explore(gas_velocity=0.002)`).
- *Probability it resolves well:* **60%**. Calculation and literature settle the shear (below what CHO took for
  weeks), the drips (avoidable by design) and the pH pulse (the gentler design is 3–6 times below the exposure
  that hurt CHO); bubble-free surface aeration is how rocking bags reach the highest CHO densities. Deposits on
  steel and the behaviour of meat cells are untested.
- *Deciding experiment:* a 5–20 litre perfusion run of a meat cell line in suspension at 100+ g/L with a small
  packed column on the loop (liquid laid onto the packing, stripped to 55 mbar, loop volume under 3% of the
  tank), against a sparged control: growth, viability, pH at the column outlet, deposits after 30 days. A
  cell-free test first confirms the stripping rate (predicted: 100 → 55 mbar in 0.18 m).
- *Cost and time:* about $5k and a week for the cell-free test; $50–150k and 2–3 months for the run [my
  estimates]; a university bioprocess or chemical-engineering lab with a cell-culture partner.
- *Evidence today:* measured in pharma cells only (shear, pH pulses, bubble-free aeration); the film itself is
  inferred.

**3. Cells at 2 bar absolute** (revised in section 8)
- *Unknown:* With dissolved oxygen and CO₂ held at their usual levels, do the cells grow as well with the
  headspace at 1 bar gauge as at Humbird's 0.33?
- *Worth:* together with unknown 2, well, **$7.3** (`floor_with_column(p_out=55.0, oxygen=True, sweep="o2_closed",
  p_top_barg=1.0)`; $7.4 at 2 mm/s; $5.0 in a yeast-style plant); badly, **$8.6** (the column alone, 189 g/L,
  mixing-limited). Alone it does nothing ($11.5), because CO₂ still binds.
- *Probability it resolves well:* **85%**. Cells at the bottom of today's tank already sit at 1.7 bar absolute;
  the design adds at most 0.67 bar, about 6 times below the lowest pressure with any reported effect on
  cultured cells. One small CHO study saw odd effects at tiny extra pressures.
- *Deciding experiment:* two 2–5 litre pressure-rated vessels side by side, one at 0.33 and one at 1.0 bar
  gauge, with the same dissolved oxygen and CO₂, a meat cell line in suspension for two weeks; growth rate,
  viability, oxygen uptake.
- *Cost and time:* about $20–50k and 1–2 months [my estimate]; any lab with steam-rated benchtop vessels.
- *Evidence today:* inferred from physics and from pressure studies on other cells; no run at these pressures.

**A cost the floor leaves out, for the medium row.** The floor counts no bubble protectant (Pluronic F68).
At its 11 litres of medium per kg, 1 g/L is 11 g per kg of cells and the 5 g/L used in dense pharma
perfusion is 56 g. At the pharma-grade list price (about $260/kg, vendor) that is **$2.9–14.5/kg**; at an
unverified bulk price of $8–15/kg, $0.1–0.8. Cells also take it up (about 12 µg per million cells, Gigout
2008, abstract, which is about 4 g per kg of 3 ng cells). Which price and dose apply is a quote and a
dose-finding run, and it affects unknown 1, since more gas needs more protectant.

---

## Answer in brief

0. **Latest (section 7): drop the membrane, keep the loop.** A short packed column of stainless steel on the
   pumped loop strips the CO₂ with no bubbles and no membrane: 1.8 m across, half a metre of packing, $26k per
   m³ of tank, floor **$8.6/kg**. With 1 bar of headspace pressure added and an oxygen sweep, every gas-side
   limit clears up to the culture's thickness (258 g/L): **$7.3/kg** in the floor's plant, $5.0 in a
   yeast-style plant, whatever gas flow the cells tolerate. Section 8: calculation and literature settle most
   of the cell side too (shear, drips, the pH pulse once the column strips gently, pressure); what is left is
   deposits on the packing and how meat cells, not CHO, respond. Items 1–2 below are the earlier membrane design.
1. **A membrane loop is limited by the liquid, not by the membrane.** A litre of culture at 100 mbar of CO₂
   holds 2.5 mmol of dissolved CO₂ and gives up about 1.1 mmol in a pass. Its 31 mmol/L of bicarbonate is
   not available, because turning bicarbonate into CO₂ needs an acid and culture medium has almost none to
   spare. So the tank must go round the loop many times an hour: about 11 to take out the CO₂ a sparger
   cannot at 190 g/L, and about 30–50 if nothing is sparged at all.
2. **The sensible design is a loop for CO₂ only, with the sparger kept.** For a 20 m³ tank at 190 g/L: about
   180 m³/h of culture through about 2,500 m² of fibre, 9 kPa of pressure drop, 45 W per m³. At an assumed
   $200 per m² it adds about $78k per m³ of tank and takes the floor from $11.5 to about **$9.2/kg**
   (range $8.6 to $13.8 across the membrane prices found). Removing CO₂ for free would give $8.5.
   *Stress test (section 6):* no module both survives repeated steaming and has a price; the one priced
   silicone module can be steamed once, which would put the floor at $35. Workable: 35%; pays $1/kg or
   more: 15%.
3. **A squat tank does about the same with no new equipment, by passing more gas per litre.** Liquid
   0.75–0.8 times as deep as the tank is wide gives **$8.7–8.8/kg** with the extra steel and floor counted.
   Measured bubble damage goes with gas per litre, not with velocity (three papers, read in full), so the
   squat tank pays in dead cells: about 13% of growth against 8%, roughly $0.3/kg, if the protectant works
   at scale as in small columns. Section 2.3, revised after reading the primary papers.
4. **The cheapest published design fails the model's gas limit but not by much.** Negulescu's 262 m³ airlift
   needs 10–14 mm/s of gas to hold its 100 g/L at 100 mbar, against the model's 6. At 6 mm/s it holds
   43–62 g/L.

---

## 1. Membrane loop

### 1.1 Loads

From the model's cell (`Cells.qo2` = 0.149 mmol O₂ per g per hour, `pf_rq` = 1.204):

| density, g/L | cell volume | CO₂ made, mmol/L/h | O₂ used, mmol/L/h | CO₂ per 20 m³ tank (16 m³ of culture), mol/h |
|---|---|---|---|---|
| 120 | 12% | 21.5 | 17.9 | 345 |
| 150 | 14% | 26.9 | 22.4 | 431 |
| 190 | 18% | 34.1 | 28.3 | 546 |
| 250 | 24% | 44.9 | 37.3 | 718 |

The sparger at the model's limits (6 mm/s, 100 mbar) removes 21.5 mmol/L/h, which is where the floor's
120 g/L comes from. A loop that works beside the sparger has to remove only the rest: 12.6 mmol/L/h at
190 g/L.

### 1.2 What a litre of culture carries per pass [INF]

This is the step that decides the design, and it is where a tank differs from blood.

- Dissolved CO₂: 0.0246 mmol/L per mbar (`pf_co2_henry`), so 2.46 mmol/L at 100 mbar.
- Bicarbonate at pH 7.2: 31 mmol/L, twelve times more. But HCO₃⁻ + H⁺ → CO₂ + H₂O uses up an acid. If only
  CO₂ is removed, the alkalinity stays, the pH rises, and the bicarbonate stays where it is. Stripping from
  100 to 55 mbar raises the pH by 0.26 and releases 1.11 mmol/L, all of it the dissolved gas.
- Blood is different: haemoglobin buffers about 30 mmol/L per pH unit, so bicarbonate does convert, and
  medical devices take 3–5 mmol out of each litre. Fresh medium buffers about 0.5 (1 mmol/L of phosphate).

      CO₂ per pass = 0.0246 × (p_in − p_out) + buffer × ΔpH,      ΔpH ≈ log₁₀(p_in / p_out)

Published data agree with this reading. Unmodified fibres in phosphate-buffered saline at 67 mbar removed
92 mL/min per m² from 45 mL/min of liquid through 0.0119 m² (Kimmel 2013 [3], full text): that is 0.049
mmol/min out of 0.074 dissolved, two thirds of the dissolved gas. With carbonic anhydrase on the fibres the
same module removed 0.104 mmol/min, 141% of the dissolved gas, which is only possible because the saline's
10 mmol/L of phosphate supplied the acid. Removal in these devices rises with liquid flow and inlet CO₂
(Hospach 2020 [6], full text), as a content-limited device should.

Consequence: liquid at 100 mbar carries less CO₂ (2.5 mmol/L) than gas at 100 mbar does (3.9 mmol/L), and a
loop gets only part of it. **A CO₂ loop must pump more litres of culture than a sparger passes litres of
gas.**

Oxygen is tighter still. Liquid against pure oxygen at 1 bar holds about 1.0 mmol/L (`ge_o2_henry`) and
there is no carrier, so a pass adds at most about 0.9 mmol/L. Blood carries about 9.

What could raise the amount per pass:

| route | effect | status |
|---|---|---|
| Strip deeper (80% per pass, to 28 mbar) | 1.8 mmol/L per pass; pH +0.55 in the loop; fibres 2.5 times as long | pH swing untested for seconds-long exposure; nothing found [14] |
| Non-bicarbonate buffer of 5 mmol/L per pH | 2.3 mmol/L per pass; passes and area halve | The cells' own contents might supply 3–6 at 12–18% of the volume, if CO₂ crossing their membranes brings it into play within seconds [INF, unmeasured]. Adding a buffer such as HEPES adds salt, which the model charges for |
| Carbonic anhydrase on the fibres | +75% to +115% in buffered saline [2,3,4]; +31–37% in blood [1,5] | Needs the buffer above. In unbuffered medium it would do little [INF]. More enzyme gave no more gain: the liquid film is the resistance [4] |
| Acid added before the loop, base after | ×1.7 to ×3.4 in blood and in carbonated water [7] | Adds salt in proportion; the model's salt limit (415 mOsm/kg) is already close |
| Alkaline sweep liquid in the fibres | Sweep side held at zero CO₂: about +11% over a 10 mbar sweep gas [INF] | Not found in any source. Uses 1–2 mol of NaOH per mol of CO₂ and risks caustic reaching the culture. Not worth it: the sweep side is not the resistance |
| Oxygen at 2 bar in the fibres | Doubles oxygen per pass | Needs a dense wall. Liquid returns at ten times air saturation; tolerance not found [14] |

### 1.3 One fibre [INF, textbook transport]

Cells flow inside the fibres, as in the filters used for perfusion, because that geometry has a known shear,
no dead corners, and a record with dense cultures (section 1.6). Flow is laminar. The wall coefficient is
Lévêque's, k = 1.62 (D/d) Gz^(1/3) with Gz = v d² / (D L); a dense silicone wall adds its own resistance in
series; the fraction exchanged in a pass is 1 − exp(−4 K L / (v d)).

Design point (`ge_*` inputs): 0.5 mm bore, wall shear rate 1,000 per second (velocity 6 cm/s), a 100 µm
silicone wall, 50% of the way to a sweep gas at 10 mbar per pass. Result: fibres 39 cm long, 6 seconds
inside, CO₂ flux **80 mmol per m² per hour**, oxygen 63% of the way to saturation.

Two properties of this geometry matter:
- At a fixed fraction per pass, the flux does not depend on the velocity, only on the bore: flux ∝ D/d.
  Halving the bore halves the area.
- The pressure drop does not depend on the bore, only on velocity squared. Low shear is cheap.

Cross-check against published devices (liquid outside thin fibres, which gives a thinner film):

| device and liquid | CO₂ flux, mmol/m²/h | at | source, access |
|---|---|---|---|
| this design, cells inside 0.5 mm silicone fibres | 80 | 100 mbar | [INF] |
| the same with a porous wall (no membrane resistance) | 142 | 100 mbar | [INF] |
| unmodified fibres, buffered saline | 201–245 | 67 mbar | Arazawa 2015 [4], Kimmel 2013 [3], full text |
| the same with carbonic anhydrase | 413–527 | 67 mbar | [3,4], full text |
| unmodified fibres, blood | 212–595 | 67 mbar | Arazawa 2012 [1], 2015 [4], full text |
| clinical CO₂-removal devices, blood | 140–450 | 60–107 mbar | Hospach 2020 [6], full text; Burki 2013 [8], abstract |

The design here is two to four times below what medical modules reach in saline. Part is the silicone wall,
part the wider bore, part the buffer in the saline. It is the cautious end. A liquid-outside module would
need less area but has not been run with dense cell suspensions (section 1.6).

### 1.4 Required flow, flux and area as functions of density

For a 20 m³ tank. "Passes/h" is tank volumes through the loop per hour. Area is per m³ of culture. Cost is
at $200 per m² purchased, ×3 installed, membranes replaced every 2 years (section 1.7).

**A. CO₂ only; the sparger stays at 6 mm/s and supplies the oxygen.**

| g/L | CO₂ for the loop, mmol/L/h | passes/h | flow, m³/h | m² per m³ | total m² | kPa | W/m³ | $k per m³ of tank | membranes and power, $/kg |
|---|---|---|---|---|---|---|---|---|---|
| 120 | 0 | 0 | 0 | 0 | 0 | – | 0 | 0 | 0 |
| 150 | 5.4 | 4.9 | 78 | 67 | 1,070 | 7.4 | 17 | 34 | 0.19 |
| 190 | 12.6 | 11.3 | 182 | 156 | 2,500 | 8.6 | 45 | 78 | 0.36 |
| 250 | 23.3 | 21.1 | 337 | 290 | 4,640 | 10.9 | 106 | 144 | 0.50 |

**B. CO₂ only; sparger at pharma practice, 1 mm/s.** (Oxygen would have to come from fine bubbles of pure
oxygen, which the model does not describe.)

| g/L | CO₂ for the loop | passes/h | flow, m³/h | m² per m³ | total m² | kPa | W/m³ | $k per m³ | $/kg |
|---|---|---|---|---|---|---|---|---|---|
| 120 | 17.9 | 16.2 | 259 | 223 | 3,570 | 6.7 | 50 | 111 | 0.81 |
| 190 | 30.5 | 27.6 | 441 | 379 | 6,060 | 8.6 | 110 | 188 | 0.87 |
| 250 | 41.3 | 37.3 | 597 | 513 | 8,200 | 10.9 | 187 | 253 | 0.89 |

**C. CO₂ and all the oxygen through the loop; nothing sparged.** Oxygen sets the flow.

| g/L | passes/h | flow, m³/h | m² per m³ | total m² | kPa | W/m³ | $k per m³ | $/kg |
|---|---|---|---|---|---|---|---|---|
| 120 | 30 | 481 | 413 | 6,610 | 6.7 | 93 | 204 | 1.50 |
| 190 | 48 | 761 | 654 | 10,470 | 8.6 | 190 | 322 | 1.50 |
| 250 | 63 | 1,002 | 861 | 13,770 | 10.9 | 315 | 422 | 1.50 |

With oxygen at 2 bar in the fibres (case D) CO₂ sets the flow again: 31 passes/h and 424 m² per m³ at
190 g/L.

Rules of thumb that follow, for the default design:
- passes per hour ≈ (CO₂ for the loop, mmol/L/h) ÷ 1.1; for oxygen, load ÷ 0.6;
- area per m³ of culture ≈ 13.8 m² per pass per hour, so **required area ≈ 12.4 m² per mmol/L/h of CO₂**;
- required flux is whatever the module delivers; at twice the flux, half the area, but the passes do not
  change. Area is the cheap variable. Flow is the hard one.

What moves case A at 190 g/L:

| change | passes/h | m² per m³ | pH rise | kPa | fibre length |
|---|---|---|---|---|---|
| as above | 11.3 | 156 | +0.26 | 8.6 | 39 cm |
| 80% stripped per pass | 7.1 | 245 | +0.55 | 21.6 | 97 cm |
| buffer of 5 mmol/L per pH | 5.4 | 75 | +0.24 | 8.6 | 39 cm |
| 1 mm bore | 11.3 | 247 | +0.26 | 27.2 | 245 cm |
| porous wall | 11.3 | 88 | +0.26 | 4.9 | 22 cm |
| shear 3,400 per second | 11.3 | 156 | +0.26 | 99.5 | 132 cm |

The sweep gas is air, about 260 m³/h for case A at 190 g/L, from a low-pressure blower. It never touches
the cells. Because it carries 0.2 bar of oxygen, the culture does not run out of oxygen during its 6
seconds in the fibres.

**A membrane hung in the tank** (tubing or fibre curtains, no pumping) avoids the flow problem but not the
area: at 190 g/L it needs about 310 m² per m³ for CO₂ and 455 for oxygen, which as 3 mm silicone tubing is
48 km per m³ and a third of the tank's volume. Bubble-free aeration with such tubing reached 30–68 m² per
m³ and 200 litres, at 15–20 million cells per mL, and was limited above about 8 million (Frahm 2009 [11],
full text). It is ruled out at these densities.

### 1.5 Pressure, shear and pumping

| quantity at 190 g/L (case A) | value | compare |
|---|---|---|
| viscosity (Thomas's equation, 18% cells) | 1.4 mPa·s | Clincke 2013 used the same equation and advised staying under 146 million cells/mL [9] |
| wall shear rate in the fibres | 1,000 per second (1.4 Pa) | 1,000–3,400 per second: "no impact ... on CHO cell growth, viability, and metabolism" [9], full text |
| pressure drop, loop | 9 kPa | a filter loop runs at several times this |
| pump power | 45 W per m³ of culture | the stirrer's limit in the model is 43 W per m³ |
| passes per cell per day | 270 | 360 in Clincke's 4-litre runs (15 volumes an hour) [9] |
| flow | 182 m³/h | an ordinary size for a sanitary centrifugal pump; no cell data at this size |
| fibres | about 4 million, 39 cm long | holds 2% of the culture at any time |

The fibres are not the worry: the shear and the number of passes are inside what CHO cells have tolerated
for 48 days. The pump is less certain. Clincke used a peristaltic pump at 1 L/min. Magnetically levitated
centrifugal pumps are reported to damage CHO cells less than peristaltic or diaphragm pumps (Blaschczok
2013 [10], snippet, no numbers), but nothing was found on pumping 100+ g/L of cells at hundreds of m³/h.

### 1.6 Has it been done?

- **Dense cells through hollow fibres, yes, at 4 litres.** CHO at up to 214 million cells/mL through 1 mm
  fibres at 15 volumes an hour for 48 days; 0.5 mm
  fibres at 100–127 million for about 12 days (Clincke 2013 [9], full text). Those were filters. The same
  runs saw CO₂ reach 170–310 mbar, which is this note's problem observed.
- **Membrane gas exchange for dense cells, once, at 2 litres, for oxygen.** A patent describes silicone
  hollow-fibre modules in place of the sparger: about 100 million cells/mL on membrane oxygen against
  about 130 million with sparging, a 0.25 m² module, and a second module for CO₂ described but without
  numbers in the part read (US 12,415,980 [12], full text of the first third; applicant's data).
- **Nothing at pilot scale or above**, and nothing for muscle, fibroblast or fish cells.

### 1.7 Fouling, sterilisation and cost

- **Sterilisation.** The standard industrial gas-exchange modules (3M Liqui-Cel, microporous
  polypropylene) cannot be steamed: hot water at 85 °C at most, no surfactants (cleaning guide [13], full
  text). Culture media contain a surfactant (Pluronic) to protect cells from bubbles, so porous fibres
  risk wetting. Dense silicone fibres are the candidate; silicone is routinely autoclaved [memory], but no
  data were found on repeated steaming of any gas-exchange module.
- **Fouling.** A gas-exchange wall has no flow through it, so it should foul less than a filter. Evidence:
  none found for gas-exchange fibres in culture broth. Tubing aerators were ended early by debris on the
  tubing (Frahm 2009 [11], full text). The model assumes membranes are replaced every 2 years (range 6
  months to 5 years, judgement).
- **Cost.** This is the weakest input. No vendor price was found for any gas-exchange module.

| what | $ per m² | source, access |
|---|---|---|
| hollow-fibre modules for gas separation | 40–200, 5-year life | Eng. Proc. 2023 [15], snippet |
| pharma hollow-fibre filter (ATF-10, 11 m²) | 1,480 | Humbird 2021 [16], full text ($16,300 each); area from the vendor's size guide, snippet |
| used in the model | 200 (40 to 1,480) | top of the first range |

Installed at 3 times the purchase price (CE Delft's overall factor for food-grade plant [17]), plus a pump
[assumed, no price found]. A steam-proof silicone module at thousands of m² is not a catalogue product,
so the true price could be outside this range on the high side.

### 1.8 What it does to the floor

`floor_with_loop`: the CO₂ limit is lifted, the next limit binds, the loop's capital is added to the plant
and membranes and power per kg.

| case | today | CO₂ removal free | with the loop paid for | density, what binds | loop |
|---|---|---|---|---|---|
| floor, loop for the CO₂ above 120 g/L | 11.5 | 8.5 | **9.2** | 189 g/L, mixing | 11 passes/h, 2,450 m², $77k/m³ |
| … membranes at $40 per m² | 11.5 | 8.5 | 8.6 | | $18k/m³ |
| … membranes at $1,480 per m² | 11.5 | 8.5 | 13.8 | | $548k/m³ |
| … membranes last 6 months | 11.5 | 8.5 | 10.3 | | |
| floor, nothing sparged | 11.5 | 8.5 | 11.6 | 189 g/L, mixing | 47 passes/h, 10,400 m², $320k/m³ |
| … with oxygen at 2 bar | 11.5 | 8.5 | 10.5 | | 31 passes/h, 6,700 m² |
| cells that tolerate only 2 mm/s of gas, CO₂ loop | 28.0 | 15.5 | 16.5 | 81 g/L, oxygen supply | 7 passes/h |
| cells that tolerate only 2 mm/s, nothing sparged | 28.0 | 8.5 | 11.6 | 189 g/L, mixing | 47 passes/h |
| fish cells (50 mbar), CO₂ loop | 20.6 | 8.8 | 12.0 | 180 g/L, mixing | 47 passes/h, 10,300 m² |
| yeast-style plant, CO₂ loop | 6.6 | 5.4 | 6.1 | 189 g/L, mixing | as the first row |

Reading the table:
- At the floor the loop is worth about $2.3/kg at the assumed price, and nothing at pharma-filter prices.
  The break-even membrane price is about $800 per m².
- **Its larger value is as insurance against the gas-flow assumption**, the largest risk on the floor. If
  cells tolerate 2 mm/s and not 6, the floor is $28. A tank with no sparging at all costs about $11.6
  whatever gas the cells tolerate. That design needs 47 passes an hour, three times what has been shown
  at 4 litres.
- **It is weakest where it is needed most.** At 50 mbar a litre carries half as much CO₂ and the driving
  force halves, so fish cells need four times the area and flow. The loop still takes them from $20.6 to
  $12.0.
- With the loop, mixing binds at 189 g/L, just under oxygen at 195. The loop does not make large tanks
  attractive, as already found.

Not modelled: the loop returning liquid at one point of the tank (CO₂ would vary by tens of mbar across a
tank that mixes in 2.4 minutes and passes the loop every 5); cells lost to the pump; contamination risk from
several million fibres; and the retention device, which could share the loop's pump but not its membranes.

### 1.9 What would have to be true of the cells

1. They grow as single cells or small clumps. Clumps above about 100 µm or cells on carriers will not
   pass 0.5 mm fibres. This excludes most anchorage-dependent processes.
2. They tolerate 270 passes a day at 1,000 per second of shear, and a large low-shear pump, for weeks.
   Shown for CHO at 4 litres with a small pump.
3. They tolerate a pH swing of about +0.3 for six seconds, 270 times a day. Not found in any source.
4. They do not coat silicone. Not known.
5. For the no-sparging design only: they tolerate liquid returning at five to ten times air saturation of
   oxygen. Not found.

---

## 2. Tank shape

### 2.1 What the model does, and what was added

`co2_limited_density` gives the density as (gas velocity ÷ liquid depth) × CO₂ per litre of gas ÷ CO₂ made
per gram. A squat tank is shallower, so it holds more. `mixing_time_ratio` makes it mix faster too. The
model charged nothing for shape. `shape_capex_factor` adds two costs [INF, with sourced parts]:

- **Steel.** Wall thickness is taken proportional to diameter (the ASME formula t = P D / (2SE − 1.2P) and
  the minimum-thickness rules both grow with diameter; Seider et al. via BioSTEAM's code [18], full text of
  the code). Steel is then diameter × surface, and cost follows steel to the power 0.6 (the slope of
  Seider's vertical-vessel correlation at the 8,000 lb of a 20 m³ tank [18]). This is applied to the whole
  bioreactor share of the plant (32%), which overstates it: the bare vessel is about a fifth of the
  installed bioreactor (Humbird 2021 [16]: $330k bare, $1.5M installed).
- **Floor.** Each tank takes (width + 2 m)² [assumed], applied to the hall's 13% of the plant (Humbird's
  sanitary hall, $20.9M of $159.5M [16]).

No source was found that states how fermenter cost varies with height-to-width ratio.

### 2.2 Results (`shape_case`)

20 m³ tank, floor case. "Velocity rule": cells tolerate 6 mm/s through the liquid surface whatever the
shape (the model's reading). "Per-litre rule": they tolerate the gas flow per litre that 6 mm/s is in the
reference tank (0.096 vvm).

| liquid depth ÷ width | width, m | depth, m | density, g/L (what binds) | $/kg, shape free | $/kg, with steel and floor | plant × | per-litre rule: g/L, $/kg |
|---|---|---|---|---|---|---|---|
| 0.25 | 4.34 | 1.08 | 195 (oxygen) | 8.3 | 9.8 | 1.37 | 72, 20.8 |
| 0.50 | 3.44 | 1.72 | 195 (oxygen) | 8.3 | 9.0 | 1.17 | 105, 14.0 |
| **0.80** | 2.94 | 2.35 | 190 (CO₂) | 8.4 | **8.8** | 1.09 | 120, 12.0 |
| 1.00 | 2.73 | 2.73 | 164 (CO₂) | 9.3 | 9.5 | 1.05 | 120, 11.8 |
| 1.30 | 2.50 | 3.25 | 138 (CO₂) | 10.4 | 10.5 | 1.02 | 120, 11.6 |
| 1.60 (the model's) | 2.34 | 3.74 | 120 (CO₂) | 11.5 | 11.5 | 1.00 | 120, 11.5 |
| 2.00 | 2.17 | 4.34 | 103 (CO₂) | 12.8 | 12.7 | 0.98 | 114, 11.8 |
| 3.00 | 1.89 | 5.68 | 45 (mixing) | 25.2 | 24.4 | 0.95 | 45, 24.4 |

- **Velocity rule: the cheapest shape is liquid 0.75 times as deep as wide, $8.7/kg, $2.8 below the
  floor.** Below that the oxygen limit binds, so a shallower tank only adds steel and floor. Counting
  steel and floor costs $0.4/kg at the optimum and moves it from "as squat as possible" to about 0.75.
- **Per-litre rule, taken as a hard limit: shape does nothing for CO₂** (section 2.3 finds it is a cost,
  not a hard limit). The gas a tank may pass falls with its depth exactly as
  fast as the gas it needs. The cheapest shape is then slightly taller than the model's (1.95, $11.4),
  because a deeper tank is allowed more gas velocity, which helps oxygen.
- **200 m³:** under the velocity rule only a very shallow tank works (0.25: 9.3 m wide, 2.3 m deep,
  $9.2/kg). Depth, not volume, is what matters: the answer is always a liquid depth of about 2.3 m.
- **Horizontal vessel.** A long horizontal shell divided into stirred, sparged compartments keeps that
  depth at any volume. Ten 20 m³ compartments in one 200 m³ shell, priced as one vessel with the squat
  shape's steel penalty: 190 g/L and **$8.0/kg**. Seider's correlation prices a horizontal vessel a third
  below a vertical one of the same weight [18], but ten agitators are not counted, so this is a sketch, not
  an estimate. No animal-cell example was found.
- **Several spargers in a tall tank.** In the balance they add nothing. The exhaust already leaves at
  96% of equilibrium, so the CO₂ removed is set by the total gas leaving the top, wherever it went in.
  A second sparger helps only where the gas is not yet saturated (a measured +25% in CO₂ transfer
  coefficient in a 12.5 m³ tank, Nickel 2024, in the repo's earlier note) or if the limit on gas is damage
  at the sparger holes and not at the surface.

### 2.3 Which gas rule is right? (revised 2026-11-14 after reading the primary papers)

Pablo downloaded the five papers and the thesis; four were read in full text for this section [21–24].

**What the sources say.**

- **The limit Humbird cites is a flow per litre, and it has two causes.** Ozturk 1996 [21]: "Cell lysis and
  foaming issues, however, limit the sparging rates to about 0.1 vvm." No velocity is given. Humbird's
  6 mm/s is that figure converted at 20 m³.
- **Bubble damage goes with gas per litre of culture.** Tramper et al. 1988 [22], insect cells: "the
  first-order death-rate constant k_d is proportional to the air flow F and to the reciprocal height H",
  and k_d = F X′ / V, with X′ (the volume of culture killed per volume of gas) about 4 × 10⁻³ and
  independent of bubble size between 2 and 5 mm. Jöbses et al. 1991 [23], hybridoma: "the cell death rate
  is linearly proportional to the gas flow rate per unit volume"; the sparger and the bubbles' rise do
  no damage, the burst at the surface does. Handa-Corrigan et al. 1989 [24], hybridoma, myeloma and BHK
  cells: viability rises with column height at a fixed gas flow. Three groups, four cell types, the same
  result. All in columns of 2–5 cm across and up to 1.5 m tall.
- **A protectant cuts the damage about twentyfold.** Jöbses [23]: the death rate at 10 L/h through 80 mL
  fell from 1.1 per hour to 0.4 with 0.1 g/L of Pluronic F68 and to 0.05 with 1 g/L. That is a killing
  volume of 8.8 × 10⁻³, 3.2 × 10⁻³ and 4 × 10⁻⁴.
- All three papers conclude that taller vessels are better for cells at a given gas flow.

**What follows** (`sparge_death`; death rate = killing volume × gas per litre) [INF from the measured rule]:

| tank at the model's 6 mm/s | gas per litre | deaths, share of the growth rate (1 g/L protectant) |
|---|---|---|
| 20 m³, the model's shape | 0.096 vvm | 8% |
| 20 m³, squat (0.8) | 0.153 vvm | 13% |
| 200 m³, the model's shape | 0.045 vvm | 4% |
| 20 m³, no protectant | 0.096 vvm | 176% (the culture dies) |

1. **Bubble damage is a cost that rises with gas per litre, not a wall at a velocity.** With 1 g/L of
   protectant, each 0.1 vvm costs about 8% of the growth rate, if the small-column figure holds at 20 m³.
   The model does not count this loss anywhere, at the floor or elsewhere.
2. **The squat tank survives, with a smaller gain.** At 6 mm/s it passes 1.6 times the gas per litre of
   the reference tank, and 1.5 times Ozturk's "about 0.1 vvm". The extra deaths cost about 5% of output,
   roughly $0.3/kg, against a gain of $2.8. So it is not true that shape "gives nothing" under the
   per-litre rule, as the first version of this note said: that would follow only if 0.1 vvm were a hard
   limit. A squat tank is simply a way to pass more gas per litre at the same surface velocity. It is the
   right move if foam (a matter of velocity and surface) is what binds and the deaths are affordable.
   Raising the gas flow by half in the reference tank is the same thing by the damage measure.
3. **The model's penalty on large tanks is probably too harsh.** At a fixed 6 mm/s a 200 m³ tank gets
   half the gas per litre that the damage evidence allows. At 0.096 vvm it would hold the same 120 g/L as
   the 20 m³ tank (the "per-litre rule" columns in 2.2: $10.5–10.9 against $18.8). But that needs 13 mm/s
   through its surface, and whether foam allows it is not in any of these papers. Humbird's own fall of
   density with size has the same origin.
4. **The protectant is the parameter that matters.** At 0.1 g/L the same gas costs 64% of growth. Cells
   take protectant up (about 0.12 g/L per 10⁷ cells/mL, Gigout 2008 in the repo's earlier note, via a
   review), which at 4–6 × 10⁷ cells/mL is 0.5–0.7 g/L. Dense cultures need to be dosed well above 1 g/L.

*Update (section 6):* newer industrial work finds no extra deaths up to 0.1–0.2 vvm when 2–5 g/L of protectant
is used, so the small-column killing volume probably overstates the loss at scale; damage there comes mainly
from fast gas at the sparger holes.

**Probabilities, replacing the earlier 40%.**
- Death by bubbles scales with gas per litre in a 20 m³ tank as in the small columns: 85%.
- The squat tank delivers most of its gain (at least $2 of the $2.8/kg), given that the floor's own
  6 mm/s is tolerable: **50%** (35–65%). It needs the protected killing volume to stay under about
  10⁻³ at scale and at 120–190 g/L, and foam at 0.15 vvm to be manageable. Ozturk, who ran dense perfusion
  cultures, put the practical limit at "about 0.1".
- The floor's own gas assumption (0.096 vvm at 120 g/L) costs under 15% of growth to bubble deaths: 60%.

What would settle it: the killing volume at 100+ g/L with 1–3 g/L of protectant, in a column at least a
metre deep, and the foam behaviour at 0.1–0.2 vvm. Both are a few weeks at bench scale.

Also not counted against squat tanks: the model's oxygen-transfer formula has no depth in it, and a
shallow tank gives bubbles less time and less pressure to give up oxygen.

---

## 3. The cheapest published design: Negulescu et al. 2023's 262 m³ airlift

From the paper (full text [19]): 261.8 m³ with 209.4 m³ working, fed-batch to 100 g/L, oxygen uptake
"about 10.3 mmol O₂/L/hr", CO₂:O₂ of 1.2, oxygen transfer of 13.5 mmol/L/h checked, vessel priced from a
1997 figure for a 190 m³ airlift scaled by the 0.6 power. It gives no dimensions and does not check CO₂.
It builds on Li et al. 2020's "300 m³, 13.75 m tall" design, so the height is scaled from that: 13.1 m,
liquid 10.5 m deep.

| | paper's oxygen uptake (0.103 mmol/g/h) | the model cell's (0.149) |
|---|---|---|
| CO₂ made at 100 g/L, mmol/L/h | 12.4 | 17.9 |
| gas velocity needed at 100 mbar | **9.7 mm/s** | **14.0 mm/s** |
| the same as gas per litre | 0.055 vvm | 0.080 vvm |
| density it holds at the model's 6 mm/s | **62 g/L** | **43 g/L** |
| gas velocity needed at 50 mbar | 19 mm/s | 28 mm/s |

- Against the model's 6 mm/s the design holds 43–62% of its stated density. Its capital per kg would be
  1.6 to 2.3 times higher, taking its $28k per m³ to the equivalent of $45–65k. It stays the cheapest
  design by far; its cost is mostly medium.
- The paper's oxygen uptake is 31% below Humbird's for the same 3 ng cell. With the model's cell the
  design's own oxygen check fails too (14.9 needed, 13.5 supplied).
- 10–14 mm/s is ordinary for an airlift: 10–15 mm/s is quoted as the usual maximum for cell-culture
  airlifts (a thesis, snippet [20]), and animal cells have been grown in airlifts of 2 to 5 m³ (Lonza;
  snippet [20]). The gas enters only the riser, where the velocity is about twice the figure above.
- Per litre the design needs less gas than the model allows a 20 m³ tank (0.055–0.08 against 0.096 vvm).
  So it fails on velocity and passes on gas per litre. By the damage evidence in section 2.3 its bubble
  deaths would be lower than the floor tank's; what is unknown is foam and gas hold-up at 10–14 mm/s.
- A further problem is outside the CO₂ balance: Humbird notes that Li et al.'s oxygen uptake was half
  the authors' own reference value, so cells would run out of oxygen in the 20-second descent (Humbird's
  report, footnote 54, read by a subagent in full text). Li et al. was not read.

Verdict: neither confirmed nor refuted. At 100 mbar it needs 1.6–2.3 times the model's gas velocity.

---

## 4. Should this be a lever in the model?

Not yet. The flux can be derived and agrees with published devices within a factor of 2–4, but the
membrane price rests on one search-result range and a pharma filter 7 times dearer, and no steam-proof
module of this size exists to price. `floor_with_loop` gives the numbers above without touching
`floor_physics.explore` or the page.

If a price is found, the option would be: in `explore`, a switch "CO₂ removed by a membrane loop" that
(1) drops "CO₂ removal" from the limits, (2) adds capital of area × price × 3 per m³, with area =
12.4 m² × (CO₂ made − CO₂ the sparger removes) at the resulting density, (3) adds membrane replacement
and pumping to consumables and utilities, with the same in the page's `floorExplore` and one case in the
parity grid. A second switch, "no sparging", would lift the oxygen limit and size the loop for oxygen.

Two smaller changes are better supported and could go in sooner:
- a note on the tank-shape lever and tornado bar that its gain assumes a velocity limit on gas;
- steel and floor for squat tanks (`shape_capex_factor`), which move the best shape from the end of the
  lever to about 0.75 and cost $0.4/kg there.

---

## 5. Summary for Pablo

**Answer.** A membrane loop can take out the CO₂ a sparger cannot, but its size is set by how little CO₂ a
litre of culture gives up per pass (about 1 mmol, because bicarbonate cannot be released without an acid),
not by membrane area. For a 20 m³ tank at 190 g/L that means about 180 m³/h through about 2,500 m² of
0.5 mm fibres, roughly $80k per m³ of tank at an assumed price. A tank with no sparging at all needs four
times that. A squat tank gets about the same gain with no new equipment by passing more gas per litre;
it pays in cells killed by bubbles, a few percent of growth if the protectant works at scale (section 2.3).

**Probabilities** (revised after the stress test in section 6; the first version said 50% and 30%).
- A CO₂ loop beside a sparger can be made to work technically at 20 m³ for CHO-like single cells, given a
  development programme: **35%** (25–50%). Down because gas fibres last only 2–4 weeks in blood and the
  cheap kind leaks within days, against a 33-day run, and because no module survives repeated steaming.
- It works and lowers the floor by $1/kg or more, with the modules paid for: **15%**. Down because the one
  priced module of the right material can be steamed once only, which would put the floor at $35, and
  because more sparging with more protectant may do the same job without a loop.
- A no-sparging tank at 190 g/L is workable at 20 m³: **15%**. It needs 30–50 passes an hour and
  oxygen-rich return liquid.
- The same for cells that grow in clumps or on carriers: under 5%.

**The experiment that would settle it.** Two steps, the first needing no cells.
1. *One week, bench, no cells.* Pump culture medium with 31 mmol/L bicarbonate at 100 mbar of CO₂ and pH
   7.2 through a small silicone hollow-fibre module at 1,000 per second. Measure CO₂ removed per m² and
   per litre, and the outlet pH. Predicted: about 80 mmol/m²/h, 1.1 mmol/L per pass, pH +0.26. Repeat
   with 5 mmol/L of added buffer, and with a suspension of dead or fixed cells at 15% by volume. This
   tests the claim that bicarbonate is not available, which sets the whole design.
2. *Six weeks, 2–10 litres.* A perfusion run of a suspension line at 100 million cells/mL or more with the
   module on the recirculation line and the sparger turned down to 1 mm/s equivalent. Measure dissolved
   CO₂, growth and viability against a sparged control, the decline of flux over 30 days, and the flux
   after a steam cycle. Success: CO₂ held at 100 mbar at 11 passes an hour with growth within 10% of the
   control and flux loss under 30%.

A cheaper route comes before either (section 2.3, now read in the primary papers): bubble damage goes with
gas per litre and a protectant cuts it twentyfold, so more gas per litre, in a squat tank or otherwise, may
be affordable. Measure the killing volume and the foam at 0.1–0.2 vvm in a dense culture first. If both are
acceptable, build squat tanks and skip the loop.

**The model's floor with it.** $9.2/kg with a CO₂ loop at the assumed price (range $8.6–13.8 across
membrane prices; $6.1 in a yeast-style plant), against $11.5 today and $8.7 for a squat tank under the
velocity rule. Neither reaches the $7 that parity needs in the floor's plant.

---

## 6. Stress test of the two loop probabilities (added 2026-11-14)

Asked by the parent session: go back to the five things the 50% and 30% rest on. Sources for this section
were read by four subagents; access levels are given for each point. One search was stopped by the
safeguard and rerun on another model.

**1. CO₂ given up per pass. Moves it up a little.** (`suspension_buffer`, `co2_per_pass`)
- Medium: about 1 mmol/L of phosphate (DMEM/F12 level, memory) buffers 0.47 mmol/L per pH unit at pH 7.2.
  That takes the amount per pass from 1.11 to 1.23 mmol/L. HEPES would add much more but is not used at
  large scale (patent snippets) and adds salt. Amino acids and serum-free media add little (not found).
- The cells: their insides buffer about 10–50 mmol/L per pH unit of cell water (a physiology review,
  snippet; about 10 in a muscle-like line, snippet). At 18% of the volume, 70% of it water, that is 1.3–4.3
  mmol/L per pH unit of culture. If it acts within the 6 seconds in the fibre, a pass gives up 1.55–2.16
  mmol/L, the loop needs 6–8 passes an hour in place of 11, and the floor with the loop goes from $9.2 to
  $9.0. It acts only if the cells carry carbonic anhydrase, which speeds the reaction; without it the
  reaction takes 5–10 seconds (textbook constants, snippet). No data were found on the enzyme in CHO,
  fibroblast or muscle cells.
- Blood does better because its red cells are 45% of the volume and full of haemoglobin, which buffers
  30–40 mmol/L per pH unit of blood, ten times what these cells could offer.

**2. Cells surviving the pump and fibres. No change.** Weeks of pumping dense cultures through hollow fibres
are documented only at 1–4 litres: Clincke 2013 (full text, read earlier) and a vendor note of a 1–2 L CHO
run at 12–24 tank volumes an hour through 1 mm fibres with a magnetically levitated pump, 54 million
cells/mL, three weeks, stopped by choice (Meissner application note, vendor, full text). A HEK study found
viability fell at high flow and that one tubing material damaged cells (Zhan 2020, full text via a tool).
Filter loops end when debris plugs the pores. No run at 500–2,000 L with its flow and shear was found.

**3. Fouling of gas fibres over weeks. Moves it down.** Polymethylpentene and silicone lungs last about 2–4
weeks in blood; clotting is the main limit and gas transfer declining is a common reason to change them
(snippets; a registry found patients needing a second lung after a median 19 days). Microporous
polypropylene turns wettable and leaks plasma after hours (snippets). A polypropylene contactor on
wastewater lost about half its flux in 13 days (snippet). The floor's runs last 33 days. Nothing was found
for cell-culture debris or antifoam on gas fibres.

**4. Module price and sterilisation. Moves it down, and is the strongest single finding.**

| module | $ per m² | sterilisation | source, access |
|---|---|---|---|
| PermSelect silicone, 0.1 to 2.1 m² | 4,300 to 704 | steam or autoclave **once**, at 121 °C at most; or gamma | vendor web store and data sheet, Nov 2026 |
| Liqui-Cel polypropylene, 8x20 to 14x28 | about 80–265 | hot water at 85 °C at most, about 1,000 cycles; no steam | distributor listing, Nov 2026 (areas from memory); 3M cleaning guide, full text |
| silicone tubing | about 800 | autoclavable | distributor listing |
| CO₂-capture studies | 50–200, 3–5 year life | (gas service) | snippets |

No module was found that is both rated for repeated steaming and priced. The cheap ones are polypropylene,
which leaks in protein-rich liquid. With the priced silicone module replaced every run, the floor with the
loop is $34.8/kg; at $704 lasting 2 years it is $11.0, which is no gain; large contactors at $160 lasting 2
years give $9.1.

**5. The acid-side option. Rules it out with bought acid; leaves a salt-free version that needs a filter
the size of 400–2,300 pharma units.** (`acid_side`)
- Adding acid before the fibres turns bicarbonate into CO₂: 10 mmol/L of acid raises the CO₂ removed per pass
  from 1.1 to 6.1 mmol/L and cuts the loop to 2 passes an hour. But the tank must stay at its pH, so the
  same amount of base goes back in after the fibres. Acid plus base is salt: 10 mmol/L of salt per pass,
  which the medium must wash out. The floor's culture has almost no room left under the salt limit (lactate
  and bicarbonate already take it to 413 of 415 mOsm/kg), so the medium would rise from 11 to 84 litres per
  kg, **$11 more per kg**. Even 2 mmol/L of acid costs $6. Medical CO₂ removal can do this because the
  patient's kidneys clear the salt.
- Making the acid and base from water by electrodialysis adds no salt and little power (about 0.2 kWh per
  kg). But its membranes cannot take a cell suspension, so the loop's liquid would have to be filtered free
  of cells first: 18–95 m³/h, which at what a perfusion filter passes (3.8 L/m²/h) is 4,800–25,000 m² of
  filter, 430–2,300 of the largest pharma units. Not practical.

**A sixth point that moves the loop's value down: more sparging may do the job.** Newer industrial work
(read by a subagent; abstracts and vendor documents) finds that with enough protectant (2 g/L for coarse
bubbles, 5 g/L for fine ones) dense CHO cultures showed no extra deaths up to 0.1–0.2 vvm at 3–200 L (Xu
2017, abstract), 4–5 g/L held 100–250 million cells/mL (Wei 2023, abstract; vendor note, snippet), and
2,000-litre single-use tanks are rated to 0.2 vvm in all (Sartorius data sheet, full text; Thermo note,
full text). Damage at scale comes mainly from gas leaving sparger holes faster than about 30 m/s (Zhu 2008,
abstract), which more protectant does not fix. If the floor's tank could run at 0.2 vvm, CO₂ would stop
binding and the floor would be $8.5 without a loop, before the cost of the protectant. Foam is the open
limit: it scales with gas speed through the surface (Pilon 2001, full text), and no measured foam ceiling
for cell-culture media was found. This is the gas-flow session's question.

---

## 7. Keeping the loop, dropping the membrane: a packed column, headspace pressure, and both together (added 2026-11-14)

Asked by the parent session, relaying Pablo: size by calculation the tricks that keep the pumped loop but
need no membrane, and say what physics settles and what only a bench test can. Code: `packing_film`,
`column_design`, `column_cost`, `headspace_pressure`, `loop_mixing`, `floor_with_column`; tests pin every
number below. Two hooks were added to `floor_physics.explore` (`otr_x`, `mix_x`, default 1, Python only).

### 7.1 A packed stripping column on the loop

The culture is pumped to the top of a short column of stainless sheet-metal packing (Mellapak 250Y type),
runs down it as a thin film against a sweep of air going up, and drains back to the tank. No bubbles burst
and there is no membrane; everything is steel that can be steamed.

How it was sized. Wetted area: Tsai et al. 2011 (form read in full in Wang's 2015 thesis). Film: laminar
(Nusselt) film along 45° channels. Liquid-side coefficient: Rocha, Bravo and Fair 1996 (penetration over one
corrugation side, 18.7 mm from the packing's measured geometry; the renewal factor 0.9 is from memory).
Cross-check: Billet and Schultes' penetration form gives a coefficient within 10%. Counter-current, log-mean
driving force; fresh air enters at the bottom, the sweep leaves the top at 20 mbar of CO₂.

| at 189 g/L, sparger kept at 6 mm/s | value |
|---|---|
| CO₂ the column must take | 12.6 mmol/L/h (34.1 made, 21.5 by the sparger) |
| culture leaving the column | 20 mbar of CO₂, so 1.97 mmol/L removed per pass; pH +0.7 for the time on the packing |
| passes | 6.3 tank volumes an hour (100 m³/h) |
| column | 1.8 m across, 0.49 m of packing (1.9 transfer units of 0.26 m) at 40 m³ per m² per hour |
| film | 0.34 mm thick, 19 cm/s, wall shear 2.4 Pa (1,700 per second), renewed every 0.1 s; 3.7 s on the packing |
| sweep air | 260 m³/h, 29 mm/s up the column, about 1% of the flooding gas rate |
| pump | 100 m³/h against about 4.5 m of head: 130 W per m³ of culture (power cost $0.002/kg) |
| oxygen it adds with an air sweep | 0.14 mmol/L per pass, 0.9 mmol/L/h (3% of the need) |
| installed cost | $26k per m³ of tank (packing, shell, distributor from Wang's vendor fits, plus a pump, ×3) |

At 258 g/L (the thickness limit) the culture is 1.8 mPa·s, the film 0.37 mm and the transfer unit 0.28 m: the
design hardly changes. The kinetics of bicarbonate do not matter: with no buffer only dissolved CO₂ can leave
(section 1.2), and that leaves at the film's rate. Taking the culture down to 10 mbar instead of 20 removes
2.2 mmol/L per pass for 0.7 m of packing but raises the pH by a full unit.

Floor, with the column's capital on the plant:

| case | today | with the column | density, what binds |
|---|---|---|---|
| sparger at 6 mm/s | 11.5 | **8.6** | 189 g/L, mixing |
| sparger at 2 mm/s (the gas-flow session's bad case), column for CO₂ only | 28.0 | 15.8 | 81 g/L, oxygen |
| 2 mm/s, column also carries oxygen, air sweep | 28.0 | 8.9 | 189, mixing (115 passes, 1,840 m³/h: a 7.7 m column) |
| 2 mm/s, oxygen sweep recycled through a lime scrubber | 28.0 | **8.9** | 189, mixing (22 passes, 347 m³/h, 3.3 m across; oxygen and lime $0.21/kg) |
| 2 mm/s, oxygen sweep once through and vented | 28.0 | 10.6 | the vented oxygen costs $1.9/kg |

So: a closed oxygen sweep with a lime scrubber is affordable. The lime (at $240/t, USGS snippet, 70% used)
costs about $0.20 per kg of cells; the oxygen the column hands over costs about $0.01 at Humbird's $0.15/kg.
Venting the sweep instead throws away about 50 times the oxygen the cells use. Venting is not affordable.

Compared with the membrane loop: the column needs fewer passes (6 against 11, because it can strip deeper
without a long fibre), no membrane, and costs a third as much ($26k against $78k per m³ at the membrane's most
optimistic price). Its cost is small enough that a factor of three error moves the floor by $0.3.

**Verdict, packed column.**
- *Settled by calculation:* size, flow, power, sweep and cost, and that it removes the CO₂ limit for about
  $0.1–0.2/kg; with an oxygen sweep and a scrubber it also covers a sparger cut to 2 mm/s. Floor $8.6 (6 mm/s)
  or $8.9 (2 mm/s).
- *Settled by literature:* nothing either way for animal cells. No one was found to have run animal or insect
  cells through a falling-film, packed or trickle contactor; blood disc oxygenators of the 1950s–60s destroyed
  far fewer red cells than bubble oxygenators (secondary source, snippet); damage in sparging is tied to
  bubbles bursting, which a film lacks; anchorage-dependent CHO cells stick to steel (patent snippet).
- *Only a bench test can tell:* whether cells tolerate 6–27 passes an hour over the packing (a free surface
  renewed ten times a second, drips from the distributor, a pH rise of 0.7 for 4 seconds) for a month, and
  whether they coat the packing.

### 7.2 Does the loop also lift the mixing limit?

The model's mixing rule (Humbird's) says oxygen transfer cannot be faster than 1/(mixing time), 141 s at
20 m³. The column loop turns the tank over every 9.5 minutes at 6 passes an hour (2 minutes at 30), slower than
or similar to the stirrer's mixing time. Its return jet adds 8 W per m³ to the stirrer's 43 (38 W at 30 passes),
which shortens the mixing time by 6% (23%), since mixing time goes as power^(−1/3) in the same equation.

**Verdict, mixing.**
- *Settled by calculation:* a loop of this size does not relax the model's mixing limit materially (×1.06).
  The model should keep it.
- *Settled by literature:* the rule itself is a rule of thumb (Humbird, after his ref. 127), not a measurement.
- *Only a bench or plant test can tell:* whether 189 g/L is really where oxygen gradients start to hurt in a
  20 m³ tank.

### 7.3 Headspace overpressure for oxygen

The model's 29 mmol/L/h is Humbird's: 90% oxygen sparged, the top at 0.33 bar gauge (his Sect. 4.1, as quoted
by the gas-flow session), kLa 26.4 per hour. With half the liquid head added, the oxygen the liquid could hold
is 1.38 mmol/L, so his figure implies the culture is held at about 0.28 mmol/L of dissolved oxygen (a little
above saturation with air). Holding that level and raising the top pressure:

| top of tank | oxygen transfer | oxygen-limited density | mixing-limited density |
|---|---|---|---|
| 0.33 bar gauge (model) | 29.0 mmol/L/h | 195 g/L | 189 g/L |
| 0.5 bar gauge | 33.0 (×1.14) | 222 | 215 |
| 1.0 bar gauge | 44.9 (×1.55) | 301 | 293, so the thickness limit (258) binds |

The mixing limit rises by the same factor because, in the model's own rule, transfer is capped by kLa and the
oxygen moved at that kLa scales with the driving force.

- *CO₂ is not helped:* at a fixed gas velocity at the top the gas carries pCO₂/RT per unit volume whatever the
  pressure, so overpressure alone leaves the floor at $11.5. (If instead the gas mass flow were held fixed, the
  dissolved CO₂ would rise with pressure.) Holding the velocity means 1.5 times more gas by mass at 1 bar gauge,
  so more oxygen bought; the model does not price the sparge oxygen.
- *The tank allows it:* steaming at 121 °C already takes 1.0 bar gauge, and stainless culture vessels are
  typically rated to 3–4 bar gauge (vendor data sheets).
- *Cells:* the only data found are for small hydrostatic pressures (CHO at up to 0.12 bar more, slower early
  growth and higher peak density; snippet). Dissolved oxygen is held where it is; total pressure of 2 bar
  absolute is what changes.

**Verdict, overpressure.**
- *Settled by calculation:* 1 bar gauge raises the oxygen and mixing limits by 55%; alone it changes nothing,
  because CO₂ still binds at 120 g/L.
- *Settled by literature:* existing steam-rated tanks take the pressure.
- *Only a bench test can tell:* whether the cells grow the same at 2 bar absolute with dissolved oxygen and
  CO₂ held fixed.

### 7.4 All together

Column on the loop with a recycled oxygen sweep, plus 1 bar gauge in the headspace. Every gas-side limit is
then above the thickness of the culture (258 g/L):

| | sterile plant without clean rooms | yeast-style plant |
|---|---|---|
| sparger at 6 mm/s | **$7.2/kg** (12.6 passes, 201 m³/h, a 2.5 m column, $33k per m³) | **$5.0/kg** |
| sparger at 2 mm/s | **$7.4/kg** (26.7 passes, 427 m³/h, 3.7 m across, $44k per m³) | **$5.2/kg** |
| for reference, today | $11.5 (at 2 mm/s: $28.0) | $6.6 (at 2 mm/s: $13.4) |

With these tricks the floor no longer depends on how much gas the cells tolerate. In the sterile plant it
lands at about $7, the parity mark. What remains is the culture's thickness limit, the plant class, and the
cells (doubling time, waste, medium), plus the protectant cost that the floor leaves out.

**Verdict, the combination.**
- *Settled by calculation:* $7.2–7.4/kg in the floor's plant and $5.0–5.2 in a yeast-style plant, whatever the
  gas-flow cap, for $33–44k per m³ of added capital.
- *Settled by literature:* the parts exist as industrial equipment (packing, scrubbers, pressure-rated tanks);
  none has been used with animal cells.
- *Only a bench test can tell:* the three cell questions above (the film, 2 bar absolute, and the 258 g/L
  thickness limit itself, which is Humbird's estimate from viscosity, not a measured culture).

### 7.5 The membrane lead

Membrane-aerated wastewater reactors (OxyMem, ZeeLung, Fluence) are sold by the thousand m², but no price per m²,
material confirmation or steam rating was found (vendor pages and a patent). The earlier result stands: no
gas-exchange membrane is both priced and rated for repeated steaming. The column makes the question moot.

---

## 8. How far calculation and literature settle the three cell questions (added 2026-11-14)

Pablo asked whether the three open questions can be settled by simulation or literature rather than given
probabilities. Code: `column_stresses`, `drop_height_for`, `loop_ph_exposure`. Literature read by two
subagents (on Sonnet, as biology searches; several calls were refused by the safeguard and not retried).

### 8.1 Cells on the column: mostly settled, and the pH result changed the design

| what a cell meets | on the column (189 g/L) | measured reference | source, access |
|---|---|---|---|
| wall shear stress | 2.4 Pa (1,700 per second) | CHO: no effect for weeks at 1,000–3,400 per second in fibres, about 2.6 Pa at medium viscosity | Clincke 2013, full text |
| | | CHO necrosis "at about 1 Pa" in simple shear; the abstract's wordings conflict | Tanzeglock 2009, abstract |
| energy dissipated in the film | at most 4,000 W/m³ at the wall, 1,300 on average | CHO growth stops at about 2.9 × 10⁵ W/m³ with repeated exposure; lysis above about 10⁶ | Godoy-Silva 2009, snippet |
| where packing sheets cross | about 2 × 10⁴ W/m³ [estimate, u³/δ] | as above | |
| a drop falling 5 cm from the distributor | about 2.5 × 10⁵ W/m³ [estimate, v³/d]; 10⁶ at a 13 cm fall | as above; inkjet-printed fibroblasts kept ≥94–95% viability at about 2 m/s | Saunders 2008, Li et al. (arXiv 1310.0656), snippets |
| a free surface with no bursting bubbles, renewed every 0.1 s | | CHO reached 1–2 × 10⁸ cells/mL in rocking bags aerated only through the wave surface (10 L), and orbitally shaken vessels with a wall film and no sparging ran at 1,000 L | Clincke 2013; Zhang 2009, snippet; Kühner, vendor |
| alkaline liquid (CO₂ stripped) | +0.7 pH while in the loop, if stripped to 20 mbar | CHO: a zone of +0.37 pH holding 7.5% of the culture, 35–44 s per pass, cut peak cell density by 18–52% | Paul et al. 2020, full text via a summary |

What this settles:
- **Shear in the film: settled, it is fine.** The film's wall stress is below what CHO took for weeks in
  Clincke's fibres (full text). Its energy dissipation is about 70 times below the repeated-exposure
  growth limit.
- **Drips: settled by design.** A free fall of more than a few centimetres onto the packing approaches the
  growth limit, and 13 cm reaches the lysis range. The distributor must lay the liquid onto the packing (a
  flooded trough or a pipe at the packing surface), not drip it from height. This is an order-of-magnitude
  estimate, not a simulation.
- **A free surface without bubbles: no direct evidence for a film, but strong precedent.** The two bubble-free
  culture systems in use (rocking bags, orbital shakers) aerate through renewing free surfaces and wall films
  and reach the highest CHO densities on record.
- **pH: the literature says the first design was too harsh, and a gentler one avoids it.** Liquid stays
  alkaline until it re-mixes with the tank, so the share of the culture exposed is the loop's volume over the
  tank's, whatever the flow. Stripped to 20 mbar with 1 m³ in the loop, the exposure (rise × share) is 1.6 times
  the one that hurt CHO. Stripped only to 55 mbar (+0.26 pH) with 0.5 m³ in the loop it is 0.29 times
  (0.18 with 0.3 m³). The gentler column needs 11 passes an hour, 178 m³/h, 2.4 m across and 0.18 m of packing,
  $30k per m³ of tank, and leaves the floor at **$8.6**. Taking "rise × share" as the measure is my inference
  from one study.
- **Not settled: deposits on the packing over a month, and meat cells rather than CHO.** Anchorage-dependent
  CHO stick to steel (patent snippet); suspension-adapted lines are selected not to. Nothing was found for
  meat cells.

### 8.2 Cells at 2 bar absolute: largely settled

- **Calculation.** In the model's tank today the bottom of the liquid is already at 1.71 bar absolute (0.33 bar
  gauge at the top plus 3.7 m of liquid). With 1 bar gauge at the top, the cells see 2.0 bar at the top and 2.38
  at the bottom: at most 0.67 bar more than they already pass through every circulation. Dissolved oxygen and
  CO₂ are held at their usual levels.
- **Literature.** The lowest pressures with reported effects on cultured cells are cyclic loading of 0.4–5 MPa
  (4–50 bar) in cartilage-forming cells, and cytoskeletal damage starts near 24–30 MPa (snippets). One CHO
  study saw slower early growth and higher final density under 0.004–0.012 MPa of extra hydrostatic pressure
  (snippet; odd, and a single study). No animal-cell culture run at 0.5–2 bar gauge headspace was found.
- **Verdict:** the added 0.07 MPa is about 6 times below the lowest pressure with a reported effect, and within
  a factor of 1.4 of what cells already meet at the bottom of the tank. Only the single odd CHO result keeps it
  from being settled.

### 8.3 More gas per litre: settled for CHO, not for meat cells

- **Literature.** Dense CHO cultures ran at 0.1–0.2 vvm with 2–5 g/L of protectant at 3–200 L with no extra
  deaths, and 2,000-litre tanks are rated to 0.2 vvm (section 6). Damage at scale is set mainly by gas leaving
  sparger holes faster than about 30 m/s, a design choice.
- **Not found:** any meat cell line in a sparged tank with its gas rate and protectant stated. Pasitka et al.
  grew chicken fibroblasts to 1.08–1.3 × 10⁸ cells/mL in suspension (abstract), but the aeration was not in
  what could be read. Duck embryonic fibroblasts were "highly shear-sensitive" in rocking and orbital vessels
  and did better in a stirred tank (2026, snippet).
- **Foam cannot be simulated reliably:** it depends on the medium's proteins and protectant. It needs a test.
- **Verdict:** this one still needs an experiment, but it matters less now: with the column and pressure the
  floor is $7.3–7.4 whatever the gas rate.

### 8.4 What changes in the experiments list

| question | before | now | why |
|---|---|---|---|
| more gas per litre | 50% | 50% | CHO settled; meat cells and foam untested |
| cells on the column | 45% | **60%** | shear settled, drips designed out, pH settled by the gentler design; deposits and meat cells untested |
| cells at 2 bar absolute | 70% | **85%** | added pressure 6× below the lowest reported effect and close to what cells already see at the bottom |

---

## Sources

Access: FT = full text read; AB = abstract; SN = search snippet; V = vendor page or data sheet. Items 1–8
and 13 were read by a subagent, 9–12 and 14 by a second, 15–18 and 20 by a third; 19 was read directly.

1. Arazawa DT et al. Immobilized carbonic anhydrase on hollow fiber membranes accelerates CO₂ removal from
   blood. J Membr Sci 2012;403-404:25. https://pmc.ncbi.nlm.nih.gov/articles/PMC3433239 . FT. 79 → 108
   mL/min/m² in bovine blood (+36%); +40% to +95% in saline.
2. Kaar JL et al. Towards improved artificial lungs through biocatalysis. Biomaterials 2007;28:3131.
   doi:10.1016/j.biomaterials.2007.03.021 . AB. Up to +75% in bicarbonate solution; no absolute rates.
3. Kimmel JD et al. Carbonic anhydrase immobilized on hollow fiber membranes using glutaraldehyde activated
   chitosan for artificial lung applications. J Mater Sci Mater Med 2013. https://pmc.ncbi.nlm.nih.gov/articles/PMC3826877 .
   FT. Saline: 91.5 → 196.6 mL/min/m² (+115%), 0.0119 m², 45 mL/min, about 50 mmHg; +37% in blood.
4. Arazawa DT et al. Kinetics of CO₂ exchange with carbonic anhydrase immobilized on fiber membranes in
   artificial lungs. J Mater Sci Mater Med 2015;26:193. https://pmc.ncbi.nlm.nih.gov/articles/PMC5973791 . FT.
   Saline 75 → 154; whole blood, unmodified, 222 mL/min/m²; liquid boundary layer is the main resistance.
5. Arazawa DT et al. Acidic sweep gas with carbonic anhydrase coated hollow fiber membranes synergistically
   accelerates CO₂ removal from blood. Acta Biomater 2015;25:143. doi:10.1016/j.actbio.2015.07.007 . AB (+109%,
   411 mL/min/m²); SN (197, 258, 230).
6. Hospach I et al. In vitro characterization of PrismaLung+. Intensive Care Med Exp 2020.
   https://pmc.ncbi.nlm.nih.gov/articles/PMC7221037 . FT. 44–133 mL/min from 0.35–1.35 m² at 300–450 mL/min of
   blood; removal rises with flow and inlet CO₂; pressure drops 7–38 mmHg.
7. Zanella A et al. Blood acidification (Intensive Care Med 2009;35:1484), acidified dialysate (J Heart Lung
   Transplant 2014;33:536), respiratory electrodialysis (ASAIO J 2016;62:143). AB. +70%, ×2.6, ×3.4.
8. Burki NK et al. A novel extracorporeal CO₂ removal system (Hemolung). Chest 2013;143:678.
   doi:10.1378/chest.12-0228 . AB. 82.5 mL/min at 430 mL/min of blood; the 0.59 m² area is SN.
9. Clincke M-F et al. Very high density of CHO cells in perfusion by ATF or TFF in WAVE bioreactor, Parts I
   and II. Biotechnol Prog 2013. https://pmc.ncbi.nlm.nih.gov/articles/PMC3752962/ ,
   https://pmc.ncbi.nlm.nih.gov/articles/PMC3752935/ . FT. Flows, fibre sizes, shear rates, densities, run
   lengths, the viscosity equation, CO₂ of 17–31 kPa.
10. Blaschczok K et al. Investigations on mechanical stress caused to CHO suspension cells by standard and
    single-use pumps. Chem Ing Tech 2013;85:144. doi:10.1002/cite.201200135 . SN, no numbers.
11. Frahm B et al. Dynamic membrane aeration. Cytotechnology 2009. https://pmc.ncbi.nlm.nih.gov/articles/PMC2677146 .
    FT. Tubing sizes, 30–68 m² per m³, 200 L, limits above 8 million cells/mL, debris on tubing.
12. US Patent 12,415,980. https://patents.google.com/patent/US12415980 . FT of the first third. Applicant's data.
13. 3M Liqui-Cel EXF membrane contactors, cleaning and storage guide.
    https://static.lenntech.com/Data-sheets/3M-Liqui-Cel-EXF-Membrane-Contactors-cleaning-storage-L.pdf . V, FT.
    Data sheet LC-1035 (10x28: 10–48 m³/h, 0.14–0.48 bar), V, values read off charts.
14. Not found: tolerance of seconds-long pH swings or of high dissolved oxygen; laminar shear thresholds in
    Pa; fouling or repeated-steaming data for any gas-exchange fibre in culture broth; any alkaline sweep
    liquid stripping CO₂ from a bicarbonate stream; any membrane loop on cells above 2 litres.
15. Hollow-fibre membrane cost of "USD 40–200 per m²", 5-year life. Eng. Proc. 2023;37(1):119.
    https://www.mdpi.com/2673-4591/37/1/119 . SN (the page refused automated reading).
16. Humbird D. Scale-up economics for cultured meat (report and paper), 2021.
    https://pmc.ncbi.nlm.nih.gov/articles/PMC8362201 . FT. ATF-10 at $16,300; bioreactor $330k bare and $1.5M
    installed at 20 m³; building rates; sparge limit.
17. CE Delft 2021, via `research_notes/plant_capital_crosscheck.md` (overall installation factor about 3).
18. Seider WD et al., Product and Process Design Principles, 4th ed. 2017, vessel cost and thickness
    correlations as coded in BioSTEAM.
    https://biosteam.readthedocs.io/en/latest/_modules/biosteam/units/design_tools/flash_vessel_design.html . FT of the
    code, not of the book.
19. Negulescu PG et al. Techno-economic modeling and assessment of cultivated meat. Biotechnol Bioeng
    2023;120:1055. doi:10.1002/bit.28324 . FT of the main text (local PDF); supplementary tables not read.
20. Airlift practice: thesis at https://core.ac.uk/download/323206707.pdf (10–15 mm/s), SN; Lonza airlifts of
    2,000 and 5,000 L, SN; Li X et al. Chem Eng Sci 2020;211:115269, not read (known through [16] and [19]).

21. Ozturk SS. Engineering challenges in high density cell culture systems. Cytotechnology 1996;22:3–16.
    doi:10.1007/BF00353919 . FT (local PDF, sparging and aeration passages). "About 0.1 vvm", for cell lysis
    and foaming; silicone tubing supports about 5 × 10⁷ cells/mL and was used up to 200 L.
22. Tramper J, Smit D, Straatman J, Vlak JM. Bubble-column design for growth of fragile insect cells.
    Bioprocess Eng 1988;3:37–41. doi:10.1007/BF00372858 . FT (local PDF).
23. Jöbses I, Martens D, Tramper J. Lethal events during gas sparging in animal cell culture. Biotechnol
    Bioeng 1991;37:484–490. doi:10.1002/bit.260370510 . FT (local PDF; results and discussion). One figure
    caption gives a death rate that does not fit the others and may be a scanning error; the numbers used
    are from the text.
24. Handa-Corrigan A, Emery AN, Spier RE. Effect of gas–liquid interfaces on the growth of suspended
    mammalian cells: mechanisms of cell damage by bubbles. Enzyme Microb Technol 1989;11:230–235.
    doi:10.1016/0141-0229(89)90097-5 . FT of the abstract and the column-height results (local PDF).
    Downloaded and not read: Tramper et al. 1986 (doi:10.1016/0141-0229(86)90007-4) and the Wageningen
    thesis (https://edepot.wur.nl/198209).

Added for sections 6 and "For the experiments list" (read by subagents):
25. PermSelect PDMS modules, web store prices and PDMSXA-1000 data sheet; sterilisation page
    https://www.permselect.com/markets/bioreactor/sterilization . Vendor, Nov 2026.
26. Liqui-Cel prices, https://parts.deutscheequipment.com/collections/3m-liqui-cel . Distributor listing, Nov 2026;
    membrane areas from memory. 3M Liqui-Cel cleaning guide (hot water 85 °C, about 1,000 cycles), full text.
27. Xu S et al. Bioprocess Biosyst Eng 2017;40:1317, doi:10.1007/s00449-017-1790-2 . AB. Wei et al. Biotechnol
    Prog 2023;39:e3340, doi:10.1002/btpr.3340 . AB. Tharmalingam & Goudar, Biotechnol Bioeng 2015;112:832 . AB.
    Gigout et al. Biotechnol Bioeng 2008;100:975 (11.7 µg per million cells) . AB via snippet. Zhu et al.
    Biotechnol Bioeng 2008;101:751 (sparger-hole gas speed) . AB.
28. Sartorius Biostat STR data sheet (0.1 vvm microsparger, 0.2 vvm in all), full text; Thermo HyPerforma 2,000 L
    application note (0.1–0.2 vvm, 23 m/s), full text; Sherman et al. BioProcess Int 2016, full text.
29. Pilon L, Fedorov AG, Viskanta R. J Colloid Interface Sci 2001;242:425 (foam height and gas speed), full text.
30. Meissner SepraPor application note (1–2 L CHO, levitated pump, three weeks), vendor, full text; Zhan et al.
    iScience 2020, https://pmc.ncbi.nlm.nih.gov/articles/PMC7593556 , full text via a tool.
31. Oxygenator life and plasma leakage, ECMO registry: snippets (https://pmc.ncbi.nlm.nih.gov/articles/PMC6260321 ,
    https://www.researchgate.net/publication/11117007).
32. Intracellular buffering 10–50 mmol/L per pH unit, snippet
    (https://comprehensivephysiology.com/WileyCDA/CompPhysArticle/refId-cp140109.html); CO₂ reaction constants,
    snippet. Poloxamer 188 price: Sigma-Aldrich Parteck PLX 188, about $260/kg at 25 kg, vendor.

Added for section 7 (read by subagents):
33. Wang C. PhD dissertation, UT Austin 2015 (sites.utexas.edu/rochelle/files/2015/02/PhD-Dissertation_Wang-Chao.pdf).
    Full text: Tsai 2011 area correlation, Mellapak 250Y measured geometry, packing and column cost fits (2014 $).
    Tsai RE et al. AIChE J 2011;57:1173 and Rocha JA, Bravo JL, Fair JR. Ind Eng Chem Res 1996;35:1660, as
    reproduced there.
34. Sulzer Mellapak brochure (liquid load 0.2 to over 200 m³/m²/h), vendor. Infors and Sartorius vessel data
    sheets (3–4 bar gauge), vendor. USGS Mineral Commodity Summaries 2025, lime ($240/t), snippet.
35. Gollub, Hirose, Everett 1967, Ann Thorac Surg 3:347 (disc vs bubble oxygenators), via a newsletter, snippet.
    CHO under small hydrostatic pressures, Sci Rep 2021, doi:10.1038/s41598-020-80576-8 , snippet. Brunner 2017
    (doi:10.1002/biot.201600633) and Paul 2020 (PMC7401239) on pH zones, snippets.

From memory, not looked up or not confirmed: PDMS permeabilities (search results give 3,190–3,970 Barrer
for CO₂; 600 for O₂ is from a vendor sheet); diffusivities and solubilities (textbook values scaled to
37 °C); that silicone tolerates repeated autoclaving.
The uncatalysed CO₂ hydration rate at 37 °C is 0.11–0.18 per second (SN), so in 6 seconds a liquid comes
about halfway to its new equilibrium without any enzyme. With no buffer this does not change the amount
per pass (only dissolved gas leaves); the buffer rows assume equilibrium is reached, so they are upper
bounds without an enzyme.
