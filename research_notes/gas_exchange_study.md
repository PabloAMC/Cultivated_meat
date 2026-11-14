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
  repository PDF). The affected point (section 2.3) rests on memory and is labelled so.
- Unit conversions: 1 mL of CO₂ per minute per m² (the medical unit, at standard conditions) = 2.68 mmol per
  m² per hour. 1 mmHg = 1.333 mbar.

---

## Answer in brief

1. **A membrane loop is limited by the liquid, not by the membrane.** A litre of culture at 100 mbar of CO₂
   holds 2.5 mmol of dissolved CO₂ and gives up about 1.1 mmol in a pass. Its 31 mmol/L of bicarbonate is
   not available, because turning bicarbonate into CO₂ needs an acid and culture medium has almost none to
   spare. So the tank must go round the loop many times an hour: about 11 to take out the CO₂ a sparger
   cannot at 190 g/L, and about 30–50 if nothing is sparged at all.
2. **The sensible design is a loop for CO₂ only, with the sparger kept.** For a 20 m³ tank at 190 g/L: about
   180 m³/h of culture through about 2,500 m² of fibre, 9 kPa of pressure drop, 45 W per m³. At an assumed
   $200 per m² it adds about $78k per m³ of tank and takes the floor from $11.5 to about **$9.2/kg**
   (range $8.6 to $13.8 across the membrane prices found). Removing CO₂ for free would give $8.5.
3. **A squat tank does about the same with no new equipment, on one condition.** Liquid 0.75–0.8 times as
   deep as the tank is wide gives **$8.7–8.8/kg** with the extra steel and floor counted. That holds only if
   what the cells tolerate is a gas velocity through the liquid surface. If it is gas flow per litre of
   culture, which is what bubble-damage models imply, shape gives nothing and the loop is the only one of
   the two that works.
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
- **Per-litre rule: shape does nothing for CO₂.** The gas a tank may pass falls with its depth exactly as
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

### 2.3 Which gas rule is right? [memory, unverified]

Humbird states the limit as a velocity "at the top of the vessel" and gives 0.1 vvm as its equivalent at
20 m³. The model reads it as a velocity. The classical account of bubble damage (Tramper's "killing
volume" model of the 1980s, as I recall it) has each bubble kill the cells in a fixed small volume when it
bursts, so the death rate is proportional to gas flow per litre of culture and falls with liquid height at
a given velocity. On that account the per-litre rule is the right one and a squat tank gains nothing.
Foaming and gas hold-up, by contrast, are velocity limits. I could not verify the formula or find the
origin of Humbird's figure: both lookups were stopped by the safeguard, and Ozturk 1996's abstract does
not mention a sparge limit (snippet).

My probability that the cells' limit behaves like a velocity (so that the squat tank's gain is real):
**40%** (range 25–55%). This is the single most useful thing to check before relying on tank shape, and
the model's tornado bar for shape ($9.3 to $25.2) is conditional on it.

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
  So it fails under the velocity rule and passes under the per-litre rule. The same open question as in
  section 2.3 decides it.
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
times that. A squat tank gets the same gain with no new equipment, if and only if the cells' gas limit is a
velocity and not a flow per litre.

**Probabilities.**
- A CO₂ loop beside a sparger can be made to work technically at 20 m³ for CHO-like single cells, given a
  development programme: **50%** (35–65%). For: shear, passes per day and pressure are inside what CHO
  tolerated for 48 days at 4 litres; the physics is simple. Against: no steam-proof module of this size
  exists; fouling of gas fibres by 18% cells over weeks is unmeasured; the pump at 180 m³/h is untested
  with cells; and the seconds-long pH swing is untested.
- It works and lowers the floor by $1/kg or more: **30%**. The extra condition is a module price under
  about $500 per m² with a life over a year.
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

A cheaper check comes before either: find out whether the gas limit is a velocity or a flow per litre
(section 2.3). If it is a velocity, build squat tanks and skip the loop.

**The model's floor with it.** $9.2/kg with a CO₂ loop at the assumed price (range $8.6–13.8 across
membrane prices; $6.1 in a yeast-style plant), against $11.5 today and $8.7 for a squat tank under the
velocity rule. Neither reaches the $7 that parity needs in the floor's plant.

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

From memory, not looked up or not confirmed: PDMS permeabilities (search results give 3,190–3,970 Barrer
for CO₂; 600 for O₂ is from a vendor sheet); diffusivities and solubilities (textbook values scaled to
37 °C); that silicone tolerates repeated autoclaving; the Tramper killing-volume scaling (section 2.3).
The uncatalysed CO₂ hydration rate at 37 °C is 0.11–0.18 per second (SN), so in 6 seconds a liquid comes
about halfway to its new equilibrium without any enzyme. With no buffer this does not change the amount
per pass (only dissolved gas leaves); the buffer rows assume equilibrium is reached, so they are upper
bounds without an enzyme.
