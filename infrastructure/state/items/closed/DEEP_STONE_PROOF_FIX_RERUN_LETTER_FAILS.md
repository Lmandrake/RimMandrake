## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FF_validation_suite_1.9). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FF_validation_suite_1.9)
Verdict: CONFIRMED MINOR. deep_stone_live.py:176-177 requires a new first-find letter; RM_DigDiscovery.cs:161 found.Add fires once per def per map, rerun without --fresh-map fails

### GPT finding (verbatim)
### FF_validation_suite_1.9 — A correct second deep-stone run fails because it demands another first-find letter
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/northstar/deep_stone_live.py:168–177` (`main`, final verdict)
- evidence:
  ```python
          new_letters = [x for x in l1 if x not in l0]
          deep_letter = [x for x in new_letters if x.startswith("Deep stone")]
          good = (d0, d1) == (3, 4) and last.startswith(chunk + " x1") and "D=4 (deep stone)" in last and bool(got_chunk) and bool(deep_letter)
  ```
- failure scenario: Run this proof successfully, then rerun without `--fresh-map`. The map correctly remembers that this chunk was already discovered and produces no second first-find letter. The cut and chunk succeed, but the proof reports MOD FAIL. Dependencies opened: `Source/RM_DigDiscovery.cs`, where the letter requires `found.Add(chunk)`, and `Source/RM_NorthstarProofs.cs`, whose rectangle reset clears rolled depths rather than that discovery set.
- confidence: high
