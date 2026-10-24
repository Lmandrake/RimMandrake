## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_4.3). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_4.3)
Verdict: CONFIRMED MINOR. NoteNonWater snapshot taken before RM_SheetMath.Pulse (RM_MapComponent_Sheet.cs:555-557); squares a non-water fluid spreads to this pulse are not excluded from irrigation

### GPT finding (verbatim)
### FA_core_sim_4.3 — Newly spreading fuel or poison can irrigate crops
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/Source/Sheet/RM_MapComponent_Sheet.cs`:555–557, 644–649 (`EnginePulse`, `Effects`, `NoteNonWater`)
- evidence:
  ```csharp
  NoteNonWater();
  if (!nonWater.Contains(k))
  soakCells.Add(map.cellIndices.IndexToCell(k));
  ```
- failure scenario: Chemfuel spreads from an occupied spill square onto previously dry soil and soaks into that new square during the same pulse. `nonWater` records only the squares occupied **before** the kernel runs. The new chemfuel square is therefore absent from the exclusion set, and its soak is passed to Explosive Growth as irrigation. The player can receive crop watering from fuel or poison.
  
  Outside-part dependencies opened: `Source/RM_SheetMath.cs`:333–350, 502–515 confirms spreading precedes losses; `Defs/Canals/FluidDefs/FlowWorks_PitFluids.xml` confirms chemfuel has nonzero infiltration.
- confidence: high
