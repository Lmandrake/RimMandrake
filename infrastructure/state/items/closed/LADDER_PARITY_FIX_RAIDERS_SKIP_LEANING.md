## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FC_pits_superdeep_2.4). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FC_pits_superdeep_2.4)
Verdict: CONFIRMED MINOR. RM_LadderParity.cs:267-278 MightClimb gate admits only player or ladder-carrier, so a hostile never reaches CanClimbAt for an already leaning ladder (callers RM_WallClimb.cs:172,335,367,401,477)

### GPT finding (verbatim)
### FC_pits_superdeep_2.4 — Ladderless raiders cannot use a ladder already leaning against a wall
- severity: MAJOR
- where: src/RimMandrake/FlowWorks/Source/Superdeep/RM_LadderParity.cs:277 (`MightClimb`)
- evidence:
  ```csharp
  return p.Faction == Faction.OfPlayer || CarriedLadder(p) != null;
  ```
- failure scenario: A portable ladder already leans against an unroofed colony wall. A raider without gear or an inventory ladder reaches it. Although `CanClimbAt` accepts the standing ladder, the blocker, breaching, and assault entry points in `RM_WallClimb.cs` first require `MightClimb`, which rejects this pawn. The raider bashes or remains outside instead of using either side’s standing ladder. This also prevents other raiders from reusing a ladder the first carrier has deployed.
- confidence: high
