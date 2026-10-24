## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_1.11). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_1.11)
Verdict: CONFIRMED MINOR. RM_MapComponent_SuspensionBridges.cs:800+810 gate now%60 then now%2500: lcm 7500, flood every 3h (TicksPerHour=2500 RM_SuspensionMath.cs:403)

### GPT finding (verbatim)
### FC_pits_superdeep_1.11 — Hourly bridge flood damage actually runs every three hours
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_MapComponent_SuspensionBridges.cs:800-812` (`MapComponentTick`)
- evidence:
  ```csharp
  if (now % 60 != 0 || (bridges.Count == 0 && floorBand.Count == 0 && underThings.Count == 0))
  if (now % RM_SuspensionMath.TicksPerHour == 0)
  RM_SuspensionWaters.FloodHour(map, bridges);
  ```
- failure scenario: A rope or timber bridge remains awash through a flood. The hourly check is behind the 60-tick gate, so it runs only at multiples of `lcm(60,2500) = 7500` ticks. Damage is one-third of the advertised hourly rate; shorter floods can miss it altogether depending on their timing. Outside this part, opened `Source/RM_SuspensionMath.cs` and confirmed `TicksPerHour = 2500`.
- confidence: high
