## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FD_defs_xml_2.1). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FD_defs_xml_2.1)
Verdict: CONFIRMED MINOR. RM_DBH_BottleWaterExt.xml:45-60 every bridged bottle gets water=1; RM_ThirstUtility.cs:196 skips our hydration when the def has WaterExt, so bottle volume and thirstQuality (toxic 0.5) are ignored under DBH

### GPT finding (verbatim)
### FD_defs_xml_2.1 — DBH bottle bridge bypasses volume and hydration-quality rules

- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Patches/LiquidTypes/RM_DBH_BottleWaterExt.xml:53–58` (`RM_Bottle_ToxicWater`; the same constant appears throughout the bridge)
- evidence:
  ```xml
              <li Class="DubsBadHygiene.WaterExt">
                <water>1</water>
                <UseForWashing>false</UseForWashing>
  ```
- failure scenario: With full DBH, thirst and the bottle bridge enabled, a desperate pawn drinks bottled toxic water. DBH adds `1` directly to its thirst need, filling the bar. FlowWorks deliberately skips its own hydration calculation whenever the bottle has `WaterExt`, so neither bottle volume nor toxic water’s `0.5` hydration factor affects the result. The same volume drawn from a tank receives the reduced hydration. Slime and fouled-water bottles have the same inconsistency; their health and mood effects still apply.

  Cross-file dependencies opened: `FlowWorks/Source/Thirst/RM_ThirstUtility.cs:189–203`, `RM_ThirstMath.cs:125–144`, and `RM_ThirstJobs.cs`. Also inspected the installed DBH **1.6** `BadHygiene.dll`: `HarmonyPatches_Thirst.IngestedPostfix` calls `Need_Thirst.Drink(modExtension.water)`, whose implementation adds that value directly to `CurLevel`. These files are outside this part.
- confidence: high
