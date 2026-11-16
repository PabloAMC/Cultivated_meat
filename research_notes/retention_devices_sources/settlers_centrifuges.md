# Non-membrane cell retention, and designs with no separate retention device

Scope: inclined settlers, acoustic settlers, continuous centrifuges (animal-cell and disc-stack), hydrocyclones, and the "centrifuge on the outflow" design. Duty is from the model (20 m3 tank, 16 m3 liquid, ~33-day runs). Repo material already in `research_notes/co2_sparging_settling.md` and `operating_modes.md` section 4 is not repeated except where it is needed for arithmetic (marked "repo").

Access levels: **full** = whole text read; **part** = part of the text read; **abstract**; **snippet** = search-engine excerpt only; **secondary** = reported by another source. Claim types: **measured**, **vendor claim**, **review claim**, **INF** (my inference).

About 37 tool calls. Search budget limited how far I chased paywalled primary texts (Pinto 2008, Johnson 1996, Bettinardi 2020, the NREL cost tables were reachable; the others were not).

---

## 0. Duty and output per tank-year (arithmetic)

| Case | x (g/L wet) | phi | Medium | Bleed | Permeate | Bleed rate D_b = bleed x 24 / 16 | Output kg/yr |
|---|---|---|---|---|---|---|---|
| Reference | 120 | 0.12 | 0.62 m3/h | 0.46 | 0.16 | 0.69 /day | 55.5 x 8760 x 0.91 = **442,400** |
| Central | 258 | 0.25 | 2.18 | 0.30 | 1.88 | 0.45 /day | 77.8 x 8760 x 0.82 = **558,900** |
| Best | 258 | 0.25 | 1.32 | 0.46 | 0.86 | 0.69 /day | 118 x 8760 x 0.85 = **878,600** |

Key point (INF): only the **permeate** has to be cell-free. In the reference case it is 0.16 m3/h, small; in the central case it is 1.88 m3/h at a culture of 25% cells by volume, which is the hard duty for every device below.

---

## 1. Inclined (lamella) settlers

### Evidence (beyond repo)
Repo already holds: Romann 2023 2,000 L bleed-recycling settler (1.78 m2 horizontal area, 30.4 L inner volume, 500 L/day, 1.46 h residence, efficiency fell to 94% above design); Coronel 2020 (50e6 cells/mL avian, retention 96-99%, doubling 26-32 h vs 25 h with ATF); Batt/Kompala compact settlers (vendor, snippet); 3,000 L N-1 at 15.8e6 cells/mL; design overflow velocity 0.7-1.0 cm/h. Searched for anything larger or denser: **not found**. No price found (searched vendor pages and TEAs).

### Stokes arithmetic (INF; my numbers, check against `settler_spec`)
v = g d^2 (rho_c - rho_m) / (18 mu). With d = 17 um, delta-rho = 0.053 g/mL (1.06 - 1.007), mu = 0.78 mPa s (medium at 37 C, assumed):
v = 9.81 x (17e-6)^2 x 53 / (18 x 0.78e-3) = 1.07e-5 m/s = **3.9 cm/h** single cell (range ~2.5-4.5 cm/h for d 15-17 um, delta-rho 0.043-0.063). Measured CHO single-cell value used in repo is 1.45 cm/h (smaller, lighter cells).
Hindered (Richardson-Zaki, n = 4.65): phi 0.12 -> (0.88)^4.65 = 0.55 -> **2.1 cm/h**; phi 0.25 -> (0.75)^4.65 = 0.26 -> **1.0 cm/h**.

Design overflow velocity: half the hindered velocity (practice runs at 50-70% of single-cell velocity, repo): 1.0 cm/h (reference), 0.5 cm/h (258 g/L).

| Case | Clarified flow | Projected plate area A = Q / v | Settler volume at 17 L/m2 (Romann ratio 30.4 L / 1.78 m2) | Fraction of 16 m3 culture outside the tank, anoxic |
|---|---|---|---|---|
| Reference | 0.16 m3/h | 0.16 / 0.010 = **16 m2** | 0.27 m3 | ~1.7% |
| Central | 1.88 | 1.88 / 0.005 = **376 m2** | 6.4 m3 | ~40% |
| Best | 0.86 | 0.86 / 0.005 = **172 m2** | 2.9 m3 | ~18% |

Romann's 2,000 L settler is 1.78 m2; the reference duty is ~9x that, the central ~210x. Oxygen in the settler runs out in seconds at these densities (repo: ~20 s at 1e8 cells/mL), so the anoxic hold-up is the binding constraint, not plate area cost. A settler at 258 g/L also has to move a concentrated sludge (phi > 0.4 on the plates) back down; flux limitation in that regime is not covered by the Romann/Coronel data (all at phi <~ 0.1, INF from 10-50e6 cells/mL x ~2-2.5 pL).

Capital (INF, nothing found): an SIP-rated stainless vessel with plates, guessed $2-5k per m2 of projected area installed -> reference $30-80k per tank ($1.5-4k per m3 of tank); central $0.75-1.9M ($38-94k/m3). Low confidence.
Running cost: pumps only, negligible (< $0.01/kg, INF).
Fouling: cell attachment on plates is the known long-run failure (Searles 1994 used vibration, repo). No month-long data at > 2,000 L found.

---

## 2. Acoustic settlers

| Item | Value | Source, access, type |
|---|---|---|
| BioSep sizes | 1, 10, 50, 200, 1,000 L/day | Getinge product page, https://www.getinge.com/se/products/applikon-biosep/ , snippet, vendor claim |
| Largest independent test | 200-400 L/day, 96% at 200 L/day, 90 W | Gorenflo 2002 (repo, snippet of abstract), measured |
| Scale limit | larger units "very difficult" because of heat | Romann 2023 (repo, full), review claim |
| FloDesign Sonics ekko | ~3 L/h per unit, pump-limited; earlier 4, 10 and 50 L/h units with ~90% clarification | BPI 2019 Q&A, https://www.bioprocessintl.com/sponsored-content/ask-the-expert-acoustic-cell-processing , snippet, vendor; https://dc.engconfintl.org/cellbasedtherapies_v/66 , snippet, vendor |
| Cadence acoustic separator (Pall) | "bioreactors up to 2,000 L", single-pass feed listed as 3.6 L/h (as returned by search; may be per chamber) | https://biopharma-asia.com/magazine-articles/integrated-disposable-clarification-solution-for-continuous-bioprocessing , snippet, sponsored/vendor |
| Price | not found (Getinge asks for quote) | searched Getinge, resellers |

Unit count (INF): reference 0.16 m3/h = 3,840 L/day -> 19 units at the largest tested 200 L/day, 4 at vendor 1,000 L/day. Central 1.88 m3/h = 45,100 L/day -> 226 units at 200 L/day (heat 226 x 90 W = 20 kW into the recirculating culture), 45 at 1,000 L/day. No acoustic data above ~1e7-5e7 cells/mL (phi <~ 0.1); at phi 0.25 the standing-wave trapping zone saturates with cells (INF). Ekko/Cadence class (3-50 L/h, ~90%) is a harvest clarifier, not a perfusion retention device for this duty.

---

## 3. Continuous centrifuges built for animal cells

| Device | Capacity per unit | g, shear, viability | Largest shown | Source, access, type |
|---|---|---|---|---|
| Sartorius kSep 6000S (fluidized bed, single-use) | max 720 L/h; up to 1.2e12 CHO cells per cycle; 2,000 g; listed **discontinued** | "low shear"; no viability number | harvest / cell therapy | https://shop.sartorius.com.cn/us/p/KSEP6000S and Sartorius kSep pages, snippet, vendor |
| kSep 400 | 114 L/h, 1,000 g | | | same, snippet, vendor |
| Centritech Lab / CELL (Pneumatic Scale Angelus) | flow not found | viable-cell recovery >= 98%, dead-cell recovery ~80%; growth equal to filter perfusion; IgM 35% lower unless run intermittently | lab hybridoma perfusion | Johnson et al. 1996 Biotechnol Prog 12:855, https://zendy.io/title/10.1021/bp960072n , abstract via snippet, measured |
| Alfa Laval Culturefuge 100 (hermetic disc stack, SIP) | 200-2,000 L/h | "fully hermetic", no air-liquid interface; **additional lysis 12.5%** per pass on CHO harvest (as the reference machine) | biopharma harvest (2,000 L+ class) | Capacity: https://www.alfalaval.ca/fr-be/produits-et-solutions/separation/separation-centrifuge/separateurs/culturefuge , snippet, vendor; 2003 launch "2000 litre/hr" https://manufacturingchemist.com/first-hermetic-cell-culture-centrifuge--33731 , snippet; lysis: Hundley & Konigsson 2020 BPI, https://bioprocessintl.com/filtration/development-of-a-single-use-hermetic-centrifuge-system-for-mammalian-harvest-with-moderate-to-high-cell-content , part, measured by vendor staff |
| Alfa Laval CultureOne prototype (single-use hermetic) | 1-3 L/min feed (60-180 L/h) tested | additional lysis **2-6%** at low load, 4-11% at moderate load, **~25%** at 3x load; handled a **28% PCV** feed (synthetic analog); concentrate 70% PCV (up to 77-97%); yield > 90% | harvest | same BPI 2020, part, measured (vendor authors) |
| Continuous centrifugal bioreactor (cells live in the rotor) | lab | viable culture > 1e8 cells/mL hybridoma | lab | Detzel 2009, https://pmc.ncbi.nlm.nih.gov/articles/PMC2796705 , snippet, measured |

INF on kSep-type (fluidized-bed) devices: they hold a fixed number of cells per chamber, then discharge. Cells carried in the permeate stream: reference 0.16 m3/h x 120 g/L = 19 kg/h; central 1.88 x 258 = 485 kg/h. One 6000S cycle holds ~1.2e12 x 2.4 ng = 2.9 kg wet. Central duty would need ~170 cycles per hour. **Fluidized-bed centrifuges are out at these densities** (they suit low-density harvest or dead-cell removal). The same arithmetic shows why a disc stack (continuous solids discharge) is the only centrifuge class that fits.

Shear mechanism (review claim): disc stacks damage cells mainly in the feed (acceleration) zone; hermetic feeds reduce it (UCL thesis 1998, https://discovery.ucl.ac.uk/id/eprint/10099092/1/An_engineering_study_of_the_re.pdf , snippet; Joseph et al. 2017 Biotechnol J, https://discovery.ucl.ac.uk/1557210/1/Farid_Joseph_et_al-2017-Biotechnology_Journal.pdf , snippet). Residence in a 2 m3/h bowl is seconds to a few minutes (INF), so oxygen deprivation is short; lysis per pass is the issue.

---

## 4. Disc-stack separators from yeast, beer and fermentation

| Item | Value | Source, access, type |
|---|---|---|
| Alfa Laval MBUX 420 nozzle separator (microorganism recovery, hygienic, pressurised) | max 100 m3/h throughput, 45 m3/h solids, 100 kW | https://pdf.directindustry.com/pdf/alfa-laval/mbux-420-nozzle-separator-hygienic-pressurised-recovery-microorganisms/16602-133207.html , snippet, vendor |
| Alfa Laval Brew 601H / 250 Plus / 20 | 55-85 m3/h, 55 kW / 18 m3/h, 18.5 kW / 0.4-1.5 m3/h | Brew leaflets, https://alfalaval.com/globalassets/documents/products/separation/centrifugal-separators/separators/brew-series/brew-601h-product-leaflet.pdf , snippet, vendor |
| Westfalia SC 35 | ~11 m3/h, 1,650 kg | used listing https://www.machineseeker.ie/westfalia-sc+35-36-177/i-21152717 , snippet |
| Beer clarifier g-force | 6,500-6,700 g | third-party page https://dolphin-centrifuge-website.pages.dev/beer-wine-centrifuge , snippet, vendor (indicative) |
| Prices, used | GEA GSC40 (2015) $24,990; Westfalia SA1 $7-30k; Westfalia OSB35 $42,900 | https://www.equipt.com/listings/1142940-gea-gsc40-06-077-disc-stack-centrifuge-disc-stack-centrifuges-in-indiana etc., snippet (non-sterile, used) |
| Price, new, industrial | bowl centrifuge 154 m3/h = **$747,500 (2013$)** purchased, installed factor 1.8, scaling exponent 0.6; power **1.35 kWh/m3** of feed (range 0.7-2.0) | Davis et al. 2016 NREL/TP-5100-64772, https://docs.nlr.gov/docs/fy16osti/64772.pdf , part (text extracted, cost table and centrifuge section read), vendor quote via Harris Group |
| Price, new, sterile biopharma disc stack | **not found** (vendors quote on request; searched Alfa Laval, GEA, Thermo, TEAs) | |
| Yeast cream 15-20% dry solids | **not found** in this pass (searched Alfa Laval/GEA yeast pages). CHO concentrate 70% PCV measured (BPI 2020 above) is the relevant analog | |

Power (INF): MBUX 420 implies ~1 kWh/m3 at full load; NREL 1.35 kWh/m3. Small hygienic units are less efficient; I assume 5-15 kW continuous per 2 m3/h unit.

---

## 5. Hydrocyclones

| Item | Value | Source, access, type |
|---|---|---|
| Pinto, Medronho, Castilho 2008 (Cytotechnology 56:57) | six geometries; CHO.K1 and recombinant CHO; separation efficiency **> 97%**; low viability loss (trypan blue, LDH); no apoptosis within 48 h of passage | https://pmc.ncbi.nlm.nih.gov/articles/pmid/19002842 (blocked), abstract via snippet, measured |
| Lubberstedt (HeLa), cited by Pinto | best 10 mm Dorr-Oliver: 81%; underflow viability constant at 1-4 bar, overflow loses viability > 3 bar | secondary via snippet |
| Elsayed & Wagner 2011 (SP2/0) | 0.85 -> 1.30 bar raised efficiency ~89% -> 95%; viable cells preferentially returned | BMC Proc 5(S8):P65, https://bmcproc.biomedcentral.com/articles/10.1186/1753-6561-5-S8-P65 (redirect to login), snippet, measured |
| Bettinardi et al. 2020 Biotechnol Bioeng (HC2015, stainless, 2.3 bar) | total efficiency up to **96%** (centrifugal 82%) at 24e6 cells/mL; ran a 50 L single-use bag (40 L working) to **50e6 cells/mL** at 1-2 RV/day, CSPR 20 pL/cell/day; overflow cells less viable | https://dc.engconfintl.org/biomanufact_iv/47 , abstract read, measured; https://pubmed.ncbi.nlm.nih.gov/32181883/ , snippet |
| Feed flow per unit, run length, price | **not found** (full texts blocked) | |

INF on cell loss: a single hydrocyclone at 96-97% total efficiency passes 3-4% of feed cells to the overflow (the permeate). Central case, feed ~2.5 m3/h at 258 g/L: overflow cells ~0.035 x 258 x 2.5 = ~23 kg/h, against 77.8 kg/h output, i.e. **~30% product loss** unless the overflow is re-treated (second stage) or harvested. Reference: 0.035 x 120 x 0.2 = 0.8 kg/h vs 55.5, ~1.5%, acceptable. Cheap, no moving parts, steamable (INF); ms-scale residence, so no anoxia.

---

## 6. "No separate device": separator on the whole outflow

### Industrial precedent
- **Melle-Boinot (Brazil, ~all sugarcane ethanol)**: after each fed-batch fermentation the wine is centrifuged; the yeast cream is acid-washed and returned. Yeast recycled **2-3 times per day for 250-280 days**, at 10-15% w/v in fermentation (Lopes presentation, https://wfcc.info/static/iccc12/presentations/mlopes.pdf , snippet; review gives 8-12%, https://pmc.ncbi.nlm.nih.gov/articles/PMC5156502 , snippet, review claim). Viability 94-97% for good strains averaged over six cycles; recycling continues while viability > 50% (snippets). Disc-stack nozzle separators are the standard machine there (vendor material, MBUX class).
- So the architecture is proven for ~500+ passes per cell lineage, but in **yeast, which has a cell wall**; animal cells are far more shear-sensitive. Shear transfer: **not established** (INF).
- Animal cells: the Centritech 1996 lab perfusion is the nearest; no month-long disc-stack recycle of animal cells found (searched Westfalia, Contifuge, Voisard 2003 table: not obtained).

### Flow balance (INF)
Concentrate at 70% PCV (BPI 2020). Centrifuge feed Q_f must carry the permeate plus enough concentrate to return the cells: Q_conc = Q_perm x phi / (0.70 - phi).
- Reference: 0.16 x 0.12 / 0.58 = 0.033 -> Q_f = **0.19 m3/h**
- Central: 1.88 x 0.25 / 0.45 = 1.04 -> Q_f = **2.92 m3/h**
- Best: 0.86 x 0.25 / 0.45 = 0.48 -> Q_f = **1.34 m3/h**
If the bleed also goes through the machine (the "whole outflow" option, harvest taken from the concentrate), add 0.30-0.46 m3/h; that adds harvest dewatering (120-258 g/L -> ~700 g/L), which a plant needs downstream anyway, so the incremental cost of retention is then only the extra capacity (INF).

### Damage per pass -> product loss (INF)
Passes per day p = Q_f x 24 / 16 (fraction of inventory through the bowl per day): reference 0.29, central **4.4**, best 2.0. Loss rate = f x p, where f = additional lysis per pass. Fraction of growth lost = f p / (D_b + f p).

| f per pass | Reference | Central | Best |
|---|---|---|---|
| 12.5% (Culturefuge 100, measured on CHO harvest) | 5% | **55%** | 27% |
| 4% (CultureOne prototype, low load) | 1.7% | 28% | 10% |
| 1% (hoped-for) | 0.4% | 9% | 3% |

Lysed cells also leave DNA and debris in the culture, which raises viscosity and foaming (INF). Measured lysis is on CHO at 7-28% PCV; cultivated-meat cells (17 um, larger) are probably more fragile per pass (INF).

### Sizing and cost
Units: Culturefuge-class 2 m3/h -> reference 1, central **2** (2.92 m3/h), best 1; plus 1 spare for a 33-day closed run (INF: a single mechanical seal failure would otherwise end the run).
Capital: sterile hermetic price **not found**. NREL scaling of the non-sterile 154 m3/h quote to 3 m3/h: 747,500 x (3/154)^0.6 = 747,500 x 0.094 = $70k purchased, $127k installed — a 50-fold extrapolation, below the floor for a hygienic SIP machine. My judgement for a CSA/Culturefuge-class unit: **$0.4-1.5M installed** (INF, low confidence).
- Reference: 2 units (1 + spare) $0.8-3.0M -> **$40-150k per m3 of tank**
- Central: 3 units $1.2-4.5M -> **$60-225k/m3**
- Best: 2 units -> **$40-150k/m3**
Model's current charge: $89k/m3 = $1.78M per tank; it sits inside all three ranges.

Running cost per kg wet cells (INF): power 10 kW per running unit x hours x $0.10/kWh:
- Reference: 10 x 8760 x 0.91 = 79,700 kWh = $8.0k / 442,400 kg = **$0.018/kg**
- Central: 20 kW x 8760 x 0.82 = 143,700 kWh = $14.4k / 558,900 = **$0.026/kg**
- Best: 10 x 8760 x 0.85 = 74,500 kWh = $7.4k / 878,600 = **$0.008/kg**
Maintenance at 4% of capex/yr (INF): central $1.2-4.5M x 0.04 = $48-180k -> $0.09-0.32/kg; reference $0.07-0.27/kg; best $0.04-0.14/kg. Power is negligible; capital and maintenance dominate; **product loss from lysis dominates everything in the central case** (28-55% of output at measured lysis).

Gravity settler and hydrocyclone running costs are pumps only (<$0.01/kg, INF).

---

## 7. Comparison for the three duties (INF)

| Device | Reference (0.16 m3/h, phi 0.12) | Central (1.88 m3/h, phi 0.25) | Best (0.86 m3/h, phi 0.25) |
|---|---|---|---|
| Inclined settler | 16 m2, 0.27 m3, plausible (9x Romann) | 376 m2, 6.4 m3 anoxic: not viable | 172 m2, 2.9 m3: very doubtful |
| Acoustic | 4-19 units, untested density | 45-226 units, 20 kW heat: no | ~100 units: no |
| Fluidized-bed centrifuge (kSep) | ~7 cycles/h: no | ~170 cycles/h: no | no |
| Hydrocyclone | ~1.5% loss, cheap: plausible | ~30% loss single-stage | ~15% loss |
| Disc stack on outflow | 1+1 units, 2-5% loss: plausible | 2+1 units, 28-55% loss at measured lysis | 1+1, 10-27% loss |

---

## 8. Probabilities (my judgement)

- Gravity (lamella) settler holds **120 g/L at 20 m3 for a month** at the reference duty with < 5% cell loss: **35%** (no data above 2,000 L or phi ~0.1; plate fouling over 33 days unknown).
- Gravity settler at **258 g/L**, central duty: **5%**; best duty: **10%**.
- Any acoustic device meets the central duty at 20 m3: **3%**; reference duty: **10%**.
- Hydrocyclone (single stage) holds the central duty with < 5% product loss: **10%**; two-stage cascade: **30%**; reference duty: **50%**.
- Disc-stack centrifuge on the whole outflow keeps **viability > 90% over a month**: reference **60%**, central **25%**, best **40%**.
- Additional lysis per pass for these cells in a hermetic disc stack is **≤ 2%**: **30%** (measured 2-12.5% on CHO).
- A sterile hermetic disc stack runs closed (SIP, no contamination, no seal failure) for **33 days**: **55%** per run (INF from long continuous Melle-Boinot service, but those plants are not aseptic).
- Retention hardware (any non-membrane design that works) installed at **≤ $89k per m3 of tank**: reference **65%**, central **35%**.
- The model's assumption of a hoped-for device at $89k/m3 with negligible cell loss is right for the central case: **20%**.

---

## 9. Not found (searched)
Sterile disc-stack prices; yeast cream % dry solids; Pinto 2008 and Bettinardi 2020 flow rates and run lengths (full text blocked); Centritech feed rate; Kendro Contifuge data; Voisard 2003 capacity table; any non-membrane animal-cell perfusion above 3,000 L or above ~5e7 cells/mL for a month; settler prices; BioSep prices.
