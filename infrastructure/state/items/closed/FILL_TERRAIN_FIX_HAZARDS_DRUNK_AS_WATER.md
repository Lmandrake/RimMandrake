## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FD_defs_xml_1.1). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FD_defs_xml_1.1)
Verdict: CONFIRMED MAJOR. FlowWorks_PitFluidTerrain.xml:299-319 chemfuel fill terrain carries Water/WaterFreshShallow tags; no terrainSuite registers it (RM_LiquidBottleUtility.cs:43-62) so RM_ThirstUtility.cs:127-141 falls back to fresh water: chemfuel is drunk as water

### GPT finding (verbatim)
### FD_defs_xml_1.1 — Hazardous canal liquids become unlimited potable drinking sources
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Defs/Canals/TerrainDefs/FlowWorks_PitFluidTerrain.xml:300–319` (`RM_Fill_Chemfuel_Trace`; also other non-water fill ladders)
- evidence:
  ```xml
      <li>Water</li>
      <li>WaterFreshShallow</li>
      <li>WaterFreshShallowStill</li>
  ```
- failure scenario: Fill a reachable shallow canal with chemfuel, propane, poison or boiling water. A thirsty pawn can select its terrain as ordinary fresh water and hydrate without the liquid’s ingestion restrictions. Repeated drinking also leaves the canal’s quantity unchanged. **Outside files opened:** `Source/LiquidTypes/RM_LiquidBottleUtility.cs:42–64` indexes only `LiquidDef.terrainSuite`, excluding canal fill terrains; `Source/Thirst/RM_ThirstUtility.cs:127–140` consequently falls back to fresh water for these Water-tagged terrains. `Source/Thirst/RM_ThirstJobs.cs:223–228` debits through the natural-body stock API; `Source/RM_LiquidStock.cs` returns successful debit when no natural body exists, as on an ordinary dug cell.
- confidence: high
