# CFD plan: which tank questions simulation can answer, and how to set it up

> Names (2026-11-19): the low-lactate example was earlier called Central; the all-favourable example was earlier called the best case. Cells are described by their traits, never as a named kind of cell.

Compiled 2026-11-16. It turns the CFD track of `roadmap_2026-11-15.md` (targets A0–A5) and the design tricks in
`bioreactor_design_tricks.md` into a plan with steps, tools, grids and the model input each step would replace. Section 5 records the
first run of FluidX3D on this machine.

## 1. What CFD can and cannot settle here

| question | can CFD settle it? | why |
|---|---|---|
| Mixing time against tank shape and impeller | yes, single-phase | liquid flow and a passive tracer |
| How fast the column's alkaline return is diluted | yes, single-phase | tracer released at the return point |
| How much medium crosses a bubble cage's mesh | yes, single-phase | the mesh as a porous (drag) layer; tracer across it |
| Oxygen and CO₂ gradients at 120–258 g/L | yes, single-phase plus scalars with sinks | needs an edit to FluidX3D (section 3) |
| Peak shear and energy dissipation near impellers | partly | large-eddy simulation; the sub-grid model sets the peak, so validate against measured data |
| Oxygen transfer from bubbles (kLa), gas hold-up | only with two-phase CFD | bubbles; not in FluidX3D |
| Foam | no | depends on proteins and protectant; needs a bench test |
| Cells on a packed column's film, fouling of membranes or mesh | no | biology and chemistry; bench tests |

## 2. Tools

- **FluidX3D** (lattice Boltzmann on the GPU; free for non-commercial research, modified source must be published with results).
  Single phase, Smagorinsky large-eddy model, moving geometry from STL files (impellers), a temperature field usable as a tracer,
  buoyant point particles. No bubbles, no chemistry.
- **OpenFOAM** (finite volume; GPL). Two-phase Euler–Euler (`multiphaseEulerFoam`) for bubbles: gas hold-up, kLa with a transfer model.
  Runs on the CPU; slower, but the only free route to bubbles.
- **Correlations** (van't Riet-type kLa per impeller and gas rate; Grenville mixing times; power numbers). Cheap, and the yardstick
  every simulation is checked against.
- **1D models** for membranes and columns (flux, pressure drop, fouling), not CFD.

## 3. The steps

**Step 0. Install and validate (done in part; section 5).** FluidX3D builds and runs on the Apple M4. Next: a Rushton turbine in a
standard lab tank (T = H, D = T/3), checking the power number (about 5 in the turbulent range) from the torque on the impeller, and
the mixing time against the Grenville correlation. Then a pitched-blade impeller. If either is off by more than about 20%, stop and
find out why before going on.

**Step 1. Single-phase flow in each candidate geometry.** One geometry per design, at 1–2 m³ (fine grid, about 4 mm on this machine),
scaled to 20 m³ at constant power per volume, with one 20 m³ check on a rented GPU.
- Plain stirred tank at liquid depth / width 0.5, 0.75, 1.0 and 1.6, one and two impellers: mixing time, against the model's
  (H/T)^2.5 rule (`floor_physics.mixing_time_ratio`) and its mixing limit.
- Stirred tank with a bubble cage: the mesh as a thin layer with Darcy drag (an added force per cell, through FluidX3D's force field);
  the impeller turning around the cage. Output: the medium crossing the mesh per hour, which replaces the judgement
  `vm_cage_exchange` (0.8).
- Draft tube with impeller (stirred airlift): the riser's gas approximated as an upward body force set by an assumed gas hold-up.
  Output: circulation and mixing per watt.
- The column's return: a tracer released at candidate return points; output the alkaline exposure each cell sees (the integral of the
  pH excess over time), which replaces the "rise × share" inference in `gas_exchange_study.md` §8.1.

**Step 2. Dissolved oxygen and CO₂.** Edit FluidX3D's temperature field into two scalars with a uniform uptake (cells) and sources
(sparger zone, cage, column return). Output: the spread of dissolved oxygen and CO₂ at 120–258 g/L in 20 m³ and 200 m³. This says
whether a well-mixed tank, which the model assumes, is a fair description at these densities.

**Step 3. Bubbles, only where they decide the answer.** Oxygen transfer per watt for impellers and spargers (target A5), including
two spargers. First pass: bubbles as buoyant particles in FluidX3D, with transfer computed along their paths. Second pass, if the first
matters: OpenFOAM Euler–Euler at 1–2 m³. Check both against van't Riet-type correlations. Output: the vessel oxygen multiplier
(`otr_mult`) for each design.

**Step 4. Membranes and columns** as 1D models: area, pressure drop, flux against fouling, for the loop designs in
`bioreactor_design_tricks.md` §2B.

## 4. Each step's output and the number it replaces

| step | output | model input it replaces | worth, if it moves |
|---|---|---|---|
| 1 | mixing time vs shape | `mixing_time_ratio`, the mixing limit in squat tanks | the squat-tank designs of the low-lactate example and the all-favourable example |
| 1 | medium across the mesh | `vm_cage_exchange` | the bubble cage, $1–24/kg depending on the case |
| 1 | alkaline exposure at the return | the column's pH check | the column's pass-rate check: in the reference tank $10.4 if 22 passes an hour were safe, $10.7 within today's limits |
| 2 | oxygen and CO₂ spread | the well-mixed assumption | whether 200 m³ is ever worth it |
| 3 | oxygen multiplier per design | `otr_mult`, antifoam's effect | up to $1.7/kg in the low-lactate example (oxygen binds) |

## 5. First run on this machine (2026-11-16)

FluidX3D v3.9 (commit cc40a38, cloned into the session's scratch space, not into this repository). Apple M4, 8 GPU cores, OpenCL 1.2.

- **Build.** The makefile's macOS target links X11, which is not installed; the plain command in `make.sh` (no graphics) builds.
  Interactive graphics are not available on macOS in any case; frames can be written to disk.
- **Speed.** The built-in benchmark (256³ cells): 766 million lattice updates a second with 16-bit storage (FP16S), 505 with 32-bit.
- **Memory.** Apple's OpenCL allows at most 2.27 GB in one buffer (12.1 GB in all). That caps the grid at about 60 million cells with
  16-bit storage and about 30 million with 32-bit. A 1 m³ tank then resolves to about 3.6 mm (32-bit); a 20 m³ tank to about 9 mm.
  The Kolmogorov scale is about 70 µm, so every run is a large-eddy simulation.
- **Validation, laminar pipe flow (Poiseuille).** With 32-bit storage the error converges to **0.16%**. With 16-bit storage it stalls
  at 23% (FP16S) and 15% (FP16C), against the 2–5% the code's author expects. Whether that is Apple's OpenCL or this slow, low-velocity
  test was not settled. **Use 32-bit for validation, and check any 16-bit run against a 32-bit one before trusting it.**
- **Time.** A 1 m³ tank at 30 million cells and 505 million updates a second runs about 17 steps a second. With the impeller tip at
  1.5 m/s held at 0.1 in lattice units, a step is 0.24 ms at 3.6 mm, so one minute of tank time is about 250,000 steps, about 4 hours.
  A mixing-time run needs a few minutes of tank time: an overnight run. A rented A100 (about 10,000 million updates a second) is 20 times faster.

## 6. Order and effort

Step 0 (one to two days more), step 1 (two to three weeks), step 2 (one to two weeks), step 3 (two to four weeks), step 4 (one week).
Steps 0 and 1 are worth doing even if the bubble work stalls; they replace three judgements the scenarios rest on.
