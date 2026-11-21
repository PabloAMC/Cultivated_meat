# Is the gas cap in large animal-cell tanks set as a velocity or as vvm?

Research date: 2026-11-21. Evidence pass only; no input changed. Follow-up 4 of `gas_flow_cap.md`. The model caps sparging
at `pf_gas_velocity` 0.006 m/s (Humbird's recasting of "usually <0.1 vvm"; 0.1 vvm in his 20 m³ tank).

## Short answer

**In practice the cap is written in vvm; the physics that would make it scale-dependent is written in velocity.**
Vendors rate their spargers and tanks in vvm, and the published scale-up rule for CO₂ removal is a constant vvm. Mass-transfer
correlations, hold-up, flooding and foam are expressed in superficial velocity, and industrial-scale CO₂ studies report
velocity. No source states a measured cell-culture limit in m/s; the 6 mm/s is a conversion. Evidence is thin and mostly
vendor documents.

## What was found

| source | unit used | content | strength |
|---|---|---|---|
| Thermo Fisher, S.U.B. drilled-hole sparger datasheet | **vvm** | hole size, count and distribution set so bubble size is consistent "across all S.U.B. BPC system sizes at 0.1 vvm" (50–2,000 L) | vendor |
| Thermo Fisher, 5:1 S.U.B. application note | **vvm** | tested "up to the rated limit of 0.1 VVM" (250 L at 5:1 turndown, 40 W/m³) | vendor |
| Thermo Fisher, enhanced S.U.B. for high-density fed-batch app note | **vvm** (and gas entry velocity at the hole, m/s) | sparge area enlarged "to support up to 0.1–0.2 vvm"; hole exit velocity kept under 23 m/s against a literature 30 m/s | vendor |
| Xu et al. 2017, Biotechnol Prog, doi:10.1002/btpr.2489 (3–2,000 L) | **vvm** | CO₂ stripping "dominated by the gas throughput"; recommends "a minimum constant vvm air or N₂ flow with a similar specific power" as the scale-up criterion; O₂ kLa not limiting at equal vvm | peer-reviewed, abstract |
| Nickel et al. 2024, Front Chem Eng 6:1470991 (12.5–15 m³ industrial tank, saline) | **velocity** | reports sparging as superficial velocity (e.g. 0.64 mm/s); vvm does not appear; CO₂ removal at scale limited by CO₂ saturating the bubbles, "independent of the power input"; foam not discussed | peer-reviewed, read in part |
| Nienow 2006 (already in `gas_flow_cap.md`) | **velocity** | large tanks at 0.1–2 mm/s; upper limit with protectant "not established" | peer-reviewed review |
| Humbird 2021, Sect. 2.3 | velocity, derived from vvm | "Sparging is limited to a superficial velocity of 0.006 m/s at the top of the vessel" | TEA assumption |

## The arithmetic that makes the choice matter

For a liquid column of height H, superficial velocity u = vvm × H / 60. In the model's 20 m³ tank (H/T 1.6: T ≈ 2.5 m,
liquid H ≈ 4.0 m) 0.1 vvm is about 6.7 mm/s, close to Humbird's 6. If the cap is 0.1 vvm, a 100 m³ tank of the same shape
(H ≈ 6.9 m) could take 11.5 mm/s; if the cap is 6 mm/s, that tank is held to about 0.05 vvm. So:
- a **vvm cap** (what vendors and the CO₂ scale-up paper use) means gas per litre, CO₂ removal per litre and bubble-burst
  damage per litre do not worsen with tank size;
- a **velocity cap** (what foam and flooding depend on) means big tanks get less gas per litre and strip CO₂ worse.

The vendor ratings stop at 2 m³, where 0.1 vvm is only about 3 mm/s (2 m³ at H/T 1.6, liquid about 1.9 m deep), so they cannot show whether 0.1 vvm stays usable at
20 m³ (6–7 mm/s). That is the open question, and no source here answers it.

## Recommendation for the parent session (not applied)

- Keep `pf_gas_velocity` as a velocity (foam, the likeliest real cap per `gas_flow_cap.md`, scales with velocity), but add
  a sentence to its note: vendors and the published CO₂ scale-up rule state the limit in vvm (0.1, up to 0.2 vvm in enhanced
  single-use designs, to 2 m³); a vvm reading would let a taller tank take more gas.
- Optionally add a switch (cap as velocity vs as vvm) to the tornado for tank size, since that is where the two differ.
  Close follow-up 4 of `gas_flow_cap.md` with this note.

## Sources

- Thermo Fisher S.U.B. drilled-hole sparger datasheet, https://assets.thermofisher.com/TFS-Assets/LSG/brochures/PG1520-PJ8211-CO020203-SUB-BPC-wDrilled-Hole-Sparger-Datasheet-Americas-FLR.pdf ;
  5:1 app note, https://assets.thermofisher.com/TFS-Assets/BPD/Application-Notes/efficient-operation-evaluation-5-1-sub-working-volumes-app-note.pdf ;
  high-density fed-batch app note, https://assets.thermofisher.com/TFS-Assets/BPD/Application-Notes/sub-enhancements-high-density-fed-batch-cultures-app-note.pdf
  (all via search summaries).
- Xu S. et al. 2017, Biotechnol Prog, doi:10.1002/btpr.2489 (abstract via search summary).
- Nickel N. et al. 2024, "Novel sparging strategies to enhance dissolved carbon dioxide stripping in industrial scale stirred
  tank reactors", https://www.frontiersin.org/journals/chemical-engineering/articles/10.3389/fceng.2024.1470991/full (read in part).
- Humbird 2021 and Nienow 2006 as cited in `gas_flow_cap.md`.
