## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_2.9). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_2.9)
Verdict: CONFIRMED MINOR. TheftTick charges on any stock change of a foreign tank that PlayerReaches (adjacency/net presence), not on a player transfer; owner's own machine use can be billed

### GPT finding (verbatim)
### FA_core_sim_2.9 — Another faction’s own tank use can be charged as player theft

- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidTheft.cs:47–53,105–107` (`TheftTick`, `PlayerReaches`)
- evidence:
  ```csharp
  if (x != t && x.Faction == Faction.OfPlayer && RM_LiquidNet.RoleOfThing(x) == RM_NetRole.Machine)
  ```
- failure scenario: Leave a switched-off player pump beside a foreign tank while the owner’s machine changes that tank’s stock. The pump’s presence makes `PlayerReaches` true regardless of whether it moved anything. A nearby witness therefore catches the player, and continuing owner activity accrues theft time and goodwill penalties. Reachability establishes opportunity, but the code uses it as attribution. Outside this part, opened `RM_LiquidNet.cs:85–98` and `RM_LiquidNetKernel.cs:572`; machine role ignores operating state, and `Touched` tests only stock/identity changes.
- confidence: high
