## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FF_validation_suite_2.8). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FF_validation_suite_2.8)
Verdict: CONFIRMED MINOR. glow_tank_live.py:155-159 empty inspect() (refused or tank gone) makes has_line False -> PASS, no instrument check

### GPT finding (verbatim)
### FF_validation_suite_2.8 — Glow-tank setting check treats an unread inspect result as success
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/northstar/glow_tank_live.py:104-106,155-159` (`inspect`, setting-off row)
- evidence:
  ```python
  return [ln for t in (ins.get("things") or []) for ln in (t.get("inspect") or [])]
  has_line = any(("Ocean water" in ln) or ln.startswith("Dry") for ln in off)
  row("GLOWTANK_SETTING_OFF_NO_LINE", "PASS" if not has_line else "FAIL", "MOD", {"inspectOff": off, "restoredTo": w0})
  ```
- failure scenario: If the final inspect call refuses, returns no things, or loses the target tank, `inspect()` returns `[]`. The absence predicate then records PASS rather than UNMEASURED. Unlike the earlier positive water-line checks, this negative check has no assertion that its instrument actually read the glow tank.
- confidence: high
