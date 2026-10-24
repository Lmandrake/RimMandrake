## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_3.6). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_3.6)
Verdict: CONFIRMED MINOR. ShotBlocked Bresenham walk from (sx,sz) is not symmetric (RM_RelativeRulesMath.cs:227-251); same pair can be blocked one way and open the other

### GPT finding (verbatim)
### FA_core_sim_3.6 — Cliff shooting restrictions depend on which endpoint is the shooter
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/RM_RelativeRulesMath.cs:227–250` (`ShotBlocked`)
- evidence:
  ```csharp
  if (e2 > -adz)
  ```
  ```csharp
  if (e2 < adx)
  ```
- failure scenario: Use endpoints `(10,10)` at depth 4 and `(12,11)` at depth 0, with intermediate depths `(11,10)=0` and `(11,11)=4`, and cliff threshold 4. Forward traversal examines `(11,10)` and blocks the shot; reverse traversal examines `(11,11)` and permits it. Both directions pass through the same legality helper, so otherwise unobstructed combat becomes one-way across this cliff geometry. I reproduced these exact arithmetic results.
- confidence: high
