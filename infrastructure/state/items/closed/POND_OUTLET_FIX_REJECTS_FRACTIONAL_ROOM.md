## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_2.8). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_2.8)
Verdict: CONFIRMED MINOR. Outlet channel path is exact-aware (PourRoomDl, Spill.cs:54) but body-return path uses whole-level CanReturnLevels (Excavation.cs:2016)

### GPT finding (verbatim)
### FA_core_sim_2.8 — Pond outlets reject usable fractional room

- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidSpill.cs:68–74` (`Outlet`)
- evidence:
  ```csharp
  if (c.InBounds(map) && ex.CanReturnLevels(c, fluid, 1))
  ```
- failure scenario: A limited pond has 500 L of remaining capacity, and a hose outflow offers a smaller quantity of its own liquid. With no eligible channel nearby, the outlet rejects the pond because it cannot accept a whole 1,000 L level. Its wet end then becomes `Blocked`, although the exact-mode `BodyRoomDl`/`BodyTake` paths could accept the transfer. Outside this part, opened `RM_MapComponent_Excavation.cs:2005–2016,2566–2598` to confirm the difference between whole-level eligibility and decilitre room.
- confidence: high
