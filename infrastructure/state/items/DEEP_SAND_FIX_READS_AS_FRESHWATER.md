## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FD_defs_xml_1.3). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FD_defs_xml_1.3)
Verdict: CONFIRMED MAJOR. RM_DeepSand.xml:128-141 Freshwater body + Water tag (for fishing); RM_ThirstUtility.cs:138 IsWater&&!IsOcean -> fresh water, so deep sand is drinkable and a pond source

### GPT finding (verbatim)
### FD_defs_xml_1.3 — Deep sand’s fishing tag also makes it a freshwater reservoir
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Defs/ManyWaters/TerrainDefs/RM_DeepSand.xml:134–158` (`RM_DeepSand`)
- evidence:
  ```xml
      <li>Water</li>
  ```
- failure scenario: Dig a canal beside deep sand or place a pump beside it. Sand is treated as natural liquid, supplies fresh water and participates in pond stock/recession logic. Pawns can also select it for freshwater drinking. The recreational-swimming exemption does not protect these systems. **Outside files opened:** `Source/RM_MapComponent_Excavation.cs:1224–1245` accepts every undug Water-tagged terrain as a source; `Source/RM_LiquidStock.cs:143,232` assigns unregistered terrain the water fluid; `Source/Thirst/RM_ThirstUtility.cs:133–140` assigns it freshwater drinking identity.
- confidence: high
