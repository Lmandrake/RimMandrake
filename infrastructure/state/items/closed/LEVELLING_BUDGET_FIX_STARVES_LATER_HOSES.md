## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_1.9). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_1.9)
Verdict: CONFIRMED MINOR. Resolve walks the whole run (walked += depths.Count, Levelling.cs:324) before the keyIndex cache check (326) and hoses are iterated in fixed order, so WalkBudget is spent re-walking known bodies and later components starve every cycle

### GPT finding (verbatim)
### FA_core_sim_1.9 — Levelling’s walk budget permanently starves later hose components
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Machinery/RM_Levelling.cs`:120–148, 286–324 (`Tick`, `DugBody`)
- evidence:
  ```csharp
  foreach (RM_NetLink h in hoses)
  ```
  ```csharp
  if (walked >= WalkBudget || RM_FlowDoorRules.SealsLiquid(start.GetEdifice(map)))
  ```
  ```csharp
  walked += depths.Count;
  ```
- failure scenario: Three early hose components each have two ends in the same 10,000-cell wet dug run. Resolving those ends consumes all 60,000 walk cells, including repeated walks of already identified bodies. A later component joining two small, unequal pools is never resolved. The next cycle starts from the same hose order and repeats the starvation indefinitely. The rotating cursor applies only after links have been constructed, so it cannot rescue these omitted links. Outside this part, I opened `Source/RM_LevellingMath.cs` to verify that distinction.
- confidence: high
