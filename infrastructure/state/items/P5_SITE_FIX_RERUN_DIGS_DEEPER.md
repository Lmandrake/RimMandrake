## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FF_validation_suite_1.7). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FF_validation_suite_1.7)
Verdict: CONFIRMED MINOR. depth_rebuild_proofs.py:426-434 prepare_site (validation_core) does not reset excavation; dig() adds deepenLevels to a rerun cut

### GPT finding (verbatim)
### FF_validation_suite_1.7 — Reusing a depth-proof map silently deepens the previous test geometry
- severity: MINOR
- where: `src/RimMandrake/FlowWorks/northstar/depth_rebuild_proofs.py:99–103,426–435` (`dig`, P5 setup)
- evidence:
  ```python
          r = B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=fill) or {}
                          n = 14 if core else 8
                          dig((sq[0] + i, sq[1] + j), n, n)
  ```
- failure scenario: Run `--only p5` twice on the same map, which the default CLI permits. `prepare_site` repaints terrain but does not reset excavation depth; `deepenLevels` adds to the existing cut. The second run measures deeper or capped geometry and can falsely fail the 152,000 L expectation. The in-part `climb_proof.py` documents this exact preparation trap and explicitly resets and checks its old digs; this suite does neither.
- confidence: high
